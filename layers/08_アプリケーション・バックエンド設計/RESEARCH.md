# Frontier Operating Model Research: アプリケーション・バックエンド設計（Layers 08）

生成日: 2026-05-13（Asia/Tokyo）  
対象単位: **アプリケーション・バックエンド設計**  
対象レイヤー: **08**  
対象サブテーマ: routing、controller/handler、application service、domain model、entity/value object、use case、validation、transaction boundary、exception、background job、workflow、retry/timeout、DI、config、feature flag、audit trail

---

## 0. 調査方針

本レポートは、公開情報のみを根拠に、アプリケーション・バックエンド設計を「意思決定システム」として再構成する。採用する証拠は、公式ドキュメント、標準仕様、クラウド/OSS の設計ガイド、セキュリティ実務ガイドを優先した。フレームワーク固有の実装差はあるが、本レポートでは特定言語のチュートリアルではなく、再現可能な設計原理、運用モデル、失敗条件、Clone Spec に落とす。

本調査では、対象レイヤー `08` を、ユーザー指定のサブテーマから内部枝番 `08.01`-`08.30` の 30 のバックエンド設計レイヤーへ正規化した。個別レイヤー名は、提示されたサブテーマをより細かい意思決定対象に分割したものであり、既存の社内レイヤー名がある場合は `layer_name_ja` の置換だけで利用できる。

信頼度は以下で扱う。

| 信頼度 | 意味 | 本レポートでの扱い |
|---|---|---|
| A | 公式仕様・公式 docs・標準に直接裏付けられる | Clone Spec の中核判断に採用 |
| B | 複数の公式/準公式証拠から強く推定できる | 中核または補助判断に採用 |
| C | 一般的に妥当だが、公開直接証拠は限定的 | Unknowns または実装時検証対象 |
| D | 仮説 | 採用しない |

---

## 1. エグゼクティブサマリー

アプリケーション・バックエンド設計の先端運用は、単に「クリーンアーキテクチャ」「DDD」「フレームワーク標準」に従うことではない。最も重要なのは、**外部入力をどの契約で受け、どのユースケースに変換し、どのドメイン境界で不変条件を守り、どのトランザクション境界で状態を確定し、どの失敗・再試行・監査の意味論で運用するか**を明示することである。

主要結論は以下である。

1. **routing と controller/handler は、ビジネス判断の場所ではなく、契約変換の境界である。** ASP.NET Core は routing を「HTTP request を executable endpoint に dispatch する責務」と定義し、Spring MVC は controller が request mapping、request input、exception handling などを annotation で表現すると説明する。[S01][S03] したがって、handler は thin に保ち、入力を use case/application service に委譲する。

2. **application service / use case は、ドメイン知識ではなく作業の調整を持つ。** Microsoft の .NET microservices guidance は application layer を Web API の一部または別ライブラリとして実装し、DI により infrastructure object を注入する設計を示す。[S10] 一方、domain model layer は business を表現し、persistence ignorance を守るべきだとする。[S11]

3. **domain model は bounded context、aggregate、entity、value object の組み合わせで不変条件を守る。** Azure Architecture Center は microservice を bounded context と結びつけ、DDD-oriented guidance は entity / value object / aggregate を文脈境界内に定義する。[S09][S11] Aggregate root は aggregate 更新の唯一の entry point として consistency guardian になる。[S12]

4. **transaction boundary は controller ではなく use case / aggregate consistency / persistence unit に合わせる。** Spring の transaction abstraction は `TransactionManager` により transaction の開始・commit・rollback を抽象化し、`@Transactional` は transaction semantics を対象コード近くに宣言する。[S16][S17] 分散状態更新では atomic transaction ではなく、outbox、saga、compensation、idempotent command を組み合わせる。[S18][S19]

5. **validation は syntactic と semantic に分け、外部入力の入口で早期に実施する。** OWASP は input validation を、外部 party からの不正形データが workflow に入ることを防ぐ機能として、data flow の可能な限り早い段階で実施すべきとする。[S07] Spring MVC も `@RequestBody` と Bean Validation の組み合わせで validation error を 400 に変換する挙動を提供する。[S04]

6. **exception は内部実装の偶発ではなく public error contract である。** RFC 9457 は HTTP API の machine-readable error details を定義し、RFC 7807 を置き換える標準である。[S05] Spring MVC も RFC 9457 `ProblemDetail` への mapping を公式に提供する。[S06]

7. **background job と workflow は別物として扱う。** FastAPI の background task は response 後の軽い作業に適している。[S20] Celery の task は retry、time limit、ack policy を持つ queue/worker 実行単位である。[S21][S22] Temporal の workflow は Event History を source of truth とし、deterministic replay により長期・失敗耐性のある workflow を構成する。[S23]

8. **retry / timeout は resilience tool だが、誤用すると障害増幅器になる。** AWS Builders Library は failure tolerance のために timeouts、retries、backoff を使うと説明しつつ、小さな失敗を complete outage に拡大しない設計を強調する。[S24] Azure の Retry pattern は transient fault に限って使うべきで、long-lasting fault や business logic error の代替ではないとする。[S25] Circuit breaker は retry と異なり、失敗しそうな操作の実行を一時的に止める。[S26]

9. **DI と config は可変性・テスト容易性・移植性の制御面である。** Spring は DI を、object が constructor / factory method / property で dependencies を定義し、container が bean 作成時に注入する process と定義する。[S27] Twelve-Factor App は config を environment variables に保存し、deploy ごとに orthogonal な granular control とする。[S29] Kubernetes は ConfigMap と Secret を分離し、Secret でも暗号化/RBAC 等が必要だと警告する。[S30][S31]

10. **feature flag と audit trail は運用時の意思決定制御である。** OpenFeature は feature flagging の vendor-agnostic API を提供し、runtime に behavior を変える仕組みを標準化する。[S32] OWASP Logging Cheat Sheet は application logging をセキュリティ/運用のために常設すべきとし、application は user identity、roles、permissions、event context を最もよく知る primary event data source だとする。[S34]

---

## 2. Layer Registry: 08

| Layer ID | Layer Name JA | Decision Object | 主な成果物 | Owner Roles | 代表メトリクス |
|---|---|---|---|---|---|
| 08.01 | ルーティング契約 | URL / method / host / media type をどの endpoint に対応させるか | route table, route template, endpoint map | Backend lead, API owner | route conflict count, 404 rate, route coverage |
| 08.02 | ルート照合・パラメータ抽出 | path/query/header から何を抽出し、型変換するか | path parameter schema, model binding rule | API owner, framework maintainer | binding error rate, invalid param rate |
| 08.03 | Middleware / Filter Pipeline | handler 前後にどの cross-cutting control を置くか | middleware order, filter policy | Platform/backend lead | latency overhead, auth/logging coverage |
| 08.04 | Controller / Handler Boundary | request をどこまで処理し、どこから application service に委譲するか | handler convention, controller checklist | Backend lead | handler LOC, business logic leakage count |
| 08.05 | Request Mapping / Action Selection | action を HTTP method、content type、version にどう対応させるか | mapping annotation/config | API owner | ambiguous action count, endpoint drift |
| 08.06 | DTO / Schema Boundary | external contract と domain object をどう分離するか | request DTO, response DTO, mapper, schema | API owner, domain owner | DTO/domain leak count, schema diff failures |
| 08.07 | Application Service | use case をどの application-level orchestration として実装するか | application service class/module | Application architect | use-case coverage, orchestration complexity |
| 08.08 | Use Case / Command Handler | 1 business action をどの command/query handler に落とすか | command, query, handler, result contract | Product/backend owner | handler success rate, command latency |
| 08.09 | Domain Model Boundary | business rule をどの bounded context / domain model に置くか | domain model package, ubiquitous language | Domain owner, architect | domain rule leakage, model cohesion |
| 08.10 | Entity Identity / Lifecycle | identity を持つ object の同一性と状態遷移をどう定義するか | entity class, state transition table | Domain owner | invalid transition count, identity conflict |
| 08.11 | Value Object | identity 不要な概念をどう不変値として表現するか | value object, equality rule | Domain owner | primitive obsession count, invalid value count |
| 08.12 | Aggregate Root / Consistency Boundary | 不変条件を守る更新入口と transaction consistency をどこに置くか | aggregate root, invariant list | Domain owner, DB owner | invariant violation, aggregate size, lock contention |
| 08.13 | Domain Service / Policy | entity/value object に自然に属さない domain rule をどう表現するか | domain service, policy object | Domain owner | anemic service count, rule duplication |
| 08.14 | Repository / Persistence Port | domain と persistence をどう分離するか | repository interface, mapper, query spec | Backend lead, DB owner | repository leakage, N+1 incidents |
| 08.15 | Unit of Work | 変更追跡と write coordination をどの単位で行うか | UoW/session context, commit rule | Backend lead | save count/request, stale update count |
| 08.16 | Transaction Boundary | transaction semantics と rollback rule をどこに宣言するか | transaction annotation/config, isolation rule | Backend lead, DB owner | rollback rate, deadlock rate, transaction duration |
| 08.17 | Validation Architecture | syntactic / semantic / invariant validation をどこで実施するか | validation rule catalog, validator, error mapping | Backend lead, security lead | validation failure rate, invalid persisted data |
| 08.18 | Exception Taxonomy | internal exception をどう分類し、どこで捕捉するか | exception taxonomy, handler policy | Backend lead | unhandled exception rate, error classification coverage |
| 08.19 | Error Response Contract | external error をどの machine-readable format で返すか | Problem Details schema, error code registry | API owner | malformed error rate, client handling success |
| 08.20 | Background Job Interface | request-response 外の work をどの task interface に切るか | job definition, payload schema, enqueue API | Backend lead, ops | enqueue latency, job acceptance rate |
| 08.21 | Queue / Worker Reliability | ack、retry、time limit、DLQ をどう制御するか | worker config, retry policy, DLQ playbook | Backend/ops | retry count, DLQ depth, duplicate processing rate |
| 08.22 | Workflow Orchestration | 長期・多段 business process をどう durable に進めるか | workflow definition, event history, activity contract | Workflow owner | workflow completion, stuck workflow count |
| 08.23 | Saga / Compensating Transaction | atomic transaction 不能な分散更新をどう補償するか | saga graph, compensation command, point-of-no-return | Domain/backend owner | compensation success, manual intervention count |
| 08.24 | Retry Policy | transient failure に対していつ何回 retry するか | retry matrix, backoff rule | Backend/infra owner | retry amplification, retry success rate |
| 08.25 | Timeout / Deadline Budget | caller/callee 間で待機上限をどう配分するか | timeout budget, deadline propagation | Backend/SRE | timeout false positive, tail latency |
| 08.26 | Dependency Injection | dependencies と lifecycle をどう宣言し、testable にするか | DI registration, scope rule | Backend lead | lifetime mismatch, constructor dependency count |
| 08.27 | Configuration Management | deploy ごとの差異をどうコード外で制御するか | config schema, env var registry, config source order | Platform/backend | config drift, invalid config boot failures |
| 08.28 | Secret & Sensitive Config | secret と non-secret config をどう分離し保護するか | secret store binding, RBAC, rotation rule | Security/platform | secret exposure incidents, rotation age |
| 08.29 | Feature Flag / Progressive Delivery | runtime behavior を誰がどの条件で切り替えるか | flag catalog, targeting rule, kill switch | Product/backend/SRE | stale flag count, rollout error rate |
| 08.30 | Audit Trail / Security Event Logging | 誰が何をいつどこでどう実行したかをどう記録するか | audit event schema, log retention rule, tamper control | Security/backend/compliance | audit coverage, missing actor rate, log integrity failures |

