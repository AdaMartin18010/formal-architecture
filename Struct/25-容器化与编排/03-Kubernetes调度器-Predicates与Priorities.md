# Kubernetes 调度器：Predicates 与 Priorities

> **来源映射**: View/00.md §3.1
> **国际权威参考**: Kubernetes Scheduler Documentation, "Kubernetes Scheduling" (Huang et al.), Borg (Google)

---

## 一、知识体系思维导图

```text
Kubernetes 调度器
│
├─► 调度流程 (Scheduler Framework)
│   ├─ 1. Predicates (过滤): 找出所有可行节点
│   ├─ 2. Priorities (评分): 为可行节点打分
│   └─ 3. Bind: 将 Pod 绑定到最优节点
│
├─► Predicates (硬性约束)
│   ├─ PodFitsResources: CPU/内存/存储是否足够
│   ├─ PodFitsHost: 指定节点名匹配
│   ├─ PodFitsHostPorts: 端口不冲突
│   ├─ MatchNodeSelector: 节点标签匹配
│   ├─ NoDiskConflict: 存储卷不冲突
│   ├─ PodToleratesNodeTaints: 容忍污点
│   └─ CheckNodeCondition: 节点状态正常
│
├─► Priorities (软性偏好)
│   ├─ LeastRequested: 选择资源使用率低的节点
│   ├─ BalancedResourceAllocation: CPU/内存均衡使用
│   ├─ NodeAffinity: 节点亲和性匹配度
│   ├─ PodAffinity/AntiAffinity: Pod间亲和/反亲和
│   ├─ TaintToleration: 污点容忍度评分
│   └─ ImageLocality: 镜像本地缓存加分
│
├─► 资源模型
│   ├─ Requests: 保证分配的资源 (调度依据)
│   ├─ Limits: 资源使用上限 (运行时限制)
│   └─ QoS 级别:
│       ├─ Guaranteed: Requests=Limits (全部资源)
│       ├─ Burstable: Requests<Limits (部分资源)
│       └─ BestEffort: 无 Requests/Limits (最后分配)
│
├─► 亲和性与反亲和性
│   ├─ NodeAffinity: 节点标签偏好 (required/preferred)
│   ├─ PodAffinity: 与某 Pod 同节点/同拓扑域
│   └─ PodAntiAffinity: 与某 Pod 不同节点/拓扑域
│
└─► 调度框架扩展 (Scheduler Framework v2)
    ├─ QueueSort: 排序待调度 Pod
    ├─ PreFilter/Filter: 自定义过滤逻辑
    ├─ PreScore/Score: 自定义评分逻辑
    ├─ Reserve: 预留资源
    ├─ Permit: 批准/拒绝/等待
    ├─ PreBind/Bind: 绑定前/绑定
    └─ PostBind: 绑定后清理
```

---

## 二、核心概念的形式化定义

### 2.1 调度问题形式化

```text
定义 (Pod 调度问题):
  输入:
    Pod P = ⟨resources_req, constraints, preferences⟩
    节点集合 N = {n₁, n₂, ..., nₖ}
    每个节点 nᵢ = ⟨allocatable, allocated, labels, taints⟩

  输出: 最优节点 n* ∈ N

  约束满足:
    feasible(N, P) = {n ∈ N | ∀predicate p, p(n, P) = true}

  优化目标:
    score(n, P) = Σ wᵢ · priorityᵢ(n, P)
    n* = argmaxₙ∈feasible score(n, P)

  资源约束形式化:
    PodFitsResources(n, P) ⟺
      n.cpu_allocated + P.cpu_req ≤ n.cpu_allocatable ∧
      n.mem_allocated + P.mem_req ≤ n.mem_allocatable ∧
      n.storage_allocated + P.storage_req ≤ n.storage_allocatable
```

### 2.2 QoS 与驱逐

