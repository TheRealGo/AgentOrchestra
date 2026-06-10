---
name: agent-orchestra-launch
description: Use when preparing or launching an isolated agent-orchestra Claude Code session, including clean HOME/CLAUDE_CONFIG_DIR, generated CLAUDE.md, env.json, command.json, isolated settings.json, --add-dir, --permission-mode, and avoiding claude -p/--print for ProfessionalAgents.
---

# agent-orchestra Launch Skill

Use this Skill when creating or starting a MainAgent or ProfessionalAgent
Claude Code session.

## Boundary

Runtime prepares only the isolated launch surface:

- generated `workspace/CLAUDE.md`;
- clean `home/`;
- clean `claude_home/`;
- copied Skills, Hooks, `settings.json`, and auth;
- `env.json`;
- `env.sh`;
- `command.json`.

Runtime does not create panes, retry shell commands, inspect process state, or
schedule work. The Agent performs normal shell/tmux operation.

The generated `workspace/CLAUDE.md` is the Agent behavior surface. Layer
`INSTRUCTIONS.md` files are specialist perspectives only; do not put tmux,
Hook, retirement, or team-operation behavior in layers.

## Isolation Rule

The run directory must be outside the target project tree. If the isolated
workspace sits under the target project, target root or parent `CLAUDE.md` can
become an ancestor startup instruction.

The Claude Code launch selects the target project as data with `--add-dir`,
adds the run directory as a second `--add-dir` so the shared `tasks.ini` and
per-agent `state.json` (which live at the run-dir root, outside the workspace)
are accessible, and sets the permission mode with `--permission-mode`. The
default mode is `bypassPermissions`, so the orchestrated team edits the target
(including `.claude/...`) and runs shell commands fully unattended. Isolation
comes from chdir into the workspace plus the isolated `CLAUDE_CONFIG_DIR`: its
generated `settings.json` registers the Stop Hook, and a seeded `.claude.json`
pre-accepts project trust. Do not override Claude Code TUI keymaps from
agent-orchestra; tmux delivery uses `${AGENT_ORCHESTRA_TUI_SUBMIT_KEY:-C-m}`.

```sh
cd "$ISOLATED_WORKSPACE"
claude --add-dir "$TARGET_PROJECT" --add-dir "$AGENT_ORCHESTRA_RUN_DIR" --permission-mode "${AGENT_ORCHESTRA_PERMISSION_MODE:-bypassPermissions}"
```

Claude Code launches in the current working directory and has no workspace-
selection flag, so chdir into the isolated workspace (it holds the generated
`CLAUDE.md`) before launching. The first `--add-dir` grants target project
access as data/workspace material; the second grants run-dir access for the
shared task/state files. `CLAUDE_CONFIG_DIR` points at the isolated
`claude_home`. Prefer launching the exact `argv` from `command.json`, which the
runtime already builds with both `--add-dir` entries and the resolved mode.

`bypassPermissions` shows a one-time warning gate at launch ("WARNING: Claude
Code running in Bypass Permissions mode … 1. No, exit / 2. Yes, I accept"); the
trust seed does not suppress it. After launching the pane, wait for that gate
and accept it with `Down` then `Enter` (selects "Yes, I accept"), then wait for
the composer before delivering the task. Only after the gate is accepted does
the Agent run unattended.

## Prepare Material

When launch material is missing, run the installed helper with the selected
layer perspective and pane id:

```sh
"$AGENT_ORCHESTRA_PYTHON" "$CLAUDE_CONFIG_DIR/agent_orchestra_minimal/prepare_agent_launch.py" \
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

The helper prints `agent_dir`, `command_json`, `env_json`, `env_sh`, `workspace`, and
`claude_config_dir`. It does not launch Claude Code. It composes the copied Agent behavior
template with the selected layer perspective into the isolated
`workspace/CLAUDE.md`.

## Launch In A Shell Pane

Read `env.json` and `command.json`, then launch the `argv` shown in
`command.json` with one short command in the target shell pane. Avoid pasting
many `export` lines; it clutters the visible Agent pane and makes failures hard
to read.

Preferred pattern inside the target shell pane:

```sh
AGENT_DIR=/path/from/helper/output
. "$AGENT_DIR/env.sh"
cd "$AGENT_DIR/workspace"
claude --add-dir "$AGENT_ORCHESTRA_TARGET_PROJECT" --add-dir "$AGENT_ORCHESTRA_RUN_DIR" --permission-mode "${AGENT_ORCHESTRA_PERMISSION_MODE:-bypassPermissions}"
```

When sending that launch command through `tmux send-keys`, quote the whole shell
command with single quotes so `$AGENT_DIR`, `$AGENT_ORCHESTRA_TARGET_PROJECT`,
and `$AGENT_ORCHESTRA_RUN_DIR` expand in the target pane, not in MainAgent's
shell:

```sh
tmux send-keys -t "$PANE" 'AGENT_DIR=/path/from/helper/output; . "$AGENT_DIR/env.sh"; cd "$AGENT_DIR/workspace"; claude --add-dir "$AGENT_ORCHESTRA_TARGET_PROJECT" --add-dir "$AGENT_ORCHESTRA_RUN_DIR" --permission-mode "${AGENT_ORCHESTRA_PERMISSION_MODE:-bypassPermissions}"' "${AGENT_ORCHESTRA_TUI_SUBMIT_KEY:-C-m}"
```

After launch, capture the pane and confirm paths did not collapse to `/env.sh`
or `/workspace`. Under the default `bypassPermissions` mode the pane then shows
the one-time "Bypass Permissions" warning gate — accept it before delivering the
task:

```sh
tmux send-keys -t "$PANE" Down   # move selection to "2. Yes, I accept"
tmux send-keys -t "$PANE" Enter  # confirm; composer appears, Agent runs unattended
```

Capture the pane again to confirm the composer (not the gate) is showing before
sending the ProfessionalAgent's task. If the gate is still up, the task keystrokes
would be swallowed by the dialog.

If `env.sh` is not available, regenerate launch material rather than pasting
every environment variable into the pane. This is launch hygiene, not a wrapper
around tmux or Claude Code behavior.

Do not create wrapper scripts for launch. Do not create durable wrapper scripts
or long paste commands for launch.

`claude -p`/`--print` is not a substitute for an independent ProfessionalAgent.
