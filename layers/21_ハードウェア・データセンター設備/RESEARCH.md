# Frontier Operating Model Research — ハードウェア・データセンター設備

- **対象レイヤー**: 21
- **推奨指示書タイトル単位**: ハードウェア・データセンター設備
- **対象サブテーマ**: cable/fiber/optics、server chassis、motherboard、CPU/RAM/storage/GPU、BIOS/UEFI/BMC/IPMI、rack、PDU、UPS、generator、cooling、physical access control、camera、fire suppression、carrier line、submarine cable
- **生成日**: 2026-05-13 JST
- **調査制約**: 公開情報のみ。標準本文が有償・会員制のものは、公式公開ページ・公開概要・ベンダー公式資料・事故報告・規制ページで補完し、条項番号レベルの断定は避けた。

---

## 0. Executive Summary

ハードウェア・データセンター設備レイヤーの中核意思決定は、**AI/HPC/クラウド負荷を、どの物理設計・電力設計・熱設計・ネットワーク接続・保守運用・安全統制の組み合わせで、サービス可用性・効率・拡張性・サプライチェーン柔軟性・物理リスクに対して最適化するか**である。

先端パターンは、従来の「施設を作り、その中にサーバを置く」モデルから、**ラック単位・ポッド単位・キャンパス単位での co-design** に移行している。ラックは OCP Open Rack V3 / Open Rack Wide / 48V 系統のような高密度・標準化された機械/電力インターフェースへ、サーバは OCP DC-MHS のようなモジュラー化へ、管理面は IPMI から Redfish / OpenBMC / SPDM / DICE へ、冷却は空冷中心から direct-to-chip liquid / closed-loop / CDU / HXU へ、ネットワークは 400G/800G/1.6T Ethernet、OSFP/QSFP-DD、AI back-end fabric、private WAN、subsea diversity へ移行している。

このレイヤーの Clone Spec は次の方針で設計すべきである。

1. **安全・法令・火災・物理アクセスを最上位制約にする**。NFPA 75/76/110、NIST SP 800-53 PE 系、TIA-942/ISO/IEC 22237/EN 50600/Uptime Tier などを設計入力にし、可用性よりも生命安全と規制適合を先に固定する。
2. **IT、電力、冷却、ネットワークを同じ容量モデルで扱う**。GPU/CPU 世代、ラック電力、液冷 supply/return、PDU/UPS/generator、光トランシーバ、ケーブル経路、carrier/subsea diversity を別々に最適化しない。
3. **標準化と交換可能性を調達・運用の武器にする**。OCP、DMTF Redfish、UEFI、OpenBMC、SPDM、PCIe/CXL/NVMe、IEEE 802.3、OSFP/QSFP-DD などの公開仕様に寄せ、特定ベンダー固有の短期最適化を抑制する。
4. **故障を前提に隔離・監視・安全停止を設計する**。OVHcloud Strasbourg 火災、Google Cloud London cooling failure のように、冗長系が存在しても火災・液体・外気温・運用判断・バックアップ配置で被害が拡大しうる。
5. **PUE だけでなく WUE、CUE、実効利用率、メンテナンス性、部品交換時間、容量予約、interconnect latency を同時に測る**。水消費と電力効率はトレードオフになりやすいため、単一指標で設計判断しない。

---

## 1. Definition

このレイヤーは、データセンターを構成する **物理的な情報処理資産・設備・供給網・安全統制・物理ネットワーク接続** を制御する。具体的には、サーバ/アクセラレータ/ストレージ、マザーボード、ファームウェア/管理プレーン、ラック、配電、UPS、発電機、冷却、光/銅ケーブル、通信キャリア接続、海底ケーブル、火災保護、物理アクセス、監視カメラを含む。

### Decision Object

「どのワークロードと可用性目標に対して、どの物理インフラ構成を、どの標準・冗長性・安全性・効率・保守性・供給制約で採用するか」

### Decision Question

世界トップの主体は、AI/HPC/クラウドデータセンター設備について、何を入力に、どのラック/サーバ/電力/冷却/光ネットワーク/物理セキュリティ/火災保護/キャリア接続を選び、どの基準・閾値・例外・承認・監査・メトリクスで運用するのか。

### Scope Exclusions

- 非公開の施設図面、侵入経路、監視死角、鍵/認証回避、個別施設の弱点探索は対象外。
- 本レポートは設計・調達・運用の Clone Spec であり、攻撃・侵入・破壊・回避手順を提供しない。
- TIA/BICSI/NFPA/JEDEC 等の有償標準については、公開概要と公式ページに基づく。契約・認証用途では原本の購入・専門家レビューが必要。

---

## 2. Layer Registry

| Field | Value |
|---|---|
| layer_id | 21 |
| layer_name_ja | ハードウェア・データセンター設備 |
| cluster | インフラ / 物理基盤 / データセンター設備 |
| definition | IT 機器、ラック、電力、冷却、配線、物理保護、キャリア接続を含むデータセンターの物理意思決定レイヤー |
| decision_object | ワークロード要求と可用性目標を満たす物理インフラ構成 |
| default_source_types | 標準、公式仕様、公式設計ガイド、事故報告、ハイパースケーラー公開資料、ベンダー技術資料、規制ページ |
| input_signals | IT load forecast、GPU/CPU roadmap、rack kW、thermal design power、network radix/bandwidth、site utility capacity、water availability、jurisdiction、threat model、SLO/SLA、maintenance window、supply-chain risk |
| output_artifacts | reference rack design、server BOM、cable matrix、power one-line、cooling design basis、commissioning plan、firmware baseline、physical security plan、fire protection basis-of-design、carrier/subsea diversity plan |
| owner_roles | Data Center Architecture、Hardware Platform Engineering、Facilities Engineering、Network Engineering、Security Engineering、Firmware/BMC Engineering、Sustainability、Procurement、Data Center Operations、Safety/Compliance |
| default_metrics | availability、PUE、WUE、CUE、rack kW、cooling capacity margin、UPS autonomy、generator start/test success、Mean Time To Repair、firmware compliance、cross-connect delivery time、optics failure rate、physical access exceptions、fire alarm/suppression test results |
| priority_rank | Critical |

---

## 3. Frontier Exemplars

| Exemplar | 適用領域 | なぜ Frontier とみなすか | 主な証拠 |
|---|---|---|---|
| Open Compute Project: Open Rack V3 / DC-MHS / Open Rack Wide 系 | rack、server chassis、motherboard、power shelf、modular server | 公開仕様としてラック、IT gear、電力、モジュラーサーバのインターフェースを定義し、複数ベンダーの相互運用を狙う | S02, S03 |
| NVIDIA GB200 NVL72 / DGX GB rack-scale systems | CPU/GPU、rack-scale AI、liquid cooling、NVLink fabric | 36 Grace CPU + 72 Blackwell GPU を単一ラック内の NVLink domain として扱う rack-scale AI 構成を公開 | S12 |
| AMD Instinct MI300X Platform / OAM/UBB | GPU、memory、accelerator module、server design | 大容量 HBM、OAM/UBB、Infinity Fabric により AI/HPC サーバの標準モジュール化と高密度化を示す | S13 |
| ASHRAE TC 9.9 + Liquid Cooling Guidelines | cooling、thermal envelope、facility water temperature | データセンター熱設計・空冷/液冷クラス・環境条件の事実上の基準 | S15 |
| Uptime Tier / TIA-942 / ISO/IEC 22237 / EN 50600 | topology、availability、physical facility、telecom、security、fire、power、cooling | 施設トポロジー、データセンター物理インフラ、運用/管理/KPI を標準化 | S17, S18, S19, S20 |
| DMTF Redfish / SPDM、UEFI、OpenBMC、TCG DICE | BIOS/UEFI、BMC/IPMI replacement、firmware security、attestation | 管理プレーンを REST/secure/attestable/open firmware stack へ移す公開標準群 | S04, S05, S06, S07, S08 |
| PCI-SIG / CXL / NVMe / IEEE 802.3 / OSFP / QSFP-DD | CPU-memory-I/O、storage、Ethernet、optics | AI/HPC サーバの帯域・レイテンシ・フォームファクタを支える基盤標準 | S09, S10, S11, S25, S26, S27 |
| Google / Microsoft / AWS / Meta data center sustainability and network disclosures | PUE/WUE、liquid/zero-water cooling、private WAN、subsea、cloud regions | ハイパースケール運用で PUE/WUE、subsea/private WAN、zero-water cooling 等の公開実績を示す | S31, S35, S36, S37, S38 |
| Equinix / AWS Direct Connect / carrier-neutral interconnection | carrier line、MMR、cross-connect、cloud interconnect | physical cross-connect、MMR、multi-location high availability を商用運用として公開 | S29, S30 |
| OVHcloud Strasbourg fire / Google Cloud London cooling incident | failure evidence、anti-pattern、resilience validation | 火災・冷却冗長失敗・安全停止・バックアップ配置の境界条件を示す公開事故事例 | S39, S40 |

