# Worker: application_testing

**Status: stub (interface-complete, no implementation yet).**

## Method
Exercises authorized local applications with test inputs across trust boundaries.

## Hypotheses served
Behavioral observations of input handling, auth, and session logic.

## Evidence emitted
Observations with raw_evidence artifacts; never prose-only results.

## Why stubbed / how to activate
Requires a running authorized lab instance; never targets out-of-scope hosts.

Stubs follow `.agents/plans/init.md` §3.8: interface-complete, clearly marked,
implemented in curriculum phase order (P04–P08 goal projects). A stub's run()
raises NotImplementedError and NEVER fabricates observations.
