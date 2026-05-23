# Frontier Operating Model Research — コンテナ・Kubernetes（Layer 17）

- 生成日: 2026-05-13
- 対象: **17 / コンテナ・Kubernetes**
- サブテーマ: image / layer / registry / runtime、namespace、cgroups、network、volume、pod、node、cluster、deployment、service、ingress、config、secret、job、autoscaler、scheduler、control plane、data plane
- 調査方式: RESEARCH.md の Frontier Operating Model Research に基づき、公開情報限定、一次情報・公式仕様・OSS 公式文書を優先し、各レイヤーを「意思決定システム」として再構成した。
- 主な一次情報ファミリー: Kubernetes 公式ドキュメント、Open Container Initiative、Linux man-pages / kernel docs、CNI / CSI 仕様、CoreDNS、NIST SP 800-190、Kubernetes Pod Security Standards。

---

## 0. Executive Summary

コンテナ・Kubernetes レイヤーの Frontier Operating Model は、単一技術ではなく、**標準化された境界面の集合**として理解するのが最も再現性が高い。コンテナイメージは OCI Image / Distribution、コンテナ実行は OCI Runtime と Kubernetes CRI、ネットワークは Kubernetes network model と CNI、ストレージは PV / PVC / StorageClass と CSI、制御は Kubernetes API object と controller reconciliation、運用は metrics / admission / policy / rollout / autoscaling / scheduling で成立する。

この領域で先端組織が共通して採る原則は次の 7 点である。

1. **Contract-first**: OCI / CRI / CNI / CSI / Kubernetes API などの明示的 contract を境界面に置き、実装差分を contract の内側へ閉じ込める。
2. **Declarative desired state**: Pod / Deployment / Service / Job / StorageClass / NetworkPolicy などの Kubernetes object を「意図の記録」として扱い、controller が実状態を望ましい状態へ収束させる。
3. **Immutable and verifiable artifacts**: 画像タグではなく digest、registry 上の attestations / signatures / metadata、脆弱性スキャン、署名検証を supply chain control の中心に置く。
4. **Layered isolation**: Linux namespaces / cgroups だけで isolation を完結させず、Pod Security Standards、RBAC、admission、NetworkPolicy、Secret encryption、least privilege と組み合わせる。
5. **Ephemeral workload, stable abstraction**: Pod / endpoint は短命と見なし、Service / DNS / Deployment / controller / selector によって安定した抽象を提供する。
6. **Resource-aware scheduling and autoscaling**: requests / limits / scheduler plugin / HPA / metrics / node pressure を合わせて、可用性・コスト・性能のトレードオフを制御する。
7. **Control plane is product-critical**: API server / etcd / scheduler / controller manager は単なる管理系ではなく、全 workload の safety、convergence、auditability を決める中核である。

最も重要な模倣仕様は、Kubernetes を「アプリケーション実行環境」ではなく、**標準化された実行・ネットワーク・ストレージ・ポリシー・観測 contract の制御平面**として設計することである。単に manifest を書くのではなく、各 manifest がどの contract を満たし、どの controller が収束させ、どの SLI/SLO で検証し、どの admission / policy / rollback が失敗を止めるかまで定義する必要がある。

---

## 1. Layer Registry

| Layer ID | Layer Name | Definition | Decision Question | Decision Object | Primary Artifacts | Owner Roles | Default Metrics |
|---|---|---|---|---|---|---|---|
| 17.01 | Container Image | 実行単位として配布される container filesystem / config / metadata を決める。 | どの base image、tag/digest、config、provenance、scan policy で配布するか。 | Image artifact contract | Dockerfile / OCI image / SBOM / signature / scan report | App owner, platform, security | critical CVE count, digest coverage, signed image rate |
| 17.02 | Image Layer | image を構成する layer の順序、cache、最小化、脆弱性面を決める。 | layer をどう分割し、再現性・cache・攻撃面・サイズをどう最適化するか。 | Layer composition | OCI layers / build cache / build recipe | Platform, app team | image size, rebuild time, vulnerable package count |
| 17.03 | Registry / Distribution | image / artifact を保管・配布・参照する registry と distribution policy を決める。 | どの registry、namespace、retention、replication、digest policy で配布するか。 | Registry control plane | OCI registry, retention policy, artifact refs | Platform, security, release engineering | pull latency, failed pulls, retention violations |
| 17.04 | OCI Runtime | OCI bundle を実行する low-level runtime と isolation behavior を決める。 | どの OCI runtime、capability、seccomp、userns、cgroup 設定で実行するか。 | Runtime execution contract | runc/crun config, RuntimeClass | Platform, runtime owner, security | runtime error rate, sandbox escape incidents |
| 17.05 | Kubernetes CRI Runtime | kubelet と runtime の gRPC 境界、runtime 実装、node 統合を決める。 | kubelet がどの CRI runtime と image/network/Pod lifecycle を連携するか。 | CRI implementation | containerd / CRI-O config, kubelet config | Platform, node SRE | node registration failures, CRI request latency |
| 17.06 | Namespace Isolation | Linux / Kubernetes namespace による可視性・権限・テナント境界を決める。 | どの namespace を host / pod / tenant / user で共有または分離するか。 | Namespace boundary | Linux namespaces, Kubernetes namespaces, user namespaces | Security, platform, app owner | privileged pod count, namespace quota compliance |
| 17.07 | cgroups / Resource Isolation | CPU / memory / I/O / process などの resource accounting / limits を決める。 | どの cgroup hierarchy / driver / requests / limits で resource を制御するか。 | Resource isolation contract | cgroup v2, kubelet cgroup driver, Pod resources | Platform, SRE | OOMKilled rate, throttling, node pressure |
| 17.08 | Kubernetes Network / CNI | Pod / Service / Node の IP 設計と network plugin 境界を決める。 | どの Pod/Service CIDR、CNI、routing、dual-stack、overlay/underlay で接続するか。 | Cluster network model | CNI config, cluster CIDR, node CIDR | Network owner, platform | packet drop, CNI error, DNS latency |
| 17.09 | NetworkPolicy / DNS / Service Discovery | L3/L4 isolation と service discovery を決める。 | どの default deny、namespace policy、DNS naming、egress control で通信を許可するか。 | Traffic permission contract | NetworkPolicy, CoreDNS config, DNS records | Security, network, app owner | policy coverage, denied flows, DNS error rate |
| 17.10 | Volume / Ephemeral Storage | Pod 内 storage と lifecycle を決める。 | どの volume type を ephemeral / config / scratch / shared data に使うか。 | Pod storage contract | emptyDir, projected, config, secret volumes | App owner, platform | ephemeral storage usage, mount errors |
| 17.11 | PV / PVC / CSI / StorageClass | persistent storage の供給・消費・provisioning・reclaim を決める。 | どの StorageClass、provisioner、access mode、reclaim policy、backup policy で永続化するか。 | Persistent storage contract | PV, PVC, StorageClass, CSI driver | Storage owner, platform, app owner | attach/mount latency, failed claims, backup success |
| 17.12 | Pod | Kubernetes の最小 deployable unit と shared context を決める。 | どの containers を同一 Pod に co-locate し、どの resource/security/probe で運用するか。 | PodSpec | Pod manifest, probes, resource requests | App owner, platform reviewer | Ready ratio, restart count, CrashLoopBackOff |
| 17.13 | Node / kubelet | workload 実行ホストと node agent の責務を決める。 | どの node pool、kubelet config、runtime、labels/taints で workload を受けるか。 | Node execution capacity | Node object, kubelet config, labels/taints | Node SRE, platform | NodeReady, kubelet errors, allocatable usage |
| 17.14 | Cluster / API Object Model | Kubernetes API object と cluster-level state の表現を決める。 | どの object model、API version、CRD、namespace、RBAC で cluster state を表すか。 | API state model | API objects, CRDs, OpenAPI schema | Platform architecture, security | deprecated API requests, API latency |
| 17.15 | Deployment / ReplicaSet / Rollout | stateless workload の rollout / rollback / scaling を決める。 | どの strategy、replica、surge/unavailable、rollback condition で更新するか。 | Rollout contract | Deployment, ReplicaSet, rollout runbook | App owner, SRE | rollout duration, unavailable pods, rollback count |
| 17.16 | Service | ephemeral Pod 群を安定 endpoint として公開する抽象を決める。 | どの selector、port、ClusterIP/NodePort/LoadBalancer/ExternalName で公開するか。 | Stable service endpoint | Service object, EndpointSlice | App owner, network | endpoint availability, connection failure |
| 17.17 | Ingress / Gateway | HTTP(S) / L4-L7 routing と外部公開面を決める。 | Ingress と Gateway API のどちらを使い、route / TLS / policy / ownership をどう分離するか。 | Edge routing contract | Ingress, Gateway, HTTPRoute, TLS config | Network, security, app owner | 5xx, TLS expiry, route policy violations |
| 17.18 | ConfigMap / Config | non-confidential config の注入方式を決める。 | どの config を image から分離し、env / args / file / volume のどれで注入するか。 | Configuration artifact | ConfigMap, projected volume, env vars | App owner, platform | config drift, invalid config, rollout failures |
| 17.19 | Secret / Encryption | confidential data の保存・注入・更新・暗号化を決める。 | どの Secret type、encryption at rest、rotation、immutability、access policy で守るか。 | Secret handling contract | Secret, imagePullSecret, encryption config | Security, platform, app owner | secret access audit, unencrypted etcd risk, rotation age |
| 17.20 | Job / CronJob | batch / one-off / scheduled task の完了条件と再実行制御を決める。 | どの completion、parallelism、deadline、retry、idempotency で task を実行するか。 | Batch execution contract | Job, CronJob, backoff/deadline | App owner, SRE | failed jobs, missed schedules, duplicate runs |
| 17.21 | Autoscaler | workload と capacity の自動調整条件を決める。 | どの metric、target、stabilization、min/max、scale policy で増減するか。 | Scaling decision rule | HPA, VPA/Cluster Autoscaler design, metrics | SRE, app owner, platform | desired/current replicas, scale latency, saturation |
| 17.22 | Scheduler | Pod placement の scoring / filtering / binding を決める。 | どの scheduler profile、plugins、taints/tolerations、affinity、priority で配置するか。 | Placement decision system | kube-scheduler config, profiles, plugins | Platform, SRE, app owner | scheduling latency, unschedulable pods, bin-packing efficiency |
| 17.23 | Control Plane | cluster state を保持・検証・収束させる制御面を決める。 | API server / etcd / controller / scheduler をどの HA / security / observability で運用するか。 | Cluster decision plane | kube-apiserver, etcd, scheduler, controller manager | Platform SRE, security | API SLO, etcd latency/quorum, controller queue |
| 17.24 | Data Plane | 実 workload の runtime / network / storage / proxy 実行面を決める。 | kubelet / runtime / kube-proxy / CNI / CSI がどの node-level contract で実行するか。 | Workload execution plane | nodes, kubelet, runtime, kube-proxy, CNI/CSI | Node SRE, network, storage | NodeReady, PodReady, packet loss, mount errors |

