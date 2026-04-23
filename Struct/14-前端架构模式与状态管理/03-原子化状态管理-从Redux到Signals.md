# 原子化状态管理：从 Redux 到 Signals

> **来源映射**: View/03.md §4.2, View/04.md §4.2, View/05.md §6-8
> **国际权威参考**: Redux Documentation; Jotai Documentation (Poimandres, 2020); Zustand Documentation; Lee Byron "Immutable User Interfaces" (2016); Hickey "The Value of Values" (2012, Rich Hickey, Clojure 设计哲学)

---

## 一、知识体系思维导图

```text
原子化状态管理演进谱系
│
├─► 2015: Redux (集中式原子)
│   ├─ 单一 Store = fold(reducer, initState, actions)
│   ├─ 不可变性: State(t+1) = f(State(t), Action)
│   ├─ 中间件生态: Redux-Thunk, Redux-Saga, RTK Query
│   └─ 代价: 样板代码、概念 ceremony
│
├─► 2019: Zustand (分布式原子 Store)
│   ├─ create(() => ({ count: 0, inc: () => ... }))
│   ├─ 无 Provider、无 Action/Reducer 仪式
│   ├─ 选择器订阅: useStore(s => s.count) → 靶向重渲染
│   └─ 本质: 微型不可变 Store 的集合
│
├─► 2020: Jotai (原子依赖图)
│   ├─ atom(0) → primitive atom
│   ├─ atom(get => get(count) * 2) → derived atom
│   ├─ 图结构: atoms 构成 DAG，变更沿依赖传播
│   └─ 本质: Recoil 理念的轻量实现
│
└─► 2023-2026: Signals (框架内置细粒度)
    ├─ 框架级集成: Angular Signals, Vue Reactivity, Preact Signals
    ├─ 编译时优化: Svelte 5 Runes ($state, $derived, $effect)
    └─ 本质: 原子状态 + 自动依赖追踪 + O(1) 靶向更新
```

---

## 二、核心概念的形式化定义

### 2.1 状态管理的「原子化」公理

```text
定义 (原子状态):
  Atom<T> = ⟨value: T, subscribers: Set<Observer>, set: (T→T) → void⟩
  原子性公理:
    1. 独立性: 每个 Atom 的状态变更不影响其他 Atom，除非通过显式依赖边
    2. 不可分性: Atom 是最小可订阅单元，不存在「部分订阅」
    3. 组合性: DerivedAtom = f(Atom₁, Atom₂, ...) 仍为 Atom

定义 (原子化状态空间):
  设 𝓐 为应用中所有 Atom 的集合
  全局状态 S = Π_{a∈𝓐} a.value  (所有原子值的笛卡尔积)
  但物理上不存储为单一对象，而是分布式原子网络
```

### 2.2 从 Redux 到 Zustand：仪式削减的形式化

```text
Redux 的状态变换仪式:
  开发者定义: ActionType + ActionCreator + Reducer + Selector
  状态变更路径: UI Event → dispatch(action) → reducer(s, a) → newState → re-render
  概念 overhead: 4 个概念实体对应 1 个状态字段

Zustand 的状态变换:
  开发者定义: create(set => ({ count: 0, inc: () => set(s => ({ count: s.count + 1 })) }))
  状态变更路径: UI Event → store.inc() → set() → subscribers 过滤 → 靶向重渲染
  概念 overhead: 1 个 create 调用对应完整状态逻辑

形式化对比:
  设状态字段数为 n
  Redux 的 ceremony 复杂度: O(4n) = O(n)
  Zustand 的 ceremony 复杂度: O(1) (单一 create)
  但 Redux 的全局可追溯性在 Zustand 中需额外 middleware 实现
```

### 2.3 Jotai 的原子依赖图

```text
定义 (Jotai 图模型):
  G = (V, E), V = PrimitiveAtoms ∪ DerivedAtoms
  E = {(src, dst) | dst 的求值函数读取了 src}

  PrimitiveAtom: writeable + readable，持有独立状态源
  DerivedAtom: readable-only，值由依赖的 Primitive/Derived Atoms 惰性求值

  写传播算法:
    1. 写入 PrimitiveAtom p → p.value 更新
    2. 标记所有直接下游 DerivedAtom 为 "stale"
    3. 惰性求值: 读取 DerivedAtom d 时，若 d.stale，递归求值上游
    4. 批量通知: 所有受影响的订阅者在微任务末尾统一重渲染

与 Redux 的本质差异:
  Redux: 全局状态 = 单一不可变树，任何变更需经根节点折叠
  Jotai: 全局状态 = 分布式原子图，变更沿 DAG 局部传播
```

---

## 三、多维矩阵对比

