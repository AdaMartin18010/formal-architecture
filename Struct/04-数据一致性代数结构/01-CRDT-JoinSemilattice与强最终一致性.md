# CRDT：Join-Semilattice 与强最终一致性

> **定位**：本文件将CRDT从"最终一致的魔法"还原为**半格（Join-Semilattice）代数的实例化**。理解半格公理是区分"盲目使用CRDT"与"理解为何CRDT有效"的关键。
>
> **核心命题**：当数据操作满足交换律、结合律、幂等律时，CRDT提供了**无需协调（Coordination-Free）**的一致性保证——这是分布式系统中最强的可用性承诺。

---

## 一、思维导图：CRDT的代数根基

```text
CRDT：从直觉到半格理论
│
├─【公理系统】Join-Semilattice (Σ, ⊑, ⊔)
│   ├─ 偏序性：⊑ 是Σ上的偏序（自反、反对称、传递）
│   ├─ 最小上界：∀S1,S2∈Σ, S1⊔S2 是 {S1,S2} 的最小上界
│   ├─ 交换律：S1⊔S2 = S2⊔S1
│   ├─ 结合律：(S1⊔S2)⊔S3 = S1⊔(S2⊔S3)
│   └─ 幂等律：S⊔S = S
│
├─【State-based CRDT】
│   ├─ 操作：读取本地状态，合并整个远程状态
│   ├─ 传播：定期或事件驱动地交换完整状态
│   ├─ 要求：状态空间小或支持增量Delta
│   └─ 优势：简单、容错（丢失消息可重试）
│
├─【Op-based CRDT】
│   ├─ 操作：传播操作（Update）而非状态
│   ├─ 要求：底层消息系统提供可靠广播（Reliable Broadcast）
│   ├─ 要求：操作本身满足交换律/结合律/幂等律
│   └─ 优势：带宽效率高（尤其大状态场景）
│
├─【常见CRDT类型】
│   ├─ Counter：G-Counter（增长计数器）, PN-Counter（可增可减）
│   ├─ Set：G-Set（仅增长集合）, OR-Set（添加赢/删除赢）, LWW-Element-Set
│   ├─ Register：LWW-Register（最后写入赢）, MV-Register（多值）
│   ├─ Map：OR-Map（嵌入其他CRDT的值）
│   └─ Sequence：RGA, WOOT, YATA（协同编辑）
│
└─【2026演进】
    ├─ Delta-State CRDT：仅传播状态差分
    ├─ Pure Op-Based：基于反熵（Anti-Entropy）的Op传播
    └─ Policy-CRDT：可配置合并语义（Add-Wins vs Remove-Wins）
```

---

## 二、Join-Semilattice 形式化

> **权威来源**：Marc Shapiro et al., "A Comprehensive Study of Convergent and Commutative Replicated Data Types", INRIA Technical Report, 2011

### 2.1 公理系统

```
定义（Join-Semilattice）：
  结构 (Σ, ⊑, ⊔) 满足：

  1. 偏序性（Partial Order）：
     ⊑ 是Σ上的偏序关系：
     - 自反：∀S∈Σ, S ⊑ S
     - 反对称：S₁ ⊑ S₂ ∧ S₂ ⊑ S₁ ⟹ S₁ = S₂
     - 传递：S₁ ⊑ S₂ ∧ S₂ ⊑ S₃ ⟹ S₁ ⊑ S₃

  2. 最小上界（Least Upper Bound）：
     ∀S₁,S₂∈Σ, S₁⊔S₂ ∈ Σ 满足：
     - S₁ ⊑ (S₁⊔S₂) 且 S₂ ⊑ (S₁⊔S₂)
     - ∀T∈Σ: (S₁⊑T ∧ S₂⊑T) ⟹ (S₁⊔S₂) ⊑ T

  3. 交换律（Commutativity）：S₁⊔S₂ = S₂⊔S₁

  4. 结合律（Associativity）：(S₁⊔S₂)⊔S₃ = S₁⊔(S₂⊔S₃)

  5. 幂等律（Idempotence）：S⊔S = S
```

### 2.2 定理：SEC保证

```
定理（Strong Eventual Consistency, SEC）：
  若所有副本最终接收到相同的更新集合，
  则State-based CRDT的状态合并保证：
  1. 最终所有副本状态收敛到相同值
  2. 收敛结果与更新接收顺序无关

证明概要：
  设副本i接收到的更新集合为Uᵢ，最终所有Uᵢ = U（相同集合）。

  每个更新u将状态从S变换为S' = S ⊔ Δ(u)。
  最终状态 = InitState ⊔ Δ(u₁) ⊔ Δ(u₂) ⊔ ... ⊔ Δ(uₙ)

  由交换律和结合律：
    ⊔ 运算的结果与操作数顺序无关。
  由幂等律：
    重复接收同一更新不改变结果。

  ∴ 所有副本的最终状态 = InitState ⊔ (⊔_{u∈U} Δ(u))
  该值唯一且与接收顺序无关。
```

