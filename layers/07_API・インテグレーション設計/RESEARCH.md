# Frontier Operating Model Research: API・インテグレーション設計（07）

作成日: 2026-05-13  
対象: 07 API・インテグレーション設計  
出力形式: RESEARCH.md準拠の Clone Spec + Evidence Map + Layer Registry + Pattern Library  
調査制約: 公開情報のみ。標準仕様、公式設計ガイド、公式 API ドキュメント、OSS/コミュニティ標準、IETF/W3C/CNCF 等の一次情報を優先した。

---

## 0. 調査方針

本調査は、ユーザー添付の `RESEARCH.md` が定義する Frontier Operating Model Research の手順に従い、各レイヤーを「意思決定システム」として再構成する。すなわち、各レイヤーについて、何を入力に、何を決め、どの基準・制約・閾値・例外で運用し、誰が責任を持ち、何を成果物として残し、何を指標に正しさを判定するかを明確化する。

今回の 07 クラスタでは、公開 API とインテグレーションを単なる技術部品ではなく、外部・内部利用者に対する **contract surface** として扱う。主な証拠面は、OpenAPI、Google Cloud API Design Guide、Azure REST API Guidelines、JSON Schema、IETF HTTP/OAuth/WebSocket/RFC 群、GraphQL、gRPC、AsyncAPI、CloudEvents、GitHub/Stripe の公式運用ドキュメント、Gateway/Observability/Contract Testing の公式ドキュメントである。

信頼度は次のように扱う。

| Confidence | 定義 | 本成果物での扱い |
|---|---|---|
| A | T0/T1/T2 の direct evidence に裏付けられた主張 | Clone Spec の中核に採用 |
| B | 独立した 2 系統以上の公開証拠で一致する主張 | Clone Spec の中核に採用 |
| C | 合理的推定だが direct proof が不足 | Unknowns または補助仮説へ隔離 |
| D | 仮説 | 実装判断に使わない |
| X | 破棄対象 | 採用しない |

---

## 1. Executive Summary

07 の API・インテグレーション設計クラスタにおける frontier pattern は、**API をコード実装の副産物ではなく、機械可読な contract、運用可能な制御面、変更可能だが壊れにくい product surface として管理すること**である。

先端組織・標準・OSS の共通パターンは次の 5 点に集約される。

1. **Contract-first / schema-first**。HTTP API は OpenAPI、JSON payload は JSON Schema、RPC は Protocol Buffers/gRPC、GraphQL は schema、event API は AsyncAPI/CloudEvents で機械可読に表現する。人間向けドキュメントは contract から派生させ、docs drift を抑える。[[S02]][[S03]][[S06]][[S17]][[S19]][[S25]][[S26]]
2. **Evolvability-first**。API は最初から pagination、filtering、versioning、stability level、deprecation/sunset、schema compatibility を設計する。後から pagination や安定性区分を足す設計は互換性リスクが高い。[[S28]][[S30]][[S31]][[S32]][[S33]]
3. **Security-by-contract**。OAuth/OIDC/JWT、scope、resource-level authorization、webhook signature、property-level authorization、入力検証を API contract の一部として扱う。認証だけでなく、対象リソースに対する権限を明示する。[[S10]][[S11]][[S12]][[S13]][[S22]][[S39]]
4. **Operational behavior is part of API design**。rate limit、429、Retry-After、idempotency、pagination cursor、error object、trace context、webhook delivery SLA は、内部運用ではなく利用者に見える API 仕様である。[[S08]][[S09]][[S14]][[S15]][[S23]][[S34]]
5. **Protocol choice is a product decision**。REST/HTTP、GraphQL、gRPC、WebSocket、Webhook、event-driven API は相互代替ではなく、利用者、呼び出し頻度、同期/非同期、スキーマ進化、双方向性、運用制御、SDK/tooling の条件で選ぶ。[[S07]][[S17]][[S18]][[S19]][[S20]][[S21]][[S26]]

このクラスタで最も再現性の高い operating model は、API Design Authority または API Platform Team が横断標準を定義し、各 service owner が API contract を所有し、Security/SRE/Docs/SDK/Partner Success が review gate を持つ構造である。API review は、設計時、breaking change 予定時、major version 追加時、public exposure 変更時、auth/rate/error/event behavior 変更時に必須化する。

---

## 2. Layer Registry: 07

| Layer ID | Layer Name | Definition | Decision Object | Primary Artifacts | Owner Roles | Default Metrics |
|---|---|---|---|---|---|---|
| 07.01 | API公開戦略 | どの API を誰に、どの公開範囲・契約・商用条件で提供するかを決める | Public / partner / internal API exposure model | API catalog, access policy, developer portal, partner terms | API product owner, legal, security, partner success | active integrations, approval lead time, partner activation, abuse events |
| 07.02 | API設計原則 | API の resource/action、transport、schema、auth、error、limit、versioning の横断規範を決める | API design standard | API style guide, review checklist, lint rules | API design authority, platform architect | design review pass rate, spec lint errors, breaking changes |
| 07.03 | リソースモデル・ドメイン境界 | API が表現する resource、collection、relationship、operation 境界を決める | Resource/domain contract | resource model, URI map, ownership matrix | domain architect, service owner | resource consistency, duplicate resources, consumer confusion |
| 07.04 | APIスキーマ・型システム | payload、field、enum、nullable、schema evolution、validation schema を決める | Schema contract | OpenAPI Schema, JSON Schema, proto, GraphQL SDL | API owner, schema steward | incompatible schema changes, validation failures, generated SDK defects |
| 07.05 | APIバージョニング・安定性 | API の stability level、version strategy、deprecation、sunset を決める | Stability and lifecycle contract | version policy, migration guide, Deprecation/Sunset headers | API governance, service owner | deprecated endpoint usage, migration completion, unplanned breaking changes |
| 07.06 | APIドキュメント・Developer Portal | 利用者が API を発見・試行・統合・運用できる情報設計を決める | Developer experience contract | docs, quickstart, examples, changelog, status, SDK docs | docs owner, developer relations, SDK owner | time-to-first-call, doc search success, support tickets |
| 07.07 | 認証 | API 利用者・クライアント・service identity をどう確認するかを決める | Authentication model | OAuth/OIDC config, API key policy, mTLS/HMAC policy | IAM/security architect | auth failure rate, credential leakage incidents, token misuse |
| 07.08 | 認可・スコープ | 誰がどの resource/action/field を実行できるかを決める | Authorization matrix | scope model, RBAC/ABAC matrix, resource checks | security, service owner | authorization defects, overprivileged scopes, denied-but-valid attempts |
| 07.09 | レート制限・クォータ | 誰にどの単位でどの上限・burst・retry guidance を与えるかを決める | Quota and throttling policy | rate-limit policy, headers, 429 behavior, quota dashboard | SRE, API platform, product owner | 429 rate, abuse blocked, false throttling, quota escalations |
| 07.10 | 入力検証・契約検証 | API request を schema/semantic/security の各面でどう検証するかを決める | Validation contract | validation schema, sanitizer rules, contract tests | service owner, security, QA | rejected invalid requests, injection attempts, false rejects |
| 07.11 | エラー設計 | 失敗をどの status/error object/correlation/原因分類で返すかを決める | Error contract | error catalog, Problem Details schema, status code matrix | API platform, SRE, support | diagnosable errors, support escalation, opaque error ratio |
| 07.12 | 冪等性・リトライ | write/retry/duplicate request を安全化する方法を決める | Retry safety contract | idempotency key policy, retry policy, dedupe storage | service owner, SRE | duplicate side effects, retry success, idempotency mismatch |
| 07.13 | ページネーション | collection API の結果分割・cursor・limit・continuation を決める | Pagination contract | cursor/token model, page size limits, Link headers | API design authority, service owner | large response errors, page latency, cursor errors |
| 07.14 | 検索・フィルタリング・ソート | 利用者が collection を絞り込む grammar、index、cost control を決める | Query contract | filter syntax, sort policy, index policy | API owner, search/data platform | query latency, expensive query rejection, result relevance |
| 07.15 | REST/HTTPリソースAPI | HTTP method、URI、status、headers、cache、conditional update を決める | REST/HTTP contract | URI map, method semantics, HTTP headers | API architect, service owner | method misuse, cache hit, conditional update conflicts |
| 07.16 | GraphQL API | schema、resolver、operation cost、field auth、persisted query を決める | GraphQL contract | SDL, schema registry, operation policy | GraphQL platform owner | query cost, resolver latency, field auth violations |
| 07.17 | gRPC/Protocol Buffers | service/method/message、streaming、deadlines、transcoding を決める | RPC/proto contract | proto files, service config, generated clients | platform architect, service owner | deadline misses, proto compatibility violations, client generation defects |
| 07.18 | WebSocket/リアルタイム双方向 | connection、subscription、message schema、heartbeat、backpressure を決める | Realtime session contract | WebSocket protocol spec, subscription model | realtime platform, SRE | reconnect rate, stale sessions, dropped messages, fanout latency |
| 07.19 | Webhook/イベント通知 | event type、delivery、signature、retry、ordering、redelivery を決める | Event delivery contract | webhook spec, event catalog, signing policy | integration platform, security | delivery success, signature failures, replay attempts, redelivery lag |
| 07.20 | HTTP semantics・headers・status | API が HTTP の共通意味論・ヘッダー・status をどう使うかを決める | HTTP behavior contract | status matrix, header registry, cache/trace policy | API platform, SRE | invalid status use, header coverage, cache/trace propagation |
| 07.21 | API Security | API 固有の脅威、認可欠陥、データ露出、abuse を制御する | API threat model | API threat model, Top 10 mapping, abuse controls | security architect, AppSec | API vulnerabilities, BOLA/BOPLA defects, WAF/gateway blocks |
| 07.22 | API Gateway/Edge Integration | 外部入口での routing、auth、rate、translation、policy enforcement を決める | Edge control plane | gateway config, route policy, certs, WAF/rate controls | platform/SRE/security | route incidents, policy drift, gateway latency |
| 07.23 | SDK/client integration | API 利用を SDK/CLI/client library でどう安定提供するかを決める | Client integration contract | SDKs, generated clients, retry defaults, examples | SDK owner, DevRel | SDK adoption, client errors, version skew |
| 07.24 | Contract testing/compatibility | consumer/provider の互換性をどう検証し、破壊的変更を検出するかを決める | Compatibility gate | Pact tests, schema diff, provider verification | QA, service owner, platform | compatibility failures caught pre-prod, escaped breakages |
| 07.25 | Change management/deprecation | API 変更・移行・廃止をどう通知し、実行し、測定するかを決める | Change lifecycle contract | changelog, migration guide, Deprecation/Sunset headers | API governance, support, product | migration completion, deprecated calls, customer escalations |
| 07.26 | Observability/audit/trace | API 呼び出しをどう計測・追跡・監査するかを決める | API telemetry contract | trace headers, logs, metrics, audit schema | SRE, security, data governance | trace coverage, audit completeness, MTTR |
| 07.27 | SLO/SLA/availability/backpressure | API の可用性・性能・劣化時動作をどう約束するかを決める | Reliability contract | SLO/SLA, timeout, backpressure, degradation policy | SRE, product, support | latency SLO, error budget, timeout, queue depth |
| 07.28 | Multitenancy/tenant isolation | tenant ごとの認可、quota、データ分離、abuse isolation を決める | Tenant isolation contract | tenant model, quota partitions, isolation tests | security, platform, data owner | cross-tenant incidents, noisy-neighbor events |
| 07.29 | API governance/review/lint | API 標準が新規・変更 API に適用される review gate を決める | Governance control | review board, lint CI, exception register | API governance board | waiver count, review lead time, lint pass rate |
| 07.30 | Partner/onboarding/integration operations | パートナー統合の申請、sandbox、keys、support、certification を決める | Partner integration model | onboarding checklist, sandbox, runbooks | partner success, support, API product | onboarding time, integration defects, support load |

