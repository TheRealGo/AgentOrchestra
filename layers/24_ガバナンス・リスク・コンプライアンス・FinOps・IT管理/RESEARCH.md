# Frontier Operating Model Research: ガバナンス・リスク・コンプライアンス・FinOps・IT管理（Layer 24）

生成日: 2026-05-13 JST  
対象範囲: governance、compliance、audit、risk、change、asset / license / cost management、FinOps、data governance、privacy、legal、contract、vendor management  
調査制約: 公開情報のみ。標準、規制、公式フレームワーク、公式ガイド、公式プレスリリースを優先し、マーケティング資料・二次解説・求人情報は中核証拠に採用しない。

> 注: 依頼表は `24` の範囲とサブテーマを指定しているが、各番号の正式レイヤー名は提示されていない。そのため、本成果物ではサブテーマを順序に沿って 14 個の実務レイヤーへ仮マッピングした。既存の layer registry がある場合は、`layer_name` だけを差し替えても Decision Model は再利用できる。

---

## 0. Method Summary

本リサーチは RESEARCH.md の Frontier Operating Model Research の形式に合わせ、各レイヤーを「意思決定システム」として再構成した。具体的には、各レイヤーについて `Definition / Frontier Exemplars / Evidence Map / Core Philosophy / Decision Model / Operating Model / Technical or Business Specification / Metrics / Failure Modes / Anti-patterns / Maturity Model / Clone Implementation Guide / Confidence & Unknowns` を出力単位にした。

証拠は次の優先順位で採用した。

| Tier | 採用対象 | 本調査での例 |
|---|---|---|
| T0 | 規範的一次情報、標準、公式フレームワーク | NIST CSF/RMF/SP 800-53/SP 800-161、ISO 37301、ISO 31000、ISO/IEC 19770-1、ISO/IEC 27701、ISO 31022、OpenChain ISO/IEC 5230、IIA Standards、FinOps Framework |
| T1 | 規制・法定・監査開示 | SEC Item 106 cybersecurity disclosure rule、EU GDPR controller/processor guidance |
| T2 | 実行可能成果物・公式運用ガイド | AWS Well-Architected Cost Optimization、Google Cloud Architecture Framework、Microsoft Cloud Adoption Framework |
| T3 | 公式運用文書・成熟度モデル | CLOC Core 12、WorldCC Contract Management Standard、EDM Council DCAM、DAMA-DMBOK |
| T4 | 履歴・制度資料 | 標準の改訂履歴、2025年版 ISO/IEC 27701 など |
| T5 | 外部検証・失敗証拠 | SEC/FTC Blackbaud enforcement release |

本稿の各 Claim は、原則として T0/T1/T2 を中核にし、失敗・反証は T5 で補強する。公開情報で確認できない内部会議体、実運用の閾値、ベンダー契約の非公開条項は `Unknowns` に隔離した。

---

## 1. Executive Summary

Layer 24 の Frontier Operating Model は、単なる「管理部門の文書体系」ではなく、**組織の意思決定・例外処理・証拠収集・継続改善を統合する control graph** として設計される。先端組織に共通するパターンは次のとおりである。

1. **Governance first**: 方針、リスク選好、説明責任、監督者、例外権限を先に定義する。COBIT、NIST CSF 2.0、SEC Item 106 は、サイバー・IT・リスクが経営監督と統合されることを示す。
2. **Risk-based tiering**: すべてを同じ重さで統制しない。資産、変更、ベンダー、データ、契約、費用を重要度・影響度・規制性・集中リスクで階層化する。
3. **Evidence-as-data**: 監査やコンプライアンスの証拠は、後追いのスクリーンショットではなく、control owner、control objective、system of record、timestamp、exception state、review status を持つデータとして管理する。
4. **Lifecycle closure**: 要求、評価、承認、実行、監視、再評価、終了を必ず閉じる。契約・ベンダー・資産・データ・変更・コストはすべて lifecycle object として扱う。
5. **FinOps and cost accountability**: クラウド/ITコストは会計上の費目ではなく、ビジネス価値、プロダクト、ワークロード、利用者行動へ紐づく意思決定信号に変換する。
6. **Privacy, legal, vendor flowdown**: プライバシー・法務・サプライチェーンは社内統制だけでは閉じない。契約条項、委託先管理、データ処理役割、通知義務、監査権、終了時処理へ flowdown する。
7. **Failure-informed controls**: Blackbaud 事例のように、セキュリティ/プライバシー/開示の失敗は「技術統制の欠陥」だけでなく、「情報が開示管理・上級管理者へ届かない governance failure」として扱う。

---

## 2. Layer Mapping

| Layer ID | 仮レイヤー名 | Decision Object | 主な成果物 | 主責任ロール |
|---|---|---|---|---|
| 24.01 | Enterprise / IT Governance | どの意思決定権限・監督構造・統制目的でIT/データ/リスクを運営するか | governance charter、risk appetite、control taxonomy、board/committee pack | Board、CIO、CISO、CRO、GRC owner |
| 24.02 | Compliance Management | どの義務を、どの統制・証拠・責任者で満たすか | obligation register、control matrix、compliance calendar、evidence repository | CCO、GRC、control owners |
| 24.03 | Internal Audit & Assurance | どのリスク・統制を独立評価し、どの改善要求を出すか | audit plan、audit charter、engagement report、finding tracker | CAE、Internal Audit、Audit Committee |
| 24.04 | Enterprise Risk Management | どのリスクを識別・評価・処理・監視するか | risk register、KRI、treatment plan、risk report | CRO、risk owners、executive committee |
| 24.05 | Change Governance / Change Enablement | どの変更を、どのリスク評価・承認・ロールバック条件で実行するか | change record、CAB decision、deployment evidence、rollback plan | Change authority、service owner、SRE、platform owner |
| 24.06 | IT Asset Management | どの資産を、誰が、どの lifecycle と証拠で管理するか | asset inventory、CMDB、ownership map、retirement record | ITAM owner、IT ops、security、finance |
| 24.07 | License & OSS Compliance | どのソフトウェア/OSS/商用ライセンスを、どの使用権・義務で管理するか | license inventory、SBOM、notice file、entitlement/reconciliation report | Legal、engineering、procurement、ITAM |
| 24.08 | IT Cost Management | どのIT費用を、どの単位・予算・配賦・最適化条件で制御するか | budget, chargeback/showback, unit cost model, anomaly alert | CFO/FP&A、CIO、platform finance |
| 24.09 | FinOps / Cloud Financial Management | クラウド支出をどの可視化・最適化・運用サイクルで事業価値へ接続するか | allocation tags、unit economics、commitment plan、optimization backlog | FinOps team、engineering、finance、product |
| 24.10 | Data Governance | どのデータ資産を、どの所有権・品質・利用制限・系譜で統治するか | data catalog、data glossary、lineage、DQ rules、access policy | CDO、data owners、data stewards |
| 24.11 | Privacy & Data Protection | どの個人データ処理を、どの目的・法的根拠・権利対応・最小化で許容するか | PII inventory、DPIA/PIA、DSAR log、retention schedule、processor register | DPO/privacy office、legal、security、product |
| 24.12 | Legal Risk & Legal Operations | どの法的リスク・案件・外部弁護士・法務費用を管理するか | legal risk register、matter intake、outside counsel guideline、legal ops dashboard | GC、legal ops、business counsel |
| 24.13 | Contract Lifecycle Management | どの契約を、どの条項・承認・義務・更新/終了で管理するか | clause library、contract playbook、CLM workflow、obligation register | Legal、procurement、sales ops、contract owner |
| 24.14 | Vendor / Third-Party Management | どの第三者を、どの重要度・契約・監視・退出条件で管理するか | vendor inventory、tiering model、due diligence record、SLA/security review、exit plan | Procurement、vendor owner、TPRM、security、legal |

---

## 3. Source Catalog

| ID | Tier | Source | Entity | 主な用途 | URL |
|---|---:|---|---|---|---|
| S01 | T0 | Cybersecurity Framework 2.0 | NIST | GOVERN機能、リスク成果分類、非規定型フレームワーク | https://csrc.nist.gov/pubs/cswp/29/the-nist-cybersecurity-framework-csf-20/final |
| S02 | T0 | Risk Management Framework SP 800-37 Rev.2 | NIST | categorization、control selection、authorization、continuous monitoring | https://csrc.nist.gov/pubs/sp/800/37/r2/final |
| S03 | T1 | 17 CFR 229.106 Cybersecurity Disclosure | SEC/eCFR | サイバーリスク管理、第三者リスク、取締役会監督、経営者役割 | https://www.ecfr.gov/current/title-17/chapter-II/part-229/subpart-229.100/section-229.106 |
| S04 | T0/T3 | COBIT | ISACA | enterprise IT governance、40 governance/management objectives、design/implementation guide | https://www.isaca.org/resources/cobit |
| S05 | T0 | ISO 37301 Compliance Management Systems | ISO | compliance management system の確立・維持・改善 | https://www.iso.org/standard/75080.html |
| S06 | T0/T3 | Global Internal Audit Standards | IIA | 内部監査の必須基準、独立性、監査計画、監査実施、報告 | https://www.theiia.org/en/standards/2024-standards/global-internal-audit-standards/ |
| S07 | T0 | ISO 31000 Risk Management | ISO | risk identification, analysis, evaluation, treatment, monitoring, communication | https://www.iso.org/standard/65694.html |
| S08 | T0 | Security and Privacy Controls SP 800-53 Rev.5 | NIST | security/privacy control catalog、組織的リスクプロセス | https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final |
| S09 | T0/T3 | ITIL 4 Practitioner: Change Enablement | PeopleCert | 変更成功率最大化、リスク評価、承認、スケジュール管理 | https://www.peoplecert.org/browse-certifications/it-governance-and-service-management/ITIL-1/itil-4-practitioner-change-enablement-3794 |
| S10 | T0 | ISO/IEC 19770-1 IT Asset Management Systems | ISO | ITAMシステム要件、組織能力評価 | https://www.iso.org/standard/68531.html |
| S11 | T0 | ISO/IEC 5230 OpenChain License Compliance | OpenChain Project | OSSライセンス要求管理、役割・責任、持続可能性 | https://openchainproject.org/license-compliance |
| S12 | T0/T3 | FinOps Framework | FinOps Foundation | FinOps operating model、principles、personas、domains、capabilities | https://www.finops.org/framework/ |
| S13 | T0/T3 | FinOps Phases | FinOps Foundation | Inform / Optimize / Operate の反復サイクル | https://www.finops.org/framework/phases/ |
| S14 | T2/T3 | Monitor cost and usage | AWS Well-Architected | cost visibility、cost allocation、billing/cost tools、usage metrics | https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/monitor-cost-and-usage.html |
| S15 | T2/T3 | Cost Optimization | Google Cloud Architecture Framework | cloud spend と business value の整合、継続的モニタリング | https://docs.cloud.google.com/architecture/framework/cost-optimization |
| S16 | T2/T3 | Cloud Adoption Framework | Microsoft Azure | govern/secure/manage workloads、クラウド導入ロードマップ | https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/overview |
| S17 | T0/T3 | DAMA-DMBOK | DAMA International | data management body of knowledge、data governance 共通言語 | https://dama.org/learning-resources/dama-data-management-body-of-knowledge-dmbok/ |
| S18 | T0/T3 | DCAM | EDM Council | mature data management function、評価指標、ベンチマーク | https://edmcouncil.org/frameworks/dcam/ |
| S19 | T0 | Privacy Framework | NIST | privacy risk management、privacy by design、mapping | https://www.nist.gov/privacy-framework |
| S20 | T0 | Privacy Principles | OECD | collection limitation, purpose specification, use limitation, safeguards, accountability など | https://www.oecd.org/en/topics/privacy-principles.html |
| S21 | T0 | ISO/IEC 27701:2025 Privacy Information Management | ISO | PIMS、PII controller/processor、accountability、evidence-based privacy management | https://www.iso.org/standard/27701 |
| S22 | T0 | ISO 31022 Legal Risk Management | ISO | 法的リスク管理、ISO 31000 補完 | https://www.iso.org/standard/69295.html |
| S23 | T0/T3 | Contract Management Standard | WorldCC | contract practice の統一フレームワーク、共通言語 | https://www.worldcc.com/Research/CCM-Institute/Contract-Management-Standard |
| S24 | T0/T3 | Cybersecurity Supply Chain Risk Management SP 800-161 | NIST | C-SCRM、サプライチェーンリスク識別・評価・低減 | https://csrc.nist.gov/pubs/sp/800/161/r1/upd1/final |
| S25 | T0 | ISO 44001 Collaborative Business Relationship Management | ISO | 協働的ビジネス関係の識別・開発・管理 | https://www.iso.org/standard/72798.html |
| S26 | T3 | CLOC Core 12 | Corporate Legal Operations Consortium | legal operations の成熟度評価と改善目標 | https://cloc.org/cloc-core-12/ |
| S27 | T0 | ISO/IEC 27001 Information Security Management Systems | ISO | ISMS、情報セキュリティリスク管理、継続改善 | https://www.iso.org/standard/27001 |
| S28 | T1 | Controller / Processor obligations | European Commission | controller/processor 役割、契約上の義務分担 | https://commission.europa.eu/law/law-topic/data-protection/rules-business-and-organisations/obligations/controllerprocessor/what-data-controller-or-data-processor_en |
| S29 | T5 | Blackbaud SEC enforcement release | SEC | 開示管理・経営者報告の失敗証拠 | https://www.sec.gov/newsroom/press-releases/2023-48 |
| S30 | T5 | Blackbaud FTC final order | FTC | 不要データ保持、遅延通知、情報セキュリティプログラム欠陥の失敗証拠 | https://www.ftc.gov/news-events/news/press-releases/2024/05/ftc-finalizes-order-blackbaud-related-allegations-firms-security-failures-led-data-breach |

