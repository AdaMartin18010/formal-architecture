# NoSQL 数据模型：KV、文档、列族与图

> **来源映射**: View/02.md §2.2, Struct/22-数据存储与数据库架构/00-总览-数据库系统的形式化分层.md
> **国际权威参考**: "Towards Robust Distributed Systems" (Eric Brewer, PODC 2000, CAP Theorem); "Amazon Dynamo: Amazon's Highly Available Key-Value Store" (DeCandia et al., SOSP 2007); "Bigtable: A Distributed Storage System for Structured Data" (Chang et al., OSDI 2006)

---

## 一、知识体系思维导图

```text
NoSQL 数据模型谱系
│
├─► CAP 定理与 BASE
│   ├─ CAP: 一致性(C) / 可用性(A) / 分区容错(P) —— 三者取其二
│   ├─ BASE: 基本可用(BA) / 软状态(S) / 最终一致(E)
│   └─ PACELC: 若分区(P)，选 A 或 C; 否则(L) 选延迟或 C
│
├─► 键值存储 (Key-Value)
│   ├─ 模型: Map⟨Key, Value⟩，Value 为不透明二进制
│   ├─ 操作: GET, PUT, DELETE
│   ├─ 扩展: 支持数据结构 (Redis: list, set, hash, zset)
│   └─ 代表: Redis, DynamoDB, Riak, etcd, RocksDB
│
├─► 文档数据库 (Document)
│   ├─ 模型: 自描述的 JSON/BSON/XML 文档
│   ├─ 查询: 嵌套字段索引、聚合管道、全文搜索
│   ├─ 模式灵活: 同一集合可有不同结构文档
│   └─ 代表: MongoDB, Couchbase, Firestore, DynamoDB (支持文档)
│
├─► 列族存储 (Wide-Column / Column Family)
│   ├─ 模型: 稀疏矩阵，按列族物理存储
│   ├─ 主键: RowKey + ColumnKey + Timestamp → Value
│   ├─ 优势: 高写入吞吐、水平扩展、时序数据友好
│   └─ 代表: Cassandra, HBase, Bigtable, ScyllaDB
│
└─► 图数据库 (Graph)
    ├─ 模型: 节点(Node) + 边(Edge) + 属性(Property)
    ├─ 查询: 图遍历 (Traversal)、模式匹配 (Cypher/Gremlin)
    ├─ 优势: 深度关系查询、推荐系统、知识图谱
    └─ 代表: Neo4j, TigerGraph, Amazon Neptune, Dgraph
```

---

## 二、核心概念的形式化定义

### 2.1 CAP 定理的形式化

```text
定理 (CAP - Brewer, 2000):
  分布式数据存储系统最多同时满足以下两项:

  Consistency (C):
    ∀read 操作，返回最近 write 的结果或错误
    形式化: 线性一致性 (Linearizability)

  Availability (A):
    每个非故障节点收到的请求必须在有限时间内响应
    形式化: ∀request: non-faulty_node → response ∈ Time_limit

  Partition Tolerance (P):
    网络分区发生时系统仍继续运行

  不可能三角:
    CA: 传统单机 RDBMS (无分区容错)
    CP: MongoDB, HBase, Redis Cluster (牺牲可用性)
    AP: Cassandra, DynamoDB, Couchbase (牺牲强一致性)
```

### 2.2 BASE 的形式化

```text
定义 (BASE 语义):
  Basically Available:
    系统基本可用，允许部分失败或降级 (如只读模式)

  Soft State:
    状态无需时刻一致，可以存在中间/临时状态
    形式化: state(t) 不保证是 "正确" 状态，但 lim(t→∞) state(t) = consistent

  Eventual Consistency:
    若无新更新，最终所有副本收敛到相同值
    形式化: ∀replicas rᵢ, rⱼ:
      if writes_stop_at(t) then ∃δ: ∀t' > t+δ: rᵢ(t') = rⱼ(t')
```

### 2.3 四种 NoSQL 模型的形式化

