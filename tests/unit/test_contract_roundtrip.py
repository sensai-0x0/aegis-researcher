"""Pydantic models must mirror the JSON Schema contracts exactly.

P02.W3 acceptance: "Define versioned Pydantic models and JSON Schema contracts."
Every record model must (a) accept the canonical payload, (b) serialize to a
JSON document that validates against its schema, and (c) reject payloads that
violate the schema's required-field contract.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

CURRICULUM = json.loads(
    (Path(__file__).resolve().parents[2] / ".agents" / "curriculum.json").read_text()
)

# schema short name -> fixture providing the canonical payload builder
PAYLOAD_BUILDERS = {
    "mission": "make_mission",
    "tool_request": "make_tool_request",
    "run": "make_run_record",
    "observation": "make_observation",
    "artifact": "make_artifact",
}

MODEL_IMPORTS = {
    "mission": ("core.mission", "Mission"),
    "tool_request": ("core.policy", "ToolRequest"),
    "run": ("core.orchestrator", "AgentRun"),
    "observation": ("core.orchestrator", "Observation"),
    "artifact": ("core.evidence", "Artifact"),
}


def _model_for(schema_name: str) -> type:
    module_name, class_name = MODEL_IMPORTS[schema_name]
    import importlib

    return getattr(importlib.import_module(module_name), class_name)


@pytest.mark.parametrize("schema_name", sorted(PAYLOAD_BUILDERS))
def test_model_serialization_validates_against_contract(
    schema_name: str, request: pytest.FixtureRequest, assert_schema_valid
) -> None:
    builder = request.getfixturevalue(PAYLOAD_BUILDERS[schema_name])
    model = _model_for(schema_name)
    instance = model.model_validate(builder()).model_dump(mode="json")
    assert_schema_valid(schema_name, instance)


@pytest.mark.parametrize("schema_name", sorted(PAYLOAD_BUILDERS))
def test_model_rejects_missing_required_fields(
    schema_name: str, request: pytest.FixtureRequest, schema_for
) -> None:
    from pydantic import ValidationError

    builder = request.getfixturevalue(PAYLOAD_BUILDERS[schema_name])
    contract_key = {
        "mission": "Mission",
        "tool_request": "ToolRequest",
        "run": "AgentRun",
        "observation": "Observation",
        "artifact": "Artifact",
    }[schema_name]
    required = CURRICULUM["canonical_record_contracts"][contract_key]["required"]

    for field in required:
        broken = {key: value for key, value in builder().items() if key != field}
        with pytest.raises(ValidationError, match=field):
            _model_for(schema_name).model_validate(broken)


@pytest.mark.parametrize("schema_name", sorted(PAYLOAD_BUILDERS))
def test_schema_rejects_instances_missing_required_fields(
    schema_name: str, request: pytest.FixtureRequest, schema_for
) -> None:
    """The schema itself (not only the model) must catch missing required fields."""
    builder = request.getfixturevalue(PAYLOAD_BUILDERS[schema_name])
    model = _model_for(schema_name)
    instance = model.model_validate(builder()).model_dump(mode="json")
    contract_key = {
        "mission": "Mission",
        "tool_request": "ToolRequest",
        "run": "AgentRun",
        "observation": "Observation",
        "artifact": "Artifact",
    }[schema_name]
    first_required = CURRICULUM["canonical_record_contracts"][contract_key]["required"][0]
    broken = {key: value for key, value in instance.items() if key != first_required}
    errors = list(Draft202012Validator(schema_for(schema_name)).iter_errors(broken))
    assert errors, f"{schema_name}: schema accepted an instance missing {first_required!r}"


@pytest.mark.parametrize("schema_name", sorted(PAYLOAD_BUILDERS))
def test_model_rejects_undeclared_fields(
    schema_name: str, request: pytest.FixtureRequest
) -> None:
    """Schemas are closed; models must be too, so agents cannot smuggle fields."""
    from pydantic import ValidationError

    builder = request.getfixturevalue(PAYLOAD_BUILDERS[schema_name])
    smuggled = {**builder(), "policy_decision": "allow"}
    with pytest.raises(ValidationError):
        _model_for(schema_name).model_validate(smuggled)
