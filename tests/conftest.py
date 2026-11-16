"""Shared fixtures for the AEGIS test suite.

Two principles drive this suite:

1. **Contracts are the type system.** Every JSON Schema in ``contracts/`` is
   validated structurally (not by regex) and cross-checked against the
   canonical record contracts declared in ``.agents/curriculum.json``.
2. **Tests are the spec.** The core-module tests (scope, policy, audit,
   mission) are written test-first against a repository whose ``core/`` is
   still empty. They fail (red) until Phase 3 implements the API exactly as
   specified here — that is the TDD contract, not a bug.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

# Guarantee `import core.*` works regardless of how pytest is invoked.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# contract file stem -> canonical record type in curriculum.json
CONTRACT_RECORDS: dict[str, str] = {
    "mission": "Mission",
    "run": "AgentRun",
    "observation": "Observation",
    "finding": "Finding",
    "artifact": "Artifact",
}

DRAFT_2020_12 = "https://json-schema.org/draft/2020-12/schema"


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """Absolute path to the repository root."""
    return REPO_ROOT


@pytest.fixture(scope="session")
def curriculum(repo_root: Path) -> dict[str, Any]:
    """Parsed agent curriculum — the source of record contracts and gates."""
    path = repo_root / ".agents" / "curriculum.json"
    assert path.is_file(), "curriculum.json missing — contract source of truth gone"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data.get("document_type") == "agent_curriculum_and_project_specification"
    return data


@pytest.fixture(scope="session")
def load_contract(
    repo_root: Path,
) -> Callable[[str], dict[str, Any]]:
    """Load a contract schema by stem; fail the test with a precise message."""
    cache: dict[str, dict[str, Any]] = {}

    def _load(name: str) -> dict[str, Any]:
        if name not in cache:
            rel = f"contracts/{name}.schema.json"
            path = repo_root / rel
            assert path.is_file(), f"contract missing: {rel}"
            try:
                cache[name] = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                pytest.fail(f"{rel} is not valid JSON: {exc}")
        return cache[name]

    return _load


def collect_enums(node: Any) -> list[str]:
    """Recursively collect every ``enum`` value reachable from a schema node."""
    found: list[str] = []
    if not isinstance(node, dict):
        return found
    enum = node.get("enum")
    if isinstance(enum, list):
        found.extend(str(v) for v in enum)
    for key in ("properties", "$defs", "definitions"):
        sub = node.get(key)
        if isinstance(sub, dict):
            for child in sub.values():
                found.extend(collect_enums(child))
    if isinstance(node.get("items"), dict):
        found.extend(collect_enums(node["items"]))
    for combo in ("anyOf", "oneOf", "allOf"):
        for child in node.get(combo) or []:
            found.extend(collect_enums(child))
    return found


def collect_property_names(node: Any, prefix: str = "") -> set[str]:
    """Recursively collect every property name declared in a schema."""
    names: set[str] = set()
    if not isinstance(node, dict):
        return names
    props = node.get("properties")
    if isinstance(props, dict):
        for key, child in props.items():
            names.add(key)
            names |= collect_property_names(child, f"{prefix}{key}.")
    for key in ("$defs", "definitions"):
        sub = node.get(key)
        if isinstance(sub, dict):
            for child in sub.values():
                names |= collect_property_names(child, prefix)
    if isinstance(node.get("items"), dict):
        names |= collect_property_names(node["items"], prefix)
    for combo in ("anyOf", "oneOf", "allOf"):
        for child in node.get(combo) or []:
            names |= collect_property_names(child, prefix)
    return names
