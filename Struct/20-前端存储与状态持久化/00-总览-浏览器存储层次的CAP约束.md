# 前端存储与状态持久化：总览

> **来源映射**: View/05.md §4
> **国际权威参考**: WHATWG Storage Standard, IndexedDB Spec, OPFS Spec

---

## 一、知识体系思维导图

```text
前端存储与状态持久化
│
├─► 存储层次结构 · 延迟-容量权衡
│   ├─ 定义: S = ⟨L, ≤, τ, cap⟩
│   │   L: 层级集合
│   │   ≤: 速度偏序
│   │   τ: 访问延迟函数
│   │   cap: 容量函数
│   │
│   ├─► L1: CPU Cache (~1ns, ~64KB, 易失) → JS 变量/闭包
│   ├─► L2: Heap (~100ns, ~1GB, 易失) → V8 Heap, WASM Memory
│   ├─► L3: SessionStorage (~1μs, ~5MB, 会话级)
│   ├─► L4: localStorage (~10μs, ~10MB, 永久用户可清除)
│   ├─► L5: IndexedDB (~1ms, ~1GB, 永久)
│   ├─► L6: OPFS (~5ms, ~磁盘容量, 永久)
│   ├─► L7: SQLite WASM (~10ms, ~2GB, 永久)
│   └─► L8: Network Storage (~100ms, ∞, 服务端控制)
│
├─► 状态同步的形式化
│   ├─ 设状态 s 在层级 Lᵢ 和 Lⱼ 的副本为 sᵢ, sⱼ
│   ├─ 强一致性: sᵢ = sⱼ, ∀t
│   ├─ 最终一致性: ◇(sᵢ = sⱼ)
│   └─ 因果一致性: if sᵢ → sⱼ (happens-before), then sᵢ ≤ sⱼ
│
└─► 前端 CAP 定理映射
    ├─ localStorage: CA 系统 (无分区)
    ├─ IndexedDB: CA 系统 (单标签)
    ├─ BroadcastChannel + localStorage: AP 系统 (因果一致)
    ├─ Service Worker + BackgroundSync: AP 系统 (最终一致)
    ├─ Web Locks API: CP 系统 (单标签)
    └─ CRDT (Yjs): AP 系统 (最终一致 + 冲突自动解决)
```

---

## 二、存储层次的形式化

| 层级 | 延迟 | 容量 | 持久性 | 前端 API |
|------|------|------|--------|---------|
| **L1: CPU Cache** | ~1ns | ~64KB | 易失 | JS 变量/闭包 |
| **L2: Heap** | ~100ns | ~1GB | 易失 | V8 Heap, WASM Memory |
| **L3: SessionStorage** | ~1μs | ~5MB | 会话级 | sessionStorage |
| **L4: localStorage** | ~10μs | ~10MB | 永久(用户可清除) | localStorage |
| **L5: IndexedDB** | ~1ms | ~1GB | 永久 | IndexedDB, idb-keyval |
| **L6: OPFS** | ~5ms | ~磁盘容量 | 永久 | Origin Private File System |
| **L7: SQLite WASM** | ~10ms | ~2GB | 永久 | sql.js, absurd-sql |
| **L8: Network** | ~100ms | ∞ | 服务端控制 | fetch, Cache API |

---

## 三、前端 CAP 约束矩阵

