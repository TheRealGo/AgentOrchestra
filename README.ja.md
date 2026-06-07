# codex-o

[English](README.md) | [日本語](README.ja.md)

`codex-o` は Codex CLI を AgentOrchestra モードで起動するコマンドです。
MainAgent と複数の独立した ProfessionalAgent を使い、プロジェクトの調査、
実装、レビュー、検証を分担しながら改善を進めます。

使う場所は、改善したいプロジェクトのディレクトリです。MainAgent は
ユーザーとの窓口になり、ProfessionalAgent は別々の Codex CLI セッション
として tmux pane 上で動きます。

## インストール

```sh
nix profile add github:TheRealGo/AgentOrchestra#codex-o
```

インストール後は、`codex-o` を通常のコマンドとして使えます。

## 必要なもの

- Codex CLI
- Nix
- tmux
- Python 3

`codex-o` は AgentTeam 用の tmux pane と、未完了作業が残っているときの
機械的な再起動判定に Codex Stop Hook を使います。

## クイックスタート

改善したいプロジェクトへ移動して `codex-o` を実行します。

```sh
cd /path/to/project
codex-o
```

起動したら、MainAgent にやってほしいことを伝えます。例:

```text
SPEC.md を見て、このプロジェクトを改善してください。
改善点がなくなるまで改善し続けてください。
```

範囲を絞った依頼もできます。

```text
テストが落ちている原因を調査し、必要な修正を入れてください。
ProfessionalAgent にレビューさせてから完了報告してください。
```

## tmux で見る

tmux セッションとして起動して動きを見たい場合:

```sh
cd /path/to/project
tmux new-session -s orchestra 'codex-o'
```

別のターミナルから attach できます。

```sh
tmux attach -t orchestra
```

## 対象プロジェクト

通常は、現在のディレクトリが改善対象になります。

```sh
cd /path/to/project
codex-o
```

対象プロジェクトを明示することもできます。

```sh
codex-o /path/to/project
```

## 起動すると何が起きるか

AgentOrchestra は一時ディレクトリに、Agent ごとの隔離された起動素材を作り
ます。

- MainAgent 用 workspace
- clean な `HOME` と `CODEX_HOME`
- コピーされた Skills と Stop Hook 設定
- 共有タスクファイル
- Agent state ファイル
- MainAgent が作る ProfessionalAgent 用の起動メタデータ

MainAgent は、依頼内容に応じて専門の ProfessionalAgent が必要かを判断しま
す。非自明な作業では、関連する layer の独立 Codex CLI セッションを起動し
ます。tmux 経由でタスクを送り、peer review を集め、受け入れた pane を退役
させます。

ランタイムは要件や品質を判断しません。判断するのは Agent です。
ランタイムは、起動、tmux 配送、共有タスク状態、Stop Hook wake のための
決定的な安全柵だけを提供します。

## 完了状態

共有タスクファイルの `[status] done` は、まだ open work がない空の静かな
初期状態を表すだけです。ユーザー依頼、調査、実装、レビューが始まったら、
Agent は `[Backlog]`、`[InProgress]`、`[InReview]` に open work を記録し、
`[status] progress` に切り替えます。

改善点がなくなるまで続ける run では、MainAgent は open work が空で、
`[Candidates]` ledger の各項目に id、summary、完了 disposition、evidence
pointer が入っている場合だけ完了できます。受け入れ済みの ProfessionalAgent
は `retired` にし、`/exit` を送り、pane が閉じたことを確認または cleanup
してから完了報告します。

## Target と edit root

ユーザーが指定した target project は、Agent の要求スコープを表す project
data のままです。その target がより大きな Git worktree の内側にある場合、
launch material は worktree root も editable access root として渡します。
これにより、Agent はユーザー要求を広げずに repository root から `git
status`、patch、検証を実行できます。Agent は要求スコープには
`AGENT_ORCHESTRA_TARGET_PROJECT` を使い、git、patch、検証には
`AGENT_ORCHESTRA_EDIT_ROOT` を使います。

## 環境チェック

起動前にローカル前提条件を確認したい場合は `doctor` を使います。

```sh
nix run github:TheRealGo/AgentOrchestra#agent-orchestra -- doctor \
  --target-project /path/to/project
```

Codex TUI への tmux transport probe まで確認する場合:

```sh
nix run github:TheRealGo/AgentOrchestra#agent-orchestra -- doctor \
  --target-project /path/to/project \
  --tui-transport
```

run が quiet か判断する前に shared task file を検査する場合:

```sh
nix run github:TheRealGo/AgentOrchestra#agent-orchestra -- doctor \
  --target-project /path/to/project \
  --task-file /private/tmp/agent-orchestra/.../tasks.ini
```

Codex CLI 自体の machine-readable diagnostics も確認する場合:

```sh
nix run github:TheRealGo/AgentOrchestra#agent-orchestra -- doctor \
  --target-project /path/to/project \
  --codex-doctor
```

`--codex-doctor` の既定 timeout は 60 秒です。最近の Codex CLI は local
inventory check が広がっているためです。AgentOrchestra が使う Codex
feature flag を確認する場合:

```sh
nix run github:TheRealGo/AgentOrchestra#agent-orchestra -- doctor \
  --target-project /path/to/project \
  --codex-features
```

`codex features list` に `prevent_idle_sleep` がある場合、AgentOrchestra は
長時間 AgentTeam が system idle sleep で止まりにくいように Agent 起動へ
`--enable prevent_idle_sleep` を追加します。無効化するには
`AGENT_ORCHESTRA_DISABLE_PREVENT_IDLE_SLEEP=1` を設定します。

## 更新

```sh
nix profile upgrade codex-o
```

別名で profile に入れている場合は、次のコマンドで確認できます。

```sh
nix profile list
```

## 開発

このリポジトリの checkout からは、local Nix app と check を使えます。

```sh
nix run .#codex-o
nix run .#agent-orchestra -- doctor --target-project .
```

標準の検証:

```sh
python3 -m unittest discover -s tests
find .codex/agent_orchestra_minimal .codex/hooks tests \
  -name '*.py' -print0 | xargs -0 python3 -m py_compile
git diff --check
nix flake check --no-build
nix build .#checks.x86_64-linux.source-contract
```

このリポジトリの標準 Python テストランナーは `unittest` です。タスクで依存追加と
理由が明示されない限り、`pytest` に置き換えないでください。

generated-copy や未追跡 fixture を検証するときは、見えている作業ツリーをそのまま
検査するために path-form Nix を使います。例: `nix flake check --no-build
path:$PWD` と `nix build path:$PWD#checks.$system.source-contract`。

環境に合わせて、`x86_64-linux` は `aarch64-darwin`、`x86_64-darwin`、
`aarch64-linux`、`x86_64-linux` などに置き換えてください。

## 詳細

- `SPEC.md` は runtime と AgentTeam の契約を定義します。
- `layers/` には ProfessionalAgent が使う専門 layer の観点があります。
- `.codex/agent_orchestra_minimal/` には最小 runtime があります。
- `.codex/skills/` には Agent 向けの操作手順があります。
