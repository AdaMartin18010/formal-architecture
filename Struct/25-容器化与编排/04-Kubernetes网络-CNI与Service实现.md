# Kubernetes 网络：CNI 与 Service 实现

> **来源映射**: View/00.md §3.1, Struct/25-容器化与编排/00-总览-容器运行时与编排系统的形式化.md
> **国际权威参考**: CNI Specification v1.0 (CNCF), "A Guide to Kubernetes Networking" (Cilium Docs), "kube-proxy: The Next Generation" (KEP-3458, nftables), "eBPF-based Networking and Observability" (Liz Rice, 2022)

---

## 一、知识体系思维导图

```text
Kubernetes 网络模型
│
├─► 网络设计哲学
│   ├─ 每个 Pod 一个唯一 IP (Pod IP)
│   ├─  Pod 间直接通信, 无需 NAT
│   ├─ 节点与 Pod 双向直接通信
│   └─ 扁平网络空间, 跨节点路由可达
│
├─► CNI (Container Network Interface)
│   ├─ 接口规范: ADD / DEL / CHECK / VERSION
│   ├─ 插件类型:
│   │   ├─ 路由型: Calico (BGP), Cilium (eBPF/xDP)
│   │   ├─ 覆盖型: Flannel (VXLAN), Weave Net
│   │   ├─ SDN型: Canal, Antrea (VMware)
│   │   └─ 云集成: AWS VPC CNI, Azure CNI, GCP VPC
│   └─ IPAM: host-local / dhcp / calico-ipam / cluster-pool
│
├─► Service 实现机制
│   ├─ kube-proxy 模式演进:
│   │   ├─ userspace (已废弃): 用户态代理, 性能差
│   │   ├─ iptables (默认): NAT 规则链, O(n) 复杂度
│   │   ├─ ipvs: 内核态负载均衡, O(1) 查找, 更多算法
│   │   └─ nftables (KEP-3458): iptables 后继, 统一表结构
│   ├─ ClusterIP: 虚拟IP, 仅集群内可达
│   ├─ NodePort: 节点端口映射 (30000-32767)
│   ├─ LoadBalancer: 云厂商 LB 集成
│   └─ ExternalName: CNAME DNS 记录
│
└─► Ingress 与 Gateway API
    ├─ Ingress (v1): 简单 L7 路由, 依赖 IngressController
    ├─ Gateway API (v1beta1): 角色分离, HTTPRoute/TCPRoute
    └─ Service Mesh: Istio, Linkerd,  sidecar L7 代理
```

---

## 二、核心概念的形式化定义

```text
定义 (Kubernetes 网络模型):
  ∀ Pod p₁, p₂ ∈ Cluster:
    reachable(p₁.ip, p₂.ip) = true  ∧  NAT(p₁.ip, p₂.ip) = false

定义 (CNI 接口):
  CNI = ⟨NetworkConfig, RuntimeConfig, Result⟩

  核心操作:
    ADD(netns, containerID, ifName, config) → ⟨IPs, Routes, DNS⟩
    DEL(netns, containerID, ifName, config) → ∅
    CHECK(netns, containerID, ifName, config) → {OK, ERROR}

定义 (Service 虚拟 IP):
  Service = ⟨ClusterIP, Port[], Selector, Endpoints[]⟩

  ClusterIP ∈ 10.96.0.0/12 (默认 Service CIDR)

  虚拟 IP 解析:
    resolve(ClusterIP) = {PodIPᵢ | Podᵢ.labels ⊇ Service.selector}

定义 (kube-proxy iptables 规则):
  KUBE-SVC-⟨hash⟩ 链: 负载均衡到 KUBE-SEP-⟨hash⟩ 链
  KUBE-SEP-⟨hash⟩ 链: DNAT 到具体 PodIP:Port

  包处理流程:
    PREROUTING → KUBE-SERVICES → KUBE-SVC-* → KUBE-SEP-* → DNAT

定义 (IPVS):
  IPVS_Scheduling = {rr, wrr, lc, wlc, lblc, dh, sh, sed, nq}
  转发模式: NAT / IP Tunneling / Direct Routing
```

---

## 三、多维矩阵对比

