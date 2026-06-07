from __future__ import annotations

import argparse
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path


if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_orchestra_minimal.launch_material import prepare_launch_material
from agent_orchestra_minimal.codex_config import codex_config
from agent_orchestra_minimal.tmux_delivery import normalize_submit_key


@dataclass(frozen=True)
class ProbeResult:
    ok: bool
    message: str
    capture_tail: str = ""


def run_probe(*, codex_binary: str = "codex", submit_key: str | None = None) -> ProbeResult:
    """Verify that tmux can submit to Codex TUI using the configured key."""

    if not shutil.which("tmux"):
        return ProbeResult(False, "tmux is not available on PATH")
    if not shutil.which(codex_binary):
        return ProbeResult(False, f"{codex_binary} is not available on PATH")

    session = f"agent-orchestra-tui-probe-{os.getpid()}"
    try:
        key = normalize_submit_key(
            submit_key
            if submit_key is not None
            else os.environ.get("AGENT_ORCHESTRA_TUI_SUBMIT_KEY", "")
        )
    except ValueError as exc:
        return ProbeResult(False, str(exc))
    tmp_parent = Path("/private/tmp") if Path("/private/tmp").is_dir() else Path(tempfile.gettempdir())
    with tempfile.TemporaryDirectory(prefix="agent-orchestra-tui-probe-", dir=tmp_parent) as tmpdir:
        root = Path(tmpdir)
        home = root / "home"
        codex_home = root / "codex_home"
        workspace = root / "workspace"
        for path in (home, codex_home, workspace):
            path.mkdir(parents=True, exist_ok=True)
        config_path = codex_home / "agent-orchestra.config.toml"
        config_path.write_text(codex_config(workspace, config_path), encoding="utf-8")
        config_path.chmod(0o600)
        _copy_auth(codex_home)

        launch = (
            f"HOME={shlex.quote(str(home))} CODEX_HOME={shlex.quote(str(codex_home))} "
            + _quote_command(
                [
                    codex_binary,
                    "--profile",
                    "agent-orchestra",
                    "--no-alt-screen",
                    "--ask-for-approval",
                    "never",
                    "--sandbox",
                    "workspace-write",
                    "--cd",
                    str(workspace),
                ]
            )
        )

        try:
            started = _run(["tmux", "new-session", "-d", "-s", session, launch])
            if started.returncode != 0:
                return ProbeResult(False, started.stderr.strip() or "tmux session start failed")

            time.sleep(3.0)
            pane = _codex_pane(session)
            if not pane:
                return ProbeResult(False, "could not find Codex TUI pane")

            capture = _run(["tmux", "capture-pane", "-t", pane, "-p", "-S", "-80"]).stdout
            if "Do you trust the contents of this directory?" in capture:
                _run(["tmux", "send-keys", "-t", pane, key])
                time.sleep(1.0)
            _run(["tmux", "send-keys", "-t", pane, "/exit", key])

            for poll_index in range(24):
                if _run(["tmux", "has-session", "-t", session]).returncode != 0:
                    return ProbeResult(True, f"Codex TUI accepted /exit via {key}")
                if poll_index in {3, 7, 11}:
                    _run(["tmux", "send-keys", "-t", pane, key])
                time.sleep(0.5)
            capture = _run(["tmux", "capture-pane", "-t", pane, "-p", "-S", "-80"]).stdout
            return ProbeResult(False, f"Codex TUI did not close after /exit {key}", capture[-1200:])
        finally:
            _run(["tmux", "kill-session", "-t", session])


def _copy_auth(codex_home: Path) -> None:
    candidates: list[Path] = []
    if current := os.environ.get("CODEX_HOME"):
        candidates.append(Path(current).expanduser() / "auth.json")
    candidates.append(Path.home() / ".codex" / "auth.json")
    for source in candidates:
        if source.is_file():
            target = codex_home / "auth.json"
            shutil.copy2(source, target)
            target.chmod(0o600)
            return


def _codex_pane(session: str) -> str | None:
    result = _run(["tmux", "list-panes", "-t", session, "-F", "#{pane_id} #{pane_current_command} #{pane_active}"])
    rows = [line.split() for line in result.stdout.splitlines() if line.strip()]
    for row in rows:
        if len(row) >= 2 and row[1] in {"codex", "node"}:
            return row[0]
    for row in rows:
        if len(row) >= 3 and row[2] == "1":
            return row[0]
    return rows[0][0] if rows else None