```text
定理 T6: 前端持久化状态系统最多同时满足 CAP 中的两项

┌─────────────────┬───────────┬───────────┬───────────┐
│    存储方案      │ 一致性(C) │ 可用性(A) │ 分区容错(P)│
├─────────────────┼───────────┼───────────┼───────────┤
│ localStorage    │ ✅ 强一致  │ ✅ 高可用  │ ❌ 无分区  │
│ IndexedDB       │ ✅ 事务一致│ ✅ 高可用  │ ⚠️ 单标签  │
│ BroadcastChannel│ ⚠️ 因果一致│ ✅ 高可用  │ ⚠️ 同源分区│
│ Service Worker  │ ⚠️ 最终一致│ ✅ 高可用  │ ✅ 分区容错│
│ Web Locks API   │ ✅ 强一致  │ ⚠️ 锁竞争  │ ❌ 单标签  │
│ CRDT (Yjs)      │ ⚠️ 最终一致│ ✅ 高可用  │ ✅ 分区容错│
└─────────────────┴───────────┴───────────┴───────────┘

工程推论:
  离线优先应用 = Service Worker + BackgroundSync (AP 系统)
  金融级表单 = Web Locks + IndexedDB (CP 系统)
  协作编辑 = CRDT + BroadcastChannel (AP 系统, 最终一致)
```

---

## 四、权威引用

> **WHATWG Storage Standard**:
> "The storage standard defines an API for persistent storage and quota estimates."

> **Jake Archibald** (Google Chrome 工程师):
> "The browser is an operating system, and Service Worker is its kernel."

---

## 五、子主题导航

| 序号 | 子主题文件 | 核心内容 |
|------|-----------|---------|
| 01 | [01-浏览器存储层次-延迟容量权衡的形式化](./01-浏览器存储层次-延迟容量权衡的形式化.md) | L1-L8 层级、τ/cap 函数 |
| 02 | [02-前端CAP定理-存储方案的分布式约束](./02-前端CAP定理-存储方案的分布式约束.md) | 定理 T6、工程推论 |
| 03 | [03-离线优先架构-ServiceWorker与后台同步](./03-离线优先架构-ServiceWorker与后台同步.md) | AP 系统、BackgroundSync |
| 04 | [04-协作编辑的CRDT-浏览器内冲突解决](./04-协作编辑的CRDT-浏览器内冲突解决.md) | Yjs、最终一致、冲突自动解决 |
| 05 | [05-状态同步策略-强一致到因果一致的选择](./05-状态同步策略-强一致到因果一致的选择.md) | 状态副本、sᵢ = sⱼ、happens-before |

---

## 六、批判性总结

前端存储的 CAP 约束表明：浏览器是一个微型分布式系统，每个标签页是一个节点，每个 Storage API 是一种一致性协议。理解这些约束是设计离线优先应用的基础。

Service Worker 将前端从"纯客户端"转变为"可离线运行的分布式节点"，这是前端工程最具范式意义的发展之一。BackgroundSync 和 Periodic Background Sync 进一步扩展了前端的自治能力。


---

## 七、概念属性关系网络

| 概念节点 | 核心属性 | 依赖节点 | 关联强度 | 形式化映射 |
|---------|---------|---------|---------|-----------|
| **存储层次 L1-L8** | 延迟 τ、容量 cap、生命周期 lifetime | 访问成本模型 Cost(Lᵢ) | ★★★★★ | Lᵢ = ⟨capacityᵢ, latencyᵢ, lifetimeᵢ, controlᵢ⟩ |
| **状态同步** | 强一致/因果一致/最终一致 | 副本状态 sᵢ, sⱼ | ★★★★★ | sᵢ = sⱼ ∨ ◇(sᵢ = sⱼ) |
| **前端 CAP 定理** | 一致性 C、可用性 A、分区容错 P | 存储方案选择 | ★★★★★ | 最多同时满足两项 |
| **Service Worker** | 生命周期状态机、事件驱动 | 缓存策略、BackgroundSync | ★★★★★ | δ: S × Event → S |
| **CRDT** | 交换律/结合律/幂等律 | 最终一致性、无冲突合并 | ★★★★★ | merge: S × S → S |
| **离线优先架构** | AP 系统、本地权威源 | Service Worker + BackgroundSync | ★★★★★ | 可用性优先 + 分区容错 |
| **存储配额** | usage、quota、持久化请求 | 浏览器策略、LRU 驱逐 | ★★★★☆ | Q = f(disk, usage, prefs, policy) |

