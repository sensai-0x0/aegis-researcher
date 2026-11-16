# P06 — Fuzzing and Vulnerability Discovery

**Weeks 17–21 · Entry gate: P05 exit gate passed; isolated test workers and evidence preservation operational**

## Purpose

Perform systematic, reproducible defect discovery against local targets and purpose-built vulnerable programs. This is the vulnerability-research centerpiece: the longest phase, covering the full arc from harness design through a bounded campaign, crash classification, minimization, and a complete discovery-to-fix cycle.

## What this phase builds

- **Fuzzing foundations (week 17):** mutation-based and coverage-guided concepts; a deterministic build and test harness for a small documented local parser or vulnerable target; seed corpus, resource limits, stop conditions, experiment manifest.
- **AFL++ campaign (week 18):** instrumented target, validated coverage feedback, a time- and resource-bounded campaign with preserved corpus, run metadata and tool versions; restartable from a known state.
- **Crash classification (week 19):** sanitizers and debugger output; crashes vs. hangs vs. assertion failures vs. harness faults; deduplication by reproducible signature; a failure taxonomy. *A crash alone is never treated as proof of exploitability or security impact.*
- **Reproduction and minimization (week 20):** re-runs against pinned builds, minimized inputs, environment/compiler/sanitizer pinning, reproducibility scores; flaky outcomes explicitly marked.
- **Root cause to regression (week 21):** failure traced to the responsible code and violated invariant; preconditions and realistic impact stated without overclaiming; corrective patch, regression test, updated graph provenance.

## Agentic engineering thread

Fuzzing is where autonomous agents could most easily go off the rails — long-running, resource-hungry, failure-prone — so the controls are strict: campaign limits and reset procedures explicit before launch, bounded scope, artifact capture on every run, and agents whose triage output is clustered metadata (Haiku/Sonnet) while *only* Opus reviews reproduction and root cause. The model-routing rule "a model never certifies a crash as a vulnerability by itself" is stated verbatim in the curriculum for this phase. Experiment manifests turn fuzzing campaigns into reproducible experiments rather than slot-machine sessions.

## Vulnerability research thread

This phase industrializes the loop from P02's memory week: hypothesis → harness → campaign → observation → classification → reproduction → root cause → patch → regression test → independent review. The craft distinctions that matter: deduplication by signature rather than vibes; stable reproductions separated from flaky ones; and impact claims that match the evidence, no further.

## Exit gate

- Finding has reproducible evidence and root-cause explanation.
- Patch fixes the underlying defect.
- Independent reviewer agrees or records a specific unresolved disagreement.

## 🎯 Goal Project

**Run one complete discovery pipeline end-to-end.** From a seeded local defect: build the harness and manifest, execute a bounded AFL++ campaign, classify and deduplicate the resulting failures, minimize one crash to a deterministic reproducer, trace it to the responsible code and violated invariant, patch the training target, add the regression test, and update the graph with provenance linking artifact → observation → hypothesis → finding → patch → review.

**Pass condition:** the reproducer replays from the stored input and environment manifest on a pinned build; the classification pipeline demonstrably separates real defects from harness faults (at least one benign outcome correctly discarded); and the independent reviewer, working from raw artifacts only, either confirms the finding or records a specific unresolved disagreement — either outcome is a pass, an unsupported certainty is not.
