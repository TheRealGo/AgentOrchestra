from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal.codex_features import parse_codex_features_list, summarize_codex_features  # noqa: E402


class CodexFeaturesContractTests(unittest.TestCase):
    def test_parser_summarizes_0137_feature_list(self) -> None:
        output = """
Feature              Status
hooks                enabled
multi_agent          disabled
unified_exec         enabled
shell_snapshot       disabled
prevent_idle_sleep   disabled
"""
        features = parse_codex_features_list(output)
        report = summarize_codex_features(output)

        self.assertEqual(features["hooks"], "enabled")
        self.assertEqual(features["multi_agent"], "disabled")
        self.assertEqual(features["unified_exec"], "enabled")
        self.assertEqual(features["shell_snapshot"], "disabled")
        self.assertEqual(features["prevent_idle_sleep"], "disabled")
        self.assertEqual(
            report.lines,
            [
                "Codex features hooks=enabled, multi_agent=disabled, "
                "unified_exec=enabled, shell_snapshot=disabled, prevent_idle_sleep=disabled"
            ],
        )

    def test_parser_prefers_disabled_over_enable_hint(self) -> None:
        output = "prevent_idle_sleep disabled; use --enable prevent_idle_sleep to opt in"

        features = parse_codex_features_list(output)

        self.assertEqual(features["prevent_idle_sleep"], "disabled")

    def test_parser_treats_explicit_unsupported_feature_as_absent(self) -> None:
        outputs = (
            "prevent_idle_sleep is not supported by this Codex build",
            "prevent_idle_sleep unavailable",
            "unknown feature prevent_idle_sleep",
        )

        for output in outputs:
            with self.subTest(output=output):
                features = parse_codex_features_list(output)

                self.assertEqual(features["prevent_idle_sleep"], "absent")


if __name__ == "__main__":
    unittest.main()
