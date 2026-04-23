# 事件溯源与 CQRS：命令查询职责分离

> **来源映射**: View/01.md §3.1.5, Struct/21-消息队列与事件流架构/00-总览-消息队列的形式化谱系.md
> **国际权威参考**: Martin Fowler, "Event Sourcing" (2015); Greg Young, CQRS Documents (2010); "Exploring CQRS and Event Sourcing" (Microsoft Patterns & Practices)

---

## 一、知识体系思维导图

```text
事件溯源与 CQRS
│
├─► 事件溯源 (Event Sourcing)
│   ├─ 核心思想: 状态不是存储的，而是被计算的
│   │   └─ State(t) = foldl(apply, State₀, Events[0..t])
│   ├─ 事件存储 (Event Store)
│   │   ├─ 仅追加 (Append-Only) 的不可变日志
│   │   ├─ 全局顺序或流内顺序保证
│   │   └─ 代表: EventStoreDB, Axon, PostgreSQL + 表
│   ├─ 版本链与 Upcasting
│   │   ├─ 事件模式演化: v1 → v2 → v3
│   │   ├─ Upcaster: Event_v1 → Event_v2 (读取时转换)
│   │   └─ 诅咒: 版本链无限增长，历史债务累积
│   └─ 时间旅行 (Temporal Query)
│       └─ 重放事件到任意时间点 t 获取历史状态
│
├─► CQRS (Command Query Responsibility Segregation)
│   ├─ 核心思想: 写模型 ≠ 读模型
│   ├─ 命令侧 (Command Side)
│   │   ├─ 接收命令，验证业务规则
│   │   ├─ 生成事件并写入 Event Store
│   │   └─ 领域模型 (Aggregate Root) 仅存在于写路径
│   └─ 查询侧 (Query Side)
│       ├─ 投影 (Projection): 事件 → 物化视图
│       ├─ 最终一致性 (Eventual Consistency)
│       └─ 读模型可针对查询优化 (反规范化)
│
└─► Event Sourcing + CQRS 集成
    ├─ 写路径: Command → Aggregate → Event → Event Store
    ├─ 投影器 (Projector): 订阅 Event Stream → 更新 Read Model
    └─ 快照 (Snapshot): 避免从第 0 个事件开始全量重放
```

---

## 二、核心概念的形式化定义

### 2.1 事件溯源的形式化

```text
定义 (事件溯源系统 ES):
  ES = ⟨E, S, apply, State₀⟩

  E: 领域事件集合, e ∈ E = ⟨event_id, event_type, payload, timestamp, aggregate_id, version⟩
  S: 状态空间
  apply: S × E → S   (状态转移函数)

  当前状态计算:
    State(t) = foldl(apply, State₀, [e₁, e₂, ..., eₙ])
    其中 [e₁..eₙ] 是 aggregate_id 对应的全部有序事件

  不可变约束:
    ∀e ∈ E: e 一旦写入不可修改
    修正只能通过写入补偿事件: e_compensate = ⟨..., "Correction", delta, ...⟩
```

### 2.2 CQRS 的形式化

```text
定义 (CQRS 系统):
  传统 CRUD:  ⟨Command, Query⟩ → 同一模型 M → 同一存储

  CQRS 分离:
    Command Side: C → M_write → Event Store
    Query Side:   Q → M_read ← Projection(Event Store)

  一致性模型:
    写侧: 强一致 (Aggregate 验证保证不变式)
    读侧: 最终一致 (Projection 滞后于 Event Store)

  延迟边界:
    ∀q ∈ Query: |time(write(e)) - time(read_projection(e))| ≤ δ
```

### 2.3 投影的形式化

```text
定义 (投影函数 Projection):
  Projection: [E] → View

  典型投影类型:
    (1) 单 Aggregate 投影: View = apply_all(State₀, events_for_aggregate)
    (2) 跨 Aggregate 投影: View = join(project(a₁), project(a₂), ...)
    (3) 时序投影: View(t) = foldl(apply, State₀, events_before(t))

  投影一致性条件:
    若 Event Store 保证分区顺序，则 Projection 按顺序应用事件
    最终: lim(t→∞) View(t) = Projection(all_events)
```

