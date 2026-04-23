# 分布式事务：2PC、Saga 与 TCC

> **来源映射**: View/02.md §2.5, Struct/22-数据存储与数据库架构/00-总览-数据库系统的形式化分层.md
> **国际权威参考**: "Atomic Transactions" (Nancy Lynch et al., Morgan Kaufmann, 1993); "Sagas" (Hector Garcia-Molina & Kenneth Salem, ACM SIGMOD, 1987); "Life beyond Distributed Transactions: An Apostate's Opinion" (Pat Helland, CIDR 2007)

---

## 一、知识体系思维导图

```text
分布式事务协议谱系
│
├─► 两阶段提交 (2PC - Two-Phase Commit)
│   ├─ 角色: 协调者 (Coordinator) + 参与者 (Participants)
│   ├─ Phase 1 (Prepare)
│   │   └─ 协调者询问所有参与者是否可以提交
│   ├─ Phase 2 (Commit/Abort)
│   │   └─ 若全部 Yes → Commit; 若有 No → Abort
│   ├─ 阻塞问题: 协调者崩溃后参与者需阻塞等待
│   ├─ 三阶段提交 (3PC): 增加预提交阶段，超时解阻塞
│   └─ 代表: XA 协议 (JTA/JTS), PostgreSQL/MQ 分布式事务
│
├─► Saga 模式
│   ├─ 核心思想: 长事务拆分为本地事务序列
│   ├─ 补偿机制: 每个正向操作对应逆向补偿操作
│   ├─ 编排方式
│   │   ├─ 编排式 Saga (Choreography): 事件驱动，服务自治
│   │   └─ 协调式 Saga (Orchestration): 中央协调器编排流程
│   └─ 语义: 最终一致，无全局隔离性
│
└─► TCC (Try-Confirm-Cancel)
    ├─ 核心思想: 业务层面的两阶段提交
    ├─ Try: 资源预留与校验 (非业务执行)
    ├─ Confirm: 确认执行业务 (Try 成功后的幂等确认)
    ├─ Cancel: 取消预留，释放资源
    └─ 特点: 业务侵入性强，但无全局锁，性能优于 2PC
```

---

## 二、核心概念的形式化定义

### 2.1 2PC 的形式化

```text
定义 (2PC 协议):
  参与者集合 P = {p₁, p₂, ..., pₙ}
  协调者 C

  Phase 1 (Prepare):
    C → ∀pᵢ: PREPARE(T)
    ∀pᵢ: 若可提交 → 写 Prepare 记录到本地日志 → reply YES
         若不可提交 → reply NO

  Phase 2 (Commit/Abort):
    if ∀reply = YES:
      C → ∀pᵢ: COMMIT(T)
      ∀pᵢ: 提交本地事务 → 释放锁 → reply ACK
    else:
      C → ∀pᵢ: ABORT(T)
      ∀pᵢ: 回滚本地事务 → 释放锁 → reply ACK

  阻塞条件:
    若 C 在 Phase 2 崩溃，且某 pᵢ 已回复 YES 但未收到 COMMIT/ABORT:
      pᵢ 必须阻塞等待 C 恢复 (持有锁)
```

### 2.2 Saga 的形式化

```text
定义 (Saga):
  Saga = [T₁, T₂, ..., Tₙ] 其中 Tᵢ 是本地事务
  每个 Tᵢ 对应补偿事务 Cᵢ，满足: Cᵢ(Tᵢ(state)) = state

  执行语义:
    正常: T₁ → T₂ → ... → Tₙ → 完成
    失败 (Tₖ 失败): T₁ → ... → Tₖ → Cₖ₋₁ → ... → C₁ → 补偿完成

  补偿顺序:
    逆序执行补偿: Cₖ₋₁ 在 Cₖ 之前执行 (k 递减)

  隔离性缺失:
    Saga 执行期间，其他事务可能观察到中间状态
    语义异常: 脏读 (其他事务读到未完成的 Saga 中间结果)
    缓解: 语义锁 (Semantic Lock) / 交换式更新 (Commutative Updates)
```

