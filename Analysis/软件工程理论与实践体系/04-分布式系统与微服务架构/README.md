# 04-分布式系统与微服务架构

> **最后更新**: 2025年11月11日
> **状态**: ✅ 持续完善中

## 概述

本主题深入探讨构建现代化、可扩展、高弹性的分布式系统与微服务架构所需的核心理论、关键技术和设计模式。
内容从CAP、FLP等经典分布式理论出发，系统性地梳理了微服务架构的设计原则，并深入剖析了服务发现、API网关、服务网格、分布式事务等核心组件的实现机制与最佳实践，旨在为设计和实现复杂的云原生应用提供坚实的理论基础和实践指南。

## 目录

- [04-分布式系统与微服务架构](#04-分布式系统与微服务架构)
  - [概述](#概述)
  - [目录](#目录)
  - [内容索引](#内容索引)
    - [01-理论基础](#01-理论基础)
    - [02-核心算法](#02-核心算法)
    - [03-架构模式](#03-架构模式)
    - [04-关键组件与实践](#04-关键组件与实践)
  - [2025 对齐](#2025-对齐)
    - [国际 Wiki](#国际-wiki)
    - [名校课程](#名校课程)
    - [代表性论文](#代表性论文)
    - [前沿技术](#前沿技术)
    - [对齐状态](#对齐状态)
  - [相关文档](#相关文档)
    - [主题内相关文档](#主题内相关文档)
    - [体系内相关文档](#体系内相关文档)

## 内容索引

### 01-理论基础

- [系统与故障模型](./01-理论基础/01-系统与故障模型.md)
  - *内容：定义分布式系统中的基本模型，包括节点、网络，以及崩溃、遗漏、拜占庭等不同的故障类型。*
- [CAP定理与设计权衡](./01-理论基础/02-CAP定理与设计权衡.md)
  - *内容：详细阐述CAP定理（一致性、可用性、分区容错性）的内涵，以及在实际系统设计中如何根据业务场景进行权衡。*
- [分布式系统核心理论(CAP_FLP_Etc)](./01-理论基础/03-分布式系统核心理论(CAP_FLP_Etc).md)
  - *内容：对CAP理论、FLP不可能原理等构建分布式系统的理论基石进行深入探讨。*

### 02-核心算法

- [共识算法概览](./02-核心算法/00-共识算法概览.md)
  - *内容：介绍在分布式系统中解决一致性问题的核心——共识算法，包括Paxos、Raft及其变种的概述。*
- [Raft协议详解](./02-核心算法/01-Raft协议详解.md)
  - *内容：深入分析Raft协议，包括领导者选举、日志复制、安全性等关键机制，并提供Rust实现参考。*
- [实用拜占庭容错PBFT](./02-核心算法/02-实用拜占庭容错PBFT.md)
  - *内容：探讨如何在允许恶意或故障节点存在的情况下达成共识的PBFT算法。*

### 03-架构模式

- [微服务架构核心原则与模式](./03-架构模式/01-微服务架构核心原则与模式.md)
  - *内容：探讨限界上下文（Bounded Context）、单一职责、数据库分离等微服务核心原则。*
- [API网关模式](./03-架构模式/02-API网关模式.md)
  - *内容：阐述API网关在路由、认证、聚合、限流等方面扮演的关键角色。*
- [服务间通信(RPC_事件驱动)](./03-架构模式/03-服务间通信(RPC_事件驱动).md)
  - *内容：对比同步（REST, gRPC）与异步（消息队列）通信方式的优缺点及适用场景。*
- [分布式事务与Saga模式](./03-架构模式/04-分布式事务与Saga模式.md)
  - *内容：解决跨服务数据一致性难题，详细介绍Saga模式的协同式与编排式实现。*
- [CQRS与事件溯源模式](./03-架构模式/05-CQRS与事件溯源模式.md)
  - *内容：讲解命令查询职责分离（CQRS）与事件溯源（Event Sourcing）这两种高级数据处理模式。*

### 04-关键组件与实践

- [服务发现与注册(Consul_Etcd)](./04-关键组件与实践/01-服务发现与注册(Consul_Etcd).md)
  - *内容：分析客户端发现和服务端发现模式，并介绍Consul、Etcd等主流注册中心的原理与应用。*
- [分布式配置管理](./04-关键组件与实践/02-分布式配置管理.md)
  - *内容：探讨在分布式环境中实现配置的统一管理、动态更新与版本控制。*
- [服务网格(Service_Mesh_Istio_Linkerd)](./04-关键组件与实践/03-服务网格(Service_Mesh_Istio_Linkerd).md)
  - *内容：深入剖析服务网格如何通过Sidecar模式将服务治理能力从业务代码中剥离。*
- [容器化与编排(Docker_Kubernetes)](./04-关键组件与实践/04-容器化与编排(Docker_Kubernetes).md)
  - *内容：阐述Docker和Kubernetes在微服务部署、扩缩容和管理中的核心作用。*
- [分布式系统可观测性](./04-关键组件与实践/05-分布式系统可观测性.md)
  - *内容：概述在分布式环境下实现日志、指标和追踪的挑战与解决方案，并链接至`06-可观测性与OpenTelemetry`主题。*

---

## 2025 对齐

### 国际 Wiki

- **Wikipedia**: [Distributed computing](https://en.wikipedia.org/wiki/Distributed_computing)
- **Wikipedia**: [Microservices](https://en.wikipedia.org/wiki/Microservices)
- **Wikipedia**: [Service mesh](https://en.wikipedia.org/wiki/Service_mesh)
- **Wikipedia**: [CAP theorem](https://en.wikipedia.org/wiki/CAP_theorem)
- **Wikipedia**: [Raft (algorithm)](https://en.wikipedia.org/wiki/Raft_(algorithm))

### 名校课程

- **MIT**: [6.824 Distributed Systems](https://pdos.csail.mit.edu/6.824/)
- **Stanford**: [CS244b: Distributed Systems](https://web.stanford.edu/class/cs244b/)
- **CMU**: [15-440 Distributed Systems](https://www.cs.cmu.edu/~dga/15-440/)
- **Berkeley**: [CS 162 Operating Systems](https://cs162.eecs.berkeley.edu/)

### 代表性论文

- **分布式系统理论**：
  - [Impossibility of Distributed Consensus with One Faulty Process](https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf) - FLP不可能原理
  - [Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services](https://users.ece.utexas.edu/~garg/dist/readings/brewer.pdf) - CAP定理

- **微服务架构**：
  - [Microservices: a definition of this new architectural term](https://martinfowler.com/articles/microservices.html)
  - [Building Microservices](https://www.oreilly.com/library/view/building-microservices/9781491950340/)

- **共识算法**：
  - [In Search of an Understandable Consensus Algorithm](https://raft.github.io/raft.pdf) - Raft算法
  - [Practical Byzantine Fault Tolerance](https://pmg.csail.mit.edu/papers/osdi99.pdf) - PBFT算法

### 前沿技术

- **微服务框架**：
  - [Go-kit](https://gokit.io/)
  - [Go-micro](https://github.com/asim/go-micro)
  - [Kratos](https://go-kratos.dev/)

- **服务网格**：
  - [Istio](https://istio.io/)
  - [Linkerd](https://linkerd.io/)
  - [Consul Connect](https://www.consul.io/docs/connect)

- **容器编排**：
  - [Kubernetes](https://kubernetes.io/)
  - [Docker Swarm](https://docs.docker.com/engine/swarm/)
  - [Nomad](https://www.nomadproject.io/)

- **服务发现**：
  - [etcd](https://etcd.io/)
  - [Consul](https://www.consul.io/)
  - [Zookeeper](https://zookeeper.apache.org/)

### 对齐状态

- **标准对齐**: ✅ 已对齐ISO/IEC/IEEE/ACM 2025年标准
- **内容完整性**: ✅ 核心内容已完善，持续补充中
- **实践案例**: ✅ 基础案例已覆盖，持续扩展中
- **最后更新**: 2025年11月11日

---

## 相关文档

### 主题内相关文档

- [分布式系统与微服务架构理论与实践](../04-分布式系统与微服务架构理论与实践.md)
  - *内容：系统梳理分布式系统与微服务架构的核心理论、设计模式、服务治理、弹性架构、云原生与工程实践，包含分布式系统核心原理、微服务架构设计与模式、服务治理与弹性架构、云原生与服务网格、API网关与通信协议等完整内容。*

### 体系内相关文档

- [软件工程理论与实践体系总论](../00-体系总论.md)
- [进度追踪与上下文](../进度追踪与上下文.md)
- [2025年11月标准对齐全面梳理报告](../2025年11月标准对齐全面梳理报告.md)
- [形式化架构理论统一计划-2025标准对齐版](../../../00-形式化架构理论统一计划-2025标准对齐版.md)
