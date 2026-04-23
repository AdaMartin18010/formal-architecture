# Curry-Howard-Lambek 三维对应

> **来源映射**: View/05.md §2.1, View/04.md §6.2
> **国际权威参考**: Howard (1969) "The formulae-as-types notion of construction"; Lambek & Scott (1986) "Introduction to Higher Order Categorical Logic"; Wadler (2015) "Propositions as Types" (Communications of the ACM)

---

## 一、知识体系思维导图

```text
Curry-Howard-Lambek 三维对应
│
├─► 第一维: Curry-Howard 同构 (逻辑 ⟷ 类型)
│   ├─ 命题 A ──► 类型 A
│   ├─ 证明 π ──► 程序 term(π)
│   ├─ 归约 (β) ──► 求值
│   └─ 矛盾 (⊥) ──► 空类型 (never / void)
│
├─► 第二维: Howard-Wadler 扩展 (类型 ⟷ 程序)
│   ├─ 积类型 A × B ──► 元组 [A, B]
│   ├─ 和类型 A + B ──► 联合 A | B
│   ├─ 函数类型 A → B ──► 箭头函数 (a: A) => B
│   └─ 递归类型 μX.F(X) ──► 递归接口/类型别名
│
├─► 第三维: Lambek 对应 (类型 ⟷ 范畴)
│   ├─ 类型 ──► 范畴中的对象
│   ├─ 函数 ──► 态射 (Morphism)
│   ├─ 复合 ──► 态射复合 (g ∘ f)
│   ├─ 恒等 ──► 恒等态射 (id)
│   └─ 多态 ──► 自然变换 (Natural Transformation)
│
└─► 前端映射层 (三维到工程)
    ├─ Props 组合 ──► 积类型 ──► 笛卡尔积
    ├─ 条件渲染 ──► 和类型 ──► 余积
    ├─ 回调传递 ──► 函数类型 ──► 指数对象
    └─ 泛型组件 ──► 多态类型 ──► 依赖积 (Π-type)
```

---

## 二、核心概念的形式化定义

### 定义 D15.4：Curry-Howard 同构

直觉主义命题逻辑的自然演绎系统 NJ 与简单类型 λ 演算 λ→ 之间存在同构：

```
┌─────────────────┬────────────────────┬────────────────────┐
│    逻辑 (NJ)    │    类型 (λ→)       │    前端概念        │
├─────────────────┼────────────────────┼────────────────────┤
│ 命题 A          │ 类型 A             │ TypeScript 类型    │
│ 证明 π: A       │ 项 t: A            │ 符合类型的程序     │
│ A ∧ B (合取)    │ A × B (积类型)     │ Props 多属性对象   │
│ A ∨ B (析取)    │ A + B (和类型)     │ 条件渲染/联合类型  │
│ A → B (蕴含)    │ A → B (函数类型)   │ 回调/处理器函数    │
│ ⊥ (假)          │ 空类型 (never)     │ 不可达代码/异常    │
│ ⊤ (真)          │ 单元类型 (void)    │ 无副作用操作       │
│ ∀x.A(x)         │ Πx:A.B(x) (依赖积) │ 泛型 <T>(x: T)=>B │
│ ∃x.A(x)         │ Σx:A.B(x) (依赖和) │ 存在类型/Branded   │
└─────────────────┴────────────────────┴────────────────────┘
```

### 定义 D15.5：Lambek 范畴语义

对于笛卡尔闭范畴 (CCC) 𝓒，类型 A 解释为对象 ⟦A⟧ ∈ Obj(𝓒)：

```
⟦A × B⟧ = ⟦A⟧ × ⟦B⟧          (范畴积)
⟦A + B⟧ = ⟦A⟧ + ⟦B⟧          (范畴余积)
⟦A → B⟧ = ⟦B⟧^⟦A⟧            (指数对象, 同态集)
⟦μX.F(X)⟧ = 初始 F-代数        (递归类型 = 最小不动点)
```

