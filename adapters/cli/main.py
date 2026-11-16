"""AEGIS operator CLI — thin over core, stdlib argparse.

Commands:
    mission validate <file>            validate a mission document
    scope check <target> --mission <file>   resolve target via core/scope.py
    audit verify <file>                verify an audit chain
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adapters import AdapterError  # noqa: E402,F401  (re-exported for entry point)
from core.audit import AuditCorruptionError, AuditLog  # noqa: E402
from core.jsonschema_lite import ValidationError, validate  # noqa: E402
from core.mission import MissionError, load_mission, load_schema  # noqa: E402
from core.scope import ScopeResolver  # noqa: E402


def cmd_mission_validate(args: argparse.Namespace) -> int:
    try:
        mission = json.loads(Path(args.file).read_text())
        validate(mission, load_schema())
    except (MissionError, ValidationError, json.JSONDecodeError, OSError) as e:
        print(f"INVALID: {e}", file=sys.stderr)
        return 1
    print(f"VALID: mission {mission['mission_id']} ({mission['status']})")
    return 0


def cmd_scope_check(args: argparse.Namespace) -> int:
    try:
        mission = load_mission(args.mission)
    except MissionError as e:
        print(f"mission error: {e}", file=sys.stderr)
        return 1
    d = ScopeResolver(mission).decide(args.target)
    print(f"{d.verb}  {d.target}  ({d.reason})")
    return 0 if d.allowed else 2


def cmd_audit_verify(args: argparse.Namespace) -> int:
    try:
        audit = AuditLog(args.file)
    except AuditCorruptionError as e:
        print(f"CORRUPT: {e}", file=sys.stderr)
        return 1
    ok, bad = audit.verify()
    status = "OK" if ok else "CORRUPT"
    print(f"{status} ({len(audit.entries())} entries, head {audit.head_hash()[:12]})")
    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="aegis", description="AEGIS operator CLI")
    sub = p.add_subparsers(dest="command", required=True)

    m = sub.add_parser("mission", help="mission operations")
    ms = m.add_subparsers(dest="subcommand", required=True)
    mv = ms.add_parser("validate")
    mv.add_argument("file")
    mv.set_defaults(fn=cmd_mission_validate)

    s = sub.add_parser("scope", help="scope operations")
    ss = s.add_subparsers(dest="subcommand", required=True)
    sc = ss.add_parser("check")
    sc.add_argument("target")
    sc.add_argument("--mission", required=True)
    sc.set_defaults(fn=cmd_scope_check)

    a = sub.add_parser("audit", help="audit operations")
    asu = a.add_subparsers(dest="subcommand", required=True)
    av = asu.add_parser("verify")
    av.add_argument("file")
    av.set_defaults(fn=cmd_audit_verify)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
