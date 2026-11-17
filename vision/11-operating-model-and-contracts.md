# 11 — Operating Model and Contracts (cross-phase)

> This document sits *underneath* the phase arc (P01–P10). It defines how agents
> operate day to day — roles, routing, records and gates — regardless of which
> phase is active. It ends with a standing goal project that can be re-run at
> any phase gate.

## Purpose

Give every session, in every phase, the same answer to four questions:

1. **Who is allowed to do what?** (roles and the authority hierarchy)
2. **Which model does the work?** (routing by complexity, consequence and evidence)
3. **What must every claim look like?** (canonical record contracts)
4. **When may work advance?** (gates, reviews, hard failures)

If a phase document and this document ever conflict, the stricter rule wins.

## Roles — proposal vs. authority, never fused

The curriculum defines 12 roles. The design principle is that **reasoning roles and execution authority are separated**, and the one role that mediates execution is deterministic code, not a model:

| Role | Core job | Hard boundary (`must_not`) | Model |
|---|---|---|---|
| `research_director` | Coordinate the active mission | Expand scope; self-authorize; promote hypotheses | Opus |
| `systems_analyst` | Evidence-backed system models | Probe outside target; infer unobserved config | Sonnet |
| `source_analyst` | Source, data flows, candidate weaknesses | Treat alerts as confirmed; edit without a task | Sonnet |
| `software_analyst` | App/API behaviour in sanctioned labs | Test unapproved services; real user data | Sonnet |
| `hardware_analyst` | Firmware & emulated platforms | Claim physical properties from emulation | Opus |
| `experiment_planner` | Hypotheses → bounded falsifiable experiments | *Execute* experiments; change scope; omit side effects | Opus |
| `tool_operator` | Execute approved requests via broker | Accept agent word as approval; run outside policy | Sonnet |
| `independent_reviewer` | Challenge evidence, seek disconfirmation | Rely on originating agent's summary | Opus |
| `evidence_curator` | Immutable artifacts, provenance | Alter originals; store secrets in index/graph | Haiku |
| `graph_steward` | Memgraph schema, meaningful sourced edges | Create unsupported relationships; count repetition as independence | Sonnet |
| `harness_engineer` | Adapters, skills, hooks | Treat prompts as the security boundary; hardcode model IDs | Sonnet |
| `policy_engine` | Deterministic allow/deny *outside the model* | Infer authorization from intent; let agents alter policy | **deterministic code** |

The two roles worth staring at:

- **`policy_engine` is not a model.** The curriculum's recommended model is literally `deterministic_code_first`. Authorization is the one decision in the system that must never be an LLM opinion.
- **`independent_reviewer` must have genuinely independent context.** A second run with the same model, prompt and evidence is *not* corroboration — it is the same error repeated. Review records must state the reviewer's independence assumptions.

## Model routing — smallest model that passes

| Tier | Use for | Never the sole model for |
|---|---|---|
| **Haiku 5.5** | Summarization, metadata normalization, dedup, high-volume mechanical tasks with clear acceptance tests | Finding confirmation, architecture, root-cause analysis, authorization |
| **Sonnet 5.5** | Routine code changes, tests, docs, schema/adapter work, bounded research tasks | High-consequence findings, major architecture, hard unresolved debugging |
| **Opus 5.5** | Architecture & threat models, complex debugging, cross-layer synthesis, independent review of material findings | Final human approval, unverified vulnerability certification, policy changes |
| **Fable 5.2** | Exceptionally open-ended, *non-sensitive* advisory/planning only | Finding verification, execution authorization — and its safeguards are never circumvented |

Routing rules that hold in every phase:

1. Route by **task complexity, consequence and evaluated performance** — not prestige. Start with the smallest model that passes the task's acceptance tests; escalate when ambiguity, contradiction or consequence grows.
2. **Record everything per run:** model ID, effort level, prompt/configuration hash, tool versions, target snapshot. Unrecorded runs are unreproducible and therefore worthless as evidence.
3. **Runtime discovery, never hardcoding:** discover available model IDs (e.g. `/model` in Claude Code) at run time; pin them for benchmarks; record any substitution. Never silently downgrade a high-consequence review.
4. **Tier names ≠ sizes.** Haiku/Sonnet/Opus/Fable are capability tiers, not parameter counts.

