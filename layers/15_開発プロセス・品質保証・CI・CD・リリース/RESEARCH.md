# Frontier Operating Model Research: 開発プロセス・品質保証・CI・CD・リリース（Layers 15）

Generated: 2026-05-13  
Scope: source code、repository、branch、commit、PR/MR、code review、static analysis、tests、build、package、artifact、CI/CD、deployment、release、rollback、canary、blue-green、migration、environment、IaC、provisioning、configuration management  
Method: `RESEARCH.md` の Frontier Operating Model Research 運用プレイブックに従い、公開一次情報・公式ドキュメント・標準・OSS公式運用文書・公開インシデントから Decision Model / Operating Model / Clone Spec を再構成した。  
Note: レイヤー 15 の個別名称はユーザー提示のサブテーマから正規化した暫定名である。原 taxonomy の正式名称が別途存在する場合は、ID と名称だけ差し替え、Decision Model は維持できる。

---

## 1. Executive Summary

このレイヤー群の frontier operating model は、単なる「CI/CDツール導入」ではなく、**すべての変更を、追跡可能・レビュー可能・検証可能・証跡付き・段階的・可逆的な単位として扱う変更制御システム**である。

先端組織・先端OSSコミュニティに共通する構造は次の通りである。

1. **Source control is the system of record**: すべての source code、infrastructure code、configuration、deployment intent、release metadata を versioned repository に置き、branch protection、CODEOWNERS、review、status checks、audit trail によって変更権限を制御する。
2. **Change is mediated by PR/MR**: 変更は branch + commit + PR/MR によって小さな論理単位に分解され、reviewer / owner / CI checks / static analysis / tests / security scan が merge 前に判断する。
3. **Build and artifact are separated from source**: release 対象は source tree そのものではなく、CI上で生成された immutable artifact / package / image / release bundle であり、build provenance、digest、release evidence、test report、package registry によって再検証できる。
4. **CI/CD is a policy enforcement surface**: lint、SAST、unit/integration/E2E tests、dependency checks、build、package、deploy、environment protection、manual approval、rollback validation を pipeline-as-code で実行し、例外も証跡化する。
5. **Deployment is progressive and observable**: production change は all-at-once ではなく、environment gating、canary、blue-green、traffic split、metrics analysis、promotion / rollback decision によって blast radius を制御する。
6. **Infrastructure and configuration are declared, not hand-mutated**: Terraform、Kubernetes manifests、GitOps のように desired state を versioned・reviewed・auditable にし、plan / diff / apply / reconciliation / drift detection を運用に組み込む。
7. **Release quality is measured by speed and stability together**: DORA metrics のように lead time、deployment frequency、failed deployment recovery time、change fail rate、deployment rework rate を同時に見る。高速化と安定性はトレードオフではなく、同じ能力の別側面として管理する。

このレイヤー群で模倣すべき中核設計は、**protected trunk + short-lived branches + mandatory PR/MR + automated quality/security gates + isolated build/provenance + immutable artifact + environment-scoped deployment + progressive rollout + tested rollback + DORA-based feedback loop** である。

---

## 2. Source Catalog

| Source ID | Entity / Source | Tier | Source Type | Main Evidence Extracted | URL |
|---|---:|---:|---|---|---|
| R01 | RESEARCH.md | Method | Internal uploaded playbook | Clone Spec、Decision Model、source tier、QA条件、反証検索、A/B confidence の形式 | Uploaded file in current conversation |
| S01 | NIST SP 800-218 Secure Software Development Framework | T0 | Standard / official guidance | secure development practices, SDLC integration, vulnerability reduction, common vocabulary | https://csrc.nist.gov/pubs/sp/800/218/final |
| S02 | SLSA v1.2 Specification | T0 | Standard / supply-chain framework | source/build tracks, provenance, build isolation, trusted control plane, source history and code review levels | https://slsa.dev/spec/v1.2/ |
| S03 | OpenSSF SCM Best Practices | T0/T3 | Security best practices | SCM access controls, CI/CD workflow permissions, read-only tokens, trusted actions | https://best.openssf.org/SCM-BestPractices/ |
| S04 | OpenSSF Scorecard | T5 | External validation / benchmark | CI tests, SAST, branch protection, code review, pinned dependencies, signed releases, token permissions | https://scorecard.dev/ |
| S05 | GitHub Protected Branches | T2/T3 | Platform official docs | required PR reviews, status checks, signed commits, linear history, merge queue, deployment checks, no-force-push | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches |
| S06 | GitHub Pull Request Reviews | T3 | Platform official docs | review comments, approvals, request changes, required approvals before merge | https://docs.github.com/articles/about-pull-request-reviews |
| S07 | GitHub Actions Workflow Syntax | T2/T3 | Platform official docs | workflow as YAML-configured automated process with jobs | https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax |
| S08 | GitHub Deployments and Environments | T2/T3 | Platform official docs | environment protection rules, approvals, wait timers, branch/tag restrictions, custom deployment protection | https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments |
| S09 | GitHub Code Scanning in Pull Requests | T2/T3 | Platform official docs | code scanning alerts in PR, severity-based failure of checks | https://docs.github.com/en/code-security/how-tos/manage-security-alerts/manage-code-scanning-alerts/triaging-code-scanning-alerts-in-pull-requests |
| S10 | GitHub Workflow Artifacts | T2 | Platform official docs | artifacts produced by workflow runs; persistent build/test output | https://docs.github.com/actions/using-workflows/storing-workflow-data-as-artifacts |
| S11 | GitHub Releases | T2/T3 | Platform official docs | releases are deployable software iterations based on Git tags | https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases |
| S12 | GitHub Packages | T2 | Platform official docs | package registry, linked source/build/deployment history | https://docs.github.com/en/packages/learn-github-packages/introduction-to-github-packages |
| S13 | GitLab CI/CD Pipelines | T2/T3 | Platform official docs | pipeline as `.gitlab-ci.yml`, jobs/stages, sequential/parallel execution | https://docs.gitlab.com/ci/pipelines/ |
| S14 | GitLab Protected Branches | T2/T3 | Platform official docs | merge/push permissions, production branch protection, Code Owner approval, MR approval | https://docs.gitlab.com/user/project/repository/branches/protected/ |
| S15 | GitLab Code Quality | T2/T3 | Platform official docs | code quality report in MR widget, pipeline artifacts, severity schema | https://docs.gitlab.com/ci/testing/code_quality/ |
| S16 | GitLab Job Artifacts | T2 | Platform official docs | job outputs and reports attached to jobs; later jobs can fetch artifacts | https://docs.gitlab.com/ci/jobs/job_artifacts/ |
| S17 | GitLab Releases | T2/T3 | Platform official docs | release packages code, binaries, docs, release notes, tags, CI release job | https://docs.gitlab.com/user/project/releases/ |
| S18 | GitLab Release Evidence | T2/T3 | Platform official docs | release evidence snapshot includes test artifacts, packages, milestones, links | https://docs.gitlab.com/user/project/releases/release_evidence/ |
| S19 | GitLab Environments | T2/T3 | Platform official docs | deployment target tracking, rollback, protected environments, variables, monitoring | https://docs.gitlab.com/ci/environments/ |
| S20 | GitLab Deployments | T2/T3 | Platform official docs | rollback creates new deployment with its own job ID; retry and rollback behavior | https://docs.gitlab.com/ci/environments/deployments/ |
| S21 | GitLab CI/CD Variables | T2/T3 | Platform official docs | environment-scoped variables and sensitive variable restrictions | https://docs.gitlab.com/ci/variables/ |
| S22 | Linux Kernel Submitting Patches | T3 | OSS official process docs | small logical patches, problem description, maintainer workflow, Reviewed-by/Tested-by tags | https://docs.kernel.org/process/submitting-patches.html |
| S23 | Linux Kernel Maintainer Entry Profile | T3 | OSS official process docs | local maintainer customs, branch information, CI, checklists | https://docs.kernel.org/maintainer/maintainer-entry-profile.html |
| S24 | Linux Kernel Development Process | T3 | OSS official process docs | rolling release cadence, merge window, weekly rc stabilization until stable | https://docs.kernel.org/process/development-process.html |
| S25 | Kubernetes Deployment | T0/T2 | Platform / official docs | desired state, rolling updates, rollback, revision history, progress deadline, maxUnavailable/maxSurge | https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ |
| S26 | Argo Rollouts | T2/T3 | Progressive delivery official docs | canary, blue-green, traffic shifting, metric analysis, auto rollback/promotion | https://argoproj.github.io/rollouts/ |
| S27 | Google SRE Workbook: Canarying Releases | T3 | SRE official practice | small traffic subset, compare canary/control, mitigate release risk before full production | https://sre.google/workbook/canarying-releases/ |
| S28 | Google SRE Book: Reliable Product Launches at Scale | T3 | SRE official practice | assume releases contain bugs; canarying prevents impact and supports recovery | https://sre.google/sre-book/reliable-product-launches/ |
| S29 | DORA Metrics Guide | T5 | Benchmark / research guidance | change lead time, deployment frequency, failed deployment recovery time, change fail rate, deployment rework rate | https://dora.dev/guides/dora-metrics/ |
| S30 | OpenGitOps Principles | T0/T3 | Standard / official principles | declarative desired state, versioned immutable state, automatic pull/reconciliation | https://opengitops.dev/ |
| S31 | Terraform Documentation | T2/T3 | IaC official docs | build/change/version infrastructure safely and efficiently | https://developer.hashicorp.com/terraform/docs |
| S32 | Terraform Plan | T2/T3 | IaC official docs | preview changes, compare config/state, speculative plan for review | https://developer.hashicorp.com/terraform/cli/commands/plan |
| S33 | Terraform Apply | T2/T3 | IaC official docs | execute proposed plan; saved plan mode for reviewed execution | https://developer.hashicorp.com/terraform/cli/commands/apply |
| S34 | Twelve-Factor App: Config | T0/T3 | Method / operating principle | deploy-varying config in environment, avoid checking config into code, no named grouped environments | https://12factor.net/config |
| S35 | Kubernetes ConfigMap | T2/T3 | Platform official docs | non-confidential key-values, decouple environment config from image, use Secrets for confidential data | https://kubernetes.io/docs/concepts/configuration/configmap/ |
| F01 | GitLab.com 2017 Database Incident Postmortem | T5 | Incident / failure evidence | destructive database operation, backup verification failures, restoration delays | https://about.gitlab.com/blog/gitlab-dot-com-database-incident/ |
| F02 | Atlassian April 2022 Outage Post-Incident Review | T5 | Incident / failure evidence | script validation gap, production deletion scope, prolonged customer impact | https://www.atlassian.com/blog/announcements/post-incident-review-april-2022-outage |
| F03 | GitHub October 2018 Post-Incident Analysis | T5 | Incident / failure evidence | network maintenance chain, replication/topology recovery gaps, prolonged degraded service | https://github.blog/news-insights/company-news/oct21-post-incident-analysis/ |

