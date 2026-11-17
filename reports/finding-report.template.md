# Finding Report: {{title}}

> Canonical template. Field mapping is 1:1 with contracts/finding.schema.json —
> render_finding.py fills every section from the record; no free invention.

| Report section | Contract field(s) |
|----------------|-------------------|
| Header / title | `title`, `finding_id`, `status` |
| Claim | `claim` |
| Affected component | `affected_component.{identifier,version,anchors}` |
| Severity | `severity` + `severity_justification` (verbatim) |
| Evidence | `evidence[]` (sha256 refs, resolved via manifests) |
| Reproduction | `reproduction[]` (verbatim, numbered) |
| Root cause | `root_cause` |
| Mitigation | `mitigation` |
| Lessons learned | `lessons_learned` |
| Review chain | `provenance.{originated_by,triaged_by}`, `reviewed_by[]` |

---

## Status: {{status}} (epistemic ladder)

{{status_note}}

## Claim

{{claim}}

## Affected component

- **Component:** {{component_id}} {{component_version}}
- **Anchors:** {{anchors}}

## Severity: {{severity}}

{{severity_justification}}

## Evidence

{{evidence_table}}

## Reproduction

{{reproduction_steps}}

## Root cause

{{root_cause}}

## Mitigation

{{mitigation}}

## Lessons learned

{{lessons_learned}}

## Review chain

- Originated by: {{originated_by}}
- Triaged by: {{triaged_by}}
- Reviewed by: {{reviewed_by}}

---
*Rendered by reports/render_finding.py from a contract-validated record. Evidence
hashes verify per evidence/manifests/ conventions; interpretation never substitutes
raw artifacts (curriculum P01/W2).*
