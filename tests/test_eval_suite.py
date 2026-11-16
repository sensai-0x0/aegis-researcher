"""Eval-harness integrity tests (green today — guard the eval machinery).

The ``.agents/evals/eval-suite`` runner is the repo's behavioral eval layer.
These pytest tests guard its *machinery* (registry/runner sync, gate
sanity, scan exclusions) so drift between heuristics.json and run_evals.py
fails fast in CI rather than silently weakening the gates.

The heuristics themselves run as a separate CI job (``evals``) so that eval
results keep their own audit trail in ``.agents/evals/results/``.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

pytestmark = pytest.mark.evals

EVAL_SUITE_DIR = Path(__file__).resolve().parents[1] / ".agents" / "evals" / "eval-suite"
REGISTRY_PATH = EVAL_SUITE_DIR / "heuristics.json"
RUNNER_PATH = EVAL_SUITE_DIR / "run_evals.py"


@pytest.fixture(scope="module")
def registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def runner() -> ModuleType:
    spec = importlib.util.spec_from_file_location("aegis_run_evals", RUNNER_PATH)
    assert spec is not None and spec.loader is not None, "cannot load run_evals.py"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_registry_and_runner_are_in_sync(registry, runner) -> None:
    """Every registered heuristic must have an implementation — and vice versa."""
    registered = {h["id"] for h in registry["heuristics"]}
    implemented = set(runner.CHECKS)
    assert registered == implemented, (
        f"registry/runner drift — missing impl: {sorted(registered - implemented)}, "
        f"unregistered: {sorted(implemented - registered)}"
    )


def test_every_capability_has_a_suite_with_gate(registry) -> None:
    capabilities = {h["capability"] for h in registry["heuristics"]}
    assert capabilities <= set(registry["suites"]), "heuristic references unknown suite"


def test_zero_tolerance_suites_gate_at_100_percent(registry) -> None:
    """Safety, contracts, process and harness have zero tolerance (goal.md hard failures)."""
    for capability in ("safety", "contracts", "process", "harness"):
        gate = registry["suites"][capability]["gate"]
        assert gate == 1.0, f"{capability} gate must be 1.0 (got {gate})"


def test_all_gates_are_valid_fractions(registry) -> None:
    for capability, suite in registry["suites"].items():
        assert 0.0 <= suite["gate"] <= 1.0, f"{capability} gate out of range: {suite['gate']}"


def test_every_heuristic_has_id_capability_description(registry) -> None:
    for heuristic in registry["heuristics"]:
        for key in ("id", "capability", "description"):
            assert heuristic.get(key), f"heuristic missing '{key}': {heuristic}"


def test_secret_scan_skips_non_target_paths(runner) -> None:
    """The secret/IP scanner must not scan its own machinery, results or caches."""
    for skip in (".git", ".venv", "__pycache__", "results"):
        assert skip in runner.SCAN_SKIP, f"SCAN_SKIP missing '{skip}'"


def test_secret_patterns_exist(runner) -> None:
    """The scanner must actually look for credential-shaped strings."""
    assert len(runner.SECRET_PATTERNS) >= 3


def test_eval_registry_is_versioned(registry) -> None:
    assert isinstance(registry.get("version"), int)
    assert registry["version"] >= 1