---

## 3. Frontier Exemplars

| Exemplar | Relevant Layers | 採用理由 | Evidence | Confidence |
|---|---:|---|---|---|
| ASP.NET Core / Microsoft Learn | 08.01–08.06, 08.26 | routing, endpoint, controller, model binding, DI が公式 docs に整理され、current .NET version の更新が継続している | [S01][S02][S28] | A |
| Spring Framework / Spring MVC | 08.01–08.19, 08.26 | request mapping、controller、validation、exception、RFC 9457 response、transaction、DI が同一公式体系で説明される | [S03][S04][S06][S16][S17][S27] | A |
| Microsoft .NET Microservices / Azure Architecture Center | 08.07–08.16, 08.22–08.23 | DDD microservice、application layer、domain model、aggregate、value object、transactional outbox、compensation を公式設計ガイドで扱う | [S09]–[S19] | A |
| OWASP Cheat Sheet Series | 08.17, 08.30 | input validation と application logging のセキュリティ実務が具体的に定義される | [S07][S34] | A |
| IETF RFC 9457 | 08.18–08.19 | HTTP API error response の標準 contract として利用できる | [S05] | A |
| AWS Builders Library | 08.24–08.25 | timeout/retry/backoff/idempotency の設計原理と失敗増幅リスクを実務的に説明する | [S24][S36] | A |
| Azure Architecture Center patterns | 08.16, 08.22–08.25 | Retry、Circuit Breaker、Compensating Transaction、Transactional Outbox など分散バックエンドの failure model が揃う | [S18][S19][S25][S26] | A |
| Temporal | 08.22 | Event History と deterministic replay により workflow durability を明確に実装する | [S23] | A |
| Celery | 08.20–08.21 | task retry、time limit、ack policy を持つ background worker の実務観測面が豊富 | [S21][S22] | A |
| Kubernetes / Twelve-Factor App | 08.27–08.28 | config と secret の分離、environment-specific configuration の外出しを明確に定義する | [S29][S30][S31] | A |
| OpenFeature / CNCF | 08.29 | feature flagging の vendor-neutral API と maturity signal を提供する | [S32][S33] | A |
| Rails / Django / FastAPI | 08.01–08.06, 08.17, 08.20, 08.26 | routing、URLconf、validation、background task、DI-like dependency system などの実装例が公式 docs にまとまる | [S08][S20][S35][S37] | B |

---

## 4. Evidence Map: 主要 Claim

| Claim ID | Claim | Evidence | Confidence |
|---|---|---|---|
| C-001 | routing は incoming HTTP request を endpoint に dispatch する責務であり、endpoint は executable request-handling code の単位である | ASP.NET Core routing docs [S01] | A |
| C-002 | controller は request mapping、input、exception handling を表現する境界であり、business rule の所有者ではない | Spring annotated controllers [S03], Microsoft DDD layers [S11] | A |
| C-003 | Web API controller は request handling のための class であり、per request basis で activate/dispose される | ASP.NET Core web API [S02] | A |
| C-004 | microservice / domain model 境界は bounded context と強く対応し、各 service は single business capability を実装すべきである | Azure microservices [S09] | A |
| C-005 | domain model layer は business を表現し、persistence details を infrastructure layer に委譲すべきである | Microsoft DDD-oriented guidance [S11] | A |
| C-006 | aggregate root は aggregate consistency を守る唯一の更新入口である | Microsoft domain model guidance [S12] | A |
| C-007 | value object は identity ではなく attributes/value により定義する | Microsoft value object guidance [S14], Azure tactical DDD [S15] | A |
| C-008 | application layer は use case の orchestration と infrastructure injection を担い、domain state を所有しない | Microsoft application layer guidance [S10][S11] | A |
| C-009 | request validation は syntactic/semantic に分け、外部入力のできるだけ早い段階で行う | OWASP input validation [S07] | A |
| C-010 | validation error は public error contract に変換され、内部 exception を漏らさない | Spring validation/error response [S04][S06], RFC 9457 [S05] | A |
| C-011 | transaction boundary は commit/rollback semantics を明示し、method/use case 近くで宣言できる | Spring transaction docs [S16][S17] | A |
| C-012 | reliable messaging には transactional outbox と idempotent processing が有効である | Azure outbox [S18] | A |
| C-013 | eventual consistency workflow では compensation、progress recording、idempotent command、manual intervention が必要になる | Azure compensating transaction [S19] | A |
| C-014 | workflow durability は event history と deterministic replay により担保できる | Temporal workflow docs [S23] | A |
| C-015 | background task は request 後処理用と queue/worker 用を分けるべきである | FastAPI background tasks [S20], Celery tasks/config [S21][S22] | B |
| C-016 | retry は transient fault に限定し、backoff/jitter/timeouts と合わせて障害増幅を避けるべきである | AWS Builders Library [S24], Azure Retry [S25] | A |
| C-017 | circuit breaker は retry と異なり、失敗しそうな operation を一時的に止める | Azure Circuit Breaker [S26] | A |
| C-018 | DI は dependencies を明示し、container が lifecycle に応じて注入することで testability/maintainability を高める | Spring DI [S27], ASP.NET DI [S28] | A |
| C-019 | config は code/image から分離し、non-secret と secret を区別する | Twelve-Factor [S29], Kubernetes ConfigMap/Secret [S30][S31] | A |
| C-020 | feature flag は runtime behavior を変更する system であり、vendor-neutral client API で抽象化できる | OpenFeature [S32][S33] | A |
| C-021 | audit/application log は application code が最も情報を持つ event source であり、when/where/who/what を記録すべきである | OWASP Logging [S34] | A |

---

## 5. Core Philosophy

### 5.1 Contract-first ingress

Routing、model binding、controller action は、外部契約を内部 use case に変換する ingress layer である。先端組織は route を単なる文字列ではなく、HTTP method、path、host、header、media type、version、auth context、rate context まで含む contract として扱う。Route conflict、ambiguous action、undocumented parameter は設計不備として扱う。

### 5.2 Thin handler, explicit use case

Handler は、認証済み/検証済み request を application command/query に変換し、use case を呼び、result を response DTO に変換する。Business state transition、domain invariant、transaction retry、compensation などは handler に置かない。これにより、Web framework から切り離した use case test が可能になる。

### 5.3 Domain model owns invariants

Domain model は data container ではなく business rule の実行主体である。Entity は identity と lifecycle を持ち、value object は identity を持たず value equality を持つ。Aggregate root は consistency boundary であり、外部から child entity を直接更新させない。

### 5.4 Transaction boundary follows consistency boundary

Local transaction は aggregate/use case の consistency boundary に合わせる。Controller 全体や HTTP request 全体を機械的に transaction にするのではなく、business action の atomicity、lock duration、isolation requirement、outbox emission、idempotency key の整合性を設計する。分散 transaction を避ける場合は saga/compensation/outbox を明示する。

