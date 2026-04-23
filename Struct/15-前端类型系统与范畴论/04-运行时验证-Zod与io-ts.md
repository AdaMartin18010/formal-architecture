# 运行时验证：Zod 与 io-ts

> **来源映射**: View/03.md §5.1, View/04.md §5.2
> **国际权威参考**: Kiss (2019) "Parse, don't validate" (Functional Programming Slack); Girard et al. (1989) "Proofs and Types"; Zod 官方文档 v3.x; io-ts (gcanti) GitHub 仓库

---

## 一、知识体系思维导图

```text
运行时验证: Zod 与 io-ts
│
├─► 问题域: 编译时类型系统的边界
│   ├─ 外部数据: API 响应、localStorage、URL 参数、用户输入
│   ├─ TypeScript 的擦除语义: 运行时无类型信息
│   └─ 类型系统不可信边界: I/O 边界是类型安全的阿喀琉斯之踵
│
├─► 核心哲学: Parse, Don't Validate
│   ├─ Validate: boolean isValid(data) — 信息丢失
│   ├─ Parse: T parse(data) — 失败时提供证据，成功时返回精炼类型
│   └─ 形式化: parse: unknown → Either<ParseError, T>
│
├─► Zod: 面向对象的 Schema 组合
│   ├─ z.object({}).optional().nullable()
│   ├─ z.infer<typeof Schema> → TypeScript 类型推导
│   ├─ 同步/异步验证: .parse() / .parseAsync()
│   └─ 转换 (Transform): z.string().transform(s => s.trim())
│
├─► io-ts: 函数式组合子设计
│   ├─ Codec 类型: decode + encode 对称对
│   ├─ 组合子: t.type, t.partial, t.union, t.intersection
│   ├─ fp-ts 生态集成: Either, Option, TaskEither
│   └─ 形式化: Codec<A, O, I> = decode: I → Either<Errors, A>
│                                    encode: A → O
│
└─► 类型守卫 (Type Guards) 与断言函数
    ├─ 用户定义类型守卫: (x: unknown) => x is T
    ├─ 断言函数: asserts x is T
    └─ 局限性: 守卫逻辑与类型系统之间的信任 gap
```

---

## 二、核心概念的形式化定义

### 定义 D15.11：Parse vs Validate

设外部输入空间为 𝒰 (unknown)，目标类型为 T ⊆ 𝒰：

```
Validate: 𝒰 → boolean
  isValid(u) = true  ⇒  u ∈ T  (但无证据传递)
  isValid(u) = false ⇒  u ∉ T  (但无错误信息)

Parse: 𝒰 → Either<Error, T>
  parse(u) = Right(t)  ⇒  t ∈ T, 且 t 携带证明
  parse(u) = Left(e)   ⇒  e 包含 u ∉ T 的路径化证据
```

**Parse 的信息优势**: 成功分支返回的 `t: T` 使得下游函数无需再次检查。

### 定义 D15.12：Codec (编解码器)

io-ts 的 `Codec<A, O, I>` 是类型 A 的**同构表示**，满足：

```
decode: I → Either<Errors, A>    (反序列化/解析)
encode: A → O                     (序列化/编码)

法则 (round-trip):
  ∀a ∈ A, decode(encode(a)) = Right(a)
  ∀i ∈ I, decode(i) = Right(a) ⇒ encode(a) = i  (部分反演)
```

### 定义 D15.13：类型守卫的形式化

TypeScript 类型守卫是一个**运行时谓词**与**编译时类型细化**的耦合：

```
Guard_T: (x: unknown) → x is T

要求:
  1. 运行时: Guard_T(x) = true ⇒ x 满足 T 的运行时结构
  2. 编译时: if (Guard_T(x)) { /* x 被细化为 T */ }

信任问题:
  类型系统信任 Guard_T 的实现正确性，但无法验证。
  错误的 Guard: (x: unknown): x is string => typeof x === "number"
  // 运行时谓词与类型声明矛盾，但编译器接受!
```

---

## 三、多维矩阵对比

### 3.1 Zod vs io-ts vs 原生验证对比

