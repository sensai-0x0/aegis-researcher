"""AEGIS workers — research activity producers.

Workers produce OBSERVATIONS + ARTIFACTS only. They never classify weakness
claims; that is the finding-triage skill's job (epistemic ladder).

WorkerBase enforces the method rules structurally:
- .claude/rules/research.md: a task without a hypothesis is a fishing
  expedition -> refused.
- .claude/rules/evidence.md: an observation without raw_evidence -> refused.
- .claude/rules/scope.md: authorization happens in core/orchestrator.py
  BEFORE dispatch; workers never contact targets themselves.
"""
from __future__ import annotations

from typing import Any

__all__ = ["WorkerBase", "TaskError", "WORKER_NAMES"]

WORKER_NAMES = (
    "system_inventory", "static_analysis", "application_testing", "fuzzing",
    "binary_analysis", "firmware", "qemu", "renode",
)


class TaskError(Exception):
    """Task malformed or missing required research discipline."""


class WorkerBase:
    """Base class for all AEGIS workers."""

    name: str = "worker"
    status: str = "implemented"  # or "stub: interface-complete only"

    def run(self, task: dict) -> dict:  # pragma: no cover - interface
        raise NotImplementedError

    # -- shared validation -----------------------------------------------------

    def check_task(self, task: dict) -> None:
        if not isinstance(task, dict):
            raise TaskError("task must be a dict")
        for key in ("target", "purpose", "hypothesis"):
            if not task.get(key) or not str(task[key]).strip():
                raise TaskError(
                    f"task.{key} missing: {self.name} refuses tasks without a "
                    f"stated {key} (.claude/rules/research.md)")

    def check_result(self, result: dict) -> dict:
        if "observations" not in result:
            raise TaskError("worker produced no observations field")
        for obs in result["observations"]:
            if not obs.get("raw_evidence"):
                raise TaskError(
                    "observation without raw_evidence refused "
                    "(.claude/rules/evidence.md)")
        return result

    def envelope(self, observations: list[dict], artifacts: list[str],
                 **extra: Any) -> dict:
        return self.check_result({"observations": observations,
                                  "artifacts": artifacts, **extra})


def get_worker(name: str) -> WorkerBase:
    """Factory. Fails closed on unknown workers."""
    if name not in WORKER_NAMES:
        raise TaskError(f"unknown worker {name!r}; known: {WORKER_NAMES}")
    import importlib
    mod = importlib.import_module(f"workers.{name}.worker")
    return mod.WORKER
