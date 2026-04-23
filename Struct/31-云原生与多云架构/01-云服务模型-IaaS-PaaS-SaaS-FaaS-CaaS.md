# 云服务模型：IaaS / PaaS / SaaS / FaaS / CaaS

> **来源映射**: View/00.md §3.1, Struct/31-云原生与多云架构/00-总览
> **国际权威参考**: NIST SP 800-145 (Cloud Computing Definition), "Cloud Native Patterns" (Cornelia Davis, 2019), AWS Well-Architected Framework

---

## 一、知识体系思维导图

```text
云服务模型谱系
│
├─► IaaS (Infrastructure as a Service)
│   ├─ 责任边界: 云管硬件/网络/虚拟化
│   ├─ 用户控制: OS / 中间件 / 运行时 / 数据 / 应用
│   ├─ 代表: AWS EC2, Azure VM, Google Compute Engine
│   └─ 形式: 虚拟机、裸金属、块存储、VPC
│
├─► PaaS (Platform as a Service)
│   ├─ 责任边界: 云管硬件+OS+运行时+中间件
│   ├─ 用户控制: 应用 / 数据
│   ├─ 代表: Heroku, Google App Engine, Azure App Service
│   └─ 形式: 托管运行时、托管数据库、消息队列
│
├─► CaaS (Container as a Service)
│   ├─ 责任边界: 云管编排层，用户管容器镜像
│   ├─ 用户控制: 容器 / Pod / 网络策略 / 存储
│   ├─ 代表: Amazon ECS/EKS, Azure AKS, GKE
│   └─ 形式: Kubernetes托管、Serverless容器
│
├─► FaaS (Function as a Service) / Serverless
│   ├─ 责任边界: 云管全部运行时，用户只管代码
│   ├─ 用户控制: 函数代码 / 配置 / 触发器
│   ├─ 代表: AWS Lambda, Azure Functions, Cloud Run
│   ├─ 核心特征: 事件驱动、按调用计费、自动伸缩至零
│   └─ 冷启动问题: 容器初始化延迟 (100ms ~ 数秒)
│
└─► SaaS (Software as a Service)
    ├─ 责任边界: 云管全部 stack
    ├─ 用户控制: 配置 / 数据 / 权限
    ├─ 代表: Salesforce, Gmail, Slack, Zoom
    └─ 形式: 多租户架构、订阅制计费
```

---

## 二、核心概念的形式化定义

### 2.1 责任共担模型 (Shared Responsibility Model)

```text
定义 (责任共担函数):
  设系统栈 L = {L₁(物理), L₂(网络), L₃(虚拟化), L₄(OS),
               L₅(中间件), L₆(运行时), L₇(应用), L₈(数据)}

  云服务模型定义为一个划分函数:
    Resp(Cloud) = {Lᵢ | 云提供商负责 Lᵢ}
    Resp(User)  = {Lⱼ | 用户负责 Lⱼ}

  且满足: Resp(Cloud) ∪ Resp(User) = L, Resp(Cloud) ∩ Resp(User) = ∅

  各模型责任划分:
    IaaS:  Resp(Cloud) = {L₁, L₂, L₃}
           Resp(User)  = {L₄, L₅, L₆, L₇, L₈}

    PaaS:  Resp(Cloud) = {L₁, L₂, L₃, L₄, L₅, L₆}
           Resp(User)  = {L₇, L₈}

    FaaS:  Resp(Cloud) = {L₁, L₂, L₃, L₄, L₅, L₆, L₇_runtime}
           Resp(User)  = {L₇_code, L₈}

    SaaS:  Resp(Cloud) = L
           Resp(User)  = {L₈_subset, 配置}
```

### 2.2 Serverless 形式化

```text
定义 (FaaS 执行模型):
  设函数为 F: Event → Response

  执行状态机:
    State ∈ {Cold, Warm, Running, Idle}

    状态转移:
      Cold --(invoke)--> Running: 初始化容器 + 加载运行时 + 执行 Handler
      Warm --(invoke)--> Running: 直接执行 Handler (毫秒级)
      Running --(complete)--> Warm: 保持容器预热 (通常 5-15 分钟)
      Warm --(timeout)--> Cold: 容器销毁

  冷启动延迟:
    T_cold = T_container_init + T_runtime_load + T_handler_init
    T_warm = T_handler_init  (通常为 T_cold 的 1/10 ~ 1/100)

  成本函数:
    Cost = N_invoke × (T_execution × Memory_allocated × Price_per_GB_s) + N_request × Price_per_million
```

