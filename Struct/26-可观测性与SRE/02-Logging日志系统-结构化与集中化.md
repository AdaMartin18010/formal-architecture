# Logging 日志系统：结构化与集中化

> **来源映射**: View/00.md §3.1, Struct/26-可观测性与SRE/00-总览-可观测性的三大支柱与SRE实践.md
> **国际权威参考**: "The Log: What every software engineer should know" (Jay Kreps, LinkedIn, 2013), "ELK Stack" (Elasticsearch, Logstash, Kibana), Grafana Loki Docs, "Structured Logging" (Go log/slog, 2023)

---

## 一、知识体系思维导图

```text
Logging 日志系统
│
├─► 日志级别与语义
│   ├─ DEBUG: 开发调试信息, 生产环境通常关闭
│   ├─ INFO:  正常运行状态报告, 业务流程节点
│   ├─ WARN:  潜在问题, 非致命异常, 降级行为
│   ├─ ERROR: 功能失败, 需要人工介入但系统仍运行
│   └─ FATAL: 系统级崩溃, 进程终止前的最后记录
│
├─► 结构化日志 (Structured Logging)
│   ├─ 传统文本: "User alice logged in from 192.168.1.1"
│   ├─ JSON/Logfmt: {"level":"info","user":"alice","ip":"192.168.1.1","ts":"2024-01-01T00:00:00Z"}
│   ├─ 优势: 可解析、可索引、可聚合、Schema 化
│   └─ 标准: OpenTelemetry LogRecord, ECS (Elastic Common Schema)
│
├─► 集中化日志架构
│   ├─ 采集层:
│   │   ├─ Fluentd / Fluent Bit: CNCF, 轻量高效
│   │   ├─ Promtail: Grafana Loki 专用采集器
│   │   ├─ Logstash: ELK 生态, 功能丰富但资源重
│   │   └─ Vector: Datadog, Rust 编写, 高性能
│   ├─ 存储层:
│   │   ├─ Elasticsearch: 倒排索引, 全文检索, 资源密集
│   │   ├─ Loki: 仅索引标签, 日志内容压缩存储, 轻量
│   │   └─ ClickHouse / Apache Doris: 列式存储, OLAP 分析
│   └─ 查询层: Kibana, Grafana Explore, Datadog Logs
│
└─► 高级实践
    ├─ TraceID 关联: 将分布式追踪 ID 注入每条日志
    ├─ 日志采样: 高吞吐量场景下按比例或分级采样
    ├─ 日志轮转: 本地 retention, 防止磁盘耗尽
    └─ 敏感信息脱敏: PII/密码/Token 的自动掩码
```

---

## 二、核心概念的形式化定义

```text
定义 (日志记录):
  LogRecord = ⟨timestamp, severity, body, attributes[], trace_id, span_id⟩

  severity ∈ {DEBUG, INFO, WARN, ERROR, FATAL}
  body: 人类可读消息 或 结构化键值对
  attributes: {key₁: value₁, key₂: value₂, ...}

定义 (结构化日志):
  StructuredLog = JSON(LogRecord)

  可解析性:
    Parse(StructuredLog) → LogRecord  (确定性的, 无歧义)
    Parse(UnstructuredLog) → LogRecord'  (启发式的, 可能丢失信息)

定义 (日志采样):
  SamplingPolicy = ⟨strategy, rate, condition⟩

  strategy ∈ {Random, LevelBased, HeadBased, TailBased}

  RandomSampling:      Keep(log) ↔ random() < rate
  LevelBasedSampling:  Keep(log) ↔ severity ≥ threshold
  HeadBasedSampling:   Keep(trace) ↔ trace_id mod N < rate
  TailBasedSampling:   Keep(trace) ↔ ∃log ∈ trace: severity ≥ ERROR

定义 (日志关联):
  Correlation(log₁, log₂) ↔
    log₁.trace_id = log₂.trace_id ∨
    log₁.correlation_id = log₂.correlation_id
```

---

## 三、多维矩阵对比

| 日志格式 | 可读性 | 可解析性 | 存储效率 | 查询能力 | 工具生态 |
|---------|--------|---------|---------|---------|---------|
| **纯文本** | 高 | 低 (需正则) | 中 | 全文搜索 | 通用 |
| **Logfmt** | 中 | 中 | 中 | 键值过滤 | Heroku, Go 生态 |
| **JSON** | 低 | 高 | 低 (冗余引号) | 结构化查询 | 通用, 主流 |
| **Protobuf** | 无 | 极高 | 高 | 需解码 | 内部高效传输 |
| **OpenTelemetry** | 中 | 极高 | 高 | 统一语义 | OTel 生态 |

