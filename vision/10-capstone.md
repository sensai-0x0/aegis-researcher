# P10 — Research Platform Capstone

**Weeks 34–36 · Entry gate: P09 exit gate passed; all core agents, workers, evidence records and graph contracts versioned**

## Purpose

Integrate every discipline into an evidence-first research workbench and demonstrate independent reproducibility. The capstone does not add new techniques; it proves the platform — and the researcher — can produce a complete, defensible, independently reproducible cross-layer investigation.

## What this phase builds

- **Integration (week 34):** mission management, harness adapters, controlled workers, evidence storage and graph ingestion connected; systems, source, software, fuzzing and emulation workers behind the tool broker; end-to-end run tracking and failure handling; Orb research views and report generation. → **AEGIS v0.9 integrated workflow.**
- **Cross-layer research case (week 35):** a deliberately constructed local target containing software, binary, firmware and emulated-system elements; inventory, source review, approved tests and firmware/emulation analysis run under one bounded mission; independent review challenges candidate findings; confirmed, disproved and unresolved hypotheses recorded distinctly.
- **Clean-room reproduction and release (week 36):** a clean environment restored from documented artifacts and configuration; selected experiments repeated *without relying on agent conversation history*; evidence hashes, findings, patches and graph relationships verified; release report, limitations, backlog and maintenance plan published. → **AEGIS v1.0 release candidate.**

## Agentic engineering thread

Week 34 is the final exam for the architecture: one mission flows from approved target to preserved observations and graph records with *all* tool calls mediated and auditable, and harness-specific logic owning neither evidence nor scope policy. Week 36 delivers the deepest agentic-engineering result in the curriculum: reproducibility without the agent. Chat history is explicitly not the canonical research record — the platform's state lives in artifacts, contracts and the graph, which is exactly what makes a clean-room reproduction possible for both the system and its findings.

## Vulnerability research thread

Week 35 exercises the full researcher's toolkit in a single investigation — the appsec boundary mapping of P04, source and dependency analysis of P05, fuzzing and reproduction of P06, binary reasoning of P07, and firmware/emulation analysis of P08 — unified by the finding lifecycle and independent review from P09's method. The deliverable dossier is the curriculum's proof that the researcher can independently explain system behaviour, evaluate candidate weaknesses, reproduce and root-cause defects, validate mitigations and communicate limitations **without relying on model authority**.

## Exit gate

- Key findings reproduce from documented instructions and artifacts.
- The report documents limitations and residual uncertainty.
- The research platform passes scope and evidence-integrity checks.

## 🎯 Goal Project

**Ship AEGIS v1.0 by surviving a clean-room audit.**

1. **Integrate** the full research workflow end-to-end (v0.9): one mission, every worker, all calls brokered, graph populated, Orb views live.
2. **Investigate** the cross-layer seeded case: produce the research dossier, evidence-linked graph and finding/hypothesis ledger — including hypotheses that remain open and ones the evidence *disproved*.
3. **Release** v1.0: a second researcher restores a clean environment from your documented artifacts and configuration alone, repeats the key experiments, verifies evidence hashes, findings, patches and graph relationships — and either reproduces your results or demonstrates a specific, documented gap.

**Pass condition (all three):** the reproduction report was produced without access to your agent conversation history; the release report states limitations and residual uncertainty plainly; and the platform passes scope and evidence-integrity checks with zero unauthorized scope expansions, zero fabricated results, and every confirmed finding backed by provenance and independent review.

**What completion means — and doesn't.** A working workbench that accepts an authorized mission, inspects a local software or emulated hardware target, runs approved analysis, preserves immutable evidence, and visualizes provenance-rich relationships. It does *not* imply mastery of every security discipline, proof of physical hardware properties from emulation, or authorization to test external systems. The output includes a next-stage specialization backlog — the curriculum compounds, it doesn't conclude.
