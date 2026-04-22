# 时序逻辑：LTL与CTL的分类与应用

> **定位**：时序逻辑是描述系统"随时间变化的行为"的形式化语言。它是模型检测（Model Checking）和形式化验证的理论基础——让"系统永远不会死锁"这样的属性变得可数学表述。
>
> **核心命题**：LTL描述线性时间路径上的属性，CTL描述分支时间树上的属性。理解它们的表达力差异，是选择验证工具的关键。

---

## 一、思维导图：时序逻辑谱系

```text
时序逻辑（Temporal Logic）
│
├─【线性时序逻辑（LTL）】
│   ├─ 描述单条执行路径上的属性
│   ├─ 运算符：X（Next）, F（Future/Eventually）, G（Globally/Always）
│   │           U（Until）, R（Release）
│   ├─ 不可表达：存在某条路径满足...
│   └─ 工具：SPIN, NuSMV (LTL模式)
│
├─【计算树逻辑（CTL）】
│   ├─ 描述所有可能执行路径的树结构
│   ├─ 路径量词：A（All paths）, E（Exists path）
│   ├─ 状态量词：X, F, G, U（与LTL相同含义）
│   ├─ 必须组合使用：AF, EG, AU等
│   └─ 工具：NuSMV, UPPAAL
│
├─【CTL*】
│   └─ LTL + CTL的并集（超集）
│
└─【应用】
    ├─ 协议验证（互斥、活性）
    ├─ 硬件验证（时序电路）
    └─ 软件验证（死锁、资源泄漏）
```

---

## 二、LTL语法与语义

```
LTL公式语法：
  φ ::= p | ¬φ | φ ∧ φ | X φ | φ U φ | F φ | G φ

  p = 原子命题
  X φ = Next φ（下一状态φ为真）
  F φ = Eventually φ（某个未来状态φ为真）
  G φ = Globally φ（所有未来状态φ为真）
  φ U ψ = φ Until ψ（φ持续为真直到ψ为真）

示例：
  G(request → F response)
    = "始终地，如果有请求，则最终会有响应"
    → 活性（Liveness）属性

  G¬(critical₁ ∧ critical₂)
    = "始终地，进程1和进程2不会同时在临界区"
    → 安全性（Safety）属性

  G(request → (¬grant U request_acked))
    = "始终地，请求后，在获得授权前请求已被确认"
    → 复杂时序约束
```

---

## 三、CTL语法与语义

```
CTL公式语法：
  φ ::= p | ¬φ | φ ∧ φ | AX φ | EX φ
        | AF φ | EF φ | AG φ | EG φ
        | A[φ U φ] | E[φ U φ]

路径量词：
  A = All paths（所有路径）
  E = Exists path（存在至少一条路径）

状态量词：
  X = Next, F = Eventually, G = Globally, U = Until

必须组合使用（不能单独使用X/F/G/U）：
  ✓ AF φ, EG φ, A[p U q]
  ✗ F φ, G φ（CTL语法不允许）

示例：
  AG(request → AF response)
    = "在所有路径的所有状态，请求后最终有响应"

  EF(initial_state)
    = "存在一条路径可到达初始状态"（可复位）

  AG(EF restart)
    = "始终可以从任何状态复位"
    → 非形式化"可恢复性"
```

---

## 四、LTL vs CTL 表达力对比

| 属性 | **LTL** | **CTL** | **说明** |
|------|--------|--------|---------|
| "最终P" | F P | AF P | 两者可表达 |
| "始终P" | G P | AG P | 两者可表达 |
| "P直到Q" | P U Q | A[P U Q] | 两者可表达 |
| "存在路径使P" | 不可表达 | EF P | CTL更强 |
| "P无限次成立" | G F P | 不可直接表达 | LTL更强 |
| "在某路径上始终P" | 不可表达 | EG P | CTL更强 |
| "活性+分支" | 不可表达 | A(GF P → GF Q) | CTL更强 |

---

## 五、概念定义与属性关系

| 概念 | 定义 | 属性 | 示例 | 反例 |
|------|------|------|------|------|
| **LTL** | 线性时序逻辑，描述单路径属性 | 表达无限行为、不可量化路径 | G F P（无限频繁） | EF P（存在路径） |
| **CTL** | 计算树逻辑，描述分支结构 | 可量化路径、不可表达无限频繁 | AG EF reset | G F P |
| **Safety** | "坏事永远不会发生" | 可反例验证（有限路径） | 无死锁 | 有死锁 |
| **Liveness** | "好事终将发生" | 需无限路径验证 | 请求终被响应 | 永远阻塞 |
| **模型检测** | 自动验证时序属性的方法 | 全自动、可反例、状态空间限制 | SPIN验证互斥 | 定理证明（非穷举） |

---

## 六、交叉引用

- → [01-总览](./00-总览-可计算性与计算模型谱系.md)
- → [01/02-计算模型谱系](02-计算模型谱系-从λ演算到进程代数.md)
- → [07/03-模型检测](../07-形式化方法与验证体系/03-模型检测-UPPAAL与状态空间爆炸问题.md)
- ↓ [11/01-Petri网](../11-工作流与并发系统分析/01-Petri网-并发系统的形式化建模.md)

---

## 七、参考文献

| 作者 | 标题 | 出处 | 年份 |
|------|------|------|------|
| Amir Pnueli | "The Temporal Logic of Programs" | *FOCS* | 1977 |
| Clarke, Emerson | "Design and Synthesis of Synchronization Skeletons" | *Logic of Programs* | 1981 |
| Baier, Katoen | *Principles of Model Checking* | MIT Press | 2008 |
| Huth, Ryan | *Logic in Computer Science* (2nd ed.) | Cambridge | 2004 |

---

*文件创建日期：2026-04-23*
*状态：已完成*
