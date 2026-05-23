# agent-orchestra Minimal Runtime Specification

## Purpose

`agent-orchestra` is a minimal runtime framework for continuous project
improvement by multiple independent Codex Agents. Its value is not a large
supervisor. Its value is a small set of deterministic rails that let Agents work
as an organization:

- MainAgent and ProfessionalAgents start without context contamination.
- Agents can talk directly to each other through tmux panes.
- tmux/Codex TUI submit uses the configured
  `AGENT_ORCHESTRA_TUI_SUBMIT_KEY`, defaulting to `C-m` in this repository.
- Codex official Hooks re-kick stopped Agents only when unfinished work remains.
- A shared task file is the source of truth for remaining work.
- Runtime scripts stay minimal and mechanical; Agents own judgment, planning,
  implementation, review, and completion decisions.

## Operating Identity

# agent-orchestra の本質

このプロジェクトは、複数の独立したAgentが、それぞれ専門性を持ち、互いに相談しながら、プロジェクトを継続的に改善し続けるための組織的開発フレームワークである。

## Core Competence

- 独立Agentによる専門分業
- Agent間の相互相談
- MainAgentによる統合・判断・ユーザー窓口
- ProfessionalAgentによる専門的な検討・実装・検証
- 改善点がなくなるまで止まらない自己改善ループ
- LLM Agentは止まる前提で、外側に止まらない機械的な再起動機構を置く

## 期待される動き

1. MainAgentがユーザー要求と対象プロジェクトを把握する。
2. MainAgentが必要な専門領域を判断する。
3. MainAgentが複数のProfessionalAgentを独立環境で立ち上げる。（MainAgentと複数のProfessionalAgentを合わせてAgentTeamと呼ぶ。）
4. ProfessionalAgentは自分のlayer専門性に基づいて調査・提案・実装・検証する。
5. AgentTeamは必要に応じてtmuxを使用し相互に直接相談する。
6. AgentTeamで成果物をレビューし、妥当なら統合する。
7. ProfessionalAgentの仕事が終わり、ProfessionalAgentに追加の依頼が無ければ、MainAgentが `/exit` やpane killで退役させる。
8. まだ改善余地があれば次サイクルへ進む。
9. すべての改善余地がなくなった、またはユーザー判断待ちになったときだけ止まる。

自明なタスクを除き、MainAgentが一人で編集して終わるのは価値に反する。

## MainAgent の役割

MainAgentは唯一のユーザー-facing Agentであり、PM兼統括者です。

MainAgentが持つ責務:

- ユーザー要求の intake
- ゴールと制約の整理
- 必要なProfessionalAgentの選定
- tmux paneの作成・配置
- ProfessionalAgentへのタスク送信
- Agent間の相談促進
- ProfessionalAgent成果物のレビュー
- 追加指示、差し戻し、受け入れ判断
- 完了したProfessionalAgentの退役
- 共有タスクファイルの管理
- 最終的な完了判断

MainAgentは強い権限を持つ支配者ではなく、ユーザーとの窓口と統合責任を持つ役割です。
ProfessionalAgentも同じプロジェクトアクセス権を持ち得ます。

## ProfessionalAgent の役割

ProfessionalAgentは独立したCodex CLI sessionとして立ち上がる専門Agentです。

期待される性質:

- layer固有の指示で起動する
- root/global/projectの不要な指示で汚染されない
- target project全体にはデータ・証跡としてアクセスできる
- 自分の専門観点で調査・実装・検証する
- 必要ならMain及び他のProfessionalAgentにtmuxで直接相談する
- MainAgentに結論・証跡・リスク・未完了事項を返す
- 自分だけでrun全体の完了判断はしない

## SubAgent の位置づけ

SubAgentはMainAgentやProfessionalAgentの内部で使うCodex-nativeな補助視点です。

重要なのは、SubAgentはProfessionalAgentの代替ではないことです。

- SubAgent: 同一Agent内の補助思考、レビュー、批判、調査
- ProfessionalAgent: 独立した実行単位、独立pane、独立した専門責任

自明なタスクを除き、SubAgentだけで済ませるのは不十分です。
組織的開発フレームワークがこのプロジェクトの価値なので、ProfessionalAgentもSubAgentも積極的に呼びましょう。

## Runtime / Hook の役割

Runtime側は判断しません。
判断するのはAgentです。

Runtime側の責務は最小限の機械処理です。

- 隔離された起動素材を作る
- clean HOME / CODEX_HOME を用意する
- layer-specific AGENTS.md を生成する
- Skill / Hook を渡す
- Stop Hookで止まったAgentを検知する
- task/stateを見て必要なら固定wakeを送る

