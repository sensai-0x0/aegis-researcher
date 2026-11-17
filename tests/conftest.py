"""Shared fixtures and payload builders for the AEGIS test suite.

The builders encode one canonical, fully authorized local-lab scenario derived
from `.agents/curriculum.json` (P01.W1 deliverable: "one approved local
mission"). Every payload matches the curriculum's ``canonical_record_contracts``
field lists exactly; individual tests override single fields to make payloads
invalid, so there is exactly one source of truth for valid data.

Imports of ``core.*`` modules are deliberately lazy (inside fixtures and test
functions): contract-level tests must stay runnable even before the Python core
exists, while core tests fail with a clear ImportError during TDD red phase.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_DIR = REPO_ROOT / "contracts"
CURRICULUM_PATH = REPO_ROOT / ".agents" / "curriculum.json"

UTC = timezone.utc
CLOCK_NOW = datetime(2026, 11, 17, 9, 0, 0, tzinfo=UTC)

MISSION_START = "2026-11-17T00:00:00+00:00"
MISSION_EXPIRY = "2026-11-24T00:00:00+00:00"
SCOPE_EXPIRY = "2026-11-30T00:00:00+00:00"
SCOPE_APPROVED_AT = "2026-11-16T12:00:00+00:00"
REQUEST_CREATED_AT = "2026-11-17T09:00:00+00:00"

PROMPT_CONFIG_HASH = hashlib.sha256(b"prompt-config-v1").hexdigest()
TARGET_SNAPSHOT_HASH = hashlib.sha256(b"lab-vm-snapshot-v1").hexdigest()


class FixedClock:
    """Deterministic clock; the implementation must accept it wherever 'now' is needed."""

    def __init__(self, start: datetime | None = None) -> None:
        self._now = start or CLOCK_NOW

    def __call__(self) -> datetime:
        return self._now

    def advance(self, **kwargs: float) -> None:
        self._now = self._now + timedelta(**kwargs)

    def set(self, when: datetime) -> None:
        self._now = when


def without(payload: dict[str, Any], *keys: str) -> dict[str, Any]:
    """Copy of a payload with the given keys removed (for missing-field tests)."""
    return {key: value for key, value in payload.items() if key not in keys}


# ---------------------------------------------------------------------------
# Canonical payloads
# ---------------------------------------------------------------------------


def mission_payload(**overrides: Any) -> dict[str, Any]:
    """An approved, unexpired mission targeting only the pinned local lab VM."""
    payload: dict[str, Any] = {
        "mission_id": "mission-local-lab-0001",
        "title": "Inventory the pinned local lab VM",
        "target_asset_ids": ["asset-vm-lab-0001"],
        "scope_id": "scope-local-lab-0001",
        "objectives": ["Produce a repeatable inventory of the pinned local lab VM"],
        "allowed_actions": [
            "inventory.read",
            "process.list",
            "file.stat",
            "artifact.store",
        ],
        "excluded_actions": ["network.connect", "file.write", "process.kill"],
        "start_time": MISSION_START,
        "expiry_time": MISSION_EXPIRY,
        "stop_conditions": [
            "Any contact with a target other than asset-vm-lab-0001",
            "Operator abort",
        ],
        "approval_state": "approved",
        "created_by": "human-owner",
        "schema_version": "1.0.0",
    }
    return {**payload, **overrides}


def scope_payload(**overrides: Any) -> dict[str, Any]:
    """A human-approved, default-deny scope manifest for the same local lab."""
    payload: dict[str, Any] = {
        "scope_id": "scope-local-lab-0001",
        "name": "Isolated local lab",
        "target_asset_ids": ["asset-vm-lab-0001"],
        "target_class": "local_vm",
        "network": {"default": "deny", "allowed_destinations": []},
        "allowed_actions": [
            "inventory.read",
            "process.list",
            "file.stat",
            "artifact.store",
        ],
        "excluded_actions": ["network.connect", "file.write", "process.kill"],
        "expires_at": SCOPE_EXPIRY,
        "stop_conditions": ["Operator abort"],
        "approved_by": "human-owner",
        "approved_at": SCOPE_APPROVED_AT,
        "schema_version": "1.0.0",
    }
    return {**payload, **overrides}


def tool_request_payload(**overrides: Any) -> dict[str, Any]:
    """A read-only ToolRequest inside the mission's allowed actions."""
    payload: dict[str, Any] = {
        "request_id": "request-local-lab-0001",
        "mission_id": "mission-local-lab-0001",
        "agent_run_id": "agent-run-local-lab-0001",
        "tool_id": "system_inventory",
        "target_asset_id": "asset-vm-lab-0001",
        "operation": "inventory.read",
        "parameters": {"path": "/etc/os-release"},
        "declared_side_effects": [],
        "expected_artifacts": ["os-release-snapshot"],
        "approval_requirement": "not_required",
        "created_at": REQUEST_CREATED_AT,
        "schema_version": "1.0.0",
    }
    return {**payload, **overrides}


