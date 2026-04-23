# HTTP 演进：从 1.1 到 2 到 3

> **来源映射**: View/00.md §2.1
> **国际权威参考**: RFC 7230 (HTTP/1.1), RFC 7540 (HTTP/2), RFC 9114 (HTTP/3), "High Performance Browser Networking" (Ilya Grigorik, O'Reilly)

---

## 一、知识体系思维导图

```text
HTTP 协议演进
│
├─► HTTP/1.0 (1996, RFC 1945)
│   ├─ 短连接: 每个请求新建 TCP 连接
│   └─ 无 Host 头、无持久连接
│
├─► HTTP/1.1 (1997/2014, RFC 7230)
│   ├─ 持久连接 (Keep-Alive): 连接复用
│   ├─ 管道化 (Pipelining): 请求流水线
│   │   └─ 缺陷: 响应必须按序返回 (队头阻塞)
│   ├─ Host 头: 支持虚拟主机
│   ├─ 分块传输 (Chunked Transfer)
│   └─ 缓存控制: Cache-Control, ETag
│
├─► HTTP/2 (2015, RFC 7540)
│   ├─ 二进制分帧层 (Binary Framing)
│   │   ├─ 帧 (Frame): 最小传输单位
│   │   ├─ 消息 (Message): 完整请求/响应
│   │   └─ 流 (Stream): 双向字节流，逻辑通道
│   ├─ 多路复用 (Multiplexing)
│   │   └─ 单一 TCP 连接上并行传输多个流
│   ├─ HPACK 头部压缩
│   │   ├─ 静态表: 61 个常用头部
│   │   ├─ 动态表: 连接级上下文
│   │   └─ Huffman 编码
│   ├─ 服务器推送 (Server Push)
│   │   └─ 服务端主动推送资源 (2023 年起逐步废弃)
│   ├─ 流优先级与依赖
│   └─ 仍基于 TCP → TCP 队头阻塞
│
└─► HTTP/3 (2022, RFC 9114)
    ├─ 基于 QUIC (UDP)
    ├─ 彻底消除 TCP 队头阻塞
    ├─ QPACK 替代 HPACK (避免队头阻塞)
    ├─ 流 ID 空间独立 (单向/双向)
    └─ 连接迁移支持
```

---

## 二、核心概念的形式化定义

### 2.1 HTTP/2 二进制分帧

```text
定义 (HTTP/2 帧结构):
  帧 = ⟨Length: 24bit, Type: 8bit, Flags: 8bit,
        R: 1bit, StreamID: 31bit, Payload⟩`

  帧类型:
    HEADERS (0x1):  头部帧，开启新流
    DATA (0x0):     数据帧，承载实体内容
    SETTINGS (0x4): 连接级配置参数
    WINDOW_UPDATE (0x8): 流量控制窗口更新
    RST_STREAM (0x3): 流级终止
    GOAWAY (0x7):   连接级优雅关闭
    PUSH_PROMISE (0x5): 服务器推送承诺

  流状态机:
    idle → open → half-closed → closed

  关键约束:
    流 ID 奇数: 客户端发起
    流 ID 偶数: 服务端发起
    同一连接上 StreamID 单调递增
```

### 2.2 HPACK 压缩

```text
定义 (HPACK 编码):
  头部字段编码方式:
    1. 索引头部字段 (Indexed Header Field)
       索引指向静态表或动态表中的完整键值对

    2. 字面量头部字段，增量索引 (Literal with Indexing)
       发送完整键值对，并加入动态表

    3. 字面量头部字段，不索引 (Literal without Indexing)
       发送完整键值对，不加入动态表 (敏感字段)

    4. 字面量头部字段，从不索引 (Literal Never Indexed)
       禁止中间代理索引 (如 Cookie、Authorization)

  动态表大小约束:
    SETTINGS_HEADER_TABLE_SIZE (默认 4KB)
    采用 LRU 淘汰策略

  安全考量 (CRIME/BREACH 攻击防护):
    HTTP/2 禁止动态表大小的自适应调整，防止信息泄露
```

### 2.3 QPACK (HTTP/3)

```text
定义 (QPACK 编码):
  HPACK 的 QUIC 适配版本:
    - 独立单向流用于编码器/解码器动态表更新
    - Encoder Stream (流 ID = 2): 服务端发送动态表更新
    - Decoder Stream (流 ID = 3): 客户端发送确认

  解决 HPACK 的队头阻塞问题:
    HPACK: 动态表更新在数据流上同步 → 阻塞后续头部解码
    QPACK: 动态表更新在独立流上异步 → 单流阻塞不影响其他流

  风险: 乱序到达时，编码器可能使用解码器尚未收到的动态表条目
  缓解: 使用 QPACK 阻塞计数器 (Blocked Streams)
```

---

## 三、多维矩阵对比

| 维度 | HTTP/1.1 | HTTP/2 | HTTP/3 |
|------|----------|--------|--------|
| **传输层** | TCP | TCP | QUIC/UDP |
| **语义** | 文本 | 二进制分帧 | 二进制分帧 |
| **多路复用** | ❌ 无 (Pipelining 受限) | ✅ 流级 | ✅ 流级 |
| **队头阻塞** | ✅ 严重 (请求级) | ⚠️ TCP 层 | ❌ 无 |
| **头部压缩** | ❌ 无 | HPACK | QPACK |
| **服务器推送** | ❌ 无 | ✅ (已废弃) | 重新设计 |
| **连接建立** | 1-3 RTT | 1-3 RTT | **0-1 RTT** |
| **连接迁移** | ❌ 无 | ❌ 无 | ✅ 支持 |
| **TLS 要求** | 可选 | 事实强制 (ALPN) | **内置强制** |
| **中间件兼容** | 优 | 良 | 差 (UDP) |
| **2026 状态** | Legacy | 主流 | **快速增长** |

---

## 四、权威引用

> **Roy Fielding** (HTTP/1.1 与 REST 架构风格设计者, 2000):
> "REST is not a protocol, it's an architectural style." —— HTTP/1.1 的设计哲学源于 REST 的无状态约束。

> **Mike Belshe** (HTTP/2 联合设计者, SPDY 发明者):
> "HTTP/2 is not about making HTTP faster; it's about removing the workarounds that developers have built to make HTTP/1.1 tolerable."

> **Mark Nottingham** (IETF HTTP Working Group 主席):
> "HTTP/3 is not about making things faster for everyone; it's about making things more reliable for the people who need it most."

> **RFC 9114** (HTTP/3):
> "HTTP/3 uses QUIC as a secure multiplexed transport. QUIC builds on the lessons learned from TCP and TLS over several decades."

---

## 五、工程实践与代码示例

### 5.1 检查浏览器 HTTP 协议版本

```javascript
// 在浏览器 DevTools Network 面板查看 Protocol 列
// 或使用 Performance API
const entries = performance.getEntriesByType('navigation');
console.log(entries[0].nextHopProtocol); // "h2" 或 "h3"
```

### 5.2 服务端启用 HTTP/2

```nginx
# nginx HTTP/2 配置
server {
    listen 443 ssl http2;

    ssl_certificate     /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # HTTP/2 服务器推送 (已不推荐)
    # http2_push /style.css;
}
```

### 5.3 HTTP/3 服务端响应头

```http
HTTP/2 200 OK
alt-svc: h3=":443"; ma=2592000; quic=":443"
# 告知客户端同一端口支持 HTTP/3
```

---

## 六、批判性总结

HTTP/2 多路复用解决了 HTTP/1.1 的**应用层队头阻塞**，却继承了 TCP 的**传输层队头阻塞**——这是一个典型的**抽象泄漏**：应用层协议假设传输层提供独立的字节流，但 TCP 的单序列号机制使所有流共享同一个可靠性管道。当 HTTP/2 的一个流对应的 TCP 包丢失时，整个连接的所有流都必须等待重传。

服务器推送 (Server Push) 的兴衰是 HTTP 标准制定中的经典教训：它旨在通过服务端"预测"客户端需求来减少往返，但实践中**命中率极低**且**浪费带宽**——服务端无法精确知道客户端缓存中已有哪些资源。Chrome 于 2022 年移除支持，HTTP/3 中重新设计为更保守的原型。这印证了协议设计的一条铁律：**过度优化假设常比不优化更糟**。

HTTP/3 的 QPACK 头部压缩虽然解决了 HPACK 的队头阻塞，却引入了**编码器-解码器状态同步复杂度**。动态表更新在独立流上传输，可能导致解码器在收到带有新索引的头部帧时，尚未收到对应的动态表插入指令。这种权衡体现了分布式系统的普遍真理：**消除一个瓶颈通常会在别处创造新瓶颈**。
