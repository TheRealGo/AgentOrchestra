# Frontier Operating Model Research: 要件工学・品質属性・規制要件（Layers 04）

生成日: 2026-05-13  
対象: 04  
研究単位: 要件工学・品質属性・規制要件  
出力形式: Clone Spec / layer registry / source catalog / evidence map / pattern library  
前提: 公開情報のみ。法務・規制領域は一般的な研究メモであり、法的助言ではない。

## 0. Scope とレイヤー割当

ユーザー提示のサブテーマを、04 の 13 レイヤーへ順序対応させた。別途正式なレイヤー台帳が存在する場合は、`layer_name_ja` だけを差し替え、decision object と evidence map はそのまま流用できる。

| Layer ID | 作業レイヤー名 | この調査での decision object |
|---|---|---|
| 04.01 | 機能要件 | システムが誰に何の業務成果・ユーザー成果を提供するかを、検証可能な振る舞いとして定義する |
| 04.02 | 非機能要件・品質属性 | 機能の成否だけでは表せない品質特性を、測定可能なシナリオ・指標・閾値として定義する |
| 04.03 | 制約条件 | 設計・実装・運用の自由度を制限する技術、契約、組織、法務、予算、納期、既存資産の境界を定義する |
| 04.04 | SLA・SLO・SLI | ユーザー体験・事業約束・運用制御を、サービス指標・目標・契約責任へ変換する |
| 04.05 | セキュリティ要件 | 脅威、資産、リスク、攻撃面、制御基準を、設計・実装・検証・運用証跡へ落とす |
| 04.06 | 可用性・信頼性・レジリエンス要件 | 障害時を含むサービス継続、復旧、データ損失許容、冗長化、DR を定義する |
| 04.07 | 性能要件 | レイテンシ、スループット、容量、資源効率、負荷条件、ユーザー体感を定量化する |
| 04.08 | 拡張性・容量要件 | 需要変動、成長、マルチテナント、クォータ、水平/垂直スケールの境界を定義する |
| 04.09 | 保守性・変更容易性要件 | 変更、解析、テスト、再利用、依存関係、技術的負債、移行容易性を定義する |
| 04.10 | 監査・証跡要件 | 誰が、いつ、何を、なぜ、どの権限で行ったかを検証可能に残す要件を定義する |
| 04.11 | 法務要件 | 契約、知財、輸出規制、開示義務、業法、消費者保護、アクセシビリティ等の遵守境界を定義する |
| 04.12 | プライバシー要件 | 個人データ処理の目的、法的根拠、最小化、透明性、権利対応、安全管理、移転を定義する |
| 04.13 | データ保持・削除要件 | データの保持期間、削除、匿名化、アーカイブ、法的保全、媒体サニタイズを定義する |

## 1. Executive Summary

このレイヤー群で先端組織に共通するパターンは、**要件を「願望」ではなく、責任・閾値・証拠・運用制御を持つ意思決定単位に変換すること**である。機能要件はユースケースやユーザーストーリーで終わらせず、受入基準、検証方法、トレーサビリティ、所有者、変更履歴まで持つ。非機能要件は「速い」「安全」「スケーラブル」のような形容詞ではなく、品質属性シナリオ、SLI/SLO、リスク受容、アーキテクチャ制約、テスト結果、監査証跡に変換する。

規範ソースの中心は、ISO/IEC/IEEE 29148 の requirements engineering、ISO/IEC 25010:2023 の product quality model、SEI の Quality Attribute Workshop / ATAM、Google SRE の SLO / error budget、NIST CSF 2.0 / SP 800-53 / SSDF、OWASP ASVS / SAMM、ISO/IEC 27001 / 27701 / ISO 22301 / ISO 19011、AICPA Trust Services Criteria、GDPR / EDPB / European Commission guidance、日本の個人情報保護委員会ガイドライン、DORA / NIS2 / Cyber Resilience Act / SEC cyber disclosure である。

この研究単位の Clone Spec は、次の 6 つの決定原則に圧縮できる。

1. **Requirement as evidence-backed contract**: 全要件は source、owner、priority、acceptance criteria、verification method、traceability、change history を持つ。
2. **Quality as scenario + measure**: 品質属性は、刺激、環境、対象、応答、応答測定値を持つシナリオへ落とし、SLO またはテスト閾値へ接続する。
3. **Risk and regulation by design**: セキュリティ、プライバシー、法務、監査、保持はリリース後のレビュー項目ではなく、要件分類時点の入力制約にする。
4. **SLO-governed operations**: SLA は営業契約、SLO は運用意思決定、SLI は測定点として分離し、error budget でリリース速度と信頼性のトレードオフを管理する。
5. **Control-to-evidence traceability**: NIST、ISO、OWASP、SOC 2、PCI、DORA、NIS2、CRA 等の要求は、control、test、log、audit evidence、owner へ変換する。
6. **Retention is a lifecycle decision**: データ保持はストレージ設定ではなく、目的、法的根拠、保持期限、削除/匿名化、法的保全、媒体サニタイズ、監査証跡を含むライフサイクル要件にする。

## 2. Frontier Exemplars / Source Catalog

Evidence tier は RESEARCH.md の T0〜T6 に合わせた。T0 は標準・仕様・公式ガイド、T1 は規制・法定・監査開示、T2 は実行可能な仕様・スキーマ・テスト可能成果物、T3 は公式運用文書、T4 は履歴・制度資料、T5 は第三者検証、T6 は補助推定である。

