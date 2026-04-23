# gRPC：基于 HTTP/2 的 RPC 框架

> **来源映射**: View/00.md §2.1
> **国际权威参考**: gRPC Core Documentation, "gRPC: A high performance, open-source universal RPC framework" (Google, 2016), Protocol Buffers Language Specification

---

## 一、知识体系思维导图

```text
gRPC 框架
│
├─► 架构层次
│   ├─ 应用层: Service/Method 定义 (.proto)
│   ├─ 存根层: Client Stub / Server Stub (代码生成)
│   ├─ 通信层: HTTP/2 帧传输
│   ├─ 序列化层: Protocol Buffers
│   └─ 传输层: TCP (HTTP/2) 或 QUIC (实验性)
│
├─► Protocol Buffers
│   ├─ IDL: .proto 文件定义消息与服务
│   ├─ 代码生成: protoc 编译器生成多语言代码
│   ├─ 二进制编码: Tag-Length-Value (TLV) 格式
│   ├─ 版本兼容: 字段编号机制，向前/向后兼容
│   └─ proto3: 简化语法，默认支持 JSON 映射
│
├─► 四种通信模式
│   ├─ Unary RPC: 一请求一响应
│   ├─ Server Streaming: 一请求多响应
│   ├─ Client Streaming: 多请求一响应
│   └─ Bidirectional Streaming: 全双工流
│
├─► HTTP/2 映射
│   ├─ Method → POST /{service}/{method}
│   ├─ 请求消息 → DATA 帧序列 (Length-Prefixed Message)
│   ├─ 响应状态 → Trailers (grpc-status, grpc-message)
│   ├─ 流 ID: 每种 RPC 对应一个 HTTP/2 流
│   └─ 元数据: Headers (初始) + Trailers (结束)
│
├─► 流控制
│   ├─ HTTP/2 级流控制 (字节级)
│   ├─ gRPC 级流控制 (消息级)
│   └─ 背压 (Backpressure): 消费者控制生产者速率
│
└─► 高级特性
    ├─ 拦截器 (Interceptors): 认证、日志、监控
    ├─ 负载均衡: 客户端负载均衡 (Name Resolver + LB Policy)
    ├─ 健康检查: gRPC Health Checking Protocol
    ├─ 超时与重试: Deadline / Retry Policy
    └─ 反射 (Reflection): 服务端元数据发现
```

---

## 二、核心概念的形式化定义

### 2.1 gRPC over HTTP/2 映射

```text
定义 (gRPC 请求映射):
  给定服务 Service, 方法 Method, 请求消息序列 M = [m₁, m₂, ..., mₙ]

  HTTP/2 请求:
    :method = POST
    :scheme = https (或 http)
    :authority = {host}:{port}
    :path = /{Service}/{Method}
    content-type = application/grpc
    te = trailers
    grpc-timeout = {超时时间}

  消息编码:
    每个消息 = ⟨Compressed-Flag: 1byte, Length: 4bytes, Message⟩
    Compressed-Flag = 0 (未压缩) 或 1 (gzip/deflate 等)

  响应状态:
    初始 HEADERS: 200 OK + 元数据
    DATA 帧: 响应消息序列
    Trailers: grpc-status (0=OK, 其他=错误码), grpc-message
```

### 2.2 四种通信模式形式化

```text
定义 (gRPC 通信模式):

  Unary:
    Client: req → Server
    Server: res → Client
    对应 HTTP/2: 一个请求流 (Client→Server) + 一个响应流 (Server→Client)

  Server Streaming:
    Client: req → Server
    Server: [res₁, res₂, ...] → Client
    对应 HTTP/2: 单一请求 DATA 帧 + 多个响应 DATA 帧

  Client Streaming:
    Client: [req₁, req₂, ...] → Server
    Server: res → Client
    对应 HTTP/2: 多个请求 DATA 帧 + 单一响应 Trailers

  Bidirectional Streaming:
    Client: [req₁, req₂, ...] ⟷ Server: [res₁, res₂, ...]
    对应 HTTP/2: 单一 HTTP/2 流上的全双工消息交换
    无强制的请求-响应顺序: 服务端可在收到全部请求前发送响应
```

### 2.3 Protocol Buffers 编码

```text
定义 (Proto3 编码):
  消息 = 字段序列，每个字段 = ⟨Tag, Value⟩

  Tag = (field_number << 3) | wire_type

  Wire Type:
    0: Varint (int32, int64, bool, enum)
    1: 64-bit (fixed64, sfixed64, double)
    2: Length-delimited (string, bytes, embedded messages, packed repeated)
    5: 32-bit (fixed32, sfixed32, float)

  Varint 编码: 7 bits per byte, MSB 指示后续字节
    例: 300 = 0b10101100 00000010 = 0xAC 0x02

  版本兼容性保证:
    - 新增字段: 旧解析器忽略未知字段 (field_number 未识别)
    - 删除字段: 保留 field_number (reserved 关键字)
    - 默认值: 标量类型有语言级默认值
```

