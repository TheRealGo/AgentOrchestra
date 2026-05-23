# Frontier Operating Model Research: プロダクト管理・ディスカバリー（03）

生成日: 2026-05-13  
対象単位: プロダクト管理・ディスカバリー  
対象レイヤー: 03  
対象サブテーマ: プロダクト戦略、プロダクトビジョン、プロダクトロードマップ、ペルソナ、ユースケース、ジャーニー、ユーザーストーリー

---

## 0. 調査プロトコル

本調査は、`RESEARCH.md` の Frontier Operating Model Research 運用プレイブックに従い、対象レイヤーを「意思決定システム」として再構成した。公開情報のみを使用し、公式文書、政府・標準・コミュニティ規範、公式ハンドブック、公式プロダクトドキュメント、公開ロードマップ、公開メソッド記事を優先した。非公開情報、認証が必要な内部文書、リーク、面談、推測だけの断定は使用していない。

信頼度は次のように扱う。

| 信頼度 | 意味 | 本調査での採用方針 |
|---|---|---|
| A | 公式・標準・実成果物などの直接証拠がある | Clone Spec の中核に採用 |
| B | 複数の独立ソースで整合する | Clone Spec の中核に採用 |
| C | 状況証拠または専門家メソッドとして有用だが直接証拠ではない | 補助仮説・実装案として採用 |
| D | 仮説 | 追加調査対象 |
| X | 反証・不適合 | 採用しない |

---

## 1. エグゼクティブサマリー

対象レイヤー 03 の先端パターンは、単なる「プロダクト管理手法」ではなく、**事業成果、顧客課題、探索証拠、実装バックログを一続きの意思決定チェーンにする operating model** である。優れた主体は、まず投資理由・顧客価値・成功指標を明確にし、その後にペルソナ、ジャーニー、ユースケース、ユーザーストーリーを段階的に具体化する。ロードマップは固定納期表ではなく、価値仮説・証拠・依存関係・学習によって更新されるポートフォリオとして扱われる。

主要な結論は次のとおり。

| # | 結論 | 根拠 | 信頼度 |
|---|---|---|---|
| 1 | プロダクト戦略は「何を作るか」ではなく、「なぜ投資するか、どの顧客価値と事業成果を狙うか、どう測るか」を決めるレイヤーである。 | AWS は why、vision、success metrics、business case、feature prioritization を一連の戦略プロセスとして扱う。GitLab は顧客中心・データ優先・成果重視を product principles にしている。 | A |
| 2 | ビジョンはスローガンではなく、後続のロードマップ、PR/FAQ、ペルソナ、ジャーニー、ユーザーストーリーの判断基準である。 | AWS はビジョンを意思決定・トレードオフ・整合のガイドとして説明し、GOV.UK は vision → objectives → roadmap → user stories の順に計画を可視化する。 | A |
| 3 | ロードマップは価値最大化と学習更新のための artifact であり、固定的な納期約束として扱うと失敗しやすい。 | AWS はロードマップを customer/company value と technical dependency で最適化し、GOV.UK はロードマップを定期的に見直す visible plan とする。GitHub は public roadmap で stage と expected timing を公開し、フィードバックを受ける。 | A |
| 4 | ペルソナはデモグラフィック属性ではなく、実顧客の行動、動機、課題、利用文脈を集約した意思決定 proxy である。 | NN/g は persona を real information に基づく target audience の表象とし、analytics だけでは attitudes/goals/pain points を捉えられないとする。AWS も persona を顧客の行動・利用理由理解に使う。 | A/B |
| 5 | ユースケースは、actor、goal、main scenario、alternative conditions/flows を含む、システム要求と境界条件の表現である。 | OMG UML はユースケースをシステムが何をすべきかを捕捉する手段とし、Ivar Jacobson の ACM Queue 記事は actor、goal、main scenario、alternative flow を実務要素として説明する。 | A/B |
| 6 | ジャーニーは、ユーザーが目的を達成する過程を、行動、感情、摩擦、システム接点、改善機会として可視化する artifact である。 | NN/g は journey map を目的達成プロセスの可視化と定義し、AWS は as-is journey、friction、target journey、supporting systems を要求する。 | A |
| 7 | ユーザーストーリーは、actor/narrative/goal と acceptance criteria を通じて、発見された顧客課題を実装可能な backlog item に変換する。 | GOV.UK は actor、narrative、goal、acceptance criteria を user story の要素として示し、Scrum Guide は Product Goal に対して Product Backlog が「何を満たすか」を形成するとする。 | A |
| 8 | discovery と delivery は分離しすぎても混同しても失敗する。先端組織は、problem validation、solution validation、backlog、delivery planning を接続しつつ、学習で更新する。 | GitLab の Product Development Flow は validation backlog、problem validation、solution validation、planning/refinement、development などを横断する公開ワークフローを示す。Product Talk は discovery を「何を作るかの意思決定」と定義し、delivery と区別する。 | B |

---

## 2. 対象レイヤーの正規化: layer_registry 抜粋

| Layer ID | 正規化名 | Decision Object | Decision Question | 主な成果物 | 主な owner |
|---|---|---|---|---|---|
| 03.01 | プロダクト戦略 | 投資対象、顧客価値、事業成果、優先市場、成功指標 | どの顧客・課題・市場・事業成果に対して、なぜこのプロダクトへ投資するのか | product strategy brief、value driver、OKR、business case、portfolio priority | CPO、VP Product、GM、Product Lead |
| 03.02 | プロダクトビジョン | 将来状態、価値仮説、北極星、判断原則 | プロダクトが将来どの状態を実現し、何を作らない判断を含めてチームをどう整合させるか | vision statement、PR/FAQ、north-star narrative、principles | Product Lead、Design Lead、Engineering Lead |
| 03.03 | プロダクトロードマップ | 価値仮説の順序、投資テーマ、マイルストーン、依存関係 | どの機会・機能・実験を、どの順序と粒度で扱い、何を学んだら変更するか | outcome roadmap、theme roadmap、public/internal roadmap、dependency map | Product Manager、Program Manager、Engineering Manager |
| 03.04 | ペルソナ | 対象ユーザーの行動、目標、制約、動機、課題 | 誰のために設計し、その人の文脈・行動・意思決定をどう proxy 化するか | persona canvas、JTBD canvas、segment/persona mapping、research evidence pack | UX Researcher、Product Manager、Designer |
| 03.05 | ユースケース | actor が system を使って達成する goal と scenario | どの actor がどの goal を達成し、正常系・代替系・例外系をどう扱うか | use-case brief、actor map、scenario flow、alternative flow、domain model | Business Analyst、Product Manager、Solution Architect |
| 03.06 | ジャーニー | ユーザーが目的達成までに通る体験・接点・摩擦・感情 | as-is と target journey のどこに価値機会・摩擦・測定点があるか | customer/user journey map、service blueprint、research wall、opportunity map | UX Researcher、Service Designer、Product Manager |
| 03.07 | ユーザーストーリー | backlog item としての actor、need、goal、acceptance criteria | 発見された課題を、どの粒度の実装可能・検証可能な単位へ変換するか | user story、acceptance criteria、epic/story map、backlog item | Product Owner、Product Manager、Scrum Team |

---

## 3. Frontier Exemplar 候補スコアリング

スコアは `RESEARCH.md` の軸に合わせ、Performance、Adoption、Artifact Richness、Peer Validation、Recency、Transferability、Failure Evidence を 100 点換算した。ここでの「トップ」は有名度ではなく、公開成果物の厚みと再現可能性で評価した。

| 候補 | 主対象レイヤー | 採用理由 | スコア | 信頼度 |
|---|---:|---|---:|---|
| AWS Prescriptive Guidance: product strategy / working backwards | 03.01–03.03, 03.04, 03.06 | why、vision、success metrics、business case、feature prioritization、persona、journey、PR/FAQ、roadmap を一連の公開プロセスとして説明している。 | 93 | A |
| GitLab Handbook: Product Principles / Product Development Flow / UX Research | 03 | 顧客中心、dogfooding、data over intuition、problem validation、solution validation、research prioritization、JTBD を公開 handbook として運用している。 | 92 | A |
| GOV.UK Service Manual | 03 | discovery、service standard、agile planning、user stories、research sharing が政府標準として詳細に公開されている。停止判断、open working、週次共有など失敗防止の示唆も強い。 | 91 | A |
| Atlassian Jira Product Discovery docs | 03.01–03.03, 03.06 | ideas、insights、impact/effort/confidence matrix、roadmaps、delivery work connection という discovery-to-delivery artifact を公式ツール仕様として公開している。 | 84 | A/B |
| Scrum Guide 2020 + Agile Manifesto | 03.03, 03.07 | Product Goal、Product Backlog、Sprint Planning、Product Owner、顧客協働・変化への対応という規範を提供する。discovery 自体は範囲外なので補完ソース扱い。 | 82 | A |
| NN/g UX methods | 03.04, 03.06 | persona、journey map、qualitative research、living document といった UX artifact の方法論が豊富。企業の内部運用ではないため補助的に採用。 | 80 | B/C |
| Product Talk / Teresa Torres | 03.01–03.03, 03.06 | discovery を「何を作るかの意思決定」と定義し、continuous discovery、opportunity solution tree、assumption testing を体系化している。 | 78 | B/C |
| GitHub Public Roadmap | 03.03 | public roadmap の stage、expected timing、feedback discussion、sunset issue など、透明な roadmap artifact と deprecation 判断を観測できる。 | 76 | A/B |

---

## 4. Source Catalog