def run_payload(**overrides: Any) -> dict[str, Any]:
    """A completed AgentRun carrying the curriculum's minimum run metadata."""
    payload: dict[str, Any] = {
        "agent_run_id": "agent-run-local-lab-0001",
        "mission_id": "mission-local-lab-0001",
        "agent_role": "systems_analyst",
        "harness_name": "claude-code",
        "harness_version": "1.0.0",
        "model_id": "claude-sonnet-5-5",
        "effort_level": "high",
        "prompt_config_hash": PROMPT_CONFIG_HASH,
        "tool_versions": {"system_inventory": "0.1.0"},
        "target_snapshot_hash": TARGET_SNAPSHOT_HASH,
        "start_time": REQUEST_CREATED_AT,
        "end_time": "2026-11-17T09:30:00+00:00",
        "outcome": "completed",
        "artifact_ids": [],
        "schema_version": "1.0.0",
    }
    return {**payload, **overrides}


def observation_payload(**overrides: Any) -> dict[str, Any]:
    """A direct observation backed by a preserved raw artifact."""
    digest = hashlib.sha256(b"raw evidence bytes").hexdigest()
    payload: dict[str, Any] = {
        "observation_id": "observation-local-lab-0001",
        "mission_id": "mission-local-lab-0001",
        "agent_run_id": "agent-run-local-lab-0001",
        "target_asset_id": "asset-vm-lab-0001",
        "observed_at": REQUEST_CREATED_AT,
        "observation_type": "filesystem",
        "description": "/etc/os-release reports the pinned lab image",
        "method": "read /etc/os-release via the approved inventory tool",
        "source_artifact_ids": [digest],
        "direct_or_derived": "direct",
        "schema_version": "1.0.0",
    }
    return {**payload, **overrides}


def finding_payload(**overrides: Any) -> dict[str, Any]:
    """A candidate finding (P04 will exercise the full lifecycle)."""
    digest = hashlib.sha256(b"raw evidence bytes").hexdigest()
    payload: dict[str, Any] = {
        "finding_id": "finding-local-lab-0001",
        "mission_id": "mission-local-lab-0001",
        "affected_asset_ids": ["asset-vm-lab-0001"],
        "affected_component_ids": ["component-labhttpd"],
        "weakness_classification": "CWE-521",
        "preconditions": "Local shell access on the pinned lab VM",
        "impact_rationale": "Weak default credentials allow unauthorized lab access",
        "supporting_artifact_ids": [digest],
        "reproduction_experiment_ids": ["experiment-local-lab-0001"],
        "verification_state": "candidate",
        "review_id": "review-local-lab-0001",
        "remediation": "Require operator-set credentials on first boot",
        "created_at": REQUEST_CREATED_AT,
        "schema_version": "1.0.0",
    }
    return {**payload, **overrides}


def artifact_payload(**overrides: Any) -> dict[str, Any]:
    """A raw artifact record as the evidence vault must represent it."""
    data = b"raw evidence bytes"
    digest = hashlib.sha256(data).hexdigest()
    payload: dict[str, Any] = {
        "artifact_id": digest,
        "sha256": digest,
        "media_type": "text/plain",
        "byte_length": len(data),
        "storage_uri": f"file://objects/raw/{digest[:2]}/{digest}",
        "source_tool_or_agent": "evidence_curator",
        "mission_id": "mission-local-lab-0001",
        "agent_run_id": "agent-run-local-lab-0001",
        "created_at": REQUEST_CREATED_AT,
        "integrity_verified": True,
        "schema_version": "1.0.0",
    }
    return {**payload, **overrides}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock()


@pytest.fixture(scope="session")
def curriculum() -> dict[str, Any]:
    """The curriculum document — the source of truth for every contract test."""
    return json.loads(CURRICULUM_PATH.read_text())


@pytest.fixture(scope="session")
def schema_for() -> Callable[[str], dict[str, Any]]:
    """Load (and cache) a JSON Schema from contracts/ by short name."""
    cache: dict[str, dict[str, Any]] = {}

    def _load(name: str) -> dict[str, Any]:
        if name not in cache:
            path = CONTRACTS_DIR / f"{name}.schema.json"
            cache[name] = json.loads(path.read_text())
        return cache[name]

    return _load


