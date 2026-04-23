# 离线优先架构：Service Worker 与 Background Sync

> **来源映射**: View/05.md §4.2
> **国际权威参考**: Service Workers Specification (W3C), Background Sync Specification (WICG), "Building Progressive Web Apps" (Tal Ater)

---

## 一、知识体系思维导图

```text
离线优先架构
│
├─► Service Worker 生命周期
│   ├─ 注册 (Register): navigator.serviceWorker.register('/sw.js')
│   ├─ 安装 (Install): 缓存静态资源 (precache)
│   ├─ 等待 (Waiting): 等待旧版本 SW 终止
│   ├─ 激活 (Activate): 清理旧缓存，接管页面
│   ├─ 空闲 (Idle): 事件驱动，无持久线程
│   └─ 终止 (Terminated): 浏览器可随时终止以节省资源
│
├─► 缓存策略谱系
│   ├─ Cache-First: 缓存命中则返回，否则网络
│   ├─ Network-First: 先网络，失败则回退缓存
│   ├─ Stale-While-Revalidate: 返回缓存并后台更新
│   ├─ Network-Only: 始终网络 (如 API 请求)
│   └─ Cache-Only: 仅缓存 (离线页面)
│
├─► Background Sync
│   ├─ One-shot Sync: 网络恢复时发送单次请求
│   ├─ Periodic Background Sync: 定期后台同步 (受限)
│   ├─ 可靠性边界: 浏览器可延迟/拒绝同步
│   └─ 权限模型: 用户安装 PWA 后才可用
│
├─► 离线优先的形式化
│   ├─ 前端作为 AP 系统: 可用性优先 + 分区容错
│   ├─ 一致性通过后台同步最终达成
│   └─ 冲突解决: LWW / 手动合并 / CRDT
│
└─► 可靠性边界
    ├─ SW 可被浏览器随时终止 (事件驱动)
    ├─ Background Sync 不保证即时执行
    ├─ 存储配额限制离线缓存大小
    └─ iOS Safari: 7 天后删除未使用 SW 缓存
```

---

## 二、核心概念的形式化定义

### 2.1 Service Worker 生命周期状态机

```text
定义 (Service Worker 状态机):
  状态集 S = {parsed, installing, installed, activating, activated, redundant}

  转移函数 δ: S × Event → S
    parsed --install--> installing
    installing --install_success--> installed
    installed --activate--> activating
    activating --activate_success--> activated
    activated --new_version--> redundant (旧 SW)
    installing --install_failure--> redundant

  关键性质:
    - 同时最多一个 activated SW 控制页面
    - 新 SW 进入 waiting 直到所有受控页面关闭
    - skipWaiting() 可强制激活，但可能导致版本不一致

  事件驱动执行模型:
    SW 没有持久运行的线程
    浏览器在事件 (fetch, push, sync, periodicSync) 发生时唤醒 SW
    事件处理完成后，浏览器可随时终止 SW
```

### 2.2 缓存策略的形式化

```text
定义 (缓存策略):
  设请求 req，缓存 C，网络 N

  策略为函数 strategy: req → Response

  Cache-First:
    strategy(req) = C.lookup(req) 若命中
                  = N.fetch(req)   否则
    适用: 静态资源 (JS/CSS/图片)，不变内容

  Network-First:
    strategy(req) = N.fetch(req) 若成功
                  = C.lookup(req) 否则
    适用: API 请求，实时数据

  Stale-While-Revalidate:
    strategy(req) = C.lookup(req) 立即返回 (可能过期)
                  ∧ N.fetch(req) 后台更新缓存
    适用: 首页内容，允许短暂过期

  形式化权衡:
     freshness × availability = constant
    Cache-First: 高可用，低新鲜度
    Network-First: 低可用 (离线失败)，高新鲜度
    SWR: 平衡，但引入"暂时不一致"窗口
```

### 2.3 离线优先作为 AP 系统