```text
键值 (KV):
  Store = Key → Value (opaque)
  查询能力: Q(k) = Store[k]  (仅支持 Key 精确匹配)

文档 (Document):
  Store = Collection of Documents
  Document = JSON-like nested structure
  查询能力: Q(θ) = {d | d satisfies predicate θ}
  θ 可包含嵌套路径: d.user.address.city = "Beijing"

列族 (Column Family):
  Store = {RowKey → {ColumnFamily → {Column → {Timestamp → Value}}}}
  物理存储按 ColumnFamily 聚簇
  优势: 稀疏矩阵的高效存储，列动态扩展

图 (Graph):
  G = (V, E, L, P)
  V: 节点集, E ⊆ V × V × Label: 边集
  L: 标签集, P: 属性函数 (V ∪ E → {key:value})
  查询: 图遍历 Q(G, start, pattern) → subgraph
```

---

## 三、多维矩阵对比

| 维度 | KV (Redis) | 文档 (MongoDB) | 列族 (Cassandra) | 图 (Neo4j) |
|------|-----------|---------------|-----------------|-----------|
| **数据模型** | 键值对 | JSON 文档 | 宽行/列族 | 节点+边+属性 |
| **Schema** | 无 | 灵活 | 灵活 (每行可不同列) | 灵活 |
| **查询能力** | Key 点查 | 丰富 (聚合/文本) | 有限 (CQL) | **图遍历** |
| **一致性** | 最终/可调 | 可调 (副本集) | 可调 (QUORUM) | ACID |
| **扩展性** | 水平 (Cluster) | 水平 (Sharding) | **水平线性** | 垂直为主 |
| **写入吞吐** | 极高 (内存) | 高 | **极高** | 中 |
| **关系查询** | 无 | 有限 ($lookup) | 反规范化 | **原生支持** |
| **适用场景** | 缓存/会话 | 内容/目录 | 时序/日志/IoT | 推荐/知识图谱 |

---

## 四、权威引用

> **Eric Brewer** ("Towards Robust Distributed Systems", PODC 2000):
> "Of the three properties of shared-data systems—Consistency, Availability, and Partition Tolerance—only two can be achieved at any given moment."

> **Giuseppe DeCandia et al.** (Amazon, "Dynamo: Amazon's Highly Available Key-Value Store", SOSP 2007):
> "Dynamo targets applications that operate with weaker consistency if this results in high availability. Dynamo does not provide any isolation guarantees and permits only single key updates."

> **Fay Chang et al.** (Google, "Bigtable: A Distributed Storage System for Structured Data", OSDI 2006):
> "Bigtable is a sparse, distributed, persistent multidimensional sorted map. The map is indexed by a row key, column key, and a timestamp."

---

## 五、工程实践与代码示例

### Cassandra CQL: 可调一致性

```sql
-- 写入时使用 QUORUM 一致性 (大多数副本确认)
CONSISTENCY QUORUM;
INSERT INTO users (id, name, email)
VALUES (uuid(), 'Alice', 'alice@example.com');

-- 读取时也使用 QUORUM，保证读写交集
CONSISTENCY QUORUM;
SELECT * FROM users WHERE name = 'Alice';

-- 轻量级事务 (LWT) - Compare-and-Set
INSERT INTO users (id, name, email)
VALUES (uuid(), 'Bob', 'bob@example.com')
IF NOT EXISTS;  -- 线性一致性操作，代价高
```

---

## 六、批判性总结

NoSQL 运动的兴起是数据库架构史上最重要的范式转移之一，但它常被误解为"反 SQL"或"反关系模型"。实际上，NoSQL 的核心洞察是 **"One Size Does Not Fit All"**（Stonebraker）——不同的数据访问模式需要不同的存储引擎和一致性模型。CAP 定理的真正价值不在于简单的"三选二"口诀，而在于迫使架构师显式思考分区场景下的行为选择。然而，NoSQL 的代价同样真实：文档数据库的模式灵活性在初期加速了开发，但在生产环境中常常导致**"模式漂移"灾难**——同一个集合中存在数十种文档变体，索引策略难以优化，查询性能不可预测。列族存储的可调一致性是一把双刃剑：QUORUM 读写提供了强一致性但牺牲了延迟和可用性，而 ANY/ONE 一致性可能导致读取到陈旧数据。图数据库虽然在关系遍历上无与伦比，但其扩展性瓶颈（图分区是 NP-Hard 问题）限制了超大规模应用。现代架构的趋势是**多模型数据库**（如 ArangoDB, Cosmos DB）和**专用引擎的组合**——但这也增加了数据一致性和运维的复杂度。


---

## 七、概念属性关系网络

### 7.1 核心概念依赖/包含/对立关系表

