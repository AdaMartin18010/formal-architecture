# 12-工具与方法

> 形式化证明与理论验证相关工具与方法论。本目录涵盖证明助手、模型检查器、SMT 求解器及它们在软件架构验证中的集成方法。
>
> **前置**：[06-形式模型理论体系](../06-形式模型理论体系/00-形式模型理论体系总论.md)、[08-实践应用开发](../08-实践应用开发/README.md)。**后续**：[13-项目报告与总结](../13-项目报告与总结/README.md)。**标准条款映射**：[13-项目报告与总结/00-标准条款与文档映射表](../13-项目报告与总结/00-标准条款与文档映射表.md)（ISO 25010 可验证性/可分析性等）。

## 核心内容

### 主要文档

- [证明助手集成-2025版](./00-证明助手集成-2025版.md) - Coq/Lean/Isabelle 等证明助手集成方法与最佳实践

### 工具谱系

| 类别 | 工具 | 适用场景 |
|---|---|---|
| 证明助手 | Coq | 依赖类型、构造性证明、形式化数学 |
| 证明助手 | Lean 4 | 现代定理证明、mathlib 数学库 |
| 证明助手 | Isabelle/HOL | 高阶逻辑、协议验证 |
| 模型检查 | TLA+ / TLC | 分布式系统规范与验证 |
| 模型检查 | SPIN / Promela | 协议验证、并发模型检查 |
| 模型检查 | UPPAAL | 实时系统模型检查 |
| SMT 求解 | Z3 | 约束求解、程序验证、符号执行 |
| SMT 求解 | CVC5 | 组合理论、SMT-LIB 标准 |
| 静态分析 | Frama-C | C 程序形式化验证 |
| 类型系统 | Liquid Haskell | 精化类型、运行时断言 |

## 方法论框架

### 1. 形式化验证生命周期

```text
需求规格 → 形式化建模 → 性质规约 → 工具验证 → 反例分析 → 模型修正
```

### 2. 工具选择决策树

- **需要数学定理证明** → Coq / Lean / Isabelle
- **需要状态空间探索** → TLA+ / SPIN / UPPAAL
- **需要约束求解/符号执行** → Z3 / CVC5
- **需要代码级验证** → Frama-C / Dafny / Liquid Haskell

### 3. 与软件架构的集成

- **架构模型 → 形式化规约**：将 UML/ArchiMate 模型转换为 TLA+/Alloy 规约
- **性质提取**：从质量属性场景（可用性、安全性、性能）提取时序逻辑公式
- **验证反馈**：将模型检查器的反例转化为架构缺陷报告

## 本节要点与自检

- **要点**：形式化证明与理论验证工具（证明助手集成 Coq/Lean/Isabelle）；与 06-形式模型、08-实践应用 的衔接；ISO 25010 可验证性/可分析性。
- **自检**：
  - 能指出证明助手在形式模型验证中的典型用法？
  - 能描述模型检查器与定理证明器的适用边界？
  - 详见 [2025-对齐参考索引](../2025-对齐参考索引.md) B2、[核心概念表](../00-总览与导航/00-核心概念表（形式化架构）.md)。

## 相关

- [形式化证明增强](../../Modern/09-理论增强与完善/01-形式化证明增强/)
- [理论验证框架](../../Modern/09-理论增强与完善/06-理论验证框架/)
- [03-自动化验证工具设计与实现](../08-实践应用开发/03-自动化验证工具设计与实现.md)

## 2025 对齐

- **国际 Wiki**：
  - [Wikipedia: Proof assistant](https://en.wikipedia.org/wiki/Proof_assistant)
  - [Wikipedia: Model checking](https://en.wikipedia.org/wiki/Model_checking)
  - [Wikipedia: Satisfiability modulo theories](https://en.wikipedia.org/wiki/Satisfiability_modulo_theories)

- **名校课程**：
  - [CMU 15-312: Foundations of Programming Languages](https://www.cs.cmu.edu/~rwh/courses/ppl/)（Coq 证明开发）
  - [MIT 6.822: Formal Reasoning About Programs](https://6826.csail.mit.edu/)（程序形式化验证）

- **前沿技术**：
  - [Lean 4](https://lean-lang.org/)（下一代定理证明器）
  - [Dafny](https://github.com/dafny-lang/dafny)（微软程序验证语言）
  - [ASTRÉE](https://www.absint.com/astree/)（静态分析器，用于航空软件验证）

- **对齐状态**：已完成（最后更新：2026-05-13）

---

**版本**: v2.0
**状态**: ✅ 工具与方法目录已完善
**最后更新**: 2026-05-13
