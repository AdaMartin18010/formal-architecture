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


---

## 七、概念属性关系网络

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    线性类型与Effect依赖分析：概念属性网络                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   线性逻辑 (Girard 1987)                                                      │
│   ├─ 线性蕴含 A ⊸ B                                                          │
│   │   ├─ 属性: 消耗 A 恰好一次以产生 B                                        │
│   │   ├─ 属性: 上下文必须不相交 (dom(Γ₁) ∩ dom(Γ₂) = ∅)                      │
│   │   └─ 属性: 无弱化 (weakening) 和收缩 (contraction)                       │
│   │                                                                          │
│   ├─ 指数模态 !A (ofCourse)                                                  │
│   │   ├─ 属性: A 可被任意次复制和使用                                         │
│   │   ├─ 属性: 引入需要显式 "提升" (promotion)                                │
│   │   └─ 前端映射: useRef — 可无限读取的引用                                  │
│   │                                                                          │
│   ├─ 加法合取 (&) vs 乘法合取 (⊗)                                            │
│   │   ├─ A & B: 选择使用 A 或 B (如 if-else 分支)                            │
│   │   └─ A ⊗ B: 同时使用 A 和 B (如并行资源)                                 │
│   │                                                                          │
│   └─ 对偶性: 资源生产者 ⟷ 资源消费者                                          │
│       └─ 前端映射: Provider ⟷ Consumer 模式                                  │
│                                                                              │
│   Effect 系统 (Lucassen & Gifford 1988)                                       │
│   ├─ 效果签名 Σ                                                              │
│   │   ├─ 属性: 操作集合 {read, write, io, exc}                               │
│   │   ├─ 属性: 效果多态 ∀α.E.τ                                               │
│   │   └─ 属性: 效果子效果关系 ε₁ ≤ ε₂                                        │
│   │                                                                          │
│   └─ 前端映射                                                                 │
│       ├─ useEffect deps 数组 ≈ 效果集合显式声明                               │
│       ├─ useState ≈ 状态资源的一次性分配                                      │
│       └─ React Compiler ≈ 自动效果推断器                                      │
│                                                                              │
│   Monad 结构 (Moggi 1991)                                                     │
│   ├─ Reader<R, A>: R → A                                                     │
│   │   └─ 前端: React Context Provider, 环境读取                               │
│   ├─ Writer<W, A>: A × W                                                     │
│   │   └─ 前端: Redux Action Log, 日志累积                                     │
│   ├─ State<S, A>: S → (A, S)                                                 │
│   │   └─ 前端: useState, 状态转换                                             │
│   └─ IO<A>: World → (A, World)                                               │
│       └─ 前端: fetch, localStorage, DOM 操作                                  │
│                                                                              │
│   React Hooks 规则作为仿射类型系统                                             │
│   ├─ 规则 H1 (顺序线性): Hooks 必须按相同顺序每次调用                          │
│   ├─ 规则 H2 (依赖显式化): deps 数组 = 效果集合                               │
│   └─ 规则 H3 (条件禁用): Hooks 不可在条件分支中调用                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 八、形式化推理链

### 推理链 R15.3.1：React Hooks 作为仿射类型系统

```
前提 P1: 仿射类型系统规则:
         (a) 弱化禁止: 变量不可丢弃 (weakening 不成立)
         (b) 收缩允许: 变量可使用至多一次 (contraction 不成立)
         (c) 交换允许: 使用顺序可交换

前提 P2: React Hooks 规则 (官方文档):
         H1: Hooks 必须按相同顺序每次调用
         H2: useEffect deps 数组必须包含所有被读取的外部变量
         H3: Hooks 不可在 if/for/while 等条件分支中调用

前提 P3: 设 hook_sequence = [h₁, h₂, ..., hₙ] 为组件每次渲染时的 hooks 调用序列

推理步骤:
  Step 1: H1 (顺序线性) ⟷ 仿射类型的 "无弱化" + "固定顺序"
          在仿射类型中，每个资源必须被使用，不能丢弃
          在 React 中，每个 hook 声明 (useState, useEffect) 必须被调用，
          不能有条件地 "跳过"
          ∴ H1 对应仿射类型的弱化禁止

  Step 2: H3 (条件禁用) ⟷ 强化 "无弱化"
          如果 Hooks 允许在 if 分支中:
          if (condition) { useState(0) }
          则 condition = false 时，该 hook 被 "丢弃"
          这直接违反了仿射类型的 "每个资源必须被使用" 原则
          ∴ H3 是 H1 的推论，确保弱化不可能发生

  Step 3: H2 (依赖显式化) ⟷ 效果追踪
          设 useEffect body 读取变量集合 V = {v₁, v₂, ..., vₙ}
          deps 数组 D 必须满足: V ⊆ closure(D)
          其中 closure(D) 是 D 中变量的依赖闭包

          违反 H2 的例子:
          const [count, setCount] = useState(0);
          useEffect(() => { console.log(count) }, []);
          // V = {count}, D = ∅
          // count ∉ closure(∅)
          // ∴ 违反 H2

  Step 4: 从线性类型视角:
          count 是类型为 number 的"资源"
          useEffect body 是一次 "使用" 该资源的操作
          deps 数组是"资源使用注册表"
          未注册的使用 = 线性错误 (linear violation)

  Step 5: React Compiler 自动推断:
          构建数据流图 G = (Nodes, Edges)
          对每条 effect body → v 的边:
            若 v ∉ deps，自动插入 v 到 deps
          这等价于自动补全线性上下文的完整注册

结论 C1: React Hooks 规则 (H1-H3) 构成一个工程化、简化的仿射类型系统，
         其中 Hooks 调用序列对应线性资源声明序列，
         deps 数组对应效果/使用注册表 ∎
```

