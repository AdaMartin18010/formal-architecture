# 结构类型与名义类型：TypeScript 的代数

> **来源映射**: View/04.md §6.5, View/05.md §2.1
> **国际权威参考**: Pierce "Types and Programming Languages" (TAPL, 2002) §15; TypeScript Handbook v5.5; Cardelli & Wegner (1985) "On Understanding Types, Data Abstraction, and Polymorphism"

---

## 一、知识体系思维导图

```text
结构类型与名义类型
│
├─► 类型等价性的两种公理化定义
│   ├─ 结构等价 (Structural): T₁ ≡ T₂ ⇔ shape(T₁) = shape(T₂)
│   ├─ 名义等价 (Nominal):   T₁ ≡ T₂ ⇔ name(T₁) = name(T₂)
│   └─ 鸭子类型 (Duck):      T₁ ≡ T₂ ⇔ behaviors(T₁) ⊇ behaviors(T₂)
│
├─► TypeScript 结构类型的代数结构
│   ├─ 积类型 (Product):     interface A { x: X; y: Y } ≡ X × Y
│   ├─ 和类型 (Sum):         type T = A | B ≡ A + B
│   ├─ 指数类型 (Exponential): (a: A) => B ≡ B^A
│   └─ 递归类型 (Recursive):  type Tree<T> = { val: T; children: Tree<T>[] }
│
├─► 名义类型的模拟技术
│   ├─ Branded Types:        type UserId = string & { readonly __brand: unique symbol }
│   ├─ Symbol 标记:            const tag = Symbol('NominalTag')
│   └─ Class + private field: class Email { #tag; constructor(readonly value: string) {} }
│
└─► 类型体操的代数边界
    ├─ 条件类型: T extends U ? X : Y
    ├─ 模板字面量: `prefix-${T}`
    └─ 不可判定性: TS 类型系统图灵完备，存在无限递归
```

---

## 二、核心概念的形式化定义

### 定义 D15.1：结构类型等价性

对于类型环境 Γ 下的两个类型 T₁ 和 T₂：

```
T₁ ≡ₛ T₂  ⇔  ∀f ∈ fields(T₁), ∃g ∈ fields(T₂) :
               name(f) = name(g) ∧ type(f) ≡ₛ type(g)
               ∧  vice versa (双向包含)
```

TypeScript 的 `interface` 和 `type` 均遵循此等价关系。

### 定义 D15.2：名义类型等价性

```
T₁ ≡ₙ T₂  ⇔  decl(T₁) = decl(T₂)
```

即类型等价性由其**声明站点**唯一标识决定，与成员形状无关。

### 定理 T15.1：结构类型系统存在语义安全漏洞

```text
前提: 设 type Email = string, type UserId = string

构造:
  shape(Email) = { length, toString, charAt, ... }
  shape(UserId) = { length, toString, charAt, ... }
  ∴ Email ≡ₛ UserId ≡ₛ string

但语义映射:
  sem(Email) = { s ∈ Σ* | s 匹配 RFC 5322 邮箱格式 }
  sem(UserId) = { s ∈ Σ* | s 是系统分配的唯一标识符 }
  sem(Email) ∩ sem(UserId) ≠ sem(Email)  (真子集关系)

推论:
  sendEmail("user_12345")  // 编译通过, 运行时语义错误
  getUser("not-an-email")  // 编译通过, 运行时语义错误

∴ 结构等价性不能保证语义安全性  ∎
```

### 定义 D15.3：Branded Type 的形式化

Branded Type 通过在交集类型中注入不可构造的 nominal 标记来模拟名义类型：

```
Brand<T, B> = T & { readonly __brand: B }

其中 B 是 unique symbol，使得:
  ∀b₁, b₂ ∈ Symbol, b₁ ≠ b₂ ⇒ Brand<T, b₁> ≢ₛ Brand<T, b₂>
```

---

## 三、多维矩阵对比

### 3.1 三种类型系统的形式化对比

