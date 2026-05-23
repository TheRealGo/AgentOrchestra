# Frontier Operating Model Research: 仮想化・クラウド基盤（Layer 19）

Generated at: 2026-05-13 Asia/Tokyo  
Research mode: 公開情報限定。一次情報・公式ドキュメント・標準・公開インシデントレポートを優先。  
Target layer unit: **仮想化・クラウド基盤**  
Target range: **19**  
Primary subthemes: hypervisor、VM、vCPU/vMemory/vDisk/vNIC、VM image、snapshot、live migration、region、AZ、VPC、subnet、route、internet/NAT gateway、security group、private endpoint、cloud IAM、quota、billing、audit、managed services

---

## 1. Executive Summary

このレイヤーの意思決定対象は、物理インフラを抽象化した計算・保存・通信・統制の基盤を、どの粒度で仮想化し、どのリージョン/ゾーン/ネットワーク/権限/費用境界に配置し、どの失敗条件まで許容して運用するかである。先端組織は、クラウドを「サーバー置き場」ではなく、**計算資源・ネットワーク到達性・権限・コスト・監査証跡を同時に制御する意思決定システム**として扱っている。

公開証拠から見える Frontier pattern は次の通りである。

1. **仮想化は抽象化であると同時に、配置・容量・障害ドメイン・責任境界を明示化する仕組みである。** NIST SP 800-125 は、hypervisor / VMM が guest OS と物理 CPU・disk・memory・NIC の間を制御し、資源分割と隔離を担うことを仮想化の中核として扱う。NIST SP 800-145 はクラウドを、共有された設定可能な資源プールへのオンデマンドネットワークアクセス、迅速なプロビジョニング、計測可能な利用として定義する。
2. **VMの仕様は、vCPU・memory・disk・network・image・snapshot・network interface の組み合わせであり、プロビジョニングの自由度と運用責任は同時に増える。** AWS EC2、Azure Virtual Machines、Google Compute Engine はそれぞれ instance type / VM size / machine type を通じて、CPU・memory・storage・network capacity を workload profile に合わせて選択させる。
3. **region / availability zone / zone は、地理ではなく障害ドメインである。** AWS は region と AZ、Azure は region と availability zone、Google Cloud は region と zone を提供し、いずれも単一障害ドメインを超えた配置を高可用性設計の基本単位にしている。
4. **VPC / VNet / VPC network は、仮想ネットワークというよりも「到達性の明細」である。** subnet、route table、internet gateway、NAT gateway、security group / firewall、private endpoint を組み合わせ、何が internet に出られるか、何が private backbone に閉じるか、何が別 trust boundary に接続できるかを明示する。
5. **IAM・quota・billing・audit は、後工程の管理ではなく、クラウド基盤の admission control である。** IAM/RBAC/allow policy は誰が何を作れるかを決め、quota は作成可能な上限を決め、billing/cost allocation は責任者を決め、audit log は変更事実の検証可能性を決める。
6. **managed services は「便利な外注」ではなく、共有責任モデルの変更である。** AWS の shared responsibility model と Well-Architected の managed services 原則は、クラウド事業者が host OS・virtualization layer・facility 等を管理することで運用負荷を下げる一方、顧客側の設定・権限・データ・ネットワーク責任は残ることを示す。
7. **重大障害は control plane、internal network、rollout safety、zone/region 依存から発生しやすい。** AWS US-EAST-1 2021 事象では内部ネットワークと foundational services の通信障害が広域影響を生み、Google Cloud 2025 GCE 事象では feature flag rollout と control plane backlog が複数サービスに影響した。Azure の incident guidance は、障害時に scope・SLO・BC/DR plan・failover cost/risk を評価してから対応すべきだとする。

この Clone Spec の推奨結論は、**基盤を「VMを立てる仕組み」ではなく、配置・隔離・容量・費用・証跡・例外をすべてコード化する platform control plane として設計すること**である。

---

## 2. Layer Normalization

### 2.1 Definition

仮想化・クラウド基盤レイヤーは、物理サーバー、ストレージ、ネットワーク、データセンター、権限、利用量、監査証跡を抽象化し、VM・仮想ネットワーク・リージョン/ゾーン・管理サービス・請求単位として提供・制御するレイヤーである。

### 2.2 Decision Object

「どの workload に、どの仮想計算資源・ネットワーク到達性・配置ドメイン・権限・費用責任・監査粒度を与えるか」

### 2.3 Decision Question

世界トップの主体は、hypervisor / VM / image / snapshot / live migration / region / AZ / VPC / subnet / route / gateway / security group / private endpoint / IAM / quota / billing / audit / managed services を、どの基準・制約・例外・承認・メトリクスで設計し、どう運用するのか。

### 2.4 Primary Owners

- Cloud platform architect / platform engineering lead
- Infrastructure SRE / cloud operations lead
- Network architect
- Security architect / IAM owner
- FinOps owner
- Compliance / audit owner
- Application owner / workload owner
- Enterprise architecture / architecture review board

### 2.5 Default Artifacts

- Landing zone / account-subscription-project hierarchy
- Region and AZ placement policy
- VPC/VNet/VPC network baseline
- IPAM / CIDR allocation plan
- Route table / gateway / NAT / private endpoint design
- IAM/RBAC/service account policy baseline
- VM instance sizing standard and image lifecycle standard
- Snapshot / backup / restore / DR runbook
- Quota management register
- Cost allocation tag / label taxonomy
- Audit logging and retention policy
- Managed-service adoption decision record
- IaC modules and policy-as-code rules
- Exception register and risk acceptance record

---

## 3. Layer Registry: 19 Proposed Breakdown

The user supplied a layer range rather than individual layer labels. The following registry assigns concrete sublayer semantics to the range while keeping the requested title unit as one Clone Spec.

