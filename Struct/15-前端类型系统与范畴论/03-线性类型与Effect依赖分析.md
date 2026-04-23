# 线性类型与 Effect 依赖分析

> **来源映射**: View/05.md §2.2, View/04.md §6.3
> **国际权威参考**: Wadler (1990) "Linear Types can Change the World"; Plotkin & Power (2001) "Semantics for Algebraic Operations"; React Compiler (React Labs, 2024); Lucassen & Gifford (1988) "Polymorphic Effect Systems"

---

## 一、知识体系思维导图

```text
线性类型与Effect依赖分析
│
├─► 线性逻辑 (Linear Logic) — Girard (1987)
│   ├─ 线性蕴含 A ⊸ B: 消耗 A 恰好一次以产生 B
│   ├─ 指数模态 !A: A 可无限复制 (收缩/弱化)
│   ├─ 加法合取 (&) vs 乘法合取 (⊗)
│   └─ 对偶性: 资源生产者 ⟷ 资源消费者
│
├─► Effect 系统的形式化
│   ├─ 效果签名 Σ: { read: State→Val, write: Val→State, io: Unit→Unit }
│   ├─ 效果多态: ∀α.E.τ (效果变量量化)
│   ├─ 效果子效果: ε₁ ≤ ε₂ (效果包含关系)
│   └─ 前端映射: useEffect deps ≈ 效果集合的显式声明
│
├─► React 中的线性类型隐喻
│   ├─ useState: 状态资源的一次性分配
│   ├─ useEffect: 副作用的线性使用上下文
│   ├─ useRef: !A (可无限读取的引用)
│   └─ React Compiler: 自动线性类型推断器
│
└─► Reader / Writer / State Monad
    ├─ Reader<R, A>: R → A (环境读取)
    ├─ Writer<W, A>: A × W (日志累积)
    └─ State<S, A>: S → (A, S) (状态转换)
```

---

## 二、核心概念的形式化定义

### 定义 D15.7：线性类型

在线性类型系统中，每个变量必须**恰好使用一次** (exactly once)。记线性函数类型为 A ⊸ B：

```
Γ₁ ⊢ t: A ⊸ B    Γ₂ ⊢ u: A
──────────────────────────── (⊸-elimination)
      Γ₁, Γ₂ ⊢ t u: B

约束: dom(Γ₁) ∩ dom(Γ₂) = ∅  (上下文必须不相交)
```

对比常规类型系统的函数类型 A → B，允许弱化 (weakening) 和收缩 (contraction)：

```
常规: λx.λy.x : A → B → A      (y 被弱化——未使用)
线性: λx.λy.x : A ⊸ B ⊸ A     ❌ 非法 (y 未使用违反线性性)
```

### 定义 D15.8：Effect 系统 (Lucassen & Gifford)

在 Effect 系统中，每个表达式的类型标注为 τ / ε，其中 ε 是该表达式可能产生的效果集合：

```
 typing rule for function application:

  Γ ⊢ f: (τ₁ → τ₂) / ε₁    Γ ⊢ x: τ₁ / ε₂
  ─────────────────────────────────────────
       Γ ⊢ f(x): τ₂ / (ε₁ ∪ ε₂ ∪ {call})
```

### 定义 D15.9：React Hooks 的 Effect 分析

React Hooks 规则可形式化为一个**简化的线性类型系统**：

```text
规则 H1 (顺序线性): Hooks 必须按相同顺序每次调用
  形式化: hook_sequence = [h₁, h₂, ..., hₙ], 顺序不可变

规则 H2 (依赖显式化): useEffect 的 deps 数组是效果集合的显式标注
  deps = { v₁, v₂, ... } ⇒ ε_effect = { read(v₁), read(v₂), ... }

规则 H3 (条件禁用): Hooks 不可在条件分支中调用
  形式化: ∀h ∈ hook_sequence, h 不在 if/while/for 的作用域内

违反 H2 的线性错误示例:
  const [count, setCount] = useState(0);
  useEffect(() => { console.log(count) }, []);
  // 线性错误: count 被读取但未在 deps 中声明
  // 对应: 资源 count 的使用未在效果集合中注册
```

