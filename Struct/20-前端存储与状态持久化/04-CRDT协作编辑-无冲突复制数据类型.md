# CRDT 协作编辑：无冲突复制数据类型

> **来源映射**: View/03.md §3.2
> **国际权威参考**: "A Comprehensive Study of Convergent and Commutative Replicated Data Types" (Shapiro et al., 2011), Yjs Documentation

---

## 一、知识体系思维导图

```text
CRDT: 无冲突复制数据类型
│
├─► 问题背景
│   ├─ 多用户同时编辑同一文档
│   ├─ 网络延迟 / 离线编辑 / 冲突解决
│   ├─ OT (Operational Transformation): 复杂、需中央服务器
│   └─ CRDT: 去中心化、最终一致、无需转换
│
├─► CRDT 核心性质
│   ├─ 交换律 (Commutativity): a ⊔ b = b ⊔ a
│   ├─ 结合律 (Associativity): (a ⊔ b) ⊔ c = a ⊔ (b ⊔ c)
│   ├─ 幂等律 (Idempotence): a ⊔ a = a
│   └─ 最终一致性: 所有副本收到相同操作集 → 状态相同
│
├─► CRDT 分类
│   ├─► State-based (CvRDT)
│   │   ├─ 传输完整状态
│   │   ├─ 合并函数: merge(state₁, state₂) → new_state
│   │   └─ 适用: 网络不稳定、状态小
│   │
│   └─► Operation-based (CmRDT)
│       ├─ 传输操作
│       ├─ 要求操作满足交换律
│       └─ 适用: 网络稳定、状态大
│
├─► 常见 CRDT 类型
│   ├─ G-Counter (增长计数器): 每个节点只增自己的计数器
│   ├─ PN-Counter (正负计数器): 两个 G-Counter 组合
│   ├─ G-Set (增长集合): 只增不减
│   ├─ OR-Set (观察移除集合): 用唯一标记实现删除
│   ├─ LWW-Register (最后写入胜): 时间戳决定最终值
│   ├─ MV-Register (多值寄存器): 并发写入保留所有值
│   └─ YATA / RGA: 文本序列 CRDT
│
└─► 文本协作 CRDT
    ├─ Yjs: YATA 算法，高效内存使用
    ├─ Automerge: JSON CRDT，文档即状态
    └─ 冲突解决: 并发插入 → 基于 Origin 和 ID 排序
```

---

## 二、核心概念的形式化定义

### 2.1 CRDT 公理

```text
定义 (CRDT):
  状态型 CRDT (CvRDT):
    S: 状态集合
    merge: S × S → S (偏序集的并/上确界)

    公理:
      1. 交换律: merge(a, b) = merge(b, a)
      2. 结合律: merge(merge(a, b), c) = merge(a, merge(b, c))
      3. 幂等律: merge(a, a) = a

    更新:
      update: S × Op → S
      更新后状态传播到其他副本，通过 merge 合并

  操作型 CRDT (CmRDT):
    Op: 操作集合
    apply: S × Op → S

    公理:
      ∀op₁, op₂ ∈ Op:
        apply(apply(s, op₁), op₂) = apply(apply(s, op₂), op₁)

    即: 操作应用顺序不影响最终状态
```

### 2.2 文本序列 CRDT (YATA)

```text
定义 (YATA 文本 CRDT):
  字符表示:
    c = ⟨id, origin, content⟩
    id: 全局唯一标识 (node_id, sequence_number)
    origin: 左邻字符的 id

  插入操作:
    insert(pos, content) → 生成新字符 c
    c.origin = document[pos-1].id  // 记录左邻

  并发插入排序:
    若两个字符 c₁, c₂ 有相同 origin:
      按 (node_id, sequence_number) 字典序排序

  删除操作:
    逻辑删除: 标记字符为已删除 (墓碑)
    不物理移除，以保持 origin 引用有效

  内存优化:
    状态向量 (State Vector): 每个节点的已接收操作计数
    可安全删除已知所有副本都接收的操作历史
```

### 2.3 CRDT 的半格与偏序集语义

