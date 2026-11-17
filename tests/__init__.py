# Test package marker.
#
# Required so pytest can collect same-basename modules across directories
# (e.g. tests/test_audit.py and tests/unit/test_audit.py) without
# "import file mismatch" errors. With this marker, modules import as
# ``tests.test_audit`` / ``tests.unit.test_audit`` and the repo root lands
# on sys.path, making ``import core.*`` work under any pytest invocation.
