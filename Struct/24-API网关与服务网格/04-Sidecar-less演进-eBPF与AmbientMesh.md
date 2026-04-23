# Sidecar-less 演进：eBPF 与 Ambient Mesh

> **来源映射**: View/00.md §3.1
> **国际权威参考**: "Cilium and eBPF" (Isovalent), Istio Ambient Mesh Whitepaper, "BPF Performance Tools" (Brendan Gregg)

---

## 一、知识体系思维导图

```text
Sidecar-less 服务网格演进
│
├─► 问题域: Sidecar 模式的代价
│   ├─► 资源开销: 每 Pod 1 个 Envoy → 内存 x2, CPU +30%
│   ├─► 延迟开销: iptables 重定向 + Envoy 处理 → +1-3ms
│   ├─► 生命周期耦合: Sidecar 启动慢影响 Pod Ready
│   ├─► 升级痛苦: 5000+ Pod → 5000+ Envoy 滚动重启
│   └─► 安全边界: Sidecar 与 App 共享网络命名空间
│
├─► 方案一: eBPF (Cilium Service Mesh)
│   ├─► 内核层可编程: 绕过 iptables, socket-level 重定向
│   ├─► 无 Sidecar: 直接在内核处理 L3/L4 策略
│   ├─► Envoy 按需: 仅需要 L7 时启动 per-node 代理
│   ├─► 性能: 延迟接近原生网络
│   └─► 限制: 内核版本要求(5.10+), L7 功能受限
│
├─► 方案二: Istio Ambient Mesh
│   ├─► zTunnel: 每节点 L4 代理(mTLS, 路由, 遥测)
│   ├─► Waypoint Proxy: 按命名空间 L7 代理(Envoy)
│   ├─► 分层安全: zTunnel 自动加密, waypoint 按需策略
│   ├─► HBONE (HTTP-Based Overlay Network): HTTP/2 CONNECT 隧道
│   └─► 零信任: 无需应用感知即获得 mTLS
│
├─► 方案三: 共享代理 (Shared Proxy)
│   ├─► 每节点一个 Envoy / per-node proxy
│   ├─► 降低资源开销但牺牲隔离性
│   └─► Linkerd 的 initial 探索方向
│
└─► 对比与选择
    ├─► eBPF: 极致性能，适合 L4 为主场景
    ├─► Ambient: 功能完整，渐进式 Sidecar-less
    └─► Sidecar: 功能最全，存量系统兼容
```

---

## 二、核心概念的形式化定义

**定义 1 (Sidecar 资源模型)**:
设集群有 $N$ 个 Pod，每个 Pod 的 Sidecar 资源需求为 $\langle cpu_s, mem_s \rangle$:
$$Overhead_{sidecar} = N \cdot (cpu_s + mem_s)$$
当 $N = 10,000, mem_s = 128MB$ 时，仅 Sidecar 内存开销即达 **1.2TB**。

**定义 2 (eBPF socket-level 重定向)**:
$$Redirect_{ebpf}(src, dst) = \begin{cases}
sockops: & \text{建立连接时插入 BPF 程序} \\
sk_msg: & \text{发送路径直接重定向到目标 socket} \\
\end{cases}$$
无需经过 TCP/IP 协议栈完整路径，延迟:
$$Latency_{ebpf} \approx Latency_{direct} + \epsilon, \quad \epsilon < 0.1ms$$

**定义 3 (Ambient Mesh 分层架构)**:
$$Ambient = \langle zTunnel, Waypoint, HBONE \rangle$$
- **zTunnel**: 节点级 L4 代理，$\forall pod \in Node, Traffic(pod) \rightarrow zTunnel$
- **Waypoint**: 服务级 L7 代理，$Waypoint(svc) = \langle policy, routing, observability \rangle$
- **HBONE**: 基于 HTTP/2 CONNECT 的覆盖网络隧道

