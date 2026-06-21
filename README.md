# AgentOrchestra

[English](README.md) | [日本語](README.ja.md)

AgentOrchestra runs a project-improvement session with a user-facing MainAgent
and independent specialist ProfessionalAgents that inspect, edit, review, and
test from separate CLI sessions in tmux panes.

It ships two runtimes that share the same model — use whichever CLI you run:

- **`codex-o`** — Codex CLI runtime.
- **`claude-o`** — Claude Code CLI runtime.

The two coexist; pick one per session. The sections below describe `codex-o` in
detail; see [Claude Code Runtime (claude-o)](#claude-code-runtime-claude-o) for
the Claude Code runtime.

## Install

Codex CLI runtime:

```sh
nix profile add github:TheRealGo/AgentOrchestra#codex-o
```

Claude Code runtime:

```sh
nix profile add github:TheRealGo/AgentOrchestra#claude-o
```

After installation, `codex-o` and `claude-o` are available as normal commands.

## Requirements

- Codex CLI
- Nix
- tmux
- Python 3

`codex-o` uses tmux panes for the AgentTeam and Codex Stop Hooks for mechanical
re-kick behavior while work remains.

## Quick Start

Open the project you want AgentOrchestra to improve and run `codex-o`.

```sh
cd /path/to/project
codex-o
```

Then ask MainAgent what you want done. For example:

```text
SPEC.md を見て、このプロジェクトを改善してください。
改善点がなくなるまで改善し続けてください。
```

For a focused task:

```text
テストが落ちている原因を調査し、必要な修正を入れてください。
ProfessionalAgent にレビューさせてから完了報告してください。
```

## Running In tmux

If you want to watch the session from tmux directly:

```sh
cd /path/to/project
tmux new-session -s orchestra 'codex-o'
```

Attach from another terminal:

```sh
tmux attach -t orchestra
```

## Target Project

By default, the current directory is the target project:

```sh
cd /path/to/project
codex-o
```

You can also pass the target project explicitly:

```sh
codex-o /path/to/project
```

## What Happens

When a session starts, AgentOrchestra creates isolated launch material in a
durable run directory. Set `AGENT_ORCHESTRA_RUN_ROOT` to choose the parent
directory; otherwise AgentOrchestra uses a user state directory outside the
target project tree:

- a MainAgent workspace;
- clean `HOME` and `CODEX_HOME`;
- copied Skills and Stop Hook configuration;
- a shared task file;
- Agent state files;
- launch metadata for any ProfessionalAgents MainAgent creates.

MainAgent decides whether specialist ProfessionalAgents are needed for the task.
For non-trivial work, it can launch independent Codex CLI sessions for relevant
layers, send tasks through tmux, collect peer review, and retire those panes
when their work is accepted.
If a peer response is needed while the receiving pane is still busy, the
delivery helper can preserve that response in a run-scoped mailbox and drain it
after the receiver is input-ready. Later sends to the same pane automatically
try that drain before sending new text. A queued response is evidence that the
message was preserved, not accepted delivery; clean completion still requires
accepted drain evidence or an explicit unresolved disposition.

The runtime does not decide requirements or quality. Agents make those
judgments; the runtime only provides deterministic rails for launch, tmux
delivery, shared task state, and Stop Hook wake behavior.

## Completion State

The shared task file starts at `[status] done` only as the empty quiet baseline.
When a user task, discovery, implementation, or review begins, Agents record
open work in `[Backlog]`, `[InProgress]`, or `[InReview]` and set
`[status] progress`.

For open-ended improvement runs, MainAgent should finish only after open work is
empty, every `[Acceptance]` item is satisfied, out-of-scope, or deferred with
evidence, every `[Gates]` item is passed or explicitly non-applicable, and
every `[Candidates]` ledger item has an id, summary, completed disposition, and
evidence pointer. Acceptance or gate items marked `blocked` or `needs_user`
keep the run at `[status] progress` until the external action is resolved or
the item is explicitly moved out of scope. Accepted ProfessionalAgents are
marked `retired`, sent `/exit`, and their panes are verified or cleaned up
before completion is reported. A stale non-retired ProfessionalAgent state file
under the run `agents/` directory is a quiet-completion blocker.

Missing tools or environment are not a quiet finish condition. Agents are
expected to try alternate completion routes such as repository-native setup,
existing Docker compose, ephemeral env/cache directories, CLI/browser/screenshot
fallbacks, equivalent checks, or a smaller reproducible harness before asking
the user. If user input is truly required, the task evidence should name the
attempted routes and the exact credential, approval, network access, service,
hardware, or scope change needed.
Routine in-scope work is not user input. Ordinary edits, tests, dependency
installation into ephemeral/cache directories, dev-server or Docker compose
startup, pane recovery, bounded tool approval retries, and verification retries
should continue when they fit the active user permission and project policy. A
`needs_user` stop is reserved for concrete external action such as a credential,
approval, network access, service, hardware, physical device interaction,
account/provider setup, payment, production/public release approval,
destructive or irreversible action, legal/security judgment, or scope change.
Low-risk local E2E verification reruns, including browser matrix checks,
local simulator/iOS smoke checks, and mobile route or interactive evidence
reruns, are autonomous when they are scoped to the active project/run. Operator
approval that merely lets those checks proceed is recorded as an
AgentOrchestra autonomy defect, not as successful zero-issue evidence.
Requirement documents are resolved case-insensitively and by the user's actual
paths. A repo with `Spec.md` or `UI.md` must be treated the same as one with
`SPEC.md`; MainAgent searches for these files before planning or creating the
acceptance ledger.
When a browser, GUI, screenshot, or Quick Look route fails with sandbox-style
permission errors such as `MachPortRendezvous`, `Operation not permitted`,
`SIGABRT`, or sandbox initialization failure, the owning Agent retries that
necessary visual evidence command once with
`sandbox_permissions="require_escalated"` and a narrow justification before
recording the gate as blocked.
Browser install, launch, screenshot, Playwright script, and MCP/browser visual
actions must also have a strict outer wall-clock timeout for the whole route.
If that timeout fires or a browser launch hangs once, Agents preserve logs,
record the candidate or gate issue, and switch evidence routes or leave the
gate failed/blocked instead of starting another unbounded browser run.

For UI/E2E work, Agents record the live server identity in
`AGENT_ORCHESTRA_SERVER_MANIFEST` or equivalent evidence: base URL, port,
PID/PGID, and log path. Screenshots, API probes, and network logs must use that
same base URL, and visual gates include semantic assertions for the required UI
states, measured viewport evidence, artifact directory, and fit assertions
rather than relying on nonblank screenshots alone. Stale localhost ports,
requested/measured viewport mismatches, workspace-only MCP output, MCP approval
prompts left unresolved, and failed dev-server cleanup stay as gate or candidate
issues.
The same manifest and cleanup rule applies to auxiliary E2E services such as
fake LLM/API servers, local databases, queues, workers, file watchers, secondary
web servers, and harness listeners. If an unmanifested current-run listener was
not recorded with PID/PGID, port/base_url, log path, owner, and cleanup command,
the environment gate remains unresolved.

Cleanup is similarly scoped. Agents should remove only current-run resources
they created, such as launch-provided cache/artifact/env directories or this
run's Docker compose project. Unknown untracked files, supervisor status files,
and `result`/`result-*` symlinks are preserved or recorded as candidates, not
deleted to make the worktree look cleaner.
Unknown local artifacts stay outside current-run cleanup unless that run created
them; unknown local artifacts are not deleted merely to make status clean.
Helper process cleanup requires known process identity plus current-run or
recorded port ownership. Docker compose, container, network, and volume cleanup
requires the compose project or resource name to match the current run scope;
ambiguous resources are blocked or recorded as `needs_user` instead of being
removed speculatively.

For SelfE2E completion, the copied-runtime status file may reach `done` only
after the shared task file is finalized and the actual
`main-self-exit*.json` beside it proves `closed: true`, no CAO cleanup, and
auxiliary cleanup scoped to the same dedicated SelfE2E session with
`session_gone: true`. That JSON must also match the recorded active MainAgent
identity in
`.tmp/self-improvement-e2e/active-main-session.json` by exact `pane` and
`session_name`; a separate proof or final helper session is not valid evidence
for the active run. The packaged
`agent_orchestra_minimal.self_e2e_finalizer` is the atomic handoff for this
ordering: it records the active binding, runs self-exit, writes the result JSON,
and only then writes/reads the copied-runtime status as `done`.
The finalized SelfE2E ledger must also include explicit evidence for
multi-viewpoint search, ProfessionalAgent review, ServiceE2E intake/replay,
standard verification, final candidate sweep, zero unresolved
Acceptance/Gates/Candidates/open work, and finalizer status readback.

## Target And Edit Roots

The requested target project remains the Agent's scoped project data. When that
target is nested inside a larger Git worktree, AgentOrchestra does not grant the
parent Git root as an editable access root by default. Agents use
`AGENT_ORCHESTRA_TARGET_PROJECT` and `AGENT_ORCHESTRA_EDIT_ROOT` for the same
scoped target unless the operator explicitly opts into the legacy parent-root
mode with `AGENT_ORCHESTRA_INCLUDE_PARENT_GIT_ROOT=1` for a run that truly must
edit from the larger repository root.

## Check Your Environment

Use `doctor` when you want to confirm local prerequisites before starting a
session:

```sh
nix run github:TheRealGo/AgentOrchestra#agent-orchestra -- doctor --target-project /path/to/project
```

To include a disposable Codex TUI tmux transport probe:

```sh
nix run github:TheRealGo/AgentOrchestra#agent-orchestra -- doctor \
  --target-project /path/to/project \
  --tui-transport
```

To validate a shared task file before deciding a run is quiet:

```sh
nix run github:TheRealGo/AgentOrchestra#agent-orchestra -- doctor \
  --target-project /path/to/project \
  --task-file "$AGENT_ORCHESTRA_RUN_DIR/tasks.ini"
```

To inspect inherited MCP configuration without printing secret env values:

```sh
nix run github:TheRealGo/AgentOrchestra#agent-orchestra -- doctor \
  --target-project /path/to/project \
  --mcp
```

To include Codex CLI's own machine-readable diagnostics:

```sh
nix run github:TheRealGo/AgentOrchestra#agent-orchestra -- doctor \
  --target-project /path/to/project \
  --codex-doctor
```

`--codex-doctor` waits up to 60 seconds by default because recent Codex CLI
versions include broader local inventory checks. To inspect the Codex feature
flags AgentOrchestra relies on:

```sh
nix run github:TheRealGo/AgentOrchestra#agent-orchestra -- doctor \
  --target-project /path/to/project \
  --codex-features
```

When `codex features list` reports `prevent_idle_sleep`, AgentOrchestra adds
`--enable prevent_idle_sleep` to Agent launches so long-running teams are less
likely to pause during system idle sleep. Set
`AGENT_ORCHESTRA_DISABLE_PREVENT_IDLE_SLEEP=1` to opt out.

## Updating

```sh
nix profile upgrade codex-o   # or: nix profile upgrade claude-o
```

If you installed under a different profile name, list your profile entries with:

```sh
nix profile list
```

## Development

This repository also exposes local Nix apps and checks for contributors.

Run from a checkout:

```sh
nix run .#codex-o
nix run .#agent-orchestra -- doctor --target-project .
```

Standard verification:

```sh
python3 -m unittest discover -s tests
find .codex/agent_orchestra_minimal .codex/hooks tests \
  -name '*.py' -print0 | xargs -0 python3 -m py_compile
git diff --check
nix flake check --no-build
nix build .#checks.x86_64-linux.source-contract
```

`unittest` is the standard Python test runner for this repository. Do not
substitute `pytest` unless a task explicitly adds and justifies that dependency.

For generated-copy or untracked-fixture verification, use path-form Nix so the
checked tree is the visible working directory, for example `nix flake check
--no-build path:$PWD` and
`nix build path:$PWD#checks.$system.source-contract`.

Use the system-specific check name for your platform when needed, such as
`aarch64-darwin`, `x86_64-darwin`, `aarch64-linux`, or `x86_64-linux`.

## Claude Code Runtime (claude-o)

This repository also ships a Claude Code runtime alongside the Codex one above.
`claude-o` starts the Claude Code CLI with AgentOrchestra: the same MainAgent
plus independent specialist ProfessionalAgents model, but each Agent runs as a
Claude Code session in a tmux pane instead of a Codex CLI session. The Codex
`codex-o` runtime is unchanged; the two coexist.

### Requirements

- Claude Code CLI
- Nix
- tmux
- Python 3

### Authentication

The Claude Code runtime **requires** a credential: without one, every Agent
starts "Not logged in" and cannot do any work. Unlike Codex — which copies its
file-based `auth.json` into the isolated home automatically — Claude Code on
macOS keeps credentials in the login Keychain, and the isolated
`CLAUDE_CONFIG_DIR` each Agent runs under does not read the Keychain, so a normal
interactive `claude` login in your shell does not carry over. You must supply a
credential explicitly.

Export one credential before `claude-o`: the runtime writes it into each Agent's
`env.sh` (mode `0600`), and every Agent launch — MainAgent and each
ProfessionalAgent pane it spawns — sources `env.sh`, so they all authenticate
from that single credential without any per-pane setup.

```sh
claude setup-token                     # prints a long-lived OAuth token
export CLAUDE_CODE_OAUTH_TOKEN=<token>  # or: export ANTHROPIC_API_KEY=<key>
cd /path/to/project && claude-o
```

If you start `claude-o` without a discoverable credential (no exported token and
no copyable `.credentials.json`), it prints a warning and still opens the
session — but the Agents stay "Not logged in" and cannot work until you provide
one. The runtime never extracts Keychain secrets; supplying the credential is a
required deployment step.

### Quick Start

Open the project you want to improve and run `claude-o`:

```sh
cd /path/to/project && claude-o
```

From a checkout you can also run the local Nix apps:

```sh
nix run .#claude-o
nix run .#agent-orchestra-claude -- doctor --target-project .
```

### Verification

```sh
python3 -m unittest discover -s tests_claude
find .claude/agent_orchestra_minimal .claude/hooks tests_claude \
  -name '*.py' -print0 | xargs -0 python3 -m py_compile
nix build .#checks.x86_64-linux.claude-source-contract
```

Use the system-specific check name for your platform when needed, such as
`aarch64-darwin`, `x86_64-darwin`, `aarch64-linux`, or `x86_64-linux`.

### More Detail (Claude Code)

- `SPEC.claude.md` specifies the Claude Code runtime as a delta over `SPEC.md`.
- `.claude/agent_orchestra_minimal/` contains the Claude Code runtime.
- `.claude/skills/` contains the Agent-facing operating procedures.

## More Detail

- `SPEC.md` defines the runtime and AgentTeam contract.
- `layers/` contains the specialist layer perspectives used by
  ProfessionalAgents.
- `.codex/agent_orchestra_minimal/` contains the minimal runtime.
- `.codex/skills/` contains Agent-facing operating procedures.