| 概念A | 关系类型 | 概念B | 关系说明 |
|-------|---------|-------|---------|
| NoSQL | ⊃ (包含) | KV Store | NoSQL包含键值存储子类 |
| NoSQL | ⊃ (包含) | Document Store | NoSQL包含文档存储子类 |
| NoSQL | ⊃ (包含) | Column Family | NoSQL包含列族存储子类 |
| NoSQL | ⊃ (包含) | Graph DB | NoSQL包含图数据库子类 |
| CAP | → (约束) | NoSQL Design | CAP定理约束NoSQL的设计选择 |
| Consistency | ⊥ (权衡) | Availability | 一致性与可用性的经典对立 |
| BASE | → (替代) | ACID | BASE是分布式NoSQL对ACID的替代哲学 |
| KV Store | → (简化) | Document Store | KV是Document的简化形式（Value无结构） |
| Document Store | → (简化) | Column Family | Document是Column的简化形式（无时间戳维度） |
| Graph DB | ⊥ (异构) | Relational Model | 图模型与关系模型在遍历查询上异构 |

### 7.2 ASCII拓扑图

```text
NoSQL数据模型概念拓扑
│
├─► CAP定理约束
│   ├─► C (Consistency) ──► 所有读返回最新写
│   ├─► A (Availability) ──► 每个请求获得响应（不保证最新）
│   └─► P (Partition Tolerance) ──► 网络分区下继续运行
│       └─► 定理: C ∧ A ∧ P 不可同时满足
│
│   CAP实例映射:
│   ├─► CA: 传统单机RDBMS (无分区容错)
│   ├─► CP: MongoDB, HBase, Redis Cluster (分区时拒绝部分写)
│   └─► AP: Cassandra, DynamoDB, Couchbase (分区时接受陈旧读)
│
├─► BASE语义
│   ├─► B (Basically Available) ──► 基本可用，允许降级
│   ├─► A (Soft State) ──► 状态无需时刻一致
│   └─► E (Eventual Consistency) ──► 无新更新时最终收敛
│
├─► 四种NoSQL模型
│   ├─► 键值存储 (KV)
│   │   ├─► Store = Key → Value (opaque)
│   │   ├─► 操作: GET, PUT, DELETE
│   │   ├─► 扩展: Redis支持list, set, hash, zset
│   │   └─► 代表: Redis, DynamoDB, Riak, etcd, RocksDB
│   │
│   ├─► 文档数据库 (Document)
│   │   ├─► Store = Collection of JSON/BSON Documents
│   │   ├─► 查询: 嵌套字段索引、聚合管道
│   │   ├─► 模式灵活: 同一集合可有不同结构文档
│   │   └─► 代表: MongoDB, Couchbase, Firestore
│   │
│   ├─► 列族存储 (Wide-Column / Column Family)
│   │   ├─► Store = {RowKey → {ColumnFamily → {Column → {Timestamp → Value}}}}
│   │   ├─► 物理存储按ColumnFamily聚簇
│   │   ├─► 优势: 稀疏矩阵高效存储，列动态扩展
│   │   └─► 代表: Cassandra, HBase, Bigtable, ScyllaDB
│   │
│   └─► 图数据库 (Graph)
│       ├─► G = (V, E, L, P)
│       ├─► 查询: 图遍历 (Traversal)、模式匹配 (Cypher/Gremlin)
│       ├─► 优势: 深度关系查询、推荐系统、知识图谱
│       └─► 代表: Neo4j, TigerGraph, Amazon Neptune
│
└─► 一致性可调谱系
    ├─► Cassandra: ANY → ONE → LOCAL_QUORUM → QUORUM → ALL
    └─► 一致性强度 ↑ ⟹ 延迟 ↑ ∧ 可用性 ↓
```

### 7.3 形式化映射

```text
概念映射:

f₁: Key → Value            via  kv_store.get(key)  (O(1)点查)
f₂: Query → Documents      via  document_collection.find(predicate)
                              predicate: { "user.address.city": "Beijing" }
f₃: (RowKey, ColumnKey, Timestamp) → Value
                              via  column_family.get(row, column, ts)
f₄: Graph × Pattern → Subgraph
                              via  graph.traversal(start, pattern).execute()
f₅: ConsistencyLevel → QuorumSize
                              via  W + R > N (N=副本数, W=写确认数, R=读确认数)
f₆: CAP_Choice → SystemBehavior
                              CP: partition → reject_writes (保证一致)
                              AP: partition → accept_stale_reads (保证可用)
```

---

## 八、形式化推理链

