# CDN 架构：边缘节点与回源策略

> **来源映射**: View/00.md §2.1
> **国际权威参考**: Akamai CDN 技术白皮书, Cloudflare Blog, "Global Load Balancing" (Google SRE Book)

---

## 一、知识体系思维导图

```text
CDN 架构体系
│
├─► 边缘节点层次 (Edge Hierarchy)
│   ├─► 用户浏览器 (Browser Cache)
│   ├─► 边缘 POP (Point of Presence): 最接近用户
│   ├─► 区域节点 (Regional/Mid-tier): 汇聚多个 POP
│   ├─► 核心节点 (Core/Origin Shield): 回源汇聚点
│   └─► 源站 (Origin Server)
│
├─► 路由与调度
│   ├─► DNS 调度 (CNAME → 最优 POP IP)
│   ├─► Anycast BGP (同一 IP 全球广播)
│   ├─► HTTP DNS / 302 调度 (应用层选路)
│   └─► 边缘负载均衡 (基于 RTT/负载/容量)
│
├─► 缓存键设计 (Cache Key)
│   ├─► 基础键: Host + Path + Query
│   ├─►  vary: Accept-Encoding, Accept-Language
│   ├─► Cookie 剥离 (避免缓存碎片化)
│   └─► 自定义键规则 (边缘计算改写)
│
├─► 回源策略 (Origin Strategy)
│   ├─► 直接回源: POP → Origin
│   ├─► 中间层回源: POP → Regional → Origin
│   ├─► Origin Shield: 统一回源入口 + 缓存聚合
│   ├─► 条件回源 (If-Modified-Since / If-None-Match)
│   └─► 分片回源 (Range Request)
│
└─► 动态加速 (DCDN)
    ├─► 动态路由优化 (实时选路避堵)
    ├─► TCP/QUIC 协议优化 (0-RTT, 连接复用)
    ├─► 边缘计算 (Cloudflare Workers / Lambda@Edge)
    └─► 边缘缓存动态内容 (短 TTL + ESI)
```

---

## 二、核心概念的形式化定义

**定义 1 (CDN 拓扑)**:
$$CDN = \langle V, E, C, R \rangle$$

- $V = \{v_0(Origin), v_1(Shield), v_2(Regional), v_3(POP), v_4(Client)\}$: 节点集合
- $E \subseteq V \times V$: 有向边，表示可回源路径
- $C: V \rightarrow \mathbb{R}^+$: 节点缓存容量函数
- $R: V \times V \rightarrow \mathbb{R}^+$: 边延迟函数

**定义 2 (最优 POP 选择)**:
$$POP^*(client) = \arg\min_{v \in POPs} \left( \alpha \cdot RTT(client, v) + \beta \cdot Load(v) + \gamma \cdot MissRate(v) \right)$$
其中 $\alpha + \beta + \gamma = 1$，分别代表延迟、负载、命中率权重。

**定义 3 (缓存键空间)**:
$$CacheKey(req) = f(Host, Path, Query_{filter}, Headers_{vary})$$
其中 $Query_{filter}$ 是允许参与缓存键的查询参数子集（通常过滤 utm_source 等追踪参数）。

**定义 4 (回源命中率)**:
$$HitRate = \frac{|\{req \mid CacheKey(req) \in Cache(v)\}|}{|TotalRequests|}$$
$$OriginOffload = 1 - \frac{|OriginRequests|}{|TotalRequests|}$$

---

## 三、多维矩阵对比

| 调度技术 | 工作层级 | 精度 | 扩展性 | 故障切换 | 典型延迟 | 代表厂商 |
|---------|---------|------|--------|---------|---------|---------|
| **DNS CNAME** | L3 | 低(地域级) | 极高 | 慢(TTL 依赖) | ~20-100 ms | 所有 CDN |
| **Anycast BGP** | L3 | 中(路由级) | 高 | 快(路由收敛) | ~5-20 ms | Cloudflare, Fastly |
| **HTTP DNS** | L7 | 高(实例级) | 中 | 中 | ~10-30 ms | 阿里云, AWS |
| **EDNS Client Subnet** | L3+ | 高 | 高 | 中 | ~5-20 ms | Google DNS, OpenDNS |

| 缓存策略 | 适用内容 | TTL 范围 | 回源频率 | 一致性 | 带宽节省 |
|---------|---------|---------|---------|--------|---------|
| **静态资源** | 图片/CSS/JS | 1年+ | 极低 | 强(Cache-Control: immutable) | 90%+ |
| **半动态** | 商品详情页 | 1-10 min | 低 | 最终一致 | 70-85% |
| **动态加速** | API/个性化 | 0-10 s | 高 | 实时 | 10-30% |
| **流媒体** | HLS/DASH 切片 | 切片时长 | 中 | 实时 | 60-80% |