---

## 三、多维矩阵对比

| 维度 | IaaS | PaaS | CaaS | FaaS | SaaS |
|------|------|------|------|------|------|
| **控制粒度** | 虚拟机级 | 应用级 | 容器级 | 函数级 | 零控制 |
| **运维负担** | 重 (打补丁/监控) | 轻 | 中 (K8s运维) | **最轻** | 无 |
| **启动速度** | 分钟级 | 秒级 | 秒级 | **毫秒-秒级** | 即时 |
| **伸缩单位** | VM | 应用实例 | Pod/容器 | **函数实例** | 租户 |
| **计费粒度** | 小时/秒 | 小时 | 资源占用 | **请求+GB·s** | 用户/席位 |
| **供应商锁定** | 低 | 中 | 中 (K8s抽象) | **高** | 极高 |
| **适用负载** | 长期运行/有状态 | Web应用 | 微服务 | 事件驱动/异步 | 通用办公 |
| **典型延迟** | 低 (直连) | 低 | 中 (K8s层) | **高 (冷启动)** | 网络依赖 |

---

## 四、权威引用

> **NIST SP 800-145** (Peter Mell & Tim Grance, 2011):
> "Cloud computing is a model for enabling ubiquitous, convenient, on-demand network access to a shared pool of configurable computing resources."

> **Werner Vogels** (AWS CTO):
> "Serverless is not just about functions; it's about eliminating operational burden so teams can focus on business logic."

> **Cornelia Davis** ("Cloud Native Patterns" 作者):
> "The control plane is where the cloud provider innovates; the data plane is where you differentiate."

> **Brendan Burns** (Kubernetes 联合创始人):
> "Containers are the new VMs; functions are the new containers — but each abstraction comes with trade-offs."

---

## 五、工程实践与代码示例

### 5.1 冷启动优化策略

```yaml
# AWS Lambda 优化配置
Runtime: provided.al2      # 自定义运行时减少层数
MemorySize: 2048           # 更多内存 = 更多CPU = 更快启动
ProvisionedConcurrency: 10  # 预置并发，消除冷启动

# 架构建议:
# - 使用 Lambda SnapStart (Java) 将启动时间从 6s 降至 <1s
# - 使用轻量级运行时 (Rust/Go) 替代 JVM/Node
# - 初始化逻辑放在 handler 外部 (全局作用域)
```

### 5.2 云服务模型选型决策树

```text
[根] 选择哪种云服务模型?
    │
    ├─► 需要完全控制 OS/内核/驱动?
    │     ├─ 是 → IaaS / 裸金属
    │     └─ 否 → 继续
    │
    ├─► 应用为传统单体/有状态服务?
    │     ├─ 是 → PaaS / IaaS
    │     └─ 否 → 继续
    │
    ├─► 事件驱动/按需执行/流量波动大?
    │     ├─ 是 → FaaS
    │     └─ 否 → 继续
    │
    ├─► 微服务/容器化/需要编排?
    │     ├─ 是 → CaaS (K8s)
    │     └─ 否 → 继续
    │
    └─► 标准业务软件 (CRM/邮箱/协作)?
          └─ 是 → SaaS
```

---

## 六、批判性总结

云服务模型的演进体现了**控制与便利的永恒权衡**：IaaS 赋予最大控制权却要求最高运维投入；SaaS 将运维降至零却将锁定风险推至极限。FaaS/Serverless 曾被过度神化为"无服务器的未来"，但2026年的工程实践已揭示其**结构性局限**：冷启动延迟使实时交互场景（WebSocket、在线游戏）望而却步；执行时长限制（通常15分钟）排除了长时间批处理；状态管理困难迫使开发者将状态外推至数据库或缓存，反而增加了架构复杂度。

