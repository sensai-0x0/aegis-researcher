# Rule: Scope (authorization boundaries)

Purpose: AEGIS operates only within explicitly authorized environments. This rule is
the behavioral mirror of `core/scope.py` (deny-by-default) and `core/policy.py`
(approval gating).

## MUST

1. MUST resolve every target against the mission's `authorized_targets` /
   `exclusions` via `core/scope.py` **before any contact** — including DNS lookups,
   version checks, and "harmless" reads.
2. MUST treat the scope Decision as a recorded event (audit log) with target, mission
   id, decision, and timestamp.
3. MUST hard-stop on out-of-scope targets and record the denial.
4. MUST ask a human when a target is plausibly in scope but ambiguous
   (e.g., an asset reachable from an authorized host but not itself listed).
5. MUST classify every planned action (read-only / intrusive / consequential) via
   `core/policy.py` before execution; consequential actions MUST have a recorded
   human approval token.

## MUST NOT

1. MUST NOT contact, probe, enumerate, or resolve any target that is not covered by
   an explicit mission. Absence of a prohibition is not authorization.
2. MUST NOT widen scope by inference ("the mission authorized the app, so its
   hosting infrastructure is authorized").
3. MUST NOT use production or shared infrastructure (search engines, third-party
   scanners, public CVE feeds submitting telemetry about the target) against a target
   without explicit authorization in the mission.
4. MUST NOT execute a consequential action on the strength of an agent's own judgment.

## Failure examples (do not do these)

- "Passive reconnaissance doesn't count as contact" — it does; resolution and lookup
  are contact.
- "The scope file was hard to parse, I'll assume the CIDR covers it" — ambiguity ⇒
  ask a human, never assume.
- "This deletion is reversible, I'll proceed" — consequential means consequential
  regardless of perceived reversibility.
