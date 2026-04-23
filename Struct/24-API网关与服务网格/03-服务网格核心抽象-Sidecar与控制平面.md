# 服务网格核心抽象：Sidecar 与控制平面

> **来源映射**: View/00.md §3.1
> **国际权威参考**: "Istio Architecture" (istio.io), "Linkerd Design Principles" (Buoyant), "The Service Mesh" (William Morgan)

---

## 一、知识体系思维导图

```text
服务网格核心抽象
│
├─► 数据平面 (Data Plane)
│   ├─► Sidecar 代理: 与应用容器共部署于同一 Pod
│   ├─► Envoy (Istio默认): C++, 高性能 L4/L7 代理
│   ├─► Linkerd-proxy: Rust, 轻量级专为网格设计
│   ├─► 流量拦截: iptables/nftables / eBPF / Windows HNS
│   └─► 功能: 路由、负载均衡、健康检查、指标、追踪
│
├─► 控制平面 (Control Plane)
│   ├─► Istiod (Istio): 单体控制平面
│   │   ├─► Pilot: xDS 配置分发
│   │   ├─► Citadel: 证书管理 (已合并)
│   │   └─► Galley: 配置验证 (已合并)
│   ├─► Linkerd-control-plane: 轻量 Go 组件
│   └─► Consul Connect: 与 Consul 服务发现集成
│
├─► xDS 协议族 (Envoy 动态配置 API)
│   ├─► LDS (Listener Discovery Service)
│   ├─► RDS (Route Discovery Service)
│   ├─► CDS (Cluster Discovery Service)
│   ├─► EDS (Endpoint Discovery Service)
│   ├─► SDS/SDS (Secret Discovery Service)
│   └─► ADS (Aggregated Discovery Service): 统一流
│
└─► mTLS (双向 TLS)
    ├─► 自动证书签发: SPIFFE/SPIRE 身份
    ├─► 证书轮换: 无中断热更新
    ├─► 双向认证: 客户端+服务端证书验证
    └─► 透传身份: x-forwarded-client-cert (XFCC)
```

---

## 二、核心概念的形式化定义

**定义 1 (Sidecar 模式)**:
设应用容器为 $A$，Sidecar 代理为 $P$，则 Pod $S$ 为:
$$S = A \cup P \text{ where } NetworkNamespace(A) = NetworkNamespace(P)$$
流量拦截:
$$Intercept(traffic) = \begin{cases}
inbound: & dst_{iptables} \rightarrow P:15006 \rightarrow A:app \\
outbound: & src_{A} \rightarrow P:15001 \rightarrow dst_{upstream}
\end{cases}$$

**定义 2 (xDS 配置模型)**:
设 Envoy 代理配置为 $Config = \langle L, R, C, E, S \rangle$:
- $L$ (Listeners): 监听器集合，$L = \{l \mid l = \langle address, filter_chain \rangle\}$
- $R$ (Routes): 路由规则，$R = \{r \mid r = \langle match, action \rangle\}$
- $C$ (Clusters): 上游集群，$C = \{c \mid c = \langle lb_policy, endpoints \rangle\}$
- $E$ (Endpoints): 后端实例，$E = \{e \mid e = \langle ip, port, weight, health \rangle\}$
- $S$ (Secrets): TLS 证书与密钥

控制平面通过 gRPC 流推送增量更新:
$$\Delta Config = CP_{desired} \ominus DP_{current}$$

**定义 3 (mTLS 身份模型)**:
$$Identity(service) = SPIFFE\ URI = spiffe://trust_domain/ns/namespace/sa/service_account$$
$$mTLS(a, b) = \begin{cases}
\top & \text{if } Verify(Chain_a, CA_{mesh}) \land Verify(Chain_b, CA_{mesh}) \\
\bot & \text{otherwise}
\end{cases}$$

**定义 4 (服务网格的流量矩阵)**:
设服务集合为 $Services = \{s_1, s_2, ..., s_n\}$，流量矩阵 $T$ 为:
$$T_{ij} = Volume(s_i \rightarrow s_j)$$
服务网格的目标是将 $T$ 透明化、可观测、可控制:
$$Mesh(T) = \langle Observable(T), Controllable(T), Secure(T) \rangle$$

---

## 三、多维矩阵对比