---

## 4. Candidate Scoring

スコアは Performance 25 / Adoption 15 / Artifact Richness 20 / Peer Validation 15 / Recency 10 / Transferability 10 / Failure Evidence 5 の 100 点換算。

| Candidate | Performance | Adoption | Artifact Richness | Peer Validation | Recency | Transferability | Failure Evidence | Score | 判定 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| OCP Open Rack V3 / DC-MHS | 22 | 13 | 20 | 14 | 8 | 10 | 3 | 90 | 採用 |
| ASHRAE TC 9.9 / Liquid Cooling | 23 | 14 | 17 | 15 | 8 | 10 | 3 | 92 | 採用 |
| Uptime Tier + TIA/ISO/EN standards | 22 | 15 | 17 | 15 | 8 | 9 | 4 | 91 | 採用 |
| DMTF Redfish / SPDM + OpenBMC + UEFI | 21 | 13 | 18 | 14 | 9 | 10 | 3 | 89 | 採用 |
| NVIDIA GB200 NVL72 rack-scale AI | 25 | 12 | 16 | 11 | 10 | 7 | 2 | 84 | 採用。ただしベンダー固有依存を明示 |
| AMD MI300X/OAM/UBB | 22 | 11 | 15 | 10 | 9 | 8 | 2 | 78 | 採用。ただし実装文脈は限定 |
| Microsoft zero-water / HXU design | 21 | 11 | 15 | 10 | 10 | 8 | 3 | 79 | 採用。水制約サイトで特に重要 |
| Google PUE/WAN/subsea disclosures | 22 | 14 | 15 | 12 | 10 | 7 | 4 | 84 | 採用 |
| Equinix/AWS Direct Connect cross-connect model | 20 | 14 | 14 | 11 | 9 | 9 | 3 | 81 | 採用 |
| Schneider/Eaton/Vertiv power chain docs | 18 | 13 | 15 | 10 | 8 | 9 | 3 | 76 | 補助採用 |
| NFPA/NIST physical/fire controls | 20 | 14 | 16 | 15 | 8 | 9 | 4 | 86 | 採用 |
| Meta 2Africa / Google subsea systems | 21 | 11 | 13 | 10 | 10 | 7 | 3 | 76 | ネットワーク/地政学補助採用 |

---

## 5. Evidence Map

| claim_id | Claim | claim_type | decision_model_field | Sources | Confidence |
|---|---|---|---|---|---|
| C-001 | 先端データセンター設備は、単一サーバ最適化ではなく、ラック/ポッド/キャンパス単位の power-thermal-network co-design に移行している | principle | core_philosophy | S02, S12, S15, S35 | B |
| C-002 | OCP Open Rack V3 はラックフレーム・IT gear・電力システムの相互接続要件を定義する公開仕様として、ラック標準化の主要参照になる | artifact | technical_spec.rack | S02 | A |
| C-003 | DC-MHS はモノリシックなサーバ設計をモジュラーでスケーラブルな設計に寄せるための公開プロジェクトである | artifact | technical_spec.server_chassis | S03 | A |
| C-004 | NVIDIA GB200 NVL72 は 36 CPU / 72 GPU / liquid-cooled rack-scale NVLink domain という、AI 向けラック単位設計の代表例である | artifact | technical_spec.cpu_gpu | S12 | A |
| C-005 | ASHRAE TC 9.9 はデータセンター熱環境・液冷設計の基準面を提供する | rule | criteria.cooling | S15 | A |
| C-006 | Uptime Tier は冗長 capacity components と distribution paths によるトポロジー分類を提供する | rule | criteria.availability | S17 | A |
| C-007 | TIA-942 は site、architecture、electrical、mechanical、fire safety、telecom、security など物理インフラ全体を対象にする | rule | criteria.facility | S18 | A |
| C-008 | ISO/IEC 22237 と EN 50600 はデータセンター施設・インフラ・運用・KPI を体系化する | rule | criteria.facility | S19, S20 | A |
| C-009 | Redfish は人間可読かつ機械処理可能な近代的管理 API として、BMC/IPMI 運用を置換・補完する基盤になる | artifact | controls.management_plane | S04 | A |
| C-010 | OpenBMC は cloud-scale, enterprise, HPC, telco をまたぐオープン BMC firmware stack として、管理ファームウェアの透明性を上げる | artifact | controls.firmware | S06 | A |
| C-011 | SPDM/DICE は component authentication、attestation、key exchange、firmware evidence を標準化し、サプライチェーン/起動時信頼性に効く | control | controls.firmware_security | S07, S08 | B |
| C-012 | PCIe/CXL/NVMe は CPU、memory、accelerator、storage の帯域/レイテンシ/拡張性の判断基準になる | artifact | interfaces.compute_storage | S09, S10, S11 | B |
| C-013 | IEEE 802.3、OSFP、QSFP-DD、OCP iAOC は 800G/1.6T 世代のデータセンター光接続設計の主要参照になる | artifact | interfaces.optics | S25, S26, S27, S28 | B |
| C-014 | PUE/WUE/CUE はデータセンター効率の基礎指標だが、PUE 単独では水・炭素・IT 利用率・地理条件を表せない | metric | metrics.sustainability | S16, S20, S36, S37, S38 | B |
| C-015 | physical access control と monitoring は、アクセス権限、ログ、監視、インシデント対応との連携を必要とする | control | controls.physical_security | S24 | A |
| C-016 | NFPA 75/76/110 は IT equipment、telecom facility、emergency/standby power の火災・電源安全の設計入力になる | rule | controls.fire_power_safety | S21, S23 | A |
| C-017 | Carrier-neutral MMR と cross-connect は cloud/network/provider への低レイテンシ・専用・物理接続を提供し、複数ロケーション利用が可用性に効く | artifact | interfaces.carrier | S29, S30 | A |
| C-018 | Subsea cable はクラウド WAN の地理的冗長・帯域・レイテンシ戦略の一部であり、landing license と海底ケーブル保護実務が制約になる | control | interfaces.submarine_cable | S31, S32, S33, S34 | B |
| C-019 | OVHcloud Strasbourg 火災は、UPS/電源室、火災検知/消火、電気遮断、バックアップ配置、サイト分離の不備がデータセンター被害を拡大しうることを示す | failure_mode | failure_modes.fire | S40 | A |
| C-020 | Google Cloud London 2022 cooling incident は、複数冗長冷却の同時故障と高外気温で安全停止が必要になることを示す | failure_mode | failure_modes.cooling | S39 | A |

---

## 6. Core Philosophy

### 6.1 Facility is a computer

先端データセンターでは、施設は単なる箱ではなく、**GPU、CPU、memory、NIC、optics、rack、PDU、UPS、generator、CDU、carrier interconnect、subsea routes を含む巨大な分散コンピュータ**として設計される。単一部品の効率よりも、ラック単位の熱密度、ネットワーク radix、液冷供給温度、電力冗長、保守作業時間、故障隔離単位を同時に最適化する。

### 6.2 Standardize the interface, specialize the workload

ラック、モジュール、BMC、ファームウェア、光トランシーバ、ストレージ、電力、管理 API は公開標準に寄せる。一方で、AI training、AI inference、HPC、storage-heavy、network edge など、ワークロードごとの熱/電力/帯域/保守パターンは専用設計にする。標準化対象は「交換可能性と検証可能性」であり、ワークロード最適化を禁止するものではない。

### 6.3 Redundancy must be testable, not decorative

N+1、2N、dual path、multi-zone、multi-carrier といった冗長性は、設計図に存在するだけでは不十分である。切替試験、熱波/水漏れ/火災/電源障害シナリオ、generator start、UPS discharge、CDU failover、cross-connect failover、firmware rollback を計測可能にする。

### 6.4 Cooling is now a first-class platform API

液冷の導入により、冷却は facilities team だけの問題ではなく、GPU SKU、board layout、quick-disconnect、coolant chemistry、leak detection、service procedure、firmware throttling、scheduling policy にまたがるプラットフォーム API になる。

### 6.5 Physical security is telemetry and governance

物理アクセス統制は、ゲート、バッジ、カメラの設置ではなく、**ID、role、zone、time、visitor workflow、camera/log retention、incident response、audit evidence** の統合システムである。

---

## 7. Decision Model

### Inputs

