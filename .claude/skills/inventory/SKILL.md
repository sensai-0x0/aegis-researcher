---
name: inventory
description: System inventory and modeling. Use when a mission needs its systems, components, dependencies, interfaces, data flows or trust boundaries established or updated — the first research activity of any mission (Understand).
---

# Skill: System Inventory

Establish accurate models of systems, components, dependencies and trust boundaries.
The output is a structured model that feeds the knowledge graph — inventory is the
foundation every other worker builds on.

## Inputs

- A validated mission (contract: `mission.schema.json`) with `authorized_targets`.
- A scope Decision from `core/scope.py` for every target inventoried.
- Prior inventory models from the graph, if any (inventories are incremental).

## Procedure

1. **Resolve scope** for the target set. Hard-stop on anything out of scope
   (rule: `scope.md`).
2. **Enumerate components**: services, processes, binaries, firmware images, AI-agent
   components, configuration surfaces. One observation per discovery, each with the
   artifact that evidences it (banner capture, file listing, config excerpt).
3. **Map dependencies**: for each component record what it calls, consumes, trusts
   (library deps, network deps, trust relationships). Cite the evidence per edge.
4. **Identify interfaces**: network listeners, file interfaces, APIs, IPC, hardware
   buses, agent tool surfaces.
5. **Draw trust boundaries**: where does data cross a privilege/trust change? Record
   each crossing as a graph edge (`TRUSTS` / `CROSSES`).
6. **Record coverage gaps**: components you could not inventory and why — these feed
   the `coverage-gap` graph query.
7. Emit the model as observations + graph nodes/edges (types per
   `graph/schema.cypher`). Never classify weaknesses here — inventory is Understand,
   not Discover.

## Outputs

- Observation records (contract: `observation.schema.json`), one per fact.
- Graph node/edge set for `Component`, `Dependency`, `TrustBoundary`.
- A coverage-gap list (components not yet inventoried).

## Quality bar

- Every component has ≥1 artifact-backed observation.
- Every dependency edge cites evidence for both endpoints.
- No component is asserted to exist without evidence; "likely present" is recorded as
  a hypothesis.

## Failure modes

- Skips trust boundaries because they are "architectural, not security" — trust
  boundaries are the primary structure of the model.
- Invents components from documentation without observational evidence.
- Marks inventory "complete" without recording the coverage-gap list.
