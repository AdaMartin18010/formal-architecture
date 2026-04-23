# 声明式基础设施：GitOps 与持续协调

> **来源映射**: View/00.md §3.1, Struct/25-容器化与编排/00-总览-容器运行时与编排系统的形式化.md
> **国际权威参考**: "GitOps" (Weaveworks, Alexis Richardson, 2017), "Kubernetes Control Theory" (Joe Beda, 2018), "Flux CD / ArgoCD Documentation", "Progressive Delivery" (James Governor, RedMonk)

---

## 一、知识体系思维导图

```text
声明式基础设施与 GitOps
│
├─► 声明式 vs 命令式
│   ├─ 命令式 (Imperative): kubectl create/run/scale —— 描述"如何做"
│   ├─ 声明式 (Declarative): kubectl apply -f —— 描述"期望是什么"
│   └─ 核心差异: 幂等性、可审计性、版本控制兼容性
│
├─► GitOps 工作流
│   ├─ 单一可信源: Git 仓库 = 期望状态的唯一真相
│   ├─ 自动协调: GitOps Agent 持续比对 Git ↔ Cluster
│   ├─ 收敛原则: 任何偏离都会被检测并纠正 (self-healing)
│   ├─ 工具:
│   │   ├─ ArgoCD: UI 丰富, ApplicationSet, 多集群
│   │   ├─ Flux CD: GitOps 原生, 渐进交付, OCI 制品支持
│   │   └─ Rancher Fleet: 大规模集群 GitOps 管理
│   └─ 安全模型: Pull-based (拉取), 集群无需外部暴露
│
├─► 控制循环 (Control Loop / Reconciliation)
│   ├─ 感知 (Observe): Watch API 资源变化
│   ├─ 差异分析 (Diff): desired state vs actual state
│   ├─ 执行 (Act): 创建/更新/删除资源
│   ├─ 报告 (Report): Status/Conditions/Events 更新
│   └─ 指数退避: 失败时 backoff 重试, 避免惊群
│
└─► 渐进交付与协调扩展
    ├─ 蓝绿部署: 并行环境切换
    ├─ 金丝雀发布: 流量权重渐进迁移 (Flagger, Argo Rollouts)
    ├─ 自动回滚: 基于 Prometheus 指标的失败检测
    └─ 漂移检测 (Drift Detection): 手动修改被自动恢复
```

---

## 二、核心概念的形式化定义

```text
定义 (声明式配置):
  DeclarativeConfig = ⟨Spec, Status⟩

  Spec:   用户声明的期望状态 (Desired State)
  Status: 系统观测到的实际状态 (Actual State)

定义 (控制循环 / Reconciliation Loop):
  Reconcile = λ(spec, status):
    while true:
      observed = Observe(system)
      if spec ≠ observed:
        diff = Diff(spec, observed)
        Execute(diff)        // 创建/更新/删除
      UpdateStatus(observed)
      Sleep(interval)

  收敛性条件 (Convergence):
    limₜ→∞ P(spec = Observe(system)) = 1
    // 在无限时间下, 系统状态以概率1收敛到期望状态

定义 (GitOps 状态机):
  GitOpsState = ⟨GitState, ClusterState, ImageState⟩

  协调函数:
    Sync(GitState) → ClusterState'
    约束: ClusterState' ≡ GitState

  漂移检测:
    Drift = Diff(ClusterState, GitState)
    if Drift ≠ ∅ → TriggerRemediation(Drift)

定义 (幂等性):
  Apply(Config) → State
  Idempotent(Apply) ↔ ∀n ≥ 1: Applyⁿ(Config) = Apply(Config)
```

---

## 三、多维矩阵对比

| 维度 | 命令式 (Imperative) | 声明式 (Declarative) | GitOps |
|------|-------------------|---------------------|--------|
| **状态表达** | 操作序列 | 目标状态 | Git 仓库 = 唯一真相 |
| **幂等性** | 否 (重复执行会报错) | 是 (kubectl apply) | 是 (持续协调) |
| **可审计性** | 低 (命令历史分散) | 中 (YAML 文件) | 高 (Git commit log) |
| **回滚能力** | 手动编写逆向操作 | 应用旧版本 YAML | git revert 自动回滚 |
| **协作模式** | 单人/脚本 | 团队共享 YAML | PR Review + 合并触发 |
| **安全边界** | 需要集群写权限 | 需要集群写权限 | 集群只读, Agent 拉取 |
| **漂移处理** | 无 | 无 (一次性应用) | 自动检测并修复 |