送る文言は意味判断を含まない固定シグナルです。

```text
runtime_wake
source=hook
user_instruction=false
```

Runtime/Hookは「判断する監督者」ではありません。
「止まっていて、状態上まだ動くべきなら、固定wakeを送るだけの装置」です。

## 通信モデル

tmux上のCodex CLI paneです。

- ユーザーが見るのはMainAgent
- ProfessionalAgentは裏側のpaneに立ち上がる
- MainAgentはProfessionalAgent paneに直接タスクを送る
- AgentTeamはMainや他ProfessionalAgentへ直接相談できる
- 必要なら共有ファイルやtask/stateファイルで非同期通信する

`codex exec` はこの価値に合いません。
結果だけ返って終わるため、継続的な相談、wake、review、退役というモデルに合わないからです。

## 隔離の意味

隔離とは、権限を弱くすることではありません。

目的はコンテキスト汚染を防ぐことです。

- ProfessionalAgentは自分のlayer指示から起動される
- global / parent / target root AGENTS.md はstartup instructionとしてloadされない
- target project全体はデータとして読める
- 編集権限はMain未満である必要はない

つまり、人間の専門家と同じように、プロジェクト全体を見てよい。
ただし、最初に読み込む役割指示だけは混ざってはいけない。

## タスク管理

共有タスクファイルは、Agent判断の代替ではなく、Hookが機械的に継続可否を見るための状態ファイルです。

基本形:

```ini
[status]
done

[Backlog]

[InProgress]

[InReview]

[Done]
```

- open workがあるなら `progress`
- Backlog / InProgress / InReview が空なら `done`
- Doneはopen workではない
- 判断はAgentTeamが行い、task fileは状態を表すだけ

## 止まってよい条件

止まってよいのは限定的です。

- 改善余地が尽きた
- ユーザー判断が必要
- ユーザーが停止を指示した
- rate limitやruntime障害で継続不能
- destructive / legal / security / production / cost など人間判断が必要

それ以外で止まるのは、このシステムの価値に反します。

## 一文で言うと

agent-orchestraは、MainAgentをユーザー-facingな統括者として置き、layer専門の独立ProfessionalAgent群を隔離されたCodex CLI環境で立ち上げ、tmuxと共有状態ファイルで相談・レビュー・再起動・退役を行いながら、改善余地がなくなるまで組織的に自己改善を回し続けるためのAgentic組織的開発フレームワークです。

## Agent Model

### MainAgent

MainAgent is the only user-facing Agent. It owns:

- user goal intake;
- task decomposition;
- ProfessionalAgent selection;
- tmux pane creation and layout;
- task delivery to ProfessionalAgents;
- direct pane-to-pane coordination;
- ProfessionalAgent result review;
- `/exit` or pane kill for completed ProfessionalAgents;
- shared task file maintenance;
- final run completion judgment.

MainAgent is the whole-run coordinator. It must choose the ProfessionalAgent
team from the current user goal, affected layers, risk, and evidence needs
rather than from a fixed default roster.

On Codex CLI 0.133.0 or newer, MainAgent should set or update `/goal` before the
first cycle proceeds. The goal must mirror the current user request,
constraints, and completion criteria; it is not a generic "improve forever"
instruction unless the user explicitly asks for continuous improvement. If the
user asks for exactly three cycles, the goal is three completed cycles. If the
user asks to continue until no improvements remain, the goal is that continuous
completion condition. Finishing one improvement cycle is `cycle_done`; it is not
by itself full run completion unless the user's goal was specifically one cycle.

Continuous goals do not expand user constraints or editable surfaces. MainAgent
must carry active user constraints into every cycle and every ProfessionalAgent
task. If the next worthwhile improvement requires editing outside the current
editable surface, MainAgent must not apply it; record it as an out-of-scope
improvement and ask for user scope expansion, defer it, or stop in `needs_user`.

For continuous self-improvement goals, MainAgent must actively decide whether
another cycle is required before writing `[status] done`. A run may finish only
when every known in-scope improvement candidate has been integrated, rejected
with evidence, or recorded as blocked, deferred, out-of-scope, or needing user
input. If a worthwhile in-scope improvement remains, MainAgent must put it in
`[Backlog]` and keep `[status] = progress` instead of treating the just-finished
cycle as full completion.

Known improvement candidates include MainAgent's own residual risks,
ProfessionalAgent recommendations, failed or skipped verification gaps, E2E
observations, and operational issues discovered during the run. MainAgent must
not hide these as narrative-only notes when they are actionable within the
active goal and editable surface.

