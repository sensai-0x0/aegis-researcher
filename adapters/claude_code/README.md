# Adapter: Claude Code

Maps AEGIS concepts onto the Claude Code harness: missions become routed work
plans (skills + agents per `CLAUDE.md`), plan steps become skill invocations.

**Boundary (curriculum P03):** this adapter contains ZERO policy, scope or
evidence logic. It packages requests for the core; `core/scope.py`,
`core/policy.py` and `core/audit.py` own every decision.

- `prepare()` translates a contract mission into steps naming the responsible
  skill/agent from `.claude/` (routing table lives in CLAUDE.md).
- `execute()` runs one step through the orchestrator (authorization + policy
  enforced there, not here).
- `report()` renders a contract run record for the harness.