---

## 三、多维矩阵对比

| 维度 | gRPC | REST/JSON | Thrift | GraphQL |
|------|------|-----------|--------|---------|
| **传输协议** | HTTP/2 | HTTP/1.1 或 HTTP/2 | TCP/HTTP/自定义 | HTTP/1.1 或 HTTP/2 |
| **序列化** | Protobuf (二进制) | JSON (文本) | Thrift Binary/Compact | JSON |
| **IDL** | .proto | OpenAPI/Swagger | .thrift | Schema |
| **流支持** | ✅ 原生四种模式 | ❌ SSE/长轮询 | ✅ 有限 | ✅ Subscriptions |
| **浏览器支持** | ❌ 需 gRPC-Web | ✅ 原生 | ❌ | ✅ 原生 |
| **强类型** | ✅ 是 | ⚠️ 弱 | ✅ 是 | ✅ 是 |
| **代码生成** | ✅ 多语言 | ⚠️ 工具链多样 | ✅ 多语言 | ✅ 多语言 |
| **互操作性** | 好 | **极好** | 中 | 良 |
| **调试便利** | 差 (二进制) | **优** (人类可读) | 差 | 良 |
| **2026 趋势** | 微服务主流 | 开放 API 主流 | 历史遗留 | 前端主流 |

---

## 四、权威引用

> **Google gRPC 团队** (2016):
> "gRPC is a modern, open source, high-performance remote procedure call (RPC) framework that can run anywhere."

> **Martin Kleppmann** ("Designing Data-Intensive Applications", O'Reilly 2017):
> "The main difference between REST and RPC is not the protocol, but the fundamental abstraction: resources vs operations."

> **Clements et al.** ("Documenting Software Architectures", SEI Series):
> "RPC frameworks trade transparency for convenience — remote calls are not local calls, and pretending they are leads to fragile distributed systems."

> **gRPC Load Balancing Design**:
> "gRPC breaks the traditional proxy-based load balancing model by pushing LB logic to the client, enabling better performance but complicating infrastructure."

---

## 五、工程实践与代码示例

### 5.1 .proto 服务定义

```protobuf
syntax = "proto3";
package example;

service OrderService {
  rpc GetOrder (GetOrderRequest) returns (Order);
  rpc ListOrders (ListOrdersRequest) returns (stream Order);
  rpc CreateOrders (stream CreateOrderRequest) returns (OrderSummary);
  rpc Chat (stream ChatMessage) returns (stream ChatMessage);
}

message GetOrderRequest {
  string order_id = 1;
}

message Order {
  string order_id = 1;
  double amount = 2;
  OrderStatus status = 3;
}

enum OrderStatus {
  PENDING = 0;
  CONFIRMED = 1;
  SHIPPED = 2;
}
```

### 5.2 Go gRPC 服务端拦截器

```go
func authInterceptor(ctx context.Context, req interface{},
    info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
    md, _ := metadata.FromIncomingContext(ctx)
    token := md.Get("authorization")
    if !validateToken(token) {
        return nil, status.Error(codes.Unauthenticated, "invalid token")
    }
    return handler(ctx, req)
}

server := grpc.NewServer(grpc.UnaryInterceptor(authInterceptor))
```

---

## 六、批判性总结

gRPC 的核心设计决策是将 HTTP/2 的流语义暴露为编程语言的**方法调用抽象**，这带来了极大的开发效率提升，但也隐藏了分布式系统的根本复杂性：**远程调用不是本地调用**。网络分区、超时、重试、幂等性——这些问题在 gRPC 的存根层被封装得过于干净，导致开发者容易编写出假设网络可靠的代码。

gRPC 的**浏览器不可见性**是其生态位局限的根源：由于依赖 HTTP/2 Trailers 和二进制 Protobuf，浏览器原生 JavaScript 无法直接调用 gRPC 服务。gRPC-Web 通过引入代理层（Envoy/Nginx）转译协议来解决这一问题，但这增加了架构复杂度。这解释了为何 REST/JSON 仍在开放 API 领域占主导地位——**可调试性和通用访问性有时比性能更重要**。

Protobuf 的强类型和高效序列化是 gRPC 的核心优势，但 `.proto` 文件的**中心化版本治理**在大型组织中成为瓶颈。Protobuf 的向前兼容性保证依赖于字段编号的稳定约定，但在缺乏严格治理的团队中，字段重用和编号冲突屡见不鲜。这印证了形式化方法中的一条原则：**规约的严谨性只有在配套的执行机制下才有意义**。
