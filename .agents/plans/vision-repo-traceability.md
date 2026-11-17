# Vision ↔ Repo Traceability Map

Companion to `.agents/curriculum.json` and `progress.md`. Each `vision/0N-*.md`
phase states a goal project and a pass condition; this map names the exact
repo artifact that satisfies (or has not yet attempted) each one, so a
reviewer never has to take "it's done" on faith. Append-only in spirit: when
a phase's status changes, add a row/date rather than silently editing the
verdict (full change history lives in git + `progress.md`'s decision log).

Last updated: 2026-11-17 (iter 7).

## P01 — Laboratory Foundations

| Vision goal project element | Repo artifact | Status |
|---|---|---|
| Isolated lab + scope manifest, no test without valid scope | `core/scope.py` (deny-by-default `ScopeResolver`), `contracts/fixtures/mission.instance.json` | ✅ done |
| Evidence Vault v0.1, SHA-256 content addressing, verify on store+retrieval | `core/evidence.py` (`EvidenceVault`), `evidence/objects/README.md`, `evidence/manifests/README.md` | ✅ done |
| Emergency stop / human-approval path | `core/policy.py` (`PolicyEngine` consequential-action gating), `core/audit.py` (hash-chained, append-only) | ✅ done |
| Research note separating observation/hypothesis/conclusion | `contracts/finding.schema.json` epistemic-ladder guards; `evals/test_cases/case-001-*` | ✅ done |

**Pass condition check:** "a second person can revoke the mission mid-run and re-verify every artifact hash without consulting you" — proven by `evals/e2e_smoke.py` (out-of-scope dispatch denied+audited; artifact hash verifies after store+retrieval) and unit tests in `tests/test_policy_audit.py`. No physical/virtualized lab (VM snapshot/restore) exists — the repo substitutes a synthetic local fixture (`evals/test_cases/fixture-gw-service/`) consistent with research.md's local-authorized-target posture. **Gap:** true VM-level snapshot/restore is not built; not required by any eval gate so far.

## P02 — Systems and Architecture

| Vision goal project element | Repo artifact | Status |
|---|---|---|
| Research CLI skeleton, typed contracts, deterministic fixtures | `adapters/cli/main.py`, `contracts/*.schema.json` (5, draft 2020-12) | ✅ done |
| System Atlas inventory worker, read-only, repeatable | `workers/system_inventory/worker.py` | ✅ done |
| C/memory literacy exercise with sanitizer-backed regression | — | ⛔ not started |
| Protocol/trust-boundary map in a graph | `graph/schema.cypher`, `graph/ingest.py` (both empty stubs) | ⛔ not started — **owned by parallel T1 thread, not this loop** |

**Pass condition check:** inventory repeatability + read-only + source/collection metadata proven in `evals/e2e_smoke.py` and `tests/`. The graph half of the goal project (host/service/process/interface nodes) cannot be marked done until T1 lands — this loop's eval suite's `graph` heuristics stay red by design (decision log #12).

## P03 — Agent Harness Engineering

| Vision goal project element | Repo artifact | Status |
|---|---|---|
| `CLAUDE.md`, rules, skills, session/decision log | `CLAUDE.md`, `.claude/rules/{research,evidence,scope}.md`, `.claude/skills/*`, `.agents/evals/progress.md` | ✅ done |
| 4 agent roles + tool broker + adversarial policy test suite | `.claude/agents/{systems-analyst,source-analyst,reviewer,evidence-curator}.md`, `core/policy.py` + `core/orchestrator.py`, `tests/test_policy_audit.py`, `tests/test_orchestrator.py` | ✅ done |
| Versioned contracts; CLI + MCP adapters on the same contracts; harness run metadata | `adapters/cli/`, `adapters/mcp/`, `contracts/run.schema.json` (`provenance.initiated_by`) | ✅ done |
| **Pass condition: run one identical bounded task through both adapters, compare results, confirm zero policy logic in adapter code** | `evals/mcp_adapter_smoke.py` + `evals/test_cases/case-002-mcp-adapter-parity.yaml` | ✅ done (iter 7) — proven **live**, not just by unit test: scope decisions match core/scope.py exactly across 3 target classes through a real JSON-RPC subprocess; malformed mission rejected server-side before reaching the resolver |

**Note:** case-002 also found and fixed a real defect (MCP `audit_verify` crashed instead of reporting failure on a corrupted chain) — exactly the kind of adversarial-boundary exercise the vision doc anticipates for week 8's test suite, discovered one phase later than the vision timeline because the second adapter path wasn't exercised live until now.

## P04 — Application Security

| Vision goal project element | Repo artifact | Status |
|---|---|---|
| Threat model + trust-boundary graph for a vulnerable local app | — | ⛔ not started |
| Full finding lifecycle (hypothesis → fixed, with patch + regression test) on a real defect | `workers/application_testing/` (interface-complete stub only) | ⛔ not started |

**Blocker:** needs an authorized, deliberately-vulnerable synthetic lab app (curriculum entry gate: "tool broker and scope checks active" — met; the lab itself does not exist). This is T4/P3 in `current-state.md`'s task queue — activation requires human-provisioned synthetic labs, which this loop does not self-authorize (scope.md MUST-NOT-5, mirrored in the P01-P04 transition record).

## P05 — Source Code and Software Supply Chain

| Vision goal project element | Repo artifact | Status |
|---|---|---|
| Semgrep-assisted source review with false-positive triage | `workers/static_analysis/` (interface-complete stub only) | ⛔ not started |
| SBOM + OSV-Scanner reachability verdict | — | ⛔ not started |

**Blocker:** same as P04 — needs a pinned authorized repository target; `static_analysis` wiring is explicitly T4/P3 ("first Discover capability") in the task queue, gated on lab authorization, not on code volume.

## P06 — Fuzzing and Vulnerability Discovery

| Vision goal project element | Repo artifact | Status |
|---|---|---|
| AFL++ campaign, crash classification, minimization, root-cause-to-regression | `workers/fuzzing/` (interface-complete stub only) | ⛔ not started |

**Blocker:** needs a deterministic local fuzz target + authorized campaign budget. No eval gate currently requires this; curriculum phase order is advisory, not enforced ("phase_order_is_default": true, adaptable to demonstrated competency).

## P07 — Reverse Engineering

| Vision goal project element | Repo artifact | Status |
|---|---|---|
| ELF/Ghidra/GDB-based binary investigation with provenance-anchored claims | `workers/binary_analysis/` (interface-complete stub only) | ⛔ not started |

**Blocker:** needs a purpose-built local vulnerable binary + tool availability (Ghidra/GDB) — not verified installed in this environment.

## P08 — Firmware and Hardware Emulation

| Vision goal project element | Repo artifact | Status |
|---|---|---|
| QEMU lab, firmware extraction, Renode simulation, boot-chain model, cross-layer graph | `workers/qemu/`, `workers/firmware/`, `workers/renode/` (all interface-complete stubs only) | ⛔ not started |

**Blocker:** needs emulation tooling + a research-suitable firmware image, plus the graph layer (T1) for the cross-layer merge this phase's goal project requires.

## P09 — AI-Agent Security

| Vision goal project element | Repo artifact | Status |
|---|---|---|
| Prompt-injection resistance suite against AEGIS's own harness | `.claude/rules/*`, `core/policy.py` exist as the thing *to be* red-teamed, but no adversarial test suite targets them yet | ⛔ not started |
| MCP tool-permission matrix tests (mock overbroad tools, confused-deputy) | `evals/mcp_adapter_smoke.py` exercises MCP for *interface parity*, not adversarial tool-description abuse | ⚠️ partially adjacent, not the goal project |
| Model/harness benchmark (Haiku/Sonnet/Opus/Fable compared) | `evals/harness_benchmarks/benchmarks.yaml` + `run_benchmarks.py` measure the **harness**, not comparative model performance | ⚠️ infrastructure exists, comparison study does not |

**Note:** this is the phase where the curriculum's own instrumentation (this repo's benchmarks + eval suite) becomes the substrate P09 turns on itself. The P07/iter-7 benchmark wiring is directly reusable here once P09 is unlocked.

## P10 — Research Platform Capstone

| Vision goal project element | Repo artifact | Status |
|---|---|---|
| AEGIS v0.9 integrated workflow (all workers behind broker, graph populated, Orb live) | `ui/orb/` (status surface, graph-viz deferred to T1), `core/orchestrator.py` | ⚠️ partially — Orb exists graph-independently; full integration needs P04–P08 workers + T1 graph |
| Cross-layer research case + independent review | `evals/e2e_smoke.py` proves one graph-independent evidence-backed finding end-to-end | ⚠️ definition-of-done met graph-independently (see `.agents/state/phase-8-state-*.md`); cross-layer (software+binary+firmware+emulated) case not attempted |
| Clean-room reproduction (v1.0 release candidate) | — | ⛔ not started |

---

## Summary

- **P01–P03 (harness build):** fully traced, done, and — as of iter 7 — P03's exit criterion is proven *live* through both adapters, not just asserted by unit test.
- **P04–P08 (capability phases):** uniformly blocked on the same two things: (1) human-authorized synthetic labs per phase (no self-authorization — scope.md MUST-NOT-5), and (2) for P08 specifically, also the T1 graph layer. Stubs are interface-complete and intentionally raise `NotImplementedError` rather than fabricating output (each stub's `WORKER.md` + `worker.py`, e.g. `workers/static_analysis/worker.py`).
- **P09:** partially adjacent infrastructure exists (MCP parity smoke, benchmark harness) but the actual red-team-the-harness goal project has not been attempted.
- **P10:** the graph-independent slice of "done" is proven (phase-8 E2E); the full capstone needs P04–P09 plus T1.

This map should be re-generated (new dated section, not an edit) whenever a phase transition is recorded in `progress.md`'s Phase Transition Records ledger.