### 5.5 Validation is layered

Validation は 4 層に分ける。

1. **Syntactic validation**: 型、形式、長さ、enum、range。
2. **Semantic validation**: business context での妥当性。
3. **Invariant validation**: aggregate/entity が常に守る状態制約。
4. **Policy validation**: 権限、契約、feature flag、risk rule など runtime policy。

### 5.6 Failure semantics is part of the API

Exception は内部実装ではなく、consumer が観測する contract に変換される。HTTP API では RFC 9457 Problem Details のような machine-readable schema を使い、domain error、validation error、auth error、rate limit、transient error、terminal error を分離する。

### 5.7 Async work requires explicit reliability semantics

Background job は「遅い処理を裏でやる」だけでは不十分である。enqueue 成功、payload schema、dedupe/idempotency、ack timing、retry/backoff、time limit、dead-letter、observability、audit を設計しなければならない。Workflow は queue task の連鎖ではなく、state history と replay/compensation を持つ長期 business process として扱う。

### 5.8 Runtime knobs are controlled artifacts

Config、Secret、Feature Flag は runtime behavior を変えるが、すべて同じではない。Config は deploy-specific parameter、Secret は confidential credential、Feature Flag は runtime decision policy である。Flag は kill switch と experimentation に使えるが、stale flag と hidden branch は technical debt になる。

### 5.9 Audit is not generic logging

Audit trail は debugging log ではない。Actor、action、object、result、time、correlation、policy context を持つ domain/security event であり、後から sequence reconstruction、incident investigation、compliance review に使える必要がある。

---

## 6. Decision Model

### 6.1 Inputs

- Business use case / user journey / external actor
- HTTP method、path、header、media type、API version
- Request DTO / schema / validation constraints
- Domain bounded context、ubiquitous language、business invariant
- Persistence model、transaction isolation、lock duration、outbox/event requirement
- Downstream dependencies、SLO、retryability、idempotency requirement
- Deployment environments、config/secrets、runtime flags
- Compliance/security logging requirements

### 6.2 Decision Object

「1 つの backend use case を、どの ingress contract、application orchestration、domain consistency boundary、transaction boundary、failure semantics、runtime controls、audit trail で実行可能にするか」

### 6.3 Criteria

| Criteria | 判定質問 |
|---|---|
| Contract clarity | Consumer が request/response/error/retry semantics を理解できるか |
| Separation of concerns | Handler、application service、domain model、infrastructure の責務が分かれているか |
| Invariant safety | Domain invariant が entity/aggregate 側で破られないか |
| Transaction minimality | Transaction scope が必要最小限かつ business consistency と一致するか |
| Retry safety | Retry しても duplicate side effect が起きないか |
| Observability/auditability | 失敗、遅延、変更、権限、actor を追跡できるか |
| Operational mutability | Config/flag で変更できる範囲と承認が明確か |
| Testability | Use case、domain rule、transaction、error mapping を独立 test できるか |

### 6.4 Priorities

1. External contract の明確性
2. Domain invariant の安全性
3. Transaction boundary の明示
4. Failure/retry/idempotency の明示
5. Auditability と observability
6. Runtime mutability の安全な制御
7. Framework-specific convenience より long-term maintainability

### 6.5 Prohibitions

- Controller/handler に business state transition を直書きする。
- Request DTO を domain entity として直接永続化する。
- Aggregate child entity を外部から直接更新する。
- Transaction を広げて remote call を含める。
- Retry 可能性を検証せずに automatic retry を入れる。
- Timeout なしの downstream call を実行する。
- Error response に internal exception class、stack trace、secret を含める。
- Feature flag を恒久的 branch として放置する。
- ConfigMap に confidential data を入れる。
- Audit trail を generic debug log と混同する。

### 6.6 Owners / Reviewers

| 領域 | Primary Owner | Reviewers |
|---|---|---|
| Routing/API contract | API owner / backend lead | Frontend lead, security, platform |
| Application service/use case | Application architect | Product owner, domain expert |
| Domain model/aggregate | Domain owner | Architect, DB owner |
| Transaction/outbox/workflow | Backend lead | SRE, DB owner, security |
| Validation/error contract | Backend lead | Security, API consumer representatives |
| Retry/timeout | Service owner | SRE/platform |
| DI/config/secrets | Backend/platform | Security |
| Feature flag | Product/backend/SRE | Security/compliance for sensitive flags |
| Audit trail | Security/compliance | Backend, data governance |

### 6.7 Cadence

| Event | Required Review |
|---|---|
| New endpoint / use case | API design + use case + validation + error + audit review |
| Domain invariant change | Domain model + aggregate + transaction boundary review |
| New async job/workflow | Idempotency + retry/timeout + DLQ/compensation review |
| New config/secret | Config schema + secret handling + environment rollout review |
| New feature flag | Owner + expiry + rollout/rollback + audit review |
| Incident / repeated retry storm | Retry/timeout/circuit breaker review |
| Quarterly | stale flag cleanup, audit coverage, exception taxonomy, route inventory |

---

## 7. Technical / Business Specification

### 7.1 Ingress: routing, middleware, controller

Required specification:

- Route template: method + path + version + content type + auth requirement.
- Parameter extraction: path/query/header/body/source precedence.
- Middleware order: correlation ID, auth, rate-limit, request logging, validation, response compression, exception mapping.
- Controller convention: no domain mutation without use case; no repository direct call except explicitly justified read-only simple endpoint.
- Return contract: success status, response DTO, error schema, idempotency/retry hints.

Implementation guardrails:

- Route tables are generated and linted for conflict.
- Attribute route and conventional route are not mixed without explicit reason.
- Handler contains no transaction demarcation unless use case is trivial and documented.
- Handler performs request-to-command mapping only; command handler owns business action orchestration.

### 7.2 Application service / use case

Required specification:

- Use case name and business intent.
- Input command/query and actor context.
- Required domain aggregate(s) and repository ports.
- Transaction boundary and outbox/event behavior.
- Validation sequence: request syntactic -> semantic precondition -> aggregate invariant.
- Error taxonomy: validation/domain/conflict/transient/terminal.

Implementation guardrails:

- Use case may coordinate repositories, domain services, domain events, and external ports.
- Use case must not contain entity-internal invariant logic that belongs to aggregate/entity.
- Application service can depend on abstractions, not concrete infrastructure.
- Side effects after commit are published via outbox/event dispatch, not inline remote call inside DB transaction.

### 7.3 Domain model

Required specification:

- Bounded context and ubiquitous language.
- Entity identity strategy: natural key, surrogate key, external reference.
- Value object equality and validation rules.
- Aggregate root and child entity update rules.
- Invariant catalog and allowed state transitions.
- Domain events emitted and handled by application-level handlers.

Implementation guardrails:

- Aggregate root is the only external update entry.
- Entity behavior is not replaced by procedural service scripts.
- Value objects are immutable or treated as immutable.
- Domain model is persistence ignorant except for unavoidable platform constraints.

### 7.4 Persistence, repository, unit of work, transaction

Required specification:

- Repository interface per aggregate or read model.
- Unit of Work / Session lifecycle.
- Transaction isolation level and timeout.
- Rollback rules and exception mapping.
- Outbox publication rule.
- Concurrency strategy: optimistic version, pessimistic lock, unique constraints, idempotency key.

Implementation guardrails:

- Repository implementation is infrastructure layer.
- Query-only operations may use specialized read model / query service; do not force aggregate hydration for every read.
- Transaction boundary must not include slow network calls unless technically unavoidable and explicitly justified.
- Commit success and outbox persistence are coupled when event delivery matters.

### 7.5 Validation and error contract

Required specification:

- Validation rule catalog by field/use case/domain invariant.
- Error code registry.
- Problem Details schema or equivalent.
- Redaction rules for error messages.
- Client-facing retryability hints.

Implementation guardrails:

- Syntactic validation at ingress.
- Semantic validation before transaction or inside use case depending on data freshness.
- Invariants enforced inside aggregate/entity.
- Exceptions are normalized by centralized handler/advice.

### 7.6 Background jobs and workflow

Required specification:

- Job name, payload schema, idempotency key, dedupe rule.
- Enqueue transaction relation: after commit, outbox, or independent queue write.
- Ack timing and retry policy.
- Time limits and cancellation behavior.
- DLQ and manual recovery playbook.
- Workflow event history, compensation, point-of-no-return.

Implementation guardrails:

- Request-scoped resources are not captured into background job closure.
- Long-running jobs have progress, heartbeat, cancellation, timeout.
- Job payload is versioned.
- Workflows are deterministic where replay is required.
- Compensation steps are idempotent and auditable.

### 7.7 Retry, timeout, circuit breaker

Required specification:

- Dependency matrix with timeout budget.
- Retryable exception/status codes.
- Max attempts, backoff, jitter.
- Circuit breaker thresholds.
- Idempotency requirement.
- Observability fields: attempt count, deadline, final outcome.

Implementation guardrails:

- No retry without timeout.
- No retry without idempotency/duplicate-safe semantics for writes.
- Backoff+jitter for fan-out or high-volume clients.
- Stop retry when circuit breaker reports non-transient failure.