| Layer ID | Proposed sublayer | Decision object | Typical artifacts | Default metrics |
|---:|---|---|---|---|
| 19.01 | Hypervisor / VMM | 物理資源をどう分割・隔離するか | hypervisor standard、host class、maintenance policy | host utilization、VM density、escape/isolation findings |
| 19.02 | VM lifecycle | VMをいつ作成・停止・削除・置換するか | VM lifecycle policy、golden path | orphan VM count、mean provisioning time |
| 19.03 | vCPU sizing | CPU capacityをどう割り当てるか | instance type matrix、reservation/limit rules | CPU saturation、ready/steal time、rightsizing rate |
| 19.04 | vMemory sizing | memory capacityをどう割り当てるか | memory class matrix、OOM handling | memory saturation、swap/OOM incidents |
| 19.05 | vDisk / block storage | boot/data diskをどう構成するか | disk tier policy、IOPS/throughput matrix | disk latency、IOPS utilization、snapshot coverage |
| 19.06 | vNIC / network interface | VM network attachmentをどう管理するか | ENI/NIC policy、IP assignment plan | public NIC count、NIC quota utilization |
| 19.07 | VM image | OS・agent・hardening状態をどう標準化するか | image catalog、deprecation calendar | image age、CVE exposure、failed boot rate |
| 19.08 | Snapshot / restore | point-in-time stateをどう保存・復元するか | snapshot schedule、restore drill | RPO/RTO、restore success、snapshot age |
| 19.09 | Live migration / host maintenance | host maintenanceをどう無停止化/縮退化するか | maintenance policy、host-event handling | disruption time、maintenance incidents |
| 19.10 | Region selection | 地理・法域・latency・service availabilityをどう選ぶか | region matrix、data residency decision | regional latency、region concentration risk |
| 19.11 | Availability Zone / zone | 障害ドメインをどう分離するか | multi-zone deployment policy | zonal redundancy coverage、single-AZ workloads |
| 19.12 | VPC / VNet / VPC network | trust boundaryをどう作るか | network topology、VPC module | VPC sprawl、shared/private/public segments |
| 19.13 | Subnet / IPAM | IP rangesとtiersをどう分割するか | CIDR plan、subnet taxonomy | IP utilization、CIDR conflict count |
| 19.14 | Route | traffic pathをどう決めるか | route tables、route review | unintended route findings、blackhole events |
| 19.15 | Internet gateway / public ingress | internet到達性をどう制御するか | ingress policy、public IP exceptions | public IP count、internet-exposed assets |
| 19.16 | NAT / egress gateway | private subnetからのegressをどう制御するか | egress policy、NAT per AZ design | egress cost、NAT saturation、cross-AZ egress |
| 19.17 | Security group / firewall / NSG | L3/L4許可をどう最小化するか | SG/NSG/firewall rule baseline | high-risk rules、unused rules、denies/flows |
| 19.18 | Private endpoint | managed services接続をどうprivate化するか | PrivateLink/PSC/Private Endpoint catalog | public API traffic reduction、endpoint coverage |
| 19.19 | Cloud IAM / RBAC | human/machine accessをどう認可するか | role catalog、policy baseline | admin principal count、least-privilege findings |
| 19.20 | Service accounts / managed identities | workload identityをどう発行するか | service account lifecycle | keyless identity ratio、stale identity count |
| 19.21 | Quota / service limits | 作成上限をどう管理するか | quota register、increase workflow | quota utilization、blocked deployments |
| 19.22 | Billing / FinOps | 使用量と責任者をどう対応付けるか | tag taxonomy、budget alerts | untagged spend、budget variance、unit cost |
| 19.23 | Audit / activity log | 変更証跡をどう保存・照合するか | audit log policy、retention/export | audit coverage、log delivery lag、alert MTTA |
| 19.24 | Managed services | 何を事業者運用に任せるか | managed-service ADR | toil reduction、SLA fit、lock-in risk |
| 19.25 | Control plane / data plane | API制御と実トラフィックをどう分離するか | control-plane dependency map | control-plane latency、data-plane independence |
| 19.26 | HA / DR | zonal/regional failureをどう許容するか | DR plan、failover playbook | RTO/RPO、failover drill pass rate |
| 19.27 | Capacity planning | capacity・reservation・burstをどう確保するか | capacity forecast、reservation plan | capacity headroom、provisioning failures |
| 19.28 | Governance / policy-as-code | 設計ルールをどう強制するか | policy-as-code、landing-zone guardrails | policy violation rate、exception aging |
| 19.29 | Resource organization / tagging | ownershipをどう表現するか | account/project hierarchy、tags/labels | owner coverage、orphaned resource count |
| 19.30 | Data protection / encryption boundary | data-at-rest/in-transit/key責任をどう分けるか | key management policy、encryption baseline | encryption coverage、key rotation exceptions |
| 19.31 | Service health / incident response | provider障害にどう反応するか | service health alerts、incident playbook | detection time、decision time、DR trigger accuracy |

---

## 4. Frontier Exemplars and Scoring

Weights: Performance 25 / Adoption 15 / Artifact Richness 20 / Peer Validation 15 / Recency 10 / Transferability 10 / Failure Evidence 5. Scores are normalized to 100. This is a research scoring, not a vendor ranking.

| Candidate | Score | Why it is frontier-relevant | Strong evidence families | Caveat |
|---|---:|---|---|---|
| AWS EC2 / VPC / IAM / Well-Architected | 93 | EC2・VPC・IAM・CloudTrail・Service Quotas・Billing・PrivateLink・Well-Architected が、VM・network・identity・cost・audit を公式成果物として広く公開している。 | S03–S19 | AWS固有の nomenclature が強い。multi-cloud移植時は抽象化が必要。 |
| Google Cloud Compute Engine / VPC / IAM / Architecture Framework | 90 | live migration、regions/zones、Private Service Connect、Cloud Audit Logs、Architecture Framework、incident report が運用判断と失敗条件をよく示す。 | S22–S30 | live migration の可否は VM type / accelerator / confidential / local SSD 等の制約に依存する。 |
| Microsoft Azure VM / VNet / RBAC / Cost / Service Health | 88 | enterprise governance、RBAC、managed identities、Private Link、Activity Log、Cost Management、availability zone / incident response guidance が豊富。 | S31–S44 | subscription / tenant / management group の設計が前提化される。 |
| VMware vSphere / ESXi / vMotion | 80 | private cloud virtualization の古典的 frontier。snapshot、vMotion、resource allocation、hypervisor operations の公開資料が厚い。 | S45–S47 | public cloudのIAM/FinOps/private endpoint等とは異なる抽象化。 |
| OpenStack Nova / Neutron | 76 | compute / network API、hypervisor choice、network/subnet/router/security group、quota、live migration をOSS運用として観測できる。 | S48–S51 | managed-service / hyperscale region / provider audit の側面は弱い。 |
| NIST SP 800-145 / 800-125 | 92 as standards baseline | cloud definition と full virtualization security の語彙・責任境界の基礎。 | S01–S02 | 実装詳細や最新cloud provider featureまでは含まない。 |

---

## 5. Evidence Map

Confidence scale: A = direct official evidence; B = multiple official/independent evidence families; C = reasonable inference; D = hypothesis; X = rejected.

| Claim ID | Claim | Decision field | Confidence | Evidence refs |
|---|---|---|---|---|
| C01 | Cloud computing should be treated as on-demand access to shared, configurable resources that are rapidly provisioned and measured. | definition / philosophy | A | S01 |
| C02 | Full virtualization depends on a hypervisor / VMM that controls instruction flow and abstracts CPU, storage, memory, and network interfaces for guest OSs. | technical spec | A | S02 |
| C03 | VM size / instance type selection is a workload-fit decision across CPU, memory, storage, and networking capacity. | criteria / thresholds | A | S03, S28, S31 |
| C04 | A VM image / AMI / machine image is the reproducible boot/configuration artifact for instance creation, and should have lifecycle controls. | artifacts / controls | A | S04, S28 |
| C05 | Cloud block snapshots are point-in-time copies/backups, often incremental or disk-specific, but they do not replace a tested backup/restore program. | controls / failure_modes | A/B | S05, S28, S46 |
| C06 | Long-running VM snapshots can harm stability/performance and should not be treated as backup in vSphere-like environments. | anti-pattern | A | S46 |
| C07 | Live migration reduces disruption during host maintenance, but support is conditional; accelerators, bare metal, confidential VMs, HPC/RDMA, local SSD, or policy settings can change behavior. | exceptions | A | S23, S45, S50 |
| C08 | Regions and AZs/zones are placement and failure-domain constructs; resilient systems distribute resources across zones/regions. | criteria / resilience | A/B | S07, S22, S32, S33 |
| C09 | VPC/VNet/VPC network is a logical network boundary with subnets, routes, gateways, and firewall/security controls. | technical spec | A | S08, S34, S49 |
| C10 | Route tables/routes are explicit traffic-direction controls and must be reviewed as security and availability artifacts. | controls | A | S09, S35, S49 |
| C11 | NAT gateways enable outbound connectivity from private resources while blocking unsolicited inbound connections; single-AZ NAT dependency is a resilience risk. | controls / failure_modes | A | S11, S37 |
| C12 | PrivateLink / Private Service Connect / Azure Private Link reduce public internet exposure by creating private service connectivity. | controls | A/B | S12, S26, S38 |
| C13 | Security groups / NSGs / firewall rules are cloud-native L3/L4 policy objects and must be least-permissive, observable, and scoped. | prohibitions / controls | A/B | S08, S27, S36 |
| C14 | IAM/RBAC/allow policies attach permissions to identities/resources and should enforce least privilege, temporary or managed identities, and separation of duties. | owners / controls | A/B | S13, S14, S24, S39, S40 |
| C15 | Quotas/service limits are per-account/project/subscription and often region-specific; deployment workflows must preflight them. | thresholds | A/B | S15, S43, S51 |
| C16 | Billing/cost management requires tags/labels/categories/budgets to map resource usage to owners and business units. | metrics / controls | A/B | S16, S42 |
| C17 | Cloud audit logs record management/API/resource access activities and answer who did what, where, and when. | audit / evidence | A/B | S17, S25, S41 |
| C18 | Managed services reduce operational burden, but the shared responsibility model means customer-side configuration, IAM, network, and data duties remain. | philosophy / tradeoff | A/B | S18, S19, S29 |
| C19 | Provider control-plane failures can propagate through internal networks, service dependencies, rollout safety gaps, or capacity backlogs. | failure_mode | A/B | S20, S30 |
| C20 | Incident response should be driven by scope, SLO, business continuity priority, and planned DR actions; rushed failover can increase risk. | operating_model | A | S44 |