---

## 2. Frontier Exemplars and Candidate Scoring

RESEARCH.md の scoring 軸に従い、個別の有名度ではなく、公開 artifact の厚み、標準性、移植性、失敗条件の可観測性を重視した。

| Candidate / Source Family | Score | Evidence Richness | Why Frontier | Transferable Pattern | Confidence |
|---|---:|---|---|---|---|
| Kubernetes project / CNCF | 95 | API docs, concepts, controllers, components, metrics, security policy | container orchestration の事実上の標準。control plane / data plane / object model / controller の公開情報が厚い。 | declarative API + reconciliation + standard object lifecycle | A |
| Open Container Initiative | 93 | Image / Runtime / Distribution specs | image、runtime、registry artifact の境界を標準化し、Kubernetes runtime stack の基礎になる。 | artifact/runtime/distribution contract separation | A |
| Linux kernel / man-pages | 88 | namespace / cgroup authoritative docs | namespaces と cgroups は container isolation / resource control の下層機構。 | kernel isolation primitives as lower-layer contract | A |
| containerd / CRI-O | 84 | official docs / GitHub / CRI integration | kubelet と OCI runtime の間をつなぐ CRI 実装として実運用に近い。 | kubelet-to-runtime adapter with image/network lifecycle | A/B |
| CNI + Kubernetes NetworkPolicy + CoreDNS | 82 | spec/repo, Kubernetes docs, CoreDNS docs | Pod network、policy、service discovery を plugin / DNS / API object の組み合わせで実装する。 | pluggable connectivity + policy + discovery | A |
| CSI + Kubernetes Storage | 82 | CSI spec, Kubernetes PV/PVC/StorageClass docs | persistent storage を vendor-neutral plugin contract に分離する。 | storage provisioning abstraction | A |
| Gateway API | 78 | official project docs, role-oriented API | Ingress の後継的 L4/L7 routing API。route ownership と infrastructure ownership を分離する。 | role-oriented edge routing | A/B |
| NIST SP 800-190 + Kubernetes PSS | 76 | NIST guidance, Kubernetes standards | container security risk と Kubernetes pod-level hardening の共通語彙を提供する。 | least privilege + policy admission + periodic review | A/B |

---

## 3. Evidence Map

| Claim ID | Claim | Evidence Type | Sources | Confidence | Decision Field |
|---|---|---|---|---|---|
| C-001 | Kubernetes は control plane と worker node で構成され、control plane は API server / etcd / scheduler / controller-manager、node は kubelet / kube-proxy / runtime を含む。 | official doc | [K8S-COMPONENTS] | A | architecture / ownership |
| C-002 | Kubernetes object は cluster state の永続的 entity であり、spec は desired state、status は current state を表し、control plane が実状態を desired state に近づける。 | official doc | [K8S-OBJECTS], [K8S-CONTROLLERS] | A | core philosophy / decision model |
| C-003 | Kubernetes API server は object の検証・設定・REST operation・shared state の frontend を担う。 | official doc | [K8S-APISERVER], [K8S-API] | A | control plane |
| C-004 | OCI は Runtime / Image / Distribution の 3 仕様を中心に container artifact と runtime execution の境界を標準化する。 | standards body | [OCI-OVERVIEW], [OCI-SPECS] | A | interface rules |
| C-005 | OCI Image / Distribution v1.1 は artifact support と referrers API により signatures / attestations / SBOM 等を image に関連付けられる。 | standards body | [OCI-IMAGE-DIST-11] | A | supply chain controls |
| C-006 | Kubernetes は Pod 実行に各 node の container runtime を必要とし、v1.26 以降は CRI v1 対応 runtime が必要である。 | official doc | [K8S-CRI], [K8S-RUNTIMES] | A | runtime compatibility |
| C-007 | Linux namespaces は process に見える global system resource を分離し、cgroup / IPC / network / mount / PID / user / UTS 等を対象にする。 | kernel/man-page | [LINUX-NS] | A | isolation |
| C-008 | cgroup v2 は resource control の kernel mechanism であり、cgroup namespace によって /proc/PID/cgroup の見え方も仮想化される。 | kernel doc | [KERNEL-CGROUP-V2] | A | resource isolation |
| C-009 | kubelet と container runtime の cgroup driver は一致させる必要があり、稼働済み node の driver 変更は pod sandbox 再作成障害を招き得る。 | official doc | [K8S-RUNTIMES] | A | failure modes |
| C-010 | Pod は Kubernetes で作成・管理できる最小 deployable unit で、containers が storage/network を共有し、shared context は namespaces/cgroups を含む。 | official doc | [K8S-PODS] | A | pod specification |
| C-011 | Kubernetes network model は Pod / Service / Node の IP range と network plugin に依存し、CNI plugin が通常の実装面になる。 | official doc / spec | [K8S-NETWORKING], [CNI] | A | network |
| C-012 | NetworkPolicy は L3/L4 traffic rules であり、対応 plugin / controller がないと作成しても効果がない。 | official doc | [K8S-NETPOL] | A | controls / failure modes |
| C-013 | Kubernetes DNS は Service / Pod を安定名で発見する手段であり、IP 直接依存を避ける。 | official doc | [K8S-DNS], [COREDNS] | A | service discovery |
| C-014 | Volume は Pod 内 container の data sharing / config / scratch / durable data のために使われ、persistent storage は PV/PVC に分離される。 | official doc | [K8S-VOLUMES], [K8S-PV] | A | storage |
| C-015 | Dynamic provisioning は PVC 作成を契機に StorageClass に基づいて storage を on-demand に provision する。 | official doc | [K8S-DYNAMIC], [K8S-STORAGECLASS] | A | storage provisioning |
| C-016 | CSI は arbitrary block/file storage を container orchestrator に公開する標準で、third-party provider が Kubernetes core を変更せず plugin を提供できる。 | official/spec | [CSI-K8S], [CSI-SPEC] | A | storage plugin contract |
| C-017 | Deployment は stateless Pod / ReplicaSet の declarative update と rollout / rollback / scaling を管理する。 | official doc | [K8S-DEPLOYMENT] | A | rollout |
| C-018 | Service は changing Pod 群を logical endpoint として公開し、selector により backend set を定義する。 | official doc | [K8S-SERVICE] | A | service exposure |
| C-019 | Ingress は HTTP/HTTPS routing API だが frozen で、Kubernetes は Gateway API を後継・補完的 API として推奨している。 | official doc | [K8S-INGRESS], [GATEWAY-API] | A | edge routing |
| C-020 | ConfigMap は非機密 key-value data であり、secret / encryption 用ではなく、サイズ上限は 1 MiB である。 | official doc | [K8S-CONFIGMAP] | A | config controls |
| C-021 | Secret も 1 MiB 上限があり、etcd 暗号化は別途 encryption provider config を設定しない限り既定では plaintext 保存リスクがある。 | official doc | [K8S-SECRET], [K8S-ENCRYPTION] | A | secret controls |
| C-022 | Job は completion まで Pod を作成・retry し、CronJob は schedule により Job を作るが、複数/未実行の可能性があるため task は idempotent にすべきである。 | official doc | [K8S-JOB], [K8S-CRONJOB] | A | batch controls |
| C-023 | HPA は metric に基づき workload replica を自動調整し、control loop interval の既定値は 15 秒である。 | official doc | [K8S-HPA] | A | autoscaling |
| C-024 | Kubernetes scheduler は scheduling cycle と binding cycle に分かれる plugin architecture で、profiles / extension points により behavior を制御できる。 | official doc | [K8S-SCHED-FW], [K8S-SCHED-CONFIG] | A | scheduler |
| C-025 | Kubernetes components は Prometheus format の metrics を export し、stable metrics は API contract として扱われる。 | official doc | [K8S-METRICS], [K8S-SYSTEM-METRICS] | A | observability |
| C-026 | Pod Security Standards は Privileged / Baseline / Restricted の 3 policy を定義し、Namespace label で Pod Security Admission enforcement を運用できる。 | official doc | [K8S-PSS], [K8S-PSS-LABELS] | A | security controls |

---

## 4. Core Philosophy

### 4.1 Contract boundary を明示する

Frontier な Kubernetes platform は、「どの実装を使うか」よりも先に「どの contract を境界にするか」を決める。image と registry では OCI Image / Distribution、実行では OCI Runtime と CRI、network では CNI、storage では CSI、cluster state では Kubernetes API object、edge routing では Gateway API / Ingress、observability では Prometheus format の component metrics が contract になる。

この contract-first の利点は、runtime、CNI、CSI、Ingress controller、registry、node pool、cloud provider が入れ替わっても、platform の運用ルールを維持できる点である。逆に contract を曖昧にすると、CNI が NetworkPolicy を実装していない、Secret が暗号化されていない、image tag が動く、scheduler が意図しない node に置く、StorageClass の reclaimPolicy が期待と違う、といった失敗が起きる。

### 4.2 Desired state と controller を分離する

Kubernetes の object は「実行命令」ではなく「望ましい状態の記録」である。Deployment、Job、Service、PVC、NetworkPolicy、HPA、Ingress/Gateway などは、object と controller のペアとして読まなければならない。frontier pattern は、manifest を単なる設定ファイルとして扱わず、次を明示する。

- どの controller がその object を読むか。
- どの resource / field が desired state を定義するか。
- actual state はどの status / event / metric で観測するか。
- reconciliation が失敗した時、どの alert / rollback / escalation が起動するか。

### 4.3 Isolation は単一機構ではなく多層にする

Linux namespaces / cgroups は container isolation の基礎だが、Kubernetes 運用で必要な isolation はそれだけでは足りない。Pod Security Standards、user namespaces、RuntimeClass、seccomp/AppArmor/SELinux、capabilities、RBAC、NetworkPolicy、Secret encryption、admission、resource quota、node taints、node pool separation を組み合わせる。とくに multi-tenant cluster では、namespace は「名前空間」だけでなく、quota、policy、RBAC、network boundary、cost attribution の単位として設計する。

### 4.4 Ephemeral を前提に stable abstraction を置く

Pod、container、endpoint、node は失われる前提で設計する。Service、DNS、Deployment、ReplicaSet、Job、HPA、PDB、PV/PVC、Gateway route は ephemeral component の前に置く安定抽象である。frontier pattern は、Pod IP への直接依存、single Pod execution、mutable tag、manual restart を避け、controller と stable abstraction へ寄せる。

### 4.5 Supply chain と runtime を同じ system として扱う

image build / scan / sign / push / pull / run / observe / deprecate は分離してはいけない。OCI artifact と registry、kubelet imagePullPolicy、digest pinning、admission、runtime sandbox、node policy、PodSecurity、Secret handling は同じ supply-chain-to-runtime pipeline として設計する。

---

## 5. Decision Model

### 5.1 Inputs

