#!/usr/bin/env python3
"""AEGIS MCP-adapter interface-parity smoke (research test case 002).

Curriculum P03 exit criterion: "Two interfaces consume the same canonical
contracts." e2e_smoke.py proves the flow end-to-end through direct core/
calls (the "zeroth" interface). This script proves the SAME scope decisions
for the SAME mission+targets are reproduced, byte-for-reason, through the
`adapters/mcp` JSON-RPC stdio interface — a second, independent interface,
with zero scope/policy logic duplicated in the adapter itself.

Aligned to evals/test_cases/case-002-mcp-adapter-parity.yaml.

Run: python3 evals/mcp_adapter_smoke.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.audit import AuditLog            # noqa: E402
from core.mission import load_mission      # noqa: E402
from core.scope import ScopeResolver       # noqa: E402

MISSION = ROOT / "contracts" / "fixtures" / "mission.instance.json"

TARGETS = [
    "203.0.113.200",          # authorized: in CIDR, outside the excluded /25
    "203.0.113.50",           # denied: inside the excluded /25 carve-out
    "unauthorized.example.com",  # denied: not listed at all
]

FAILURES: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    mark = "PASS" if cond else "FAIL"
    print(f"[{mark}] {name}" + (f" — {detail}" if detail else ""))
    if not cond:
        FAILURES.append(name)


class MCPClient:
    """Minimal JSON-RPC 2.0 stdio client for adapters/mcp/server.py."""

    def __init__(self) -> None:
        self.proc = subprocess.Popen(
            # -u: the server's stdout is a pipe, not a tty, so Python fully
            # buffers it by default — readline() below would block forever
            # waiting on data sitting in the child's buffer without this.
            [sys.executable, "-u", "-m", "adapters.mcp.server"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, cwd=ROOT, bufsize=1,
        )
        self._id = 0

    def call(self, method: str, params: dict | None = None) -> dict:
        self._id += 1
        req = {"jsonrpc": "2.0", "id": self._id, "method": method}
        if params is not None:
            req["params"] = params
        assert self.proc.stdin is not None and self.proc.stdout is not None
        self.proc.stdin.write(json.dumps(req) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        return json.loads(line)

    def tool(self, name: str, arguments: dict) -> dict:
        resp = self.call("tools/call", {"name": name, "arguments": arguments})
        if "error" in resp:
            raise RuntimeError(resp["error"])
        return json.loads(resp["result"]["content"][0]["text"])

    def close(self) -> None:
        if self.proc.stdin:
            self.proc.stdin.close()
        self.proc.wait(timeout=5)


def main() -> int:
    mission = load_mission(MISSION)
    mission_raw = json.loads(MISSION.read_text())

    client = MCPClient()
    try:
        init = client.call("initialize")
        check("mcp server initializes", "result" in init and
              init["result"]["protocolVersion"] == "2024-11-05")

        listed = client.call("tools/list")
        tool_names = {t["name"] for t in listed["result"]["tools"]}
        check("mcp exposes mission_validate/scope_check/audit_verify",
              {"aegis.mission_validate", "aegis.scope_check", "aegis.audit_verify"} <= tool_names)

        validated = client.tool("aegis.mission_validate", {"mission": mission_raw})
        check("mcp mission_validate agrees mission is valid", validated["valid"] is True)

        # Parity: the same mission + target must produce the same decision
        # whether resolved directly through core/scope.py or through MCP.
        resolver = ScopeResolver(mission)
        for target in TARGETS:
            direct = resolver.decide(target)
            via_mcp = client.tool("aegis.scope_check",
                                   {"mission": mission_raw, "target": target})
            check(f"scope decision parity for {target}",
                  via_mcp["allowed"] == direct.allowed and via_mcp["reason"] == direct.reason,
                  f"direct={direct.allowed}/{direct.reason!r} "
                  f"mcp={via_mcp['allowed']}/{via_mcp['reason']!r}")

        # A malformed mission must never reach the scope resolver via MCP
        # (contract enforcement is server-side, not duplicated client logic).
        try:
            client.tool("aegis.scope_check",
                        {"mission": {"not": "a valid mission"}, "target": "203.0.113.200"})
            check("malformed mission rejected before scope resolution", False)
        except RuntimeError as e:
            check("malformed mission rejected before scope resolution",
                  "invalid params" in str(e).lower() or "contract" in str(e).lower())

        # Audit verify through MCP: a healthy chain verifies ...
        with tempfile.TemporaryDirectory() as td:
            audit_path = Path(td) / "audit.jsonl"
            audit = AuditLog(audit_path)
            audit.append("scope_decision", {"target": "203.0.113.200", "decision": "allow"})
            audit.append("scope_decision", {"target": "unauthorized.example.com", "decision": "deny"})
            verified = client.tool("aegis.audit_verify", {"path": str(audit_path)})
            check("mcp audit_verify confirms a healthy chain",
                  verified["ok"] is True and verified["entries"] == 2)

            # ... and a tampered chain is caught (not crashed on), through
            # the same interface. core/audit.py verifies eagerly on load and
            # raises AuditCorruptionError for a corrupted chain; the server
            # must report that as ok=False rather than dying mid-stream.
            lines = audit_path.read_text().splitlines()
            lines[-1] = lines[-1].replace('"decision": "deny"', '"decision": "allow"')
            audit_path.write_text("\n".join(lines) + "\n")
            tampered_result = client.tool("aegis.audit_verify", {"path": str(audit_path)})
            check("mcp audit_verify catches a tampered chain without crashing the server",
                  tampered_result["ok"] is False and tampered_result["first_bad_seq"] == 1)

            # The server process must still be alive and answer further calls.
            post = client.call("tools/list")
            check("mcp server survives a corrupted-chain report",
                  "result" in post and len(post["result"]["tools"]) == 3)
    finally:
        client.close()

    print("\nMCP ADAPTER PARITY SMOKE:", "OK" if not FAILURES else f"FAILED ({FAILURES})")
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    sys.exit(main())