```text
定义 (CRDT 的代数结构):
  状态型 CRDT 的状态集合 S 配备偏序 ≤，形成 join-半格:

  偏序 ≤:
    a ≤ b ⟺ merge(a, b) = b
    即: a 是 b 的"子状态"

  半格性质:
    1. 交换律: a ⊔ b = b ⊔ a
    2. 结合律: (a ⊔ b) ⊔ c = a ⊔ (b ⊔ c)
    3. 幂等律: a ⊔ a = a
    4. 最小元: ⊥ (空状态), ⊥ ⊔ a = a

  单调性:
    所有操作都是单调的: apply(s, op) ≥ s
    因此状态永不"回退"

  收敛定理:
    若所有副本最终收到相同的操作集 (可能顺序不同)
    则所有副本的状态收敛到该操作集的上确界
    ⊔{apply(⊥, op₁), apply(⊥, op₂), ...} = s_final
```

### 2.4 Delta-State CRDT 与带宽优化

```text
定义 (Delta-State CRDT):
  传统 State-based CRDT: 传输完整状态，带宽 O(|state|)
  Delta-State CRDT: 仅传输状态差异 δ

  形式化:
    设副本状态 s，执行操作 op 后:
      s' = apply(s, op)
      δ(s, s') = s' \ s  (集合差，或半格意义上的差异)

    传输: 广播 δ 而非 s'
    合并: s_recv ⊔ δ = s_recv ⊔ s' (由结合律保证)

  优势:
    - 带宽与操作复杂度成正比，而非状态大小
    - 对于大文档中的小修改，δ 极小

  Yjs 实现:
    Y.encodeStateAsUpdate(ydoc, remoteStateVector)
    → 仅编码 remoteStateVector 之后的新操作
```

---

## 三、CRDT vs OT 对比矩阵

| 维度 | OT (Operational Transformation) | CRDT |
|------|--------------------------------|------|
| **中央服务器** | **必需** | 可选 (P2P) |
| **冲突解决** | 变换操作以维持一致性 | 数学性质保证无冲突 |
| **离线支持** | 困难 | **原生支持** |
| **实现复杂度** | **高** (变换函数复杂) | 中 |
| **内存开销** | 低 | 高 (墓碑、历史) |
| **可扩展性** | 受中央服务器限制 | **水平扩展** |
| **代表实现** | Google Docs (早期), Etherpad | Yjs, Automerge, Figma |
| **适用场景** | 中心化文档编辑 | 分布式协作、P2P、边缘计算 |

---

## 四、权威引用

> **Marc Shapiro** et al. (INRIA, 2011):
> "A Comprehensive Study of Convergent and Commutative Replicated Data Types." —— CRDT 的奠基论文。

> **Martin Kleppmann** ("Designing Data-Intensive Applications"):
> "CRDTs are a family of data structures that can be replicated across multiple computers in a network, where replicas can be updated independently and concurrently without coordination."

> **Kevin Jahns** (Yjs 作者):
> "Yjs doesn't just synchronize text; it synchronizes any shared data structure with sub-second latency over any network."

---

## 五、工程实践

### 5.1 Yjs 协作编辑

```javascript
import * as Y from 'yjs';
import { WebsocketProvider } from 'y-websocket';

// 创建文档
const ydoc = new Y.Doc();

// 创建共享文本类型
const ytext = ydoc.getText('my-text');

// 绑定到编辑器 (如 ProseMirror, Monaco, Quill)
const provider = new WebsocketProvider(
  'wss://demo.yjs.dev',
  'my-document-room',
  ydoc
);

// 本地修改自动同步
ytext.insert(0, 'Hello, collaborative world!');

// 监听远程修改
ytext.observe(() => {
  console.log('Document updated:', ytext.toString());
});
```

### 5.2 CRDT 内存优化

```javascript
// 状态向量用于垃圾回收
const stateVector = Y.encodeStateAsUpdate(ydoc);

// 只发送差异
const diff = Y.encodeStateAsUpdate(ydoc, remoteStateVector);

// 合并更新
Y.applyUpdate(ydoc, diff);
```

### 5.3 Automerge 的持久化与二进制格式

