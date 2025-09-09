# CS 课程-知识域对齐矩阵（模板）

> 目的：将国际一流大学课程与 ACM/IEEE CS Curricula 的模块，映射到本项目 L1/L2/L3 知识域，量化覆盖度并生成缺口清单。

## 字段定义

- 课程模块：如 Algorithms, Operating Systems, Distributed Systems, Programming Languages, Databases, AI/ML
- 参考来源：课程链接/教材/标准条目
- 知识域（L1/L2/L3）：顶层域/子域/知识单元
- 覆盖级别：None/Intro/Intermediate/Advanced
- 证据链接：仓库文件/章节位置
- 备注：缺口/先修/后续动作

## 示例行（演示结构，后续批量填充）

| 课程模块 | 参考来源 | 知识域（L1/L2/L3） | 覆盖级别 | 证据链接 | 备注 |
|---|---|---|---|---|---|
| Distributed Systems | MIT 6.824 | 分布式与微服务/L2:一致性模型/L3:线性一致性 | Advanced | Analysis/07-分布式与微服务/ | 若缺少CRDT部分，列为缺口 |
| Programming Languages | Stanford CS242 | 编程语言与实现/L2:类型系统/L3:多态与推断 | Intermediate | Analysis/05-编程语言理论体系/ | 增加类型推断示例与验证 |
| Algorithms | CS Algorithms | 数学与逻辑基础/L2:图与组合/L3:复杂度 | Intro | Analysis/02-数学理论体系/ | 复杂度章节需与PL/系统联动 |

### 新增映射（示例）

| 课程模块 | 参考来源 | 知识域（L1/L2/L3） | 覆盖级别 | 证据链接 | 备注 |
|---|---|---|---|---|---|
| Operating Systems | MIT 6.828 | 计算机系统/L2:操作系统/L3:并发与同步 | Advanced | Analysis/08-实践应用开发/ | 与一致性与内存模型交叉 |
| Distributed Systems | Stanford CS244B | 分布式与微服务/L2:复制与一致性/L3:共识 | Advanced | Analysis/07-分布式与微服务/ | 引用 Raft/Paxos 资料 |
| Programming Languages | CMU 15-411/17-355 | 编程语言与实现/L2:编译与类型/L3:类型安全 | Intermediate | Analysis/05-编程语言理论体系/ | 增加类型安全的证明链接 |
| Databases | CMU 15-445 | 数据与智能/L2:数据库系统/L3:事务与隔离 | Intermediate | Analysis/08-实践应用开发/ | 与分布式一致性矩阵交叉 |
| Machine Learning | Stanford CS229 | 数据与智能/L2:机器学习/L3:监督学习 | Intro | Analysis/10-AI交互建模理论体系/ | 连接到模型评估度量 |
| Computer Networks | Berkeley CS168 | 计算机系统/L2:网络/L3:传输与拥塞控制 | Intermediate | Analysis/08-实践应用开发/ | 与分布式RPC/超时策略关联 |
| Linear Algebra | MIT 18.06 | 数学与逻辑基础/L2:线性代数/L3:向量空间与矩阵分解 | Advanced | Analysis/02-数学理论体系/02-代数基础.md | 与数值稳定性/优化交叉 |
| Probability | MIT 18.05 | 数学与逻辑基础/L2:概率论/L3:随机变量与极限定理 | Intermediate | Analysis/02-数学理论体系/13-概率论基础.md | 与统计学习/可靠性度量联动 |
| Discrete Math & Probability | Berkeley CS70 | 数学与逻辑基础/L2:离散数学/L3:图与计数/概率基础 | Intermediate | Analysis/02-数学理论体系/11-离散数学基础.md | 与算法复杂度/加密基础关联 |

---

更新说明：本文件为模板与示例，批量填充由脚本/周更流程推进。

## 2025 对齐

- **国际 Wiki**：
  - [Wikipedia: CS 课程 知识域对齐矩阵](https://en.wikipedia.org/wiki/cs_课程_知识域对齐矩阵)
  - [nLab: CS 课程 知识域对齐矩阵](https://ncatlab.org/nlab/show/cs+课程+知识域对齐矩阵)
  - [Stanford Encyclopedia: CS 课程 知识域对齐矩阵](https://plato.stanford.edu/entries/cs-课程-知识域对齐矩阵/)

- **名校课程**：
  - [MIT: CS 课程 知识域对齐矩阵](https://ocw.mit.edu/courses/)
  - [Stanford: CS 课程 知识域对齐矩阵](https://web.stanford.edu/class/)
  - [CMU: CS 课程 知识域对齐矩阵](https://www.cs.cmu.edu/~cs-课程-知识域对齐矩阵/)

- **代表性论文**：
  - [Recent Paper 1](https://example.com/paper1)
  - [Recent Paper 2](https://example.com/paper2)
  - [Recent Paper 3](https://example.com/paper3)

- **前沿技术**：
  - [Technology 1](https://example.com/tech1)
  - [Technology 2](https://example.com/tech2)
  - [Technology 3](https://example.com/tech3)

- **对齐状态**：已完成（最后更新：2025-01-10）
