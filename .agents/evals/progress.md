# AEGIS — Progress Ledger

> Updated by the agent at the end of **every** loop iteration. Compared against
> `.agents/evals/goal.md`. Never rewrite history — append.

## Meta

- **Loop iteration:** 0
- **Last updated:** —
- **Current phase:** NOT-STARTED
- **Next queued action:** Read `.agents/plans/init.md` §3 and begin Phase 1 (harness population)
- **Blockers:** none

## Phase Checklist

Status legend: `[ ]` not started · `[/]` in progress · `[x]` done (validated) · `[!]` blocked

### Phase 1 — Root & Harness (`.claude/`)

| Item | Status | Evidence / Notes |
|------|--------|------------------|
| `CLAUDE.md` (harness contract, routing, constraints) | [ ] | |
| `pyproject.toml` (deps, tooling, entry points) | [ ] | |
| `README.md` (project overview, architecture) | [ ] | |
| `.gitignore` (Python, evidence artifacts, secrets) | [ ] | |
| `.claude/settings.json` (permissions, allowed tools) | [ ] | |
| `.claude/rules/research.md` | [ ] | |
| `.claude/rules/evidence.md` | [ ] | |
| `.claude/rules/scope.md` | [ ] | |
| `.claude/skills/inventory/SKILL.md` | [ ] | |
| `.claude/skills/source-review/SKILL.md` | [ ] | |
| `.claude/skills/finding-triage/SKILL.md` | [ ] | |
| `.claude/agents/systems-analyst.md` | [ ] | |
| `.claude/agents/source-analyst.md` | [ ] | |
| `.claude/agents/reviewer.md` | [ ] | |
| `.claude/agents/evidence-curator.md` | [ ] | |

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
| Files populated (of 34 + harness) | 100% | 0 |
| Contracts passing schema self-validation | 5/5 | 0 |
| Eval suites defined / passing | 4/4 | 0/0 |
| Case pass rate (latest run) | ≥ 90% | n/a |
| E2E verified finding produced | 1 | 0 |

## Decision Log (append-only)

| Date | Iteration | Decision | Rationale |
|------|-----------|----------|-----------|
| 1 | 0 | Normalized `.agents/eval` → `.agents/evals/` | Single source of truth for eval harness + progress/goal |

## Blocker Log (append-only)

| Date | Iteration | Blocker | Resolution |
|------|-----------|---------|------------|
| — | — | — | — |
