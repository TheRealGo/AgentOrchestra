# OS・Linux・システム管理 — Frontier Operating Model Research

対象レイヤー: **18**  
対象単位: **OS・Linux・システム管理**  
作成日: **2026-05-13 JST**  
調査方式: 公開情報限定。公式ドキュメント、標準、man-pages、Linux kernel docs、ディストリビューション公式文書、IETF RFC、systemd 公式/一次 man-page を優先。

---

## 0. Scope

本調査は、OS・Linux・システム管理を「アプリケーション、ユーザ、サービス、ハードウェア、ネットワークを、カーネルとディストリビューションの公開インターフェースを通じて、安全・再現可能・観測可能に制御する意思決定システム」として再構成する。

対象サブテーマは、次の 24 レイヤーとして扱う。

| Layer ID | Layer Name | Decision Object |
|---:|---|---|
| 18.01 | user space | アプリケーションとライブラリが、カーネル境界をどう利用し、どこまでをユーザ空間責任にするか |
| 18.02 | kernel | カーネルをどの構成・バージョン・サポート系列で運用するか |
| 18.03 | system call | syscall / libc wrapper / UAPI をどう設計・利用・制限するか |
| 18.04 | process | プロセス生成、終了、namespace、cgroup、権限境界をどう制御するか |
| 18.05 | thread | thread / clone flags / shared resources をどう分離・共有するか |
| 18.06 | scheduler | CPU 時間、公平性、latency、priority をどう配分するか |
| 18.07 | virtual memory | 仮想アドレス、page table、mmap、swap をどう管理するか |
| 18.08 | memory manager | 物理メモリ、slab、page cache、reclaim、OOM をどう運用するか |
| 18.09 | file descriptor | FD lifetime、open file description、dup/fork/exec 境界をどう管理するか |
| 18.10 | socket | endpoint、protocol family、nonblocking I/O、socket lifecycle をどう設計するか |
| 18.11 | filesystem | VFS、mount、namespace、FHS、path lookup をどう標準化するか |
| 18.12 | device driver | driver model、device registration、sysfs ABI をどう設計・維持するか |
| 18.13 | OS log | kernel log、journal、syslog、監査ログをどう収集・検索・保全するか |
| 18.14 | time sync | system clock、RTC、NTP/SNTP、chrony/timesyncd をどう同期するか |
| 18.15 | shell | POSIX shell / Bash / automation scripts をどう運用標準化するか |
| 18.16 | user | UID、login account、shadow password、home、shell をどう管理するか |
| 18.17 | group | GID、supplementary group、user private group、権限委譲をどう管理するか |
| 18.18 | service manager | init、PID 1、unit、dependency、restart、activation をどう制御するか |
| 18.19 | cgroup / resource control | CPU、memory、I/O、PIDs、delegation を unit / scope / slice にどう割り当てるか |
| 18.20 | OS package manager | package metadata、依存関係、upgrade、remove、autoremove をどう実行するか |
| 18.21 | package trust / signature | repository metadata、Release file、GPG/RPM signature をどう検証するか |
| 18.22 | OS release / lifecycle | kernel / distro の stable、longterm、EOL、backport をどう選ぶか |
| 18.23 | kernel tunables / admin interfaces | `/proc`, `/sys`, `sysctl` をどう変更・監査・ロールバックするか |
| 18.24 | operational runbooks | 上記を production で変更する際の承認、観測、復旧、検証をどう標準化するか |

---

## 1. Executive Summary

OS・Linux・システム管理の frontier pattern は、**kernel boundary を直接操作するのではなく、安定した UAPI、man-pages、systemd unit、package metadata、cgroup、journal、time sync、policy-as-documents を介して、変更可能性と安全性を両立する**ことである。

この領域の優れた主体は、Linux kernel を単なる「OS コア」としてではなく、次の 4 つの contract の集合として扱う。

1. **User-space contract**: syscall、glibc wrapper、man-pages、UAPI、ABI stability。
2. **Resource contract**: process/thread、scheduler、VM、memory、FD、socket、cgroup。
3. **Operations contract**: filesystem hierarchy、mount、device/sysfs、systemd、journal、time sync、package manager。
4. **Change-control contract**: release lifecycle、signature verification、sysctl / procfs / sysfs change policy、rollback、observability。

最も重要な設計判断は、次の 6 点である。

| Priority | Frontier Decision Rule | Rationale |
|---:|---|---|
| 1 | **Kernel 内部実装ではなく、公開 UAPI / man-pages / stable ABI を運用境界にする** | Linux kernel docs は user-space API を man-pages と併用し、ABI 文書は stable/testing/obsolete/removed を分ける。内部実装依存は移植性とアップグレード性を壊す。 |
| 2 | **process / thread / FD / socket / mount / cgroup の共有境界を明文化する** | `clone(2)` flags、FD / open file description、mount namespace、cgroup v2 は、共有と隔離の正確な制御面である。 |
| 3 | **service manager を PID 1 の unit graph として扱い、個別 daemon 管理にしない** | systemd は service、socket、mount、timer、resource control、journal を unit と依存関係に正規化する。 |
| 4 | **ログは text stream ではなく、kernel / journal / syslog / audit の複数 channel と retention policy として設計する** | journald は structured / indexed journal を提供し、syslog は RFC 5424 で protocol と structured data を定義する。 |
| 5 | **時刻同期と package trust を初期構築の一部にする** | NTP / chrony / timesyncd は証明書検証、ログ時系列、分散システム整合性の前提であり、APT/RPM/DNF は署名・metadata 検証が trust root である。 |
| 6 | **`/proc`, `/sys`, `sysctl`, mount, package upgrade は change-management 対象にする** | これらは即時に production behavior を変え得るため、事前検証、変更記録、ロールバック、監視が必須である。 |

---

## 2. Frontier Exemplars

| Candidate | Type | Why Frontier | Evidence Tier | Confidence |
|---|---|---|---|---|
| Linux kernel project | OSS / kernel | UAPI、scheduler、MM、VFS、driver model、admin guide を公式に文書化し、stable / longterm release channel を運用している | T0/T3 | A |
| Linux man-pages project | Documentation / interface | syscall、FD、socket、clone、mount、passwd などユーザ空間から観測可能な contract を正確に記述する | T0/T2 | A |
| glibc | libc / runtime | syscall wrapper と C library API の境界を明示し、raw syscall と library function の使い分けを規定する | T0/T2 | A |
| systemd project | init / service manager | PID 1、unit graph、service supervision、socket activation、cgroup-based resource control、journal を統合する | T0/T2/T3 | A |
| Debian / APT / Debian Policy | Distribution / package governance | package lifecycle、dependency、maintainer scripts、Release file authentication、policy conformance を明文化する | T0/T3 | A |
| Fedora / RPM / DNF | Distribution / package governance | RPM metadata/signature、DNF config、signature enforcement、repository trust を明文化する | T0/T3 | A |
| IETF NTP / Syslog standards | Standards | RFC 5905 と RFC 5424 が time sync と syslog protocol の標準語彙を提供する | T0 | A |
| Filesystem Hierarchy Standard | Standard | `/bin`, `/etc`, `/var`, `/usr`, `/run` などの配置原則を標準化する | T0 | A |
| chrony | Time synchronization | NTP server/client、reference clock、intermittent network、VM 環境を含む time sync 実装として広く使われる | T2/T3 | B |

---

## 3. Source Catalog

