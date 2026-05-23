# Frontier Operating Model Research: ランタイム・言語実行基盤（Layers 16）

生成日: 2026-05-13（JST）  
調査範囲: language runtime、VM runtime、interpreter、compiler、standard library、package manager、dependency resolver、GC、thread/connection pool、async/process runtime、memory allocation  
調査方針: 公開情報のみ。標準・公式ドキュメント・公式API文書・OSSリポジトリ/開発ガイド・リリース/設計文書・失敗/例外情報を優先し、主張を Decision Model に正規化した。

## 0. 正規化メモ

ユーザー提示表では 16 の個別レイヤー名が明示されていないため、本成果物では 14 レイヤーを次のように正規化した。16.08 は、package manager と dependency resolver の間に実務上必須となる「package metadata / lockfile」層として補完した。

| Layer ID | 正規化レイヤー名 | 主な対象 |
|---|---|---|
| 16.01 | 言語ランタイム全体 | object model、runtime API、runtime configuration、diagnostics、compatibility |
| 16.02 | VM ランタイム | VM lifecycle、class/module loading、verification、VM flags、thread/sync、fatal handling |
| 16.03 | インタプリタ | bytecode/AST execution、frame model、dispatch、debug/profiling hooks |
| 16.04 | コンパイラ | frontend、type checking、IR、optimization、code generation、diagnostics |
| 16.05 | Bytecode / JIT / AOT 実行パイプライン | tiered execution、profiling、deoptimization、AOT/JIT gates |
| 16.06 | 標準ライブラリ | foundational APIs、portability、stability、stdlib inclusion policy |
| 16.07 | パッケージマネージャ | install/build/publish、registry access、cache、workspace、scripts |
| 16.08 | パッケージメタデータ / Lockfile | manifest schema、semantic versioning、checksum、reproducible install |
| 16.09 | 依存リゾルバ | constraint solving、backtracking、minimum-version selection、conflict reporting |
| 16.10 | Garbage Collection | memory reclamation、pause/throughput trade-off、heap goal、debug/tuning |
| 16.11 | Memory Allocation | size classes、thread/CPU-local cache、fragmentation、allocator hooks |
| 16.12 | Thread Pool / Scheduler | bounded execution、work stealing、blocking offload、queue/rejection policy |
| 16.13 | Connection Pool | connection lifecycle、borrow/return、health check、keepalive、leak detection |
| 16.14 | Async / Process Runtime | event loop、non-blocking I/O、timers、signals、child process lifecycle |

## 1. Executive Summary

ランタイム・言語実行基盤の frontier pattern は、「言語仕様・実行性能・メモリ/並行性制約・パッケージ供給網を、一つの運用可能な contract として管理する」ことである。トップ候補は OpenJDK/HotSpot、CPython/PyPA/pip、Go toolchain/runtime、Rust/rustc/Cargo/Tokio、V8/Node/libuv、LLVM/Clang、TCMalloc/jemalloc/mimalloc、HikariCP である。

主要な結論は次の通りである。

1. **実行基盤は runtime API ではなく governance surface である。** HotSpot は VM lifecycle、class loading、bytecode verifier、CDS、interpreter、exception handling、synchronization、thread management、C++ heap management、JNI、fatal error handling を runtime の主要領域として明示する。Go runtime は goroutine/type information と環境変数による runtime 制御を公開し、V8 は JS/Wasm 実行、コンパイル、メモリ割当、GC を runtime の一部として扱う。[S001][S011][S022]
2. **先端 runtime は単一の実行方式に依存せず、interpreter / baseline / optimizing / AOT の tiered pipeline を設計対象にする。** V8 は Ignition、Sparkplug、Maglev、TurboFan の tiering を説明し、CPython は 3.13 で experimental JIT build option を導入し、JDK 25 は AOT 関連 feature を含む。JIT/AOT は性能機能ではなく、rollback、flag、deoptimization、profiling、security policy を含む運用対象である。[S023][S010][S041]
3. **コンパイラは source-to-code の実装ではなく、IR・verifier・pass governance の体系である。** LLVM IR は SSA-based、type-safe、low-level の common code representation であり、verifier で well-formedness を検査する。Go compiler は parse/typecheck/IR/middle-end/backend を分離し、CPython も tokenize/parse/AST/CFG/bytecode へ段階化する。[S040][S042][S006]
4. **パッケージエコシステムでは、resolver の「正解」よりも reproducibility と conflict explainability が重要である。** Cargo は dependency resolution を primary task とし結果を Cargo.lock に保存するが、単一の最善解はなく constraints と heuristics で解く。pip は backtracking resolver を説明し、Go は MVS により build list を決定する。npm package-lock は exact tree と integrity metadata を保持する。[S018][S031][S013][S030]
5. **GC・allocator・thread/connection pool は性能最適化ではなく SLO 管理である。** Go GC は memory allocation / recycling の cost model と GOGC/GOMEMLIMIT を公開する。V8 Orinoco は stop-the-world GC が jank、latency、throughput degradation を生むことを背景に parallel/concurrent/incremental GC を説明する。TCMalloc は per-thread/per-CPU cache、jemalloc は fragmentation avoidance and scalable concurrency、mimalloc は free-list sharding と eager page purging を掲げる。ThreadPoolExecutor、libuv、Tokio、HikariCP は bounded execution / resource pooling を公開運用面にしている。[S012][S024][S033][S034][S035][S038][S027][S028][S037]

## 2. Frontier Exemplars / Candidate Scores

| Candidate | 主対象レイヤー | 採用理由 | Score |
|---|---:|---|---:|
| OpenJDK / HotSpot / Java SE | 16.01, 16.02, 16.05, 16.06, 16.10, 16.12 | VM runtime の公開設計領域、Java SE API、JEP release process、長期運用実績が揃う。 | 94 |
| Go toolchain / runtime / modules | 16.01, 16.04, 16.09, 16.10, 16.11, 16.12 | runtime knobs、GC guide、MVS、compiler pipeline、allocator source が公式公開されている。 | 92 |
| Rust / rustc / Cargo / Tokio | 16.04, 16.06, 16.07, 16.08, 16.09, 16.11, 16.12, 16.14 | rustc book/dev guide、Cargo resolver/manifest/registry、std docs、Tokio runtime docs が揃う。 | 91 |
| V8 / Node.js / libuv | 16.01, 16.03, 16.05, 16.10, 16.12, 16.14 | JS/Wasm engine、tiered JIT、GC blog、event loop、thread pool、process/I/O runtime が公開されている。 | 90 |
| CPython / PyPA / pip | 16.01, 16.03, 16.04, 16.06, 16.08, 16.09, 16.10, 16.11 | devguide、InternalDocs、memory/GC API、PEP 703、pip resolver、packaging specs が揃う。 | 89 |
| LLVM / Clang | 16.04, 16.05 | IR、verifier、target-independent code generation、compiler frontend の規範性が高い。 | 89 |
| TCMalloc / jemalloc / mimalloc | 16.11 | allocator design、fragmentation/concurrency/security trade-off が明確。 | 86 |
| HikariCP | 16.13 | JDBC connection pool の公開実装・設定・失敗条件が明確。 | 78 |

Scoring: Performance 25 / Adoption 15 / Artifact Richness 20 / Peer Validation 15 / Recency 10 / Transferability 10 / Failure Evidence 5 を 100 点換算。公開成果物の厚みを重視し、内部運用の推測は加点していない。

## 3. Evidence Map