| 维度 | 结构类型 (TS) | 名义类型 (Java/C#) | 鸭子类型 (Python/Ruby) |
|------|--------------|-------------------|----------------------|
| **等价判据** | 成员集合递归相等 | 声明名称相等 | 运行时行为子集 |
| **检查时机** | 编译时 | 编译时 | 运行时 |
| **错误发现** | 静态 (但语义泄漏) | 静态 (完全安全) | 动态 (运行时异常) |
| **子类型关系** | 宽度/深度子类型 | 显式继承/实现 | 隐式协议匹配 |
| **泛型变型** | 协变 (有缺陷) | 声明站点变型 | 无变型概念 |
| **模块边界** | 形状兼容即可 | 显式导入导出 | 无边界概念 |
| **重构安全性** | 低 (改名不破坏兼容) | 高 (改名即破坏) | 极低 |
| **表达力/安全权衡** | 灵活性优先 | 安全性优先 | 极简主义 |

### 3.2 TypeScript 名义类型模拟策略对比

| 策略 | 形式化表达 | 运行时开销 | 类型安全增强 | 工程适用性 |
|------|-----------|-----------|------------|-----------|
| **Branded Types** | `string & { __brand: unique symbol }` | 零 | ★★★★☆ | 高 |
| **Opaque Types** | `declare const __opaque__: unique symbol` | 零 | ★★★★☆ | 高 |
| **Class 封装** | `class Email { #tag; constructor(v: string) {} }` | 低 (对象包装) | ★★★★★ | 中 |
| **模板字面量约束** | `` `${string}@${string}` `` | 零 | ★★☆☆☆ | 低 |
| **Zod/io-ts 运行时** | `z.string().email()` | 中 | ★★★★★ | 极高 |

---

## 四、权威引用

> **Benjamin C. Pierce** (TAPL, 2002):
> "A type system is a tractable syntactic method for proving the absence of certain program behaviors by classifying phrases according to the kinds of values they compute." —— 结构类型正是通过"短语分类"而非"名称绑定"来实现这一点的。

> **Luca Cardelli & Peter Wegner** (1985):
> "On Understanding Types, Data Abstraction, and Polymorphism" —— 首次系统区分了 inclusion polymorphism（名义继承）与 parametric polymorphism（泛型），为结构子类型奠定了理论基础。

> **TypeScript Design Team** (2014):
> "TypeScript uses structural typing. This is because JavaScript is inherently structurally typed at runtime." —— 结构类型是 TS 对 JS 运行时语义的一种静态镜像。

> **Mark Seemann** ("Code That Fits in Your Head", 2021):
> "Primitive obsession is the tendency to use primitive types (like strings and integers) to represent domain concepts (like email addresses and user IDs)." —— 名义类型模拟（Branded Types）正是对抗这种"原始类型痴迷"的工程解药。

---

## 五、工程实践与代码示例

### 5.1 Branded Type 完整实现

```typescript
// 1. 声明唯一符号
declare const __EmailBrand: unique symbol;
declare const __UserIdBrand: unique symbol;

// 2. 定义 branded 类型
type Email = string & { readonly [__EmailBrand]: void };
type UserId = string & { readonly [__UserIdBrand]: void };

// 3. 构造器（运行时验证）
function createEmail(raw: string): Email {
  if (!raw.includes('@')) throw new Error('Invalid email');
  return raw as Email;
}

function createUserId(raw: string): UserId {
  return raw as UserId;
}

// 4. 使用：编译期阻止语义错误
function sendEmail(to: Email, subject: string): void { /* ... */ }

const uid = createUserId("user_123");
const em = createEmail("a@b.com");

sendEmail(em, "Hello");      // ✅ 编译通过
// sendEmail(uid, "Hello");  // ❌ 编译错误: UserId 不可赋值给 Email
```

### 5.2 类型级编程：结构类型的代数运算

```typescript
// 积类型（Product）
type Point = { x: number; y: number };  // number × number

// 和类型（Sum）
type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "rect"; w: number; h: number };

// 指数类型（Exponential）：函数即指数
type MapStringTo<T> = (s: string) => T;  // T^string

// 递归类型（Recursive）
type JSONValue =
  | string | number | boolean | null
  | JSONValue[]
  | { [key: string]: JSONValue };
```

---

## 六、批判性总结

TypeScript 选择结构类型并非设计缺陷，而是对 JavaScript 运行时本质的诚实映射：ECMAScript 规范中不存在"类名"或"类型标签"的概念，对象等价性完全由 `[[OwnProperty]]` 集合决定。结构类型是"鸭子类型"的静态化延伸，它降低了从 JS 到 TS 的迁移成本，但也引入了一个根本性的语义鸿沟——**形状等价 ≠ 语义等价**。

在大型前端系统中，这种鸿沟表现为：两个来自不同业务域的接口如果恰好拥有相同字段，就会被类型系统视为可互换，从而导致隐蔽的语义错误。工程界的缓解策略呈现光谱化分布：从纯编译时的 Branded Types（零运行时成本、中等安全增益），到运行时的 Zod/io-ts 验证（有运行时成本、完全安全），再到语言级别的 `class` 封装（对象分配开销、最高安全级别）。

值得注意的是，TypeScript 5.x 引入的 `const type parameters` 和更严格的泛型推断并未改变结构类型的根本哲学。社区对名义类型的呼声（如微软内部实验的 "Nominal Types" 提案）长期处于"讨论但未被采纳"的状态，核心障碍在于与 JS 互操作性的断裂风险。因此，2026 年的最佳实践仍然是**"编译时结构类型 + 运行时边界验证"的双重防线**：内部模块间依赖结构类型保证灵活性，IO 边界（API、localStorage、URL 参数）使用 Zod 进行运行时契约验证。这种"内松外紧"的策略，是对结构类型语义不完备性的一种务实工程回应。


---

## 七、概念属性关系网络

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    结构类型与名义类型：概念属性关系网络                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   类型等价性公理                                                              │
│   ├─ 结构等价 (Structural): T₁ ≡ₛ T₂ ⇔ shape(T₁) = shape(T₂)               │
│   │   ├─ 属性: 递归形状比较                                                   │
│   │   ├─ 属性: 宽度子类型 (width subtyping)                                  │
│   │   ├─ 属性: 深度子类型 (depth subtyping)                                  │
│   │   └─ 属性: 无声明站点标识                                                 │
│   │                                                                         │
│   ├─ 名义等价 (Nominal): T₁ ≡ₙ T₂ ⇔ decl(T₁) = decl(T₂)                    │
│   │   ├─ 属性: 声明名称唯一性                                                 │
│   │   ├─ 属性: 显式继承/实现关系                                              │
│   │   └─ 属性: 重构安全性高                                                   │
│   │                                                                         │
│   └─ 鸭子类型 (Duck): T₁ ≡ₐ T₂ ⇔ behaviors(T₁) ⊇ behaviors(T₂)             │
│       └─ 属性: 运行时协议匹配                                                 │
│                                                                             │
│   TypeScript 的代数结构                                                       │
│   ├─ 积类型 (Product): interface {x:X; y:Y} ≡ X × Y                         │
│   ├─ 和类型 (Sum): type T = A \| B ≡ A + B                                   │
│   ├─ 指数类型 (Exponential): (a:A) => B ≡ B^A                              │
│   └─ 递归类型 (Recursive): type Tree<T> = {val:T; children:Tree<T>[]}       │
│                                                                             │
│   名义类型模拟技术                                                            │
│   ├─ Branded Types: T & { readonly __brand: unique symbol }                │
│   │   ├─ 属性: 编译时区分                                                    │
│   │   ├─ 属性: 零运行时开销                                                  │
│   │   └─ 属性: 需显式构造器                                                  │
│   ├─ Opaque Types: declare const __opaque__: unique symbol                  │
│   │   └─ 属性: 模块级封装                                                    │
│   └─ Class + private field: class Email { #tag; ... }                       │
│       └─ 属性: 运行时对象包装，最高安全级别                                   │
│                                                                             │
│   与范畴论的关系                                                              │
│   积类型 ──────► 范畴积 (Product) ────► π₁, π₂ 投影态射                     │
│   和类型 ──────► 余积 (Coproduct) ────► in₁, in₂ 注入态射                    │
│   函数类型 ────► 指数对象 (Exponential) ──► eval 态射                        │
│   递归类型 ────► 初始 F-代数 (Initial F-algebra) ──► 最小不动点               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 八、形式化推理链

### 推理链 R15.1.1：结构类型存在语义安全漏洞

```
前提 P1 (结构等价公理):
  T₁ ≡ₛ T₂ ⇔ ∀f ∈ fields(T₁), ∃g ∈ fields(T₂):
    name(f) = name(g) ∧ type(f) ≡ₛ type(g) ∧ vice versa

前提 P2 (TypeScript 类型擦除):
  运行时 type(T) = ∅，即无类型信息保留

前提 P3 (语义映射独立性):
  sem: Type → P(DomainValue) 是独立于结构等价性的解释函数

构造反例:
  设 type Email = string, type UserId = string

  Step 1: shape(Email) = { length, toString, charAt, charCodeAt, ... }
          shape(UserId) = { length, toString, charAt, charCodeAt, ... }
          ∴ shape(Email) = shape(UserId)                         [集合相等]

  Step 2: 由 P1, Email ≡ₛ UserId ≡ₛ string                      [结构等价传递]

  Step 3: sem(Email) = { s ∈ Σ* | s 匹配 RFC 5322 邮箱格式 }
          sem(UserId) = { s ∈ Σ* | s 是系统分配的唯一标识符 }
          sem(Email) ∩ sem(UserId) = ∅ 或真子集关系              [由 P3]

  Step 4: 构造函数:
          sendEmail: Email → void
          getUser: UserId → User
          由于 Email ≡ₛ UserId ≡ₛ string，以下调用类型合法:
            sendEmail("user_12345")  // 编译通过
            getUser("not-an-email")  // 编译通过

  Step 5: 但 "user_12345" ∉ sem(Email)，"not-an-email" ∉ sem(UserId)
          ∴ 运行时发生语义类型错误

结论 C1: 结构等价性不能保证语义安全性
         ∵ shape(T₁) = shape(T₂) ↛ sem(T₁) = sem(T₂) ∎
```

### 推理链 R15.1.2：Branded Type 恢复名义区分

```
前提 P1: unique symbol 在 TypeScript 中保证全局唯一性
         ∀s₁, s₂: unique symbol. s₁ ≠ s₂

前提 P2: 交集类型 T & U 要求值同时满足 T 和 U 的结构

前提 P3: unique symbol 不可被值字面量构造

定义: Brand<T, B> = T & { readonly __brand: B }

推理步骤:
  Step 1: 设 declare const __EmailBrand: unique symbol
          declare const __UserIdBrand: unique symbol
          ∴ __EmailBrand ≠ __UserIdBrand                          [由 P1]

  Step 2: type Email = string & { readonly [__EmailBrand]: void }
          type UserId = string & { readonly [__UserIdBrand]: void }

  Step 3: fields(Email) = fields(string) ∪ { [__EmailBrand]: void }
          fields(UserId) = fields(string) ∪ { [__UserIdBrand]: void }
          ∵ __EmailBrand ≠ __UserIdBrand,
          ∴ fields(Email) ≠ fields(UserId)                        [集合不等]

  Step 4: 由结构等价公理 P1:
          fields(Email) ≠ fields(UserId) ⇒ Email ≢ₛ UserId

  Step 5: sendEmail("user_12345") 编译错误
          ∵ "user_12345": string 不可赋值给 Email
          (需要显式类型断言: "user_12345" as Email)

  Step 6: 类型断言点成为语义验证的"关口"(chokepoint)
          ∴ 运行时语义错误被推向编译期的显式断言

结论 C2: Brand<T, unique_symbol> 在结构类型系统中模拟名义类型区分 ∎
```

### 推理链 R15.1.3：TypeScript 类型系统的代数完备性

```
前提 P1: 笛卡尔闭范畴 (CCC) 要求: 积、余积、指数、终对象、始对象

前提 P2: TypeScript 类型系统支持:
         - 积: {a:A, b:B} 或 [A, B]
         - 和: A | B
         - 指数: (a:A) => B
         - 终: void / undefined
         - 始: never

推理步骤:
  Step 1: 设 𝓣𝓢 为 TypeScript 类型构成的范畴
          Obj(𝓣𝓢) = TypeScript 类型
          Hom(A, B) = (a: A) => B 的函数集合

  Step 2: 验证 CCC 公理:
          (a) 积: ∃ π₁: A×B → A, π₂: A×B → B
                对应解构: const {a, b}: {a:A, b:B}
          (b) 指数: ∃ eval: B^A × A → B
                 对应: (f: (a:A) => B, a: A) => f(a)
          (c) 终对象: ∃ ! : A → 1
                 对应: const unit = (): void => {}

  Step 3: 但 TS 允许 any: ∀T. any <: T ∧ T <: any
          这破坏了 CCC 的同构结构
          ∵ any 到 never 的映射既有 left inverse 又有非平凡 right inverse
          违反了同构的唯一性

  Step 4: 此外，tsconfig "strict" 关闭时:
          null/undefined 可赋值给任意类型
          相当于在初始对象 0 到任意 A 的态射之外，
          还存在额外的 "隐式强制转换"

结论 C3: TypeScript 在 strict 模式下近似 CCC，但 any 的存在使其严格来说
         不是笛卡尔闭范畴，而是"带孔的 CCC" (CCC with holes) ∎
```

---

## 九、推理判定树/决策树

### 决策树 DT15.1：类型系统选型与名义类型模拟策略

```text
                    ┌──────────────────────────────┐
                    │   需要区分同构语义类型?        │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
              ┌─────────┐                   ┌──────────┐
              │   是    │                   │    否    │
              └────┬────┘                   └────┬─────┘
                   │                             │
                   ▼                             ▼
       ┌───────────────────────┐        ┌──────────────┐
       │ 运行时验证是否可接受?  │        │ 使用原生 string│
       └───────────┬───────────┘        │ number 等类型 │
                   │                    └──────────────┘
        ┌──────────┼──────────┐
        ▼          ▼          ▼
   ┌─────────┐ ┌─────────┐ ┌──────────┐
   │ 零运行时 │ │ 可接受  │ │ 完全验证 │
   │ 开销    │ │ 低开销  │ │ 必须    │
   └────┬────┘ └────┬────┘ └─────┬────┘
        │           │            │
        ▼           ▼            ▼
   ┌─────────┐ ┌─────────┐ ┌──────────────┐
   │ Branded │ │ Opaque  │ │ Class +      │
   │ Types   │ │ Types   │ │ private field│
   │ (unique │ │ (declare│ │ (newtype     │
   │ symbol) │ │ const   │ │ wrapper)     │
   └─────────┘ └─────────┘ └──────────────┘
        │           │            │
        ▼           ▼            ▼
   ┌─────────┐ ┌─────────┐ ┌──────────────┐
   │ Zod/io- │ │ Zod/io- │ │ Zod Schema   │
   │ ts 边界 │ │ ts 边界 │ │ + class-     │
   │ 验证    │ │ 验证    │ │ validator    │
   └─────────┘ └─────────┘ └──────────────┘
```

### 决策规则集

| 节点 | 判定条件 | 是 → | 否 → |
|------|---------|------|------|
| N1 | 同结构不同语义? | N2 | 原生类型足够 |
| N2 | 零运行时开销? | Branded/Opaque | N3 |
| N3 | 运行时验证可接受? | Class 包装 | N4 |
| N4 | 需要编码/解码对称? | io-ts Codec | Zod Schema |

---

## 十、国际课程对齐标注

### 课程映射矩阵

| 本节内容 | Stanford CS 242 | CMU 15-312 | MIT 6.170 |
|---------|----------------|------------|-----------|
| 结构类型系统 | Week 3: Type Systems [TAPL Ch.11, 15] | Subtyping & Structural Types | Software Studio: TS Type Design |
| 名义类型系统 | Week 4: Objects & Classes [TAPL Ch.18-19] | Object-Oriented Type Theory | N/A |
| 类型代数 | Week 2-3: Algebraic Data Types | Type Constructors & Kinds | N/A |
| 子类型关系 | Week 4: Subtyping & Inheritance | Foundations: Subtyping Axioms | N/A |
| Branded Types 模拟 | Week 5: Advanced Types (研讨) | Phantom Types & Newtype | N/A |

### 权威来源引用索引

| 学者/来源 | 年份 | 核心观点 | 本文件引用 |
|-----------|------|---------|-----------|
| Benjamin C. Pierce | 2002 | "A type system is a tractable syntactic method for proving the absence of certain program behaviors..." (TAPL) | 结构类型定义 |
| Luca Cardelli & Peter Wegner | 1985 | 首次系统区分 inclusion polymorphism 与 parametric polymorphism | 子类型理论基础 |
| TypeScript Design Team | 2014 | "TypeScript uses structural typing because JavaScript is inherently structurally typed at runtime." | 设计决策溯源 |
| Mark Seemann | 2021 | Primitive obsession: using primitive types to represent domain concepts | Branded Types 工程动机 |
| Cardelli | 1988 | "A semantics of multiple inheritance" — 名义类型的形式化 | 名义等价性 |
| Compagnoni & Pierce | 1996 | "Higher-order intersection types" — 交集类型与子类型 | Branded Type 形式化 |

### 课程深度对齐

- **Stanford CS 242**: 本节的结构类型形式化直接对应 CS242 第3-4周内容。Pierce《TAPL》第15章的子类型关系 (Subtyping) 是核心阅读材料。CS242 的作业通常要求实现类型检查器，本节的形式化定义可作为实现参考。
- **CMU 15-312**: CMU 课程更深入地探讨了名义类型系统的元理论 (meta-theory)，包括 F-bounded polymorphism 和 nominal subtyping 的完备性证明。本节中的 Branded Types 模拟在 CMU 课程中被归类为 "newtype pattern" 或 "phantom types"。
- **MIT 6.170**: MIT 课程侧重工程实践，本节中的 Branded Types 工程实践和 Zod 运行时验证与 MIT 6.170 中关于类型安全边界处理的教学目标一致。
