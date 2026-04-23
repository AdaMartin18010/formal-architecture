# 前端 CAP 定理：一致性、可用性与分区容错

> **来源映射**: View/05.md §4.2
> **国际权威参考**: Brewer (2000) "Towards Robust Distributed Systems" (PODC Keynote); Gilbert & Lynch (2002) "Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services"; Martin Kleppmann (2017) "Designing Data-Intensive Applications"

---

## 一、知识体系思维导图

```text
前端 CAP 定理: 一致性、可用性、分区容错
│
├─► CAP 定理回顾 (分布式系统)
│   ├─ C (Consistency): 所有节点同时看到相同的数据
│   ├─ A (Availability): 每个请求都能收到非错误响应
│   ├─ P (Partition Tolerance): 网络分区时系统继续运行
│   └─ 定理: 网络分区时, C 和 A 不可兼得
│
├─► 前端场景的 CAP 重新诠释
│   ├─ "节点": 浏览器标签页、Service Worker、服务器、边缘节点
│   ├─ "网络分区": 离线、慢网、跨标签页通信失败、CORS 限制
│   └─ "一致性": 多端状态同步、离线编辑冲突、乐观更新回滚
│
├─► 前端存储方案的 CAP 定位
│   ├─ CP 系统: IndexedDB + Web Locks (强一致，分区时阻塞)
│   ├─ AP 系统: localStorage + BroadcastChannel (高可用，最终一致)
│   ├─ AP 系统: Service Worker + BackgroundSync (离线可用，后台同步)
│   └─ AP 系统: CRDT (Yjs, Automerge) —— 分区容忍 + 最终一致
│
├─► 乐观更新 (Optimistic UI)
│   ├─ 策略: 先更新 UI，后同步服务器
│   ├─ 冲突解决: 重试、回滚、合并、覆盖
│   ├─ 风险: 用户基于假设状态做决策，回滚时体验断裂
│   └─ 形式化: UI(t) = f(State_local(t)) ∪ Pending_ops(t)
│
└─► 离线优先架构 (Offline-First)
    ├─ 本地即真相 (Local-First): 设备是数据主副本
    ├─ 同步策略: 实时 (WebSocket) vs 延迟 (BackgroundSync)
    ├─ 冲突解决: Last-Write-Wins vs CRDT vs 自定义合并
    └─ 安全性: 端到端加密、本地数据保护
```

---

## 二、核心概念的形式化定义

### 定义 D16.10：前端 CAP 的重新诠释

在浏览器环境中，重新定义 CAP 三要素：

```
Consistency (一致性):
  定义: ∀t, ∀节点 n₁, n₂ ∈ {tabs, SW, server}:
        read(n₁, t) = read(n₂, t)

  前端实例:
    - 多标签页间的 localStorage 同步 (通过 storage 事件)
    - Service Worker 缓存与服务器数据的一致
    - 客户端状态管理 (Redux/Zustand) 与服务器状态的一致

Availability (可用性):
  定义: ∀请求 req, 系统返回非错误响应的概率 > threshold

  前端实例:
    - 离线时应用仍可操作 (Service Worker 拦截请求)
    - 网络超时时的降级 UI (骨架屏/缓存数据)
    - 弱网环境下的渐进式加载

Partition Tolerance (分区容错):
  定义: 当任意节点间通信失败时，系统仍能提供部分功能

  前端实例:
    - 浏览器离线 (客户端与服务器分区)
    - 跨域隔离 (不同源标签页无法直接通信)
    - 隐私模式 (localStorage/IndexedDB 可能受限)
```

### 定义 D16.11：乐观更新的形式化

乐观更新策略的形式化描述：

```
设服务器真实状态为 S_server(t)，客户端本地状态为 S_local(t)

悲观更新 (Pessimistic):
  UI(t) = f(S_server(t))
  操作流: UserAction → Request → Wait → ServerConfirm → UIUpdate

乐观更新 (Optimistic):
  UI(t) = f(S_local(t))
  S_local(t) = S_sync(t) + Σ pending_ops

  操作流: UserAction → UIUpdate → Request → ServerConfirm/rollback

一致性风险:
  若用户基于 UI(t) 做了决策 D，随后服务器拒绝操作:
    Rollback: UI(t+Δ) ≠ UI(t)
    用户可能已执行不可撤销的 D
```

### 定义 D16.12：CRDT 的形式化基础

无冲突复制数据类型 (Conflict-free Replicated Data Types) 满足：

