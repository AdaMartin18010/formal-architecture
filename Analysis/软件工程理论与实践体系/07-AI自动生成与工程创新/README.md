# 07-AI自动生成与工程创新

## 概述

本主题探讨人工智能（AI），特别是大型语言模型（LLM），在现代软件工程中扮演的变革性角色。内容从AI作为新型抽象层的概念性讨论出发，涵盖了主流生成模型（GANs, VAEs, Transformers）的原理，并深入分析了AI在生成代码、辅助工程实践（如测试、文档、编译优化）等方面的应用、潜力与局限性。

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
