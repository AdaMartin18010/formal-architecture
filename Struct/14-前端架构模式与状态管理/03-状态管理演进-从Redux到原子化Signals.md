# 状态管理演进：从 Redux 到原子化 Signals

> **来源映射**: View/03.md §4.2, View/04.md §4.2
> **权威参考**: Redux 文档, Jotai 文档, Zustand 文档

---

## 一、核心概念定义

### 1.1 状态管理的演进谱系

```text
2015: Flux / Redux (单一 Store, 显式 Action/Reducer)
  ↓
2017: Redux Toolkit (样板代码减少, immer 不可变)
  ↓
2019: Context API + useReducer (React 内置)
  ↓
2020: Zustand (原子化, 极简 API)
  ↓
2021: Jotai (原子化状态图, 依赖追踪)
  ↓
2023-2026: Signals (框架内置, 细粒度响应式)
```

### 1.2 2026 年状态管理分层

| 层级 | 2020 年模式 | 2026 年模式 | 权威实现 |
|-----|-----------|-----------|---------|
| **组件级** | `useState` | `useState` / Signal | React / Solid |
| **跨组件** | Redux / Context | Jotai / Zustand | 原子化状态 |
| **服务端** | REST + Client Fetch | Server Components + `use()` | React 19 |
| **表单级** | Formik / Redux-Form | `signalForm()` / Actions | Angular 20 / React 19 |

---

## 二、待完善内容

- [ ] Redux vs Zustand 的性能基准对比
- [ ] Jotai 的原子依赖图分析
- [ ] Server State 与 Client State 的分离策略