---

## 6. Core Philosophy

### 6.1 Abstraction is not invisibility

Cloud abstraction hides rack/host details, but it does not remove the need to reason about capacity, placement, fault domains, network paths, identity, and cost. The strongest operators expose just enough of those controls to application teams through reusable modules and policies.

### 6.2 Every resource must have five boundaries

A production resource should have explicit boundaries for:

1. **Location**: region, zone, data residency.
2. **Network reachability**: VPC/subnet/routes/gateways/private endpoints/security groups.
3. **Identity**: human and workload principals, roles, permission scope, credential lifecycle.
4. **Economic accountability**: tag/label, cost center, budget, forecast, quota owner.
5. **Evidence**: audit logs, config history, deployment record, exception record.

### 6.3 Provider-managed does not mean risk-free

Managed services reduce operational toil, but they also introduce provider control-plane dependencies, regional availability constraints, service-specific quotas, pricing effects, and shared responsibility ambiguity. A managed-service decision should be made with an explicit ADR, not by default.

### 6.4 Design for control-plane degradation

A platform can keep running while creation, deletion, failover, quota increase, or IAM updates are delayed. Critical workloads must distinguish data-plane availability from control-plane availability and test both.

### 6.5 Default private, explicit public

Public ingress and public service endpoints are exceptions. The default posture is private subnet, no direct public IP, private service connectivity, explicit egress, and audited inbound/outbound rules.

---

## 7. Decision Model

### 7.1 Inputs

- Workload class: stateless web, stateful database, batch, HPC, AI/accelerator, regulated workload, legacy OS, licensed software.
- SLO/SLA expectations: availability, latency, throughput, RTO, RPO, maintenance window tolerance.
- Data constraints: residency, sovereignty, encryption/key ownership, backup retention, deletion requirements.
- Operating constraints: team maturity, on-call capacity, automation level, existing IaC, patching model.
- Demand profile: steady, bursty, seasonal, unpredictable, reservation needs, capacity commitments.
- Security posture: trust zones, internet exposure, lateral movement risk, privileged access model.
- Network topology: on-premises connectivity, east-west traffic, service endpoints, egress requirements.
- Governance signals: budget, cost center, owner, quota headroom, compliance evidence.
- Provider constraints: regional service availability, quotas, local/AZ mapping, maintenance policies, live migration limitations.

### 7.2 Criteria

1. **Workload fit over generic standardization**: select VM size/storage/network by observed bottleneck and SLO, not by one-size instance class.
2. **Fault-domain isolation over nominal availability**: a workload is not resilient merely because a provider is resilient; it must use zones/regions and test failure paths.
3. **Least reachability over simple connectivity**: every public route, public IP, and broad firewall rule must have a business reason.
4. **Least privilege over admin convenience**: access must be scoped to role, resource, duration, and workload identity.
5. **Measurability over assumption**: capacity, quota, cost, audit, and recovery must be instrumented.
6. **Managed-service adoption over undifferentiated operations** when service features, compliance, lock-in, quota, and cost fit the workload.
7. **Reproducibility over artisanal servers**: VM image, IaC, bootstrapping, snapshot, and restore procedures must be repeatable.

### 7.3 Priorities

1. Safety: isolation, least privilege, auditability.
2. Availability: multi-zone/region design and tested recovery.
3. Operability: standard modules, logs, monitoring, quota and cost alerts.
4. Performance: right-size compute/storage/network for workload.
5. Cost efficiency: idle elimination, reservation/commitment planning, unit economics.
6. Developer productivity: self-service within guardrails.
7. Portability: abstractions that avoid unnecessary provider-specific coupling.

### 7.4 Prohibitions

- No production VM without owner, environment, data-classification, and cost tags/labels.
- No internet-exposed VM NIC unless explicitly approved; internet ingress should terminate at a controlled entry point.
- No broad `0.0.0.0/0` inbound admin access.
- No long-lived human keys as default cloud access path.
- No workload using a single AZ/zone when its stated SLO requires zonal fault tolerance.
- No unmanaged route or NAT change outside IaC/change record.
- No snapshot-only backup strategy for critical state.
- No quota increase request after deployment is already blocked; quota should be preflighted.
- No managed service adoption without shared responsibility and exit/rollback analysis.
- No DR failover without trigger criteria and rollback criteria.

### 7.5 Thresholds and Guardrails

| Area | Recommended threshold / rule | Rationale |
|---|---|---|
| Quota | Alert at 60%; deployment block or approval at 80%; urgent review at 90%. | Most quota failures appear at provisioning time; preflight avoids emergency increases. |
| Budget | Alert at 50/80/100% of monthly budget and at anomaly detection. | Billing is a control plane signal, not a finance-only report. |
| Public exposure | Public IP count and public ingress rules must be zero by default; exceptions expire. | Reduces attack surface and orphan exposure. |
| NAT | For multi-AZ private workloads requiring internet egress, use NAT/gateway resilience per failure domain where provider architecture requires it. | Avoid single egress dependency and cross-AZ blast radius. |
| Image age | Base images older than 30–90 days require rebuild or risk exception depending on patch criticality. | Reduces drift and unpatched boot artifacts. |
| Snapshot restore | Restore drills at least quarterly for critical systems; backup without restore evidence is incomplete. | Confirms RPO/RTO rather than assuming them. |
| IAM review | Privileged roles reviewed monthly; non-human identities reviewed at least quarterly. | Permissions drift quickly in cloud environments. |
| Audit retention | Minimum retention aligned to regulation and incident response; security-critical logs exported to immutable or restricted store. | Local project/account deletion must not delete evidence. |
| DR test | At least annual full test; higher cadence for Tier 0/Tier 1 workloads. | Failover mechanics age as systems change. |

### 7.6 Owners and Reviewers

| Decision | Primary owner | Required reviewers |
|---|---|---|
| Region/AZ placement | Application owner + platform architect | SRE, security, compliance, FinOps |
| VPC/subnet/CIDR | Network architect | Security, platform, app owner |
| Route/gateway/NAT | Network architect | SRE, security, cost owner |
| Security group/firewall | Security architect + service owner | Network, SRE |
| IAM/RBAC/service account | IAM owner | Security, app owner, audit |
| VM image standard | Platform engineering | Security, endpoint/OS owner |
| Snapshot/backup/restore | SRE + app owner | Compliance, security |
| Managed-service adoption | App owner + platform architect | Security, data owner, FinOps, procurement/legal if needed |
| Quota increase | Platform operations | App owner, FinOps |
| Billing taxonomy | FinOps owner | Platform, business owner |
| Audit policy | Security/audit owner | Platform, compliance |

### 7.7 Cadence

- Architecture review: new production workload and every major topology change.
- IAM review: monthly for privileged roles; quarterly for all service accounts/managed identities.
- Network exposure review: continuous scanning plus monthly exception review.
- Quota/capacity review: monthly, and before launches/campaigns/migrations.
- Cost review: weekly for anomalies; monthly for allocation and commitments.
- Image refresh: monthly or aligned to patch release cycles.
- Backup/restore drill: quarterly for critical workloads.
- DR game day: semiannual or annual depending on tier.
- Managed-service review: annually or before material price/functionality/compliance changes.

---

## 8. Operating Model

