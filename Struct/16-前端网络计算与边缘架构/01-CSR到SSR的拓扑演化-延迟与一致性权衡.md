# CSR 到 SSR 的拓扑演化：延迟与一致性权衡

> **来源映射**: View/05.md §5.1
> **权威参考**: Next.js 文档, Vercel Edge Network 文档

---

## 一、五种渲染拓扑的形式化对比

| 拓扑 | 延迟公式 | 一致性 | 首屏性能 | 交互性能 |
|------|---------|--------|---------|---------|
| **CSR** | `L_cdn + L_js_exec + L_api × n` | 强 | 差 | 优 |
| **SSR** | `L_cdn + L_ssr + L_hydration` | 强 | 中 | 中 |
| **Islands** | `L_cdn + Σ(L_island × p_activate)` | 强 | **优** | 按需 |
| **RSC+Edge** | `L_edge + L_rsc_stream + L_cc` | 中 | 优 | 中 |
| **DPR** | `min(L_cache, L_revalidate)` | 可调 | **最优** | 按需 |

---

## 二、待完善内容

- [ ] 每种拓扑的详细网络时序图
- [ ] TTFB/FCP/LCP/TTI/CLS 在各拓扑中的表现数据
- [ ] 水合 (Hydration) 问题的形式化分析