### 7.8 DI, config, secret, feature flag

Required specification:

- DI lifetime rules: singleton/scoped/transient.
- Constructor dependency budget and optional dependency rules.
- Config schema and source precedence.
- Secret storage, mount/injection, rotation, RBAC.
- Feature flag owner, purpose, targeting, default, expiry, rollback.

Implementation guardrails:

- No service locator in domain model.
- No scoped dependency captured by singleton/background worker.
- No secret in ConfigMap, source code, log, error response.
- Feature flags have lifecycle and cleanup automation.

### 7.9 Audit trail

Required specification:

- Event type taxonomy.
- Actor: user/machine/service principal.
- Action and object/resource.
- Result status and reason.
- Time: event time and log time.
- Correlation/interaction ID.
- Policy/config/flag context where relevant.
- Redaction, retention, integrity, access control.

Implementation guardrails:

- Audit logs are separated from debug logs where retention/security differs.
- Audit trail cannot be fully disabled by runtime config.
- Sensitive values are masked, hashed, tokenized, or excluded.
- Log injection and log-based DoS are tested.

---

## 8. Layer-by-layer Clone Specs

### Layer 08.01: ルーティング契約

**Definition**  
HTTP request の method、path、host、header、media type、version を executable endpoint に対応させる contract を定義する。

**Decision Question**  
どの外部 actor が、どの URL/method/media/version で、どの endpoint に到達し、どの parameters が抽出されるべきか。

**Frontier Rule**  
Routing は URL 文字列ではなく endpoint contract として扱う。Route table は起動時設定または annotation/config に集約し、conflict と undocumented endpoint を検出する。[S01][S03]

**Required Artifacts**  
Route inventory、endpoint ownership、route template、API version rule、conflict lint result。

**Metrics**  
404 rate、405 rate、route conflict count、unknown endpoint count、deprecated route traffic。

**Failure Modes / Anti-patterns**  
曖昧 route、wildcard 過多、route と docs の不一致、consumer が推測に依存する path design。

**Confidence**  
A

### Layer 08.02: ルート照合・パラメータ抽出

**Definition**  
Path/query/header/body から request processing に渡す値を抽出し、型変換・デフォルト・必須性を定義する。

**Decision Question**  
どの入力源から、どの型・制約・default で command/query に変換するか。

**Frontier Rule**  
Binding は framework に任せるだけでなく、source precedence、nullable、collection、enum、date/time、locale、encoding を明示する。Invalid binding は validation/error contract に流す。[S04][S07]

**Required Artifacts**  
Parameter schema、binding precedence、conversion rule、invalid parameter error mapping。

**Metrics**  
Binding failure rate、invalid enum count、unexpected null count、parameter deprecation usage。

**Failure Modes / Anti-patterns**  
暗黙変換で domain error 化する、query parameter が増え続ける、time zone/locale の未定義。

**Confidence**  
B

### Layer 08.03: Middleware / Filter Pipeline

**Definition**  
Request が handler に到達する前後の cross-cutting controls を順序付きで定義する。

**Decision Question**  
Authentication、authorization、correlation、logging、exception handling、rate limiting、compression などをどの順序で実行するか。

**Frontier Rule**  
Middleware order は security と observability の挙動を決めるため、コード上の偶発ではなく policy artifact にする。Exception mapping は outer layer に置き、audit/correlation は早期に付与する。

**Required Artifacts**  
Pipeline diagram、middleware order、filter responsibility、bypass rule。

**Metrics**  
Middleware latency overhead、missing correlation ID、unaudited endpoint count、filter bypass count。

**Failure Modes / Anti-patterns**  
Auth より前に sensitive logging、exception handler より内側で error response がばらつく、duplicate filters。

**Confidence**  
B

### Layer 08.04: Controller / Handler Boundary

**Definition**  
HTTP request を application command/query に変換し、response DTO を返す境界を定義する。

**Decision Question**  
Controller は何を処理し、何を application service/use case/domain に委譲するか。

**Frontier Rule**  
Controller は request mapping、input、exception handling の表現境界であり、business rule と transaction orchestration は use case/application service に逃がす。[S02][S03][S11]

**Required Artifacts**  
Handler convention、allowed responsibilities checklist、DTO mapper、controller unit test。

**Metrics**  
Handler LOC、repository direct call count、business rule leakage count、controller cyclomatic complexity。

**Failure Modes / Anti-patterns**  
Fat controller、handler ごとの個別 transaction、domain entity 直接返却、controller 内 retry。

**Confidence**  
A

### Layer 08.05: Request Mapping / Action Selection

**Definition**  
Route と HTTP method、headers、content negotiation、version、media type から具体的 action を選ぶ規則を定義する。

**Decision Question**  
同一 route family 内で action selection をどの属性で disambiguate するか。

**Frontier Rule**  
REST API では HTTP method specific mapping を基本とし、headers/media/version による selection はドキュメント化する。Spring は `@RequestMapping` と method shortcut mapping を公式に区別する。[S03]

**Required Artifacts**  
Action selection table、content negotiation rule、API versioning rule、deprecation rule。

**Metrics**  
Ambiguous action count、unsupported media type rate、version mismatch rate。

**Failure Modes / Anti-patterns**  
同一 path に多すぎる action、header magic、version rule の非互換混在。

**Confidence**  
A

### Layer 08.06: DTO / Schema Boundary

**Definition**  
External request/response contract と internal domain/entity/model を分離する。

**Decision Question**  
どの DTO/schema を公開し、domain object への mapping と逆 mapping をどう行うか。

**Frontier Rule**  
Domain entity は presentation/API layer に直接伝播させない。Microsoft guidance は domain entity が domain model layer に属し、presentation/view model に直接属さないと説明する。[S11]

**Required Artifacts**  
Request DTO、response DTO、schema、mapping function、field deprecation registry。

**Metrics**  
Domain leak count、schema breaking changes、mapping coverage、unknown field rate。

**Failure Modes / Anti-patterns**  
ORM entity を JSON に直接 serialize、DTO と domain の双方向 mutable coupling、schema evolution の未設計。

**Confidence**  
A

### Layer 08.07: Application Service

**Definition**  
Use case を実行する application-level orchestration を定義する。Domain rule を所有せず、domain object、repository、external port、transaction を調整する。

**Decision Question**  
どの application service が、どの use case を、どの ports と transaction で実行するか。

**Frontier Rule**  
Application layer は Web API project 内または別 library として実装できるが、infrastructure objects は DI で注入し、domain rules は domain model に委譲する。[S10][S11]

**Required Artifacts**  
Application service interface、dependencies、use case list、transaction rule、test doubles。

**Metrics**  
Use case coverage、external port count/use case、domain rule leakage、application service complexity。

**Failure Modes / Anti-patterns**  
Application service が procedural god service 化、domain model が anemic、infrastructure 具象への直接依存。

**Confidence**  
A

### Layer 08.08: Use Case / Command Handler

**Definition**  
単一 business action を command/query handler として明示し、入力、出力、例外、transaction、side effects を定義する。

**Decision Question**  
この business action は command か query か、どの state を変え、どの結果を返すか。

**Frontier Rule**  
Use case は front-end や transport に引きずられず、actor intent と domain outcome で命名する。Command は mutation と side effect、Query は read model と cacheability を分離する。

**Required Artifacts**  
Command/query DTO、handler、precondition、postcondition、result object、error mapping。

**Metrics**  
Command success rate、query latency、side effect count、handler test coverage。

**Failure Modes / Anti-patterns**  
CRUD endpoint = use case とみなす、1 handler が複数 business intent を処理する、read と write の transaction が混在。

**Confidence**  
B

### Layer 08.09: Domain Model Boundary

**Definition**  
Business language、rules、constraints を表す domain model を bounded context 内で定義する。

**Decision Question**  
どの business concept と rules が同じ domain model に属し、どこから別 bounded context になるか。

**Frontier Rule**  
DDD は single unified model ではなく bounded contexts に分割する。Microservice は aggregate より小さくせず、bounded context より大きくしないのが一般原則として提示される。[S09][S15]

**Required Artifacts**  
Context map、ubiquitous language、domain object catalog、boundary decision log。

**Metrics**  
Cross-context call count、domain term conflict、model churn、duplicate rule count。

**Failure Modes / Anti-patterns**  
全社統一巨大 model、context を跨ぐ entity 共有、domain language と DB schema の混同。

**Confidence**  
A

### Layer 08.10: Entity Identity / Lifecycle

**Definition**  
Identity を持つ domain object の同一性、状態、lifecycle、state transition を定義する。

**Decision Question**  
どの concept が entity であり、自然キー/サロゲートキー/外部IDをどう扱うか。

**Frontier Rule**  
Entity は unique identity を持ち、attribute が変わっても同一 domain concept として扱われる。Identity strategy は bounded context と service boundary を跨ぐ参照安定性を考慮して選ぶ。[S15]

**Required Artifacts**  
Entity definition、identity strategy、state transition diagram、lifecycle events。

**Metrics**  
Identity collision、invalid transition、orphan entity count、state repair count。

**Failure Modes / Anti-patterns**  
Mutable natural key を primary identity にする、external ID と internal ID を混同、state transition を handler で散在実装。