---

## 3. Layer Registry: 15

| Layer ID | Layer Name JA | Decision Object | Output Artifacts | Primary Owners | Default Metrics |
|---:|---|---|---|---|---|
| 15.01 | ソースコード管理 | 何を source of truth として version 管理するか | repository, source tree, history, tags | Engineering Manager, Tech Lead, Maintainer | repository coverage, untracked change count, signed history coverage |
| 15.02 | リポジトリ構造 | mono-repo / multi-repo / service repo / infra repo の境界 | repo map, ownership map, CODEOWNERS | Platform Lead, Architecture Lead | dependency clarity, owner coverage, cross-repo change latency |
| 15.03 | ブランチ戦略 | trunk, release branch, feature branch, protected branch の運用 | branch policy, protection rules, merge queue | Maintainer, Release Manager | branch lifetime, direct-push violations, stale branches |
| 15.04 | コミット規律 | commit をどの粒度・形式・署名・説明で残すか | commit log, trailers, signed commits | Developer, Maintainer | commit revertability, signed commit ratio, patch size |
| 15.05 | PR/MR運用 | 変更をどの単位で review / merge するか | PR/MR, description, checklist, linked issue | Developer, Reviewer | PR cycle time, review latency, rework rate |
| 15.06 | Code Owners / 承認権限 | 誰が merge / release / deploy を承認できるか | CODEOWNERS, approval matrix | Code Owner, Security, SRE | owner coverage, approval bypasses |
| 15.07 | コードレビュー | 何を技術レビューし、どの条件で merge 可とするか | review comments, approvals, Reviewed-by | Reviewer, Maintainer | review depth, defects escaped, requested-change ratio |
| 15.08 | 静的解析 / SAST | merge 前に検出すべき品質・脆弱性リスク | code scanning report, SAST alerts | AppSec, Developer | high/critical open alerts, false-positive rate |
| 15.09 | テスト設計 | どのリスクをどの test layer で検証するか | test plan, test cases, fixtures | QA Lead, Developer | risk coverage, flaky test rate, mutation/coverage indicators |
| 15.10 | CIテスト自動化 | どの tests をどの event で自動実行するか | CI jobs, test reports, coverage reports | Platform, QA, Developers | pass rate, queue time, failed check escape rate |
| 15.11 | ビルド設計 | source から artifact をどう生成するか | build script, build logs, container image | Build Platform Owner | build success rate, reproducibility, duration |
| 15.12 | ビルド再現性・プロベナンス | artifact がどこで・どう生成されたかを証明するか | provenance, digest, attestation | Supply Chain Security, Build Owner | provenance coverage, rebuild verification rate |
| 15.13 | パッケージ管理 | artifact をどの registry / version / dependency policy で扱うか | package, dependency lock, registry record | Package Owner, Platform | dependency freshness, pinned dependency ratio |
| 15.14 | アーティファクト管理 | build/test/release outputs をどう保存・共有・検証するか | job artifact, report, SBOM/attestation where applicable | CI Owner, Release Manager | artifact retention compliance, digest verification |
| 15.15 | サプライチェーンセキュリティ | source-to-release chain の信頼境界をどう確保するか | SLSA controls, Scorecard checks, signatures | Security, Platform | SLSA level, Scorecard score, signed releases |
| 15.16 | CI/CDパイプライン | jobs/stages/gates をどの順序で実行するか | workflow YAML, pipeline DAG | Platform Engineering | deployment frequency, pipeline duration, failure rate |
| 15.17 | パイプライン権限・シークレット | CI token、secrets、workflow permissions をどう制限するか | token policy, secrets scopes | Security, Platform | secret exposure incidents, token privilege violations |
| 15.18 | デプロイ設計 | artifact をどの target にどう反映するか | deployment record, rollout spec | SRE, Release Manager | deploy success rate, failed deployment recovery time |
| 15.19 | 環境管理 | dev/staging/prod/ephemeral をどう分離・保護するか | environment registry, environment gates | SRE, Platform | environment drift, approval SLA, protected env violations |
| 15.20 | 構成管理 | config を code / env / secret / runtime のどこで管理するか | config map, env vars, secrets, config schema | Platform, Security | config drift, secret leakage, misconfiguration incidents |
| 15.21 | IaC | infrastructure desired state をどう定義・review・apply するか | Terraform plan, IaC module, state | Platform / Infra | plan/apply mismatch, drift count, policy violations |
| 15.22 | プロビジョニング | infra / runtime / credentials をどう生成・廃棄するか | provision plan, runbooks, state records | Platform, SRE | provisioning lead time, failed provision rate |
| 15.23 | マイグレーション | schema/data/config/runtime の変更順序をどう安全化するか | migration plan, rollback plan | Backend Lead, DBA/SRE | migration failure rate, rollback compatibility |
| 15.24 | リリース計画 | いつ何を誰に release するか | release plan, release train, freeze window | Product, Release Manager | release predictability, slipped releases |
| 15.25 | バージョニング・タグ | version / tag / compatibility をどう定義するか | release tag, version manifest | Maintainer, Release Manager | tag immutability, version conflict count |
| 15.26 | リリース証跡 | release が何を含み何を検証済みかをどう残すか | release notes, evidence, test artifacts | Release Manager | evidence completeness, audit exceptions |
| 15.27 | ロールバック | どの条件で、どの対象を、どう戻すか | rollback runbook, previous deployment revision | SRE, Release Manager | rollback time, rollback success rate |
| 15.28 | プログレッシブデリバリー | blast radius をどう段階的に拡大するか | rollout strategy, traffic policy | SRE, Product, Release | promotion/abort ratio, blast-radius incidents |
| 15.29 | カナリア | 小規模 exposure で何を比較し、いつ昇格するか | canary analysis, metrics gate | SRE, Service Owner | canary detection rate, false rollback rate |
| 15.30 | ブルーグリーン | old/new environment の切替・保持・戻しをどう設計するか | blue-green topology, switch plan | SRE, Infra | switch success, warm standby drift |
| 15.31 | デプロイ監視・ゲート | rollout 中に何を観測し停止・昇格するか | SLI dashboard, alerts, analysis run | SRE, Observability | alert precision, SLO burn, rollout halt latency |
| 15.32 | 本番変更承認 | production 変更に必要なレビュー・承認・職務分離 | deployment approval, CAB-lite record | SRE, Security, Compliance | bypass count, approval latency |
| 15.33 | 障害学習・ポストモーテム | 失敗を次の gate / runbook / tests にどう反映するか | postmortem, action items, new checks | Incident Commander, SRE | repeat incident rate, action item closure |
| 15.34 | DORA / Delivery Metrics | delivery capability をどう測定・改善するか | metrics dashboard, trend review | Engineering Leadership | lead time, deployment frequency, CFR, recovery time |
| 15.35 | 継続改善・成熟度 | 15.01–15.34 全体をどう改善し成熟化するか | maturity assessment, roadmap | CTO, Platform Lead | maturity score, control coverage, adoption |