---

## 4. Frontier Candidate Scoring

| Candidate family | 主に効くレイヤー | Performance | Adoption | Artifact richness | Peer validation | Recency | Transferability | Failure evidence | Score / 100 | 採用判断 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| NIST CSF/RMF/SP 800-53/SP 800-161 | 24.01, 24.02, 24.04, 24.10, 24.11, 24.14 | 5 | 5 | 5 | 5 | 5 | 5 | 4 | 98 | 中核採用。governance/risk/control/supply-chain の backbone。 |
| ISO management system family | 24.02, 24.04, 24.06, 24.11, 24.12 | 5 | 5 | 4 | 5 | 4 | 5 | 3 | 90 | 標準語彙と監査可能な management system の核。 |
| ISACA COBIT | 24.01 | 5 | 5 | 4 | 5 | 4 | 5 | 3 | 88 | IT governance objective の体系化に採用。 |
| IIA Global Internal Audit Standards | 24.03 | 5 | 5 | 4 | 5 | 5 | 4 | 4 | 90 | 監査の独立性・実施・報告に採用。 |
| FinOps Foundation + cloud provider cost frameworks | 24.08, 24.09 | 5 | 5 | 5 | 4 | 5 | 5 | 3 | 91 | cost/usage/business value の接続に採用。 |
| OpenChain + ISO/IEC 19770 | 24.06, 24.07 | 4 | 4 | 5 | 5 | 5 | 5 | 4 | 88 | asset/license/OSS compliance の実装に採用。 |
| DAMA-DMBOK + EDM DCAM | 24.10 | 4 | 4 | 4 | 4 | 5 | 4 | 3 | 80 | data governance の operating model と maturity に採用。 |
| WorldCC + ISO 44001 + CLOC | 24.12, 24.13, 24.14 | 4 | 4 | 4 | 4 | 5 | 4 | 3 | 80 | legal/contract/vendor の lifecycle と成熟度に採用。 |
| SEC/FTC Blackbaud enforcement | 24.02, 24.03, 24.11, 24.14 | 4 | 3 | 4 | 5 | 5 | 4 | 5 | 82 | failure-informed controls と開示エスカレーション設計に採用。 |

---

## 5. Evidence Map: Critical Claims

| Claim ID | Layer | Claim | Evidence | Confidence |
|---|---:|---|---|---|
| C24-01-1 | 24.01 | governance は経営監督、リスク管理、管理目的、所有者を結合する。 | S01, S03, S04 | A |
| C24-02-1 | 24.02 | compliance は義務リストではなく、確立・実装・評価・維持・改善される management system である。 | S05, S08, S27 | A |
| C24-03-1 | 24.03 | internal audit は独立性、戦略/資源、engagement planning/execution/reporting を持つ独立保証機能として設計される。 | S06 | A |
| C24-04-1 | 24.04 | risk management は identification, analysis, evaluation, treatment, monitoring, communication の循環であり、governance/strategy/planning/reporting に埋め込む。 | S07, S02, S01 | A |
| C24-05-1 | 24.05 | change enablement は成功する変更数を最大化しつつ、リスク評価・承認・スケジュール管理で統制する。 | S09, S08 | A |
| C24-06-1 | 24.06 | ITAM は資産 inventory だけでなく、所有権、lifecycle、要件適合性を持つ management system である。 | S10, S01, S27 | A |
| C24-07-1 | 24.07 | OSS/license compliance は key process、役割責任、義務管理を明示する program として設計する。 | S11, S10 | A |
| C24-08-1 | 24.08 | IT cost management は cost visibility、attribution、unit metrics、budget/anomaly/optimization を組み合わせる。 | S14, S15, S16 | A |
| C24-09-1 | 24.09 | FinOps は Inform/Optimize/Operate を反復し、finance・engineering・product の分散意思決定を調整する operating model である。 | S12, S13 | A |
| C24-10-1 | 24.10 | data governance は data asset を戦略・規制・品質・利用価値に接続し、共通語彙・所有権・成熟度指標を持つ。 | S17, S18 | A |
| C24-11-1 | 24.11 | privacy は個人データ処理の目的、最小化、権利、accountability、processor/controller 役割を統制する。 | S19, S20, S21, S28 | A |
| C24-12-1 | 24.12 | legal risk は ISO 31000 型のリスク管理を法務領域に適用し、法的リスクを識別・評価・処理する。 | S22, S07, S26 | A |
| C24-13-1 | 24.13 | contract management は共通言語と lifecycle framework で、条項、承認、義務、変更、更新/終了を管理する。 | S23, S25, S28 | A |
| C24-14-1 | 24.14 | vendor management は third-party / supply-chain risk を識別・評価・低減し、契約・監視・退出条件へ flowdown する。 | S24, S03, S25 | A |
| C-F-1 | 24.02/24.11/24.14 | 開示・通知・証拠エスカレーションの失敗は重大な regulatory failure になり得る。 | S29, S30 | A |

---

## 6. Cross-Layer Pattern Library

| Pattern ID | Pattern | Applies to | Description | Preconditions | Tradeoffs | Confidence |
|---|---|---|---|---|---|---|
| P01 | Governance-anchored control graph | 24 | すべての統制を objective / owner / evidence / exception / metric / review cadence に接続する。 | 経営監督、control taxonomy、system of record | 初期設計が重い。運用しないと文書棚になる。 | A |
| P02 | Risk-based tiering | 24.04–24.06, 24.10–24.14 | 重要度、影響、規制性、外部依存、データ感度で対象を tiering し、審査深度を変える。 | risk scoring rubric、asset/data/vendor inventory | 低リスク分類の誤りが blind spot になる。 | A |
| P03 | Evidence-as-data | 24.02–24.03 | 監査証跡を control object として構造化し、証拠収集を自動化する。 | evidence schema、control owner、collector integration | 自動証拠が妥当性を保証するわけではない。 | B |
| P04 | Lifecycle closure | 24.05–24.14 | 変更、資産、契約、ベンダー、データ、ライセンスを request → approval → operation → review → retirement で閉じる。 | lifecycle state model、RACI、system workflow | 状態遷移が複雑化しやすい。 | A |
| P05 | Business-value-linked cost governance | 24.08–24.09 | IT/cloud cost を workload, product, customer, margin, unit economics に結びつける。 | tagging/allocation、FinOps persona、usage telemetry | 配賦争いが増える。過度な最適化は速度を落とす。 | A |
| P06 | Obligation flowdown | 24.11–24.14 | privacy/legal/security/vendor 義務を契約条項、委託先要件、監査権、通知、終了処理へ流し込む。 | obligation register、clause library、vendor inventory | 条項が強すぎると調達速度が落ちる。 | A |
| P07 | Failure-informed escalation | 24.01–24.03, 24.11, 24.14 | 重大情報が上級管理者、開示管理、監査委員会へ到達するルートを明示する。 | severity model、disclosure committee、incident/legal/privacy escalation | 低レベル noise が増える可能性。 | A |

---

# 7. Clone Specs by Layer

## 24.01 Enterprise / IT Governance

### Definition
IT、セキュリティ、データ、クラウド、法務・コンプライアンス関連の意思決定権限、監督責任、リスク選好、統制目的、例外権限を定義し、経営目標と実行統制を接続するレイヤー。

### Frontier Exemplars
- **NIST CSF 2.0 + RMF**: GOVERN 機能と risk management cycle を通じ、サイバーリスクを経営レベルの成果分類と継続監視に接続する。Evidence: S01, S02.
- **ISACA COBIT**: enterprise IT governance を governance objectives / management objectives / design guide / implementation guide として体系化する。Evidence: S04.
- **SEC Item 106**: public company の cybersecurity risk management、third-party risk、board oversight、management role を開示対象にする。Evidence: S03.

### Evidence Map
| Claim | Evidence | Confidence |
|---|---|---|
| governance は、方針文書ではなく、監督・責任・リスク・統制・報告の decision system である。 | S01, S03, S04 | A |
| third-party cybersecurity risk も経営レベル governance に含めるべきである。 | S03, S24 | A |
| governance object は objective, owner, metric, evidence, exception を持つべきである。 | S01, S02, S04 | B |

### Core Philosophy
経営が許容するリスク、投資優先順位、統制の厳しさ、例外許容条件を明示し、個別部門が勝手に「安全」「安い」「速い」を判断しない構造にする。

