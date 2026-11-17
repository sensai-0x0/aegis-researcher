# ui/orb — AEGIS status surface

Minimal, dependency-free status surface (single static HTML, data embedded).
Named for the curriculum's graph_stack visualization (Orb/Memgraph) — the live
graph view belongs to the graph thread; this surface shows **platform state**:
eval suite health, current phase, latest results.

## Regenerate

```bash
python3 ui/orb/generate_status.py
```

Reads `.agents/evals/results/latest.json` + the progress ledger and rewrites
`status.html` (self-contained) and `status.json`. Safe to run any time; it is
a read-only view — it never mutates research state.
