# 五种渲染拓扑：CSR 到 SSR 到 RSC

> **来源映射**: View/05.md §5.1, View/03.md §1.2
> **国际权威参考**: Vercel "Rendering on the Web" (2019); React Server Components RFC (React Labs, 2020); Next.js App Router Documentation (2023-2026); Malte Ubl (Vercel) "The Edge Computing Spectrum"

---

## 一、知识体系思维导图

```text
五种渲染拓扑: CSR 到 SSR 到 RSC
│
├─► 拓扑 I: 经典 CSR (Client-Side Rendering)
│   ├─ 网络路径: Client ←(HTML)→ CDN ←(API)→ Origin
│   ├─ 延迟公式: L_total = L_cdn + L_js_exec + Σ(L_api × n)
│   ├─ 首屏: ❌ JS 阻塞渲染
│   └─ 交互: ✅ 完全 hydrated，SPA 体验
│
├─► 拓扑 II: SSR + Hydration
│   ├─ 网络路径: Client ←(HTML)→ CDN ←(SSR)→ Origin
│   ├─ 延迟公式: L_total = L_cdn + L_ssr + L_hydration
│   ├─ 首屏: ✅ HTML 立即可见
│   └─ 交互: ⚠️ hydration 重复执行 (注水税)
│
├─► 拓扑 III: SSG (Static Site Generation)
│   ├─ 网络路径: Client ←(HTML)→ CDN ←(Build Time)
│   ├─ 延迟公式: L_total ≈ L_cdn (无服务器计算)
│   ├─ 首屏: ✅ 最优 (纯静态)
│   └─ 一致性: ❌ ε = ∞ (构建时快照)
│
├─► 拓扑 IV: RSC + Edge (React Server Components)
│   ├─ 网络路径: Client ←(RSC Payload)→ Edge ←(API)→ Origin
│   ├─ 延迟公式: L_total = L_edge + L_rsc_stream + L_client_cc
│   ├─ 首屏: ✅ 流式渲染
│   └─ 边界: ⚠️ 服务端/客户端组件拆分增加心智负担
│
├─► 拓扑 V: PPR (Partial Prerendering)
│   ├─ 网络路径: Client ←(Shell+Stream)→ Edge
│   ├─ 延迟公式: L_total = L_shell + L_stream_dynamic
│   ├─ 首屏: ✅ 静态壳立即显示
│   └─ 动态: ⚠️ Suspense 边界内流式填充
│
└─► 渲染决策树
    ├─ 内容变化频率?
    ├─ 个性化程度?
    ├─ 交互复杂度?
    └─ 首屏延迟容忍?
```

---

## 二、核心概念的形式化定义

### 定义 D16.1：渲染拓扑的形式化

设渲染请求在时间 t 到达，定义渲染函数 R: Request × Time → HTML：

```
CSR:    R(req, t) = R_client(R_initial(), t)
        // 初始 HTML 为空壳，完整渲染在客户端执行

SSR:    R(req, t) = R_server(req, t)
        // 服务器每次请求时完整渲染

SSG:    R(req, t) = R_server(req, t₀)  (t₀ ≪ t 为构建时间)
        // 渲染结果在构建时确定，请求时仅读取缓存

ISR:    R(req, t) = if t - t_last < TTL
                     then Cache(req)
                     else R_server(req, t) async
        // 增量静态再生，后台更新

RSC:    R(req, t) = Serialize(Γ_server(req, t))
        // 服务端渲染组件树为 RSC Payload，客户端反序列化

PPR:    R(req, t) = R_shell(req, t₀) ⊕ Stream(R_dynamic(req, t))
        // 静态壳与动态流的组合
```

### 定义 D16.2：延迟分解模型

```
L_total = L_dns + L_tcp + L_tls + L_ttfb + L_download + L_parse + L_exec + L_render

其中各拓扑的关键差异:
  CSR:   L_ttfb 低, L_exec 极高 (JS bundle), L_render 在客户端
  SSR:   L_ttfb 中 (服务器渲染), L_exec 中 (hydration), L_render 重复
  SSG:   L_ttfb 最低, L_exec 低, L_render 一次
  RSC:   L_ttfb 中 (Edge), L_exec 低 ( selective hydration), L_render 流式
  PPR:   L_ttfb 最低 (shell cached), L_exec 增量, L_render 渐进
```

