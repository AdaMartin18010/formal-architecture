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
