# Kubernetes 核心抽象：从 Pod 到 Deployment

> **来源映射**: View/00.md §3.1, Struct/25-容器化与编排/00-总览-容器运行时与编排系统的形式化.md
> **国际权威参考**: Kubernetes Docs (v1.29), "Borg, Omega, and Kubernetes" (Brendan Burns et al., ACM Queue 2016), "Designing Distributed Systems" (Brendan Burns, O'Reilly 2018)

---

## 一、知识体系思维导图

```text
Kubernetes 核心抽象
│
├─► Pod (最小调度单元)
│   ├─ 共享 Namespace: Network (IP), IPC, UTS
│   ├─ 共享存储: Volumes (emptyDir, hostPath, PVC)
│   ├─ 生命周期: Pending → Running → Succeeded/Failed
│   └─ 设计哲学: "一个 Pod 一个逻辑主机"
│
├─► 工作负载控制器 (Workload Controllers)
│   ├─ Deployment: 无状态应用, ReplicaSet管理, 滚动更新
│   ├─ StatefulSet: 有状态应用, 稳定网络标识, 有序部署/扩缩容
│   ├─ DaemonSet: 每节点一个副本, 日志/监控/网络代理
│   ├─ Job: 批处理, 完成计数 (completions), 并行度 (parallelism)
│   └─ CronJob: 定时触发, Cron表达式调度
│
├─► 服务发现与负载均衡
│   ├─ Service: ClusterIP/NodePort/LoadBalancer/ExternalName
│   ├─ EndpointSlice: 后端 Pod IP 列表的分片抽象
│   └─ DNS: CoreDNS, 服务名 → ClusterIP 解析
│
└─► 声明式 API 与控制器模式
    ├─ Spec (期望状态) vs Status (实际状态)
    ├─ Control Loop: Watch → Diff → Act → Report
    └─ OwnerReference: 级联删除与孤儿依赖管理
```

---

## 二、核心概念的形式化定义

```text
定义 (Pod):
  Pod = ⟨Containers[], SharedNetwork, SharedVolumes, Phase⟩

  SharedNetwork = {
    IP:    集群内唯一虚拟IP (ClusterIP空间)
    Ports: 容器端口映射集合
  }

定义 (Deployment):
  Deployment = ⟨ReplicaSetSpec, Strategy, Selector⟩

  ReplicaSetSpec = {
    replicas: ℕ⁺                // 期望副本数
    template: PodTemplate       // Pod 模板
  }

  RollingUpdateStrategy = {
    maxSurge:       ℕ | percentage     // 更新时可超出的最大副本数
    maxUnavailable: ℕ | percentage     // 更新时允许不可用的最大副本数
  }

定义 (StatefulSet):
  StatefulSet = ⟨ReplicaSetSpec, ServiceName, VolumeClaimTemplates[]⟩

  稳定标识约束:
    ∀i ∈ [0, replicas-1]:
      PodName = ⟨name⟩-⟨ordinal⟩     // web-0, web-1, web-2
      Hostname = PodName
      PVCName  = ⟨volumeClaimTemplate⟩-⟨PodName⟩

定义 (控制器模式):
  ControlLoop = λ(desired, observed):
    if desired ≠ observed:
      action = Reconcile(desired, observed)
      Execute(action)
    Sleep(period)
```

---

## 三、多维矩阵对比

| 特性 | Deployment | StatefulSet | DaemonSet | Job |
|------|-----------|-------------|-----------|-----|
| **状态管理** | 无状态 | 有状态 (稳定标识) | 节点级守护 | 一次性完成 |
| **Pod 命名** | 随机哈希 | 有序序号 (-0, -1) | 节点名派生 | 随机哈希 |
| **存储** | 任意 PVC | 独立 PVC 模板/ Pod | hostPath 或 PVC | 可选临时存储 |
| **更新策略** | RollingUpdate / Recreate | RollingPartition | RollingUpdate | 不适用 |
| **副本数来源** | replicas 字段 | replicas 字段 | 节点数 | completions |
| **典型场景** | Web服务, API | 数据库, Kafka, Redis | 日志采集, CNI | 数据迁移, 批处理 |
| **级联删除** | 删除 RS → 删除 Pods | 删除 Pod 需按序 | 节点移除即删除 | TTL 后自动清理 |

---

## 四、权威引用

> **Brendan Burns, et al.** ("Borg, Omega, and Kubernetes", ACM Queue 2016):
> "Kubernetes was designed from the ground up to be a platform for building platforms. Its API is declarative, and its controllers continuously drive the observed state toward the desired state."

> **Kelsey Hightower** (Kubernetes 布道者, Google):
> "Kubernetes does not run containers. It runs Pods. The Pod is the atomic unit of deployment in Kubernetes."

> **Brian Grant** (Kubernetes 联合创建者, Google):
> "The controller pattern in Kubernetes is inspired by the way Google internally managed services with Borg. Watch, Diff, Act — this loop is the heart of the system."

---

## 五、工程实践与代码示例

**Deployment 声明式配置:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.25
        ports:
        - containerPort: 80
```

**StatefulSet 的有序部署保证:**

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  serviceName: "nginx"
  replicas: 3
  podManagementPolicy: OrderedReady  # 默认: 顺序创建/逆序删除
  volumeClaimTemplates:
  - metadata:
      name: www
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 1Gi
```

---

## 六、批判性总结

Kubernetes 的 Pod 抽象是其最精妙的设计决策之一：通过强制共享网络命名空间，它将"逻辑主机"的概念从物理机迁移到了容器组层面，使得 Sidecar 模式（如 Istio Envoy、日志采集器）得以优雅实现。然而，这一设计也带来了耦合性——同一 Pod 内的容器必须共置 (co-locate)，无法独立扩缩容。

Deployment 的滚动更新机制看似简单，实则暗藏复杂性：maxSurge 和 maxUnavailable 的百分比计算在 replicas 较小时（如 2 个副本）会产生非直觉行为——设置 maxUnavailable=25% 实际效果等同于 maxUnavailable=0（向上取整）。StatefulSet 的有序部署和持久化存储设计解决了有状态服务的编排问题，但其 Pod 重建时的 DNS 缓存漂移和 PVC 残留清理仍是运维陷阱。

更深层的问题是：Kubernetes API 的声明式模型虽然优雅，但其**eventual consistency**在脑裂 (split-brain) 场景下（如 etcd 网络分区）可能导致控制器行为失控。2024-2026 年的趋势是引入 **systemd-sysext** 和 **Image-Based Updates**（如 Flatcar、Bottlerocket），将声明式哲学从应用层下沉到操作系统层，但 Kubernetes 控制平面的单点复杂性（etcd + apiserver + scheduler + controller-manager）并未得到根本解决。
