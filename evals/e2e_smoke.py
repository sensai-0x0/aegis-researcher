#!/usr/bin/env python3
"""AEGIS end-to-end smoke (graph-independent) — the definition-of-done path.

mission → scope/policy gate → orchestrator → worker → evidence vault →
observations → triaged findings → contract validation → audit verify → report.

Demonstrates the full evidence chain on the synthetic lab fixture with zero
external contact. Graph ingestion is deferred to the graph thread (T1).

Run: python3 evals/e2e_smoke.py
"""
from __future__ import annotations

import json
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.audit import AuditLog                     # noqa: E402
from core.evidence import EvidenceVault             # noqa: E402
from core.jsonschema_lite import ValidationError, validate  # noqa: E402
from core.mission import load_mission               # noqa: E402
from core.orchestrator import Orchestrator          # noqa: E402
from core.policy import PolicyEngine                # noqa: E402
from workers.system_inventory.worker import SystemInventoryWorker  # noqa: E402

FIXTURE = ROOT / "evals" / "test_cases" / "fixture-gw-service"
MISSION = ROOT / "contracts" / "fixtures" / "mission.instance.json"
OUT = ROOT / "reports" / "out"

FAILURES: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    mark = "PASS" if cond else "FAIL"
    print(f"[{mark}] {name}" + (f" — {detail}" if detail else ""))
    if not cond:
        FAILURES.append(name)


def schema_path(name: str) -> dict:
    return json.loads((ROOT / "contracts" / f"{name}.schema.json").read_text())


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def main() -> int:
    tmp = tempfile.TemporaryDirectory()
    vault_dir = Path(tmp.name) / "objects"

    # 1. Mission (contract-validated load; non-active would refuse).
    mission = load_mission(MISSION)
    check("mission loads + validates", mission["status"] == "active")

    # 2. Governance core.
    audit = AuditLog(Path(tmp.name) / "audit.jsonl")
    policy = PolicyEngine(audit, mission)
    orch = Orchestrator(mission, audit, policy)
    run = orch.start_run({"name": "cli", "version": "0.1.0"})
    check("run authorized via scope gate", run["status"] == "authorized")

    # 3. Out-of-scope dispatch MUST be denied AND audited.
    try:
        orch.dispatch(SystemInventoryWorker(), {
            "target": "unauthorized.example.com", "purpose": "probe",
            "hypothesis": "h", "path": str(FIXTURE)})
        check("out-of-scope dispatch denied", False)
    except Exception:
        check("out-of-scope dispatch denied",
              any(e["event"] == "scope_denied" for e in audit.entries()))

    # 4. In-scope dispatch of the inventory worker against the synthetic lab.
    result = orch.dispatch(
        SystemInventoryWorker(),
        {"target": "203.0.113.200", "purpose": "inventory synthetic gw-service lab",
         "hypothesis": "the lab tree contains admin.py and proxy.cfg components "
                       "whose route table shows an unauthenticated admin proxy",
         "hypothesis_id": "h1", "path": str(FIXTURE)},
        action={"name": "local inventory listing", "touches_target": True,
                "purely_passive": True})
    obs = result["observations"][0]
    artifact = result["artifact"]
    check("inventory observation has evidence", bool(obs["raw_evidence"]))
    check("coverage gap list empty (P02 exit)", "0 top-level" not in result["coverage_note"])

    # 5. Evidence vault: store artifact, verify hash on store AND retrieval (P01/W2).
    vault = EvidenceVault(vault_dir)
    (Path(tmp.name) / "listing.txt").write_text(result["raw"])
    record = vault.store(Path(tmp.name) / "listing.txt", run_id=run["run_id"],
                         media_type="text/plain", tool="aegis.system_inventory",
                         tool_version="0.1.0")
    vault.open(record["sha256"])  # verifies or raises
    check("artifact hash verifies after store+retrieval", True)

    # 6. Triage: h1 stays hypothesis (NO reproduction — inflation guard);
    #    h2 (inventory completeness) is confirmed WITH reproduction.
    hypothesis = {
        "finding_id": str(uuid.uuid4()), "title": "Admin route proxied without auth middleware",
        "status": "hypothesis", "affected_component": {
            "identifier": "gw-service", "version": "1.4.2",
            "anchors": ["admin.py:1", "proxy.cfg:1"]},
        "claim": "The admin route is proxied to loopback without the auth middleware.",
        "rationale": "proxy.cfg shows location /admin proxy_pass to 127.0.0.1:9090; "
                     "inventory artifact evidences both files' presence.",
        "verification_plan": "Static inspection of route application + authorized "
                             "lab reproduction requesting /admin/ unauthenticated.",
        "evidence": [record["sha256"]],
        "created_at": now(), "provenance": {"originated_by": "agent:source-analyst"},
    }
    confirmed = {
        "finding_id": str(uuid.uuid4()),
        "title": "Synthetic lab inventory is complete (no coverage gaps)",
        "status": "confirmed", "affected_component": {"identifier": "gw-service-lab"},
        "claim": "All fixture components were observed with hash-verified evidence.",
        "severity": "info",
        "severity_justification": "Completeness finding: reproduction re-runs the "
                                  "inventory and diffs zero missing components.",
        "evidence": [record["sha256"]],
        "reproduction": [
            "1. python3 workers/system_inventory/worker.py against the fixture",
            "2. assert components == {app.py, admin.py, proxy.cfg}",
            "3. assert artifact sha256 verifies in the vault",
        ],
        "root_cause": "n/a — completeness verification, not a weakness",
        "mitigation": "n/a",
        "reviewed_by": ["agent:reviewer"],
        "created_at": now(),
        "provenance": {"originated_by": "agent:reviewer", "triaged_by": "agent:reviewer"},
    }

    # 7. Contract validation of the finding-tier records.
    schema_map = {"observation": "observation", "artifact": "artifact",
                  "hypothesis": "finding", "finding": "finding"}
    for name, rec in (("observation", obs), ("artifact", artifact),
                      ("hypothesis", hypothesis), ("finding", confirmed)):
        try:
            validate(rec, schema_path(schema_map[name]))
            check(f"{name} validates against contract", True)
        except ValidationError as e:
            check(f"{name} validates against contract", False, str(e))

    # 8. Conclude + audit chain verification + final run-record validation.
    orch.conclude()
    try:
        validate(run, schema_path("run"))
        check("concluded run validates against contract", True)
    except ValidationError as e:
        check("concluded run validates against contract", False, str(e))
    ok, bad = audit.verify()
    check("audit chain verifies", ok and bad is None)
    check("run concluded with audit ref", run["audit_ref"].startswith("audit-chain:"))

    # 9. Human report: h1 renders as hypothesis (never as confirmed).
    OUT.mkdir(parents=True, exist_ok=True)
    (Path(tmp.name) / "h1.json").write_text(json.dumps(hypothesis))
    (Path(tmp.name) / "art.json").write_text(json.dumps(record))
    import subprocess
    proc = subprocess.run([sys.executable, str(ROOT / "reports" / "render_finding.py"),
                           str(Path(tmp.name) / "h1.json"),
                           "--artifact", str(Path(tmp.name) / "art.json"),
                           "-o", str(OUT / "e2e-h1-hypothesis-report.md")],
                          capture_output=True, text=True)
    check("hypothesis finding renders to report", proc.returncode == 0,
          proc.stdout.strip() or proc.stderr.strip())

    print("\nE2E SMOKE:", "OK" if not FAILURES else f"FAILED ({FAILURES})")
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    sys.exit(main())