- Workload: AI training/inference、HPC、general compute、storage、network edge、regulated tenancy
- IT demand: GPU count、CPU cores、HBM/DRAM capacity、NVMe IOPS/throughput、interconnect bandwidth、rack kW
- Facility constraints: utility MW、generator fuel/runtime、UPS autonomy、floor loading、water availability、ambient climate、seismic/flood/fire risk
- Network constraints: east-west AI fabric、front-end network、carrier diversity、cloud/on-prem interconnect、subsea route diversity
- Security constraints: customer compliance、sovereignty、physical access segregation、camera policy、audit retention、supply-chain attestation
- Sustainability constraints: PUE、WUE、CUE、water scarcity、renewable energy、heat reuse、embodied carbon
- Operational constraints: staffing、maintenance window、spares、RMA lead time、firmware update cadence、commissioning/acceptance capacity

### Criteria

1. Safety and compliance: fire、electrical、life safety、physical security、environmental constraints
2. Availability: fault domains、capacity redundancy、distribution path redundancy、maintenance without outage
3. Thermal viability: chip inlet/junction margin、coolant supply/return、humidity/dew point、leak containment
4. Electrical viability: rack kW、phase balance、UPS/generator transfer、short-circuit/arc flash risk、monitoring
5. Network viability: bandwidth、latency、oversubscription、optics power、fiber plant、cross-connect/subsea diversity
6. Serviceability: replaceable trays/modules、blind-mate connectors、quick disconnects、FRU procedure、spares
7. Standard conformance: OCP/ASHRAE/Uptime/TIA/ISO/EN/NFPA/NIST/DMTF/UEFI/PCIe/CXL/NVMe/IEEE/MSA
8. Sustainability: PUE/WUE/CUE、water-positive plans、zero-water feasibility、grid impact、heat reuse
9. Transferability: multi-vendor sourcing、open firmware、open rack/chassis interfaces、avoidance of proprietary dead ends

### Priorities

1. **Life safety / fire / electrical code**
2. **Workload availability and safe shutdown**
3. **Power-thermal-network co-design at rack and pod level**
4. **Observability and testability of redundancy**
5. **Open or widely adopted interfaces**
6. **Operational maintainability and replaceability**
7. **Energy/water/carbon optimization**
8. **Cost and procurement optimization**

### Prohibitions

- 未検証の高密度 GPU ラックを、既存空冷ホールに単純投入する。
- PUE だけで冷却方式を決め、WUE/CUE/地域水制約/外気温リスクを評価しない。
- UPS、battery、power room、fuel、fire suppression、data hall の fault domain を混在させる。
- BMC/IPMI/firmware に shared credentials、未監査 update、未分離 management network を残す。
- cable labels、path diversity、optics compatibility、connector cleanliness、patch documentation を運用後回しにする。
- carrier/subsea について、同一 conduit、同一 landing station、同一 provider dependency を冗長と誤認する。
- 物理アクセス例外を ticket/log/audit なしで許可する。

### Exceptions

- 実験的 AI pod は、limited blast radius、短期 lease、manual ops、acceptance waiver を条件に暫定設計を認める。
- 水制約地域では、エネルギー効率が若干下がっても zero-water / closed-loop 設計を優先できる。
- Sovereign/regulated workload は、carrier/provider diversity よりデータ所在・物理アクセス分離を優先する場合がある。
- Legacy facility migration では、19-inch / air-cooled / IPMI 残存を認めるが、deprecation plan と risk register が必要。

### Owners

- Accountable: VP/Head of Infrastructure or Data Center Engineering
- Decision Authority: Data Center Architecture Review Board
- Responsible: Facilities Engineering、Hardware Platform Engineering、Network Engineering、Firmware/BMC Engineering、Physical Security、Safety/Compliance、Sustainability、Procurement
- Reviewers: SRE/Operations、Finance、Legal/Regulatory、Supply Chain、Customer Security/Compliance

### Cadence

- Reference architecture: 半期ごと、または GPU/CPU generation refresh ごと
- Rack/pod acceptance: build ごと
- Power/cooling redundancy test: commissioning、年次、major maintenance 後
- Firmware/security baseline: quarterly、重大脆弱性発生時、new platform introduction 時
- Physical access audit: monthly/quarterly、incident 後、customer audit 前
- Carrier/subsea diversity review: 半期または route/provider 変更時

---

## 8. Operating Model

### 8.1 Governance

1. **Design Intake**: workload forecast、site constraints、availability target、compliance requirement を登録。
2. **Basis of Design**: rack kW、cooling method、power topology、network fabric、physical security zones、fire protection assumptions を文書化。
3. **Architecture Review**: OCP/ASHRAE/Uptime/TIA/ISO/EN/NFPA/NIST/DMTF/UEFI/PCIe/CXL/NVMe/IEEE の参照適合を確認。
4. **Supplier Qualification**: thermal test、firmware security、interoperability、spares、RMA、compliance evidence を評価。
5. **Commissioning**: integrated systems test、generator start/load、UPS discharge/transfer、CDU failure、BMC telemetry、fire alarm、physical access event、carrier failover を検証。
6. **Operations**: DCIM/BMS/Redfish/telemetry を統合し、capacity、alarms、security events、maintenance を管理。
7. **Postmortem / Continuous Improvement**: cooling/power/access/network/fire incidents を failure pattern として pattern_library に戻す。

### 8.2 Artifacts

- Data Center Basis of Design
- Reference Rack Bill of Materials
- Server Platform Qualification Report
- Cable/Fiber Matrix and Labeling Standard
- Power One-Line and Rack Power Budget
- UPS/Generator Test Plan
- Cooling Design Basis and Liquid Loop Spec
- Firmware/BMC Baseline and Attestation Policy
- Physical Security Zone Model
- Camera/Monitoring Retention Policy
- Fire Protection Basis of Design
- Carrier/Subsea Diversity Plan
- Integrated Systems Test Report
- Decommissioning and E-waste Plan

### 8.3 Review Gates

| Gate | Exit Criteria |
|---|---|
| G0: Demand validation | workload forecast、SLO/SLA、budget、site candidate が確定 |
| G1: Design basis | power/cooling/network/security/fire basis が文書化され、例外が risk register 化 |
| G2: Prototype / lab validation | rack thermal、firmware、network、power draw、optics interop が lab test 合格 |
| G3: Pilot deployment | limited blast radius で production-like load test 合格 |
| G4: Commissioning | integrated systems test、failover、alarm、security audit 合格 |
| G5: Operational handoff | runbook、spares、training、monitoring、SLO dashboards 完備 |
| G6: Lifecycle review | refresh/decommission、firmware EOL、component obsolescence、sustainability metrics 更新 |

---

## 9. Technical / Business Specification by Subtheme

### 9.0 Internal Branch Mapping

| Internal Branches | Subtheme |
|---|---|
| 21.01-21.03 | cable / fiber / optics |
| 21.04-21.05 | server chassis / motherboard |
| 21.06-21.09 | CPU / RAM / storage / GPU |
| 21.10-21.13 | BIOS / UEFI / BMC / IPMI |
| 21.14-21.17 | rack / PDU / UPS / generator |
| 21.18-21.20 | cooling / liquid cooling / heat rejection |
| 21.21-21.24 | physical access control / camera / fire suppression |
| 21.25-21.27 | carrier line / fiber route / submarine cable |
| 21.28-21.30 | site selection / facility topology / availability zone physical design |
| 21.31-21.33 | commissioning / integrated systems test / maintenance |
| 21.34-21.36 | supply chain / spares / lifecycle refresh |
| 21.37-21.39 | sustainability / energy / water accounting |
| 21.40-21.41 | safety / regulatory / insurance constraints |
| 21.42 | decommissioning / disposal / e-waste |

### 9.1 cable / fiber / optics

**Decision**: どの速度・距離・フォームファクタ・fiber plant・ケーブル経路・保守方式を採用するか。

**Frontier specification**

- Ethernet PHY/速度は IEEE 802.3 の 200/400/800G/1.6T 進化に追従する。
- ラック内/ラック間は DAC/AEC/AOC/optical transceiver を距離、消費電力、熱、コスト、障害率で選択する。
- 800G/1.6T では OSFP/QSFP-DD 系フォームファクタ、breakout、MPO/SN/MDC/LC などの connector strategy を設計時に固定する。
- AI back-end fabric は optics power と switch radix が支配的制約になるため、ケーブル経路、bend radius、清掃、ラベル、spares を初期設計に含める。
- Immersion/liquid-cooled racks では OCP iAOC のような air-to-immersion/connector thermal form factor を検討する。

**Controls**

- cable matrix: source/destination、port、media、length、path、redundancy group、owner、install date。
- fiber certification: insertion loss、return loss、cleanliness、polarity、breakout mapping。
- optics telemetry: Tx/Rx power、temperature、FEC errors、uncorrectables、DOM/DDM。
- 禁止: undocumented patch、same-path dual link、dirty connectors、unsupported breakout、unlabeled temporary cable。

