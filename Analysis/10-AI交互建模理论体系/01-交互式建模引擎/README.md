# AI建模引擎实践原型（迁移文档）

本页为从 `FormalUnified/08-实践与应用/AI-Modeling-Engine` 迁移至 `Analysis/10-AI交互建模理论体系/01-交互式建模引擎` 的文档入口，聚焦于理论到实践的映射与导航；源代码仍保留在原路径（见下方链接）。

## 概述

AI建模引擎将形式化架构理论转化为可运行原型，覆盖：

- 语义分析 → 概念提取
- 模型生成 → 状态机 / Petri网 / 统一STS
- AI增强验证 → 模型检查/定理证明/仿真与AI策略
- 多语言代码生成 → Rust / Go / Python

## 快速导航

- 概览与使用说明（源）：[`README.md`](../../../FormalUnified/08-实践与应用/AI-Modeling-Engine/README.md)
- 目录索引（源）：[`index.md`](../../../FormalUnified/08-实践与应用/AI-Modeling-Engine/index.md)
- 原型代码（源）：
  - [`prototype.py`](../../../FormalUnified/08-实践与应用/AI-Modeling-Engine/prototype.py)
  - [`enhanced_prototype.py`](../../../FormalUnified/08-实践与应用/AI-Modeling-Engine/enhanced_prototype.py)
- 配置（源）：[`config.yaml`](../../../FormalUnified/08-实践与应用/AI-Modeling-Engine/config.yaml)

更多文件见《源代码与配置索引》。

## 理论映射（要点）

- 哲学基础 → 概念与推理：本体论/认识论/系统思维 → 概念结构与策略选择
- 数学理论 → 集合/图/逻辑 → 元素、关系与性质规范
- 形式方法 → FSM / Petri网 / USTS → 模型生成与验证接口

## 典型工作流

1) 需求文本 → 语义分析（概念集合）
2) 概念集合 → 形式化模型（FSM/Petri/USTS）
3) 验证性质（reachability/safety/consistency 等，AI增强）
4) 代码生成（Rust/Go/Python）

> 运行演示与完整示例请参见源目录中的 `README.md` 与 `prototype.py`。

## 迁移说明

- 本目录聚焦“理论体系”视角的文档与导航；源实现仍位于 `FormalUnified`，保持可运行环境与历史一致性。
- 后续如需将实现并入 `Analysis/08-实践应用开发`，将在完成运行环境与依赖校验后再行调整。

---
本页由“FormalUnified→Analysis”内容迁移统一计划生成与维护。
