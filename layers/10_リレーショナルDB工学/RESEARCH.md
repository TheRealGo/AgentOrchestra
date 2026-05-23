# Frontier Operating Model Research: リレーショナルDB工学（Layer 10）

Generated: 2026-05-13  
Scope: repository / DAO / ORM / SQL、query plan、transaction / isolation / lock / deadlock、index / constraint / table / view、stored procedure / trigger、partition / sharding / replication、backup / restore、WAL、checkpoint、storage engine  
Method: `RESEARCH.md` の公開情報限定 Frontier Operating Model Research に従い、T0/T2/T3/T4/T5 の公式文書・標準・OSS/製品ドキュメント・論文・公開事故報告を横断して、意思決定モデルと Clone Spec に正規化した。

---

## 0. Executive Summary

リレーショナルDB工学レイヤーの核心は、「アプリケーションの永続化要求を、SQL contract、schema invariant、transaction boundary、query plan、storage/recovery mechanism、replication/failover topology へ分解し、各判断を計測・復旧・変更可能な形で運用すること」である。

先端組織に共通する原理は次の 8 点に集約される。

1. **データ整合性はコードではなく schema と transaction で固定する。** 主キー、外部キー、一意制約、CHECK、NOT NULL、適切な isolation level を「後で検査する仕組み」ではなく「破れない境界」として使う。
2. **Repository / DAO / ORM は SQL を隠す層ではなく、SQL contract を制御する層である。** ORM が生成する SQL、fetch plan、transaction scope、session/DbContext の寿命、raw SQL escape hatch を明示しない設計は、N+1、phantom side effect、lock storm、plan regression の温床になる。
3. **Query plan は production artifact として扱う。** `EXPLAIN` / execution plan / optimizer statistics / plan cache / query shape を、コードレビュー・migration review・性能回帰検知の一部にする。
4. **Transaction は短く、再試行可能で、業務不変条件ごとに設計する。** isolation は「強ければよい」ではなく、anomaly tolerance、deadlock/retry budget、latency、write contention によって選ぶ。
5. **Index / partition / shard は「速くする手段」ではなく「access pattern と運用境界の契約」である。** 書き込み増幅、lock、maintenance、replication lag、restore 単位まで含めて判断する。
6. **Replication は backup ではない。** replication は可用性・read scaling・migration・CDC のための機構であり、誤削除や論理破壊も複製する。PITR、base backup、WAL/binlog/log chain、restore drill が別途必要である。
7. **WAL / redo / transaction log / checkpoint は durability と recovery time を決める制御面である。** `fsync`、synchronous commit、checkpoint frequency、redo capacity、log backup chain を性能チューニングだけで扱うと、復旧不能事故になる。
8. **分散SQL・sharding は「RDBを大きくする」だけではなく、整合性・レイテンシ・キー設計・failover の再設計である。** Spanner / CockroachDB / Vitess / Aurora の公開資料は、scaling の前に topology と failure model を決める必要を示している。

本レイヤーの Clone Spec は、RDB を「DBA の専門領域」として分離せず、アプリケーション設計、SRE、セキュリティ、データモデリング、DR、リリース管理を統合した operating model として実装することを求める。

---

## 1. Layer Registry（10）

| Layer ID | Layer Name | Definition | Decision Question | Primary Artifacts | Owner Roles | Default Metrics |
|---:|---|---|---|---|---|---|
| 10.01 | Repository Pattern | domain/use-case から永続化 contract を切り出す境界 | どの aggregate / use case に対し、どの persistence API を公開し、transaction をどこで閉じるか | repository interface, service transaction map, query method list | application architect, backend lead | query count/request, transaction scope violations |
| 10.02 | DAO | DB vendor / SQL / connection の詳細を encapsulate する層 | どの SQL を DAO に閉じ込め、どこから raw SQL を許可するか | DAO class, SQL template, result mapper | backend lead, DBA | SQL coverage, prepared statement rate |
| 10.03 | ORM / Persistence Mapping | object model と relational model の mapping | entity lifecycle、identity map、fetch plan、change tracking をどう制御するか | entity model, mappings, fetch graph, session policy | backend lead | N+1 count, ORM-generated SQL latency |
| 10.04 | SQL Language / Dialect | 標準 SQL と vendor dialect の使用境界 | 標準 SQL・dialect・extension・stored logic をどう使い分けるか | SQL style guide, dialect matrix | data architect, DBA | dialect exceptions, portability risk |
| 10.05 | SQL Query Design | query shape と parameterization の設計 | どの SQL が安全・説明可能・再利用可能か | query inventory, prepared statement policy | backend lead, security | slow query rate, injection review findings |
| 10.06 | Query Planner / Optimizer | cost/statistics から実行方法を選ぶ機構 | optimizer に何を任せ、何を statistics / hint / schema で制御するか | optimizer config, stats policy | DBA, platform engineer | cardinality error, plan churn |
| 10.07 | Execution Plan / EXPLAIN | query plan を可視化・検証する成果物 | plan をどの時点で取り、どの plan regression を release blocker にするか | EXPLAIN baseline, plan hash, regression report | DBA, backend lead | plan regression count, rows scanned/returned |
| 10.08 | Statistics / Cardinality | planner が使う分布・件数・相関情報 | statistics freshness と extended stats をどう維持するか | analyze schedule, stats catalog | DBA | stale stats age, estimate/actual ratio |
| 10.09 | Transaction Design / ACID | atomicity・consistency・isolation・durability の単位 | 業務 invariant をどの transaction boundary で守るか | transaction map, invariant matrix | domain owner, backend lead | rollback rate, transaction duration |
| 10.10 | Isolation / MVCC | concurrent transaction の可視性制御 | anomaly tolerance と retry budget から isolation をどう選ぶか | isolation policy, anomaly test | backend lead, DBA | serialization failures, retry success |
| 10.11 | Locking / Row Versioning | shared resource への同時アクセス制御 | どの lock を取り、どの順序・粒度・期間に制限するか | lock order guide, blocking runbook | DBA, SRE | lock wait p95, blocked sessions |
| 10.12 | Deadlock / Retry | 循環待ちの検出・解消・再試行 | deadlock をどこで検出し、どの transaction を retry 可能にするか | retry policy, deadlock graph | backend lead, DBA | deadlock count, retry success rate |
| 10.13 | Index Engineering | access pattern を物理構造へ落とす設計 | どの predicate/order/join を index で支え、どの write amplification を受け入れるか | index catalog, index RFC | DBA, backend lead | index hit ratio, write amplification, bloat |
| 10.14 | Constraints / Keys | schema-level invariant | どの invariant を DB が直接拒否すべきか | DDL constraints, key design | data architect | constraint violation rate, orphan rate |
| 10.15 | Table Design | row model、normalization、physical table shape | table boundary、key、columns、ownership をどう決めるか | schema DDL, ERD | data architect, domain owner | table growth, migration frequency |
| 10.16 | View / Materialized View | query abstraction と read model | view を security / abstraction / performance のどの目的で使うか | view definitions, refresh policy | DBA, analytics lead | refresh lag, view query latency |
| 10.17 | Stored Procedure / Function | DB 内 procedural logic | 何を DB 内で atomic に実行し、何を app layer に残すか | procedure catalog, permission model | DBA, backend lead | procedure latency, privilege exceptions |
| 10.18 | Trigger / Rule | DML event による自動処理 | どの side effect を自動化し、どこまで可観測化するか | trigger catalog, audit tests | DBA, security | hidden mutation findings, trigger failures |
| 10.19 | Partitioning | table を管理・scan・retention 単位へ分割 | 何を partition key にし、pruning / maintenance / retention をどう保証するか | partition scheme, retention policy | DBA | partition pruning rate, maintenance time |
| 10.20 | Sharding | database を複数 server / tablet / keyspace へ水平分割 | shard key、reshard、cross-shard transaction をどう扱うか | shard map, reshard runbook | platform lead, DBA | hotspot rate, cross-shard query count |
| 10.21 | Replication | data copies と topology | sync/async、physical/logical、quorum、GTID/LSN をどう選ぶか | replication topology, failover plan | SRE, DBA | replication lag, failover RTO |
| 10.22 | CDC / Logical Decoding / Binlog | data change stream | change stream を移行・analytics・integration にどう使うか | CDC schema, offset policy | data platform lead | lag, duplicate/drop rate |
| 10.23 | Backup Strategy | recoverable copy の取得 | base backup、snapshot、log backup、retention をどう設計するか | backup policy, backup manifest | SRE, DBA | backup age, backup success, retention |
| 10.24 | Restore / PITR / DR Drill | backup から復旧する実行能力 | どこまで戻せるか、誰が何分で戻すか | restore runbook, PITR drill | SRE, DBA | RPO, RTO, restore success rate |
| 10.25 | WAL / Redo / Transaction Log | durability と crash recovery の log | log flush、commit visibility、replay、archiving をどう制御するか | WAL/binlog policy, log chain | DBA, platform engineer | WAL generation, log lag, archive failures |
| 10.26 | Checkpoint / Flush | dirty pages と log replay 範囲の制御 | recovery time と I/O burst をどう均衡させるか | checkpoint config, I/O dashboard | DBA, SRE | checkpoint duration, write stalls |
| 10.27 | Storage Engine / Physical Layout | page、file、buffer、storage engine の物理構造 | engine behavior と storage device を data contract にどう反映するか | storage profile, engine config | platform engineer, DBA | fsync latency, page corruption, buffer hit |
| 10.28 | HA / Failover | primary/replica/quorum の切替 | failure detector、promotion、split-brain 防止をどう設計するか | failover runbook, topology diagram | SRE, DBA | failover time, inconsistency incidents |
| 10.29 | Observability / Capacity Governance | RDB engineering の測定・警戒・改善 | query、lock、WAL、replication、backup、capacity をどの SLO で監視するか | dashboards, alerts, capacity plan | SRE, DBA, backend lead | p99 latency, log growth, lag, capacity headroom |