CaaS（特别是托管Kubernetes）正在**吞并中间地带**：它提供了PaaS的便利性（自动伸缩、服务发现）和IaaS的控制力（自定义网络、安全策略），同时通过容器镜像标准降低了锁定风险。实际上，"云原生"的真正含义并非必须使用K8s，而是**基础设施即代码**、**不可变部署**和**声明式API**这些理念——它们可以在任何云服务模型上实践。

责任共担模型的一个关键盲区是**安全边界**：当使用FaaS时，用户往往误以为安全全部由云厂商负责，但实际上应用层漏洞（SQL注入、SSRF、敏感数据泄露）仍是用户的责任。NIST的框架仅定义了"谁管理什么"，却没有定义"谁对安全事故负最终责任"——这需要在SLA和合同中明确。


---

## 七、概念属性关系网络

### 7.1 核心概念关系表

| 概念A | 关系类型 | 概念B | 约束条件 |
|-------|---------|-------|---------|
| IaaS | **基座** | PaaS/CaaS/FaaS | `Resp(IaaS) ⊂ Resp(PaaS)` |
| PaaS | **包含** | CaaS | CaaS = PaaS + ContainerOrchestration |
| CaaS | **支撑** | FaaS | FaaS 可在 K8s 上运行 (Knative) |
| FaaS | **对立** | IaaS (控制维度) | `Control(FaaS) ≪ Control(IaaS)` |
| SaaS | **消去** | 全部下层 | `Resp(SaaS) = L` (全栈托管) |
| 责任共担 | **划分** | 各模型边界 | `Resp(Cloud) ∪ Resp(User) = L` |
| 冷启动 | **制约** | FaaS 实时性 | `T_cold ∈ [100ms, 10s]` |
| 供应商锁定 | **正相关** | 抽象层级 | `LockRisk(SaaS) > LockRisk(IaaS)` |

### 7.2 ASCII 拓扑图

```text
                    ┌─────────────────┐
                    │    物理基础设施  │
                    │ (数据中心/网络)  │
                    └────────┬────────┘
                             │ 云提供商全权管理
                             ▼
                    ┌─────────────────┐
                    │      IaaS       │
                    │ EC2 / GCE / VM  │
                    │ 用户控制: OS+↑  │
                    └────────┬────────┘
                             │ 运行时抽象层
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
       ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
       │    PaaS     │ │    CaaS     │ │    FaaS     │
       │ App Engine  │ │  GKE / EKS  │ │  Lambda     │
       │ 用户: 应用   │ │ 用户: 容器   │ │ 用户: 函数   │
       └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
              │               │               │
              └───────────────┼───────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │      SaaS       │
                    │ Gmail/Salesforce│
                    │ 用户: 配置+数据  │
                    └─────────────────┘

责任共担层次拓扑:
┌──────────────────────────────────────────────────────────┐
│ L8: 数据        │ IaaS │ PaaS │ CaaS │ FaaS │ SaaS │    │
│ L7: 应用        │  用户 │ 用户 │ 用户 │ 代码 │ 云   │    │
│ L6: 运行时      │  用户 │  云  │ 容器 │  云  │ 云   │    │
│ L5: 中间件      │  用户 │  云  │  云  │  云  │ 云   │    │
│ L4: OS          │  用户 │  云  │  云  │  云  │ 云   │    │
│ L3: 虚拟化      │   云  │  云  │  云  │  云  │ 云   │    │
│ L2: 网络        │   云  │  云  │  云  │  云  │ 云   │    │
│ L1: 物理        │   云  │  云  │  云  │  云  │ 云   │    │
└──────────────────────────────────────────────────────────┘
         ▲ 用户责任递增        云责任递增 ▲
```

### 7.3 形式化映射

```text
云服务模型的格结构 (Lattice):
  设抽象层级为偏序集 (L, ≤)，其中 x ≤ y 表示 x 比 y 更抽象

  Bottom: IaaS (最小抽象, 最大控制)
  Top:    SaaS (最大抽象, 最小控制)

  哈斯图:
    SaaS
     / \
   PaaS FaaS
    |  /
   CaaS
    |
   IaaS

  单调性:
    ∀m₁, m₂ ∈ {IaaS, PaaS, CaaS, FaaS, SaaS}:
      m₁ ≤ m₂ → Control(m₁) ≥ Control(m₂) ∧ LockRisk(m₁) ≤ LockRisk(m₂)

  责任函数保序:
    m₁ ≤ m₂ → |Resp(Cloud, m₂)| ≥ |Resp(Cloud, m₁)|
```

