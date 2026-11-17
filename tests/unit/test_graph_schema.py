"""Initial Memgraph schema — P01.W2 "Represent missions, runs and artifacts in
an initial Memgraph schema".

Curriculum criteria under test:
- research_data_contract.node_types / relationship_types are the vocabulary.
- graph_rules: "Never store secrets, credentials or private keys in Memgraph."
- Plan §3.9: uniqueness constraints on ids and sha256.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "graph" / "schema.cypher"

# Node labels required by the first phases (P01.W2 missions/runs/artifacts,
# P02/P03 observations). Hypothesis/Finding labels arrive with P04 and are
# deliberately not required yet.
REQUIRED_LABELS = ["Mission", "AgentRun", "Artifact", "Observation", "Scope"]

# Relationship types the early phases actually create.
REQUIRED_RELATIONSHIPS = ["AUTHORIZED_BY", "PRODUCES", "OBSERVES", "DERIVED_FROM"]


@pytest.fixture(scope="module")
def schema_text() -> str:
    assert SCHEMA_PATH.is_file(), "graph/schema.cypher is missing"
    return SCHEMA_PATH.read_text()


@pytest.mark.parametrize("label", REQUIRED_LABELS)
def test_required_node_labels_are_declared(schema_text: str, label: str) -> None:
    assert re.search(rf":\s*{label}\b", schema_text), f"missing node label :{label}"


@pytest.mark.parametrize("relationship", REQUIRED_RELATIONSHIPS)
def test_required_relationship_types_are_declared(
    schema_text: str, relationship: str
) -> None:
    assert re.search(rf"\b{relationship}\b", schema_text), (
        f"missing relationship type {relationship}"
    )


def test_uniqueness_constraints_cover_ids_and_content_hashes(schema_text: str) -> None:
    assert "CREATE CONSTRAINT" in schema_text
    assert "IS UNIQUE" in schema_text
    for identifier in ("mission_id", "agent_run_id", "sha256"):
        assert identifier in schema_text, f"schema must constrain {identifier}"


def test_schema_declares_no_secret_bearing_properties(schema_text: str) -> None:
    """graph_rules: never store secrets, credentials or private keys."""
    leaked = re.search(
        r"(?i)\b(password|secret|credentials|api[_-]?key|private[_-]?key)\b",
        schema_text,
    )
    assert leaked is None, f"schema must not reference secret-like properties: {leaked!r}"


def test_schema_carries_provenance_properties(schema_text: str) -> None:
    """required_provenance_fields must exist as node properties."""
    for field in ("record_id", "created_at", "schema_version", "mission_id"):
        assert field in schema_text, f"missing provenance property {field}"