---

## 2. Frontier Exemplars and Candidate Scoring

Scoring follows `RESEARCH.md`: Performance 25 / Adoption 15 / Artifact Richness 20 / Peer Validation 15 / Recency 10 / Transferability 10 / Failure Evidence 5, normalized to 100.

| Candidate | Why It Is Frontier-Relevant | Score | Strength | Caveat |
|---|---:|---:|---|---|
| PostgreSQL | MVCC、WAL、logical/physical replication、declarative partitioning、extensibility、rich official docs が揃う OSS RDBMS | 90 | artifact richness, transferability | sharding は core だけで完結しない |
| MySQL / InnoDB | web-scale OLTP、InnoDB storage engine、redo log、GTID/binlog replication、PITR の公開実装が豊富 | 84 | adoption, storage-engine specificity | isolation semantics や gap locks は誤用リスクが高い |
| Microsoft SQL Server | query processing、locking/row versioning、transaction log、recovery model、deadlock docs が詳細 | 83 | enterprise operations, recovery model | ecosystem が Microsoft stack に寄る |
| Oracle Database | optimizer、RMAN、redo/undo、concurrency model の成熟度が高い | 80 | enterprise-grade recovery/tuning | 一部情報はライセンス・製品前提が強い |
| SQLite | embedded RDB の frontier。WAL、locking、query planner docs が明確 | 76 | small footprint, transparent internals | single-writer 制約など workload 適性が狭い |
| Google Cloud Spanner | global-scale transactional consistency、synchronous replication、schema hotspot avoidance を公式化 | 89 | distributed SQL exemplar | TrueTime / managed service 前提が強い |
| CockroachDB | quorum replication と SERIALIZABLE-first の distributed SQL design を公開 | 84 | distributed transactions, transferability | retry handling と latency trade-off が大きい |
| Vitess | MySQL sharding、resharding、VReplication、Kubernetes 運用の実践例 | 81 | sharding operations | application-visible restrictions がある |
| Amazon Aurora | storage-layer replication、continuous incremental backup、PITR を managed DB として実装 | 80 | storage/recovery architecture | cloud/provider lock-in が強い |
| Hibernate / Spring Data / Jakarta Persistence | Java の ORM・repository standard と実装が豊富 | 78 | standardization, application-layer persistence | ORM abstraction leakage が避けられない |
| SQLAlchemy | Python における Core/ORM、dialect、Session transaction model が明確 | 76 | explicitness, dialect separation | framework discipline が必要 |
| EF Core | DbContext、change tracking、compiled queries、query caching が公式に整理 | 76 | .NET ecosystem maturity | LINQ translation と DB dialect 境界に注意 |
| jOOQ | database-first / type-safe SQL DSL。ORM より SQL contract に近い | 74 | SQL-centric mapping | Java/JVM and license considerations |

---

## 3. Source Catalog

