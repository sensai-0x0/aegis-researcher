"""Epistemic-discipline contract tests (complement to tests/unit/ conformance).

``tests/unit/test_contracts_conform_to_curriculum.py`` already covers schema
structure: parsing, dialect, closed objects, exact required-field equality
with the curriculum, lifecycle enums and sha256 formatting. This module
covers the *epistemic* semantics those structural checks cannot express:

- an observation is a recorded fact — it may not carry claim-like fields,
- an observation cannot exist without at least one preserved evidence
  reference (P01.W2: "Agent-generated interpretation is never substituted
  for raw output"),
- a finding cannot exist without an independent review reference
  (goal.md hard failure: "Any confirmed finding without supporting
  provenance").

Red until Phase 2 populates ``contracts/`` accordingly.
"""

from __future__ import annotations

import re
from typing import Any

import pytest

pytestmark = pytest.mark.contract

# Fields that encode agent *claims* rather than recorded *facts*.
CLAIM_LIKE_FIELDS = ("conclusion", "verdict", "confirmed_finding", "final_severity")


def _collect_property_names(node: Any) -> set[str]:
    names: set[str] = set()
    if isinstance(node, dict):
        props = node.get("properties")
        if isinstance(props, dict):
            for key, child in props.items():
                names.add(key)
                names |= _collect_property_names(child)
        for key in ("$defs", "definitions"):
            sub = node.get(key)
            if isinstance(sub, dict):
                for child in sub.values():
                    names |= _collect_property_names(child)
        if isinstance(node.get("items"), dict):
            names |= _collect_property_names(node["items"])
        for combo in ("anyOf", "oneOf", "allOf"):
            for child in node.get(combo) or []:
                names |= _collect_property_names(child)
    return names


def test_observation_forbids_claim_like_fields(schema_for) -> None:
    """Observations are facts only — no agent-conclusion fields anywhere."""
    props = _collect_property_names(schema_for("observation"))
    present = [field for field in CLAIM_LIKE_FIELDS if field in props]
    assert not present, f"observation schema contains claim-like fields: {present}"


def test_observation_requires_evidence_reference(schema_for) -> None:
    """An observation cannot be recorded without at least one evidence reference."""
    schema = schema_for("observation")
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
        assert prop.get("type") == "array", (
            f"evidence field '{key}' must reference artifacts as an array"
        )
        assert prop.get("minItems", 0) >= 1, f"evidence field '{key}' must have minItems >= 1"


def test_finding_requires_independent_review_link(schema_for) -> None:
    """A finding is a reviewed conclusion: the review reference is mandatory."""
    required = set(schema_for("finding").get("required", []))
    review_keys = [key for key in required if "review" in key]
    assert review_keys, "finding contract must require a review record reference"
