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
5. After launch, verify the exact pane identity before recording or delivering
   work:
   - `tmux display-message -p -t "$PANE" '#{session_name}:#{window_index}.#{pane_index} #{pane_id} #{pane_current_command} #{pane_current_path}'`
     must still refer to the pane id returned by the targeted `split-window`
     inside the current dedicated orchestra session.
   - `pane_current_command` must be the Codex CLI process, normally `node` or
     `codex`, not `zsh`, `bash`, `fish`, or another shell.
   - `pane_current_path` must match `command.json` `cwd` or the prepared
     ProfessionalAgent workspace under that Agent's launch directory, not the
     MainAgent workspace, the target repository root, CAO, ToO, service-E2E, or
     another session.
   - A bounded capture must show the Codex TUI for that ProfessionalAgent, not
     a shell prompt, default launch debris, or a different conversation.
   If any check fails, do not send task text, do not mark the Agent `working`,
   and do not launch more Agents. Kill or reuse only that bad pane when it is
   still inside the current dedicated orchestra session, relaunch from the
   same `command.json`, and record a launch-routing `[Candidates]` item with
   pane id, session name, expected cwd, actual command/path, and capture
   evidence.
6. Do not use raw probe commands such as `echo launch-test`, `paste-test`,
   `tmux display-message` without `-t`, `testbuf`, or active-pane inference to
   decide whether a ProfessionalAgent pane is valid. Raw `tmux send-keys` is
   only for shell launch commands and `/exit`; all task, review, follow-up, and
   recovery instructions go through `agent-orchestra-tmux-common` after pane
   identity is verified.
7. Before delivery, add the ProfessionalAgent work item to `[InProgress]` with
   owner, verified pane id, verified session name, reviewers, required checks,
   and expected evidence. If you had to create the task entry before launch
   verification, keep it explicitly blocked until verification passes; do not
   leave `status=launching` or `ready` entries that point at an unverified shell
   pane.
8. After the Codex TUI is ready and the pane identity is verified, use
   `agent-orchestra-tmux-common` to send one
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
   If the helper returns non-zero but a later bounded capture proves the scoped
   assignment was accepted and the pane is actually Working on that assignment,
   immediately update the ProfessionalAgent `state.json` to `working`, keep an
   unresolved `[Candidates]` delivery-defect item with the helper result and
   recovery evidence, and continue supervising that Agent. Do not leave Agent
   state as `ready` while the pane is visibly Working on accepted assigned work.
   If a required final ProfessionalAgent report request is accepted only after
   multiple submit attempts, record the result-json retry count and
   `zero_issue_blocker` flag as `[Gates]` or `[Candidates]` evidence. Do not
   report clean zero-issue completion until the degraded-delivery disposition is
   fixed and regression-verified or otherwise explicitly resolved in the task
   file.
9. If the pane still shows a default composer prompt such as `Find and fix...`,
   `Improve documentation...`, or `Implement {feature}`, delivery is not
   confirmed; keep the work item open and record the failure or retry evidence.
   If delayed delivery affected the run, add a `[Candidates]` issue so the
   final sweep cannot hide it as narrative-only history.
10. If inherited MCP startup warnings, a Codex update notice, a model-choice
   prompt, a weekly-limit notice, or another launch-time banner keeps the TUI
   non-interactive, use the delivery helper's bounded recovery path, then inspect
   the pane and retry or relaunch when safe.
   Disabling MCP inheritance or moving the scoped QA work back to MainAgent may
   be an emergency workaround and evidence route, but it is not an integrated
   fix for the AgentOrchestra delivery defect. Keep a candidate unresolved
   until a runtime or contract fix is made and a later E2E proves delivery works
   without the defect recurring.
11. A ProfessionalAgent that remains visibly Working with no new output beyond
   the assignment's bounded supervision window is a stuck-pane condition. Capture
   the pane, interrupt or send a recovery instruction through
   `agent-orchestra-tmux-common`, mark the work item blocked/deferred or
   relaunch it with evidence, and keep `[status] progress`. Do not wait
   indefinitely, and do not let stale `ready` Agent state hide a stuck Working
   pane.

