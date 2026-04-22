# λ演算：函数抽象与组合

> **定位**：λ演算是计算理论的"原子"——图灵机证明了什么是可计算的，λ演算证明了计算本质上就是函数应用。它是Lisp、Haskell、ML等函数式语言的理论根基。
>
> **核心命题**：λ演算只有三种构造（变量、抽象、应用），却足以表达所有可计算函数。这种极简主义揭示了计算的深层统一性。

---

## 一、思维导图：λ演算核心

```text
λ演算（Lambda Calculus）
│
├─【三种构造】
│   ├─ 变量（Variable）：x, y, z
│   ├─ 抽象（Abstraction）：λx.M（函数定义）
│   └─ 应用（Application）：(M N)（函数调用）
│
├─【核心操作】
│   ├─ α转换（Alpha）：变量重命名
│   ├─ β归约（Beta）：函数应用 (λx.M)N → M[x:=N]
│   └─ η转换（Eta）：λx.(f x) ↔ f（若x不在f中自由出现）
│
├─【表达能力】
│   ├─ 布尔值：TRUE = λx.λy.x, FALSE = λx.λy.y
│   ├─ 自然数：Church编码
│   ├─ 递归：Y组合子
│   └─ 图灵完备：可模拟任意图灵机
│
└─【现代影响】
    ├─ 函数式编程（Lisp, Haskell, ML）
    ├─ 类型理论（Simply Typed λ, System F）
    └─ 编程语言语义
```

---

## 二、λ演算的形式化语法

> **权威来源**：Alonzo Church, "An Unsolvable Problem of Elementary Number Theory", *American Journal of Mathematics*, 1936

```
语法定义：
  M, N ::= x           （变量）
         | λx.M        （抽象：x为形参，M为体）
         | (M N)       （应用：将函数M应用于参数N）

β归约（核心计算规则）：
  (λx.M) N →β M[x := N]

  含义：将函数体M中所有自由出现的x替换为N

示例：
  (λx.x) y →β y
  (λx.x x) (λx.x x) →β (λx.x x) (λx.x x)  // 无限归约！

Church编码（自然数）：
  0 = λf.λx.x
  1 = λf.λx.f x
  2 = λf.λx.f (f x)
  3 = λf.λx.f (f (f x))

  SUCCESSOR = λn.λf.λx.f (n f x)
  PLUS = λm.λn.λf.λx.m f (n f x)

Y组合子（递归）：
  Y = λf.(λx.f (x x)) (λx.f (x x))

  性质：Y g = g (Y g)
  → 实现不动点递归
```

---

## 三、λ演算与类型理论

```
Simply Typed λ Calculus（STLC）：
  类型：τ ::= Bool | Nat | τ → τ

  类型规则：
    Γ ⊢ x : τ        若 Γ(x) = τ
    Γ ⊢ λx:τ₁.M : τ₁ → τ₂   若 Γ, x:τ₁ ⊢ M : τ₂
    Γ ⊢ M N : τ₂     若 Γ ⊢ M : τ₁ → τ₂ 且 Γ ⊢ N : τ₁

关键性质：
  - 强规范化：所有良类型的项都有有限归约序列
  → 对应：停机（在STLC中所有程序都停机！）

  - 限制：STLC不是图灵完备的
  → 需要增加递归类型或general recursion

Curry-Howard同构：
  类型 = 命题
  程序 = 证明

  A → B = 若A则B
  A × B = A且B
  A + B = A或B

  → 编程与证明是同一枚硬币的两面
```

---

## 四、概念定义与属性关系

| 概念 | 定义 | 属性 | 示例 | 反例 |
|------|------|------|------|------|
| **λ抽象** | λx.M：以x为参数的函数 | 匿名、高阶、可嵌套 | λx.x（恒等函数） | 具名函数定义 |
| **β归约** | (λx.M)N → M[x:=N] | 核心计算规则、可能无限 | (λx.x)y → y | α转换（非计算） |
| **Church编码** | 用λ项编码数据结构 | 纯λ、无需原始类型 | Church数 | 内置整数类型 |
| **Y组合子** | 实现递归的不动点组合子 | 自应用、类型系统中需递归类型 | Y = λf.(λx.f(xx))(λx.f(xx)) | 直接递归定义 |
| **Curry-Howard** | 类型与命题、程序与证明的对应 | 深刻、跨学科、影响深远 | 程序类型 = 逻辑命题 | 无类型程序 |

---

## 五、交叉引用

- → [01-总览](./00-总览-可计算性与计算模型谱系.md)
- → [01/01-可计算性](01-可计算性边界-停机问题与Rice定理.md)
- → [01/03-时序逻辑](03-时序逻辑-LTL与CTL的分类与应用.md)
- ↓ [07/04-Rust类型系统](../../07-形式化方法与验证体系/04-Rust类型系统-借检查器作为轻量级分离逻辑.md)

---

## 六、参考文献

| 作者 | 标题 | 出处 | 年份 |
|------|------|------|------|
| Alonzo Church | "An Unsolvable Problem of Elementary Number Theory" | *American Journal of Mathematics* | 1936 |
| Henk Barendregt | *The Lambda Calculus: Its Syntax and Semantics* | North-Holland | 1984 |
| Benjamin Pierce | *Types and Programming Languages* | MIT Press | 2002 |
| Sørensen, Urzyczyn | *Lectures on the Curry-Howard Isomorphism* | Elsevier | 2006 |

---

*文件创建日期：2026-04-23*
*状态：已完成*
