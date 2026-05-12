# 同伦类型论 HoTT

> 同伦类型论（Homotopy Type Theory）深化内容，与 Cambridge L313、CMU 80-518、nLab 对齐。
>
> HoTT 为形式化架构理论提供了「命题即类型、证明即程序、等价即路径」的统一视角，是连接数学基础与计算机科学的桥梁理论。

## 核心内容

### 主要文档

- [同伦类型论 HoTT 总论](./00-同伦类型论HoTT总论.md) - 单值公理、恒等类型、高阶归纳类型
- [HoTT 与软件架构](./01-HoTT与软件架构.md) - 同伦视角下的架构演化与等价性

### 理论要点

#### 1. 类型即空间（Types as Spaces）
- 类型 $A$ 被解释为空間，元素 $a, b : A$ 之间的恒等类型 $a =_A b$ 被解释为从 $a$ 到 $b$ 的路径空间
- 路径复合、路径逆转满足群胚（groupoid）结构，高阶路径满足 $
infty$-群胚结构

#### 2. 单值公理（Univalence Axiom）
- 对于类型 $A, B$，等价关系 $A \simeq B$ 与恒等关系 $A =_{\mathcal{U}} B$ 在单值公理下等价
- 在软件架构中的意义：「结构等价即结构恒等」，支持架构重构的形式化验证

#### 3. 高阶归纳类型（HITs）
- 通过生成元和关系同时定义类型，支持商类型、截断、推送等构造
- 应用：形式化描述具有等价关系的架构组件（如模块的接口等价类）

## 与相关理论体系的关系

| 理论体系 | 连接点 |
|---|---|
| [数学理论体系](../../02-数学理论体系/) | 同伦论、范畴论、拓扑学基础 |
| [形式语言理论体系](../../03-形式语言理论体系/) | 类型理论、依赖类型、Curry-Howard 对应 |
| [形式模型理论体系](../00-形式模型理论体系总论.md) | 状态转换系统的同伦语义、模型等价 |
| [编程语言理论体系](../../05-编程语言理论体系/) | 依赖类型语言（Coq、Agda、Lean）的实现基础 |

## 2025 对齐

- **国际 Wiki**：
  - [nLab: Homotopy Type Theory](https://ncatlab.org/nlab/show/homotopy+type+theory)
  - [Wikipedia: Homotopy Type Theory](https://en.wikipedia.org/wiki/Homotopy_type_theory)

- **名校课程**：
  - [Cambridge L313: Category Theory and Logic](https://www.cl.cam.ac.uk/teaching/2324/L313/)（范畴论与同伦类型论）
  - [CMU 80-518: Homotopy Type Theory](https://www.cmu.edu/dietrich/philosophy/hott/)（同伦类型论）

- **代表性论文/著作**：
  - *Homotopy Type Theory: Univalent Foundations of Mathematics* (Univalent Foundations Program, 2013)
  - *Type Theory and Formal Proof* (Nederpelt & Geuvers, 2014)

- **前沿工具**：
  - [Coq](https://coq.inria.fr/)（含 HoTT 库）
  - [Agda](https://wiki.portal.chalmers.se/agda/pmwiki.php)（依赖类型编程）
  - [Lean](https://leanprover.github.io/)（定理证明器，mathlib4 支持大量同伦内容）

- **对齐状态**：已完成（最后更新：2026-05-13）

## 相关

- [类型论基础](../../02-数学理论体系/08-类型论基础.md)
- [形式模型理论体系总论](../00-形式模型理论体系总论.md)
- [编程语言理论体系/00-类型理论-范畴论基础-2025版](../../05-编程语言理论体系/00-类型理论-范畴论基础-2025版.md)

---

**版本**: v2.0
**状态**: ✅ 导航与理论要点已完善
**最后更新**: 2026-05-13
