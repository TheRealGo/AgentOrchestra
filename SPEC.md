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
- MainAgentによるユーザー窓口・制約保持・稼働調整
- ProfessionalAgentによる専門的な検討・実装・検証
- AgentTeam全員による共同編集・相互レビュー・blocking objection
- 改善点がなくなるまで止まらない自己改善ループ
- LLM Agentは止まる前提で、外側に止まらない機械的な再起動機構を置く

## 期待される動き

1. MainAgentがユーザー要求と対象プロジェクトを把握する。
2. MainAgentが必要な専門領域を判断する。
3. MainAgentが複数のProfessionalAgentを独立環境で立ち上げる。（MainAgentと複数のProfessionalAgentを合わせてAgentTeamと呼ぶ。）
4. ProfessionalAgentは自分のlayer専門性に基づいて調査・提案・実装・検証する。
5. AgentTeamは必要に応じてtmuxを使用し相互に直接相談する。
6. AgentTeamで成果物をレビューし、変更単位のDRI/maintainerとpeer reviewに基づいて統合する。
7. ProfessionalAgentの仕事が終わり、ProfessionalAgentに追加の依頼が無ければ、MainAgentが `/exit` やpane killで退役させる。
8. まだ改善余地があれば次サイクルへ進む。
9. すべての改善余地がなくなった、またはユーザー判断待ちになったときだけ止まる。

自明なタスクを除き、MainAgentが一人で編集して終わるのは価値に反する。

## MainAgent の役割

MainAgentは唯一のユーザー-facing Agentであり、AgentTeamのstewardです。

MainAgentが持つ責務:

- ユーザー要求の intake
- ゴールと制約の整理
- 必要なProfessionalAgentの選定
- tmux paneの作成・配置
- ProfessionalAgentへのタスク送信
- Agent間の相談促進
- AgentTeamの相互相談・peer review・blocking objectionの可視化
- 追加指示、差し戻し、受け入れ判断がTeamで行われるための調整
- 完了したProfessionalAgentの退役
- 共有タスクファイルの管理
- ユーザーへの最終報告と完了条件の説明

MainAgentは強い権限を持つ支配者ではなく、ユーザーとの窓口、制約保持、稼働調整、未解決事項の可視化を持つstewardです。
ProfessionalAgentも同じプロジェクトアクセス権を持ち得ます。
編集・提案・レビュー・差し戻し・blocking objectionはAgentTeam共通の権限です。
統合はMainAgentの排他的権限ではなく、変更単位のDRI/maintainer、affected peer、required checks、記録された合意に基づきます。

## ProfessionalAgent の役割

ProfessionalAgentは独立したCodex CLI sessionとして立ち上がる専門Agentです。

期待される性質:

- 自分のlayer観点から起動する
- root/global/projectの不要な指示で汚染されない
- target project全体にはデータ・証跡としてアクセスできる
- 自分の専門観点で調査・実装・検証する
- Main及び他のProfessionalAgentにtmuxで直接相談し、非自明な作業では少なくとも1つのpeer相談または不要理由を残す
- AgentTeamへ結論・証跡・リスク・未完了事項を返し、MainAgentはユーザー-facing channelとしてそれを統合説明する
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
- role-specific startup `AGENTS.md` を生成する
- layer `INSTRUCTIONS.md` を専門観点としてstartup `AGENTS.md`へ添付する
- Skill / Hook を渡す
- Codex CLI の `--cd` / `--add-dir` / `--profile` で起動できる最小のenv/command metadataを渡す
- Stop Hookで止まったAgentを検知する
- task/stateを見て必要なら固定wakeを送る

送る文言は意味判断を含まない固定シグナルです。

```text
runtime_wake
source=hook
user_instruction=false
resync=startup_agents_role_contract_team_skill_task_state
action=resume_existing_work_after_resync
```

Runtime/Hookは「判断する監督者」ではありません。
「止まっていて、状態上まだ動くべきなら、固定wakeを送るだけの装置」です。

## 通信モデル

tmux上のCodex CLI paneです。

