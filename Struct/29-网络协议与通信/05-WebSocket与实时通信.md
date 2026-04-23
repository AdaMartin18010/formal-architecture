# WebSocket 与实时通信

> **来源映射**: View/00.md §2.1
> **国际权威参考**: RFC 6455 (The WebSocket Protocol), RFC 8441 (WebSocket over HTTP/2), "High Performance Browser Networking" (Ilya Grigorik)

---

## 一、知识体系思维导图

```text
WebSocket 协议
│
├─► 设计动机
│   ├─ HTTP 轮询: 高延迟、高开销、无效请求
│   ├─ HTTP 长轮询 (Long Polling): 服务端挂起请求
│   ├─ Server-Sent Events (SSE): 服务端单向推送
│   └─ WebSocket: 全双工、低延迟、单一长连接
│
├─► 握手升级
│   ├─ 客户端请求: GET /chat HTTP/1.1
│   │   ├─ Connection: Upgrade
│   │   ├─ Upgrade: websocket
│   │   ├─ Sec-WebSocket-Key: Base64 随机值 (16字节)
│   │   └─ Sec-WebSocket-Version: 13
│   ├─ 服务端响应: 101 Switching Protocols
│   │   ├─ Sec-WebSocket-Accept: SHA1(Key + GUID) 的 Base64
│   │   └─ GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
│   └─ 升级后: TCP 连接转为 WebSocket 帧传输
│
├─► 帧格式 (RFC 6455)
│   ├─ FIN: 是否为消息最后一个帧
│   ├─ RSV1-3: 扩展保留位 (通常为 0)
│   ├─ OPCODE: 帧类型
│   │   ├─ 0x1: 文本帧 (UTF-8)
│   │   ├─ 0x2: 二进制帧
│   │   ├─ 0x8: 关闭帧
│   │   ├─ 0x9: Ping 帧
│   │   └─ 0xA: Pong 帧
│   ├─ MASK: 客户端→服务端必须掩码
│   ├─ Payload Length: 7/7+16/7+64 bit
│   ├─ Masking Key: 客户端发送时 32bit 掩码密钥
│   └─ Payload Data: 与 Masking Key XOR
│
├─► 心跳机制
│   ├─ Ping/Pong 帧: 协议级保活
│   ├─ 应用级心跳: 自定义消息 (如 {"type":"ping"})
│   └─ 超时检测: 未收到 Pong 则关闭连接
│
└─► 应用场景
    ├─ 即时通讯 (IM): Slack, Discord, 微信 Web 端
    ├─ 实时协作: Google Docs, Figma, Notion
    ├─ 金融行情: 股票/加密货币实时报价
    ├─ 游戏同步: 多人在线游戏状态同步
    └─ IoT 遥测: 设备实时数据上报
```

---

## 二、核心概念的形式化定义

### 2.1 WebSocket 握手

```text
定义 (WebSocket 握手协议):
  客户端挑战:
    key = Base64Encode(随机 16 字节)

  服务端响应:
    accept = Base64Encode(SHA1(key || GUID))
    GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

  安全目的:
    - 防止非 WebSocket 客户端意外连接
    - 证明服务端实现了 WebSocket 协议 (非缓存响应)

  子协议协商 (可选):
    Sec-WebSocket-Protocol: chat, superchat
    服务端选择一个返回

  扩展协商 (可选):
    Sec-WebSocket-Extensions: permessage-deflate
    启用消息级压缩
```

### 2.2 帧解析形式化

```text
定义 (WebSocket 帧):
  帧 = ⟨FIN: 1bit, RSV: 3bits, opcode: 4bits,
        MASK: 1bit, payload_len: 7/23/71bits,
        [masking_key: 32bits], payload_data⟩`

  Payload Length 编码:
    0-125: 直接表示长度
    126:   后续 16 bits 为实际长度
    127:   后续 64 bits 为实际长度

  掩码规则 (客户端→服务端):
    masked_octet_i = original_octet_i XOR masking_key[i mod 4]

  掩码目的:
    - 防止缓存投毒攻击 (代理误将 WebSocket 帧缓存为 HTTP)
    - 避免与 HTTP 头部格式冲突
    - 注意: 服务端→客户端不需要掩码

  分片规则:
    消息可由多个帧组成，首帧 opcode ≠ 0, FIN = 0
    后续帧 opcode = 0 (Continuation), 末帧 FIN = 1
```

### 2.3 关闭握手

```text
定义 (WebSocket 关闭):
  主动关闭方发送 Close 帧:
    opcode = 0x8
    payload = ⟨status_code: 16bits, reason: UTF-8⟩`

  标准状态码:
    1000: Normal Closure
    1001: Going Away (浏览器导航离开)
    1002: Protocol Error
    1003: Unsupported Data
    1006: Abnormal Closure (连接异常断开，无 Close 帧)
    1008: Policy Violation
    1009: Message Too Big
    1011: Internal Server Error

  握手要求:
    一方发送 Close 帧后，必须继续处理收到的数据直到对方也发送 Close 帧
    底层 TCP 连接应由服务端关闭 (避免 TIME_WAIT 累积)
```