| Source ID | Source | Type | Evidence Tier | Directness | URL |
|---|---|---|---|---|---|
| S01 | Linux Kernel Documentation | official_doc | T0/T3 | direct | https://docs.kernel.org/ |
| S02 | Kernel.org Releases | release_note | T3 | direct | https://www.kernel.org/ |
| S03 | Linux Kernel User-space API Guide | official_doc | T0 | direct | https://docs.kernel.org/userspace-api/index.html |
| S04 | Linux Kernel ABI Documentation | official_doc | T0 | direct | https://docs.kernel.org/admin-guide/abi.html |
| S05 | Linux Kernel Memory Management Documentation | official_doc | T0/T3 | direct | https://docs.kernel.org/mm/index.html |
| S06 | CFS Scheduler Design | official_doc | T0/T3 | direct | https://docs.kernel.org/scheduler/sched-design-CFS.html |
| S07 | EEVDF Scheduler Documentation | official_doc | T0/T3 | direct | https://docs.kernel.org/scheduler/sched-eevdf.html |
| S08 | Linux VFS Documentation | official_doc | T0/T3 | direct | https://docs.kernel.org/filesystems/vfs.html |
| S09 | Linux Driver API | official_doc | T0/T3 | direct | https://docs.kernel.org/driver-api/index.html |
| S10 | Linux Device Model | official_doc | T0/T3 | direct | https://docs.kernel.org/driver-api/driver-model/device.html |
| S11 | procfs Documentation | official_doc | T0/T3 | direct | https://docs.kernel.org/filesystems/proc.html |
| S12 | sysctl Documentation | official_doc | T0/T3 | direct | https://docs.kernel.org/admin-guide/sysctl/index.html |
| S13 | cgroup v2 Documentation | official_doc | T0/T3 | direct | https://docs.kernel.org/admin-guide/cgroup-v2.html |
| S14 | syscalls(2) | man_page | T0/T2 | direct | https://man7.org/linux/man-pages/man2/syscalls.2.html |
| S15 | syscall(2) | man_page | T0/T2 | direct | https://man7.org/linux/man-pages/man2/syscall.2.html |
| S16 | glibc Manual: System Calls | official_doc | T0/T2 | direct | https://sourceware.org/glibc/manual/2.43/html_node/System-Calls.html |
| S17 | clone(2) | man_page | T0/T2 | direct | https://man7.org/linux/man-pages/man2/clone.2.html |
| S18 | open(2) | man_page | T0/T2 | direct | https://man7.org/linux/man-pages/man2/open.2.html |
| S19 | socket(2) | man_page | T0/T2 | direct | https://man7.org/linux/man-pages/man2/socket.2.html |
| S20 | mount_namespaces(7) | man_page | T0/T2 | direct | https://man7.org/linux/man-pages/man7/mount_namespaces.7.html |
| S21 | mount(8) | man_page | T0/T2 | direct | https://man7.org/linux/man-pages/man8/mount.8.html |
| S22 | Filesystem Hierarchy Standard | standard | T0 | direct | https://specifications.freedesktop.org/fhs/latest/ |
| S23 | systemd.io | official_doc | T0/T3 | direct | https://systemd.io/ |
| S24 | systemd(1) | man_page | T0/T2 | direct | https://man7.org/linux/man-pages/man1/systemd.1.html |
| S25 | systemd.service(5) | man_page | T0/T2 | direct | https://man7.org/linux/man-pages/man5/systemd.service.5.html |
| S26 | systemd.resource-control(5) | man_page | T0/T2 | direct | https://man7.org/linux/man-pages/man5/systemd.resource-control.5.html |
| S27 | systemd-journald.service(8) | man_page | T0/T2 | direct | https://man7.org/linux/man-pages/man8/systemd-journald.service.8.html |
| S28 | journalctl(1) | man_page | T0/T2 | direct | https://man7.org/linux/man-pages/man1/journalctl.1.html |
| S29 | dmesg(1) | man_page | T0/T2 | direct | https://man7.org/linux/man-pages/man1/dmesg.1.html |
| S30 | RFC 5424 Syslog Protocol | standard | T0 | direct | https://datatracker.ietf.org/doc/html/rfc5424 |
| S31 | RFC 5905 NTPv4 | standard | T0 | direct | https://datatracker.ietf.org/doc/html/rfc5905 |
| S32 | chrony Project | official_doc | T2/T3 | direct | https://chrony-project.org/ |
| S33 | systemd-timesyncd(8) | man_page | T0/T2 | direct | https://manpages.debian.org/trixie/systemd-timesyncd/systemd-timesyncd.8.en.html |
| S34 | GNU Bash Manual | official_doc | T0/T2 | direct | https://www.gnu.org/software/bash/manual/bash.html |
| S35 | passwd(5) | man_page | T0/T2 | direct | https://man7.org/linux/man-pages/man5/passwd.5.html |
| S36 | Red Hat Managing Users and Groups | official_doc | T3 | direct | https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/7/html/system_administrators_guide/ch-managing_users_and_groups |
| S37 | apt(8) | man_page | T0/T2 | direct | https://manpages.debian.org/trixie/apt/apt.8.en.html |
| S38 | apt-secure(8) | man_page | T0/T2 | direct | https://manpages.debian.org/testing/apt/apt-secure.8.ja.html |
| S39 | DNF Command Reference | official_doc | T0/T2 | direct | https://dnf.readthedocs.io/en/latest/command_ref.html |
| S40 | DNF Configuration Reference | official_doc | T0/T2 | direct | https://dnf.readthedocs.io/en/latest/conf_ref.html |
| S41 | Debian Policy Manual | policy | T0/T3 | direct | https://www.debian.org/doc/debian-policy/ |
| S42 | RPM Packaging Guide | official_doc | T3 | direct | https://rpm-packaging-guide.github.io/ |
| S43 | Fedora Signature Checking Change | official_doc | T3 | direct | https://fedoraproject.org/wiki/Changes/Enforcing_signature_checking_by_default |

---

## 4. Evidence Map

| Claim ID | Layer(s) | Claim | Evidence | Confidence |
|---|---|---|---|---|
| C001 | 18.01–18.03 | Linux user-space contract は、kernel docs、man-pages、glibc wrapper、UAPI/ABI docs の組み合わせで把握するべきである | S01, S03, S04, S14, S16 | A |
| C002 | 18.03 | アプリケーションは通常 libc wrapper を使い、raw syscall は例外的に扱うべきである | S15, S16 | A |
| C003 | 18.04–18.05 | process/thread の分離・共有は `clone(2)` flags によって file descriptor、filesystem state、memory、cgroup、namespace 単位で決まる | S17 | A |
| C004 | 18.06 | Linux scheduler は CFS から EEVDF へ公平性と latency control の設計を発展させている | S06, S07 | A |
| C005 | 18.07–18.08 | MM subsystem は page table、process address、page allocation、slab、reclaim、swap、page cache、OOM を統合的に扱う | S05 | A |
| C006 | 18.09 | FD は process-local な integer handle だが、open file description は dup/fork で共有され得る | S18 | A |
| C007 | 18.10 | socket は communication endpoint を作成し、FD として返され、domain/type/protocol で意味が決まる | S19 | A |
| C008 | 18.11 | filesystem は VFS abstraction、path lookup、mount namespace、FHS を分けて設計する必要がある | S08, S20, S21, S22 | A |
| C009 | 18.12 | device driver は driver model と sysfs ABI を通じて管理され、sysfs に内部実装を漏らすべきではない | S09, S10, S04 | A |
| C010 | 18.13 | OS logging は kernel ring buffer、journald、journalctl、RFC 5424 syslog の複数面を統合する必要がある | S27, S28, S29, S30 | A |
| C011 | 18.14 | time sync は NTPv4、chrony、systemd-timesyncd の capabilities 差を理解して選ぶ必要がある | S31, S32, S33 | A |
| C012 | 18.15 | shell は interactive 操作と automation の両方の入口であり、Bash 仕様と POSIX 互換性の差を標準化する必要がある | S34 | B |
| C013 | 18.16–18.17 | user/group は `/etc/passwd`, shadow password, UID/GID, user private group, umask, validation utilities で管理される | S35, S36 | A |
| C014 | 18.18–18.19 | systemd は PID 1 として units、service supervision、dependency、activation、cgroup resource control を管理する | S23, S24, S25, S26 | A |
| C015 | 18.20–18.21 | package manager は dependency resolution だけでなく、repository metadata / package signature / Release file verification を trust root とする | S37, S38, S39, S40, S42, S43 | A |
| C016 | 18.22 | kernel / distro release は latest 追随ではなく stable / longterm / distro kernel support channel の選定で運用する | S02 | A |
| C017 | 18.23–18.24 | `/proc`, `/sys`, `sysctl`, mount, package upgrade は production behavior を即時に変更し得るため、change-management と rollback 対象にする | S11, S12, S21, S37, S38 | A |