- ユーザーが見るのはMainAgent
- ProfessionalAgentは裏側のpaneに立ち上がる
- MainAgentはProfessionalAgent paneに直接タスクを送る
- AgentTeamはMainや他ProfessionalAgentへ直接相談できる
- ProfessionalAgent同士の直接相談は通常の協働経路であり、質問/反論、応答/未応答、採否理由をreview evidenceとして扱う
- tmux通信の具体手順はSkillが担う。Agentは配送確認できない通信を成功扱いしない
- 必要なら共有ファイルやtask/stateファイルで非同期通信する

`codex exec` はこの価値に合いません。
結果だけ返って終わるため、継続的な相談、wake、review、退役というモデルに合わないからです。

## 隔離の意味

隔離とは、権限を弱くすることではありません。

目的はコンテキスト汚染を防ぐことです。

- ProfessionalAgentは自分のlayer観点から起動される
- global / parent / target root AGENTS.md はstartup instructionとしてloadされない
- target project全体はデータとして読める
- 編集権限はMain未満である必要はない

つまり、人間の専門家と同じように、プロジェクト全体を見てよい。
ただし、最初に読み込む役割指示だけは混ざってはいけない。

## タスク管理

共有タスクファイルは、Agent判断の代替ではなく、Hookが機械的に継続可否を見るための状態ファイルです。

空の初期化済み task file は、未着手で open work がないことを表す
`[status] done` で開始する。ユーザー task を受けた後、調査・発見・実装・review
などの open work が始まる前に、Agent は `[status] progress` に切り替える。

初期化直後の基本形:

```ini
[status]
done

[Backlog]

[InProgress]

[InReview]

[Candidates]

[Done]
```

- open workがあるなら `progress`
- Backlog / InProgress / InReview が空で、Candidatesに未解決候補がなければ `done`
- Doneはopen workではない
- Candidatesは最終改善候補ledgerであり、missing/open/backlog/未知のdispositionは未解決として扱う
- 判断はAgentTeamが行い、task fileは状態を表すだけ
- InReviewはMainAgent待ち専用ではなく、peer review、request-changes、blocking objection解消待ちを含む
- 変更単位には可能な限りowner_dri、affected scope、reviewers、required checks、blocking objections、resolution/evidenceを明示する

## 止まってよい条件

止まってよいのは限定的です。

- 改善余地が尽きた
- ユーザー判断が必要
- ユーザーが停止を指示した
- rate limitやruntime障害で継続不能
- destructive / legal / security / production / cost など人間判断が必要

それ以外で止まるのは、このシステムの価値に反します。

## 一文で言うと

agent-orchestraは、MainAgentをユーザー-facingなstewardとして置き、layer専門の独立ProfessionalAgent群を隔離されたCodex CLI環境で立ち上げ、tmuxと共有状態ファイルで相談・共同編集・相互レビュー・再起動・退役を行いながら、改善余地がなくなるまで組織的に自己改善を回し続けるためのAgentic組織的開発フレームワークです。

## Agent Model

### MainAgent

MainAgent is the only user-facing Agent and the AgentTeam steward. It owns:

- user goal intake;
- user constraints and editable-surface continuity;
- task decomposition;
- ProfessionalAgent selection;
- tmux pane creation and layout;
- task delivery to ProfessionalAgents;
- direct pane-to-pane coordination;
- Team review facilitation and unresolved blocking-objection visibility;
- `/exit` or pane kill for completed ProfessionalAgents;
- shared task file maintenance;
- final user reporting and completion-criteria explanation.

MainAgent is the whole-run coordinator and user-facing steward. It must choose the ProfessionalAgent
team from the current user goal, affected layers, risk, and evidence needs
rather than from a fixed default roster.

MainAgent does not outrank ProfessionalAgents for editing, specialist judgment,
request-changes, or blocking objections. Editing authority is shared across the
AgentTeam within the active user constraints and editable surface.

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

The standard Python verification runner is `unittest`, not `pytest`.
AgentTeam verification should use `python3 -m unittest discover -s tests`,
`python3 -m py_compile` for runtime Python surfaces, `git diff --check`, and
Nix checks where applicable. `pytest` is not a project dependency and should
not be run unless the user explicitly requests it or an Agent first confirms it
is available and necessary for the scoped work.

