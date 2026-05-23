# Clone Spec: アイデンティティ・アクセス管理（Layers 09）

Generated: 2026-05-13  
Scope: identity / account / credential / password / MFA / session / token / OAuth / OIDC / SAML / Federation / SSO / RBAC / ABAC / policy / permission / role / tenant / org / group / user provisioning / access review / privileged access / data access  
Method: `RESEARCH.md` の Frontier Operating Model Research 手順に従い、公開情報・公式標準・公式プロダクトドキュメント・公開インシデント分析から、意思決定モデル、運用モデル、失敗条件、Clone Implementation Guide に正規化した。

---

## 1. Definition

このレイヤーは、組織内外の人間・非人間 ID が、どの保証レベルで識別・認証され、どの権限・文脈・時間制約・監査条件の下で、どのアプリケーション、クラウドリソース、データ、管理操作にアクセスできるかを決める制御面である。

この単位では、単なる「ログイン」や「SSO」ではなく、ID ライフサイクル、資格情報、認証強度、セッション、トークン、フェデレーション、プロビジョニング、権限制御、特権昇格、データアクセス、監査・失効までを一つの意思決定システムとして扱う。

**Decision Object**: ある主体が、ある時点・文脈・保証レベルで、あるリソース・データ・操作にアクセスしてよいか、またそのアクセスをどの期間・証跡・例外条件で維持または失効させるか。

**Decision Question**: 先端組織は、すべての人間・非人間 ID に対して、どの保証レベルで認証し、どのポリシーで権限を判定し、どの期間・文脈・監査証跡でアクセスを許可・制限・失効するのか。

---

## 2. Layer Registry: 09 のサブレイヤー分解

| Layer | サブレイヤー | 決定対象 | 主な成果物 |
|---:|---|---|---|
| 09.01 | Identity control plane | ID を制御面としてどう統合するか | IAM architecture, IdP/PDP/PEP map, identity taxonomy |
| 09.02 | Account & identity object model | user, guest, service account, workload, group, tenant をどう表現するか | subject schema, account model, tenant/group hierarchy |
| 09.03 | Credential lifecycle | 資格情報をどう発行・保管・更新・失効するか | credential inventory, binding/recovery/revocation policy |
| 09.04 | Password & recovery | パスワードとアカウント復旧をどう安全化するか | password policy, recovery policy, breached-password controls |
| 09.05 | MFA / passkey / authenticator assurance | どの認証器をどのリスクに要求するか | MFA policy, passkey rollout, AAL mapping |
| 09.06 | Session management | セッションをいつ作成・更新・終了・再認証するか | session policy, cookie/token controls, reauth rules |
| 09.07 | Token lifecycle | access token, refresh token, PAT, API token をどうスコープ・保護・失効するか | token policy, expiry/rotation/revocation rules |
| 09.08 | OAuth authorization | 委任認可をどう設計するか | OAuth client registry, scope catalog, redirect rules |
| 09.09 | OIDC authentication | OAuth 上のログインをどう検証するか | OIDC config, ID token validation, claims mapping |
| 09.10 | SAML / federation / enterprise SSO | エンタープライズ SSO とフェデレーションをどう維持するか | SAML metadata, cert rotation, federation runbook |
| 09.11 | App SSO & conditional access | アプリ別アクセス条件をどう追加するか | app sign-on policy, device/location/risk step-up rules |
| 09.12 | RBAC | 職務・役割ベースの権限をどう標準化するか | role catalog, permission bundle, role owner map |
| 09.13 | ABAC / ReBAC / context authorization | 属性・関係・文脈で権限をどう動的判定するか | attribute schema, relationship graph, policy rules |
| 09.14 | Policy evaluation & enforcement | allow/deny/step-up をどの順序で評価するか | policy-as-code, PDP/PEP design, test suite |
| 09.15 | Permission / role catalog | permission, role, entitlement をどう命名・管理するか | permission registry, entitlement catalog, SoD matrix |
| 09.16 | Tenant / org / group model | テナント、組織、グループ境界をどう設計するか | org hierarchy, group ownership, namespace rules |
| 09.17 | User provisioning / SCIM | ID とグループをどう自動プロビジョニングするか | SCIM mapping, provisioning monitor, connector registry |
| 09.18 | Joiner-Mover-Leaver lifecycle | 入社・異動・退職でアクセスをどう変えるか | lifecycle workflow, birthright access, deprovision playbook |
| 09.19 | Entitlement / request workflow | アクセス要求・承認・期限をどう処理するか | access package, request form, approval workflow |
| 09.20 | Access review / certification | アクセスを誰がどの頻度で再認証するか | review campaign, reviewer evidence, remediation log |
| 09.21 | Privileged access | 管理者権限をどう最小化・一時化するか | PIM/PAM, JIT, zero standing privilege policy |
| 09.22 | Non-human identity | service account, workload identity, automation token をどう管理するか | workload identity policy, keyless auth, owner inventory |
| 09.23 | Data / object-level access | データ・オブジェクト単位の認可をどう担保するか | object authorization tests, data policy, access log |
| 09.24 | Audit / evidence / logging | 認証・認可・変更の証跡をどう保持するか | audit log pipeline, evidence pack, SIEM mapping |
| 09.25 | Incident response / revocation | 侵害時に何を無効化・回転・調査するか | token revocation runbook, key rotation, session kill procedure |
| 09.26 | Maturity / continuous assurance | IAM をどう継続改善するか | IAM scorecard, maturity model, risk posture dashboard |

---

## 3. Frontier Exemplars

