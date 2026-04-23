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


---

## 七、概念属性关系网络

### 7.1 核心概念关系表

| 概念A | 关系类型 | 概念B | 关系说明 |
|-------|----------|-------|----------|
| PV | 供应 -> | 存储资源 | 集群级存储卷，由管理员或动态供应创建 |
| PVC | 请求 -> | PV | 用户级存储请求，绑定到匹配的 PV |
| StorageClass | 模板 -> | 动态供应 | provisioner + parameters + reclaimPolicy |
| CSI | 规范 -> | 存储驱动 | 容器存储接口，解耦核心与后端 |
| VolumeSnapshot | 捕获 -> | PV 状态 | 时间点快照，由 SnapshotClass 管理 |
| AccessMode | 约束 -> | PV/PVC | RWO/RWX/ROX 的并发访问语义 |
| ReclaimPolicy | 决定 -> | PV 生命周期 | Retain/Recycle/Delete |
| VolumeBindingMode | 控制 -> | 调度时机 | Immediate vs WaitForFirstConsumer |
| TopoLVM | 管理 -> | 本地存储 | LVM 本地卷与拓扑感知调度 |
| Longhorn | 复制 -> | 块存储 | 分布式块存储，提供副本机制 |

### 7.2 ASCII拓扑图

```text
Kubernetes 存储请求绑定流程
===========================================================

        用户提交 PVC
              |
              v
       +-------------+
       |    PVC      |
       | (100Gi,     |
       |  RWO,       |
       |  fast-ssd)  |
       +------+------+
              |
              v
       +-------------+
       | StorageClass|
       | (fast-ssd)  |
       | provisioner:|
       | csi-driver  |
       +------+------+
              |
              v
       +-------------+
       |  CSI Driver |
       | (外部供应商) |
       +------+------+
              |
              v
       +-------------+
       |     PV      |
       | (自动创建)   |
       +------+------+
              |
              v
       +-------------+
       |   绑定成功   |
       | PVC <-> PV  |
       +-------------+

CSI Sidecar 架构
===========================================================

       +------------------------------------------+
       |          Kubernetes Control Plane         |
       |  (API Server / attach-detach controller)  |
       +--------------------+---------------------+
                            |
                            v
       +------------------------------------------+
       |  external-provisioner | external-attacher  |
       |  external-resizer     | external-snapshotter|
       |  node-driver-registrar|                    |
       +----------+----------+-----------+----------+
                  |                      |
                  v                      v
       +-------------------+  +-------------------+
       |  CSI Controller     |  |  CSI Node Plugin  |
       |  (StatefulSet)      |  |  (DaemonSet)      |
       +----------+----------+  +---------+---------+
                  |                      |
                  v                      v
       +-------------------+  +-------------------+
       |  存储后端            |  |  节点挂载操作      |
       |  (Ceph/AWS/GCP)     |  |  (mount/umount)   |
       +-------------------+  +-------------------+

===========================================================
```

### 7.3 形式化映射

设存储系统为六元组 **ST = (V, C, S, B, A, R)**，其中：

- **V** = 卷集合 {v1, v2, ...}，每个卷具有容量 cap(v) 和模式 mode(v)
- **C** = 声明集合 {pvc1, pvc2, ...}，每个 PVC 具有请求 req(pvc) = (size, access_mode, storage_class)
- **S** = 存储类集合 {sc1, sc2, ...}，每个类具有供应器 provisioner(sc) 和参数 params(sc)
- **B** = 绑定关系 B: PVC -> PV，满足 match(pvc, pv) = True
- **A** = 访问模式 A = {ReadWriteOnce, ReadOnlyMany, ReadWriteMany}
- **R** = 回收策略 R = {Retain, Delete, Recycle}

绑定约束形式化为：
forall pvc in PVCs, exists pv in PVs, bind(pvc, pv) ->
  size(pv) >= size(pvc) and access_mode(pv) superset access_mode(pvc) and storage_class(pv) = storage_class(pvc)

---

## 八、形式化推理链

**公理 1（容量守恒）**：绑定的 PV 容量必须不小于 PVC 请求容量。
forall (pvc, pv) in Bindings, cap(pv) >= req_size(pvc)

**公理 2（访问模式兼容性）**：PV 的访问模式必须覆盖 PVC 的请求模式。
forall (pvc, pv) in Bindings, mode(pvc) in modes(pv)

