# agent-orchestra Claude Code Runtime Specification

This document specifies the **Claude Code** runtime for agent-orchestra. It is a
delta over `SPEC.md`: the organizational model, AgentTeam roles, shared task
file, candidate ledger, re-kick conditions, and completion philosophy described
in `SPEC.md` are unchanged and authoritative. This file defines only what is
specific to running the runtime on the Claude Code CLI instead of the Codex CLI.

The two runtimes coexist in this repository:

- `.codex/` + `tests/` — the original Codex runtime (`codex-o`). Unchanged.
- `.claude/` + `tests_claude/` — the Claude Code runtime (`claude-o`).
- `layers/` — shared specialist perspectives, used by both. Runtime-neutral.

The Claude Code runtime keeps the same value: MainAgent stays user-facing, layer
specialist ProfessionalAgents start from isolated instructions in tmux panes,
they consult through tmux, a shared task file is the deterministic Hook state,
and a Stop Hook re-kicks stopped Agents while in-scope work remains.

## Launcher

`claude-o` starts a MainAgent Claude Code session for the target project:

```sh
cd /path/to/project
claude-o
```

It prepares isolated launch material and `exec`s `claude` from the isolated
workspace. Requirements: Claude Code CLI, Nix, tmux, Python 3.

## Codex → Claude Code Mapping

| Concept | Codex runtime | Claude Code runtime |
| --- | --- | --- |
| CLI binary | `codex` | `claude` |
| Launcher | `codex-o` | `claude-o` |
| Config home env | `CODEX_HOME` | `CLAUDE_CONFIG_DIR` |
| Startup instruction file | generated `workspace/AGENTS.md` | generated `workspace/CLAUDE.md` |
| Profile / trust / hooks | `agent-orchestra.config.toml` + `--profile-v2` | `settings.json` in `CLAUDE_CONFIG_DIR` |
| Approval / sandbox | `--ask-for-approval never --sandbox workspace-write` | `--permission-mode bypassPermissions` (default; one-time launch gate accepted via tmux) — no sandbox |
| Workspace selection | `--cd WORKSPACE` | chdir into the workspace (no `--cd` flag) |
| Target access | `--add-dir TARGET` | `--add-dir TARGET` + `--add-dir RUN_DIR` (run-dir for shared task/state files) |
| Project trust | `trust_level = "trusted"` | pre-seeded `.claude.json` `hasTrustDialogAccepted` |
| Auth | copied `auth.json` | forwarded token env, or copied `.credentials.json` (isolated config does not read the Keychain) |
| In-session helper | Codex-native SubAgent | Claude Code subagent (Task/Agent tool, `.claude/agents`) |
| One-shot mode (rejected) | `codex exec` | `claude -p` / `--print` |

The `AGENT_ORCHESTRA_*` environment contract and the `C-m` default TUI submit
key (`AGENT_ORCHESTRA_TUI_SUBMIT_KEY`) are unchanged.

## Launch Argv

The runtime launches:

```sh
claude --add-dir "$TARGET_PROJECT" --add-dir "$RUN_DIR" --permission-mode "$MODE"
```

- Claude Code launches in the current working directory, so isolation comes from
  chdir into the generated workspace (`os.chdir` for MainAgent; `cd
  "$AGENT_DIR/workspace"` in the pane for ProfessionalAgents), not a `--cd` flag.
- The run directory is added as a second `--add-dir` so the shared `tasks.ini`
  and per-agent `state.json` (at the run-dir root, outside the workspace) are
  readable and editable without a per-file permission prompt. This does not break
  instruction isolation: verified live that a nested `CLAUDE.md` under an added
  directory is not loaded as startup instruction — only the cwd workspace
  `CLAUDE.md` is — and `_reject_parent_claude_md` still guards cwd ancestors.
- The isolated `CLAUDE_CONFIG_DIR` carries the generated `settings.json` Stop
  Hook and the trust seed; this replaces Codex `--profile-v2`.
- `$MODE` defaults to `bypassPermissions` and is overridable with
  `AGENT_ORCHESTRA_PERMISSION_MODE`. `bypassPermissions` is required because the
  team edits arbitrary repo paths (including `.claude/...`) and runs shell commands
  unattended, and no scoped allow-list reliably covers that (see Generated
  settings.json). It stops at a one-time "Yes, I accept" Bypass Permissions warning
  gate on launch (the trust seed does not suppress it), which the operator / launch
  skill accepts with a single keystroke (`Down`, `Enter`) after launch, before the
  task is delivered. `acceptEdits` is available as an override but only auto-accepts
  edits inside the cwd workspace, so it is not unattended for target edits.
- The launcher must not append an initial prompt: a Claude Code positional arg is
  the first user message, and a synthetic first prompt is forbidden by `SPEC.md`.
  Extra argv may only be option-shaped; allowed: `--model` and `--fallback-model`
  (options taking a value), `--verbose` (flag). Boundary options that must not
  be overridden: `--add-dir`, `--permission-mode`, `--settings`,
  `--setting-sources`, `--dangerously-skip-permissions`,
  `--allow-dangerously-skip-permissions`, `--system-prompt`,
  `--append-system-prompt`, `--agents`, `-p`/`--print`.

