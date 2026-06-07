from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from typing import Any


TRACKED_FEATURES = (
    "hooks",
    "multi_agent",
    "unified_exec",
    "shell_snapshot",
    "prevent_idle_sleep",
)
FEATURE_LIST_TIMEOUT_SECONDS = 5.0
ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")


@dataclass(frozen=True)
class CodexFeatureReport:
    failed: bool
    features: dict[str, str]
    lines: list[str]

    def has_feature(self, name: str) -> bool:
        return self.features.get(name) not in {None, "absent"}


def run_codex_features_list(
    *,
    codex_binary: str = "codex",
    timeout_seconds: float = FEATURE_LIST_TIMEOUT_SECONDS,
    runner: Any = subprocess.run,
) -> CodexFeatureReport:
    try:
        result = runner(
            [codex_binary, "features", "list"],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return CodexFeatureReport(
            failed=True,
            features={},
            lines=[f"Codex features list timed out after {timeout_seconds:g}s"],
        )
    except OSError as exc:
        return CodexFeatureReport(
            failed=True,
            features={},
            lines=[f"Codex features list could not run: {exc}"],
        )

    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    if result.returncode != 0:
        detail = f": {stderr}" if stderr else ""
        return CodexFeatureReport(
            failed=True,
            features={},
            lines=[f"Codex features list exited {result.returncode}{detail}"],
        )
    if not stdout:
        detail = f": {stderr}" if stderr else ""
        return CodexFeatureReport(
            failed=True,
            features={},
            lines=[f"Codex features list returned no output{detail}"],
        )
    return summarize_codex_features(stdout)


def summarize_codex_features(output: str) -> CodexFeatureReport:
    features = parse_codex_features_list(output)
    lines = [
        "Codex features "
        + ", ".join(f"{name}={features.get(name, 'absent')}" for name in TRACKED_FEATURES)
    ]
    return CodexFeatureReport(failed=False, features=features, lines=lines)


def parse_codex_features_list(output: str) -> dict[str, str]:
    features = {name: "absent" for name in TRACKED_FEATURES}
    for raw_line in output.splitlines():
        line = ANSI_ESCAPE.sub("", raw_line).strip()
        if not line:
            continue
        normalized = line.lower().replace("-", "_")
        for feature in TRACKED_FEATURES:
            if not _contains_feature_name(normalized, feature):
                continue
            features[feature] = _feature_state(normalized)
    return features


def _contains_feature_name(line: str, feature: str) -> bool:
    return re.search(rf"(^|[^a-z0-9_]){re.escape(feature)}([^a-z0-9_]|$)", line) is not None


def _feature_state(line: str) -> str:
    words = set(re.findall(r"[a-z0-9_]+", line))
    if words & {"absent", "missing", "unavailable", "unsupported", "unknown"}:
        return "absent"
    if "not" in words and words & {"available", "found", "recognized", "supported"}:
        return "absent"
    if words & {"disabled", "disable", "off", "false", "no"}:
        return "disabled"
    if words & {"enabled", "enable", "on", "true", "yes"}:
        return "enabled"
    if words & {"experimental", "available", "stable"}:
        return "available"
    return "present"