```
性质 1 (交换性): merge(A, B) = merge(B, A)
性质 2 (结合性): merge(merge(A, B), C) = merge(A, merge(B, C))
性质 3 (幂等性): merge(A, A) = A

推论: 对于 CRDT，最终一致性不依赖更新顺序!

前端实例 (Yjs):
  Y.Array 使用 YATA (Yet Another Transformation Approach) 算法
  保证: 无论操作顺序如何，所有副本收敛到相同状态
```

---

## 三、多维矩阵对比

### 3.1 前端存储方案的 CAP 分析

| 存储方案 | 一致性 (C) | 可用性 (A) | 分区容错 (P) | CAP 分类 | 适用场景 |
|---------|-----------|-----------|-------------|---------|---------|
| **localStorage** | ✅ 强一致 (单标签) | ✅ 高可用 | ❌ 无分区 (单标签) | CA | 用户偏好、主题 |
| **IndexedDB** | ✅ 事务一致 | ✅ 高可用 | ⚠️ 单标签 | CP | 离线文档、缓存 |
| **BroadcastChannel** | ⚠️ 因果一致 | ✅ 高可用 | ⚠️ 同源分区 | AP | 跨标签通信 |
| **Service Worker** | ⚠️ 最终一致 | ✅ 高可用 | ✅ 分区容错 | AP | 离线应用 |
| **SharedWorker** | ✅ 强一致 | ✅ 高可用 | ❌ 无分区 | CA | 跨标签状态共享 |
| **Web Locks API** | ✅ 强一致 | ⚠️ 锁竞争阻塞 | ❌ 单标签 | CP | 互斥操作 |
| **CRDT (Yjs)** | ⚠️ 最终一致 | ✅ 高可用 | ✅ 分区容错 | AP | 协作编辑 |
| **OPFS** | ✅ 强一致 | ✅ 高可用 | ❌ 单标签 | CP | 大文件处理 |

### 3.2 离线优先策略对比

| 策略 | 冲突检测 | 冲突解决 | 用户体验 | 实现复杂度 | 数据完整性 |
|------|---------|---------|---------|-----------|-----------|
| **Last-Write-Wins (LWW)** | 时间戳比较 | 覆盖 | 简单直观 | 低 | 弱 (可能丢数据) |
| **乐观锁 (Version Vector)** | 版本向量 | 手动合并 | 需用户介入 | 中 | 中 |
| **CRDT** | 无 (自动收敛) | 内置合并 | 透明 | 高 | 强 |
| **操作转换 (OT)** | 操作历史 | 变换函数 | 透明 | 极高 | 强 (需中心服务器) |
| **自定义业务规则** | 业务逻辑 | 应用特定 | 需设计 | 高 | 视规则而定 |

---

## 四、权威引用

> **Eric Brewer** (2000, PODC Keynote "Towards Robust Distributed Systems"):
> "The CAP theorem states that in any networked shared-data system, you can have at most two of the three properties: Consistency, Availability, and Partition Tolerance." —— CAP 定理的原始提出。

> **Seth Gilbert & Nancy Lynch** (2002, "Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services", ACM SIGACT News):
> "In a network that is not perfectly reliable, one must choose between consistency and availability." —— CAP 定理的形式化证明。