---

## 3. Frontier Exemplars and Candidate Scoring

スコアは RESEARCH.md の既定軸に合わせ、Performance / Adoption / Artifact Richness / Peer Validation / Recency / Transferability / Failure Evidence を 100 点換算した。評価対象は「有名度」ではなく、公開証拠密度と再現可能性である。

| Candidate | Score | Primary Scope | Why Frontier | Evidence Tier |
|---|---:|---|---|---|
| IETF HTTP / OAuth / WebSocket / Problem Details / Deprecation RFCs | 94 | HTTP semantics, auth, error, lifecycle, realtime | protocol-level semantics と header/status/error/lifecycle の規範を提供する | T0 |
| OpenAPI Initiative / OAS | 92 | HTTP API contract | HTTP API を programming-language agnostic に記述し、docs/codegen/test/tooling の基盤になる | T0/T2 |
| Google Cloud API Design Guide + AIPs | 91 | REST/RPC/gRPC, pagination, filtering, versioning | Google 内外で使える network API design guide と AIP による詳細規範を提供する | T0/T3 |
| Azure REST API Guidelines | 89 | Cloud data-plane REST APIs | data plane API に対して MUST レベルの prescriptive guidance、versionable contract、retry/idempotency を明示する | T0/T3 |
| GitHub REST/GraphQL/Webhook Docs | 87 | operational public API | pagination/rate limit/GraphQL/webhook の実運用仕様が公開されている | T2/T3 |
| Stripe API Docs | 85 | idempotency, webhook, payment-grade API | idempotency key、webhook signature、event processing の実務仕様が明確 | T2/T3 |
| GraphQL Specification / GraphQL over HTTP | 84 | query API, schema, exact data fetch | schema-driven query API と HTTP interoperability の標準面を提供する | T0 |
| gRPC / Protocol Buffers | 83 | RPC and service-to-service API | high-performance RPC、IDL、codegen、deadlines/metadata/streaming の基盤 | T0/T2 |
| AsyncAPI + CloudEvents | 82 | event/message-driven APIs | message-driven API と event envelope の標準化により Webhook/Kafka/MQTT 等をまたぐ | T0 |
| Envoy Gateway / Kubernetes Gateway API | 79 | edge/gateway/API policy | API Gateway を routing/security/rate/protocol translation の control plane として扱える | T2/T3 |
| OpenTelemetry + W3C Trace Context | 78 | observability | API 呼び出しの tracing/metrics/logs と HTTP header propagation を標準化する | T0/T3 |
| Pact | 75 | contract testing | consumer-driven contract testing を concrete request/response で実行し、provider changes の互換性を検証する | T3/T5 |
| OWASP API Security Top 10 | 74 | security failure taxonomy | API 固有の脅威分類と failure pattern を提供する | T5 |

---

## 4. Evidence Map

| Claim ID | Claim | Evidence | Directness | Confidence | Applies to Layers |
|---|---|---|---|---|---|
| C01 | API は実装後の説明ではなく、機械可読 contract として先に定義すべき | OAS defines a programming-language-agnostic interface description for HTTP APIs; OpenAPI Initiative presents API descriptions as reusable basis for docs/codegen/tests | Direct | A | 07.02, 07.04, 07.06, 07.10, 07.23, 07.24 |
| C02 | HTTP API には共通の stateless semantics、URI、headers、status の規範が必要 | RFC 9110 defines HTTP architecture, common terminology, shared protocol aspects | Direct | A | 07.15, 07.20 |
| C03 | REST/RPC/gRPC は別々の設計思想を持つが、API design guide で一貫性を持たせられる | Google Cloud API Design Guide covers networked APIs, REST and RPC, with focus on gRPC/Protocol Buffers/HTTP transcoding | Direct | A | 07.02, 07.15, 07.17 |
| C04 | Azure data-plane API では consistency、developer friendliness、retries/idempotency、versionable contracts が設計目標として明示される | Azure REST API Guidelines goals include consistent HTTP/REST/JSON APIs, SDK, retries/idempotency/optimistic concurrency, sustainable versionable contracts | Direct | A | 07.02, 07.05, 07.12 |
| C05 | JSON Schema は JSON payload の validation と schema 管理の基盤になる | JSON Schema Draft 2020-12 is published as a comprehensive update for creating and validating JSON schemas | Direct | A | 07.04, 07.10 |
| C06 | HTTP API の error object は machine-readable な Problem Details に標準化できる | RFC 9457 defines Problem Details for HTTP APIs and obsoletes RFC 7807 | Direct | A | 07.11, 07.20 |
| C07 | rate limit は 429 と Retry-After 等の client-visible guidance を含めて設計すべき | RFC 6585 defines 429 Too Many Requests and notes Retry-After may be included | Direct | A | 07.09, 07.20, 07.27 |
| C08 | write retry は idempotency key で duplicate side effect を防ぐべき | Stripe official docs describe idempotency keys for safely retrying create/update requests | Direct | A | 07.12 |
| C09 | pagination は collection API の初期設計時に入れるべき | Google AIP-158 says adding pagination later is backward-incompatible in its model | Direct | A | 07.13 |
| C10 | GraphQL は schema と operation cost control を前提に設計する必要がある | GraphQL spec governs language; GitHub GraphQL rate limits assign points to queries to prevent abuse | Near-direct | B | 07.16, 07.09, 07.21 |
| C11 | gRPC は high-performance RPC として load balancing/tracing/health/auth を含む ecosystem を持つ | gRPC official site describes high-performance RPC framework with support for load balancing, tracing, health checking, auth | Direct | A | 07.17, 07.26 |
| C12 | WebSocket は two-way communication を提供するが、origin-based security、handshake、message framing が前提 | RFC 6455 defines WebSocket opening handshake and framing over TCP | Direct | A | 07.18, 07.20, 07.21 |
| C13 | Webhook は fast 2xx acknowledgement、signature validation、asynchronous processing を前提に設計するべき | GitHub requires 2xx within 10 seconds; signature is sent in X-Hub-Signature-256 | Direct | A | 07.19, 07.21, 07.27 |
| C14 | OAuth security は RFC 6749 のまま止めず、Best Current Practice を反映すべき | RFC 9700 updates and extends OAuth 2.0 threat model and deprecates less secure modes | Direct | A | 07.07, 07.08, 07.21 |
| C15 | API lifecycle は runtime header と documentation の両方で deprecation/sunset を伝えるべき | RFC 9745 Deprecation header, RFC 8594 Sunset header | Direct | A | 07.05, 07.25 |
| C16 | API Gateway は auth、rate limiting、routing、protocol translation を service 横断の control plane にする | Envoy Gateway defines API gateway as centralized entry point handling authentication, rate limiting, protocol translation | Direct | A | 07.22, 07.09, 07.21 |
| C17 | API observability は distributed tracing context を HTTP header で伝搬させる | W3C Trace Context defines standard HTTP headers for distributed tracing | Direct | A | 07.26 |
| C18 | consumer-driven contract testing は consumer が実際に使う request/response を例として検証する | Pact docs describe code-first consumer-driven contracts generated by automated consumer tests | Direct | A | 07.24 |
| C19 | event/message-driven API は AsyncAPI/CloudEvents で protocol-neutral に表現できる | AsyncAPI is protocol agnostic for message-driven APIs; CloudEvents defines common event metadata | Direct | A | 07.19, 07.18, 07.04 |
| C20 | API security failure は authentication だけでなく object/property authorization、excessive data exposure、unsafe consumption を含む | OWASP API Security Top 10 provides API risk taxonomy | Near-direct | B | 07.08, 07.10, 07.21, 07.28 |

---

## 5. Core Philosophy

### 5.1 Contract before implementation

優れた API 組織は、endpoint を実装してからドキュメントを後追いで書かない。API の公開単位、resource、schema、error、pagination、auth、rate limit、idempotency、deprecation、telemetry を contract として設計し、OpenAPI/proto/GraphQL SDL/AsyncAPI/CloudEvents のような機械可読成果物に落とす。これにより、SDK generation、docs generation、contract tests、schema diff、mock server、client validation、security review を同じ contract に接続できる。[[S02]][[S03]][[S06]][[S17]][[S19]][[S26]]

### 5.2 Protocol is a decision, not a fashion

REST/HTTP は resource と stateless interaction に強い。GraphQL は consumer-specific data selection と aggregate query に強いが、query cost、field authorization、resolver observability が必要になる。gRPC は service-to-service RPC、typed IDL、streaming、low-latency/efficient codegen に強い。WebSocket は persistent bidirectional session を必要とするリアルタイム用途に向く。Webhook と CloudEvents/AsyncAPI は非同期 event delivery に向く。frontier design は protocol を流行で選ばず、traffic pattern、coupling、tooling、security、observability、failure semantics で選ぶ。[[S07]][[S17]][[S18]][[S19]][[S20]][[S21]][[S25]][[S26]]

### 5.3 Compatibility is a product obligation

API は一度公開すると、利用者の code、business process、monitoring、support runbook に組み込まれる。したがって、schema field、enum、pagination、error code、rate limit、auth scope、webhook event type、SDK default の変更は product change として扱う。deprecation と sunset は runtime signal と docs/changelog/migration guide で伝える。[[S30]][[S31]][[S32]][[S33]]

