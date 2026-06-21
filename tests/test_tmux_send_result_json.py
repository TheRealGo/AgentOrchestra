from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.tmux_delivery import DeliveryResult  # noqa: E402
from agent_orchestra_minimal.tmux_send import _write_result_json  # noqa: E402


class TmuxSendResultJsonTests(unittest.TestCase):
    def test_result_json_records_degraded_delivery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "delivery" / "result.json"

            _write_result_json(
                path,
                pane="%221",
                result=DeliveryResult(True, 3, "› MainAgent: task\n\n• Working"),
            )

            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["pane"], "%221")
            self.assertTrue(data["accepted"])
            self.assertEqual(data["attempts"], 3)
            self.assertTrue(data["degraded"])
            self.assertFalse(data["expected_submit_key_fallback"])
            self.assertEqual(data["failure_phase"], "")
            self.assertEqual(data["ledger_candidate"], "delivery-defect")
            self.assertTrue(data["zero_issue_blocker"])
            self.assertIn("Gates/Candidates", data["required_disposition"])
            self.assertIn("Working", data["capture_tail"])

    def test_result_json_treats_nonstandard_submit_key_fallback_as_expected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "delivery" / "result.json"

            _write_result_json(
                path,
                pane="%221",
                result=DeliveryResult(True, 2, "› MainAgent: task\n\n• Working"),
                submit_key="M-Enter",
            )

            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertTrue(data["accepted"])
            self.assertEqual(data["attempts"], 2)
            self.assertFalse(data["degraded"])
            self.assertTrue(data["expected_submit_key_fallback"])
            self.assertEqual(data["failure_phase"], "")
            self.assertEqual(data["ledger_candidate"], "")
            self.assertFalse(data["zero_issue_blocker"])

    def test_result_json_records_unaccepted_delivery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "result.json"

            _write_result_json(path, pane="%222", result=DeliveryResult(False, 0, "busy"))

            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertFalse(data["accepted"])
            self.assertFalse(data["degraded"])
            self.assertFalse(data["expected_submit_key_fallback"])
            self.assertEqual(data["failure_phase"], "input-not-ready")
            self.assertEqual(data["ledger_candidate"], "delivery-defect")
            self.assertTrue(data["zero_issue_blocker"])
            self.assertIn("input-ready", data["required_disposition"])

    def test_result_json_distinguishes_submitted_but_unaccepted_delivery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "result.json"

            _write_result_json(path, pane="%222", result=DeliveryResult(False, 3, "queued"))

            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertFalse(data["accepted"])
            self.assertEqual(data["attempts"], 3)
            self.assertEqual(data["failure_phase"], "submitted-unaccepted")
            self.assertTrue(data["zero_issue_blocker"])
            self.assertIn("delivery succeeds", data["required_disposition"])


if __name__ == "__main__":
    unittest.main()