The shared task file has a `[Candidates]` ledger for finalization evidence.
Candidate items must record an id, disposition, summary, and evidence pointer.
Candidate ids must be unique so the finalization ledger has one deterministic
disposition for each improvement candidate.
Candidate field keys must not be duplicated; duplicate keys make the candidate
unresolved rather than letting later values override earlier evidence.
Completed dispositions are `integrated`, `rejected`, `deferred`, `blocked`,
`out-of-scope`, and `needs_user`. Missing, `open`, `backlog`, or unrecognized
dispositions are unresolved and prevent quiet completion.

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

### Equal Editing And Change Units

AgentTeam collaboration is an equal-editing model. Any MainAgent or
ProfessionalAgent may edit, propose new work, review a peer, request changes,
or raise a blocking objection when acting within the active user constraints
and editable surface.

Non-trivial work should be represented as a change unit with:

- `owner_dri`;
- affected files, contracts, or layers;
- reviewers;
- required checks;
- blocking objections;
- resolution and evidence.

Integration readiness is not a unilateral MainAgent permission grant. It is a
recorded Team/DRI review decision. MainAgent may block integration for user
constraint violations, editable-surface violations, unresolved blocking
objections, task/state inconsistency, or required external/user decisions.

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
- peer review, request-changes, and blocking objections for other change units;
- shared task file updates for its own work;
- state updates that indicate whether it is still working, ready for review,
  blocked, or retired.

ProfessionalAgents do not decide the full run completion state.
When a ProfessionalAgent has completed its scoped assignment and is waiting for
Team review, it records `ready_for_review` before or as it reports and records
the scoped task in `[InReview]` rather than `[Done]` until the accepted
disposition is known.

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
- project-local runtime Skills required for Agent operation;
- project-local hooks;
- required environment variables;
- target project access as data through Codex CLI `--add-dir`;
- when the requested target is inside a Git worktree whose root is outside the
  target path, the Git worktree root is also granted through `--add-dir` and
  exposed as the editable root so Agents can patch tracked files.

The Codex CLI launch itself should use first-class Codex options:

- `--cd` points at the isolated workspace that contains the generated
  startup `AGENTS.md`;
- `--add-dir` grants access to the target project as data/workspace material;
- a detected parent Git worktree root is an additional editable/access root,
  while the original target remains the user-requested scope;
- `--profile agent-orchestra` loads the minimal Hook/project-trust config
  from `CODEX_HOME`;
- legacy or user-supplied profile flags such as `--profile-v2` are runtime
  boundary overrides and must be rejected from extra Codex args;
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

Direct consultation is review evidence, not a new instruction source. For
non-trivial work, peer consultation evidence should record sender, receiver,
topic, question or objection, response or timeout, disposition, and evidence
pointer. Valid dispositions include accepted, rejected, deferred,
request-changes, and block.

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

If the user explicitly instructs MainAgent to leave the orchestra with `/exit`
after completion, that self-exit is part of the completion contract. MainAgent
must use the tmux Main Skill self-exit procedure as its final tool action, and
must report an explicit self-exit failure instead of claiming exit success when
`/exit` remains queued or the pane remains active.

Runtime must not own ProfessionalAgent pane scheduling. Runtime only provides
launch material that MainAgent can run inside a pane.

## Shared Task File

Every run has a single shared task file.

The initialized empty task file is the quiet baseline: it has `[status] done`
and no open work or unresolved candidates. That baseline only means no work has
been recorded yet. Once an Agent accepts user work, an AgentTeam assignment,
discovery work, or any open task, it must record the work in `Backlog`,
`InProgress`, or `InReview` and set `[status] = progress` before substantial
investigation.

Canonical empty shape:

