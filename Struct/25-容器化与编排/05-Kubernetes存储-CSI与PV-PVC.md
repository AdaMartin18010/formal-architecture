# Kubernetes 存储：CSI 与 PV-PVC 模型

> **来源映射**: View/00.md §3.1, Struct/25-容器化与编排/00-总览-容器运行时与编排系统的形式化.md
> **国际权威参考**: CSI Specification v1.9 (CNCF), Kubernetes Storage SIG Docs, "Container Storage Interface" (KEP-178), "Dynamic Provisioning and Storage Classes in Kubernetes"

---

## 一、知识体系思维导图

```text
Kubernetes 存储体系
│
├─► 核心抽象
│   ├─ PV (PersistentVolume): 集群级存储资源, 由管理员或动态供应创建
│   ├─ PVC (PersistentVolumeClaim): 用户级存储请求, 绑定到 PV
│   ├─ StorageClass: 存储模板, provisioner + parameters + reclaimPolicy
│   └─ VolumeSnapshot: 时间点快照, SnapshotClass 管理
│
├─► CSI (Container Storage Interface)
│   ├─ 架构:  sidecar 模式 (node-driver-registrar, external-provisioner,
│   │                    external-attacher, external-resizer, external-snapshotter)
│   ├─ 接口规范: Identity, Controller, Node 服务
│   ├─ 生命周期: CreateVolume → ControllerPublish → NodeStage → NodePublish
│   │           → NodeUnpublish → NodeUnstage → ControllerUnpublish → DeleteVolume
│   └─ 拓扑感知: AccessibleTopology, VolumeScheduling
│
├─► 访问模式与回收策略
│   ├─ AccessModes: RWO (单节点读写), ROX (多节点只读),
│   │               RWX (多节点读写), RWOP (单Pod读写, v1.22+)
│   ├─ ReclaimPolicy: Retain (保留), Delete (删除), Recycle (已废弃)
│   └─ VolumeBindingMode: Immediate / WaitForFirstConsumer
│
└─► 高级特性
    ├─ 动态扩容: VolumeExpansion (在线/离线), Resizer sidecar
    ├─ 快照与恢复: VolumeSnapshot → SnapshotContent → restore PVC
    ├─ 克隆: VolumeDataSource (PVC→PVC 克隆)
    └─ 本地存储: local PV, OpenEBS, TopoLVM
```

---

## 二、核心概念的形式化定义

```text
定义 (PV-PVC 绑定):
  PVC = ⟨capacity, accessModes, storageClassName, selector⟩
  PV  = ⟨capacity, accessModes, storageClassName, phase, claimRef⟩

  绑定条件 (Bindable):
    Bindable(PVC, PV) ↔
      PV.capacity ≥ PVC.capacity ∧
      PV.accessModes ⊇ PVC.accessModes ∧
      (PVC.storageClassName = PV.storageClassName ∨ PV.storageClassName = "") ∧
      PV.phase = Available

  绑定操作:
    Bind(PVC, PV) → PV.phase = Bound ∧ PV.claimRef = PVC

定义 (动态供应 Dynamic Provisioning):
  触发条件:
    PVC.storageClassName ≠ "" ∧ ∄ PV: Bindable(PVC, PV)

  供应流程:
    Provisioner(SC.provisioner, PVC.parameters) → PV
    → 自动执行 Bind(PVC, PV)

定义 (CSI 拓扑约束):
  AccessibleTopology = {labelSelector₁, labelSelector₂, ...}

  调度约束:
    Schedule(Pod, PVC) → Pod.node.labels ∈ PV.accessibleTopology
    (当 VolumeBindingMode = WaitForFirstConsumer)

定义 (扩容):
  Expansion(PV, newCapacity) → {
    Online:  PV.status.phase = Bound ∧ 文件系统在线扩展
    Offline: PV.status.phase = Released ∧ 离线扩展
  }
```

---

## 三、多维矩阵对比

| 存储类型 | 访问模式 | 延迟 | 可用性 | 典型用途 | 代表实现 |
|---------|---------|------|--------|---------|---------|
| **云盘** | RWO | 低 | 高 (多副本) | 数据库, 事务存储 | AWS EBS, Azure Disk |
| **网络文件系统** | RWX | 中 | 中 | 共享内容, 配置 | NFS, EFS, Azure Files |
| **对象存储** | 协议限制 | 中-高 | 极高 | 备份, 静态资源 | S3, GCS, MinIO |
| **本地 SSD** | RWO | 极低 | 低 (节点绑定) | 缓存, 临时计算 | local PV, TopoLVM |
| **分布式块存储** | RWO/RWX | 低-中 | 高 | 通用持久化 | Ceph RBD, Longhorn |
| **分布式文件系统** | RWX | 中 | 高 | AI/ML, 大数据 | CephFS, GlusterFS |

