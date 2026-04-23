# Islands 架构：选择性注水与零 JS 默认

> **来源映射**: View/03.md §1.2, View/05.md §5.1
> **权威参考**: Astro 文档, Fresh 文档

---

## 一、核心概念

```text
Islands Architecture:
  延迟公式: L_total = L_cdn + Σ(L_island × p_activate)
  优势: 默认零 JS, 交互组件按需激活
  策略: idle / visible / media query 触发 hydration
```

---

## 二、待完善内容

- [ ] Islands 的 hydration 策略详细对比
- [ ] Astro 的 client:directives 语义分析