### 5.4 Failure behavior is part of the API

優れた API は成功時レスポンスだけでなく、429、5xx、retry、timeout、duplicate delivery、partial failure、idempotency mismatch、webhook redelivery、GraphQL cost rejection、gRPC deadline exceeded を定義する。エラー・リトライ・limit・trace は「内部運用」ではなく、利用者が統合を安定させるための API 仕様である。[[S08]][[S09]][[S15]][[S16]][[S23]][[S34]]

### 5.5 Security is resource-specific and event-specific

API security は token が valid かどうかだけでは足りない。resource owner、tenant、scope、object-level authorization、property-level authorization、field masking、input validation、signature validation、replay protection、rate abuse、auditability が必要である。Webhook では payload の HMAC signature、timestamp/replay protection、secret rotation、fast acknowledgement、async queue が必須になる。[[S11]][[S22]][[S24]][[S39]]

---

## 6. Decision Model

### 6.1 Inputs

| Input Category | Examples | Used By Layers |
|---|---|---|
| Consumer archetype | external developer, partner, internal service, mobile client, browser, batch integration | 07.01, 07.06, 07.23, 07.30 |
| Domain model | resources, relationships, actions, events, ownership boundaries | 07.03, 07.15, 07.16, 07.17, 07.19 |
| Data sensitivity | PII, financial data, tenant data, regulated data, secrets | 07.07, 07.08, 07.10, 07.21, 07.28 |
| Traffic profile | QPS, burst, long polling, streaming, fanout, batch, webhook volume | 07.09, 07.18, 07.19, 07.22, 07.27 |
| Failure profile | retry needs, duplicate risk, timeout, partial success, idempotency needs | 07.11, 07.12, 07.27 |
| Tooling ecosystem | OpenAPI, proto, GraphQL, AsyncAPI, SDK generators, gateway, lint, CI | 07.04, 07.17, 07.23, 07.24, 07.29 |
| Lifecycle constraints | stability level, public commitment, deprecation window, migration path | 07.05, 07.25 |
| Security model | OAuth/OIDC, service identity, mTLS, API keys, HMAC, RBAC/ABAC | 07.07, 07.08, 07.21, 07.28 |
| Observability needs | trace propagation, logs, audit, metrics, SLOs | 07.11, 07.26, 07.27 |
| Commercial/partner model | pricing, quota tier, support tier, certification, onboarding | 07.01, 07.09, 07.30 |

### 6.2 Criteria

1. **Discoverability**: API catalog、docs、examples、schema、changelog により、利用者が自力で統合できる。
2. **Least surprise**: naming、HTTP method、status、error、pagination、date/time、IDs、auth scopes が一貫している。
3. **Backward compatibility**: schema evolution、versioning、deprecation、contract tests により、利用者を予告なく壊さない。
4. **Security and privacy**: authn/authz、tenant isolation、least privilege、input validation、signature/replay protection を保証する。
5. **Operational robustness**: rate limit、retry、idempotency、trace、SLO、backpressure、gateway controls を定義する。
6. **Protocol fitness**: REST/GraphQL/gRPC/WebSocket/Webhook を用途に応じて選ぶ。
7. **Automation potential**: spec lint、codegen、docs generation、contract testing、schema diff、mocking、gateway config へ接続できる。
8. **Supportability**: error object、correlation ID、logs、audit、docs、support runbook が揃っている。

### 6.3 Priorities

1. Public / partner API では **security + compatibility** を throughput より優先する。
2. New collection API では **pagination/filtering/sorting** を最初から入れる。
3. Write API では **idempotency / retry semantics** を成功レスポンスと同じレベルで設計する。
4. Event delivery では **signature / dedupe / ordering caveat / replay protection** を先に決める。
5. GraphQL では **query cost/depth/node limit + field authorization** を schema design と同時に決める。
6. gRPC では **deadline / status / metadata / compatibility of proto fields** を最初に標準化する。
7. Gateway では **central policy + service ownership** の境界を明確にし、service-specific business auth を gateway に押し込みすぎない。

### 6.4 Prohibitions

- OpenAPI/proto/GraphQL/AsyncAPI 等の canonical contract なしに public API を公開する。
- 200 OK の body 内で business error を返し、HTTP status と error taxonomy を曖昧にする。
- `limit` の上限なし、cursor なし、sort/filter grammar なしで collection API を公開する。
- POST だけで全操作を表現し、resource/action semantics を隠す。
- OAuth token の有効性だけで authorization を済ませ、resource-level/object-level check を省く。
- Webhook を unsigned payload として送信する。
- retry 可能な write API に idempotency key や dedupe strategy を定義しない。
- GraphQL で query cost/depth/node count、resolver timeout、field authorization を設定しない。
- proto field number を再利用する、enum evolution を考慮しない、unknown field を破壊的に扱う。
- deprecation を docs だけで通知し、runtime signal、usage telemetry、migration support を持たない。

### 6.5 Decision thresholds

| Threshold | Recommended Default | Rationale |
|---|---|---|
| Public API contract | OpenAPI/proto/GraphQL SDL/AsyncAPI のいずれか必須 | docs/codegen/test/gateway/security automation に接続するため |
| Collection response size | default + max page size を必須化 | unbounded response と latency blow-up を防ぐ |
| Rate limit response | 429 + optional Retry-After + docs/dashboard | client が backoff 可能にする |
| Webhook acknowledgement | 2xx を短時間で返し、処理は async queue に逃がす | sender timeout と duplicate delivery を抑える |
| Webhook validation | signature + timestamp/replay check | spoofing/replay を防ぐ |
| Idempotency key | create/update の retry-prone operation で必須または推奨 | duplicate side effects を防ぐ |
| Breaking change | API governance approval + migration guide + deprecation window | consumer disruption を抑える |
| GraphQL operation | depth/cost/node/time limits | abuse と unbounded resolver chain を防ぐ |
| Trace propagation | W3C Trace Context or equivalent | distributed debugging と audit を可能にする |

### 6.6 Owners and reviewers

| Role | Responsibility |
|---|---|
| API Product Owner | 公開戦略、consumer needs、pricing/quota/support tier、changelog owner |
| Service Owner | endpoint/schema/business semantics、runtime behavior、SLO、backward compatibility |
| API Design Authority | cross-API style guide、review gate、exception register、standard patterns |
| Security/AppSec | authn/authz、scope、input validation、tenant isolation、threat model、webhook signing |
| SRE/API Platform | gateway、rate limit、observability、trace、SLO、backpressure、incident response |
| Docs/DevRel | developer portal、examples、SDK docs、migration guide、support content |
| SDK Owner | generated/manual SDK、client retry behavior、version skew、language-specific ergonomics |
| Legal/Privacy | terms of use、data processing、PII、regional/regulatory constraints |
| Partner Success/Support | onboarding、sandbox、certification、escalation、integration health |

---

## 7. Operating Model

### 7.1 Process

| Stage | Gate | Required Evidence | Output |
|---|---|---|---|
| API proposal | Exposure decision | Consumer archetype, business purpose, data sensitivity, protocol choice | API proposal record |
| Design review | Contract completeness | OpenAPI/proto/GraphQL/AsyncAPI draft, resource model, auth, error, pagination, rate, idempotency | approved API contract |
| Security review | Threat and authorization | authn/authz matrix, tenant model, input validation, abuse/rate plan | security signoff |
| Implementation | Contract conformance | generated stubs/SDK, gateway config, tests, schema validation | implementation artifacts |
| Pre-release | Compatibility and docs | contract tests, schema diff, docs, quickstart, SDK, changelog | release-ready API |
| Launch | Operational readiness | SLO, dashboard, alerts, rate limit, support runbook, status comms | production API |
| Change/deprecation | Lifecycle control | usage telemetry, migration guide, Deprecation/Sunset headers, support plan | migration program |
| Retirement | Safe shutdown | remaining usage, exception approvals, final comms, fallback | retired API record |

### 7.2 Review triggers

API review is mandatory when any of the following changes occurs.

- New public/partner API or new major API family.
- New resource, collection, action, event type, or GraphQL schema segment.
- Change to authentication, authorization, scope, tenant isolation, or sensitive data exposure.
- Change to error object, status code semantics, pagination token, filter grammar, idempotency semantics, rate limit behavior.
- Change to SDK public API or generated client behavior.
- Deprecation, sunset, migration, major version addition, removal of endpoint/event/schema field.
- Gateway route/policy change affecting external traffic.
- Webhook event delivery, signing, retry, ordering, redelivery behavior change.

### 7.3 Artifacts

| Artifact | Required For | Owner | Verification |
|---|---|---|---|
| API catalog entry | all public/partner/internal platform APIs | API product owner | registry check |
| OpenAPI/proto/GraphQL/AsyncAPI contract | all APIs | service owner | spec lint + schema diff |
| Resource model / domain map | REST/GraphQL/gRPC APIs | domain architect | design review |
| Authz matrix | sensitive APIs | security | test + review |
| Error catalog | all APIs | API platform | error contract tests |
| Rate limit/quota policy | public/partner/high-volume APIs | SRE/API platform | gateway config + docs |
| Idempotency policy | write APIs | service owner | dedupe tests |
| Pagination/filter/search policy | collection APIs | service owner | contract tests |
| Webhook event catalog | event APIs | integration platform | signature/delivery tests |
| SDK docs/examples | public/partner APIs | SDK/DevRel | smoke tests |
| SLO/dashboard/runbook | production APIs | SRE | observability review |
| Changelog/migration guide | public changes | API product owner | release checklist |

### 7.4 Meeting and cadence model

| Cadence | Forum | Purpose |
|---|---|---|
| Weekly | API Design Review | New API designs, exceptions, style guide interpretation |
| Weekly/biweekly | Security/API Threat Review | authz model, tenant isolation, webhook signing, abuse cases |
| Release-based | API Change Review | breaking/non-breaking classification, migration plan, docs/SKD readiness |
| Monthly | API Portfolio Review | usage, deprecated usage, support load, top errors, partner health |
| Quarterly | API Standards Review | style guide updates, lint rule changes, protocol/gateway/tooling decisions |
| Incident-based | API Postmortem | outage, authz defect, schema break, rate-limit abuse, webhook delivery failure |

---

## 8. Technical / Business Specification by Subtheme

### 8.1 API公開

API publication is a product and risk decision. An API should be classified as one of: internal platform API, first-party product API, partner API, public developer API, or regulated/sensitive API. The classification determines docs visibility, auth model, approval workflow, quota, SLA, support, legal terms, SDK availability, sandbox, and change policy.