| Source ID | Entity | Title | Type | Tier | Use | URL |
|---|---|---|---|---|---|---|
| S01 | ISO | ISO/IEC 9075-1:2023 SQL Framework | standard | T0 | SQL conceptual framework and terms | https://www.iso.org/standard/76583.html |
| S02 | Eclipse Foundation | Jakarta Persistence 3.2 | standard/spec | T0 | Java ORM/persistence standard | https://jakarta.ee/specifications/persistence/3.2/ |
| S03 | Eclipse Foundation | Jakarta Data 1.0 | standard/spec | T0 | Repository abstraction and query methods | https://jakarta.ee/specifications/data/1.0/jakarta-data-1.0 |
| S04 | OWASP | SQL Injection Prevention Cheat Sheet | security guidance | T0/T5 | Prepared statements and query parameterization | https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html |
| S05 | PostgreSQL | Concurrency Control / Transaction Isolation | official docs | T2/T3 | MVCC and isolation semantics | https://www.postgresql.org/docs/current/mvcc.html |
| S06 | PostgreSQL | Planner/Optimizer | official docs | T2/T3 | optimizer decision mechanism | https://www.postgresql.org/docs/current/planner-optimizer.html |
| S07 | PostgreSQL | Using EXPLAIN | official docs | T2/T3 | query plan inspection | https://www.postgresql.org/docs/current/using-explain.html |
| S08 | PostgreSQL | SQL Language / Reference | official docs | T2/T3 | DDL, index, view, procedure, trigger commands | https://www.postgresql.org/docs/current/sql.html |
| S09 | PostgreSQL | Table Partitioning | official docs | T2/T3 | partitioning design and caveats | https://www.postgresql.org/docs/current/ddl-partitioning.html |
| S10 | PostgreSQL | Logical Replication / Replication Solutions | official docs | T2/T3 | logical vs physical replication | https://www.postgresql.org/docs/current/logical-replication.html |
| S11 | PostgreSQL | Continuous Archiving and PITR | official docs | T2/T3 | WAL archive and recovery | https://www.postgresql.org/docs/current/continuous-archiving.html |
| S12 | PostgreSQL | WAL, Checkpoint, Storage Layout | official docs | T2/T3 | WAL, checkpoint, file/page layout | https://www.postgresql.org/docs/current/wal-intro.html |
| S13 | MySQL | InnoDB Storage Engine | official docs | T2/T3 | storage engine and ACID model | https://dev.mysql.com/doc/refman/8.4/en/innodb-storage-engine.html |
| S14 | MySQL | InnoDB Transaction Isolation / Deadlocks | official docs | T2/T3 | isolation, locks, deadlock minimization | https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html |
| S15 | MySQL | Redo Log / Checkpoints / PITR / GTID | official docs | T2/T3 | redo, checkpoint, binary log recovery and replication | https://dev.mysql.com/doc/refman/8.4/en/innodb-redo-log.html |
| S16 | Microsoft | SQL Server Query Processing Architecture Guide | official docs | T2/T3 | optimizer, execution plans, plan cache | https://learn.microsoft.com/en-us/sql/relational-databases/query-processing-architecture-guide?view=sql-server-ver17 |
| S17 | Microsoft | SQL Server Locking, Row Versioning, Deadlocks | official docs | T2/T3 | locks, isolation, deadlocks | https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-transaction-locking-and-row-versioning-guide?view=sql-server-ver17 |
| S18 | Microsoft | SQL Server Transaction Log / Recovery / Checkpoints | official docs | T2/T3 | WAL, recovery models, checkpoint, log backup | https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-transaction-log-architecture-and-management-guide?view=sql-server-ver17 |
| S19 | SQLite | WAL / Isolation / Query Planner / Locking | official docs | T2/T3 | embedded RDB concurrency and WAL | https://sqlite.org/wal.html |
| S20 | SQLAlchemy | Session Basics / Dialects / Connections | official docs | T2/T3 | session lifecycle, dialects, transactions | https://docs.sqlalchemy.org/en/latest/orm/session_basics.html |
| S21 | Hibernate | Hibernate ORM User Guide / Short Guide | official docs | T2/T3 | ORM mapping, fetching, query language | https://docs.hibernate.org/orm/7.0/userguide/html_single/ |
| S22 | Microsoft | EF Core Change Tracking / Performance | official docs | T2/T3 | DbContext, query caching, compiled queries | https://learn.microsoft.com/en-us/ef/core/change-tracking/ |
| S23 | Spring | Spring Data JPA Reference | official docs | T2/T3 | repositories, query methods, transactionality | https://docs.spring.io/spring-data/jpa/reference/index.html |
| S24 | jOOQ | jOOQ Manual / Transaction Management | official docs | T2/T3 | type-safe SQL DSL and transactions | https://www.jooq.org/doc/latest/manual/ |
| S25 | Cockroach Labs | CockroachDB Architecture / Transactions | official docs | T2/T3 | quorum replication and serializable transactions | https://www.cockroachlabs.com/docs/stable/architecture/overview |
| S26 | Google Cloud | Spanner Docs / Transactions / Replication / Schema | official docs | T2/T3 | global consistency and schema hotspot avoidance | https://docs.cloud.google.com/spanner/docs |
| S27 | Vitess | Resharding / Sharding Docs | official docs | T2/T3 | MySQL sharding and resharding | https://vitess.io/docs/23.0/user-guides/configuration-advanced/resharding/ |
| S28 | AWS | Amazon Aurora Storage / Backup / Replication | official docs | T2/T3 | storage replication, backups, PITR | https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Managing.Backups.html |
| S29 | Mohan et al. | ARIES Transaction Recovery | paper | T4 | WAL recovery method and checkpoint lineage | https://www.cs.cmu.edu/~15849g/readings/mohan92.pdf |
| S30 | Hellerstein, Stonebraker, Hamilton | Architecture of a Database System | paper | T4 | DBMS architecture, query processor, storage, transaction system | https://db.cs.berkeley.edu/papers/fntdb07-architecture.pdf |
| S31 | Google Research | Spanner: Google's Globally-Distributed Database | paper | T4 | distributed transactions and TrueTime | https://research.google.com/archive/spanner-osdi2012.pdf |
| S32 | Yale | Calvin: Fast Distributed Transactions | paper | T4 | deterministic ordering for distributed transactions | https://cs.yale.edu/homes/thomson/publications/calvin-sigmod12.pdf |
| S33 | GitLab | Postmortem of Database Outage, Jan 31 2017 | incident | T5 | backup/restore failure and data loss | https://about.gitlab.com/blog/postmortem-of-database-outage-of-january-31/ |
| S34 | GitHub | Oct 21 Post-Incident Analysis | incident | T5 | replication/failover inconsistency and recovery | https://github.blog/news-insights/company-news/oct21-post-incident-analysis/ |
| S35 | PostgreSQL Wiki | Fsync Errors | incident/history | T4/T5 | storage/fsync reliability failure mode | https://wiki.postgresql.org/wiki/Fsync_Errors |
| S36 | Dintyala et al. | SQLCheck: Automated Detection and Diagnosis of SQL Anti-Patterns | paper | T4/T5 | SQL anti-pattern taxonomy | https://arxiv.org/abs/2004.10232 |

---

## 4. Evidence Map

| Claim ID | Claim | Field | Confidence | Evidence |
|---|---|---|---|---|
| C01 | SQL is the normative interface contract for relational data structures and operations, but vendor dialects and extensions must be treated as explicit dependencies. | definition / interface | A | S01, S08 |
| C02 | Repository / DAO / ORM is not an excuse to hide persistence behavior; it must expose transaction boundary, generated SQL, fetch plan, and parameterization rules. | rule / control | B | S02, S03, S20, S21, S22, S23, S24 |
| C03 | Prepared statements / parameterized queries are the default control for user input reaching SQL. | security rule | A | S04, S08, S16 |
| C04 | ORM session or DbContext is a unit-of-work/stateful transaction object and must not be shared across concurrent tasks without synchronization. | prohibition | A | S20, S22, S21 |
| C05 | Query optimization is cost/statistics based; stale or misleading statistics can produce plan regressions even when SQL text is unchanged. | decision criterion | A | S06, S07, S16 |
| C06 | Execution plans are reviewable artifacts; high-impact query changes should include before/after plan evidence. | artifact / review | A | S07, S16 |
| C07 | PostgreSQL MVCC maps SQL isolation levels to engine-specific behavior; MySQL InnoDB, SQL Server, and SQLite differ in isolation/locking implementation. | tradeoff | A | S05, S14, S17, S19 |
| C08 | Deadlocks are normal concurrency failure modes and require application-level retry or transaction redesign, not only DBA intervention. | failure mode | A | S14, S17 |
| C09 | Constraints, keys, and indexes encode invariants and access paths; they are not merely documentation or optional optimization. | rule | A | S08, S13, S16 |
| C10 | Partitioning improves pruning, maintenance, and lifecycle control only when partition keys and constraints align with workload. | decision criterion | A | S09, S27, S26 |
| C11 | Sharding and distributed SQL introduce restrictions around key design, cross-shard transactions, latency, and failover semantics. | tradeoff | A | S25, S26, S27, S31, S32 |
| C12 | Replication topology must distinguish physical/logical, synchronous/asynchronous, quorum/leader-follower, and CDC/binlog semantics. | rule | A | S10, S15, S25, S26, S28 |
| C13 | PITR requires a restorable base backup plus continuous log stream/chain; replication alone does not satisfy recovery requirements. | control | A | S11, S15, S18, S28 |
| C14 | WAL/redo/transaction log records must be persisted before corresponding dirty pages are relied on for recovery. | rule | A | S12, S15, S18, S29 |
| C15 | Checkpoints reduce crash recovery work but can create I/O bursts; checkpoint design is a recovery-time and performance tradeoff. | tradeoff | A | S12, S15, S18, S19 |
| C16 | Storage engine and physical layout are part of the data contract because durability depends on file/page/log behavior and storage reliability. | rule | B | S12, S13, S19, S30, S35 |
| C17 | Backup systems can appear successful while restore capability is broken; production backup must be verified through restore drills. | failure mode | A | S33, S11, S15, S18, S28 |
| C18 | Async replication/failover can create stale or divergent state after network partition; failover must be tested with data reconciliation paths. | failure mode | A | S34, S10, S15, S25, S26 |
| C19 | Disabling or weakening durability controls such as fsync or equivalent flush behavior must be limited to explicitly noncritical data. | prohibition | A | S12, S18, S35 |
| C20 | SQL anti-patterns are detectable and should be linted or reviewed as part of CI for high-risk services. | control | B | S36, S07, S16 |

---

## 5. Core Philosophy

### 5.1 Relational engineering is a contract discipline

A relational database is not simply a storage dependency. It is a contract system spanning schema, SQL, constraints, transaction semantics, storage logging, recovery, and operational topology. The frontier pattern is to encode as much correctness as possible in the database contract, while keeping application access explicit and observable.

### 5.2 Abstraction is acceptable only when the generated behavior is observable

Repository, DAO, ORM, and SQL DSL layers are useful when they compress repetitive data access while preserving inspectability. They become harmful when they obscure generated SQL, hide transaction boundaries, silently fetch associations, or make query shape unpredictable.

### 5.3 Query performance is governed through evidence, not taste