| 候補 | Evidence Tier | 採用理由 | 移植可能な設計原理 |
|---|---:|---|---|
| NIST SP 800-63-4 / 63B / 63C | T0 | identity proofing, authentication, authenticator management, federation を分けて整理する規範的一次情報。2025 年版では継続評価、fraud/deepfake、syncable authenticators も扱う。[S01][S02][S03] | ID 保証レベル、認証保証レベル、フェデレーション保証レベルをリスク別に分解する。 |
| NIST SP 800-162 ABAC | T0 | subject, object, operation, environment 属性によるアクセス制御モデルを定義する。[S04] | RBAC で粗く標準化し、ABAC/ReBAC で文脈・データ・関係を扱う。 |
| NIST SP 800-207 Zero Trust | T0 | ネットワーク位置を信頼根拠にせず、ユーザー・資産・リソース単位の継続認証・認可を基礎にする。[S05] | アクセスを「場所」ではなく「主体・デバイス・リソース・行為・リスク」の決定に変換する。 |
| IETF OAuth 2.0 / Security BCP / Bearer / DPoP | T0 | 委任認可、bearer token 保護、最新の OAuth セキュリティ BCP、sender-constrained token を規定する。[S06][S07][S08][S09] | OAuth を「ログイン」ではなく委任認可と token governance として設計する。 |
| OpenID Connect Core | T0 | OAuth 2.0 上の identity layer として ID token と claims を標準化する。[S10] | 認証用途では OAuth 単体ではなく OIDC を使い、issuer/audience/expiry/signature を検証する。 |
| OASIS SAML | T0 | XML assertion による security domain 間の federation / enterprise SSO を標準化する。[S11] | レガシー・エンタープライズ SSO では SAML metadata, signing cert, assertion condition を運用管理する。 |
| IETF SCIM 2.0 | T0 | users, groups, service provider config を JSON/HTTP で表現し、クロスドメイン ID 管理を標準化する。[S12][S13] | IdP とアプリ間のユーザー・グループ自動プロビジョニング、特に deprovisioning を標準化する。 |
| W3C WebAuthn / FIDO-style credentials | T0 | RP-scoped public key credentials による phishing-resistant authentication を提供する。[S14] | パスワード・SMS 依存から passkey / hardware-bound credential へ移行する。 |
| AWS IAM / IAM Access Analyzer / IAM Identity Center | T2/T3 | explicit deny, permission boundary, resource policy, ABAC, least privilege analysis, SCIM provisioning を公開ドキュメントで説明する。[S16][S17][S18][S19] | ポリシー評価順序、least privilege 分析、SCIM 自動化を運用に組み込む。 |
| Google Cloud IAM / service account guidance | T2/T3 | allow/deny/principal access boundary の評価と、service account / keyless best practice を公開する。[S20][S21] | 非人間 ID を専用資産として扱い、長期鍵を避け、所有者・用途・権限を管理する。 |
| Microsoft Entra ID Governance / PIM / Lifecycle Workflows | T2/T3 | access reviews, entitlement management, privileged identity management, lifecycle automation を公開する。[S22][S23][S24][S25] | アクセスを request, approval, assignment, expiration, review のライフサイクルにする。 |
| Okta Identity Governance / Access Certifications / App Policies | T2/T3 | access certification, resource owner, sign-on policy, device/location/risk 条件を公開する。[S26][S27][S28] | アクセスレビューをキャンペーン化し、アプリ別条件と自動 remediation を運用する。 |
| CyberArk PAM / JIT / Zero Standing Privileges | T2/T3 | privileged access を JIT / ZSP で一時化し、承認・時間制限・監査を組み合わせる。[S29][S30] | 常設特権を廃止し、必要時だけ権限を作成し、使用後に削除する。 |
| GitHub Enterprise IAM / SCIM / PAT / Audit Logs | T2/T3 | SAML SSO, SCIM, fine-grained PAT, audit logs の設計を公開する。[S35][S36][S37] | 開発者トークンと組織メンバーシップをアプリ横断の IAM 統制に含める。 |
| Kubernetes RBAC | T2/T3 | Role, ClusterRole, RoleBinding, ClusterRoleBinding で API リソースへの authorization を定義する。[S38] | クラウドネイティブ環境では API resource 単位に RBAC を設計する。 |
| OWASP Authorization / MFA / Session / API BOLA guidance | T3/T5 | deny by default, every-request authorization, MFA, session safety, object-level authorization failureを実装観点で整理する。[S31][S32][S33][S34] | 認証後の application/data authorization を別制御として検証する。 |
| Microsoft Storm-0558 / Okta / Cloudflare public incident analyses | T5 | token forgery, signing key leakage, support-system compromise, stale service credentials の失敗条件を観測できる。[S39][S40][S41][S42] | IAM は侵害時の revocation, key isolation, token rotation, audit visibility まで設計する。 |

### Candidate Score（公開証拠密度ベース）

| Candidate family | Performance | Adoption | Artifact richness | Peer validation | Recency | Transferability | Failure evidence | Score /100 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| NIST 800-63 / 800-53 / ZTA / ABAC | 5 | 5 | 5 | 5 | 5 | 5 | 3 | 96 |
| IETF OAuth / DPoP / Bearer | 5 | 5 | 5 | 5 | 5 | 5 | 4 | 98 |
| OpenID Connect | 5 | 5 | 5 | 5 | 4 | 5 | 3 | 94 |
| SCIM | 4 | 4 | 5 | 5 | 4 | 5 | 3 | 89 |
| WebAuthn / passkeys | 5 | 4 | 5 | 5 | 5 | 4 | 3 | 91 |
| AWS IAM | 5 | 5 | 5 | 4 | 5 | 4 | 4 | 92 |
| Microsoft Entra Governance / PIM | 5 | 5 | 5 | 4 | 5 | 4 | 4 | 92 |
| Google Cloud IAM | 5 | 5 | 5 | 4 | 5 | 4 | 3 | 90 |
| Okta Identity Governance | 4 | 5 | 5 | 3 | 5 | 4 | 5 | 86 |
| CyberArk PAM | 4 | 4 | 4 | 3 | 5 | 4 | 4 | 82 |
| GitHub Enterprise IAM | 4 | 5 | 5 | 3 | 5 | 4 | 4 | 85 |
| Kubernetes RBAC | 4 | 5 | 5 | 4 | 5 | 4 | 2 | 84 |
| OWASP authorization guidance | 4 | 5 | 4 | 4 | 5 | 5 | 5 | 90 |

---

## 4. Evidence Map

| Claim ID | 主張 | Evidence | Confidence |
|---|---|---|---|
| C-001 | IAM は identity proofing, authentication, federation を別々の保証レベルとして扱うべきである。 | NIST SP 800-63-4 / 63B / 63C。[S01][S02][S03] | A |
| C-002 | 認証器、セッション、資格情報は、発行時だけでなく、紛失・盗難・失効・同期・回復まで lifecycle 管理が必要である。 | NIST SP 800-63B-4。[S02] | A |
| C-003 | syncable passkeys は usability を上げるが、暗号鍵の同期、central IDM、revocation/key review の設計を必要とする。 | NIST 63B-4, WebAuthn。[S02][S14] | A |
| C-004 | OAuth は delegated authorization であり、bearer token は possession だけでアクセスできるため、保管・転送・スコープ・replay 対策が重要である。 | RFC 6749, RFC 6750, RFC 9700, RFC 9449。[S06][S07][S08][S09] | A |
| C-005 | OIDC は OAuth 2.0 上の authentication layer であり、ID token / claims validation を必要とする。 | OpenID Connect Core。[S10] | A |
| C-006 | SAML は enterprise federation / SSO の assertion 交換基盤であり、署名・条件・audience・metadata 運用が制御点になる。 | OASIS SAML technical overview。[S11] | A |
| C-007 | SCIM は user/group のクロスドメイン provisioning を標準化し、deprovisioning gap を閉じるための中核インタフェースである。 | RFC 7643/7644, AWS IAM Identity Center, GitHub SCIM。[S12][S13][S19][S36] | A |
| C-008 | Authorization は deny by default と every-request permission validation を前提にすべきであり、隠し ID や UI 非表示は権限制御ではない。 | OWASP Authorization, OWASP API BOLA。[S31][S34] | A |
| C-009 | RBAC は職務の粗い標準化に適し、ABAC/ReBAC は属性・関係・環境文脈による動的判定に適する。 | NIST ABAC, Kubernetes RBAC, OWASP Authorization。[S04][S31][S38] | B |
| C-010 | Cloud IAM では identity policy, resource policy, permission boundary, deny policy, principal access boundary など複数 policy family の評価順序が実際のアクセス決定を左右する。 | AWS IAM, Google Cloud IAM。[S16][S20] | A |
| C-011 | Access governance は group membership ではなく、request, approval, assignment, expiration, review, remediation の継続プロセスである。 | Microsoft Entra, Okta Identity Governance。[S22][S23][S26][S27] | A |
| C-012 | Privileged access の frontier pattern は standing admin を最小化し、JIT / PIM / PAM / ZSP で時間制限・承認・監査をかけることである。 | Microsoft PIM, CyberArk JIT/ZSP。[S24][S29][S30] | A |
| C-013 | Non-human identity は user と同じ扱いでは不十分であり、service account owner, keyless auth, token rotation, least privilege が必要である。 | Google Cloud service account guidance, Cloudflare incident。[S21][S41] | A |
| C-014 | Data access は IdP では完結せず、object-level / row-level / resource-level authorization checks をアプリケーション・データ層で行う必要がある。 | OWASP API BOLA, OWASP Authorization。[S31][S34] | A |
| C-015 | IAM の失敗は、signing key leakage, token forgery, stale service credentials, insufficient logging, incomplete revocation で大きな blast radius を持つ。 | Microsoft Storm-0558, Okta, Cloudflare。[S39][S40][S41][S42] | A |
| C-016 | トークンや PAT は期限、スコープ、承認、利用状況に基づき管理すべきで、classic/broad token は縮小すべきである。 | GitHub PAT guidance, OAuth BCP。[S07][S35] | A |
| C-017 | Legacy protocol は MFA や modern auth と相性が悪く、条件付きアクセスや MFA を迂回する経路として扱う必要がある。 | Okta app sign-on policy guidance。[S28] | B |
| C-018 | IAM は監査可能性を成果物に含める必要があり、audit log は debugging, compliance, incident investigation に使う。 | GitHub audit logs, Microsoft/Okta/Cloudflare incident analyses。[S37][S39][S40][S41] | A |

