# Flink 流处理：Event Time 与 Watermark

> **来源映射**: View/00.md §3.1
> **国际权威参考**: "Streaming Systems" (Akidau et al.), Flink Documentation, "The Dataflow Model" (Google, 2015)

---

## 一、知识体系思维导图

```text
Flink 流处理核心机制
│
├─► 时间语义
│   ├─ Event Time: 事件产生的时间 (业务时间)
│   ├─ Ingestion Time: 事件进入 Flink 的时间
│   └─ Processing Time: 算子处理事件的时间 (机器时间)
│
├─► Watermark (水印)
│   ├─► 定义
│   │   ├─ 特殊事件，携带时间戳 t
│   │   ├─ 语义: "所有 Event Time ≤ t 的事件都已到达"
│   │   └─ 触发: 窗口计算、超时处理
│   │
│   ├─► 生成策略
│   │   ├─ 周期性: 固定间隔生成 (默认 200ms)
│   │   ├─ 标记驱动: 每事件检查生成条件
│   │   └─ 空闲超时: 某分区无数据时的处理
│   │
│   └─► 迟到数据
│       ├─ 定义: Watermark 已超过窗口结束，但事件到达
│       ├─ 处理: 丢弃 / 允许迟到 (allowedLateness) / 侧输出流
│       └─ 根源: 网络延迟、乱序到达、时钟偏差
│
├─► 窗口操作
│   ├─ Tumbling Window: 固定大小、不重叠 (如每5分钟)
│   ├─ Sliding Window: 固定大小、可重叠 (如每5分钟统计过去10分钟)
│   ├─ Session Window: 活动间隙触发 (如 30分钟无活动则关闭)
│   └─ Global Window: 全局单一窗口，需自定义触发器
│
├─► 状态管理
│   ├─ Keyed State: 每个 key 独立状态 (ValueState, ListState, MapState)
│   ├─ Operator State: 每个算子实例状态
│   ├─ State Backend: HashMapStateBackend / RocksDBStateBackend
│   └─ Checkpoint: 一致性快照 (Chandy-Lamport 算法)
│
└─► Exactly-Once 语义
    ├─ Checkpoint 屏障 (Barrier): 全局快照标记
    ├─ 两阶段提交: 预写日志 + 外部系统事务
    └─ 端到端: Kafka (offset) → Flink (state) → Sink (事务)
```

---

## 二、核心概念的形式化定义

### 2.1 Event Time 与 Watermark

```text
定义 (时间语义):
  设事件 e 的时间属性:
    T_event(e): 事件产生时间 (嵌入事件本身)
    T_ingest(e): 事件进入系统时间
    T_process(e): 事件被处理时间

  理想情况: T_event = T_ingest = T_process
  实际情况: T_event ≤ T_ingest ≤ T_process (存在延迟和乱序)

  乱序度:
    out_of_orderness = T_process - T_event
    典型值: 毫秒到分钟级

  Watermark:
    W(t) = max(T_event) - max_allowed_lateness
    语义: 系统相信所有 Event Time < W(t) 的事件都已到达

  窗口触发条件:
    当 Watermark ≥ window_end_time 时，触发窗口计算

  迟到事件:
    late_event(e) ⟺ T_event(e) < window_end_time ≤ W(current)
    即: 事件本应在窗口内，但到达时窗口已关闭
```

### 2.2 Checkpoint 机制

```text
定义 (分布式快照):
  Flink 使用 Chandy-Lamport 算法的变体:

  1. JobManager 向所有 Source 注入 Checkpoint Barrier
  2. Source 在数据流中插入 Barrier，保存自身状态
  3. 算子收到 Barrier 后:
     - 暂停处理该 Barrier 之后的数据
     - 保存当前状态到 State Backend
     - 转发 Barrier 到下游
  4. 当所有 Sink 确认收到 Barrier 并保存状态:
     - Checkpoint 完成
     - 通知所有算子继续处理

  一致性保证:
    Checkpoint 成功 ⟹ 所有算子状态一致，恰好处理到 Barrier 位置

  恢复:
    失败时从最近 Checkpoint 恢复，重放 Barrier 之后的数据
```

