from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_orchestra_minimal.tmux_delivery import DeliveryResult  # noqa: E402
from agent_orchestra_minimal.tmux_peer_mailbox import enqueue_message, queued_messages, read_message  # noqa: E402
import agent_orchestra_minimal.tmux_send as tmux_send  # noqa: E402
from agent_orchestra_minimal.tmux_send import _drain_mailbox, _write_result_json  # noqa: E402
from tmux_send_helpers import FakeTmuxSend  # noqa: E402


class TmuxPeerMailboxTests(unittest.TestCase):
    def test_input_not_ready_consultation_can_be_queued_without_zero_issue_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mailbox_dir = Path(tmp) / "mailbox"
            queued = enqueue_message(
                pane="%221",
                text="pa-runtime -> pa-qa: response after your current work",
                mailbox_dir=mailbox_dir,
                sender="pa-runtime",
                topic="peer consultation response",
            )
            result_path = Path(tmp) / "delivery.json"

            _write_result_json(
                result_path,
                pane="%221",
                result=DeliveryResult(False, 0, "• Working"),
                queued_path=queued,
            )

            evidence = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertFalse(evidence["accepted"])
            self.assertTrue(evidence["queued"])
            self.assertEqual(evidence["ledger_candidate"], "queued-consultation")
            self.assertFalse(evidence["zero_issue_blocker"])
            self.assertIn("drain queued consultation", evidence["required_disposition"])

            message = read_message(queued)
            self.assertEqual(message["pane"], "%221")
            self.assertEqual(message["sender"], "pa-runtime")
            self.assertIn("response after your current work", message["text"])

    def test_drain_mailbox_removes_message_only_after_accepted_delivery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mailbox_dir = Path(tmp) / "mailbox"
            queued = enqueue_message(
                pane="%221",
                text="pa-runtime -> pa-qa: queued response",
                mailbox_dir=mailbox_dir,
                sender="pa-runtime",
                topic="peer consultation response",
            )
            fake = FakeTmuxSend(
                baseline_capture="• Done.\n\n› \n",
                captures=["› pa-runtime -> pa-qa: queued response\n\n• Working\n"],
            )

            result = _drain_mailbox(
                "%221",
                submit_key="C-m",
                mailbox_dir=str(mailbox_dir),
                max_retries=0,
                poll_interval_seconds=0,
                polls_per_attempt=1,
                allow_interrupted_recovery=False,
                runner=fake,
            )

            self.assertEqual(result["queued"], 1)
            self.assertEqual(result["delivered"], 1)
            self.assertEqual(result["failed"], 0)
            self.assertFalse(queued.exists())
            self.assertEqual(queued_messages(pane="%221", mailbox_dir=mailbox_dir), [])

    def test_drain_mailbox_keeps_message_when_target_stays_busy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mailbox_dir = Path(tmp) / "mailbox"
            queued = enqueue_message(
                pane="%221",
                text="pa-runtime -> pa-qa: queued response",
                mailbox_dir=mailbox_dir,
            )
            fake = FakeTmuxSend(
                baseline_capture="› previous task\n\n• Working\n",
                captures=[],
            )

            result = _drain_mailbox(
                "%221",
                submit_key="C-m",
                mailbox_dir=str(mailbox_dir),
                max_retries=0,
                poll_interval_seconds=0,
                polls_per_attempt=1,
                allow_interrupted_recovery=False,
                runner=fake,
            )

            self.assertEqual(result["queued"], 1)
            self.assertEqual(result["delivered"], 0)
            self.assertEqual(result["failed"], 1)
            self.assertTrue(queued.exists())

    def test_cli_auto_drains_queued_messages_before_new_send(self) -> None:
        calls: list[str] = []
        original_queued_messages = tmux_send.queued_messages
        original_drain = tmux_send._drain_mailbox
        original_send_text = tmux_send.send_text
        try:
            tmux_send.queued_messages = lambda **_: [Path("queued.json")]  # type: ignore[assignment]

            def fake_drain(*_: object, **__: object) -> dict[str, object]:
                calls.append("drain")
                return {"queued": 1, "delivered": 1, "failed": 0, "delivered_paths": [], "failed_messages": []}

            def fake_send(*_: object, **__: object) -> DeliveryResult:
                calls.append("send")
                return DeliveryResult(True, 1, "• Working")

            tmux_send._drain_mailbox = fake_drain  # type: ignore[assignment]
            tmux_send.send_text = fake_send  # type: ignore[assignment]

            result_json = Path(tempfile.mkdtemp()) / "result.json"
            exit_code = tmux_send.main(["--pane", "%221", "--text", "MainAgent: after drain", "--result-json", str(result_json)])

            self.assertEqual(exit_code, 0)
            self.assertEqual(calls, ["drain", "send"])
            evidence = json.loads(result_json.read_text(encoding="utf-8"))
            self.assertEqual(evidence["auto_drain"]["queued"], 1)
            self.assertEqual(evidence["auto_drain"]["delivered"], 1)
        finally:
            tmux_send.queued_messages = original_queued_messages  # type: ignore[assignment]
            tmux_send._drain_mailbox = original_drain  # type: ignore[assignment]
            tmux_send.send_text = original_send_text  # type: ignore[assignment]

    def test_cli_does_not_send_new_message_when_auto_drain_fails(self) -> None:
        calls: list[str] = []
        original_queued_messages = tmux_send.queued_messages
        original_drain = tmux_send._drain_mailbox
        original_send_text = tmux_send.send_text
        try:
            tmux_send.queued_messages = lambda **_: [Path("queued.json")]  # type: ignore[assignment]

            def fake_drain(*_: object, **__: object) -> dict[str, object]:
                calls.append("drain")
                return {"queued": 1, "delivered": 0, "failed": 1, "delivered_paths": [], "failed_messages": []}

            def fake_send(*_: object, **__: object) -> DeliveryResult:
                calls.append("send")
                return DeliveryResult(True, 1, "• Working")

            tmux_send._drain_mailbox = fake_drain  # type: ignore[assignment]
            tmux_send.send_text = fake_send  # type: ignore[assignment]

            result_json = Path(tempfile.mkdtemp()) / "result.json"
            exit_code = tmux_send.main(["--pane", "%221", "--text", "MainAgent: after drain", "--result-json", str(result_json)])

            self.assertEqual(exit_code, 1)
            self.assertEqual(calls, ["drain"])
            evidence = json.loads(result_json.read_text(encoding="utf-8"))
            self.assertFalse(evidence["accepted"])
            self.assertEqual(evidence["failure_phase"], "auto-drain-failed")
            self.assertEqual(evidence["auto_drain"]["queued"], 1)
            self.assertEqual(evidence["auto_drain"]["failed"], 1)
            self.assertFalse(evidence["new_message_sent"])
            self.assertEqual(evidence["ledger_candidate"], "delivery-defect")
            self.assertTrue(evidence["zero_issue_blocker"])
        finally:
            tmux_send.queued_messages = original_queued_messages  # type: ignore[assignment]
            tmux_send._drain_mailbox = original_drain  # type: ignore[assignment]
            tmux_send.send_text = original_send_text  # type: ignore[assignment]


if __name__ == "__main__":
    unittest.main()