---

## 5. Core Philosophy

1. **Identity is the control plane, not the login screen.** 先端組織は IAM を UI ログインではなく、ユーザー、デバイス、ワークロード、サービスアカウント、トークン、データ、管理操作を束ねる制御面として設計する。

2. **Access is a per-request decision.** アクセスは一度の認証で永続的に保証されるものではなく、subject, resource, action, environment, assurance, risk, entitlement, token/session state を入力にした都度判定である。[S04][S05][S31]

3. **Standing access decays unless justified.** 特権・外部アクセス・データアクセスは、明示的な business justification、owner、期限、review がなければ縮退または失効する設計にする。[S22][S23][S24][S30]

4. **Credentials and tokens are liabilities.** パスワード、refresh token, PAT, service account key, signing key は、機能ではなく漏えい時の負債として扱う。短命化、スコープ制限、sender constraint、keyless auth、replay resistance、revocation を設計に含める。[S07][S08][S09][S21][S35]

5. **Federation without lifecycle is incomplete.** SSO だけでは不十分である。SCIM、JML workflow、access review、deprovisioning、token revocation がなければ、退職者・異動者・外部ユーザー・自動化 ID が残存する。[S12][S13][S19][S22][S36]

6. **Central IAM cannot replace application/data authorization.** IdP は認証と粗い認可の中心になれるが、object-level / data-level authorization はアプリケーションやデータ制御面で実装しなければならない。[S31][S34]

---

## 6. Decision Model

### Inputs

- HRIS / contractor / vendor source-of-truth events: joiner, mover, leaver, sponsor change, contract end.
- Identity attributes: user type, employment status, manager, department, geography, tenant, group, externalId, assurance level.
- Device and workload posture: managed/unmanaged, compliance, workload identity provider, service account owner, key age.
- Authentication state: method, AAL/FAL, MFA type, passkey/hardware token, session age, recent step-up.
- Token state: issuer, audience, scope, expiration, refreshability, sender constraint, revocation status, PAT approval.
- Resource attributes: app, API, cloud account/project/subscription, Kubernetes namespace, data classification, owner, environment.
- Action attributes: read/write/admin/export/delete/impersonate/secrets/signing-key access.
- Environment/risk: network, location, impossible travel, threat intelligence, incident mode, support session, change window.
- Policy catalog: RBAC roles, ABAC rules, SoD constraints, deny policies, boundaries, access packages, PIM/PAM policies.
- Governance signals: access review results, exception age, unused access, external access findings, audit findings.

### Decision Object

`allow`, `deny`, `step-up`, `JIT elevation`, `time-bound assignment`, `deprovision`, `session termination`, `token revocation`, `key rotation`, `manual review`, or `break-glass` for a subject-resource-action tuple.

### Criteria

- Least privilege and need-to-know.
- Deny by default.
- Every-request authorization for APIs and object/data access.
- Authentication assurance proportional to resource sensitivity and action risk.
- Time-bound and owner-backed access.
- Separation of duties for privileged and financial/regulatory operations.
- Explicit auditability: who approved, why, for how long, and under which policy.
- Revocability under incident conditions.
- Federation interoperability without lifecycle gaps.
- Non-human identity parity: workload and service identities receive owners, expiry, rotation, logs, and least privilege.

### Priorities

1. Establish IdP and authoritative lifecycle source before broad app integration.
2. Put privileged users, service accounts, external users, and high-risk data behind stricter controls first.
3. Prefer phishing-resistant MFA/passkeys for privileged and high-risk access.
4. Use OIDC/OAuth/SAML for standards-based federation, but pair SSO with SCIM/deprovisioning and token revocation.
5. Use RBAC for stable job-function bundles; use ABAC/ReBAC for contextual and data/object decisions.
6. Make PIM/PAM/JIT the default for administrative roles; reduce standing privilege.
7. Treat application authorization and data authorization as first-class controls, not IdP side effects.
8. Automate evidence collection for audit, access reviews, and incident response.

### Prohibitions

- Shared admin accounts, except explicitly sealed break-glass accounts with hardware MFA, vaulting, alerting, and post-use review.
- Permanent global administrator assignments as a default operating model.
- Long-lived bearer tokens, PATs, refresh tokens, or service account keys without owner, expiry, scope, and revocation path.
- OAuth used as authentication without OIDC or equivalent identity validation.
- Manual app-side accounts that bypass SCIM/JML deprovisioning.
- Authorization based on hidden object IDs, UI-only checks, or client-side checks.
- Legacy protocols that bypass MFA or modern conditional access, unless isolated under a documented exception.
- Catch-all allow policies without a terminal deny/step-up control.
- Access reviews that only certify group names without mapping effective entitlements and data/actions.

### Thresholds and Operating Defaults

These are clone defaults, not universal compliance requirements. They should be tuned by risk class.

| Control | Default threshold | Rationale / evidence |
|---|---|---|
| Privileged MFA | 100% of privileged interactive users; phishing-resistant preferred | Passkeys/WebAuthn and MFA guidance; privileged blast radius is high.[S14][S24][S33] |
| Privileged access duration | JIT, time-bound, default hours not days; standing admin minimized | Microsoft PIM and CyberArk JIT/ZSP model.[S24][S29][S30] |
| Access reviews | Quarterly for privileged, external, sensitive data; semiannual/annual for lower-risk; event-triggered after incidents and org changes | Microsoft supports recurring weekly/monthly/quarterly/annually reviews; Okta supports campaigns and incident-triggered reviews.[S22][S26] |
| SCIM token rotation/monitoring | Alert before expiry; dedicated SCIM service identity; synchronization failure is security event | AWS notes SCIM token expiry can stop synchronization; GitHub notes SCIM automation depends on the authorizing identity.[S19][S36] |
| PAT/API tokens | Fine-grained, resource-scoped, approved where possible, expiration required, unused token detection | GitHub recommends fine-grained tokens and notes broad classic tokens are riskier.[S35] |
| Service account keys | Avoid long-lived keys where possible; owner and rotation mandatory if unavoidable | Google Cloud recommends avoiding service account keys and managing/identifying unused service accounts.[S21] |
| Token replay risk | Sender-constrained tokens for high-risk APIs; short lifetimes for bearer tokens | RFC 9449 DPoP and OAuth Security BCP.[S07][S09] |
| Object-level authorization | Test every external API endpoint and sensitive internal endpoint for object-level access | OWASP API BOLA identifies object ID manipulation as a major failure mode.[S34] |
| Break-glass | 2+ accounts, hardware MFA, offline/vaulted credential, alert on use, post-use review within 24h | Derived from PIM/PAM and incident response best practice; exact threshold is organization-specific. |

