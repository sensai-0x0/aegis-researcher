"""Contract conformance tests (Phase 2 spec — currently red by design).

Every contract in ``contracts/`` must:
- parse as JSON,
- target JSON Schema Draft 2020-12,
- be closed (``additionalProperties: false``) — no undeclared fields,
- be self-consistent under jsonschema meta-validation,
- require *at least* the fields the curriculum's canonical record contract
  declares for that record type,
- encode the epistemic discipline: findings carry the full lifecycle,
  observations carry evidence references and no claim-like fields,
  artifacts are content-addressed with SHA-256.

Source of truth for field lists: ``.agents/curriculum.json`` ->
``canonical_record_contracts``. These tests fail (red) until Phase 2
populates the contract files.
"""

from __future__ import annotations

import re
from typing import Any

import jsonschema
import pytest

from tests.conftest import (
    CONTRACT_RECORDS,
    DRAFT_2020_12,
    collect_enums,
    collect_property_names,
)

pytestmark = pytest.mark.contract

# Fields that encode agent *claims* rather than recorded *facts*.
CLAIM_LIKE_FIELDS = ("conclusion", "verdict", "confirmed_finding", "final_severity")

HEX64 = "a" * 64


# --- Structural validity -----------------------------------------------------

@pytest.mark.parametrize("name", CONTRACT_RECORDS)
def test_contract_parses(load_contract: Any, name: str) -> None:
    schema = load_contract(name)
    assert isinstance(schema, dict) and schema, f"{name}.schema.json is empty"


@pytest.mark.parametrize("name", CONTRACT_RECORDS)
def test_contract_targets_draft_2020_12(load_contract: Any, name: str) -> None:
    assert load_contract(name).get("$schema") == DRAFT_2020_12


@pytest.mark.parametrize("name", CONTRACT_RECORDS)
def test_contract_is_closed(load_contract: Any, name: str) -> None:
    """No undeclared properties anywhere at the top level."""
    assert load_contract(name).get("additionalProperties") is False


@pytest.mark.parametrize("name", CONTRACT_RECORDS)
def test_contract_is_self_consistent(load_contract: Any, name: str) -> None:
    """The schema must be a valid Draft 2020-12 schema per meta-validation."""
    schema = load_contract(name)
    validator_cls = jsonschema.validators.validator_for(schema)
    assert validator_cls.meta_schema is not None, "unknown dialect"
    validator_cls.check_schema(schema)


# --- Curriculum cross-check ---------------------------------------------------

@pytest.mark.parametrize("name,record_type", CONTRACT_RECORDS.items())
def test_contract_requires_curriculum_fields(
    load_contract: Any, curriculum: dict[str, Any], name: str, record_type: str
) -> None:
    """Schema ``required`` ⊇ curriculum ``canonical_record_contracts[Type].required``."""
    declared = curriculum["canonical_record_contracts"][record_type]["required"]
    schema_required = set(load_contract(name).get("required", []))
    missing = sorted(set(declared) - schema_required)
    assert not missing, f"{record_type} contract does not require curriculum fields: {missing}"


def test_finding_lifecycle_covers_curriculum(
    load_contract: Any, curriculum: dict[str, Any]
) -> None:
    """The finding contract must enumerate the full epistemic lifecycle."""
    lifecycle = set(curriculum["research_data_contract"]["finding_lifecycle"])
    enums = set(collect_enums(load_contract("finding")))
    missing = sorted(lifecycle - enums)
    assert not missing, f"finding schema enum missing lifecycle states: {missing}"


# --- Epistemic discipline ------------------------------------------------------

def test_observation_forbids_claim_like_fields(load_contract: Any) -> None:
    """Observations are facts only — no agent-conclusion fields anywhere."""
    props = collect_property_names(load_contract("observation"))
    present = [field for field in CLAIM_LIKE_FIELDS if field in props]
    assert not present, f"observation schema contains claim-like fields: {present}"


def test_observation_requires_evidence_reference(load_contract: Any) -> None:
    """An observation cannot exist without at least one evidence reference."""
    schema = load_contract("observation")
    required = set(schema.get("required", []))
    evidence_keys = [
        key
        for key in required
        if re.fullmatch(r"(raw_)?evidence(_refs|_ids|_references)?", key)
    ]
    assert evidence_keys, "observation contract must require an evidence reference field"
    props = schema.get("properties", {})
    for key in evidence_keys:
        prop = props.get(key)
        assert isinstance(prop, dict), f"required evidence field '{key}' has no properties entry"
        assert prop.get("type") == "array", f"evidence field '{key}' must be an array of artifact refs"
        assert prop.get("minItems", 0) >= 1, f"evidence field '{key}' must have minItems >= 1"


def test_artifact_requires_well_formed_sha256(load_contract: Any) -> None:
    """Artifacts are content-addressed: sha256 is required and hex64-patterned."""
    schema = load_contract("artifact")
    assert "sha256" in schema.get("required", []), "artifact must require sha256"
    prop = schema.get("properties", {}).get("sha256", {})
    pattern = prop.get("pattern", "")
    assert pattern, "sha256 must carry a validation pattern"
    assert re.fullmatch(pattern, HEX64), f"sha256 pattern does not accept hex64: {pattern!r}"
    assert not re.fullmatch(pattern, "zz" * 32), "sha256 pattern must reject non-hex"


# --- Safety-relevant metadata ---------------------------------------------------

def test_finding_requires_independent_review_link(load_contract: Any) -> None:
    """A confirmed finding is impossible without a review record reference."""
    schema = load_contract("finding")
    required = set(schema.get("required", []))
    review_keys = [key for key in required if "review" in key]
    assert review_keys, "finding contract must require a review reference"


def test_mission_requires_scope_and_approval(load_contract: Any) -> None:
    """Missions cannot exist without authorization scope and approval state."""
    schema = load_contract("mission")
    required = set(schema.get("required", []))
    assert "scope_id" in required, "mission must bind to an authorized scope"
    assert "approval_state" in required, "mission must record its approval state"
    assert "excluded_actions" in required, "mission must record excluded actions"
