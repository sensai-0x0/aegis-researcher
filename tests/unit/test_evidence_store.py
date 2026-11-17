"""Evidence vault: content-addressed artifact store — P01.W2.

Curriculum criteria under test (phase exit criteria):
- "Artifact hashes verify after storage and retrieval."
- "Agent-generated interpretation is never substituted for raw output."
  (raw/derived separation)
- evidence_contract: SHA-256 content hashing, required provenance metadata,
  "Preserve raw and transformed artifacts separately."
"""

from __future__ import annotations

import hashlib
from typing import Any

import pytest
from pydantic import ValidationError

EVIDENCE_BYTES = b"raw evidence bytes"


def _put(store, data: bytes = EVIDENCE_BYTES, **overrides: Any):
    kwargs: dict[str, Any] = {
        "media_type": "text/plain",
        "source_tool_or_agent": "evidence_curator",
        "mission_id": "mission-local-lab-0001",
        "agent_run_id": "agent-run-local-lab-0001",
    }
    kwargs.update(overrides)
    return store.put(data, **kwargs)


# ---------------------------------------------------------------------------
# Content addressing
# ---------------------------------------------------------------------------


def test_put_returns_content_addressed_artifact(tmp_path, clock) -> None:
    from core.evidence import ArtifactStore

    store = ArtifactStore(tmp_path / "evidence", clock=clock)
    artifact = _put(store)
    digest = hashlib.sha256(EVIDENCE_BYTES).hexdigest()
    assert artifact.artifact_id == digest
    assert artifact.sha256 == digest
    assert artifact.byte_length == len(EVIDENCE_BYTES)
    assert digest in artifact.storage_uri
    assert artifact.created_at == clock()


def test_object_bytes_are_stored_in_a_content_addressed_path(tmp_path, clock) -> None:
    from core.evidence import ArtifactStore

    store = ArtifactStore(tmp_path / "evidence", clock=clock)
    artifact = _put(store)
    digest = artifact.sha256
    assert (tmp_path / "evidence" / "objects" / "raw" / digest[:2] / digest).is_file()


def test_get_round_trips_the_exact_bytes(tmp_path, clock) -> None:
    from core.evidence import ArtifactStore

    store = ArtifactStore(tmp_path / "evidence", clock=clock)
    artifact = _put(store)
    assert store.get(artifact.artifact_id) == EVIDENCE_BYTES


def test_identical_bytes_deduplicate_to_one_object(tmp_path, clock) -> None:
    from core.evidence import ArtifactStore

    store = ArtifactStore(tmp_path / "evidence", clock=clock)
    first = _put(store)
    second = _put(store, agent_run_id="agent-run-local-lab-0002")
    assert first.artifact_id == second.artifact_id
    objects = list((tmp_path / "evidence" / "objects" / "raw").rglob("*"))
    assert len([path for path in objects if path.is_file()]) == 1


def test_unknown_artifact_id_raises(tmp_path, clock) -> None:
    from core.evidence import ArtifactNotFoundError, ArtifactStore

    store = ArtifactStore(tmp_path / "evidence", clock=clock)
    with pytest.raises(ArtifactNotFoundError):
        store.get("b" * 64)


# ---------------------------------------------------------------------------
# Integrity verification
# ---------------------------------------------------------------------------


def test_verify_passes_after_storage_and_retrieval(tmp_path, clock) -> None:
    """Artifact hashes verify after storage and retrieval."""
    from core.evidence import ArtifactStore

    store = ArtifactStore(tmp_path / "evidence", clock=clock)
    artifact = _put(store)
    assert artifact.integrity_verified is True
    assert store.verify(artifact.artifact_id) is True
    store.get(artifact.artifact_id)  # retrieval must not corrupt anything
    assert store.verify(artifact.artifact_id) is True


def test_get_detects_tampered_objects(tmp_path, clock) -> None:
    """Retrieval re-verifies content; a corrupted object must never be returned."""
    from core.evidence import ArtifactStore, IntegrityError

    store = ArtifactStore(tmp_path / "evidence", clock=clock)
    artifact = _put(store)
    object_path = tmp_path / "evidence" / "objects" / "raw" / artifact.sha256[:2] / artifact.sha256
    object_path.write_bytes(b"tampered!")

    assert store.verify(artifact.artifact_id) is False
    with pytest.raises(IntegrityError):
        store.get(artifact.artifact_id)