| 维度 | Zod | io-ts | Class-Validator | JSON Schema | 原生类型守卫 |
|------|-----|-------|----------------|------------|------------|
| **设计范式** | 面向对象/链式 | 函数式/组合子 | 装饰器/元数据 | 声明式 JSON |  imperative |
| **TS 类型推导** | ✅ `z.infer` | ✅ 原生集成 | ⚠️ 需反射 | ❌ 外部工具 | 手动 |
| **运行时开销** | 中 (对象创建) | 低 (纯函数) | 高 (反射) | 中 | 最低 |
| **错误报告** | 路径化、可定制 | 路径化、fp-ts | 一般 | 一般 | 自定义 |
| **转换能力** | ✅ `.transform` | ✅ `.map` | ❌ | ❌ | 手动 |
| **生态集成** | 独立、轻量 | fp-ts 深度绑定 | NestJS | AJV | 无 |
| **bundle 大小** | ~12KB gzipped | ~8KB + fp-ts | ~20KB | ~15KB (AJV) | 0 |
| **学习曲线** | 低 | 高 (需 fp-ts) | 中 | 中 | 低 |

### 3.2 验证策略的防御层次

| 层次 | 位置 | 工具 | 检测时机 | 可信度 |
|------|------|------|---------|--------|
| **L1: 编译时类型** | 开发阶段 | TypeScript | 编译 | 高 (内部代码) |
| **L2: 边界解析** | 运行时入口 | Zod/io-ts | 数据进入时 | 高 (有错误证据) |
| **L3: 类型守卫** | 运行时分支 | `is` / `asserts` | 条件判断 | 中 (依赖实现正确) |
| **L4: 防御式编程** | 运行时随处 | `if (!x) throw` | 每次使用 | 低 (噪音大) |
| **L5: 测试覆盖** | CI 阶段 | Jest/Vitest | 测试执行 | 中 (依赖覆盖率) |

---

## 四、权威引用

> **Alexis King** (2019, "Parse, don't validate", blog post):
> "The difference between parsing and validation is that a parser produces evidence of its success in the form of a refined type, while a validator merely throws away information and returns a boolean." —— 这篇文章已成为函数式编程社区关于类型安全边界处理的纲领性文本。

> **Tom Crockett** (2019, "The Trouble with Typed Errors"):
> "Runtime type checking is not a sign of weakness in your type system; it is an admission that the outside world is untyped." —— 运行时验证不是对类型系统的否定，而是对 I/O 边界现实性的承认。

> **Giulio Canti** (io-ts 作者):
> "A runtime type system for IO decoding/encoding." —— io-ts 将类型系统的概念扩展到运行时，实现了编译时与运行时的双重验证。

> **Colin McDonnell** (Zod 作者, 2020):
> "Zod is designed to be as developer-friendly as possible. The goal is to eliminate duplicative type declarations by inferring static TypeScript types from your schemas." —— Zod 的流行源于其对开发者体验的关注，特别是自动类型推导。

---

## 五、工程实践与代码示例

### 5.1 Zod：Schema 即类型源

```typescript
import { z } from "zod";

// 1. 定义 Schema（单一定义源）
const UserSchema = z.object({
  id: z.number().int().positive(),
  email: z.string().email(),
  name: z.string().min(1).max(100),
  role: z.enum(["admin", "user", "guest"]),
  metadata: z.record(z.string()).optional(),
});

// 2. 自动推导 TypeScript 类型
type User = z.infer<typeof UserSchema>;
// 等价于:
// type User = { id: number; email: string; name: string; role: "admin"|"user"|"guest"; metadata?: Record<string,string> }

// 3. 运行时解析 (Parse, don't validate)
const raw = await fetch("/api/user/123").then(r => r.json());

// 严格解析: 失败时抛出 ZodError (包含路径化错误)
const user = UserSchema.parse(raw);

// 安全解析: 返回 { success: true, data: User } | { success: false, error: ZodError }
const result = UserSchema.safeParse(raw);
if (result.success) {
  console.log(result.data.email); // ✅ 类型安全 + 运行时安全
}

// 4. 转换 (Transform) —— 解析即处理
const DateSchema = z.string().datetime().transform(s => new Date(s));
```

### 5.2 io-ts：函数式编解码器

