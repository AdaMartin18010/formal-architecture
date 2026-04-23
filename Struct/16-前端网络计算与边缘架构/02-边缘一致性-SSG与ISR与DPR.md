# 边缘一致性：SSG 与 ISR 与 DPR

> **来源映射**: View/05.md §5.2, View/03.md §1.3
> **国际权威参考**: Vercel "Incremental Static Regeneration" (2020); RFC 5861 "HTTP Cache-Control Extensions for Stale Content"; Cloudflare "Distributed Persistent Rendering" (2022); Fielding & Taylor (2002) "Principled Design of the Modern Web Architecture"

---

## 一、知识体系思维导图

```text
边缘一致性: SSG 与 ISR 与 DPR
│
├─► SSG (Static Site Generation) —— 构建时一致性
│   ├─ 形式化: s_edge(t) = s_origin(t₀), t₀ ≪ t
│   ├─ 陈旧度: ε = ∞ (无限陈旧)
│   ├─ 延迟: L ≈ L_cdn (无计算)
│   └─ 适用: 文档、博客、营销页
│
├─► ISR (Incremental Static Regeneration) —— 后台刷新一致性
│   ├─ 形式化: s_edge(t) = s_origin(t₀), 后台异步更新至 t₁
│   ├─ 陈旧度: ε = |s(t₀) - s(t₁)|,  bounded by TTL
│   ├─ Stale-While-Revalidate (SWR): RFC 5861
│   └─ 竞争条件: 首次访问触发再生，后续访问可能拿到旧版本
│
├─► DPR (Distributed Persistent Rendering) —— 按需持久化
│   ├─ 形式化: s_edge(t) = if cached(t) then Cache else Render(t)
│   ├─ 边缘存储: KV store (Vercel KV, Cloudflare KV)
│   ├─ 一致性协议: 首次渲染写入边缘，后续读取边缘缓存
│   └─ 失效策略: TTL + 显式 revalidate + tag-based purge
│
├─► 一致性模型谱系
│   ├─ 强一致 (Strong): s_edge(t) ≡ s_origin(t)
│   ├─ 顺序一致 (Sequential): 所有节点看到相同的更新顺序
│   ├─ 因果一致 (Causal): 因果相关的操作顺序一致
│   ├─ 最终一致 (Eventual): lim_{t→∞} s_edge(t) = s_origin(t)
│   └─ 前端映射: 所有边缘渲染策略均为最终一致或更弱
│
└─► 缓存失效策略
    ├─ 时间驱动 (TTL): 固定过期时间
    ├─ 事件驱动 (Tag-based): 按内容标签批量失效
    ├─ 按需驱动 (On-demand): 显式 API 调用 revalidate
    └─ 混合策略: TTL + Stale-While-Revalidate + Background Refresh
```

---

## 二、核心概念的形式化定义

### 定义 D16.4：边缘渲染一致性

设源服务器状态为 s_origin(t)，边缘节点状态为 s_edge(t)，定义一致性偏差：

```
一致性偏差: ε(t) = ‖s_edge(t) - s_origin(t)‖

其中 ‖·‖ 是状态空间上的适当度量 (如语义差异、字段差异等)。

强一致: ε(t) = 0  ∀t
最终一致: lim_{t→∞} ε(t) = 0  (在有限时间内收敛)
有界不一致: ε(t) ≤ ε_max  ∀t
```

### 定义 D16.5：Stale-While-Revalidate 的形式化

RFC 5861 定义的 HTTP Cache-Control 扩展：

```
Cache-Control: max-age=<seconds>, stale-while-revalidate=<seconds>

语义:
  阶段 1 (0 ≤ Δt < max-age): 缓存新鲜，直接返回 s_edge
  阶段 2 (max-age ≤ Δt < max-age + stale-while-revalidate):
         返回陈旧的 s_edge，同时后台发起 revalidate 请求
  阶段 3 (Δt ≥ max-age + stale-while-revalidate):
         阻塞等待 revalidate 完成，返回最新 s_origin

形式化状态机:
  FRESH --(Δt > max-age)--> STALE --(revalidate complete)--> FRESH
                            |
                            --(Δt > max-age + swr)--> BLOCKING
```

### 定义 D16.6：DPR 的缓存一致性协议