```text
定义 (QoS 级别):
  设 Pod P 的资源配置:

  Guaranteed(P) ⟺ ∀container c ∈ P:
    c.cpu_request = c.cpu_limit ∧
    c.mem_request = c.mem_limit ∧
    c.cpu_request > 0 ∧ c.mem_request > 0

  BestEffort(P) ⟺ ∀container c ∈ P:
    c.cpu_request = 0 ∧ c.mem_request = 0

  Burstable(P) ⟺ ¬Guaranteed(P) ∧ ¬BestEffort(P)

  驱逐优先级 (节点压力时):
    BestEffort > Burstable > Guaranteed
    即: Guaranteed 最后被驱逐
```

---

## 三、调度器对比矩阵

| 特性 | 默认 Scheduler | Custom Scheduler | Scheduler Framework | Volcano (批处理) |
|------|---------------|-----------------|--------------------|-----------------|
| **适用场景** | 通用工作负载 | 特殊硬件/策略 | 插件化扩展 | ML/HPC 批处理 |
| **扩展方式** | 不可扩展 | 独立二进制 | **插件 (Webhook)** | 替换调度器 |
| **调度延迟** | 10-100ms | 同默认 | 同默认 | 优化批处理 |
| **Gang Scheduling** | ❌ | 自实现 | 插件 | ✅ 原生 |
| **优先级抢占** | ✅ | 自实现 | ✅ | ✅ |
| **复杂性** | 低 | 高 | 中 | 中 |

---

## 四、权威引用

> **Brendan Burns** (Kubernetes 联合创始人):
> "The Kubernetes scheduler is designed to be simple, fast, and extensible."

> **Google Borg 论文** (EuroSys 2015):
> "Borg's scheduler uses a two-phase approach: feasibility checking followed by scoring." —— Kubernetes 调度器的直接祖先。

> **Wei Huang** et al. (Kubernetes Scheduling SIG):
> "The scheduling framework provides extension points that allow users to implement custom scheduling logic without forking the scheduler."

---

## 五、工程实践

### 5.1 Pod 资源配置最佳实践

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: app
    image: myapp:1.0
    resources:
      requests:
        cpu: "500m"       # 保证 0.5 核
        memory: "512Mi"   # 保证 512MB
      limits:
        cpu: "2000m"      # 上限 2 核
        memory: "1Gi"     # 上限 1GB
    # QoS: Burstable (Requests < Limits)
---
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: app
    image: critical-app:1.0
    resources:
      requests:
        cpu: "1000m"
        memory: "2Gi"
      limits:
        cpu: "1000m"
        memory: "2Gi"
    # QoS: Guaranteed (Requests = Limits)
```

### 5.2 亲和性配置

```yaml
apiVersion: v1
kind: Pod
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: disktype
            operator: In
            values: ["ssd"]
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 1
        preference:
          matchExpressions:
          - key: zone
            operator: In
            values: ["zone-a"]
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values: ["web"]
        topologyKey: kubernetes.io/hostname
        # 同一节点上不运行多个 web Pod
```

---

## 六、批判性总结

Kubernetes 调度器的**两阶段过滤+评分**设计是**组合优化问题**的贪心近似解：它不能保证全局最优，但在多项式时间内给出足够好的解。这与 Google Borg 的调度哲学一致——**快速决策优于完美决策**，因为集群状态每秒都在变化。

但默认调度器的**资源模型过于简化**：它只考虑 Requests 和 Limits，忽略了 NUMA 拓扑、GPU 拓扑、网络带宽、磁盘 I/O 等关键维度。这导致在 HPC 和 AI 训练场景中，Kubernetes 调度器表现不佳——Volcano 和 Kube-batch 等项目的出现正是为了填补这一空白。

QoS 级别的设计是**优雅的资源分层**：Guaranteed 工作负载获得最高优先级，BestEffort 工作负载作为"填料"提高资源利用率。但这种分层也带来了**资源碎片**问题——Burstable Pod 的资源请求与实际使用之间的差异，导致节点资源利用率统计失真。这是声明式资源模型的固有代价。
