# Islands 架构：选择性注水与零 JS 默认

> **来源映射**: View/03.md §1.2, View/05.md §5.1
> **权威参考**: Astro 文档, Jason Miller "Islands Architecture"

---

## 一、核心概念定义

### 1.1 Islands 的形式化定义

```text
定义 (Islands Architecture):
  页面 = 静态 HTML 海洋 + 交互式 Islands (孤岛)

  形式化特征:
    静态 HTML ∈ DOM, JS ⊆ ∅ (默认)
    仅在交互组件 (Islands) 上执行选择性注水 (Selective Hydration)

  计算边界: 从"应用级"下放到"组件级"

  延迟公式: L_total = L_cdn + Σ(L_island × p_activate)
    其中 p_activate 为 Island 被激活的概率
```

### 1.2 Islands vs SPA 的形式化对比

| 维度 | Islands (Astro) | SPA (React/Vue) |
|------|----------------|----------------|
| 默认 JS 体积 | 0 (静态 HTML) | 完整应用 bundle |
| 首屏性能 | **优** (无 JS 阻塞) | 差 (JS 执行阻塞) |
| 交互一致性 | 中 (按需激活) | 优 (应用级统一) |
| SEO | **优** | 中 (需 SSR 辅助) |
| Hydration 成本 | 组件级 | 应用级 |

---

## 二、权威引用

> **Jason Miller** (Preact 作者, "Islands Architecture" 提出者):
> "The islands pattern encourages server-rendering of pages with small, isolated 'islands' of interactivity."

> **Fred K. Schott** (Astro 作者):
> "Ship less JavaScript, faster."

---

## 三、待完善内容

- [ ] Islands 的 hydration 策略 (idle, visible, media query)
- [ ] Astro 的 Islands 通信机制
- [ ] Islands 与微前端的边界辨析