**关系网络拓扑**：

```text
存储层次 L1-L8 ──→ 访问成本模型 ──→ 存储方案选择
      ↓                                   ↑
状态同步 ←── 前端 CAP 定理 ────────────┘
      ↓              ↑
Service Worker ──→ 离线优先架构 ──→ CRDT
      ↓                                   ↑
缓存策略 ←── BackgroundSync ───────── 存储配额
```

---

## 八、形式化推理链

**推理链 R1：从存储层次到访问成本最优选择的推理**

```text
前提:
  P1: 设存储层次 L = {L₁, ..., L₈}, 每个 Lᵢ = ⟨capacityᵢ, latencyᵢ, lifetimeᵢ, controlᵢ⟩
  P2: 访问数据 d 的请求序列 req(d) = (r₁, r₂, ..., rₙ)
  P3: 局部性原理: 时间局部性 + 空间局部性

推导:
  Step 1: 缓存命中率定义
    hit_rate(Lᵢ) = hitsᵢ / (hitsᵢ + missesᵢ)

  Step 2: 有效访问延迟
    effective_latency(Lᵢ) =
      hit_rateᵢ × latencyᵢ + (1 - hit_rateᵢ) × latencyᵢ₊₁

  Step 3: 总成本最小化
    Cost(Lᵢ) = latencyᵢ + miss_penaltyᵢ × (1 - hit_rateᵢ)
    最优层级选择: L* = argmin_{Lᵢ} Cost(Lᵢ)

  Step 4: 层次间比例关系
    典型延迟比: latencyᵢ₊₁ / latencyᵢ ≈ 10
    因此: 命中率每提升 10%，有效延迟降低约 1 个数量级

结论 (定理 T-ST1):
  前端存储的最优访问策略遵循层次化缓存原理:
    频繁访问的小数据 → L1/L2 (内存)
    会话级状态 → L3/L4 (SessionStorage/localStorage)
    结构化持久数据 → L5/L6 (IndexedDB/OPFS)
    大文件/网络资源 → L7/L8 (Cache API/Network)
  偏离此层次（如将频繁访问数据置于 IndexedDB）将导致有效延迟恶化 10³~10⁴ 倍。
```

**推理链 R2：从前端 CAP 到存储方案选择的完备性**

```text
前提:
  P1: CAP 定理: 分布式系统最多同时满足 C, A, P 中的两项
  P2: 浏览器是多标签页分布式系统，网络断开是常态分区
  P3: 业务场景对一致性的需求函数 R_consistency(business)

推导:
  Step 1: 前端存储的 CAP 映射
    localStorage: CA 系统 (无分区，单标签强一致)
    IndexedDB: CA 系统 (单标签事务一致)
    BroadcastChannel + localStorage: AP 系统 (因果一致)
    Service Worker + BackgroundSync: AP 系统 (最终一致)
    Web Locks API: CP 系统 (单标签强一致，锁竞争降低可用性)
    CRDT (Yjs): AP 系统 (最终一致 + 冲突自动解决)

  Step 2: 场景-方案匹配
    离线优先应用 → AP (Service Worker + BackgroundSync)
    金融级表单 → CP (Web Locks + IndexedDB 事务)
    协作编辑 → AP (CRDT + BroadcastChannel)
    用户偏好 → CA (localStorage)

  Step 3: 一致性需求判定
    强一致需求 ⟺ R_consistency ∈ {金融交易, 库存扣减, 权限变更}
    最终一致需求 ⟺ R_consistency ∈ {社交点赞, 评论, 内容同步}
    因果一致需求 ⟺ R_consistency ∈ {聊天消息, 评论回复}

结论 (定理 T-ST2):
  前端存储方案的选择由 CAP 约束和业务一致性需求共同决定:
    Scheme* = argmax_{scheme} [satisfies(CAP, scheme) ∧ match(consistency_need, scheme)]
  网络分区不可消除，因此离线场景下 A 和 P 必选，C 必须降级为最终一致或因果一致。
```