| 服务网格 | 数据平面 | 语言 | 资源开销 | 启动时间 | 社区 | 2026 年状态 |
|---------|---------|------|---------|---------|------|------------|
| **Istio** | Envoy | C++ | 高(100MB+) | 慢 | CNCF Graduated | **最广泛部署** |
| **Linkerd** | linkerd2-proxy | Rust | 极低(10MB) | 快 | CNCF Graduated | 轻量首选 |
| **Consul Connect** | Envoy / 内置 | C++ / Go | 中 | 中 | HashiCorp | 与 Consul 深度绑定 |
| **Kuma** | Envoy | C++ | 中 | 中 | CNCF Sandbox | 多云场景 |
| **AWS App Mesh** | Envoy | C++ | 托管 | 托管 | AWS | AWS 生态 |

| xDS API | 配置对象 | 更新粒度 | 典型大小 | 热更新支持 |
|--------|---------|---------|---------|-----------|
| **LDS** | Listener | 单个端口 | 大 | 是 |
| **RDS** | Route | 虚拟主机 | 中 | 是 |
| **CDS** | Cluster | 上游服务 | 中 | 是 |
| **EDS** | Endpoint | 单个实例 | 小 | 是 |
| **SDS** | Secret | 单个证书 | 小 | 是(无中断) |
| **ADS** | 全部聚合 | 增量 | 可变 | 是 |

| 证书管理方案 | 签发速度 | 依赖 | 多集群支持 | 适用场景 |
|-------------|---------|------|-----------|---------|
| **Istio Citadel** | 快 | Istiod | 是(多信任域) | 纯 Istio 环境 |
| **SPIRE** | 快 | SPIRE Server | **是** | 跨平台统一身份 |
| **Cert-manager** | 中 | Kubernetes | 是 | 与外部 CA 集成 |
| **Vault** | 中 | HashiCorp Vault | 是 | 企业级密钥管理 |

---

## 四、权威引用

> **Brendan Burns** (Kubernetes 联合创始人, KubeCon 2017):
> "Service mesh is the TCP/IP of the cloud native era — a layer that provides reliable delivery without applications needing to worry about it."

> **William Morgan** (Linkerd 作者, "What's a Service Mesh?", 2017):
> "A service mesh is a dedicated infrastructure layer for handling service-to-service communication."

> **Istio 官方文档** ("Istio Architecture", 2025):
> "Istio uses Envoy proxies as the data plane, managed by a unified control plane (istiod) that provides service discovery, configuration, and certificate management."

---

## 五、工程实践与代码示例

```yaml
# Istio 流量管理：虚拟服务 + 目标规则
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews-route
spec:
  hosts:
    - reviews
  http:
    - match:
        - headers:
            end-user:
              exact: jason
      route:
        - destination:
            host: reviews
            subset: v2
    - route:
        - destination:
            host: reviews
            subset: v1
          weight: 90
        - destination:
            host: reviews
            subset: v3
          weight: 10
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: reviews-destination
spec:
  host: reviews
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
    outlierDetection:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s
  subsets:
    - name: v1
      labels:
        version: v1
    - name: v2
      labels:
        version: v2
    - name: v3
      labels:
        version: v3
```

---

## 六、批判性总结

服务网格的核心洞察是**将网络通信从应用代码中完全抽离**，但这一愿景的实现代价是显著的。Sidecar 模式虽然做到了语言无关和零侵入，却引入了**资源税**（每个 Pod 额外 100MB+ 内存）、**延迟税**（额外一次网络跳，通常增加 1-3ms）和**运维税**（需要管理代理的生命周期和版本升级）。

Istio 选择 Envoy 作为数据平面是一个关键的技术决策。Envoy 的 C++ 实现提供了极高的性能和丰富的 L7 功能，但也带来了二进制体积大（>100MB）、启动慢、资源占用高的问题。Linkerd 的 Rust 代理（linkerd2-proxy）则走了另一条路：专为服务网格场景裁剪功能集，实现了 10MB 级别的内存占用和亚秒级冷启动。这体现了**专用化（specialization）对通用化（generalization）的性能优势**。

xDS 协议是服务网格控制平面与数据平面之间的**事实标准接口**，其增量更新机制（Delta xDS）显著降低了大规模集群中的配置推送开销。然而，xDS 的复杂性和 Envoy 配置的冗长是入门者的主要障碍。一个典型的 VirtualService 配置需要理解 Listener、Route、Cluster、Endpoint 四层概念，这比简单的 HTTP 路由规则抽象高出至少两个认知层级。

mTLS 的"自动加密"在安全性上是一个巨大进步，但其隐含的**信任域（trust domain）管理**在大规模多集群场景中变得复杂。当服务跨集群通信时，需要建立信任锚（trust anchor）的联邦关系，这往往涉及组织层面的安全策略协商——技术问题在此演变为治理问题。
