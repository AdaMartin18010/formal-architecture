# 事务与隔离级别：ACID 的形式化

> **来源映射**: View/02.md §2.1.2, Struct/22-数据存储与数据库架构/00-总览-数据库系统的形式化分层.md
> **国际权威参考**: "A Critique of ANSI SQL Isolation Levels" (Berenson et al., ACM SIGMOD, 1995); "The Transaction Concept: Virtues and Limitations" (Jim Gray, VLDB 1981); CMU 15-445 / Berkeley CS186

---

## 一、知识体系思维导图

```text
事务与隔离级别
│
├─► ACID 性质
│   ├─ Atomicity (原子性): 全做或全不做
│   ├─ Consistency (一致性): 事务保持数据库不变式
│   ├─ Isolation (隔离性): 并发事务互不干扰
│   └─ Durability (持久性): 提交后数据永久保存
│
├─► 并发控制机制
│   ├─ 两阶段锁 (2PL - Two-Phase Locking)
│   │   ├─ 阶段1 (Growing): 获取锁，不释放锁
│   │   ├─ 阶段2 (Shrinking): 释放锁，不获取锁
│   │   └─ Strict 2PL: 锁持有到事务结束 (commit/abort)
│   ├─ MVCC (Multi-Version Concurrency Control)
│   │   ├─ 写不阻塞读，读不阻塞写
│   │   ├─ 每个事务看到数据的快照版本
│   │   └─ 垃圾回收: 移除不可见的旧版本
│   └─ Optimistic Concurrency Control
│       ├─ 执行不检查冲突
│       └─ 提交时验证，冲突则回滚
│
└─► 隔离级别与异常
    ├─ READ UNCOMMITTED: 允许脏读
    ├─ READ COMMITTED:   允许不可重复读
    ├─ REPEATABLE READ:  允许幻读 (Snapshot Isolation)
    └─ SERIALIZABLE:     无异常，等价串行执行
```

---

## 二、核心概念的形式化定义

### 2.1 ACID 的形式化

```text
定义 (事务 T):
  T = 一组操作序列 [o₁, o₂, ..., oₙ] where oᵢ ∈ {read(x), write(x), commit, abort}

  Atomicity:
    事务执行结果 state' ∈ {apply_all(T), state₀}
    即: 要么所有操作生效，要么全部不生效

  Consistency:
    设不变式集合 Invariants = {φ₁, φ₂, ..., φₖ}
    ∀state: state ⊨ Invariants → T(state) ⊨ Invariants
    (注意: 事务执行中间状态可暂时违反不变式)

  Isolation:
    并发执行等价于某个串行执行
    形式化: 历史 H 是串行化的 ⟺ H ≡ H_serial

  Durability:
    commit(T) → ∀后续读: read(x) 返回 T 写入的值
    (即使系统崩溃，已提交数据通过 WAL 恢复)
```

### 2.2 隔离异常的形式化

```text
定义 (脏读 Dirty Read):
  事务 T₂ 读取了 T₁ 未提交的数据:
    w₁(x) ... r₂(x) ... (a₁ or c₁) ...
  T₁ 若 abort: T₂ 读取了"从未存在"的数据

定义 (不可重复读 Non-Repeatable Read / Fuzzy Read):
  同一事务内两次读取同一数据得到不同结果:
    r₁(x) ... w₂(x) ... c₂ ... r₁(x)  且 r₁(x) ≠ r₁'(x)

定义 (幻读 Phantom Read):
  同一事务内两次查询条件得到不同行集合:
    q₁(σ_θ) → R₁ ... insert₂(满足 θ) ... c₂ ... q₁(σ_θ) → R₂ 且 R₁ ≠ R₂
  注意: 幻读是"谓词锁"层面的异常，非单行数据异常

定义 (写偏斜 Write Skew):
  T₁ 读取 x, T₂ 读取 y, T₁ 写 y, T₂ 写 x
  各自保持局部不变式，但破坏全局不变式:
    r₁(x), r₂(y), w₁(y), w₂(x), c₁, c₂
```

### 2.3 2PL 与 MVCC 的形式化

