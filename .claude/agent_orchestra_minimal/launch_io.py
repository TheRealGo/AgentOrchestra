from __future__ import annotations

import json
import os
import shlex
import shutil
from dataclasses import dataclass
from pathlib import Path

from .claude_settings import DEFAULT_PERMISSION_MODE, claude_settings, trust_seed


@dataclass(frozen=True)
class LaunchMaterial:
    agent_id: str
    agent_kind: str
    run_dir: Path
    workspace: Path
    home: Path
    claude_config_dir: Path
    startup_claude_md: Path
    task_file: Path
    state_file: Path
    env_path: Path
    env_shell_path: Path
    command_path: Path
    settings_path: Path
    env: dict[str, str]
    command: dict[str, object]


RUNTIME_FILES = (
    "agent_state.py",
    "candidate_ledger.py",
    "claude_settings.py",
    "cli.py",
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


def install_claude_material(
    claude_config_dir: Path,
    home: Path,
    workspace: Path,
    settings_path: Path,
    *,
    permission_mode: str = DEFAULT_PERMISSION_MODE,
) -> None:
    project_claude = Path(__file__).resolve().parents[1]
    hooks_dir = claude_config_dir / "hooks"
    skills_dir = claude_config_dir / "skills"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    skills_dir.mkdir(parents=True, exist_ok=True)

    hook_source = project_claude / "hooks" / "agent_orchestra_stop_hook.py"
    hook_target = hooks_dir / "agent_orchestra_stop_hook.py"
    shutil.copy2(hook_source, hook_target)
    hook_target.chmod(0o755)

    for skill in SKILLS:
        _copy_tree(project_claude / "skills" / skill, skills_dir / skill)

    runtime_source = project_claude / "agent_orchestra_minimal"
    runtime_target = claude_config_dir / "agent_orchestra_minimal"
    if runtime_target.exists():
        shutil.rmtree(runtime_target)
    runtime_target.mkdir(parents=True)
    for filename in RUNTIME_FILES:
        shutil.copy2(runtime_source / filename, runtime_target / filename)
    for dirname in RUNTIME_DIRS:
        shutil.copytree(runtime_source / dirname, runtime_target / dirname)

    settings_path.write_text(
        claude_settings(hook_target, permission_mode=permission_mode), encoding="utf-8"
    )
    _install_trust_seed(home, claude_config_dir, workspace)


def _install_trust_seed(home: Path, claude_config_dir: Path, workspace: Path) -> None:
    seed = trust_seed(workspace)
    for directory in (home, claude_config_dir):
        directory.mkdir(parents=True, exist_ok=True)
        (directory / ".claude.json").write_text(seed, encoding="utf-8")


def install_claude_auth(claude_config_dir: Path, auth_source: str | Path | None = None) -> None:
    """Copy ``.credentials.json`` when present.

    On macOS, Claude Code reads credentials from the system Keychain, so an
    isolated HOME usually authenticates without copying anything. This best
    effort copy covers file-based credentials (for example on Linux).
    """

    candidates = [Path(auth_source).expanduser()] if auth_source else []
    if current := os.environ.get("CLAUDE_CONFIG_DIR"):
        candidates.append(Path(current).expanduser() / ".credentials.json")
    candidates.append(Path.home() / ".claude" / ".credentials.json")
    source = next((path for path in candidates if path.is_file()), None)
    if source is None:
        return
    target = claude_config_dir / ".credentials.json"
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
    lines = ["# Source this file before launching the isolated Claude Code Agent."]
    lines.extend(f"export {key}={shlex.quote(value)}" for key, value in sorted(env.items()))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _copy_tree(source: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)
