"""AEGIS adapter layer: bridges between agent harnesses and the core.

Curriculum P03 exit criteria (from .agents/curriculum.json):
1. Two interfaces consume the same canonical contracts — every adapter speaks
   the contract schemas; none defines its own.
2. Core policy and evidence logic remain outside harness-specific code —
   adapters delegate ALL authorization/policy/audit decisions to core/.
3. Unsupported adapters fail closed — unknown adapter names raise
   AdapterError; there is no silent fallback.

Adapter protocol:
    prepare(mission) -> plan       # harness-shaped work plan from a contract mission
    execute(step) -> observation   # one plan step executed under core governance
    report(run) -> report dict     # contract run -> harness-neutral report
"""
from __future__ import annotations

from typing import Protocol

__all__ = ["Adapter", "AdapterError", "get_adapter", "SUPPORTED"]


class Adapter(Protocol):
    name: str
    version: str

    def prepare(self, mission: dict) -> dict: ...
    def execute(self, step: dict) -> dict: ...
    def report(self, run: dict) -> dict: ...


class AdapterError(Exception):
    """Requested adapter is unsupported. Fail closed."""


SUPPORTED = ("claude_code", "codex", "mcp", "cli")


def get_adapter(name: str) -> Adapter:
    """Factory. Fails closed on anything outside SUPPORTED."""
    if name not in SUPPORTED:
        raise AdapterError(
            f"adapter {name!r} unsupported; supported: {SUPPORTED}; "
            f"failing closed (no fallback)")
    module = {
        "claude_code": "adapters.claude_code.adapter",
        "codex": "adapters.codex.adapter",
        "mcp": "adapters.mcp.server",
        "cli": "adapters.cli.main",
    }[name]
    import importlib
    mod = importlib.import_module(module)
    return mod.ADAPTER
