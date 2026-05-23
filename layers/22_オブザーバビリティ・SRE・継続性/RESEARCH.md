# Frontier Operating Model Research: オブザーバビリティ・SRE・継続性

対象レイヤー: 22  
対象サブテーマ: metrics / logs / traces、alerts / dashboards、SLI / SLO / SLA、error budget、incident、on-call、runbook、postmortem、capacity planning、performance tuning、availability design、redundancy、failover、DR、BCP  
生成日: 2026-05-13 JST  
調査制約: 公開情報のみ。公式標準、公式ドキュメント、OSS公式文書、公開ハンドブック、公開インシデント資料を優先。

---

## 0. このレイヤー束の正規化

このレイヤー束は、システムを「観測できる状態」にし、観測結果から信頼性判断を行い、障害時に被害を抑え、復旧し、学習し、事業継続に接続するための意思決定システムである。

**Decision Object:** 重要サービスについて、どのユーザー体験を、どのテレメトリー・SLI/SLO/SLA・アラート・運用体制・冗長化・復旧目標で守るか。

**Decision Question:** 先端組織は、サービスの信頼性をどのように測定し、どの条件で人間を呼び、どの体制でインシデントを処理し、どの失敗から学習し、どのRTO/RPO・冗長化・フェイルオーバー・BCPで継続性を保証するのか。

**本レポートでのレイヤー名の扱い:** ユーザー指定は `22` とサブテーマ列であり、個別レイヤー名は明示されていない。そのため、サブテーマを20個に分解し、22.01から22.20へ順番に割り当てた。正式な既存レイヤー台帳がある場合は、名称だけ差し替え可能な形にしている。

---

## 1. Executive Summary

この領域の frontier pattern は **「ユーザー体験を中心にした信頼性制御ループ」** である。先端組織は、CPU使用率やサーバー死活のような内部状態だけで運用判断をしない。まず critical user journey と顧客影響を定義し、その体験を SLIs と SLOs に落とし、SLO 違反リスクや error budget burn をアラート条件にし、オンコール・インシデント・ポストモーテム・容量計画・性能改善・可用性設計・DR/BCPへ接続する。

OpenTelemetry は、signals を「OSやアプリケーションの活動を説明する system outputs」として扱い、traces / metrics / logs / baggage をサポートし、collect / process / export の標準化レイヤーを提供する。CNCF TAG Observability は、metrics / logs / traces を単なる三本柱ではなく primary signals と捉え、目的に応じた signal 選択、コスト、cardinality、相関を設計対象にする。Google SRE は、SLI/SLO/SLA、four golden signals、error budget、SLOベースのアラート、オンコール負荷、blameless postmortem を実務モデルとして公開している。Prometheus / Alertmanager / Grafana は、alert rule、deduplication、grouping、routing、dashboard as code を実装可能な公開成果物にしている。AWS / Azure / Google Cloud の Well-Architected Reliability 系文書は、冗長化、自動復旧、復旧手順テスト、DR、RTO/RPO、マルチゾーン/マルチリージョン設計を、NIST SP 800-34 と ISO 22301 は、contingency planning と business continuity management system を標準・公的文書として提供する。[^otel-signals][^cncf-whitepaper][^sre-slo][^sre-golden][^sre-error-budget][^prom-alertmanager][^grafana-oac][^aws-rel-principles][^azure-dr][^nist-800-34][^iso-22301]

### 1.1 中核結論

| 結論 | 実装上の意味 | 確度 |
|---|---|---|
| 信頼性は「内部稼働率」ではなく「ユーザーが期待する振る舞い」で測る。 | SLIは user journey から定義し、infra metric は診断・容量・性能補助に分離する。 | A |
| Alert は monitoring output ではなく、interrupt budget の消費である。 | paging alert は緊急・行動可能・ユーザー影響あり・SLO/error budget に接続されたものに制限する。 | A |
| Metrics / logs / traces は役割が異なり、相関できて初めて運用価値が上がる。 | trace_id/span_id、resource metadata、service/version/env、deployment/event annotations を共通化する。 | A |
| Error budget は信頼性と開発速度の意思決定装置である。 | budget burn に応じて release freeze、risk review、ticket/page、capacity/perf投資を発動する。 | A |
| On-call は英雄的対応ではなく、持続可能性を設計する制度である。 | 5分/30分級の応答目標、primary/secondary、25% on-call rule、2 incidents / 12h shift などを参考に workload を制御する。 | A |
| Incident management は技術調査だけでなく、役割・通信・意思決定・記録のプロトコルである。 | Incident Lead / Responder / Communications Lead / escalation / timeline / status page を事前定義する。 | A/B |
| Postmortem は責任追及ではなく、再発可能性と影響を下げる学習機構である。 | 発生前に trigger criteria を決め、owner、root cause、impact、timeline、action item、reviewを必須化する。 | A |
| DR/BCP は backup の有無ではなく、RTO/RPOと事業影響に対してテスト済みであることが本体である。 | BIA、RTO/RPO、recovery strategy、failover drill、restore test、supplier/comms/people plan を結合する。 | A |

### 1.2 この領域でやってはいけないこと

- 「すべてを収集する」ことを observability と誤解する。コスト、cardinality、PII、保持期間、相関不能性が制御不能になる。
- CPU、memory、disk だけでページングする。顧客影響とSLOに結びつかない alert は疲弊を生む。
- SLO を全サービス一律の nines にする。criticality、ユーザー期待、コスト、事業価値が反映されない。
- SLA を SLO より厳しく設定する。外部契約違反リスクを内部制御できない。
- on-call を少人数・無補償・無訓練・runbookなしで回す。burnout と MTTR 悪化を招く。
- postmortem を「担当者のミス」文書にする。情報隠蔽と再発を生む。
- multi-region を作っただけで DR と見なす。データ整合性、切替権限、DNS/traffic、復旧順序、演習がなければ復旧能力ではない。
- BCP を IT のみで閉じる。人員、サプライヤー、法務、顧客通信、オフィス、資金決済、手作業代替が抜ける。

---

## 2. Frontier Exemplars / Candidate Scoring

スコアは RESEARCH.md の `Performance / Adoption / Artifact Richness / Peer Validation / Recency / Transferability / Failure Evidence` に対応する簡易100点換算である。評価対象は有名度ではなく、公開証拠の厚みと再現性である。

| Candidate | 主対象 | 採用理由 | Score | Evidence Tier |
|---|---:|---|---:|---|
| Google SRE Book / SRE Workbook | 22.06–22.14 | SLI/SLO/SLA、error budget、alerting on SLOs、four golden signals、on-call、postmortem、overload handlingを体系化し、運用判断に直結する閾値・例外・失敗条件を公開している。 | 96 | T0/T3 |
| OpenTelemetry + CNCF TAG Observability | 22.01–22.03 | traces/metrics/logs の標準化、context propagation、collector、resource metadata、multi-signal correlation を提供し、ベンダーロックインを下げる実装面が豊富。 | 94 | T0/T2/T3 |
| Prometheus / Alertmanager / Grafana | 22.04–22.05 | alerting rules、deduplication/grouping/routing、dashboard、observability as code が公開仕様・OSS文書として実装可能。 | 92 | T2/T3 |
| AWS Well-Architected Reliability | 22.14–22.19 | 自動復旧、復旧手順テスト、capacity guess停止、DR planning、RTO/RPO、failure managementを公式設計原則として公開している。 | 91 | T0/T3 |
| Azure Well-Architected Reliability | 22.16–22.19 | redundancy、failover、DR procedure automation、idempotent scripts、RTO alignment を明示し、クラウド実装パターンに近い。 | 89 | T0/T3 |
| Google Cloud Architecture Framework Reliability | 22.14–22.19 | reliability pillar、global load balancing、built-in redundancy、region/zone設計などを current docs として公開している。 | 88 | T0/T3 |
| NIST SP 800-34 Rev.1 | 22.19–22.20 | contingency planning、DR plan、BIA template、organizational resiliency、system lifecycle との関係を公的ガイドとして提供。 | 88 | T0 |
| ISO 22301:2019 | 22.20 | BCMS の国際標準。リスク特定、緊急時準備、体系的危機対応、recovery time 改善を目的にする。 | 86 | T0 |
| GitLab public handbook / runbooks | 22.10–22.13 | EOC/IMOC、incident roles、on-call schedules、runbook、status definitions、incident metrics を公開し、運用モデルとして再利用しやすい。 | 85 | T3/T5 |
| PagerDuty Incident Response Documentation | 22.10–22.13 | on-call practitioner 向けの preparation / during / after incident、SEV-1/2 postmortem、owner designation を公開。 | 83 | T3/T5 |

