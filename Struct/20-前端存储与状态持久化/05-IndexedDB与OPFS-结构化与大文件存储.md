# IndexedDB 与 OPFS：结构化与大文件存储

> **来源映射**: View/03.md §3.2
> **国际权威参考**: Indexed Database API (W3C), File System Standard (WHATWG), "High Performance Browser Networking" (Ilya Grigorik)

---

## 一、知识体系思维导图

```text
浏览器结构化与大文件存储
│
├─► IndexedDB
│   ├─ 数据模型: 对象存储 (Object Store) = 键值集合
│   ├─ 索引: 在对象属性上建立 B-Tree 索引
│   ├─ 事务: ACID (Atomic, Consistent, Isolated, Durable)
│   ├─ 游标: 范围查询与迭代 (IDBCursor)
│   ├─ 版本升级: 通过 onupgradeneeded 迁移 Schema
│   └─ 封装库: idb, Dexie.js, localForage
│
├─► Origin Private File System (OPFS)
│   ├─ 同步 API (Worker): createSyncAccessHandle
│   ├─ 异步 API (Main Thread): createWritable, getFile
│   ├─ 随机读写: seek + read/write (类 POSIX)
│   ├─ 大文件吞吐: 比 IndexedDB 快 10-100×
│   └─ 沙箱路径: 应用无法访问真实文件系统
│
├─► 存储配额与持久化
│   ├─ 临时 (Temporary): 浏览器可自动清理
│   ├─ 持久 (Persistent): navigator.storage.persist()
│   ├─ 最佳 effort: 默认策略
│   └─ 配额查询: navigator.storage.estimate()
│
├─► 性能特征
│   ├─ IndexedDB: 适合小对象 (<1MB)、索引查询
│   ├─ OPFS: 适合大文件 (>10MB)、流式读写
│   ├─ 内存映射: OPFS 支持 in-place 修改
│   └─ 序列化成本: IndexedDB 使用 Structured Clone
│
└─► 选择决策树
    ├─ 需要索引查询? → IndexedDB
    ├─ 大文件/二进制? → OPFS
    ├─ 需要事务原子性? → IndexedDB
    └─ 需要 POSIX 随机访问? → OPFS
```

---

## 二、核心概念的形式化定义

### 2.1 IndexedDB 的键值存储模型

```text
定义 (IndexedDB 数据库):
  数据库 DB = (objectStores, version)

  对象存储 OS = (records, keyPath, autoIncrement, indexes)
    records ⊆ Key × Value
    keyPath: Value → Key (可选，从值中提取键)
    autoIncrement: Boolean (自动生成整数键)

  索引 Index = (name, keyPath, unique, multiEntry)
    索引将 keyPath 映射到 Record 集合
    unique: 是否要求 keyPath 值唯一
    multiEntry: 数组值是否展开为多个索引条目

  事务 T = (mode, scope, operations)
    mode ∈ {readonly, readwrite, versionchange}
    scope: 本次事务涉及的对象存储集合
    operations: 原子执行的操作序列

  ACID 保证:
    Atomic: 事务内所有操作全成功或全回滚
    Consistent: 索引与主数据始终一致
    Isolated: 并发事务通过锁隔离
    Durable: 成功提交后数据持久化到磁盘
```

### 2.2 OPFS 的同步文件系统 API

```text
定义 (Origin Private File System):
  OPFS 是浏览器内的沙箱文件系统:
    根目录: await navigator.storage.getDirectory()
    路径: 纯逻辑路径，与真实 OS 文件系统隔离

  同步访问句柄 (Worker only):
    handle = await fileHandle.createSyncAccessHandle()
    handle.read(buffer, { at: offset })  // 随机读
    handle.write(buffer, { at: offset }) // 随机写
    handle.truncate(newSize)
    handle.flush()

  性能特征:
    - 绕过主线程事件循环
    - 直接映射到磁盘 I/O (通过 WASM/Worker)
    - 吞吐量: 可达 1 GB/s (取决于磁盘)

  与 IndexedDB 的形式化差异:
    IndexedDB: Record-oriented, 事务边界, 结构化克隆序列化
    OPFS: Byte-oriented, 无事务 (需应用层保证), 零拷贝读写
```

### 2.3 存储配额的形式化管理