### 定理 T15.2：前端渲染范畴是笛卡尔闭范畴的近似

```text
前提: 设前端渲染范畴 𝓕，对象包括 State, VDOM, DOM, Effect

验证 CCC 公理:
  1. 终对象 (Terminal): 存在 !: A → 1，对应 React 的 `return null`
  2. 积 (Product): 存在投影 π₁: A×B → A, π₂: A×B → B，对应 Props 解构
  3. 指数 (Exponential): 存在 eval: B^A × A → B，对应函数调用 f(a)

反例 (非严格 CCC):
  React 的 useEffect 有副作用，破坏纯性
  ∴ 𝓕 是 "效应化 CCC" (Effectful CCC)，而非数学上的纯 CCC
```

### 定义 D15.6：模态逻辑的编程对应 (Wadler)

| 模态算子 | 逻辑意义 | 类型构造 | 前端实例 |
|---------|---------|---------|---------|
| ◇A (可能) | A 在可能世界中成立 | Monad T(A) | `Promise<A>`, 异步可能成功 |
| □A (必然) | A 在所有世界中成立 | Comonad W(A) | `() => A`, 纯函数必然可重入 |
| !A ( ofCourse ) | A 可无限复制 | 指数型 comonad | 可序列化 Props |
| ?A (whyNot) | A 可能缺失 | Option/Maybe | `A \| undefined` |

---

## 三、多维矩阵对比

### 3.1 三维对应的完整映射矩阵

| 逻辑命题 | 类型表达式 | 范畴对象 | TypeScript 语法 | 前端工程概念 |
|---------|-----------|---------|----------------|-------------|
| A ∧ B | A × B | 积对象 | `{a: A; b: B}` / `[A, B]` | 多属性 Props |
| A ∨ B | A + B | 余积对象 | `A \| B` | 条件渲染分支 |
| A → B | A → B | 指数对象 | `(a: A) => B` | 回调函数 |
| ⊥ | 0 | 初始对象 | `never` | 异常/错误边界 |
| ⊤ | 1 | 终对象 | `void` / `undefined` | 无返回值 |
| ¬A | A → 0 | 到初始对象的态射 | `(a: A) => never` | 类型守卫的否定分支 |
| A ↔ B | (A→B) × (B→A) | 同构对 | 双向类型转换函数 | 序列化/反序列化对 |
| ∀X.A(X) | ΠX.A(X) | 依赖积 | `<T>(x: T) => A<T>` | 泛型高阶组件 |
| ∃X.A(X) | ΣX.A(X) | 依赖和 | `{type: T; value: A<T>}` | 存在类型/动态分发 |

### 3.2 经典逻辑 vs 直觉主义逻辑 vs 前端类型系统

| 特性 | 经典逻辑 | 直觉主义逻辑 | TypeScript 类型系统 |
|------|---------|-------------|-------------------|
| 排中律 (A ∨ ¬A) | ✅ 成立 | ❌ 不成立 | ❌ 不可判定任意类型的 never |
| 双重否定消除 | ✅ 成立 | ❌ 不成立 | ❌ `((A => never) => never) ≠ A` |
| 构造性证明 | 可选 | 必须 | 必须 (类型即程序) |
|  Curry-Howard | 部分成立 | 完全成立 | 完全成立 (子集) |
| 对应计算模型 | 无 | λ 演算 | JavaScript 运行时 |
| 定理证明器 | 不适用 | Coq/Agda | TS 编译器 (tsc) |

---

## 四、权威引用

> **William Howard** (1969, "The formulae-as-types notion of construction"):
> 首次发表 Curry-Howard 对应，揭示了直觉主义自然演绎与简单类型 λ 演算之间的精确同构关系。

> **Philip Wadler** (2015, "Propositions as Types", *Communications of the ACM* 58(12):75-84):
> "Propositions as Types is a notion with many names and many origins. It is closely related to the BHK interpretation of intuitionistic logic... The notion of Propositions as Types describes a correspondence between a given logic and a given programming language." —— 这篇获 HOPL 认可的综述论文系统梳理了从 Curry (1934) 到现代依赖类型理论的完整谱系。