- Workload type: stateless service、stateful service、batch、scheduled batch、daemon、control plane addon、ML/AI workload、security-sensitive workload。
- Runtime requirements: CPU architecture、GPU/accelerator、kernel feature、privilege、hostNetwork / hostPID / hostIPC、user namespaces、seccomp/capabilities。
- Image requirements: base image、digest、registry location、signature、attestation、SBOM、vulnerability threshold、pull policy。
- Network requirements: Service exposure、ingress/gateway、DNS、egress、default deny、namespace isolation、dual-stack、service mesh requirement。
- Storage requirements: ephemeral / persistent、access mode、throughput、latency、backup、reclaimPolicy、snapshot、encryption。
- Scheduling requirements: requests/limits、affinity/anti-affinity、taints/tolerations、priority、topology spread、node pool、zone/region。
- Scaling requirements: metrics、target utilization、min/max replica、scale up/down stabilization、cold-start tolerance。
- Security requirements: tenant boundary、RBAC、Pod Security Standards、Secret encryption、audit、compliance、incident blast radius。
- Operability requirements: rollout/rollback、observability、alerting、upgrade cadence、cluster lifecycle、SLO/SLA、cost budget。

### 5.2 Criteria

| Criterion | Rationale | Typical Evidence |
|---|---|---|
| Portability | OCI / CRI / CNI / CSI / API object により provider lock-in を下げる。 | OCI specs, Kubernetes APIs, CNI/CSI specs |
| Determinism | digest、declared resources、selectors、StorageClass、scheduler profile で再現可能にする。 | image digest, PodSpec, Deployment spec |
| Least privilege | PodSecurity、RBAC、NetworkPolicy、Secret scope、capabilities を最小化する。 | PSS, NetworkPolicy, RBAC policy |
| Convergence | controller が desired state に収束できるよう field と status を設計する。 | Deployment/Job/HPA controllers |
| Operability | metrics、events、logs、probes、runbooks により障害原因を切り分ける。 | metrics docs, kubelet / apiserver metrics |
| Blast-radius containment | namespace / node pool / policy / quota / rollout strategy で影響を限定する。 | quotas, PSS labels, rollout limits |
| Evolution | deprecated API、Ingress freeze、Gateway migration、CSI/CRI compatibility を追従する。 | release notes, deprecation metrics |

### 5.3 Priorities

1. **Standard contract first**: OCI / CRI / CNI / CSI / Kubernetes API の境界を明示する。
2. **Image immutability**: 本番では mutable tag 依存を避け、digest と signature / attestation / scan を使う。
3. **Resource declaration**: Pod は requests / limits / QoS / probes を明示し、scheduler と autoscaler の入力を安定させる。
4. **Namespace as tenancy unit**: namespace は RBAC / quota / PSS / NetworkPolicy / cost / ownership とセットで設計する。
5. **Default-deny where possible**: egress/ingress と pod privilege は default deny / baseline / restricted から例外化する。
6. **Controller-managed lifecycle**: Deployment / Job / CronJob / HPA / Service / Gateway で lifecycle を管理し、裸 Pod 運用は例外にする。
7. **Observed control plane**: API server / etcd / scheduler / controller manager / admission webhook の SLO を明示する。

### 5.4 Prohibitions

- 本番 workload を `default` namespace に置く。
- mutable tag のみで本番 deployment を固定する。
- ImagePullBackOff / CrashLoopBackOff を application incident と platform incident に分けずに放置する。
- CNI が NetworkPolicy を実装していない cluster で NetworkPolicy に依存する。
- Secret を ConfigMap、environment dump、Git repository、plain-text manifest に置く。
- etcd Secret encryption を確認せずに「Secret は暗号化されている」とみなす。
- 稼働済み node の kubelet/runtime cgroup driver を無計画に変更する。
- hostNetwork / hostPID / hostIPC / privileged を通常 workload に許す。
- CronJob / retryable Job を非 idempotent な処理として設計する。
- Ingress と Gateway API の ownership を定義せず、application team と infrastructure team の責任境界を曖昧にする。
- Resource requests/limits なしに HPA / scheduler / capacity planning を成立させようとする。

### 5.5 Thresholds and Hard Constraints

| Constraint | Value / Rule | Source | Implication |
|---|---|---|---|
| ConfigMap size | 1 MiB | [K8S-CONFIGMAP] | 大容量 config は volume / object storage / external config system を使う。 |
| Secret size | 1 MiB | [K8S-SECRET] | 大容量 secret / cert bundle は分割や外部 secret store を検討する。 |
| Image tags | tags can move; digests are fixed | [K8S-IMAGES] | 本番は digest pinning を標準化する。 |
| ImagePullBackOff backoff | retry delay capped up to 300s | [K8S-IMAGES] | registry / credential / digest miss は rollout SLO に影響する。 |
| CRI compatibility | CRI v1 required since Kubernetes v1.26 | [K8S-CRI], [K8S-RUNTIMES] | runtime upgrade は Kubernetes version と連動する。 |
| HPA sync interval | default 15s | [K8S-HPA] | scale reaction time と metric freshness を設計する。 |
| Ingress API | frozen; Gateway API recommended for new features | [K8S-INGRESS], [GATEWAY-API] | 新規 L7 policy は Gateway API を優先検討する。 |
| PodSecurity Admission | GA since v1.25; namespace label based | [K8S-PSS-LABELS] | namespace 作成時に enforce/audit/warn labels を標準化する。 |
| Scheduler config | KubeSchedulerConfiguration v1; extension points | [K8S-SCHED-CONFIG] | custom scheduling は plugin/profile で行う。 |
| CSI | GA from Kubernetes v1.13 | [CSI-K8S] | persistent storage integration は CSI driver を前提にする。 |

### 5.6 Owners and Reviewers

| Domain | Primary Owner | Reviewers | Artifacts Reviewed |
|---|---|---|---|
| Image / registry | Release engineering / platform | Security, app owner | Dockerfile, image digest, SBOM, signature, vulnerability report |
| Runtime / nodes | Platform SRE | Security, runtime owner | kubelet config, runtime config, RuntimeClass, node pool spec |
| Namespace / policy | Platform governance | Security, tenant owner | namespace labels, quota, RBAC, NetworkPolicy, PSS |
| Network | Network platform | Security, app owner | CNI config, Service, Ingress/Gateway, DNS, NetworkPolicy |
| Storage | Storage platform | App owner, security | StorageClass, PVC, backup/snapshot, reclaimPolicy |
| Workload objects | Application owner | Platform reviewer, SRE | Deployment, PodSpec, probes, resources, Service, HPA |
| Batch | Application owner | SRE | Job/CronJob, idempotency, deadlines, retry/backoff |
| Scheduling / scaling | Platform SRE | App owner, finance/capacity | scheduler profile, HPA policy, requests/limits, node pool |
| Control plane | Platform SRE | Security, architecture | API server, etcd, controller, scheduler, admission, metrics |

---

## 6. Operating Model

### 6.1 Role Model

- **Platform Architecture Owner**: Kubernetes version、cluster topology、control plane design、extension boundaries、API deprecation policy を決める。
- **Runtime Owner**: containerd / CRI-O、OCI runtime、cgroup driver、RuntimeClass、node OS、kernel feature を管理する。
- **Image Supply Chain Owner**: base image、build pipeline、registry、scan、signature、attestation、retention、promotion を管理する。
- **Network Owner**: CNI、Pod/Service CIDR、NetworkPolicy、CoreDNS、Gateway/Ingress、load balancer、egress policy を管理する。
- **Storage Owner**: CSI driver、StorageClass、PV/PVC、snapshot、backup、reclaimPolicy、capacity を管理する。
- **Security Owner**: RBAC、admission、PSS、Secret encryption、audit、policy-as-code、incident response を管理する。
- **Application Owner**: PodSpec、Deployment、Service、ConfigMap、Secret usage、Job/CronJob、HPA、runbook を所有する。
- **SRE / Operations Owner**: SLO、alerts、rollout/rollback、capacity planning、incident triage、upgrade windows を管理する。

### 6.2 Lifecycle Process

1. **Cluster / platform design review**
   - Version、control plane HA、etcd backup、node pools、CNI、CSI、runtime、registry、admission、metrics を決める。
   - CRI / CNI / CSI / Gateway / Ingress controller の support matrix を source catalog に残す。

2. **Namespace onboarding**
   - namespace owner、quota、limit range、RBAC、PSS labels、NetworkPolicy baseline、cost labels、Secret policy を作成する。
   - production namespace では default deny ingress/egress と restricted または baseline PSS を原則にする。

3. **Image promotion**
   - image build、scan、SBOM、signature/attestation、registry push、digest pinning、retention を release pipeline に組み込む。
   - production deployment は image digest で固定し、tag は human-friendly alias として扱う。

4. **Workload readiness review**
   - PodSpec、resources、probes、securityContext、ConfigMap/Secret、Service、NetworkPolicy、HPA、Deployment strategy、Job idempotency を review する。
   - Pod が host namespace / privileged / hostPath / broad RBAC を要求する場合は exception ticket を必須化する。

5. **Rollout / rollback**
   - Deployment は maxUnavailable / maxSurge、readiness probe、progressDeadlineSeconds、rollback policy を定義する。
   - Job / CronJob は activeDeadlineSeconds、backoffLimit、concurrencyPolicy、startingDeadlineSeconds、idempotency key を定義する。

6. **Continuous operations**
   - API server、scheduler、controller、kubelet、runtime、CNI、CSI、CoreDNS、Ingress/Gateway、application workload の metrics を監視する。
   - deprecated API requests、ImagePullBackOff、CrashLoopBackOff、unschedulable Pods、PVC pending、DNS errors、policy-denied flows を日次またはリアルタイムで検出する。

7. **Upgrade / deprecation management**
   - Kubernetes minor upgrade ごとに CRI compatibility、API removals、scheduler config changes、metrics deprecation、Ingress/Gateway migration、CSI/CNI compatibility を確認する。
   - canary node pool、canary namespace、control plane upgrade window、rollback plan を用意する。

### 6.3 Governance Forums

| Forum | Cadence | Participants | Decisions |
|---|---|---|---|
| Platform Architecture Review | monthly / major change | platform, security, network, storage, app representatives | version, runtime, CNI/CSI, admission, cluster topology |
| Workload Production Readiness Review | before prod launch | app owner, SRE, security, platform | PodSpec, Deployment, Service, HPA, NetworkPolicy, Secret, runbook |
| Security Exception Review | on demand | security, platform, app owner | privileged, host namespace, broad RBAC, hostPath, external exposure |
| Capacity / Cost Review | weekly/monthly | SRE, finance/capacity, app owners | requests/limits, HPA targets, node pool sizing, overprovisioning |
| Incident Review | after SEV / major failure | SRE, app, platform, network/storage | root cause, controller behavior, policy gap, runbook update |
| Upgrade Readiness Review | each minor version | platform, SRE, security | deprecated APIs, CRI/CNI/CSI compatibility, metrics changes |

---

## 7. Technical / Business Specification

### 7.1 Image / Layer / Registry Specification

**Decision object**: production workload に投入可能な image artifact。

**Spec**:

- OCI Image Specification に準拠した image を生成し、registry は OCI Distribution compatible とする。
- Production manifest は image digest を記録する。tag は build label または release alias として残すが、deployment の immutable identity にはしない。
- Base image は approved list から選定し、minimal image / distroless / slim image を候補にする。ただし debugability、compliance、package management needs と trade-off する。
- Layer は vulnerability surface と rebuild cache を分ける。OS package layer、language runtime layer、dependency layer、application binary layer を分離し、頻繁に変わる layer を後段に置く。
- Registry は namespace / repository ownership、retention、promotion stage、replication、immutability、pull credentials、audit を定義する。
- OCI v1.1 artifact / referrers を使える環境では、signature、attestation、SBOM、scan result を image digest に関連付ける。
- Admission で unsigned image、critical CVE image、unapproved registry、mutable tag-only deployment を拒否または audit する。

**Failure modes**:

- `latest` tag や mutable tag による silent drift。
- registry credential expiry による ImagePullBackOff。
- base image CVE の未検出。
- large image による rollout 遅延。
- SBOM / signature が tag に紐づき、digest に紐づいていない。

### 7.2 Runtime / Namespace / cgroups Specification

**Decision object**: node 上で Pod を安全かつ予測可能に実行する runtime contract。

**Spec**:

- kubelet は CRI v1 compatible runtime と接続する。runtime 実装は containerd または CRI-O を標準候補にし、Kubernetes version support matrix を管理する。
- low-level runtime は OCI Runtime Spec compatible とする。runc/crun 等の runtime は security profile と kernel feature support を確認する。
- cgroup driver は kubelet と runtime で一致させる。systemd managed host では systemd cgroup driver を標準にする。
- cgroup v2 の availability、kernel version、node OS、runtime support を node pool spec に記録する。
- user namespaces は root-in-container と host privilege の分離に有効だが、hostNetwork / hostIPC / hostPID 等との制約を確認する。
- PodSecurity、securityContext、capabilities、seccomp、readOnlyRootFilesystem、runAsNonRoot、allowPrivilegeEscalation を workload review に含める。
- RuntimeClass を使って sandboxed runtime、GPU runtime、specialized runtime を分離できるようにする。

**Failure modes**:

- kubelet/runtime cgroup driver mismatch。
- CRI API version mismatch による node registration failure。
- privileged / host namespace による isolation bypass。
- container root が host root と近すぎる設計。
- runtime upgrade と Kubernetes minor version upgrade の非同期。

### 7.3 Network / Service / Ingress / Gateway Specification

**Decision object**: cluster 内外の traffic permission と endpoint abstraction。

**Spec**:

- Pod CIDR、Service CIDR、Node IP range は重複させない。IPv4 / IPv6 / dual-stack の方針を cluster design 時に決める。
- CNI plugin は NetworkPolicy support、dual-stack support、eBPF / overlay / underlay、encryption、observability、upgrade path で評価する。
- Namespace 作成時に default-deny NetworkPolicy を適用し、application owner が明示的に ingress / egress を開く。
- Service は ephemeral Pods を stable endpoint として公開する。selector と EndpointSlice の健全性を監視する。
- CoreDNS / cluster DNS は service discovery の中核として SLO を持つ。DNS latency / SERVFAIL / NXDOMAIN spike を監視する。
- Ingress は既存互換性のため維持できるが、新規 L4/L7 policy、role separation、cross-namespace reference、GatewayClass/HTTPRoute ownership が必要な場合は Gateway API を優先する。
- TLS certificate、route ownership、external DNS、WAF/load balancer policy は Gateway/Ingress と別 artifact として管理する。

**Failure modes**:

- NetworkPolicy 非対応 CNI で policy に依存する。
- Service selector typo により endpoint が空になる。
- DNS outage が application outage と誤診される。
- Ingress controller / Gateway controller の ownership 不明。
- east-west traffic が default allow のまま横展開を許す。

### 7.4 Volume / PV / CSI Specification

**Decision object**: Pod lifecycle と storage lifecycle の分離。

**Spec**:

- Pod 内の scratch / cache / shared temporary data は ephemeral volume として扱い、durable data は PVC を使う。
- PersistentVolume は provider 管理の storage resource、PersistentVolumeClaim は workload の storage request として分離する。
- StorageClass は provisioner、parameters、reclaimPolicy、volumeBindingMode、allowVolumeExpansion を明示する。
- Dynamic provisioning を標準にし、特殊 data class だけ pre-provisioned PV とする。
- CSI driver は version compatibility、node plugin / controller plugin、snapshot support、resize support、topology awareness、failure behavior を検証する。
- Stateful workload は backup / restore / snapshot / disaster recovery の runbook を release criteria に含める。

**Failure modes**:

- reclaimPolicy の誤設定による data loss または orphan volume。
- PVC Pending が capacity issue か StorageClass issue か切り分けられない。
- zone/topology と scheduler placement の不整合。
- CSI driver upgrade による attach/mount error。
- ephemeral storage exhaustion による eviction。

### 7.5 Pod / Deployment / Service / Config / Secret Specification

**Decision object**: application workload の unit、lifecycle、exposure、configuration、secrets。

**Spec**:

- Pod は最小 deployable unit として扱い、複数 container は sidecar、adapter、ambassador、init 等の明確な理由がある場合に限る。
- Production workload は裸 Pod ではなく Deployment、StatefulSet、DaemonSet、Job/CronJob 等の controller-managed object として運用する。
- Deployment は replicas、strategy、readiness、liveness/startup probes、resources、securityContext、revision history、progress deadline を定義する。
- Service は Pod IP ではなく logical endpoint として定義し、client は Service DNS name を使う。
- ConfigMap は非機密 config のみとし、Secret と混同しない。1 MiB 上限を超える config は外部 config store / volume / object store を検討する。
- Secret は namespace scoped の secret material として扱い、encryption at rest、rotation、least-privilege mount、immutable secret を検討する。
- 本番 Secret は `env` への展開を最小化し、file mount / external secret integration / short-lived credentials を優先する。

**Failure modes**:

- ConfigMap に credential を格納する。
- Secret encryption provider 未設定なのに encrypted と誤認する。
- readiness probe 不備により rollout 中に traffic が壊れる。
- liveness probe が過度に aggressive で self-inflicted restart を起こす。
- sidecar が resource requests を持たず Pod QoS を悪化させる。

### 7.6 Job / CronJob / Autoscaler / Scheduler Specification

**Decision object**: non-steady workload と placement / scaling の自動意思決定。

**Spec**:

- Job は completion、parallelism、backoffLimit、activeDeadlineSeconds、ttlSecondsAfterFinished を定義する。
- CronJob は schedule、timeZone、concurrencyPolicy、startingDeadlineSeconds、suspend、successful/failed history limits を定義する。
- CronJob / retryable Job は duplicate execution / missed execution を前提に idempotent に設計する。
- HPA は metric source、target、min/max replica、stabilization window、scale policy を定義する。CPU metric だけで不十分な workload は custom metrics を使う。
- Scheduler は requests/limits、affinity、topology spread、taints/tolerations、priority/preemption を入力として placement を決める。
- Custom scheduling は kube-scheduler profiles / plugins / extension points で行い、manual nodeName pinning は例外にする。

**Failure modes**:

- HPA が CPU 以外の bottleneck を見ずに scale する。
- requests 未設定により scheduler と HPA が誤判断する。
- CronJob が duplicate side effect を発生させる。
- affinity / anti-affinity が強すぎて Pods が unschedulable になる。
- priority/preemption が低優先 workload を過度に排除する。

### 7.7 Control Plane / Data Plane Specification

**Decision object**: cluster の意思決定面と実行面の責任分離。

**Control Plane Spec**:

- kube-apiserver は API validation、admission、REST operation、front-end of cluster state として SLO を持つ。
- etcd は cluster state の source of truth として backup、quorum、latency、compaction、encryption を管理する。
- kube-scheduler は Pod placement decision system として scheduler latency、unschedulable queue、profile/plugin health を監視する。
- kube-controller-manager は Deployment / Job / Node / EndpointSlice 等の controller convergence を監視する。
- Admission webhooks は availability / latency / failurePolicy を SLO 化し、control plane の single point of failure にしない。

**Data Plane Spec**:

- kubelet は node-local agent として PodSpec を実行し、container runtime、CNI、CSI、probes、status を扱う。
- container runtime は image pull / unpack / container lifecycle を担う。
- kube-proxy または replacement は Service traffic routing を担う。
- CNI plugin は Pod network namespace、IP assignment、routing、policy を担う。
- CSI node plugin は volume mount / unmount / attach operation を担う。

**Failure modes**:

- API server outage で existing workload は動くが new scheduling / scaling / reconciliation が止まる。
- etcd latency が API latency と controller convergence を悪化させる。
- NodeNotReady により workloads が rescheduled されるが storage / topology constraints で復旧しない。
- kubelet と runtime の状態不一致により ghost containers / stale sandboxes が残る。
- admission webhook outage が all deployments を止める。

---

## 8. Metrics

| Area | Metrics / Signals | Interpretation | Action |
|---|---|---|---|
| API server | `apiserver_request_duration_seconds`, `apiserver_request_total`, inflight requests, deprecated API requests | control plane responsiveness / API compatibility | latency SLO breach, API deprecation remediation |
| Admission | admission duration, rejected requests, webhook latency | policy overhead and failure | webhook timeout tuning, failurePolicy review |
| Scheduler | scheduling latency, unschedulable Pods, requested resources, preemption events | placement bottleneck / capacity shortage | node pool scaling, affinity review, requests tuning |
| Controller | workqueue depth, reconciliation errors, rollout progress | desired/current state divergence | controller health check, object spec review |
| Kubelet | NodeReady, runtime errors, probe failures, cAdvisor metrics, PSI | node-level pressure and runtime health | drain/cordon, node repair, resource tuning |
| Runtime/image | ImagePullBackOff, ErrImagePull, pull latency, registry 5xx | supply chain / registry issue | registry HA, credential rotation, digest verification |
| Workload | Pod Ready ratio, restarts, CrashLoopBackOff, OOMKilled, throttling | app health and resource fit | probe tuning, limits/requests adjustment |
| Network | DNS latency/errors, NetworkPolicy deny logs, CNI errors, service endpoint count | service discovery / policy / connectivity | CoreDNS scale, CNI repair, policy debugging |
| Storage | PVC Pending, attach/mount latency, volume errors, backup success | storage provisioning / persistence | StorageClass capacity, CSI upgrade, backup repair |
| Autoscaling | current vs desired replicas, scale events, target metric error | scaling effectiveness | HPA policy tuning, metric pipeline repair |
| Security | privileged pods, PSS violations, unsigned images, Secret access audit | policy compliance | admission enforcement, exception review |

---

## 9. Failure Modes