**引理 1（动态供应原子性）**：CSI 动态供应在 PVC 创建时触发，PV 的创建与绑定是原子操作（由 external-provisioner 保证）。
*证明*：external-provisioner watch PVC 的 creation 事件，调用 CSI CreateVolume，成功后创建 PV 对象并设置 PVC 的 volumeName 字段。整个流程在一个控制循环中完成，失败时 PVC 保持 Pending 状态。参见 Kubernetes CSI Spec v1.9。

**引理 2（WaitForFirstConsumer 拓扑感知）**：VolumeBindingMode=WaitForFirstConsumer 时，PV 的创建延迟到 Pod 调度完成后，确保存储拓扑与 Pod 节点一致。
*证明*：调度器在 Pod 调度时选择节点，然后将 volume binding 决策传递给 PV 控制器，PV 控制器根据节点拓扑约束（如可用区）创建 PV。这避免了 Immediate 模式下 PV 与 Pod 节点跨 AZ 的不匹配。参见 Michelle Au (2018) "Volume Topology Awareness", Kubernetes Enhancement Proposal。

**定理 1（存储调度死锁定理）**：在 WaitForFirstConsumer 模式下，若 PVC 的拓扑约束与 Pod 的调度约束冲突（如 PVC 只能在 zone-a，但 Pod 的 AntiAffinity 要求不在 zone-a），则调度将永远失败。
*形式化*：exists pvc, pod, topology(pvc) intersect feasible_nodes(pod) = empty -> scheduling(pvc, pod) diverges
*证明*：Pod 等待 PVC 绑定（以确定调度节点），PVC 等待 Pod 调度（以确定拓扑）。当约束互斥时，形成循环等待，满足死锁的四个必要条件（互斥、占有等待、不可抢占、循环等待）。

**定理 2（快照一致性定理）**：CSI 快照提供崩溃一致性（crash-consistent），而非应用一致性（application-consistent）。
*形式化*：snapshot(PV, t) captures filesystem_state(t) but not application_buffer(t)
*证明*：快照在块层捕获数据，但应用内存中的数据（如数据库缓冲区、事务日志）可能未刷盘。因此数据库快照恢复后可能需要事务回滚或日志重放。参见 Ceph Documentation (2023) "Snapshots and Consistency"。

**推论 1**：本地存储（Local PV）虽然提供了最佳 I/O 性能（绕过网络），但牺牲了高可用性——节点故障时数据不可访问。这是 CAP 定理在存储领域的直接体现：选择 Partition Tolerance + Consistency 时，Availability 必须降级。

**推论 2**：RWO（ReadWriteOnce）的语义存在歧义：在 Kubernetes 中它表示"可被单个节点以读写方式挂载"，而非"可被单个 Pod 挂载"。这意味着一个节点上的多个 Pod 可以共享同一个 RWO 卷（通过 hostPath 或同一节点的多个 Pod），这一设计常导致使用者困惑。

---

## 九、ASCII推理判定树

### 9.1 存储类型选型决策树

```text
Kubernetes 存储选型决策
===========================================================

                      +-------------+
                      | 数据持久性?  |
                      +------+------+
                             |
            +----------------+----------------+
            v                v                v
         临时数据          持久数据          共享数据
            |                |                |
            v                v                v
    +-------------+  +-------------+  +-------------+
    |  emptyDir   |  |    PVC      |  |   RWX PVC   |
    | (Pod生命周期)|  |  + 云盘     |  |  + NFS/     |
    +------+------+  |  + 本地SSD   |  |    CephFS   |
           |         +------+------+  +------+------+
           |                |                |
           v                v                v
    适用:              适用:            适用:
    - 缓存             - 数据库         - 共享文件
    - 临时文件          - 应用数据       - 内容管理
    - Sidecar共享      - 配置持久化      - 多Pod读写

===========================================================
```

### 9.2 CSI 驱动部署决策树

```text
CSI 驱动选型与部署
===========================================================

                      +-------------+
                      | 基础设施环境 |
                      +------+------+
                             |
            +----------------+----------------+
            v                v                v
         公有云            私有云            混合云
            |                |                |
            v                v                v
    +-------------+  +-------------+  +-------------+
    | 云原生CSI    |  | 开源CSI      |  | 多云CSI     |
    | (EBS/PD/    |  | (Ceph/       |  | (Portworx/  |
    |  AzureDisk) |  |  Longhorn)   |  |  Robin)     |
    +------+------+  +------+------+  +------+------+
           |                |                |
           v                v                v
    优势:              优势:            优势:
    - 深度集成          - 成本可控       - 跨云迁移
    - 自动快照          - 代码透明       - 统一接口
    - 托管维护          - 社区支持       - 避免锁定

===========================================================
```