### 2.3 TCC 的形式化

```text
定义 (TCC 事务):
  对于业务操作 op，定义三元组:
    Try(op): 预留资源，校验条件，不执行业务
    Confirm(op): 在 Try 成功基础上，幂等执行业务
    Cancel(op): 释放 Try 预留的资源

  状态机:
    Init → TrySuccess → ConfirmSuccess
                  ↘ CancelSuccess
    Init → TryFail → (无需补偿)

  约束:
    (1) Try + Confirm = 原子业务执行
    (2) Try + Cancel = 空操作 (无业务效果)
    (3) Confirm 和 Cancel 必须幂等
    (4) Confirm 必须最终成功 (无限重试直至成功)
```

---

## 三、多维矩阵对比

| 维度 | 2PC/XA | 3PC | Saga | TCC |
|------|--------|-----|------|-----|
| **一致性** | 强一致 | 强一致 | 最终一致 | 最终一致 |
| **阻塞性** | **阻塞** (协调者故障) | 非阻塞 (超时继续) | 非阻塞 | 非阻塞 |
| **隔离性** | 全局隔离 | 全局隔离 | **无隔离** | **无全局隔离** |
| **性能** | 低 (两次 RTT + 锁持有) | 中 (三次 RTT) | **高** | **高** |
| **实现复杂度** | 低 (协议标准化) | 中 | 高 (补偿逻辑) | **很高** (三接口) |
| **业务侵入性** | 低 | 低 | 中 | **高** |
| **回滚能力** | 自动 | 自动 | 补偿逻辑 | 预留释放 |
| **适用场景** | 短事务、同构资源 | 网络分区敏感 | 长事务、跨服务 | 高并发资源预留 |

---

## 四、权威引用

> **Hector Garcia-Molina & Kenneth Salem** ("Sagas", ACM SIGMOD 1987):
> "A saga is a sequence of local transactions. Each local transaction updates the database and communicates with the outside world. If a local transaction fails, the saga executes compensating transactions to undo the impact of the preceding local transactions."

> **Pat Helland** ("Life beyond Distributed Transactions: An Apostate's Opinion", CIDR 2007):
> "In a system that cannot count on distributed transactions, the management of uncertainty must be implemented in the business logic. The work is moved from the platform into the app."

> **Nancy Lynch et al.** ("Atomic Transactions", Morgan Kaufmann, 1993):
> "The Two-Phase Commit protocol is the standard method for ensuring atomic commitment in distributed systems. Its blocking nature is a fundamental consequence of the impossibility of consensus in asynchronous systems with even one faulty process (FLP result)."

---

## 五、工程实践与代码示例

### Saga 编排式实现 (伪代码)

```java
// 协调器定义 Saga 流程
public class OrderSaga {
    private SagaOrchestrator orchestrator;

    public void createOrder(OrderRequest req) {
        orchestrator.start()
            .step("deductInventory",
                  () -> inventoryService.deduct(req.getItems()),
                  () -> inventoryService.rollbackDeduct(req.getItems()))
            .step("deductBalance",
                  () -> paymentService.charge(req.getUserId(), req.getAmount()),
                  () -> paymentService.refund(req.getUserId(), req.getAmount()))
            .step("createShipment",
                  () -> shippingService.create(req.getAddress(), req.getItems()),
                  () -> shippingService.cancelShipment(req.getOrderId()))
            .execute();
    }
}

// 补偿必须幂等且最终成功
@Idempotent
public void rollbackDeduct(List<Item> items) {
    // 1. 查询是否有扣减记录
    // 2. 若有，执行回滚
    // 3. 幂等: 重复调用结果相同
}
```

---

## 六、批判性总结

