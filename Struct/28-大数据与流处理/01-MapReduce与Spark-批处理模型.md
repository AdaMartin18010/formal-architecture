# MapReduce 与 Spark：批处理模型

> **来源映射**: View/00.md §3.1, 模块28总览
> **国际权威参考**: "MapReduce: Simplified Data Processing on Large Clusters" (Dean & Ghemawat, OSDI 2004), "Resilient Distributed Datasets" (Zaharia et al., NSDI 2012), "Spark: The Definitive Guide" (Chambers & Zaharia, 2018)

---

## 一、知识体系思维导图

```text
MapReduce 与 Spark 批处理模型
│
├─► MapReduce 编程模型
│   ├─► 核心阶段
│   │   ├─ Map:     (K₁, V₁) → list(K₂, V₂)
│   │   ├─ Shuffle: 按键 K₂ 分组排序
│   │   └─ Reduce:  (K₂, list(V₂)) → list(K₃, V₃)
│   ├─► 容错机制
│   │   ├─ 中间结果写入 HDFS
│   │   ├─ Map 失败: 重新调度到副本节点
│   │   └─ Reduce 失败: 重新读取 Map 输出
│   ├─► 局限性
│   │   ├─ 中间结果落盘，IO 开销大
│   │   ├─ 不适合迭代计算 (ML 训练)
│   │   └─ 编程模型受限 (仅 Map + Reduce)
│   └─► 代表实现
│       ├─ Hadoop MapReduce
│       └─ Apache Hive (SQL → MapReduce)
│
├─► Apache Spark
│   ├─► 核心抽象: RDD (Resilient Distributed Dataset)
│   │   ├─ 不可变分区集合
│   │   ├─ 血统 (Lineage): 转换依赖图
│   │   ├─ 惰性求值 (Lazy Evaluation)
│   │   └─ 容错: 血统重算替代检查点
│   ├─► 编程接口演进
│   │   ├─ RDD API (低级，细粒度控制)
│   │   ├─ DataFrame API (结构化，Catalyst 优化)
│   │   └─ Dataset API (类型安全 + 结构化，Scala/Java)
│   ├─► 执行优化
│   │   ├─ Catalyst 优化器: 逻辑计划 → 物理计划
│   │   ├─ Tungsten 引擎: 堆外内存、代码生成
│   │   └─ DAG 调度: 阶段划分、任务流水线
│   └─► 部署模式
│       ├─ Standalone、YARN、Mesos、Kubernetes
│       └─ 交互式: spark-shell、PySpark、Jupyter
│
└─► 批处理特征
    ├─ 输入: 有界数据集 (Bounded Dataset)
    ├─ 延迟: 分钟到小时
    ├─ 吞吐: TB-PB 级
    ├─ 容错: 任务级重算
    └─ 适用: ETL、报表、离线分析、机器学习训练
```

---

## 二、核心概念的形式化定义

```text
定义 (MapReduce 形式化):
  设输入数据集 D = {(k₁, v₁), (k₂, v₂), ..., (kₙ, vₙ)}

  Map 函数:
    M: (K₁, V₁) → list(K₂, V₂)
    输出: {(k'₁, v'₁), (k'₂, v'₂), ...}

  Shuffle 阶段:
    groupByKey: list(K₂, V₂) → {K₂ → list(V₂)}
    排序: 每个 Reduce 输入按键有序

  Reduce 函数:
    R: (K₂, list(V₂)) → list(K₃, V₃)

  完整计算:
    Result = ⋃ᵢ R(kᵢ, [v | (kᵢ, v) ∈ M(D)])

定义 (RDD 抽象):
  RDD 是一个五元组 (Partitions, Dependencies, Compute, Partitioner, PreferredLocations):
    Partitions:     数据分区的集合 {p₁, p₂, ..., pₙ}
    Dependencies:   父 RDD 依赖关系 (窄依赖/宽依赖)
    Compute:        分区计算函数 pᵢ → Iterator[T]
    Partitioner:    键值分区函数 (Hash/Range)
    PreferredLocations: 数据本地性偏好

  转换操作 (Transformation, 惰性):
    map, filter, flatMap, groupByKey, reduceByKey, join, ...

  行动操作 (Action, 触发执行):
    collect, reduce, count, saveAsTextFile, ...

  血统图 (Lineage Graph):
    G = (RDD_nodes, Transforms_edges)
    容错: 若分区 p 丢失，从血统图根节点重算 p

定义 (DataFrame Catalyst 优化):
  逻辑计划 (Logical Plan) → 优化器 (Catalyst) → 物理计划 (Physical Plan)

  优化规则:
    - 谓词下推 (Predicate Pushdown)
    - 列式裁剪 (Column Pruning)
    - 常量折叠 (Constant Folding)
    - 连接重排序 (Join Reordering)
```

