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


---

## 七、概念属性关系网络

| 概念A | 关系 | 概念B | 关系说明 |
|-------|------|-------|----------|
| **页面 P** | **包含** | StaticHTML ∪ Hydrate(Islands) | 集合划分：静态内容与交互组件互不相交 |
| **Island** | **依赖** | Hydration 策略 | strategy ∈ {load, visible, idle, media, client:only} |
| **零 JS 默认** | **对立** | SPA 全量 JS | SPA: JS_bundle = Framework + AppLogic + Components |
| **Hydration** | **包含** | 注水触发条件 + 状态恢复 | DOMContentLoaded / IntersectionObserver / requestIdleCallback |
| **Islands** | **对立** | SSR 整页注水 | SSR: O(|PageTree|) 注水；Islands: O(|Islands|) 注水 |
| **框架运行时** | **对立** | 零 JS 静态内容 | 静态 HTML 不携带任何框架运行时代码 |
| **延迟成本模型** | **映射** | 策略函数 delay(strategy) | L_total = L_html + L_css + Σ size(i.bundle) × delay(i.strategy) |
| **Island 间通信** | **依赖** | 事件总线 / Nano Stores | 跨 Island 直接引用被禁止，保持边界隔离 |
| **Islands** | **映射** | DDD  bounded context | 每个 Island 对应独立的业务能力边界 |
| **Astro** | **包含** | Islands + 框架共享机制 | 群岛间框架共享缓解运行时重复加载 |

---

## 八、形式化推理链

```text
公理 A4 (边界隔离): Server ∩ Client = ∅ (计算资源层面)
        ↓
引理 L1 (静态内容无运行时): ¬interactive(c) ⟹ JS(c) = ∅
        ↓
引理 L2 (选择性注水单调性): 若 Islands ⊆ Islands'，则
                            HydrationCost(Islands) ≤ HydrationCost(Islands')
        ↓
定理 T8 (Islands 最小 JS 定理): 在给定交互需求集合 I 下，Islands 架构的
                                 JS 传输体积达到理论下界 Σ_{i∈I} size(i.bundle)
        ↓
推论 C1 (零 JS 极限): 当交互密度 ρ → 0 时，Islands 的 JS 体积趋近 0，
                      退化为纯静态站点
```

```text
公理 A3 (变更最小化): Δs → min(|ΔDOM|)
        ↓
引理 L3 (组件级注水精确性): 仅交互组件激活生命周期，静态 DOM 不参与 hydration
        ↓
引理 L4 (策略偏序最优性): urgency(load) > urgency(visible) > urgency(idle)，
                          高优先级策略最小化用户可感知延迟
        ↓
定理 T9 (Islands 首屏最优性): L_total = L_cdn + Σ(L_island × p_activate) 在
                               内容驱动场景下优于 SSR 与 SPA 的加载模型
        ↓
推论 C2 (适用域边界): 当交互密度 ρ → 1 时，几乎所有组件均为 Island，
                      Islands 退化为「复杂构建步骤的 SPA」
```

---

## 九、推理判定树：何时使用 Islands vs SSR vs SPA？

```text
                    [开始: 渲染架构选型]
                          │
                          ▼
                ┌─────────────────┐
                │ Q1: 内容/应用比?│
                │ 内容 / 混合 / 应用│
                └────────┬────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
      [内容]           [混合]            [应用]
        │                │                │
        ▼                ▼                ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ Q2: SEO 需求? │ │ Q2: 动态数据? │ │ Q2: 状态复杂? │
│ 强 / 弱       │ │ 多 / 少       │ │ 是 / 否       │
└───────┬───────┘ └───────┬───────┘ └───────┬───────┘
        │                 │                 │
   ┌────┴────┐       ┌────┴────┐       ┌────┴────┐
   ▼         ▼       ▼         ▼       ▼         ▼
  [强]      [弱]    [多]      [少]    [是]      [否]
   │         │       │         │       │         │
   ▼         ▼       ▼         ▼       ▼         ▼
 Islands   Islands   RSC      Islands   SPA      Islands
 (Astro)   +CDN    (Next.js)  +API    (React)   +Vue
 最优      静态      流式      混合     状态驱动   轻交互
```

---

## 十、国际课程对齐标注

