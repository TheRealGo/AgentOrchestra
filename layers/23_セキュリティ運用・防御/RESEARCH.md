# Frontier Operating Model Research: セキュリティ運用・防御（Layers 23）

Generated: 2026-05-13  
Scope: vulnerability / patch management、threat detection、incident response、SIEM、IDS/IPS、EDR、DLP、zero trust、network / endpoint / application / data security  
Method: `RESEARCH.md` の公開情報限定・証拠階層・Clone Spec 形式に従い、NIST / CISA / MITRE / FIRST / CIS / OWASP / OMB / SEC / 主要公式実装文書を中心に正規化した。

---

## 0. Executive Summary

セキュリティ運用・防御レイヤーの先端運用モデルは、個別ツールの導入ではなく、**資産・脆弱性・ログ・検知・対応・データ分類・アクセス判断を、リスクベースの継続的意思決定システムとして結合すること**で成立する。NIST CSF 2.0 の GOVERN / IDENTIFY / PROTECT / DETECT / RESPOND / RECOVER、NIST SP 800-137 の継続的監視、NIST SP 800-61 Rev.3 のインシデント対応、NIST SP 800-40 Rev.4 のパッチ管理、NIST SP 800-207 と CISA Zero Trust Maturity Model のゼロトラスト、MITRE ATT&CK / D3FEND の攻撃・防御語彙、FIRST CVSS / EPSS と CISA KEV / SSVC の脆弱性優先順位付けが中核証拠である。

14レイヤーを通じた共通の Frontier Pattern は次の6つである。

1. **Asset-first security**: すべての防御判断は、資産、所有者、露出、重要度、データ分類、依存関係から始める。
2. **Evidence-driven prioritization**: CVSS だけでなく、KEV、EPSS、SSVC、実際の露出、業務影響、悪用観測を組み合わせる。
3. **Telemetry-as-control**: SIEM / EDR / IDS / DLP / cloud logs は監査用ログではなく、検知・対応・統制検証の制御面として扱う。
4. **Detection engineering lifecycle**: ATT&CK / D3FEND / Sigma / OCSF 等で検知をコード化し、テスト、バージョン管理、廃止、例外管理を行う。
5. **Response as governance**: インシデント対応はSOCだけの作業ではなく、法務、広報、事業、IT、経営、規制報告を含む意思決定フローである。
6. **Zero Trust convergence**: ネットワーク境界防御を捨てるのではなく、identity / device / network / application / data / visibility / automation / governance を統合して、最小権限・継続的検証・セグメンテーションを実現する。

---

## 1. Layer Registry

| Layer ID | Layer Name | Decision Object | Decision Question | Primary Owners | Primary Outputs |
|---|---|---|---|---|---|
| 23.01 | セキュリティ運用統括 / SOC Operating Model | 組織全体の防御運用設計 | SOCは何を監視し、どのリスク基準で優先し、誰へエスカレーションし、どの指標で改善するか | CISO, SOC Manager, Security Engineering, Risk Owner | SOC charter, detection roadmap, escalation matrix, metrics dashboard |
| 23.02 | 脆弱性管理 | 脆弱性の発見・優先順位・所有者割当 | どの脆弱性を、どの資産・脅威・影響基準で、いつまでに修正または緩和するか | Vulnerability Management Lead, Asset Owner, Product Owner | risk-ranked vulnerability queue, SLA, exceptions, remediation evidence |
| 23.03 | パッチ管理 | パッチ適用の計画・検証・展開 | どのパッチを、どのテスト・展開リング・ロールバック条件で適用するか | IT Ops, Platform Engineering, Change Manager, Security | patch calendar, emergency patch runbook, verification report |
| 23.04 | 脅威検知 / Detection Engineering | 検知ユースケースと検知ロジック | どの攻撃行動を、どのデータソース・ルール・閾値・テストで検知するか | Detection Engineer, Threat Intel, SOC Analyst | ATT&CK coverage map, Sigma/rule repo, detection tests |
| 23.05 | インシデント対応 | インシデント分類・封じ込め・復旧・報告 | 何をインシデントとし、どの重大度で、誰が、どの順序で封じ込め・復旧・通知するか | Incident Commander, SOC, Legal, PR, Business Owner | IR plan, playbooks, comms plan, post-incident review |
| 23.06 | SIEM / ログ管理 | ログ収集・正規化・保管・分析 | どのログを、どの形式・期間・権限・相関規則で扱うか | SIEM Engineer, SOC, Data Platform, Compliance | log source matrix, retention policy, correlation rules, audit trail |
| 23.07 | IDS/IPS | ネットワーク侵入検知・防止 | どの通信を、どのセンサー配置・署名・振る舞い検知・遮断条件で監視/防止するか | Network Security, SOC, Infrastructure | sensor map, ruleset, tuning backlog, inline exception list |
| 23.08 | EDR | エンドポイント検知・対応 | どの端末挙動を、どのリアルタイム監視・自動封じ込め・ハンティングで扱うか | Endpoint Security, SOC, IT Ops | EDR policy, isolation playbook, hunting queries, agent coverage report |
| 23.09 | DLP | データ流出防止ポリシー | どの機密データを、どの場所・活動・利用者・例外条件で監視/ブロックするか | Data Protection, Privacy, Compliance, Security | DLP policy set, incident queue, exception registry, tuning report |
| 23.10 | Zero Trust | 継続的アクセス判断 | 誰が、どの端末から、どの資源へ、どの文脈でアクセスできるかをどう継続検証するか | CISO, IAM, Network, Endpoint, App, Data Owners | ZT roadmap, policy decision model, microsegmentation plan |
| 23.11 | ネットワークセキュリティ | ネットワーク境界・経路・管理面防御 | どのネットワーク通信・管理面・セグメントを、どのポリシーで許可/拒否/監査するか | Network Security, NetOps, Cloud Network | firewall policy, segmentation model, device hardening baseline |
| 23.12 | エンドポイントセキュリティ | 端末の構成・実行制御・マルウェア防御 | 端末で何を許可し、何を実行禁止し、どの構成逸脱を修正するか | Endpoint Engineering, IT Ops, Security | secure baseline, app control policy, malware defense policy |
| 23.13 | アプリケーションセキュリティ | セキュア開発・検証・リリース判断 | アプリをどの設計・実装・依存関係・テスト・リリース基準で安全にするか | AppSec, Product Security, Engineering | threat model, security requirements, test results, SBOM/attestation |
| 23.14 | データセキュリティ | データ分類・保護・保持・廃棄 | データをどの分類・暗号・アクセス・保持・廃棄ルールで保護するか | Data Governance, Privacy, Security, Legal | data inventory, classification policy, encryption/key policy, disposal evidence |

---

## 2. Source Catalog（主要証拠）