## Generated settings.json

The runtime generates `settings.json` (replacing the Codex TOML config). Claude
Code has no per-hash hook trust model, so there is no trusted-hash field:

```json
{
  "hooks": {
    "Stop": [
      { "hooks": [ { "type": "command", "command": "python3 <abs hook path>" } ] }
    ]
  },
  "permissions": { "defaultMode": "bypassPermissions" }
}
```

The Stop Hook command embeds an absolute, shell-quoted path so it does not depend
on `$CLAUDE_CONFIG_DIR` expansion at hook run time.

The team must edit arbitrary repo paths — including dot-directories like
`.claude/...` — and run shell commands fully unattended. No scoped allow-list
covers that: `acceptEdits` only auto-accepts edits inside the cwd workspace (and
prompts for the `--add-dir` target and the run-dir `tasks.ini`); a bare `Edit`
allow rule is inert; and a path-glob allow rule (`Edit(//target/**)`) was verified
to miss dot-directories, so the team stalled on the first `.claude/...` edit.
`bypassPermissions` removes the whole class of permission prompts in one move, so
it is the default. The cost is a one-time launch warning gate (the trust seed does
not suppress it), accepted with a single keystroke after launch.

This is **looser than the Codex posture**: Codex paired `--ask-for-approval never`
with `--sandbox workspace-write`, which confined writes; `bypassPermissions` has no
sandbox, so the boundary is the isolated `HOME` / `CLAUDE_CONFIG_DIR` / the two
`--add-dir` roots plus the operator's accepted risk (Claude Code's own warning
recommends a sandboxed VM/container). Operators who want per-action approval can
set `AGENT_ORCHESTRA_PERMISSION_MODE=acceptEdits`, accepting that target edits will
prompt and the run is no longer unattended.

## Project Trust Seed