分布式事务协议的选择本质上是在**一致性、可用性和工程复杂度**之间的权衡。2PC 是理论上最优雅的方案，但其阻塞特性与微服务架构的高可用要求根本冲突——协调者单点故障可能导致参与者无限期持有锁，这在云原生环境中不可接受。3PC 试图通过超时机制解决阻塞问题，但增加的通信轮次和极端场景下的不一致性使其从未获得广泛采用。Saga 和 TCC 代表了"放弃全局一致性，拥抱最终一致"的工程务实路线，但它们将分布式事务的复杂性**从基础设施转移到了应用代码**——补偿逻辑的正确性需要业务开发者自行保证，而这在复杂业务流程中极易出错（如补偿顺序错误、补偿遗漏、补偿与正向操作的竞态条件）。Pat Helland 的论断至今仍然成立：当平台无法提供分布式事务时，不确定性管理必须嵌入业务逻辑。**没有完美的分布式事务协议，只有对业务容忍度的精确匹配**——金融核心系统可能仍需要 2PC 的强保证，而电商订单则完全可以用 Saga 的最终一致性换取系统的可用性和弹性。


---

## 七、概念属性关系网络

### 7.1 核心概念依赖/包含/对立关系表

| 概念A | 关系类型 | 概念B | 关系说明 |
|-------|---------|-------|---------|
| 2PC | ⊃ (包含) | Coordinator | 两阶段提交包含协调者角色 |
| 2PC | ⊃ (包含) | Participant | 两阶段提交包含参与者角色 |
| 2PC | → (依赖) | Prepare Phase | 2PC依赖准备阶段收集投票 |
| 2PC | → (依赖) | Commit Phase | 2PC依赖提交阶段执行决议 |
| 2PC | ⊥ (阻塞) | Availability | 2PC的阻塞特性与可用性对立 |
| 3PC | → (改进) | 2PC | 三阶段提交是2PC的阻塞改进方案 |
| Saga | → (替代) | 2PC | Saga是2CP的长事务替代方案 |
| Saga | ⊃ (包含) | Compensation | Saga包含补偿事务机制 |
| TCC | → (替代) | 2PC | TCC是业务层2PC替代方案 |
| TCC | ⊃ (包含) | Try-Confirm-Cancel | TCC包含三阶段业务操作 |
| Orchestration | ⊥ (对立) | Choreography | Saga的两种编排方式对立 |

### 7.2 ASCII拓扑图

```text
分布式事务协议概念拓扑
│
├─► 两阶段提交 (2PC)
│   ├─► 角色
│   │   ├─► Coordinator (协调者): 发起事务，收集投票，执行决议
│   │   └─► Participants (参与者): 执行本地事务，投票Yes/No
│   │
│   ├─► Phase 1 (Prepare)
│   │   ├─► C → ∀p: PREPARE(T)
│   │   ├─► p: 若可提交 → 写Prepare记录到本地日志 → reply YES
│   │   └─► p: 若不可提交 → reply NO
│   │
│   ├─► Phase 2 (Commit/Abort)
│   │   ├─► 若 ∀reply = YES → C → ∀p: COMMIT(T)
│   │   └─► 若 ∃reply = NO → C → ∀p: ABORT(T)
│   │
│   └─► 阻塞问题
│       ├─► C在Phase 2崩溃，且p已回复YES但未收到COMMIT/ABORT
│       └─► p必须阻塞等待C恢复（持有锁）
│
├─► 三阶段提交 (3PC)
│   ├─► Phase 1: CanCommit? (预准备)
│   ├─► Phase 2: PreCommit (预提交)
│   ├─► Phase 3: DoCommit (正式提交)
│   └─► 改进: 超时解阻塞，但增加通信轮次
│       └─► 极端场景下仍可能不一致
│
├─► Saga模式
│   ├─► 核心: 长事务拆分为本地事务序列
│   ├─► 补偿机制
│   │   ├─► 每个正向操作 Tᵢ 对应补偿操作 Cᵢ
│   │   └─► Cᵢ(Tᵢ(state)) = state (恢复原状)
│   │
│   ├─► 编排方式
│   │   ├─► Choreography (编排式): 事件驱动，服务自治
│   │   │   └─► 服务间通过事件总线协调
│   │   └─► Orchestration (协调式): 中央协调器编排流程
│   │       └─► 协调器定义Saga步骤与补偿链
│   │
│   └─► 语义: 最终一致，无全局隔离性
│       └─►  Saga执行期间，其他事务可能观察到中间状态
│
└─► TCC (Try-Confirm-Cancel)
    ├─► Try: 资源预留与校验（非业务执行）
    ├─► Confirm: 在Try成功基础上，幂等执行业务
    ├─► Cancel: 释放Try预留的资源
    │
    ├─► 状态机
    │   ├─► Init → TrySuccess → ConfirmSuccess
    │   │                  ↘ CancelSuccess
    │   └─► Init → TryFail → (无需补偿)
    │
    └─► 约束
        ├─► Try + Confirm = 原子业务执行
        ├─► Try + Cancel = 空操作
        ├─► Confirm和Cancel必须幂等
        └─► Confirm必须最终成功（无限重试直至成功）
```

