"""TDD spec for ``core/policy.py`` — approval gating (currently red).

Behavioral mirror of ``.claude/rules/scope.md`` §MUST-5 and the operating
contract principle *"agents propose and interpret; the control plane
authorizes"*. The eval heuristic ``safety.policy-approval-gating`` checks
that consequential actions are gated behind recorded human approval; these
tests define the exact semantics:

- Actions are classified: ``READ_ONLY`` / ``INTRUSIVE`` / ``CONSEQUENTIAL``.
- Unclassifiable operations default to ``CONSEQUENTIAL`` (deny-by-default).
- Consequential actions require a recorded human approval token.
- **No self-approval**: an approval token issued by the same agent run that
  requests the action is rejected.
- Every decision is a record, not a boolean.

The public API specified here (Phase 3 acceptance target)::

    from core.policy import ActionClass, PolicyDecision, classify_action, evaluate

    classify_action(operation)                # -> ActionClass
    evaluate(request, approval=None)          # -> PolicyDecision
"""

from __future__ import annotations

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.safety]

READ_ONLY_OPS = ("read", "list", "stat", "get", "inspect")
CONSEQUENTIAL_OPS = ("write", "delete", "execute", "modify_state", "external_disclosure")

HUMAN_APPROVAL = {"approved_by": "human-owner", "approved_at": "2026-11-17T00:00:00Z"}


def _request(operation: str, requested_by: str = "agent-run-1") -> dict:
    return {
        "request_id": "req-001",
        "mission_id": "m-test-001",
        "operation": operation,
        "target_asset_id": "asset-lab-host-a",
        "requested_by": requested_by,
    }


def test_policy_module_exists() -> None:
    import core.policy  # noqa: F401


@pytest.mark.parametrize("operation", READ_ONLY_OPS)
def test_read_only_operations_are_classified_read_only(operation: str) -> None:
    from core.policy import ActionClass, classify_action

    assert classify_action(operation) is ActionClass.READ_ONLY


@pytest.mark.parametrize("operation", CONSEQUENTIAL_OPS)
def test_consequential_operations_are_classified_consequential(operation: str) -> None:
    from core.policy import ActionClass, classify_action

    assert classify_action(operation) is ActionClass.CONSEQUENTIAL


def test_unknown_operation_defaults_to_consequential() -> None:
    """Deny-by-default posture: unclassifiable operations are treated as consequential."""
    from core.policy import ActionClass, classify_action

    assert classify_action("frobnicate") is ActionClass.CONSEQUENTIAL


def test_consequential_action_without_approval_is_denied() -> None:
    from core.policy import evaluate

    decision = evaluate(_request("delete"), approval=None)
    assert decision.allowed is False
    assert "approval" in decision.reason.lower()


def test_consequential_action_with_human_approval_is_allowed() -> None:
    from core.policy import evaluate

    decision = evaluate(_request("delete"), approval=HUMAN_APPROVAL)
    assert decision.allowed is True
    assert decision.decided_at


def test_agent_cannot_self_approve() -> None:
    """An approval token from the requesting agent run is not human approval."""
    from core.policy import evaluate

    self_approval = {"approved_by": "agent-run-1", "approved_at": "2026-11-17T00:00:00Z"}
    decision = evaluate(_request("delete", requested_by="agent-run-1"), approval=self_approval)
    assert decision.allowed is False
    assert "self" in decision.reason.lower() or "approval" in decision.reason.lower()


def test_read_only_action_needs_no_approval() -> None:
    from core.policy import evaluate

    decision = evaluate(_request("read"), approval=None)
    assert decision.allowed is True


def test_policy_decision_is_a_record() -> None:
    from core.policy import evaluate

    decision = evaluate(_request("delete"), approval=None)
    for field in ("mission_id", "operation", "allowed", "reason", "decided_at"):
        assert hasattr(decision, field), f"PolicyDecision must expose '{field}'"