---

## 三、多维矩阵对比

| 维度 | 传统 CRUD | Event Sourcing | CQRS | ES + CQRS |
|------|----------|---------------|------|----------|
| **数据模型** | 当前状态 | 事件历史 | 分离读写 | 事件历史 + 分离读写 |
| **存储结构** | 行/文档更新 | 仅追加日志 | 双存储 | Event Store + Read DB |
| **可审计性** | 弱 (仅当前值) | **强** (完整历史) | 中 | **最强** |
| **调试能力** | 弱 | **强** (可重放) | 中 | **最强** |
| **模式演化** | 简单 (DDL) | **复杂** (Upcasting) | 中 | **复杂** |
| **一致性** | 强一致 | 强一致 (单流) | 最终一致 | 写强/读最终 |
| **复杂度** | 低 | 高 | 高 | **很高** |
| **团队要求** | 通用技能 | 领域建模深度 | 架构理解 | **资深团队** |

---

## 四、权威引用

> **Martin Fowler** ("Event Sourcing", martinfowler.com, 2015):
> "The fundamental idea of Event Sourcing is that we should ensure that every change to the state of an application is captured in an event object, and that these event objects are themselves stored in the sequence they were applied for the same lifetime as the application state itself."

> **Greg Young** (CQRS Documents, 2010):
> "CQRS is simply the creation of two objects where there was previously only one. The separation occurs based upon whether the methods are a command or a query."

> **Pat Helland** (Microsoft, "Immutability Changes Everything", CIDR 2015):
> "Computation around immutable data is fundamentally easier than around mutable data. Event sourcing embraces this by making the event log the single source of truth."

---

## 五、工程实践与代码示例

### 事件溯源 Aggregate (简化示例)

```java
public class BankAccount {
    private String accountId;
    private long balance;
    private List<DomainEvent> uncommittedEvents = new ArrayList<>();

    // 命令处理
    public void withdraw(long amount) {
        if (balance < amount) {
            throw new InsufficientFundsException();
        }
        apply(new MoneyWithdrawn(accountId, amount, Instant.now()));
    }

    // 状态应用 (纯函数)
    public void apply(DomainEvent event) {
        if (event instanceof MoneyDeposited) {
            balance += ((MoneyDeposited) event).getAmount();
        } else if (event instanceof MoneyWithdrawn) {
            balance -= ((MoneyWithdrawn) event).getAmount();
        }
        uncommittedEvents.add(event);
    }

    // 从事件流重建
    public static BankAccount reconstitute(String id, List<DomainEvent> history) {
        BankAccount account = new BankAccount(id);
        history.forEach(account::apply);
        return account;
    }
}
```

---

## 六、批判性总结

Event Sourcing 与 CQRS 的组合是领域驱动设计（DDD）中最强大但也最危险的架构模式。它将系统从"状态机"转变为"事件驱动的状态还原机"，带来了无与伦比的可审计性和调试能力——你可以精确重放任意时间点的系统状态，这在金融、医疗等监管严格的领域具有不可替代的价值。然而，**Event Sourcing 的"版本诅咒"是真实且严重的**：随着系统演进，事件模式可能经历数十次变更，Upcasting 链会无限增长，读取性能线性下降。更危险的是，新手团队常被"完整历史"的美好愿景吸引，低估了模式演化、投影故障恢复、最终一致性调试的复杂性。CQRS 加剧了这一问题：读写分离意味着团队必须维护两套模型、两套存储、两套一致性语义，任何投影器的 Bug 都会导致读模型与写模型长期偏离。Greg Young 本人也多次警告：**"不要在没有明确业务需求的情况下使用 Event Sourcing"**——这是一个为特定问题域设计的专业工具，而非通用架构默认选项。
