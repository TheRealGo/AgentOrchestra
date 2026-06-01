from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_orchestra_minimal.doctor import doctor_command
from agent_orchestra_minimal.launch_material import LaunchMaterial, prepare_launch_material


MAIN_LAYER_PREFIX = "15_"


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in {"start", "doctor", "-h", "--help"}:
        return start_main(parse_start_args(argv))
    if argv[0] == "start":
        return start_main(parse_start_args(argv[1:]))

    parser = argparse.ArgumentParser(prog="agent-orchestra")
    subparsers = parser.add_subparsers(dest="command", required=True)
    doctor = subparsers.add_parser("doctor", help="check local startup prerequisites")
    doctor.add_argument("--target-project", default=os.getcwd())
    doctor.add_argument(
        "--tui-transport",
        action="store_true",
        help="verify Codex TUI tmux delivery with a disposable /exit probe",
    )
    doctor.add_argument(
        "--codex-doctor",
        action="store_true",
        help="include Codex CLI 0.135+ machine-readable diagnostics",
    )
    doctor.add_argument(
        "--codex-doctor-timeout-seconds",
        type=float,
        default=20.0,
        help="maximum time to wait for codex doctor --json",
    )

    args = parser.parse_args(argv)
    if args.command == "doctor":
        return doctor_command(args)
    parser.error(f"unknown command: {args.command}")
    return 2


def start_main(args: argparse.Namespace) -> int:
    target = Path(args.target_project or args.target_project_arg or os.getcwd()).expanduser().resolve()
    run_dir = Path(args.run_dir).expanduser().resolve() if args.run_dir else default_run_dir()
    tmux_pane = current_tmux_pane()
    if not tmux_pane:
        print(
            "agent-orchestra: warning: not running inside tmux; pane orchestration and hook wake may be limited.",
            file=sys.stderr,
        )

    material = prepare_main_material(
        target_project=target,
        run_dir=run_dir,
        agent_id=args.agent_id,
        tmux_pane=tmux_pane,
    )
    print(f"agent-orchestra: run dir: {material.run_dir}", file=sys.stderr)
    if args.dry_run:
        print_start_material(material)
        return 0

    env = os.environ.copy()
    env.update(material.env)
    os.chdir(material.workspace)
    os.execvpe("codex", material.command["argv"], env)
    return 0


def prepare_main_material(
    *,
    target_project: Path,
    run_dir: Path,
    agent_id: str,
    tmux_pane: str | None,
) -> LaunchMaterial:
    target_project = target_project.expanduser().resolve()
    run_dir = run_dir.expanduser().resolve()
    root = protocol_root()
    os.environ.setdefault("AGENT_ORCHESTRA_REPO_ROOT", str(root))
    layer_source = main_layer_instruction(root)
    if layer_source is None:
        raise FileNotFoundError("agent-orchestra protocol layer 15 INSTRUCTIONS.md was not found")
    return prepare_launch_material(
        run_dir=run_dir,
        agent_id=agent_id,
        agent_kind="MainAgent",
        target_project=target_project,
        instruction_source=layer_source,
        lead_layer=layer_source.parent.name if layer_source else "MainAgent",
        tmux_pane=tmux_pane,
        initial_state="ready",
    )


def parse_start_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="agent-orchestra", usage="agent-orchestra [target-project]")
    if "--" in argv:
        parser.error("initial task arguments are not supported; start codex-o and enter the task in the TUI")
    parser.add_argument("--target-project")
    parser.add_argument("--run-dir")
    parser.add_argument("--agent-id", default="main")
    parser.add_argument("--dry-run", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("target_project_arg", nargs="?")
    return parser.parse_args(argv)


def default_run_dir() -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return Path("/private/tmp/agent-orchestra") / f"{stamp}-agent-orchestra"


def current_tmux_pane() -> str | None:
    if "TMUX" not in os.environ:
        return None
    if pane := pane_from_current_tty():
        return pane
    if pane := os.environ.get("TMUX_PANE"):
        return pane
    return None


def pane_from_current_tty() -> str | None:
    try:
        tty_result = subprocess.run(
            ["tty"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        panes_result = subprocess.run(
            ["tmux", "list-panes", "-a", "-F", "#{pane_id} #{pane_tty}"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return pane_id_from_tty_listing(tty_result.stdout.strip(), panes_result.stdout)


def pane_id_from_tty_listing(current_tty: str, listing: str) -> str | None:
    if not current_tty:
        return None
    for line in listing.splitlines():
        pane, _, pane_tty = line.partition(" ")
        if pane and pane_tty.strip() == current_tty:
            return pane
    return None


def protocol_root() -> Path:
    if root := os.environ.get("AGENT_ORCHESTRA_REPO_ROOT"):
        return Path(root).expanduser().resolve()
    return Path(__file__).resolve().parents[2]


def main_layer_instruction(root: Path) -> Path | None:
    layers_dir = root / "layers"
    if not layers_dir.is_dir():
        return None
    for path in sorted(layers_dir.iterdir()):
        instruction = path / "INSTRUCTIONS.md"
        if path.name.startswith(MAIN_LAYER_PREFIX) and instruction.is_file():
            return instruction
    return None


def print_start_material(material: LaunchMaterial) -> None:
    print(f"run_dir={material.run_dir}")
    print(f"agent_dir={material.state_file.parent}")
    print(f"command_json={material.command_path}")
    print(f"env_json={material.env_path}")
    print(f"env_sh={material.env_shell_path}")
    print(f"workspace={material.workspace}")
    print(f"codex_home={material.codex_home}")


if __name__ == "__main__":
    raise SystemExit(main())