### 8.1 公理体系

**公理 1 (CAP不可能性公理)** — Eric Brewer, 2000; Seth Gilbert & Nancy Lynch, 2002
> 分布式数据存储系统在网络分区时，一致性与可用性不可兼得。
> Partition ⟹ ¬(Consistency ∧ Availability)

**公理 2 (最终一致性收敛公理)** — Werner Vogels, 2009
> 若无新更新，最终所有副本收敛到相同值。
> ∀replicas rᵢ, rⱼ: writes_stop_at(t) ⟹ ∃δ: ∀t' > t+δ: rᵢ(t') = rⱼ(t')

**公理 3 (Quorum交集公理)** — Thomas & VFD, 1985
> 若写Quorum W与读Quorum R满足 W + R > N，则读写操作至少访问一个共同副本。
> 保证: read_quorum ∩ write_quorum ≠ ∅

### 8.2 引理

**引理 1 (Cassandra一致性的延迟-强度单调性)**
> 一致性级别从ANY到ALL，延迟单调增，可用性单调减。
> Proof: ANY只需一个副本响应（可能为Hinted Handoff），ALL需全部N个副本响应。

**引理 2 (图分区的不可能性)**
> 图数据库的扩展性受限于图分区是NP-Hard问题。
> 最小化跨分区边割（edge cut）在一般图上无多项式时间精确解。

### 8.3 定理

**定理 1 (Dynamo的向量时钟一致性)** — DeCandia et al., 2007
> Dynamo使用向量时钟检测并发更新冲突。
>
> 形式化: 版本V₁与V₂
> V₁ < V₂ ⟺ ∀i: V₁[i] ≤ V₂[i] ∧ ∃j: V₁[j] < V₂[j]
> V₁ ∥ V₂ (并发) ⟺ ¬(V₁ < V₂) ∧ ¬(V₂ < V₁)
>
> 冲突时: 返回所有并发版本，由应用层解决（read repair或last-write-wins）

**定理 2 (Bigtable的多维映射形式化)** — Chang et al., 2006
> Bigtable是一个稀疏的、分布式的、持久化的多维有序映射。
> (row: string, column: string, time: int64) → string
>
> 性质:
> (1) 行内有序: 按RowKey字典序排序
> (2) 列族聚簇: 同一列族的数据物理存储在一起
> (3) 时间维度: 每个Cell可保存多个时间戳版本

### 8.4 推论

**推论 1 (NoSQL的模式灵活性代价)**
> 文档数据库的模式灵活性在生产环境中导致"模式漂移"灾难。
> 同一集合中存在数十种文档变体时，索引策略难以优化，查询性能不可预测。

**推论 2 (可调一致性的双刃剑)**
> QUORUM读写提供了强一致性但牺牲了延迟和可用性；
> ANY/ONE一致性可能导致读取到严重陈旧数据。
> 架构师必须显式为每个操作选择一致性级别。

---

## 九、ASCII推理判定树 / 决策树

### 9.1 NoSQL数据库选型决策树

```text
NoSQL数据库选型
│
├─► 数据访问模式是什么？
│   ├─ 简单Key查询 ──► 键值存储
│   │   ├─ 内存缓存为主 ──► Redis
│   │   ├─ 持久化+高可用 ──► DynamoDB / Riak
│   │   └─ 嵌入式/本地 ──► RocksDB / LevelDB
│   │
│   ├─ JSON文档查询 ──► 文档数据库
│   │   ├─ 丰富查询+聚合 ──► MongoDB
│   │   ├─ 移动同步 ──► Couchbase / Firestore
│   │   └─ 简单文档+事务 ──► DynamoDB (支持文档)
│   │
│   ├─ 宽列/时序数据 ──► 列族存储
│   │   ├─ 高写入吞吐 ──► Cassandra / ScyllaDB
│   │   ├─ Hadoop生态 ──► HBase
│   │   └─ 云托管 ──► Bigtable / DynamoDB
│   │
│   └─ 深度关系遍历 ──► 图数据库
│       ├─ 通用图查询 ──► Neo4j
│       ├─ 大规模分析 ──► TigerGraph
│       └─ 云托管 ──► Amazon Neptune
```

### 9.2 一致性级别选择决策树

```text
Cassandra一致性级别选择
│
├─► 读取延迟是否敏感？
│   ├─ 是（亚毫秒要求）──► ONE / LOCAL_ONE
│   │                       └─ 读取最近副本，可能陈旧
│   │
│   └─ 否 ──► 是否需要强一致性？
│               ├─ 是 ──► QUORUM (大多数副本)
│               │           ├─ 写QUORUM + 读QUORUM ⟹ 读写交集保证最新
│               │           └─ 延迟中等，可用性中等
│               │
│               └─ 否（可接受最终一致）──► LOCAL_QUORUM
│                                           └─ 本地数据中心quorum
│                                           └─ 避免跨地域RTT
```

---

## 十、国际权威课程对齐

### 10.1 MIT 6.830: Database Systems

| 课程内容 | 对应 Lecture | 对应本文件内容 | 映射深度 |
|---------|-------------|---------------|---------|
| Distributed Databases | Lec 12-13 | NoSQL的分布式设计 | 核心映射 |
| Consistency Models | Lec 4-5 | CAP定理与一致性级别 | 核心映射 |

### 10.2 Stanford CS 145 / CS 245: Database Systems

| 课程内容 | 对应模块 | 对应本文件内容 |
|---------|---------|---------------|
| Distributed Data Management | Lecture 11-12 | NoSQL的分布式架构 |
| Data Models | Lecture 3-4 | KV/文档/列族/图的数据模型对比 |

### 10.3 CMU 15-445: Database Systems

| 课程内容 | 对应 Lecture | 对应本文件内容 |
|---------|-------------|---------------|
| Distributed Database Systems | Lecture 23-24 | NoSQL与分布式数据存储 |
| Storage Models | Lecture 6 | 列式存储与分解存储模型 |

### 10.4 Berkeley CS 186: Database Systems

| 课程内容 | 对应模块 | 对应本文件内容 |
|---------|---------|---------------|
| Distributed Data | Lecture 26 | NoSQL与Replication |
| Data Models | Lecture 1, 8 | 关系模型与替代数据模型 |

### 10.5 核心参考文献

1. **Eric Brewer** (2000). "Towards Robust Distributed Systems." *PODC 2000*. —— CAP定理的首次提出，分布式数据库设计的理论基石。

2. **Giuseppe DeCandia et al.** (2007). "Dynamo: Amazon's Highly Available Key-Value Store." *SOSP 2007*. —— Amazon Dynamo的原始论文，定义了最终一致性、向量时钟和一致性哈希的工程实现。

3. **Fay Chang et al.** (2006). "Bigtable: A Distributed Storage System for Structured Data." *OSDI 2006*. —— Google Bigtable的原始论文，定义了列族存储的多维映射模型。

4. **Seth Gilbert & Nancy Lynch** (2002). "Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services." *ACM SIGACT News*, 33(2), 51-59. —— CAP定理的形式化证明，将Brewer的猜想提升为定理。

---

## 十一、批判性总结

NoSQL运动的兴起是数据库架构史上最重要的范式转移之一，但它常被误解为"反SQL"或"反关系模型"。实际上，NoSQL的核心洞察是Michael Stonebraker所阐述的"One Size Does Not Fit All"——不同的数据访问模式需要不同的存储引擎和一致性模型。CAP定理的真正价值不在于简单的"三选二"口诀，而在于迫使架构师显式思考分区场景下的行为选择：当网络分裂时，系统应该拒绝写入以保证一致性（CP），还是接受读取陈旧数据以保证可用性（AP）？这一选择的答案取决于业务的本质——金融交易系统通常选择CP，而社交媒体的时间线通常选择AP。然而，NoSQL的代价同样真实：文档数据库的模式灵活性在初期加速了开发，但在生产环境中常常导致"模式漂移"灾难——同一个集合中存在数十种文档变体，索引策略难以优化，查询性能不可预测。列族存储的可调一致性是一把双刃剑：QUORUM读写提供了强一致性但牺牲了延迟和可用性，而ANY/ONE一致性可能导致读取到严重陈旧的数据。图数据库虽然在关系遍历上无与伦比，但其扩展性瓶颈（图分区是NP-Hard问题）限制了超大规模应用。现代架构的趋势是多模型数据库（如ArangoDB, Cosmos DB）和专用引擎的组合——但这也增加了数据一致性和运维的复杂度。架构师应当认识到：NoSQL不是对关系模型的否定，而是对关系模型适用边界的必要补充——关系模型在复杂查询和事务保证上仍然无与伦比，而NoSQL在特定访问模式下的扩展性优势不可替代。
