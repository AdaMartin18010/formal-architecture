# Atomic Design：形态学分解的本体论

> **来源映射**: View/03.md §2.2, View/04.md §6.4
> **权威参考**: Brad Frost "Atomic Design" (2013)

---

## 一、核心概念定义

### 1.1 Atomic Design 的层次结构

```text
Atomic Design (Brad Frost):
  分解维度: 视觉形态 (Visual Morphology)

  Atoms ──► Molecules ──► Organisms ──► Templates ──► Pages
    │          │            │            │            │
    ▼          ▼            ▼            ▼            ▼
   按钮        搜索框        导航栏        页面布局      实例
   输入框      卡片头部       商品列表       模板填充

  本体论假设: UI 是物理世界的化学类比
  问题: 业务逻辑无处安放 → "智能组件" 反模式 (Container/Presentational 分裂)
```

### 1.2 形式化特征

| 层级 | 定义 | 属性 | 关系 | 示例 | 反例 |
|------|------|------|------|------|------|
| **Atom** | 不可再分的最小 UI 单元 | 无业务逻辑、纯样式 | 被 Molecule 组合 | Button, Input, Label | 包含状态的组件 |
| **Molecule** | 原子的功能组合 | 简单交互、无数据获取 | 组合 Atoms → 被 Organism 使用 | SearchBar, FormField | 直接调用 API |
| **Organism** | 独立的功能区块 | 可能包含状态 | 组合 Molecules | Header, ProductCard | 页面级路由逻辑 |
| **Template** | 页面布局骨架 | 无真实数据 | 占位符填充 | PageLayout | 硬编码内容 |
| **Page** | 真实内容填充的实例 | 完整业务上下文 | 模板 + 数据 | HomePage, ProductPage | 可复用组件 |

---

## 二、权威引用

> **Brad Frost** (Atomic Design 作者, 2013):
> "Atomic design is not a linear process, but rather a mental model to help us think of our user interfaces as both a cohesive whole and a collection of parts at the same time."

---

## 三、批判性分析

```text
Atomic Design vs FSD 的本体论分歧:

  Atomic Design: "UI 是物理世界的化学类比"
  FSD: "UI 是业务能力的投影"

  形式化差异:
    Atomic Design 是 "自底向上" 的组合 (Composition)
    FSD 是 "自顶向下" 的分解 (Decomposition)

  适用性定理:
    当项目规模 S < 5 人月, Atomic Design 足够
    当 S > 20 人月 或 团队 T > 3 个, FSD 必要
    ∵ 沟通成本 C ∝ T², FSD 通过边界显式化降低 C
```

---

## 四、待完善内容

- [ ] Atomic Design 在大型项目中的具体失效案例分析
- [ ] Container/Presentational 模式的历史演进与批判
