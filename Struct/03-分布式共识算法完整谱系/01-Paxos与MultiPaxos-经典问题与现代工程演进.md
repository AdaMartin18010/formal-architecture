# Paxos与Multi-Paxos：经典问题与现代工程演进

> **定位**：Paxos是分布式共识算法的"相对论"——优美、正确，但难懂。Raft和HotStuff的存在，恰恰证明工程可读性（与正确性）并不矛盾。
>
> **核心命题**：理解Paxos不仅是历史兴趣，更是理解所有后续共识算法（Raft, PBFT, HotStuff）的共同祖先。

---

## 一、思维导图：Paxos家族树

```text
Paxos家族
│
├─【基础Paxos（Single-Decree）】
│   ├─ 准备阶段（Prepare）
│   │   └─ Proposer: prepare(n) → Promise(n, v)
│   ├─ 接受阶段（Accept）
│   │   └─ Proposer: accept(n, v) → Accepted(n, v)
│   └─ 仅就单一值达成共识
│
├─【Multi-Paxos】
│   ├─ 优化：Leader稳定后跳过Prepare阶段
│   ├─ 日志条目按索引顺序复制
│   └─ 等价于Raft（但描述方式不同）
│
├─【Fast Paxos】
│   ├─ 优化：无冲突时一轮RPC完成
│   └─ 冲突时回退到Classic Paxos
│
├─【Cheap Paxos / Flexible Paxos】
│   └─ 优化Quorum定义，降低写入成本
│
└─【工程实现】
    ├─ Chubby（Google）
    ├─ ZooKeeper ZAB（非严格Paxos但思想相近）
    └─ etcd / Raft（Multi-Paxos的工程简化）
```

---

## 二、Paxos的形式化定义

> **权威来源**：Leslie Lamport, "The Part-Time Parliament", *ACM TOCS*, 1998

### 2.1 基础Paxos（Single-Decree）

```
参与者角色：
  Proposer（提议者）：发起提案
  Acceptor（接受者）：投票决定是否接受
  Learner（学习者）：学习已决定的值

核心约束：
  P1: 接受者必须接受它收到的第一个提案
  P2: 如果值为v的提案被选择，则更高编号的提案也必须选择v

两阶段协议：

  Phase 1: Prepare
    Proposer → Acceptor: prepare(n)  // n是全局唯一的提案编号
    Acceptor → Proposer: promise(n, [已接受的最高编号提案])

    若多数Acceptor返回Promise，则进入Phase 2

  Phase 2: Accept
    Proposer → Acceptor: accept(n, v)
      // v = 若有已接受提案则选其值，否则选Proposer自己的值
    Acceptor → Proposer: accepted(n, v)

    若多数Acceptor返回Accepted，则v被选择

安全性（Safety）证明要点：
  - 任何两个多数派Quorum必有交集
  - 若v在Phase 2被选择，则后续提案在Phase 1必发现v
  - 因此P2成立，所有被选择的值相同
```

### 2.2 Multi-Paxos优化

```
问题：基础Paxos每次决策都需两阶段（2 RTT）

优化：稳定Leader跳过Prepare阶段

  正常工况（Leader稳定）：
    Leader → Followers: accept(idx, n, v)  // 仅需1 RTT
    Followers → Leader: accepted(idx, n, v)

  Leader变更时：
    新Leader执行完整两阶段以确定各索引的已提交值

  等价于Raft的：
    - Leader追加日志 = Multi-Paxos的Accept
    - Leader选举 = Paxos的Leader变更
```

---

## 三、Paxos vs Raft：同一算法的两种描述