### Owners and Reviewers

| Role | Accountability |
|---|---|
| CISO / security architecture owner | IAM control philosophy, risk acceptance, policy hierarchy, incident revocation posture |
| IAM platform owner | IdP, federation, SCIM, MFA/passkeys, session/token controls, access review tooling |
| Cloud platform owner | AWS/GCP/Azure IAM, service accounts, cloud role catalog, access analyzer/CIEM findings |
| Application owner | App SSO, object-level authorization, entitlement mapping, audit events |
| Data owner / data steward | Data classification, data access policy, high-risk data approvals, row/object controls |
| Resource owner / group owner | Access package ownership, group membership justification, review completion |
| Privileged access owner | PIM/PAM/JIT policies, break-glass runbook, admin session evidence |
| SOC / incident response | Token/key/session revocation, suspicious access detection, blast-radius analysis |
| Compliance / audit | Evidence retention, certification completeness, control exceptions |

### Cadence

- **App onboarding**: before production, each app must have SSO/federation design, provisioning/deprovisioning path, role/entitlement map, object-level authorization assessment, logging plan, and owner.
- **Policy change**: role/policy changes go through review, tests, and deployment evidence.
- **Runtime**: authentication and authorization decisions are evaluated per request or per session boundary depending on resource sensitivity.
- **Access review**: recurring campaigns by app, group, privileged role, external user, data set, and exception register.
- **Incident mode**: immediate token/session revocation, key rotation, deprovision verification, audit-log review, and after-action remediation.
- **Annual architecture review**: standards drift, OAuth/OIDC/SAML/SCIM config, passkey rollout, service account risk, PAM coverage, authorization test coverage.

---

## 7. Operating Model

### 7.1 App and Resource Onboarding Process

1. Classify the resource: application, API, cloud account/project, data product, Kubernetes namespace, privileged platform, SaaS tenant.
2. Identify owner and data steward.
3. Select federation pattern: OIDC for modern app authentication, OAuth for delegation, SAML for enterprise SSO/legacy SaaS, SCIM for lifecycle.
4. Define subject set: employees, contractors, guests, service accounts, workloads, agents, support users.
5. Define entitlements: roles, permissions, data scopes, admin actions, break-glass path.
6. Choose authorization model: RBAC for stable jobs, ABAC/ReBAC for dynamic context and object/data decisions.
7. Configure policy: deny-by-default, step-up MFA, device/risk/location conditions, expiry, SoD checks.
8. Configure provisioning: SCIM or equivalent automated lifecycle, externalId mapping, ownership transfer, deprovision test.
9. Configure logs: authentication, token issuance, policy decision, privilege elevation, entitlement changes, object access where sensitive.
10. Threat-model failure modes: BOLA, stale tokens, signing cert expiry, SCIM failure, legacy protocol bypass, support/admin escalation abuse.

### 7.2 Request / Approval / Entitlement Workflow

1. User or automation requests access package.
2. System checks eligibility, source-of-truth status, SoD rules, requester risk, existing access, and expiration policy.
3. Resource owner or manager approves based on business justification.
4. Assignment is time-bound where feasible.
5. Assignment is propagated through IdP, SCIM, cloud IAM, application policy, or data policy.
6. Logs and evidence are recorded.
7. Access is reviewed or auto-expired.

### 7.3 Runtime Access Flow

1. Subject authenticates to IdP or workload identity provider.
2. Authentication method is mapped to assurance and risk.
3. Session is created with explicit lifetime and reauthentication triggers.
4. Token is issued with issuer, audience, scope, expiration, and optional sender constraint.
5. PDP evaluates identity, device/workload, resource, action, environment, and policy.
6. PEP enforces decision in app, API gateway, cloud control plane, Kubernetes API, or data access layer.
7. Sensitive object/data access performs application/data-layer authorization, not just endpoint-level authorization.
8. Audit event records subject, resource, action, result, policy ID, token/session context, and correlation ID.

### 7.4 Privileged Access Flow

1. Privileged access is normally not standing.
2. User requests elevation for a role/resource/action and duration.
3. System performs step-up authentication, eligibility, SoD, device/risk checks, and approval if required.
4. PIM/PAM grants a temporary role, local group membership, credential checkout, or session proxy.
5. Session is logged and optionally recorded.
6. Grant expires automatically or is revoked at task completion.
7. Access is reviewed; anomalies trigger investigation.

### 7.5 Joiner-Mover-Leaver Lifecycle

| Event | Required control |
|---|---|
| Joiner | Create identity from authoritative source; assign birthright access; require MFA/passkey enrollment; provision baseline app/group entitlements. |
| Mover | Add new role-based entitlements; remove old entitlements; trigger high-risk access review; update manager, department, geography, data scope. |
| Leaver | Disable sign-in, revoke sessions/tokens, SCIM deprovision apps, remove groups, transfer ownership of service accounts/repos/data, preserve audit evidence. |
| Vendor/guest expiry | Sponsor review; auto-expire by contract end; revoke federation and app assignments; remove external collaboration artifacts. |
| Service account owner change | Reassign owner; validate purpose; rotate keys/tokens; review permissions; disable if unused. |

---

## 8. Technical / Business Specification

### 8.1 Identity, Account, Tenant, Org, Group

- Assign immutable subject IDs. Email, display name, username, and department are mutable attributes and must not be primary authorization keys.
- Maintain an identity taxonomy: employee, contractor, vendor, guest, customer, service account, workload, agent/bot, break-glass account.
- Treat tenant/org/group as authorization context, not proof of identity.
- Groups must have owner, purpose, membership source, expiry/review cadence, and downstream entitlement mapping.
- Avoid nested group structures that obscure effective access unless tooling can compute and review them.
- For external identities, maintain sponsor, contract end, data scope, and review cadence.

### 8.2 Credentials, Passwords, MFA, Passkeys

- Password controls should focus on breached-password blocklists, secure hashing, rate limiting, and recovery abuse prevention, not arbitrary complexity alone.[S02]
- MFA is required for privileged access, sensitive data, admin portals, financial/production operations, and external access where feasible.
- Prefer phishing-resistant authenticators: WebAuthn/FIDO2/passkeys or hardware-backed credentials for high-risk populations.[S14]
- Maintain at least two recovery paths for critical users, but require step-up/reproofing and alerting for authenticator reset.
- For syncable passkeys, explicitly design sync fabric risk, account recovery, authenticator revocation, periodic key review, and central identity management integration.[S02]
- Notify users and security systems when authenticators are added, removed, or reset.

### 8.3 Session and Token Management