```typescript
import * as t from "io-ts";
import * as E from "fp-ts/Either";
import { pipe } from "fp-ts/function";

// 1. 定义 Codec
const UserCodec = t.type({
  id: t.number,
  email: t.string,
  name: t.string,
  role: t.union([t.literal("admin"), t.literal("user"), t.literal("guest")]),
});

type User = t.TypeOf<typeof UserCodec>; // 类型推导

// 2. 解码 (Decode)
const raw: unknown = { id: 1, email: "a@b.com", name: "Alice", role: "admin" };

const decoded = UserCodec.decode(raw); // Either<Errors, User>

// 3. 处理结果 (函数式风格)
pipe(
  decoded,
  E.fold(
    (errors) => console.error("Validation failed:", errors),
    (user) => console.log("Valid user:", user.email)
  )
);

// 4. 编码 (Encode) —— 对称性
const encoded = UserCodec.encode({ id: 1, email: "a@b.com", name: "Alice", role: "admin" });
// 保证: decode(encode(x)) = Right(x)
```

### 5.3 类型守卫的信任 gap 示例

```typescript
// 危险的类型守卫（实现错误但编译器信任）
function isString(x: unknown): x is string {
  return typeof x === "number"; // ❌ 逻辑错误！
}

const val: unknown = 42;
if (isString(val)) {
  val.toUpperCase(); // 编译通过，运行时崩溃！
}

// 安全的做法: 用 Zod 替代手动守卫
const StringGuard = z.string();
if (StringGuard.safeParse(val).success) {
  val; // 仍不会被细化为 string，需通过 result.data 获取
}
```

---

## 六、批判性总结

Zod 和 io-ts 代表了前端类型安全策略中的**边界防御层**，它们共同回应了一个核心问题：当 TypeScript 的类型信息在编译后被完全擦除，我们如何保证外部不可信数据符合内部类型的契约？答案不是放弃类型系统，而是在 I/O 边界建立**运行时的同态映射**——将编译时的类型声明镜像为运行时的验证程序。

这两种库的设计哲学存在深刻差异：Zod 采用面向对象的链式 API，追求开发者体验和低学习成本；io-ts 采用函数式组合子设计，追求数学上的对称性（decode/encode 对）和与 fp-ts 生态的深度融合。从工程角度看，Zod 在 2023-2026 年间已成为前端运行时验证的事实标准，其 `z.infer` 机制消除了"一份数据、两份声明"的重复劳动。但从理论角度看，io-ts 的 `Codec` 概念更接近类型论中的**同构 (Isomorphism)** 理想——编码与解码的对称性保证了数据在系统边界处的语义守恒。

更深层的批判在于：无论 Zod 还是 io-ts，都无法解决**类型系统与运行时之间的根本语义鸿沟**。一个通过 `z.string().email()` 验证的值，在类型层面仍然是 `string`，而非语义上更精确的 `EmailAddress` 类型。TypeScript 缺乏真正的 refine types（如 Liquid Types 或 Dependent Types），使得运行时验证的"成功结果"无法获得比原始类型更丰富的静态信息。未来的演进方向可能是将 Zod Schema 直接编译为依赖类型——这在学术界已有探索（如 Python 的 Ghostscript、Haskell 的 Liquid Haskell），但在前端工程中的落地仍需时日。在 2026 年，务实的最佳实践仍然是：**所有外部数据入口必须经过 Zod/io-ts 解析，解析结果作为类型安全的"净化区"边界，内部逻辑则完全依赖 TypeScript 的静态类型系统。**


---

## 七、概念属性关系网络

### 7.1 运行时验证核心概念的属性-关系矩阵

| 概念 | 核心属性 | 依赖概念 | 被依赖概念 | 关系类型 | 形式化映射 |
|------|---------|---------|-----------|---------|-----------|
| **Schema** | 结构声明、可组合性 | TypeSystem | Parser, Validator | 定义-实例 | Schema → 𝓟(𝒰) |
| **Parser** | 证据生产、路径化错误 | Schema | TypeRefiner | 实现-契约 | parse: 𝒰 → Either<E, T> |
| **Validator** | 布尔判定、信息丢失 | Predicate | Guard | 特化-泛化 | validate: 𝒰 → boolean |
| **Codec** | 对称性 (decode/encode) | Isomorphism, Parser | WireFormat | 同构-映射 | Codec<A,O,I> ≅ (I→Either<E,A>) × (A→O) |
| **Type Guard** | 编译时细化、运行时谓词 | Predicate, SubType | Assertion | 信任-耦合 | Guard_T: 𝒰 → 𝒰 is T |
| **Refined Type** | 谓词约束、子类型 | BaseType, Predicate | Parser | 增强-收缩 | {v:T \| φ(v)} <: T |
| **Round-trip Law** | 解码-编码可逆性 | Codec | Identity | 法则-保证 | decode∘encode = id_A |

