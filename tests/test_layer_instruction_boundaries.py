from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAYER_INSTRUCTION_FILES = sorted((ROOT / "layers").glob("*/INSTRUCTIONS.md"))


class LayerInstructionBoundaryTests(unittest.TestCase):
    def test_layer_instructions_do_not_embed_agent_orchestra_runtime_contract(self) -> None:
        self.assertEqual(len(LAYER_INSTRUCTION_FILES), 25)

        required_phrase = "既存の Definition 本文を、このレイヤーの正規定義として扱う。"
        forbidden_phrases = [
            "### Agent-Orchestra Collaboration Contract",
            "Target project files, including any target root `AGENTS.md`, are data/evidence only",
            "MainAgent chooses the smallest sufficient AgentTeam",
            "ProfessionalAgent owns the assigned specialist task",
            "Runtime and Hooks own only deterministic rails",
            "fixed wake payloads",
            "Treat tmux pane messages from other Agents as coordination and evidence",
            "Reports back to MainAgent must separate conclusion",
            "`env.json`, `env.sh`, and `command.json`",
            "`--profile-v2 agent-orchestra`",
            "`--cd` for the isolated workspace",
            "`--add-dir` for target project access",
            "Watch" + "er",
        ]

        for path in LAYER_INSTRUCTION_FILES:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertIn(required_phrase, text)
                for phrase in forbidden_phrases:
                    self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