---

## 4. Layer Normalization

### Definition

開発プロセス・品質保証・CI/CD・リリースレイヤーは、source code から production 変更までの全経路を、**変更提案、レビュー、検証、ビルド、パッケージ、証跡、デプロイ、リリース、ロールバック、学習**に分解し、各段階で誰が何を判断し、どの自動制御で品質・セキュリティ・可用性を守るかを決めるレイヤーである。

### Decision Object

「source / config / infrastructure / package / artifact / release / deployment の変更を、どの gate、owner、artifact、metric、exception、rollback path によって production へ到達させるか」。

### Decision Question

このレイヤーで優れた主体は、何を入力に、どの変更を source control 上のどの単位として扱い、どの branch / commit / PR / review / static analysis / test / build / artifact / CI/CD / deployment / release / rollback / canary / environment / IaC / configuration management の基準で許可し、誰が責任を持ち、何を証跡として残し、どの metric で正しさを判定するか。

---

## 5. Frontier Exemplars

| Exemplar | Why it is frontier-relevant | Transferable Patterns | Evidence |
|---|---|---|---|
| NIST SSDF | secure software development を SDLC 全体の高水準 practice として整理し、脆弱性低減・共通語彙・組織間伝達に使える | security requirements as lifecycle gates, common control vocabulary | S01 |
| SLSA | source and build integrity、provenance、trusted build platform を formal level として定義する | isolated builder, provenance, source history, code review as supply-chain control | S02 |
| OpenSSF Scorecard / SCM Best Practices | OSS repository / CI/CD security posture を observable checks に落とす | branch protection, code review, SAST, pinned dependencies, signed releases, token permissions | S03, S04 |
| GitHub | branch protection、PR reviews、code scanning、Actions environments、artifacts、packages、releases を統合した developer platform | protected branch + PR review + required checks + deploy environment gates | S05–S12 |
| GitLab | CI/CD pipelines、protected branches、artifacts、release evidence、environments、rollback を一体管理する platform | release evidence, MR widgets, protected environments, environment-scoped variables | S13–S21 |
| Linux Kernel | 大規模分散OSSにおける patch submission、maintainer customs、review tags、rolling release cadence の公開運用 | small logical patch, maintainer-local customs, merge window + rc stabilization | S22–S24 |
| Kubernetes | deployment desired state、rolling update、rollback、revision history、progress deadline を宣言的に扱う | declarative deployment, rollout status, revision rollback, surge/unavailable budget | S25 |
| Argo Rollouts | Kubernetes 上で canary / blue-green / analysis / traffic shifting / automated rollback を CRD と controller に落とす | progressive delivery as controller-managed decision loop | S26 |
| Google SRE | canarying と reliable release の operational philosophy を明文化する | assume release contains bugs; compare canary/control; rollback before broad impact | S27, S28 |
| Terraform / OpenGitOps | infrastructure desired state を versioned、reviewed、planned、applied、reconciled にする | IaC plan-review-apply, Git as desired-state ledger, pull reconciliation | S30–S33 |
| Twelve-Factor / Kubernetes ConfigMap | deploy-varying configuration を code/image と分離し、environment-specific input として扱う | env vars, ConfigMap, Secret, no baked environment config | S34, S35 |

---

## 6. Evidence Map

