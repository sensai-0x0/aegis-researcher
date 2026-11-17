# Worker: binary_analysis

**Status: stub (interface-complete, no implementation yet).**

## Method
Static/dynamic analysis of compiled artifacts (disassembly, symbol, string evidence).

## Hypotheses served
Component and sink observations from binaries where source is unavailable.

## Evidence emitted
Observations with raw_evidence artifacts; never prose-only results.

## Why stubbed / how to activate
Requires disassembly toolchain (e.g. objdump/radare2) wired via adapter.

Stubs follow `.agents/plans/init.md` §3.8: interface-complete, clearly marked,
implemented in curriculum phase order (P04–P08 goal projects). A stub's run()
raises NotImplementedError and NEVER fabricates observations.