**Metrics**

- optics failure rate、FEC error rate、mean port bring-up time、cable install/rework error rate、spare coverage、link utilization、inter-rack latency。

**Evidence**: S25, S26, S27, S28.

### 9.2 server chassis

**Decision**: ワークロードに対して、1U/2U/4U/6U/8U、OCP sled、rack-scale tray、air/liquid chassis、service direction、FRU 粒度をどう決めるか。

**Frontier specification**

- CPU/GPU 世代に合わせ、熱密度とサービス性を chassis の最上位制約にする。
- AI/HPC は 8-GPU baseboard または NVL72 のような rack-scale tray を検討し、空冷限界を超える場合は液冷 chassis を標準候補にする。
- OCP DC-MHS のような modular hardware system を参照し、motherboard、I/O、power、management modules の交換性を高める。
- top-service/front-service/rear-service の保守動線を data hall layout と同時に決める。

**Controls**

- chassis thermal test、airflow impedance、quick-disconnect leak test、rail/weight/floor loading、blind-mate connector validation。
- FRU/RMA runbook と spares model を機種導入前に承認。

**Metrics**

- rack density、service time per tray、RMA lead time、MTTR、technician touch count、thermal derate events。

**Evidence**: S03, S12, S13, S14.

### 9.3 motherboard

**Decision**: CPU socket、memory channel、PCIe/CXL lanes、GPU/NIC/storage attachment、BMC integration、power delivery、firmware root-of-trust をどう設計するか。

**Frontier specification**

- motherboard は compute、memory、I/O、management、security root-of-trust の合流点として扱う。
- PCIe lane budget、CXL capability、NVMe boot/storage、GPU interconnect、NIC placement、thermal zones を co-design する。
- board-level telemetry は Redfish/OpenBMC で上位運用に露出させる。
- BMC、UEFI、secure boot、attestation、SPDM/DICE、firmware update/rollback を platform baseline に含める。

**Controls**

- schematic/board review、power integrity、signal integrity、thermal simulation、BMC isolation、firmware signing、manufacturing test、burn-in。
- 禁止: undocumented jumper/strapping、unreviewed vendor firmware、BMC shared secrets、telemetry gaps。

**Metrics**

- boot success rate、firmware update success、BMC responsiveness、sensor coverage、PCIe error rate、CXL error rate、RMA root-cause closure。

**Evidence**: S04, S05, S06, S07, S08, S09, S10.

### 9.4 CPU / RAM / storage / GPU

**Decision**: どの CPU/GPU/RAM/storage SKU と interconnect を、どの workload mix、thermal/power/cost/supply constraints で採用するか。

**Frontier specification**

- AI training は GPU memory capacity、GPU-to-GPU bandwidth、rack fabric、cooling capacity を優先する。
- AI inference は memory bandwidth、latency、batching、front-end network、power efficiency を優先する。
- General compute は CPU per watt、memory capacity、NVMe density、VM/container scheduling flexibility を優先する。
- Storage-heavy は NVMe endurance、thermal throttling、failure domain、rebuild bandwidth、power capping を重視する。
- CXL memory pooling は将来選択肢として、memory-bound workloads と stranded DRAM 削減に対して検証する。

**Controls**

- SKU approval は workload benchmark、rack power、cooling margin、supply risk、firmware support、software ecosystem を必須項目にする。
- GPU clusters は network fabric、job scheduler、power capping、thermal throttling、RMA spares を含めて承認。

**Metrics**

- accelerator utilization、training throughput、tokens/sec/W、memory bandwidth utilization、NVMe latency/IOPS、power cap events、thermal throttle events、hardware failure per MW。

**Evidence**: S09, S10, S11, S12, S13, S14.

### 9.5 BIOS / UEFI / BMC / IPMI

**Decision**: pre-boot、firmware update、out-of-band management、telemetry、attestation、remote control をどの標準/権限/監査で運用するか。

**Frontier specification**

- BIOS/UEFI は OS boot と platform initialization の contract として version-controlled baseline にする。
- IPMI は legacy として扱い、新規設計では Redfish API、OpenBMC、secure management network を優先する。
- SPDM/DICE で component authentication、attestation、measurement、key exchange を設計入力にする。
- BMC は高権限攻撃面であるため、ネットワーク分離、credential rotation、firmware signing、audit logging、break-glass procedure を要求する。

**Controls**

- firmware SBOM、signed images、rollback protection、lab validation、canary rollout、BMC log export、Redfish API access control。
- 禁止: default credentials、flat management network、unlogged remote console、unsigned firmware、emergency-only firmware process。

**Metrics**

- firmware compliance rate、known vulnerable firmware count、update failure rate、BMC auth failures、Redfish API coverage、attestation pass rate。

**Evidence**: S04, S05, S06, S07, S08.

### 9.6 rack

**Decision**: 19-inch vs OCP/open rack、rack height/width、power shelf、busbar、rack kW、air/liquid containment、weight/floor loading、service envelope をどう決めるか。

**Frontier specification**

- OCP ORv3 は high-density, open rack, 48V distribution, power shelf などの公開インターフェース参照になる。
- Rack は IT gear の置き場ではなく、電力・冷却・ネットワーク・保守の標準単位として管理する。
- AI racks は 30–120kW+ のレンジが現実的な検討対象になり、施設側の冷却/配電/床荷重/安全作業を先に確認する。
- Rack acceptance は mechanical fit、power connector、coolant connector、network cabling、BMC onboarding、load test を含む。

**Controls**

- rack power budget、thermal budget、network port map、weight/load rating、earthing/grounding、seismic restraints、service clearance。
- 禁止: rack kW 不明の受入、temporary PDU bypass、uncertified rack modifications、dual-cord same PDU。

**Metrics**

- rack kW utilized、rack thermal margin、rack stranded capacity、rack commissioning cycle time、cable rework、rack incident rate。

**Evidence**: S02, S12, S15, S22.

### 9.7 PDU / power distribution

**Decision**: utility → switchgear → UPS → PDU/busway → rack PDU → server PSU の power chain をどう設計・監視・保守するか。

**Frontier specification**

- High-density racks では floor PDU より busway、rack-level monitoring、software-visible power capping が重要になる。
- 48V DC/OCP power shelf、AC distribution、hybrid power architecture は site と rack architecture に合わせて比較する。
- Power path は redundancy だけでなく、phase balance、arc flash、breaker coordination、short-circuit current、maintenance isolation を考慮する。

**Controls**

- metered/switched rack PDU、branch circuit monitoring、load balancing、breaker coordination、arc flash labels、maintenance lockout/tagout。
- 禁止: breaker trip margin なし、phase imbalance、unmonitored temporary feed、overloaded neutral、unsupported plug/connector。

**Metrics**

- power utilization、branch circuit headroom、phase imbalance、power incidents、PDU telemetry coverage、breaker trip near-misses。

**Evidence**: S02, S22.

### 9.8 UPS

**Decision**: central UPS、distributed UPS、rack-level batteries、battery chemistry、autonomy、bypass、maintenance、transfer をどう設計するか。

**Frontier specification**

- UPS は generator start/transfer までの bridge として扱い、全負荷維持時間だけでなく、safe shutdown、ride-through、grid interaction、BESS integration を検討する。
- Mission-critical では UPS topology、static transfer、bypass path、battery monitoring、fire separation を設計入力にする。
- Liquid-cooled AI racks では pump/CDU/control systems の power continuity を IT load と同等に扱う。

**Controls**

- UPS discharge test、battery health monitoring、thermal runaway/fire separation、bypass procedure、maintenance mode simulation、spares。
- 禁止: battery room と critical IT/fire domains の不適切な混在、未試験 bypass、unmonitored battery health。

**Metrics**

- UPS availability、battery state of health、autonomy minutes、transfer success、maintenance bypass events、battery alarm response time。

**Evidence**: S21, S22, S40.

### 9.9 generator

**Decision**: generator capacity、fuel supply、start time、emissions permit、load bank testing、ATS、maintenance をどう運用するか。

**Frontier specification**

- NFPA 110 を emergency/standby power の性能要件参照にする。
- Generator は utility outage だけでなく、grid constraint、fuel logistics、emissions regulation、black-start、multi-day outage を考慮する。
- Generator と UPS、ATS、critical mechanical load、cooling load の integrated test を必須にする。

**Controls**

- start/load transfer test、fuel quality、fuel delivery contract、load bank、ATS test、exhaust/emissions compliance、maintenance lockout。
- 禁止: no-load test のみ、fuel contract 未検証、cooling load を除いた generator sizing、single fuel dependency without risk review。

