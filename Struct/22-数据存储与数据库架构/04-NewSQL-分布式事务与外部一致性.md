# NewSQL：分布式事务与外部一致性

> **来源映射**: View/02.md §2.3, Struct/22-数据存储与数据库架构/00-总览-数据库系统的形式化分层.md
> **国际权威参考**: "Spanner: Google's Globally-Distributed Database" (Corbett et al., OSDI 2012); "CockroachDB: The Resilient Geo-Distributed SQL Database" (Taft et al., SIGMOD 2020); "Large-scale Incremental Processing Using Distributed Transactions and Notifications" (Peng & Dabek, OSDI 2010, Percolator)

---

## 一、知识体系思维导图

```text
NewSQL 分布式数据库
│
├─► 核心目标
│   └─ 在分布式架构上恢复 ACID + SQL，兼得 NoSQL 的扩展性
│
├─► Google Spanner
│   ├─ TrueTime API: 原子钟 + GPS 时钟同步
│   │   ├─ TTinterval: [earliest, latest] 时间区间
│   │   └─ 时钟不确定度 ε ≈ 7ms (全球)
│   ├─ 外部一致性 (External Consistency)
│   │   └─ 若 T₁ 提交在 T₂ 开始之前，则 T₁ 的时间戳 < T₂ 的时间戳
│   ├─ 两阶段锁 + 2PC + Paxos 复制组
│   └─ 全局读写事务: 时间戳分配 + 等待直至 ε 过去
│
├─► CockroachDB
│   ├─ 架构: 全局排序的分布式 KV 层 (RocksDB + Raft)
│   ├─ 混合逻辑时钟 (HLC): 结合物理时钟与 Lamport 逻辑时钟
│   ├─ 串行化默认: Serializable Snapshot Isolation (SSI)
│   ├─ 租约持有者 (Leaseholder): 数据位置的本地时钟权威
│   └─ 跟随者读取 (Follower Reads): 利用时钟偏移读取本地副本
│
└─► Percolator (TiDB 基础)
    ├─ 基于 Bigtable 的分布式事务协议
    ├─ 三列设计: lock, write, data
    ├─ 两阶段提交 (2PC) 变体
    │   ├─ Prewrite: 写入主锁 + 数据，检查冲突
    │   └─ Commit: 释放锁，写入提交记录
    └─ 单点时间戳分配器 (TSO)
```

---

## 二、核心概念的形式化定义

### 2.1 TrueTime 与外部一致性的形式化

```text
定义 (TrueTime API):
  TT.now(): 返回时间区间 [t_earliest, t_latest]
  保证:  wall_clock ∈ [t_earliest, t_latest]

  时钟不确定度: ε = t_latest - t_earliest ≈ 1-7ms

  等待函数:
    TT.after(t): 阻塞直到 t_latest > t (本地时钟确信越过 t)

定义 (外部一致性):
  对于事务 T₁, T₂:
    若 commit(T₁) 在 start(T₂) 之前发生 (因果序)
    则: commit_ts(T₁) < commit_ts(T₂)

  Spanner 实现:
    commit_ts = TT.now().latest  at commit time
    确保: ∀T₁ before T₂: commit_ts(T₁) < commit_ts(T₂)

  读写事务等待:
    在提交后，等待 TT.after(commit_ts) 才响应客户端
    保证后续事务的 start_ts > 当前事务的 commit_ts
```

### 2.2 CockroachDB HLC 的形式化

```text
定义 (混合逻辑时钟 HLC):
  HLC = ⟨pt, lc⟩ where pt = 物理时间, lc = 逻辑计数器

  发送/本地事件:
    send: HLC' = ⟨max(pt, pt_received), lc+1⟩ if pt == pt_received else ⟨pt, 0⟩

  性质:
    - 捕获因果关系: if e₁ → e₂ then HLC(e₁) < HLC(e₂)
    - 接近物理时间: |HLC.pt - wall_clock| 有界
    - 无需专用时钟硬件 (对比 Spanner TrueTime)
```

### 2.3 Percolator 事务协议

```text
定义 (Percolator 2PC):
  数据存储在 Bigtable 中，每行有三列:
    data: 实际数据值
    lock: 事务锁信息 (指向主锁位置)
    write: 提交时间戳 → 数据时间戳的映射

  Prewrite (第一阶段):
    选择 Primary Row，写入 lock 列 (带 primary 指针)
    写入所有行的 data 列 (时间戳 = start_ts)
    冲突检查: 若存在 lock 或 write[start_ts, ∞) → abort

  Commit (第二阶段):
    清除 Primary Row 的 lock，写入 write 列 (commit_ts)
    异步清除 Secondary Rows 的 lock

  读操作:
    从最新时间戳开始扫描，跳过锁，找到已提交的数据
```