---

## 三、多维矩阵对比

| 维度 | Hadoop MapReduce | Spark RDD | Spark DataFrame | Spark SQL |
|------|------------------|-----------|-----------------|-----------|
| **抽象级别** | 低 (Map+Reduce) | 中 (分布式集合) | 高 (结构化表) | 高 (SQL) |
| **内存使用** | 磁盘为主 | 内存 + 磁盘 | 内存优化 | 内存优化 |
| **迭代性能** | 差 (多次读写磁盘) | 优 (内存缓存) | 优 | 优 |
| **类型安全** | 弱 (Java Object) | 强 (泛型) | 弱 (运行时推断) | 弱 |
| **优化器** | 无 | 无 | Catalyst + Tungsten | Catalyst + Tungsten |
| **容错方式** | 任务重试 | 血统重算 | 血统重算 | 血统重算 |
| **生态集成** | Hive、Pig | MLlib、GraphX | Spark ML、Structured Streaming | Hive Metastore |

| 特性 | 窄依赖 (Narrow) | 宽依赖 (Wide/Shuffle) |
|------|-----------------|----------------------|
| **父分区** | 一个子分区依赖一个父分区 | 一个子分区依赖多个父分区 |
| **操作** | map, filter, union | groupByKey, reduceByKey, join |
| **Shuffle** | 无 | 有 |
| **容错成本** | 低 (仅重算丢失分区) | 高 (可能触发全链路重算) |
| **流水线** | 可流水线执行 | 阶段边界 |

---

## 四、权威引用

> **Jeffrey Dean & Sanjay Ghemawat** (Google, OSDI 2004):
> "MapReduce is a programming model and an associated implementation for processing and generating large data sets. Users specify a map function that processes a key/value pair to generate a set of intermediate key/value pairs, and a reduce function that merges all intermediate values associated with the same intermediate key."

> **Matei Zaharia et al.** (UC Berkeley, NSDI 2012):
> "Resilient Distributed Datasets (RDDs) are a distributed memory abstraction that lets programmers perform in-memory computations on large clusters in a fault-tolerant manner."

> **Matei Zaharia** ("Spark: The Definitive Guide", 2018):
> "The DataFrame API is the cornerstone of structured processing in Spark. It combines the performance optimizations of relational systems with the expressiveness of functional programming."

> **Armbrust et al.** ("Spark SQL: Relational Data Processing in Spark", SIGMOD 2015):
> "Catalyst is the first production-quality query optimizer that supports both relational and procedural processing within a single system."

---

## 五、工程实践与代码示例

```python
# PySpark: WordCount 与 DataFrame 优化示例
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, explode, split

spark = SparkSession.builder \
    .appName("WordCountOptimized") \
    .config("spark.sql.adaptive.enabled", "true") \
    .getOrCreate()

# DataFrame API (推荐): Catalyst 自动优化
df = spark.read.text("hdfs://input/")
word_counts = df.select(
    explode(split(col("value"), "\\s+")).alias("word")
).groupBy("word").agg(count("*").alias("count")) \
 .orderBy(col("count").desc())

word_counts.write.mode("overwrite").parquet("hdfs://output/")

# RDD API (低级控制，无自动优化)
text_rdd = spark.sparkContext.textFile("hdfs://input/")
word_counts_rdd = text_rdd.flatMap(lambda line: line.split()) \
    .map(lambda word: (word, 1)) \
    .reduceByKey(lambda a, b: a + b) \
    .sortBy(lambda x: x[1], ascending=False)
```

---

## 六、批判性总结

