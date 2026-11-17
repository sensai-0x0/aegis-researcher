"""Append-only run manifest — P01.W2 "Evidence vault and provenance".

Curriculum criteria under test:
- "Create an append-only run manifest and test artifact integrity verification."
- Plan §3.6: append-only records; history must be rewrite- and delete-proof.
"""

from __future__ import annotations

import json
from typing import Any

import pytest


def _record(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "agent_run_id": "agent-run-local-lab-0001",
        "mission_id": "mission-local-lab-0001",
        "outcome": "completed",
    }
    return {**payload, **overrides}


def test_append_returns_record_id_and_persists(tmp_path, clock) -> None:
    from core.evidence import RunManifest

    manifest = RunManifest(tmp_path / "manifests" / "runs.jsonl", clock=clock)
    record_id = manifest.append(_record(), record_id="agent-run-local-lab-0001")
    assert record_id == "agent-run-local-lab-0001"
    assert manifest.records() == [_record()]


def test_records_are_stored_as_json_lines(tmp_path, clock) -> None:
    from core.evidence import RunManifest

    path = tmp_path / "manifests" / "runs.jsonl"
    manifest = RunManifest(path, clock=clock)
    manifest.append(_record(), record_id="agent-run-local-lab-0001")
    lines = [json.loads(line) for line in path.read_text().splitlines() if line]
    assert len(lines) == 1
    assert lines[0]["payload"]["agent_run_id"] == "agent-run-local-lab-0001"


def test_manifest_survives_reload_without_truncation(tmp_path, clock) -> None:
    """Append-only across processes: reopening must never wipe history."""
    from core.evidence import RunManifest

    path = tmp_path / "manifests" / "runs.jsonl"
    RunManifest(path, clock=clock).append(_record(), record_id="run-1")
    RunManifest(path, clock=clock).append(
        _record(agent_run_id="agent-run-local-lab-0002"), record_id="run-2"
    )
    reloaded = RunManifest(path, clock=clock)
    assert [record["agent_run_id"] for record in reloaded.records()] == [
        "agent-run-local-lab-0001",
        "agent-run-local-lab-0002",
    ]


def test_duplicate_record_ids_are_rejected(tmp_path, clock) -> None:
    """Re-appending a record id would silently rewrite history; refuse it."""
    from core.evidence import DuplicateRecordError, RunManifest

    manifest = RunManifest(tmp_path / "manifests" / "runs.jsonl", clock=clock)
    manifest.append(_record(), record_id="run-1")
    with pytest.raises(DuplicateRecordError):
        manifest.append(_record(outcome="tampered"), record_id="run-1")
    assert len(manifest.records()) == 1


def test_verify_detects_a_modified_record(tmp_path, clock) -> None:
    from core.evidence import RunManifest

    path = tmp_path / "manifests" / "runs.jsonl"
    manifest = RunManifest(path, clock=clock)
    manifest.append(_record(), record_id="run-1")
    manifest.append(
        _record(agent_run_id="agent-run-local-lab-0002"), record_id="run-2"
    )
    lines = path.read_text().splitlines()
    tampered = json.loads(lines[0])
    tampered["payload"]["outcome"] = "rewritten"
    lines[0] = json.dumps(tampered)
    path.write_text("\n".join(lines) + "\n")
    assert RunManifest(path, clock=clock).verify() is False


def test_verify_detects_a_deleted_record(tmp_path, clock) -> None:
    from core.evidence import RunManifest

    path = tmp_path / "manifests" / "runs.jsonl"
    manifest = RunManifest(path, clock=clock)
    for index in range(3):
        manifest.append(_record(agent_run_id=f"agent-run-{index}"), record_id=f"run-{index}")
    lines = path.read_text().splitlines()
    del lines[1]
    path.write_text("\n".join(lines) + "\n")
    assert RunManifest(path, clock=clock).verify() is False


def test_untampered_manifest_verifies(tmp_path, clock) -> None:
    from core.evidence import RunManifest

    manifest = RunManifest(tmp_path / "manifests" / "runs.jsonl", clock=clock)
    manifest.append(_record(), record_id="run-1")
    assert manifest.verify() is True
