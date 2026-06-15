from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.process_env import clean_codex_env  # noqa: E402


class ProcessEnvContractTests(unittest.TestCase):
    def test_clean_codex_env_keeps_terminal_basics_and_drops_secrets(self) -> None:
        env = clean_codex_env(
            {"CODEX_HOME": "/isolated/codex", "AGENT_ORCHESTRA_AGENT_ID": "main"},
            parent_env={
                "PATH": "/bin",
                "TERM": "xterm-256color",
                "GITHUB_TOKEN": "secret",
                "OPENAI_API_KEY": "secret",
                "CUSTOM_PASSWORD": "secret",
                "UNRELATED": "drop-me",
            },
        )

        self.assertEqual(env["PATH"], "/bin")
        self.assertEqual(env["TERM"], "xterm-256color")
        self.assertEqual(env["CODEX_HOME"], "/isolated/codex")
        self.assertEqual(env["AGENT_ORCHESTRA_AGENT_ID"], "main")
        self.assertNotIn("GITHUB_TOKEN", env)
        self.assertNotIn("OPENAI_API_KEY", env)
        self.assertNotIn("CUSTOM_PASSWORD", env)
        self.assertNotIn("UNRELATED", env)


if __name__ == "__main__":
    unittest.main()
