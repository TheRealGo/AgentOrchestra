from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.cli import write_selfe2e_active_main_binding  # noqa: E402


class SelfE2EActiveMainLaunchTests(unittest.TestCase):
    def test_selfe2e_launch_records_active_main_pane_and_session_binding(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "AgentOrchestra"
            status_file = target / ".tmp" / "self-improvement-e2e" / "status"
            status_file.parent.mkdir(parents=True)
            status_file.write_text("progress", encoding="utf-8")
            env: dict[str, str] = {}

            def fake_run(args: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                self.assertEqual(args, ["tmux", "display-message", "-p", "-t", "%439", "#{session_name}"])
                return subprocess.CompletedProcess(
                    args=args,
                    returncode=0,
                    stdout="AgentOrchestra-self-e2e-20260621-200315\n",
                    stderr="",
                )

            binding_path = write_selfe2e_active_main_binding(target, "%439", env, runner=fake_run)

            self.assertEqual(binding_path, status_file.parent / "active-main-session.json")
            self.assertEqual(env["AGENT_ORCHESTRA_SELF_E2E_SESSION"], "AgentOrchestra-self-e2e-20260621-200315")
            self.assertEqual(
                json.loads(binding_path.read_text(encoding="utf-8")),
                {
                    "pane": "%439",
                    "session_name": "AgentOrchestra-self-e2e-20260621-200315",
                },
            )


if __name__ == "__main__":
    unittest.main()