| Claim ID | 主張 | Evidence | Directness | Confidence |
|---|---|---|---|---|
| C01 | VM/runtime は lifecycle、option、loading、verification、interpreter、exception/synchronization/thread/memory/fatal handling を統合管理する。 | HotSpot Runtime Overview [S001]、Go runtime docs [S011]、V8 docs [S022] | Direct | A |
| C02 | 言語実行基盤は release governance を持ち、feature freeze / release candidate / late enhancement gate を明示すべきである。 | OpenJDK JEP 3 [S003]、OpenJDK JDK project [S039] | Direct | A |
| C03 | Interpreter / baseline / optimizing compiler / AOT は単なる性能階層ではなく、profiling、rollback、deoptimization、security gate を伴う decision object である。 | V8 Maglev [S023]、CPython JIT option [S010]、JDK 25 project [S041] | Near direct | B |
| C04 | Compiler は IR と verifier を中核にし、frontend/middle/backend の責務境界を明示するほど移植性と検証性が上がる。 | LLVM LangRef [S040]、LLVM CodeGenerator [S043]、Go compiler README [S042]、CPython compiler docs [S006] | Direct | A |
| C05 | Standard library は “portable foundation” と “core platform API” の境界を定義し、エコシステム全体の互換性 contract になる。 | Java SE API [S004]、Python stdlib [S009]、Rust std [S021] | Direct | A |
| C06 | Package manager は install/build/publish よりも、manifest、registry、cache、lockfile、integrity、workspace を統合する供給網 runtime として設計する。 | Cargo manifest/registries [S019][S020]、npm package.json/package-lock [S030][S044]、Go modules [S013] | Direct | A |
| C07 | Dependency resolver は constraints と heuristics/backtracking/MVS を明示し、conflict explanation と deterministic outcome を運用指標にする。 | Cargo resolver [S018]、pip resolver [S031]、Go modules [S013]、uv resolver [S032] | Direct | A |
| C08 | GC は throughput、pause、heap footprint、memory limit、debugging の SLO surface であり、言語 semantics から独立しない。 | Go GC guide/runtime [S012][S011]、Python gc [S008]、V8 Orinoco [S024] | Direct | A |
| C09 | Allocator は lock contention、fragmentation、cache locality、secure mode、stats を制御する runtime subsystem である。 | TCMalloc [S033]、jemalloc [S034]、mimalloc [S035]、Go malloc [S015]、Rust GlobalAlloc [S036]、Python memory API [S007] | Direct | A |
| C10 | Thread pool/scheduler は bounded execution、queueing、blocking offload、work stealing、rejection/backpressure を明示する必要がある。 | Java ThreadPoolExecutor [S038]、libuv threadpool [S027]、Tokio runtime [S029] | Direct | A |
| C11 | Connection pool は database/network 接続の SLO object であり、keepalive、lifetime、validation、leak detection、max connections の設計が必要である。 | HikariCP [S037]、Java SQL API [S004] | Near direct | B |
| C12 | Async/process runtime は event loop、OS event queue、timers、I/O、signals、child processes、blocking task isolation を一体管理する。 | Node event loop [S025]、libuv features [S026]、Tokio runtime [S028] | Direct | A |

## 4. Source Catalog

| Source ID | Entity | Source | Tier | Access | Key facts used |
|---|---|---|---|---|---|
| S001 | OpenJDK HotSpot | HotSpot Runtime Overview, https://openjdk.org/groups/hotspot/docs/RuntimeOverview.html | T0/T3 | HTML | HotSpot runtime subsystems: command-line options, lifecycle, class loading, verifier, CDS, interpreter, exceptions, synchronization, thread management, C++ heap management, JNI, fatal errors. |
| S002 | OpenJDK | OpenJDK Developers’ Guide, https://openjdk.org/guide/ | T3 | HTML | Contribution guide, standard flows, JEP references, roles such as Author/Committer/Reviewer. |
| S003 | OpenJDK | JEP 3: JDK Release Process, https://openjdk.org/jeps/3 | T0/T3 | HTML | Six-month feature release cycle, RDP phases, release candidate rules, late enhancement gate. |
| S004 | Oracle / Java SE | Java SE 25 & JDK 25 API, https://docs.oracle.com/en/java/javase/25/docs/api/index.html | T0 | HTML | Java SE API modules, java.base as foundational API, JDK-specific APIs. |
| S005 | Python | Python Developer’s Guide, https://devguide.python.org/ | T3 | HTML | CPython reference interpreter contribution and development guide. |
| S006 | CPython | InternalDocs/compiler.md, https://github.com/python/cpython/blob/main/InternalDocs/compiler.md | T2/T3 | GitHub | Source-to-bytecode pipeline: tokenize, parse AST, transform AST, CFG/optimize, emit bytecode. |
| S007 | Python | Memory Management C API, https://docs.python.org/3/c-api/memory.html | T0/T2 | HTML | Python private heap, allocators, object-specific allocation, extension safety. |
| S008 | Python | gc module, https://docs.python.org/3/library/gc.html | T0/T2 | HTML | Optional GC over reference counting, disable/tune/debug, version changes. |
| S009 | Python | The Python Standard Library, https://docs.python.org/3/library/ | T0 | HTML | Standard library distributed with Python, built-in and Python modules, portability. |
| S010 | Python | What’s New in Python 3.13, https://docs.python.org/3/whatsnew/3.13.html | T3 | HTML | Experimental JIT compiler build option. |
| S011 | Go | package runtime, https://pkg.go.dev/runtime | T0/T2 | HTML | Runtime package, goroutines/type info, GOGC and GOMEMLIMIT env vars. |
| S012 | Go | A Guide to the Go Garbage Collector, https://go.dev/doc/gc-guide | T0/T3 | HTML | Go memory allocation/recycling model, GC guide for advanced users, stack vs heap. |
| S013 | Go | Go Modules Reference, https://go.dev/ref/mod | T0/T2 | HTML | MVS, build list, go.mod, module cache, checksum verification, vendoring. |
| S014 | Go | go.mod file reference, https://go.dev/doc/modules/gomod-ref | T0 | HTML | go.mod module path, minimum Go version, dependencies, replace/exclude. |
| S015 | Go | runtime/malloc.go, https://go.dev/src/runtime/malloc.go | T2 | Source | Allocator based on TCMalloc, size classes, mheap/mspan/mcentral/mcache, per-P cache. |
| S016 | Rust | rustc book, https://doc.rust-lang.org/rustc/what-is-rustc.html | T0/T3 | HTML | rustc as compiler, crate as translation unit, Cargo invocation. |
| S017 | Rust | rustc-dev-guide, https://rustc-dev-guide.rust-lang.org/ | T3 | HTML | Contribution/development guide for rustc. |
| S018 | Cargo | Dependency Resolution, https://doc.rust-lang.org/cargo/reference/resolver.html | T0/T2 | HTML | Cargo dependency resolution as primary task, lockfile result, constraints and heuristics. |
| S019 | Cargo | Manifest Format, https://doc.rust-lang.org/cargo/reference/manifest.html | T0/T2 | HTML | Cargo.toml as TOML manifest with metadata required to compile package. |
| S020 | Cargo | Registries, https://doc.rust-lang.org/cargo/reference/registries.html | T0/T2 | HTML | Registry, index, crates.io default, alternate registry, publishing. |
| S021 | Rust | std crate docs, https://doc.rust-lang.org/std/ | T0 | HTML | Rust standard library as portable foundation, minimal battle-tested abstractions, I/O, multithreading. |
| S022 | V8 | V8 Documentation, https://v8.dev/docs | T0/T3 | HTML | V8 as JS/Wasm engine, compiles/executes JS, memory allocation, GC. |
| S023 | V8 | Maglev blog, https://v8.dev/blog/maglev | T3/T4 | HTML | Ignition bytecode, tiered pipeline, Maglev between Sparkplug and TurboFan. |
| S024 | V8 | Orinoco GC blog, https://v8.dev/blog/trash-talk | T3/T4 | HTML | STW GC latency/jank, parallel/concurrent/incremental GC. |
| S025 | Node.js | Event Loop, https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick | T0/T3 | HTML | Event loop phases, non-blocking I/O, libuv timer behavior changes. |
| S026 | libuv | libuv documentation, https://docs.libuv.org/en/v1.x/ | T0/T3 | HTML | Event loop backed by epoll/kqueue/IOCP/event ports, TCP/UDP, DNS, fs, process, thread pool, signals. |
| S027 | libuv | Thread pool, https://docs.libuv.org/en/v1.x/threadpool.html | T0/T2 | HTML | Default size 4, UV_THREADPOOL_SIZE max 1024, global/shared pool, memory trade-off. |
| S028 | Tokio | Tokio crate docs, https://docs.rs/tokio/latest/tokio/ | T0/T2 | HTML | Event-driven non-blocking I/O, tasks, async TCP/UDP/fs/process/signal, runtime scheduler/I/O/timer. |
| S029 | Tokio | Runtime configurations, https://docs.rs/tokio/latest/tokio/runtime/index.html | T0/T2 | HTML | Multi-thread scheduler, work stealing, current-thread scheduler, resource drivers. |
| S030 | npm | package-lock.json, https://docs.npmjs.com/cli/v11/configuring-npm/package-lock-json/ | T0/T2 | HTML | Exact dependency tree, lockfile format, integrity/resolved metadata. |
| S031 | pip | Dependency Resolution, https://pip.pypa.io/en/stable/topics/dependency-resolution/ | T0/T3 | HTML | Backtracking resolver and conflict handling. |
| S032 | Astral uv | Resolver internals, https://docs.astral.sh/uv/concepts/resolution/ | T3 | HTML | Multi-environment Python resolution and contradictory requirements. |
| S033 | Google | TCMalloc Design, https://google.github.io/tcmalloc/design.html | T0/T3 | HTML | Per-thread/per-CPU caches, low contention, size classes, front/middle/back-end. |
| S034 | jemalloc | jemalloc, https://jemalloc.net/ | T0/T3 | HTML | Fragmentation avoidance, scalable concurrency, profiling and tuning hooks. |
| S035 | Microsoft | mimalloc, https://microsoft.github.io/mimalloc/ | T0/T3 | HTML | Free-list sharding, eager page purging, secure mode, bounded worst-case. |
| S036 | Rust | GlobalAlloc, https://doc.rust-lang.org/std/alloc/trait.GlobalAlloc.html | T0/T2 | HTML | Unsafe global allocator trait, #[global_allocator], optimizer caveats. |
| S037 | HikariCP | HikariCP repository, https://github.com/brettwooldridge/HikariCP | T2/T3 | GitHub | Fast/simple/reliable JDBC pool, keepalive note, artifact matrix. |
| S038 | Java | ThreadPoolExecutor, https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/ThreadPoolExecutor.html | T0/T2 | HTML | Pooled threads, resource bounding, adjustable parameters, statistics. |
| S039 | OpenJDK | JDK Project, https://openjdk.org/projects/jdk/ | T3 | HTML | Open-source Java SE RIs and six-month feature releases. |
| S040 | LLVM | LLVM Language Reference, https://llvm.org/docs/LangRef.html | T0 | HTML | LLVM IR as SSA-based, type-safe, low-level common representation; verifier. |
| S041 | OpenJDK | JDK 25 Project, https://openjdk.org/projects/jdk/25/ | T3 | HTML | JDK 25 GA, Java SE 25 RI, AOT and other features. |
| S042 | Go | cmd/compile README, https://go.dev/src/cmd/compile/README | T2/T3 | Source | Compiler phases: frontend, IR, middle-end optimizations, backend. |
| S043 | LLVM | Code Generator, https://llvm.org/docs/CodeGenerator.html | T0/T3 | HTML | Target-independent codegen stages: instruction selection, scheduling, register allocation. |
| S044 | npm | package.json, https://docs.npmjs.com/cli/v11/configuring-npm/package-json/ | T0/T2 | HTML | name/version identifier, semver, metadata, license, bugs, discoverability. |