| Source ID | Entity | Source | Tier | 主に効くレイヤー | 何が取れるか | URL |
|---|---|---|---|---|---|---|
| S01 | AWS | Developing product strategies that deliver measurable business value | T3 official guidance | 03.01–03.03 | 戦略プロセス全体、why、metrics、business case、roadmap | https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-product-development/introduction.html |
| S02 | AWS | Start with why | T3 official guidance | 03.01, 03.02, 03.04, 03.06 | vision、persona、journey、PR/FAQ、user story への接続 | https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-product-development/start-with-why.html |
| S03 | AWS | Define success metrics | T3 official guidance | 03.01–03.03 | OKR、value driver、3–5 year adoption/growth horizon | https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-product-development/success-metrics.html |
| S04 | AWS | Develop the business case | T3 official guidance | 03.01 | value driver、revenue/cost saving、assumption refinement | https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-product-development/business-case.html |
| S05 | AWS | Prioritize features and plan delivery | T3 official guidance | 03.03, 03.07 | value-based roadmap、MVP、dynamic backlog、dependency | https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-product-development/features-delivery.html |
| S06 | GitLab | Product Principles | T3 official handbook | 03.01–03.03 | customer-centric innovation、dogfooding、quality over velocity、data over intuition、outcomes not launches | https://handbook.gitlab.com/handbook/product/product-principles/ |
| S07 | GitLab | Product Processes | T3 official handbook | 03.01–03.03, 03.07 | product development framework、direction pages、milestones、release posts | https://handbook.gitlab.com/handbook/product/product-processes/ |
| S08 | GitLab | Product Development Flow | T3 official handbook | 03 | validation backlog、problem validation、solution validation、planning/refinement、development | https://handbook.gitlab.com/handbook/product-development/how-we-work/product-development-flow/ |
| S09 | GitLab | Foundational Research | T3 official handbook | 03.04, 03.06 | mental models、behaviors、unmet needs、roadmap/product direction input | https://handbook.gitlab.com/handbook/product/ux/experience-research/foundational-research/ |
| S10 | GitLab | Jobs to be Done Research Playbook | T3 official handbook | 03.04–03.06 | job performer、job canvas、confidence level、workshop roles | https://handbook.gitlab.com/handbook/product/ux/jobs-to-be-done/jtbd-playbook/ |
| S11 | GitLab | Research Prioritization | T3 official handbook | 03.01–03.06 | quarterly research prioritization、business impact、dependency、triangulation | https://handbook.gitlab.com/handbook/product/ux/experience-research/research-prioritization/ |
| S12 | GOV.UK | How the discovery phase works | T0/T3 government manual | 03.01–03.06 | discovery の目的、4–8 weeks、problem reframing、stop/no-go、success measurement | https://www.gov.uk/service-manual/agile-delivery/how-the-discovery-phase-works |
| S13 | GOV.UK | Service Standard 1: Understand users and their needs | T0/T3 government manual | 03.04, 03.06 | user needs、context、assumption reduction、prototype/analytics/research | https://www.gov.uk/service-manual/service-standard/point-1-understand-user-needs |
| S14 | GOV.UK | Service Standard 2: Solve a whole problem | T0/T3 government manual | 03.01, 03.06 | whole journey、scope by user needs、work in the open、roadmap/research artifacts | https://www.gov.uk/service-manual/service-standard/point-2-solve-a-whole-problem |
| S15 | GOV.UK | Planning in agile | T0/T3 government manual | 03.02, 03.03, 03.07 | vision、objectives、measurable results、roadmap、user stories、visible planning | https://www.gov.uk/service-manual/agile-delivery/planning-agile |
| S16 | GOV.UK | Writing user stories | T0/T3 government manual | 03.07 | actor、narrative、goal、acceptance criteria、epic splitting、backlog priority | https://www.gov.uk/service-manual/agile-delivery/writing-user-stories |
| S17 | GOV.UK | Sharing user research findings | T0/T3 government manual | 03.04, 03.06, 03.07 | research wall、journey maps、personas、findings for prioritization/user stories/roadmap | https://www.gov.uk/service-manual/user-research/sharing-user-research-findings |
| S18 | Atlassian | What is Jira Product Discovery? | T2/T3 official product doc | 03.01–03.03 | ideas、insights、roadmaps、business-tech alignment、why behind work | https://support.atlassian.com/jira-product-discovery/docs/what-is-jira-product-discovery/ |
| S19 | Atlassian | What are insights? | T2/T3 official product doc | 03.01–03.06 | interview snippets、research links、support cases、sales opportunities、analytics、stakeholder messages | https://support.atlassian.com/jira-product-discovery/docs/what-are-insights/ |
| S20 | Atlassian | Understand the matrix view | T2/T3 official product doc | 03.03 | impact vs effort、confidence level による idea prioritization | https://support.atlassian.com/jira-product-discovery/docs/understand-the-matrix-view/ |
| S21 | Product Talk | Product Discovery Basics | T6 expert method | 03.01–03.03 | discovery と delivery の分離、what to build decision | https://www.producttalk.org/product-discovery/ |
| S22 | Product Talk | Continuous Discovery Mindsets | T6 expert method | 03.01–03.06 | weekly customer touchpoints、small research activities、desired outcome | https://www.producttalk.org/continuous-discovery-mindsets/ |
| S23 | Product Talk | Opportunity Solution Trees | T6 expert method | 03.01–03.06 | desired outcome、opportunity space、solution space、assumption testing | https://www.producttalk.org/opportunity-solution-trees/ |
| S24 | Product Talk | Assumption Testing | T6 expert method | 03 | whole idea ではなく underlying assumptions をテスト | https://www.producttalk.org/glossary-discovery-assumption-testing/ |
| S25 | NN/g | Journey Mapping 101 | T5/T6 methodology | 03.06 | goal 達成プロセスの可視化、actions/thoughts/emotions | https://www.nngroup.com/articles/journey-mapping-101/ |
| S26 | NN/g | Personas topic page | T5/T6 methodology | 03.04 | real information、attitudes、goals、pain points、analytics alone の限界 | https://www.nngroup.com/topic/personas/ |
| S27 | NIST | Human Centered Design | T0/T3 government/standards summary | 03.04, 03.06 | users/tasks/environments、user involvement、evaluation、iteration、whole experience | https://www.nist.gov/itl/iad/visualization-and-usability-group/human-factors-human-centered-design |
| S28 | Scrum Guides | The Scrum Guide 2020 | T0 community standard | 03.03, 03.07 | Product Goal、Product Backlog、Sprint Planning、Product Owner 役割 | https://scrumguides.org/scrum-guide.html |
| S29 | Agile Manifesto | Manifesto for Agile Software Development | T0 community principle | 03.03, 03.07 | customer collaboration、responding to change、working software | https://agilemanifesto.org/ |
| S30 | OMG | UML 2.5.1 | T0 formal specification | 03.05 | visualizing/specifying/documenting artifacts、use case の仕様背景 | https://www.omg.org/spec/UML/2.5.1/About-UML |
| S31 | ACM Queue / Ivar Jacobson | Use Cases are Essential | T5 expert article | 03.05 | actor、goal、main scenario、alternative conditions/flows | https://queue.acm.org/detail.cfm?id=3631182 |
| S32 | GitHub | GitHub public roadmap repository | T2 official artifact | 03.03 | features under work、stage、expected timing、public feedback discussions | https://github.com/github/roadmap |
| S33 | GitHub | Sunset Subversion support issue | T2 official artifact | 03.03 | low usage/high support burden による deprecation 判断 | https://github.com/github/roadmap/issues/915 |
| S34 | GitLab | Healthy Backlog at GitLab | T3 official handbook | 03.03, 03.07 | stale backlog、roadmap transparency、community feedback、cleanup rationale | https://handbook.gitlab.com/handbook/product-development/programs/backlog/ |

---

## 5. Evidence Map: 主要 claim

| Claim ID | 対象 | Claim | Evidence | Confidence |
|---|---|---|---|---|
| C001 | 03.01 | プロダクト戦略は、顧客価値と事業価値を同時に定義し、測定可能な outcome へ接続する必要がある。 | S01, S03, S04, S06 | A |
| C002 | 03.01–03.02 | why と vision が不明確なまま roadmap を作ると、意思決定が機能要求の寄せ集めになる。 | S02, S12, S15 | B |
| C003 | 03.02 | ビジョンは、PR/FAQ、persona、journey、epic/user story、roadmap の上位判断基準として使う。 | S02, S15 | A |
| C004 | 03.03 | roadmap は value、dependency、learning、MVP を反映して更新される dynamic artifact である。 | S05, S15, S32 | A |
| C005 | 03.03 | public roadmap は期待時期と stage を共有し、フィードバックを受ける transparency mechanism になり得る。 | S32, S33 | A/B |
| C006 | 03.04 | persona は analytics segment だけでは不十分で、attitude、goal、pain point、context などの質的理解を含む必要がある。 | S26, S27, S02, S10 | A/B |
| C007 | 03.05 | use case は actor が達成したい goal、main scenario、alternative conditions/flows を含み、例外条件を開発前に露出する。 | S30, S31 | A/B |
| C008 | 03.06 | journey map は goal 達成プロセスを action、thought、emotion、friction、system touchpoint として可視化する。 | S25, S02, S17 | A |
| C009 | 03.07 | user story は actor、narrative、goal、acceptance criteria を持ち、ユーザー価値を backlog priority に接続する。 | S16, S28 | A |
| C010 | 03 | discovery は「何を作るかを決める活動」であり、delivery は「作って出す活動」である。両者を連結しつつ混同しないことが重要である。 | S21, S08, S12 | B |
| C011 | 03.01–03.06 | 継続的 discovery は、週次の顧客接点、小さな研究活動、desired outcome への接続によって、学習遅延を下げる。 | S22, S23, S11 | B/C |
| C012 | 03.03, 03.07 | 古い backlog item を放置すると、重要度判断、貢献、リソース集中を阻害する。 | S34, S33 | B |
| C013 | 03 | discovery artifact は research wall、journey map、persona、roadmap、story として共有され、チームの意思決定に使われる必要がある。 | S17, S08, S18, S19 | A/B |
| C014 | 03 | 成熟した product discovery は、仮説全体ではなく、riskiest assumption を分解して検証する。 | S23, S24, S08 | B/C |

---

## 6. Cross-layer Operating Model

### 6.1 Artifact Chain

