"""CLI integration tests — P02.W3 "Python research core".

Curriculum criteria under test:
- "Build a CLI that accepts a mission file and emits a structured run manifest."
- "The CLI validates mission input, emits schema-valid output and fails safely
  on malformed or incomplete input."
- "Add ... deterministic output fixtures."

The CLI is exercised in a subprocess via ``python -m adapters.cli.main`` so exit
codes, stdout structure and output files are real. Contract (documented in
tests/README.md):

    aegis mission validate <mission.json>            → exit 0/1
    aegis run start --mission M --scope S
                    --output OUT.json --workdir DIR
                    [--now ISO-8601]                 → exit 0/1

Machine-readable stdout: ``{"ok": true, ...}`` on success and
``{"ok": false, "error": {"code": ..., "message": ...}}`` on failure.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

NOW_FLAG = "2026-11-17T09:00:00+00:00"


@pytest.fixture
def mission_file(tmp_path: Path, make_mission) -> Path:
    path = tmp_path / "mission.json"
    path.write_text(json.dumps(make_mission()))
    return path


@pytest.fixture
def scope_file(tmp_path: Path, make_scope) -> Path:
    path = tmp_path / "scope.json"
    path.write_text(json.dumps(make_scope()))
    return path


# ---------------------------------------------------------------------------
# mission validate
# ---------------------------------------------------------------------------


def test_validate_accepts_a_valid_mission(mission_file, run_cli) -> None:
    result = run_cli("mission", "validate", str(mission_file))
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["mission_id"] == json.loads(mission_file.read_text())["mission_id"]


def test_validate_is_deterministic(mission_file, run_cli) -> None:
    """deterministic output fixtures" — identical input, identical bytes."""
    first = run_cli("mission", "validate", str(mission_file))
    second = run_cli("mission", "validate", str(mission_file))
    assert first.stdout == second.stdout


def test_validate_fails_safely_on_malformed_json(tmp_path: Path, run_cli) -> None:
    path = tmp_path / "broken.json"
    path.write_text('{"mission_id": "mission-x",')  # truncated JSON
    result = run_cli("mission", "validate", str(path))
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["error"]["code"] == "invalid_json"
    # A fail-safe CLI must never surface a raw traceback to the operator.
    assert "Traceback" not in result.stdout
    assert "Traceback" not in result.stderr


def test_validate_names_the_missing_fields(tmp_path: Path, make_mission, run_cli) -> None:
    payload = {
        key: value
        for key, value in make_mission().items()
        if key not in {"target_asset_ids", "approval_state"}
    }
    path = tmp_path / "incomplete.json"
    path.write_text(json.dumps(payload))
    result = run_cli("mission", "validate", str(path))
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["ok"] is False
    assert report["error"]["code"] == "schema_violation"
    assert "target_asset_ids" in report["error"]["message"]
    assert "approval_state" in report["error"]["message"]


def test_validate_reports_a_missing_file(tmp_path: Path, run_cli) -> None:
    result = run_cli("mission", "validate", str(tmp_path / "absent.json"))
    assert result.returncode == 1
    assert json.loads(result.stdout)["error"]["code"] in {"file_not_found", "invalid_json"}


# ---------------------------------------------------------------------------
# run start
# ---------------------------------------------------------------------------


def _start_run(mission_file: Path, scope_file: Path, tmp_path: Path, run_cli, *extra: str):
    output = tmp_path / "out" / "run-manifest.json"
    workdir = tmp_path / "out" / "work"
    args = [
        "run",
        "start",
        "--mission",
        str(mission_file),
        "--scope",
        str(scope_file),
        "--output",
        str(output),
        "--workdir",
        str(workdir),
        *extra,
    ]
    return run_cli(*args), output, workdir


def test_run_start_emits_a_schema_valid_run_manifest(
    mission_file, scope_file, tmp_path: Path, run_cli, assert_schema_valid
) -> None:
    result, output, workdir = _start_run(
        mission_file, scope_file, tmp_path, run_cli, "--now", NOW_FLAG
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["agent_run_id"]

    record = json.loads(output.read_text())
    assert record["mission_id"] == json.loads(mission_file.read_text())["mission_id"]
    assert_schema_valid("run", record)

    # Every permitted execution must be auditable on disk.
    assert (workdir / "audit.jsonl").is_file()


def test_run_start_refuses_an_unapproved_mission(
    tmp_path: Path, make_mission, scope_file, run_cli
) -> None:
    mission_file = tmp_path / "unapproved.json"
    mission_file.write_text(json.dumps(make_mission(approval_state="draft")))
    result, output, _ = _start_run(mission_file, scope_file, tmp_path, run_cli)
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["ok"] is False
    assert report["error"]["code"] == "not_authorized"
    assert not output.exists(), "a refused run must not leave a partial manifest"


def test_run_start_refuses_an_expired_mission(
    mission_file, scope_file, tmp_path: Path, run_cli
) -> None:
    result, output, _ = _start_run(
        mission_file, scope_file, tmp_path, run_cli, "--now", "2026-12-01T00:00:00+00:00"
    )
    assert result.returncode == 1
    assert json.loads(result.stdout)["error"]["code"] == "not_authorized"
    assert not output.exists()


def test_unknown_command_exits_with_usage_error(run_cli) -> None:
    result = run_cli("frobnicate")
    assert result.returncode == 2
