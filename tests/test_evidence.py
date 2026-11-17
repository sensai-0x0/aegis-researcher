"""TDD spec for ``core/evidence.py`` — the content-addressed artifact store (red).

P01.W2 acceptance (curriculum): "Artifact hashes verify after storage and
retrieval" and "content-addressed artifact storage using SHA-256
identifiers". The conftest bundle fixes the construction shape::

    from core.evidence import ArtifactStore

    store = ArtifactStore(tmp_path / "evidence", clock=clock)
    artifact = store.store(data)
    store.retrieve(artifact.sha256)
    store.verify(artifact.sha256)

The ``Artifact`` record shape follows ``make_artifact`` in conftest:
``artifact_id == sha256`` (content address), ``storage_uri`` points into
``objects/raw/<prefix>/<digest>``, and provenance fields are carried.
"""

from __future__ import annotations

import hashlib

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.safety]


def _make_store(tmp_path, clock):
    from core.evidence import ArtifactStore

    return ArtifactStore(tmp_path / "evidence", clock=clock)


def test_store_returns_content_addressed_record(tmp_path, clock) -> None:
    store = _make_store(tmp_path, clock)
    data = b"raw evidence bytes"
    artifact = store.store(data)

    digest = hashlib.sha256(data).hexdigest()
    assert artifact.sha256 == digest
    assert artifact.artifact_id == digest, "artifact_id must be the content address"
    assert digest in artifact.storage_uri, "storage path must be content-addressed"


def test_retrieve_roundtrips_original_bytes(tmp_path, clock) -> None:
    store = _make_store(tmp_path, clock)
    data = b"\x00\x01\xff raw bytes with \n newlines"
    artifact = store.store(data)
    assert store.retrieve(artifact.sha256) == data


def test_identical_content_stores_to_one_address(tmp_path, clock) -> None:
    """Content addressing: same bytes, same digest — storage is deduplicated."""
    store = _make_store(tmp_path, clock)
    first = store.store(b"dedupe me")
    second = store.store(b"dedupe me")
    assert first.sha256 == second.sha256
    different = store.store(b"dedupe me!")
    assert different.sha256 != first.sha256


def test_verify_accepts_intact_artifact(tmp_path, clock) -> None:
    store = _make_store(tmp_path, clock)
    artifact = store.store(b"integrity matters")
    assert store.verify(artifact.sha256) is True


def test_verify_rejects_tampered_artifact(tmp_path, clock) -> None:
    """A mutated object on disk must fail verification — evidence is immutable."""
    import hashlib
    from pathlib import Path

    store = _make_store(tmp_path, clock)
    data = b"tamper target"
    artifact = store.store(data)
    digest = hashlib.sha256(data).hexdigest()

    object_path = Path(store.root) if hasattr(store, "root") else tmp_path / "evidence"
    matches = list(object_path.rglob(digest))
    assert matches, f"stored object not found under {object_path}"
    matches[0].write_bytes(b"tampered bytes!")  # corrupt the stored object

    assert store.verify(artifact.sha256) is False


def test_artifact_record_carries_provenance(tmp_path, clock) -> None:
    """make_artifact contract: created_at, integrity flag and media type are recorded."""
    store = _make_store(tmp_path, clock)
    artifact = store.store(b"provenance")
    assert artifact.created_at  # clock-driven timestamp
    assert artifact.integrity_verified is True
    assert artifact.media_type
