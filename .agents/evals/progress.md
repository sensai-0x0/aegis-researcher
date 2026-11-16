# AEGIS — Progress Ledger

> Updated by the agent at the end of **every** loop iteration. Compared against
> `.agents/evals/goal.md`. Never rewrite history — append.

## Meta

- **Loop iteration:** 5
- **Last updated:** 2026-11-17 (iter 5)
- **Current phase:** PHASE-8 next (ui/orb, reports, E2E demo) — Phases 4, 5, 7 complete; graph externally owned
- **Next queued action:** Phase 8: `ui/orb` status surface, `reports/` templates, then E2E demo (mission → run → evidence → finding → graph → report)
- **Blockers:** none — graph gate owned by parallel thread
- **Latest eval run:** 27/30 (90%) — 6/6 owned suites green; 47 unit tests green
- **Curriculum alignment:** P01 (evidence vault) pulled forward into iter 4 per `.agents/curriculum.json`; P03 exits govern Phase 4 adapters; progressive disclosure honored (P04+ details not preloaded)

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
| `core/mission.py` — Mission model, schema-validated load | [x] | iter 4 — loads+validates via jsonschema_lite; rejects non-active missions |
| `core/scope.py` — authorization/scope resolver | [x] | iter 4 — deny-by-default; exclusions first; CIDR/host/app/component matching; 8 unit tests |
| `core/orchestrator.py` — run lifecycle, worker dispatch | [x] | iter 4 — state machine; refuses out-of-scope; refuses observations without evidence |
| `core/policy.py` — safety policy, approval gating | [x] | iter 4 — read_only/intrusive/consequential; approver must be in mission; all decisions audited |
| `core/audit.py` — append-only hash-chained audit log | [x] | iter 4 — sha256 chain, tamper detection on reload, no removal API (test-enforced) |
| `core/jsonschema_lite.py` + `core/evidence.py` + `tests/` (31 tests) | [x] | iter 4 — single-source validator; evidence vault with store/retrieval hash verification (P01/W2 exits) |

### Phase 4 — Adapters

| Item | Status | Evidence / Notes |
|------|--------|------------------|
| `adapters/claude_code/` — agent harness adapter | [x] | iter 5 — routing table, zero core logic, harness-neutral reports |
| `adapters/codex/` — alternative harness adapter | [x] | iter 5 — same canonical contracts, P03 exit verified by test |
| `adapters/mcp/` — MCP server surface | [x] | iter 5 — JSON-RPC 2.0 stdio; scope_check validates contract server-side; fail-closed |
| `adapters/cli/` — operator CLI | [x] | iter 5 — argparse (stdlib); mission validate / scope check / audit verify; entry fixed in pyproject |

### Phase 5 — Workers

| Item | Status | Evidence / Notes |
|------|--------|------------------|
| `workers/system_inventory/` | [x] | iter 5 — implemented: local tree → sha256 artifact + evidenced observations; hypothesis guard |
| `workers/static_analysis/` | [x] | iter 5 — interface-complete stub (curriculum P05) |
| `workers/application_testing/` | [x] | iter 5 — interface-complete stub (curriculum P04) |
| `workers/fuzzing/` | [x] | iter 5 — interface-complete stub (curriculum P06) |
| `workers/binary_analysis/` | [x] | iter 5 — interface-complete stub (curriculum P07) |
| `workers/firmware/` | [x] | iter 5 — interface-complete stub (curriculum P08) |
| `workers/qemu/` | [x] | iter 5 — interface-complete stub (curriculum P08) |
| `workers/renode/` | [x] | iter 5 — interface-complete stub (curriculum P08) |

### Phase 6 — Evidence & Graph

| Item | Status | Evidence / Notes |
|------|--------|------------------|
| `evidence/manifests/` conventions + README | [x] | iter 4 — pulled forward per curriculum P01/W2 (evidence vault before workers) |
| `evidence/objects/` content-addressed store layout | [x] | iter 4 — immutability + content addressing + vault helper core/evidence.py |
| `graph/schema.cypher` — full graph model | [!] | DELEGATED to parallel thread (human instruction, iter 5) |
| `graph/ingest.py` — evidence → graph ingestion | [!] | DELEGATED to parallel thread |
| `graph/queries/` — cross-domain pattern queries | [!] | DELEGATED to parallel thread |

### Phase 7 — Evals (repo-level `evals/`)

| Item | Status | Evidence / Notes |
|------|--------|------------------|
| `evals/test_cases/` — research test corpus | [x] | iter 5 — case-001 (curriculum P01/P02-aligned) + synthetic gw-service fixture |
| `evals/expected_results/` — ground truth per case | [x] | iter 5 — case-001-expected: h1 stays hypothesis (no reproduction), h2 confirmed |
| `evals/harness_benchmarks/` — harness perf/quality benchmarks | [x] | iter 5 — 5 benchmarks incl. triage inflation guard + deny-by-default behavior |

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
| Files populated (of 34 + harness) | 100% | 33 of 34 (graph ×3 external, rest populated incl. tests/adapters/workers) |
| Contracts passing schema self-validation | 5/5 | 5/5 (+1 negative guard) |
| Eval suites defined / passing | 7/7 | 6/6 owned green (graph externally owned) |
| Case pass rate (latest run) | ≥ 90% | 90% (27/30; graph red = external) |
| Unit tests | green | 47/47 |
| E2E verified finding produced | 1 | 0 (Phase 8) |

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
| 11 | 4 | Curriculum comparison applied: P01 evidence vault pulled forward (done iter 4); P03 exits adopted as Phase 4 acceptance; P04+ details NOT preloaded (progressive disclosure) | `.agents/curriculum.json` is now the authoritative curriculum; header_agent_instructions govern agent behavior |
| 12 | 5 | Phase 6 (graph) delegated to a parallel thread by human instruction; this loop skips it and does not chase the graph gate | Avoids duplicate/conflicting graph work across sessions |
| 13 | 5 | Phase 4 accepted against curriculum P03 exits, encoded as tests: two interfaces same contracts, zero core logic in adapters, fail-closed registry | `.agents/curriculum.json` exit criteria → executable acceptance |
| 14 | 5 | MCP `aegis.scope_check` now validates the mission against the contract server-side before resolving scope | Test caught the gap; "interfaces consume the same canonical contracts" means validating them too |
| 15 | 5 | CLI uses stdlib argparse; pyproject entry corrected to `adapters.cli.main:main` | Deps not installed in env; honest minimal tooling until venv deps land (typer stays in extras) |

## Blocker Log (append-only)

| Date | Iteration | Blocker | Resolution |
|------|-----------|---------|------------|
| — | — | — | — |