```javascript
import * as Automerge from '@automerge/automerge';

// 创建文档
let doc = Automerge.init();
doc = Automerge.change(doc, (d) => {
  d.title = 'Project Plan';
  d.tasks = [];
});

// 序列化为二进制 (高效压缩)
const binary = Automerge.save(doc);
console.log(`Binary size: ${binary.length} bytes`);

// 从二进制恢复
const loaded = Automerge.load(binary);

// 增量同步: 仅传输差异
const syncState = Automerge.initSyncState();
const [newSyncState, message] = Automerge.generateSyncMessage(doc, syncState);
// 发送 message 到远端...

// 合并远端更新
const [updatedDoc, newSyncState2] = Automerge.receiveSyncMessage(
  doc, syncState, remoteMessage
);
```

---

## 六、批判性总结

CRDT 的核心洞察是**用数学换协调**：传统 OT 需要中央服务器来序列化和转换操作，而 CRDT 通过**交换律、结合律和幂等律**的数学保证，让各个副本独立处理操作，最终自动达成一致。这是**最终一致性**理论在协作编辑领域的工程胜利。

但 CRDT 的代价是**内存膨胀**：逻辑删除（墓碑机制）意味着历史数据永远不会真正消失，文档编辑历史越长，内存占用越大。Yjs 通过**状态向量垃圾回收**缓解了这个问题——当所有副本都确认收到某段历史后，这段历史可以被安全清除。但这引入了**可用性与一致性的新权衡**：过于激进的垃圾回收可能导致慢速副本永远丢失某些操作。

2026 年的趋势是**CRDT 与数据库的融合**：SQLite 的 CRDT 扩展、PostgreSQL 的分布式协作插件，让 CRDT 从"前端协作库"进化为"通用数据同步协议"。这验证了 Marc Shapiro 的原始愿景——CRDT 不是特定问题的解决方案，而是**分布式数据管理的基本原语**。

CRDT 的半格语义为其工程实现提供了**坚实的数学地基**：join-半格保证无论操作以何种顺序到达，合并结果总是唯一的上确界。这是 CRDT 与 ad-hoc 冲突解决方案的本质区别——后者依赖启发式规则（如"时间戳大的赢"），而 CRDT 依赖代数结构的数学必然性。Delta-State CRDT 是工程优化的里程碑：它将带宽消耗从 O(文档大小) 降低到 O(操作大小)，使 CRDT 在移动网络和边缘计算场景中具备了实用价值。Automerge 的二进制格式进一步将压缩率提升了 5-10 倍，使大型文档的初始同步从"不可行"变为"可接受"。但 CRDT 的**查询能力**仍是短板：与 SQL 的关系代数相比，CRDT 的文档模型在复杂查询和聚合分析上效率低下。这解释了为什么 CRDT 目前主要局限于协作编辑和简单键值同步，而非通用数据库替代方案。


---

## 七、概念属性关系网络