---

## 三、窗口类型对比矩阵

| 窗口类型 | 大小 | 重叠 | 触发条件 | 适用场景 | 复杂度 |
|---------|------|------|---------|---------|--------|
| **Tumbling** | 固定 | ❌ 无 | 时间到 | 固定周期统计 | 低 |
| **Sliding** | 固定 | ✅ 有 | 滑动步长 | 移动平均、趋势 | 中 |
| **Session** | 动态 | ❌ 无 | 活动间隙 | 用户行为分析 | 高 |
| **Global** | 无限 | N/A | 自定义 | 全局聚合 | 低 |
| **Count** | 事件数 | ❌ 无 | 事件数到 | 批量处理 | 低 |

---

## 四、权威引用

> **Tyler Akidau** ("Streaming Systems" 作者):
> "Event time is the only time that matters for correctness."

> **Google Dataflow Team** ("The Dataflow Model", 2015):
> "We propose a model that allows for the natural expression of both batch and streaming computations, with a focus on what is computed, rather than how."

> **Apache Flink 文档**:
> "Flink is a distributed processing engine for stateful computations over unbounded and bounded data streams."

> **Martin Kleppmann**:
> "Stream processing is not just about low latency; it's about processing data in the order it happened."

---

## 五、工程实践

### 5.1 Flink Event Time 与 Watermark

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);

DataStream<Event> stream = env
    .addSource(new KafkaSource<>())
    .assignTimestampsAndWatermarks(
        WatermarkStrategy
            .<Event>forBoundedOutOfOrderness(Duration.ofSeconds(30))
            .withTimestampAssigner((event, timestamp) -> event.getEventTime())
    );

// 窗口聚合
stream
    .keyBy(Event::getUserId)
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .allowedLateness(Time.minutes(2))  // 允许 2 分钟迟到
    .sideOutputLateData(lateDataTag)   // 迟到数据侧输出
    .aggregate(new CountAggregate());
```

### 5.2 Watermark 生成策略

```java
// 1. 周期性 Watermark (默认 200ms)
WatermarkStrategy.<Event>forBoundedOutOfOrderness(Duration.ofSeconds(30))

// 2. 标记驱动 Watermark
WatermarkStrategy.<Event>forGenerator(ctx -> new WatermarkGenerator<Event>() {
    private long maxTimestamp = Long.MIN_VALUE;

    @Override
    public void onEvent(Event event, long eventTimestamp, WatermarkOutput output) {
        maxTimestamp = Math.max(maxTimestamp, eventTimestamp);
    }

    @Override
    public void onPeriodicEmit(WatermarkOutput output) {
        output.emitWatermark(new Watermark(maxTimestamp - 30000)); // 30s 延迟
    }
});

// 3. 空闲 Source 处理
WatermarkStrategy.<Event>forBoundedOutOfOrderness(Duration.ofSeconds(30))
    .withIdleness(Duration.ofMinutes(5));  // 5分钟无数据则标记空闲
```

---

## 六、批判性总结

Watermark 是流处理中最优雅的概念之一：它用**不完美的时间估计**来平衡**延迟**与**完整性**。但 Watermark 的本质是一个**启发式假设**——它假设"最大延迟不超过 X"，而这个假设在网络故障、系统重载时往往不成立。Watermark 的失效不是 bug，而是**工程现实的必然**。

Flink 的 Checkpoint 机制将 Chandy-Lamport 快照算法从理论变为工业现实，但 Checkpoint 的代价是**延迟增加**：Barrier 传播需要等待所有算子同步，大状态（如 TB 级 RocksDB）的快照可能耗时数分钟。这再次验证了分布式系统的永恒真理：**一致性有成本，且成本与状态大小成正比**。

批流一体（Unified Batch & Stream）是 Flink 的愿景，但 2026 年的现实是：**批和流的思维模型仍然不同**。批处理工程师习惯"数据完整后再计算"，流处理工程师接受"永远不完整的数据"。这种思维差异比技术差异更难弥合——它要求组织从"报表驱动"转向"事件驱动"，这是文化变革，而非工具升级。