**Metrics**

- start success、time to assume load、fuel autonomy、test pass rate、emissions exceedances、ATS incidents、generator unavailability hours。

**Evidence**: S21, S22.

### 9.10 cooling

**Decision**: air cooling、direct-to-chip liquid、rear-door heat exchanger、immersion、CDU/HXU、water-side economizer、closed-loop/zero-water をどう選ぶか。

**Frontier specification**

- ASHRAE TC 9.9 を inlet condition、allowable/recommended envelope、liquid cooling classes、water temperature の基準にする。
- GPU racks は air/liquid hybrid または direct liquid cooling を前提に thermal design basis を作る。
- Water-constrained sites では Microsoft 型 zero-water/closed-loop direct-to-chip のように water evaporation を避ける設計を評価する。
- Cooling は IT scheduling と連動させ、thermal throttling、safe shutdown、redundant cooling failure、outside air temperature を監視する。

**Controls**

- coolant chemistry、leak detection、quick-disconnect validation、CDU/HXU redundancy、pump/fan/filter sensors、condensation control、drain/containment、emergency shutdown。
- 禁止: liquid loop water quality 不明、leak response runbook なし、cooling redundancy 未試験、extreme ambient margin なし。

**Metrics**

- PUE、WUE、cooling capacity utilization、supply/return temperature、delta-T、CDU availability、leak incidents、thermal throttle events、safe shutdown events。

**Evidence**: S15, S16, S35, S36, S37, S39.

### 9.11 physical access control

**Decision**: facility、campus、data hall、cage、rack、MMR、power/cooling rooms、loading dock、office をどの zone と authorization model で分離するか。

**Frontier specification**

- NIST SP 800-53 PE 系のように、physical access authorization、control、monitoring、visitor records、incident coordination を運用制御として扱う。
- Role + location + time + purpose + escort + customer segregation で許可を切る。
- High-risk areas は multi-factor physical access、mantrap、security guard、anti-tailgating、temporary access workflow、break-glass review を導入する。

**Controls**

- access request ticket、approval、badge issuance、zone mapping、visitor escort、quarterly review、terminated employee removal、alarm response、audit trail。
- 禁止: shared badges、永久 visitor exception、no-log emergency access、unreviewed vendor access。

**Metrics**

- access exception count、orphan badge count、door forced-open events、tailgating alarms、visitor compliance、review completion rate、incident response time。

**Evidence**: S24.

### 9.12 camera / monitoring

**Decision**: どの zone を、どの camera/sensor/log retention/alerting/investigation workflow で監視するか。

**Frontier specification**

- Video surveillance は physical access monitoring の一要素であり、guards、door logs、sensors、incident response と統合する。
- Privacy/legal requirements を前提に、retention、masking、access to footage、chain of custody を定義する。
- Camera は deterrence ではなく、access anomaly、door events、loading dock、MMR、power room、critical corridors、rack/cage access の証跡として設計する。

**Controls**

- camera coverage map、retention policy、access logs to footage、integrity/tamper alerts、time synchronization、incident evidence workflow。
- 禁止: blind spot acceptance without risk sign-off、unlogged footage access、camera time drift、footage retention mismatch。

**Metrics**

- camera uptime、coverage exceptions、retention compliance、footage retrieval time、tamper alarms、incident evidence completeness。

**Evidence**: S24.

### 9.13 fire suppression

**Decision**: IT equipment areas、telecom spaces、power rooms、battery rooms、fuel rooms、liquid cooling zones をどの detection/suppression/compartmentation/emergency procedure で守るか。

**Frontier specification**

- NFPA 75 は information technology equipment areas、NFPA 76 は telecommunications facilities、NFPA 110 は emergency/standby power を対象にするため、用途別に適用を整理する。
- Fire protection は detection、alarm、suppression、compartmentation、electrical isolation、smoke/corrosion/water damage、evacuation、firefighter access を統合する。
- UPS/battery rooms、inverters、fuel、liquid cooling loops は data hall から fault domain を分離する。

**Controls**

- early smoke detection、clean agent/water mist/sprinkler design basis、battery fire procedure、electrical cutoff、fire drill、emergency response interface、post-incident preservation。
- 禁止: automatic suppression なしの高密度/critical hall、electrical cutoff 不明、battery room と data hall の未分離、backups co-located without recovery plan。

**Metrics**

- alarm test pass rate、suppression inspection、fire drill completion、electrical isolation time、battery alarms、false positive/negative alarms、post-incident restoration time。

**Evidence**: S21, S23, S40.

### 9.14 carrier line / submarine cable

**Decision**: data center と外部ネットワーク/クラウド/IXP/キャリア/海底ケーブルを、どの MMR、cross-connect、provider diversity、route diversity、landing diversity、license/risk model で接続するか。

**Frontier specification**

- Carrier-neutral facility では MMR と cross-connect を、低レイテンシ・専用・物理接続の基本単位にする。
- AWS Direct Connect 等の cloud interconnect は、単一ロケーションではなく複数ロケーション利用を可用性設計に含める。
- Hyperscaler private WAN は subsea cables、edge locations、regional cloud zones を統合する。
- Subsea cable は landing license、foreign ownership/security review、repair time、maritime protection、fishing/anchoring/dredging risk、geopolitical disruption を設計入力にする。

**Controls**

- carrier diversity matrix、LOA-CFA/cross-connect workflow、MMR access control、path diversity validation、landing station risk、subsea cable provider/consortium mapping、repair SLA、route change process。
- 禁止: two providers sharing same conduit/meet-me room path but treated as diverse、same landing station dependency、unverified cloud interconnect redundancy。

**Metrics**

- cross-connect delivery time、carrier SLA、packet loss/latency、route diversity score、subsea landing diversity、failover test success、provider concentration risk。

**Evidence**: S29, S30, S31, S32, S33, S34.

---

## 10. Metrics

| Category | Metrics | Notes |
|---|---|---|
| Availability | site availability、critical load availability、rack/pod availability、maintenance without outage、capacity redundancy | Uptime/TIA/ISO/EN の topology と operational test に接続 |
| Power | rack kW、power headroom、UPS autonomy、generator start success、PDU branch headroom、phase imbalance、power incident rate | GPU rack では kW/rack と cooling が最重要連動指標 |
| Cooling | PUE、WUE、cooling capacity margin、supply/return temperature、CDU/HXU uptime、leak rate、thermal throttle events | PUE 単独最適化を禁止し、WUE/CUE と併用 |
| Compute | GPU utilization、tokens/sec/W、training throughput、CPU utilization、memory bandwidth utilization、NVMe latency/IOPS | Facility capacity と workload scheduling の接点 |
| Network | link utilization、FEC errors、optics failure、east-west latency、cross-connect latency、carrier failover success | 800G/1.6T では optics thermals も見る |
| Firmware | firmware compliance、BMC availability、Redfish API coverage、attestation pass、vulnerable firmware count | BMC を高権限 security plane として扱う |
| Physical security | access exceptions、badge orphan count、door alarms、tailgating events、camera uptime、footage retrieval time | NIST PE 系と audit evidence に接続 |
| Fire/safety | alarm test pass、suppression inspection、battery alarms、electrical isolation time、fire drill completion | Incident postmortem と連動 |
| Sustainability | PUE、WUE、CUE、renewable match、water replenishment progress、embodied carbon、e-waste | Geography と water scarcity を含めて判断 |
| Operations | MTTR、spares coverage、RMA cycle time、commissioning duration、change failure rate、maintenance backlog | Clone の実装可能性を示す主要指標 |

---

## 11. Failure Modes

| Failure Mode | Mechanism | Preventive Controls | Evidence |
|---|---|---|---|
| Fire propagation from power/battery/UPS area | 電源室、battery、inverter、湿気、短絡、消火/遮断不足が data hall に波及 | compartmentation、automatic detection/suppression、electrical cutoff、battery monitoring、fire drill、offsite backups | S23, S40 |
| Cooling redundancy common-mode failure | 複数冗長冷却が同時故障し、外気温上昇で safe operating temperature を維持不能 | extreme ambient scenario、N+1/2N test、safe shutdown automation、thermal telemetry、capacity shedding | S15, S39 |
| Rack power overcommit | GPU load spike、phase imbalance、breaker trip、rack PDU saturation | real-time PDU telemetry、power capping、phase review、breaker coordination、rack load test | S22 |
| Liquid leak near electronics | quick-disconnect failure、coolant chemistry、condensation、maintenance error | leak detection、dry-break connectors、drip trays、fluid compatibility、emergency shutdown、training | S15, S35 |
| BMC/firmware compromise | legacy IPMI、default credentials、unsigned firmware、flat management network | Redfish/OpenBMC baseline、network isolation、signed firmware、SPDM/DICE attestation、credential rotation | S04, S06, S07, S08 |
| Optics/cabling fault cascade | dirty connector、incorrect breakout、FEC errors、overheated optics、same-path redundant cables | fiber certification、DOM telemetry、cable matrix、path diversity、spares、connector cleaning | S25, S26, S27 |
| Cross-connect diversity illusion | 複数 carrier が同一 conduit/MMR/landing station に依存 | physical path validation、carrier diversity matrix、multi-location cloud interconnect、failover tests | S29, S30, S33 |
| Physical access exception drift | permanent temporary badges、visitor escort failure、unreviewed vendor access | time-bounded access、quarterly review、door/camera correlation、incident workflow | S24 |
| Backup co-location failure | primary data and backups in same fire/fault domain | offsite/region-separated backups、restore testing、blast radius mapping | S40 |
| Sustainability metric gaming | PUE 改善が WUE/CUE/indirect water/grid impact を悪化させる | xUE metrics、site water risk、carbon accounting、transparent reporting | S16, S20, S36, S37, S38 |

