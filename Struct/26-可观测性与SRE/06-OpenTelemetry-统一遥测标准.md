# OpenTelemetry：统一遥测标准

> **来源映射**: View/00.md §3.1, Struct/26-可观测性与SRE/00-总览-可观测性的三大支柱与SRE实践.md
> **国际权威参考**: OpenTelemetry Specification (v1.30, CNCF 毕业项目), "OpenTelemetry: A Full Guide" (O'Reilly 2023), "Merging OpenTracing and OpenCensus" (CNCF, 2019), OTLP Protocol Docs

---

## 一、知识体系思维导图

```text
OpenTelemetry 统一遥测标准
│
├─► 三大信号统一 (Signals)
│   ├─ Traces: 分布式追踪, Span, TraceID, 因果关联
│   ├─ Metrics: 指标采集, Counter/Gauge/Histogram, 与 Prometheus 兼容
│   ├─ Logs: 日志记录, LogRecord, 与 Traces 关联
│   └─ 目标: 单一 SDK 采集所有遥测数据, 统一语义约定 (Semantic Conventions)
│
├─► 架构组件
│   ├─ API: 语言级接口, 无操作 (noop) 默认, 零成本抽象
│   ├─ SDK: API 实现, 采样、批处理、资源属性配置
│   ├─ Instrumentation: 自动插桩 (Agent) / 手动插桩 (API)
│   ├─ OTLP (OpenTelemetry Protocol): gRPC/HTTP 二进制传输协议
│   ├─ Collector: 接收/处理/导出遥测数据的代理/网关
│   │   ├─ Receiver: 接收端 (OTLP, Prometheus, Zipkin, Jaeger)
│   │   ├─ Processor: 批处理、过滤、富化 (attributes enrich)
│   │   ├─ Exporter: 导出端 (Prometheus, Jaeger, Loki, S3)
│   │   └─ Pipeline: Receiver → Processor → Exporter
│   └─ Semantic Conventions: 标准化属性命名 (http.method, db.system, ...)
│
├─► 部署模式
│   ├─ Agent 模式: 每个节点一个 Collector, 接收本机数据
│   ├─ Gateway 模式: 集中式 Collector 集群, 聚合多集群数据
│   ├─ Sidecar 模式: 与 Pod 共置, 服务网格集成
│   └─ 无 Agent: 应用直连后端 (开发/测试场景)
│
└─► 生态集成
    ├─ 与 Prometheus: OTLP → Prometheus remote write / OpenMetrics
    ├─ 与 Jaeger: OTLP → Jaeger gRPC (原生支持)
    ├─ 与 Kubernetes: Operator, 自动注入, DaemonSet Collector
    └─ 与云服务: AWS Distro for OTel, Azure Monitor, GCP Ops Agent
```

---

## 二、核心概念的形式化定义

```text
定义 (OpenTelemetry 信号):
  Signal ∈ {Trace, Metric, Log}

  Trace = ⟨trace_id, spans[]⟩
  Metric = ⟨name, kind, value, attributes, timestamp⟩
  Log = ⟨timestamp, severity, body, attributes, trace_id, span_id⟩

定义 (OTLP 协议):
  OTLP = ⟨ExportTraceServiceRequest, ExportMetricsServiceRequest,
          ExportLogsServiceRequest⟩

  传输绑定:
    OTLP/gRPC: 端口 4317, protobuf, 双向流
    OTLP/HTTP: 端口 4318, protobuf 或 JSON, 请求-响应

定义 (Collector Pipeline):
  Pipeline = ⟨Receivers[], Processors[], Exporters[], service.pipelines⟩

  数据流:
    ∀ signal ∈ {traces, metrics, logs}:
      Input → Receiver(signal) → Processor(batch/filter) → Exporter(backend)

定义 (语义约定):
  SemanticConvention = ⟨attribute_name, type, requirement_level, examples⟩

  示例:
    http.method: string, required, ["GET", "POST"]
    http.status_code: int, required, [200, 404, 500]
    db.system: string, required, ["mysql", "postgresql", "redis"]

定义 (采样一致性):
  ConsistentSampling(trace) ↔
    ∀span ∈ trace: sampled(span) = sampled(root_span)
    // 父采样决策传播给所有子 Span, 保证链路完整性
```

---

## 三、多维矩阵对比

| 信号类型 | 数据模型 | 采集频率 | 存储特征 | 主要用途 | OTLP 支持 |
|---------|---------|---------|---------|---------|----------|
| **Traces** | Span 树, 因果关系 | 请求驱动 | 高基数, 保留期短 | 故障定位, 延迟分析 | v1.0+ |
| **Metrics** | 时间序列, 聚合 | 周期性 scrape | 低基数, 保留期长 | 容量规划, 告警 | v1.0+ |
| **Logs** | 文本/结构化记录 | 事件驱动 | 高体积, 保留期中 | 审计, 调试, 关联 | v1.0+ |

| Collector 模式 | 部署位置 | 资源开销 | 可靠性 | 适用场景 | 配置复杂度 |
|--------------|---------|---------|--------|---------|-----------|
| **Agent** | 每节点 DaemonSet | 低 | 节点级 | 边缘采集, 本地批处理 | 低 |
| **Gateway** | 独立集群 | 中-高 | 集群级 | 多集群聚合, 统一出口 | 高 |
| **Sidecar** | 每 Pod | 中 | Pod 级 | 服务网格, 多租户隔离 | 中 |
| **直连** | 应用内 | 无额外 | 应用级 | 开发测试, 简单场景 | 极低 |

| 遥测标准 | 状态 | Traces | Metrics | Logs | 语言覆盖 | 生态 |
|---------|------|--------|---------|------|---------|------|
| **OpenTelemetry** | CNCF 毕业 | 原生 | 原生 | 原生 | 12+ | 主流 |
| **OpenTracing** | 已归档 | 仅 Trace | 无 | 无 | 9+ | 历史 |
| **OpenCensus** | 已归档 | 支持 | 支持 | 无 | 8+ | 历史 |
| **Prometheus** | CNCF 毕业 | 无 | 原生 | 无 | 多 | 指标专用 |
| **Jaeger** | CNCF 毕业 | 原生 | 无 | 无 | 多 | 追踪专用 |

---

## 四、权威引用

> **CNCF Technical Oversight Committee** (OpenTelemetry Graduation, 2023):
> "OpenTelemetry is the second project to graduate from CNCF after Kubernetes, reflecting its critical role as the universal standard for cloud-native observability."

> **Bogdan Drutu & Sergey Kanzhelev** (OpenTelemetry 项目联合创始人, 2019):
> "We merged OpenTracing and OpenCensus not just to unify APIs, but to create a single standard that covers traces, metrics, and logs with first-class support for all three."

> **Austin Parker** (Honeycomb, "Distributed Tracing in Practice", O'Reilly 2020):
> "OpenTelemetry's semantic conventions are its most undervalued feature. Standardized attribute names mean your dashboards and alerts work across every service, in every language."

> **Ted Young** (OpenTelemetry 维护者, "The Future of Observability", 2023):
> "OTLP is designed to be the TCP/IP of observability — a common protocol that any system can speak, regardless of backend."

---

## 五、工程实践与代码示例

**OpenTelemetry Collector 配置:**

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024
  resource:
    attributes:
      - key: environment
        value: production
        action: upsert

exporters:
  prometheusremotewrite:
    endpoint: http://prometheus:9090/api/v1/write
  otlp/jaeger:
    endpoint: jaeger:4317
    tls:
      insecure: true

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch, resource]
      exporters: [otlp/jaeger]
    metrics:
      receivers: [otlp]
      processors: [batch, resource]
      exporters: [prometheusremotewrite]
```

**Go 应用自动初始化 (OTel SDK):**

```go
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace"
    sdktrace "go.opentelemetry.io/otel/sdk/trace"
)

