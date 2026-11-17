"""TDD spec for ``core/scope.py`` — the ScopeManifest authorization boundary (red).

The conftest payload (``make_scope``) fixes the model shape; the curriculum's
``default_execution_posture`` fixes the semantics. Structural roundtrips
against the mission contract are covered by ``tests/unit/``; this module
specifies the *posture* a scope manifest must enforce:

1. **Network is deny-by-default**: a manifest whose ``network.default`` is
   anything other than ``"deny"`` must not validate. Open-by-default scopes
   are not expressible.
2. **An unapproved manifest is not an authorization**: ``approved_by`` and
   ``approved_at`` (a human, recorded) are mandatory.
3. **Closed model**: no undeclared fields — nothing can smuggle authority
   in, and no self-authorization fields exist for an agent to set.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

pytestmark = [pytest.mark.unit, pytest.mark.safety]


def test_valid_scope_manifest_validates(make_scope) -> None:
    from core.scope import ScopeManifest

    scope = ScopeManifest.model_validate(make_scope())
    assert scope.scope_id == "scope-local-lab-0001"
    assert scope.network["default"] == "deny"


def test_network_open_by_default_is_not_expressible(make_scope) -> None:
    """The posture is deny-by-default; a scope cannot opt out of it."""
    from core.scope import ScopeManifest

    payload = make_scope(network={"default": "allow", "allowed_destinations": ["*"]})
    with pytest.raises(ValidationError):
        ScopeManifest.model_validate(payload)


def test_scope_must_carry_recorded_human_approval(make_scope) -> None:
    """approved_by/approved_at are mandatory — approval cannot be implicit."""
    from core.scope import ScopeManifest

    payload = make_scope()
    payload.pop("approved_by")
    payload.pop("approved_at")
    with pytest.raises(ValidationError):
        ScopeManifest.model_validate(payload)


def test_scope_model_is_closed(make_scope) -> None:
    """No undeclared fields: authority cannot be smuggled into the manifest."""
    from core.scope import ScopeManifest

    with pytest.raises(ValidationError):
        ScopeManifest.model_validate(make_scope(operator_feeling="lucky"))


def test_scope_manifest_has_no_self_authorization_fields(make_scope) -> None:
    """A human approves the manifest; nothing on it carries a policy decision."""
    from core.scope import ScopeManifest

    forbidden = {"decision", "policy_decision", "policy_outcome", "allow", "granted", "authorized"}
    field_names = set(ScopeManifest.model_fields)
    assert not (field_names & forbidden), (
        f"ScopeManifest declares authority fields: {sorted(field_names & forbidden)}"
    )