---

## 九、推理判定树/决策树

```text
前端存储与状态持久化方案选型决策树
│
├─► 数据生命周期判定
│   ├─ [页面级临时] ──► JS 变量 / React State / V8 Heap (L1-L2)
│   ├─ [会话级] ──► SessionStorage (L3, 标签页关闭清除)
│   ├─ [用户级永久] ──► localStorage (L4, 同源共享)
│   ├─ [应用级结构化] ──► IndexedDB (L5, ACID 事务)
│   ├─ [大文件/二进制] ──► OPFS (L6, 随机读写)
│   ├─ [离线缓存] ──► Cache API (L7, Request/Response 对)
│   └─ [服务端权威] ──► Network Storage (L8, fetch + 同步协议)
│
├─► 一致性需求判定
│   ├─ [强一致 + 在线] ──► 服务端状态 + 悲观更新
│   ├─ [强一致 + 离线] ──► Web Locks + IndexedDB 事务 (CP)
│   ├─ [因果一致] ──► BroadcastChannel + 向量时钟
│   ├─ [最终一致] ──► Service Worker + BackgroundSync (AP)
│   └─ [自动冲突解决] ──► CRDT (Yjs/Automerge)
│
├─► 离线可用性判定
│   ├─ [必须离线可用] ──► IndexedDB/OPFS + Service Worker
│   │   └─ 需后台同步 ──► BackgroundSync API
│   └─ [在线优先] ──► 服务端状态缓存 (React Query/SWR)
│
└─► 容量与性能判定
    ├─ [< 5MB 字符串] ──► localStorage
    ├─ [< 1MB 结构化对象] ──► IndexedDB
    ├─ [> 10MB 大文件] ──► OPFS (Worker 同步 API)
    └─ [需索引查询] ──► IndexedDB (B-Tree 索引)
```

---

## 十、国际课程对齐标注

| 核心内容 | 国际课程 | 章节/主题映射 | 对齐强度 |
|---------|---------|-------------|---------|
| 浏览器存储层次 | **Stanford CS 142** Web Applications | Browser Storage, Local State Management | ★★★★★ |
| CAP 定理与分布式约束 | **Berkeley CS 162** Operating Systems | Distributed Systems, CAP Theorem, Consistency | ★★★★★ |
| 缓存层次与局部性原理 | **Berkeley CS 162** | Memory Hierarchy, Caching, Locality | ★★★★★ |
| Service Worker 与离线架构 | **Stanford CS 142** | Progressive Web Apps, Offline-First Design | ★★★★★ |
| 一致性模型与状态同步 | **Berkeley CS 162** | Concurrency, Consistency Models, Transactions | ★★★★★ |
| 存储配额与持久化 | **Stanford CS 142** | Client-Side Storage, Security & Privacy | ★★★★☆ |

> **权威来源说明**：
>
> - **Stanford CS 142**（Web Applications，Mendel Rosenblum 等）系统讲授浏览器环境下的存储机制、状态管理和渐进式 Web 应用（PWA）设计，其课程项目直接涉及 localStorage、IndexedDB 和 Service Worker 的工程实践。
> - **Berkeley CS 162**（Operating Systems and Systems Programming，John Kubiatowicz 等）在分布式系统模块中讲授 CAP 定理、一致性模型和缓存层次结构，这些理论是前端存储设计的直接数学基础。
> - **Eric A. Brewer** (2000): "Towards Robust Distributed Systems." PODC Keynote. CAP 定理的首次提出。
> - **Seth Gilbert & Nancy Lynch** (2002): "Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services." *ACM SIGACT News*, 33(2):51-59. CAP 定理的形式化证明。
> - **Doug Terry** (2013): "Replicated Data Consistency Explained Through Baseball." *ACM Queue*, 11(5). 一致性模型的经典科普，涵盖从强一致到最终一致的完整谱系。