```text
定义 (Strict 2PL):
  锁协议:
    read(x) → 获取 read_lock(x)
    write(x) → 获取 write_lock(x) (若已有 read_lock，升级为 write_lock)
    commit/abort → 释放所有锁

  两阶段性质:
    存在点 p: p 之前只获取锁，p 之后只释放锁

  串行性: Strict 2PL 保证冲突可串行化 (Conflict Serializability)

定义 (MVCC):
  每个数据项 x 有版本链: x = [v₁, v₂, ..., vₙ]
  每个版本 vᵢ = ⟨value, txn_id, begin_ts, end_ts⟩

  读取规则 (快照读):
    txn T with start_ts 读取 x 的最新可见版本:
      v = max{vᵢ | vᵢ.begin_ts ≤ T.start_ts < vᵢ.end_ts}

  写入规则:
    写操作创建新版本: v_new = ⟨value, T.id, T.start_ts, ∞⟩
    旧版本 end_ts 更新为 T.start_ts
```

---

## 三、多维矩阵对比

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | 写偏斜 | 实现机制 | 代表数据库 |
|---------|------|----------|------|--------|---------|----------|
| **READ UNCOMMITTED** | ✗ 允许 | ✗ 允许 | ✗ 允许 | ✗ 允许 | 无锁 | 极少使用 |
| **READ COMMITTED** | ✓ 禁止 | ✗ 允许 | ✗ 允许 | ✗ 允许 | MVCC / Short锁 | Oracle, PostgreSQL, SQL Server |
| **REPEATABLE READ** | ✓ 禁止 | ✓ 禁止 | ✗ 允许 | ✗ 允许 | MVCC 快照 | MySQL InnoDB |
| **SNAPSHOT ISOLATION** | ✓ 禁止 | ✓ 禁止 | ✓ 禁止 | ✗ 允许 | MVCC + 写冲突检测 | SQL Server, Oracle, CockroachDB |
| **SERIALIZABLE** | ✓ 禁止 | ✓ 禁止 | ✓ 禁止 | ✓ 禁止 | S2PL / SSI | PostgreSQL (SSI), MySQL (S2PL) |

---

## 四、权威引用

> **Jim Gray** ("The Transaction Concept: Virtues and Limitations", VLDB 1981):
> "The transaction concept is the essential ingredient that has allowed the database industry to flourish. It provides the abstraction that allows programmers to ignore concurrency and system failures."

> **Berenson et al.** ("A Critique of ANSI SQL Isolation Levels", ACM SIGMOD 1995):
> "The ANSI SQL isolation levels are incomplete and ambiguous. We define new phenomena (write skew) and show that Snapshot Isolation prevents more anomalies than Repeatable Read but is still not serializable."

> **Michael Cahill et al.** ("Serializable Isolation for Snapshot Databases", ACM TODS 2009):
> "Serializable Snapshot Isolation (SSI) is the first implementation of full serializability that performs almost as well as snapshot isolation, the gold standard for performance."

---

## 五、工程实践与代码示例

### PostgreSQL 可串行化隔离级别

```sql
-- Session 1
BEGIN ISOLATION LEVEL SERIALIZABLE;
SELECT * FROM accounts WHERE id = 1;  -- balance = 100
-- ... 一些业务逻辑 ...
UPDATE accounts SET balance = balance - 50 WHERE id = 1;
COMMIT;
-- 若 Session 2 并发修改导致写偏斜，此 COMMIT 将失败:
-- ERROR: could not serialize access due to read/write dependencies

-- 应用层重试逻辑 (必须实现)
-- 伪代码:
-- while (true) {
--   try { execute_transaction(); break; }
--   catch (SerializationFailure) { sleep(random_backoff); continue; }
-- }
```

---

## 六、批判性总结

ACID 与隔离级别是数据库理论中最精妙也最被误解的概念之一。ANSI SQL 标准定义的四个隔离级别（RU, RC, RR, Serializable）在 1995 年被 Berenson 等人证明是**不完整且存在歧义**的——标准未定义"幻读"的精确语义，也未涵盖"写偏斜"这一重要异常。Snapshot Isolation 的引入进一步模糊了隔离级别的光谱：它在实践中阻止了大多数异常（包括幻读），却仍允许写偏斜，因此不等价于真正的串行化。PostgreSQL 的 Serializable Snapshot Isolation (SSI) 是一个工程杰作，它通过检测"串行化图"中的危险结构（rw-依赖环）在几乎不损失性能的前提下实现了真正的串行化。但 SSI 并非万能药：**在高冲突负载下，事务重试率会急剧上升**，此时性能反而不如显式锁。MVCC 虽解决了读写冲突，却引入了版本链清理（Vacuum）的开销——PostgreSQL 的 Autovacuum 和 MySQL InnoDB 的 Purge 线程都是长期存在的工程痛点。最终，隔离级别的选择不是技术问题，而是**业务正确性与性能之间的权衡决策**。


---

## 七、概念属性关系网络

### 7.1 核心概念依赖/包含/对立关系表

