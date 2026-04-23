# Service Worker 与 PWA：离线优先架构

> **来源映射**: View/03.md §3.2, View/05.md §4.3
> **国际权威参考**: W3C Service Workers Specification (Living Standard); Mozilla "Using Service Workers"; Google "PWA Checklist" (web.dev); Russell (2015) "Service Workers: The State of the Web"

---

## 一、知识体系思维导图

```text
Service Worker 与 PWA: 离线优先架构
│
├─► Service Worker 生命周期
│   ├─ 注册 (Register): navigator.serviceWorker.register('/sw.js')
│   ├─ 安装 (Install): event.waitUntil(cache.addAll(['/index.html', ...]))
│   ├─ 激活 (Activate): event.waitUntil(clients.claim())
│   ├─ 更新 (Update): 字节差异检测 → 新 SW 等待激活
│   └─ 终止 (Terminate): 事件驱动，空闲时自动终止
│
├─► 缓存策略矩阵
│   ├─ Cache-First: 缓存命中则返回，否则网络
│   ├─ Network-First: 网络优先，失败回退缓存
│   ├─ Stale-While-Revalidate: 返回缓存，后台更新
│   ├─ Network-Only: 始终网络 (不缓存)
│   └─ Cache-Only: 始终缓存 (离线应用)
│
├─► Background Sync
│   ├─ 延迟同步: 用户离线时排队，恢复后自动重试
│   ├─ 周期性同步: Periodic Background Sync (受限)
│   └─ 一次性同步: one-shot sync
│
├─► Push Notifications
│   ├─ Web Push Protocol: IETF RFC 8030
│   ├─ VAPID: 服务器身份验证 (Voluntary Application Server Identification)
│   ├─ Notification API: 系统级通知展示
│   └─ 权限模型: 用户授权 + 可撤销
│
└─► PWA 核心 checklist
    ├─ HTTPS (安全上下文必需)
    ├─ Web App Manifest (名称、图标、主题色、display mode)
    ├─ Service Worker (离线能力)
    ├─ 响应式设计
    └─ 安装提示 (beforeinstallprompt)
```

---

## 二、核心概念的形式化定义

### 定义 D16.13：Service Worker 的事件驱动生命周期

Service Worker 是一个**事件驱动的 Web Worker**，其生命周期可用状态机形式化：

```
状态机 𝓢𝓦:

  [parsed] --(register)--> [installing]
     |
     └─ 触发: navigator.serviceWorker.register()

  [installing] --(install success)--> [installed/waiting]
     |
     └─ 触发: install 事件完成
     └─ 注意: 若存在活跃 SW，新 SW 进入 waiting 状态

  [installed/waiting] --(skipWaiting or clients closed)--> [activating]
     |
     └─ 触发: 所有受控页面关闭，或调用 skipWaiting()

  [activating] --(activate success)--> [activated]
     |
     └─ 触发: activate 事件完成 (旧缓存清理)

  [activated] --(fetch/message/sync/push)--> [running]
     |
     └─ 触发: 事件处理

  [running] --(idle timeout)--> [terminated]
     |
     └─ Service Worker 不保持持久状态!
```

### 定义 D16.14：缓存一致性协议

Service Worker 作为客户端与服务器之间的**代理层**，定义缓存协议：

```
协议 SW-Cache:

  请求处理:
    Client --(fetch req)--> SW --(strategy)--> Response

  策略形式化:
    CacheFirst(req) = if hit(Cache, req) then Cache[req] else fetch(req)
    NetworkFirst(req) = try fetch(req) catch Cache[req]
    SWR(req) = return Cache[req] || fetch(req) && update(Cache, req)

  一致性约束:
    ∀req, SW 返回的响应必须满足 HTTP 语义 (status, headers, body)
    Cache 更新必须原子化 (先写副本，再交换引用)
```

### 定义 D16.15：离线优先的数据同步模型

```
设本地状态为 S_local，服务器状态为 S_server

离线优先协议:
  1. 读取: 始终从 S_local 读取 (可用性优先)
  2. 写入: 写入 S_local 并标记为 dirty，加入同步队列 Q
  3. 在线检测: 监听 online/offline 事件 + fetch 探活
  4. 同步: 当 online 时，按 FIFO 处理 Q:
           for op in Q:
             try:
               S_server' = apply(op, S_server)
               mark_clean(op)
             catch Conflict:
               resolve_conflict(op, S_server)
```