```text
Business Strategy / Market Thesis
  -> Product Strategy
  -> Product Vision / PR-FAQ / North Star
  -> Success Metrics / OKR / Business Case
  -> Persona / JTBD / Segment Hypotheses
  -> As-is Journey / Service Blueprint / Friction Map
  -> Opportunity Map / Use Cases / Assumptions
  -> Roadmap Themes / MVP / Experiment Plan
  -> Epics / User Stories / Acceptance Criteria
  -> Delivery / Release / Instrumentation
  -> Learning Review / Roadmap Update / Backlog Cleanup
```

### 6.2 意思決定ゲート

| Gate | 目的 | 入力 | 判定基準 | 可能な出力 |
|---|---|---|---|---|
| G0 Problem Framing | 解くべき問題かを決める | 顧客観察、事業課題、制約、既存データ | 問題がユーザー視点で表現され、predefined solution になっていないか | discovery 継続、範囲変更、停止 |
| G1 Outcome & Vision | 成功状態を定義する | strategy、customer value、business outcome | measurable result、north-star、非目標が明確か | vision、OKR、success metrics |
| G2 Evidence Confidence | persona/journey/use case を採用する | research、analytics、support、sales、stakeholder insight | 質的・量的証拠がつながっているか、反証可能か | persona、journey、use-case set、unknowns |
| G3 Opportunity Prioritization | どの機会に賭けるか | opportunity tree、impact/effort/confidence、dependency | strategic fit、customer impact、business impact、confidence、risk | target opportunity、experiment plan、MVP scope |
| G4 Roadmap Commitment | どの順序で扱うか | target opportunity、capacity、dependency、technical risk | value sequencing、MVP learning、dependency feasibility | roadmap item、theme、milestone、defer/stop |
| G5 Story Readiness | 実装可能単位へ落とす | use case、journey friction、design、acceptance criteria | actor/narrative/goal が明確で、acceptance criteria が検証可能か | user story、epic split、reject/rework |
| G6 Learn / Pivot / Sunset | 継続・転換・終了を決める | metrics、usage、qualitative feedback、support burden | outcome trend、adoption、maintenance burden、strategic relevance | scale、iterate、pivot、deprecate、backlog cleanup |

### 6.3 標準 cadence

| Cadence | 会議体 / activity | 主な layer | 成果物 |
|---|---|---|---|
| 年次 / 半期 | 事業戦略・投資テーマレビュー | 03.01 | market thesis、investment thesis、portfolio priorities |
| 四半期 | OKR / research prioritization / direction review | 03.01–03.03, 03.04–03.06 | OKR、research backlog、roadmap update、direction page |
| 月次 | roadmap / opportunity portfolio review | 03.03, 03.06 | roadmap diff、dependency update、experiment result |
| 週次 | customer touchpoint / discovery synthesis / story grooming | 03.04–03.07 | interview notes、insights、journey update、story candidates |
| sprint | planning / review / retro / delivery learning | 03.03, 03.07 | sprint goal、selected stories、acceptance results、retro actions |
| event-driven | incident、major customer feedback、market shock、deprecation | 03 | reprioritization、sunset notice、business case refresh |

---

# 7. Clone Specs

## 7.1 Layer 03.01: プロダクト戦略

### Definition

プロダクト戦略は、どの顧客・市場・課題・価値仮説に対して、なぜプロダクトへ投資するのかを決定し、その投資判断を測定可能な事業成果と顧客成果に接続するレイヤーである。機能リストではなく、投資 thesis、差別化仮説、価値捕捉、優先順位、成功指標、停止条件を定義する。

### Frontier Exemplars

| Exemplar | 採用理由 | Evidence |
|---|---|---|
| AWS product strategy / working backwards | why、vision、metrics、business case、feature prioritization を価値実現の連続プロセスとして公開している。 | S01–S05 |
| GitLab Product Principles | customer-centric innovation、dogfooding、data over intuition、outcomes not launches を product principle として公開している。 | S06 |
| GOV.UK Discovery / Service Standard | predefined solution ではなく problem を理解し、停止判断も有効な discovery 成果とする。 | S12–S14 |
| Product Talk | discovery を what-to-build decision とし、desired outcome から opportunity/solution/assumption を展開する。 | S21–S24 |

### Core Philosophy

1. プロダクト戦略は「機能を増やす計画」ではなく、「顧客価値と事業成果の間にある仮説を管理する仕組み」である。
2. 戦略の最小単位は、market、customer、problem、value driver、metric、constraint、stop condition の組である。
3. 戦略は一度決めて固定するものではなく、customer evidence、value realization、technical feasibility、business case によって更新される。
4. 先端組織は、launch を成果とせず、usage、adoption、retention、revenue、cost reduction、risk reduction などの outcome で正しさを判定する。

### Decision Model

| Field | 内容 |
|---|---|
| Inputs | 事業目標、市場構造、顧客セグメント、顧客課題、競争環境、既存 usage/support/sales データ、研究結果、技術制約、財務制約 |
| Decision Object | どの顧客価値と事業成果に投資し、どの機会を捨てるか |
| Criteria | strategic fit、customer pain、business value、differentiation、feasibility、risk、time-to-learning、evidence confidence |
| Priorities | measurable outcome、customer evidence、business case、learning velocity、portfolio focus |
| Prohibitions | executive wish-list をそのまま roadmap 化すること、測定不能な「戦略目標」を置くこと、顧客課題なしに機能を約束すること |
| Thresholds | success metric は少なくとも baseline/target/measurement owner を持つ。major investment は business case と value driver を持つ。 |
| Owners | CPO、VP Product、GM、Product Lead、Finance partner、UX Research Lead、Engineering Lead |
| Cadence | 年次・半期の investment thesis、四半期 OKR、月次 roadmap/value review、event-driven reprioritization |
| Outputs | product strategy brief、OKR、business case、target customer、value driver map、investment themes、stop/pivot criteria |
| Controls | strategy review、metric instrumentation review、research evidence check、financial review、technical feasibility review |
| Metrics | adoption、activation、retention、revenue、margin、cost saving、NPS/CSAT、time-to-value、support burden、strategic option value |

### Operating Model

1. **Strategy framing**: 事業目標、顧客課題、制約を整理し、predefined solution を problem statement に戻す。
2. **Customer/value discovery**: research、support、sales、analytics、market data を統合し、顧客価値仮説を作る。
3. **Outcome definition**: OKR、success metric、baseline、target、measurement owner を設定する。
4. **Business case**: revenue、cost saving、efficiency、risk reduction、strategic positioning を定量化し、assumption を明示する。
5. **Portfolio prioritization**: 投資テーマを impact、confidence、dependency、cost、risk で比較する。
6. **Review and revise**: 実験・リリース・顧客反応で戦略仮説を更新し、不要な backlog/roadmap item を除去する。

### Technical / Business Specification

最低限の strategy brief は以下を含む。

| 項目 | 必須内容 |
|---|---|
| Problem statement | 対象顧客、現状の摩擦、解決しない場合の損失 |
| Target customer | persona/JTBD/segment、除外対象 |
| Value hypothesis | 顧客価値、事業価値、なぜ今か |
| Success metrics | baseline、target、measurement method、owner、レビュー cadence |
| Business case | revenue/cost/risk/strategic value、assumption、confidence |
| Strategic tradeoffs | やること、やらないこと、延期すること |
| Discovery plan | 未検証仮説、検証方法、判断日 |
| Roadmap implication | 主要テーマ、MVP、依存関係、停止条件 |

### Failure Modes

| Failure | 症状 | 防止策 |
|---|---|---|
| Feature-list strategy | 戦略文書が機能名の羅列になる | outcome、customer problem、business case を必須にする |
| Vanity metrics | 成果が pageview や launch count に偏る | leading/lagging metric と value driver を接続する |
| Executive anchoring | 上位者の案が discovery を迂回する | problem statement と research evidence を gate にする |
| Static portfolio | 一度決めた roadmap を学習で変えない | 月次 value review と explicit pivot/stop criteria |
| Unbounded discovery | 学習は多いが投資判断が進まない | time-box、decision owner、confidence threshold を置く |

### Anti-patterns

- 戦略を「来期に作る機能一覧」と同義にする。
- 顧客価値と事業価値のどちらか一方だけで投資を正当化する。
- 成功指標を後付けする。
- persona、journey、story を戦略と無関係な UX artifact として分離する。
- stale backlog を「将来の選択肢」と誤認して維持し続ける。

### Maturity Model

| Level | 状態 | 判定基準 |
|---:|---|---|
| 0 | 未整備 | strategy がなく、機能要求への反応で動く |
| 1 | 個人依存 | PM の暗黙判断で優先順位が決まる |
| 2 | 文書化 | product strategy brief と OKR があるが、測定と更新が弱い |
| 3 | 標準化 | customer evidence、business case、success metric、roadmap が接続される |
| 4 | 計測・自動化 | instrumentation と dashboard により strategy review が定期化される |
| 5 | 自律改善 | portfolio が学習で動的に更新され、stop/pivot/deprecate が自然に行われる |

### Clone Implementation Guide

1. すべての新規 product initiative に `strategy brief` を義務化する。
2. brief は `problem / target customer / value hypothesis / metrics / business case / assumptions / roadmap implication` を必須にする。
3. 顧客 evidence がない major initiative は discovery backlog に戻す。
4. 四半期ごとに strategy review を行い、metric trend、research result、support burden、market change で investment theme を更新する。
5. stale backlog cleanup を運用に入れ、戦略との接続が切れた item を close / archive / reframe する。

### Confidence & Unknowns

- 確度A: AWS、GitLab、GOV.UK の公開文書に基づく戦略・指標・discovery の構造。
- 確度B: Product Talk の continuous discovery / opportunity tree を実務補助パターンとして採用する点。
- 不明点: 各組織の内部投資配分、非公開の財務閾値、実際の roadmap 承認権限。

---

## 7.2 Layer 03.02: プロダクトビジョン

### Definition

プロダクトビジョンは、プロダクトが将来どの状態を実現し、どの顧客価値を提供し、何をしないかを明示するレイヤーである。ビジョンは宣伝文句ではなく、戦略、ロードマップ、ペルソナ、ジャーニー、ユースケース、ユーザーストーリーを整合させる上位判断基準である。

