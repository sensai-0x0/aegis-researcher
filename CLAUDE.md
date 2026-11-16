# AEGIS — Agent Harness Contract

AEGIS is an evidence-driven security research intelligence platform. It develops deep,
verifiable understanding of software, hardware and AI-agent systems — optimizing for
verified knowledge, reproducibility and cumulative discovery, **never** for activity,
tool usage, or the volume of reported vulnerabilities.

## Mission in one line

Every research activity must compound upon the last:
**Understand → Discover → Verify → Improve → Connect → Evolve.**

## Hard constraints (apply to everything you do here)

1. All research stays within **explicitly authorized environments** — resolve targets
   through `core/scope.py` before any contact. Deny-by-default.
2. **Consequential actions require recorded human approval** (enforced by
   `core/policy.py`, logged by `core/audit.py`).
3. **Evidence is authoritative.** An observation without an artifact reference is
   invalid. An unverified claim is a hypothesis, never a finding.
4. An **append-only audit log** records every authorization and policy decision.

## Repository map

| Path | Purpose |
|------|---------|
| `contracts/` | JSON Schemas — the platform's type system (mission, run, observation, finding, artifact) |
| `core/` | Mission model, scope resolver, policy engine, orchestrator, audit chain |
| `adapters/` | Bridges to agent harnesses (claude_code, codex, mcp) and the operator CLI |
| `workers/` | Research activity producers (inventory, static analysis, fuzzing, firmware, qemu, renode) — emit observations only |
| `evidence/` | Content-addressed, immutable objects + manifests (chain of custody) |
| `graph/` | Provenance-rich knowledge graph (schema, ingestion, cross-domain queries) |
| `evals/` | Research test corpus, ground truth, harness benchmarks |
| `ui/orb/` | Status/visualization surface |
| `reports/` | Human-readable report templates |

## The epistemic ladder (the heart of AEGIS)

`observation` (reproducible fact + evidence) → `hypothesis` (claimed weakness,
unverified) → `confirmed` (reproduced, evidence-backed) → `rejected` (refuted, with
evidence). You must never skip a rung or relabel without new evidence.

## Routing

| Task | Use |
|------|-----|
| Model a system, enumerate components/trust boundaries | skill `inventory` + agent `systems-analyst` |
| Review source for weaknesses | skill `source-review` + agent `source-analyst` |
| Classify observations / validate findings | skill `finding-triage` + agent `reviewer` |
| Evidence hygiene, manifests, graph ingestion | agent `evidence-curator` |

## Operating rules

- Method rules: `.claude/rules/{research,evidence,scope}.md` — MUST/MUST NOT.
- Full operating plan: `.agents/plans/init.md` (§5 continuous work loop).
- Measurement: `.agents/evals/eval-suite/run_evals.py` (heuristic evals; gates red ⇒
  fix before new capability).
- Progress state: `.agents/evals/progress.md` — update every iteration.
- Fixed goal: `.agents/evals/goal.md` — never soften it.
- Known agent errors + patches: `.agents/evals/errors.md`.