### 定义 D16.3：Hydration 的形式化

Hydration 是将静态 HTML 与客户端 JavaScript 状态**对齐**的过程：

```
设服务器渲染产出 HTML_tree 和初始状态 S₀
设客户端 React 组件函数为 C: Props × State → VDOM

Hydration 正确性条件:
  HTML_tree ≅ DOM(VirtualDOM(C(props, S₀)))

其中 ≅ 表示结构同构 (节点类型、属性、子节点顺序一致)

"注水税" (Hydration Tax):
  T_hydrate = T_reconcile(HTML_tree, VDOM) + T_event_attach + T_state_init
  // 客户端重复执行了服务端已经完成的渲染逻辑
```

---

## 三、多维矩阵对比

### 3.1 五种渲染拓扑的全面对比

| 维度 | CSR | SSR | SSG | ISR | RSC | PPR |
|------|-----|-----|-----|-----|-----|-----|
| **TTFB** | 优 | 中 | **最优** | **最优** | 良 | **最优** |
| **FCP** | 差 | 良 | **最优** | **最优** | 良 | **最优** |
| **TTI** | 中 | 中 | 优 | 优 | 良 | 良 |
| **首屏一致性** | 强 | 强 | 弱 (快照) | 中 | 强 | 壳强/动态中 |
| **服务器成本** | 低 | 高 | 极低 | 低 | 中 | 低 |
| **构建成本** | 低 | 低 | 高 | 中 | 低 | 中 |
| **动态数据** | ✅ 实时 | ✅ 实时 | ❌ 静态 | ⚠️ 延迟 | ✅ 实时 | ✅ 混合 |
| **个性化** | ✅ 完全 | ✅ 完全 | ❌ 无 | ❌ 无 | ✅ 边缘 | ⚠️ 壳通用 |
| **JS Bundle** | 大 | 大 | 中 | 中 | 小 (selective) | 小 |
| **Edge 可行** | ❌ | ⚠️ | ✅ | ✅ | ✅ | ✅ |

### 3.2 渲染决策树矩阵

| 场景特征 | 推荐拓扑 | 理由 |
|---------|---------|------|
| 后台管理系统 / 纯 SPA | CSR | 高交互密度，首屏延迟可容忍 |
| 营销页面 / 博客 / 文档 | SSG | 内容静态，追求极致首屏 |
| 电商商品页 / 新闻站 | ISR | 内容 semi-static，需要时效性 |
| 社交网络 / 实时仪表板 | SSR + RSC | 高动态 + 需要 SEO |
| 混合内容平台 (Vercel/Next) | PPR | 静态壳 + 动态内容的黄金平衡 |
| 低功耗设备 / 慢网络 | SSG/Islands | 最小化 JS 执行 |

---

## 四、权威引用

> **Vercel Engineering Blog** (2019, "Rendering on the Web"):
> "The decision between server rendering and client rendering is not binary. Modern frameworks support a spectrum of rendering modes, from fully static to fully dynamic." —— 渲染模式并非二选一，而是一个连续光谱。

> **Dan Abramov & Lauren Tan** (React Labs, 2020, React Server Components RFC):
> "Server Components allow developers to build apps that span the server and client, enabling a new hybrid approach that combines the rich interactivity of client-side apps with the improved performance of server rendering." —— RSC 的核心目标：交互性与性能的混合平衡。

> **Malte Ubl** (Vercel CTO):
> "The edge is not just a CDN; it's a place where you can run code close to the user. Partial Prerendering pushes this idea to its logical conclusion by pre-rendering the static parts of a page and streaming the rest." —— PPR 是边缘计算在渲染层面的逻辑延伸。

> **Ryan Carniato** (SolidJS 作者, 2023):
> "Hydration is a tax we pay for the convenience of writing components once and running them twice. Islands architecture tries to avoid this tax by only hydrating the parts that need it." —— Islands 架构对 hydration 重复计算问题的批判。

---

## 五、工程实践与代码示例

### 5.1 Next.js App Router 中的渲染模式选择

