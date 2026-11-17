import tempfile
import unittest
from pathlib import Path

from core.audit import AuditLog
from core.mission import MissionError, load_mission
from core.orchestrator import ObservationError, Orchestrator
from core.policy import PolicyEngine
from core.scope import ScopeError

ROOT = Path(__file__).resolve().parents[1]
MISSION_PATH = ROOT / "contracts" / "fixtures" / "mission.instance.json"


class FakeWorker:
    name = "system_inventory"

    def __init__(self, evidence=True):
        self.evidence = evidence

    def run(self, task):
        obs = {
            "observation_id": "33333333-3333-4333-8333-333333333333",
            "target": task["target"],
            "raw_evidence": ["a" * 64] if self.evidence else [],
        }
        return {"observations": [obs], "artifacts": ["a" * 64]}


class TestMissionLoading(unittest.TestCase):
    def test_fixture_mission_loads(self):
        m = load_mission(MISSION_PATH)
        self.assertEqual(m["status"], "active")
        self.assertTrue(m["human_approvers"])

    def test_rejects_broken_mission(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "m.json"
            bad.write_text('{"mission_id": "nope"}')
            with self.assertRaises(MissionError):
                load_mission(bad)


class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.audit = AuditLog(Path(self.tmp.name) / "audit.jsonl")
        self.mission = load_mission(MISSION_PATH)
        self.orch = Orchestrator(self.mission, self.audit,
                                 PolicyEngine(self.audit, self.mission))

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self):
        return self.orch.start_run({"name": "cli", "version": "0.1.0"})

    def test_lifecycle(self):
        run = self._run()
        self.assertEqual(run["status"], "authorized")
        self.orch.conclude()
        self.assertEqual(run["status"], "concluded")
        self.assertTrue(run["audit_ref"].startswith("audit-chain:"))

    def test_dispatch_denies_out_of_scope(self):
        self._run()
        with self.assertRaises(ScopeError):
            self.orch.dispatch(FakeWorker(), {"target": "evil.example.com:443",
                                             "purpose": "p", "hypothesis": "h"})
        self.assertTrue(any(e["event"] == "scope_denied" for e in self.audit.entries()))

    def test_dispatch_allows_in_scope(self):
        self._run()
        res = self.orch.dispatch(FakeWorker(), {"target": "203.0.113.200",
                                               "purpose": "p", "hypothesis": "h"})
        self.assertEqual(len(res["observations"]), 1)
        self.assertEqual(self.orch.run["status"], "collecting")
        self.assertTrue(self.orch.run["artifacts"])

    def test_no_observation_without_evidence(self):
        self._run()
        with self.assertRaises(ObservationError):
            self.orch.dispatch(FakeWorker(evidence=False), {"target": "203.0.113.200",
                                                           "purpose": "p", "hypothesis": "h"})

    def test_consequential_blocked_without_approval(self):
        self._run()
        with self.assertRaises(PermissionError):
            self.orch.dispatch(FakeWorker(), {"target": "203.0.113.200",
                                             "purpose": "p", "hypothesis": "h"},
                               action={"name": "reboot target", "modifies_state": True})
        self.assertTrue(any(e["event"] == "policy_blocked" for e in self.audit.entries()))

    def test_cannot_dispatch_before_start(self):
        with self.assertRaises(RuntimeError):
            self.orch.dispatch(FakeWorker(), {"target": "203.0.113.200"})


if __name__ == "__main__":
    unittest.main()
