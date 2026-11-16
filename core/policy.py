"""Safety policy engine for AEGIS.

Classifies actions (read_only / intrusive / consequential) and gates
consequential actions behind recorded human approval. Every decision is
written to the hash-chained audit log. Consequential + no valid approver =
denied, never deferred-by-default.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from core.audit import AuditLog

__all__ = ["ActionClass", "PolicyDecision", "PolicyEngine", "PolicyError"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class ActionClass:
    READ_ONLY = "read_only"
    INTRUSIVE = "intrusive"
    CONSEQUENTIAL = "consequential"


class PolicyError(Exception):
    """Raised when a consequential action lacks valid approval."""


@dataclass(frozen=True)
class PolicyDecision:
    action_class: str
    decision: str            # allowed | denied | approved | pending_approval
    approver: str | None
    timestamp: str
    reason: str

    def as_contract(self) -> dict:
        """Shape matching run.schema.json policy_decisions items."""
        return {
            "action_class": self.action_class,
            "decision": self.decision,
            "approver": self.approver,
            "timestamp": self.timestamp,
            "reason": self.reason,
        }


class PolicyEngine:
    """Classifies and gates actions. All outcomes are audited."""

    def __init__(self, audit: AuditLog, mission: dict):
        self.audit = audit
        self.mission = mission
        self.approvers = list(mission.get("human_approvers", []))

    def classify(self, action: dict) -> str:
        """Classify an action description: {name, modifies_state?, touches_target?}."""
        if action.get("modifies_state") or action.get("destructive"):
            return ActionClass.CONSEQUENTIAL
        if action.get("touches_target") and not action.get("purely_passive"):
            return ActionClass.INTRUSIVE
        return ActionClass.READ_ONLY

    def check(self, action: dict, approver: str | None = None) -> PolicyDecision:
        """Classify + gate. Consequential actions REQUIRE an approved-by name
        present in the mission's human_approvers. Every outcome is audited."""
        acls = self.classify(action)
        name = action.get("name", "<unnamed>")
        if acls == ActionClass.CONSEQUENTIAL:
            if approver and approver in self.approvers:
                d = PolicyDecision(acls, "approved", approver, _now(),
                                   f"consequential action {name!r} approved by {approver}")
            elif approver:
                d = PolicyDecision(acls, "denied", approver, _now(),
                                   f"approver {approver!r} not in mission human_approvers")
            else:
                d = PolicyDecision(acls, "denied", None, _now(),
                                   f"consequential action {name!r} has no recorded human approval")
        else:
            d = PolicyDecision(acls, "allowed", None, _now(),
                               f"{acls} action {name!r} permitted without approval")
        self.audit.append("policy_decision", d.as_contract())
        return d

    def require(self, action: dict, approver: str | None = None) -> PolicyDecision:
        """Like check() but raises PolicyError when consequential actions are not
        properly approved. Use before executing anything consequential."""
        d = self.check(action, approver)
        if d.action_class == ActionClass.CONSEQUENTIAL and d.decision != "approved":
            raise PolicyError(d.reason)
        return d