---

## 三、多维矩阵对比

| 维度 | Spanner | CockroachDB | TiDB | YugabyteDB |
|------|---------|-------------|------|-----------|
| **共识算法** | Paxos | Multi-Raft | Multi-Raft | Raft |
| **时钟机制** | TrueTime (原子钟+GPS) | HLC | TSO (中心授时) | HLC |
| **默认隔离级** | 外部一致 (可串行化) | Serializable (SSI) | SI / RC | SI |
| **跨地域一致** | **强** (全球外部一致) | 因果一致 | 区域强一致 | 可调 |
| **SQL 兼容** | 部分 (无 auto-inc) | 高 (PostgreSQL) | 高 (MySQL) | 中 |
| **硬件依赖** | 原子钟/GPS (高) | 无 | 无 | 无 |
| **开源** | 否 | **是** (Apache 2.0) | **是** | **是** |
| **代表场景** | 全球金融 (Google) | 全球分布式 OLTP | 混合负载 HTAP | 云原生应用 |

---

## 四、权威引用

> **James Corbett et al.** (Google, "Spanner: Google's Globally-Distributed Database", OSDI 2012):
> "Spanner is the first system to distribute data at global scale and support externally-consistent distributed transactions. TrueTime is the key enabler—external consistency is just strong consistency at global scale."

> **Irfan Sharif et al.** (Cockroach Labs, "CockroachDB: The Resilient Geo-Distributed SQL Database", SIGMOD 2020):
> "CockroachDB provides serializable default isolation using Serializable Snapshot Isolation (SSI). It does not require specialized hardware for clock synchronization."

> **Daniel Peng & Frank Dabek** (Google, "Large-scale Incremental Processing Using Distributed Transactions and Notifications", OSDI 2010):
> "Percolator provides cross-row, cross-table transactions with ACID snapshots over Bigtable. It processes the same volume of data as MapReduce but with latency reduced from hours to seconds."

---

## 五、工程实践与代码示例

### CockroachDB: 地理分区与跟随者读取

```sql
-- 创建按地理分区表
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    region STRING,
    amount DECIMAL
) PARTITION BY LIST (region) (
    PARTITION us_west VALUES IN ('us-west'),
    PARTITION us_east VALUES IN ('us-east'),
    PARTITION eu VALUES IN ('eu')
);

-- 放置约束：将分区绑定到特定区域的节点
ALTER PARTITION us_west OF TABLE orders
    CONFIGURE ZONE USING constraints = '[+region=us-west]';

-- 跟随者读取 (利用时钟偏移读取本地副本)
SET SESSION CHARACTERISTICS AS TRANSACTION AS OF SYSTEM TIME '-10s';
SELECT * FROM orders WHERE region = 'us-west';
-- 牺牲 10 秒新鲜度，换取本地读取延迟 (无需跨地域 RTT)
```

---

## 六、批判性总结

NewSQL 是数据库领域"回归 ACID"的技术运动，其核心命题是：分布式架构不必以牺牲事务语义为代价。Spanner 用 TrueTime 证明了**时钟同步硬件可以"购买"一致性**——这是 CAP 定理语境下的一个关键修正：当分区容错(P)和时钟同步同时满足时，强一致性(C)与可用性(A)的权衡可以被重新定义。然而，这种"购买"是有价格的：原子钟和 GPS 接收器的部署成本使 Spanner 长期成为 Google 的专属特权。CockroachDB 和 TiDB 的创新在于证明了**无需专用硬件也能接近 Spanner 的语义**——HLC 和 TSO 以软件方式实现了可接受的全局一致性，尽管在跨地域延迟和时钟偏移边界上做出了妥协。Percolator 协议是 Google 的又一次工程杰作，但它暴露了基于 Bigtable 的事务系统的固有缺陷：**单点 TSO 是瓶颈，锁清理是异步的且可能遗留孤儿锁**。NewSQL 的真正挑战不在于技术可行性，而在于**工程复杂度和运维成本**——分布式事务的调试比单机事务困难一个数量级，网络延迟抖动、时钟漂移、Raft 选主风暴等问题在生产环境中层出不穷。NewSQL 不是银弹，而是为需要全球分布式 ACID 的特定场景准备的精密仪器。


