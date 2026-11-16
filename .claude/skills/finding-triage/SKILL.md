---
name: finding-triage
description: Epistemic classifier for research output. Use whenever observations, hypotheses or candidate findings must be classified, promoted, demoted or rejected — the gate between observation and confirmed finding (Verify/Improve).
---

# Skill: Finding Triage

The epistemic classifier. Its only allegiance is to the evidence. Triage decides what
something **is** on the ladder — never how impressive it sounds.

## Inputs

- Observations (contract: `observation.schema.json`) with complete evidence chains.
- Hypotheses (contract: `finding.schema.json`, status `hypothesis`).
- The graph context for the component (prior findings, root causes, related work).

## Procedure

1. **Verify the evidence chain first.** An observation with missing artifacts or
   broken custody is **invalid input** — return it to the evidence-curator, do not
   triage it.
2. **Classify each record** against the ladder:
   - `observation` — reproducible fact, no claim attached.
   - `hypothesis` — claimed weakness, unverified: MUST have rationale + verification
     plan.
   - `confirmed` — reproduced ≥1 time with a complete evidence chain; severity
     assigned WITH justification; `root_cause` and `mitigation` required before the
     finding is final.
   - `rejected` — refuted: MUST cite refuting evidence; the refutation is preserved.
3. **State the transition condition** for every record: what evidence would change
   its classification. A triage decision without a transition condition is incomplete.
4. **Severity with justification**: severity describes impact *given the evidence*;
   unverified reachability caps severity and the cap is stated.
5. **Record lessons learned**: if this triage revealed a method gap (a worker that
   should have caught this earlier, an inventory blind spot), write it — it feeds
   Evolve.

## Outputs

- Updated finding records with status, justification, transition conditions.
- Rejected records with refuting evidence (preserved, never deleted).
- Lessons-learned entries for the graph (`Lesson` nodes).

## Quality bar

- Zero promotions to `confirmed` without a reproduction observation.
- Every rejected record has evidence — "didn't reproduce" alone is not a rejection,
  it is an unresolved hypothesis.
- Severity claims are checkable against the cited evidence.

## Failure modes

- Triage inflation: promoting on a single low-fidelity observation.
- Deleting refuted hypotheses instead of preserving refutations.
- Treating triage as severity theater (Loud words, weak chain).
