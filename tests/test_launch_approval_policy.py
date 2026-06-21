from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.launch_args import codex_approval_policy_for_target, codex_launch_argv  # noqa: E402
from agent_orchestra_minimal.launch_material import prepare_launch_material  # noqa: E402


class LaunchApprovalPolicyTests(unittest.TestCase):
    def test_selfe2e_generated_copy_uses_never_approval_inside_workspace_sandbox(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "AgentOrchestra"
            (target / ".tmp" / "self-improvement-e2e").mkdir(parents=True)
            (target / ".tmp" / "self-improvement-e2e" / "status").write_text("progress", encoding="utf-8")

            argv = codex_launch_argv(
                "codex",
                workspace="/tmp/workspace",
                target_project=str(target),
                auto_enable_prevent_idle_sleep=False,
            )

        self.assertEqual(argv[argv.index("--ask-for-approval") + 1], "never")
        self.assertEqual(argv[argv.index("--sandbox") + 1], "workspace-write")
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", argv)

    def test_normal_target_keeps_on_request_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "project"
            target.mkdir()

            argv = codex_launch_argv(
                "codex",
                workspace="/tmp/workspace",
                target_project=str(target),
                auto_enable_prevent_idle_sleep=False,
            )
            self.assertEqual(codex_approval_policy_for_target(target), "on-request")

        self.assertEqual(argv[argv.index("--ask-for-approval") + 1], "on-request")

    def test_service_e2e_target_status_uses_never_approval_inside_workspace_sandbox(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "service"
            (target / ".tmp" / "agent-orchestra-service-e2e").mkdir(parents=True)
            (target / ".tmp" / "agent-orchestra-service-e2e" / "status").write_text(
                "progress",
                encoding="utf-8",
            )

            argv = codex_launch_argv(
                "codex",
                workspace="/tmp/workspace",
                target_project=str(target),
                auto_enable_prevent_idle_sleep=False,
            )
            policy = codex_approval_policy_for_target(target)

        self.assertEqual(policy, "never")
        self.assertEqual(argv[argv.index("--ask-for-approval") + 1], "never")
        self.assertEqual(argv[argv.index("--sandbox") + 1], "workspace-write")
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", argv)

    def test_selfe2e_launch_material_for_all_agent_kinds_uses_never_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            target = root / "AgentOrchestra"
            (target / ".tmp" / "self-improvement-e2e").mkdir(parents=True)
            (target / ".tmp" / "self-improvement-e2e" / "status").write_text("progress", encoding="utf-8")

            for agent_kind in ("MainAgent", "ProfessionalAgent"):
                with self.subTest(agent_kind=agent_kind):
                    material = prepare_launch_material(
                        run_dir=root / f"run-{agent_kind}",
                        agent_id=agent_kind.lower(),
                        agent_kind=agent_kind,
                        target_project=target,
                        instruction_text="Layer instruction.",
                    )

                    argv = list(material.command["argv"])
                    self.assertEqual(argv[argv.index("--ask-for-approval") + 1], "never")
                    self.assertEqual(argv[argv.index("--sandbox") + 1], "workspace-write")
                    self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", argv)

    def test_service_e2e_launch_material_for_all_agent_kinds_uses_never_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            target = root / "service"
            (target / ".tmp" / "agent-orchestra-service-e2e").mkdir(parents=True)
            (target / ".tmp" / "agent-orchestra-service-e2e" / "status").write_text(
                "progress",
                encoding="utf-8",
            )

            for agent_kind in ("MainAgent", "ProfessionalAgent"):
                with self.subTest(agent_kind=agent_kind):
                    material = prepare_launch_material(
                        run_dir=root / f"run-service-{agent_kind}",
                        agent_id=f"service-{agent_kind.lower()}",
                        agent_kind=agent_kind,
                        target_project=target,
                        instruction_text="Service E2E instruction.",
                    )

                    argv = list(material.command["argv"])
                    self.assertEqual(material.command["approval_policy"], "never")
                    self.assertEqual(argv[argv.index("--ask-for-approval") + 1], "never")
                    self.assertEqual(argv[argv.index("--sandbox") + 1], "workspace-write")
                    self.assertEqual(material.env["AGENT_ORCHESTRA_TARGET_PROJECT"], str(target.resolve()))
                    self.assertEqual(material.env["AGENT_ORCHESTRA_EDIT_ROOT"], str(target.resolve()))
                    self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", argv)

    def test_selfe2e_launch_material_adds_explicit_codex_runtime_roots(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            parent = root / "AgentOrchestra-dev"
            target = parent / "AgentOrchestra"
            for relative in (
                ".tmp/self-improvement-e2e",
                ".codex/agent_orchestra_minimal",
                ".codex/skills",
                ".codex/hooks",
            ):
                (target / relative).mkdir(parents=True)
            (target / ".tmp" / "self-improvement-e2e" / "status").write_text(
                "progress",
                encoding="utf-8",
            )

            material = prepare_launch_material(
                run_dir=root / "run",
                agent_id="main",
                agent_kind="MainAgent",
                target_project=target,
                instruction_text="SelfE2E instruction.",
            )

        argv = list(material.command["argv"])
        add_dirs = [argv[index + 1] for index, value in enumerate(argv) if value == "--add-dir"]
        env_access_roots = material.env["AGENT_ORCHESTRA_ACCESS_ROOTS"].split(os.pathsep)
        expected_roots = {
            str(target.resolve()),
            str((target / ".codex").resolve()),
            str((target / ".codex/agent_orchestra_minimal").resolve()),
            str((target / ".codex/skills").resolve()),
            str((target / ".codex/hooks").resolve()),
        }
        self.assertEqual(material.env["AGENT_ORCHESTRA_EDIT_ROOT"], str(target.resolve()))
        self.assertTrue(expected_roots.issubset(set(add_dirs)))
        self.assertTrue(expected_roots.issubset(set(env_access_roots)))
        self.assertNotIn(str(parent.resolve()), add_dirs)


if __name__ == "__main__":
    unittest.main()