| Source ID | Entity | Source / URL | Tier | Officiality | 主な用途 | 主に効く Layer |
|---|---|---|---|---|---|---|
| S01 | ISO | ISO/IEC/IEEE 29148:2018 Requirements engineering, https://www.iso.org/standard/72089.html | T0 | standards_body | 要件プロセス、情報項目、SRS/StRS/SyRS/BRS/OpsCon | 04.01,04.02,04.03 |
| S02 | IEEE SA | IEEE/ISO/IEC 29148-2018 summary, https://standards.ieee.org/standard/29148-2018.html | T0 | standards_body | good requirement、属性、ライフサイクル適用 | 04.01,04.02,04.03 |
| S03 | SEBoK | System Requirements Definition, https://sebokwiki.org/wiki/System_Requirements_Definition | T0/T3 | community_governed | 検証可能性、verification planning | 04.01,04.02 |
| S04 | IREB | CPRE Glossary, https://cpre.ireb.org/en/downloads-and-resources/glossary | T0/T3 | community_governed | 要件工学語彙、共通用語 | 04.01,04.02 |
| S05 | ISO | ISO/IEC 25010:2023 Product quality model, https://www.iso.org/standard/78176.html | T0 | standards_body | 品質属性モデル、測定・評価参照 | 04.02,04.06,04.07,04.08,04.09 |
| S06 | CMU SEI | Quality Attribute Workshop collection, https://www.sei.cmu.edu/library/quality-attribute-workshop-collection/ | T0/T3 | official_doc | 品質属性の発見、ビジネス/ミッション目標からの導出 | 04.02,04.06,04.07,04.08,04.09 |
| S07 | CMU SEI | ATAM collection, https://www.sei.cmu.edu/library/architecture-tradeoff-analysis-method-collection/ | T0/T3 | official_doc | 品質属性間のトレードオフ、アーキテクチャリスク | 04.02,04.06,04.07,04.08,04.09 |
| S08 | Google | Site Reliability Workbook: Implementing SLOs, https://sre.google/workbook/implementing-slos/ | T3 | official_doc | SLI/SLO、error budget、運用意思決定 | 04.04,04.06,04.07 |
| S09 | Google | Error Budget Policy, https://sre.google/workbook/error-budget-policy/ | T3 | official_doc | error budget と変更制御 | 04.04,04.06 |
| S10 | AWS | Well-Architected Reliability Pillar, https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html | T3 | official_doc | 可用性、復旧、DR、信頼性設計 | 04.04,04.06,04.08 |
| S11 | AWS | Availability in Reliability Pillar, https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/availability.html | T3 | official_doc | availability の定量定義 | 04.04,04.06 |
| S12 | AWS | Well-Architected Performance Efficiency, https://docs.aws.amazon.com/wellarchitected/latest/framework/performance-efficiency.html | T3 | official_doc | 性能効率、需要変化、資源効率 | 04.07,04.08 |
| S13 | Google Cloud | Well-Architected Framework Reliability, https://docs.cloud.google.com/architecture/framework/reliability | T3 | official_doc | reliability, deployment, operations | 04.04,04.06,04.08 |
| S14 | Microsoft Azure | Well-Architected Framework, https://learn.microsoft.com/en-us/azure/well-architected/ | T3 | official_doc | 品質駆動のアーキテクチャ意思決定 | 04.02,04.06,04.07,04.08,04.09 |
| S15 | NIST | Cybersecurity Framework 2.0, https://csrc.nist.gov/pubs/cswp/29/the-nist-cybersecurity-framework-csf-20/final | T0 | standards_body | サイバーリスク outcomes、governance、risk communication | 04.05,04.10,04.11 |
| S16 | NIST | SP 800-53 Rev.5, https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final | T0 | standards_body | セキュリティ/プライバシー control catalog | 04.05,04.10,04.12 |
| S17 | NIST | SP 800-218 SSDF, https://csrc.nist.gov/pubs/sp/800/218/final | T0 | standards_body | secure SDLC、セキュア開発要件 | 04.05,04.09 |
| S18 | CISA | Secure by Design, https://www.cisa.gov/resources-tools/resources/secure-by-design | T0/T3 | regulator | secure-by-design/default、メーカー責任 | 04.05,04.11 |
| S19 | OWASP | ASVS 5.0, https://owasp.org/www-project-application-security-verification-standard/ | T0/T2 | community_governed | アプリケーションセキュリティ検証要件 | 04.05 |
| S20 | OWASP | SAMM, https://owasp.org/www-project-samm/ | T0/T3 | community_governed | ソフトウェアセキュリティ成熟度 | 04.05,04.09 |
| S21 | ISO | ISO/IEC 27001:2022, https://www.iso.org/standard/27001 | T0 | standards_body | ISMS 要求事項、継続改善 | 04.05,04.10,04.11 |
| S22 | ISO | ISO/IEC 27701:2019, https://www.iso.org/standard/71670.html | T0 | standards_body | PIMS、PII controller/processor | 04.12,04.13 |
| S23 | ISO | ISO 22301:2019, https://www.iso.org/standard/75106.html | T0 | standards_body | BCMS、事業継続、復旧 | 04.04,04.06 |
| S24 | ISO | ISO 19011:2018, https://www.iso.org/standard/70017.html | T0 | standards_body | 監査プログラム、マネジメントシステム監査 | 04.10 |
| S25 | NIST | SP 800-92 Log Management, https://csrc.nist.gov/pubs/sp/800/92/final | T0/T3 | standards_body | ログ管理基盤、組織的ログプロセス | 04.10,04.13 |
| S26 | NIST | SP 800-88 Rev.1 Media Sanitization, https://csrc.nist.gov/pubs/sp/800/88/r1/final | T0/T3 | standards_body | データ廃棄、媒体サニタイズ | 04.13 |
| S27 | NIST | Privacy Framework, https://www.nist.gov/privacy-framework/privacy-framework | T0 | standards_body | enterprise privacy risk management | 04.12 |
| S28 | AICPA-CIMA | Trust Services Criteria 2017 with revised points of focus 2022, https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022 | T1/T5 | official_doc | SOC 2 security/availability/processing integrity/confidentiality/privacy | 04.05,04.06,04.10,04.12 |
| S29 | European Commission | GDPR data protection rules, https://commission.europa.eu/law/law-topic/data-protection/rules-business-and-organisations_en | T1 | regulator | GDPR compliance obligations | 04.11,04.12,04.13 |
| S30 | European Commission | Data retention answer, https://commission.europa.eu/law/law-topic/data-protection/rules-business-and-organisations/principles-gdpr/how-long-can-data-be-kept-and-it-necessary-update-it_en | T1 | regulator | shortest possible retention, erase/review time limits | 04.12,04.13 |
| S31 | EDPB | SME Data Protection Guide: basics, https://www.edpb.europa.eu/sme-data-protection-guide/data-protection-basics_en | T1/T3 | regulator | storage limitation, deletion/anonymization, retention policy | 04.12,04.13 |
| S32 | Personal Information Protection Commission Japan | 個人情報保護法ガイドライン通則編, https://www.ppc.go.jp/personalinfo/legal/guidelines_tsusoku/ | T1 | regulator | 日本 APPI ガイドライン、安全管理措置 | 04.11,04.12,04.13 |
| S33 | PPC Japan | Laws and Policies English, https://www.ppc.go.jp/en/legal/ | T1 | regulator | APPI consolidated text and rules | 04.11,04.12,04.13 |
| S34 | EIOPA | DORA, https://www.eiopa.europa.eu/digital-operational-resilience-act-dora_en | T1 | regulator | EU financial ICT resilience, application date | 04.04,04.05,04.06,04.10,04.11 |
| S35 | European Commission | NIS2 Directive, https://digital-strategy.ec.europa.eu/en/policies/nis2-directive | T1 | regulator | EU cybersecurity legal framework, 18 sectors | 04.05,04.10,04.11 |
| S36 | European Commission | Cyber Resilience Act, https://digital-strategy.ec.europa.eu/en/policies/cyber-resilience-act | T1 | regulator | products with digital elements, cybersecurity lifecycle obligations | 04.05,04.11 |
| S37 | SEC | Cybersecurity risk management, strategy, governance, incident disclosure, https://www.sec.gov/rules-regulations/2023/07/s7-09-22 | T1 | regulator | material incident disclosure and annual governance disclosure | 04.05,04.10,04.11 |
| S38 | SEC | Small entity compliance guide, https://www.sec.gov/resources-small-businesses/small-business-compliance-guides/cybersecurity-risk-management-strategy-governance-incident-disclosure | T1/T3 | regulator | 8-K four-business-day disclosure after materiality determination | 04.05,04.10,04.11 |
| S39 | PCI SSC | PCI DSS v4.0.1 announcement/library, https://www.pcisecuritystandards.org/document_library/ | T0/T1 | standards_body | payment account data technical/operational requirements | 04.05,04.10,04.13 |
| S40 | Cloud Security Alliance | Cloud Controls Matrix v4.1, https://cloudsecurityalliance.org/artifacts/cloud-controls-matrix-v4-1 | T0/T5 | community_governed | cloud security/privacy controls and CAIQ assessment | 04.05,04.10,04.12 |
| S41 | NIST | AI RMF, https://www.nist.gov/itl/ai-risk-management-framework | T0 | standards_body | trustworthy AI risk considerations | 04.11,04.12 |
| S42 | European Commission AI Act Service Desk | Article 9 Risk Management System, https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-9 | T1/T3 | regulator | high-risk AI lifecycle risk management | 04.11,04.12 |

## 3. Candidate Scoring

| Candidate / exemplar | Performance | Adoption | Artifact richness | Peer validation | Recency | Transferability | Failure evidence | 100点換算 | 採用理由 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| ISO/IEC/IEEE 29148 | 5 | 5 | 4 | 5 | 4 | 5 | 3 | 92 | 要件工学の規範的基盤。StRS/SyRS/SRS などの成果物に移植しやすい。 |
| ISO/IEC 25010:2023 | 5 | 5 | 4 | 5 | 5 | 5 | 3 | 94 | 品質要件の共通語彙。品質属性を測定・評価対象へ変換できる。 |
| SEI QAW / ATAM | 5 | 4 | 5 | 5 | 3 | 5 | 5 | 92 | 品質属性の発見とトレードオフ分析に強い。失敗・リスク抽出まで扱う。 |
| Google SRE SLO / Error Budget | 5 | 5 | 5 | 5 | 4 | 5 | 5 | 97 | SLA/SLO/SLI を運用意思決定へ変換する公開モデルとして強い。 |
| AWS / Google / Azure Well-Architected | 5 | 5 | 5 | 4 | 5 | 4 | 4 | 93 | 可用性、性能、拡張性、信頼性の実装・レビュー粒度が具体的。 |
| NIST CSF 2.0 / SP 800-53 / SSDF | 5 | 5 | 5 | 5 | 5 | 5 | 4 | 98 | セキュリティ/プライバシー control とリスク管理の基準として高密度。 |
| OWASP ASVS / SAMM | 4 | 5 | 5 | 4 | 5 | 5 | 4 | 92 | アプリケーションセキュリティ要件を検証可能な要求 ID にできる。 |
| ISO/IEC 27001 / 27701 | 5 | 5 | 4 | 5 | 4 | 5 | 3 | 92 | ISMS/PIMS として組織的な責任・監査・継続改善へ接続できる。 |
| ISO 22301 | 4 | 4 | 4 | 5 | 4 | 5 | 4 | 86 | 可用性・DR・BCP の要求を事業継続に接続する基準。 |
| AICPA SOC 2 TSC | 4 | 5 | 4 | 5 | 4 | 4 | 4 | 88 | セキュリティ、可用性、処理の完全性、機密性、プライバシーを保証報告に接続できる。 |
| GDPR / EDPB / EC guidance / APPI | 5 | 5 | 4 | 5 | 5 | 4 | 5 | 94 | プライバシー・保持・権利対応の規制要件を直接規定する。 |
| DORA / NIS2 / CRA / SEC cyber disclosure | 5 | 4 | 4 | 5 | 5 | 3 | 5 | 87 | セクター別・製品別・開示別の現行規制要件を提供する。 |

## 4. Evidence Map / Key Claims