```typescript
// SSG: 构建时生成 (默认)
export default async function BlogPage() {
  const posts = await getAllPosts(); // 构建时调用
  return <PostList posts={posts} />;
}

// SSR: 强制动态渲染
export const dynamic = 'force-dynamic';
export default async function Dashboard() {
  const data = await getRealtimeData(); // 每次请求时调用
  return <Dashboard data={data} />;
}

// ISR: 增量静态再生
export const revalidate = 60; // 60 秒后后台重新生成
export default async function ProductPage({ params }: { params: { id: string } }) {
  const product = await getProduct(params.id);
  return <ProductDetail product={product} />;
}

// RSC: 服务端组件 (默认)
import { ClientChart } from './ClientChart'; // 客户端组件需显式导入

export default async function AnalyticsPage() {
  const data = await fetchAnalytics(); // 仅在服务端执行
  return (
    <div>
      <ServerTable data={data} />
      <ClientChart initialData={data} /> {/* 客户端交互组件 */}
    </div>
  );
}

// PPR: 部分预渲染 (Next.js 14+)
export const experimental_ppr = true;
export default function Page() {
  return (
    <div>
      <StaticShell /> {/* 构建时预渲染 */}
      <Suspense fallback={<Skeleton />}>
        <DynamicContent /> {/* 流式填充 */}
      </Suspense>
    </div>
  );
}
```

### 5.2 渲染决策的形式化流程

```typescript
type PageCharacteristics = {
  contentFreshness: 'static' | 'semi-static' | 'dynamic';
  interactionDensity: 'none' | 'low' | 'high';
  personalization: 'none' | 'geo' | 'user-specific';
  seoCritical: boolean;
};

function selectRenderingStrategy(c: PageCharacteristics): string {
  if (!c.seoCritical && c.interactionDensity === 'high') return 'CSR';
  if (c.contentFreshness === 'static' && c.personalization === 'none') return 'SSG';
  if (c.contentFreshness === 'semi-static') return 'ISR';
  if (c.personalization === 'user-specific') return 'SSR + RSC';
  return 'PPR'; // 默认: 混合策略
}
```

---

## 六、批判性总结

前端渲染架构在过去十年经历了从 CSR 到 SSR 再到 RSC/PPR 的螺旋式演进，每一次范式转移都声称解决了前一代的问题，却又引入了新的复杂性。CSR 的问题在于首屏白屏和 SEO 不友好，SSR 通过服务器预渲染解决了首屏但引入了 hydration 重复执行的"注水税"，SSG 将渲染推向构建时获得了极致性能但牺牲了动态性，ISR 试图在静态与动态之间找到平衡却带来了缓存失效的复杂性，RSC 通过服务端组件减少了客户端 bundle 却制造了"网络边界成为编程模型一部分"的心智负担，而 PPR 则在所有这些模式之上增加了一层"静态壳 + 动态流"的分割逻辑。

这种演进的内在驱动力是**矛盾的不可能性三角**：首屏性能、交互响应性和动态数据 freshness 无法同时最大化。每一种拓扑都是对这个三角形的不同权衡。PPR 作为 2024-2026 年的前沿方案，其本质是将页面拆分为"可预渲染的部分"和"必须动态的部分"，但这种拆分不是自动的——开发者必须显式地标记 Suspense 边界，理解哪些数据可以在构建时获取、哪些必须在请求时获取。这种**认知负载的转移**（从运行时性能优化转移到架构设计时的模式选择）是否是净收益，取决于团队的规模和成熟度。

更深层的批判在于：渲染模式的多样性虽然提供了灵活性，但也导致了**框架锁定和可移植性危机**。一个深度依赖 Next.js App Router 的 RSC 应用几乎无法迁移到 Astro 或 Remix，因为 RSC 的协议、序列化格式和组件边界语义是 React 特有的。这违背了 Web 的开放性和标准化精神。2026 年的最佳实践应该是"渐进式采用"：营销页面用 SSG，后台系统用 CSR，关键业务流用 PPR，而不是将所有页面统一在单一模式下。理解每种拓扑的延迟模型和一致性特征，比盲目追随最新框架更为重要。