### 7.3 形式化映射

```text
概念映射:

f₁: Coordinator × Participants → 2PC
     via  phase1_prepare(votes) → phase2_commit(all_yes) / abort(any_no)

f₂: Coordinator_failure × Prepared_Participant → Blocking
     via  participant_holds_locks ∧ waits_for_coordinator_recovery

f₃: Saga → [LocalTransaction]      via  saga = [T₁, T₂, ..., Tₙ]
f₄: LocalTransaction → Compensation
     via  ∀Tᵢ: ∃Cᵢ: Cᵢ ∘ Tᵢ = identity

f₅: Saga_failure → CompensationChain
     via  T₁→...→Tₖ失败 → Cₖ₋₁→...→C₁逆序补偿

f₆: TCC → Business2PC              via  try(reserve) → confirm(commit) / cancel(release)
f₇: TCC_try → ResourceReservation   via  validate ∧ reserve_resources
f₈: TCC_confirm → IdempotentCommit  via  ensure(try_success) → execute_business
```

---

## 八、形式化推理链

### 8.1 公理体系

**公理 1 (2PC原子性公理)** — Nancy Lynch et al., 1993
> 2PC保证所有参与者最终执行相同决议（全部提交或全部中止）。
> ∀pᵢ, pⱼ ∈ Participants: decision(pᵢ) = decision(pⱼ) ∈ {Commit, Abort}

**公理 2 (2PC阻塞公理)** — FLP不可能性结果
> 在异步网络中，若协调者故障，已回复YES的参与者可能无限阻塞。
> Coordinator_fails ∧ participant_prepared ⟹ possible_indefinite_blocking

**公理 3 (Saga补偿公理)** — Garcia-Molina & Salem, 1987
> Saga的补偿操作必须满足语义逆运算：补偿后系统状态等价于事务未发生。
> Cᵢ(Tᵢ(state)) ≡ state

### 8.2 引理

**引理 1 (2PC的通信复杂度)**
> 2PC需要2N条消息（N个参与者），3PC需要3N条消息。
> 通信轮次 ↑ ⟹ 延迟 ↑ ∧ 故障窗口 ↑

**引理 2 (Saga的隔离性缺失)**
> Saga执行期间，其他事务可能观察到中间状态（脏读）。
> 缓解: 语义锁（Semantic Lock）/ 交换式更新（Commutative Updates）

### 8.3 定理

**定理 1 (2PC阻塞的不可解性)** — Fischer, Lynch & Paterson, 1985
> 在异步分布式系统中，不存在确定性的共识算法能在即使一个进程故障时保证终止。
>
> 对2PC的影响:
> 若网络异步 ∧ Coordinator可能故障 ⟹ 2PC的阻塞问题是固有的，不可通过协议改进完全消除。
> 3PC通过同步假设（超时）缓解阻塞，但牺牲了部分故障安全性。