---

## 七、概念属性关系网络

### 7.1 核心概念依赖/包含/对立关系表

| 概念A | 关系类型 | 概念B | 关系说明 |
|-------|---------|-------|---------|
| NewSQL | → (目标) | Distributed ACID | NewSQL目标是在分布式架构上恢复ACID |
| Spanner | ⊃ (包含) | TrueTime | Spanner包含TrueTime时钟同步机制 |
| TrueTime | → (依赖) | Atomic Clock | TrueTime依赖原子钟/GPS硬件 |
| External Consistency | → (依赖) | TrueTime | 外部一致性依赖TrueTime的时间区间 |
| CockroachDB | ⊃ (包含) | HLC | CockroachDB包含混合逻辑时钟 |
| HLC | → (依赖) | Physical Clock | HLC依赖物理时钟与逻辑计数器组合 |
| SSI | → (实现) | Serializable | 串行化快照隔离实现可串行化 |
| Percolator | ⊃ (包含) | 2PC | Percolator包含两阶段提交变体 |
| TSO | → (依赖) | Timestamp Oracle | Percolator依赖中心时间戳分配器 |
| Paxos | ⊥ (替代) | Raft | Spanner用Paxos，CockroachDB/TiDB用Raft |

### 7.2 ASCII拓扑图

```text
NewSQL分布式数据库概念拓扑
│
├─► Google Spanner
│   ├─► TrueTime API
│   │   ├─► TT.now() → [t_earliest, t_latest]
│   │   ├─► 时钟不确定度 ε ≈ 1-7ms (全球)
│   │   ├─► 原子钟 + GPS 时钟同步
│   │   └─► TT.after(t): 阻塞直到本地时钟确信越过t
│   │
│   ├─► 外部一致性 (External Consistency)
│   │   ├─► 若 T₁提交在 T₂开始之前 ⟹ commit_ts(T₁) < commit_ts(T₂)
│   │   ├─► commit_ts = TT.now().latest at commit time
│   │   └─► 提交后等待 TT.after(commit_ts) 才响应客户端
│   │
│   ├─► 两阶段锁 + 2PC + Paxos复制组
│   │   ├─► 读写事务: 时间戳分配 + 等待直至ε过去
│   │   └─► 只读事务: 时间戳选择 + 快照读
│   │
│   └─► 硬件依赖
│       └─► 原子钟/GPS接收器 → 高部署成本
│
├─► CockroachDB
│   ├─► 架构: 全局排序的分布式KV层 (RocksDB + Raft)
│   ├─► 混合逻辑时钟 (HLC)
│   │   ├─► HLC = ⟨pt, lc⟩ (物理时间, 逻辑计数器)
│   │   ├─► 捕获因果关系: e₁ → e₂ ⟹ HLC(e₁) < HLC(e₂)
│   │   └─► 无需专用时钟硬件
│   ├─► 串行化默认: Serializable Snapshot Isolation (SSI)
│   ├─► 租约持有者 (Leaseholder): 数据位置的本地时钟权威
│   └─► 跟随者读取 (Follower Reads): 利用时钟偏移读取本地副本
│
└─► Percolator (TiDB基础)
    ├─► 基于Bigtable的分布式事务协议
    ├─► 三列设计: lock, write, data
    ├─► 两阶段提交变体
    │   ├─► Prewrite: 写入主锁 + 数据，检查冲突
    │   └─► Commit: 释放锁，写入提交记录
    └─► 单点时间戳分配器 (TSO)
        └─► 潜在单点瓶颈
```

### 7.3 形式化映射

```text
概念映射:

f₁: TrueTime → TimestampInterval   via  TT.now() → [t_earliest, t_latest]
f₂: TimestampInterval → ExternalConsistency
                                    via  wait(TT.after(commit_ts)) ⟹ subsequent_start_ts > commit_ts
f₃: HLC → CausalityTracking        via  send/recv事件更新HLC，捕获happens-before关系
f₄: Transaction → Serializable     via  ssi.detect_rw_cycle() → abort_or_commit
f₅: Key → Leaseholder              via  range_partitioning(key) → node_leaseholder
f₆: PercolatorTransaction → 2PC    via  prewrite(primary, secondaries) → commit(primary)
f₇: TSO → GlobalTimestamp          via  centralized_timestamp_oracle.allocate()
f₈: Raft → Consensus               via  raft_log.replicate(command) → majority_ack → commit
```

