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


---

## 七、概念属性关系网络

### 7.1 核心概念关系表

| 概念A | 关系类型 | 概念B | 关系说明 |
|-------|----------|-------|----------|
| Scheduler | 执行 -> | Predicates | 过滤不满足硬性约束的节点 |
| Scheduler | 执行 -> | Priorities | 对可行节点评分排序 |
| Predicates | 检查 -> | Node资源 | CPU/Memory/Storage/GPU是否足够 |
| Predicates | 检查 -> | 亲和性约束 | NodeAffinity/PodAffinity/AntiAffinity |
| Priorities | 优化 -> | 资源均衡 | LeastRequested/BalancedResourceAllocation |
| Priorities | 优化 -> | 拓扑分布 | SelectorSpreadPriority |
| Taint | 排斥 -> | Pod | 除非 Pod 有对应 Toleration |
| Toleration | 容忍 -> | Taint | 允许 Pod 调度到带 Taint 的节点 |
| QoS Class | 决定 -> | 驱逐优先级 | Guaranteed > Burstable > BestEffort |
| ResourceQuota | 限制 -> | Namespace | 命名空间级别的资源总量限制 |

### 7.2 ASCII拓扑图

```text
Kubernetes 调度流程拓扑
===========================================================

                      +-------------+
                      |  待调度 Pod  |
                      +------+------+
                             |
                             v
                    +----------------+
                    | 1. Predicates  |
                    |   (过滤阶段)    |
                    | 找出可行节点集F |
                    +--------+-------+
                             |
              +--------------+--------------+
              v              v              v
         +--------+    +--------+    +--------+
         |资源足够?|    |端口冲突?|    |亲和性? |
         +---+----+    +---+----+    +---+----+
             |             |             |
        Yes  |        No   |        Yes  |
             |             |             |
             v             v             v
        保留节点       排除节点       保留节点

                             |
                             v
                    +----------------+
                    | 2. Priorities  |
                    |   (评分阶段)    |
                    | 为F中节点打分   |
                    +--------+-------+
                             |
              +--------------+--------------+
              v              v              v
         +--------+    +--------+    +--------+
         |资源均衡 |    |节点亲和 |    |负载分散 |
         |得分+5  |    |得分+3  |    |得分+2  |
         +---+----+    +---+----+    +---+----+
                             |
                             v
                    +--------+--------+
                    | 3. Bind (绑定)  |
                    | 选择最高分节点  |
                    | n* = argmax(score)|
                    +-----------------+

QoS 与驱逐关系
===========================================================

        +-------------+     +-------------+     +-------------+
        | Guaranteed  |     |  Burstable  |     | BestEffort  |
        | (Req=Limit) |     | (Req<Limit) |     |  (无请求)   |
        +------+------+     +------+------+     +------+------+
               |                   |                   |
               v                   v                   v
          最高优先级           中等优先级          最低优先级
          (最后驱逐)           (条件驱逐)          (首先驱逐)

===========================================================
```

### 7.3 形式化映射

设调度问题为三元组 **S = (P, N, F)**，其中：

- **P** = 待调度 Pod，具有资源请求 R(P) = {cpu_req, mem_req, gpu_req, ...}
- **N** = 节点集合 {n1, n2, ..., nm}，每个节点具有可用资源 A(ni) = {cpu_avail, mem_avail, ...}
- **F** = 可行性函数 F(P, ni) = AND_{j=1..k} predicate_j(P, ni)

调度目标函数：
n*= argmax_{ni in F(P)} Sum_{l=1..q} w_l* priority_l(P, ni)

约束条件：

- 硬约束（Hard Constraints）：F(P, ni) = True 是必要条件
- 软约束（Soft Constraints）：priority_l(P, ni) 提供偏好排序
- 资源守恒：forall ni, Sum_{P scheduled to ni} R(P) <= Capacity(ni)

QoS 形式化为资源承诺集合：

- Guaranteed: Requests(P) = Limits(P) and Requests(P) > 0
- Burstable: Requests(P) < Limits(P) and Requests(P) > 0
- BestEffort: Requests(P) = 0

---

## 八、形式化推理链

**公理 1（资源守恒公理）**：节点上所有已调度 Pod 的资源请求总和不得超过节点容量。
forall n in Nodes, Sum_{P in Pods(n)} cpu_req(P) <= cpu_capacity(n)
forall n in Nodes, Sum_{P in Pods(n)} mem_req(P) <= mem_capacity(n)