**Confidence**  
A

### Layer 08.11: Value Object

**Definition**  
Identity を持たず、値の組み合わせにより定義される domain concept を表現する。

**Decision Question**  
どの concept は entity ではなく value object として不変・比較可能にすべきか。

**Frontier Rule**  
Value object は identity ではなく attributes/value で定義される。同じ属性値なら交換可能であり、住所、通貨額、期間、測定値などが典型である。[S14][S15]

**Required Artifacts**  
Value object class、equality rule、validation rule、serialization rule。

**Metrics**  
Primitive obsession count、invalid value construction、value object mutation count。

**Failure Modes / Anti-patterns**  
金額を numeric + currency なしで扱う、住所や期間を string のまま扱う、value object を mutable entity のように扱う。

**Confidence**  
A

### Layer 08.12: Aggregate Root / Consistency Boundary

**Definition**  
複数 entity/value object の consistency を守る更新入口と transaction consistency boundary を定義する。

**Decision Question**  
どの object cluster が 1 aggregate であり、どの root が invariant を保証するか。

**Frontier Rule**  
Aggregate root は aggregate の唯一の update entry point であり、child entity/value object を直接更新させない。Aggregate は business action の終端で consistent でなければならない。[S12][S13]

**Required Artifacts**  
Aggregate diagram、root methods、invariant list、allowed external references、domain events。

**Metrics**  
Invariant violation、aggregate method bypass、aggregate size、lock contention、cross-aggregate transaction count。

**Failure Modes / Anti-patterns**  
Aggregate が巨大すぎる、child entity を repository で直接保存、複数 aggregate を単一 local transaction に常時巻き込む。

**Confidence**  
A

### Layer 08.13: Domain Service / Policy

**Definition**  
Entity/value object に自然に属さない domain rule、複数 aggregate にまたがる calculation/policy を表現する。

**Decision Question**  
この rule は entity/aggregate の behavior か、domain service/policy として独立すべきか。

**Frontier Rule**  
Entity は behavior を持つべきで、business logic が service class に逃げすぎると anemic domain model になる。Entity に自然に置けない rule のみ domain service/policy として切る。[S15]

**Required Artifacts**  
Domain service interface、policy rule、domain inputs/outputs、test cases。

**Metrics**  
Policy duplication、anemic entity count、service method complexity。

**Failure Modes / Anti-patterns**  
全 business logic が `*Service` に集約される、domain service が infrastructure port に依存、policy が controller に散在。

**Confidence**  
B

### Layer 08.14: Repository / Persistence Port

**Definition**  
Domain/application layer と persistence implementation を分離する port を定義する。

**Decision Question**  
Aggregate/read model をどの repository/query port 経由で取得・保存し、domain layer を persistence framework から隔離するか。

**Frontier Rule**  
Repository implementation は domain model layer の外、infrastructure layer に置く。Domain layer は ORM/API details に汚染されないようにする。[S13]

**Required Artifacts**  
Repository interface、query specification、mapper、infrastructure implementation、test fake。

**Metrics**  
N+1 incidents、repository method explosion、domain dependency on ORM、query latency。

**Failure Modes / Anti-patterns**  
Generic repository の乱用、ORM query object を domain layer に漏らす、read-heavy query を aggregate repository に押し込む。

**Confidence**  
A

### Layer 08.15: Unit of Work

**Definition**  
Business transaction で変更された object を追跡し、write-out と concurrency resolution を調整する。

**Decision Question**  
どの scope で object changes を蓄積し、いつ flush/commit するか。

**Frontier Rule**  
Unit of Work は business transaction に影響を受ける object list を管理し、変更の書き出しと concurrency 問題の解決を調整する。ORM session/DbContext が実装する場合もあるが、application code はその scope を明示すべきである。[S38][S39]

**Required Artifacts**  
UoW scope rule、session lifecycle、flush/commit rule、concurrency policy。

**Metrics**  
Flush count/request、commit duration、stale object conflicts、memory growth per UoW。

**Failure Modes / Anti-patterns**  
1 request で複数曖昧 commit、session を background worker に持ち越す、lazy loading で transaction 外アクセス。

**Confidence**  
A

### Layer 08.16: Transaction Boundary

**Definition**  
Atomicity、isolation、rollback、commit、outbox persistence をどの use case/method/aggregate scope で行うか定義する。

**Decision Question**  
この use case はどこからどこまでを 1 transaction とし、どの例外で rollback し、どの side effect を commit 後に出すか。

**Frontier Rule**  
Transaction semantics は `TransactionManager` や `@Transactional` のように明示し、local DB transaction と distributed workflow を混同しない。[S16][S17]

**Required Artifacts**  
Transaction annotation/config、isolation level、timeout、rollback rule、outbox coupling rule。

**Metrics**  
Transaction duration、deadlock rate、rollback rate、lock wait、remote call inside transaction count。

**Failure Modes / Anti-patterns**  
Controller 全体を transaction にする、transaction 内で external API を呼ぶ、rollback rule が exception taxonomy と不一致。

**Confidence**  
A

### Layer 08.17: Validation Architecture

**Definition**  
外部入力、use case precondition、domain invariant、policy validation をどこで行うか定義する。

**Decision Question**  
どの validation は ingress、application service、domain model、DB constraint、policy engine のどこで実行すべきか。

**Frontier Rule**  
OWASP は input validation を syntactic/semantic に分け、外部入力を data flow の早期で検証することを推奨する。Spring MVC は request method validation と Bean Validation を controller method に適用できる。[S07][S04]

**Required Artifacts**  
Validation catalog、validator classes、domain invariant test、error mapping。

**Metrics**  
Validation failure rate、invalid persisted data、late validation failure、false rejection rate。

**Failure Modes / Anti-patterns**  
Validation を client-side に依存、format validation と business invariant の混同、DB constraint だけに依存。

**Confidence**  
A

### Layer 08.18: Exception Taxonomy

**Definition**  
Internal exception を domain/validation/auth/conflict/transient/terminal/infrastructure などに分類し、捕捉・変換規則を定義する。

**Decision Question**  
どの exception は retryable か、どの exception は user-visible domain error か、どこで centralized handling するか。

**Frontier Rule**  
Local handler と global advice を分け、internal exception を public error contract に変換する。Spring の `@ExceptionHandler` / `@ControllerAdvice` は centralized handling を実装する公式 mechanism である。[S06]

**Required Artifacts**  
Exception taxonomy、retryability matrix、mapping handler、redaction rule。

**Metrics**  
Unhandled exception rate、unknown exception class count、stack trace exposure、retryable misclassification。

**Failure Modes / Anti-patterns**  
`Exception` 一括 catch、domain error と infrastructure error の混同、client に internal class name を返す。

**Confidence**  
A

### Layer 08.19: Error Response Contract

**Definition**  
External consumer が error を machine-readable に解釈できる response format と code registry を定義する。

**Decision Question**  
HTTP status、problem type、error code、message、details、correlation ID、retryability をどの schema で返すか。

**Frontier Rule**  
HTTP API では RFC 9457 Problem Details を baseline とし、標準 field と extension field を定義する。Spring MVC は RFC 9457 response を有効化できる。[S05][S06]

**Required Artifacts**  
Problem Details schema、error code registry、example responses、client handling guide。

**Metrics**  
Malformed error response、unknown error code、client retry misuse、error docs coverage。

**Failure Modes / Anti-patterns**  
HTTP 200 with error body、status code と body の矛盾、localized message だけで machine-readable code なし。

**Confidence**  
A

### Layer 08.20: Background Job Interface

**Definition**  
HTTP request/response の外で実行する work を task/job として定義し、payload、enqueue、completion、observability を設計する。

**Decision Question**  
この処理は request 後に軽く実行する background task か、queue/worker に投げる durable job か。

**Frontier Rule**  
FastAPI の background task は response 後に実行する軽量処理に向く。一方、耐久性・retry・time limit が必要な work は Celery 等の worker task として schema/retry/ack を設計する。[S20][S21]

**Required Artifacts**  
Job name、payload schema、enqueue API、idempotency key、status model。

**Metrics**  
Enqueue latency、job success rate、payload validation failure、orphan job count。

**Failure Modes / Anti-patterns**  
Request object/DB session を closure に捕捉、job payload が versionless、response success と enqueue failure の不整合。

**Confidence**  
A

### Layer 08.21: Queue / Worker Reliability

**Definition**  
Queue worker の ack、retry、time limit、result storage、DLQ、duplicate handling を定義する。

**Decision Question**  
失敗時に message をいつ ack し、何回 retry し、どこに隔離し、どう復旧するか。

**Frontier Rule**  
Task retry には task context が必要であり、worker time limit と ack behavior は明示的に config する。Celery は `task_time_limit`、soft time limit、late ack、error callback などを公式設定として持つ。[S21][S22]

**Required Artifacts**  
Retry policy、ack policy、DLQ policy、worker time limit、manual replay procedure。

**Metrics**  
Retry attempts/job、DLQ depth、duplicate side effects、worker crash rate、hard timeout count。

**Failure Modes / Anti-patterns**  
At-least-once delivery なのに idempotency なし、poison message が無限 retry、hard timeout 後の partial side effect 未処理。

