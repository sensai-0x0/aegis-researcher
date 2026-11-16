"""TDD spec for ``core/scope.py`` — authorization boundary (currently red).

Behavioral mirror of ``.claude/rules/scope.md`` and the agent operating
contract in the curriculum:

- **Deny by default.** Anything not explicitly listed is denied, including
  when no mission exists at all.
- **Exclusions override authorization.** A target listed as both authorized
  and excluded is denied.
- **Every decision is a record.** Decisions carry mission id, target, reason
  and a timestamp so they can be appended to the audit log.
- **The resolver cannot be widened at runtime.** There is no API to grant
  targets after construction; scope changes go through a new approved mission.

The public API specified here (Phase 3 acceptance target)::

    from core.scope import ScopeDecision, ScopeResolver, ScopeViolation, assert_authorized

    resolver = ScopeResolver(mission)          # mission: mapping | None
    decision = resolver.decide(target)         # -> ScopeDecision
    resolver.assert_authorized(target)         # raises ScopeViolation if denied
    assert_authorized(mission, target)         # module-level convenience
"""

from __future__ import annotations

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.safety]

MISSION = {
    "mission_id": "m-test-001",
    "title": "synthetic lab inventory",
    "authorized_targets": ["10.10.0.5", "lab-host-a"],
    "exclusions": ["10.10.0.1"],
    "approval_state": "approved",
}


def test_scope_module_exists() -> None:
    import core.scope  # noqa: F401


def test_unlisted_target_is_denied() -> None:
    from core.scope import ScopeResolver, ScopeViolation

    resolver = ScopeResolver(MISSION)
    with pytest.raises(ScopeViolation):
        resolver.assert_authorized("unlisted-host")


def test_authorized_target_is_allowed() -> None:
    from core.scope import ScopeResolver

    resolver = ScopeResolver(MISSION)
    decision = resolver.decide("10.10.0.5")
    assert decision.allowed is True
    assert decision.mission_id == "m-test-001"
    assert decision.target == "10.10.0.5"
    assert decision.reason  # a denial-free decision still explains itself
    assert decision.decided_at  # recorded event, not a bool


def test_exclusion_overrides_authorization() -> None:
    from core.scope import ScopeResolver, ScopeViolation

    mission = {**MISSION, "authorized_targets": MISSION["authorized_targets"] + ["10.10.0.1"]}
    resolver = ScopeResolver(mission)
    with pytest.raises(ScopeViolation):
        resolver.assert_authorized("10.10.0.1")


def test_no_mission_denies_everything() -> None:
    """Absence of a prohibition is not authorization: no mission, no access."""
    from core.scope import ScopeViolation, assert_authorized

    with pytest.raises(ScopeViolation):
        assert_authorized(None, "10.10.0.5")


def test_violation_names_target_and_mission() -> None:
    from core.scope import ScopeResolver, ScopeViolation

    resolver = ScopeResolver(MISSION)
    with pytest.raises(ScopeViolation) as excinfo:
        resolver.assert_authorized("unlisted-host")
    message = str(excinfo.value)
    assert "unlisted-host" in message
    assert "m-test-001" in message


def test_scope_cannot_be_widened_at_runtime() -> None:
    """Agents must not be able to grant themselves new targets."""
    from core.scope import ScopeResolver

    resolver = ScopeResolver(MISSION)
    mutators = {"allow", "add_target", "authorize", "widen", "grant", "set_targets"}
    exposed = {name for name in dir(resolver) if not name.startswith("_")}
    assert not (exposed & mutators), f"resolver exposes scope-widening API: {sorted(exposed & mutators)}"


def test_deny_decisions_are_records_too() -> None:
    from core.scope import ScopeResolver

    resolver = ScopeResolver(MISSION)
    decision = resolver.decide("unlisted-host")
    assert decision.allowed is False
    assert decision.mission_id == "m-test-001"
    assert decision.reason
