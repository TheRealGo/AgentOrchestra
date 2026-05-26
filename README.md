# codex-o

[English](README.md) | [日本語](README.ja.md)

`codex-o` starts Codex CLI with AgentOrchestra: a small runtime for running a
project-improvement session with a MainAgent and independent specialist
ProfessionalAgents.

Use it from the project you want to improve. MainAgent stays user-facing, while
ProfessionalAgents can inspect, edit, review, and test from separate Codex CLI
sessions in tmux panes.

## Install

```sh
nix profile add github:TheRealGo/AgentOrchestra#codex-o
```

After installation, `codex-o` is available as a normal command.

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

## Updating

```sh
nix profile upgrade codex-o
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

Use the system-specific check name for your platform when needed, such as
`aarch64-darwin`, `x86_64-darwin`, `aarch64-linux`, or `x86_64-linux`.

## More Detail

- `SPEC.md` defines the runtime and AgentTeam contract.
- `layers/` contains the specialist layer perspectives used by
  ProfessionalAgents.
- `.codex/agent_orchestra_minimal/` contains the minimal runtime.
- `.codex/skills/` contains Agent-facing operating procedures.