A query is not “fast” because it has an index or because it is written in an ORM. It is acceptable when its plan, row estimates, row counts, runtime, I/O, lock footprint, and workload impact are measured under representative data.

### 5.4 Transaction design is application design

Transaction isolation and lock behavior should be designed against business invariants. The relevant question is not “which isolation level is theoretically best?” but “which anomaly must be impossible, which retry is tolerable, and which lock footprint can production support?”

### 5.5 Recovery is a production feature

Backup, WAL/binlog archiving, restore, PITR, and failover drills are not administrative afterthoughts. They are part of product reliability. A backup that has not been restored into a verified environment is an unproven artifact.

---

## 6. Decision Model

### Inputs

- Domain invariants: uniqueness, referential integrity, lifecycle rules, ledger rules, tenant boundaries.
- Workload: OLTP/OLAP split, read/write ratio, hot keys, burst pattern, cardinality, data retention.
- Query inventory: critical SQL, ORM-generated SQL, dynamic queries, reporting queries, bulk jobs.
- Consistency requirements: anomaly tolerance, stale-read tolerance, idempotency, retry feasibility.
- Latency requirements: p95/p99, tail-latency sensitivity, lock wait budget, failover budget.
- Durability and recovery: RPO, RTO, PITR range, backup retention, restore environment.
- Topology: single primary, read replicas, multi-region, distributed SQL, sharded keyspaces.
- Storage constraints: SSD/HDD/cloud volume, fsync behavior, checksum, snapshot semantics.
- Security constraints: injection risk, privilege boundaries, row-level security, audit requirements.
- Framework constraints: ORM capabilities, repository conventions, migration tools, connection pool behavior.

### Decision Object

For every persistent use case, decide the **data contract**: schema objects, SQL contract, persistence abstraction, transaction boundary, isolation/lock behavior, plan baseline, scale topology, recovery procedure, and observability controls.

### Criteria

1. Correctness before latency. Invariants that can be expressed as constraints must not be left only to application code.
2. Explicit SQL contract. Critical paths must expose SQL text or generated SQL and must be parameterized.
3. Measured plan quality. Query changes require plan evidence under representative cardinalities.
4. Bounded transactions. Transactions must be short, retryable where needed, and scoped to business invariants.
5. Engine-aware semantics. Isolation, locking, upsert, sequences, partitioning, triggers, and replication must be interpreted per engine.
6. Recovery evidence. RPO/RTO claims require restore drills and log-chain verification.
7. Operational reversibility. Migrations, index builds, partition changes, resharding, and failover need rollback or reconciliation procedures.
8. Observability by default. Slow query, lock wait, deadlock, WAL/binlog, replication lag, checkpoint, backup, restore, and capacity metrics must be visible.

### Priorities

1. Schema invariants and data safety.
2. Transaction correctness and retry semantics.
3. Query plan and index evidence.
4. Recovery and failover proof.
5. ORM/repository maintainability.
6. Partitioning/sharding/replication scale.
7. Vendor portability.

### Prohibitions

- No unparameterized SQL for user-controlled input.
- No transaction boundary hidden inside low-level DAO unless explicitly documented.
- No production-critical ORM query without generated SQL visibility.
- No long-lived transaction across remote calls, user think time, or unbounded batch loops.
- No assumption that replication protects against deletion, corruption, or bad migrations.
- No backup success claim without restore verification.
- No partition/shard key selected only from schema convenience; it must match access and growth patterns.
- No trigger/procedure side effect without tests, documentation, and audit visibility.
- No durability weakening (`fsync`-like controls, async commit, unsafe storage) without written risk acceptance.

### Owners and Reviewers

| Area | Owner | Reviewer |
|---|---|---|
| Repository / DAO / ORM | Backend lead | DBA, security for sensitive data |
| SQL query design | Backend engineer | DBA or performance reviewer |
| Schema / constraint / index | Data architect or DBA | Domain owner, backend lead |
| Transaction / isolation | Backend lead | DBA, SRE for retry and contention |
| Partition / sharding | DB platform lead | SRE, data architect, product owner |
| Replication / CDC | SRE / DBA | Data platform lead, security |
| Backup / restore / DR | SRE / DBA | Engineering management, security/compliance |
| WAL / checkpoint / storage engine | DBA / platform engineer | SRE, infra storage owner |

### Cadence

- Query plan review: every critical query change and every schema/index migration.
- Slow-query review: weekly for high-traffic systems; monthly for lower-tier systems.
- Statistics/index health review: weekly or automated.
- Lock/deadlock review: after every incident and monthly trend review.
- Backup integrity check: daily backup status; at least monthly restore verification for critical systems.
- DR drill: quarterly for business-critical systems; semiannual for lower-tier systems.
- Failover drill: quarterly for HA systems; after topology changes.
- Schema governance review: every release train or migration batch.

---

## 7. Operating Model

### 7.1 Required Artifacts

| Artifact | Purpose | Minimum Contents |
|---|---|---|
| Data Contract Register | persistent use cases and DB contracts | aggregate, table/view/procedure, transaction boundary, isolation, critical queries |
| Query Inventory | critical SQL and ORM-generated SQL | SQL shape, caller, expected rows, index dependency, plan baseline |
| Schema RFC | migration decision record | DDL, rollback, lock impact, data backfill plan, constraint validation plan |
| Index RFC | index justification | target query, plan before/after, write cost, storage cost, removal plan |
| Transaction Map | business invariant to transaction boundary mapping | use case, isolation, retry, lock order, timeout |
| Replication Topology Diagram | data-copy behavior | primary/replica, sync/async, GTID/LSN/offset, failover path |
| Backup Manifest | recoverability evidence | backup schedule, retention, encryption, log archive, restore test result |
| WAL/Log Chain Register | log continuity | archive status, replication slot/binlog status, lag, retention |
| Deadlock/Blocking Runbook | concurrency incident handling | diagnostics, kill/retry rules, owner, rollback path |
| DR Runbook | disaster recovery | restore order, PITR procedure, verification SQL, communication path |

### 7.2 Governance Process

1. **Design intake**: new feature declares data invariants, workload, consistency, and recovery requirements.
2. **Persistence design**: choose repository/DAO/ORM/raw SQL/SQL DSL boundary. Define transaction owner.
3. **Schema design**: produce DDL, constraints, indexes, partitions, views/procedures/triggers if needed.
4. **Plan review**: run EXPLAIN/execution plan under representative data; record plan baseline.
5. **Migration review**: evaluate lock duration, rollback, backfill, validation, and deploy sequencing.
6. **Runtime instrumentation**: add slow-query logging, query tags where supported, ORM SQL logging for pre-prod, lock/deadlock alerts.
7. **Recovery wiring**: confirm backup, WAL/binlog/archive, PITR path, restore verification.
8. **Release gate**: block release when critical query plan, lock impact, or recovery path is unknown.
9. **Post-release observation**: compare actual plan/runtime/lock metrics against baseline.
10. **Continuous improvement**: remove unused indexes, prune partitions, adjust statistics, refine retry logic.

### 7.3 Review Boards

- **Persistence Review**: repository/DAO/ORM/raw SQL boundaries, query shape, transaction ownership.
- **Schema Review**: table/constraint/index/view/procedure/trigger design, migration strategy.
- **Reliability Review**: replication, backup, restore, PITR, failover, WAL/checkpoint and storage settings.
- **Incident Review**: deadlocks, long blocking, failed backup, failed restore, replication divergence, query-plan regression.

---

## 8. Technical Specification

### 8.1 Repository / DAO / ORM / SQL

**Rule RDB-APP-001: Repository is an application-facing contract, not the transaction owner by default.**  
Repositories should express domain or aggregate access patterns. Service/use-case layer should normally own transaction demarcation unless a framework convention explicitly provides safe defaults.

**Rule RDB-APP-002: DAO owns vendor-specific SQL, but not hidden business invariants.**  
DAO may encapsulate SQL templates, connection API, result mapping, stored procedure calls, or vendor hints. Business invariants must still be visible through service contracts and schema constraints.

**Rule RDB-APP-003: ORM-generated SQL is production evidence.**  
For critical paths, record generated SQL, parameterization, expected cardinality, fetch graph, and plan. ORM usage is not accepted until SQL behavior is visible.