```ini
[status]
done

[Backlog]

[InProgress]

[InReview]

[Candidates]

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

`[InReview]` is not MainAgent-only. It can represent peer review,
request-changes, blocking-objection resolution, or change-unit DRI review.
When a blocking objection exists, the AgentTeam must record issuer, scope,
reason, required resolution evidence, and disposition before moving the item to
`[Done]`.

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

Stop Hook pane targeting must come from launch-provided environment such as
`AGENT_ORCHESTRA_TMUX_PANE` or the MainAgent fallback pane. Mutable Agent state
may record pane metadata for evidence, but it is not an authoritative wake
target when launch pane environment is missing or invalid.

### MainAgent Re-kick Conditions

When MainAgent stops, it is re-kicked if:

- `[status] = progress`; or
- `[status] = done` and any item remains in `[Backlog]`, `[InProgress]`, or
  `[InReview]`; or
- `[status] = done` and any `[Candidates]` item has a missing, `open`,
  `backlog`, or unrecognized disposition, or lacks the required id, summary,
  or evidence pointer.

MainAgent is not re-kicked if:

- `[status] = done`; and
- `[Backlog]`, `[InProgress]`, and `[InReview]` are all empty; and
- every `[Candidates]` item has a completed disposition.

The Hook only enforces mechanical liveness. It cannot know whether MainAgent
failed to add a known improvement candidate to `[Backlog]`. MainAgent owns that
judgment before finalization: for a continuous self-improvement goal, it must
run a final improvement-candidate sweep and either create the next-cycle
Backlog item or explicitly record why each remaining candidate is rejected,
blocked, deferred, out-of-scope, or needs user input.

tmux delivery is also a liveness contract. Pasting text into a target Codex TUI
pane is not delivery. The concrete send/capture/retry procedure belongs in the
tmux Skills, not in this SPEC. The SPEC-level invariant is that Agents must not
silently treat unconfirmed communication as delivered.

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
resync=startup_agents_role_contract_team_skill_task_state
action=resume_existing_work_after_resync
```

Agents must treat this as a bounded resync signal: reload the already-loaded
startup Agent role contract, relevant Skills, shared task file, and Agent state,
then continue existing work according to that state. It is not a new user
requirement.

### GitHub Issue #7: Long-Run Memory Dilution

Long-running operation, including 120-hour-class runs, assumes that an Agent's
conversation memory can become incomplete or diluted. The current mitigation is
contractual and mechanical rather than semantic: every `runtime_wake` and every
improvement-cycle boundary requires MainAgent to resynchronize from generated
startup `AGENTS.md`, the MainAgent Role Contract, the `agent-orchestra-team`
Skill, the shared task file, and its Agent state before choosing whether to
continue, launch ProfessionalAgents, stop, or report completion.

This resynchronization is sufficient only if the reloaded contract still drives
the run's operational decisions. A long-run-equivalent wake/cycle check must
confirm that MainAgent preserves ProfessionalAgent launch judgment, the active
layer perspective such as Layer15 process/QA for release and E2E work, Team
review and blocking-objection handling, final improvement-candidate sweep, and
ProfessionalAgent retirement audit. Residual risk remains that an Agent can
fail to perform a semantic final sweep even though the Hook and task file are
mechanically consistent; that risk must be recorded as a completed
`[Candidates]` disposition, Backlog item, or follow-up issue when discovered.

The Issue #7 E2E acceptance gate must be backed by tracked repository evidence,
not by ignored local run logs. That gate covers `runtime_wake` bounded resync,
`cycle_done` versus run completion, generated startup `AGENTS.md`, MainAgent
Role Contract, `agent-orchestra-team` Skill, shared task file, Agent state,
smallest sufficient team selection, Layer15 process/QA judgment, Team review,
blocking-objection evidence, candidate disposition, and ProfessionalAgent
retirement audit. Retirement evidence must show that accepted ProfessionalAgents
are marked `retired`, sent `/exit`, and have pane cleanup verified, with
`kill-pane` only as cleanup after the attempted `/exit`. Acceptance evidence
must also report whether the run used live long-duration execution or a
long-run-equivalent contract check, include verification commands such as
`python3 -m unittest discover -s tests`, `python3 -m py_compile`,
`git diff --check`, and applicable Nix checks, and record any residual risk or
deferred criterion explicitly.

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
- `--profile agent-orchestra`;
- `--ask-for-approval`, `--sandbox`, `--enable`, and `-c` config overrides;
- `--cd` isolated workspace;
- `--add-dir` target project access;
- no `codex exec` ProfessionalAgents.
- layer `INSTRUCTIONS.md` as specialist perspective, not behavior.
- ProfessionalAgent protocol layers resolve from
  `AGENT_ORCHESTRA_REPO_ROOT/layers`, never from the target project's
  `layers/` tree unless explicitly requested as experimental project-local
  instructions.