**定理 2 (Saga最终一致性的收敛)**
> 若所有补偿操作最终成功执行，则Saga最终达到一致状态。
>
> 条件:
> (1) ∀Cᵢ: Cᵢ是确定性的
> (2) ∀Cᵢ: Cᵢ最终成功执行（无限重试直至成功）
> (3) 补偿按逆序执行: Cₖ₋₁在Cₖ之前
> (4) (1) ∧ (2) ∧ (3) ⟹ Saga最终一致

### 8.4 推论

**推论 1 (3PC的有限采用)**
> 3PC虽通过超时机制缓解了2PC的阻塞问题，但增加的通信轮次和极端场景下的不一致性使其未获广泛采用。
> 工业界更倾向于Saga/TCC的异步最终一致方案。

**推论 2 (TCC的业务侵入性)**
> TCC要求业务系统实现三接口（Try/Confirm/Cancel），侵入性强。
> 但TCC将分布式事务的复杂性从基础设施显式暴露给业务层，便于调试和优化。

---

## 九、ASCII推理判定树 / 决策树

### 9.1 分布式事务协议选择决策树

```text
分布式事务协议选择
│
├─► 事务持续时间是否短（<1秒）？
│   ├─ 是 ──► 参与者是否同构（同一数据库类型）？
│   │           ├─ 是 ──► 2PC/XA
│   │           │           └─ 强一致，标准化协议
│   │           │           └─ ⚠ 协调者单点故障风险
│   │           │
│   │           └─ 否（异构资源）──► 评估3PC或TCC
│   │               └─ 3PC: 超时解阻塞，但复杂度高
│   │               └─ TCC: 业务层实现，灵活性高
│   │
│   └─ 否（长事务，>1秒）──► Saga模式
│               ├─► 是否需要中央协调？
│               │   ├─ 是 ──► Orchestration Saga
│               │   │           └─ 中央协调器定义流程
│               │   │           └─ 适合复杂业务流程
│               │   │
│               │   └─ 否（服务自治）──► Choreography Saga
│               │                   └─ 事件驱动，服务间松耦合
│               │                   └─ 适合简单线性流程
│               │
│               └─► 补偿逻辑复杂度如何？
│                   ├─ 简单（直接回滚）──► Saga直接适用
│                   └─ 复杂（涉及外部系统）──► 评估补偿的可达性
│                               └─ 不可补偿操作 ⟹ 不能用Saga
```

### 9.2 分布式事务故障处理决策树

```text
分布式事务故障处理
│
├─► 2PC协调者故障
│   ├─► 是否有事务日志？
│   │   ├─ 是 ──► 从日志恢复协调者状态
│   │   │           ├─ 已决定Commit/Abort → 重发决议
│   │   │           └─ 未决定 → 参与者阻塞直至协调者恢复
│   │   │
│   │   └─ 否（无日志）──► 参与者超时后自主决策
│   │                       └─ 启发式策略（可能不一致！）
│   │
│   └─► 预防措施
│       ├─ 协调者主备复制
│       └─ 事务状态持久化到高可用存储
│
├─► Saga补偿失败
│   ├─► 补偿操作是否幂等？
│   │   ├─ 是 ──► 无限重试直至成功
│   │   └─ 否 ──► 需要人工介入或死信队列
│   │
│   └─► 预防措施
│       ├─ 补偿操作必须幂等设计
│       └─ 监控补偿执行状态，超时告警
│
└─► TCC Confirm/Cancel失败
    ├─► 是否设置最终成功机制？
    │   ├─ 是 ──► 定时任务扫描未完成Confirm/Cancel，自动重试
    │   └─ 否 ──► 资源永久悬挂，需人工清理
    │
    └─► 预防措施
        ├─ Confirm/Cancel操作必须幂等
        └─ 悬挂资源监控与自动回收机制
```

---

## 十、国际权威课程对齐

### 10.1 MIT 6.824: Distributed Systems

| 课程内容 | 对应 Lecture | 对应本文件内容 | 映射深度 |
|---------|-------------|---------------|---------|
| Distributed Transactions | LEC 11: Distributed Transactions | 2PC、事务原子性 | 核心映射 |
| FLP不可能性 | LEC 4-5 | 2PC阻塞的理论根源 | 理论映射 |
| Spanner | LEC 12/13 | 分布式事务的外部一致性 | 扩展映射 |

