# 网络协议与通信：总览

> **来源映射**: View/00.md §2.1
> **国际权威参考**: RFC 793 (TCP), RFC 7540 (HTTP/2), RFC 9000 (QUIC), gRPC 文档

---

## 一、知识体系思维导图

```text
网络协议与通信
│
├─► 传输层协议
│   ├─► TCP
│   │   ├─ 三次握手、四次挥手
│   │   ├─ 滑动窗口、拥塞控制 (慢启动、拥塞避免、快重传)
│   │   ├─ 队头阻塞 (Head-of-Line Blocking)
│   │   └─ 连接建立延迟: 1-RTT (TLS 1.2: 2-RTT)
│   │
│   ├─► UDP
│   │   ├─ 无连接、无拥塞控制、无可靠性保证
│   │   └─ 适用: DNS、视频流、实时游戏
│   │
│   └─► QUIC (基于 UDP)
│       ├─ 0-RTT / 1-RTT 连接建立
│       ├─ 内置 TLS 1.3 (加密默认)
│       ├─ 多路复用无队头阻塞
│       ├─ 连接迁移 (Connection Migration): IP变化不影响连接
│       └─ HTTP/3 基于 QUIC
│
├─► 应用层协议
│   ├─► HTTP/1.1
│   │   ├─ 文本协议、持久连接 (Keep-Alive)
│   │   ├─ 队头阻塞: 同一连接请求串行
│   │   └─ 优化: 域名分片、精灵图、内联
│   │
│   ├─► HTTP/2
│   │   ├─ 二进制分帧层
│   │   ├─ 多路复用: 同一连接并行请求
│   │   ├─ 头部压缩 (HPACK)
│   │   ├─ 服务器推送 (Server Push)
│   │   └─ 仍基于 TCP → 存在 TCP 层队头阻塞
│   │
│   ├─► HTTP/3
│   │   ├─ 基于 QUIC (UDP)
│   │   ├─ 彻底消除队头阻塞
│   │   └─ 2026年: 主流浏览器支持、CDN广泛部署
│   │
│   ├─► gRPC
│   │   ├─ 基于 HTTP/2
│   │   ├─ Protocol Buffers: 二进制序列化
│   │   ├─ 四种模式: Unary / Server Streaming / Client Streaming / Bidirectional
│   │   └─ 适用: 微服务间通信
│   │
│   └─► WebSocket
│       ├─ 全双工、持久连接
│       ├─ 基于 TCP，初始 HTTP 握手升级
│       └─ 适用: 实时通信、推送
│
└─► RPC 框架对比
    ├─ gRPC: HTTP/2 + Protobuf, 强类型, 跨语言
    ├─ Thrift: Facebook, 紧凑二进制, 多传输协议
    ├─ Dubbo: 阿里巴巴, Java生态, 服务治理
    └─ REST: HTTP/1.1 + JSON, 简单, 通用
```

---

## 二、协议演进的关键指标对比

| 协议 | 传输层 | 连接建立 | 队头阻塞 | 多路复用 | 头部压缩 | 连接迁移 | 2026年状态 |
|------|--------|---------|---------|---------|---------|---------|-----------|
| **HTTP/1.1** | TCP | 1-3 RTT | ✅ 严重 | ❌ 无 | ❌ 无 | ❌ 无 |  legacy |
| **HTTP/2** | TCP | 1-3 RTT | ⚠️ TCP层 | ✅ 有 | ✅ HPACK | ❌ 无 | 主流 |
| **HTTP/3** | QUIC/UDP | 0-1 RTT | ❌ 无 | ✅ 有 | ✅ QPACK | ✅ 支持 | **增长中** |
| **gRPC** | HTTP/2 | 同HTTP/2 | 同HTTP/2 | ✅ 有 | ✅ Protobuf | ❌ 无 | 主流 |
| **WebSocket** | TCP | HTTP升级 | ✅ 有 | N/A | ❌ 无 | ❌ 无 | 实时场景 |

---

## 三、QUIC 的形式化优势

```text
TCP + TLS 1.2 的握手:
  TCP 三次握手: 1 RTT
  TLS 握手: 2 RTT
  总计: 3 RTT (首次连接)

QUIC + TLS 1.3 的握手:
  首次连接: 1 RTT (QUIC + TLS 1.3 合并)
  恢复连接: 0 RTT (使用之前协商的参数)

队头阻塞对比:
  HTTP/2 over TCP:
    若一个 TCP 包丢失，所有流等待重传

  HTTP/3 over QUIC:
    每个流独立拥塞控制、独立重传
    一个流的丢包不影响其他流
```

---

## 四、权威引用

> **Vint Cerf** & **Bob Kahn** (TCP/IP 发明者):
> "We wanted to build a network that could survive nuclear war." —— TCP 的可靠性设计初衷。

> **Jana Iyengar** (QUIC 联合发明者, Google):
> "QUIC is not just a new transport protocol; it's a rethinking of how the web should work."

> **RFC 9000** (QUIC):
> "QUIC is a UDP-based multiplexed and secure transport protocol."

---

## 五、子主题导航

| 序号 | 子主题文件 | 核心内容 |
|------|-----------|---------|
| 01 | [01-TCP协议-握手拥塞控制与队头阻塞](./01-TCP协议-握手拥塞控制与队头阻塞.md) | 三次握手、滑动窗口、拥塞算法 |
| 02 | [02-HTTP演进-从1.1到2到3](./02-HTTP演进-从1.1到2到3.md) | 二进制分帧、HPACK/QPACK、多路复用 |
| 03 | [03-QUIC与HTTP3-0RTT与连接迁移](./03-QUIC与HTTP3-0RTT与连接迁移.md) | UDP、内置TLS、无队头阻塞 |
| 04 | [04-gRPC-基于HTTP2的RPC框架](./04-gRPC-基于HTTP2的RPC框架.md) | Protobuf、四种通信模式 |
| 05 | [05-WebSocket与实时通信](./05-WebSocket与实时通信.md) | 全双工、升级握手、心跳机制 |
| 06 | [06-RPC框架对比-gRPC-Thrift-Dubbo-REST](./06-RPC框架对比-gRPC-Thrift-Dubbo-REST.md) | 性能、生态、适用场景 |

---

## 六、批判性总结

HTTP/3 的普及标志着**传输层协议的根本性变革**：从 TCP（操作系统内核实现、演进缓慢）转向 QUIC（用户空间实现、可快速迭代）。这是 30 年来互联网协议栈最大的变化。

但 QUIC 也带来新挑战：中间件（防火墙、NAT、负载均衡器）对 UDP 的支持不如 TCP 成熟；企业网络的 UDP 限制可能导致 QUIC 降级到 TCP。这再次验证了**康威定律**——技术演进的边界由组织（和网络运营商）的能力决定。
