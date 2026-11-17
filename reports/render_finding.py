#!/usr/bin/env python3
"""Render a contract-validated finding into a human report (stdlib-only).

Contract enforcement happens BEFORE rendering: an invalid finding never
renders, and a confirmed finding without reproduction is structurally
impossible (finding.schema.json if/then guard + this renderer's own check).

Usage:
    python3 reports/render_finding.py finding.json \
        [--artifact artifact.json] [--observation obs.json] -o out.md
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.jsonschema_lite import ValidationError, validate  # noqa: E402

TEMPLATE = (ROOT / "reports" / "finding-report.template.md").read_text()

STATUS_NOTES = {
    "observation": "A reproducible fact. No weakness is claimed at this tier.",
    "hypothesis": "A claimed weakness, NOT verified. Must not be treated as a finding.",
    "confirmed": "Reproduced with a complete evidence chain. Severity is justified below.",
    "rejected": "Refuted by evidence. The refutation is preserved in the record.",
}


def render(finding: dict, artifact: dict | None, observation: dict | None) -> str:
    if finding["status"] == "confirmed" and not finding.get("reproduction"):
        raise ValidationError("confirmed finding without reproduction refuses to render")
    comp = finding.get("affected_component", {})
    evidence_rows = ["| Artifact (sha256) | Note |", "|---|---|"]
    if artifact:
        evidence_rows.append(f"| `{artifact['sha256']}` | {artifact.get('media_type')} "
                             f"via {artifact.get('source', {}).get('tool', 'unknown')} |")
    for h in finding.get("evidence", []):
        if not artifact or h != artifact["sha256"]:
            evidence_rows.append(f"| `{h}` | referenced in finding.evidence |")
    obs_row = ""
    if observation:
        obs_row = (f"\n> Supporting observation `{observation['observation_id']}` "
                   f"({observation['method']['worker']}) cites evidence "
                   f"`{observation['raw_evidence'][0][:16]}…`\n")
    return (TEMPLATE
            .replace("{{title}}", finding["title"])
            .replace("{{finding_id}}", finding["finding_id"])
            .replace("{{status}}", finding["status"])
            .replace("{{status_note}}", STATUS_NOTES[finding["status"]])
            .replace("{{claim}}", finding.get("claim") or "_No claim recorded (observation tier)._")
            .replace("{{component_id}}", comp.get("identifier", "unknown"))
            .replace("{{component_version}}", f"(v{comp['version']})" if comp.get("version") else "")
            .replace("{{anchors}}", ", ".join(f"`{a}`" for a in comp.get("anchors", [])) or "none recorded")
            .replace("{{severity}}", str(finding.get("severity") or "unassigned (pre-confirmation)"))
            .replace("{{severity_justification}}", finding.get("severity_justification") or "_n/a before confirmation_")
            .replace("{{evidence_table}}", obs_row + "\n".join(evidence_rows))
            .replace("{{reproduction_steps}}", "\n".join(finding.get("reproduction", [])) or "_n/a_")
            .replace("{{root_cause}}", finding.get("root_cause") or "_pending_")
            .replace("{{mitigation}}", finding.get("mitigation") or "_pending_")
            .replace("{{lessons_learned}}", finding.get("lessons_learned") or "_none recorded_")
            .replace("{{originated_by}}", finding.get("provenance", {}).get("originated_by", "unknown"))
            .replace("{{triaged_by}}", finding.get("provenance", {}).get("triaged_by") or "unreviewed")
            .replace("{{reviewed_by}}", ", ".join(finding.get("reviewed_by", [])) or "none")
            )


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__, file=sys.stderr)
        return 1
    finding = json.loads(Path(args[0]).read_text())
    artifact = observation = None
    if "--artifact" in args:
        artifact = json.loads(Path(args[args.index("--artifact") + 1]).read_text())
    if "--observation" in args:
        observation = json.loads(Path(args[args.index("--observation") + 1]).read_text())
    schema = json.loads((ROOT / "contracts" / "finding.schema.json").read_text())
    try:
        validate(finding, schema)
    except ValidationError as e:
        print(f"REFUSED: finding violates contract: {e}", file=sys.stderr)
        return 1
    out = render(finding, artifact, observation)
    if "-o" in args:
        dest = Path(args[args.index("-o") + 1])
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(out)
        print(f"rendered -> {dest}")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
