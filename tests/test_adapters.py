import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adapters import AdapterError, get_adapter  # noqa: E402
from adapters.cli import main as cli_main  # noqa: E402
from adapters.mcp import server as mcp_server  # noqa: E402
from core.jsonschema_lite import validate  # noqa: E402
from core.mission import load_schema  # noqa: E402

MISSION = json.loads((ROOT / "contracts" / "fixtures" / "mission.instance.json").read_text())


class TestAdapterContract(unittest.TestCase):
    """Curriculum P03 exits, as tests."""

    def test_unsupported_adapter_fails_closed(self):
        for bad in ("unknown", "gpt-harness", "", None):
            with self.assertRaises(AdapterError):
                get_adapter(bad)

    def test_two_interfaces_same_contracts(self):
        # claude_code and codex both prepare from the SAME contract mission.
        cc = get_adapter("claude_code")
        cx = get_adapter("codex")
        plan_cc, plan_cx = cc.prepare(MISSION), cx.prepare(MISSION)
        validate(MISSION, load_schema())  # canonical contract round-trips
        self.assertEqual(plan_cc["mission_id"], plan_cx["mission_id"])
        self.assertEqual([s["target"] for s in plan_cc["steps"]],
                         [s["target"] for s in plan_cx["steps"]])
        # Neither plan carries adapter-local schema definitions.
        for plan in (plan_cc, plan_cx):
            self.assertNotIn("schema", plan)
            self.assertNotIn("inputSchema", plan)

    def test_reports_are_harness_neutral(self):
        run = {"run_id": "r", "status": "concluded", "artifacts": ["a" * 64],
               "workers_invoked": [], "policy_decisions": []}
        for name in ("claude_code", "codex"):
            rep = get_adapter(name).report(run)
            self.assertEqual(rep["run_id"], "r")
            self.assertEqual(rep["status"], "concluded")


class TestMcpServer(unittest.TestCase):
    def test_initialize_and_tools_list(self):
        resp = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
        self.assertIn("protocolVersion", resp["result"])
        resp = mcp_server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        names = [t["name"] for t in resp["result"]["tools"]]
        self.assertIn("aegis.scope_check", names)

    def test_scope_check_enforced_server_side(self):
        resp = mcp_server.handle({
            "jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": "aegis.scope_check",
                       "arguments": {"mission": MISSION, "target": "evil.example.com"}}})
        text = resp["result"]["content"][0]["text"]
        self.assertIn('"allowed": false', text)
        self.assertIn("core/scope.py", text)

    def test_unknown_tool_fails_closed(self):
        resp = mcp_server.handle({"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                                  "params": {"name": "aegis.dangerous", "arguments": {}}})
        self.assertIn("error", resp)
        self.assertEqual(resp["error"]["code"], -32602)

    def test_unknown_method_fails_closed(self):
        resp = mcp_server.handle({"jsonrpc": "2.0", "id": 5, "method": "admin/backdoor"})
        self.assertEqual(resp["error"]["code"], -32601)

    def test_malformed_payload_fails_closed(self):
        resp = mcp_server.handle({"jsonrpc": "2.0", "id": 6, "method": "tools/call",
                                  "params": {"name": "aegis.scope_check",
                                             "arguments": {"mission": {"mission_id": "x"},
                                                           "target": "t"}}})
        self.assertIn("error", resp)


class TestCli(unittest.TestCase):
    MISSION_FILE = str(ROOT / "contracts" / "fixtures" / "mission.instance.json")

    def test_mission_validate_ok(self):
        self.assertEqual(cli_main.main(["mission", "validate", self.MISSION_FILE]), 0)

    def test_scope_check_allow_and_deny(self):
        self.assertEqual(cli_main.main(["scope", "check", "203.0.113.200",
                                        "--mission", self.MISSION_FILE]), 0)
        self.assertEqual(cli_main.main(["scope", "check", "example.com",
                                        "--mission", self.MISSION_FILE]), 2)


if __name__ == "__main__":
    unittest.main()