| Claim ID | Layer | Claim | Decision model への変換 | Sources | Confidence |
|---|---|---|---|---|---|
| C01 | 04.01–04.03 | 要件工学は、要件を生むプロセス、成果物、成果物の内容を定義するライフサイクル活動である。 | 要件は backlog item ではなく、process + artifact + verification chain として扱う。 | S01, S02, S03 | A |
| C02 | 04.01 | 機能要件は、ステークホルダー要求からシステム要求、ソフトウェア要求へ変換され、受入・検証可能でなければならない。 | 各機能要件に actor, trigger, precondition, behavior, output, acceptance criteria, verification method を必須化する。 | S01, S02, S03 | A |
| C03 | 04.02 | 品質要件は ISO/IEC 25010 の品質モデルを参照して分類・測定・評価できる。 | NFR を品質属性 taxonomy にマップし、特性ごとに測定値とテスト方法を設定する。 | S05 | A |
| C04 | 04.02,04.06–04.09 | 品質属性はビジネス/ミッション目標から導出され、アーキテクチャへ重大な影響を与える。 | QAW でシナリオ生成・優先順位付けし、ATAM で tradeoff/risk/sensitivity point を記録する。 | S06, S07 | A |
| C05 | 04.04 | SLO は SLI、目標値、評価ウィンドウ、error budget を持ち、運用と事業判断に使う。 | SLA と SLO を分離し、SLO 逸脱・error budget 消費をリリース制御とインシデント優先度に接続する。 | S08, S09 | A |
| C06 | 04.06 | Availability は「必要なときに合意された機能を正常に実行できる時間割合」として扱える。 | 可用性要件を service tier, SLI, SLO, downtime budget, RTO/RPO, DR test に分解する。 | S10, S11, S13, S23 | A |
| C07 | 04.07,04.08 | 性能効率は、需要変化や技術変化の中でリソースを効率的に使い性能要件を満たす能力である。 | performance budget, capacity model, load test, autoscaling threshold, resource efficiency を要件化する。 | S12, S14, S05 | A |
| C08 | 04.05 | セキュリティ要件は、リスク、資産、脅威、control catalog、SDLC practice の組み合わせとして管理する。 | threat model、control mapping、ASVS/NIST/ISO controls、security test、evidence owner を必須化する。 | S15, S16, S17, S19, S21 | A |
| C09 | 04.05 | Secure-by-design はユーザーへ後付け負担を転嫁せず、メーカー/開発組織が設計段階からセキュリティ成果に責任を持つ考え方である。 | デフォルト安全設定、MFA、secure update、vulnerability disclosure、SBOM、パッチメトリクスを要求テンプレートへ組み込む。 | S18, S17, S36 | B |
| C10 | 04.10 | ログと監査は単なる保存ではなく、組織的なログ管理プロセス、レビュー、調査、証跡保全を含む。 | audit event taxonomy、time sync、immutability、retention、privileged activity logging、review cadence を要件化する。 | S24, S25, S16, S28 | A |
| C11 | 04.12 | プライバシー要件は、個人データの処理目的、リスク、権利、透明性、安全管理を enterprise risk として管理する。 | data inventory、processing purpose、legal basis、data subject rights、DPIA/PIA、PIMS controls を requirements gate に入れる。 | S22, S27, S29, S31, S32 | A |
| C12 | 04.13 | 個人データ保持は最短必要期間を基本に、削除/匿名化、保持期限、レビュー期限を持つ。 | retention schedule、deletion SLA、anonymization rule、legal hold、exception approval を必須化する。 | S30, S31, S32 | A |
| C13 | 04.13 | 媒体サニタイズは、ライフサイクル全体で情報の機密性カテゴリに応じた実務判断と記録を要する。 | Clear/Purge/Destroy 相当のサニタイズ方針、証明書、検証方法、バックアップ所在を要求化する。 | S26 | A |
| C14 | 04.11 | 規制要件は一枚岩ではなく、管轄、業種、製品分類、データ分類、上場/非上場、顧客契約により変化する。 | regulatory obligation matrix を作り、各 obligation を feature/control/log/process/disclosure へ変換する。 | S29, S32, S34, S35, S36, S37, S38, S39 | A |
| C15 | 04.09 | 保守性は変更、解析、テスト、再利用の効率性として品質要件化すべきである。 | modularity, analyzability, testability, dependency freshness, change lead time を要求・メトリクス化する。 | S05, S07, S14 | B |
| C16 | 04.03 | 制約条件は設計解を狭める条件であり、曖昧に管理すると品質属性や法務要件との衝突が見えなくなる。 | constraint register を作り、source、owner、binding level、expiry、waiver process を持たせる。 | S01, S07, S14 | B |
| C17 | 04.11,04.12 | AI を含むシステムでは、リスク管理、ログ、透明性、ロバスト性、サイバーセキュリティ等が追加の要件化対象になる。 | AI classification、model/data governance、risk management file、technical documentation、logging requirement を追加する。 | S41, S42 | B |

## 5. Core Philosophy

### 5.1 Requirements are governed artifacts

先端組織は、要件を「仕様を作る前の文章」ではなく、**意思決定・責任・検証・証拠を束ねる governance artifact** として扱う。要件には少なくとも ID、source、stakeholder、owner、category、priority、risk、acceptance criteria、verification method、trace target、release target、change history を持たせる。これがない要件は、優先順位付けも検証も監査もできない。

### 5.2 Quality attributes must be measured at the boundary where users feel them

品質属性は、内部コンポーネントの都合だけではなく、ユーザーまたは事業プロセスが体感する境界で測る。可用性なら「サービスが使えるか」、性能なら「ユーザーの主要操作が何 ms で完了するか」、拡張性なら「どの需要増加まで何の追加作業なしに耐えるか」、保守性なら「変更要求から安全なリリースまで何日か」を測る。

### 5.3 Regulation is not a checklist; it is a source of system behavior

法務・規制要件は、コンプライアンス部門のチェックリストに閉じると実装へ反映されない。GDPR/APPI の保持・削除、SEC のインシデント開示、DORA/NIS2 の ICT risk management、CRA の製品サイバーセキュリティ、PCI DSS の payment account data controls などは、データモデル、ログ、通知、権限、リリース gate、サポート運用、監査証跡へ変換する。

### 5.4 SLO is the bridge between product promise and engineering control

SLA は顧客との契約、SLO は内部運用目標、SLI は観測点である。SLO を持たない SLA は違約リスクだけを増やし、SLI を持たない SLO は測れない。error budget は、信頼性と開発速度のトレードオフを定量化する意思決定装置である。

### 5.5 Retention and deletion are product features

保持・削除は、データ基盤の後工程ではなく、プロダクト機能である。ユーザー削除、契約終了、退会、法的保全、監査証跡、バックアップ、アーカイブ、匿名化、媒体廃棄のすべてが、設計時点で要件化されるべきである。

## 6. Decision Model

### 6.1 Inputs

- Business goals, mission goals, product strategy, market commitments
- Stakeholder needs, user journeys, service criticality, customer contract terms
- Existing architecture, integration boundaries, data flows, dependency map
- Regulatory scope: jurisdictions, industry, product category, listing status, data category, customer sector
- Risk appetite and materiality threshold
- Threat model, abuse cases, asset inventory, data classification
- Operational constraints: staffing, on-call, support hours, maintenance windows, incident response capability
- Performance baseline, traffic forecast, capacity model, cost envelope
- Audit obligations, evidence retention obligations, third-party assurance obligations
- Privacy inventory: personal data categories, processing purposes, legal basis, international transfer, data subject rights

### 6.2 Decision Object

`requirements_baseline` を決定する。これは以下を含む。

- 機能要求ベースライン
- 品質属性要求ベースライン
- 制約条件台帳
- SLA/SLO/SLI 台帳
- セキュリティ control mapping
- 可用性/DR/RTO/RPO 要件
- 性能/容量/拡張性モデル
- 保守性/変更容易性要求
- 監査・ログ・証跡要件
- 法務・規制 obligation matrix
- プライバシー・データ保持 schedule
- 検証・監査 evidence plan

### 6.3 Criteria

1. **Traceable**: 要件は business/stakeholder/regulatory/control source へ遡れる。
2. **Testable**: 受入基準、検証方法、測定ウィンドウ、合格閾値を持つ。
3. **Owned**: product、architecture、security、privacy、legal、SRE、QA のいずれかに責任者がいる。
4. **Prioritized by risk and value**: 価値、リスク、法的拘束力、顧客影響、実装費用で優先順位付けする。
5. **Measurable at runtime where possible**: SLI、ログ、監査イベント、メトリクスに変換できるものは観測する。
6. **Conflict-aware**: 性能 vs セキュリティ、保持 vs 最小化、可用性 vs コスト、監査証跡 vs プライバシーなどのトレードオフを明示する。
7. **Evidence-ready**: リリース後に監査・顧客・規制当局へ説明できる証拠を残す。

### 6.4 Priorities

| Priority | 対象 | 理由 |
|---|---|---|
| P0 | 法的禁止、安全、重大セキュリティ、重大プライバシー、生命/財産/基本権リスク | 違反時の影響が不可逆または重大 |
| P1 | 契約 SLA、顧客コミット、データ完全性、決済/認証/権限 | 事業継続と信頼に直結 |
| P2 | 主要ユーザー価値、主要業務フロー、可用性/性能/拡張性 | 事業成果と顧客体験に直結 |
| P3 | 保守性、運用性、監査効率、変更容易性 | 長期の速度・品質・コストを制御 |
| P4 | 最適化、快適性、将来拡張、nice-to-have | 事業制約に応じて調整可能 |

### 6.5 Prohibitions

- 「高速」「安全」「スケーラブル」「準拠」だけの非測定要件を承認しない。
- source と owner のない要件を baseline に入れない。
- SLA を SLI/SLO/observability なしに契約しない。
- 個人データを目的・保持期限・削除方法なしに収集しない。
- 監査ログを後付けにしない。特権操作、データアクセス、設定変更は設計時に audit event 化する。
- 法務要件を Jira ticket の free text に閉じない。obligation matrix と control mapping を持つ。
- security waiver を期限・承認者・補償統制なしに許可しない。
- performance test を production release 後の確認だけにしない。

