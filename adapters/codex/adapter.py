"""Codex adapter. Same canonical contracts as claude_code; no core logic here."""
from __future__ import annotations

__all__ = ["CodexAdapter", "ADAPTER"]

VERSION = "0.1.0"


class CodexAdapter:
    name = "codex"
    version = VERSION

    def prepare(self, mission: dict) -> dict:
        steps = [{
            "step_id": f"inventory:{t['value']}",
            "kind": "inventory",
            "target": t["value"],
            "worker": "system_inventory",
        } for t in mission.get("authorized_targets", [])]
        return {
            "adapter": self.name,
            "mission_id": mission["mission_id"],
            "steps": steps,
            "note": "consumes the same contract schemas as every other adapter",
        }

    def execute(self, step: dict) -> dict:
        return {"step_id": step.get("step_id"), "adapter": self.name,
                "status": "handed-to-orchestrator"}

    def report(self, run: dict) -> dict:
        return {
            "adapter": self.name,
            "run_id": run.get("run_id"),
            "status": run.get("status"),
            "artifacts": len(run.get("artifacts", [])),
        }


ADAPTER = CodexAdapter()