### Frontier Exemplars

| Exemplar | 採用理由 | Evidence |
|---|---|---|
| AWS Start with why / PR-FAQ | vision、persona、journey、PR/FAQ、epics/user stories、roadmap の接続を明示する。 | S02 |
| GOV.UK Planning in Agile | vision、objectives、roadmap、user stories の順で可視化し、stakeholder ownership を作る。 | S15 |
| GitLab Direction Pages / Product Principles | category/stage/group direction と customer-centric principles によってビジョンを公開・分散運用する。 | S06, S07 |

### Core Philosophy

1. ビジョンは「魅力的な表現」ではなく「意思決定の制約」である。
2. 良いビジョンは、顧客、問題、望ましい将来状態、事業成果、除外対象を含む。
3. ビジョンは roadmap の前提であり、roadmap の変更時にも参照される。
4. vision statement 単体では弱く、PR/FAQ、target journey、success metrics、persona とセットで有効になる。

### Decision Model

| Field | 内容 |
|---|---|
| Inputs | product strategy、顧客研究、事業制約、技術制約、競争文脈、既存 product direction |
| Decision Object | 将来状態、north-star、価値仮説、非目標、トレードオフ |
| Criteria | clarity、customer relevance、strategic fit、measurability、decision usefulness、durability、communicability |
| Priorities | why before what、one coherent narrative、tradeoff explicitness、stakeholder alignment |
| Prohibitions | 競合追随だけの vision、測定不能な抽象 slogan、すべての顧客を対象にする曖昧さ |
| Owners | Product Lead、Design Lead、Engineering Lead、Executive Sponsor |
| Cadence | strategy update 時、major discovery 終了時、quarterly direction review、market shock 発生時 |
| Outputs | vision statement、north-star narrative、PR/FAQ、non-goals、target journey、principles |
| Controls | stakeholder review、research evidence check、roadmap alignment check、story traceability check |
| Metrics | stakeholder alignment、roadmap traceability、decision latency、rework rate、strategy/story traceability |

### Operating Model

1. **Vision drafting**: why、for whom、future state、business/customer value を 1 ページで定義する。
2. **Narrative expansion**: PR/FAQ または equivalent narrative で、顧客が受け取る価値と想定質問を具体化する。
3. **Artifact linkage**: persona、target journey、success metrics、roadmap themes、epics/user stories に vision reference を付与する。
4. **Tradeoff review**: what we will not do、who is not the primary user、which use cases are out of scope を明記する。
5. **Revalidation**: research result、market change、metrics underperformance が出たら vision を更新または再確認する。

### Technical / Business Specification

ビジョン文書の必須構造。

```text
1. Target user / customer
2. Current problem and why it matters
3. Desired future state
4. Customer value
5. Business value
6. Differentiation / strategic edge
7. Non-goals / exclusions
8. Success indicators
9. Roadmap implications
10. Evidence and unknowns
```

### Failure Modes

| Failure | 症状 | 防止策 |
|---|---|---|
| Slogan vision | かっこいいが優先順位を決められない | vision に non-goals と measurable outcome を入れる |
| Vision-roadmap disconnect | roadmap item が vision と接続しない | roadmap item ごとに vision theme を紐づける |
| Stakeholder drift | 部門ごとに違う解釈を持つ | PR/FAQ と FAQ を使い、想定反論を明文化する |
| Frozen vision | 環境変化後も更新されない | quarterly direction review と research trigger を置く |

### Anti-patterns

- vision を経営資料の冒頭飾りにする。
- ビジョンに「誰を優先しないか」を書かない。
- vision と success metric を分離する。
- vision から story までの traceability を持たない。

### Maturity Model

| Level | 状態 | 判定基準 |
|---:|---|---|
| 0 | 未整備 | vision が存在しない |
| 1 | 標語 | vision はあるが意思決定に使われない |
| 2 | 文書化 | vision statement と high-level goals がある |
| 3 | 接続済み | vision が OKR、roadmap、persona、journey、story に接続される |
| 4 | 検証可能 | vision ごとに success indicator と evidence review がある |
| 5 | 適応的 | vision が市場・顧客学習で更新され、全 artifact が差分追随する |

### Clone Implementation Guide

1. product/team ごとに 1 ページ vision を作る。
2. vision は `future state / customer value / business value / non-goals / evidence / success indicators` を必須化する。
3. roadmap、persona、journey、story の各 artifact に vision theme ID を付ける。
4. 四半期ごとに vision drift を確認し、優先順位変更時は vision 更新または roadmap 修正のどちらかを選ぶ。

### Confidence & Unknowns

- 確度A: AWS と GOV.UK の vision-to-roadmap/story linkage。
- 確度B: GitLab の direction pages をビジョン運用の exemplar とする点。
- 不明点: 各企業の内部 vision approval board、vision change の非公開判断基準。

---

## 7.3 Layer 03.03: プロダクトロードマップ

### Definition

プロダクトロードマップは、価値仮説、機会、機能、実験、依存関係、マイルストーンを、顧客価値と事業成果の観点で順序づけるレイヤーである。正しくは「約束表」ではなく、学習と価値実現に応じて更新される decision artifact である。

### Frontier Exemplars

| Exemplar | 採用理由 | Evidence |
|---|---|---|
| AWS feature prioritization / delivery planning | roadmap を customer/company value、technical dependency、MVP、dynamic backlog で扱う。 | S05 |
| GOV.UK Planning in Agile | vision、objectives、roadmap、user stories を接続し、roadmap を可視化・定期見直しする。 | S15 |
| GitHub Public Roadmap | stage、expected timing、feedback discussions を公開する実 artifact。deprecation/sunset 判断も観測できる。 | S32, S33 |
| Atlassian Jira Product Discovery | insights、ideas、matrix、roadmaps、delivery work connection を tool artifact として提供する。 | S18–S20 |
| GitLab Product Processes / Healthy Backlog | direction pages、milestone、release post、backlog cleanup を公開している。 | S07, S34 |

### Core Philosophy

1. ロードマップは outcome と opportunity を delivery に接続する translation layer である。
2. item の優先順位は、impact、confidence、effort、dependency、risk、strategic fit、learning value で決まる。
3. roadmap は stage と uncertainty を表現すべきであり、すべてを同じ確度の約束として扱ってはいけない。
4. backlog は roadmap の無限倉庫ではない。古い item は再評価、統合、close、deprecate する。

### Decision Model

| Field | 内容 |
|---|---|
| Inputs | strategy、vision、OKR、customer insights、opportunity map、technical dependencies、capacity、regulatory/market deadline、support burden |
| Decision Object | どの roadmap theme/item を、どの stage・順序・粒度・確度で提示するか |
| Criteria | customer impact、business impact、confidence、effort、technical dependency、risk、MVP feasibility、learning value、strategic fit |
| Priorities | outcome over output、explicit uncertainty、dependency visibility、short feedback cycle、stakeholder alignment |
| Prohibitions | 全 item を committed date として扱う、根拠のない機能要望を roadmap に載せる、古い backlog を放置する |
| Thresholds | roadmap item は owner、target outcome、evidence, stage、dependency、review date を持つ。committed item は delivery capacity と acceptance criteria を持つ。 |
| Owners | Product Manager、Product Operations、Engineering Manager、Design Lead、Program Manager |
| Cadence | quarterly roadmap review、monthly dependency review、weekly delivery sync、event-driven replan |
| Outputs | outcome roadmap、theme roadmap、public/internal roadmap、dependency map、MVP scope、release notes、deprecation plan |
| Controls | roadmap review board、capacity check、research confidence gate、dependency gate、sunset/deprecation review |
| Metrics | roadmap item hit-rate、outcome attainment、learning velocity、stale backlog ratio、dependency slip、customer-facing change transparency |

### Operating Model

1. **Idea intake**: customer insight、support case、sales signal、analytics、stakeholder request を idea/opportunity として収集する。
2. **Evidence attachment**: idea に insight、persona、journey friction、metric、business case を紐付ける。
3. **Prioritization**: impact vs effort、confidence、dependency、strategic fit で比較する。
4. **Stage assignment**: explore、validate、plan、build、launch、deprecate などの stage を割り当てる。
5. **Roadmap communication**: internal roadmap と public roadmap の粒度を分け、確度と timing を明示する。
6. **Review/update**: metric と discovery result により item を promote、defer、merge、close、sunset する。

### Technical / Business Specification

roadmap item の標準 schema。

| Field | 必須性 | 内容 |
|---|---|---|
| roadmap_item_id | 必須 | 一意 ID |
| theme | 必須 | vision/strategy theme |
| target outcome | 必須 | 測定したい顧客/事業成果 |
| target persona/JTBD | 必須 | 誰の課題か |
| evidence refs | 必須 | research、support、sales、analytics など |
| confidence | 必須 | low / medium / high または 0–100 |
| impact | 必須 | customer/business impact |
| effort/cost | 必須 | engineering/design/research effort |
| dependency | 必須 | technical/org/legal dependency |
| stage | 必須 | explore / validate / plan / build / launch / deprecate |
| owner | 必須 | PM/EM/DRI |
| review date | 必須 | 更新期限 |
| communication level | 必須 | internal only / customer-facing / public |

### Failure Modes

| Failure | 症状 | 防止策 |
|---|---|---|
| Date theater | 根拠のない日付が約束化する | stage と confidence を公開し、committed と exploratory を分ける |
| Roadmap as backlog | 低確度の要望が大量に積まれる | evidence threshold と stale cleanup を設定する |
| Dependency blindness | 技術依存が後で発覚する | engineering dependency review を roadmap gate に入れる |
| No deprecation path | やめる機能の判断が遅れる | usage/support burden/strategic relevance による sunset gate |
| Misaligned public roadmap | 外部期待と内部計画が乖離する | public wording、feedback loop、change log を管理する |

### Anti-patterns

- roadmap を営業約束リストにする。
- impact/effort/confidence のない item を roadmap に残す。
- roadmap と user story backlog を同じ粒度で混在させる。
- roadmap 変更理由を記録しない。
- close / deprecate / sunset を失敗として扱い、意思決定から除外する。