| Claim ID | Claim | Decision Model Field | Evidence | Confidence |
|---|---|---|---|---|
| C01 | 開発・品質・リリースの第一原則は、変更を source-controlled, reviewable, auditable な単位にすること。 | principles / controls | GitHub protected branches require PR reviews and checks; GitLab protected branches regulate who can push/merge; OpenSSF SCM practices treat SCM platform setup as security-critical. | A |
| C02 | Branch policy は default / production / release branch を protected とし、direct push, force push, delete, unreviewed merge を原則禁止する。 | prohibitions / thresholds | GitHub protected branches block deletion/force push and can require status checks, linear history, signed commits, merge queue, and deployment success; GitLab allows protected branches where only maintainers can merge/push and Code Owner approval can be required. | A |
| C03 | PR/MR は変更の意思決定単位であり、review、approval、requested changes、comments、suggestions、status checks を通じて merge 可否を判断する。 | decision_object / approval | GitHub PR reviews describe approval/request-change workflows and required approvals; Linux kernel requires small logical patches and technical Reviewed-by/Tested-by signaling. | A |
| C04 | 変更は小さい論理単位で、問題・ユーザー影響・trade-off・変更理由を説明できなければならない。 | criteria / artifacts | Linux kernel patch guidance states each patch should be one logical change and commit log should describe problem, impact, and trade-offs. | A |
| C05 | Static analysis / code quality / code scanning は PR/MR ゲートに統合し、重大度に応じて merge を停止できる必要がある。 | controls / thresholds | GitHub code scanning can fail PR checks for high/critical/security severity; GitLab Code Quality exposes MR widget and report artifacts. | A |
| C06 | CI pipeline は repository 内の declarative configuration として管理され、jobs/stages を event-triggered に実行する。 | operating_model / interfaces | GitHub Actions workflow is a YAML-configured automated process; GitLab pipeline configuration lives in `.gitlab-ci.yml` and runs jobs/stages sequentially or in parallel. | A |
| C07 | Build output、test reports、quality reports、release evidence は job artifacts / release evidence として保存し、後続 job・監査・rollback の根拠にする。 | outputs / evidence | GitHub artifacts persist workflow output; GitLab job artifacts and release evidence capture build/report/test/package/release state. | A |
| C08 | Release artifact は source tree とは別の immutable package / image / release bundle として registry / release system に置く。 | artifacts / controls | GitHub Packages links packages with source/build/deployment history; GitHub Releases are deployable iterations based on Git tags; GitLab Releases package code, binaries, docs, notes, tags. | A |
| C09 | Build provenance は artifact がいつ・どこで・どう作られたかを説明し、consumer は provenance を使って検証・再構築可能性を評価する。 | provenance / controls | SLSA Build Track requires provenance and trusted control plane properties; SLSA provenance describes where, when, and how artifacts were produced. | A |
| C10 | Build platform は developer workstation ではなく、consistent build process, isolation, unforgeable provenance を担う trusted platform であるべき。 | prohibitions / controls | SLSA build requirements assign provenance generation and isolation to build platform and define authenticity/unforgeability controls. | A |
| C11 | Deployment は environment を明示的な target として扱い、approvals, wait timers, branch/tag restrictions, environment-scoped secrets/variables で production gate を作る。 | approval / exceptions | GitHub environment protection rules block secrets access and deployment until rules pass; GitLab environments track deployments and can protect variables and environments. | A |
| C12 | Kubernetes-style deployment は desired state、rolling update、revision history、rollout status、rollback を宣言的に管理する frontier baseline である。 | technical_spec / controls | Kubernetes Deployment manages desired state, rolling updates, revision history, progress status, and rollback by revision. | A |
| C13 | Progressive delivery は canary / blue-green / traffic shifting / metrics analysis によって blast radius を制御し、成功なら promotion、失敗なら rollback する。 | rollout / failure_modes | Argo Rollouts supports canary, blue-green, weighted traffic, analysis, auto rollback/promotion; Google SRE canarying compares canary/control on small traffic. | A |
| C14 | Release engineering は「release contains bugs」を前提に、canarying、fast detection、rollback/recovery path を前提に設計する。 | philosophy / exceptions | Google SRE reliable release guidance assumes releases may contain bugs and uses canarying and recovery to limit user impact. | B |
| C15 | IaC は plan-review-apply の流れで、current state と desired configuration の差分を preview し、reviewed saved plan を apply する設計が望ましい。 | IaC / controls | Terraform plan compares configuration and state and supports speculative plan for code review; Terraform apply executes a proposed plan and can use saved plan mode. | A |
| C16 | GitOps は declarative desired state を versioned and immutable に保存し、agent が自動 pull/reconcile するモデルである。 | IaC / operating_model | OpenGitOps principles define declarative, versioned immutable, automatically pulled desired state. | A |
| C17 | Configuration は deploy-varying data として code/image から分離し、non-confidential は ConfigMap/env vars、confidential は Secret 等に分ける。 | configuration / prohibitions | Twelve-Factor says config that varies by deploy should be in environment and not checked into code; Kubernetes ConfigMap decouples environment-specific config from image and recommends Secret for confidential data. | A |
| C18 | Delivery performance は speed だけでなく stability と一緒に測る必要があり、DORA metrics は lead time, deployment frequency, recovery time, change fail rate, deployment rework rate を見る。 | metrics | DORA metrics guide defines throughput and instability metrics and notes speed/stability are not simple trade-offs. | A |
| C19 | 重大障害の多くは、destructive operation、script scope validation、backup verification、topology/failover readiness、manual exception の gate 不足から生じる。 | failure_modes | GitLab 2017 DB incident, Atlassian 2022 outage, GitHub 2018 incident show failures in destructive operation control, script validation, backup/recovery, and topology recovery. | B |
| C20 | 成熟した operating model は success path だけでなく rollback, restore, postmortem feedback, new gate creation を閉ループ化する。 | maturity / feedback | GitLab rollback/deployment docs, Kubernetes rollback, Google SRE canary/rollback philosophy, incident postmortems support continuous control improvement. | B |

---

## 7. Core Philosophy

### 7.1 Change as a controlled unit

変更は「誰かが編集したファイル」ではなく、branch、commit、PR/MR、review、CI checks、build artifact、deployment record、release evidence によって構成される controlled unit である。source code、IaC、configuration、pipeline definition、deployment manifest のすべてを同じ変更制御面に載せる。

### 7.2 Shift-left without abandoning production feedback

static analysis、unit test、integration test、code scanning、dependency policy は merge 前に置く。ただし frontier model は pre-production gate を過信しない。Google SRE の canarying が示す通り、production traffic で小さく検証し、control と比較し、失敗時に速く rollback する production feedback loop が必要である。

### 7.3 Immutable artifact over mutable source

release は repository の現在状態ではなく、特定 commit から CI上で生成された artifact / package / image / release bundle である。artifact は version、digest、build log、test evidence、provenance、release note、deployment record と結合される。

### 7.4 Declarative desired state

deployment、environment、infrastructure、configuration は、手作業の imperative operation ではなく、GitOps / IaC / Kubernetes のような declarative desired state として扱う。manual console change は原則として例外であり、後追いで source of truth に戻す必要がある。

### 7.5 Progressive exposure and reversible decisions

release は一度に全ユーザーへ出すものではない。canary、blue-green、traffic split、feature flags、staged rollout、environment gates によって exposure を段階的に増やす。promotion と rollback は同じレベルの第一級操作として設計する。

---

## 8. Decision Model

### Inputs

- Change request: issue、design doc、incident action item、security advisory、migration need、product release item
- Source state: repository、branch、commit、tag、dependency lock、submodule / vendored dependency
- Risk profile: security severity、customer impact、data migration、backward compatibility、availability risk、regulatory impact
- Ownership: CODEOWNERS、maintainer、service owner、SRE owner、release owner、security reviewer
- Quality signals: static analysis、SAST、lint、unit/integration/E2E tests、coverage、flaky test history、code quality report
- Build signals: build log、artifact digest、provenance、package version、image manifest、release evidence
- Environment signals: target environment、protection rules、secrets/variables scope、current deployment revision、drift state
- Deployment signals: rollout strategy、traffic split、SLI/SLO、error budget、canary metrics、alert state
- Recovery signals: rollback runbook、previous known-good artifact、database migration reversibility、backup/restore status

### Decision Criteria

1. **Traceability**: 変更は issue / PR / commit / artifact / deployment / release evidence まで追跡できるか。
2. **Ownership**: 変更対象に対して適切な owner / reviewer / approver がいるか。
3. **Small logical unit**: review 可能な論理単位か。複数関心が混在していないか。
4. **Automated verification**: required checks、tests、static analysis、code scanning、policy checks が pass しているか。
5. **Build integrity**: release artifact は trusted build platform で生成され、provenance / digest / artifact record があるか。
6. **Environment safety**: target environment の approval、branch/tag restrictions、secret scope が満たされているか。
7. **Progressive delivery**: production blast radius を小さく始める strategy があるか。
8. **Observability**: rollout 中に判定できる SLI / alerts / dashboards / canary analysis があるか。
9. **Rollback readiness**: previous revision、rollback command/runbook、migration fallback、customer communication path があるか。
10. **Auditability**: 例外・承認・変更・rollback・postmortem が evidence として残るか。

### Priorities

1. Protected source of truth
2. Mandatory review and automated gate before merge
3. Reproducible / provenance-backed build
4. Immutable artifact and release evidence
5. Environment-scoped deployment controls
6. Progressive rollout before broad exposure
7. Fast rollback and postmortem feedback
8. DORA-style speed/stability optimization

### Prohibitions

- protected branch への direct push / force push / unreviewed merge
- production release artifact を local developer workstation で生成すること
- CI/CD workflow に不要な write token や broad secret access を与えること
- release tag / artifact / image を同名で mutable に差し替えること
- production config / secret を source code や container image に焼き込むこと
- migration plan なしで data-destructive operation を production 実行すること
- canary / monitoring / rollback path なしで high-risk change を all-at-once release すること
- manual console change を source of truth に反映しないこと