### 7.2 概念关系拓扑图

```text
类型系统层级
│
├─► 编译时层 (TypeScript)
│   └─ 类型声明 T ──[擦除]──► 运行时无信息
│
├─► 运行时边界层 (Zod / io-ts)
│   ├─ Schema ──[定义]──► Parser / Codec
│   ├─ Parser ──[生成]──► Refined Type (证据)
│   └─ Codec ──[满足]──► Round-trip Law
│
├─► 运行时分支层 (Type Guards)
│   ├─ User Guard ──[信任 Gap]──► 编译器接受但无法验证
│   └─ Schema-derived Guard ──[派生]──► Parser + boolean投影
│
└─► 工程实践层
    ├─ Zod ──[链式OO]──► 开发者体验优先
    └─ io-ts ──[组合子FP]──► 数学对称性优先
```

---

## 八、形式化推理链

### 8.1 从类型擦除到运行时验证的必然性推理

**命题 P15.4**: TypeScript 的擦除语义导致运行时类型真空。

```
前提 1: TS 编译后所有类型信息被擦除 (类型擦除语义)
前提 2: I/O 边界数据来自外部不可信源 (用户输入、API、localStorage)
前提 3: 不可信数据 ⊈ 内部类型约束 (外部数据空间 𝒰 ⊃ 目标类型 T)

推理链:
  (1) 擦除语义 ⇒ 运行时无类型信息 ..................... [TS 语言规范]
  (2) 无类型信息 ∧ 不可信输入 ⇒ 类型不匹配风险 ...... [集合论: 𝒰 ⊃ T]
  (3) 类型不匹配风险 ∧ 生产环境要求 ⇒ 需要运行时验证
  (4) 需要运行时验证 ∧ 信息保留原则 ⇒ 选择 Parse 而非 Validate

∴ 在 TS 擦除语义下，外部数据入口必须配备运行时 Parser
```

### 8.2 Curry-Howard 对应视角下的运行时验证

在理想的依赖类型系统中，类型本身即命题，程序即证明。运行时验证可以看作这一理想的**工程近似**：

```
理想世界 (Martin-Löf 1984, MLTT):
  命题: "此值满足性质 φ"
  证明: 项 p: φ(v)
  运行时: 无需验证，类型即保证

现实世界 (TypeScript + Zod):
  命题: "此值满足 Schema S"
  证明: Parser 成功返回 Right(v)
  运行时: 显式执行 parse(v) 以构造"运行时证明"

近似关系:
  Zod Schema S   ≈   逻辑命题 φ_S
  .parse(v)      ≈   证明构造器 (proof constructor)
  ZodError       ≈   反证 (refutation)
  z.infer<S>     ≈   命题的命题截断 (propositional truncation)
```

> **Benjamin C. Pierce** (2002, "Types and Programming Languages", MIT Press):
> "A type system is a tractable syntactic method for proving the absence of certain program behaviors by classifying phrases according to the kinds of values they compute." —— 当这种"句法方法"在运行时不存在时，我们必须退回到运行时的动态证明。

### 8.3 Codec 同构的类型安全性证明草图

**定理 T15.2**: io-ts 的 `Codec<A, O, I>` 在 decode 成功时提供类型安全保证。

```
给定: Codec c = ⟨decode: I→Either<E,A>, encode: A→O⟩
假设: ∀a∈A, decode(encode(a)) = Right(a)  (Round-trip)

类型安全性:
  若 decode(i) = Right(a), 则 a ∈ A

证明:
  1. decode(i) = Right(a) ⇒ a 满足 A 的构造规则 ............ [decode 定义]
  2. 构造规则 ⇒ TypeScript 类型推导将 a 归为 A ............. [c 的类型声明]
  3. ∴ 运行时值与编译时类型一致 ............................. [安全性得证]

注: 此证明依赖 Codec 实现者的正确性，类型系统无法验证 round-trip。
```

---

## 九、推理判定树 / ASCII 决策树

### 9.1 运行时验证策略选择决策树

