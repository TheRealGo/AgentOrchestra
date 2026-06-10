from __future__ import annotations

from collections.abc import Sequence
import os

from .claude_settings import DEFAULT_PERMISSION_MODE
from .tmux_targets import optional_tmux_pane


CLAUDE_OPTIONS_WITH_VALUES = frozenset(
    {
        "--model",
        "--fallback-model",
    }
)
CLAUDE_FLAGS_WITHOUT_VALUES = frozenset(
    {
        "--verbose",
    }
)
FORBIDDEN_CLAUDE_ARGS = frozenset(
    {
        "--add-dir",
        "--permission-mode",
        "--dangerously-skip-permissions",
        "--allow-dangerously-skip-permissions",
        "--settings",
        "--setting-sources",
        "--system-prompt",
        "--append-system-prompt",
        "--agents",
        "-p",
        "--print",
        "--cd",
    }
)
# Non-interactive one-shot modes do not fit the continuous consult/wake/review
# model, the same way Codex's `codex exec` did not.
FORBIDDEN_FIRST_TOKENS = frozenset({"-p", "--print"})
# Auth credentials Claude Code reads from the environment. Forwarding them into
# the isolated Agent environment (and env.sh, which ProfessionalAgent panes
# source) lets one exported token authenticate MainAgent and every
# ProfessionalAgent, because an isolated CLAUDE_CONFIG_DIR does not inherit the
# macOS Keychain login.
AUTH_ENV_VARS = (
    "CLAUDE_CODE_OAUTH_TOKEN",
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_BASE_URL",
)


def forwarded_auth_env() -> dict[str, str]:
    """Auth env vars present in the launching environment, to pass to the Agent."""

    return {name: os.environ[name] for name in AUTH_ENV_VARS if os.environ.get(name)}


def validate_claude_args(args: Sequence[str]) -> tuple[str, ...]:
    """Accept only option-shaped Claude CLI argv extensions, never initial tasks."""

    result = tuple(args)
    if result and result[0] in FORBIDDEN_FIRST_TOKENS:
        raise ValueError("claude_args must not request non-interactive print mode")
    expect_value_for: str | None = None
    for arg in result:
        if arg == "--" or arg in FORBIDDEN_CLAUDE_ARGS:
            raise ValueError(f"claude_args must not override runtime boundary option {arg!r}")
        if expect_value_for:
            if arg == "--" or arg.startswith("-"):
                raise ValueError(f"claude_args must not pass runtime boundary option as a value {arg!r}")
            expect_value_for = None
            continue
        if arg in CLAUDE_OPTIONS_WITH_VALUES:
            expect_value_for = arg
            continue
        if arg in CLAUDE_FLAGS_WITHOUT_VALUES:
            continue
        raise ValueError(f"claude_args must be option-shaped; unexpected positional arg {arg!r}")
    if expect_value_for:
        raise ValueError(f"claude_args missing value for {expect_value_for}")
    return result


def claude_launch_argv(
    claude_binary: str,
    *,
    target_project: str,
    run_dir: str | None = None,
    permission_mode: str = DEFAULT_PERMISSION_MODE,
    extra_args: Sequence[str] = (),
) -> list[str]:
    """Build the Claude Code launch argv.

    Claude Code launches in the current working directory, so isolation comes
    from chdir into the generated workspace rather than a ``--cd`` flag. The
    isolated ``CLAUDE_CONFIG_DIR`` carries the generated ``settings.json`` Stop
    Hook and project trust, which replaces Codex's ``--profile-v2``.

    ``run_dir`` is added as a second ``--add-dir`` so the shared ``tasks.ini``
    and per-agent ``state.json`` — which live at the run-dir root, outside the
    workspace — are readable and editable without a per-file permission prompt
    that would stall an unattended run. This does not break instruction
    isolation: verified live that a nested ``CLAUDE.md`` under an added
    directory is not loaded as startup instruction (only the cwd workspace
    ``CLAUDE.md`` is), and ``_reject_parent_claude_md`` still guards cwd
    ancestors.
    """

    argv = [claude_binary, "--add-dir", target_project]
    if run_dir:
        argv += ["--add-dir", run_dir]
    argv += ["--permission-mode", permission_mode, *extra_args]
    return argv


def main_tmux_pane(agent_kind: str, tmux_pane: str | None) -> str | None:
    if agent_kind == "MainAgent":
        return optional_tmux_pane(tmux_pane)
    return optional_tmux_pane(os.environ.get("AGENT_ORCHESTRA_MAIN_TMUX_PANE"))