## 5. Cluster-Level Decision Model

### Definition

ランタイム・言語実行基盤は、ソースコード・パッケージ・依存関係・バイトコード/IR・プロセス・メモリ・スレッド/非同期 I/O・接続リソースを、ユーザーが観測可能な挙動と組織が制御可能な運用面へ変換する層である。

### Decision Object

「どの言語/実行単位を、どの互換性 contract、性能 envelope、メモリ/並行性制約、供給網保証、運用テレメトリで実行可能にするか」

### Inputs

- 言語仕様、ABI/API compatibility、target OS/CPU、deployment model、security boundary
- source code、manifest、lockfile、registry metadata、dependency constraints
- workload shape: startup-sensitive / throughput-sensitive / latency-sensitive / memory-constrained / embedded / server-side / interactive
- concurrency model: threads, goroutines, tasks, event loop, child processes, DB/network connections
- operational SLO: p95/p99 latency, pause time, RSS cap, CPU budget, package reproducibility, build determinism
- ecosystem constraints: semantic versioning、registry availability、package signing/checksum、deprecation policy

### Criteria

1. Semantics safety: source/interpreter/compiler/JIT/GC/allocator が同一言語 semantics を維持する。
2. Reproducibility: package install、dependency resolution、compiler output、runtime flags が再現可能である。
3. Observability: GC、allocator、thread pool、connection pool、event loop、resolver conflict が計測可能である。
4. Evolvability: release train、feature gate、deprecation、compatibility test、rollback が存在する。
5. Performance envelope: startup、warmup、steady-state throughput、latency、memory footprint を用途ごとに最適化できる。
6. Failure containment: OOM、deadlock、pool exhaustion、resolver conflict、JIT deopt storm、GC pause、event-loop blocking を隔離できる。

### Priorities

1. Correctness and compatibility before peak performance.
2. Determinism before convenience in package/dependency management.
3. Bounded resource usage before unbounded parallelism.
4. Explicit flags / documented knobs before implicit tuning.
5. Public diagnostics before private tribal knowledge.

### Prohibitions

- 実行結果が interpreter と JIT/AOT で不一致になる設計。
- lockfile / checksum / registry source を無視する build pipeline。
- GC/allocator/threadpool/connection pool を metrics なしで production に置く運用。
- “latest resolves best” のように resolver decision を非決定的にする設計。
- event loop 上で blocking I/O / CPU-heavy work を実行する設計。
- experimental flag を stable contract として扱う運用。

### Owners / Reviewers

- Runtime owner / VM owner / Compiler owner
- Standard library API owner
- Package ecosystem owner / release engineering owner
- Performance engineering / SRE
- Security / supply-chain owner
- Database/platform owner for connection pooling
- Developer-experience owner for diagnostics and documentation

### Cadence

- Feature release train: 6 months など明示された release cadence を持つ。
- Runtime/JIT/GC changes: benchmark regression gate、canary、feature flag、rollback path を必須化。
- Package metadata/resolver changes: lockfile compatibility and migration plan を必須化。
- Standard library changes: API review、deprecation window、documentation and examples sync。
- Allocator/thread/connection pool changes: production metrics and leak/exhaustion tests。

## 6. Layer Clone Specs

### 16.01. 言語ランタイム全体

#### Definition

言語プログラムを実行可能にする object model、type/runtime metadata、panic/fatal handling、environment flags、diagnostics、observability、embedding/API surface を決めるレイヤー。

#### Frontier Exemplars

- Go runtime: goroutines/type information、GOGC/GOMEMLIMIT などの runtime knobs を公開する。[S011]
- V8: JS/Wasm engine として compile/execute、memory allocation、GC を統合する。[S022]
- CPython: reference interpreter として devguide、InternalDocs、memory/GC API を公開する。[S005][S006][S007][S008]
- OpenJDK/HotSpot: VM runtime のサブシステムを明示し、Java SE RI と release process を持つ。[S001][S003]

#### Decision Model

| Field | Spec |
|---|---|
| Inputs | language semantics、target OS/CPU、embedding needs、runtime flags、telemetry requirements、compatibility constraints |
| Criteria | semantic correctness、startup、steady-state throughput、memory envelope、diagnosability、configuration stability |
| Priorities | public API > private hooks、documented flags > implicit behavior、fallback path > peak optimization |
| Prohibitions | undocumented stable behavior、runtime crashes without fatal diagnostics、private flag dependency in production |
| Exceptions | experimental features may use opt-in build/runtime flags and explicit rollback policy |
| Owners | runtime owner、release owner、performance owner、security owner |
| Review cadence | feature/release boundary、runtime flag additions、compatibility-affecting changes |

#### Technical / Business Specification

- Runtime public surface: environment variables, CLI flags, runtime package/API, diagnostics endpoint or dump format.
- Lifecycle: initialization、main execution、shutdown、fatal error、fork/exec or subprocess interactions.
- Diagnostics: fatal log、heap/thread dump、runtime version、flag dump、feature flag state.
- Compatibility: stable vs experimental flags, ABI/API stability window, migration guide.

#### Metrics

Startup time、p50/p99 execution latency、RSS、heap live bytes、runtime CPU、panic/fatal count、configuration drift、observability coverage。

#### Failure Modes

- Runtime flag drift creates environment-specific behavior.
- Fatal crash lacks actionable log.
- Experimental feature becomes de facto production dependency without rollback.
- Runtime embeds hidden global state that blocks multi-tenant/process reuse.

#### Anti-patterns

- “Runtime is just implementation detail.”
- No public inventory of runtime knobs.
- No separation between stable and developer/experimental flags.

#### Clone Implementation Guide

1. Runtime surface catalog を作る: env vars, CLI flags, APIs, generated diagnostics, feature gates.
2. Stable / experimental / developer-only を分類し、production allowed list を作る。
3. Runtime metrics を standard dashboard 化する。
4. Fatal error and rollback runbook を release process に組み込む。

#### Confidence & Unknowns

Confidence A: runtime surface and subsystem model.  
Unknown: 各プロジェクトの内部 tuning threshold は公開情報のみでは確定できない。

---

### 16.02. VM ランタイム

#### Definition

仮想マシンの lifecycle、class/module loading、verification、bytecode execution、VM flags、synchronization、thread management、native interface、fatal handling を統合するレイヤー。

#### Frontier Exemplars

- HotSpot: command-line options、VM lifecycle、class loading、bytecode verifier、CDS、interpreter、exception handling、synchronization、thread management、C++ heap management、JNI、fatal errors を runtime overview に列挙する。[S001]
- JDK project: open-source Java SE RI として feature release cadence を持つ。[S039]

#### Decision Model

| Field | Spec |
|---|---|
| Inputs | bytecode/module format、class loader graph、verification policy、native boundary、VM flags、security policy |
| Criteria | safe loading、verifiability、startup、class data sharing、thread/sync correctness、native boundary safety |
| Priorities | verification > execution speed、flag clarity > hidden tuning、fatal diagnosis > silent crash |
| Prohibitions | unverified bytecode execution、unbounded native boundary trust、unsupported VM flags as stable interface |
| Exceptions | developer/diagnostic flags may exist but must be labeled non-standard or experimental |
| Owners | VM owner、classloader owner、security owner、release owner |
| Review cadence | VM flag additions、module/class loading change、native interface change、major release |

#### Technical / Business Specification