### 6.6 Thresholds / Default Gates

| Gate | 既定閾値 |
|---|---|
| Requirement completeness | baseline 化する要件の 100% が owner, source, acceptance criteria, verification method を持つ |
| Quality attribute specificity | P0/P1/P2 の品質属性要件は 100% が scenario + response measure を持つ |
| SLO readiness | 外部 SLA を持つサービスは 100% が SLI, SLO, error budget, alerting rule を持つ |
| Security baseline | internet-facing / sensitive data 系は ASVS または NIST/ISO control mapping を必須化 |
| Privacy baseline | 個人データを扱う機能は data inventory, purpose, legal basis, retention, deletion path を必須化 |
| Audit baseline | 特権操作、個人データアクセス、権限変更、設定変更、支払/契約変更は audit event 必須 |
| Retention baseline | データクラスごとに retention period, delete/anonymize action, legal hold exception を定義 |
| DR baseline | mission-critical service は RTO/RPO, backup, restore test, failover playbook を定義 |
| Change waiver | waiver は owner, reason, expiry, compensating control, review cadence を必須化 |

### 6.7 Owners / RACI

| Role | Accountable | Responsible | Consulted | Informed |
|---|---|---|---|---|
| Product Owner | 機能価値、顧客コミット、優先順位 | 受入基準、ユーザー価値 | Legal, Security, SRE, UX | Sales, Support |
| Requirements Engineer / Business Analyst | 要件品質、トレーサビリティ | 要件台帳、分類、変更管理 | Product, Architecture | Delivery teams |
| Solution / Enterprise Architect | 品質属性、制約、トレードオフ | アーキテクチャ決定、ATAM/QAW | SRE, Security, Data | Product |
| SRE / Platform Lead | SLO、可用性、性能、運用 | SLI、alerting、capacity、DR test | Product, Architecture | Support |
| Security Architect / AppSec | セキュリティ baseline | threat model、ASVS/NIST mapping、security tests | Legal, Privacy, Engineering | Product |
| Privacy Officer / DPO equivalent | プライバシー要件 | DPIA/PIA、data rights、retention | Legal, Data, Security | Product |
| Legal / Compliance | 法務・規制 obligation | obligation matrix、contract/legal review | Product, Security, Privacy | Leadership |
| QA / Test Lead | 検証戦略 | acceptance tests、NFR tests、evidence | Engineering, Product | Audit |
| Data Governance Lead | データ分類・保持 | retention schedule、data catalog、lineage | Privacy, Security, Legal | Product |
| Internal Audit / GRC | 監査プログラム | control evidence、audit plan | Security, Legal, SRE | Leadership |

### 6.8 Cadence

| Cadence | 活動 |
|---|---|
| Continuous | 要件 intake、regulatory watch、security/privacy triage、incident lessons learned |
| Weekly | backlog refinement、requirements quality review、architecture constraint review |
| Per epic / major feature | QAW-lite、threat model、privacy review、legal/regulatory screen、SLO impact review |
| Per release | baseline freeze、acceptance evidence review、security gate、privacy gate、SLO readiness gate |
| Monthly | SLO/error budget review、capacity review、control evidence health、regulatory change review |
| Quarterly | risk appetite review、architecture tradeoff review、retention schedule review、audit sampling |
| Annual / audit cycle | SOC 2 / ISO / regulatory audit evidence review、BC/DR exercise、policy refresh |

## 7. Operating Model

### 7.1 Process

1. **Requirement intake**: 顧客要求、事業要求、規制要求、セキュリティ要求、運用要求、データ要求を同一 intake に入れる。
2. **Classification**: functional, quality attribute, constraint, SLA/SLO, security, availability, performance, scalability, maintainability, audit, legal, privacy, retention に分類する。
3. **Source and owner assignment**: business source、stakeholder、law/control source、契約 source、risk source を付ける。
4. **Scenario decomposition**: 品質属性は scenario と response measure へ分解する。
5. **Control mapping**: security/privacy/audit/regulatory は NIST/ISO/OWASP/SOC2/PCI/sector regulation へマッピングする。
6. **Conflict analysis**: 法務 vs product、privacy vs audit、performance vs security、availability vs cost の衝突を ADR / risk decision に記録する。
7. **Verification planning**: 受入テスト、負荷テスト、security test、DR test、audit evidence、manual review を計画する。
8. **Baseline approval**: product、architecture、security、privacy/legal、SRE、QA が該当分だけ承認する。
9. **Implementation and evidence collection**: test、monitoring、logs、docs、runbook、screenshots、config snapshots、tickets を evidence store に保存する。
10. **Operational feedback**: incident、SLO breach、customer complaint、audit finding、regulatory change から要件を更新する。

### 7.2 Required Artifacts

| Artifact | Purpose | Owner |
|---|---|---|
| Requirements Register | すべての要件の canonical 台帳 | Requirements Engineer |
| Source & Obligation Matrix | 法務・規制・契約・標準の要求源と実装対象を接続 | Legal / Compliance |
| Quality Attribute Scenario Register | NFR を測定可能なシナリオへ変換 | Architect |
| Constraint Register | 技術・業務・法務・契約制約の一覧 | Architect / Legal |
| SLI/SLO Catalog | サービスごとの指標・目標・error budget | SRE |
| Security Requirements Baseline | control、threat、ASVS/NIST/ISO mapping | Security Architect |
| Privacy Requirements Baseline | data purpose、legal basis、rights、DPIA、retention | Privacy Officer |
| Audit Event Taxonomy | 記録すべきイベント、属性、保持、アクセス権限 | GRC / Security |
| Retention Schedule | データクラスごとの保持期間、削除、例外 | Data Governance |
| Verification Matrix | 要件→テスト/証拠/監査項目 | QA Lead |
| Waiver Register | 例外承認、期限、補償統制 | Risk Owner |
| ADR / Tradeoff Register | 品質属性・制約の意思決定記録 | Architect |

## 8. Technical / Business Specification

### 8.1 Requirement Object Schema

```yaml
requirement:
  id: REQ-<layer>-<sequence>
  title: string
  statement: "system shall ... / service shall ... / organization shall ..."
  layer_id: "04"
  category: [functional, quality_attribute, constraint, security, legal, privacy, retention]
  source_type: [stakeholder, contract, regulation, standard, risk, incident, strategy]
  source_ref: string
  owner_role: string
  accountable_person_or_group: string
  priority: [P0, P1, P2, P3, P4]
  criticality: [mission_critical, business_critical, standard, experimental]
  affected_services: [string]
  affected_data_classes: [public, internal, confidential, restricted, personal, sensitive_personal]
  jurisdictions: [JP, EU, US, Global]
  acceptance_criteria: [string]
  verification_method: [test, review, inspection, analysis, monitoring, audit, legal_review]
  quality_attribute_scenario_ref: string|null
  sli_slo_ref: string|null
  control_refs: [NIST-800-53, ISO27001, ASVS, SOC2, PCI, custom]
  legal_obligation_refs: [GDPR, APPI, DORA, NIS2, CRA, SEC, contract]
  retention_rule_ref: string|null
  audit_event_refs: [string]
  evidence_refs: [string]
  status: [draft, reviewed, baselined, implemented, verified, waived, retired]
  waiver:
    required: boolean
    approver: string|null
    expiry: date|null
    compensating_controls: [string]
  change_history:
    - date: date
      actor: string
      change: string
      reason: string
```

### 8.2 Quality Attribute Scenario Template

```yaml
quality_attribute_scenario:
  id: QAS-<attribute>-<sequence>
  attribute: [availability, performance, scalability, security, maintainability, privacy, auditability, safety]
  source_of_stimulus: user|system|attacker|operator|regulator|dependency|disaster
  stimulus: string
  environment: normal|peak|degraded|attack|maintenance|disaster|migration
  artifact: service|component|data_store|workflow|operator|control_plane
  response: string
  response_measure:
    metric: string
    target: string
    window: string
    percentile: string|null
  verification_method: string
  evidence: string
```

例:

```yaml
id: QAS-availability-001
attribute: availability
source_of_stimulus: dependency
stimulus: primary database instance becomes unavailable
environment: peak business hours
artifact: order submission service
response: service fails over without losing committed orders
response_measure:
  metric: successful order submissions
  target: ">= 99.9% over 28 days; RTO <= 15 min; RPO <= 5 min"
  window: 28d
verification_method: quarterly failover test + production SLI
```

### 8.3 Regulatory Obligation Matrix Template

```yaml
obligation:
  id: OBL-<jurisdiction>-<sequence>
  source: GDPR|APPI|DORA|NIS2|CRA|SEC|PCI|contract|other
  article_or_clause: string
  jurisdiction: string
  entity_scope: string
  product_scope: string
  data_scope: string
  obligation_text_summary: string
  system_implication: [feature, control, logging, deletion, notification, reporting, documentation, governance]
  owner: legal|privacy|security|sre|product|engineering|audit
  implementation_refs: [requirement_id]
  evidence_refs: [policy, log, ticket, test, report, configuration, attestation]
  review_cadence: monthly|quarterly|annual|on_change
  status: draft|active|superseded|not_applicable
```

### 8.4 Service Criticality and Default Targets