### Thresholds and Gates

| Gate | Minimum Frontier Threshold | Evidence Basis |
|---|---|---|
| Branch protection | default / production / release branches require PR/MR, status checks, no force push, restricted push/merge; signed commits and linear history where needed | S05, S14 |
| Code ownership | files / directories / services have CODEOWNERS or equivalent; owner approval required for high-risk areas | S05, S14 |
| PR/MR review | at least one independent qualified reviewer; security/SRE/database reviewer added by path/risk; self-approval prohibited for protected release | S06, S22 |
| Static analysis | high/critical security findings fail required checks unless formally waived | S09, S15 |
| CI tests | required unit/integration/contract/regression tests pass before merge; flaky tests quarantined with owner and due date | S07, S13, S15 |
| Build | build runs on controlled CI/build platform; artifact has digest and build log; provenance required for release candidates | S02, S10, S16 |
| Package / artifact | artifact version unique; release artifact immutable; package linked to source/build metadata where supported | S11, S12, S17, S18 |
| Environment | production environments require approval/protection; secrets are environment-scoped; branch/tag restrictions enforced | S08, S19, S21 |
| IaC | Terraform plan or equivalent diff reviewed in PR; apply uses reviewed plan for production; drift reviewed before apply | S31–S33 |
| Deployment | rollout status monitored; progress deadline defined; revision history retained | S25 |
| Canary | small initial population, canary/control comparison, automatic or manual abort criteria | S26, S27 |
| Rollback | prior artifact/revision retained; rollback command/runbook tested; database migration fallback documented | S20, S25, S27 |
| Metrics | DORA metrics reviewed at team/platform level; speed and stability measured together | S29 |

### Owners and Reviewers

| Role | Responsibility |
|---|---|
| Developer | Creates branch, commits, PR/MR, tests, and change rationale. Owns correctness until merged and deployed. |
| Maintainer / Code Owner | Approves domain correctness, design fit, and maintainability. Controls merge permission. |
| Reviewer | Evaluates code, tests, performance, security implications, rollback implications. |
| AppSec / Security Engineer | Owns SAST policy, dependency policy, secret handling, supply-chain controls. |
| Build Platform Owner | Owns CI runners/builders, provenance, artifact retention, pipeline availability. |
| QA / Test Lead | Owns test strategy, flaky test management, regression coverage, release qualification. |
| SRE / Operations | Owns environment gates, deployment safety, observability, rollback, incident feedback. |
| Release Manager | Owns release plan, version/tag, release evidence, promotion decision, stakeholder communication. |
| Platform Engineer | Owns IaC modules, provisioning workflows, GitOps controllers, environment lifecycle. |
| Product Owner | Owns customer exposure strategy, release timing, feature rollout, business acceptance. |

### Cadence

- Per change: PR/MR review, CI gate, static analysis, test, build.
- Per release candidate: provenance verification, package scan, release evidence, staging deploy, canary plan.
- Per production deploy: environment approval, rollout status, canary/blue-green analysis, rollback readiness.
- Weekly: flaky test review, CI failure review, open high-severity code scanning review.
- Monthly: DORA metrics, branch protection exceptions, deployment incidents, IaC drift, postmortem action closure.
- Quarterly: maturity assessment, SLSA/Scorecard posture, release process tabletop/rollback test.

---

## 9. Operating Model

### 9.1 End-to-End Change Flow

```text
1. Intake
   issue / incident action / product requirement / security fix / migration need

2. Design and risk classification
   low-risk code change / high-risk service change / data migration / infra change / security fix

3. Source change
   short-lived branch -> commits -> tests locally -> PR/MR

4. Review gate
   CODEOWNERS -> reviewer assignment -> technical review -> requested changes / approval

5. Automated merge gate
   lint -> SAST -> unit tests -> integration tests -> code quality -> policy checks -> required status checks

6. Merge
   merge queue / protected branch merge -> immutable commit history -> release branch/tag if applicable

7. Build
   controlled CI/build platform -> artifact -> digest -> provenance -> package registry -> job artifacts

8. Release candidate
   release notes -> release evidence -> staging deployment -> acceptance checks -> production approval

9. Deployment
   environment gate -> canary/blue-green/rolling update -> metrics analysis -> promotion or abort

10. Recovery / learning
    rollback if needed -> incident/postmortem -> new test/gate/runbook -> metrics update
```

### 9.2 Repository and Branch Model

Recommended default is trunk-based development with short-lived branches, protected default branch, and optional release branches for compatibility windows or regulated production release. Long-lived feature branches are allowed only for exceptional cases and must be continuously rebased/merged to avoid integration cliff.

Branch protection must include, at minimum, required PR/MR review, required status checks, restricted push/merge rights, no force push, and deployment checks for protected environments. For high-risk repositories, add signed commits, linear history, merge queue, and Code Owner approval.

### 9.3 PR/MR Review Model

A PR/MR should be small, logically cohesive, and linked to an issue or change request. It must state the problem, approach, user impact, tests run, rollback considerations, and whether the change affects APIs, data, security, infra, or production operations. Linux kernel patch practice provides a transferable standard: each patch is a small logical change with clear rationale and technical review tags.

Review is not mere approval. It checks correctness, maintainability, security, test adequacy, operational risk, observability, and rollback. Required approvals should be path-sensitive: security-sensitive code requires AppSec; IaC touching production requires platform/SRE; database migrations require data owner/DBA; public API changes require API owner and documentation owner.

### 9.4 Quality and Security Gates

Static analysis, SAST, dependency checks, code quality reports, unit tests, integration tests, and release tests should all be expressed as pipeline gates. Severity should determine action: high/critical security findings block merge unless there is a documented exception; medium/low findings create tracked remediation; flaky tests are not ignored but quarantined with owner and deadline.

### 9.5 Build and Artifact Model

The build stage should run in a controlled build platform, not on an engineer’s machine. Output artifacts include binaries, packages, container images, test reports, logs, coverage, code quality reports, and provenance. Release artifacts must be immutable, versioned, digest-addressable where possible, and linked to source commit and build run.

SLSA-style provenance is the frontier control because it answers: who/what initiated the build, which source revision was used, which builder produced the output, what dependencies or steps were involved, and whether the consumer can trust this chain.

### 9.6 Environment and Deployment Model

Environments are not just names. They are deployment targets with protection rules, variable/secret scopes, approval policies, monitoring, current revision, and rollback state. Production should have explicit approval/protection, branch/tag restrictions, and environment-scoped credentials.

Kubernetes Deployment provides a canonical declarative model: desired state, rollout progress, rolling update strategy, revision history, and rollback. Argo Rollouts extends this into progressive delivery with canary, blue-green, traffic routing, metric analysis, and automated rollback/promotion.

### 9.7 Release and Rollback Model

Release is a product and operational decision, not only a build result. It should include version/tag, release notes, artifact identifiers, test evidence, known risks, migration notes, rollout plan, rollback plan, and customer communication where applicable.

Rollback must be tested and explicit. A mature system retains previous deployment revisions/artifacts, can roll back application deployment quickly, and understands which migrations are reversible, forward-fix-only, or require compensating actions. GitLab and Kubernetes both model rollback as explicit deployment/revision operations, not as vague “undo.”

### 9.8 IaC and Configuration Model

Infrastructure is defined through IaC and reviewed as code. Terraform plan or equivalent diff is the review artifact; apply is the controlled execution. For production, saved plan or otherwise tightly coupled plan/apply flow reduces mismatch between reviewed intent and executed change.

Configuration that varies by environment must be externalized. Non-confidential configuration can use environment variables or ConfigMap; confidential configuration belongs in Secret or equivalent secret manager. Environment-specific config must not be baked into source code or container image.

