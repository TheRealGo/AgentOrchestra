from __future__ import annotations
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .agent_state import KNOWN_STATES, AgentState
from .launch_args import editable_access_roots, launch_access_roots, main_tmux_pane, optional_tmux_pane, validate_codex_args
from .launch_env import build_launch_command, build_launch_env
from .launch_io import PRIVATE_DIR_MODE, PRIVATE_FILE_MODE, ensure_target_link, install_auth_material, install_codex_material, remove_isolated_path, validate_auth_source, write_env_shell, write_json
from .launch_startup import agents_md, startup_text
from .task_file import SharedTaskFile
from .tmux_delivery import normalize_submit_key
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
    cache_dir: Path
    artifact_dir: Path
    environment_dir: Path
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
    initial_task_status: str = "done",
) -> LaunchMaterial:
    _validate_id(agent_id)
    kind = _normalize_kind(agent_kind)
    target_root = Path(target_project).expanduser().resolve(strict=True)
    if not target_root.is_dir():
        raise NotADirectoryError(target_root)
    editable_roots = editable_access_roots(target_root)
    edit_root = editable_roots[-1]
    access_roots = launch_access_roots(target_root, editable_roots)
    assigned_text = startup_text(instruction_text, instruction_source)
    run_root = Path(run_dir).expanduser().resolve()
    agent_dir = run_root / "agents" / agent_id
    workspace, home, codex_home = agent_dir / "workspace", agent_dir / "home", agent_dir / "codex_home"
    state_file, env_path, env_shell_path, command_path = agent_dir / "state.json", agent_dir / "env.json", agent_dir / "env.sh", agent_dir / "command.json"
    config_path = codex_home / "config.toml"
    cache_dir, artifact_dir, environment_dir = agent_dir / "cache", agent_dir / "artifacts", agent_dir / "env"
    shared_task = Path(task_file).expanduser().resolve() if task_file else run_root / "tasks.ini"
    normalized_tmux_pane = optional_tmux_pane(tmux_pane)
    submit_key = normalize_submit_key(os.environ.get("AGENT_ORCHESTRA_TUI_SUBMIT_KEY"))
    extra_codex_args = validate_codex_args(codex_args)
    validate_auth_source(auth_source)
    if _is_relative_to(workspace, target_root):
        raise ValueError(
            "isolated workspace must not be inside target_project; use a run_dir "
            "outside the target tree so target root AGENTS.md cannot become a startup instruction"
        )
    _reject_parent_agents_md(workspace)
    for directory in (run_root, agent_dir):
        directory.mkdir(parents=True, exist_ok=True)
        directory.chmod(PRIVATE_DIR_MODE)
    for isolated_dir in (workspace, home, codex_home):
        remove_isolated_path(isolated_dir)
    for directory in (workspace, home, codex_home):
        directory.mkdir(parents=True, exist_ok=True)
        directory.chmod(PRIVATE_DIR_MODE)
    for directory in (cache_dir, artifact_dir, environment_dir):
        remove_isolated_path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        directory.chmod(PRIVATE_DIR_MODE)
    ensure_target_link(workspace / "target_project", target_root)
    SharedTaskFile.initialize(shared_task, status=initial_task_status)
    AgentState(
        agent_id=agent_id,
        agent_kind=kind,
        state=_normalize_initial_state(initial_state),
        tmux_target=normalized_tmux_pane,
    ).write(state_file)
    startup_agents = workspace / "AGENTS.md"
    startup_agents.write_text(
        agents_md(
            agent_id=agent_id,
            agent_kind=kind,
            lead_layer=lead_layer,
            target_project=target_root,
            access_roots=access_roots,
            task_file=shared_task,
            state_file=state_file,
            cache_dir=cache_dir,
            artifact_dir=artifact_dir,
            environment_dir=environment_dir,
            assigned_text=assigned_text,
        ),
        encoding="utf-8",
    )
    startup_agents.chmod(PRIVATE_FILE_MODE)
    install_codex_material(codex_home, workspace, config_path)
    install_auth_material(codex_home, auth_source)
    main_pane = main_tmux_pane(kind, normalized_tmux_pane)
    env = build_launch_env(
        home=home, codex_home=codex_home, agent_id=agent_id, agent_kind=kind,
        agent_dir=agent_dir, run_root=run_root, task_file=shared_task,
        state_file=state_file, target_root=target_root, access_roots=access_roots,
        edit_root=edit_root,
        cache_dir=cache_dir, artifact_dir=artifact_dir, environment_dir=environment_dir,
        mcp_source_config=config_path, submit_key=submit_key,
        tmux_pane=normalized_tmux_pane, main_pane=main_pane,
    )
    command = build_launch_command(
        codex_binary=codex_binary, workspace=workspace, run_root=run_root, target_root=target_root,
        access_roots=access_roots, extra_args=extra_codex_args, env_path=env_path,
        env_shell_path=env_shell_path, config_path=config_path,
    )
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
        cache_dir=cache_dir,
        artifact_dir=artifact_dir,
        environment_dir=environment_dir,
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


def _reject_parent_agents_md(workspace: Path) -> None:
    for parent in workspace.resolve().parents:
        if (parent / "AGENTS.md").exists():
            raise ValueError("isolated workspace must not have an ancestor AGENTS.md")