def test_verify_all_reports_only_tampered_objects(tmp_path, clock) -> None:
    from core.evidence import ArtifactStore

    store = ArtifactStore(tmp_path / "evidence", clock=clock)
    keep = _put(store, data=b"keep me")
    drop = _put(store, data=b"tamper me", agent_run_id="agent-run-local-lab-0002")
    drop_path = (
        tmp_path / "evidence" / "objects" / "raw" / drop.sha256[:2] / drop.sha256
    )
    drop_path.write_bytes(b"corrupted")
    failing = store.verify_all()
    assert (drop.artifact_id, "raw") in failing
    assert (keep.artifact_id, "raw") not in failing


# ---------------------------------------------------------------------------
# Provenance metadata is mandatory
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "field",
    ["media_type", "source_tool_or_agent", "mission_id", "agent_run_id"],
)
def test_put_requires_provenance_metadata(tmp_path, clock, field: str) -> None:
    """evidence_contract.minimum_run_metadata: provenance is not optional."""
    from core.evidence import ArtifactStore

    store = ArtifactStore(tmp_path / "evidence", clock=clock)
    with pytest.raises(ValidationError, match=field):
        _put(store, **{field: ""})


def test_artifact_record_carries_required_provenance_fields(tmp_path, clock) -> None:
    from core.evidence import ArtifactStore

    store = ArtifactStore(tmp_path / "evidence", clock=clock)
    artifact = _put(store)
    assert artifact.mission_id == "mission-local-lab-0001"
    assert artifact.agent_run_id == "agent-run-local-lab-0001"
    assert artifact.source_tool_or_agent == "evidence_curator"
    assert artifact.integrity_verified is True


def test_artifact_registry_lists_all_stored_artifacts(tmp_path, clock) -> None:
    from core.evidence import ArtifactStore

    store = ArtifactStore(tmp_path / "evidence", clock=clock)
    first = _put(store, data=b"first")
    second = _put(store, data=b"second", agent_run_id="agent-run-local-lab-0002")
    listed = {artifact.artifact_id for artifact in store.artifacts()}
    assert listed == {first.artifact_id, second.artifact_id}


# ---------------------------------------------------------------------------
# Raw and derived separation
# ---------------------------------------------------------------------------


def test_raw_and_derived_artifacts_are_preserved_separately(tmp_path, clock) -> None:
    """Same bytes may legitimately exist as raw input and derived analysis."""
    from core.evidence import ArtifactStore

    store = ArtifactStore(tmp_path / "evidence", clock=clock)
    raw = _put(store, kind="raw")
    derived = _put(store, kind="derived", source_tool_or_agent="static_analysis_worker")
    assert raw.artifact_id == derived.artifact_id  # same content address
    assert raw is not derived  # but distinct custody records
    assert store.get(raw.artifact_id, kind="raw") == EVIDENCE_BYTES
    assert store.get(derived.artifact_id, kind="derived") == EVIDENCE_BYTES
    kinds = {(artifact.artifact_id, artifact.kind) for artifact in store.artifacts()}
    assert (raw.artifact_id, "raw") in kinds
    assert (derived.artifact_id, "derived") in kinds
    assert (tmp_path / "evidence" / "objects" / "raw" / raw.sha256[:2] / raw.sha256).is_file()
    assert (
        tmp_path / "evidence" / "objects" / "derived" / derived.sha256[:2] / derived.sha256
    ).is_file()


def test_kind_defaults_to_raw(tmp_path, clock) -> None:
    from core.evidence import ArtifactStore

    store = ArtifactStore(tmp_path / "evidence", clock=clock)
    artifact = _put(store)
    assert artifact.kind == "raw"


def test_unknown_kind_is_rejected(tmp_path, clock) -> None:
    from core.evidence import ArtifactStore

    store = ArtifactStore(tmp_path / "evidence", clock=clock)
    with pytest.raises(ValidationError, match="kind"):
        _put(store, kind="quarantine")