流量路径:
$$A \rightarrow zTunnel_A \xrightarrow{HBONE} zTunnel_B \rightarrow B \quad (纯 L4)$$
$$A \rightarrow zTunnel_A \xrightarrow{HBONE} Waypoint_X \xrightarrow{HBONE} zTunnel_B \rightarrow B \quad (需 L7)$$

**定义 4 (功能-性能权衡空间)**:
$$Tradeoff = \langle Performance, L7Features, Isolation, Complexity \rangle$$
- Sidecar: $\langle Medium, High, High, Medium \rangle$
- eBPF: $\langle High, Low, Medium, High \rangle$
- Ambient: $\langle High, High, Medium, Medium \rangle$

---

## 三、多维矩阵对比

| 架构模式 | 延迟开销 | 内存开销/Pod | L7 能力 | mTLS 自动 | 升级粒度 | 隔离性 |
|---------|---------|------------|---------|----------|---------|--------|
| **Sidecar** | +1-3 ms | +100-150 MB | **完整** | 是 | Pod 级 | **强(命名空间隔离)** |
| **eBPF (Cilium)** | **+0.1 ms** | **~0** | 有限 | 是 | 节点级 | 中(共享内核) |
| **Ambient (zTunnel)** | **+0.5 ms** | **~0** | waypoint 提供 | **是** | 节点级(zT) + 命名空间级(wp) | 中 |
| **Per-Node Proxy** | +0.5 ms | 分摊 | 完整 | 是 | 节点级 | 弱(多租户风险) |

| 技术方案 | 内核要求 | 开发语言 | 控制平面 | 与 K8s 集成 | 成熟度(2026) |
|---------|---------|---------|---------|-------------|-------------|
| **Cilium + Envoy** | Linux 5.10+ | eBPF/C/Go | Cilium Operator | CNI 原生 | 生产可用 |
| **Istio Ambient** | 无特殊要求 | Rust(zT)/C++(wp) | Istiod | Istio 原生 | **生产可用** |
| **Waypoint-only** | 无 | C++ | Istiod | Istio | 实验性 |

| 场景 | 推荐方案 | 理由 |
|------|---------|------|
| **纯 L4 流量加密** | eBPF / zTunnel | 无额外代理开销 |
| **需要完整 L7 策略** | Ambient / Sidecar | Waypoint 提供完整 Envoy 能力 |
| **超大规模(10万+ Pod)** | Ambient | 避免 10万+ Sidecar 资源开销 |
| **严格多租户隔离** | Sidecar | 最强的安全边界 |
| **边缘/IoT 设备** | eBPF | 资源受限环境下的最佳选择 |

---

## 四、权威引用

> **Thomas Graf** (Cilium 作者, eBPF Co-maintainer, KubeCon 2023):
> "eBPF allows us to implement service mesh functionality at the kernel layer, reducing latency to near-native levels."

> **Istio 项目** ("Introducing Ambient Mesh", 2022):
> "Ambient mesh splits the data plane into two layers: a secure overlay (zTunnel) for L4 handling, and waypoints for L7 processing."

> **Brendan Gregg** ("BPF Performance Tools", Addison-Wesley, 2020):
> "eBPF is not just a technology; it's a fundamental shift in how we instrument and program the Linux kernel."

---

## 五、工程实践与代码示例

```yaml
# Istio Ambient Mesh: 将命名空间加入 Ambient 模式
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    istio.io/dataplane-mode: ambient  # 启用 zTunnel
---
# 为 reviews 服务部署 L7 Waypoint Proxy
apiVersion: gateway.networking.k8s.io/v1beta1
kind: Gateway
metadata:
  name: reviews-waypoint
  namespace: production
spec:
  gatewayClassName: istio-waypoint
  listeners:
    - name: mesh
      protocol: HBONE
      port: 15008
---
# 将 reviews 服务的流量路由到 Waypoint
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: reviews-waypoint
  namespace: production
spec:
  host: reviews
  trafficPolicy:
    tunnel:
      protocol: CONNECT
      targetPort: 15008
```

