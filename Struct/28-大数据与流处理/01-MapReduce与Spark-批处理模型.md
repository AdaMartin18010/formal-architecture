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
