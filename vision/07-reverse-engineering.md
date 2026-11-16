# P07 — Reverse Engineering

**Weeks 22–25 · Entry gate: P06 exit gate passed**

## Purpose

Understand compiled program structure and vulnerability mechanics using local binaries and sanctioned training challenges. Source is a courtesy the real world rarely extends; this phase builds the ability to reason about software when all you have is bytes — while keeping every exercise on local, authorized targets.

## What this phase builds

- **ELF, Ghidra and GDB orientation (week 22):** headers, sections, symbols, dynamic linking, debug info; binary provenance, hashes and build metadata recorded; decompiled output treated as *interpretation*, never source truth.
- **Assembly and runtime (week 23):** architecture-specific assembly, calling conventions, registers, stack and heap; debugger-traced functions; compiler output compared across controlled build settings; source↔binary↔runtime relationships documented.
- **Memory-safety defects (week 24):** stack and heap errors, use-after-free, bounds errors, integer issues in isolated CTF binaries and purpose-built vulnerable programs; defect preconditions traced; relevant mitigations observed. *No payload is developed for use against a third-party target.*
- **Mitigations and patch verification (week 25):** compiler and OS mitigations studied conceptually; vulnerable vs. corrected builds compared; remediation validated with tests and debugger observations; a review-ready report.

## Agentic engineering thread

Binary analysis is where model assertions are most seductive and least trustworthy — Ghidra decompilation plus a confident model summary can fabricate a very convincing non-existent vulnerability. The phase's controls respond directly: binary provenance and tool versions recorded for every analysis, decompiled claims anchored to reproducible debugger observations, and Opus-tier review for any mitigation or impact claim. Agents learn to present decompilation as *an interpretation with an author and a tool version* — the same provenance discipline the evidence vault enforced in P01, now applied to a domain where nobody can diff against original source.

## Vulnerability research thread

The technical payoff is precondition reasoning: *what conditions must hold for this defect to be reachable, and what mitigations stand between the defect and the impact?* Week 25 forces the key distinction in the discipline — mitigations are not root-cause fixes — and requires the corrected program to pass regression tests. This is the understanding layer beneath P06's automated discovery: fuzzing finds crashes, reverse engineering explains them.

## Exit gate

- Report distinguishes mitigations from root-cause fixes.
- The corrected program passes the relevant regression tests.

## 🎯 Goal Project

**Explain a binary you were never given source for — then prove the fix.** Take a purpose-built vulnerable local binary: produce the binary inventory and provenance record, a behaviour map with annotated execution traces, and a memory-safety investigation that explains the root cause and exact preconditions of the seeded defect. Then compare the vulnerable build against a corrected build, show which mitigations change the picture and which don't, and validate the correction with regression tests.

**Pass condition:** every behavioural claim in the report is anchored to a reproducible local observation with recorded tool versions; the crash-vs-impact distinction is explicit (the report separates "the program faults" from "an attacker gains X, under conditions Y"); and the reviewer — who was not shown your Ghidra session — can reproduce the key trace and accepts the precondition analysis.
