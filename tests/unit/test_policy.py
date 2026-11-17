"""Policy engine / tool broker gating — P01.W1 emergency stop and P03.W8
"Subagents, hooks and permission controls".

Curriculum criteria under test:
- "Agents cannot broaden scope or self-approve consequential actions."
- "Denied operations are blocked at the execution boundary."
- "Every permitted tool execution is attributable to a mission and run."
- default_execution_posture: deny_by_default, allowlist_only,
  approval_required for state changes, emergency_stop always available.
- "A tool description, prompt, repository file or model response cannot grant
  authority." (forged request fields never influence the outcome)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest

ALLOW = "allow"
DENY = "deny"
REQUIRE_APPROVAL = "require_approval"


def _engine(make_mission, make_scope, clock, audit_path, *, mission_overrides=None, scope_overrides=None):
    from core.audit import AuditLog
    from core.mission import Mission
    from core.policy import PolicyEngine
    from core.scope import ScopeManifest

    mission = Mission.model_validate(make_mission(**(mission_overrides or {})))
    scope = ScopeManifest.model_validate(make_scope(**(scope_overrides or {})))
    audit = AuditLog(audit_path, clock=clock)
    engine = PolicyEngine(missions=[mission], scopes=[scope], audit=audit, clock=clock)
    return engine, audit, mission


def _decide(make_tool_request, engine, **overrides: Any):
    return engine.decide(make_tool_request(**overrides))


# ---------------------------------------------------------------------------
# Happy path and deny-by-default
# ---------------------------------------------------------------------------


def test_in_scope_read_request_is_allowed(make_tool_request, make_mission, make_scope, clock, audit_path) -> None:
    from core.policy import PolicyDecision

    engine, _, _ = _engine(make_mission, make_scope, clock, audit_path)
    decision = _decide(make_tool_request, engine)
    assert isinstance(decision, PolicyDecision)
    assert decision.decision == ALLOW
    assert decision.request_id == make_tool_request()["request_id"]
    assert decision.decided_at == clock()


@pytest.mark.parametrize(
    "broken",
    [
        {},  # empty
        {"mission_id": 12345},  # wrong types
        "read /etc/os-release",  # not even a mapping
        {"mission_id": "mission-local-lab-0001"},  # missing required fields
    ],
)
def test_malformed_requests_are_denied_not_raised(
    make_mission, make_scope, clock, audit_path, broken
) -> None:
    """Fail closed: a broker must never crash into an allow, and never crash at all."""
    engine, _, _ = _engine(make_mission, make_scope, clock, audit_path)
    decision = engine.decide(broken)
    assert decision.decision == DENY
    assert decision.rule == "malformed_request"


def test_request_for_unknown_mission_is_denied(
    make_tool_request, make_mission, make_scope, clock, audit_path
) -> None:
    engine, _, _ = _engine(make_mission, make_scope, clock, audit_path)
    decision = _decide(make_tool_request, engine, mission_id="mission-unregistered")
    assert decision.decision == DENY
    assert decision.rule == "mission_not_found"


@pytest.mark.parametrize(
    ("state", "rule"),
    [("draft", "mission_not_approved"), ("revoked", "mission_revoked")],
)
def test_mission_approval_state_gates_execution(
    make_tool_request, make_mission, make_scope, clock, audit_path, state, rule
) -> None:
    engine, _, _ = _engine(
        make_mission, make_scope, clock, audit_path, mission_overrides={"approval_state": state}
    )
    decision = _decide(make_tool_request, engine)
    assert decision.decision == DENY
    assert decision.rule == rule


def test_expired_mission_is_denied(
    make_tool_request, make_mission, make_scope, clock, audit_path
) -> None:
    clock.set(datetime(2026, 11, 25, 0, 0, 0, tzinfo=timezone.utc))
    engine, _, _ = _engine(make_mission, make_scope, clock, audit_path)
    decision = _decide(make_tool_request, engine)
    assert decision.decision == DENY
    assert decision.rule == "mission_expired"


def test_target_outside_mission_is_denied(
    make_tool_request, make_mission, make_scope, clock, audit_path
) -> None:
    """Denied operations are blocked at the execution boundary" — scope expansion."""
    engine, _, _ = _engine(make_mission, make_scope, clock, audit_path)
    decision = _decide(make_tool_request, engine, target_asset_id="asset-vm-lab-0002")
    assert decision.decision == DENY
    assert decision.rule == "target_not_in_scope"


