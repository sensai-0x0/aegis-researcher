import unittest

from core.scope import Decision, ScopeError, ScopeResolver

MISSION = {
    "mission_id": "11111111-1111-4111-8111-111111111111",
    "authorized_targets": [
        {"type": "cidr", "value": "203.0.113.0/24"},
        {"type": "application", "value": "gw-service@203.0.113.10:8443"},
        {"type": "component", "value": "gw-*"},
        {"type": "host", "value": "gw.lab.local"},
    ],
    "exclusions": [
        {"type": "cidr", "value": "203.0.113.0/25", "reason": "shared infrastructure"},
    ],
}


class TestScopeDenyByDefault(unittest.TestCase):
    def setUp(self):
        self.r = ScopeResolver(MISSION)

    def test_unlisted_target_denied(self):
        d = self.r.decide("example.com:443")
        self.assertFalse(d.allowed)
        self.assertIn("not listed", d.reason)

    def test_exclusion_wins_over_authorization(self):
        # 203.0.113.5 is inside the authorized /24 but inside the excluded /25.
        d = self.r.decide("203.0.113.5")
        self.assertFalse(d.allowed)
        self.assertIn("shared infrastructure", d.reason)

    def test_authorized_cidr(self):
        d = self.r.decide("203.0.113.200")
        self.assertTrue(d.allowed)

    def test_exclusion_wins_even_for_named_application(self):
        # The mission fixture authorizes gw-service@203.0.113.10:8443 but also
        # excludes 203.0.113.0/25 ("shared infrastructure"). Exclusions are
        # evaluated first: the named application is DENIED. Documented behavior.
        d = self.r.decide("gw-service@203.0.113.10:8443")
        self.assertFalse(d.allowed)
        self.assertIn("shared infrastructure", d.reason)

    def test_application_match_by_name_and_host(self):
        # Upper half of the /24 is outside the excluded /25.
        self.assertTrue(self.r.decide("gw-service@203.0.113.200:8443").allowed)
        self.assertTrue(self.r.decide("gw-service@203.0.113.201:9000").allowed)  # host in /24

    def test_component_wildcard(self):
        self.assertTrue(self.r.decide("gw-worker@anywhere").allowed)
        self.assertFalse(self.r.decide("other-worker@anywhere").allowed)

    def test_empty_target_denied(self):
        self.assertFalse(self.r.decide("").allowed)
        self.assertFalse(self.r.decide(None).allowed)

    def test_assert_authorized_raises(self):
        with self.assertRaises(ScopeError):
            self.r.assert_authorized("not-in-scope.host")

    def test_decision_is_recordable(self):
        d = self.r.decide("203.0.113.200")
        self.assertIsInstance(d, Decision)
        self.assertEqual(d.verb, "ALLOW")
        self.assertEqual(d.mission_id, MISSION["mission_id"])
        self.assertTrue(d.decided_at)


if __name__ == "__main__":
    unittest.main()
