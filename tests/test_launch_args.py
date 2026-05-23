from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.launch_material import prepare_launch_material  # noqa: E402


class LaunchArgsTests(unittest.TestCase):
    def test_launch_material_rejects_codex_args_that_look_like_initial_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_args = (
                ("--", "fix"),
                ("fix", "launcher"),
                ("exec", "echo ok"),
                ("--cd", str(ROOT)),
                ("--add-dir", str(ROOT)),
                ("--dangerously-bypass-hook-trust",),
                ("--dangerously-bypass-approvals-and-sandbox",),
                ("-c", "sandbox_mode=danger-full-access"),
                ("-c", "hooks.enabled=false"),
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

    def test_launch_material_accepts_narrow_safe_codex_args(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            material = prepare_launch_material(
                run_dir=Path(tmpdir) / "run",
                agent_id="pro-safe-argv",
                agent_kind="ProfessionalAgent",
                target_project=ROOT,
                instruction_text="Docs instruction.",
                codex_args=("--model", "gpt-5.5", "--no-alt-screen", "-c", "model_reasoning_effort=high"),
            )

        argv = material.command["argv"]
        self.assertIn("--model", argv)
        self.assertIn("--no-alt-screen", argv)
        self.assertIn("model_reasoning_effort=high", argv)


if __name__ == "__main__":
    unittest.main()
