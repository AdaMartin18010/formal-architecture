# 组件组合的幺半群：HOC 作为自同态

> **来源映射**: View/05.md §6.2
> **权威参考**: React Higher-Order Components 文档

---

## 一、幺半群结构

```text
定义: ⟨C, ∘, ε⟩
  C: 组件集合
  ∘: 组合操作 (嵌套/包裹)
  ε: 空组件/Fragment

结合律: (A ∘ B) ∘ C = A ∘ (B ∘ C)
单位元: A ∘ ε = ε ∘ A = A
❌ 交换律不成立: A ∘ B ≠ B ∘ A

∴ ⟨C, ∘, ε⟩ 是幺半群, 非阿贝尔群

HOC 是群上的自同态:
  HOC: C → C
  withTheme(A) = ThemeProvider ∘ A ∘ ThemeConsumer
  即: HOC 是组件群上的群同态
```

---

## 二、待完善内容

- [ ] HOC 的数学性质与 Hooks 的对比
- [ ] Render Props 作为范畴积的解释