| 概念A | 关系类型 | 概念B | 关系说明 |
|-------|---------|-------|---------|
| ACID | ⊃ (包含) | Atomicity | ACID包含原子性子属性 |
| ACID | ⊃ (包含) | Consistency | ACID包含一致性子属性 |
| ACID | ⊃ (包含) | Isolation | ACID包含隔离性子属性 |
| ACID | ⊃ (包含) | Durability | ACID包含持久性子属性 |
| Isolation | → (层级) | Isolation Level | 隔离性通过隔离级别实现 |
| 2PL | → (实现) | Isolation | 两阶段锁是实现隔离性的机制 |
| MVCC | ⊥ (替代) | 2PL | MVCC是2PL的替代并发控制方案 |
| Dirty Read | ⊥ (消除) | READ COMMITTED | 脏读被读已提交隔离级别消除 |
| Non-Repeatable Read | ⊥ (消除) | REPEATABLE READ | 不可重复读被可重复读隔离级别消除 |
| Phantom Read | ⊥ (消除) | SERIALIZABLE | 幻读被串行化隔离级别消除 |
| Write Skew | ⊥ (消除) | SSI | 写偏斜被串行化快照隔离消除 |

### 7.2 ASCII拓扑图

```text
事务与隔离级别概念拓扑
│
├─► ACID性质
│   ├─► A (Atomicity) ──► 全做或全不做
│   │   └─► 实现: WAL + Undo/Redo
│   │
│   ├─► C (Consistency) ──► 保持数据库不变式
│   │   └─► 实现: 约束检查 + 触发器 + 外键
│   │
│   ├─► I (Isolation) ──► 并发事务互不干扰
│   │   └─► 实现: 2PL / MVCC / SSI
│   │
│   └─► D (Durability) ──► 提交后数据永久保存
│       └─► 实现: WAL持久化 + Checkpoint
│
├─► 并发控制机制
│   ├─► 2PL (Two-Phase Locking)
│   │   ├─► Growing Phase: 获取锁，不释放锁
│   │   ├─► Shrinking Phase: 释放锁，不获取锁
│   │   └─► Strict 2PL: 锁持有到事务结束
│   │
│   ├─► MVCC (Multi-Version Concurrency Control)
│   │   ├─► 写不阻塞读，读不阻塞写
│   │   ├─► 版本链: x = [v₁, v₂, ..., vₙ]
│   │   ├─► 快照读: 读取事务开始时的可见版本
│   │   └─► 垃圾回收: 移除不可见旧版本
│   │
│   └─► SSI (Serializable Snapshot Isolation)
│       ├─► 基于MVCC快照
│       ├─► 检测串行化图的危险结构 (rw-依赖环)
│       └─► 冲突时事务重试
│
└─► 隔离级别谱系 (异常阻止能力递增)
    ├─► READ UNCOMMITTED ──► 允许脏读、不可重复读、幻读、写偏斜
    ├─► READ COMMITTED ──► 阻止脏读
    ├─► REPEATABLE READ ──► 阻止脏读、不可重复读
    ├─► SNAPSHOT ISOLATION ──► 阻止脏读、不可重复读、幻读
    │                            但允许写偏斜
    └─► SERIALIZABLE ──► 阻止所有异常 (含写偏斜)
        ├─► 实现1: Strict 2PL (MySQL InnoDB)
        └─► 实现2: SSI (PostgreSQL)
```

### 7.3 形式化映射

```text
概念映射:

f₁: Transaction → ACID      via  concurrency_manager + recovery_manager
f₂: Operation → Lock          via  lock_manager.acquire(lock_type, resource)
f₃: Transaction → Snapshot    via  mvcc.start_timestamp → visible_versions
f₄: IsolationLevel → Anomalies  via  allowed_anomalies(level)
                              RU: {dirty_read, non_repeatable, phantom, write_skew}
                              RC: {non_repeatable, phantom, write_skew}
                              RR: {phantom, write_skew}
                              SI: {write_skew}
                              Serializable: {}
f₅: Write → Version           via  mvcc.create_version(data, txn_id, start_ts, ∞)
f₆: Version → Visibility      via  start_ts ∈ [begin_ts, end_ts) ? visible : invisible
f₇: Conflict → Retry          via  ssi.detect_rw_cycle() → abort(txn) + retry
```

---

## 八、形式化推理链

### 8.1 公理体系

**公理 1 (原子性公理)** — Jim Gray, 1981
> 事务执行结果仅两种可能：全部操作生效或全部不生效。
> result(T) ∈ {apply_all(T), state₀}