### Decision Model
- 入力: 事業戦略、regulatory obligations、risk appetite、material incidents、audit findings、asset/vendor/data criticality、cost pressure。
- 判断基準: business value、material risk、法令/契約義務、顧客影響、可監査性、説明責任、費用対効果。
- 優先順位: 1) 法令・安全・顧客信頼、2) 事業継続、3) 変化速度、4) コスト最適化。
- 禁止事項: owner 不明の統制、例外期限なしの waiver、board/management 報告経路なしの重大リスク、第三者依存の未登録。
- 例外条件: 緊急対応、規制解釈変更、重大顧客要請。ただし期限、承認者、補償統制、再評価日を必須にする。
- 承認者: Board/Audit Committee、CEO/CIO/CISO/CRO、GRC steering committee。
- 見直し頻度: board pack 四半期、risk/control review 月次、重大インシデント時は臨時。

### Operating Model
- 役割: Board oversight、executive risk committee、GRC owner、domain control owner、internal audit。
- プロセス: policy approval、control objective definition、risk appetite setting、exception review、management reporting。
- 会議体: quarterly governance committee、monthly risk/control council、incident disclosure committee。
- ツール: GRC platform、policy repository、risk register、control/evidence graph、board reporting dashboard。
- 成果物: governance charter、risk appetite statement、control taxonomy、RACI、exception register、board pack。

### Technical / Business Specification
- `GovernanceObject` schema: `id, objective, domain, owner, approver, linked_risks, linked_controls, metrics, evidence_sources, exceptions, review_cadence, status`。
- すべての重大 asset / vendor / contract / data domain / cloud workload は少なくとも 1 つの GovernanceObject に接続する。
- 例外は `temporary / compensating control / residual risk accepted / expiry date` を必須属性にする。

### Metrics
Policy coverage、control objective coverage、risk appetite breach count、exception aging、board pack SLA、material risk escalation time、ownerless control count、audit finding closure rate。

### Failure Modes
- governance が委員会資料に閉じ、system of record と接続されない。
- 重大セキュリティ/プライバシー情報が disclosure management へ上がらない。Blackbaud 事例は、情報連携欠陥が開示・通知・信頼失墜に繋がることを示す。Evidence: S29, S30.
- third-party risk が procurement 内で閉じ、board/management oversight に乗らない。

### Anti-patterns
「全社方針を作ったので governance 完了」、例外期限なし、RACI だけで system owner がいない、KPI が会議開催数だけ、CISO/CRO の veto 権限が不明。

### Maturity Model
- Level 0: 方針・責任不在。
- Level 1: 個別部門の暗黙判断。
- Level 2: governance charter と RACI がある。
- Level 3: risk/control/objective が system of record で接続される。
- Level 4: 例外・証拠・KRI が自動集計され、board reporting に反映。
- Level 5: 事業戦略変更、規制変更、インシデント学習が governance model を自律更新する。

### Clone Implementation Guide
1. 主要 governance domains を `Cybersecurity / Privacy / Data / Cloud cost / Vendor / Legal / Change / Asset` に分ける。
2. 各 domain に objective owner と executive sponsor を置く。
3. risk appetite と materiality threshold を定義する。
4. GRC台帳に risk-control-evidence-exception の最小スキーマを実装する。
5. board/committee pack を evidence graph から自動生成する。

### Confidence & Unknowns
- 確度A: NIST/COBIT/SEC による governance, risk, oversight の中核構造。
- 確度B: GovernanceObject schema は複数標準の抽象化。
- 不明点: 個別企業の board cadence、veto rights、materiality threshold は公開情報だけでは確定できない。

---

## 24.02 Compliance Management

### Definition
法令、規制、標準、契約、社内方針から生じる義務を、統制、証拠、所有者、評価頻度、是正措置へ変換するレイヤー。

### Frontier Exemplars
- **ISO 37301**: compliance management system の確立、実装、評価、維持、改善を規定する。Evidence: S05.
- **NIST SP 800-53 / ISO 27001**: security/privacy controls と ISMS を通じ、統制の設計・実装・継続改善を支える。Evidence: S08, S27.
- **SEC/FTC enforcement examples**: compliance failure が情報共有・通知・保持・開示の弱さから発生することを示す。Evidence: S29, S30.

### Evidence Map
| Claim | Evidence | Confidence |
|---|---|---|
| compliance は義務管理、統制実装、評価、改善を含む management system である。 | S05 | A |
| security/privacy controls は compliance evidence の実行単位になる。 | S08, S27 | A |
| 開示・通知・保持・証拠管理の欠陥は重大な compliance failure になる。 | S29, S30 | A |

### Core Philosophy
「準拠しているか」を後で確認するのではなく、義務を control object に分解し、日々の運用証拠として自動収集する。

### Decision Model
- 入力: 法令・規制、標準、契約義務、顧客要件、社内方針、監査指摘、インシデント。
- 判断基準: 義務の強制力、罰則/損害、顧客影響、証拠取得可能性、統制成熟度。
- 優先順位: mandatory obligations、material risks、customer commitments、industry standards、internal policies。
- 禁止事項: 義務に owner がない、統制に evidence source がない、監査直前だけの手動証拠収集、期限切れ例外。
- 例外条件: 法解釈未確定、legacy system 制約、移行期間。ただし法務承認・補償統制・期限必須。
- 承認者: CCO、Legal、CISO、control owner、risk committee。
- 見直し頻度: obligation review 四半期、control testing 月次/四半期、規制変更時は臨時。

### Operating Model
- 役割: compliance officer、obligation owner、control owner、evidence owner、legal reviewer、internal audit。
- プロセス: obligation intake → applicability assessment → control mapping → evidence design → testing → exception/remediation。
- ツール: GRC、policy management、contract repository、ticketing、evidence collector、regulatory change tracker。
- 成果物: obligation register、control matrix、compliance calendar、attestation、evidence repository、remediation tracker。

### Technical / Business Specification
- `Obligation` schema: `source, jurisdiction, effective_date, applicability, owner, mapped_controls, evidence_required, testing_frequency, breach_notification_rule`。
- `Control` schema: `objective, procedure, system, owner, evidence_type, test_method, pass/fail criteria, exception_process`。
- 重大義務は `obligation → control → evidence → test result → remediation` の edge を持つ。

### Metrics
Obligation coverage、mapped control ratio、evidence freshness、control test pass rate、exception aging、regulatory change assessment SLA、audit finding recurrence、late notification count。

### Failure Modes
- obligation register が法務内に閉じ、システム運用へ変換されない。
- evidence がスクリーンショット依存で再現性がない。
- 重大違反情報が management disclosure channel へ届かない。
- データ保持義務と最小化義務が整合しない。

### Anti-patterns
「認証取得=コンプライアンス完了」、control owner と evidence owner の混同、監査人向け資料と実運用の乖離、契約義務を regulatory obligation と別台帳に分断。

### Maturity Model
- Level 0: 義務不明。
- Level 1: 法務/監査担当者の個人管理。
- Level 2: obligation register と compliance calendar がある。
- Level 3: control/evidence mapping が標準化される。
- Level 4: 証拠収集・testing・exception aging が自動化。
- Level 5: 規制変更、契約変更、システム変更が compliance impact を自動評価する。

### Clone Implementation Guide
1. 上位20の法令・契約・認証義務を選び、Obligation schema に登録する。
2. 各義務を control objective に分解し、NIST/ISO control catalog と対応付ける。
3. evidence source をシステムログ、設定、承認履歴、契約条項、監査結果へ分ける。
4. 例外承認 workflow と期限切れ escalation を実装する。
5. 四半期ごとに obligation-to-control coverage をレビューする。

### Confidence & Unknowns
- 確度A: ISO 37301、NIST SP 800-53、ISO 27001 の構造。
- 確度B: obligation schema は標準の抽象化。
- 不明点: 各国法令や業界固有規制の具体的適用範囲。

---

## 24.03 Internal Audit & Assurance

### Definition
組織の governance、risk management、control の有効性を独立評価し、経営・監査委員会へ保証と改善勧告を提供するレイヤー。

### Frontier Exemplars
- **IIA Global Internal Audit Standards**: internal audit の目的、倫理、governance、独立性、監査管理、engagement planning/execution/reporting を規定する。Evidence: S06.
- **NIST control assessment / RMF**: control implementation と continuous monitoring を評価可能な evidence structure にする。Evidence: S02, S08.

### Evidence Map
| Claim | Evidence | Confidence |
|---|---|---|
| 内部監査は独立性と監査委員会への説明責任を持つ。 | S06 | A |
| 監査は engagement planning, execution, communication, follow-up の lifecycle を持つ。 | S06 | A |
| control assessment は RMF/control catalog と接続すると再現性が上がる。 | S02, S08 | B |

### Core Philosophy
監査は「過去の不備探し」ではなく、governance/risk/control system が設計通りに機能しているかを独立に検証し、改善を閉じる保証機能である。

### Decision Model
- 入力: enterprise risk register、prior audit findings、regulatory obligations、incident history、material systems/vendors、management requests。
- 判断基準: inherent/residual risk、regulatory materiality、control maturity、change velocity、third-party exposure、財務/顧客影響。
- 優先順位: high materiality/high residual risk、repeat findings、重大変更後、regulator/customer commitments。
- 禁止事項: management による監査範囲の不当制限、監査人が統制 owner を兼ねる、未完了 finding の期限なし延長。
- 例外条件: 緊急経営要請、重大インシデント後の特別監査。
- 承認者: CAE、Audit Committee、監査対象 domain owner は範囲合意のみ。
- 見直し頻度: annual audit plan、quarterly refresh、finding follow-up 月次。

### Operating Model
- 役割: Chief Audit Executive、audit manager、engagement lead、subject matter specialist、management action owner。
- プロセス: risk-based audit planning → engagement planning → evidence request → testing → draft report → management response → remediation follow-up。
- ツール: audit management system、GRC/evidence repository、data analytics、issue tracker。
- 成果物: internal audit charter、annual audit plan、engagement workpaper、audit report、finding tracker、management action plan。

### Technical / Business Specification
- `AuditFinding` schema: `finding_id, control_objective, severity, evidence, root_cause, risk_impact, owner, action_plan, due_date, validation_method, closure_evidence`。
- 監査 finding は必ず risk/control/obligation のいずれかに接続する。
- Repeat finding は severity を自動加重する。

### Metrics
Audit plan completion、high-risk coverage、finding closure SLA、repeat finding rate、management action overdue、audit cycle time、evidence request latency、independence exceptions。

### Failure Modes
- 監査計画が過年度踏襲で risk-based でない。
- finding が action plan なしで報告される。
- control evidence が実運用を表さない。
- 監査が経営監督と切り離され、重大 risk signal を board に届けない。

### Anti-patterns
「三線モデル」の名だけで独立性がない、監査人が実装支援に入りすぎる、low-risk control testing に工数を浪費、finding closure が自己申告のみ。

### Maturity Model
- Level 0: 監査なし。
- Level 1: 規制/顧客要求時のみ監査。
- Level 2: annual audit plan と charter がある。
- Level 3: risk-based planning と標準 workpaper。
- Level 4: evidence analytics と continuous auditing。
- Level 5: 監査結果が governance/control design を継続更新する。