---

## 3. Source Catalog

| Source ID | Entity | Source | Source Type | Tier | 主な抽出対象 |
|---|---|---|---|---|---|
| SRC-OTEL-SIGNALS | OpenTelemetry | Signals / Metrics / Logs / Traces / Context propagation | official_doc / spec | T0/T2 | signals、runtime measurement、log event、span、context propagation、signal correlation |
| SRC-CNCF-OBS | CNCF TAG Observability | Observability Whitepaper / TAG site | official_doc / community-governed | T0/T3 | primary signals、purpose-bound observability、cost/cardinality、correlation、alert fatigue |
| SRC-GOOGLE-SRE | Google SRE | SRE Book / Workbook | official_doc | T0/T3 | SLI/SLO/SLA、golden signals、error budget、on-call、postmortem、alerting on SLOs、overload |
| SRC-PROM | Prometheus | Alerting rules / Alertmanager | official_doc / OSS | T2/T3 | alert conditions、PromQL、for、grouping、dedup、routing、silence、inhibition |
| SRC-GRAFANA | Grafana | Dashboards / Observability as Code | official_doc / OSS | T2/T3 | dashboard panels、versioned observability config、CI/CD、dashboard as code |
| SRC-AWS-REL | AWS | Well-Architected Reliability Pillar / DR | official_doc | T0/T3 | automatic recovery、KPIs、test recovery、RTO/RPO、DR strategy |
| SRC-AZURE-REL | Microsoft Azure | Well-Architected Reliability / Redundancy / DR | official_doc | T0/T3 | redundancy layers、failover automation、RTO targets、idempotent scripts |
| SRC-GCP-REL | Google Cloud | Architecture Framework Reliability / Scalable resilient apps | official_doc | T0/T3 | reliability principles、region/zone、global load balancing、built-in redundancy |
| SRC-NIST-80034 | NIST | SP 800-34 Rev.1 | standard / regulator-adjacent | T0 | contingency planning、DR plan、BIA、resilience、lifecycle |
| SRC-ISO-22301 | ISO | ISO 22301:2019 | standard | T0 | business continuity management system、resilience、systematic crisis response |
| SRC-GITLAB-IM | GitLab | Incident Management Handbook / Runbooks | official_doc | T3/T5 | EOC/IMOC、incident roles、status definitions、runbooks、escalation |
| SRC-PD-IR | PagerDuty | Incident Response Documentation / Postmortem Process | official_doc | T3/T5 | on-call準備、incident lifecycle、SEV postmortem、owner assignment |

---

## 4. Evidence Map

| Claim ID | Claim | Decision Field | Evidence | Confidence |
|---|---|---|---|---|
| C-001 | OpenTelemetry は signals の収集・処理・export を目的にし、traces / metrics / logs / baggage をサポートする。 | interface rules / artifacts | SRC-OTEL-SIGNALS | A |
| C-002 | Metrics は runtime に取得される service measurement であり、availability/performance indicator、alerting、autoscaling decision に使える。 | metrics / thresholds | SRC-OTEL-SIGNALS | A |
| C-003 | Logs は timestamped event record であり、structured schema、metadata、trace correlation がないと分析性が下がる。 | artifacts / controls | SRC-OTEL-SIGNALS | A |
| C-004 | Traces は request path と span から構成され、context propagation によって分散システム横断の因果関係を作る。 | interface rules / diagnosis | SRC-OTEL-SIGNALS | A |
| C-005 | SLI は service level の定量指標、SLO は SLI に対する target、SLA は外部合意として分離して扱うべきである。 | decision model / rules | SRC-GOOGLE-SRE | A |
| C-006 | Golden signals は latency, traffic, errors, saturation であり、user-facing system の最小監視セットになる。 | metrics / minimum viable instrumentation | SRC-GOOGLE-SRE | A |
| C-007 | Error budget は `1 - SLO` として扱われ、信頼性と変更速度の意思決定に使われる。 | thresholds / governance | SRC-GOOGLE-SRE | A |
| C-008 | SLO alert は precision, recall, detection time, reset time を評価軸にし、burn rate / multiple windows が有効な設計パターンである。 | alert rule / escalation | SRC-GOOGLE-SRE | A |
| C-009 | Alertmanager は alert の deduplication, grouping, routing, silencing, inhibition を担う。 | alert routing / noise control | SRC-PROM | A |
| C-010 | Dashboard は関連情報を panels で一望可能にする view であり、Observability as Code によって versioning / CI/CD / reliable deployment 対象にできる。 | artifacts / governance | SRC-GRAFANA | A |
| C-011 | Google SRE は on-call を持続可能にするため、25% on-call rule、primary/secondary、応答目標、alert noise control を示す。 | ownership / staffing | SRC-GOOGLE-SRE | A |
| C-012 | Incident response は on-call practitioner が事前準備・発生中・事後対応を実行する formal process として文書化できる。 | operating model | SRC-PD-IR / SRC-GITLAB-IM | B |
| C-013 | Blameless postmortem は incident record、impact、actions、root cause、follow-up actions を含み、個人非難ではなく再発防止を目的にする。 | learning loop / controls | SRC-GOOGLE-SRE / SRC-PD-IR | A |
| C-014 | AWS Reliability は business-value KPIs を監視し、threshold breach に対して automation を実行して回復する設計原則を示す。 | automated remediation | SRC-AWS-REL | A |
| C-015 | DR は backup/redundant components だけでは足りず、RTO/RPOを business needs から設定し、strategyを実装する必要がある。 | DR thresholds / strategy | SRC-AWS-REL / SRC-AZURE-REL | A |
| C-016 | Azure は failover environment の deployment / recovery procedure を自動化し、RTO targets に合わせることを推奨する。 | failover / DR controls | SRC-AZURE-REL | A |
| C-017 | NIST SP 800-34 は情報システム contingency planning の目的・プロセス・形式、DR plan / BIA template を提供する。 | BCP / DR artifacts | SRC-NIST-80034 | A |
| C-018 | ISO 22301 は事業継続のための BCMS 標準であり、リスク特定、緊急時準備、体系的危機対応、recovery time 改善に効く。 | BCP governance | SRC-ISO-22301 | A |

---

## 5. Layer Registry: 22

