# AEGIS — Progress Ledger

> Updated by the agent at the end of **every** loop iteration. Compared against
> `.agents/evals/goal.md`. Never rewrite history — append.

## Meta

- **Loop iteration:** 3
- **Last updated:** 2026-11-17 (iter 3)
- **Current phase:** PHASE-3 (core) — Phase 2 complete, contracts gate 7/7 green
- **Next queued action:** Phase 3: `core/scope.py` → `policy.py` → `audit.py` → `mission.py` → `orchestrator.py` + tests
- **Blockers:** none
- **Latest eval run:** 20/30 (67%) — contracts 7/7 ✅, harness ✅, process ✅; safety needs Phase 3

## Phase Checklist

Status legend: `[ ]` not started · `[/]` in progress · `[x]` done (validated) · `[!]` blocked

### Phase 1 — Root & Harness (`.claude/`)

| Item | Status | Evidence / Notes |
|------|--------|------------------|
| `CLAUDE.md` (harness contract, routing, constraints) | [x] | iter 2 — 3.0KB; mission, repo map, epistemic ladder, routing table, loop pointers |
| `pyproject.toml` (deps, tooling, entry points) | [x] | iter 2 — PEP 621, jsonschema dep, aegis CLI entry, ruff/pytest config |
| `README.md` (project overview, architecture) | [x] | iter 2 — architecture diagram + epistemic model table + safety model |
| `.gitignore` (Python, evidence artifacts, secrets) | [x] | iter 2 — evidence/objects ignored, manifests tracked, results raw ignored |
| `.claude/settings.json` (permissions, allowed tools) | [x] | iter 2 — allow/ask/deny tiers; goal.md edits denied; force-push denied |
| `.claude/rules/research.md` | [x] | iter 2 — hypothesis-first; negative results recorded; failure examples |
| `.claude/rules/evidence.md` | [x] | iter 2 — sha256 content addressing, custody, immutability, failure examples |
| `.claude/rules/scope.md` | [x] | iter 2 — resolve-before-contact, deny-by-default, approval gating |
| `.claude/skills/inventory/SKILL.md` | [x] | iter 2 — Understand; components/deps/trust boundaries; coverage gaps |
| `.claude/skills/source-review/SKILL.md` | [x] | iter 2 — Discover; entry→sink paths; anchored hypotheses + verification plans |
| `.claude/skills/finding-triage/SKILL.md` | [x] | iter 2 — Verify/Improve; ladder classification + transition conditions |
| `.claude/agents/systems-analyst.md` | [x] | iter 2 — Understand lead; hand-off contracts to analyst/curator |
| `.claude/agents/source-analyst.md` | [x] | iter 2 — Discover lead; hypotheses only, build on graph |
| `.claude/agents/reviewer.md` | [x] | iter 2 — Verify/Improve gate; adversarial, blocks inflation |
| `.claude/agents/evidence-curator.md` | [x] | iter 2 — evidence integrity + Connect; veto power over broken chains |

### Phase 2 — Contracts (JSON Schemas)

| Item | Status | Evidence / Notes |
|------|--------|------------------|
| `contracts/mission.schema.json` | [x] | iter 3 — targets/exclusions/rules/constraints/approvers; deny-by-default documented |
| `contracts/run.schema.json` | [x] | iter 3 — policy_decisions incl. approver for consequential; workers carry hypotheses |
| `contracts/observation.schema.json` | [x] | iter 3 — raw_evidence minItems 1; no claim fields; method fidelity confidence |
| `contracts/finding.schema.json` | [x] | iter 3 — epistemic ladder + if/then guards (confirmed⇒reproduction, rejected⇒evidence) |
| `contracts/artifact.schema.json` | [x] | iter 3 — sha256 = artifact id; append-only custody chain |

### Phase 3 — Core

| Item | Status | Evidence / Notes |
|------|--------|------------------|
| `core/mission.py` — Mission model, schema-validated load | [ ] | |
| `core/scope.py` — authorization/scope resolver | [ ] | |
| `core/orchestrator.py` — run lifecycle, worker dispatch | [ ] | |
| `core/policy.py` — safety policy, approval gating | [ ] | |
| `core/audit.py` — append-only hash-chained audit log | [ ] | |

### Phase 4 — Adapters

| Item | Status | Evidence / Notes |
|------|--------|------------------|
| `adapters/claude_code/` — agent harness adapter | [ ] | |
| `adapters/codex/` — alternative harness adapter | [ ] | |
| `adapters/mcp/` — MCP server surface | [ ] | |
| `adapters/cli/` — operator CLI | [ ] | |

### Phase 5 — Workers