**Rule RDB-APP-004: Session / DbContext / Unit-of-Work lifecycle is bounded.**  
Session-like objects are scoped to one request, command, job item, or transaction. They must not be shared across concurrent threads/tasks unless framework documentation explicitly allows the pattern.

**Rule RDB-APP-005: Escape hatch to raw SQL is mandatory.**  
When ORM translation produces poor SQL, unsupported dialect features, or complex analytical operations, raw SQL or a SQL DSL such as jOOQ should be permitted under review.

**Rule RDB-APP-006: Dynamic queries must remain parameterized.**  
Dynamic filters, sorting, pagination, and search conditions must use parameter binding for values and allow-listed identifiers for column/table names.

**Repository/ORM review checklist**

- Does the repository method map to a stable use case or aggregate?
- Is transaction scope above the repository, inside the repository, or managed by framework default?
- Does the method issue one query, N queries, or lazy follow-up queries?
- Is fetch behavior explicit for associations?
- Does generated SQL have parameter binding?
- Is pagination deterministic and indexed?
- Is there a raw SQL alternative for the hot path?
- Is connection/session lifecycle safe for concurrency?

### 8.2 SQL Query Plan Governance

**Rule RDB-PLAN-001: Treat plans as release artifacts.**  
Critical SQL changes include SQL text, bind parameter shape, plan output, expected rows, actual rows, and index dependencies.

**Rule RDB-PLAN-002: Optimizer statistics are part of application correctness.**  
Outdated statistics can break latency SLOs and trigger lock/backlog incidents. Production migrations that drastically change cardinality require statistics refresh or analyzer scheduling.

**Rule RDB-PLAN-003: Plan hints are last-resort controls.**  
Prefer schema, statistics, query rewrite, and index design. Hints or forced plans must carry expiry criteria.

**Rule RDB-PLAN-004: Plan changes are not automatically regressions.**  
A plan regression is one that violates runtime, I/O, lock, memory, or capacity thresholds under representative load.

**Plan evidence fields**

- SQL fingerprint / normalized query
- bind parameter categories
- plan shape / plan hash
- estimated vs actual row count
- index/table access methods
- join order and join type
- sort/hash/temp usage
- memory grant or spill indicators where supported
- runtime p50/p95/p99
- rows scanned vs rows returned
- lock/wait profile

### 8.3 Transactions, Isolation, Locks, Deadlocks

**Rule RDB-TXN-001: Transaction boundary follows business invariant.**  
A transaction should encompass exactly the reads/writes needed to make an invariant true or reject the operation. Avoid transaction-per-DAO-call and avoid one giant transaction around an entire workflow.

**Rule RDB-TXN-002: Isolation level is an explicit product decision.**  
Read committed, repeatable read, snapshot, serializable, and engine-specific variants must be chosen by anomaly risk and retry feasibility. Do not assume the same isolation name behaves identically across engines.

**Rule RDB-TXN-003: Deadlock handling is normal-path engineering.**  
Deadlock victims and serialization failures must be retried only for idempotent or reconstructible commands. Retry count, backoff, and user-visible effect must be designed.

**Rule RDB-TXN-004: Lock order is a contract.**  
When multiple tables/rows are updated, define a consistent order. Cross-service lock ordering should be documented for high-contention workflows.

**Rule RDB-TXN-005: Long transactions are incidents waiting to happen.**  
No transaction should span user interaction, network calls to unreliable external systems, unbounded loops, or human approval.

**Concurrency design matrix**

| Workload | Default Design | Escalation |
|---|---|---|
| Simple CRUD | read committed / default engine semantics, short transaction | add optimistic locking or constraints if lost update risk exists |
| Ledger / money movement | strict invariant transaction, idempotency key, unique constraints | serializable or explicit locks, retry and audit |
| Inventory / limited resource | conditional update, unique/partial constraints, lock ordering | serializable or `SELECT FOR UPDATE` equivalent |
| Bulk maintenance | batch chunks, low lock timeout, off-peak scheduling | partition swap/detach, online index build where available |
| Multi-tenant isolation | tenant key in constraints/indexes, RLS where used | separate schema/database for high-risk tenants |
| Cross-shard write | avoid by design | distributed transaction only when platform supports and retry is safe |

### 8.4 Index, Constraint, Table, View

**Rule RDB-SCHEMA-001: Constraints own invariants.**  
Primary key, foreign key, unique, CHECK, NOT NULL, exclusion constraints, and generated identity rules should enforce what must never be wrong.

**Rule RDB-SCHEMA-002: Every index must name its query and lifecycle.**  
Index creation requires target queries, expected plan change, write/storage cost, and removal condition.

**Rule RDB-SCHEMA-003: Views are contracts.**  
Use views for stable read APIs, security abstraction, or read model simplification. Use materialized views only with explicit refresh and staleness rules.

**Rule RDB-SCHEMA-004: Partitioning is not a substitute for indexing.**  
Partitioning is justified by pruning, retention, maintenance, bulk load/delete, tenant/time isolation, or storage management. It does not automatically improve arbitrary queries.

**Index RFC minimum template**

```text
Index name:
Target query fingerprints:
Predicate / join / order supported:
Before plan:
After plan:
Estimated write overhead:
Estimated storage overhead:
Backfill/build strategy:
Lock impact:
Rollback/drop plan:
Review date:
```

### 8.5 Stored Procedure and Trigger

**Rule RDB-PROC-001: Stored procedures are allowed for atomic data-local operations.**  
Use them when DB-side atomicity, permission boundary, batch efficiency, or data-local logic is stronger than application-layer implementation.

**Rule RDB-PROC-002: Triggers require higher governance than procedures.**  
Triggers can hide writes and complicate debugging. Each trigger must have purpose, affected tables, side effects, failure behavior, ordering, and audit visibility.

**Rule RDB-PROC-003: Stored logic must be versioned with application migrations.**  
Procedure/function/trigger definitions are release artifacts and must be included in drift detection.

**Good uses**

- Audit row maintenance where the trigger behavior is simple and observable.
- Enforcing data-local invariant that cannot be expressed as a simple constraint.
- Bulk data transformations under one transaction.
- Permission boundary where direct table access is intentionally denied.

**Bad uses**

- Hidden business workflow spanning multiple domains.
- Sending external requests from DB logic.
- Mutating unrelated tables without documented side effects.
- Using triggers to compensate for missing application transaction design.

### 8.6 Partition, Sharding, Replication, CDC

**Rule RDB-SCALE-001: Partition before shard when the problem is maintenance/pruning.**  
Partitioning is appropriate for time-series retention, large-table maintenance, tenant isolation inside one engine, or pruning. Sharding is appropriate only when one database cannot meet capacity, locality, or fault-isolation requirements.

**Rule RDB-SCALE-002: Shard key is a product-level decision.**  
Shard key influences locality, hotspots, cross-shard joins, resharding cost, and tenant movement. It must not be chosen solely from an existing primary key.

**Rule RDB-SCALE-003: Replication mode must state loss and consistency semantics.**  
Document whether replication is synchronous, asynchronous, quorum-based, physical, logical, binlog/GTID-based, or CDC stream. “Replica exists” is not a sufficient design.

**Rule RDB-SCALE-004: CDC is an integration log, not a transaction substitute.**  
CDC consumers must handle duplicates, reordering, schema evolution, lag, offset loss, and backfill.

**Topology decision matrix**

| Requirement | Prefer | Avoid |
|---|---|---|
| Read scaling with tolerated staleness | read replicas | sync replication if latency sensitive |
| Zero or near-zero data loss | synchronous/quorum commit where feasible | async replica promotion without reconciliation |
| Online migration | logical replication / CDC / dual-write with reconciliation | one-shot dump for high-change tables |
| Time-based retention | partitioning by time | deleting millions of rows from one unpartitioned table |
| Tenant mobility | tenant-key partition/shard | random or monotonically hot shard keys |
| Global consistency | distributed SQL with explicit consistency model | ad-hoc multi-region async writes |