以下は Clone 実装時の初期値であり、実際の SLA/SLO は事業価値、コスト、ユーザー影響、法的義務、運用能力で調整する。

| Tier | Service type | Default SLO posture | DR posture | Review |
|---|---|---|---|---|
| Tier 0 | 生命・安全・決済・認証・規制上重大な中核 | SLI/SLO 必須、error budget policy 必須、24/7 incident response | RTO/RPO 明示、定期 failover、multi-region 検討 | 月次 SLO + 四半期 DR |
| Tier 1 | 主要売上・主要顧客体験 | SLI/SLO 必須、alerting 必須 | RTO/RPO 明示、backup restore test | 月次 |
| Tier 2 | 社内業務・補助機能 | SLI または operational metric、business-hour support | backup/recovery 手順 | 四半期 |
| Tier 3 | 実験・低影響 | 軽量 monitoring | best-effort | 半期 |

### 8.5 Security Requirement Baseline

Minimum baseline for internet-facing or sensitive-data systems:

- Asset and data classification
- Threat model and abuse cases
- Authentication and session requirements
- Authorization model and least privilege
- Cryptography at rest/in transit and key management
- Input validation, output encoding, injection protections
- Secure error handling and logging
- Secrets management
- Dependency and supply chain controls
- Vulnerability management and patch SLA
- Secure deployment and configuration baseline
- Incident response hooks and security monitoring
- ASVS/NIST/ISO control mapping
- Security waiver process

### 8.6 Privacy and Retention Baseline

Minimum baseline for systems processing personal data:

- Processing purpose and legal basis
- Data minimization statement
- Data inventory and data-flow diagram
- Data subject rights handling path
- Consent/preference model where applicable
- International transfer assessment where applicable
- Access control and logging for personal data access
- DPIA/PIA trigger criteria
- Retention period and deletion/anonymization method per data category
- Backup and archive handling
- Legal hold exception
- Processor/subprocessor obligations
- Breach notification and incident escalation hooks

### 8.7 Audit Event Minimum Set

| Event category | Required fields |
|---|---|
| Authentication | subject, method, success/failure, timestamp, source, risk signal |
| Authorization / privilege change | actor, target subject, role/permission before/after, approver, reason, ticket |
| Personal data access | actor, data category, purpose, record scope, timestamp, lawful basis or business reason |
| Administrative configuration | actor, setting before/after, environment, approval, timestamp |
| Security event | detector, severity, asset, event type, response status |
| Data deletion/retention action | actor/system, data class, deletion/anonymization method, legal hold status, evidence |
| Financial/payment-impacting change | actor, amount/rule/object, approver, before/after, timestamp |
| Incident and disclosure decision | incident id, materiality assessment, decision maker, timestamp, notification deadline |

## 9. Layer-by-Layer Clone Specs

### 04.01 機能要件

**Definition**: ユーザー、外部システム、業務プロセス、規制上の主体が、システムに期待する振る舞いと成果を定義するレイヤー。

**Frontier pattern**: 機能要件を user story だけに閉じず、stakeholder need → system requirement → software requirement → acceptance test → production evidence の鎖で管理する。ISO/IEC/IEEE 29148 と SEBoK の考え方に基づき、要求は「検証できる文」に変換する。

**Decision model**

- Inputs: stakeholder need, business process, customer contract, operational scenario, regulation-triggered function
- Criteria: complete, correct, feasible, testable, unambiguous, necessary, traceable
- Outputs: functional requirement, use case, acceptance criteria, test case, traceability link
- Owners: Product Owner, Requirements Engineer, QA Lead
- Metrics: requirement acceptance pass rate, orphan requirement count, escaped functional defect count, change request rate

**Implementation rules**

1. 各機能要件は「actor / trigger / precondition / system behavior / output / exception / acceptance criteria」を持つ。
2. 機能要件に含まれるデータ処理が personal data、payment data、regulated data を含む場合、04.12/04.13/04.11 へ自動リンクする。
3. acceptance criteria が UI 文言だけの場合は不十分。API、データ、ログ、権限、エラー、監査イベントまで確認する。
4. 機能要件は SLO/SLA に影響する場合、04.04 へリンクする。

**Failure modes**

- user story が実装都合で書かれ、業務成果へ遡れない。
- 例外処理、監査ログ、削除、権限が機能要件から漏れる。
- 顧客契約上の約束が product backlog に入らない。

### 04.02 非機能要件・品質属性

**Definition**: 機能の有無ではなく、システムがどの条件でどの品質を満たすべきかを定義するレイヤー。

**Frontier pattern**: ISO/IEC 25010:2023 の品質モデルを共通分類として使い、SEI QAW でビジネス/ミッション目標から品質属性シナリオを抽出し、ATAM で tradeoff/risk/sensitivity point を明示する。

**Decision model**

- Inputs: business goals, mission goals, stakeholder concerns, risk appetite, service criticality, usage context
- Criteria: measurable response, architecture relevance, user impact, tradeoff impact, verification feasibility
- Outputs: quality attribute scenario, NFR baseline, tradeoff register, architecture decision record
- Owners: Architect, SRE, Security, QA
- Metrics: scenario coverage, NFR test pass rate, tradeoff decisions documented, NFR-related incident count

**Implementation rules**

1. 「高速」「安全」「使いやすい」「堅牢」などの形容詞だけの NFR は承認しない。
2. 各品質要件は scenario template に落とす。
3. 属性間の衝突を ADR に記録する。例: 強い監査ログ vs データ最小化、低 latency vs 暗号化/検査、可用性 vs コスト。
4. 品質要件は test/monitoring/audit のいずれかで検証可能にする。

**Failure modes**

- NFR がプロジェクト終盤のテスト観点になる。
- 品質属性に owner がなく、障害時に責任分界が不明になる。
- アーキテクチャ上の tradeoff を議論せずに SLA を契約する。

### 04.03 制約条件

**Definition**: 設計・実装・運用の選択肢を制限する条件を明示し、例外と変更管理を定義するレイヤー。

**Frontier pattern**: 制約を「背景メモ」ではなく constraint register として管理する。source、binding level、owner、expiry、waiver process を持たせる。技術制約、法務制約、契約制約、組織制約、運用制約を分ける。

**Decision model**

- Inputs: existing platform, enterprise architecture standard, cloud region, vendor lock-in, contract, law, budget, timeline, staffing
- Criteria: binding force, risk, reversibility, cost impact, quality impact
- Outputs: constraint register, waiver decision, ADR, migration assumption
- Owners: Architect, Legal, Compliance, Product
- Metrics: unresolved constraints, expired constraints, waiver count, constraint-caused rework

**Implementation rules**

1. 制約は `hard/legal`, `hard/contractual`, `hard/technical`, `soft/preference`, `temporary` に分類する。
2. 各制約は影響レイヤーを持つ。例: data residency は 04.06/04.12/04.13、vendor SLA は 04.04/04.06、legacy API は 04.01/04.07/04.09。
3. 制約を破る場合は waiver に期限、承認者、補償統制を必須化する。

**Failure modes**

- 制約と要件を混同し、設計自由度が過剰に狭まる。
- 「既存システムだから」という非明示制約が意思決定を支配する。
- 法務/契約制約の expiry や変更可能性を確認しない。

### 04.04 SLA・SLO・SLI

**Definition**: サービス品質の契約約束、内部目標、観測指標を分離し、ユーザー体験と運用判断を接続するレイヤー。

**Frontier pattern**: Google SRE 型の SLI/SLO/error budget を採用し、外部 SLA を持つ場合は必ず内部 SLO と observability を先に定義する。error budget を release freeze、incident priority、capacity investment の意思決定に使う。

**Decision model**

- Inputs: customer promise, user journey, service tier, historical reliability, business impact, operational capacity
- Criteria: user-centered indicator, measurable window, controllability, cost of reliability, legal/contract exposure
- Outputs: SLI definition, SLO target, SLA clause, error budget policy, alert rules
- Owners: SRE, Product, Legal, Customer Success
- Metrics: SLO compliance, error budget burn rate, alert precision, SLA credit exposure, customer-impact minutes

**Implementation rules**

1. SLI はユーザーが感じる境界で測る。内部 CPU や queue length だけを SLI にしない。
2. SLO は target + window を持つ。例: 28日間の successful request ratio >= 99.9%。
3. SLA は契約と補償を含むため、Legal と Finance が承認する。
4. SLO 逸脱時の product/engineering 判断を error budget policy に記録する。
5. Alert は SLO burn rate に基づき、ノイズではなくユーザー影響に反応させる。

**Failure modes**

- 営業が高 SLA を契約し、SRE が測定できない。
- SLO が availability だけで、latency、freshness、correctness を無視する。
- error budget が単なるレポートで、リリース判断に効かない。

### 04.05 セキュリティ要件

**Definition**: 資産、脅威、リスク、制御、検証、運用監視をつなぎ、システムが攻撃・誤用・不正アクセスに耐える条件を定義するレイヤー。

**Frontier pattern**: NIST CSF 2.0 で governance/risk/outcome を整理し、NIST SP 800-53 / ISO 27001 / OWASP ASVS / NIST SSDF / CISA Secure by Design を使って要求を control、test、evidence へ変換する。

**Decision model**