| Layer ID | Layer Name | Definition | Decision Object | Primary Artifacts | Owner Roles | Default Metrics |
|---:|---|---|---|---|---|---|
| 22.01 | Metrics | runtime measurement を設計・収集・集約・保持・利用する層。 | どの数値をどの粒度・ラベル・保持期間・集約で測るか。 | metric taxonomy, semantic conventions, recording rules, cardinality policy | SRE, service owner, platform observability | latency, traffic, errors, saturation, cardinality, ingest cost |
| 22.02 | Logs | event record を構造化し、検索・監査・診断に使える形で保持する層。 | 何を event として記録し、どの schema / severity / PII control / retention で扱うか。 | log schema, severity policy, PII redaction, retention policy | service owner, security, observability platform | parse error rate, log volume, high-severity events, audit coverage |
| 22.03 | Traces | request / transaction の因果経路を span と context で追跡する層。 | どの境界を span 化し、どの sampling / propagation / baggage で相関するか。 | trace instrumentation spec, propagation policy, sampling policy | service owner, SRE, platform observability | trace coverage, sampled rate, p95/p99 span latency, missing parent rate |
| 22.04 | Alerts | 介入すべき状態を rule 化し、通知・抑制・ルーティングする層。 | どの条件で page / ticket / automation を起動するか。 | alert rules, routing tree, severity matrix, silence policy | SRE, on-call owner, service owner | precision, recall, false positive rate, page count, alert:incident ratio |
| 22.05 | Dashboards | 状況把握・調査・意思決定のための visual view を管理する層。 | 誰がどの判断をするために、どの view を持つか。 | SLO dashboard, incident dashboard, capacity dashboard, dashboard-as-code | SRE, service owner, product owner | dashboard coverage, stale dashboard count, time-to-diagnosis |
| 22.06 | SLI | service level を定量化する指標を設計する層。 | どの user journey を good event / bad event で測るか。 | SLI definitions, event taxonomy, measurement query | product owner, SRE, service owner | good/total event ratio, latency threshold pass rate, freshness |
| 22.07 | SLO | SLI に対する internal target と measurement window を設定する層。 | どの reliability target を、どの期間・例外・レビュー周期で守るか。 | SLO document, SLO query, review minutes | product owner, SRE lead, engineering manager | SLO attainment, burn rate, breach count |
| 22.08 | SLA | 顧客・外部主体との合意品質と補償条件を定義する層。 | どの service level を契約し、違反時にどう対応するか。 | SLA terms, support policy, credit policy, status report | legal, product, sales, SRE | SLA breach count, credits issued, customer impact minutes |
| 22.09 | Error Budget | SLO未達許容量を開発速度・変更制御に接続する層。 | budget burn に応じて release / risk / capacity / incident actions をどう変えるか。 | error budget policy, burn-rate alerts, release freeze rule | product owner, SRE, engineering manager | remaining budget, burn rate, freeze days, risky launches |
| 22.10 | Incident | 異常を宣言し、役割・通信・意思決定・復旧を統制する層。 | どの状態を incident とし、誰が何を決めるか。 | incident state doc, severity matrix, timeline, comms plan | Incident Lead, Responder, Comms Lead, SRE | MTTD, MTTA, MTTR/MTTM, impact duration |
| 22.11 | On-call | 人間の即応体制・負荷・エスカレーションを設計する層。 | どのサービスに誰が何分以内に応答し、どう持続可能に回すか。 | rotation, escalation policy, handover, training checklist | SRE manager, on-call owner, team leads | pages/shift, incidents/shift, sleep interruptions, handover quality |
| 22.12 | Runbook | 既知の症状に対する診断・緩和・復旧手順を管理する層。 | どの症状に、どの手順・安全条件・rollback・escalation を用意するか。 | runbook, automation script, safety checklist | service owner, SRE, platform team | runbook coverage, success rate, stale runbooks, mean execution time |
| 22.13 | Postmortem | 重大事象から再発防止・改善を抽出する層。 | どの事象をレビューし、どの action item を誰がいつ完了するか。 | postmortem doc, action item tracker, review notes | incident lead, postmortem owner, SRE, management | action item completion, repeat incident rate, review latency |
| 22.14 | Capacity Planning | 需要・資源・成長・余力を予測し、過負荷を防ぐ層。 | どの capacity をいつ、どの余裕率・承認・コストで確保するか。 | demand forecast, capacity model, load test, autoscaling plan | SRE, platform, finance, product | headroom, saturation, forecast error, scale latency |
| 22.15 | Performance Tuning | latency/throughput/resource効率を改善する層。 | どの bottleneck を、どの性能予算・計測・実験で改善するか。 | performance budget, profiling report, optimization backlog | service owner, SRE, performance engineer | p95/p99 latency, throughput, CPU/memory per request, regression count |
| 22.16 | Availability Design | 期待稼働率に対するアーキテクチャと運用制約を設計する層。 | どの failure を許容し、どの design pattern でユーザー影響を抑えるか。 | availability target, dependency map, fault model, resilience review | architect, SRE, product owner | availability, customer impact minutes, dependency SLO coverage |
| 22.17 | Redundancy | 冗長化の範囲・層・整合性・コストを決める層。 | 何を複製し、どこまで active/passive/active-active にするか。 | redundancy matrix, replica policy, quorum/consistency design | architect, platform, data owner | single point of failure count, replication lag, redundancy coverage |
| 22.18 | Failover | 障害時に alternative path へ切り替える手順・自動化を設計する層。 | 何を trigger に、誰/何が、どの順序で切り替え、どう戻すか。 | failover runbook, traffic switch plan, game day result | SRE, platform, incident lead | failover success rate, failover time, rollback time, split-brain events |
| 22.19 | Disaster Recovery | 大規模障害・サイト喪失・データ損失に対する復旧戦略を設計する層。 | RTO/RPOに応じて backup-restore / pilot-light / warm-standby / active-active を選ぶか。 | DR plan, backup policy, restore test, regional recovery topology | DR owner, SRE, data/platform owner | RTO actual, RPO actual, restore success, exercise pass rate |
| 22.20 | BCP | 事業機能継続のため、人・プロセス・技術・サプライヤー・通信を統合する層。 | どの business function を、どの MTD / RTO / alternate process で継続するか。 | BIA, BC plan, crisis comms plan, supplier plan, exercise report | business owner, risk, legal, IT/SRE, exec sponsor | BIA coverage, exercise cadence, recovery capability, supplier readiness |

---

## 6. Core Philosophy

1. **User-visible reliability first.** 監視対象はサーバーではなく、ユーザーが期待する成果である。infra metric は診断、容量、性能、予兆のために必要だが、paging と SLO は user journey に接続する。

2. **Telemetry is a contract.** Metrics / logs / traces は単なる副産物ではなく、サービスが自分の状態を外部へ表明する契約である。service.name、version、environment、region、tenant、trace_id、span_id、deployment_id などの metadata は設計対象である。

3. **Alerting is an interrupt economy.** Alert は情報ではなく人間の集中力を奪う割り込みである。重大で、行動可能で、SLO/error budgetに接続し、重複排除・抑制・ルーティングされた alert だけが page になる。

4. **Error budgets convert reliability into governance.** SLO と error budget は、信頼性と feature velocity の緊張を感情論から制度へ変える。budget が健全なら変更を進め、不健全なら信頼性投資へ切り替える。

5. **Incidents require command, not chaos.** Incident 中は、技術調査、意思決定、顧客通信、記録、エスカレーションを分離する。役割分担は平時に決め、incident 中に発明しない。

6. **Learning is an operational control.** Postmortem は文化施策ではなく、再発確率と影響を下げる operational control である。action item が owner / due date / priority / verification を持たなければ学習にならない。

7. **Continuity is tested capability.** DR/BCP は文書ではなく、演習で確認された復旧能力である。RTO/RPO、BIA、復旧順序、権限、通信、代替業務、supplier dependency をテストしない計画は仮説にすぎない。

---

## 7. Decision Model

### Inputs

- Critical user journeys, customer segments, contractual commitments, revenue / safety / compliance impact
- Service catalog, dependency graph, data classification, topology, region/zone layout, third-party dependencies
- Telemetry signals: metrics, logs, traces, profiles, events, status page, customer reports
- Historical incidents, postmortem action items, alert noise, on-call load, support tickets
- Demand forecast, launch calendar, seasonal traffic, capacity utilization, performance trends
- Business impact analysis, maximum tolerable downtime, RTO/RPO, supplier risk, legal/comms constraints

### Criteria

| Criteria | 判断基準 |
|---|---|
| User impact | ユーザー体験・契約・安全・収益への影響があるか |
| Actionability | alert / dashboard / runbook が具体的行動につながるか |
| Precision vs recall | significant event を取り逃さず、noise を増やさないか |
| Cost and cardinality | 収集・保持・クエリ・高cardinalityが許容範囲か |
| Recovery feasibility | RTO/RPO を手順・人員・自動化・権限で満たせるか |
| Sustainability | on-call と incident load が burnout を生まないか |
| Governance | SLA、規制、顧客通信、BCP、監査証跡に接続できるか |

### Priorities

1. まず user journey と SLO を定義する。
2. SLO を測れる minimal telemetry を整備する。
3. Page は SLO / error budget / major incident に接続する。
4. Dashboard は意思決定単位で設計し、owner と更新責任を持たせる。
5. Incident process は severity、roles、communication、timeline を固定する。
6. Runbook と automation は安全条件・rollback・escalation を明記する。
7. Capacity / performance / availability は SLO risk と cost risk の両方で優先順位を決める。
8. DR / BCP は business impact から RTO/RPO を決め、演習で実測する。

### Prohibitions

- SLOなしで SLA を販売する。
- good event / bad event の定義がないまま error budget を運用する。
- action 不能な alert を page にする。
- dashboard を作成者個人の便宜で増やし、owner と削除基準を持たない。
- high-cardinality label に user_id / request_id / unbounded URL / raw query を入れる。
- log に secret / token / PII を未処理で出す。
- postmortem に個人名の責任追及を書く。
- failover / restore を本番相当で一度もテストせずに DR 完了とする。

