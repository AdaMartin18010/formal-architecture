# Metrics 指标系统：Prometheus 与 TSDB

> **来源映射**: View/00.md §3.1, Struct/26-可观测性与SRE/00-总览-可观测性的三大支柱与SRE实践.md
> **国际权威参考**: "Prometheus: Up & Running" (Brian Brazil, O'Reilly 2018), Prometheus Docs (v2.50), "Borgmon" (Google, 2003), "Time-Series Database Requirements" (Fabian Reinartz, 2015)

---

## 一、知识体系思维导图

```text
Metrics 指标系统
│
├─► 指标类型 (Prometheus 数据模型)
│   ├─ Counter: 单调递增累计值, rate()/increase() 计算速率
│   ├─ Gauge: 可增可减的瞬时值, 如温度、队列深度
│   ├─ Histogram: 采样值分布到预定义桶 (buckets), histogram_quantile()
│   └─ Summary: 客户端预计算分位数, 滑动时间窗口
│
├─► Prometheus 架构
│   ├─ Pull 模型: 周期性 HTTP scrape /metrics 端点
│   ├─ Service Discovery: Kubernetes, Consul, EC2, file-based
│   ├─ PromQL: 多维数据查询语言, 向量操作, 聚合
│   ├─ Alertmanager: 分组、抑制、静默、路由
│   └─ TSDB: 自定义时序数据库, 块存储 (2h chunks), mmap
│
├─► TSDB 存储引擎
│   ├─ 内存: head block (最近2h), WAL 预写日志
│   ├─ 磁盘: 不可变块 (chunk files, index, tombstones)
│   ├─ 压缩: Gorilla XOR 压缩 ( float ), 16x 压缩比
│   ├─ 保留: 时间或大小-based 保留, 自动压缩 (compaction)
│   └─ 远程存储: Remote Write / Remote Read (Thanos, Cortex, Mimir)
│
└─► 高可用与扩展
    ├─ 联邦 (Federation): 层级聚合, 全局视图
    ├─ Thanos: Sidecar + Query + Store + Compactor, 对象存储后端
    ├─ Cortex: 多租户, 水平扩展, DynamoDB/Cassandra 索引
    └─ Grafana Mimir: Grafana Labs 的 Cortex 分支, 简化运维
```

---

## 二、核心概念的形式化定义

```text
定义 (Prometheus 数据模型):
  TimeSeries = ⟨metric_name, labelSet[], timestamp, value⟩

  LabelSet = {label₁=value₁, label₂=value₂, ...}
  唯一性约束:
    ∀ts₁, ts₂ ∈ TSDB:
      ts₁.metric_name = ts₂.metric_name ∧ ts₁.labelSet = ts₂.labelSet
      → ts₁ = ts₂   (同一时序)

定义 (指标类型):
  Counter(t) ∈ ℝ⁺, 单调性: Counter(t₂) ≥ Counter(t₁)  ∀t₂ > t₁

  Gauge(t) ∈ ℝ, 无约束

  Histogram = ⟨buckets[], sum, count⟩
    buckets = {(le₁, c₁), (le₂, c₂), ..., (+Inf, cₙ)}
    where cᵢ = count(samples ≤ leᵢ)

  Summary = ⟨quantiles[], sum, count⟩
    quantiles = {(φ₁, v₁), (φ₂, v₂), ...}  where φ ∈ [0, 1]

定义 (PromQL 向量):
  InstantVector = {⟨metric, labels, t, v⟩}   // 单时间戳
  RangeVector   = {⟨metric, labels, [t₁,t₂], [v₁,v₂,...]⟩}  // 时间窗口

定义 (TSDB 压缩):
  GorillaCompression(valueᵢ, valueᵢ₋₁):
    xor = valueᵢ.bits XOR valueᵢ₋₁.bits
    leading_zeros = count_leading_zero(xor)
    trailing_zeros = count_trailing_zero(xor)
    存储: (leading_zeros, meaningful_bits, meaningful_value)
```

---

## 三、多维矩阵对比

| 指标类型 | 数学性质 | 适用场景 | 聚合方式 | 典型查询 |
|---------|---------|---------|---------|---------|
| **Counter** | 单调递增 | 请求总数、错误总数、字节传输 | rate(), increase() | `rate(http_requests_total[5m])` |
| **Gauge** | 任意变化 | 温度、内存使用、并发连接 | avg(), max(), min() | `node_memory_used_bytes` |
| **Histogram** | 分布累积 | 请求延迟、响应大小 | histogram_quantile() | `histogram_quantile(0.99, rate(http_duration_bucket[5m]))` |
| **Summary** | 预计算分位 | 严格 SLA 监控 | 直接读取 | `http_request_duration_seconds{quantile="0.99"}` |

| 方案 | 存储模型 | 扩展性 | 多租户 | 长期存储 | 运维复杂度 |
|-----|---------|--------|--------|---------|-----------|
| **单实例 Prometheus** | 本地 TSDB | 垂直 | 无 | 有限 | 低 |
| **Thanos** | 对象存储 (S3) | 水平 | 无 | 无限 | 中 |
| **Cortex** | 块存储 + 索引 | 水平 | 原生 | 无限 | 高 |
| **Grafana Mimir** | 对象存储 | 水平 | 原生 | 无限 | 中 |
| **VictoriaMetrics** | 自定义 LTS | 垂直/水平 | 部分 | 高 | 低 |
| **InfluxDB** | TSM / IOx | 集群版 | 企业版 | 高 | 中 |

---

## 四、权威引用

> **Fabian Reinartz** (Prometheus 核心维护者, KubeCon 2015):
> "Pull-based monitoring is superior for dynamic environments because the monitoring system can control the scrape frequency and detect down targets from its own perspective."

> **Brian Brazil** ("Prometheus: Up & Running", O'Reilly 2018):
> "Counters should never be downsampled. A counter's value at any point in time is meaningless; only its rate of change matters."

> **Björn Rabenstein** (Prometheus 联合创始人):
> "Histograms are more powerful than Summaries because they allow server-side aggregation and arbitrary quantile calculation. Summaries lock you into the quantiles chosen at instrumentation time."

> **Rob Skillington** (M3DB 作者, Uber):
> "At Uber's scale, single-node Prometheus was insufficient. M3 provided a distributed, replicated time-series database while maintaining PromQL compatibility."

---

## 五、工程实践与代码示例

**Histogram 指标定义 (Go client):**

```go
var requestDuration = prometheus.NewHistogramVec(
    prometheus.HistogramOpts{
        Name:    "http_request_duration_seconds",
        Help:    "HTTP request latency distribution",
        Buckets: prometheus.DefBuckets, // [0.005, 0.01, 0.025, ..., 10]
    },
    []string{"method", "status"},
)

// 使用
requestDuration.WithLabelValues("GET", "200").Observe(duration.Seconds())
```

**PromQL 核心查询:**

```promql
-- 99分位延迟 (_histogram_quantile 必须配合 rate)
histogram_quantile(0.99,
  sum by (le) (rate(http_request_duration_seconds_bucket[5m]))
)

-- 错误率 (/status=~"5..")
sum(rate(http_requests_total{status=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))

-- 内存使用率
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes)
/
node_memory_MemTotal_bytes
```

---

## 六、批判性总结

Prometheus 的 Pull 模型在动态云原生环境中是优雅的设计——监控目标无需知道监控服务器的地址，服务发现自动处理扩缩容，失败的 scrape 天然构成"目标不可达"的告警信号。但这一模型在**防火墙/NAT 后方**或**批处理任务**（Job 完成后即消失）场景下显得笨拙，Pushgateway 的引入虽缓解了问题，却打破了数据模型的纯粹性。

Histogram 与 Summary 的选择是 Metrics 工程中最常见的决策陷阱：Summary 在客户端预计算分位数，无法聚合（多个实例的 99 分位不等于全局 99 分位），却提供了精确的滑动窗口；Histogram 支持服务端聚合，但桶边界预设导致分位数计算存在误差，且桶数量爆炸会影响 TSDB 性能。Prometheus 的 `histogram_quantile()` 假设数据线性分布，在桶边界附近产生系统性偏差，这在微秒级延迟场景中尤为明显。

TSDB 的存储引擎设计体现了时序数据的特殊性：Gorilla XOR 压缩对浮点序列可达 16x 压缩比，但高基数（high cardinality）问题——即唯一时间序列数量爆炸（如 user_id、request_id 等无界标签）——是 Prometheus 的**阿喀琉斯之踵**。单实例 Prometheus 的推荐上限约 1000 万时间序列，超过此阈值查询延迟和内存占用将急剧恶化。Thanos、Cortex、Mimir 等分布式方案通过对象存储和查询分片解决了扩展性问题，但引入了 eventual consistency 和跨集群查询的复杂性。2026 年的趋势是 **Native Histograms (exponential buckets)**——用指数间隔桶替代线性桶，在减少桶数量的同时保持分位数精度，以及 **OTLP 直接摄入**——绕过 Prometheus 数据模型，让 OpenTelemetry 生态直接对接后端存储。