Minimum clone spec:

- Maintain an API catalog with owner, visibility, consumer type, auth, data sensitivity, SLO, current version, docs URL, schema URL, gateway route, and deprecation status.
- Public and partner APIs require developer portal, quickstart, examples, status/changelog, contact/support route, rate/quota docs, error docs, and SDK policy.
- Sensitive APIs require security review, authorization matrix, audit logging, abuse controls, and privacy/legal review.
- API keys or tokens must be provisioned through controlled onboarding; sandbox credentials must not grant production data access.
- Publish clear version and deprecation commitments before first external launch.

Key failure modes: undocumented public endpoint, stale partner docs, manual key issuance without audit, sandbox not matching production behavior, public endpoint without owner.

### 8.2 API設計

API design standard must define resource naming, operation naming, HTTP methods, request/response format, date/time/ID conventions, pagination, errors, idempotency, authentication, authorization, rate limit, tracing, versioning, and deprecation. Google and Azure guidance show that mature API design uses common design principles across REST/RPC and includes retry/idempotency/versionable contract as design goals. [[S04]][[S05]]

Minimum clone spec:

- Create an API Style Guide with mandatory patterns and allowed exceptions.
- Require design review before implementation for external APIs.
- Enforce style guide with OpenAPI/proto/GraphQL/AsyncAPI lint rules.
- Maintain exception register with owner, reason, risk, expiry, and compensating controls.
- Prefer explicit resource contracts over implementation-driven endpoint naming.

### 8.3 APIスキーマ

Schema is the stable contract boundary. JSON APIs should use OpenAPI Schema/JSON Schema; RPC APIs should use Protocol Buffers; GraphQL APIs should use GraphQL SDL; event APIs should use AsyncAPI/CloudEvents where applicable. [[S02]][[S06]][[S17]][[S19]][[S25]][[S26]]

Minimum clone spec:

- Every public request/response/event payload has a schema.
- Fields have type, required/optional status, nullability, constraints, examples, sensitivity classification, and compatibility rules.
- Enum changes, field removals, required field additions, semantic changes, and default changes are classified for compatibility.
- Generated clients and validators must use the canonical schema, not hand-maintained duplicates.
- Schema diff runs in CI for all API changes.

Key failure modes: schema drift between docs and runtime, required field added without versioning, enum value not forward-compatible, unknown field rejected unexpectedly, sensitive field accidentally exposed.

### 8.4 APIバージョニング

Versioning is a lifecycle mechanism, not just a URI pattern. Mature API programs define stability levels, compatibility rules, deprecation, migration, and sunset. Google AIPs explicitly cover stability and versioning; HTTP Deprecation and Sunset headers provide runtime lifecycle signals. [[S30]][[S31]][[S32]][[S33]]

Minimum clone spec:

- Define stability states: experimental/alpha, beta, GA, deprecated, sunset, retired.
- Define which changes are non-breaking, potentially breaking, breaking, and security emergency.
- Require migration guide and usage telemetry before deprecation.
- Use changelog, docs, email/support notices, and when appropriate Deprecation/Sunset headers.
- Do not remove externally used API until agreed usage threshold or exception process is complete.

### 8.5 APIドキュメント

Documentation is part of the API surface. It should be generated or at least continuously validated from contract artifacts. OpenAPI-style contracts can support interactive docs, code generation, and test automation, reducing docs drift. [[S02]][[S03]]

Minimum clone spec:

- Docs include overview, auth, quickstart, reference, examples, SDK usage, errors, pagination, rate limits, idempotency, webhooks/events, changelog, migration guides, and support channel.
- Every endpoint/method/event has examples for success, client error, server error, rate limited, and auth failure.
- Docs include a “known limits” section: max page size, rate windows, webhook timeout, retry guidance, GraphQL cost limits, gRPC deadlines.
- Docs changes are part of release checklist; API launch cannot ship without docs.
- Search logs and support tickets are used to improve docs.

### 8.6 認証

Authentication confirms the caller/client identity. Mature API security uses OAuth 2.0/OIDC/JWT/service identity/mTLS/HMAC according to risk and client type. RFC 9700 updates OAuth 2.0 security practice and deprecates less secure modes. [[S10]][[S11]][[S12]][[S13]]

Minimum clone spec:

- Browser/user APIs use OAuth/OIDC where user delegation is required.
- Service-to-service APIs use workload identity, mTLS, signed tokens, or equivalent service identity.
- API keys alone are not sufficient for high-risk user/resource authorization; if used, they are scoped, rotated, monitored, and not placed in URLs.
- Token audience, issuer, expiry, scope, tenant, and replay constraints are validated.
- Credential issuance and rotation are auditable.

### 8.7 認可

Authorization determines whether an authenticated caller may perform a specific action on a specific resource/field. API security failures often occur at object/property level, not merely at login. [[S39]]

Minimum clone spec:

- Maintain authz matrix by resource, action, field, tenant, role/scope, and ownership relation.
- Check authorization server-side for every object access; do not infer from client-provided IDs.
- Separate scopes for read/write/admin/export/webhook-management.
- Sensitive fields require property-level authorization and masking.
- Test BOLA/BOPLA-like cases: same tenant wrong object, different tenant, overbroad scope, hidden field update, mass assignment.

### 8.8 レート制限

Rate limiting is a consumer-visible fairness and abuse-control mechanism. It should be implemented with stable status and headers, not only hidden gateway rules. RFC 6585 defines 429 Too Many Requests, and GitHub publishes detailed REST/GraphQL rate limit behavior and secondary constraints. [[S09]][[S15]][[S16]]

Minimum clone spec:

- Define rate dimensions: client, user, tenant, token, endpoint, resource, IP, region, and quota tier.
- Return 429 for policy throttling; include Retry-After or documented reset guidance where appropriate.
- Provide headers or dashboard for remaining quota/reset when feasible.
- Apply secondary limits for abuse patterns: concurrency, mutation rate, search cost, GraphQL query cost, webhook creation bursts.
- Maintain quota escalation workflow and business approval.

### 8.9 入力検証

Input validation combines schema validation, semantic validation, business authorization, and security sanitization. JSON Schema/OpenAPI/proto/GraphQL schemas are necessary but not sufficient; they must be combined with object authorization and business constraints. [[S06]][[S39]]

Minimum clone spec:

- Validate content type, schema, required fields, type constraints, string lengths, enum values, numeric ranges, date/time format, IDs, and nested object limits.
- Validate business semantics: resource exists, caller owns/can access it, state transition is allowed, idempotency parameters match, field update is permitted.
- Reject unknown or unexpected fields where mass assignment risk exists, or explicitly ignore with documented behavior.
- Use centralized validators generated from canonical schema when possible.
- Log rejected classes without leaking secrets or sensitive payloads.

### 8.10 エラー

Errors must be stable, diagnosable, and machine-readable. RFC 9457 Problem Details gives a standard model for HTTP API error details. [[S08]]

Minimum clone spec:

- Use HTTP status for transport/protocol class and stable error code for application class.
- Error body includes type/code, title/message, detail if safe, instance/request ID, correlation/trace ID, retryability, docs link, and field-level validation errors where applicable.
- Do not leak secrets, PII, internal SQL/stack traces, auth tokens, or cross-tenant existence hints.
- Define retry guidance by error class: retry, do not retry, retry after, contact support, idempotency mismatch.
- Support team can map error code to runbook and ownership.

### 8.11 冪等性

Idempotency protects clients and systems from duplicate side effects when create/update requests are retried after network or server failures. Stripe’s published idempotency model shows a concrete pattern: a client-supplied idempotency key is associated with the first result and later reused to return consistent results for that key. [[S23]]

Minimum clone spec:

- Safe/idempotent operations are documented; unsafe write operations define retry behavior.
- For retry-prone creates/updates, accept idempotency key with unique entropy and bounded TTL.
- Store parameter hash, result status/body, caller identity, operation, and expiry.
- Reject same key with materially different parameters.
- Define behavior for 5xx, timeout, validation failure, concurrent same-key request, and expired key.

### 8.12 ページネーション

Pagination should exist at API birth for collection APIs. AIP-158 highlights that adding pagination later can be backward-incompatible in its model, and GitHub REST APIs expose pagination via Link headers and `per_page`. [[S14]][[S28]]

Minimum clone spec:

- Define default page size, max page size, cursor/page token shape, stable ordering, and continuation behavior.
- Prefer cursor/page token for mutable collections; avoid offset where consistency or performance is poor.
- Do not expose internal database cursor details in tokens; sign/encrypt tokens where necessary.
- Include next/previous links or tokens consistently.
- Document whether results are snapshot-consistent, eventually consistent, or best-effort.

### 8.13 検索・フィルタリング・ソート

Search and filtering turn collection APIs into query products. Google AIP-160 provides a filtering model and emphasizes returning the results users want. [[S29]]

Minimum clone spec:

- Define filter grammar, allowed fields, operators, sort keys, default sort, max query length, and index/cost policy.
- Reject or degrade expensive queries with clear error and docs.
- For GraphQL, use operation cost/depth/node limits; for REST, use query param grammar and documented indexes.
- Separate full-text search from structured filtering where semantics differ.
- Return deterministic ordering for pagination.

### 8.14 REST

REST/HTTP APIs should align URI/resource design with HTTP method semantics, status codes, headers, caching, conditional requests, and content negotiation. HTTP is stateless and defines shared protocol elements across versions. [[S07]]

Minimum clone spec:

- Use resource nouns, collections, stable IDs, and relationship links where applicable.
- Use GET/POST/PUT/PATCH/DELETE with documented semantics; avoid POST-only designs unless justified.
- Use status codes consistently: 200/201/202/204, 400/401/403/404/409/422/429, 5xx.
- Use ETag/If-Match or optimistic concurrency for conflicting updates where appropriate.
- Define cacheability, content type, and idempotency semantics.

### 8.15 GraphQL

GraphQL enables clients to specify the shape of data, but this shifts complexity into schema governance, resolver performance, authorization, and query cost control. The GraphQL specification governs the language, and the GraphQL over HTTP effort addresses interoperability over HTTP. [[S17]][[S18]]

Minimum clone spec:

- Maintain schema registry and schema change review.
- Define nullable/non-nullable fields carefully; changing nullability can be breaking.
- Enforce query depth, cost, node, resolver timeout, and payload limits.
- Use field-level authorization and sensitive-field masking.
- Prefer persisted queries or allowlisting for high-risk clients.
- Monitor resolver latency and fanout.

### 8.16 gRPC

gRPC is a high-performance RPC framework with service definitions, generated clients, streaming, and ecosystem support for load balancing, tracing, health checks, and auth. [[S19]]

