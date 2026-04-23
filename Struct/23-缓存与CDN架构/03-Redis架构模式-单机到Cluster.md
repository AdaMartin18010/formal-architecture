# Redis 架构模式：从单机到 Cluster

> **来源映射**: View/00.md §2.1
> **国际权威参考**: Redis 官方文档, "Redis Cluster Specification" (antirez), "Dissecting Redis" (Martin Kleppmann)

---

## 一、知识体系思维导图

```text
Redis 架构演进谱系
│
├─► 单机模式 (Standalone)
│   ├─► 单线程事件循环 (epoll/kqueue)
│   ├─► 内存数据集 + AOF/RDB 持久化
│   └─► 单点故障、容量受限、无水平扩展
│
├─► 主从复制 (Replication)
│   ├─► 全量同步 (RDB snapshot + buffer)
│   ├─► 增量同步 (PSYNC2, replication offset)
│   ├─► 读写分离 (读→从, 写→主)
│   └─► 手动故障转移
│
├─► Sentinel 高可用
│   ├─► 哨兵集群监控 (SDOWN / ODOWN)
│   ├─► 自动故障转移 (raft-like leader election)
│   ├─► 客户端通知 (pub/sub 配置变更)
│   └─► 只保证高可用，不保证扩展性
│
├─► Cluster 分片集群
│   ├─► 16384 哈希槽 (Hash Slot)
│   ├─► 去中心化 Gossip 协议
│   ├─► 客户端重定向 (MOVED / ASK)
│   ├─► 主从复制 per shard
│   └─► 自动故障转移 (基于 Sentinel 思想)
│
└─► 代理模式 (Proxy)
    ├─► Twemproxy (Twitter): 静态分片
    ├─► Codis: 基于 ZooKeeper 的平滑扩缩容
    └─► Redis Cluster Proxy: 官方代理
```

---

## 二、核心概念的形式化定义

**定义 1 (Redis 单线程模型)**:
设事件循环为 $E$，文件描述符集合为 $F$，则每个时间步：
$$E: \text{aeProcessEvents}(F) \rightarrow \text{read}(f_i) \rightarrow \text{process}(cmd_j) \rightarrow \text{write}(resp)$$
所有命令串行执行，无锁竞争，时间复杂度为 $O(1)$ 的命令保证恒定延迟。

**定义 2 (主从复制的形式化)**:
设主节点状态为 $M_t$，从节点状态为 $S_t$，复制偏移为 $offset$:
$$\Delta_t = M_t - S_t \text{ (replication backlog)}$$
全量同步: $S_0 \leftarrow RDB(M_t)$
增量同步: $S_{t+\delta} \leftarrow S_t \oplus \Delta_{[t, t+\delta]}$

**定义 3 (哈希槽分片)**:
$$Slot(key) = CRC16(key) \mod 16384$$
$$Cluster = \bigcup_{i=1}^{n} Shard_i, \quad Shard_i = \langle Master_i, \{Replica_{i,j}\}, Slots_i \rangle$$
其中 $\bigcap_{i=1}^{n} Slots_i = \emptyset$，$\bigcup_{i=1}^{n} Slots_i = [0, 16383]$

**定义 4 (Gossip 协议)**:
设节点集合 $V = \{v_1, v_2, ..., v_n\}$，每周期节点 $v_i$ 随机选择 $k$ 个节点交换状态：
$$Exchange(v_i, v_j) \rightarrow \text{merge}(State_i, State_j)$$
信息传播的收敛时间: $O(\log n)$ 轮（概率性保证）

---

## 三、多维矩阵对比

| 架构模式 | 数据容量 | 读吞吐 | 写吞吐 | 高可用 | 扩展性 | 一致性 |
|---------|---------|--------|--------|--------|--------|--------|
| **单机** | 内存上限 | 10万 QPS | 10万 QPS | 无 | 无 | 强一致 |
| **主从复制** | 内存上限 | 横向扩展 | 主节点上限 | 手动切换 | 读扩展 | 最终一致 |
| **Sentinel** | 内存上限 | 横向扩展 | 主节点上限 | **自动** | 读扩展 | 最终一致 |
| **Cluster** | **横向扩展** | 横向扩展 | **横向扩展** | **自动** | **线性扩展** | 最终一致 |
| **Codis/Twemproxy** | 横向扩展 | 横向扩展 | 横向扩展 | 依赖底层 | 平滑扩缩容 | 最终一致 |

