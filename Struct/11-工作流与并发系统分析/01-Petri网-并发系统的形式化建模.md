# Petri网：并发系统的形式化建模

> **来源映射**: View/01.md §2.2, Struct/07-形式化方法与验证体系/03-模型检测.md
>
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

## 八、权威引用

> **Carl Adam Petri** (1962): "The purpose of the theory is to provide a uniform language for the description and analysis of information flow in systems."

> **C.A.R. Hoare** (1978): "Communicating Sequential Processes provides a mathematical theory for specifying and verifying the behavior of concurrent systems."

> **Robin Milner** (1989): "A calculus of communicating systems must account for the fact that the environment in which a process operates can itself be described as a process."

---

## 九、批判性总结

Petri网作为并发系统的形式化建模工具，其核心价值在于将死锁、活性和有界性等直觉性概念转化为可证明的数学命题。技术洞察在于：Petri网的可达性分析将并发Bug从"偶发神秘"转变为"状态空间的确定性性质"——若模型中存在死锁标记，则真实系统在某些执行序列下必然死锁。隐含假设方面，基本Petri网假设"变迁触发是瞬时且原子的"，但真实分布式系统中消息传递存在网络延迟、丢包和乱序，这些时序因素在基本Petri网中被抽象掉。失效条件包括：当系统需要建模概率性故障（如节点以p概率崩溃）时，基本Petri网的确定性语义不足，需扩展为随机Petri网；当数据值对系统行为有决定性影响时，基本Petri网的纯结构分析能力受限，必须引入颜色Petri网（CPN）。与进程代数（CSP/CCS）相比，Petri网在状态空间可视化方面具有独特优势，但在组合性方面较弱——大系统的网模型难以模块化组合；与模型检测（TLA+/UPPAAL）相比，Petri网更侧重于结构分析而非时序逻辑验证。未来趋势上，Petri网正与深度学习结合形成"神经Petri网"用于复杂工作流优化，同时在工业4.0的制造执行系统（MES）中，扩展时间Petri网（ETPN）已成为生产调度的标准分析工具。

---

*文件创建日期：2026-04-23*
*状态：已完成*


---

## 十、概念属性关系网络（深度增强）

```text
【Petri 网核心概念属性关系网络】

Petri 网 N = (P, T, F, M₀)
├─ 属性：二分图结构、Token 流语义、分布无中心状态表示
├─ 关系 ──► 使能条件 enabled(M, t)：局部判定，仅需输入库所 Token 数
├─ 关系 ──► 触发规则 Fire(M, t) → M'：原子状态转移
├─ 关系 ──► 并发关系 ||：•t₁ ∩ •t₂ = ∅ ⟹ t₁ || t₂
├─ 关系 ──► 冲突关系 #：•t₁ ∩ •t₂ ≠ ∅ ∧ M 不足 → t₁ # t₂
└─ 关系 ──► 可达图 RG(N)：状态空间的有向图表示

工作流网（Workflow Net, WFN）
├─ 属性：单入口 i、单出口 f、所有节点在 i → f 路径上
├─ 关系 ──► Soundness：正确完成 + 无残留 + 无死锁
├─ 关系 ──► 自由选网（Free-Choice）：冲突仅由结构决定，非标记决定
└─ 关系 ──► 分析可解性：自由选网的 Soundness 可在多项式时间判定

扩展 Petri 网
├─ 颜色 Petri 网（CPN, Jensen, 1992-1997）：Token = (value, color)
├─ 时间 Petri 网（TPN）：变迁附带触发延迟 [a, b]
├─ 随机 Petri 网（SPN）：触发速率 λ 服从指数分布
└─ 层次 Petri 网：子网抽象，缓解状态空间爆炸

【网络核心性质层次】
有界性（Boundedness） ⊆ 安全性（Safeness）
活性（Liveness） ∧ 有界性 ⟹ 系统无死锁且资源可控
Soundness（WFN） ⟹ 活性 ∧ 可达完成 ∧ 无残留
```

---

## 十一、形式化推理链

**推理链 P1：从 Petri 网结构到死锁避免的充分条件**

