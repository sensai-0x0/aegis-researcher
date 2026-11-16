# Rule: Evidence (evidence-first, chain of custody)

Purpose: evidence is the only authority in AEGIS. These rules make every claim
traceable, every artifact reproducible, and every conclusion auditable.

## MUST

1. Every observation MUST reference ≥1 artifact; artifacts MUST be content-addressed
   (sha256) and written to `evidence/objects/` before the observation is recorded.
2. Every artifact MUST have a manifest entry recording: hash, producer (run/worker),
   tool + version, and custody event.
3. Every conclusion MUST cite the evidence that supports it. Unverified conclusions
   MUST be labeled `hypothesis`.
4. A finding promoted to `confirmed` MUST include ≥1 reproduction observation.
5. Evidence for refuted hypotheses MUST be preserved (rejected ≠ deleted).

## MUST NOT

1. MUST NOT modify or delete a stored evidence object. Correction happens by adding a
   new object + manifest entry superseding the old one.
2. MUST NOT describe evidence in prose without storing the artifact ("I saw a stack
   trace showing…" is invalid without the artifact).
3. MUST NOT rely on un-snapshotted state: if the evidence is a system state (config,
   memory, version), it MUST be captured as an artifact at observation time.
4. MUST NOT summarize results in a way that outruns the evidence (no "confirmed"
   language on hypothesis-tier records).
5. MUST NOT bypass manifests by writing directly to `evidence/objects/`.

## Failure examples (do not do these)

- Storing an observation whose `raw_evidence` array is empty.
- Recomputing a "better" hash for an existing object instead of adding a superseding
  manifest entry — that breaks the chain of custody.
- A report section that asserts a vulnerability exists, citing "prior analysis"
  rather than an artifact id.
