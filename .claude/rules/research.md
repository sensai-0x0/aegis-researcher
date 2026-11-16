# Rule: Research Method (hypothesis-driven discipline)

Purpose: every research activity in AEGIS begins as a hypothesis, executes a method,
and ends in evidence — or in a *recorded* negative result. Fishing expeditions and
volume-driven scanning are prohibited.

## MUST

1. Every research activity MUST begin with a written hypothesis stating:
   what is claimed, why it is plausible, and what evidence would confirm or refute it.
2. Every hypothesis MUST name the worker/method that will produce the evidence and
   the target it will run against (which must be in-scope).
3. Negative results MUST be recorded: a refuted hypothesis is knowledge and feeds the
   graph as a rejected finding.
4. Each activity MUST end in observations tied to artifacts, never in prose-only notes.
5. Coverage gaps discovered during research MUST be recorded for the graph
   (`components with zero observations`).

## MUST NOT

1. MUST NOT run tools "to see what turns up" without a stated hypothesis.
2. MUST NOT continue a method that has produced no observations for its stated
   purpose without recording why (budget/threshold rules live in the mission).
3. MUST NOT reuse a method unmodified after it failed once — adapt and record the
   adaptation as a lesson learned.
4. MUST NOT report activity metrics (scans run, tools called) as results.

## Failure examples (do not do these)

- *"I ran a port scan of the whole /24 to get a feel for the environment"* — no
  hypothesis, no scope decision recorded per target.
- *"The endpoint is probably vulnerable to X, I'll note it as high severity"* —
  probability is a hypothesis tier, not a severity, and never a finding.
- *"Testing didn't reproduce it, moving on"* — without recording the refutation
  evidence, the next agent wastes an iteration rediscovering it.
