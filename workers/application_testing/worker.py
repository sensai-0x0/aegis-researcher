"""application_testing worker — interface-complete stub (see WORKER.md)."""
from __future__ import annotations

from workers import WorkerBase

__all__ = ["ApplicationTestingWorker", "WORKER"]


class ApplicationTestingWorker(WorkerBase):
    name = "application_testing"
    status = "stub: interface-complete only"

    def run(self, task: dict) -> dict:
        self.check_task(task)  # even stubs refuse hypothesis-free tasks
        raise NotImplementedError(
            f"application_testing is an interface-complete stub; wire its toolchain per WORKER.md — never fabricate observations")


WORKER = ApplicationTestingWorker()