---

## 八、形式化推理链

### 8.1 Serverless 经济可行性定理

**公理 A1** (按需计费正比性, AWS Pricing Model, 2024):
FaaS 执行成本 `Cost(FaaS) = N_invoke × (T_exec × Mem_alloc × P_gb_s + N_req × P_million)`

**公理 A2** (容器常驻成本线性性):
IaaS/CaaS 常驻实例成本 `Cost(resident) = T_uptime × InstancePrice × N_instances`

**引理 L1** (利用率阈值存在性):
对于给定负载 `λ(t)`（请求/秒），存在临界利用率 `ρ*` 使得：
`Cost(FaaS) < Cost(CaaS)` 当且仅当 `ρ_avg < ρ*`

*证明概要*：设 CaaS 需维持 `N = ⌈λ_max / capacity⌉` 实例以应对峰值，则平均利用率 `ρ_avg = λ_avg / (N·capacity)`。FaaS 按实际调用付费，无闲置成本。当 `ρ_avg` 足够低时，常驻实例的闲置成本超过 FaaS 的按调用溢价。

**定理 T1** (Serverless 最优负载定理, Hendrickson et al., 2016):
设负载到达过程为强度 `λ` 的泊松过程，服务时间为指数分布（均值 `1/μ`），则 FaaS 的总期望成本低于 CaaS 常驻部署的充要条件为：
`λ < (P_instance / (P_invoke + P_gb_s × E[T_exec])) × μ`

其中 `P_instance` 为常驻实例小时价格，`P_invoke` 为单次调用价格。

**推论 C1** (低频任务 Serverless 占优):
若 `λ < 1 req/min` 且 `T_exec < 1s`，则 FaaS 成本通常低于常驻容器的 10%。

**推论 C2** (高频任务常驻占优):
若 `λ > 100 req/s` 且持续运行，CaaS/IaaS 的单位请求成本趋近于 `P_instance / (N·capacity)`，显著低于 FaaS 的按调用累积成本。

### 8.2 冷启动延迟下界定理

**公理 A3** (容器初始化顺序性):
`T_cold = T_container_init + T_runtime_load + T_handler_init`，三者串行不可重叠。

**公理 A4** (运行时加载有界性):
`T_runtime_load ≥ Size(runtime) / Bandwidth(disk)`，由磁盘 I/O 带宽限制。

**引理 L2** (JVM 冷启动下界):
对于 JVM 运行时，`T_runtime_load ≥ 2s`（类加载、JIT 预热），故 `T_cold(JVM) > 2s`。

**定理 T2** (冷启动时间-资源权衡):
对于给定的函数代码 `f`，在资源分配 `R = (CPU, Mem)` 下，冷启动时间满足：
`T_cold(f, R) = α/CPU + β·Mem + γ·Size(f) + δ`

其中 `α, β, γ, δ` 为平台相关常数。增加 `CPU` 配额可降低容器初始化时间，但存在边际递减：`∂T_cold/∂CPU → 0` 当 `CPU > 4vCPU`。

---

## 九、ASCII 推理判定树

### 9.1 云服务模型选型决策树

```text
┌─────────────────────────────────────────────────────────────┐
│ [根] 需要运行自定义代码?                                     │
│    │                                                        │
│   ┌┴──────────────┐                                        │
│   ▼               ▼                                        │
│ [是]            [否]                                       │
│   │               │                                        │
│   ▼               ▼                                        │
│ 需要控制        直接使用                                   │
│ OS/内核?        SaaS                                       │
│   │               │                                        │
│  ┌┴────┐         └───────► Gmail/Slack/Salesforce          │
│  ▼      ▼                                                  │
│ [是]   [否]                                                │
│  │      │                                                  │
│  ▼      ▼                                                  │
│ IaaS   需要长期运行                                        │
│ 或     服务?                                               │
│ 裸金属  │                                                   │
│        ┌┴──────────────┐                                  │
│        ▼               ▼                                  │
│      [是]             [否]                                │
│        │               │                                  │
│        ▼               ▼                                  │
│      事件驱动/        微服务/                             │
│      流量波动大?      需要编排?                           │
│        │               │                                  │
│       ┌┴────┐         ┌┴────┐                            │
│       ▼      ▼         ▼      ▼                            │
│      [是]   [否]      [是]   [否]                          │
│       │      │         │      │                            │
│       ▼      ▼         ▼      ▼                            │
│      FaaS   PaaS      CaaS   PaaS                         │
│    (Lambda) (GAE)    (GKE)  (Heroku)                      │
└─────────────────────────────────────────────────────────────┘
```

