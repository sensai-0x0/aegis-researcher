import tempfile
import unittest
from pathlib import Path

from core.audit import AuditCorruptionError, AuditLog
from core.policy import ActionClass, PolicyError, PolicyEngine

MISSION = {
    "mission_id": "11111111-1111-4111-8111-111111111111",
    "human_approvers": ["operator-primary"],
}


def fresh_policy(tmp):
    audit = AuditLog(Path(tmp) / "audit.jsonl")
    return audit, PolicyEngine(audit, MISSION)


class TestPolicyGating(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.audit, self.policy = fresh_policy(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_read_only_allowed_without_approval(self):
        d = self.policy.check({"name": "banner grab", "touches_target": True,
                               "purely_passive": True})
        self.assertEqual(d.action_class, ActionClass.READ_ONLY)
        self.assertEqual(d.decision, "allowed")

    def test_intrusive_allowed_without_approval(self):
        d = self.policy.check({"name": "test payload", "touches_target": True})
        self.assertEqual(d.action_class, ActionClass.INTRUSIVE)
        self.assertEqual(d.decision, "allowed")

    def test_consequential_denied_without_approver(self):
        d = self.policy.check({"name": "create account", "modifies_state": True})
        self.assertEqual(d.action_class, ActionClass.CONSEQUENTIAL)
        self.assertEqual(d.decision, "denied")
        self.assertIsNone(d.approver)

    def test_consequential_denied_with_unknown_approver(self):
        d = self.policy.check({"name": "create account", "modifies_state": True},
                              approver="random-agent")
        self.assertEqual(d.decision, "denied")

    def test_consequential_approved_by_mission_approver(self):
        d = self.policy.check({"name": "create account", "modifies_state": True},
                              approver="operator-primary")
        self.assertEqual(d.decision, "approved")
        self.assertEqual(d.approver, "operator-primary")

    def test_require_raises_when_unapproved(self):
        with self.assertRaises(PolicyError):
            self.policy.require({"name": "wipe config", "modifies_state": True})

    def test_every_decision_audited(self):
        self.policy.check({"name": "grab", "touches_target": True})
        self.policy.check({"name": "wipe", "modifies_state": True})
        events = [e["event"] for e in self.audit.entries()]
        self.assertEqual(events.count("policy_decision"), 2)


class TestAuditChain(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "audit.jsonl"

    def tearDown(self):
        self.tmp.cleanup()

    def test_chain_verifies_after_reload(self):
        a = AuditLog(self.path)
        a.append("e1", {"x": 1})
        a.append("e2", {"x": 2})
        b = AuditLog(self.path)  # reload from disk
        ok, bad = b.verify()
        self.assertTrue(ok)
        self.assertIsNone(bad)
        self.assertEqual(len(b.entries()), 2)

    def test_tamper_detection(self):
        a = AuditLog(self.path)
        a.append("e1", {"x": 1})
        a.append("e2", {"x": 2})
        # Tamper with the first entry's payload on disk.
        lines = self.path.read_text().splitlines()
        entry = lines[0].replace('"x": 1', '"x": 999')
        self.path.write_text("\n".join([entry] + lines[1:]) + "\n")
        with self.assertRaises(AuditCorruptionError):
            AuditLog(self.path)

    def test_no_delete_method_exists(self):
        # Append-only by construction: no removal API may appear.
        forbidden = ("delete", "remove", "truncate", "pop", "clear")
        names = [n for n in dir(AuditLog) if not n.startswith("_")]
        self.assertEqual([n for n in names if any(f in n for f in forbidden)], [])


if __name__ == "__main__":
    unittest.main()