- Inputs: asset inventory, data classification, threat model, abuse cases, vulnerability history, regulatory baseline
- Criteria: risk reduction, exploitability, blast radius, control effectiveness, verification feasibility
- Outputs: security requirements baseline, control mapping, threat model, test plan, waiver register, security evidence
- Owners: Security Architect, AppSec, Engineering Lead, Compliance
- Metrics: control coverage, ASVS coverage, critical vuln age, patch SLA, MFA coverage, secrets leakage count, security waiver age

**Implementation rules**

1. Internet-facing application は ASVS 等の検証標準を参照する。
2. Secure SDLC を要件に含め、設計・実装・テスト・リリース・運用の各段階に security activity を置く。
3. 認証、認可、暗号、入力処理、セッション、ログ、秘密情報、依存関係、脆弱性対応、インシデント対応は最低 baseline とする。
4. 顧客が後付けで安全化しないと危険な設計は secure-by-default 原則に反する。
5. AI/ML 機能を含む場合は model/data security、prompt abuse、model access、logging、misuse case を追加する。

**Failure modes**

- compliance control は満たすが実際の threat model を無視する。
- security review がリリース直前に集中し、設計変更不能になる。
- waiver が無期限化し、補償統制が存在しない。

### 04.06 可用性・信頼性・レジリエンス要件

**Definition**: サービスが通常時・障害時・災害時に合意された機能を継続または復旧できる条件を定義するレイヤー。

**Frontier pattern**: AWS/Google/Azure Well-Architected と ISO 22301 を参照し、availability SLO、fault tolerance、RTO/RPO、backup/restore、DR exercise、dependency failure handling をセットで定義する。

**Decision model**

- Inputs: service criticality, customer impact, dependency topology, failure modes, business continuity objective
- Criteria: user impact, recovery objective, data loss tolerance, cost of redundancy, operational readiness
- Outputs: availability SLO, RTO/RPO, DR plan, backup plan, failover runbook, resilience test evidence
- Owners: SRE, Architect, Business Continuity Owner, Product
- Metrics: uptime, customer-impact minutes, MTTA/MTTR, failed failover tests, backup restore success, RTO/RPO compliance

**Implementation rules**

1. Availability は service tier ごとに定義する。全サービスに同じ target を課さない。
2. RTO と RPO を別々に定義する。短い RTO だけではデータ損失を制御できない。
3. DR plan は実施テストと evidence がない限り未検証と扱う。
4. Dependency failure を品質属性シナリオに含める。
5. Maintenance window が SLO/SLA に与える影響を契約・運用で明示する。

**Failure modes**

- 可用性目標だけがあり、復旧手順とテストがない。
- バックアップはあるが restore が検証されていない。
- 単一 dependency の障害が主要サービスの全停止になる。

### 04.07 性能要件

**Definition**: 通常時・ピーク時・劣化時の応答時間、処理量、資源使用量、データ鮮度、ユーザー体感を定量化するレイヤー。

**Frontier pattern**: performance efficiency を、P50/P95/P99 latency、throughput、resource utilization、capacity、cost per transaction、load profile、degradation behavior のセットで定義する。AWS/Azure/Google の Well-Architected と ISO 25010 の performance efficiency を参照する。

**Decision model**

- Inputs: user journey, load forecast, historical traffic, performance baseline, cost target, dependency latency
- Criteria: user-visible impact, percentile target, peak condition, resource efficiency, testability
- Outputs: performance budget, load test profile, latency SLO, capacity plan, profiling evidence
- Owners: Engineering Lead, SRE, Architect, QA Performance Engineer
- Metrics: p50/p95/p99 latency, throughput, saturation, error rate under load, cost per request, load test pass rate

**Implementation rules**

1. 平均 latency だけを要件にしない。重要操作には percentile を定義する。
2. 「同時ユーザー数」だけでは不足。arrival rate、request mix、data volume、think time、dependency behavior を定義する。
3. 性能要件は負荷テスト、profiling、production telemetry に接続する。
4. コスト制約と性能目標の tradeoff を明示する。

**Failure modes**

- peak profile が現実のトラフィックと違う。
- p99 が悪化しているのに平均値で合格する。
- キャッシュや非同期化で correctness / freshness 要件が壊れる。

### 04.08 拡張性・容量要件

**Definition**: 需要増加、データ増加、テナント増加、リージョン増加、機能増加に対して、どの範囲まで安全に拡張できるかを定義するレイヤー。

**Frontier pattern**: scalability を「無限に増える」ではなく、scale unit、quota、limit、autoscaling threshold、capacity forecast、backpressure、tenant isolation、dependency bottleneck として定義する。Well-Architected の performance efficiency / reliability と SLO を接続する。

**Decision model**

- Inputs: growth forecast, tenancy model, data volume forecast, dependency limits, regional expansion plan
- Criteria: scale trigger, bottleneck, isolation, cost elasticity, operational simplicity
- Outputs: capacity model, scale test plan, autoscaling policy, quota model, tenant isolation requirements
- Owners: Architect, SRE, Platform Lead, Product
- Metrics: max sustainable throughput, scale-out time, capacity headroom, quota breach count, noisy-neighbor incidents

**Implementation rules**

1. scale dimension を明示する。users、requests/sec、tenants、records、storage、regions、models、events/sec は別物である。
2. 各 dimension に limit、warning threshold、hard quota、degradation behavior を定義する。
3. Autoscaling は cooldown、scale metric、manual override、cost guardrail を持つ。
4. Backpressure、rate limit、queue limits を設計要件に含める。

**Failure modes**

- 水平スケール可能と言いながら database、queue、license、third-party API が bottleneck になる。
- テナント分離がなく、noisy neighbor が SLA 事故になる。
- growth forecast が product planning と接続していない。

### 04.09 保守性・変更容易性要件

**Definition**: システムを安全・迅速・低コストに解析、修正、テスト、再利用、移行できる条件を定義するレイヤー。

**Frontier pattern**: ISO 25010 の maintainability と flexibility、ATAM の modifiability tradeoff、Azure/AWS/Google の architecture review を組み合わせ、保守性を「コード品質」ではなく change economics として管理する。

**Decision model**

- Inputs: expected change scenarios, dependency map, modular boundaries, team topology, technical debt, compliance needs
- Criteria: change frequency, blast radius, testability, dependency risk, cognitive load, lifecycle cost
- Outputs: modifiability scenarios, architecture boundaries, testability requirements, dependency policy, deprecation/migration plan
- Owners: Architect, Engineering Lead, QA, Platform Lead
- Metrics: lead time for change, change failure rate, test coverage, dependency freshness, code churn hotspots, migration effort

**Implementation rules**

1. 変更シナリオを要件化する。例: tax rate rule を 1営業日以内に変更できる。
2. API、schema、configuration、policy、business rules を分離する。
3. Testability を機能要件の後に追加せず、設計要件に入れる。
4. Deprecated component には retirement date、migration guide、consumer inventory を持たせる。

**Failure modes**

- 初期速度を優先し、変更頻度の高いルールがコードに埋まる。
- dependency 更新方針がなく、セキュリティと互換性が劣化する。
- 仕様変更の影響範囲を把握できない。

### 04.10 監査・証跡要件

**Definition**: システム・組織・ユーザー・管理者の重要行為を、事後検証、インシデント調査、規制対応、顧客保証に使える形で記録・保全するレイヤー。

**Frontier pattern**: ISO 19011 の audit program、NIST SP 800-92 の log management、NIST SP 800-53 の audit/accountability controls、SOC 2 TSC の assurance requirements を統合し、監査を「ログ保存」ではなく evidence lifecycle として扱う。

**Decision model**

- Inputs: control requirements, threat model, legal obligations, customer assurance, data access patterns, privileged actions
- Criteria: evidentiary value, tamper resistance, privacy minimization, retention obligation, investigation usefulness
- Outputs: audit event taxonomy, log retention policy, evidence store, audit review procedure, access review evidence
- Owners: GRC, Security, SRE, Internal Audit, Data Governance
- Metrics: audit event coverage, log ingestion completeness, log tamper incidents, evidence retrieval time, audit finding closure time

**Implementation rules**

1. Audit log は事後に推測できない事実を残す。actor、target、action、timestamp、source、reason、approval、before/after を基本にする。
2. 監査ログ自体にアクセス制御、改ざん耐性、保持、削除例外を設定する。
3. 個人データアクセスログは privacy requirement と衝突するため、目的・保持期間・アクセス権限を明示する。
4. Audit evidence は policy、ticket、test result、configuration snapshot、log、meeting record を含む。

**Failure modes**

- ログはあるが time sync がなく、証拠性が低い。
- 監査ログの保持期間が短すぎて incident 調査に使えない。
- ログに個人データを過剰に入れ、プライバシーリスクを増やす。

### 04.11 法務要件

**Definition**: 法令、規制、契約、開示義務、知財、輸出規制、消費者保護、製品責任、業法、アクセシビリティ等をシステム要求へ変換するレイヤー。

**Frontier pattern**: legal obligation を「遵守する」ではなく、system implication に変換する。DORA、NIS2、CRA、SEC cyber disclosure、PCI DSS、GDPR/APPI、AI Act 等の義務を、feature、control、logging、reporting、documentation、governance、notification deadline へ割り当てる。

**Decision model**

