"""qemu worker — interface-complete stub (see WORKER.md)."""
from __future__ import annotations

from workers import WorkerBase

__all__ = ["QemuWorker", "WORKER"]


class QemuWorker(WorkerBase):
    name = "qemu"
    status = "stub: interface-complete only"

    def run(self, task: dict) -> dict:
        self.check_task(task)  # even stubs refuse hypothesis-free tasks
        raise NotImplementedError(
            f"qemu is an interface-complete stub; wire its toolchain per WORKER.md — never fabricate observations")


WORKER = QemuWorker()
