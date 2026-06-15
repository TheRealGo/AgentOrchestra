from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.agent_state import AgentState  # noqa: E402
from agent_orchestra_minimal.cli import current_tmux_pane, default_run_dir, default_run_root, start_main  # noqa: E402
from agent_orchestra_minimal.codex_features import CodexFeatureReport  # noqa: E402
from agent_orchestra_minimal.launch_args import codex_launch_argv, main_tmux_pane  # noqa: E402
from agent_orchestra_minimal.launch_args import _codex_supports_prevent_idle_sleep  # noqa: E402
from agent_orchestra_minimal.launch_material import prepare_launch_material  # noqa: E402


class LaunchArgsTests(unittest.TestCase):
    def setUp(self) -> None:
        _codex_supports_prevent_idle_sleep.cache_clear()

    def test_launch_material_rejects_codex_args_that_look_like_initial_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_args = (
                ("--", "fix"),
                ("fix", "launcher"),
                ("exec", "echo ok"),
                ("--profile", "agent-orchestra"),
                ("--profile=agent-orchestra",),
                ("--profile-v2", "agent-orchestra"),
                ("--profile-v2=agent-orchestra",),
                ("--enable", "prevent_idle_sleep"),
                ("--enable=prevent_idle_sleep",),
                ("--cd", str(ROOT)),
                (f"--cd={ROOT}",),
                ("--add-dir", str(ROOT)),
                (f"--add-dir={ROOT}",),
                ("--dangerously-bypass-hook-trust",),
                ("--dangerously-bypass-hook-trust=true",),
                ("--dangerously-bypass-approvals-and-sandbox",),
                ("--dangerously-bypass-approvals-and-sandbox=true",),
                ("-c", "sandbox_mode=danger-full-access"),
                ("-c", "hooks.enabled=false"),
                ("-c", "default_permissions=:workspace"),
                ("-c", "permissions.project-edit.network.enabled=true"),
                ("-c=sandbox_mode=danger-full-access",),
                ("-c=hooks.enabled=false",),
                ("-c=default_permissions=:workspace",),
                ("-c=permissions.project-edit.network.enabled=true",),
                ("--model", "--cd"),
                ("--model=--cd",),
                ("--model=",),
                ("--model", "--"),
                ("--model", "--no-alt-screen"),
                ("-m", "--add-dir"),
                ("-m=--add-dir",),
                ("-m=",),
                ("-c", "--no-alt-screen"),
                ("-c=--no-alt-screen",),
                ("-c=",),
            )
            for codex_args in bad_args:
                with self.subTest(codex_args=codex_args):
                    with self.assertRaisesRegex(ValueError, "codex_args"):
                        prepare_launch_material(
                            run_dir=Path(tmpdir) / "run",
                            agent_id="pro-bad-argv",
                            agent_kind="ProfessionalAgent",
                            target_project=ROOT,
                            instruction_text="Docs instruction.",
                            codex_args=codex_args,
                        )

    def test_invalid_codex_args_do_not_write_partial_launch_material(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir) / "run"

            with self.assertRaisesRegex(ValueError, "codex_args"):
                prepare_launch_material(
                    run_dir=run_dir,
                    agent_id="pro-bad-argv",
                    agent_kind="ProfessionalAgent",
                    target_project=ROOT,
                    instruction_text="Docs instruction.",
                    codex_args=("--profile", "agent-orchestra"),
                )

            self.assertFalse((run_dir / "agents" / "pro-bad-argv").exists())

    def test_launch_material_accepts_narrow_safe_codex_args(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            material = prepare_launch_material(
                run_dir=Path(tmpdir) / "run",
                agent_id="pro-safe-argv",
                agent_kind="ProfessionalAgent",
                target_project=ROOT,
                instruction_text="Docs instruction.",
                codex_args=(
                    "--model",
                    "gpt-5.5",
                    "--model=gpt-5.5",
                    "-m=gpt-5.5",
                    "--no-alt-screen",
                    "-c",
                    "model_reasoning_effort=high",
                    "-c=model_reasoning_effort=high",
                ),
            )

        argv = material.command["argv"]
        self.assertIn("--model", argv)
        self.assertIn("--model=gpt-5.5", argv)
        self.assertIn("-m=gpt-5.5", argv)
        self.assertIn("--no-alt-screen", argv)
        self.assertIn("model_reasoning_effort=high", argv)
        self.assertIn("-c=model_reasoning_effort=high", argv)

    def test_default_run_root_uses_explicit_environment_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            configured = Path(tmpdir) / "durable-runs"
            with patch.dict(os.environ, {"AGENT_ORCHESTRA_RUN_ROOT": str(configured)}, clear=False):
                self.assertEqual(default_run_root(), configured)
                self.assertEqual(default_run_dir().parent, configured)

    def test_default_run_root_avoids_tmp_without_override(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            root = default_run_root()

        self.assertNotIn("/tmp", str(root))
        self.assertNotIn("/private/tmp", str(root))
        self.assertTrue(default_run_dir().name.endswith("-agent-orchestra"))

    def test_start_main_does_not_pass_secret_parent_environment_to_codex(self) -> None:
        class Material:
            run_dir = Path("/run")
            workspace = Path("/")
            env = {"CODEX_HOME": "/isolated/codex", "AGENT_ORCHESTRA_AGENT_ID": "main"}
            command = {"argv": ["codex", "--version"]}

        args = type(
            "Args",
            (),
            {
                "target_project": str(ROOT),
                "target_project_arg": None,
                "run_dir": str(ROOT / ".tmp" / "run"),
                "agent_id": "main",
                "dry_run": False,
            },
        )()
        captured: dict[str, dict[str, str]] = {}

        def fake_execvpe(_program: str, _argv: list[str], env: dict[str, str]) -> None:
            captured["env"] = env
            raise SystemExit(0)

        with patch.dict(os.environ, {"PATH": "/bin", "GITHUB_TOKEN": "secret", "OPENAI_API_KEY": "secret"}, clear=True):
            with patch("agent_orchestra_minimal.cli.current_tmux_pane", return_value="%1"):
                with patch("agent_orchestra_minimal.cli.prepare_main_material", return_value=Material()):
                    with patch("agent_orchestra_minimal.cli.os.chdir"):
                        with patch("agent_orchestra_minimal.cli.os.execvpe", side_effect=fake_execvpe):
                            with self.assertRaises(SystemExit):
                                start_main(args)

        self.assertEqual(captured["env"]["PATH"], "/bin")
        self.assertEqual(captured["env"]["CODEX_HOME"], "/isolated/codex")
        self.assertNotIn("GITHUB_TOKEN", captured["env"])
        self.assertNotIn("OPENAI_API_KEY", captured["env"])

    def test_launch_argv_enables_prevent_idle_sleep_when_codex_feature_exists(self) -> None:
        report = CodexFeatureReport(
            failed=False,
            features={"prevent_idle_sleep": "disabled"},
            lines=["Codex features prevent_idle_sleep=disabled"],
        )
        with patch.dict(os.environ, {"AGENT_ORCHESTRA_DISABLE_PREVENT_IDLE_SLEEP": ""}, clear=False):
            with patch("agent_orchestra_minimal.launch_args.run_codex_features_list", return_value=report):
                argv = codex_launch_argv(
                    "codex",
                    workspace="/tmp/workspace",
                    target_project=str(ROOT),
                )

        self.assertIn("--enable", argv)
        self.assertIn("prevent_idle_sleep", argv)

    def test_launch_argv_adds_runtime_roots_without_changing_edit_roots(self) -> None:
        argv = codex_launch_argv(
            "codex",
            workspace="/run/agents/main/workspace",
            target_project="/repo",
            access_roots=("/repo", "/repo-root"),
            runtime_roots=("/run", "/repo"),
            auto_enable_prevent_idle_sleep=False,
        )

        add_dirs = [argv[index + 1] for index, value in enumerate(argv) if value == "--add-dir"]
        self.assertEqual(add_dirs, ["/repo", "/repo-root", "/run"])

    def test_launch_argv_does_not_enable_prevent_idle_sleep_when_feature_probe_fails(self) -> None:
        report = CodexFeatureReport(
            failed=True,
            features={},
            lines=["Codex features list could not run"],
        )
        with patch("agent_orchestra_minimal.launch_args.run_codex_features_list", return_value=report):
            argv = codex_launch_argv(
                "codex",
                workspace="/tmp/workspace",
                target_project=str(ROOT),
            )

        self.assertNotIn("prevent_idle_sleep", argv)

    def test_launch_argv_does_not_enable_prevent_idle_sleep_when_feature_is_absent(self) -> None:
        report = CodexFeatureReport(
            failed=False,
            features={"prevent_idle_sleep": "absent"},
            lines=["Codex features prevent_idle_sleep=absent"],
        )
        with patch("agent_orchestra_minimal.launch_args.run_codex_features_list", return_value=report):
            argv = codex_launch_argv(
                "codex",
                workspace="/tmp/workspace",
                target_project=str(ROOT),
            )

        self.assertNotIn("prevent_idle_sleep", argv)

    def test_launch_argv_prevent_idle_sleep_opt_out(self) -> None:
        report = CodexFeatureReport(
            failed=False,
            features={"prevent_idle_sleep": "disabled"},
            lines=["Codex features prevent_idle_sleep=disabled"],
        )
        with patch.dict(os.environ, {"AGENT_ORCHESTRA_DISABLE_PREVENT_IDLE_SLEEP": "1"}, clear=False):
            with patch("agent_orchestra_minimal.launch_args.run_codex_features_list", return_value=report):
                argv = codex_launch_argv(
                    "codex",
                    workspace="/tmp/workspace",
                    target_project=str(ROOT),
                )

        self.assertNotIn("prevent_idle_sleep", argv)

    def test_professional_main_pane_requires_explicit_main_pane_environment(self) -> None:
        with patch.dict(os.environ, {"AGENT_ORCHESTRA_TMUX_PANE": "%caller"}, clear=True):
            self.assertIsNone(main_tmux_pane("ProfessionalAgent", "%pro"))

        with patch.dict(os.environ, {"AGENT_ORCHESTRA_MAIN_TMUX_PANE": "%main"}, clear=True):
            self.assertEqual(main_tmux_pane("ProfessionalAgent", "%pro"), "%main")

    def test_blank_tmux_pane_values_are_not_written_as_deterministic_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            material = prepare_launch_material(
                run_dir=Path(tmpdir) / "run",
                agent_id="pro-blank-pane",
                agent_kind="ProfessionalAgent",
                target_project=ROOT,
                instruction_text="Docs instruction.",
                tmux_pane="   ",
            )
            state = AgentState.read(material.state_file)

        self.assertNotIn("AGENT_ORCHESTRA_TMUX_PANE", material.env)
        self.assertIsNone(state.tmux_target)

    def test_main_pane_environment_is_trimmed_and_blank_values_are_ignored(self) -> None:
        self.assertEqual(main_tmux_pane("MainAgent", "  %main  "), "%main")
        self.assertIsNone(main_tmux_pane("MainAgent", "   "))
        with patch.dict(os.environ, {"AGENT_ORCHESTRA_MAIN_TMUX_PANE": "  %main  "}, clear=True):
            self.assertEqual(main_tmux_pane("ProfessionalAgent", "%pro"), "%main")
        with patch.dict(os.environ, {"AGENT_ORCHESTRA_MAIN_TMUX_PANE": "   "}, clear=True):
            self.assertIsNone(main_tmux_pane("ProfessionalAgent", "%pro"))

    def test_tmux_pane_values_must_be_deterministic_pane_ids(self) -> None:
        for value in ("1", ":0.1", "%main other", "%main\nother"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "tmux pane"):
                main_tmux_pane("MainAgent", value)
        with patch.dict(os.environ, {"AGENT_ORCHESTRA_MAIN_TMUX_PANE": ":0.1"}, clear=True):
            with self.assertRaisesRegex(ValueError, "tmux pane"):
                main_tmux_pane("ProfessionalAgent", "%pro")

    def test_current_tmux_pane_does_not_infer_from_active_client_pane(self) -> None:
        with patch.dict(os.environ, {"TMUX": "/tmp/tmux-123/default,1,0"}, clear=True):
            with patch("agent_orchestra_minimal.cli.pane_from_current_tty", return_value=None):
                with patch("agent_orchestra_minimal.cli.subprocess.run") as run:
                    pane = current_tmux_pane()

        self.assertIsNone(pane)
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
