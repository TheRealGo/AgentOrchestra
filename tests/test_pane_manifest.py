from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.pane_manifest import PaneRecord, resume_decision  # noqa: E402


class PaneManifestTests(unittest.TestCase):
    def test_usage_limited_and_stale_panes_are_quarantined_for_resume(self) -> None:
        decision = resume_decision(
            [
                PaneRecord("main-recovery", "%11", "usage_limited", "checkpoint-a"),
                PaneRecord("main", "%12", "working_stale", "checkpoint-b"),
            ]
        )

        self.assertEqual(decision.active, ())
        self.assertEqual([record.agent_id for record in decision.quarantine], ["main-recovery", "main"])
        self.assertEqual(
            decision.strategy,
            "launch_recovery_from_latest_checkpoint_and_keep_stale_panes_quarantined",
        )

    def test_single_active_pane_is_safe_resume_target(self) -> None:
        active = PaneRecord("main", "%12", "working", "checkpoint-b")
        stale = PaneRecord("main-recovery", "%11", "usage_limited", "checkpoint-a")

        decision = resume_decision([stale, active])

        self.assertEqual(decision.active, (active,))
        self.assertEqual(decision.quarantine, (stale,))
        self.assertEqual(decision.strategy, "resume_active_pane")


if __name__ == "__main__":
    unittest.main()