### 8.1 Roles

| Role | Responsibilities |
|---|---|
| Cloud platform team | landing zone, IaC modules, image pipeline, quota dashboards, network baseline, self-service guardrails |
| Network team | IPAM, VPC/VNet/VPC network topology, routing, NAT, private endpoints, firewall policy |
| Security/IAM team | identity federation, RBAC/IAM policy, service accounts, security groups, audit log controls |
| SRE / operations | SLO, capacity, health alerts, incident response, backup/restore, DR drills |
| FinOps | tag taxonomy, budgets, cost allocation, commitment planning, unit economics |
| App owner | workload SLO, data classification, region selection input, runtime ownership, exception acceptance |
| Compliance/audit | retention, evidence quality, regulatory constraints, periodic attestation |
| Architecture review board | cross-domain decisions, exceptions, pattern library maintenance |

### 8.2 Process

1. **Workload intake**: capture SLO, data class, region needs, expected scale, security posture, budget, owner.
2. **Placement decision**: choose account/subscription/project, region, zone strategy, managed/self-managed service boundary.
3. **Network admission**: allocate CIDR/subnet, route, ingress/egress gateway, private endpoint needs, firewall/security group baseline.
4. **Identity admission**: create human access path, service identity, role assignment, conditional controls, break-glass path.
5. **Compute admission**: select VM/machine family, image, boot disk, data disks, NICs, placement group/host/sole tenancy if needed.
6. **Resilience admission**: define backup/snapshot/restore, live migration policy, multi-zone/region, RTO/RPO, failover runbook.
7. **Economic admission**: attach tags/labels, budget, quota owner, unit-cost model, commitment/reservation plan.
8. **Audit admission**: enable management/data/network logs, export destination, retention, alerting, evidence mapping.
9. **Launch review**: verify IaC, policy-as-code, quota preflight, smoke test, rollback plan.
10. **Continuous operation**: observe metrics, cost, audit, quota, drift; feed incidents into pattern library.

### 8.3 Meeting / Review Bodies

- Weekly platform operations review: quotas, policy violations, blocked deployments, provider health.
- Weekly FinOps cost anomaly review: untagged spend, idle resources, reservation/commitment gaps.
- Monthly cloud security review: public exposure, IAM drift, service-account keys, audit gaps.
- Monthly architecture exception board: expired exceptions, region/service constraints, managed-service risks.
- Quarterly resilience review: restore tests, DR drills, SLO misses, zonal/regional concentration.

### 8.4 Tooling Stack

- IaC: Terraform / OpenTofu / CloudFormation / ARM/Bicep / Deployment Manager alternatives.
- Policy-as-code: AWS Config/SCP/IAM Access Analyzer, Azure Policy, Google Org Policy, OPA/Conftest where applicable.
- Image pipeline: EC2 Image Builder, Azure VM Image Builder / Compute Gallery, Google image pipeline or image builder tooling.
- Network evidence: VPC Flow Logs / firewall logs / NSG flow logs where available.
- Audit evidence: CloudTrail, Cloud Audit Logs, Azure Activity Log and resource logs.
- Cost: AWS Cost Explorer/Budgets/CUR/Cost Categories, Microsoft Cost Management, Google Cloud Billing exports/budgets.
- Quota: AWS Service Quotas, Azure Quotas/subscription service limits, Google Cloud Quotas.
- Incident/health: AWS Health Dashboard/PES, Google Cloud Service Health, Azure Service Health / Status history.

---

## 9. Technical / Business Specification

### 9.1 Hypervisor and VM Compute Plane

**Decision rule:** choose the lowest-operational-burden compute primitive that satisfies OS, kernel, licensing, security, performance, accelerators, data locality, and SLO requirements.

| Situation | Preferred primitive | Notes |
|---|---|---|
| Legacy OS, special agent, custom kernel, licensed software | VM | Keep image and patching lifecycle explicit. |
| Predictable VM workload with special CPU/memory ratio | Provider VM / custom machine type where supported | Use rightsizing metrics and reservations/commitments. |
| Host-level compliance or license affinity | Dedicated host / sole-tenant node / placement control | Track capacity, live migration limits, cost premium. |
| Accelerator/HPC/RDMA workload | Specialized VM/bare metal/managed accelerator service | Expect live migration limitations; require checkpoint/restart or redundant fleet. |
| Commodity app needing minimal ops | Managed service/serverless/container platform | Use shared responsibility analysis and quota/cost review. |
| Private cloud / regulated on-prem environment | vSphere / OpenStack / private cloud | Must replicate cloud controls: IAM, quota, network policy, billing/showback, audit. |

Required compute-plane controls:

- Instance type / size must map to CPU, memory, disk, and network capacity.
- Production VMs must be launched from approved images or approved bootstrap pipelines.
- VM placement must record region, zone, subnet, IAM/service account, owner, cost tag, and data class.
- VM lifecycle must favor replacement over manual repair unless stateful constraints prevent replacement.
- Host maintenance behavior must be known. Live migration, terminate/restart, notice windows, and accelerator limitations must be documented.

### 9.2 vCPU / vMemory / vDisk / vNIC

| Resource | Frontier decision | Operational control | Failure if ignored |
|---|---|---|---|
| vCPU | Match workload shape: general, compute-optimized, burstable, HPC, accelerator. | utilization SLO, headroom, rightsizing review, CPU credit/steal/ready where applicable | throttling, noisy-neighbor sensitivity, overcommit, cost waste |
| vMemory | Match memory density and OOM tolerance. | memory saturation alarms, crash/OOM tracking, memory-optimized class review | swapping, OOM kills, instance instability |
| vDisk | Separate boot/data disks; choose disk type by latency/IOPS/throughput/durability. | disk latency alarms, throughput caps, snapshot/backup schedule | data loss, slow I/O, failed restore, cost overrun |
| vNIC | Treat NIC as network identity and policy attachment, not only interface. | subnet binding, SG/firewall attachment, public IP exception, NIC quota monitor | lateral movement, public exposure, IP exhaustion, failed provisioning |

### 9.3 VM Image and Snapshot Lifecycle

VM images are the standard boot artifacts. They should contain OS baseline, hardening, agents, patch level, logging/monitoring hooks, bootstrapping contract, and deprecation date.

Snapshot controls:

- Use snapshots for point-in-time disk state and short-term recovery, not as the only backup strategy for critical workloads.
- Test restore, not just snapshot creation.
- Separate crash-consistent, application-consistent, and multi-disk consistency requirements.
- Do not keep VM snapshots indefinitely in vSphere-like environments; long-running snapshots can affect stability/performance.
- For cross-region DR, validate whether snapshots/images are regional/global and how copy/replication works.

### 9.4 Live Migration and Host Maintenance

Live migration is a maintenance continuity mechanism, not a universal availability guarantee. Google Cloud documents live migration for maintenance and lists unsupported cases such as bare metal, many confidential VM cases, GPUs, TPUs, and certain storage/HPC-optimized cases. VMware vMotion and OpenStack live migration likewise require compatibility, network/storage readiness, and operational constraints.

Required design response:

- If live migration is supported: set host maintenance policy, observe events, and still design application-level redundancy for blackouts/performance degradation.
- If live migration is unsupported: use checkpoint/restart, redundant replicas, zone spread, queue draining, or maintenance windows.
- For accelerator/HPC workloads: assume migration can be disruptive unless official support says otherwise.
- For critical systems: distinguish host maintenance continuity from region/AZ failure tolerance.

### 9.5 Region and Availability Zone Strategy

Selection criteria:

1. Data residency and legal jurisdiction.
2. Latency to users and upstream/downstream services.
3. Availability of required managed services, machine families, accelerators, and private connectivity.
4. Resilience model: single-zone, multi-zone, multi-region, active/passive, active/active.
5. Cost and capacity availability.
6. Operational familiarity and support coverage.

Placement rules:

- Tier 0/Tier 1 workloads should not rely on a single zone unless explicitly risk-accepted.
- Zone IDs / physical-zone mappings can differ by provider and account/subscription context; avoid assuming that logical zone labels map to identical physical sites across accounts.
- For multi-region DR, define data replication, DNS/traffic failover, consistency model, RTO/RPO, and rollback.
- Provider-wide dependencies such as IAM, DNS, billing, or control-plane APIs must be mapped separately from workload region placement.

### 9.6 VPC / Subnet / Route / Gateway Design

Recommended baseline topology:

| Segment | Purpose | Internet ingress | Internet egress | Notes |
|---|---|---:|---:|---|
| Public edge subnet | load balancer, edge proxy, bastion/zero-trust connector if used | controlled | controlled | No application servers by default. |
| Private app subnet | application VMs/services | no direct | via NAT or private endpoints | Default placement for workloads. |
| Isolated data subnet | databases/stateful internal systems | no | usually no direct; private service only | Strongest route restrictions. |
| Endpoint subnet | private endpoints / PrivateLink / PSC | no | private backbone | Separates service connectivity from workload compute. |
| Management subnet | monitoring, patching, admin plane | no direct | constrained | Requires strict IAM and audit. |

Route/gateway rules:

- Route tables are security artifacts. Review them with the same rigor as firewall rules.
- Internet gateway/public route should only exist where workloads require public ingress/egress.
- NAT gateway is for outbound access from private subnets; it should not be used as a substitute for private endpoints when managed-service traffic can stay private.
- For AWS-style zonal NAT designs, create NAT gateways per AZ or equivalent resilient egress pattern where multi-AZ private workloads rely on internet egress.
- Private endpoints should be the default for high-sensitivity workloads connecting to provider-managed services.

### 9.7 Security Groups / Firewalls / NSGs

Rules:

- Default deny inbound. Allow only required ports/protocols/sources.
- Prefer identity/application-level controls in addition to L3/L4 controls.
- Use security group references, service tags, or managed identities where provider supports them rather than broad CIDR ranges.
- Remove unused rules; assign rule owners and expiry dates.
- Do not use broad inbound admin rules; use session manager, bastion, just-in-time access, or zero-trust access path.
- Capture flow/firewall logs where useful for detection and policy tuning.

### 9.8 Private Endpoints

Private endpoints solve a specific problem: private, scoped connectivity to managed services or partner/customer services without exposing traffic to the public internet.

Adoption criteria:

- Data sensitivity or compliance requires no public service endpoint.
- Workload resides in private subnet and uses provider-managed services.
- Egress policy must restrict reachable services.
- Cross-account/project/subscription service consumption needs explicit approval.
- Cost, DNS, IP consumption, quota, and operational ownership are understood.

Known complexity:

- DNS split-horizon and endpoint-specific names.
- Endpoint subnet/IP exhaustion.
- Service-specific region support.
- Cross-tenant/account approval workflows.
- Monitoring and logging coverage.

### 9.9 Cloud IAM / RBAC / Managed Identities

IAM operating principles:

- Use federated human identity and temporary credentials where possible.
- Prefer roles/managed identities/service accounts over long-lived keys.
- Separate human admin, CI/CD deployer, runtime workload, and break-glass identities.
- Attach permissions at the narrowest workable scope.
- Use deny/organization policies/SCP/Azure Policy/Org Policy to prevent classes of bad actions.
- Review privileged access and unused permissions continuously.
- Record every role assignment as auditable infrastructure state.

### 9.10 Quota

Quota is a design constraint and operational risk signal.

Required mechanisms:

- Maintain a quota register for critical services: vCPU, VM instances, disks, snapshots, IPs, NICs, routes, private endpoints, NAT gateways, IAM objects, logs, API rate limits.
- Preflight quotas during CI/CD plan/apply and before launch events.
- Alert on quota utilization thresholds.
- Treat quota increase as an approval workflow with business reason, region, workload owner, expiry/review date if temporary.
- Include quota exhaustion in game days.

### 9.11 Billing / FinOps

Every cloud resource must be accountable. Minimum taxonomy:

- owner
- business unit / cost center
- product / service
- environment
- data classification
- compliance scope
- lifecycle / expiry
- workload tier

FinOps controls:

- Budgets and anomaly detection.
- Cost allocation tags/labels/categories.
- Unit-cost metrics for major products.
- Idle/orphan resource cleanup.
- Reserved/committed-use planning.
- Showback/chargeback where appropriate.
- Cost review before managed-service adoption and region selection.

### 9.12 Audit

Audit logs must be enabled before production launch. Minimum evidence questions:

- Who created/modified/deleted the resource?
- Which principal assumed which role?
- Which API/action was invoked?
- Which network/security/IAM route changed?
- Was the action allowed or denied?
- Where is the log retained if the project/account is compromised or deleted?

Audit baseline:

- Management/control-plane logs always on.
- Data-plane logs enabled for sensitive stores and critical services.
- Network/security logs enabled for exposed segments.
- Export to central, access-restricted logging account/project/subscription.
- Immutable or retention-locked store for regulated workloads.
- Alerts for high-risk events: public exposure, IAM admin grant, route/gateway changes, audit disablement, key creation, quota exhaustion, budget anomaly.

### 9.13 Managed Services

Managed-service adoption decision:

| Question | Adopt managed service if yes | Prefer self-managed / VM if yes |
|---|---|---|
| Does the service meet SLO/RTO/RPO? | Provider SLA and architecture fit. | Service lacks required resilience or regional support. |
| Does it reduce undifferentiated operations? | Patching, scaling, backup, failover are materially simplified. | Team needs kernel/OS/database internals or special plugins. |
| Is responsibility clear? | Shared responsibility and controls are documented. | Ambiguous data/security/network responsibility. |
| Is cost predictable? | Cost model matches workload and budget alerts exist. | Cost spikes are hard to bound. |
| Is exit/rollback possible? | Data export, backup, migration, or dual-run path exists. | Lock-in risk exceeds value. |
| Are quotas and private endpoints supported? | Private connectivity and quota plan exist. | Public endpoint or quota constraints violate policy. |

---

## 10. Metrics

| Metric | Type | Target use |
|---|---|---|
| Provisioning success rate | Reliability | Detect capacity/quota/control-plane issues. |
| VM launch P50/P95/P99 latency | Reliability / operations | Identify provisioning degradation. |
| Quota utilization by service/region | Capacity | Avoid blocked launches. |
| Single-AZ workload count | Resilience | Reduce concentration risk. |
| Public IP / public ingress count | Security | Reduce attack surface. |
| High-risk SG/NSG/firewall rules | Security | Detect broad exposure. |
| Private endpoint coverage for sensitive services | Security / compliance | Reduce public service traffic. |
| IAM admin principal count | Security | Reduce privilege concentration. |
| Service-account key age / keyless identity ratio | Security | Remove long-lived credentials. |
| Audit log coverage and delivery lag | Compliance | Ensure evidence completeness. |
| Untagged / unallocated spend | FinOps | Improve accountability. |
| Budget variance and anomaly count | FinOps | Detect waste or abuse. |
| Image age and image CVE exposure | Security / operations | Keep boot artifacts current. |
| Backup restore success rate | Resilience | Confirm actual recoverability. |
| RTO/RPO drill result | Resilience | Validate business continuity. |
| Policy-as-code violation rate | Governance | Measure guardrail effectiveness. |
| Exception aging | Governance | Prevent permanent exceptions. |
| Provider incident impact count | Vendor risk | Track dependency exposure. |

---

## 11. Failure Modes

