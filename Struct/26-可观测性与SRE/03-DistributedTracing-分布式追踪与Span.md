# Distributed Tracing：分布式追踪与 Span

> **来源映射**: View/00.md §3.1, Struct/26-可观测性与SRE/00-总览-可观测性的三大支柱与SRE实践.md
> **国际权威参考**: "Dapper, a Large-Scale Distributed Systems Tracing Infrastructure" (Benjamin Sigelman et al., Google, 2010), OpenTelemetry Trace Spec (v1.30), "Mastering Distributed Tracing" (Yuri Shkuro, Packt 2019), Jaeger Architecture Docs

---

## 一、知识体系思维导图

```text
分布式追踪 (Distributed Tracing)
│
├─► 核心概念
│   ├─ Trace: 端到端请求链路的完整表示, 全局唯一 TraceID
│   ├─ Span: 基本工作单元, 具有操作名、起止时间、父引用
│   ├─ SpanContext: 传播上下文 {TraceID, SpanID, TraceFlags, TraceState}
│   ├─ Parent-Child: 因果时序关系 (happens-before)
│   └─ Link: 跨 Trace 的关联 (如批量处理中的关联)
│
├─► 上下文传播 (Context Propagation)
│   ├─ 进程内: 语言运行时 Context (Go context, Java Scope)
│   ├─ 进程间 HTTP: W3C Trace Context header (traceparent/tracestate)
│   ├─ 消息队列: 消息属性注入 SpanContext
│   ├─ gRPC: OpenCensus/OpenTelemetry 拦截器
│   └─ 自动 vs 手动: Agent 字节码注入 / 显式 API 调用
│
├─► 采样策略
│   ├─ 头部采样 (Head-Based): 请求入口处决策, 简单但可能丢弃错误链路
│   ├─ 尾部采样 (Tail-Based): 收集完整链路后决策, 保留错误/慢请求
│   ├─ 概率采样: 固定比例 (如 1%), 实现简单
│   └─ 自适应采样: 基于吞吐量动态调整采样率
│
└─► 实现系统
    ├─ Jaeger: Uber 开源, CNCF 毕业, Agent/Collector/Query/Storage
    ├─ Zipkin: Twitter 开源, 轻量, 兼容 OpenTracing
    ├─ Tempo: Grafana Labs, 对象存储后端, TraceQL
    └─ AWS X-Ray / GCP Cloud Trace / Azure Monitor: 云厂商托管
```

---

## 二、核心概念的形式化定义

```text
定义 (Trace):
  Trace = ⟨trace_id, Span[]⟩

  trace_id: 全局唯一标识符 (16 bytes, W3C 标准)
  ∀ span ∈ Trace: span.trace_id = trace_id

定义 (Span):
  Span = ⟨span_id, parent_span_id, name, start_time, end_time,
          attributes[], events[], links[], status⟩

  duration = end_time - start_time ≥ 0

  父子关系 (DAG):
    parent(span) = {s ∈ Trace | s.span_id = span.parent_span_id}
    Children(s) = {span ∈ Trace | span.parent_span_id = s.span_id}
    ∀ span: depth(span) = 0 if parent(span) = ∅ else depth(parent(span)) + 1

定义 (SpanContext 传播):
  SpanContext = ⟨trace_id, span_id, trace_flags, trace_state⟩

  传播不变性:
    Propagate(ctx, boundary) → ctx'
    where ctx'.trace_id = ctx.trace_id  (trace_id 跨边界保持不变)
    and   ctx'.span_id  = new_span_id   (每个边界生成新 span_id)

定义 (尾部采样决策函数):
  TailSample(trace) = {
    Keep  if ∃span ∈ trace: span.status = ERROR
         ∨ max(duration(span)) > threshold
         ∨ random() < rate
    Drop  otherwise
  }
```

---

## 三、多维矩阵对比

| 维度 | 头部采样 | 尾部采样 | 概率采样 | 自适应采样 |
|------|---------|---------|---------|-----------|
| **决策时机** | 请求入口 | 链路完成 | 请求入口 | 动态调整 |
| **实现复杂度** | 低 | 高 (需缓冲全链路) | 低 | 中 |
| **错误链路保留** | 可能丢失 | 保证保留 | 概率保留 | 概率保留 |
| **存储成本** | 低 | 高 (临时缓冲) | 可控 | 可控 |
| **延迟影响** | 无 | 尾部决策延迟 | 无 | 无 |
| **适用场景** | 高吞吐量 API | 低吞吐量关键链路 | 通用 | 流量波动大 |