def _quote_command(args: list[str]) -> str:
    return " ".join(shlex.quote(arg) for arg in args)


def _run(args: list[str], input: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, input=input, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prepare isolated launch material for one agent-orchestra Agent."
    )
    parser.add_argument("--run-dir")
    parser.add_argument("--target-project")
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--agent-kind", default="ProfessionalAgent")
    parser.add_argument("--lead-layer")
    parser.add_argument(
        "--protocol-layer",
        help="layer directory name or numeric prefix under AGENT_ORCHESTRA_REPO_ROOT/layers",
    )
    parser.add_argument("--instruction-source")
    parser.add_argument("--instruction-text")
    parser.add_argument("--tmux-pane")
    parser.add_argument("--initial-state", default="working")
    parser.add_argument("--auth-source")
    args = parser.parse_args(argv)

    run_dir = args.run_dir or os.environ.get("AGENT_ORCHESTRA_RUN_DIR")
    if not run_dir and os.environ.get("AGENT_ORCHESTRA_TASK_FILE"):
        run_dir = str(Path(os.environ["AGENT_ORCHESTRA_TASK_FILE"]).expanduser().resolve().parent)
    target_project = args.target_project or os.environ.get("AGENT_ORCHESTRA_TARGET_PROJECT")

    if not run_dir:
        parser.error("--run-dir or AGENT_ORCHESTRA_RUN_DIR is required")
    if not target_project:
        parser.error("--target-project or AGENT_ORCHESTRA_TARGET_PROJECT is required")

    instruction_source = args.instruction_source
    if not instruction_source and args.protocol_layer:
        instruction_source = str(resolve_protocol_layer_instruction(args.protocol_layer))
    if not instruction_source and not args.instruction_text and args.lead_layer:
        instruction_source = str(resolve_protocol_layer_instruction(args.lead_layer))
    if not instruction_source and not args.instruction_text:
        parser.error("--instruction-source, --instruction-text, --protocol-layer, or resolvable --lead-layer is required")
    lead_layer = args.lead_layer
    if instruction_source and not lead_layer:
        lead_layer = Path(instruction_source).expanduser().resolve().parent.name

    material = prepare_launch_material(
        run_dir=run_dir,
        agent_id=args.agent_id,
        agent_kind=args.agent_kind,
        target_project=target_project,
        instruction_text=args.instruction_text,
        instruction_source=instruction_source,
        lead_layer=lead_layer,
        task_file=os.environ.get("AGENT_ORCHESTRA_TASK_FILE"),
        initial_state=args.initial_state,
        tmux_pane=args.tmux_pane,
        auth_source=args.auth_source,
    )

    print(f"agent_dir={material.state_file.parent}")
    print(f"command_json={material.command_path}")
    print(f"env_json={material.env_path}")
    print(f"env_sh={material.env_shell_path}")
    print(f"workspace={material.workspace}")
    print(f"codex_home={material.codex_home}")
    return 0


def resolve_protocol_layer_instruction(selector: str) -> Path:
    normalized = selector.strip()
    if not normalized:
        raise FileNotFoundError("empty protocol layer selector")
    layers_dir = protocol_root() / "layers"
    if not layers_dir.is_dir():
        raise FileNotFoundError(f"protocol layers directory was not found: {layers_dir}")

    exact = layers_dir / normalized / "INSTRUCTIONS.md"
    if exact.is_file():
        return exact

    prefix_matches: list[Path] = []
    if normalized.isdigit():
        prefixes = {normalized, normalized.zfill(2)}
        prefix_matches = [
            path / "INSTRUCTIONS.md"
            for path in sorted(layers_dir.iterdir())
            if path.is_dir() and any(path.name.startswith(f"{prefix}_") for prefix in prefixes)
            and (path / "INSTRUCTIONS.md").is_file()
        ]
    if len(prefix_matches) == 1:
        return prefix_matches[0]
    if len(prefix_matches) > 1:
        raise FileNotFoundError(f"protocol layer selector {selector!r} matched multiple layers")

    raise FileNotFoundError(f"protocol layer INSTRUCTIONS.md was not found for selector {selector!r}")


def protocol_root() -> Path:
    if root := os.environ.get("AGENT_ORCHESTRA_REPO_ROOT"):
        return Path(root).expanduser().resolve()
    return Path(__file__).resolve().parents[2]


if __name__ == "__main__":
    raise SystemExit(main())
