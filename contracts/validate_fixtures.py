#!/usr/bin/env python3
"""AEGIS contract self-validation (stdlib-only).

Validates every fixture in contracts/fixtures/ against its schema using the
shared minimal validator in core/jsonschema_lite.py (single source of truth).

Usage:
    python3 contracts/validate_fixtures.py          # validates all fixtures
    python3 contracts/validate_fixtures.py --negative   # expects negative fixtures to FAIL

Exit 0 when all expectations hold, 1 otherwise.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.jsonschema_lite import ValidationError, validate  # noqa: E402

HERE = Path(__file__).resolve().parent



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