- launch material preserves `AGENT_ORCHESTRA_REPO_ROOT` in both `env.json` and
  `env.sh` so installed Nix `codex-o` can prepare later ProfessionalAgents from
  the same protocol source.

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

### Release Skill

Documents the project-local AgentOrchestra release workflow from the private
development repository to the public release mirror. It is repository-local
operator guidance for explicit release tasks, not part of the minimal runtime
launch contract by default. It does not make runtime responsible for release
judgment, release approval, branch selection, or publishing.

### Skill Granularity

Skills should be split by operation surface:

- team coordination;
- isolated launch;
- common tmux communication;
- MainAgent pane management;
- task/state updates.
- project-local release workflow evidence and commands when a release task
  explicitly uses that Skill.

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

## Release Evidence And SPEC Traceability

AgentOrchestra changes should leave release evidence that maps each change unit
back to this SPEC and to executable verification. The minimum evidence record
for a non-trivial change is:

- SPEC clause or section affected;
- owner_dri and affected scope;
- reviewers and peer consultation disposition when applicable;
- required checks run, skipped, or deferred with reason;
- candidate-ledger disposition for residual improvements;
- blocking objections and resolution evidence.

The shared task file exposes deterministic finalization blockers: non-`done`
status, open work in `[Backlog]`, `[InProgress]`, or `[InReview]`, and
unresolved `[Candidates]` entries. Final release evidence should report that
blocker list as empty, or explicitly record why a blocker is deferred,
blocked, out-of-scope, or needs user input.

## Completion Criteria

The minimal runtime is acceptable when tests and E2E evidence show:

- repository startup instruction surface is controlled by generated
  `AGENTS.md`, not by incidental root files or target root `AGENTS.md`;
- MainAgent starts from isolated instructions;
- ProfessionalAgent starts from isolated `AGENTS.md` behavior plus
  selected layer perspective;
- `layers/**` remains free of Agent behavior contracts;
- MainAgent can create a ProfessionalAgent tmux pane;
- MainAgent can send initial tasks, follow-ups, and review requests through
  Skill-defined tmux delivery procedures without false-accepting queued
  composer text or interrupting a peer pane that is still working;
- ProfessionalAgents can send messages to MainAgent or peer panes through the
  same Skill-defined delivery procedures and record consultation evidence;
- Stop Hook re-kicks MainAgent while open work remains;
- long-run-equivalent wake/cycle repetition preserves MainAgent resync from
  generated startup `AGENTS.md`, the MainAgent Role Contract, the
  `agent-orchestra-team` Skill, shared task file, and Agent state before
  ProfessionalAgent launch, Layer15 process/QA judgment, Team review, final
  candidate sweep, or pane-retirement audit decisions;
- Stop Hook does not re-kick MainAgent after `status=done`, no open work, and
  completed `[Candidates]` dispositions;
- Stop Hook re-kicks a ProfessionalAgent only when its own state is active;
- quiet ProfessionalAgent states are not re-kicked;
- accepted ProfessionalAgents are marked `retired`, sent `/exit`, and have pane
  cleanup verified before MainAgent reports completion;
- user-requested MainAgent self-exit uses the tmux Main Skill self-exit
  procedure and reports explicit failure if it cannot submit `/exit`;
- verification uses `unittest`, direct Python `py_compile`,
  `git diff --check`, and path-form Nix checks when Git-backed generated-copy
  visibility would otherwise hide untracked fixture files;
- runtime code remains small, mechanical, and responsibility-limited.
