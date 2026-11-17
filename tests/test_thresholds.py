"""Guardrails for the threshold/ratchet configuration itself."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.evals

REPO_ROOT = Path(__file__).resolve().parents[1]
THRESHOLDS_PATH = Path(__file__).parent / "thresholds.json"
HEURISTICS_PATH = REPO_ROOT / ".agents" / "evals" / "eval-suite" / "heuristics.json"
RATCHET_SCRIPT = REPO_ROOT / "tools" / "ci" / "check_ratchet.py"


@pytest.fixture(scope="module")
def thresholds() -> dict:
    return json.loads(THRESHOLDS_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def heuristics() -> dict:
    return json.loads(HEURISTICS_PATH.read_text(encoding="utf-8"))


def test_thresholds_parse(thresholds) -> None:
    assert isinstance(thresholds, dict)
    assert isinstance(thresholds.get("version"), int)


def test_coverage_floor_is_a_sane_percent(thresholds) -> None:
    floor = thresholds["coverage"]["min_line_percent"]
    assert isinstance(floor, (int, float))
    assert 0 <= floor <= 100


def test_eval_rate_floor_is_a_sane_fraction(thresholds) -> None:
    floor = thresholds["evals"]["min_overall_rate"]
    assert isinstance(floor, (int, float))
    assert 0 <= floor <= 1


def test_eval_floor_never_exceeds_zero_tolerance_suite_gates(thresholds, heuristics) -> None:
    """A suite gated at 1.0 implies the overall floor cannot exceed it."""
    overall_floor = thresholds["evals"]["min_overall_rate"]
    for suite in heuristics["suites"].values():
        assert overall_floor <= suite["gate"], "evals.min_overall_rate exceeds a suite gate"


def test_ratchet_script_exists() -> None:
    assert RATCHET_SCRIPT.is_file(), "tools/ci/check_ratchet.py missing — ratchet unenforceable"


def test_ratchet_script_tracks_both_gate_files() -> None:
    source = RATCHET_SCRIPT.read_text(encoding="utf-8")
    assert "tests/thresholds.json" in source
    assert ".agents/evals/eval-suite/heuristics.json" in source
