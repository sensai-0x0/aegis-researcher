---
name: source-review
description: Structured source code review for weaknesses. Use when reviewing authorized source code to produce hypothesis-driven findings — entry points, attacker-reachable paths, dangerous sinks, and proposed verification methods (Discover).
---

# Skill: Source Review

Structured, hypothesis-driven source review. Produces **hypotheses with anchors**,
not conclusions — verification is a separate, mandatory step.

## Inputs

- Authorized access to the source (in-scope per mission).
- The current inventory model (components, trust boundaries) — review is targeted,
  not a line-by-line read.
- Prior findings/hypotheses from the graph (avoid rediscovering; build on them).

## Procedure

1. **Orient on entry points**: enumerate externally reachable inputs (network
   handlers, parsers, file importers, agent tool invocations, IPC).
2. **Trace attacker-reachable paths** from entry points toward high-value sinks:
   memory operations, deserialization, command execution, file/SQL access,
   authentication decisions, agent action dispatch.
3. **Record hypotheses**: for each suspicious path, write a hypothesis per rule
   `research.md` — claim, plausibility rationale, file:line anchor(s), what evidence
   would confirm/refute, and the **proposed verification method** (which worker,
   what input, what expected observation).
4. **Prioritize** by reachability × impact; record the prioritization rationale.
5. Hand the hypothesis list to `finding-triage` / the reviewer agent. Do not label
   anything confirmed.

## Outputs

- Hypothesis records (contract: `finding.schema.json`, status `hypothesis`), each
  with file:line anchors and a verification plan.
- An updated model of dangerous sinks per component (feeds the graph).
- Coverage note: code regions reviewed vs. skipped, with reasons.

## Quality bar

- Every hypothesis has ≥1 precise anchor (file:line) — no "somewhere in auth".
- Every hypothesis names its refutation condition.
- Review coverage is stated (what was and wasn't read).

## Failure modes

- Reporting a suspicious pattern as a finding — it is a hypothesis until reproduced.
- Reviewing without the inventory (blind line-by-line reads waste budget and miss
  trust boundaries).
- Dropping hypotheses that look "probably fine" without recording why (negative
  results are knowledge).
