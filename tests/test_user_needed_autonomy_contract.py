from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEX = ROOT / ".codex"
sys.path.insert(0, str(CODEX))

from agent_orchestra_minimal.launch_material import prepare_launch_material  # noqa: E402


class UserNeededAutonomyContractTests(unittest.TestCase):
    def test_runtime_surfaces_define_true_user_needed_boundary(self) -> None:
        surfaces = [
            ROOT / "SPEC.md",
            ROOT / "README.md",
            ROOT / "README.ja.md",
            CODEX / "skills" / "agent-orchestra-team" / "SKILL.md",
            CODEX / "skills" / "agent-orchestra-environment" / "SKILL.md",
            CODEX / "agent_orchestra_minimal" / "agent_templates" / "main.AGENTS.md",
            CODEX / "agent_orchestra_minimal" / "agent_templates" / "professional.AGENTS.md",
        ]

        for path in surfaces:
            text = " ".join(path.read_text(encoding="utf-8").split())
            self.assertIn("needs_user", text, path)
            self.assertIn("credential", text, path)
            self.assertIn("payment", text, path)
            self.assertTrue("physical" in text or "物理" in text, path)
            self.assertTrue("legal/security" in text or "法務/安全" in text, path)
            self.assertIn("scope", text, path)

    def test_low_risk_in_scope_work_is_not_rejected_for_lack_of_blanket_approval(self) -> None:
        surfaces = [
            CODEX / "skills" / "agent-orchestra-team" / "SKILL.md",
            CODEX / "agent_orchestra_minimal" / "agent_templates" / "main.AGENTS.md",
            ROOT / "SPEC.md",
        ]

        for path in surfaces:
            text = " ".join(path.read_text(encoding="utf-8").split())
            self.assertTrue(
                "Routine work inside the active editable surface" in text
                or "Routine work inside the already granted editable surface" in text,
                path,
            )
            self.assertIn("current Codex build lacks a blanket auto-approval feature", text, path)
            self.assertIn("fixable AgentOrchestra candidate", text, path)
            self.assertIn("[status] progress", text, path)

    def test_service_e2e_approval_cleanup_boundaries_are_documented(self) -> None:
        surfaces = [
            ROOT / "SPEC.md",
            ROOT / "README.md",
            CODEX / "skills" / "agent-orchestra-team" / "SKILL.md",
            CODEX / "skills" / "agent-orchestra-environment" / "SKILL.md",
            CODEX / "skills" / "agent-orchestra-service-e2e-improvement" / "SKILL.md",
            CODEX / "agent_orchestra_minimal" / "agent_templates" / "main.AGENTS.md",
            CODEX / "agent_orchestra_minimal" / "agent_templates" / "professional.AGENTS.md",
        ]

        for path in surfaces:
            text = " ".join(path.read_text(encoding="utf-8").split())
            self.assertTrue("browser" in text and ("iOS" in text or "ios" in text), path)
            self.assertTrue("Docker" in text or "compose" in text, path)
            self.assertIn("ownership", text, path)
            self.assertIn("autonomy defect", text, path)

    def test_generated_main_and_professional_startup_include_user_needed_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            for agent_kind in ("MainAgent", "ProfessionalAgent"):
                material = prepare_launch_material(
                    run_dir=Path(tmpdir) / agent_kind,
                    agent_id=agent_kind.lower(),
                    agent_kind=agent_kind,
                    target_project=ROOT,
                    instruction_text="Instruction.",
                )
                startup = " ".join(material.startup_agents.read_text(encoding="utf-8").split())
                self.assertIn("needs_user", startup)
                self.assertIn("credential", startup)
                self.assertIn("account/provider setup", startup)
                self.assertIn("payment", startup)
                self.assertIn("physical", startup)
                self.assertIn("legal/security", startup)
                self.assertIn("scope expansion", startup)
                self.assertIn("local browser", startup)
                self.assertIn("Docker cleanup", startup)
                self.assertIn("autonomy defect", startup)


if __name__ == "__main__":
    unittest.main()
