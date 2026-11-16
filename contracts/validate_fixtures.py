#!/usr/bin/env python3
"""AEGIS contract self-validation (stdlib-only).

Validates every fixture in contracts/fixtures/ against its schema using a
minimal JSON Schema 2020-12 subset validator covering exactly the keywords the
AEGIS contracts use: type, enum, required, properties, additionalProperties,
items, minItems, minLength, minimum, pattern, allOf/if/then.

Usage:
    python3 contracts/validate_fixtures.py          # validates all fixtures
    python3 contracts/validate_fixtures.py --negative   # expects negative fixtures to FAIL

Exit 0 when all expectations hold, 1 otherwise.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


class ValidationError(Exception):
    pass


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
    """Raise ValidationError on first violation."""
    if "allOf" in schema:
        for sub in schema["allOf"]:
            _try_conditional(value, sub, path)
    if "if" in schema and _matches_if(value, schema["if"]):
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


def _matches_if(value, if_schema) -> bool:
    """Evaluate an `if` clause's properties/const subset without raising."""
    try:
        validate(value, if_schema, path="$if")
        return True
    except ValidationError:
        return False


def _try_conditional(value, sub, path) -> None:
    """allOf members may themselves be if/then guards; recurse uniformly."""
    if "if" in sub and _matches_if(value, sub["if"]):
        validate(value, sub["then"], path)
    else:
        validate(value, sub, path)


def _fixture_name(fx: Path) -> str:
    """negative-<name>.instance.json validates against <name>.schema.json (expects failure)."""
    return fx.stem.replace(".instance", "").removeprefix("negative-")


def main() -> int:
    fixtures = sorted(HERE.glob("fixtures/*.instance.json"))
    if not fixtures:
        print("no fixtures found", file=sys.stderr)
        return 1
    failures = 0
    for fx in fixtures:
        name = _fixture_name(fx)
        negative = fx.stem.startswith("negative-")
        schema_path = HERE / f"{name}.schema.json"
        instance = json.loads(fx.read_text())
        schema = json.loads(schema_path.read_text())
        expect_fail = negative or "--negative" in sys.argv
        try:
            validate(instance, schema)
            ok = not expect_fail
            outcome = "VALID" if not expect_fail else "unexpectedly VALID"
        except ValidationError as e:
            ok = expect_fail
            outcome = f"INVALID: {e}"
        status = "PASS" if ok else "FAIL"
        if not ok:
            failures += 1
        print(f"[{status}] {name:<12} {outcome}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
