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

<!-- Append new entries below. Never rewrite or delete existing entries. -->