---

## 5. Layer Registry

### 18.01. user space

**Definition**  
user space は、アプリケーション、shell、library、daemon、package-managed binary が動作する非 kernel 領域であり、kernel services へは syscall、libc wrapper、device files、procfs/sysfs、socket、filesystem、systemd unit などを通じてアクセスする。

**Decision Question**  
どの機能を application/library/service 側に置き、どの機能を kernel / service manager / package manager の公開 interface に委譲するか。

**Inputs**  
application requirements、security boundary、syscall availability、distribution support、library ABI、container / namespace boundary、observability requirements。

**Outputs**  
binary、shared library、service unit、shell script、package metadata、runtime config、log stream。

**Owner Roles**  
platform engineer、SRE、application owner、security engineer、release engineer。

**Default Metrics**  
crash rate、syscall error rate、startup latency、dependency freshness、privilege boundary violations、supportability。

**Decision Rules**

- libc wrapper が存在するなら raw syscall より wrapper を優先する。
- kernel internal headers / private implementation に依存しない。
- service behavior は unit file と config file に落とし、手動 shell 手順へ閉じ込めない。
- user-space component の dependency と package provenance を package manager で管理する。

**Failure Modes**

- kernel version 固有挙動へ暗黙依存する。
- shell script が interactive 前提で automation に失敗する。
- systemd unit 外で daemon を起動し、restart / logging / cgroup control から外れる。

### 18.02. kernel

**Definition**  
kernel は、process、scheduler、memory、filesystem、device、network、security、cgroup、syscall interface を管理する OS 中核である。

**Decision Question**  
どの kernel version / config / module / patch / support channel を採用し、どの UAPI と ABI を production contract とするか。

**Inputs**  
hardware support、distribution kernel、CVE / security advisory、LTS / longterm EOL、driver requirements、performance profile、container requirements。

**Outputs**  
kernel package、module policy、boot config、sysctl baseline、ABI compatibility matrix、rollback kernel。

**Decision Rules**

- production では distribution-supported kernel または longterm/stable channel を基準にする。
- mainline/latest は検証環境または明示的な hardware / feature requirement がある場合に限定する。
- kernel internal API を user-space contract と見なさない。
- upgrade は bootloader rollback と observability を準備してから行う。

**Failure Modes**

- driver / kernel ABI mismatch。
- rollback kernel を残さず upgrade する。
- config drift により security hardening または hardware support が消える。

### 18.03. system call

**Definition**  
system call は、user-space process が kernel service を要求する fundamental interface である。Linux では多くの場合 glibc wrapper を通じて呼ばれる。

**Decision Question**  
アプリケーションは syscall をどの abstraction で利用し、どの error semantics / privilege / seccomp / ABI boundary を前提にするか。

**Inputs**  
required kernel service、libc support、syscall availability、architecture、errno behavior、seccomp policy、container profile。

**Outputs**  
libc API use、raw syscall exception list、seccomp allowlist、error handling policy、compatibility tests。

**Decision Rules**

- 通常は libc wrapper を使い、raw `syscall(2)` は wrapper 不在・特殊用途・feature probe に限定する。
- errno と partial failure を前提に retry / fallback を設計する。
- syscall availability は kernel version と architecture に依存し得るため feature detection を行う。
- seccomp profile は application の actual syscall surface から生成・検証する。

**Failure Modes**

- syscall number を architecture independent と誤認する。
- wrapper と raw syscall の semantic difference を無視する。
- ENOSYS / EPERM / EINVAL を同じ障害として扱う。

### 18.04. process

**Definition**  
process は address space、FD table、credentials、namespace、signal disposition、cgroup membership などを持つ execution unit である。

**Decision Question**  
プロセス生成・監督・終了・隔離・resource assignment を、どの primitive と service manager で制御するか。

**Inputs**  
service topology、privilege model、namespace requirements、resource budgets、restart policy、signal semantics、logging requirements。

**Outputs**  
service unit、fork/exec policy、namespace/cgroup config、PID tracking、health check、shutdown procedure。

**Decision Rules**

- long-running process は systemd unit または container runtime 管理に置く。
- fork/daemonize の legacy behavior は unit type と PID tracking に明示する。
- process isolation は namespace、cgroup、credentials、mount の組み合わせで定義する。
- graceful shutdown signal と timeout を標準化する。

**Failure Modes**

- orphan process / zombie process。
- supervisor が main PID を誤認する。
- process が unit cgroup から外れて resource control と logging を失う。

### 18.05. thread

**Definition**  
thread は process 内または clone-based execution context として、memory、FD、filesystem state、signal handling、TLS などを共有し得る execution unit である。

**Decision Question**  
thread と process の境界を、どの shared resource と failure isolation の tradeoff で決めるか。

**Inputs**  
latency、parallelism、shared memory need、crash isolation、scheduler behavior、runtime library、debuggability。

**Outputs**  
thread pool policy、clone flag policy、stack sizing、affinity/priority config、deadlock diagnostics。

**Decision Rules**

- memory sharing が必要な場合だけ thread を選ぶ。failure isolation が重要なら process 分離を優先する。
- shared FD / cwd / signal / memory の影響を設計レビューで確認する。
- thread pool は unbounded にせず、CPU / I/O profile に応じて上限を持つ。
- cancellation と shutdown は explicit protocol にする。

**Failure Modes**

- FD / cwd / signal handler の shared-state bug。
- thread leak による memory / scheduler pressure。
- priority inversion や lock contention。

### 18.06. scheduler

**Definition**  
scheduler は runnable task に CPU time を割り当て、公平性、latency、throughput、priority、real-time constraints を制御する subsystem である。

**Decision Question**  
workload に応じて、どの scheduling class、priority、CPU affinity、cgroup CPU control、latency hint を使うか。

**Inputs**  
CPU saturation、latency SLO、interactive vs batch workload、NUMA、container density、priority model、real-time need。

**Outputs**  
CPU quota / weight、nice level、scheduler policy、affinity、latency test、runqueue metrics。

**Decision Rules**

- general-purpose workloads は default scheduler と cgroup CPU controls で扱い、real-time policy は限定的に使う。
- latency-sensitive workload は CPU saturation と runqueue length を常時観測する。
- CPU quota は hard cap として、CPU weight は relative share として扱う。
- scheduler tuning は benchmark と rollback を伴う change とする。

**Failure Modes**

- CPU quota による throttling が latency を悪化させる。
- noisy neighbor を CPU weight だけで抑えようとする。
- real-time priority の誤用で system responsiveness を壊す。

### 18.07. virtual memory

**Definition**  
virtual memory は process address space、page table、mmap、anonymous/file-backed memory、copy-on-write、swap を通じて memory abstraction を提供する。

**Decision Question**  
各 workload の address space と memory mapping を、performance、isolation、overcommit、swap、page fault behavior の観点でどう制御するか。

**Inputs**  
working set、allocation pattern、mmap usage、huge page need、swap policy、container memory limit、OOM tolerance。

**Outputs**  
vm sysctl baseline、memory limit、swap setting、mmap policy、memory pressure alert、OOM runbook。