| Item | Status | Evidence / Notes |
|------|--------|------------------|
| `workers/system_inventory/` | [ ] | |
| `workers/static_analysis/` | [ ] | |
| `workers/application_testing/` | [ ] | |
| `workers/fuzzing/` | [ ] | |
| `workers/binary_analysis/` | [ ] | |
| `workers/firmware/` | [ ] | |
| `workers/qemu/` | [ ] | |
| `workers/renode/` | [ ] | |

### Phase 6 — Evidence & Graph

| Item | Status | Evidence / Notes |
|------|--------|------------------|
| `evidence/manifests/` conventions + README | [ ] | |
| `evidence/objects/` content-addressed store layout | [ ] | |
| `graph/schema.cypher` — full graph model | [ ] | |
| `graph/ingest.py` — evidence → graph ingestion | [ ] | |
| `graph/queries/` — cross-domain pattern queries | [ ] | |

### Phase 7 — Evals (repo-level `evals/`)

| Item | Status | Evidence / Notes |
|------|--------|------------------|
| `evals/test_cases/` — research test corpus | [ ] | |
| `evals/expected_results/` — ground truth per case | [ ] | |
| `evals/harness_benchmarks/` — harness perf/quality benchmarks | [ ] | |

### Phase 8 — UI, Reports & E2E Validation

| Item | Status | Evidence / Notes |
|------|--------|------------------|
| `ui/orb/` — status/visualization surface | [ ] | |
| `reports/` — report templates & conventions | [ ] | |
| End-to-end: mission → run → evidence → finding → graph | [ ] | |
| All eval suites green | [ ] | |

### Phase 9 — `.agents/evals/` Harness (agent-behavior evals)

| Item | Status | Evidence / Notes |
|------|--------|------------------|
| `cases/` — behavior eval cases authored | [ ] | |
| `rubrics/` — grading rubrics for LLM-judged cases | [ ] | |
| `runners/` — executable eval runner(s) | [ ] | |
| `results/` — latest run outputs, pass-rate trend | [ ] | |
| `suites.json` — suite definitions & gates | [ ] | |

## Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Files populated (of 34 + harness) | 100% | 21 (+fixtures/validator) |
| Contracts passing schema self-validation | 5/5 | 5/5 (+1 negative guard) |
| Eval suites defined / passing | 7/7 | 3/7 (contracts, harness, process) |
| Case pass rate (latest run) | ≥ 90% | 67% (in-progress build) |
| E2E verified finding produced | 1 | 0 |

## Decision Log (append-only)

| Date | Iteration | Decision | Rationale |
|------|-----------|----------|-----------|
| 1 | 0 | Normalized `.agents/eval` → `.agents/evals/` | Single source of truth for eval harness + progress/goal |
| 2 | 1 | Built stdlib-only heuristic eval suite at `.agents/evals/eval-suite/` (29 heuristics, 7 suites with gates) | Python env has no third-party packages; stdlib runner guarantees the evals always run. Registry/runner drift fails by design |
| 3 | 1 | curriculum.json is empty (0 bytes) → goal.md ↔ progress.md is the improvement comparator; divergences logged here | E-001 in errors.md; curriculum to be derived from logged decisions |
| 4 | 1 | Branch strategy: one `feat/<phase>` branch per phase, `--no-ff` merge to main, prune after merge | Matches init.md §5 loop; keeps phase boundaries reviewable |
| 5 | 2 | Phase order adjusted: eval suite (Phase 9 core) built first so every later phase lands with measurable gates | goal.md Evolve capability; init.md §5 rule 3 (gates before capability) |
| 6 | 3 | Contracts enforce the epistemic ladder structurally via allOf if/then guards (confirmed⇒reproduction, hypothesis⇒plan, rejected⇒evidence) — plus stdlib mini-validator + fixtures since jsonschema isn't installed | goal.md Verify; deps unavailable in env, stdlib validator guarantees contracts always checkable |
| 7 | 3 | Added `contracts.fixtures-validate` heuristic (29→30) so schema/fixture drift fails the suite | E-002 prevention; registry+runner updated in same commit per drift rule |
| 8 | 3 | Integrated parallel-session work into main at ref level: contracts (016e355) includes vision/ curriculum (P01–P10), populated `.agents/curriculum.json`, rainbow README + WHY.md doc split | User worked concurrently in separate worktrees; ff-verified update-ref is the safe integration path under concurrency |
| 9 | 3 | Loop relocated to dedicated worktree `aegis-loop` (branch `loop/integration`) | E-003; exclusive-custody working tree ends branch-switch races |
| 10 | 3 | `harness.readme-architecture` heuristic now checks README.md + WHY.md as one doc set | User split docs deliberately (rainbow front door + detailed WHY.md); harness adapts to user's structure |

## Blocker Log (append-only)

| Date | Iteration | Blocker | Resolution |
|------|-----------|---------|------------|
| — | — | — | — |
