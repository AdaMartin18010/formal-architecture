# 06-可观测性与OpenTelemetry

## 概述

本主题聚焦于现代软件系统的可观测性（Observability），内容涵盖其三大支柱——日志、指标和分布式追踪的原理，并重点探讨了开源标准OpenTelemetry（OTel）的架构、组件和在不同语言（Rust, Go, Java）中的集成实践。此外，本章也为未来探索AI辅助的可观测性创新预留了空间。

## 内容索引

### 01-核心概念

- [可观测性三大支柱](./01-核心概念/01-可观测性三大支柱.md)
  - *内容：介绍可观测性的基本定义，以及构成其基础的三个核心信号：跟踪（Traces）、指标（Metrics）和日志（Logs）。*
- [OpenTelemetry架构与组件](./01-核心概念/02-OpenTelemetry架构与组件.md)
  - *内容：深入探讨OpenTelemetry的分层架构模型（API, SDK, Collector），以及构成其生态系统的核心组件和设计哲学。*

### 02-OpenTelemetry实践

- [OpenTelemetry遥测数据处理](./02-OpenTelemetry实践/01-OpenTelemetry遥测数据处理.md)
  - *内容：详细介绍OpenTelemetry如何处理遥测数据，包括上下文传播（Context Propagation）、处理器（Processor）和导出器（Exporter）等关键概念。*
- [Rust与Go集成实践](./02-OpenTelemetry实践/02-Rust与Go集成实践.md)
  - *内容：提供在Rust和Go这两种高性能语言中集成OpenTelemetry的具体代码示例和场景分析。*
- [Java工作流观测实践](./02-OpenTelemetry实践/03-Java工作流观测实践.md)
  - *内容：展示如何在Java应用中，特别是在工作流引擎的场景下，实现完整的可观测性。*

### 03-AI辅助与创新

- **待补充**
  - *内容：探索如何利用AI和机器学习技术，对收集到的海量遥测数据进行智能分析，实现异常检测、根因定位和性能预测等高级功能。*
