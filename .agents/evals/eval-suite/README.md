# AEGIS Heuristic Eval Suite

Simple, deterministic, heuristic checks over the codebase that answer one question:
**is the agent doing the right thing?** They compare repository state and agent
artifacts against the behavior mandated by `.agents/plans/init.md` and the mission in
`.agents/evals/goal.md`.

## Design principles

1. **Heuristics, not proofs.** Each check is a cheap pattern over files/content that
   correlates strongly with the required property. Known blind spots are listed below.
2. **Binary pass/fail.** A check either holds or doesn't; no subjective scoring.
3. **Fail = information.** A failing check on unstarted work is the expected baseline;
   the suite doubles as the phase-completion checklist.
4. **No dependencies.** The runner is stdlib-only Python so it runs on any machine the
   agent has, including a bare environment.
5. **Registry/runner drift is a failure.** A heuristic registered in `heuristics.json`
   without an implementation reports `NO IMPLEMENTATION` and fails.

## Suites & gates

| Suite    | Gate | Why |
|----------|------|-----|
| safety   | 100% | Authorization + evidence integrity outrank everything |
| contracts| 100% | Schemas are the type system; invalid contracts corrupt everything downstream |
| process  | 100% | An un-updated ledger means the loop didn't happen |
| harness  | 100% | Agents/skills/rules must always be loadable |
| evidence | ≥90% | Near-perfect required once populated |
| graph    | ≥80% | May lag code phases, must converge |
| research | ≥50% | Corpus grows across phases |

Exit code is non-zero when any gate is unmet — the work loop treats that as a red
gate and must fix before new capability (see `init.md` §5 rule 3).

## Running

```bash
python3 .agents/evals/eval-suite/run_evals.py
```

Results go to `.agents/evals/results/latest.json` (overwritten) and
`results/history.jsonl` (append-only, includes commit hash — the pass-rate trend is
the "Evolve" capability made measurable).

## Adding a heuristic

1. Add an entry to `heuristics.json` (`id`, `capability`, `description`).
2. Implement `h_<name>() -> (bool, str)` in `run_evals.py` and register it in `CHECKS`.
3. Commit both in the same iteration (registry/runner drift fails by design).

## Known blind spots (documented, not hidden)

- Secret patterns catch credential-*shaped* strings only; a secret in an unusual
  format (e.g., base64 in a "notes" field) can pass. Mitigation: `.gitignore` +
  human review before anything sensitive enters the repo.
- The IPv4 heuristic exempts all `172.*` (true private range is `172.16–31.*`) and
  cannot detect hostnames. It is a tripwire, not a firewall; `core/scope.py` remains
  the enforcement point.
- Content heuristics (README documents architecture, rules contain MUST) prove
  presence, not quality — deep review is the reviewer agent's job per `.claude/`.