**Decision Rules**

- workload の working set と memory limit を測定してから overcommit / swap / hugepage を変更する。
- file-backed page cache と anonymous memory を区別して capacity planning する。
- page fault、major fault、RSS、PSS、swap-in/out を観測する。
- container memory limit と host memory policy の二重制約をレビューする。

**Failure Modes**

- free memory の見かけだけで capacity を判断する。
- page cache reclaim と memory leak を混同する。
- overcommit と OOM killer behavior を未検証のまま production に適用する。

### 18.08. memory manager

**Definition**  
memory manager は physical memory、page allocator、slab allocator、reclaim、compaction、swap、page cache、OOM を扱う kernel subsystem である。

**Decision Question**  
システム全体の physical memory を、どの allocator、reclaim、limit、pressure、failure policy で運用するか。

**Inputs**  
RAM size、NUMA topology、slab growth、page cache behavior、kernel memory, cgroup limits、memory pressure events。

**Outputs**  
capacity model、memory alert thresholds、OOM policy、cgroup memory controls、kernel tunable change record。

**Decision Rules**

- memory pressure は `MemAvailable`、major fault、swap activity、cgroup OOM、slab growth を組み合わせて判断する。
- OOM は事故ではなく、限界条件として runbook 化する。
- kernel memory / slab の増加も application memory と同じく監視対象にする。
- memory tunables は change window と rollback を持つ。

**Failure Modes**

- cgroup memory limit を設定しても host 全体の pressure を見ない。
- swap 無効化で OOM 頻度を上げる。
- slab leak / file cache growth / application leak を切り分けない。

### 18.09. file descriptor

**Definition**  
file descriptor は process 内の integer handle であり、open file description、socket、pipe、eventfd など kernel object への参照を表す。

**Decision Question**  
FD の open/close、inheritance、duplication、limit、nonblocking、CLOEXEC をどう制御するか。

**Inputs**  
concurrency、socket count、file handle count、fork/exec usage、library behavior、ulimit、leak risk。

**Outputs**  
FD limit、CLOEXEC policy、leak detection、lsof/sof diagnostics、nonblocking I/O policy。

**Decision Rules**

- long-running service は FD leak test と limit alert を持つ。
- fork/exec する process では CLOEXEC を原則にする。
- socket / file / pipe / eventfd を同じ FD namespace で capacity planning する。
- open file description sharing を理解し、offset / status flag の共有に注意する。

**Failure Modes**

- `Too many open files` が出るまで検知しない。
- exec 後に secret FD を子プロセスへ漏らす。
- FD と open file description の違いを誤解する。

### 18.10. socket

**Definition**  
socket は communication endpoint であり、domain、type、protocol によって network / IPC semantics が決まる FD である。

**Decision Question**  
どの protocol family、blocking mode、buffer、timeout、backlog、lifecycle を採用するか。

**Inputs**  
latency、throughput、protocol、connection count、failure domain、TLS, DNS, retry, kernel limits。

**Outputs**  
socket config、timeout policy、listen backlog、keepalive、epoll/poll design、network error runbook。

**Decision Rules**

- socket I/O は timeout と cancellation を必須にする。
- high concurrency では nonblocking I/O と event loop / thread pool の設計を明示する。
- network failure は transient と permanent に分け、retry と circuit breaker を標準化する。
- socket FD も FD limit の一部として扱う。

**Failure Modes**

- default timeout なしで thread / FD を枯渇させる。
- backlog / ephemeral port / conntrack / DNS failure をアプリケーション障害と誤認する。
- TCP keepalive と application heartbeat を混同する。

### 18.11. filesystem

**Definition**  
filesystem は VFS abstraction、path lookup、inode/dentry、mount、namespace、storage backend、directory hierarchy を統合する layer である。

**Decision Question**  
ファイル配置、mount topology、namespace isolation、filesystem type、permissions、backup/recovery をどう設計するか。

**Inputs**  
FHS requirements、data durability、container mount、read-only root、tmpfs usage、backup, inode pressure、storage performance。

**Outputs**  
filesystem layout、fstab、mount units、backup policy、permission model、namespace runbook。

**Decision Rules**

- directory semantics は FHS と distribution conventions に合わせる。
- mount changes は namespace と propagation を明示する。
- `/proc`, `/sys`, `/dev`, `/run`, `/var` の意味を区別する。
- `fstab` と mount units は boot-time failure impact を検証する。

**Failure Modes**

- bind mount / namespace propagation を誤り、意図せず host path を露出する。
- storage full と inode exhaustion を区別しない。
- `/tmp`、`/var`、`/run` の lifecycle を誤解する。

### 18.12. device driver

**Definition**  
device driver は kernel と hardware/device abstraction を接続し、driver model、bus、device registration、sysfs、module lifecycle を通じて管理される。

**Decision Question**  
どの driver / module / firmware / sysfs ABI を採用し、kernel upgrade と device compatibility をどう維持するか。

**Inputs**  
hardware inventory、kernel version、module support、firmware、udev rules、sysfs attributes、vendor support、security advisories。

**Outputs**  
driver matrix、module allow/deny list、firmware baseline、udev rules、sysfs change policy、rollback plan。

**Decision Rules**

- driver compatibility は kernel release と distribution support channel に紐づける。
- sysfs は user-space-visible ABI として扱い、内部構造依存にしない。
- module loading policy は security boundary の一部として管理する。
- hardware rollout は driver + firmware + kernel + observability をセットで検証する。

**Failure Modes**

- kernel upgrade 後に out-of-tree driver が壊れる。
- sysfs attribute を内部実装として勝手に解釈する。
- module autoloading が攻撃面を広げる。

### 18.13. OS log

**Definition**  
OS log は kernel ring buffer、systemd journal、syslog、audit、application stdout/stderr を含む operational evidence layer である。

**Decision Question**  
どの log source を、どの format、retention、index、correlation、privacy policy で収集・検索・保全するか。

**Inputs**  
incident response needs、compliance、retention、storage capacity、PII policy、service topology、time sync quality。

**Outputs**  
journald config、syslog forwarding、log retention、field taxonomy、alert rules、incident evidence pack。

**Decision Rules**

- boot / kernel / service / application の log channel を分けて保存する。
- journald field と syslog structured data を活用し、plain text grep だけに依存しない。
- clock sync status を log trustworthiness の前提にする。
- retention と privacy redaction を policy として文書化する。

**Failure Modes**

- log rotation / retention の誤設定で incident evidence を失う。
- local time 表示と monotonic / realtime clock の差を誤認する。
- high-volume logs が disk full を引き起こす。

### 18.14. time sync

**Definition**  
time sync は system clock、RTC、NTP/SNTP、chrony、systemd-timesyncd、time zone を管理し、分散システムの時系列整合性を支える layer である。

**Decision Question**  
どの time source と daemon を採用し、どの offset / drift / stratum / failover threshold で運用するか。

**Inputs**  
network stability、VM/container environment、compliance、log ordering、TLS/certificate needs、latency measurement precision。

**Outputs**  
NTP server list、chrony/timesyncd config、offset alert、drift monitoring、time incident runbook。

**Decision Rules**

- production server は offset / drift / stratum / synchronization status を監視する。
- simple SNTP で足りる環境と、chrony 等の full NTP implementation が必要な環境を分ける。
- large clock step と gradual slew の影響を application に伝える。
- time sync failure は certificate validation、distributed tracing、log ordering に直結する重大障害として扱う。

**Failure Modes**

- time daemon が起動しているだけで同期済みと見なす。
- VM suspend/resume や network partition 後の clock step を未検証にする。
- timezone と system clock sync を混同する。

### 18.15. shell

**Definition**  
shell は command interpreter であり、interactive operation、scripting、service hooks、package maintainer scripts、automation runbooks の実行基盤である。