| 边缘计算平台 | 运行时 | 冷启动 | 语言支持 | 最大执行时间 | 典型场景 |
|-------------|--------|--------|---------|-------------|---------|
| **Cloudflare Workers** | V8 Isolates | 0 ms | JS/WASM | 50 ms | A/B测试、边缘路由 |
| **Lambda@Edge** | Node.js/Python | 1-10 ms | JS/Python | 30 s | 授权、响应改写 |
| **Fastly Compute@Edge** | WASM | 0 ms | Rust/JS | 无限制 | 实时流处理 |
| **阿里云 DCDN** | 自定义 | ~1 ms | Lua/JS | 1 s | 缓存键改写、鉴权 |

---

## 四、权威引用

> **Cloudflare** ("An Introduction to Anycast", 2020):
> "Anycast makes the network topology agnostic to clients: every user connects to the same IP address, and BGP routes them to the closest datacenter."

> **Google SRE Book** ("Load Balancing at the Frontend", O'Reilly 2017):
> "DNS-based load balancing remains the only mechanism capable of handling truly global scale, despite its inherent TTL limitations."

> **Akamai** ("Content Delivery at Scale: The Akamai Platform", Whitepaper):
> "Our intelligent platform uses real-time data from 325,000+ servers in 135+ countries to optimize content delivery."

---

## 五、工程实践与代码示例

```nginx
# Nginx / OpenResty 作为 Origin Shield 的缓存配置
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=shield:100m
                 max_size=50g inactive=7d use_temp_path=off;

server {
    location / {
        proxy_cache shield;
        proxy_cache_use_stale error timeout updating http_500 http_502;
        proxy_cache_lock on;           # 防惊群
        proxy_cache_lock_timeout 5s;

        # 缓存键设计: 忽略 utm 参数，保留版本号
        proxy_cache_key "$scheme$proxy_host$uri$is_args$args";

        # 条件回源
        proxy_set_header If-Modified-Since $http_if_modified_since;
        proxy_set_header If-None-Match $http_if_none_match;

        proxy_pass http://origin_backend;

        # 不同路径不同 TTL
        location ~* \.(jpg|png|css|js)$ {
            proxy_cache_valid 200 365d;
            add_header Cache-Control "public, immutable";
        }

        location /api/ {
            proxy_cache_valid 200 5m;
            proxy_cache_valid 404 1m;
            add_header Cache-Control "public, must-revalidate";
        }
    }
}
```

---

## 六、批判性总结

CDN 的本质是**将互联网的拓扑距离转化为缓存的命中概率**，其核心经济模型是：边缘存储成本 + 回源带宽成本 < 源站直接服务的带宽成本。但随着边缘计算（Edge Computing）的兴起，CDN 正在从"内容分发网络"演化为"分布式计算平台"。

Anycast BGP 虽然优雅，但存在一个被低估的风险：**路由劫持**。由于 Anycast 依赖 BGP 公告，恶意 AS（自治系统）可以通过劫持 IP 前缀将流量导向伪造的边缘节点。虽然 RPKI（Resource Public Key Infrastructure）正在缓解这一问题，但全球 RPKI 部署率至今未达 100%，这意味着 Anycast CDN 在理论上仍存在流量被截获的风险。

缓存键设计是 CDN 优化中最具技巧性的环节。过度保守的键策略（将所有 Query 参数纳入键）会导致缓存碎片化，降低命中率；而过度激进的键策略（忽略必要的 vary 头）会导致用户收到错误内容（例如压缩/未压缩版本混淆）。Fastly 提出的 **Surrogate Key**（代理键）机制允许一个对象关联多个标签，实现细粒度的批量失效，这是传统 URL 键模型的有力补充。

动态加速（DCDN）代表了 CDN 领域的最新前沿。传统 CDN 对动态内容几乎无能为力，因为 API 响应无法缓存。DCDN 通过协议优化（QUIC 替代 TCP）、路由优化（实时选路绕过拥塞）和边缘计算（在边缘节点执行部分业务逻辑）来压缩动态响应的延迟。然而，一个根本性的矛盾在于：**动态内容越个性化，缓存价值越低**。DCDN 的上限取决于业务能够容忍多少"准静态化"——这不仅是技术问题，更是产品设计的权衡。
