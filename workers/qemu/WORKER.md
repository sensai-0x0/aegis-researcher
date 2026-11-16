# Worker: qemu

**Status: stub (interface-complete, no implementation yet).**

## Method
Full-system emulation of authorized images for safe dynamic analysis.

## Hypotheses served
Runtime observations from emulated targets (logs, state captures).

## Evidence emitted
Observations with raw_evidence artifacts; never prose-only results.

## Why stubbed / how to activate
Requires qemu + authorized image; stub until lab exists.

Stubs follow `.agents/plans/init.md` §3.8: interface-complete, clearly marked,
implemented in curriculum phase order (P04–P08 goal projects). A stub's run()
raises NotImplementedError and NEVER fabricates observations.
