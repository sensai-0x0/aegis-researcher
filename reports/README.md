# Reports — human-readable research output

Reports are the human interface to findings. They are **rendered from contract
records** — a report section that cannot cite a contract field or artifact hash
must not exist (rule: evidence is authoritative; prose never outruns evidence).

## Files

- `finding-report.template.md` — the canonical section structure, 1:1 with
  `contracts/finding.schema.json`
- `render_finding.py` — renderer; validates the finding against the contract
  BEFORE rendering, and refuses confirmed-without-reproduction structurally

## Usage

```bash
python3 reports/render_finding.py <finding.json> \
    [--artifact <artifact.json>] [--observation <obs.json>] -o out.md
```

Output lands in `reports/out/` (gitignored — rendered output, not templates).

## Rules

1. Renderer validates first: an invalid finding NEVER renders.
2. Every section maps to explicit contract fields (see template header table).
3. Severity text repeats the contract's `severity_justification` verbatim —
   the reviewer's justification, not the renderer's opinion.
4. Status ladder language is fixed: observation / hypothesis / confirmed /
   rejected. A confirmed finding prints its reproduction steps verbatim.
