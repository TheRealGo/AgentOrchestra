from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude"))
from agent_orchestra_minimal.launch_material import prepare_launch_material  # noqa: E402


class LaunchMaterialHookIOTests(unittest.TestCase):
    def test_generated_stop_hook_runs_from_isolated_claude_home(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            fake_bin = tmp / "bin"
            fake_bin.mkdir()
            calls = tmp / "tmux_calls.txt"
            fake_tmux = fake_bin / "tmux"
            fake_tmux.write_text(
                "#!/bin/sh\ncat >/dev/null\nprintf '%s\\n' \"$*\" >> \"$AO_TMUX_CALLS\"\nexit 0\n",
                encoding="utf-8",
            )
            fake_tmux.chmod(0o755)

            material = prepare_launch_material(
                run_dir=tmp / "run",
                agent_id="main-hook",
                agent_kind="MainAgent",
                target_project=ROOT,
                instruction_text="Hook smoke instruction.",
                tmux_pane="%7",
            )
            material.task_file.write_text(
                "[status]\nprogress\n\n[Backlog]\n\n[InProgress]\n\n[InReview]\n\n[Candidates]\n\n[Done]\n",
                encoding="utf-8",
            )
            env = os.environ | material.env | {
                "AO_TMUX_CALLS": str(calls),
                "PATH": f"{fake_bin}{os.pathsep}{os.environ.get('PATH', '')}",
            }
            result = subprocess.run(
                [
                    material.env["AGENT_ORCHESTRA_PYTHON"],
                    str(material.claude_config_dir / "hooks" / "agent_orchestra_stop_hook.py"),
                ],
                # Claude Code delivers Stop Hook context as JSON on stdin; the hook
                # drains it before deciding the re-kick from env + task/state.
                input='{"hook_event_name":"Stop","stop_hook_active":false}',
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            calls_text = calls.read_text(encoding="utf-8")
            # Fire-and-forget wake: a paste followed by exactly three submit-key
            # presses. There is no poll/capture confirmation (it would deadlock on
            # the agent's own Stop Hook), so the reason has no delivery suffix and
            # the hook prints no wake issue.
            self.assertIn("load-buffer", calls_text)
            self.assertIn("paste-buffer -t %7", calls_text)
            self.assertEqual(calls_text.count("send-keys -t %7 C-m"), 3)
            self.assertNotIn("capture-pane", calls_text)
            self.assertNotIn("wake issue", result.stderr)


if __name__ == "__main__":
    unittest.main()