| Failure mode | Mechanism | Prevention / mitigation |
|---|---|---|
| Control-plane dependency outage | API creation/deletion/IAM/quota operations degrade while existing data plane may continue. | Distinguish control/data plane in SLO; pre-provision capacity; avoid emergency scaling dependence. |
| Internal network coupling | Provider internal services such as DNS, authorization, monitoring, or control plane share dependency paths. | Multi-region design; service-health alerts; resilient app-level retries; avoid single-region critical dependencies. |
| Unsafe rollout / feature flag blast radius | Rapid global rollout or failed safety check overloads service operations. | Watch provider incident feeds; design for regional isolation; avoid all workloads relying on one service path. |
| Single-AZ workload | Workload pinned to one zone fails on zone incident. | Multi-zone deployment, zone-redundant services, failover runbooks. |
| Single NAT/egress gateway | Private workloads in multiple zones depend on one egress path. | Per-failure-domain NAT or resilient egress; prefer private endpoints for managed services. |
| Route table drift | Unreviewed route exposes private subnet or blackholes traffic. | IaC-only route changes, route diff review, policy-as-code. |
| Broad security group rule | `0.0.0.0/0` or overly broad east-west access enables compromise/lateral movement. | Least-permissive rules, expiry, flow analysis, security review. |
| Public endpoint sprawl | Managed service accessed via public endpoints despite private network intent. | Private endpoint catalog, DNS controls, egress allowlists. |
| IAM privilege creep | Accumulated roles and long-lived keys create high blast radius. | Temporary credentials, IAM reviews, permission analysis, break-glass isolation. |
| Quota exhaustion | Deployment fails when vCPU/IP/NIC/disk/endpoint/API limits are reached. | Quota preflight, monitoring, increase workflow. |
| Snapshot false confidence | Snapshots exist but restore fails or data is inconsistent. | Restore drills, application-consistent backups, multi-disk consistency. |
| Long-running VM snapshots | Snapshot chains cause performance/stability risk. | Snapshot TTL, backup tooling, snapshot inventory alerts. |
| Managed-service lock-in surprise | Service cannot meet cost/compliance/migration requirements later. | ADR, exit plan, export/backup validation, architecture review. |
| Billing blind spots | Untagged resources and shared accounts hide cost ownership. | Tag policy, budgets, cost categories, cleanup workflow. |
| Audit gap | Logs disabled, local-only, or deleted during incident. | Central export, retention lock, alert on log disablement. |
| Rushed failover | DR invoked without scope/risk analysis causing data loss or longer outage. | Trigger criteria, SLO-based decision, tested runbooks. |

---

## 12. Anti-patterns

- Treating cloud as cheaper VMware without IAM, quota, billing, and audit controls.
- Building a flat VPC where every subnet can reach every other subnet.
- Putting application servers directly in public subnets with public IPs.
- Using NAT for all managed-service traffic instead of private endpoints.
- Treating region selection as only a latency decision and ignoring service availability, data residency, and DR topology.
- Assuming logical AZ names map to the same physical site across accounts/subscriptions.
- Relying on provider live migration instead of application-level redundancy.
- Using snapshots as the only backup and never testing restore.
- Allowing manual console changes without IaC reconciliation.
- Granting admin roles to CI/CD or runtime workloads.
- Ignoring quota until deployment day.
- Running unmanaged images for months without rebuild.
- Adopting managed services without knowing who owns backup, encryption, network exposure, patching, and incident response.
- Treating cost allocation as finance reporting rather than platform design.
- Storing audit logs in the same account/project/subscription with broad admins and no retention controls.

---

## 13. Maturity Model

| Level | Name | Criteria |
|---:|---|---|
| 0 | Unmanaged VM sprawl | Manual VM creation, no standard images, no network segmentation, no cost owner, no audit baseline. |
| 1 | Basic documented cloud use | VPC/subnet/IAM basics documented, but exceptions are informal and many resources are hand-built. |
| 2 | Standardized landing zone | Account/project/subscription hierarchy, baseline VPC, IAM roles, tags, CloudTrail/Audit/Activity logs, quotas documented. |
| 3 | IaC-driven multi-zone platform | Production workloads deployed by IaC, multi-zone patterns available, approved images, private endpoint patterns, budget alerts. |
| 4 | Automated guardrails and evidence | Policy-as-code blocks unsafe designs, quota/cost/security/audit dashboards, restore/DR drills, image pipelines, automated remediation. |
| 5 | Adaptive frontier platform | Control/data-plane risk modeled, provider incident learnings integrated, self-service with evidence, continuous rightsizing/FinOps, chaos/game-day validation, managed-service portfolio governance. |

---

## 14. Clone Implementation Guide

### Phase 0: Baseline inventory, 1–2 weeks

Deliverables:

- Resource inventory across accounts/subscriptions/projects.
- Current public exposure list.
- Current IAM privileged principal list.
- Untagged/unowned resource list.
- Quota utilization snapshot.
- Current audit logging coverage.
- Current backup/snapshot inventory and restore evidence.

Exit criteria:

- Every production resource has at least an owner and environment classification or is marked orphaned.
- Unknown public ingress and unknown admin access are visible.

### Phase 1: Landing-zone and ownership model, 2–4 weeks

Deliverables:

- Account/subscription/project hierarchy.
- Standard tags/labels.
- IAM/RBAC role catalog.
- Central audit log destination.
- Budget and anomaly alerts.
- Quota register.

Exit criteria:

- New workloads cannot launch without owner, environment, cost center, data class, and audit destination.

### Phase 2: Network baseline, 3–6 weeks

Deliverables:

- CIDR/IPAM plan.
- Public/private/isolated/endpoint subnet modules.
- Route table templates.
- NAT/egress pattern.
- Private endpoint catalog and DNS pattern.
- Security group/NSG/firewall rule standards.

Exit criteria:

- Production workloads use standard network modules.
- Public IP exceptions have owner, reason, and expiry.

### Phase 3: Compute, image, and recovery standard, 4–8 weeks

Deliverables:

- VM size/machine family decision matrix.
- Golden image pipeline.
- Image deprecation calendar.
- Snapshot policy.
- Backup/restore runbook.
- Host maintenance/live migration policy by workload class.

Exit criteria:

- New production VM launches from approved image or approved exception.
- Restore test is recorded for critical stateful workloads.

### Phase 4: IAM hardening and workload identity, 4–8 weeks

Deliverables:

- Human federation and temporary access path.
- Service account/managed identity lifecycle.
- Privileged role review workflow.
- Key rotation/keyless identity targets.
- Break-glass process.

Exit criteria:

- CI/CD and runtime workloads do not use broad human admin credentials.
- Privileged access is reviewed and logged.

### Phase 5: FinOps and quota automation, ongoing after week 6

Deliverables:

- Budget alerts by owner/product/environment.
- Cost allocation reports.
- Idle/orphan cleanup workflows.
- Reservation/commitment review.
- Quota preflight in deployment pipelines.

Exit criteria:

- Deployment failures from predictable quota exhaustion decrease.
- Untagged spend trends downward.

### Phase 6: Managed-service portfolio governance, ongoing

Deliverables:

- Managed-service adoption ADR template.
- Shared responsibility checklist.
- Exit/rollback plan template.
- Private endpoint and audit checklist.
- Cost model and quota model.

Exit criteria:

- Every managed-service adoption decision records responsibility, network exposure, auditability, cost, quota, and exit plan.

### Phase 7: Resilience game days and incident learning, ongoing

Deliverables:

- Zone failure game day.
- Region degradation tabletop.
- Control-plane API degradation scenario.
- Quota exhaustion scenario.
- Provider incident retrospective process.

Exit criteria:

- Lessons learned update IaC modules, policy-as-code, source catalog, and pattern library.

---

## 15. Pattern Library