| 追踪系统 | 存储后端 | 查询语言 | 采样支持 | 云原生 | 协议支持 |
|---------|---------|---------|---------|--------|---------|
| **Jaeger** | Cassandra/ES/Badger | N/A (UI) | 头/尾/概率 | 优秀 | OTel, Zipkin |
| **Zipkin** | Cassandra/MySQL/ES | N/A | 头/概率 | 良好 | Zipkin B3 |
| **Tempo** | S3/GCS/Azure Blob | TraceQL | 头 (Grafana Agent) | 优秀 | OTel, Zipkin |
| **AWS X-Ray** | 托管 | X-Ray 查询 | 头/概率 | 集成 EKS | AWS 专有 |
| **Datadog APM** | 托管 | 类SQL | 头/尾 | 集成 | DD 专有 |

---

## 四、权威引用

> **Benjamin Sigelman, et al.** ("Dapper", Google, SIGCOMM 2010):
> "Dapper's core value lies in its ubiquity: low enough overhead to be always-on, and simple enough instrumentation to be deployed across virtually all services."

> **Yuri Shkuro** (Uber, "Mastering Distributed Tracing", 2019):
> "A trace without spans is just an ID. The span is where the data lives — timing, tags, logs, and the causal relationships that make tracing useful."

> **W3C Trace Context Working Group** (Recommendation, 2021):
> "The traceparent header represents the incoming request in a tracing system, with a common format for request identification and a proposed mechanism for vendor propagation."

> **Ted Young** (OpenTelemetry 维护者, "Sampling in OpenTelemetry", 2022):
> "Tail-based sampling is the only way to guarantee that interesting traces — those with errors or high latency — are captured. Head-based sampling makes the decision before the interesting events occur."

---

## 五、工程实践与代码示例

**W3C Trace Context HTTP 传播:**

```http
GET /api/orders HTTP/1.1
Host: api.example.com
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
tracestate: congo=t61rcWkgMzE,rwgate=sfKS=8@00
```

**OpenTelemetry 手动创建 Span (Go):**

```go
ctx, span := tracer.Start(ctx, "process-payment",
    trace.WithAttributes(
        attribute.String("payment.method", "credit_card"),
        attribute.Float64("payment.amount", 99.99),
    ),
)
defer span.End()

// 记录事件
span.AddEvent("validation_complete", trace.WithAttributes(
    attribute.Int("items.count", 3),
))

// 设置状态
if err != nil {
    span.RecordError(err)
    span.SetStatus(codes.Error, "payment failed")
}
```

**Jaeger 全链路查询:**

```bash
# 查找包含 error=true 且 duration > 1s 的 trace
jaeger-query/api/traces?service=order-service&tags=error%3Dtrue&minDuration=1s
```

---

## 六、批判性总结

分布式追踪的价值不在于"画出漂亮的调用链火焰图"，而在于**将因果关系注入可观测性数据**：当用户报告"下单失败"时，追踪能将前端按钮点击与后台 17 个微服务中的第 14 个数据库连接超时关联起来。然而，追踪的采用率长期低于指标和日志，根本原因是**插桩成本**——要么需要开发者在每个函数调用处手动传递 context，要么依赖语言 Agent 的字节码注入（如 Java OpenTelemetry Javaagent），后者虽实现自动，但带来的启动延迟和运行时开销在生产环境中常被质疑。

采样策略的选择是追踪工程中的核心决策：头部采样实现简单（在入口网关处根据 trace_id 哈希决策），但其根本缺陷是**在"错误发生前"就决定了是否丢弃整条链路**——一个被采样的健康请求可能包含未被采样的下游错误。尾部采样（如 Jaeger 的 tail-based sampling）通过缓冲完整链路后再决策，能精准保留异常链路，但需要巨大的内存缓冲（典型配置 10-30 秒窗口 × 数千并发链路），且增加了数据出口的延迟。

OpenTelemetry 的 Trace 协议统一了之前分裂的 OpenTracing 和 OpenCensus 生态，这是巨大的进步，但协议统一不等于体验统一：Jaeger UI、Grafana Tempo、Datadog APM 各自的查询语言和分析模型差异巨大，trace 数据从一种后端迁移到另一种后端仍是痛苦的 ETL 工程。更深层的问题是，追踪在**异步消息队列**和**事件驱动架构**中的传播仍不完善——当一条 trace 跨越 Kafka 分区并被消费者组并行处理时，父子关系的语义变得模糊，Link 机制虽能表达关联，却失去了严格的时序保证。追踪的未来是与 eBPF 结合：通过内核可观测性自动捕获网络调用，实现**零插桩追踪**，但这需要内核 5.10+ 和对加密流量（TLS）解析的妥协。