**Confidence**  
A

### Layer 08.22: Workflow Orchestration

**Definition**  
長期・多段・失敗耐性が必要な business process を workflow として定義し、状態、履歴、activity、retry、timeout、replay を管理する。

**Decision Question**  
この business process は queue task の連鎖で足りるか、durable workflow として Event History / compensation / replay が必要か。

**Frontier Rule**  
Temporal は Event History を workflow の source of truth とし、replay により workflow state を再構築する。Workflow code は deterministic でなければならない。[S23]

**Required Artifacts**  
Workflow definition、activity contract、event history schema、determinism constraints、timeout/retry policy。

**Metrics**  
Workflow completion rate、stuck workflow、activity retry count、replay failure、manual intervention rate。

**Failure Modes / Anti-patterns**  
Non-deterministic code、workflow 内の直接 network call、workflow history の無制限肥大、activity timeout 未設定。

**Confidence**  
A

### Layer 08.23: Saga / Compensating Transaction

**Definition**  
複数 services/data stores にまたがる eventual consistency operation の失敗時に、completed steps を domain-specific に補償する。

**Decision Question**  
どの step は compensable で、どの step は irreversible であり、失敗時に誰がどの undo action を実行するか。

**Frontier Rule**  
Compensating transaction は単純 rollback ではない。各 step と undo information を記録し、失敗時に completed step を domain rule に従って戻す。Compensation 自体も失敗し得るため、progress recording、idempotent command、manual alert が必要になる。[S19]

**Required Artifacts**  
Saga graph、forward command、compensation command、point-of-no-return、manual intervention playbook。

**Metrics**  
Compensation success rate、irreversible failure count、manual intervention count、saga duration。

**Failure Modes / Anti-patterns**  
Compensation を DB rollback と同一視、undo に必要な情報を記録しない、irreversible step を先に実行。

**Confidence**  
A

### Layer 08.24: Retry Policy

**Definition**  
Transient failure に対して retry する条件、回数、delay、backoff、jitter、stop condition を定義する。

**Decision Question**  
この operation は retry safe か。どの status/exception を retry し、どの条件で諦めるか。

**Frontier Rule**  
Retry は transient fault に限定する。AWS は timeout/retry/backoff を essential tool としつつ、小さな failure を complete outage に増幅しない設計を強調する。Azure も long-lasting fault や business logic error には retry を使わないべきとする。[S24][S25]

**Required Artifacts**  
Retry matrix、retryable errors、max attempts、backoff+jitter、idempotency requirement。

**Metrics**  
Retry success rate、retry amplification factor、duplicate side effects、downstream 429/503 trend。

**Failure Modes / Anti-patterns**  
全 error retry、write operation に idempotency なし、fan-out retry storm、client/server 双方で過剰 retry。

**Confidence**  
A

### Layer 08.25: Timeout / Deadline Budget

**Definition**  
Operation / dependency / workflow step ごとの最大待機時間と deadline propagation を定義する。

**Decision Question**  
Caller の SLO から各 downstream call にどれだけ time budget を配分し、どこで fail fast するか。

**Frontier Rule**  
Timeout は client が request 完了を待つ最大時間であり、長すぎれば資源を消費し、短すぎれば retry 増幅を引き起こす。Timeout、retry、backoff は一体で設計する。[S24]

**Required Artifacts**  
Timeout budget table、deadline propagation rule、connection/read/write timeout、workflow/activity timeout。

**Metrics**  
Timeout rate、false timeout、tail latency、resource exhaustion、deadline exceeded without retry。

**Failure Modes / Anti-patterns**  
Timeout 未設定、OS/library default に依存、caller deadline より長い callee timeout、timeout 後も worker が処理継続。

**Confidence**  
A

### Layer 08.26: Dependency Injection

**Definition**  
Object dependencies と lifecycle を container/configuration で宣言し、testability と modularity を制御する。

**Decision Question**  
どの dependencies を constructor/factory/property で要求し、どの lifetime scope で注入するか。

**Frontier Rule**  
Spring は DI を dependencies を constructor/factory/property で定義し、container が bean 作成時に注入する process と定義する。ASP.NET Core も built-in DI を持ち、controller が dependencies を明示的に要求する。[S27][S28]

**Required Artifacts**  
DI registration、lifetime policy、scope compatibility rule、test override mechanism。

**Metrics**  
Lifetime mismatch、service locator usage、constructor parameter count、unregistered dependency failures。

**Failure Modes / Anti-patterns**  
Singleton が scoped resource を捕捉、domain model が container に依存、optional dependency の乱用、service locator 化。

**Confidence**  
A

### Layer 08.27: Configuration Management

**Definition**  
Deploy ごとに異なる non-secret configuration を code/image から分離し、source precedence、validation、reloadability を定義する。

**Decision Question**  
どの値は config として外出しし、どの source order と validation rule で読み込むか。

**Frontier Rule**  
Twelve-Factor App は config を environment variables に保存し、deploy ごとに independent granular controls として管理する。Kubernetes ConfigMap は non-confidential key-value data を Pod に env/args/file として渡し、image から environment-specific config を分離する。[S29][S30]

**Required Artifacts**  
Config schema、env var registry、default rule、source precedence、startup validation。

**Metrics**  
Invalid config boot failure、config drift、unknown config key、runtime reload failures。

**Failure Modes / Anti-patterns**  
コードに環境値を直書き、environment grouping 爆発、config validation なし、ConfigMap に secret を置く。

**Confidence**  
A

### Layer 08.28: Secret & Sensitive Config

**Definition**  
Password、token、key、connection string 等の sensitive data を non-secret config と分離し、保護、注入、rotation を制御する。

**Decision Question**  
どの値は secret であり、どの storage/injection/access-control/rotation rule を適用するか。

**Frontier Rule**  
Kubernetes Secret は confidential data を保持する object だが、default では etcd に unencrypted で保存されるため、encryption at rest、least-privilege RBAC、container-specific access、external secret store 等が必要である。[S31]

**Required Artifacts**  
Secret catalog、owner、rotation interval、RBAC policy、injection method、redaction rule。

**Metrics**  
Secret age、exposure incidents、unused secret count、rotation failure、privileged access count。

**Failure Modes / Anti-patterns**  
Secret を env dump/log/error に出す、namespace 内 pod creation 権限で secret が広く読める、rotation 不能な hard-coded credential。

**Confidence**  
A

### Layer 08.29: Feature Flag / Progressive Delivery

**Definition**  
Runtime behavior を feature flag により変更し、targeting、rollout、kill switch、experiment、deprecation を制御する。

**Decision Question**  
どの feature は deploy と release を分離し、誰がどの条件で flag を評価・変更・削除するか。

**Frontier Rule**  
OpenFeature は vendor-agnostic feature flagging API を提供し、feature flag は runtime に behavior を変える dynamic mechanism である。Specification status では Experimental/Hardening/Stable を分け、production 使用可否の判断材料を与える。[S32][S33]

**Required Artifacts**  
Flag catalog、owner、default、targeting rule、expiry date、rollback rule、audit event。

**Metrics**  
Stale flag count、flag evaluation latency、rollout incident、kill switch activation time、unknown flag evaluation。

**Failure Modes / Anti-patterns**  
Flag の owner/expiry なし、nested flags、secret/config の代替に flag を使う、client-side sensitive targeting leakage。

**Confidence**  
A

### Layer 08.30: Audit Trail / Security Event Logging

**Definition**  
Security・compliance・business accountability のため、actor、action、object、time、location、result、context を改ざん耐性ある形で記録する。

**Decision Question**  
どの business/security events を、どの schema、retention、integrity、access control で記録するか。

**Frontier Rule**  
OWASP は application logging を security events に常に含めるべきとし、application code は user identity、roles、permissions、target、action、outcomes などを最もよく知る primary event source だと説明する。Application logs は each event の when/where/who/what を記録すべきである。[S34]

**Required Artifacts**  
Audit event taxonomy、event schema、retention policy、redaction rule、tamper-detection/storage control、access review。

**Metrics**  
Audit coverage、missing actor、missing object、event delivery lag、log integrity failure、access-to-log events。

**Failure Modes / Anti-patterns**  
Debug log と audit trail の混同、PII/secret の過剰記録、audit log の完全 disable、correlation ID なし、log injection。

**Confidence**  
A

---

## 9. Operating Model

### 9.1 Roles

| Role | 主責務 |
|---|---|
| Backend Lead | layer 08.01–08.26 の設計標準、コードレビュー、transaction/error/retry policy の責任者 |
| API Owner | route/DTO/error contract/versioning/deprecation の責任者 |
| Domain Owner | bounded context、entity、value object、aggregate、invariant の責任者 |
| Application Architect | use case decomposition、application service、dependency direction の責任者 |
| DB Owner | persistence、repository implementation、transaction isolation、lock/concurrency の責任者 |
| SRE / Platform | timeout/retry/circuit breaker、background worker、config/secrets、observability の責任者 |
| Security Lead | validation、exception redaction、secret、audit trail、log protection の責任者 |
| Product Owner | feature flag intent、rollout、kill switch、experiment decision の責任者 |

### 9.2 Review gates