| 维度 | Redux + RTK | Zustand | Jotai | Signals (Solid/Angular) |
|------|------------|---------|-------|------------------------|
| **状态拓扑** | 单一集中树 | 分布式微型 Store | **原子依赖图** | **持久响应式图** |
| **订阅粒度** | 手动优化 (selector) | 选择器函数 | 原子级自动 | 信号级自动 |
| **重渲染范围** | 连接组件级 | 选择器靶向 | **原子靶向** | **O(1) 靶向** |
| **不可变性** | 强制 (immer/RTK) | 推荐 | 推荐 | 可变/不可变均可 |
| **时间旅行** | ✅ 原生 | ⚠️ 需 middleware | ⚠️ 需 devtools | ❌ (通常不支持) |
| **生态/工具链** | ★★★★★ | ★★★★ | ★★★ | ★★★★ |
| **概念 overhead** | **高** | **低** | 中 | 低 |
| **2026 新选型首选** | 存量维护 | **小型/中型** | **中型/大型** | **框架内置趋势** |

---

## 四、权威引用

> **Dan Abramov** (Redux 作者, 2015):
> "The state of your whole application is stored in an object tree inside a single store."

> **Daishi Kato** (Jotai 作者, 2020):
> "Jotai takes a bottom-up approach to global state management. Atoms are the core abstraction, and they can be composed into larger state structures."

> **Rich Hickey** (Clojure 作者, "The Value of Values", 2012):
> "Place-oriented programming is the source of much of our complexity. If we use immutable values, we get much simpler programs."

> **Lee Byron** (Immutable.js / GraphQL 作者, 2016):
> "Immutable data allows us to treat our application state as a value that flows through time, making it predictable and debuggable."

---

## 五、工程实践与代码示例

### 5.1 Zustand 的极简状态切片

```js
import { create } from 'zustand';

// 无需 Provider、无需 Reducer、无需 Action Types
const useCounterStore = create((set) => ({
  count: 0,
  inc: () => set((state) => ({ count: state.count + 1 })),
  dec: () => set((state) => ({ count: state.count - 1 })),
}));

// 组件仅订阅 count，inc/dec 引用稳定不触发重渲染
function Counter() {
  const count = useCounterStore((s) => s.count);
  const inc = useCounterStore((s) => s.inc);
  return <button onClick={inc}>{count}</button>;
}
```

### 5.2 Jotai 的原子组合与派生

```js
import { atom, useAtom } from 'jotai';

// 原始原子 (Primitive Atoms)
const countAtom = atom(0);
const multiplierAtom = atom(2);

// 派生原子 (Derived Atom) —— 自动追踪依赖
const multipliedCountAtom = atom(
  (get) => get(countAtom) * get(multiplierAtom)
);

// 写操作原子 (Write-only 逻辑封装)
const incrementCountAtom = atom(null, (get, set) => {
  set(countAtom, (prev) => prev + 1);
});

function Counter() {
  const [multiplied] = useAtom(multipliedCountAtom);
  const [, increment] = useAtom(incrementCountAtom);
  return <button onClick={increment}>{multiplied}</button>;
}
```

> **工程洞察**: Jotai 的原子图允许「状态逻辑」在文件/组件间自由组合，无需集中式 Store 的「提前规划」——这与函数式编程中「惰性求值」与「引用透明」的哲学高度一致。

---

## 六、批判性总结

原子化状态管理的演进谱系揭示了前端架构中一个深刻的「去中心化」趋势：从 Redux 的「单一真理源」到 Zustand 的「分布式微型 Store」，再到 Jotai 的「原子依赖图」，最终收敛于 Signals 的「运行时响应式网络」。这一趋势并非对 Redux 哲学——不可变性、可预测性、可追溯性——的否定，而是对其**工程实现方式**的优化与重构。

Redux 的历史功绩在于将「状态即折叠」的函数式思想引入前端主流，但其「单一 Store + Action/Reducer」的仪式结构在大型应用中产生了严重的「概念税」。每一个新增状态字段都需要穿越类型定义、ActionCreator、ReducerCase、Selector 的四重门，这种线性增长的 ceremony 与原子化状态的自然组合性形成了尖锐矛盾。Zustand 的破局之道在于将状态管理的「接口面积」压缩到极限——`create` 一个函数即定义完整的 Store——但其代价是牺牲了 Redux DevTools 原生提供的时间旅行与状态快照能力。

Jotai 代表了更理论化的尝试：它将状态管理重新建模为**图范畴上的组合问题**。Atom 作为最小可观测单元，其派生关系构成有向无环图，状态变更沿图的拓扑序传播。这一模型在数学上与电子电路的「节点电压分析」同构：原始 Atom 是独立电压源，Derived Atom 是依赖节点的电压，而组件则是「测量仪器」——仅在其连接的节点电压变化时重新读数。Signals 则将这一思想推向框架内核，彻底消除了「状态管理库」作为外部依赖的必要性。

批判性审视，原子化管理的潜在风险在于「图复杂性失控」。当数百个 Atom 构成复杂的派生网络时，开发者可能面临与 MVVM 时代相似的「隐式依赖黑洞」——变更的级联路径难以在代码层面直观追踪。2026 年的最佳实践倾向于「领域边界内的原子自由组合 + 领域边界间的显式契约」，这正是 FSD 架构方法论与原子化状态管理的天然交汇点。
