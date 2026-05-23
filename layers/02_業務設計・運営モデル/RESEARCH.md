# Frontier Operating Model Research: 業務設計・運営モデル（02）

生成日: 2026-05-13  
対象単位: **業務設計・運営モデル**  
対象レイヤー: **02**  
対象サブテーマ: 業務方針、業務プロセス、業務ルール/例外、承認、監査、権限、組織設計、運用体制  
調査制約: 公開情報のみ。標準、公式文書、公開運用資料、公式ハンドブック、公開ベンダー/標準団体資料を優先。

## 0. エグゼクティブサマリー

02 の業務設計・運営モデルは、単なる「業務マニュアル」ではなく、**方針、プロセス、ルール、例外、承認、監査、権限、組織、運用を一つの意思決定システムとして接続するレイヤー群**である。公開情報から抽出できる frontier pattern は次の通り。

1. **方針はリスク・目的・制約を翻訳する上位 contract であり、手順書ではない。** NIST CSF 2.0 は GOVERN を通じて、戦略、期待、方針、役割、責任、権限、監督をリスクマネジメントに接続する。ISO 9001 は、品質マネジメントをプロセス、責任、データ、改善に接続する。
2. **プロセスは部門別の作業列ではなく、入力、出力、チェック、責任、指標、例外を持つ end-to-end flow として定義する。** ISO 9001、BPMN、Toyota Production System、AWS Well-Architected がこの方向性を支える。
3. **業務ルールはプロセスから分離して管理し、例外は期限・範囲・リスク受容・補完統制を持つ。** OMG DMN は business decisions / business rules の精密な仕様化を、GitLab と Google SRE は例外・エスカレーション・ポリシーの実運用例を示す。
4. **承認は blanket approval ではなく、DRI/owner を既定にし、高リスク・不可逆・横断・財務/評判影響の時だけ追加承認を発動する。** GitLab DRI、GitLab Required Approvals、Google SRE error budget policy がこの構造を裏付ける。DORA は heavyweight change approval を anti-pattern として扱う。
5. **監査は年次イベントではなく、統制設計、証跡、継続モニタリング、内部/外部監査をつなぐ evidence system である。** COSO、NIST RMF、NIST SP 800-53、SOC 2、ISO 19011 が直接証拠となる。
6. **権限は「誰が何をできるか」だけではなく、意思決定権限、アクセス権限、職務分掌、緊急権限、監査ログを接続する。** NIST SP 800-53、NIST CSF、GitLab IAM が強い証拠となる。
7. **組織設計は人員配置ではなく、価値流、認知負荷、所有権、相互作用モード、アーキテクチャとの整合を決める。** AWS DevOps Guidance と Team Topologies が主要パターンを示す。
8. **運用体制は、SLO/error budget、runbook、on-call、incident、postmortem、observability、改善 backlog を持つ closed-loop system として設計する。** Google SRE と AWS Operational Excellence が中心証拠である。

本成果物では、02 を以下の 8 レイヤーとして正規化した。

| Layer ID | Layer Name | Decision Object |
|---|---|---|
| 02.01 | 業務方針 | 事業目的、リスク、法規制、顧客約束を、業務で守るべき方針・標準・禁止事項・レビュー周期へ変換すること |
| 02.02 | 業務プロセス | 価値提供の end-to-end flow、入力/出力、責任、制御点、例外、指標を設計すること |
| 02.03 | 業務ルール/例外 | 反復判断の条件、閾値、禁止、例外、補完統制、失効条件を管理すること |
| 02.04 | 承認 | 誰がいつ何を承認し、どの条件なら承認を省略・追加・エスカレーションするかを決めること |
| 02.05 | 監査 | 統制が設計通りに動作し、証跡が残り、独立評価と改善につながる仕組みを決めること |
| 02.06 | 権限 | 役割、意思決定権限、アクセス権限、職務分掌、緊急権限、失効を設計すること |
| 02.07 | 組織設計 | 価値流、顧客成果、認知負荷、所有権、チーム相互作用に基づき組織境界を決めること |
| 02.08 | 運用体制 | 日次・週次・月次の運用、障害対応、SLO、継続改善、ナレッジ、体制を決めること |

## 1. Source Catalog

| Source ID | Entity | Source | Tier | Primary Use | URL |
|---|---|---|---|---|---|
| S01 | NIST | The NIST Cybersecurity Framework (CSF) 2.0 | T0 | 方針、Govern、roles/responsibilities/authorities、Profiles/Tiers、継続改善 | https://csrc.nist.gov/pubs/cswp/29/the-nist-cybersecurity-framework-csf-20/final |
| S02 | NIST | SP 800-37 Rev.2 Risk Management Framework | T0 | categorization、control selection、assessment、authorization、continuous monitoring、責任/説明責任 | https://csrc.nist.gov/pubs/sp/800/37/r2/final |
| S03 | NIST | SP 800-53 Rev.5 Security and Privacy Controls | T0 | access control、audit/accountability、controls catalog、risk-based controls | https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final |
| S04 | COSO | Internal Control — Integrated Framework | T0/T1 | internal control、operations/reporting/compliance objectives、control design | https://www.coso.org/guidance-on-ic |
| S05 | ISO | ISO 9001 explained | T0 | QMS、process approach、documented information、monitoring、responsibility、improvement | https://www.iso.org/home/insights-news/resources/iso-9001-explained.html |
| S06 | ISO/TC 176 | Q&A on ISO Management Systems Standards | T0 | process approach as interrelated processes, coherent system, risk-based thinking | https://committee.iso.org/sites/tc176/home/news/content-left-area/news-and-updates/questions-and-answers-iso-qualit.html |
| S07 | OMG | BPMN 2.0 Specification | T0/T2 | process notation, stakeholder-readable process models, machine-readable artifacts | https://www.omg.org/spec/BPMN/2.0/ |
| S08 | OMG | Decision Model and Notation (DMN) | T0/T2 | business decisions, business rules, decision tables, BPMN/CMMN complement | https://www.omg.org/dmn/ |
| S09 | Toyota | Toyota Production System | T3 | waste elimination, lead time, JIT, jidoka, daily kaizen | https://global.toyota/en/company/vision-and-philosophy/production-system/ |
| S10 | AWS | Well-Architected Framework: Operational Excellence | T0/T3 | operating at scale, team organization, workload operation, continual evolution | https://docs.aws.amazon.com/wellarchitected/latest/framework/operational-excellence.html |
| S11 | AWS | Operational Excellence Pillar: Operating Model | T3 | operating model visualization, team roles, shared goals, team interactions | https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/operating-model.html |
| S12 | AWS | DevOps Guidance: Structure teams around desired business outcomes | T3 | team structure, ownership, Conway/inverse Conway, business outcomes | https://docs.aws.amazon.com/wellarchitected/latest/devops-guidance/oa.std.4-structure-teams-around-desired-business-outcomes.html |
| S13 | GitLab | The GitLab Handbook | T3 | public operating handbook, transparent company operating model | https://handbook.gitlab.com/handbook/ |
| S14 | GitLab | Directly Responsible Individuals (DRI) | T3 | ownership, DRI, RACI/DACI, final decision rights, rare approvals | https://handbook.gitlab.com/handbook/people-group/directly-responsible-individuals/ |
| S15 | GitLab | Development Required Approvals | T3 | risk-triggered approvals, approval process, proposal issue, CEO/Fellow approval examples | https://handbook.gitlab.com/handbook/engineering/development/required-approvals/ |
| S16 | GitLab | Identity and Access Management (IAM) v3 | T3/T2 | RBAC/IAM, provisioning/deprovisioning, GitOps, audit artifacts, change management | https://handbook.gitlab.com/handbook/security/identity/ |
| S17 | Google SRE | Blameless Postmortem for System Resilience | T3 | incident review, action items, blameless culture, review/publication, knowledge sharing | https://sre.google/sre-book/postmortem-culture/ |
| S18 | Google SRE | Implementing SLOs | T3 | SLO stakeholder agreement, error budget policy, documented owner/reviewer/approver, dashboards | https://sre.google/workbook/implementing-slos/ |
| S19 | Google SRE | Error Budget Policy | T3 | thresholds, postmortem trigger, P0 items, escalation, reliability vs innovation control | https://sre.google/workbook/error-budget-policy/ |
| S20 | Team Topologies | Key Concepts | T3 | stream-aligned/platform/enabling/complicated-subsystem teams, interaction modes, cognitive load | https://teamtopologies.com/key-concepts |
| S21 | DORA | Research Program / Core Model | T5 | delivery/operations performance, sociotechnical capabilities, anti-patterns such as heavyweight approvals | https://dora.dev/research/ |
| S22 | AICPA & CIMA | SOC 2: Trust Services Criteria | T1/T5 | service organization control reports for security, availability, processing integrity, confidentiality, privacy | https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2 |
| S23 | AICPA & CIMA | 2017 Trust Services Criteria with revised points of focus 2022 | T1/T5 | criteria for attestation/consulting engagements over information and system controls | https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022 |
| S24 | ISO | ISO 19011:2018 Guidelines for auditing management systems | T0 | audit program, audit principles, management system audit, auditor competence | https://www.iso.org/standard/70017.html |
| S25 | NSAI | ISO/IEC 27001 Information Security Management System overview | T0/T5 | ISMS scope, risk treatment, roles/responsibilities, governance, internal audit, continual improvement | https://www.nsai.ie/certification/management-systems/iso-iec-27001-information-security-management-system/ |

## 2. Candidate Scoring

スコアは RESEARCH.md の評価軸（Performance、Adoption、Artifact Richness、Peer Validation、Recency、Transferability、Failure Evidence）に基づく簡易 100 点換算。企業内部の非公開運用ではなく、公開成果物の厚みと移植可能性を重視した。

| Candidate / Source Family | 主な効用 | Score | 採用理由 |
|---|---|---:|---|
| NIST CSF / RMF / SP 800-53 | Governance, controls, authority, monitoring | 95 | T0 の規範性が強く、roles/policy/oversight/control/continuous monitoring を横断する。02.01, 02.05, 02.06 に特に有効。 |
| ISO 9001 / ISO 19011 / ISO 27001 | Process, management system, audit, continual improvement | 90 | process approach、documented information、monitoring、audit program、roles/responsibilities を広く支える。02.02, 02.05 に特に有効。 |
| COSO Internal Control | Control, audit, operations/reporting/compliance objectives | 88 | 内部統制の代表的枠組み。02.05 の基準軸として有効。 |
| Google SRE | SLO, error budget, postmortem, operations | 88 | operational decision rules が具体的で、02.08 と 02.04/02.05 の threshold 設計にも使える。 |
| AWS Well-Architected / DevOps Guidance | Operating model, business outcomes, team ownership | 86 | team organization、operating model、business-outcome alignment の実装指針が厚い。02.07, 02.08 に有効。 |
| GitLab Handbook / DRI / IAM / Approvals | Public operating handbook, DRI, approvals, IAM evidence | 86 | 公開された実運用文書が豊富。02.04, 02.06, 02.07 の operational artifact が強い。 |
| OMG BPMN / DMN | Process and decision/rule modeling standards | 84 | 02.02 と 02.03 の specification artifact として直接使える。 |
| Toyota Production System | Waste, JIT, jidoka, kaizen, lead time | 82 | 02.02/02.08 の現場運用哲学として強い。デジタル業務への移植には抽象化が必要。 |
| Team Topologies | Team design, cognitive load, interaction modes | 80 | 02.07 の組織設計で明確な model を提供する。規範標準ではないため T3。 |
| DORA | Performance evidence and anti-patterns | 78 | 02.04/02.07/02.08 の anti-pattern と metrics に有効。個別組織の運用証拠ではなく研究プログラム。 |
| AICPA SOC 2 / Trust Services Criteria | Audit/control reporting | 82 | 02.05 の外部保証・統制証跡設計に有効。全文利用にはアカウント/ライセンス制約あり。 |