---

## 三、多维矩阵对比

### 3.1 缓存策略的适用场景矩阵

| 策略 | 网络假设 | 数据新鲜度 | 离线可用 | 实现复杂度 | 适用资源 |
|------|---------|-----------|---------|-----------|---------|
| **Cache-First** | 弱网/离线 | 低 (缓存期) | ✅ 是 | 低 | 静态资源 (JS/CSS/字体) |
| **Network-First** | 强网优先 | **最高** | ⚠️ 降级 | 低 | API 数据、用户特定内容 |
| **Stale-While-Revalidate** | 混合 | 中 (即时+后台) | ✅ 是 | 中 | 图片、半静态内容 |
| **Cache-Only** | 纯离线 | 低 | ✅ 是 | 低 | App Shell、离线应用 |
| **Network-Only** | 始终在线 | **最高** | ❌ 否 | 最低 | 支付、敏感操作 |
| **Race (竞速)** | 混合 |  whichever returns first | ⚠️ 不确定 | 中 | 非关键资源 |

### 3.2 PWA vs 原生应用 vs 传统 Web 的对比

| 维度 | 传统 Web | PWA | 原生应用 (iOS/Android) |
|------|---------|-----|----------------------|
| **安装** | 无需安装 | 可选安装 (Add to Home) | 应用商店下载 |
| **离线能力** | ❌ 无 | ✅ Service Worker | ✅ 原生实现 |
| **推送通知** | ❌ 无 | ✅ Push API | ✅ 原生 |
| **后台同步** | ❌ 无 | ⚠️ 受限 | ✅ 完全支持 |
| **系统集成** | 低 | 中 (分享、文件处理) | **高** |
| **更新机制** | 即时 | Service Worker 更新 | 应用商店审核 |
| **发现性** | SEO 友好 | SEO + 安装提示 | 应用商店搜索 |
| **性能上限** | JS 解释器 | JS 解释器 | 原生编译 |
| **权限模型** | 宽松 | 显式授权 | 安装时授权 |
| **开发成本** | 低 | 中 | 高 |

---

## 四、权威引用

> **W3C Service Workers Specification** (Living Standard, maintained by Jake Archibald et al.):
> "Service workers are a type of Web Worker. They are JavaScript files that run separately from the main browser thread, intercepting network requests, caching or retrieving resources from the cache, and delivering push messages." —— Service Worker 的权威标准化定义。

> **Alex Russell** (2015, "Service Workers: The State of the Web"):
> "Service workers are the most significant addition to the web platform since XMLHttpRequest. They give developers the power to build reliable, fast, and engaging experiences, even on flaky networks." —— Service Worker 作为 Web 平台关键基础设施的定位。

> **Jake Archibald** (Google Chrome DevRel, "The Service Worker Lifecycle"):
> "Service workers don't live forever. The browser may kill them at any time when they're not handling events. This means you can't rely on global state in a service worker." —— Service Worker 无状态性的关键工程约束。

> **Google web.dev** ("PWA Checklist"):
> "A Progressive Web App is a website that uses modern web capabilities to deliver an app-like experience. It must be reliable, fast, and engaging." —— PWA 的三要素定义：可靠、快速、 engaging。

---

## 五、工程实践与代码示例

### 5.1 生产级 Service Worker 实现

```typescript
// sw.ts (TypeScript，编译后注册)
const CACHE_NAME = 'app-cache-v2';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/static/main.js',
  '/static/styles.css',
  '/offline.html', // 离线回退页面
];

// 安装: 预缓存关键资源
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting()) // 立即激活
  );
});

// 激活: 清理旧缓存
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then(cacheNames =>
      Promise.all(
        cacheNames
          .filter(name => name !== CACHE_NAME)
          .map(name => caches.delete(name))
      )
    ).then(() => self.clients.claim()) // 立即控制所有客户端
  );
});

// 拦截请求: 策略矩阵
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  if (isStaticAsset(url)) {
    event.respondWith(staleWhileRevalidate(request));
  } else if (isAPIRequest(url)) {
    event.respondWith(networkFirstWithTimeout(request, 3000));
  } else {
    event.respondWith(networkFirst(request));
  }
});

// Stale-While-Revalidate 策略
async function staleWhileRevalidate(request: Request): Promise<Response> {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);

  const fetchPromise = fetch(request).then(response => {
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  }).catch(() => cached); // 网络失败回退缓存

  return cached || fetchPromise;
}

// Network-First + 超时回退
async function networkFirstWithTimeout(
  request: Request,
  timeoutMs: number
): Promise<Response> {
  const cache = await caches.open(CACHE_NAME);

  const timeoutPromise = new Promise<Response>((_, reject) =>
    setTimeout(() => reject(new Error('Timeout')), timeoutMs)
  );

  try {
    const networkResponse = await Promise.race([
      fetch(request),
      timeoutPromise
    ]);
    cache.put(request, networkResponse.clone());
    return networkResponse;
  } catch {
    const cached = await cache.match(request);
    if (cached) return cached;
    return caches.match('/offline.html') as Promise<Response>;
  }
}
```