### Maturity Model

| Level | 状態 | 判定基準 |
|---:|---|---|
| 0 | 未整備 | roadmap がない、または口頭で管理 |
| 1 | 納期表 | 機能名と日付だけの roadmap |
| 2 | テーマ化 | strategy theme と quarter 単位の planning がある |
| 3 | 証拠接続 | item ごとに outcome、evidence、confidence、owner がある |
| 4 | 動的更新 | metric/research/dependency で roadmap が定期更新される |
| 5 | 透明・適応 | public/internal roadmap、sunset、backlog cleanup、learning loop が成熟している |

### Clone Implementation Guide

1. roadmap item schema を導入し、`outcome / evidence / confidence / dependency / owner / review date` を必須化する。
2. roadmap を `Now / Next / Later` または `Explore / Validate / Build / Launch` など stage-based にする。
3. monthly review で stale item、low-confidence item、dependency-risk item を処理する。
4. public communication が必要な場合は、stage と expected timing を明示し、change log を残す。
5. deprecation/sunset は usage、support burden、strategic fit を使って明文化する。

### Confidence & Unknowns

- 確度A: AWS、GOV.UK、GitHub、Atlassian の公開 roadmap/prioritization artifact。
- 確度B: GitLab backlog cleanup と GitHub sunset issue から導いた stale/deprecation pattern。
- 不明点: 各組織の内部 capacity model、営業との commitment ルール、非公開 roadmap の粒度。

---

## 7.4 Layer 03.04: ペルソナ

### Definition

ペルソナは、対象ユーザーの属性、行動、目標、動機、制約、痛み、環境、意思決定文脈を表現し、プロダクト判断の proxy とするレイヤーである。正しくは、デモグラフィックや架空キャラクターではなく、実証された顧客理解を設計・優先順位・検証に接続する artifact である。

### Frontier Exemplars

| Exemplar | 採用理由 | Evidence |
|---|---|---|
| NN/g Personas | real information、attitudes/goals/pain points、analytics alone の限界を明示する。 | S26 |
| NIST Human Centered Design | users、tasks、environments の明示的理解、users involvement、evaluation、iteration を示す。 | S27 |
| AWS Start with why | persona を顧客行動・利用理由理解に使い、journey と PR/FAQ へ接続する。 | S02 |
| GitLab JTBD / Foundational Research | mental model、behavior、unmet needs、job performer、job canvas、confidence level を公開している。 | S09, S10 |
| GOV.UK Understand users | user needs、context、assumption reduction を service standard とする。 | S13 |

### Core Philosophy

1. persona は「誰向けか」を曖昧にしないための decision proxy である。
2. 先端組織では persona は research evidence と confidence level を持つ。
3. analytics segment は有用だが、attitude、goal、pain point、context は定性的研究で補う必要がある。
4. persona は固定キャラクターではなく、学習により更新される living artifact である。

### Decision Model

| Field | 内容 |
|---|---|
| Inputs | user interviews、field studies、support tickets、analytics、sales calls、survey、usage logs、JTBD workshops、domain research |
| Decision Object | どの persona/JTBD を primary、secondary、excluded とするか |
| Criteria | evidence quality、strategic relevance、behavioral distinction、need severity、addressability、market/business value、design implication |
| Priorities | behavior over demographics、needs over labels、evidence confidence、design usefulness、traceability |
| Prohibitions | analytics だけで persona を作る、職種名だけの persona、全ユーザーを一つにまとめる、古い persona を更新しない |
| Thresholds | persona は evidence refs、last validated date、confidence、primary goals、pain points、usage context を持つ。primary persona は roadmap/story へ trace される。 |
| Owners | UX Researcher、Product Manager、Product Designer、Data Analyst |
| Cadence | major discovery 時、quarterly research review、new segment launch 時、metric anomaly 発生時 |
| Outputs | persona canvas、JTBD canvas、segment map、research repository、confidence score、excluded persona list |
| Controls | research quality review、triangulation、persona-story traceability、stale review |
| Metrics | persona coverage、research recency、story traceability、segment adoption、support pain reduction、decision reuse rate |

### Operating Model

1. **Hypothesis persona**: initial market/segment hypothesis を立てる。ただし confidence low と明示する。
2. **Evidence collection**: interview、support、sales、analytics、behavior observation を組み合わせる。
3. **Synthesis**: goals、pain points、constraints、current workaround、decision criteria、environment を抽出する。
4. **JTBD alignment**: persona が「属性」だけに落ちないよう、達成したい job と outcome を紐づける。
5. **Artifact publication**: persona を roadmap、journey、use case、story の参照元にする。
6. **Review/update**: 新しい research、usage shift、support issue で persona を更新または retired にする。

### Technical / Business Specification

persona canvas の必須 field。

| Field | 内容 |
|---|---|
| persona_id | 一意 ID |
| name/label | 判断を助ける短いラベル。属性名だけにしない |
| primary job / goal | 達成したい job、目的、成功条件 |
| context | 利用環境、組織文脈、制約、頻度 |
| behavior | 現在の行動、workaround、利用パターン |
| pain points | 摩擦、失敗、未充足ニーズ |
| decision criteria | 購買・利用・採用判断の基準 |
| evidence refs | interview、analytics、support、sales、research report |
| confidence | high/medium/low と根拠 |
| product implication | roadmap theme、journey friction、story への示唆 |
| last validated | 最終確認日 |
| owner | researcher/PM |

### Failure Modes

| Failure | 症状 | 防止策 |
|---|---|---|
| Fictional persona | 実在しない平均像を作る | evidence refs と confidence を必須化する |
| Demographic trap | 年齢・性別・職種だけで設計判断する | behavior、goal、pain point、context を必須にする |
| Too many personas | 優先順位が決められない | primary/secondary/excluded を明示する |
| Stale persona | 市場変化後も古い persona を使う | last validated と review cadence を設定する |
| No traceability | persona が story/roadmap に使われない | artifact linkage を mandatory にする |

### Anti-patterns

- 「30代男性マネージャー」のような属性だけの persona。
- 既存顧客の最大セグメントをそのまま primary persona とみなす。
- persona を UX チームの壁紙にして、roadmap・story と接続しない。
- 反証データが出ても persona を更新しない。

### Maturity Model

| Level | 状態 | 判定基準 |
|---:|---|---|
| 0 | 未整備 | 誰向けかが不明 |
| 1 | 仮説 | PM/営業の印象で persona が作られる |
| 2 | 文書化 | persona canvas があるが evidence/confidence が弱い |
| 3 | 研究接続 | interview/analytics/support と persona が接続される |
| 4 | 運用接続 | persona が roadmap、journey、story、metric に trace される |
| 5 | 動的管理 | persona/JTBD が research repository と連動し、更新・retire される |

### Clone Implementation Guide

1. persona を `hypothesis / validated / retired` の状態で管理する。
2. persona canvas に `evidence refs / confidence / last validated / product implication` を必須化する。
3. roadmap item と user story に primary persona ID を紐づける。
4. quarterly research review で stale persona を検出する。
5. analytics だけではなく、少なくとも interview/support/sales など別 family の証拠で補強する。

### Confidence & Unknowns

- 確度A: NN/g、NIST、GOV.UK、AWS の user/persona/HCD principles。
- 確度B: GitLab JTBD と foundational research を persona operating model に接続する点。
- 不明点: 各組織の persona 更新頻度、persona confidence の内部閾値。

---

## 7.5 Layer 03.05: ユースケース

### Definition

ユースケースは、actor が system との相互作用を通じて特定の goal を達成する scenario を定義するレイヤーである。正常系だけでなく、代替条件、例外、失敗、関連 actor、system boundary を明確にすることで、要求、設計、テスト、ユーザーストーリーの橋渡しを行う。

### Frontier Exemplars

| Exemplar | 採用理由 | Evidence |
|---|---|---|
| OMG UML 2.5.1 | UML を distributed object systems の artifact を visualizing/specifying/documenting する formal specification として定義する。 | S30 |
| Ivar Jacobson / ACM Queue | actor、goal、main scenario、alternative conditions/flows という use case の実務要素を説明する。 | S31 |
| GOV.UK / AWS | user need、journey、story への接続を通じ、use case 的な scenario thinking を実装判断へつなげる。 | S02, S13, S16 |
| GitLab Product Development Flow | problem/solution validation から build phase へ接続する artifact flow を示す。 | S08 |

### Core Philosophy

1. ユースケースは画面仕様ではなく、actor が system を使って goal を達成する行動単位である。
2. 良いユースケースは、main success scenario と alternatives/failures を同時に扱う。
3. ユースケースは、ペルソナ/JTBD とユーザーストーリーの間に位置し、要求の抜け漏れと例外を露出する。
4. UI や実装方式を早く決めすぎず、actor、goal、boundary、observable result を先に明確にする。

### Decision Model

| Field | 内容 |
|---|---|
| Inputs | persona/JTBD、journey friction、business rule、domain constraint、system boundary、regulatory/security requirements |
| Decision Object | どの actor が、どの system boundary 内で、どの goal を達成し、どの alternative/exception を扱うか |
| Criteria | actor clarity、goal value、scenario completeness、exception coverage、testability、domain consistency、implementation neutrality |
| Priorities | goal before UI、boundary clarity、alternative coverage、shared understanding、test derivability |
| Prohibitions | UI 操作手順だけを書く、正常系だけを書く、actor と stakeholder を混同する、implementation detail を先に固定する |
| Thresholds | use case は primary actor、goal、precondition、main scenario、alternative flow、postcondition、business rule refs を持つ。 |
| Owners | Product Manager、Business Analyst、Solution Architect、Designer、QA Lead |
| Cadence | major feature discovery、domain modeling、before story splitting、test planning |
| Outputs | use-case brief、actor map、scenario flow、alternative flow、system boundary diagram、acceptance test seed |
| Controls | domain review、security/privacy review、scenario walkthrough、test coverage review |
| Metrics | scenario coverage、defect escape from missing edge cases、story rework rate、test case derivation rate |

