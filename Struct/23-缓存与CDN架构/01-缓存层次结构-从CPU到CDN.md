# 缓存层次结构：从 CPU 到 CDN

> **来源映射**: View/00.md §2.1
> **国际权威参考**: Hennessy & Patterson《计算机体系结构：量化研究方法》, Netflix EVCache 论文, Akamai CDN 技术白皮书

---

## 一、知识体系思维导图

```text
缓存层次结构 (L1 → L5)
│
├─► L1: CPU 寄存器与缓存
│   ├─► 寄存器 (~0.3 ns)
│   ├─► L1i / L1d Cache (~1 ns, 32-64 KB)
│   ├─► L2 Cache (~4 ns, 256-512 KB)
│   └─► L3 Cache (~10 ns, 8-64 MB, 共享)
│
├─► L2: 应用内缓存 (In-Process)
│   ├─► Guava Cache (Java)
│   ├─► Caffeine (高性能 Java)
│   └─► sync.Map / Ristretto (Go)
│
├─► L3: 进程外缓存 (Remote)
│   ├─► Redis (单线程 + 多线程 IO)
│   ├─► Memcached (多线程)
│   └─► EVCache (Netflix, Memcached 集群)
│
├─► L4: CDN 边缘缓存 (Edge)
│   ├─► Cloudflare Edge Cache
│   ├─► Akamai Intelligent Platform
│   └─► AWS CloudFront /阿里云 CDN
│
└─► L5: 浏览器端缓存 (Client)
    ├─► Service Worker Cache API
    ├─► LocalStorage / IndexedDB
    └─► HTTP Cache (Cache-Control, ETag)
```

---

## 二、核心概念的形式化定义

**定义 1 (局部性原理)**:
设程序访问地址序列为 $A = (a_1, a_2, ..., a_n)$，定义：

- **时间局部性**: $P(a_{t+1} = a_t) > \epsilon$，即短期内重复访问同一地址的概率显著大于均匀分布
- **空间局部性**: $P(|a_{t+1} - a_t| < \delta) > \epsilon$，即访问地址倾向于聚簇

**定义 2 (缓存层次的形式化模型)**:
$$Hierarchy = \langle L_1, L_2, L_3, L_4, L_5, M \rangle$$
其中每层 $L_i = \langle C_i, T_i, H_i \rangle$:

- $C_i$: 容量 (Capacity)
- $T_i$: 访问延迟 (Latency)
- $H_i$: 命中率 (Hit Rate)

**平均内存访问时间 (AMAT)**:
$$AMAT = T_1 + (1 - H_1) \cdot T_2 + (1 - H_1)(1 - H_2) \cdot T_3 + ...$$

**定义 3 (缓存一致性层次)**:
$$Coherence(L_i, L_j) = \begin{cases}
Strong & \text{if } \forall t, Val(L_i, t) = Val(L_j, t) \\
Eventual & \text{if } \lim_{t \to \infty} Val(L_i, t) = Val(L_j, t) \\
None & \text{otherwise}
\end{cases}$$

---

## 三、多维矩阵对比

| 层级 | 典型容量 | 访问延迟 | 命中率要求 | 一致性模型 | 失效策略 |
|------|---------|---------|-----------|-----------|---------|
| **L1 CPU Cache** | 32-64 KB | ~1 ns | 95%+ | 硬件 MESI 协议 | 硬件自动 |
| **L2 应用内缓存** | 10-100 MB | ~1 μs | 80%+ | 强一致(同进程) | TTL / LRU |
| **L3 远程缓存** | 10-1000 GB | ~1 ms | 60%+ | 最终一致 | TTL + 主动失效 |
| **L4 CDN 边缘** | TB 级(分布式) | 10-100 ms | 85%+ | 最终一致 | Cache-Control / 主动刷新 |
| **L5 浏览器缓存** | 用户设备决定 | 0 ms(本地) | 90%+ | 用户控制 | HTTP 头 / 手动清除 |

| 局部性类型 | 适用层级 | 典型场景 | 形式化描述 |
|-----------|---------|---------|-----------|
| **时间局部性** | L1-L3 | 循环变量、热点数据 | $P(a_{t+k} = a_t) \propto 1/k$ |
| **空间局部性** | L1, L4 | 数组遍历、图片/视频 | $P(|a_{t+1} - a_t| < B) \approx 1$ |
| **访问频率局部性** | L2-L3 | 排行榜、配置数据 | Zipf 分布: $f_k \propto 1/k^s$ |

---

## 四、权威引用

> **Hennessy & Patterson** ("Computer Architecture: A Quantitative Approach", 6th Ed.):
> "Cache performance is limited by the 3C model: Compulsory misses, Capacity misses, and Conflict misses."

> **Netflix Technology Blog** ("Announcing EVCache", 2016):
> "EVCache is a memcached-based caching solution that provides fast, reliable access to data stored in multiple AWS Availability Zones."

> **Akamai Technical Whitepaper** ("Content Delivery at Scale"):
> "Edge caching reduces origin load by 80-95% for cacheable content, with median TTFB improvement of 50-70%."

---

## 五、工程实践与代码示例

```python
# Caffeine 风格的多层缓存配置 (伪代码)
class MultiLevelCache:
    def __init__(self):
        self.l2 = Caffeine.newBuilder() \
            .maximumSize(10_000) \
            .expireAfterWrite(5, TimeUnit.MINUTES) \
            .build()
        self.l3 = RedisClusterClient.create(uri)

    def get(self, key):
        # L2 命中?
        value = self.l2.getIfPresent(key)
        if value: return value

        # L3 命中?
        value = self.l3.get(key)
        if value:
            self.l2.put(key, value)  # 回填 L2
            return value

        # 回源
        value = load_from_database(key)
        self.l2.put(key, value)
        self.l3.setex(key, 3600, value)
        return value
```

---

## 六、批判性总结

缓存层次结构的设计本质是**延迟-成本-一致性**的三元权衡。从 L1 到 L5，容量呈指数级增长而延迟呈指数级下降，但一致性保证却从硬件强一致性（MESI 协议）退化到最终一致甚至无保证。

一个常见的工程误区是**过度缓存**：在 L2 和 L3 之间引入过多层级（如本地 Caffeine + Redis + Memcached），导致失效链路复杂化。2013 年 Facebook 的 Memcache 论文揭示了一个关键洞察——**缓存的命中率曲线存在明显的边际递减效应**，当命中率超过 95% 后，再增加容量带来的收益远低于维护成本。

另一个被忽视的维度是**访问模式的非平稳性**。传统缓存假设访问服从 Zipf 分布，但在现代微服务架构中，突发流量（thundering herd）和长尾请求使得静态 TTL 策略失效。Netflix 的 EVCache 采用了**分层 TTL + 热点预加载**的组合策略，其本质是用预测模型替代静态假设。这提示我们：缓存策略正从"被动响应"向"主动预测"演进，而机器学习驱动的缓存预取将成为下一个十年的关键方向。
