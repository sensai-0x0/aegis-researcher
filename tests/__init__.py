# Test package marker.
#
# Required so pytest can collect same-basename modules across directories
# (e.g. tests/test_audit.py and tests/unit/test_audit.py) without
# "import file mismatch" errors. With this marker, modules import as
# ``tests.test_audit`` / ``tests.unit.test_audit`` and the repo root lands
# on sys.path, making ``import core.*`` work under any pytest invocation.
#
# main's dataclass-era tests also run standalone via
# ``python3 -m unittest discover -s tests -v``; both invocations are
# supported by this package layout.
