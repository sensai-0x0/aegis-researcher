"""AEGIS MCP server — JSON-RPC 2.0 over stdio.

Thin, honest MCP surface: three tools, each backed by core/. All scope and
policy decisions happen in core; this file only marshals JSON-RPC and
validates payloads against the canonical contracts. Unknown methods fail
closed.

Run: python3 -m adapters.mcp.server
Test: echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python3 -m adapters.mcp.server
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.audit import AuditCorruptionError, AuditLog  # noqa: E402
from core.jsonschema_lite import ValidationError, validate  # noqa: E402
from core.mission import load_schema  # noqa: E402
from core.scope import ScopeResolver  # noqa: E402

PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "aegis-mcp", "version": "0.1.0"}

TOOLS = [
    {
        "name": "aegis.mission_validate",
        "description": "Validate a mission document against the canonical contract.",
        "inputSchema": {
            "type": "object",
            "required": ["mission"],
            "properties": {"mission": {"type": "object"}},
        },
    },
    {
        "name": "aegis.scope_check",
        "description": "Resolve a mission target via core/scope.py (deny-by-default).",
        "inputSchema": {
            "type": "object",
            "required": ["mission", "target"],
            "properties": {"mission": {"type": "object"}, "target": {"type": "string"}},
        },
    },
    {
        "name": "aegis.audit_verify",
        "description": "Verify the hash chain of an audit log file.",
        "inputSchema": {
            "type": "object",
            "required": ["path"],
            "properties": {"path": {"type": "string"}},
        },
    },
]


def tool_call(name: str, args: dict) -> dict:
    """Dispatch a tool call. Fail closed on unknown tools."""
    if name == "aegis.mission_validate":
        try:
            validate(args["mission"], load_schema())
            return {"valid": True, "contract": "mission.schema.json"}
        except (ValidationError, KeyError) as e:
            return {"valid": False, "error": str(e)}
    if name == "aegis.scope_check":
        # Contract enforcement is server-side: a malformed mission never
        # reaches the scope resolver (curriculum P03: interfaces consume the
        # same canonical contracts).
        try:
            validate(args["mission"], load_schema())
        except (ValidationError, KeyError) as e:
            raise ValueError(f"mission violates contract: {e}") from e
        decision = ScopeResolver(args["mission"]).decide(args["target"])
        return {"allowed": decision.allowed, "reason": decision.reason,
                "decided_at": decision.decided_at, "enforced_by": "core/scope.py"}
    if name == "aegis.audit_verify":
        # core/audit.py verifies eagerly on load and raises on a corrupted
        # chain (fail-closed by design — see tests/test_policy_audit.py
        # test_tamper_detection). audit_verify's job is to REPORT that
        # corruption, not to crash the server on it, so it is caught here.
        try:
            audit = AuditLog(args["path"])
        except AuditCorruptionError as e:
            m = re.search(r"at seq (\d+)", str(e))
            return {"ok": False, "first_bad_seq": int(m.group(1)) if m else None,
                    "entries": None}
        ok, bad = audit.verify()
        return {"ok": ok, "first_bad_seq": bad, "entries": len(audit.entries())}
    raise KeyError(f"unknown tool {name!r}: failing closed")


def handle(msg: dict) -> dict | None:
    method, mid = msg.get("method"), msg.get("id")
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": mid,
                "result": {"protocolVersion": PROTOCOL_VERSION,
                           "serverInfo": SERVER_INFO, "tools": TOOLS}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}}
    if method == "tools/call":
        params = msg.get("params", {})
        try:
            result = tool_call(params.get("name", ""), params.get("arguments", {}))
            return {"jsonrpc": "2.0", "id": mid,
                    "result": {"content": [{"type": "text",
                                            "text": json.dumps(result, sort_keys=True)}]}}
        except (KeyError, ValidationError, FileNotFoundError, ValueError) as e:
            return {"jsonrpc": "2.0", "id": mid,
                    "error": {"code": -32602, "message": f"invalid params: {e}"}}
    if "id" in msg:
        return {"jsonrpc": "2.0", "id": mid,
                "error": {"code": -32601, "message": f"method not found: {method}"}}
    return None  # notification: no response


def main() -> int:  # pragma: no cover - exercised via stdio
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError as e:
            print(json.dumps({"jsonrpc": "2.0", "id": None,
                              "error": {"code": -32700, "message": f"parse error: {e}"}}))
            continue
        resp = handle(msg)
        if resp is not None:
            print(json.dumps(resp))
    return 0


if __name__ == "__main__":
    sys.exit(main())
