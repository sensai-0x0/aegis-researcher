"""TDD spec for ``core/mission.py`` — mission model + schema-validated load (currently red).

The curriculum's ``Mission`` canonical record defines the authorization
boundary of every experiment. ``goal.md`` §Understand names
``core/mission.py`` as the entry point. These tests define the contract:

- ``Mission.load(path)`` validates the file against
  ``contracts/mission.schema.json`` and rejects malformed input *safely*
  (no partially-constructed mission escapes).
- Required fields come from the curriculum; unknown fields are rejected
  (the contract is closed).
- An expired mission (``expiry_time`` in the past) must not load as active.

The public API specified here (Phase 3 acceptance target)::

    from core.mission import Mission, MissionError

    mission = Mission.load(path)   # validates against contracts/mission.schema.json
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from jsonschema import ValidationError

pytestmark = pytest.mark.unit

TEST_TIME = "2026-11-17T00:00:00Z"


def _mission_dict(curriculum: dict[str, Any]) -> dict[str, Any]:
    """Build a schema-minimal synthetic mission from the curriculum's required list."""
    required = curriculum["canonical_record_contracts"]["Mission"]["required"]
    values: dict[str, Any] = {
        "mission_id": "m-test-001",
        "title": "synthetic inventory mission",
        "target_asset_ids": ["asset-lab-host-a"],
        "scope_id": "s-test-001",
        "objectives": ["inventory approved lab host"],
        "allowed_actions": ["read"],
        "excluded_actions": ["execute", "write"],
        "start_time": TEST_TIME,
        "expiry_time": "2030-01-01T00:00:00Z",
        "stop_conditions": ["any out-of-scope contact"],
        "approval_state": "approved",
        "created_by": "test-fixture",
        "schema_version": "1.0.0",
    }
    missing = set(required) - set(values)
    assert not missing, f"fixture does not cover required fields: {sorted(missing)}"
    return {key: values[key] for key in required}


@pytest.fixture()
def mission_file(tmp_path, curriculum):
    def _write(payload: Any) -> object:
        path = tmp_path / "mission.json"
        if isinstance(payload, (str, bytes)):
            path.write_bytes(payload)
        else:
            path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    return _write


def test_mission_module_exists() -> None:
    import core.mission  # noqa: F401


def test_valid_mission_loads(mission_file, curriculum) -> None:
    from core.mission import Mission

    mission = Mission.load(mission_file(_mission_dict(curriculum)))
    assert mission.mission_id == "m-test-001"
    assert mission.scope_id == "s-test-001"


def test_mission_validates_against_contract(mission_file, curriculum) -> None:
    """A loaded mission must satisfy contracts/mission.schema.json."""
    from core.mission import Mission

    Mission.load(mission_file(_mission_dict(curriculum)))  # must not raise


@pytest.mark.parametrize("drop", ["mission_id", "scope_id", "approval_state", "expiry_time"])
def test_missing_required_field_is_rejected(mission_file, curriculum, drop) -> None:
    from core.mission import Mission, MissionError

    payload = _mission_dict(curriculum)
    payload.pop(drop)
    with pytest.raises((MissionError, ValidationError)):
        Mission.load(mission_file(payload))


def test_unknown_field_is_rejected(mission_file, curriculum) -> None:
    """The contract is closed: no undeclared properties."""
    from core.mission import Mission, MissionError

    payload = {**_mission_dict(curriculum), "operator_feeling": "lucky"}
    with pytest.raises((MissionError, ValidationError)):
        Mission.load(mission_file(payload))


def test_malformed_json_is_rejected_safely(mission_file) -> None:
    from core.mission import Mission, MissionError

    with pytest.raises(MissionError):
        Mission.load(mission_file("{not json"))


def test_missing_file_raises_filenotfound(tmp_path) -> None:
    from core.mission import Mission

    with pytest.raises(FileNotFoundError):
        Mission.load(tmp_path / "does-not-exist.json")


def test_expired_mission_is_rejected(mission_file, curriculum) -> None:
    """An expired authorization is not an authorization."""
    from core.mission import Mission, MissionError

    payload = {**_mission_dict(curriculum), "expiry_time": "2020-01-01T00:00:00Z"}
    with pytest.raises((MissionError, ValidationError)):
        Mission.load(mission_file(payload))
