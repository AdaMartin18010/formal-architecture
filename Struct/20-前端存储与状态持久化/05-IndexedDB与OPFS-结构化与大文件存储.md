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

## 四、权威引用

> **Joshua Bell** (Chrome, IndexedDB 规范编辑):
> "IndexedDB was designed to be the database for the web platform. It supports transactions, indexes, and cursors—everything you need for complex client-side data."

> **WHATWG File System Standard**:
> "The Origin Private File System provides access to a special kind of file system that is highly optimized for performance and offers in-place write access to its content."

> **Ilya Grigorik** ("High Performance Browser Networking"):
> "The browser is not just a document viewer; it's a full-fledged operating system with its own storage, networking, and rendering stack."

---

## 五、工程实践与代码示例

### 5.1 IndexedDB 结构化数据管理

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

### 5.2 OPFS 大文件随机读写

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

### 5.3 存储配额监控与清理策略

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

## 六、批判性总结

IndexedDB 是**浏览器内唯一提供 ACID 事务保障的客户端数据库**，其设计目标是在 Web 环境中复现传统数据库的核心能力：事务原子性确保批量操作要么全成功要么全回滚，B-Tree 索引使范围查询和排序在毫秒级完成，版本升级机制允许应用在发布新版本时无损迁移 Schema。但这些能力是有代价的——IndexedDB 的 Structured Clone 序列化对大型对象（>1MB）的性能急剧下降，因为每个写入都需要将整个对象图序列化为二进制格式。这决定了 IndexedDB 的**最佳工作负载是大量小对象**，而非少量大对象。

OPFS（Origin Private File System）的出现填补了浏览器存储在**大文件场景**的空白。它的同步访问句柄在 Web Worker 中提供了接近原生文件系统的性能：随机 seek、in-place 修改、零拷贝读写。对于视频编辑器的素材文件、科学计算的中间结果、游戏引擎的资源包，OPFS 的吞吐量比 IndexedDB 高出一个数量级。但 OPFS 的 API 设计暴露了浏览器安全模型与性能需求之间的张力——同步 API 被限制在 Worker 中，因为主线程的任何同步 I/O 都会阻塞用户交互；而异步 API 虽然可以在主线程使用，却失去了随机读写的性能优势。

2026 年的关键决策是**IndexedDB 与 OPFS 的协同使用**：用 IndexedDB 存储元数据（文件路径、创建时间、标签、索引），用 OPFS 存储实际的大文件内容。这种"元数据-内容分离"模式结合了 IndexedDB 的查询能力和 OPFS 的吞吐能力，是当前大文件 Web 应用的最佳实践。但浏览器存储生态仍缺少一个关键能力——**跨 origin 的共享存储**。在 Privacy Sandbox 的演进中，Shared Storage API 和 Private State Tokens 正在尝试在安全与功能之间寻找新的平衡点，但标准的成熟仍需时日。