Minimum clone spec:

- Define `.proto` files as source of truth; review field numbers, names, reserved fields, enum evolution, oneof usage, and package naming.
- Require deadlines/timeouts and document retry semantics.
- Use gRPC status codes consistently and map to HTTP status when transcoding.
- Use interceptors for auth, tracing, metrics, and validation.
- Use HTTP/JSON transcoding only where public/REST compatibility is intentionally designed.

### 8.17 WebSocket

WebSocket provides two-way communication after an HTTP opening handshake and message framing over TCP. It is suitable for realtime interactive sessions but requires session lifecycle, backpressure, auth refresh, and message schema control. [[S20]]

Minimum clone spec:

- Authenticate and authorize at handshake and subscription time.
- Define topics/channels, subscription filters, message schema, sequencing, ack/replay behavior, heartbeat, reconnect/backoff, and disconnect reasons.
- Enforce connection limits, subscription limits, message rate, payload size, and idle timeout.
- Use backpressure and drop/degrade rules for slow consumers.
- Monitor fanout latency, dropped messages, reconnect storms, and stale sessions.

### 8.18 Webhook

Webhooks are external event delivery contracts. They must handle sender timeout, receiver downtime, duplicate delivery, out-of-order delivery, replay, signature verification, and redelivery gaps. GitHub documents a 2xx response within 10 seconds and HMAC signature verification via `X-Hub-Signature-256`; Stripe recommends signature verification with official libraries. [[S21]][[S22]][[S24]]

Minimum clone spec:

- Define event types, payload schema, event ID, created time, API version, tenant/account, delivery ID, and idempotency/dedupe key.
- Sign payloads with endpoint secret; support secret rotation and replay protection.
- Receiver should return 2xx quickly and process asynchronously.
- Sender defines retry schedule, max attempts, redelivery mechanism, and manual replay.
- Document ordering guarantees or explicitly state when order is not guaranteed.
- Provide delivery logs and test/sandbox events.

### 8.19 HTTP

HTTP layer decisions cover method semantics, URI, headers, status, caching, conditional requests, content negotiation, trace, rate, deprecation, and security headers. RFC 9110 is the core reference for HTTP semantics. [[S07]]

Minimum clone spec:

- Define status code matrix and header registry for all APIs.
- Use `Content-Type`, `Accept`, `ETag`, `If-Match`, `Retry-After`, `Link`, trace headers, and Deprecation/Sunset where applicable.
- Avoid custom headers when standard headers or registered patterns exist, unless a clear reason exists.
- Preserve semantics across HTTP versions; do not couple API meaning to one gateway implementation.

---

## 9. Layer-by-Layer Clone Specs

### 07.01 API公開戦略

**Definition**: どの API をどの consumer に公開し、どの契約・認証・quota・support・法務条件で運用するかを決める。  
**Decision Question**: この API は public/partner/internal のどれとして公開すべきか、公開するならどの access control、docs、quota、SLA、support、terms が必要か。  
**Frontier Pattern**: API catalog と developer portal を持ち、公開範囲ごとに review/terms/auth/quota/support を分ける。  
**Metrics**: time-to-first-call, partner onboarding time, active clients, support tickets, abuse incidents, undocumented endpoint count.  
**Failure Modes**: owner 不明 API、docs なし公開、sandbox と本番の差、credential 発行の監査不備。  
**Confidence**: B。公開 API の設計要素は複数公式 docs で観測できるが、各社の内部公開判断は一部非公開。

### 07.02 API設計原則

**Definition**: API の横断的な設計規範を決める。  
**Decision Question**: どの resource model、protocol、schema、error、auth、rate、versioning、docs、review を全 API に強制するか。  
**Frontier Pattern**: Google/Azure 型の API Design Guide + OpenAPI/proto lint + review board + exception register。[[S04]][[S05]]  
**Metrics**: lint pass rate, design review lead time, exception count, breaking-change defects.  
**Failure Modes**: style guide はあるが CI で強制されない、例外が永久化する、protocol choice が場当たり。  
**Confidence**: A。

### 07.03 リソースモデル・ドメイン境界

**Definition**: API が表現する business/domain resource、collection、relationship、operation の境界を決める。  
**Decision Question**: どの概念を resource として外部 contract に出し、どの内部実装を隠すか。  
**Frontier Pattern**: 内部 DB/entity を直接露出せず、consumer の操作単位に合わせて stable resource を定義する。  
**Metrics**: duplicate resources, ambiguous ownership, support questions about concepts, compatibility of resource IDs.  
**Failure Modes**: DB table 名をそのまま API に出す、複数 API が同じ resource を違う意味で表す、関係性が actions に埋もれる。  
**Confidence**: B。

### 07.04 APIスキーマ・型システム

**Definition**: API の request/response/event/message の構造と進化規則を決める。  
**Decision Question**: どの schema artifact を source of truth にし、どの変更を互換/非互換と判定するか。  
**Frontier Pattern**: OpenAPI/JSON Schema/proto/GraphQL/AsyncAPI を canonical schema とし、CI で diff/lint/codegen を行う。[[S02]][[S06]][[S17]][[S19]][[S26]]  
**Metrics**: schema diff failures, generated SDK failures, incompatible field changes, validation error classes.  
**Failure Modes**: docs schema と runtime が違う、required field 追加、enum backward compatibility 破壊、proto field number 再利用。  
**Confidence**: A。

### 07.05 APIバージョニング・安定性

**Definition**: API の version、stability level、deprecation、sunset、migration を決める。  
**Decision Question**: 変更をどの stability level で公開し、どの契約で consumer を壊さず進化させるか。  
**Frontier Pattern**: alpha/beta/GA/deprecated/sunset/retired を定義し、Deprecation/Sunset headers と migration guide を使う。[[S30]][[S31]][[S32]][[S33]]  
**Metrics**: deprecated usage, migration completion, breaking-change incidents, version skew.  
**Failure Modes**: URI version だけで変更管理がない、docs だけで deprecation 通知、usage telemetry なし retirement。  
**Confidence**: A。

### 07.06 APIドキュメント・Developer Portal

**Definition**: API の発見・学習・試行・統合・運用を支える情報設計を決める。  
**Decision Question**: 利用者が self-service で API を使い始め、問題を診断し、変更に追随できるために何を公開するか。  
**Frontier Pattern**: Quickstart + interactive reference + examples + auth/rate/error/idempotency docs + changelog + SDK docs。  
**Metrics**: time-to-first-call, docs page success, search zero-result rate, support ticket categories.  
**Failure Modes**: reference だけで use case guide がない、changelog 不足、error/rate/idempotency docs 不足、SDK docs version skew。  
**Confidence**: B。

### 07.07 認証

**Definition**: caller/client/service/user の identity を確認する仕組みを決める。  
**Decision Question**: OAuth/OIDC/JWT/API key/mTLS/HMAC/workload identity のどれをどの risk profile で使うか。  
**Frontier Pattern**: OAuth/OIDC/JWT を delegated/user auth に、mTLS/workload identity を service auth に、HMAC signature を webhook に使い、RFC 9700 の BCP を反映する。[[S10]][[S11]][[S12]][[S13]]  
**Metrics**: auth failures, credential rotation, token misuse, leaked credentials, suspicious client activity.  
**Failure Modes**: API key を user auth と混同、audience/issuer 未検証、長寿命 token、credential in URL。  
**Confidence**: A。

### 07.08 認可・スコープ

**Definition**: authenticated principal が resource/action/field に対して何をできるかを決める。  
**Decision Question**: scope/RBAC/ABAC/tenant/resource ownership をどう組み合わせ、object/property authorization を保証するか。  
**Frontier Pattern**: scope は coarse gate、resource-level/object-level check は service が強制、sensitive field は property-level authorization。[[S39]]  
**Metrics**: authorization defects, overprivileged scopes, denied requests, cross-tenant access attempts.  
**Failure Modes**: token scope だけで object check 不足、IDOR/BOLA、mass assignment、hidden field update。  
**Confidence**: B。

### 07.09 レート制限・クォータ

**Definition**: API 利用を principal、tenant、endpoint、operation、cost に応じて制御する。  
**Decision Question**: どの単位で上限を設け、client にどう通知し、例外・増枠をどう管理するか。  
**Frontier Pattern**: 429/Retry-After、rate-limit headers/dashboard、secondary limits、GraphQL cost limit、quota tiering。[[S09]][[S15]][[S16]]  
**Metrics**: 429 rate, abuse blocked, quota exceptions, false positives, latency under load.  
**Failure Modes**: hidden throttling、IP only limit、Retry-After 不在、unbounded GraphQL/search、limit bypass by tokens.  
**Confidence**: A。

### 07.10 入力検証・契約検証

**Definition**: request を schema、semantic、security、business state の各面で検証する。  
**Decision Question**: どの validation を gateway/service/schema/contract test のどこで行うか。  
**Frontier Pattern**: schema validation + business authorization + semantic state validation + contract tests。[[S06]][[S38]][[S39]]  
**Metrics**: invalid request rejection, false rejection, injection attempts, escaped validation defects.  
**Failure Modes**: schema だけで business/state を検証しない、unknown fields の mass assignment、validation error が opaque。  
**Confidence**: A/B。

### 07.11 エラー設計

**Definition**: API failure を status、machine-readable error body、trace/correlation、retryability、docs link で表現する。  
**Decision Question**: client と support が同じ error を安定して識別・診断・retry 判定できるように何を返すか。  
**Frontier Pattern**: Problem Details 型 error、stable code、field-level validation errors、correlation/trace ID、retry guidance。[[S08]]  
**Metrics**: opaque error ratio, support escalation, retry misbehavior, error-code coverage.  
**Failure Modes**: 200 + error body、stack trace leakage、status code misuse、no correlation ID、client が retry 可否を判定できない。  
**Confidence**: A。

### 07.12 冪等性・リトライ

**Definition**: write/retry/duplicate request の side effect を安全化する。  
**Decision Question**: どの operation が retry-safe で、client はどの key/condition で再試行できるか。  
**Frontier Pattern**: create/update の idempotency key、parameter hash、dedupe storage、TTL、same-key mismatch handling。[[S23]]  
**Metrics**: duplicate side effects, retry success, idempotency key conflicts, mismatch rejections.  
**Failure Modes**: network timeout 後の duplicate create、same key different params、dedupe TTL 不明、5xx retry semantics 不明。  
**Confidence**: A。

### 07.13 ページネーション

