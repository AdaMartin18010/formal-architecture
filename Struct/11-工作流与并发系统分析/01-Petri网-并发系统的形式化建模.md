# Petri网：并发系统的形式化建模

> **定位**：Petri网是并发系统的"几何学"——用图的结构（库所Place和变迁Transition）精确描述系统的状态空间和并发行为。它是理解死锁、活性和有界性的强大工具。
>
> **核心命题**：如果一个系统的Petri网模型存在死锁，那么真实系统在某些执行序列下也会死锁。Petri网让并发Bug从"偶发神秘"变成"可证明存在"。

---

## 一、思维导图：Petri网核心概念

```text
Petri网
│
├─【基本结构】
│   ├─ Place（库所）：状态/条件（圆形）
│   ├─ Transition（变迁）：事件/动作（矩形/条形）
│   ├─ Token（托肯）：标记状态（黑点）
│   └─ Arc（弧）：连接Place和Transition
│
├─【动态行为】
│   ├─ 使能（Enabled）：输入Place都有足够Token
│   ├─ 触发（Fire）：消耗输入Token，产生输出Token
│   └─ 并发：多个变迁同时使能 → 非确定性选择
│
├─【性质分析】
│   ├─ 可达性（Reachability）：某标记是否可达
│   ├─ 有界性（Boundedness）：Place中Token数是否有限
│   ├─ 活性（Liveness）：无死锁
│   └─ 公平性（Fairness）：无饥饿
│
└─【扩展】
    ├─ 颜色Petri网（CPN）：带数据值的Token
    ├─ 时间Petri网：变迁有延迟
    └─ 层次Petri网：模块化组合
```

---

## 二、Petri网的形式化定义

> **权威来源**：Carl Adam Petri, *Kommunikation mit Automaten*, 1962

```
Petri网定义为四元组 N = (P, T, F, M₀)

  P = 有限库所集合（Places）
  T = 有限变迁集合（Transitions），P ∩ T = ∅
  F ⊆ (P × T) ∪ (T × P) = 弧关系（流关系）
  M₀: P → ℕ = 初始标记（每个Place的初始Token数）

变迁t ∈ T的使能条件：
  ∀p ∈ •t: M(p) ≥ 1
  其中 •t = {p | (p, t) ∈ F} 是t的输入库所集合

触发后的新标记 M'：
  M'(p) = M(p) - |F(p, t)| + |F(t, p)|

  即：消耗输入Token，产生输出Token

并发性：
  若两个变迁t₁, t₂的输入库所不相交（•t₁ ∩ •t₂ = ∅）
  → 它们可以并发触发
```

---

## 三、经典问题建模

### 3.1 生产者-消费者

```text
Petri网表示：

  [Producer] ──► |buffer_empty| ──► [Consume] ──► |buffer_full|
       ▲                                              │
       └──────────────────────────────────────────────┘

库所：
  - producer_ready: 生产者就绪
  - buffer_empty: 缓冲区空位
  - buffer_full: 缓冲区有数据
  - consumer_ready: 消费者就绪

变迁：
  - produce: producer_ready + buffer_empty → buffer_full
  - consume: consumer_ready + buffer_full → buffer_empty + producer_ready

性质验证：
  ✓ 有界性：buffer_empty + buffer_full = 容量（恒定）
  ✓ 活性：无死锁（生产者和消费者不会互相阻塞）
```

### 3.2 哲学家就餐问题（死锁分析）

```text
5位哲学家，5把叉子

Petri网揭示死锁：
  若所有哲学家同时拿起左叉 → 所有叉子被占用
  → 无人能拿右叉 → 死锁

解决策略的Petri网建模：
  1. 资源排序：限制同时拿叉的方式
  2. 引入"同时拿两把叉"的原子变迁
  3. 限制就餐人数（最多4人）

验证：
  策略3的Petri网：
    - 添加"room"库所，容量=4
    - 进入餐桌需消耗room Token
    → 至少1人无法进入 → 至少1把叉子可用 → 无死锁
```

---

## 四、性质分析技术

| 性质 | **定义** | **分析方法** | **工具** |
|------|---------|------------|---------|
| **可达性** | 标记M是否从M₀可达 | 状态空间搜索 | TINA, LoLA |
| **有界性** | 所有Place的Token数是否有上界 | 覆盖图分析 | TINA |
| **活性** | 每个变迁是否始终可被触发 | 活性图分析 | LoLA |
| **死锁** | 是否存在无使能变迁的标记 | 状态空间搜索 | 所有工具 |
| **公平性** | 使能的变迁是否最终触发 | 公平性分析 | CPN Tools |
| **-home标记** | 是否存在可无限返回的标记 | 结构分析 | TINA |

---

## 五、概念定义与属性关系

| 概念 | 定义 | 属性 | 示例 | 反例 |
|------|------|------|------|------|
| **Petri网** | 用Place/Transition/Token建模并发系统的形式化工具 | 图形化、可分析、表达能力有限（非图灵完备） | 工作流建模 | 需要概率分析的系统 |
| **标记（Marking）** | 各Place中Token数量的分布 | 表示系统状态、可变迁 | M = [2, 0, 1] | 非状态表示 |
| **使能（Enabled）** | 变迁的所有输入Place都有足够Token | 可触发的前提 | produce变迁使能 | 缺Token的变迁 |
| **死锁** | 无变迁使能的标记 | 系统停止、需避免 | 哲学家全拿左叉 | 有使能变迁的状态 |
| **颜色Petri网** | Token带数据值的扩展Petri网 | 更强表达力、更复杂分析 | CPN Tools建模 | 基本Petri网 |

---

## 六、交叉引用

- → [11-总览](./00-总览-Petri网与工作流引擎.md)
- → [11/02-工作流引擎](03-工作流引擎-状态机与Saga模式的形式化.md)
- → [05/03-EDA](../05-架构模式与部署单元光谱/03-事件驱动架构-解耦与一致性的设计哲学.md)
- ↓ [07/03-模型检测](../07-形式化方法与验证体系/03-模型检测-UPPAAL与状态空间爆炸问题.md)

---

## 七、参考文献

| 作者 | 标题 | 出处 | 年份 |
|------|------|------|------|
| Carl Adam Petri | *Kommunikation mit Automaten* | Dissertation | 1962 |
| Jensen | *Coloured Petri Nets* (3 vols.) | Springer | 1992-1997 |
| Murata | "Petri Nets: Properties, Analysis and Applications" | *Proc. IEEE* | 1989 |
| Reisig | *Understanding Petri Nets* | Springer | 2013 |

---

*文件创建日期：2026-04-23*
*状态：已完成*