| Failure Mode | Mechanism | Early Signal | Prevention / Control |
|---|---|---|---|
| Mutable image drift | tag が移動し、同一 manifest で別 image が起動する。 | digest mismatch, deployment with tag-only image | digest pinning, admission policy, registry immutability |
| ImagePullBackOff | registry, credential, DNS, digest, policy failure。 | `ImagePullBackOff`, `ErrImagePull`, pull latency | registry HA, image pre-pull, credential rotation |
| Runtime mismatch | kubelet と runtime の CRI / cgroup / version mismatch。 | node registration failure, sandbox errors | support matrix, canary node pool, driver alignment |
| Namespace escape / privilege escalation | host namespaces, privileged, capabilities, weak PSS。 | privileged pod count, PSS audit warnings | PSS restricted/baseline, admission, exception workflow |
| Resource starvation | requests/limits 不備、overcommit、noisy neighbor。 | throttling, OOMKilled, PSI, NodePressure | resource policy, LimitRange, quota, HPA/VPA review |
| NetworkPolicy no-op | CNI が NetworkPolicy を実装しない。 | policy created but traffic still flows | CNI capability validation, conformance tests |
| DNS outage | CoreDNS saturation / misconfig / upstream issue。 | DNS latency, SERVFAIL, NXDOMAIN spike | CoreDNS scaling, cache tuning, runbook |
| Empty service endpoint | selector mismatch / readiness failure。 | endpoint count zero, 503 | selector validation, readiness gates, rollout checks |
| PVC stuck | StorageClass/provisioner/topology/capacity mismatch。 | PVC Pending, attach/mount failures | StorageClass validation, CSI health, topology-aware scheduling |
| Deployment bad rollout | readiness probe 欠落、surge/unavailable misfit。 | rollout stuck, unavailable pods | progressive rollout, probes, rollback automation |
| CronJob duplicate side effects | controller timing / missed schedule / concurrency。 | duplicate Jobs, missed schedules | idempotent task design, concurrencyPolicy, deadlines |
| HPA wrong signal | CPU 以外が bottleneck、metric stale。 | oscillation, saturation despite scale | custom metrics, stabilization windows |
| Scheduler deadlock | hard affinity / topology / taints が強すぎる。 | unschedulable pods | scheduling simulation, policy review |
| Admission webhook outage | webhook unavailable / timeout / failurePolicy。 | all creates/updates fail or bypass policy | HA webhook, timeout, failurePolicy design |
| Secret leakage | ConfigMap misuse, env dump, unencrypted etcd, broad RBAC。 | audit anomalies, secret in logs/repo | encryption at rest, least privilege, rotation |

---

## 10. Anti-patterns

1. **Kubernetes を YAML 実行基盤としてだけ扱う**: controller、status、metrics、policy、rollback を設計しない manifest は運用システムではない。
2. **Pod を application boundary と誤認する**: Pod は scheduling / shared context unit であり、service ownership や transaction boundary ではない。
3. **Namespace を folder として扱う**: namespace は policy、quota、RBAC、network、cost、ownership の単位である。
4. **Secret を「base64 だから安全」と扱う**: Kubernetes Secret は機密情報の型であって、暗号化・アクセス制御・rotation を別途設計する必要がある。
5. **CNI / CSI / Ingress controller を black box にする**: plugin の機能差は NetworkPolicy、topology、policy、observability、recovery に直結する。
6. **requests/limits を後回しにする**: scheduler、HPA、capacity planning、QoS が成立しない。
7. **Image tag を release identity にする**: tag は mutable であり、digest を release identity にしなければ forensic と rollback が不安定になる。
8. **Gateway / Ingress ownership を曖昧にする**: route、TLS、external exposure、security policy の責任分界が事故を生む。
9. **Job idempotency を無視する**: Kubernetes batch controller は retry / duplicate / missed schedule の可能性を持つ。
10. **Control plane metrics を platform only とみなす**: API latency や admission latency は全 workload の deployability と recovery に影響する。

---

## 11. Maturity Model

| Level | Name | Criteria |
|---:|---|---|
| 0 | 未整備 | ad hoc Docker host、manual run、no registry policy、no resource policy、no namespace governance。 |
| 1 | 個人依存 | Kubernetes cluster はあるが、default namespace、mutable tags、manual kubectl、no PSS / no NetworkPolicy。 |
| 2 | 文書化 | Namespace、Deployment、Service、ConfigMap/Secret、PVC、basic registry、runtime support が文書化されている。 |
| 3 | 標準化 | digest pinning、requests/limits、probes、HPA、PSS baseline/restricted、NetworkPolicy、StorageClass、rollout/rollback runbook が標準化。 |
| 4 | 自動化・計測 | admission policy、policy-as-code、image signing/scanning、metrics SLO、GitOps/CI validation、control plane dashboards、canary upgrades。 |
| 5 | 自律改善・業界先端 | supply chain provenance、multi-cluster policy、Gateway role separation、scheduler/autoscaler optimization、runtime sandboxing、chaos drills、continuous deprecation management。 |

---

## 12. Clone Implementation Guide

### 12.1 Initial 30–60 Day Implementation

**Week 1–2: Baseline inventory**

- Kubernetes version、node OS、container runtime、CRI version、cgroup driver、CNI、CSI、Ingress/Gateway controller、CoreDNS、registry、admission controllers を棚卸しする。
- 全 namespace、RBAC、PSS labels、NetworkPolicy、ResourceQuota、LimitRange、Secrets、ConfigMaps、StorageClasses、HPA、CronJobs を抽出する。
- Production deployments の image tag/digest、requests/limits、probes、securityContext、Service/Ingress/Gateway、PVC、HPA を audit する。

**Week 3–4: Minimum policy standard**

- Namespace onboarding template を作る: owner label、quota、LimitRange、PSS labels、default-deny NetworkPolicy、RBAC、cost labels。
- Image policy を作る: allowed registries、digest requirement、scan threshold、signature/attestation requirement。
- Workload production readiness checklist を作る: PodSpec、probes、requests/limits、Deployment strategy、Service、NetworkPolicy、Secret handling、HPA、runbook。

**Week 5–6: Observability and failure controls**

- API server、scheduler、controller manager、kubelet、CoreDNS、CNI、CSI、registry、Ingress/Gateway の dashboards / alerts を整備する。
- ImagePullBackOff、CrashLoopBackOff、Unschedulable、PVC Pending、DNS error、admission webhook error、deprecated API requests の alert を作る。
- Rollback / node drain / storage attach issue / DNS incident / admission outage / registry outage の runbook を整備する。

**Week 7–8: Automation and enforcement**

- CI/CD で manifest validation、schema validation、policy-as-code、image digest check、securityContext check、Secret misuse check を実行する。
- Admission で high-risk violations を audit → warn → enforce の順に移行する。
- Version upgrade / deprecation management の calendar と canary node pool を作る。

### 12.2 Required Documents

| Document | Purpose | Minimum Sections |
|---|---|---|
| Cluster Architecture Spec | control/data plane と extension contract を定義する。 | version, runtime, CNI, CSI, ingress/gateway, registry, admission, metrics |
| Namespace Onboarding Spec | tenant boundary と governance を定義する。 | owner, quota, RBAC, PSS, NetworkPolicy, labels, cost |
| Workload Readiness Checklist | app production gate を定義する。 | image, PodSpec, resources, probes, Service, HPA, Secret, rollback |
| Image Supply Chain Policy | build-to-run の artifact control を定義する。 | base image, scan, digest, signing, SBOM, registry, retention |
| Storage Policy | persistent data の contract を定義する。 | StorageClass, PVC, reclaim, backup, snapshot, topology |
| Network Policy Baseline | traffic permission の default を定義する。 | default deny, namespace egress, ingress, DNS, exceptions |
| Control Plane SLO | cluster decision plane の信頼性を定義する。 | API latency, etcd, scheduler, admission, controller queues |
| Exception Register | privileged / host access / broad RBAC の例外を追跡する。 | request, rationale, risk, approver, expiry, compensating control |

### 12.3 Minimum Viable Controls

- Production namespace は PSS `baseline` 以上、security-sensitive namespace は `restricted` を標準。
- Production Deployment は digest-pinned image、readiness/liveness/startup probe、requests/limits、securityContext、rollback policy を必須。
- Production Service は NetworkPolicy と paired review。
- Production Secret は Secret object のみでは不十分。RBAC、encryption at rest、rotation、access audit を必須。
- Production PVC は StorageClass、backup/snapshot、reclaimPolicy を review。
- HPA は metric source と min/max を定義し、scale-down behavior を review。
- CronJob は idempotency、concurrencyPolicy、deadline を必須。
- Control plane と admission webhook は application SLO と同じ運用重要度で監視。

---

## 13. Layer-by-layer Clone Specs

### 17.01 Container Image

- **Definition**: runtime に渡される filesystem/config/metadata artifact。
- **Decision model**: base image、digest、tag、registry、signature、SBOM、scan threshold、pull policy を決める。
- **Clone spec**: production manifest は digest を pin し、scan / signature / attestation を digest に関連付ける。base image update と vulnerability remediation を release process に組み込む。
- **Metrics**: unsigned image rate、critical CVE count、digest coverage、pull failure、image size。
- **Failure / anti-pattern**: mutable tag-only deployment、unscanned base image、registry credential expiry。
- **Sources**: [K8S-IMAGES], [OCI-OVERVIEW], [OCI-IMAGE-DIST-11]

### 17.02 Image Layer

- **Definition**: image を構成する filesystem diff と build cache unit。
- **Decision model**: OS layer、runtime layer、dependency layer、application layer、metadata layer の分離を決める。
- **Clone spec**: stable dependency を前段、頻繁に変わる app layer を後段にし、unnecessary package / secret / build tool を final image から除外する。
- **Metrics**: layer count、image size、rebuild time、vulnerable packages、cache hit。
- **Failure / anti-pattern**: build secret の layer 残存、巨大 image、debug tools の本番残留。
- **Sources**: [OCI-OVERVIEW], [K8S-IMAGES]

### 17.03 Registry / Distribution

- **Definition**: image / artifact の storage、distribution、lookup、access control。
- **Decision model**: allowed registries、repository ownership、retention、replication、immutability、credentials を決める。
- **Clone spec**: registry namespace を app/team/environment で分け、promotion を digest based にする。OCI referrers 対応なら SBOM/signature を image digest に付与する。
- **Metrics**: pull success、pull latency、retention violation、replication lag、credential failures。
- **Failure / anti-pattern**: public registry 直 pull、unbounded retention、artifact provenance 不明。
- **Sources**: [OCI-SPECS], [OCI-IMAGE-DIST-11], [K8S-IMAGES]

### 17.04 OCI Runtime

- **Definition**: OCI bundle を process として起動する low-level runtime。
- **Decision model**: runtime implementation、seccomp、capabilities、cgroup、namespaces、rootless/userns support を決める。
- **Clone spec**: runtime support matrix を Kubernetes version / node OS / cgroup v2 / security profile と紐付け、RuntimeClass で特殊 runtime を分離する。
- **Metrics**: runtime create/start latency、sandbox errors、security profile violations。
- **Failure / anti-pattern**: privileged runtime default、runtime upgrade without node canary。
- **Sources**: [OCI-RUNTIME-11], [K8S-RUNTIMES]

### 17.05 Kubernetes CRI Runtime

