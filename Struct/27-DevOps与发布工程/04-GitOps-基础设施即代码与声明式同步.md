# GitOps：基础设施即代码与声明式同步

> **来源映射**: View/00.md §3.1, 模块27总览
> **国际权威参考**: "Infrastructure as Code" (Kief Morris, 2020), "GitOps" (Weaveworks, 2017), "Terraform: Up & Running" (Brikman, 2022), Flux/ArgoCD Official Documentation

---

## 一、知识体系思维导图

```text
GitOps 与基础设施即代码
│
├─► 基础设施即代码 (IaC)
│   ├─► 声明式 (Declarative)
│   │   ├─ 描述期望状态，系统负责收敛
│   │   ├─ Terraform: HCL 描述云资源
│   │   ├─ Pulumi: 通用编程语言 (TS/Python/Go)
│   │   └─ CloudFormation / ARM / Bicep
│   ├─► 命令式 (Imperative)
│   │   ├─ Ansible: 步骤化 playbook
│   │   ├─ Chef: 菜谱式资源配置
│   │   └─ SaltStack / Puppet
│   └─► 核心原则
│       ├─ 版本控制: Git 作为唯一可信源
│       ├─ 幂等性: 多次执行结果一致
│       ├─ 可审计: 所有变更可追溯
│       └─ 可复现: 相同输入产生相同基础设施
│
├─► GitOps 工作流
│   ├─► 核心理念
│   │   ├─ Git 作为 Single Source of Truth
│   │   ├─ 声明式系统描述 (K8s YAML/Helm/Kustomize)
│   │   ├─ 自动同步: Git 变更 → 集群状态调和
│   │   └─ 差异检测 (Drift Detection)
│   ├─► 代表工具
│   │   ├─ ArgoCD: 可视化 UI, 应用集, 多集群
│   │   ├─ FluxCD: CNCF 毕业, GitOps 原生, 轻量
│   │   └─ Rancher Fleet: 多集群 GitOps 管理
│   └─► 部署模式
│       ├─ Push: CI 系统主动推送变更到集群
│       └─ Pull: 集群代理拉取 Git 变更并应用
│
└─► 漂移检测与状态调和
    ├─ 漂移 (Drift): 实际状态偏离 Git 声明状态
    ├─ 检测周期: 定期扫描或事件触发
    ├─ 自动修复: 自恢复 (Self-healing) 模式
    └─ 人工审批: 生产环境变更需审批
```

---

## 二、核心概念的形式化定义

```text
定义 (基础设施即代码的形式化):
  设基础设施状态空间 S，代码描述 D，执行引擎 E:
    apply: D × S_current → S_target
    幂等性要求: apply(D, apply(D, S)) = apply(D, S)

  状态差异函数:
    diff: S_actual × S_declared → Δ
    其中 Δ = {(r, action) | r 为资源, action ∈ {Create, Update, Delete, NoOp}}

定义 (GitOps 控制回路):
  设 Git 仓库 G，目标集群 C，同步代理 A (如 ArgoCD/Flux):

  控制回路 (Reconciliation Loop):
    while True:
      S_git   = read(G)          # Git 声明状态
      S_cluster = observe(C)     # 集群实际状态
      Δ = diff(S_git, S_cluster) # 计算差异
      if Δ ≠ ∅:
        apply(Δ, C)              # 调和差异
      sleep(interval)

  漂移检测:
    drift_detected = S_cluster ≠ S_git
    自恢复策略:
      - auto_sync:   自动应用 Δ
      - notify_only: 告警但不自动修复
      - manual:      人工审批后修复

定义 (Terraform 状态管理):
  状态文件 tfstate 记录映射:
    M: resource_address → (provider_id, attributes)

  plan 阶段计算:
    Δ = diff(M_current, M_desired)

  状态锁定 (State Locking):
    防止并发修改，使用 DynamoDB / Consul / GCS 实现互斥锁
```

---

## 三、多维矩阵对比

