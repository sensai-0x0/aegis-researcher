#!/usr/bin/env python3
"""Generate the ui/orb status surface (stdlib-only, read-only over repo state)."""
from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / ".agents" / "evals" / "results" / "latest.json"
LEDGER = ROOT / ".agents" / "evals" / "progress.md"

HTML = """<!doctype html>
<html><head><meta charset="utf-8"><title>AEGIS — Status</title>
<style>
 body{font-family:ui-monospace,monospace;background:#0b0e14;color:#d7dce3;margin:2rem}
 h1{color:#7ee2b8} h2{color:#9fb2c8;font-weight:600}
 .ok{color:#7ee2b8}.red{color:#ff7a90}.dim{color:#5c6773}
 table{border-collapse:collapse;margin:1rem 0}td,th{border:1px solid #263042;padding:.4rem .8rem;text-align:left}
 .bar{display:inline-block;height:.8rem;background:#263042;border-radius:.4rem;overflow:hidden;vertical-align:middle;width:16rem}
 .bar>span{display:block;height:100%;background:#7ee2b8}
</style></head><body>
<h1>🛡 AEGIS — status orb</h1>
<p class="dim">generated @@TS@@ · commit @@COMMIT@@</p>
<h2>Eval suites</h2>
<table><tr><th>suite</th><th>rate</th><th></th><th>gate</th></tr>@@SUITE_ROWS@@</table>
<h2>Overall</h2>
<p>@@OVERALL@@ <span class="dim">(@@PASSED@@/@@TOTAL@@ heuristics)</span></p>
<h2>Loop</h2>
<p>phase: <b>@@PHASE@@</b><br>next: @@NEXT@@</p>
<p class="dim">graph suite owned by a parallel thread · data: .agents/evals/results/latest.json</p>
</body></html>
"""


def git_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True, cwd=ROOT).stdout.strip()
    except OSError:
        return "unknown"


def ledger_fields() -> tuple[str, str]:
    if not LEDGER.is_file():
        return "unknown", "unknown"
    t = LEDGER.read_text()
    phase = re.search(r"\*\*Current phase:\*\*\s*(.+)", t)
    nxt = re.search(r"\*\*Next queued action:\*\*\s*(.+)", t)
    return (phase.group(1).strip() if phase else "unknown",
            nxt.group(1).strip()[:120] if nxt else "unknown")


def main() -> int:
    data = json.loads(RESULTS.read_text())
    rows = []
    for cap, s in data["suites"].items():
        cls = "ok" if s["met"] else "red"
        pct = int(s["rate"] * 100)
        rows.append(f'<tr><td>{cap}</td><td class="{cls}">{pct}%</td>'
                    f'<td><span class="bar"><span style="width:{pct}%"></span></span></td>'
                    f'<td class="dim">{int(s["gate"] * 100)}%</td></tr>')
    phase, nxt = ledger_fields()
    o = data["overall"]
    owned_green = all(s["met"] for c, s in data["suites"].items() if c != "graph")
    html = (HTML
            .replace("@@TS@@", time.strftime("%Y-%m-%d %H:%M %Z"))
            .replace("@@COMMIT@@", git_commit())
            .replace("@@SUITE_ROWS@@", "\n".join(rows))
            .replace("@@OVERALL@@", "ALL OWNED GATES GREEN" if owned_green else "GATES OPEN")
            .replace("@@PASSED@@", str(o["passed"]))
            .replace("@@TOTAL@@", str(o["total"]))
            .replace("@@PHASE@@", phase)
            .replace("@@NEXT@@", nxt))
    (ROOT / "ui" / "orb" / "status.html").write_text(html)
    (ROOT / "ui" / "orb" / "status.json").write_text(json.dumps(data, indent=2))
    print(f"status.html + status.json written ({o['passed']}/{o['total']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