```text
定义 (离线优先的系统模型):
  将前端视为分布式系统的一个副本节点

  CAP 定理在前端的映射:
    Consistency (一致性):
      强一致: 所有用户同时看到相同状态 (需要在线)
      最终一致: 离线修改最终同步到所有副本

    Availability (可用性):
      离线优先 = 高可用性: 无论网络状态，UI 始终可交互

    Partition Tolerance (分区容错):
      网络断开是常态，必须容忍

  离线优先的选择:
    AP + 最终一致性:
      本地状态为权威源 (Single Source of Truth)
      网络恢复时执行后台同步
      冲突解决策略决定最终状态

  可靠性边界:
    Background Sync 不保证执行:
      - 浏览器可能因电量、网络类型拒绝同步
      - 操作系统可能限制后台任务频率
      - 用户可能撤销通知权限 (影响 Sync 注册)
```

---

## 三、缓存策略与同步方案对比矩阵

| 维度 | Cache-First | Network-First | Stale-While-Revalidate | Background Sync | Periodic Sync |
|------|-------------|---------------|------------------------|-----------------|---------------|
| **离线可用** | **是** | 否 | **是** (过期数据) | 延迟同步 | 延迟同步 |
| **数据新鲜度** | 低 | **高** | 中 | **高** | 中 |
| **首屏速度** | **极快** | 慢 | **快** | N/A | N/A |
| **实现复杂度** | 低 | 低 | 中 | **高** | 高 |
| **浏览器支持** | **广泛** | **广泛** | **广泛** | Chrome/Edge | Chrome 有限 |
| **可靠性** | **高** | **高** | **高** | 中 (可能延迟) | 低 |
| **适用场景** | 静态资源 | API 实时数据 | 内容页面 | 表单提交 | 内容刷新 |

---

## 四、工程实践与代码示例

### 4.1 Service Worker 缓存策略实现

```javascript
// sw.js - Workbox 风格的缓存策略
const CACHE_NAME = 'app-v1';
const PRECACHE_ASSETS = ['/index.html', '/app.js', '/styles.css'];

// 安装阶段：预缓存核心资源
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_ASSETS))
  );
  self.skipWaiting();
});

// 激活阶段：清理旧缓存
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key !== CACHE_NAME)
          .map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

// 请求拦截：Stale-While-Revalidate
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.open(CACHE_NAME).then(async (cache) => {
      const cached = await cache.match(event.request);

      // 后台网络请求更新缓存
      const fetchPromise = fetch(event.request).then((networkResponse) => {
        cache.put(event.request, networkResponse.clone());
        return networkResponse;
      });

      // 立即返回缓存（如有），否则等待网络
      return cached || fetchPromise;
    })
  );
});
```

### 4.2 Background Sync 可靠提交

```javascript
// 注册后台同步 (主线程)
async function submitFormWithSync(data) {
  // 1. 本地持久化到 IndexedDB (确保不丢失)
  await db.outbox.add({ data, status: 'pending', createdAt: Date.now() });

  // 2. 注册后台同步
  const registration = await navigator.serviceWorker.ready;
  try {
    await registration.sync.register('sync-outbox');
    showToast('将在网络恢复后自动提交');
  } catch (err) {
    // 浏览器不支持 Background Sync，立即尝试网络请求
    await processOutboxImmediately();
  }
}

// Service Worker 中处理 sync 事件
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-outbox') {
    event.waitUntil(processOutbox());
  }
});

async function processOutbox() {
  const pending = await db.outbox.where('status').equals('pending').toArray();

  for (const item of pending) {
    try {
      await fetch('/api/submit', {
        method: 'POST',
        body: JSON.stringify(item.data),
        headers: { 'Content-Type': 'application/json' },
      });
      await db.outbox.delete(item.id); // 成功删除
    } catch (err) {
      // 网络仍不可用，保留 pending 状态，下次 sync 重试
      console.error('Sync failed for item', item.id, err);
      break; // 停止处理，避免无序提交
    }
  }
}
```

---

## 五、权威引用

> **Eric A. Brewer** (2000): "In any distributed system, you can only guarantee two of the three: Consistency, Availability, and Partition Tolerance."

