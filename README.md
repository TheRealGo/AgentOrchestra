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
temporary run directory:

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

The runtime does not decide requirements or quality. Agents make those
judgments; the runtime only provides deterministic rails for launch, tmux
delivery, shared task state, and Stop Hook wake behavior.

## Completion State

The shared task file starts at `[status] done` only as the empty quiet baseline.
When a user task, discovery, implementation, or review begins, Agents record
open work in `[Backlog]`, `[InProgress]`, or `[InReview]` and set
`[status] progress`.

For open-ended improvement runs, MainAgent should finish only after open work is
empty and every `[Candidates]` ledger item has an id, summary, completed
disposition, and evidence pointer. Accepted ProfessionalAgents are marked
`retired`, sent `/exit`, and their panes are verified or cleaned up before
completion is reported.

## Target And Edit Roots

The requested target project remains the Agent's scoped project data. When that
target is nested inside a larger Git worktree, launch material also grants the
worktree root as an editable access root so Agents can run `git status`, patch
tracked files, and verify from the repository root without widening the user
request. Agents use `AGENT_ORCHESTRA_TARGET_PROJECT` for the requested scope and
`AGENT_ORCHESTRA_EDIT_ROOT` for git, patching, and verification commands.

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
  --task-file /private/tmp/agent-orchestra/.../tasks.ini
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
