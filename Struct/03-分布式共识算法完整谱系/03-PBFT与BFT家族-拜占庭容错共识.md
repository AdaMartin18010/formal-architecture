# PBFT与BFT家族：拜占庭容错共识

> **定位**：从Crash Fault Tolerance（CFT）到Byzantine Fault Tolerance（BFT），是共识算法从"可信任数据中心"到"开放对抗环境"的跃迁。BFT的代价是3f+1节点（vs CFT的2f+1），但区块链和跨组织协作使BFT成为必需。
>
> **核心命题**：BFT不是区块链专属；任何需要容忍恶意行为的场景（跨组织数据共享、外包计算验证）都需要BFT。
>
> **来源映射**：Castro & Liskov(1999) → Tendermint/DiemBFT → 区块链与跨组织共识

---

## 一、思维导图：BFT共识家族

```text
BFT共识家族
│
├─【经典BFT】
│   ├─ PBFT（Practical Byzantine Fault Tolerance）
│   │   ├─ 1999年Castro & Liskov
│   │   ├─ 三阶段：PRE-PREPARE → PREPARE → COMMIT
│   │   ├─ 视图变更（View Change）处理Leader故障
│   │   └─ 复杂度：O(n²)
│   │
│   └─ Tendermint / BFT-SMaRt
│       ├─ 基于PBFT优化
│       └─ 区块链友好设计
│
├─【优化BFT】
│   ├─ HotStuff
│   │   ├─ 线性复杂度 O(n)
│   │   ├─ 阈值签名
│   │   └─ 链式结构（Chained HotStuff）
│   │
│   ├─ Streamlet
│   │   ├─ 极简设计（两消息类型）
│   │   └─ 更易理解和实现
│   │
│   └─ Narwhal & Tusk / Bullshark
│       ├─ DAG-based
│       └─ 解耦数据传播与共识
│
└─【CFT vs BFT对比】
    ├─ 节点数：2f+1 vs 3f+1
    ├─ 消息复杂度：O(n) vs O(n²)（PBFT）/ O(n)（HotStuff）
    ├─ 应用场景：数据中心 vs 区块链/跨组织
    └─ 信任假设：可信基础设施 vs 对抗环境
```

---

## 二、PBFT三阶段协议

> **权威来源**：Miguel Castro, Barbara Liskov, "Practical Byzantine Fault Tolerance", *OSDI*, 1999

```
PBFT三阶段协议（正常工况）：

  Phase 1: PRE-PREPARE
    Leader → All Replicas: <<PRE-PREPARE, v, n, d>, m>
      v = 视图编号, n = 序列号, d = m的摘要, m = 客户端请求

    每个Replica验证：
      - d是m的正确摘要
      - n在合理范围内
      - 未接受过相同<v,n>的不同d

    验证通过 → 进入PREPARED状态

  Phase 2: PREPARE
    Replica → All: <PREPARE, v, n, d, i>
      i = Replica编号

    每个Replica收集PREPARE消息，直到收到2f个匹配（含自己）
    → 进入PREPARED-CERTIFIED状态

  Phase 3: COMMIT
    Replica → All: <COMMIT, v, n, d, i>

    每个Replica收集COMMIT消息，直到收到2f+1个匹配（含自己）
    → 请求被COMMIT，可执行并回复客户端

安全性保证：
  - 诚实节点在PREPARED状态达成一致
  - 若f个恶意节点，需要2f+1个COMMIT确保至少f+1个诚实节点已PREPARE
  - 因此诚实节点不可能对冲突请求同时COMMIT

视图变更（View Change）：
  - Leader可能是恶意的，需超时触发视图变更
  - 新Leader收集2f+1个VIEW-CHANGE消息
  - 确定新视图中各序列号的已提交请求
```

---

## 三、CFT vs BFT：成本与收益

| 维度 | **CFT（Raft/Paxos）** | **BFT（PBFT/HotStuff）** |
|------|----------------------|------------------------|
| **容错节点数** | f（总节点2f+1） | f（总节点3f+1） |
| **正常工况消息** | O(n)（Leader广播） | O(n²)（PBFT全互联）/ O(n)（HotStuff） |
| **视图变更成本** | 低（选举新Leader） | 高（需证明状态转移正确性） |
| **密码学开销** | 无 | 数字签名/阈值签名 |
| **吞吐量** | 高（~100K+ req/s） | 中（~10K req/s，PBFT）/ 高（HotStuff） |
| **延迟** | 低（~1-2 RTT） | 高（~3-5 RTT，PBFT）/ 中（HotStuff） |
| **信任假设** | 节点可信但可能崩溃 | 节点可能任意恶意行为 |
| **适用场景** | 数据中心内部 | 区块链、跨组织、外包计算 |

---

## 四、BFT的工程挑战

### 4.1 为什么BFT慢

```
性能瓶颈分析：

  1. 消息复杂度
     PBFT: O(n²) — 每阶段每个节点向所有节点广播
     Raft: O(n) — Leader向Followers广播

  2. 密码学开销
     PBFT: 每消息需数字签名验证
     HotStuff: 阈值签名聚合（O(n)验证）

  3. 视图变更
     PBFT: 需收集并验证大量消息以证明状态
     HotStuff: 阈值签名简化视图变更

优化路径：
  PBFT → HotStuff: 从O(n²)到O(n)
  关键创新：阈值签名（Threshold Signature）
    - 每个节点签名的份额可聚合成单一签名
    - 验证成本与节点数无关
```