**Definition**: collection response の分割、cursor、page size、ordering、continuation を決める。  
**Decision Question**: collection API を巨大化・不安定化させず、client が継続取得できる contract をどう作るか。  
**Frontier Pattern**: default/max page size、cursor/page token、stable order、Link/next token、pagination at outset。[[S14]][[S28]]  
**Metrics**: page latency, large response failures, cursor errors, client pagination misuse.  
**Failure Modes**: unbounded list、offset pagination with unstable ordering、token leaks internal state、pagination 後付け。  
**Confidence**: A。

### 07.14 検索・フィルタリング・ソート

**Definition**: collection から必要な対象を探索・絞り込み・並べ替える grammar と cost policy を決める。  
**Decision Question**: どの field/operator/sort を許可し、どの query を expensive として制御するか。  
**Frontier Pattern**: AIP-160 型 filtering、allowed fields/operators、index policy、cost limit、deterministic order。[[S29]]  
**Metrics**: query latency, expensive query rejections, zero-result rate, result relevance.  
**Failure Modes**: arbitrary SQL-like filter、unindexed sort、filter grammar undocumented、pagination と sort の非決定性。  
**Confidence**: B。

### 07.15 REST/HTTPリソースAPI

**Definition**: resource-oriented HTTP API の URI、method、status、headers、cache、conditional update を決める。  
**Decision Question**: HTTP semantics と domain resource をどう対応させるか。  
**Frontier Pattern**: RFC 9110 semantics + OpenAPI contract + standard status/header usage。[[S07]][[S02]]  
**Metrics**: method/status misuse, cache behavior, ETag/conflict handling, endpoint consistency.  
**Failure Modes**: POST-only RPC disguised as REST、status misuse、cache unsafe GET、conditional update 不在。  
**Confidence**: A。

### 07.16 GraphQL API

**Definition**: GraphQL schema、operation、resolver、query cost、field authorization を決める。  
**Decision Question**: client の exact data fetch を許しつつ、performance/security/compatibility をどう制御するか。  
**Frontier Pattern**: schema registry、field auth、query cost/depth/node limit、persisted queries、resolver observability。[[S17]][[S18]][[S16]]  
**Metrics**: query cost, resolver latency, field auth violations, schema breaking changes.  
**Failure Modes**: unbounded nested query、N+1 resolver、sensitive field exposure、nullable/non-nullable breaking changes。  
**Confidence**: A/B。

### 07.17 gRPC/Protocol Buffers

**Definition**: RPC service/method/message、streaming、deadlines、status、metadata、transcoding を決める。  
**Decision Question**: typed RPC をどの service boundary と compatibility rule で提供するか。  
**Frontier Pattern**: proto source of truth、generated clients、deadline/status/interceptors、proto compatibility rules。[[S19]][[S04]]  
**Metrics**: deadline exceeded, proto compatibility violations, generated client defects, streaming errors.  
**Failure Modes**: field number reuse、deadline 不在、status code inconsistency、HTTP transcoding が REST と矛盾。  
**Confidence**: A。

### 07.18 WebSocket/リアルタイム双方向

**Definition**: persistent bidirectional connection の session、message、subscription、backpressure を決める。  
**Decision Question**: client と server が長時間接続する中で auth、heartbeat、message schema、reconnect、flow control をどう扱うか。  
**Frontier Pattern**: handshake auth、subscription auth、heartbeat/reconnect、message schema、rate/connection limits、backpressure。[[S20]]  
**Metrics**: connection churn, reconnect storms, dropped messages, fanout latency, stale sessions.  
**Failure Modes**: auth refresh 不備、slow consumer で全体劣化、message schema drift、reconnect storm。  
**Confidence**: A/B。

### 07.19 Webhook/イベント通知

**Definition**: external event delivery の event schema、delivery、signing、retry、ordering、redelivery を決める。  
**Decision Question**: 非同期 event をどう安全・検証可能・再送可能に届けるか。  
**Frontier Pattern**: event catalog + signature + fast 2xx ack + async processing + delivery log + redelivery + event schema。[[S21]][[S22]][[S24]][[S25]][[S26]]  
**Metrics**: delivery success, signature failures, duplicate deliveries, redelivery lag, endpoint health.  
**Failure Modes**: unsigned payload、receiver が同期処理で timeout、ordering assumption、duplicate delivery 未処理、manual replay 不在。  
**Confidence**: A。

### 07.20 HTTP semantics・headers・status

**Definition**: API が HTTP の method/status/header/cache/trace/lifecycle semantics をどう使うかを決める。  
**Decision Question**: どの標準 HTTP mechanism を API contract に採用し、どの custom behavior を避けるか。  
**Frontier Pattern**: RFC 9110 base、Problem Details、429/Retry-After、Link、Trace Context、Deprecation/Sunset。[[S07]][[S08]][[S09]][[S32]][[S33]][[S34]]  
**Metrics**: header coverage, status correctness, trace propagation, client retry correctness.  
**Failure Modes**: custom header sprawl、status/code mismatch、missing trace、lifecycle signals missing。  
**Confidence**: A。

### 07.21 API Security

**Definition**: API 固有の脅威、abuse、data exposure、authorization failures を制御する。  
**Decision Question**: API の attack surface をどの threat model、control、test、monitoring で管理するか。  
**Frontier Pattern**: OWASP API Security Top 10 mapping、authz matrix、input validation、rate abuse controls、logging/audit、webhook signature。[[S39]]  
**Metrics**: API vulnerabilities, BOLA/BOPLA tests, abuse blocks, sensitive data exposure, security review coverage.  
**Failure Modes**: object auth 不備、overprivileged token、excessive data exposure、unsafe third-party API consumption。  
**Confidence**: B。

### 07.22 API Gateway/Edge Integration

**Definition**: external/internal edge で routing、TLS、auth、rate、policy、protocol translation をどう扱うかを決める。  
**Decision Question**: どの cross-cutting concern を gateway に寄せ、どの business logic を service に残すか。  
**Frontier Pattern**: gateway as centralized entrypoint for routing/security/rate/protocol translation; service retains business authorization。[[S36]][[S37]]  
**Metrics**: gateway latency, route incidents, policy drift, auth/rate enforcement coverage.  
**Failure Modes**: gateway が business auth を過剰保持、route shadowing、policy drift、single chokepoint capacity incident。  
**Confidence**: A/B。

### 07.23 SDK/client integration

**Definition**: API を SDK、CLI、generated client、examples でどう利用しやすく安定提供するかを決める。  
**Decision Question**: どの言語・runtime・retry default・versioning で client experience を提供するか。  
**Frontier Pattern**: contract-based codegen + hand-authored ergonomic layer + retry/idempotency/rate/error handling defaults。[[S02]][[S03]][[S23]]  
**Metrics**: SDK adoption, time-to-first-call, SDK support tickets, version skew, client error rate.  
**Failure Modes**: generated SDK が docs とずれる、retry default が dangerous、language SDK version skew、SDK が deprecated API を使う。  
**Confidence**: B。

### 07.24 Contract testing/compatibility

**Definition**: consumer/provider の contract を test と diff で検証し、互換性を守る。  
**Decision Question**: どの consumer behavior を contract として固定し、provider changes をどう検証するか。  
**Frontier Pattern**: schema diff + consumer-driven contract tests + provider verification + canary integration tests。[[S38]]  
**Metrics**: pre-prod compatibility failures, escaped breakages, consumer contract coverage.  
**Failure Modes**: static schema だけで behavior を検証しない、consumer が使わない field に過剰固定、provider verification 不足。  
**Confidence**: A/B。

### 07.25 Change management/deprecation

**Definition**: API change、migration、deprecation、sunset、retirement を運用する。  
**Decision Question**: 変更が consumer に与える影響をどう分類し、通知し、移行させ、完了確認するか。  
**Frontier Pattern**: changelog + migration guide + usage telemetry + Deprecation/Sunset headers + exception process。[[S32]][[S33]]  
**Metrics**: deprecated call volume, migration completion, customer escalations, deadline exceptions.  
**Failure Modes**: docs-only deprecation、usage unknown、unplanned retirement、SDK/partner の移行漏れ。  
**Confidence**: A。

### 07.26 Observability/audit/trace

**Definition**: API calls を trace、metrics、logs、audit events として観測可能にする。  
**Decision Question**: API 利用・失敗・権限・tenant・latency をどの粒度で追跡し、support/security/SRE が診断できるようにするか。  
**Frontier Pattern**: W3C Trace Context + OpenTelemetry + structured logs + audit trail + error correlation。[[S34]][[S35]]  
**Metrics**: trace coverage, log completeness, audit completeness, MTTR, unknown failure ratio.  
**Failure Modes**: correlation ID 不在、tenant/user/resource が audit されない、PII overlogging、trace breaks at gateway。  
**Confidence**: A/B。

### 07.27 SLO/SLA/availability/backpressure

**Definition**: API の reliability contract、latency、availability、timeout、degradation、backpressure を決める。  
**Decision Question**: API はどの availability/latency/error budget を約束し、過負荷時にどう劣化するか。  
**Frontier Pattern**: SLO/error budget + rate/backpressure + timeout/deadline + async queue + status/incident comms。  
**Metrics**: availability, p95/p99 latency, timeout rate, error budget burn, queue depth, backpressure events.  
**Failure Modes**: no timeout、unbounded queue、slow consumer cascade、retry storm、synchronous webhook processing。  
**Confidence**: B。

### 07.28 Multitenancy/tenant isolation

**Definition**: API の tenant boundary、quota isolation、data isolation、authorization を決める。  
**Decision Question**: 同じ API surface 上で tenant 間のデータ・quota・abuse・observability をどう分離するか。  
**Frontier Pattern**: tenant-aware authz、tenant-scoped rate limits、cross-tenant tests、audit per tenant、noisy-neighbor controls。  
**Metrics**: cross-tenant access attempts, noisy-neighbor incidents, tenant quota violations, isolation test pass rate.  
**Failure Modes**: tenant ID を client-supplied に依存、shared cursor token leaks、global quota only、audit に tenant 不在。  
**Confidence**: B。

### 07.29 API governance/review/lint

**Definition**: API design standard を実際の新規・変更 API に強制する review/lint/exception 制御を決める。  
**Decision Question**: API 標準違反をどう検出し、例外をどう認め、いつ見直すか。  
**Frontier Pattern**: API review board + automated lint + schema diff + security review + exception register。  
**Metrics**: lint pass rate, waiver count, review lead time, standards drift, escaped violations.  
**Failure Modes**: review が advisory だけ、waiver 永久化、manual checklist fatigue、lint rules outdated。  
**Confidence**: B。

### 07.30 Partner/onboarding/integration operations