| Pattern ID | Pattern | Type | Preconditions | Tradeoffs | Evidence refs | Confidence |
|---|---|---|---|---|---|---|
| P01 | Default-private VPC with explicit public edge | control | Workload supports private subnet and controlled ingress | Requires DNS/private endpoint design | S08, S09, S11, S12, S26, S27, S34, S35, S36, S38 | A |
| P02 | Multi-zone baseline for Tier 0/Tier 1 | reliability | Workload can replicate or run multiple instances | Higher cost/complexity | S07, S22, S32, S33, S44 | A |
| P03 | Golden image with deprecation clock | operating model | VM-based workloads exist | Requires image pipeline ownership | S04, S28 | A |
| P04 | Snapshot plus restore drill | resilience | Stateful disks | Drill cost and operational overhead | S05, S28, S46 | A |
| P05 | Private endpoint catalog | security | Managed services support private connectivity | DNS/IP/quota complexity | S12, S26, S38 | A |
| P06 | IAM role catalog + service identities | control | Federated identity or cloud IAM in place | Requires permission review process | S13, S14, S24, S39, S40 | A |
| P07 | Quota preflight | decision rule | Deployment pipeline has provider API access | Requires quota source integration | S15, S43, S51 | A |
| P08 | Cost tags as admission control | metric/control | Tag taxonomy exists | Users may resist launch blocking | S16, S42 | B |
| P09 | Control-plane degradation game day | failure pattern | SRE + platform teams can simulate or tabletop | Hard to reproduce provider outages directly | S20, S30, S44 | B |
| P10 | Managed-service ADR | operating model | Service alternatives exist | Slower adoption but lower hidden risk | S18, S19, S29 | B |

---

## 16. Validation Queries

Use these queries periodically to revalidate current docs, detect changes, and search for counterevidence.

```text
site:docs.aws.amazon.com EC2 instance types CPU memory storage networking after:2025-01-01
site:docs.aws.amazon.com VPC NAT gateway resiliency Availability Zone after:2025-01-01
site:docs.aws.amazon.com VPC PrivateLink endpoint internet gateway NAT device public IP after:2025-01-01
site:docs.aws.amazon.com IAM least privilege roles temporary credentials after:2025-01-01
site:docs.aws.amazon.com Service Quotas region-specific quota increase after:2025-01-01
site:docs.cloud.google.com Compute Engine live migration limitations GPU TPU confidential VM after:2025-01-01
site:status.cloud.google.com/incidents Google Compute Engine Incident Report VM creation termination reservation after:2025-01-01
site:learn.microsoft.com Azure Private Link private endpoint virtual network after:2025-01-01
site:learn.microsoft.com Azure availability zones region outage disaster recovery after:2025-01-01
site:aws.amazon.com/message OR site:aws.amazon.com/premiumsupport/technology/pes EC2 VPC IAM outage Post-Event Summary
"VMware vSphere snapshot" "not" "backup" site:knowledge.broadcom.com OR site:techdocs.broadcom.com
site:docs.openstack.org nova live migration hypervisor quotas neutron security groups
```

Counterevidence-specific queries:

```text
"AWS PrivateLink" limitations quota DNS private endpoint
"Azure Private Endpoint" DNS limitation quota cross region
"Private Service Connect" limitations IAM firewall DNS
"NAT gateway" outage "Availability Zone" "single point"
"cloud quota" deployment failed vCPU IP address private endpoint
"live migration" unsupported GPU TPU confidential VM local SSD
"cloud audit logs" disabled deleted retention incident
"cost allocation tags" untagged spend cloud incident
```

---

## 17. Confidence and Unknowns

### Confidence A

- Cloud and virtualization definitions from NIST.
- Provider VM/image/snapshot/VPC/IAM/quota/billing/audit docs.
- Region/AZ/zone concepts from AWS, Google Cloud, and Azure.
- Private connectivity concepts from AWS PrivateLink, Google Private Service Connect, and Azure Private Link.
- Public incident evidence for AWS 2021 and Google Cloud GCE 2025.

### Confidence B

- Cross-provider pattern synthesis: default-private network, IAM as admission control, quota preflight, cost tags as governance, managed-service ADR.
- Failure-mode generalization from official provider incident reports.

### Confidence C

- Concrete thresholds such as image age 30–90 days, quota alert thresholds, and review cadence. These are recommended operating heuristics derived from common practice and source patterns, not universal provider requirements.

### Unknowns

- Provider-internal hypervisor scheduling algorithms, capacity allocation, and internal live migration implementation details beyond public docs.
- Exact physical mapping between logical zones for a given customer unless provider-specific mapping APIs/docs are used.
- Customer-specific negotiated quotas, private SLA terms, support commitments, and enterprise agreement pricing.
- Non-public incident root causes and future provider roadmap.
- Workload-specific compliance constraints, licensing constraints, and RTO/RPO tradeoffs.

### Additional Research

- Add workload-specific overlays: regulated finance, healthcare, public sector, AI/HPC, SaaS multi-tenant, internal enterprise apps.
- Compare provider-specific landing-zone reference architectures.
- Add evidence from provider reference architectures and certification/audit reports if a regulated environment is targeted.
- Add cost model benchmark using actual usage data once available.

---

## 18. Source Catalog