- Sessions must have lifetime, inactivity timeout, reauthentication triggers, and step-up conditions.
- Access tokens must be audience-bound, scoped, short-lived relative to sensitivity, and revocable.
- Refresh tokens and PATs require stronger controls: rotation, theft detection, inactivity expiry, approval, device binding or sender constraint for high-risk APIs.
- Bearer tokens must be protected in transport and storage; possession equals access unless additional sender constraints are used.[S08][S09]
- Prefer DPoP, mTLS, or other proof-of-possession approaches for high-risk delegation to reduce replay risk.[S09]
- Token revocation must be part of incident response, not a manual afterthought.

### 8.4 OAuth, OIDC, SAML, Federation, SSO

- Use OAuth 2.0 for delegated authorization; do not treat OAuth alone as user authentication.[S06]
- Use OIDC for authentication, with strict validation of issuer, audience, expiry, nonce/state, signature, JWKS rotation, and required claims.[S10]
- Use authorization code with PKCE for public/native/browser clients; avoid deprecated or insecure flows identified by OAuth security BCP.[S07]
- Strictly validate redirect URIs and client registration.
- Use least-privilege scopes and resource-specific tokens.
- Use SAML for enterprise SSO where required, with signed assertions, audience/recipient validation, condition enforcement, metadata ownership, and certificate rotation runbooks.[S11]
- Pair SSO with SCIM or equivalent provisioning/deprovisioning. SSO without lifecycle automation leaves residual app accounts and tokens.[S12][S13][S36]

### 8.5 RBAC, ABAC, ReBAC, Policy Evaluation

- Use RBAC for stable enterprise job functions and platform roles.
- Use ABAC for context-dependent decisions: data sensitivity, geography, device posture, business unit, resource label, time, environment, ownership, project, or risk.[S04]
- Use ReBAC where relationships matter: document owner, repository collaborator, team member, manager chain, tenant membership, delegated admin.
- Enforce deny-by-default and every-request authorization for APIs and sensitive data paths.[S31]
- Cloud IAM must model evaluation order explicitly. AWS combines identity/resource policies but applies boundaries and explicit deny; Google Cloud evaluates principal access boundaries, deny policies, and allow policies.[S16][S20]
- Policy changes should be versioned, tested, reviewed, and deployed through controlled pipelines.

### 8.6 Provisioning and Deprovisioning

- Use SCIM 2.0 or equivalent standard lifecycle automation wherever the SaaS/app supports it.[S12][S13]
- Map stable external IDs; do not rely only on email for identity linkage.
- Monitor provisioning sync status, token expiry, connector health, and failed deprovisioning.
- SCIM authorizing identities should be dedicated service identities, not ordinary admin users who may leave the organization.[S36]
- If SCIM tokens expire or connectors fail, treat the event as security-relevant because deprovisioning can silently stop.[S19]

### 8.7 Access Review and Certification

- Reviews should cover effective entitlements, not only group names.
- Prioritize privileged roles, external users, sensitive data, production environments, broad tokens, service accounts, and exception grants.
- Reviewers should be resource owners, data owners, managers, or security owners depending on entitlement type.
- Campaigns should record decision, justification, reviewer, timestamp, remediation, and unresolved exceptions.[S22][S26]
- Incident-triggered reviews should be supported for affected apps, groups, users, tokens, or service accounts.[S26]

### 8.8 Privileged Access

- Use PIM/PAM/JIT for privileged roles and eliminate standing admin by default.[S24][S29][S30]
- Require step-up authentication and, where appropriate, approval for elevation.
- Scope elevation to role, resource, operation, and duration.
- Auto-remove elevated permissions after expiry.
- Monitor and record privileged sessions where risk warrants it.
- Maintain controlled break-glass accounts for availability, but vault, alert, review, and rotate them.

### 8.9 Non-human Identity

- Service accounts and workload identities require owner, purpose, environment, resource scope, credential type, rotation policy, and last-used signal.
- Prefer workload identity federation, managed identities, or IAM Credentials APIs over long-lived keys.[S21]
- Disable unused service accounts and remove default broad roles.
- Automation tokens should be fine-grained, repository/resource-scoped, approved where possible, and expiry-bound.[S35]
- Incident response must include non-human credentials. Cloudflare’s 2023 incident showed that stale service tokens and service account credentials can preserve attacker access after human identity cleanup.[S41]

### 8.10 Data and Object-level Access

- Data authorization inputs should include user, tenant, group, role, object owner, data classification, purpose, geography, action, and consent/legal constraints where applicable.
- Every endpoint that accesses an object by ID must enforce object-level authorization.[S34]
- Do not rely on unguessable IDs, hidden UI elements, or client-side filtering as authorization.
- High-risk data operations such as export, delete, impersonation, sharing, and admin read require step-up, approval, or stronger logging.
- Store audit records with subject, resource/object, action, decision, policy ID, data class, and correlation ID.

---

## 9. Metrics

| Category | Metrics |
|---|---|
| Identity coverage | % apps behind SSO, % apps with SCIM, % identities with source-of-truth, stale guest count, orphan account count |
| Credential / MFA | MFA coverage, phishing-resistant MFA coverage, privileged MFA coverage, authenticator reset rate, suspicious recovery attempts |
| Session / token | token age distribution, idle tokens, revoked leaked tokens, PAT count by scope/expiry, refresh token reuse anomalies |
| Authorization | unused permissions, explicit-deny hits, policy test coverage, role count, role entropy, group owner coverage, SoD violations |
| Provisioning | joiner provisioning SLA, mover cleanup latency, leaver deprovision completion, SCIM failure rate, connector token expiry risk |
| Privileged access | standing admin count, JIT grant count, median privilege duration, break-glass usage, PIM review completion, privileged session anomalies |
| Non-human identity | service accounts with owner, keys older than threshold, unused service accounts, workload identity adoption, automation token expiry compliance |
| Data access | object-level authorization test coverage, blocked unauthorized object access, sensitive export volume, high-risk data approval completion |
| Governance | access review completion, remediation completion, exception age, review overturn rate, resource owner coverage |
| Incident readiness | time to revoke sessions/tokens, time to rotate keys, blast-radius determination time, audit log completeness, post-incident access review completion |

---

## 10. Failure Modes

