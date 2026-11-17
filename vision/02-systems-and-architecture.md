# P02 — Systems and Architecture

**Weeks 3–6 · Entry gate: P01 exit gate passed**

## Purpose

Deepen existing Python and Linux skills into genuine systems understanding across processes, memory, networking and architecture. You cannot discover weaknesses in a system you cannot explain. This phase converts "Linux user" into "person who can model a running system as structured, queryable data" — the cognitive base for every attack and mitigation discussion that follows.

## What this phase builds

- **Research CLI skeleton (week 3):** typed Python, packaging, pytest, structured logging, versioned Pydantic models and JSON Schema contracts, deterministic output fixtures.
- **System Atlas inventory worker (week 4):** read-only collection of processes, services, users, permissions, mounts, packages, kernel and network metadata — normalized into typed JSON records, repeatable on a pinned target snapshot.
- **C and memory literacy (week 5):** pointers, allocation, undefined behaviour, sanitizers (ASan/UBSan), debugger-driven root-cause analysis, corrected examples with regression tests.
- **System Atlas v0.1 (week 6):** protocol and interface map from observed local traffic (TCP/IP, DNS, HTTP/TLS, sockets), trust boundaries, and host/service/process/interface entities in Memgraph.

## Agentic engineering thread

Week 3 is the first *harness-adjacent* engineering: the CLI skeleton later becomes the research core that both Claude Code and alternate harness adapters call (P03, P09). The JSON Schema contracts defined here are the portable spine — they are what makes the workbench harness-independent rather than a pile of prompts. Inventory collection is also the first place agents must obey read-only constraints and label unknowns as unknown rather than inferring — the epistemic habit that separates a research agent from a confidently wrong one.

## Vulnerability research thread

The memory week (5) is the curriculum's first genuine vulnerability-research skill: reproduce a defect locally, explain it at source level, demonstrate a corrective change with a regression test. That observation → reproduction → root cause → fix loop is the exact cycle scaled up in P06 (fuzzing) and P07 (binaries). The trust-boundary map from week 6 is what makes P04's threat modelling possible — you test boundaries you can first *see*.

## Exit gate

- The map is based on observed local configuration and traffic.
- Unknowns are labelled as unknown rather than inferred.
- No external target is contacted.

## 🎯 Goal Project

**Ship the System Atlas v0.1 as evidence, not notes.** Take one pinned local Linux target and produce a complete structured model: inventory (repeatable, read-only), a C defect experiment set with sanitizer-backed reports and a corrected example, and a Memgraph graph of hosts, services, processes, interfaces and trust boundaries built purely from observed traffic.

**Pass condition:** an independent reviewer can re-run the inventory against the pinned snapshot, get a matching dataset, point at any node in the graph and find the raw artifact and collection metadata that justifies it — and no edge in the graph encodes an inference you did not observe.
