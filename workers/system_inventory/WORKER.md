# Worker: system_inventory

**Status: implemented (local-scope only).**

## Method
Enumerates a target directory tree (an authorized local component) into
components and interfaces: files, executable bits, symlinked dependencies.
Produces one content-addressed artifact (the inventory listing, sha256) and
observations per top-level component.

## Hypotheses served
- "Component X exists and exposes interface Y" — inventory verifies presence
  with evidence, per the inventory skill.

## Evidence emitted
- Artifact: the full listing (raw output, preserved, hash-addressed).
- Observations: `component present` facts with `raw_evidence` = [artifact hash].

## Limits
- Local filesystem targets only; never contacts network targets (scope rule).
- Does NOT classify weaknesses — inventory is Understand, not Discover.
