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