### 8.7 Backup, Restore, PITR, DR

**Rule RDB-REC-001: Backup is not complete until restore is proven.**  
Every critical database must have documented and tested restore steps, not just successful backup jobs.

**Rule RDB-REC-002: PITR requires log continuity.**  
PostgreSQL WAL archives, MySQL binary logs, SQL Server log chains, and equivalent logs must be retained and monitored so that a restore can advance from a base backup to the desired point.

**Rule RDB-REC-003: Replication and snapshots do not replace logical recovery.**  
Replication can replicate bad writes. Snapshots can preserve corrupted or already-deleted state. PITR and tested restores are separate requirements.

**Rule RDB-REC-004: Recovery runbook includes verification SQL.**  
A restore is not complete until checks validate schema version, row counts, critical invariants, application smoke tests, and data freshness.

**Backup/restore minimum controls**

- Daily backup job status and alerting.
- Log archive/binlog/log-chain continuity alerting.
- Encryption and access control for backup media.
- Restore test into isolated environment.
- PITR exercise using a randomly selected timestamp.
- Backup retention matched to compliance and product requirements.
- Runbook with named owners and escalation path.

### 8.8 WAL, Checkpoint, Storage Engine

**Rule RDB-LOG-001: WAL/redo/transaction log settings are reliability settings first.**  
Performance changes to log flush, fsync, synchronous commit, redo capacity, or checkpoint policy require explicit recovery-risk review.

**Rule RDB-LOG-002: Checkpoint tuning is a recovery-time vs I/O tradeoff.**  
Frequent checkpoints can increase I/O pressure; infrequent checkpoints increase replay work and recovery time. Tune with workload and restore objectives.

**Rule RDB-LOG-003: Storage behavior is part of the DB contract.**  
Disk cache, cloud volume semantics, filesystem, fsync behavior, checksum options, and snapshot consistency affect whether the DB can actually honor durability.

**Rule RDB-LOG-004: WAL/binlog/redo growth is a production risk signal.**  
Unexpected log growth can indicate long transactions, replication lag, stalled archiving, bulk writes, or checkpoint pressure.

---

## 9. Metrics

| Category | Metric | Purpose | Example Alert Condition |
|---|---|---|---|
| Query latency | p50/p95/p99 per query fingerprint | user-facing latency and plan regression | p99 exceeds SLO for 3 windows |
| Query shape | rows scanned / rows returned | full-scan and index selectivity signal | ratio exceeds threshold for critical query |
| Plan quality | plan hash change / estimate-to-actual ratio | optimizer/statistics drift | high cardinality error after migration |
| ORM behavior | SQL statements per request | N+1 detection | request query count jumps after release |
| Connection pool | active, idle, wait time | saturation and transaction leakage | pool wait p95 above budget |
| Transaction | duration, rollback rate, serialization failures | transaction health | long transactions exceed budget |
| Locking | lock wait p95, blocked sessions, lock escalation | contention | blocked critical table beyond threshold |
| Deadlocks | count, victim query, retry success | concurrency failure | deadlocks exceed baseline |
| Index | index usage, bloat, write cost | maintainability and performance | unused large index persists after review |
| Partition | pruning rate, partition count, maintenance time | partition effectiveness | pruning not applied to critical queries |
| Replication | LSN/binlog/offset lag, apply lag | data freshness and failover risk | lag exceeds RPO budget |
| WAL/binlog | generation rate, archive lag, slot retained bytes | recovery/log health | archive delay or unbounded retained log |
| Checkpoint | duration, sync time, write stalls | I/O burst and recovery tuning | checkpoint duration spikes under load |
| Backup | backup age, success, size, retention | recoverability | last good backup older than policy |
| Restore | restore duration, verification pass/fail | RTO proof | restore drill fails or exceeds RTO |
| Capacity | table/index growth, disk free, hot shard/table | scaling | projected exhaustion before next review |
| Security | unparameterized query findings, privilege exceptions | injection and least privilege | dynamic SQL without parameterization |

---

## 10. Failure Modes

| Failure Mode | Mechanism | Early Signal | Prevention / Control | Evidence |
|---|---|---|---|---|
| ORM N+1 explosion | lazy association access issues many follow-up SQL calls | query count/request spikes | fetch graph, join fetch, batch fetch, SQL logging | S21, S20, S22 |
| Hidden transaction boundary | repository/DAO opens commits unpredictably | partial updates, inconsistent retry behavior | use-case-owned transaction map | S23, S20 |
| SQL injection | untrusted input concatenated into SQL | security review findings, unusual query text | prepared statements, allow-listed identifiers | S04 |
| Plan regression | statistics/cardinality drift changes execution plan | p99 increase, row estimate mismatch | EXPLAIN baselines, stats refresh, plan monitoring | S06, S07, S16 |
| Hot index/table contention | too many writers target same key/range | lock wait, deadlocks, CPU low + waits high | key redesign, batching, partitioning, conditional updates | S14, S17, S26 |
| Deadlock storm | inconsistent lock order or large transactions | deadlock graph repeats | lock order, shorter transactions, retry | S14, S17 |
| Replication lag surprise | async replica falls behind | stale reads, failover data gap | lag alerting, read-after-write routing, sync/quorum when required | S10, S15, S25, S26 |
| Split-brain / divergent failover | partition/failover promotes stale side | inconsistent data, manual reconciliation | consensus/quorum, fencing, reconciliation plan | S34, S25, S26 |
| Backup silently unusable | backup job not monitored or restore not tested | no recent restore proof | restore drills, backup validation, owner alerts | S33 |
| PITR gap | missing WAL/binlog/log chain segment | restore cannot reach target time | log archiving monitor, retention, replica slot/binlog governance | S11, S15, S18 |
| Checkpoint I/O stall | dirty pages flushed in bursts | write latency spikes | tune checkpoint, I/O capacity, observe WAL/checkpoint metrics | S12, S15, S18, S19 |
| Storage durability lie | fsync/storage failure loses acknowledged data | corruption, inconsistent pages | reliable storage, checksums, fsync policy, fail-safe hardware/cloud config | S12, S35 |
| Trigger side-effect confusion | invisible automatic writes | unexplained data mutation | trigger catalog, tests, audit logs | S08 |
| Shard hotspot | key distribution sends writes to one shard | skewed CPU/latency, queueing | shard key review, hash/prefix design, reshard plan | S26, S27 |
| Migration locks production | DDL blocks writes/reads | blocked sessions during deploy | online DDL where available, lock timeout, staged migration | S08, S14, S17 |

---

## 11. Anti-patterns

1. **“ORMだからSQLを見なくてよい”**: generated SQL、fetch plan、query count を見ない。
2. **Transaction per DAO method**: use-case invariant を複数 transaction に分断する。
3. **Business invariant only in application code**: DB constraint で拒否できる不整合を application validation だけに置く。
4. **Index by intuition**: target query と before/after plan のない index を作る。
5. **Partitioning as magic performance fix**: pruning 条件と retention/maintenance 目的がない partitioning。
6. **Replication as backup**: replica があれば誤削除や論理破壊から回復できると考える。
7. **Untested PITR**: WAL/binlog/log backup はあるが復旧演習がない。
8. **Async failover without reconciliation**: asynchronous replica を昇格してもデータ差分検証しない。
9. **Disabling durability for speed**: fsync/synchronous commit/log flush を安全性評価なしに弱める。
10. **Long transaction around external calls**: DB lock を保持したまま API call やユーザー待ちを行う。
11. **Trigger as invisible workflow engine**: trigger が別ドメインの業務処理を暗黙に実行する。
12. **Monotonic hotspot key for distributed storage**: auto-increment や時刻順 key を分散環境で無警戒に使う。
13. **No query fingerprinting**: slow query を text variant 単位でしか見ず、同一 query shape を追跡できない。
14. **No schema drift detection**: DB production state と migration repo の差を検出しない。
15. **No restore verification SQL**: restore は終わったが、アプリ整合性を検査していない。

---

## 12. Maturity Model

