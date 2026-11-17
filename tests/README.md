# AEGIS Test Suite

Tests that **drive the development** of the AEGIS research workbench. They are
written against `.agents/curriculum.json` (the authoritative specification) and
`.agents/plans/init.md` (the intended module layout) — *not* against any existing
implementation. All `core.*` tests are expected to fail (red) until the modules
they specify are implemented.

## Running

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest            # full suite
.venv/bin/pytest tests/unit/test_policy.py   # one module
```

## Scope — curriculum phases covered

| Test file | Phase / week | Acceptance criteria exercised |
|---|---|---|
| `unit/test_contracts_conform_to_curriculum.py` | P01.W2, P02.W3, P03.W9 | Schemas implement `canonical_record_contracts` exactly; draft 2020-12; closed (`additionalProperties: false`); finding lifecycle enum; minimum run metadata; tool requests carry no self-authorization fields |
| `unit/test_contract_roundtrip.py` | P02.W3 | Pydantic models mirror the schemas: serialize → schema-valid; reject missing/undeclared fields |
| `unit/test_mission.py` | P01.W1, P02.W3 | Mission contract, approval states, time windows, disjoint allow/exclude actions; `load_mission` fails safely on malformed/incomplete input |
| `unit/test_scope.py` | P01.W1 | Scope manifests: default-deny network, no wildcards, local-target classes only, recorded human approval, expiry, stop conditions; resolver denies by default (unregistered/unapproved/revoked/expired mission, unknown scope, target expansion, disallowed/excluded operations) |
| `unit/test_policy.py` | P01.W1, P03.W8 | Tool broker: deny-by-default, fail-closed on malformed requests, forged approval fields never grant authority, consequential actions require recorded human approval, emergency stop, audit attribution |
| `unit/test_audit.py` | P03.W8 | Append-only hash-chained log; tamper and deletion detection; executions attributable to mission + run; no secret-bearing fields |
| `unit/test_evidence_store.py` | P01.W2 | SHA-256 content addressing, dedup, verify-after-store-and-retrieval, tamper detection, mandatory provenance metadata, raw/derived separation |
| `unit/test_run_manifest.py` | P01.W2 | Append-only run manifest; rewrite/deletion detection; duplicate record ids rejected |
| `unit/test_orchestrator.py` | P01 exit, P02.W3 | No run without a valid approved mission + scope; metadata-complete run records (schema-valid); "no observation without a preserved artifact or an explicit reason"; one-way lifecycle state machine |
| `unit/test_graph_schema.py` | P01.W2 | Initial Memgraph schema: required labels/relationships, uniqueness constraints, provenance properties, no secret-bearing properties |
| `integration/test_cli.py` | P02.W3 | `mission validate` and `run start` end-to-end; schema-valid run manifests; fail-safe structured errors; deterministic validate output; no partial output on refusal |

## Target API contract

The tests define the following public surface (module → symbols). Implementation
should treat this as the spec; deviations require updating the tests deliberately,
not quietly.

### `core.mission`
- `Mission`, `ApprovalState` (`draft|approved|revoked`), `MissionValidationError`
- `load_mission(path: Path) -> Mission` — schema-validating loader; raises
  `MissionValidationError` for unreadable files, malformed JSON, and schema/model
  violations (never leaks `JSONDecodeError`/`FileNotFoundError`).
- Validation rules: tz-aware datetimes only; `expiry_time > start_time`;
  `allowed_actions ∩ excluded_actions = ∅`; ids match `[A-Za-z0-9][A-Za-z0-9._-]*`;
  `schema_version` pinned to the curriculum's `"1.0.0"`.

### `core.scope`
- `ScopeManifest` — `network.default` must be `"deny"`; wildcard destinations
  (`*`, `0.0.0.0/0`, `::/0`) rejected; `target_class` restricted to local
  classes (`local_vm`, `local_container`, `local_process`, `emulated_device`,
  `emulated_firmware`); `approved_by`/`approved_at`/`expires_at`/non-empty
  `stop_conditions` required.
- `ScopeResolver(missions, scopes, *, clock)` with
  `assert_authorized(mission, target_asset_id, operation) -> Decision`
  (never raises). `Decision` carries `decision`, `reason`, `rule`.
- Denial rules (each a distinct `rule` id): `mission_not_registered`,
  `mission_not_approved`, `mission_revoked`, `mission_expired`,
  `scope_expired`, `target_not_in_scope`, `operation_not_allowed`,
  `operation_excluded`.

### `core.policy`
- `ToolRequest` (canonical contract), `PolicyDecision`, `PolicyEngine`
- `PolicyEngine(missions, scopes, *, audit, clock)` with:
  - `decide(request | mapping, *, approval_token=None) -> PolicyDecision` —
    **never raises**; malformed input → `decision="deny"`, `rule="malformed_request"`.
  - `record_human_approval(*, approval_token, mission_id, approved_by, approved_at)`
  - `emergency_stop(reason: str)`, `resume(*, approved_by, approved_at, note)`
  - `halted: bool`
- Rule ids: `malformed_request`, `mission_not_found`, `mission_not_approved`,
  `mission_revoked`, `mission_expired`, `target_not_in_scope`,
  `operation_not_allowed`, `operation_excluded`, `approval_required`,
  `emergency_stop`. Outcomes: `allow` / `deny` / `require_approval`.
- Any request field outside the ToolRequest contract (e.g. a forged
  `policy_decision`) makes the request malformed → deny.

### `core.audit`
- `AuditLog(path, *, clock)` with `append(event)`, `events()`, `verify() -> bool`.
- `AuditEvent`: chain fields `prev_hash`/`entry_hash` (genesis = `"0"*64`);
  `event_type="tool.execution"` requires non-null `mission_id` and `agent_run_id`.
- Event types used: `policy.decision`, `human_approval`, `emergency_stop`,
  `resume`.

### `core.evidence`
- `ArtifactStore(root, *, clock)`: `put(data, *, media_type,
  source_tool_or_agent, mission_id, agent_run_id, kind="raw") -> Artifact`,
  `get(artifact_id, *, kind="raw")`, `verify(artifact_id, *, kind="raw")`,
  `verify_all() -> list[tuple[artifact_id, kind]]`, `artifacts()`.
- Layout: `objects/<kind>/<sha256[:2]>/<sha256>`; identical bytes dedupe per
  kind so raw and derived artifacts are preserved separately.
- `kind` limited to `raw|derived`. Empty provenance metadata → `ValidationError`.
- `get` re-verifies content: tampered object → `IntegrityError`.
- `RunManifest(path, *, clock)`: `append(record, *, record_id)`,
  `records()`, `verify()`; duplicate ids → `DuplicateRecordError`.
- Exceptions: `IntegrityError`, `ArtifactNotFoundError`, `DuplicateRecordError`.

### `core.orchestrator`
- `Orchestrator(*, policy, audit, store, run_manifest, clock)`
- `start_run(mission, *, agent_role, harness_name, harness_version, model_id,
  effort_level, prompt_config_hash, tool_versions, target_snapshot_hash) -> AgentRun`
- `record_observation(agent_run_id, *, target_asset_id, observation_type,
  description, method, source_artifact_ids, direct_or_derived="direct",
  missing_artifact_reason=None) -> Observation` — empty `source_artifact_ids`
  require a non-empty `missing_artifact_reason`; cited artifacts must exist in
  the store.
- `finish_run(agent_run_id, *, outcome) -> AgentRun` — appends the completed
  record to the run manifest (schema-valid against `contracts/run.schema.json`).
- `run_state(agent_run_id) -> RunState` (`planned→running→concluded` is one-way).
- Exceptions: `RunNotAuthorized`, `InvalidRunState`,
  `ObservationValidationError`.
- Models re-exported here: `AgentRun`, `Observation`.

### `adapters.cli` (`python -m adapters.cli.main`, console script `aegis`)
```
aegis mission validate <mission.json>
aegis run start --mission M.json --scope S.json --output OUT.json
                --workdir DIR [--now ISO-8601]
