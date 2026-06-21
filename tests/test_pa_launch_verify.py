from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.launch_io import RUNTIME_FILES  # noqa: E402
from agent_orchestra_minimal.pa_launch_verify import verify_pane_identity  # noqa: E402


class ProfessionalAgentLaunchVerifyTests(unittest.TestCase):
    def test_accepts_verified_codex_pane(self) -> None:
        result = verify_pane_identity(
            expected_pane="%631",
            expected_session="AgentOrchestra-self-e2e-20260622-050109",
            expected_cwd="/run/agents/pa-layer15-qa/workspace",
            display_line=(
                "AgentOrchestra-self-e2e-20260622-050109:1.3 %631 "
                "node /run/agents/pa-layer15-qa/workspace"
            ),
            capture="│ >_ OpenAI Codex │\n› Implement {feature}\n  gpt-5.5 default\n",
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.reasons, ())

    def test_rejects_shell_pane_before_task_delivery(self) -> None:
        result = verify_pane_identity(
            expected_pane="%631",
            expected_session="AgentOrchestra-self-e2e-20260622-050109",
            expected_cwd="/run/agents/pa-layer15-qa/workspace",
            display_line=(
                "AgentOrchestra-self-e2e-20260622-050109:1.3 %631 "
                "zsh /run/agents/main/workspace"
            ),
            capture="Directory: /run/agents/main/workspace\n# ",
        )

        self.assertFalse(result.valid)
        self.assertIn("shell-process", result.reasons)
        self.assertIn("cwd-mismatch", result.reasons)
        self.assertIn("tui-capture-missing", result.reasons)

    def test_rejects_wrong_session_and_pane(self) -> None:
        result = verify_pane_identity(
            expected_pane="%631",
            expected_session="AgentOrchestra-self-e2e-20260622-050109",
            expected_cwd="/run/agents/pa-layer15-qa/workspace",
            display_line="ToO:0.1 %335 node /run/agents/pa-layer15-qa/workspace",
            capture="│ >_ OpenAI Codex │\n› Find and fix a bug in @filename\n",
        )

        self.assertFalse(result.valid)
        self.assertIn("pane-id-mismatch", result.reasons)
        self.assertIn("session-mismatch", result.reasons)

    def test_rejects_codex_process_in_main_workspace(self) -> None:
        result = verify_pane_identity(
            expected_pane="%632",
            expected_session="AgentOrchestra-self-e2e-20260622-050109",
            expected_cwd="/run/agents/pa-layer16-runtime/workspace",
            display_line=(
                "AgentOrchestra-self-e2e-20260622-050109:1.4 %632 "
                "node /run/agents/main/workspace"
            ),
            capture="│ >_ OpenAI Codex │\n› Improve documentation in @filename\n",
        )

        self.assertFalse(result.valid)
        self.assertEqual(result.reasons, ("cwd-mismatch",))

    def test_pa_launch_verifier_is_installed_into_isolated_runtime_material(self) -> None:
        self.assertIn("pa_launch_verify.py", RUNTIME_FILES)


if __name__ == "__main__":
    unittest.main()