MapReduce 的历史意义在于它首次证明了**大规模数据并行处理可以通过简单的函数式抽象在普通硬件集群上实现**，但其设计哲学——将中间结果持久化到分布式文件系统以确保容错——在迭代计算场景下成为了致命瓶颈。Spark 的革命性不在于替代了 MapReduce，而在于它挑战了"容错必须依赖磁盘复制"的假设：通过 RDD 血统图实现**细粒度、低开销的内存容错**，将机器学习等迭代工作负载的性能提升了 10-100 倍。

然而，Spark 的演进轨迹揭示了大数据系统的一个普遍规律：**抽象层级的提升伴随着控制力的丧失**。RDD API 给予开发者完整的分区控制和自定义序列化能力，但需要深入理解分布式计算的底层机制；DataFrame API 通过 Catalyst 优化器自动选择最佳执行计划，但在复杂场景下可能做出次优决策（如不必要的 Shuffle）。实践中，绝大多数 ETL 和报表场景应优先使用 DataFrame/SQL API，仅在性能调优或实现自定义算子时回落至 RDD。Spark 3.x 引入的 Adaptive Query Execution (AQE) 进一步缩小了自动优化与手动调优之间的差距，但"理解执行计划 (explain)"仍然是大数据工程师的核心技能。批处理的本质是**在数据完整性与计算延迟之间做权衡**——MapReduce 选择了极端的完整性，Spark 在两者之间找到了更优平衡点。


---

## 七、概念属性关系网络

### 7.1 核心概念依赖/包含/对立关系表

| 概念A | 关系 | 概念B | 关系说明 |
|-------|------|-------|---------|
| MapReduce | 包含 → | Map + Shuffle + Reduce | 三阶段 pipeline 是不可拆分的原子结构 |
| Spark RDD | 对立于 → | MapReduce | 内存迭代 vs 磁盘落盘的范式对立 |
| 窄依赖 | 对立于 → | 宽依赖 | 无 Shuffle vs 有 Shuffle 的执行差异 |
| Catalyst | 优化 → | DataFrame | Catalyst 优化器将逻辑计划转为物理计划 |
| Tungsten | 加速 → | Spark 执行 | Tungsten 的代码生成和堆外内存提升性能 |
| 血统 (Lineage) | 替代 → | Checkpoint | RDD 用血统重算替代传统检查点容错 |
| DataFrame API | 抽象于 → | RDD API | DataFrame 是 RDD 的结构化高层抽象 |

### 7.2 ASCII 拓扑图

```text
                        ┌─────────────────┐
                        │   大数据批处理    │
                        │  (Batch Processing)│
                        └────────┬────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
       ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
       │  MapReduce   │   │  Spark RDD   │   │ Spark DataFrame│
       │              │   │              │   │              │
       │ Map→Shuffle→ │   │ 内存迭代     │   │ Catalyst     │
       │ Reduce       │   │ 血统容错     │   │ 自动优化     │
       └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
              │                  │                  │
              ▼                  ▼                  ▼
       ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
       │ 磁盘持久化    │   │ 窄依赖/宽依赖 │   │ Tungsten     │
       │ 任务级重试   │   │ 阶段划分     │   │ 向量化执行   │
       └──────────────┘   └──────────────┘   └──────────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
             ┌──────────┐ ┌──────────┐ ┌──────────┐
             │ DAG 调度  │ │ 内存管理  │ │ 代码生成  │
             │          │ │          │ │          │
             └──────────┘ └──────────┘ └──────────┘
```

### 7.3 形式化映射

设输入数据集 D = {(k₁, v₁), ..., (kₙ, vₙ)}，
MapReduce 计算：Result = ⋃ᵢ Reduce(kᵢ, [v | (kᵢ, v) ∈ Map(D)])

RDD 五元组：RDD = (Partitions, Dependencies, Compute, Partitioner, PreferredLocations)

- 窄依赖：父分区 → 子分区，1:1 或 n:1，无 Shuffle
- 宽依赖：父分区 → 子分区，n:m，触发 Shuffle

Catalyst 优化器：Logical Plan → Optimized Logical Plan → Physical Plan → Executed Plan
优化规则集合 R = {谓词下推, 列式裁剪, 常量折叠, 连接重排序}