```
DPR 协议 (简化):

  Client --(GET /page)--> Edge
    |
    ├─ Cache HIT: return cached_html
    |
    └─ Cache MISS:
         Edge --(render request)--> Origin
         Origin --(html)--> Edge
         Edge --(store in KV)--> Edge KV
         Edge --(return html)--> Client

  后续请求:
    Client --(GET /page)--> Edge --(KV HIT)--> return cached_html

  失效:
    Admin --(POST /revalidate)--> Edge --(purge KV key)--> OK
```

### 定理 T16.1：ISR 存在短暂的一致性窗口

```text
前提: ISR 配置 revalidate = T 秒

定理: 在以下时间窗口内，不同用户可能看到不同版本:

  [t₀, t₀ + T + L_revalidate]

其中:
  t₀ = 上次再生完成时间
  T = TTL 配置
  L_revalidate = 再生延迟 (渲染 + 传播)

证明:
  用户 A 在 t₁ = t₀ + T - δ 访问 → 得到版本 V₀
  用户 B 在 t₂ = t₀ + T + δ 访问 → 触发后台再生
  用户 C 在 t₃ = t₀ + T + L_revalidate/2 访问 → 可能得到 V₀ 或 V₁

  ∵ 边缘节点之间无全局锁
  ∴ 在再生传播期间存在版本分歧

∴ ISR 最多提供最终一致性，非顺序一致性 ∎
```

---

## 三、多维矩阵对比

### 3.1 三种边缘渲染策略的形式化对比

| 维度 | SSG | ISR | DPR |
|------|-----|-----|-----|
| **状态公式** | s(t) = s(t₀) | s(t) = s(t₀) 后台刷新 | s(t) = f(cache, origin) |
| **陈旧度 ε** | ∞ | ≤ TTL + L_revalidate | ≤ TTL |
| **首访问延迟** | 最低 | 最低 | 中 (若 miss 需渲染) |
| **缓存命中** | 100% | 100% | 随时间增加 |
| **服务器负载** | 零 | 低 (后台再生) | 中 (按需渲染) |
| **存储需求** | 高 (所有页面预构建) | 高 | 低 (仅访问过的页面) |
| **构建时间** | O(Pages) | O(Pages) | O(1) |
| **个性化支持** | ❌ 无 | ❌ 无 | ⚠️ 有限 |
| **边缘存储依赖** | 无 | 无 | ✅ KV Store |
| **一致性级别** | 快照一致 | 最终一致 | 最终一致 |

### 3.2 缓存失效策略对比

| 策略 | 触发条件 | 粒度 | 延迟 | 复杂度 | 适用场景 |
|------|---------|------|------|--------|---------|
| **TTL** | 时间到期 | 页面级 | 低 | 低 | 新闻、博客 |
| **Tag-based** | 内容更新事件 | 标签组 | 中 | 中 | 电商 (SKU 更新) |
| **Path-based** | 特定路径 | 单页 | 低 | 低 | 页面编辑 |
| **Webhook** | 外部系统通知 | 自定义 | 低 | 高 | CMS 集成 |
| **按需 (On-demand)** | 用户/API 调用 | 页面/标签 | 即时 | 低 | 紧急更新 |
| **Background Refresh** | 定时任务 | 全局 | 中 | 中 | 预热 |

---

## 四、权威引用

> **Roy Fielding & Richard Taylor** (2002, "Principled Design of the Modern Web Architecture", ACM TOIT):
> "REST does not attempt to capture all of the semantics of the Web, but rather focuses on the constraints that are visible to the network interface." —— 缓存约束是 REST 架构风格的核心可见约束之一，边缘渲染策略直接继承了这一哲学。

> **RFC 5861** ("HTTP Cache-Control Extensions for Stale Content", 2010):
> "The stale-while-revalidate response directive indicates that caches MAY serve the response in which it appears after it becomes stale, up to the indicated number of seconds." —— ISR 的 HTTP 标准化基础。

> **Lee Byron** (GraphQL 共同创始人, 关于缓存):
> "The hardest problem in computer science is not naming things or cache invalidation. It is naming things while cache invalidation is happening." —— 缓存失效的工程复杂性。

> **Guillermo Rauch** (Vercel CEO):
> "Incremental Static Regeneration gives you the best of both worlds: the performance of static sites with the freshness of dynamic rendering." —— ISR 的价值主张。

---

## 五、工程实践与代码示例

### 5.1 Next.js ISR 与按需重验证

