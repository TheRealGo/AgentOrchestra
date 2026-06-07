from __future__ import annotations

from collections.abc import Sequence
from functools import lru_cache
import os
from pathlib import Path
import subprocess

from .codex_features import run_codex_features_list
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
FORBIDDEN_CONFIG_FRAGMENTS = (
    "sandbox",
    "hook",
    "approval",
    "cd",
    "add-dir",
    "profile",
    "default-permissions",
    "permissions.",
)


def validate_codex_args(args: Sequence[str]) -> tuple[str, ...]:
    """Accept only option-shaped Codex argv extensions, never initial tasks."""

    result = tuple(args)
    expect_value_for: str | None = None
    for arg in result:
        if arg == "--" or _is_forbidden_boundary_arg(arg):
            raise ValueError(f"codex_args must not override runtime boundary option {arg!r}")
        assigned_option, assigned_value = _option_assignment(arg)
        if assigned_option:
            if assigned_value == "" or assigned_value.startswith("-"):
                raise ValueError(f"codex_args must not pass runtime boundary option as a value {arg!r}")
            if assigned_option == "-c" and _is_boundary_config(assigned_value):
                raise ValueError(f"codex_args must not override runtime boundary config {arg!r}")
            continue
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


def _option_assignment(arg: str) -> tuple[str | None, str | None]:
    option, separator, value = arg.partition("=")
    if separator and option in CODEX_OPTIONS_WITH_VALUES:
        return option, value
    return None, None


def _is_forbidden_boundary_arg(arg: str) -> bool:
    if arg in FORBIDDEN_CODEX_ARGS:
        return True
    option, separator, _value = arg.partition("=")
    return bool(separator and option in FORBIDDEN_CODEX_ARGS)


def codex_launch_argv(
    codex_binary: str,
    *,
    workspace: str,
    target_project: str,
    access_roots: Sequence[str] = (),
    extra_args: Sequence[str] = (),
    auto_enable_prevent_idle_sleep: bool | None = None,
) -> list[str]:
    enable_prevent_idle_sleep = (
        codex_supports_prevent_idle_sleep(codex_binary)
        if auto_enable_prevent_idle_sleep is None
        else auto_enable_prevent_idle_sleep
    )
    argv = [
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
    ]
    if enable_prevent_idle_sleep:
        argv.extend(["--enable", "prevent_idle_sleep"])
    for root in access_roots:
        if root != target_project:
            argv.extend(["--add-dir", root])
    argv.extend(extra_args)
    return argv


def codex_supports_prevent_idle_sleep(codex_binary: str = "codex") -> bool:
    if os.environ.get("AGENT_ORCHESTRA_DISABLE_PREVENT_IDLE_SLEEP") == "1":
        return False
    return _codex_supports_prevent_idle_sleep(codex_binary)


@lru_cache(maxsize=8)
def _codex_supports_prevent_idle_sleep(codex_binary: str) -> bool:
    report = run_codex_features_list(codex_binary=codex_binary)
    return not report.failed and report.has_feature("prevent_idle_sleep")


def editable_access_roots(target_root: Path) -> tuple[Path, ...]:
    roots = [target_root]
    git_root = git_worktree_root(target_root)
    if git_root and git_root != target_root:
        roots.append(git_root)
    return tuple(roots)


def git_worktree_root(path: Path) -> Path | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    root_text = result.stdout.strip()
    if not root_text:
        return None
    root = Path(root_text).expanduser().resolve()
    return root if root.is_dir() else None


def _is_boundary_config(value: str) -> bool:
    normalized = value.lower().replace("_", "-")
    return any(fragment in normalized for fragment in FORBIDDEN_CONFIG_FRAGMENTS)


def main_tmux_pane(agent_kind: str, tmux_pane: str | None) -> str | None:
    if agent_kind == "MainAgent":
        return optional_tmux_pane(tmux_pane)
    return optional_tmux_pane(os.environ.get("AGENT_ORCHESTRA_MAIN_TMUX_PANE"))