**Definition**: パートナーが API を申請・試用・統合・運用・移行する workflow を決める。  
**Decision Question**: partner integration を self-service と control のどのバランスで運用するか。  
**Frontier Pattern**: onboarding checklist、sandbox、test credentials、certification、delivery logs、support runbook、health dashboard、migration comms。  
**Metrics**: onboarding time, integration pass rate, support load, partner health, failed deliveries, quota escalations.  
**Failure Modes**: manual onboarding bottleneck、sandbox mismatch、certification criteria unclear、partner-specific undocumented exceptions。  
**Confidence**: B/C。公開 docs から一般化できるが、個別企業の partner operations は非公開要素が多い。

---

## 10. Failure Modes

| Failure Mode | Description | Preventive Controls | Layers |
|---|---|---|---|
| Silent breaking change | schema/status/error/pagination/auth behavior が予告なく変わる | schema diff, contract tests, changelog, deprecation process | 07.04, 07.05, 07.24, 07.25 |
| Docs drift | docs と runtime/schema が一致しない | contract-first docs generation, docs CI, examples smoke tests | 07.06, 07.23 |
| Duplicate side effects | retry で複数 create/charge/update が発生する | idempotency key, dedupe store, retry policy | 07.12 |
| Unbounded collection | list/search が巨大 response や expensive query を返す | default/max page size, cursor, query cost, index policy | 07.13, 07.14, 07.09 |
| Opaque errors | client/support が failure を診断できない | Problem Details, stable error codes, correlation/trace IDs | 07.11, 07.26 |
| Overprivileged access | token/scope が resource/field の権限を超える | authz matrix, object/property checks, least privilege scopes | 07.08, 07.21, 07.28 |
| Webhook spoofing/replay | unsigned or unverifiable payload を処理する | HMAC signature, timestamp, secret rotation, replay cache | 07.19, 07.21 |
| Receiver timeout cascade | webhook receiver が同期処理し、delivery failure/duplicate が増える | quick 2xx ack, async queue, retry/redelivery docs | 07.19, 07.27 |
| GraphQL abuse | deep/expensive query が resolver fanout を起こす | cost/depth/node limits, persisted queries, resolver timeout | 07.16, 07.09, 07.21 |
| gRPC compatibility break | proto field reuse or incompatible message change | proto lint, reserved fields, compatibility tests | 07.17, 07.24 |
| Gateway policy drift | gateway config と service auth/route docs がずれる | policy-as-code, gateway CI, ownership map | 07.22, 07.29 |
| Missing trace/audit | incident/security investigation で request path が見えない | W3C Trace Context, OpenTelemetry, structured audit | 07.26 |
| Tenant data leak | tenant isolation が API layer で崩れる | tenant-scoped authz, tenant-aware tokens, isolation tests | 07.28, 07.08, 07.21 |
| Rate-limit surprise | hidden throttling or no retry guidance | 429, Retry-After, docs, quota dashboard | 07.09, 07.20 |
| Deprecated API dependency | deprecated endpoint/event still used by partners | usage telemetry, migration plan, partner outreach | 07.25, 07.30 |

---

## 11. Anti-patterns

| Anti-pattern | Why harmful | Replacement Pattern |
|---|---|---|
| “Docs after implementation” | docs drift と undocumented behavior を生む | contract-first with OpenAPI/proto/GraphQL/AsyncAPI |
| “POST everything” | resource semantics、cache、idempotency、authz が曖昧になる | REST resource methods or explicit RPC design |
| “Auth means token valid” | object/property authorization を見落とす | resource-level authorization matrix |
| “Unlimited list/search” | latency/cost/DoS リスク | pagination + query cost + filter whitelist |
| “Errors are free text” | clients が machine-process できない | Problem Details / stable error code |
| “Retry until success” | duplicate side effects and retry storms | idempotency + backoff + retryability classification |
| “Webhook payload trust” | spoofing/replay の温床 | HMAC signature + timestamp + replay cache |
| “GraphQL without cost controls” | resolver fanout and resource exhaustion | cost/depth/node/persisted query limits |
| “Gateway does all security” | business authz が gateway に過剰集中し drift する | gateway for coarse controls, service for resource auth |
| “Deprecation only in blog post” | runtime consumer が検知できない | docs + changelog + headers + usage telemetry |
| “One SDK version forever” | API evolution と client behavior が乖離する | SDK version policy and compatibility matrix |
| “Waiver without expiry” | standard erosion | exception register with expiry/review |

---

## 12. Maturity Model

| Level | Name | Criteria |
|---:|---|---|
| 0 | 未整備 | API inventory なし。docs と runtime が別管理。auth/rate/error/pagination が endpoint ごとに異なる。 |
| 1 | 個人依存 | 一部チームが docs/schema を持つが、横断標準・review・CI 強制はない。 |
| 2 | 文書化 | API style guide、OpenAPI/proto/GraphQL schema、docs、auth/rate/error ルールが存在する。 |
| 3 | 標準化 | API review、spec lint、schema diff、security review、gateway policy、error/rate/idempotency/pagination templates が標準化される。 |
| 4 | 自動化・計測 | CI/CD が lint/diff/contract tests/docs generation/gateway config を自動検証。trace、SLO、usage、deprecation telemetry が dashboard 化される。 |
| 5 | 自律改善・業界先端 | API portfolio が product metrics と security/reliability metrics で継続改善され、partner health、migration readiness、schema evolution、abuse controls が予測的に管理される。 |

---

## 13. Clone Implementation Guide

### Phase 0: Inventory and classification（0–2 weeks）

1. API catalog を作成し、公開範囲、owner、consumer、auth、schema、docs、gateway route、data sensitivity、SLO、version/deprecation status を記録する。
2. Public/partner API を優先し、schema/docs/auth/rate/error/pagination/idempotency の欠落を棚卸しする。
3. Critical API を data sensitivity、traffic、revenue/partner dependency、security risk、support load でランク付けする。
4. API governance owner と initial review board を指名する。

### Phase 1: Minimum standard（30 days）

1. API Style Guide v0 を作る。必須項目: resource naming、schema、auth/authz、rate、error、pagination、idempotency、versioning、webhook、observability。
2. OpenAPI/proto/GraphQL/AsyncAPI の source-of-truth policy を定義する。
3. Public/partner API の新規公開に review gate を必須化する。
4. Error catalog と Problem Details 型 template を作る。
5. Rate limit と 429/Retry-After の統一方針を作る。
6. Webhook signing と fast ack の template を作る。

### Phase 2: Automation and controls（60 days）

1. Spec lint、schema diff、contract tests を CI に組み込む。
2. Gateway policy-as-code を整備し、auth/rate/route/TLS/trace の標準設定を作る。
3. Docs generation と examples smoke tests を導入する。
4. Idempotency key implementation pattern と dedupe store を共通部品化する。
5. GraphQL cost/depth/node limit、gRPC deadline/status policy、WebSocket connection/rate policy を整備する。
6. Usage telemetry と trace/correlation ID を API dashboard に接続する。

### Phase 3: Lifecycle and partner operations（90 days）

1. Deprecation/Sunset policy と migration guide template を作る。
2. Deprecated usage dashboard と partner/customer outreach workflow を作る。
3. SDK generation/versioning/release checklist を整備する。
4. Developer portal に quickstart、sandbox、API keys/tokens、status/changelog、webhook delivery logs を統合する。
5. API incident postmortem template に schema break、authz defect、rate-limit surprise、webhook delivery failure、trace gap を組み込む。
6. Exception register を review cadence に乗せ、期限切れ waiver を自動検出する。

### Minimum Team Design

| Function | FTE / Role | Initial Responsibility |
|---|---|---|
| API Platform Lead | 1 | style guide, governance, tooling roadmap |
| API Architect / Design Authority | 1–2 | design review, resource/protocol decisions |
| AppSec/API Security | 0.5–1 | authz model, threat model, OWASP mapping |
| SRE/Gateway Engineer | 1 | gateway, rate limit, telemetry, SLO |
| Docs/DevRel | 1 | developer portal, quickstarts, migration guides |
| SDK/Client Engineer | 0.5–1 | SDK generation, language clients, examples |
| Partner Success/Support | 0.5–1 | onboarding, certification, support runbooks |

---

## 14. Pattern Library

| Pattern ID | Pattern | Layer Scope | Description | Preconditions | Tradeoffs | Confidence |
|---|---|---|---|---|---|---|
| P01 | Contract-first API | 07.02,07.04,07.06,07.23,07.24 | OpenAPI/proto/GraphQL/AsyncAPI を source of truth にする | schema tooling, CI | initial design overhead | A |
| P02 | Runtime lifecycle signaling | 07.05,07.25,07.20 | Deprecation/Sunset headers + docs/migration | HTTP API, usage telemetry | header interpretation not guaranteed | A |
| P03 | Idempotent write pattern | 07.12 | key + parameter hash + stored result + TTL | write retry risk | storage and concurrency complexity | A |
| P04 | Cursor pagination at outset | 07.13,07.14 | collection API に最初から cursor/default/max を入れる | stable order/index | implementation complexity | A |
| P05 | Machine-readable error | 07.11,07.20 | Problem Details-like error with stable code and trace | error catalog | client migration from legacy errors | A |
| P06 | Webhook signed async delivery | 07.19,07.21,07.27 | signature + quick 2xx + async queue + redelivery | endpoint secrets/logs | receiver complexity | A |
| P07 | GraphQL cost governance | 07.16,07.09,07.21 | query depth/cost/node limits and persisted queries | schema registry | reduces arbitrary query freedom | B |
| P08 | Gateway policy-as-code | 07.22,07.09,07.21,07.29 | routing/auth/rate/TLS/trace policy under CI | gateway platform | central bottleneck risk | B |
| P09 | Consumer-driven contract testing | 07.24 | consumer behavior encoded as executable contracts | consumer/provider CI | contract sprawl | A/B |
| P10 | Trace-context propagation | 07.26,07.20 | standard trace headers across gateway/services | observability stack | privacy/logging caution | A |
| P11 | Authz matrix | 07.08,07.21,07.28 | resource/action/field/tenant authorization mapped and tested | role/scope model | governance effort | B |
| P12 | API exception register | 07.29,07.02 | style-guide waivers with owner/expiry/risk | review board | review overhead | B |

---

## 15. Validation Queries

Use these queries to re-run or challenge the claims in this report.

