# 工作流与并发系统分析：Petri 网与工作流引擎

> **来源映射**: View/01.md §2.2
> **国际权威参考**: "Petri Nets: Properties, Analysis and Applications" (Murata, 1989), "Workflow Patterns" (van der Aalst et al.), Temporal Logic of Actions (Lamport)

---

## 一、知识体系思维导图

```text
工作流与并发系统分析
│
├─► Petri 网
│   ├─► 基本结构
│   │   ├─ Place (库所): 圆形，表示状态/条件
│   │   ├─ Transition (变迁): 矩形，表示事件/动作
│   │   ├─ Token (托肯): 黑点，表示标记状态
│   │   └─ Arc (弧): 有向边，连接 Place 和 Transition
│   │
│   ├─► 动态行为
│   │   ├─ 使能 (Enabled): 输入 Place 有足够 Token
│   │   ├─ 触发 (Fire): 消耗输入 Token，产生输出 Token
│   │   └─ 并发: 多个变迁同时使能 → 非确定性选择
│   │
│   ├─► 性质分析
│   │   ├─ 可达性 (Reachability): 某标记是否可达
│   │   ├─ 有界性 (Boundedness): Place 中 Token 数上限
│   │   ├─ 活性 (Liveness): 无死锁 (每个变迁最终可触发)
│   │   └─ 公平性 (Fairness): 无饥饿
│   │
│   └─► 扩展
│       ├─ 有色 Petri 网: Token 带有数据值
│       ├─ 时间 Petri 网: 变迁有触发延迟
│       └─ 层次 Petri 网: 子网抽象
│
├─► 工作流模式
│   ├─ 顺序 (Sequence): A → B → C
│   ├─ 并行分支 (Parallel Split): A → B ∥ C
│   ├─ 同步合并 (Synchronization): B ∥ C → D
│   ├─ 选择 (Choice): A → B ⊕ C
│   ├─ 循环 (Loop): A → [条件] → A
│   └─ 工作流模式总数: van der Aalst 定义 20+ 种基本模式
│
├─► 时序逻辑验证
│   ├─ LTL (线性时序逻辑): 路径属性
│   ├─ CTL (计算树逻辑): 分支属性
│   └─ TLA+ (Lamport): 状态机 + 时序逻辑 + 证明
│
└─► 现代工作流引擎
    ├─ Temporal (原 Cadence): 代码即工作流，持久化执行
    ├─ Camunda: BPMN 2.0 引擎
    ├─ AWS Step Functions: 云托管状态机
    └─ Netflix Conductor: 微服务编排
```

---

## 二、核心概念的形式化定义

### 2.1 Petri 网

```text
定义 (Petri 网):
  N = (P, T, F, M₀)
  
  P: 有限库所集合
  T: 有限变迁集合 (P ∩ T = ∅)
  F: (P × T) ∪ (T × P) → ℕ (弧的权重)
  M₀: P → ℕ (初始标记)
  
  变迁 t ∈ T 在标记 M 下使能:
    enabled(M, t) ⟺ ∀p ∈ •t: M(p) ≥ F(p, t)
    其中 •t = {p | F(p, t) > 0} 是 t 的输入库所
    
  触发规则:
    M' = M - F(•t, t) + F(t, t•)
    即: 从输入库所消耗 Token，向输出库所产生 Token
    
  可达性:
    R(N, M₀) = {M | M₀ →* M}
    其中 →* 是触发关系的自反传递闭包
```

### 2.2 工作流作为状态机

```text
定义 (工作流引擎):
  工作流 W = (S, s₀, A, T, C)
  
  S: 状态集合
  s₀ ∈ S: 初始状态
  A: 活动 (Activity) 集合
  T: S × A → S (状态转换)
  C: A → (S → Bool) (活动补偿函数)
  
  执行语义:
    编排式 (Orchestration):
      中央协调器按预定义顺序触发活动
      
    编舞式 (Choreography):
      各服务通过事件自主响应，无中央协调
      
  Saga 模式:
    长事务分解为子事务序列
    每个子事务有对应的补偿操作
    失败时按逆序执行补偿
```

---

## 三、工作流引擎对比矩阵

| 维度 | Temporal | Camunda | AWS Step Functions | Netflix Conductor |
|------|---------|---------|-------------------|------------------|
| **建模方式** | 代码 (DSL) | BPMN 图形 | ASL JSON | JSON DSL |
| **持久化** | **事件溯源** | 数据库 | DynamoDB | Redis/Postgres |
| **补偿/Saga** | ✅ 原生 | ✅ BPMN | ✅ | ✅ |
| **定时任务** | ✅ | ✅ | ✅ | ✅ |
| **语言 SDK** | Go/Java/TS/Python | Java | AWS SDK | Java/Go/Python |
| **可视化** | UI 展示 | **BPMN 编辑器** | 有限 | 有限 |
| **开源** | **MIT** | **Apache** | ❌ | **Apache** |
| **适用场景** | 微服务编排 | 业务流程 | AWS 生态 | 媒体工作流 |

---

## 四、权威引用

> **Carl Adam Petri** (1962):
> "Kommunikation mit Automaten." —— Petri 网的原始博士论文。

> **Tadao Murata** ("Petri Nets: Properties, Analysis and Applications", 1989):
> "Petri nets are a graphical and mathematical modeling tool applicable to many systems."

> **Wil van der Aalst** ("Workflow Patterns", 2003):
> "We have identified 20 workflow patterns that provide the basis for an in-depth comparison of workflow management systems."

> **Leslie Lamport** (TLA+):
> "A specification is not a program. It is a mathematical formula."

---

## 五、子主题导航

| 序号 | 子主题文件 | 核心内容 |
|------|-----------|---------|
| 01 | [01-Petri网-并发系统的形式化建模](./01-Petri网-并发系统的形式化建模.md) | 结构、动态行为、性质分析 |
| 02 | [02-定时自动机-工作流的形式化验证](./02-定时自动机-工作流的形式化验证.md) | 时间约束、模型检测、UPPAAL |
| 03 | [03-工作流引擎-状态机与Saga模式的形式化](./03-工作流引擎-状态机与Saga模式的形式化.md) | 编排/编舞、Saga、Temporal |

---

## 六、批判性总结

Petri 网是**并发系统的几何学**：它用图的拓扑结构精确描述系统的状态空间和并发行为，使死锁、活性和有界性从"偶发神秘"变为"可形式化证明"。但 Petri 网的**状态空间爆炸**问题限制了其在大型系统中的应用——一个包含 100 个库所的 Petri 网，其可达状态集可能是天文数字，使得自动化分析不可行。

Temporal 的**代码即工作流**范式是工作流引擎的**范式革命**：传统 BPMN 引擎要求开发者学习图形化建模语言，而 Temporal 让开发者用熟悉的编程语言（Go/Java/TypeScript）编写工作流逻辑，引擎自动处理持久化、重试、超时和补偿。这不是语法糖的改进，而是**抽象层次的跃迁**——从"描述工作流"到"编写工作流"。但这也带来了** Vendor Lock-in**风险：一旦深度使用 Temporal 的特定语义，迁移到其他引擎的成本极高。

2026 年的工作流趋势是**事件驱动编排**（Event-Driven Orchestration）：将 Saga 模式与事件溯源（Event Sourcing）结合，每个工作流步骤产生领域事件，这些事件既驱动工作流前进，又成为系统审计和数据分析的源头。这是**命令与查询职责分离**（CQRS）在工作流领域的延伸——工作流引擎处理命令（编排），事件流处理查询（分析）。