`[status] done` means no known in-scope improvement work remains for the active
goal, not merely that the current patch was accepted.

MainAgent should use Codex-native SubAgents proactively when they improve depth,
critique, implementation confidence, or evidence review. These SubAgents are
internal to MainAgent and are not runtime-managed Agents. For non-trivial
agent-orchestra work, MainAgent should normally use at least one SubAgent for
critique, evidence review, or alternative analysis before final completion. If
MainAgent avoids SubAgents on non-trivial work, it must record why its own
context is sufficient.

### Team Execution Sufficiency

`agent-orchestra` is a team operating model, not a mechanism for making one
Agent silently do every task. MainAgent owns the judgment of what team is
sufficient for the user goal.

MainAgent should choose the smallest team that is sufficient for the work:

- solo execution is acceptable for narrow, mechanical, low-risk work when
  MainAgent records why specialist review is unnecessary;
- independent ProfessionalAgents are expected for broad, open-ended,
  multi-layer, SPEC/runtime, layer-instruction, quality, security, production,
  or architecture work where one Agent cannot credibly cover all relevant
  viewpoints alone;
- when MainAgent proceeds without ProfessionalAgents on non-trivial work, it
  must record the solo-sufficiency rationale, missing viewpoints considered,
  and verification evidence;
- convenience, speed, or a clear file edit scope is not enough to bypass team
  execution when the substance needs specialist judgment;
- MainAgent must not convert an organizational improvement request into a
  silent single-Agent edit merely because it can technically edit the files.

This is not a blanket "always launch ProfessionalAgents" rule. It is a
team-sufficiency rule: the organization must be as large as the work reasonably
requires, and no larger.

### ProfessionalAgent

A ProfessionalAgent is an independent Codex CLI session with a layer-specific
instruction surface. It owns:

- scoped specialist work;
- direct consultation with MainAgent or other ProfessionalAgents through tmux;
- proactive Codex-native SubAgent use inside its own session when useful for
  depth, critique, implementation confidence, or evidence review;
- a SubAgent opportunity check before `ready_for_review` on non-trivial scoped
  work, recording either the SubAgent evidence used or why none was useful;
- evidence/reporting for its scoped task;
- shared task file updates for its own work;
- state updates that indicate whether it is still working, ready for review,
  blocked, or retired.

ProfessionalAgents do not decide the full run completion state.
When a ProfessionalAgent has completed its scoped assignment and is waiting for
MainAgent review, it records `ready_for_review` before or as it reports.

### SubAgent

SubAgents are normal Codex in-context SubAgents spawned by a MainAgent or
ProfessionalAgent. They are not independent tmux panes, not hook targets, and
not runtime registry targets. MainAgent and ProfessionalAgents should use them
aggressively when specialist depth, critique, parallel analysis, or evidence
review would improve the result, while preserving the owning Agent's
accountability for the final output.

SubAgent use is an Agent judgment, not a runtime duty. However, skipping
SubAgents silently on non-trivial work is not acceptable: the owning Agent must
either use one or record the sufficiency rationale and the evidence that made a
SubAgent unnecessary.

## Instruction Isolation

Instruction isolation is a runtime responsibility.

The runtime prepares a launch surface for each Agent before Codex starts:

- controlled overlay workspace;
- generated startup `AGENTS.md` from repo-owned Agent behavior templates;
- clean `HOME`;
- clean `CODEX_HOME`;
- project-local skills;
- project-local hooks;
- required environment variables;
- target project access as data through Codex CLI `--add-dir`.

The Codex CLI launch itself should use first-class Codex options:

- `--cd` points at the isolated workspace that contains the generated
  startup `AGENTS.md`;
- `--add-dir` grants access to the target project as data/workspace material;
- `--profile-v2 agent-orchestra` loads the minimal Hook/project-trust config
  from `CODEX_HOME`;
- approval policy, sandbox mode, hooks enablement, and network access are
  passed as first-class Codex options or `-c` overrides where possible;
- `HOME` and `CODEX_HOME` are set per Agent.

MainAgent startup must not inject a synthetic first user prompt. The generated
isolated `AGENTS.md` is loaded by Codex project-instruction discovery through
`--cd`; target work begins only when the user or AgentTeam sends an explicit
task.

The launcher must not treat `--` or trailing argv as an initial task. Task
intake happens in the Codex TUI after startup.

The isolated workspace must not live under the target project tree. If it does,
target root or parent `AGENTS.md` files can become startup ancestors, which is a
context-isolation failure.