---

## 八、形式化推理链

### 8.1 公理体系

**公理 A1 (数据局部性公理)** [Dean & Ghemawat, 2004]
> 设数据分片大小为 B，网络传输成本为 C_network，本地磁盘读取成本为 C_disk，
> 则 C_network ≫ C_disk（通常差 1-2 个数量级）。
> 因此，计算应调度到数据所在节点，即"移动计算而非移动数据"。

**公理 A2 (内存-磁盘延迟公理)** [Zaharia et al., 2012]
> 设内存访问延迟为 t_mem，磁盘访问延迟为 t_disk，
> 则 t_disk / t_mem ≈ 10⁵。
> 因此，迭代计算中内存缓存的边际收益远大于磁盘持久化。

### 8.2 引理

**引理 L1 (Shuffle 成本引理)**
> 设 Map 输出数据量为 M，Reduce 输入数据量为 R，网络带宽为 B，
> 则 Shuffle 时间 t_shuffle = (M + R) / B + t_sort。
> 若 M ≫ R（如 word count），t_shuffle 主导总执行时间。
> 因此，减少 Shuffle 是 Spark 优化的首要目标。

**引理 L2 (血统容错成本引理)** [Zaharia et al., 2012]
> 设 RDD 血统链长度为 L，每个分区重算时间为 t_recompute，
> 则血统容错成本 C_lineage = L · t_recompute。
> 当 L > threshold 或 t_recompute 较大时，Checkpoint 成本 C_checkpoint < C_lineage。

### 8.3 定理

**定理 T1 (MapReduce 完备性定理)** [Dean & Ghemawat, 2004]
> 对于任意可分解为"映射-分组-归约"模式的计算，
> MapReduce 可在大规模集群上实现线性扩展。
> 扩展效率 η = T₁ / (n · Tₙ)，其中 T₁ 为单机时间，Tₙ 为 n 节点时间。
> 当数据本地性达到 95% 以上时，η → 1。

**定理 T2 (Spark 迭代加速定理)** [Zaharia et al., 2012]
> 设迭代算法（如机器学习）需要 k 轮迭代，
> MapReduce 每轮迭代需读写磁盘，总时间 T_mr = k · (t_compute + t_io)。
> Spark 将数据缓存于内存，总时间 T_spark = t_io + k · t_compute。
> 当 k ≫ 1 且 t_io > t_compute 时，T_spark / T_mr → 1/k。

### 8.4 推论

**推论 C1 (DataFrame 优化必然性推论)** [Armbrust et al., 2015]
> 设 DataFrame 查询经过 Catalyst 优化后的执行时间为 T_opt，
> 手写 RDD 实现时间为 T_manual，
> 则 T_opt ≤ T_manual 的概率 P ≥ 0.9（对于标准查询模式）。
> 仅在非标准模式（如自定义聚合逻辑）下，手动 RDD 可能优于自动优化。

**推论 C2 (列式存储批处理优势推论)**
> 设表有 N 列，查询访问 K 列，行存读取量为 R_row = M · N · w，
> 列存读取量为 R_col = M · K · w。
> 当 K/N < 0.3 时，R_col / R_row < 0.3，且列存压缩率 η_col > η_row。
> 因此，OLAP 场景下列式存储的 I/O 优势是结构性的。

---

## 九、ASCII 推理判定树 / 决策树

### 9.1 决策树一：MapReduce vs Spark 选型