**公理 2 (隔离性公理)** — Berenson et al., 1995
> 并发执行等价于某个串行执行顺序。
> serializable(H) ⟺ ∃H_serial: H ≡ H_serial

**公理 3 (持久性公理)**
> 事务提交后，其修改永久保存，即使系统崩溃。
> commit(T) ⟹ ∀subsequent_reads: read(x) returns T's write

### 8.2 引理

**引理 1 (2PL的冲突可串行化)**
> Strict 2PL保证冲突可串行化（Conflict Serializability）。
> Proof: 2PL的锁点（lock point）定义了事务的等效串行顺序。

**引理 2 (MVCC的读写不阻塞)**
> MVCC下，读操作不获取写锁，写操作不阻塞读操作。
> Proof: 读操作读取历史版本，无需等待当前写事务提交。

### 8.3 定理

**定理 1 (ANSI隔离级别的异常包含关系)** — Berenson et al., 1995
> 隔离级别从低到高依次消除更多异常：
> RU ⊃ RC ⊃ RR ⊃ SI ⊃ Serializable
>
> 形式化: allowed_anomalies(RU) ⊃ allowed_anomalies(RC) ⊃ ... ⊃ allowed_anomalies(Serializable) = ∅

**定理 2 (SSI的性能-正确性权衡)** — Cahill et al., 2009
> Serializable Snapshot Isolation (SSI) 在几乎不损失性能的前提下实现真正的串行化。
>
> 核心洞察: 串行化图的危险结构是rw-依赖环；SSI检测这种结构并中止构成环的事务之一。
> 冲突率低时，SSI ≈ SI性能；冲突率高时，重试率上升。

### 8.4 推论

**推论 1 (幻读的谓词锁本质)**
> 幻读是"谓词锁"层面的异常，非单行数据异常。
> 传统行锁无法阻止幻读，需要间隙锁（Gap Lock）或谓词锁（Predicate Lock）。

**推论 2 (MVCC的版本清理开销)**
> MVCC虽解决了读写冲突，但引入了版本链清理（Vacuum/Purge）的持续性开销。
> 长事务阻塞旧版本清理，导致存储膨胀和查询性能退化。

---

## 九、ASCII推理判定树 / 决策树

### 9.1 隔离级别选择决策树

```text
隔离级别选择
│
├─► 是否可以容忍读取未提交数据？
│   ├─ 是（极少场景）──► READ UNCOMMITTED
│   │                       └─ 最高并发，最低一致性
│   │
│   └─ 否 ──► 同一事务内是否需要重复读取相同结果？
│               ├─ 否（单次读取业务）──► READ COMMITTED
│               │                       └─ Oracle/PostgreSQL默认
│               │                       └─ 允许幻读和写偏斜
│               │
│               └─ 是 ──► 是否需要防止幻读？
│                           ├─ 否 ──► REPEATABLE READ (MySQL默认)
│                           │           └─ 阻止不可重复读，允许幻读
│                           │
│                           └─ 是 ──► 是否需要防止写偏斜？
│                                       ├─ 否 ──► SNAPSHOT ISOLATION
│                                       │           └─ SQL Server/Oracle默认
│                                       │           └─ 阻止幻读，允许写偏斜
│                                       │
│                                       └─ 是（最强一致性）──► SERIALIZABLE
│                                                           └─ PostgreSQL SSI
│                                                           └─ MySQL S2PL
│                                                           └─ 性能最低，一致性最高
```

### 9.2 并发控制机制选择决策树

```text
并发控制机制选择
│
├─► 读写比例如何？
│   ├─ 读 >> 写（如报表系统）──► MVCC
│   │                           └─ 读不阻塞写，写不阻塞读
│   │                           └─ PostgreSQL / Oracle默认
│   │
│   ├─ 写 >> 读（如高频交易）──► Strict 2PL
│   │                           └─ 悲观锁，避免冲突重试
│   │                           └─ MySQL InnoDB (RR隔离级)
│   │
│   └─ 读写均衡 ──► 冲突频率如何？
│               ├─ 低冲突 ──► MVCC + SSI
│               │               └─ 乐观并发，冲突时重试
│               │               └─ PostgreSQL Serializable
│               │
│               └─ 高冲突 ──► Strict 2PL 或显式应用层锁
│                               └─ 避免大量事务重试开销
```

---

## 十、国际权威课程对齐

### 10.1 MIT 6.830: Database Systems

