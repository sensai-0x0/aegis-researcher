# Worker: fuzzing

**Status: stub (interface-complete, no implementation yet).**

## Method
Coverage-guided input mutation against authorized parsers/services.

## Hypotheses served
Crash and hang observations with reproducer artifacts.

## Evidence emitted
Observations with raw_evidence artifacts; never prose-only results.

## Why stubbed / how to activate
Requires fuzzing engine + corpus; stub until a target lab is authorized.

Stubs follow `.agents/plans/init.md` §3.8: interface-complete, clearly marked,
implemented in curriculum phase order (P04–P08 goal projects). A stub's run()
raises NotImplementedError and NEVER fabricates observations.