| CNI 插件 | 数据平面 | 网络模式 | 网络策略 | 性能 | 适用场景 |
|---------|---------|---------|---------|------|---------|
| **Calico** | Linux 路由/eBPF | BGP/VXLAN | NetworkPolicy | 高 | 通用, 大规模 |
| **Cilium** | eBPF/XDP | 隧道/直连 | CiliumNetworkPolicy | 极高 | 安全, 可观测 |
| **Flannel** | VXLAN/UDP | Overlay | 不支持 | 中 | 小型集群 |
| **Weave** | VXLAN | Overlay | 支持 | 中 | 简单快速 |
| **Antrea** | OVS/eBPF | Overlay | Antrea Policy | 高 | VMware 生态 |
| **AWS VPC** | ENI | 主机网络 | VPC SecurityGroup | 极高 | AWS EKS |

| kube-proxy 模式 | 转发位置 | 后端选择复杂度 | 连接跟踪 | 健康检查 | 调度算法 |
|----------------|---------|--------------|----------|---------|---------|
| **userspace** | 用户态 | O(n) | 手动 | 轮询 | round-robin |
| **iptables** | 内核态 (Netfilter) | O(n) 概率 | conntrack | 被动 | 随机 |
| **ipvs** | 内核态 (IPVS) | O(1) | conntrack | 主动 | rr/wrr/lc/wlc |
| **nftables** | 内核态 (nf_tables) | O(1) 预期 | conntrack | 主动 | 灵活 |

---

## 四、权威引用

> **Tim Hockin** (Kubernetes 联合创始人, Google):
> "The Kubernetes network model is deliberately simple: every pod gets its own IP, and all pods can talk to each other without NAT. Everything else is an implementation detail."

> **Liz Rice** (Isovalent/Cilium, "Learning eBPF", O'Reilly 2023):
> "eBPF allows us to run sandboxed programs in the kernel without changing kernel source code or loading modules. Cilium uses eBPF to replace kube-proxy and enforce network policy."

> **Dan Williams** (Red Hat, OVN/Kubernetes Networking):
> "IPVS is the natural successor to iptables for kube-proxy. It offers O(1) backend selection and supports multiple scheduling algorithms natively."

> **Rob Whiteley** (NGINX, Gateway API 推进者):
> "Gateway API represents the next evolution of Ingress, separating infrastructure concerns from application routing concerns."

---

## 五、工程实践与代码示例

**Calico BGP 模式路由示例:**

```bash
# 节点上查看 Pod CIDR 路由
ip route | grep bird
10.244.1.0/26 via 192.168.1.11 proto bird
10.244.2.0/26 via 192.168.1.12 proto bird
```

**Cilium 替代 kube-proxy (eBPF 模式):**

```bash
cilium install --kube-proxy-replacement=strict \
  --helm-set k8sServiceHost=auto \
  --helm-set k8sServicePort=6443
```

**NetworkPolicy 示例:**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  # 默认拒绝所有入站流量
```

---

## 六、批判性总结

Kubernetes 网络模型的"每个 Pod 一个 IP、全网可达无 NAT"设计，从根本上颠覆了 Docker 默认的桥接+NAT 模式，为微服务通信提供了与物理机网络等价的语义。但这一设计的代价是**IP 地址空间消耗爆炸**：一个中等规模集群（1000 节点 × 110 Pod/节点）就需要 /14 甚至更大的 CIDR，与现有企业网络规划的冲突长期存在。

kube-proxy 的实现演进揭示了 Linux 网络栈的历史包袱：iptables 模式虽然简单，但其**O(n) 规则遍历**在大规模 Service（>1000 个）场景下导致 `kube-proxy` CPU 占用飙升和 conntrack 表溢出；ipvs 的 O(1) 查找改善了这个问题，但其对 UDP 会话老化和短连接负载不均的处理仍不完美。nftables 作为 iptables 的官方后继者，提供了更统一的表结构和更好的性能，但 Kubernetes 社区向 nftables 的迁移进展缓慢——这再次印证了"在基础设施领域，技术债务的偿还周期以十年计"。

Cilium 的 eBPF 方案代表了数据平面的未来：绕过 Netfilter 全路径，直接在 socket 层或 XDP 层处理包转发，配合 eBPF 的 Map 结构实现真正的 O(1) 负载均衡。但 eBPF 的验证器复杂性、内核版本依赖（≥5.10 才能获得完整特性）和调试困难性，使其在生产环境的采用仍局限于技术领先的团队。Service Mesh（Istio）则在 L7 引入了另一层代理复杂度，Sidecar 的资源开销（每个 Pod 额外 100MB+ 内存）推动了 Ambient Mesh 的无 Sidecar 架构探索。网络的分层抽象正在从"内核态 vs 用户态"之争，演变为"eBPF 内核可编程 vs 用户态代理灵活性"的新权衡。
