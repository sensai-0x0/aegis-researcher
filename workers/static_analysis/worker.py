"""static_analysis worker — interface-complete stub (see WORKER.md)."""
from __future__ import annotations

from workers import WorkerBase

__all__ = ["StaticAnalysisWorker", "WORKER"]


class StaticAnalysisWorker(WorkerBase):
    name = "static_analysis"
    status = "stub: interface-complete only"

    def run(self, task: dict) -> dict:
        self.check_task(task)  # even stubs refuse hypothesis-free tasks
        raise NotImplementedError(
            f"static_analysis is an interface-complete stub; wire its toolchain per WORKER.md — never fabricate observations")


WORKER = StaticAnalysisWorker()
