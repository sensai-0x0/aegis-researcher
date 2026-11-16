# P09 — AI-Agent Security

**Weeks 31–33 · Entry gate: P08 exit gate passed; mission, policy, evidence and graph infrastructure operational**

## Purpose

Evaluate the security and reliability of agents, harnesses, tool interfaces and research memory using synthetic test ranges. The curriculum turns its own instruments on itself: the harness built in P03, the broker that mediated every prior phase, and the models that routed every task are now the *targets*. This is where agentic engineering and vulnerability research fully converge — the attack surface being studied is an AI research agent.

## What this phase builds

- **Instruction boundaries (week 31):** synthetic repositories and documents containing conflicting or misleading instructions; testing whether the agent distinguishes untrusted content from trusted project policy; attempted vs. successful policy violations recorded in a controlled harness; deterministic controls hardened with regression tests. *A claimed refusal is not a pass unless the operation is actually blocked.*
- **MCP tool security (week 32):** tool identity, schemas, server trust, authentication boundaries; mock tools with intentionally confusing or overbroad descriptions; broker and worker enforcement verified; logging, approval and denial paths tested. *Tool descriptions cannot grant authority; policy is enforced outside the model.*
- **Harness and model benchmark (week 33):** benchmark cases with seeded positives, benign decoys and incomplete evidence; Haiku/Sonnet/Opus/Fable compared on identical cases; model ID, effort, harness, config hash, tools, cost and outcome recorded; precision, recall, evidence completeness, scope compliance and reproducibility measured.

## Agentic engineering thread

This is the curriculum's capstone on agent architecture. Week 31 operationalizes the instruction-hierarchy principle from the operating contract — repository content is data, not policy — and converts past violations into regression cases, making the harness *measurably* more secure week over week. Week 33 turns model routing from policy into evidence: the "smallest model that passes acceptance tests" principle finally gets its benchmark data, with the correlated-error caveat recorded (same model, prompt and evidence is not independent corroboration) and scope violations treated as hard failures. The evaluation metrics defined here (seeded true/false positive rates, evidence completeness, cost per verified result) become the standing quality dashboard for the platform.

## Vulnerability research thread

The methodology transfers wholesale: define the trust boundary, construct adversarial inputs under authorization, observe, reproduce, classify, and drive a fix with regression coverage. Prompt injection, confused-deputy tool descriptions and authorization bypass in a tool broker are vulnerability classes — studied with the same rigour as a use-after-free, and reported in the same finding lifecycle (candidate → reproduced → confirmed → fixed-verified). Week 32's mock overbroad tools are a controlled confused-deputy experiment: the researcher's first exercise in *agent* exploitation.

## Exit gate

- Runs are repeatable and configuration-pinned.
- No model's unsupported claim is counted as a finding.
- Scope violations are a hard failure.
- Benchmarks distinguish model performance from tool and harness effects.

## 🎯 Goal Project

**Red-team your own workbench — and publish the scorecard.** Against the AEGIS harness and broker, running entirely on synthetic local ranges: execute the injection-resistance suite, the MCP tool-permission matrix tests, and the model/harness benchmark with configuration-pinned repeatable runs.

**Pass condition:** every test has expected and observed outcomes; at least one harness weakness found in weeks 31–32 is fixed and covered by a regression test (a claimed refusal demonstrably corresponds to a blocked operation); the benchmark report compares model tiers on identical cases with model vs. tool/harness effects separated, cost per verified result computed, and zero scope violations across all runs. The independent reviewer attempts one injection of their own design.
