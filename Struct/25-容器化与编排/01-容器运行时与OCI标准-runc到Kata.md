# 容器运行时与 OCI 标准：从 runc 到 Kata Containers

> **来源映射**: View/00.md §3.1, Struct/25-容器化与编排/00-总览-容器运行时与编排系统的形式化.md
> **国际权威参考**: OCI Runtime Spec v1.1, Docker Runtime (Solomon Hykes, 2013), Kata Containers (Hyper.sh, 2017), gVisor (Google, 2018), "Linux Kernel Documentation: namespaces(7), cgroups(7)"

---

## 一、知识体系思维导图

```text
容器运行时与OCI标准
│
├─► OCI (Open Container Initiative)
│   ├─ runtime-spec: runc, crun, kata-runtime, gVisor-runsc
│   ├─ image-spec: manifest, config, layers, content-addressable
│   └─ distribution-spec: Registry API v2, push/pull
│
├─► Linux 隔离机制
│   ├─ Namespaces: PID, NET, MNT, UTS, IPC, USER, CGROUP, TIME
│   ├─ Cgroups v1/v2: CPU (shares/quota/period), Memory (limit/swap), IO, Pids
│   ├─ Capabilities: CAP_NET_ADMIN, CAP_SYS_PTRACE, 细粒度权限
│   └─ Seccomp / AppArmor / SELinux: 系统调用过滤与MAC
│
├─► 联合文件系统
│   ├─ OverlayFS: lowerdir + upperdir + workdir = merged
│   ├─ AUFS (legacy): Docker 早期默认
│   └─ 写时复制 (COW): 分层镜像的物理基础
│
└─► 安全容器 (Secure Containers)
    ├─ Kata Containers: QEMU/KVM microVM, kata-agent, 轻量VM级隔离
    ├─ gVisor: 用户态内核 (Sentry), ptrace/seccomp拦截, 独立TCP/IP栈
    └─ Firecracker: AWS microVM, 125ms冷启动, 内存开销 < 5MiB
```

---

## 二、核心概念的形式化定义

```text
定义 (容器运行时):
  Runtime = ⟨Namespace, Cgroup, RootFS, Seccomp, Capabilities⟩

  Namespace 隔离函数:
    ∀ ns ∈ {PID, NET, MNT, UTS, IPC, USER, CGROUP}:
      isolate_ns(process, ns) → 进程在 ns 空间中的独立视图

  Cgroup 限制函数 (v2 unified hierarchy):
    limit(cgroup, resource, value) → ∀p ∈ cgroup.processes:
      consumption(p, resource) ≤ value

定义 (OverlayFS 挂载):
  OverlayFS = ⟨LowerDir[], UpperDir, WorkDir, MergedDir⟩

  读取解析规则:
    read(path) = {
      UpperDir/path  if ∃ UpperDir/path
      LowerDirᵢ/path if ∃ LowerDirᵢ/path ∧ ∄ UpperDir/path
      ENOENT         otherwise
    }

定义 (安全容器)
  SecureContainer = {
    Kata:   VM_isolation(VM, Container) ∧ VM.start_time < 1s
    gVisor: Userspace_kernel(Sentry) ∧ syscall_intercept_rate > 0.95
    Firecracker: microVM(mem < 32MiB, vCPU ≤ 2, boot < 150ms)
  }
```

---

## 三、多维矩阵对比

| 维度 | runc (Native) | Kata Containers | gVisor | Firecracker |
|------|---------------|-----------------|--------|-------------|
| **隔离级别** | 进程级 (Namespace) | VM级 (KVM) | 用户态内核 | VM级 (KVM) |
| **启动延迟** | ~100ms | ~500ms-1s | ~150ms | ~125ms |
| **内存开销** | ~0 (共享内核) | ~128MB/VM | ~15MB/Sentry | ~5MB/VM |
| **系统调用路径** | 直接 → Host Kernel | 直接 → Guest Kernel | 拦截 → Sentry | 直接 → Guest Kernel |
| **适用场景** | 可信工作负载 | 不可信/多租户 | 不可信/沙箱 | Serverless/FaaS |
| **OCI兼容** | 原生 | kata-runtime | runsc | containerd/firecracker |
| **网络栈** | Host内核 | Guest内核 | Sentry用户态 | Guest内核 |

---

## 四、权威引用

> **Solomon Hykes** (Docker 创始人, dotCloud, 2013):
> "What Docker does is it abstracts away the complexity of running applications in containers."

> **Open Containers Initiative** (Linux Foundation, runtime-spec v1.1, 2023):
> "The OCI Runtime Spec defines the configuration, execution environment, and lifecycle of a container."

> **Samuel Ortiz & Sebastien Boeuf** (Kata Containers 核心维护者, USENIX ATC 2018):
> "Kata Containers combine the speed of containers with the security of VMs by using lightweight virtual machines."

> **Google gVisor Team** (2018):
> "gVisor intercepts application system calls and acts as the guest kernel, without the need for fixed resource allocations."

---

## 五、工程实践与代码示例

**runc 创建容器的核心流程:**

```bash
# 1. 创建 rootfs
mkdir -p /mycontainer/rootfs
# 2. 生成 OCI runtime spec
runc spec --rootless
# 3. 运行容器
runc run mycontainer
```

**OverlayFS 挂载示例:**

```bash
mount -t overlay overlay \
  -o lowerdir=/image_layer1:/image_layer2,\
     upperdir=/container_diff,\
     workdir=/work \
  /merged
```

**Kata Containers 与 containerd 集成:**

```toml
# /etc/containerd/config.toml
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.kata]
  runtime_type = "io.containerd.kata.v2"
```

---

## 六、批判性总结

容器运行时的演进本质上是对**隔离性-性能-兼容性**三角权衡的持续探索。runc 利用 Linux Namespace 和 Cgroup 实现了极致的启动速度和零内存开销，但其共享内核模型无法防御内核漏洞（如 CVE-2022-0847 DirtyPipe）。Kata Containers 通过轻量 VM 提供了强隔离，但每个 Pod 引入 ~128MB 内存开销和数百毫秒启动延迟，在 Serverless 高密度场景下难以承受。gVisor 试图走中间路线——用户态内核拦截系统调用，但其兼容性问题（尤其是复杂网络/存储 syscall）长期被诟病，且性能损失在某些场景可达 50% 以上。

Cgroups v2 的统一层级设计改善了 v1 中控制器碎片化的问题，但容器生态的迁移进展缓慢。OverlayFS 的 inode 耗尽和性能抖动问题在大规模镜像场景下仍是运维痛点。未来的趋势是**基于 eBPF 的安全容器**（如 Continuum、Sherlock）——利用内核可编程性在保持原生性能的同时实现系统调用过滤和行为监控，这或许能打破"隔离必牺牲性能"的魔咒。