- **Definition**: kubelet と runtime の gRPC 境界。
- **Decision model**: containerd / CRI-O version、CRI v1 support、image lifecycle、Pod sandbox lifecycle を決める。
- **Clone spec**: kubelet/runtime compatibility を upgrade gate にし、node registration / sandbox creation / image pull を conformance test に含める。
- **Metrics**: CRI errors、node registration failures、sandbox creation latency、runtime restarts。
- **Failure / anti-pattern**: CRI API mismatch、dockershim-era assumptions、runtime config drift。
- **Sources**: [K8S-CRI], [K8S-RUNTIMES]

### 17.06 Namespace Isolation

- **Definition**: Kubernetes namespace と Linux namespace による可視性・権限境界。
- **Decision model**: tenant namespace、host namespace exception、user namespace、quota、PSS、RBAC を決める。
- **Clone spec**: namespace は owner/quota/PSS/RBAC/NetworkPolicy/cost の bundle として作成する。hostNetwork/hostPID/hostIPC は exception-only。
- **Metrics**: namespaces without owner/quota/PSS、host namespace pods、PSS violations。
- **Failure / anti-pattern**: default namespace production、namespace sprawl、policy-less namespace。
- **Sources**: [K8S-NAMESPACES], [LINUX-NS], [K8S-USERNS], [K8S-PSS-LABELS]

### 17.07 cgroups / Resource Isolation

- **Definition**: CPU/memory/I/O 等の resource accounting と制限。
- **Decision model**: requests/limits、QoS、cgroup version、cgroup driver、node allocatable、eviction threshold を決める。
- **Clone spec**: kubelet と runtime の cgroup driver を統一し、requests/limits と node allocatable を capacity model に入れる。
- **Metrics**: OOMKilled、CPU throttling、PSI、NodePressure、evictions、allocatable utilization。
- **Failure / anti-pattern**: no requests、wrong limits、driver mismatch、overcommit without SLO。
- **Sources**: [KERNEL-CGROUP-V2], [K8S-RUNTIMES], [K8S-SYSTEM-METRICS]

### 17.08 Kubernetes Network / CNI

- **Definition**: Pod/Service/Node の IP 接続と plugin implementation。
- **Decision model**: CIDR、dual-stack、CNI、routing、overlay/underlay、encryption、network observability を決める。
- **Clone spec**: CNI capability matrix を作り、NetworkPolicy support、upgrade path、failure mode を production gate に入れる。
- **Metrics**: CNI errors、pod sandbox network failures、packet drops、node-to-pod latency。
- **Failure / anti-pattern**: CIDR overlap、plugin capability mismatch、network debug observability 欠落。
- **Sources**: [K8S-NETWORKING], [CNI]

### 17.09 NetworkPolicy / DNS / Service Discovery

- **Definition**: Pod traffic permission と service discovery。
- **Decision model**: default-deny、namespace egress、DNS、service naming、policy ownership を決める。
- **Clone spec**: namespace baseline として default deny を入れ、DNS / kube-apiserver / external dependencies への明示 egress を定義する。
- **Metrics**: policy coverage、denied flows、DNS latency、CoreDNS errors。
- **Failure / anti-pattern**: NetworkPolicy no-op、Service DNS ではなく Pod IP 直接依存。
- **Sources**: [K8S-NETPOL], [K8S-DNS], [COREDNS]

### 17.10 Volume / Ephemeral Storage

- **Definition**: Pod 内の ephemeral / shared / projected data。
- **Decision model**: emptyDir、projected、config/secret volume、hostPath exception、ephemeral storage limit を決める。
- **Clone spec**: transient data は explicit volume として定義し、hostPath は exception-only。ephemeral storage requests/limits を capacity model に入れる。
- **Metrics**: ephemeral storage usage、volume mount errors、evictions。
- **Failure / anti-pattern**: hostPath abuse、ephemeral data を durable と誤認。
- **Sources**: [K8S-VOLUMES]

### 17.11 PV / PVC / CSI / StorageClass

- **Definition**: persistent storage の供給・消費・provisioning。
- **Decision model**: StorageClass、provisioner、access mode、reclaimPolicy、topology、snapshot/backup を決める。
- **Clone spec**: app owner は PVC を要求し、storage owner は StorageClass と CSI driver を管理する。backup/restore runbook を production gate にする。
- **Metrics**: PVC Pending、attach/mount latency、backup success、orphan volumes。
- **Failure / anti-pattern**: default StorageClass misuse、reclaimPolicy data loss、topology mismatch。
- **Sources**: [K8S-PV], [K8S-DYNAMIC], [K8S-STORAGECLASS], [CSI-K8S], [CSI-SPEC]

### 17.12 Pod

- **Definition**: Kubernetes の最小 deployable unit、containers の shared context。
- **Decision model**: containers、init/sidecar、resources、probes、securityContext、restartPolicy、volumes を決める。
- **Clone spec**: one-container-per-Pod を標準とし、multi-container Pod は tight coupling の理由を文書化する。production は controller-managed object で運用する。
- **Metrics**: PodReady、restarts、CrashLoopBackOff、probe failures。
- **Failure / anti-pattern**: naked Pod production、sidecar resource 無設定、probe 不備。
- **Sources**: [K8S-PODS]

### 17.13 Node / kubelet

- **Definition**: workload を実行する host と node agent。
- **Decision model**: node pool、labels/taints、kubelet config、runtime、OS/kernel、capacity、cordon/drain policy を決める。
- **Clone spec**: node pool は workload class と isolation requirement で分け、kubelet / runtime / CNI / CSI / kernel compatibility を管理する。
- **Metrics**: NodeReady、kubelet errors、allocatable usage、node pressure、drain duration。
- **Failure / anti-pattern**: mixed workload without taints、manual node mutation、untracked kubelet config drift。
- **Sources**: [K8S-NODES], [K8S-KUBELET], [K8S-RUNTIMES]

### 17.14 Cluster / API Object Model

- **Definition**: cluster state の API representation と object lifecycle。
- **Decision model**: object model、API version、CRDs、schema、namespace、RBAC、deprecation を決める。
- **Clone spec**: object は desired state contract として扱い、schema validation、deprecation monitoring、API latency SLO を定義する。
- **Metrics**: deprecated API requests、API latency、object count、admission rejection。
- **Failure / anti-pattern**: unmanaged CRDs、deprecated API remaining、object status 未監視。
- **Sources**: [K8S-OBJECTS], [K8S-API], [K8S-METRICS]

### 17.15 Deployment / ReplicaSet / Rollout

- **Definition**: stateless workload の declared replica と update lifecycle。
- **Decision model**: replicas、strategy、maxSurge/maxUnavailable、readiness、rollback、revision history を決める。
- **Clone spec**: readiness probe と progressDeadlineSeconds を rollout gate にし、bad rollout は automatic rollback または rapid manual rollback 可能にする。
- **Metrics**: rollout duration、available replicas、unavailable pods、rollback count。
- **Failure / anti-pattern**: readiness 無し rollout、surge/availability mismatch、manual kubectl patch。
- **Sources**: [K8S-DEPLOYMENT]

### 17.16 Service

- **Definition**: Pod 群への stable network abstraction。
- **Decision model**: selector、port、type、EndpointSlice、session affinity、external exposure を決める。
- **Clone spec**: client は Service DNS に依存し、Pod IP 直接依存は禁止。selector correctness と endpoint availability を監視する。
- **Metrics**: endpoint count、connection failures、service latency、empty endpoint duration。
- **Failure / anti-pattern**: selector mismatch、empty endpoint、NodePort sprawl。
- **Sources**: [K8S-SERVICE], [K8S-DNS]

### 17.17 Ingress / Gateway

- **Definition**: cluster 外からの HTTP(S) / L4-L7 routing。
- **Decision model**: Ingress vs Gateway、GatewayClass、Route ownership、TLS、policy、load balancer を決める。
- **Clone spec**: new L7 platform design は Gateway API を優先し、infra owner は Gateway/GatewayClass、app owner は HTTPRoute を管理する。
- **Metrics**: 5xx、route conflicts、TLS expiry、controller reconciliation errors。
- **Failure / anti-pattern**: Ingress controller drift、TLS ownership 不明、route shadowing。
- **Sources**: [K8S-INGRESS], [GATEWAY-API]

### 17.18 ConfigMap / Config

- **Definition**: non-confidential config の Kubernetes object。
- **Decision model**: config source、namespace、immutability、env/file/arg injection、rollout trigger を決める。
- **Clone spec**: Secret と分離し、ConfigMap は 1 MiB 制約内で使う。production config change は rollout / restart / reload のいずれで反映されるかを明記する。
- **Metrics**: invalid config、config drift、rollout failures due to config。
- **Failure / anti-pattern**: credential in ConfigMap、large config、change without rollout plan。
- **Sources**: [K8S-CONFIGMAP]

### 17.19 Secret / Encryption

- **Definition**: confidential data の Kubernetes object と保護 controls。
- **Decision model**: Secret type、encryption at rest、RBAC、mount mode、rotation、immutability、external secret integration を決める。
- **Clone spec**: etcd encryption provider config を確認し、secret access を RBAC/audit で最小化する。long-lived secret は rotation deadline を持つ。
- **Metrics**: secret age、broad RBAC bindings、unencrypted etcd risk、access anomalies。
- **Failure / anti-pattern**: base64 を暗号化と誤認、env var leak、secret in logs/git。
- **Sources**: [K8S-SECRET], [K8S-ENCRYPTION]

### 17.20 Job / CronJob

- **Definition**: finite / scheduled workload execution。
- **Decision model**: completions、parallelism、deadline、backoff、schedule、concurrency、idempotency を決める。
- **Clone spec**: task は duplicate / missed schedule に耐えるよう idempotent にし、deadline と history retention を設定する。
- **Metrics**: failed Jobs、missed schedules、duration、duplicate runs、deadline exceeded。
- **Failure / anti-pattern**: non-idempotent CronJob、unbounded failed Jobs、no deadline。
- **Sources**: [K8S-JOB], [K8S-CRONJOB]

### 17.21 Autoscaler

- **Definition**: workload replica / capacity の自動調整。
- **Decision model**: metric、target、min/max、scale behavior、stabilization、custom metrics を決める。
- **Clone spec**: HPA は resource requests と metric pipeline を prerequisite にし、scale down stabilization と SLO impact を review する。
- **Metrics**: desired/current replicas、metric unavailable、scale event rate、saturation。
- **Failure / anti-pattern**: no requests with HPA、wrong metric、oscillation、scale-to-zero without readiness。
- **Sources**: [K8S-HPA], [K8S-SYSTEM-METRICS]

### 17.22 Scheduler

- **Definition**: Pod を Node に配置する decision system。
- **Decision model**: profiles、plugins、queueing、filtering、scoring、binding、affinity、taints、priority を決める。
- **Clone spec**: scheduler behavior は kube-scheduler config / profiles / extension points で制御し、manual node pinning は例外扱いにする。
- **Metrics**: scheduling latency、unschedulable pods、preemption、resource fit。
- **Failure / anti-pattern**: hard affinity deadlock、over-constrained topology、priority misuse。
- **Sources**: [K8S-SCHED-FW], [K8S-SCHED-CONFIG]