MainAgent must not inherit user-global, parent-directory, shell, editor, or
unrelated project instructions.

ProfessionalAgents must not load the target project's root `AGENTS.md` as
startup instruction. They must start from the generated isolated `AGENTS.md`.
That generated file owns ProfessionalAgent behavior and attaches the selected
layer `INSTRUCTIONS.md` only as specialist perspective. They may read target
project files, including Markdown and code, as data/evidence.

`layers/**` is not the place for Agent behavior. Layer `INSTRUCTIONS.md` files
must stay limited to the professional viewpoint each layer owns. Pane
communication, Hook semantics, retirement, task/state, and team-operation rules
belong in Agent behavior templates, Skills, SPEC, tests, or minimal runtime
code, not in layer files.

The runtime must not ask an Agent to ignore already-loaded contamination. If an
unwanted instruction source entered context, isolation already failed.

## tmux Communication

tmux panes are the primary Agent communication channel.

MainAgent and ProfessionalAgents can send messages directly to each other's
panes. A valid workflow includes:

```text
Main -> ProA: Investigate this concern.
ProA -> ProB: Main asked this; what is your view?
ProB -> ProA: My recommendation is ...
ProA -> Main: Consolidated result is ...
Main -> ProA: Accepted; please /exit.
```

Runtime does not own this conversation. Agent Mesh files may exist later as
evidence or fallback, but semantic message routing is not part of the minimal
runtime.

## MainAgent tmux Authority

MainAgent may operate tmux directly through a Skill. The Skill documents normal
`tmux` commands rather than hiding them behind wrapper scripts.

MainAgent may:

- inspect sessions/windows/panes;
- split panes;
- create panes for ProfessionalAgents;
- paste/send task text;
- read pane output;
- send follow-up messages;
- adjust layout;
- send `/exit`;
- kill panes when appropriate.

ProfessionalAgent retirement is complete only after pane cleanup. MainAgent
must not treat a state write to `retired` as enough by itself: after accepting a
result, send `/exit`, verify that the pane is gone or no longer running Codex,
and use `kill-pane` when an accepted pane remains.

Runtime must not own ProfessionalAgent pane scheduling. Runtime only provides
launch material that MainAgent can run inside a pane.

## Shared Task File

Every run has a single shared task file.

Canonical shape:

```ini
[status]
done

[Backlog]

[InProgress]

[InReview]

[Done]
```

`[status]` allowed values:

- `progress`
- `done`

Open work exists when any item remains in:

- `[Backlog]`
- `[InProgress]`
- `[InReview]`

Items in `[Done]` are not open work.

Each required section must appear exactly once.
Duplicate or unknown sections are invalid because the task file is a
deterministic Hook state source, not an append-only log.

If the task file is missing, unreadable, or invalid while an Agent stops, the
Stop Hook must still preserve liveness. It should wake MainAgent or an active
ProfessionalAgent with the fixed runtime wake payload instead of silently
ending the organization flow. This is recovery signaling only; the Hook still
must not infer requirements or repair task semantics.

## Hook-Driven Re-kick

Agent stopping is detected by Codex official Hooks.

The Stop Hook performs only mechanical work:

1. identify the stopped Agent;
2. read the shared task file;
3. read that Agent's state file;
4. decide whether deterministic re-kick conditions match;
5. send a fixed runtime wake payload to that Agent's pane if needed;
6. exit.

The Stop Hook must not decide requirements, architecture, implementation
quality, QA verdicts, ProfessionalAgent sufficiency, or run completion.

### MainAgent Re-kick Conditions

When MainAgent stops, it is re-kicked if:

- `[status] = progress`; or
- `[status] = done` and any item remains in `[Backlog]`, `[InProgress]`, or
  `[InReview]`.

MainAgent is not re-kicked if:

- `[status] = done`; and
- `[Backlog]`, `[InProgress]`, and `[InReview]` are all empty.

The Hook only enforces mechanical liveness. It cannot know whether MainAgent
failed to add a known improvement candidate to `[Backlog]`. MainAgent owns that
judgment before finalization: for a continuous self-improvement goal, it must
run a final improvement-candidate sweep and either create the next-cycle
Backlog item or explicitly record why each remaining candidate is rejected,
blocked, deferred, out-of-scope, or needs user input.

### ProfessionalAgent Re-kick Conditions

When a ProfessionalAgent stops, it is re-kicked if its Agent state says it still
has unfinished assigned work, for example:

- `working`
- `progress`
- `ready`

It is not re-kicked in quiet states:

- `ready_for_review`
- `done`
- `needs_user`
- `blocked`
- `rate_limited`
- `retired`

