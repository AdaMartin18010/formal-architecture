# 同伦类型论 HoTT 总论

[返回主题树](../../00-主题树与内容索引.md) | [形式模型理论体系总论](../00-形式模型理论体系总论.md) | [类型论基础](../../02-数学理论体系/08-类型论基础.md)

> **重要声明**：本文档基于 2025 年国际数学与计算机科学标准，提供同伦类型论（Homotopy Type Theory, HoTT）深化内容，与 Cambridge L313、CMU 80-518、nLab 等权威资源对齐。

## 目录

- [1. 概述](#1-概述)
- [2. 单值公理与恒等类型](#2-单值公理与恒等类型)
- [3. 高阶归纳类型](#3-高阶归纳类型)
- [4. 与项目理论映射](#4-与项目理论映射)
- [5. 课程对齐](#5-课程对齐)
- [2025 对齐](#2025-对齐)

---

## 1. 概述

### 1.1 同伦类型论定位

同伦类型论（HoTT）将**类型论**与**同伦论**统一：类型视为空间，恒等类型视为路径，等价视为同伦等价。它为形式化证明、语义理论、编程语言提供统一基础。

### 1.2 核心思想

| 类型论概念 | 同伦论解释 |
|------------|------------|
| 类型 $A$ | 空间（拓扑空间） |
| 项 $a : A$ | 空间中的点 |
| 恒等类型 $a =_A b$ | 从 $a$ 到 $b$ 的路径空间 |
| 等价 $A \simeq B$ | 同伦等价 |
| 单值公理 $A \simeq B \Rightarrow A = B$ | 等价类型可视为同一 |

### 1.3 与形式化架构的关系

- **结构同构**：可形式化为类型等价 $M_{sem} \simeq M_{tech}$
- **语义熵**：类型等价类的多样性度量
- **形式化证明**：HoTT 为 Coq/Lean/Agda 等证明助手提供理论基础

---

## 2. 单值公理与恒等类型

### 2.1 恒等类型

**定义 2.1** (恒等类型)

$$\frac{\Gamma \vdash a : A \quad \Gamma \vdash b : A}{\Gamma \vdash a =_A b : \mathrm{Type}}$$

- **自反性**：$\mathrm{refl}_a : a =_A a$
- **J 规则**：依赖恒等的消除规则

### 2.2 单值公理（Univalence Axiom）

**公理 2.1** (单值)

$$(A \simeq B) \simeq (A = B)$$

即：等价类型与恒等类型等价。等价类型可视为同一类型的不同表示。

### 2.3 与形式化验证

- **Lean 4**：HoTT 为 Lean 的 `Universe` 和 `Equiv` 提供语义
- **Coq**：UniMath 库实现 HoTT 公理
- **Agda**：原生支持 HoTT 风格

---

## 3. 高阶归纳类型

### 3.1 归纳类型扩展

**定义 3.1** (高阶归纳类型 HIT)

高阶归纳类型允许构造子携带**路径**：

$$\mathrm{Circle} : \mathrm{Type} \quad \mathrm{base} : \mathrm{Circle} \quad \mathrm{loop} : \mathrm{base} = \mathrm{base}$$

### 3.2 典型 HIT

- **圆 $S^1$**：`base` + `loop`
- **球面 $S^2$**：`base` + `surf`
- **截断**：$n$-截断 $\|A\|_n$ 将高阶结构截断到 $n$ 阶

### 3.3 与形式模型

- **状态机**：状态空间可视为 HIT（状态 + 转换路径）
- **Petri 网**：库所与变迁可视为带路径的归纳类型

---

## 4. 与项目理论映射

| HoTT 概念 | 项目对应 |
|----------|----------|
| 类型等价 $A \simeq B$ | 结构同构 $M_{sem} \cong M_{tech}$ |
| 单值公理 | 语义等价性形式化 |
| 恒等类型 $a = b$ | 语义实例等价 |
| 路径空间 | 转换/迁移路径 |
| 截断 $\|A\|_0$ | 命题截断（存在性） |

---

## 5. 课程对齐

### 5.1 Cambridge L313

- **同伦类型论与单值基础**（2025-26）
- 链接：<https://www.cl.cam.ac.uk/teaching/2526/L313/>
- 内容：HoTT 公理、单值、高阶归纳类型、形式化证明

### 5.2 CMU 80-518/818

- **逻辑专题：类型论**（Spring 2025）
- 链接：<https://awodey.github.io/typetheory/>
- 内容：Martin-Löf 类型论、HoTT、范畴语义

### 5.3 数学权威教育交叉引用

| 数学基础 | 权威资源 | 与本 HoTT 内容映射 |
|----------|----------|-------------------|
| 离散数学 | MIT 6.042J、Stanford CS 103、Cambridge DiscMath | 归纳、证明技术 |
| 范畴论 | Cambridge CAT、Oxford C2.7、Cornell CS 6117 | 函子、伴随、类型范畴语义 |
| 类型论 | CMU 80-518/818 | Martin-Löf、HoTT 公理 |
| HoTT 实现 | Birmingham HoTT-UF-Agda | Agda 形式化讲义 |

### 5.4 其他资源

- **nLab**：<https://ncatlab.org/nlab/show/homotopy+type+theory>
- **HoTT Book**：<https://homotopytypetheory.org/book/>

---

## 2025 对齐

- **国际 Wiki**：[Wikipedia: Homotopy type theory](https://en.wikipedia.org/wiki/Homotopy_type_theory)
- **HoTT 社区**：<https://homotopytypetheory.org/>
- **Lean 4 HoTT**：<https://github.com/leanprover/lean4>
- **UniMath**：<https://github.com/UniMath/UniMath>