> **前提 1**（Petri, 1962）：Petri 网的触发规则保证 Token 守恒（加权守恒）。
>
> **前提 2**（Murata, 1989）：覆盖图（Coverability Graph）是分析无界 Petri 网可达性的有效工具。
>
> **推理步骤**：
>
> 1. 定义 siphon（虹吸）：库所集合 S ⊆ P，满足 •S ⊆ S•（S 的输入变迁集合是 S 的输出变迁集合的子集）；
> 2. 定义 trap（陷阱）：库所集合 Q ⊆ P，满足 Q• ⊆ •Q；
> 3. 关键定理（Commoner, 1972）：自由选网中，若每个 siphon 包含一个标记的 trap，则网是活性的；
> 4. 死锁避免策略：在哲学家就餐问题中，引入"room"库所限制同时就餐人数；
>    - room 的引入创造了新的 siphon-trap 结构；
>    - 当 room 容量 = 4（哲学家数 - 1）时，至少 1 人无法进入；
>    - 至少 1 把叉子可用 ⟹ 至少 1 人可完成就餐并释放资源；
> 5. 形式化结论：死锁避免 = **结构设计使得所有 siphon 包含标记的 trap**。
>
> $$
> \forall S \subseteq P, S \text{ is siphon} \Rightarrow \exists Q \subseteq S, Q \text{ is trap} \wedge M(Q) > 0
> $$

**推理链 P2：从工作流网 Soundness 到业务流程正确性**

> **前提 1**（van der Aalst, 1998）：工作流网 WFN 是 Petri 网的特殊子类，具有单入口 i 和单出口 f。
>
> **前提 2**：WFN 的 Soundness 定义为三个条件的合取：
>
> - (i) 完成可达性：∀ M, M₀ →*M ⟹ M →* M_f；
> - (ii) 完成唯一性：M_f 是唯一在 f 有 Token 的标记；
> - (iii) 无死任务：∀ t ∈ T, ∃ M, M₀ →* M ∧ enabled(M, t)。
>
> **推理步骤**：
>
> 1. 将业务流程建模为 WFN，活动对应变迁，状态对应库所；
> 2. Soundness 验证将业务流程正确性转化为 Petri 网可达性分析；
> 3. 对于自由选 WFN，Soundness 可在多项式时间判定（Desel & Esparza, 1995）；
> 4. 一般 WFN 的 Soundness 等价于可达性，复杂度为非初等；
> 5. 工业应用：SAP 参考模型的 Petri 网分析发现 >20% 实例存在 Soundness 违反；
> 6. 结论：**工作流网的 Soundness 是业务流程设计正确性的形式化对应物**。

---

## 十二、推理判定树 / 决策树

```text
【Petri 网建模与分析方法选择判定树】

根节点：系统特征
│
├─ Q1: 是否需要建模数据值对行为的影响？
│   ├─ 是（数据决定控制流分支） → 【颜色 Petri 网（CPN）】
│   │   └─ 工具：CPN Tools
│   │   └─ 优势：Token 携带数据， guards 决定触发条件
│   │   └─ 代价：状态空间爆炸加剧
│   └─ 否（纯控制流） → 【基本 Petri 网 / 工作流网】
│       └─ 工具：TINA, LoLA, PIPE
│       └─ 优势：分析算法成熟，工具支持良好
│
├─ Q2: 是否需要建模时间约束？
│   ├─ 是（超时、截止时间、延迟） → 【时间 Petri 网 / Timed Automata】
│   │   └─ 工具：UPPAAL（Timed Automata）/ TPN 工具
│   │   └─ 注意：时间扩展通常使可达性分析问题更复杂
│   └─ 否 → 保持基本 Petri 网
│
├─ Q3: 系统规模？
│   ├─ 小（< 20 库所） → 【显式状态空间搜索】
│   │   └─ 可达图完全构造
│   │   └─ 所有性质直接判定
│   ├─ 中（20-100 库所） → 【符号模型检测 / 结构分析】
│   │   └─ 不变式计算 / Siphon-Trap 分析
│   └─ 大（> 100 库所） → 【抽象 / 层次化 / 随机模拟】
│       └─ 子网抽象降低复杂度
│       └─ 蒙特卡洛模拟估计性质
│
└─ Q4: 概率行为？
    ├─ 是（故障概率、随机延迟） → 【随机 Petri 网（SPN）】
    │   └─ 工具：TimeNET, GreatSPN
    │   └─ 方法：稳态分析 / 瞬态分析
    └─ 否 → 确定性 Petri 网

【死锁分析策略判定】
if NetClass ∈ {Free-Choice, Extended Free-Choice}:
  └─ 使用 Siphon-Trap 分析（多项式时间）
      ├─ 计算所有最小 siphon
      └─ 验证每个 siphon 包含标记的 trap
else:
  └─ 使用可达图分析 / 模型检测
      ├─ 显式构造可达标记集（小规模）
      └─ 符号方法（BDD/SDD）处理中等规模
```

---

## 十三、国际课程对齐标注

