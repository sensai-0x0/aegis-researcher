"""Audit log — append-only, hash-chained, tamper-evident (P03.W8).

Curriculum criteria under test:
- "Execution audit records" and "audit_logging" competency.
- Plan §3.6: audit is "append-only, hash-chained (prev_hash, entry hash), no
  deletes; used by policy and orchestrator for every decision."
- graph_rules: "Never store secrets, credentials or private keys" — the audit
  log carries no secret fields.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from pydantic import ValidationError

GENESIS = "0" * 64


def _event(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "event_type": "policy.decision",
        "mission_id": "mission-local-lab-0001",
        "agent_run_id": "agent-run-local-lab-0001",
        "request_id": "request-local-lab-0001",
        "payload": {"decision": "allow"},
    }
    return {**payload, **overrides}


def test_append_returns_event_and_persists_in_order(audit_path, clock) -> None:
    from core.audit import AuditEvent, AuditLog

    audit = AuditLog(audit_path, clock=clock)
    first = audit.append(AuditEvent.model_validate(_event(request_id="r1")))
    second = audit.append(AuditEvent.model_validate(_event(request_id="r2")))
    assert first.request_id == "r1" and second.request_id == "r2"
    assert [event.request_id for event in audit.events()] == ["r1", "r2"]
    assert first.timestamp == clock()


def test_hash_chain_links_every_entry(audit_path, clock) -> None:
    from core.audit import AuditEvent, AuditLog

    audit = AuditLog(audit_path, clock=clock)
    audit.append(AuditEvent.model_validate(_event()))
    audit.append(AuditEvent.model_validate(_event()))
    audit.append(AuditEvent.model_validate(_event()))
    events = audit.events()
    assert events[0].prev_hash == GENESIS
    for previous, current in zip(events, events[1:]):
        assert current.prev_hash == previous.entry_hash
    assert all(event.entry_hash for event in events)
    assert audit.verify() is True


def test_log_survives_reload_and_continues_the_chain(audit_path, clock) -> None:
    """Append-only: a new process must see history and extend it, never reset it."""
    from core.audit import AuditEvent, AuditLog

    first = AuditLog(audit_path, clock=clock)
    first.append(AuditEvent.model_validate(_event(request_id="r1")))
    second = AuditLog(audit_path, clock=clock)
    assert [event.request_id for event in second.events()] == ["r1"]
    second.append(AuditEvent.model_validate(_event(request_id="r2")))
    reloaded = AuditLog(audit_path, clock=clock)
    assert [event.request_id for event in reloaded.events()] == ["r1", "r2"]
    assert reloaded.verify() is True


def test_verify_detects_a_modified_entry(audit_path, clock) -> None:
    from core.audit import AuditEvent, AuditLog

    audit = AuditLog(audit_path, clock=clock)
    audit.append(AuditEvent.model_validate(_event()))
    audit.append(AuditEvent.model_validate(_event()))
    lines = audit_path.read_text().splitlines()
    tampered = json.loads(lines[0])
    tampered["payload"]["decision"] = "deny"  # history rewrite
    lines[0] = json.dumps(tampered)
    audit_path.write_text("\n".join(lines) + "\n")
    assert AuditLog(audit_path, clock=clock).verify() is False


def test_verify_detects_a_deleted_entry(audit_path, clock) -> None:
    from core.audit import AuditEvent, AuditLog

    audit = AuditLog(audit_path, clock=clock)
    for index in range(3):
        audit.append(AuditEvent.model_validate(_event(request_id=f"r{index}")))
    lines = audit_path.read_text().splitlines()
    del lines[1]
    audit_path.write_text("\n".join(lines) + "\n")
    assert AuditLog(audit_path, clock=clock).verify() is False


def test_tool_execution_events_require_mission_and_run_attribution() -> None:
    """Every permitted tool execution is attributable to a mission and run."""
    from core.audit import AuditEvent

    with pytest.raises(ValidationError, match="mission_id"):
        AuditEvent.model_validate(
            _event(event_type="tool.execution", mission_id=None)
        )
    with pytest.raises(ValidationError, match="agent_run_id"):
        AuditEvent.model_validate(
            _event(event_type="tool.execution", agent_run_id=None)
        )
    # Policy decisions may concern malformed requests with no mission; only
    # executions carry the strict attribution requirement.
    AuditEvent.model_validate(_event(event_type="policy.decision", mission_id=None))


def test_event_type_is_required_and_nonempty() -> None:
    from core.audit import AuditEvent

    with pytest.raises(ValidationError):
        AuditEvent.model_validate(_event(event_type=""))


def test_audit_log_does_not_invite_secret_storage() -> None:
    """The audit record contract must not declare secret-bearing fields."""
    from core.audit import AuditEvent

    declared = set(AuditEvent.model_fields)
    forbidden = {"secret", "password", "credential", "api_key", "private_key", "token_value"}
    assert not (declared & forbidden), f"audit events must not declare secret fields: {declared & forbidden}"
