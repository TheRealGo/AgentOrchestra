from __future__ import annotations
import os
import re
import sys
from pathlib import Path
from typing import Sequence

from .agent_state import KNOWN_STATES, AgentState
from .claude_settings import DEFAULT_PERMISSION_MODE
from .launch_args import claude_launch_argv, forwarded_auth_env, main_tmux_pane, optional_tmux_pane, validate_claude_args
from .launch_io import LaunchMaterial, ensure_target_link, install_claude_auth, install_claude_material, remove_isolated_path, write_env_shell, write_json
from .launch_startup import claude_md, startup_text
from .task_file import SharedTaskFile
from .tmux_delivery import normalize_submit_key

SAFE_ID = re.compile(r"^[A-Za-z0-9_.-]+$")


def prepare_launch_material(
    *,
    run_dir: str | Path,
    agent_id: str,
    agent_kind: str,
    target_project: str | Path,
    instruction_text: str | None = None,
    instruction_source: str | Path | None = None,
    lead_layer: str | None = None,
    task_file: str | Path | None = None,
    initial_state: str = "working",
    tmux_pane: str | None = None,
    auth_source: str | Path | None = None,
    claude_binary: str = "claude",
    claude_args: Sequence[str] = (),
    permission_mode: str | None = None,
) -> LaunchMaterial:
    _validate_id(agent_id)
    kind = _normalize_kind(agent_kind)
    target_root = Path(target_project).expanduser().resolve(strict=True)
    if not target_root.is_dir():
        raise NotADirectoryError(target_root)
    assigned_text = startup_text(instruction_text, instruction_source)
    run_root = Path(run_dir).expanduser().resolve()
    agent_dir = run_root / "agents" / agent_id
    workspace = agent_dir / "workspace"
    home = agent_dir / "home"
    claude_config_dir = agent_dir / "claude_home"
    state_file = agent_dir / "state.json"
    env_path = agent_dir / "env.json"
    env_shell_path = agent_dir / "env.sh"
    command_path = agent_dir / "command.json"
    settings_path = claude_config_dir / "settings.json"
    shared_task = Path(task_file).expanduser().resolve() if task_file else run_root / "tasks.ini"
    normalized_tmux_pane = optional_tmux_pane(tmux_pane)
    resolved_permission_mode = _resolve_permission_mode(permission_mode)

    if _is_relative_to(workspace, target_root):
        raise ValueError(
            "isolated workspace must not be inside target_project; use a run_dir "
            "outside the target tree so target root CLAUDE.md cannot become a startup instruction"
        )
    _reject_parent_claude_md(workspace)

    for isolated_dir in (workspace, home, claude_config_dir):
        remove_isolated_path(isolated_dir)
    for directory in (workspace, home, claude_config_dir, agent_dir):
        directory.mkdir(parents=True, exist_ok=True)
    ensure_target_link(workspace / "target_project", target_root)
    SharedTaskFile.initialize(shared_task)
    AgentState(
        agent_id=agent_id,
        agent_kind=kind,
        state=_normalize_initial_state(initial_state),
        tmux_target=normalized_tmux_pane,
    ).write(state_file)

    startup_claude_md = workspace / "CLAUDE.md"
    startup_claude_md.write_text(
        claude_md(
            agent_id=agent_id,
            agent_kind=kind,
            lead_layer=lead_layer,
            target_project=target_root,
            task_file=shared_task,
            state_file=state_file,
            assigned_text=assigned_text,
        ),
        encoding="utf-8",
    )
    install_claude_material(
        claude_config_dir, home, workspace, settings_path,
        permission_mode=resolved_permission_mode,
    )
    install_claude_auth(claude_config_dir, auth_source)

    submit_key = normalize_submit_key(os.environ.get("AGENT_ORCHESTRA_TUI_SUBMIT_KEY"))
    main_pane = main_tmux_pane(kind, normalized_tmux_pane)
    extra_claude_args = validate_claude_args(claude_args)
    env = {
        "HOME": str(home),
        "CLAUDE_CONFIG_DIR": str(claude_config_dir),
        "PYTHONPATH": str(claude_config_dir),
        "AGENT_ORCHESTRA_AGENT_ID": agent_id,
        "AGENT_ORCHESTRA_AGENT_KIND": kind,
        "AGENT_ORCHESTRA_AGENT_DIR": str(agent_dir),
        "AGENT_ORCHESTRA_RUN_DIR": str(run_root),
        "AGENT_ORCHESTRA_TASK_FILE": str(shared_task),
        "AGENT_ORCHESTRA_AGENT_STATE": str(state_file),
        "AGENT_ORCHESTRA_TARGET_PROJECT": str(target_root),
        "AGENT_ORCHESTRA_PYTHON": sys.executable,
        "AGENT_ORCHESTRA_TUI_SUBMIT_KEY": submit_key,
        "AGENT_ORCHESTRA_PERMISSION_MODE": resolved_permission_mode,
    }
    if protocol_root := os.environ.get("AGENT_ORCHESTRA_REPO_ROOT"):
        env["AGENT_ORCHESTRA_REPO_ROOT"] = str(Path(protocol_root).expanduser().resolve())
    if normalized_tmux_pane:
        env["AGENT_ORCHESTRA_TMUX_PANE"] = normalized_tmux_pane
    if main_pane:
        env["AGENT_ORCHESTRA_MAIN_TMUX_PANE"] = main_pane
    for auth_var, auth_value in forwarded_auth_env().items():
        env[auth_var] = auth_value
    argv = claude_launch_argv(
        claude_binary, target_project=str(target_root), run_dir=str(run_root),
        permission_mode=resolved_permission_mode, extra_args=extra_claude_args,
    )
    command = {
        "argv": argv,
        "cwd": str(workspace),
        "env_file": str(env_path),
        "env_shell_file": str(env_shell_path),
        "settings": str(settings_path),
        "permission_mode": resolved_permission_mode,
        "does_not_launch": True,
    }
    write_json(env_path, env)
    write_env_shell(env_shell_path, env)
    # env.json / env.sh may carry forwarded auth credentials; keep them private.
    env_path.chmod(0o600)
    env_shell_path.chmod(0o600)
    write_json(command_path, command)

    return LaunchMaterial(
        agent_id=agent_id,
        agent_kind=kind,
        run_dir=run_root,
        workspace=workspace,
        home=home,
        claude_config_dir=claude_config_dir,
        startup_claude_md=startup_claude_md,
        task_file=shared_task,
        state_file=state_file,
        env_path=env_path,
        env_shell_path=env_shell_path,
        command_path=command_path,
        settings_path=settings_path,
        env=env,
        command=command,
    )


