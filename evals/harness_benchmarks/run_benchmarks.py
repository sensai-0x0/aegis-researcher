#!/usr/bin/env python3
"""AEGIS harness benchmark runner (stdlib-only).

Wires `benchmarks.yaml` definitions to real runner output. A benchmark is
only reported if there is an actual measurement behind it — unwired
benchmarks are recorded as "not_wired" rather than faked as 0 or skipped
silently (research.md MUST NOT 4: never report activity metrics as results;
the corollary here is never report an absent measurement as a result either).

Currently wired (this iteration):
  - bench-evidence-chain-completeness  (from evals/e2e_smoke.py)
  - bench-deny-by-default-behavior     (from evals/e2e_smoke.py)
  - bench-time-to-first-verified-finding (wall-clock of the same run)

Not yet wired (recorded honestly, not fabricated):
  - bench-triage-accuracy        — needs an expected_results comparator, not built yet
  - bench-provenance-recall      — needs graph/queries, owned by the parallel T1 thread

Run: python3 evals/harness_benchmarks/run_benchmarks.py
Output:
    evals/harness_benchmarks/results/latest.json
    evals/harness_benchmarks/results/history.jsonl  (append-only, per benchmarks.yaml trend:)
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BENCHMARKS_YAML = HERE / "benchmarks.yaml"
RESULTS = HERE / "results"
E2E_SMOKE = ROOT / "evals" / "e2e_smoke.py"

CHECK_LINE = re.compile(r"^\[(PASS|FAIL)\]\s+(.+?)(?:\s+—.*)?$")


def git_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=ROOT
        ).stdout.strip() or "no-commit"
    except OSError:
        return "no-git"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_benchmark_ids(path: Path) -> list[str]:
    """Minimal extraction of top-level `id:` fields from benchmarks.yaml.

    Not a general YAML parser — this file's shape is a flat list of mappings
    starting each entry with `- id: <value>`, which is all we need here.
    """
    ids = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^- id:\s*(\S+)", line)
        if m:
            ids.append(m.group(1))
    return ids


def run_e2e_smoke() -> tuple[dict[str, bool], float, int]:
    """Run the e2e smoke once; return (check_name -> passed, wall_seconds, returncode)."""
    start = time.monotonic()
    proc = subprocess.run(
        [sys.executable, str(E2E_SMOKE)], capture_output=True, text=True, cwd=ROOT
    )
    elapsed = time.monotonic() - start
    checks: dict[str, bool] = {}
    for line in proc.stdout.splitlines():
        m = CHECK_LINE.match(line.strip())
        if m:
            checks[m.group(2).strip()] = m.group(1) == "PASS"
    return checks, elapsed, proc.returncode


def score(checks: dict[str, bool], names: list[str]) -> tuple[int, int]:
    total = len(names)
    passed = sum(1 for n in names if checks.get(n) is True)
    return passed, total


def main() -> int:
    known_ids = set(load_benchmark_ids(BENCHMARKS_YAML))
    checks, elapsed, e2e_rc = run_e2e_smoke()

    results: list[dict] = []

    ec_passed, ec_total = score(
        checks,
        ["inventory observation has evidence", "artifact hash verifies after store+retrieval"],
    )
    results.append({
        "id": "bench-evidence-chain-completeness",
        "status": "wired",
        "passed": ec_passed, "total": ec_total,
        "rate": ec_passed / ec_total if ec_total else None,
        "gate": 1.0,
        "met": ec_total > 0 and ec_passed == ec_total,
    })

    db_passed, db_total = score(checks, ["out-of-scope dispatch denied"])
    results.append({
        "id": "bench-deny-by-default-behavior",
        "status": "wired",
        "passed": db_passed, "total": db_total,
        "rate": db_passed / db_total if db_total else None,
        "gate": 1.0,
        "met": db_total > 0 and db_passed == db_total,
    })

    results.append({
        "id": "bench-time-to-first-verified-finding",
        "status": "wired",
        "wall_seconds": round(elapsed, 3),
        "iteration_count": 1,
        "gate": None,
        "met": e2e_rc == 0,
    })

    for unwired_id in ("bench-triage-accuracy", "bench-provenance-recall"):
        if unwired_id in known_ids:
            results.append({"id": unwired_id, "status": "not_wired", "rate": None, "met": None})

    record = {
        "timestamp": now(),
        "commit": git_commit(),
        "e2e_returncode": e2e_rc,
        "benchmarks": results,
    }

    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "latest.json").write_text(json.dumps(record, indent=2) + "\n")
    with (RESULTS / "history.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    gated_failed = [r for r in results if r.get("gate") is not None and not r.get("met")]
    for r in results:
        label = r["id"]
        if r["status"] == "not_wired":
            print(f"[SKIP] {label} — not wired yet")
        else:
            print(f"[{'OK' if r.get('met') else 'GATE-MISS'}] {label} — {r}")

    return 0 if not gated_failed else 1


if __name__ == "__main__":
    sys.exit(main())