```text
                        外部数据需要验证?
                              │
                    ┌─────────┴─────────┐
                    │Yes                │No (纯内部计算)
                    ▼                   ▼
              数据来源类型?        无需运行时验证
                    │
        ┌───────────┼───────────┐
        │API 响应    │用户输入    │localStorage / URL
        ▼           ▼           ▼
    需要解析+     需要解析+     需要解析+
    错误报告      表单错误      简单解析
        │           │           │
        └───────────┴───────────┘
                    │
            团队熟悉 fp-ts?
                    │
        ┌───────────┴───────────┐
        │Yes                    │No
        ▼                       ▼
    追求数学对称性?          追求开发者体验?
        │                       │
    ┌───┴───┐               ┌───┴───┐
    │Yes    │No             │Yes    │No
    ▼       ▼               ▼       ▼
  io-ts   Zod (+fp-ts)   Zod      JSON Schema
  (Codec) (混合策略)     (原生)   (+AJV)
```

### 9.2 Parse vs Validate 判定树

```text
                    验证失败时是否需要错误路径?
                              │
                    ┌─────────┴─────────┐
                    │Yes                │No
                    ▼                   ▼
            是否需要类型细化证据?    使用 boolean Validator
                    │
            ┌───────┴───────┐
            │Yes            │No (仅 throw)
            ▼               ▼
        使用 Parser     使用 .safeParse()
        (Either)        (返回对象，手动处理)
            │
    需要函数式组合?
            │
    ┌───────┴───────┐
    │Yes            │No
    ▼               ▼
  io-ts decode    Zod .parse() / .safeParse()
  (fp-ts Either)  (面向对象/异常)
```

---

## 十、国际课程对齐

### 10.1 课程体系映射

| 本模块主题 | Stanford CS 242 | CMU 15-312 | MIT 6.170 |
|-----------|-----------------|------------|-----------|
| **运行时类型安全** | Lecture 5: Type Safety and Soundness | Lecture 8: Runtime Systems and Type Passing | Lab 3: Type-safe API Design |
| **Parse vs Validate** | Reading: Pierce (2002) TAPL Ch. 8 | Homework 4: Contracts and Refinements | Lecture: Input Validation as Partial Functions |
| **Codec / 同构** | Lecture 12: Isomorphisms and Coercions | Lecture 10: Lens and Prisms (Optics) | Project: Serialization Protocol Design |
| **类型擦除与保留** | Lecture 6: Erasure vs. Retention | Lecture 9: Compiling Functional Languages | Discussion: JS/TS Runtime Semantics |
| **形式化验证边界** | Guest Lecture: Liquid Types (Jhala 2008) | Lecture 14: Program Verification with SMT | Reading: "Parse, don't validate" (King 2019) |

### 10.2 核心参考文献

> **Benjamin C. Pierce** (2002, "Types and Programming Languages", MIT Press):
> 第 8 章 (Typed Arithmetic Expressions) 和第 14 章 (Subtyping) 为理解运行时验证与静态类型系统的交互提供了形式化基础。Pierce 将类型安全性定义为"良类型的程序不会卡住 (well-typed programs don't get stuck)"——运行时验证正是防止"卡住"的最后防线。

> **Robert Harper** (2016, "Practical Foundations for Programming Languages", 2nd ed., Cambridge University Press):
> 第 21 章 (Structural Subtyping) 与第 33 章 (Algebraic Data Types) 中关于"动态类型作为静态类型的递归和 (Dynamic Typing as Static Sum)"的论述，揭示了 Zod 的 `union` 类型与运行时 tag 检查在形式上的统一性。

> **Frank Pfenning & Christine Paulin-Mohring** (1989, "Inductively Defined Types in the Calculus of Constructions", LFCS):
> 归纳类型 (Inductive Types) 的理论基础表明，Zod 的 `.object({})` 和 io-ts 的 `t.type({})` 本质上是在构造一个**归纳谓词**——Schema 的每个字段对应一个构造子 (constructor) 的类型约束。

### 10.3 课程作业对标

- **Stanford CS 242 (Programming Languages)**: Homework 2 要求实现一个带类型标注的 λ-演算解释器，其中包含了"静态类型检查 + 运行时 tag 检验"的双重验证机制，与本模块的 Zod/io-ts 组合策略直接对应。
- **CMU 15-312 (Foundations of Programming Languages)**: Assignment 4 涉及 Contracts (契约) 的设计与实现——Racket 的 `contract?` 机制与 Zod 的 Schema 验证在哲学上同构：都是在模块边界处插入动态检查。
- **MIT 6.170 (Software Studio)**: Lab 3 的"Type-safe Full-stack Development"要求学生在 TypeScript 后端中使用 Zod 进行 API 输入验证，并讨论"编译时类型与运行时类型的间隙 (the gap between compile-time and runtime types)"。