If launch fails, inspect the pane and process state, re-read `env.json`,
`env.sh`, and `command.json`, retry in the same pane when safe, or use a fresh pane. Report
the exact pane id, launch material path, captured error, and next action when
recovery still fails. Do not add runtime scripts to hide the failure.

## Retire A ProfessionalAgent

If MainAgent accepts a ProfessionalAgent result and no follow-up remains:

1. Remove the accepted ProfessionalAgent task from open task sections.
2. Write that ProfessionalAgent state to `retired`.
3. Send `/exit` with the packaged `agent_orchestra_minimal.self_exit` helper
   when available, passing `--pane "$PANE"` and a result JSON path under the
   artifact directory. Do not skip this step; `kill-pane` is only cleanup after
   an attempted `/exit` with bounded retries and captured evidence.
4. Verify pane cleanup and use `kill-pane` only if the accepted pane remains.
   If the helper is unavailable, use the manual fallback below, then use
   `kill-pane` only after an attempted `/exit` and a captured residue check.

Set `retired` before `/exit` so the Stop Hook has a cheap quiet path during the
accepted retirement. This is only valid after MainAgent has accepted the result
or explicitly chosen retirement; do not use `retired` to silence unfinished
work.

```sh
"${AGENT_ORCHESTRA_PYTHON:-python3}" -m agent_orchestra_minimal.self_exit \
  --pane "$PANE" \
  --submit-key "${AGENT_ORCHESTRA_TUI_SUBMIT_KEY:-C-m}" \
  --result-path "${AGENT_ORCHESTRA_ARTIFACT_DIR}/self-exit-${AGENT_ID}.json" \
  --foreground
```

The helper alternates submit keys, clears queued `/exit` text, and handles
intermediate Codex prompts such as the Memories opt-in prompt before cleanup.
For a verified dedicated SelfE2E session, an accepted ProfessionalAgent may
already have returned to a shell after `/exit` before the helper inspects the
pane. In that case, and only after the ProfessionalAgent result is accepted,
its state is `retired`, and the pane id/session still match that accepted
ProfessionalAgent inside the dedicated `AgentOrchestra-self-e2e-*` session,
pass `--allow-shell-cleanup-session-prefix AgentOrchestra-self-e2e-` so the
helper can record same-session shell cleanup as `closed=true`. Do not use this
for CAO, ToO, observer, service-E2E controller, ambiguous panes, or
ProfessionalAgents whose result has not been accepted.

Manual fallback:

```sh
tmux send-keys -t "$PANE" Escape C-u
tmux send-keys -t "$PANE" "/exit" "${AGENT_ORCHESTRA_TUI_SUBMIT_KEY:-C-m}"
```

Capture the pane after sending `/exit`. If `/exit` is still visible at the
composer, a prompt such as Memories is blocking exit, or unrelated text is
still queued, record that as retirement residue evidence before any
`kill-pane` cleanup.

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

Use the packaged `agent_orchestra_minimal.self_exit` helper as the final tool
action so the submit happens after the active Codex turn has yielded back to the
TUI. The helper retries only while `pane_current_command` is still a Codex CLI
command such as `node` or `codex`,
alternates `C-m`/`C-j` submit keys, writes JSON evidence, and clears queued
`/exit` text if the pane remains open. If `/exit` still cannot close the
MainAgent pane after bounded attempts, the helper performs `kill-pane` cleanup
and records that cleanup in the JSON evidence. This avoids ad hoc delayed jobs
that can leak `/exit` into the shell prompt after Codex has already exited.
If Codex has already returned to a shell inside a dedicated
`AgentOrchestra-self-e2e-*` session, the helper may also clean that shell pane
and record `reason=dedicated_session_shell_cleanup`; it must not perform this
shell-pane cleanup in CAO, ToO, service-E2E, observer, or controller sessions.
For SelfE2E, this shell cleanup applies only to the recorded worker pane whose
tmux session name starts with `AgentOrchestra-self-e2e-`; do not use it for
CAO, ToO, observer, service-E2E controller, or ambiguous panes.
Prefer `AGENT_ORCHESTRA_TMUX_PANE` for the pane id; if the tool execution
environment does not expose it, resolve the pane from Agent state `tmux_target`
before forking. Do not fall back to a bare `tmux display-message` active-pane
lookup.

