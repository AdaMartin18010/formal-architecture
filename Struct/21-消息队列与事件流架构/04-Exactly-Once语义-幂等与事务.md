# Exactly-Once 语义：幂等与事务

> **来源映射**: View/01.md §3.1.4, Struct/21-消息队列与事件流架构/00-总览-消息队列的形式化谱系.md
> **国际权威参考**: KIP-98: Exactly Once Delivery and Transactional Messaging (Confluent, 2017); "Exactly-Once Semantics Are Possible: Here's How Kafka Does It" (Neha Narkhede, 2017)

---

## 一、知识体系思维导图

```text
Exactly-Once 语义实现
│
├─► 语义层级
│   ├─ At-Most-Once: 最多一次 (可能丢失)
│   ├─ At-Least-Once: 至少一次 (可能重复)
│   └─ Exactly-Once: 恰好一次 (不丢不重)
│
├─► 幂等生产者 (Idempotent Producer)
│   ├─ PID (Producer ID) + Sequence Number
│   ├─ Broker 端去重: 拒绝重复 Sequence Number
│   ├─ 幂等范围: 单分区、单会话 (PID 有效期内)
│   └─ 形式化: f(f(x)) = f(x)
│
├─► 事务 API (Transactions API)
│   ├─ TransactionalId: 跨会话恢复 Producer 状态
│   ├─ 事务协调器 (Transaction Coordinator)
│   ├─ 两阶段提交协议 (2PC 简化版)
│   │   ├─ Phase 1: 发送消息到分区，标记事务
│   │   └─ Phase 2: commitTransaction() 或 abortTransaction()
│   └─ 消费者隔离级别: read_committed / read_uncommitted
│
└─► EOS 流处理 (Kafka Streams EOS)
    ├─ 消费-处理-生产 的原子性
    ├─ 通过事务保证: Offset 提交 + 输出消息 原子写入
    └─ 形式化: process(msg) → [new_offsets, new_messages] 原子提交
```

---

## 二、核心概念的形式化定义

### 2.1 幂等性的形式化

```text
定义 (幂等操作):
  设操作 f: S → S 作用于状态 S
  f 是幂等的 ⟺ ∀s ∈ S: f(f(s)) = f(s)
  
Kafka 幂等生产者:
  设 Producer 状态 = ⟨PID, seq_num_per_partition⟩
  Broker 维护每个分区的已接收序列号集合: Received[PID][partition]
  
  去重条件:
    accept(msg) ⟺ msg.seq_num > max(Received[PID][partition])
    
  幂等性保证:
    若网络重传导致同一消息发送多次，仅第一次被接受
    形式化: send(m) retry N 次 ⟹ append(m) 执行恰好 1 次
```

### 2.2 事务的形式化

```text
定义 (Kafka 事务 T):
  T = ⟨TransactionalId, PID, partitions, state⟩
  
  状态机:
    Init → Ongoing → PrepareCommit → Committed
                        ↘ PrepareAbort  → Aborted
  
  原子性保证:
    ∀msg ∈ T: commit(T) → all msgs visible
              abort(T) → no msgs visible
  
  隔离级别:
    read_uncommitted: 消费者看到所有消息 (包括未提交的)
    read_committed:   消费者仅看到已提交消息 (过滤 abort 的)
```

### 2.3 Exactly-Once 的组成证明

```text
定理 (Exactly-Once = At-Least-Once + Idempotency + Transactions):
  
  (1) At-Least-Once: acks=all + 生产者重试 保证消息不丢失
  (2) Idempotency: PID + SeqNum 保证 Broker 端不重复写入
  (3) Transactions: 保证跨分区、跨 Topic 的原子可见性
  
  推论:
    在 Kafka 内部流转中: Exactly-Once 可达
    在 Kafka ↔ 外部系统: 需要外部系统支持幂等写入 (idempotent consumer)
```

---

## 三、多维矩阵对比

| 维度 | At-Most-Once | At-Least-Once | Exactly-Once (Kafka) | Exactly-Once (Flink) |
|------|-------------|--------------|---------------------|---------------------|
| **丢失风险** | 有 | 无 | 无 | 无 |
| **重复风险** | 无 | 有 | 无 (Kafka 内部) | 无 |
| **生产者配置** | acks=0 | acks=1/all | enable.idempotence=true | Two-Phase Commit |
| **消费者配置** | 自动提交 | 手动提交 | isolation.level=read_committed | Checkpoint |
| **吞吐量影响** | 最高 | 中 | 低 (约 10-20% 下降) | 低 |
| **外部系统集成** | 简单 | 简单 | 需外部幂等 | 需外部事务支持 |
| **故障恢复** | 无 | 可能重复消费 | 精确恢复 | 精确恢复 |

---

## 四、权威引用

> **Neha Narkhede** (Confluent, "Exactly-Once Semantics Are Possible", 2017):
> "Exactly-once semantics in Kafka are achieved through idempotent producers and atomic transactions. The idempotent producer eliminates duplicates due to producer retries, and transactions enable atomic multi-partition writes."

> **KIP-98: Exactly Once Delivery and Transactional Messaging** (Apache Kafka, 2017):
> "This proposal adds the notion of a transaction to Kafka. A transaction allows a producer to send messages to multiple partitions such that either all or none of the messages are ever visible to consumers."

> **Jay Kreps** ("I ♥ Logs", O'Reilly, 2014):
> "There is no exactly-once delivery in distributed systems. What there can be is an exactly-once processing guarantee—idempotent operations make retries safe."

---

## 五、工程实践与代码示例

### 幂等 + 事务生产者配置

```java
Properties props = new Properties();
props.put("bootstrap.servers", "localhost:9092");
props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");

// 幂等 + 事务
props.put("enable.idempotence", "true");
props.put("transactional.id", "my-producer-1"); // 跨会话恢复
props.put("acks", "all");
props.put("retries", Integer.MAX_VALUE);

KafkaProducer<String, String> producer = new KafkaProducer<>(props);
producer.initTransactions();

try {
    producer.beginTransaction();
    producer.send(new ProducerRecord<>("topic-a", "key1", "value1"));
    producer.send(new ProducerRecord<>("topic-b", "key2", "value2"));
    producer.commitTransaction();  // 原子提交到两个 Topic
} catch (Exception e) {
    producer.abortTransaction();
}
```

---

## 六、批判性总结

Kafka 的 Exactly-Once 实现是分布式消息系统领域最重要的工程突破之一，但它常被误解为"魔法般的保证"。**Kafka EOS 仅在 Kafka 内部流转时成立**——一旦数据离开 Kafka 进入外部数据库、缓存或第三方系统，EOS 的保证边界即被打破。此时需要依赖外部系统的幂等性（如数据库 UPSERT、带条件的写入等）来实现端到端的 Exactly-Once。更深层的问题是：事务 API 基于简化的两阶段提交协议，事务协调器是单点瓶颈，高并发事务场景下可能成为吞吐量瓶颈。此外，`read_committed` 隔离级别引入了"事务消息可见性延迟"（消费者需等待事务提交才能读取），这在实时性要求高的场景下不可接受。幂等生产者的会话绑定（PID 与 broker 连接关联）意味着** Producer 重启后旧会话的幂等窗口丢失**，需要 TransactionalId 机制跨会话恢复状态，这进一步增加了运维复杂度。