| CSI 特性 | 支持版本 | 关键能力 | 限制 |
|---------|---------|---------|------|
| **动态供应** | v0.3+ | 按需创建 PV | 依赖外部 Provisioner |
| **扩容** | v1.2+ | 在线/离线扩展 | 并非所有驱动支持在线 |
| **快照** | v1.2+ | 时间点一致性 | 崩溃一致性非应用一致性 |
| **克隆** | v1.3+ | PVC→PVC 快速复制 | 同StorageClass约束 |
| **拓扑感知** | v1.2+ | 区域/节点亲和 | 增加调度复杂度 |
| **原始块设备** | v1.11+ | 绕过文件系统 | 需应用自行管理 |

---

## 四、权威引用

> **Kubernetes Storage SIG** (CSI v1.9 Specification):
> "CSI was designed to provide a universal standard for exposing block and file storage systems to container orchestrators."

> **Saad Ali** (Google, Kubernetes Storage SIG Lead, KEP-178):
> "Before CSI, every storage vendor had to write an in-tree volume plugin. CSI moves storage innovation out of the Kubernetes release cycle."

> **Michelle Au & Hemant Kumar** ("Kubernetes Storage: PVs, PVCs, and the CSI", KubeCon 2020):
> "WaitForFirstConsumer binding mode is critical for topology-aware storage. It delays PV provisioning until the pod is scheduled, ensuring the volume is created in the same zone."

---

## 五、工程实践与代码示例

**StorageClass 动态供应配置:**

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: ebs.csi.aws.com
volumeBindingMode: WaitForFirstConsumer  # 拓扑感知关键
allowVolumeExpansion: true
parameters:
  type: gp3
  encrypted: "true"
reclaimPolicy: Delete
```

**PVC 请求与 Pod 挂载:**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-data
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 100Gi
---
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: postgres
    image: postgres:16
    volumeMounts:
    - name: data
      mountPath: /var/lib/postgresql/data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: postgres-data
```

**VolumeSnapshot 示例:**

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: postgres-snap
spec:
  volumeSnapshotClassName: csi-snapclass
  source:
    persistentVolumeClaimName: postgres-data
```

---

## 六、批判性总结

Kubernetes 的 PV-PVC 分离抽象是基础设施管理中的经典**关注点分离**实践：PVC 让应用开发者表达"我需要什么"，PV 和 StorageClass 让集群管理员决定"我提供什么"。CSI 的 sidecar 插件架构进一步将存储供应商从 Kubernetes 核心代码树中解耦，这是架构上的重大胜利——但它也引入了**副作用复杂性**：一个完整的 CSI 驱动需要部署 5 个 sidecar（provisioner、attacher、resizer、snapshotter、node-registrar），每个都是独立的容器和 RBAC 主体，部署和维护成本显著增加。

拓扑感知存储（WaitForFirstConsumer）解决了云环境中跨可用区 (AZ) 挂载失败的问题，但其与调度器的深度耦合导致了**调度-存储死锁**风险：Pod 等待 PVC 绑定，PVC 等待 Pod 调度，任何一方的状态同步延迟都会导致调度失败。动态扩容虽然便利，但"在线扩容"的真实语义常被误解——底层块设备扩容后，文件系统扩展（resize2fs/xfs_growfs）仍由 kubelet 触发，某些场景下需要 Pod 重启才能真正生效。

快照 (VolumeSnapshot) 提供的是**崩溃一致性 (crash-consistent)** 而非应用一致性，这意味着数据库等有状态应用在快照前需要执行 `fsync` 或冻结 I/O。Ceph、Longhorn 等分布式存储在 Kubernetes 上的 CSI 集成已相当成熟，但本地存储（local PV）的高可用难题——节点故障时数据不可访问——至今没有通用解决方案，TopoLVM 和 OpenEBS 的副本机制仍在持续演进。存储领域的终极矛盾是：**持久化要求数据与节点解耦，而性能要求数据与计算局部性耦合**——Kubernetes 的存储体系在这一矛盾中左右摇摆。