@pytest.fixture(scope="session")
def assert_schema_valid() -> Callable[[str, Any], None]:
    """Assert an instance validates against contracts/<name>.schema.json."""

    def _assert(name: str, instance: Any) -> None:
        from jsonschema import Draft202012Validator

        schema = json.loads((CONTRACTS_DIR / f"{name}.schema.json").read_text())
        errors = sorted(
            Draft202012Validator(schema).iter_errors(instance),
            key=lambda error: list(error.absolute_path),
        )
        assert not errors, "\n".join(
            f"{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
            for error in errors
        )

    return _assert


@pytest.fixture
def make_mission() -> Callable[[], dict[str, Any]]:
    return mission_payload


@pytest.fixture
def make_scope() -> Callable[[], dict[str, Any]]:
    return scope_payload


@pytest.fixture
def make_tool_request() -> Callable[[], dict[str, Any]]:
    return tool_request_payload


@pytest.fixture
def make_run_record() -> Callable[[], dict[str, Any]]:
    return run_payload


@pytest.fixture
def make_observation() -> Callable[[], dict[str, Any]]:
    return observation_payload


@pytest.fixture
def make_finding() -> Callable[[], dict[str, Any]]:
    return finding_payload


@pytest.fixture
def make_artifact() -> Callable[[], dict[str, Any]]:
    return artifact_payload


@pytest.fixture
def run_kwargs() -> dict[str, Any]:
    """Keyword arguments for Orchestrator.start_run other than the mission."""
    return {
        "agent_role": "systems_analyst",
        "harness_name": "claude-code",
        "harness_version": "1.0.0",
        "model_id": "claude-sonnet-5-5",
        "effort_level": "high",
        "prompt_config_hash": PROMPT_CONFIG_HASH,
        "tool_versions": {"system_inventory": "0.1.0"},
        "target_snapshot_hash": TARGET_SNAPSHOT_HASH,
    }


@pytest.fixture
def bundle(make_orchestrator) -> SimpleNamespace:
    """A pre-wired orchestrator around the canonical approved mission."""
    return make_orchestrator()


@pytest.fixture
def audit_path(tmp_path: Path) -> Path:
    return tmp_path / "audit.jsonl"


@pytest.fixture
def make_orchestrator(
    tmp_path: Path,
    clock: FixedClock,
    make_mission: Callable[[], dict[str, Any]],
    make_scope: Callable[[], dict[str, Any]],
) -> Callable[..., SimpleNamespace]:
    """Build a fully wired orchestrator bundle around one approved mission.

    Returns a SimpleNamespace with ``orchestrator``, ``mission``, ``scope``,
    ``store`` and ``audit`` so tests can create artifacts through the same
    store the orchestrator validates against.
    """

    def _make(
        *,
        mission_overrides: dict[str, Any] | None = None,
        scope_overrides: dict[str, Any] | None = None,
    ) -> SimpleNamespace:
        from core.audit import AuditLog
        from core.evidence import ArtifactStore, RunManifest
        from core.mission import Mission
        from core.orchestrator import Orchestrator
        from core.policy import PolicyEngine
        from core.scope import ScopeManifest

        mission = Mission.model_validate(make_mission(**(mission_overrides or {})))
        scope = ScopeManifest.model_validate(make_scope(**(scope_overrides or {})))
        audit = AuditLog(tmp_path / "audit.jsonl", clock=clock)
        store = ArtifactStore(tmp_path / "evidence", clock=clock)
        run_manifest = RunManifest(tmp_path / "manifests" / "runs.jsonl", clock=clock)
        policy = PolicyEngine(
            missions=[mission], scopes=[scope], audit=audit, clock=clock
        )
        orchestrator = Orchestrator(
            policy=policy, audit=audit, store=store, run_manifest=run_manifest, clock=clock
        )
        return SimpleNamespace(
            orchestrator=orchestrator,
            mission=mission,
            scope=scope,
            store=store,
            audit=audit,
        )

    return _make


# ---------------------------------------------------------------------------
# CLI subprocess helper
# ---------------------------------------------------------------------------


def _run_cli_subprocess(*args: str) -> subprocess.CompletedProcess[str]:
    """Invoke the CLI in a subprocess so exit codes and output files are real."""
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    return subprocess.run(
        [sys.executable, "-m", "adapters.cli.main", *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env=env,
        timeout=60,
        check=False,
    )


@pytest.fixture
def run_cli() -> Callable[..., subprocess.CompletedProcess[str]]:
    return _run_cli_subprocess
