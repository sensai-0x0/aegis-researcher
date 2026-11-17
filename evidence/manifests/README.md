# Evidence Manifests — chain of custody

Manifests are the **tracked** half of the evidence store (the objects themselves stay
local, see `evidence/objects/README.md`). A manifest records what was stored, by whom,
and how it moved — the chain of custody that makes findings defensible.

## Format

One JSON file per run: `manifests/<run_id>.manifest.json`:

```json
{
  "run_id": "<uuid>",
  "mission_id": "<uuid>",
  "created_at": "<iso8601>",
  "artifacts": [
    {
      "artifact_id": "<sha256 — equals the file content address>",
      "media_type": "text/plain",
      "size": 4213,
      "produced_by": {"run_id": "<uuid>", "worker": "application_testing"},
      "source": {"tool": "curl", "version": "8.7.1", "command": "…"},
      "custody": [
        {"actor": "worker:application_testing", "action": "collected", "timestamp": "…"},
        {"actor": "agent:evidence-curator", "action": "stored", "timestamp": "…"},
        {"actor": "agent:evidence-curator", "action": "verified", "timestamp": "…"}
      ]
    }
  ]
}
```

The per-artifact shape is exactly `contracts/artifact.schema.json` — manifests are
batches of validated artifact records.

## Rules (from .claude/rules/evidence.md)

1. **Append-only.** Corrections supersede: add a new artifact + custody event marked
   `superseded` on the old one. Never edit a stored record.
2. **Custody is mandatory.** Every artifact carries ≥1 custody event; every custody
   event names a concrete actor.
3. **Verify on write.** The curator recomputes sha256 before recording a `verified`
   custody event.
4. **Manifests are committed to git; objects are not.** The manifest is the durable
   index; objects can be re-fetched/re-derived per the source command.
5. **No evidence without provenance.** A manifest entry whose `source.tool` is
   unknown cannot be accepted (rule: agent interpretation never substitutes for raw
   output — curriculum P01/W2 exit criterion).