| Level | Name | Criteria |
|---:|---|---|
| 0 | 未整備 | SQL、schema、transaction、backup が個人判断。restore 手順なし。ORM-generated SQL が不可視。 |
| 1 | 個人依存 | 熟練者が query/index/backup を手作業で管理。事故対応は可能だが再現性が低い。 |
| 2 | 文書化 | schema migration、repository conventions、backup policy、主要 query の plan が文書化されている。 |
| 3 | 標準化 | SQL style、transaction map、index RFC、migration review、restore drill、deadlock runbook が標準運用。 |
| 4 | 自動化・計測 | query fingerprint、plan regression、N+1、lock/deadlock、WAL/binlog、backup/restore が自動監視される。CI で SQL lint / migration dry-run。 |
| 5 | 自律改善・業界先端 | workload 変化に応じて index/statistics/partition/capacity を継続最適化。failover/restore を定期演習。distributed topology と recovery objectives が product SLO と統合。 |

---

## 13. Clone Implementation Guide

### Phase 1: 0–30 days — 現状可視化

Deliverables:

- Database inventory: engine/version/topology/schema count/table sizes.
- Critical query inventory: top 20 latency/cost/traffic queries.
- ORM/repository inventory: critical repository methods and generated SQL visibility.
- Backup manifest: backup schedule, latest successful backup, log archive/binlog/log-chain status.
- RPO/RTO register: service-by-service recovery requirement.
- Current incident signals: slow queries, lock waits, deadlocks, replication lag, backup failures.

Actions:

1. Turn on safe slow-query/query fingerprint collection.
2. Record EXPLAIN/execution plans for top critical queries.
3. Map top business invariants to DB constraints and transaction boundaries.
4. Verify last backup by restoring at least one representative database into isolated environment.
5. Create deadlock/blocking runbook.
6. Identify unparameterized SQL and dynamic SQL risks.

Exit criteria:

- Critical data paths have owner, query, transaction, and recovery visibility.
- At least one restore test has succeeded or failed with documented remediation.

### Phase 2: 31–90 days — 標準化

Deliverables:

- Repository/DAO/ORM standard.
- SQL style and parameterization standard.
- Schema RFC and index RFC templates.
- Transaction isolation and retry policy.
- Migration review process.
- Backup/PITR/DR runbooks with verification SQL.
- WAL/binlog/log chain and replication lag dashboards.

Actions:

1. Require plan evidence for every critical query or index migration.
2. Add CI checks for migration syntax, destructive DDL warnings, and SQL anti-patterns.
3. Add N+1 detection or query-count guardrails for hot request paths.
4. Add lock timeout and statement timeout policy where applicable.
5. Define failover and replica-read rules.
6. Review and remove clearly unused/redundant indexes after safe observation window.

Exit criteria:

- New DB changes pass schema/query/transaction/recovery review.
- Backup and restore paths are repeatable by someone other than the original author.

### Phase 3: 91–180 days — 自動化・SLO統合

Deliverables:

- Query plan regression dashboard.
- Automated restore drill schedule.
- Replication/failover rehearsal process.
- Capacity forecast for table/index/log growth.
- Partition/sharding readiness assessment.
- Incident pattern library.

Actions:

1. Automate query fingerprint regression detection by release.
2. Run PITR drill to a random timestamp within retention window.
3. Simulate replica lag and failover conditions in staging.
4. Build capacity forecast: table/index/WAL/binlog/backup storage.
5. Define shard/partition key criteria before any scale migration.
6. Review stored procedure/trigger catalog for hidden side effects.

Exit criteria:

- Recovery objectives are backed by measured restore/failover data.
- Query, transaction, and storage reliability signals are part of service SLO review.

### Phase 4: 181–365 days — Frontier化

Deliverables:

- Self-service persistence design playbook.
- Automated SQL lint + EXPLAIN CI for supported engines.
- Online schema migration platform or standard tooling.
- Periodic chaos/failover exercise.
- Sharding/distributed SQL decision framework.
- Continuous index/statistics/partition optimization process.

Actions:

1. Integrate query plans into code review bots for high-risk paths.
2. Automate backup restore verification and report pass/fail to reliability review.
3. Implement data reconciliation tooling for failover and CDC.
4. Standardize tenant/key design for scale-out.
5. Build a DB change risk score combining DDL lock risk, data volume, query criticality, and recovery impact.

Exit criteria:

- DB engineering decisions are reproducible, evidence-backed, and audited.
- The organization can explain and test its data correctness, performance, and recovery model under failure.

---

## 14. Validation Queries

Use these queries to reproduce or challenge the findings.

```text
site:postgresql.org/docs/current "Write-Ahead Logging" checkpoint recovery
site:postgresql.org/docs/current "EXPLAIN" "query plan" statistics
site:postgresql.org/docs/current "Transaction Isolation" MVCC
site:dev.mysql.com/doc/refman/8.4/en "InnoDB" "deadlock" "transaction isolation"
site:dev.mysql.com/doc/refman/8.4/en "redo log" "checkpoint" "point-in-time recovery"
site:learn.microsoft.com/en-us/sql "transaction log" "checkpoint" "recovery model"
site:learn.microsoft.com/en-us/sql "deadlock" "row versioning" "isolation level"
site:sqlite.org "WAL" "checkpoint" "isolation"
site:docs.sqlalchemy.org "Session" "transaction" "not safe" concurrent
site:learn.microsoft.com/en-us/ef/core "DbContext" "change tracking" "compiled queries"
site:docs.hibernate.org/orm "fetch" "round trips" "transaction"
site:docs.spring.io/spring-data/jpa "Transactionality" "Repository"
site:vitess.io/docs "resharding" "sharding" restrictions
site:docs.cloud.google.com/spanner "transactions" "replication" "hotspots"
site:cockroachlabs.com/docs "SERIALIZABLE" "transaction retries"
site:docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide "backup" "replication" "cluster volume"
"GitLab" "database outage" "backup" "restore" postmortem
"GitHub" "post-incident analysis" "database" "replication" failover
"PostgreSQL" "Fsync Errors" fsyncgate
"SQL anti-patterns" "SQLCheck" database applications
```

---

## 15. Pattern Library

| Pattern ID | Pattern | Type | Preconditions | Tradeoffs | Evidence | Confidence |
|---|---|---|---|---|---|---|
| P01 | Use-case-owned transaction boundary | decision rule | service layer can coordinate repositories | requires clear service ownership | S20, S23 | B |
| P02 | Query plan as code-review artifact | operating model | critical query inventory exists | slows reviews but prevents regressions | S07, S16 | A |
| P03 | Constraint-first invariants | principle | invariant expressible in schema | complex constraints may need migration care | S08, S13 | A |
| P04 | Explicit fetch graph for ORM hot paths | control | ORM used in latency-sensitive path | more query-specific code | S21, S22, S20 | B |
| P05 | Idempotent transaction retry | operating model | command can be reconstructed or deduped | needs idempotency key / unique constraint | S14, S17, S25 | A |
| P06 | Base backup + log-chain PITR | control | engine supports WAL/binlog/log backup | storage and retention cost | S11, S15, S18 | A |
| P07 | Restore drill as compliance gate | control | backup exists | consumes staging capacity/time | S33, S28 | A |
| P08 | Partition for retention and pruning | decision rule | workload filters by partition key | wrong key hurts queries/maintenance | S09, S27 | A |
| P09 | Shard key risk review | decision rule | scale-out beyond one DB | cross-shard queries and resharding complexity | S26, S27, S31 | A |
| P10 | WAL/checkpoint observability | metric pattern | access to engine metrics | requires platform expertise | S12, S15, S18, S19 | A |
| P11 | Replication lag budget by use case | control | replicas used for reads/failover | staleness routing complexity | S10, S15, S25, S26, S34 | A |
| P12 | Trigger catalog and side-effect tests | control | triggers/stored logic in use | additional testing and documentation | S08 | B |
| P13 | SQL parameterization default | security control | application constructs SQL | dynamic identifiers still need allow-list | S04 | A |
| P14 | Storage reliability review | failure pattern | self-managed storage or risky cloud volume changes | infra/DB cross-team ownership | S12, S35 | B |

---

