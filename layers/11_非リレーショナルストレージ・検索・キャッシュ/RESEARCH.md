# 非リレーショナルストレージ・検索・キャッシュ — Frontier Operating Model Research

Generated: 2026-05-13  
Scope: Layer 11。他レイヤーの詳細設計はユーザー指定外のため対象外。  
Research mode: 公開情報限定。公式ドキュメント、標準、OSS ドキュメント、クラウド設計ガイドを優先し、マーケティング資料や第三者記事は原則として補助扱いにした。

## 0. Executive Summary

この単位の Frontier pattern は、**データ形状ではなくアクセスパターンを先に固定し、永続ストア・検索インデックス・キャッシュを別々の意思決定対象として扱い、TTL / retention / invalidation をデータライフサイクル制御として明示する**、という運用モデルである。

非リレーショナルストレージの先端設計は、単に「NoSQL を使う」ことではない。DynamoDB は key-value / document model を支えるが、主キー、パーティションキー、ソートキー、GSI の設計でアクセスパターンを物理分散に落とす [S01][S02][S03][S04][S05]。MongoDB は document model において embedding / references / shard key / indexes をクエリ形状に合わせる [S07][S08][S09][S10][S11]。Cassandra は query-first modeling と partition key を中心に設計し、TTL は tombstone と compaction の運用負荷に直結する [S12][S13][S14][S15]。Neo4j は property graph model、schema constraints、search-performance indexes、GQL / SPARQL の標準語彙によって、関係探索を第一級の query object にする [S16][S17][S18][S19][S20]。InfluxDB / Prometheus 系の time-series は timestamp、measurement / tags / fields、bucket、shard、retention、WAL / block / compaction を中心に設計する [S21][S22][S23][S24][S25][S26]。

検索・キャッシュの先端設計では、検索インデックスを「DB の副産物」ではなく独立した serving layer として扱う。Elasticsearch は index を documents / mappings / settings / shards の組で定義し、Lucene は postings + term dictionary を inverted index の中核とする [S27][S28][S29][S30][S31]。キャッシュは、Redis / Memcached の低レイテンシ特性だけでなく、cache-aside / write-through、TTL、jitter、eviction、distributed key routing、client-side invalidation をアプリケーション契約として実装する必要がある [S32][S33][S34][S35][S36][S37][S38][S39][S40][S41][S42][S43][S44]。

最終的な Clone Spec の核は次の 8 点である。

1. **Access-pattern-first**: key、document shape、partition、index、cache key は、実データ構造ではなく read/write pattern から逆算する。
2. **Primary-key discipline**: key-value / wide-column は primary key が物理配置、スループット、局所性、hot partition を決める。
3. **Workload-based indexing**: document / graph / search index では、全 field を索引化せず、query predicate、sort、range、full-text、aggregation の実需要から index catalog を作る。
4. **Lifecycle as a first-class policy**: TTL、retention、archive、delete、compaction、eviction は後付けでなく schema / key / index 設計の一部にする。
5. **Search is not storage**: full-text / vector / faceted search の serving index は、source-of-truth DB と同期・再構築・遅延許容を明示する。
6. **Cache owns staleness risk**: cache-aside / write-through / client-side caching / keyspace event を使う場合、stale read、stampede、origin load、eviction を測定する。
7. **Distribution requires key governance**: shard key、hash slot、hash tag、partition suffix、tenant prefix、cardinality budget を registry 化する。
8. **Failure search is mandatory**: hot partitions、large partitions、tombstone accumulation、index bloat、query fan-out、cache stampede、TTL herd、stale invalidation を設計時に検出する。

---

## 1. Layer Registry

| Layer ID | Layer Name | Definition | Decision Question | Decision Object | Primary Owner Roles | Default Metrics |
|---|---|---|---|---|---|---|
| 11.01 | Key-value store | key による単一 item / value 取得、条件付き更新、partitioned serving を制御する層。 | どのアクセスパターンを key-addressed operation に落とし、どの key schema と分散方式で低レイテンシ・高スループットを維持するか。 | key schema, partition key, sort key, value envelope, consistency mode | Data platform architect, backend service owner, SRE | p50/p95/p99 latency, RCU/WCU or ops/sec, hot key rate, partition skew, item size, conditional failure rate |
| 11.02 | Document store | JSON/BSON 的 document、embedding / reference、document index、schema evolution を制御する層。 | どの関連データを 1 document に埋め込み、どの関係を参照化し、どの index / shard key で query pattern を支えるか。 | document schema, relationship model, index catalog, shard key | Application architect, data model owner, DBA/SRE | query latency, document size, index selectivity, working-set ratio, shard balance, write amplification |
| 11.03 | Column / wide-column store | partition key + clustering columns による分散 row / column-family 型アクセスを制御する層。 | どの query をどの table / partition に閉じ、large partition と tombstone を避けつつ write-heavy workload を支えるか。 | table-per-query model, primary key, compaction, consistency level | Data platform architect, Cassandra/Scylla operator, SRE | partition size, tombstones/read, compaction backlog, read/write latency, repair lag, consistency error rate |
| 11.04 | Graph store | node / relationship / property / label / traversal / graph query を制御する層。 | どの関係を edge として第一級化し、どの constraint / index / traversal pattern で探索を開始・制限するか。 | property graph / RDF graph model, graph schema, traversal policy | Graph data modeler, domain architect, analytics owner | traversal latency, expansion factor, path length, index usage, constraint violations, graph density |
| 11.05 | Time-series store | timestamped data、tags / labels、bucket、shard、retention、downsample を制御する層。 | どの時系列をどの cardinality・retention・aggregation 粒度で保存し、古いデータをどう削除・圧縮・集約するか。 | measurement/table model, tag set, retention policy, shard duration, rollup policy | Observability owner, data platform SRE, capacity owner | ingest rate, active series/cardinality, query latency by range, retention cost, compaction lag, WAL/block size |
| 11.06 | Search index | full-text / structured / vector / faceted search の serving index を制御する層。 | どの source data を、どの mapping / analyzer / shard / refresh / relevance policy で検索可能にするか。 | search index schema, mapping, analyzer, shard plan, refresh policy | Search platform owner, application owner, relevance engineer | indexing throughput, search latency, relevance metrics, refresh lag, shard size, merge backlog |
| 11.07 | Inverted index | term → postings list / doc values / segment という情報検索の基盤構造を制御する層。 | どの field を token 化し、どの term dictionary / postings / skip / scoring / segment merge で query を高速化するか。 | analyzer chain, token stream, postings format, segment lifecycle | Search engineer, IR engineer, platform SRE | index size, postings length, query CPU, merge time, false positives, scoring latency |
| 11.08 | Cache | origin data store の負荷・レイテンシを下げるための一時保存を制御する層。 | 何を cacheable とし、cache-aside / write-through / read-through のどれで freshness と負荷を両立させるか。 | cache contract, cache object, population strategy, eviction policy | Backend service owner, SRE, performance engineer | hit ratio, miss penalty, origin QPS reduction, stale-read rate, eviction rate, memory utilization |
| 11.09 | Distributed cache | 複数 node / shard にまたがる cache routing、replication、availability、hot key を制御する層。 | どの key をどの routing / slot / shard / replica に置き、multi-key operation と failover をどう制限するか。 | cluster topology, hash slots, key routing, replica policy | Platform SRE, cache operator, backend architect | slot balance, node memory skew, failover time, cross-slot error rate, hot shard rate, network latency |
| 11.10 | Cache key | cache object を一意に識別する名前空間、versioning、tenant isolation、dependency を制御する層。 | どの request / entity / policy version / tenant / locale / auth scope を key に入れ、衝突・過剰粒度・無効化不能を避けるか。 | key naming scheme, key envelope, version stamp, dependency graph | Backend owner, API owner, security owner | key cardinality, collision rate, invalidation coverage, stale key count, key length, namespace violations |
| 11.11 | Invalidation | source update、event、delete、schema change による cache / index の無効化を制御する層。 | どの change event がどの cache / index / local cache を無効化し、失敗時に TTL / replay / repair でどう収束するか。 | invalidation event map, dependency graph, replay policy | Event platform owner, backend owner, SRE | invalidation latency, missed event rate, stale-read rate, replay success, dead-letter queue size |
| 11.12 | TTL | データ・cache・index・session の有効期限と自動削除を制御する層。 | どの object に何秒/何日/どの clock basis の TTL を設定し、jitter、retention、compaction、archive とどう接続するか。 | TTL policy, expiration field, retention window, jitter rule | Data governance owner, service owner, SRE | expiry lag, deletion throughput, TTL herd events, tombstone backlog, stale window, storage reduction |

---

## 2. Source Catalog

