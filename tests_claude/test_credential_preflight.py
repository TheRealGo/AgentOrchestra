from __future__ import annotations

import contextlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude"))

from agent_orchestra_minimal import cli  # noqa: E402
from agent_orchestra_minimal.launch_args import AUTH_ENV_VARS  # noqa: E402


def _warn(config_dir: Path) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        cli._warn_if_no_credential(SimpleNamespace(claude_config_dir=config_dir))
    return buf.getvalue()


class CredentialPreflightTests(unittest.TestCase):
    def test_warns_when_no_token_and_no_credentials_file(self) -> None:
        cleared = {name: "" for name in AUTH_ENV_VARS}
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, cleared, clear=False):
                out = _warn(Path(tmp))
        self.assertIn("Not logged in", out)
        self.assertIn("claude setup-token", out)
        self.assertIn("CLAUDE_CODE_OAUTH_TOKEN", out)
        # The warning must not claim the Keychain will be used.
        self.assertIn("does not read the macOS Keychain", out)
        # It must not advise a per-Agent `/login` (does not scale to the team);
        # the one exported credential reaches every Agent via the forwarded env.sh.
        self.assertNotIn("/login", out)
        self.assertIn("cannot", out)

    def test_silent_when_token_is_present(self) -> None:
        cleared = {name: "" for name in AUTH_ENV_VARS}
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(
                os.environ, {**cleared, "CLAUDE_CODE_OAUTH_TOKEN": "tok"}, clear=False
            ):
                out = _warn(Path(tmp))
        self.assertEqual(out, "")

    def test_silent_when_credentials_file_is_present(self) -> None:
        cleared = {name: "" for name in AUTH_ENV_VARS}
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".credentials.json").write_text("{}", encoding="utf-8")
            with mock.patch.dict(os.environ, cleared, clear=False):
                out = _warn(Path(tmp))
        self.assertEqual(out, "")


if __name__ == "__main__":
    unittest.main()