## 3. Evidence Graph（主要 Claim）

| Claim ID | Layers | Claim | Evidence | Confidence |
|---|---|---|---|---|
| C-02.01-01 | 02.01 | 方針は strategy, expectations, policy, roles, responsibilities, authorities, oversight をリスク文脈で接続する上位 contract として設計する。 | S01, S02, S25 | A |
| C-02.02-01 | 02.02 | プロセスは入力・出力・相互作用・チェック・指標・改善を持つ coherent system として定義する。 | S05, S06, S07 | A |
| C-02.02-02 | 02.02 | 効率性・品質・リードタイム改善には、異常検知/停止、JIT、日次 kaizen、ムダ排除が有効な運用原理になる。 | S09 | B |
| C-02.03-01 | 02.03 | 反復判断は business rules / decision tables としてプロセスから分離し、入力・出力・ルール・hit policy・例外を持たせる。 | S08, S07 | A |
| C-02.03-02 | 02.03 | 例外は risk acceptance であり、期限、範囲、補完統制、承認者、レビュー日がなければ統制逸脱になる。 | S01, S02, S03, S18 | B |
| C-02.04-01 | 02.04 | 通常判断は DRI が進め、財務/評判/リスク/横断性/不可逆性が高い時だけ追加承認を要求する。 | S14, S15, S18, S21 | B |
| C-02.04-02 | 02.04 | blanket / heavyweight change approval は速度と品質の両方を損ねる anti-pattern になりうる。 | S21, S15, S18 | B |
| C-02.05-01 | 02.05 | 監査は control design、control operation、evidence、independent review、remediation tracking から成る継続システムである。 | S04, S02, S03, S22, S24 | A |
| C-02.06-01 | 02.06 | 権限は role/responsibility/authority/access を明示し、アクセス制御・職務分掌・監査証跡・失効を持つ。 | S01, S03, S16, S25 | A |
| C-02.07-01 | 02.07 | チームは business outcome / value stream とシステム構造に合わせて設計し、所有権と interaction mode を明示する。 | S12, S20, S11 | A/B |
| C-02.08-01 | 02.08 | 運用体制は SLO/error budget、runbook、incident/postmortem、observability、改善 backlog を持つ closed loop として設計する。 | S10, S11, S17, S18, S19 | A/B |

## 4. Cross-layer Operating Principles

### 4.1 設計原則

| Principle | 内容 | 対象レイヤー | Source |
|---|---|---|---|
| Policy-to-Control Traceability | 方針、標準、プロセス、ルール、統制、証跡、監査所見を同じ ID 体系で接続する。 | 02.01, 02.03, 02.05, 02.06 | S01, S02, S03, S04 |
| Process-as-System | 部門単位ではなく、価値流/顧客成果単位でプロセスを定義する。 | 02.02, 02.07, 02.08 | S05, S06, S07, S09, S12 |
| Decision/Process Separation | プロセスの流れは BPMN、判断ロジックは DMN/decision table に分離する。 | 02.02, 02.03 | S07, S08 |
| DRI-first Approval | 既定は単一 owner / DRI。承認はリスク閾値により追加する。 | 02.04, 02.06, 02.07 | S14, S15, S18 |
| Evidence-by-Design | 業務・権限・例外・承認は最初から証跡が残るツール/ワークフローで実行する。 | 02.03, 02.04, 02.05, 02.06 | S02, S03, S16, S22 |
| Closed-loop Operations | SLO、error budget、incident、postmortem、改善 backlog を接続し、学習を運用へ戻す。 | 02.08 | S17, S18, S19, S10 |
| Outcome-aligned Organization | 組織境界を value stream、business outcome、system interaction に合わせる。 | 02.07 | S12, S20, S11 |
| Continuous Improvement | 方針・プロセス・監査・運用のいずれも static document ではなく定期/イベント駆動で改善する。 | 全レイヤー | S05, S06, S09, S10, S17 |

### 4.2 成熟度モデル（共通）

| Level | Name | 共通基準 |
|---:|---|---|
| 0 | 未整備 | 方針・プロセス・権限・承認が暗黙。証跡は個人の記憶やチャットに依存。 |
| 1 | 個人依存 | 主要 owner はいるが、ルール、例外、承認、監査が標準化されていない。 |
| 2 | 文書化 | 方針、プロセス、承認、権限、監査手順が文書化される。ただし実行証跡や指標は弱い。 |
| 3 | 標準化 | ID 体系、template、RACI/DRI、プロセス map、ルール/例外台帳、承認 matrix、監査証跡が標準化される。 |
| 4 | 自動化・計測 | ワークフロー、IAM、GitOps、ticketing、logs、dashboards により証跡と指標が自動取得される。 |
| 5 | 自律改善・業界先端 | SLO/error budget、audit findings、exception trends、customer outcomes から方針・プロセス・組織を継続的に再設計する。 |

---

# 5. Clone Spec: Layer 02.01 業務方針

## Definition

業務方針は、事業目的、顧客約束、法規制、契約、リスク許容度、組織文化を、業務で守るべき **policy / standard / procedure / guideline / exception path** に変換するレイヤーである。手順の詳細ではなく、何を守るべきか、何を禁止するか、誰が責任を持つか、どの証拠で有効性を判断するかを決める。

## Decision Question

先端組織は、どの事業目的・リスク・法規制・顧客約束を入力に、どの方針体系を作り、誰が承認・改定し、どの統制・指標・例外ルートで業務への浸透を確認するか。

## Frontier Exemplars

| Exemplar | 採用理由 | Source |
|---|---|---|
| NIST CSF 2.0 GOVERN | strategy, expectations, policy, roles/responsibilities/authorities, oversight をリスク文脈で定義する。 | S01 |
| ISO 9001 | leadership commitment, customer focus, process approach, documented information, monitoring, continual improvement を品質方針に接続する。 | S05 |
| COSO Internal Control | operations/reporting/compliance objectives を統制設計に接続する。 | S04 |
| GitLab Handbook | 方針・運用方法を公開 handbook として維持し、merge request / issue による継続改善を可能にする。 | S13 |
| ISO/IEC 27001 overview | scope、risk treatment、roles/responsibilities、governance、internal audit、continual improvement を ISMS の基盤に置く。 | S25 |

## Evidence Map

| Claim | Evidence | Confidence |
|---|---|---|
| 方針は strategy / expectations / policy / roles / oversight を enterprise risk に接続する。 | S01, S02 | A |
| 方針はプロセス・責任・文書化・計測・改善に落ちる必要がある。 | S05, S06 | A |
| 透明な handbook は operational policy を実行可能な成果物にする。 | S13 | B |
| 方針が統制に接続しない場合、監査・例外・権限で機能しない。 | S04, S03, S22 | A/B |

## Core Philosophy

方針は「守るべき文言」ではなく、**業務判断の境界条件**である。よい業務方針は、現場に自由度を残しながら、リスク許容度、禁止事項、承認条件、証跡、レビュー周期を明確にする。

## Decision Model

| Field | Spec |
|---|---|
| Inputs | 事業目的、顧客契約、法規制、リスク appetite/tolerance、過去インシデント、監査所見、戦略 OKR、組織設計、外部標準 |
| Criteria | 方針が目的達成に必要か、リスクに比例しているか、実行可能か、監査可能か、既存プロセス/権限と矛盾しないか |
| Priorities | 1. 法規制/契約遵守、2. 顧客影響、3. 重大リスク低減、4. 業務速度、5. 現場裁量 |
| Prohibitions | 方針と手順の混同、owner 不明方針、レビュー日なし、例外ルートなし、統制/証跡なし方針、部門限定で全社影響を持つ方針 |
| Exceptions | 例外は期限、範囲、理由、リスク受容者、補完統制、失効日、再審査日を必須にする。 |
| Approvers | Policy owner、Risk/Compliance、Legal、Security/Privacy、対象 business owner、必要に応じて経営会議/board committee |
| Review Cadence | 年次レビューを既定。重大インシデント、法規制変更、事業モデル変更、監査所見、高頻度例外発生時は event-driven review。 |

## Operating Model

| Component | Design |
|---|---|
| Roles | Policy Owner、Policy Steward、Control Owner、Process Owner、Legal/Compliance Reviewer、Training Owner、Audit Liaison |
| Process | 方針要求の起票 → 影響評価 → policy draft → control/process mapping → 承認 → 公開 → training/acknowledgement → monitoring → review |
| Governance Forum | 月次 policy review board、四半期 risk/control review、年次 management review |
| Artifacts | Policy registry、policy document、control mapping、process mapping、exception path、training record、review log、revision diff |
| Tools | Handbook/CMS、GRC、ticketing、workflow、e-signature、LMS、version control |
| Audit Evidence | 承認履歴、最新版公開証跡、対象者通知/受講、例外記録、方針と統制の対応表、レビュー記録 |

## Technical / Business Specification

### Policy Record Schema

| Field | Required | Notes |
|---|---|---|
| policy_id | Yes | 例: POL-SEC-001, POL-FIN-004 |
| title | Yes | 方針名 |
| purpose | Yes | 何の目的/リスクを扱うか |
| scope | Yes | 対象組織、プロセス、システム、データ、地域 |
| owner | Yes | accountable owner。委員会ではなく個人/役割を明示 |
| steward | Recommended | 日常更新担当 |
| requirements | Yes | 守るべき outcome / rule |
| prohibitions | Yes | 禁止事項 |
| related_controls | Yes | control IDs / audit criteria |
| related_processes | Yes | process IDs |
| exception_path | Yes | exception request form / approver / expiry |
| approval_record | Yes | approvers, date, decision memo |
| effective_date | Yes | 施行日 |
| review_date | Yes | 次回レビュー期限 |
| version / changelog | Yes | diff と理由 |
| training_required | Conditional | 対象者、頻度、記録 |

## Metrics

- Policy coverage: 主要プロセスに対応方針が存在する割合
- Stale policy rate: review_date 超過方針の割合
- Control mapping coverage: 方針要求が統制 ID に接続されている割合
- Exception volume / aging: 例外件数、期限超過、再発
- Audit findings from policy gap: 方針不備に起因する監査所見数
- Acknowledgement coverage: 対象者の受領/研修完了率
- Policy change lead time: 起票から公開までの日数

## Failure Modes