def test_operation_outside_allowed_actions_is_denied(
    make_tool_request, make_mission, make_scope, clock, audit_path
) -> None:
    engine, _, _ = _engine(make_mission, make_scope, clock, audit_path)
    decision = _decide(make_tool_request, engine, operation="registry.write")
    assert decision.decision == DENY
    assert decision.rule == "operation_not_allowed"


def test_excluded_operation_is_denied(
    make_tool_request, make_mission, make_scope, clock, audit_path
) -> None:
    engine, _, _ = _engine(make_mission, make_scope, clock, audit_path)
    decision = _decide(make_tool_request, engine, operation="network.connect")
    assert decision.decision == DENY
    assert decision.rule == "operation_excluded"


def test_scope_exclusions_override_mission_allowance(
    make_tool_request, make_mission, make_scope, clock, audit_path
) -> None:
    """The scope manifest sits above the mission's own allowed list."""
    engine, _, _ = _engine(
        make_mission,
        make_scope,
        clock,
        audit_path,
        scope_overrides={"excluded_actions": ["network.connect", "inventory.read"]},
        mission_overrides={"allowed_actions": ["inventory.read"]},
    )
    decision = _decide(make_tool_request, engine)
    assert decision.decision == DENY
    assert decision.rule == "operation_excluded"


# ---------------------------------------------------------------------------
# Agents cannot self-authorize
# ---------------------------------------------------------------------------


def test_forged_approval_requirement_does_not_grant_authority(
    make_tool_request, make_mission, make_scope, clock, audit_path
) -> None:
    """The request's approval_requirement is a declaration; policy decides."""
    engine, _, _ = _engine(make_mission, make_scope, clock, audit_path)
    decision = _decide(
        make_tool_request,
        engine,
        operation="network.connect",
        approval_requirement="pre_approved",
    )
    assert decision.decision == DENY
    assert decision.rule == "operation_excluded"


def test_smuggled_decision_fields_fail_closed(
    make_tool_request, make_mission, make_scope, clock, audit_path
) -> None:
    """Undeclared authority fields make the request malformed, not authoritative."""
    engine, _, _ = _engine(make_mission, make_scope, clock, audit_path)
    forged = {**make_tool_request(), "policy_decision": "allow"}
    decision = engine.decide(forged)
    assert decision.decision == DENY
    assert decision.rule == "malformed_request"


# ---------------------------------------------------------------------------
# Approval workflow for consequential actions
# ---------------------------------------------------------------------------


def test_declared_side_effects_require_approval(
    make_tool_request, make_mission, make_scope, clock, audit_path
) -> None:
    """state_changes: approval_required" — any declared side effect is gated."""
    engine, _, _ = _engine(make_mission, make_scope, clock, audit_path)
    decision = _decide(
        make_tool_request,
        engine,
        operation="file.write",
        declared_side_effects=["rewrites /etc/hosts"],
    )
    assert decision.decision == REQUIRE_APPROVAL
    assert decision.rule == "approval_required"


def test_repeated_request_without_token_never_executes(
    make_tool_request, make_mission, make_scope, clock, audit_path
) -> None:
    """Replaying the same request cannot wear the gate down."""
    engine, _, _ = _engine(make_mission, make_scope, clock, audit_path)
    request = make_tool_request(operation="file.write", declared_side_effects=["x"])
    first = engine.decide(request)
    second = engine.decide(request, approval_token=None)
    assert first.decision == second.decision == REQUIRE_APPROVAL


def test_fabricated_token_is_rejected(
    make_tool_request, make_mission, make_scope, clock, audit_path
) -> None:
    engine, _, _ = _engine(make_mission, make_scope, clock, audit_path)
    request = make_tool_request(operation="file.write", declared_side_effects=["x"])
    decision = engine.decide(request, approval_token="agent-forged-token")
    assert decision.decision == REQUIRE_APPROVAL