### 定义 D15.10：Reader/Writer/State Monad

| Monad | 类型签名 | 计算语义 | 前端实例 |
|-------|---------|---------|---------|
| **Reader<R, A>** | `R → A` | 从环境 R 中读取并产生 A | React Context Provider |
| **Writer<W, A>** | `(A, W)` | 产生结果 A 并累积日志 W | Redux Action Log |
| **State<S, A>** | `S → (A, S)` | 接收状态 S，返回结果与新状态 | `useState` 的完整语义 |
| **IO<A>** | `World → (A, World)` | 与外部世界交互 | `fetch`, `localStorage` |

State Monad 的 bind 操作对应 React 状态更新链：

```
bind: State<S, A> → (A → State<S, B>) → State<S, B>

React 映射:
  const [s, setS] = useState(initial);
  // setS 是 S → (A, S) 的特例，其中 A = void
```

---

## 三、多维矩阵对比

### 3.1 线性类型 vs 仿射类型 vs 常规类型

| 特性 | 线性类型 (Linear) | 仿射类型 (Affine) | 常规类型 (Unrestricted) |
|------|------------------|------------------|------------------------|
| **使用次数** | 恰好一次 | 至多一次 | 任意次数 |
| **弱化 (Weakening)** | ❌ 禁止 | ❌ 禁止 | ✅ 允许 |
| **收缩 (Contraction)** | ❌ 禁止 | ✅ 允许 | ✅ 允许 |
| **交换 (Exchange)** | ✅ 允许 | ✅ 允许 | ✅ 允许 |
| **实现语言** | Rust (Borrow Checker) | ATS, Clean | TypeScript, Java |
| **前端映射** | React Compiler (部分) | useEffect cleanup | 默认行为 |
| **错误检测时机** | 编译时 | 编译时 | 无 |
| **适用场景** | 资源管理、内存安全 | 文件句柄、网络连接 | 通用计算 |

### 3.2 Effect 系统演进对比

| 系统 | 效果表示 | 推断方式 | 与类型系统集成 | 前端可用性 |
|------|---------|---------|--------------|-----------|
| **FX (Lucassen & Gifford)** | 效果集合 {read, write} | 显式标注 | 紧耦合 | 无 |
| **Java Checked Exceptions** | throws 子句 | 显式标注 | 部分集成 | 无 |
| **Koka (Leijen)** | 行多态效果 | 自动推断 | 原生集成 | 无 |
| **React Hooks** | deps 数组 | 手动 + ESLint | 运行时检查 | ✅ 成熟 |
| **React Compiler** | 依赖图 | 自动推断 | 编译时优化 | ✅ 2024+ |
| **Effect-TS** | 类型层效果追踪 | 显式 + 推断 | 原生集成 | ✅ 社区 |

---

## 四、权威引用

> **Jean-Yves Girard** (1987, "Linear Logic"):
> "Linear logic is a logic of actions and resources." —— 线性逻辑将逻辑命题从"真值"重新诠释为"资源"，为后续的类型系统研究开辟了新方向。

> **Philip Wadler** (1990, "Linear Types can Change the World"):
> "A linear type system ensures that every value is used exactly once. This can be used to manage resources such as files and memory." —— 线性类型在资源管理中的开创性应用。

> **David Lucassen & David Gifford** (1988, "Polymorphic Effect Systems"):
> 首次提出将副作用显式标注在类型签名中的效果系统，使得"纯函数"与" effectful 函数"在类型层面可区分。

> **React Labs Team** (2024, React Compiler 文档):
> "React Compiler automatically memoizes your code, inserting dependencies where they are missing and removing them where they are unnecessary." —— React Compiler 本质上是将手动 Effect 声明转化为自动线性/仿射类型推断的工程实践。

