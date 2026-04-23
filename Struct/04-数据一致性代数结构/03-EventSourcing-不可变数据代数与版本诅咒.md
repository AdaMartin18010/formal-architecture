# Event Sourcing：不可变数据代数与版本诅咒

> **来源映射**: Struct/04-数据一致性代数结构/03-EventSourcing-不可变数据代数与版本诅咒.md
>
> **定位**：本文件分析Event Sourcing的代数美感与工程诅咒。将状态定义为事件日志的折叠（fold）是函数式编程的优雅表达，但在长生命周期系统中，版本链永存和Upcasting线性增重构成了严峻的维护挑战。
>
> **核心命题**：Event Sourcing的不可变性与CRDT的收敛性存在深层张力——CRDT允许状态合并（重写历史视角），而Event Sourcing禁止任何历史重写。在>5年长生命周期系统中，维护成本呈超线性增长。

---

## 一、思维导图：Event Sourcing的代数结构

```text
Event Sourcing：不可变数据代数
│
├─【核心代数】
│   ├─ State = foldl(apply, initState, events)
│   ├─ 事件是事实（Fact）：不可变、追加-only
│   ├─ 状态是投影（Projection）：纯函数，无副作用
│   ├─ 时间旅行：重放至任意时间点，状态可重现
│   └─ 左折叠（Left Fold）的代数结构
│
├─【形式化美感】
│   ├─ 不可变性 → 天然审计追踪
│   ├─ 追加-only → 高写入吞吐量（顺序IO）
│   ├─ 纯函数投影 → 并行计算、缓存友好
│   ├─ 事件驱动 → 系统间解耦（发布-订阅）
│   └─ CQRS天然伴侣 → 读写分离
│
├─【形式化诅咒】
│   ├─ 版本链永存 → 2019年的v1事件不能被修改
│   ├─ Upcasting链 → v1→v2→v3→...→vN
│   ├─ 投影管道线性增重 → 所有消费者需理解所有历史版本
│   ├─ 存储膨胀 → 事件日志只增不减
│   ├─ 删除悖论 → "删除"是添加删除事件，真实数据永存
│   └─ GDPR/隐私合规 → "被遗忘权"与不可变性的冲突
│
└─【与CRDT的张力】
    ├─ Event Sourcing：禁止历史重写（绝对不可变）
    ├─ CRDT：允许状态合并（重写历史视角）
    └─ 选择：函数式美学 vs 工程现实
```

---

## 二、核心代数结构

### 2.1 形式化定义

```
定义（Event Sourcing系统）：
  三元组 (E, S, apply)，其中

  E = 事件类型集合
  S = 状态类型集合
  apply: S × E → S  （纯函数，无副作用）

系统状态：
  State(t) = foldl(apply, initState, [e₁, e₂, ..., eₙ])
  其中 [e₁, ..., eₙ] 是时间t之前发生的所有事件（按时间顺序）

时间旅行：
  ∀t₁ < t₂, State(t₁) 可通过截取事件日志前缀 [e₁, ..., eₖ] 重现
  （其中 eₖ 是时间t₁前的最后一个事件）
```

### 2.2 与函数式编程的对应

| 函数式概念 | Event Sourcing映射 | 工程价值 |
|-----------|-------------------|---------|
| **不可变数据结构** | 事件一旦写入永不被修改 | 审计性、可重现性、线程安全 |
| **纯函数（Pure Function）** | apply(s, e) 仅依赖s和e | 可测试、可缓存、可并行 |
| **Monoid** | 事件序列的拼接是Monoid运算 | 可分段处理、可分布式聚合 |
| **Catamorphism** | foldl(apply, init, events) | 统一的归约模式 |
| **Event Stream** | 无限延迟列表（Lazy List） | 实时处理与批处理统一 |

---

## 三、形式化美感：Event Sourcing的优势

### 3.1 审计与合规

```
传统CRUD系统：
  状态：Account.balance = 100
  问题："余额如何从200变成100？" → 可能需要外部日志

Event Sourcing系统：
  事件日志：
    1. AccountCreated(id=42, initial=200)
    2. Deposit(id=42, amount=50, source="transfer")
    3. Withdrawal(id=42, amount=150, target="invoice#123")
  状态 = foldl(apply, 0, [AccountCreated(200), Deposit(50), Withdrawal(150)])
       = 0 + 200 + 50 - 150 = 100

  审计回答："余额从200→250（存款50）→100（取款150）"
  无需外部日志，审计内建于数据模型。
```

### 3.2 时间旅行与调试

```
场景：发现某账户今天出现错误余额

传统系统：
  - 恢复快照到昨天 → 丢失今天其他正确交易
  - 或：在副本数据库上手动分析

Event Sourcing：
  - 重放事件日志至"错误发生前一刻"
  - State(t_error - 1ms) = foldl(apply, init, events[:k])
  - 逐步应用后续事件，定位导致错误的事件
  - 可在不影响生产的情况下，在本地完全重现生产状态
```