## 16. Confidence & Unknowns

### Confidence A

- SQL standard and persistence standards exist and are directly relevant to SQL/ORM/repository design: S01–S03.
- PostgreSQL/MySQL/SQL Server/SQLite official docs directly support the claims about WAL/redo/logs, transaction isolation, locks, deadlocks, checkpoints, replication, backup/PITR: S05–S19.
- Backup/restore and replication failure patterns are directly supported by public incident reports: S33–S34.
- Distributed SQL/sharding/replication tradeoffs are directly supported by product docs and papers: S25–S32.

### Confidence B

- Exact “frontier” ranking among PostgreSQL, MySQL, SQL Server, Spanner, CockroachDB, Vitess, and Aurora is a research synthesis from adoption, documentation density, and transferability. It is not a market-share ranking.
- Operating cadence recommendations such as weekly slow-query review and quarterly DR drills are synthesized from reliability practice, not directly mandated by one cited source.
- Repository/DAO/ORM operating rules are synthesized from standards and framework docs; exact implementation differs by language and framework.

### Confidence C

- Suggested phase durations assume a medium-size engineering organization. Smaller teams can compress them; regulated enterprises may need longer cycles.
- Some metrics thresholds require workload-specific calibration and should not be copied literally.

### Unknowns / Additional Research

- Exact layer names for 10 were inferred from the provided subtheme list. If a canonical layer registry has different names, update the layer registry table.
- Vendor-specific online DDL behavior, lock levels, and replication semantics should be researched per target engine/version before implementation.
- Managed-service details such as Aurora, Cloud SQL, AlloyDB, Azure SQL, or RDS differ by edition/region; production design should verify the current service documentation.
- Security and compliance requirements such as encryption, audit, data residency, and retention need a separate governance layer.
- Cost model for storage, I/O, backup retention, cross-region replication, and data transfer should be added for cloud production environments.

---

## 17. Minimal Clone Spec

### Definition

Layer 10 controls how relational persistence is specified, queried, optimized, transacted, constrained, scaled, replicated, recovered, and observed.

### Decision Question

World-class teams decide, for each persistent use case: what SQL/schema contract should exist, how application abstraction maps to it, which transaction/isolation/lock behavior protects invariants, which plan/index/partition/shard/replication topology supports workload, and how WAL/log/checkpoint/backup/restore prove recoverability.

### Frontier Candidates

PostgreSQL, MySQL/InnoDB, SQL Server, Oracle Database, SQLite, Spanner, CockroachDB, Vitess, Aurora, Hibernate/Jakarta Persistence/Spring Data, SQLAlchemy, EF Core, jOOQ.

### Core Philosophy

Relational DB engineering is a correctness-and-recovery discipline first, and a performance discipline second. Performance work is valid only when it preserves explicit data contracts and remains recoverable under failure.

### Decision Model

- Inputs: domain invariant, workload, query inventory, consistency target, RPO/RTO, topology, storage, security, framework constraints.
- Criteria: correctness, explicit SQL, measured plan, short transactions, engine semantics, restore evidence, observability.
- Priorities: constraints → transaction → plan → recovery → abstraction → scale.
- Prohibitions: unparameterized SQL, hidden transaction boundaries, unobserved ORM SQL, long transactions, replication-as-backup, untested restore, unsafe durability weakening.
- Owners: backend lead, DBA, SRE, data architect, security, domain owner.
- Cadence: plan review per critical change; slow-query review weekly/monthly; restore/failover drills quarterly for critical systems.

### Technical / Business Specification

1. Maintain a data contract register for critical use cases.
2. Require repository/DAO/ORM methods to expose transaction scope and SQL behavior.
3. Require parameterized SQL for all user-controlled input.
4. Require EXPLAIN/execution plan evidence for critical SQL/index/schema changes.
5. Require explicit transaction isolation and retry policy for contested workflows.
6. Encode invariants in constraints where possible.
7. Treat index, partition, and shard changes as RFC-governed operational changes.
8. Separate replication, backup, and PITR responsibilities.
9. Monitor WAL/binlog/log-chain, checkpoint, replication lag, lock/deadlock, and restore success.
10. Test restore and failover with verification SQL.

### Metrics

p99 query latency, rows scanned/returned, plan hash churn, cardinality error, query count/request, transaction duration, lock wait, deadlock count, retry success, index usage/bloat, replication lag, WAL/binlog growth, checkpoint duration, backup age, restore duration, RPO/RTO, schema drift.

### Failure Modes

ORM N+1, stale statistics, plan regression, missing constraints, deadlocks, long transactions, hidden trigger side effects, replication lag/divergence, backup failure, PITR log-chain gap, checkpoint stalls, storage/fsync failures, sharding hotspots.

### Anti-patterns

ORM hides SQL; DAO owns business transaction; replication is backup; partitioning fixes all performance; index without target query; long transaction around external call; trigger as workflow engine; durability settings weakened for speed; no restore drills.

### Implementation Guide

- 0–30 days: inventory DBs, queries, ORM, backups, RPO/RTO; perform first restore test.
- 31–90 days: standardize repository, SQL, schema/index RFC, transaction/retry, backup/restore runbooks.
- 91–180 days: automate plan regression, N+1 detection, restore drills, replication/failover rehearsal.
- 181–365 days: integrate DB engineering into service SLO, continuous capacity/index/statistics optimization, sharding/distributed SQL decision framework.

---

## 18. Appendix: Engine-Specific Notes

### PostgreSQL

- Strong evidence surface for MVCC, transaction isolation, EXPLAIN, planner/optimizer, partitioning, logical replication, continuous archiving/PITR, WAL, checkpoint, and storage layout.
- Best used as a transferable model for schema-first, WAL-backed, MVCC RDB engineering.
- Caution: engine-specific isolation semantics, autovacuum/statistics, replication slots, WAL retention, and extension behavior require direct operational review.

### MySQL / InnoDB

- Strong evidence surface for InnoDB transaction model, repeatable-read default, row locks, deadlocks, redo log, checkpoints, binary log, GTID replication, and PITR.
- Best used as a model for high-adoption OLTP and replication/binlog operations.
- Caution: gap locks, isolation semantics, binlog configuration, and online DDL vary by version and configuration.

### SQL Server

- Strong evidence surface for query processing architecture, plan cache, locking/row versioning, deadlock handling, transaction log, recovery models, log backup, and checkpoints.
- Best used as a model for explicit recovery model governance and enterprise operational documentation.
- Caution: edition/platform differences and Azure SQL variants must be checked separately.

### SQLite

- Strong evidence surface for WAL mode, checkpointing, isolation, locking, prepared statements, and query planner counters.
- Best used as a model for embedded/local RDB where storage file semantics are application-visible.
- Caution: single-writer and filesystem behavior dominate concurrency design.

### Spanner / CockroachDB / Vitess / Aurora

- Spanner and CockroachDB represent distributed SQL consistency and quorum/transaction tradeoffs.
- Vitess represents sharded MySQL with resharding and VReplication operations.
- Aurora represents storage-layer replication and managed continuous backups.
- Caution: these systems solve different problems. Treat them as topology exemplars, not interchangeable RDB choices.

---

## 19. Final QA

| QA Check | Status | Notes |
|---|---|---|
| T0/T2/T3 evidence present | Pass | SQL/Jakarta/OWASP standards and official DB docs included |
| Source family diversity | Pass | Standards, official product docs, OSS docs, papers, incident reports |
| Critical claims A/B | Pass | WAL/PITR/isolation/query-plan/replication/backup claims have direct sources |
| Failure evidence included | Pass | GitLab, GitHub, PostgreSQL fsync, SQL anti-pattern paper |
| Historical/difference evidence | Partial | Fsync history and incident reports included; Wayback diff not executed |
| Current canonical docs checked | Pass | Current official docs used where available |
| Clone Spec fields complete | Pass | Definition, exemplars, evidence, philosophy, decision model, operating model, specs, metrics, failure modes, anti-patterns, maturity, implementation guide, unknowns |
| Remaining gap | Known | Canonical layer names for IDs 10 not supplied; names inferred |
