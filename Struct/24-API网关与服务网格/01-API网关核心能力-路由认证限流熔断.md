# API 网关核心能力：路由、认证、限流、熔断

> **来源映射**: View/00.md §3.1
> **国际权威参考**: Nginx 文档, "Release It!" (Michael Nygard), AWS API Gateway 文档, Envoy 文档

---

## 一、知识体系思维导图

```text
API 网关核心能力
│
├─► 请求路由 (Routing)
│   ├─► 路径匹配: 前缀、精确、正则、参数化
│   ├─► Host 路由: 虚拟主机 / SNI 路由
│   ├─► Header/Method 路由: 灰度、A/B 测试
│   ├─► 权重路由: canary 发布
│   └─► 重写与重定向: URL 改写、协议转换
│
├─► 认证与鉴权 (AuthN/AuthZ)
│   ├─► JWT 验证: 签名、过期、issuer
│   ├─► OAuth2/OIDC: 令牌交换、用户信息
│   ├─► API Key: 简单密钥、配额绑定
│   ├─► mTLS: 客户端证书验证
│   └─► 插件化鉴权: OPA, Casbin, 自定义
│
├─► 速率限制 (Rate Limiting)
│   ├─► 令牌桶 (Token Bucket): 允许突发
│   ├─► 漏桶 (Leaky Bucket): 平滑流量
│   ├─► 固定窗口 (Fixed Window): 简单但有临界问题
│   ├─► 滑动窗口 (Sliding Window): 精确但成本高
│   └─► 分布式限流: Redis 计数器 / 令牌桶
│
└─► 熔断与降级 (Circuit Breaker)
    ├─► 三种状态: Closed → Open → Half-Open
    ├─► 触发条件: 错误率 / 延迟 P99 / 并发数
    ├─► 恢复策略: 指数退避、渐进式恢复
    ├─► 降级响应: 默认值、缓存值、友好错误
    └─► 舱壁隔离 (Bulkhead): 资源池隔离
```

---

## 二、核心概念的形式化定义

**定义 1 (路由匹配)**:
设请求为 $req = \langle method, host, path, headers, body \rangle$，路由规则集为 $R = \{r_1, r_2, ..., r_n\}$。
每条规则 $r_i = \langle predicate_i, upstream_i, priority_i \rangle$:
$$Match(req, r_i) = predicate_i(method) \land predicate_i(host) \land predicate_i(path) \land predicate_i(headers)$$
$$Route(req) = upstream_j \text{ where } j = \arg\max_{i} \{ priority_i \mid Match(req, r_i) = \top \}$$

**定义 2 (令牌桶算法)**:
设桶容量为 $C$，当前令牌数为 $tokens$，上次填充时间为 $last$，填充速率为 $rate$ (tokens/second):
$$tokens' = \min(C, tokens + rate \cdot (now - last))$$
$$Allow(req) = \begin{cases}
\top & \text{if } tokens' \geq 1 \\ \bot & \text{otherwise}
\end{cases}$$
若允许，则 $tokens'' = tokens' - 1$

**定义 3 (熔断器状态机)**:
设错误率阈值为 $\theta_{error}$，最小请求数为 $n_{min}$，熔断持续时间为 $T_{cooldown}$:
$$State_{t+1} = \begin{cases}
Open & \text{if } State_t = Closed \land \frac{Errors}{n_{min}} > \theta_{error} \\
HalfOpen & \text{if } State_t = Open \land (now - t_{trip}) > T_{cooldown} \\
Closed & \text{if } State_t = HalfOpen \land ProbeSuccess \\
Open & \text{if } State_t = HalfOpen \land ProbeFailure
\end{cases}$$

**定义 4 (负载均衡函数)**:
$$lb: Upstreams \times Request \rightarrow Backend$$
- 轮询: $lb(U, req) = U[i \mod |U|]$
- 加权轮询: $P(U_i) = \frac{w_i}{\sum_j w_j}$
- 最小连接: $lb(U, req) = \arg\min_{u \in U} Conn(u)$
- 一致性哈希: $lb(U, req) = U[\text{Hash}(req.key) \mod |U|]$

---

## 三、多维矩阵对比

| 限流算法 | 允许突发 | 平滑性 | 存储开销 | 分布式实现难度 | 典型使用 |
|---------|---------|--------|---------|--------------|---------|
| **固定窗口** | 否 | 差 | 低(1计数器) | 低 | 简单场景，容忍临界 |
| **滑动窗口(日志)** | 否 | 优 | 高(记录每个请求) | 中 | 精确计费的计费系统 |
| **滑动窗口(计数器)** | 否 | 良 | 中(2计数器) | 中 | 中等精度需求 |
| **令牌桶** | **是** | 良 | 低 | 高(需原子操作) | **通用首选，允许突发** |
| **漏桶** | 否 | **优** | 低 | 中 | 严格平滑，如 SMS 发送 |