| 日志系统 | 索引策略 | 存储成本 | 查询语言 | 扩展性 | 资源占用 |
|---------|---------|---------|---------|--------|---------|
| **Elasticsearch** | 倒排索引 (全文) | 高 (原始日志 × 1.5) | Lucene DSL | 水平扩展 | 高 (JVM) |
| **Loki** | 仅标签索引 | 低 (对象存储) | LogQL | 水平扩展 | 极低 |
| **ClickHouse** | 稀疏主键索引 | 极低 (列式压缩) | SQL | 水平扩展 | 中 |
| **Splunk** | 专有索引 | 极高 | SPL | 商业集群 | 极高 |
| **Datadog** | 托管索引 | 极高 (按量计费) | 类SQL | SaaS | 无 (托管) |

---

## 四、权威引用

> **Jay Kreps** (LinkedIn, "The Log: What every software engineer should know", 2013):
> "The log is perhaps the simplest possible storage abstraction. It is an append-only, totally-ordered sequence of records ordered by time."

> **Grafana Loki Team** ("Like Prometheus, but for logs", 2019):
> "Loki only indexes labels, not the full log content. This reduces indexing cost by orders of magnitude while maintaining query flexibility through LogQL."

> **Steve Newman** (Google, "Structured Logging at Google", 2015):
> "Unstructured logs are a liability. They require fragile regex parsing, break when formats change, and cannot be aggregated across services."

> **Dave Cheney** (Go 社区领袖, "Let's talk about logging", 2015):
> "There are only two things you should log: things that developers care about when they are developing or debugging software, and things that operators care about when they are operating software."

---

## 五、工程实践与代码示例

**结构化日志输出 (Go slog):**

```go
logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    Level: slog.LevelInfo,
}))

logger.Info("user login",
    slog.String("user_id", "alice"),
    slog.String("ip", "192.168.1.1"),
    slog.String("trace_id", "abc123"),
)
// {"time":"2024-01-01T00:00:00Z","level":"INFO","msg":"user login","user_id":"alice","ip":"192.168.1.1","trace_id":"abc123"}
```

**Loki + Promtail 配置:**

```yaml
# promtail-config.yaml
server:
  http_listen_port: 9080
positions:
  filename: /tmp/positions.yaml
clients:
  - url: http://loki:3100/loki/api/v1/push
scrape_configs:
  - job_name: kubernetes-pods
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: pod
    pipeline_stages:
      - json:
          expressions:
            level: level
            trace_id: trace_id
```

**LogQL 查询示例:**

```logql
-- 查找特定服务的 ERROR 日志
{app="payment-service"} |= "ERROR" | json | level="ERROR"

-- 按 trace_id 关联日志
{app="order-service"} |= "trace_id=\"abc123\""

-- 统计每分钟 ERROR 数量
sum by (level) (rate({app="api"} |= "ERROR" [1m]))
```

---

## 六、批判性总结

日志系统的设计体现了信息检索与存储成本的永恒博弈：Elasticsearch 通过倒排索引提供亚秒级全文检索，但索引体积可达原始日志的 1.5-2 倍，在 PB 级日志场景下存储成本令人望而却步；Loki 放弃全文索引、仅索引标签的策略将成本降低了 1-2 个数量级，但代价是**无标签过滤的查询必须扫描整个时间范围内的日志块**，在宽时间窗口查询时延迟可达分钟级。这一权衡没有普适答案——取决于查询模式是"已知标签的精确定位"还是"未知内容的模糊搜索"。

结构化日志的普及是行业的重要进步，但 JSON 格式本身存在**存储冗余**（键名重复、引号开销）和**解析开销**。在高吞吐量场景（>100MB/s）下，日志采集代理的 JSON 序列化/反序列化 CPU 占用不可忽略，Protobuf 或 MessagePack 等二进制格式在内部传输中越来越受欢迎。日志采样是另一个被低估的实践：在微服务链路中，100% 日志采集往往产生 90% 的无用噪声，基于 Trace 尾采样（仅保留包含错误的完整链路）能在不丢失关键信息的前提下减少 90% 存储。

日志与追踪的融合是 2024-2026 年的明确趋势：OpenTelemetry 的 LogRecord 原生支持 trace_id 和 span_id 字段，使"从日志跳转到追踪"和"从追踪关联日志"成为标准能力。但三大支柱的存储后端分离（Prometheus 存指标、Loki/ES 存日志、Jaeger 存追踪）仍是架构债务——工程师需要在三个系统间跳转以完成一次故障排查。统一存储（如 SigNoz、HyperDX）试图用单一后端（ClickHouse）解决此问题，但各自的查询语言和可视化习惯已形成路径依赖，真正的统一仍任重道远。
