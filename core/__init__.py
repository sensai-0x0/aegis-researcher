"""AEGIS core — authorization, policy, audit, mission and orchestration.

Layering (dependency order):
    jsonschema_lite -> mission -> scope -> policy -> audit -> orchestrator

Nothing outside this package may perform a target-contacting action without a
scope Decision and a policy classification (see .claude/rules/scope.md).
"""