**Decision Question**  
どの shell dialect、error handling、environment、privilege boundary、script style を標準とするか。

**Inputs**  
POSIX compatibility、Bash features、automation target、privilege requirements、CI/CD, distribution shell defaults。

**Outputs**  
shell style guide、script templates、lint/test policy、environment policy、sudo/runuser boundary。

**Decision Rules**

- portable script は POSIX shell、Bash-specific script は shebang と dependency を明示する。
- production script は `set -e` 等の単純適用だけでなく、error handling と idempotency を明示する。
- environment variables、PATH、locale、umask を script 内または unit で固定する。
- shell script は change-controlled artifact とし、対話手順をそのまま貼らない。

**Failure Modes**

- `/bin/sh` と Bash の差異で script が壊れる。
- unquoted variables / glob expansion / word splitting による事故。
- sudo と environment inheritance の誤用。

### 18.16. user

**Definition**  
user は UID、login name、password/shadow state、home、shell、primary group、supplementary group、service account 属性を持つ identity object である。

**Decision Question**  
human user と service account を、どの UID/GID、認証、権限、lifecycle、audit policy で管理するか。

**Inputs**  
joiner/mover/leaver、service ownership、least privilege、MFA/SSH policy、password lock state、home directory、shell access。

**Outputs**  
account policy、UID range、service account registry、sudo policy、deprovision checklist、audit log。

**Decision Rules**

- human account と service account を分離する。
- `/etc/passwd` は identity metadata、secret は shadow mechanism に置く。
- login shell、home、sudo 権限、SSH key を lifecycle 管理する。
- inactive / orphan account を定期検出する。

**Failure Modes**

- shared account による accountability loss。
- service account に interactive login を許す。
- UID reuse による file ownership の誤帰属。

### 18.17. group

**Definition**  
group は GID と membership による authorization aggregation であり、file permission、sudo、service access、collaboration boundary を制御する。

**Decision Question**  
どの権限を user 単位ではなく group 単位で付与し、membership lifecycle をどう監査するか。

**Inputs**  
role model、file ownership、service access、sudoers、user private group policy、umask、collaboration needs。

**Outputs**  
group registry、membership approval、periodic review、umask policy、sudoers fragments。

**Decision Rules**

- privilege は individual ではなく role/group 経由で付与する。
- user private group と shared group の目的を分ける。
- group membership は access review の対象にする。
- group deletion / GID reuse は file ownership impact を確認する。

**Failure Modes**

- stale group membership による privilege creep。
- broad group に sudo / production access を付ける。
- umask と group write の組み合わせを検証しない。

### 18.18. service manager

**Definition**  
service manager は PID 1 または init subsystem として、service lifecycle、dependency、activation、restart、logging、resource control を管理する。

**Decision Question**  
service をどの unit type、dependency graph、restart policy、environment、logging、resource control で定義するか。

**Inputs**  
service dependencies、start/stop order、readiness、socket activation need、restart tolerance、resource budget、log routing。

**Outputs**  
unit files、drop-ins、targets、timers、sockets、restart policy、health checks、runbook。

**Decision Rules**

- daemon は raw background process ではなく unit として定義する。
- `ExecStart`, `Type`, `Restart`, `TimeoutStopSec`, dependencies を明示する。
- `--runtime` と persistent changes を分ける。
- `--force` 等の destructive operation は change approval 対象にする。

**Failure Modes**

- service が起動順序に暗黙依存する。
- restart loop が障害を隠す。
- drop-in override が undocumented drift になる。

### 18.19. cgroup / resource control

**Definition**  
cgroup / resource control は process group に CPU、memory、I/O、PIDs などの resource accounting, limit, delegation を適用する mechanism である。

**Decision Question**  
service、container、session、batch job をどの resource domain に置き、どの limit / weight / accounting を適用するか。

**Inputs**  
resource budget、tenant priority、container density、SLO、noisy-neighbor risk、OOM behavior、delegation model。

**Outputs**  
slice/scope/service resource config、CPU/memory/I/O limits、accounting metrics、capacity dashboard。

**Decision Rules**

- unit-level resource control は service definition と同じ repository / config management に置く。
- hard limit と relative weight を混同しない。
- cgroup v2 hierarchy と delegation boundary を明確にする。
- resource accounting を有効化し、limit 前後の behavior を比較する。

**Failure Modes**

- memory limit が local OOM を起こし、service restart loop になる。
- CPU quota が latency SLO を壊す。
- container runtime と systemd cgroup 管理が衝突する。

### 18.20. OS package manager

**Definition**  
OS package manager は package metadata、dependency、repository、install/remove/upgrade、maintainer scripts、database を通じて system state を変更する mechanism である。

**Decision Question**  
どの repository と package set を trust し、upgrade / remove / autoremove / hold / pinning をどう運用するか。

**Inputs**  
repository policy、security updates、dependency graph、maintainer scripts、service impact、reboot requirement、rollback capability。

**Outputs**  
package baseline、repository list、pinning/hold policy、upgrade window、pre/post checks、rollback image。

**Decision Rules**

- package manager は single source of truth とし、manual binary copy を例外扱いにする。
- production upgrade は dependency diff、maintainer script impact、service restart impact を確認する。
- `apt` は end-user CLI として扱い、scripts では安定した lower-level tool を使う。
- package DB integrity と installed file verification を定期確認する。

**Failure Modes**

- untracked `/usr/local` binary が package-owned files と衝突する。
- autoremove で必要 dependency を消す。
- unattended upgrade が service restart / kernel reboot requirement を見落とす。

### 18.21. package trust / signature

**Definition**  
package trust は repository metadata、Release file、GPG key、RPM signature、TLS、policy enforcement によって package provenance を検証する layer である。

**Decision Question**  
どの repository/key/signature policy を採用し、署名失敗・key rotation・metadata mismatch をどう扱うか。

**Inputs**  
repository source、key ownership、Release metadata、package signature、repo_gpgcheck、GPG policy、mirror policy、TLS verification。

**Outputs**  
trusted key registry、repository allowlist、signature verification config、key rotation runbook、exception log。

**Decision Rules**

- unsigned repository / package は原則拒否する。
- key material は repository ごとに scope を限定し、global trust を避ける。
- Release info change や metadata signature failure は emergency bypass ではなく investigation 対象にする。
- internal repository も external repository と同等に署名・監査する。

**Failure Modes**

- key rotation を運用せず期限切れで update 停止。
- GPG check 無効化が恒久化する。
- mirror compromise と metadata mismatch を区別しない。

### 18.22. OS release / lifecycle

**Definition**  
OS release / lifecycle は kernel、distribution、package set、security support、EOL、backport、upgrade path を管理する layer である。

**Decision Question**  
どの release line を採用し、どの時点で upgrade / migration / decommission するか。

**Inputs**  
EOL date、security support、hardware support、application compatibility、vendor support、kernel longterm schedule、compliance requirements。

**Outputs**  
release matrix、EOL calendar、upgrade roadmap、compatibility tests、decommission plan。

**Decision Rules**

- latest ではなく support lifecycle と security patch availability を基準にする。
- distribution kernel と upstream kernel の responsibility boundary を明確にする。
- EOL 6–12 か月前に migration plan を開始する。
- longterm kernel の EOL 延長可能性は保証ではなく risk variable とする。

**Failure Modes**

- EOL 後も production 継続し、CVE patch が得られない。
- application compatibility test なしに major upgrade する。
- kernel upgrade と driver/firmware compatibility を分離して扱う。

### 18.23. kernel tunables / admin interfaces

**Definition**  
kernel tunables / admin interfaces は `/proc`, `/sys`, `sysctl`, module parameters, boot parameters など、runtime または boot-time で kernel behavior を変更する interface である。

