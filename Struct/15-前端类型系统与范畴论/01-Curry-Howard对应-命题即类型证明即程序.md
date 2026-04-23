# Curry-Howard 对应：命题即类型，证明即程序

> **来源映射**: View/05.md §2.1
> **权威参考**: Howard (1969), Lambek (1970s), Pierce "Types and Programming Languages"

---

## 一、核心概念定义

### 1.1 Curry-Howard-Lambek 三维对应

```text
Curry-Howard-Lambek 对应的三维扩展:

  逻辑命题 ──► 类型 ──► 范畴对象 ──► 前端概念
  证明     ──► 程序 ──► 态射     ──► 组件/函数
  切消     ──► 求值 ──► 态射相等 ──► 渲染/执行
```

### 1.2 详细对应表

| 逻辑命题 | TypeScript | 范畴对象 | 前端概念 |
|---------|-----------|---------|---------|
| A ∧ B | `[A, B]` 元组 | A × B 积 | Props 组合 |
| A ∨ B | `A \| B` 联合 | A + B 和 | 条件渲染 |
| A → B | `(a: A) => B` | B^A 指数 | 回调函数 |
| ¬A | `never` | 初始对象 0 | 错误边界 |
| ∀x.P(x) | `<T>(x: T)=>P` | 依赖积 Π | 泛型组件 |
| ∃x.P(x) | `{x: T & P}` | 依赖和 Σ | Branded Types |
| ◇A | `Promise<A>` | Monad T(A) | 异步操作 |
| □A | `() => A` | Comonad W(A) | 纯函数 |

---

## 二、权威引用

> **William Howard** (1969):
> "The formulae-as-types notion of construction."

> **Joachim Lambek** (1980):
> "From λ-calculus to Cartesian closed categories."

---

## 三、待完善内容

- [ ] 直觉主义逻辑与经典逻辑在前端类型系统中的差异
- [ ] Monad 在异步编程中的形式化 (Promise = Monad)
- [ ] Comonad 与 UI 状态管理的潜在关联