---

## 10. Technical / Business Specification for Cloning

### 10.1 Minimum Repository Controls

| Control | Required Design |
|---|---|
| Repository classification | Classify repositories by production impact: core product, service, infra, library, experimental, archived. |
| CODEOWNERS | Every production-impacting path has owner. Missing owner blocks merge. |
| Branch protection | Default, production, release branches protected. No direct push. No force push. No delete. Required status checks. |
| Merge queue | Use for high-velocity repositories to test queued changes against latest protected branch. |
| Signed commits/tags | Required for high-risk repos and release tags; recommended elsewhere. |
| Tags | Release tags immutable. Moving/deleting release tags prohibited except formal security/emergency process. |
| Token permissions | CI tokens default read-only; write permissions granted per job and minimized. |
| Workflow trust | Third-party CI actions pinned and reviewed; untrusted fork workflows cannot access secrets. |
| Audit trail | Merge, approval, environment approval, deployment, rollback are logged. |

### 10.2 PR/MR Template

```markdown
## Change Summary
- What changed:
- Why now:
- Linked issue/design doc:

## Risk Classification
- [ ] Low-risk code change
- [ ] Public API / compatibility impact
- [ ] Data migration
- [ ] Infrastructure / provisioning
- [ ] Security-sensitive
- [ ] Production operational behavior

## Verification
- Unit tests:
- Integration tests:
- Static analysis / SAST:
- Manual validation, if any:

## Deployment and Rollback
- Target environments:
- Migration needed:
- Rollout strategy:
- Rollback path:
- Observability / dashboards:

## Reviewers
- Code owner:
- Security reviewer:
- SRE / platform reviewer:
- Product / release approver:
```

### 10.3 CI/CD Pipeline Baseline

```yaml
# Illustrative skeleton; adapt to GitHub Actions, GitLab CI, Buildkite, CircleCI, Jenkins, etc.
stages:
  - validate_source
  - test
  - security
  - build
  - package
  - release_candidate
  - deploy_staging
  - deploy_production
  - verify_rollout

validate_source:
  controls:
    - branch_protection_required
    - code_owner_approval_required
    - commit_signature_required_for_release
    - dependency_lockfile_present

static_analysis:
  gates:
    - lint_must_pass
    - code_quality_report_must_not_regress_above_threshold
    - sast_high_critical_must_be_zero_or_waived

unit_and_integration_tests:
  gates:
    - unit_tests_pass
    - integration_tests_pass
    - flaky_tests_tracked_with_owner

build:
  controls:
    - controlled_builder_only
    - artifact_digest_generated
    - provenance_generated
    - build_log_retained

package:
  controls:
    - package_version_unique
    - artifact_immutable
    - package_linked_to_source_commit

release_candidate:
  controls:
    - release_notes_generated
    - release_evidence_collected
    - rollback_plan_present
    - migration_plan_present_if_needed

deploy_staging:
  controls:
    - environment_scoped_variables
    - staging_smoke_tests_pass
    - contract_tests_pass

deploy_production:
  controls:
    - production_environment_approval
    - branch_or_tag_restriction
    - canary_or_blue_green_strategy_required
    - previous_revision_available

verify_rollout:
  controls:
    - canary_metrics_within_threshold
    - error_rate_not_regressed
    - latency_not_regressed
    - rollback_if_abort_condition_met
```

### 10.4 Quality Gates

| Gate | Implementation Detail | Failure Action |
|---|---|---|
| Lint / formatting | deterministic rules in CI; local optional | block merge |
| Static analysis | language/tool specific; reports in PR/MR | block if severe; ticket if non-severe |
| SAST | PR/MR code scanning; severity threshold | block high/critical unless waived |
| Dependency scan | pinned dependencies and advisory checks | block exploitable critical; tracked remediation otherwise |
| Unit tests | fast per PR | block merge |
| Integration tests | service/API/database integration | block if touched area affected |
| Contract tests | public/internal API compatibility | block breaking change unless approved migration |
| E2E/smoke tests | staging / pre-prod | block production deployment |
| Performance tests | relevant for latency/capacity-sensitive changes | hold release or require SRE approval |
| Rollback test | high-risk deploy path | block high-risk production release if no rollback proof |

### 10.5 Build and Provenance Controls

- Build must run in controlled CI/build platform.
- Build input must reference immutable commit SHA, not floating branch name alone.
- Builder identity and workflow identity are recorded.
- Artifact digest is generated and carried into package/deployment manifest.
- Provenance record is attached to release candidate.
- Release artifact is not rebuilt manually after approval; if rebuilt, the approval and evidence cycle restarts.
- Artifact retention policy keeps build outputs long enough for rollback, audit, and incident analysis.

### 10.6 Deployment Specification

| Area | Required Design |
|---|---|
| Environment tiers | dev, ephemeral preview, staging/pre-prod, production. Each has owner, secrets scope, approvals, and retention rules. |
| Production gate | manual approval or automated policy approval, branch/tag restriction, required deployment checks. |
| Rollout strategy | rolling update for low/medium risk; canary or blue-green for high-risk; feature flags when business exposure must be separated from deploy. |
| Observability | define SLI and abort thresholds before deploy. Error rate, latency, saturation, business KPI, and logs/traces as relevant. |
| Rollback | retain previous revision/artifact; rollback command/runbook; migration fallback or forward-fix plan. |
| Freeze / exception | release freeze exceptions require explicit owner and audit record. |

### 10.7 Migration Specification

Migrations need a separate decision model because database/schema/config changes are often not trivially reversible.

Recommended default is **expand-contract**:

1. Expand: add backward-compatible schema/config/API support.
2. Deploy application compatible with both old and new state.
3. Migrate data in controlled batches, with metrics and checkpoints.
4. Switch reads/writes when validation passes.
5. Contract: remove old field/path only after observation window and rollback risk is low.

Migration PR/MR must include target state, affected records/resources, idempotency, retry behavior, rollback or forward-fix plan, backup/restore requirement, expected duration, monitoring, and owner on call.

---

## 11. Metrics

### 11.1 DORA / Delivery Metrics

| Metric | Formula / Observation | Decision Use |
|---|---|---|
| Change lead time | time from code committed/merged to production | detect bottlenecks in review, CI, release, environment approval |
| Deployment frequency | production deployments per service/team/time | measure delivery throughput and batching behavior |
| Failed deployment recovery time | time from failed deployment detection to recovery | evaluate rollback/runbook/observability maturity |
| Change fail rate | percentage of deployments requiring rollback/hotfix/intervention | measure release quality and risk controls |
| Deployment rework rate | percentage of deployments that require rework | identify insufficient verification or release readiness |

### 11.2 Repository and Review Metrics

- PR/MR cycle time
- review wait time
- average patch size / files touched
- required check failure rate
- number of bypassed protections
- direct-push violations
- CODEOWNERS coverage
- reviewer load distribution
- stale branch count
- revert rate by repository

### 11.3 Quality and Security Metrics

- high/critical SAST findings open by age
- code scanning alerts introduced per PR
- false-positive ratio by scanner
- unit/integration/E2E pass rate
- flaky test count and age
- coverage trend for risk-critical modules
- dependency vulnerabilities by severity and exploitability
- signed release / provenance coverage
- OpenSSF Scorecard trend for OSS repositories

### 11.4 Build / Artifact Metrics

- build success rate
- build duration p50/p95
- queue time
- artifact retention compliance
- artifact digest verification coverage
- provenance generation coverage
- package version conflict count
- failed publish count
- rebuild verification success rate

### 11.5 Deployment / Release Metrics

- deploy success rate
- environment approval latency
- canary promotion rate
- canary abort rate
- false promotion rate
- rollback time p50/p95
- incidents per deployment
- SLO burn during rollout
- migration failure rate
- postmortem action item closure rate

