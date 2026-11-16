"""Mission loading and validation for AEGIS.

A mission is the single source of truth for authorization. It is validated
against contracts/mission.schema.json at load time; nothing runs against a
mission that fails validation or is not `active`.
"""
from __future__ import annotations

import json
from pathlib import Path

from core.jsonschema_lite import ValidationError, validate

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "contracts" / "mission.schema.json"

# Re-exported for callers that want the precise failure.
__all__ = ["MissionError", "load_mission", "load_schema"]


class MissionError(Exception):
    """Mission missing, invalid, or not active."""


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text())


def load_mission(path: str | Path) -> dict:
    """Load and validate a mission document. Raises MissionError."""
    p = Path(path)
    if not p.is_file():
        raise MissionError(f"mission file not found: {p}")
    try:
        mission = json.loads(p.read_text())
    except json.JSONDecodeError as e:
        raise MissionError(f"mission is not valid JSON: {e}") from e
    try:
        validate(mission, load_schema())
    except ValidationError as e:
        raise MissionError(f"mission violates contract: {e}") from e
    if mission["status"] != "active":
        raise MissionError(f"mission status is {mission['status']!r}; only 'active' missions run")
    return mission


def mission_approvers(mission: dict) -> list[str]:
    return list(mission.get("human_approvers", []))


def mission_is_active(mission: dict) -> bool:
    return mission.get("status") == "active"