| Failure mode | Mechanism | Prevention / detection |
|---|---|---|
| Token forgery or signing key compromise | Attacker obtains signing key or validation gap, creating trusted tokens | key isolation, HSM/secure enclave, strict issuer/audience validation, signing-key rotation, anomaly detection, token revocation runbook; Storm-0558 illustrates this class.[S39][S42] |
| Bearer token replay | Token theft from endpoint/log/browser/storage enables access by possession | TLS, secure storage, short lifetimes, sender-constrained tokens, DPoP/mTLS, refresh token rotation.[S08][S09] |
| SCIM / lifecycle failure | Sync stops because connector token expires or authorizing user leaves; accounts remain | dedicated SCIM identity, expiry alerting, connector monitoring, deprovision reconciliation.[S19][S36] |
| Stale service credentials | Human credentials rotated but service tokens/keys remain active | non-human inventory, keyless auth, automatic rotation, stale-key detection, incident credential sweep; Cloudflare incident demonstrates this risk.[S21][S41] |
| Support/admin system compromise | Administrative support logs or tools expose tokens/session data | support-access least privilege, sensitive log minimization, session binding, admin step-up, data retention controls; Okta incident drove additional safeguards.[S40] |
| Role and group sprawl | Roles accumulate, groups lose owners, effective access becomes unknowable | role catalog, owner registry, access analyzer, periodic reviews, role mining, unused permission removal.[S18][S22] |
| Authorization stops at login | App assumes SSO authentication implies object/data authorization | object-level checks, deny by default, authorization tests, data policy enforcement.[S31][S34] |
| Legacy protocol MFA bypass | POP/IMAP or older clients cannot enforce MFA/conditional access | disable legacy protocol, migrate to modern auth, isolate exceptions, monitor usage.[S28] |
| Excessive standing admin | Admin rights remain assigned permanently | PIM/PAM/JIT/ZSP, approval, time-bound grants, recurring privileged review.[S24][S29][S30] |
| Broad developer tokens | Classic PAT/API tokens have broad repo/org access and no expiration | fine-grained PATs, org owner approval, expiration, unused-token revocation.[S35] |
| Break-glass abuse | Emergency account is used as shadow admin | vaulting, hardware MFA, alerts, post-use review, password/key rotation. |
| Policy evaluation misunderstanding | Operators assume allow policy works without considering explicit deny/boundary/PAB | documented evaluation model, policy simulation, automated analyzer, regression tests.[S16][S20] |

---

## 11. Anti-patterns

- Treating SSO as equivalent to complete IAM.
- Using OAuth access tokens as proof of authentication without OIDC identity validation.
- Issuing long-lived bearer tokens without audience, scope, expiry, and revocation.
- Allowing service account keys by default because they are operationally convenient.
- Maintaining permanent global administrators as normal operating practice.
- Certifying access by asking reviewers to approve group names they cannot map to effective permissions.
- Depending on hidden object IDs or UI suppression instead of server-side authorization.
- Running access reviews only annually for privileged or high-risk data access.
- Letting SCIM be authorized by a normal employee account with no continuity plan.
- Using email address as immutable identity key.
- Keeping guest/vendor access without sponsor and expiry.
- Allowing broad classic PATs when fine-grained scoped tokens are available.
- Making break-glass accounts unmonitored to avoid false positives.
- Ignoring non-human credentials during identity incident response.

---

## 12. Historical Change Pattern

| Shift | Older model | Frontier model | Evidence |
|---|---|---|---|
| Perimeter trust to Zero Trust | Network location implied trust | Identity, device/workload, resource, action, and risk drive each decision | NIST Zero Trust.[S05] |
| Password + SMS MFA to phishing-resistant authentication | Password complexity and OTP dominate | Passkeys/WebAuthn/hardware-backed authenticators for high-risk use | NIST 63B, WebAuthn.[S02][S14] |
| OAuth permissive flows to hardened OAuth | Implicit/ROPC and broad bearer tokens | authorization code + PKCE, least scopes, token binding/sender constraint, BCP security posture | OAuth BCP, DPoP.[S07][S09] |
| SSO-only to SSO + lifecycle governance | Federation authenticates users but leaves app accounts | SCIM, JML workflows, access reviews, expiration, remediation | SCIM RFCs, Entra/Okta/GitHub docs.[S12][S13][S22][S26][S36] |
| Static RBAC to hybrid RBAC/ABAC/ReBAC | Coarse roles only | Roles for stable bundles; attributes/relationships for dynamic resource and data decisions | NIST ABAC, OWASP.[S04][S31] |
| Standing privilege to JIT/ZSP | Persistent admin roles | Time-bound elevation and auto-removal after use | Microsoft PIM, CyberArk.[S24][S29][S30] |
| Static service account keys to workload identity | Long-lived keys in automation | Keyless or short-lived workload identity and owner-based inventory | Google Cloud service account guidance.[S21] |
| Periodic audit to continuous assurance | Annual certification | Continuous findings, analyzer/recommender, event-triggered reviews, incident revocation | AWS Access Analyzer, Entra/Okta governance.[S18][S22][S26] |

---

## 13. Maturity Model

| Level | Name | Criteria |
|---:|---|---|
| 0 | 未整備 | App ごとに手動アカウント。中央 IdP なし。共有 admin が存在。退職時の削除は手作業。ログは断片的。 |
| 1 | 部分統合 | 主要 SaaS に SSO。MFA は一部。粗いグループ/RBAC。プロビジョニングは手動。service account と token は台帳外。 |
| 2 | 文書化 | IdP、MFA、主要アプリ SCIM、role catalog、access review、break-glass runbook、privileged accounts inventory がある。 |
| 3 | 標準化 | JML 自動化、SCIM monitoring、RBAC/ABAC policy-as-code、PIM/JIT、fine-grained token policy、service account ownership、audit pipeline が運用される。 |
| 4 | 自動化・計測 | access analyzer / CIEM / recommender、continuous access review、unused access remediation、passkey rollout、object-level authorization tests、token/key revocation automation が計測される。 |
| 5 | 自律改善・業界先端 | human/non-human identity control plane、zero standing privilege、real-time risk and continuous access evaluation、automated remediation、evidence-grade governance、data/object policy integration が閉ループ化している。 |

---

## 14. Clone Implementation Guide

### 0–30 days: Containment and inventory

- Create identity inventory: users, guests, service accounts, workloads, automation tokens, privileged accounts, break-glass accounts.
- Identify top 20 business-critical apps and top 20 data/production systems.
- Enforce MFA for all privileged interactive users.
- Disable or isolate legacy protocols that cannot enforce MFA.
- Freeze creation of shared admin accounts.
- Define break-glass account policy and logging.
- Collect IdP, cloud IAM, PAM/PIM, SaaS admin, GitHub, and key app audit logs into SIEM or equivalent.
- Begin stale token and service account key review.

### 31–60 days: Source-of-truth and standards

- Define identity taxonomy and immutable subject ID rules.
- Select authoritative lifecycle source for employees, contractors, vendors, and guests.
- Create role and entitlement catalog for critical apps.
- Register resource owners and group owners.
- Integrate critical apps with OIDC/SAML SSO.
- Enable SCIM where available and monitor provisioning failures.
- Establish token policy: expiry, scope, approval, revocation, fine-grained tokens.
- Launch first access review for privileged roles, external users, and sensitive data access.

### 61–90 days: Privilege and non-human identity hardening

- Put cloud/admin roles behind PIM/PAM/JIT.
- Remove standing admin where operationally feasible.
- Inventory service accounts and automation tokens; assign owner and purpose.
- Replace long-lived keys with workload identity or managed identity where feasible.
- Add policy-as-code tests for IAM roles and deny conditions.
- Implement object-level authorization tests for critical APIs.
- Add incident playbook for token revocation, session termination, key rotation, and SCIM deprovision verification.

### 91–180 days: Governance and automation

- Roll out phishing-resistant MFA/passkeys for administrators and high-risk users.
- Extend SCIM/lifecycle automation to remaining critical SaaS and internal apps.
- Build access packages with owner, approver, expiry, and review cadence.
- Deploy access analyzer / recommender / CIEM findings into remediation workflow.
- Implement ABAC/ReBAC for data or resource classes where RBAC is too coarse.
- Standardize OAuth/OIDC/SAML configuration review and certificate/JWKS rotation.
- Add continuous monitoring for SCIM sync failure, expired connectors, stale guests, unused permissions, and broad tokens.

### 181+ days: Continuous assurance

