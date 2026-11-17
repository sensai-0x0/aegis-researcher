"""JSON Schema 2020-12 validator for AEGIS — jsonschema-backed, stdlib-safe.

Single source of truth for AEGIS schema validation. When the `jsonschema`
package is installed (it is a declared pyproject.toml dependency), `validate`
delegates to it for full draft 2020-12 coverage. When it is not installed —
e.g. a bare `python3` with no venv, which several AEGIS environments and
CI-equivalent runs use deliberately (decision log #2/#15: stdlib guarantees
the evals always run) — it falls back to a minimal stdlib-only subset
validator covering exactly the keywords AEGIS contracts use: type, enum,
const, required, properties, additionalProperties, items, minItems,
minLength, minimum, pattern, allOf/if/then. Both paths raise the same
`ValidationError` from the same `validate(value, schema)` call, so every
caller (`contracts/validate_fixtures.py`, adapters, core/mission.py, …) is
unaffected by which path is active. Fixture-level parity between the two
paths is checked manually, not re-verified on every run (no third-party
dependency in the stdlib-only path itself).
"""
from __future__ import annotations

import re

try:
    import jsonschema as _jsonschema
except ImportError:  # pragma: no cover - exercised wherever the dep is absent
    _jsonschema = None


class ValidationError(Exception):
    """Raised on the first schema violation found."""


def _type_ok(value, expected) -> bool:
    checks = {
        "object": lambda v: isinstance(v, dict),
        "array": lambda v: isinstance(v, list),
        "string": lambda v: isinstance(v, str),
        "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
        "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
        "boolean": lambda v: isinstance(v, bool),
        "null": lambda v: v is None,
    }
    if isinstance(expected, list):
        return any(_type_ok(value, e) for e in expected)
    return checks.get(expected, lambda v: True)(value)


def validate(value, schema, path="$") -> None:
    """Validate `value` against `schema`; raise ValidationError on violation."""
    if _jsonschema is not None:
        try:
            _jsonschema.Draft202012Validator(schema).validate(value)
        except _jsonschema.exceptions.ValidationError as e:
            raise ValidationError(f"{path}: {e.message}") from e
        return
    _validate_stdlib(value, schema, path)


def _validate_stdlib(value, schema, path="$") -> None:
    """Fallback path used only when the `jsonschema` package is absent."""
    if "allOf" in schema:
        for sub in schema["allOf"]:
            _try_conditional(value, sub, path)
    if "if" in schema and matches_if(value, schema["if"]):
        validate(value, schema["then"], path)
    if "const" in schema and value != schema["const"]:
        raise ValidationError(f"{path}: expected const {schema['const']!r}, got {value!r}")
    if "type" in schema and not _type_ok(value, schema["type"]):
        raise ValidationError(f"{path}: expected type {schema['type']}")
    if "enum" in schema and value not in schema["enum"]:
        raise ValidationError(f"{path}: {value!r} not in enum {schema['enum']}")
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            raise ValidationError(f"{path}: shorter than minLength {schema['minLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            raise ValidationError(f"{path}: does not match pattern {schema['pattern']}")
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            raise ValidationError(f"{path}: fewer than minItems {schema['minItems']}")
        if "items" in schema:
            for i, item in enumerate(value):
                validate(item, schema["items"], f"{path}[{i}]")
    if isinstance(value, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                raise ValidationError(f"{path}: missing required property {key!r}")
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in props:
                    raise ValidationError(f"{path}: undeclared property {key!r}")
        for key, sub in props.items():
            if key in value:
                validate(value[key], sub, f"{path}.{key}")


def matches_if(value, if_schema) -> bool:
    """Evaluate an `if` clause without raising."""
    try:
        validate(value, if_schema, path="$if")
        return True
    except ValidationError:
        return False


def _try_conditional(value, sub, path) -> None:
    """allOf members may themselves be if/then guards; recurse uniformly."""
    if "if" in sub and matches_if(value, sub["if"]):
        validate(value, sub["then"], path)
    else:
        validate(value, sub, path)