### 5.2 Background Sync 实现离线写入

```typescript
// 主线程: 注册同步
async function savePostOffline(postData: PostData): Promise<void> {
  // 1. 写入 IndexedDB
  await db.posts.add({ ...postData, status: 'pending', synced: false });

  // 2. 注册后台同步
  const registration = await navigator.serviceWorker.ready;

  if ('sync' in registration) {
    await (registration as any).sync.register(`sync-post-${postData.id}`);
  } else {
    // 降级: 立即尝试同步
    await syncPost(postData);
  }
}

// Service Worker: 处理 sync 事件
self.addEventListener('sync', (event: any) => {
  if (event.tag.startsWith('sync-post-')) {
    event.waitUntil(syncPendingPosts());
  }
});

async function syncPendingPosts(): Promise<void> {
  const pending = await db.posts.where('synced').equals(false).toArray();

  for (const post of pending) {
    try {
      await fetch('/api/posts', {
        method: 'POST',
        body: JSON.stringify(post),
        headers: { 'Content-Type': 'application/json' }
      });
      await db.posts.update(post.id, { synced: true, status: 'synced' });
    } catch (error) {
      console.error('Sync failed for post', post.id, error);
      // 保留 pending 状态，下次 sync 重试
    }
  }
}
```

---

## 六、批判性总结

Service Worker 是 Web 平台向操作系统能力靠拢的最重要一步，它将浏览器从一个"文档查看器"转变为一个"应用运行时"，使得 Web 应用能够在离线、慢网和后台场景中保持功能可用。然而，这种能力的获得并非没有代价——Service Worker 引入了一层**不可见的代理逻辑**，它拦截网络请求、改写缓存行为、管理生命周期，使得前端应用的调试和推理复杂度呈指数级增长。

Service Worker 的最大工程陷阱在于其**生命周期的不直观性**。新版本的 SW 不会立即取代旧版本，而是进入 "waiting" 状态，直到所有受控页面关闭。这意味着用户可能在数小时甚至数天内继续使用旧版本，而开发者却误以为更新已生效。`skipWaiting()` 虽然可以强制激活，但可能导致新旧资源版本不匹配（如旧 HTML 引用新 CSS）。这种**缓存版本地狱**是 PWA 工程中最痛苦的调试场景之一。

Background Sync 和 Push API 进一步模糊了 Web 与原生应用的边界，但它们在 iOS Safari 上的支持长期滞后（Push 直到 2023 年才在 iOS 16.4 中启用），造成了严重的**平台碎片化**。Android/Chrome 上的 PWA 体验已接近原生，但 iOS 的限制（无后台同步、通知权限更严格、存储配额更小）使得"一次编写，到处运行"的 PWA 愿景仍未完全实现。

更深层的批判在于：**离线优先不是免费午餐**。将数据持久化在客户端意味着需要处理同步冲突、数据迁移、隐私合规（GDPR "被遗忘权"要求能够彻底删除用户数据）和存储配额管理。一个简单的"离线可用"功能可能演变为需要 CRDT 合并、版本向量、端到端加密的复杂分布式系统。2026 年的务实建议是：对于内容消费型应用（新闻、文档），Service Worker + Cache-First 策略已足够；对于生产力工具（笔记、任务管理），应认真评估 Local-First 架构和 CRDT 库（如 Yjs 或 ElectricSQL）；对于社交应用，Push Notification 的收益需与权限请求导致的用户流失率权衡。Service Worker 是一把双刃剑——它赋予了 Web 应用对抗网络不确定性的超能力，但也要求团队具备分布式系统设计的思维深度。
