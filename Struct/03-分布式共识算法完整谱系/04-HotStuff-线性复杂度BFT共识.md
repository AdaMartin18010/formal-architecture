# HotStuff：线性复杂度BFT共识

> **定位**：HotStuff是BFT共识从"学术可证明"到"工业可部署"的关键突破——它用阈值签名将PBFT的O(n²)消息复杂度降到O(n)，同时保留了可证明的安全性。DiemBFT（原Libra）和多个主流区块链采用了HotStuff。
>
> **核心命题**：消息复杂度不是理论细节，而是工程瓶颈。O(n²)意味着100个节点的BFT系统每轮需要10,000条消息；O(n)意味着仅需100条。

---

## 一、思维导图：HotStuff核心创新

```text
HotStuff
│
├─【核心创新】
│   ├─ 阈值签名（Threshold Signature）
│   │   └─ n个签名份额 → 聚合成1个签名
│   ├─ 三阶段线性通信
│   │   └─ Leader收集签名，广播聚合结果
│   └─ 链式结构（Chained HotStuff）
│       └─ 流水线化，提高吞吐量
│
├─【与PBFT对比】
│   ├─ 消息：O(n²) → O(n)
│   ├─ 视图变更：简化（阈值签名证明）
│   └─ 实现复杂度：中等（需密码学库）
│
├─【安全保证】
│   ├─ 安全性：恶意节点 < n/3
│   ├─ 活性：部分同步假设
│   └─ 乐观响应：正常时3δ延迟
│
└─【应用】
    ├─ DiemBFT（原Libra）
    ├─ Celo
    └─ Flow区块链
```

---

## 二、HotStuff三阶段协议

> **权威来源**：Yin et al., "HotStuff: BFT Consensus in the Lens of Blockchain", 2018

```
HotStuff三阶段（简化版）：

  Phase 1: PREPARE
    Leader提出区块B，附带QC（Quorum Certificate）
    Leader → All: <<PREPARE, B, QC_high>, σ_L>

    Replica验证：
      - B的父块有有效QC
      - QC_high是已知最高QC

    Replica → Leader: PREPARE-VOTE(B), σ_i

  Phase 2: PRE-COMMIT
    Leader收集2f+1个PREPARE-VOTE
    聚合成QC_prepare（阈值签名）

    Leader → All: <<PRE-COMMIT, QC_prepare>, σ_L>

    Replica → Leader: PRE-COMMIT-VOTE, σ_i

  Phase 3: COMMIT
    Leader收集2f+1个PRE-COMMIT-VOTE
    聚合成QC_precommit

    Leader → All: <<COMMIT, QC_precommit>, σ_L>

    Replica → Leader: COMMIT-VOTE, σ_i

  DECIDE:
    Leader收集2f+1个COMMIT-VOTE
    聚合成QC_commit

    Leader → All: <<DECIDE, QC_commit>, σ_L>

    Replica收到DECIDE：
      - 区块B被提交
      - QC_commit可作为安全性的密码学证明

关键创新：阈值签名
  - 每个投票是一个签名份额
  - 2f+1个份额可聚合成单一签名
  - 验证聚合签名 = O(1)（与节点数无关）
```

---

## 三、HotStuff vs PBFT 对比

| 维度 | **PBFT** | **HotStuff** |
|------|---------|-------------|
| **消息复杂度** | O(n²)（每阶段全广播） | O(n)（Leader广播） |
| **视图变更** | 复杂（需证明状态） | 简化（QC作为证明） |
| **密码学** | 数字签名（O(n)验证） | 阈值签名（O(1)验证） |
| **延迟（正常）** | 5δ（三阶段+回复） | 3δ（可流水线化） |
| **实现难度** | 中 | 中高（需阈值签名库） |
| **代表系统** | Tendermint, BFT-SMaRt | DiemBFT, Celo, Flow |

---

## 四、链式HotStuff（Chained HotStuff）

```
流水线优化：

  传统HotStuff：
    区块1: Prepare → PreCommit → Commit → Decide（完成）
    区块2: Prepare → PreCommit → Commit → Decide（完成）
    → 串行执行，吞吐量受限

  Chained HotStuff：
    时间t:  Prepare(区块1)
    时间t+1: PreCommit(区块1) + Prepare(区块2)
    时间t+2: Commit(区块1) + PreCommit(区块2) + Prepare(区块3)
    时间t+3: Decide(区块1) + Commit(区块2) + PreCommit(区块3) + Prepare(区块4)

    → 每个时间步同时推进4个阶段
    → 流水线化，提高吞吐量

安全保证：
  - 3-chain提交规则：
    区块B在以下情况下被提交：
      B有QC_prepare，且
      B的直接子块有QC_precommit，且
      B的孙子块有QC_commit
```

---

## 五、概念定义与属性关系

| 概念 | 定义 | 属性 | 示例 | 反例 |
|------|------|------|------|------|
| **HotStuff** | 线性复杂度BFT共识算法 | O(n)消息、阈值签名、链式优化 | DiemBFT | PBFT（O(n²)） |
| **阈值签名** | 多方签名份额可聚合成单一签名 | O(1)验证、降低通信复杂度 | BLS签名 | 传统数字签名 |
| **Quorum Certificate** | 证明多数节点投票的密码学证据 | 可传递、可验证 | QC_prepare | 普通投票集合 |
| **3-chain规则** | 链式HotStuff的提交条件 | 流水线安全、延迟-吞吐权衡 | 3个连续QC | 单QC提交（不安全） |
| **视图变更** | Leader故障时的换主机制 | HotStuff中简化（QC证明状态） | Pacemaker | PBFT复杂View Change |

---

## 六、交叉引用

- → [03-总览](./00-总览-共识问题与算法家族树.md)
- → [03/01-Paxos](01-Paxos与MultiPaxos-经典问题与现代工程演进.md)
- → [03/03-PBFT](03-PBFT与BFT家族-拜占庭容错共识.md)
- → [03/05-Bullshark](05-Bullshark-DAG共识与异步优势.md)
- ↓ [09/01-BAN逻辑](../09-安全模型与可信计算/01-BAN逻辑-安全协议的形式化分析.md)

---

## 七、参考文献

| 作者 | 标题 | 出处 | 年份 |
|------|------|------|------|
| Yin et al. | "HotStuff: BFT Consensus in the Lens of Blockchain" | *arXiv* | 2018 |
| Diem团队 | DiemBFT技术文档 | developers.diem.com | 持续更新 |
| Boneh et al. | BLS阈值签名论文 | 密码学会议 | 2003 |
| Castro, Liskov | PBFT原始论文 | *OSDI* | 1999 |

---

*文件创建日期：2026-04-23*
*状态：已完成*
