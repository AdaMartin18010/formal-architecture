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