### 3.3 CQRS的天然伴侣

```text
Event Sourcing + CQRS架构
│
├─【写路径】（Command Side）
│   ├─ 接收Command（如PlaceOrder）
│   ├─ 验证业务规则
│   ├─ 生成Event（OrderPlaced）
│   ├─ 追加到Event Store
│   └─ 发布Event到消息总线
│
└─【读路径】（Query Side）
    ├─ 监听Event Stream
    ├─ 构建专用投影（Projection/Read Model）
    │   ├─ 订单列表投影（用于管理后台）
    │   ├─ 库存投影（用于实时库存查询）
    │   └─ 搜索索引投影（用于Elasticsearch）
    └─ 读模型优化：去规范化、预计算、缓存

优势：
  - 写模型简单（仅追加事件）
  - 读模型灵活（多个投影满足不同查询需求）
  - 读写独立扩展
```

---

## 四、形式化诅咒：版本链与维护成本

### 4.1 版本链永存

```
问题：业务规则变化需要修改事件结构

2019年：PaymentInitiated v1
  { orderId: string, amount: number, currency: string }

2020年：支持多种支付方式 → PaymentInitiated v2
  { orderId: string, amount: number, currency: string, method: string }

2021年：支持分期付款 → PaymentInitiated v3
  { orderId: string, amount: number, currency: string, method: string,
    installment: { count: number, interestRate: number } }

2022年：增加风控标记 → PaymentInitiated v4
  { orderId, amount, currency, method, installment, riskScore: number }

...

2026年：PaymentInitiated v8

诅咒：v1, v2, v3, v4, v5, v6, v7 事件永远不能被修改或删除。
      它们永久存在于事件日志中。
      所有投影代码必须能够理解所有历史版本。
```

### 4.2 Upcasting链

```
Upcasting：将旧版本事件转换为当前版本事件的过程

Projection代码必须维护：

function upcast(event):
  if event.version == 1:
    return upcast_v1_to_v2(event)
  if event.version == 2:
    return upcast_v2_to_v3(event)
  if event.version == 3:
    return upcast_v3_to_v4(event)
  ...
  if event.version == 7:
    return upcast_v7_to_v8(event)
  return event  // v8, current

function buildProjection(allEvents):
  for event in allEvents:
    currentEvent = upcast(event)  // 经过整个Upcasting链
    apply(projectionState, currentEvent)

维护成本增长：
  N年历史 → O(N)个版本 → O(N)个Upcasting函数
  每次新增版本需验证整个Upcasting链的正确性
  测试矩阵：M个投影 × N个版本 = M×N种组合
```

### 4.3 存储膨胀

| 时间 | 事件数 | 存储增长 | 问题 |
|------|--------|---------|------|
| 1年 | 1亿 | 100GB | 可管理 |
| 3年 | 5亿 | 600GB | 备份时间增长 |
| 5年 | 15亿 | 2TB | 快照恢复耗时 |
| 10年 | 50亿 | 10TB+ | 重放时间达小时级 |
| 20年 | 200亿 | 100TB+ | 几乎不可管理 |

**缓解策略**：

- 快照（Snapshot）：定期保存fold后的状态，重放时从最近快照开始
- 归档（Archive）：将旧事件迁移至冷存储
- 压缩：事件序列化格式优化（如Protobuf替代JSON）
- 但：快照与归档引入新复杂度（一致性、恢复流程）

### 4.4 删除悖论与GDPR冲突

```
GDPR "被遗忘权"（Right to be Erased）要求：
  "数据主体有权要求控制者删除与其相关的个人数据"

Event Sourcing的不可变性要求：
  "事件一旦写入，永不被修改或删除"

冲突解决策略（均不完美）：
┌────────────────────┬──────────────────────────────┐
│ 策略               │ 代价                         │
├────────────────────┼──────────────────────────────┤
│ 加密删除           │ 删除密钥 = 逻辑删除；但密钥   │
│ (Crypto-Shredding) │ 管理成为新风险点              │
├────────────────────┼──────────────────────────────┤
│ 事件重写（迁移）   │ 违反不可变性核心原则；审计    │
│                    │ 追踪断裂                      │
├────────────────────┼──────────────────────────────┤
│ 匿名化事件         │ 保留事件结构但去除PII；业务   │
│                    │ 语义可能受损                  │
├────────────────────┼──────────────────────────────┤
│ 分离PII存储        │ 事件引用外部PII；外部可删除   │
│                    │ 但增加系统复杂度              │
└────────────────────┴──────────────────────────────┘
```

---

## 五、Event Sourcing vs CRDT：深层张力

