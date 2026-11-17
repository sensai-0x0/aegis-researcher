# Adapter: Codex

Same interface, same contracts, different harness packaging (Codex-style CLI
agent loop). Identical boundary guarantee: no policy/scope/evidence logic in
the adapter — the core owns every decision (curriculum P03 exit: harness-
independent core; unsupported adapters fail closed, supported ones share the
canonical contracts).
