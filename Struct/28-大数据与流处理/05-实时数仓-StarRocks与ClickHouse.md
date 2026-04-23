# 实时数仓：StarRocks 与 ClickHouse

> **来源映射**: View/00.md §3.1, 模块28总览
> **国际权威参考**: "StarRocks: A Next-Generation Sub-second MPP Database" (StarRocks, 2022), "ClickHouse: A Fast Open-Source OLAP DBMS" (Yandex, 2016), "The Snowflake Elastic Data Warehouse" (Dageville et al., SIGMOD 2016), "MonetDB/X100: Hyper-Pipelining Query Execution" (Boncz et al., CIDR 2005)

---

## 一、知识体系思维导图

```text
实时数仓 (Real-Time OLAP)
│
├─► 架构范式: MPP (Massively Parallel Processing)
│   ├─ 无共享架构 (Shared-Nothing)
│   ├─ 数据分片 (Sharding) + 分布式执行
│   ├─ 查询分解为子任务并行执行
│   └─ 协调节点聚合结果
│
├─► StarRocks
│   ├─► 架构特点
│   │   ├─ 存算分离/存算一体 双模式
│   │   ├─ 短路径优化 (Short-Circuit Optimization)
│   │   ├─ 查询缓存 (Query Cache) + 物化视图 (Materialized View)
│   │   └─ 数据湖分析: 查询 Iceberg/Hudi/Delta Lake 外表
│   ├─► 存储引擎
│   │   ├─ MPP + 向量化执行 + 短向量优化
│   │   ├─ 列式存储 + 智能索引 (ZoneMap/BloomFilter/Bitmap)
│   │   └─ 实时更新: 主键表 (Primary Key) 支持实时 Upsert
│   ├─► 数据导入
│   │   ├─ Stream Load (HTTP 同步)
│   │   ├─ Routine Load (Kafka 持续导入)
│   │   ├─ Spark/Flink 连接器
│   │   └─ INSERT INTO SELECT (内表/外表)
│   └─► 适用场景
│       ├─ 实时报表、用户画像、漏斗分析
│       ├─ 实时风控、A/B 测试效果分析
│       └─ 统一湖仓分析 (Lakehouse Analytics)
│
├─► ClickHouse
│   ├─► 架构特点
│   │   ├─ 列式存储 + 数据压缩 (LZ4/ZSTD)
│   │   ├─ 向量化执行引擎 (Vectorized Execution)
│   │   ├─ MergeTree 引擎家族
│   │   └─ 分布式表 + 本地表双层模型
│   ├─► 存储引擎
│   │   ├─ MergeTree: 主键排序、分区、分片
│   │   ├─ ReplacingMergeTree: 最终一致性去重
│   │   ├─ SummingMergeTree: 预聚合
│   │   └─ AggregatingMergeTree: 增量聚合状态
│   ├─► 查询特性
│   │   ├─ 近似算法: uniqCombined, quantilesTDigest
│   │   ├─ 物化视图 (Projection, 2021+)
│   │   └─ 稀疏主键索引 + 跳跃索引 (Data Skipping Indexes)
│   └─► 适用场景
│       ├─ 日志分析、时序数据、监控指标
│       ├─ 海量数据 OLAP (PB 级)
│       └─ 事件流分析、广告投放分析
│
└─► 核心技术共性
    ├─ 列式存储: 只读取需要的列，高压缩比
    ├─ 向量化执行: SIMD 指令批量处理，Cache Friendly
    ├─ 智能索引: 减少 IO，加速过滤
    └─ 物化视图: 预计算常用查询，空间换时间
```

---

## 二、核心概念的形式化定义

