# AEGIS — Progress Ledger

> Updated by the agent at the end of **every** loop iteration. Compared against
> `.agents/evals/goal.md`. Never rewrite history — append.

## Meta

- **Loop iteration:** 2
- **Last updated:** 2026-11-17 (iter 2)
- **Current phase:** PHASE-2 (contracts) — Phase 1 complete, harness gate 7/7 green
- **Next queued action:** Phase 2: author 5 JSON Schemas (draft 2020-12) + fixtures + validator
- **Blockers:** none
- **Latest eval run:** 12/29 (41%) — harness 7/7 ✅, process 3/3 ✅; red gates are Phases 2,3,5,6,7 work

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
| `contracts/mission.schema.json` | [ ] | |
| `contracts/run.schema.json` | [ ] | |
| `contracts/observation.schema.json` | [ ] | |
| `contracts/finding.schema.json` | [ ] | |
| `contracts/artifact.schema.json` | [ ] | |

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
| Files populated (of 34 + harness) | 100% | 15 |
| Contracts passing schema self-validation | 5/5 | 0 |
| Eval suites defined / passing | 7/7 | 2/7 (harness, process) |
| Case pass rate (latest run) | ≥ 90% | 41% (in-progress build) |
| E2E verified finding produced | 1 | 0 |

## Decision Log (append-only)

| Date | Iteration | Decision | Rationale |
|------|-----------|----------|-----------|
| 1 | 0 | Normalized `.agents/eval` → `.agents/evals/` | Single source of truth for eval harness + progress/goal |
| 2 | 1 | Built stdlib-only heuristic eval suite at `.agents/evals/eval-suite/` (29 heuristics, 7 suites with gates) | Python env has no third-party packages; stdlib runner guarantees the evals always run. Registry/runner drift fails by design |
| 3 | 1 | curriculum.json is empty (0 bytes) → goal.md ↔ progress.md is the improvement comparator; divergences logged here | E-001 in errors.md; curriculum to be derived from logged decisions |
| 4 | 1 | Branch strategy: one `feat/<phase>` branch per phase, `--no-ff` merge to main, prune after merge | Matches init.md §5 loop; keeps phase boundaries reviewable |
| 5 | — | Added failing-first pytest suite (263 tests) + GitHub Actions CI (tests/evals/ratchet jobs) + gate ratchet on `feat/test-suite-ci`; state snapshot in `state/pytest-state-20261117T110041.md` | goal.md §Evolve: regressions caught in CI; gates tighten monotonically via `tests/thresholds.json` + `tools/ci/check_ratchet.py`; two-thread collision resolved by adopting the pydantic/PolicyEngine conftest API |

## Blocker Log (append-only)

| Date | Iteration | Blocker | Resolution |
|------|-----------|---------|------------|
| — | — | — | — |