---

## 三、CRDT 实例详解

### 3.1 G-Counter（增长计数器）

```
应用场景：页面浏览量、点赞数、API调用次数（只增不减的计数）

状态：GC = [c₁, c₂, ..., cₙ]  （每个副本维护自己的计数数组）

操作：
  - increment(i)：副本i将自己的计数 cᵢ += 1
  - query()：返回总和 Σcᵢ
  - merge(GC₁, GC₂)：逐元素取最大值
    result[j] = max(GC₁[j], GC₂[j])

半格结构验证：
  - 偏序：GC₁ ⊑ GC₂ ⟺ ∀j, GC₁[j] ≤ GC₂[j]
  - 合并：GC₁ ⊔ GC₂ = [max(GC₁[j], GC₂[j])]ⱼ
  - 交换律：max(a,b) = max(b,a) ✅
  - 结合律：max(max(a,b),c) = max(a,max(b,c)) ✅
  - 幂等律：max(a,a) = a ✅

反例（为何不能直接用整数加法）：
  整数加法不满足幂等律：a + a ≠ a
  若两个副本都增量，合并时加法会导致重复计数。
```

### 3.2 PN-Counter（可增可减计数器）

```
应用场景：库存数量、账户余额（允许增减，但需非负约束）

状态：PN = (P, N)，其中P和N都是G-Counter
  - P追踪增量操作
  - N追踪减量操作

操作：
  - increment(i)：P[i] += 1
  - decrement(i)：N[i] += 1
  - query()：返回 (ΣP[j]) - (ΣN[j])
  - merge(PN₁, PN₂)：
      P_result[j] = max(PN₁.P[j], PN₂.P[j])
      N_result[j] = max(PN₁.N[j], PN₂.N[j])

限制：
  query() 可能返回负值（若 decrement 多于 increment）
  若业务要求非负，需额外约束或改用其他CRDT
```

### 3.3 OR-Set（观察删除集合）

> **权威来源**：Marc Shapiro, Nuno Preguiça et al., "A Comprehensive Study of Convergent and Commutative Replicated Data Types", 2011

```
应用场景：购物车、标签系统、协作收藏夹（添加/删除元素）

问题：普通集合的删除不满足交换律
  - 副本A：添加x，然后删除x
  - 副本B：与A并发删除x
  - 若先执行A的删除再合并B的删除 → 最终无x
  - 若先执行B的删除再合并A的添加 → 最终有x（A的添加在删除后）

OR-Set解决方案：
  每个元素关联唯一标签（Tag），删除标记标签而非元素本身

  状态：ORSet = (A, R)，其中
    A = {(element, tag)} 已添加的元素-标签对集合
    R = {tag} 已删除的标签集合

  query()：返回 {e | ∃tag: (e, tag) ∈ A ∧ tag ∉ R}

  add(e)：生成新标签t，A ← A ∪ {(e, t)}
  remove(e)：对所有 (e, t) ∈ A，R ← R ∪ {t}

  merge(ORSet₁, ORSet₂)：
    A = A₁ ∪ A₂
    R = R₁ ∪ R₂

  直观："删除"不是删除元素，而是"隐藏"该元素的所有已见标签。
        并发添加会生成不同标签 → 不会被对方的删除覆盖。

半格验证：
  偏序：(A₁,R₁) ⊑ (A₂,R₂) ⟺ A₁⊆A₂ ∧ R₁⊆R₂
  合并：(A₁,R₁)⊔(A₂,R₂) = (A₁∪A₂, R₁∪R₂)
  集合并天然满足交换/结合/幂等 ✅
```

### 3.4 LWW-Register（最后写入赢寄存器）

```
应用场景：配置值、用户偏好设置（简单覆盖语义可接受时）

状态：(value, timestamp)

操作：
  - write(v)：timestamp = 当前逻辑时钟或物理时钟
  - read()：返回value
  - merge((v₁,t₁), (v₂,t₂))：
      若 t₁ > t₂ → 返回 (v₁,t₁)
      若 t₂ > t₁ → 返回 (v₂,t₂)
      若 t₁ = t₂ → 确定性消解（如按节点ID排序）

风险：
  "最后写入"由时钟决定，可能非直觉。
  物理时钟有漂移 → 需NTP或逻辑时钟。
  并发写入（相同timestamp）→ 需额外消解策略。
```

---

## 四、多维矩阵：CRDT类型对比