---

## 十、国际权威课程对齐

### 10.1 课程映射

**MIT 6.824: Distributed Systems**

- **Lecture 2**: RPC and Threads -> 对应 CSI 的 gRPC 接口设计与并发处理
- **Lecture 9**: Consistency and Replication -> 对应分布式存储的副本一致性策略
- **Project 2**: Raft -> 对应 etcd 中存储状态的共识管理

**Stanford CS 140: Operating Systems**

- **Lecture 11**: File Systems -> 对应 PV/PVC 的文件系统抽象与挂载语义
- **Lecture 15**: Storage Devices -> 对应块设备、SSD 与存储性能特征
- **Project**: File System -> 对应文件系统实现与持久化保证

**CMU 15-440: Distributed Systems**

- **Lecture 5**: Distributed Storage -> 对应分布式块存储与一致性协议
- **Lecture 12**: Cloud Computing -> 对应云原生存储与动态供应

**Berkeley CS 162: Operating Systems**

- **Lecture 11**: File Systems -> 对应文件系统接口与日志结构
- **Lecture 18**: Distributed Systems -> 对应网络文件系统（NFS）与共享存储

### 10.2 核心参考文献

1. Jie Yu, Saad Ali (2018). Container Storage Interface (CSI) Specification. CNCF. CSI 接口规范原文，定义了存储插件的标准 gRPC 接口。

2. Sage Weil, Scott A. Brandt, Ethan L. Miller, Darrell D. E. Long, Carlos Maltzahn (2006). Ceph: A Scalable, High-Performance Distributed File System. OSDI 2006. Ceph 分布式存储系统的原理论文，Kubernetes Ceph CSI 驱动的理论基础。

3. Sajib Kundu, Raju Rangaswami, et al. (2012). Modeling Virtualized Applications Using Machine Analytical Approach. ACM SIGMETRICS. 存储虚拟化性能建模，对 CSI 驱动的性能优化有指导意义。

4. Michelle Au (2018). Volume Topology Awareness. Kubernetes Enhancement Proposal (KEP-490). 拓扑感知存储的设计提案，解决了跨可用区挂载失败问题。

---

## 十一、深度批判性总结

Kubernetes 的 PV-PVC 分离抽象是基础设施管理中的经典关注点分离实践：PVC 让应用开发者表达我需要什么，PV 和 StorageClass 让集群管理员决定我提供什么。CSI 的 sidecar 插件架构进一步将存储供应商从 Kubernetes 核心代码树中解耦，这是架构上的重大胜利——但它也引入了副作用复杂性：一个完整的 CSI 驱动需要部署 5 个 sidecar（provisioner、attacher、resizer、snapshotter、node-registrar），每个都是独立的容器和 RBAC 主体，部署和维护成本显著增加。

拓扑感知存储（WaitForFirstConsumer）解决了云环境中跨可用区（AZ）挂载失败的问题，但其与调度器的深度耦合导致了调度-存储死锁风险：Pod 等待 PVC 绑定，PVC 等待 Pod 调度，任何一方的状态同步延迟都会导致调度失败。动态扩容虽然便利，但在线扩容的真实语义常被误解——底层块设备扩容后，文件系统扩展（resize2fs/xfs_growfs）仍由 kubelet 触发，某些场景下需要 Pod 重启才能真正生效。

快照（VolumeSnapshot）提供的是崩溃一致性（crash-consistent）而非应用一致性，这意味着数据库等有状态应用在快照前需要执行 fsync 或冻结 I/O。Ceph、Longhorn 等分布式存储在 Kubernetes 上的 CSI 集成已相当成熟，但本地存储（local PV）的高可用难题——节点故障时数据不可访问——至今没有通用解决方案，TopoLVM 和 OpenEBS 的副本机制仍在持续演进。存储领域的终极矛盾是：持久化要求数据与节点解耦，而性能要求数据与计算局部性耦合——Kubernetes 的存储体系在这一矛盾中左右摇摆。
