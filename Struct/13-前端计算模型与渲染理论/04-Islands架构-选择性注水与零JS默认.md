# Islands 架构：选择性注水与零 JS 默认

> **来源映射**: View/03.md §1.2, View/05.md §5.1
> **国际权威参考**: Jason Miller "Islands Architecture" (2020); Astro Documentation; Deno Fresh Documentation; McIlroy "Mass Produced Software Components" (1968, NATO 软件工程会议) — 组件化思想的学术源头

---

## 一、知识体系思维导图

```text
Islands 架构
│
├─► 核心隐喻
│   ├─ 页面 = 静态 HTML 海洋 + 交互式 Islands (孤岛)
│   ├─ 默认: JS = ∅ (纯静态 HTML 输出)
│   └─ 例外: 仅在有交互需求的组件上激活 JS
│
├─► 选择性注水策略 (Selective Hydration)
│   ├─ idle:      浏览器空闲时注水 (requestIdleCallback)
│   ├─ visible:   进入视口时注水 (IntersectionObserver)
│   ├─ media:     媒体查询匹配时注水 (matchMedia)
│   ├─ load:      页面加载完成后立即注水
│   └─ client:only: 强制客户端渲染 (无服务端输出)
│
├─► 计算边界迁移
│   ├─ SPA: 应用级 hydration → 整棵组件树激活
│   ├─ SSR: 页面级 hydration → 整页激活
│   └─ Islands: 组件级 hydration → 精确控制交互边界
│
└─► 性能模型
    ├─ 首屏 L_total = L_cdn + Σ(L_island × p_activate)
    ├─ JS 体积: 仅交互组件的框架运行时 + 业务逻辑
    └─ 零 JS 默认: 内容页实现理论最小 JS 传输量
```

---

## 二、核心概念的形式化定义

### 2.1 Islands 架构的集合论语义

```text
定义 (Islands 页面):
  设页面 P 为 DOM 树的子集，Islands 为需客户端激活的交互组件集合
  P = StaticHTML ∪ Hydrate(Islands)
  其中:
    StaticHTML ∩ JS_runtime = ∅      (静态部分无框架运行时)
    ∀island ∈ Islands, island.hydrate(strategy) → island.interactive = true

定义 (零 JS 默认公理):
  默认条件: 若组件 c 无交互属性 (client:*, onclick 等)，则
    c ∈ StaticHTML 且 c 不携带任何 JS 运行时代码
  形式化: ¬interactive(c) ⟹ JS(c) = ∅

延迟成本模型:
  设首屏加载时间 L_total = L_html + L_css + L_islands
  其中 L_islands = Σ_{i∈Islands} (size(i.bundle) × delay(i.strategy))
  策略函数:
    delay(idle)     = f(browserIdle)  ∈ [0, +∞)
    delay(visible)  = f(viewportEntry) ∈ [0, +∞)
    delay(load)     = 0               (立即)
    delay(client)   = L_html          (与 HTML 同步)
```

### 2.2 选择性注水的策略谱系

```text
定义 (Hydration 策略偏序):
  设 urgency: Strategy → ℕ 为紧急度映射
    load      → 0  (最高优先级)
    visible   → 1  (中优先级，与用户滚动相关)
    idle      → 2  (最低优先级，后台执行)
    client    → 特殊 (无服务端输出，纯客户端)

注水触发条件:
  load:      DOMContentLoaded 事件
  visible:   IntersectionObserver(entry.isIntersecting)
  idle:      requestIdleCallback(callback, { timeout })
  media:     window.matchMedia(query).matches

 Islands 通信约束:
  静态 HTML 与 Island 之间通过事件冒泡/自定义事件通信
  Island 与 Island 之间通过全局事件总线或共享状态 (Nano Stores) 通信
  跨 Island 直接引用被禁止 (保持边界隔离)
```

### 2.3 与 SSR/SPA 的形式化对比

```text
SPA (单页应用):
  JS_bundle = FrameworkRuntime + AppLogic + Components
  HydrationCost = O(|ComponentTree|)  (整棵组件树注水)

SSR + Hydration (Next.js Pages / Nuxt 2):
  JS_bundle = FrameworkRuntime + AppLogic + Components
  HydrationCost = O(|PageTree|)       (整页注水)
  优势: 首屏 HTML 可立即渲染
  劣势: 仍需下载完整框架运行时 + 注水整页

Islands (Astro / Fresh):
  JS_bundle = Σ_{i∈Islands} (FrameworkRuntime_i + ComponentLogic_i)
  HydrationCost = O(|Islands|)        (仅交互组件注水)
  优势: 静态内容零 JS 开销，交互组件精确控制
  劣势: 多 Islands 可能重复加载框架运行时 (若不共享)
```

---

## 三、多维矩阵对比