- Inputs: jurisdiction, entity type, industry, product category, customer sector, data category, contract, listing status
- Criteria: legal binding force, deadline, penalty, user impact, implementation impact, evidence burden
- Outputs: obligation matrix, legal review checklist, release gate, disclosure runbook, contract requirement mapping
- Owners: Legal Counsel, Compliance, Product, Security, Privacy
- Metrics: obligation mapping coverage, legal review SLA, unresolved legal blockers, regulatory change lead time, missed disclosure deadlines

**Implementation rules**

1. Legal requirement は `obligation` と `system implication` に分ける。
2. 「適用なし」の判断にも根拠、承認者、見直し日を残す。
3. インシデント報告/開示義務は incident response runbook と接続する。
4. 製品セキュリティ規制は product lifecycle、update mechanism、vulnerability handling、technical documentation に接続する。
5. AI/automated decisioning を含む場合は、AI Act、NIST AI RMF、sector rules を screen する。

**Failure modes**

- 法務要件が契約締結時だけレビューされ、実装/運用に流れない。
- 法域拡大時に既存機能の privacy/retention/legal impact が再評価されない。
- 開示義務の期限を検知する operational trigger がない。

### 04.12 プライバシー要件

**Definition**: 個人データ処理に関する目的、法的根拠、最小化、透明性、権利対応、移転、安全管理、リスク評価を定義するレイヤー。

**Frontier pattern**: NIST Privacy Framework と ISO/IEC 27701 を enterprise risk / PIMS の骨格とし、GDPR/EDPB/European Commission guidance と APPI/PPC guidance を具体義務に使う。privacy-by-design を data model、access control、consent/preference、DSR workflow、retention schedule に変換する。

**Decision model**

- Inputs: data inventory, processing purpose, legal basis, user rights, transfer, processor/subprocessor, privacy risk
- Criteria: lawfulness, fairness, transparency, purpose limitation, data minimization, accuracy, storage limitation, integrity/confidentiality, accountability
- Outputs: privacy requirement baseline, DPIA/PIA, data-flow diagram, privacy notice requirements, DSR workflow, processor controls
- Owners: Privacy Officer / DPO, Legal, Data Governance, Security, Product
- Metrics: personal data inventory coverage, DSR SLA compliance, DPIA completion, consent/preference accuracy, privacy incident count, access review findings

**Implementation rules**

1. 個人データを扱う機能は、purpose、legal basis、data category、retention、access path、third-party sharing を持つ。
2. 新しいデータ処理、sensitive data、AI profiling、cross-border transfer、large-scale monitoring は DPIA/PIA trigger にする。
3. Data subject rights は UI/サポート/バックオフィス/データ基盤すべてに影響するため、機能要件として設計する。
4. プライバシー要件は security requirement と重なるが、同一ではない。confidentiality だけで privacy compliance は満たせない。

**Failure modes**

- データ最小化の判断が実装者の裁量に任される。
- DSR 要求に対してバックアップ、ログ、第三者提供先、アーカイブが対象外扱いになる。
- privacy notice と実際のデータフローが一致しない。

### 04.13 データ保持・削除要件

**Definition**: データをいつまで、なぜ、どこに、どの形式で保持し、いつ・どの方法で削除・匿名化・サニタイズするかを定義するレイヤー。

**Frontier pattern**: GDPR/EDPB/EC guidance の storage limitation、APPI/PPC の安全管理・記録、NIST SP 800-88 の media sanitization、NIST SP 800-92 の log retention/log management を組み合わせ、retention schedule を product/data platform/control evidence に接続する。

**Decision model**

- Inputs: data category, processing purpose, legal basis, contract, tax/accounting law, audit obligation, legal hold, security investigation need
- Criteria: minimum necessary retention, statutory retention, evidence needs, user rights, deletion feasibility, backup/archive constraints
- Outputs: retention schedule, deletion/anonymization requirements, legal hold procedure, backup deletion policy, media sanitization certificate
- Owners: Data Governance, Legal, Privacy, Security, SRE
- Metrics: data class coverage, deletion SLA compliance, retention exceptions, stale data findings, successful deletion/anonymization evidence, legal hold accuracy

**Implementation rules**

1. 各データクラスに retention period、start event、end event、delete/anonymize action、exception、evidence を定義する。
2. バックアップとアーカイブを retention 対象から除外しない。restore 時の再削除/再匿名化も設計する。
3. Legal hold は retention extension であり、owner、case id、expiry/review を持つ。
4. 監査ログは privacy と security の両方の観点で保持期間を決める。
5. 媒体廃棄はサニタイズ方法、検証、証明、chain of custody を記録する。

**Failure modes**

- retention policy はあるが実装されていない。
- ユーザー削除後にバックアップや分析基盤に個人データが残る。
- 監査証跡とプライバシー削除が衝突したときの例外ルールがない。

## 10. Metrics

| Metric | Layer | Definition | Use |
|---|---|---|---|
| Orphan requirement rate | 04 | source または owner のない要件比率 | 台帳品質 |
| Acceptance criteria coverage | 04.01 | acceptance criteria を持つ機能要件比率 | 検証可能性 |
| Quality scenario coverage | 04.02 | P0/P1/P2 品質要件のうち scenario 化済み比率 | NFR 品質 |
| Constraint waiver age | 04.03 | waiver の平均経過日数と期限超過数 | 制約管理 |
| SLO compliance | 04.04 | target window 内の SLO 達成率 | 信頼性管理 |
| Error budget burn rate | 04.04 | error budget 消費速度 | リリース/運用判断 |
| Control coverage | 04.05 | 適用 control の実装・検証済み比率 | セキュリティ準拠 |
| Critical vulnerability age | 04.05 | critical/high vulnerability の未修正期間 | セキュリティ運用 |
| Customer-impact minutes | 04.06 | ユーザー影響ありの停止/劣化時間 | 可用性 |
| RTO/RPO test success | 04.06 | DR/restore test の目標達成率 | 復旧能力 |
| p95/p99 latency | 04.07 | 主要操作の percentile latency | 体感性能 |
| Capacity headroom | 04.08 | 現在需要に対する余力 | 拡張性 |
| Change lead time | 04.09 | 要求から安全な release までの時間 | 保守性 |
| Change failure rate | 04.09 | 変更が障害/rollback に至った比率 | 保守性 |
| Audit evidence retrieval time | 04.10 | 監査証跡取得にかかる時間 | 監査準備性 |
| Legal obligation mapping coverage | 04.11 | 適用義務のうち実装/証拠に接続済み比率 | 法務要件管理 |
| DSR SLA compliance | 04.12 | データ主体権利要求の期限内完了率 | プライバシー運用 |
| Retention rule coverage | 04.13 | データクラスのうち retention rule を持つ比率 | 保持管理 |
| Deletion evidence pass rate | 04.13 | 削除/匿名化テストで証拠確認できる比率 | 削除実効性 |

## 11. Failure Modes

| Failure mode | Typical cause | Detection | Prevention / Control |
|---|---|---|---|
| Vague NFR | 形容詞だけの要求、品質モデル不在 | NFR review で response measure がない | QAS template 必須化 |
| Contract-SLO mismatch | 営業 SLA と内部運用の不整合 | SLA に対応する SLI/SLO がない | SLA gate に SRE/Legal/Finance 承認 |
| Security as late gate | security review が終盤だけ | リリース直前の blocker 増加 | threat modeling and ASVS/NIST mapping at design |
| Privacy blind spot | data inventory 不備 | DSR 対象外データが発見される | data-flow review and privacy gate |
| Retention over-collection | indefinite retention, unclear purpose | stale data finding, storage growth | retention schedule + deletion automation |
| Audit evidence gap | log schema/evidence store 不備 | 監査時に証拠収集不能 | audit event taxonomy + evidence plan |
| Reliability theater | DR plan 未テスト | restore failure, RTO 未達 | quarterly restore/failover exercise |
| Performance surprise | production-like load test 不足 | launch incident, p99 degradation | performance budget and load profile |
| Scalability bottleneck | dependency limit 未把握 | quota breach, queue saturation | capacity model, limit register |
| Maintainability debt | architecture tradeoff 未記録 | change lead time 増大 | modifiability scenarios, ADR |
| Legal applicability error | jurisdiction/entity/product scope 誤認 | external counsel/audit finding | obligation matrix with review cadence |
| Waiver drift | 例外期限なし | expired waiver, compensating control missing | waiver expiry and review automation |

## 12. Anti-patterns

- 「NFR は非機能だから後でテストする」
- 「SLA は営業資料、SLO はエンジニアリング資料」と分断する
- 「規制準拠」は法務の承認印であり、システム挙動ではないと考える
- 個人データ retention を「必要な限り」とだけ書く
- 監査ログにすべてを入れ、プライバシー最小化とアクセス制御を無視する
- ASVS/NIST/ISO の control ID を貼るだけで、テスト・証拠・owner を作らない
- 可用性 SLO を定めるが、RTO/RPO/backup restore を定めない
- 性能要件を平均値で表し、percentile と peak condition を無視する
- 拡張性を「cloud なのでスケールする」と表現する
- 保守性をコードレビューだけで管理し、変更シナリオを要件化しない
- 法規制の適用範囲を一度だけ判断し、国・顧客・製品・データの変更時に再評価しない

## 13. Maturity Model