```text
定义 (存储配额):
  浏览器为每个 origin 分配存储配额 Q:

  Q = f(disk_space, origin_usage, user_preferences, browser_policy)

  典型策略:
    Chrome: 配额 ≈ 磁盘剩余空间的 60%
    Safari: 配额 ≈ 1 GB (桌面), 更严格 (移动)
    Firefox: 动态调整，提示用户

  持久化请求:
    persistent = await navigator.storage.persist()
    persistent = true → 浏览器不会自动清理 (但仍可能被用户手动删除)

  配额监控:
    { usage, quota } = await navigator.storage.estimate()
    usageDetails 可细分为: indexedDB, serviceWorkerRegistrations, webSQL

  驱逐策略 (Eviction):
    当磁盘空间不足时，浏览器按 LRU 清理临时存储
    持久化存储 (persisted=true) 不会被自动清理
```

---

## 三、IndexedDB vs OPFS 对比矩阵

| 维度 | IndexedDB | OPFS | localStorage | Cache API |
|------|-----------|------|--------------|-----------|
| **数据模型** | 结构化对象 (键值) | 原始字节流 | 字符串键值 | Request/Response |
| **事务支持** | **ACID** | 无 (应用层实现) | 无 | 无 |
| **索引查询** | **B-Tree 索引** | 无 | 无 | 按 URL |
| **大文件 (>10MB)** | 性能差 | **优秀** | 不支持 | 支持 |
| **随机读写** | 记录级 | **字节级 seek** | 不支持 | 不支持 |
| **序列化成本** | Structured Clone | **零拷贝** | JSON stringify | 无 |
| **Worker 同步** | 异步 (IndexedDB v2) | **同步 API** | 不支持 | 异步 |
| **适用场景** | 结构化数据、查询 | 大文件、媒体、游戏资源 | 小配置项 | 网络响应缓存 |

---

## 四、工程实践与代码示例

### 4.1 IndexedDB 结构化数据管理

```javascript
import { openDB } from 'idb';

const db = await openDB('app-store', 2, {
  upgrade(db, oldVersion, newVersion, transaction) {
    // v1 → v2 迁移
    if (oldVersion < 1) {
      const store = db.createObjectStore('documents', { keyPath: 'id' });
      store.createIndex('by-date', 'createdAt');
      store.createIndex('by-tag', 'tags', { multiEntry: true });
    }
    if (oldVersion < 2) {
      const store = transaction.objectStore('documents');
      store.createIndex('by-author', 'authorId');
    }
  },
});

// 事务写入
await db.put('documents', {
  id: 'doc-1',
  title: 'Architecture Notes',
  createdAt: Date.now(),
  tags: ['frontend', 'storage'],
  authorId: 'user-42',
});

// 索引范围查询
const recentDocs = await db.getAllFromIndex(
  'documents', 'by-date',
  IDBKeyRange.lowerBound(Date.now() - 7 * 86400000)
);

// 标签查询 (multiEntry)
const frontendDocs = await db.getAllFromIndex(
  'documents', 'by-tag', 'frontend'
);
```

### 4.2 OPFS 大文件随机读写

```javascript
// 在 Web Worker 中使用同步 OPFS API
self.onmessage = async (event) => {
  const { action, fileName, offset, data } = event.data;
  const root = await navigator.storage.getDirectory();

  if (action === 'write') {
    const fileHandle = await root.getFileHandle(fileName, { create: true });

    // 同步访问句柄 (仅 Worker 可用)
    const syncHandle = await fileHandle.createSyncAccessHandle();

    // 定位并写入
    const written = syncHandle.write(data, { at: offset });
    syncHandle.flush();
    syncHandle.close();

    self.postMessage({ written });
  }

  if (action === 'read') {
    const fileHandle = await root.getFileHandle(fileName);
    const syncHandle = await fileHandle.createSyncAccessHandle();

    const buffer = new Uint8Array(data.length); // data.length = 读取大小
    const read = syncHandle.read(buffer, { at: offset });
    syncHandle.close();

    self.postMessage({ read, buffer });
  }
};
```

### 4.3 存储配额监控与清理策略

```javascript
async function monitorStorage() {
  const estimate = await navigator.storage.estimate();
  const usedGB = (estimate.usage / 1e9).toFixed(2);
  const quotaGB = (estimate.quota / 1e9).toFixed(2);
  const percent = ((estimate.usage / estimate.quota) * 100).toFixed(1);

  console.log(`Storage: ${usedGB} GB / ${quotaGB} GB (${percent}%)`);

  // 超过 80% 时触发清理
  if (percent > 80) {
    await cleanupOldCache();
  }

  // 请求持久化 (避免被浏览器自动清理)
  if (navigator.storage.persist) {
    const isPersistent = await navigator.storage.persist();
    console.log(`Persistent storage granted: ${isPersistent}`);
  }
}

async function cleanupOldCache() {
  const db = await openDB('app-store', 2);
  const tx = db.transaction('documents', 'readwrite');
  const store = tx.objectStore('documents');
  const index = store.index('by-date');

  // 删除 30 天前的文档
  const cutoff = Date.now() - 30 * 86400000;
  const oldKeys = await index.getAllKeys(IDBKeyRange.upperBound(cutoff));

  for (const key of oldKeys) {
    await store.delete(key);
  }

  await tx.done;
}
```

