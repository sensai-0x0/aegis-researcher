"""Run orchestration for AEGIS.

The orchestrator owns the run lifecycle (planned -> authorized -> running ->
collecting -> concluded) and dispatches work to workers. It enforces the two
hard invariants:

1. Nothing dispatches without a scope Decision for the task target.
2. No observation exists without at least one evidence artifact
   (.claude/rules/evidence.md #1).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Callable, Protocol
from datetime import datetime, timezone

from core.audit import AuditLog
from core.policy import ActionClass, PolicyEngine
from core.scope import ScopeError, ScopeResolver


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


__all__ = ["Worker", "ObservationError", "Orchestrator", "TRANSITIONS"]

TRANSITIONS = {    "planned": {"authorized"},
    "authorized": {"running", "concluded", "aborted"},  # concluded: authorized run may end unused
    "running": {"collecting", "aborted"},
    "collecting": {"concluded", "aborted"},
    "concluded": set(),
    "aborted": set(),
}


class Worker(Protocol):
    """Workers produce observations + artifacts only; they never classify."""

    name: str

    def run(self, task: dict) -> dict:  # {"observations": [...], "artifacts": [...]}
        ...


class ObservationError(Exception):
    """An observation without evidence was produced — contract violation."""


class Orchestrator:
    def __init__(self, mission: dict, audit: AuditLog, policy: PolicyEngine):
        self.mission = mission
        self.audit = audit
        self.policy = policy
        self.scope = ScopeResolver(mission)
        self.run: dict | None = None

    # -- lifecycle ---------------------------------------------------------

    def start_run(self, adapter: dict, initiated_by: str = "orchestrator") -> dict:
        run = {
            "run_id": str(uuid.uuid4()),
            "mission_id": self.mission["mission_id"],
            "adapter": adapter,
            "started_at": _now(),
            "ended_at": None,
            "status": "planned",
            "workers_invoked": [],
            "policy_decisions": [],
            "artifacts": [],
            "audit_ref": None,
            "provenance": {"initiated_by": initiated_by},
        }
        self.run = run
        self._transition("authorized")
        self.audit.append("run_started", {"run_id": run["run_id"],
                                          "mission_id": run["mission_id"]})
        return run

    def _transition(self, to: str) -> None:
        if self.run is None:
            raise RuntimeError("no run started")
        cur = self.run["status"]
        if to not in TRANSITIONS[cur]:
            raise RuntimeError(f"illegal transition {cur} -> {to}")
        self.run["status"] = to

    def dispatch(self, worker: Worker, task: dict, action: dict | None = None,
                 approver: str | None = None) -> dict:
        """Authorize, classify, and execute a worker task.

        `task` must carry `target`. `action` describes what the worker will do
        (for classification). Returns {"observations": [...], "artifacts": [...]}.
        """
        if self.run is None or self.run["status"] != "authorized":
            raise RuntimeError("run must be in 'authorized' state to dispatch")
        target = task.get("target")
        try:
            decision = self.scope.assert_authorized(target)
        except ScopeError as e:
            self.audit.append("scope_denied", {"target": target, "reason": str(e),
                                               "worker": worker.name})
            raise
        self.audit.append("scope_allowed", {"target": target, "worker": worker.name,
                                            "reason": decision.reason})

        action = action or {"name": f"{worker.name}:{task.get('purpose', 'task')}"}
        pd = self.policy.check(action, approver)
        if pd.action_class == ActionClass.CONSEQUENTIAL and pd.decision != "approved":
            self.audit.append("policy_blocked", {"worker": worker.name, "reason": pd.reason})
            raise PermissionError(pd.reason)
        self.run["policy_decisions"].append(pd.as_contract())

        self._transition("running")
        result = worker.run(task)
        self._validate_result(result)
        self._transition("collecting")

        self.run["workers_invoked"].append({
            "worker": worker.name,
            "purpose": task.get("purpose", ""),
            "hypothesis": task.get("hypothesis", ""),
            "started_at": _now(),
            "ended_at": _now(),
        })
        self.run["artifacts"].extend(result.get("artifacts", []))
        self.audit.append("worker_completed", {
            "worker": worker.name,
            "observations": len(result.get("observations", [])),
            "artifacts": len(result.get("artifacts", [])),
        })
        return result

    def conclude(self) -> dict:
        self._transition("concluded")
        self.run["ended_at"] = _now()
        self.run["audit_ref"] = f"audit-chain:{self.audit.head_hash()[:12]}"
        self.audit.append("run_concluded", {"run_id": self.run["run_id"],
                                            "audit_ref": self.run["audit_ref"]})
        return self.run

    # -- invariants ---------------------------------------------------------

    @staticmethod
    def _validate_result(result: dict) -> None:
        for obs in result.get("observations", []):
            if not obs.get("raw_evidence"):
                raise ObservationError(
                    f"observation {obs.get('observation_id', '<no-id>')} has no "
                    f"raw_evidence: .claude/rules/evidence.md #1 violated")