| 维度 | Terraform | Pulumi | Ansible | ArgoCD | FluxCD |
|------|-----------|--------|---------|--------|--------|
| **范式** | 声明式 | 声明式 (编程式) | 命令式 | 声明式 (GitOps) | 声明式 (GitOps) |
| **适用范围** | 云资源 (IaC) | 云资源 + K8s | 服务器配置 | K8s 应用部署 | K8s 应用部署 |
| **状态管理** | 本地/远程状态文件 | 服务后端 | 无状态 | Git 即状态 | Git 即状态 |
| **语言** | HCL | TS/Python/Go/C# | YAML | YAML/JSON | YAML |
| **多集群** | Workspace + 后端 | Stack | inventory | 原生支持 | 原生支持 |
| **可视化** | Terraform Cloud | Pulumi Cloud | AWX/Tower | 优秀 Web UI | 有限 CLI/GUI |
| **社区生态** | 最成熟 (4000+ providers) | 快速增长 | 成熟 | CNCF 孵化 | CNCF 毕业 |

| 维度 | Push 模式 | Pull 模式 |
|------|-----------|-----------|
| **执行主体** | CI/CD 系统 | 集群内代理 |
| **安全模型** | CI 需集群凭据 | 集群只需 Git 只读权限 |
| **网络要求** | 出网到集群 API | 出网到 Git 仓库 |
| **实时性** | 触发式 | 轮询/Webhook |
| **审批流程** | CI 中实现 | 原生支持 |
| **代表工具** | Jenkins/GitLab CI | ArgoCD, FluxCD |

---

## 四、权威引用

> **Kief Morris** ("Infrastructure as Code", 2nd Ed, 2020):
> "Infrastructure as Code is an approach to infrastructure automation based on practices from software development. It emphasizes consistent, repeatable routines for provisioning and changing systems."

> **Alexis Richardson** (Weaveworks CEO, "GitOps" 概念提出者, 2017):
> "GitOps is a way to do Kubernetes cluster management and application delivery. It works by using Git as a single source of truth for declarative infrastructure and applications."

> **Yevgeniy Brikman** ("Terraform: Up & Running", 2022):
> "Terraform's true superpower is not just creating infrastructure, but the ability to plan changes before applying them, giving operators full visibility into what will happen."

> **CNCF GitOps Working Group** (GitOps Principles v1.0, 2021):
> "The desired state of a GitOps managed system must be stored in a way that supports versioning, immutability of versions, and retains a complete version history."

---

## 五、工程实践与代码示例

```hcl
# Terraform: 声明式基础设施示例
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket         = "tf-state-prod"
    key            = "vpc/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tf-lock-table"  # 状态锁定
    encrypt        = true
  }
}

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true

  tags = {
    Name        = "prod-vpc"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# 漂移检测: terraform plan 输出差异
# terraform plan -detailed-exitcode
# 退出码 0: 无差异, 2: 有差异
```

```yaml
# ArgoCD Application: 声明式 GitOps 配置
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-service
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/gitops-repo.git
    targetRevision: HEAD
    path: overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true        # 删除 Git 中不存在的资源
      selfHeal: true     # 自动修复漂移
    syncOptions:
      - CreateNamespace=true
```

---

## 六、批判性总结

GitOps 看似将运维复杂性优雅地转移给了 Git，但其背后隐藏着三个深层挑战。**第一，Git 作为唯一可信源的假设在实践中经常被打破**：紧急故障修复时，工程师直接通过 `kubectl edit` 修改集群以快速恢复服务，而 Git 仓库中的声明文件并未同步更新，导致"配置漂移"成为常态而非例外。成熟的团队必须将紧急修改纳入标准运维流程：任何手动修改都必须在 15 分钟内回写到 Git，否则自动修复将覆盖救急变更。**第二，Terraform 的状态文件是架构的"阿喀琉斯之踵"**：状态文件损坏或丢失意味着整个基础设施的映射关系消失，虽然 `terraform import` 可以重建，但大规模环境下的手动导入成本极高。状态文件必须存放在远程后端（S3 + DynamoDB），并启用版本控制和加密。**第三，声明式系统的"最终一致性"在紧急场景下是双刃剑**：ArgoCD 的自动同步可能在故障排查时与人工操作发生冲突，生产环境应当启用"手动同步 + 审批"模式，将 GitOps 的自动化与变更管理的审慎性结合。GitOps 不是"无运维"，而是将运维关注点从"如何执行变更"转移到"如何定义期望状态"——这是一种范式的跃迁，但绝非银弹。
