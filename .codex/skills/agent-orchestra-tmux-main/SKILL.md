---
name: agent-orchestra-tmux-main
description: Use when MainAgent manages ProfessionalAgent tmux panes, including splitting panes, arranging layout, launching prepared ProfessionalAgents, sending tasks, following up, accepting results, /exit retirement, and kill-pane cleanup when appropriate.
---

# agent-orchestra tmux Main Skill

Use this Skill when MainAgent manages ProfessionalAgent panes. This is guidance
for the usual role split, not a hard permission boundary.

## Main Responsibilities

MainAgent usually owns:

- pane creation and layout;
- launching prepared ProfessionalAgents;
- initial task delivery;
- follow-up and review;
- `/exit` retirement;
- `kill-pane` cleanup after legitimate retirement.

Use ordinary `tmux` commands directly. Do not create wrapper scripts for pane
operations.

## Split And Layout

```sh
tmux split-window -h -c "$PWD"
tmux split-window -v -c "$PWD"
tmux select-layout tiled
```

Keep MainAgent readable. When multiple ProfessionalAgent panes exist, keep
MainAgent on the left where practical and arrange ProfessionalAgents on the
right.

## Launch A ProfessionalAgent

1. Choose the ProfessionalAgent layer from the user goal, affected files, risk,
   and evidence needs.
2. Split a shell pane and capture its pane id.
3. Use `agent-orchestra-launch` to prepare isolated launch material.
4. In the shell pane, source the generated `env.sh` and run the Codex CLI
   `argv` from `command.json`. Keep the pane readable; avoid pasting many
   `export` lines.
5. After the Codex TUI is ready, use `agent-orchestra-tmux-common` to send the
   scoped task and verify delivery.

If launch fails, inspect the pane and process state, re-read `env.json`,
`env.sh`, and `command.json`, retry in the same pane when safe, or use a fresh pane. Report
the exact pane id, launch material path, captured error, and next action when
recovery still fails. Do not add runtime scripts to hide the failure.

## Retire A ProfessionalAgent

If MainAgent accepts a ProfessionalAgent result and no follow-up remains:

1. Remove the accepted ProfessionalAgent task from open task sections.
2. Write that ProfessionalAgent state to `retired`.
3. Send `/exit`.
4. Verify pane cleanup and use `kill-pane` if the accepted pane remains.

Set `retired` before `/exit` so the Stop Hook has a cheap quiet path during the
accepted retirement. This is only valid after MainAgent has accepted the result
or explicitly chosen retirement; do not use `retired` to silence unfinished
work.

```sh
tmux send-keys -t "$PANE" "/exit" "${AGENT_ORCHESTRA_TUI_SUBMIT_KEY:-C-m}"
```

Retirement is not complete until the pane is gone. After a short wait, verify
the pane id is absent:

```sh
tmux list-panes -a -F '#{pane_id}' | rg -qxF "$PANE"
```

If the accepted pane remains, capture any final output and force-close it:

```sh
tmux capture-pane -t "$PANE" -p -S -120
tmux kill-pane -t "$PANE"
```

Do not finish a run with accepted ProfessionalAgent panes still present. The
`retired` state makes the Hook quiet; it does not replace pane cleanup.