```text
                    ┌─────────────────┐
                    │  批处理引擎选型   │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                              ▼
    ┌─────────────────┐            ┌─────────────────┐
    │  工作负载类型    │            │  工作负载类型    │
    │  迭代计算?       │            │  单次 ETL?      │
    │  (ML/图计算)     │            │  (报表/日志处理) │
    └────────┬────────┘            └────────┬────────┘
         Yes │    No                    Yes │    No
        ┌────┴────┐                      ┌───┴───┐
        ▼         ▼                      ▼       ▼
   ┌────────┐ ┌────────┐          ┌────────┐ ┌────────┐
   │ Spark  │ │ 继续   │          │ 两者   │ │ 继续   │
   │ 必选   │ │ 评估   │          │ 均可   │ │ 评估   │
   └────────┘ └────────┘          └────────┘ └────────┘
        │        │                      │       │
        │   实时性要求?                 │   生态兼容性?
        │   < 秒级?                     │   需 Hive 集成?
        │   │Yes  │No                  │   │Yes  │No
        │  ┌──┴───┐                   │  ┌──┴───┐
        │  ▼      ▼                   │  ▼      ▼
        │┌────────┐┌────────┐         │┌────────┐┌────────┐
        ││ Spark  ││ Spark  │         ││ Hive   ││ Spark  │
        ││ Streaming││ Structured│      ││ on     ││ Native │
        ││ (流式) ││ (批处理)│         ││ MR     ││ (推荐) │
        │└────────┘└────────┘         │└────────┘└────────┘
        │                             │
        └─────────────────────────────┴─────────┘
```

### 9.2 决策树二：RDD vs DataFrame API 选择

```text
                    ┌─────────────────┐
                    │  Spark API 选型  │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                              ▼
    ┌─────────────────┐            ┌─────────────────┐
    │  查询模式是否    │            │  查询模式标准?   │
    │  标准 SQL/聚合?  │            │  无自定义逻辑?   │
    └────────┬────────┘            └────────┬────────┘
         Yes │    No                    Yes │    No
        ┌────┴────┐                      ┌───┴───┐
        ▼         ▼                      ▼       ▼
   ┌────────┐ ┌────────┐          ┌────────┐ ┌────────┐
   │ DataFrame│ │ 继续   │          │ DataFrame│ │ 深入   │
   │ /SQL   │ │ 评估   │          │ 首选   │ │ 评估   │
   └────────┘ └────────┘          └────────┘ └────────┘
        │        │                      │       │
        │   需细粒度控制?               │   性能调优?
        │   (分区/序列化)               │   瓶颈在 Shuffle?
        │   │Yes  │No                  │   │Yes  │No
        │  ┌──┴───┐                   │  ┌──┴───┐
        │  ▼      ▼                   │  ▼      ▼
        │┌────────┐┌────────┐         │┌────────┐┌────────┐
        ││ RDD    ││ Dataset│         ││ RDD    ││ DataFrame│
        ││ (低级) ││ (类型  │         ││ 手动   ││ AQE自动 │
        ││        ││ 安全)  │         ││ 优化   ││ 优化   │
        │└────────┘└────────┘         │└────────┘└────────┘
        │                             │
        └─────────────────────────────┴─────────┘
```

---

## 十、国际权威课程对齐

### 10.1 MIT 6.824: Distributed Systems

| Lecture | 主题 | 本文件映射 | Lab |
|---------|------|-----------|-----|
| Lecture 15 | Big Data: Spark | RDD 抽象、血统容错、内存计算 | Lab 4: Spark |
| Lecture 3 | GFS | 分布式存储与数据局部性 | Lab 1: MapReduce |
| Lecture 1 | Introduction | 大数据分布式处理概览 | Reading |

### 10.2 Stanford CS 145: Databases

| Week | Lecture | 本文件映射 | Assignment |
|------|---------|-----------|------------|
| Week 5 | Scale: Indexing and IO | 数据局部性与 I/O 优化 | Project 1 |
| Week 8 | Query Optimization | Catalyst 优化器原理 | HW 2 |
| Week 10 | Systems Design | 批处理系统设计权衡 | Project 2 |

### 10.3 CMU 15-719: Advanced Cloud Computing

| Lecture | 主题 | 本文件映射 | Project |
|---------|------|-----------|---------|
| Week 4 | Parallel Programming Frameworks | MapReduce/Spark 编程模型 | Lab 2 |
| Week 6 | Scheduling Cloud Clusters | DAG 调度与数据局部性 | Reading |
| Week 12 | Big Data Analytics | Spark SQL 与 DataFrame | Final Project |

### 10.4 Berkeley CS 186: Database Systems

| Lecture | 主题 | 本文件映射 | Assignment |
|---------|------|-----------|------------|
| Lecture 6 | Sorting, Building Indices | Shuffle 与排序机制 | Project 2 |
| Lecture 8 | Query Optimization Part 2 | 连接重排序与物理计划 | HW |
| Lecture 14 | Distributed Databases | 分布式数据并行处理 | Final |