| 维度 | Islands (Astro) | SSR + Hydration (Next.js) | SPA (React/Vue) | 纯静态 (Jekyll) |
|------|----------------|---------------------------|-----------------|-----------------|
| **默认 JS 体积** | **理论最小** | 完整框架运行时 | 完整应用 Bundle | **0** |
| **首屏 TTFB** | **优** (静态 CDN) | 中 (服务端渲染耗时) | 差 (JS 阻塞) | **优** |
| **交互一致性** | 中 (按需激活) | 优 (统一注水) | **优** | 无 |
| **SEO** | **优** | **优** | 需 SSR 辅助 | **优** |
| **构建复杂度** | 低 | 中 | 低 | **极低** |
| **动态数据获取** | 需 Island 或 API | 原生支持 | 原生支持 | 不支持 |
| **框架运行时共享** | 需配置 | 天然单一 | 天然单一 | N/A |
| **适用场景** | **内容驱动** | **混合应用** | **高交互应用** | 文档/博客 |

---

## 四、权威引用

> **Jason Miller** (Preact 作者, "Islands Architecture", 2020):
> "The islands pattern encourages server-rendering of pages with small, isolated 'islands' of interactivity."

> **Fred K. Schott** (Astro 作者):
> "Ship less JavaScript, faster. Astro is the web framework for content-driven websites."

> **Ryan Dahl** (Deno / Fresh 作者):
> "Fresh uses a different architecture from the ground up. There is no build step and the code runs on the server by default."

> **Douglas McIlroy** (NATO 软件工程会议, 1968):
> "We should aspire to have a software components industry, where software is assembled from off-the-shelf parts." — Islands 的组件隔离思想可追溯至此。

---

## 五、工程实践与代码示例

### 5.1 Astro Islands 的声明式 hydration 指令

```astro
---
// 服务端执行: 纯静态 HTML 输出
import Counter from '../components/Counter.jsx';
---

<!-- 静态内容: 零 JS -->
<h1>欢迎来到我的博客</h1>
<p>这是一段纯静态内容，不携带任何 JavaScript。</p>

<!-- Island 1: 页面加载完成后立即注水 -->
<Counter client:load initial={0} />

<!-- Island 2: 进入视口时注水 (懒加载交互) -->
<ImageCarousel client:visible />

<!-- Island 3: 浏览器空闲时注水 (低优先级) -->
<CommentSection client:idle />

<!-- Island 4: 仅客户端渲染 (无服务端输出) -->
<BrowserOnlyChart client:only="react" />
```

### 5.2 Fresh (Deno) 的零构建 Islands 模型

```tsx
// routes/index.tsx —— 服务端渲染为 HTML
import { useSignal } from "@preact/signals";
import Counter from "../islands/Counter.tsx";

export default function HomePage() {
  return (
    <div>
      <h1>静态标题</h1>
      {/* 仅 Counter 组件被注水，其余为纯 HTML */}
      <Counter start={3} />
    </div>
  );
}

// islands/Counter.tsx —— 自动识别为 Island
import { useSignal } from "@preact/signals";

export default function Counter({ start }) {
  const count = useSignal(start);
  return <button onClick={() => count.value++}>{count}</button>;
}
```

---

## 六、批判性总结

Islands 架构是前端渲染理论中「渐进增强」哲学的当代极致表达。它将 Web 的原始语义——HTML 作为文档格式、CSS 作为表现层、JS 作为行为增强——从被 SPA 范式淹没的历史中重新拯救出来，并以形式化的「零 JS 默认」公理确立了新的架构基准。从集合论视角审视，Islands 将页面 P 划分为两个互不相交的子集：StaticHTML（无运行时依赖的纯标记）与 Hydrate(Islands)（需客户端激活的交互组件），这种划分在理论上实现了「内容」与「行为」的正交分离。

然而，Islands 架构面临的挑战同样深刻。首先是**框架运行时的重复加载问题**：当多个 Islands 使用不同框架（如一个 React Island、一个 Vue Island、一个 Svelte Island）时，用户需下载多份框架运行时，这可能抵消甚至逆转「零 JS 默认」带来的体积优势。Astro 的「群岛间框架共享」机制虽然缓解了这一问题，却引入了构建配置的复杂性。其次是**状态共享的边界困境**：Islands 之间的通信被设计为松耦合（事件总线或 Nano Stores），但在实际工程中，「购物车状态跨越三个 Island」的场景要求开发者手动管理跨边界状态同步，这在某种程度上复刻了微前端的状态碎片化难题。

更深层的理论批判指向 Islands 的**适用域边界**。该架构对「内容驱动」站点（博客、文档、营销页）是近乎完美的匹配，但对于「应用驱动」场景（SaaS 后台、实时协作工具、数据可视化仪表盘），交互密度之高使得几乎所有组件都成为 Island，此时 Islands 退化为「带有复杂构建步骤的 SPA」。2026 年的技术共识是：Islands 不是 SPA 的替代者，而是前端架构光谱上的一个重要节点——它与 SSR、RSC、SPA 共同构成了「按交互密度选择渲染策略」的连续体，而非非此即彼的排他选项。