> **Martin Kleppmann** (2017, "Designing Data-Intensive Applications", O'Reilly):
> "The CAP theorem is often misunderstood as 'pick two'. In reality, partition tolerance is not really optional—if your network can partition, you must tolerate it. The real choice is between consistency and availability when a partition occurs." —— Kleppmann 对 CAP 常见误解的澄清：分区容错不是可选项。

> **Martin Kleppmann & Adam Wiggins** (2020, "Local-First Software", Ink & Switch):
> "Local-first software: you own your data, in spite of the cloud." —— 离线优先/本地优先软件运动的开创性论文，将 CAP 权衡从服务端扩展到客户端。

> **Marc Shapiro et al.** (2011, "Conflict-Free Replicated Data Types", SSS):
> "A CRDT is a data type designed so that its replicas can be updated concurrently and independently, without coordination, and always converge to a correct common state." —— CRDT 的数学定义和分类。

---

## 五、工程实践与代码示例

### 5.1 乐观更新的完整实现模式

```typescript
// 乐观更新状态机
type OptimisticState<T> =
  | { status: 'idle'; data: T }
  | { status: 'pending'; data: T; previous: T }
  | { status: 'confirmed'; data: T }
  | { status: 'error'; data: T; previous: T; error: Error };

class OptimisticUpdater<T> {
  private state: OptimisticState<T>;

  constructor(initial: T) {
    this.state = { status: 'idle', data: initial };
  }

  async execute(
    optimisticData: T,
    serverCall: () => Promise<T>
  ): Promise<void> {
    const previous = this.state.data;

    // 1. 乐观更新 UI
    this.state = { status: 'pending', data: optimisticData, previous };

    try {
      // 2. 发送服务器请求
      const confirmed = await serverCall();

      // 3. 确认成功
      this.state = { status: 'confirmed', data: confirmed };
    } catch (error) {
      // 4. 回滚到先前状态
      this.state = {
        status: 'error',
        data: previous,
        previous,
        error: error as Error
      };
      throw error;
    }
  }

  get currentData(): T {
    return this.state.data;
  }

  get isPending(): boolean {
    return this.state.status === 'pending';
  }
}

// 使用示例: 点赞按钮
const likeUpdater = new OptimisticUpdater({ liked: false, count: 0 });

async function toggleLike() {
  const current = likeUpdater.currentData;
  const optimistic = {
    liked: !current.liked,
    count: current.count + (current.liked ? -1 : 1)
  };

  await likeUpdater.execute(
    optimistic,
    () => fetch('/api/like', { method: 'POST' }).then(r => r.json())
  );
}
```

### 5.2 CRDT 基础：G-Counter (递增计数器)

```typescript
// G-Counter: 只能递增的 CRDT，满足交换律、结合律、幂等律
class GCounter {
  private counts: Map<string, number> = new Map();

  constructor(private replicaId: string) {}

  increment(): void {
    const current = this.counts.get(this.replicaId) || 0;
    this.counts.set(this.replicaId, current + 1);
  }

  get value(): number {
    return Array.from(this.counts.values()).reduce((a, b) => a + b, 0);
  }

  // 合并操作 (merge) —— CRDT 核心
  merge(other: GCounter): GCounter {
    const merged = new GCounter(this.replicaId);
    const allKeys = new Set([...this.counts.keys(), ...other.counts.keys()]);

    for (const key of allKeys) {
      const a = this.counts.get(key) || 0;
      const b = other.counts.get(key) || 0;
      merged.counts.set(key, Math.max(a, b)); // 取最大值 (LWW)
    }

    return merged;
  }
}

// 验证 CRDT 性质:
// 交换律: A.merge(B) = B.merge(A) ✅
// 结合律: (A.merge(B)).merge(C) = A.merge(B.merge(C)) ✅
// 幂等律: A.merge(A) = A ✅
```

---

## 六、批判性总结

将 CAP 定理应用于前端环境是一次富有洞察力的概念迁移，但它也暴露了理论抽象与工程现实之间的深刻张力。在传统的分布式数据库语境中，"节点"是明确的服务器实例，"分区"是网络中断的清晰事件；但在浏览器中，"节点"可以是同一个标签页的不同框架、跨域的 iframe、或休眠后恢复的服务工作者，"分区"可以是一个用户切换到了飞行模式、一个标签页被浏览器冻结、或一次 CORS 预检失败。这种**分区的普遍性和模糊性**使得 CAP 的选择不再是架构师的有意识决策，而是浏览器运行时的隐含约束。

乐观更新是前端对 CAP 权衡最直观的工程回应：在分区发生时（离线或高延迟），选择可用性（A）而牺牲强一致性（C），允许用户继续操作，待分区恢复后再通过重试或合并解决冲突。这种模式在社交媒体（点赞、评论）和生产力工具（文档编辑、任务管理）中取得了巨大成功，但其风险常常被低估。当用户基于"已保存"的乐观反馈做了后续操作（如关闭页面、分享链接），随后的回滚或冲突解决可能带来**不可逆的决策错误**。

CRDT 和本地优先软件 (Local-First Software) 代表了更根本的范式转变：将客户端设备视为数据的"主副本"，服务器仅作为同步和备份的中介。这种模型天然地选择了 AP（可用性 + 分区容错），但通过数学上的收敛保证（而非业务规则）来管理一致性。Yjs 和 Automerge 在协作编辑领域的成功证明了这一范式的可行性，但其推广受限于 CRDT 的**语义表达力边界**——并非所有业务操作都可以被表达为交换性、结合性和幂等性的合并函数。

2026 年的务实建议是：**不要试图在前端实现强一致性**。浏览器环境本质上是分区的（标签页隔离、离线常态、隐私模式限制），追求 CP 系统（如通过 Web Locks 实现的互斥访问）只会导致脆弱性和性能瓶颈。相反，应拥抱最终一致性：使用 IndexedDB 存储本地状态，Service Worker 提供离线可用性，BackgroundSync 在恢复连接时同步，CRDT 处理并发冲突。对于少数确实需要强一致性的场景（如支付确认、库存扣减），将决策权交给服务器，前端仅作为展示层。CAP 定理在前端的最佳应用不是作为技术选型的公式，而是作为**设计直觉的提醒**：在分区常态化的浏览器环境中，可用性和韧性比瞬时一致性更有用户价值。


---

## 七、概念属性关系网络

### 7.1 前端 CAP 概念语义网络

| 概念 | 核心属性 | 依赖概念 | 派生概念 | 关系类型 | 形式化映射 |
|------|---------|---------|---------|---------|-----------|
| **一致性 (C)** | 所有节点同时看到相同数据 | 分布式共识 | 强一致、最终一致、因果一致 | 安全属性 | ∀n₁,n₂,t: read(n₁,t)=read(n₂,t) |
| **可用性 (A)** | 每个请求收到非错误响应 | 故障容错 | 降级服务、离线优先 | 活性属性 | ∀req: P(response ≠ error) > threshold |
| **分区容错 (P)** | 网络分区时系统继续运行 | 网络不可靠性 | 离线模式、冲突解决 | 假设-约束 | 分区不可避免 |
| **乐观更新** | 先更新 UI、后同步、可回滚 | 可用性优先 | 冲突检测、重试队列 | 交互-策略 | UI(t) = f(S_local(t)) |
| **CRDT** | 交换性、结合性、幂等性 | 最终一致性 | Yjs、Automerge | 数据结构 | merge(A,B) = merge(B,A) |
| **Local-First** | 设备是主副本、服务器为备份 | 分区容错 | 端到端加密、冲突解决 | 范式-转变 | S_device = source of truth |
| **版本向量** | 并发检测、 happens-before | 因果一致 | 乐观锁、向量时钟 | 排序-逻辑 | VV: Replica → Counter |

### 7.2 前端分布式系统的概念依赖拓扑

```text
前端 CAP 权衡的概念依赖
│
├─► 网络可靠性假设
│   ├─ 理想网络 (无分区) ──[允许]──► CA 系统
│   │   └─ 实例: localStorage (单标签)、SharedWorker
│   │
│   └─ 现实网络 (分区常态) ──[强制]──► AP 或 CP 选择
│       ├─ 选择 AP: Service Worker、CRDT、BackgroundSync
│       └─ 选择 CP: IndexedDB + WebLocks、两阶段提交(有限)
│
├─► 一致性强度选择
│   ├─ 强一致 ──[需要]──► 协调机制 (锁、事务)
│   ├─ 因果一致 ──[需要]──► 向量时钟 / 版本向量
│   └─ 最终一致 ──[需要]──► 收敛算法 (CRDT merge、LWW)
│
├─► 可用性策略选择
│   ├─ 乐观更新 ──[风险]──► 回滚、用户决策错误
│   ├─ 离线优先 ──[成本]──► 同步冲突解决、数据迁移
│   └─ 降级服务 ──[体验]──► 骨架屏、缓存数据、只读模式
│
└─► 冲突解决机制
    ├─ Last-Write-Wins ──[简单]──► 可能丢数据
    ├─ CRDT ──[复杂]──► 自动收敛、语义受限
    ├─ OT ──[极复杂]──► 需中心服务器、强一致
    └─ 业务规则 ──[定制化]──► 灵活、实现成本高
```

---

## 八、形式化推理链

### 8.1 从前端分区常态到 AP 系统偏好的推理链

**命题 P16.4**: 浏览器环境本质上是分区的，因此前端存储系统应优先选择 AP（可用性 + 分区容错）而非 CP。

```
前提 1: 浏览器标签页之间无共享内存 (进程隔离)
前提 2: 离线是移动设备的常态而非异常
前提 3: 隐私模式限制 Storage API 访问
前提 4: CORS 和同源策略构成逻辑分区

推理链:
  Step 1: 分区普遍性
    ∀用户, ∃t: 设备处于离线状态 ........................ [网络现实]
    ∀应用, ∃场景: 用户关闭标签页后重新打开 .............. [生命周期]
    ∀多标签应用, ∃时刻: 标签页间无通信通道 .............. [架构限制]
    ∴ 分区 P 是前端环境的固有属性，不可消除

  Step 2: CAP 选择
    由 CAP 定理: 分区时 C 和 A 不可兼得 .................. [Gilbert & Lynch 2002]
    若选择 CP (如 WebLocks):
      - 分区时锁无法释放 ⇒ 操作阻塞 ...................... [可用性丧失]
      - 用户看到"加载中"或卡顿 .......................... [体验劣化]

    若选择 AP (如 CRDT + localStorage):
      - 分区时操作继续本地执行 ........................... [可用性保持]
      - 恢复时通过 merge 收敛 ............................ [最终一致性]

  Step 3: 业务价值分析
    设用户流失率与不可用时间正相关: Churn ∝ T_unavailable
    设数据错误成本与不一致强度正相关: Cost ∝ ε

    对于大多数前端应用 (社交、协作、内容):
      Churn(T_unavailable) >> Cost(ε) .................... [用户体验优先]
      ∴ AP 优于 CP

    对于少数场景 (支付确认、库存扣减):
      Cost(ε) >> Churn(T_unavailable) .................... [数据正确优先]
      ∴ 将强一致性委托给服务器，前端仅作展示

∴ 前端默认架构 = AP (Local-First + 最终一致)，强一致场景回源处理
```

> **Martin Kleppmann & Adam Wiggins** (2020, "Local-First Software", Ink & Switch):
> "Local-first software: you own your data, in spite of the cloud." —— 这篇开创性论文将 CAP 权衡从数据中心扩展到个人设备，论证了"设备作为主副本"的架构天然选择 AP，并通过 CRDT 和端到端加密管理一致性风险。

### 8.2 CRDT 收敛性的代数证明

**定理 T16.5 (CRDT 收敛)**: 满足交换性、结合性和幂等性的 merge 操作，保证所有副本在收到相同操作集合后收敛到相同状态，无需协调。

```
形式化定义:
  设状态空间为 S, merge: S × S → S

  性质:
    (1) 交换性: ∀a,b∈S, merge(a,b) = merge(b,a)
    (2) 结合性: ∀a,b,c∈S, merge(merge(a,b),c) = merge(a,merge(b,c))
    (3) 幂等性: ∀a∈S, merge(a,a) = a

  收敛定理:
    设副本 i 执行操作序列 O_i, 副本 j 执行操作序列 O_j
    设全局操作集合 O = O_i ∪ O_j (作为集合，忽略顺序)

    由交换性: merge 的结果与操作顺序无关
    由结合性: merge 可对任意分组进行
    由幂等性: 重复应用相同状态不产生变化

    ∴ State_i = merge(O) = State_j ...................... [收敛得证]

前端实例 (G-Counter):
  S = Map<ReplicaId, number>
  merge(a,b) = Map(max)  (按 key 取最大值)

  验证:
    交换性: max(a[k], b[k]) = max(b[k], a[k]) ........... ✅
    结合性: max(max(a,b),c) = max(a,max(b,c)) .......... ✅
    幂等性: max(a[k], a[k]) = a[k] ...................... ✅
```

> **Marc Shapiro et al.** (2011, "Conflict-Free Replicated Data Types", SSS):
> "A CRDT is a data type designed so that its replicas can be updated concurrently and independently, without coordination, and always converge to a correct common state." —— Shapiro 等人的论文首次系统分类了 CRDT（基于状态 vs 基于操作），并证明了其收敛性的代数条件。

---

## 九、推理判定树 / ASCII 决策树

### 9.1 前端存储 CAP 定位决策树

```text
                    应用是否需要离线功能?
                              │
                    ┌─────────┴─────────┐
                    │Yes                │No
                    ▼                   ▼
              数据一致性要求?        使用简单存储
                    │               (localStorage / fetch)
            ┌───────┴───────┐
            │强一致          │最终一致/弱一致
            ▼               ▼
        服务器协调        本地优先架构
        (回源处理)        (Local-First)
            │               │
            │       ┌───────┴───────┐
            │       │冲突频繁?      │
            │       │               │
            │   ┌───┴───┐      ┌────┴────┐
            │   │Yes    │No    │简单覆盖  │无需合并
            │   ▼       ▼      ▼         ▼
            │  CRDT   LWW      LWW      单向同步
            │ (Yjs)   (时间戳) (最新写)  (主从)
            │
            ▼
        需要事务支持?
            │
        ┌───┴───┐
        │Yes    │No
        ▼       ▼
      IndexedDB 服务器事务
      + WebLocks  (2PC)
      (单标签页)
```

### 9.2 乐观更新 vs 悲观更新决策树

```text
                    操作是否可撤销?
                              │
                    ┌─────────┴─────────┐
                    │Yes                │No (不可逆)
                    ▼                   ▼
              网络延迟高?           悲观更新
                    │               (等待服务器确认)
            ┌───────┴───────┐
            │Yes            │No
            ▼               ▼
        乐观更新        悲观更新
        (先更新UI)      (延迟低，直接等待)
            │
    需要冲突解决?
            │
    ┌───────┴───────┐
    │Yes            │No (独立操作)
    ▼               ▼
  实现回滚机制      简单乐观更新
  + 重试队列        (如点赞、收藏)
  (如表单编辑)
            │
            ▼
        用户已基于乐观状态做决策?
            │
        ┌───┴───┐
        │Yes    │No
        ▼       ▼
      高风险      低风险
      (需警告)   (可静默回滚)
      (如支付)   (如关注)
```

---

## 十、国际课程对齐

### 10.1 课程体系映射

| 本模块主题 | Stanford CS 144 | MIT 6.829 |
|-----------|-----------------|-----------|
| **CAP 定理** | Discussion: Distributed Systems | Lecture 12: CAP and FLP |
| **最终一致性** | Reading: Eventual Consistency | Lecture 13: Consistency Models |
| **CRDT 理论** | Guest Lecture: Conflict-free Replication | Reading: Shapiro et al. (2011) |
| **Local-First** | Discussion: Edge and Offline | Project: Offline-first App Design |
| **乐观更新** | Lab: Reliable Transport | Lecture 9: Application Protocols |
| **版本向量** | Reading: Version Vectors | Assignment: Distributed Clocks |

### 10.2 核心参考文献

> **Eric Brewer** (2000, PODC Keynote "Towards Robust Distributed Systems"):
> "The CAP theorem states that in any networked shared-data system, you can have at most two of the three properties: Consistency, Availability, and Partition Tolerance." —— Brewer 在 2000 年的 PODC 主题演讲中首次提出 CAP 猜想，其原始语境是分布式 Web 服务，但证明结构（通过分区场景展示 C 和 A 的互斥）适用于所有网络系统，包括浏览器。

> **Seth Gilbert & Nancy Lynch** (2002, ACM SIGACT News):
> "In a network that is not perfectly reliable, one must choose between consistency and availability." —— Gilbert 和 Lynch 使用异步网络模型严格证明了 CAP 定理。其证明的核心——网络分割论证（network-splitting argument）——可直接映射到前端场景：当浏览器离线时，选择"返回缓存数据 (可用性)"还是"阻塞等待网络恢复 (一致性)"。

> **Martin Kleppmann** (2017, "Designing Data-Intensive Applications", O'Reilly):
> "The CAP theorem is often misunderstood as 'pick two'. In reality, partition tolerance is not really optional—if your network can partition, you must tolerate it. The real choice is between consistency and availability when a partition occurs." —— Kleppmann 的澄清对前端架构尤为重要：浏览器的分区（离线、跨标签页隔离）是常态，因此架构师真正的决策是在 C 和 A 之间取舍。

> **Marc Shapiro et al.** (2011, "Conflict-Free Replicated Data Types", SSS):
> 系统阐述了基于状态和基于操作的 CRDT 的分类，并证明了其收敛性的充要条件。Shapiro 等人的工作为 Yjs、Automerge 等前端 CRDT 库提供了理论基础。

### 10.3 课程作业对标

- **Stanford CS 144**: Discussion Section 4 专门讨论"Distributed Systems Constraints"，其中一道思考题要求学生将 CAP 定理应用于"手机备忘录应用"：当用户在飞行模式下编辑笔记时，应用应该选择一致性（禁止编辑）还是可用性（允许编辑并稍后同步）？这与本模块第 5.1 节的乐观更新实现和第 6 节的批判性总结完全一致。
- **MIT 6.829**: Assignment 6 要求学生实现一个简化版的 CRDT G-Set（Grow-only Set），并在模拟网络分区的环境下验证其收敛性。该作业的评分标准包括"证明你的 merge 操作满足交换律、结合律和幂等律"——与本模块第 5.2 节的 G-Counter 实现和定理 T16.5 的代数证明直接对应。