```c
// eBPF socket 重定向伪代码 (Cilium 核心原理)
SEC("sockops")
int bpf_sockmap(struct bpf_sock_ops *skops) {
    __u32 op = skops->op;

    if (op == BPF_SOCK_OPS_TCP_CONNECT_CB ||
        op == BPF_SOCK_OPS_TCP_LISTEN_CB) {
        // 将 socket 注册到 sockhash map
        __u32 key = skops->remote_ip4;
        bpf_sock_hash_update(skops, &sock_ops_map, &key, BPF_ANY);
    }
    return 0;
}

SEC("sk_msg")
int bpf_redir(struct sk_msg_md *msg) {
    __u32 key = msg->remote_ip4;
    // 直接重定向到目标 socket，绕过 TCP/IP 栈
    bpf_msg_redirect_hash(msg, &sock_ops_map, &key, BPF_F_INGRESS);
    return SK_PASS;
}
```

---

## 六、批判性总结

Sidecar-less 运动并非对服务网格的否定，而是对其**实现方式**的重新思考。Sidecar 模式的根本问题在于它将"功能"与"部署单元"过度耦合——为了获得 L7 能力，每个 Pod 都必须承担完整 Envoy 的资源代价，即使其中 80% 的流量仅需 L4 处理。

Istio Ambient Mesh 的分层架构（zTunnel + Waypoint）提供了一个精妙的解决方案：**按需求分层付费**。zTunnel 作为每节点常驻组件，以轻量级 Rust 实现处理 L4 的加密和路由；Waypoints 作为按需部署的 L7 代理，仅在需要复杂流量策略的命名空间中存在。这与操作系统中"微内核 + 可加载模块"的设计哲学异曲同工。

eBPF 代表了更激进的优化方向：将网络处理下沉到内核层，完全消除用户态代理的开销。但 eBPF 的 Verifier（内核代码校验器）对程序复杂度和循环有严格限制，这使得某些高级 L7 功能（如复杂的 WASM 插件）在内核层难以实现。Cilium 的折中方案是 **eBPF for L4 + per-node Envoy for L7**，但这又回到了代理模式的某种变体。

一个尚未充分讨论的维度是**可观测性的代价**。Sidecar 模式为每个 Pod 提供了独立的 Envoy Admin 接口和指标端点，而 Ambient 的 zTunnel 是节点级共享的，这使得排查特定 Pod 的网络问题变得更加复杂。当系统从"每个 Pod 一个代理"演变为"每个节点一个代理"时，故障隔离的粒度从 Pod 级降级到了节点级——这是性能优化的隐性成本。

---

## 七、深度增强：概念属性关系网络

### 7.1 核心概念关系表

| 概念 A | 关系 | 概念 B | 说明 |
|--------|------|--------|------|
| Sidecar | 被替代 | zTunnel | 每节点 L4 代理替代每 Pod Sidecar |
| Waypoint | 按需 | L7 代理 | 仅需要 L7 策略时部署 |
| HBONE | 实现 | 覆盖网络 | HTTP/2 CONNECT 隧道 |
| eBPF | 替代 | iptables | 内核层 socket 重定向 |
| Cilium | 使用 | eBPF | 内核层 L4 策略执行 |
| Verifier | 限制 | eBPF 复杂度 | 内核代码校验器限制循环和复杂度 |

### 7.2 ASCII 拓扑图：Sidecar-less 分层架构

```text
              Sidecar-less 分层架构对比
                          |
     +--------------------+--------------------+
     |                                         |
  Sidecar 模式                           Ambient 模式
     |                                         |
  +--+--+                                +-----+-----+
  | Pod |                                |   Node    |
  |App  |                                | zTunnel   |
  |Envoy|                                | (L4)      |
  +--+--+                                +-----+-----+
     |                                         |
     v                                         v
  +--+--+          +--------+           +-----+-----+
  | Pod |          |  Pod   |           | Waypoint  |
  |App  |          |App     |           | (L7, Envoy|
  |Envoy|          |Envoy   |           | 按需)      |
  +--+--+          +--------+           +-----+-----+
     |                                         |
     v                                         v
  资源: N*Mem_Envoy                    资源: N_node*Mem_zT + N_svc*Mem_wp
  延迟: +1-3ms                         延迟: +0.5ms (L4), +1-2ms (L7)
```

