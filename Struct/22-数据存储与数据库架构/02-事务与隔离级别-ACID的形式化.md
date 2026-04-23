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
