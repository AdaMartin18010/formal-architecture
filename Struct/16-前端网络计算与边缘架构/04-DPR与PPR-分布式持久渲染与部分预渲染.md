# DPR 与 PPR：分布式持久渲染与部分预渲染

> **来源映射**: View/05.md §5.2
> **权威参考**: Vercel DPR, Next.js PPR

---

## 一、核心概念

```text
DPR (Distributed Persistent Rendering):
  S(t) = f(s(t₀), Δt), Δt = t - t₀
  若 Δt < TTL, 使用 Edge 缓存
  若 Δt ≥ TTL, 回源重新渲染 (Stale-while-revalidate)

PPR (Partial Prerendering):
  s = s_shell ⊕ s_dynamic
  壳立即返回, 动态部分流式填充
```

---

## 二、待完善内容

- [ ] DPR 的缓存失效策略形式化
- [ ] PPR 的 Suspense 边界设计