| GitOps 工具 | 架构 | 多集群 | 渐进交付 | UI | 生态 |
|-----------|------|--------|---------|-----|------|
| **ArgoCD** | Pull-based | 优秀 | Argo Rollouts | 丰富 | CNCF 孵化 |
| **Flux CD** | Pull-based | 良好 | Flagger | 基础 | CNCF 毕业 |
| **Rancher Fleet** | Pull-based | 大规模 | 无 | 集成 Rancher | SUSE |
| **Tekton** | Push-based | 需配置 | 手动 | 无 | CI/CD 原生 |

---

## 四、权威引用

> **Alexis Richardson** (Weaveworks CEO, "GitOps" 命名者, 2017):
> "GitOps is a way to do Kubernetes cluster management and application delivery. It works by using Git as a single source of truth for declarative infrastructure and applications."

> **Joe Beda** (Kubernetes 联合创始人, "Control Theory for Kubernetes", 2018):
> "Kubernetes is fundamentally a control theory system. Controllers watch the state of the world and take action to drive observed state toward desired state."

> **Kelsey Hightower** (Google):
> "The key to GitOps is not the tools. It's the discipline of having a single source of truth and the confidence that the system will converge to that truth."

> **James Governor** (RedMonk, "Progressive Delivery", 2019):
> "Continuous Delivery is about shipping fast; Progressive Delivery is about shipping safely. GitOps provides the foundation for both."

---

## 五、工程实践与代码示例

**ArgoCD Application 声明:**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
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
      prune: true      # 删除 Git 中不存在的资源
      selfHeal: true   # 自动修复手动漂移
    syncOptions:
    - CreateNamespace=true
```

**Flux CD GitRepository + Kustomization:**

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: myapp
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/org/gitops-repo.git
  ref:
    branch: main
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: myapp
  namespace: flux-system
spec:
  interval: 10m
  path: ./overlays/production
  prune: true
  sourceRef:
    kind: GitRepository
    name: myapp
```

---

## 六、批判性总结

GitOps 的核心价值不在于"用 Git 管理 YAML"这一表面形式，而在于它建立了**不可变基础设施的闭环**：Git 的提交历史构成了状态演变的完整审计链，任何对生产环境的变更都必须通过 PR Review 这一"社会性门控"。这与传统运维的"SSH 登录改配置"形成了文明与野蛮的分野。然而，GitOps 的"拉取模型"（Pull-based）虽然提升了安全性（集群无需对外暴露 API），但其**协调延迟**（通常 1-5 分钟）对于需要秒级响应的紧急故障恢复场景是致命的——ArgoCD 的同步间隔与 Flux 的轮询周期决定了它无法替代命令式调试工具。

声明式配置的幂等性假设在实践中经常被打破：`kubectl apply` 的三向合并策略（last-applied-configuration vs live vs new）在处理列表字段（如环境变量数组）时会产生非直觉行为，这是 Kubernetes API 中最常见的"配置漂移"来源之一。控制循环的"最终一致性"（eventual consistency）在脑裂、网络分区或控制器自身故障时可能导致**调和风暴**（reconciliation storm）——多个控制器对同一资源进行冲突更新。

更深层的矛盾在于：GitOps 假设"Git 中的状态是唯一真相"，但现代系统的实际状态分散在多个维度——Kubernetes 资源状态、云厂商 IAM 策略、Terraform 管理的云资源、Vault 中的密钥。2024-2026 年的趋势是**平台工程内部开发者平台 (IDP)** 将这些分散的声明式配置统一到单一控制平面（如 Backstage + Crossplane + GitOps），但不同工具间的状态一致性仍是一个开放的分布式系统难题。GitOps 是正确方向，但不是终点。