| Failure | 兆候 | 防止策 |
|---|---|---|
| 方針肥大化 | 現場が読まない、例外だらけ | 方針/標準/手順を分離し、risk-based scope にする |
| owner 不明 | 改定されない、問い合わせ先不明 | policy_id ごとに owner と steward を必須化 |
| 統制非接続 | 監査で証跡が出せない | control mapping と evidence requirements を方針に埋め込む |
| 例外 uncontrolled | 期限切れ例外、口頭例外 | exception registry と expiry automation |
| 現場速度低下 | 方針承認待ちが常態化 | DRI-first、risk-triggered approval、template 化 |

## Anti-patterns

- すべてを policy と呼び、手順、標準、ガイドライン、FAQ を区別しない。
- 例外を「承認者のメール」で済ませ、期限・補完統制・失効条件を残さない。
- 方針を公開するだけで、研修、プロセス組込、監査証跡を設計しない。
- 方針 owner が委員会名だけで、個人/役割の accountability がない。
- 過去の監査対応で作った文書が、現行業務と乖離したまま残る。

## Clone Implementation Guide

1. 既存方針を `policy_id / owner / scope / review_date / related_process / related_control / exception_path` で棚卸しする。
2. 方針を `Policy / Standard / Procedure / Guideline / FAQ` に分類し直す。
3. 上位 20 の重要方針だけ、control mapping と exception path を先に整備する。
4. 方針ごとに DRI と review board を決め、改定履歴を version control で残す。
5. 方針違反、例外、監査所見、インシデントを同じ taxonomy で集計する。

## Confidence & Unknowns

- 確度 A: NIST/ISO/COSO は方針・統制・責任・改善の構造を直接裏付ける。
- 確度 B: GitLab handbook 型の透明運用はデジタル企業には移植可能性が高いが、規制・人事・地域制約により公開範囲は調整が必要。
- 不明点: 非公開の board approval threshold、法務レビュー詳細、国別労務制約は公開情報だけでは確定できない。

## Validation Queries

```text
site:nist.gov CSF 2.0 GOVERN policy roles responsibilities authorities oversight
site:iso.org ISO 9001 explained documented information responsibilities performance evaluation
site:coso.org internal control operations reporting compliance objectives
site:handbook.gitlab.com policy handbook owner exception approval
"policy exception" "risk acceptance" "compensating control" official
```

---

# 6. Clone Spec: Layer 02.02 業務プロセス

## Definition

業務プロセスは、顧客価値・内部成果・法規制・品質要求を満たすために、入力、出力、活動、責任、制御点、判断点、例外、指標、証跡を設計するレイヤーである。部門別手順ではなく、end-to-end value flow として設計する。

## Decision Question

先端組織は、どの価値流を対象に、どの入力/出力/活動/責任/制御点/例外/指標でプロセスを定義し、どのように継続改善するか。

## Frontier Exemplars

| Exemplar | 採用理由 | Source |
|---|---|---|
| ISO 9001 / ISO TC176 | process approach、risk-based thinking、documented information、monitoring、continual improvement を示す。 | S05, S06 |
| BPMN 2.0 | stakeholder が読め、かつ software process components に変換可能な process notation。 | S07 |
| Toyota Production System | ムダ排除、リードタイム短縮、jidoka、JIT、daily kaizen を業務改善原理として提供。 | S09 |
| AWS Operational Excellence | team organization、workload operation、operating at scale、evolving over time を示す。 | S10, S11 |
| DMN | 複雑な decision logic を BPMN process から分離する。 | S08 |

## Evidence Map

| Claim | Evidence | Confidence |
|---|---|---|
| プロセスは interrelated activities が inputs を intended result に変換する構造として扱う。 | S05, S06 | A |
| BPMN はプロセス図を stakeholder が直接使える形で表現し、必要に応じて実行コンポーネントへ変換できる。 | S07 | A |
| プロセス改善はムダ、リードタイム、異常停止、同期化、日次改善で測ることができる。 | S09 | B |
| プロセスの運用は team/role/goal と接続しなければ scale しない。 | S10, S11 | B |

## Core Philosophy

プロセスは「作業順序」ではなく、**結果を再現する制御システム**である。優れたプロセスは、入力・出力・制約・責任・例外・証跡・指標が見えるため、属人性を下げ、改善可能性を上げる。

## Decision Model

| Field | Spec |
|---|---|
| Inputs | 顧客要求、SLA/SLO、法規制、品質要求、リスク、既存 systems、handoff、失敗履歴、コスト、volume、季節性 |
| Criteria | outcome alignment、cycle time、quality、control strength、customer impact、automation potential、handoff reduction、auditability |
| Priorities | 1. 顧客/規制 outcome、2. 品質と安全性、3. end-to-end lead time、4. control/evidence、5. cost/toil reduction |
| Prohibitions | 部門最適だけのプロセス、owner 不明、start/end 不明、handoff 不明、例外未定義、指標なし、証跡なし |
| Exceptions | exception path を BPMN gateway / DMN decision / exception registry として設計する。 |
| Approvers | Process Owner、Control Owner、System Owner、Legal/Compliance、Customer/Operations representative |
| Review Cadence | 主要プロセスは四半期。高 volume/high risk process は monthly metrics review。インシデント・監査所見・SLA breach 後は event-driven review。 |

## Operating Model

| Component | Design |
|---|---|
| Roles | Process Owner、Process Analyst、Control Owner、Automation Owner、Data Owner、Frontline Operator、Exception Manager |
| Process | inventory → scope/value stream definition → current-state map → risk/control map → target-state design → pilot → rollout → measurement → improvement |
| Governance Forum | process design review、monthly process performance review、continuous improvement board |
| Artifacts | Process inventory、BPMN diagram、SIPOC、RACI/DRI、control points、work instruction、exception map、metric dashboard、change log |
| Tools | BPMN modeler、workflow engine、ticketing、process mining、BI dashboard、GRC、knowledge base |
| Audit Evidence | workflow logs、case records、approval records、control execution logs、exception records、change history、training records |

## Technical / Business Specification

### Process Record Schema

| Field | Required | Notes |
|---|---|---|
| process_id | Yes | 例: PROC-O2C-001 |
| process_name | Yes | 業務名 |
| value_stream | Yes | 例: order-to-cash、hire-to-retire、incident-to-resolution |
| owner / DRI | Yes | accountable role |
| trigger | Yes | start event |
| input | Yes | data/document/material/request |
| output | Yes | intended result |
| customer | Yes | external/internal customer |
| steps | Yes | BPMN / workflow IDs |
| decision_points | Yes | DMN / decision IDs |
| controls | Yes | control IDs |
| exceptions | Yes | exception IDs / routes |
| systems | Yes | apps, data stores, integrations |
| RACI | Yes | responsible/accountable/consulted/informed |
| SLA/SLO | Conditional | if service-impacting |
| metrics | Yes | cycle time, defect, cost, volume, quality |
| evidence | Yes | logs, tickets, approvals |
| review_cadence | Yes | monthly/quarterly/event-driven |

## Metrics

- End-to-end lead time / cycle time
- First-pass yield / rework rate
- Defect / incident rate
- Handoff count and waiting time
- Work-in-progress / queue age
- SLA/SLO compliance
- Cost per case / cost per transaction
- Exception rate
- Automation coverage
- Process adherence and evidence completeness

## Failure Modes

| Failure | 兆候 | 防止策 |
|---|---|---|
| 部門最適 | 部門 KPI は達成するが顧客 lead time が長い | value stream owner と end-to-end metric を置く |
| プロセス過剰文書化 | 手順書が多いが現場が使わない | BPMN/DMN + minimal work instruction + dashboard に寄せる |
| 例外の闇運用 | 「いつもの workaround」が増える | exception registry、root cause review、process redesign |
| 制御点抜け | 監査・品質不良が出る | control point と evidence requirement をプロセスに埋め込む |
| 自動化による固定化 | 悪いプロセスをそのまま自動化 | automate 前に value stream と waste を見直す |

## Anti-patterns

- プロセス名が部署名と同じで、顧客成果や start/end が不明。
- 手順書はあるが、実行ログ、完了条件、例外条件、owner がない。
- すべての判断を BPMN gateway に詰め込み、ルール変更のたびにプロセス全体を変更する。
- プロセス改善が「会議での感想」に留まり、cycle time、defect、rework、cost が見えない。

## Clone Implementation Guide

1. 重要 value stream を 5〜10 個に絞り、process inventory を作る。
2. 各プロセスに `trigger / input / output / owner / customer / metrics / controls / exceptions` を埋める。
3. 高リスク・高 volume プロセスを BPMN 化し、複雑判断は DMN 化する。
4. 現場運用に合わせて workflow / ticketing / logs を証跡源にする。
5. 月次で bottleneck、exception、defect、rework を見て、process backlog を運営する。

## Confidence & Unknowns

- 確度 A: ISO/BPMN は process approach と process notation を直接裏付ける。
- 確度 B: Toyota/AWS の運用哲学は広く移植可能だが、製造・クラウド・SaaS で metric の定義は変える必要がある。
- 不明点: 具体的な業界規制、ERP/CRM/workflow 構成、現行業務 volume は個別調査が必要。

## Validation Queries

```text
site:iso.org ISO 9001 process approach documented information performance evaluation
site:omg.org BPMN business process model notation stakeholders process components
site:global.toyota Toyota Production System jidoka just-in-time kaizen lead time
site:docs.aws.amazon.com wellarchitected operational excellence operating model process
```

---

# 7. Clone Spec: Layer 02.03 業務ルール/例外

## Definition

業務ルール/例外は、反復判断の条件、閾値、禁止事項、デフォルト処理、例外条件、補完統制、失効条件、レビュー責任を管理するレイヤーである。プロセスの flow から decision logic を分離し、変更・監査・自動化を容易にする。

## Decision Question

先端組織は、どの判断をルール化し、どの判断を人間判断に残し、どの条件で例外を許可し、どの証跡と補完統制でリスクを管理するか。

## Frontier Exemplars

| Exemplar | 採用理由 | Source |
|---|---|---|
| OMG DMN | business decisions / business rules を明確に仕様化し、decision table で曖昧さを減らす。 | S08 |
| BPMN 2.0 | process flow と decision points の配置を定義する。 | S07 |
| Google SRE Error Budget Policy | threshold-based exception / escalation / postmortem trigger の実例。 | S19 |
| NIST CSF / RMF / SP 800-53 | risk governance、control selection、authorization、continuous monitoring を例外管理に接続する。 | S01, S02, S03 |
| GitLab Required Approvals | 特定条件を満たすと追加承認を要求する rule-based approval の公開例。 | S15 |

## Evidence Map

| Claim | Evidence | Confidence |
|---|---|---|
| 業務判断は DMN により business users と technical developers が共有できる rule artifact になる。 | S08 | A |
| decision table は inputs, outputs, rules を持つ。 | S08 | A |
| error budget policy のように、閾値を超えると action item / escalation / freeze を発動できる。 | S18, S19 | A/B |
| 例外は risk governance と control monitoring に接続しなければならない。 | S01, S02, S03 | A/B |

## Core Philosophy

ルールは「暗黙の慣習」ではなく、**意思決定を再現・変更・監査するための仕様**である。例外はルールの失敗ではなく、ルールが扱えない状況を可視化する feedback signal である。

## Decision Model

