from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.doctor import inspect_tmux_liveness  # noqa: E402
from agent_orchestra_minimal.tmux_liveness import (  # noqa: E402
    classify_capture,
    inspect_pane_liveness,
    normalized_activity_fingerprint,
)


class FakeLivenessTmux:
    def __init__(self, captures: list[str]) -> None:
        self.captures = captures
        self.calls: list[list[str]] = []

    def __call__(self, args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        self.calls.append(args)
        stdout = self.captures.pop(0) if self.captures else ""
        return subprocess.CompletedProcess(args=args, returncode=0, stdout=stdout, stderr="")


class TmuxLivenessTests(unittest.TestCase):
    def test_classifies_visibly_working_without_substantive_change_as_stale(self) -> None:
        first = "• Working (7s • esc to interrupt)\n\n› Summarize recent commit\n"
        second = "• Working (38s • esc to interrupt)\n\n› Summarize recent commit\n"
        fake = FakeLivenessTmux([first, second])

        liveness = inspect_pane_liveness("%199", runner=fake, interval_seconds=0)

        self.assertEqual(liveness.state, "working_stale")
        self.assertTrue(liveness.stale_working)

    def test_classifies_working_with_new_tool_output_as_progress(self) -> None:
        first = "• Working (7s • esc to interrupt)\n\n› Summarize recent commit\n"
        second = "• Working (38s • esc to interrupt)\n\n• Explored\n  └ Read ProductApp.tsx\n"
        fake = FakeLivenessTmux([first, second])

        liveness = inspect_pane_liveness("%199", runner=fake, interval_seconds=0)

        self.assertEqual(liveness.state, "working")
        self.assertFalse(liveness.stale_working)
        self.assertTrue(liveness.changed)

    def test_ignores_timer_only_changes_in_fingerprint(self) -> None:
        first = "◦ Working (7s • esc to interrupt)\n\nPursuing goal (3h 9m)\n"
        second = "◦ Working (45s • esc to interrupt)\n\nPursuing goal (3h 10m)\n"

        self.assertEqual(
            normalized_activity_fingerprint(first),
            normalized_activity_fingerprint(second),
        )

    def test_ready_prompt_is_not_stale(self) -> None:
        self.assertEqual(classify_capture("› Use /skills to list available skills\n"), "ready")

    def test_old_prompt_before_activity_is_not_ready(self) -> None:
        capture = (
            "› Explain this codebase\n\n"
            "• Using agent-orchestra-task-file\n\n"
            "• Explored\n"
            "  └ Read tasks.ini\n\n"
            "  gpt-5.5 default · ${HOME}/Li…\n"
        )

        self.assertEqual(classify_capture(capture), "unknown")

    def test_doctor_fails_on_stale_working(self) -> None:
        with patch(
            "agent_orchestra_minimal.doctor.inspect_pane_liveness",
            return_value=type(
                "Liveness",
                (),
                {
                    "state": "working_stale",
                    "changed": False,
                    "reason": "pane remained visibly Working without substantive output changes",
                    "stale_working": True,
                },
            )(),
        ):
            report = inspect_tmux_liveness("%199", samples=2, interval_seconds=0)

        self.assertTrue(report.failed)
        self.assertIn("stale Working requires interrupt", "\n".join(report.lines))


if __name__ == "__main__":
    unittest.main()