---

## 五、权威引用

> **Joshua Bell** (2015): "IndexedDB was designed to be the database for the web platform. It supports transactions, indexes, and cursors—everything you need for complex client-side data."

> **Ilya Grigorik** (2013): "The browser is not just a document viewer; it's a full-fledged operating system with its own storage, networking, and rendering stack."

> **Jim Gray** (1981): "A transaction is a transformation of state that preserves the consistency constraints of a database. Atomicity, consistency, isolation, and durability are the fundamental properties."

> **Douglas Engelbart** (1962): "The complexity of our problems is growing faster than our ability to solve them. We must augment human intellect with new conceptual tools."

---

## 六、批判性总结

IndexedDB 是**浏览器内唯一提供 ACID 事务保障的客户端数据库**，其设计目标是在 Web 环境中复现传统数据库的核心能力：事务原子性确保批量操作要么全成功要么全回滚，B-Tree 索引使范围查询和排序在毫秒级完成，版本升级机制允许应用在发布新版本时无损迁移 Schema。但这些能力是有代价的——IndexedDB 的 Structured Clone 序列化对大型对象（>1MB）的性能急剧下降，因为每个写入都需要将整个对象图序列化为二进制格式。这决定了 IndexedDB 的**最佳工作负载是大量小对象**，而非少量大对象。

OPFS（Origin Private File System）的出现填补了浏览器存储在**大文件场景**的空白。它的同步访问句柄在 Web Worker 中提供了接近原生文件系统的性能：随机 seek、in-place 修改、零拷贝读写。对于视频编辑器的素材文件、科学计算的中间结果、游戏引擎的资源包，OPFS 的吞吐量比 IndexedDB 高出一个数量级。但 OPFS 的 API 设计暴露了浏览器安全模型与性能需求之间的张力——同步 API 被限制在 Worker 中，因为主线程的任何同步 I/O 都会阻塞用户交互；而异步 API 虽然可以在主线程使用，却失去了随机读写的性能优势。

2026 年的关键决策是**IndexedDB 与 OPFS 的协同使用**：用 IndexedDB 存储元数据（文件路径、创建时间、标签、索引），用 OPFS 存储实际的大文件内容。这种"元数据-内容分离"模式结合了 IndexedDB 的查询能力和 OPFS 的吞吐能力，是当前大文件 Web 应用的最佳实践。但浏览器存储生态仍缺少一个关键能力——**跨 origin 的共享存储**。在 Privacy Sandbox 的演进中，Shared Storage API 和 Private State Tokens 正在尝试在安全与功能之间寻找新的平衡点，但标准的成熟仍需时日。


---

## 七、概念属性关系网络

| 概念节点 | 核心属性 | 依赖节点 | 关联强度 | 形式化映射 |
|---------|---------|---------|---------|-----------|
| **IndexedDB** | 对象存储、B-Tree 索引、ACID 事务 | 结构化克隆、版本升级 | ★★★★★ | DB = (objectStores, version), OS = (records, keyPath, indexes) |
| **OPFS** | 同步 API (Worker)、零拷贝、随机 seek | 沙箱路径、字节级访问 | ★★★★★ | Byte-oriented, POSIX-like, createSyncAccessHandle |
| **存储配额 Q** | usage、quota、持久化、LRU 驱逐 | 浏览器策略、origin 隔离 | ★★★★★ | Q = f(disk_space, usage, prefs, policy) |
| **事务 ACID** | Atomic、Consistent、Isolated、Durable | 锁机制、版本升级 | ★★★★★ | T = (mode, scope, ops), mode ∈ {readonly, readwrite, versionchange} |
| **元数据-内容分离** | IndexedDB 存元数据、OPFS 存内容 | 查询能力 + 吞吐能力结合 | ★★★★★ | metadata ∈ IndexedDB, content ∈ OPFS |
| **结构化克隆** | 序列化成本、循环引用、类型支持 | IndexedDB 写入性能 | ★★★★☆ | StructuredClone(value) → binary |
| **Storage Buckets** | 独立配额、持久性级别、过期时间 | 配额管理、资源隔离 | ★★★★☆ | Bucket = (name, quota, durability, expires) |