### Operating Model

1. **Actor identification**: primary actor、secondary actor、external systems を定義する。
2. **Goal definition**: actor が達成したい goal を product outcome と接続する。
3. **Boundary setting**: subject/system boundary と外部依存を明確にする。
4. **Main scenario**: 最も単純な成功フローを step-by-step で記述する。
5. **Alternative/exception analysis**: 失敗条件、分岐、復旧、失敗終了を列挙する。
6. **Story derivation**: use case を epic/story/acceptance criteria に分解する。
7. **Test derivation**: main/alternative flow を acceptance test と QA scenario に変換する。

### Technical / Business Specification

use-case brief の標準 schema。

| Field | 内容 |
|---|---|
| use_case_id | 一意 ID |
| name | primary actor が達成したい goal を表す動詞句 |
| primary actor | goal の主体 |
| secondary actors | 支援 actor / external systems |
| trigger | use case 開始条件 |
| preconditions | 開始前に真である条件 |
| main success scenario | actor/system の相互作用ステップ |
| alternative flows | 分岐・例外・復旧・失敗終了 |
| postconditions | 成功/失敗後の状態 |
| business rules | 関連 rule / policy / constraint |
| linked persona/JTBD | persona/JTBD refs |
| linked journey point | journey stage/friction refs |
| linked stories/tests | user story / acceptance test refs |
| confidence | high/medium/low と根拠 |

### Failure Modes

| Failure | 症状 | 防止策 |
|---|---|---|
| UI-script confusion | button click sequence が use case になる | actor goal と system boundary を先に定義する |
| Happy-path bias | exception が開発後に発覚する | alternative flow を必須 field にする |
| Actor ambiguity | 誰の goal か不明 | primary/secondary actor を区別する |
| Overengineering | use case が巨大で更新不能 | high-value scenario から始め、story に分解する |
| No test linkage | use case が実装・テストに接続しない | acceptance criteria/test case と linked refs を持つ |

### Anti-patterns

- 「ログイン画面でボタンを押す」のような UI 手順をユースケース名にする。
- alternative flow を「後で考える」として省く。
- actor を組織名や内部部署だけで表し、実際の利用者の goal を消す。
- use case を完成文書として固定し、discovery で更新しない。

### Maturity Model

| Level | 状態 | 判定基準 |
|---:|---|---|
| 0 | 未整備 | 要求が会話とチケットに分散 |
| 1 | 正常系のみ | happy path はあるが例外がない |
| 2 | 文書化 | actor、goal、main scenario がある |
| 3 | 例外接続 | alternative flow、business rules、boundary がある |
| 4 | 実装接続 | story、acceptance criteria、test case と trace される |
| 5 | モデル駆動 | domain model、journey、metrics、QA coverage と継続的に同期する |

### Clone Implementation Guide

1. high-risk/high-value capability から use case brief を作る。
2. use case は UI ではなく actor goal で命名する。
3. main scenario と alternative flow を必須にする。
4. story splitting 前に scenario walkthrough を行う。
5. use case から acceptance criteria と test case を派生させる。

### Confidence & Unknowns

- 確度A: OMG UML 仕様背景。
- 確度B: ACM Queue / Ivar Jacobson の実務解説、GOV.UK/AWS/GitLab との artifact chain 接続。
- 不明点: 各先端企業の内部 use-case template、正式 UML の採用度。

---

## 7.6 Layer 03.06: ジャーニー

### Definition

ジャーニーは、ユーザーまたは顧客が目的を達成するまでの行動、接点、思考、感情、摩擦、制約、システム関与、成功/失敗条件を可視化し、改善機会とプロダクト要求を導くレイヤーである。単なる体験図ではなく、as-is と target の差分を discovery と roadmap へ接続する artifact である。

### Frontier Exemplars

| Exemplar | 採用理由 | Evidence |
|---|---|---|
| NN/g Journey Mapping | journey map を goal 達成プロセスの可視化と定義し、actions、thoughts、emotions の narrative を示す。 | S25 |
| AWS customer journey | as-is journey、goals、friction、target journey、supporting systems を vision の構成要素にする。 | S02 |
| GOV.UK Service Manual | whole problem、service context、research sharing、journey maps/research wall を product roadmap/story に接続する。 | S12–S17 |
| GitLab Foundational Research | mental models、behaviors、unmet needs、problem areas を product direction/roadmap input にする。 | S09 |
| Product Talk Opportunity Solution Tree | desired outcome から opportunity space を可視化し、solution/assumption testing へ接続する。 | S23, S24 |

### Core Philosophy

1. ジャーニーは、組織のプロセスではなく、ユーザーが目的を達成する流れを中心に置く。
2. as-is journey は現在の摩擦を露出し、target journey は改善仮説を明確にする。
3. journey map は persona、use case、roadmap、story、metrics の接続点である。
4. journey は研究結果の展示物ではなく、優先順位と設計判断に使う decision artifact である。

### Decision Model

| Field | 内容 |
|---|---|
| Inputs | interviews、field studies、diary studies、support cases、analytics、service data、persona/JTBD、system constraints |
| Decision Object | どの journey stage / friction / opportunity を改善対象にし、target journey をどう設計するか |
| Criteria | user pain severity、frequency、business impact、service boundary、technical feasibility、risk、measurability、cross-team dependency |
| Priorities | whole experience、as-is before target、friction evidence、opportunity clarity、measurement points |
| Prohibitions | 組織都合のプロセス図を journey と呼ぶ、research evidence なしに感情を推測する、target journey だけ作る |
| Thresholds | journey map は persona/JTBD、goal、stages、actions、touchpoints、pain points、emotion/thoughts、evidence refs、metrics、opportunities を持つ。 |
| Owners | UX Researcher、Service Designer、Product Manager、Data Analyst、Support/Operations representative |
| Cadence | discovery phase、major redesign、quarterly research synthesis、post-launch journey review |
| Outputs | as-is journey map、target journey map、service blueprint、opportunity map、research wall、journey metrics |
| Controls | research evidence review、cross-functional walkthrough、whole-problem review、accessibility/privacy review |
| Metrics | task success、time-to-value、drop-off、conversion、support contacts、friction score、CSAT/NPS、journey-stage adoption |

### Operating Model

1. **Scope and goal**: journey の user goal、persona/JTBD、境界を決める。
2. **As-is evidence**: interview、observation、analytics、support data で現状 journey を記述する。
3. **Friction synthesis**: pain points、workarounds、drop-off、emotion、dependencies を整理する。
4. **Opportunity mapping**: friction を opportunity に変換し、impact/confidence/effort で評価する。
5. **Target journey**: 改善後の体験、必要 system capability、測定点を描く。
6. **Roadmap/story translation**: target journey の差分を use case、epic、story、experiments に変換する。
7. **Learning loop**: release 後の journey metric と qualitative feedback で更新する。

### Technical / Business Specification

journey map の標準 schema。

| Field | 内容 |
|---|---|
| journey_id | 一意 ID |
| persona/JTBD | 対象ユーザー / job |
| goal | 達成目的 |
| scope | start/end、channel、service boundary |
| stages | journey stages |
| actions | 各 stage の user actions |
| touchpoints | product、human support、external systems |
| thoughts/emotions | research に基づく心理・感情 |
| pain points/frictions | 摩擦、失敗、待ち時間、混乱 |
| evidence refs | interview、analytics、support、field notes |
| opportunities | 改善機会、仮説 |
| target journey | 改善後 flow |
| metrics | stage-level measurement |
| linked roadmap/stories | roadmap item、use case、story refs |
| last validated | 最終確認日 |

### Failure Modes

| Failure | 症状 | 防止策 |
|---|---|---|
| Pretty map syndrome | 見栄えは良いが意思決定に使われない | opportunity、metrics、roadmap refs を必須化する |
| Organization-centric map | 社内部門の handoff 図になる | user goal と actions を中心に置く |
| Evidence-free emotions | 感情曲線を想像で描く | qualitative evidence refs を必須にする |
| No target design | as-is 分析で終わる | target journey と experiment/story 変換を gate にする |
| Local optimization | 一部画面だけ改善し、全体体験が悪化 | whole-problem review と service blueprint を使う |

### Anti-patterns

- journey map を一度作って wall decoration にする。
- as-is を観察せず target journey だけ描く。
- journey friction を roadmap priority に変換しない。
- persona/JTBD と接続しない。
- channel、human support、external system を無視する。

### Maturity Model

| Level | 状態 | 判定基準 |
|---:|---|---|
| 0 | 未整備 | journey がない |
| 1 | 想像図 | 内部メンバーの推測で journey を描く |
| 2 | 文書化 | stages/actions/touchpoints がある |
| 3 | 研究接続 | evidence refs、pain points、opportunities がある |
| 4 | 実装接続 | roadmap、use case、story、metrics に接続される |
| 5 | 継続改善 | journey metrics と research で as-is/target が継続更新される |

### Clone Implementation Guide

1. primary persona/JTBD ごとに high-value journey を 1 つ選ぶ。
2. as-is journey を research と data で作る。推測部分は confidence low と明示する。
3. friction を opportunity と measurement point に変換する。
4. target journey から roadmap theme、use case、user story を派生させる。
5. release 後に journey metrics をレビューし、map を更新する。

### Confidence & Unknowns

- 確度A: NN/g、AWS、GOV.UK の journey map 定義・運用示唆。
- 確度B: Product Talk の opportunity mapping を journey-to-roadmap translation に使う点。
- 不明点: 各社の具体的 journey score、service blueprint の内部レビュー基準。

---

## 7.7 Layer 03.07: ユーザーストーリー

### Definition

ユーザーストーリーは、ユーザーまたは actor の need と goal を、実装可能・優先順位付け可能・検証可能な backlog item に変換するレイヤーである。単なる要求チケットではなく、persona、journey、use case、acceptance criteria、Product Goal への traceability を持つ。

### Frontier Exemplars

