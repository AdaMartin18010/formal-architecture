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


---

## 七、概念属性关系网络

### 7.1 核心概念关系表

| 概念A | 关系类型 | 概念B | 关系说明 |
|-------|----------|-------|----------|
| Metrics | 量化 -> | 系统状态 | 时序数值，聚合维度 |
| Logs | 记录 -> | 离散事件 | 结构化/非结构化文本 |
| Traces | 追踪 -> | 请求链路 | 跨服务因果关联 |
| Observability | 包含 -> | Metrics/Logs/Traces | 三大支柱统一 |
| Monitoring | 子集 -> | Observability | 基于已知问题的仪表盘 |
| SLO | 定义 -> | 可靠性目标 | 以用户为中心的服务水平 |
| SLI | 量化 -> | SLO | 服务水平的具体指标 |
| Error Budget | 计算 -> | 100% - SLO | 允许的不稳定窗口 |
| Alerting | 触发 -> | 人工响应 | 基于阈值或异常检测 |
| Incident Response | 处理 -> | 故障 | 事后复盘与系统改进 |

### 7.2 ASCII拓扑图

```text
可观测性三大支柱拓扑
===========================================================

                      +------------------+
                      |   Observability  |
                      |    (可观测性)     |
                      +--------+---------+
                               |
              +----------------+----------------+
              v                v                v
       +-------------+ +-------------+ +-------------+
       |   Metrics   | |    Logs     | |   Traces    |
       |   (指标)    | |   (日志)    | |   (追踪)    |
       +------+------+ +------+------+ +------+------+
              |               |               |
              v               v               v
       +-------------+ +-------------+ +-------------+
       |  Prometheus | |  Loki/ES    | | Jaeger/     |
       |  Counter/   | |  结构化/    | | Zipkin/     |
       |  Gauge/     | |  全文检索   | | Tempo       |
       |  Histogram  | |             | |             |
       +-------------+ +-------------+ +-------------+

SRE 可靠性层次拓扑
===========================================================

       +------------------+
       |      SLA         |
       | (对外合同/赔偿)   |
       +--------+---------+
                |
                v
       +------------------+
       |      SLO         |
       | (内部可靠性目标)  |
       +--------+---------+
                |
                v
       +------------------+
       |      SLI         |
       | (可量化指标)      |
       +--------+---------+
                |
                v
       +------------------+
       |  Error Budget    |
       | (100% - SLO)     |
       +------------------+

===========================================================
```

### 7.3 形式化映射

设可观测性系统为五元组 **O = (M, L, T, C, A)**，其中：

- **M** = 指标空间，每个指标 m = (name, labels, timestamp, value)
- **L** = 日志空间，每条日志 l = (timestamp, level, message, attributes)
- **T** = 追踪空间，每个 trace = {span1, span2, ...}，span = (trace_id, span_id, parent_id, operation, start, end)
- **C** = 关联函数 Correlation: M x L x T -> Context，将三类信号关联到同一上下文
- **A** = 分析查询语言 {PromQL, LogQL, TraceQL}

SRE 可靠性模型形式化为：

- SLI = f(metrics) in [0, 1]
- SLO = target(SLI) in [0, 1]
- ErrorBudget = 1 - SLO
- BurnRate = d(ErrorConsumed)/dt

---

## 八、形式化推理链

**公理 1（可观测性公理）**：系统的可观测性等于通过其外部输出推断内部状态的能力。
Observability(System) = |{internal_state | infer(external_outputs, state)}| / |AllStates|

**公理 2（错误预算守恒）**：在观测窗口内，错误预算是固定的；提前耗尽意味着禁止变更直到窗口重置。
forall window, ErrorBudget(window) = const, if Consumed >= Budget then FreezeDeployments = True

**引理 1（Metrics 的低基数约束）**：Prometheus 的 TSDB 设计假设时间序列数量（cardinality）有界，高基数标签（如 user_id、request_id）导致性能退化。
*证明*：TSDB 为每个时间序列维护独立的内存头和磁盘块，基数爆炸使索引（inverted index）和压缩率恶化。单实例 Prometheus 推荐上限约 1000 万序列。参见 Ganesh Vernekar (2022) "Lifecycle of a Sample in Prometheus TSDB", USENIX SREcon。

**引理 2（追踪采样的完备性-效率权衡）**：100% 采样提供完整因果图但带来存储和性能开销；头部采样无法捕获下游错误，尾部采样需要大内存缓冲。
*证明*：头部采样在请求入口处决策，无法预知下游是否出错；尾部采样缓冲完整 trace 后决策，内存需求与并发请求数和缓冲窗口成正比。参见 Yuri Shkuro (2019) "Mastering Distributed Tracing", Packt Publishing。

**定理 1（监控盲区定理）**：基于已知问题设计的仪表盘（dashboards）无法捕获未知故障模式。
*形式化*：forall dashboard d, fault f, if f not in assumptions(d) then detect(d, f) = False
*证明*：传统监控基于预定义指标和阈值，而未知故障模式（如级联失效的新路径、新类型的资源泄漏）不产生预期信号。可观测性通过保留高基数原始数据（如结构化日志、分布式追踪）支持探索性查询，从而降低盲区。参见 Charity Majors (2021) "Observability Engineering", OReilly。

**定理 2（错误预算决策定理）**：错误预算将可靠性决策从定性争论转化为定量规则。
*形式化*：if ErrorBudgetRemaining > Threshold then Allow(feature_deployments) else Block(deployments) and Require(reliability_work)
*证明*：错误预算提供了双方（产品团队 vs SRE 团队）都认可的中立仲裁指标，消除了主观优先级冲突。参见 Betsy Beyer et al. (2016) "Site Reliability Engineering", OReilly, Chapter 2。