### Clone Implementation Guide
1. Internal audit charter を作り、監査委員会/経営への報告経路を定義する。
2. enterprise risk register と compliance obligations を監査計画に接続する。
3. AuditFinding schema と closure evidence の要件を固定する。
4. high-risk controls から data-driven testing を開始する。
5. quarterly に repeat/overdue/material finding を governance committee へ報告する。

### Confidence & Unknowns
- 確度A: IIA Standards の監査構造。
- 確度B: NIST controls との evidence integration。
- 不明点: 具体的な監査委員会構成、監査範囲、外部監査人との分担。

---

## 24.04 Enterprise Risk Management

### Definition
組織が直面する戦略、運用、サイバー、法務、財務、第三者、データ、コンプライアンスのリスクを識別・分析・評価・処理・監視・報告するレイヤー。

### Frontier Exemplars
- **ISO 31000**: risk identification, analysis, evaluation, treatment, monitoring, communication を governance/strategy/planning/reporting に統合する。Evidence: S07.
- **NIST RMF / CSF**: cybersecurity/privacy risk を categorization, controls, authorization, continuous monitoring へ展開する。Evidence: S01, S02.
- **SEC Item 106**: material cybersecurity risks と processes の開示を求める。Evidence: S03.

### Evidence Map
| Claim | Evidence | Confidence |
|---|---|---|
| ERM は一回限りの risk assessment ではなく、識別から監視までの循環である。 | S07 | A |
| cybersecurity risk は組織のERM/統制/継続監視に統合される。 | S01, S02, S03 | A |
| third-party risk は enterprise risk として扱う必要がある。 | S03, S24 | A |

### Core Philosophy
リスクを「回避すべき悪」ではなく、事業目的に対する不確実性として扱い、受容・低減・移転・回避を明示的に選択する。

### Decision Model
- 入力: strategic objectives、assets、vendors、data sensitivity、incidents、regulatory obligations、financial exposure、change plans。
- 判断基準: likelihood、impact、velocity、detectability、control effectiveness、materiality、risk appetite alignment。
- 優先順位: materiality 高、regulatory impact 高、customer trust impact 高、control gap 大、concentration risk 高。
- 禁止事項: risk owner 不明、treatment plan なしの high residual risk、評価基準の恣意変更。
- 例外条件: 経営が residual risk を受容。ただし期限、補償統制、再評価日、承認者を明記。
- 承認者: risk owner、CRO/CISO/Legal、executive risk committee。
- 見直し頻度: high risk 月次、medium risk 四半期、重大変更/インシデント時は臨時。

### Operating Model
- 役割: CRO、risk domain owner、control owner、risk analyst、executive committee。
- プロセス: risk identification → scoring → treatment selection → control mapping → residual risk approval → monitoring → reporting。
- ツール: risk register、GRC、KRI dashboard、incident database、vendor risk platform。
- 成果物: risk taxonomy、risk appetite statement、risk register、treatment plan、KRI report、risk acceptance memo。

### Technical / Business Specification
- `Risk` schema: `category, scenario, causes, consequences, inherent_score, controls, residual_score, owner, treatment, due_date, KRI, linked_assets/vendors/data/contracts`。
- risk scoring は impact と likelihood に加え、velocity と detectability を持つ。
- high residual risk は governance committee 承認がない限り `accepted` にできない。

### Metrics
Risk register coverage、high residual risk count、KRI breach、treatment overdue、risk acceptance aging、control effectiveness trend、loss event frequency、third-party concentration risk。

### Failure Modes
- annual risk assessment が形式化し、重大変更や新規ベンダーを反映しない。
- リスク評価が数値風だが calibration されていない。
- treatment plan が予算・owner・期限を持たない。
- cyber/privacy/vendor/legal risk が別々の台帳で相互影響を見ない。

### Anti-patterns
Risk heatmap だけで意思決定しない、risk acceptance を実質放置に使う、低減不可能なリスクを control gap として扱い続ける、risk appetite を事業部が知らない。

### Maturity Model
- Level 0: リスク未定義。
- Level 1: 個別事故後に対応。
- Level 2: risk register と annual assessment。
- Level 3: risk taxonomy と treatment workflow。
- Level 4: KRI、control effectiveness、incident/loss data が統合。
- Level 5: 事業計画、投資、変更、契約、ベンダー判断に risk signal が自動反映。

### Clone Implementation Guide
1. risk taxonomy を `strategic / operational / cyber / privacy / legal / financial / third-party / compliance` に分ける。
2. impact scoring を customer, financial, regulatory, availability, reputation の5軸で定義する。
3. risk-control-owner-evidence の関係を GRC に実装する。
4. high residual risk の acceptance workflow を作る。
5. KRI dashboard を executive committee に月次提出する。

### Confidence & Unknowns
- 確度A: ISO 31000、NIST RMF/CSF、SEC rule の中核構造。
- 確度B: velocity/detectability を含む scoring は実務抽象化。
- 不明点: 事業固有の risk appetite threshold。

---

## 24.05 Change Governance / Change Enablement

### Definition
システム、プロセス、契約、データ、クラウド構成、統制に対する変更を、リスク評価、承認、スケジュール、証拠、ロールバック条件で管理するレイヤー。

### Frontier Exemplars
- **ITIL 4 Change Enablement**: 変更成功数の最大化を目的に、risk assessment、authorization、schedule management を行う。Evidence: S09.
- **NIST SP 800-53 Configuration/Change Controls**: security/privacy controls として変更・構成管理を扱う。Evidence: S08.

### Evidence Map
| Claim | Evidence | Confidence |
|---|---|---|
| change enablement は速度を止める統制ではなく、成功する変更数を最大化する仕組みである。 | S09 | A |
| 変更には risk assessment、authorization、schedule、status communication が必要である。 | S09 | A |
| security/privacy control catalog と接続することで、変更が統制証拠になる。 | S08 | B |

### Core Philosophy
変更統制はリリース速度と安全性のトレードオフを管理する。先端運用では、すべての変更をCABで手動審査せず、standard change、normal change、emergency change をリスクで分ける。

### Decision Model
- 入力: change request、affected services/assets/data/vendors、risk score、test evidence、rollback plan、deployment window、customer impact。
- 判断基準: blast radius、reversibility、test coverage、security/privacy impact、SLO impact、regulatory impact、dependency risk。
- 優先順位: 重大障害/脆弱性修正、customer-impacting changes、high-risk infrastructure changes、routine automated changes。
- 禁止事項: owner なし変更、rollback plan なし high-risk change、test evidence なし production change、emergency bypass の常態化。
- 例外条件: active incident、critical vulnerability、regulatory deadline。ただし post-implementation review 必須。
- 承認者: change authority、service owner、security/privacy/legal reviewer、高リスク時は CAB または executive approver。
- 見直し頻度: change review 週次、emergency review 随時、failure trend 月次。

### Operating Model
- 役割: change manager、service owner、release manager、SRE、security reviewer、CAB。
- プロセス: request → classification → impact/risk assessment → approval → deploy → verify → close/PIR。
- ツール: ITSM、CI/CD、feature flag、configuration management、observability、incident management。
- 成果物: change record、risk assessment、approval log、deployment evidence、rollback evidence、post-implementation review。

### Technical / Business Specification
- `ChangeRecord` schema: `change_id, type, affected_ci, risk_score, approver, test_evidence, security_review, scheduled_window, rollback_plan, deployment_result, incidents_linked, PIR_required`。
- low-risk standard changes は policy-as-code で自動承認できる。
- high-risk changes は approval + verification + rollback drill を必須にする。

### Metrics
Change success rate、change failure rate、emergency change ratio、rollback rate、lead time for change、approval cycle time、PIR completion、change-linked incident rate。

### Failure Modes
- すべての変更を同じ承認経路に乗せ、速度と統制の両方を失う。
- emergency change が通常リリースの抜け道になる。
- rollback plan が文書だけで検証されていない。
- change record と CI/CD evidence が分断される。

### Anti-patterns
CAB が技術詳細のレビュー会になる、標準変更を定義しない、変更失敗率を測らない、顧客/規制/プライバシー影響を後から評価する。

### Maturity Model
- Level 0: 変更記録なし。
- Level 1: 手動承認のみ。
- Level 2: change record とCAB。
- Level 3: risk-based change classification。
- Level 4: CI/CD evidence、automated approvals、policy-as-code。
- Level 5: SLO/risk/cost/security signals に基づく adaptive change governance。

### Clone Implementation Guide
1. 変更分類を `standard / normal / emergency / major` に固定する。
2. blast radius と reversibility を risk scoring に入れる。
3. CI/CD から deployment evidence を ITSM に自動連携する。
4. emergency change の post-review と再発防止を義務化する。
5. change-linked incident を毎月分析する。

### Confidence & Unknowns
- 確度A: ITIL 4 change enablement の目的と設計原則。
- 確度B: policy-as-code 自動承認はクラウド/DevOps実務からの抽象化。
- 不明点: 各社固有の CAB 構成、risk threshold。

---

## 24.06 IT Asset Management

### Definition
ハードウェア、ソフトウェア、クラウドリソース、SaaS、データ基盤、構成要素を、所有権、状態、ライフサイクル、リスク、費用、ライセンス義務と接続して管理するレイヤー。

### Frontier Exemplars
- **ISO/IEC 19770-1**: IT asset management system の要求事項を規定し、組織の ITAM 能力評価にも使える。Evidence: S10.
- **NIST CSF/ISO 27001**: security/privacy risk management の前提として asset visibility を必要とする。Evidence: S01, S27.

### Evidence Map
| Claim | Evidence | Confidence |
|---|---|---|
| ITAM は inventory だけでなく、management system として定義される。 | S10 | A |
| 資産可視性は security/risk/compliance の前提である。 | S01, S27 | A |
| asset record は owner、criticality、lifecycle、cost、license、risk と接続すべきである。 | S10, S01, S14 | B |

### Core Philosophy
「何を持っているか」を知るだけでなく、「誰が責任を持ち、何のために使い、どのリスク・費用・義務を持ち、いつ終了するか」を管理する。

### Decision Model
- 入力: procurement record、discovery scan、cloud inventory、CMDB、license entitlement、vulnerability data、cost data、contract data。
- 判断基準: business criticality、data sensitivity、security exposure、license obligation、cost impact、lifecycle status、ownership clarity。
- 優先順位: internet-facing/high-data/high-cost/regulated assets、ownerless assets、end-of-life assets、unused resources。
- 禁止事項: ownerless production asset、unclassified asset、unmanaged SaaS、unsupported/end-of-life asset without exception。
- 例外条件: legacy dependency、temporary project asset、forensic hold。期限・補償統制・廃止計画を必須にする。
- 承認者: ITAM owner、service owner、security、finance、procurement。
- 見直し頻度: discovery 日次/週次、ownership review 月次、lifecycle review 四半期。

### Operating Model
- 役割: ITAM manager、configuration manager、service owner、procurement、security、finance。
- プロセス: discover → classify → assign owner → reconcile → monitor lifecycle/cost/license → retire。
- ツール: CMDB、asset discovery、cloud inventory、SaaS management、endpoint management、ITSM、license management。
- 成果物: asset inventory、CMDB、ownership map、criticality classification、retirement record、reconciliation report。

