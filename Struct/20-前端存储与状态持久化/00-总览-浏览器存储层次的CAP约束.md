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
