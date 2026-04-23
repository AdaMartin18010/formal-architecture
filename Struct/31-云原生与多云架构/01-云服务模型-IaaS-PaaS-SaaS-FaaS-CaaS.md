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
