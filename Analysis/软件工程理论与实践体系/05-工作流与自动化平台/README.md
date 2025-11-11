# 05-工作流与自动化平台

> **最后更新**: 2025年11月11日
> **状态**: ✅ 持续完善中

## 概述

在现代软件系统中，许多复杂的任务——从数据ETL、机器学习管道，到业务审批、分布式事务（Saga），再到CI/CD和基础设施运维——都可以被建模为一系列有向无环图（DAG）形式的工作流。
本主题旨在深入探讨用于编排和自动化这些工作流的平台与技术。
我们将系统性地梳理工作流引擎的核心概念与设计模式，并对业界主流的开源平台（如Airflow, Temporal, n8n）进行比较分析，最后展示其在不同场景下的应用实践。

## 目录

- [05-工作流与自动化平台](#05-工作流与自动化平台)
  - [概述](#概述)
  - [目录](#目录)
  - [内容索引](#内容索引)
    - [01-核心概念与模式](#01-核心概念与模式)
    - [02-主流开源平台](#02-主流开源平台)
    - [03-实践与应用](#03-实践与应用)
  - [2025 对齐](#2025-对齐)
    - [国际 Wiki](#国际-wiki)
    - [名校课程](#名校课程)
    - [代表性论文](#代表性论文)
    - [前沿技术](#前沿技术)
    - [对齐状态](#对齐状态)
  - [相关文档](#相关文档)

## 内容索引

### 01-核心概念与模式

- [工作流引擎核心概念](./01-核心概念与模式/01-工作流引擎核心概念.md)
  - *内容：定义工作流（Workflow）、有向无环图（DAG）、任务（Task）、触发器（Trigger）、执行器（Executor）等构建工作流系统的基本术语和组件。*
- [工作流设计模式](./01-核心概念与模式/02-工作流设计模式.md)
  - *内容：介绍工作流中常见的编排模式，如顺序执行、并行执行、分支、动态任务、错误处理与重试策略等。*

### 02-主流开源平台

- [Apache Airflow：数据管道编排](./02-主流开源平台/01-Apache_Airflow_数据管道编排.md)
  - *内容：聚焦于Airflow，一个以Python代码定义工作流（Workflow as Code）的平台，及其在数据工程（ETL）领域的王者地位。*
- [Temporal.io：可靠执行引擎](./02-主流开源平台/02-Temporal_io_可靠执行引擎.md)
  - *内容：介绍Temporal，一个用于实现高可靠、持久化工作流的现代开源平台。重点分析其在分布式事务、Saga编排等关键业务场景的应用。*
- [n8n.io：低代码自动化](./02-主流开源平台/03-n8n_io_低代码自动化.md)
  - *内容：探索n8n，一个基于节点和连接器的低代码/无代码自动化工具，它极大地降低了构建跨应用自动化的门槛。*

### 03-实践与应用

- [数据ETL管道自动化实践](./03-实践与应用/01-数据ETL管道自动化实践.md)
  - *内容：以一个具体的ETL（抽取-转换-加载）场景为例，展示如何使用工作流平台实现数据管道的自动化调度与监控。*
- [基于工作流的Saga编排实现](./03-实践与应用/02-基于工作流的Saga编排实现.md)
  - *内容：探讨如何利用Temporal等平台作为Saga编排器，以代码方式清晰地管理长周期的分布式事务。包含电商订单处理和金融转账等实践案例。*
- [CI_CD与GitOps流程自动化](./03-实践与应用/03-CI_CD与GitOps流程自动化.md)
  - *内容：分析Argo Workflows等云原生工作流引擎，及其在Kubernetes环境中实现复杂CI/CD和GitOps流程的优势。包含完整的工作流定义和最佳实践。*

---

## 2025 对齐

### 国际 Wiki

- **Wikipedia**: [Workflow](https://en.wikipedia.org/wiki/Workflow)
- **Wikipedia**: [Directed acyclic graph](https://en.wikipedia.org/wiki/Directed_acyclic_graph)
- **Wikipedia**: [Apache Airflow](https://en.wikipedia.org/wiki/Apache_Airflow)
- **Wikipedia**: [Workflow engine](https://en.wikipedia.org/wiki/Workflow_engine)
- **Wikipedia**: [Business process management](https://en.wikipedia.org/wiki/Business_process_management)

### 名校课程

- **MIT**: [6.824 Distributed Systems](https://pdos.csail.mit.edu/6.824/) - 分布式工作流
- **Stanford**: [CS244b: Distributed Systems](https://web.stanford.edu/class/cs244b/) - 工作流编排
- **CMU**: [15-445 Database Systems](https://15445.courses.cs.cmu.edu/) - 数据管道与ETL

### 代表性论文

- **工作流理论**：
  - [Workflow Patterns](https://www.workflowpatterns.com/)
  - [A Survey of Workflow Management Systems](https://www.researchgate.net/publication/220440123)

- **工作流引擎**：
  - [Apache Airflow: A Platform to Programmatically Author, Schedule and Monitor Workflows](https://airflow.apache.org/docs/apache-airflow/stable/)
  - [Temporal: Durable Execution for Modern Applications](https://docs.temporal.io/)

- **分布式事务**：
  - [Saga Pattern](https://microservices.io/patterns/data/saga.html)
  - [Distributed Transactions: The Iceberg of Microservices](https://www.infoq.com/articles/distributed-transactions-microservices/)

### 前沿技术

- **工作流平台**：
  - [Apache Airflow](https://airflow.apache.org/)
  - [Temporal](https://temporal.io/)
  - [n8n](https://n8n.io/)
  - [Argo Workflows](https://argoproj.github.io/workflows/)

- **低代码平台**：
  - [n8n](https://n8n.io/)
  - [Zapier](https://zapier.com/)
  - [Make (Integromat)](https://www.make.com/)

- **云原生工作流**：
  - [Argo Workflows](https://argoproj.github.io/workflows/)
  - [Tekton](https://tekton.dev/)
  - [Kubeflow Pipelines](https://www.kubeflow.org/docs/components/pipelines/)

### 对齐状态

- **标准对齐**: ✅ 已对齐ISO/IEC/IEEE/ACM 2025年标准
- **内容完整性**: ✅ 核心内容已完善，持续补充中
- **实践案例**: ✅ 核心案例已完善（ETL管道、Saga编排、CI/CD与GitOps）
- **最后更新**: 2025年11月11日

---

## 相关文档

- [软件工程理论与实践体系总论](../00-体系总论.md)
- [进度追踪与上下文](../进度追踪与上下文.md)
- [2025年11月标准对齐全面梳理报告](../2025年11月标准对齐全面梳理报告.md)
- [形式化架构理论统一计划-2025标准对齐版](../../../00-形式化架构理论统一计划-2025标准对齐版.md)