Claude Code stops at a per-directory trust dialog ("Is this a project you created
or one you trust?") for any untrusted folder, which blocks unattended launch.
`--dangerously-skip-permissions` does not bypass it. The runtime pre-seeds the
trust disposition into `.claude.json` in both the isolated `HOME` and
`CLAUDE_CONFIG_DIR`:

```json
{ "hasCompletedOnboarding": true,
  "projects": { "<abs workspace>": {
      "hasTrustDialogAccepted": true,
      "hasCompletedProjectOnboarding": true,
      "projectOnboardingSeenCount": 1,
      "allowedTools": [] } } }
```

This is the Claude Code analog of the Codex `trust_level = "trusted"` project
entry. Verified live: with the seed in `CLAUDE_CONFIG_DIR/.claude.json`, a launch
into the isolated config reaches the composer with no trust dialog.

## Authentication

Codex copies a file-based `auth.json` into the isolated `CODEX_HOME`. Claude Code
has no equivalent on macOS: credentials live in the login Keychain, not a file,
and the isolated `CLAUDE_CONFIG_DIR` does not read them. This was verified
empirically with `claude -p`: a launch into a fresh config reports "Not logged
in" even when `HOME` is the real home and the isolated `.claude.json` carries a
copied `oauthAccount` — seeding the account does not make the isolated config
consult the Keychain. (The default `~/.claude` config authenticates from the
Keychain normally; only the override stops consulting it.) The runtime copies
`.credentials.json` into the isolated config when one exists (file-based auth,
for example on Linux or after `claude setup-token`), but it cannot and must not
extract Keychain secrets.

To make one credential reach every Agent, the runtime forwards the auth
environment variables it finds at launch — `CLAUDE_CODE_OAUTH_TOKEN`,
`ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_BASE_URL` — into the
Agent environment and into `env.sh`, which ProfessionalAgent panes source.
`env.json` and `env.sh` are written `0o600` because they can now carry a secret.

A Claude Code Agent cannot do any work without a credential — it starts "Not
logged in" — so on a macOS Keychain-only setup the operator must supply auth
once, and the runtime then propagates it to the whole team:

- run `claude setup-token` once and export `CLAUDE_CODE_OAUTH_TOKEN` (or export
  `ANTHROPIC_API_KEY`) before `claude-o`. MainAgent inherits it directly, and
  each ProfessionalAgent pane sources the forwarded `env.sh`, so one exported
  credential authenticates the whole team without per-pane setup. `/login` only
  authenticates the single isolated `CLAUDE_CONFIG_DIR` it runs in, so it does
  not propagate to the other Agents and is not a team-wide path.

When neither a forwarded token nor a copyable `.credentials.json` is discoverable
at launch, `claude-o` prints a one-time warning naming the fix (run `claude
setup-token`, export `CLAUDE_CODE_OAUTH_TOKEN`, re-run). The launch does not
abort, but every Agent stays "Not logged in" and cannot work until a credential
is supplied, so a credential is effectively required, not optional.

This is a deployment prerequisite, not a runtime defect: the runtime forwards the
credential the platform exposes; it cannot and must not extract Keychain secrets.

## Instruction Isolation

Isolation prevents startup-instruction contamination, not access:

- the generated `workspace/CLAUDE.md` is the only startup instruction surface;
- `HOME` and `CLAUDE_CONFIG_DIR` are isolated so global/user `CLAUDE.md` and
  settings do not load;
- the workspace must live outside the target tree and must not have an ancestor
  `CLAUDE.md`, because Claude Code discovers `CLAUDE.md` up the directory tree;
- the target project is reachable as data through `--add-dir`; a target root
  `CLAUDE.md` is data/evidence, not startup instruction.
- the run directory is reachable as data through a second `--add-dir` (for the
  shared task/state files); the nested per-agent `workspace/CLAUDE.md` files
  under it are not loaded as startup instruction — only the cwd workspace
  `CLAUDE.md` is — so adding the run dir does not contaminate instructions.

## Stop Hook

Claude Code delivers Stop Hook context as JSON on stdin (`session_id`,
`transcript_path`, `cwd`, `hook_event_name`, `stop_hook_active`). The hook reads
and drains stdin, then runs the same mechanical re-kick decision from the
launch-provided `AGENT_ORCHESTRA_*` environment and the shared task/state files.
It exits 0 and never blocks Claude Code from stopping; re-kick is delivered as an
external tmux wake, not as a native blocking decision. Native blocking cannot
wake a different pane (the ProfessionalAgent → Main fallback), so the tmux wake
is retained.

## Wake Delivery

The Stop Hook runs while Claude Code is still blocked on that same hook, so a
poll-and-confirm send would deadlock. The wake is therefore a fire-and-forget
`load-buffer` + `paste-buffer` followed by several submit-key presses spaced a
second apart: the keys land in the tmux input queue and Claude Code processes
them once it returns to its idle composer. This mirrors the proven self-exit
pattern where the paste arrives but the submit only takes effect after the active
turn yields back to the TUI. The fixed wake payload is unchanged:

```text
runtime_wake
source=hook
user_instruction=false
```

The payload is reasonless by design (the Hook is a mechanical re-kick device, not
a supervisor that explains itself), and both this payload and the candidate-ledger
logic (`candidate_ledger.py`) are byte-identical to the Codex runtime. A
consequence both runtimes share: a near-miss `[Candidates]` disposition (a colon
or bare word instead of `disposition=<completed>`, an unrecognized value, a
duplicated field key, or a missing `summary=`/`evidence=`) stays unresolved, so a
`done` task file re-kicks forever while the woken agent reports "no open work".
This Claude port keeps the shared deterministic core byte-identical to Codex and
recovers convergence in the runtime-specific guidance layer: the
`agent-orchestra-task-file` skill and the main/common startup templates instruct
the agent, when woken with no open Backlog/InProgress/InReview work, to audit
`[Candidates]` and fix the malformed disposition rather than re-report and stop.

Agent-to-Agent delivery (MainAgent → ProfessionalAgent pane and peer-to-peer) is
sent from a separate process and is poll-confirmed against the target pane, so it
keeps the send/capture/retry contract.

## Claude Code TUI Markers

Delivery confirmation reads the target pane with `tmux capture-pane`. The markers
below are captured empirically from Claude Code v2.1.x and may need adjustment
across TUI versions:

- composer / user-message line prefix: `❯`;
- working / output: assistant and tool output lines begin with `⏺`; the working
  and completion status line begins with a rotating spinner glyph (for example
  `✻ Frolicking…` or `✻ Baked for 10s`); `esc to interrupt` appears while busy;
- a message still held on the `❯` composer line with no spinner is queued, not
  delivered;
- pane identity for probes uses `pane_title` containing `Claude Code`;
  `pane_current_command` is unreliable for Claude Code and is not used.

## Completion Criteria

The Claude Code runtime is acceptable when `tests_claude` and live tmux/Claude
Code E2E evidence show the same behavior `SPEC.md` requires, with the Claude Code
launch contract above:

- startup instruction surface is the generated `CLAUDE.md`, not target root
  `CLAUDE.md` or incidental ancestor files;
- the launch argv uses `--add-dir` and `--permission-mode`, never `--cd`, an
  initial prompt, or `-p`/`--print`;
- `settings.json` registers the Stop Hook with an absolute command path and no
  trust-hash field;
- the trust seed is written so unattended launch does not stop at the trust
  dialog;
- the Stop Hook reads stdin, decides re-kick from task/state, and dispatches a
  tmux wake while open work remains; it stays quiet after `status=done` with no
  open work and completed `[Candidates]` dispositions;
- verification uses `python3 -m unittest discover -s tests_claude`,
  `python3 -m py_compile` over `.claude` runtime Python, `git diff --check`, and
  the Nix `claude-source-contract` check;
- runtime code stays small, mechanical, and responsibility-limited (soft 100,
  hard 300 lines per file).
```
