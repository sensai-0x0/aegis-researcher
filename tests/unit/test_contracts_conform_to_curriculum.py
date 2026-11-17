"""Contract-level tests: the JSON Schemas in ``contracts/`` must implement the
canonical record contracts defined in ``.agents/curriculum.json``.

The curriculum is the source of truth (``canonical_record_contracts``); these
tests fail if a schema drifts from it. Covered phases:

- P01.W2 — artifact manifest schema and integrity metadata
- P02.W3 — "Define versioned Pydantic models and JSON Schema contracts"
- P03.W9 — "Define versioned JSON contracts for missions, tool requests,
  runs, observations and findings"
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

CURRICULUM = json.loads(
    (Path(__file__).resolve().parents[2] / ".agents" / "curriculum.json").read_text()
)

# schema short name in contracts/ -> canonical record contract key in the curriculum
SCHEMA_TO_CONTRACT = {
    "mission": "Mission",
    "run": "AgentRun",
    "observation": "Observation",
    "artifact": "Artifact",
    "finding": "Finding",
    "tool_request": "ToolRequest",
}

# curriculum evidence_contract.minimum_run_metadata -> schema field(s) that carry it
RUN_METADATA_MAPPING: dict[str, tuple[str, ...]] = {
    "mission_id": ("mission_id",),
    "scope_id": ("scope_id",),
    "agent_run_id": ("agent_run_id",),
    "agent_role": ("agent_role",),
    "harness_name_and_version": ("harness_name", "harness_version"),
    "model_id": ("model_id",),
    "effort_level": ("effort_level",),
    "prompt_or_configuration_hash": ("prompt_config_hash",),
    "tool_names_and_versions": ("tool_versions",),
    "target_snapshot_or_hash": ("target_snapshot_hash",),
    "start_and_end_time": ("start_time", "end_time"),
    "exit_status": ("outcome", "exit_status"),
    "artifact_ids": ("artifact_ids",),
}

# Fields an agent must never be able to set to influence the policy outcome.
SELF_AUTHORIZATION_FIELDS = {
    "decision",
    "policy_decision",
    "policy_outcome",
    "allow",
    "granted",
    "authorized",
}


def contract_required(schema_name: str) -> set[str]:
    key = SCHEMA_TO_CONTRACT[schema_name]
    return set(CURRICULUM["canonical_record_contracts"][key]["required"])


# ---------------------------------------------------------------------------
# Schema file structure
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("schema_name", sorted(SCHEMA_TO_CONTRACT))
def test_schema_file_exists_and_parses(schema_name: str) -> None:
    path = Path(__file__).resolve().parents[2] / "contracts" / f"{schema_name}.schema.json"
    assert path.is_file(), f"missing contract file: {path}"
    parsed = json.loads(path.read_text())
    assert isinstance(parsed, dict) and parsed, f"{path} is not a JSON object"


@pytest.mark.parametrize("schema_name", sorted(SCHEMA_TO_CONTRACT))
def test_schema_uses_draft_2020_12_and_aegis_id(schema_name: str, schema_for) -> None:
    schema = schema_for(schema_name)
    assert schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema"
    assert "aegis.local/schemas" in schema.get("$id", ""), (
        "$id must live under the aegis.local/schemas namespace"
    )


@pytest.mark.parametrize("schema_name", sorted(SCHEMA_TO_CONTRACT))
def test_schema_is_valid_draft_2020_12(schema_name: str, schema_for) -> None:
    Draft202012Validator.check_schema(schema_for(schema_name))


@pytest.mark.parametrize("schema_name", sorted(SCHEMA_TO_CONTRACT))
def test_required_fields_match_curriculum_contract(schema_name: str, schema_for) -> None:
    """The schema's required list must equal the curriculum's required list."""
    schema = schema_for(schema_name)
    schema_required = set(schema.get("required", []))
    expected = contract_required(schema_name)
    assert schema_required == expected, (
        f"{schema_name}: schema required - curriculum = {sorted(schema_required - expected)}; "
        f"curriculum - schema = {sorted(expected - schema_required)}"
    )


@pytest.mark.parametrize("schema_name", sorted(SCHEMA_TO_CONTRACT))
def test_schema_disallows_undeclared_properties(schema_name: str, schema_for) -> None:
    """Closed contracts prevent agents from smuggling extra authority fields."""
    assert schema_for(schema_name).get("additionalProperties") is False


# ---------------------------------------------------------------------------
# Semantics the platform depends on
# ---------------------------------------------------------------------------


def test_finding_lifecycle_matches_curriculum(schema_for, curriculum) -> None:
    """The finding verification_state enum must track the full curriculum lifecycle."""
    lifecycle = curriculum["research_data_contract"]["finding_lifecycle"]
    enum = schema_for("finding")["properties"]["verification_state"]["enum"]
    assert sorted(enum) == sorted(lifecycle)


def test_run_schema_covers_curriculum_minimum_run_metadata(schema_for, curriculum) -> None:
    """Every field the evidence contract calls mandatory must be required in run.schema."""
    required = set(schema_for("run").get("required", []))
    properties = set(schema_for("run").get("properties", {}))
    for metadata_item, carrying_fields in RUN_METADATA_MAPPING.items():
        assert metadata_item in curriculum["evidence_contract"]["minimum_run_metadata"]
        assert any(field in required and field in properties for field in carrying_fields), (
            f"run.schema.json must require one of {carrying_fields} "
            f"for minimum_run_metadata item {metadata_item!r}"
        )


def test_tool_request_schema_has_no_self_authorization_fields(schema_for) -> None:
    """Agents propose; the policy engine decides. No field may carry a decision."""
    properties = set(schema_for("tool_request").get("properties", {}))
    overlap = properties & SELF_AUTHORIZATION_FIELDS
    assert not overlap, f"tool_request schema must not declare authority fields: {overlap}"


def test_artifact_schema_constrains_sha256_format(schema_for) -> None:
    sha256_property = schema_for("artifact")["properties"]["sha256"]
    pattern = sha256_property.get("pattern")
    assert pattern, "artifact schema must pin the sha256 format"
    digest = "a" * 64
    assert re.fullmatch(pattern, digest), f"pattern {pattern!r} rejects a valid sha256"
    assert not re.fullmatch(pattern, digest.upper()), "pattern must require lowercase hex"
    assert not re.fullmatch(pattern, digest[:63]), "pattern must require exactly 64 hex chars"


def test_curriculum_contracts_referenced_by_tests_exist_in_curriculum() -> None:
    contracts = CURRICULUM["canonical_record_contracts"]
    missing = set(SCHEMA_TO_CONTRACT.values()) - set(contracts)
    assert not missing, f"tests reference contracts missing from the curriculum: {missing}"
