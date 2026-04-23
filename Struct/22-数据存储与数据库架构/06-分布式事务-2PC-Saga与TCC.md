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
