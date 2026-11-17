"""Mission contract and loader — P01.W1 / P02.W3.

Curriculum criteria under test:
- P01.W1: "A test cannot begin without a valid scope record." (mission↔scope link)
- P02.W3: "The CLI validates mission input ... and fails safely on malformed or
  incomplete input."
- canonical_record_contracts.Mission required fields (source: curriculum.json).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

CURRICULUM = json.loads(
    (Path(__file__).resolve().parents[2] / ".agents" / "curriculum.json").read_text()
)
MISSION_REQUIRED = CURRICULUM["canonical_record_contracts"]["Mission"]["required"]


# ---------------------------------------------------------------------------
# Model validation
# ---------------------------------------------------------------------------


def test_valid_mission_payload_loads(make_mission) -> None:
    from core.mission import ApprovalState, Mission

    mission = Mission.model_validate(make_mission())
    assert mission.mission_id == make_mission()["mission_id"]
    assert mission.approval_state is ApprovalState.APPROVED
    assert mission.target_asset_ids == ["asset-vm-lab-0001"]
    assert mission.scope_id == make_mission()["scope_id"]


@pytest.mark.parametrize("field", MISSION_REQUIRED)
def test_missing_required_field_is_rejected(make_mission, field: str) -> None:
    from core.mission import Mission

    broken = {key: value for key, value in make_mission().items() if key != field}
    with pytest.raises(ValidationError, match=field):
        Mission.model_validate(broken)


def test_expiry_time_must_be_after_start_time(make_mission) -> None:
    from core.mission import Mission

    payload = make_mission(expiry_time=make_mission()["start_time"])
    with pytest.raises(ValidationError, match="[Ee]xpir"):
        Mission.model_validate(payload)


@pytest.mark.parametrize(
    "field", ["start_time", "expiry_time"]
)
def test_naive_datetimes_are_rejected(make_mission, field: str) -> None:
    """Authorization windows are meaningless without an explicit timezone."""
    from core.mission import Mission

    payload = make_mission(**{field: "2026-11-17T00:00:00"})
    with pytest.raises(ValidationError):
        Mission.model_validate(payload)


def test_allowed_and_excluded_actions_must_be_disjoint(make_mission) -> None:
    """A mission that both allows and excludes an action is contradictory."""
    from core.mission import Mission

    payload = make_mission(allowed_actions=["inventory.read", "network.connect"])
    with pytest.raises(ValidationError, match="[Ee]xcluded"):
        Mission.model_validate(payload)


@pytest.mark.parametrize("state", ["draft", "approved", "revoked"])
def test_known_approval_states_are_accepted(make_mission, state: str) -> None:
    from core.mission import ApprovalState, Mission

    mission = Mission.model_validate(make_mission(approval_state=state))
    assert mission.approval_state is ApprovalState(state)


def test_unknown_approval_state_is_rejected(make_mission) -> None:
    """Only recorded states are valid — an agent cannot invent an approval."""
    from core.mission import Mission

    with pytest.raises(ValidationError):
        Mission.model_validate(make_mission(approval_state="self_approved"))


@pytest.mark.parametrize(
    "mission_id", ["", "has spaces", "-leading-dash", "m" * 200]
)
def test_mission_id_format_is_constrained(make_mission, mission_id: str) -> None:
    from core.mission import Mission

    with pytest.raises(ValidationError):
        Mission.model_validate(make_mission(mission_id=mission_id))


def test_schema_version_is_pinned(make_mission) -> None:
    from core.mission import Mission

    with pytest.raises(ValidationError):
        Mission.model_validate(make_mission(schema_version="0.9.0"))
    Mission.model_validate(make_mission(schema_version="1.0.0"))


# ---------------------------------------------------------------------------
# File loading (drives the CLI's mission-validation path)
# ---------------------------------------------------------------------------


def test_load_mission_reads_a_valid_file(tmp_path: Path, make_mission) -> None:
    from core.mission import Mission, load_mission

    path = tmp_path / "mission.json"
    path.write_text(json.dumps(make_mission()))
    mission = load_mission(path)
    assert isinstance(mission, Mission)
    assert mission.mission_id == make_mission()["mission_id"]


def test_load_mission_fails_safely_on_malformed_json(tmp_path: Path) -> None:
    """A truncated file must raise the domain error, not leak JSONDecodeError."""
    from core.mission import MissionValidationError, load_mission

    path = tmp_path / "mission.json"
    path.write_text('{"mission_id": "mission-x",')  # truncated
    with pytest.raises(MissionValidationError):
        load_mission(path)


def test_load_mission_reports_missing_fields(tmp_path: Path, make_mission) -> None:
    from core.mission import MissionValidationError, load_mission

    payload: dict[str, Any] = {
        key: value
        for key, value in make_mission().items()
        if key not in {"target_asset_ids", "approval_state"}
    }
    path = tmp_path / "mission.json"
    path.write_text(json.dumps(payload))
    with pytest.raises(MissionValidationError) as excinfo:
        load_mission(path)
    message = str(excinfo.value)
    assert "target_asset_ids" in message and "approval_state" in message


def test_load_mission_fails_safely_on_missing_file(tmp_path: Path) -> None:
    from core.mission import MissionValidationError, load_mission

    with pytest.raises(MissionValidationError):
        load_mission(tmp_path / "does-not-exist.json")