**Decision Question**  
どの tunable を変更可能にし、変更権限、永続化、検証、ロールバックをどう定義するか。

**Inputs**  
performance bottleneck、security baseline、kernel docs、application requirement、benchmark, incident evidence。

**Outputs**  
sysctl baseline、proc/sys change log、sysfs change policy、boot parameter registry、rollback file。

**Decision Rules**

- sysctl は root 権限と専門知識が必要な runtime configuration として扱う。
- `/proc/sys` 書き換えは immediate impact を持つため、change-management 対象にする。
- sysfs は stable ABI と internal implementation を区別し、internal details を parse しない。
- tunable change は before/after metrics と rollback value を記録する。

**Failure Modes**

- blog post の sysctl 値を根拠なく全 host へ適用する。
- persistent config と runtime config が乖離する。
- reboot 後に消える変更を恒久設定と誤認する。

### 18.24. operational runbooks

**Definition**  
operational runbook は OS layer の変更・障害対応・復旧・検証を、誰がいつ何を見て何を戻すかまで定義した実行手順である。

**Decision Question**  
OS-level change と incident response を、どの approval、precheck、observability、rollback、postmortem process で制御するか。

**Inputs**  
change type、blast radius、SLO、service dependency、backup/rollback availability、monitoring, security risk。

**Outputs**  
runbook、precheck checklist、change record、rollback command、metric dashboard、post-change report。

**Decision Rules**

- kernel/package/mount/sysctl/service changes は precheck、canary、rollback を必須にする。
- runbook は manual command list ではなく、decision points と failure branches を含める。
- incident logs は journald/syslog/kernel log/time sync status を含めて evidence pack 化する。
- postmortem は runbook と monitoring thresholds に反映する。

**Failure Modes**

- reboot / service restart / package upgrade の blast radius を過小評価する。
- rollback command が存在するが検証されていない。
- monitoring が application metric だけで OS-level pressure を検知できない。

---

## 6. Clone Spec

### 6.1 Definition

OS・Linux・システム管理レイヤーは、Linux kernel、user-space、service manager、filesystem、identity、logging、time、package manager を統合し、production system の execution、resource、identity、storage、observability、change-control を制御する operating model である。

このレイヤーの優れた実装は、個別コマンド集ではなく、**contract、policy、instrumentation、rollback** の 4 点を中心に設計される。

### 6.2 Core Philosophy

1. **Stable interface first**  
   kernel internal ではなく、UAPI、man-pages、ABI docs、systemd unit、package metadata、standards を運用境界にする。

2. **Explicit ownership**  
   kernel、package、service、identity、logs、time、mount、sysctl の各 owner を分けるが、change approval は統一する。

3. **Everything observable**  
   process、scheduler、memory、FD、socket、filesystem、service、time、package state は観測できる前提で設計する。

4. **Default-deny for privilege and trust**  
   root 権限、service account、group membership、module loading、repository trust、signature exception は明示承認制にする。

5. **Runtime drift is a defect**  
   `/proc`, `/sys`, `sysctl`, `systemctl --runtime`, manual mount, manual binary install など runtime-only 変更は、恒久設定との差分として検出する。

6. **Upgrade is a reliability event**  
   kernel upgrade、package upgrade、systemd unit change、time daemon change、repository key change は、通常運用ではなく reliability event として扱う。

### 6.3 Decision Model

| Field | Specification |
|---|---|
| Inputs | workload SLO、security baseline、kernel/distro release、hardware inventory、package inventory、service graph、identity registry、log/time requirements、compliance requirements |
| Decision Object | OS-level execution and operations contract |
| Criteria | stability、security、observability、reproducibility、least privilege、recoverability、performance、supportability |
| Priorities | public interface > internal implementation; package-managed state > manual state; unit-managed service > orphan daemon; signed repository > ad-hoc binary; measured tuning > folklore tuning |
| Prohibitions | undocumented kernel internal dependency、untracked binary install、unsigned package source、shared human accounts、persistent GPG check disablement、unreviewed sysctl changes、manual daemonization outside service manager |
| Thresholds | kernel/distro EOL window、time offset alert、FD usage threshold、memory pressure threshold、package signature failure = block、service restart loop threshold、disk/inode usage threshold |
| Owners | platform owner、SRE、security owner、release engineer、identity admin、network/storage owner、application owner |
| Reviewers | security, SRE, application owner, change manager, compliance when relevant |
| Cadence | daily monitoring; weekly package/security review; monthly account/group review; quarterly OS baseline review; EOL roadmap review at least 6–12 months before deadline |
| Interfaces | syscalls、glibc、man-pages、procfs、sysfs、sysctl、systemd unit files、journalctl、package manager CLI/API、repository metadata、NTP/syslog protocols |
| Controls | configuration management、package lock/pinning、GPG/RPM signature enforcement、unit file review、resource controls、log retention、time sync monitoring、rollback kernel/package snapshot |
| Exceptions | break-glass root access、temporary unsigned repo exception、runtime unit override、emergency sysctl change、kernel boot parameter override; all require expiry and post-review |
| Metrics | uptime, MTTR, kernel/package patch latency, service restart count, OOM count, FD leak rate, time offset, disk/inode pressure, unauthorized account count, unsigned package attempts |

### 6.4 Operating Model

| Domain | Owner | Core Artifacts | Review Cadence | Primary Risk |
|---|---|---|---|---|
| Kernel & release | Platform / SRE | kernel matrix, boot config, rollback plan | Monthly + before upgrade | unpatched CVE, driver mismatch |
| User-space runtime | Platform / app owner | library baseline, syscall/seccomp profile | Per release | ABI mismatch, unsupported syscall |
| Process/service | SRE / app owner | systemd units, health checks, restart policy | Per service change | restart loop, orphan process |
| Resource control | SRE | cgroup/resource configs, capacity dashboard | Quarterly + SLO breach | noisy neighbor, OOM |
| Filesystem/mount | Platform/storage | fstab, mount units, backup policy | Per storage change | boot failure, data loss |
| Device/driver | Platform/hardware | driver/firmware matrix, module policy | Hardware rollout | unsupported module |
| Logging | SRE/security | journald/syslog config, retention policy | Quarterly | evidence loss, disk full |
| Time | SRE/platform | NTP/chrony/timesyncd config, offset alert | Monthly | log misordering, TLS failure |
| Identity | IAM/security | user/group registry, sudoers, SSH policy | Monthly | privilege creep |
| Package/trust | Release/security | repo allowlist, keys, pinning, upgrade runbook | Weekly security review | supply-chain compromise |
| Runbooks | SRE/change manager | precheck, rollback, postmortem templates | After every incident/change | untested recovery |

### 6.5 Technical Specification

#### 6.5.1 Kernel and UAPI Baseline

- Maintain a kernel support matrix including distribution kernel version, upstream base, patch source, EOL, hardware support, driver constraints, rollback version.
- Define allowed kernel modules and firmware sources.
- Track kernel parameters and sysctl values as versioned configuration.
- Treat UAPI / man-page-documented behavior as the contract; avoid parsing internal kernel data structures.
- For custom seccomp, profile actual syscall behavior in staging before production enforcement.

#### 6.5.2 Process, Thread, Scheduler, Memory

- All long-running daemons must be supervised by systemd or an equivalent service manager.
- Define service-specific resource budgets using cgroup controls.
- Monitor CPU saturation, run queue, throttling, memory pressure, major page faults, OOM kills, service restart loops.
- Maintain an OOM runbook covering cgroup OOM vs host OOM, victim identification, recent memory growth, swap state, and rollback.
- Thread pools must have upper bounds and shutdown semantics.

#### 6.5.3 FD, Socket, Filesystem

