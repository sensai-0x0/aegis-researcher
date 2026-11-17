"""Scope manifests and the scope resolver — P01.W1 "Research scope and isolated
laboratory".

Curriculum criteria under test:
- "Define written scope manifests for local targets, permitted actions,
  exclusions, time limits and stop conditions."
- "A test cannot begin without a valid scope record."
- "Targets are isolated by default." (default-deny network, allowlist-only targets)
- agent_operating_contract: "Testing public or third-party systems" is prohibited.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest
from pydantic import ValidationError


def _resolver(make_mission, make_scope, clock, mission_overrides=None, scope_overrides=None):
    from core.mission import Mission
    from core.scope import ScopeManifest, ScopeResolver

    mission = Mission.model_validate(make_mission(**(mission_overrides or {})))
    scope = ScopeManifest.model_validate(make_scope(**(scope_overrides or {})))
    return ScopeResolver(missions=[mission], scopes=[scope], clock=clock), mission


# ---------------------------------------------------------------------------
# Scope manifest model
# ---------------------------------------------------------------------------


def test_valid_scope_manifest_loads(make_scope) -> None:
    from core.scope import ScopeManifest

    scope = ScopeManifest.model_validate(make_scope())
    assert scope.network.default == "deny"
    assert scope.target_class == "local_vm"
    assert scope.approved_by == "human-owner"


@pytest.mark.parametrize("network", [{"default": "allow"}, {}, {"default": "permit"}])
def test_network_access_must_default_to_deny(make_scope, network: dict[str, Any]) -> None:
    """Configure default-deny network access" — an open default is invalid."""
    from core.scope import ScopeManifest

    payload = make_scope(network=network) if network else {**make_scope(), "network": None}
    with pytest.raises(ValidationError, match="[Dd]eny"):
        ScopeManifest.model_validate(payload)


@pytest.mark.parametrize("wildcard", [["*"], ["0.0.0.0/0"], ["::/0"]])
def test_wildcard_destinations_are_rejected(make_scope, wildcard: list[str]) -> None:
    """An allow-all exception defeats default-deny and must never parse."""
    from core.scope import ScopeManifest

    payload = make_scope(network={"default": "deny", "allowed_destinations": wildcard})
    with pytest.raises(ValidationError, match="[Ww]ildcard"):
        ScopeManifest.model_validate(payload)


@pytest.mark.parametrize("target_class", ["local_vm", "local_container", "local_process", "emulated_device", "emulated_firmware"])
def test_local_target_classes_are_accepted(make_scope, target_class: str) -> None:
    from core.scope import ScopeManifest

    ScopeManifest.model_validate(make_scope(target_class=target_class))


@pytest.mark.parametrize("target_class", ["public_internet", "third_party_service", "production"])
def test_external_target_classes_are_rejected(make_scope, target_class: str) -> None:
    """Only explicitly authorized local labs, VMs and emulations are allowed."""
    from core.scope import ScopeManifest

    with pytest.raises(ValidationError):
        ScopeManifest.model_validate(make_scope(target_class=target_class))


@pytest.mark.parametrize("field", ["approved_by", "approved_at"])
def test_scope_requires_recorded_human_approval(make_scope, field: str) -> None:
    """An unapproved scope record cannot authorize anything."""
    from core.scope import ScopeManifest

    payload = {key: value for key, value in make_scope().items() if key != field}
    with pytest.raises(ValidationError, match=field):
        ScopeManifest.model_validate(payload)


def test_scope_requires_expiry_and_stop_conditions(make_scope) -> None:
    """exclusions, time limits and stop conditions" are mandatory fields."""
    from core.scope import ScopeManifest

    payload = {key: value for key, value in make_scope().items() if key != "expires_at"}
    with pytest.raises(ValidationError, match="expires_at"):
        ScopeManifest.model_validate(payload)

    payload = make_scope(stop_conditions=[])
    with pytest.raises(ValidationError, match="stop_conditions"):
        ScopeManifest.model_validate(payload)


def test_scope_id_must_be_nonempty_and_wellformed(make_scope) -> None:
    from core.scope import ScopeManifest

    with pytest.raises(ValidationError):
        ScopeManifest.model_validate(make_scope(scope_id="has spaces"))


# ---------------------------------------------------------------------------
# Scope resolver: deny by default
# ---------------------------------------------------------------------------


def test_in_scope_read_operation_is_allowed(make_mission, make_scope, clock) -> None:
    from core.scope import Decision

    resolver, mission = _resolver(make_mission, make_scope, clock)
    decision = resolver.assert_authorized(mission, "asset-vm-lab-0001", "inventory.read")
    assert decision.decision is Decision.ALLOW
    assert decision.reason  # every decision must explain itself


def test_unregistered_mission_is_denied(make_mission, make_scope, clock) -> None:
    from core.mission import Mission
    from core.scope import Decision, ScopeManifest, ScopeResolver

    scope = ScopeManifest.model_validate(make_scope())
    resolver = ScopeResolver(missions=[], scopes=[scope], clock=clock)
    stranger = Mission.model_validate(make_mission())
    decision = resolver.assert_authorized(stranger, "asset-vm-lab-0001", "inventory.read")
    assert decision.decision is Decision.DENY