- VM option taxonomy: standard、non-standard、developer、diagnostic、experimental.
- Loader policy: parent delegation or equivalent graph, isolation model, cache/CDS policy.
- Verification: bytecode/module validation, fail-closed behavior, error message standard.
- Thread/sync: monitor implementation、safe points、thread dump、deadlock diagnostics.
- Fatal handling: crash log with VM version, flags, native stack, heap state.

#### Metrics

Class/module load time、verification time、startup time、thread count、monitor contention、native boundary error rate、fatal crash recoverability。

#### Failure Modes

- Loader leaks or classpath/module path ambiguity.
- VM flag combinations not tested in production.
- Native integration bypasses verifier/safety model.
- Fatal crash lacks configuration context.

#### Anti-patterns

- Treating VM options as tribal tuning.
- No stable/developer flag boundary.
- No class/module loading diagnostics.

#### Clone Implementation Guide

Create a VM runtime registry that maps each VM knob to owner, stability level, default, allowed ranges, test coverage, and rollback procedure. Add CI tests for class/module loading, verifier failures, and crash log completeness.

#### Confidence & Unknowns

Confidence A for HotSpot-derived VM subsystem structure.  
Unknown: Internal HotSpot tuning heuristics and private production policies are not fully public.

---

### 16.03. インタプリタ

#### Definition

AST/bytecode を逐次実行し、frame、stack、exception、debugging、profiling、fallback semantics を定義するレイヤー。

#### Frontier Exemplars

- CPython: source to bytecode compiler pipeline and reference interpreter documentation.[S006]
- V8 Ignition: JS is first compiled to Ignition bytecode and interpreted before later optimization tiers.[S023]
- HotSpot interpreter: VM runtime overview includes interpreter as a core HotSpot subsystem.[S001]

#### Decision Model

| Field | Spec |
|---|---|
| Inputs | bytecode/AST format、frame layout、debugger/profiler requirements、exception model、JIT fallback needs |
| Criteria | semantic fidelity、debuggability、dispatch throughput、low startup overhead、safe fallback |
| Priorities | interpreter correctness > JIT performance、debug hooks > opaque execution、bytecode version clarity > hidden evolution |
| Prohibitions | interpreter/JIT semantic divergence、undocumented bytecode changes、profiling hooks that distort semantics |
| Exceptions | optimized specialized opcodes may exist but must deopt/fallback safely |
| Owners | interpreter owner、compiler owner、debug/profiling tooling owner |
| Review cadence | bytecode format changes、frame layout changes、debugger/profiler changes |

#### Technical / Business Specification

- Bytecode/AST contract: version, opcode definitions, stack effect, exception behavior.
- Frame model: locals, stack, instruction pointer, traceback/debug metadata.
- Dispatch: direct-threaded/switch/specialized dispatch; document performance assumptions.
- Integration: profiler counters and hotness signals for JIT/AOT pipeline.
- Fallback: any optimized tier must be able to return to interpreter semantics.

#### Metrics

Cold-start execution time、dispatch ns/op、bytecode size、frame allocation rate、exception overhead、debug/profiler overhead、fallback correctness failures。

#### Failure Modes

- Optimized tier assumes interpreter-invisible invariants.
- Debugger/profiler hooks become incompatible with specialized opcodes.
- Bytecode changes break cached artifacts.

#### Anti-patterns

- Treating bytecode as private while external tools depend on it.
- JIT-only tests without interpreter equivalence tests.
- No bytecode/frame versioning.

#### Clone Implementation Guide

Define bytecode/frame schema, create interpreter conformance tests, add cross-tier equivalence tests, and expose profiler counters that do not alter semantics.

#### Confidence & Unknowns

Confidence B: interpreter principles are triangulated across CPython, V8, and HotSpot.  
Unknown: Precise opcode implementation strategies differ by project and version.

---

### 16.04. コンパイラ

#### Definition

source code を parse、type check、lower、optimize、codegen し、diagnostics と machine/bytecode artifacts を生成するレイヤー。

#### Frontier Exemplars

- LLVM: SSA-based, type-safe, low-level IR and verifier; target-independent code generation.[S040][S043]
- Go compiler: frontend / IR / middle-end / backend phases and optimization passes.[S042]
- CPython compiler: tokenize, parse AST, transform AST, CFG/optimize, bytecode emission.[S006]
- rustc: Rust compiler; crate is translation unit and most users invoke via Cargo.[S016]

#### Decision Model

| Field | Spec |
|---|---|
| Inputs | source language、grammar、type system、target runtime、target ABI/ISA、optimization goals |
| Criteria | correctness、diagnostic quality、optimization safety、incrementality、cross-target portability、build determinism |
| Priorities | verified IR > ad hoc transform、clear diagnostics > clever optimization、reproducible build > non-deterministic speedups |
| Prohibitions | optimization without verifier/regression tests、target-specific logic leaking into frontend、silent ICEs |
| Exceptions | experimental optimization passes require flag, benchmark evidence, rollback path |
| Owners | compiler frontend owner、IR owner、backend owner、diagnostics owner、release owner |
| Review cadence | grammar/type changes、IR changes、optimization pass changes、target backend additions |

#### Technical / Business Specification

- Compiler pipeline document: parse → typecheck → IR → optimize → codegen → link/package.
- IR contract: verification rules, allowed transformations, metadata, debug info preservation.
- Diagnostics: stable error categories, source spans, suggestions, machine-readable output if used by tooling.
- Regression: compile-time benchmark, code-size benchmark, correctness suite, fuzzing, sanitizer where relevant.
- Build determinism: controlled randomness, stable timestamps, reproducible artifacts.

#### Metrics

Compile time、incremental cache hit rate、ICE rate、diagnostic satisfaction、binary/bytecode size、optimization regression count、target coverage、fuzz crash count。

#### Failure Modes

- Optimizer miscompilation.
- IR invariant not enforced.
- Diagnostics become unstable API for tooling.
- Compile-time explosion from expensive passes.

#### Anti-patterns

- “One-pass compiler” with no intermediate invariant.
- Target backend coupled to parser.
- No verifier or post-pass validation.

#### Clone Implementation Guide

Write a compiler phase contract, introduce IR verifier, gate optimization passes with correctness and performance benchmark deltas, and publish diagnostics compatibility rules.

#### Confidence & Unknowns

Confidence A for phase/IR/verifier model.  
Unknown: Project-specific optimization heuristics are partly internal and workload-dependent.

---

### 16.05. Bytecode / JIT / AOT 実行パイプライン

#### Definition

interpreter、baseline compiler、optimizing compiler、AOT compiler、profile feedback、deoptimization、code cache、feature flags を設計するレイヤー。

#### Frontier Exemplars

- V8: Ignition → Sparkplug → Maglev → TurboFan tiering; Maglev sits between baseline and optimizing tiers.[S023]
- Python 3.13: experimental JIT compiler build option and runtime flag.[S010]
- JDK 25: AOT-related features and production release process.[S041][S003]
- LLVM: code generation and JIT-capable codegen infrastructure.[S043]

#### Decision Model

| Field | Spec |
|---|---|
| Inputs | hotness profile、startup target、latency target、security/JIT policy、AOT artifacts、deopt metadata |
| Criteria | warmup cost、peak throughput、startup、code cache memory、deopt safety、observability |
| Priorities | safe fallback > peak speed、profile-guided promotion > static guess、explicit opt-in for experimental JIT/AOT |
| Prohibitions | unbounded code cache、no deopt path、JIT silently enabled in restricted environments |
| Exceptions | embedded/serverless may disable JIT and prefer AOT/interpreter |
| Owners | JIT/AOT owner、runtime owner、security owner、performance owner |
| Review cadence | tier policy change、JIT flag change、AOT artifact format change、deopt metadata change |

#### Technical / Business Specification

- Tier state machine: interpreter → baseline → mid-tier → optimizing → deopt/fallback.
- Promotion criteria: counters, type feedback, callsite stability, warmup budget.
- Deoptimization: metadata fidelity, exception safety, debugger compatibility.
- Code cache: memory limit, eviction, fragmentation, executable-memory policy.
- Security: W^X policy, JIT disable flag, sandboxing where applicable.

#### Metrics

Warmup time、peak throughput、deopt rate、code cache size、JIT compile CPU、startup overhead、security policy violations、rollback count。

#### Failure Modes

- Deopt storm under polymorphic workloads.
- JIT startup overhead hurts short-lived processes.
- AOT profile mismatch worsens production performance.
- Executable memory policy conflicts with hardening.

#### Anti-patterns

- JIT as hidden global default without flag inventory.
- No interpreter/JIT equivalence tests.
- AOT artifacts not invalidated when runtime/stdlib changes.

#### Clone Implementation Guide

Create tier decision table, code cache budget, JIT/AOT feature gates, deopt telemetry, and a safe default for restricted or short-lived environments.

#### Confidence & Unknowns

Confidence B: tiered execution and operational controls are evidenced across V8, CPython, JDK, and LLVM.  
Unknown: Exact tier thresholds are implementation-specific and frequently unpublished.