**公理 2（Predicate 单调性）**：若节点 n 满足 Pod P 的所有 Predicates，则 n 的资源容量至少为 P 的请求量。
F(P, n) = True -> forall r in Resources, avail_r(n) >= req_r(P)

**引理 1（调度可行性下界）**：若集群总资源容量不足以满足 Pod 请求，则调度必然失败。
*证明*：Sum_{n in Nodes} Capacity(n) < Sum_{P in Pending} Request(P) -> 不存在合法调度方案。这是调度问题的必要条件，而非充分条件（因碎片化和亲和性约束）。参见 Ullman (1975) NP-Complete Scheduling Problems。

**引理 2（Priorities 评分上界）**：每个 Priority 函数的输出归一化到 [0, 10] 区间，总评分上界为 10 * q（q 为启用的 priority 数量）。
*证明*：由 Kubernetes Scheduler Framework 的 NormalizeScore 插件保证，每个 ScorePlugin 的 Score 方法返回值经 Normalize 后映射到 [0, 10]。参见 Kubernetes Enhancement Proposals (KEP-624, 2019)。

**定理 1（调度器时间复杂度）**：Kubernetes 默认调度器的时间复杂度为 O(|N| *(k + q))，其中 |N| 为节点数，k 为 Predicates 数量，q 为 Priorities 数量。
*证明*：每个 Pod 调度需遍历所有节点执行 k 个 Predicates（每个 O(1) 若使用缓存），然后对通过的节点执行 q 个 Priorities。因此总复杂度为 O(|N|*k + |F|*q)，最坏情况下 |F| = |N|。参见 Rejiba & Chamanara (2022) Custom Scheduling in Kubernetes: A Survey, ACM Computing Surveys。

**定理 2（QoS 驱逐顺序定理）**：在节点内存压力触发 OOM 或驱逐时，Pod 的驱逐顺序严格遵循 BestEffort -> Burstable -> Guaranteed。
*形式化*：forall p1, p2 in Pods(n), if QoS(p1) < QoS(p2) then eviction_priority(p1) > eviction_priority(p2)
*证明*：由 kubelet 的 eviction_manager 实现，QoS 级别映射到 oom_score_adj：BestEffort=1000, Burstable=2-999, Guaranteed=-998。Linux OOM Killer 选择 oom_score 最高的进程终止。参见 Kubernetes Documentation: Out-of-Resource Handling。

**推论 1**：Predicates 的过滤结果具有单调性：若节点 n 不满足 Pod P 的某个 Predicate，则向 n 添加更多 Pod 不会使 n 变得可行（资源 Predicate 是单调递减的）。

**推论 2**：Priorities 的评分不具有传递性：priority(A) > priority(B) and priority(B) > priority(C) 不保证 priority(A) > priority(C) 在所有权重组合下成立，因为不同 Priorities 可能给出矛盾的排序。

---

## 九、ASCII推理判定树

### 9.1 Pod 调度失败排查决策树

```text
Pod 调度失败排查
===========================================================

                      +-------------+
                      | Pod Pending? |
                      +------+------+
                             |
                             v
                    +----------------+
                    | kubectl describe |
                    | pod <name>      |
                    +--------+-------+
                             |
              +--------------+--------------+
              v              v              v
         +--------+    +--------+    +--------+
         |0/3节点|    |0/3节点 |    |其他错误 |
         |资源不足|    |有污点的 |    |(亲和性) |
         +---+----+    +---+----+    +---+----+
             |             |             |
             v             v             v
    +----------------+ +---------+ +----------------+
    | 检查节点资源:   | | 检查污点:| | 检查亲和性规则: |
    | - CPU/Memory   | | - 节点有 | | - nodeSelector |
    | - GPU/存储      | |   NoSchedule?| | - podAffinity |
    |                | | - Pod无  | | - antiAffinity |
    | 方案:          | |   toleration| |                |
    | - 扩容集群      | |           | | 方案:          |
    | - 降低请求      | | 方案:    | | - 修改规则      |
    | - 清理资源      | | - 添加   | | - 增加可用节点  |
    |                | | toleration| |                |
    +----------------+ +---------+ +----------------+

===========================================================
```

### 9.2 资源配额设计决策树