---

## 五、工程实践与代码示例

### 5.1 React Compiler 的自动依赖推断

```typescript
// 编译前: 开发者手动声明 (易出错)
function Counter() {
  const [count, setCount] = useState(0);
  const [step, setStep] = useState(1);

  useEffect(() => {
    console.log(count + step);
  }, [count]); // ❌ 遗漏 step，线性错误!
}

// 编译后 (React Compiler 自动 memo 化):
// Compiler 构建依赖图:
//   useEffect body → 读取 {count, step}
//   自动插入: [count, step]
// 等价于线性类型系统的自动效果推断
```

### 5.2 Effect-TS 风格的效果追踪

```typescript
// 使用 Effect-TS 显式追踪效果
import * as Effect from "@effect/io/Effect";
import * as Console from "@effect/console/Console";

// 类型签名显式标注效果:
// Effect.Effect<never, Error, string> = 需求环境 × 错误类型 × 返回值
const fetchUser = (id: string): Effect.Effect<never, Error, User> =>
  Effect.tryCatchPromise(
    () => fetch(`/api/user/${id}`).then(r => r.json()),
    () => new Error("Fetch failed")
  );

// 组合效果 (类似 Monad bind):
const program = Effect.gen(function* ($) {
  const user = yield* $(fetchUser("123"));   // 效果传递
  yield* $(Console.log(user.name));           // IO 效果
  return user;
});
```

### 5.3 State Monad 的简化实现

```typescript
// State<S, A> = (s: S) => [A, S]
type State<S, A> = (s: S) => [A, S];

const unit = <S, A>(a: A): State<S, A> => s => [a, s];

const bind = <S, A, B>(
  sa: State<S, A>,
  f: (a: A) => State<S, B>
): State<S, B> => s => {
  const [a, s1] = sa(s);
  return f(a)(s1);
};

// React useState 是 State Monad 的特例
// const [value, setValue] = useState(initial)
// setValue 对应于: (a: A) => State<S, void>
```

---

## 六、批判性总结

线性类型和 Effect 系统代表了类型理论从"描述数据形状"到"约束计算行为"的范式跃迁。在前端领域，React Hooks 的"规则"——不可在条件中调用、必须保持顺序、依赖数组必须完整——本质上是一个**工程化、简化的仿射类型系统**。React Compiler 的出现标志着这一系统从"手动声明"向"自动推断"的进化，但其底层逻辑仍然是线性的：每个状态资源、每个副作用，都必须在编译器的依赖图中被精确追踪。

然而，这种映射存在根本性的**表达力缺口**。真正的线性类型系统（如 Rust 的 Borrow Checker）能够追踪资源的生命周期和所有权转移，而 React Compiler 只能追踪值的读取依赖，无法阻止诸如"事件监听器未清理"或"竞态条件"等更复杂的资源管理错误。此外，JavaScript 的闭包捕获语义使得"使用一次"的静态分析极其困难——一个被闭包捕获的变量可能在任意 future tick 中被使用，这使得线性性检查在 JS 运行时模型中只能是**近似而非精确**的。

Effect-TS 等库尝试将代数效果 (Algebraic Effects) 引入前端，通过显式的 `Effect` 类型来追踪 IO、异常、并发等副作用。这在理论上比 React 的依赖数组更强大，但在实践中面临**学习曲线陡峭**和**与现有生态集成困难**的双重挑战。2026 年的务实结论是：对于绝大多数前端应用，React Compiler 的自动推断加上 ESLint 的规则检查已经足够；只有在高可靠性要求的金融或医疗前端系统中，才值得引入完整的 Effect 类型系统。线性类型的"资源即真理"哲学正在缓慢但确定地改变前端工程，但其完全采纳仍需等待 JavaScript 运行时语义的根本变革——或者 WebAssembly 的成熟。
