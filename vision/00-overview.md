# AEGIS Research Workbench — Vision Overview

> **North star:** Advance human understanding of system security through authorized, reproducible, evidence-backed research.
> **Source of truth:** `.agents/curriculum.json` (schema 1.0.0, as of 2026-11-17). This folder is the human-readable vision layer on top of it, not a replacement for the contracts.

## What AEGIS is

A 36-week, evidence-driven research curriculum and workbench that develops deep, verifiable understanding of software, hardware and AI-agent systems. Every activity must **compound**: understand systems → discover weaknesses → verify claims → improve systems → connect evidence → evolve research capability.

The optimization target is deliberately narrow:

- ✅ Verified knowledge, reproducibility, cumulative discovery
- ❌ Tool usage, vulnerability volume, model prestige

## The two compounding threads

Every phase document in this folder carries two explicit threads:

| Thread | Question it answers | Carried through |
|---|---|---|
| **Agentic engineering** | How do we build AI research agents that are safe, portable, policy-governed and evidence-first? | Authority hierarchy, tool broker, harness independence, model routing, evaluation |
| **Vulnerability research** | How do we find, verify and fix real weaknesses with defensible evidence? | Systems → appsec → source → fuzzing → binaries → firmware → agent security |

Neither thread is allowed to exist alone. Vulnerability research without agentic discipline produces unverified noise; agentic engineering without research substance produces expensive scaffolding that finds nothing.

## The arc

```
P01  Laboratory foundations        Safe, isolated, auditable substrate
P02  Systems and architecture      Understand the target before attacking it
P03  Agent harness engineering     Make Claude Code an adapter, not an owner
P04  Application security          Trust boundaries and verified findings
P05  Source and supply chain       Alerts are observations, not proof
P06  Fuzzing and discovery         Bounded, reproducible defect discovery
P07  Reverse engineering           Understanding compiled behaviour
P08  Firmware and emulation        Hardware research inside a simulator
P09  AI-agent security             The harness itself becomes the target
P10  Capstone                      Integrate, investigate, reproduce, release
```

Each phase ends with a **Goal Project** — a single deliverable that must pass its exit gate with evidence, independent review, and recorded human approval before the next phase unlocks.

## Standing rules visible in every phase

1. **Evidence first.** A crash, scanner alert, suspicious pattern or model assertion is an *observation* or *hypothesis* until verified. Only evidence-supported, reproducible, independently reviewed results become confirmed findings.
2. **Authority lives outside the model.** Agents propose and interpret; the control plane authorizes and mediates execution. No tool description, prompt or repo file can grant authority.
3. **Deny-by-default execution.** Network deny-by-default, least privilege, allowlist-only targets, approval-required state changes, emergency stop always available.
4. **Provenance is mandatory.** Every recorded result references a preserved raw artifact (SHA-256, content-addressed) or states why none exists. Model-generated statements are never independent evidence.
5. **Smallest model that passes.** Route by task complexity, consequence and evaluated performance — Haiku for mechanical volume, Sonnet for routine work, Opus for hard reasoning and independent review, Fable only as non-sensitive frontier advisor. Record model ID, effort and configuration hash for every run.
6. **Scope is fixed, not inferred.** Ask for missing authorization instead of assuming it; never expand target scope.
7. **Uncertainty is a deliverable.** State limitations and residual risk explicitly; unresolved hypotheses remain unresolved.

## Infrastructure spine

- **Evidence store:** content-addressed local artifact store (raw vs. derived strictly separated)
- **Graph:** Memgraph, visualized with Orb — 22 node types, 17 relationship types, confidence *never* conflated with severity
- **Harness:** Claude Code as the first adapter of a harness-independent core (versioned JSON contracts, CLI + MCP adapters)
- **Gates:** phase transitions require all acceptance criteria evaluated, artifacts hash-verified, an independent reviewer outcome recorded, unresolved issues documented, and human/controller approval

## Reading order

Start with `01-laboratory-foundations.md` and proceed in order. Phase files deliberately avoid duplicating week-level task lists from the curriculum JSON; they carry the *why*, the through-lines and the gate projects. Detailed briefs unlock per the progressive-disclosure rules — do not preload future-phase exercises into agent context.