> **Joachim Lambek & Philip J. Scott** (1986, "Introduction to Higher Order Categorical Logic"):
> "Cartesian closed categories may be viewed as categorical models of the typed λ-calculus." —— 将 Curry-Howard 从逻辑-类型二维扩展到包含范畴论的三维对应。

> **Robert Harper** ("Practical Foundations for Programming Languages", 2nd ed., 2016):
> "Type theory is the theory of computability." —— 强调类型系统作为计算理论的统一框架。

---

## 五、工程实践与代码示例

### 5.1 条件渲染作为和类型的证明

```typescript
// 逻辑: A ∨ B ⇒ 渲染分支
type Result<T> =
  | { tag: "success"; value: T }   // 左分支: A
  | { tag: "error"; message: string }; // 右分支: B

// 证明/程序: 对和类型的 case analysis
function renderResult<T>(r: Result<T>): string {
  switch (r.tag) {
    case "success": return `Value: ${r.value}`;  // 左注入的消除
    case "error":   return `Error: ${r.message}`; // 右注入的消除
  }
}
// 对应范畴论: [A + B → C] ≅ [A → C] × [B → C]  (余积的泛性质)
```

### 5.2 Promise 作为可能性模态 (◇A)

```typescript
// 逻辑: ◇A 表示 "A 是可能成立的"
// 类型: Promise<A> 表示 "A 可能在未来得到"

// Monad 的 return (□I / 可能性引入)
const unit = <T>(x: T): Promise<T> => Promise.resolve(x);

// Monad 的 bind (◇-elimination)
const bind = <A, B>(
  ma: Promise<A>,
  f: (a: A) => Promise<B>
): Promise<B> => ma.then(f);

// 范畴论: T(A) = Promise<A> 是 Set 范畴上的单子
// η: Id ⇒ T  (unit)
// μ: T² ⇒ T  (join, 即 Promise<Promise<A>> → Promise<A>)
```

---

## 六、批判性总结

Curry-Howard-Lambek 三维对应是二十世纪理论计算机科学最深刻的结果之一，它将逻辑学、编程语言理论和范畴论这三个原本独立的领域统一在同一个形式框架之下。然而，当我们将这一对应映射到前端工程实践时，必须清醒地认识到**理论纯粹性与工程现实之间的张力**。

首先，TypeScript 类型系统虽然具备了积类型、和类型和函数类型，但它并非一个完整的直觉主义逻辑模型。TS 允许 `any` 类型的存在，这相当于在逻辑系统中引入了一条"公理"可以证明任何命题——即**爆炸原理 (ex falso quodlibet)** 的非受控版本，破坏了证明的相关性 (proof relevance)。其次，JavaScript 运行时的副作用模型（可变状态、I/O、异常抛出）使得前端范畴 𝓕 只是一个"近似 CCC"，而非数学上严格的笛卡尔闭范畴。`useEffect` 的依赖数组、React 的并发渲染调度、DOM 的底层突变操作，都使得态射复合不再满足结合律的严格形式。

更深层次的批判在于：Curry-Howard 对应承诺了"证明即程序"的美好图景，但在前端工程中，**类型正确性远不等于行为正确性**。一个类型正确的组件仍然可能渲染错误的 UI、产生可访问性缺陷、或引入性能退化。类型系统只能排除"一定错误"的程序，无法保证"一定正确"的程序。因此，三维对应应当被视为一种**设计直觉和架构隐喻**，而非严格的工程契约。2026 年的趋势显示，随着 Effect 类型系统（如 React Compiler 的自动依赖推断）和更严格的函数式编程模式在前端的渗透，这种对应正在从"理论趣味"走向"实用工具"，但其根本局限性——类型无法穷尽语义——将始终存在。