| 维度 | **Event Sourcing** | **CRDT** |
|------|-------------------|---------|
| **核心哲学** | 历史是神圣不可侵犯的 | 状态是可合并、可重解释的 |
| **数据模型** | 事件日志（append-only facts） | 半格状态（mergeable states） |
| **状态推导** | State = foldl(apply, init, events) | State = S₁ ⊔ S₂ ⊔ S₃ ⊔ ... |
| **并发处理** | 依赖外部定序（如事件总线） | 天然协调自由（交换/结合/幂等） |
| **版本演化** | Upcasting链线性增重 | 代数结构稳定，演化影响小 |
| **删除语义** | "添加删除事件"（逻辑删除） | 物理合并可能消除旧状态 |
| **审计能力** | 极强（完整历史） | 弱（合并后丢失操作历史） |
| **长周期维护** | 成本超线性增长 | 成本稳定（代数结构不变） |
| **最佳适用** | 金融审计、合规系统、短期项目 | 协作编辑、IoT、长周期分布式系统 |

**批判性结论**：Event Sourcing是函数式编程美学对工程现实的系统性高估。在**短生命周期系统**（<3年）中，其审计性和可重现性的价值超过维护成本；在**长生命周期系统**（>5年）中，版本链永存的诅咒通常使传统CRUD+审计日志成为更务实的选择。

---

## 六、概念定义与属性关系

| 概念 | 定义 | 属性 | 示例 | 反例 |
|------|------|------|------|------|
| **Event Sourcing** | 将系统状态建模为不可变事件序列的左折叠 | 审计性、可重现性、追加-only写入、版本链诅咒 | 金融交易系统的事件日志 | 简单CRUD博客系统（过度设计） |
| **Projection（投影）** | 从事件日志派生的特定查询优化视图 | 只读、可重建、可有多重投影 | 订单列表视图、库存视图 | 直接修改投影（违反单向数据流） |
| **Upcasting** | 将旧版本事件转换为当前版本的过程 | 必须保持语义等价、线性链增长、测试负担 | v1 PaymentInitiated → v8 | 跳过中间版本直接升级（可能丢失语义） |
| **Snapshot（快照）** | 事件日志在某时间点的fold结果缓存 | 加速恢复、与事件日志需一致性保证 | 每日自动快照 | 无快照（长日志重放极慢） |
| **Crypto-Shredding** | 加密存储后删除密钥以实现逻辑删除 | 满足合规、但密钥管理成新风险 | GDPR删除实现 | 物理删除事件（破坏不可变性） |

---

## 七、交叉引用

- → [04-总览](./00-总览-从直觉到半格理论.md)
- → [04/01-CRDT](01-CRDT-JoinSemilattice与强最终一致性.md)
- → [04/02-向量时钟](02-向量时钟-偏序关系与因果关系.md)
- → [05/03-事件驱动架构](../05-架构模式与部署单元光谱/03-事件驱动架构-解耦与一致性的设计哲学.md)
- ↑ [00/05-元认知批判](../00-元认知与系统思维框架/05-元认知批判-模型的隐含假设与失效条件.md)

---

## 八、参考文献

| 作者 | 标题 | 出处 | 年份 |
|------|------|------|------|
| Martin Fowler | "Event Sourcing" | martinfowler.com | 2005 |
| Greg Young | *Exploring CQRS and Event Sourcing* | Microsoft patterns & practices | 2012 |
| Chris Richardson | *Microservices Patterns* (Chapter 6: Event Sourcing) | Manning | 2018 |
| Mathias Verraes | "The Complexity of Versioning Events" | verraes.net | 2015 |
| Marc Shapiro et al. | CRDT论文（对比参考） | INRIA | 2011 |
| Michiel Overeem et al. | "An Empirical Characterization of Event Sourced Systems..." | *IEEE Software* | 2022 |
| GDPR Regulation | Article 17: Right to erasure ('right to be forgotten') | EU Regulation | 2016 |

## 九、权威引用

> **Martin Fowler** (2005): "The fundamental idea of Event Sourcing is that we should ensure that every change to the state of an application is captured in an event object, and that these event objects are themselves stored in the sequence they were applied for the same lifetime as the application state itself."

> **Greg Young** (2012): "Events are facts. A fact is something that happened; it cannot be changed, only reinterpreted. This is the single most important concept in event sourcing."

---

## 十、批判性总结

Event Sourcing将系统状态建模为不可变事件流的左折叠，这种函数式美学在理论上无懈可击，却在长周期工程中暴露出结构性诅咒。其隐含假设——事件模式演化是低频且可控的——与现实业务的高速迭代存在根本张力：每新增一个业务字段，整个Upcasting链就延长一环，测试矩阵呈M×N爆炸。版本链永存导致存储膨胀和重放缓存恶化，而GDPR"被遗忘权"与不可变性的冲突至今没有完美解法。与CRDT的收敛性哲学相比，Event Sourcing坚守历史神圣性，提供了无可比拟的审计能力，却丧失了状态合并的灵活性。与快照型数据库相比，时间旅行能力以超线性维护成本为代价。未来趋势上，加密删除（Crypto-Shredding）和差分事件压缩正在缓解合规与存储压力，而"事件溯源+物化视图"的混合模式正在成为工业界的主流务实选择。

---

*文件创建日期：2026-04-23*
*状态：已完成*