| 课程代码 | 课程名称 | 对齐章节 | 映射内容 |
|----------|----------|----------|----------|
| **Stanford CS 142** | Web Applications | Lecture: Responsive Web Design (Week 4) | 渐进增强哲学：HTML 为文档、CSS 为表现、JS 为行为增强；Islands 是这一哲学的当代极致表达 |
| **CMU 15-213** | Computer Systems | Lecture: Cache Performance & Memory Hierarchy | 首屏加载 L_total 的优化对应缓存策略与预取技术；零 JS 默认对应「最小工作集」原则 |
| **MIT 6.170** | Software Studio | Lab: Progressive Enhancement & Performance | 选择性注水的用户体验权衡；Islands 架构的内容-行为正交分离 |

> **学术溯源**: Islands 架构的组件隔离思想可追溯至 **Douglas McIlroy** (NATO 软件工程会议, 1968) 提出的「软件组件工业」愿景——软件应由现成零件组装而成。Jason Miller (2020) 的「Islands Architecture」论文将这一思想转化为前端渲染的正式模式，而 Fred K. Schott (Astro 作者) 的「Ship less JavaScript」则是其工程 slogan。

---

## 十一、深度批判性形式化总结（增强版）

Islands 架构是前端渲染理论中「渐进增强」哲学的当代极致表达，其形式化核心在于将页面 P 划分为两个互不相交的子集：StaticHTML（无运行时依赖的纯标记）与 Hydrate(Islands)（需客户端激活的交互组件）。这种划分在集合论语义上实现了「内容」与「行为」的正交分离，从而在最弱假设下满足了 A3（最小变更公理）的局部版本——仅交互组件承担状态变更与 DOM 更新的成本。Jason Miller (2020) 将 Islands 定义为「server-rendering of pages with small, isolated 'islands' of interactivity」，这一定义的形式化内涵在于：Islands 将 hydration 的粒度从「应用级」或「页面级」压缩到「组件级」，使 hydration 成本从 O(|ComponentTree|) 或 O(|PageTree|) 降至 O(|Islands|)。

然而，Islands 架构面临的挑战同样深刻，且大多源于其形式化模型的边界假设。首先是**框架运行时的重复加载问题**：当多个 Islands 使用不同框架（如一个 React Island、一个 Vue Island、一个 Svelte Island）时，用户需下载多份框架运行时，这可能抵消甚至逆转「零 JS 默认」带来的体积优势。设 FrameworkRuntime_i 为第 i 个 Island 的框架体积，则总运行时开销为 Σ FrameworkRuntime_i，在异构框架场景下这一求和可能远超单一 SPA 的 FrameworkRuntime。Astro 的「群岛间框架共享」机制虽然缓解了这一问题，却引入了构建配置的复杂性，使得 Islands 的「零配置」理想让位于「精细调优」的现实。

其次是**状态共享的边界困境**：Islands 之间的通信被设计为松耦合（事件总线或 Nano Stores），但在实际工程中，「购物车状态跨越三个 Island」的场景要求开发者手动管理跨边界状态同步，这在某种程度上复刻了微前端的状态碎片化难题。从范畴论语义审视，Islands 的静态 HTML 与动态 Island 之间缺乏自然的态射定义——StaticHTML 无法直接「提升」为 Island 的输入，而 Island 的输出也无法「沉降」为静态内容，这种范畴间断裂迫使开发者依赖外部通信机制来弥补。

更深层的理论批判指向 Islands 的**适用域边界**。该架构对「内容驱动」站点（博客、文档、营销页）是近乎完美的匹配，但对于「应用驱动」场景（SaaS 后台、实时协作工具、数据可视化仪表盘），交互密度之高使得几乎所有组件都成为 Island，此时 Islands 退化为「带有复杂构建步骤的 SPA」。Ryan Dahl (Deno / Fresh) 承认 Fresh 的「无构建步骤」设计在应用级场景中仍需权衡。2026 年的技术共识是：Islands 不是 SPA 的替代者，而是前端架构光谱上的一个重要节点——它与 SSR、RSC、SPA 共同构成了「按交互密度选择渲染策略」的连续体，而非非此即彼的排他选项。未来研究应聚焦于：Islands 间框架运行时的形式化共享协议、跨 Island 状态同步的一致性模型，以及 Islands 与 RSC 的融合架构（如 Server Islands）。
