# Tree Shaking 形式化：可达性分析与副作用

> **来源映射**: View/05.md §8.2
> **权威参考**: Rollup 文档, ES Module Spec

---

## 一、核心概念

```text
可达集 R = {v ∈ V | ∃e ∈ E, e →* v}
死亡代码 D = V \ R

副作用分析:
  side: V → {0, 1}
  若 side(v) = 1, 则 v ∈ R (强制保留)

ESM vs CSM:
  ESM: 静态导入, AOT 优化
  CSM: 动态 require, 运行时近似
```

---

## 二、待完善内容

- [ ] Tree Shaking 的精确算法实现
- [ ] 副作用标记的自动化工具