### 推理链 R15.3.2：Effect-TS 的代数效果类型系统

```
前提 P1: 代数效果 (Algebraic Effects) 由 Plotkin & Power (2001) 提出:
         效果操作符 Σ = { op₁: A₁ → B₁, op₂: A₂ → B₂, ... }
         效果处理程序 (handler): 解释每个 op 的具体行为

前提 P2: Effect-TS 类型签名:
         Effect.Effect<R, E, A> = 需求环境 R × 错误类型 E × 返回值 A

推理步骤:
  Step 1: 类型分解:
          R (Requirements): 该 effect 需要的外部能力/服务
          E (Errors): 该 effect 可能产生的错误类型
          A (Value): 成功时的返回值类型

  Step 2: 对应代数效果的 Σ:
          R 对应 Σ 中操作所需的能力上下文
          E 对应 Σ 中操作的异常出口
          A 对应 Σ 中操作的正常返回值

  Step 3: Effect 组合子的范畴语义:
          flatMap (bind): Effect<R, E, A> → (A → Effect<R, E, B>) → Effect<R, E, B>
          对应 Kleisli 组合: (A → T B) ∘ (B → T C) = A → T C
          其中 T = Effect<R, E, ->

  Step 4: 与 Monad 的关系:
          Effect-TS 的 Effect<R, E, A> 是一个带环境参数的 Monad
          即 ReaderT R (ExceptT E Identity) A
          在 Haskell 类型类中:
          type Effect r e a = ReaderT r (ExceptT e Identity) a

  Step 5: 前端工程价值:
          传统 Promise<A> 丢失了错误类型信息 (统一为 Error)
          Effect<R, E, A> 在类型层面保留了完整的错误语义
          ∴ 调用者必须显式处理或传播错误类型 E

结论 C2: Effect-TS 的 Effect<R, E, A> 是 Reader + Except 的 Monad Transformer
         组合，在类型层面实现了代数效果的完全追踪 ∎
```

### 推理链 R15.3.3：线性类型到 Rust Borrow Checker 的推理

```
前提 P1: 线性类型规则 (Girard 1987; Wadler 1990):
         Γ₁ ⊢ t: A ⊸ B    Γ₂ ⊢ u: A
         ───────────────────────────── (⊸-elim)
               Γ₁, Γ₂ ⊢ t u: B
         约束: dom(Γ₁) ∩ dom(Γ₂) = ∅

前提 P2: Rust 所有权规则:
         (a) 每个值有且只有一个所有者
         (b) 当所有者离开作用域，值被释放
         (c) 可变借用 (&mut T) 要求独占访问
         (d) 不可变借用 (&T) 允许多个并发读取

推理步骤:
  Step 1: Rust 所有权 ⟷ 线性类型的 "恰好一次使用"
          let x = String::from("hello");
          let y = x;  // x 的所有权移动到 y
          // x 此后不可使用 —— 线性消耗

  Step 2: Rust &mut T ⟷ 线性类型的 ⊸
          fn consume(s: String) -> usize { s.len() }
          // s: String 被线性消耗，调用后 s 不可用

  Step 3: Rust &T ⟷ 指数模态 !A
          let x = String::from("hello");
          let r1 = &x;
          let r2 = &x;
          // x 被 "提升" 为不可变引用，允许多次读取
          // 对应 !String —— 可无限复制的视图

  Step 4: React Compiler 的局限:
          React Compiler 只能追踪值的读取依赖，
          不能追踪所有权转移或生命周期
          ∴ React Compiler ≈ 仿射类型推断，而非完整的线性类型系统

  Step 5: 根本差异:
          Rust Borrow Checker: 编译期追踪内存所有权和生命周期
          React Compiler: 编译期追踪值读取和 memo 依赖
          前者保证内存安全，后者保证渲染一致性

结论 C3: Rust 的 Borrow Checker 是线性类型系统的完全实现，
         React Compiler 是其在前端渲染领域的弱化近似 (仿射类型推断) ∎
```

