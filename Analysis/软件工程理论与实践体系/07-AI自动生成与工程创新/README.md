# 07-AI自动生成与工程创新

> **最后更新**: 2025年11月11日
> **状态**: ✅ 持续完善中

## 概述

本主题探讨人工智能（AI），特别是大型语言模型（LLM），在现代软件工程中扮演的变革性角色。内容从AI作为新型抽象层的概念性讨论出发，涵盖了主流生成模型（GANs, VAEs, Transformers）的原理，并深入分析了AI在生成代码、辅助工程实践（如测试、文档、编译优化）等方面的应用、潜力与局限性。

## 目录

- [概述](#概述)
- [内容索引](#内容索引)
  - [AI生成与抽象](#01-ai生成与抽象)
  - [AI辅助工程](#02-ai辅助工程)
- [2025 对齐](#2025-对齐)
- [相关文档](#相关文档)

## 内容索引

### 01-AI生成与抽象

- [AI生成的新颖性与上下文限制](./01-AI生成与抽象/01-AI生成的新颖性与上下文限制.md)
  - *内容：探讨AI生成内容的"新颖性"来源（主要是组合式创新），并深入分析决定其生成质量的关键因素——上下文窗口（Context Window）的大小及其有效利用率。*
- [作为新抽象层的AI](./01-AI生成与抽象/02-作为新抽象层的AI.md)
  - *内容：将AI类比为继汇编、高级语言之后的又一个新的抽象层次，开发者可以通过"意图"而非精确的代码来指导编程，同时分析其带来的机遇与挑战。*
- [生成模型概览(GAN_VAE_Transformer)](./01-AI生成与抽象/03-生成模型概览(GAN_VAE_Transformer).md)
  - *内容：介绍支撑现代AI内容生成的三种核心深度学习模型：生成对抗网络（GANs）、变分自编码器（VAEs）和Transformer。*
- [创造性系统的形式化分析](./01-AI生成与抽象/04-创造性系统的形式化分析.md)
  - *内容：提供一个关于"创造性系统"的Rust风格伪代码实现，形式化地探讨如何结合生成模型和评估模型来探索和优化创意作品。*

### 02-AI辅助工程

- [AI驱动的工具链与基础设施](./02-AI辅助工程/01-AI驱动的工具链与基础设施.md)
  - *内容：展望AI如何深度融入软件开发的全生命周期，包括智能化的IDE、自优化的编译器和运行时、自动化测试以及动态知识库等。*
- [AI代码生成实践案例](./02-AI辅助工程/02-AI代码生成实践案例.md)
  - *内容：提供AI代码生成在实际工程中的应用案例，涵盖代码补全、测试生成、文档生成、重构建议等多个方面。包含GitHub Copilot、代码测试生成、API文档生成等实践案例。*

---

## 2025 对齐

### 国际 Wiki

- **Wikipedia**: [Artificial intelligence](https://en.wikipedia.org/wiki/Artificial_intelligence)
- **Wikipedia**: [Large language model](https://en.wikipedia.org/wiki/Large_language_model)
- **Wikipedia**: [Generative adversarial network](https://en.wikipedia.org/wiki/Generative_adversarial_network)
- **Wikipedia**: [Transformer (machine learning model)](https://en.wikipedia.org/wiki/Transformer_(machine_learning_model))
- **Wikipedia**: [Code generation](https://en.wikipedia.org/wiki/Code_generation)

### 名校课程

- **MIT**: [6.034 Artificial Intelligence](https://ocw.mit.edu/courses/6-034-artificial-intelligence-fall-2010/)
- **Stanford**: [CS224N: Natural Language Processing with Deep Learning](https://web.stanford.edu/class/cs224n/)
- **CMU**: [11-785 Introduction to Deep Learning](https://deeplearning.cs.cmu.edu/)
- **Berkeley**: [CS 188 Introduction to Artificial Intelligence](https://inst.eecs.berkeley.edu/~cs188/)

### 代表性论文

- **生成模型**：
  - [Generative Adversarial Networks](https://arxiv.org/abs/1406.2661) - GANs
  - [Auto-Encoding Variational Bayes](https://arxiv.org/abs/1312.6114) - VAEs
  - [Attention Is All You Need](https://arxiv.org/abs/1706.03762) - Transformer

- **AI代码生成**：
  - [CodeBERT: A Pre-Trained Model for Programming and Natural Languages](https://arxiv.org/abs/2002.08155)
  - [GitHub Copilot: Your AI Pair Programmer](https://github.com/features/copilot)
  - [Codex: Evaluating Large Language Models Trained on Code](https://arxiv.org/abs/2107.03374)

- **AI辅助工程**：
  - [The Future of Programming](https://www.youtube.com/watch?v=ecIWPzGEbFc)
  - [AI-Powered Development Tools](https://www.oreilly.com/library/view/ai-powered-development/9781492083451/)

### 前沿技术

- **AI代码生成工具**：
  - [GitHub Copilot](https://github.com/features/copilot)
  - [Tabnine](https://www.tabnine.com/)
  - [Codeium](https://codeium.com/)
  - [Amazon CodeWhisperer](https://aws.amazon.com/codewhisperer/)

- **大型语言模型**：
  - [OpenAI GPT](https://openai.com/)
  - [Anthropic Claude](https://www.anthropic.com/)
  - [Google PaLM](https://ai.googleblog.com/2022/04/pathways-language-model-palm-scaling-to.html)
  - [Meta LLaMA](https://ai.meta.com/llama/)

- **AI开发工具**：
  - [Cursor](https://cursor.sh/)
  - [v0](https://v0.dev/)
  - [Replit](https://replit.com/)

### 对齐状态

- **标准对齐**: ✅ 已对齐ISO/IEC/IEEE/ACM 2025年标准
- **内容完整性**: ✅ 核心内容已完善，持续补充中
- **实践案例**: ✅ 核心案例已完善（代码补全、测试生成、文档生成、重构建议）
- **最后更新**: 2025年11月11日

---

## 相关文档

- [软件工程理论与实践体系总论](../00-体系总论.md)
- [进度追踪与上下文](../进度追踪与上下文.md)
- [2025年11月标准对齐全面梳理报告](../2025年11月标准对齐全面梳理报告.md)
- [形式化架构理论统一计划-2025标准对齐版](../../../00-形式化架构理论统一计划-2025标准对齐版.md)