| 课程内容 | 对应 Lecture | 对应本文件内容 | 映射深度 |
|---------|-------------|---------------|---------|
| Transactions & Concurrency | Lec 7-9 | ACID、2PL、MVCC、隔离级别 | 核心映射 |
| Recovery | Lec 10-11 | ARIES、WAL、Checkpoint | 核心映射 |

### 10.2 Stanford CS 145 / CS 245: Database Systems

| 课程内容 | 对应模块 | 对应本文件内容 |
|---------|---------|---------------|
| Transaction Management | Lecture 11-14 | ACID语义与隔离级别 |
| Concurrency Control | Lecture 12-13 | 2PL与MVCC的实现机制 |
| Advanced Topics | Lecture 14-15 | Snapshot Isolation与SSI |

### 10.3 CMU 15-445: Database Systems

| 课程内容 | 对应 Lecture | 对应本文件内容 |
|---------|-------------|---------------|
| Concurrency Control Theory | Lecture 17 | 冲突可串行化理论 |
| Two-Phase Locking | Lecture 18 | 2PL协议与实现 |
| Timestamp Ordering | Lecture 19 | 时间戳排序并发控制 |
| Multi-Version Concurrency Control | Lecture 20 | MVCC版本链与可见性规则 |
| Database Logging | Lecture 21 | WAL与ARIES日志结构 |
| Database Recovery | Lecture 22 | Analysis-Redo-Undo三阶段恢复 |

### 10.4 Berkeley CS 186: Database Systems

| 课程内容 | 对应模块 | 对应本文件内容 |
|---------|---------|---------------|
| Transactions & Concurrency | Lecture 14-16 | ACID与隔离级别 |
| Advanced Concurrency Control | Lecture 22 | MVCC与2PL的对比 |
| Crash Recovery | Lecture 23-25 | ARIES恢复算法 |

### 10.5 核心参考文献

1. **Jim Gray** (1981). "The Transaction Concept: Virtues and Limitations." *VLDB 1981*. —— 事务概念的经典论文，奠定了ACID在数据库系统中的核心地位，明确指出事务是数据库行业繁荣的关键要素。

2. **Hal Berenson et al.** (1995). "A Critique of ANSI SQL Isolation Levels." *ACM SIGMOD 1995*. —— 系统批判了ANSI SQL隔离级别的不完整性和歧义性，定义了写偏斜等新异常，引入了Snapshot Isolation概念。

3. **Michael Cahill et al.** (2009). "Serializable Isolation for Snapshot Databases." *ACM TODS*, 34(4), 1-42. —— Serializable Snapshot Isolation (SSI)的原始论文，首次在几乎不损失性能的前提下实现了真正的串行化。

4. **C. Mohan et al.** (1992). "ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging." *ACM TODS*, 17(1), 94-162. —— ARIES恢复算法的奠基论文，定义了现代数据库存储引擎恢复的标准方法。

---

## 十一、批判性总结

ACID与隔离级别是数据库理论中最精妙也最被误解的概念之一。ANSI SQL标准定义的四个隔离级别（Read Uncommitted, Read Committed, Repeatable Read, Serializable）在1995年被Berenson等人证明是不完整且存在歧义的——标准未定义"幻读"的精确语义，也未涵盖"写偏斜"这一重要异常。这一理论缺陷的直接后果是不同数据库厂商对同一隔离级别的实现存在显著差异：MySQL的Repeatable Read通过Next-Key Locking阻止了幻读，而标准SQL的Repeatable Read允许幻读；Oracle的Read Committed实际上实现了Snapshot Isolation的语义。Snapshot Isolation的引入进一步模糊了隔离级别的光谱：它在实践中阻止了大多数异常（包括幻读），却仍允许写偏斜，因此不等价于真正的串行化。PostgreSQL的Serializable Snapshot Isolation (SSI)是一个工程杰作，它通过检测"串行化图"中的危险结构（rw-依赖环）在几乎不损失性能的前提下实现了真正的串行化，但SSI并非万能药——在高冲突负载下，事务重试率会急剧上升，此时性能反而不如显式锁。MVCC虽解决了读写冲突，却引入了版本链清理（Vacuum/Purge）的开销——PostgreSQL的Autovacuum和MySQL InnoDB的Purge线程都是长期存在的工程痛点，长事务阻塞旧版本清理导致的存储膨胀是生产环境中的经典故障模式。最终，隔离级别的选择不是纯粹的技术问题，而是业务正确性与性能之间的权衡决策——金融核心系统可能选择Serializable的强保证，而社交网站的点赞计数则可能完全接受Read Committed的最终一致性。架构师必须清醒认识到：不存在"完美的隔离级别"，只有对业务容忍度的精确匹配。
