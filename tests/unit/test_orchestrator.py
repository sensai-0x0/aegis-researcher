"""Orchestrator: run lifecycle and record emission — P02.W3 "Python research core".

Curriculum criteria under test:
- P02.W3: "Build a CLI that accepts a mission file and emits a structured run
  manifest." (the orchestrator produces the manifest the CLI surfaces)
- P01 exit: "Every recorded result references a preserved raw artifact or
  explicitly states why none exists."
- P01.W1: "A test cannot begin without a valid scope record."
- evidence_contract.minimum_run_metadata — the emitted run record must carry it.
"""

from __future__ import annotations

import pytest


def _start(bundle, run_kwargs):
    return bundle.orchestrator.start_run(bundle.mission, **run_kwargs)


# ---------------------------------------------------------------------------
# Run lifecycle
# ---------------------------------------------------------------------------


def test_start_run_creates_a_metadata_complete_agent_run(bundle, run_kwargs, clock) -> None:
    from core.orchestrator import AgentRun, RunState

    run = _start(bundle, run_kwargs)
    assert isinstance(run, AgentRun)
    assert run.agent_run_id
    assert run.mission_id == bundle.mission.mission_id
    assert run.scope_id == bundle.scope.scope_id
    assert run.agent_role == "systems_analyst"
    assert run.harness_name == "claude-code"
    assert run.model_id == "claude-sonnet-5-5"
    assert run.prompt_config_hash == run_kwargs["prompt_config_hash"]
    assert run.target_snapshot_hash == run_kwargs["target_snapshot_hash"]
    assert run.start_time == clock()
    assert run.end_time is None
    assert bundle.orchestrator.run_state(run.agent_run_id) is RunState.RUNNING


def test_start_run_refuses_unapproved_mission(
    make_orchestrator, run_kwargs
) -> None:
    """A test cannot begin without a valid scope record" — and an approval."""
    from core.orchestrator import RunNotAuthorized

    bundle = make_orchestrator(mission_overrides={"approval_state": "draft"})
    with pytest.raises(RunNotAuthorized):
        _start(bundle, run_kwargs)


def test_start_run_refuses_out_of_scope_mission(make_orchestrator, run_kwargs) -> None:
    """A mission targeting an asset its scope does not cover cannot start."""
    from core.orchestrator import RunNotAuthorized

    bundle = make_orchestrator(
        mission_overrides={"target_asset_ids": ["asset-vm-lab-0002"]}
    )
    with pytest.raises(RunNotAuthorized):
        _start(bundle, run_kwargs)


def test_start_run_refuses_expired_mission(make_orchestrator, run_kwargs, clock) -> None:
    from datetime import datetime, timezone

    from core.orchestrator import RunNotAuthorized

    clock.set(datetime(2026, 11, 25, 0, 0, 0, tzinfo=timezone.utc))
    bundle = make_orchestrator()
    with pytest.raises(RunNotAuthorized):
        _start(bundle, run_kwargs)


def test_run_lifecycle_is_a_one_way_state_machine(bundle, run_kwargs) -> None:
    from core.orchestrator import InvalidRunState

    orchestrator = bundle.orchestrator
    with pytest.raises(InvalidRunState):
        orchestrator.finish_run("agent-run-never-started", outcome="completed")

    run = _start(bundle, run_kwargs)
    orchestrator.finish_run(run.agent_run_id, outcome="completed")
    with pytest.raises(InvalidRunState):
        orchestrator.finish_run(run.agent_run_id, outcome="completed")


def test_finish_run_completes_the_record_and_writes_the_manifest(
    bundle, run_kwargs, assert_schema_valid
) -> None:
    """emits a structured run manifest" — schema-valid and metadata-complete."""
    from core.orchestrator import AgentRun

    run = _start(bundle, run_kwargs)
    finished = bundle.orchestrator.finish_run(run.agent_run_id, outcome="completed")
    assert isinstance(finished, AgentRun)
    assert finished.end_time is not None
    assert finished.outcome == "completed"
    assert finished.artifact_ids == []

    manifest_records = bundle.orchestrator.run_manifest.records()
    assert manifest_records, "finished run must be appended to the run manifest"
    record = next(
        r
        for r in manifest_records
        if r["agent_run_id"] == run.agent_run_id
    )
    assert record["mission_id"] == bundle.mission.mission_id
    assert_schema_valid("run", record)


def test_run_lifecycle_transitions_are_recorded_in_audit(bundle, run_kwargs) -> None:
    start_count = len(bundle.audit.events())
    run = _start(bundle, run_kwargs)
    bundle.orchestrator.finish_run(run.agent_run_id, outcome="completed")
    assert len(bundle.audit.events()) > start_count


# ---------------------------------------------------------------------------
# Observations
# ---------------------------------------------------------------------------


def _observe(orchestrator, agent_run_id, **overrides):
    kwargs = {
        "target_asset_id": "asset-vm-lab-0001",
        "observation_type": "filesystem",
        "description": "/etc/os-release reports the pinned lab image",
        "method": "read /etc/os-release via the approved inventory tool",
        "source_artifact_ids": [],
        "direct_or_derived": "direct",
    }
    kwargs.update(overrides)
    return orchestrator.record_observation(agent_run_id, **kwargs)


def test_observation_requires_a_preserved_artifact(bundle, run_kwargs) -> None:
    """Every recorded result references a preserved raw artifact ... or
    explicitly states why none exists."""
    from core.orchestrator import ObservationValidationError

    run = _start(bundle, run_kwargs)
    artifact = bundle.store.put(
        b"inventory snapshot",
        media_type="text/plain",
        source_tool_or_agent="system_inventory",
        mission_id=bundle.mission.mission_id,
        agent_run_id=run.agent_run_id,
    )
    observation = _observe(
        bundle.orchestrator,
        run.agent_run_id,
        source_artifact_ids=[artifact.artifact_id],
    )
    assert observation.source_artifact_ids == [artifact.artifact_id]
    assert observation.mission_id == bundle.mission.mission_id
    assert observation.agent_run_id == run.agent_run_id


def test_observation_without_artifact_requires_explicit_reason(
    bundle, run_kwargs
) -> None:
    from core.orchestrator import ObservationValidationError

    run = _start(bundle, run_kwargs)
    with pytest.raises(ObservationValidationError):
        _observe(bundle.orchestrator, run.agent_run_id, source_artifact_ids=[])

    observation = _observe(
        bundle.orchestrator,
        run.agent_run_id,
        source_artifact_ids=[],
        missing_artifact_reason="live process state cannot be captured to a file",
    )
    assert observation.missing_artifact_reason


def test_observation_cites_only_artifacts_that_exist(
    bundle, run_kwargs
) -> None:
    """An observation may not cite evidence the vault cannot verify."""
    from core.evidence import ArtifactNotFoundError

    run = _start(bundle, run_kwargs)
    nonexistent = "a" * 64
    with pytest.raises(ArtifactNotFoundError):
        _observe(
            bundle.orchestrator,
            run.agent_run_id,
            source_artifact_ids=[nonexistent],
        )


def test_observation_is_rejected_after_the_run_concludes(
    bundle, run_kwargs
) -> None:
    from core.orchestrator import InvalidRunState

    run = _start(bundle, run_kwargs)
    bundle.orchestrator.finish_run(run.agent_run_id, outcome="completed")
    with pytest.raises(InvalidRunState):
        _observe(bundle.orchestrator, run.agent_run_id, source_artifact_ids=[])