| Exemplar | 採用理由 | Evidence |
|---|---|---|
| GOV.UK Writing User Stories | actor、narrative、goal、acceptance criteria、epic splitting、backlog priority を明示する。 | S16 |
| Scrum Guide 2020 | Product Goal、Product Backlog、Sprint Planning、Product Owner、Sprint Goal による backlog governance を示す。 | S28 |
| AWS Start with why / feature delivery | PR/FAQ と target journey から epics/user stories、roadmap へ接続する。 | S02, S05 |
| GitLab Product Development Flow | validation backlog から planning/refinement/development へ進む workflow を示す。 | S08 |
| Agile Manifesto | customer collaboration、responding to change、working software の価値観を提供する。 | S29 |

### Core Philosophy

1. user story は機能要求ではなく、actor が goal を達成するための価値単位である。
2. goal と acceptance criteria が弱い story は、実装後に「完成したが価値がない」状態を生む。
3. story は persona、journey friction、use case、roadmap outcome に trace できる必要がある。
4. epic は大きな仮説であり、learning と delivery のために小さな story に分割する。

### Decision Model

| Field | 内容 |
|---|---|
| Inputs | roadmap item、use case、journey friction、persona/JTBD、design prototype、technical dependency、acceptance test、analytics requirements |
| Decision Object | どの user need を、どの粒度・優先順位・acceptance criteria で backlog item 化するか |
| Criteria | user value、goal clarity、testability、vertical slice、dependency readiness、evidence linkage、delivery feasibility、learning value |
| Priorities | user goal before task、small testable slice、acceptance criteria、traceability、Product Goal alignment |
| Prohibitions | “As a system…” の乱用、goal がない story、solution-only ticket、acceptance criteria なし、巨大 epic を story と呼ぶ |
| Thresholds | story は actor、need/narrative、goal、acceptance criteria、evidence refs、linked roadmap/use case、definition of done を持つ。 |
| Owners | Product Owner、Product Manager、Designer、Engineering Lead、QA Lead、Scrum Team |
| Cadence | backlog refinement、sprint planning、daily/sprint review、post-release learning |
| Outputs | user story、acceptance criteria、epic/story map、sprint backlog、test cases、instrumentation notes |
| Controls | story readiness review、acceptance criteria review、definition of done、sprint planning、review/retro |
| Metrics | story cycle time、acceptance pass rate、rework rate、defect escape、story-to-outcome traceability、delivered value |

### Operating Model

1. **Story candidate intake**: roadmap item、use case、journey friction、customer insight から story 候補を作る。
2. **Actor/goal validation**: actor、need、goal を確認し、persona/JTBD に接続する。
3. **Acceptance definition**: outcome checklist、business rule、edge case、instrumentation を acceptance criteria にする。
4. **Slicing/refinement**: epic を vertical slice に分割し、依存関係と testability を確認する。
5. **Sprint planning**: Product Goal と Sprint Goal に対して重要 backlog item を選ぶ。
6. **Review/learning**: 完成物、顧客価値、metric、research feedback を review し、次の backlog を更新する。

### Technical / Business Specification

user story の標準 schema。

| Field | 内容 |
|---|---|
| story_id | 一意 ID |
| actor | persona/JTBD/use-case actor |
| narrative | 何が必要か |
| goal / so that | なぜ必要か、どの outcome に効くか |
| acceptance criteria | 検証可能な outcome checklist |
| linked roadmap item | roadmap refs |
| linked use case / journey | use case/journey refs |
| evidence refs | insight/research/support/analytics refs |
| dependency | technical/design/data/legal dependency |
| instrumentation | 測定イベント、success/failure signal |
| definition of done | 品質、accessibility、security、docs、release 条件 |
| priority | backlog priority と理由 |
| owner | PO/PM/DRI |
| status | draft/ready/in progress/done/validated |

### Failure Modes

| Failure | 症状 | 防止策 |
|---|---|---|
| Requirement ticket | story が「ボタンを追加する」だけになる | actor/narrative/goal と evidence refs を必須にする |
| Missing acceptance | done 判定が主観的になる | acceptance criteria と test case を story readiness gate にする |
| Oversized story | sprint 内で完了せず学習が遅い | epic/story split と vertical slicing を行う |
| No traceability | story が strategy/roadmap/persona と切れる | linked refs を必須 field にする |
| Build without validation | 価値のない実装が増える | discovery confidence と Product Goal alignment を確認する |

### Anti-patterns

- 「As a user, I want a button, so that I can click it」のような goal のない story。
- acceptance criteria を実装後に書く。
- epic を小さくせず sprint に入れる。
- story を research・journey・use case と接続しない。
- story 完了を launch と同義にし、outcome validation を行わない。

### Maturity Model

| Level | 状態 | 判定基準 |
|---:|---|---|
| 0 | 未整備 | backlog が task list |
| 1 | 形式のみ | As/I want/So that 形式だが goal が弱い |
| 2 | 文書化 | actor、need、goal、acceptance criteria がある |
| 3 | 接続済み | persona、journey、use case、roadmap に trace される |
| 4 | 検証可能 | instrumentation、test、definition of done が story に含まれる |
| 5 | 学習駆動 | story outcome が release 後に検証され、backlog と roadmap が自動的に更新される |

### Clone Implementation Guide

1. story template に `actor / narrative / goal / acceptance criteria / evidence refs / linked roadmap/use case/journey / instrumentation` を入れる。
2. backlog refinement で story readiness checklist を使う。
3. すべての story に Product Goal または roadmap theme を紐づける。
4. sprint review では demo だけでなく、user goal と metric hypothesis を確認する。
5. release 後に story outcome validation を行い、次の discovery/backlog に反映する。

### Confidence & Unknowns

- 確度A: GOV.UK user story guide、Scrum Guide、AWS の epic/user story 接続。
- 確度B: GitLab Product Development Flow を story readiness/validation gate に接続する点。
- 不明点: 各社の internal Definition of Ready、Jira/Linear 等の具体的 field 設定。

---

## 8. Pattern Library

| Pattern ID | Pattern Name | Scope | Type | Description | Preconditions | Tradeoffs | Confidence |
|---|---|---|---|---|---|---|---|
| P001 | Outcome-first strategy | 03.01–03.03 | principle | feature request の前に customer/business outcome と success metric を定義する。 | strategy owner、measurement capacity | 初期速度は落ちるが、後戻りが減る | A |
| P002 | Vision-to-story traceability | 03.02–03.07 | control | vision theme から roadmap、journey、use case、story まで ID で追跡する。 | artifact registry、template 統一 | 管理負荷が増える | B |
| P003 | Evidence-backed persona | 03.04 | decision_rule | persona に evidence refs、confidence、last validated を持たせる。 | research repository | 低証拠 persona を使えなくなる | A/B |
| P004 | As-is before target journey | 03.06 | principle | target journey を描く前に as-is と friction を証拠化する。 | user research/data | 調査期間が必要 | A |
| P005 | Opportunity-to-roadmap gate | 03.01–03.03, 03.06 | operating_model | opportunity を impact/confidence/effort/dependency で roadmap 化する。 | opportunity backlog | 高価値でも低信頼の item は遅れる | B |
| P006 | Alternative-flow use case | 03.05, 03.07 | control | use case に alternative/failure flow を必須にし、acceptance test に接続する。 | domain review、QA involvement | 文書量が増える | B |
| P007 | Story readiness checklist | 03.07 | control | actor、goal、acceptance criteria、evidence、linked roadmap/use case がない story を sprint に入れない。 | backlog discipline | 短期の ticket throughput は落ちる | A |
| P008 | Public/transparent roadmap | 03.03 | operating_model | stage、expected timing、feedback channel を公開し、変更履歴を残す。 | customer-facing governance | 外部期待管理が難しくなる | B |
| P009 | Stale backlog cleanup | 03.03, 03.07 | failure_pattern | 古い backlog item を定期的に close/reframe/archive する。 | backlog metadata、owner | 一部 stakeholder の不満が出る | B |
| P010 | Assumption decomposition | 03 | decision_rule | solution 全体ではなく、underlying assumptions を分解して検証する。 | hypothesis discipline | 実験設計スキルが必要 | B/C |

---

## 9. Validation / Refutation Queries

再実行時は次の反証・鮮度確認クエリを使う。

```text
site:docs.aws.amazon.com/prescriptive-guidance/latest/strategy-product-development roadmap deprecated OR updated
site:docs.aws.amazon.com/prescriptive-guidance/latest/strategy-product-development "success metrics" "product strategy"
site:handbook.gitlab.com/handbook/product "data over intuition" "outcomes"
site:handbook.gitlab.com/handbook/product-development "validation backlog" "solution validation"
site:gov.uk/service-manual "discovery" "not start building"
site:gov.uk/service-manual "writing user stories" "acceptance criteria"
site:support.atlassian.com/jira-product-discovery "impact" "effort" "confidence"
site:github.com/github/roadmap "sunset" OR "deprecated" OR "removed"
site:nngroup.com "personas" "analytics alone"
site:nngroup.com "journey map" "qualitative" "research"
site:scrumguides.org "Product Goal" "Product Backlog"
site:omg.org/spec/UML/2.5.1 "UseCase"
"product roadmap" "incident" OR "lawsuit" OR "customer backlash"
"persona" "failed" "product" "case study"
"user story" "anti-pattern" "acceptance criteria"
```

---

## 10. QA チェック

| Check | 判定 | 根拠 |
|---|---|---|
| Coverage | Pass | 03 の各 layer に direct/near-direct evidence がある。 |
| T0/T1/T2/T3 coverage | Pass | GOV.UK、Scrum Guide、OMG、NIST、GitHub、Atlassian、GitLab、AWS を使用。 |
| Critical claim confidence | Pass | 主要 claim は A/B。Product Talk など expert method は C を含め補助扱い。 |
| Failure evidence | Partial Pass | GitHub sunset、GitLab backlog cleanup、GOV.UK stop/no-go は取得。失敗事例の網羅的調査は追加余地あり。 |
| History/diff | Partial Pass | GitHub roadmap issue と GitLab backlog cleanup は履歴/失敗面を持つ。Wayback diff は未実行。 |
| Artifact specificity | Pass | strategy brief、vision doc、roadmap item、persona canvas、use-case brief、journey map、user story schema を定義。 |
| Unknowns separated | Pass | 内部承認権限、財務閾値、内部 roadmap capacity model は unknown として分離。 |

