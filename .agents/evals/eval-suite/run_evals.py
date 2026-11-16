#!/usr/bin/env python3
"""AEGIS heuristic eval suite (stdlib-only).

Compares repository/agent state against the heuristics registered in
heuristics.json. Each heuristic is a simple, deterministic check over the
codebase — the machine-checkable form of "is the agent doing the right thing".

Usage:
    python3 .agents/evals/eval-suite/run_evals.py [--strict]

Output:
    .agents/evals/results/latest.json   (full result, overwritten)
    .agents/evals/results/history.jsonl (one line per run, append-only)
Exit code 0 when every suite gate is met, else 1.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import ipaddress  # noqa: F401  (kept for future IPv6 work)

ROOT = Path(__file__).resolve().parents[3]
EVALS = ROOT / ".agents" / "evals"
RESULTS = EVALS / "results"
REGISTRY = Path(__file__).resolve().parent / "heuristics.json"

# Files/dirs whose content legitimately contains secret-like or address-like
# strings because they DEFINE the patterns (self-exemption list).
SCAN_SKIP = (".git", ".venv", "__pycache__", "results", "eval-suite", "errors.md")

DOC_RANGES = ("192.0.2.", "198.51.100.", "203.0.113.")
PRIVATE_OK = ("127.", "10.", "192.168.", "172.", "0.0.0.0", "255.255.255.255")

SECRET_PATTERNS = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)\b(api[_-]?key|secret|passwd|password|token)\b\s*[=:]\s*['\"][A-Za-z0-9+/_\-]{16,}['\"]"),
)
IPV4_RE = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")


def tracked_files() -> list[Path]:
    """Files to scan: everything under ROOT except skip-list entries."""
    out = []
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT).as_posix()
        if any(s in rel for s in SCAN_SKIP):
            continue
        if p.suffix in {".pyc", ".pyo", ".so", ".png", ".jpg", ".pdf"}:
            continue
        out.append(p)
    return out


def read(rel: str) -> str | None:
    p = ROOT / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else None


def git_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=ROOT
        ).stdout.strip() or "no-commit"
    except OSError:
        return "no-git"


# --------------------------------------------------------------------------
# Heuristic implementations. Each returns (passed, detail).
# --------------------------------------------------------------------------

def h_claude_md() -> tuple[bool, str]:
    t = read("CLAUDE.md")
    if not t:
        return False, "CLAUDE.md missing"
    if len(t) < 800:
        return False, f"too thin ({len(t)} bytes)"
    need = ("mission", "evidence", "scope")
    low = t.lower()
    missing = [k for k in need if k not in low]
    if missing:
        return False, f"missing keywords: {missing}"
    return True, f"{len(t)} bytes, mission/constraints/routing present"


def h_pyproject() -> tuple[bool, str]:
    t = read("pyproject.toml")
    if not t:
        return False, "pyproject.toml missing"
    ok_name = re.search(r'name\s*=\s*["\']aegis["\']', t)
    ok_proj = "[project]" in t
    ok_scripts = "[project.scripts]" in t
    if not (ok_name and ok_proj):
        return False, f"name={bool(ok_name)} [project]={ok_proj}"
    return True, f"PEP 621 ok, scripts={ok_scripts}"


def h_readme() -> tuple[bool, str]:
    t = read("README.md")
    if not t:
        return False, "README.md missing"
    low = t.lower()
    checks = {
        "architecture": "architecture" in low or "data flow" in low or "──" in t or "→" in t,
        "epistemic": "observation" in low and "hypothesis" in low and ("confirmed" in low or "finding" in low),
    }
    failed = [k for k, v in checks.items() if not v]
    if failed:
        return False, f"missing: {failed}"
    return True, "architecture + epistemic model documented"


def _frontmatter(rel: str, required_keys: tuple[str, ...]) -> tuple[bool, str]:
    t = read(rel)
    if not t:
        return False, f"{rel} missing"
    if not t.lstrip().startswith("---"):
        return False, f"{rel} has no YAML frontmatter"
    head = t.split("---", 2)[1]
    missing = [k for k in required_keys if not re.search(rf"^\s*{k}\s*:", head, re.M)]
    if missing:
        return False, f"{rel} frontmatter missing: {missing}"
    return True, "frontmatter ok"


def h_rules() -> tuple[bool, str]:
    fails = []
    for r in ("research", "evidence", "scope"):
        t = read(f".claude/rules/{r}.md")
        if not t:
            fails.append(f"{r}.md missing")
            continue
        if len(t) < 400:
            fails.append(f"{r}.md too thin ({len(t)}B)")
        elif not re.search(r"\bMUST\b|\bMUST NOT\b|\bMUST-NOT\b", t):
            fails.append(f"{r}.md has no MUST/MUST NOT rules")
    return (not fails), "; ".join(fails) or "3 rules with MUST/MUST NOT present"


def h_skills() -> tuple[bool, str]:
    fails = []
    for s in ("inventory", "source-review", "finding-triage"):
        ok, detail = _frontmatter(f".claude/skills/{s}/SKILL.md", ("name", "description"))
        if not ok:
            fails.append(detail)
    return (not fails), "; ".join(fails) or "3 skills with valid frontmatter"


def h_agents() -> tuple[bool, str]:
    fails = []
    for a in ("systems-analyst", "source-analyst", "reviewer", "evidence-curator"):
        ok, detail = _frontmatter(f".claude/agents/{a}.md", ("name", "description", "tools"))
        if not ok:
            fails.append(detail)
    return (not fails), "; ".join(fails) or "4 agents with valid frontmatter"


def h_settings() -> tuple[bool, str]:
    t = read(".claude/settings.json")
    if not t:
        return False, "settings.json missing"
    try:
        data = json.loads(t)
    except json.JSONDecodeError as e:
        return False, f"invalid JSON: {e}"
    perms = data.get("permissions", {})
    tiers = [k for k in ("allow", "ask", "deny") if k in perms]
    if not tiers:
        return False, "no permission tiers defined"
    return True, f"tiers: {tiers}"


def _load_schemas() -> dict[str, str | None]:
    return {n: read(f"contracts/{n}.schema.json") for n in
            ("mission", "run", "observation", "finding", "artifact")}


def h_contracts_parse() -> tuple[bool, str]:
    fails = []
    for name, t in _load_schemas().items():
        if t is None:
            fails.append(f"{name} missing")
            continue
        try:
            json.loads(t)
        except json.JSONDecodeError as e:
            fails.append(f"{name}: {e}")
    return (not fails), "; ".join(fails) or "5/5 parse"


def h_contracts_draft() -> tuple[bool, str]:
    fails = []
    for name, t in _load_schemas().items():
        if t is None:
            continue
        if "2020-12" not in t:
            fails.append(f"{name} not draft 2020-12")
    return (not fails), "; ".join(fails) or "all draft 2020-12"


def h_contracts_ladder() -> tuple[bool, str]:
    t = read("contracts/finding.schema.json") or ""
    ladder = ("observation", "hypothesis", "confirmed", "rejected")
    missing = [s for s in ladder if s not in t]
    return (not missing), f"missing statuses: {missing}" if missing else "epistemic ladder enforced"


def h_observation_evidence() -> tuple[bool, str]:
    t = read("contracts/observation.schema.json") or ""
    if not t:
        return False, "observation schema missing"
    has_req = re.search(r"\"(?:raw_)?evidence\"\s*:\s*\{[^}]*\"minItems\"\s*:\s*1", t, re.S) or \
              ("required" in t and re.search(r"(raw_)?evidence", t) and "minItems" in t)
    return bool(has_req), "evidence refs required" if has_req else "observations may exist without evidence"


def h_artifact_hash() -> tuple[bool, str]:
    t = read("contracts/artifact.schema.json") or ""
    return ("sha256" in t and "required" in t), "sha256 required" if "sha256" in t else "artifact schema missing sha256"


def h_contracts_closed() -> tuple[bool, str]:
    fails = [n for n, t in _load_schemas().items()
             if t is not None and "additionalProperties" not in t]
    return (not fails), "; ".join(f"{f} not closed" for f in fails) or "all schemas closed"


def h_no_secrets() -> tuple[bool, str]:
    hits = []
    for p in tracked_files():
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for pat in SECRET_PATTERNS:
            m = pat.search(text)
            if m:
                hits.append(f"{p.relative_to(ROOT)}:{pat.pattern[:24]}")
    return (not hits), "; ".join(hits[:5]) or "no credential-shaped strings"


def h_no_real_addresses() -> tuple[bool, str]:
    hits = []
    for p in tracked_files():
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in IPV4_RE.finditer(text):
            ip = m.group(0)
            if ip.startswith(DOC_RANGES) or ip.startswith(PRIVATE_OK):
                continue
            hits.append(f"{p.relative_to(ROOT)}:{ip}")
    return (not hits), "; ".join(hits[:5]) or "only documentation/private ranges"


def h_scope_deny_default() -> tuple[bool, str]:
    t = read("core/scope.py") or ""
    if not t:
        return False, "core/scope.py missing"
    checks = {
        "deny-by-default": re.search(r"(?i)deny.by.default|DEFAULT\s*=\s*.{0,20}DENY|default.{0,20}deny", t) is not None,
        "assert_authorized": "def assert_authorized" in t or "def assert_authorization" in t,
    }
    failed = [k for k, v in checks.items() if not v]
    return (not failed), "; ".join(failed) or "deny-by-default + assert_authorized present"


def h_policy_gating() -> tuple[bool, str]:
    t = read("core/policy.py") or ""
    if not t:
        return False, "core/policy.py missing"
    checks = {
        "consequential-class": re.search(r"(?i)consequential", t) is not None,
        "approval": re.search(r"(?i)approval|approved_by|approve", t) is not None,
    }
    failed = [k for k, v in checks.items() if not v]
    return (not failed), "; ".join(failed) or "consequential actions gated by approval"


def h_audit_append_only() -> tuple[bool, str]:
    t = read("core/audit.py") or ""
    if not t:
        return False, "core/audit.py missing"
    chained = "prev_hash" in t or "previous_hash" in t
    hashed = "sha256" in t or "hashlib" in t
    deletes = re.search(r"def\s+\w*delete\w*|def\s+\w*remove\w*|def\s+\w*truncate\w*", t, re.I)
    if not (chained and hashed):
        return False, f"chained={chained} hashed={hashed}"
    if deletes:
        return False, f"append-only violated: {deletes.group(0)}"
    return True, "hash-chained, append-only, no delete/remove/truncate"


def h_manifests() -> tuple[bool, str]:
    t = read("evidence/manifests/README.md")
    if not t:
        return False, "manifests README missing"
    low = t.lower()
    ok = "custody" in low or "provenance" in low
    return ok, "custody documented" if ok else "no custody/provenance rules"


def h_objects() -> tuple[bool, str]:
    t = read("evidence/objects/README.md")
    if not t:
        return False, "objects README missing"
    low = t.lower()
    ok = ("immutab" in low or "immutable" in low) and ("sha256" in low or "content-address" in low)
    return ok, "immutability + content addressing" if ok else "missing immutability/content-addressing"


def h_observation_no_claims() -> tuple[bool, str]:
    t = read("contracts/observation.schema.json") or ""
    if not t:
        return False, "observation schema missing"
    bad = re.search(r"(?i)\"conclusion\"|\"verdict\"|\"confirmed_finding\"", t)
    return (not bad), "facts only" if not bad else f"claim-like field found: {bad.group(0)}"


def h_graph_constraints() -> tuple[bool, str]:
    t = read("graph/schema.cypher")
    if not t:
        return False, "schema.cypher missing"
    n = len(re.findall(r"(?i)CREATE CONSTRAINT", t))
    has_sha = "sha256" in t
    return n >= 3 and has_sha, f"{n} constraints, sha256={has_sha}"


def h_graph_queries() -> tuple[bool, str]:
    qdir = ROOT / "graph" / "queries"
    if not qdir.is_dir():
        return False, "queries dir missing"
    files = [p.name for p in qdir.glob("*") if p.suffix in {".cypher", ".cyp"}]
    if len(files) < 5:
        return False, f"{len(files)}/5 queries"
    joined = " ".join((qdir / f).read_text(errors="replace").lower() for f in files)
    need = ("attack" in joined or "path" in joined, "coverage" in joined or "gap" in joined)
    if not all(need):
        return False, f"missing themes: attack-path={need[0]} coverage-gap={need[1]}"
    return True, f"{len(files)} queries with required themes"


def h_ingest() -> tuple[bool, str]:
    t = read("graph/ingest.py") or ""
    if not t:
        return False, "graph/ingest.py missing"
    ok = re.search(r"(?i)\bMERGE\b|idempotent", t) is not None
    return ok, "MERGE/idempotent" if ok else "no idempotent upsert path"


def h_progress() -> tuple[bool, str]:
    t = read(".agents/evals/progress.md") or ""
    if not t:
        return False, "progress.md missing"
    it = re.search(r"\*\*Loop iteration:\*\*\s*(\d+)", t)
    phase = re.search(r"\*\*Current phase:\*\*\s*(.+)", t)
    nxt = re.search(r"\*\*Next queued action:\*\*\s*(\S.*)", t)
    if not it or int(it.group(1)) < 1:
        return False, f"iteration counter invalid ({it.group(1) if it else 'none'})"
    if not phase or "NOT-STARTED" in phase.group(1):
        return False, "phase not set"
    if not nxt:
        return False, "no next action queued"
    return True, f"iter={it.group(1)}, phase={phase.group(1).strip()}"


def h_decision_log() -> tuple[bool, str]:
    t = read(".agents/evals/progress.md") or ""
    # Rows after the header row in the decision table; baseline entry alone is not enough.
    rows = [ln for ln in t.splitlines() if re.match(r"^\|\s*\d+\s*\|\s*\d+\s*\|", ln)]
    return (len(rows) >= 2), f"{len(rows)} entries" if len(rows) >= 2 else "decision log not appended beyond baseline"


def h_errors_ledger() -> tuple[bool, str]:
    t = read(".agents/evals/errors.md") or ""
    if not t:
        return False, "errors.md missing"
    for key in ("symptom", "root cause", "patch", "prevention"):
        if key not in t.lower():
            return False, f"errors.md missing section: {key}"
    return True, "entry format defined"


def h_test_cases() -> tuple[bool, str]:
    d = ROOT / "evals" / "test_cases"
    files = [p for p in d.glob("*") if p.name != ".gitkeep"] if d.is_dir() else []
    return bool(files), f"{len(files)} cases" if files else "no research test cases"


def h_expected_results() -> tuple[bool, str]:
    d = ROOT / "evals" / "expected_results"
    files = [p for p in d.glob("*") if p.name != ".gitkeep"] if d.is_dir() else []
    return bool(files), f"{len(files)} ground truths" if files else "no expected results"


CHECKS = {
    "harness.claude-md-contract": h_claude_md,
    "harness.pyproject-valid": h_pyproject,
    "harness.readme-architecture": h_readme,
    "harness.rules-nonempty": h_rules,
    "harness.skills-frontmatter": h_skills,
    "harness.agents-frontmatter": h_agents,
    "harness.settings-json-valid": h_settings,
    "contracts.all-parse": h_contracts_parse,
    "contracts.draft-2020-12": h_contracts_draft,
    "contracts.epistemic-ladder": h_contracts_ladder,
    "contracts.observation-evidence": h_observation_evidence,
    "contracts.artifact-hash": h_artifact_hash,
    "contracts.no-open-objects": h_contracts_closed,
    "safety.no-hardcoded-secrets": h_no_secrets,
    "safety.no-undocumented-addresses": h_no_real_addresses,
    "safety.scope-deny-by-default": h_scope_deny_default,
    "safety.policy-approval-gating": h_policy_gating,
    "safety.audit-append-only": h_audit_append_only,
    "evidence.manifests-documented": h_manifests,
    "evidence.objects-immutability": h_objects,
    "evidence.observation-no-claims": h_observation_no_claims,
    "graph.constraints-defined": h_graph_constraints,
    "graph.queries-present": h_graph_queries,
    "graph.ingest-idempotent": h_ingest,
    "process.progress-ledger-current": h_progress,
    "process.decision-log-appended": h_decision_log,
    "process.errors-ledger": h_errors_ledger,
    "research.test-cases-present": h_test_cases,
    "research.expected-results": h_expected_results,
}


def main() -> int:
    registry = json.loads(REGISTRY.read_text())
    results, suites = [], {}
    for h in registry["heuristics"]:
        hid, cap = h["id"], h["capability"]
        fn = CHECKS.get(hid)
        if fn is None:
            passed, detail = False, "NO IMPLEMENTATION (registry/runner drift)"
        else:
            passed, detail = fn()
        results.append({"id": hid, "capability": cap, "passed": passed, "detail": detail})

    for cap in registry["suites"]:
        sub = [r for r in results if r["capability"] == cap]
        total, npass = len(sub), sum(r["passed"] for r in sub)
        rate = npass / total if total else 1.0
        gate = registry["suites"][cap]["gate"]
        suites[cap] = {"passed": npass, "total": total, "rate": round(rate, 3),
                       "gate": gate, "met": rate >= gate}

    record = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "commit": git_commit(),
        "overall": {"passed": sum(r["passed"] for r in results),
                    "total": len(results),
                    "rate": round(sum(r["passed"] for r in results) / len(results), 3)},
        "suites": suites,
        "heuristics": results,
    }

    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "latest.json").write_text(json.dumps(record, indent=2) + "\n")
    with (RESULTS / "history.jsonl").open("a") as f:
        f.write(json.dumps({k: record[k] for k in ("timestamp", "commit", "overall", "suites")}) + "\n")

    w = max(len(r["id"]) for r in results) + 2
    for r in results:
        mark = "PASS" if r["passed"] else "FAIL"
        print(f"[{mark}] {r['id']:<{w}} {r['detail']}")
    print("-" * 78)
    for cap, s in suites.items():
        flag = "OK " if s["met"] else "GATE"
        print(f"[{flag}] {cap:<10} {s['passed']}/{s['total']} ({s['rate']:.0%}) gate>={s['gate']:.0%}")
    print(f"overall: {record['overall']['passed']}/{record['overall']['total']} ({record['overall']['rate']:.0%})")

    failed_gates = [c for c, s in suites.items() if not s["met"]]
    if failed_gates:
        print(f"GATES NOT MET: {failed_gates}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