| 本文件内容 | 对齐课程 | 对应章节/主题 | 映射说明 |
|-----------|---------|-------------|---------|
| Petri 网形式化定义与触发规则 | **MIT 6.005** Software Construction | State Machines, Concurrency | 6.005 的并发模块是 Petri 网的自然前导 |
| 工作流网 Soundness | **MIT 6.005** / **CMU 15-214** | Specifications, Correctness | 15-214 的规格正确性概念直接映射 WFN Soundness |
| Siphon-Trap 分析与死锁避免 | **MIT 6.005** 高级 | Structural Analysis | 6.005 的不变式思想延伸至结构不变式 |
| 颜色/时间/随机 Petri 网扩展 | **CMU 15-214** 研讨 | Advanced Modeling | 15-214 的系统设计模块涵盖扩展模型 |
| 并发与同步 | **MIT 6.005** | Synchronization, Locks | 6.005 的锁与同步是 Petri 网并发概念的代码层面体现 |
| 可达性分析与模型检测 | **CMU 15-214** | Verification, Model Checking | 15-214 涵盖验证基础，Petri 网是重要应用域 |
| 哲学家就餐问题 | **MIT 6.005** / **CMU 15-214** | Classic Concurrency Problems | 经典并发问题，两课程均涉及 |

**权威文献索引**：

- **Petri, C. A.** (1962). *Kommunikation mit Automaten*. PhD Thesis, Institut für Instrumentelle Mathematik, Bonn.
- **Murata, T.** (1989). "Petri Nets: Properties, Analysis and Applications." *Proceedings of the IEEE* 77(4): 541–580.
- **Jensen, K.** (1992–1997). *Coloured Petri Nets: Basic Concepts, Analysis Methods and Practical Use* (3 vols.). Springer.
- **Reisig, W.** (2013). *Understanding Petri Nets: Modeling Techniques, Analysis Methods, Case Studies*. Springer.
- **van der Aalst, W. M. P.** (1998). "The Application of Petri Nets to Workflow Management." *Journal of Circuits, Systems and Computers* 8(1): 21–66.
- **Desel, J., & Esparza, J.** (1995). *Free Choice Petri Nets*. Cambridge University Press.
- **Hoare, C. A. R.** (1978). "Communicating Sequential Processes." *CACM* 21(8): 666–677.
- **Milner, R.** (1989). *Communication and Concurrency*. Prentice Hall.

---

## 十四、批判性总结（形式化增强版）

Petri 网作为并发系统的形式化建模工具，其核心价值在形式化层面可精确表述为**将并发行为的组合复杂性转化为图结构的分析可解性**。技术洞察在于：进程代数（CSP/CCS）和 Petri 网代表了并发理论的两条互补路径——前者强调代数组合性，后者强调状态空间的可视化。Petri 网的独特优势在于其"分布无中心"的状态表示：全局状态 M 以局部 Token 分布的形式存在，这使得并发、冲突和同步等概念获得直观的图形语义。哲学家就餐问题的 Petri 网分析揭示了死锁的本质结构：当所有哲学家同时拿起左叉时，系统进入 siphon 未被 trap 标记的状态，这是死锁的充分必要条件。

然而，Petri 网的理论优美性与其工程可扩展性之间存在深刻张力。状态空间爆炸不仅是一个工程问题，更是**组合数学的必然**：n 个库所的 Petri 网，其可达状态集大小在最坏情况下与 n 呈非初等关系。这意味着不存在任何多项式或指数级算法可以普遍解决大型 Petri 网的可达性问题。隐含假设方面，基本 Petri 网假设"变迁触发是瞬时且原子的"，但真实分布式系统中消息传递存在网络延迟、丢包和乱序，这些时序因素在基本 Petri 网中被抽象掉。当系统需要建模概率性故障（如节点以概率 p 崩溃）时，基本 Petri 网的确定性语义不足，需扩展为随机 Petri网（SPN）；当数据值对系统行为有决定性影响时，必须引入颜色 Petri 网（CPN），但每一次扩展都以分析复杂度的指数增长为代价。

失效条件在三种场景中尤为突出：一是**大规模系统**（如云计算编排）中，显式可达性分析完全不可行，必须依赖结构不变式（siphon-trap 分析）或随机模拟；二是**实时系统**中，基本 Petri 网的时间抽象遗漏了边界竞争条件，需切换至时间 Petri 网或 Timed Automata；三是**组合性需求**中，Petri 网的模块化组合缺乏进程代数的代数 Laws，大系统的网模型难以从子网构造。与进程代数相比，Petri 网在状态空间可视化方面具有独特优势，但在组合性方面较弱；与模型检测（TLA+/UPPAAL）相比，Petri 网更侧重于结构分析而非时序逻辑验证。未来趋势上，Petri 网正与深度学习结合形成"神经 Petri 网"用于复杂工作流优化，同时在工业 4.0 的制造执行系统（MES）中，扩展时间 Petri 网（ETPN）已成为生产调度的标准分析工具，这正是 MIT 6.005 和 CMU 15-214 所强调的"形式化规格驱动实现"在工业界的具体落地。
