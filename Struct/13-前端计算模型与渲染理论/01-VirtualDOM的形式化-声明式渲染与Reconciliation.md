# Virtual DOM 的形式化：声明式渲染与 Reconciliation

> **来源映射**: View/03.md §1.1, View/04.md §1, View/05.md §1.1
> **权威参考**: React 官方文档, "React: The Virtual DOM and Internals", Dan Abramov 博客

---

## 一、核心概念定义

### 1.1 Virtual DOM 的形式化定义

```text
定义 (Virtual DOM): 设 State 为应用状态空间，VDOM 为虚拟 DOM 树空间
  render: State → VDOM  (渲染函数，将状态映射为虚拟树)
  diff: VDOM × VDOM → Patch  (差异函数，求最小更新集)
  patch: Patch → DOM  (补丁函数，将差异应用到真实 DOM)

核心公理: UI = f(state)  →  f: State → UI 的声明
```

### 1.2 Reconciliation 的复杂度分析

| 操作 | 时间复杂度 | 空间复杂度 | 备注 |
|------|-----------|-----------|------|
| render | O(组件数) | O(VDOM 树节点数) | 生成完整虚拟树 |
| diff | O(n) | O(树深度) | n = 树节点数，启发式 O(n) |
| patch | O(更新节点数) | O(1) | 最小 DOM 操作集 |

> **React Diff 算法的启发式假设**:
>
> 1. 不同类型的元素产生不同的树 (根节点类型不同则整棵子树重建)
> 2. 通过 `key` 属性暗示哪些子元素可能保持稳定

---

## 二、形式化批判：Virtual DOM 的数学冗余

```text
定理 T1: Virtual DOM 不是满足 A3（最小变更公理）的必要条件

证明:
  前提: A3 要求 Δs → min(|ΔDOM|)
  假设: VDOM 是满足 A3 的必要条件
        ⇒ 不存在非 VDOM 系统能满足 A3

  构造反例:
    设系统 Ψ = Signals (SolidJS)
    对于状态变更 Δs, Signals 系统:
      1. 通过依赖图 G = (V, E), V = signals, E = dependencies
      2. 变更传播仅沿 E 的出边到达受影响的 DOM 节点
      3. 更新集 U = {dom | dom ∈ effect(s), s ∈ changed}
      4. |U| = O(1) (常数时间定位)

    而 VDOM 系统:
      1. 需重新执行组件函数生成新 VDOM 树
      2. 执行 Diff 算法求最小差异
      3. 复杂度 O(n), n = 树节点数
      4. 内存需维护两棵树 (双缓冲)

  ∵ Signals 直接满足 A3 且无需 VDOM
  ∴ 假设不成立
  ∴ VDOM 不是 A3 的必要条件    ∎
```

---

## 三、思维表征

### 3.1 决策树：何时选择 Virtual DOM

```text
[根] 选择渲染模型
    │
    ▼
┌─────────────────┐
│ 生态兼容性优先?  │
│ (需要 React 生态)│
└────────┬────────┘
         │
    ┌────┴────┐
    ▼          ▼
  [是]       [否]
    │          │
    ▼          ▼
 React 19   检查性能敏感度
 + Compiler    │
             ┌─┴─┐
             ▼   ▼
          [高]  [低]
           │     │
           ▼     ▼
        Signals 任意模型
        (Solid) 均可
```

### 3.2 概念定义-属性-关系-示例

| 概念 | 定义 | 关键属性 | 关系 | 示例 | 反例 |
|------|------|---------|------|------|------|
| **Virtual DOM** | 内存中的轻量 DOM 树表示 | 不可变、可对比、可批量更新 | render → diff → patch | React Element Tree | 直接 DOM 操作 |
| **Reconciliation** | 对比新旧 VDOM 求最小更新集 | O(n) 启发式、key 优化 | 输入: 两棵 VDOM 树; 输出: Patch 列表 | React Diff | 全量 DOM 重建 |
| **Double Buffering** | 内存中维护两棵 VDOM 树 | 当前树 + 工作树 | 交替使用减少渲染闪烁 | React 内部实现 | Signals 无此概念 |

---

## 四、权威引用

> **Pete Hunt** (React 早期核心开发者, 2013):
> "We built React to solve one problem: building large applications with data that changes over time."

> **Ryan Carniato** (SolidJS 作者):
> "Virtual DOM is pure overhead. It was a solution to a problem that no longer exists with fine-grained reactivity."

---

## 五、待完善内容

- [ ] VDOM 与真实 DOM 的详细 diff 算法步骤
- [ ] Fiber 架构的形式化分析 (时间切片、优先级调度)
- [ ] React 18+ Concurrent 特性的半可判定性分析
- [ ] VDOM 在服务器端渲染 (SSR) 中的角色