- Move privileged operations to zero standing privilege by default.
- Introduce continuous access evaluation with risk-triggered step-up/revocation.
- Integrate data classification and object-level policy into authorization systems.
- Automate access review recommendations and remediation while preserving owner accountability.
- Run IAM incident simulations: signing key compromise, token leak, service account leak, SCIM outage, IdP compromise, PIM failure.
- Maintain evidence packs for audits: policy version, approval, provisioning, review, remediation, and revocation proof.

---

## 15. Pattern Library

| Pattern ID | Pattern | Type | Description | Preconditions | Tradeoffs | Confidence |
|---|---|---|---|---|---|---|
| P-001 | Identity control plane | principle | Identity, device/workload, resource, action, environment, and risk are normalized into a central decision model. | IdP, source-of-truth, policy registry | Requires integration discipline and owner model. | A |
| P-002 | Federation + lifecycle pair | decision_rule | SSO integration is incomplete unless paired with provisioning/deprovisioning and review. | OIDC/SAML plus SCIM or equivalent | Some legacy apps lack SCIM; compensating controls needed. | A |
| P-003 | Hybrid RBAC/ABAC | operating_model | RBAC handles stable role bundles; ABAC/ReBAC handles dynamic resource/data decisions. | Attribute quality and policy tests | ABAC policy can become opaque without governance. | B |
| P-004 | Zero standing privilege | control | Privileged rights are created only when needed and removed automatically. | PIM/PAM/JIT tooling | Operational latency; break-glass needed. | A |
| P-005 | Non-human identity parity | control | Service accounts and workloads receive owner, lifecycle, least privilege, logs, and revocation path. | Inventory and automation | Keyless migration can require platform changes. | A |
| P-006 | Token as governed asset | control | Tokens are scoped, expiring, revocable, monitored, and sender-constrained where risk warrants. | Token inventory and issuers | Developer friction if not automated. | A |
| P-007 | Object-level authorization tests | control | Every sensitive object/data access path is tested for authorization bypass. | App testability and data model clarity | Requires app teams to own authz. | A |
| P-008 | Access review as remediation workflow | operating_model | Review campaigns produce revocation/remediation, not just attestation. | Resource owners and entitlement map | Review fatigue if scopes are too broad. | A |
| P-009 | Incident revocation closure | failure_pattern | Identity incident response includes token/session/key/service-account revocation. | Centralized logs and revocation APIs | Requires rehearsals and coverage across SaaS/cloud. | A |
| P-010 | Break-glass with evidence | control | Emergency access exists but is vaulted, monitored, and reviewed post-use. | PAM/vault/logging | Risk of underuse or misuse if too complex. | B |

---

## 16. QA / Validation Queries

| Query | Purpose | Claim tested |
|---|---|---|
| `site:nist.gov "800-63B-4" "authenticator" "session"` | NIST authentication/session/authenticator lifecycleの現行確認 | C-001, C-002 |
| `site:datatracker.ietf.org "RFC 9700" OAuth "implicit" "security"` | OAuth Security BCP と非推奨フロー確認 | C-004 |
| `site:openid.net/specs "OpenID Connect Core" "ID Token"` | OIDC が authentication layer であることの確認 | C-005 |
| `site:docs.oasis-open.org/security/saml "assertion" "single sign-on"` | SAML assertion / SSO の確認 | C-006 |
| `site:datatracker.ietf.org "RFC 7644" SCIM "Users" "Groups"` | SCIM protocol と user/group provisioning の確認 | C-007 |
| `site:docs.aws.amazon.com/IAM "explicit deny" "permissions boundary"` | AWS policy evaluation model の確認 | C-010 |
| `site:docs.cloud.google.com/iam "principal access boundary" "deny policies"` | Google Cloud IAM evaluation model の確認 | C-010 |
| `site:learn.microsoft.com/entra "access reviews" "privileged roles"` | Access review と privileged role review の確認 | C-011, C-012 |
| `site:docs.cyberark.com "Just in Time access" "expiration"` | JIT privileged access の時間制限確認 | C-012 |
| `site:docs.github.com SCIM automatic deprovisioning authorized tokens` | SCIM と deprovisioning/token persistence の確認 | C-007 |
| `site:owasp.org "Broken Object Level Authorization" "object ID"` | Object-level authorization failure の確認 | C-014 |
| `site:blog.cloudflare.com "failed to rotate" "service" "token"` | stale service token failure の確認 | C-013, C-015 |
| `site:microsoft.com/security "Storm-0558" "signing key" "token"` | signing key / forged token incident の確認 | C-015 |
| `site:sec.okta.com "Zero Standing Privileges" "IP binding"` | Okta incident後の補強策確認 | C-015 |

---

## 17. Confidence & Unknowns

### Confidence A

- NIST, IETF, OpenID, OASIS, SCIM, W3C, OWASP, major cloud/platform docs で裏付けられる標準的 IAM 原則。
- OAuth/OIDC/SAML/SCIM/WebAuthn の役割分担。
- Bearer token, token replay, SCIM deprovisioning, privileged access, service account key risk, object-level authorization の主要失敗モード。
- Microsoft Storm-0558, Okta, Cloudflare など公開インシデントで観測できる失敗条件。

### Confidence B

- RBAC/ABAC/ReBAC の使い分けと移行順序。標準と実装例から強く推定できるが、組織ごとのデータモデルで最適解が変わる。
- Break-glass の推奨個数・レビュー SLA・特権時間単位などの定量閾値。PIM/PAM 原則から導けるが、事業継続要件によって調整が必要。
- Access review の頻度。Microsoft/Okta などは多様な recurrence を示すが、規制・データ分類・リスクで変わる。

### Confidence C

- 各ベンダー内部の実際の運用会議体、承認階層、例外処理 SLA。
- 非公開の incident lessons learned と内部 detection thresholds。
- パスキー導入率や各企業の実運用上の failure rates。

### Unknowns / Additional Research

- 対象組織の現行アプリ数、IdP 構成、SCIM 対応率、service account 数、権限体系、監査要件。
- データ分類体系と object-level authorization の実装状況。
- 現在の PIM/PAM の対象範囲と break-glass 利用履歴。
- API / SaaS / cloud それぞれの token inventory と revocation API coverage。
- 既存のアクセスレビューが effective entitlement を見ているか、単なる group membership を見ているか。

---

## 18. Source Catalog