### Owners

| Role | 主責任 |
|---|---|
| Product Owner | user journey、SLO/SLAの事業判断、顧客影響基準 |
| Service Owner | instrumentation、runbook、capacity、performance、postmortem action item |
| SRE Lead | SLO/error budget、alert quality、on-call、incident process、reliability review |
| Platform Observability Owner | telemetry platform、schema、retention、cost、tooling、dashboard as code |
| Incident Lead / IMOC | incident command、timeline、decision、escalation、coordination |
| Incident Responder / EOC | technical diagnosis、mitigation、restore、runbook execution |
| Communications Lead | status page、customer/internal comms、support alignment |
| DR/BCP Owner | BIA、RTO/RPO、DR/BCP exercise、supplier/people/process continuity |
| Legal / Security / Risk | SLA terms、privacy/log controls、compliance、crisis obligations |

### Review Cadence

| 対象 | 頻度 | Trigger |
|---|---:|---|
| SLI/SLO definition | 四半期 | 新サービス、主要導線変更、顧客契約変更、重大incident |
| Alert rules | 月次 + incident後 | false positive、missed incident、page storm、burnout |
| Dashboard catalog | 四半期 | stale panels、owner不明、service change |
| On-call health | 月次 | pages/shift増加、handover問題、退職/休暇/チーム変更 |
| Runbook | incident後 + 四半期 | runbook失敗、依存変更、自動化追加 |
| Postmortem action items | 週次/隔週 | due date超過、repeat incident |
| Capacity forecast | 月次/launch前 | growth, seasonality, major launch, cost anomaly |
| DR exercise | 半期/年次 + major topology change | region追加、data tier変更、RTO/RPO変更 |
| BCP exercise | 年次 + major business/process change | critical function変更、supplier変更、規制変更 |

---

## 8. Technical / Business Specification

### 8.1 Telemetry Architecture

**Minimum viable design:**

- 全サービスに `service.name`, `service.version`, `deployment.environment`, `region/zone`, `team`, `tier`, `customer_impact_class` を付与する。
- OpenTelemetry SDK / Collector / OTLP または互換 pipeline を使い、metrics / logs / traces を可能な限り同じ resource metadata で出す。
- request path には W3C Trace Context 互換の propagation を使い、trace_id / span_id を logs にも付与する。
- Metrics は SLO用と診断用を分ける。SLO用は good/total event, latency threshold pass, availability, freshness などに限定する。
- Logs は structured を原則にし、severity、event_type、operation、resource、tenant class、error code、trace_id、redaction status を持つ。
- Traces は critical path、cross-service boundary、external dependency、queue, DB, cache, RPC, async workflow を span 化する。
- Cardinality policy を設ける。user_id、session_id、raw URL、unbounded label は metrics label に入れず、trace/log属性で扱う。
- Retention は用途で分ける。SLO metrics は長期、high-resolution metrics は短期、logs/traces はsampling/retention/cost tierを分ける。

### 8.2 Alerting and Notification

**Paging alert の要件:**

1. 影響が現在進行中、または短時間で error budget を大きく消費する。
2. 人間が即時に取るべき action がある。
3. Runbook または escalation path がある。
4. 重複・storm を防ぐ grouping / inhibition / silence がある。
5. Alert message に service、symptom、impact、SLO/burn、dashboard、runbook、recent deploy、owner、escalation が入る。

**Recommended severity mapping:**

| Severity | Condition | Notification | Expected Action |
|---|---|---|---|
| SEV-1 | 広範な顧客影響、SLO急速消費、SLA違反、data loss、security/public incident | Page + Incident Lead + Comms + Leadership | 即時mitigation、status update、executive awareness |
| SEV-2 | 重要機能の部分停止、error budget大幅消費、回避策限定 | Page | Incident declaration、mitigation、customer comms判断 |
| SEV-3 | 影響限定、budget消費が数日単位、workaroundあり | Ticket + business-hours | 計画対応、postmortem optional |
| SEV-4 | 内部品質低下、予兆、no customer impact | Ticket / backlog | backlogまたはmaintenance |

**Burn-rate based pattern:**

- 1h / 5m または 6h / 30m などの multi-window, multi-burn-rate を採用し、短期急変と長期劣化を分ける。
- Page は「数時間で error budget を消費し得る」状態に絞る。
- Ticket は「数日単位で budget を削る」状態に使う。
- Low-traffic services は短期 window が不安定なので synthetic probe、request aggregation、longer windows、manual review を追加する。

### 8.3 Dashboards

Dashboard は「見るため」ではなく「判断するため」に作る。最低限のセットは次の通り。

| Dashboard | 用途 | 必須パネル |
|---|---|---|
| Executive reliability | 経営・プロダクト判断 | SLO attainment, SLA breach, customer impact minutes, incident trend, budget remaining |
| Service SLO | サービスowner/SRE | good/total events, burn rate, latency, error ratio, dependency health, recent deploys |
| Incident commander | Incident中の command | current impact, severity, timeline, affected regions, mitigations, owner, comms status |
| Diagnostics | 技術調査 | golden signals, logs by error code, trace exemplars, dependency latency, saturation |
| Capacity | 需要・余力判断 | QPS, resource headroom, queue depth, autoscaling latency, forecast vs actual |
| DR/BCP | 継続性 | RTO/RPO actual, backup/restore status, replica lag, failover readiness, exercise results |

Dashboard は Git 管理し、owner、purpose、last reviewed、data source、runbook links、deprecation criteria を持つ。Grafana の Observability as Code の考え方と同様、dashboard / datasource / config を code として versioning、testing、CI/CD の対象にする。[^grafana-oac]

### 8.4 SLI / SLO / SLA

**SLI design checklist:**

- User journey から good event / bad event を決める。
- 分母は total eligible events。分子は acceptable events。
- Threshold は user happiness を反映し、平均ではなく percentile / ratio / freshness を重視する。
- Client-side と server-side の差を明示する。可能なら client-side synthetic / RUM を併用する。
- Batch / data pipeline は availability ではなく correctness / freshness / durability / completeness を使う。
- External dependency の障害を SLIに含めるか、separate dependency SLI として扱うかを明記する。

**SLO document minimum fields:**

```yaml
service: checkout-api
owner_team: commerce-platform
critical_user_journey: "user completes checkout"
measurement_window: 28d
sli:
  name: checkout_success_latency
  good_event: "HTTP 2xx or accepted payment callback within 2s"
  total_event: "valid checkout requests excluding documented maintenance window"
  source: "server metrics + synthetic probes"
slo:
  target: "99.9%"
  window: "28d rolling"
error_budget:
  allowed_bad_events: "0.1% of eligible events"
  policy: "freeze risky launches when burn > 50%; reliability review when burn > 25% in 7d"
alerts:
  page: "multi-window multi-burn-rate"
  ticket: "slow burn or non-urgent budget erosion"
exceptions:
  - "declared maintenance windows approved by product and customer comms"
  - "force majeure covered by SLA terms only if contractually excluded"
review_cadence: quarterly
```

**SLA design rules:**

- SLA は外部契約なので、内部 SLO より緩くする。
- SLA credit は legal / finance / support / product と合意する。
- SLA exception と status page / incident report / customer notice の整合を取る。
- SLAの対象範囲、measurement source、maintenance window、excluded events、claim process を明記する。

### 8.5 Incident Management

**Incident lifecycle:**

1. Detect: SLO alert, customer report, synthetic probe, support escalation, security/third-party signal。
2. Triage: severity, impacted service, current user impact, known recent changes, owner確認。
3. Declare: incident channel/doc、Incident Lead、Responder、Comms Lead、severity を設定。
4. Stabilize: rollback, traffic shift, disable feature, rate limit, degrade response, dependency bypass。
5. Communicate: status page、support/customer comms、internal stakeholders、executive update。
6. Resolve: impact終了確認、SLO/budget status、customer comms、monitoring継続。
7. Learn: postmortem、follow-up issue、action item、alert/runbook/dashboard更新。

**Incident state document fields:**

