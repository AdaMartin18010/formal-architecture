# 前端数据流模式：从 MVVM 到 Flux

> **来源映射**: View/03.md §2.2, View/04.md §5.2, View/05.md §4-5
> **国际权威参考**: Trygve Reenskaug "The Model-View-Controller" (Xerox PARC, 1979); Facebook "Flux: An Application Architecture for React" (2014); Gamma et al. "Design Patterns" (Addison-Wesley, 1994), Observer Pattern; Meijer "Your Mouse is a Database" (2012, RxJS 理论基础)

---

## 一、知识体系思维导图

```text
前端数据流模式演进
│
├─► MVC (1979, Smalltalk)
│   ├─ Model ↔ View ↔ Controller (三角通信)
│   ├─ 问题: View 可直接修改 Model → 状态变更来源不可追溯
│   └─ 前端映射: Backbone.js (2010)
│
├─► MVVM (2005, Microsoft)
│   ├─ Model ↔ ViewModel ↔ View (双向绑定)
│   ├─ 问题: 级联更新难以追踪，调试困难
│   └─ 前端映射: Knockout.js, Vue 2, AngularJS
│
├─► Flux (2014, Facebook)
│   ├─ 单向数据流: Action → Dispatcher → Store → View
│   ├─ 核心约束: 状态变更必须经过 Dispatcher
│   └─ 前端映射: 早期 React 应用架构
│
├─► Redux (2015, Dan Abramov)
│   ├─ 单一不可变 Store + 纯函数 Reducer
│   ├─ 时间旅行调试: State(t+1) = reducer(State(t), Action)
│   └─ 问题: 样板代码 (Boilerplate) 冗长
│
└─► 现代演进 (2020+)
    ├─ Zustand: 极简原子化 Store
    ├─ Jotai: 原子依赖图 (Atom → Derived Atom)
    └─ Signals: 细粒度响应式图 (见模块 13)
```

---

## 二、核心概念的形式化定义

### 2.1 MVC / MVVM 的形式化

```text
定义 (MVC 三元组):
  设 State 为应用状态空间，View 为视图空间，Event 为事件空间
  Model:      State 的持有者，定义业务规则与数据变换
  View:       State → UI 的渲染函数
  Controller: Event → (Model × View) 的协调器

问题形式化:
  若 View 可直接调用 Model.setState(s')，则
  ∃e₁, e₂ ∈ Event: Model(t+1) = f(Model(t), e₁) = g(Model(t), e₂)
  当 f ≠ g 时，状态变更的因果链断裂，调试复杂度为 O(|Event|^|State|)

定义 (MVVM 双向绑定):
  ViewModel = ⟨state: State, commands: Event → void⟩
  绑定函数 bind: View ↔ ViewModel 为双向态射
    View → ViewModel: 用户输入事件 (onInput, onClick)
    ViewModel → View: 状态变更通知 (Observer 模式)

级联更新问题:
  设 ViewModel A 绑定 ViewModel B (computed property)
  A 变更 → B 自动更新 → 若 B 也反向影响 A → 循环依赖
  检测复杂度: 图环检测 O(V+E)，但调试语义极其隐晦
```

### 2.2 Flux 的单向数据流代数

```text
定义 (Flux 代数):
  Action     = ⟨type: string, payload: any⟩    (可序列化事件描述)
  Dispatcher = λ(action: Action) → void        (分发中心，无业务逻辑)
  Store      = ⟨state: State, reduce: Action → State⟩  (状态持有者)
  View       = State → VDOM                    (纯渲染)

数据流约束 (单向性公理):
  ∀s_{t+1} ∈ State, ∃!a ∈ Action : s_{t+1} = Store.reduce(s_t, a)
  即: 任何状态变更都有且仅有一个 Action 作为原因

形式化优势:
  状态历史可追溯: State_t = fold(reduce, initialState, [a₀, a₁, ..., a_t])
  时间旅行调试: 给定 Action 日志，可重放任意历史状态
  可预测性: 相同 Action 序列在相同初始状态下产生确定性的 State 序列
```

### 2.3 Redux 的 reducer 组合子

```text
定义 (Redux Store):
  Store = ⟨S, A, reducer: (S, A) → S, subscribers: Set<Listener⟩⟩
  reducer 必须满足:
    1. 纯函数性: ∀s, a, reducer(s, a) 无副作用、无外部依赖
    2. 引用透明: reducer(s, a) = reducer(s, a)  (确定性)
    3. 不可变性: 输出状态与输入状态不共享可变引用

组合子 combineReducers:
  设全局状态 S = S₁ × S₂ × ... × Sₙ (笛卡尔积)
  对每个子状态 Sᵢ，存在专用 reducerᵢ: (Sᵢ, A) → Sᵢ
  combineReducers(reducers) = λ(s, a) → ⟨reducer₁(s₁,a), ..., reducerₙ(sₙ,a)⟩
```

---

## 三、多维矩阵对比

