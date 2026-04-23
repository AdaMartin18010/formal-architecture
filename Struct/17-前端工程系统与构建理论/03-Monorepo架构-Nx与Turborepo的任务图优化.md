# Monorepo 架构：Nx 与 Turborepo 的任务图优化

> **来源映射**: View/05.md §8.1
> **国际权威参考**: Turborepo Docs (Vercel), Nx Docs (Nrwl), "Monorepo Patterns" (Google Engineering Practices), "Bazel: Build in the Cloud" (Google), "Rush Stack" (Microsoft), Lerna Archive

---

## 一、知识体系思维导图

```text
Monorepo 架构与任务图优化
│
├─► Monorepo 核心概念
│   ├─ 工作区 (Workspace): 多个包共享单一仓库
│   ├─ 内部依赖图: workspace:* 协议 ⟺ 语义版本控制
│   ├─ 任务图 (Task Graph): 构建/测试/类型检查的有向依赖
│   └─ 变更传播: 仅执行受变更影响 (affected) 的任务
│
├─► Turborepo 架构
│   ├─ Pipeline: turbo.json 定义任务依赖图
│   ├─ 本地缓存: 文件系统哈希缓存
│   ├─ 远程缓存: Vercel Remote Cache / 自建缓存服务器
│   ├─ 任务签名: 输入文件哈希 + 环境变量 + 依赖版本
│   └─ 并行执行: 拓扑排序后的任务并行化
│
├─► Nx 架构
│   ├─ 项目图 (Project Graph): 包间依赖关系
│   ├─ 任务图 (Task Graph): 任务间的 DAG
│   ├─ 计算缓存: 本地 + 分布式缓存 (Nx Cloud)
│   ├─ 分布式任务执行 (DTE): CI 中的并行分发
│   ├─ 代码生成器 (Generators): 脚手架与一致性约束
│   └─ 插件生态: 官方插件覆盖主流技术栈
│
├─► 形式化对比
│   ├─ 缓存策略: 文件哈希 vs 输入签名
│   ├─ 任务调度: 贪心并行 vs 分布式编排
│   ├─ 变更检测: git diff vs Nx affected 算法
│   └─ 扩展模型: 配置驱动 vs 插件驱动
│
└─► 工程实践
    ├─ 任务依赖声明的完备性
    ├─ 缓存失效的调试策略
    └─ CI/CD 集成与远程缓存安全
```

---

## 二、核心概念的形式化定义

### 2.1 Monorepo 工作区模型

```text
定义 (Monorepo 工作区 𝓦):
  𝓦 = ⟨P, D, T, C⟩
  
  P = {p₁, p₂, ..., pₙ}: 包集合
  D ⊆ P × P: 包间内部依赖关系
  T = {t₁, t₂, ..., tₘ}: 任务类型集合 (build/test/lint/typecheck)
  C: 缓存函数，将任务执行映射到产物哈希

  工作区依赖图:
    G_pkg = (P, D) 是有向图
    要求: G_pkg 无环 (DAG)，否则存在循环内部依赖

  任务图:
    对于任务类型 τ ∈ T，任务图 G_τ = (V_τ, E_τ)
    V_τ = {(p, τ) | p ∈ P}: 包-任务节点
    E_τ = {((pᵢ, τ), (pⱼ, τ)) | (pⱼ, pᵢ) ∈ D}: 任务依赖边
      (若 pⱼ 依赖 pᵢ，则 pⱼ 的 τ 任务依赖 pᵢ 的 τ 任务)
```

### 2.2 任务缓存的形式化

```text
定义 (任务缓存):
  对于任务节点 v = (p, τ)，其缓存键定义为:
    Key(v) = Hash(Inputs(p, τ), Deps(p), Env(τ))
    
    Inputs(p, τ): 任务 τ 在包 p 上的输入文件集合
    Deps(p): 包 p 的所有依赖的版本哈希
    Env(τ): 任务相关的环境变量

  缓存查找:
    若 Cache[Key(v)] 存在，则跳过执行，直接复用产物
    否则执行任务，并将产物存入 Cache[Key(v)]

  缓存命中率:
    HitRate = |{v | Cache[Key(v)] exists}| / |V_τ|
    理想情况下，未变更包的任务命中率为 100%
```

### 2.3 增量构建的变更传播

```text
定义 (Affected 集合):
  设变更包集合 ΔP ⊆ P (由 git diff 确定)
  
  Affected(ΔP) = ΔP ∪ {p ∈ P | ∃q ∈ ΔP, q →* p}
  即所有直接变更包及其下游依赖包

  需执行任务集合:
    Tasks_to_run = {(p, τ) | p ∈ Affected(ΔP), τ ∈ T}
    
  拓扑排序后并行执行:
    按 G_τ 的拓扑序调度任务，无依赖关系的任务并行执行
```

---

## 三、多维矩阵对比