### 10.5 核心参考文献

1. **Dean, J., & Ghemawat, S.** (2004). "MapReduce: Simplified Data Processing on Large Clusters." *OSDI'04*, 137–150. —— Google 的奠基性论文，首次证明大规模数据并行处理可通过简单函数式抽象在普通硬件集群上实现。

2. **Zaharia, M., Chowdhury, M., Das, T., Dave, A., Ma, J., McCauley, M., ... & Stoica, I.** (2012). "Resilient Distributed Datasets: A Fault-Tolerant Abstraction for In-Memory Cluster Computing." *NSDI'12*, 15–28. —— Spark 核心论文，提出 RDD 内存抽象和血统图容错机制。

3. **Armbrust, M., Xin, R. S., Lian, C., Huai, Y., Liu, D., Bradley, J. K., ... & Zaharia, M.** (2015). "Spark SQL: Relational Data Processing in Spark." *SIGMOD'15*, 1383–1394. —— Catalyst 优化器的首次公开发表，支持关系型与过程式处理的统一优化。

4. **Zaharia, M., Xin, R. S., Wendell, P., Das, T., Armbrust, M., Dave, A., ... & Ghodsi, A.** (2016). "Apache Spark: A Unified Engine for Big Data Processing." *Communications of the ACM*, 59(11), 56–65. —— Spark 2.x 的统一引擎愿景，将批处理、流处理、SQL 和机器学习整合到单一执行引擎。

---

## 十一、批判性总结（深度增强版）

MapReduce 的历史意义在于它首次证明了**大规模数据并行处理可以通过简单的函数式抽象在普通硬件集群上实现**。2004 年 Google 的论文发表时，业界普遍认为大规模数据处理需要专用硬件（如超级计算机）和复杂的并行编程模型（如 MPI）。Dean 和 Ghemawat 的洞见在于：大多数数据分析任务可以自然地表达为"映射-分组-归约"的三阶段模式，而底层分布式细节（任务调度、容错、数据局部性）可以由运行时系统自动处理。这一抽象将分布式编程的门槛从"掌握 MPI 和集群管理"降低到"会写两个函数"。但 MapReduce 的设计哲学——将中间结果持久化到分布式文件系统以确保容错——在迭代计算场景下成为了致命瓶颈。机器学习算法的参数更新需要反复读取同一数据集，而 MapReduce 每轮迭代都要重新从磁盘加载数据，造成 I/O 开销占总时间的 90% 以上。

Spark 的革命性不在于替代了 MapReduce，而在于它挑战了"容错必须依赖磁盘复制"的假设。通过 RDD 血统图（Lineage Graph）实现细粒度、低开销的内存容错，Spark 将机器学习等迭代工作负载的性能提升了 10-100 倍。但这一优化的代价是**内存成本的增加**——RDD 缓存需要集群内存容量大于工作集大小，这在内存价格高昂的早期限制了 Spark 的适用范围。随着云计算中内存成本的指数下降和 Tungsten 引擎的堆外内存优化，内存计算已成为大数据处理的默认假设。

Spark 的演进轨迹揭示了一个普遍规律：**抽象层级的提升伴随着控制力的丧失**。RDD API 给予开发者完整的分区控制和自定义序列化能力，但需要深入理解分布式计算的底层机制；DataFrame API 通过 Catalyst 优化器自动选择最佳执行计划，但在复杂场景下可能做出次优决策（如选择广播连接而非 Shuffle 连接，导致内存溢出）。Spark 3.x 引入的 Adaptive Query Execution (AQE) 进一步缩小了自动优化与手动调优之间的差距，但"理解执行计划（explain）"仍然是大数据工程师的核心技能。实践中，绝大多数 ETL 和报表场景应优先使用 DataFrame/SQL API，仅在性能调优或实现自定义算子时回落至 RDD。批处理的本质是在**数据完整性与计算延迟之间做权衡**——MapReduce 选择了极端的完整性（所有中间结果落盘），Spark 在两者之间找到了更优平衡点，而流处理引擎则进一步将延迟压缩到亚秒级。