```text
资源配额与限制设计
===========================================================

                      +-------------+
                      | 设计资源策略|
                      +------+------+
                             |
              +--------------+--------------+
              | 工作负载类型?                |
              +--------------+--------------+
                             |
            +----------------+----------------+
            v                v                v
         生产关键          普通服务          批处理/测试
            |                |                |
            v                v                v
    +-------------+  +-------------+  +-------------+
    | Guaranteed  |  | Burstable   |  | BestEffort  |
    | QoS         |  | QoS         |  | (或无限制)  |
    +------+------+  +------+------+  +------+------+
           |                |                |
           v                v                v
    Request=Limit     Request<Limit      无 Request
    (精确预留)         (弹性共享)        (尽力而为)
           |                |                |
           v                v                v
    适用场景:          适用场景:          适用场景:
    - 数据库           - Web服务          - CI/CD Job
    - 核心API          - 缓存层           - 数据处理
    - 支付服务         - 消息队列         - 开发环境

===========================================================
```

---

## 十、国际权威课程对齐

### 10.1 课程映射

**MIT 6.824: Distributed Systems**

- **Lecture 8**: Spanner -> 对应分布式调度中的全局资源视图与一致性
- **Lecture 12**: Cache Consistency -> 对应调度器缓存与节点状态同步
- **Project 2**: Raft KV Store -> 对应 etcd 作为调度状态存储的共识机制

**Stanford CS 140: Operating Systems**

- **Lecture 7**: Scheduling -> 对应 CPU 调度与 Kubernetes 节点选择的类比
- **Lecture 9**: Memory Management -> 对应内存请求/限制与 OOM 处理
- **Project**: PintOS Priority Scheduler -> 对应优先级调度算法实现

**CMU 15-440: Distributed Systems**

- **Lecture 7**: Resource Allocation -> 对应分布式资源分配策略
- **Lecture 10**: Load Balancing -> 对应 Priorities 中的负载均衡策略

**Berkeley CS 162: Operating Systems**

- **Lecture 8**: Scheduling -> 对应多队列调度与 Kubernetes 调度框架
- **Lecture 15**: Distributed File Systems -> 对应存储资源调度与拓扑感知

### 10.2 核心参考文献

1. Z. Rejiba, J. Chamanara (2022). Custom Scheduling in Kubernetes: A Survey on Common Problems and Solution Approaches. ACM Computing Surveys, 55, 1-37. 对 Kubernetes 调度算法的全面综述，涵盖默认调度器和自定义调度器扩展。

2. J. E. Ullman (1975). NP-Complete Scheduling Problems. Journal of Computer and System Sciences, 10, 384-393. 调度问题复杂度分析的经典论文，Kubernetes 调度作为装箱问题的近似解。

3. W.-K. Lai, Y.-C. Wang, S.-C. Wei (2023). Delay-Aware Container Scheduling in Kubernetes. IEEE Internet of Things Journal, 10, 11813-11824. 考虑网络延迟感知的容器调度优化。

4. Z. Jian, X. Xie, Y. Fang, et al. (2024). DRS: A Deep Reinforcement Learning Enhanced Kubernetes Scheduler for Microservice-based System. Software: Practice and Experience, 54, 2102-2126. 基于深度强化学习的 Kubernetes 调度器优化。

---

## 十一、深度批判性总结

Kubernetes 调度器的两阶段过滤+评分设计是组合优化问题的贪心近似解：它不能保证全局最优，但在多项式时间内给出足够好的解。这与 Google Borg 的调度哲学一致——快速决策优于完美决策，因为集群状态每秒都在变化。然而，这种贪心策略在面对复杂约束（如 PodAntiAffinity + TopologySpreadConstraints + ResourceQuota 的组合）时，可能陷入局部最优，导致调度结果远离理论最优解。

但默认调度器的资源模型过于简化：它只考虑 Requests 和 Limits，忽略了 NUMA 拓扑、GPU 拓扑、网络带宽、磁盘 I/O 等关键维度。这导致在 HPC 和 AI 训练场景中，Kubernetes 调度器表现不佳——Volcano 和 Kube-batch 等项目的出现正是为了填补这一空白。特别是 GPU 调度，默认调度器将 GPU 视为标量资源（nvidia.com/gpu: 1），完全忽略了 GPU 之间的 NVLink 拓扑、显存容量差异和多实例 GPU（MIG）的细粒度划分。

QoS 级别的设计是优雅的资源分层：Guaranteed 工作负载获得最高优先级，BestEffort 工作负载作为填料提高资源利用率。但这种分层也带来了资源碎片问题——Burstable Pod 的资源请求与实际使用之间的差异，导致节点资源利用率统计失真。这是声明式资源模型的固有代价：为了可预测性而牺牲利用率，或为了利用率而牺牲可预测性。未来的调度器应当引入在线学习机制，根据历史使用模式动态调整资源请求建议，而非依赖开发者的人工估算。