---

### 16.06. 標準ライブラリ

#### Definition

言語 ecosystem における foundational API、platform abstraction、I/O、collections、concurrency、compiler/runtime integration、documentation and stability boundary を決めるレイヤー。

#### Frontier Exemplars

- Java SE API: core platform APIs and modules, with java.base as foundational module.[S004]
- Python stdlib: distributed with Python, combining built-in modules and pure Python modules, with portability emphasis.[S009]
- Rust std: portable foundation of Rust software, minimal battle-tested shared abstractions, core types, I/O, multithreading.[S021]

#### Decision Model

| Field | Spec |
|---|---|
| Inputs | common use cases、platform abstraction needs、language primitives、ecosystem package availability、compatibility guarantees |
| Criteria | portability、stability、minimality vs batteries-included、security/maintenance cost、documentation quality |
| Priorities | stable foundational APIs > convenience APIs、portable API > platform-specific shortcut、documentation examples > implicit knowledge |
| Prohibitions | adding APIs without maintenance owner、platform-specific behavior hidden behind portable name、silent breaking change |
| Exceptions | platform-specific modules may exist with explicit capability checks |
| Owners | standard library API owner、language governance group、documentation owner、security owner |
| Review cadence | API proposal、deprecation、major release、security fix |

#### Technical / Business Specification

- Inclusion criteria: frequency of need, portability, maintenance burden, ecosystem alternatives, security implications.
- Stability policy: semver or release-cycle compatibility, deprecation warnings, removal windows.
- Documentation: examples, source links, platform notes, feature flags.
- Test strategy: conformance, platform matrix, fuzz/property tests for core APIs.

#### Metrics

API usage/adoption、breaking-change count、deprecation debt、docs coverage、platform failure rate、security advisory count、stdlib package size。

#### Failure Modes

- Standard library absorbs too many domain-specific APIs and slows evolution.
- Under-specified platform behavior causes portability bugs.
- Deprecation never reaches removal, accumulating compatibility debt.

#### Anti-patterns

- Treating stdlib as dumping ground for popular utilities.
- No source/documentation linkage.
- No platform abstraction policy.

#### Clone Implementation Guide

Define stdlib RFC/API-review process, add lifecycle states (experimental/stable/deprecated), require ownership for every module, and publish portability matrices.

#### Confidence & Unknowns

Confidence A for stdlib boundary.  
Unknown: Exact inclusion committees and internal API scoring are project-specific.

---

### 16.07. パッケージマネージャ

#### Definition

package の install、build、test、publish、fetch、cache、registry access、workspace、script execution、audit/integrity を実行するレイヤー。

#### Frontier Exemplars

- Cargo: manifest、registry、resolver、lockfile、workspace と Rust compiler workflow を統合する。[S018][S019][S020]
- npm: package.json and package-lock.json define package metadata and exact dependency tree.[S030][S044]
- Go modules: go.mod, module cache, checksum verification, vendoring, MVS.[S013][S014]
- pip/PyPA: dependency resolution and PEP 508-style specifiers.[S031]

#### Decision Model

| Field | Spec |
|---|---|
| Inputs | manifest、lockfile、registry index/API、cache、platform/target、auth credentials、install mode |
| Criteria | reproducibility、speed、registry availability、integrity、conflict diagnostics、developer ergonomics |
| Priorities | lockfile integrity > convenience、cache correctness > speed、registry provenance > arbitrary source |
| Prohibitions | installing without source/integrity record、hidden mutation of manifest、unbounded script execution without policy |
| Exceptions | local path/git dependencies allowed with explicit source and lock metadata |
| Owners | package manager owner、ecosystem security owner、registry owner、release engineering owner |
| Review cadence | manifest schema changes、lockfile version changes、registry protocol changes、script execution policy changes |

#### Technical / Business Specification

- Commands: install, update, build, test, publish, audit, vendor, verify.
- Registry protocol: index, package metadata, artifact URL, checksum/signature, auth.
- Cache: location, eviction, integrity recheck, offline mode.
- Scripts/hooks: allowed lifecycle hooks, sandboxing policy, audit logging.
- Workspaces: dependency sharing, lockfile scope, publish boundaries.

#### Metrics

Install time、cache hit rate、lockfile drift、registry error rate、publish error rate、audit finding count、script execution failures、offline install success。

#### Failure Modes

- Registry outage blocks builds without cache/offline policy.
- Lifecycle scripts execute unsafe commands.
- Lockfile is regenerated non-deterministically.
- Cache corruption causes hidden package substitution.

#### Anti-patterns

- Treating package manager as CLI only, not supply-chain control plane.
- No registry source provenance.
- No lockfile review in CI.

#### Clone Implementation Guide

Mandate lockfile commits, configure registry allowlist, turn on checksum verification, make install mode reproducible by default, and add CI policy for manifest/lockfile drift.

#### Confidence & Unknowns

Confidence A for package manager control surfaces.  
Unknown: Some registry anti-abuse internals and risk scoring are not public.

---

### 16.08. パッケージメタデータ / Lockfile

#### Definition

package identity、version、dependency declarations、features、target/environment markers、source provenance、integrity hashes、exact resolved tree を記述するレイヤー。

#### Frontier Exemplars

- Cargo.toml: manifest in TOML containing metadata required to compile package.[S019]
- Cargo.lock: resolver output stored as lockfile.[S018]
- package.json: name/version as unique publish identifier and package metadata.[S044]
- package-lock.json: exact dependency tree, resolved URL, integrity hash.[S030]
- go.mod/go.sum: module path, Go version, dependency requirements, checksum verification.[S013][S014]

#### Decision Model

| Field | Spec |
|---|---|
| Inputs | package identity、semantic version、dependency constraints、features、targets、registry source、checksums |
| Criteria | unique identity、deterministic install、integrity、human reviewability、backward compatibility |
| Priorities | exact resolved state > flexible ranges in production、checksum > trust-by-registry、schema versioning > ad hoc metadata |
| Prohibitions | ambiguous package identity、missing source/integrity、lockfile omitted from applications、unversioned schema changes |
| Exceptions | libraries may omit lockfile from publish artifact when ecosystem convention requires, but CI must test lock resolution |
| Owners | package metadata owner、registry owner、release engineering owner、security owner |
| Review cadence | schema field addition、lockfile version change、integrity algorithm change、semver policy change |

#### Technical / Business Specification

- Manifest schema: package, dependencies, dev/build/optional dependencies, features, targets, scripts, license, repository, MSRV/runtime version.
- Lockfile schema: package name/version/source, resolved artifact, integrity hash, transitive dependency graph, lockfile version.
- Policy: application lockfile required; library lockfile policy explicit; CI fails on drift.
- Migration: schema version, parser compatibility, old lockfile update behavior.

#### Metrics

Lockfile drift rate、schema validation failures、checksum mismatch、reproducible install pass rate、metadata completeness、license/source completeness。

#### Failure Modes

- Flexible ranges resolve differently across machines.
- Missing integrity field allows artifact substitution.
- Lockfile version incompatibility breaks CI.
- Metadata lacks license/security contact.

#### Anti-patterns

- “Do not commit lockfiles” as blanket policy.
- Manual lockfile edits without verifier.
- Package identity not tied to version and source.

#### Clone Implementation Guide

Create manifest and lockfile schema validation, require integrity fields, separate library/application lockfile policy, and add diff review for resolved source changes.

#### Confidence & Unknowns

Confidence A for metadata/lockfile purpose.  
Unknown: Ecosystem-specific lockfile conventions differ; library policy should be adapted.

---

### 16.09. 依存リゾルバ

#### Definition

manifest constraints、version ranges、feature flags、target markers、registry metadata を入力し、install/build 可能な dependency graph を決定するレイヤー。

#### Frontier Exemplars

- Cargo resolver: dependency resolution is a primary task; no single best resolution; constraints and heuristics; result in Cargo.lock.[S018]
- pip resolver: backtracking behavior and conflict diagnosis guidance.[S031]
- Go MVS: build list uses minimum version selection and highest required version rule.[S013]
- uv resolver: multi-environment Python resolution and contradictory requirements.[S032]

#### Decision Model

| Field | Spec |
|---|---|
| Inputs | version constraints、features、platform markers、registry versions、lockfile pins、policy preferences |
| Criteria | satisfiability、determinism、minimal churn、explainability、performance、security policy compliance |
| Priorities | existing lock stability > unnecessary upgrades、clear conflict path > silent failure、deterministic tie-breaks > fastest random success |
| Prohibitions | non-deterministic version choice、conflict errors without dependency path、ignoring target/environment markers |
| Exceptions | security update mode may intentionally override minimal-churn policy |
| Owners | resolver owner、package manager owner、ecosystem security owner |
| Review cadence | resolver algorithm changes、semver interpretation changes、feature-unification changes、lockfile update policy changes |

#### Technical / Business Specification