| CRDT类型 | 操作 | 半格合并 | 协调需求 | 适用场景 | 限制 |
|---------|------|---------|---------|---------|------|
| **G-Counter** | 仅increment | 逐元素max | 无 | PV/UV计数、API调用统计 | 不可减 |
| **PN-Counter** | increment/decrement | (P,N)分别max | 无 | 库存、票数 | 可能负值 |
| **G-Set** | 仅add | 集合并 | 无 | 去重ID集合、标签 | 不可删除 |
| **OR-Set** | add/remove | (A,R)集合并 | 无 | 购物车、协作收藏 | 存储膨胀（标签积累） |
| **LWW-Register** | write | 取最大timestamp | 无 | 配置、偏好设置 | 并发写丢失数据 |
| **MV-Register** | write | 合并并发版本 | 无 | 需要保留并发写的场景 | 客户端需处理多版本 |
| **RGA序列** | insert/delete | 基于树/图的合并 | 无 | 协同编辑、有序列表 | 实现复杂度高 |
| **LWW-Element-Set** | add/remove | 元素级LWW | 无 | 简单集合（可接受LWW语义） | 并发add/remove可能非预期 |

---

## 五、State-based vs Op-based CRDT

| 维度 | **State-based** | **Op-based** |
|------|----------------|-------------|
| **传播单元** | 完整状态（或Delta） | 操作（Update） |
| **网络要求** | 任何消息传递（允许丢失、重复、乱序） | 需要可靠广播（因果顺序或全序） |
| **带宽效率** | 低（完整状态大）或中（Delta优化） | 高（仅传播操作） |
| **实现复杂度** | 低（仅需merge函数） | 中（需处理操作幂等/顺序） |
| **容错性** | 高（丢失消息可重试，幂等保证） | 中（依赖广播层可靠性） |
| **垃圾回收** | 需处理状态膨胀 | 需处理操作日志膨胀 |
| **2026趋势** | Delta-State CRDT（Delta CRDT） | Pure Operation-Based with Anti-Entropy |

---

## 六、概念定义与属性关系

| 概念 | 定义 | 属性 | 示例 | 反例 |
|------|------|------|------|------|
| **Join-Semilattice** | 带有偏序和最小上界运算的代数结构，且⊔满足交换/结合/幂等律 | 保证收敛性、无冲突合并、顺序无关 | (ℕ, ≤, max) 是自然数上的半格 | (ℕ, +) 不是半格（不满足幂等） |
| **强最终一致性**（SEC） | 无新更新时所有副本收敛，且收敛结果与接收顺序无关 | 无需协调、高可用、低延迟 | CRDT购物车跨设备同步 | 普通最终一致（需外部冲突解决） |
| **协调自由**（Coordination-Free） | 副本本地处理更新无需等待其他副本 | 无单点瓶颈、分区时完全可用、线性扩展 | G-Counter增量 | 线性一致读写（需要Quorum协调） |
| **Delta-State CRDT** | 仅传播状态差分而非完整状态的优化 | 带宽效率接近Op-based，但保持State-based的容错性 | Riak 2.0的CRDT实现 | 原始State-based（传播完整状态） |
| **tombstone** | 标记已删除元素但保留其元信息的记录 | 防止已删除数据复活、导致存储膨胀 | OR-Set中的R集合 | 物理删除（导致并发添加时数据复活） |

---

## 七、交叉引用

- → [04-总览](./00-总览-从直觉到半格理论.md)
- → [04/02-向量时钟](02-向量时钟与偏序集-HappensBefore关系.md)
- → [04/03-EventSourcing](03-EventSourcing-不可变数据代数与版本诅咒.md)
- ↓ [02/04-一致性光谱](../../02-分布式系统不可能性与权衡定理/04-一致性模型光谱-从严格一致到最终一致.md)
- ↓ [03/02-Raft](../../03-分布式共识算法完整谱系/02-Raft-状态机复制与模块化工程化.md)
- ↑ [00/05-元认知批判](../../00-元认知与系统思维框架/05-元认知批判-模型的隐含假设与失效条件.md)

---

## 八、参考文献

| 作者 | 标题 | 出处 | 年份 |
|------|------|------|------|
| Marc Shapiro et al. | "A Comprehensive Study of Convergent and Commutative Replicated Data Types" | INRIA | 2011 |
| Nuno Preguiça et al. | "Delta State Replicated Data Types" | *Journal of Parallel and Distributed Computing* | 2016 |
| Carlos Baquero et al. | "Pure Operation-Based Replicated Data Types" | *ArXiv* | 2017 |
| Marc Shapiro et al. | "Conflict-free Replicated Data Types" | *SSS* | 2011 |
| Sebastian Burckhardt | "Principles of Eventual Consistency" | *Foundations and Trends in Programming Languages* | 2014 |
| Mihai Letia et al. | "Causality Tracking in Causal Message Logging Protocols" | *ACM Computing Surveys* | 2022 |
| Riak Docs | "Data Types" (Basho/RIAK) | docs.riak.com | 持续更新 |

---

*文件创建日期：2026-04-23*
*状态：已完成*
