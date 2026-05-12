# 工作流与自动化平台

> **目录说明**：本目录包含工作流系统、自动化平台、流程编排及相关微服务集成理论文档。建议配合 [00-主题树与内容索引](../../00-主题树与内容索引.md) 和 [07-分布式与微服务理论体系总论](../00-分布式与微服务理论体系总论-整合版.md) 阅读。

## 概述

工作流与自动化平台是分布式系统中协调多服务协作、管理长事务与保证业务一致性的关键基础设施。本目录涵盖工作流理论、主流平台、微服务集成模式及工程实践。

## 核心理论体系

### 1. 工作流理论基础

- **工作流定义**：工作流是一类能够完全或部分自动执行的经营过程，根据一系列过程规则，文档、信息或任务能够在不同执行者之间传递与执行。
- **工作流参考模型**（WfMC）：包含过程定义工具、工作流执行服务、客户端应用、调用应用、管理监控工具五大组件。
- **工作流模式**：控制流模式（顺序、并行、选择、循环）、数据模式、资源模式。

### 2. 工作流建模语言

- **BPMN 2.0**（Business Process Model and Notation）：业务流程建模的行业标准符号体系
- **BPEL**（Business Process Execution Language）：面向 Web 服务的业务流程编排语言
- **状态机工作流**：基于有限状态机的事件驱动工作流建模

### 3. 微服务中的工作流模式

- **Saga 模式**：分布式长事务的补偿机制，分为编排式（Choreography）与协调式（Orchestration）
- **事件溯源（Event Sourcing）**：以事件序列作为系统状态的唯一真相来源
- **CQRS**：命令查询职责分离，优化工作流中的读写性能

### 4. 主流工作流平台

- **Apache Airflow**：以 DAG 为核心的数据管道编排平台
- **Temporal**：具备持久化与容错能力的微服务工作流引擎
- **Camunda**：基于 BPMN 的开源工作流与决策自动化平台
- **Netflix Conductor**：云原生微服务编排引擎

## 文档结构

| 文档 | 内容 |
|---|---|
| [工作流理论基础](./01-工作流理论基础.md) | WfMC 参考模型、工作流模式 |
| [BPMN 与建模语言](./02-BPMN与建模语言.md) | BPMN 2.0 符号、BPEL 规范 |
| [Saga 与长事务模式](./03-Saga与长事务模式.md) | 编排式/协调式 Saga、补偿事务 |
| [主流平台对比](./04-主流平台对比.md) | Airflow、Temporal、Camunda、Conductor |
| [微服务集成实践](./05-微服务集成实践.md) | 与 gRPC/Kafka/事件总线的集成模式 |

## 与相关理论体系的关系

- **上游理论**：[形式模型理论体系](../../06-形式模型理论体系/00-形式模型理论体系总论.md)（Petri 网、状态机）
- **平行理论**：[分布式系统理论](../01-分布式系统理论.md)（共识、一致性）
- **下游实践**：[08-实践应用开发](../../08-实践应用开发/README.md)

## 2025 对齐

- **国际 Wiki**：
  - [Wikipedia: Workflow management system](https://en.wikipedia.org/wiki/Workflow_management_system)
  - [Wikipedia: Business process management](https://en.wikipedia.org/wiki/Business_process_management)
  - [Wikipedia: Saga pattern](https://en.wikipedia.org/wiki/Compensating_transaction)

- **名校课程**：
  - [MIT 6.033: Computer Systems Engineering](https://web.mit.edu/6.033/www/)（分布式系统、工作流管理）
  - [CMU 15-313: Foundations of Software Engineering](https://www.cs.cmu.edu/~ckaestne/17313/)（软件工程实践）

- **代表性论文**：
  - *Workflow Patterns* (van der Aalst et al., 2003)
  - *Saga Pattern* (Garcia-Molina & Salem, 1987)
  - *Practical Dynamo* (DeCandia et al., 2007) — 事件驱动架构基础

- **前沿技术**：
  - [Temporal](https://temporal.io/)（持久化工作流引擎）
  - [Apache Airflow](https://airflow.apache.org/)（数据管道编排）
  - [Camunda](https://camunda.com/)（BPMN 工作流引擎）
  - [Netflix Conductor](https://conductor.netflix.com/)（微服务编排）

- **对齐状态**：已完成（最后更新：2026-05-13）

---

**文档版本**：v2.0
**创建时间**：2025年1月
**状态**：✅ 核心内容已补全
**最后更新**：2026-05-13
