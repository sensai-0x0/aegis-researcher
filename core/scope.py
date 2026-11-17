"""Deny-by-default scope resolution for AEGIS.

Mirrors .claude/rules/scope.md behaviorally. Exclusions are evaluated BEFORE
authorizations; anything not explicitly listed is DENIED. Ambiguity is treated
as denial — the caller must ask a human (rule scope.md #4).
"""
from __future__ import annotations

import fnmatch
import ipaddress
from dataclasses import dataclass
from datetime import datetime, timezone

__all__ = ["Decision", "ScopeError", "ScopeResolver"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str
    target: str
    mission_id: str | None
    decided_at: str

    @property
    def verb(self) -> str:
        return "ALLOW" if self.allowed else "DENY"


class ScopeError(Exception):
    """Raised when a scope check is structurally impossible (no mission, etc.)."""


class ScopeResolver:
    """Resolve targets against a validated mission. Deny-by-default."""

    def __init__(self, mission: dict):
        self.mission = mission
        self.mission_id = mission.get("mission_id")
        self.authorized = mission.get("authorized_targets", [])
        self.exclusions = mission.get("exclusions", [])
        if not self.authorized:
            # An active mission with zero authorized targets authorizes nothing.
            self.authorized = []

    # -- public API ---------------------------------------------------------

    def decide(self, target: str) -> Decision:
        """Return the scope Decision for `target`. Never raises for scope logic."""
        if not isinstance(target, str) or not target.strip():
            return Decision(False, "empty or invalid target", str(target), self.mission_id, _now())
        target = target.strip()
        for rule in self.exclusions:
            if self._matches(rule, target):
                reason = rule.get("reason") or "explicitly excluded by mission"
                return Decision(False, f"excluded: {reason}", target, self.mission_id, _now())
        for rule in self.authorized:
            if self._matches(rule, target):
                return Decision(True, f"authorized by {rule.get('type')}:{rule.get('value')}",
                                target, self.mission_id, _now())
        # Deny-by-default: absence of a prohibition is NOT authorization.
        return Decision(False, "not listed in mission authorized_targets", target,
                        self.mission_id, _now())

    def assert_authorized(self, target: str) -> Decision:
        """Return the Decision or raise ScopeError (caller must catch + audit)."""
        d = self.decide(target)
        if not d.allowed:
            raise ScopeError(d.reason)
        return d

    # -- matching -----------------------------------------------------------

    def _matches(self, rule: dict, target: str) -> bool:
        kind, value = rule.get("type"), str(rule.get("value", ""))
        if not value:
            return False
        if kind == "cidr":
            try:
                net = ipaddress.ip_network(value, strict=False)
            except ValueError:
                return False
            host = self._host_of(target)
            try:
                return host is not None and ipaddress.ip_address(host) in net
            except ValueError:
                return False
        if kind == "host":
            host = self._host_of(target)
            return host is not None and (fnmatch.fnmatch(host, value) or host == value)
        if kind == "application":
            # e.g. gw-service@203.0.113.10:8443 — match on name and/or host[:port]
            app_host = self._host_of(target)
            app_name = target.split("@", 1)[0] if "@" in target else target
            rule_name = value.split("@", 1)[0] if "@" in value else value
            rule_host = self._host_of(value)
            name_ok = fnmatch.fnmatch(app_name, rule_name) or app_name == rule_name
            host_ok = app_host is not None and rule_host is not None and (
                fnmatch.fnmatch(app_host, rule_host) or app_host == rule_host)
            return name_ok or host_ok
        if kind in ("component", "repository"):
            base = target.split("@", 1)[0].split(":", 1)[0]
            return fnmatch.fnmatch(base, value) or base == value
        return False

    @staticmethod
    def _host_of(target: str) -> str | None:
        """Extract the host part of 'name@host:port' / 'host:port' / bare 'host'."""
        t = target.split("/", 1)[0]  # strip path component if any
        if "@" in t:
            t = t.split("@", 1)[1]
        t = t.rsplit(":", 1)[0] if t.count(":") == 1 else t.split(":", 1)[0]
        return t or None