---

## 九、推理判定树/决策树

### 决策树 DT15.3：Effect 管理与类型系统选择

```text
              ┌─────────────────────────────────────┐
              │   应用是否需要追踪副作用类型?         │
              └───────────────┬─────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
        ┌───────────┐                   ┌───────────┐
        │    是     │                   │     否    │
        └─────┬─────┘                   └─────┬─────┘
              │                               │
              ▼                               ▼
    ┌─────────────────┐               ┌───────────────┐
    │ 副作用复杂度?    │               │ React Hooks    │
    │                 │               │ + ESLint规则   │
    └────────┬────────┘               │ 足够           │
             │                        └───────────────┘
    ┌────────┼────────┐
    ▼        ▼        ▼
 ┌──────┐ ┌──────┐ ┌──────────┐
 │ 简单  │ │ 中等  │ │ 复杂     │
 │ IO   │ │ 组合  │ │ 分布式  │
 └──┬───┘ └──┬───┘ └────┬─────┘
    │        │          │
    ▼        ▼          ▼
 ┌──────┐ ┌──────┐ ┌──────────┐
 │Effect│ │Effect│ │Effect-TS │
 │-TS   │ │-TS   │ │ +        │
 │单效  │ │多效  │ │ 自定义   │
 └──────┘ │组合  │ │ Algebra  │
          └──────┘ └──────────┘
```

### 判定规则集：Effect 管理策略选择

| 判定节点 | 条件 | 是 → | 否 → |
|---------|------|------|------|
| N1 | 需要编译期效果追踪? | N2 | React Hooks + ESLint |
| N2 | 单效果类型 (IO/Error)? | Effect-TS 简单模式 | N3 |
| N3 | 需要效果组合 (Reader + Writer + State)? | Effect-TS 完整模式 | N4 |
| N4 | 需要自定义代数效果? | Effect-TS 自定义 Algebra | 无原生方案 |

---

## 十、国际课程对齐标注

### 课程映射矩阵

| 本节内容 | Stanford CS 242 | CMU 15-312 | MIT 6.170 |
|---------|----------------|------------|-----------|
| 线性类型系统 | Week 7: Linear Types & Rust Ownership | Advanced Type Systems | N/A |
| Effect 系统 | Week 8: Session Types & Effects | Semantics of Effects | N/A |
| Monad 语义 | Week 5: Monads [Moggi 1991, Wadler] | Monad Theory & Applications | N/A |
| 代数效果 | 研讨: Plotkin & Power (2001) | Algebraic Effects (高级) | N/A |
| React Compiler 推断 | 项目实践 (未标准化) | N/A | Software Studio |

### 权威来源引用索引

| 学者 | 年份 | 贡献 | 本文件引用点 |
|------|------|------|-------------|
| Jean-Yves Girard | 1987 | Linear Logic | 线性逻辑理论基础 |
| Philip Wadler | 1990 | Linear Types can Change the World | 线性类型资源管理 |
| David Lucassen & David Gifford | 1988 | Polymorphic Effect Systems | 效果系统理论起源 |
| Eugenio Moggi | 1991 | Notions of Computation and Monads | 计算的单子范畴语义 |
| Gordon Plotkin & John Power | 2001 | Semantics for Algebraic Operations | 代数效果理论 |
| React Labs Team | 2024 | React Compiler Documentation | 自动依赖推断工程实践 |
| Daan Leijen | 2014+ | Koka: Programming with Row Polymorphic Effects | 行多态效果系统 |

### 课程深度对齐

- **Stanford CS 242**: 本节的线性类型内容对应 CS242 第7周关于 Linear Types 和 Rust Ownership 的讨论。Wadler (1990) 的 "Linear Types can Change the World" 是 CS242 的推荐阅读。CS242 近年由 Will Crichton 教授设计，强调从理论到系统的桥梁，本节将线性类型映射到 React Compiler 的做法与 CS242 的教学理念一致。
- **CMU 15-312**: CMU 课程深入探讨 Effect 系统的形式化语义，包括 FX 语言 (Lucassen & Gifford) 和 Koka (Leijen) 的行多态效果。本节中的 Effect-TS 映射与 CMU 课程中关于 effect polymorphism 和 row types 的内容对齐。
- **MIT 6.170**: MIT 课程不涉及线性类型或 Effect 系统的理论，但 React Hooks 的工程实践是 MIT 6.170 的常见项目主题。本节中的 Hooks 规则形式化可作为 MIT 学生的类型理论补充材料。