```markdown
Incident ID:
Severity:
Status:
Start time / detection time / declaration time / mitigation time / resolution time:
Incident Lead:
Responder(s):
Communications Lead:
Affected services / regions / customers:
Current hypothesis:
Customer impact:
Mitigations attempted:
Next decision deadline:
Timeline:
Links: dashboards, traces, logs, runbooks, deploys, status page
Follow-up owner:
```

### 8.6 On-call

**Sustainable on-call rules:**

- Primary/secondary と fall-through を設計する。
- 重要 user-facing service は minutes-level response、低重要度は business-hours/ticket に分ける。
- on-call 負荷は量と質で管理する。Google SRE の公開モデルでは、SRE時間の50%以上をengineering workに使い、on-callは25%以内に抑える考え方、また12時間シフトあたり2 incidentsを上限目安にする考え方が示されている。[^sre-oncall]
- Alert は 1 incident : 1 page に近づける。fan-out、重複、unactionable alert を削減する。
- Handover は active incidents、risky changes、maintenance、disabled alerts、known degradations を含む。
- Training は shadowing、game day、Wheel of Misfortune、runbook drill を含む。

### 8.7 Runbook

Runbook は「既知の問題に対する安全な操作手順」である。最低限、次を持つ。

```markdown
Runbook title:
Applies to:
Symptoms / alert names:
Severity guidance:
Pre-checks:
Safety constraints:
Diagnostic commands / queries:
Decision tree:
Mitigation steps:
Rollback steps:
Escalation path:
Expected time:
Verification:
Customer communication notes:
Post-action cleanup:
Last reviewed:
Owner:
```

Runbook は automation scripts と接続してよいが、危険操作は manual approval、dry-run、blast radius、rollback、audit log を必須にする。

### 8.8 Postmortem

Postmortem trigger は事前定義する。典型 trigger は、ユーザー可視の停止・劣化、data loss、on-call intervention、rollback/reroute、長い解決時間、monitoring failure、SLA breach、重大な near miss。Google SRE は postmortem を incident、impact、actions、root cause、follow-up actions を記録する learning opportunity として扱い、blameless を明示している。PagerDuty も major incident に対して blame-free な postmortem と owner assignment を公開している。[^sre-postmortem][^pd-postmortem]

**Postmortem fields:**

- Summary / impact / timeline / detection / escalation / mitigation / resolution
- Root cause(s) and contributing factors
- What went well / what went poorly / where we got lucky
- Customer and business impact
- Alerting and observability gaps
- Runbook / automation / architecture gaps
- Action items with owner, due date, priority, verification method
- Review result and management acceptance

### 8.9 Capacity Planning / Performance Tuning

Capacity planning は、需要、資源、software efficiency の関数として扱う。Google SRE は resource use を demand/load, capacity, software efficiency と結びつけ、SREが需要予測、容量確保、ソフトウェア修正に関与する点を示している。[^sre-intro]

**Capacity model inputs:**

- Historical traffic, seasonality, product launch, growth forecast
- Resource utilization by request class, saturation signal, queue depth
- Autoscaling lag, cold start, regional limits, quota, provider limits
- Cost per request / cost per tenant / cost per good event
- Incident history from overload / throttling / degraded dependency

**Performance tuning flow:**

1. SLO risk or cost risk から性能課題を選ぶ。
2. Profiling / tracing / metrics / logs で bottleneck を特定する。
3. Performance budget を定義する。例: p95 300ms、p99 1s、CPU/request 20%削減。
4. Experiment を分離する。feature flag、canary、load test、synthetic traffic。
5. Regression guard をCI/CDまたはrelease gateに追加する。
6. Optimization の副作用を確認する。キャッシュ不整合、tail latency、memory pressure、cost shift。

### 8.10 Availability / Redundancy / Failover / DR / BCP

**Availability design:**

- target availability から allowed downtime を計算し、on-call response、detection、mitigation、failover time を逆算する。
- 単一障害点を dependency graph で洗い出す。
- Failure domain を分ける。process、node、zone、region、provider、identity、DNS、CI/CD、control plane、data plane。
- Graceful degradation、load shedding、rate limiting、circuit breaker、backpressure を設計する。
- Google SRE の overload handling と同様、過負荷時は redirect / degraded responses / resource error handling を透明に扱う。[^sre-overload]

**Redundancy design:**

- Azure Well-Architected は critical flows の各 workload layer に適切な redundancy を加えることを推奨する。冗長化は compute / data / networking / infrastructure tier ごとに設計する。[^azure-redundancy]
- Google Cloud は region/zone、managed instance groups、GKE、regional persistent disks、global load balancing、built-in redundancy を利用した scalable/resilient apps パターンを示している。[^gcp-scalable]
- 冗長化の設計対象は、インスタンス数だけでなく、データ、設定、認証、監視、CI/CD、DNS、status page、operator access を含む。

**Failover design:**

- Trigger: SLO breach、health check、data plane failure、region outage、manual incident decision。
- Mechanism: traffic shift、DNS、load balancer、database promotion、queue drain、feature disable、read-only mode。
- Guardrails: split-brain防止、replication lag check、idempotent recovery script、rollback path、manual approval boundary。
- Azure は failover environment の deployment / recovery procedure を可能な限り自動化し、RTO targets に合わせること、declarative/idempotent scripts と retry/circuit-breaker logic を使うことを推奨している。[^azure-dr]

**DR strategy selection:**

AWS は DR について、backup と redundant workload components は出発点であり、RTO/RPOを business needs に基づいて設定し、probability of disruption と cost of recovery を踏まえて戦略を選ぶと説明している。[^aws-dr]

| Strategy | 典型RTO/RPO | Cost | 適用条件 | 主なリスク |
|---|---|---:|---|---|
| Backup and restore | hours–days | 低 | 低頻度利用、低収益影響、長いRTO許容 | restore未検証、data loss、復旧順序不明 |
| Pilot light | minutes–hours | 中 | core data/services を常時保持し、app層を復旧時に拡張 | 起動手順失敗、依存不足 |
| Warm standby | minutes | 中〜高 | 重要サービス、短いRTO、限定規模で常時稼働 | capacity不足、切替後過負荷 |
| Multi-site active-active | near-zero〜minutes | 高 | 重大事業機能、グローバル高可用性 | data consistency、運用複雑性、blast radius拡大 |

**BCP:**

NIST SP 800-34 は contingency planning の目的・プロセス・形式を理解し、情報システムと運用を評価して計画要件と優先順位を決めるためのガイドであり、DR plan と BIA template を補助資料として提供している。ISO 22301 は、組織のレジリエンス向上、リスク管理改善、体系的危機対応、stakeholder trust に寄与する BCMS 標準である。[^nist-800-34][^iso-22301]

BCP では、IT復旧だけでなく次を含める。

- Critical business functions and owners
- MTD / RTO / RPO / manual workaround
- People availability, delegation, emergency access
- Supplier / vendor / cloud / network / payment / logistics dependency
- Customer / regulator / media communication
- Legal, privacy, contractual obligations
- Facilities, remote work, device, identity, cash/approval process
- Exercise plan, lessons learned, plan maintenance

---

## 9. Layer-specific Clone Spec Matrix