> **Jake Archibald** (2014): "Service Workers are event-driven. The browser starts them up when there's work to do, and terminates them when they're idle. This means they don't consume resources when not in use."

> **Alex Russell** (2015): "The network is a liability. Every request you make is a chance for failure. Progressive Web Apps invert this assumption: work offline first, enhance with connectivity."

> **Tal Ater** (2017): "Offline-first is not just about caching assets; it's about designing your application to work without a network connection, and then enhancing it when the network is available."

---

## 六、批判性总结

离线优先架构是**前端工程对 CAP 定理的最直接应用**：在网络分区（即用户离线）不可避免的前提下，选择可用性（A）和分区容错（P），通过后台同步最终达成一致性。这一架构范式的转变从"网络优先"到"本地优先"，彻底改变了前端应用的设计哲学——不再将网络视为默认状态，而是视为一种**可选的增强能力**。

Service Worker 的**事件驱动执行模型**是浏览器资源管理的精妙设计：SW 不占用持久线程，仅在 `fetch`、`sync`、`push` 等事件触发时被唤醒，处理完成后立即终止。这使得 SW 具备了原生后台任务的能力，同时又不会消耗移动设备的宝贵电量。但这一模型也引入了**可靠性边界**——浏览器可以随时终止 SW，后台同步可以被操作系统延迟数小时甚至数天，iOS Safari 更是会在 7 天后删除未使用的 SW 缓存。这意味着离线优先应用必须设计**幂等的重试机制**和**优雅降级路径**。

Background Sync API 的**承诺与现实的鸿沟**值得关注：规范承诺"网络恢复时自动同步"，但实践中浏览器会根据电池状态、网络类型（WiFi/蜂窝）、用户互动频率等多重因素决定是否立即执行同步。在 Android 上，Chrome 的同步通常能在数分钟内完成；但在 iOS 上，WebKit 对后台任务的限制极为严格，Background Sync 几乎不可靠。这迫使工程团队必须在"乐观后台同步"和"显式用户触发的同步"之间做出务实的选择。

2026 年的前沿方向是**Periodic Background Sync** 与**Content Index API** 的结合——允许 PWA 在后台定期刷新内容，并在操作系统级别（如 Android 的"近期使用"界面）展示离线可用的内容索引。这标志着 Web 应用正在从"在线文档"进化为"操作系统级应用"，但平台差异（Android vs iOS vs Desktop）仍然是最棘手的碎片化挑战。


---

## 七、概念属性关系网络

| 概念节点 | 核心属性 | 依赖节点 | 关联强度 | 形式化映射 |
|---------|---------|---------|---------|-----------|
| **Service Worker 生命周期** | 状态机 S = {parsed,...,redundant}、事件驱动 | 缓存策略、激活控制 | ★★★★★ | δ: S × Event → S |
| **缓存策略** | Cache-First/Network-First/SWR/Network-Only | 新鲜度、可用性权衡 | ★★★★★ | strategy: req → Response |
| **Background Sync** | one-shot sync、periodic sync、可靠性边界 | Service Worker、IndexedDB | ★★★★★ | 事件触发: sync/periodicSync |
| **离线优先 (AP 系统)** | 本地权威源、高可用、分区容错 | CAP 定理、最终一致性 | ★★★★★ | AP + ◇(sᵢ = sⱼ) |
| **可靠性边界** | SW 可终止、Sync 可延迟、配额限制 | 浏览器策略、OS 限制 | ★★★★☆ | 执行概率 P(execute \| conditions) |
| **幂等重试** | 幂等性 idempotent、指数退避 | 后台同步、失败恢复 | ★★★★★ | f(f(x)) = f(x) |
| **PWA 安装** | manifest、install prompt、后台权限 | Background Sync、Periodic Sync | ★★★★☆ | beforeinstallprompt 事件 |

**关系网络拓扑**：