- Establish FD limits per service and alert at 70/85/95% usage.
- Enforce CLOEXEC by default where supported.
- Require explicit socket timeouts and retry policy.
- Track listen backlog, connection count, ephemeral port exhaustion, DNS failure, TLS failure separately.
- Version-control mount configuration and validate boot impact.
- Separate host mount namespace and container namespace assumptions.
- Follow FHS for OS-managed paths; use `/var` for variable state, `/etc` for host-specific config, `/run` for runtime state, and `/usr/local` only for policy-approved local software.

#### 6.5.4 Device Driver and Sysfs

- Maintain hardware inventory mapped to driver, module, firmware, kernel version, and support status.
- Do not treat arbitrary sysfs layout as stable unless documented as stable ABI.
- Require rollback kernel or module fallback for driver-sensitive upgrades.
- Lock down module loading where possible in high-security environments.

#### 6.5.5 Logging and Time

- Enable and monitor systemd journal, kernel ring buffer collection, syslog forwarding if required, and audit log if mandated.
- Define retention by incident response and compliance need, not by default disk size.
- Include time sync status in every incident evidence pack.
- Select time sync implementation based on need:
  - `systemd-timesyncd`: simple SNTP client use cases.
  - `chrony`: production environments requiring robust NTP behavior, intermittent network handling, VM suitability, server/peer/reference clock support.
  - specialized PTP/NTP architecture: sub-millisecond or regulated time requirements.

#### 6.5.6 Shell, User, Group

- Shell scripts must declare interpreter, set locale/PATH assumptions, handle failure explicitly, and be tested in CI where production-impacting.
- Human users and service accounts must be distinct.
- Shared accounts are disallowed except documented break-glass accounts with rotation and monitoring.
- Group membership must have owner, purpose, approver, and review date.
- Sudo privileges must be group-based and audited.

#### 6.5.7 Service Manager and Resource Control

- Unit files are source-controlled. Drop-ins are treated as configuration changes.
- Unit config must specify Type, dependencies, restart policy, timeout, environment source, logging behavior, and resource controls where relevant.
- Runtime-only changes require expiry.
- Resource controls must be documented as hard limit, soft share, or accounting-only.

#### 6.5.8 Package Manager and Trust

- Repository list and trust keys are source-controlled.
- Unsigned repository/package exceptions require time-limited approval and documented compensating controls.
- Package upgrade runbook must include dependency diff, service restart impact, kernel/reboot requirement, configuration file prompts, and rollback plan.
- Scripts should not use high-level interactive CLIs where official docs warn against scripting stability.
- Package drift detection should compare desired package baseline with installed database.

---

## 7. Metrics

| Category | Metric | Good Signal | Bad Signal |
|---|---|---|---|
| Kernel lifecycle | % hosts on supported kernel/distro | 100% supported | Any host past EOL |
| Patch latency | days from security advisory to patched | severity-based SLA met | critical patch > SLA |
| Service health | restart loop count | rare, investigated | repeated auto-restart without owner action |
| CPU | CPU throttling / run queue | within SLO | quota-induced latency |
| Memory | OOM kills, major faults, memory pressure | stable working set | rising faults/OOM without owner |
| FD | FD usage ratio, leak slope | stable under load | monotonic FD growth |
| Socket | connection count, timeout rate, backlog drops | bounded and explainable | no timeout / backlog saturation |
| Filesystem | disk/inode usage, mount failures | below threshold, all mounts verified | boot failure, inode exhaustion |
| Logs | log retention coverage, dropped logs | meets incident retention | dropped / truncated logs |
| Time | offset, stratum, synchronization status | offset within threshold | unsynchronized or high drift |
| Identity | stale accounts/groups | zero orphan privileged accounts | stale sudo/group membership |
| Package trust | signature verification failures | blocked and investigated | checks disabled |
| Drift | config vs runtime drift | minimal, explained | undocumented runtime overrides |
| Runbooks | rollback test success | tested for critical changes | untested rollback |

---

## 8. Failure Modes

| Failure Mode | Typical Trigger | Detection | Prevention / Control |
|---|---|---|---|
| Unsupported kernel in production | EOL ignored | release matrix audit | EOL calendar, migration roadmap |
| Driver breakage after kernel upgrade | out-of-tree module / firmware mismatch | boot logs, dmesg, hardware health | driver matrix, rollback kernel |
| Sysctl folklore tuning | copied values without measurement | performance regression, incident review | baseline, benchmark, rollback |
| FD leak | missing close, inherited FD | FD count growth, `lsof` | CLOEXEC, leak tests, alerts |
| Socket exhaustion | no timeouts, high connection churn | backlog drops, TIME_WAIT, port exhaustion | timeout policy, connection pooling |
| OOM kill | memory growth, cgroup limit | OOM log, service restart | memory budget, pressure alerts |
| Restart loop masking failure | aggressive Restart policy | systemd restart count | rate limits, alert on restarts |
| Package trust bypass | disabled gpgcheck / unsigned repo | config audit | signed repo policy, exception expiry |
| Log evidence loss | retention too short / disk full | missing incident logs | retention design, log volume limits |
| Time drift | daemon down, network partition | offset alert, unsynchronized status | redundant sources, chrony/timesyncd monitoring |
| Privilege creep | stale group membership | access review | owner/expiry/review process |
| Runtime drift | manual `systemctl --runtime`, manual mount | config drift scan | source-controlled config, expiry |

---

## 9. Anti-patterns

1. **“Linux だから同じ”と見なす**  
   distribution kernel、glibc、systemd version、package policy、SELinux/AppArmor、filesystem layout の差を無視する。

2. **root shell を運用モデルにする**  
   手作業コマンドで状態を変え、artifact と audit trail を残さない。

3. **kernel internal を API と誤認する**  
   `/sys` や `/proc` の内部表現を application logic の contract にする。

4. **package manager 外で本番 binary を置く**  
   provenance、upgrade、rollback、file ownership が壊れる。

5. **“起動している”を “正常” と扱う**  
   systemd active、time daemon running、journal present、NTP service enabled だけでは正常性を示さない。

6. **signature check を障害対応で無効化して戻さない**  
   supply-chain control の恒久的破壊になる。

7. **FD / socket / thread / memory を個別に見て capacity planning しない**  
   resource exhaustion はしばしば複合的に発生する。

8. **rollback を documentation だけにする**  
   bootable rollback kernel、package downgrade path、config restore を実地検証しない。

---

## 10. Maturity Model

| Level | Name | Criteria |
|---:|---|---|
| 0 | 未整備 | root 手作業中心。kernel/package/service/account/log の registry がない。 |
| 1 | 個人依存 | ベテランが運用を把握しているが、runbook と source-controlled config が不足。 |
| 2 | 文書化 | OS baseline、package list、service units、user/group policy、基本 runbook がある。 |
| 3 | 標準化 | kernel/distro lifecycle、package trust、systemd units、logging/time、sysctl、identity が標準管理される。 |
| 4 | 自動化・計測 | configuration management、drift detection、resource dashboards、package compliance、time/log health、rollback tests がある。 |
| 5 | 自律改善・業界先端 | SLO-driven OS tuning、canary upgrades、policy-as-code、automated evidence packs、postmortem-to-runbook feedback が常態化。 |

---

## 11. Clone Implementation Guide

### 0–30 days: Baseline and risk closure

1. OS inventory を作る: distro、kernel、systemd、glibc、package manager、release/EOL、hardware、driver。
2. service inventory を作る: unit、owner、restart policy、dependencies、logs、resource controls。
3. identity inventory を作る: human user、service account、sudo、groups、orphan/stale accounts。
4. package trust を確認する: repositories、keys、signature enforcement、unsigned exceptions。
5. time/log baseline を確認する: offset、time daemon、journald/syslog、retention、disk usage。
6. high-risk manual drift を検出する: runtime unit overrides、manual mounts、manual binaries、sysctl changes。

### 31–90 days: Standardization