```text
定义 (MPP 查询执行):
  设查询 Q，数据分片集合 P = {p₁, p₂, ..., pₙ}，计算节点 N = {n₁, n₂, ..., nₘ}

  查询计划树 T = (Operators, Edges)
  分布式执行:
    1. 优化器生成物理计划，标记交换算子 (Exchange)
    2. 计划切分为片段 (Fragment)，每个片段可在节点并行执行
    3. 数据 shuffle: 按 join key / aggregation key 重分布
    4. 汇聚节点合并结果

  执行时间:
    T_exec = maxᵢ(T_fragmentᵢ) + T_shuffle + T_merge

定义 (向量化执行):
  传统火山模型: 每次处理 1 行 (tuple-at-a-time)
    CPU 开销: 虚函数调用 + 分支预测失败 + Cache Miss

  向量化模型: 每次处理 1 批 (batch-at-a-time, 通常 4096 行)
    对列数据 C = [c₁, c₂, ..., cₙ]，批量应用算子:
      result = SIMD_op(C, constant) 或 SIMD_op(C₁, C₂)

    性能增益来源:
      - 减少虚函数调用 (n/4096 倍)
      - SIMD 指令并行 (AVX2/AVX-512: 256/512 bit)
      - CPU Cache 局部性提升

定义 (物化视图形式化):
  设基表 B，查询模式 Q(B)，物化视图 MV:
    MV = Q(B) 的预计算结果

  查询重写规则:
    若 ∃MV, Q(B) 可转换为 Q'(MV)，则:
      执行 Q'(MV) 替代 Q(B)
      约束: Q'(MV) 的结果 ≡ Q(B) 的结果

  维护策略:
    - 同步刷新: 基表变更立即更新 MV (高一致，高开销)
    - 异步刷新: 定时/事件触发刷新 (最终一致，低开销)
    - 增量刷新: ΔMV = Q(ΔB) (仅计算变更部分)

定义 (列式存储的优势):
  设表有 N 列，查询访问 K 列，总行数 M:
    行存读取量: O(M × N × width_avg)
    列存读取量: O(M × K × width_avg), K << N 时增益显著

  压缩比:
    列存: 同类型数据连续存储，压缩率 η_col >> η_row
    常用压缩: Run-Length Encoding (RLE), Dictionary, Delta
```

---

## 三、多维矩阵对比

| 维度 | StarRocks | ClickHouse | Apache Druid | Snowflake |
|------|-----------|------------|--------------|-----------|
| **架构** | MPP + 存算分离 | MPP + 分布式 | 自定义 (Broker/Coord) | SaaS 纯存算分离 |
| **部署模式** | 开源/云原生 | 开源/云原生 | 开源 | 仅 SaaS |
| **实时更新** | **强 (主键 Upsert)** | 弱 (ReplacingMergeTree) | 追加为主 | 强 |
| **Join 性能** | **优秀 (Colocate/Broadcast)** | 一般 (推荐大宽表) | 弱 | 优秀 |
| **标准 SQL** | **高兼容 (MySQL 协议)** | 中等 (方言较重) | 中等 | 高兼容 |
| **数据湖查询** | **Iceberg/Hudi/Delta 外表** | 有限 (需集成) | 有限 | 外部表 |
| **物化视图** | 异步物化视图 + 查询重写 | Projection (有限) | 数据立方体 | 物化视图 |
| **向量化执行** | 是 (Short-Circuit) | **是 (极成熟)** | 部分 | 是 |
| **适用场景** | 实时数仓、湖仓分析 | 日志/时序/海量 OLAP | 实时聚合、监控 | 企业数仓 |
| **社区** | 中国主导，增长快 | 俄罗斯/Yandex，全球 | 美国，稳定 | 商业 |

| 技术 | 行式存储 | 列式存储 | 向量化执行 | 传统火山模型 |
|------|---------|---------|-----------|-------------|
| **OLTP** | 优秀 | 差 | 不适用 | 适用 |
| **OLAP** | 差 | 优秀 | 优秀 | 中 |
| **压缩比** | 低 | 高 | - | - |
| **单点查询** | 快 | 慢 (多列) | - | - |
| **聚合查询** | 慢 | 极快 | 极快 | 中 |
| **代表数据库** | MySQL, PostgreSQL | ClickHouse, StarRocks | StarRocks, DuckDB | Presto/Trino |

---

## 四、权威引用

> **Marcin Zukowski et al.** ("MonetDB/X100: Hyper-Pipelining Query Execution", CIDR 2005):
> "Vectorized execution achieves order-of-magnitude performance improvements over traditional tuple-at-a-time processing by amortizing interpretation overhead and leveraging SIMD instructions."

> **Alexey Milovidov** (Yandex, ClickHouse 创始人, 2016):
> "ClickHouse was developed for Yandex.Metrica, the second largest web analytics platform in the world. The key requirement was to run analytical queries on non-aggregated data in real time."

> **StarRocks Documentation** ("Query Optimization", 2023):
> "StarRocks' CBO (Cost-Based Optimizer) generates execution plans by evaluating the cost of various join orders, distribution strategies, and index selections, achieving sub-second query performance on petabyte-scale datasets."