| 熔断策略 | 触发指标 | 恢复方式 | 灵敏度 | 适用场景 |
|---------|---------|---------|--------|---------|
| **错误率熔断** | 错误百分比 > 阈值 | 定时探测 | 高 | 依赖服务不稳定 |
| **慢调用熔断** | P99 延迟 > 阈值 | 定时探测 | 中 | 依赖服务性能退化 |
| **并发数熔断** | 并发请求 > 阈值 | 即时 | 高 | 资源耗尽保护 |
| **组合熔断** | 多指标加权 | 渐进恢复 | 最高 | 核心链路保护 |

| 认证方式 | 安全性 | 有状态 | 跨域支持 | 实现复杂度 | 性能开销 |
|---------|--------|--------|---------|-----------|---------|
| **API Key** | 低 | 否 | 是 | 低 | 极低 |
| **JWT (HS256)** | 中 | 否 | 是 | 低 | 低 |
| **JWT (RS256)** | 中 | 否 | 是 | 中 | 中(验签) |
| **OAuth2/OIDC** | **高** | 是(会话) | 是 | 高 | 高(令牌交换) |
| **mTLS** | **最高** | 否 | 是 | 高 | 中(TLS 握手) |

---

## 四、工程实践与代码示例

```go
// Go 实现的令牌桶限流器 (基于 Redis 的分布式版本)
type RedisTokenBucket struct {
    client *redis.Client
    key    string
    rate   float64 // tokens per second
    cap    int64   // bucket capacity
}

func (b *RedisTokenBucket) Allow(ctx context.Context, n int64) bool {
    script := redis.NewScript(`
        local key = KEYS[1]
        local rate = tonumber(ARGV[1])
        local capacity = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        local requested = tonumber(ARGV[4])

        local fill_time = capacity / rate
        local ttl = math.floor(fill_time * 2)

        local last_tokens = redis.call("get", key)
        if last_tokens == false then
            last_tokens = capacity
        end

        local last_updated = redis.call("get", key .. ":last_updated")
        if last_updated == false then
            last_updated = 0
        end

        local delta = math.max(0, now - tonumber(last_updated))
        local filled_tokens = math.min(capacity, tonumber(last_tokens) + (delta * rate))
        local allowed = filled_tokens >= requested

        if allowed then
            filled_tokens = filled_tokens - requested
        end

        redis.call("setex", key, ttl, filled_tokens)
        redis.call("setex", key .. ":last_updated", ttl, now)

        return allowed
    `)

    now := float64(time.Now().UnixNano()) / 1e9
    result, _ := script.Run(ctx, b.client, []string{b.key},
        b.rate, b.cap, now, n).Result()
    return result.(int64) == 1
}
```

---

## 五、权威引用

> **Roy Fielding** (2000): "REST provides a set of architectural constraints that, when applied as a whole, emphasizes scalability of component interactions, generality of interfaces, and independent deployment of components."

> **Sam Newman** (2015): "The API gateway is the single entry point for all clients. It handles requests in one of two ways: either routing them to the appropriate service, or fanning them out to multiple services."

> **Google SRE Team** (2017): "Rate limiting is a critical defense mechanism for protecting services from overload. Without it, a single misbehaving client can degrade experience for all users."

> **Michael Nygard** (2018): "Circuit breakers are a way to automatically degrade functionality when the system is under stress."

> **Envoy 官方文档** (2022): "Envoy's routing subsystem supports complex route matching based on domain, path, headers, and runtime parameters."

> **AWS API Gateway 文档** (2023): "API Gateway uses the token bucket algorithm to limit requests, with a default rate of 10,000 requests per second.

---

## 六、批判性总结

API 网关作为微服务架构的**统一流量入口**，其设计哲学是将横切关注点（cross-cutting concerns）从业务服务中抽离，但这引入了一个**新的单点瓶颈和故障域**。

令牌桶算法是限流领域的事实标准，但其实现细节常被忽视。在分布式环境中，令牌桶的"填充"和"消费"需要原子操作，而 Redis 的 Lua 脚本虽然提供了原子性，但将限流逻辑绑定到 Redis 的可用性上——当 Redis 不可达时，网关面临"限流失效"与"拒绝服务"的两难选择。**降级策略的设计**（如本地回退到固定窗口）比限流算法本身更能体现工程的成熟度。

熔断器的核心悖论在于：**触发熔断的请求恰恰是系统最需要服务的请求**。一个设计良好的熔断器应当区分"可降级请求"（如推荐接口）和"不可降级请求"（如支付接口），对后者采用舱壁隔离（Bulkhead）而非全局熔断。Michael Nygard 在 "Release It!" 中强调的"舱壁模式"（将资源池隔离为多个独立分区）比单纯的熔断更能防止故障扩散。

在路由层面，现代网关正从"静态配置"向"动态编程"演进。Envoy 的 RDS（Route Discovery Service）和 WASM 插件允许路由规则在运行时动态更新，但这也将网关的复杂性从运维层推向了开发层——网关不再只是网络设备，而是**可编程的应用逻辑载体**。这一趋势与 Service Mesh 的边界正在模糊，预示着网关与网格的最终融合。
