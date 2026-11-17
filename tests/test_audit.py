"""TDD spec for ``core/audit.py`` — append-only hash-chained log (currently red).

The eval heuristic ``safety.audit-append-only`` requires a hash-chained,
append-only audit log with no delete path; ``goal.md`` §Verify makes
``core/audit.py`` the guarantor of chain of custody. These tests define the
exact semantics:

- Entries chain via SHA-256: ``entry[i].prev_hash == entry[i-1].hash``; the
  first entry chains to a genesis hash of 64 zeros.
- ``verify()`` accepts an intact log and rejects any tampered byte.
- The API exposes **no** delete/truncate/remove/rewrite path — correction
  happens by appending a superseding event, never by mutating history.
- Appending preserves every prior byte on disk.

The public API specified here (Phase 3 acceptance target)::

    from core.audit import AuditLog

    log = AuditLog(path, clock=None)           # JSONL, one record per line; clock injectable
    record = log.append(event: dict)           # -> dict with hash, prev_hash
    log.verify() -> bool                       # recompute the whole chain
    log.entries() -> iterator[dict]            # ordered replay of the log
"""

from __future__ import annotations

import re

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.safety]

GENESIS = "0" * 64
HEX64 = re.compile(r"[0-9a-f]{64}")
FORBIDDEN_METHODS = {"delete", "truncate", "remove", "pop", "clear", "rewrite", "reset", "purge"}


def _make_log(tmp_path, events=None, clock=None):
    from core.audit import AuditLog

    log = AuditLog(tmp_path / "audit.jsonl", clock=clock)
    for event in events or []:
        log.append(event)
    return log


def test_audit_module_exists() -> None:
    import core.audit  # noqa: F401


def test_first_entry_chains_to_genesis(tmp_path) -> None:
    record = _make_log(tmp_path).append({"event": "mission.open", "mission_id": "m-001"})
    assert record["prev_hash"] == GENESIS
    assert HEX64.fullmatch(record["hash"])


def test_entries_chain_via_sha256(tmp_path) -> None:
    log = _make_log(tmp_path)
    first = log.append({"event": "mission.open"})
    second = log.append({"event": "scope.decision", "target": "10.10.0.5"})
    assert second["prev_hash"] == first["hash"]
    assert second["hash"] != first["hash"]


def test_verify_accepts_intact_log(tmp_path) -> None:
    log = _make_log(
        tmp_path,
        events=[{"event": "a"}, {"event": "b"}, {"event": "c"}],
    )
    assert log.verify() is True


def test_verify_detects_tampering(tmp_path) -> None:
    from core.audit import AuditLog

    path = tmp_path / "audit.jsonl"
    log = AuditLog(path)
    log.append({"event": "mission.open"})
    log.append({"event": "tool.execution", "tool": "inventory"})

    # Tamper: rewrite an event in place (same byte length, different content).
    text = path.read_text(encoding="utf-8")
    tampered = text.replace("tool.execution", "tool.executed")
    assert tampered != text, "tamper fixture failed to modify the log"
    path.write_text(tampered, encoding="utf-8")

    assert AuditLog(path).verify() is False


def test_log_api_is_append_only(tmp_path) -> None:
    """No mutation-of-history API may exist on the log type."""
    from core.audit import AuditLog

    exposed = {name.lower() for name in dir(AuditLog) if not name.startswith("_")}
    offenders = sorted(exposed & FORBIDDEN_METHODS)
    assert not offenders, f"AuditLog exposes history-mutating API: {offenders}"


def test_append_preserves_prior_bytes(tmp_path) -> None:
    from core.audit import AuditLog

    path = tmp_path / "audit.jsonl"
    log = AuditLog(path)
    log.append({"event": "mission.open"})
    before = path.read_bytes()

    log.append({"event": "scope.decision"})

    after = path.read_bytes()
    assert after.startswith(before), "appending rewrote existing audit bytes"


def test_append_returns_record_with_event_data(tmp_path) -> None:
    record = _make_log(tmp_path).append({"event": "policy.decision", "allowed": False})
    assert record["event"] == "policy.decision"
    assert record["allowed"] is False
    assert "timestamp" in record or "recorded_at" in record


def test_entries_replays_the_log_in_order(tmp_path) -> None:
    events = [{"event": "mission.open"}, {"event": "policy.decision"}, {"event": "tool.execution"}]
    log = _make_log(tmp_path, events=events)
    replayed = list(log.entries())
    assert [entry["event"] for entry in replayed] == [event["event"] for event in events]


def test_injected_clock_is_respected(tmp_path, clock) -> None:
    """Timestamps must be deterministic when a clock is injected (conftest pattern)."""
    from core.audit import AuditLog

    log = AuditLog(tmp_path / "audit.jsonl", clock=clock)
    record = log.append({"event": "mission.open"})
    stamped = record.get("timestamp") or record.get("recorded_at")
    assert clock().isoformat() in str(stamped)