| Source ID | Entity | Source / Artifact | Type | Tier | Primary Use |
|---|---|---|---|---|---|
| S01 | NIST | [Cybersecurity Framework 2.0](https://www.nist.gov/cyberframework) / [CSWP 29 PDF](https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf) | standard / framework | T0 | 共通アウトカム、GOVERN/IDENTIFY/PROTECT/DETECT/RESPOND/RECOVER |
| S02 | NIST | [SP 800-137 Information Security Continuous Monitoring](https://csrc.nist.gov/pubs/sp/800/137/final) | official guide | T0 | 継続監視、資産・脅威・脆弱性・統制有効性の可視化 |
| S03 | CISA | [Continuous Diagnostics and Mitigation Program](https://www.cisa.gov/resources-tools/programs/continuous-diagnostics-and-mitigation-cdm-program) | public program | T3/T5 | 継続診断、ダッシュボード、政府規模のセキュリティ態勢可視化 |
| S04 | MITRE | [ATT&CK](https://attack.mitre.org/) | knowledge base | T0/T5 | 攻撃戦術・技術・データソース・検知戦略 |
| S05 | MITRE | [D3FEND](https://d3fend.mitre.org/) | defensive knowledge graph | T0/T5 | 防御技術、countermeasure 語彙 |
| S06 | OCSF | [Open Cybersecurity Schema Framework](https://ocsf.io/) | schema / OSS | T0/T2 | セキュリティイベントの正規化スキーマ |
| S07 | SigmaHQ | [Sigma Detection Format](https://sigmahq.io/docs/basics/rules.html) / [rule repository](https://github.com/SigmaHQ/sigma) | OSS / rule format | T2/T3 | SIEM非依存の検知ルール記述 |
| S08 | NIST | [SP 800-40 Rev.4 Enterprise Patch Management Planning](https://csrc.nist.gov/pubs/sp/800/40/r4/final) | official guide | T0 | パッチ管理プロセス |
| S09 | CISA | [Known Exploited Vulnerabilities Catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) | official catalog | T0/T2 | 悪用確認済み脆弱性の優先対応 |
| S10 | CISA | [BOD 23-01 Asset Visibility and Vulnerability Detection](https://www.cisa.gov/news-events/directives/bod-23-01-implementation-guidance-improving-asset-visibility-and-vulnerability-detection-federal) | directive / guide | T0/T3 | 資産可視化・脆弱性列挙の運用基準 |
| S11 | FIRST | [CVSS v4.0 Specification](https://www.first.org/cvss/specification-document) | standard | T0 | 脆弱性特性・深刻度の標準表現 |
| S12 | CISA / CERT/CC | [Stakeholder-Specific Vulnerability Categorization](https://www.cisa.gov/sites/default/files/publications/cisa-ssvc-guide%20508c.pdf) | guide / decision model | T0 | 脆弱性対応優先度の意思決定木 |
| S13 | FIRST | [EPSS](https://www.first.org/epss/) / [model](https://www.first.org/epss/model) | model / data | T0/T2 | CVEの今後30日悪用確率推定 |
| S14 | NIST | [SP 800-61 Rev.3 Incident Response Recommendations](https://csrc.nist.gov/pubs/sp/800/61/r3/final) | official guide | T0 | IRとサイバーリスク管理の統合 |
| S15 | CISA | [Federal Government Cybersecurity Incident & Vulnerability Response Playbooks](https://www.cisa.gov/planning-response-recovery) | playbook | T3 | 標準化されたIR/Vulnerability response |
| S16 | SEC | [Cybersecurity Risk Management, Strategy, Governance, and Incident Disclosure Final Rule](https://www.sec.gov/rules-regulations/2023/07/s7-09-22) | regulation | T1 | 重要インシデント開示・ガバナンス開示 |
| S17 | ENISA / EU | [Threats and Incidents / NIS2 reporting](https://www.enisa.europa.eu/topics/state-of-cybersecurity-in-the-eu/threats-and-incidents) | regulator guidance | T1/T3 | 24h/72h等の重大インシデント報告モデル |
| S18 | NIST | [SP 800-92 Computer Security Log Management](https://csrc.nist.gov/pubs/sp/800/92/final) | official guide | T0 | ログ管理プログラム |
| S19 | OMB | [M-21-31 Event Logging](https://www.whitehouse.gov/wp-content/uploads/2021/08/M-21-31-Improving-the-Federal-Governments-Investigative-and-Remediation-Capabilities-Related-to-Cybersecurity-Incidents.pdf) | government memo | T1/T3 | ログ取得・保管・管理成熟度モデル |
| S20 | CISA | [Logging Made Easy](https://cisagov.github.io/lme-docs/) / [GitHub](https://github.com/cisagov/LME) | OSS / implementation | T2/T3 | 小中規模向けログ集中・検知実装 |
| S21 | NIST | [SP 800-94 Intrusion Detection and Prevention Systems](https://csrc.nist.gov/pubs/sp/800/94/final) | official guide | T0 | IDS/IPS設計・導入・監視・維持 |
| S22 | OISF | [Suricata](https://suricata.io/) / [docs](https://docs.suricata.io/) | OSS | T2/T3 | IDS/IPS/NSM 実装例 |
| S23 | Snort | [Snort](https://www.snort.org/) | OSS | T2/T3 | NIDS/NIPS 実装例 |
| S24 | Zeek | [Zeek Network Security Monitor](https://zeek.org/) / [docs](https://docs.zeek.org/en/current/about.html) | OSS | T2/T3 | ネットワーク監視・SIEM連携ログ |
| S25 | OMB / White House | [M-22-01 EDR implementation guidance](https://www.whitehouse.gov/wp-content/uploads/2021/10/M-22-01.pdf) / [EO 14144 definition](https://www.presidency.ucsb.edu/documents/executive-order-14144-strengthening-and-promoting-innovation-the-nations-cybersecurity) | government memo / EO | T1/T3 | EDRの導入・定義・政府規模の可視化 |
| S26 | NIST | [SP 800-83 Rev.1 Malware Incident Prevention and Handling](https://csrc.nist.gov/pubs/sp/800/83/r1/final) | official guide | T0 | マルウェア予防・対応 |
| S27 | NIST | [SP 800-167 Application Whitelisting](https://csrc.nist.gov/pubs/sp/800/167/final) | official guide | T0 | アプリケーション許可リスト / 実行制御 |
| S28 | CIS | [Control 4 Secure Configuration](https://www.cisecurity.org/controls/secure-configuration-of-enterprise-assets-and-software) | control | T0/T5 | エンタープライズ資産とソフトウェアの安全構成 |
| S29 | CIS | [Control 10 Malware Defenses](https://www.cisecurity.org/controls/malware-defenses) | control | T0/T5 | マルウェア防御 |
| S30 | Microsoft | [Defender Attack Surface Reduction](https://learn.microsoft.com/en-us/defender-endpoint/attack-surface-reduction) | vendor official doc | T2/T3 | ASRの監査・警告・ブロック・除外運用 |
| S31 | Microsoft | [Purview Data Loss Prevention](https://learn.microsoft.com/en-us/purview/dlp-learn-about-dlp) | vendor official doc | T2/T3 | DLPポリシー・アラート・調査ライフサイクル |
| S32 | NIST | [SP 800-122 Protecting PII](https://csrc.nist.gov/pubs/sp/800/122/final) | official guide | T0 | PIIの識別・保護レベル・インシデント計画 |
| S33 | NIST | [SP 800-111 Storage Encryption](https://csrc.nist.gov/pubs/sp/800/111/final) | official guide | T0 | 保存データ暗号化 |
| S34 | NIST | [SP 800-88 Rev.1 Media Sanitization](https://csrc.nist.gov/pubs/sp/800/88/r1/final) | official guide | T0 | データ廃棄・媒体サニタイズ |
| S35 | NIST | [SP 800-207 Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/800/207/final) | official guide | T0 | ゼロトラスト原則 |
| S36 | CISA | [Zero Trust Maturity Model 2.0](https://www.cisa.gov/resources-tools/resources/zero-trust-maturity-model) | maturity model | T0/T3 | ZT実装ロードマップ |
| S37 | DoD CIO | [DoD Zero Trust Strategy](https://dodcio.defense.gov/Portals/0/Documents/Library/DoD-ZTStrategy.pdf) | government strategy | T1/T3 | 大規模ZT移行モデル |
| S38 | NIST | [SP 800-41 Rev.1 Firewall Policy](https://csrc.nist.gov/pubs/sp/800/41/r1/final) | official guide | T0 | ファイアウォールポリシー・導入・管理 |
| S39 | NSA | [Network Infrastructure Security Guide](https://www.nsa.gov/Press-Room/News-Highlights/Article/Article/2949885/nsa-details-network-infrastructure-best-practices/) | government guide | T0/T3 | ネットワークデバイス設計・設定ハードニング |
| S40 | CIS | [Control 12 Network Infrastructure Management](https://www.cisecurity.org/controls/network-infrastructure-management) | control | T0/T5 | ネットワーク機器の管理・追跡・修正 |
| S41 | NIST | [SP 800-53 Rev.5 Controls](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final) | control catalog | T0 | セキュリティ/プライバシー管理策カタログ |
| S42 | NIST | [SP 800-171 Rev.3 CUI Protection](https://csrc.nist.gov/pubs/sp/800/171/r3/final) | official guide | T0/T1 | CUI保護要件 |
| S43 | NIST | [SP 800-218 SSDF](https://csrc.nist.gov/pubs/sp/800/218/final) | official guide | T0 | セキュアソフトウェア開発 |
| S44 | OWASP | [ASVS](https://owasp.org/www-project-application-security-verification-standard/) | open standard | T0/T5 | Webアプリ技術管理策検証 |
| S45 | OWASP | [Top 10 Web Application Security Risks](https://owasp.org/www-project-top-ten/) | community standard | T0/T5 | 主要Webアプリリスク |
| S46 | SLSA | [Supply-chain Levels for Software Artifacts](https://slsa.dev/) / [spec v1.2](https://slsa.dev/spec/v1.2/) | specification | T0/T5 | ソフトウェアサプライチェーン完全性 |
| S47 | OpenSSF | [Scorecard](https://scorecard.dev/) | OSS / benchmark | T2/T5 | OSSプロジェクトのセキュリティリスク自動評価 |
| S48 | CISA | [Secure by Design](https://www.cisa.gov/securebydesign) / [Secure by Demand](https://www.cisa.gov/resources-tools/resources/secure-demand-guide) | official guidance | T0/T3 | ソフトウェア製造者・購買者のセキュリティ要求 |
| S49 | CIS | [Control 3 Data Protection](https://www.cisecurity.org/controls/data-protection) | control | T0/T5 | データ識別・分類・取扱・保持・廃棄 |
| S50 | CISA | [Cybersecurity Performance Goals 2.0](https://www.cisa.gov/cybersecurity-performance-goals-2-0-cpg-2-0) | baseline controls | T0/T5 | 重要インフラ向け優先ベースライン |
| S51 | NIST | [SP 800-204 Microservices Security](https://csrc.nist.gov/pubs/sp/800/204/final) | official guide | T0 | API gateway / service mesh 等のアプリ基盤防御 |

---

## 3. Evidence Map（主要主張）

| Claim ID | Claim | Confidence | Evidence |
|---|---|---|---|
| C-001 | 先端防御運用は、GOVERN/IDENTIFY/PROTECT/DETECT/RESPOND/RECOVERを同時並行で回すアウトカム管理である。 | A | S01 |
| C-002 | セキュリティ態勢の正しさは、資産・脅威・脆弱性・統制有効性を継続監視し、リスク意思決定へ戻すことで判定する。 | A | S02, S03 |
| C-003 | 脆弱性優先度は、CVSSの深刻度だけでなく、既知悪用、悪用確率、資産重要度、組織文脈を組み合わせるべきである。 | A | S09, S11, S12, S13 |
| C-004 | パッチ管理は、識別、優先、取得、テスト、導入、検証、例外、ロールバックまでを含むエンタープライズプロセスである。 | A | S08, S09 |
| C-005 | 検知設計は、攻撃者の戦術・技術、データソース、検知ロジック、正規化スキーマ、テストを接続する必要がある。 | A | S04, S05, S06, S07 |
| C-006 | インシデント対応は、検知・対応・復旧を単発処理でなく、サイバーリスク管理活動へ組み込むべきである。 | A | S14, S15 |
| C-007 | ログ管理は、収集・保管・分析・アクセス・完全性・成熟度を設計する独立した運用能力である。 | A | S18, S19, S20 |
| C-008 | IDS/IPSは、ネットワーク/無線/ネットワーク振る舞い/ホスト型など複数タイプを環境に応じて組み合わせる。 | A | S21, S22, S23, S24 |
| C-009 | EDRは、端末データの継続監視、収集、分析、自動対応を組み合わせて、能動的検知・ハンティング・封じ込めを支える。 | A | S25, S03 |
| C-010 | DLPは、機密データ分類、場所、ユーザー活動、ポリシー条件、アラート調査、チューニングのライフサイクルで運用する。 | A/B | S31, S32, S49 |
| C-011 | Zero Trustは、静的な境界から、ユーザー・資産・リソース中心の継続的な認証・認可へ防御判断を移す。 | A | S35, S36 |
| C-012 | ネットワーク防御は、ファイアウォールポリシー、セグメント、管理面、機器構成、監査、更新を統合して管理する。 | A | S38, S39, S40 |
| C-013 | エンドポイント防御は、マルウェア対策、セキュア構成、アプリケーション許可リスト、攻撃面縮小を組み合わせる。 | A | S26, S27, S28, S29, S30 |
| C-014 | アプリケーション防御は、SSDF、ASVS、Top 10、SLSA、Secure by Design/ Demand を通じて、開発・検証・供給網・購買を一体で扱う。 | A | S43, S44, S45, S46, S48 |
| C-015 | データ防御は、識別、分類、暗号化、アクセス制御、保持、廃棄、PII/CUI等の規制文脈で設計する。 | A | S32, S33, S34, S42, S49 |

---

## 4. Frontier Exemplars and Candidate Scoring

| Candidate / Source Family | Performance | Adoption | Artifact Richness | Peer Validation | Recency | Transferability | Failure Evidence | Weighted Score /100 | Notes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| NIST CSF / SP 800 series | 5 | 5 | 5 | 5 | 4 | 5 | 3 | 94 | セキュリティ運用の規範的ベースライン。実装方法をprescribeしすぎないためClone Specに適する。 |
| CISA KEV / BOD / CPG / ZTMM / CDM | 5 | 4 | 5 | 5 | 5 | 4 | 4 | 93 | 連邦運用を前提にしつつ、実務的な優先順位・成熟度・ダッシュボード思想が強い。 |
| MITRE ATT&CK / D3FEND | 5 | 5 | 5 | 5 | 5 | 5 | 2 | 94 | 検知・防御・脅威モデリングの共通語彙。 |
| FIRST CVSS / EPSS | 4 | 5 | 4 | 5 | 5 | 5 | 3 | 89 | 脆弱性トリアージの標準指標。SSVC/KEVと組み合わせて強い。 |
| CIS Controls | 4 | 5 | 4 | 4 | 5 | 5 | 3 | 86 | 実装可能なベースライン管理策。組織規模ごとのIGにより移植性が高い。 |
| OWASP / OpenSSF / SLSA | 4 | 5 | 5 | 5 | 5 | 5 | 3 | 91 | AppSec/OSS/サプライチェーン領域の再現性が高い。 |
| Microsoft Purview / Defender docs | 4 | 4 | 5 | 3 | 5 | 3 | 3 | 76 | DLP/EDR実装例として有用。ただしベンダ固有性が強いためT2/T3補助証拠扱い。 |
| Suricata / Snort / Zeek / Sigma / OCSF | 4 | 5 | 5 | 4 | 5 | 5 | 3 | 88 | 検知・ログ・IDS/IPS・NSMの実行可能成果物。 |

---

# 5. Clone Specs by Layer

## Layer 23.01: セキュリティ運用統括 / SOC Operating Model

### Definition
組織全体のセキュリティ監視、防御制御、検知、トリアージ、エスカレーション、改善サイクルを束ねる運用設計レイヤー。単なるSOCのチケット処理ではなく、リスク、資産、ログ、検知、対応、例外、経営報告を接続する。

### Frontier Exemplars
NIST CSF 2.0はアウトカム単位でセキュリティ活動を整理し、NIST SP 800-137は継続監視プログラムの目的をリスク意思決定に必要な可視性として定義する。CISA CDMはダッシュボードと継続診断を通じた政府規模の態勢可視化を示す。MITRE ATT&CK/D3FENDはSOCの検知・防御語彙を標準化する。

### Evidence Map
Source refs: S01, S02, S03, S04, S05, S06, S07, S50.  
Confidence: A for outcome taxonomy and ISCM; B for ideal SOC operating model synthesis.

### Core Philosophy
SOCの目的は「すべてのアラートを見る」ことではない。重要資産に対する現実的脅威を、十分なログと検知で早く識別し、封じ込め・復旧・統制改善へ変換することである。先端SOCは、アラート量ではなく、カバレッジ、精度、対応速度、学習速度を管理する。

### Decision Model
- Inputs: asset criticality, threat intelligence, control posture, telemetry coverage, vulnerability backlog, incident history, business criticality.
- Criteria: risk reduction, detectability, response feasibility, regulatory impact, user/business disruption, repeatability.
- Priorities: critical asset coverage > known exploited risk > identity/device telemetry > lateral movement detection > data exfiltration detection.
- Prohibitions: unowned alerts, untested detections, unverifiable control claims, unmanaged exceptions, dashboard-only compliance.
- Exceptions: business-critical outage risk, legal hold, privacy restrictions, regulated data boundaries.
- Owners: CISO, SOC Manager, Detection Engineering Lead, Incident Commander, IT/Cloud/Endpoint owners.
- Cadence: daily triage, weekly detection review, monthly control coverage review, quarterly tabletop and maturity review.

### Operating Model
1. 資産・データ・IDをSOC対象範囲として登録する。  
2. MITRE ATT&CKとD3FENDで検知・防御カバレッジを可視化する。  
3. SIEM/EDR/IDS/DLP/Cloudログのログソースマトリクスを作る。  
4. SOC triage queueを重大度、資産重要度、攻撃段階、ユーザー影響で優先する。  
5. IR/VM/Patch/Data/Legal/PRへのエスカレーション条件を明文化する。  
6. 毎月、未検知事象・誤検知・検知欠落・手戻り・例外を改善backlogへ戻す。

### Technical / Business Specification
- SOC runbook must map alert type → severity → owner → SLA → evidence required → closure criteria.
- Detection repository should be version-controlled and mapped to ATT&CK technique, data source, log field, test case, and owner.
- SOC dashboards must separate: operational queue, control coverage, risk exposure, incident readiness, executive risk summary.
- Tooling must support case management, evidence retention, chain-of-custody, automation hooks, and post-incident metrics.

### Metrics
MTTD, MTTA, MTTC, MTTR, true positive rate, false positive burden, ATT&CK coverage, telemetry coverage by critical asset, alert-to-incident conversion rate, automation success rate, recurring incident count, control improvement closure rate.

### Failure Modes
- Alert fatigue due to unprioritized ingestion.
- Blind spots from unmanaged assets and SaaS/cloud logs.
- Tool sprawl without data normalization.
- Security team closes alerts without asset owner remediation.
- Executive reporting focuses on volume rather than risk reduction.

### Anti-patterns
- SIEM導入をSOC成熟度と同一視する。
- 重大度をツールのデフォルトseverityだけで決める。
- 例外承認が期限・所有者・補償統制なしに残る。
- tabletopやpost-incident reviewの学習を検知/統制へ戻さない。

### Maturity Model
- Level 0: アラート確認が属人化。
- Level 1: 主要ツールの通知を手動処理。
- Level 2: runbook、severity、escalationが文書化。
- Level 3: ATT&CK coverage、ログソース、IR/VM連携が標準化。
- Level 4: detection-as-code、SOAR、coverage metrics、continuous monitoringが自動化。
- Level 5: 脅威・資産・事業影響・統制改善が一体で最適化される。

### Clone Implementation Guide
最初の30日でSOC charter、critical asset list、ログソース棚卸し、アラート分類、エスカレーション表を作る。60日でATT&CK coverageとtop 20 detection use casesを作る。90日で検知repo、post-incident review loop、月次risk dashboardを運用する。

### Confidence & Unknowns
A: CSF/ISCM/ATT&CK/D3FEND/OCSF/Sigmaに基づく構造。  
B: SOC staffing ratiosや自動化閾値は組織依存。  
Unknowns: 個別業界の規制SLA、既存ツール制約、プライバシー制約。

---

## Layer 23.02: 脆弱性管理

### Definition
資産上の脆弱性を発見し、悪用可能性、露出、業務影響、データ影響、補償統制、修正可否に基づいて、修正・緩和・例外・廃止を決めるレイヤー。

### Frontier Exemplars
CISA KEVは実際に悪用された脆弱性を優先するカタログを提供する。FIRST CVSS v4.0は脆弱性特性の標準表現、EPSSはCVEの今後30日の悪用確率、CISA/CERT SSVCはステークホルダー別の対応優先度を意思決定木として扱う。CISA BOD 23-01は資産可視化と脆弱性列挙を運用基盤として位置づける。

### Evidence Map
Source refs: S09, S10, S11, S12, S13, S41.  
Confidence: A for prioritization inputs; B for specific SLA values outside KEV/government context.

### Core Philosophy
脆弱性管理は「スキャン結果の消化」ではない。**攻撃されやすく、重要資産にあり、現実的に到達可能で、影響が大きい弱点を先に減らす**リスク・キュー管理である。

### Decision Model
- Inputs: asset inventory, software inventory, CVE, CVSS, EPSS, KEV, SSVC decision points, external exposure, exploit maturity, business owner, data sensitivity, compensating controls.
- Criteria: known exploitation, internet exposure, privilege impact, business criticality, exploit likelihood, patch availability, operational risk.
- Priorities: KEV/exploited > externally exposed critical assets > high EPSS + high impact > privileged path > regulated data systems.
- Prohibitions: CVSS-only prioritization, ownerless findings, indefinite risk acceptance, unverifiable remediation.
- Exceptions: patch unavailable, unsupported legacy system, operational safety risk, compensating control with expiry.
- Owners: Vulnerability Manager, Asset Owner, Product/Service Owner, IT Ops, Risk Approver.
- Cadence: continuous scanning for external assets; weekly internal risk queue; monthly exception review; quarterly coverage audit.

### Operating Model
1. 資産・ソフトウェア・所有者・外部露出・データ分類を紐づける。  
2. CVEをCVSS/EPSS/KEV/SSVC/asset criticalityで正規化する。  
3. 修正、設定変更、ネットワーク隔離、検知強化、廃止を選択肢にする。  
4. SLAはseverityではなくrisk tierごとに設定する。  
5. 修正完了はチケット完了ではなく、再スキャン、バージョン証拠、設定証拠、到達不能証拠で確認する。  
6. 例外は期限、補償統制、残余リスク、承認者を必須にする。

### Technical / Business Specification
- Vulnerability record fields: CVE/CWE, asset ID, owner, exposure, exploit status, CVSS vector, EPSS, KEV due date, SSVC outcome, data classification, remediation option, evidence, exception expiry.
- Integrations: asset inventory, CMDB, EDR, cloud asset inventory, scanner, ticketing, SIEM, patch platform.
- Risk queue must be deduplicated by asset/service and aggregated by business service to avoid ticket noise.

### Metrics
Asset coverage, scan freshness, vulnerability enumeration coverage, KEV SLA compliance, high-risk MTTR, remediation verification rate, exception age, unsupported asset count, internet-exposed critical vulnerabilities, reopen rate.

### Failure Modes
- スキャン済みだが資産所有者が不明。
- CVSS Criticalを大量処理し、実悪用KEVを遅らせる。
- クラウド/コンテナ/OSS依存関係が対象外。
- 例外が永久化する。
- 修正後の検証がない。

### Anti-patterns
- 「Critical/Highだけ修正」で十分とする。
- Scanner severityを業務リスクと同一視する。
- 同じ脆弱性を資産数分だけ発券し、サービス単位の意思決定を失う。
- 補償統制を証拠なしに記載する。

### Maturity Model
Level 0: 年次/不定期スキャン。  
Level 1: CVSS順の手動チケット。  
Level 2: asset owner/SLA/再スキャンがある。  
Level 3: KEV/EPSS/SSVC/asset criticalityで優先順位付け。  
Level 4: 外部露出・SBOM・cloud・endpoint・SIEM連携。  
Level 5: 攻撃観測・事業リスク・自動修復・例外統制が統合。

### Clone Implementation Guide
30日で資産台帳と所有者を修正し、KEV/EPSS/CVSSを取り込む。60日でrisk queueとSLAを再設計する。90日でSSVC decision log、exception register、verification evidenceを運用する。

### Confidence & Unknowns
A: KEV/CVSS/EPSS/SSVC/BOD 23-01。  
B: 組織別SLAとrisk threshold。  
Unknowns: OT/医療/工場系の停止リスク、サプライヤーSLA、クラウド責任分界。

---

## Layer 23.03: パッチ管理

### Definition
アプリケーション、OS、ファームウェア、クラウドサービス、コンテナ、ネットワーク機器、OT/IoTを含むパッチの識別、取得、テスト、展開、検証、ロールバック、例外を管理するレイヤー。

### Frontier Exemplars
NIST SP 800-40 Rev.4は、エンタープライズパッチ管理を識別・優先順位付け・取得・インストール・検証のプロセスとして扱う。CISA KEV/BOD 22-01は悪用確認済み脆弱性への期限付き対応を強制するモデルを示す。

### Evidence Map
Source refs: S08, S09, S10, S15, S41.  
Confidence: A for enterprise patch process; B for exact deployment rings.

### Core Philosophy
パッチ管理はIT保守ではなく、脆弱性リスクを実際に下げる変更管理である。最良の組織は、標準パッチと緊急パッチを分け、テスト、canary/ring deployment、ロールバック、証跡、例外を一体運用する。

### Decision Model
- Inputs: vulnerability queue, vendor advisory, asset criticality, exploit status, dependency risk, maintenance windows, change freeze, test results, rollback feasibility.
- Criteria: exploited status, exposure, blast radius, operational safety, patch reliability, business continuity, compliance deadline.
- Priorities: exploited/KEV and internet-facing > identity/security tools > privileged infrastructure > data stores > general endpoints.
- Prohibitions: untested broad deployment to critical systems, no rollback plan, unsupported assets without risk treatment.
- Exceptions: emergency mitigation instead of patch, vendor patch not available, OT safety window, business outage approval.
- Owners: Patch Manager, IT Ops, Service Owner, Change Advisory, Security.
- Cadence: monthly standard cycle; weekly high-risk review; emergency out-of-band process; quarterly unsupported asset review.

### Operating Model
1. パッチ対象を資産台帳と脆弱性キューに紐づける。  
2. 標準、緊急、例外、廃止の4分類に分ける。  
3. canary → pilot → broad deployment → critical systems のringを設計する。  
4. 失敗時はrollback、network isolation、virtual patching、WAF/IDS rule、credential resetを候補化する。  
5. 適用後はscanner/agent/config/versionで検証する。

### Technical / Business Specification
- Patch ticket requires: affected assets, patch ID, CVE/KEV link, risk tier, test evidence, deployment ring, maintenance window, rollback plan, verification evidence.
- Emergency patch board must include Security + Service Owner + IT Ops + Business approver.
- Legacy unsupported assets require isolation, compensating detection, migration plan, and named risk owner.

### Metrics
Patch compliance by risk tier, KEV deadline adherence, emergency patch MTTR, failed patch rate, rollback rate, unpatched critical asset count, unsupported/EOL count, verification lag, maintenance window breach count.

### Failure Modes
- 脆弱性管理とパッチ管理が別キューで同期しない。
- テスト過剰で悪用中脆弱性の対応が遅れる。
- パッチ成功が「配布成功」で終わり、実際のバージョン検証がない。
- 例外がrisk ownerなしに残る。

### Anti-patterns
- 月次パッチだけでKEV/zero-dayを処理する。
- change freezeを無期限の免罪符にする。
- 重要システムほどパッチされない構造を放置する。

### Maturity Model
Level 0: 手動・随時。  
Level 1: 月次パッチカレンダー。  
Level 2: 重要度SLAと検証。  
Level 3: KEV/EPSS/asset riskで緊急プロセス分離。  
Level 4: 自動配布、ring、rollback、dashboard。  
Level 5: 攻撃観測と変更影響を自動最適化。

### Clone Implementation Guide
30日で標準パッチ/緊急パッチ/例外の定義を作る。60日でdeployment ringとverification evidenceを標準化する。90日でKEV-driven emergency patch flowとEOL資産廃止計画を運用する。

### Confidence & Unknowns
A: NIST SP 800-40 Rev.4、CISA KEV。  
B: ring数やSLAは業務依存。  
Unknowns: vendor patch品質、OT/レガシー停止許容度。

---

## Layer 23.04: 脅威検知 / Detection Engineering

### Definition
攻撃者の戦術・技術・行動を、観測可能なデータソースと検知ロジックへ変換し、テスト・チューニング・運用・廃止を管理するレイヤー。

### Frontier Exemplars
MITRE ATT&CKは実観測に基づく攻撃戦術・技術の知識ベース、D3FENDは防御 countermeasure 語彙、Sigmaはログ検知ルールのベンダ非依存フォーマット、OCSFはセキュリティイベントの共通スキーマを提供する。

### Evidence Map
Source refs: S04, S05, S06, S07, S18, S20, S24.  
Confidence: A for frameworks and schemas; B for specific detection efficacy without local validation.

### Core Philosophy
検知は「ルールを増やす」活動ではなく、攻撃仮説をデータで検証するエンジニアリングである。先端組織は、検知ロジックをコードとして管理し、ATT&CK coverage、data source coverage、test pass、false positive cost、incident yieldで評価する。

### Decision Model
- Inputs: threat model, ATT&CK techniques, threat intel, incident history, available telemetry, OCSF/log schema, existing detections, purple team results.
- Criteria: business risk, attacker cost, data reliability, alert precision, response actionability, evasion resistance, maintainability.
- Priorities: credential theft, privilege escalation, persistence, lateral movement, defense evasion, exfiltration, cloud control plane abuse.
- Prohibitions: untested detections, IOC-only dependence, no owner, no data source requirement, alert without response path.
- Exceptions: privacy-limited telemetry, encrypted traffic visibility limits, noisy data sources.
- Owners: Detection Engineering Lead, SOC, Threat Intel, Data Platform, Platform/Cloud/Endpoint owners.
- Cadence: weekly detection release, monthly coverage review, post-incident detection gap review, quarterly purple-team validation.

### Operating Model
1. Top threatsをATT&CK techniquesへマップする。  
2. 各techniqueに必要なdata sourceとlog fieldsを定義する。  
3. Sigma/SQL/KQL等のrule repoに、owner、test、version、expiryを付ける。  
4. 検知をsimulation/purple team/incident replayで検証する。  
5. false positive tuningとsilent failure detectionを行う。  
6. 使われない/無効な検知を廃止する。

### Technical / Business Specification
- Detection record: threat hypothesis, ATT&CK ID, data source, normalized fields, query, severity logic, suppression logic, test case, response playbook, owner, review date.
- Coverage matrix must show technique × data source × detection × test status.
- Detections should be portable where feasible: Sigma for logs, OCSF for schema normalization, SIEM-specific query generated downstream.

### Metrics
ATT&CK technique coverage, high-risk data source coverage, detection test pass rate, detection latency, alert precision, false positive hours/month, detection-to-response linkage rate, stale rule count, post-incident detection gap count.

### Failure Modes
- IOC過依存で攻撃者が小変更すれば無力化。
- ログが欠落しているのにcoverageありと誤認。
- 検知は出るが対応runbookがない。
- 検知ルールがチューニングされずSOCを疲弊させる。

### Anti-patterns
- ATT&CK coverageを「タグ付け数」として扱う。
- vendor default detectionsを自社の重要資産文脈へ調整しない。
- false positiveを現場努力で吸収し続ける。

### Maturity Model
Level 0: vendor default alertのみ。  
Level 1: IOC/ruleを手動追加。  
Level 2: ATT&CK mappingとowner管理。  
Level 3: detection-as-code、test、tuning workflow。  
Level 4: OCSF/Sigma等で移植性と自動検証。  
Level 5: threat intel、purple team、incident replayが継続的に検知を進化させる。

### Clone Implementation Guide
30日でtop 10 ATT&CK techniquesと必要ログを定義する。60日でrule repoとtest fixtureを作る。90日でpost-incident gap reviewとmonthly detection release processを回す。

### Confidence & Unknowns
A: ATT&CK/D3FEND/Sigma/OCSF。  
B: ローカル環境における検知精度。  
Unknowns: 実ログ品質、プライバシー制約、ツールquery互換性。

---

## Layer 23.05: インシデント対応

### Definition
サイバーインシデントを検知、分類、封じ込め、根絶、復旧、通知、学習へ進める意思決定レイヤー。技術対応だけでなく、事業継続、法務、規制報告、顧客/社内コミュニケーションを含む。

### Frontier Exemplars
NIST SP 800-61 Rev.3はインシデント対応をCSF 2.0に沿ったリスク管理活動として位置づける。CISA playbooksは標準化されたincident/vulnerability response手順を示す。SEC cyber disclosure ruleやENISA/NIS2は、重大インシデントの外部報告・開示判断を組み込む必要性を示す。

### Evidence Map
Source refs: S14, S15, S16, S17, S18, S19.  
Confidence: A for IR lifecycle and regulatory reporting existence; B for jurisdiction-specific obligations outside US/EU.

### Core Philosophy
IRの目的は「火消し」ではなく、被害限定、証拠保全、業務復旧、規制/顧客責任、再発防止を同時に最適化することである。先端組織は、初動判断を属人化せず、重大度、権限、通信、証拠、外部連携を事前に設計する。

### Decision Model
- Inputs: alert/evidence, affected assets, business service, data type, user impact, attacker activity, containment options, legal/regulatory triggers, communications risk.
- Criteria: safety, business impact, active threat, data exposure, legal obligation, containment feasibility, recovery confidence.
- Priorities: human safety/critical operations > active containment > evidence preservation > credential/session invalidation > recovery > disclosure/communication.
- Prohibitions: uncoordinated public statements, evidence destruction, premature root cause claims, unapproved ransom/payment decisions, closure without lessons learned.
- Exceptions: law enforcement sensitivity, national security delay, safety-critical OT constraints.
- Owners: Incident Commander, SOC Lead, Forensics, IT/Cloud/Endpoint owner, Legal, Privacy, PR, Executive sponsor.
- Cadence: incident bridge as needed; status updates by severity; post-incident review within defined window; tabletop quarterly.

### Operating Model
1. Event → Alert → Incident の分類基準を定義する。  
2. severityを技術重大度 + business impact + data impact + active threatで決める。  
3. Incident Commanderに意思決定権限を付与する。  
4. containment actionsを事前承認レベル別に分ける。  
5. evidence collection、chain of custody、timeline、communications logを標準化する。  
6. post-incident reviewでcontrol/detection/process backlogへ戻す。

### Technical / Business Specification
- IR plan includes: roles, contact tree, severity matrix, containment authority, forensic data checklist, legal/regulatory notification decision tree, customer communications templates, recovery validation criteria.
- Playbooks: ransomware, credential compromise, cloud account takeover, data exfiltration, malware outbreak, DDoS, insider data movement, third-party incident.
- Required artifacts: incident timeline, evidence inventory, decisions log, containment record, recovery proof, PIR actions.

### Metrics
MTTD, MTTC, MTTR, time to incident commander assignment, time to containment decision, evidence completeness, notification SLA adherence, recovery validation pass, recurrence rate, PIR action closure.

### Failure Modes
- 重大度判断が技術チームだけで行われ、法務/事業報告が遅れる。
- 封じ込めを急ぎすぎて証拠を失う。
- 役割不明で複数チームが矛盾する操作をする。
- 復旧完了後に根本原因・再発防止が放置される。

### Anti-patterns
- IR planが監査用文書で、演習されない。
- すべてのインシデントをSOC managerが抱える。
- 通知義務をincident後半で初めて確認する。
- バックアップ復旧を検証せずにransomware readinessを主張する。

### Maturity Model
Level 0: 事案ごとに場当たり対応。  
Level 1: 連絡網と基本手順。  
Level 2: severity/runbook/tabletopあり。  
Level 3: 法務・広報・事業・技術の統合IR。  
Level 4: SOAR/evidence automation、forensics readiness、regulatory decision tree。  
Level 5: incident learningが検知・脆弱性・設計・経営リスクへ自動接続。

### Clone Implementation Guide
30日でseverity matrix、IC権限、contact tree、top 5 playbooksを作る。60日でtabletopとforensic evidence checklistを実施する。90日でregulatory reporting decision treeとPIR backlog governanceを入れる。

### Confidence & Unknowns
A: NIST SP 800-61 Rev.3、CISA playbooks、SEC/ENISA reporting references。  
B: 具体的通知期限と対象は法域・業種依存。  
Unknowns: サイバー保険条件、契約上の通知義務、法執行連携要件。

---

## Layer 23.06: SIEM / ログ管理

### Definition
ログとセキュリティイベントを収集、正規化、保管、相関、検索、監査、アラート化し、検知・調査・法的証拠・統制検証に使える状態にするレイヤー。

### Frontier Exemplars
NIST SP 800-92はログ管理の実務ガイド、OMB M-21-31は政府機関向けのイベントログ成熟度モデル、OCSFはベンダ横断のセキュリティイベントスキーマ、CISA Logging Made Easyは小中規模向けの無料・OSSログ集中/検知実装を示す。

### Evidence Map
Source refs: S18, S19, S06, S07, S20, S24.  
Confidence: A for log management principles; B for exact retention periods outside regulated context.

### Core Philosophy
SIEMの価値はログ量ではなく、**調査に必要な証拠を、必要な粒度、期間、権限、形式で取り出せること**である。先端運用は、ログをコストセンターではなく、検知・IR・統制監査・脅威ハンティングの共通データ面として設計する。

### Decision Model
- Inputs: critical assets, attack techniques, regulatory requirements, log sources, event schemas, retention needs, privacy constraints, SIEM cost model.
- Criteria: detection value, investigation value, retention obligation, integrity, timeliness, normalization feasibility, cost per GB/event.
- Priorities: identity logs, endpoint telemetry, cloud control plane, network flow/DNS/proxy, privileged activity, data access, application audit events.
- Prohibitions: collecting logs with no owner/use case, plaintext secrets in logs, unaudited admin access, unverifiable retention.
- Exceptions: privacy-restricted events, high-volume packet data, ephemeral workloads.
- Owners: SIEM/Data Engineer, SOC, Compliance, Platform owners, Privacy.
- Cadence: daily health monitoring, weekly parser/ingestion review, monthly log source coverage review, annual retention policy review.

### Operating Model
1. Log Source Matrixを作成し、source → fields → schema → owner → retention → use casesを紐づける。  
2. OCSF等の共通スキーマへ正規化する。  
3. 検知ルール、調査query、compliance use caseをsourceごとに定義する。  
4. retentionをhot/warm/cold/archiveへ分ける。  
5. ログ欠落、時刻同期、parser failure、ingestion delayを監視する。  
6. privacy/security access controlを適用する。

### Technical / Business Specification
- Required log metadata: source, asset/user ID, timestamp quality, normalized event type, retention class, sensitivity, parser version, owner.
- SIEM must support: role-based access, immutable/auditable storage where required, case links, rule versioning, enrichment, suppression, health monitoring.
- Cost controls: sample only low-value telemetry; never sample security-critical logs without explicit decision.

### Metrics
Log source coverage, critical source freshness, ingestion latency, parser error rate, searchable retention compliance, storage cost per useful detection, query success time, log access audit exceptions, missing log incidents.

### Failure Modes
- ログは大量にあるが、正規化されず調査できない。
- 重要ログの保持期間が短く、侵害範囲調査ができない。
- SIEM admin権限が過大で、ログ改ざんリスクがある。
- クラウド/SaaS/IDログが欠ける。

### Anti-patterns
- 「全部SIEMへ送る」を戦略とする。
- ログ保持をコストだけで決める。
- parser failureを監視しない。
- 検知ルールとログソースの依存関係を記録しない。

### Maturity Model
Level 0: 分散ログ。  
Level 1: 主要ログを手動検索。  
Level 2: SIEMに主要ソース集約、基本相関。  
Level 3: schema, retention, owner, use caseが管理される。  
Level 4: health monitoring, detection-as-code, OCSF/Sigma連携。  
Level 5: ログ価値・コスト・リスク・検知効果が継続最適化。

### Clone Implementation Guide
30日でlog source matrixとtop 10 critical logsを定義する。60日でretention classesとparser health monitoringを入れる。90日でOCSF/Sigma対応、SIEM rule repo、cost/risk dashboardを作る。

### Confidence & Unknowns
A: NIST SP 800-92、OMB M-21-31、OCSF、CISA LME。  
B: retention期間とstorage architecture。  
Unknowns: データ主権、プライバシー、既存SIEM費用制約。

---

## Layer 23.07: IDS/IPS

### Definition
ネットワーク、無線、ホスト、ネットワーク振る舞い、NSMデータを使って侵入・攻撃通信を検知し、必要な場合に遮断するレイヤー。

### Frontier Exemplars
NIST SP 800-94はIDPS設計・導入・設定・監視・維持のガイドを提供する。SuricataとSnortはIDS/IPS実装、Zeekは高忠実度ネットワークログとSIEM連携を提供するNSM実装である。

### Evidence Map
Source refs: S21, S22, S23, S24, S38, S40.  
Confidence: A for IDPS classes and deployment considerations; B for signature efficacy.

### Core Philosophy
IDS/IPSは境界だけに置くものではない。重要経路、セグメント境界、クラウド/データセンター/OT接続、egress、identity-sensitive flowsの観測点を設計し、検知と遮断のリスクを分けて運用する。

### Decision Model
- Inputs: network topology, critical flows, threat model, encryption visibility, sensor placement options, rulesets, false positive history, business impact of blocking.
- Criteria: visibility, block safety, latency, packet loss, signature relevance, evasion resistance, investigation value.
- Priorities: north-south ingress/egress, critical east-west segments, privileged admin paths, data exfil paths, OT/legacy zones.
- Prohibitions: inline blocking without test/tuning, default ruleset overload, unmanaged bypass, packet capture of sensitive data without policy.
- Exceptions: encrypted traffic, high-throughput links, safety-critical networks, privacy-restricted payloads.
- Owners: Network Security, SOC, NetOps, Privacy, Service owners.
- Cadence: daily alert review, weekly ruleset update/tuning, monthly sensor coverage review, quarterly bypass/exception audit.

### Operating Model
1. ネットワーク経路と重要セグメントを可視化する。  
2. sensor placementを検知専用/inline遮断/NSMログに分ける。  
3. ルールセットを脅威・環境・アセットに合わせて最小化/調整する。  
4. 遮断ルールはmonitor → alert → blockの段階を踏む。  
5. IDS/IPS eventsをSIEM/IR playbookへ接続する。  
6. bypass、packet loss、TLS blind spotsを定期監査する。

### Technical / Business Specification
- Sensor inventory: location, traffic scope, mode, throughput, packet loss, ruleset version, logging destination, owner.
- Rule record: signature ID, threat/ATT&CK mapping, action, mode, test status, false positive notes, expiry/review date.
- Inline IPS must have emergency bypass and rollback process.

### Metrics
Sensor coverage, alert precision, packet loss, rule freshness, blocked malicious connections, false block incidents, encrypted/uninspected flow ratio, egress anomaly detection, bypass age.

### Failure Modes
- センサーがあるが重要east-west通信を見ていない。
- ルール数が多すぎてSOCが処理できない。
- Inline IPSが業務停止を引き起こす。
- TLS/QUIC/クラウド通信で可視性が低下する。

### Anti-patterns
- IDSを設置して「監視済み」とする。
- すべてのシグネチャを有効にする。
- blockを有効化してもrollback/bypassを設計しない。
- Zeek/NSMログを検知・調査に使わない。

### Maturity Model
Level 0: IDSなし。  
Level 1: 境界IDS。  
Level 2: 主要セグメントとSIEM連携。  
Level 3: ruleset tuning、coverage、alert workflowが標準化。  
Level 4: Suricata/Snort/Zeek等の組合せでNSM/IPS/検知を最適化。  
Level 5: 暗号化/クラウド/OTを含むリスクベースの可視性・防御制御。

### Clone Implementation Guide
30日でsensor mapとcritical flowsを作る。60日でruleset tuningとSIEM連携を標準化する。90日でinline candidate rulesをmonitor modeで検証し、bypass/rollback手順を整備する。

### Confidence & Unknowns
A: NIST SP 800-94、Suricata/Snort/Zeek公式資料。  
B: 具体的な遮断効果。  
Unknowns: 暗号化可視性、パケット取得の法務/プライバシー制約。

---

## Layer 23.08: EDR

### Definition
エンドポイントのプロセス、ファイル、ネットワーク、認証、メモリ、レジストリ、スクリプト等のテレメトリを収集・分析し、検知、ハンティング、隔離、封じ込め、復旧を行うレイヤー。

### Frontier Exemplars
OMB M-22-01は連邦機関のEDR導入を促進し、EDRを能動的検知・可視化・対応強化の手段として扱う。EO 14144はEDRをリアルタイム継続監視、endpoint data collection、rules-based automated response、analysisを組み合わせるツール/能力として定義する。CISA CDMはEDRを継続診断とダッシュボードに接続する運用面を示す。

### Evidence Map
Source refs: S25, S03, S26, S30, S04.  
Confidence: A for EDR definition/role; B for product-specific response quality.

### Core Philosophy
EDRはアンチウイルスの置換ではない。端末をセンサー兼レスポンス実行点として扱い、攻撃面縮小、ハンティング、封じ込め、証拠収集を同一面で実行する。

### Decision Model
- Inputs: endpoint inventory, user/device criticality, process telemetry, identity context, malware detections, ATT&CK mapping, ASR policy, business criticality.
- Criteria: agent coverage, telemetry fidelity, response action safety, isolation impact, detection confidence, privacy constraints.
- Priorities: privileged endpoints, servers, identity infrastructure, developer/admin machines, high-value data access endpoints, internet-exposed workloads.
- Prohibitions: unmanaged endpoints, disabled/tampered agents, global auto-remediation without test, exclusions without expiry.
- Exceptions: performance-sensitive systems, OT/medical devices, privacy-restricted telemetry.
- Owners: Endpoint Security, SOC, IT Ops, Device Owner, Privacy.
- Cadence: daily agent health, weekly detection review, monthly policy/exclusion review, quarterly tamper and coverage audit.

### Operating Model
1. Endpoint inventoryとEDR agent coverageを100%近くへ持っていく。  
2. High-value endpointsを別policy tierに分ける。  
3. Isolation、kill process、quarantine、file collection、live responseの承認基準を作る。  
4. ASR/app control/malware preventionとEDR detectionを連携する。  
5. Advanced hunting queriesをATT&CKとincident historyに基づき管理する。  
6. Agent health/tamper/exclusion driftを監視する。

### Technical / Business Specification
- EDR policy fields: device group, telemetry level, prevention mode, detection mode, auto-response actions, exclusions, retention, privacy category.
- Response playbook must specify: isolate device conditions, user notification, business owner approval if server, evidence collection, release criteria.
- Exceptions require technical justification, expiry, compensating controls.

### Metrics
Agent coverage, telemetry freshness, tamper events, isolation time, auto-response success, high-risk device unmanaged count, exclusion age, mean time to collect evidence, endpoint detection true positive rate.

### Failure Modes
- agent未導入/壊れた端末が重要資産に残る。
- 除外設定が広すぎる。
- SOCがEDR action権限を持たず封じ込めが遅い。
- Privacy/legalへの配慮が不足しログ利用が止まる。

### Anti-patterns
- EDR導入率だけを成功指標にする。
- 自動隔離を全端末に一律適用する。
- 除外をパフォーマンス問題の恒久回避策にする。

### Maturity Model
Level 0: AVのみ。  
Level 1: EDR導入、一部端末監視。  
Level 2: agent healthとbasic response。  
Level 3: high-value tiers、hunting、IR連携。  
Level 4: ASR/app control/SIEM/SOAR連携、自動封じ込め。  
Level 5: 行動分析、risk-adaptive response、ZT device signal連携。

### Clone Implementation Guide
30日でagent coverageとhigh-value endpoint listを作る。60日でisolation/evidence playbooksとexception registerを作る。90日でhunting query libraryとASR/EDR/SIEM連携を運用する。

### Confidence & Unknowns
A: OMB/EO/CISA CDM定義。  
B: Microsoft等の実装文書は補助的。  
Unknowns: 既存EDR製品のログ保持、OS対応、法域別プライバシー制約。

---

## Layer 23.09: DLP / Data Loss Prevention

### Definition
機密データが、メール、端末、クラウド、SaaS、ストレージ、生成AI、ネットワーク、外部共有、印刷、リムーバブルメディア等を通じて不適切に移動・公開・利用されることを検知、警告、ブロック、調査、教育するレイヤー。

### Frontier Exemplars
Microsoft Purview DLPは、機密情報を保護するポリシー、アラート、調査、チューニングのライフサイクルを公開している。NIST SP 800-122はPIIの識別と適切な保護レベル、CIS Control 3はデータの識別・分類・取扱・保持・廃棄の管理策を示す。

### Evidence Map
Source refs: S31, S32, S49, S33, S34, S50.  
Confidence: A/B; DLPそのものはベンダ実装依存が強いため、原則はA、実装詳細はB。

### Core Philosophy
DLPは「漏えいを全部止める」ものではない。分類された重要データについて、通常業務を過度に阻害せず、危険な行動を検知・警告・ブロックし、利用者教育とポリシー改善へ戻す統制である。

### Decision Model
- Inputs: data classification, sensitive information types, user role, device state, location, activity type, destination, sharing context, business justification, incident history.
- Criteria: data sensitivity, external exposure, user intent signal, business need, regulatory impact, false positive cost, enforceability.
- Priorities: regulated PII/CUI/secrets > credentials/API keys > financial/customer data > confidential documents > broad sharing risks.
- Prohibitions: blocking without appeal path, scanning without privacy/legal basis, unmanaged shadow IT data flows, indefinite exception.
- Exceptions: approved partner sharing, legal discovery, incident response evidence handling, executive/legal override.
- Owners: Data Protection Officer, Privacy, Security, Compliance, Data Owner, IT/SaaS Admin.
- Cadence: weekly alert triage, monthly policy tuning, quarterly classification coverage review.

### Operating Model
1. Data classificationとsensitive information typesを定義する。  
2. 対象場所をendpoint/email/SaaS/cloud storage/AI/chat/data lakeに拡張する。  
3. Policy actionをmonitor → notify → user justification → block → quarantineに段階化する。  
4. User coachingとbusiness exception workflowを組み込む。  
5. DLP alertsをSOC/insider risk/privacy incident processへ接続する。  
6. False positivesを定期チューニングする。

### Technical / Business Specification
- DLP policy fields: data type, location, activity, actor, condition, exception, action, severity, notification, evidence, retention.
- DLP must integrate with classification labels, identity, device compliance, eDiscovery/legal hold, IR, and privacy incident response.
- Alerts must distinguish: accidental sharing, policy misuse, credential leakage, bulk exfiltration, insider risk, compromised account.

### Metrics
Classified data coverage, DLP policy coverage by location, alert precision, blocked high-risk actions, user justification rates, exception age, data exfil incidents, time to investigate DLP alert, policy tuning backlog.

### Failure Modes
- 分類されていないデータはDLP対象外になる。
- 誤検知が多く利用者が回避策を使う。
- 監視のプライバシー説明が不足し、運用が止まる。
- SaaS/生成AI/外部共有のデータフローが未管理。

### Anti-patterns
- すべての外部送信をブロックする。
- DLPを導入してデータ分類を後回しにする。
- alert調査・user education・policy tuningを設計しない。

### Maturity Model
Level 0: DLPなし、手動監査。  
Level 1: メール/endpointの基本検知。  
Level 2: data classificationとpolicy exceptions。  
Level 3: SaaS/cloud/endpoint/email統合、調査workflow。  
Level 4: user coaching、risk-adaptive action、ZT/data signals連携。  
Level 5: 業務文脈・データ分類・行動分析に基づく自律チューニング。

### Clone Implementation Guide
30日で保護対象データとtop locationsを決める。60日でmonitor-only policiesとalert triageを開始する。90日で高リスク行動をuser notification/blockへ段階移行し、例外とチューニングを制度化する。

### Confidence & Unknowns
A: NIST PII/Data protection/CIS Control 3。  
B: Microsoft Purview等の実装からの抽象化。  
Unknowns: 監視の法的根拠、BYOD、生成AIデータ経路、地域別privacy law。

---

## Layer 23.10: Zero Trust

### Definition
アクセス要求を、ネットワーク境界の内外ではなく、ユーザー、デバイス、アプリケーション、データ、ネットワーク、可視性、リスク文脈に基づき継続的に評価し、最小権限・セグメンテーション・継続認可を実現するレイヤー。

### Frontier Exemplars
NIST SP 800-207は、ゼロトラストを静的なネットワーク境界からユーザー・資産・リソース中心へ移すパラダイムとして定義する。CISA Zero Trust Maturity Model 2.0はidentity、devices、networks、applications/workloads、dataを柱に、visibility/analytics、automation/orchestration、governanceを横断能力として扱う。DoD Zero Trust Strategyは大規模組織のロードマップ例である。

### Evidence Map
Source refs: S35, S36, S37, S01, S41, S50.  
Confidence: A for principles and pillars; B for implementation sequencing.

### Core Philosophy
Zero Trustは製品カテゴリではない。すべてのアクセス要求を「明示的に検証し、最小権限で許可し、侵害前提で監視する」ためのポリシーエンジンと運用モデルである。

### Decision Model
- Inputs: identity assurance, device compliance, resource sensitivity, data classification, network context, behavior risk, session risk, threat intel, business role.
- Criteria: least privilege, continuous verification, explicit authorization, segmentation, observability, user friction, operational resilience.
- Priorities: phishing-resistant identity > device posture > privileged access > critical applications > data-level controls > microsegmentation.
- Prohibitions: implicit trust by network location, standing broad privilege, unmanaged devices to sensitive apps, opaque policy exceptions.
- Exceptions: break-glass access, emergency operations, legacy protocol constraints, safety-critical systems.
- Owners: CISO, IAM, Network, Endpoint, App, Data, Cloud, Risk.
- Cadence: quarterly maturity assessment; monthly high-risk policy review; continuous policy telemetry review.

### Operating Model
1. Protect surfaceを定義する: critical apps/data/users/workloads。  
2. Identity, device, network, app, data signalsを収集する。  
3. Policy Decision Point/Policy Enforcement Pointを定義する。  
4. Least privilegeとsegmentationを段階導入する。  
5. Legacy exceptionsを期限付きで管理する。  
6. Access decision telemetryをSIEM/SOCへ送る。

### Technical / Business Specification
- Policy model: subject, device, resource, action, data sensitivity, context, risk score, enforcement action, session controls, logging.
- Required capabilities: MFA/phishing-resistant auth, device compliance, conditional access, microsegmentation, app-level authorization, data labels, privileged access management, continuous logging.
- Break-glass accounts must be monitored, time-bound, separately approved, and tested.

### Metrics
Phishing-resistant MFA coverage, managed device coverage, conditional access policy coverage, privileged standing access reduction, microsegmentation coverage, policy decision latency, blocked risky sessions, exception age, ZTMM maturity by pillar.

### Failure Modes
- Zero TrustをVPN置換だけで捉える。
- identityだけ強化してdata/app/networkが未統合。
- Legacy exceptionが増殖する。
- ユーザー摩擦が過大で回避策が生まれる。

### Anti-patterns
- 「社内ネットワークだから信頼」を残す。
- 常時admin権限を放置する。
- policyが複雑すぎて誰も説明できない。
- 可視性・監査なしにアクセス制御だけ導入する。

### Maturity Model
Level 0: 境界/VPN中心。  
Level 1: MFAと基本条件付きアクセス。  
Level 2: device complianceと主要appsへのZT適用。  
Level 3: identity/device/app/data/networkのポリシー連携。  
Level 4: microsegmentation、continuous risk、automation。  
Level 5: resource-level policyと自律的risk-adaptive enforcement。

### Clone Implementation Guide
30日でprotect surfaceとcurrent access mapを作る。60日でphishing-resistant MFA、device posture、conditional accessをcritical appsへ適用する。90日でprivileged access、microsegmentation、data labels、ZTMM self-assessmentを統合する。

### Confidence & Unknowns
A: NIST SP 800-207、CISA ZTMM、DoD Strategy。  
B: 移行順序と具体製品設計。  
Unknowns: legacy app compatibility、OT/IoT、user experience constraints。

---

## Layer 23.11: ネットワークセキュリティ

### Definition
ネットワーク機器、ファイアウォール、セグメント、ルーティング、DNS、VPN/ZTNA、管理面、east-west/north-south通信、クラウドネットワークを安全に設計・設定・監視・変更するレイヤー。

### Frontier Exemplars
NIST SP 800-41 Rev.1はファイアウォールポリシーと選定・設定・テスト・導入・管理を示す。NSA Network Infrastructure Security Guideはネットワークデバイス設計・設定のハードニング実務を示す。CIS Control 12はネットワークデバイスを追跡・報告・修正して脆弱なサービスやアクセス点の悪用を防ぐことを要求する。

### Evidence Map
Source refs: S38, S39, S40, S21, S35, S50.  
Confidence: A for firewall/network device governance; B for cloud-specific implementation.

### Core Philosophy
ネットワーク防御は「境界で止める」だけではない。許可された通信だけを明示し、管理面を分離・強化し、セグメント間の動きを検知し、構成逸脱を継続的に修正する制御面である。

### Decision Model
- Inputs: network topology, data flows, asset criticality, trust zones, admin paths, firewall rules, exposed services, device configs, vulnerabilities.
- Criteria: least connectivity, segmentation, manageability, resilience, auditability, latency, change risk.
- Priorities: management plane isolation, internet exposure reduction, privileged admin paths, critical service segmentation, egress control, DNS/proxy visibility.
- Prohibitions: any-any rules, unmanaged public exposure, shared admin credentials, default SNMP/management access, unreviewed firewall exceptions.
- Exceptions: temporary migration windows, emergency connectivity, legacy protocols with compensating controls.
- Owners: Network Security, NetOps, Cloud Networking, SOC, Service Owners.
- Cadence: continuous config monitoring; monthly rule recertification for high-risk rules; quarterly segmentation test.

### Operating Model
1. Network zonesとdata flowsを文書化する。  
2. Firewall policyをdeny-by-default、least connectivityへ近づける。  
3. 管理面をout-of-bandまたは厳格なadmin segmentに分離する。  
4. ルール例外にowner、purpose、expiry、riskを付ける。  
5. IDS/Zeek/flow/DNS/proxy logsをSOCへ接続する。  
6. 構成driftと脆弱なサービスを自動検知する。

### Technical / Business Specification
- Firewall rule record: source/destination/service/action, owner, business justification, expiry, last hit, risk tier, change ID.
- Network device baseline: secure management protocol, MFA/PAM for admin, logging, config backup, firmware patch, NTP, AAA, SNMP hardening, banner/legal controls.
- Cloud network controls: security groups, route tables, VPC/VNet segmentation, private endpoints, egress control, flow logs.

### Metrics
External exposure count, any-any rule count, expired firewall exceptions, rule recertification completion, device config compliance, management plane exposure, segmentation test pass rate, network device patch compliance, egress anomaly detections.

### Failure Modes
- ルールが蓄積し、誰も必要性を説明できない。
- 管理面が業務ネットワークから到達可能。
- cloud security groupが野放し。
- セグメンテーションが図面上だけでテストされない。

### Anti-patterns
- Firewall rule cleanupを年1回の監査作業にする。
- VPN内を全面信頼する。
- Network teamとSOCがログ/検知要件を共有しない。

### Maturity Model
Level 0: ad hocルール。  
Level 1: 基本firewallとネットワーク図。  
Level 2: rule owner/expiry/recertification。  
Level 3: segmentation、management plane hardening、flow/DNS/proxy logging。  
Level 4: config compliance、automated exposure detection、ZT integration。  
Level 5: policy-as-code、adaptive segmentation、continuous validation。

### Clone Implementation Guide
30日でnetwork zone/rule inventoryを作る。60日でhigh-risk rulesとmanagement planeを修正する。90日でrule recertification、flow logs、segmentation test、config drift monitoringを標準運用にする。

### Confidence & Unknowns
A: NIST firewall/NSA/CIS network controls。  
B: クラウド/SDN/ZTNA具体設計。  
Unknowns: レガシー回線、OT接続、M&Aネットワーク。

---

## Layer 23.12: エンドポイントセキュリティ

### Definition
ユーザー端末、サーバー、モバイル、開発者端末、管理端末、仮想デスクトップ、IoT/特殊端末のセキュア構成、実行制御、マルウェア対策、攻撃面縮小、ローカル権限、データ保護を管理するレイヤー。

### Frontier Exemplars
NIST SP 800-83 Rev.1はマルウェア予防・対応、NIST SP 800-167はアプリケーションホワイトリスト、CIS Control 4はセキュア構成、CIS Control 10はマルウェア防御、Microsoft Defender ASRは攻撃面縮小ルールの監査・警告・ブロック運用を示す。

### Evidence Map
Source refs: S26, S27, S28, S29, S30, S25.  
Confidence: A for controls and prevention concepts; B for vendor-specific ASR implementation.

### Core Philosophy
端末防御はEDRだけではない。secure baseline、least privilege、patch、app control、malware defense、ASR、disk encryption、DLP、device complianceを組み合わせて、端末を侵害しづらく、侵害時にも被害が広がりにくい状態にする。

### Decision Model
- Inputs: device inventory, OS/app baseline, user role, local admin status, malware risk, app allowlist, ASR events, EDR health, data access.
- Criteria: attack surface reduction, usability, manageability, compatibility, risk tier, recovery ability.
- Priorities: admin/developer endpoints, privileged access workstations, servers, unmanaged BYOD, endpoints accessing sensitive data.
- Prohibitions: unmanaged local admin, disabled security agent, unsupported OS, broad ASR/DLP exclusions, unsigned/unapproved software.
- Exceptions: developer tools, legacy apps, performance-sensitive workloads, regulated BYOD constraints.
- Owners: Endpoint Engineering, IT Ops, Security, Business Device Owners.
- Cadence: daily agent/baseline health; monthly exception review; quarterly secure baseline refresh.

### Operating Model
1. Device groupsをrisk tier別に分ける。  
2. Secure baselineをOS/app/browser/office/macro/script/local adminで定義する。  
3. App allowlistingを高価値端末から導入する。  
4. ASRをaudit → warn → blockで段階適用する。  
5. Malware/EDR/DLP/disk encryptionのcoverageを統合監視する。  
6. Reimage/recovery手順を準備する。

### Technical / Business Specification
- Endpoint baseline fields: OS version, patch tier, encryption, firewall, EDR, malware protection, app control, ASR mode, local admin, screen lock, browser config.
- Exceptions require user, device, reason, risk, compensating control, expiry.
- Privileged endpoints require stricter baseline and isolated admin workflows.

### Metrics
Secure baseline compliance, local admin exception count, ASR block/audit ratio, malware detections, app control coverage, unsupported OS count, disk encryption coverage, endpoint firewall coverage, device recovery time.

### Failure Modes
- 端末台帳が不完全で未管理端末が存在。
- local adminが広く残る。
- ASR/app controlを急にblockし業務停止。
- 開発者端末が例外だらけになる。

### Anti-patterns
- EDR導入でsecure configurationを省略する。
- すべての端末に同一ポリシーを適用する。
- 例外をアプリ/フォルダ単位で広く許可する。

### Maturity Model
Level 0: AVと手動設定。  
Level 1: MDM/endpoint management導入。  
Level 2: secure baselineとpatch/EDR coverage。  
Level 3: app control、ASR、least privilege、exception governance。  
Level 4: automated remediation、risk-tiered policy、ZT device signal。  
Level 5: behavior-informed adaptive hardeningとself-healing endpoint。

### Clone Implementation Guide
30日でendpoint inventoryとbaseline gapを把握する。60日でlocal admin削減、encryption/EDR/patch coverageを改善する。90日でASR audit、app control pilot、exception governanceを開始する。

### Confidence & Unknowns
A: NIST malware/app whitelisting、CIS controls。  
B: ASR等ベンダ実装の効果。  
Unknowns: 開発者体験、BYOD、特殊端末互換性。

---

## Layer 23.13: アプリケーションセキュリティ

### Definition
アプリケーションの要件、設計、実装、依存関係、CI/CD、テスト、リリース、運用、脆弱性対応、サプライチェーン完全性を管理するレイヤー。

### Frontier Exemplars
NIST SP 800-218 SSDFはセキュアソフトウェア開発の実践群を提供する。OWASP ASVSはWebアプリ技術管理策の検証基準、OWASP Top 10は主要Webアプリリスク、SLSAは成果物とサプライチェーン完全性、OpenSSF ScorecardはOSSプロジェクトのセキュリティリスク自動評価、CISA Secure by Design/Demandは製造者と購買者の責任を再配置する。

### Evidence Map
Source refs: S43, S44, S45, S46, S47, S48, S51.  
Confidence: A for standards and control categories; B for app-specific thresholds.

### Core Philosophy
AppSecは「リリース前診断」ではない。設計時の脅威モデリング、セキュア要件、コード/依存関係/ビルド/デプロイの統制、実行時監視、脆弱性対応をSDLCに組み込む。

### Decision Model
- Inputs: product risk, data sensitivity, architecture, threat model, dependencies, code changes, test results, SBOM, build provenance, runtime exposure.
- Criteria: exploitability, user/data impact, supply chain integrity, release risk, compensating controls, regulatory impact.
- Priorities: auth/access control, secrets, injection, cryptography, insecure design, vulnerable dependencies, CI/CD integrity, API abuse, logging/monitoring.
- Prohibitions: hardcoded secrets, unauthenticated sensitive endpoints, unreviewed critical changes, unsigned/unattested artifacts, ignored critical findings.
- Exceptions: risk acceptance with owner, compensating WAF/feature flag, delayed release with emergency patch plan.
- Owners: Product Security, Engineering, AppSec, Platform, Product Owner, Release Manager.
- Cadence: design review before major change; continuous SAST/SCA/secrets scanning; pre-release risk gate; post-release monitoring.

### Operating Model
1. App risk tierをデータ・外部露出・認可複雑性で決める。  
2. Tier別にASVS/SSDF requirementsを割り当てる。  
3. Threat modelを主要機能/architecture changeで実施する。  
4. CI/CDでSAST/SCA/secrets/IaC/container scanを自動化する。  
5. SLSA/provenance/SBOMを高リスク成果物へ適用する。  
6. Release gateはrisk-basedにし、finding exceptionを期限付き承認にする。

### Technical / Business Specification
- AppSec record: app ID, owner, risk tier, data classification, ASVS level, threat model, security tests, dependency posture, SBOM, release exceptions.
- CI/CD controls: branch protection, code review, signed builds, artifact provenance, secrets scanning, dependency update automation, vulnerability gates.
- Runtime controls: WAF/API gateway rules, authz monitoring, security logging, abuse detection, patch runbook.

### Metrics
Threat model coverage, ASVS control coverage, pre-prod critical findings, escaped vulnerabilities, SCA MTTR, secrets detection rate, SBOM/provenance coverage, secure code review coverage, release exceptions age, dependency freshness.

### Failure Modes
- 診断結果がリリース直前に出て修正不能。
- 認可ロジックが設計レビューなしに肥大化。
- OSS依存関係やCI/CDが攻撃面になる。
- AppSecが中央チームのボトルネックになる。

### Anti-patterns
- OWASP Top 10だけをチェックリスト化する。
- SAST/DAST導入で設計リスクを見ない。
- 高リスクfindingsを恒久例外にする。
- SBOMを作るだけで脆弱性対応に使わない。

### Maturity Model
Level 0: 事後診断のみ。  
Level 1: 基本SAST/SCA/secrets scan。  
Level 2: secure requirementsとrelease gate。  
Level 3: threat modeling、ASVS、risk-tiered controls、developer enablement。  
Level 4: CI/CD provenance、SLSA/SBOM、automated remediation、runtime detection。  
Level 5: secure by design/default、product security metrics、self-service guardrails。

### Clone Implementation Guide
30日でapp inventory/risk tier/ownerを作る。60日でSSDF/ASVS baselineとCI scanningを導入する。90日でthreat modeling、dependency automation、SBOM/provenance pilot、exception governanceを開始する。

### Confidence & Unknowns
A: NIST SSDF、OWASP、SLSA、OpenSSF、CISA Secure by Design。  
B: App-specific testing depth and thresholds。  
Unknowns: 技術スタック、リリース速度、規制要件、ソフトウェア購買契約。

---

## Layer 23.14: データセキュリティ

### Definition
データを発見、分類、所有者設定、アクセス制御、暗号化、鍵管理、保持、バックアップ、廃棄、監査、インシデント対応の対象として管理するレイヤー。

### Frontier Exemplars
CIS Control 3はデータの識別・分類・安全な取扱・保持・廃棄を明示する。NIST SP 800-122はPIIの識別と保護レベル、SP 800-111は保存データ暗号化、SP 800-88は媒体サニタイズ、SP 800-171 Rev.3はCUI保護要件を示す。NIST CSF 2.0のProtect機能にもdata securityが含まれる。

### Evidence Map
Source refs: S49, S32, S33, S34, S42, S01, S31, S50.  
Confidence: A for data lifecycle controls; B for organization-specific classification taxonomy.

### Core Philosophy
データセキュリティは「保存時暗号化」だけではない。どのデータがどこにあり、誰が所有し、誰がなぜアクセスし、どのライフサイクルで保持/削除され、漏えい時に何を通知するかを決める統制である。

### Decision Model
- Inputs: data inventory, classification, owner, location, processing purpose, access path, encryption status, retention requirement, legal hold, regulatory category, sharing relationships.
- Criteria: confidentiality, integrity, availability, legal basis, business value, breach impact, minimization, recoverability.
- Priorities: regulated personal data, credentials/secrets, customer confidential data, CUI, financial data, intellectual property, backups.
- Prohibitions: unlabeled sensitive data, shared accounts, unmanaged public buckets, no retention owner, disposal without evidence.
- Exceptions: legal hold, regulated retention, emergency access, anonymization/pseudonymization constraints.
- Owners: Data Owner, Data Governance, Privacy, Security, Legal, Platform/Data Engineering.
- Cadence: continuous discovery; quarterly access review; annual retention/disposal review; post-incident classification review.

### Operating Model
1. Data inventoryとclassification taxonomyを作る。  
2. Data ownerとstewardを割り当てる。  
3. Access control、encryption、DLP、loggingをclassification別に定義する。  
4. Retention scheduleとdisposal/sanitization evidenceを管理する。  
5. Backup/restoreとransomware recoveryを含む可用性を設計する。  
6. Data incident playbookをIRへ接続する。

### Technical / Business Specification
- Data record: dataset ID, owner, classification, location, systems, data subjects/category, access groups, encryption, key owner, retention, DLP policy, backup, deletion method.
- Encryption policy: data at rest/in transit, key rotation, HSM/KMS ownership, access logs, break-glass access.
- Disposal evidence: method, scope, verifier, date, residual risk, certificate where applicable.

### Metrics
Data inventory coverage, classification coverage, sensitive data in unmanaged locations, encryption coverage, access review completion, overprivileged data access, retention violations, disposal evidence coverage, key rotation compliance, data incident count.

### Failure Modes
- データがどこにあるか分からない。
- 分類はあるがアクセス制御・DLPに接続されない。
- バックアップに機密データが残り続ける。
- 削除要求や保持期限に対応できない。
- 鍵管理がplatform teamに属人化する。

### Anti-patterns
- 機密データ保護をDLPだけに任せる。
- すべてのデータを同じ分類にする。
- 暗号化済みだからアクセス制御レビュー不要とする。
- データ廃棄をストレージ削除と同一視する。

### Maturity Model
Level 0: データ台帳なし。  
Level 1: 主要データの手動分類。  
Level 2: owner/access/encryption/retention文書化。  
Level 3: discovery/classification/DLP/access review連携。  
Level 4: automated data posture management、key governance、disposal evidence。  
Level 5: data-centric zero trust、purpose-based access、continuous compliance。

### Clone Implementation Guide
30日でtop critical datasetsとownersを確定する。60日でclassification、access review、encryption status、retentionを台帳化する。90日でDLP、logging、disposal evidence、data incident playbookを運用する。

### Confidence & Unknowns
A: CIS Control 3、NIST PII/encryption/sanitization/CUI。  
B: 分類taxonomyと閾値。  
Unknowns: 地域別privacy law、契約保持義務、データローカライゼーション。

---

## 6. Cross-Layer Operating Model

### 6.1 Role Model

| Role | Responsibilities |
|---|---|
| CISO / Security Governance | リスク許容度、優先順位、予算、例外承認、経営報告 |
| SOC Manager | 監視、トリアージ、検知運用、SOC品質管理 |
| Detection Engineering | 検知設計、ルール管理、ATT&CK/D3FEND coverage、テスト |
| Vulnerability Manager | 脆弱性キュー、SLA、KEV/EPSS/SSVC、例外管理 |
| Patch / IT Ops | パッチ適用、変更管理、検証、rollback |
| Incident Commander | IR指揮、封じ込め、復旧、意思決定ログ |
| Network Security | セグメンテーション、ファイアウォール、IDS/IPS、管理面防御 |
| Endpoint Security | EDR、ASR、secure baseline、app control、malware defense |
| AppSec / Product Security | SSDF、ASVS、threat modeling、CI/CD、SBOM/SLSA |
| Data Protection / Privacy | データ分類、DLP、PII/CUI、通知義務、保持/廃棄 |
| Legal / Compliance / PR | 報告義務、証拠保全、外部コミュニケーション |

### 6.2 Core Artifacts

| Artifact | Purpose | Minimum Required Fields |
|---|---|---|
| Critical Asset Register | 防御優先順位の基盤 | asset ID, owner, criticality, exposure, data classification, dependencies |
| Telemetry Matrix | ログ/EDR/IDS/DLP/Cloud可視性 | source, fields, owner, retention, use case, health status |
| Risk Queue | VM/Patch/Detection/IRを統合 | issue, assets, exploitability, impact, owner, SLA, evidence |
| Detection Repository | 検知をコード化 | rule, ATT&CK ID, data source, test, owner, severity, version |
| Exception Register | 例外を統制 | scope, reason, owner, approver, expiry, compensating controls |
| Incident Record | IR証跡 | timeline, evidence, decisions, actions, communications, PIR actions |
| Data Inventory | データ防御基盤 | dataset, owner, class, location, access, encryption, retention, DLP policy |
| Maturity Dashboard | 経営・運用指標 | coverage, risk, SLA, exceptions, incidents, improvement backlog |

### 6.3 Review Cadence

| Cadence | Review |
|---|---|
| Daily | SOC queue, critical alerts, EDR/IDS/SIEM health, emergency vulnerabilities |
| Weekly | high-risk vulnerability queue, detection tuning, patch failures, IR action items |
| Monthly | exception review, log source coverage, ATT&CK coverage, firewall/high-risk access recertification |
| Quarterly | tabletop, ZT maturity, segmentation test, data access review, AppSec maturity review |
| Annual | risk appetite, policy refresh, retention schedule, third-party/security program review |

---

## 7. Metrics Library

| Metric | Applies To | Definition |
|---|---|---|
| Asset Coverage | 23.01,23.02,23.03,23.11,23.12 | managed assets / known assets |
| Telemetry Coverage | 23.01,23.04,23.06,23.07,23.08 | critical assets with required logs/EDR/IDS telemetry |
| KEV SLA Compliance | 23.02,23.03 | KEV vulnerabilities remediated by due date / applicable KEV |
| MTTD / MTTC / MTTR | 23.01,23.04,23.05,23.08 | detection, containment, recovery time |
| Detection Precision | 23.01,23.04,23.06,23.07 | true positive alerts / reviewed alerts |
| Rule/Test Coverage | 23.04,23.06,23.07 | detections with tests / detections in production |
| Exception Age | all | open exceptions past review date or expiry |
| Secure Baseline Compliance | 23.11,23.12 | compliant devices/configs / in-scope devices/configs |
| DLP Policy Precision | 23.09 | confirmed risky data events / DLP alerts |
| ZT Policy Coverage | 23.10 | critical resources governed by conditional/contextual access |
| AppSec Gate Pass | 23.13 | releases passing risk-based gates without critical exceptions |
| Data Classification Coverage | 23.09,23.14 | classified datasets / known datasets |
| Encryption Coverage | 23.09,23.14 | protected sensitive data stores / sensitive data stores |
| PIR Action Closure | 23.01,23.05 | post-incident actions closed by due date |

---

## 8. Failure Modes and Anti-pattern Library

| Pattern | Description | Affected Layers | Preventive Control |
|---|---|---|---|
| Tool-first SOC | SIEM/EDR導入を成熟度と誤認 | 23.01,23.06,23.08 | operating model, coverage metrics, runbooks |
| CVSS-only VM | CVSS順に処理し悪用中リスクを逃す | 23.02,23.03 | KEV/EPSS/SSVC/asset criticality |
| Ownerless findings | 修正責任者が不明 | 23.02,23.03,23.13,23.14 | asset/app/data owner registry |
| Infinite exceptions | 期限なし例外が統制を崩す | all | exception register with expiry and compensating controls |
| No verification | パッチ/修正/封じ込めの証拠がない | 23.03,23.05,23.13 | verification evidence and rescan |
| Alert fatigue | ノイズで重大事象を逃す | 23.01,23.04,23.06,23.07,23.08,23.09 | tuning, suppression governance, precision metrics |
| Boundary trust | VPN/社内NWを信頼し横展開を許す | 23.10,23.11 | zero trust, segmentation, continuous verification |
| Data blind spots | データ分類とDLP/アクセス制御が接続されない | 23.09,23.14 | data inventory and label-driven controls |
| AppSec at release only | 設計/依存関係/CI/CDリスクを後追い | 23.13 | SSDF, threat modeling, CI/CD controls |
| Logging without purpose | ログ収集だけで検知・調査に使えない | 23.06 | log source matrix, schema, retention, use cases |

---

## 9. Validation Queries

Use these queries for recurring revalidation and contradiction search.

```text
# Cross-layer standards freshness
site:nist.gov cyber security framework 2.0 update
site:csrc.nist.gov "SP 800-61" "Rev. 3" incident response
site:csrc.nist.gov "SP 800-40" "Rev. 4" patch management
site:cisa.gov "Cybersecurity Performance Goals" "2.0"

# Vulnerability / patch contradiction
site:cisa.gov "Known Exploited Vulnerabilities" "BOD 22-01" "due date"
site:first.org "CVSS v4.0" specification
site:first.org/epss "EPSS" "model"
"SSVC" "vulnerability" "decision tree" site:cisa.gov OR site:sei.cmu.edu

# Detection / SIEM / IDS validation
site:attack.mitre.org "Detection Strategies"
site:d3fend.mitre.org "countermeasure"
site:sigmahq.io "Sigma rules" "SIEM"
site:ocsf.io "security schema"
site:cisa.gov OR site:cisagov.github.io "Logging Made Easy"
site:csrc.nist.gov "SP 800-94" "IDPS"

# EDR / endpoint
site:whitehouse.gov "M-22-01" "Endpoint Detection and Response"
site:presidency.ucsb.edu "endpoint detection and response" "continuous monitoring"
site:csrc.nist.gov "SP 800-167" "Application Whitelisting"
site:cisecurity.org "Control 10" "Malware Defenses"

# Data / DLP / Zero Trust
site:csrc.nist.gov "SP 800-207" "Zero Trust Architecture"
site:cisa.gov "Zero Trust Maturity Model" "Version 2.0"
site:learn.microsoft.com "Purview" "Data Loss Prevention" "alerts"
site:csrc.nist.gov "SP 800-122" "PII"
site:cisecurity.org "Control 3" "Data Protection"

# AppSec
site:csrc.nist.gov "SP 800-218" "SSDF"
site:owasp.org "ASVS"
site:owasp.org "Top 10" "2025"
site:slsa.dev "spec" "v1.2"
site:cisa.gov "Secure by Design" "Secure by Demand"
```

---

## 10. Implementation Roadmap

### Phase 0: Baseline and Ownership（0–30日）
- Layer 23.01: SOC charter、escalation matrix、critical asset listを作る。
- Layer 23.02/23.03: asset owner、KEV/EPSS/CVSS取り込み、patch/VM queueを統合する。
- Layer 23.06/23.08: critical logsとEDR coverageを棚卸しする。
- Layer 23.14: critical datasetsとdata ownersを確定する。

### Phase 1: Risk-prioritized Operations（31–60日）
- SSVC-style decision log、patch rings、exception registerを導入する。
- Top ATT&CK techniquesに基づく検知use casesとlog source matrixを作る。
- IR severity matrix、Incident Commander権限、top incident playbooksを作る。
- ZT protect surface、conditional access、device compliance baselineを決める。

### Phase 2: Evidence and Automation（61–90日）
- Detection-as-code、SIEM parser health、EDR isolation playbook、IDS rule tuningを開始する。
- DLP monitor policies、data classification、access reviewを開始する。
- AppSec CI gates、threat modeling、SBOM/provenance pilotを導入する。
- Monthly risk dashboardを経営・現場双方に出す。

### Phase 3: Continuous Improvement（91日以降）
- Quarterly tabletop、segmentation test、ZT maturity self-assessmentを行う。
- PIR actionsをVM/Patch/Detection/AppSec/Data backlogへ自動接続する。
- Metricsをrisk reductionとbusiness impactへ寄せ、alert volumeやscan countだけの報告を廃止する。

---

## 11. Confidence & Unknowns

### High Confidence（A）
- NIST CSF 2.0、NIST SP 800 series、CISA KEV/BOD/ZTMM/CPG、MITRE ATT&CK/D3FEND、FIRST CVSS/EPSS、CIS Controls、OWASP/SSDF/SLSA等に基づく基本構造。
- 脆弱性管理、パッチ管理、IR、ログ管理、Zero Trust、AppSec、Data Protectionの主要アウトカムと意思決定モデル。

### Medium Confidence（B）
- 14レイヤーを単一企業へ移植する際のSLA、具体ツール、組織分掌、運用頻度、ログ保持期間。
- ベンダ文書から抽象化したDLP/EDR/ASR/SIEM実装パターン。

### Low Confidence / Requires Local Evidence（C/D）
- 業界別の規制期限、契約上の通知義務、法域別データ保護要件。
- OT/IoT/医療/工場/金融勘定系など、可用性・安全性制約が強い環境での標準SLA。
- 実環境での検知精度、誤検知率、パッチ失敗率、ユーザー摩擦。

---

## 12. Minimum Clone Specification

A team cloning the frontier operating model for Layers 23 should implement the following minimum viable security operation stack:

1. Critical asset and data inventory with owners.
2. Vulnerability prioritization using KEV + EPSS + CVSS + SSVC + asset criticality.
3. Patch deployment rings with emergency process, rollback, and verification evidence.
4. SIEM/log matrix with retention, normalization, parser health, and detection use cases.
5. Detection-as-code mapped to ATT&CK and tested before production.
6. IR plan with severity, Incident Commander, legal/regulatory decision tree, and PIR loop.
7. EDR coverage and endpoint secure baseline with exception governance.
8. IDS/IPS/NSM visibility at critical ingress/egress/east-west points.
9. DLP tied to data classification, user coaching, alert triage, and policy tuning.
10. Zero Trust roadmap across identity, device, network, application, data, visibility, automation, governance.
11. Network security controls for management plane, segmentation, firewall policy, and config drift.
12. AppSec SDLC based on SSDF/ASVS, CI/CD scans, dependency management, SBOM/provenance.
13. Data security lifecycle: classification, encryption, access review, retention, disposal evidence.
14. Cross-layer metrics and monthly executive risk dashboard.