### Technical / Business Specification
- `Asset` schema: `asset_id, type, owner, business_service, environment, criticality, data_classification, cost_center, license_ref, vendor_ref, contract_ref, lifecycle_state, last_seen, risk_score`。
- discovery source と financial/procurement source の reconciliation を行う。
- asset lifecycle state は `requested / approved / active / dormant / exception / retired` に統一する。

### Metrics
Inventory coverage、ownerless asset count、unknown asset rate、stale asset rate、EOL asset count、cloud orphan resources、asset-to-cost allocation ratio、retirement SLA。

### Failure Modes
- CMDB が手入力で陳腐化する。
- procurement にある SaaS と security inventory が一致しない。
- unused cloud resources が cost waste になる。
- EOL assets が vulnerability と compliance risk を生む。

### Anti-patterns
asset = hardware だけ、クラウド ephemeral resource を除外、owner が部署名だけ、retirement 証拠がない、ITAM と license/cost/risk が分断。

### Maturity Model
- Level 0: 資産不明。
- Level 1: 手動台帳。
- Level 2: inventory と owner 登録。
- Level 3: CMDB/discovery/reconciliation。
- Level 4: asset-risk-cost-license の統合。
- Level 5: lifecycle automation と policy-driven retirement。

### Clone Implementation Guide
1. 主要 asset types を `endpoint / server / cloud resource / SaaS / database / network / repository` に分ける。
2. discovery と procurement と finance のデータを突合する。
3. ownerless / stale / high-cost / high-risk assets を initial cleanup backlog にする。
4. asset lifecycle と change/vendor/contract/license record を接続する。
5. monthly reconciliation を governance metric にする。

### Confidence & Unknowns
- 確度A: ISO/IEC 19770-1 のITAM管理システム構造。
- 確度B: asset-to-risk-cost-license schema は標準とクラウド実務の統合。
- 不明点: 各社の discovery カバレッジ、ephemeral resource 管理方式。

---

## 24.07 License & OSS Compliance

### Definition
商用ソフトウェア、SaaS、OSS、コンポーネント、ライブラリの使用権、制約、配布義務、表示義務、ソース提供義務、契約義務、監査リスクを管理するレイヤー。

### Frontier Exemplars
- **OpenChain ISO/IEC 5230**: OSSライセンス要求を管理するための key process、役割責任、持続可能性を示す。Evidence: S11.
- **ISO/IEC 19770-1**: IT asset と license entitlement/reconciliation の management system を支える。Evidence: S10.

### Evidence Map
| Claim | Evidence | Confidence |
|---|---|---|
| OSS license compliance は明示的な process、roles、responsibilities を必要とする。 | S11 | A |
| license compliance は ITAM と結合し、使用実態と権利を突合する。 | S10, S11 | A |
| software distribution では license notice / source obligations / attribution が成果物になる。 | S11 | A |

### Core Philosophy
ソフトウェア利用を「購入済み/無料」ではなく、使用形態・配布形態・変更有無・顧客提供形態に応じた権利義務として管理する。

### Decision Model
- 入力: SBOM、dependency scan、commercial entitlement、deployment count、distribution model、contract terms、procurement record。
- 判断基準: license type、copyleft strength、distribution exposure、modification、SaaS/internal use、customer contractual obligations、audit risk。
- 優先順位: externally distributed products、strong copyleft components、commercial overuse risk、unknown license、critical dependencies。
- 禁止事項: unknown license の出荷、entitlement 超過、notice omission、source obligation 未履行、ライセンス例外の未承認。
- 例外条件: legal approved exception、customer-specific distribution、security patch urgency。
- 承認者: legal IP counsel、OSS review board、engineering owner、procurement/ITAM。
- 見直し頻度: build/release ごと、commercial license reconciliation 月次/四半期、policy review 年次。

### Operating Model
- 役割: OSS compliance lead、legal counsel、engineering owner、release manager、procurement、ITAM。
- プロセス: component intake → scan → license classification → obligation decision → approval → notice/source package → release evidence。
- ツール: SCA/SBOM tool、license management、artifact repository、CI/CD gate、procurement system。
- 成果物: approved component list、SBOM、license notices、source offer/package、entitlement report、exception register。

### Technical / Business Specification
- `SoftwareComponent` schema: `name, version, source, license, dependency_path, product, distribution_mode, obligation, approval_status, notice_required, source_required, owner`。
- release gate は unknown/prohibited license を block する。
- commercial license は deployment/usage count と entitlement を定期突合する。

### Metrics
Unknown license count、prohibited license violations、SBOM coverage、license review SLA、notice completeness、commercial overuse exposure、exception aging、component approval reuse rate。

### Failure Modes
- OSS scan はあるが legal decision が記録されない。
- SBOM と出荷成果物が一致しない。
- commercial SaaS の seat overage/underuse を検知できない。
- dependency transitive license を無視する。

### Anti-patterns
「OSSは無料なので承認不要」、CI scan だけで義務履行完了、商用 license と OSS license を別部門で分断、notice/source package を release artifact として管理しない。

### Maturity Model
- Level 0: ライセンス管理なし。
- Level 1: 問題発生時に法務確認。
- Level 2: approved license list と手動 review。
- Level 3: SCA/SBOM と release gate。
- Level 4: obligation automation、commercial reconciliation、exception workflow。
- Level 5: product/customer/distribution context に応じた dynamic license governance。

### Clone Implementation Guide
1. allowed/restricted/prohibited license taxonomy を定義する。
2. SCA を CI/CD に接続し、unknown/prohibited を gate する。
3. SBOM と license notice を release artifact にする。
4. commercial entitlement と actual usage を月次突合する。
5. OSS exception board と legal signoff を実装する。

### Confidence & Unknowns
- 確度A: OpenChain/ISO 19770 の中核構造。
- 確度B: CI/CD gate と schema は実装抽象化。
- 不明点: 個別ライセンス解釈、契約上の特約、特定国の法的解釈。

---

## 24.08 IT Cost Management

### Definition
IT支出、クラウド支出、SaaS支出、ライセンス費用、運用費、人件費配賦を、予算、実績、利用量、事業価値、単位経済性、異常検知、最適化施策で管理するレイヤー。

### Frontier Exemplars
- **AWS Well-Architected Cost Optimization**: cost visibility、usage metrics、allocation、billing/cost tools を提示する。Evidence: S14.
- **Google Cloud Cost Optimization**: cloud spend を business value に合わせ、必要なリソースだけを継続的に調整する。Evidence: S15.
- **Microsoft Cloud Adoption Framework**: cloud governance/management のロードマップ内で cost/governance を扱う。Evidence: S16.

### Evidence Map
| Claim | Evidence | Confidence |
|---|---|---|
| cost management は visibility と attribution が前提である。 | S14 | A |
| cloud spend は business value と継続的最適化に接続すべきである。 | S15 | A |
| cloud adoption/governance は cost, security, management を統合して扱う。 | S16 | A |

### Core Philosophy
ITコストを「削減対象」ではなく、事業価値を生む資源消費として扱う。削減だけでなく、speed, reliability, security, revenue, margin との最適点を探す。

### Decision Model
- 入力: invoice、usage telemetry、tag/allocation data、budget、forecast、product revenue、asset/license/vendor data、optimization recommendations。
- 判断基準: business value、unit cost、budget variance、utilization、waste、commitment coverage、gross margin impact、risk of underprovisioning。
- 優先順位: unallocated spend、high-growth spend、idle resources、license waste、critical workload cost、budget breach。
- 禁止事項: untagged cloud spend、ownerless cost center、削減のみを目的に reliability/security を落とす、利用量不明の契約更新。
- 例外条件: growth investment、seasonal spike、incident response、regulated capacity requirement。
- 承認者: CFO/FP&A、CIO、product owner、platform owner、FinOps。
- 見直し頻度: anomaly daily、budget monthly、forecast monthly、unit economics quarterly。

### Operating Model
- 役割: IT finance、FP&A、platform owner、service owner、procurement、FinOps。
- プロセス: collect invoice/usage → allocate → analyze variance → identify optimization → approve action → track savings/value。
- ツール: cloud cost management、BI、budgeting、asset/license management、contract repository。
- 成果物: cost allocation model、showback/chargeback report、budget variance report、optimization backlog、unit cost dashboard。

### Technical / Business Specification
- `CostObject` schema: `provider, account/subscription, service, resource_id, tag_owner, product, environment, cost_center, unit_metric, budget, forecast, actual, anomaly_status, optimization_action`。
- `minimum allocation rule`: production workload の 95% 以上を owner/product/cost_center に配賦する。
- optimization action は `estimated_savings, risk, owner, due_date, realized_savings` を持つ。

### Metrics
Allocation coverage、untagged spend、budget variance、forecast accuracy、unit cost、idle resource cost、realized savings、SaaS/license utilization、cost anomaly MTTD/MTTR。

### Failure Modes
- cost visibility が請求書単位で止まり、product/workload へ配賦されない。
- 削減施策が reliability/security と衝突する。
- 予約/commitment を過剰購入する。
- コスト異常検知はあるが owner action がない。

### Anti-patterns
「クラウド費用=インフラ部門の問題」、tagging だけを目的化、savings target のみで value metric がない、SaaS shelfware を見ない。

### Maturity Model
- Level 0: 請求後に把握。
- Level 1: 部門別予算のみ。
- Level 2: cloud/SaaS cost visibility と基本配賦。
- Level 3: unit cost、budget variance、optimization backlog。
- Level 4: anomaly detection、forecast、automated rightsizing recommendations。
- Level 5: product P&L、customer economics、real-time cost guardrails に統合。

### Clone Implementation Guide
1. cloud/SaaS/license の top spend を抽出する。
2. owner/product/cost_center tagging policy を定義する。
3. unallocated spend を initial remediation backlog にする。
4. monthly cost review で budget variance と optimization action を追う。
5. unit cost metric を product/service ごとに1つ以上設定する。

### Confidence & Unknowns
- 確度A: AWS/Google/Microsoft 公式 cost guidance。
- 確度B: allocation coverage 95% は実務上の推奨閾値であり、標準値ではない。
- 不明点: 具体的な chargeback 方針、会計処理、税務・地域差。

---

## 24.09 FinOps / Cloud Financial Management

### Definition
クラウド支出を finance、engineering、product、procurement の共同意思決定に変換し、Inform / Optimize / Operate の反復でビジネス価値とクラウド利用を整合させるレイヤー。

### Frontier Exemplars
- **FinOps Framework**: scopes, principles, personas, phases, maturity, domains, capabilities を持つ operating model。Evidence: S12.
- **FinOps Phases**: Inform, Optimize, Operate の反復で現状把握、改善機会、価値実現を進める。Evidence: S13.
- **Cloud provider cost frameworks**: tagging/allocation, monitor usage, optimize over time を実装面で支える。Evidence: S14, S15.

