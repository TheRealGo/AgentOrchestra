from __future__ import annotations

from collections.abc import Sequence
import os

from .tmux_targets import optional_tmux_pane


CODEX_OPTIONS_WITH_VALUES = frozenset(
    {
        "--model",
        "-m",
        "-c",
    }
)
CODEX_FLAGS_WITHOUT_VALUES = frozenset(
    {
        "--no-alt-screen",
    }
)
FORBIDDEN_CODEX_ARGS = frozenset(
    {
        "--profile",
        "--profile-v2",
        "--ask-for-approval",
        "--sandbox",
        "--enable",
        "--cd",
        "--add-dir",
        "--dangerously-bypass-hook-trust",
    }
)
FORBIDDEN_CONFIG_FRAGMENTS = ("sandbox", "hook", "approval", "cd", "add-dir", "profile")


def validate_codex_args(args: Sequence[str]) -> tuple[str, ...]:
    """Accept only option-shaped Codex argv extensions, never initial tasks."""

    result = tuple(args)
    expect_value_for: str | None = None
    for arg in result:
        if arg == "--" or arg in FORBIDDEN_CODEX_ARGS:
            raise ValueError(f"codex_args must not override runtime boundary option {arg!r}")
        if expect_value_for:
            if arg == "exec":
                raise ValueError("codex_args must not request codex exec")
            if arg == "--" or arg.startswith("-"):
                raise ValueError(f"codex_args must not pass runtime boundary option as a value {arg!r}")
            if expect_value_for == "-c" and _is_boundary_config(arg):
                raise ValueError(f"codex_args must not override runtime boundary config {arg!r}")
            expect_value_for = None
            continue
        if arg in CODEX_OPTIONS_WITH_VALUES:
            expect_value_for = arg
            continue
        if arg in CODEX_FLAGS_WITHOUT_VALUES:
            continue
        raise ValueError(f"codex_args must be option-shaped; unexpected positional arg {arg!r}")
    if expect_value_for:
        raise ValueError(f"codex_args missing value for {expect_value_for}")
    if result and result[0] == "exec":
        raise ValueError("codex_args must not request codex exec")
    return result


def codex_launch_argv(
    codex_binary: str,
    *,
    workspace: str,
    target_project: str,
    extra_args: Sequence[str] = (),
) -> list[str]:
    return [
        codex_binary,
        "--profile",
        "agent-orchestra",
        "--ask-for-approval",
        "never",
        "--sandbox",
        "workspace-write",
        "--enable",
        "hooks",
        "-c",
        "sandbox_workspace_write.network_access=true",
        "--cd",
        workspace,
        "--add-dir",
        target_project,
        *extra_args,
    ]


def _is_boundary_config(value: str) -> bool:
    normalized = value.lower().replace("_", "-")
    return any(fragment in normalized for fragment in FORBIDDEN_CONFIG_FRAGMENTS)


def main_tmux_pane(agent_kind: str, tmux_pane: str | None) -> str | None:
    if agent_kind == "MainAgent":
        return optional_tmux_pane(tmux_pane)
    return optional_tmux_pane(os.environ.get("AGENT_ORCHESTRA_MAIN_TMUX_PANE"))