| Field | Spec |
|---|---|
| Inputs | 方針、規制、契約、リスク評価、業務データ、顧客属性、取引額、SLO/error budget、過去例外、監査所見 |
| Criteria | 反復性、影響度、誤判定コスト、自動化可能性、説明可能性、監査可能性、変更頻度 |
| Priorities | 1. 法規制/安全性、2. 顧客/財務影響、3. 一貫性、4. 速度、5. 人間判断の余地 |
| Prohibitions | owner 不明 rule、hard-coded business rule、期限なし例外、口頭 override、補完統制なし例外、ルール変更の未テスト |
| Exceptions | 例外は `scope / reason / risk / compensating_control / approver / expiry / monitoring` を必須にする。 |
| Approvers | Rule Owner、Process Owner、Risk/Compliance、System Owner、Business Owner |
| Review Cadence | 高影響 rule は月次/四半期。例外が閾値を超えたら rule redesign。規制・契約変更時は即時。 |

## Operating Model

| Component | Design |
|---|---|
| Roles | Rule Owner、Decision Analyst、Exception Owner、Risk Owner、Control Owner、Automation Owner |
| Process | rule discovery → decision model → test cases → approval → deploy → monitor → exception review → rule update |
| Governance Forum | rule review board、exception review、control/risk review |
| Artifacts | Rule catalog、decision table、test cases、exception register、risk acceptance record、compensating controls、rule change log |
| Tools | DMN modeler、rules engine、workflow、GRC、ticketing、feature flag、analytics |
| Audit Evidence | rule version、execution log、decision output、override log、exception approvals、expiry review、test results |

## Technical / Business Specification

### Rule Record Schema

| Field | Required | Notes |
|---|---|---|
| rule_id | Yes | 例: RULE-CREDIT-012 |
| decision_name | Yes | 何を判断するか |
| policy_source | Yes | policy_id / regulation / contract |
| owner | Yes | accountable role |
| inputs | Yes | variables / data source |
| conditions | Yes | if/then/else, decision table rows |
| outputs | Yes | approve/reject/manual review/route 等 |
| hit_policy | Conditional | DMN decision table の hit policy |
| default_outcome | Yes | 条件不一致時の扱い |
| exception_allowed | Yes | true/false と条件 |
| exception_approver | Conditional | 例外可の場合必須 |
| compensating_control | Conditional | high-risk exception では必須 |
| test_cases | Yes | positive/negative/boundary cases |
| deployment_target | Conditional | workflow/rules engine/system |
| effective_date / expiry | Yes | rule validity |
| review_date | Yes | stale 防止 |

### Exception Record Schema

| Field | Required | Notes |
|---|---|---|
| exception_id | Yes | 例: EXC-2026-0042 |
| related_rule / policy / process | Yes | 何からの例外か |
| requestor | Yes | 誰が要求したか |
| business_reason | Yes | 目的と代替案 |
| risk_assessment | Yes | impact / likelihood |
| scope | Yes | 対象期間、顧客、システム、金額、地域 |
| compensating_control | Yes | high risk では必須 |
| approver | Yes | risk owner または delegated authority |
| expiry_date | Yes | 無期限禁止 |
| monitoring | Yes | 何を監視するか |
| closure_outcome | Yes | expire / renew / convert to rule / reject |

## Metrics

- Rule execution volume
- Override / manual review rate
- Exception rate by rule/process/team
- Expired exceptions
- Rule conflict count
- Decision latency
- False positive / false negative rate
- Audit findings caused by rule ambiguity
- Rule change lead time
- Percentage of rules with tests

## Failure Modes

| Failure | 兆候 | 防止策 |
|---|---|---|
| ルールの hard-code | business 変更が system release 待ちになる | DMN/rule catalog と versioned deployment |
| 例外の常態化 | exception rate が上がる | rule redesign trigger を設定 |
| 例外期限切れ | 期限超過が放置 | auto-expiry, reminder, escalation |
| ルール衝突 | 同じケースに異なる結論 | rule dependency map と test suite |
| 説明不能判断 | 顧客/監査に説明できない | input/output/rationale/evidence を記録 |

## Anti-patterns

- 承認者の裁量だけでルールの結果を覆す。
- 例外を「一時的」と言いながら expiry_date を置かない。
- BPMN の分岐に複雑な価格・与信・リスク判断を埋め込む。
- ルール変更に test cases と impact analysis がない。
- ルール owner と system owner が分離されず、business change が追随しない。

## Clone Implementation Guide

1. 重要プロセスから decision points を抽出し、`rule_id` を付ける。
2. 複雑/高頻度/高影響判断を DMN decision table にする。
3. 例外申請を workflow 化し、risk acceptance と expiry を必須にする。
4. ルールと例外を dashboard 化し、例外率が高い rule を redesign backlog に入れる。
5. ルール変更を test suite と approval record に接続する。

## Confidence & Unknowns

- 確度 A: DMN/BPMN は rule/process separation を直接裏付ける。
- 確度 B: 例外管理の設計は NIST/Google/GitLab から強く推定できるが、業界ごとのリスク許容度は別途必要。
- 不明点: 規制業務では例外自体が禁止されるルールがある。個別法規制 mapping が必要。

## Validation Queries

```text
site:omg.org DMN business decisions business rules decision tables
site:docs.camunda.io DMN decision table inputs outputs rules hit policy
site:sre.google error budget policy escalation postmortem threshold
site:handbook.gitlab.com required approvals considerations approval process
```

---

# 8. Clone Spec: Layer 02.04 承認

## Definition

承認は、誰がどの判断に責任を持ち、どの条件で追加承認・拒否・エスカレーション・事後レビューが必要になるかを決めるレイヤーである。承認は統制であると同時に、速度を落とす制約でもあるため、risk-based / DRI-first に設計する。

## Decision Question

先端組織は、通常判断をどこまで owner/DRI に委譲し、財務、顧客、法務、評判、セキュリティ、不可逆性、横断影響が大きい時にどの承認者を追加するか。

## Frontier Exemplars

| Exemplar | 採用理由 | Source |
|---|---|---|
| GitLab DRI | 最終意思決定者を明示し、曖昧さと analysis paralysis を減らす公開運用例。 | S14 |
| GitLab Required Approvals | 特定条件を満たした時だけ追加承認を求める risk-triggered approval。 | S15 |
| Google SRE SLO/Error Budget Policy | SLO と error budget の承認を stakeholders に要求し、閾値超過時の action/escalation を明文化。 | S18, S19 |
| NIST RMF | control selection/assessment/authorization/continuous monitoring を構造化し、authorization decision を risk management に接続する。 | S02 |
| DORA | heavyweight change approval が performance を損ねる anti-pattern であることを示唆。 | S21 |

## Evidence Map

| Claim | Evidence | Confidence |
|---|---|---|
| DRI は最終意思決定権を持つが、関係者から input を集める。 | S14 | B |
| 追加承認は財務影響、risk、reputation、3+ functions、複数 success criteria などで発動する。 | S14, S15 | B |
| Error budget policy は product manager, developers, SRE などの stakeholder agreement を必要とする。 | S18 | A/B |
| 承認は authorization / continuous monitoring と接続する。 | S02 | A |
| 重い change approval は delivery performance を悪化させる可能性がある。 | S21 | B |

## Core Philosophy

承認は「上位者が安心するためのハンコ」ではなく、**責任、リスク、不可逆性、利害対立を処理するための制御点**である。標準判断は DRI に委譲し、承認は例外的・閾値ベースにする。

## Decision Model

| Field | Spec |
|---|---|
| Inputs | decision type、financial impact、customer impact、legal/regulatory impact、security/privacy risk、reversibility、cross-functional scope、SLO/error budget、architecture impact、brand/reputation risk |
| Criteria | irreversible か、threshold 超過か、複数機能に影響するか、顧客/契約/規制に影響するか、既存方針から逸脱するか |
| Priorities | 1. 法規制/契約、2. 安全性/セキュリティ、3. 顧客・評判・財務リスク、4. 速度、5. 学習 |
| Prohibitions | 全件承認、承認者不明、approval by title only、承認と責任の分離、事後承認常態化、承認理由なし |
| Exceptions | 緊急承認は break-glass として許可。ただし事後レビュー、期限、証跡、補完統制を必須化。 |
| Approvers | DRI を既定。閾値により CFO/Legal/Security/Risk/Architecture/Executive/Fellow Engineer 等を追加。 |
| Review Cadence | 承認 matrix は四半期。承認 lead time と bypass は月次。重大 incident 後は matrix を見直す。 |

## Operating Model

| Component | Design |
|---|---|
| Roles | DRI、Approver、Reviewer、Consulted、Informed、Risk Owner、Executive Escalation Owner |
| Process | proposal → threshold check → DRI decision or approval workflow → decision record → execution → monitoring → post-decision review |
| Governance Forum | decision review、architecture review、risk approval board、incident review、quarterly approval matrix review |
| Artifacts | Approval matrix、decision memo、proposal issue、risk assessment、approval log、RACI/DACI、rollback plan、monitoring plan |
| Tools | workflow/ticketing、e-signature、GRC、issue tracker、architecture decision records、dashboard |
| Audit Evidence | proposal, approver identity, date/time, threshold, rationale, alternatives, risk acceptance, execution outcome |

## Technical / Business Specification

### Approval Trigger Matrix

| Trigger | Threshold Example | Default Approval |
|---|---|---|
| Financial impact | 予算外支出、pricing 変更、revenue/cost 重大影響 | DRI + Finance + Executive |
| Legal/regulatory | 契約変更、規制対応、privacy/security commitments | DRI + Legal/Compliance |
| Security/privacy | privileged access、customer data、control exception | DRI + Security/Risk |
| Architecture irreversibility | separate database, new microservice, platform split, irreversible vendor lock-in | DRI + Architecture authority |
| Cross-functional | 3 functions 以上、複数 KPI に影響 | DRI + function heads |
| Reputation/customer impact | major policy/ToS/pricing/customer-visible change | DRI + GTM/Legal/Executive |
| SLO/Error budget | error budget exhaustion, freeze, reliability tradeoff | Product + Development + SRE |
| Emergency | outage, security incident, time-critical legal action | Incident Commander / delegated executive, post-review required |

### Decision Memo Schema

| Field | Required | Notes |
|---|---|---|
| decision_id | Yes | DEC-YYYY-### |
| DRI | Yes | accountable owner |
| decision_type | Yes | product/process/security/finance/legal/etc. |
| context | Yes | なぜ今必要か |
| options | Yes | 少なくとも selected + rejected alternatives |
| recommendation | Yes | DRI の判断 |
| risk_assessment | Yes | impact/likelihood/mitigation |
| approval_triggers | Yes | matrix 上の該当条件 |
| approvers | Conditional | 該当時必須 |
| consulted / informed | Recommended | RACI/DACI |
| rollback / exit plan | Conditional | irreversible でない場合も推奨 |
| monitoring metric | Yes | 判断後に何を見るか |
| decision_date | Yes | auditability |

## Metrics

- Approval lead time
- Approval queue age
- Number of approval touchpoints
- Percentage of DRI-only vs escalated decisions
- Retroactive approvals / bypasses
- Decision reversal rate
- Incident/audit finding caused by wrong approval path
- Cycle time impact of approval
- Ratio of threshold-triggered approvals to blanket approvals

## Failure Modes