### 17.23 Control Plane

- **Definition**: cluster desired state を保存・検証・収束させる decision plane。
- **Decision model**: API server、etcd、controller manager、scheduler、admission、audit、HA、backup を決める。
- **Clone spec**: API server / etcd / admission は workload deployment SLO の前提として監視し、etcd backup / restore drill と API deprecation monitoring を運用する。
- **Metrics**: API latency、etcd request latency、admission latency、controller queue、deprecated API requests。
- **Failure / anti-pattern**: single control plane、admission webhook SPOF、backup untested。
- **Sources**: [K8S-COMPONENTS], [K8S-APISERVER], [K8S-METRICS]

### 17.24 Data Plane

- **Definition**: node 上で workload traffic/storage/runtime を実行する plane。
- **Decision model**: node OS、kubelet、runtime、CNI、CSI、kube-proxy/replacement、node pool、observability を決める。
- **Clone spec**: data plane は workload class ごとに node pool 分離し、kubelet/runtime/CNI/CSI の health を統合 monitor する。
- **Metrics**: NodeReady、PodReady、runtime errors、CNI errors、CSI mount errors、packet drops。
- **Failure / anti-pattern**: node drift、plugin upgrade without canary、unobserved kubelet/runtime errors。
- **Sources**: [K8S-COMPONENTS], [K8S-NODES], [K8S-KUBELET], [K8S-RUNTIMES], [K8S-NETWORKING], [CSI-K8S]

---

## 14. Historical Changes / Directional Shifts

| Change | Direction | Impact | Sources |
|---|---|---|---|
| Kubernetes CRI v1 required since v1.26 | runtime boundary hardening | runtime version compatibility が upgrade gate になった。 | [K8S-CRI], [K8S-RUNTIMES] |
| OCI Image / Distribution v1.1 added artifact / referrers support | supply chain metadata integration | signatures / attestations / SBOM を registry artifact として扱いやすくなった。 | [OCI-IMAGE-DIST-11] |
| OCI Runtime Spec v1.1 added cgroup v2 support | modern Linux resource control | cgroup v2 対応 runtime が node design に影響する。 | [OCI-RUNTIME-11] |
| CSI became GA in Kubernetes v1.13 | storage interface stabilization | storage vendor integration は Kubernetes core 変更ではなく CSI driver で行う。 | [CSI-K8S] |
| Ingress API frozen; Gateway API recommended | edge API modernization | L7 routing の新機能と role separation は Gateway API に寄る。 | [K8S-INGRESS], [GATEWAY-API] |
| Pod Security Admission GA since v1.25 | namespace-level pod hardening | PSS enforcement/audit/warn labels が namespace governance の基礎になる。 | [K8S-PSS-LABELS] |
| User namespaces stable in Kubernetes v1.36 | root-in-container risk reduction | host user ID との分離が一般 workload isolation に使いやすくなった。 | [K8S-USERNS] |
| Scheduler framework stable since v1.19 and QueueingHint stable v1.34 | scheduler extensibility | custom scheduling は patch ではなく plugin/profile に寄る。 | [K8S-SCHED-FW], [K8S-SCHED-CONFIG] |
| Kubernetes metrics lifecycle formalized | metrics as contract | stable/beta/alpha/deprecated metrics を dashboard / alert lifecycle に反映する。 | [K8S-METRICS], [K8S-SYSTEM-METRICS] |

---

## 15. Validation Queries

RESEARCH.md の反証検索方針に沿って、主要 claim を崩しに行く query を明示する。

| Query | Target Claim | Purpose |
|---|---|---|
| `site:kubernetes.io/docs "CRI v1" "node won't register"` | C-006 | CRI v1 requirement の現行性を確認する。 |
| `site:kubernetes.io/docs "cgroup driver" "changing" "joined"` | C-009 | cgroup driver 変更リスクを確認する。 |
| `site:kubernetes.io/docs "ImagePullBackOff" "300 seconds"` | image failure controls | image pull backoff の具体制約を確認する。 |
| `site:kubernetes.io/docs "NetworkPolicy" "no effect" CNI` | C-012 | NetworkPolicy no-op 条件を確認する。 |
| `site:kubernetes.io/docs "Secret" "etcd" "plaintext"` | C-021 | Secret encryption の既定動作を確認する。 |
| `site:kubernetes.io/docs "Ingress" "frozen" "Gateway API"` | C-019 | Ingress/Gateway の現行推奨を確認する。 |
| `site:kubernetes.io/docs "CronJob" "idempotent"` | C-022 | CronJob duplicate/missed schedule risk を確認する。 |
| `site:kubernetes.io/docs "HorizontalPodAutoscaler" "15 seconds"` | C-023 | HPA sync interval の既定値を確認する。 |
| `site:kubernetes.io/docs "scheduler framework" "scheduling cycle" "binding cycle"` | C-024 | scheduler plugin architecture の現行性を確認する。 |
| `site:opencontainers.org "Image Specification v1.1" "referrers"` | C-005 | OCI artifacts/referrers support を確認する。 |
| `site:man7.org "namespaces" "cgroup" "network"` | C-007 | Linux namespace 分類を確認する。 |
| `site:kernel.org "cgroup v2" "cgroup namespace"` | C-008 | cgroup namespace behavior を確認する。 |

---

## 16. Confidence & Unknowns

### Confidence A

- Kubernetes control plane / node component split。
- Kubernetes object desired/current state model。
- OCI Image / Runtime / Distribution の specification family。
- Kubernetes CRI v1 requirement と runtime compatibility。
- Linux namespaces / cgroups の kernel-level isolation / resource control。
- Pod、Deployment、Service、Ingress、ConfigMap、Secret、Job、CronJob、HPA、Scheduler の公式 behavior。
- NetworkPolicy の plugin dependency。
- PV/PVC/StorageClass/CSI の storage abstraction。
- Component metrics と Prometheus format。

### Confidence B

- Gateway API を新規 L7 platform design の優先候補にするべきという運用判断。根拠は Ingress freeze と Gateway API の official positioning だが、組織の既存 controller / cloud integration により例外がある。
- production で digest pinning / signing / SBOM / admission を標準にする判断。根拠は OCI artifact support と Kubernetes image digest semantics だが、具体ツールは組織依存。
- namespace を tenancy / governance bundle として扱う判断。根拠は Kubernetes namespace、PSS、NetworkPolicy、quota の公式機能だが、multi-tenancy level は組織依存。

### Confidence C / Unknowns

- 各 managed Kubernetes provider（EKS/GKE/AKS 等）の現在の default CNI / CSI / Gateway / Secret encryption 設定は、本レポートでは provider-specific に検証していない。
- private registry の exact policy、signature tool、SBOM format、admission controller 実装は組織選定が必要。
- sandboxed runtime（Kata Containers、gVisor 等）の採用判断は workload risk / performance / cloud support に依存する。
- service mesh の採否は本レイヤー範囲では補助要素として扱い、独立した調査対象にするべきである。
- VPA / Cluster Autoscaler / Karpenter 等の autoscaler ecosystem は HPA 以外も重要だが、本レポートでは Kubernetes 公式 HPA と scheduler を中心にした。

---

## 17. Source Catalog

