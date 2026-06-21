# AgentOrchestra

[English](README.md) | [日本語](README.ja.md)

AgentOrchestra は、ユーザーとの窓口になる MainAgent と、複数の独立した
専門 ProfessionalAgent を使って、プロジェクトの調査・実装・レビュー・検証を
分担しながら改善を進めるランタイムです。ProfessionalAgent は別々の CLI
セッションとして tmux pane 上で動きます。

同じモデルを共有する 2 つのランタイムを同梱しており、使う CLI に応じて
どちらかを選びます。

- **`codex-o`** — Codex CLI ランタイム
- **`claude-o`** — Claude Code CLI ランタイム

両者は共存し、セッションごとにどちらかを使います。以下は `codex-o` の詳細で、
Claude Code ランタイムは [Claude Code ランタイム (claude-o)](#claude-code-ランタイム-claude-o) を参照してください。

## インストール

Codex CLI ランタイム:

```sh
nix profile add github:TheRealGo/AgentOrchestra#codex-o
```

Claude Code ランタイム:

```sh
nix profile add github:TheRealGo/AgentOrchestra#claude-o
```

インストール後は、`codex-o` と `claude-o` を通常のコマンドとして使えます。

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

AgentOrchestra は永続的な run directory に、Agent ごとの隔離された起動素
材を作ります。親ディレクトリは `AGENT_ORCHESTRA_RUN_ROOT` で指定でき、省
略時は対象プロジェクト外のユーザー state directory を使います。

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
`[Acceptance]` の各項目が satisfied / out-of-scope / deferred のいずれかで
evidence 付き、`[Gates]` の各項目が passed または明示的な non-applicable、
さらに
`[Candidates]` ledger の各項目に id、summary、完了 disposition、evidence
pointer が入っている場合だけ完了できます。Acceptance/Gates の
blocked/needs_user は外部アクション待ちの未完了状態であり、残っている間は
`[status] progress` のままです。受け入れ済みの ProfessionalAgent
は `retired` にし、`/exit` を送り、pane が閉じたことを確認または cleanup
してから完了報告します。run の `agents/` directory 配下に stale な
non-retired ProfessionalAgent state file が残っている場合も、quiet completion
の blocker です。

ツールや環境が足りないだけでは静かに終了できません。Agent は repo 標準手順、
既存 Docker compose、ephemeral env/cache、CLI/browser/screenshot fallback、
同等の検証、または小さな再現ハーネスなど、完成に向かう別経路を試してから
ユーザーに依頼します。本当にユーザー入力が必要な場合は、試した経路と、
必要な credential、approval、network access、service、hardware、scope 変更を
task evidence に具体的に残します。
通常の範囲内作業はユーザー入力ではありません。通常の編集、テスト、ephemeral
env/cache への依存導入、dev server や Docker compose の起動、pane 復旧、
bounded な tool approval retry、verification retry は、現在のユーザー許可と
project policy に収まる限り Agent が続行します。`needs_user` で止めるのは、
credential、approval、network access、service、hardware、物理 device 操作、
account/provider 設定、payment、本番/公開 release 承認、破壊的または不可逆な
操作、法務/安全判断、scope 変更など、具体的な外部アクションが必要な場合だけです。
要件文書は大文字小文字を区別せず、ユーザーが示した実際の path を優先して
解決します。`Spec.md` や `UI.md` がある repo は `SPEC.md` と同じように扱い、
MainAgent は計画や acceptance ledger 作成の前にそれらを探索して読みます。
Browser install、launch、screenshot、Playwright script、MCP/browser visual
action は、経路全体に strict な outer wall-clock timeout を設定します。
timeout したり browser launch が一度 hang した場合、Agent は log を保存し、
candidate または gate issue として記録し、別の evidence route に切り替えるか
gate failed/blocked として残します。unbounded な browser retry は行いません。

UI/E2E では、Agent は `AGENT_ORCHESTRA_SERVER_MANIFEST` または同等の evidence
に live server の base URL、port、PID/PGID、log path を残します。screenshot、
API probe、network log は同じ base URL を使い、visual gate には単に非 blank な
画像だけでなく、要求された UI 状態の semantic assertion、実測 viewport、
artifact directory、fit assertion を含めます。古い localhost port、
要求/実測 viewport の不一致、workspace に残っただけの MCP 出力、未解決の
MCP approval prompt、dev server cleanup 失敗は gate または candidate issue
として残ります。
同じ manifest/cleanup ルールは fake LLM/API server、local database、queue、
worker、file watcher、secondary web server、harness listener などの補助
E2E service にも適用します。current-run listener が PID/PGID、port/base URL、
log path、owner、cleanup command とともに記録されていなければ、environment
gate は未解決のままです。

cleanup も現在 run が作ったものに限定します。launch-provided cache/artifact/env
directory やその run の Docker compose project は片付けてよい一方で、不明な
untracked file、supervisor status file、`result` / `result-*` symlink は
worktree を綺麗に見せる目的で削除せず、candidate/evidence として扱います。

## Target と edit root

ユーザーが指定した target project は、Agent の要求スコープを表す project
data のままです。その target がより大きな Git worktree の内側にある場合でも、
AgentOrchestra はデフォルトでは親 Git root を editable access root として渡し
ません。通常は `AGENT_ORCHESTRA_TARGET_PROJECT` と
`AGENT_ORCHESTRA_EDIT_ROOT` は同じ scoped target を指します。より大きな
repository root から編集する必要が本当にある run だけ、operator が明示的に
`AGENT_ORCHESTRA_INCLUDE_PARENT_GIT_ROOT=1` を指定して legacy parent-root mode
へ opt-in します。

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
  --task-file "$AGENT_ORCHESTRA_RUN_DIR/tasks.ini"
```

secret env 値を出力せずに継承 MCP 設定を確認する場合:

```sh
nix run github:TheRealGo/AgentOrchestra#agent-orchestra -- doctor \
  --target-project /path/to/project \
  --mcp
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
nix profile upgrade codex-o   # claude-o の場合: nix profile upgrade claude-o
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

## Claude Code ランタイム (claude-o)

このリポジトリは、上記の Codex ランタイムに加えて Claude Code ランタイムも
同梱しています。`claude-o` は Claude Code CLI を AgentOrchestra モードで起動
するコマンドです。MainAgent と複数の独立した ProfessionalAgent を使うモデル
は同じですが、各 Agent は Codex CLI セッションではなく Claude Code セッション
として tmux pane 上で動きます。Codex の `codex-o` ランタイムは無改変で、両者
は共存します。

### 必要なもの

- Claude Code CLI
- Nix
- tmux
- Python 3

### 認証

Claude Code ランタイムは認証情報が**必須**です。認証が無いと、各 Agent は
「Not logged in」の状態で起動し、いかなる作業もできません。Codex が file ベースの
`auth.json` を隔離 home へ自動コピーするのに対し、macOS の Claude Code は認証情報を
ログイン Keychain に保存し、各 Agent が動く隔離された `CLAUDE_CONFIG_DIR` は Keychain
を読みません。そのため、普段のシェルでの `claude` 対話ログインは Agent に引き継がれ
ません。認証情報を明示的に渡す必要があります。

`claude-o` の前に認証情報を 1 度だけ export します。runtime はそれを各 Agent の
`env.sh`（パーミッション `0600`）に書き込み、**各 Agent の起動時 — MainAgent も、
MainAgent が立ち上げる各 ProfessionalAgent の pane も — が `env.sh` を source する**
ため、pane ごとの設定なしに全員が同じ 1 つの認証情報で認証されます。

```sh
claude setup-token                     # 長期 OAuth トークンが表示される
export CLAUDE_CODE_OAUTH_TOKEN=<token>  # もしくは: export ANTHROPIC_API_KEY=<key>
cd /path/to/project && claude-o
```

認証情報を渡さずに `claude-o` を起動した場合（export したトークンも、コピー可能な
`.credentials.json` も無い場合）、警告を表示したうえでセッション自体は開きますが、
各 Agent は「Not logged in」のままで、認証情報を渡すまで作業できません。runtime は
Keychain の秘密情報を取り出すことはありません。認証情報の用意は必須のデプロイ手順です。

### クイックスタート

改善したいプロジェクトへ移動して `claude-o` を実行します。

```sh
cd /path/to/project && claude-o
```

checkout からは local Nix app としても実行できます。

```sh
nix run .#claude-o
nix run .#agent-orchestra-claude -- doctor --target-project .
```

### 検証

```sh
python3 -m unittest discover -s tests_claude
find .claude/agent_orchestra_minimal .claude/hooks tests_claude \
  -name '*.py' -print0 | xargs -0 python3 -m py_compile
nix build .#checks.x86_64-linux.claude-source-contract
```

環境に合わせて、`x86_64-linux` は `aarch64-darwin`、`x86_64-darwin`、
`aarch64-linux`、`x86_64-linux` などに置き換えてください。

### 詳細 (Claude Code)

- `SPEC.claude.md` は Claude Code ランタイムを `SPEC.md` への delta として
  定義します。
- `.claude/agent_orchestra_minimal/` には Claude Code ランタイムがあります。
- `.claude/skills/` には Agent 向けの操作手順があります。

## 詳細

- `SPEC.md` は runtime と AgentTeam の契約を定義します。
- `layers/` には ProfessionalAgent が使う専門 layer の観点があります。
- `.codex/agent_orchestra_minimal/` には最小 runtime があります。
- `.codex/skills/` には Agent 向けの操作手順があります。