| ID | Name | Frontier Pattern | Minimum Clone Spec | Failure Modes / Anti-patterns | Confidence |
|---:|---|---|---|---|---|
| 22.01 | Metrics | SLO指標と診断指標を分け、runtime measurement を安定したmetadataと集約で扱う。 | golden signals、SLI event ratio、resource saturation、recording rules、cardinality policy、retention tier。 | label爆発、平均値依存、infra metricだけでpage、cost未管理。 | A |
| 22.02 | Logs | structured logs を基準に、event type / severity / trace_id / redaction を持つ。 | JSON/log schema、severity enum、PII redaction、audit log、retention、log sampling。 | unstructured free text、secret漏洩、ログ量肥大、severity乱用、検索不能。 | A |
| 22.03 | Traces | critical request path を span 化し、context propagation で service boundary をまたぐ。 | trace/span naming、sampling、W3C context、span attributes、exemplars、logsとの相関。 | sampling過少、missing parent、高cardinality attribute、async処理の切断。 | A |
| 22.04 | Alerts | SLO/error budget と user-visible symptom から page/ticket/automation を分ける。 | alert rule、severity、routing、dedup/grouping、silence、runbook link、burn-rate rule。 | alert fatigue、duplicate pages、threshold-only、unactionable page、low-traffic誤検知。 | A |
| 22.05 | Dashboards | 役割ごとの判断 view を作り、dashboard as code で管理する。 | executive/SLO/incident/diagnostic/capacity/DR dashboard、owner、review date。 | 見るだけdashboard、owner不明、古いpanel、incident中に探す。 | A |
| 22.06 | SLI | CUJに対して good event / total event を定義し、ユーザー体験に近い測定点を選ぶ。 | SLI definition、measurement query、source of truth、eligibility/exclusions。 | server availabilityをユーザー体験と誤認、client側劣化を未計測。 | A |
| 22.07 | SLO | SLI target、window、例外、review cadence を定義し、運用判断に接続する。 | SLO document、rolling window、burn dashboard、review process。 | 全サービス同一SLO、99.999乱用、現実より高すぎる目標、未レビュー。 | A |
| 22.08 | SLA | 外部合意を internal SLO より保守的にし、credit/claim/exceptionを明確にする。 | SLA terms、measurement source、maintenance、excluded events、credits。 | SLA>SLO、例外不明、status reportなし、営業主導で運用不可能。 | B |
| 22.09 | Error Budget | `1 - SLO` を変更制御、release risk、信頼性投資へ接続する。 | error budget policy、burn thresholds、release freeze、risk review。 | budget無視、green SLOでも顧客不満、budget超過時の行動なし。 | A |
| 22.10 | Incident | severity/roles/timeline/commsを即時に立ち上げる command system。 | incident declaration、Incident Lead、Responder、Comms、state doc、status page。 | incident宣言遅れ、全員が調査、顧客通信なし、decision owner不在。 | A/B |
| 22.11 | On-call | 持続可能な輪番、応答時間、primary/secondary、escalationを設計する。 | rotation、handover、training、escalation、compensation/coverage、alert load review。 | 1人運用、無補償、夜間過多、untrained responder、burnout。 | A |
| 22.12 | Runbook | 既知症状に対して安全な診断・緩和・rollback・escalationを提供する。 | symptom、pre-check、commands、decision tree、mitigation、verification、owner。 | stale runbook、危険操作、rollback不在、tribal knowledge。 | B |
| 22.13 | Postmortem | blame-freeに根本要因・影響・再発防止を文書化し、action itemを閉じる。 | trigger criteria、owner、timeline、RCA、action items、review meeting。 | human errorで終了、action item未完、未レビュー、repeat incident。 | A |
| 22.14 | Capacity Planning | demand/load、capacity、software efficiency、cost を forecast と load test で結ぶ。 | demand forecast、headroom target、quota、autoscaling、load test、capacity review。 | launch前未検証、quota忘れ、over/under-provision、季節性無視。 | B |
| 22.15 | Performance Tuning | SLO risk / cost risk を基準に bottleneck を計測し、regression guard を作る。 | profiling、trace analysis、perf budget、optimization backlog、release gate。 | 平均latencyだけ、tail latency無視、最適化の副作用未確認。 | B |
| 22.16 | Availability Design | failure model から architecture と operations を逆算する。 | availability target、dependency map、fault model、degradation plan、resilience review。 | SPOF、control plane依存、manual-only復旧、依存SLO未確認。 | A |
| 22.17 | Redundancy | critical flow の各層に適切な冗長性を加え、整合性とコストを管理する。 | redundancy matrix、replication、multi-zone/region、quorum、dependency redundancy。 | 冗長化の過信、同一failure domain、replication lag無視、複雑性増加。 | A |
| 22.18 | Failover | trigger、切替、検証、rollback、権限を自動化・手順化する。 | failover runbook、traffic switch、DB promotion、split-brain guard、game day。 | 切替未演習、DNS TTL忘れ、戻し手順なし、partial failover。 | A |
| 22.19 | Disaster Recovery | business RTO/RPOからDR strategyを選び、restore/failoverを実測する。 | DR plan、backup、restore test、regional recovery、RTO/RPO evidence。 | backupあり復旧不可、RPO未測定、dependent service不在、権限不明。 | A |
| 22.20 | BCP | IT復旧をcritical business functions、人員、サプライヤー、通信に接続する。 | BIA、BC plan、crisis comms、manual workaround、supplier plan、exercise。 | ITだけのBCP、BIA未更新、机上計画、サプライヤー障害未考慮。 | A |

---

## 10. Metrics

### 10.1 Reliability / SLO

| Metric | Definition | Use |
|---|---|---|
| SLO attainment | measurement window 内で SLI が target を満たした割合 | product/SRE governance |
| Error budget remaining | `allowed bad events - observed bad events` | release risk / freeze decision |
| Burn rate | SLOに対するbudget消費速度 | alerting / escalation |
| Customer impact minutes | affected customers × duration | incident severity / SLA reporting |
| SLA breach count | contractually defined breach events | legal/support/finance |

### 10.2 Observability Platform

| Metric | Definition | Use |
|---|---|---|
| Instrumentation coverage | critical services with metrics/logs/traces | observability readiness |
| Cardinality growth | time series count / labels / service | cost and query stability |
| Trace completeness | traces with full critical path spans | diagnosis quality |
| Log parse failure rate | logs rejected or unmatched by schema | analysis quality |
| Telemetry cost per service | ingest + storage + query cost | budget and optimization |

### 10.3 Alert / Incident

| Metric | Definition | Use |
|---|---|---|
| Alert precision | alerts that correspond to significant events | noise reduction |
| Alert recall | significant events detected by alerts | detection quality |
| MTTD | event start to detection | monitoring quality |
| MTTA | detection to acknowledgement | on-call quality |
| MTTM / MTTR | detection to mitigation / resolution | response quality |
| Alert:incident ratio | pages per incident | grouping/dedup quality |
| Postmortem action completion | closed action items / total | learning loop |

### 10.4 Capacity / Performance / Continuity

| Metric | Definition | Use |
|---|---|---|
| Headroom | available capacity before saturation | capacity planning |
| Forecast error | forecast vs actual load/resource | planning quality |
| Autoscaling latency | scale trigger to usable capacity | overload prevention |
| p95/p99 latency | tail latency | user experience |
| RTO actual | failover/restore time measured in exercise | DR readiness |
| RPO actual | actual data loss window | DR/data readiness |
| Restore success rate | successful restore tests / total | backup validity |
| BCP exercise pass rate | exercises meeting objectives | continuity maturity |

---

## 11. Failure Modes

| Failure Mode | Cause | Detection | Mitigation |
|---|---|---|---|
| Alert fatigue | threshold-only alerts, duplicate alerts, non-actionable alerts | pages/shift, alert:incident ratio, ignored alerts | SLO burn alerts, grouping/dedup, silence, alert review |
| Observability cost explosion | unbounded labels, full traces/logs, retention不設計 | ingest cost, cardinality, query latency | cardinality policy, sampling, retention tiers, aggregation |
| SLO theater | SLOが意思決定に使われない | budget超過でもrelease継続 | error budget policy, review cadence, release gates |
| Dashboard sprawl | owner不在、目的不明、stale panels | stale dashboard count, incident中の探索時間 | dashboard catalog, as-code, deletion policy |
| On-call burnout | pages過多、少人数、夜間過多、runbook不足 | pages/shift, attrition, incident load | rotation設計、noise reduction、training、staffing |
| Runbook rot | 手順未更新、依存変更、未演習 | runbook failure in incidents | owner/review, game day, automation tests |
| Blameful postmortem | 個人責任追及、心理的安全性不足 | root causeがhuman errorのみ | blameless template, review, management reinforcement |
| Capacity surprise | launch/seasonality/quota無視 | saturation, overload incidents | forecast, load tests, quota management, autoscaling |
| Tail latency regression | average metric依存、p99未監視 | p95/p99 SLI breach | percentile SLI, tracing, profiling, perf gates |
| Failover failure | 未演習、依存不明、manual-only, DNS/DB切替不備 | game day failure, RTO breach | regular failover drills, automation, rollback plan |
| Backup unrecoverable | restore未検証、権限/暗号鍵/依存欠落 | restore test fail | restore drills, key escrow, dependency map |
| BCP incomplete | IT中心、people/supplier/comms除外 | exercise failure, unclear roles | BIA, business owner involvement, tabletop/full exercise |

