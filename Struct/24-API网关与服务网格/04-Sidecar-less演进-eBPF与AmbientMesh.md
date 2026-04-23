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