### 9.2 冷启动优化策略决策树

```text
┌─────────────────────────────────────────────────────────────┐
│ [根] 冷启动延迟是否影响 SLA?                                 │
│    │                                                        │
│   ┌┴──────────────────────────────┐                        │
│   ▼                               ▼                        │
│ [是] (延迟敏感)                 [否]                       │
│   │                               │                        │
│   ▼                               ▼                        │
│ 运行时类型?                     无需优化                   │
│   │                                                        │
│  ┌┴────────────────┐                                      │
│  ▼                 ▼                                      │
│ JVM/Node heavy    Go/Rust/Python                         │
│   │                 │                                      │
│   ▼                 ▼                                      │
│ 多策略组合        轻量优化                                │
│   │                 │                                      │
│  ┌┴───────┐       ┌┴──────────────┐                      │
│  ▼        ▼       ▼               ▼                      │
│ SnapStart  预置   128MB         增加内存                 │
│ (Java)    并发   默认配置       至 1-2GB                  │
│   │        │       │               │                      │
│   ▼        ▼       ▼               ▼                      │
│ <1s       <100ms  可能有         降低                    │
│ 启动      冷启动  改善           初始化                   │
│           (付费)                 时间                    │
│                                   │                      │
│                                  ┌┴──────────────┐      │
│                                  ▼               ▼      │
│                                仍不满足        满足     │
│                                  │               │      │
│                                  ▼               ▼      │
│                              考虑预置并发     完成优化  │
│                              或迁移至       (推荐配置)  │
│                              常驻容器                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 十、国际权威课程对齐

### 10.1 课程映射

| 本文件主题 | MIT 6.824 | Stanford CS 244B | CMU 15-319 | Berkeley CS 162 |
|-----------|-----------|------------------|------------|-----------------|
| **IaaS/PaaS/SaaS** | Lec 1: OS Review | Lec: Abstractions | Lec: Cloud Overview | Lec: Abstractions |
| **FaaS/Serverless** | — | Lec: Storage/Comm | Project: Serverless (FaaS) | — |
| **CaaS/K8s** | Lab 5: Persistent KV | Lec: Object-Oriented DS | Project: K8s Orchestration | HW: Threads |
| **责任共担模型** | Lec: RPC Transparency | Lec: Security | Quiz: Cloud Security | Lec: Protection |
| **冷启动/弹性** | Lec: Event-Driven | Lec: Process Migration | Project: Auto-scaling | Lec: Scheduling |
| **成本模型** | — | — | Project: Cost Evaluation | — |

### 10.2 详细映射

**MIT 6.824: Distributed Systems**

- **Lecture 1** (Introduction & O/S Review): 系统分层抽象 → 对应"责任共担模型"的层次划分
- **Lecture 2** (RPC & Threads): 远程过程调用与线程模型 → 对应 FaaS 的执行模型与状态机
- **Lab 5** (Persistent Key/Value Service): 状态持久化 → 对应 IaaS 到 PaaS 的状态管理边界

**Stanford CS 244B: Distributed Systems**

- **Lecture: Storage/Communication Abstractions**: 存储与通信抽象 → 对应各云服务模型的核心差异
- **Lecture: Object-Oriented Distributed System Design**: 面向对象分布式设计 → 对应 PaaS 的应用级抽象
- **Homework**: 论文阅读与批判分析 → 对应"多维矩阵对比"的方法论

**CMU 15-319/15-619: Cloud Computing**

- **Lecture: Cloud Overview & Virtualization**: 云计算概述与虚拟化 → 对应 IaaS 的形式化定义
- **Project: VM Provisioning (AWS/Azure/GCP)**: 虚拟机配置 → 对应 IaaS 实践
- **Project: Serverless Functions**: 无服务器函数部署 → 对应 FaaS 冷启动与执行模型
- **Project: Container Orchestration (K8s)**: 容器编排 → 对应 CaaS 的编排操作集合
- **Quiz: Cloud Economics**: 云经济学 → 对应成本函数与计费模式对比

**Berkeley CS 162: Operating Systems**

- **Lecture: Abstractions**: 操作系统抽象 → 对应从 IaaS 到 SaaS 的抽象层级演进
- **Lecture: Virtual Memory / Paging**: 虚拟内存 → 对应云环境中资源超分与限制
- **Lecture: Scheduling**: CPU 调度 → 对应 FaaS 的并发模型与冷启动调度

### 10.3 核心参考文献

1. **Mell, P., & Grance, T.** (2011). *The NIST Definition of Cloud Computing* (NIST SP 800-145). National Institute of Standards and Technology. —— 云服务模型的权威定义来源，确立 IaaS/PaaS/SaaS 三大基本分类及责任共担模型的标准化表述。

2. **Davis, C.** (2019). *Cloud Native Patterns: Designing Change-Tolerant Software*. Manning Publications. —— 云原生应用设计的模式语言，深入阐述容器化、动态管理与可观测性的工程实践模式。

3. **Hendrickson, S., Sturdevant, S., Harter, T., Venkataramani, V., Arpaci-Dusseau, A. C., & Arpaci-Dusseau, R. H.** (2016). Serverless computation with openlambda. *Elasticloud Workshop*. —— 无服务器计算的开创性学术分析，提出 FaaS 冷启动的经济学与性能权衡框架。

4. **Barroso, L. A., & Hölzle, U.** (2009). *The Datacenter as a Computer: An Introduction to the Design of Warehouse-Scale Machines*. Morgan & Claypool Publishers. —— 仓库级计算机的设计原理，为理解 IaaS 底层资源管理与虚拟化提供物理基础。

---

## 十一、批判性总结

云服务模型的演进史是**控制与便利之间永恒张力**的技术注脚。NIST SP 800-145 所确立的 IaaS/PaaS/SaaS 三分法在2011年具有划时代的分类学意义，但到2026年已显露出其**边界模糊性**：CaaS 的兴起打破了 PaaS 与 IaaS 之间的清晰界限，FaaS 则同时侵蚀了 PaaS（运行时托管）和 SaaS（按调用计费）的领地。这种分类失效并非学术缺陷，而是技术创新的必然结果——最成功的云产品（如 AWS Lambda、Google Cloud Run）往往是跨模型的**杂交形态**。

责任共担模型在安全语境下存在致命的**解释学漏洞**。NIST 框架精确定义了"谁管理什么"，却未能回答"谁对安全事故负最终责任"。当 FaaS 函数因第三方库漏洞被入侵时，云厂商声称"运行时安全由我负责"，而用户则面临"应用层安全由你负责"的困境——中间地带的真空地带恰好是攻击者最钟爱的猎场。更深层的问题是，随着模型抽象度提高（从 IaaS 到 SaaS），用户的**可见性**呈指数衰减：SaaS 用户几乎无法审计底层的安全配置，只能依赖 SOC2 报告这种高度中介化的信任符号。

FaaS 的"冷启动"问题揭示了 Serverless 范式中一个被刻意淡化的**结构性矛盾**：云厂商将无服务器包装为"纯事件驱动"的理想模型，却隐藏了容器初始化这一物理现实的必然性。预置并发（Provisioned Concurrency）的引入实质上是对 Serverless 原教旨主义的背叛——它承认了常驻实例在某些场景下的不可替代性。CaaS（托管 Kubernetes）之所以在2026年成为企业主流选择，正因为它诚实地承认了运维复杂性的存在，而不是像 FaaS 那样将其伪装为零。最终，服务模型的选择不应是宗教式的站队，而应是**负载特征、团队能力与成本结构的函数优化**——对于年调用量不足千万的函数，FaaS 的便利性远超其冷启动代价；对于持续高吞吐的服务，常驻容器的经济性无可匹敌。