```text
Service Worker 生命周期 ──→ 缓存策略 ←── 新鲜度/可用性权衡
      ↓                         ↑              ↓
Background Sync ────────→ 离线优先架构 ──→ 可靠性边界
      ↓                         ↑              ↓
IndexedDB 持久化 ←────── 幂等重试 ───────── PWA 安装
```

---

## 八、形式化推理链

**推理链 R1：从网络状态到缓存策略最优选择的推理**

```text
前提:
  P1: 设网络状态 N ∈ {online, offline, slow}
  P2: 设请求分类: R_static (JS/CSS/图片), R_api (数据接口), R_content (HTML/内容)
  P3: 缓存策略集合: {Cache-First, Network-First, SWR, Network-Only, Cache-Only}

推导:
  Step 1: 策略效用函数
    定义效用 U(strategy, N, R) = freshness × availability × speed
    其中 freshness ∈ [0,1], availability ∈ {0,1}, speed ∈ [0,1]

  Step 2: 各策略的效用矩阵
    ┌──────────────┬──────────┬──────────┬──────────┐
    │   策略        │ online   │ offline  │   slow   │
    ├──────────────┼──────────┼──────────┼──────────┤
    │ Cache-First  │ 中(f旧)   │ 高(可用)  │ 高(快)   │
    │ Network-First│ 高(新鲜)  │ 低(不可用)│ 低(慢)   │
    │ SWR          │ 高        │ 中(过期)  │ 高(快)   │
    │ Network-Only │ 高        │ 无        │ 低       │
    │ Cache-Only   │ 低        │ 高        │ 高       │
    └──────────────┴──────────┴──────────┴──────────┘

  Step 3: 最优策略选择
    R_static:   argmax = Cache-First (不变内容，优先可用)
    R_api:      argmax = Network-First (在线时新鲜，离线时降级)
    R_content:  argmax = SWR (平衡新鲜与速度)

  Step 4: 形式化权衡
    freshness × availability = constant (约束曲面)
    Cache-First: 牺牲新鲜度换取可用性
    Network-First: 牺牲可用性换取新鲜度
    SWR: 在约束曲面上寻找帕累托最优

结论 (定理 T-OFF1):
  最优缓存策略是网络状态、请求类型和用户体验目标的函数:
    Strategy*(N, R) = argmax_{s} [U(s, N, R)]
  工程实践中采用混合策略: 按路由模式匹配不同策略，
  而非全局单一策略。
```

**推理链 R2：从离线优先到后台同步可靠性的形式化边界**

```text
前提:
  P1: 离线优先 = AP 系统: 选择可用性 A 和分区容错 P，一致性 C 最终达成
  P2: Background Sync 的注册: registration.sync.register(tag)
  P3: 浏览器/操作系统可能因资源管理拒绝执行 sync 事件

推导:
  Step 1: 同步请求的可靠性
    P(sync_executed | registered) = f(battery, network_type, user_engagement, os_policy)
    其中:
      battery: 低电量 → P ↓
      network_type: WiFi → P ↑, cellular → P ↓
      user_engagement: 频繁使用 → P ↑
      os_policy: iOS WebKit 限制严格 → P ↓ (可能趋近于 0)

  Step 2: 数据不丢失的充分条件
    不丢失 ⟺ 数据持久化到 IndexedDB BEFORE 注册 sync
    即: write(data, IndexedDB) → register(sync) → (sync_fires → read(data) → send)
    若 sync 永不触发: 数据仍保留在 IndexedDB，用户可手动重试

  Step 3: 幂等性要求
    设后台提交操作 f, 幂等 ⟺ f(f(x)) = f(x)
    必要性: sync 可能重复触发 (网络超时后重试)
    非幂等操作 (如扣款) 不可仅依赖 Background Sync

  Step 4: 有序性保证
    多个 pending 项的处理顺序:
      按 createdAt 排序 + 逐项处理 + 失败时 break
      保证: 若 item_k 失败，则 item_{k+1..n} 不提交
      避免: 乱序提交导致的因果倒置

结论 (定理 T-OFF2):
  Background Sync 的可靠性上界由操作系统策略决定，工程师只能控制下界:
    下界保证: IndexedDB 持久化 + 幂等操作 + 有序处理
    上界限制: P(sync_executed) ≤ 1，在 iOS 上可能 < 0.5
  高价值操作必须提供显式"重试"UI，不可完全依赖后台同步。
```

