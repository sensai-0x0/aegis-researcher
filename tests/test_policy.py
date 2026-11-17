"""TDD spec for ``core/policy.py`` — the authorization control plane (red).

Behavioral mirror of ``.claude/rules/scope.md`` and the operating contract
principle *"agents propose and interpret; the control plane authorizes"*.
The conftest ``make_orchestrator`` bundle fixes the construction shape::

    from core.policy import PolicyEngine, ToolRequest

    engine = PolicyEngine(missions=[mission], scopes=[scope], audit=audit, clock=clock)
    request = ToolRequest.model_validate(make_tool_request())
    decision = engine.decide(request)   # -> allowed / reason / decided_at

Semantics specified here (all derived from the curriculum's
``default_execution_posture`` and goal.md hard failures):

1. A request is allowed only when *every* gate passes: approved unexpired
   mission, approved unexpired scope, target in the scope's targets,
   operation in ``allowed_actions`` and not in ``excluded_actions``.
2. **Deny by default**: unlisted operations are denied.
3. **Exclusions override the allowlist** — listing an operation in both is
   still a denial.
4. **Network is deny-by-default**: with the scope's ``network.default =
   "deny"`` and no allowed destinations, ``network.connect`` is denied.
5. **Consequential actions need recorded human approval**; an unapproved
   request carrying ``approval_requirement: "human_approval"`` is denied.
6. **Every decision is a record** (not a boolean) and **every decision is
   appended to the audit chain**.
7. **The engine cannot be widened at runtime** — there is no API to grant
   missions, scopes or operations after construction.
"""

from __future__ import annotations

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.safety]


@pytest.fixture()
def engine_factory(make_mission, make_scope, audit_path, clock):
    """Build a PolicyEngine around one approved mission + scope."""

    def _make(mission_overrides=None, scope_overrides=None):
        from core.audit import AuditLog
        from core.mission import Mission
        from core.policy import PolicyEngine
        from core.scope import ScopeManifest

        mission = Mission.model_validate(make_mission(**(mission_overrides or {})))
        scope = ScopeManifest.model_validate(make_scope(**(scope_overrides or {})))
        audit = AuditLog(audit_path, clock=clock)
        engine = PolicyEngine(missions=[mission], scopes=[scope], audit=audit, clock=clock)
        return engine, audit

    return _make


@pytest.fixture()
def request_factory(make_tool_request):
    """Build a ToolRequest from the canonical payload."""

    def _make(**overrides):
        from core.policy import ToolRequest

        return ToolRequest.model_validate(make_tool_request(**overrides))

    return _make


# --- The happy path -----------------------------------------------------------


def test_in_scope_read_only_request_is_allowed(engine_factory, request_factory) -> None:
    engine, _ = engine_factory()
    decision = engine.decide(request_factory())
    assert decision.allowed is True
    assert decision.reason
    assert decision.decided_at


# --- Deny-by-default gates ------------------------------------------------------


def test_target_outside_scope_is_denied(engine_factory, request_factory) -> None:
    engine, _ = engine_factory()
    request = request_factory(target_asset_id="asset-someone-elses-box")
    decision = engine.decide(request)
    assert decision.allowed is False
    assert "asset-someone-elses-box" in decision.reason


def test_unlisted_operation_is_denied(engine_factory, request_factory) -> None:
    """Nothing outside allowed_actions is permitted — absence is not authorization."""
    engine, _ = engine_factory()
    decision = engine.decide(request_factory(operation="firmware.flash"))
    assert decision.allowed is False
    assert "firmware.flash" in decision.reason


def test_excluded_operation_is_denied_even_if_allowlisted(engine_factory, request_factory) -> None:
    """Exclusions take precedence over the allowlist."""
    engine, _ = engine_factory(
        mission_overrides={"allowed_actions": ["inventory.read", "file.write"]}
    )
    decision = engine.decide(request_factory(operation="file.write"))
    assert decision.allowed is False
    assert "file.write" in decision.reason


def test_network_is_deny_by_default(engine_factory, request_factory) -> None:
    """Scope network.default=deny with no allowed destinations blocks contact."""
    engine, _ = engine_factory()
    decision = engine.decide(request_factory(operation="network.connect"))
    assert decision.allowed is False


def test_expired_mission_denies_everything(engine_factory, request_factory) -> None:
    """An expired authorization is not an authorization."""
    engine, _ = engine_factory(
        mission_overrides={"expiry_time": "2026-11-10T00:00:00+00:00"}
    )
    decision = engine.decide(request_factory())
    assert decision.allowed is False


def test_expired_scope_denies_everything(engine_factory, request_factory) -> None:
    engine, _ = engine_factory(
        scope_overrides={"expires_at": "2026-11-10T00:00:00+00:00"}
    )
    decision = engine.decide(request_factory())
    assert decision.allowed is False


def test_unapproved_mission_denies_everything(engine_factory, request_factory) -> None:
    engine, _ = engine_factory(mission_overrides={"approval_state": "pending"})
    decision = engine.decide(request_factory())
    assert decision.allowed is False


# --- Approval gating for consequential actions ------------------------------------


def test_consequential_action_without_approval_is_denied(engine_factory, request_factory) -> None:
    engine, _ = engine_factory()
    request = request_factory(operation="file.write", approval_requirement="human_approval")
    decision = engine.decide(request)
    assert decision.allowed is False
    assert "approval" in decision.reason.lower()


# --- Decisions are records, and they are audited -----------------------------------


def test_decision_is_a_record(engine_factory, request_factory) -> None:
    engine, _ = engine_factory()
    decision = engine.decide(request_factory())
    for field in ("allowed", "reason", "decided_at"):
        assert hasattr(decision, field), f"PolicyDecision must expose '{field}'"


def test_every_decision_is_appended_to_the_audit_chain(engine_factory, request_factory) -> None:
    """goal.md: unlogged consequential execution is a hard failure."""
    engine, audit = engine_factory()
    engine.decide(request_factory())
    engine.decide(request_factory(operation="firmware.flash"))  # denied too

    assert audit.verify() is True
    entries = list(audit.entries())
    assert len(entries) >= 2, "each decision (allowed or denied) must be audited"
    joined = " ".join(str(entry) for entry in entries)
    assert "request-local-lab-0001" in joined


# --- The engine cannot be widened ----------------------------------------------------


def test_engine_cannot_be_widened_at_runtime(engine_factory) -> None:
    """Agents must not be able to grant themselves missions, scopes or operations."""
    engine, _ = engine_factory()
    mutators = {
        "add_mission", "add_scope", "grant", "widen", "allow", "allow_operation", "set_policy",
    }
    exposed = {name for name in dir(engine) if not name.startswith("_")}
    assert not (exposed & mutators), (
        f"PolicyEngine exposes scope-widening API: {sorted(exposed & mutators)}"
    )