| 维度 | **Paxos / Multi-Paxos** | **Raft** |
|------|------------------------|----------|
| **论文风格** | 形式化、数学化 | 工程化、模块化 |
| **易理解性** | 难（Lamport自认"难以理解"） | 易（专为教学设计） |
| **Leader概念** | 隐式、优化后才有 | 显式、核心设计 |
| **日志复制** | 按索引独立运行Paxos实例 | 日志是连续的，Leader驱动 |
| **成员变更** | 未在原论文中定义 | Joint Consensus机制 |
| **工程实现** | Chubby, Spanner | etcd, Consul, TiKV |
| **安全性** | 等价（可互相模拟） | 等价 |
| **性能** | 等价（优化后） | 等价 |

---

## 四、Paxos的工程教训

### 4.1 "Paxos Made Simple"的反讽

> **Lamport原话**："The Paxos algorithm, when presented in plain English, is very simple."
>
> **工程现实**：即便简化版，实现仍充满陷阱。

### 4.2 实际实现的难点

| 难点 | 描述 | 工程解决方案 |
|------|------|------------|
| **Leader选举未定义** | 原论文聚焦安全性，未指定Leader如何产生 | 租约（Lease）+ 超时选举 |
| **成员变更** | 动态增删节点无标准方案 | Raft的Joint Consensus；WYNAMIC Paxos |
| **日志压缩** | 无限增长 | 快照（Snapshot）+ 截断 |
| **读优化** | 强一致读需走共识（慢） | Lease Read, Read Index, Follower Read |
| **网络分区处理** | 脑裂双Leader | Fencing Token, 租约到期 |

### 4.3 为什么工程选择Raft而非Paxos

```
Raft的设计哲学：可理解性优先

  "We designed Raft to be easier to understand than Paxos..."
  — Ongaro & Ousterhout, In Search of an Understandable Consensus Algorithm

关键设计决策：
  1. 强Leader模型：所有操作通过Leader
     → 简化日志一致性保证

  2. 日志连续性：不允许日志空洞
     → 简化状态机复制

  3. 安全性与活性分离：
     - 安全性：状态机永远不会执行不一致的命令
     - 活性：系统最终会选出Leader并推进

  4. 成员变更：Joint Consensus
     → 安全地过渡新旧配置
```

---

## 五、概念定义与属性关系

| 概念 | 定义 | 属性 | 示例 | 反例 |
|------|------|------|------|------|
| **Single-Decree Paxos** | 就单一值达成共识的基础算法 | 两阶段、安全性保证、活性需额外假设 | 分布式锁的获取 | 日志复制（需要Multi-Paxos） |
| **Multi-Paxos** | 连续运行Paxos实例以复制日志 | 稳定Leader时1 RTT、与Raft等价 | Chubby的日志复制 | 基础Paxos（每次两阶段） |
| **Fast Paxos** | 无冲突时一轮RPC完成共识 | 冲突时回退、乐观优化 | 低竞争场景 | 高竞争场景（性能劣化） |
| **Quorum** | 多数派集合，任意两个Quorum必有交集 | 是Paxos安全性的核心 | 5节点中的3个 | 非多数派子集（如2/5） |

---

## 六、交叉引用

- → [03-总览](./00-总览-共识问题与算法家族树.md)
- → [03/02-Raft](02-Raft-状态机复制与模块化工程化.md)
- → [03/04-HotStuff](04-HotStuff-线性复杂度BFT共识.md)
- ↓ [07/02-TLA+验证](../../07-形式化方法与验证体系/02-TLA+-时序逻辑与规范验证.md)

---

## 七、参考文献

| 作者 | 标题 | 出处 | 年份 |
|------|------|------|------|
| Leslie Lamport | "The Part-Time Parliament" | *ACM TOCS* | 1998 |
| Leslie Lamport | "Paxos Made Simple" | *ACM SIGACT News* | 2001 |
| Diego Ongaro, John Ousterhout | "In Search of an Understandable Consensus Algorithm" | *ATC* | 2014 |
| Mike Burrows | "The Chubby lock service..." | *OSDI* | 2006 |

---

*文件创建日期：2026-04-23*
*状态：已完成*