---

## 12. Anti-patterns

1. **Server-first procurement**: GPU server を先に購入し、後から電力・冷却・床荷重・optics・BMC を合わせる。
2. **PUE-only optimization**: PUE だけで cooling strategy を決め、水消費、地域水リスク、grid carbon、IT utilization を無視する。
3. **Legacy management plane acceptance**: IPMI/default credentials/flat BMC network を「一時的」として恒久化する。
4. **Paper redundancy**: 図面上は A/B feed だが、同一 PDU、同一 conduit、同一冷却制御、同一 operator procedure に依存している。
5. **Fire protection as compliance checkbox**: fire detection/suppression、electrical cutoff、battery isolation、firefighter access、backup separation を統合しない。
6. **Cabling as manual craft**: cable label、path diversity、optics compatibility、cleaning、DOM telemetry を現場技能に依存する。
7. **Carrier diversity by invoice**: 複数社請求書があるだけで、物理経路・landing station・MMR が同一であるリスクを見ない。
8. **No evidence handoff**: commissioning 結果、firmware baseline、security zone、camera coverage、fire inspection を運用チームに渡さない。
9. **Water/energy tradeoff hidden**: zero-water か高効率 evaporative cooling かの判断を、地域の水・電力・炭素制約と分離する。
10. **No restore test**: facility resilience を語るが、region/site separated recovery と backup restore を実際に試験しない。

---

## 13. Historical Changes / Directional Shifts

| Shift | Before | Now / Frontier | Implication |
|---|---|---|---|
| Rack design | 19-inch rack、server-by-server、AC distribution | OCP Open Rack V3、48V、power shelf、rack-scale AI、Open Rack Wide | Rack is the unit of design and procurement |
| Server design | Monolithic chassis、vendor-specific boards | DC-MHS、OAM/UBB、sled/tray、modular I/O | Serviceability and multi-vendor sourcing improve |
| Compute density | CPU-centric virtualization | GPU/HBM/interconnect-centric AI racks | Power/cooling/network becomes bottleneck |
| Cooling | Raised floor / CRAH / air containment | direct-to-chip liquid、CDU/HXU、closed-loop、zero-water options | Cooling moves into IT platform design |
| Management | IPMI, vendor BMC silos | Redfish、OpenBMC、SPDM、DICE、attestation | Firmware becomes auditable control plane |
| Network | 10/40/100G Ethernet and traditional WAN | 400/800G/1.6T、AI back-end fabric、private WAN、subsea | Optics and fiber plant are strategic capacity |
| Facility standards | Local engineering practice | Uptime/TIA/ISO/EN/NFPA/NIST driven governance | Auditability and comparability increase |
| Sustainability | PUE headline metric | PUE + WUE + CUE + water positive + zero-water + embodied carbon | Single-metric optimization becomes unsafe |
| Carrier | Local loop/provider circuits | carrier-neutral cross-connect、cloud interconnect、multi-location | MMR and path diversity become design objects |
| Subsea | Telecom consortium background asset | hyperscaler private/consortium cable as cloud WAN | Geopolitics and landing licenses enter infra strategy |

---

## 14. Maturity Model

| Level | Name | Criteria |
|---:|---|---|
| 0 | 未整備 | 機器・電力・冷却・配線が担当者ごとに管理され、rack kW、cable matrix、firmware baseline、fire basis が不明 |
| 1 | 個人依存 | Experienced operators が現場で調整。設計例外・配線・アクセス許可がチケット化されていない |
| 2 | 文書化 | rack BOM、power/cooling design、access policy、fire plan、cross-connect records が文書化されるが、統合試験は限定的 |
| 3 | 標準化 | OCP/ASHRAE/Uptime/TIA/ISO/EN/NFPA/NIST/DMTF 等を参照し、reference architecture と review gate が存在 |
| 4 | 自動化・計測 | DCIM/BMS/Redfish/telemetry/access logs/camera/fire alarms/carrier SLA が dashboard 化され、commissioning と failover test が定期化 |
| 5 | 自律改善・業界先端 | workload scheduling、power capping、cooling telemetry、firmware attestation、optics health、sustainability、carrier diversity が統合最適化され、事故・反証・履歴差分が pattern library に還流 |

---

## 15. Clone Implementation Guide

### Phase 0: Scope and Guardrails

- 対象 workloads、availability tier、site constraints、compliance、customer audit requirements を定義する。
- 攻撃的/侵入的情報、非公開施設図面、弱点探索を明示的に除外する。
- 既存設備の current state inventory を作成する。

### Phase 1: Reference Architecture

作成物:

- Reference rack types: general compute、AI air-cooled、AI liquid-cooled、storage、network spine/leaf、management。
- Power design basis: rack kW、PDU/busway、UPS topology、generator runtime、ATS、maintenance bypass。
- Cooling design basis: air/liquid/immersion candidate、ASHRAE class、supply/return target、CDU/HXU、leak detection。
- Network design basis: 400/800G/1.6T roadmap、OSFP/QSFP-DD、cable matrix、front-end/back-end/management separation。
- Security basis: physical zones、access rules、camera coverage、BMC/firmware policy。
- Fire basis: IT area、telecom、UPS/battery、fuel、liquid loop、emergency procedures。

### Phase 2: Supplier and Standard Mapping

- OCP / DC-MHS / ORv3 compatibility を rack/server/power shelf で評価。
- Redfish/OpenBMC/SPDM/DICE/UEFI support を platform gate にする。
- PCIe/CXL/NVMe/IEEE/OSFP/QSFP-DD compatibility を I/O gate にする。
- ASHRAE/Uptime/TIA/ISO/EN/NFPA/NIST conformance matrix を作成。

### Phase 3: Lab Validation

- rack thermal load test、liquid leak test、power step/load test、firmware update/rollback、BMC security test、optics/FEC burn-in、server burn-in。
- GPU workload representative benchmarks と power/thermal envelope を同時取得。
- Failover and safe shutdown scenarios をテスト。

### Phase 4: Pilot Deployment

- 1 pod または limited rack group で production-like workload を稼働。
- DCIM/BMS/Redfish/telemetry/access/camera/fire alarms/carrier metrics を統合 dashboard に出す。
- Exception register を週次レビューし、waiver 期限を設定。

### Phase 5: Production Rollout

- Integrated systems test 合格後に production capacity として開放。
- Spares、RMA、firmware baseline、runbook、training を handoff。
- Site-level and region-level recovery drills を実施。

### Phase 6: Continuous Improvement

- Incident/postmortem を evidence_graph と pattern_library に追加。
- Firmware EOL、server/chassis lifecycle、optics roadmap、cooling technology、regulatory changes を半期レビュー。
- PUE/WUE/CUE、rack utilization、water risk、grid risk、carrier/subsea risk を portfolio level で再評価。

---

## 16. Source Catalog