1. Kernel/distro lifecycle matrix と upgrade policy を定義する。
2. systemd unit template と review checklist を作る。
3. sysctl / procfs / sysfs change policy を作る。
4. package upgrade runbook と rollback procedure を作る。
5. user/group lifecycle と access review を標準化する。
6. core OS metrics dashboard を作る: CPU, memory, FD, socket, disk/inode, service restarts, OOM, time offset, package compliance。

### 91–180 days: Automation and resilience

1. configuration management で OS baseline を適用する。
2. drift detection を自動化する。
3. canary upgrade と rollback test を導入する。
4. seccomp / cgroup / service sandboxing を workload 別に適用する。
5. log evidence pack generation と postmortem feedback loop を作る。
6. EOL 6–12 か月前の migration trigger を自動通知する。

---

## 12. Validation Queries

次のクエリを定期的に実行し、Clone Spec の前提を崩しに行く。

```text
site:docs.kernel.org "sysfs" "stable ABI" "obsolete"
site:docs.kernel.org "cgroup v2" "delegation" "no internal process"
site:docs.kernel.org "scheduler" "EEVDF" "CFS" after:2025-01-01
site:kernel.org "longterm" "EOL" "stable"
site:man7.org/linux/man-pages "clone" "CLONE_VM" "CLONE_FILES"
site:man7.org/linux/man-pages "open" "open file description" "CLOEXEC"
site:man7.org/linux/man-pages "systemd.service" "Restart" "TimeoutStopSec"
site:man7.org/linux/man-pages "systemd.resource-control" "MemoryMax" "CPUWeight"
site:manpages.debian.org "apt-secure" "Release" "signature"
site:dnf.readthedocs.io "gpgcheck" "repo_gpgcheck"
site:datatracker.ietf.org "RFC 5424" "structured data" "syslog"
site:datatracker.ietf.org "RFC 5905" "NTPv4"
"systemd" "incident" "restart loop" "postmortem"
"Linux kernel" "driver" "regression" "stable" "rollback"
"apt" "repository" "signature" "expired key" "incident"
```

---

## 13. Pattern Library

| Pattern ID | Pattern | Layer Scope | Description | Preconditions | Tradeoffs | Confidence |
|---|---|---|---|---|---|---|
| P001 | Public Interface Boundary | 18.01–18.03, 18.12–18.23 | Kernel internal ではなく man-pages / UAPI / stable ABI / systemd unit / package metadata を contract とする | 公式 docs と version inventory がある | 一部最適化は制限される | A |
| P002 | Unit-first Service Governance | 18.04, 18.18, 18.19 | daemon を unit graph、restart、logging、cgroup に載せる | systemd または同等 service manager | unit complexity が増える | A |
| P003 | Resource-as-SLO | 18.06–18.10, 18.19 | CPU/memory/FD/socket を SLO と capacity model に接続する | metrics が取れる | tuning overhead | B |
| P004 | Signed Supply Chain by Default | 18.20–18.21 | repository と package を署名検証し、例外を期限付きにする | repo/key registry | emergency friction | A |
| P005 | Time as Reliability Dependency | 18.13–18.14 | log, TLS, distributed tracing の前提として time sync を監視する | time daemon and offset metric | false positives in unstable networks | A |
| P006 | Runtime Drift is a Bug | 18.18, 18.23, 18.24 | runtime-only changes を差分として検出し、恒久設定へ反映または期限切れにする | config management | initial cleanup cost | B |
| P007 | Upgrade with Rollback Artifact | 18.02, 18.12, 18.20, 18.22, 18.24 | kernel/package/service changes は rollback kernel/snapshot/config を持って実施する | backup and test environment | slower upgrades | A |
| P008 | Identity Lifecycle Closure | 18.16–18.17 | human/service account separation, group review, sudo review を定期化する | IAM owner | operations overhead | A |

---

## 14. Confidence & Unknowns

### Confidence A

- syscall / FD / socket / clone / mount / passwd 等の interface は man-pages と kernel docs に直接記載がある。
- systemd の PID 1、unit、service、resource-control、journal は一次 man-pages と公式説明で裏付けられる。
- package trust は apt-secure、DNF config、RPM/Fedora/Debian docs で直接裏付けられる。
- time sync と syslog は RFC 5905 / RFC 5424 と実装ドキュメントで裏付けられる。

### Confidence B

- chrony を production-grade time sync の標準候補とする判断は、実装 capabilities と distro usage から強く推定できるが、全組織で唯一の正解ではない。
- cgroup resource controls の設定値や threshold は workload 依存であり、原則は A、具体値は B/C になる。
- shell scripting standard は Bash 公式 docs と POSIX shell knowledge に基づくが、組織の portability 要件に依存する。

### Unknowns

- 各 distribution の現行 release/EOL は個別確認が必要である。
- SELinux/AppArmor、auditd、container runtime、Kubernetes node OS hardening は本スコープに隣接するが、独立レイヤーとして深掘りすべきである。
- workload-specific sysctl values、scheduler tuning、memory overcommit policy は benchmark と production telemetry がなければ確定できない。
- commercial support contract や private vendor driver support は公開情報だけでは判断できない。

---

## 15. Minimal Runbook Templates

### 15.1 Kernel Upgrade Runbook

```text
1. Identify target kernel and support channel.
2. Verify hardware driver and firmware compatibility.
3. Check security advisory / changelog relevance.
4. Confirm rollback kernel in bootloader.
5. Apply to canary host.
6. Reboot canary and collect: dmesg, journal, service status, driver health, network/storage health.
7. Run workload smoke tests and performance checks.
8. Expand rollout by blast radius.
9. Keep previous kernel until stability window passes.
10. Record evidence and update kernel matrix.
```

### 15.2 Package Upgrade Runbook

```text
1. Refresh package metadata with signature verification enabled.
2. Review package diff, removed packages, new dependencies, maintainer scripts, config prompts.
3. Identify service restarts and reboot requirement.
4. Snapshot or ensure package rollback path.
5. Apply to canary.
6. Check journal, service status, application health, package database integrity.
7. Roll out in controlled waves.
8. Record package baseline and exceptions.
```

### 15.3 Sysctl Change Runbook

```text
1. Define problem and measurable target.
2. Locate official documentation for the tunable.
3. Record current value and persistence source.
4. Test in staging or canary.
5. Apply runtime value with rollback command ready.
6. Observe before/after metrics.
7. If successful, persist through config management.
8. If failed, revert and document.
```

### 15.4 Service Unit Change Runbook

```text
1. Review unit diff: Type, ExecStart, dependencies, Restart, Timeout, Environment, resource controls.
2. Validate syntax and reload daemon.
3. Apply to canary or single instance.
4. Restart or reload service according to dependency impact.
5. Observe status, journal, restart count, resource usage.
6. Roll back drop-in or unit file if needed.
7. Commit final unit and update runbook.
```

### 15.5 Time Sync Incident Runbook

```text
1. Check synchronization status, offset, stratum, selected source.
2. Inspect daemon logs and network reachability to time sources.
3. Check recent suspend/resume, VM migration, network partition, firewall changes.
4. Assess blast radius for TLS, logs, distributed tracing, database replication.
5. Restore sync or switch source.
6. Record offset window and impacted events.
7. Reconcile logs using monotonic timestamps where possible.
```

---

## 16. Final Operating Principle

OS・Linux・システム管理で frontier な運用は、チューニング値や個別コマンドの巧拙ではなく、**公開 contract に基づく変更可能な設計**で決まる。kernel、syscall、scheduler、memory、FD、socket、filesystem、driver、log、time、shell、identity、service manager、package manager は互いに独立していない。優れた運用モデルは、これらを単一の production control plane として扱い、変更前に意図を定義し、変更中に観測し、変更後に証拠を残し、失敗時に戻せる状態を保つ。