---

## 九、推理判定树/决策树

```text
离线优先架构缓存策略选择决策树
│
├─► 资源类型判定
│   ├─ [静态资源: JS/CSS/字体/图片] ──► Cache-First
│   │   └─ 安装时 precache (Workbox generateSW)
│   ├─ [API 数据] ──► Network-First (在线优先，离线回退缓存)
│   ├─ [内容页面] ──► Stale-While-Revalidate (立即返回缓存，后台更新)
│   ├─ [实时数据] ──► Network-Only (始终网络，不缓存)
│   └─ [离线 fallback] ──► Cache-Only (离线页面，如 /offline.html)
│
├─► 后台同步策略判定
│   ├─ [表单提交] ──► One-shot Background Sync
│   │   └─ 流程: IndexedDB outbox → register sync → SW 处理 → 成功删除
│   ├─ [内容刷新] ──► Periodic Background Sync (需 PWA 安装)
│   │   └─ 限制: Chrome 有限支持，iOS 不可用
│   └─ [推送通知] ──► Push API + Notification API
│
├─► 数据持久化判定
│   ├─ [结构化数据] ──► IndexedDB (ACID 事务)
│   ├─ [大文件] ──► OPFS (Worker 同步读写)
│   └─ [简单配置] ──► localStorage (字符串键值)
│
└─► 可靠性增强判定
    ├─ [必须送达] ──► IndexedDB + 显式重试 UI + 服务器去重 (idempotency key)
    ├─ [尽力送达] ──► Background Sync + 指数退避重试
    └─ [通知用户] ──► Sync 成功/失败均通过 Notification API 反馈
```

---

## 十、国际课程对齐标注

| 核心内容 | 国际课程 | 章节/主题映射 | 对齐强度 |
|---------|---------|-------------|---------|
| Service Worker 生命周期 | **Stanford CS 142** Web Applications | Progressive Web Apps, Service Workers | ★★★★★ |
| 缓存策略与新鲜度权衡 | **Berkeley CS 162** Operating Systems | Caching, Replacement Policies, Consistency | ★★★★★ |
| 离线优先与 AP 系统 | **Berkeley CS 162** | Distributed Systems, Availability, Partition Tolerance | ★★★★★ |
| 后台同步可靠性 | **Stanford CS 142** | Background Tasks, Event-Driven Architecture | ★★★★☆ |
| 幂等性与重试机制 | **Berkeley CS 162** | Fault Tolerance, Idempotent Operations | ★★★★★ |
| PWA 与安装模型 | **Stanford CS 142** | Web App Manifest, Installability | ★★★★☆ |

> **权威来源说明**：
>
> - **Stanford CS 142**（Web Applications）在 Progressive Web Apps 模块中系统讲授 Service Worker、Cache API 和 Background Sync 的工程实现，其课程项目要求学生构建支持离线访问的 Web 应用。
> - **Berkeley CS 162**（Operating Systems）在 Caching 和 Distributed Systems 模块中讲授缓存替换策略、可用性优先设计和容错机制，这些理论直接支撑离线优先架构的形式化分析。
> - **Jake Archibald** (2014): "Service Workers: an Introduction." *Google Developers*. Service Worker 技术的核心推广者，系统阐述了事件驱动执行模型。
> - **Alex Russell** (2015): "The Network is a Liability." *Progressive Web Apps Summit*. 提出离线优先设计哲学的关键人物。
> - **Tal Ater** (2017): *Building Progressive Web Apps*. O'Reilly. PWA 技术的权威工程指南，涵盖 Service Worker、Background Sync 和离线架构。
> - **Jim Gray** (1981): "The Transaction Concept: Virtues and Limitations." *VLDB*. 事务 ACID 性质的奠基论文，幂等性作为容错关键原则的提出者。