| 维度 | Turborepo | Nx | Bazel | Rush | Lerna |
|------|-----------|-----|-------|------|-------|
| **开发公司** | Vercel | Nrwl | Google | Microsoft | 社区 (已归档) |
| **配置方式** | turbo.json | project.json / nx.json | BUILD/WORKSPACE | rush.json | lerna.json |
| **任务图定义** | Pipeline (显式) | 自动推断 + 显式 | Starlark 规则 | Command 定义 | 无原生支持 |
| **本地缓存** | ✅ 文件系统 | ✅ 本地 + SQLite | ✅ 复杂缓存 | ✅ | ❌ |
| **远程缓存** | ✅ Vercel / 自建 | ✅ Nx Cloud | ✅ Bazel Remote | ⚠️ 有限 | ❌ |
| **分布式执行** | ❌ | ✅ DTE (Nx Cloud) | ✅ 原生 | ❌ | ❌ |
| **变更检测** | git diff | affected 图算法 | 文件级精确追踪 | git diff | git diff |
| **代码生成** | ❌ | ✅ Generators | ❌ | ❌ | ❌ |
| **插件生态** | 小 | **大** (官方覆盖全栈) | 大 | 中 | 小 |
| **学习曲线** | 低 | 中 | 高 | 中 | 低 |
| **适用规模** | 中小规模 | 中小到超大规模 | 超大规模 | 大规模 | 小规模 |

---

## 四、权威引用

> **Jared Palmer** (Turborepo 创始人, 2021):
> "Turborepo is a build system that uses a directed acyclic graph (DAG) to schedule tasks. It caches the results of tasks so that you never have to do the same work twice."

> **Victor Savkin** (Nx 创始人, Nrwl, 2022):
> "Nx is not just a build tool. It's a set of dev tools for monorepos, including task scheduling, caching, code generation, and distributed execution."

> **Google Engineering Practices** ("Monorepo Patterns", 2020):
> "At Google, we use a monorepo because it simplifies dependency management and enables large-scale refactoring across the entire codebase. The trade-off is that you need a sophisticated build system like Bazel to handle the scale."

> **Vercel** (Turborepo 文档, 2023):
> "Remote Caching shares your local cache across your entire team and CI/CD pipelines. It can save hours of compute time per day in large monorepos."

---

## 五、工程实践与代码示例

### 5.1 Turborepo Pipeline 配置

```json
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**", "dist/**"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"]
    },
    "lint": {
      "dependsOn": ["^build"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
```

### 5.2 Nx Project 配置

```json
// packages/ui/project.json
{
  "name": "ui",
  "sourceRoot": "packages/ui/src",
  "targets": {
    "build": {
      "executor": "@nx/vite:build",
      "outputs": ["{options.outputPath}"],
      "dependsOn": ["^build"],
      "options": {
        "outputPath": "dist/packages/ui"
      }
    },
    "test": {
      "executor": "@nx/vite:test",
      "dependsOn": ["build"],
      "outputs": ["{workspaceRoot}/coverage/{projectName}"]
    }
  }
}
```

### 5.3 远程缓存安全设置

```bash
# Turborepo 远程缓存签名验证
export TURBO_REMOTE_CACHE_SIGNATURE_KEY=$(openssl rand -base64 32)

# Nx Cloud 访问令牌 (只读 vs 读写)
npx nx connect-to-nx-cloud
# 在 CI 中设置 NX_CLOUD_ACCESS_TOKEN (只读权限)
```

---

## 六、批判性总结

Monorepo 工具链将图论从**模块依赖级**提升到**任务调度级**，这是前端工程系统形式化的重要进阶。Turborepo 和 Nx 的核心洞察是：构建、测试、Lint 等任务不仅依赖于源代码，还依赖于其他任务的输出——这构成了一个**元层次的依赖图**（Task Graph）。通过拓扑排序和缓存，工具将 O(n) 的全量构建优化为 O(|Affected|) 的增量构建，在大型仓库中可将 CI 时间从小时级压缩到分钟级。

但任务图优化的有效性严重依赖于**任务依赖声明的完备性**。当 `dependsOn` 声明不完整时（例如，测试任务实际上依赖环境变量但未声明），缓存可能返回错误的过期产物，导致**不可重现的构建错误**。这种错误极难调试，因为本地复现时可能因缓存未命中而表现正常。形式化的解决路径是**声明式依赖完整性验证**：工具应自动检测任务输入的完备性，并在依赖声明缺失时发出警告。

Nx 的分布式任务执行（DTE）代表了 Monorepo 工具链的前沿方向。在 CI 环境中，Nx 将任务图分解为子图，分发到多个 Agent 并行执行，通过 Nx Cloud 协调产物同步。这本质上是**任务级 MapReduce**：Map 阶段并行执行任务，Reduce 阶段合并产物。然而，DTE 的网络开销和任务调度延迟使其在小型仓库中反而慢于单机执行——这再次验证了**没有银弹**的定理：优化策略的收益与问题规模正相关，选择工具时必须进行量化的成本-收益分析。