- Algorithm policy: MVS、backtracking SAT-like resolver、PubGrub-style explanations, or hybrid.
- Tie-breaks: newest compatible, lowest direct-change, security-preferred, lock-preserving.
- Conflict reporting: dependency path, conflicting constraints, suggested remedies.
- Performance: backtrack budget, registry query cache, resolution cache, benchmark suite.
- Security: yanked/vulnerable package policy, allow/deny lists.

#### Metrics

Resolution time、backtrack count、conflict explanation completeness、lockfile churn、registry queries、security override count、resolver regression count。

#### Failure Modes

- Resolver thrashes on complex graphs.
- Minimal-churn policy hides required security update.
- Feature unification creates unexpected dependency activation.
- Conflict message gives no actionable path.

#### Anti-patterns

- “Resolve latest” without stability policy.
- No resolver regression corpus.
- No separation between normal update and security update mode.

#### Clone Implementation Guide

Build a resolver test corpus from production dependency graphs, define tie-break policy, implement conflict explanation, and add lockfile-churn metric to CI.

#### Confidence & Unknowns

Confidence A for resolver decision model.  
Unknown: Some internal resolver heuristics and benchmark corpora are not public.

---

### 16.10. Garbage Collection

#### Definition

heap object lifetime、allocation pressure、pause time、throughput、memory limit、debug/tuning knobs、reference-cycle handling を制御するレイヤー。

#### Frontier Exemplars

- Go GC: GC guide, GOGC target percentage, GOMEMLIMIT soft memory limit.[S012][S011]
- V8 Orinoco: stop-the-world pause reduction through parallel/concurrent/incremental GC.[S024]
- Python gc: optional collector that supplements reference counting and can be disabled/tuned/debugged.[S008]
- OpenJDK/HotSpot: GC is part of VM runtime family and JDK 25 includes Generational Shenandoah.[S001][S041]

#### Decision Model

| Field | Spec |
|---|---|
| Inputs | allocation rate、live heap、object graph、latency SLO、memory cap、CPU budget、language reference semantics |
| Criteria | pause time、mutator utilization、throughput、heap/RSS footprint、predictability、debuggability |
| Priorities | bounded pauses for latency workloads、throughput for batch workloads、explicit memory limit for containers |
| Prohibitions | invisible GC pauses、no memory limit in containerized production、GC tuning without heap telemetry |
| Exceptions | reference-counted runtimes may use cycle collector or disabled GC for controlled phases |
| Owners | GC owner、runtime owner、performance/SRE owner |
| Review cadence | GC algorithm changes、default knob changes、container/runtime memory policy changes |

#### Technical / Business Specification

- GC taxonomy: reference counting, generational, concurrent, incremental, compacting, mark-sweep, cycle collector.
- Knobs: heap growth target, memory limit, generations, debug stats, pause logging.
- Integration: allocator interface, safe points, write barriers, finalizers, weak references.
- Operations: memory dashboards, production heap dump policy, GC regression benchmark.

#### Metrics

p50/p99/p999 pause time、GC CPU percentage、heap live bytes、RSS、allocation rate、mutator utilization、collection frequency、OOM count。

#### Failure Modes

- Long stop-the-world pause violates latency SLO.
- Heap growth overshoots container memory limit.
- Finalizer cycles or references retain objects unexpectedly.
- GC tuning reduces pauses but increases CPU/RSS beyond budget.

#### Anti-patterns

- Tuning GC from folklore without workload metrics.
- No distinction between live heap and RSS.
- Treating GC logs as optional in production incidents.

#### Clone Implementation Guide

Define workload-specific GC profiles, expose GC metrics, set memory limits in container environments, maintain GC regression suite, and document emergency tuning runbook.

#### Confidence & Unknowns

Confidence A for GC as SLO surface.  
Unknown: Exact defaults and behavior vary by runtime version; current canonical docs must be rechecked before rollout.

---

### 16.11. Memory Allocation

#### Definition

small/large allocation path、size classes、per-thread/per-CPU cache、spans/pages、fragmentation、purging、secure allocation、stats/profiling hooks を制御するレイヤー。

#### Frontier Exemplars

- TCMalloc: fast uncontended allocation, per-thread/per-CPU caches, front/middle/back-end design, size classes.[S033]
- jemalloc: fragmentation avoidance and scalable concurrency with profiling/tuning hooks.[S034]
- mimalloc: free-list multi-sharding, eager page purging, secure mode, bounded worst-case.[S035]
- Go runtime allocator: TCMalloc-inspired size classes, mheap/mspan/mcentral/mcache, lock-light path.[S015]
- Python memory API and Rust GlobalAlloc: allocator boundary and extension safety.[S007][S036]

#### Decision Model

| Field | Spec |
|---|---|
| Inputs | allocation size distribution、thread count、CPU count、fragmentation tolerance、security hardening、profiling needs |
| Criteria | allocation latency、contention、fragmentation、RSS return-to-OS、cache locality、safety、observability |
| Priorities | fast common path > rare large allocation speed、bounded memory > unlimited per-thread cache、stats > opaque allocator |
| Prohibitions | mixing allocator families unsafely、no stats for production allocator、unbounded per-thread cache under high thread count |
| Exceptions | secure mode may trade memory/speed for guard pages/randomization |
| Owners | allocator owner、runtime owner、performance owner、security owner |
| Review cadence | allocator replacement、size-class policy change、secure-mode policy、memory profiling change |

#### Technical / Business Specification

- Size classes: thresholds, rounding, small vs large allocation path.
- Local caches: per-thread/per-CPU/per-P cache limits and transfer policy.
- Page backend: span/page map, hugepage policy, return-to-OS strategy, purging.
- Safety: guard pages, randomization, encrypted free lists if needed.
- Stats: allocated/active/mapped/resident, fragmentation ratio, allocation sampling.

#### Metrics

alloc/free ns/op、contention time、active/allocated ratio、RSS、mapped bytes、fragmentation、purge rate、OOM/failed allocation count、heap profile coverage。

#### Failure Modes

- Per-thread cache multiplies RSS in high-concurrency service.
- Fragmentation causes memory growth despite low live heap.
- Allocator mismatch corrupts memory.
- Secure mode too expensive for workload without risk classification.

#### Anti-patterns

- Replacing allocator solely based on microbenchmark.
- No allocator stats in incident dashboard.
- Disabling purging to improve benchmark without RSS SLO.

#### Clone Implementation Guide

Instrument allocator stats, classify workloads by allocation profile, set cache and purging policy, run fragmentation benchmarks, and document allowed allocator substitution paths.

#### Confidence & Unknowns

Confidence A for allocator control points.  
Unknown: Production choice among TCMalloc/jemalloc/mimalloc depends on workload and platform; no universal best allocator.

---

### 16.12. Thread Pool / Scheduler

#### Definition

thread/task 実行資源を bounded に管理し、queueing、work stealing、blocking offload、rejection/backpressure、shutdown、stats を制御するレイヤー。

#### Frontier Exemplars

- Java ThreadPoolExecutor: pooled threads, resource bounding, adjustable parameters, statistics.[S038]
- libuv threadpool: global shared pool, default size 4, UV_THREADPOOL_SIZE up to 1024, memory trade-off.[S027]
- Tokio: multi-thread scheduler, work stealing, current-thread scheduler, I/O and timer drivers.[S028][S029]
- Go runtime: goroutines managed by runtime; environment/runtime controls exposed.[S011]

#### Decision Model

| Field | Spec |
|---|---|
| Inputs | task type、CPU vs blocking I/O、queue size、latency SLO、thread limit、runtime driver requirements |
| Criteria | throughput、queue latency、resource bounding、fairness、cancellation、observability |
| Priorities | bounded queue > unbounded memory growth、blocking offload > event-loop blocking、metrics > black-box scheduling |
| Prohibitions | CPU-heavy tasks on event loop、unbounded thread creation、no rejection/backpressure policy |
| Exceptions | short-lived CLI tools may use simple current-thread runtime |
| Owners | runtime/scheduler owner、SRE/performance owner、service owner |
| Review cadence | pool size policy changes、scheduler strategy changes、blocking API additions |

#### Technical / Business Specification

- Pool configuration: core/max threads, queue type/size, idle timeout, thread naming, priority.
- Scheduler: work stealing, cooperative budget, blocking pool, current-thread mode.
- Backpressure: rejection policy, admission control, queue shedding, cancellation.
- Observability: active/idle threads, queue depth, wait time, task duration, blocked task detector.
- Shutdown: graceful drain, forced cancel, stuck task diagnosis.

#### Metrics

Queue depth、queue wait p95/p99、active/idle threads、task duration、rejection count、blocking time、context switches、scheduler lag。

#### Failure Modes

- Unbounded queue converts latency issue into memory/OOM issue.
- Thread starvation when blocking work uses compute pool.
- Work stealing hides unfairness without per-class metrics.
- Shutdown hangs due to uninterruptible tasks.

#### Anti-patterns

