from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.cli import main as cli_main  # noqa: E402
from agent_orchestra_minimal.codex_config import inspect_mcp_inheritance  # noqa: E402
from agent_orchestra_minimal.doctor import inspect_mcp  # noqa: E402
from agent_orchestra_minimal.launch_material import prepare_launch_material  # noqa: E402


class McpInheritanceContractTests(unittest.TestCase):
    def test_launch_config_inherits_only_mcp_servers_from_user_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            codex_home = root / "user-codex"
            codex_home.mkdir()
            _write_source_config(codex_home / "config.toml")

            with patch.dict(os.environ, _env(codex_home), clear=False):
                material = prepare_launch_material(
                    run_dir=root / "run",
                    agent_id="pro-mcp",
                    agent_kind="ProfessionalAgent",
                    target_project=ROOT,
                    instruction_text="MCP inheritance instruction.",
                )

            config = material.config_path.read_text(encoding="utf-8")
            command = json.loads(material.command_path.read_text(encoding="utf-8"))

        self.assertIn("[mcp_servers.memory]", config)
        self.assertIn("[mcp_servers.playwright.env]", config)
        self.assertIn('TOKEN = "secret-value"', config)
        self.assertIn("startup_timeout_sec = 90", config)
        self.assertNotIn('approval_policy = "on-request"', config)
        self.assertNotIn('sandbox_mode = "danger-full-access"', config)
        self.assertNotIn("echo source-hook", config)
        self.assertNotIn("[profiles.source-profile]", config)
        self.assertEqual(command["mcp_servers"], ["memory", "playwright"])
        summary = json.dumps(command, sort_keys=True)
        self.assertNotIn("secret-value", summary)
        self.assertNotIn("@playwright/mcp", summary)

    def test_missing_source_config_does_not_block_launch(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            with patch.dict(os.environ, _env(root / "missing-codex", home=root / "home"), clear=False):
                material = prepare_launch_material(
                    run_dir=root / "run",
                    agent_id="pro-no-mcp",
                    agent_kind="ProfessionalAgent",
                    target_project=ROOT,
                    instruction_text="No MCP source instruction.",
                )
                config = material.config_path.read_text(encoding="utf-8")

        self.assertEqual(material.command["mcp_servers"], [])
        self.assertNotIn("[mcp_servers.", config)

    def test_mcp_inheritance_can_be_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            codex_home = root / "user-codex"
            codex_home.mkdir()
            _write_source_config(codex_home / "config.toml")
            env = _env(codex_home) | {"AGENT_ORCHESTRA_DISABLE_MCP_INHERITANCE": "1"}

            with patch.dict(os.environ, env, clear=False):
                material = prepare_launch_material(
                    run_dir=root / "run",
                    agent_id="pro-mcp-disabled",
                    agent_kind="ProfessionalAgent",
                    target_project=ROOT,
                    instruction_text="MCP disabled instruction.",
                )
                config = material.config_path.read_text(encoding="utf-8")

        self.assertEqual(material.command["mcp_servers"], [])
        self.assertTrue(material.command["mcp_inheritance_disabled"])
        self.assertNotIn("[mcp_servers.", config)

    def test_nested_agent_inherits_mcp_from_parent_generated_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            codex_home = root / "user-codex"
            codex_home.mkdir()
            _write_source_config(codex_home / "config.toml")

            with patch.dict(os.environ, _env(codex_home), clear=False):
                main = prepare_launch_material(
                    run_dir=root / "run",
                    agent_id="main",
                    agent_kind="MainAgent",
                    target_project=ROOT,
                    instruction_text="Main MCP inheritance instruction.",
                )

            with patch.dict(os.environ, main.env, clear=True):
                child = prepare_launch_material(
                    run_dir=main.run_dir,
                    agent_id="pro-child",
                    agent_kind="ProfessionalAgent",
                    target_project=ROOT,
                    instruction_text="Child MCP inheritance instruction.",
                    task_file=main.task_file,
                )
                config = child.config_path.read_text(encoding="utf-8")

        self.assertEqual(child.command["mcp_servers"], ["memory", "playwright"])
        self.assertIn("[mcp_servers.playwright]", config)
        self.assertIn("[mcp_servers.memory]", config)
        self.assertNotIn('approval_policy = "on-request"', config)

    def test_existing_long_mcp_startup_timeout_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            codex_home = root / "user-codex"
            codex_home.mkdir()
            _write_source_config(codex_home / "config.toml")
            with (codex_home / "config.toml").open("a", encoding="utf-8") as f:
                f.write("\nstartup_timeout_sec = 120\n")

            with patch.dict(os.environ, _env(codex_home), clear=False):
                material = prepare_launch_material(
                    run_dir=root / "run",
                    agent_id="pro-timeout",
                    agent_kind="ProfessionalAgent",
                    target_project=ROOT,
                    instruction_text="MCP timeout instruction.",
                )
                config = material.config_path.read_text(encoding="utf-8")

        self.assertIn("startup_timeout_sec = 120", config)

    def test_existing_short_mcp_startup_timeout_is_raised_to_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            codex_home = root / "user-codex"
            codex_home.mkdir()
            _write_source_config(codex_home / "config.toml")
            with (codex_home / "config.toml").open("a", encoding="utf-8") as f:
                f.write("\nstartup_timeout_sec = 12\n")

            with patch.dict(os.environ, _env(codex_home), clear=False):
                material = prepare_launch_material(
                    run_dir=root / "run",
                    agent_id="pro-short-timeout",
                    agent_kind="ProfessionalAgent",
                    target_project=ROOT,
                    instruction_text="MCP short timeout instruction.",
                )
                config = material.config_path.read_text(encoding="utf-8")

        self.assertIn("startup_timeout_sec = 90", config)

    def test_doctor_mcp_reports_source_names_playwright_and_commands_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            codex_home = root / "user-codex"
            codex_home.mkdir()
            _write_source_config(codex_home / "config.toml")

            with patch.dict(os.environ, _env(codex_home), clear=False):
                inheritance = inspect_mcp_inheritance()
                report = inspect_mcp(command_checker=lambda command: Path(command).name in {"node", "npx"})

        self.assertTrue(inheritance.playwright_present)
        self.assertFalse(report.failed)
        self.assertIn("MCP servers: memory, playwright", report.lines)
        self.assertIn("Playwright MCP: present", report.lines)
        output = "\n".join(report.lines)
        self.assertNotIn("secret-value", output)
        self.assertNotIn("@playwright/mcp", output)

    def test_doctor_cli_accepts_mcp_flag(self) -> None:
        with patch("agent_orchestra_minimal.cli.doctor_command", return_value=0) as doctor:
            result = cli_main(["doctor", "--target-project", str(ROOT), "--mcp"])

        self.assertEqual(result, 0)
        self.assertTrue(doctor.call_args.args[0].mcp)


def _write_source_config(path: Path) -> None:
    path.write_text(
        """\
approval_policy = "on-request"
sandbox_mode = "danger-full-access"

[[hooks.Stop]]
command = "echo source-hook"

[profiles.source-profile]
model = "source-only"

[mcp_servers.playwright]
command = "npx"
args = ["-y", "@playwright/mcp"]

[mcp_servers.playwright.env]
TOKEN = "secret-value"

[mcp_servers.memory]
command = "node"
args = ["server.js"]
""",
        encoding="utf-8",
    )


def _env(codex_home: Path, *, home: Path | None = None) -> dict[str, str]:
    env = {
        "CODEX_HOME": str(codex_home),
        "AGENT_ORCHESTRA_MCP_SOURCE_CONFIG": str(codex_home / "config.toml"),
        "AGENT_ORCHESTRA_DISABLE_PREVENT_IDLE_SLEEP": "1",
    }
    if home is not None:
        env["HOME"] = str(home)
    return env


if __name__ == "__main__":
    unittest.main()
