# Kafka 的分布式日志：分区、复制与 ISR

> **来源映射**: View/00.md §3.1
> **国际权威参考**: "Kafka: a Distributed Messaging System for Log Processing" (Kreps et al., LinkedIn 2011)

---

## 一、知识体系思维导图

```text
Kafka 分布式日志核心机制
│
├─► Topic 与 Partition
│   ├─ Topic: 消息的逻辑分类 (类似数据库表)
│   ├─ Partition: Topic 的物理分片，有序、不可变的提交日志
│   ├─ 每个 Partition 是一个追加写的日志文件
│   └─ 分区数决定并行度: 消费者数 ≤ 分区数
│
├─► 生产者 (Producer)
│   ├─ 分区策略:
│   │   ├─ 轮询 (RoundRobin): 无 key 时均匀分配
│   │   ├─ 按 key 哈希: 保证同 key 消息顺序
│   │   └─ 自定义分区器
│   ├─ ACK 级别:
│   │   ├─ acks=0: 发完不管 (最高吞吐)
│   │   ├─ acks=1: Leader 确认 (平衡)
│   │   └─ acks=all: ISR 全部确认 (最高可靠)
│   └─ 幂等生产者: PID + Sequence Number
│
├─► 消费者组 (Consumer Group)
│   ├─ 组内消费者协同消费分区
│   ├─ 每个分区只能被一个消费者持有
│   └─ 再均衡 (Rebalance): 消费者加入/离开时重新分配
│
├─► 复制机制
│   ├─ Leader-Follower 模型
│   ├─ ISR (In-Sync Replicas): 与 Leader 保持同步的副本
│   ├─ HW (High Watermark): 已提交的最大偏移
│   ├─ LEO (Log End Offset): 当前日志末尾
│   └─ min.insync.replicas: 最小同步副本数
│
└─► KRaft (Kafka Raft)
    ├─ 替代 ZooKeeper: 自管理元数据
    ├─ 基于 Raft 共识算法
    └─ 优势: 简化架构、降低延迟、提高可扩展性
```

---

## 二、核心概念的形式化定义

### 2.1 Partition 日志结构

```text
定义 (分区日志):
  Partition p 是一个有序、不可变、追加的消息序列:
    p = [m₀, m₁, m₂, ..., mₙ]

  消息结构:
    mᵢ = ⟨offset=i, key, value, timestamp, headers⟩

  关键性质:
    1. 顺序性: ∀i < j, mᵢ 在 mⱼ 之前写入
    2. 不可变性: mᵢ 一旦写入不可修改
    3. 持久性: 写入后即使 Broker 崩溃也不丢失 (已复制到 ISR)
    4. 偏移唯一性: offset 在分区内全局唯一、单调递增
```

### 2.2 ISR 与一致性

```text
定义 (ISR - In-Sync Replicas):
  设 Partition p 的副本集合 R = {r₀, r₁, ..., rₖ}，其中 r₀ 是 Leader

  ISR(p) = {r ∈ R | lag(r, r₀) ≤ replica.lag.time.max.ms}

  即: ISR 是与 Leader 的日志延迟在可接受时间窗口内的副本

  提交条件 (acks=all):
    消息 m 被提交 ⟺ m 已写入 ISR 中的所有副本

  可用性条件:
    Partition 可写 ⟺ |ISR(p)| ≥ min.insync.replicas

  Leader 选举:
    若 Leader 失效，从 ISR 中选举新 Leader
    若 ISR 为空，根据 unclean.leader.election.enable 决定:
      - false: 等待 ISR 恢复 (可用性降低，一致性保证)
      - true: 从所有副本中选 Leader (可用性优先，可能丢失数据)
```

---

## 三、ACK 级别与权衡矩阵

| ACK 级别 | 语义 | 延迟 | 吞吐 | 数据丢失条件 | 适用场景 |
|---------|------|------|------|------------|---------|
| **acks=0** | 最多一次 (At Most Once) | **最低** | **最高** | 任意 Broker 故障 | 日志采集、 metrics |
| **acks=1** | 至少一次 (At Least Once) | 低 | 高 | Leader 崩溃且未同步到 Follower | 普通消息 |
| **acks=all** | 至少一次 + 最强持久化 | 高 | 中 | **ISR 全部故障** | 金融交易、订单 |
| **acks=all + 幂等** | **恰好一次 (Exactly Once)** | 高 | 中 | ISR 全部故障 (重复概率极低) | 对账、计费 |

---

## 四、权威引用

> **Jay Kreps** (Kafka 作者, LinkedIn, 2011):
> "Kafka: a Distributed Messaging System for Log Processing." —— "日志即真相"思想的奠基论文。

> **Jun Rao** (Kafka 核心开发者, Confluent):
> "Replication is the most important feature in a distributed system. Without it, you don't have a distributed system; you have a single point of failure."

> **Martin Kleppmann** ("Designing Data-Intensive Applications"):
> "Logs are the source of truth; everything else is a derived view."

---

## 五、工程实践

### 5.1 生产者配置示例

```java
Properties props = new Properties();
props.put("bootstrap.servers", "kafka1:9092,kafka2:9092");
props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");

// 高可靠性配置
props.put("acks", "all");                    // 等待 ISR 全部确认
props.put("retries", Integer.MAX_VALUE);      // 无限重试
props.put("enable.idempotence", "true");      // 幂等生产者
props.put("max.in.flight.requests.per.connection", "5"); // 管道化

// ISR 配置
props.put("min.insync.replicas", "2");        // 至少 2 个副本确认

Producer<String, String> producer = new KafkaProducer<>(props);
producer.send(new ProducerRecord<>("orders", orderId, orderJson));
```

### 5.2 ISR 监控指标

```text
关键监控指标:
  - UnderReplicatedPartitions: 副本不足的 Partition 数
  - OfflinePartitions: 无 Leader 的 Partition 数
  - RequestLatency: 生产/消费延迟
  - ISRShrink/ISRExpand: ISR 变化频率
  - LogEndOffset - HighWatermark: 未提交消息数

告警规则:
  - UnderReplicatedPartitions > 0 → 立即告警
  - OfflinePartitions > 0 → 紧急告警
  - RequestLatency > 100ms (P99) → 性能告警
```

---

## 六、批判性总结

Kafka 的 ISR 机制是**CAP 定理**的工程实现：当网络分区发生时，Kafka 选择**一致性**（等待 ISR 恢复）还是**可用性**（允许 unclean leader election）由配置决定。默认配置 `unclean.leader.election.enable=false` 表明 Kafka 的设计偏好是**一致性优先**——这与 Redis Cluster 的可用性优先形成鲜明对比。

KRaft 模式（Kafka 3.0+ 默认）是 Kafka 架构的**自我革命**：用 Raft 共识替代 ZooKeeper，消除了外部依赖的运维复杂性。这验证了分布式系统的**内聚性原则**——将元数据管理纳入系统自身，减少跨系统协调的故障面。但 KRaft 的推进也意味着 ZooKeeper 在 Kafka 生态中的角色逐步退出，这是技术债务清理的典型案例。