| 协议/机制 | 用途 | 通信开销 | 收敛速度 | 容错性 |
|----------|------|---------|---------|--------|
| **PSYNC2** | 主从增量复制 | 低 | 实时 | 断点续传 |
| **Raft (Sentinel)** | 领导者选举 | 中 | 秒级 | 多数派存活 |
| **Gossip** | 集群状态传播 | 中 | $O(\log n)$ | 高(去中心化) |
| **MOVED/ASK** | 客户端重定向 | 一次往返 | 即时 | 无状态 |

---

## 四、权威引用

> **Salvatore Sanfilippo (antirez)** ("Redis Cluster Specification", 2015):
> "Redis Cluster uses a gossip protocol to propagate information about the cluster topology so that every node eventually converges to the same view."

> **Martin Kleppmann** ("Designing Data-Intensive Applications", 2017):
> "Redis is not just a cache; its data structures and atomic operations make it suitable for queues, real-time analytics, and leaderboards."

> **Twitter Engineering** ("Twemproxy: A Redis/Memcache proxy", 2012):
> "At Twitter scale, we needed a lightweight proxy to partition data across hundreds of cache backends without changing application code."

---

## 五、工程实践与代码示例

```text
# Redis Cluster 槽位迁移的核心命令流程
# 1. 设定迁移目标
CLUSTER SETSLOT <slot> MIGRATING <target_node_id>

# 2. 在目标节点设定导入状态
CLUSTER SETSLOT <slot> IMPORTING <source_node_id>

# 3. 逐个迁移键 (原子性的 DUMP + RESTORE)
MIGRATE <target_ip> <target_port> <key> 0 <timeout>

# 4. 完成迁移，将槽位分配给目标节点
CLUSTER SETSLOT <slot> NODE <target_node_id>
```

```python
# Python redis-py-cluster 的 ASK 重定向处理
from rediscluster import RedisCluster

startup_nodes = [
    {"host": "127.0.0.1", "port": "7000"},
    {"host": "127.0.0.1", "port": "7001"}
]

# 客户端自动处理 MOVED/ASK 重定向
rc = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)

# 键自动路由到正确槽位
rc.set("foo", "bar")  # 路由到 Slot(12182) 所在节点
```

---

## 六、批判性总结

Redis 的架构演进清晰地反映了分布式系统从**垂直扩展**到**水平扩展**的必然路径，但每一步扩展都伴随着一致性和操作复杂性的代价。

单线程事件循环是 Redis 的设计精髓，也是其最大瓶颈。虽然 Redis 6.0+ 引入了多线程 IO，但命令执行仍为单线程——这意味着在 Cluster 模式下，**单个热键（hot key）的写入仍然无法通过分片扩展**，因为同一个键始终路由到同一个槽位。这在秒杀、计数器等场景中构成了根本性的架构约束。

Gossip 协议作为 Cluster 的核心通信机制，其概率性收敛特性在工程实践中常被低估。当网络分区发生时，两个隔离的节点子集可能各自更新拓扑视图，导致**脑裂后合并不是瞬间完成的**。虽然 Redis Cluster 通过 `cluster-node-timeout` 和配置纪元（configuration epoch）来缓解这一问题，但与 Raft/Paxos 的强一致性保证相比，Gossip 更适合**最终一致的元数据同步**，而非关键状态的共识达成。

值得深思的是，Redis Cluster 的 16384 个槽位设计是一个精妙的工程妥协：槽位数量必须足够大以实现细粒度负载均衡，但又不能太大以至于集群元数据（每个节点存储的槽位映射表）过度膨胀。16384 = $2^{14}$，使得槽位位图仅需 2KB 即可表示整个集群的拓扑——这是**空间效率与灵活性**之间的最佳平衡点。