| Failure | 兆候 | 防止策 |
|---|---|---|
| 承認過多 | 速度低下、shadow process | risk-triggered matrix、DRI-first、approval SLA |
| 承認不足 | 高影響判断が現場だけで進む | threshold detection、decision memo、audit sampling |
| 責任分散 | 承認者は多いが accountable がいない | single DRI + final approver を分ける |
| 事後承認常態化 | urgent 扱いが多い | break-glass monitoring、post-review、recurrence cap |
| 承認理由なし | 判断品質が検証不能 | rationale / options / metrics を必須化 |

## Anti-patterns

- すべての変更を committee approval にかける。
- 承認者を役職階層で決め、リスク/専門性/owner に基づかない。
- DRI がいない状態で consensus を承認と見なす。
- 例外承認に期限と補完統制がない。
- 事後承認を通常プロセスとして許容する。

## Clone Implementation Guide

1. 主要 decision type を棚卸しし、DRI と approval triggers を定義する。
2. 承認 matrix を `financial / legal / security / customer / architecture / cross-functional / SLO` で作る。
3. DRI-only 判断と escalated approval を分ける。
4. Decision memo template と issue/workflow を用意し、証跡を自動保存する。
5. 月次で承認 lead time、bypass、incident linkage をレビューし、approval debt を削る。

## Confidence & Unknowns

- 確度 B: GitLab/Google SRE の公開運用はデジタル企業に有効な direct operational exemplar。
- 確度 A: NIST RMF は authorization / continuous monitoring の規範構造を提供。
- 不明点: 具体的な金額閾値、法務承認範囲、役員会決裁規程は企業・国・業界で異なる。

## Validation Queries

```text
site:handbook.gitlab.com DRI rare need for approvals financial risk reputation
site:handbook.gitlab.com development required approvals approval process CEO Fellow Engineer
site:sre.google implementing SLOs stakeholder agreement error budget policy approvers
site:dora.dev 2019 heavyweight change approval negatively impact performance
site:csrc.nist.gov SP 800-37 authorization continuous monitoring risk management
```

---

# 9. Clone Spec: Layer 02.05 監査

## Definition

監査は、方針・プロセス・ルール・承認・権限・運用が設計通りに動作し、目的、法規制、顧客約束、リスク管理に合致しているかを、証跡に基づき独立または準独立に評価し、改善へ接続するレイヤーである。

## Decision Question

先端組織は、どの統制を、どの証拠で、どの頻度・独立性・サンプル・基準で評価し、発見事項をどの remediation loop に接続するか。

## Frontier Exemplars

| Exemplar | 採用理由 | Source |
|---|---|---|
| COSO Internal Control | operations, reporting, compliance objectives を満たす internal control 設計の代表枠組み。 | S04 |
| NIST RMF | control selection, implementation, assessment, authorization, continuous monitoring の構造を示す。 | S02 |
| NIST SP 800-53 | security/privacy controls catalog として audit/accountability/access controls を提供。 | S03 |
| AICPA SOC 2 / Trust Services Criteria | service organization controls の外部保証・統制評価基準。 | S22, S23 |
| ISO 19011 | audit program、audit principles、management system audits、auditor competence の標準ガイド。 | S24 |
| GitLab IAM | audit/compliance artifacts、GitOps、merge request approval rules、audit/diff logging の公開実装例。 | S16 |

## Evidence Map

| Claim | Evidence | Confidence |
|---|---|---|
| 内部統制は operations/reporting/compliance objectives を達成するための設計・実行対象である。 | S04 | A |
| RMF は categorization, control selection, implementation, assessment, authorization, continuous monitoring をつなぐ。 | S02 | A |
| SP 800-53 は組織・資産を守る controls catalog であり、risk-based に customisable。 | S03 | A |
| SOC 2 は security, availability, processing integrity, confidentiality, privacy に関する controls report である。 | S22, S23 | A/B |
| ISO 19011 は audit program と auditor competence を扱う。 | S24 | A |
| GitOps/IaC/API を使うと audit artifacts と diff logging を自動化できる。 | S16 | B |

## Core Philosophy

監査は「チェックリスト消化」ではなく、**統制と業務の実効性を証拠で検証し、改善へ戻す feedback loop**である。監査が強い組織は、監査時に証拠を作るのではなく、日常運用から証拠が生まれる。

## Decision Model

| Field | Spec |
|---|---|
| Inputs | policy/control catalog、process logs、access logs、approval records、incident records、risk register、customer commitments、regulations、prior audit findings |
| Criteria | materiality、risk、control criticality、evidence reliability、sample coverage、independence、remediation effectiveness |
| Priorities | 1. material/high-risk controls、2. regulatory/customer commitments、3. prior findings、4. high-change areas、5. automation opportunities |
| Prohibitions | 証跡後付け、自己承認、監査人と control owner の兼務、所見放置、scope 不明、サンプル根拠なし |
| Exceptions | 監査証跡不足は finding として扱い、compensating evidence と remediation を記録する。 |
| Approvers | Audit Program Owner、Internal Audit、Control Owner、Risk/Compliance、External Auditor where applicable |
| Review Cadence | 高リスク統制は continuous/quarterly、通常統制は半期/年次。重大 incident / control failure 後は event-driven audit。 |

## Operating Model

| Component | Design |
|---|---|
| Roles | Audit Program Owner、Internal Auditor、External Auditor、Control Owner、Process Owner、Evidence Owner、Remediation Owner |
| Process | audit planning → scope/control selection → evidence request/collection → testing → findings → management response → remediation → retest → closure |
| Governance Forum | audit committee、quarterly control review、monthly remediation review、external audit kickoff/exit meeting |
| Artifacts | Audit plan、control matrix、evidence catalog、test scripts、sample list、findings register、management response、remediation plan、closure evidence |
| Tools | GRC、SIEM/logging、workflow、IAM、version control、data warehouse、evidence automation |
| Audit Evidence | logs、tickets、approval records、access reviews、configuration diffs、training records、process outputs、control test results |

## Technical / Business Specification

### Control / Audit Record Schema

| Field | Required | Notes |
|---|---|---|
| control_id | Yes | CTRL-### |
| objective | Yes | 何を防ぐ/検知するか |
| related_policy | Yes | policy_id |
| related_process | Yes | process_id |
| control_type | Yes | preventive/detective/corrective |
| frequency | Yes | continuous/daily/monthly/quarterly/annual |
| owner | Yes | control owner |
| performer | Yes | 実行者 |
| reviewer | Conditional | review control では必須 |
| evidence_source | Yes | log/ticket/config/report |
| test_procedure | Yes | どう検証するか |
| sample_method | Conditional | sample audit の場合必須 |
| result | Yes | pass/fail/exception |
| finding_id | Conditional | fail の場合 |
| remediation_owner | Conditional | finding の場合 |
| due_date | Conditional | finding の場合 |
| retest_result | Conditional | remediation 後 |

### Audit Program Cadence

| Audit Type | Frequency | Trigger |
|---|---|---|
| Continuous control monitoring | Continuous / daily | access, config, logs, transactions |
| Control self-assessment | Quarterly | owner-level assertion |
| Internal audit | Semiannual / annual | risk-based plan |
| External audit / certification | Annual or contractual | SOC 2, ISO, customer requirement |
| Incident-driven audit | Event-driven | breach, outage, fraud, regulatory inquiry |
| Supplier audit | Risk-based | critical vendor, data processing, contractual requirement |

## Metrics

- Control pass/fail rate
- Findings by severity
- Remediation SLA adherence
- Repeat findings rate
- Evidence freshness
- Evidence automation coverage
- Audit request cycle time
- Number of controls without owner
- Control exceptions aging
- Audit cost per control / per evidence item

## Failure Modes

| Failure | 兆候 | 防止策 |
|---|---|---|
| 証跡後付け | 監査前に資料作成が集中 | evidence-by-design、logs/workflow integration |
| control owner 不明 | 所見の対応が遅い | control matrix with accountable owner |
| 監査と現場の乖離 | 監査項目が実業務と合わない | process mapping と control mapping の同期 |
| 所見放置 | overdue findings、repeat findings | remediation SLA、executive escalation |
| 監査過剰 | 現場負荷が大きい | risk-based scoping、automation、control rationalization |

## Anti-patterns

- 監査対応チームが証跡を「作る」。
- 監査基準が方針・プロセス・権限・実ログと接続していない。
- 年次監査だけで high-risk controls を見ている。
- 所見が Jira/ticket/workflow に接続せず、管理表で止まる。
- external audit のための統制と、実運用の統制が別物になる。

## Clone Implementation Guide

1. 重要方針から control catalog を作り、各 control に owner/evidence/frequency を付ける。
2. evidence source を workflow/log/IAM/GitOps から自動取得できるようにする。
3. high-risk controls から continuous monitoring を実装する。
4. findings register と remediation workflow を統一し、due date と retest を必須化する。
5. 四半期ごとに control effectiveness と audit burden を見直し、不要統制を削る。

## Confidence & Unknowns

- 確度 A: COSO/NIST/ISO/AICPA は監査・統制・保証の構造を直接裏付ける。
- 確度 B: GitLab IAM は evidence automation の公開実装例として強いが、全社統制全体の公開情報ではない。
- 不明点: 個別 SOC 2 report、ISO certificate scope、内部監査計画は通常非公開。

## Validation Queries

```text
site:coso.org internal control operations reporting compliance objectives
site:csrc.nist.gov SP 800-37 control assessment authorization continuous monitoring
site:csrc.nist.gov SP 800-53 audit accountability access control controls catalog
site:aicpa-cima.com SOC 2 controls security availability processing integrity confidentiality privacy
site:iso.org ISO 19011 audit program auditor competence management system audit
site:handbook.gitlab.com IAM audit compliance artifacts diff logging GitOps
```

---

# 10. Clone Spec: Layer 02.06 権限

## Definition

権限は、誰が何を決められ、どの情報・システム・業務操作へアクセスでき、どの職務分掌・監査ログ・失効・緊急権限で制御されるかを設計するレイヤーである。単なる IT access ではなく、decision authority と operational access の統合モデルである。

## Decision Question

先端組織は、役割、責任、意思決定権限、アクセス権限、職務分掌、緊急権限、失効、監査証跡をどのように設計・レビュー・自動化するか。

## Frontier Exemplars

| Exemplar | 採用理由 | Source |
|---|---|---|
| NIST CSF 2.0 | roles, responsibilities, authorities を governance outcome に置く。 | S01 |
| NIST SP 800-53 | access control と audit/accountability の control catalog。 | S03 |
| NIST RMF | controls に対する responsibility/accountability、authorization、continuous monitoring を示す。 | S02 |
| GitLab IAM | RBAC/IAM、provisioning/deprovisioning、GitOps、audit/diff logging の公開実装例。 | S16 |
| GitLab DRI/RACI | decision authority と accountability を明確化する。 | S14 |
| ISO/IEC 27001 overview | roles/responsibilities/governance/internal audit を ISMS 要求として整理する。 | S25 |

## Evidence Map

