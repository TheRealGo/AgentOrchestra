from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Sequence

from .codex_config import inspect_mcp_inheritance
from .launch_args import codex_approval_policy_for_target, codex_launch_argv


def build_launch_env(
    *,
    home: Path,
    codex_home: Path,
    agent_id: str,
    agent_kind: str,
    agent_dir: Path,
    run_root: Path,
    task_file: Path,
    state_file: Path,
    target_root: Path,
    access_roots: tuple[Path, ...],
    edit_root: Path,
    cache_dir: Path,
    artifact_dir: Path,
    environment_dir: Path,
    mcp_source_config: Path,
    submit_key: str,
    tmux_pane: str | None,
    main_pane: str | None,
) -> dict[str, str]:
    env = {
        "HOME": str(home),
        "CODEX_HOME": str(codex_home),
        "PATH": os.environ.get("PATH", os.defpath),
        "PYTHONPATH": str(codex_home),
        "AGENT_ORCHESTRA_AGENT_ID": agent_id,
        "AGENT_ORCHESTRA_AGENT_KIND": agent_kind,
        "AGENT_ORCHESTRA_AGENT_DIR": str(agent_dir),
        "AGENT_ORCHESTRA_RUN_DIR": str(run_root),
        "AGENT_ORCHESTRA_RUN_ID": _safe_env_id(run_root.name),
        "AGENT_ORCHESTRA_TASK_FILE": str(task_file),
        "AGENT_ORCHESTRA_AGENT_STATE": str(state_file),
        "AGENT_ORCHESTRA_TARGET_PROJECT": str(target_root),
        "AGENT_ORCHESTRA_ACCESS_ROOTS": os.pathsep.join(str(root) for root in access_roots),
        "AGENT_ORCHESTRA_EDIT_ROOT": str(edit_root),
        "AGENT_ORCHESTRA_CACHE_DIR": str(cache_dir),
        "AGENT_ORCHESTRA_ARTIFACT_DIR": str(artifact_dir),
        "AGENT_ORCHESTRA_ENV_DIR": str(environment_dir),
        "AGENT_ORCHESTRA_SERVER_MANIFEST": str(environment_dir / "server-processes.json"),
        "AGENT_ORCHESTRA_MCP_SOURCE_CONFIG": str(mcp_source_config),
        "AGENT_ORCHESTRA_PYTHON": sys.executable,
        "AGENT_ORCHESTRA_TUI_SUBMIT_KEY": submit_key,
    }
    if protocol_root := os.environ.get("AGENT_ORCHESTRA_REPO_ROOT"):
        env["AGENT_ORCHESTRA_REPO_ROOT"] = str(Path(protocol_root).expanduser().resolve())
    if tmux_pane:
        env["AGENT_ORCHESTRA_TMUX_PANE"] = tmux_pane
    if main_pane:
        env["AGENT_ORCHESTRA_MAIN_TMUX_PANE"] = main_pane
    return env


def build_launch_command(
    *,
    codex_binary: str,
    workspace: Path,
    run_root: Path,
    target_root: Path,
    access_roots: tuple[Path, ...],
    extra_args: Sequence[str],
    env_path: Path,
    env_shell_path: Path,
    config_path: Path,
) -> dict[str, object]:
    mcp = inspect_mcp_inheritance(config_path)
    approval_policy = codex_approval_policy_for_target(target_root)
    argv = codex_launch_argv(
        codex_binary,
        workspace=str(workspace),
        target_project=str(target_root),
        access_roots=tuple(str(root) for root in access_roots),
        runtime_roots=(str(run_root),),
        extra_args=extra_args,
        approval_policy=approval_policy,
    )
    return {
        "argv": argv,
        "cwd": str(workspace),
        "env_file": str(env_path),
        "env_json_file": str(env_path),
        "env_shell_file": str(env_shell_path),
        "runtime_access_roots": [str(run_root)],
        "config_profile": "agent-orchestra",
        "approval_policy": approval_policy,
        "mcp_servers": list(mcp.servers),
        "mcp_inheritance_disabled": not mcp.enabled,
        "does_not_launch": True,
    }


def _safe_env_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-") or "run"