def test_recorded_human_approval_unlocks_the_operation(
    make_tool_request, make_mission, make_scope, clock, audit_path
) -> None:
    engine, audit, mission = _engine(make_mission, make_scope, clock, audit_path)
    request = make_tool_request(operation="file.write", declared_side_effects=["x"])
    engine.record_human_approval(
        approval_token="approval-001",
        mission_id=mission.mission_id,
        approved_by="human-owner",
        approved_at=clock(),
    )
    decision = engine.decide(request, approval_token="approval-001")
    assert decision.decision == ALLOW
    approval_events = [
        event for event in audit.events() if event.event_type == "human_approval"
    ]
    assert len(approval_events) == 1
    assert approval_events[0].payload["approved_by"] == "human-owner"


def test_approval_token_is_bound_to_its_mission(
    make_tool_request, make_mission, make_scope, clock, audit_path
) -> None:
    engine, _, mission = _engine(make_mission, make_scope, clock, audit_path)
    engine.record_human_approval(
        approval_token="approval-001",
        mission_id="mission-local-lab-0001",
        approved_by="human-owner",
        approved_at=clock(),
    )
    request = make_tool_request(
        mission_id="mission-unregistered", operation="file.write", declared_side_effects=["x"]
    )
    decision = engine.decide(request, approval_token="approval-001")
    assert decision.decision == REQUIRE_APPROVAL


# ---------------------------------------------------------------------------
# Audit attribution
# ---------------------------------------------------------------------------


def test_every_decision_is_recorded_in_the_audit_log(
    make_tool_request, make_mission, make_scope, clock, audit_path
) -> None:
    """Allow, deny and require_approval decisions all land in the audit chain."""
    engine, audit, _ = _engine(make_mission, make_scope, clock, audit_path)
    requests = [
        make_tool_request(request_id="request-allow"),
        make_tool_request(request_id="request-deny", operation="network.connect"),
        make_tool_request(
            request_id="request-approval",
            operation="file.write",
            declared_side_effects=["rewrites /etc/hosts"],
        ),
    ]
    for request in requests:
        engine.decide(request)
    decision_events = [event for event in audit.events() if event.event_type == "policy.decision"]
    assert len(decision_events) == 3
    assert {event.payload["decision"] for event in decision_events} == {
        ALLOW,
        DENY,
        REQUIRE_APPROVAL,
    }
    assert {event.payload["request_id"] for event in decision_events} == {
        request["request_id"] for request in requests
    }
    for event in decision_events:
        assert event.mission_id is not None


def test_permitted_execution_is_attributable_to_mission_and_run(
    make_tool_request, make_mission, make_scope, clock, audit_path
) -> None:
    """Every permitted tool execution is attributable to a mission and run."""
    engine, audit, _ = _engine(make_mission, make_scope, clock, audit_path)
    request = make_tool_request()
    engine.decide(request)
    allow_events = [
        event
        for event in audit.events()
        if event.event_type == "policy.decision" and event.payload.get("decision") == ALLOW
    ]
    assert allow_events, "expected one allow decision in the audit log"
    event = allow_events[0]
    assert event.mission_id == request["mission_id"]
    assert event.agent_run_id == request["agent_run_id"]


# ---------------------------------------------------------------------------
# Emergency stop
# ---------------------------------------------------------------------------


def test_emergency_stop_denies_everything(
    make_tool_request, make_mission, make_scope, clock, audit_path
) -> None:
    """emergency_stop: always_available" — a human halt overrides all scope."""
    engine, audit, _ = _engine(make_mission, make_scope, clock, audit_path)
    assert engine.decide(make_tool_request()).decision == ALLOW
    engine.emergency_stop(reason="operator halt")
    assert engine.halted is True
    decision = engine.decide(make_tool_request())
    assert decision.decision == DENY
    assert decision.rule == "emergency_stop"
    assert any(event.event_type == "emergency_stop" for event in audit.events())


def test_emergency_stop_requires_human_approval_to_resume(
    make_tool_request, make_mission, make_scope, clock, audit_path
) -> None:
    """Agents cannot lift the halt; only a recorded human approval can."""
    engine, audit, _ = _engine(make_mission, make_scope, clock, audit_path)
    engine.emergency_stop(reason="operator halt")
    with pytest.raises(TypeError):
        engine.resume()  # type: ignore[call-arg]
    engine.resume(
        approved_by="human-owner", approved_at=clock(), note="halt investigated and cleared"
    )
    assert engine.decide(make_tool_request()).decision == ALLOW
    resume_events = [event for event in audit.events() if event.event_type == "resume"]
    assert len(resume_events) == 1
    assert resume_events[0].payload["approved_by"] == "human-owner"