### Evidence Map
| Claim | Evidence | Confidence |
|---|---|---|
| FinOps はクラウド財務管理の operating model である。 | S12 | A |
| FinOps は Inform / Optimize / Operate の反復サイクルを持つ。 | S13 | A |
| FinOps は engineering と finance の共同責任にする必要がある。 | S12, S14, S15 | A |

### Core Philosophy
クラウドの可変費構造では、購入後統制では遅い。利用者が費用シグナルを見ながら設計・運用判断を変える分散型ガバナンスが必要である。

### Decision Model
- 入力: cloud usage、allocation tags、unit economics、forecast、commitment utilization、architecture changes、business KPIs。
- 判断基準: value per cost、elasticity、commitment risk、waste、performance/reliability tradeoff、engineering effort、customer impact。
- 優先順位: high-value visibility gaps、large waste pools、commitment opportunities、unit cost regressions、budget anomalies。
- 禁止事項: unallocated spend、rightsizing without SLO review、commitment purchase without forecast confidence、optimization without owner。
- 例外条件: launch/growth period、incident resiliency、regulatory capacity、strategic experimentation。
- 承認者: FinOps lead、engineering owner、product owner、finance owner。
- 見直し頻度: daily anomaly、weekly optimization review、monthly forecast、quarterly commitment strategy。

### Operating Model
- 役割: FinOps practitioner、engineering owner、finance analyst、product manager、procurement、platform team。
- プロセス: Inform → allocate/benchmark/report、Optimize → rightsizing/commitments/architecture、Operate → policy/automation/accountability。
- ツール: cloud cost platform、BI、tagging policy、budget/anomaly alert、architecture review。
- 成果物: FinOps charter、allocation policy、unit economics dashboard、optimization backlog、commitment plan、forecast report。

### Technical / Business Specification
- `FinOpsDecision` schema: `workload, owner, unit_metric, current_cost, business_value, optimization_option, savings_estimate, engineering_effort, risk, approval, realized_value`。
- unit metrics は `cost per transaction / customer / deployment / model inference / GB processed` など、事業単位に合わせる。
- optimization backlog は realized savings と avoided cost を分けて計測する。

### Metrics
Allocation coverage、forecast accuracy、unit cost trend、commitment coverage/utilization、realized savings、waste backlog aging、budget anomaly time-to-action、engineer cost dashboard adoption。

### Failure Modes
- FinOps が finance の月次レポートに閉じる。
- engineering が cost signal を見ない。
- commitment discount を追いすぎて lock-in/overcommit する。
- savings を「削減額」として二重計上する。

### Anti-patterns
「FinOps = コスト削減チーム」、tagging 警察化、unit economics なし、product owner 不在、optimization が reliability/SLO と切り離される。

### Maturity Model
- Level 0: cloud bill の事後確認。
- Level 1: dashboard と予算警告。
- Level 2: allocation/tagging と monthly review。
- Level 3: Inform/Optimize/Operate cycle と unit economics。
- Level 4: automated anomaly, rightsizing, commitment analytics。
- Level 5: engineering/product が cost-value tradeoff をリアルタイムに最適化する。

### Clone Implementation Guide
1. FinOps charter と persona/RACI を定義する。
2. top 20 workloads の owner、unit metric、allocation を確定する。
3. daily anomaly と weekly optimization review を始める。
4. commitment purchase は forecast confidence と owner signoff を必須にする。
5. quarterly に FinOps maturity を評価し、能力単位で改善する。

### Confidence & Unknowns
- 確度A: FinOps Foundation の framework/phases。
- 確度B: unit metric examples は実務適用例。
- 不明点: 各社の cloud provider mix、pricing contract、reserved commitment 条件。

---

## 24.10 Data Governance

### Definition
データ資産の所有権、利用目的、品質、系譜、アクセス、分類、規制適合、ライフサイクル、ビジネス価値を定義し、データ利用の安全性と価値創出を両立するレイヤー。

### Frontier Exemplars
- **DAMA-DMBOK**: data management の共通知識体系を提供し、データ資産を戦略・規制・AI/ML/cloud と接続する。Evidence: S17.
- **EDM Council DCAM**: mature data management function、objective metrics、peer benchmarks、共通用語を提供する。Evidence: S18.
- **NIST/Privacy/ISO**: data governance を privacy/security obligations と接続する。Evidence: S19, S21, S27.

### Evidence Map
| Claim | Evidence | Confidence |
|---|---|---|
| data governance は data assets を構造化・統治・最適化する共通言語を必要とする。 | S17 | A |
| maturity metrics と peer benchmark は data management capability の評価に使える。 | S18 | A |
| 個人データ/機微データは privacy/security governance と接続する必要がある。 | S19, S21, S27 | A |

### Core Philosophy
データは「保存された情報」ではなく、所有者、意味、品質、アクセス権、規制義務、利用価値を持つ資産である。

### Decision Model
- 入力: data inventory、business glossary、lineage、data quality metrics、access logs、privacy classification、regulatory obligations、AI/analytics use cases。
- 判断基準: business criticality、data quality、sensitivity、regulatory exposure、lineage completeness、ownership clarity、reuse value。
- 優先順位: regulated/PII data、high-value product data、AI training data、financial/reporting data、unowned critical datasets。
- 禁止事項: ownerless critical data、definition mismatch、unapproved sensitive data access、lineage unknown for regulated reporting。
- 例外条件: research sandbox、incident investigation、legal hold。ただし data minimization、access expiry、review 必須。
- 承認者: data owner、data steward、CDO、privacy/security reviewer。
- 見直し頻度: data domain review 月次/四半期、DQ review 週次/月次、access review 月次/四半期。

### Operating Model
- 役割: CDO、data domain owner、data steward、data custodian、privacy officer、security architect、analytics/AI owner。
- プロセス: catalog → classify → assign owner → define glossary/rules → monitor DQ/lineage/access → remediate。
- ツール: data catalog、metadata platform、lineage、DQ monitor、IAM、privacy management、data lake/warehouse governance。
- 成果物: data catalog、business glossary、data domain model、DQ rules、lineage map、access policy、data issue tracker。

### Technical / Business Specification
- `DataAsset` schema: `asset_id, domain, owner, steward, classification, purpose, systems, lineage, quality_rules, access_policy, retention, privacy_basis, downstream_consumers`。
- regulated reporting / AI / PII datasets は lineage と quality rules を必須にする。
- data issue は business impact と root cause を持つ。

### Metrics
Catalog coverage、critical data owner coverage、DQ rule pass rate、lineage completeness、access review completion、unclassified data count、data issue aging、glossary adoption、sensitive data exposure。

### Failure Modes
- data catalog が検索ツールに留まり、ownership/quality/access に接続されない。
- business glossary が各部門で別定義になる。
- AI/analytics 利用が privacy/legal basis と分断される。
- lineage が regulated reporting に追いつかない。

### Anti-patterns
「CDOが全データの owner」、data governance = catalog導入、品質指標が技術メトリクスだけ、access review が形式化、data domain と product/service owner が不一致。

### Maturity Model
- Level 0: データ資産不明。
- Level 1: 個別チームの台帳。
- Level 2: catalog と owner 登録。
- Level 3: glossary、DQ rules、classification、access policy。
- Level 4: lineage/DQ/access/privacy の統合監視。
- Level 5: data product governance と AI/analytics governance が自律改善する。

### Clone Implementation Guide
1. top critical data domains を5〜10個選ぶ。
2. 各 domain に owner/steward を置き、business glossary を作る。
3. PII/regulated/AI-use datasets から catalog, lineage, DQ rules を実装する。
4. access review と privacy purpose を data asset に接続する。
5. DQ issue を business incident として管理する。

### Confidence & Unknowns
- 確度A: DAMA-DMBOK、DCAM、privacy/security標準の構造。
- 確度B: DataAsset schema は複数標準の抽象化。
- 不明点: 各社固有の data domains、DQ threshold、metadata platform。

---

## 24.11 Privacy & Data Protection

### Definition
個人データの収集、利用、共有、保存、削除、第三者提供、権利対応、リスク評価を、目的、法的根拠、最小化、安全管理、説明責任に基づき管理するレイヤー。

### Frontier Exemplars
- **NIST Privacy Framework**: privacy risk management と innovation/protection の両立を支援する voluntary tool。Evidence: S19.
- **OECD Privacy Principles**: collection limitation、purpose specification、use limitation、security safeguards、accountability などの基本原則。Evidence: S20.
- **ISO/IEC 27701**: PIMS、PII controller/processor、accountability、evidence-based privacy management。Evidence: S21.
- **European Commission GDPR guidance**: controller/processor の役割と契約上の義務分担。Evidence: S28.

### Evidence Map
| Claim | Evidence | Confidence |
|---|---|---|
| privacy は risk management framework として実装できる。 | S19 | A |
| 個人データ処理には collection limitation, purpose, use limitation, safeguards, accountability が必要である。 | S20 | A |
| PII controller/processor の責任分担と証拠管理が必要である。 | S21, S28 | A |
| 不要データ保持や遅延通知は regulatory failure になり得る。 | S30 | A |

### Core Philosophy
個人データは「使えるか」ではなく、「特定目的に必要最小限で、説明可能・削除可能・権利行使可能か」で判断する。

### Decision Model
- 入力: processing activity、PII inventory、purpose、legal basis、data subject rights、retention、processor/subprocessor、security controls、DPIA/PIA triggers。
- 判断基準: lawfulness、purpose limitation、data minimization、privacy risk、security safeguards、cross-border transfer、processor obligations、individual rights impact。
- 優先順位: sensitive data、large-scale processing、children/vulnerable subjects、automated decisioning、third-party transfers、breach notification。
- 禁止事項: purpose unknown processing、unbounded retention、processor contract missing、DSAR untracked、privacy review bypass。
- 例外条件: legal hold、security investigation、statutory retention、vital interest。例外は legal/privacy 承認必須。
- 承認者: DPO/privacy office、legal、security、data/product owner。
- 見直し頻度: processing inventory 四半期、DPIA trigger 変更時、processor review 年次、retention review 月次/四半期。

### Operating Model
- 役割: DPO/privacy officer、product owner、data owner、security、legal、processor owner。
- プロセス: data intake → privacy classification → purpose/legal basis → DPIA/PIA → control mapping → DSAR/retention/breach workflow。
- ツール: privacy management platform、data catalog、consent/DSAR system、retention engine、vendor/contract repository。
- 成果物: Record of Processing Activities、PII inventory、DPIA/PIA、DSAR log、processor register、retention schedule、breach notification log。

### Technical / Business Specification
- `ProcessingActivity` schema: `purpose, legal_basis, data_categories, subjects, controller_processor_role, processors, retention, transfer, safeguards, DPIA_required, DSAR_process, breach_notification_rule`。
- PII data asset は data catalog と processing activity に接続する。
- processor contract は security/privacy obligations、subprocessor、notification、deletion/return を持つ。

### Metrics
Processing inventory coverage、DPIA completion、DSAR SLA、retention deletion completion、processor contract coverage、privacy incident count、unapproved processing count、purpose mismatch count。

### Failure Modes
- privacy review がローンチ直前のチェックリストになる。
- PII inventory と data catalog が一致しない。
- データ保持期間が未設定で不要データが残る。
- processor/subprocessor の変更が privacy office へ通知されない。
- breach/disclosure情報が経営・法務へ遅れて届く。

