"""system_inventory worker — local component enumeration with evidence.

Produces one content-addressed artifact (the inventory listing) and one
observation per top-level component. Authorization is the orchestrator's job;
this worker touches only the path it is given.
"""
from __future__ import annotations

import hashlib
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from workers import WorkerBase, TaskError

__all__ = ["SystemInventoryWorker", "WORKER"]

MAX_DEPTH = 4
MAX_ENTRIES = 5000


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class SystemInventoryWorker(WorkerBase):
    name = "system_inventory"
    status = "implemented"

    def run(self, task: dict) -> dict:
        self.check_task(task)
        root = Path(str(task.get("path", task["target"])))
        if not root.is_dir():
            raise TaskError(f"inventory target is not a directory: {root}")

        lines: list[str] = []
        components = sorted(p.name for p in root.iterdir()
                            if not p.name.startswith("."))
        for dirpath, dirnames, filenames in os.walk(root):
            depth = len(Path(dirpath).relative_to(root).parts)
            if depth >= MAX_DEPTH:
                dirnames[:] = []
            dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
            for fn in sorted(filenames):
                if len(lines) >= MAX_ENTRIES:
                    break
                p = Path(dirpath) / fn
                rel = p.relative_to(root)
                try:
                    mode = "x" if os.access(p, os.X_OK) else "-"
                    size = p.stat().st_size
                except OSError:
                    continue
                lines.append(f"{mode} {size:>10} {rel}")
        listing = "\n".join(lines) + "\n"

        digest = hashlib.sha256(listing.encode()).hexdigest()
        run_id = task.get("run_id", "00000000-0000-4000-8000-000000000000")
        artifact = {
            "artifact_id": digest, "sha256": digest, "media_type": "text/plain",
            "size": len(listing), "produced_by": {"run_id": run_id, "worker": self.name},
            "source": {"tool": "aegis.system_inventory", "version": "0.1.0"},
            "custody": [{"actor": f"worker:{self.name}", "action": "collected",
                         "timestamp": _now()}],
            "created_at": _now(),
        }
        observations = [{
            "observation_id": str(uuid.uuid4()),
            "run_id": run_id,
            "target": {"kind": "component", "identifier": comp},
            "method": {"worker": self.name,
                       "description": f"listed in inventory of {root}",
                       "tool": "aegis.system_inventory 0.1.0"},
            "raw_evidence": [digest],
            "confidence": "high",
            "hypothesis_id": task.get("hypothesis_id"),
            "created_at": _now(),
            "provenance": {"collected_by": f"worker:{self.name}"},
        } for comp in components]

        return self.envelope(
            observations, [digest],
            artifact=artifact,
            raw=listing,
            coverage_note=f"{len(components)} top-level components, "
                          f"{len(lines)} entries, truncated at {MAX_ENTRIES}",
        )


WORKER = SystemInventoryWorker()