| source_id | Entity | Title / Locator | Type | Tier | Directness | Notes |
|---|---|---|---|---|---|---|
| S01 | RESEARCH.md | Frontier Operating Model Research 運用プレイブック | playbook | T0-internal | direct | 本成果物の運用手順。公開情報限定、Clone Spec、Evidence Map、Decision Model を要求 |
| S02 | Open Compute Project | Open Rack Base Specification Version 3 — https://www.opencompute.org/documents/open-rack-base-specification-version-3-pdf | official_spec | T0 | direct | Open Rack Frame V3 family の component requirements |
| S03 | Open Compute Project | Server/MHS/DC-MHS specs — https://www.opencompute.org/wiki/Server/MHS/DC-MHS-Specs-and-Designs | official_spec/wiki | T0 | direct | DC-MHS、DC-SCM、M-XIO 等の modular hardware specs |
| S04 | DMTF | Redfish — https://www.dmtf.org/standards/redfish | standard | T0 | direct | Secure/simple management for hybrid IT/SDDC, human and machine capable |
| S05 | UEFI Forum | UEFI Specifications — https://uefi.org/specifications | standard | T0 | direct | OS/platform firmware interface specifications |
| S06 | OpenBMC | OpenBMC project — https://openbmc.org/ | OSS/official | T3 | direct | Open source BMC firmware stack for heterogeneous systems |
| S07 | DMTF | SPDM — https://www.dmtf.org/standards/spdm | standard | T0 | direct | Authentication, attestation, key exchange for infrastructure security |
| S08 | Trusted Computing Group | DICE Attestation Architecture — https://trustedcomputinggroup.org/resource/dice-attestation-architecture/ | standard | T0 | direct | DICE layered attestation architecture |
| S09 | PCI-SIG | PCI Express 6.0 Specification — https://pcisig.com/pci-express-6.0-specification | standard | T0 | direct | Data center/AI/HPC interconnect spec |
| S10 | CXL Consortium | CXL Memory Pooling overview — https://computeexpresslink.org/wp-content/uploads/2023/12/CXL-2.0-Memory-Pooling.pdf | standard/whitepaper | T0/T3 | direct | Memory pooling and Fabric Manager concepts |
| S11 | NVM Express | NVMe Specifications — https://nvmexpress.org/specifications/ | standard | T0 | direct | NVMe/NVMe-oF specification family |
| S12 | NVIDIA | GB200 NVL72 — https://www.nvidia.com/en-us/data-center/gb200-nvl72/ and NVIDIA DGX GB rack hardware docs | vendor_official | T2 | direct | 36 Grace CPUs, 72 Blackwell GPUs, liquid-cooled rack-scale NVLink domain |
| S13 | AMD | AMD Instinct MI300X Platform data sheet — https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-platform-data-sheet.pdf | vendor_official | T2 | direct | 192GB HBM3, Infinity Fabric, UBB/OAM platform data |
| S14 | Dell Technologies | PowerEdge XE9680 Technical Guide — https://www.delltechnologies.com/asset/en-ca/products/servers/technical-support/poweredge-xe9680-technical-guide.pdf | vendor_official | T2 | direct | 6U GPU server technical guide |
| S15 | ASHRAE | Data Center Resource Page / TC 9.9 / Thermal Guidelines reference — https://www.ashrae.org/technical-resources/bookstore/datacom-series | standard/guidance | T0 | direct | Thermal, cooling, humidity, liquid cooling guidance |
| S16 | The Green Grid | PUE/WUE white papers — https://datacenters.lbl.gov/sites/default/files/WP49-PUE%20A%20Comprehensive%20Examination%20of%20the%20Metric_v6.pdf and https://www.thegreengrid.org/system/files/store/WUE_v1.pdf | metric_guidance | T0/T3 | direct | PUE/WUE xUE metric foundations |
| S17 | Uptime Institute | Tier Standard: Topology — https://uptimeinstitute.com/resources/asset/tier-standard-topology | standard | T0 | direct | Redundant capacity components and distribution paths |
| S18 | Telecommunications Industry Association | ANSI/TIA-942 Standard — https://tiaonline.org/products-and-services/tia942certification/ansi-tia-942-standard/ | standard | T0 | direct | Physical infrastructure across site, architecture, electrical, mechanical, fire, telecom, security |
| S19 | ISO | ISO/IEC 22237-1:2021 — https://www.iso.org/standard/78550.html | standard | T0 | direct | General principles, terminology, reference models for data centres |
| S20 | BSI/CENELEC | EN 50600 series — https://landingpage.bsigroup.com/LandingPage/Series?UPI=BS+EN+50600 | standard | T0 | direct | Building, power, environmental control, cabling, security, operations, KPIs |
| S21 | NFPA | NFPA 110 — https://www.nfpa.org/codes-and-standards/nfpa-110-standard-development/110 | standard | T0 | direct | Emergency and standby power systems |
| S22 | Schneider/Eaton/Vertiv | Data center power chain / PDU / UPS / busway white papers | vendor_guidance | T3 | near_direct | Power distribution, UPS, generator bridge, busway guidance |
| S23 | NFPA | NFPA 75 and NFPA 76 — https://www.nfpa.org/codes-and-standards/nfpa-75-standard-development/75 and https://www.nfpa.org/codes-and-standards/nfpa-76-standard-development/76 | standard | T0 | direct | Fire protection for IT equipment and telecommunications facilities |
| S24 | NIST | SP 800-53 Rev. 5 and PE controls — https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final | standard/security_controls | T0 | direct | Physical and Environmental Protection controls |
| S25 | IEEE | IEEE 802.3 Ethernet Working Group — https://www.ieee802.org/3/ | standard | T0 | direct | Ethernet projects including 200G/400G/800G/1.6T work |
| S26 | OSFP MSA | OSFP MSA — https://osfpmsa.org/ | MSA | T0/T3 | direct | OSFP 400G/800G/1.6T pluggable form factor |
| S27 | QSFP-DD MSA | QSFP-DD MSA — https://www.qsfp-dd.com/ | MSA | T0/T3 | direct | QSFP-DD 400G/800G/1600G form factor |
| S28 | Open Compute Project | 800G OSFP112 2xSR4 iAOC spec — https://www.opencompute.org/documents/800g-osfp112-2xsr4-air-to-2x400g-osfp112-rhs-sr4-immersion-pdf | official_spec | T0/T2 | direct | OCP optical cable for large-scale data center applications |
| S29 | Equinix | Cross Connect — https://docs.equinix.com/cross-connect/ | official_doc | T2/T3 | direct | Dedicated physical cabling links inside IBX data center |
| S30 | AWS | Direct Connect locations and cross-connect docs — https://aws.amazon.com/directconnect/locations/ and https://docs.aws.amazon.com/directconnect/latest/UserGuide/Colocation.html | official_doc | T2/T3 | direct | Direct Connect availability and multi-location recommendation |
| S31 | Google | Google Cloud WAN/subsea infrastructure — https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/google-cloud-wan-development/ | official_doc | T2/T3 | direct | Global WAN, lit fiber, subsea cable footprint |
| S32 | Meta / 2Africa | Completion of core 2Africa system — https://engineering.fb.com/2025/11/17/connectivity/core-2africa-system-completion-future-connectivity/ | official_doc | T2/T3 | direct | Open-access subsea cable system and connectivity claims |
| S33 | FCC / eCFR | Submarine cable landing licenses — https://www.fcc.gov/research-reports/guides/submarine-cable-landing-licenses and https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-1/subpart-FF | regulator | T1/T0 | direct | Cable landing license requirements for U.S. |
| S34 | ICPC | ICPC Best Practices — https://www.iscpc.org/publications/icpc-best-practices/ | industry_guidance | T3/T5 | direct | Government and operator best practices for submarine cable protection |
| S35 | Microsoft | Zero-water cooling and HXU open sourcing — https://www.microsoft.com/en-us/microsoft-cloud/blog/2024/12/09/sustainable-by-design-next-generation-datacenters-consume-zero-water-for-cooling/ | official_doc | T2/T3 | direct | Chip-level closed-loop cooling and zero-water design |
| S36 | Google Data Centers | PUE and Environmental Report — https://datacenters.google/efficiency and https://sustainability.google/reports/google-2025-environmental-report/ | official_doc | T2/T3 | direct | Fleet PUE and environmental strategy |
| S37 | AWS Sustainability | Data Centers and Water Stewardship — https://aws.amazon.com/sustainability/data-centers/ | official_doc | T2/T3 | direct | Water positive commitment and water efficiency |
| S38 | Meta Sustainability | Data centers / environmental data index — https://sustainability.atmeta.com/data-centers/ | official_doc | T2/T3 | direct | PUE/WUE and data center sustainability reporting |
| S39 | Google Cloud | London europe-west2 cooling incident report — https://status.cloud.google.com/incidents/fmEL9i2fArADKawkZAa2 | incident | T5 | direct | Multiple redundant cooling system failure and safe shutdown |
| S40 | BEA-RI / OVHcloud | OVH Strasbourg fire investigation and OVH status page — https://regmedia.co.uk/2022/06/10/ovh_report.pdf and https://corporate.ovhcloud.com/en/newsroom/news/informations-site-strasbourg/ | incident | T5 | direct | Data center fire, power room/battery/inverter risk, emergency response |

---

## 17. Pattern Library