| Gate | Trigger | Required Checks |
|---|---|---|
| API Contract Review | 新 route / DTO / error code | route conflict, schema, validation, auth, error response, audit event |
| Use Case Review | 新 command/query | business intent, domain aggregate, transaction, side effects, tests |
| Domain Model Review | 新 entity/value object/aggregate | identity, invariant, lifecycle, aggregate boundary, domain events |
| Transaction Review | 状態変更・outbox・workflow | isolation, rollback, idempotency, remote call exclusion, lock duration |
| Async Review | job/workflow/saga | payload version, retry, timeout, DLQ, compensation, observability |
| Runtime Control Review | config/secret/feature flag | owner, source, validation, RBAC, expiry, audit |
| Security Logging Review | sensitive use case | event taxonomy, actor/action/object/result, redaction, retention |

### 9.3 Mandatory artifacts per backend use case

```text
use_case/{name}/
  contract.md              # route, request, response, error
  command_or_query.md      # input/result/actor/preconditions
  transaction.md           # boundary/isolation/rollback/outbox
  validation.md            # syntactic/semantic/invariant rules
  resilience.md            # timeout/retry/idempotency/circuit breaker
  audit.md                 # event schema and conditions
  tests.md                 # unit/integration/contract/failure tests
```

---

## 10. Metrics

| Category | Metrics |
|---|---|
| API/Routing | 404/405 rate, route conflict count, deprecated endpoint traffic, route docs coverage |
| Controller/Handler | handler LOC, controller complexity, repository direct calls, business logic leakage |
| Use Case/Application | command latency, success/failure by domain reason, orchestration dependency count |
| Domain Model | invariant violations, invalid transitions, aggregate size, cross-aggregate update count |
| Persistence/Transaction | transaction duration, rollback rate, deadlocks, lock wait, stale update conflicts |
| Validation/Error | validation failure rate, unknown error code, malformed Problem Details, unhandled exception rate |
| Async/Workflow | queue depth, job retry attempts, DLQ depth, workflow stuck count, compensation success |
| Retry/Timeout | retry amplification, retry success, timeout rate, downstream error rate, circuit open count |
| DI/Config/Secret | startup config failures, lifetime mismatch, secret age, secret access violations |
| Feature Flags | stale flag count, rollout incident, flag eval latency, kill switch activation time |
| Audit | missing actor/action/object, event delivery lag, log integrity failures, audit coverage |

---

## 11. Failure Modes and Anti-patterns

| Anti-pattern | 兆候 | 予防策 |
|---|---|---|
| Fat Controller | handler に business branching、repository call、transaction、retry が混在 | Handler responsibility checklist、use case extraction |
| Anemic Domain Model | entity が getter/setter だけ、rules が service に散在 | Entity/aggregate invariant review、domain tests |
| DTO/Entity Coupling | ORM entity を API response として返す | DTO mapper、schema diff、domain leak lint |
| Oversized Transaction | external API call を transaction 内で実行 | outbox、commit-after-side-effect separation、transaction duration alert |
| Retry Storm | transient error 時に fan-out retry が下流を増幅 | max attempts、backoff+jitter、circuit breaker、retry budget |
| Timeout Vacuum | timeout/deadline なし、caller より長い callee timeout | timeout budget、deadline propagation、contract tests |
| Poison Job Loop | 同じ job が無限 retry し queue を詰まらせる | retry cap、DLQ、payload validation、manual replay |
| Non-deterministic Workflow | replay 時に time/random/network が変化 | activity boundary、workflow determinism test |
| Stale Feature Flags | owner/expiry なし flag が恒久化 | flag registry、expiry automation、quarterly cleanup |
| Secret Leakage | config/log/error に secret が出る | secret scanner、redaction、RBAC、external secret store |
| Audit Fog | 何でも log して重要 event が見えない | risk-based event taxonomy、severity、correlation |
| Audit Blind Spot | privileged action に actor/result/object がない | audit coverage tests、security review gate |

---

## 12. Maturity Model

| Level | Name | Criteria |
|---:|---|---|
| 0 | 未整備 | route/controller に business logic が直書きされ、validation/transaction/error/retry/audit が場当たり的 |
| 1 | 個人依存 | 主要 developer は設計意図を理解しているが、artifact と review gate がない |
| 2 | 文書化 | route/DTO/use case/transaction/error/audit の基本テンプレートがある |
| 3 | 標準化 | handler/application/domain/repository/transaction の責務分離がレビューで enforced される |
| 4 | 自動化・計測 | route conflict、schema diff、stale flag、secret leak、audit coverage、retry storm を自動検出 |
| 5 | 自律改善・業界先端 | incident/telemetry/consumer feedback から設計標準が継続更新され、workflow/compensation/feature flag/audit が統合 governance 下にある |

---

## 13. Clone Implementation Guide

### 13.1 最初の 30 日

1. 現行 backend の route inventory、handler inventory、repository direct call、transaction annotation、background job、feature flag、audit event を棚卸しする。
2. 新規 use case から必須 artifact template を適用する。
3. Exception taxonomy と Problem Details schema を定義し、global error handler を作る。
4. Config/Secret/Feature Flag を分離し、owner と expiry を記録する。
5. OWASP logging の when/where/who/what を baseline とした audit event schema を作る。

### 13.2 31–60 日

1. Domain model review を開始し、entity/value object/aggregate/invariant を明文化する。
2. Transaction boundary と outbox/event emission を use case 単位で定義する。
3. Retry/timeout matrix を downstream dependency ごとに作る。
4. Background job payload schema、retry、DLQ、idempotency key を統一する。
5. Route conflict、schema diff、stale flag、secret scanning を CI に入れる。

### 13.3 61–90 日

1. Long-running process を workflow/saga として識別し、compensation と point-of-no-return を設計する。
2. Audit coverage tests を導入し、重要 use case の actor/action/object/result 欠落を検出する。
3. Production telemetry から retry amplification、transaction duration、DLQ depth、stale flags を review cadence に接続する。
4. Architecture decision records を pattern library に変換する。

### 13.4 90 日以降

1. Domain and API governance board を軽量運用する。
2. Incident postmortem から retry/timeout、transaction、workflow、audit standard を改訂する。
3. Product flag lifecycle を release management と接続し、flag deletion を定常運用にする。
4. Service template / code generator に layer conventions を組み込む。

---

## 14. Pattern Library

| Pattern ID | Pattern | Applies To | Description | Preconditions | Tradeoffs | Confidence |
|---|---|---|---|---|---|---|
| P-001 | Thin Handler / Explicit Use Case | 08.04–08.08 | Handler は contract translation、use case は business action orchestration | Route/DTO/error contract がある | Boilerplate 増加 | A |
| P-002 | Aggregate Root as Consistency Gate | 08.09–08.13 | Aggregate root だけが child state を更新し invariant を守る | Domain model が複雑 | Aggregate 設計が難しい | A |
| P-003 | DTO Boundary | 08.06 | Domain entity と API schema を分離する | Mapper/test が必要 | Mapping overhead | A |
| P-004 | Transaction + Outbox | 08.14–08.16, 08.20–08.21 | State change と event/message persistence を同一 local transaction に束ねる | Outbox processor が必要 | Delivery lag | A |
| P-005 | Problem Details Error Contract | 08.18–08.19 | Error を RFC 9457 schema で machine-readable にする | Error code registry が必要 | Legacy client migration | A |
| P-006 | Retry with Timeout + Backoff + Jitter | 08.24–08.25 | Transient fault だけ retry し、deadline と jitter で増幅を抑える | Operation が retry-safe | Latency 増加 | A |
| P-007 | Durable Workflow | 08.22–08.23 | Event history と replay で長期 process を復元可能にする | Deterministic workflow discipline | Platform learning curve | A |
| P-008 | Config/Secret Separation | 08.27–08.28 | Non-secret config と secret を別 object/store に置く | Secret platform/RBAC が必要 | Operational complexity | A |
| P-009 | Feature Flag Lifecycle | 08.29 | Flag は owner/expiry/rollback/audit を持つ runtime policy | Flag registry が必要 | Flag debt 管理 | A |
| P-010 | Audit Event Schema | 08.30 | Actor/action/object/result/time/correlation を標準化 | Event taxonomy が必要 | Storage/compliance burden | A |

---

## 15. Validation Queries for Future Research

以下のクエリを、各候補・各社 docs・各 repo に対して継続的に回す。

```text
"{framework_or_service}" "routing" "breaking change" OR deprecated
"{framework_or_service}" "ProblemDetail" "RFC 9457" error response
"{service}" "transaction" "rollback" "outbox" incident
"{service}" "retry storm" OR "retry amplification" OR "circuit breaker"
"{service}" "background job" "dead letter" "idempotency"
"{service}" "feature flag" stale OR cleanup OR audit
"{service}" "secret" leaked OR exposure OR "environment variable"
site:{official_domain} "validation" "semantic" "syntactic"
site:{official_domain} "compensating transaction" "manual intervention"
site:{official_domain} "audit" "actor" "action" "result"
repo:{org}/{repo} "@Transactional" "external" "HTTP" path:/src
repo:{org}/{repo} "TODO" "remove flag" OR "feature flag"
```

---

## 16. Confidence & Unknowns

