# AEGIS — Project Goal (Definition of Success)

> This file is the fixed reference point. `progress.md` is compared against it every
> loop iteration. It may only be changed by explicit human instruction, never by the
> agent to make progress look better.

## Mission

Build a continuously evolving, evidence-driven security research intelligence platform
that develops a deep, verifiable understanding of software, hardware and AI-agent
systems.

Every research activity must compound upon the last.

## The Six Capabilities

| # | Capability | Definition |
|---|------------|------------|
| 1 | **Understand** | Establish accurate models of systems, components, dependencies and trust boundaries. |
| 2 | **Discover** | Identify weaknesses through disciplined, hypothesis-driven security research. |
| 3 | **Verify** | Distinguish observations from hypotheses and confirmed findings through reproducible evidence. |
| 4 | **Improve** | Establish root causes, validate mitigations and preserve lessons learned. |
| 5 | **Connect** | Build a provenance-rich knowledge graph that reveals relationships, patterns and previously unseen connections across research domains. |
| 6 | **Evolve** | Continuously improve research accuracy, agent reliability and investigative capability without compromising authorization, safety or evidence integrity. |

## North Star

Advance human understanding of system security. Optimize for:

- **Verified knowledge**
- **Reproducibility**
- **Cumulative discovery**

Never optimize for: activity, tool usage, or the volume of reported vulnerabilities.

## Non-Negotiable Constraints

1. All research must remain within **explicitly authorized environments**.
2. **Human oversight** of consequential actions is mandatory.
3. **Evidence is authoritative**; agent conclusions are always subject to verification.
4. An unverified claim must never be presented as a confirmed finding.
5. Integrity of the evidence chain outranks speed, volume and convenience.

## What "Done" Looks Like (map to capabilities)

- **Understand** → `core/mission.py` + `core/scope.py` + inventory skill produce mission-scoped system models; `graph/schema.cypher` models components, dependencies, trust boundaries.
- **Discover** → `workers/*` execute hypothesis-driven activities; `finding-triage` skill governs classification.
- **Verify** → `contracts/{observation,finding,artifact}.schema.json` + `evidence/` enforce reproducible, hash-addressed evidence; `core/audit.py` guarantees chain of custody.
- **Improve** → findings carry root cause + mitigation; lessons learned persist in the graph and `evals/`.
- **Connect** → `graph/ingest.py` links findings, observations, artifacts and provenance across domains; `graph/queries/` exposes cross-domain patterns.
- **Evolve** → `.agents/evals/` continuously scores agent behavior and harness capability; regressions are caught, improvements compound.

The harness is considered operational when: every file in the repository structure is
populated to the quality bar in `.agents/plans/init.md`, all contracts validate, all
eval suites run green, and the continuous work loop can run unattended for one full
cycle producing at least one verified, evidence-backed finding end-to-end.