---

## 12. Anti-pattern Library

| Pattern ID | Anti-pattern | Why harmful | Replacement Pattern |
|---|---|---|---|
| AP-001 | CPU 90% page | user impact不明でnoiseが多い | saturation + SLO impact + capacity forecast |
| AP-002 | 全ログ永久保存 | cost/PII/query性能が破綻 | retention tier + sampling + redaction |
| AP-003 | request_id を metrics label に入れる | cardinality爆発 | request_idはtrace/log属性、metricはbounded labels |
| AP-004 | SLAを営業資料だけで決める | 運用不能・補償リスク | internal SLO > external SLA + legal/SRE review |
| AP-005 | 全サービス99.99% | 価値・コスト・依存性が無視される | CUJ criticality-based SLO |
| AP-006 | SLO違反後もlaunch継続 | reliability governanceが無効 | error budget policy / risk acceptance |
| AP-007 | 一人オンコール | burnout / single point of knowledge | primary/secondary + escalation + training |
| AP-008 | incident中に役割を決める | coordinationが遅れる | pre-defined IC/Responder/Comms roles |
| AP-009 | Postmortem = 人為ミス | 再発防止がシステムに戻らない | contributing factors + systemic actions |
| AP-010 | multi-regionならDR完了 | 切替・整合性・権限・復旧順序が未検証 | RTO/RPO exercise + failover runbook |
| AP-011 | backup successだけを監視 | restore可能性を保証しない | restore test + RPO actual + key/access validation |
| AP-012 | BCPをIT部門だけで作る | critical business functionが守れない | business-led BIA + supplier/comms/people plan |

---

## 13. Maturity Model

| Level | Name | Criteria |
|---:|---|---|
| 0 | 未整備 | 死活監視のみ。alert owner不明。incidentはチャットで場当たり対応。backupはあるがrestore未確認。 |
| 1 | 個人依存 | 一部メトリクス/ログあり。経験者が調査できる。on-callは非公式。runbookは断片的。 |
| 2 | 文書化 | metrics/logs/tracesの基本整備、service owner、runbook、incident severity、postmortem template、DR文書がある。 |
| 3 | 標準化 | SLI/SLO/error budget、alert routing、dashboard catalog、on-call rotation、incident roles、BIA/RTO/RPOが標準化される。 |
| 4 | 自動化・計測 | burn-rate alerts、observability as code、auto-remediation、capacity forecast、load/failover/restore exercises、action item trackingが機能する。 |
| 5 | 自律改善・業界先端 | SLOと事業意思決定が接続し、telemetry costも最適化され、failure injection/DR/BCP演習が継続し、postmortemからarchitectureとprocessが自律改善する。 |

---

## 14. Clone Implementation Guide

### 0–30 days: Baseline

- Service catalog を作り、critical user journeys と owner を登録する。
- 主要サービスに minimal metrics/logs/traces を導入する。
- Golden signals dashboard と basic incident dashboard を作る。
- 既存 alert を棚卸しし、page/ticket/info に分類する。
- Incident severity、Incident Lead / Responder / Comms Lead の役割を決める。
- 重大サービスの backup / restore 状況を確認する。
- BIA の対象 business function を特定する。

**Artifacts:** `service_catalog.csv`, `telemetry_baseline.md`, `alert_inventory.csv`, `incident_roles.md`, `backup_restore_gap.md`, `bia_scope.md`

### 31–60 days: SLO-driven operations

- 上位5–10の critical user journeys に SLI/SLO を定義する。
- Error budget policy を作る。
- SLO burn-rate alert を page/ticket に分けて実装する。
- Alertmanager / incident tooling の routing / grouping / silence / escalation を整備する。
- On-call handover、training、runbook template を導入する。
- Postmortem trigger と owner assignment を標準化する。

**Artifacts:** `slo_documents/`, `error_budget_policy.md`, `alert_rules.yaml`, `oncall_policy.md`, `runbook_template.md`, `postmortem_template.md`

### 61–90 days: Reliability controls

- Runbook coverage を major alerts に対して80%以上にする。
- Incident state doc と status update cadence を演習する。
- Capacity forecast と headroom target を作る。
- Load test と performance regression guard を導入する。
- Dependency map と single point of failure register を作る。
- DR plan に RTO/RPO、restore order、failover trigger、roles を入れる。

**Artifacts:** `runbooks/`, `capacity_model.xlsx or md`, `dependency_map.md`, `spof_register.csv`, `dr_plan.md`, `load_test_report.md`

### 91–180 days: Continuity and continuous improvement

- Dashboard / alert / collector config を code 化し、CIでlint/testする。
- Postmortem action item completion を経営レビューに入れる。
- Failover game day、restore test、BCP tabletop exercise を実施する。
- SLAとSLOの整合を legal/sales/support/SRE でレビューする。
- Telemetry cost/carinality review を定例化する。
- Error budget と product roadmap / launch governance を接続する。

**Artifacts:** `observability_as_code/`, `game_day_report.md`, `restore_test_report.md`, `bcp_exercise_report.md`, `sla_slo_alignment.md`, `telemetry_cost_report.md`

---

## 15. Validation Queries

RESEARCH.md の反証・検証方針に合わせ、次のクエリで claim を崩しに行く。

| Query | 狙い | 崩す対象 |
|---|---|---|
| `site:sre.google "alerting on SLOs" "precision" "recall"` | SLO alert 評価軸の確認 | C-008 |
| `site:sre.google "error budget" "1 minus the SLO"` | error budget 定義の確認 | C-007 |
| `site:sre.google "Being On-Call" "25%" "incidents per day"` | on-call閾値の確認 | C-011 |
| `site:opentelemetry.io/docs/concepts/signals "Traces" "Metrics" "Logs"` | OTel signal supportの確認 | C-001 |
| `site:opentelemetry.io/docs/concepts/context-propagation "traces" "metrics" "logs"` | signal correlationの確認 | C-004 |
| `site:prometheus.io/docs/alerting "deduplicating" "grouping" "routing"` | Alertmanager機能の確認 | C-009 |
| `site:grafana.com/docs/grafana/latest/as-code "version" "dashboards" "CI/CD"` | observability-as-codeの確認 | C-010 |
| `site:docs.aws.amazon.com/wellarchitected "Automatically recover from failure" "KPIs"` | AWS reliability principle確認 | C-014 |
| `site:docs.aws.amazon.com/wellarchitected "RTO" "RPO" "Disaster Recovery"` | DR目標の確認 | C-015 |
| `site:learn.microsoft.com/en-us/azure/well-architected/reliability "failover" "RTO" "idempotent"` | Azure DR automation確認 | C-016 |
| `site:csrc.nist.gov/pubs/sp/800/34/r1 "Business Impact Analysis" "Disaster Recovery"` | NIST artifacts確認 | C-017 |
| `site:iso.org "ISO 22301" "Business continuity" "resilience"` | ISO 22301の現行確認 | C-018 |
| `site:handbook.gitlab.com "Incident Management" "Engineer On Call" "Incident Manager On Call"` | GitLab role model確認 | C-012 |
| `site:response.pagerduty.com "Postmortem Process" "SEV-2/1"` | PagerDuty postmortem trigger確認 | C-013 |
| `"GitLab" "database outage" "postmortem"` | 公開失敗事例からrunbook/backup/restoreの反証探索 | 22.19/22.20 failure modes |

---

## 16. Confidence & Unknowns

### Confidence A

- OpenTelemetry signals、metrics/logs/traces、context propagation の基本定義。
- Google SRE の SLI/SLO/SLA、golden signals、error budget、on-call、postmortem、SLO alert 設計。
- Prometheus Alertmanager の grouping / dedup / routing / silencing / inhibition。
- Grafana の dashboards と observability as code の公式説明。
- AWS/Azure/Google Cloud の reliability / redundancy / DR 公式設計原則。
- NIST SP 800-34 と ISO 22301 の contingency / BCMS の公式位置づけ。

### Confidence B

- GitLab / PagerDuty の incident/on-call/postmortem 運用を一般組織へ移植する際の役割分離モデル。
- 一般的な service owner / product owner / SRE / legal / risk の責任分界。
- DR strategy の RTO/RPOレンジ。実際の値は業務とシステムに依存する。