| ID | Source | Entity | Tier | Primary use |
|---|---|---:|---:|---|
| S01 | [NIST Digital Identity Guidelines SP 800-63-4](https://pages.nist.gov/800-63-4/) | NIST | T0 | identity proofing / authentication / federation baseline |
| S02 | [NIST SP 800-63B-4 Authentication and Authenticator Management](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-63B-4.pdf) | NIST | T0 | authenticator, password, MFA, session, syncable authenticator |
| S03 | [NIST SP 800-63C-4 Federation and Assertions](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-63C-4.pdf) | NIST | T0 | federation, assertions, CSP/RP model |
| S04 | [NIST SP 800-162 Attribute Based Access Control](https://csrc.nist.gov/pubs/sp/800/162/upd2/final) | NIST | T0 | ABAC model |
| S05 | [NIST SP 800-207 Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/800/207/final) | NIST | T0 | zero trust decision framing |
| S06 | [RFC 6749 OAuth 2.0 Authorization Framework](https://datatracker.ietf.org/doc/html/rfc6749) | IETF | T0 | delegated authorization |
| S07 | [RFC 9700 OAuth 2.0 Security Best Current Practice](https://datatracker.ietf.org/doc/rfc9700/) | IETF | T0 | OAuth hardening / deprecated modes |
| S08 | [RFC 6750 Bearer Token Usage](https://datatracker.ietf.org/doc/html/rfc6750) | IETF | T0 | bearer token risk |
| S09 | [RFC 9449 Demonstrating Proof of Possession at the Application Layer](https://www.rfc-editor.org/rfc/rfc9449.html) | IETF | T0 | sender-constrained tokens |
| S10 | [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html) | OpenID Foundation | T0 | identity layer / ID token |
| S11 | [OASIS SAML Technical Overview](https://docs.oasis-open.org/security/saml/Post2.0/sstc-saml-tech-overview-2.0.html) | OASIS | T0 | SAML federation / SSO |
| S12 | [RFC 7644 SCIM Protocol](https://datatracker.ietf.org/doc/html/rfc7644) | IETF | T0 | provisioning protocol |
| S13 | [RFC 7643 SCIM Core Schema](https://www.rfc-editor.org/rfc/rfc7643.html) | IETF | T0 | user/group schema |
| S14 | [W3C Web Authentication Level 3](https://www.w3.org/TR/webauthn-3/) | W3C | T0 | passkeys / public key credentials |
| S15 | [CISA Zero Trust Maturity Model](https://www.cisa.gov/zero-trust-maturity-model) | CISA | T0/T3 | identity pillar and maturity framing |
| S16 | [AWS IAM Policy Evaluation Logic](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html) | AWS | T2 | policy evaluation, explicit deny, boundary |
| S17 | [AWS IAM ABAC](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction_attribute-based-access-control.html) | AWS | T2 | tags-based access |
| S18 | [AWS IAM Access Analyzer](https://aws.amazon.com/iam/access-analyzer/) | AWS | T2 | least privilege analysis and review |
| S19 | [AWS IAM Identity Center Automatic Provisioning / SCIM](https://docs.aws.amazon.com/singlesignon/latest/userguide/provision-automatically.html) | AWS | T2 | SCIM provisioning and token expiry risk |
| S20 | [Google Cloud IAM Policy Types](https://docs.cloud.google.com/iam/docs/policy-types) | Google Cloud | T2 | allow/deny/principal access boundary |
| S21 | [Google Cloud Service Account Best Practices](https://docs.cloud.google.com/iam/docs/best-practices-service-accounts) | Google Cloud | T2 | service account and keyless guidance |
| S22 | [Microsoft Entra Access Reviews](https://learn.microsoft.com/en-us/entra/id-governance/access-reviews-overview) | Microsoft | T2 | recurring reviews and privileged/data access |
| S23 | [Microsoft Entra Entitlement Management](https://learn.microsoft.com/en-us/entra/id-governance/entitlement-management-overview) | Microsoft | T2 | request, assignment, expiration, review |
| S24 | [Microsoft Entra Privileged Identity Management](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/) | Microsoft | T2 | PIM / standing admin reduction |
| S25 | [Microsoft Entra Lifecycle Workflows](https://learn.microsoft.com/en-us/entra/id-governance/what-are-lifecycle-workflows) | Microsoft | T2 | JML automation |
| S26 | [Okta Access Certifications](https://help.okta.com/oie/en-us/content/topics/identity-governance/access-certification/iga-access-cert.htm) | Okta | T2 | review campaign / remediation |
| S27 | [Okta Identity Governance](https://help.okta.com/oie/ja-jp/content/topics/identity-governance/iga.htm) | Okta | T2 | lifecycle and governance |
| S28 | [Okta App Sign-on Policies](https://help.okta.com/en-us/content/topics/security/policies/about-app-signon-policies.htm) | Okta | T2 | app policy, device/location/risk, legacy protocol note |
| S29 | [CyberArk Just-in-Time Access and Elevation](https://docs.cyberark.com/epm/latest/en/content/policies/jitelevationadmin-newui.htm) | CyberArk | T2 | JIT elevation |
| S30 | [CyberArk Privileged Access Manager](https://www.cyberark.com/products/privileged-access-manager/) | CyberArk | T2 | zero standing privileges |
| S31 | [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) | OWASP | T3/T5 | deny by default / every-request authorization |
| S32 | [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) | OWASP | T3/T5 | session controls |
| S33 | [OWASP Multifactor Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html) | OWASP | T3/T5 | MFA patterns |
| S34 | [OWASP API Security: Broken Object Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/) | OWASP | T3/T5 | BOLA / object-level authorization |
| S35 | [GitHub Managing Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) | GitHub | T2 | fine-grained PAT / expiry |
| S36 | [GitHub SCIM for Organizations](https://docs.github.com/en/enterprise-cloud@latest/organizations/managing-saml-single-sign-on-for-your-organization/about-scim-for-organizations) | GitHub | T2 | SCIM provisioning and deprovisioning |
| S37 | [GitHub Enterprise Audit Log](https://docs.github.com/en/enterprise-cloud@latest/admin/concepts/security-and-compliance/audit-log-for-an-enterprise) | GitHub | T2 | audit logs |
| S38 | [Kubernetes RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/) | Kubernetes | T2/T3 | API resource authorization |
| S39 | [Microsoft: Analysis of Storm-0558 Techniques](https://www.microsoft.com/en-us/security/blog/2023/07/14/analysis-of-storm-0558-techniques-for-unauthorized-email-access/) | Microsoft | T5 | forged token / signing key incident |
| S40 | [Okta: HAR Files / Support System Incident Follow-up](https://sec.okta.com/articles/harfiles/) | Okta | T5 | support-system compromise and mitigations |
| S41 | [Cloudflare Thanksgiving 2023 Security Incident](https://blog.cloudflare.com/thanksgiving-2023-security-incident/) | Cloudflare | T5 | stale service tokens / service accounts |
| S42 | [Microsoft MSRC Storm-0558 Key Acquisition Investigation](https://www.microsoft.com/en-us/msrc/blog/2023/09/results-of-major-technical-investigations-for-storm-0558-key-acquisition) | Microsoft | T5 | signing key material failure |
| S43 | [NIST SP 800-53 Rev. 5 Security and Privacy Controls](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final) | NIST | T0 | access control, identification/authentication, audit control families |

---

## 19. QA Result

| Check | Result |
|---|---|
| Coverage | T0 standards, T2 platform docs, T3/T5 operational and failure evidence are all present. |
| Critical claims | Core claims C-001 to C-018 are A/B confidence and tied to source IDs. |
| Recency | Current canonical sources were used where available; incident sources are treated as failure evidence, not current product state. |
| Exceptions | Break-glass, legacy protocols, guests/vendors, syncable authenticators, non-human credentials, SCIM outage are included. |
| Failure | Storm-0558, Okta support-system incident, Cloudflare 2023 incident, BOLA, token replay, SCIM failure are included. |
| Provenance | All major claims reference source IDs in the Source Catalog. |
| Output integrity | Definition, Frontier Exemplars, Evidence Map, Core Philosophy, Decision Model, Operating Model, Technical Spec, Metrics, Failure Modes, Anti-patterns, Maturity Model, Implementation Guide, Confidence & Unknowns are populated. |
