# Signals 响应式图模型：细粒度依赖追踪

> **来源映射**: View/03.md §1.1, View/04.md §6.1, View/05.md §1.1
> **权威参考**: SolidJS 文档, Angular Signals RFC, Vue Reactivity 文档

---

## 一、核心概念定义

### 1.1 Signal 的形式化定义

```text
定义 (Signal): 信号是一个带有依赖追踪的可变单元
  Signal<T> = ⟨value: T, observers: Set<Effect>, read: ()→T, write: (T)→void⟩

依赖图: G = (V, E)
  V = {signals} ∪ {effects} ∪ {memos}
  E = {(source, target) | target 在计算时读取了 source}

传播算法: 当 signal s 的值变化时
  1. 标记 s 的所有直接 observer 为 "dirty"
  2. 递归标记下游 effect 为 "pending"
  3. 在微任务队列中批量执行 pending effects
```

### 1.2 Signals vs Hooks 的形式化对比

```text
Hooks (React):
  Component: State → VDOM
  执行次数: ℕ⁺ (正整数, 可多次重执行)
  副作用管理: useEffect 在每次渲染后调度
  闭包问题: 每次执行创建新闭包, 引用旧状态需依赖数组
  本质: UI = f(state, t)  (t 为时间/渲染次数)

Signals (Solid):
  Component: Setup → Reactive Graph
  执行次数: 1 (仅初始化执行一次)
  副作用管理: createEffect 订阅信号变化
  闭包问题: 无 (信号是持久引用, 不依赖闭包捕获)
  本质: UI = graph(state)  (graph 为持久依赖结构)

核心分歧:
  Hooks 认为 "渲染是重新执行函数"
  Signals 认为 "渲染是图的增量更新"
  这是"计算作为函数" vs "计算作为图" 的哲学分歧
```

---

## 二、思维表征

### 2.1 多维矩阵对比

| 维度 | Hooks (React) | Signals (Solid) | Signals (Angular) |
|------|--------------|----------------|-------------------|
| 执行模型 | 函数重执行 | 单执行 + 图更新 | 单执行 + zoneless |
| 依赖声明 | 依赖数组 (手动) | 自动追踪 | 自动追踪 |
| 闭包陷阱 | 存在 (stale closure) | 不存在 | 不存在 |
| 内存模型 | 双树快照 | 依赖图 | 依赖图 |
| 性能天花板 | O(n) diff | O(1) 靶向 | O(1) 靶向 |
| 心智模型熵 | 高 | 低 | 低 |

### 2.2 决策树：选择 Signals

```text
[根] 选择响应式模型
    │
    ▼
┌─────────────────────┐
│ 判定 D1: 是否要求     │
│ A3 最小变更严格满足?  │
│ (性能临界)            │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    ▼              ▼
 [是]            [否]
    │              │
    ▼              ▼
┌───────────┐  ┌───────────┐
│ 判定 D2:  │  │ 判定 D3:  │
│ 接受编译时 │  │ 生态兼容性 │
│ 魔法?      │  │ 优先?      │
└────┬──────┘  └────┬──────┘
     │              │
  ┌──┴──┐        ┌──┴──┐
  ▼     ▼        ▼     ▼
[是]   [否]    [是]   [否]
  │      │       │      │
  ▼      ▼       ▼      ▼
Svelte  Solid   React   React
Runes   Signals 19 +   19 +
        (F2)    Compiler Hooks
        (F1)    (F3)    (F4)
```

---

## 三、权威引用

> **Ryan Carniato** (SolidJS 作者):
> "Adding any state management actually lowers the performance ceiling of your framework... The answer to Signals and better performance is found in fine-grained rendering."

> **Angular Team** (Signals RFC, 2023):
> "Signals provide a reactive primitive that is framework-agnostic and can serve as the foundation for Angular's change detection."

---

## 四、待完善内容

- [ ] Signal 的图传播算法伪代码
- [ ] Effect 的调度与批处理机制
- [ ] Memo/Computed 的缓存策略
- [ ] Signals 在大型应用中的性能基准测试数据