---

## 11. Confidence & Unknowns 全体

### 確度A

- プロダクト戦略における why、vision、metrics、business case、feature prioritization の連鎖。
- discovery phase で problem、users、constraints、success measurement を理解し、場合によっては alpha/build に進まない判断をすること。
- vision、objectives、roadmap、user stories を可視化し、学習により計画を更新すること。
- user story に actor、narrative、goal、acceptance criteria が必要であること。
- journey map が goal 達成プロセスを可視化する artifact であること。
- Product Goal と Product Backlog の関係。

### 確度B

- GitLab、AWS、GOV.UK、Atlassian、GitHub の公開情報から抽出した cross-layer operating model。
- stale backlog cleanup と deprecation/sunset を roadmap governance の failure-mode 対策として扱うこと。
- persona/JTBD/journey/use case/story を一連の artifact chain として標準化すること。

### 確度C

- Product Talk の continuous discovery、opportunity solution tree、assumption testing を全組織の標準 operating model として一般化すること。強い方法論ではあるが、企業内実装の直接証拠ではないため補助扱い。
- NN/g の persona/journey 方法論を特定企業の frontier operating model と同一視すること。方法論としては有用だが、内部運用証拠ではない。

### 主な Unknowns

1. 各 frontier organization の内部 roadmap 承認権限、財務閾値、capacity allocation model。
2. public roadmap と internal roadmap の差分管理ルール。
3. persona confidence、journey confidence、story readiness の実際の数値閾値。
4. PR/FAQ、direction page、roadmap、backlog、research repository の内部 tool integration。
5. deprecation/sunset の顧客通知期間、契約上の制約、例外承認プロセス。

---

## 12. 最小導入パッケージ

03 を自組織に clone する場合、最初に導入すべき最小セットは次の 10 点である。

| # | Artifact / Process | 対象 layer | 目的 |
|---:|---|---|---|
| 1 | Product Strategy Brief | 03.01 | 投資理由、顧客価値、事業価値、成功指標を 1 枚にする |
| 2 | Product Vision + Non-goals | 03.02 | 判断原則とやらないことを明確にする |
| 3 | Success Metrics / OKR Registry | 03.01–03.03 | 戦略と roadmap を測定可能にする |
| 4 | Roadmap Item Schema | 03.03 | outcome、evidence、confidence、dependency、owner を必須化する |
| 5 | Idea / Insight Repository | 03.01–03.06 | research、support、sales、analytics、stakeholder signal を集約する |
| 6 | Persona/JTBD Canvas | 03.04 | target user と job を evidence-backed にする |
| 7 | As-is / Target Journey Map | 03.06 | friction と opportunity を可視化する |
| 8 | Use-case Brief | 03.05 | actor、goal、scenario、alternative flow を明確化する |
| 9 | User Story Template | 03.07 | actor、goal、acceptance criteria、evidence refs を標準化する |
| 10 | Monthly Roadmap & Backlog Cleanup Review | 03.03, 03.07 | stale item、低証拠 item、sunset 候補を処理する |

---

## 13. 推奨テンプレート

### 13.1 Product Strategy Brief

```markdown
# Product Strategy Brief

Product / Initiative:
Owner:
Date:
Version:

## Why now
- Customer problem:
- Business problem:
- Market / timing driver:

## Target customer
- Primary persona / JTBD:
- Secondary persona:
- Excluded users / non-goals:

## Value hypothesis
- Customer value:
- Business value:
- Differentiation:

## Success metrics
| Metric | Baseline | Target | Owner | Review cadence |
|---|---:|---:|---|---|

## Evidence
- Research:
- Analytics:
- Support / sales:
- Competitive / market:

## Business case
- Revenue / growth:
- Cost saving / efficiency:
- Risk reduction:
- Investment cost:
- Key assumptions:

## Roadmap implication
- MVP:
- Roadmap themes:
- Dependencies:
- Stop / pivot criteria:
```

### 13.2 Roadmap Item

```markdown
# Roadmap Item

ID:
Theme:
Owner:
Stage: Explore / Validate / Plan / Build / Launch / Deprecate
Confidence: Low / Medium / High
Review date:

## Target outcome

## Target persona / JTBD

## Evidence refs

## Impact / Effort / Dependency

## MVP / Scope

## Linked use cases / journeys / stories

## Risks and stop criteria
```

### 13.3 Persona / JTBD Canvas

```markdown
# Persona / JTBD Canvas

Persona ID:
Status: Hypothesis / Validated / Retired
Confidence:
Last validated:
Owner:

## Primary job / goal

## Context and constraints

## Current behavior / workaround

## Pain points

## Decision criteria

## Evidence refs

## Product implications

## Linked journeys / roadmap items / stories
```

### 13.4 Use-case Brief

```markdown
# Use Case

Use case ID:
Name:
Primary actor:
Secondary actors:
Linked persona / JTBD:
Linked journey:

## Goal

## Preconditions

## Main success scenario
1.
2.
3.

## Alternative flows
- A1:
- A2:

## Postconditions

## Business rules / constraints

## Linked stories / acceptance tests
```

### 13.5 User Story

```markdown
# User Story

Story ID:
Status: Draft / Ready / In Progress / Done / Validated
Priority:
Owner:

## Story
As a [actor/persona],
I need [narrative/need],
So that [goal/outcome].

## Acceptance criteria
- [ ]
- [ ]

## Evidence refs

## Linked roadmap item

## Linked use case / journey

## Instrumentation

## Definition of done
```

---

## 14. Source References

- [S01] AWS Prescriptive Guidance, *Developing product strategies that deliver measurable business value*, https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-product-development/introduction.html
- [S02] AWS Prescriptive Guidance, *Start with why*, https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-product-development/start-with-why.html
- [S03] AWS Prescriptive Guidance, *Define success metrics*, https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-product-development/success-metrics.html
- [S04] AWS Prescriptive Guidance, *Develop the business case*, https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-product-development/business-case.html
- [S05] AWS Prescriptive Guidance, *Prioritize features and plan delivery*, https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-product-development/features-delivery.html
- [S06] GitLab Handbook, *Product Principles*, https://handbook.gitlab.com/handbook/product/product-principles/
- [S07] GitLab Handbook, *Product Processes*, https://handbook.gitlab.com/handbook/product/product-processes/
- [S08] GitLab Handbook, *Product Development Flow*, https://handbook.gitlab.com/handbook/product-development/how-we-work/product-development-flow/
- [S09] GitLab Handbook, *Foundational Research*, https://handbook.gitlab.com/handbook/product/ux/experience-research/foundational-research/
- [S10] GitLab Handbook, *Jobs to be Done Research Playbook*, https://handbook.gitlab.com/handbook/product/ux/jobs-to-be-done/jtbd-playbook/
- [S11] GitLab Handbook, *Research Prioritization*, https://handbook.gitlab.com/handbook/product/ux/experience-research/research-prioritization/
- [S12] GOV.UK Service Manual, *How the discovery phase works*, https://www.gov.uk/service-manual/agile-delivery/how-the-discovery-phase-works
- [S13] GOV.UK Service Manual, *Understand users and their needs*, https://www.gov.uk/service-manual/service-standard/point-1-understand-user-needs
- [S14] GOV.UK Service Manual, *Solve a whole problem for users*, https://www.gov.uk/service-manual/service-standard/point-2-solve-a-whole-problem
- [S15] GOV.UK Service Manual, *Planning in agile*, https://www.gov.uk/service-manual/agile-delivery/planning-agile
- [S16] GOV.UK Service Manual, *Writing user stories*, https://www.gov.uk/service-manual/agile-delivery/writing-user-stories
- [S17] GOV.UK Service Manual, *Sharing user research findings*, https://www.gov.uk/service-manual/user-research/sharing-user-research-findings
- [S18] Atlassian Support, *What is Jira Product Discovery?*, https://support.atlassian.com/jira-product-discovery/docs/what-is-jira-product-discovery/
- [S19] Atlassian Support, *What are insights?*, https://support.atlassian.com/jira-product-discovery/docs/what-are-insights/
- [S20] Atlassian Support, *Understand the matrix view*, https://support.atlassian.com/jira-product-discovery/docs/understand-the-matrix-view/
- [S21] Product Talk, *Product Discovery Basics*, https://www.producttalk.org/product-discovery/
- [S22] Product Talk, *Continuous Discovery Mindsets*, https://www.producttalk.org/continuous-discovery-mindsets/
- [S23] Product Talk, *Opportunity Solution Trees*, https://www.producttalk.org/opportunity-solution-trees/
- [S24] Product Talk, *Assumption Testing*, https://www.producttalk.org/glossary-discovery-assumption-testing/
- [S25] Nielsen Norman Group, *Journey Mapping 101*, https://www.nngroup.com/articles/journey-mapping-101/
- [S26] Nielsen Norman Group, *Personas topic page*, https://www.nngroup.com/topic/personas/
- [S27] NIST, *Human Centered Design*, https://www.nist.gov/itl/iad/visualization-and-usability-group/human-factors-human-centered-design
- [S28] Scrum Guides, *The Scrum Guide 2020*, https://scrumguides.org/scrum-guide.html
- [S29] Agile Manifesto, *Manifesto for Agile Software Development*, https://agilemanifesto.org/
- [S30] Object Management Group, *UML 2.5.1*, https://www.omg.org/spec/UML/2.5.1/About-UML
- [S31] ACM Queue / Ivar Jacobson, *Use Cases are Essential*, https://queue.acm.org/detail.cfm?id=3631182
- [S32] GitHub, *GitHub public roadmap*, https://github.com/github/roadmap
- [S33] GitHub Roadmap Issue #915, *Sunset Subversion support in GitHub Enterprise Server*, https://github.com/github/roadmap/issues/915
- [S34] GitLab Handbook, *Healthy Backlog at GitLab*, https://handbook.gitlab.com/handbook/product-development/programs/backlog/