> **Benoit Dageville et al.** (Snowflake, SIGMOD 2016):
> "The separation of storage and compute is the architectural foundation that enables elasticity, scalability, and pay-per-use economics in modern data warehouses."

---

## 五、工程实践与代码示例

```sql
-- StarRocks: 主键表 + 物化视图示例
-- 创建支持实时更新的主键表
CREATE TABLE user_events (
    event_id BIGINT,
    user_id BIGINT,
    event_type VARCHAR(64),
    event_time DATETIME,
    amount DECIMAL(18,2)
) PRIMARY KEY(event_id)
DISTRIBUTED BY HASH(event_id) BUCKETS 16
PROPERTIES ("replication_num" = "3");

-- 实时 Upsert (流式导入支持 exactly-once)
INSERT INTO user_events VALUES (1, 1001, 'purchase', '2024-01-15 10:00:00', 99.99);
INSERT INTO user_events VALUES (1, 1001, 'purchase', '2024-01-15 10:00:00', 89.99);  -- 自动覆盖

-- 创建异步物化视图加速聚合查询
CREATE MATERIALIZED VIEW mv_daily_stats
AS SELECT
    DATE(event_time) as dt,
    event_type,
    COUNT(*) as cnt,
    SUM(amount) as total_amount
FROM user_events
GROUP BY dt, event_type;

-- 查询自动路由到物化视图
SELECT dt, SUM(total_amount) FROM mv_daily_stats WHERE dt = '2024-01-15' GROUP BY dt;
```

```sql
-- ClickHouse: MergeTree 引擎 + 物化投影示例
CREATE TABLE events (
    event_id UInt64,
    user_id UInt64,
    event_type LowCardinality(String),
    event_time DateTime,
    amount Decimal(18,2)
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (user_id, event_time)
SETTINGS index_granularity = 8192;

-- 插入数据 (批量插入性能最优)
INSERT INTO events VALUES (1, 1001, 'click', '2024-01-15 10:00:00', 0.00),
                          (2, 1002, 'purchase', '2024-01-15 10:05:00', 99.99);

-- 使用 Projection (ClickHouse 21.6+) 预聚合
ALTER TABLE events ADD PROJECTION event_daily_agg
(
    SELECT
        toStartOfDay(event_time) as day,
        event_type,
        count(),
        sum(amount)
    GROUP BY day, event_type
);

-- 数据自动按 Projection 预计算，查询时透明加速
SELECT toStartOfDay(event_time) as day, sum(amount)
FROM events
WHERE day = '2024-01-15'
GROUP BY day;
```

---

## 六、批判性总结

StarRocks 与 ClickHouse 代表了实时数仓的两种工程哲学。**ClickHouse 是极致性能的化身**——它从 Yandex 的海量日志分析场景诞生，设计上优先考虑单查询的极限吞吐，其列式存储和向量化执行引擎是业界最成熟的实现。但 ClickHouse 的分布式 Join 能力长期薄弱，官方推荐通过"大宽表"模型规避 Join，这在星型/雪花型维度模型普及的企业数仓中造成了显著的建模约束。StarRocks 则选择了**更均衡的路线**——在保持优秀向量化执行性能的同时，通过 Colocate Join、Broadcast Join、Pipeline 执行引擎等技术大幅提升了分布式 Join 的能力，使其能够直接替代传统 MPP 数仓（如 Greenplum）而不改变建模范式。

两者的深层差异在于**更新语义**。ClickHouse 的 MergeTree 家族本质上是追加优先的日志结构，ReplacingMergeTree 的去重是后台异步合并的，查询时可能读到旧版本；StarRocks 的主键表则提供了真正的实时 Upsert 语义，对需要精确去重和实时修正的场景（如金融交易、广告计费）更为友好。物化视图是两者共同认可的"空间换时间"策略，但实现成熟度差异显著：StarRocks 的异步物化视图支持透明的查询重写，对用户几乎无感；ClickHouse 的 Projection 相对年轻，覆盖的查询模式有限。

2026 年的趋势表明，实时数仓正在与数据湖格式（Iceberg/Delta Lake）深度融合——StarRocks 的"湖仓分析"和 ClickHouse 的"数据湖集成"都在走同一条路：**用高性能 OLAP 引擎直接查询湖中的开放格式数据**，避免昂贵的 ETL 入仓过程。这不是 OLAP 数据库的终结，而是其角色的进化——从"数据仓库的查询层"进化为"数据湖的分析加速层"。
