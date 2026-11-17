"""Claude Code adapter. No policy/scope/evidence logic lives here — see README."""
from __future__ import annotations

__all__ = ["ClaudeCodeAdapter", "ADAPTER"]

VERSION = "0.1.0"

# Routing table mirror of CLAUDE.md (documentation, not logic).
ROUTING = {
    "inventory": {"skill": "inventory", "agent": "systems-analyst"},
    "source-review": {"skill": "source-review", "agent": "source-analyst"},
    "finding-triage": {"skill": "finding-triage", "agent": "reviewer"},
    "evidence": {"skill": None, "agent": "evidence-curator"},
}


class ClaudeCodeAdapter:
    name = "claude_code"
    version = VERSION

    def prepare(self, mission: dict) -> dict:
        """Contract mission -> harness work plan. Steps route to skills/agents."""
        steps = []
        for target in mission.get("authorized_targets", []):
            steps.append({
                "step_id": f"inventory:{target['value']}",
                "kind": "inventory",
                "target": target["value"],
                "route": ROUTING["inventory"],
                "worker": "system_inventory",
            })
        return {
            "adapter": self.name,
            "mission_id": mission["mission_id"],
            "steps": steps,
            "note": "execute() runs each step through core/orchestrator.py; "
                    "scope and policy decisions happen in core, never here.",
        }

    def execute(self, step: dict) -> dict:
        """One plan step -> observation envelope shape (harness-neutral)."""
        return {
            "step_id": step.get("step_id"),
            "adapter": self.name,
            "route": step.get("route"),
            "status": "handed-to-orchestrator",
            "note": "actual execution is dispatched via core/orchestrator.dispatch()",
        }

    def report(self, run: dict) -> dict:
        """Contract run -> harness-neutral report summary."""
        return {
            "adapter": self.name,
            "run_id": run.get("run_id"),
            "status": run.get("status"),
            "workers": len(run.get("workers_invoked", [])),
            "artifacts": len(run.get("artifacts", [])),
            "policy_decisions": len(run.get("policy_decisions", [])),
        }


ADAPTER = ClaudeCodeAdapter()
