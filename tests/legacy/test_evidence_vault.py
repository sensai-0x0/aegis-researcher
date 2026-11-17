import tempfile
import unittest
from pathlib import Path

from core.evidence import EvidenceIntegrityError, EvidenceVault


class TestEvidenceVault(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.vault = EvidenceVault(Path(self.tmp.name) / "objects")
        self.src = Path(self.tmp.name) / "banner.txt"
        self.src.write_text("HTTP/1.1 200 OK\r\nServer: gw/1.4.2\r\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_store_returns_content_address_record(self):
        rec = self.vault.store(self.src, run_id="22222222-2222-4222-8222-222222222222")
        self.assertEqual(rec["artifact_id"], rec["sha256"])
        self.assertEqual(len(rec["sha256"]), 64)
        self.assertTrue(any(c["action"] == "stored" for c in rec["custody"]))
        # Object placed at <h[:2]>/<h>
        p = Path(self.tmp.name) / "objects" / rec["sha256"][:2] / rec["sha256"]
        self.assertTrue(p.is_file())

    def test_hash_verifies_after_store_and_retrieval(self):
        rec = self.vault.store(self.src, run_id="r")
        opened = self.vault.open(rec["sha256"])  # verifies internally
        self.assertEqual(opened.read_text(), self.src.read_text())

    def test_retrieval_detects_tampering(self):
        rec = self.vault.store(self.src, run_id="r")
        p = Path(self.tmp.name) / "objects" / rec["sha256"][:2] / rec["sha256"]
        p.write_text("TAMPERED")  # violates immutability — must be detectable
        with self.assertRaises(EvidenceIntegrityError):
            self.vault.open(rec["sha256"])

    def test_duplicate_store_is_idempotent(self):
        r1 = self.vault.store(self.src, run_id="r1")
        r2 = self.vault.store(self.src, run_id="r2")
        self.assertEqual(r1["sha256"], r2["sha256"])
        self.assertEqual(r2["custody"][0]["action"], "verified")


if __name__ == "__main__":
    unittest.main()