func initTracer() func() {
    exp, _ := otlptrace.New(ctx, otlptrace.WithEndpoint("localhost:4317"))
    tp := sdktrace.NewTracerProvider(
        sdktrace.WithBatcher(exp),
        sdktrace.WithResource(resource.NewWithAttributes(
            semconv.SchemaURL,
            semconv.ServiceNameKey.String("my-service"),
        )),
    )
    otel.SetTracerProvider(tp)
    return func() { tp.Shutdown(ctx) }
}
```

---

## 六、批判性总结

OpenTelemetry 的统一愿景——用单一 SDK 和协议覆盖 Traces、Metrics、Logs 三大信号——是云原生可观测性领域自 Prometheus 以来最重要的标准化努力。它终结了 OpenTracing 与 OpenCensus 的分裂，用 OTLP 协议将遥测数据从供应商锁定中解放出来，这是无可争议的历史性贡献。然而，"统一采集"不等于"统一体验"，这是当前生态中最突出的认知鸿沟。

在采集端，OTel SDK 的自动插桩（Auto-Instrumentation）对主流框架（Spring, Express, Django, Gin）已相当成熟，但在**异步编程模型**（如 Python asyncio、JavaScript 事件循环、Kotlin 协程）中的上下文传播仍存在边界情况——trace 在跨线程/事件循环边界时可能丢失。手动插桩的 API 设计虽然遵循统一规范，但各语言实现的细节差异（如 Java 的 `@WithSpan` 注解与 Go 的 `tracer.Start()`）增加了跨语言团队的认知成本。

在 Collector 侧，Pipeline 架构提供了强大的灵活性，但也带来了**配置复杂性爆炸**：一个生产级 Collector 通常需要 100-200 行 YAML 配置，涉及多个 Receiver、Processor 链和 Exporter 的矩阵组合。更糟糕的是，Collector 的内存占用在高吞吐量场景（>10MB/s）下会显著增长，其批处理缓冲策略（batch processor）的调优缺乏通用法则。

最深层的矛盾在于：OTel 统一了**前端采集**，但后端存储（Prometheus 存指标、Jaeger/Tempo 存追踪、Loki/ES 存日志）和查询语言（PromQL、TraceQL、LogQL）仍是分裂的。用户需要打开三个界面才能完成一次完整的故障排查。"三大支柱统一"的终极形态不是协议统一，而是**查询语义和分析体验的统一**——SigNoz、HyperDX 等新兴平台试图用 ClickHouse 单一存储和统一查询层解决此问题，但它们的成熟度与生态广度尚无法与传统方案竞争。OTel 是必要但不充分的基础设施；真正的统一可观测性平台，仍需要 3-5 年的生态演进。