### 4.2 BFT在区块链中的应用

| 系统 | BFT变体 | 特点 |
|------|--------|------|
| **Tendermint（Cosmos）** | PBFT优化 | 区块提案+投票两轮；即时最终性 |
| **DiemBFT（原Libra）** | HotStuff | 线性复杂度；链式结构 |
| **Aptos** | Bullshark | DAG-based；高并发 |
| **Sui** | Mysticeti | DAG优化；亚秒最终性 |

---

## 五、概念定义与属性关系

| 概念 | 定义 | 属性 | 示例 | 反例 |
|------|------|------|------|------|
| **BFT** | 容忍最多f个节点任意恶意行为的共识 | 高成本（3f+1节点）、强安全保证 | 区块链共识 | CFT（仅容忍崩溃） |
| **PBFT** | 首个实用的BFT共识算法 | 三阶段、O(n²)、1999年 | Hyperledger Fabric | HotStuff（O(n)优化） |
| **阈值签名** | 多方签名份额可聚合成单一签名 | O(1)验证、降低BFT通信复杂度 | HotStuff, Tendermint | 传统数字签名（O(n)验证） |
| **视图变更** | BFT中Leader故障时的换主机制 | 复杂、是BFT性能瓶颈 | PBFT View Change | Raft选举（更简单） |
| **即时最终性** | 区块一旦提交不可回滚 | 强一致性、适合金融 | Tendermint, HotStuff | PoW的概率最终性 |

---

## 六、交叉引用

- → [03-总览](./00-总览-共识问题与算法家族树.md)
- → [03/01-Paxos](01-Paxos与MultiPaxos-经典问题与现代工程演进.md)
- → [03/04-HotStuff](04-HotStuff-线性复杂度BFT共识.md)
- → [03/05-Bullshark](05-Bullshark-DAG共识与异步优势.md)
- ↓ [09/02-可信计算](../09-安全模型与可信计算/02-可信计算-从形式验证到运行时可信.md)

---

## 七、参考文献

| 作者 | 标题 | 出处 | 年份 |
|------|------|------|------|
| Castro, Liskov | "Practical Byzantine Fault Tolerance" | *OSDI* | 1999 |
| Yin et al. | "HotStuff: BFT Consensus in the Lens of Blockchain" | *arXiv* | 2018 |
| Spiegelman et al. | "Bullshark: DAG BFT Protocols Made Practical" | *arXiv* | 2022 |
| Buchman et al. | "Tendermint: Byzantine Fault Tolerance in the Age of Blockchains" | Thesis | 2016 |

## 八、权威引用

> **Miguel Castro and Barbara Liskov** (1999): "Practical Byzantine Fault Tolerance achieves consensus in asynchronous distributed systems where less than one-third of the replicas may behave arbitrarily."

> **Ethan Buchman et al.** (2016): "Tendermint combines Byzantine fault tolerance with blockchain semantics to provide a practical consensus engine for proof-of-stake systems."

## 九、批判性总结

PBFT将拜占庭容错从理论可能性转化为工程现实，但其O(n²)消息复杂度和3f+1的节点成本使其长期局限于学术和小规模联盟链场景。隐含假设是：恶意节点的行为是任意的但计算能力有限（无法破解密码学承诺）；随着量子计算的发展，这一假设可能被动摇。失效条件包括：视图变更期间的网络风暴（新Leader需收集并验证大量VIEW-CHANGE消息）、密码学签名验证的CPU瓶颈（在高吞吐场景成为主要延迟来源）、以及f+1诚实节点假设在网络分区中的脆弱性（分区可能使诚实节点分散到无法形成Quorum的子集）。与CFT共识（Raft/Paxos）相比，BFT的代价是50%额外节点和显著更高的实现复杂度；未来趋势是HotStuff及其DAG后继者通过阈值签名和流水线将BFT消息复杂度降至O(n)，以及硬件可信执行环境（TEE）的兴起可能重新定义"拜占庭"的边界——将部分容错责任从软件协议转移到硬件保障。

---

## 十、形式化定义

```text
BFT共识形式化定义：
  设系统包含 n 个副本节点，其中最多 f 个节点可能呈现拜占庭故障
  则安全性要求：n ≥ 3f + 1

  BFT共识的核心属性：
    一致性（Agreement）：所有非故障节点对相同的请求序列达成一致
    有效性（Validity）：被提交的请求必须来自客户端
    终止性（Termination）：所有非故障节点最终提交请求

PBFT三阶段形式化：
  设 V = {v₁, v₂, ...} 为视图集合，每个视图有唯一主节点 p = v mod n
  对于请求 m，协议生成证书：
    PRE-PREPARE证书：⟨⟨PRE-PREPARE, v, n, d⟩, m⟩，由主节点签名
    PREPARE证书：集合 {⟨PREPARE, v, n, d, i⟩ | i ∈ 接受节点集}
    COMMIT证书：集合 {⟨COMMIT, v, n, d, i⟩ | i ∈ 提交节点集}

  安全性条件：
    若某请求在视图 v 中被提交，则所有诚实节点在视图 v' ≥ v 中
    对该请求的排序保持一致

  视图变更形式化：
    新主节点 p' 需收集 2f+1 个 VIEW-CHANGE 消息
    并证明已提交请求在新视图中的连续性
```

---

*文件创建日期：2026-04-23*
*状态：已完成*