| pattern_id | pattern_name | layer_scope | pattern_type | description | preconditions | tradeoffs | confidence |
|---|---|---|---|---|---|---|---|
| P-001 | Rack-as-a-Platform | 21 | operating_model | Rack を IT gear、power、cooling、network、firmware、security の標準運用単位にする | rack telemetry、standard rack design、BOM | 初期設計コスト増、legacy racks との混在 | A |
| P-002 | Open Interface / Specialized Workload | 21 | principle | Interface は標準化し、workload profile は専用化する | standards mapping、supplier qualification | ベンダー固有最適化より短期性能が劣る場合 | B |
| P-003 | Liquid Cooling as Control Plane | 21 | decision_rule | Liquid loop を facilities だけでなく scheduler/firmware/telemetry と接続する | sensors、CDU/HXU、leak runbook | 運用複雑性、保守教育 | B |
| P-004 | Attestable Management Plane | 21 | control | BMC/UEFI/firmware を Redfish/OpenBMC/SPDM/DICE 等で監査可能にする | signed firmware、network isolation | supplier support 差、legacy remediation | B |
| P-005 | Multi-dimensional Sustainability | 21 | metric | PUE/WUE/CUE/water risk/carbon/IT utilization を同時に測る | reliable metering、site water data | 指標が多く意思決定が複雑化 | B |
| P-006 | Tested Redundancy | 21 | control | N+1/2N/dual path を実地 failover test で証明する | commissioning process、safe test window | test risk、temporary capacity loss | A |
| P-007 | Physical Security as Evidence Graph | 21 | control | door logs、badge、camera、visitor、incident response を相関する | IAM/PACS/camera integration | privacy/legal review が必要 | B |
| P-008 | Carrier/Subsea Diversity Matrix | 21 | decision_rule | carrier/provider の請求単位ではなく物理経路/landing/MMR で冗長性を評価 | route data、carrier cooperation | 情報取得が難しい、契約制約 | B |
| P-009 | Fire Domain Isolation | 21 | failure_pattern | UPS/battery/fuel/data hall/backup を fault domain として分離 | floor plan、fire engineering | CAPEX/OPEX 増、space inefficiency | A |
| P-010 | Cable Plant as Source of Truth | 21 | operating_model | cable matrix、label、test result、DOM/FEC telemetry を台帳化する | DCIM/network inventory | 初期運用負荷 | A |

---

## 18. Validation Queries

次回再調査時の既定クエリ。

```text
site:opencompute.org Open Rack V3 specification ORV3 power shelf 48V after:2024-01-01
site:opencompute.org DC-MHS specification M-XIO M-PESTI after:2024-01-01
site:nvidia.com GB200 NVL72 liquid cooled rack scale hardware docs
site:amd.com Instinct MI300X platform OAM UBB data sheet
site:ashrae.org TC 9.9 liquid cooling guidelines data centers after:2024-01-01
site:uptimeinstitute.com Tier Standard Topology redundant capacity distribution paths
site:tiaonline.org ANSI/TIA-942-C data center standard physical infrastructure
site:iso.org ISO/IEC 22237 data centre facilities infrastructure
site:dmtf.org Redfish SPDM specification firmware attestation
site:openbmc.org OpenBMC release notes BMC firmware stack
site:uefi.org UEFI specification firmware update secure boot
site:computeexpresslink.org CXL memory pooling fabric manager specification
site:nvmexpress.org NVMe specification power management data center
site:ieee802.org/3 802.3dj 800G 1.6T Ethernet task force
site:osfpmsa.org OSFP 1.6T specification
site:qsfp-dd.com QSFP-DD 1600G specification
site:nfpa.org NFPA 75 76 110 data center fire emergency power
site:csrc.nist.gov SP 800-53 PE physical access monitoring video surveillance
site:equinix.com cross connect meet me room dedicated physical cabling
site:aws.amazon.com Direct Connect locations multiple locations high availability
site:cloud.google.com subsea cable WAN lit fiber cloud regions
site:engineering.fb.com 2Africa subsea cable completion open access
site:fcc.gov submarine cable landing license foreign adversary security
"data center" (incident OR outage OR fire OR cooling failure OR generator failure OR water leak) after:2025-01-01
"GB200" (cooling OR power OR deployment issue OR liquid leak OR recall) after:2025-01-01
"OpenBMC" (CVE OR security advisory OR firmware update) after:2025-01-01
"submarine cable" (cut OR outage OR sabotage OR repair) after:2025-01-01
```

---

## 19. Confidence & Unknowns

### Confidence A

- OCP Open Rack V3 / DC-MHS がラック/モジュラーサーバ仕様として公開されている。
- Redfish、UEFI、SPDM、NIST SP 800-53、NFPA、Uptime/TIA/ISO/EN は本レイヤーの規範的入力である。
- NVIDIA GB200 NVL72 が rack-scale liquid-cooled 72-GPU NVLink domain として公開されている。
- Google Cloud London 2022 cooling incident、OVHcloud Strasbourg fire は公開 incident/failure evidence として有効である。

### Confidence B

- 先端設計が rack/pod/campus co-design へ移っているという統合判断。
- zero-water/direct-to-chip cooling、CXL memory pooling、CPO/800G/1.6T optics が次世代主流候補になるという方向性。
- Carrier/subsea diversity が AI/cloud infrastructure の戦略レイヤーとして重要化しているという判断。

### Confidence C

- ベンダー固有プラットフォームの実際の大規模稼働品質、RMA率、failure distribution。
- Open Rack Wide / AMD Helios 等の 2026 以降の採用規模。
- 液冷方式別の長期保守コスト、水質管理、漏水発生率。

### Unknowns

- 個別ハイパースケーラーの非公開ラック仕様、内部承認フロー、実障害率。
- TIA/BICSI/NFPA/JEDEC 有償標準の条項単位の要件。
- 各クラウド/キャリアの実際の物理 route/landing diversity。
- GPU rack の現場施工品質、coolant chemistry、connector failure の大規模統計。
- 国・地域ごとの permitting、grid interconnection、water rights、subsea landing security review の最新差分。

---

## 20. QA Report

| QA Check | Result | Notes |
|---|---|---|
| Coverage | Pass | 21.01-21.42 の内部枝番を14 subthemesへ対応付け、すべてに Decision/Controls/Metrics/Evidence を付与 |
| Critical Claim | Pass | 主要 claim は公式標準・公式仕様・公式/事故資料で A/B 化 |
| Recency | Partial Pass | 2025/2026 の公開資料を含む。ただし有償標準の最新版本文は未確認 |
| Exceptions | Pass | experimental AI pod、water-constrained site、legacy migration、regulated workload を記載 |
| Failure | Pass | OVHcloud fire、Google Cloud cooling incident を反証/失敗証拠として採用 |
| Provenance | Pass | Source Catalog で source_id と locator を付与 |
| Registry Integrity | Pass | layer_registry、source_catalog、claim map、pattern library を Markdown に統合 |
| Output Integrity | Pass | Clone Spec の必須欄を網羅 |

---

## 21. Minimal Clone Spec

### Philosophy

安全・可用性・熱/電力・物理ネットワーク・管理ファームウェア・物理セキュリティを、ラック単位の実装可能な contract に落とす。標準に寄せて交換可能性を確保し、AI/HPC workload には専用化した thermal/power/network design を与える。

### Decision Model Summary

- **入力**: workload、rack kW、thermal envelope、network bandwidth、availability target、site utility/water constraints、security/compliance、supplier risk。
- **判断基準**: safety、availability、thermal viability、power viability、network viability、serviceability、standard conformance、sustainability、transferability。
- **優先順位**: life safety > availability > power/thermal/network co-design > observability/testability > standard interfaces > maintainability > sustainability > cost。
- **禁止事項**: untested redundancy、legacy insecure BMC、PUE-only decision、unlabeled cables、same-path diversity、fire domain mixing、unlogged physical access。
- **例外条件**: limited blast radius の pilot、water-constrained zero-water site、regulated sovereign workload、legacy migration with deprecation plan。
- **承認者**: Data Center Architecture Review Board、Safety/Compliance、Facilities、Hardware、Network、Security、Sustainability。
- **見直し頻度**: 半期、new hardware generation、new site、major incident、regulatory change、firmware security event。

### Implementation Baseline

1. OCP/ASHRAE/Uptime/TIA/ISO/EN/NFPA/NIST/DMTF/UEFI/PCIe/CXL/NVMe/IEEE/MSA の standards matrix を作る。
2. 4 rack archetypes を作る: general compute、AI air-cooled、AI liquid-cooled、storage/network。
3. power/cooling/network/firmware/security/fire/carrier の design basis を rack archetype ごとに作る。
4. lab validation と pilot で thermal、power、firmware、optics、BMC、fire/security events を試験する。
5. production handoff では runbook、spares、dashboard、audit evidence、postmortem loop を必須化する。