| ID | Source | Tier | URL | Notes |
|---|---|---:|---|---|
| K8S-OVERVIEW | Kubernetes Documentation Overview | T0 | https://kubernetes.io/docs/concepts/overview/ | Kubernetes の公式 overview。 |
| K8S-COMPONENTS | Kubernetes Components | T0 | https://kubernetes.io/docs/concepts/overview/components/ | control plane と node components。 |
| K8S-API | Kubernetes API | T0 | https://kubernetes.io/docs/concepts/overview/kubernetes-api/ | API server / OpenAPI / API discovery。 |
| K8S-APISERVER | kube-apiserver reference | T0 | https://kubernetes.io/docs/reference/command-line-tools-reference/kube-apiserver/ | API server の役割。 |
| K8S-OBJECTS | Kubernetes Objects | T0 | https://kubernetes.io/docs/concepts/overview/working-with-objects/ | spec/status desired state model。 |
| K8S-CONTROLLERS | Controllers | T0 | https://kubernetes.io/docs/concepts/architecture/controller/ | reconciliation / control loop。 |
| OCI-SPECS | Open Container Initiative specs | T0 | https://opencontainers.org/ | current OCI spec family。 |
| OCI-OVERVIEW | OCI Overview | T0 | https://opencontainers.org/about/overview/ | Runtime / Image / Distribution overview。 |
| OCI-IMAGE-DIST-11 | OCI Image and Distribution v1.1 release | T0 | https://opencontainers.org/posts/blog/2024-05-07-image-and-distribution-1-1/ | artifacts / referrers support。 |
| OCI-RUNTIME-11 | OCI Runtime Spec v1.1 release | T0 | https://opencontainers.org/posts/blog/2023-07-21-oci-runtime-spec-v1-1/ | low-level runtime / cgroup v2 support。 |
| K8S-IMAGES | Kubernetes Images | T0 | https://kubernetes.io/docs/concepts/containers/images/ | tags, digests, pull policy, ImagePullBackOff。 |
| K8S-CRI | Container Runtime Interface | T0 | https://kubernetes.io/docs/concepts/architecture/cri/ | kubelet-runtime gRPC / CRI v1。 |
| K8S-RUNTIMES | Container Runtimes | T0 | https://kubernetes.io/docs/setup/production-environment/container-runtimes/ | CRI runtime, cgroup driver, compatibility。 |
| LINUX-NS | Linux namespaces man page | T0 | https://man7.org/linux/man-pages/man7/namespaces.7.html | namespace types and container use。 |
| KERNEL-CGROUP-V2 | Linux kernel cgroup v2 docs | T0 | https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html | cgroup v2 / cgroup namespace。 |
| K8S-USERNS | Kubernetes User Namespaces | T0 | https://kubernetes.io/docs/concepts/workloads/pods/user-namespaces/ | user namespace isolation and constraints。 |
| K8S-NAMESPACES | Kubernetes Namespaces | T0 | https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/ | namespace isolation / quota。 |
| K8S-PODS | Kubernetes Pods | T0 | https://kubernetes.io/docs/concepts/workloads/pods/ | smallest deployable unit / shared context。 |
| K8S-NETWORKING | Cluster Networking | T0 | https://kubernetes.io/docs/concepts/cluster-administration/networking/ | network model, IP ranges, CNI。 |
| CNI | Container Network Interface | T0/T3 | https://github.com/containernetworking/cni | CNI spec / libraries / plugin interface。 |
| K8S-NETPOL | Network Policies | T0 | https://kubernetes.io/docs/concepts/services-networking/network-policies/ | NetworkPolicy semantics and plugin dependency。 |
| K8S-DNS | DNS for Services and Pods | T0 | https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/ | service/pod DNS records。 |
| COREDNS | CoreDNS | T3 | https://coredns.io/ | Kubernetes service discovery plugin ecosystem。 |
| K8S-VOLUMES | Kubernetes Volumes | T0 | https://kubernetes.io/docs/concepts/storage/volumes/ | Pod volumes, ephemeral vs persistent needs。 |
| K8S-PV | Persistent Volumes | T0 | https://kubernetes.io/docs/concepts/storage/persistent-volumes/ | PV/PVC subsystem。 |
| K8S-DYNAMIC | Dynamic Volume Provisioning | T0 | https://kubernetes.io/docs/concepts/storage/dynamic-provisioning/ | PVC-based on-demand provisioning。 |
| K8S-STORAGECLASS | Storage Classes | T0 | https://kubernetes.io/docs/concepts/storage/storage-classes/ | StorageClass fields and defaults。 |
| CSI-K8S | Kubernetes CSI Docs | T0 | https://kubernetes-csi.github.io/docs/ | CSI in Kubernetes / third-party storage plugins。 |
| CSI-SPEC | Container Storage Interface Spec | T0/T3 | https://github.com/container-storage-interface/spec | CSI protobuf/spec repository。 |
| K8S-NODES | Kubernetes Nodes | T0 | https://kubernetes.io/docs/concepts/architecture/nodes/ | node lifecycle / status / labels / cordon。 |
| K8S-KUBELET | kubelet reference | T0 | https://kubernetes.io/docs/reference/command-line-tools-reference/kubelet/ | primary node agent。 |
| K8S-DEPLOYMENT | Deployments | T0 | https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ | rollout / rollback / scaling。 |
| K8S-SERVICE | Services | T0 | https://kubernetes.io/docs/concepts/services-networking/service/ | stable network endpoint abstraction。 |
| K8S-INGRESS | Ingress | T0 | https://kubernetes.io/docs/concepts/services-networking/ingress/ | HTTP routing, frozen API, Gateway recommendation。 |
| GATEWAY-API | Gateway API | T0/T3 | https://gateway-api.sigs.k8s.io/ | role-oriented L4/L7 routing API。 |
| K8S-CONFIGMAP | ConfigMaps | T0 | https://kubernetes.io/docs/concepts/configuration/configmap/ | non-confidential config, 1 MiB limit。 |
| K8S-SECRET | Secrets | T0 | https://kubernetes.io/docs/concepts/configuration/secret/ | secret limits, immutability, imagePullSecrets。 |
| K8S-ENCRYPTION | Encrypting Confidential Data at Rest | T0 | https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/ | etcd encryption provider config。 |
| K8S-JOB | Jobs | T0 | https://kubernetes.io/docs/concepts/workloads/controllers/job/ | one-off tasks, completions, deadlines。 |
| K8S-CRONJOB | CronJobs | T0 | https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/ | schedule, missed/duplicate run considerations。 |
| K8S-HPA | Horizontal Pod Autoscaling | T0 | https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/ | HPA control loop / metrics。 |
| K8S-SCHED-FW | Scheduling Framework | T0 | https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/ | scheduler plugin architecture。 |
| K8S-SCHED-CONFIG | Scheduler Configuration | T0 | https://kubernetes.io/docs/reference/scheduling/config/ | scheduler profiles / plugins。 |
| K8S-METRICS | Kubernetes Metrics Reference | T0 | https://kubernetes.io/docs/reference/instrumentation/metrics/ | component metrics and stable metrics。 |
| K8S-SYSTEM-METRICS | Metrics for System Components | T0 | https://kubernetes.io/docs/concepts/cluster-administration/system-metrics/ | `/metrics`, Prometheus format, metric lifecycle。 |
| NIST-800-190 | NIST SP 800-190 Application Container Security Guide | T0/T1 | https://csrc.nist.gov/pubs/sp/800/190/final | container security guidance。 |
| K8S-PSS | Pod Security Standards | T0 | https://kubernetes.io/docs/concepts/security/pod-security-standards/ | Privileged / Baseline / Restricted policies。 |
| K8S-PSS-LABELS | Enforce Pod Security Standards with Namespace Labels | T0 | https://kubernetes.io/docs/tasks/configure-pod-container/enforce-standards-namespace-labels/ | namespace label based enforcement/audit/warn。 |

---

## 18. Appendix: Minimal `layer_registry.csv` Projection

```csv
layer_id,layer_name_ja,cluster,definition,decision_question,decision_object,default_source_types,output_artifacts,owner_roles,default_metrics
17.01,Container Image,コンテナ・Kubernetes,実行単位として配布される container filesystem/config/metadata,どの image contract で本番実行可能と判断するか,Image artifact contract,"OCI,Kubernetes images,registry docs","image digest,SBOM,signature,scan report","release engineering,platform,security","critical CVE,digest coverage,pull failures"
17.02,Image Layer,コンテナ・Kubernetes,image を構成する filesystem diff と cache unit,layer をどう分割し再現性と攻撃面を制御するか,Layer composition,"OCI image spec,build docs","Dockerfile,build recipe,layer metadata","platform,app owner","image size,rebuild time,vulnerable packages"
17.03,Registry / Distribution,コンテナ・Kubernetes,image/artifact の保管・配布・参照,どの registry policy で配布と証跡を制御するか,Registry control plane,"OCI distribution,registry docs","registry namespace,retention policy,artifact refs","platform,security","pull latency,retention violations"
17.04,OCI Runtime,コンテナ・Kubernetes,OCI bundle execution behavior,どの runtime/security/cgroup contract で実行するか,Runtime execution contract,"OCI runtime,Kubernetes runtime docs","runtime config,RuntimeClass","platform,runtime owner,security","runtime errors,sandbox incidents"
17.05,Kubernetes CRI Runtime,コンテナ・Kubernetes,kubelet-runtime gRPC boundary,kubelet がどの runtime と連携するか,CRI implementation,"Kubernetes CRI,containerd,CRI-O","containerd/CRI-O config,kubelet config","platform,node SRE","node registration failures,CRI latency"
17.06,Namespace Isolation,コンテナ・Kubernetes,Linux/Kubernetes namespaces による分離,どの namespace を共有または分離するか,Namespace boundary,"Linux namespaces,Kubernetes namespaces,PSS","namespace labels,RBAC,quota,NetworkPolicy","security,platform,app owner","PSS violations,host namespace pods"
17.07,cgroups / Resource Isolation,コンテナ・Kubernetes,resource accounting and limits,どの cgroup/requests/limits で resource を制御するか,Resource isolation contract,"kernel cgroups,Kubernetes runtimes","cgroup driver,Pod resources","platform,SRE","OOMKilled,throttling,node pressure"
17.08,Kubernetes Network / CNI,コンテナ・Kubernetes,Pod/Service/Node network model,どの CNI/IP/routing で接続するか,Cluster network model,"Kubernetes networking,CNI","CNI config,CIDR","network,platform","CNI errors,packet drops"
17.09,NetworkPolicy / DNS,コンテナ・Kubernetes,L3/L4 isolation and discovery,どの traffic と DNS を許可するか,Traffic permission contract,"NetworkPolicy,DNS,CoreDNS","NetworkPolicy,DNS config","network,security,app","policy coverage,DNS errors"
17.10,Volume / Ephemeral Storage,コンテナ・Kubernetes,Pod-local storage,どの volume type を ephemeral/config/shared に使うか,Pod storage contract,"Kubernetes volumes","volume specs","app,platform","mount errors,ephemeral usage"
17.11,PV/PVC/CSI/StorageClass,コンテナ・Kubernetes,persistent storage abstraction,どの storage class/provisioner/reclaim policy を使うか,Persistent storage contract,"PV/PVC,CSI,StorageClass","PVC,PV,StorageClass","storage,platform,app","PVC pending,attach latency,backup success"
17.12,Pod,コンテナ・Kubernetes,smallest deployable unit,どの containers を同一 Pod に co-locate するか,PodSpec,"Kubernetes pods","Pod manifest,probes,resources","app,platform","Ready ratio,restarts"
17.13,Node / kubelet,コンテナ・Kubernetes,workload execution host and agent,どの node pool/kubelet/runtime で workload を受けるか,Node execution capacity,"Kubernetes nodes,kubelet","Node object,kubelet config","node SRE,platform","NodeReady,kubelet errors"
17.14,Cluster / API Object Model,コンテナ・Kubernetes,cluster state API model,どの API object/version/schema で state を表すか,API state model,"Kubernetes API,objects,metrics","API objects,CRDs,OpenAPI schema","platform,security","API latency,deprecated API requests"
17.15,Deployment / Rollout,コンテナ・Kubernetes,stateless workload rollout,どの strategy/rollback/scale で更新するか,Rollout contract,"Kubernetes deployments","Deployment,ReplicaSet","app,SRE","rollout duration,unavailable pods"
17.16,Service,コンテナ・Kubernetes,stable endpoint abstraction,どの selector/port/type で公開するか,Stable service endpoint,"Kubernetes services,DNS","Service,EndpointSlice","app,network","endpoint availability,connection failures"
17.17,Ingress / Gateway,コンテナ・Kubernetes,L4/L7 routing,どの route/TLS/policy/ownership で外部公開するか,Edge routing contract,"Ingress,Gateway API","Ingress,Gateway,HTTPRoute","network,security,app","5xx,TLS expiry,route conflicts"
17.18,ConfigMap / Config,コンテナ・Kubernetes,non-confidential config,どの config を image から分離するか,Configuration artifact,"Kubernetes ConfigMaps","ConfigMap,projected volume","app,platform","config drift,invalid config"
17.19,Secret / Encryption,コンテナ・Kubernetes,confidential data handling,どの secret/encryption/rotation/access policy で守るか,Secret handling contract,"Kubernetes Secrets,encryption docs","Secret,encryption config","security,platform,app","secret age,access audit"
17.20,Job / CronJob,コンテナ・Kubernetes,batch and scheduled tasks,どの completion/deadline/retry/idempotency で実行するか,Batch execution contract,"Jobs,CronJobs","Job,CronJob","app,SRE","failed jobs,missed schedules"
17.21,Autoscaler,コンテナ・Kubernetes,automatic scaling decision,どの metric/target/min-max で増減するか,Scaling decision rule,"HPA,metrics","HPA,metrics pipeline","SRE,app,platform","desired/current replicas,scale latency"
17.22,Scheduler,コンテナ・Kubernetes,Pod placement decision,どの plugin/profile/affinity/taint で配置するか,Placement decision system,"scheduler framework,config","scheduler profile,plugins","platform,SRE","scheduling latency,unschedulable pods"
17.23,Control Plane,コンテナ・Kubernetes,cluster decision plane,API/etcd/scheduler/controller をどう HA/secure/observe するか,Cluster decision plane,"components,API,metrics","apiserver,etcd,scheduler,controller-manager","platform SRE,security","API SLO,etcd latency,controller queue"
17.24,Data Plane,コンテナ・Kubernetes,workload execution plane,kubelet/runtime/network/storage がどの node-level contract で実行するか,Workload execution plane,"nodes,kubelet,runtimes,CNI,CSI","node,kubelet,runtime,CNI/CSI","node SRE,network,storage","NodeReady,PodReady,CNI/CSI errors"
```
