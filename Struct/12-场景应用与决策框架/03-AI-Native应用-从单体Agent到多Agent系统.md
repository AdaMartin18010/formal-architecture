# AI-Native应用：从单体Agent到多Agent系统

> **定位**：AI-Native不是"加个AI功能"，而是"AI作为系统核心"——从单体大模型到多Agent协作，AI正在重新定义应用架构。
>
> **核心命题**：多Agent系统的核心挑战不是"让AI更聪明"，而是"让多个AI有效协作"——这与分布式系统中多节点协作的挑战惊人地相似。

---

## 一、思维导图：AI-Native应用架构演进

```text
AI-Native应用架构
│
├─【单体Agent】
│   ├─ 单一大模型（GPT-4, Claude）
│   ├─ ReAct模式（推理+行动循环）
│   ├─ 工具调用（Function Calling）
│   └─ 局限：上下文窗口、单点瓶颈
│
├─【RAG增强】
│   ├─ 向量数据库（Pinecone, Milvus）
│   ├─ 嵌入模型（Embedding）
│   ├─ 检索+生成管道
│   └─ 局限：检索质量、幻觉仍然存在
│
├─【多Agent系统】
│   ├─ 角色分工（Planner, Coder, Reviewer）
│   ├─ 通信协议（Agent间消息传递）
│   ├─ 协调模式（Orchestration vs Choreography）
│   └─ 共享状态（黑板、消息队列）
│
└─【MLOps集成】
    ├─ 模型版本管理
    ├─ A/B测试
    ├─ 监控与反馈循环
    └─ 持续训练（CT）
```

---

## 二、单体Agent架构

```
ReAct模式（Reasoning + Acting）：

  Agent循环：
    1. Thought: LLM推理当前状态和下一步
    2. Action: 调用工具（搜索、代码执行、API）
    3. Observation: 获取工具返回结果
    4. 重复直到任务完成

  示例：
    User: "查询北京明天天气并发送到我的邮箱"

    Thought: 需要1)查询天气 2)发送邮件
    Action: search_weather(city="北京", date="明天")
    Observation: {"temp": "15-25°C", "condition": "晴"}

    Thought: 已获得天气，下一步发送邮件
    Action: send_email(to="user@example.com", body="北京明天天气...")
    Observation: {"status": "sent"}

    Thought: 任务完成
    Final Answer: 邮件已发送

工具调用协议：
  OpenAI Function Calling:
    - 定义工具schema（JSON Schema）
    - LLM生成函数调用参数
    - 应用执行函数并返回结果
```

---

## 三、多Agent系统：分布式AI

```
多Agent系统的核心问题映射到分布式系统：

┌─────────────────────────┬────────────────────────────┐
│ 分布式系统               │ 多Agent系统                 │
├─────────────────────────┼────────────────────────────┤
│ 节点通信                 │ Agent间消息传递             │
│ 共识算法                 │ Agent决策一致性             │
│ 负载均衡                 │ 任务分配给最合适的Agent      │
│ 故障恢复                 │ Agent失败时的备用/重试       │
│ 状态同步                 │ 共享上下文/黑板              │
│ 一致性与可用性           │ Agent意见冲突时的仲裁        │
└─────────────────────────┴────────────────────────────┘

AutoGPT / MetaGPT模式：
  - 多个Agent角色：产品经理、架构师、工程师、测试
  - 共享工作区（文件系统、消息队列）
  - 迭代协作完成任务

  挑战：
    - 循环依赖（Agent A等B，B等A）
    - 意见冲突（不同Agent给出矛盾建议）
    - 上下文爆炸（多轮对话后信息过载）
```

---

## 四、RAG架构深度解析

```
RAG（Retrieval-Augmented Generation）管道：

  离线阶段（索引）：
    Documents → Chunking → Embedding → Vector DB

    Chunking策略：
      - 固定大小（如512 tokens）
      - 语义分块（按段落/主题）
      - 重叠窗口（避免边界信息丢失）

    Embedding模型选择：
      - text-embedding-3-large（OpenAI）
      - E5, BGE（开源）
      - 领域微调（法律、医疗）

  在线阶段（查询）：
    Query → Embedding → Similarity Search → Top-K Chunks
    → Prompt Engineering（Query + Chunks → Context）
    → LLM Generate

  高级优化：
    - 重排序（Reranking）：Cross-encoder精排Top-K
    - 查询改写（Query Expansion）：扩展同义词
    - 混合检索：向量 + 关键词（BM25）
    - 元数据过滤：按时间、来源预过滤
```

---

## 五、AI-Native应用的工程挑战

| 挑战 | **分布式系统类比** | **缓解策略** |
|------|------------------|------------|
| **幻觉** | 拜占庭故障 | RAG、多模型投票、人工审核 |
| **延迟** | 网络延迟 | 流式输出、缓存、模型蒸馏 |
| **成本** | 资源成本 | 模型路由（小模型处理简单任务） |
| **一致性** | 最终一致 | 提示工程约束、输出schema |
| **可解释性** | 分布式追踪 | Chain-of-Thought、日志记录 |
| **安全** | 注入攻击 | 输入过滤、输出审核、沙箱 |

---

## 六、概念定义与属性关系

| 概念 | 定义 | 属性 | 示例 | 反例 |
|------|------|------|------|------|
| **AI-Native** | 以AI为核心能力而非附加功能的应用 | 智能优先、动态生成、上下文感知 | ChatGPT, Claude | 传统应用+Chatbot |
| **RAG** | 检索增强生成，结合外部知识库 | 减少幻觉、可更新知识、可溯源 | 企业知识库问答 | 纯参数化LLM |
| **Agent** | 可感知环境、推理、行动的自主实体 | 目标驱动、可工具调用、可协作 | AutoGPT | 单次LLM调用 |
| **多Agent** | 多个Agent协作完成复杂任务 | 分布式、角色分工、通信协议 | MetaGPT | 单体Agent |
| **Embedding** | 文本到向量空间的映射 | 语义相似性、可检索 | text-embedding-3 | One-hot编码 |

---

## 七、交叉引用

- → [12-总览](../00-总览-模型到现实问题的映射方法论.md)
- → [10/01-AI本体论](../../10-AI时代的软件工程本体论/01-AI生成代码的范式冲击-构造性证明到归纳验证.md)
- → [10/03-AI辅助架构](../../10-AI时代的软件工程本体论/03-AI辅助架构设计-LLM作为架构师的协作者.md)
- → [05/03-EDA](../05-架构模式与部署单元光谱/03-事件驱动架构-解耦与一致性的设计哲学.md)
- ↓ [03/03-PBFT](../../03-分布式共识算法完整谱系/03-PBFT与BFT家族-拜占庭容错共识.md)

---

## 七、参考文献

| 作者 | 标题 | 出处 | 年份 |
|------|------|------|------|
| Yao et al. | "A Survey on Large Language Model based Autonomous Agents" | *arXiv* | 2023 |
| Lewis et al. | "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" | *NeurIPS* | 2020 |
| Hong et al. | "MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework" | *arXiv* | 2023 |
| OpenAI | "Function Calling" docs | openai.com | 持续更新 |

---

*文件创建日期：2026-04-23*
*状态：已完成*
