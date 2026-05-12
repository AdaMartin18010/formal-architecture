# 2-WorkflowDomain

> **重定向声明**: 本文档内容已合并至 [05-工作流与自动化平台/](05-工作流与自动化平台/README.md)目录下的相关文件，请参考主权威文件获取最新内容。
> 建议配合[00-主题树与内容索引](../00-主题树与内容索引.md)一同阅读。

## 主题简介

本分支系统性梳理了工作流理论、建模、主流平台、微服务集成、Rust/Go实践、图表分析与参考文献，内容涵盖：

- 建模语言与表达（2.2）✅
- 主流平台与对比（2.3）✅
- 微服务集成模式（2.4）✅
- Rust/Go工程实践（2.5）✅
- 权威参考文献（2.7）✅

各分节已递归补全高质量内容，详见对应文件。

## 分节索引

- [2.2-WorkflowDomain-建模与表达](./2.2-WorkflowDomain-建模与表达.md) ✅ 已修复
- [2.3-WorkflowDomain-主流平台](./2.3-WorkflowDomain-主流平台.md) ✅ 已修复
- [2.4-WorkflowDomain-微服务集成](./2.4-WorkflowDomain-微服务集成.md) ✅ 已修复
- [2.5-WorkflowDomain-RustGo实践](./2.5-WorkflowDomain-RustGo实践.md) ✅ 已修复
- [2.7-WorkflowDomain-参考文献](./2.7-WorkflowDomain-参考文献.md) ✅ 已修复

> **主权威内容请参考 [05-工作流与自动化平台/](05-工作流与自动化平台/README.md) 目录下最新文件。**

## 2025 对齐

- **国际 Wiki**：
  - [Wikipedia: Workflow Management System](https://en.wikipedia.org/wiki/Workflow_management_system)
  - [Wikipedia: Business Process Management](https://en.wikipedia.org/wiki/Business_process_management)

- **名校课程**：
  - [MIT 6.033: Computer Systems Engineering](https://web.mit.edu/6.033/www/)（分布式系统、工作流管理）
  - [Stanford CS 243: Program Analysis and Optimizations](https://web.stanford.edu/class/cs243/)（工作流系统、任务调度）
  - [CMU 15-313: Foundations of Software Engineering](https://www.cs.cmu.edu/~charlie/courses/15-313/)（工作流系统理论和实践）

- **代表性论文**：
  - [Recent Advances in Workflow Management Systems](https://www.sciencedirect.com/science/article/pii/S1570826824000136) (2024)

- **前沿技术**：
  - [Apache Airflow](https://airflow.apache.org/)（工作流编排平台）
  - [Temporal](https://temporal.io/)（工作流编排平台）
  - [n8n](https://n8n.io/)（工作流自动化平台）
  - [Argo Workflows](https://argoproj.github.io/workflows/)（Kubernetes原生工作流引擎）
  - [ISO/IEC 25010:2025](https://www.iso.org/standard/35733.html)（软件质量模型）
  - [IEEE 1012:2025](https://standards.ieee.org/standard/1012-2025.html)（软件验证与确认标准）

## 工作流核心理论要点

### 1. 工作流参考模型（WfMC）

工作流管理联盟（WfMC）定义的参考模型包含五大接口：
- **接口 1**：过程定义导入/导出（XPDL）
- **接口 2/3**：客户端应用与工作流引擎的交互
- **接口 4**：引擎间互操作
- **接口 5**：管理与监控

### 2. Saga 模式与工作流

在微服务架构中，长事务通过 Saga 模式管理：
- **编排式 Saga**：各服务通过事件总线自发协调
- **协调式 Saga**：中央协调器（Orchestrator）统一调度各步骤与补偿操作

### 3. 形式化视角

工作流可形式化为 Petri 网或状态机：
- **Petri 网模型**：任务对应变迁（Transition），条件对应库所（Place）
- **状态机模型**：工作流实例的生命周期对应状态转换路径

## 相关导航

- [05-工作流与自动化平台/README.md](05-工作流与自动化平台/README.md)（主权威）
- [07-分布式与微服务/README.md](../README.md)
- [04-软件架构理论体系/07-工作流架构理论](../04-软件架构理论体系/07-工作流架构理论.md)

- **对齐状态**：已完成（最后更新：2026-05-13）

---

**文档版本**：v2.0
**项目定位**：知识梳理与理论构建项目（非编程项目）
**最后更新**：2026-05-13
