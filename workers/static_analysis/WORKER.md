# Worker: static_analysis

**Status: stub (interface-complete, no implementation yet).**

## Method
Structured source analysis for dangerous flows (sinks) without execution.

## Hypotheses served
Attacker-reachable path hypotheses from source (feeds source-review skill).

## Evidence emitted
Observations with raw_evidence artifacts; never prose-only results.

## Why stubbed / how to activate
Requires an analysis toolchain (e.g. semgrep/codeql) wired via adapter; fails closed until then.

Stubs follow `.agents/plans/init.md` §3.8: interface-complete, clearly marked,
implemented in curriculum phase order (P04–P08 goal projects). A stub's run()
raises NotImplementedError and NEVER fabricates observations.
