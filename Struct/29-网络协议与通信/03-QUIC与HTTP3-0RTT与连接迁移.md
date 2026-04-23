# QUIC 与 HTTP/3：0-RTT 与连接迁移

> **来源映射**: View/00.md §2.1
> **国际权威参考**: RFC 9000 (QUIC), RFC 9114 (HTTP/3), IETF QUIC Working Group

---

## 一、知识体系思维导图

```text
QUIC与HTTP/3
│
├─► QUIC 传输协议 (基于 UDP)
│   ├─► 设计动机
│   │   ├─ TCP + TLS 握手延迟过高 (2-3 RTT)
│   │   ├─ TCP 队头阻塞 (应用层多路复用受阻)
│   │   ├─ 连接迁移困难 (IP变化即断连)
│   │   └─ 协议僵化 (中间件干扰 TCP 选项)
│   │
│   ├─► 核心特性
│   │   ├─ 0-RTT / 1-RTT 连接建立
│   │   ├─ 内置 TLS 1.3 (加密默认)
│   │   ├─ 多路复用无队头阻塞
│   │   ├─ 连接迁移 (Connection ID)
│   │   └─ 用户空间实现 (快速迭代)
│   │
│   └─► 帧结构
│       ├─ STREAM 帧: 应用数据
│       ├─ ACK 帧: 确认
│       ├─ CRYPTO 帧: 握手数据
│       └─ PATH_CHALLENGE/PATH_RESPONSE: 路径验证
│
├─► HTTP/3 (基于 QUIC)
│   ├─► 与 HTTP/2 的差异
│   │   ├─ 移除 TCP 层: HTTP/3 → QUIC → UDP
│   │   ├─ QPACK 替代 HPACK (避免队头阻塞)
│   │   ├─ 流 ID 空间独立
│   │   └─ 服务器推送重新设计
│   │
│   └─► 性能收益
│       ├─ 首字节时间 (TTFB) 降低 20-30%
│       ├─ 连接建立时间降低 50-75%
│       └─ 移动网络体验显著提升
│
└─► 部署现状 (2026)
    ├─ 浏览器: Chrome/Firefox/Safari 默认支持
    ├─ CDN: Cloudflare/Fastly/Akamai 全面支持
    ├─ 服务端: nginx-quic, Caddy, LiteSpeed
    └─ 挑战: 企业防火墙 UDP 限制、QoS 降级
```

---

## 二、核心概念的形式化定义

### 2.1 QUIC 握手形式化

```text
定义 (QUIC 握手):
  设客户端 C, 服务端 S, 共享配置 SCFG (来自前次连接)

  首次连接 (1-RTT):
    C → S: ClientHello + QUIC参数
    S → C: ServerHello + 证书 + 加密的Extensions
    C → S: 加密的Finished + 应用数据

  恢复连接 (0-RTT):
    C → S: ClientHello + 早期数据 (使用之前协商的密钥)
    S → C: ServerHello + 确认

  安全条件:
    0-RTT 仅适用于幂等操作 (GET/HEAD)
    重放攻击风险: 攻击者可重放 0-RTT 数据包
```

### 2.2 连接迁移

```text
定义 (连接迁移):
  传统 TCP: Connection = ⟨SrcIP, SrcPort, DstIP, DstPort⟩
    IP变化 → 四元组变化 → 连接中断

  QUIC: Connection = ⟨ConnectionID, ...⟩
    ConnectionID 独立于网络地址
    IP变化 → 发送 PATH_CHALLENGE → 验证 → 继续通信

  适用场景:
    - WiFi ↔ 蜂窝网络切换
    - NAT 重绑定
    - 移动设备网络变化
```

---

## 三、多维矩阵对比

| 特性 | TCP + TLS 1.2 | TCP + TLS 1.3 | QUIC | HTTP/3 |
|------|--------------|--------------|------|--------|
| **握手延迟** | 2-3 RTT | 1-2 RTT | **0-1 RTT** | 同QUIC |
| **加密** | 可选 | 默认 | **始终加密** | 始终加密 |
| **队头阻塞** | ✅ TCP层 | ✅ TCP层 | **❌ 无** | ❌ 无 |
| **连接迁移** | ❌ 不支持 | ❌ 不支持 | **✅ 支持** | ✅ 支持 |
| **中间件兼容** | 好 | 好 | **差(UDP)** | 差 |
| **实现位置** | 内核 | 内核 | **用户空间** | 用户空间 |
| **拥塞控制** | 内核固定 | 内核固定 | **可插拔** | 可插拔 |

---

## 四、权威引用

> **Jana Iyengar** (QUIC 联合发明者, Google):
> "QUIC is not just a new transport protocol; it's a rethinking of how the web should work."

> **Mark Nottingham** (IETF HTTP Working Group 主席):
> "HTTP/3 is not about making things faster for everyone; it's about making things more reliable for the people who need it most."

> **RFC 9000** (QUIC: A UDP-Based Multiplexed and Secure Transport):
> "QUIC provides applications with flow-controlled streams for structured communication, low-latency connection establishment, and network path migration."

---

## 五、工程实践

### 5.1 nginx 启用 HTTP/3

```nginx
server {
    listen 443 quic reuseport;
    listen 443 ssl;

    ssl_certificate     /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # 启用 0-RTT
    ssl_early_data on;

    # 添加 Alt-Svc 头部，通知客户端支持 HTTP/3
    add_header Alt-Svc 'h3=":443"; ma=86400';
}
```

### 5.2 客户端连接迁移示例

```text
客户端从 WiFi 切换到 4G:
  1. WiFi 连接: ConnectionID=0xABCD, SrcIP=192.168.1.100
  2. 检测到 WiFi 断开
  3. 4G 连接: ConnectionID=0xABCD, SrcIP=10.0.0.50
  4. 发送 PATH_CHALLENGE 到新路径
  5. 服务端回复 PATH_RESPONSE
  6. 连接继续，应用无感知
```

---

## 六、批判性总结

QUIC 的 0-RTT 是**用安全性换取延迟**的典型工程权衡：它允许客户端在握手完成前发送数据，但引入了**重放攻击**风险。因此，0-RTT 数据被限制为幂等操作——这是一个务实的安全边界，而非完美的安全保证。

HTTP/3 的普及标志着互联网协议栈的**范式转移**：从操作系统内核控制的 TCP，转向用户空间可控的 QUIC。这使得协议演进不再受限于内核更新周期（Windows/Linux 内核版本碎片化），浏览器和 CDN 可以独立升级 QUIC 版本。这是**端点驱动创新**对**中间件僵化**的胜利，但代价是企业网络的 UDP 兼容性问题——许多防火墙仍默认阻止或限速 UDP 流量。