| 维度 | MVC (Backbone) | MVVM (Vue 2) | Flux (原始) | Redux | Zustand (2026) |
|------|---------------|--------------|-------------|-------|----------------|
| **数据流向** | 双向/三角 | **双向绑定** | **单向** | **单向** | **单向** |
| **状态集中性** | 分散 | 分散 | 多 Store | **单一 Store** | 原子化分散 |
| **可预测性** | 低 | 低 | 中 | **高** | 高 |
| **样板代码** | 中 | 低 | 高 | **极高** | **极低** |
| **时间旅行调试** | ❌ | ❌ | ❌ | ✅ | ✅ (via middleware) |
| **学习曲线** | 低 | 低 | 中 | 高 | **极低** |
| **适用规模** | <5人 | <10人 | 5-20人 | **20+人** | 任意 |
| **2026年地位** | 历史遗产 | 过渡技术 | 历史遗产 | 企业存量 | **主流新选型** |

---

## 四、权威引用

> **Trygve Reenskaug** (MVC 发明者, Xerox PARC, 1979):
> "The essential purpose of MVC is to bridge the gap between the human user's mental model and the digital model that exists in the computer."

> **Facebook Engineering** (Flux 发布博客, 2014):
> "Flux is the application architecture that Facebook uses for building client-side web applications. It complements React's composable view components by utilizing a unidirectional data flow."

> **Dan Abramov** (Redux 作者, 2015):
> "The state of your whole application is stored in an object tree inside a single store. The only way to change the state tree is to emit an action."

> **Erik Meijer** (RxJS / ReactiveX 创始人):
> "Observables are the missing bridge between object-oriented and functional programming. They are the dual of enumerables."

---

## 五、工程实践与代码示例

### 5.1 Flux 单向数据流的严格实现

```js
// Dispatcher: 中央分发器 (单例)
const dispatcher = {
  _stores: [],
  register(store) { this._stores.push(store); },
  dispatch(action) {
    this._stores.forEach(store => store.reduce(action));
  }
};

// Store: 状态持有者 + Reducer
const TodoStore = {
  _state = { todos: [] },
  reduce(action) {
    switch(action.type) {
      case 'ADD':
        this._state.todos = [...this._state.todos, action.payload];
        this._emit();
        break;
    }
  }
};

// View: 纯渲染，通过回调触发 Action
function TodoList({ todos, onAdd }) {
  return <ul>{todos.map(t => <li>{t}</li>)}</ul>;
}
```

### 5.2 MVVM 双向绑定的「不可预测性」案例

```js
// Vue 2 双向绑定 (隐式依赖链)
export default {
  data() {
    return { firstName: 'John', lastName: 'Doe' };
  },
  computed: {
    // computed 依赖 firstName + lastName
    fullName() { return this.firstName + ' ' + this.lastName; }
  },
  watch: {
    // watch fullName → 反向修改 firstName
    fullName(newVal) {
      const parts = newVal.split(' ');
      this.firstName = parts[0]; // 触发 fullName 重新计算 → 循环?
    }
  }
};
```

> **工程教训**: 双向绑定将「数据依赖图」隐式埋入框架运行时，开发者难以在代码层面直观理解级联更新的触发路径，这是 MVVM 在大型应用中被 Flux/Redux 取代的核心原因。

---

## 六、批判性总结

从 MVVM 到 Flux 再到现代原子化状态管理的演进，本质上是前端数据流理论从「隐式依赖」走向「显式因果」的认知升级。MVVM 的双向绑定在小型应用中提供了极高的开发效率——开发者只需声明 View 与 ViewModel 的绑定关系，框架自动处理同步——但这种便利性的代价是**状态变更因果链的不可追溯性**。当应用规模扩大时，一个 Model 的微小变更可能通过多层 computed 与 watch 触发级联反应，调试复杂度呈指数级增长，这正是 Facebook 在 2014 年提出 Flux 的根本动机。

Flux 的核心贡献不在于其技术实现，而在于它确立了「单向数据流」作为前端架构的**不可约公理**：任何状态变更都必须通过显式的 Action 描述，经 Dispatcher 路由到 Store，最终反映到 View。这一约束将状态空间的历史演化从「隐式图遍历」转化为「显式折叠序列」，从而赋予了时间旅行调试与确定性重放的理论基础。Redux 将这一思想推向极致：单一不可变 Store 与纯函数 Reducer 的组合，使前端状态管理首次具备了函数式编程的引用透明性。

然而，Redux 的严格性也成为了其阿喀琉斯之踵。`combineReducers` 的笛卡尔积状态空间在大型应用中导致「样板代码爆炸」——每一个字段变更都需要穿越 Action → Reducer → Selector 的三重仪式。Zustand 与 Jotai 的崛起正是对这一痛点的回应：它们保留了单向数据流的可预测性，却将状态从「单一集中式 Store」解放为「分布式原子」，在理论上更接近化学中的「独立反应单元」模型。2026 年的共识已然清晰：**数据流的方向性（单向）比其拓扑结构（集中/分散）更为根本**——只要状态变更保持显式与可追踪，原子化分散同样是 Flux 精神的有效继承。