---

## 八、形式化推理链

### 8.1 公理体系

**公理 1 (TrueTime区间包含公理)** — Corbett et al., 2012
> TrueTime返回的时间区间保证包含绝对时间。
> ∀call: wall_clock ∈ [t_earliest, t_latest]

**公理 2 (外部一致性因果公理)**
> 若事务T₁的提交在T₂的开始之前（因果序），则T₁的时间戳小于T₂的时间戳。
> commit(T₁) before start(T₂) ⟹ commit_ts(T₁) < commit_ts(T₂)

**公理 3 (HLC因果捕获公理)** — Kulkarni et al., 2014
> 混合逻辑时钟捕获分布式系统中的happens-before关系。
> e₁ → e₂ ⟹ HLC(e₁) < HLC(e₂)

### 8.2 引理

**引理 1 (Spanner读写事务的等待下界)**
> 写事务提交后需等待至少ε（时钟不确定度）才响应客户端。
> wait_time ≥ ε = t_latest - t_earliest
> Proof: 需保证 commit_ts < 所有后续事务的start_ts。由于时钟不确定度为ε，需等待本地时钟确信越过commit_ts。

**引理 2 (CockroachDB跟随者读取的新鲜度上界)**
> 跟随者读取的数据版本滞后于Leader的时间上界为时钟偏移阈值。
> staleness ≤ max_clock_offset

### 8.3 定理

**定理 1 (Spanner外部一致性的实现)** — Corbett et al., 2012
> Spanner通过TrueTime实现了外部一致的分布式事务。
>
> 构造:
> (1) commit_ts = TT.now().latest at commit time
> (2) 提交后等待 TT.after(commit_ts)
> (3) 后续事务的start_ts = TT.now().earliest > commit_ts
> (4) 故: commit_ts(T₁) < start_ts(T₂) ⟹ T₁在T₂之前全局可见

**定理 2 (无专用硬件的近似外部一致性)** — CockroachDB设计
> CockroachDB通过HLC和SSI实现了无需原子钟的近似外部一致性。
>
> 权衡:
> (1) HLC不保证全局时钟同步，仅捕获因果序
> (2) 跨地域事务的串行化依赖SSI的冲突检测
> (3) 时钟漂移边界 > ε_Spanner，故一致性保证弱于Spanner
> (4) 但: 无专用硬件依赖，部署成本显著降低

### 8.4 推论

**推论 1 (Spanner的时钟硬件成本)**
> TrueTime的原子钟和GPS接收器部署成本使Spanner长期成为Google专属特权。
> 时钟硬件是Spanner外部一致性的必要非充分条件。

**推论 2 (Percolator TSO的单点瓶颈)**
> Percolator的单点TSO在高并发事务场景下成为吞吐量限制。
> TiDB通过TSO集群化（PD集群）缓解，但引入了额外的协调延迟。

---

## 九、ASCII推理判定树 / 决策树

### 9.1 NewSQL数据库选型决策树

```text
NewSQL数据库选型
│
├─► 是否需要全球分布式强一致？
│   ├─ 是（全球金融、跨大陆事务）──► Google Spanner (云托管)
│   │                                   └─ TrueTime外部一致，原子钟依赖
│   │                                   └─ 高成本，最高一致性保证
│   │
│   └─ 否（区域/大陆内分布）──► 是否需要PostgreSQL兼容？
│               ├─ 是 ──► CockroachDB
│               │           └─ SSI默认串行化，跟随者读取
│               │           └─ 开源，Apache 2.0
│               │
│               └─ 否（MySQL兼容）──► TiDB
│                                   └─ Percolator分布式事务
│                                   └─ HTAP混合负载支持
│                                   └─ 活跃中文社区
```

### 9.2 分布式事务一致性级别选择决策树

```text
分布式事务一致性选择
│
├─► 是否可接受最终一致（非金融场景）？
│   ├─ 是 ──► 使用Saga / 异步补偿
│   │           └─ 最终一致，高可用，无全局锁
│   │
│   └─ 否（需要强一致）──► 是否需要全局外部一致（TrueTime级别）？
│               ├─ 是 ──► Spanner + 2PC + TrueTime等待
│               │           └─ 最高一致性，最高延迟（+ε等待）
│               │
│               └─ 否（因果一致足够）──► CockroachDB SSI / TiDB SI
│                                   └─ 串行化快照隔离
│                                   └─ 冲突检测 + 事务重试
│                                   └─ 无专用时钟硬件需求
```