| Claim | Evidence | Confidence |
|---|---|---|
| roles/responsibilities/authorities は risk governance の中核である。 | S01 | A |
| controls は business needs, laws, policies, standards に基づき選択され、組織 risk process に組み込まれる。 | S03 | A |
| IAM/RBAC は provisioning, deprovisioning, policies, audit artifacts と接続する。 | S16 | B |
| DRI/RACI は decision accountability を明示する。 | S14 | B |
| ISMS では roles/responsibilities/governance/internal audit/continual improvement が要求される。 | S25 | B |

## Core Philosophy

権限は「アクセスを与える」ことではなく、**業務結果に責任を持つ役割へ、必要最小限の操作権と意思決定権を与え、証跡と失効を保証すること**である。

## Decision Model

| Field | Spec |
|---|---|
| Inputs | role catalog、job architecture、process RACI、system/data classification、risk level、legal/regulatory constraints、SoD rules、employment lifecycle、vendor access |
| Criteria | need-to-know、least privilege、separation of duties、business continuity、auditability、automation feasibility、revocation speed |
| Priorities | 1. customer/data safety、2. legal/compliance、3. operational continuity、4. least privilege、5. self-service efficiency |
| Prohibitions | shared account、orphan account、standing admin where not needed、SoD conflict、unlogged break-glass、access without owner、manual spreadsheet-only reviews |
| Exceptions | break-glass / emergency access は short-lived、logged、approved、post-reviewed。 |
| Approvers | Role Owner、System Owner、Data Owner、Manager、Security/IAM、Risk/Compliance for privileged/high-risk access |
| Review Cadence | privileged access は monthly/quarterly。standard access は quarterly/semiannual。joiner/mover/leaver は event-driven。 |

## Operating Model

| Component | Design |
|---|---|
| Roles | IAM Owner、Role Owner、System Owner、Data Owner、Manager、Security Reviewer、Access Reviewer、Break-glass Approver |
| Process | role definition → access mapping → request/provision → approval → use/logging → review → deprovision → audit |
| Governance Forum | access review board、SoD review、privileged access review、IAM change review |
| Artifacts | Role catalog、permission matrix、SoD matrix、access request record、access review record、break-glass log、deprovisioning log |
| Tools | IAM/IdP、RBAC/ABAC、PAM、workflow、SIEM/logging、GitOps/IaC、HRIS integration |
| Audit Evidence | user listing、RBAC mappings、group membership、approval records、access logs、diff logs、offboarding records |

## Technical / Business Specification

### Authority Matrix Schema

| Field | Required | Notes |
|---|---|---|
| role_id | Yes | ROLE-### |
| role_name | Yes | business role / technical role |
| decision_rights | Yes | 何を決められるか |
| process_scope | Yes | 対象プロセス |
| system_scope | Conditional | 対象 system/data |
| permissions | Yes | read/write/approve/admin/export/delete |
| conditions | Yes | geography, entity, data class, amount threshold, time window |
| approver | Yes | granting authority |
| reviewer | Yes | periodic review owner |
| SoD_conflicts | Yes | incompatible roles/actions |
| break_glass_allowed | Yes | yes/no and condition |
| provision_method | Yes | automatic/manual/GitOps/API |
| deprovision_trigger | Yes | termination, transfer, expiry, contract end |
| logging_required | Yes | events to log |
| review_cadence | Yes | monthly/quarterly/semiannual |

## Metrics

- Privileged accounts count
- Standing admin ratio
- Orphan / stale accounts
- Access review completion rate
- Access review exceptions
- SoD violations
- Joiner/mover/leaver SLA
- Deprovisioning MTTR
- Break-glass usage and post-review completion
- Permission drift from role baseline
- Number of manual access grants outside workflow

## Failure Modes

| Failure | 兆候 | 防止策 |
|---|---|---|
| 過剰権限 | 高権限ユーザーが多い | least privilege, role baseline, periodic review |
| 退職/異動後残存 | orphan account, stale groups | HRIS-triggered deprovisioning |
| SoD 逸脱 | 同一人物が申請・承認・監査 | SoD matrix and workflow enforcement |
| shared account | 操作者特定不能 | individual identity, PAM/session recording |
| break-glass 濫用 | emergency access が定常化 | time-bound access, mandatory post-review |
| decision authority 不明 | だれが決めるか不明 | DRI/RACI authority map |

## Anti-patterns

- job title と access role を一対一で固定し、実際の業務 responsibility を見ない。
- 退職時だけ access を消し、異動時の mover control がない。
- privileged access を permanent にする。
- 職務分掌を監査時だけ確認し、workflow で防止しない。
- 意思決定権限と system access 権限を別々に管理する。

## Clone Implementation Guide

1. business roles と technical roles を分け、authority matrix を作る。
2. 重要プロセスごとに RACI/DRI と access permissions を接続する。
3. JML（joiner/mover/leaver）を HRIS/IAM/workflow と接続する。
4. privileged access、SoD conflicts、break-glass を先に自動検出する。
5. access review を evidence source に接続し、review exceptions を remediation ticket 化する。

## Confidence & Unknowns

- 確度 A: NIST CSF / SP 800-53 は権限・統制・監査の構造を直接裏付ける。
- 確度 B: GitLab IAM は公開実装例として強いが、全社の具体的権限 matrix は非公開。
- 不明点: 実際の role taxonomy、各システム権限、国別データ規制、顧客契約に基づく access constraints は個別調査が必要。

## Validation Queries

```text
site:csrc.nist.gov SP 800-53 access control audit accountability least privilege separation of duties
site:nist.gov CSF roles responsibilities authorities policy oversight
site:handbook.gitlab.com identity access management RBAC provisioning deprovisioning audit artifacts
site:handbook.gitlab.com DRI RACI accountable final decision
site:nsai.ie ISO 27001 assigned roles responsibilities governance internal audit
```

---

# 11. Clone Spec: Layer 02.07 組織設計

## Definition

組織設計は、どの価値流・顧客成果・システム境界・認知負荷・依存関係に基づき、チーム、役割、責任、相互作用、権限、評価指標を設計するかを決めるレイヤーである。人員表ではなく、業務成果を実現する operating architecture である。

## Decision Question

先端組織は、価値流、製品/サービス、システム構造、顧客成果、認知負荷、依存関係を入力に、どのチーム境界、所有権、相互作用モード、権限、指標を設計するか。

## Frontier Exemplars

| Exemplar | 採用理由 | Source |
|---|---|---|
| AWS DevOps Guidance | チーム構造を business outcomes と system architecture に合わせ、ownership を明確にする。 | S12 |
| AWS Operating Model | operating model を可視化し、チームの役割・相互依存・shared goals を理解する。 | S11 |
| Team Topologies | stream-aligned, platform, enabling, complicated subsystem teams と interaction modes/cognitive load を定義する。 | S20 |
| GitLab Handbook / DRI | transparent handbook、DRI、RACI/DACI による responsibility clarity。 | S13, S14 |
| DORA | sociotechnical capabilities、documentation、culture、approval anti-patterns を performance と接続する。 | S21 |
| Toyota TPS | 全員参加 kaizen と現場改善を組織文化として扱う。 | S09 |

## Evidence Map

| Claim | Evidence | Confidence |
|---|---|---|
| チームは desired business outcomes と system architecture / interactions に合わせて設計する。 | S12 | A/B |
| operating model は team roles, interacting teams, shared goals を理解する必要がある。 | S11 | B |
| team types と interaction modes を明示すると依存関係と認知負荷を管理できる。 | S20 | B |
| DRI/RACI は責任と意思決定権限を明確にする。 | S14 | B |
| 高品質な internal documentation と sociotechnical systems は delivery/operations performance に影響する。 | S21 | B |

## Core Philosophy

組織設計の frontier pattern は、**成果に近いチームに所有権を置き、複雑性を platform/enabling/complicated subsystem teams で吸収し、相互作用モードを明示して認知負荷を制御すること**である。

## Decision Model

| Field | Spec |
|---|---|
| Inputs | business outcomes、customer segments、value streams、product architecture、system dependencies、team cognitive load、skills、risk/compliance requirements、geography/timezone、operational ownership |
| Criteria | end-to-end ownership、customer proximity、cognitive load、dependency reduction、speed, quality, resilience, compliance, talent scalability |
| Priorities | 1. value stream ownership、2. system/organization alignment、3. cognitive load、4. platform leverage、5. governance clarity |
| Prohibitions | owner 不明、handoff-heavy silos、hybrid team type 乱立、shared component ownership without interface、matrix authority conflict |
| Exceptions | 高度専門領域は complicated subsystem team、能力育成は enabling team、共通基盤は platform team として切り出す。 |
| Approvers | Business Owner、Product/Engineering/Operations leaders、People/HR、Finance、Risk/Compliance for regulated functions |
| Review Cadence | 半期/年次の org review。高成長・戦略転換・システム再設計・incident recurring 時は event-driven。 |

## Operating Model

| Component | Design |
|---|---|
| Roles | Value Stream Owner、Team Lead、DRI、Product Owner、Platform Owner、Enabling Lead、Operations Lead、People Partner |
| Process | value stream mapping → team boundary design → ownership map → interaction mode design → authority matrix → KPI design → operating cadence → review |
| Governance Forum | quarterly org design review、value stream review、platform council、architecture council、people review |
| Artifacts | Team charter、ownership map、value stream map、interaction map、RACI/DACI、skill matrix、cognitive load assessment、team KPI dashboard |
| Tools | org design map、architecture map、service catalog、product roadmap、OKR system、team health survey、dependency tracker |
| Audit Evidence | charters、role descriptions、decision records、ownership registry、KPI dashboards、org review minutes |

## Technical / Business Specification

### Team Charter Schema

| Field | Required | Notes |
|---|---|---|
| team_id | Yes | TEAM-### |
| team_type | Yes | stream-aligned / platform / enabling / complicated-subsystem / shared-service |
| mission | Yes | outcome and customers |
| value_stream | Conditional | stream-aligned では必須 |
| services / products owned | Yes | ownership registry |
| DRI / lead | Yes | accountable role |
| decision_rights | Yes | what team can decide independently |
| interfaces | Yes | APIs, SLAs, operating agreements |
| interaction_modes | Yes | collaboration / X-as-a-Service / facilitating |
| dependencies | Yes | upstream/downstream teams |
| cognitive_load_risks | Recommended | known complexity constraints |
| KPIs | Yes | outcome, delivery, quality, cost, risk |
| operating_cadence | Yes | ceremonies/reviews |
| escalation_path | Yes | cross-team conflicts |

### Organization Design Rules

| Rule | Meaning |
|---|---|
| Value first | Primary teams should own customer/business outcomes, not functional tasks only. |
| Interface explicit | Cross-team dependencies require clear interface, SLA/SLO, escalation path. |
| Platform as product | Platform teams must treat internal teams as customers and measure adoption/satisfaction. |
| Enable temporarily | Enabling teams should transfer capability, not become permanent bottlenecks. |
| Cognitive load cap | Team scope should be reduced when domain + technical + operational complexity exceeds capacity. |
| Ownership visible | Service, process, data, control, policy each has an owner registry. |

## Metrics

- Delivery lead time / deployment frequency / change failure / restore time where applicable
- Value stream cycle time
- Team dependency count
- Ownership ambiguity incidents
- Cross-team escalation volume
- Platform adoption and internal customer satisfaction
- Team cognitive load / team health
- Ratio of work owned end-to-end vs handoff-based
- Decision latency by team/interface
- Operational load / toil per team