```
Exit codes: `0` success, `1` error, `2` usage. Stdout is always machine-readable:
`{"ok": true, ...}` or `{"ok": false, "error": {"code": ..., "message": ...}}`.
Error codes: `invalid_json`, `schema_violation`, `not_authorized`,
`file_not_found`. `run start` writes the schema-valid run record to
`--output` (nothing partial on refusal) and an append-only `audit.jsonl` under
`--workdir`. The CLI must inject the fixed clock from `--now` so output is
reproducible.

### `graph/schema.cypher`
Node labels `Mission`, `AgentRun`, `Artifact`, `Observation`, `Scope`;
relationships `AUTHORIZED_BY`, `PRODUCES`, `OBSERVES`, `DERIVED_FROM`;
uniqueness constraints on `mission_id`, `agent_run_id`, `sha256`; provenance
properties present; no secret-bearing property names.

## Conventions and decisions

1. **The curriculum wins.** Where `.agents/plans/init.md` and
   `curriculum.json` disagree, tests follow the curriculum. Known resolutions:
   - run record id is `agent_run_id` (curriculum `AgentRun`), not `run_id`;
   - mission fields follow `canonical_record_contracts.Mission`
     (`target_asset_ids`, `objectives`, `approval_state`, …), not the plan's
     earlier sketch;
   - the finding state machine is the curriculum's nine-state
     `finding_lifecycle`, not the plan's four-state ladder;
   - graph node label is `AgentRun`, not `Run`.
2. **Determinism.** Every component accepts an injected clock (`FixedClock` in
   `conftest.py`); tests never sleep and never read wall-clock time.
3. **Fail closed.** Anything the policy engine cannot fully parse is a denial,
   never an exception and never an allow.
4. **Fixtures carry the scenario.** `conftest.py` builders encode exactly one
   approved local-lab mission; tests override single fields to make payloads
   invalid, so valid data has a single source of truth.

## Next phases (not yet covered)

- P03.W9: adapter conformance (MCP + CLI consuming identical contracts;
  unsupported adapters fail closed).
- P04+: `Finding` lifecycle transitions and independent review gating;
  hypothesis ledger; worker interface (`run(task) → observations + artifacts`);
  `evals/` research corpus and harness benchmarks.