---

## 12. Failure Modes

| Failure Mode | Mechanism | Prevention / Control | Evidence |
|---|---|---|---|
| Direct production mutation | Manual change bypasses source/review/CI evidence | protected branch/environment, IaC only, break-glass audit | S05, S08, S30–S33 |
| Unreviewed risky change | Owner not involved; reviewer lacks context | CODEOWNERS, path-based review, risk-class PR template | S05, S06, S14, S22 |
| Large PR/MR hides defects | Multiple concerns exceed review capacity | small logical patches, split change, merge queue | S22, S05 |
| Static analysis is advisory only | Findings ignored until production incident | severity-based required checks, exception workflow | S09, S15 |
| CI secrets exposed | Workflow gets excessive token/secrets, especially from untrusted code | least-privilege tokens, environment-scoped variables, trusted actions | S03, S08, S21 |
| Local/manual release build | Artifact cannot be traced or reproduced | controlled builder, provenance, artifact registry | S02, S10, S16 |
| Mutable release artifact | Same version/tag points to different bytes | immutable versioning, digest, signed tags/releases | S02, S11, S12 |
| All-at-once deploy | Bug hits all customers before detection | canary, blue-green, traffic split, progressive rollout | S26–S28 |
| Missing rollback path | Release can fail but cannot recover quickly | retain prior revision, rollback runbook, migration fallback | S20, S25, S27 |
| Destructive data operation | Wrong scope/delete/drop operation damages production | migration review, dry run, backup verification, two-person control | F01, F02 |
| Untested backup/restore | Backup exists but restore fails or is too slow | scheduled restore drills, backup monitoring, RPO/RTO tests | F01 |
| Staging mismatch | Test environment misses production identifiers/topology | production-like staging, canary, scoped script validation | F02 |
| Topology/failover assumption failure | network or infra maintenance causes cascading recovery issue | disaster recovery tests, topology failover runbooks, gradual maintenance | F03 |
| Metrics blind spot | rollout proceeds despite hidden user impact | SLI/KPI dashboard, canary/control comparison, abort threshold | S27, S28 |

---

## 13. Anti-patterns

1. **CI/CD as deployment script only**: pipeline が policy enforcement と evidence collection をしていない。
2. **Protected branch without meaningful checks**: branch は保護されているが required checks が弱い、または admin bypass が常態化している。
3. **Reviewer theater**: reviewer は approval するだけで、tests、rollback、security、operational risk を見ない。
4. **Mutable `latest` release culture**: version / tag / digest を固定せず、何が production に出たか再現できない。
5. **Artifact without provenance**: artifact はあるが、どの commit / builder / dependency / workflow から作られたか不明。
6. **Secrets as configuration convenience**: CI/CD variables や secrets が environment scope なしに広く共有される。
7. **IaC plan not reviewed**: Terraform plan や manifest diff を PR/MR review に入れず、apply 結果だけを見る。
8. **Canary as checkbox**: traffic split はしているが、control comparison、abort threshold、promotion criteria がない。
9. **Rollback as hope**: previous version はあるが、rollback command、data compatibility、customer communication が未検証。
10. **Postmortem without control change**: incident action item が新しい test/gate/runbook に変換されない。

---

## 14. Maturity Model

| Level | Name | Criteria |
|---:|---|---|
| 0 | 未整備 | source control はあるが直接 push 可能。CIは任意。release artifact と deployment record が分離されていない。rollback は属人的。 |
| 1 | 個人依存 | PR/MR review や tests はあるが owner・gate・exception が不統一。CI failure を無視する運用がある。 |
| 2 | 文書化 | branch protection、PR template、basic CI、release note、rollback runbook が文書化されている。まだ証跡と自動化が弱い。 |
| 3 | 標準化 | protected branch、CODEOWNERS、required checks、static analysis、test reports、artifact retention、environment approvals が標準化されている。 |
| 4 | 自動化・計測 | provenance、immutable artifacts、package registry、GitOps/IaC、canary/blue-green、DORA dashboard、policy-as-code が運用される。 |
| 5 | 自律改善・業界先端 | SLSA/Scorecard posture を継続改善し、incident feedback が新しい gates に自動的に反映され、progressive delivery と rollback がサービス標準になっている。 |

---

## 15. Clone Implementation Guide

### Phase 0: Baseline Assessment

- 全 repositories を catalog 化する。
- production-impacting repositories を分類する。
- default / release / production branches の protection 状態を棚卸しする。
- CI/CD workflows、required checks、secrets、runner permissions を棚卸しする。
- production deployment の source commit / artifact / environment / approval / rollback traceability を確認する。
- DORA baseline を計測する。

### Phase 1: Repository and PR/MR Controls

- protected branches を全 production-impacting repos に設定する。
- direct push / force push / delete を禁止する。
- CODEOWNERS を導入し、owner missing path をなくす。
- PR/MR template を導入し、risk classification、verification、rollback を必須化する。
- required checks を最低限 lint + unit test + build にする。
- high-risk paths に security / platform / SRE review を設定する。

### Phase 2: Quality and Security Gates

- SAST / code scanning を PR/MR に統合する。
- high/critical severity policy を定義する。
- code quality report を MR/PR に表示する。
- flaky test management を開始する。
- dependency policy、pinned actions/dependencies、read-only default token を設定する。
- OpenSSF Scorecard などで外部 posture を計測する。

### Phase 3: Build, Package, Artifact, Provenance

- release candidate artifact を controlled CI build のみに限定する。
- artifact digest、build logs、test reports、job artifacts を retention policy 付きで保存する。
- package registry / container registry / release system に source commit と build record を結合する。
- SLSA provenance generation を導入する。
- release evidence snapshot を整備する。

### Phase 4: Deployment and Environment Controls

- environment registry を作る: dev / preview / staging / prod。
- production environment に approval、branch/tag restriction、secrets scope を設定する。
- staging smoke tests、contract tests、migration dry-run を deployment gate にする。
- Kubernetes Deployment or equivalent desired-state deployment を標準化する。
- rollout status、progress deadline、revision history を設定する。

### Phase 5: Progressive Delivery and Rollback

- high-risk services に canary または blue-green を導入する。
- canary metrics と abort threshold を事前定義する。
- previous known-good artifact / revision を保持する。
- rollback drill を定期実施する。
- database migrations に expand-contract pattern を導入する。
- incident postmortem action を new test / new gate / runbook change に変換する。

### Phase 6: Measurement and Continuous Improvement

- DORA metrics を service/team/platform レベルで dashboard 化する。
- branch protection bypass、approval latency、CI failure、rollback、postmortem action closure を月次レビューする。
- quarterly に SLSA / Scorecard / IaC drift / secrets exposure / environment policy を再評価する。
- platform team は共通 pipeline templates、IaC modules、rollout templates、policy-as-code を提供する。

---

## 16. Reference Architecture