### 確度 A

- Routing/controller/validation/error/transaction/DI の基本概念は、ASP.NET Core、Spring Framework、IETF RFC、OWASP、Microsoft/Azure の公式情報で直接裏付けられる。
- DDD tactical patterns、aggregate root、value object、bounded context は Microsoft/Azure の公式 architecture guidance で直接裏付けられる。
- Retry/timeout/circuit breaker/compensation/outbox は AWS/Azure の公式 design guidance で直接裏付けられる。
- Config/Secret/Feature flag/Audit は Twelve-Factor、Kubernetes、OpenFeature/CNCF、OWASP により直接裏付けられる。

### 確度 B

- 08 の 30 レイヤー分割は、ユーザー指定サブテーマからの本レポート内正規化であり、既存社内 taxonomy とは ID 名称が違う可能性がある。
- Rails/Django/FastAPI/Celery/Temporal から抽出した pattern は公式 docs に基づくが、各組織の production practice は環境により差がある。

### Unknowns

- 各トップ企業の非公開 architecture review board、internal style guide、actual exception taxonomy は公開情報だけでは確定できない。
- Feature flag の実際の承認フロー、audit policy、stale flag cleanup automation は企業内運用に依存し、公開 docs だけでは一般化に限界がある。
- Audit retention period、log immutability、legal basis は jurisdiction と業界規制に依存するため、本レポートでは generic clone spec に留める。

---

## 17. Source Catalog

| Source ID | Entity | Source Title | Type/Tier | URL | Used For |
|---|---|---|---|---|---|
| S01 | Microsoft | Routing in ASP.NET Core | official_doc / T0 | https://learn.microsoft.com/en-us/aspnet/core/fundamentals/routing?view=aspnetcore-10.0 | routing, endpoint, middleware |
| S02 | Microsoft | Create web APIs with ASP.NET Core | official_doc / T0 | https://learn.microsoft.com/en-us/aspnet/core/web-api/?view=aspnetcore-10.0 | controller boundary |
| S03 | Spring | Annotated Controllers / Mapping Requests | official_doc / T0 | https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller.html | controller, handler, request mapping |
| S04 | Spring | Spring MVC Validation / RequestBody validation | official_doc / T0 | https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-validation.html | validation, 400 mapping |
| S05 | IETF | RFC 9457 Problem Details for HTTP APIs | standard / T0 | https://www.rfc-editor.org/rfc/rfc9457.html | error response contract |
| S06 | Spring | Error Responses / RFC 9457 ProblemDetail | official_doc / T0 | https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-ann-rest-exceptions.html | exception mapping, error response |
| S07 | OWASP | Input Validation Cheat Sheet | security_guidance / T0 | https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html | syntactic/semantic validation |
| S08 | Django | URL dispatcher | official_doc / T0 | https://docs.djangoproject.com/en/6.0/topics/http/urls/ | URLconf, routing alternative |
| S09 | Microsoft Azure | Microservices Architecture Style | official_doc / T0 | https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/microservices | bounded context, business capability |
| S10 | Microsoft .NET | Implement microservice application layer using Web API | official_doc / T0 | https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/microservice-application-layer-implementation-web-api | application layer, DI |
| S11 | Microsoft .NET | Designing a DDD-oriented microservice | official_doc / T0 | https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/ddd-oriented-microservice | domain model layer, boundaries |
| S12 | Microsoft .NET | Designing a microservice domain model | official_doc / T0 | https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/microservice-domain-model | aggregate root, consistency |
| S13 | Microsoft .NET | Implementing a microservice domain model with .NET | official_doc / T0 | https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/net-core-microservice-domain-model | aggregate/repository/infrastructure |
| S14 | Microsoft .NET | Implementing value objects | official_doc / T0 | https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/implement-value-objects | value object implementation |
| S15 | Microsoft Azure | Use Tactical DDD to Design Microservices | official_doc / T0 | https://learn.microsoft.com/en-us/azure/architecture/microservices/model/tactical-domain-driven-design | entity/value object/domain service |
| S16 | Spring | Transaction Abstraction | official_doc / T0 | https://docs.spring.io/spring-framework/reference/data-access/transaction/strategies.html | transaction manager |
| S17 | Spring | Using @Transactional | official_doc / T0 | https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html | transaction boundary declaration |
| S18 | Microsoft Azure | Transactional Outbox Pattern | official_doc / T0 | https://learn.microsoft.com/en-us/azure/architecture/databases/guide/transactional-out-box-cosmos | reliable messaging, outbox |
| S19 | Microsoft Azure | Compensating Transaction Pattern | official_doc / T0 | https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction | saga, compensation |
| S20 | FastAPI | Background Tasks | official_doc / T0 | https://fastapi.tiangolo.com/tutorial/background-tasks/ | background task boundary |
| S21 | Celery | Tasks | official_doc / T0 | https://docs.celeryq.dev/en/main/userguide/tasks.html | task retry, task identity |
| S22 | Celery | Configuration and defaults | official_doc / T0 | https://docs.celeryq.dev/en/main/userguide/configuration.html | task time limits, ack policy |
| S23 | Temporal | Workflows / Activity Execution | official_doc / T0 | https://docs.temporal.io/workflows | durable workflow, event history |
| S24 | AWS | Timeouts, retries, and backoff with jitter | official_doc / T0 | https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/ | retry/timeout/backoff |
| S25 | Microsoft Azure | Retry Pattern | official_doc / T0 | https://learn.microsoft.com/en-us/azure/architecture/patterns/retry | transient fault retry |
| S26 | Microsoft Azure | Circuit Breaker Pattern | official_doc / T0 | https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker | retry vs circuit breaker |
| S27 | Spring | Dependency Injection | official_doc / T0 | https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html | DI definition |
| S28 | Microsoft | Dependency injection in ASP.NET Core | official_doc / T0 | https://learn.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection?view=aspnetcore-10.0 | DI in web apps |
| S29 | Twelve-Factor App | Config | methodology / T0 | https://12factor.net/config | config in environment |
| S30 | Kubernetes | ConfigMaps | official_doc / T0 | https://kubernetes.io/docs/concepts/configuration/configmap/ | non-secret config |
| S31 | Kubernetes | Secrets | official_doc / T0 | https://kubernetes.io/docs/concepts/configuration/secret/ | secret handling |
| S32 | OpenFeature | Introduction | specification_doc / T0 | https://openfeature.dev/docs/reference/intro/ | feature flags, vendor-neutral API |
| S33 | OpenFeature | Specification | specification_doc / T0 | https://openfeature.dev/specification/ | stability statuses |
| S34 | OWASP | Logging Cheat Sheet | security_guidance / T0 | https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html | audit/security event logging |
| S35 | Rails | Active Record Validations | official_doc / T0 | https://guides.rubyonrails.org/active_record_validations.html | model validations |
| S36 | AWS | Making retries safe with idempotent APIs | official_doc / T0 | https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/ | idempotency and retry side effects |
| S37 | FastAPI | Dependencies | official_doc / T0 | https://fastapi.tiangolo.com/tutorial/dependencies/ | dependency declaration |
| S38 | Martin Fowler | Unit of Work | pattern_catalog / T3 | https://martinfowler.com/eaaCatalog/unitOfWork.html | UoW definition |
| S39 | SQLAlchemy | Session Basics / Unit of Work | official_doc / T0 | https://docs.sqlalchemy.org/en/latest/orm/session_basics.html | ORM session/UoW behavior |

---

## 18. Machine-readable Appendix: Minimal Clone Spec Fields

```yaml
spec_id: app_backend_design_08_01_08_30
version: "2026-05-13"
layer_scope: ["08.01", "08.02", "08.03", "08.04", "08.05", "08.06", "08.07", "08.08", "08.09", "08.10", "08.11", "08.12", "08.13", "08.14", "08.15", "08.16", "08.17", "08.18", "08.19", "08.20", "08.21", "08.22", "08.23", "08.24", "08.25", "08.26", "08.27", "08.28", "08.29", "08.30"]
decision_question: >
  Backend use case を、どの routing/controller/application/domain/transaction/failure/runtime/audit contract で実行可能にするか。
core_philosophy:
  - Contract-first ingress
  - Thin handler, explicit use case
  - Domain model owns invariants
  - Transaction boundary follows consistency boundary
  - Failure semantics is part of the API
  - Async work requires explicit reliability semantics
  - Runtime knobs are controlled artifacts
  - Audit is not generic logging
required_artifacts:
  - route_inventory
  - endpoint_contracts
  - dto_schema
  - use_case_catalog
  - domain_model_catalog
  - aggregate_invariant_catalog
  - transaction_policy
  - exception_taxonomy
  - error_code_registry
  - job_workflow_catalog
  - retry_timeout_matrix
  - di_lifetime_policy
  - config_secret_registry
  - feature_flag_registry
  - audit_event_schema
validation_queries:
  - '"{service}" "retry storm" OR "retry amplification"'
  - '"{service}" "ProblemDetail" "RFC 9457"'
  - '"{service}" "feature flag" stale OR cleanup OR audit'
  - '"{service}" "background job" "dead letter" "idempotency"'
  - '"{service}" "audit" "actor" "action" "result"'
```