## Failure Modes

| Failure | 兆候 | 防止策 |
|---|---|---|
| Silo design | 顧客成果に責任を持つ owner がいない | value stream ownership |
| 認知負荷過多 | delivery slowdown, incident, burnout | team scope reduction, platform/enabling support |
| Platform bottleneck | platform team が承認ゲート化 | platform as product, self-service, adoption metrics |
| Matrix conflict | だれが決めるか不明 | DRI/RACI/DACI and authority map |
| Team type drift | hybrid team 乱立 | team charter review and topology rationalization |

## Anti-patterns

- 組織を既存部門・職能だけで設計し、価値流を見ない。
- Platform team を central approval gate にする。
- 「横断チーム」を作りすぎて、ownership を分散させる。
- 組織変更で reporting line だけ変え、process/interface/authority を更新しない。
- 成果指標が部門別 local KPI だけで、顧客成果・価値流が見えない。

## Clone Implementation Guide

1. 主要 value stream と owned services/products を棚卸しする。
2. 各 value stream に stream-aligned owner/team を置く。
3. platform/enabling/complicated subsystem の切り出し条件を定義する。
4. team charter と interaction map を作り、authority matrix と接続する。
5. dependency、cognitive load、DORA/operations metrics を quarterly review に入れる。

## Confidence & Unknowns

- 確度 A/B: AWS の business-outcome alignment は直接的。Team Topologies は strong model だが標準ではないため B。
- 確度 B: DORA/GitLab/Toyota は culture/documentation/ownership の補助証拠。
- 不明点: 実際の headcount、capability、P&L、地域制約、labor law、報酬制度は公開情報だけでは決められない。

## Validation Queries

```text
site:docs.aws.amazon.com wellarchitected structure teams around desired business outcomes ownership
site:docs.aws.amazon.com operational excellence operating model team roles shared goals
site:teamtopologies.com stream-aligned platform enabling complicated subsystem cognitive load
site:handbook.gitlab.com DRI RACI team ownership handbook
site:dora.dev internal documentation sociotechnical systems delivery performance
```

---

# 12. Clone Spec: Layer 02.08 運用体制

## Definition

運用体制は、日次・週次・月次で業務/サービスを安定運営し、障害・例外・変更・顧客影響・改善を処理する役割、プロセス、会議体、runbook、SLO、incident response、postmortem、knowledge management、tooling を設計するレイヤーである。

## Decision Question

先端組織は、どの service/process をどの owner と operating cadence で運営し、どの SLO/error budget、runbook、incident/postmortem、observability、改善 backlog で継続改善するか。

## Frontier Exemplars

| Exemplar | 採用理由 | Source |
|---|---|---|
| AWS Operational Excellence | team organization, workload operation at scale, evolution over time の design principles。 | S10, S11 |
| Google SRE SLOs | SLO/error budget による reliability と velocity の tradeoff 管理。 | S18, S19 |
| Google SRE Postmortem | incident documentation, root cause, action items, review/publication, blameless culture。 | S17 |
| Toyota Production System | daily kaizen、異常検知/停止、JIT、lead time 短縮。 | S09 |
| NIST CSF 2.0 | Govern/Identify/Protect/Detect/Respond/Recover を concurrent/continuous に扱う。 | S01 |
| GitLab Handbook | 透明な運用情報、runbook/handbook 型の operational knowledge。 | S13, S16 |

## Evidence Map

| Claim | Evidence | Confidence |
|---|---|---|
| Operational excellence は team organization, workload operation at scale, evolution over time を含む。 | S10 | A/B |
| operating model は複数組織階層の中で team roles, interacting teams, shared goals を理解する必要がある。 | S11 | B |
| SLO は 100% ではなく error budget と tradeoff で管理する。 | S18, S19 | A/B |
| postmortem は incident, impact, mitigation/resolution, root cause, follow-up actions を記録し、review/publication する。 | S17 | A/B |
| CSF functions は concurrent/continuous に扱うべきで、Respond/Recover は常時 ready であるべき。 | S01 | A |

## Core Philosophy

運用体制は「保守担当」ではなく、**顧客価値、信頼性、コスト、速度、リスクを日々調整する operational control loop**である。よい運用体制は、平常時の観測、異常時の対応、事後の学習、改善の優先順位付けが一体化している。

## Decision Model

| Field | Spec |
|---|---|
| Inputs | service/process catalog、customer commitments、SLO/SLI、incident history、support tickets、monitoring, cost, capacity, staffing, risk register, change calendar |
| Criteria | customer impact、availability/reliability、response time、cost、toil、risk、compliance、learning value |
| Priorities | 1. safety/security/customer impact、2. service restoration、3. evidence and communication、4. root cause/action items、5. automation and prevention |
| Prohibitions | ownerなし service、runbookなし critical process、unreviewed postmortem、alert fatigue、manual toil hidden、SLOなし運用 |
| Exceptions | emergency operations は incident command / break-glass / post-review で処理。通常業務への恒久化は禁止。 |
| Approvers | Service Owner、Operations Lead、SRE/Platform、Product/Business Owner、Incident Commander、Risk/Compliance for major events |
| Review Cadence | daily/weekly ops review、monthly SLO/error budget review、quarterly operational excellence review、incident-driven postmortem。 |

## Operating Model

| Component | Design |
|---|---|
| Roles | Service Owner、Operations Lead、On-call、Incident Commander、SRE/Platform、Support Lead、Comms Lead、Postmortem Reviewer、Knowledge Owner |
| Process | operate → observe → detect → triage → respond → recover → postmortem → action items → backlog prioritization → process/policy update |
| Governance Forum | daily standup/ops huddle、weekly operations review、monthly SLO review、postmortem review、quarterly operational excellence review |
| Artifacts | Service catalog、runbook、SLO document、error budget policy、incident record、postmortem、on-call schedule、dashboard、action item backlog |
| Tools | monitoring/observability、ticketing、incident management、pager/on-call、knowledge base、automation/runbook tools、BI/dashboard |
| Audit Evidence | alerts、incident tickets、timeline、runbook execution logs、postmortem review、action item closure、SLO dashboard、change records |

## Technical / Business Specification

### Service / Operation Record Schema

| Field | Required | Notes |
|---|---|---|
| service_or_process_id | Yes | SVC-### / PROC-### |
| owner | Yes | accountable owner |
| customer / users | Yes | internal/external |
| criticality | Yes | tier 0/1/2/3 |
| SLI | Conditional | availability, latency, accuracy, throughput, freshness 等 |
| SLO | Conditional | target and window |
| error_budget_policy | Conditional | action thresholds |
| runbook | Yes for critical | detection/triage/recovery steps |
| on_call | Conditional | coverage model |
| escalation_path | Yes | incident, security, legal, executive |
| dependencies | Yes | systems, vendors, teams |
| dashboards | Yes | health and KPI |
| incident_classes | Yes | severity definitions |
| postmortem_trigger | Yes | SLO breach, severity, customer impact, near miss |
| knowledge_owner | Yes | runbook/doc maintenance |
| review_cadence | Yes | daily/weekly/monthly/quarterly |

### Incident / Postmortem Minimum Content

| Field | Required | Notes |
|---|---|---|
| incident_id | Yes | INC-YYYY-### |
| severity | Yes | customer/business impact |
| timeline | Yes | detection, escalation, mitigation, recovery |
| impact | Yes | users, revenue, compliance, SLO budget |
| root causes / contributing factors | Yes | system/process/people context, no blame |
| actions taken | Yes | mitigation/resolution |
| action items | Yes | owner, priority, due date |
| review status | Yes | reviewed/unreviewed/published |
| stakeholder communication | Conditional | customer/internal/executive |
| linked changes | Conditional | deployments/config/vendor |
| lessons learned | Yes | update to runbook/process/policy |

## Metrics

- SLO compliance
- Error budget burn rate
- Incident count by severity
- MTTD / MTTA / MTTR
- Customer impact minutes
- Runbook coverage and freshness
- Postmortem completion/review rate
- Action item closure SLA
- Toil percentage
- Automation coverage
- Alert precision / false positive rate
- Operational cost per service/process

## Failure Modes

| Failure | 兆候 | 防止策 |
|---|---|---|
| SLO なし運用 | 何が悪い状態か決まらない | SLI/SLO/error budget policy |
| Alert fatigue | 対応されない alert が増える | alert quality review, SLO-based alerting |
| Runbook stale | 障害時に手順が使えない | runbook review cadence, chaos/game days |
| Blameful incident review | 事実隠し、再発 | blameless postmortem, management reinforcement |
| Action item 未完了 | 同じ障害が再発 | owner/due date, monthly tracking |
| Toil hidden | 運用負荷が慢性化 | toil measurement, automation backlog |

## Anti-patterns

- 重大サービスに owner、SLO、runbook、escalation path がない。
- 障害後に postmortem を書くがレビューも公開も action item 追跡もない。
- SLO を 100% に設定し、現実的な tradeoff と error budget を設計しない。
- 運用改善が開発/事業計画に反映されない。
- manual toil を「頑張り」として評価し、自動化 backlog にしない。

## Clone Implementation Guide

1. critical service/process catalog を作り、owner/criticality/dependencies を付ける。
2. 上位 10 critical services/processes に SLI/SLO/runbook/escalation を設定する。
3. incident severity と postmortem trigger を定義する。
4. error budget / incident / support / cost / toil を monthly review に入れる。
5. postmortem action items を roadmap/backlog と接続し、方針・プロセス・権限へ反映する。

## Confidence & Unknowns

- 確度 A/B: Google SRE と AWS は運用設計の直接的・豊富な公開証拠。
- 確度 B: Toyota TPS は process/operations improvement の強い原理だが、SaaS/デジタル運用では SLO・observability へ翻訳が必要。
- 不明点: 実際の SLO 値、on-call 補償、顧客 SLA、ベンダー契約、規制報告義務は個社・業界で異なる。

## Validation Queries

```text
site:sre.google postmortem incident impact root cause action items review
site:sre.google implementing SLOs error budget policy stakeholder agreement dashboards
site:docs.aws.amazon.com wellarchitected operational excellence operating model
site:global.toyota Toyota Production System kaizen jidoka just-in-time lead time
site:nist.gov CSF 2.0 Respond Recover continuous ready incident operations
```

---

# 13. Layer Registry CSV-like Table