### Anti-patterns
「プライバシーポリシー掲載=完了」、同意だけに依存、retention schedule が実際の削除に接続しない、processor契約を procurement だけで処理する、DSARを手動メールで管理。

### Maturity Model
- Level 0: PII処理不明。
- Level 1: プライバシーポリシーと手動相談。
- Level 2: PII inventory、DPIA/DSAR/retention 手順。
- Level 3: processing activity と data catalog/contract の接続。
- Level 4: automated privacy controls、DSAR workflow、retention deletion、processor monitoring。
- Level 5: privacy-by-design が product/data/change workflow に組み込まれ、自動リスク評価される。

### Clone Implementation Guide
1. processing activity register を作る。
2. PII catalog と controller/processor role を明示する。
3. DPIA trigger を `sensitive/large-scale/automated decisioning/third-party transfer` に設定する。
4. DSAR、retention、breach notification workflow をシステム化する。
5. processor contract と vendor register を privacy record に接続する。

### Confidence & Unknowns
- 確度A: NIST/OECD/ISO/GDPR公式 guidance の中核構造。
- 確度B: ProcessingActivity schema は標準抽象化。
- 不明点: 国別の法的根拠、越境移転、同意要件、データ主体権利の差分。

---

## 24.12 Legal Risk & Legal Operations

### Definition
法的リスク、訴訟・紛争、規制調査、契約リスク、知財、外部弁護士、法務費用、法務業務プロセスを管理し、事業判断へ法的制約と選択肢を提供するレイヤー。

### Frontier Exemplars
- **ISO 31022**: ISO 31000 を補完する legal risk management guideline。Evidence: S22.
- **ISO 31000**: legal risk も一般リスク管理プロセスに統合する基盤。Evidence: S07.
- **CLOC Core 12**: legal operations の成熟度評価と改善目標設定。Evidence: S26.

### Evidence Map
| Claim | Evidence | Confidence |
|---|---|---|
| legal risk は ISO 31000 型の risk management process に統合できる。 | S22, S07 | A |
| legal operations は成熟度評価、目標設定、進捗管理の対象である。 | S26 | B |
| legal risk は contract/privacy/vendor/compliance と接続する必要がある。 | S22, S23, S28 | B |

### Core Philosophy
法務は「最終承認者」ではなく、事業目的に対する法的リスク、選択肢、許容条件、交渉余地を構造化する意思決定機能である。

### Decision Model
- 入力: matter intake、contract request、regulatory change、dispute、incident、product launch、jurisdiction、outside counsel spend。
- 判断基準: legal exposure、likelihood、precedent risk、financial impact、regulatory scrutiny、reputation、business urgency、privilege sensitivity。
- 優先順位: regulatory deadlines、litigation/investigation、material contracts、privacy/security incidents、high-revenue/high-liability deals。
- 禁止事項: legal review bypass、privilege mishandling、untracked outside counsel spend、legal risk without owner/action。
- 例外条件: emergency customer negotiation、incident response、court/regulator deadline。
- 承認者: General Counsel、business counsel、legal ops、executive sponsor。
- 見直し頻度: matter review 週次/月次、legal risk review 四半期、outside counsel review 月次/四半期。

### Operating Model
- 役割: GC、business legal counsel、legal ops、privacy counsel、IP counsel、outside counsel manager。
- プロセス: matter intake → triage → risk rating → assignment → advice/approval → action tracking → closure/lessons learned。
- ツール: matter management、e-billing、CLM、knowledge base、legal hold、regulatory tracker。
- 成果物: legal risk register、matter record、advice memo、outside counsel guideline、legal spend dashboard、legal playbook。

### Technical / Business Specification
- `LegalMatter` schema: `matter_type, jurisdiction, business_owner, legal_owner, risk_rating, deadline, privilege_status, external_counsel, budget, status, decision, lessons`。
- legal risk は `contract/vendor/privacy/compliance/change` record に link 可能にする。
- outside counsel は matter budget、scope、rate、outcome で管理する。

### Metrics
Matter cycle time、legal intake SLA、high-risk matter count、outside counsel spend variance、contract review SLA、repeat issue rate、legal risk closure、self-service adoption。

### Failure Modes
- 法務が属人的相談窓口に留まり、risk data が残らない。
- 事業側が遅すぎる法務相談でリスクを固定化する。
- outside counsel spend が成果・予算と接続されない。
- 法的助言が contract/vendor/privacy workflow へ反映されない。

### Anti-patterns
法務が「No department」化、matter intake なし、契約レビューが個人メール、法律相談のナレッジ再利用なし、法務KPIが件数だけ。

### Maturity Model
- Level 0: 法務相談が非構造。
- Level 1: 個人管理とメール依存。
- Level 2: matter intake と basic playbook。
- Level 3: legal risk register、CLM/matter/e-billing 統合。
- Level 4: self-service、analytics、outside counsel optimization。
- Level 5: 法的リスクが product/change/contract/vendor decision に自動反映。

### Clone Implementation Guide
1. legal matter intake form を導入し、risk rating を必須にする。
2. high-frequency matters に playbook と self-service template を作る。
3. CLM、privacy、vendor、incident workflow と legal review trigger を接続する。
4. outside counsel guideline と budget approval を標準化する。
5. legal ops maturity を四半期で評価する。

### Confidence & Unknowns
- 確度A: ISO 31022/31000 の legal risk 構造。
- 確度B: CLOC Core 12 による legal ops 成熟度活用。
- 不明点: 弁護士資格・秘匿特権・管轄別規制の具体要件。

---

## 24.13 Contract Lifecycle Management

### Definition
契約の作成、交渉、承認、締結、義務履行、変更、更新、終了、保管、リスク評価を lifecycle として管理するレイヤー。

### Frontier Exemplars
- **WorldCC Contract Management Standard**: 契約実務の統一フレームワークと共通言語を提供する。Evidence: S23.
- **ISO 44001**: 協働的ビジネス関係の識別、開発、管理を扱い、contract/vendor relationship と接続する。Evidence: S25.
- **GDPR controller/processor guidance**: データ処理契約に controller/processor の義務分担が必要である。Evidence: S28.

### Evidence Map
| Claim | Evidence | Confidence |
|---|---|---|
| contract management は共通フレームワークと共通言語を必要とする。 | S23 | A |
| 契約関係はビジネス関係管理・サプライチェーン・vendor management と接続する。 | S25, S24 | B |
| privacy/security/data processing obligations は契約条項へ flowdown する。 | S28, S21, S24 | A |

### Core Philosophy
契約は締結して終わる文書ではなく、リスク、権利、義務、収益、費用、更新、終了、データ処理、第三者依存を管理する operating artifact である。

### Decision Model
- 入力: contract request、counterparty、deal value、risk tier、template deviation、data/security terms、jurisdiction、renewal date、obligations。
- 判断基準: liability exposure、revenue/procurement value、data/privacy/security risk、non-standard terms、termination rights、SLA/credit、renewal risk。
- 優先順位: high-value contracts、non-standard terms、data processing agreements、critical vendor/customer contracts、auto-renewal risk。
- 禁止事項: unsigned/non-approved contracts、side letters outside repository、obligation owner missing、auto-renewal without review、unapproved clause deviation。
- 例外条件: urgent deal close、regulated customer requirement、strategic partnership。legal/business approval 必須。
- 承認者: legal、business owner、finance、security/privacy、procurement/sales leadership。
- 見直し頻度: intake/approval per contract、obligation review monthly、renewal review 90/180日前。

### Operating Model
- 役割: contract manager、legal counsel、business owner、procurement/sales ops、security/privacy reviewer、finance。
- プロセス: request → template/playbook → negotiation → approval → signature → obligation extraction → performance/renewal/termination。
- ツール: CLM、e-signature、contract repository、clause library、obligation management、vendor/customer CRM/ERP。
- 成果物: clause library、contract playbook、approval matrix、executed contract、obligation register、renewal calendar、deviation report。

### Technical / Business Specification
- `Contract` schema: `counterparty, type, value, owner, risk_tier, jurisdiction, template, deviations, obligations, renewal_date, termination_rights, data_processing, security_terms, vendor/customer_links`。
- non-standard clause は clause library と deviation approval に接続する。
- obligation は `owner, due_date, evidence, breach consequence` を持つ。

### Metrics
Contract cycle time、template usage rate、non-standard clause rate、approval SLA、obligation completion、renewal leakage、auto-renewal prevented、contract repository coverage、deviation aging。

### Failure Modes
- 契約が repository に集約されず、義務・更新・終了が見えない。
- 交渉済み条項が運用部門に伝わらない。
- data processing/security terms が vendor/privacy workflow と接続しない。
- auto-renewal により不要契約や不利条件が継続する。

### Anti-patterns
契約レビューを法務メールだけで処理、締結後の義務抽出なし、clause library なし、更新日管理なし、営業/調達の side agreement を放置。

### Maturity Model
- Level 0: 契約所在不明。
- Level 1: 手動レビューと共有フォルダ。
- Level 2: repository、template、approval matrix。
- Level 3: CLM workflow、clause library、renewal calendar。
- Level 4: obligation management、risk-based approval、自動抽出/通知。
- Level 5: contract intelligence が vendor/privacy/revenue/cost/risk decisions に連動。

### Clone Implementation Guide
1. contract taxonomy と approval matrix を定義する。
2. 標準 template と fallback clause を整備する。
3. executed contract を repository に集約し、owner/renewal/risk tier を必須化する。
4. high-risk obligations を抽出して owner と evidence を紐づける。
5. vendor/customer/privacy/security workflow との link を実装する。

### Confidence & Unknowns
- 確度A: WorldCC standard と GDPR processor/controller guidance の構造。
- 確度B: Contract schema と metrics は CLM実務の抽象化。
- 不明点: 個別業界の必須条項、国別 enforceability、電子署名要件。

---

## 24.14 Vendor / Third-Party Management

### Definition
サプライヤー、SaaS、外部委託先、クラウドプロバイダー、データ処理者、戦略パートナーを、重要度、リスク、契約、監視、義務、退出条件で管理するレイヤー。

### Frontier Exemplars
- **NIST SP 800-161 C-SCRM**: supply chain cybersecurity risks を全階層で識別・評価・低減し、リスク管理プロセスへ統合する。Evidence: S24.
- **SEC Item 106**: third-party service provider に起因する cybersecurity risk の評価・管理を開示文脈に含める。Evidence: S03.
- **ISO 44001**: collaborative business relationships を識別・開発・管理する。Evidence: S25.
- **EU controller/processor guidance**: processor 委託は契約上の義務分担を必要とする。Evidence: S28.

### Evidence Map
| Claim | Evidence | Confidence |
|---|---|---|
| vendor/supply-chain risk は enterprise cybersecurity risk management に統合する必要がある。 | S24, S03 | A |
| third-party management は契約条項、監視、リスク低減を含む lifecycle である。 | S24, S25, S23 | A |
| data processor/vendor は privacy obligations の flowdown 対象である。 | S28, S21 | A |