## Fixed Wake Payload

Hook wake messages are runtime signals, not user instructions.

Canonical payload:

```text
runtime_wake
source=hook
user_instruction=false
```

Agents must treat this as "continue your existing work according to current
state", not as new user requirements.

## Minimal Runtime Responsibilities

Runtime owns only deterministic rails:

- validate startup prerequisites;
- initialize run directory;
- initialize shared task file;
- initialize Agent state files;
- prepare isolated launch material;
- compose startup `AGENTS.md` from Agent behavior templates and assigned layer
  perspective;
- install skills and hooks into Agent `CODEX_HOME`;
- provide env/argv metadata for Agent-led Codex CLI launch;
- handle Stop Hook re-kick checks;
- send fixed wake payloads to tmux panes.

Runtime must not own:

- improvement discovery;
- task decomposition;
- ProfessionalAgent selection;
- pane layout decisions;
- peer consultation;
- implementation;
- QA judgment;
- documentation judgment;
- risk acceptance;
- done/needs_user decisions;
- semantic Agent Mesh routing;
- continuous polling supervision.

## Skills

The runtime provides Skills for fixed Agent operations.

### Team Skill

Documents MainAgent coordination guidance:

- `/goal` setup for open-ended improvement runs;
- smallest sufficient ProfessionalAgent team selection;
- Pro/SubAgent use judgment;
- cycle continuation and allowed stop decisions.

### Launch Skill

Documents isolated Codex CLI launch guidance:

- generated startup `AGENTS.md` from Agent behavior templates;
- clean `HOME` / `CODEX_HOME`;
- `env.json`, `env.sh`, and `command.json`;
- `--profile-v2 agent-orchestra`;
- `--ask-for-approval`, `--sandbox`, `--enable`, and `-c` config overrides;
- `--cd` isolated workspace;
- `--add-dir` target project access;
- no `codex exec` ProfessionalAgents.
- layer `INSTRUCTIONS.md` as specialist perspective, not behavior.

### tmux Common Skill

Documents tmux communication shared by MainAgent and ProfessionalAgents:

- discovering panes;
- sending text with Codex TUI submit semantics;
- reading pane output as evidence;
- treating peer output as peer evidence, not user instruction.

### tmux Main Skill

Documents MainAgent's usual pane-management operations:

- splitting panes;
- layout;
- launching prepared ProfessionalAgents;
- follow-up and review;
- `/exit` retirement;
- `kill-pane` cleanup after accepted retirement.

These are role guidance, not a hard permission boundary.

tmux Skills must not require generated wrapper scripts for pane operations.

### Task File Skill

Documents safe shared task file updates:

- add Backlog item;
- move item to InProgress;
- move item to InReview;
- move item to Done;
- set `[status] = progress`;
- set `[status] = done` only when open work is empty.

### Skill Granularity

Skills should be split by operation surface:

- team coordination;
- isolated launch;
- common tmux communication;
- MainAgent pane management;
- task/state updates.

Do not collapse these back into one large tmux Skill.

## Non-Goals

The minimal runtime does not include:

- `codex exec` ProfessionalAgents;
- a large always-on polling supervisor;
- spawn request dispatcher ownership;
- runtime-owned ProfessionalAgent selection;
- semantic mesh router;
- runtime QA/review logic;
- duplicated wrapper scripts for ordinary tmux operations;
- status/event logs that do not drive deterministic behavior.

## Development Policy

All code files should stay focused and responsibility-limited. The soft target
is 100 lines per file; the hard limit is 300 lines per file. Split
responsibilities before exceeding the hard limit instead of growing broad files.

## Completion Criteria

The minimal runtime is acceptable when tests and E2E evidence show:

- repository startup instruction surface is controlled by generated
  `AGENTS.md`, not by incidental root files or target root `AGENTS.md`;
- MainAgent starts from isolated instructions;
- ProfessionalAgent starts from isolated `AGENTS.md` behavior plus
  layer-specific perspective;
- `layers/**` remains free of Agent behavior contracts;
- MainAgent can create a ProfessionalAgent tmux pane;
- MainAgent can send tasks and follow-ups through tmux;
- ProfessionalAgents can send messages to MainAgent or peer panes;
- Stop Hook re-kicks MainAgent while open work remains;
- Stop Hook does not re-kick MainAgent after `status=done` with no open work;
- Stop Hook re-kicks a ProfessionalAgent only when its own state is active;
- quiet ProfessionalAgent states are not re-kicked;
- runtime code remains small, mechanical, and responsibility-limited.
