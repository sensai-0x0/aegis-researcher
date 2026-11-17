# P04 — Application Security

**Weeks 10–13 · Entry gate: P03 exit gate passed; tool broker and scope checks active**

## Purpose

Assess deliberately vulnerable local applications and authorized training environments — with testability and root-cause understanding as the emphasis, never bug-counting. This is the first phase where the workbench actually *hunts*, and it sets the pattern: model first, test under authorization, verify, fix, review.

## What this phase builds

- **Threat modelling (week 10):** components, data flows, identities, trust boundaries and exposed interfaces mapped for a deliberately vulnerable local app; threats translated into *testable* security requirements; model elements stored in Memgraph.
- **Authn/authz (week 11):** authentication lifecycle, session handling, authorization decisions and object-level access — tested through PortSwigger Academy labs with structured test cases for expected *and* prohibited access.
- **Input handling and APIs (week 12):** input validation, output encoding, injection classes, API schemas, deserialization risk; input paths mapped to handlers and controls; negative tests and positive controls recorded.
- **Business logic and verified findings (week 13):** seeded logic defects and concurrency edge cases; full reproduce → root-cause → fix → regression-test cycle; a responsible-report template.

## Agentic engineering thread

P04 is the first live exercise of the P03 authority chain: every proposed test is tied to a local target and authorized scope before the broker lets it run. The reporting rule gets its sharpest test here — *a test outcome is not labelled vulnerable without demonstrating the violated security requirement*. Agents must maintain the observation/hypothesis/finding distinction under real analysis pressure, where the temptation to declare victory on a juicy response diff is highest. Independent Opus review of every candidate finding becomes routine practice.

## Vulnerability research thread

The craft taught here is precision: reachable code paths distinguished from speculative patterns, findings that carry affected component, preconditions, evidence, impact rationale and remediation. Week 13 completes the first full finding lifecycle — including writing the patch and proving it addresses the root cause with regression tests. That finding shape is reused verbatim in P05 (patch review), P06 (fuzzed defects) and P10 (the capstone dossier).

## Exit gate

- Finding includes affected component, preconditions, evidence, impact rationale and remediation.
- Patch demonstrably addresses the root cause.
- Reviewer independently checks the evidence.

## 🎯 Goal Project

**Take one finding from hypothesis to fixed — with the paper trail to prove it.** Against a deliberately vulnerable local application: produce the threat model and trust-boundary graph, then complete the full finding lifecycle for at least one real defect — including a business-logic or access-control weakness, not just an injection class.

**Pass condition:** the finding record cites reproducible lab evidence and the violated security requirement; the patch passes a regression test that failed before it; an independent reviewer run, working only from raw artifacts (not your summaries), reproduces the defect and agrees with impact and remediation — or records a specific dissent.