- Pool size = CPU cores for mixed blocking and CPU work without separation.
- “Just use async” without blocking offload policy.
- No rejection policy.

#### Clone Implementation Guide

Classify tasks, separate CPU/blocking pools, define queue/rejection policy, add pool metrics and saturation alerts, and require shutdown tests.

#### Confidence & Unknowns

Confidence A for thread pool/scheduler control points.  
Unknown: Optimal pool sizes must be empirically tuned per workload.

---

### 16.13. Connection Pool

#### Definition

database/network connection の作成、borrow/return、validation、idle/lifetime、keepalive、leak detection、max connection budget、shutdown を制御するレイヤー。

#### Frontier Exemplars

- HikariCP: production-ready JDBC connection pool with explicit artifact matrix and keepalive warning to avoid rare pool-zero condition.[S037]
- Java SQL API: database connectivity and transaction/XA-related APIs as standard platform surface.[S004]

#### Decision Model

| Field | Spec |
|---|---|
| Inputs | DB max connections、service concurrency、query latency、network idle timeout、transaction model、driver behavior |
| Criteria | borrow latency、connection reuse、DB protection、stale connection avoidance、leak detection、shutdown correctness |
| Priorities | DB protection > local throughput、bounded pool > connection storm、validation/keepalive > stale connection surprises |
| Prohibitions | unbounded per-service/per-tenant pools、no max lifetime、no leak detection for long transactions、no metrics |
| Exceptions | serverless or short-lived jobs may prefer no persistent pool or very small pool |
| Owners | platform owner、DBA/data platform owner、service owner、SRE |
| Review cadence | DB limit change、driver upgrade、network timeout change、pool configuration change |

#### Technical / Business Specification

- Config: maxPoolSize, minIdle, connectionTimeout, idleTimeout, maxLifetime, keepaliveTime, validation query, leakDetectionThreshold.
- Lifecycle: create, validate, borrow, return, evict, close, shutdown.
- Budgeting: DB max connections divided across services, instances, tenants, and replicas.
- Reliability: keepalive, retries outside transaction boundary, health check, driver-level timeout.
- Observability: active/idle/waiting connections, borrow latency, timeout count, leak count.

#### Metrics

Active/idle connections、pending borrowers、borrow latency p95/p99、connection acquisition timeout、leak detection count、DB connection utilization、eviction count、stale connection error rate。

#### Failure Modes

- Pool exhaustion cascades into request timeout.
- Over-pooling overwhelms database.
- Stale connections remain after network/DB idle timeout.
- Connection leak slowly reduces available pool.

#### Anti-patterns

- One pool per tenant without global budget.
- No keepalive/lifetime alignment with network and database timeouts.
- No metric alerts on pending borrowers.

#### Clone Implementation Guide

Inventory all pools, allocate DB connection budgets, standardize Hikari-like settings, add leak detection in non-prod and selective prod, and alert on pending borrowers and acquisition timeouts.

#### Confidence & Unknowns

Confidence B: HikariCP and Java SQL provide strong public evidence, but connection-pool policy is workload/database specific.  
Unknown: Private SRE pool budgets and incident thresholds are usually not public.

---

### 16.14. Async / Process Runtime

#### Definition

event loop、OS event queue、timers、non-blocking I/O、signals、child processes、task scheduling、blocking offload、cancellation/backpressure を制御するレイヤー。

#### Frontier Exemplars

- Node.js event loop: phases for timers, pending callbacks, poll, check, close; non-blocking I/O through OS/kernel and libuv.[S025]
- libuv: event loop backed by epoll/kqueue/IOCP/event ports, async TCP/UDP, DNS, fs, IPC, child processes, thread pool, signals.[S026]
- Tokio: event-driven non-blocking I/O platform with tasks, async I/O, process/signal support, scheduler, I/O driver, timer.[S028][S029]

#### Decision Model

| Field | Spec |
|---|---|
| Inputs | async I/O workload、timer workload、blocking operations、child process needs、signal handling、cancellation semantics |
| Criteria | non-blocking behavior、event loop latency、fairness、timer accuracy、backpressure、process cleanup |
| Priorities | never block event loop、explicit blocking offload、structured cancellation、observable loop lag |
| Prohibitions | sync file/network calls on event loop、child process without reap policy、timers without drift monitoring |
| Exceptions | current-thread runtime acceptable for embedded/single-purpose tools with known blocking constraints |
| Owners | async runtime owner、service owner、SRE/performance owner、security owner for subprocesses |
| Review cadence | runtime version upgrade、timer/event-loop semantics change、blocking API introduction、process/signal behavior change |

#### Technical / Business Specification

- Event loop phases and driver: OS event queue, timers, poll, callbacks, close handling.
- Task model: spawn, join, cancel, local vs multi-thread, cooperative budget.
- Blocking offload: dedicated pool, max threads, queue/backpressure.
- Process runtime: spawn, stdin/out/err, signal, timeout, reap, sandbox/env allowlist.
- I/O: TCP/UDP/DNS/fs integration and error handling.

#### Metrics

Event loop lag、poll latency、timer drift、task queue depth、blocked worker count、async task duration、subprocess count、zombie/reap failures、cancellation latency。

#### Failure Modes

- Blocking call stalls all callbacks.
- Timer semantics change across runtime/libuv versions affects scheduling.
- Subprocess not reaped, causing zombie leak.
- Cancellation drops resources without cleanup.

#### Anti-patterns

- Mixing sync and async APIs without blocking classification.
- No event-loop lag metric.
- No child process timeout/reap policy.

#### Clone Implementation Guide

Adopt async runtime guidelines, ban blocking calls in async contexts unless offloaded, instrument loop lag and task duration, and define subprocess lifecycle policy.

#### Confidence & Unknowns

Confidence A for event-loop/process-runtime model.  
Unknown: Runtime-specific scheduling fairness and timer internals require version-specific verification.

## 7. Cross-Layer Operating Model

### Roles

| Role | Responsibilities |
|---|---|
| Runtime Architect | 16.01–16.05 の compatibility/performance/failure policy を統括する。 |
| Compiler/IR Owner | compiler pipeline、IR invariants、optimization gates、diagnostics compatibility を管理する。 |
| Standard Library Council | API inclusion、stability、deprecation、platform abstraction を決める。 |
| Package Ecosystem Owner | package manager、manifest、lockfile、resolver、registry policy を管理する。 |
| Performance Engineering | GC、allocator、scheduler、JIT/AOT、pool tuning の benchmark and regression gate を運用する。 |
| SRE / Platform | production metrics、resource limits、incident runbooks、pool/thread/async saturation を管理する。 |
| Security / Supply Chain | integrity、checksums、registry provenance、script policy、executable memory/JIT policy を管理する。 |
| Release Manager | release train、feature flags、rollbacks、deprecations、migration docs を統制する。 |

### Process

1. **Design intake:** new runtime/compiler/package/GC/pool feature is registered as a decision object, not just issue/PR.
2. **Spec review:** affected layers, compatibility risk, metrics, rollback, artifacts, docs, security impact are reviewed.
3. **Implementation gate:** verifier/conformance tests、benchmark suite、lockfile/resolver corpus、runtime telemetry are required before merge.
4. **Release gate:** feature flags、migration docs、deprecation notes、runtime/stdlib/package-manager version compatibility are checked.
5. **Production validation:** canary, dashboard, error budgets, memory/thread/pool saturation, resolver/build reproducibility are monitored.
6. **Post-release learning:** incidents and regressions are converted into anti-patterns and validation queries.

### Core Artifacts

- Runtime flag catalog
- VM lifecycle and fatal-error specification
- Bytecode / IR / ABI / codegen documentation
- Interpreter/JIT/AOT equivalence tests
- Standard library API review records
- Manifest and lockfile schema
- Resolver algorithm policy and regression corpus
- GC/allocator/thread/connection/async runtime dashboards
- Release train and deprecation policy
- Incident runbooks for OOM, GC pause, pool exhaustion, event-loop blocking, resolver conflict, miscompilation

## 8. Metrics Framework

| Metric family | Representative metrics |
|---|---|
| Correctness | conformance pass rate、miscompilation count、interpreter/JIT equivalence failures、resolver lock reproducibility |
| Performance | startup time、warmup time、throughput、compile time、install time、resolution time |
| Latency | p99 runtime latency、GC pause、event loop lag、thread queue wait、connection borrow latency |
| Memory | RSS、heap live、allocator fragmentation、code cache size、per-thread/per-CPU cache usage |
| Reliability | fatal crashes、OOM、deadlocks、pool exhaustion、stale connection errors、zombie process count |
| Supply chain | checksum mismatch、registry source drift、lockfile drift、vulnerability/advisory count |
| Developer experience | diagnostic clarity、conflict explanation completeness、documentation coverage、time-to-first-success |
| Governance | release gate violations、late feature exceptions、deprecation debt、rollback count |

## 9. Failure Modes and Controls