| Source ID | Entity | Title / Locator | Source Type | Tier | Why it matters |
|---|---|---|---|---|---|
| S01 | AWS | [What is Amazon DynamoDB?](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html) | official_doc | T0/T2 | DynamoDB が key-value / document data model を支えることを明示する。 |
| S02 | AWS | [Core components of Amazon DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html) | official_doc | T0/T2 | table / item / attribute / primary key / partition key / sort key の中核定義。 |
| S03 | AWS | [Designing partition keys to distribute your workload in DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-partition-key-uniform-load.html) | official_doc | T0/T3 | hot partition と workload distribution の設計根拠。 |
| S04 | AWS | [Data Modeling foundations in DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/data-modeling-foundations.html) | official_doc | T0/T3 | single-table design と access-pattern-first の根拠。 |
| S05 | AWS | [Using Global Secondary Indexes in DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GSI.html) | official_doc | T0/T2 | alternate access pattern と index capacity の根拠。 |
| S06 | AWS | [Using time to live in DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/TTL.html) | official_doc | T0/T2 | per-item expiration timestamp と自動削除の根拠。 |
| S07 | MongoDB | [Data Modeling in MongoDB](https://www.mongodb.com/docs/manual/data-modeling/) | official_doc | T0/T3 | embedding / referencing を access pattern に合わせる設計根拠。 |
| S08 | MongoDB | [Embedded Data in Your MongoDB Schema](https://www.mongodb.com/docs/manual/data-modeling/embedding/) | official_doc | T0/T3 | related data を単一 document に入れ、1 database operation で取得する根拠。 |
| S09 | MongoDB | [Schema Design Patterns](https://www.mongodb.com/docs/manual/data-modeling/design-patterns/) | official_doc | T0/T3 | schema pattern と query performance の根拠。 |
| S10 | MongoDB | [Choose a Shard Key](https://www.mongodb.com/docs/manual/core/sharding-choose-a-shard-key/) | official_doc | T0/T3 | shard key cardinality と horizontal scaling の根拠。 |
| S11 | MongoDB | [TTL Indexes](https://www.mongodb.com/docs/manual/core/index-ttl/) | official_doc | T0/T2 | TTL index による document 自動削除の根拠。 |
| S12 | Apache Cassandra | [Logical Data Modeling](https://cassandra.apache.org/doc/3.11/cassandra/data_modeling/data_modeling_logical.html) | official_doc | T0/T3 | primary key が partition size と read speed を左右する根拠。 |
| S13 | Apache Cassandra | [Storage-Attached Indexing Overview](https://cassandra.apache.org/doc/stable/cassandra/developing/cql/indexing/sai/sai-overview.html) | official_doc | T0/T2 | secondary index / SAI の適用範囲。 |
| S14 | Apache Cassandra | [Compaction / Tombstones](https://cassandra.apache.org/doc/latest/cassandra/managing/operating/compaction/tombstones.html) | official_doc | T0/T3 | delete / TTL が tombstone になり compaction 対象になる根拠。 |
| S15 | Apache Cassandra | [CQL TTL](https://cassandra.apache.org/doc/latest/cassandra/developing/cql/cql_singlefile.html) | official_doc | T0/T2 | TTL が inserted values に作用し、update で reset される挙動。 |
| S16 | Neo4j | [Graph database concepts](https://neo4j.com/docs/getting-started/appendix/graphdb-concepts/) | official_doc | T0/T3 | nodes / relationships / properties の定義。 |
| S17 | Neo4j | [Index configuration](https://neo4j.com/docs/operations-manual/current/performance/index-configuration/) | official_doc | T0/T2 | range / point / text / full-text / token lookup index の根拠。 |
| S18 | Neo4j | [Constraints](https://neo4j.com/docs/cypher-manual/current/schema/constraints/) | official_doc | T0/T2 | uniqueness / existence constraints による graph quality control。 |
| S19 | ISO | [ISO/IEC 39075:2024 Database languages — GQL](https://www.iso.org/standard/76120.html) | standard | T0 | property graph の data structures / operations / query language 標準。 |
| S20 | W3C | [SPARQL 1.1 Query Language](https://www.w3.org/TR/sparql11-query/) | standard | T0 | RDF graph query の標準。 |
| S21 | InfluxData | [InfluxDB schema design recommendations](https://docs.influxdata.com/influxdb3/cloud-serverless/write-data/best-practices/schema-design/) | official_doc | T0/T3 | bucket / measurement / tag / field の time-series modeling。 |
| S22 | InfluxData | [InfluxDB shards and shard groups](https://docs.influxdata.com/influxdb/v2/reference/internals/shards/) | official_doc | T0/T2 | time-based shard / shard group / shard lifecycle の根拠。 |
| S23 | InfluxData | [In-memory indexing and TSM](https://docs.influxdata.com/influxdb/v1/concepts/storage_engine/) | official_doc | T0/T2 | WAL / cache / TSM / shard の storage-engine 根拠。 |
| S24 | InfluxData | [Data retention in InfluxDB](https://docs.influxdata.com/influxdb/v2/reference/internals/data-retention/) | official_doc | T0/T2 | retention enforcement と expired data deletion。 |
| S25 | InfluxData | [Time Series Index details](https://docs.influxdata.com/influxdb/v1/concepts/tsi-details/) | official_doc | T0/T2 | TSI が LSM-tree-based index である根拠。 |
| S26 | Prometheus | [Storage](https://prometheus.io/docs/prometheus/latest/storage/) | official_doc | T0/T2 | TSDB blocks / WAL / retention の reference。 |
| S27 | Elastic | [Index fundamentals](https://www.elastic.co/docs/manage-data/data-store/index-basics) | official_doc | T0/T2 | documents / mappings / settings / shards の search index definition。 |
| S28 | Elastic | [Near real-time search](https://www.elastic.co/docs/manage-data/data-store/near-real-time-search) | official_doc | T0/T2 | segment / refresh / NRT search の挙動。 |
| S29 | Elastic | [Merge settings](https://www.elastic.co/docs/reference/elasticsearch/index-settings/merge) | official_doc | T0/T2 | Lucene segment merge と immutable segment の根拠。 |
| S30 | Apache Lucene | [org.apache.lucene.index package summary](https://lucene.apache.org/core/10_3_1/core/org/apache/lucene/index/package-summary.html) | official_doc | T0/T2 | postings + term dictionary と inverted index の中核定義。 |
| S31 | OpenSearch | [Intro to OpenSearch](https://docs.opensearch.org/latest/getting-started/intro/) | official_doc | T0/T2 | inverted index が words → documents を map する定義。 |
| S32 | Redis | [EXPIRE command](https://redis.io/docs/latest/commands/expire/) | official_doc | T0/T2 | passive / active expiration の実装根拠。 |
| S33 | Redis | [Key eviction](https://redis.io/docs/latest/develop/reference/eviction/) | official_doc | T0/T2 | maxmemory と eviction policy の根拠。 |
| S34 | Redis | [Redis cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/) | official_doc | T0/T2 | hash slots / hash tags / multi-key constraints の根拠。 |
| S35 | Redis | [Scale with Redis Cluster](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/) | official_doc | T0/T3 | live resharding と same-slot multi-key operation の根拠。 |
| S36 | Redis | [Redis keyspace notifications](https://redis.io/docs/latest/develop/pubsub/keyspace-notifications/) | official_doc | T0/T2 | key events / expiration events を subscribe する仕組み。 |
| S37 | Redis | [Client-side caching reference](https://redis.io/docs/latest/develop/reference/client-side-caching/) | official_doc | T0/T2 | invalidation messages と stale avoidance の根拠。 |
| S38 | Memcached | [Memcached Documentation](https://docs.memcached.org/) | official_doc | T0/T2 | key / expiration / flags / raw data、LRU cache の根拠。 |
| S39 | Memcached | [Basic Text Protocol](https://docs.memcached.org/protocols/basic/) | official_doc | T0/T2 | key length、expiration time、CAS の protocol-level contract。 |
| S40 | Microsoft Azure | [Cache-Aside Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside) | official_doc | T0/T3 | cache-aside、expiration policy、stale data handling の設計根拠。 |
| S41 | Microsoft Azure | [Caching guidance](https://learn.microsoft.com/en-us/azure/architecture/best-practices/caching) | official_doc | T0/T3 | distributed cache consistency trade-off、expiration、layering の根拠。 |
| S42 | AWS | [Caching patterns — Database Caching Strategies Using Redis](https://docs.aws.amazon.com/whitepapers/latest/database-caching-strategies-using-redis/caching-patterns.html) | official_doc / historical whitepaper | T3 | cache-aside / write-through の整理。Historical reference 扱い。 |
| S43 | AWS | [Cache Validity](https://docs.aws.amazon.com/whitepapers/latest/database-caching-strategies-using-redis/cache-validity.html) | official_doc / historical whitepaper | T3 | TTL と jitter の設計根拠。Historical reference 扱い。 |
| S44 | AWS | [Evictions](https://docs.aws.amazon.com/whitepapers/latest/database-caching-strategies-using-redis/evictions.html) | official_doc / historical whitepaper | T3 | LRU / LFU / volatile-ttl / noeviction の比較。Historical reference 扱い。 |
| S45 | RocksDB | [RocksDB Bloom Filter](https://github.com/facebook/rocksdb/wiki/RocksDB-Bloom-Filter) | repo_doc | T3 | SST file lookup と Bloom filter の key-value storage exemplar。 |
| S46 | RocksDB | [RocksDB Compaction](https://github.com/facebook/rocksdb/wiki/Compaction) | repo_doc | T3 | LSM compaction と write amplification trade-off の exemplar。 |

---

## 3. Candidate Scoring

Scoring is evidence-density oriented, not a product ranking. Weight: Performance 25 / Adoption 15 / Artifact Richness 20 / Peer Validation 15 / Recency 10 / Transferability 10 / Failure Evidence 5.

| Candidate / Family | Covered Layers | Score / 100 | Rationale |
|---|---:|---:|---|
| Amazon DynamoDB | 11.01, 11.02, 11.10, 11.12 | 91 | key-value / document model、primary key、partition-key distribution、GSI、TTL、access-pattern documentation が厚い [S01][S02][S03][S04][S05][S06]。 |
| MongoDB | 11.02, 11.05, 11.12 | 89 | document modeling、embedding/reference、schema patterns、shard key、TTL index、time-series index が公式 docs に揃う [S07][S08][S09][S10][S11]。 |
| Apache Cassandra | 11.03, 11.12 | 88 | query-first / primary-key model、SAI、TTL→tombstone、compaction failure modes が観測可能 [S12][S13][S14][S15]。 |
| Neo4j + GQL / SPARQL | 11.04, 11.06 | 84 | property graph concepts、constraints、search-performance index、GQL / SPARQL 標準が揃う [S16][S17][S18][S19][S20]。 |
| InfluxDB + Prometheus | 11.05, 11.12 | 86 | time-series model、bucket/shard/retention、TSM/TSI、WAL/block retention が観測可能 [S21][S22][S23][S24][S25][S26]。 |
| Elasticsearch / Lucene / OpenSearch | 11.06, 11.07 | 92 | search index、inverted index、mappings、segments、refresh、merge の公式説明が強い [S27][S28][S29][S30][S31]。 |
| Redis / Memcached | 11.08, 11.09, 11.10, 11.11, 11.12 | 90 | TTL、eviction、cluster hash slots、keyspace notifications、client-side invalidation、memcached protocol が揃う [S32][S33][S34][S35][S36][S37][S38][S39]。 |
| Azure / AWS caching guidance | 11.08, 11.11, 11.12 | 82 | cache-aside、distributed cache consistency、TTL / jitter / eviction の汎用設計指針がある。ただし AWS whitepaper は historical reference として扱う [S40][S41][S42][S43][S44]。 |
| RocksDB | 11.01, 11.07 | 77 | embedded key-value / LSM / Bloom filter / compaction の技術 exemplar。application-level operating model は他候補より薄い [S45][S46]。 |

---

## 4. Evidence Map

| Claim ID | Claim | Decision Field | Confidence | Supporting Sources |
|---|---|---|---|---|
| C01 | Key-value / document store は primary key と access pattern を物理配置・低レイテンシの単位にする。 | criteria / interface rules | A | [S01][S02][S03][S04] |
| C02 | DynamoDB の partition key design が hot partition / throttling / workload distribution を左右する。 | failure_modes / thresholds | A | [S03][S02] |
| C03 | Document store では embedding と references を query / update pattern に基づいて選ぶ。 | decision rules | A | [S07][S08][S09] |
| C04 | Shard key は high cardinality と distribution を満たさないと horizontal scaling を阻害する。 | thresholds / failure_modes | A | [S10][S03] |
| C05 | Cassandra の primary key は partition size と on-disk organization と read speed を決定する。 | decision rules | A | [S12] |
| C06 | Cassandra の TTL は expiration 後に tombstone を作り、compaction / gc_grace_seconds と結びつく。 | failure_modes / lifecycle | A | [S14][S15] |
| C07 | Graph store は nodes / relationships / properties を first-class objects とし、constraints と indexes で探索を制御する。 | interface rules / controls | A | [S16][S17][S18] |
| C08 | GQL は property graph の構造・操作・照会の標準であり、SPARQL は RDF graph query の標準である。 | standard vocabulary | A | [S19][S20] |
| C09 | Time-series store は measurement / tags / fields / timestamp、bucket / shard、retention を schema-level に扱う。 | technical spec | A | [S21][S22][S24] |
| C10 | InfluxDB 系では TSM / TSI / WAL / shard lifecycle が storage-engine と query cost を支える。 | technical spec | A | [S23][S25] |
| C11 | Search index は documents / mappings / settings / shards の組であり、refresh と segment merge が freshness / cost を決める。 | interface / cadence | A | [S27][S28][S29] |
| C12 | Inverted index は term dictionary + postings で term から documents へ lookup する構造である。 | technical spec | A | [S30][S31] |
| C13 | Redis TTL は passive expiration と active expiration の両方で処理される。 | lifecycle / controls | A | [S32] |
| C14 | Cache TTL は data change rate と stale-data risk に合わせ、jitter で synchronized expiry を緩和する。 | thresholds / exceptions | B | [S40][S43] |
| C15 | Redis Cluster は hash slots と hash tags を使い、multi-key operation は same slot に制約される。 | distribution / prohibitions | A | [S34][S35] |
| C16 | Redis keyspace notifications と client-side caching は event / invalidation messages で stale local cache を抑える。 | invalidation controls | A | [S36][S37] |
| C17 | Memcached は key / expiration / flags / raw data を protocol-level item として扱い、expiration 0 や 30-day boundary を持つ。 | interface / thresholds | A | [S38][S39] |
| C18 | Eviction は容量超過時の automatic key removal であり、TTL とは別の memory control である。 | controls / failure_modes | A | [S33][S44] |
| C19 | Cache-aside は application が cache hit/miss、origin fetch、populate、freshness を管理する。 | operating model | A | [S40][S42] |
| C20 | Distributed cache は consistency / availability / partition-tolerance の trade-off を明示し、local + shared cache の層化は複雑性を増やす。 | tradeoff / exceptions | B | [S41][S42] |

---

## 5. Cross-layer Core Philosophy

### 5.1 Access pattern is the schema

非リレーショナル領域では、schema は ER 図の正規化結果ではなく、**実際に発行される read / write / update / delete / search / invalidation pattern の materialization** である。DynamoDB の single-table design、Cassandra の query-first table、MongoDB の embedding / referencing、Elasticsearch の mapping / analyzer、Redis の cache key はすべてこの原則で統合できる [S04][S12][S07][S27][S32]。

### 5.2 Distribution is governed by names

partition key、shard key、hash slot、hash tag、tenant prefix、cache namespace は、データの論理名であると同時に物理配置と負荷分散の制御面である。したがって、命名規則は単なる style guide ではなく、capacity engineering の主要成果物である [S03][S10][S34][S35]。

### 5.3 Indexes are contracts, not hints

document index、SAI、graph index、search index、inverted index は、特定の query contract を支えるために作る。索引を増やすほど read latency は下がることがあるが、write amplification、merge cost、storage cost、schema migration cost が増える。frontier operator は index catalog に owner、query、predicate、selectivity、write cost、retirement rule を持たせる [S05][S13][S17][S27][S29][S30]。

### 5.4 TTL is policy, not cleanup

TTL は「勝手に消す」機能ではなく、staleness、compliance、storage cost、origin load、compaction、tombstone、jitter、archive を束ねる policy である。DynamoDB TTL、MongoDB TTL index、Cassandra TTL、InfluxDB retention、Redis EXPIRE / eviction、Memcached expiration は、同じ単語でも挙動と operational side effects が異なる [S06][S11][S14][S15][S24][S32][S39]。

### 5.5 Cache is a probabilistic optimization layer

cache は source of truth ではなく、可用性・一貫性・レイテンシ・origin load の trade-off を最適化する layer である。cache-aside では application が freshness を管理し、distributed cache では network partition / failover / local cache invalidation / hot key を織り込む必要がある [S40][S41][S42][S43]。

---

# 6. Clone Specs by Layer

## 6.1 Layer 11.01 — Key-value store

### Definition

Key-value store は、key-addressed operation を中心に、single item lookup、conditional update、partitioned serving、optional sort key / secondary access を制御する層である。value は opaque blob、JSON/document、attribute map、structured entity などでよいが、frontier design では key schema がアクセス契約の中心になる。

### Frontier Exemplars

- **Amazon DynamoDB**: key-value / document data model、partition key / sort key、GSI、TTL、single-table design を公式 docs が体系化している [S01][S02][S04][S05][S06]。
- **Redis / Memcached**: in-memory key-value cache として、expiration、eviction、key protocol、distributed cluster constraints を公開している [S32][S33][S34][S38][S39]。
- **RocksDB**: embedded key-value の LSM / Bloom filter / compaction exemplar。production service contract より storage-engine trade-off の参照に向く [S45][S46]。

### Decision Model

| Field | Spec |
|---|---|
| Inputs | access pattern inventory, QPS by key, item size distribution, read/write mix, consistency requirement, update conflict risk, tenant boundaries |
| Decision Object | key schema + value envelope + partition / sort / secondary access design |
| Criteria | direct lookup ratio, key cardinality, partition distribution, conditional update safety, item size, cost per operation, observability |
| Priorities | exact-key lookup first; high-cardinality partitioning; colocate only data read together; avoid scan; define item envelope version |
| Prohibitions | low-cardinality hot key as primary partition key; unbounded item growth; opaque key naming without registry; using KV as ad hoc relational join engine |
| Thresholds | item size budget; per-partition throughput budget; key cardinality minimum; p99 latency SLO; conditional retry budget |
| Owners | service owner, data platform architect, SRE, cost owner |
| Cadence | design review before new entity/access pattern; monthly hot-key review; quarterly key schema migration review |
| Controls | key-schema registry, load tests by access pattern, hot-partition alarms, conditional write policy, TTL policy, index catalog |
| Exceptions | append-only event objects, session tokens, ephemeral locks, feature flags; each requires explicit TTL / conflict policy |

### Technical / Business Specification

1. Create an `access_patterns.yaml` before table/key design. Required fields: operation name, read/write, key predicates, sort/range predicates, expected QPS, item size, consistency, SLA, owner.
2. Define key pattern as `entity#id` or `tenant#entity#id` only when tenant isolation and distribution are both validated. Do not put low-cardinality states such as `status#open` alone as partition key.
3. For composite access, decide whether it belongs in sort key, GSI, materialized item duplication, or search index. Do not add secondary index unless an access pattern owns it.
4. Design value envelope with `schema_version`, `entity_type`, `updated_at`, `ttl_epoch` if applicable, and `source_event_id` if replicated.
5. For writes with conflict risk, require conditional expressions / compare-and-set / optimistic versioning.
6. For high-write workloads, test hot partitions with production-like key distributions, not uniform synthetic IDs.

### Metrics

- p50 / p95 / p99 get / put / update latency
- operation throughput by key prefix and partition
- hot key / hot partition rate
- item size p50 / p99 and max
- conditional write failure and retry rate
- secondary-index write amplification
- TTL deletion lag and expired item count
- scan / query ratio; scans should approach zero for OLTP workloads

### Failure Modes

- **Hot partition**: one partition key receives disproportionate load and throttles [S03].
- **Unbounded item growth**: value envelope becomes a mini-database, causing latency and cost spikes.
- **Index afterthought**: secondary access patterns are added after production, causing backfill and throughput risk [S05].
- **No TTL owner**: ephemeral entities persist indefinitely, raising storage cost [S06].
- **Opaque keys**: invalidation and migration become impossible because key structure is not discoverable.

### Anti-patterns

- Designing key schema from object class names rather than access patterns.
- Using random UUID everywhere without considering query grouping.
- Overloading one key namespace across tenants, environments, and versions.
- Relying on scans for operational reports in a KV store.
- Storing mutable aggregate documents without version / compare-and-set.

### Clone Implementation Guide

- Week 1–2: inventory top 50 read/write access patterns and rank by QPS, latency, business criticality.
- Week 3–4: create key-schema registry and model 2–3 candidate key designs; load-test skewed workloads.
- Week 5–6: define secondary access rules: sort key, GSI, duplication, or external search index.
- Week 7–8: add dashboards for hot key, partition skew, TTL lag, conditional failures.
- Week 9–12: migrate first service behind a key-contract review gate.

### Confidence & Unknowns

- Confidence A: key-value / document data model, partition key, sort key, GSI, TTL evidence is direct [S01][S02][S05][S06].
- Confidence B: exact frontier thresholds vary by provider/account/workload. Use load tests and provider quotas to set local thresholds.
- Unknown: internal adaptive partition behavior beyond official docs; treat as black-box and validate empirically.

---

## 6.2 Layer 11.02 — Document store

### Definition

Document store は、document shape、embedded subdocuments、references、schema evolution、document-level indexing、sharding、lifecycle を制御する層である。document は domain object と近いが、frontier design では application object ではなく query/update unit として設計する。

### Frontier Exemplars

- **MongoDB**: data modeling docs、embedding / referencing、schema patterns、shard key、TTL indexes が体系化されている [S07][S08][S09][S10][S11]。
- **DynamoDB document model**: key-value と document model を併せ持ち、access pattern による single-table design の比較対象になる [S01][S04]。

### Decision Model

| Field | Spec |
|---|---|
| Inputs | domain relationship map, read shape, update frequency, atomicity boundary, document growth, query predicates, shard key candidates |
| Decision Object | document schema + relationship representation + index / shard / TTL plan |
| Criteria | one-read retrieval, update locality, bounded document size, index selectivity, shard distribution, schema evolvability |
| Priorities | embed data read together; reference data updated independently or growing unbounded; index actual predicates; model lifecycle early |
| Prohibitions | embedding unbounded arrays; wildcard indexing as substitute for workload planning; low-cardinality shard key; mixed schema without version |
| Thresholds | document size p99, embedded-array growth limit, index count budget, shard-key cardinality, stale schema version age |
| Owners | application architect, document schema owner, DBA/SRE, analytics owner |
| Cadence | schema review per feature; index review monthly; shard-key review before scale-out; TTL review quarterly |

### Technical / Business Specification

1. For every document type, maintain `document_schema.md` with: query examples, update examples, fields, embedded arrays, references, indexes, shard key, TTL / archive rule.
2. Use embedding for one-to-few / read-together / atomic-update groups. Use references for many-to-many, independently updated, large, or security-separated relationships [S07][S08].
3. Create indexes from query workload, not from every field. Partial / sparse / wildcard indexes must have an explicit reason and retirement rule [S09].
4. Shard key candidates must be scored for cardinality, frequency, monotonicity, distribution, and query targeting [S10].
5. Use TTL indexes for finite-lifetime data such as logs, sessions, or machine-generated events, but do not treat TTL as archival if the data is needed for compliance or audit [S11].

### Metrics

- query latency by collection and predicate
- index selectivity and index hit ratio
- document size distribution and growth rate
- shard balance, jumbo chunk / skew indicators
- write amplification by index count
- schema version distribution
- TTL delete lag and expired documents remaining

### Failure Modes

- **Unbounded embedded array** causing document size and update cost explosion.
- **Scatter-gather queries** when shard key is absent from predicates [S10].
- **Index sprawl** increasing write cost and migration risk.
- **Schema drift** where application versions interpret the same field differently.
- **TTL misuse** where operational cleanup deletes data needed for audit [S11].

### Anti-patterns

- Copying relational normalized schema into document store as references-only.
- Embedding every child object without a growth bound.
- Adding wildcard indexes to avoid understanding workload.
- Choosing shard key from business semantics without cardinality analysis.
- Storing cache-like ephemeral documents with no TTL.

### Clone Implementation Guide

- Build a document relationship decision matrix: embed / reference / duplicate / search-index.
- Add an index catalog with owner, query, selectivity, storage, write cost, and last-used date.
- Run shard-key simulations using production-like tenant and time distributions.
- Add TTL index only after classifying data as ephemeral, archival, regulated, or source-of-truth.
- Add schema versioning and migration playbook before multi-version deployment.

### Confidence & Unknowns

- Confidence A: embedding/reference and TTL index claims are directly supported [S07][S08][S11].
- Confidence A: shard key cardinality and scaling claim is directly supported [S10].
- Unknown: exact index selectivity thresholds must be measured per workload.

---

## 6.3 Layer 11.03 — Column / wide-column store

### Definition

Column / wide-column store は、Cassandra-style の keyspace / table / partition key / clustering columns / column values / compaction / consistency / TTL を制御する層である。frontier design では、1 table = 1 or small set of query shapes と捉え、normalized schema ではなく query materialization を作る。

### Frontier Exemplars

- **Apache Cassandra**: logical data modeling、primary key の重要性、SAI、TTL / tombstone / compaction の公式説明が揃う [S12][S13][S14][S15]。
- **DataStax / Cassandra-compatible ecosystems**: operational best practices の補助候補。直接採用は Apache docs で裏取りする。

### Decision Model

| Field | Spec |
|---|---|
| Inputs | query list, required ordering, time window, partition cardinality, write rate, consistency requirement, TTL need |
| Decision Object | table-per-query schema + partition key + clustering columns + compaction / TTL policy |
| Criteria | single-partition query, bounded partition size, write distribution, clustering order, tombstone control, repair/compaction feasibility |
| Priorities | query-first; denormalize deliberately; keep partitions bounded; avoid secondary indexes unless SAI use case is explicit |
| Prohibitions | cross-partition OLTP query; low-cardinality partition key; mixed TTL and non-TTL data in same hot partition without tombstone model |
| Thresholds | partition size budget, rows per partition, tombstones per read, compaction backlog, repair interval, consistency SLA |
| Owners | data platform architect, Cassandra operator, service owner, SRE |
| Cadence | design review for each query/table; tombstone review weekly; compaction/repair review monthly |

### Technical / Business Specification

1. Start from `queries.md`, not `entities.md`. For each query, define exact partition predicates and clustering range.
2. Partition key must keep query inside a bounded, high-cardinality partition. If partition grows, introduce time bucket, sharding key, or additional partition component [S12].
3. Clustering columns define on-disk order within partition and must match range / ordering requirements.
4. Use SAI for specific column-level secondary search cases, not as a substitute for primary-key modeling [S13].
5. TTL must be modeled with tombstone and compaction impact. Mixing different TTLs or TTL/non-TTL in a partition can delay tombstone cleanup [S14][S15].

### Metrics

- partition size and row count distribution
- single-partition query ratio
- tombstones per read and tombstone warning count
- compaction backlog / pending tasks
- read/write latency p99 by table
- repair lag / consistency repair interval
- disk amplification and SSTable count

### Failure Modes

- **Large partition**: low-cardinality or time-unbounded partition causes read amplification [S12].
- **Tombstone accumulation**: deletes / TTL create tombstones that persist until compaction and grace rules allow removal [S14].
- **Secondary-index overuse**: index query becomes global or high fan-out.
- **Consistency mismatch**: application assumes strong read-after-write while consistency settings do not guarantee it.
- **Compaction debt**: write-heavy table cannot compact fast enough, increasing read cost.

### Anti-patterns

- Modeling Cassandra like relational tables and then joining in application code.
- Querying by non-primary-key fields without explicit index / duplication strategy.
- Using TTL on high-volume data without tombstone budget.
- Storing all tenant data under one partition key.
- Ignoring repair / gc_grace_seconds implications.

### Clone Implementation Guide

- Build one worksheet per query with partition key, clustering order, expected partition growth, and retention.
- Add `partition_budget.csv` with max rows, max bytes, max time window.
- Run tombstone tests for TTL-heavy tables before launch.
- Add compaction and repair dashboards as launch blockers.
- Create SAI approval rule: only when primary-key modeling cannot satisfy query and workload is measured.

### Confidence & Unknowns

- Confidence A: primary-key and TTL/tombstone behavior is direct official evidence [S12][S14][S15].
- Confidence B: exact partition-size thresholds depend on Cassandra version, hardware, compaction strategy, and latency SLO.

---

## 6.4 Layer 11.04 — Graph store

### Definition

Graph store は、domain entities as nodes、relationships as edges、properties、labels/types、graph constraints、graph indexes、traversal/query language を制御する層である。frontier design は、「関係を保存する」ではなく、「関係探索を低コストで開始・制限・説明可能にする」ことを目的にする。

### Frontier Exemplars

- **Neo4j**: property graph concept、index types、constraints、query tuning を体系化している [S16][S17][S18]。
- **ISO GQL**: property graph の構造・操作・照会言語の標準 [S19]。
- **W3C SPARQL / RDF**: RDF graph の標準 query language [S20]。

### Decision Model

| Field | Spec |
|---|---|
| Inputs | domain relationship map, path queries, graph density, edge directionality, relationship properties, integrity constraints |
| Decision Object | graph model + query language + index/constraint/traversal policy |
| Criteria | relationship centrality, traversal selectivity, path length, starting-node lookup, constraint enforceability, explainability |
| Priorities | model relationships as first-class; index traversal start points; constrain identities; bound path expansion; separate graph analytics from OLTP graph |
| Prohibitions | unbounded path queries; all-to-all relationships without selectivity; using graph store for simple key lookup only; missing uniqueness constraints |
| Thresholds | max traversal depth, expansion factor budget, path query timeout, graph density threshold, constraint violation SLO |
| Owners | graph modeler, domain architect, analytics owner, SRE |
| Cadence | graph model review per domain change; query-plan review before production; constraint/index review monthly |

### Technical / Business Specification

1. Create `graph_model.md` with node labels, relationship types, properties, uniqueness constraints, existence constraints, and canonical path queries.
2. For every production query, define starting node lookup and expected traversal depth. Query plan must show index use for start-point selection where applicable [S17].
3. Use constraints for identifiers and required properties to protect graph quality [S18].
4. Choose GQL/Cypher/SPARQL model based on graph type: property graph vs RDF / semantic web [S19][S20].
5. Maintain an expansion budget: if average degree or path count makes query explosive, add relationship type filters, time windows, direction, or precomputed projections.

### Metrics

- path query p95/p99 latency
- starting index usage ratio
- average and p99 expansion factor
- result cardinality per query
- constraint violation count
- graph density by label/type
- slow traversal count and timeout rate

### Failure Modes

- **Traversal explosion** from unbounded path patterns.
- **No indexed start point**, causing broad graph scans [S17].
- **Weak identity constraints**, causing duplicate nodes and broken relationships [S18].
- **Graph-for-everything**: graph store used for simple CRUD without relationship advantage.
- **Model drift**: multiple teams use different relationship types for the same domain relation.

### Anti-patterns

- Treating graph model as ER diagram with edge names but no query use cases.
- Allowing arbitrary-depth queries from user input.
- Creating full-text indexes to mask bad graph topology.
- No distinction between OLTP graph and offline graph analytics projection.

### Clone Implementation Guide

- Identify top 10 relationship-centric use cases: fraud ring, dependency impact, recommendation, entitlement, lineage, knowledge graph.
- Model only relationships that appear in path queries or integrity rules.
- Add constraints before bulk import.
- Add search-performance indexes for start nodes and high-selectivity predicates.
- Add query budget tests with worst-case high-degree nodes.

### Confidence & Unknowns

- Confidence A: property graph concepts, index types, constraints, and standards are directly supported [S16][S17][S18][S19][S20].
- Unknown: benchmark superiority vs relational alternatives is workload-specific and should be tested rather than asserted.

---

## 6.5 Layer 11.05 — Time-series store

### Definition

Time-series store は、timestamped measurements、tags/labels、fields/values、retention、shards/blocks、rollups/downsampling、write ingest、time-range query を制御する層である。frontier design では、time と cardinality が storage cost と query cost の第一級変数になる。

### Frontier Exemplars

- **InfluxDB**: buckets / measurements / tags / fields、shards、retention、TSM/TSI の説明が揃う [S21][S22][S23][S24][S25]。
- **Prometheus TSDB**: WAL、blocks、retention、observability metrics storage の reference [S26]。
- **MongoDB time series collections**: document store 側の time-series support として補助的に参照可能 [S11]。

### Decision Model

| Field | Spec |
|---|---|
| Inputs | metric/event type, timestamp precision, ingest rate, tag cardinality, query range, retention, rollup requirement, compliance |
| Decision Object | time-series schema + tag/field split + retention/shard/downsample policy |
| Criteria | write throughput, cardinality control, time-range query speed, compression, retention cost, downsample accuracy |
| Priorities | keep tags low-cardinality and queryable; keep fields as measured values; define retention per bucket; align shard duration with retention/query patterns |
| Prohibitions | unbounded high-cardinality labels such as user_id/request_id unless justified; embedding data attributes in measurement/table names; infinite retention by default |
| Thresholds | active series budget, tag cardinality budget, ingest QPS, retention days, shard/block size, query range SLO |
| Owners | observability owner, data platform SRE, cost owner, data governance owner |
| Cadence | cardinality review weekly for observability; retention review quarterly; rollup review per product analytics change |

### Technical / Business Specification

1. Define schema as `measurement/table + timestamp + tag set + field set`. Tags are for indexed filtering/grouping; fields are measured values [S21].
2. Assign every bucket/database a retention period. No time-series dataset should launch with infinite retention unless explicitly approved [S24][S26].
3. Set tag cardinality budgets per source. Block high-cardinality labels at ingestion when possible.
4. Use shard / block design aligned with time-range query and retention. InfluxDB organizes data into shards and shard groups [S22]; Prometheus local storage uses blocks and WAL [S26].
5. Define rollup/downsample artifacts for long-range dashboards to avoid querying raw high-frequency data.

### Metrics

- ingest points/sec
- active series count and label cardinality
- bytes per series / storage growth per day
- query latency by time range and predicate
- retention delete lag
- shard/block compaction lag
- WAL size / replay time
- dropped / rejected high-cardinality series

### Failure Modes

- **Cardinality explosion** from user_id, request_id, session_id labels.
- **Infinite retention** causing unbounded storage cost.
- **Misclassified tags/fields** causing either unqueryable dimensions or index bloat [S21].
- **Long raw queries** over months of high-frequency data.
- **Retention mismatch** where legal/audit needs exceed operational retention.

### Anti-patterns

- Treating time-series as document logs with arbitrary schema.
- Putting changing values in tag names or measurement names.
- Using raw metrics for long-range reports instead of rollups.
- Not budgeting WAL/replay/compaction under outage recovery.

### Clone Implementation Guide

- Create `timeseries_schema_registry.csv` with measurement, tags, fields, retention, rollup, owner.
- Add cardinality admission control for new labels/tags.
- Define tiered retention: hot raw, warm rollup, cold archive.
- Build dashboards for active series, top labels, ingestion QPS, retention lag.
- Add query guardrails: max range, max series, async export for heavy analytics.

### Confidence & Unknowns

- Confidence A: InfluxDB data model, shard, retention, TSM/TSI evidence is direct [S21][S22][S23][S24][S25].
- Confidence A: Prometheus storage and WAL/retention evidence is direct [S26].
- Unknown: exact cardinality budget must be set per backend and hardware/service tier.

---

## 6.6 Layer 11.06 — Search index

### Definition

Search index は、source-of-truth data から search-serving representation を構築し、documents、mappings、analyzers、shards、refresh、replicas、ranking、facets、vector fields、lifecycle を制御する層である。

### Frontier Exemplars

- **Elasticsearch**: index fundamentals、near-real-time search、merge settings を公式 docs が説明する [S27][S28][S29]。
- **Lucene**: inverted index / postings / term dictionary の core library [S30]。
- **OpenSearch**: inverted index と mappings の説明を公開する [S31]。

### Decision Model

| Field | Spec |
|---|---|
| Inputs | source entities, searchable fields, filter/sort/facet fields, language, freshness SLO, relevance goals, reindex cost |
| Decision Object | index schema + mapping/analyzer + shard/replica + refresh/merge policy + sync pipeline |
| Criteria | relevance, latency, freshness, write throughput, storage, shard balance, reindexability, source consistency |
| Priorities | explicit mappings; analyzer per language/use case; index only searched/sorted/aggregated fields; separate source-of-truth from index |
| Prohibitions | dynamic mapping without review for critical indexes; using search index as transaction source of truth; unlimited refresh frequency; uncontrolled shard count |
| Thresholds | refresh interval, acceptable indexing lag, shard size target, merge backlog, search p99, relevance threshold |
| Owners | search platform owner, relevance engineer, service owner, SRE |
| Cadence | mapping review before field launch; relevance review per release; shard/merge review monthly; full reindex test quarterly |

### Technical / Business Specification

1. Maintain `search_index_contract.yaml`: source entity, index fields, mapping, analyzer, relevance signals, refresh SLO, reindex procedure.
2. Mappings must define data type and indexing behavior for each field. Do not index fields that are not queried or aggregated [S27][S31].
3. Define refresh policy as product freshness SLO, not as “always immediate.” Elasticsearch is near-real-time because refresh makes new segments searchable, typically with a lag window [S28].
4. Define shard count and size target before launch. Over-sharding hurts memory and merge overhead; under-sharding limits parallelism.
5. Reindex must be safe: versioned index names + alias switch + backfill + validation + rollback.

### Metrics

- search p50/p95/p99 latency
- indexing throughput and queue depth
- refresh / indexing lag
- shard size and shard skew
- merge backlog and segment count
- query cache hit ratio
- relevance metrics: NDCG, MRR, CTR, zero-result rate
- failed reindex / mapping conflict count

### Failure Modes

- **Mapping explosion** from uncontrolled dynamic fields.
- **Relevance regression** from analyzer or scoring changes.
- **Refresh pressure** causing indexing throughput loss [S28].
- **Segment merge backlog** causing disk and CPU pressure [S29].
- **Stale index** when event sync misses source updates.

### Anti-patterns

- Indexing every field “just in case.”
- Using search index as primary transaction store.
- Changing analyzer without full reindex plan.
- Assuming keyword, text, date, numeric fields behave interchangeably.
- No alias-based migration.

### Clone Implementation Guide

- Create index contract for each search use case.
- Introduce mapping review gate and analyzer test corpus.
- Build sync pipeline with idempotent upsert/delete and dead-letter queue.
- Add reindex rehearsal and alias rollback procedure.
- Add relevance evaluation set before major ranking changes.

### Confidence & Unknowns

- Confidence A: index fundamentals, refresh, segment merge evidence is direct [S27][S28][S29].
- Confidence B: target shard size and refresh interval are workload-specific.

---

## 6.7 Layer 11.07 — Inverted index

### Definition

Inverted index は、token / term から document postings list へ lookup する information retrieval data structure を制御する層である。これは search index の物理・論理中核であり、analyzer、term dictionary、postings、positions、doc values、segments、merge、skip/scoring を含む。

### Frontier Exemplars

- **Apache Lucene**: postings と term dictionary を inverted index の中核として定義する [S30]。
- **Elasticsearch / OpenSearch**: Lucene segments、near-real-time refresh、inverted index の実用運用を提供する [S28][S29][S31]。

### Decision Model

| Field | Spec |
|---|---|
| Inputs | text fields, language, tokenization rules, phrase/proximity needs, filter fields, sort/aggregation needs, scoring model |
| Decision Object | analyzer chain + postings format + field indexing options + segment lifecycle |
| Criteria | token recall/precision, postings size, scoring speed, phrase query support, language handling, merge cost |
| Priorities | use analyzer that matches user query language; store positions only when needed; doc_values for sort/agg; minimize unnecessary indexed fields |
| Prohibitions | applying full-text analyzer to identifiers; keyword-only indexing for natural language; analyzer mismatch between index and query; no test corpus |
| Thresholds | index size per document, postings length, token count/document, merge latency, query CPU budget |
| Owners | IR/search engineer, relevance owner, platform SRE |
| Cadence | analyzer review per language/domain; token diff tests per release; segment/merge review monthly |

### Technical / Business Specification

1. Maintain analyzer test corpus with examples for identifiers, names, Japanese/English text, synonyms, stopwords, punctuation, numbers.
2. Decide field mode: `text`, `keyword`, numeric/date, vector, doc values, stored field. Each mode must map to query use.
3. Include positions/offsets only for phrase/highlight needs. Otherwise reduce index size.
4. Validate query analyzer and index analyzer alignment.
5. Track segment count and merge settings because immutable segments are periodically merged [S29].

### Metrics

- token count per document
- postings length by term
- index size / source size ratio
- top expensive terms
- phrase query latency
- segment count and merge time
- analyzer regression failures
- zero-result and over-result rates

### Failure Modes

- **Analyzer mismatch**: query terms do not match indexed terms.
- **Identifier splitting**: IDs or SKUs tokenized into useless parts.
- **Postings bloat**: high-frequency terms dominate memory/CPU.
- **Merge starvation**: too many small segments degrade performance [S29].
- **Scoring opacity**: ranking changes cannot be explained.

### Anti-patterns

- Treating inverted index as a black box.
- Using one analyzer for all fields and languages.
- Indexing raw logs with unlimited fields.
- Ignoring deleted-document and segment-merge cost.

### Clone Implementation Guide

- Build `field_indexing_matrix.csv` with analyzer, indexed?, stored?, doc_values?, positions?, query examples.
- Add analyzer golden tests and token snapshots.
- Add high-frequency term reports.
- Tune merge and refresh with production-like indexing load.
- Add relevance error taxonomy: no match, bad match, wrong ranking, stale index.

### Confidence & Unknowns

- Confidence A: Lucene postings / term dictionary and OpenSearch inverted-index explanation are direct [S30][S31].
- Unknown: codec-level choices and skip/scoring internals vary by Lucene version and deployment.

---

## 6.8 Layer 11.08 — Cache

### Definition

Cache は、origin data store / compute / API の repeated access を一時的に保存し、latency、throughput、availability、cost を最適化する層である。cache は source of truth ではなく、freshness と origin load の trade-off を持つ。

### Frontier Exemplars

- **Azure Cache-Aside pattern**: application が cache hit/miss と freshness を管理する pattern [S40]。
- **AWS Redis caching patterns**: cache-aside / lazy loading と write-through を整理する。ただし historical reference として扱う [S42]。
- **Redis / Memcached**: TTL、eviction、raw key-value item、LRU の実装面を持つ [S32][S33][S38][S39]。

### Decision Model

| Field | Spec |
|---|---|
| Inputs | repeated reads, origin latency/cost, data volatility, stale risk, serialization cost, memory budget, failure mode |
| Decision Object | cacheability contract + population strategy + eviction/TTL + origin fallback |
| Criteria | hit ratio, miss penalty, stale risk, origin offload, memory efficiency, operational simplicity |
| Priorities | cache read-heavy and repeatable data; define freshness; use explicit TTL; instrument miss path; protect origin under herd |
| Prohibitions | caching user-specific sensitive data without auth scope in key; caching mutable data with no invalidation/TTL; treating cache as durable |
| Thresholds | minimum hit ratio, maximum stale window, maximum origin QPS under miss storm, memory high-water mark, eviction budget |
| Owners | backend owner, SRE, security owner, data governance owner |
| Cadence | cache review per endpoint; hit/miss review weekly; stale incidents postmortem; TTL review monthly |

### Technical / Business Specification

1. For each cache object, define `cache_contract`: source, key, value schema, TTL, invalidation events, staleness tolerance, auth scope, fallback.
2. Select population strategy:
   - cache-aside for read-heavy unknown working set [S40][S42]
   - write-through when freshness and hit probability justify write overhead [S42]
   - refresh-ahead / prewarm only for predictable hot sets
3. Define eviction policy separate from TTL. TTL is freshness/lifecycle; eviction is memory pressure [S33][S44].
4. Add stampede protection: single-flight / lock with lock TTL / jitter / probabilistic early refresh. AWS cache validity docs support jitter as a TTL herd mitigation [S43].
5. Never cache without measuring hit ratio, miss penalty, and stale-read rate.

### Metrics

- hit ratio by key family
- miss rate and miss penalty latency
- origin QPS reduction
- stale read rate
- eviction rate and reason
- memory utilization and fragmentation
- serialization/deserialization time
- stampede events and lock wait time

### Failure Modes

- **Cache stampede** from synchronized expiration or cold start.
- **Stale data** from too-long TTL or missed invalidation [S40].
- **Origin overload** on cache outage.
- **Eviction churn** when memory policy removes hot data [S33][S44].
- **Security leakage** from missing tenant/user/auth scope in key.

### Anti-patterns

- “Cache everything” without hit-ratio proof.
- TTL as the only invalidation mechanism for high-risk mutable data.
- No fallback or circuit breaker when cache is unavailable.
- Serializing huge objects that are only partially used.
- Mixing user-specific and global data in same key namespace.

### Clone Implementation Guide

- Create cache-contract registry for top 20 high-QPS endpoints.
- Add cache-aside wrapper with metrics and single-flight.
- Add TTL jitter for all high-fanout keys.
- Add stale-risk classification: safe, tolerable, dangerous, prohibited.
- Add origin protection: rate limit, circuit breaker, fallback response.

### Confidence & Unknowns

- Confidence A: cache-aside and expiration guidance is direct [S40][S42].
- Confidence B: TTL jitter is supported by AWS guidance but implementation parameters are workload-specific [S43].

---

## 6.9 Layer 11.09 — Distributed cache

### Definition

Distributed cache は、multiple nodes / shards / replicas にまたがる cache placement、routing、resilience、failover、hot shard、multi-key constraints を制御する層である。

### Frontier Exemplars

- **Redis Cluster**: hash slots、hash tags、resharding、same-slot multi-key operation が公式に定義される [S34][S35]。
- **Azure caching guidance**: distributed cache が consistency / availability / partition trade-off を持つことを明示する [S41]。
- **Memcached**: simple distributed object cache として client-side routing / key protocol の基礎を持つ [S38][S39]。

### Decision Model

| Field | Spec |
|---|---|
| Inputs | key cardinality, node count, memory per node, multi-key operations, availability target, network topology, failover model |
| Decision Object | cache topology + key routing + replica/failover + multi-key policy |
| Criteria | balanced slots, low cross-node latency, failover speed, multi-key feasibility, hot-key mitigation, operational simplicity |
| Priorities | distribute by key; keep multi-key operations in same hash slot only when necessary; avoid hot tags; separate local and remote cache roles |
| Prohibitions | assuming strong consistency across partitions; using hash tags for broad co-location; no client support for MOVED/ASK or failover |
| Thresholds | max memory skew, hot shard QPS, failover RTO, cross-slot error rate, replication lag, node CPU/memory ceiling |
| Owners | platform SRE, cache operator, backend architect |
| Cadence | topology review monthly; resharding rehearsal quarterly; failover test quarterly |

### Technical / Business Specification

1. Maintain cluster topology registry: nodes, slots, replicas, endpoints, failover settings, scaling procedure.
2. For Redis Cluster, understand hash slots and hash tags; multi-key operations require keys in the same slot [S34][S35].
3. Key tags must be approved. Co-location improves multi-key operations but can create hot shards.
4. Define client requirements: cluster-aware client, retry policy, MOVED/ASK handling, timeout, backoff.
5. Separate L1 local cache and L2 distributed cache; define invalidation and fallback for both [S41].

### Metrics

- slot / memory / QPS distribution by node
- hot key and hot shard rate
- failover duration and error rate
- cross-slot errors
- cache client retry count
- replication lag
- node CPU / memory / network

### Failure Modes

- **Hot shard** due to hash tag or tenant-heavy key.
- **Cross-slot errors** from multi-key operation across slots [S34].
- **Failover storm** from client retry misconfiguration.
- **Stale local cache** when distributed invalidation is missed [S37].
- **Over-layering**: L1 + L2 + origin consistency becomes unmanageable [S41].

### Anti-patterns

- Using one hash tag per tenant without tenant load distribution analysis.
- Assuming a distributed cache is strongly consistent.
- Resharding without testing client behavior.
- Running multi-key scripts across arbitrary keys.
- No cold-start or node-loss origin protection.

### Clone Implementation Guide

- Build distributed cache design doc with slot/routing model.
- Add key heatmap dashboard by slot and key prefix.
- Add cluster-aware client policy template.
- Test failover, resharding, and cache outage under production-like load.
- Add hot-key mitigation: key splitting, local short TTL, request coalescing, partial materialization.

### Confidence & Unknowns

- Confidence A: Redis cluster constraints and hash tag behavior are directly documented [S34][S35].
- Confidence B: distributed consistency trade-off is supported by Azure guidance [S41], but exact semantics depend on cache engine and deployment.

---

## 6.10 Layer 11.10 — Cache key

### Definition

Cache key は、cache object の identity、namespace、tenant/auth isolation、versioning、dependency、invalidation addressability を制御する層である。良い cache key は「一意に取れる」だけでなく、「安全に失効できる」ことが条件である。

### Frontier Exemplars

- **Redis**: key expiration、cluster hash tags、client tracking が key identity と invalidation を operational object にする [S32][S34][S37]。
- **Memcached protocol**: key length and expiration contract が protocol-level に定義される [S39]。
- **AWS caching techniques**: SQL statement / customer ID / object key など keying technique の比較を示す [S42]。

### Decision Model

| Field | Spec |
|---|---|
| Inputs | request parameters, entity ID, tenant, locale, auth scope, feature flag, schema version, source version, dependency event |
| Decision Object | cache key schema + namespace + version + dependency model |
| Criteria | uniqueness, bounded cardinality, invalidatability, tenant isolation, observability, cluster distribution, key length |
| Priorities | encode all value-affecting dimensions; version key when schema/policy changes; keep key readable enough for ops; isolate tenants/users |
| Prohibitions | omitting auth/tenant/locale dimensions; using raw unbounded query strings; global keys for user-specific data; same hash tag for all keys |
| Thresholds | max key length, key cardinality per namespace, collision rate, orphan key age, invalidation coverage |
| Owners | backend owner, API owner, security owner, SRE |
| Cadence | key schema review per cache launch; namespace cleanup monthly; dependency audit quarterly |

### Technical / Business Specification

1. Standard key envelope: `{env}:{service}:{object}:{version}:{tenant_scope}:{identity}:{variant_hash}`.
2. For user-specific data, include tenant/user/auth-scope or do not cache.
3. For request-derived keys, canonicalize parameters: sorted query params, normalized locale, stable serialization, hash long variants.
4. Include schema version or policy version when value representation or authorization logic changes.
5. For Redis Cluster hash tags, only wrap the minimum co-location component, e.g. `cart:{tenant:user}:items`; avoid `{tenant}` alone if tenant can be hot [S34].
6. Maintain `cache_key_registry.csv` with namespace, pattern, owner, TTL, invalidation event, sample keys.

### Metrics

- key cardinality by namespace
- key collision / overwrite incidents
- orphan keys after invalidation
- invalidation coverage by event
- average and max key length
- top keys by QPS and memory
- keyspace scan sampling results

### Failure Modes

- **Key collision** returning wrong data.
- **Authorization leak** when auth scope is not part of key.
- **Unbounded cardinality** from raw query strings or timestamps.
- **Uninvalidatable key** because source dependency is not encoded.
- **Cluster hot slot** from over-broad hash tag [S34].

### Anti-patterns

- `cache:<url>` without canonicalization.
- `user:{id}` cache shared across permissions.
- Including current timestamp in key for every request.
- Storing key semantics only in application code with no registry.
- No version bump on value schema change.

### Clone Implementation Guide

- Create cache key naming standard and linter.
- Add key registry as a deployment artifact.
- Add canonicalization library for request-derived keys.
- Add namespace-level dashboards for cardinality and memory.
- Add invalidation integration tests that assert expected keys are removed.

### Confidence & Unknowns

- Confidence A: Redis hash tags / cluster constraints and Memcached key protocol are direct [S34][S39].
- Confidence B: exact key envelope is a transferable pattern inferred from cache design needs and provider constraints.

---

## 6.11 Layer 11.11 — Invalidation

### Definition

Invalidation は、source-of-truth update、delete、event、permission change、schema change、deployment、manual purge によって cache / local cache / search index / derived views を stale 状態から収束させる層である。

### Frontier Exemplars

- **Redis keyspace notifications**: key changes / expirations を Pub/Sub channels で受け取れる [S36]。
- **Redis client-side caching**: tracked keys の変更時に invalidation messages を送る [S37]。
- **Azure cache-aside**: application が cached data と underlying store の consistency strategy を実装する [S40]。

### Decision Model

| Field | Spec |
|---|---|
| Inputs | source change event, affected entity, cache key dependency, index document ID, local cache clients, TTL fallback, replay log |
| Decision Object | invalidation event map + dependency graph + delivery/replay/fallback policy |
| Criteria | correctness risk, latency, delivery reliability, idempotency, replayability, blast radius, operational override |
| Priorities | explicit event-to-key mapping; idempotent delete/update; TTL fallback; dead-letter and replay; measure stale reads |
| Prohibitions | relying on best-effort Pub/Sub alone for high-risk correctness; manual purge as normal path; no TTL fallback; no dependency registry |
| Thresholds | invalidation latency SLO, missed event budget, stale window, replay RTO, DLQ threshold |
| Owners | event platform owner, backend owner, search/cache owner, SRE |
| Cadence | invalidation map review per schema/event change; replay drill quarterly; stale incident postmortem |

### Technical / Business Specification

1. Create `invalidation_event_map.md`: source event → cache namespace / key pattern / search document / local cache channel.
2. Invalidation operations should be idempotent. Deleting an absent key must be safe.
3. Use durable event streams for high-risk invalidation. Redis keyspace notifications and Pub/Sub are useful signals, but correctness-critical workflows need replayable source events [S36][S37].
4. Add TTL fallback to every cache object. Invalidation failure should converge eventually [S32][S40].
5. For client-side caching, clients that receive invalidation messages must remove corresponding keys to avoid stale data [S37].
6. Add manual purge tools with audit logs and blast-radius controls.

### Metrics

- invalidation event latency p50/p99
- missed invalidation / stale-read incidents
- DLQ size and replay success
- keys removed per event
- local cache invalidation lag
- manual purge count
- source-to-index consistency lag

### Failure Modes

- **Missed event** leaves stale cache until TTL.
- **Non-durable Pub/Sub** loses invalidation under network/client outage.
- **Over-invalidation** removes too many keys and overloads origin.
- **Under-invalidation** misses variants such as locale/auth/version.
- **Circular dependency** where invalidation requires cached data to compute affected keys.

### Anti-patterns

- Invalidate by wildcard scans in production hot path.
- No replay path for cache/index updates.
- Treating key expiration event as a reliable business event.
- Using local in-memory cache with no server-assisted or event invalidation.
- Manual purge without audit.

### Clone Implementation Guide

- Inventory all source events and map affected cache/index objects.
- Add durable event stream or change data capture for high-risk invalidation.
- Add Redis keyspace notifications only as observability or low-risk trigger, not sole correctness mechanism unless accepted.
- Add integration tests: update source → expected cache key gone → next read fresh.
- Add stale-read synthetic checker.

### Confidence & Unknowns

- Confidence A: Redis keyspace notification and client-side invalidation behavior are direct [S36][S37].
- Confidence B: durable replay recommendation is inferred from delivery semantics and correctness needs; exact implementation depends on event platform.

---

## 6.12 Layer 11.12 — TTL

### Definition

TTL は、cache key、database item/document/column、session、lock、time-series point、search result、derived object の lifetime を明示し、自動 expiration / deletion / eviction / retention / compaction と接続する層である。

### Frontier Exemplars

- **Redis EXPIRE**: timeout 後に key が削除され、passive / active expiration がある [S32]。
- **DynamoDB TTL**: per-item expiration timestamp による自動削除 [S06]。
- **MongoDB TTL index**: document expiration for logs/session/event data [S11]。
- **Cassandra TTL**: inserted values に TTL を指定し、expiration 後は tombstone になる [S14][S15]。
- **InfluxDB retention**: bucket retention に基づく expired data deletion [S24]。
- **Memcached protocol**: expiration time 0 / 30-day behavior が protocol にある [S39]。

### Decision Model

| Field | Spec |
|---|---|
| Inputs | data volatility, stale tolerance, legal retention, cost target, origin load, deletion semantics, clock source, compaction/eviction side effects |
| Decision Object | TTL / retention / expiration policy + jitter + exception table |
| Criteria | freshness, storage reduction, origin protection, deletion correctness, operational side effects, auditability |
| Priorities | set TTL for ephemeral data; align TTL to change rate and stale risk; add jitter for hot synchronized keys; document no-expiry exceptions |
| Prohibitions | default infinite lifetime for ephemeral/cache data; TTL for regulated records without archive/legal review; TTL shorter than refresh/recompute latency; lock TTL absent |
| Thresholds | TTL min/max by class, jitter percentage/range, deletion lag, tombstone budget, retention period, stale window |
| Owners | data governance owner, service owner, SRE, security/privacy owner |
| Cadence | TTL policy review quarterly; expired-data audit monthly; incident review after stale/delete errors |

### Technical / Business Specification

1. Classify every object: source-of-truth, derived, cache, session, lock, metric, log, audit, PII, regulated.
2. Define TTL class table:
   - lock: seconds, must include owner token and safe release
   - cache: seconds/minutes/hours, add jitter for hot keys [S43]
   - session: business/security policy
   - log/metric: retention period with archive/rollup [S24][S26]
   - document/item cleanup: TTL field/index and delete lag [S06][S11]
3. Distinguish TTL, eviction, retention, and deletion. Eviction can remove valid data due to memory pressure; TTL/retention remove expired data by policy [S33][S44].
4. For Cassandra, TTL is not free cleanup: it creates tombstones and interacts with compaction [S14][S15].
5. For Memcached, understand expiration time semantics: 0 never expires; values up to 30 days are relative seconds; above that are treated as Unix time [S39].
6. For Redis, use TTL/EXPIRE introspection and conditional expiration options when extending or shortening lifetimes [S32].

### Metrics

- expired object count by class
- deletion / expiry lag
- stale read rate after TTL
- TTL herd events and origin spike correlation
- storage reduction from TTL
- tombstone count / compaction backlog
- no-expiry object count
- lock expiry / orphan lock incidents

### Failure Modes

- **TTL herd**: many hot keys expire simultaneously, overloading origin [S43].
- **Premature expiry**: TTL too short causes continual origin fetch [S40].
- **Stale extension**: TTL too long or refreshed incorrectly returns outdated data.
- **Tombstone overload**: TTL-heavy Cassandra tables create read/compaction pressure [S14].
- **Compliance deletion error**: TTL deletes data that should have been retained or archived.
- **Eviction mistaken for expiry**: data disappears under memory pressure despite valid TTL [S33][S44].

### Anti-patterns

- Same TTL for all cache keys.
- No jitter for high-QPS hot keys.
- TTL used as the only business workflow trigger.
- No TTL on locks.
- Infinite TTL on sessions, feature flags, or ephemeral objects.
- TTL values hidden in application code rather than registry.

### Clone Implementation Guide

- Create `ttl_policy.yaml` with object class, TTL, jitter, owner, source, archive, legal notes.
- Add TTL linting to cache/database write paths.
- Add dashboards for no-expiry keys, expired-but-not-deleted items, tombstones, and origin spikes after expiry.
- Add synthetic tests for expiration behavior across Redis, Memcached, DynamoDB, MongoDB, Cassandra, InfluxDB.
- Add quarterly policy review with security/privacy/cost owners.

### Confidence & Unknowns

- Confidence A: TTL behavior is direct across Redis, DynamoDB, MongoDB, Cassandra, InfluxDB, Memcached [S06][S11][S14][S15][S24][S32][S39].
- Confidence B: jitter ranges and stale windows are workload-specific and require empirical tuning.

---

## 7. Integrated Operating Model

### 7.1 Roles

| Role | Responsibilities |
|---|---|
| Data platform architect | Store selection, key/partition/shard strategy, data lifecycle architecture. |
| Service owner | Access pattern inventory, schema ownership, cache contract, operational SLO. |
| Search platform owner | Search index contracts, mappings, analyzers, reindex, relevance evaluation. |
| Cache operator / platform SRE | Redis/Memcached topology, eviction, memory, failover, client policy. |
| Data governance / security owner | TTL / retention / privacy / audit classification and exceptions. |
| Observability owner | Time-series schema, cardinality budget, retention, dashboard performance. |
| Cost owner | Storage/index/cache/memory cost budgets and optimization cadence. |

### 7.2 Required Artifacts

| Artifact | Purpose | Required Fields |
|---|---|---|
| `access_patterns.yaml` | Non-relational schema の starting point | operation, predicates, sort/range, QPS, consistency, SLA, owner |
| `key_schema_registry.csv` | KV / cache / shard key governance | namespace, pattern, tenant scope, cardinality, version, owner |
| `document_schema.md` | Document modeling contract | fields, embedded refs, indexes, shard key, TTL, migrations |
| `wide_column_table_specs/` | Cassandra table-per-query contract | query, partition key, clustering, TTL, compaction, consistency |
| `graph_model.md` | Graph topology and traversal contract | node labels, relationship types, properties, constraints, indexes |
| `timeseries_schema_registry.csv` | Time-series cardinality and retention control | measurement, tags, fields, retention, rollup, owner |
| `search_index_contract.yaml` | Search serving contract | source, mapping, analyzer, refresh, shard, relevance, reindex |
| `field_indexing_matrix.csv` | Inverted-index field-level decision | field, analyzer, indexed, doc_values, stored, positions, query |
| `cache_contracts.yaml` | Cache safety contract | key, value schema, TTL, jitter, invalidation, stale policy |
| `invalidation_event_map.md` | Source changes to derived objects | event, affected keys/index docs, delivery, replay, fallback |
| `ttl_policy.yaml` | Expiration and retention governance | class, TTL, jitter, archive, deletion semantics, owner |
| `slo_dashboards` | Continuous verification | latency, hit ratio, lag, tombstones, shards, cardinality, eviction |

### 7.3 Review Cadence

| Review | Cadence | Gate Criteria |
|---|---|---|
| Access pattern review | Before new entity/index/cache launch | All critical operations mapped; no scan-only OLTP path. |
| Key / shard review | Before scale-out and monthly | Cardinality, distribution, hot-key tests complete. |
| Index review | Monthly | Every index has owner, query, last-used evidence, retirement rule. |
| TTL / retention review | Quarterly | No orphan no-expiry objects; legal exceptions documented. |
| Cache safety review | Monthly for high-QPS services | hit ratio, stale risk, origin protection, invalidation coverage measured. |
| Search relevance review | Per release | Analyzer diff and relevance regression passed. |
| Failure drill | Quarterly | cache outage, node failover, reindex rollback, invalidation replay tested. |

---

## 8. Maturity Model

| Level | Name | Criteria |
|---:|---|---|
| 0 | 未整備 | Store / cache / index が個別実装で、key schema、TTL、index owner、retention が不明。 |
| 1 | 個人依存 | 一部の担当者が key / index / cache を把握しているが registry や review gate がない。 |
| 2 | 文書化 | access patterns、key schema、index catalog、TTL policy が文書化されている。 |
| 3 | 標準化 | 新規 store/index/cache は design review を通過し、metrics / owner / SLO が必須。 |
| 4 | 自動化・計測 | key linting、index drift detection、TTL dashboards、cardinality guard、stale checker、reindex pipeline がある。 |
| 5 | 自律改善・業界先端 | workload telemetry から key/index/cache/TTL を継続最適化し、失敗予兆を検出して自動緩和する。 |

---

## 9. Pattern Library

| Pattern ID | Pattern | Layers | Description | Preconditions | Trade-offs | Confidence |
|---|---|---|---|---|---|---|
| P01 | Access-pattern-first schema | 11.01,11.02,11.03 | Query/read/write から key, document, table を決める。 | Access pattern inventory exists. | Denormalization and duplication increase write complexity. | A |
| P02 | High-cardinality distribution key | 11.01,11.02,11.03,11.09 | Partition/shard/slot の負荷を分散する key を選ぶ。 | Production-like key distribution known. | Query locality may decline. | A |
| P03 | Bounded partition/window | 11.03,11.05 | Time bucket or sharding key to keep partitions/shards bounded. | Time or tenant growth forecast exists. | More queries may need multiple buckets. | B |
| P04 | Workload-owned index catalog | 11.02,11.04,11.06,11.07 | Index must map to an owned query and measurable benefit. | Query telemetry exists. | Governance overhead. | A |
| P05 | Alias-based reindex | 11.06,11.07 | Versioned index + alias switch + rollback. | Search index supports aliases or routing indirection. | Requires duplicate storage during migration. | B |
| P06 | TTL + jitter | 11.08,11.12 | Add randomized TTL offset to reduce synchronized expiry. | Cache keys are hot enough to create herd risk. | Slightly variable freshness. | B |
| P07 | Durable invalidation + TTL fallback | 11.11,11.12 | Replayable events handle correctness; TTL handles eventual convergence. | Source change events available. | More infrastructure than Pub/Sub only. | B |
| P08 | Client-side cache with server invalidation | 11.08,11.11 | Local cache gets invalidation messages from Redis tracking. | Clients support tracking protocol. | More invalidation traffic and client complexity. | A |
| P09 | Tag cardinality budget | 11.05 | Limit time-series tags/labels to prevent series explosion. | Observability schema registry exists. | Some dimensions move to logs/traces, not metrics. | A |
| P10 | Same-slot hash tag for atomic multi-key | 11.09,11.10 | Redis hash tag co-locates keys needed by one operation. | Multi-key operation is required. | Hot slot risk if overused. | A |

---

## 10. Failure Modes and Anti-patterns Matrix

| Failure / Anti-pattern | Primary Layers | Detection Signal | Prevention / Control | Sources |
|---|---|---|---|---|
| Hot partition / hot key | 11.01,11.03,11.09,11.10 | partition QPS skew, throttling, p99 spikes | high-cardinality key, random suffix, key heatmap, load test | [S03][S34][S35] |
| Large partition | 11.03 | partition bytes/rows p99, slow reads | add time bucket / sharding key / query split | [S12] |
| Tombstone overload | 11.03,11.12 | tombstones/read, compaction backlog | TTL budget, compaction strategy, avoid mixed TTLs | [S14][S15] |
| Document over-embedding | 11.02 | document size growth, update latency | embed only bounded read-together data | [S07][S08] |
| Low-cardinality shard key | 11.02 | shard skew, jumbo chunks, scatter-gather | cardinality and distribution scoring | [S10] |
| Index sprawl | 11.02,11.06,11.07 | write latency, index storage, unused indexes | index catalog, last-used review, workload ownership | [S09][S27] |
| Analyzer mismatch | 11.06,11.07 | zero-result rate, token diff failures | analyzer corpus, query/index analyzer tests | [S30][S31] |
| Segment merge backlog | 11.06,11.07 | segment count, merge CPU/disk | refresh/merge tuning, shard sizing | [S28][S29] |
| Time-series cardinality explosion | 11.05 | active series growth, memory/storage spike | tag budget, label admission control | [S21][S26] |
| Infinite retention | 11.05,11.12 | storage growth, no retention policy | retention policy and archive/rollup | [S24][S26] |
| Cache stampede / TTL herd | 11.08,11.12 | miss storm, origin QPS spike | TTL jitter, single-flight, refresh-ahead | [S40][S43] |
| Stale cache | 11.08,11.11,11.12 | stale-read incidents, late invalidation | durable invalidation, TTL fallback, client tracking | [S37][S40] |
| Eviction mistaken for expiration | 11.08,11.12 | memory pressure evictions | separate TTL policy from eviction policy | [S33][S44] |
| Cross-slot multi-key error | 11.09,11.10 | Redis CROSSSLOT errors | hash tag only for required co-location | [S34][S35] |
| Authorization leak through key | 11.10 | cache returns data across auth scope | include tenant/user/auth/version in key | [S39][S40] |

---

## 11. Clone Implementation Plan

### Phase 1 — Inventory and classification

1. Inventory all non-relational stores, search indexes, caches, and TTL/retention mechanisms.
2. Classify each object as source-of-truth, derived, cache, index, metric, log, session, lock, or temporary artifact.
3. Capture top access patterns by service and rank by QPS, latency, cost, risk.
4. Create initial registries: key schema, document schema, table-per-query, graph model, time-series schema, search index, cache contract, TTL policy.

### Phase 2 — Decision gates

1. Introduce design review questions:
   - What query/access pattern owns this key/index/table/cache?
   - What is the distribution/cardinality proof?
   - What is the lifecycle policy?
   - What is the invalidation path?
   - What is the failure mode and rollback?
2. Add mandatory fields to design docs: owner, SLO, metrics, source references, migration plan.
3. Reject designs that rely on scan, unbounded partition, global hot key, unknown TTL, or unowned index.

### Phase 3 — Instrumentation

1. Build dashboards for p99 latency, hot keys, partition skew, shard balance, active series, index lag, cache hit ratio, stale read, evictions, TTL deletion lag.
2. Add synthetic checkers:
   - source update → cache invalidated
   - search index eventually consistent within SLO
   - TTL object expires within expected lag
   - high-cardinality tag blocked
3. Add index and key linting to CI/CD.

### Phase 4 — Migration and optimization

1. Start with one high-QPS service and one search index.
2. Refactor key schema or cache key only through versioned rollout.
3. Apply alias-based search reindex for schema/analyzer changes.
4. Add TTL jitter and single-flight to hot cache paths.
5. Run quarterly failure drills: cache outage, search reindex rollback, invalidation replay, hot-partition load test.

---

## 12. Validation Queries

Use these queries to challenge the Clone Spec and detect missing evidence.

```text
site:docs.aws.amazon.com/amazondynamodb "hot partitions" "partition key"
site:docs.aws.amazon.com/amazondynamodb "Time to Live" "within a few days"
site:mongodb.com/docs "Choose a Shard Key" "cardinality"
site:mongodb.com/docs "TTL indexes" "automatically remove documents"
site:cassandra.apache.org/doc "TTL" "tombstone" "compaction"
site:cassandra.apache.org/doc "primary key" "partition" "read"
site:neo4j.com/docs "search-performance indexes" "planner"
site:iso.org "ISO/IEC 39075" "property graphs"
site:docs.influxdata.com "retention" "shard" "bucket"
site:prometheus.io/docs/prometheus/latest/storage "WAL" "retention"
site:elastic.co/docs "near real-time search" "segment"
site:lucene.apache.org/core "postings" "term dictionary"
site:docs.opensearch.org "inverted index" "mappings"
site:redis.io/docs "EXPIRE" "passive" "active"
site:redis.io/docs "cluster" "hash tags" "same hash slot"
site:redis.io/docs "client-side caching" "invalidation messages"
site:docs.memcached.org/protocols/basic "expiration time" "30 days"
site:learn.microsoft.com/azure/architecture/patterns "cache-aside" "expiration"
"cache stampede" "TTL jitter" Redis official OR AWS
"Cassandra tombstone" "TTL" "incident" OR "postmortem"
"Elasticsearch mapping explosion" "incident" OR "postmortem"
"Prometheus high cardinality" "incident" OR "postmortem"
"Redis hot key" "incident" OR "postmortem"
"DynamoDB hot partition" "incident" OR "postmortem"
```

---

## 13. QA Checklist

| Check | Pass Condition |
|---|---|
| Coverage | All 12 requested layers have definition, decision model, metrics, failures, implementation guide. |
| Primary evidence | Each critical claim has official/standard/OSS documentation source. |
| A/B confidence | Core clone decisions rely on A/B claims only. |
| Source freshness | Current docs preferred. Historical AWS whitepaper pages are explicitly marked historical. |
| Failure coverage | Hot partition, tombstone, shard skew, index bloat, stale cache, TTL herd, invalidation miss covered. |
| Artifact readiness | Required registries and dashboards are specified. |
| Transferability | Product-specific behavior is separated from general pattern. |
| Unknowns | Workload-specific thresholds are not overclaimed; empirical load tests required. |

---

## 14. Practical Defaults for a New Organization

These are initial defaults, not universal truths. Tune with production telemetry.

| Control | Default Starting Point | When to Change |
|---|---|---|
| KV key schema | access-pattern-first, high-cardinality partition key, versioned value envelope | when hot partitions or missing access pattern appear |
| Document embedding | embed bounded read-together subdocuments | when child set grows unbounded or updates independently |
| Wide-column partition | partition by entity + time bucket when data grows over time | when partition p99 grows or queries need multi-bucket scans |
| Graph traversal | require indexed start node and max traversal depth | when domain requires exploratory analytics; move to graph analytics projection |
| Time-series tags | only dimensions used for filtering/grouping, cardinality budget required | when dashboard needs new dimension; review as schema change |
| Search refresh | product freshness SLO, not immediate by default | when user-facing freshness must be near real-time |
| Cache strategy | cache-aside with TTL + jitter + single-flight for hot paths | when writes dominate or freshness requires write-through/invalidation |
| Distributed cache | cluster-aware client; key heatmap; hash tags by exception | when multi-key atomicity is required and hot-slot risk accepted |
| Cache key | include env/service/object/version/tenant/auth/variant hash | when data is global and safe to share, omit scoped components deliberately |
| Invalidation | durable source event + idempotent delete/update + TTL fallback | when low-risk data can tolerate TTL-only freshness |
| TTL | classify object, set TTL, add jitter for hot cache keys | when legal retention or source-of-truth requirements prohibit deletion |

---

## 15. Confidence Summary

| Confidence | Claims |
|---|---|
| A | DynamoDB key/value/document model, partition keys, GSIs, TTL; MongoDB embedding/shard key/TTL indexes; Cassandra primary keys/TTL tombstones; Neo4j graph/index/constraint; InfluxDB bucket/shard/retention/TSM/TSI; Lucene postings/inverted index; Redis EXPIRE/cluster/keyspace/client invalidation; Memcached protocol expiration. |
| B | Cross-product clone patterns: access-pattern-first, TTL+jitter, durable invalidation + TTL fallback, index catalog governance, tag cardinality budgets. These are strongly supported by multiple official source families but require local tuning. |
| C | Exact numeric thresholds such as max partition size, ideal shard size, refresh interval, TTL ranges, cache hit-ratio targets. These are intentionally left as empirical choices. |
| D | Claims about a specific vendor being universally superior. Not adopted. |
| X | Non-public/internal architecture claims, leaked material, or unverified third-party performance assertions. Rejected. |
