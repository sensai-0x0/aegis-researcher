# AEGIS

**A continuously evolving, evidence-driven security research intelligence platform** that
develops a deep, verifiable understanding of software, hardware and AI-agent systems.

Every research activity compounds upon the last:

**Understand** accurate models → **Discover** weaknesses via hypothesis-driven research →
**Verify** through reproducible evidence → **Improve** root causes + mitigations →
**Connect** a provenance-rich knowledge graph → **Evolve** research accuracy and agent
reliability without compromising authorization, safety or evidence integrity.

> **North Star:** advance human understanding of system security. Optimize for verified
> knowledge, reproducibility and cumulative discovery — never activity, tool usage or
> the volume of reported vulnerabilities.

## Architecture

```
                    ┌──────────────────────────────────────────────┐
                    │                     UI                       │
                    │  mission → scope/policy gate → orchestrator →│ workers
                    │        ↓                                     │ (inventory,
                    │   evidence/  ←  observations  ←  artifacts   │  static, fuzz,
                    │        ↓                                     │  binary, fw,
                    │   observations → findings (triage)           │  qemu, renode)
                    │        ↓                                     │
                    │   graph/ ← ingest ← audit chain              │
                    │        ↓                                     │
                    │   reports/ + evals/ (test corpus, ground     │
                    │              truth, harness benchmarks)      │
                    └──────────────────────────────────────────────┘
```

## The epistemic model

AEGIS enforces three tiers of claim strength, and every tier transition requires
evidence:

| Tier | Meaning | Required by contract |
|------|---------|----------------------|
| **Observation** | A reproducible fact: a method run against a target, producing artifacts | ≥1 artifact reference |
| **Hypothesis** | A claimed weakness, not yet reproduced | Written rationale + proposed verification |
| **Confirmed finding** | Reproduced ≥1 time with a complete evidence chain | Root cause + mitigation before finalization |
| **Rejected** | Refuted by evidence | Refuting evidence preserved |

Evidence is authoritative; agent conclusions are always subject to verification.

## Safety model

- `core/scope.py` — deny-by-default authorization; every target contact requires a
  scope Decision from an explicit mission.
- `core/policy.py` — actions are classified read-only / intrusive / consequential;
  consequential actions require recorded human approval.
- `core/audit.py` — append-only hash-chained log of every authorization and policy
  decision. Evidence integrity outranks speed, volume and convenience.

## Repository layout

- `contracts/` — JSON Schemas (draft 2020-12): mission, run, observation, finding, artifact
- `core/` — mission, scope, orchestrator, policy, audit
- `adapters/` — claude_code, codex, mcp, cli
- `workers/` — system_inventory, static_analysis, application_testing, fuzzing, binary_analysis, firmware, qemu, renode
- `evidence/` — manifests (tracked) + objects (content-addressed, local)
- `graph/` — schema.cypher, ingest.py, queries/
- `evals/` — test_cases, expected_results, harness_benchmarks
- `ui/orb/`, `reports/` — status surface and human report templates
- `.agents/evals/` — the agent-behavior eval harness (heuristic eval suite, goal, progress, errors)

## Operating loop

The platform is built and extended by a continuous work loop defined in
`.agents/plans/init.md` §5: ORIENT → SELECT → BUILD → SELF-CHECK → EVAL → RECORD →
REFLECT → CONTINUE/HALT, one work item per iteration, gates enforced by
`.agents/evals/eval-suite/run_evals.py`.

## Status

Under active construction — see `.agents/evals/progress.md` for the live ledger.
