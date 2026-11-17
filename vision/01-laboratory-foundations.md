# P01 — Laboratory Foundations

**Weeks 1–2 · Entry gate: working Python + Linux CLI**

## Purpose

Establish a safe, repeatable and auditable environment *before* any agent interacts with a research target. This phase exists because everything later in the curriculum — fuzzing campaigns, firmware analysis, agent benchmarking — is only as trustworthy as the substrate it runs on. An agent that cannot prove isolation, restore a baseline or halt itself is not a research agent; it is an uncontained risk.

## What this phase builds

Two primitives the entire workbench stands on:

1. **The isolated lab** — a disposable virtualized environment with default-deny networking, snapshot/restore, and a written scope manifest that defines every authorized target, action, exclusion, time limit and stop condition. A test cannot begin without a valid scope record, and a human can always halt execution and revoke the mission.
2. **The evidence vault (v0.1)** — content-addressed artifact storage keyed by SHA-256, append-only run manifests, and the raw-vs-derived separation rule: agent summaries and conclusions are never substituted for raw output. Missions, runs and artifacts get their first Memgraph schema.

## Agentic engineering thread

This is where the authority hierarchy becomes concrete rather than theoretical. The scope manifest is the first **policy artifact** — the thing that later lets the tool broker (P03) make deterministic allow/deny decisions without asking the model's opinion. Building "emergency stop and human approval path" as a tested deliverable installs the habit that consequential actions are gated outside the agent. The provenance metadata recorded here (source, collection time, mission, run, tool version, target snapshot) becomes the template every future agent run must satisfy.

## Vulnerability research thread

The discipline taught here is the difference between a lab result and a claim: restore-and-replay, hash verification, observation vs. hypothesis vs. conclusion. Every later finding (P04–P08) inherits its defensibility from these two weeks. Researchers learn early that "I found a bug" is worthless without an artifact reference that verifies after storage and retrieval.

## Exit gate

- Every recorded result references a preserved raw artifact or explicitly states why none exists.
- Artifact hashes verify after storage and retrieval.
- Agent-generated interpretation is never substituted for raw output.

## 🎯 Goal Project

**Build and prove the containment contract.** Deliver a working isolated research lab plus Evidence Vault v0.1, then demonstrate the full lifecycle on one approved local mission: create a scope manifest → run a bounded experiment inside the isolated environment → destroy/restore the target to a known baseline → produce artifacts whose SHA-256 hashes verify on retrieval → write a research note that cleanly separates observations, hypotheses and conclusions.

**Pass condition:** a second person can revoke the mission mid-run with the emergency stop, restore the target from snapshot, and re-verify every artifact hash without consulting you.
