# Evidence Objects — immutable content-addressed store

Objects are the **raw, preserved outputs** of research activity. They are the only
authoritative record; every observation, hypothesis and finding must trace to one or
more objects by content address.

## Layout

```
evidence/objects/<sha256[:2]>/<sha256>     # e.g. ab/abcdef…64hex
```

The file name IS the sha256 of its content. `artifact_id == sha256` always — there is
no separate naming scheme to keep in sync.

## Rules (from .claude/rules/evidence.md + curriculum P01/W2)

1. **Immutable.** Stored objects are never modified or deleted. A correction is a new
   object plus a superseding manifest entry.
2. **Content-addressed.** Before recording `stored` custody, recompute the sha256 and
   confirm it matches the target path. On retrieval, verify again: **artifact hashes
   must verify after storage and retrieval** (P01 exit criterion).
3. **Raw only.** An object holds raw output (banner, packet capture, config excerpt,
   response body). Agent interpretation lives in observations/findings — never in
   place of the raw object ("agent-generated interpretation is never substituted for
   raw output").
4. **Local-only in git.** This directory's contents are gitignored; manifests in
   `evidence/manifests/` are the durable, committed index. Re-derivation is possible
   via the manifest's `source.command`.
5. **Write through the curator.** Nothing writes here directly except the
   evidence-curator flow, which always pairs an object write with a manifest entry.

## Helper

`python3 -m core.evidence store <file> --run-id <uuid>` — hash, place, and emit the
manifest record JSON to stdout (implemented in `core/evidence.py`).
