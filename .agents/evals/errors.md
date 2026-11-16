# AEGIS — Agent Error Ledger

> Append-only record of agent errors, with the patch applied and the eval that now
> guards against recurrence. An error is only "closed" when a heuristic/case exists
> that would fail if the error were reintroduced.

## Entry format

```
### E-<NNN> — <short title>
- Date / Iteration:
- Capability:      safety | evidence | contracts | harness | process | graph | research
- Symptom:         <what was observably wrong>
- Root cause:      <why the agent did the wrong thing>
- Patch:           <what was changed to fix it>
- Prevention:      <heuristic id / eval case that now catches it>
- Status:          OPEN | PATCHED | CLOSED (when prevention exists and passes)
```

## Errors

### E-001 — curriculum.json is empty; phase-improvement comparator missing
- Date / Iteration: 2026-11-17 / 1
- Capability: process
- Symptom: `.agents/curriculum.json` is 0 bytes, so the mandated comparison between
  curriculum, goal.md and progress.md cannot be performed as specified.
- Root cause: file was created as a placeholder in the initial scaffold without content.
- Patch: proceed with goal.md ↔ progress.md comparison as the authoritative
  improvement signal; log every planned-vs-actual divergence in the progress.md
  Decision Log so a future curriculum can be derived from it.
- Prevention: `process.progress-ledger-current` heuristic + Decision Log entries
  tagged with the divergence they capture.
- Status: PATCHED (awaiting human-populated curriculum to CLOSE)

### E-002 — negative fixture naming didn't map to its schema
- Date / Iteration: 2026-11-17 / 3
- Capability: contracts
- Symptom: `negative-finding-no-repro.instance.json` derived a nonexistent schema
  path (`finding-no-repro.schema.json`) and crashed the validator.
- Root cause: ad-hoc fixture naming; stem-to-schema mapping convention was undefined.
- Patch: naming convention fixed — `negative-<base>.instance.json` validates against
  `<base>.schema.json`; fixture renamed to `negative-finding.instance.json`.
- Prevention: `contracts.fixtures-validate` heuristic added to the eval suite (runs
  the validator; any fixture that can't resolve to a schema fails).
- Status: CLOSED

### E-003 — concurrent sessions sharing the repo caused interleaved commits and a lost-merge window
- Date / Iteration: 2026-11-17 / 3
- Capability: process
- Symptom: while this loop committed Phase 2, parallel sessions (user + worktrees)
  switched branches in the shared primary tree; the iter-3 commit landed on
  `feat/readme-rainbow-header` instead of the intended branch, the merge chain broke,
  and the shared working tree was switched out mid-phase (contracts appeared empty
  in-tree although committed elsewhere).
- Root cause: multiple agents operating in ONE working tree; loop assumed exclusive
  custody. Secondary: loop ran `reset --hard` inside another session's worktree
  (aegis-worktrees/main) during sync — content happened to be identical to the
  committed state, but the operation was unsafe by principle.
- Patch: loop moved to a dedicated worktree (`aegis-loop`, branch `loop/integration`);
  integration done at ref level (update-ref verified fast-forward); harness heuristic
  `h_readme` updated to accept the user's README+WHY.md doc split.
- Prevention: eval-suite runs from the loop worktree only; ledger Decision Log
  records ref-level integration; rule adopted — never checkout/reset inside another
  session's worktree, only fast-forward-verified `update-ref` on main.
- Status: CLOSED

<!-- Append new entries below. Never rewrite or delete existing entries. -->
