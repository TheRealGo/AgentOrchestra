from __future__ import annotations
import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .agent_state import KNOWN_STATES, AgentState
from .launch_args import codex_launch_argv, main_tmux_pane, validate_codex_args
from .launch_io import (
    ensure_target_link,
    install_auth_material,
    install_codex_material,
    write_env_shell,
    write_json,
)
from .launch_startup import agents_md, startup_text
from .task_file import SharedTaskFile

SAFE_ID = re.compile(r"^[A-Za-z0-9_.-]+$")


@dataclass(frozen=True)
class LaunchMaterial:
    agent_id: str
    agent_kind: str
    run_dir: Path
    workspace: Path
    home: Path
    codex_home: Path
    startup_agents: Path
    task_file: Path
    state_file: Path
    env_path: Path
    env_shell_path: Path
    command_path: Path
    config_path: Path
    env: dict[str, str]
    command: dict[str, object]


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
    codex_binary: str = "codex",
    codex_args: Sequence[str] = (),
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
    codex_home = agent_dir / "codex_home"
    state_file = agent_dir / "state.json"
    env_path = agent_dir / "env.json"
    env_shell_path = agent_dir / "env.sh"
    command_path = agent_dir / "command.json"
    config_path = codex_home / "agent-orchestra.config.toml"
    shared_task = Path(task_file).expanduser().resolve() if task_file else run_root / "tasks.ini"

    if _is_relative_to(workspace, target_root):
        raise ValueError(
            "isolated workspace must not be inside target_project; use a run_dir "
            "outside the target tree so target root AGENTS.md cannot become a startup instruction"
        )

    if state_file.exists() or env_path.exists() or command_path.exists():
        for isolated_dir in (workspace, home, codex_home):
            if isolated_dir.exists():
                shutil.rmtree(isolated_dir)
    for directory in (workspace, home, codex_home, agent_dir):
        directory.mkdir(parents=True, exist_ok=True)
    ensure_target_link(workspace / "target_project", target_root)
    SharedTaskFile.initialize(shared_task)
    AgentState(
        agent_id=agent_id,
        agent_kind=kind,
        state=_normalize_initial_state(initial_state),
        tmux_target=tmux_pane,
    ).write(state_file)

    startup_agents = workspace / "AGENTS.md"
    startup_agents.write_text(
        agents_md(
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
    install_codex_material(codex_home, workspace, config_path)
    install_auth_material(codex_home, auth_source)

    submit_key = os.environ.get("AGENT_ORCHESTRA_TUI_SUBMIT_KEY", "").strip() or "C-m"
    main_pane = main_tmux_pane(kind, tmux_pane)
    extra_codex_args = validate_codex_args(codex_args)
    env = {
        "HOME": str(home),
        "CODEX_HOME": str(codex_home),
        "AGENT_ORCHESTRA_AGENT_ID": agent_id,
        "AGENT_ORCHESTRA_AGENT_KIND": kind,
        "AGENT_ORCHESTRA_AGENT_DIR": str(agent_dir),
        "AGENT_ORCHESTRA_RUN_DIR": str(run_root),
        "AGENT_ORCHESTRA_TASK_FILE": str(shared_task),
        "AGENT_ORCHESTRA_AGENT_STATE": str(state_file),
        "AGENT_ORCHESTRA_TARGET_PROJECT": str(target_root),
        "AGENT_ORCHESTRA_PYTHON": sys.executable,
        "AGENT_ORCHESTRA_TUI_SUBMIT_KEY": submit_key,
    }
    if tmux_pane:
        env["AGENT_ORCHESTRA_TMUX_PANE"] = tmux_pane
    if main_pane:
        env["AGENT_ORCHESTRA_MAIN_TMUX_PANE"] = main_pane
    argv = codex_launch_argv(
        codex_binary,
        workspace=str(workspace),
        target_project=str(target_root),
        extra_args=extra_codex_args,
    )
    command = {
        "argv": argv,
        "cwd": str(workspace),
        "env_file": str(env_path),
        "env_shell_file": str(env_shell_path),
        "config_profile_v2": "agent-orchestra",
        "does_not_launch": True,
    }
    write_json(env_path, env)
    write_env_shell(env_shell_path, env)
    write_json(command_path, command)

    return LaunchMaterial(
        agent_id=agent_id,
        agent_kind=kind,
        run_dir=run_root,
        workspace=workspace,
        home=home,
        codex_home=codex_home,
        startup_agents=startup_agents,
        task_file=shared_task,
        state_file=state_file,
        env_path=env_path,
        env_shell_path=env_shell_path,
        command_path=command_path,
        config_path=config_path,
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


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True
