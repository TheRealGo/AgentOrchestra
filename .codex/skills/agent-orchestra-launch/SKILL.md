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
- `env.json`;
- `env.sh`;
- `command.json`.

Runtime does not create panes, retry shell commands, inspect process state, or
schedule work. The Agent performs normal shell/tmux operation.

The generated `workspace/AGENTS.md` is the Agent behavior surface. Layer
`INSTRUCTIONS.md` files are specialist perspectives only; do not put tmux,
Hook, retirement, or team-operation behavior in layers.

## Isolation Rule

The run directory must be outside the target project tree. If the isolated
workspace sits under the target project, target root or parent `AGENTS.md` can
become an ancestor startup instruction.

The Codex CLI launch uses Codex options for sandbox, approval, hooks,
workspace, and target access. The generated profile is kept minimal for project
trust and Stop Hook registration. Do not override Codex TUI keymaps from
agent-orchestra; tmux delivery uses `${AGENT_ORCHESTRA_TUI_SUBMIT_KEY:-C-m}`.

```sh
codex --profile agent-orchestra --ask-for-approval never --sandbox workspace-write --enable hooks --cd "$ISOLATED_WORKSPACE" --add-dir "$TARGET_PROJECT"
```

`--cd` points at the isolated workspace with generated `AGENTS.md`.
`--add-dir` grants target project access as data/workspace material.
`CODEX_HOME` points at the isolated `codex_home`.

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

The helper prints `agent_dir`, `command_json`, `env_json`, `env_sh`, `workspace`, and
`codex_home`. It does not launch Codex. It composes the copied Agent behavior
template with the selected layer perspective into the isolated
`workspace/AGENTS.md`.

## Launch In A Shell Pane

Read `env.json` and `command.json`, then launch the `argv` shown in
`command.json` with one short command in the target shell pane. Avoid pasting
many `export` lines; it clutters the visible Agent pane and makes failures hard
to read.

Preferred pattern inside the target shell pane:

```sh
AGENT_DIR=/path/from/helper/output
. "$AGENT_DIR/env.sh"
codex --profile agent-orchestra --ask-for-approval never --sandbox workspace-write --enable hooks \
  -c 'sandbox_workspace_write.network_access=true' \
  --cd "$AGENT_DIR/workspace" --add-dir "$AGENT_ORCHESTRA_TARGET_PROJECT"
```

When sending that launch command through `tmux send-keys`, quote the whole shell
command with single quotes so `$AGENT_DIR` and `$AGENT_ORCHESTRA_TARGET_PROJECT`
expand in the target pane, not in MainAgent's shell:

```sh
tmux send-keys -t "$PANE" 'AGENT_DIR=/path/from/helper/output; . "$AGENT_DIR/env.sh"; codex --profile agent-orchestra --ask-for-approval never --sandbox workspace-write --enable hooks -c sandbox_workspace_write.network_access=true --cd "$AGENT_DIR/workspace" --add-dir "$AGENT_ORCHESTRA_TARGET_PROJECT"' "${AGENT_ORCHESTRA_TUI_SUBMIT_KEY:-C-m}"
```

After launch, capture the pane and confirm paths did not collapse to `/env.sh`
or `/workspace`.

If `env.sh` is not available, regenerate launch material rather than pasting
every environment variable into the pane. This is launch hygiene, not a wrapper
around tmux or Codex behavior.

Do not create wrapper scripts for launch. Do not create durable wrapper scripts
or long paste commands for launch.

`codex exec` is not a substitute for an independent ProfessionalAgent.
