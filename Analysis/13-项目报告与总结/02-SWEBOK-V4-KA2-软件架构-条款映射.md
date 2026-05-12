# SWEBOK V4 KA 2（Software Architecture）条款↔本仓库小节映射

[返回主题树](../00-总览与导航/00-主题树与内容索引.md) | [标准条款与文档映射表](00-标准条款与文档映射表.md) | [项目报告与总结](README.md)

> **用途**：SWEBOK V4.0 知识域 2（Software Architecture）的条款/主题与本仓库文档/小节的逐项映射，便于季度复审与覆盖度检查。
> **依据**：Guide to the Software Engineering Body of Knowledge V4.0（IEEE Computer Society，2024年10月）。
> **维护**：每季度与 SWEBOK 版本同步复审；与 [2025-对齐资源库 第六节](../2025-对齐资源库-最新版.md#六swebok-v4-对齐矩阵2025-09) 及 [00-标准条款与文档映射表](00-标准条款与文档映射表.md) 联动。

## 1. Software Architecture Fundamentals

| SWEBOK 条款/主题 | 本仓库对应文档/小节 | 状态 | 备注 |
|------------------|---------------------|------|------|
| The Senses of "Architecture" | [06-软件架构理论体系/00-软件架构理论体系总论-整合版](../06-软件架构理论体系/00-软件架构理论体系总论-整合版.md)（§1 软件架构定义、架构抽象层次） | 已覆盖 | 与 ISO 42010 视点一致 |
| Stakeholders and Concerns | [06-软件架构理论体系/00-软件架构理论体系总论-整合版](../06-软件架构理论体系/00-软件架构理论体系总论-整合版.md)（架构决策、利益相关方）、[07-分布式与微服务/04-软件架构理论体系](../07-分布式与微服务/04-软件架构理论体系/README.md) | 已覆盖 | 部分在 04-软件架构理论体系总论中 |
| Uses of Architecture | [06-软件架构理论体系](../06-软件架构理论体系/00-软件架构理论体系总论-整合版.md)（架构用途、沟通与决策）、[04-软件架构理论体系/00-软件架构理论统一总论](../04-软件架构理论体系/00-软件架构理论统一总论.md) | 已覆盖 | 主入口为 06 |

## 2. Software Architecture Description

| SWEBOK 条款/主题 | 本仓库对应文档/小节 | 状态 | 备注 |
|------------------|---------------------|------|------|
| Architecture Views and Viewpoints | [06-软件架构理论体系/00-软件架构理论体系总论-整合版](../06-软件架构理论体系/00-软件架构理论体系总论-整合版.md)（架构视图层、视点）、[00-标准条款与文档映射表 §1](00-标准条款与文档映射表.md#1-isoiecieee-42010架构描述) | 已覆盖 | 与 ISO 42010 对应 |
| Architecture Patterns, Styles and Reference Architectures | [06-软件架构理论体系/01-架构模式理论](../06-软件架构理论体系/01-架构模式理论.md)、[06-软件架构理论体系/02-ISO42024架构基础标准对齐](../06-软件架构理论体系/02-ISO42024架构基础标准对齐.md)、[07-分布式与微服务/04-软件架构理论体系/01a-设计模式详解](../07-分布式与微服务/04-软件架构理论体系/01a-设计模式详解.md) | 已覆盖 | 参考架构见 DIS 42042 |
| Architecture Description Languages and Architecture Frameworks | [06-形式模型理论体系](../06-形式模型理论体系/00-形式模型理论体系总论.md)（形式化建模）、[03-形式语言理论体系](../03-形式语言理论体系/00-形式语言理论统一总论.md)、[06-软件架构理论体系](../06-软件架构理论体系/)（形式化描述） | 部分覆盖 | ADL 可后续补充专门小节 |
| Architecture as Significant Decisions | [06-软件架构理论体系/00-软件架构理论体系总论-整合版](../06-软件架构理论体系/00-软件架构理论体系总论-整合版.md)（架构决策）、[07-分布式与微服务/04-软件架构理论体系](../07-分布式与微服务/04-软件架构理论体系/) | 已覆盖 | 与 42010 架构决策对应 |

## 3. Software Architecture Process

| SWEBOK 条款/主题 | 本仓库对应文档/小节 | 状态 | 备注 |
|------------------|---------------------|------|------|
| Architecture in Context (relation to Design) | [06-软件架构理论体系](../06-软件架构理论体系/00-软件架构理论体系总论-整合版.md)、[07-分布式与微服务/04-软件架构理论体系](../07-分布式与微服务/04-软件架构理论体系/README.md)（架构与设计模式关系） | 已覆盖 | 设计模式详解区分架构模式 vs 设计模式 |
| Architectural Design (Analysis, Synthesis, Evaluation) | [07-分布式与微服务/04-软件架构理论体系/07-架构评估与工作流理论](../07-分布式与微服务/04-软件架构理论体系/07-架构评估与工作流理论.md)、[10-统一架构质量系统理论](../07-分布式与微服务/04-软件架构理论体系/10-统一架构质量系统理论.md) | 已覆盖 | 分析与评估有专门文档 |
| Architecture Practices, Methods, and Tactics | [06-软件架构理论体系](../06-软件架构理论体系/)、[Modern/02-语义驱动架构理论](../../Modern/02-语义驱动架构理论/)、[05-实施理论](../../Modern/05-语义驱动架构实施理论/) | 部分覆盖 | 战术/方法以模式与评估为主 |
| Architecting in the Large | [07-分布式与微服务/00-分布式与微服务理论体系总论-整合版](../07-分布式与微服务/00-分布式与微服务理论体系总论-整合版.md)、[06-软件架构理论体系/05-微服务架构理论](../06-软件架构理论体系/05-微服务架构理论.md)、[06-云原生架构理论](../06-软件架构理论体系/06-云原生架构理论.md) | 已覆盖 | 大规模与分布式视角 |

## 4. Software Architecture Evaluation

| SWEBOK 条款/主题 | 本仓库对应文档/小节 | 状态 | 备注 |
|------------------|---------------------|------|------|
| Goodness in Architecture / Quality Attributes | [07-分布式与微服务/04-软件架构理论体系/10-统一架构质量系统理论](../07-分布式与微服务/04-软件架构理论体系/10-统一架构质量系统理论.md)、[06-软件架构理论体系](../06-软件架构理论体系/00-软件架构理论体系总论-整合版.md)（质量属性）、[13-项目报告与总结/00-国际标准对齐-2025版](00-国际标准对齐-2025版.md)（ISO 25010） | 已覆盖 | 质量与可验证性有专门小节 |
| Evaluation Methods and Techniques | [07-分布式与微服务/04-软件架构理论体系/07-架构评估与工作流理论](../07-分布式与微服务/04-软件架构理论体系/07-架构评估与工作流理论.md)、[06-形式模型理论体系/04-模型检查理论](../06-形式模型理论体系/04-模型检查理论.md) | 已覆盖 | 形式化评估见模型检查 |

---

## 5. SWEBOK V4.0a (2025年9月) 更新动态

### 5.1 V4.0a发布信息

**Guide to the Software Engineering Body of Knowledge V4.0a** (2025): *SWEBOK V4.0a*, 已发布, IEEE Computer Society.

- **发布机构**: IEEE Computer Society
- **主编**: Hironori Washizaki (Waseda University, IEEE CS 2025 President)
- **发布日期**: 2025年9月（V4.0的首次修订版）
- **与V4.0的核心差异**: 新增3个知识领域(KA)，总KA数从15扩展至18；Agile和DevOps从附录整合入核心KA

### 5.2 新增3个知识领域详解

| 新增KA | 名称 | 主编 | 核心内容 | 与本项目关联 |
|--------|------|------|----------|-------------|
| **KA 2** | Software Architecture | Rich Hilliard | 架构基础、架构描述、架构过程、架构评估 | 🔴 直接对应本映射表 |
| **KA 6** | Software Engineering Operations | Francis Bordeleau, Alain April | DevOps、SRE、持续交付、可观测性、基础设施即代码 | 🟡 Modern/05-语义驱动架构实施理论部分覆盖 |
| **KA 13** | Software Security | Nobukazu Yoshioka, Seiji Munetoh | 安全开发生命周期、威胁建模、安全测试、密码学应用 | 🟡 Analysis/09-安全模型与可信计算部分覆盖 |

**KA 2 Software Architecture的意义**: 这是"软件架构"首次作为独立知识领域进入SWEBOK。在V3.0中，架构内容分散于Software Design和Software Engineering Models and Methods；V4.0虽有所集中，但仍未独立。V4.0a的升格反映了工业界和学术界对软件架构作为独立学科的认可，也直接提升了本项目（以软件架构为核心）的理论地位。

### 5.3 18个知识领域完整列表与状态

```
╔════╦══════════════════════════════════════════╦════════════╦════════════════════════════╗
║ KA ║ Knowledge Area                           ║ 本项目覆盖  ║ 覆盖模块                    ║
╠════╬══════════════════════════════════════════╬════════════╬════════════════════════════╣
║  1 ║ Software Requirements                    ║ 🟡 部分    ║ Analysis/01-需求工程        ║
║  2 ║ Software Architecture                    ║ 🟢 全面    ║ Analysis/06-, 07-/04-       ║
║  3 ║ Software Design                          ║ 🟢 全面    ║ Analysis/06-设计模式        ║
║  4 ║ Software Construction                    ║ 🟡 部分    ║ Modern/05-实施理论          ║
║  5 ║ Software Testing                         ║ 🟡 部分    ║ Analysis/06-测试策略        ║
║  6 ║ Software Engineering Operations          ║ 🟡 部分    ║ Modern/05-实施/DevOps       ║
║  7 ║ Software Maintenance                     ║ 🟡 部分    ║ Modern/03-可逆计算/演化     ║
║  8 ║ Software Configuration Management        ║ 🟢 全面    ║ Analysis/06-SCM理论         ║
║  9 ║ Software Engineering Management          ║ 🟡 部分    ║ Analysis/06-工程管理        ║
║ 10 ║ Software Engineering Process             ║ 🟢 全面    ║ Modern/05-过程理论          ║
║ 11 ║ Software Engineering Models and Methods  ║ 🟢 全面    ║ Analysis/03-, 06-形式方法   ║
║ 12 ║ Software Quality                         ║ 🟢 全面    ║ Analysis/10-质量系统        ║
║ 13 ║ Software Security                        ║ 🟡 部分    ║ Analysis/09-安全模型        ║
║ 14 ║ Software Engineering Professional Practice║ 🟢 全面   ║ View/伦理与职业规范         ║
║ 15 ║ Software Engineering Economics           ║ 🟡 部分    ║ Analysis/08-成本模型        ║
║ 16 ║ Computing Foundations                    ║ 🟢 全面    ║ Analysis/01-计算理论        ║
║ 17 ║ Mathematical Foundations                 ║ 🟢 全面    ║ Analysis/02-数学理论        ║
║ 18 ║ Engineering Foundations                  ║ 🟢 全面    ║ Analysis/01-工程基础        ║
╚════╩══════════════════════════════════════════╩════════════╩════════════════════════════╝
                        🟢 全面=≥80%  🟡 部分=30-80%  🔴 待建=<30%
```

### 5.4 SWEBOK V4 KA ↔ 本项目模块 ASCII 映射表

```
SWEBOK V4.0a KA                    ↔    本项目核心模块
═══════════════════════════════════════════════════════════════════════
KA 1 Software Requirements         →   Analysis/01-哲学基础理论
                                        Analysis/01-知识体系/需求工程
───────────────────────────────────────────────────────────────────────
KA 2 Software Architecture         →   Analysis/06-软件架构理论体系  [主入口]
                                        Analysis/07-分布式与微服务/04-软件架构理论体系
                                        Modern/02-语义驱动架构理论
                                        Modern/03-业务语义与技术实现同构理论
───────────────────────────────────────────────────────────────────────
KA 3 Software Design               →   Analysis/06-软件架构理论体系/01-架构模式理论
                                        Analysis/07-分布式与微服务/04-设计模式详解
───────────────────────────────────────────────────────────────────────
KA 4 Software Construction         →   Modern/05-语义驱动架构实施理论
                                        Modern/03-可逆计算/代码生成
───────────────────────────────────────────────────────────────────────
KA 5 Software Testing              →   Analysis/06-软件架构理论体系/测试策略
                                        Analysis/06-形式模型理论体系/模型检查
───────────────────────────────────────────────────────────────────────
KA 6 Software Engineering Ops      →   Modern/05-语义驱动架构实施理论/DevOps
                                        Modern/06-虚拟化与语义架构融合理论
───────────────────────────────────────────────────────────────────────
KA 7 Software Maintenance          →   Modern/03-可逆计算/演化与重构
                                        Analysis/06-软件架构理论体系/架构演化
───────────────────────────────────────────────────────────────────────
KA 8 Software Configuration Mgmt   →   Analysis/06-软件架构理论体系/SCM
                                        Modern/05-实施理论/版本治理
───────────────────────────────────────────────────────────────────────
KA 9 Software Engineering Mgmt     →   Analysis/06-软件架构理论体系/工程管理
                                        Analysis/08-性能量化与容量规划模型
───────────────────────────────────────────────────────────────────────
KA 10 Software Engineering Process  →   Modern/05-语义驱动架构实施理论/过程框架
                                        Analysis/06-软件架构理论体系/过程模型
───────────────────────────────────────────────────────────────────────
KA 11 Software Eng Models & Methods →   Analysis/03-形式语言理论体系
                                        Analysis/06-形式模型理论体系
                                        Analysis/07-形式化方法与验证体系
───────────────────────────────────────────────────────────────────────
KA 12 Software Quality             →   Analysis/10-统一架构质量系统理论
                                        Analysis/04-形式模型理论体系/质量属性
───────────────────────────────────────────────────────────────────────
KA 13 Software Security            →   Analysis/09-安全模型与可信计算
                                        Modern/02-语义驱动架构理论/语义安全
───────────────────────────────────────────────────────────────────────
KA 14 Professional Practice        →   View/00-05 (职业伦理与系统思维)
                                        Analysis/00-总览与导航/工程伦理
───────────────────────────────────────────────────────────────────────
KA 15 Software Engineering Economics →   Analysis/08-性能量化与容量规划模型
                                        Analysis/06-软件架构理论体系/成本分析
───────────────────────────────────────────────────────────────────────
KA 16 Computing Foundations         →   Analysis/01-形式化计算理论根基
                                        Struct/01-形式化计算理论根基
───────────────────────────────────────────────────────────────────────
KA 17 Mathematical Foundations      →   Analysis/02-数学理论体系
                                        Struct/00-元认知与系统思维框架
───────────────────────────────────────────────────────────────────────
KA 18 Engineering Foundations       →   Analysis/01-哲学基础理论/系统论
                                        Struct/00-元认知与系统思维框架
═══════════════════════════════════════════════════════════════════════
```

### 5.5 SWEBOK Summit 2026 前瞻

**SWEBOK Summit 2026**将于ICSE 2026期间举办，以下议题与本项目直接相关：

| 议题 | 与本项目关联 | 跟踪建议 |
|------|-------------|----------|
| 量子软件工程 (Quantum SE) | Analysis/02-数学理论体系/量子计算基础 | 低优先级跟踪 |
| LLM支持的安全术语协调 | Modern/02-语义驱动架构理论/语义安全 | 中优先级跟踪 |
| AI工程化知识体系 (AI/ML Engineering KA) | Modern/07-AI增强语义架构理论 | **高优先级跟踪** |

若SWEBOK V5.0采纳"AI Engineering"或"Machine Learning Engineering"作为独立KA，本项目的Modern/07-AI增强语义架构理论模块将成为直接对标对象，需提前准备知识映射。

### 5.6 批判性分析

#### SWEBOK V4.0a的局限与不确定性

1. **KA 2 Software Architecture的"迟到"**: 架构作为独立KA直到2025年才正式确立，相较于IEEE 1471(2000)、ISO 42010(2011/2022)等架构标准的发布晚了10-15年。这导致V4.0a的KA 2在内容深度上尚不及专门的架构标准（如42010的视图-视点机制、42020的过程模型），更多是"知识汇编"而非"方法论创新"。

2. **新增KA的边界模糊**: KA 6 (Software Engineering Operations)与KA 9 (Software Engineering Management)、KA 10 (Software Engineering Process)之间存在显著内容重叠。DevOps/SRE实践既涉及运维工程（KA 6），也涉及项目管理（KA 9）和过程改进（KA 10），SWEBOK未提供清晰的内容划分原则。

3. **形式化方法的持续边缘化**: 尽管本项目将形式化方法视为核心，但在SWEBOK V4.0a中，形式化方法仍主要散布于KA 11 (Models and Methods)和KA 17 (Mathematical Foundations)中，未获得与其实际工程价值相称的独立地位。

#### 与工业实践和本项目理论的差距

1. **语义驱动架构的缺位**: SWEBOK V4.0a的KA 2 Software Architecture延续了传统"组件-连接器"视角和"视图-视点"描述框架，未涉及语义建模、业务-技术同构、语义健康度等前沿概念。本项目的MSMFIT/SMDD理论体系在SWEBOK中尚无直接对应，属于"标准空白区的先行探索"。

2. **可逆计算的完全缺失**: 作为本项目的核心理论贡献之一，可逆计算（双向转换、DSL↔代码、模型↔实现）在SWEBOK全部18个KA中均未涉及。这反映了标准知识体系对"可逆工程"和"双向映射"范式的认知滞后。

3. **AI架构特殊性响应不足**: 虽然V4.0a在多个KA中提及Machine Learning和AI，但未将AI系统架构的特殊性（模型-数据-管道三元结构、LLM Agent编排、RAG架构、提示工程架构等）作为独立主题处理。这与工业界AI工程实践的快速发展形成鲜明对比。

4. **架构评估的形式化缺口**: KA 2中关于Architecture Evaluation的内容主要涵盖ATAM、SAAM等定性评估方法，对模型检查、定理证明、类型系统验证等形式化评估方法着墨甚少，与ISO 42030和本项目的形式化验证体系存在深度差距。

## 汇总与后续

- **已覆盖**：上述多数条款已在本仓库 06-软件架构理论体系、07-分布式/04-软件架构、形式模型与质量/评估文档中对应。
- **部分覆盖**：ADL 与架构框架、部分"Practices/Methods/Tactics"可后续增补小节或链接到 Modern 实施/方法文档。
- **新增覆盖（V4.0a）**: KA 6 Software Engineering Operations、KA 13 Software Security需在本项目中建立更系统的对应文档。
- **不覆盖**：无；KA 2 范围内无明确"不覆盖"项。
- **复审**：每季度选 1–2 条核对文档是否仍为最新路径；SWEBOK 版本更新时同步本表结构；重点跟踪SWEBOK Summit 2026关于AI Engineering KA的讨论。

**文档版本**：v1.1
**创建日期**：2025-02-10
**最后更新**：2026-05-13
**建议复审**：每季度
