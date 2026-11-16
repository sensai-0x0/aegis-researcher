# Adapter: MCP

Exposes the AEGIS research core as MCP (JSON-RPC 2.0 over stdio) tools so any
MCP-capable harness can consume the same canonical contracts.

**Server-side enforcement (curriculum P03 exit):** every tool call validates
its inputs against the contract schemas and routes authorization/policy
through `core/` — the harness on the other end of the pipe can never bypass
the scope gate.

## Tools

| Tool | Contract enforced | Core guard |
|------|-------------------|------------|
| `aegis.mission_validate` | mission.schema.json | none (read-only) |
| `aegis.scope_check` | mission + target | `core/scope.py` Decision |
| `aegis.audit_verify` | audit chain | `core/audit.py verify()` |

## Run

```bash
python3 -m adapters.mcp.server        # JSON-RPC 2.0 over stdin/stdout
```

Unsupported methods fail closed (JSON-RPC error, never a fallback).
