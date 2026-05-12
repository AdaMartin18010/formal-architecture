# 形式语言理论体系

[返回主题树](../00-主题树与内容索引.md) | [主计划文档](../00-形式化架构理论统一计划.md)

## 概述

本目录包含形式化架构理论的形式语言理论体系，提供统一的形式语言理论基础，涵盖从基础语法语义到高级类型理论的完整框架。形式语言理论是连接数学基础与计算机科学的桥梁，为编程语言设计、编译器构造、协议规范、软件验证提供严格的数学工具。

## 文档结构

### 主要文档

- [00-形式语言理论统一总论](./00-形式语言理论统一总论.md) - 形式语言理论体系总览，涵盖乔姆斯基层次、语法理论、语义理论
- 00-形式语言理论体系总论-整合版 - 整合版总论，统一各分支的符号与术语（待补充）
- 00-形式语言理论体系总论-严格形式化版 - 严格形式化版本，含完整公理化（待补充）

### 专题文档

- [00-形式化方法工业标准-2025版](./00-形式化方法工业标准-2025版.md) - 形式化方法工业标准与合规指南
- 01-自动机理论深化 - 有限自动机、下推自动机、图灵机及其在软件工程中的应用（待补充）
- 02-语法理论深化 - 上下文无关语法、属性语法、解析算法（待补充）
- 03-语义理论深化 - 指称语义、操作语义、公理语义的对比与统一（待补充）
- [04-语义理论对比](./04-语义理论对比.md) - 不同语义方法的优缺点分析与选择指南

## 理论体系

### 1. 形式语言基础理论

- **形式语言定义**：字母表、字符串、语言的形式化定义
- **形式语法**：产生式规则、推导、语法树、歧义性
- **形式语义**：从语法到语义的映射，组合性原则

### 2. 乔姆斯基层次结构

| 层次 | 语言类 | 自动机 | 产生式限制 |
|---|---|---|---|
| 类型 3 | 正则语言 | 有限状态自动机 | $A \to aB$ 或 $A \to a$ |
| 类型 2 | 上下文无关语言 | 下推自动机 | $A \to \alpha$ |
| 类型 1 | 上下文相关语言 | 线性有界自动机 | $\alpha A \beta \to \alpha \gamma \beta$ |
| 类型 0 | 递归可枚举语言 | 图灵机 | 无限制 |

### 3. 形式语法理论

- **上下文无关语法（CFG）**：范式转换、语法分析（LL/LR）
- **属性语法**：继承属性、综合属性、语法制导翻译
- **范畴语法**：Lambek 演算、类型语法、自然语言处理应用

### 4. 形式语义理论

- **指称语义**：域论、连续函数、不动点语义
- **操作语义**：大步/小步语义、结构化操作语义（SOS）
- **公理语义**：Hoare 逻辑、最弱前置条件、程序正确性证明

### 5. 类型理论

- **简单类型 λ 演算**：类型安全、正规化定理
- **多态类型系统**：参数多态（System F）、子类型多态、特设多态
- **依赖类型理论**：Π-类型、Σ-类型、Curry-Howard 对应

### 6. 形式化验证

- **语法分析验证**：解析器正确性、语法覆盖性
- **语义分析验证**：类型安全、语义等价性
- **类型检查验证**：类型推导算法的正确性与完备性

## 验证状态

- [x] 语法分析器理论验证
- [x] 语义分析器理论验证
- [x] 类型检查器理论验证
- [x] 乔姆斯基层次结构完整性检查
- [ ] 跨理论体系语义一致性检查（进行中）

## 相关链接

- [数学理论体系](../02-数学理论体系/) - 数学基础（集合论、逻辑、范畴论）
- [形式模型理论体系](../04-形式模型理论体系/) - 模型理论（状态机、Petri 网）
- [软件架构理论体系](../04-软件架构理论体系/) - 架构理论（架构描述语言 ADL）
- [编程语言理论体系](../05-编程语言理论体系/) - 语言实现（编译器、类型系统）

## 2025 对齐

- **国际 Wiki**：
  - [Wikipedia: Formal language](https://en.wikipedia.org/wiki/Formal_language)
  - [Wikipedia: Chomsky hierarchy](https://en.wikipedia.org/wiki/Chomsky_hierarchy)
  - [Wikipedia: Type theory](https://en.wikipedia.org/wiki/Type_theory)
  - [Wikipedia: Semantics of programming languages](https://en.wikipedia.org/wiki/Semantics_of_programming_languages)

- **名校课程**：
  - [CMU 15-312: Foundations of Programming Languages](https://www.cs.cmu.edu/~rwh/courses/ppl/)（类型理论与语义）
  - [MIT 6.035: Computer Language Engineering](https://ocw.mit.edu/courses/6-035-computer-language-engineering-spring-2010/)（编译器与语法分析）
  - [Stanford CS 242: Programming Languages](https://web.stanford.edu/class/cs242/)（语言设计与形式化）

- **代表性论文/著作**：
  - *Types and Programming Languages* (Pierce, 2002)
  - *Semantics with Applications* (Nielson & Nielson, 1992)
  - *Introduction to Automata Theory, Languages, and Computation* (Hopcroft, Motwani & Ullman, 2006)

- **前沿技术**：
  - [ANTLR](https://www.antlr.org/)（语法分析器生成器）
  - [LLVM](https://llvm.org/)（编译器基础设施）
  - [Tree-sitter](https://tree-sitter.github.io/tree-sitter/)（增量解析库）

- **对齐状态**：已完成（最后更新：2026-05-13）

---

**版本**: v2.0
**状态**: ✅ 形式语言理论体系导航已完善
**最后更新**: 2026-05-13
