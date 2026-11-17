#!/usr/bin/env python3
"""Gate ratchet — gates may only tighten, never loosen.

Compares the numeric gates in the working tree against a base git ref for:

- ``tests/thresholds.json``                              (coverage / eval-rate floors)
- ``.agents/evals/eval-suite/heuristics.json``           (per-suite eval gates)

Exits 1 if any tracked numeric value **decreased**. Increases and new files
pass. This makes the test and eval libraries monotonically tighter over
time: a PR that relaxes a gate is rejected by CI, while tightening PRs
merge freely.

Usage:
    python tools/ci/check_ratchet.py --base origin/main
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

TRACKED_FILES = (
    "tests/thresholds.json",
    ".agents/evals/eval-suite/heuristics.json",
)

# Numeric keys that are version metadata, not gates.
SKIP_KEYS = {"version"}


def flatten_numbers(node: object, prefix: str = "") -> dict[str, float]:
    """Collect every numeric leaf as ``dotted.path -> value``."""
    out: dict[str, float] = {}
    if isinstance(node, dict):
        for key, child in node.items():
            if key in SKIP_KEYS:
                continue
            out.update(flatten_numbers(child, f"{prefix}{key}." if prefix else f"{key}."))
    elif isinstance(node, list):
        for i, child in enumerate(node):
            out.update(flatten_numbers(child, f"{prefix}{i}."))
    elif isinstance(node, bool):
        pass  # bools are not gates
    elif isinstance(node, (int, float)):
        out[prefix.rstrip(".")] = float(node)
    return out


def read_at_ref(ref: str, rel_path: str) -> dict | None:
    """Read a tracked file at a git ref; None when it did not exist there."""
    result = subprocess.run(
        ["git", "show", f"{ref}:{rel_path}"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        print(f"ERROR: {rel_path} at {ref} is not valid JSON: {exc}", file=sys.stderr)
        sys.exit(2)


def read_current(rel_path: str) -> dict:
    path = REPO_ROOT / rel_path
    if not path.is_file():
        print(f"ERROR: tracked gate file missing: {rel_path}", file=sys.stderr)
        sys.exit(2)
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base", required=True, help="git ref to compare against (e.g. origin/main)"
    )
    args = parser.parse_args()

    loosened: list[tuple[str, float, float]] = []
    tightened: list[tuple[str, float, float]] = []

    for rel_path in TRACKED_FILES:
        base = read_at_ref(args.base, rel_path)
        current = read_current(rel_path)
        if base is None:
            print(f"[NEW ] {rel_path} (not present at {args.base} — nothing to compare)")
            continue

        base_gates = flatten_numbers(base)
        current_gates = flatten_numbers(current)
        for gate, old in sorted(base_gates.items()):
            new = current_gates.get(gate)
            if new is None:
                loosened.append((f"{rel_path}::{gate}", old, float("-inf")))
                print(f"[LOOSENED] {rel_path}::{gate} {old} -> REMOVED")
            elif new < old:
                loosened.append((f"{rel_path}::{gate}", old, new))
                print(f"[LOOSENED] {rel_path}::{gate} {old} -> {new}")
            elif new > old:
                tightened.append((f"{rel_path}::{gate}", old, new))
                print(f"[TIGHTENED] {rel_path}::{gate} {old} -> {new}")
            else:
                print(f"[UNCHANGED] {rel_path}::{gate} = {new}")

    if loosened:
        print(
            f"\nRATCHET VIOLATION: {len(loosened)} gate(s) loosened relative to {args.base}. "
            "Gates may only increase. See tests/thresholds.json 'policy'.",
            file=sys.stderr,
        )
        return 1

    print(f"\nOK: no gates loosened ({len(tightened)} tightened) vs {args.base}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