### 7.3 形式化映射

Sidecar 资源模型：
Overhead_sidecar = N * (cpu_s + mem_s)

Ambient 资源模型：
Overhead_ambient = N_nodes * (cpu_zt + mem_zt) + N_waypoints * (cpu_wp + mem_wp)

eBPF 重定向：
Latency_eBPF ~~ Latency_direct + epsilon, epsilon < 0.1ms

功能-性能权衡空间：
Tradeoff = <Performance, L7Features, Isolation, Complexity>
- Sidecar: <Medium, High, High, Medium>
- eBPF: <High, Low, Medium, High>
- Ambient: <High, High, Medium, Medium>

---

## 八、深度增强：形式化推理链

### 8.1 公理

**公理 A1（Sidecar 资源线性增长公理）**
Overhead_sidecar ~ O(N_pods)

**公理 A2（eBPF 延迟逼近公理）**
Latency_eBPF -> Latency_direct 当 N_redirects -> infinity

**公理 A3（分层必要公理）** [Istio Ambient, 2022]
forall traffic: NeedL7(traffic) = false => Waypoint(traffic) = null

### 8.2 引理

**引理 L1（Ambient 资源节省）**
设 L4 流量比例为 p，节点数为 M << N_pods
SavedResources = p * N_pods * MEM_envoy - M * MEM_zt
当 N_pods = 10000, M = 100, p = 0.8 时，节省约 0.8TB 内存。

**引理 L2（eBPF Verifier 限制）**
forall prog: eBPF:
Verifier(prog) = pass => complexity(prog) < THRESHOLD
且 no_unbounded_loops(prog) = true

### 8.3 定理

**定理 T1（Ambient 延迟分层）**
纯 L4 路径：T = T_direct + T_zTunnel ~ T_direct + 0.5ms
需要 L7 路径：T = T_direct + T_zTunnel + T_waypoint ~ T_direct + 1.5ms
仍优于 Sidecar 的 T_direct + 1-3ms

**定理 T2（eBPF L7 功能不完备性）**
exists f in AdvancedL7: Implementable(eBPF, f) = false
例如：复杂 WASM 插件、深度包检测中的正则回溯。

**定理 T3（可观测性粒度降级）**
Sidecar 可观测粒度 = Pod 级
Ambient zTunnel 可观测粒度 = Node 级
Granularity_loss = Pod -> Node

### 8.4 推论

**推论 C1**：Cilium 的折中方案：
eBPF for L4 + per-node Envoy for L7
Latency = Latency_eBPF + Latency_envoy_node
Isolation = Medium (共享节点代理)

**推论 C2**：超大规模集群（10万+ Pod）的 Ambient 优势：
Overhead_ratio = Overhead_ambient / Overhead_sidecar ~ M / N_pods -> 0
当 M << N_pods 时，资源节省趋近于 p。

---

## 九、深度增强：ASCII 推理判定树

### 9.1 决策树：Sidecar-less 方案选型

```text
                    [开始]
                      |
              +-------+-------+
              |               |
        [内核版本?]      [L7需求比例?]
              |               |
      +---+---+---+       +---+---+
      |   |   |   |       |       |
    <5.10 5.10+ 任意   任意   <20%   >80%
      |   |   |   |       |       |
      v   v   v   v       v       v
   [不可  [eBPF  [Ambient [Ambient [eBPF [Ambient
    用]   优先]  Mesh]   Mesh]   优先] 或
                                      Sidecar]
```

### 9.2 决策树：可观测性与性能权衡

