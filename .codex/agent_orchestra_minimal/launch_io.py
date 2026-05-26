from __future__ import annotations

import json
import os
import shlex
import shutil
from pathlib import Path

from .codex_config import codex_config


RUNTIME_FILES = (
    "agent_state.py",
    "candidate_ledger.py",
    "cli.py",
    "codex_config.py",
    "doctor.py",
    "launch_args.py",
    "launch_io.py",
    "launch_material.py",
    "launch_startup.py",
    "operating_identity.py",
    "prepare_agent_launch.py",
    "task_file.py",
    "tmux_targets.py",
    "tmux_delivery.py",
    "rekick.py",
    "tmux_send.py",
    "tmux_wake.py",
)
RUNTIME_DIRS = ("agent_templates",)
SKILLS = (
    "agent-orchestra-launch",
    "agent-orchestra-task-file",
    "agent-orchestra-team",
    "agent-orchestra-tmux-common",
    "agent-orchestra-tmux-main",
)


def install_codex_material(codex_home: Path, workspace: Path, config_path: Path) -> None:
    project_codex = Path(__file__).resolve().parents[1]
    hooks_dir = codex_home / "hooks"
    skills_dir = codex_home / "skills"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    skills_dir.mkdir(parents=True, exist_ok=True)

    hook_source = project_codex / "hooks" / "agent_orchestra_stop_hook.py"
    hook_target = hooks_dir / "agent_orchestra_stop_hook.py"
    shutil.copy2(hook_source, hook_target)
    hook_target.chmod(0o755)

    for skill in SKILLS:
        _copy_tree(project_codex / "skills" / skill, skills_dir / skill)

    runtime_source = project_codex / "agent_orchestra_minimal"
    runtime_target = codex_home / "agent_orchestra_minimal"
    if runtime_target.exists():
        shutil.rmtree(runtime_target)
    runtime_target.mkdir(parents=True)
    for filename in RUNTIME_FILES:
        shutil.copy2(runtime_source / filename, runtime_target / filename)
    for dirname in RUNTIME_DIRS:
        shutil.copytree(runtime_source / dirname, runtime_target / dirname)

    config_path.write_text(codex_config(workspace, config_path), encoding="utf-8")


def install_auth_material(codex_home: Path, auth_source: str | Path | None) -> None:
    candidates = [Path(auth_source).expanduser()] if auth_source else []
    if current_codex_home := os.environ.get("CODEX_HOME"):
        candidates.append(Path(current_codex_home).expanduser() / "auth.json")
    candidates.append(Path.home() / ".codex" / "auth.json")
    source = next((path for path in candidates if path.is_file()), candidates[0])
    if not source.is_file():
        return
    target = codex_home / "auth.json"
    shutil.copy2(source, target)
    target.chmod(0o600)


def ensure_target_link(link_path: Path, target: Path) -> None:
    if link_path.is_symlink():
        if link_path.resolve() == target:
            return
        link_path.unlink()
    elif link_path.exists():
        raise FileExistsError(f"target_project path exists and is not a symlink: {link_path}")
    link_path.parent.mkdir(parents=True, exist_ok=True)
    os.symlink(target, link_path, target_is_directory=True)


def remove_isolated_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_env_shell(path: Path, env: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Source this file before launching the isolated Codex Agent."]
    lines.extend(f"export {key}={shlex.quote(value)}" for key, value in sorted(env.items()))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _copy_tree(source: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)
