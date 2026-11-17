import json
import tempfile
import unittest
from pathlib import Path

from workers import TaskError, WORKER_NAMES, get_worker

ROOT = Path(__file__).resolve().parents[1]

TASK = {"target": "203.0.113.200", "purpose": "inventory lab component",
        "hypothesis": "gw-service ships a config file exposing its admin route table"}


class TestWorkerBaseDiscipline(unittest.TestCase):
    def test_all_workers_registered(self):
        self.assertEqual(len(WORKER_NAMES), 8)
        for name in WORKER_NAMES:
            w = get_worker(name)
            self.assertEqual(w.name, name)

    def test_task_without_hypothesis_refused(self):
        w = get_worker("system_inventory")
        with self.assertRaises(TaskError):
            w.run({"target": "x", "purpose": "p"})  # no hypothesis: fishing
        with self.assertRaises(TaskError):
            w.run({"target": "x", "hypothesis": "h"})  # no purpose
        with self.assertRaises(TaskError):
            w.run({})  # nothing

    def test_observation_without_evidence_refused(self):
        w = get_worker("system_inventory")
        with self.assertRaises(TaskError):
            w.check_result({"observations": [{"observation_id": "o"}],
                            "artifacts": []})

    def test_inventory_produces_evidenced_observations(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "gw-service").mkdir()
            (Path(tmp) / "gw-service" / "app.py").write_text("print('gw')\n")
            (Path(tmp) / "gw-service" / "admin.cfg").write_text("route=/admin\n")
            res = get_worker("system_inventory").run({**TASK, "path": tmp})
        self.assertEqual(len(res["observations"]), 1)  # one top-level component
        obs = res["observations"][0]
        self.assertEqual(len(obs["raw_evidence"]), 1)
        self.assertEqual(res["artifact"]["sha256"], res["artifact"]["artifact_id"])
        self.assertIn("admin.cfg", res["raw"])

    def test_stub_refuses_but_never_fabricates(self):
        for name in ("fuzzing", "firmware", "renode", "qemu",
                     "static_analysis", "application_testing",
                     "binary_analysis"):
            w = get_worker(name)
            self.assertIn("stub", w.status)
            with self.assertRaises(NotImplementedError):
                w.run(TASK)

    def test_missing_inventory_target_fails_cleanly(self):
        with self.assertRaises(TaskError):
            get_worker("system_inventory").run({**TASK, "path": "/nonexistent/xyz"})


if __name__ == "__main__":
    unittest.main()