**关系网络拓扑**：

```text
IndexedDB ←── 事务 ACID ←── 结构化克隆
      ↓              ↑              ↓
B-Tree 索引 ←── 元数据-内容分离 ──→ 查询能力
      ↓                           ↑
OPFS ←── 零拷贝/随机 seek ────→ 吞吐能力
      ↓                           ↑
存储配额 Q ←── Storage Buckets ── 资源隔离
```

---

## 八、形式化推理链

**推理链 R1：从事务 ACID 到前端结构化存储可靠性的推理**

```text
前提:
  P1: IndexedDB 事务 T = (mode, scope, operations)
  P2: ACID 性质:
        Atomic: 事务内操作全成功或全回滚
        Consistent: 索引与主数据始终一致
        Isolated: 并发事务通过锁隔离
        Durable: 成功提交后持久化到磁盘
  P3: 浏览器可能随时终止 (crash, 关闭标签, OOM)

推导:
  Step 1: 原子性的实现
    设事务内操作序列 ops = [op₁, op₂, ..., opₙ]
    原子性保证: ∀k ∈ [1,n]:
      (ops[1..k] 成功 ∧ ops[k+1..n] 失败) → 回滚到 ops[1..k-1] 之前状态
    实现: 预写日志 (Write-Ahead Logging) + 两阶段提交 (浏览器内部)

  Step 2: 隔离级别分析
    IndexedDB 使用"快照隔离"变体:
      readonly 事务: 读取事务开始时的快照
      readwrite 事务: 同一对象存储上的读写互斥
    隔离级别等价于 SQL 的 READ COMMITTED (非 SERIALIZABLE)

  Step 3: 持久性边界
    Durable ⟺ 数据写入操作系统文件系统缓存
    但: OS 缓存可能因崩溃丢失 (未 fsync 到磁盘)
    浏览器不保证 fsync，因此 IndexedDB 的持久性是"尽力而为"

  Step 4: 版本升级的原子性
    versionchange 事务独占数据库:
      onupgradeneeded 中所有 schema 变更在单一事务内完成
      失败则整个版本升级回滚

结论 (定理 T-DB1):
  IndexedDB 的 ACID 保证是浏览器存储中最强的:
    Atomicity: 操作序列全有或全无
    Consistency: 索引与数据的一致性由浏览器维护
    Isolation: 对象存储级读写锁 (READ COMMITTED)
    Durability: 尽力持久化 (不保证跨系统崩溃)
  对于金融级应用，Durability 的"尽力"性质不可接受——
  必须在上传服务端后才向用户确认成功。
```

**推理链 R2：从存储特征到 IndexedDB/OPFS 协同使用的形式化**

```text
前提:
  P1: IndexedDB: Record-oriented, 事务边界, Structured Clone, B-Tree 索引
  P2: OPFS: Byte-oriented, 无事务, 零拷贝, 字节级 seek
  P3: 大文件场景: 文件大小 > 10MB, 需要随机读写

推导:
  Step 1: 性能特征对比
    ┌──────────────┬─────────────┬─────────────┐
    │   维度        │  IndexedDB  │    OPFS     │
    ├──────────────┼─────────────┼─────────────┤
    │ 数据模型      │ 结构化对象   │ 原始字节流   │
    │ 事务支持      │ ACID        │ 无 (应用层)  │
    │ 索引查询      │ B-Tree      │ 无          │
    │ 大文件 (>10MB)│ 性能差       │ 优秀 (1GB/s)│
    │ 随机读写      │ 记录级       │ 字节级 seek │
    │ 序列化成本    │ Structured  │ 零拷贝       │
    │               │ Clone (高)   │             │
    └──────────────┴─────────────┴─────────────┘

  Step 2: 协同使用模式
    元数据: 文件路径、创建时间、标签、权限 → IndexedDB (索引查询)
    内容: 实际文件数据、媒体资源、游戏包 → OPFS (吞吐能力)
    关联: metadata.contentHandle → OPFS FileHandle

  Step 3: 一致性保证 (应用层)
    元数据与内容的一致性需应用层维护:
      写入: 先写 OPFS 内容 → 成功后再写 IndexedDB 元数据
      删除: 先删 IndexedDB 元数据 → 再删 OPFS 内容
      回滚: 若 OPFS 写入失败，不写入元数据
    这不是原子操作，但将不一致窗口最小化

  Step 4: 配额统一
    IndexedDB 和 OPFS 共享同一 origin 配额:
      usage_total = usage_idb + usage_opfs + usage_cache + ...
      quota 由浏览器按 LRU 策略在临时存储间分配

结论 (定理 T-DB2):
  IndexedDB 与 OPFS 的协同使用遵循"能力互补"原则:
    需要查询能力 → IndexedDB (元数据)
    需要吞吐能力 → OPFS (内容)
  分离模式的查询-内容一致性由应用层乐观控制，
  其可靠性低于数据库的外键约束，但在浏览器环境中是工程最优解。
```

