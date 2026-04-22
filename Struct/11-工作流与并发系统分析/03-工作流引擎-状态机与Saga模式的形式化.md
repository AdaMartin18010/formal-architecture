# 工作流引擎：状态机与Saga模式的形式化

> **定位**：工作流引擎是分布式系统的"编排大脑"——它将 Saga 模式、状态机和补偿事务封装为可运行、可监控、可回滚的基础设施。Temporal、Camunda 等现代工作流引擎让复杂长事务的实现从"手写状态机"提升到"声明式编排"。
>
> **核心命题**：工作流引擎的本质是持久化状态机——每个工作流实例的状态被持久化，确保即使进程崩溃，工作流也能从断点恢复。

---

## 一、思维导图：工作流引擎核心概念

```text
工作流引擎
│
├─【核心抽象】
│   ├─ Workflow（工作流定义）
│   │   └─ 活动的DAG或状态机
│   ├─ Activity（活动）
│   │   └─ 原子业务操作（可补偿）
│   ├─ Execution（执行实例）
│   │   └─ 工作流的运行时状态
│   └─ Compensation（补偿）
│       └─ 活动的撤销操作
│
├─【执行模式】
│   ├─ 编排式（Orchestration）
│   │   └─ 中央协调器驱动流程
│   └─ 编舞式（Choreography）
│       └─ 事件驱动，各服务自主响应
│
├─【持久化保证】
│   ├─ 事件溯源：所有状态变更记录为事件
│   ├─ 快照：定期保存完整状态
│   └─ 重放：从事件流恢复状态
│
└─【代表系统】
    ├─ Temporal（原Cadence）：代码即工作流
    ├─ Camunda：BPMN引擎
    ├─ AWS Step Functions：云托管
    └─ Netflix Conductor：微服务编排
```

---

## 二、工作流作为持久化状态机

```
形式化定义：

  工作流 W = (S, s₀, A, T, C)

  S = 状态集合（工作流实例的可能状态）
  s₀ ∈ S = 初始状态
  A = 活动集合
  T ⊆ S × A × S = 状态转换（执行活动导致状态变化）
  C: A → A' = 补偿函数（每个活动有可补偿操作）

持久化保证：
  - 每个状态转换产生事件 e = (s, a, s')
  - 事件流 E = [e₁, e₂, ..., eₙ] 被持久化到事件存储
  - 崩溃恢复：重放 E 重建状态

Saga执行语义：
  正向执行：s₀ ─a₁→ s₁ ─a₂→ s₂ ─a₃→ s₃ (成功)

  失败回滚：s₀ ─a₁→ s₁ ─a₂→ s₂ (a₃失败)
              → 补偿：s₂ ─c₂→ s₁' ─c₁→ s₀'

  关键约束：补偿操作本身也可能失败
    → 工作流引擎需记录补偿状态，支持补偿的补偿
```

---

## 三、编排式 vs 编舞式对比

| 维度 | **编排式（Orchestration）** | **编舞式（Choreography）** |
|------|--------------------------|--------------------------|
| **控制流** | 中央协调器显式定义 | 分布式，事件隐式协调 |
| **可见性** | 高（单一工作流图） | 低（分散在各服务） |
| **耦合度** | 中（服务依赖协调器） | 低（仅依赖事件） |
| **复杂度** | 协调器复杂，服务简单 | 服务复杂，整体流程隐式 |
| **调试** | 易（集中日志） | 难（分布式追踪必需） |
| **代表系统** | Temporal, Camunda, Step Functions | 纯EDA, EventBridge |
| **适用场景** | 复杂流程、需强监控 | 简单流程、高松耦合需求 |

---

## 四、Temporal的工作流代码示例

```go
// Temporal Go SDK示例：订单处理Saga
func OrderWorkflow(ctx workflow.Context, orderID string) error {
    // Saga选项：补偿超时、重试策略
    saga := &Saga{}
    defer saga.Compensate()  // 失败时自动执行补偿

    // 1. 扣减库存
    inventoryResult := workflow.ExecuteActivity(
        ctx, activities.ReserveInventory, orderID,
    )
    saga.AddCompensation(activities.ReleaseInventory, orderID)

    // 2. 处理支付
    paymentResult := workflow.ExecuteActivity(
        ctx, activities.ProcessPayment, orderID,
    )
    saga.AddCompensation(activities.RefundPayment, orderID)

    // 3. 创建配送
    shipmentResult := workflow.ExecuteActivity(
        ctx, activities.CreateShipment, orderID,
    )
    saga.AddCompensation(activities.CancelShipment, orderID)

    // 等待所有结果
    var inventory, payment, shipment Result
    inventoryResult.Get(ctx, &inventory)
    paymentResult.Get(ctx, &payment)
    shipmentResult.Get(ctx, &shipment)

    // 4. 发送确认
    workflow.ExecuteActivity(ctx, activities.SendConfirmation, orderID)

    return nil
}

// Temporal的核心保证：
// - 工作流代码是确定性的（限制API使用）
// - 所有状态变更持久化到事件存储
// - Worker崩溃后可从断点恢复
// - 活动可配置重试、超时、心跳
```

---

## 五、概念定义与属性关系

| 概念 | 定义 | 属性 | 示例 | 反例 |
|------|------|------|------|------|
| **工作流引擎** | 持久化执行业务流程的运行时 | 可靠、可恢复、可监控 | Temporal, Camunda | 手写状态机（无持久化） |
| **Saga** | 长事务拆分为本地事务+补偿的模式 | 最终一致、无全局锁、补偿复杂 | 电商订单处理 | 2PC分布式事务 |
| **编排式** | 中央协调器驱动的工作流执行 | 可见性高、耦合中、调试易 | Temporal workflow | 纯事件驱动 |
| **编舞式** | 事件驱动、各参与者自主响应 | 松耦合、可见性低、调试难 | EDA + 事件订阅 | 集中式协调 |
| **补偿** | 撤销已完成活动的业务操作 | 非技术回滚、可能有副作用 | 释放库存、退款 | 数据库事务回滚 |
| **确定性执行** | 给定相同输入和历史，工作流产生相同输出 | 可重放、可恢复 | Temporal workflow函数 | 使用随机数/时间的函数 |

---

## 六、交叉引用

- → [11-总览](./00-总览-Petri网与工作流引擎.md)
- → [11/01-Petri网](01-Petri网-并发系统的形式化建模.md)
- → [05/03-EDA](../05-架构模式与部署单元光谱/03-事件驱动架构-解耦与一致性的设计哲学.md)
- → [04/04-EventSourcing](../../04-数据一致性代数结构/04-EventSourcing-事件溯源与左折叠代数.md)
- ↓ [12/01-电商场景](../12-场景应用与决策框架/01-电商场景-从初创到全球化的架构演进.md)

---

## 七、参考文献

| 作者 | 标题 | 出处 | 年份 |
|------|------|------|------|
| Hector Garcia-Molina, Kenneth Salem | "Sagas" | *ACM SIGMOD* | 1987 |
| Temporal团队 | Temporal文档与架构 | temporal.io | 持续更新 |
| Camunda团队 | Camunda BPMN引擎文档 | camunda.com | 持续更新 |
| Netflix | Conductor文档 | github.com/Netflix/conductor | 持续更新 |

---

*文件创建日期：2026-04-23*
*状态：已完成*