| Source ID | Entity | Source title | Type | Tier | Key evidence | URL |
|---|---|---|---|---|---|---|
| S01 | NIST | SP 800-145: The NIST Definition of Cloud Computing | standard | T0 | cloud definition, essential characteristics | https://csrc.nist.gov/pubs/sp/800/145/final |
| S02 | NIST | SP 800-125: Guide to Security for Full Virtualization Technologies | standard | T0 | hypervisor/VMM, full virtualization security | https://csrc.nist.gov/pubs/sp/800/125/final |
| S03 | AWS | Amazon EC2 instance types | official_doc | T2 | CPU/memory/storage/network capacity combinations | https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-types.html |
| S04 | AWS | Amazon Machine Images in Amazon EC2 | official_doc | T2 | AMI as boot/software artifact | https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AMIs.html |
| S05 | AWS | Amazon EBS snapshots | official_doc | T2 | point-in-time incremental backups | https://docs.aws.amazon.com/ebs/latest/userguide/ebs-snapshots.html |
| S06 | AWS | Elastic network interfaces | official_doc | T2 | logical virtual network card in VPC | https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-eni.html |
| S07 | AWS | AWS Availability Zones | official_doc | T2 | region/AZ structure and AZ IDs | https://docs.aws.amazon.com/global-infrastructure/latest/regions/aws-availability-zones.html |
| S08 | AWS | How Amazon VPC works | official_doc | T2 | VPC, subnet, gateway, security group concepts | https://docs.aws.amazon.com/vpc/latest/userguide/how-it-works.html |
| S09 | AWS | Configure route tables | official_doc | T2 | route table controls traffic direction | https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Route_Tables.html |
| S10 | AWS | Enable internet access using an internet gateway | official_doc | T2 | internet gateway / NAT behavior | https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Internet_Gateway.html |
| S11 | AWS | NAT gateway basics | official_doc | T2 | NAT egress and AZ resilience guidance | https://docs.aws.amazon.com/vpc/latest/userguide/nat-gateway-basics.html |
| S12 | AWS | What is AWS PrivateLink? | official_doc | T2 | private connectivity without IGW/NAT/public IP | https://docs.aws.amazon.com/vpc/latest/privatelink/what-is-privatelink.html |
| S13 | AWS | Policies and permissions in IAM | official_doc | T2 | IAM policies attached to identities/resources | https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html |
| S14 | AWS | IAM roles | official_doc | T2 | assumable identities without long-term credentials | https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html |
| S15 | AWS | Service Quotas | official_doc | T2 | quotas/limits and increase workflow | https://docs.aws.amazon.com/servicequotas/latest/userguide/intro.html |
| S16 | AWS | Cost allocation tags | official_doc | T2 | tag-based cost allocation | https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-alloc-tags.html |
| S17 | AWS | AWS CloudTrail user guide | official_doc | T2 | operational/risk auditing and API events | https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html |
| S18 | AWS | Shared Responsibility Model | official_doc | T0/T3 | customer/provider responsibility boundary | https://aws.amazon.com/compliance/shared-responsibility-model/ |
| S19 | AWS | Operational Excellence / managed services | official_doc | T3 | managed services reduce operational burden | https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/operational-excellence.html |
| S20 | AWS | Summary of AWS Service Event in US-EAST-1, Dec 2021 | incident | T5 | internal network/control-plane failure pattern | https://aws.amazon.com/message/12721/ |
| S21 | AWS | AWS Post-Event Summaries | incident_index | T5 | PES criteria and minimum availability | https://aws.amazon.com/premiumsupport/technology/pes/ |
| S22 | Google Cloud | Regions and zones, Compute Engine | official_doc | T2 | zones as failure domains; multi-zone/region placement | https://docs.cloud.google.com/compute/docs/regions-zones |
| S23 | Google Cloud | Live migration process during maintenance events | official_doc | T2 | live migration mechanics and limitations | https://docs.cloud.google.com/compute/docs/instances/live-migration-process |
| S24 | Google Cloud | Understanding allow policies | official_doc | T2 | IAM allow policy bindings | https://docs.cloud.google.com/iam/docs/allow-policies |
| S25 | Google Cloud | Cloud Audit Logs overview | official_doc | T2 | who did what, where, and when | https://docs.cloud.google.com/logging/docs/audit |
| S26 | Google Cloud | Private Service Connect | official_doc | T2 | private connectivity between consumers/producers | https://docs.cloud.google.com/vpc/docs/private-service-connect |
| S27 | Google Cloud | VPC firewall rules | official_doc | T2 | allow/deny VM connections | https://docs.cloud.google.com/firewall/docs/firewalls |
| S28 | Google Cloud | Machine families and machine images/snapshots | official_doc | T2 | machine sizing, VM image, disk snapshot concepts | https://docs.cloud.google.com/compute/docs/machine-resource ; https://docs.cloud.google.com/compute/docs/machine-images ; https://docs.cloud.google.com/compute/docs/disks/snapshots |
| S29 | Google Cloud | Well-Architected / Architecture Framework | official_doc | T3 | operational/reliability/security/cost pillars | https://docs.cloud.google.com/architecture/framework |
| S30 | Google Cloud | GCE incident report, May 2025 | incident | T5 | feature flag rollout/control-plane backlog | https://status.cloud.google.com/incidents/SXRPpPwx2RZ5VHjTwFLx |
| S31 | Microsoft Azure | Overview of virtual machines in Azure | official_doc | T2 | VM virtualization and customer maintenance duties | https://learn.microsoft.com/en-us/azure/virtual-machines/overview |
| S32 | Microsoft Azure | Azure availability zones overview | official_doc | T2 | isolated datacenter groups in a region | https://learn.microsoft.com/en-us/azure/reliability/availability-zones-overview |
| S33 | Microsoft Azure | Azure regions overview | official_doc | T2 | region resilience options | https://learn.microsoft.com/en-us/azure/reliability/regions-overview |
| S34 | Microsoft Azure | Azure Virtual Network overview | official_doc | T2 | VNet integration and private access | https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-overview |
| S35 | Microsoft Azure | Azure virtual network traffic routing | official_doc | T2 | route tables and system routes | https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-udr-overview |
| S36 | Microsoft Azure | Azure network security groups | official_doc | T2 | allow/deny inbound/outbound traffic | https://learn.microsoft.com/en-us/azure/virtual-network/network-security-groups-overview |
| S37 | Microsoft Azure | Azure NAT Gateway | official_doc | T2 | managed NAT outbound private subnet behavior | https://learn.microsoft.com/en-us/azure/nat-gateway/nat-overview |
| S38 | Microsoft Azure | Azure Private Link / Private Endpoint | official_doc | T2 | private endpoint as network interface with private IP | https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-overview |
| S39 | Microsoft Azure | Azure RBAC documentation | official_doc | T2 | fine-grained access management | https://learn.microsoft.com/en-us/azure/role-based-access-control/ |
| S40 | Microsoft Azure | Managed identities for Azure resources | official_doc | T2 | resource-level managed identity and RBAC | https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview |
| S41 | Microsoft Azure | Activity Log in Azure Monitor | official_doc | T2 | management/control-plane operation records | https://learn.microsoft.com/en-us/azure/azure-monitor/platform/activity-log |
| S42 | Microsoft Azure | Microsoft Cost Management overview | official_doc | T2 | cost analysis, monitoring, optimization | https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/overview-cost-management |
| S43 | Microsoft Azure | Azure Quotas overview | official_doc | T2 | subscription quotas and quota increases | https://learn.microsoft.com/en-us/azure/quotas/quotas-overview |
| S44 | Microsoft Azure | What to do during an Azure service disruption | official_doc | T3/T5 | incident scope, DR/failover caution, PIR use | https://learn.microsoft.com/en-us/azure/reliability/incident-response |
| S45 | Broadcom / VMware | vSphere vMotion migration | official_doc | T2/T3 | running VM migration for maintenance | https://techdocs.broadcom.com/us/en/vmware-cis/vsphere/vsphere/8-0/vcenter-and-host-management/migrating-virtual-machines-host-management/migration-with-vmotion-host-management.html |
| S46 | Broadcom / VMware | Overview of virtual machine snapshots in vSphere | support_doc | T3 | snapshots not backup; long-running risk | https://knowledge.broadcom.com/external/article/342618/overview-of-virtual-machine-snapshots-in.html |
| S47 | Broadcom / VMware | vSphere Resource Management | official_doc | T3 | allocation, shares, reservations, limits | https://techdocs.broadcom.com/us/en/vmware-cis/vsphere/vsphere/7-0/vsphere-resource-management.html |
| S48 | OpenStack | Nova hypervisors | official_doc | T3 | hypervisor selection and support | https://docs.openstack.org/nova/latest/admin/configuration/hypervisors.html |
| S49 | OpenStack | Neutron documentation | official_doc | T3 | network connectivity as a service and vNIC connectivity | https://docs.openstack.org/neutron/latest/ |
| S50 | OpenStack | Nova live migration | official_doc | T3 | live migration while instance continues running | https://docs.openstack.org/nova/latest/admin/live-migration-usage.html |
| S51 | OpenStack | Nova quotas | official_doc | T3 | resource limits by project/user | https://docs.openstack.org/nova/ussuri/user/quotas.html |

---

## 19. Minimal Machine-Readable Extract

```yaml
clone_spec:
  layer_range: "19"
  layer_name_ja: "仮想化・クラウド基盤"
  generated_at: "2026-05-13T00:00:00+09:00"
  decision_object: "どの workload に、どの仮想計算資源・ネットワーク到達性・配置ドメイン・権限・費用責任・監査粒度を与えるか"
  frontier_candidates:
    - AWS EC2/VPC/IAM/Well-Architected
    - Google Cloud Compute Engine/VPC/IAM/Architecture Framework
    - Microsoft Azure VM/VNet/RBAC/Cost/Service Health
    - VMware vSphere/ESXi/vMotion
    - OpenStack Nova/Neutron
    - NIST SP 800-145/SP 800-125
  core_philosophy:
    - "Abstraction is not invisibility."
    - "Every resource needs location, network, identity, cost, and evidence boundaries."
    - "Default private, explicit public."
    - "Managed service adoption changes the responsibility model, not the need for controls."
    - "Design for control-plane degradation."
  critical_controls:
    - approved images
    - multi-zone placement for critical workloads
    - private subnet default
    - route and gateway review
    - private endpoint catalog
    - least-privilege IAM/RBAC
    - quota preflight
    - cost allocation tags/labels
    - centralized audit logs
    - restore and DR drills
  top_failure_modes:
    - control-plane outage
    - internal network dependency
    - unsafe rollout blast radius
    - single-zone design
    - broad public ingress
    - quota exhaustion
    - snapshot-only backup
    - IAM privilege creep
    - unallocated spend
    - rushed failover
  confidence:
    A:
      - NIST definitions
      - provider official VM/network/IAM/quota/audit docs
      - public incident reports
    B:
      - cross-provider synthesized patterns
    C:
      - suggested review cadences and alert thresholds
```