**对应 Lab:**

- Lab 4: Sharded KV — 理解跨分片原子操作的实现挑战

### 10.2 Stanford CS 245: Database System Principles

| 课程内容 | 对应模块 | 对应本文件内容 |
|---------|---------|---------------|
| Distributed Transactions | Lecture 9-10 | 2PC与3PC协议分析 |
| Long-Running Transactions | Lecture 11-12 | Saga与补偿模式 |
| Recovery | Lecture 13-14 | 事务故障恢复机制 |

### 10.3 CMU 15-445: Database Systems

| 课程内容 | 对应 Lecture | 对应本文件内容 |
|---------|-------------|---------------|
| Distributed Database Systems | Lecture 23-24 | 分布式事务与2PC |
| Concurrency Control | Lecture 17-20 | 锁协议与隔离级别 |

### 10.4 Berkeley CS 186: Database Systems

| 课程内容 | 对应模块 | 对应本文件内容 |
|---------|---------|---------------|
| Distributed Transactions | Lecture 20-21 | 2PC与分布式一致性 |
| Recovery | Lecture 23-25 | 事务故障恢复与WAL |

### 10.5 核心参考文献

1. **Hector Garcia-Molina & Kenneth Salem** (1987). "Sagas." *ACM SIGMOD Record*, 16(3), 249-259. —— Saga模式的原始论文，首次提出了长事务拆分为本地事务序列及补偿机制的概念。

2. **Pat Helland** (2007). "Life beyond Distributed Transactions: An Apostate's Opinion." *CIDR 2007*. —— 分布式事务局限性的经典论述，明确提出在大型分布式系统中应放弃全局事务，将不确定性管理嵌入业务逻辑。

3. **Nancy Lynch et al.** (1993). *Atomic Transactions*. Morgan Kaufmann. —— 分布式事务协议的标准教材，系统分析了2PC、3PC的理论性质和局限性。

4. **Michael J. Fischer, Nancy A. Lynch & Michael S. Paterson** (1985). "Impossibility of Distributed Consensus with One Faulty Process." *Journal of the ACM*, 32(2), 374-382. —— FLP不可能性结果，证明了异步系统中确定性共识的不可能性，是2PC阻塞问题的理论根源。

---

## 十一、批判性总结

分布式事务协议的选择本质上是在一致性、可用性和工程复杂度之间的权衡。2PC是理论上最优雅的方案，但其阻塞特性与微服务架构的高可用要求根本冲突——协调者单点故障可能导致参与者无限期持有锁，这在云原生环境中不可接受。3PC试图通过超时机制解决阻塞问题，但增加的通信轮次和极端场景下的不一致性使其从未获得广泛采用。Saga和TCC代表了"放弃全局一致性，拥抱最终一致"的工程务实路线，但它们将分布式事务的复杂性从基础设施转移到了应用代码——补偿逻辑的正确性需要业务开发者自行保证，而这在复杂业务流程中极易出错。补偿顺序错误、补偿遗漏、补偿与正向操作的竞态条件是生产环境中的经典故障模式。Pat Helland的论断至今仍然成立：当平台无法提供分布式事务时，不确定性管理必须嵌入业务逻辑。没有完美的分布式事务协议，只有对业务容忍度的精确匹配——金融核心系统可能仍需要2PC的强保证，而电商订单则完全可以用Saga的最终一致性换取系统的可用性和弹性。一个被忽视的趋势是，现代系统架构正在从"协议中心主义"转向"业务语义中心主义"：不再试图用通用协议解决所有分布式一致性问题，而是根据具体业务场景设计专用的一致性模型——库存扣减使用预扣+异步确认，支付使用状态机+幂等设计，物流配送使用事件溯源+补偿。这种"场景化一致性"虽然增加了设计的多样性，却降低了系统的整体复杂度，因为它承认了不同业务领域对一致性的需求本质上是异构的。