### Core Philosophy
ベンダーは購買対象ではなく、組織のリスク境界の延長である。重要な第三者は、自社の資産・データ・統制・インシデント・契約・退出計画と同じ粒度で管理する。

### Decision Model
- 入力: vendor request、service criticality、data access、network/system access、subprocessors、financial dependency、contract terms、security assessment、country/jurisdiction。
- 判断基準: criticality、data sensitivity、cyber risk、operational dependency、concentration risk、financial viability、subcontractor chain、exit feasibility。
- 優先順位: critical service providers、PII/processors、production/system access、single points of failure、high spend/high lock-in vendors。
- 禁止事項: vendor owner missing、no due diligence for high-risk vendor、contract without security/privacy terms、no exit plan for critical vendor、unapproved subprocessor。
- 例外条件: emergency procurement、sole-source strategic vendor、incident replacement。executive/legal/security approval と retrospective review 必須。
- 承認者: vendor owner、procurement、security、privacy/legal、finance、executive risk committee for critical vendors。
- 見直し頻度: critical vendors quarterly/semiannual、medium annual、trigger events on contract change, incident, service expansion, subprocessor change。

### Operating Model
- 役割: vendor owner、procurement、TPRM、security assessor、privacy/legal reviewer、finance、business owner。
- プロセス: intake → tiering → due diligence → contract terms → onboarding → continuous monitoring → renewal review → offboarding/exit。
- ツール: vendor management platform、security questionnaire、contract repository、privacy processor register、risk register、continuous monitoring feeds。
- 成果物: vendor inventory、tiering model、due diligence report、risk acceptance、contract obligations、SLA report、subprocessor register、exit plan。

### Technical / Business Specification
- `Vendor` schema: `vendor_id, owner, service, tier, data_access, system_access, criticality, contract_ref, processor_role, subprocessors, security_assessment, risk_score, monitoring_frequency, exit_plan, concentration_group`。
- Tier 1 vendor は `security assessment + privacy review + contract controls + exit plan + annual/quarterly review` を必須にする。
- vendor risk は asset/data/contract/risk register に接続する。

### Metrics
Vendor inventory coverage、tiering completion、due diligence SLA、critical vendor review completion、contract control coverage、subprocessor approval rate、vendor incident count、exit plan coverage、concentration risk exposure。

### Failure Modes
- vendor inventory が procurement 支出台帳に留まり、data/system access が見えない。
- critical vendor に exit plan がない。
- subprocessor 変更が privacy/legal/security へ届かない。
- contract renewal が security/privacy review を bypass する。
- third-party incident 情報が management/disclosure channel に遅れて届く。

### Anti-patterns
全ベンダーに同じ questionnaire、低価格だけで調達判断、契約後にセキュリティレビュー、vendor owner が部署名だけ、SaaS free trial/shadow IT を除外。

### Maturity Model
- Level 0: ベンダー不明。
- Level 1: procurement 台帳のみ。
- Level 2: vendor inventory と基本 due diligence。
- Level 3: risk-based tiering、security/privacy/legal contract flowdown。
- Level 4: continuous monitoring、subprocessor tracking、exit planning、concentration analysis。
- Level 5: third-party risk が enterprise risk, data governance, contract, incident, FinOps にリアルタイム接続。

### Clone Implementation Guide
1. vendor inventory を contract/procurement/SaaS discovery から統合する。
2. tiering criteria を `criticality / data / access / spend / substitutability / jurisdiction` で定義する。
3. Tier 1/2 vendor に標準 due diligence と contract controls を適用する。
4. privacy processor register、contract obligations、asset/data access と接続する。
5. critical vendors の exit plan と concentration risk を四半期レビューする。

### Confidence & Unknowns
- 確度A: NIST C-SCRM、SEC Item 106、GDPR controller/processor guidance の構造。
- 確度B: Vendor schema は複数標準の抽象化。
- 不明点: 個別vendorの契約条項、監査権、実際のsubprocessor chain、国別規制。

---

# 8. Integrated Operating Model

## 8.1 Shared Data Model

14レイヤーを統合する場合、最小限の共通オブジェクトは次のとおり。

| Object | Required fields | Linked objects |
|---|---|---|
| GovernanceObject | objective, owner, approver, metric, review cadence | Risk, Control, Evidence, Exception |
| Obligation | source, applicability, owner, control, evidence, deadline | Contract, Privacy, Vendor, Compliance |
| Risk | scenario, impact, likelihood, owner, treatment, KRI | Asset, Vendor, Data, Contract, Change |
| Control | objective, owner, system, evidence, test method | Obligation, Risk, Audit Finding |
| Evidence | source system, timestamp, collector, status, hash/reference | Control, Audit, Compliance |
| Exception | scope, reason, approver, residual risk, expiry, compensating control | Control, Risk, Change |
| Asset | owner, lifecycle, criticality, data class, cost center | Risk, Cost, License, Change |
| DataAsset | owner, classification, purpose, lineage, retention | Privacy, Contract, Vendor, Risk |
| Vendor | owner, tier, service, data/system access, contract, exit plan | Contract, Privacy, Risk, Cost |
| Contract | owner, counterparty, obligations, renewal, deviations | Vendor, Legal, Privacy, Cost |
| Change | affected objects, risk score, approval, evidence, rollback | Asset, Control, Risk, Incident |
| CostObject | owner, product, service, unit metric, budget, actual | Asset, Vendor, Cloud workload |

## 8.2 Minimal Governance Forums

| Forum | Cadence | Scope | Inputs | Outputs |
|---|---|---|---|---|
| Executive Risk / Governance Committee | Monthly/Quarterly | 24.01, 24.04, 24.14 | KRI, high residual risk, exceptions, incidents | risk acceptance, investment decision, escalation |
| GRC Control Review | Monthly | 24.02, 24.03, 24.04 | control test results, evidence freshness, findings | remediation decisions, exception review |
| Change Advisory / Change Authority | Weekly/As needed | 24.05 | high-risk changes, emergency changes | approval, rollback requirements, PIR |
| FinOps Review | Weekly/Monthly | 24.08, 24.09 | spend, anomaly, unit cost, optimization backlog | optimization actions, forecast updates |
| Data & Privacy Council | Monthly/Quarterly | 24.10, 24.11 | PII inventory, DPIA, DQ issues, access review | data policy, privacy decisions |
| Contract/Vendor Review | Monthly/Quarterly | 24.12, 24.13, 24.14 | renewals, high-risk clauses, vendor reviews | contract approvals, exit/renewal decisions |

## 8.3 Control Automation Priorities

1. Asset discovery → ownerless/high-risk asset detection。
2. Cloud cost allocation → owner/product/cost center mapping。
3. Evidence collection → control testing dashboard。
4. Change evidence → CI/CD deployment and approval link。
5. Vendor/contract link → renewal and due diligence triggers。
6. Data catalog/PII inventory → privacy and retention workflow。
7. License/SBOM scan → release gate and notice/source obligations。

---

# 9. Implementation Roadmap

## 0–30 days: Registry and ownership baseline

- Layer mapping を正式 layer registry に合わせて確定する。
- GRC minimum schema: Risk, Control, Obligation, Evidence, Exception を作る。
- Top 20 systems/assets/vendors/contracts/data domains/cloud workloads を登録する。
- ownerless objects を remediation backlog にする。
- governance forums と escalation thresholds を確定する。

## 31–60 days: Evidence and workflow connection

- obligation-to-control mapping を高リスク領域から実装する。
- asset/vendor/data/contract/change/cost の各台帳を最低限 link する。
- FinOps allocation and anomaly review を開始する。
- privacy processing activity register と processor register を作る。
- high-risk vendor due diligence と contract obligation extraction を開始する。

## 61–90 days: Risk-based automation and assurance

- policy-as-code / automated evidence collection を優先統制から開始する。
- audit finding schema と closure evidence を固定する。
- change risk scoring と CI/CD evidence linkage を実装する。
- license/SBOM release gate を high-risk products に適用する。
- management dashboard を board/executive committee に提出する。

## 90 days以降: Continuous improvement

- exception aging と risk acceptance を executive review に組み込む。
- unit economics と product P&L に cost data を接続する。
- data quality/lineage/privacy controls を AI/analytics use cases に拡張する。
- vendor concentration risk と exit plan drill を実施する。
- internal audit が evidence graph の妥当性を独立評価する。

---

# 10. QA Report

| QA Check | Result | Notes |
|---|---|---|
| Coverage | Pass | 24 の全レイヤーに T0/T1/T2/T3 の中核証拠を割当。 |
| Critical Claim | Pass | 各レイヤーの主要 claim は A または B。 |
| Recency | Pass with note | ISO/IEC 27701:2025 など現行/新規標準を採用。標準本文の有償詳細までは確認対象外。 |
| Exceptions | Pass | 各レイヤーに例外条件と承認者を記載。 |
| Failure | Pass | SEC/FTC Blackbaud を横断 failure evidence として採用。 |
| Provenance | Pass | Source Catalog ID を各 claim に接続。 |
| Output Integrity | Pass | RESEARCH.md の Clone Spec 必須欄を各レイヤーに反映。 |

## 10.1 Validation Queries

次回再検証時の既定クエリ。

```text
site:csrc.nist.gov "Cybersecurity Framework 2.0" GOVERN risk management
site:csrc.nist.gov "SP 800-37" "continuous monitoring" authorization
site:ecfr.gov "229.106" "third-party service provider" cybersecurity risk
site:isaca.org COBIT governance management objectives
site:iso.org "ISO 37301" "compliance management systems"
site:theiia.org "Global Internal Audit Standards" "independence" "engagement"
site:finops.org/framework "Inform" "Optimize" "Operate"
site:iso.org "ISO/IEC 19770-1" "IT asset management"
site:openchainproject.org "ISO/IEC 5230" license compliance
site:csrc.nist.gov "SP 800-161" "supply chain risk management"
site:worldcc.com "Contract Management Standard"
site:oecd.org "privacy principles" "accountability"
"Blackbaud" SEC FTC breach disclosure notification
```

## 10.2 Known Unknowns

- ISO標準の詳細条文は多くが有償本文であり、本稿は公開概要と公式説明に基づく。
- 各企業の具体的な閾値、承認権限、取締役会報告フォーマット、ベンダー契約条項は公開情報だけでは確定できない。
- レイヤー24の正式名称が別 registry に存在する場合、本文の仮マッピングを差し替える必要がある。
- 各国の privacy/legal/compliance 要件は jurisdiction ごとに差分が大きいため、実装時は現地法務レビューが必要。

---

# 11. Final Clone Design Principle

Layer 24 は個別最適で設計してはいけない。Frontier pattern は、**governance を頂点に、risk を評価軸、compliance を義務変換、audit を独立保証、change/asset/license/cost/FinOps を運用制御、data/privacy/legal/contract/vendor を外部・データ・法的境界管理として接続する統合 operating model** である。

最小実装は次の式に集約される。

```text
Every critical decision object must have:
owner + risk tier + obligation/control mapping + evidence source + exception path + review cadence + business metric.
```

この式を満たさない資産、変更、契約、ベンダー、データ、クラウド費用、ライセンス、法務案件は、先端組織では「管理されている」と見なさない。