---

## 九、推理判定树/决策树

```text
浏览器结构化/大文件存储方案选型决策树
│
├─► 数据模型判定
│   ├─ [结构化对象 + 索引查询] ──► IndexedDB
│   │   └─ 需要复杂查询 ──► Dexie.js / idb (Promise 封装)
│   ├─ [原始字节/大文件] ──► OPFS
│   │   └─ 需要随机读写 ──► OPFS Sync Access Handle (Worker)
│   └─ [键值字符串] ──► localStorage / sessionStorage
│
├─► 文件大小判定
│   ├─ [< 1MB 结构化对象] ──► IndexedDB (最佳)
│   ├─ [1-10MB] ──► IndexedDB (可行) 或 OPFS (若需随机访问)
│   └─ [> 10MB] ──► OPFS (必须，IndexedDB Structured Clone 性能急剧下降)
│
├─► 事务需求判定
│   ├─ [需要 ACID] ──► IndexedDB (原子写入、索引一致性)
│   └─ [无需事务] ──► OPFS / Cache API
│       └─ 若需应用层事务 ──► 自定义 write-ahead log + 两阶段提交
│
├─► 线程环境判定
│   ├─ [主线程] ──► IndexedDB (异步 API) / OPFS (异步 API)
│   └─ [Web Worker] ──► OPFS (同步 API，性能最优)
│       └─ IndexedDB 在 Worker 中仍为异步
│
└─► 配额与持久化判定
    ├─ [请求持久化] ──► navigator.storage.persist()
    │   └─ granted=true → 浏览器不会自动清理
    ├─ [监控配额] ──► navigator.storage.estimate()
    │   └─ usage / quota > 80% → 触发清理策略
    └─ [存储桶隔离] ──► Storage Buckets API (实验性)
        └─ 为不同模块分配独立配额和生命周期
```

---

## 十、国际课程对齐标注

| 核心内容 | 国际课程 | 章节/主题映射 | 对齐强度 |
|---------|---------|-------------|---------|
| IndexedDB 数据模型与事务 | **Stanford CS 142** Web Applications | Client-Side Databases, Structured Storage | ★★★★★ |
| B-Tree 索引与查询优化 | **Berkeley CS 162** Operating Systems | File Systems, Index Structures | ★★★★★ |
| ACID 事务与隔离级别 | **Berkeley CS 162** | Transactions, Concurrency Control | ★★★★★ |
| 文件系统 API 与随机 I/O | **Berkeley CS 162** | File Systems, I/O Performance | ★★★★★ |
| 存储配额与资源管理 | **Stanford CS 142** | Browser Security, Storage Policies | ★★★★☆ |
| 零拷贝与高性能 I/O | **Berkeley CS 162** | Memory Mapping, DMA, Zero-Copy | ★★★★☆ |

> **权威来源说明**：
>
> - **Stanford CS 142**（Web Applications）在 Client-Side Storage 和 Structured Data 模块中讲授 IndexedDB 的设计与使用，其课程项目涉及完整的浏览器端数据持久化方案。
> - **Berkeley CS 162**（Operating Systems）在 File Systems 和 Transactions 模块中系统讲授 B-Tree 索引、ACID 事务和并发控制，这些理论是 IndexedDB 设计的形式化基础。
> - **Jim Gray** (1981): "The Transaction Concept: Virtues and Limitations." *VLDB*. 事务 ACID 性质的奠基论文，数据库事务理论的起点。
> - **Douglas Comer** (1979): "The Ubiquitous B-Tree." *ACM Computing Surveys*, 11(2):121-137. B-Tree 索引结构的标准参考，IndexedDB 索引的实现基础。
> - **Joshua Bell** (2015): "IndexedDB: The Database for the Web Platform." *W3C*. IndexedDB 规范的编辑者，系统阐述了浏览器数据库的设计目标。
> - **WHATWG File System Standard** (2023): "Origin Private File System." 定义 OPFS 的同步/异步 API 和沙箱安全模型。