| Failure mode | Affected layers | Control |
|---|---:|---|
| Interpreter/JIT semantic divergence | 16.03, 16.05 | Cross-tier conformance tests and deopt/fallback telemetry. |
| Miscompilation | 16.04, 16.05 | IR verifier, optimization regression suite, fuzzing, release rollback. |
| Non-deterministic dependency install | 16.07–16.09 | Lockfile required, checksum verification, deterministic resolver tie-breaks. |
| Resolver conflict without actionability | 16.09 | Dependency path explanation and suggested remediation. |
| Long GC pause | 16.10 | GC pause metrics, workload-specific profile, canary before default changes. |
| Allocator fragmentation/RSS growth | 16.11 | Allocator stats, fragmentation tests, purging and cache limits. |
| Thread starvation | 16.12 | Separate blocking/CPU pools, queue limits, rejection/backpressure. |
| Connection pool exhaustion | 16.13 | Budgeted max pool, pending borrower alerts, leak detection, keepalive/lifetime alignment. |
| Event-loop blocking | 16.14 | Blocking API ban/offload, event-loop lag metric, task duration tracing. |
| Experimental runtime feature becomes production dependency | 16.01, 16.05 | Stable/experimental flag classification and rollback plan. |

## 10. Anti-pattern Library

| Pattern ID | Anti-pattern | Why harmful | Replacement pattern |
|---|---|---|---|
| AP-RT-01 | Runtime flags as tribal knowledge | Reproducibility and incident debugging fail. | Runtime flag catalog with owner/stability/default/range. |
| AP-VM-01 | VM verification treated as optional | Unsafe bytecode/module loading can violate runtime contract. | Fail-closed verifier and loader diagnostics. |
| AP-COMP-01 | Optimizer without verifier | Miscompilation becomes hard to localize. | IR verifier after each high-risk pass. |
| AP-JIT-01 | JIT enabled without feature gate | Security and warmup regressions surprise production. | Feature flag, code-cache budget, deopt telemetry. |
| AP-STD-01 | Standard library as utility dump | Maintenance and compatibility debt grows. | Inclusion criteria and API lifecycle. |
| AP-PKG-01 | No lockfile in application deploy | Install becomes non-reproducible. | Commit lockfile and verify in CI. |
| AP-RES-01 | Resolver error says only “conflict” | Developers cannot fix constraints. | Path-based conflict explanation. |
| AP-GC-01 | GC tuning by folklore | SLO trade-offs become invisible. | Pause/RSS/CPU dashboards and profile-specific tuning. |
| AP-ALLOC-01 | Allocator swap by benchmark only | Fragmentation/security/workload mismatch ignored. | Workload-specific allocation profile and incident metrics. |
| AP-POOL-01 | Unbounded queues | Latency failure becomes memory failure. | Bounded queues and rejection/backpressure. |
| AP-DBPOOL-01 | Pool max copied between services | DB overload or underutilization. | Budget connection count from DB max and replica count. |
| AP-ASYNC-01 | Blocking calls inside event loop | All callbacks/tasks stall. | Static linting plus blocking offload pool. |

## 11. Maturity Model

| Level | Name | Criteria |
|---:|---|---|
| 0 | 未整備 | Runtime/package/pool behavior is managed by individual developers; no source-of-truth docs or metrics. |
| 1 | 個人依存 | Some runtime flags and package practices known, but lockfiles, GC, pool, and async policies differ by team. |
| 2 | 文書化 | Runtime flag catalog, package metadata rules, basic GC/thread/pool metrics, and release notes exist. |
| 3 | 標準化 | Compiler/runtime/package/resolver/pool policies are standardized; CI enforces lockfile, tests, and benchmark gates. |
| 4 | 自動化・計測 | Resolver corpus, IR/verifier gates, GC/allocator dashboards, pool saturation alerts, event-loop lag tracing, canary rollout are automated. |
| 5 | 自律改善・業界先端 | Runtime tiers, memory/pool policies, dependency risk, and release gates adapt from telemetry; anti-patterns are fed back into design reviews. |

## 12. Clone Implementation Guide

### 0–30 days: Baseline and inventory

- Create runtime flag/API inventory for production services.
- Inventory package managers, manifests, lockfiles, registry sources, and cache policies.
- Add baseline metrics: GC pause/RSS, allocation stats if available, thread queue depth, connection pool active/pending, event loop lag.
- Identify compiler/runtime/version combinations in production.

### 31–90 days: Policy and gates

- Define stable/experimental runtime feature policy.
- Mandate application lockfiles and checksum verification in CI.
- Define dependency resolver update modes: normal, security, minimal-churn, full-upgrade.
- Establish compiler/runtime benchmark gates for startup, throughput, memory, and latency.
- Standardize connection-pool and thread-pool configuration templates.

### 91–180 days: Verification and observability

- Add interpreter/JIT equivalence tests where applicable.
- Introduce IR/verifier or post-pass validation for compiler changes.
- Build resolver regression corpus from real dependency graphs.
- Add GC/allocator/thread/pool/async incident dashboards and SLO alerts.
- Formalize standard library inclusion/deprecation policy.

### 181–365 days: Advanced operation

- Implement canary and rollback for runtime/JIT/GC/default flag changes.
- Automate lockfile drift and dependency risk scoring.
- Run allocator and GC workload-profile experiments.
- Create event-loop blocking detectors and subprocess lifecycle enforcement.
- Convert incidents into anti-patterns and validation queries.

## 13. Validation Queries

Use these to rerun or challenge the Clone Spec.

```text
site:openjdk.org/groups/hotspot/docs RuntimeOverview HotSpot interpreter thread management fatal errors
site:openjdk.org/jeps/3 "Release Candidate" "six months"
site:docs.python.org/3/library/gc.html "Changed in version" "garbage collector"
site:github.com/python/cpython InternalDocs compiler bytecode CFG
site:go.dev/doc/gc-guide GOGC GOMEMLIMIT allocation rate
site:go.dev/ref/mod "minimal version selection" "build list"
site:doc.rust-lang.org/cargo/reference/resolver.html "Cargo.lock" "heuristics"
site:docs.npmjs.com/cli/v11/configuring-npm/package-lock-json integrity resolved lockfileVersion
site:v8.dev/blog/maglev Ignition Sparkplug TurboFan Maglev
site:nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick "libuv" "timer"
site:docs.libuv.org/en/v1.x/threadpool.html UV_THREADPOOL_SIZE default
site:docs.rs/tokio/latest/tokio/runtime "work-stealing" "current-thread"
site:google.github.io/tcmalloc/design.html "per-CPU" "size classes"
site:jemalloc.net fragmentation scalable concurrency
site:microsoft.github.io/mimalloc free list sharding eager page purging
site:github.com/brettwooldridge/HikariCP keepalive connection pool
```

## 14. QA Report

| Check | Result | Notes |
|---|---|---|
| Coverage | Pass | Each normalized layer 16 has at least one T0/T2/T3 public source. |
| Critical Claim | Pass | Major claims C01–C12 are A/B confidence and use official/OSS sources. |
| Recency | Partial pass | npm v11 docs and Rust std 1.95.0 are current as of 2026; some historical design posts such as V8 Orinoco/Maglev are used as architecture/history evidence, not as current implementation guarantees. |
| Exceptions | Pass | Experimental JIT/AOT, lockfile conventions, disabled GC, serverless/no-pool cases are separated. |
| Failure | Pass | GC pause, allocator fragmentation, resolver conflict, pool exhaustion, event-loop blocking, feature rollback are included. |
| Provenance | Pass | Source catalog maps each claim to public evidence. |
| Registry Integrity | Pass | Layer IDs 16 are unique and mapped to one normalized layer each. |
| Output Integrity | Pass | Clone Spec fields, metrics, failure modes, anti-patterns, maturity, implementation guide, and validation queries are included. |

## 15. Confidence & Unknowns

### Confidence A

- VM/runtime subsystem model from HotSpot, Go runtime, V8, and CPython docs.
- Compiler pipeline and IR/verifier principles from LLVM, Go, CPython, rustc.
- Package metadata/lockfile/resolver core from Cargo, npm, Go modules, pip.
- GC/allocator/thread/async control points from official docs.

### Confidence B

- Connection-pool frontier model from HikariCP and Java SQL APIs; precise settings are workload-specific.
- JIT/AOT operating model from V8/CPython/JDK/LLVM; exact thresholds are implementation-specific.

### Confidence C

- Organization design assumptions such as runtime council composition and review meeting cadence. These are inferred from public governance and engineering artifacts, not directly observable for all exemplars.

### Unknowns / Additional Research

- Exact private tuning thresholds for JIT promotion, GC heuristics, allocator cache sizing, and pool sizing.
- Internal release-review boards and exception approval processes for each exemplar.
- Production incident rates for individual runtimes and package managers.
- Security hardening choices for executable memory/JIT in private production environments.
- Enterprise registry mirroring, provenance signing, and policy engine details beyond public docs.
