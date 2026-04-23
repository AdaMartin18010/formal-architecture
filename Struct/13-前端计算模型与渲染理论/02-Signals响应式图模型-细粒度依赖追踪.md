# Signals 响应式图模型：细粒度依赖追踪

> **来源映射**: View/03.md §1.1, View/04.md §6.1, View/05.md §1.1
> **国际权威参考**: SolidJS Documentation; Angular Signals RFC (2023); Vue Reactivity System Docs; C.A.R. Hoare "Communicating Sequential Processes" (1985); Ullman "Principles of Database and Knowledge-Base Systems" (1988), Ch. 3 (依赖图与拓扑排序)

---

## 一、知识体系思维导图

```text
Signals 响应式图模型
│
├─► 原子层 (Atomic Layer)
│   ├─ Signal<T>: 持有值 + 观察者集合的可变单元
│   ├─ Computed<T>: 惰性求值缓存 (Memoization)
│   └─ Effect: 副作用订阅者，在依赖变更时执行
│
├─► 图结构层 (Graph Layer)
│   ├─ 依赖图 G = (V, E)
│   │   V = {signals} ∪ {computed} ∪ {effects}
│   │   E = {(source, target) | target 计算时读取 source}
│   ├─ 性质: DAG (无环有向图) — 环检测必需
│   ├─ 传播方向: 源变更 → 下游标记 dirty → 批量执行
│   └─ 拓扑序: 确保 effect 按依赖深度倒序执行
│
├─► 调度层 (Scheduling Layer)
│   ├─ 同步传播 (Vue 3, MobX): 立即更新
│   ├─ 微任务批处理 (SolidJS): queueMicrotask 批量 effect
│   └─ 事务封装: batch()/untrack() 控制触发粒度
│
└─► 形式化优势
    ├─ A3 满足度: ✅ O(1) 靶向更新
    ├─ 内存模型: O(\|graph\|) 与组件实例解耦
    └─ 定理: Signals 图是 VDOM 树范畴的真子范畴超集
```

---

## 二、核心概念的形式化定义

### 2.1 Signal 代数结构

```text
定义 (Signal 代数):
  Signal<T> = ⟨value: T, observers: Set<Subscriber>, version: ℕ⟩
    read(): T       → 返回 value，并注册当前上下文到 observers
    write(v: T): void → 若 v ≠ value，更新 value++version，通知 observers

定义 (Computed / Memo):
  Computed<T> = ⟨fn: ()→T, cache: T\|∅, dirty: bool⟩
    惰性求值: 首次读取或 dirty=true 时执行 fn，缓存结果
    依赖追踪: fn 执行期间自动建立 Signal → Computed 边

定义 (Effect):
  Effect = ⟨fn: ()→void, deps: Set<Signal|Computed>⟩
    执行时机: 初始化一次 + 依赖变更后调度
    清理机制: 每次执行前调用前次返回的 cleanup 函数
```

### 2.2 依赖图的 DAG 拓扑性质

```text
定义 (响应式图): G = (V, E)
  V = S ∪ C ∪ X  (Signals ∪ Computeds ∪ Effects)
  E ⊆ (S × C) ∪ (S × X) ∪ (C × C) ∪ (C × X)  (依赖边)

约束 (无环性): G 必须是无环有向图 (DAG)
  若存在环 → 递归依赖导致无限循环或死锁
  检测: 深度优先搜索 (DFS) 回溯标记，或拓扑排序 Kahn 算法

传播算法 (Topological Push-Pull):
  Push 阶段 (源变更):
    1. 源 Signal s 的 version++
    2. 遍历 s.observers，标记下游 Computed 为 dirty
    3. Effect 加入待执行队列 (去重)

  Pull 阶段 (读取求值):
    1. 读取 Computed c 时，若 c.dirty=true，递归拉取上游最新值
    2. 重新执行 c.fn，建立/更新 E 中的边 (动态依赖追踪)

调度 (Batching):
    将所有 pending effects 收集到微任务队列
    同一微任务内多次 state 变更仅触发一次 effect 执行
```

### 2.3 Signals vs Hooks 的语义鸿沟

```text
Hooks (React) 语义:
  Component: State × ℕ⁺ → VDOM   (时间/渲染次数为隐式参数)
  执行模型: 函数重执行 (Re-execution)
  闭包语义: 每次渲染创建新闭包，捕获旧状态需依赖数组
  时间维度: UI = f(state, t)  — 渲染具有时序性

Signals (Solid) 语义:
  Component: Setup → ReactiveGraph  (Setup 仅执行一次)
  执行模型: 图的增量更新 (Incremental Graph Update)
  闭包语义: Signal 为持久引用，不依赖闭包捕获
  时间维度: UI = graph(state)  — 图结构独立于时间

核心分歧:
  Hooks 认为 "渲染是函数的重新求值"
  Signals 认为 "渲染是持久图的增量传播"
  这是「计算作为函数 (λ演算)」vs「计算作为图 (数据流)」的范式之争
```