```text
                  ┌──────────────────────┐
                  │ Issue / Design / Risk │
                  └──────────┬───────────┘
                             │
                             ▼
┌──────────────┐     ┌─────────────────┐     ┌─────────────────────┐
│ Source Repo  │────▶│ PR/MR + Review  │────▶│ Protected Branch     │
│ CODEOWNERS   │     │ Required Checks │     │ Merge Queue / Tag    │
└──────────────┘     └─────────────────┘     └──────────┬──────────┘
                                                         │
                                                         ▼
                         ┌─────────────────────────────────────────┐
                         │ Controlled Build Platform                │
                         │ tests / SAST / build / provenance        │
                         └──────────┬──────────────────────────────┘
                                    │
                                    ▼
                         ┌─────────────────────────────────────────┐
                         │ Package / Artifact Registry              │
                         │ digest / version / release evidence      │
                         └──────────┬──────────────────────────────┘
                                    │
                                    ▼
                         ┌─────────────────────────────────────────┐
                         │ Environment Gates                        │
                         │ staging checks / prod approval / secrets │
                         └──────────┬──────────────────────────────┘
                                    │
                                    ▼
                         ┌─────────────────────────────────────────┐
                         │ Progressive Deployment                   │
                         │ canary / blue-green / rolling update     │
                         └──────────┬──────────────────────────────┘
                                    │
                       ┌────────────┴────────────┐
                       ▼                         ▼
              ┌────────────────┐        ┌────────────────┐
              │ Promote Release │        │ Rollback / Fix  │
              └───────┬────────┘        └───────┬────────┘
                      │                         │
                      └────────────┬────────────┘
                                   ▼
                         ┌──────────────────┐
                         │ Metrics + Learning│
                         │ DORA / Postmortem │
                         └──────────────────┘
```

---

## 17. Validation Queries

Use these queries to re-run evidence collection, detect contradictions, or refresh the source catalog.

```text
site:docs.github.com "protected branches" "required status checks" "merge queue"
site:docs.gitlab.com "protected branches" "Code Owner" "merge request approval"
site:slsa.dev/spec "provenance" "build" "source track" "code review"
site:scorecard.dev "Branch-Protection" "Code-Review" "SAST" "Signed-Releases"
site:docs.github.com "code scanning" "pull request" "fail check" "critical"
site:docs.gitlab.com "release evidence" "test artifacts" "packages"
site:kubernetes.io/docs "Deployment" "rollback" "revision history" "maxSurge"
site:argoproj.github.io/rollouts "canary" "blue-green" "automated rollback"
site:sre.google "canarying releases" "rollback" "control"
site:developer.hashicorp.com/terraform "plan" "apply" "saved plan"
"GitLab.com Database Incident" "backup" "postmortem"
"Atlassian April 2022 outage" "script" "post-incident review"
"GitHub October 2018 post incident analysis" "degraded service"
```

---

## 18. Confidence and Unknowns

### Confidence A

- Protected branch / PR/MR / required checks / environment approvals are supported directly by GitHub and GitLab official documentation.
- SLSA build provenance and source/build tracks are supported directly by the SLSA specification.
- Kubernetes deployment rollout / rollback / revision history are supported directly by Kubernetes official documentation.
- Terraform plan/apply and GitOps declarative desired state are supported directly by official docs/principles.
- DORA metrics are supported by DORA’s official guide.

### Confidence B

- The unified model “protected source → reviewed PR → CI gate → provenance artifact → progressive deployment → rollback → DORA feedback” is synthesized from multiple independent source families rather than stated as a single standard.
- Failure modes around destructive scripts, backups, and topology recovery are inferred from multiple postmortems and generalized into controls.

### Confidence C

- Specific numeric thresholds for test coverage, canary traffic percentage, rollback time SLO, and artifact retention duration are domain-dependent and cannot be fixed globally from public sources.
- Whether every organization should use trunk-based development versus release branches depends on product compatibility, regulation, and team topology.

### Unknowns / Additional Research

- The exact official names of layers 15 in the user’s master taxonomy were not provided; this artifact maps them from the provided subthemes.
- Regulated industries may require additional controls: validated build environments, formal change advisory boards, segregation of duties, electronic signatures, retention rules.
- Database migration safety requires domain-specific constraints: data volume, replication topology, backup RPO/RTO, legal data retention.
- Non-Kubernetes deployment systems need equivalent abstractions for desired state, progressive rollout, revision history, and rollback.
- For proprietary platforms, internal pipeline evidence, incident data, and actual approval logs are not publicly observable and should not be inferred.

---

## 19. Compact Clone Spec

### Layer ID

15

### Layer Name

開発プロセス・品質保証・CI/CD・リリース

### Definition

source code から production release までの変更を、review、test、build、artifact、deployment、rollback、metric に分解し、品質・セキュリティ・可用性を守りながら高速に届ける operating system。

### Frontier Exemplars

NIST SSDF、SLSA、OpenSSF、GitHub、GitLab、Linux Kernel、Kubernetes、Argo Rollouts、Google SRE、Terraform、OpenGitOps、DORA。

### Core Philosophy

変更は小さく、所有者が明確で、レビューされ、自動検証され、trusted builder で artifact 化され、証跡付きで environment に展開され、小さく公開され、観測され、すぐ戻せるべきである。

### Decision Model

- Inputs: change request, source state, risk profile, ownership, quality/build/environment/deployment/recovery signals.
- Criteria: traceability, ownership, small logical unit, automated verification, build integrity, environment safety, progressive delivery, observability, rollback readiness, auditability.
- Priorities: protected source, mandatory review, automated gates, provenance, immutable artifact, environment controls, progressive rollout, rollback, DORA feedback.
- Prohibitions: direct production mutation, unreviewed merge, local release build, mutable release artifact, secrets in source/image, all-at-once high-risk deployment.
- Owners: developer, maintainer, code owner, AppSec, build owner, QA, SRE, release manager, platform engineer, product owner.
- Cadence: per change, per release candidate, per production deployment, weekly quality/security review, monthly DORA review, quarterly maturity assessment.

### Operating Model

Source repo is the ledger. PR/MR is the decision object. CI/CD is the control plane. Artifact registry is the release object store. Environment gate is the production boundary. Progressive delivery is the blast-radius controller. DORA dashboard and postmortem process are the feedback loop.

### Technical / Business Specification

Adopt protected branches, CODEOWNERS, PR templates, required checks, severity-based SAST gate, CI artifacts, controlled build/provenance, package registry, release evidence, environment-scoped secrets, IaC plan/apply, Kubernetes-style desired state, canary/blue-green, rollback runbook, DORA metrics.

### Metrics

DORA metrics plus PR cycle time, review latency, SAST severity backlog, flaky tests, build success, provenance coverage, environment approval latency, canary abort/promotion, rollback time, postmortem closure.

### Failure Modes

Bypass of source control, large unreviewable changes, advisory-only static analysis, overprivileged CI secrets, local builds, mutable releases, no rollback, destructive migration, untested backups, staging mismatch, unobserved rollout.

### Anti-patterns

CI/CD as script only, reviewer theater, mutable latest, artifact without provenance, secrets as config convenience, plan not reviewed, canary without metrics, rollback by hope, postmortem without new controls.

### Maturity Model

Level 0 manual and unprotected; Level 1 ad hoc PR/CI; Level 2 documented; Level 3 standardized gates; Level 4 automated/provenance/progressive/dora-measured; Level 5 self-improving with incident feedback and supply-chain posture management.

---

## Appendix A. Source-to-Decision Mapping

| Source | Strongest Field Contribution |
|---|---|
| NIST SSDF | secure development lifecycle controls |
| SLSA | source/build provenance and supply-chain integrity |
| OpenSSF SCM / Scorecard | SCM, CI/CD and repository security posture checks |
| GitHub docs | protected branch, PR review, actions, code scanning, artifacts, releases, packages, environments |
| GitLab docs | CI pipeline, protected branches, code quality, artifacts, release evidence, environments, rollback |
| Linux kernel docs | small logical patches, maintainer customs, technical review tags, release cadence |
| Kubernetes docs | deployment desired state, rolling update, revision history, rollback |
| Argo Rollouts | canary, blue-green, metric-driven promotion/rollback |
| Google SRE | canary philosophy and reliable releases under assumption of defects |
| DORA | speed/stability metrics and delivery capability measurement |
| Terraform / OpenGitOps | IaC and declarative versioned desired state |
| Twelve-Factor / Kubernetes ConfigMap | configuration separation and environment-specific config management |
| GitLab / Atlassian / GitHub incidents | failure boundaries, backup/restore, destructive operation, topology/failover risks |
