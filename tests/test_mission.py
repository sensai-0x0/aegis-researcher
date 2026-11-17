"""TDD spec for ``core/mission.py`` — the Mission model (red).

``tests/unit/test_contract_roundtrip.py`` already proves the model mirrors
``contracts/mission.schema.json`` (canonical payload accepted, missing
required fields rejected). This module pins the Mission-specific semantics:

- the model is closed (undeclared fields rejected) — a mission cannot carry
  smuggled authority,
- the construction shape matches the conftest bundle: a pydantic model the
  ``PolicyEngine``/``Orchestrator`` can consume,
- expiry *enforcement* belongs to the policy engine (see test_policy.py);
  the model only carries the timestamps.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

pytestmark = pytest.mark.unit


def test_valid_mission_validates(make_mission) -> None:
    from core.mission import Mission

    mission = Mission.model_validate(make_mission())
    assert mission.mission_id == "mission-local-lab-0001"
    assert mission.scope_id == "scope-local-lab-0001"
    assert mission.approval_state == "approved"


@pytest.mark.parametrize("drop", ["mission_id", "scope_id", "approval_state", "expiry_time"])
def test_missing_required_field_is_rejected(make_mission, drop) -> None:
    from core.mission import Mission

    payload = make_mission()
    payload.pop(drop)
    with pytest.raises(ValidationError):
        Mission.model_validate(payload)


def test_unknown_field_is_rejected(make_mission) -> None:
    """The contract is closed: no undeclared properties on a mission."""
    from core.mission import Mission

    with pytest.raises(ValidationError):
        Mission.model_validate(make_mission(operator_feeling="lucky"))


def test_mission_records_boundaries_not_authority(make_mission) -> None:
    """A mission defines authorized task + boundaries; it is not a policy decision."""
    from core.mission import Mission

    mission = Mission.model_validate(make_mission())
    assert mission.allowed_actions, "mission must record allowed actions"
    assert mission.excluded_actions, "mission must record excluded actions"
    assert mission.stop_conditions, "mission must record stop conditions"
