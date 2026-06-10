from __future__ import annotations

import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude"))

from agent_orchestra_minimal.launch_args import AUTH_ENV_VARS, forwarded_auth_env  # noqa: E402
from agent_orchestra_minimal.launch_material import prepare_launch_material  # noqa: E402


class AuthForwardingTests(unittest.TestCase):
    def test_forwarded_auth_env_only_returns_present_nonempty_vars(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"CLAUDE_CODE_OAUTH_TOKEN": "tok-123", "ANTHROPIC_API_KEY": ""},
            clear=False,
        ):
            forwarded = forwarded_auth_env()
        self.assertEqual(forwarded.get("CLAUDE_CODE_OAUTH_TOKEN"), "tok-123")
        self.assertNotIn("ANTHROPIC_API_KEY", forwarded)
        self.assertIn("CLAUDE_CODE_OAUTH_TOKEN", AUTH_ENV_VARS)

    def test_token_is_forwarded_into_agent_env_and_env_sh(self) -> None:
        cleared = {name: "" for name in AUTH_ENV_VARS}
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "target"
            target.mkdir()
            with mock.patch.dict(
                os.environ,
                {**cleared, "CLAUDE_CODE_OAUTH_TOKEN": "tok-abc"},
                clear=False,
            ):
                material = prepare_launch_material(
                    run_dir=Path(tmpdir) / "run",
                    agent_id="main",
                    agent_kind="MainAgent",
                    target_project=target,
                    instruction_text="Main instruction.",
                )
            self.assertEqual(material.env["CLAUDE_CODE_OAUTH_TOKEN"], "tok-abc")
            # ProfessionalAgent panes source env.sh, so the token must be there too.
            self.assertIn("tok-abc", material.env_shell_path.read_text(encoding="utf-8"))
            # An unset credential is not forwarded as an empty value.
            self.assertNotIn("ANTHROPIC_API_KEY", material.env)

    def test_env_files_carrying_secrets_are_private(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "target"
            target.mkdir()
            with mock.patch.dict(
                os.environ, {"CLAUDE_CODE_OAUTH_TOKEN": "tok-private"}, clear=False
            ):
                material = prepare_launch_material(
                    run_dir=Path(tmpdir) / "run",
                    agent_id="main",
                    agent_kind="MainAgent",
                    target_project=target,
                    instruction_text="Main instruction.",
                )
            for path in (material.env_path, material.env_shell_path):
                mode = stat.S_IMODE(os.stat(path).st_mode)
                self.assertEqual(mode, 0o600, f"{path} should be private (0o600), got {oct(mode)}")


if __name__ == "__main__":
    unittest.main()