| layer_id | layer_name_ja | cluster | definition | decision_question | decision_object | default_source_types | input_signals | output_artifacts | owner_roles | default_metrics |
|---|---|---|---|---|---|---|---|---|---|---|
| 02.01 | 業務方針 | 業務設計・運営モデル | 事業目的・リスク・法規制・顧客約束を業務方針へ変換する | 何を入力に、どの方針体系を作り、誰が承認/改定し、どの統制/指標/例外で浸透を確認するか | policy/standard/procedure/guideline taxonomy | standard, official_doc, handbook, control framework | strategy, legal, risk, customer, incidents, audit findings | policy registry, control mapping, exception path | Policy Owner, Risk/Compliance, Legal, Process Owner | stale policy, control coverage, exception aging, audit findings |
| 02.02 | 業務プロセス | 業務設計・運営モデル | 価値提供 flow の入力・出力・責任・制御点・指標を設計する | どの value flow をどの process/control/exception/metrics で運営するか | process model / value stream | ISO, BPMN, TPS, operational excellence | customer request, SLA, handoff, defects, volume | process inventory, BPMN, RACI, dashboard | Process Owner, Control Owner, Automation Owner | cycle time, yield, defect, rework, exception rate |
| 02.03 | 業務ルール/例外 | 業務設計・運営モデル | 反復判断の条件・閾値・例外・補完統制を管理する | どの判断をルール化し、どの条件で例外を許可するか | rule/decision/exception | DMN, controls, SRE policy, approvals | policy, data, thresholds, exceptions, risks | rule catalog, decision table, exception register | Rule Owner, Risk Owner, Exception Owner | override rate, expired exceptions, false positives, rule conflicts |
| 02.04 | 承認 | 業務設計・運営モデル | 誰が何を承認し、どの条件で追加承認/省略/エスカレーションするかを決める | DRI に委譲する判断と追加承認が必要な判断をどう分けるか | approval matrix / decision memo | DRI docs, RMF, SRE, DORA | financial impact, risk, reversibility, cross-functional scope | approval matrix, decision memo, approval log | DRI, Approver, Risk Owner, Executive | approval lead time, bypasses, reversals, decision latency |
| 02.05 | 監査 | 業務設計・運営モデル | 統制の設計・実行・証跡・独立評価・改善を接続する | どの統制をどの証拠でどの頻度/独立性で評価し改善するか | audit/control/evidence system | COSO, NIST, SOC2, ISO19011, GitOps | policies, controls, logs, access, incidents, risk register | control matrix, evidence catalog, findings register | Audit Owner, Control Owner, Evidence Owner | findings, pass rate, remediation SLA, evidence freshness |
| 02.06 | 権限 | 業務設計・運営モデル | 役割・意思決定権限・アクセス権限・職務分掌・失効を設計する | 誰が何を決め、何にアクセスし、どうレビュー/失効するか | authority/access matrix | NIST, IAM docs, DRI/RACI, ISO27001 | roles, data class, systems, HR lifecycle, SoD rules | role catalog, permission matrix, access review | IAM Owner, Role Owner, System Owner, Data Owner | privileged accounts, SoD violations, deprovisioning MTTR |
| 02.07 | 組織設計 | 業務設計・運営モデル | 価値流・認知負荷・所有権・相互作用に基づきチーム境界を決める | どの team topology と ownership が business outcome を最大化するか | team topology / ownership map | AWS, Team Topologies, DORA, GitLab | value streams, architecture, dependencies, skills, cognitive load | team charter, ownership map, interaction map | Business Owner, Team Lead, Platform Owner | lead time, dependencies, ownership ambiguity, team health |
| 02.08 | 運用体制 | 業務設計・運営モデル | 日次運用・障害対応・SLO・改善・ナレッジを設計する | どの owner/cadence/SLO/runbook/postmortem で closed-loop operation を作るか | operating model / service operations | SRE, AWS OE, TPS, NIST CSF | service catalog, SLO, incidents, cost, support, risk | runbook, SLO doc, incident record, postmortem | Service Owner, Ops Lead, Incident Commander | SLO compliance, MTTR, incident severity, toil, action closure |

## 14. Pattern Library

| pattern_id | pattern_name | layer_scope | pattern_type | description | preconditions | tradeoffs | evidence_count | confidence |
|---|---|---|---|---|---|---|---:|---|
| P-001 | Policy-Control-Evidence Chain | 02.01,02.05,02.06 | control | 方針要求を control ID、evidence source、audit finding に接続する。 | policy registry, control catalog | 初期設計負荷が高い | 6 | A |
| P-002 | BPMN + DMN Separation | 02.02,02.03 | decision_rule | process flow と decision logic を分離し、プロセス変更とルール変更を独立させる。 | process map, decision ownership | モデリング教育が必要 | 3 | A |
| P-003 | DRI-first, Threshold Approval | 02.04,02.06,02.07 | operating_model | 通常判断は DRI に委譲し、閾値超過時だけ追加承認する。 | DRI/RACI, approval matrix | 誤った閾値だと承認不足/過多が起きる | 5 | B |
| P-004 | Exception-as-Risk-Acceptance | 02.03,02.04,02.05 | control | 例外を期限付き risk acceptance として登録し、補完統制と失効を必須にする。 | exception registry | 現場に負荷が出る | 5 | B |
| P-005 | Evidence-by-Design | 02.05,02.06,02.08 | control | 監査証跡を後付けせず、workflow/log/IAM/GitOps から自動取得する。 | workflow/logging integration | ツール統合が必要 | 5 | B |
| P-006 | Value Stream Team Ownership | 02.02,02.07,02.08 | operating_model | チームを value stream / business outcome に沿って設計し、end-to-end owner を置く。 | value stream map, service catalog | 既存職能組織との摩擦 | 4 | B |
| P-007 | SLO/Error-Budget Operating Loop | 02.04,02.08 | metric/control | SLO と error budget で信頼性・速度の tradeoff を制御する。 | measurable SLIs | SLO 選定が難しい | 3 | A/B |
| P-008 | Blameless Learning Loop | 02.05,02.08 | failure_pattern | incident 後に blame ではなく system/process 改善を行い、action item を追跡する。 | incident record, review culture | 責任追及文化と衝突 | 2 | B |
| P-009 | Role/Access/Decision Unified Authority | 02.04,02.06,02.07 | control | job role、decision rights、system permissions、SoD を同じ authority matrix に統合する。 | role catalog, IAM | 導入時の棚卸しが重い | 4 | B |
| P-010 | Continuous Improvement Cadence | 全レイヤー | maturity_pattern | 月次/四半期/年次で metrics、exceptions、findings、incidents を見て設計を更新する。 | metrics and owner | 会議体が増えやすい | 7 | A/B |

## 15. 90-Day Clone Implementation Roadmap

| Phase | Days | Objective | Key Deliverables |
|---|---:|---|---|
| Phase 0: Scope | 0–7 | 対象範囲と owner を確定 | layer registry、source/control mapping、top 10 risks、working group |
| Phase 1: Inventory | 8–21 | 方針・プロセス・ルール・承認・権限・監査・運用を棚卸し | policy registry、process inventory、rule/exception inventory、approval matrix draft、access role inventory、service catalog |
| Phase 2: Normalize | 22–45 | 主要 artifacts を標準 template に移行 | policy schema、process record、rule/exception schema、decision memo、control/evidence matrix、authority matrix、team charter、runbook/SLO doc |
| Phase 3: Pilot | 46–70 | 重要 value stream 1–2 個で end-to-end 試行 | BPMN/DMN、workflow evidence、access review、SLO/error budget、postmortem template、dashboard |
| Phase 4: Automate | 71–90 | 証跡・指標・レビュー会議を運用化 | automated evidence, exception alerts, approval SLA dashboard, access review workflow, operational review pack |

## 16. Target Operating Cadence

| Cadence | Meeting / Review | Participants | Inputs | Outputs |
|---|---|---|---|---|
| Daily | Ops huddle | Ops Lead, Service Owners | alerts, incidents, queues, SLO threats | immediate actions, escalations |
| Weekly | Process / service review | Process Owners, Team Leads | cycle time, exceptions, defects, incidents | improvement backlog, owner assignment |
| Monthly | Controls and exceptions review | Risk, Compliance, Control Owners | exceptions, audit evidence, access exceptions | remediation tickets, policy/process changes |
| Monthly | SLO/error budget review | Product, Engineering, SRE/Ops | SLI/SLO, budget burn, incidents | reliability/feature tradeoff decisions |
| Quarterly | Policy and approval matrix review | Policy Owners, Legal, Risk, Executives | policy age, approval lead time, findings | policy updates, threshold changes |
| Quarterly | Organization design review | Business/Tech leaders, HR/People | value stream metrics, dependencies, team health | team boundary / ownership changes |
| Annual | Audit and management review | Internal Audit, Execs, Control Owners | audit plan, findings, risk profile | audit plan, resource allocation, governance changes |

## 17. QA / Validation Checklist

| Check | Result | Notes |
|---|---|---|
| Coverage | Pass | 02 の全レイヤーを正規化し Clone Spec を作成。 |
| T0/T1/T2 coverage | Pass | NIST, ISO, OMG, COSO, AICPA を中核証拠に採用。 |
| Critical claims A/B | Pass | 主要 claim は標準/公式文書/公開運用資料で裏付け。 |
| Exceptions | Pass | 02.01/02.03/02.04/02.05/02.06/02.08 に exception path を明示。 |
| Failure evidence / anti-patterns | Partial Pass | 公開標準と DORA/SRE/GitLab から anti-pattern を抽出。個社内部失敗事例は限定的。 |
| Historical change | Pass | NIST CSF 2.0 final と CSF 1.1 to 2.0 transition material を source catalog に反映。 |
| Provenance | Pass | Source ID による evidence map を付与。 |
| Unknowns | Pass | 非公開 thresholds、内部権限 matrix、監査報告書などは unknowns に明示。 |

## 18. 反証・追加調査クエリ

```text
"DRI" approval failure incident governance
"heavyweight change approval" delivery performance DORA
"policy exception" "expired" "audit finding"
"access review" "orphan accounts" "audit finding"
"postmortem" "action items" "not completed" incident recurrence
site:nist.gov CSF 2.0 roles responsibilities authorities policy oversight
site:csrc.nist.gov SP 800-37 authorization continuous monitoring control assessment
site:csrc.nist.gov SP 800-53 access control audit accountability separation of duties
site:iso.org ISO 9001 process approach documented information performance evaluation
site:iso.org ISO 19011 audit program management system auditing
site:omg.org BPMN DMN business process decision rules
site:handbook.gitlab.com DRI required approvals IAM audit artifacts
site:sre.google error budget policy postmortem action items SLO approval
site:docs.aws.amazon.com wellarchitected operational excellence operating model team ownership
site:teamtopologies.com cognitive load interaction modes platform stream-aligned
```

## 19. Unknowns and Limitations

1. **企業内部の具体的閾値は非公開である。** 金額承認、法務承認、役員決裁、SOC 2 実査結果、アクセス権限 matrix は多くの場合公開されない。
2. **標準は outcome / control structure を示すが、実行方法は組織依存である。** NIST CSF は特定の達成方法を prescribe しないため、Clone Spec では実装 template として再構成した。
3. **業界規制の差分は未反映である。** 金融、医療、防衛、公共、製薬では承認・監査・権限に追加制約がある。
4. **文化・労務・地域制約は公開情報だけでは判定できない。** DRI、on-call、postmortem、透明 handbook の採用には労務・心理的安全性・法務レビューが必要。
5. **本成果物は public-evidence-based clone spec であり、個別企業の内部実態を断定しない。**

## 20. Recommended Next Artifacts

1. `policy_registry.csv`
2. `process_inventory.csv`
3. `rule_exception_register.csv`
4. `approval_matrix.csv`
5. `control_evidence_matrix.csv`
6. `authority_matrix.csv`
7. `team_topology_map.md`
8. `service_operations_catalog.csv`
9. `slo_error_budget_policy_template.md`
10. `postmortem_template.md`
