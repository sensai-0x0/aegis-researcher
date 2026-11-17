# Legacy regression net for main's pre-port dataclass core API.
#
# These specs test core/scope.py's ScopeResolver and core/evidence.py's
# EvidenceVault as they exist today (stdlib dataclass API). They exist so the
# Option B port (CLAUDE.md Data model policy; progress.md decision row 6) —
# replacing this API with the pydantic ScopeManifest/ArtifactStore API that
# tests/unit/ and tests/test_scope.py / tests/test_evidence.py already
# specify — has a safety net against behavioral regressions during the
# transition. Delete this package once the port lands and tests/unit/ is
# verified to cover the same behavior (exclusion-wins-over-authorization,
# content-address verification, tamper detection).