| Level | Name | Criteria |
|---:|---|---|
| 0 | 未整備 | 要件は口頭・チケット断片。NFR、法務、プライバシー、保持はリリース直前に発見される。 |
| 1 | 個人依存 | PO/architect/security/legal の経験でレビューするが、標準テンプレートや evidence store がない。 |
| 2 | 文書化 | requirements register、NFR checklist、SLO catalog、privacy checklist、retention policy はあるが、トレーサビリティが弱い。 |
| 3 | 標準化 | ISO/IEC/IEEE 29148 型の要件属性、ISO 25010/QAW 型 NFR、NIST/OWASP/ISO control mapping、obligation matrix が標準運用される。 |
| 4 | 自動化・計測 | 要件 completeness、SLO、security controls、privacy inventory、retention deletion、audit evidence がメトリクス化・一部自動検証される。 |
| 5 | 自律改善・業界先端 | incident/audit/regulatory change/customer feedback が自動的に要件台帳へ feedback され、tradeoff と evidence が継続更新される。 |

## 14. Clone Implementation Guide

### 14.1 First 30 Days: Baseline and visibility

1. 04 の requirements register を作り、既存要件を分類する。
2. P0/P1 サービスの SLA/SLO/SLI の棚卸しを行う。
3. 個人データ、決済データ、規制対象データの data inventory を作る。
4. Security baseline を OWASP ASVS / NIST / ISO 27001 のいずれかにマップする。
5. Regulatory obligation matrix の初版を作る。最低限、対象法域、契約、業法、顧客保証、開示義務を入れる。
6. Retention schedule の初版を作る。unknown は unknown として明示し、暫定期限を置く。

### 14.2 Days 31–60: Scenario and control conversion

1. P0/P1/P2 要件に quality attribute scenario を付与する。
2. SLI/SLO と alerting を定義し、error budget policy を試行する。
3. threat model と privacy impact screen を major feature に必須化する。
4. audit event taxonomy を作り、特権操作、個人データアクセス、設定変更、削除操作を最低対象にする。
5. control-to-evidence matrix を作る。control ID、implementation、test、evidence、owner を持たせる。

### 14.3 Days 61–90: Gates and feedback loop

1. Release gate に requirements completeness、security、privacy、SLO readiness、retention impact を入れる。
2. DR/restore test を実施し、RTO/RPO evidence を保存する。
3. performance/load test profile を主要 user journey へ適用する。
4. legal/regulatory watch cadence を設定し、規制変更が requirement intake に入るようにする。
5. audit sampling を実施し、evidence retrieval time と gaps を測る。

### 14.4 Operating cadence after 90 days

- 週次: requirements quality review、waiver review、new feature risk screen
- 月次: SLO/error budget review、security/privacy control evidence health、capacity review
- 四半期: QAW/ATAM-lite、retention review、DR/restore test、regulatory obligation update
- 年次: full audit readiness、SOC/ISO/FedRAMP/PCI 等の外部保証準備、policy refresh

## 15. Pattern Library

| Pattern ID | Pattern | Scope | Description | Preconditions | Tradeoffs | Confidence |
|---|---|---|---|---|---|---|
| P01 | Requirement-as-contract | 04 | 要件に source/owner/acceptance/verification/evidence を持たせる | requirements register | 初期入力コスト増 | A |
| P02 | Quality Attribute Scenario | 04.02,04.06–04.09 | NFR を刺激・環境・応答・測定値へ変換 | stakeholder workshop | 抽象 NFR より時間がかかる | A |
| P03 | SLO/Error Budget Governance | 04.04,04.06,04.07 | SLO と error budget でリリース速度と信頼性を調整 | production telemetry | 経営/営業との調整が必要 | A |
| P04 | Control-to-Evidence Mapping | 04.05,04.10–04.13 | control ID を実装、テスト、ログ、証拠へ接続 | control baseline | GRC と engineering の連携が必要 | A |
| P05 | Obligation Matrix | 04.11–04.13 | 法務・規制要求を system implication に変換 | legal counsel review | 法域ごとの専門性が必要 | A |
| P06 | Retention-as-Code | 04.12,04.13 | retention rule を data catalog / policy / deletion workflow に接続 | data inventory | legacy data の移行が難しい | B |
| P07 | Waiver with Expiry | 04.03,04.05,04.11 | 例外に期限・補償統制・承認者を必須化 | risk owner | 短期的な delivery friction | A |
| P08 | Audit Event Taxonomy | 04.10 | 重要操作を event schema と保持方針へ落とす | logging pipeline | privacy/log volume tradeoff | A |
| P09 | DR Evidence Loop | 04.04,04.06,04.13 | RTO/RPO/backup を定期テスト証拠にする | SRE/BC owner | テストコスト | A |
| P10 | Maintainability Scenario | 04.09 | 変更要求を時間・影響・テスト容易性で要件化 | architecture ownership | 初期設計制約増 | B |

## 16. Validation Queries

次のクエリを、対象組織・対象プロダクト・対象法域ごとに置換して実行する。

```text
site:{official_domain} "requirements engineering" "ISO/IEC/IEEE 29148"
site:{official_domain} "quality attributes" "availability" "performance" "security"
site:{official_domain} "SLO" "error budget" "service level objective"
site:{official_domain} "availability" "RTO" "RPO" "disaster recovery"
site:{official_domain} "performance" "p95" OR "p99" "latency"
site:{official_domain} "ASVS" OR "NIST SP 800-53" OR "ISO 27001" "control"
site:{official_domain} "privacy" "retention" "deletion" "data subject"
site:{official_domain} "audit log" "retention" "privileged access"
site:{official_domain} "DORA" OR "NIS2" OR "Cyber Resilience Act" OR "SEC cybersecurity"
"{candidate}" (incident OR outage OR breach OR CVE OR lawsuit OR rollback OR deprecation)
"{candidate}" "SLA" "service credits" "availability"
"{candidate}" "retention policy" "delete" "anonymize"
"{candidate}" "SOC 2" "Trust Services Criteria" "availability" "privacy"
"{candidate}" "subprocessor" "DPA" "data retention"
"{candidate}" "security advisory" "postmortem" "root cause"
```

## 17. QA Checklist

| Check | Pass condition |
|---|---|
| Coverage | 04 の各 layer に source、owner、artifact、metric がある |
| Critical claim | P0/P1 の主張は T0/T1/T2/T3 の A/B confidence で裏付ける |
| Traceability | 重要要件が source → requirement → test/control/log → evidence へ接続されている |
| Recency | 規制・標準・クラウド公式文書は current canonical を確認する |
| Exceptions | waiver、legal hold、security exception、SLA exception が期限付きで管理される |
| Failure | incident/outage/breach/deprecation の反証検索を行う |
| Privacy | personal data 処理に purpose/legal basis/retention/deletion/access control がある |
| SLO | external SLA に internal SLI/SLO/error budget が対応している |
| Audit | audit event taxonomy と evidence retrieval process がある |
| Output integrity | Clone Spec に decision model、operating model、metrics、failure modes、unknowns がある |

## 18. Confidence & Unknowns

### Confidence A

- ISO/IEC/IEEE 29148、ISO/IEC 25010、NIST CSF/SP 800-53/SP 800-218、OWASP ASVS、ISO/IEC 27001/27701、ISO 22301、ISO 19011、GDPR/EDPB/EC guidance、APPI/PPC guidance、DORA/NIS2/CRA/SEC cyber disclosure は、公開された公式・準公式・規範ソースで確認できる。
- SLO/error budget、quality attribute workshop、ATAM は公開された公式資料で手法として確認できる。

### Confidence B

- 「frontier pattern」としての統合運用モデルは、複数ソースを組み合わせた合成である。個別ソースがこの統合モデルをそのまま規定しているわけではない。
- 04 の layer names は、ユーザー提示サブテーマからの作業割当である。別の canonical layer registry があれば名称は更新が必要である。

### Unknowns / 追加調査

- 対象企業、対象プロダクト、対象法域、対象顧客セクターが未指定のため、具体的な SLA 値、保持期間、規制適用範囲、法的根拠は確定していない。
- 日本 APPI は 2026 年時点で改正議論・改正案が存在し得るため、実装時は PPC、官報、弁護士確認で current law を確定する必要がある。
- EU digital regulation は AI Act / GDPR / CRA / NIS2 / DORA 周辺で施行日・適用詳細・ガイダンス更新が続くため、実装時は official source と外部 counsel で再確認する必要がある。
- SOC 2、PCI DSS、FedRAMP、CSA CCM などは対象市場・顧客要求により要否が変わる。

## 19. Minimal Clone Spec Summary

このレイヤー群を自組織で複製する場合、最初に作るべきものは次の 12 個である。

1. Requirements Register
2. Quality Attribute Scenario Register
3. Constraint Register
4. SLI/SLO Catalog
5. Security Requirements Baseline
6. Privacy Requirements Baseline
7. Regulatory Obligation Matrix
8. Retention Schedule
9. Audit Event Taxonomy
10. Control-to-Evidence Matrix
11. Waiver Register
12. ADR / Tradeoff Register

これらが揃うと、機能、品質、SLA、セキュリティ、可用性、性能、拡張性、保守性、監査、法務、プライバシー、保持のすべてを、単なるドキュメントではなく、**実装可能・検証可能・監査可能な意思決定システム**として運用できる。
