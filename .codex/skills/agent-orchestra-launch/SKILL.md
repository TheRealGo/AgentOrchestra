---
name: agent-orchestra-launch
description: Use when preparing or launching an isolated agent-orchestra Codex CLI session, including clean HOME/CODEX_HOME, generated AGENTS.md, env.json, command.json, --profile agent-orchestra, --cd, --add-dir, and avoiding codex exec for ProfessionalAgents.
---

# agent-orchestra Launch Skill

Use this Skill when creating or starting a MainAgent or ProfessionalAgent
Codex CLI session.

## Boundary

Runtime prepares only the isolated launch surface:

- generated `workspace/AGENTS.md`;
- clean `home/`;
- clean `codex_home/`;
- copied Skills, Hooks, config, and auth;
- inherited `[mcp_servers.*]` from the current Codex config unless explicitly
  disabled;
- `env.json`;
- `env.sh`;
- `command.json`.

Runtime does not create panes, retry shell commands, inspect process state, or
schedule work. The Agent performs normal shell/tmux operation.

The generated `workspace/AGENTS.md` is the Agent behavior surface. Layer
`INSTRUCTIONS.md` files are specialist perspectives only; do not put tmux,
Hook, retirement, or team-operation behavior in layers.

## Isolation Rule

The run directory must be durable and outside the target project tree. Use an
explicit `--run-dir` or `AGENT_ORCHESTRA_RUN_ROOT` when a caller needs a
specific parent directory; do not place active runs under volatile temp
directories that may be cleaned while tmux panes are still alive. If the
isolated workspace sits under the target project, target root or parent
`AGENTS.md` can become an ancestor startup instruction.

The Codex CLI launch uses Codex options for sandbox, approval, hooks,
workspace, and target access. The generated profile is kept minimal for project
trust and Stop Hook registration. Do not override Codex TUI keymaps from
agent-orchestra; tmux delivery uses `${AGENT_ORCHESTRA_TUI_SUBMIT_KEY:-C-m}`.

Do not recompose the Codex launch command by hand. The generated
`command.json` is the runtime boundary for the full argv, including any
detected feature flags such as `--enable prevent_idle_sleep`.

In that argv, `--cd` points at the isolated workspace with generated
`AGENTS.md`; `--add-dir` grants target project access as data/workspace
material and also grants `AGENT_ORCHESTRA_RUN_DIR` access for Agent state,
launch material, cache/env directories, and evidence artifacts. Runtime-run
access does not make the run directory part of the user-requested edit scope:
use `$AGENT_ORCHESTRA_EDIT_ROOT` for repository patching and git verification.
If `codex features list` reports `prevent_idle_sleep`, runtime may also add
`--enable prevent_idle_sleep`; set
`AGENT_ORCHESTRA_DISABLE_PREVENT_IDLE_SLEEP=1` before preparing launch material
to opt out.
When the requested target is nested inside a Git worktree, runtime may add the
worktree root as an additional `--add-dir`; Agents should use
`$AGENT_ORCHESTRA_EDIT_ROOT` for git status, patching, and verification while
preserving `$AGENT_ORCHESTRA_TARGET_PROJECT` as the user-requested scope.
`CODEX_HOME` points at the isolated `codex_home`.
Runtime copies only `[mcp_servers.*]` and child tables from
`$CODEX_HOME/config.toml`, falling back to `~/.codex/config.toml`. It does not
copy approval policy, sandbox mode, hooks, projects, profiles, or other runtime
boundary settings. Set `AGENT_ORCHESTRA_DISABLE_MCP_INHERITANCE=1` only when
MCP inheritance must be disabled. Generated command metadata records MCP server
names only; do not print inherited env values or secrets.
Each Agent also receives `AGENT_ORCHESTRA_CACHE_DIR`,
`AGENT_ORCHESTRA_ARTIFACT_DIR`, and `AGENT_ORCHESTRA_ENV_DIR` for ephemeral
dependency caches, evidence, and disposable environment state.

## Prepare Material

When launch material is missing, run the installed helper with the selected
layer perspective and pane id:

```sh
"$AGENT_ORCHESTRA_PYTHON" "$CODEX_HOME/agent_orchestra_minimal/prepare_agent_launch.py" \
  --agent-id "pro-layer-review" \
  --protocol-layer "08" \
  --tmux-pane "$PRO_PANE"
```

Use `--protocol-layer` with a numeric layer id such as `06`, `08`, `15`, or an
exact protocol layer directory name. The helper resolves the layer from
`$AGENT_ORCHESTRA_REPO_ROOT/layers`, not from the target project. Do not use the
target project's `layers/` tree as the source for ProfessionalAgent startup
perspective unless the user explicitly asks for project-local experimental
layer instructions.

Do not wrap environment-variable paths in single quotes when invoking
`prepare_agent_launch.py`; single quotes prevent shell expansion and make the
helper look for a literal `$VARIABLE` path. Use double quotes, or an
already-resolved absolute path.

The helper prints `agent_dir`, `command_json`, `env_json`, `env_sh`,
`workspace`, and `codex_home`. It does not launch Codex. It composes the copied
Agent behavior template with the selected layer perspective into the isolated
`workspace/AGENTS.md`.

For ProfessionalAgents, the helper initializes `state.json` as `ready` unless
`--initial-state` is explicitly provided. Leave it `ready` until the Codex TUI
has accepted the scoped assignment. Delivery confirmation, not pane creation or
TUI startup, is what allows the Agent to become `working`.

## Launch In A Shell Pane

Read `env.json` and `command.json`, then launch the `argv` shown in
`command.json` with one short command in the target shell pane. The final Codex
process must receive the explicit generated environment from `env.json`, not
the parent shell environment; parent shells can contain tokens or other
secrets that Codex may snapshot. Avoid pasting many `export` lines; it clutters
the visible Agent pane and makes failures hard to read. Do not type out
`codex --profile ...` yourself; that can drop runtime feature flags or future
launch-boundary changes.

Preferred pattern inside the target shell pane:

```sh
PYTHON_BIN="${AGENT_ORCHESTRA_PYTHON:-python3}"
"$PYTHON_BIN" -c 'import json, os, sys; from pathlib import Path; agent=Path(sys.argv[1]); cmd=json.loads((agent/"command.json").read_text()); env=json.loads((agent/"env.json").read_text()); os.chdir(cmd["cwd"]); os.execvpe(cmd["argv"][0], cmd["argv"], env)' /path/from/helper/output
```

When sending that launch command through `tmux send-keys`, quote the whole shell
command with single quotes and pass the absolute `agent_dir` path as the final
Python argument. Do not depend on pane-local shell variables unless they are
exported into the Python process:

```sh
tmux send-keys -t "$PANE" 'PYTHON_BIN="${AGENT_ORCHESTRA_PYTHON:-python3}"; "$PYTHON_BIN" -c '"'"'import json, os, sys; from pathlib import Path; agent=Path(sys.argv[1]); cmd=json.loads((agent/"command.json").read_text()); env=json.loads((agent/"env.json").read_text()); os.chdir(cmd["cwd"]); os.execvpe(cmd["argv"][0], cmd["argv"], env)'"'"' /path/from/helper/output' "${AGENT_ORCHESTRA_TUI_SUBMIT_KEY:-C-m}"
```

Before pasting any shell launch command, capture the target pane. The pane must
be at a shell prompt or otherwise clearly outside Codex TUI. Do not paste a
launch command into a pane that still shows a Codex composer (`›`), "Working",
`Goal paused`, "Conversation interrupted", `/ps`, or any background terminal
status. In that case, first submit `/exit`, wait for a shell prompt, or create a
new pane and record the recovery in `[Candidates]`. A recovery launch command
visible inside an active Codex composer is prompt pollution and must be treated
as failed launch evidence, not as a valid relaunch.

After launch, capture the pane and confirm paths did not collapse to `/env.sh`
or `/workspace`.

If `env.sh` is not available, regenerate launch material rather than pasting
every environment variable into the pane. This is launch hygiene, not a wrapper
around tmux or Codex behavior.

Do not create wrapper scripts for launch. Do not create durable wrapper scripts
or long paste commands for launch.

`codex exec` is not a substitute for an independent ProfessionalAgent.