---

## 三、多维矩阵对比

| 维度 | HTTP 轮询 | HTTP 长轮询 | SSE | WebSocket |
|------|-----------|-------------|-----|-----------|
| **通信方向** | 客户端→服务端 | 客户端→服务端 | 服务端→客户端 | **全双工** |
| **实时性** | 差 (由轮询间隔决定) | 较好 (有事件即返回) | 好 | **极好** |
| **协议开销** | 高 (重复 HTTP 头) | 较高 | 低 | **极低** |
| **连接数** | 每轮询新建连接 | 挂起连接多 | 单一长连接 | 单一长连接 |
| **二进制支持** | ✅ | ✅ | ❌ (仅文本) | ✅ |
| **浏览器支持** | ✅ 全部 | ✅ 全部 | ✅ 现代浏览器 | ✅ 现代浏览器 |
| **代理兼容** | ✅ | ✅ | ⚠️ 需处理缓冲 | ⚠️ 需处理升级 |
| **自动重连** | ❌ 需自行实现 | ❌ 需自行实现 | ⚠️ EventSource 有限 | ❌ 需自行实现 |
| **适用场景** | 低频更新 | 中频推送 | 单向实时流 | **双向实时交互** |

---

## 四、权威引用

> **RFC 6455** (The WebSocket Protocol):
> "The WebSocket Protocol enables two-way communication between a client running untrusted code in a controlled environment to a remote host that has opted-in to communications from that code."

> **Ilya Grigorik** ("High Performance Browser Networking", O'Reilly):
> "WebSocket is not a replacement for HTTP; it is an extension that fills the gap for low-latency, full-duplex communication."

> **Ian Hickson** (HTML5 规范编辑者, WebSocket 早期推动者):
> "WebSocket was designed to be as simple as possible while providing the necessary features for real-time web applications."

> **Fette & Melnikov** (RFC 6455 作者):
> "The security model used for WebSocket is the origin-based security model commonly used by Web browsers."

---

## 五、工程实践与代码示例

### 5.1 Node.js WebSocket 服务端 (ws 库)

```javascript
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', (ws, req) => {
  console.log('Client connected from', req.socket.remoteAddress);

  // 心跳检测
  ws.isAlive = true;
  ws.on('pong', () => { ws.isAlive = true; });

  ws.on('message', (data, isBinary) => {
    if (isBinary) {
      console.log('Received binary:', data.length, 'bytes');
    } else {
      console.log('Received text:', data.toString());
    }
    // Echo back
    ws.send(data, { binary: isBinary });
  });

  ws.on('close', (code, reason) => {
    console.log('Connection closed:', code, reason.toString());
  });
});

// 定时心跳
const interval = setInterval(() => {
  wss.clients.forEach((ws) => {
    if (!ws.isAlive) return ws.terminate();
    ws.isAlive = false;
    ws.ping();
  });
}, 30000);
```

### 5.2 客户端 JavaScript

```javascript
const ws = new WebSocket('wss://example.com/socket');

ws.onopen = () => {
  ws.send(JSON.stringify({ type: 'subscribe', channel: 'trades' }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

ws.onclose = (event) => {
  if (!event.wasClean) {
    console.error('Connection died unexpectedly');
    // 实现指数退避重连
  }
};
```

---

## 六、批判性总结

WebSocket 的**掩码机制 (Masking)** 是一个饱受争议的设计：它强制客户端发送的所有数据经过 XOR 掩码，增加了客户端和服务端的计算开销，却仅为了防御一种理论上的**缓存投毒攻击**（即恶意 JavaScript 构造可被 HTTP 代理误缓存的帧）。在实际部署中，现代代理已能正确处理 Upgrade 握手，掩码的边际安全收益与其持续性能成本之间的比例值得质疑。

WebSocket 的**无状态连接管理**与**有状态业务会话**之间的张力是工程实践中的主要痛点。HTTP 的无状态性使得负载均衡器可以任意分发请求，但 WebSocket 的长连接要求**粘性会话 (Sticky Session)** 或**分布式发布-订阅**（Redis Pub/Sub、RabbitMQ）来实现多实例间的消息广播。这导致 WebSocket 系统的架构复杂度远超 REST API——开发者不仅要管理连接生命周期，还要设计消息路由拓扑。

WebSocket over HTTP/2 (RFC 8441) 试图利用 HTTP/2 的多路复用来减少连接数，但 2026 年的主流实现仍直接基于 TCP。WebSocket 最大的隐性成本在于**连接治理**：在百万级并发场景下，每个连接的文件描述符、内存缓冲区、心跳定时器累积成巨大的资源负担。这解释了为何部分高并发系统（如 Slack）在底层采用**自定义 UDP 协议**替代 WebSocket——当规模成为主要约束时，协议标准化让步于资源效率。
