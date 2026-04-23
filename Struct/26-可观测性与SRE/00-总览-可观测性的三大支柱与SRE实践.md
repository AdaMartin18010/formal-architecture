# 可观测性与 SRE：总览

> **来源映射**: View/00.md §3.1
> **国际权威参考**: Google SRE Book, "Site Reliability Engineering" (O'Reilly), OpenTelemetry

---

## 一、知识体系思维导图

```text
可观测性与SRE
│
├─► 可观测性三大支柱 (Three Pillars)
│   ├─► Metrics (指标)
│   │   ├─ 时序数据: CPU、内存、QPS、延迟、错误率
│   │   ├─ 聚合维度: Gauge / Counter / Histogram / Summary
│   │   └─ 代表: Prometheus, InfluxDB, Datadog
│   │
│   ├─► Logging (日志)
│   │   ├─ 结构化日志: JSON / Logfmt
│   │   ├─ 日志级别: DEBUG/INFO/WARN/ERROR/FATAL
│   │   ├─ 集中化: ELK / Loki / Splunk
│   │   └─ 关联: TraceID 注入日志
│   │
│   └─► Tracing (追踪)
│       ├─ 分布式追踪: 请求全链路
│       ├─ Span: 操作单元、父子关系、耗时
│       ├─ 采样策略: 头部采样/尾部采样/概率采样
│       └─ 代表: Jaeger, Zipkin, OpenTelemetry
│
├─► SRE 核心实践
│   ├─► SLO (Service Level Objective)
│   │   ├─ 定义: 服务可靠性目标
│   │   ├─ SLI (Indicator): 可量化指标 (如 99.9% 可用性)
│   │   └─ 错误预算 (Error Budget): 100% - SLO
│   │
│   ├─► 监控与告警
│   │   ├─ 告警分级: P0(立即) / P1(4h) / P2(24h)
│   │   ├─ 告警 fatigue: 减少误报、Actionable告警
│   │   └─ 自动化: 自动恢复、Runbook驱动
│   │
│   ├─► 混沌工程 (Chaos Engineering)
│   │   ├─ 假设: 系统某部分故障，整体是否仍可用
│   │   ├─ 实验: 随机终止实例、网络延迟、CPU耗尽
│   │   └─ 代表: Chaos Monkey, Gremlin, Litmus
│   │
│   └─► 容量规划
│       ├─ 负载测试: 峰值模拟
│       ├─ 自动扩缩容: HPA/VPA/Cluster Autoscaler
│       └─ 排队论: Little定律应用
│
└─► OpenTelemetry (统一标准)
    ├─ 统一 API/SDK: 语言无关的插桩标准
    ├─ Collector: 接收/处理/导出遥测数据
    └─ OTLP: OpenTelemetry Protocol (gRPC/HTTP)
```

---

## 二、SLO 与错误预算的形式化

```text
定义 (SLO):
  SLO = ⟨SLI, Target, Window⟩

  SLI: 服务级别指标，如 "HTTP 2xx 请求比例"
  Target: 目标值，如 99.9%
  Window: 评估窗口，如 30天

  错误预算:
    ErrorBudget = 1 - Target = 0.1% (30天 ≈ 43分钟)

  工程决策:
    - 错误预算充足 → 允许发布新功能
    - 错误预算耗尽 → 冻结发布，优先修复稳定性
```

---

## 三、Metrics 类型对比

| 类型 | 定义 | 示例 | 适用场景 |
|------|------|------|---------|
| **Gauge** | 可增可减的瞬时值 | 当前温度、内存使用量 | 状态快照 |
| **Counter** | 单调递增的累计值 | 总请求数、总错误数 | 速率计算 (rate()) |
| **Histogram** | 采样值分布到桶中 | 请求延迟分布 | P50/P95/P99 分位数 |
| **Summary** | 客户端计算的分位数 | 请求延迟的99分位 | 无需服务端聚合 |

---

## 四、权威引用

> **Google SRE Book** (2016):
> "Hope is not a strategy." —— SRE 的核心是系统性消除对"希望"的依赖。

> **Cindy Sridharan** ("Distributed Systems Observability" 作者):
> "Monitoring tells you whether the system works. Observability lets you ask why it's not working."

> **Charity Majors** (Honeycomb CEO):
> "Observability is about being able to ask any question about your system, without having to know the question in advance."

---

## 五、子主题导航

| 序号 | 子主题文件 | 核心内容 |
|------|-----------|---------|
| 01 | [01-Metrics指标系统-Prometheus与TSDB](./01-Metrics指标系统-Prometheus与TSDB.md) | Gauge/Counter/Histogram、PromQL |
| 02 | [02-Logging日志系统-结构化与集中化](./02-Logging日志系统-结构化与集中化.md) | ELK/Loki、日志级别、TraceID关联 |
| 03 | [03-DistributedTracing-分布式追踪与Span](./03-DistributedTracing-分布式追踪与Span.md) | Jaeger/Zipkin、采样策略、OpenTelemetry |
| 04 | [04-SRE实践-SLO错误预算与告警](./04-SRE实践-SLO错误预算与告警.md) | SLI/SLO/SLA、错误预算、告警分级 |
| 05 | [05-混沌工程-故障注入与韧性验证](./05-混沌工程-故障注入与韧性验证.md) | Chaos Monkey、假设验证、安全实验 |
| 06 | [06-OpenTelemetry-统一遥测标准](./06-OpenTelemetry-统一遥测标准.md) | OTLP、Collector、语言SDK |

---

## 六、批判性总结

监控 (Monitoring) 与可观测性 (Observability) 的本质区别：**监控基于已知问题设计仪表盘；可观测性允许对未知问题进行探索性分析**。传统监控回答"系统是否工作"，可观测性回答"系统为什么不工作"。

OpenTelemetry 是 CNCF 的第二个毕业项目（继 Kubernetes 之后），其目标是统一 Metrics/Logs/Traces 的采集标准。但 2026 年的现实是：**三大支柱仍未真正统一**——存储后端分离（Prometheus 存指标、Loki 存日志、Jaeger 存追踪）、查询语言不统一。统一的可观测性平台仍是愿景，而非现实。