**推论 1**：三大支柱的统一采集（OpenTelemetry）不等于统一分析——存储后端分离（Prometheus/Loki/Jaeger）和查询语言差异（PromQL/LogQL/TraceQL）仍迫使工程师在多个系统间跳转以完成故障排查。

**推论 2**：SLO 的设计是政治过程而非纯技术过程：过于宽松损害用户信任，过于严格导致成本指数增长。Google 的四个九（99.99%）不是技术最优解，而是成本-收益曲线的拐点。

---

## 九、ASCII推理判定树

### 9.1 可观测性数据选型决策树

```text
可观测性数据类型选型
===========================================================

                      +-------------+
                      | 排查什么问题?|
                      +------+------+
                             |
            +----------------+----------------+
            v                v                v
         系统性能          业务逻辑          跨服务链路
            |                |                |
            v                v                v
    +-------------+  +-------------+  +-------------+
    |   Metrics   |  |    Logs     |  |   Traces    |
    | (延迟/吞吐) |  | (事件详情)  |  | (调用链路)  |
    +------+------+  +------+------+  +------+------+
           |                |                |
           v                v                v
    工具:              工具:            工具:
    - Prometheus       - Loki         - Jaeger
    - Grafana          - Elasticsearch - Tempo
    - Datadog          - Splunk       - Zipkin

===========================================================
```

### 9.2 SLO 设计决策树

```text
SLO 设计决策
===========================================================

                      +-------------+
                      | 服务关键度?  |
                      +------+------+
                             |
            +----------------+----------------+
            v                v                v
         关键核心          重要服务          内部工具
            |                |                |
            v                v                v
    +-------------+  +-------------+  +-------------+
    |  99.99%     |  |   99.9%     |  |   99%       |
    | (52.6m/年)  |  | (8.8h/年)   |  | (3.65d/年)  |
    +------+------+  +------+------+  +------+------+
           |                |                |
           v                v                v
    适用:              适用:            适用:
    - 支付系统         - 电商平台       - 内部管理
    - 核心API          - 用户服务       - 非关键工具
    - 身份认证         - 推荐系统       - 批处理系统

===========================================================
```

---

## 十、国际权威课程对齐

### 10.1 课程映射

**MIT 6.172: Performance Engineering**

- **Lecture 1**: Performance Measurement -> 对应 Metrics 采集与基准测试方法
- **Lecture 5**: Profiling -> 对应分布式追踪与性能瓶颈定位
- **Project**: Performance Analysis -> 对应系统性能指标的统计建模

**Stanford CS 240: Advanced Topics in OS**

- **Lecture 3**: Monitoring and Debugging -> 对应可观测性系统的设计原则
- **Lecture 8**: Distributed Tracing -> 对应追踪系统的实现与采样策略

**CMU 15-319: Cloud Computing**

- **Lecture 6**: Cloud Monitoring -> 对应云原生监控架构与告警设计
- **Lecture 10**: SRE Practices -> 对应错误预算与可靠性工程

**Berkeley CS 162: Operating Systems**

- **Lecture 20**: Performance Evaluation -> 对应系统性能度量与实验设计
- **Project 4**: Web Server Performance -> 对应延迟、吞吐量和资源利用率分析

### 10.2 核心参考文献

1. Betsy Beyer, Chris Jones, Jennifer Petoff, Niall Richard Murphy (2016). Site Reliability Engineering: How Google Runs Production Systems. OReilly. SRE 领域的奠基之作，涵盖错误预算、事后复盘和可靠性设计。

2. Charity Majors, Liz Fong-Jones, George Miranda (2021). Observability Engineering. OReilly. 系统论述了可观测性三大支柱的理论基础与实践方法。

3. Cindy Sridharan (2018). Distributed Systems Observability. OReilly. 从分布式系统视角阐述了监控、日志和追踪的集成策略。

4. Ganesh Vernekar (2022). Lifecycle of a Sample in Prometheus TSDB. USENIX SREcon APAC. Prometheus TSDB 存储引擎的深入解析。

---

## 十一、深度批判性总结

监控（Monitoring）与可观测性（Observability）的本质区别：监控基于已知问题设计仪表盘；可观测性允许对未知问题进行探索性分析。传统监控回答系统是否工作，可观测性回答系统为什么不工作。这一区分不仅是术语之争，而是反映了对系统认知论的根本不同——监控假设我们预先知道什么可能出错，可观测性承认系统的复杂性超出人类的事先想象。

OpenTelemetry 是 CNCF 的第二个毕业项目（继 Kubernetes 之后），其目标是统一 Metrics/Logs/Traces 的采集标准。但 2026 年的现实是：三大支柱仍未真正统一——存储后端分离（Prometheus 存指标、Loki 存日志、Jaeger 存追踪）、查询语言不统一。统一的可观测性平台仍是愿景，而非现实。

SRE 的错误预算概念是软件工程史上最优雅的管理工具之一：它将抽象的可靠性转化为可量化的预算，使产品团队与工程团队有了共同语言。但 SLO 的设计是一个政治过程而非技术过程：过于宽松的 SLO（如 99%）意味着允许 7.2 小时/月的宕机，可能损害用户信任；过于严格的 SLO（如 99.999%）意味着仅允许 26 秒/月，成本呈指数增长。Google 的四个九（99.99%）不是技术最优解，而是成本-收益曲线的拐点——再往上每增加一个九，成本增加 10 倍，收益边际递减。