def _validate_id(agent_id: str) -> None:
    if not SAFE_ID.fullmatch(agent_id):
        raise ValueError(f"agent_id must match {SAFE_ID.pattern}")


def _normalize_kind(agent_kind: str) -> str:
    normalized = agent_kind.strip().lower()
    if normalized in {"main", "mainagent", "main_agent"}:
        return "MainAgent"
    if normalized in {"professional", "professionalagent", "professional_agent"}:
        return "ProfessionalAgent"
    raise ValueError("agent_kind must be MainAgent or ProfessionalAgent")


def _normalize_initial_state(state: str) -> str:
    normalized = state.strip().lower() or "working"
    if normalized not in KNOWN_STATES:
        raise ValueError(f"invalid initial state {normalized!r}")
    return normalized


def _resolve_permission_mode(permission_mode: str | None) -> str:
    candidate = permission_mode or os.environ.get("AGENT_ORCHESTRA_PERMISSION_MODE") or ""
    candidate = candidate.strip()
    return candidate or DEFAULT_PERMISSION_MODE


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def _reject_parent_claude_md(workspace: Path) -> None:
    for parent in workspace.resolve().parents:
        if (parent / "CLAUDE.md").exists():
            raise ValueError("isolated workspace must not have an ancestor CLAUDE.md")
