# P05 — Source Code and Software Supply Chain

**Weeks 14–16 · Entry gate: P04 exit gate passed**

## Purpose

Connect source-level weaknesses, dependency exposure and patch quality — **without treating a scanner alert as proof**. This phase is the curriculum's sustained lesson in epistemic humility: tooling produces candidate observations at scale; only verification produces findings.

## What this phase builds

- **Analyzer-assisted source review (week 14):** static analysis, taint and data-flow concepts against a pinned repository; Semgrep integration; alerts mapped to source files, symbols and code paths; explicit false-positive triage with recorded reasoning.
- **SBOM and dependency relationships (week 15):** Syft-generated SBOM; OSV-Scanner candidate advisories; package identity/version/config vs. actual dependency path; package→asset and package→advisory edges in Memgraph.
- **Patch review and regression validation (week 16):** diffs mapped to affected functions, tests and findings; before/after behaviour recorded; residual risk and unresolved assumptions documented.

## Agentic engineering thread

This phase stress-tests the agent behaviour contract in the noisiest environment: a scanner fires dozens of alerts and the agent must keep *every one of them* classified as a candidate observation. Acceptance criteria enforce the discipline — at least one false positive correctly rejected, analyzer version and source locations preserved, alerts cited with retrieval timestamps. The model routing also shows the tiered pattern in action: Haiku normalizes alert metadata, Sonnet drives source tooling, Opus reviews reachability and material findings. The output — a structured source-review worker and result schema — becomes another reusable core capability behind the broker.

## Vulnerability research thread

Reachability is the headline skill: applicability is assessed separately from mere package presence. A vulnerable version of a package in an SBOM is a hypothesis; a vulnerable version on an actually reachable code path is a candidate finding. Week 16 then closes the loop the reverse direction — reviewing someone else's patch the way P04 taught you to write your own, and refusing to mark anything fixed until an appropriate regression test passes.

## Exit gate

- A patch is not marked fixed until an appropriate regression test passes.
- Review records before/after behaviour and residual uncertainty.

## 🎯 Goal Project

**Turn a dependency advisory into a defensible reachability verdict.** Take a pinned repository: generate its SBOM, pull candidate known vulnerabilities, then pick one advisory and produce the complete assessment — package identity and version provenance, dependency-path analysis, whether the vulnerable code is reachable in this build, patch review of the upstream fix, and a regression validation of the patched behaviour.

**Pass condition:** the final verdict cites every candidate tied to an identified package and version, includes at least one correctly rejected false positive with recorded reasoning, marks nothing fixed without a passing regression test, and clearly states residual risk an independent reviewer can accept or contest.
