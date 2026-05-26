from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.launch_material import prepare_launch_material  # noqa: E402


class CodexConfigContractTests(unittest.TestCase):
    def test_launch_config_escapes_toml_path_keys(self) -> None:
        with tempfile.TemporaryDirectory(prefix='agent"orchestra-') as tmpdir:
            material = prepare_launch_material(
                run_dir=Path(tmpdir) / "run",
                agent_id="main",
                agent_kind="MainAgent",
                target_project=ROOT,
                instruction_text="Main instruction.",
            )

            config = material.config_path.read_text(encoding="utf-8")

        escaped_workspace = _toml_key_text(str(material.workspace))
        self.assertIn(f'[projects."{escaped_workspace}"]', config)
        self.assertIn('trust_level = "trusted"', config)
        state_key = f"{material.config_path}:stop:0:0"
        escaped_state_key = _toml_key_text(state_key)
        self.assertIn(f'[hooks.state."{escaped_state_key}"]', config)
        self.assertIn(r"agent\"orchestra-", config)


def _toml_key_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


if __name__ == "__main__":
    unittest.main()
