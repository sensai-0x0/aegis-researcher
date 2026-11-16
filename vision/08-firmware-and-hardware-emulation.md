# P08 — Firmware and Hardware Emulation

**Weeks 26–30 · Entry gate: P07 exit gate passed; emulation targets and disposable snapshots available**

## Purpose

Build a hardware-security research capability using emulated full systems and embedded platforms — while being ruthlessly honest about what emulation can and cannot establish. Physical side-channel and fault-injection work is explicitly out of scope for the 36-week core; the discipline here is cross-layer thinking under documented limitations.

## What this phase builds

- **QEMU lab (week 26):** repeatable emulated Linux system with virtual devices, guest inventory, snapshots, isolated networking; host/guest/machine model and image hashes recorded.
- **Firmware analysis (week 27):** EMBA/Binwalk-driven extraction and inventory of a research-suitable image — filesystems, binaries, packages, configuration — with the original image hash-identified and preserved, and tool-derived results distinguished from manual confirmation. *No device is modified.*
- **Renode embedded simulation (week 28):** documented platform or exercise loaded with sample firmware; modeled peripherals, memory and communication interfaces inspected; simulator version, platform description and known modeling gaps recorded.
- **Boot chain and platform trust (week 29):** UEFI concepts, secure boot, measured boot; boot stages and trust transitions modeled; emulation limitation report stating which properties *cannot* be established by emulation alone.
- **Cross-layer graph (week 30):** QEMU, Renode and firmware records merged into the common schema; provenance, confidence, reproducibility and recency modeled as separate dimensions; Orb views; graph schema v1.0.

## Agentic engineering thread

Hardware is the domain where agents hallucinate most confidently — plausible-sounding claims about chipsets and boot ROMs that no emulator can verify. The controls are therefore mostly *epistemic*: each trust assertion must carry evidence or be marked as an assumption; simulation evidence must never be misrepresented as physical-hardware evidence; and Fable is admitted here (as non-sensitive design advisor) because ambitious cross-layer architecture is exactly where a frontier advisor earns its cost — with the standing rule that its safeguards must never be circumvented. Week 30 is also the graph's maturation milestone: confidence, severity, recency and reproducibility as distinct, queryable dimensions.

## Vulnerability research thread

The research skill is layered provenance: firmware component → package → binary → interface → observation, every edge with a source or derivation record. This is where the evidence-first pipeline meets its hardest heterogeneous input: packed firmware images, unknown filesystems, simulated peripherals with documented gaps. The boot-chain week plants the security-architecture mindset — where trust transitions happen and which assumptions each transition silently makes — that underpins real firmware research beyond this curriculum.

## Exit gate

- Every important relationship has a source or derivation record.
- Confidence is separate from severity.
- Hypotheses and confirmed findings are visually distinguishable.

## 🎯 Goal Project

**Build one cross-layer case study that survives its own limitations report.** Select a research-suitable firmware image and one supported emulated platform: produce the firmware inventory and component graph, the QEMU and Renode run records, a boot-chain model with evidence or explicit assumptions at every trust transition, and merge everything into the cross-layer Memgraph schema with Orb views separating hypotheses from confirmed findings.

**Pass condition:** the case study contains a self-written limitations section listing what emulation cannot establish; no node or edge claims a physical property from simulation; an independent reviewer can query the graph, pick any relationship, and find its provenance — including the ones marked as assumptions.
