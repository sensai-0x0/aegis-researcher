"""Evidence vault — content-addressed artifact store (curriculum P01/W2).

Store raw outputs immutably; verify hashes on every store AND retrieval.
Objects live at evidence/objects/<sha256[:2]>/<sha256>; the returned record
matches contracts/artifact.schema.json (custody events are appended by the
evidence-curator flow).
"""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

__all__ = ["EvidenceVault", "EvidenceIntegrityError"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class EvidenceIntegrityError(Exception):
    """Content does not match its content address."""


class EvidenceVault:
    def __init__(self, objects_dir: str | Path):
        self.root = Path(objects_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    # -- store -----------------------------------------------------------------

    def store(self, source: str | Path, run_id: str, media_type: str = "application/octet-stream",
              tool: str = "unknown", tool_version: str = "0", command: str | None = None) -> dict:
        """Hash, place, verify. Returns the artifact record (pre-custody)."""
        src = Path(source)
        if not src.is_file():
            raise FileNotFoundError(src)
        digest = self._sha256(src)
        dest = self._path_for(digest)
        if dest.is_file():
            # Immutability: an existing object with the same hash is identical.
            self.verify(digest)
            existed = True
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            self.verify(digest)  # P01 exit: hash verifies after storage
            existed = False
        return {
            "artifact_id": digest,
            "sha256": digest,
            "media_type": media_type,
            "size": src.stat().st_size,
            "produced_by": {"run_id": run_id},
            "source": {"tool": tool, "version": tool_version, "command": command},
            "custody": [
                {"actor": f"vault:{self.__class__.__name__}",
                 "action": "stored" if not existed else "verified",
                 "timestamp": _now(),
                 "note": "content-address verified on store"},
            ],
            "created_at": _now(),
        }

    # -- retrieval ---------------------------------------------------------------

    def open(self, artifact_id: str) -> Path:
        p = self._path_for(artifact_id)
        if not p.is_file():
            raise FileNotFoundError(f"artifact {artifact_id} not present")
        self.verify(artifact_id)  # P01 exit: hash verifies after retrieval
        return p

    def verify(self, artifact_id: str) -> None:
        p = self._path_for(artifact_id)
        if not p.is_file():
            raise EvidenceIntegrityError(f"missing object for {artifact_id}")
        actual = self._sha256(p)
        if actual != artifact_id:
            raise EvidenceIntegrityError(
                f"integrity failure: object at {p} hashes to {actual}, expected {artifact_id}")

    # -- internals -----------------------------------------------------------------

    def _path_for(self, digest: str) -> Path:
        return self.root / digest[:2] / digest

    @staticmethod
    def _sha256(p: Path) -> str:
        h = hashlib.sha256()
        with p.open("rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def record_to_manifest(record: dict) -> str:
        return json.dumps(record, sort_keys=True)