```text
site:spec.openapis.org/oas OpenAPI Specification interface description HTTP APIs
site:cloud.google.com/apis/design API design guide REST RPC gRPC Protocol Buffers
site:github.com/microsoft/api-guidelines Azure REST API Guidelines idempotency versioning
site:datatracker.ietf.org RFC 9457 Problem Details HTTP APIs
site:datatracker.ietf.org RFC 6585 429 Too Many Requests Retry-After
site:docs.stripe.com/api idempotent requests idempotency key
site:docs.github.com REST API pagination Link header per_page
site:docs.github.com REST API rate limits secondary rate limits
site:docs.github.com GraphQL rate limits points query cost
site:graphql.github.io/graphql-over-http GraphQL over HTTP interoperability
site:grpc.io gRPC load balancing tracing health checking authentication
site:datatracker.ietf.org RFC 6455 WebSocket two-way communication opening handshake
site:docs.github.com webhooks 2XX 10 seconds X-Hub-Signature-256
site:cloudevents.io CloudEvents specification event data common formats
site:asyncapi.com AsyncAPI specification protocol agnostic message-driven APIs
site:datatracker.ietf.org RFC 9745 Deprecation HTTP response header
site:datatracker.ietf.org RFC 8594 Sunset HTTP response header
site:w3.org/TR/trace-context standard HTTP headers distributed tracing
site:opentelemetry.io APIs SDKs collector distributed traces metrics logs
site:owasp.org API Security Top 10 2023 broken object authorization
"API" "breaking change" "deprecation" "migration guide"
"webhook" "replay" "signature" "idempotency"
"GraphQL" "query depth" "cost limit" "authorization"
"gRPC" "proto" "reserved fields" "breaking change"
"OpenAPI" "schema diff" "lint" "breaking change"
```

---

## 16. Confidence & Unknowns

### High-confidence findings

- API contract should be machine-readable and tied to tooling: A.
- HTTP semantics, error design, rate limiting status, deprecation headers, WebSocket protocol, OAuth security practices are strongly grounded in standards/RFCs: A.
- Pagination, filtering, versioning, idempotency, REST/RPC/gRPC style patterns are strongly supported by official design guides and public operational docs: A/B.
- Webhook security and delivery behavior are grounded in public GitHub/Stripe docs and general event specs: A/B.
- Gateway/observability/contract testing patterns are well supported by public docs, but exact organizational workflows vary: B.

### Unknowns / not inferable from public sources

- Individual companies’ internal API review boards, approval thresholds, and exception politics.
- Exact private rate-limit algorithms and abuse detection heuristics beyond public docs.
- Partner-specific commercial terms, private support SLAs, and hidden migration exceptions.
- Proprietary API gateway policy implementation and incident learnings not publicly disclosed.
- Internal SDK release cadences and unreleased compatibility test matrices.

### Additional research if higher precision is required

1. Select 3–5 target companies and run per-company evidence extraction over public docs, changelogs, SDK repos, status pages, and developer forums.
2. Compare OpenAPI/proto/GraphQL schemas over historical versions via repository tags or Wayback snapshots.
3. Build a machine-readable source catalog and claims graph from the sources below.
4. Run incident/deprecation-specific searches for API outages, breaking changes, webhook failures, and SDK migration incidents.

---

## 17. Source Catalog

| ID | Source | Type | Tier | URL | Notes |
|---|---|---|---|---|---|
| S01 | RESEARCH.md | user-provided playbook | T0/T3 | local attachment | Clone Spec, evidence model, QA, scoring, triangulation procedure |
| S02 | OpenAPI Initiative | standard/community | T0 | https://www.openapis.org/ | OpenAPI overview and ecosystem |
| S03 | OpenAPI Specification GitHub | standard/spec | T0 | https://github.com/OAI/OpenAPI-Specification | OAS as programming-language-agnostic HTTP API description |
| S04 | Google Cloud API Design Guide | official design guide | T0/T3 | https://cloud.google.com/apis/design | Network API design, REST/RPC/gRPC/Protocol Buffers |
| S05 | Azure REST API Guidelines | official guideline | T0/T3 | https://github.com/microsoft/api-guidelines | Prescriptive Azure REST API guidance |
| S06 | JSON Schema Draft 2020-12 | standard/spec | T0 | https://json-schema.org/draft/2020-12 | JSON validation/schema vocabulary |
| S07 | RFC 9110 HTTP Semantics | standard/RFC | T0 | https://datatracker.ietf.org/doc/html/rfc9110 | HTTP architecture, semantics, URI, protocol elements |
| S08 | RFC 9457 Problem Details | standard/RFC | T0 | https://datatracker.ietf.org/doc/html/rfc9457 | Machine-readable HTTP API error details |
| S09 | RFC 6585 Additional HTTP Status Codes | standard/RFC | T0 | https://datatracker.ietf.org/doc/html/rfc6585 | 429 Too Many Requests |
| S10 | RFC 6749 OAuth 2.0 | standard/RFC | T0 | https://datatracker.ietf.org/doc/html/rfc6749 | OAuth 2.0 authorization framework |
| S11 | RFC 9700 OAuth 2.0 Security BCP | standard/RFC | T0 | https://datatracker.ietf.org/doc/rfc9700/ | Best current security practice for OAuth 2.0 |
| S12 | OpenID Connect Core 1.0 | standard/spec | T0 | https://openid.net/specs/openid-connect-core-1_0.html | Identity layer on OAuth 2.0 |
| S13 | RFC 7519 JWT | standard/RFC | T0 | https://datatracker.ietf.org/doc/html/rfc7519 | JSON Web Token claims format |
| S14 | GitHub REST Pagination Docs | official doc | T2/T3 | https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api | Link header, per_page |
| S15 | GitHub REST Rate Limits | official doc | T2/T3 | https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api | Primary/secondary rate limits |
| S16 | GitHub GraphQL Rate Limits | official doc | T2/T3 | https://docs.github.com/en/graphql/overview/rate-limits-for-the-graphql-api | Query points and hourly limits |
| S17 | GraphQL Specification | standard/spec | T0 | https://spec.graphql.org/ | GraphQL language/spec versions |
| S18 | GraphQL over HTTP | draft/spec | T0 | https://graphql.github.io/graphql-over-http/draft/ | HTTP interoperability for GraphQL |
| S19 | gRPC | official project | T0/T2 | https://grpc.io/ | High-performance RPC framework |
| S20 | RFC 6455 WebSocket | standard/RFC | T0 | https://datatracker.ietf.org/doc/html/rfc6455 | WebSocket handshake and framing |
| S21 | GitHub Handling Webhook Deliveries | official doc | T2/T3 | https://docs.github.com/en/webhooks/using-webhooks/handling-webhook-deliveries | 2xx within 10 seconds |
| S22 | GitHub Validating Webhook Deliveries | official doc | T2/T3 | https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries | HMAC signature header |
| S23 | Stripe Idempotent Requests | official doc | T2/T3 | https://docs.stripe.com/api/idempotent_requests | Idempotency key behavior |
| S24 | Stripe Webhook Signature Verification | official doc | T2/T3 | https://docs.stripe.com/webhooks/signature | Stripe-Signature verification |
| S25 | CloudEvents Specification | standard/CNCF | T0 | https://github.com/cloudevents/spec | Event metadata interoperability |
| S26 | AsyncAPI Specification | standard/spec | T0 | https://www.asyncapi.com/docs/reference/specification/latest | Protocol-agnostic message-driven API descriptions |
| S27 | Arazzo Specification | standard/spec | T0 | https://spec.openapis.org/arazzo/latest.html | API workflow description |
| S28 | Google AIP-158 Pagination | official design guide | T0/T3 | https://google.aip.dev/158 | Pagination guidance |
| S29 | Google AIP-160 Filtering | official design guide | T0/T3 | https://google.aip.dev/160 | Filtering guidance |
| S30 | Google AIP-181 Stability Levels | official design guide | T0/T3 | https://google.aip.dev/181 | API stability levels |
| S31 | Google AIP-185 API Versioning | official design guide | T0/T3 | https://google.aip.dev/185 | API versioning guidance |
| S32 | RFC 9745 Deprecation Header | standard/RFC | T0 | https://datatracker.ietf.org/doc/rfc9745/ | Deprecation HTTP response header |
| S33 | RFC 8594 Sunset Header | standard/RFC | T0 | https://datatracker.ietf.org/doc/html/rfc8594 | Sunset HTTP response header |
| S34 | W3C Trace Context | standard/W3C | T0 | https://www.w3.org/TR/trace-context/ | Distributed tracing headers |
| S35 | OpenTelemetry | official project | T3 | https://opentelemetry.io/docs/ | Observability framework |
| S36 | Kubernetes Gateway API | official project/spec | T2/T3 | https://gateway-api.sigs.k8s.io/ | Kubernetes service networking API |
| S37 | Envoy Gateway API Gateway Docs | official project | T2/T3 | https://gateway.envoyproxy.io/latest/concepts/api-gateways/ | API Gateway as routing/security/rate/protocol translation control plane |
| S38 | Pact Docs | official project | T3/T5 | https://docs.pact.io/ | Consumer-driven contract testing |
| S39 | OWASP API Security Top 10 2023 | third-party security taxonomy | T5 | https://owasp.org/API-Security/editions/2023/en/0x11-t10/ | API risk categories |
| S40 | CloudEvents HTTP Webhook | standard/spec | T0 | https://github.com/cloudevents/spec/blob/main/cloudevents/bindings/http-protocol-binding.md | HTTP binding / webhook-related event delivery model |

---

## 18. Machine-readable Skeleton

```yaml
cluster: API・インテグレーション設計
layer_range: "07"
generated_at: "2026-05-13"
confidence_policy:
  A: direct_evidence_from_T0_T1_T2
  B: corroborated_by_multiple_source_families
  C: plausible_but_not_directly_proven
  D: hypothesis
  X: rejected
core_patterns:
  - contract_first_api
  - schema_governed_evolution
  - explicit_authz_and_rate_controls
  - machine_readable_errors
  - idempotent_retry_safety
  - pagination_at_outset
  - event_delivery_security
  - lifecycle_signaling
  - observability_by_default
critical_artifacts:
  - api_catalog
  - api_style_guide
  - openapi_or_proto_or_graphql_or_asyncapi_contract
  - authz_matrix
  - error_catalog
  - rate_limit_policy
  - idempotency_policy
  - pagination_filtering_policy
  - webhook_event_catalog
  - gateway_policy_as_code
  - contract_tests
  - changelog_migration_guide
  - trace_audit_dashboard
validation_status:
  coverage: "T0/T2/T3 sources available for all major subthemes"
  critical_claims: "A/B only used in core recommendations"
  exceptions: "organization-internal review boards and partner workflows remain partially unknown"
```