---

## 十、国际权威课程对齐

### 10.1 MIT 6.824: Distributed Systems

| 课程内容 | 对应 Lecture | 对应本文件内容 | 映射深度 |
|---------|-------------|---------------|---------|
| Spanner | LEC 12/13: Spanner | TrueTime、外部一致性、全球事务 | 核心映射 |
| Distributed Transactions | LEC 11: Distributed Transactions | 2PC与Percolator协议 | 直接映射 |
| Optimistic Concurrency | LEC 14: FaRM | 乐观并发与SSI | 对比映射 |

**对应 Lab:**

- Lab 4: Sharded KV — 理解跨分片事务的原子性挑战

### 10.2 Stanford CS 245: Database System Principles

| 课程内容 | 对应模块 | 对应本文件内容 |
|---------|---------|---------------|
| Distributed Databases | Lecture 9-10 | 分布式事务与一致性协议 |
| Clock Synchronization | Lecture 11-12 | TrueTime与HLC的时钟机制 |
| Consensus | Lecture 13-14 | Paxos/Raft在NewSQL中的应用 |

### 10.3 CMU 15-445: Database Systems

| 课程内容 | 对应 Lecture | 对应本文件内容 |
|---------|-------------|---------------|
| Distributed Database Systems | Lecture 23-24 | NewSQL架构与分布式事务 |
| Timestamp Ordering | Lecture 19 | 时间戳排序与并发控制 |

### 10.4 Berkeley CS 186: Database Systems

| 课程内容 | 对应模块 | 对应本文件内容 |
|---------|---------|---------------|
| Distributed Transactions | Lecture 20-21 | 2PC与分布式一致性 |
| Paxos Consensus | Lecture 21 | 共识算法在数据库中的应用 |

### 10.5 核心参考文献

1. **James Corbett et al.** (2012). "Spanner: Google's Globally-Distributed Database." *OSDI 2012*. —— Spanner的原始论文，首次证明了全球分布式数据库可实现外部一致性，TrueTime是其关键使能技术。

2. **Irfan Sharif et al.** (2020). "CockroachDB: The Resilient Geo-Distributed SQL Database." *SIGMOD 2020*. —— CockroachDB的系统论文，阐述了无需专用硬件的SSI实现和地理分区策略。

3. **Daniel Peng & Frank Dabek** (2010). "Large-scale Incremental Processing Using Distributed Transactions and Notifications." *OSDI 2010*. —— Percolator的原始论文，定义了基于Bigtable的分布式事务协议。

4. **Sandeep Kulkarni et al.** (2014). "Logical Physical Clocks and Consistent Snapshots in Distributed Systems." *OPODIS 2014*. —— 混合逻辑时钟（HLC）的原始论文，提出了无需专用硬件的因果时钟方案。

---

## 十一、批判性总结

NewSQL是数据库领域"回归ACID"的技术运动，其核心命题是：分布式架构不必以牺牲事务语义为代价。Spanner用TrueTime证明了时钟同步硬件可以"购买"一致性——这是CAP定理语境下的一个关键修正：当分区容错(P)和时钟同步同时满足时，强一致性(C)与可用性(A)的权衡可以被重新定义。然而，这种"购买"是有价格的：原子钟和GPS接收器的部署成本使Spanner长期成为Google的专属特权，直到Cloud Spanner的发布才使这一技术民主化。CockroachDB和TiDB的创新在于证明了无需专用硬件也能接近Spanner的语义——HLC和TSO以软件方式实现了可接受的全局一致性，尽管在跨地域延迟和时钟偏移边界上做出了妥协。Percolator协议是Google的又一次工程杰作，但它暴露了基于Bigtable的事务系统的固有缺陷：单点TSO是明显的吞吐量瓶颈，锁清理是异步的且可能遗留孤儿锁，Prewrite阶段的冲突检测在高并发写入场景下导致大量事务中止。NewSQL的真正挑战不在于技术可行性，而在于工程复杂度和运维成本——分布式事务的调试比单机事务困难一个数量级，网络延迟抖动、时钟漂移、Raft选主风暴等问题在生产环境中层出不穷。NewSQL不是银弹，而是为需要全球分布式ACID的特定场景（金融核心、全球库存管理、跨境支付）准备的精密仪器。对于大多数应用场景，传统RDBMS的主从复制或分片架构配合适当的应用层补偿，可能是更具成本效益的选择。