```typescript
// app/blog/[slug]/page.tsx
// ISR: 每 60 秒后台重新生成
export const revalidate = 60;

export async function generateStaticParams() {
  const posts = await fetch('https://api.example.com/posts').then(r => r.json());
  return posts.map((p: { slug: string }) => ({ slug: p.slug }));
}

export default async function BlogPost({ params }: { params: { slug: string } }) {
  const post = await fetch(`https://api.example.com/posts/${params.slug}`, {
    next: { revalidate: 60 }
  }).then(r => r.json());

  return <article>{post.content}</article>;
}

// 按需重验证 API (App Router)
// app/api/revalidate/route.ts
import { revalidatePath, revalidateTag } from 'next/cache';
import { NextRequest } from 'next/server';

export async function POST(request: NextRequest) {
  const { path, tag, secret } = await request.json();

  if (secret !== process.env.REVALIDATE_SECRET) {
    return Response.json({ error: 'Invalid secret' }, { status: 401 });
  }

  if (path) {
    revalidatePath(path);      // 路径级失效
    return Response.json({ revalidated: true, path });
  }

  if (tag) {
    revalidateTag(tag);        // 标签级失效 (批量)
    return Response.json({ revalidated: true, tag });
  }

  return Response.json({ error: 'Missing path or tag' }, { status: 400 });
}
```

### 5.2 Vercel KV 实现 DPR 边缘缓存

```typescript
import { kv } from '@vercel/kv';

interface CacheEntry {
  html: string;
  revalidatedAt: number;
  tags?: string[];
}

const TTL_SECONDS = 3600;

export async function getOrRenderPage(
  key: string,
  renderFn: () => Promise<string>,
  tags?: string[]
): Promise<string> {
  // 1. 尝试读取边缘 KV
  const cached = await kv.get<CacheEntry>(key);
  const now = Date.now();

  if (cached && (now - cached.revalidatedAt) < TTL_SECONDS * 1000) {
    // Cache HIT
    return cached.html;
  }

  // 2. Cache MISS 或过期: 渲染并存储
  const html = await renderFn();

  await kv.set(key, {
    html,
    revalidatedAt: now,
    tags,
  });

  return html;
}

// 标签批量失效
export async function invalidateByTag(tag: string): Promise<number> {
  // 扫描并删除匹配标签的 KV 条目
  // 注: 实际生产环境应使用 Vercel 的 revalidateTag 或 Cloudflare Purge API
  const keys = await kv.keys('*');
  let count = 0;

  for (const key of keys) {
    const entry = await kv.get<CacheEntry>(key);
    if (entry?.tags?.includes(tag)) {
      await kv.del(key);
      count++;
    }
  }

  return count;
}
```

---

## 六、批判性总结

SSG、ISR 和 DPR 构成了前端边缘渲染的一致性光谱，从"绝对静态但无限陈旧"到"按需动态但最终一致"。这三种策略的共同前提是**接受不一致性以换取性能和可扩展性**——这是分布式系统设计的经典权衡，只是在边缘渲染场景中被重新演绎。

ISR 的"Stale-While-Revalidate"机制在工程上极为巧妙：它利用 HTTP 缓存语义（RFC 5861）和边缘节点的局部性，在用户体验不受影响的前提下实现后台刷新。但这种机制隐藏了一个危险的**竞争条件**：当内容更新涉及多个相关页面时，ISR 的独立再生可能导致用户在短时间内看到"页面 A 已更新但页面 B 仍陈旧"的碎片化视图。对于电商平台，这意味着商品详情页显示新价格而购物车页面仍显示旧价格——一种业务上不可接受的不一致。

DPR 试图通过"按需渲染 + 边缘持久化"解决 SSG 的构建时间爆炸问题，但它引入了新的复杂性：边缘 KV 存储的跨区域复制延迟、缓存键的设计空间爆炸、以及"冷启动"（首个用户触发渲染）的延迟惩罚。Vercel KV 和 Cloudflare KV 虽然提供了全球一致的键值存储，但其一致性模型通常是最终一致，在高写入场景下可能出现 read-your-writes 失败。

2026 年的最佳实践应该是**分层一致性策略**：核心商业数据（价格、库存）通过短 TTL + 显式失效保证近实时一致；辅助内容（推荐、评论）通过 ISR 接受分钟级延迟；静态外壳（导航、页脚）通过 SSG 永久缓存。一致性不是非黑即白的属性，而是一个可以根据业务语义精细调节的连续参数。边缘渲染的真正挑战不在于技术实现，而在于**让产品团队理解和接受"不同程度的一致性"这一概念**，并为之设计相应的用户体验（如"内容可能已更新，刷新查看"的提示）。
