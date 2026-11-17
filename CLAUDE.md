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

## Data model policy (pydantic-first)

Use **Pydantic wherever possible** instead of stdlib dataclasses/plain dicts for
data shapes:

1. Every canonical record type (Mission, Scope, ToolRequest, AgentRun, Observation,
   Hypothesis, Finding, Artifact, Review, …) is a **Pydantic model** that mirrors
   its JSON Schema in `contracts/`. Validate with `model_validate`; serialize with
   `model_dump(mode="json")` — never hand-map dicts.
2. Models are **closed** (`model_config = ConfigDict(extra="forbid")`) and mirror
   the schema exactly — no undeclared fields, no authority fields on agent-facing
   records.
3. Parsers, policy decisions, graph records and CLI I/O accept/emit Pydantic
   models; timestamps and clocks are injectable dependencies, not `datetime.now()`
   calls scattered through logic.
4. Stdlib `dataclass`/dict shapes are the exception, allowed only for genuinely
   unsuitable cases (e.g. performance-critical inner loops) — and each one needs a
   comment justifying why Pydantic was not used.
5. When touching code that predates this rule (e.g. dataclass-era `core/`), migrate
   to Pydantic in the same change set rather than widening the stdlib API.

Canonical test payloads live in `tests/conftest.py` (`*_payload` builders); models
must validate them and reject field-drop/extra-field variants (see
`tests/unit/test_contract_roundtrip.py`).

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