| 概念节点 | 核心属性 | 依赖节点 | 关联强度 | 形式化映射 |
|---------|---------|---------|---------|-----------|
| **CRDT 公理** | 交换律、结合律、幂等律 | 半格 (join-semilattice) | ★★★★★ | merge(a,b)=merge(b,a); merge(merge(a,b),c)=merge(a,merge(b,c)) |
| **CvRDT (状态型)** | 完整状态传输、merge 函数 | 偏序集 ≤、上确界 ⊔ | ★★★★★ | merge(a,b) = a ⊔ b |
| **CmRDT (操作型)** | 操作广播、apply 函数 | 操作交换律 | ★★★★★ | apply(apply(s,op₁),op₂) = apply(apply(s,op₂),op₁) |
| **YATA 文本 CRDT** | id, origin, content, 墓碑 | 字符排序、并发插入 | ★★★★★ | c = ⟨id, origin, content⟩ |
| **Delta-State** | 状态差异 δ、带宽优化 | 半格差分、状态向量 | ★★★★★ | δ(s,s') = s' \\ s |
| **收敛定理** | 操作集上确界、最终一致 | CRDT 公理、网络传播 | ★★★★★ | ⊔{apply(⊥,opᵢ)} = s_final |
| **OT (Operational Transformation)** | 中央服务器、操作变换 | 与 CRDT 形成对比 | ★★★★☆ | transform(op₁, op₂) → (op₁', op₂') |

**关系网络拓扑**：

```text
CRDT 公理 ←── 半格语义 ←── 收敛定理
      ↓              ↑              ↓
CvRDT ←────────→ CmRDT ←─────── Delta-State
      ↓              ↑              ↓
YATA 文本 CRDT ←── 状态向量 ──── 带宽优化
      ↓                           ↑
OT (对比方案) ───────────────── 工程选型
```

---

## 八、形式化推理链

**推理链 R1：从 CRDT 公理到收敛定理的演绎**

```text
前提:
  P1: 设状态集合 S 配备偏序 ≤，形成 join-半格 (S, ≤, ⊔)
  P2: CRDT 公理:
        (1) 交换律: a ⊔ b = b ⊔ a
        (2) 结合律: (a ⊔ b) ⊔ c = a ⊔ (b ⊔ c)
        (3) 幂等律: a ⊔ a = a
  P3: 所有操作单调: apply(s, op) ≥ s
  P4: 网络最终交付: ∀op, ∀replica r:  eventually r receives op

推导:
  Step 1: 半格与偏序的关系
    a ≤ b ⟺ a ⊔ b = b
    即: merge(a,b) = b ⟺ a 是 b 的子状态

  Step 2: 操作集的上确界存在性
    设所有副本执行的操作集为 O = {op₁, op₂, ..., opₙ}
    由于结合律和交换律，O 的上确界存在且唯一:
      s_final = ⊔_{op∈O} apply(⊥, op)
    操作顺序不影响最终结果

  Step 3: 单调性保证不回退
    ∀s, op: apply(s, op) ≥ s
    因此状态序列 s₀ ≤ s₁ ≤ s₂ ≤ ... 单调递增
    最终收敛到不动点: s_final = apply(s_final, op_any_new)

  Step 4: 收敛性证明
    设副本 r₁ 收到操作集 O₁, 副本 r₂ 收到操作集 O₂
    最终 O₁ = O₂ = O (网络最终交付假设)
    则: state(r₁) = ⊔_{op∈O₁} apply(⊥,op) = ⊔_{op∈O} apply(⊥,op) = state(r₂)
    ∴ 所有副本最终状态一致

结论 (定理 T-CRDT1 - 收敛定理):
  任何满足交换律、结合律和幂等律的状态型 CRDT，
  在操作单调且网络最终交付的条件下，保证强最终一致性 (Strong Eventual Consistency):
    ∀r₁, r₂: eventually (state(r₁) = state(r₂) = s_final)
  这是 CRDT 与 ad-hoc 冲突解决方案的本质区别——收敛性由代数结构保证，
  而非依赖启发式规则 (Shapiro et al., 2011)。
```

**推理链 R2：从 Delta-State 到带宽优化的量化分析**

```text
前提:
  P1: 设状态大小 |s| = N (如文档字符数)
  P2: 设单次操作 op 的影响范围 |δ(s, apply(s,op))| = k ≪ N
  P3: 传统 State-based CRDT 传输完整状态: bandwidth = O(N)

推导:
  Step 1: Delta-State 定义
    δ(s, s') = s' \\ s  (半格意义上的最小上界差)
    由结合律保证: s_recv ⊔ δ = s_recv ⊔ s'

  Step 2: 带宽分析
    传统: bandwidth = O(|s|) = O(N)
    Delta: bandwidth = O(|δ|) = O(k)
    优化比: R = N/k
    对于大文档中的小修改: R 可达 10³ ~ 10⁶

  Step 3: Yjs 实现细节
    Y.encodeStateAsUpdate(ydoc, remoteStateVector)
    → 仅编码 remoteStateVector 之后的新操作
    状态向量 SV 空间: O(N_replicas) = O(N)
    每次同步带宽: O(未接收操作数) ≪ O(文档大小)

  Step 4: Automerge 二进制压缩
    二进制格式压缩率 vs JSON: 5-10×
    增量同步消息: 仅包含差异操作 + 必要元数据

结论 (定理 T-CRDT2):
  Delta-State CRDT 的带宽复杂度从 O(|state|) 降至 O(|operation|):
    bandwidth(Δ-CRDT) = O(k) ≪ bandwidth(full-state) = O(N)
  这使得 CRDT 在移动网络和边缘计算场景中具备实用价值，
  但代价是状态向量存储开销 O(N_replicas) 和更复杂的垃圾回收逻辑。
```

---

## 九、推理判定树/决策树

```text
CRDT 协作编辑方案选型决策树
│
├─► 协作场景判定
│   ├─ [纯文本编辑] ──► Yjs (YATA 算法，内存高效)
│   ├─ [富文本文档] ──► Yjs + ProseMirror/Quill 绑定
│   ├─ [JSON 数据结构] ──► Automerge (文档即状态，二进制高效)
│   ├─ [表格/电子表格] ──► Yjs Array / 自定义序列 CRDT
│   └─ [图形/白板] ──► 自定义 CRDT (位置/属性独立合并)
│
├─► 网络拓扑判定
│   ├─ [中央服务器] ──► Y-websocket / Y-webrtc (星型拓扑)
│   ├─ [P2P 去中心化] ──► Y-webrtc + 信令服务器
│   └─ [混合模式] ──► 中央持久化 + P2P 实时同步
│
├─► 传输优化判定
│   ├─ [大文档 + 频繁小修改] ──► Delta-State CRDT (Yjs update)
│   ├─ [小文档 + 全量加载] ──► State-based (简单实现)
│   └─ [操作型网络] ──► CmRDT (操作广播，要求可靠传输)
│
├─► 持久化需求判定
│   ├─ [服务器持久化] ──► Yjs document update → 数据库存储
│   ├─ [本地离线编辑] ──► IndexedDB 存储 Yjs update 历史
│   └─ [版本历史] ──► 保留完整操作日志 (支持时间旅行)
│
└─► 冲突解决策略判定
    ├─ [文本并发编辑] ──► YATA/RGA 自动合并 (无需用户介入)
    ├─ [注册器并发写入] ──► LWW-Register (时间戳决胜)
    ├─ [计数器] ──► PN-Counter (正负分离，最终求和)
    └─ [集合] ──► OR-Set (观察移除，唯一标记)
```

---

## 十、国际课程对齐标注

| 核心内容 | 国际课程 | 章节/主题映射 | 对齐强度 |
|---------|---------|-------------|---------|
| CRDT 代数结构与收敛定理 | **Berkeley CS 162** Operating Systems | Distributed Systems, Replication, Consistency | ★★★★★ |
| 半格与偏序集语义 | **Berkeley CS 162** | Order Theory, Lattices (数学基础) | ★★★★☆ |
| 协作编辑与 OT/CRDT 对比 | **Stanford CS 142** Web Applications | Real-Time Collaboration, Data Synchronization | ★★★★☆ |
| 操作交换性与无冲突合并 | **Berkeley CS 162** | Concurrency, Commutativity, Atomic Operations | ★★★★★ |
| Delta-State 与带宽优化 | **Berkeley CS 162** | Network Efficiency, Incremental Updates | ★★★★☆ |
| 状态向量与垃圾回收 | **Berkeley CS 162** | Distributed Garbage Collection | ★★★★☆ |

> **权威来源说明**：
>
> - **Berkeley CS 162**（Operating Systems）在 Distributed Systems 模块系统讲授数据复制、一致性模型和分布式系统的数学基础，CRDT 的半格语义与该课程的一致性理论直接对应。
> - **Stanford CS 142**（Web Applications）在 Real-Time Collaboration 和数据同步模块中讲授协作编辑的工程实践，Yjs 和 Automerge 是该领域的前沿参考实现。
> - **Marc Shapiro et al.** (2011): "A Comprehensive Study of Convergent and Commutative Replicated Data Types." *Tech Report INRIA*. CRDT 的奠基论文，首次系统定义了 CvRDT 和 CmRDT 及其收敛定理。
> - **Martin Kleppmann** (2017): *Designing Data-Intensive Applications*. O'Reilly. 第 5 章系统阐述了 CRDT 在协作编辑和分布式状态管理中的应用。
> - **Kevin Jahns** (2020): "Yjs: A Framework for Near Real-Time P2P Shared Editing." 提出 YATA 算法和 Delta-State 优化，是 Yjs 库的理论基础。
> - **Nuno Preguiça et al.** (2009): "A Commutative Replicated Data Type for Cooperative Editing." *ICDCS*. 早期文本 CRDT (RGA) 的关键论文。