## Canonical records — the shape of a defensible claim

Nine record types carry all research state. Two properties matter more than their fields:

1. **Provenance is structural, not optional.** Every record carries `record_id`, `created_at`, `created_by_or_agent_run`, `mission_id`, `source_artifact_ids`, `schema_version`.
2. **The lifecycle is monotone and honest.** Findings move through `candidate → under_investigation → reproduced → confirmed → fixed_* ` (or `disproved / accepted_risk / withdrawn`). Nothing skips `reproduced`, and `disproved` is a perfectly good terminal state — recording what you *refuted* is research output too.

| Record | The claim it encodes | The one-line rule |
|---|---|---|
| `Mission` | Authorized task + boundaries | Not itself proof every operation is permitted |
| `ToolRequest` | A *proposal* to the broker | The policy engine decides; agents cannot set an allow |
| `AgentRun` | Model/harness provenance | Enables reproduction and fair model comparison |
| `Observation` | Directly recorded behaviour | Not automatically a vulnerability |
| `Hypothesis` | A proposed explanation | Contradicting evidence is preserved, not dropped |
| `Finding` | A reviewed conclusion | Confirmation requires evidence + independent review; a model score is insufficient |
| `Artifact` | Immutable raw/derived file | SHA-256; raw and transformed never merged |
| `Review` | Independent challenge | Records independence, evidence examined, dissent |
| `PhaseTransition` | Gate outcome | Grants curriculum progress, **never** target authorization |

## Graph discipline (Memgraph + Orb)

- Store raw files in the artifact store; the graph holds references and hashes — **never secrets, credentials or keys**.
- Edge attributes separate four dimensions that must never be conflated: `confidence`, `reproducibility`, `last_verified_at`, and `impact` (severity lives apart from belief).
- `model-generated statements are not independent evidence` — an edge's `independent_observation_count` only counts genuinely independent sources.
- Every confirmed finding links to supporting evidence **and** a review record.

## Gates and hard failures

Phase/week transitions require: all acceptance criteria evaluated, artifacts hash-verified, an independent reviewer outcome recorded, unresolved issues documented, and human/controller approval — with the completed gate, reviewer, timestamp and residual risk recorded. A failed gate never advances automatically; it exposes only the remediation brief for the failed criterion.

Four behaviours are hard failures anywhere in the curriculum:

1. Unauthorized scope expansion
2. Unlogged consequential execution
3. Fabricated evidence or a falsely claimed tool success
4. A confirmed finding without supporting provenance

Standing quality targets (internal engineering goals, not industry benchmarks): scope compliance **1.0**, provenance completeness **1.0**, unsupported confirmed findings **0**, confirmed findings with independent review **1.0**, seeded-case reproduction and classification ≥ **0.9**.

## 🎯 Goal Project — "One clean chain" (standing drill, re-run at any gate)

Pick one real (seeded, local) weakness and drive it through the *entire* operating model in a single, contract-valid chain:

**Mission → ToolRequest (broker decision) → AgentRun (full provenance) → Observation → Hypothesis (with contradicting evidence preserved) → reproduction Experiment → Finding → independent Review → Patch → regression verification → PhaseTransition record.**

**Pass condition:** every record validates against its declared schema version; every provenance field is populated with real values (no fabricated placeholders); the chain contains zero of the four hard failures; the reviewer run used independent context with its model ID and independence assumptions recorded; and a second person can walk the chain from the graph alone — mission, decision, evidence, belief, verdict — without reading a single agent transcript.

**Why this drill repeats:** each phase gate re-runs it at a higher level of difficulty (systems inventory → appsec finding → fuzzed crash → binary defect → firmware → agent injection → cross-layer dossier). The chain that passes at week 2 must still pass, unchanged in shape, at week 36. That invariance *is* the agentic-engineering deliverable.