def test_unapproved_mission_is_denied(make_mission, make_scope, clock) -> None:
    from core.scope import Decision

    resolver, mission = _resolver(
        make_mission, make_scope, clock, mission_overrides={"approval_state": "draft"}
    )
    decision = resolver.assert_authorized(mission, "asset-vm-lab-0001", "inventory.read")
    assert decision.decision is Decision.DENY


def test_revoked_mission_is_denied(make_mission, make_scope, clock) -> None:
    from core.scope import Decision

    resolver, mission = _resolver(
        make_mission, make_scope, clock, mission_overrides={"approval_state": "revoked"}
    )
    decision = resolver.assert_authorized(mission, "asset-vm-lab-0001", "inventory.read")
    assert decision.decision is Decision.DENY


def test_expired_mission_is_denied(make_mission, make_scope, clock) -> None:
    from core.scope import Decision

    clock.set(datetime(2026, 11, 25, 12, 0, 0, tzinfo=timezone.utc))
    resolver, mission = _resolver(make_mission, make_scope, clock)
    decision = resolver.assert_authorized(mission, "asset-vm-lab-0001", "inventory.read")
    assert decision.decision is Decision.DENY


def test_mission_is_denied_once_its_scope_expires(make_mission, make_scope, clock) -> None:
    from core.scope import Decision

    clock.set(datetime(2026, 12, 1, 0, 0, 0, tzinfo=timezone.utc))
    resolver, mission = _resolver(make_mission, make_scope, clock)
    decision = resolver.assert_authorized(mission, "asset-vm-lab-0001", "inventory.read")
    assert decision.decision is Decision.DENY


def test_mission_cannot_reference_an_unknown_scope(make_mission, make_scope, clock) -> None:
    """A mission whose scope_id does not resolve must be denied, not assumed ok."""
    from core.scope import Decision

    resolver, mission = _resolver(
        make_mission, make_scope, clock, mission_overrides={"scope_id": "scope-unregistered"}
    )
    decision = resolver.assert_authorized(mission, "asset-vm-lab-0001", "inventory.read")
    assert decision.decision is Decision.DENY


def test_target_outside_the_mission_is_denied(make_mission, make_scope, clock) -> None:
    """Agents cannot broaden scope" — a new asset is not automatically covered."""
    from core.scope import Decision

    resolver, mission = _resolver(make_mission, make_scope, clock)
    decision = resolver.assert_authorized(mission, "asset-vm-lab-0002", "inventory.read")
    assert decision.decision is Decision.DENY


def test_operation_outside_allowed_actions_is_denied(make_mission, make_scope, clock) -> None:
    from core.scope import Decision

    resolver, mission = _resolver(make_mission, make_scope, clock)
    decision = resolver.assert_authorized(mission, "asset-vm-lab-0001", "registry.write")
    assert decision.decision is Decision.DENY


def test_operation_excluded_by_mission_is_denied_even_if_listed_allowed(
    make_mission, make_scope, clock
) -> None:
    from core.scope import Decision

    resolver, mission = _resolver(
        make_mission,
        make_scope,
        clock,
        mission_overrides={"allowed_actions": ["inventory.read", "network.connect"]},
    )
    decision = resolver.assert_authorized(mission, "asset-vm-lab-0001", "network.connect")
    assert decision.decision is Decision.DENY


def test_operation_excluded_by_scope_overrides_mission_allowance(
    make_mission, make_scope, clock
) -> None:
    """The scope manifest is the authority above the mission."""
    from core.scope import Decision

    resolver, mission = _resolver(
        make_mission,
        make_scope,
        clock,
        scope_overrides={"excluded_actions": ["network.connect", "inventory.read"]},
        mission_overrides={"allowed_actions": ["inventory.read"]},
    )
    decision = resolver.assert_authorized(mission, "asset-vm-lab-0001", "inventory.read")
    assert decision.decision is Decision.DENY


def test_every_decision_carries_a_distinct_reason(
    make_mission, make_scope, clock
) -> None:
    """Audit consumers must be able to distinguish denial causes."""
    resolver, mission = _resolver(make_mission, make_scope, clock)
    reasons = {
        resolver.assert_authorized(mission, "asset-vm-lab-0002", "inventory.read").reason,
        resolver.assert_authorized(mission, "asset-vm-lab-0001", "registry.write").reason,
        resolver.assert_authorized(mission, "asset-vm-lab-0001", "network.connect").reason,
    }
    assert len(reasons) == 3


def test_resolver_never_raises_for_wellformed_requests(
    make_mission, make_scope, clock
) -> None:
    """assert_authorized returns a Decision; authorization failures are values."""
    resolver, mission = _resolver(make_mission, make_scope, clock)
    for target, operation in [
        ("asset-vm-lab-0002", "inventory.read"),
        ("asset-vm-lab-0001", "file.write"),
    ]:
        decision = resolver.assert_authorized(mission, target, operation)
        assert decision is not None
