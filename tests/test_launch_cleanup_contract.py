from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.launch_material import prepare_launch_material  # noqa: E402


class LaunchCleanupContractTests(unittest.TestCase):
    def test_partial_launch_material_without_marker_files_is_cleaned(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            target = root / "target"
            target.mkdir()
            agent_dir = root / "run" / "agents" / "pro-partial"
            for dirname in ("home", "codex_home", "workspace"):
                stale = agent_dir / dirname / "stale"
                stale.parent.mkdir(parents=True)
                stale.write_text("stale\n", encoding="utf-8")

            material = prepare_launch_material(
                run_dir=root / "run",
                agent_id="pro-partial",
                agent_kind="ProfessionalAgent",
                target_project=target,
                instruction_text="Fresh instruction.",
            )

            self.assertFalse((material.home / "stale").exists())
            self.assertFalse((material.codex_home / "stale").exists())
            self.assertFalse((material.workspace / "stale").exists())

    def test_target_project_link_collision_is_removed_with_stale_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            target = root / "target"
            target.mkdir()
            collision = root / "run" / "agents" / "main" / "workspace" / "target_project"
            collision.mkdir(parents=True)

            material = prepare_launch_material(
                run_dir=root / "run",
                agent_id="main",
                agent_kind="MainAgent",
                target_project=target,
                instruction_text="Instruction.",
            )

            self.assertTrue((material.workspace / "target_project").is_symlink())
            self.assertEqual((material.workspace / "target_project").resolve(), target.resolve())


if __name__ == "__main__":
    unittest.main()
