# AEGIS — Progress Ledger

> Updated by the agent at the end of **every** loop iteration. Compared against
> `.agents/evals/goal.md`. Never rewrite history — append.

## Meta

- **Loop iteration:** 6
- **Last updated:** 2026-11-17 (iter 6; merged with `feat/curriculum-test-suite-p01-p03` test-suite/CI thread — decision row 21)
- **Current phase:** PHASE-3 RECONCILIATION — main's Phase 2/3 are complete against the dataclass API; decision row 20 commits to porting that core to the pydantic/contract API (`tests/unit/`, `tests/test_*.py`) before Phase 3 can be marked done against this branch's acceptance bar. Phase 8 (graph leg) status below is otherwise unchanged from main.
- **Next queued action:** Begin T1 (contracts conformance — 13 remaining failures against curriculum) then T2–T7 (port `core/audit.py` → `core/orchestrator.py` to pydantic) per revised triage in `state/pytest-state-20261117T110041.md` §Addendum
- **Blockers:** none — graph gate owned by parallel thread
- **Latest eval run:** 27/30 (90%) — rerun on the merged tree, same gate state as main (graph still 0/3, delegated); pytest on the merged tree: 310 collected / 90 passed / 212 failed / 8 errors (up from 263/18 pre-merge; `tests/legacy/` regression net adds coverage against main's still-live dataclass core)
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
| `core/jsonschema_lite.py` + `core/evidence.py` + `tests/` (31 tests) | [x] | iter 4 — single-source validator; evidence vault with store/retrieval hash verification (P01/W2 exits); iter 7 — validator now delegates to real `jsonschema` when installed, stdlib subset remains the fallback, same API |

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
| `evals/test_cases/` — research test corpus | [x] | iter 5 — case-001 (curriculum P01/P02-aligned) + synthetic gw-service fixture; iter 7 — case-002 (P03 harness-interface-parity, no network) |
| `evals/expected_results/` — ground truth per case | [x] | iter 5 — case-001-expected: h1 stays hypothesis (no reproduction), h2 confirmed; iter 7 — case-002-expected: h3/h4 confirmed live |
| `evals/harness_benchmarks/` — harness perf/quality benchmarks | [x] | iter 5 — 5 benchmarks defined incl. triage inflation guard + deny-by-default behavior; iter 7 — 3 of 5 wired to real runner output (`run_benchmarks.py`) |
| `evals/mcp_adapter_smoke.py` — second interface proven live | [x] | iter 7 — 10/10 PASS: adapters/mcp scope_check reproduces core/scope.py decisions exactly across 3 target classes; audit_verify fix (see below) |

### Phase 8 — UI, Reports & E2E Validation

| Item | Status | Evidence / Notes |
|------|--------|------------------|
| `ui/orb/` — status/visualization surface | [x] | iter 6 — static self-contained status.html + status.json from eval results; read-only over repo state |
| `reports/` — report templates & conventions | [x] | iter 6 — canonical template 1:1 with finding schema; render_finding.py validates BEFORE rendering |
| End-to-end: mission → run → evidence → finding → graph | [x] | iter 6 — `evals/e2e_smoke.py` 14/14 PASS: scope deny+audit, inventory→vault→observation, h1 hypothesis + h2 confirmed, all contracts validate, audit chain verifies, report renders; GRAPH LEG deferred to T1 owner |
| All eval suites green | [x] | iter 6 — all 6 loop-owned suites 100%; graph suite external by delegation |

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
| Files populated (of 34 + harness) | 100% | 34/34 loop-owned (graph ×3 external; reports+ui+e2e added) |
| Contracts passing schema self-validation | 5/5 | 5/5 (+1 negative guard) |
| Eval suites defined / passing | 7/7 | 6/6 owned green (graph externally owned) |
| Case pass rate (latest run) | ≥ 90% | 91% (29/32; graph red = external) |
| Unit tests | green | 47/47 |
| E2E verified finding produced | 1 | 1 (e2e_smoke: h2 confirmed, full evidence chain) |

## Phase Transition Records (append-only)

Per `curriculum.json` → `header_agent_instructions.progressive_disclosure.transition_record`
and `curriculum_control.phase_transition_requires`. Each record is immutable; a
corrected transition is superseded by a new record, never edited in place.

### P01–P03 → P04 (harness build → research-capability activation)

| Field | Value |
|-------|-------|
| Transition | P01 Laboratory foundations, P02 Systems & architecture, P03 Agent harness engineering → P04 (first Discover-capability phase) |
| Date / Iteration | 2026-11-17 / iter 7 |
| Completed gate (objective, evidence-backed) | P01: `core/scope.py` deny-by-default + exclusions-first (scope suite 5/5), `core/evidence.py` content-addressed vault with hash verify on store+retrieval (evidence suite 3/3), emergency-stop = policy-gated consequential actions (`core/policy.py`, safety suite 5/5). P02: adapters (`claude_code`, `codex`, `mcp`, `cli`) consume the same 5 canonical contracts with zero core logic duplicated (harness suite 7/7); `orchestrator.py` blocks out-of-scope dispatch and evidence-free observations, attributable to mission+run (`provenance.initiated_by`, caught + fixed in iter 6). P03: CLI (`adapters/cli`) validates mission input, emits schema-valid output, fails safely on malformed input (contracts suite 7/7); `workers/system_inventory` repeatable read-only collection with source/collection metadata on every observation (research suite 2/2, process suite 3/3). |
| Supporting runs | 47/47 unit tests · eval-suite 27/30 (6/6 loop-owned suites 100%, graph suite external/T1) · `evals/e2e_smoke.py` 14/14 (one evidence-backed `confirmed` finding, full custody chain, audit verifies) |
| Independent reviewer outcome | Self-reviewed against `curriculum.json` phase `acceptance_criteria` arrays for P01/P02/P03 (cross-checked field-by-field above) by the loop agent acting in the `reviewer` capacity: PASS on every listed criterion for the harness-build scope. No `reviewer` sub-agent was separately dispatched this iteration — recorded here as a limitation, not elided. |
| Unresolved issues | (1) Graph leg of E2E remains delegated to the T1 parallel thread — P04+ work that depends on graph-backed queries is blocked until T1 lands. (2) User's `feat/curriculum-test-suite-p01-p03` branch is still WIP on the primary tree — not yet folded. (3) `workers/` P04–P08 remain interface-complete stubs; no real Discover-capability execution has occurred. |
| Human / curriculum-controller approval | **Pending.** Per `scope.md` MUST-NOT-5 and goal.md's anti-inflation stance, this agent does not self-authorize unlocking P04 execution authority (synthetic lab provisioning, live worker activation). This record documents that the P01–P03 *harness-build* gate is objectively met; a human must still approve provisioning an authorized synthetic lab before any P04 worker (`static_analysis`, `application_testing`, …) executes against a target. Content disclosure of P04's one-sentence phase outcome is permitted now (`future_preview`); detailed P04 briefs stay locked until that approval is recorded. |

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
| 16 | 6 | Loop seat re-established at `aegis-loop2` after external restructure pruned `aegis-loop`; uncommitted reports/ui files salvaged into the new worktree | E-007; repo restructured by parallel thread (origin added, user test-suite branch WIP on primary tree) |
| 17 | 6 | Phase 8 executed graph-independently: E2E smoke proves everything except graph ingestion; report renderer validates before rendering; run contract now carries `provenance` on the run record | goal.md "done" requires E2E; graph leg (T1) owned by parallel thread, integration queued |
| 18 | 6 | `orchestrator.start_run()` records `provenance.initiated_by` | run.schema.json requires provenance; smoke validation caught the gap |
| 19 | — | Added failing-first pytest suite (263 tests) + GitHub Actions CI (tests/evals/ratchet jobs) + gate ratchet on `feat/test-suite-ci`; state snapshot in `state/pytest-state-20261117T110041.md` | goal.md §Evolve: regressions caught in CI; gates tighten monotonically via `tests/thresholds.json` + `tools/ci/check_ratchet.py`; two-thread collision resolved by adopting the pydantic/PolicyEngine conftest API |
| 20 | — | Data model policy: **Pydantic wherever possible**, not stdlib (`CLAUDE.md` §Data model policy + `tests/README.md`) — resolves state-snapshot triage decision in favor of Option B | Curriculum P02.W3 requires "versioned Pydantic models and JSON Schema contracts"; conftest payload builders are the canonical fixtures; dataclass-era `core/` on main migrates rather than widens |
| 21 | — | Merged `main` (through `b0b6394`) into `feat/curriculum-test-suite-p01-p03` (triage T9); main's dataclass-era `core/*.py` + populated `contracts/*.schema.json` now present on this branch, superseding the empty stubs rows 1–18 describe as `[ ]`/`[x]` from the pre-merge perspective | state/pytest-state snapshot addendum; conflicts (progress.md, 2 eval-result files, tests/__init__.py, tests/test_scope.py, tests/test_evidence.py) resolved by: taking main's ledger/result data, union of `__init__.py` docstrings, keeping both HEAD's target-API specs and main's current-API specs (renamed into `tests/legacy/`) as a regression net until the Option B port (row 20) lands |
| 22 | 7 | Recorded P01–P03 → P04 phase transition in the ledger per `transition_record` contract; human approval marked pending rather than assumed | `scope.md` MUST-NOT-5 — agent must not self-authorize; curriculum's progressive-disclosure gate requires a recorded approval, not an inferred one |
| 23 | 7 | Wired `bench-evidence-chain-completeness` + `bench-deny-by-default-behavior` + `bench-time-to-first-verified-finding` to real `evals/e2e_smoke.py` output via new `evals/harness_benchmarks/run_benchmarks.py`; left `bench-triage-accuracy`/`bench-provenance-recall` explicitly `not_wired` rather than faked | goal.md P2 backlog item; research.md MUST-NOT-4 (never report activity metrics as results) extends to never reporting an absent measurement as a result |
| 24 | 7 | Added case-002 (`evals/mcp_adapter_smoke.py`): proved live, not just unit-tested, that `adapters/mcp` reproduces `core/scope.py` scope decisions exactly for all 3 target classes. Discovered + fixed a real bug in the process: `aegis.audit_verify` crashed the MCP server on a corrupted chain instead of reporting `ok=false`, because `core/audit.AuditLog` raises `AuditCorruptionError` eagerly on load (intentional, tested fail-closed behavior) and the server didn't catch it | P03 exit "two interfaces consume the same canonical contracts" — never actually exercised live through the adapter before this; the crash was a genuine harness defect, not a hypothetical |
| 25 | 7 | Authored `.agents/plans/vision-repo-traceability.md`: phase-by-phase map of each `vision/0N-*.md` goal project to its concrete repo artifact and status (done/blocked/not-started), with explicit blockers named (lab authorization for P04-P08, T1 graph for P02/P08/P10) | goal.md T8 backlog item; makes "what's actually done vs. what's stubbed" independently checkable without re-reading every vision doc and every worker stub |
| 26 | 7 | `core/jsonschema_lite.py` now delegates to the real `jsonschema` package when installed (confirmed byte-for-reason parity against all 6 fixtures first), falling back to the stdlib subset validator — same `validate()`/`ValidationError` API either way, zero caller changes. Verified 47/47 tests + 29/32 evals + e2e/mcp smokes pass identically under both plain `python3` and a local `.venv` with deps installed. Did not swap the CLI to typer (lower value, more surface, argparse already works and is tested) | T5/P3 backlog ("swap mini-validator→jsonschema behind same API"); `jsonschema` is already a non-optional pyproject.toml dependency, so this closes the gap between the manifest's stated dependency and what the code actually used when present, while preserving the stdlib-only guarantee (decision log #2/#15) for environments without it |
| 27 | 7 | Merged `main` (through d0685b1/1ba5443/5b08635 — pydantic-first policy, pytest+CI thread, T6 integration) into this iter-7 work; only the 3 append-only ledger/result files conflicted, resolved by concatenating both threads' rows in commit order rather than picking one side | User approved ("Yes to main"); confirms T6 (feat/curriculum-test-suite-p01-p03) was already folded into main by the other thread before this merge — nothing further needed there |

## Blocker Log (append-only)

| Date | Iteration | Blocker | Resolution |
|------|-----------|---------|------------|
| — | — | — | — |
