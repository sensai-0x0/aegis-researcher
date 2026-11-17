"""Append-only, hash-chained audit log for AEGIS.

Every authorization and policy decision is recorded here. The log is
tamper-evident: each entry carries the previous entry's hash and its own
sha256 over the canonical payload. Entries are NEVER removed; verification
replays the chain and reports the first corrupted sequence number.
"""
from __future__ import annotations

import hashlib
import json
import threading
from datetime import datetime, timezone
from pathlib import Path

__all__ = ["AuditLog", "AuditCorruptionError", "GENESIS"]

GENESIS = "0" * 64


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class AuditCorruptionError(Exception):
    """The chain does not verify: evidence integrity is compromised."""


class AuditLog:
    """JSONL-backed, hash-chained, append-only audit log. Thread-safe."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._entries: list[dict] = []
        self._load_existing()

    # -- append (the only mutation) ------------------------------------------

    def append(self, event: str, payload: dict) -> dict:
        with self._lock:
            prev = self._entries[-1]["hash"] if self._entries else GENESIS
            entry = {
                "seq": len(self._entries),
                "timestamp": _now(),
                "event": event,
                "payload": payload,
                "prev_hash": prev,
            }
            entry["hash"] = self._hash(entry)
            self._entries.append(entry)
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, sort_keys=True) + "\n")
            return entry

    # -- verification ---------------------------------------------------------

    def verify(self) -> tuple[bool, int | None]:
        """Recompute the whole chain. Returns (ok, first_bad_seq_or_None)."""
        prev = GENESIS
        for i, entry in enumerate(self._entries):
            expected = dict(entry)
            claimed = expected["hash"]
            expected["hash"] = self._hash({k: v for k, v in entry.items() if k != "hash"})
            if entry["prev_hash"] != prev or claimed != expected["hash"]:
                return False, i
            prev = claimed
        return True, None

    def entries(self, event: str | None = None) -> list[dict]:
        return [e for e in self._entries if event is None or e["event"] == event]

    def head_hash(self) -> str:
        return self._entries[-1]["hash"] if self._entries else GENESIS

    # -- internals --------------------------------------------------------------

    @staticmethod
    def _hash(entry: dict) -> str:
        return hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()

    def _load_existing(self) -> None:
        if not self.path.is_file():
            return
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                self._entries.append(json.loads(line))
        ok, bad = self.verify()
        if not ok:
            raise AuditCorruptionError(
                f"audit chain corrupted at seq {bad}: refusing to operate "
                f"(evidence integrity outranks availability)")
