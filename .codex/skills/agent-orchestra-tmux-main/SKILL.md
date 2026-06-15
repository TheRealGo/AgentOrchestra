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

Use ordinary `tmux` commands directly for pane operations. Do not create wrapper
scripts for pane operations. For task, follow-up, and review message delivery,
use `agent-orchestra-tmux-common`; that Skill owns the concrete
send/capture/retry procedure and delivery-failure handling.

## Split And Layout

```sh
MAIN_PANE="${AGENT_ORCHESTRA_TMUX_PANE:?}"
PRO_PANE_1="$(tmux split-window -h -t "$MAIN_PANE" -c "$PWD" -P -F '#{pane_id}')"
PRO_PANE_2="$(tmux split-window -v -t "$PRO_PANE_1" -c "$PWD" -P -F '#{pane_id}')"
tmux select-layout -t "$MAIN_PANE" tiled
```

Always pass an explicit `-t` target for `split-window`, `select-layout`, and
other pane/window operations. Never rely on tmux's current active client or
active window; MainAgent may be running in a detached or non-active session, and
untargeted splits can create ProfessionalAgent panes in the wrong session.

Keep MainAgent readable. When multiple ProfessionalAgent panes exist, keep
MainAgent on the left where practical and arrange ProfessionalAgents on the
right.
Before launching or delivering to a ProfessionalAgent, verify the target pane is
tall enough to show the Codex composer and status footer. If a pane only shows a
launch banner, MCP warning, or weekly-limit notice with no composer, enlarge the
pane or rearrange the layout before retrying delivery; a hidden composer is not a
ready pane.

## Launch A ProfessionalAgent

1. Choose the ProfessionalAgent layer from the user goal, affected files, risk,
   and evidence needs.
2. Split a shell pane and capture its pane id.
3. Use `agent-orchestra-launch` to prepare isolated launch material.
   The helper-created ProfessionalAgent state starts as `ready`; do not change
   it to `working` until the scoped assignment delivery is confirmed or the
   ProfessionalAgent itself accepts the assignment and records `working`.
4. In the shell pane, launch the Codex CLI `argv` from `command.json` with the
   explicit generated environment from `env.json` using `os.execvpe`. Do not let
   the final Codex process inherit the parent shell environment; parent shells
   may contain tokens that Codex can snapshot. Keep the pane readable; avoid
   pasting many `export` lines.
5. Before delivery, add the ProfessionalAgent work item to `[InProgress]` with
   owner, pane id, reviewers, required checks, and expected evidence.
6. After the Codex TUI is ready, use `agent-orchestra-tmux-common` to send one
   complete scoped initial task immediately and verify delivery before leaving
   that pane unattended. Do not continue solo investigation, launch the next
   ProfessionalAgent, or start implementation while a ready ProfessionalAgent
   still shows only a default composer. Do not send a preliminary receipt-only
   message or contradictory follow-up before the first assignment is accepted.
   A non-zero `agent_orchestra_minimal.tmux_send` result for an initial
   ProfessionalAgent assignment is a blocking delivery defect, not a warning.
   Do not mark that ProfessionalAgent as working, do not rely on its future
   review, and do not launch additional Agents until delivery is confirmed,
   safely retried/relaunched, or recorded as blocked with evidence.
7. If the pane still shows a default composer prompt such as `Find and fix...`,
   `Improve documentation...`, or `Implement {feature}`, delivery is not
   confirmed; keep the work item open and record the failure or retry evidence.
   If delayed delivery affected the run, add a `[Candidates]` issue so the
   final sweep cannot hide it as narrative-only history.
8. If inherited MCP startup warnings, a Codex update notice, a model-choice
   prompt, a weekly-limit notice, or another launch-time banner keeps the TUI
   non-interactive, use the delivery helper's bounded recovery path, then inspect
   the pane and retry or relaunch when safe.
   Disabling MCP inheritance or moving the scoped QA work back to MainAgent may
   be an emergency workaround and evidence route, but it is not an integrated
   fix for the AgentOrchestra delivery defect. Keep a candidate unresolved
   until a runtime or contract fix is made and a later E2E proves delivery works
   without the defect recurring.

