# P03 — Agent Harness Engineering

**Weeks 7–9 · Entry gate: P02 exit gate passed; System Atlas can inventory a local target**

## Purpose

Make Claude Code the *initial interface* to a portable, policy-governed research core — not the owner of policy, evidence or research state. This is the phase where the agentic-engineering thread becomes the main subject: everything before it built the substrate; everything after it runs through what gets built here.

## What this phase builds

- **Disciplined workspace (week 7):** `CLAUDE.md` with project goal, invariants and escalation rules; focused rules and skills for inventory, source review and evidence handling; session handoff notes and a research decision log. Progressive disclosure is enforced: a fresh session can identify the project goal, current mission and constraints without replaying the entire conversation.
- **Roles and deterministic controls (week 8):** systems analyst, source analyst, reviewer and evidence curator roles; hooks and permissions for deterministic checks and audit logging; a **tool broker** that validates mission, target, operation and approval state before any execution. Test suite covers denied operations, invalid scope, malformed requests and emergency stop.
- **MCP and portability (week 9):** versioned JSON contracts for missions, tool requests, runs, observations and findings; CLI and MCP adapters consuming the same canonical contracts; harness run metadata schema (model, harness, version, settings, tool versions per run).

## Agentic engineering thread

This is the curriculum's core thesis in code. Three invariants drive all three weeks:

1. **Separation of reasoning from authority.** Agents propose; the tool broker and policy engine decide. The acceptance criterion is blunt: *agents cannot broaden scope or self-approve consequential actions*, and denied operations are blocked at the execution boundary — not by a polite model.
2. **Harness independence.** Core policy and evidence logic live outside harness-specific code; two interfaces consume the same contracts; unsupported adapters **fail closed**. If Claude Code disappears tomorrow, the research core survives.
3. **Context as a designed artifact.** Persistent context is concise, layered and gated — the anti-context-bloat discipline that keeps a 36-week project from drowning its own agents in transcripts.

## Vulnerability research thread

The tool broker is vulnerability research *infrastructure*: it makes every permitted tool execution attributable to a mission and run, so a finding can always be traced back to authorized, auditable execution. Week 8's adversarial test suite (malformed requests, invalid scope, denied operations) is also the researcher's first taste of attacking an authorization boundary — a skill turned around on the harness itself in P09.

## Exit gate

- Two interfaces consume the same canonical contracts.
- Core policy and evidence logic remain outside harness-specific code.
- Unsupported adapters fail closed.

## 🎯 Goal Project

**Prove the core is bigger than its harness.** Deliver the Claude Code configuration, four agent role definitions, the tool broker prototype with its policy test suite, and both CLI and MCP adapters over the same versioned contracts. Then run one identical bounded research task (e.g., a System Atlas inventory pass) through *both* adapters.

**Pass condition:** the two runs produce comparable, schema-valid results with complete run metadata; a deliberately invalid tool request (wrong mission, expired scope, malformed schema) is rejected identically by both paths; and the harness-specific code contains zero policy or evidence logic. The reviewer — with independent context — confirms the boundary by attempting an operation the broker must deny.