---

## 三、多维矩阵对比

| 维度 | React Hooks | SolidJS Signals | Angular Signals | Vue 3 Composition |
|------|-------------|-----------------|-----------------|-------------------|
| **执行模型** | 函数重执行 | 单执行 + 图更新 | 单执行 + zoneless | 单执行 + 代理追踪 |
| **依赖声明** | 依赖数组 (手动) | **自动追踪** | **自动追踪** | 自动追踪 (Proxy) |
| **闭包陷阱** | 存在 (stale closure) | **不存在** | **不存在** | 不存在 |
| **内存模型** | 双 VDOM 树快照 | **持久依赖图** | 持久依赖图 | 代理对象图 |
| **靶向更新** | O(n) diff | **O(1)** | **O(1)** | O(1) |
| **批处理策略** | 自动批处理 (18+) | 微任务队列 | 微任务队列 | 微任务队列 |
| **心智模型熵** | 高 | **低** | **低** | 低 |
| **生态成熟度** | ★★★★★ | ★★ | ★★★★ | ★★★★ |

---

## 四、权威引用

> **Ryan Carniato** (SolidJS 作者, 2023):
> "Adding any state management actually lowers the performance ceiling of your framework... The answer to Signals and better performance is found in fine-grained rendering."

> **Angular Team** (Signals RFC, 2023):
> "Signals provide a reactive primitive that is framework-agnostic and can serve as the foundation for Angular's change detection."

> **Evan You** (Vue 作者, 关于 Proxy-based Reactivity):
> "Vue's reactivity system is built on JavaScript Proxies, enabling automatic dependency tracking without explicit subscription APIs."

> **Michel Weststrate** (MobX 作者, 2015):
> "Anything that can be derived from the application state, should be derived. Automatically."

---

## 五、工程实践与代码示例

### 5.1 SolidJS Signals 的自动依赖追踪

```jsx
import { createSignal, createEffect, createMemo } from "solid-js";

// Signal: 原子状态单元
const [count, setCount] = createSignal(0);

// Computed: 自动追踪 count 的依赖
const double = createMemo(() => count() * 2);

// Effect: 自动订阅 count 和 double
// 注意: 若某次执行未读取 count()，则自动取消该依赖
createEffect(() => {
  console.log(`count=${count()}, double=${double()}`);
});

setCount(1); // 触发 effect，输出更新
```

### 5.2 动态依赖与条件分支

```jsx
const [showDetails, setShowDetails] = createSignal(false);
const [summary, setSummary] = createSignal("Loading...");
const [details, setDetails] = createSignal(null);

createEffect(() => {
  if (showDetails()) {
    // 仅在 showDetails() === true 时建立对 details 的依赖
    console.log(details());
  } else {
    // 此分支不读取 details → 取消 details 的订阅
    console.log(summary());
  }
});
```

> **工程洞察**: SolidJS 的依赖追踪是**动态**的——每次 effect 执行都会重新建立依赖集合，这与 Vue 3 的 Proxy 拦截和 Angular Signals 的显式 `computed()` 略有差异，但拓扑语义等价。

---

## 六、批判性总结

Signals 响应式图模型代表了前端计算语义从「时间维度（函数重执行）」向「结构维度（持久依赖图）」的深刻范式迁移。其形式化核心在于将 UI 更新建模为有向无环图上的增量传播问题，从而以 O(1) 靶向更新严格满足 A3（最小变更公理）。然而，这一模型并非没有代价。

首先，依赖图的 DAG 约束在工程实践中常被忽视——动态依赖追踪与条件分支的组合可能导致难以调试的「幽灵依赖」或「丢失依赖」问题。其次，Signals 的「单执行组件」模型要求开发者彻底抛弃「渲染 = 重新执行函数」的心智惯性，这对从 React 生态迁移的团队构成了显著的认知迁移成本。更深层的理论争议在于：Signals 的依赖图本质上是**命令式数据流**的隐式表达，其图结构在运行时动态演化，缺乏编译时的静态可预测性；这与 Svelte 编译时确定的依赖边形成对比。最后，Signals 的 O(1) 更新复杂度建立在「图规模与组件规模解耦」的前提上，但在超大规模应用中（如数万个 Signal 节点），图的内存占用与遍历开销仍不可忽视。尽管如此，Signals 在 2023-2026 年间已成为 Angular、Vue、Preact、Solid 等主流框架的共识方向，标志着前端响应式理论从「虚拟树比对」到「图传播」的历史性范式转移。