```sh
"${AGENT_ORCHESTRA_PYTHON:-python3}" -m agent_orchestra_minimal.self_exit \
  --pane "${AGENT_ORCHESTRA_TMUX_PANE}" \
  --submit-key "${AGENT_ORCHESTRA_TUI_SUBMIT_KEY:-C-m}" \
  --result-path "${AGENT_ORCHESTRA_ARTIFACT_DIR}/main-self-exit.json"
```

For a verified dedicated SelfE2E worker pane, append:

```sh
--allow-shell-cleanup-session-prefix AgentOrchestra-self-e2e- \
--cleanup-auxiliary-shells
```

The helper's result file is the self-exit evidence for generic non-SelfE2E
verification. Do not call `agent_orchestra_minimal.self_exit` directly with a
copied-runtime SelfE2E
`${AGENT_ORCHESTRA_EDIT_ROOT}/.tmp/self-improvement-e2e/main-self-exit*.json`
result path; the CLI rejects that path so MainAgent cannot skip copied-runtime
status readback. In SelfE2E, only the packaged finalizer writes the
copied-runtime result file under
`${AGENT_ORCHESTRA_EDIT_ROOT}/.tmp/self-improvement-e2e/`, beside the
copied-runtime `status` file. Evidence text alone is not sufficient.
Also write/read
`${AGENT_ORCHESTRA_EDIT_ROOT}/.tmp/self-improvement-e2e/active-main-session.json`
with the active SelfE2E MainAgent `pane` and `session_name` before relying on
the final result. The result JSON must match those fields exactly; a proof
session or later helper session is not valid evidence for the current MainAgent.
The result must show `closed: true`; `killed_pane: true` is acceptable only
after bounded `/exit` attempts were made and queued `/exit` text was cleared,
or when `reason=dedicated_session_shell_cleanup` proves the remaining shell pane
belonged to the dedicated SelfE2E session. With auxiliary cleanup enabled,
`auxiliary_shell_panes` records same-session shell panes that were cleaned. Do
not claim that MainAgent exited when the pane is still present, and do not leave
`/exit` or other queued text behind at a shell prompt.

When SelfE2E also requires the copied-runtime status file to become `done`
after current-session self-exit evidence exists, use the two-phase packaged
finalizer as the final tool action instead of `self_exit` directly. It records
`active-main-session.json`, runs the same self-exit procedure for the recorded
pane, writes `main-self-exit*.json`, then calls the status finalizer against the
already-finalized shared task file:

```sh
"${AGENT_ORCHESTRA_PYTHON:-python3}" -m agent_orchestra_minimal.self_e2e_finalizer \
  --pane "${AGENT_ORCHESTRA_TMUX_PANE}" \
  --submit-key "${AGENT_ORCHESTRA_TUI_SUBMIT_KEY:-C-m}" \
  --result-path "${AGENT_ORCHESTRA_EDIT_ROOT}/.tmp/self-improvement-e2e/main-self-exit.json" \
  --status-path "${AGENT_ORCHESTRA_EDIT_ROOT}/.tmp/self-improvement-e2e/status" \
  --task-file "${AGENT_ORCHESTRA_TASK_FILE}" \
  --allow-shell-cleanup-session-prefix AgentOrchestra-self-e2e- \
  --cleanup-auxiliary-shells
```

Do not rely on CAO cleanup, a post-exit Hook wake, or a separate proof session
to flip the copied-runtime status to `done`.