```text
                    [开始]
                      |
              +-------+-------+
              |               |
        [排查粒度?]      [延迟要求?]
              |               |
      +---+---+---+       +---+---+
      |   |   |   |       |       |
    Pod  服务  节点  集群   <1ms    <0.5ms
    级   级   级   级      |       |
      |   |   |   |       |       |
      v   v   v   v       v       v
   [Sidecar [Ambient [eBPF   [eBPF  [eBPF
         ]    +wp]    only]   only]  only]
```

---

## 十、深度增强：国际权威课程对齐

### 10.1 MIT 6.824: Distributed Systems

| Lecture | 主题 | 映射 |
|---------|------|------|
| Lec 4 | Primary-Backup | 节点级代理 vs Pod 级代理 |
| Lec 6 | Raft | 控制平面高可用 |

### 10.2 Stanford CS 244b: Advanced Topics in Networking

| Lecture | 主题 | 映射 |
|---------|------|------|
| eBPF & Kernel Networking | 内核可编程网络 | eBPF socket 重定向 |
| Network Virtualization | 网络虚拟化 | Cilium 与容器网络 |

### 10.3 CMU 15-440: Distributed Systems

| 模块 | 映射 | Project |
|------|------|---------|
| Virtualization | 容器与内核虚拟化 | eBPF 程序开发 |
| Security | 内核安全与隔离 | Cilium 网络策略 |

### 10.4 Berkeley CS 162: Operating Systems

| Lecture | 主题 | 映射 |
|---------|------|------|
| Lec 12 | The Kernel | 内核可编程性与 eBPF |
| Lec 26 | Security | 内核层安全策略执行 |

### 10.5 核心参考文献

1. **Graf, T.** (2023). Cilium and eBPF: Rethinking Networking and Security. KubeCon.
2. **Istio Project.** (2022). Introducing Ambient Mesh. istio.io.
3. **Gregg, B.** (2020). *BPF Performance Tools*. Addison-Wesley. —— eBPF 技术权威著作。
4. **McCanne, S., & Jacobson, V.** (1993). The BSD Packet Filter. *USENIX Winter*. —— BPF 原始论文。

---

## 十一、批判性总结（深度增强版）

Sidecar-less 运动并非对服务网格价值的否定，而是对其**实现方式**的重新思考。Sidecar 模式的根本问题在于将功能与部署单元过度耦合——为了获得 L7 能力，每个 Pod 都必须承担完整 Envoy 的资源代价，即使其中 80% 的流量仅需 L4 处理。这类似于操作系统发展中从单体内核到微内核的演进：不是所有功能都需要放在最高特权级，按需求分层才是资源效率的最优解。

Istio Ambient Mesh 的分层架构（zTunnel + Waypoint）提供了一个精妙的解决方案：按需求分层付费。zTunnel 作为每节点常驻组件，以轻量级 Rust 实现处理 L4 的加密和路由；Waypoints 作为按需部署的 L7 代理，仅在需要复杂流量策略的命名空间中存在。这与操作系统中微内核 + 可加载模块的设计哲学异曲同工——核心功能常驻，扩展功能按需加载。

eBPF 代表了更激进的优化方向：将网络处理下沉到内核层，完全消除用户态代理的开销。但 eBPF 的 Verifier（内核代码校验器）对程序复杂度和循环有严格限制，这使得某些高级 L7 功能（如复杂的 WASM 插件）在内核层难以实现。Cilium 的折中方案是 eBPF for L4 + per-node Envoy for L7，但这又回到了代理模式的某种变体。这揭示了一个深层原理：**功能完整性（Turing-complete expressiveness）与执行环境安全性（sandboxing）之间存在根本张力**。

一个尚未充分讨论的维度是可观测性的代价。Sidecar 模式为每个 Pod 提供了独立的 Envoy Admin 接口和指标端点，而 Ambient 的 zTunnel 是节点级共享的，这使得排查特定 Pod 的网络问题变得更加复杂。当系统从每个 Pod 一个代理演变为每个节点一个代理时，故障隔离的粒度从 Pod 级降级到了节点级——这是性能优化的隐性成本。在可观测性工具（如 Cilium Hubble）成熟之前，这一降级可能成为生产环境故障排查的痛点。