If launch fails, inspect the pane and process state, re-read `env.json`,
`env.sh`, and `command.json`, retry in the same pane when safe, or use a fresh pane. Report
the exact pane id, launch material path, captured error, and next action when
recovery still fails. Do not add runtime scripts to hide the failure.

## Retire A ProfessionalAgent

If MainAgent accepts a ProfessionalAgent result and no follow-up remains:

1. Remove the accepted ProfessionalAgent task from open task sections.
2. Write that ProfessionalAgent state to `retired`.
3. Send `/exit` after clearing any stale composer text. Do not skip this step;
   `kill-pane` is only cleanup after an attempted `/exit` and a short wait.
4. Verify pane cleanup and use `kill-pane` if the accepted pane remains.

Set `retired` before `/exit` so the Stop Hook has a cheap quiet path during the
accepted retirement. This is only valid after MainAgent has accepted the result
or explicitly chosen retirement; do not use `retired` to silence unfinished
work.

```sh
tmux send-keys -t "$PANE" Escape C-u
tmux send-keys -t "$PANE" "/exit" "${AGENT_ORCHESTRA_TUI_SUBMIT_KEY:-C-m}"
```

Capture the pane after sending `/exit`. If `/exit` is still visible at the
composer, send the submit key again once; if unrelated text is still queued,
repeat the clear-and-send sequence before using `kill-pane` cleanup.

Retirement is not complete until the pane is gone. After a short wait, check
whether the pane id is still present:

```sh
if tmux list-panes -a -F '#{pane_id}' | rg -qxF "$PANE"; then
  tmux capture-pane -t "$PANE" -p -S -120
  tmux kill-pane -t "$PANE"
fi
```

Do not finish a run with accepted ProfessionalAgent panes still present. The
`retired` state makes the Hook quiet; it does not replace pane cleanup.

## Exit MainAgent When Requested

If the user explicitly instructed MainAgent to leave the orchestra after
completion, submit `/exit` to MainAgent's own pane as the final tmux action. Do
not use delayed or background self-exit shell jobs; under sandboxed Codex TUI
turns they can fail before sending the key.
Do not send a normal completion report, mark a persistent goal complete, or
wait at the prompt as a substitute for leaving the orchestra. If the self-exit
is required, the self-exit submission command is the final assistant action for
that turn; a still-present MainAgent pane means the requirement is not yet
satisfied.

Use a detached Python self-exit as the final tool action so the submit happens
after the active Codex turn has yielded back to the TUI. Send the submit key
again after short delays; empirically the first `/exit` paste can land while the
TUI is still returning from the active turn, leaving `/exit` visibly queued in
the composer until a later submit key arrives:

```sh
"$AGENT_ORCHESTRA_PYTHON" - <<'PY'
import os
import subprocess
import time

pane = os.environ["AGENT_ORCHESTRA_TMUX_PANE"]
submit_key = os.environ.get("AGENT_ORCHESTRA_TUI_SUBMIT_KEY", "C-m")

if os.fork() == 0:
    os.setsid()
    time.sleep(2)
    subprocess.run(["tmux", "send-keys", "-t", pane, "Escape", "C-u"], check=False)
    subprocess.run(["tmux", "send-keys", "-t", pane, "/exit", submit_key], check=False)
    for _ in range(2):
        time.sleep(2)
        subprocess.run(["tmux", "send-keys", "-t", pane, submit_key], check=False)
    time.sleep(2)
    subprocess.run(["tmux", "send-keys", "-t", pane, "Escape", "C-u"], check=False)
    subprocess.run(["tmux", "send-keys", "-t", pane, "/exit", submit_key], check=False)
PY
```

If self-exit submission fails or remains visibly queued, report the failure
explicitly. Do not claim that MainAgent exited when the pane is still present
with `/exit` stuck in the composer.