### Confidence C

- 各 layer ID の個別名称。ユーザー指定は範囲とサブテーマであり、正式台帳が未提示のため、サブテーマを20個に分解して割り当てた。
- 具体的な page threshold、burn rate threshold、retention period、sampling rate、headroom target。これはサービス規模・顧客契約・コストによって異なる。

### Unknowns / 追加調査

- 対象組織の既存ツールチェーン、cloud/provider、service criticality、SLA契約。
- 現行 incident history、alert noise、on-call負荷、postmortem完了率。
- データ分類、PII、ログ保持、規制要件。
- 既存DR topology、backup/restore実績、BCP演習結果。
- サードパーティ依存、サプライヤー契約、顧客通信義務。

---

## 17. References

[^otel-signals]: OpenTelemetry, “Signals,” https://opentelemetry.io/docs/concepts/signals/ . Signals are defined as system outputs; supported categories include traces, metrics, logs, and baggage. Accessed 2026-05-13.
[^otel-metrics]: OpenTelemetry, “Metrics,” https://opentelemetry.io/docs/concepts/signals/metrics/ . Defines metrics as runtime measurements and discusses instruments and aggregation. Accessed 2026-05-13.
[^otel-logs]: OpenTelemetry, “Logs,” https://opentelemetry.io/docs/concepts/signals/logs/ . Defines logs as timestamped records and describes structured/unstructured logs and trace correlation. Accessed 2026-05-13.
[^otel-traces]: OpenTelemetry, “Traces,” https://opentelemetry.io/docs/concepts/signals/traces/ . Describes tracers, spans, trace exporters, and context propagation. Accessed 2026-05-13.
[^otel-context]: OpenTelemetry, “Context propagation,” https://opentelemetry.io/docs/concepts/context-propagation/ . Explains correlation of traces, metrics, and logs across services. Accessed 2026-05-13.
[^cncf-tag]: CNCF TAG Observability, https://tag-observability.cncf.io/ . TAG scope and end-user guidance. Accessed 2026-05-13.
[^cncf-whitepaper]: CNCF TAG Observability, “Observability Whitepaper,” https://github.com/cncf/tag-observability/blob/main/whitepaper.md . Discusses primary signals, purpose, cost, cardinality, alert fatigue, and correlation. Accessed 2026-05-13.
[^sre-slo]: Google SRE Book, “Service Level Objectives,” https://sre.google/sre-book/service-level-objectives/ . Defines SLI, SLO, SLA and user-relevant metrics. Accessed 2026-05-13.
[^sre-golden]: Google SRE Book, “Monitoring Distributed Systems,” https://sre.google/sre-book/monitoring-distributed-systems/ . Defines the four golden signals: latency, traffic, errors, saturation. Accessed 2026-05-13.
[^sre-error-budget]: Google SRE Workbook, “Error Budget Policy,” https://sre.google/workbook/error-budget-policy/ . Defines error budget as 1 minus SLO. Accessed 2026-05-13.
[^sre-alerting]: Google SRE Workbook, “Alerting on SLOs,” https://sre.google/workbook/alerting-on-slos/ . Discusses precision, recall, detection time, reset time, and burn-rate alerting. Accessed 2026-05-13.
[^sre-oncall]: Google SRE Book, “Being On-Call,” https://sre.google/sre-book/being-on-call/ . Discusses sustainable on-call, response times, 25% rule, primary/secondary, and alert noise. Accessed 2026-05-13.
[^sre-postmortem]: Google SRE Book, “Postmortem Culture,” https://sre.google/sre-book/postmortem-culture/ . Defines postmortem content and blameless philosophy. Accessed 2026-05-13.
[^sre-overload]: Google SRE Book, “Handling Overload,” https://sre.google/sre-book/handling-overload/ . Discusses graceful degradation and load balancing under overload. Accessed 2026-05-13.
[^sre-intro]: Google SRE Book, “Introduction,” https://sre.google/sre-book/introduction/ . Discusses demand/load, capacity, and software efficiency. Accessed 2026-05-13.
[^prom-alertmanager]: Prometheus, “Alertmanager,” https://prometheus.io/docs/alerting/latest/alertmanager/ . Describes deduplication, grouping, routing, silencing, and inhibition. Accessed 2026-05-13.
[^prom-alert-rules]: Prometheus, “Alerting rules,” https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/ . Describes alert rules, PromQL expressions, `for`, and notification to external services. Accessed 2026-05-13.
[^grafana-dashboard]: Grafana, “Dashboards,” https://grafana.com/docs/grafana/latest/visualizations/dashboards/ . Defines dashboards as panels that provide an at-a-glance view of related information. Accessed 2026-05-13.
[^grafana-oac]: Grafana, “Observability as Code,” https://grafana.com/docs/grafana/latest/as-code/observability-as-code/ . Describes versioning, automation, CI/CD, and programmatic management of dashboards and observability workflows. Accessed 2026-05-13.
[^aws-rel-principles]: AWS, “Design principles - Reliability Pillar,” https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/design-principles.html . Describes automatically recovering from failure by monitoring KPIs and triggering automation. Accessed 2026-05-13.
[^aws-dr]: AWS, “Plan for Disaster Recovery (DR),” https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/plan-for-disaster-recovery-dr.html . Describes RTO/RPO as objectives for restoration and business-need based DR strategy. Accessed 2026-05-13.
[^azure-dr]: Microsoft Azure Well-Architected Framework, “Architecture strategies for disaster recovery,” https://learn.microsoft.com/en-us/azure/well-architected/reliability/disaster-recovery . Recommends automated deployment/recovery procedures aligned with RTO targets. Accessed 2026-05-13.
[^azure-redundancy]: Microsoft Azure Well-Architected Framework, “Architecture Strategies for Designing for Redundancy,” https://learn.microsoft.com/en-us/azure/well-architected/reliability/redundancy . Recommends redundancy throughout critical flows and workload layers. Accessed 2026-05-13.
[^azure-principles]: Microsoft Azure Well-Architected Framework, “Reliability design principles,” https://learn.microsoft.com/en-us/azure/well-architected/reliability/principles . Reliability principles across lifecycle. Accessed 2026-05-13.
[^gcp-reliability]: Google Cloud Architecture Center, “Well-Architected Framework: Reliability pillar,” https://docs.cloud.google.com/architecture/framework/reliability . Provides principles and recommendations to design, deploy, and manage reliable workloads. Accessed 2026-05-13.
[^gcp-scalable]: Google Cloud Architecture Center, “Patterns for scalable and resilient apps,” https://docs.cloud.google.com/architecture/scalable-and-resilient-apps . Discusses regions/zones, regional persistent disks, global load balancing, and built-in redundancy. Accessed 2026-05-13.
[^nist-800-34]: NIST CSRC, “SP 800-34 Rev. 1, Contingency Planning Guide for Federal Information Systems,” https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final . Provides contingency planning guidance and BIA/plan templates. Accessed 2026-05-13.
[^iso-22301]: ISO, “ISO 22301:2019 - Security and resilience — Business continuity management systems — Requirements,” https://www.iso.org/standard/75106.html . Describes BCMS, resilience, risk identification, emergency preparation, and recovery time improvement. Accessed 2026-05-13.
[^gitlab-im]: GitLab Handbook, “Incident Management,” https://handbook.gitlab.com/handbook/engineering/infrastructure-platforms/incident-management/ . Describes incident roles, EOC/IMOC, on-call schedules, runbooks, status definitions, and incident metrics. Accessed 2026-05-13.
[^pd-ir]: PagerDuty, “Incident Response Documentation,” https://response.pagerduty.com/ . Describes incident preparation, during-incident, and after-incident process for on-call practitioners. Accessed 2026-05-13.
[^pd-postmortem]: PagerDuty, “Postmortem Process,” https://response.pagerduty.com/after/post_mortem_process/ . Describes SEV-1/2 postmortems, blame-free description, and owner designation. Accessed 2026-05-13.
[^gitlab-outage]: GitLab, “Postmortem of database outage of January 31,” https://about.gitlab.com/blog/postmortem-of-database-outage-of-january-31/ . Public failure evidence for backup/restore and incident learning patterns. Accessed 2026-05-13.
