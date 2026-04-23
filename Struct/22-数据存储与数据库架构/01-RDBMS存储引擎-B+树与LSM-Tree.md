# RDBMS 存储引擎：B+ 树与 LSM-Tree

> **来源映射**: View/02.md §2.1, Struct/22-数据存储与数据库架构/00-总览-数据库系统的形式化分层.md
> **国际权威参考**: "The Log-Structured Merge-Tree (LSM-Tree)" (O'Neil et al., Acta Informatica, 1996); "The B-tree, the Ubiquitous B-tree" (Comer, ACM Computing Surveys, 1979); CMU 15-445 Database Systems (Andy Pavlo)

---

## 一、知识体系思维导图

```text
RDBMS 存储引擎架构
│
├─► 页式存储管理 (Page-Oriented Storage)
│   ├─ 页 (Page/Block): 固定大小 (通常 4KB/8KB/16KB)
│   ├─ Buffer Pool: 内存中的页缓存
│   │   ├─ 页表 (Page Table): 页号 → 内存帧映射
│   │   ├─ 替换策略: LRU, CLOCK, 2Q
│   │   └─ 脏页管理: Write-Back 策略
│   └─ 磁盘布局: 堆文件 (Heap File) + 页目录
│
├─► B+ 树索引 (B+ Tree Index)
│   ├─ 结构特性
│   │   ├─ 所有数据存储在叶子节点
│   │   ├─ 叶子节点通过指针链表连接 (范围扫描友好)
│   │   └─ 内部节点仅存储导航键 ( fanout 最大化 )
│   ├─ 操作复杂度
│   │   ├─ 点查: O(log_b N) 磁盘 I/O
│   │   ├─ 范围查: O(log_b N + k) (k 为结果数)
│   │   └─ 插入/删除: O(log_b N) (可能触发节点分裂/合并)
│   └─ 代表: InnoDB (MySQL), PostgreSQL, SQL Server, Oracle
│
└─► LSM-Tree (Log-Structured Merge Tree)
    ├─ 核心思想: 写优化，将随机写转为顺序写
    ├─ 结构层次
    │   ├─ MemTable: 内存中的有序结构 (Skip List / B+树)
    │   ├─ WAL: 预写日志 (Write-Ahead Log)
    │   ├─ Immutable MemTable: 只读，等待刷盘
    │   └─ SSTable (Sorted String Table): 磁盘上的不可变文件
    ├─ 合并策略
    │   ├─ Leveling: 层级合并 (LevelDB, RocksDB)
    │   └─ Tiering: 层内多文件，满后合并 (Cassandra)
    └─ 放大分析
        ├─ 写放大 (Write Amplification)
        ├─ 读放大 (Read Amplification)
        └─ 空间放大 (Space Amplification)
```

---

## 二、核心概念的形式化定义

### 2.1 B+ 树的形式化

```text
定义 (B+ 树):
  设阶数为 d 的 B+ 树满足:

  内部节点:
    - 包含 k 个键和 k+1 个指针，其中 ⌈d/2⌉ - 1 ≤ k ≤ d - 1
    - 键 keyᵢ 是子树 i 和子树 i+1 的分隔键

  叶子节点:
    - 包含 k 个键值对，其中 ⌈d/2⌉ - 1 ≤ k ≤ d - 1
    - 通过 next 指针连接形成有序链表
    - 所有实际数据记录存储于此

  树高:
    h ≤ log_{⌈d/2⌉}(N) + 1
    对于 d=200, N=1亿: h ≤ 4-5 层
```

### 2.2 LSM-Tree 的形式化

```text
定义 (LSM-Tree L):
  L = {L₀, L₁, L₂, ..., Lₖ} 其中 Lᵢ 为第 i 层的 SSTable 集合

  不变式:
    ∀Lᵢ: 层内 SSTables 的 Key 范围互不重叠 (Leveling)
    |Lᵢ| 的大小限制呈指数增长: size(Lᵢ₊₁) = T × size(Lᵢ) (T 为大小倍数)

  写入路径:
    write(k, v) → WAL.append(k,v) → MemTable.insert(k,v)
    当 MemTable 满: flush to L₀ as SSTable

  读取路径:
    read(k): 依次查询 MemTable → Immutable → L₀ → L₁ → ... → Lₖ
    使用 Bloom Filter 过滤不含 k 的 SSTable

  合并操作 (Compaction):
    当 |Lᵢ| 超过阈值: select SSTables from Lᵢ, merge into Lᵢ₊₁
```

### 2.3 放大分析

```text
写放大 (WA):
  定义: WA = 写入磁盘的总数据量 / 用户写入的数据量
  B+ 树: WA ≈ 1 (In-Place Update)，但随机写导致高 I/O
  LSM-Tree: WA = f(层数, 合并策略) = O(T/(T-1) × 层数)

读放大 (RA):
  定义: RA = 读取的页或文件数 / 返回的记录数
  B+ 树: RA ≈ h (树高) 对于点查
  LSM-Tree: RA = O(层数) (最坏情况需检查每层一个文件)

空间放大 (SA):
  定义: SA = 数据库总大小 / 实际数据大小
  B+ 树: SA ≈ 1 (紧凑，有碎片化)
  LSM-Tree: SA > 1 (旧版本数据在合并前保留)
```

---

## 三、多维矩阵对比

| 维度 | B+ 树 (InnoDB) | LSM-Tree (RocksDB) | 哈希索引 | 跳表 (Skip List) |
|------|---------------|-------------------|---------|-----------------|
| **写性能** | 中 (随机写) | **优** (顺序写) | 优 | 优 (内存) |
| **读性能** | **优** (点查+范围) | 中 (需多层查找) | **极优** (点查) | 中 |
| **范围查询** | **优** | 中 | 无 | 中 |
| **写放大** | 低 | **高** | 低 | 低 |
| **读放大** | 低 | **高** | 低 | 低 |
| **空间放大** | 低 | **中-高** | 低 | 低 |
| **并发控制** | 成熟 (B-link) | MVCC + 快照 | 简单 | 简单 |
| **崩溃恢复** | WAL + Checkpoint | WAL + SSTable | 无/日志 | 无 |
| **适用负载** | 读写均衡 | **写密集型** | 纯内存点查 | 内存索引 |

---

## 四、权威引用

> **Patrick O'Neil et al.** ("The Log-Structured Merge-Tree (LSM-Tree)", Acta Informatica, 1996):
> "The LSM-Tree uses an algorithm that defers and batches index changes, cascading the changes from a memory-based component through one or more disk components in an efficient manner reminiscent of merge sorts."

> **Douglas Comer** ("The Ubiquitous B-Tree", ACM Computing Surveys, 1979):
> "The B-tree is the standard organization for indexes in a database system. It provides logarithmic time access for both random and sequential processing."

> **Mark Callaghan et al.** (Facebook, "MySQL vs. RocksDB", 2014):
> "RocksDB's LSM tree provides better write throughput and compression than InnoDB's B+ tree, at the cost of higher read amplification and more complex tuning."

---

## 五、工程实践与代码示例

### RocksDB 基础配置与操作

```cpp
#include <rocksdb/db.h>

using namespace rocksdb;

// 配置 Options
Options options;
options.create_if_missing = true;
options.compression = kLZ4Compression;
options.write_buffer_size = 64 * 1024 * 1024;  // 64MB MemTable
options.target_file_size_base = 64 * 1024 * 1024;
options.max_bytes_for_level_base = 512 * 1024 * 1024;

DB* db;
Status s = DB::Open(options, "/path/to/db", &db);

// 写入 (异步 WAL)
WriteOptions write_options;
write_options.sync = false;
s = db->Put(write_options, "key1", "value1");

// 读取
std::string value;
s = db->Get(ReadOptions(), "key1", &value);

// 范围扫描
auto* iter = db->NewIterator(ReadOptions());
for (iter->Seek("prefix"); iter->Valid() && iter->key().starts_with("prefix"); iter->Next()) {
    Process(iter->key(), iter->value());
}
```

---

## 六、批判性总结

B+ 树与 LSM-Tree 的对比本质上是"读优化"与"写优化"两种设计哲学的碰撞。B+ 树通过 In-Place Update 保持了数据的局部性和紧凑性，使其在混合负载（OLTP）中表现卓越，但随机写导致的磁盘寻道成本使其在 SSD 时代仍面临挑战。LSM-Tree 将随机写转化为顺序写，配合 SSD 的顺序写入优势，在写密集型场景（如日志、时序数据）中实现了数量级的性能提升。然而，LSM-Tree 并非没有代价：**写放大问题在层级数增加时呈超线性增长**，对于写密集型工作负载，SSD 的寿命会被显著压缩；读放大则要求 Bloom Filter 等辅助结构的存在，增加了内存占用和实现复杂度。现代数据库（如 MyRocks、TiKV）选择 LSM-Tree 作为底层存储，证明了写优化在云计算时代的优势，但这也要求 DBA 和开发者理解 compaction 策略、tuning 参数——LSM-Tree 的"开箱即用"体验远不如 B+ 树。未来存储引擎的趋势可能是**混合架构**：热数据用 B+ 树或内存结构，冷数据用 LSM-Tree 压缩归档，但这又引入了数据迁移和一致性的新挑战。


---

## 七、概念属性关系网络

### 7.1 核心概念依赖/包含/对立关系表

| 概念A | 关系类型 | 概念B | 关系说明 |
|-------|---------|-------|---------|
| Page | → (组织) | Heap File | 页是堆文件的存储组织单元 |
| Buffer Pool | → (缓存) | Page | Buffer Pool缓存磁盘页 |
| B+ Tree | → (索引) | Data Record | B+树索引指向数据记录 |
| B+ Tree | ⊥ (对比) | LSM-Tree | 读优化与写优化两种索引哲学对立 |
| LSM-Tree | ⊃ (包含) | MemTable | LSM树包含内存表组件 |
| LSM-Tree | ⊃ (包含) | SSTable | LSM树包含磁盘排序表组件 |
| MemTable | → (刷盘) | Immutable MemTable | 内存表满后变为不可变内存表 |
| Immutable MemTable | → (刷盘) | SSTable | 不可变内存表刷盘为SSTable |
| Compaction | → (维护) | SSTable | 合并操作维护SSTable层级 |
| Write Amplification | ⊥ (权衡) | Read Amplification | 写放大与读放大的反向权衡 |

### 7.2 ASCII拓扑图

```text
RDBMS存储引擎概念拓扑
│
├─► 页式存储管理
│   ├─► Page (4KB / 8KB / 16KB)
│   │   ├─► 页头 (page_id, checksum, free_space)
│   │   ├─► 记录目录 (slot_directory)
│   │   └─► 数据区域 (tuples / index_entries)
│   │
│   ├─► Buffer Pool
│   │   ├─► Page Table: page_id → frame_address
│   │   ├─► 替换策略
│   │   │   ├─► LRU ──► 最近最少使用
│   │   │   ├─► CLOCK ──► 近似LRU，低开销
│   │   │   └─► 2Q ──► 区分热页与冷页
│   │   └─► 脏页管理: Write-Back策略
│   │
│   └─► 堆文件组织
│       ├─► 页链表 / 页目录
│       └─► 空闲空间管理
│
├─► B+树索引 (读优化)
│   ├─► 内部节点: 导航键 + 子节点指针
│   │   └─► fanout最大化，减少树高
│   ├─► 叶子节点: 键值对 + next指针
│   │   └─► 有序链表，范围扫描友好
│   ├─► 操作复杂度
│   │   ├─► 点查: O(log_b N)
│   │   ├─► 范围查: O(log_b N + k)
│   │   └─► 插入/删除: O(log_b N) + 分裂/合并
│   └─► In-Place Update
│       └─► 随机写，数据局部性优
│
├─► LSM-Tree索引 (写优化)
│   ├─► 写入路径
│   │   ├─► write(k,v) → WAL.append → MemTable.insert
│   │   └─► MemTable满 → flush to L₀ as SSTable
│   │
│   ├─► 读取路径
│   │   └─► read(k): MemTable → Immutable → L₀ → L₁ → ... → Lₖ
│   │       └─► Bloom Filter过滤不含k的SSTable
│   │
│   ├─► 合并策略 (Compaction)
│   │   ├─► Leveling: 层级合并 (LevelDB, RocksDB)
│   │   │   └─► 层内Key范围不重叠
│   │   └─► Tiering: 层内多文件，满后合并 (Cassandra)
│   │       └─► 写放大较低，读放大较高
│   │
│   └─► 放大分析
│       ├─► Write Amplification = 写入磁盘总量 / 用户写入量
│       ├─► Read Amplification = 读取页数 / 返回记录数
│       └─► Space Amplification = 数据库总大小 / 实际数据大小
│
└─► 权衡矩阵
    ├─► B+树: 读优、写中、空间紧凑
    └─► LSM-Tree: 写优、读中、空间松散
```

### 7.3 形式化映射

```text
概念映射:

f₁: Tuple → Page        via  heap_manager.insert(tuple) → page_id + slot_id
f₂: Page → BufferPool   via  buffer_pool.fix(page_id) → frame_pointer
f₃: Key → Record        via  bplus_tree.search(key) → record_pointer
f₄: Key → Value         via  lsm_tree.read(key) → memtable ∪ sstables
f₅: Write → MemTable    via  skip_list.insert(key, value) (有序内存结构)
f₆: MemTable → SSTable  via  flush(sorted_kv_pairs) → immutable_file
f₇: SSTables → SSTable' via  compaction(level_n, level_n+1) → merged_files
f₈: Query → Cost        via  cost_model(IO_cost × weight_io + CPU_cost × weight_cpu)
```

---

## 八、形式化推理链

### 8.1 公理体系

**公理 1 (B+树阶数约束公理)** — Douglas Comer, 1979
> 阶数为d的B+树节点包含k个键，满足 ⌈d/2⌉ - 1 ≤ k ≤ d - 1。
> 树高上界: h ≤ log_{⌈d/2⌉}(N) + 1

**公理 2 (LSM-Tree层级大小公理)** — O'Neil et al., 1996
> LSM-Tree第i层的大小限制呈指数增长: |Lᵢ₊₁| = T × |Lᵢ|，T为大小倍数。
> 层内SSTable的Key范围互不重叠（Leveling策略）。

**公理 3 (WAL先写公理)** — Jim Gray, 1981
> 任何数据修改必须先写WAL并fsync，再修改内存结构。
> write(data) ⟹ wal.fsync precedes memtable.update

### 8.2 引理

**引理 1 (B+树范围查询的最优性)**
> B+树的叶子节点链表使范围查询的I/O复杂度最优。
> 范围查I/O = O(log_b N)（定位起点）+ O(k/B)（顺序扫描），B为页大小。

**引理 2 (LSM-Tree写放大的上界)**
> Leveling策略下，写放大 WA ≤ T/(T-1) × 层数。
> Proof: 每层数据被合并到下一层T次，总写放大为几何级数求和。

### 8.3 定理

**定理 1 (B+树与LSM-Tree的读写权衡)** — 基于放大分析
> 对于N条记录，页面大小B，B+树阶数d:
> B+树点查I/O = O(log_d N)，LSM-Tree最坏点查I/O = O(层数 × 每层级文件数)
> B+树写入I/O = O(log_d N)（随机写），LSM-Tree写入I/O = O(1)（顺序写，摊销）
>
> 故: B+树读优写劣，LSM-Tree写优读劣。

**定理 2 (RocksDB的压缩空间-写放大权衡)**
> 压缩算法降低Space Amplification但增加CPU开销和写放大。
> compression_level ↑ ⟹ space_amplification ↓ ∧ cpu_overhead ↑ ∧ write_amplification ↑

### 8.4 推论

**推论 1 (SSD时代的LSM-Tree优势)**
> SSD的顺序写入带宽 >> 随机写入带宽，放大了LSM-Tree的写优化优势。
> 但SSD的擦写寿命有限，LSM-Tree的高写放大压缩SSD寿命。

**推论 2 (混合负载的索引选择)**
> 读写比 > 10: 倾向B+树；写读比 > 10: 倾向LSM-Tree。
> 混合负载可能需要混合索引架构（如MyRocks的热数据B+树+冷数据LSM）。

---

## 九、ASCII推理判定树 / 决策树

### 9.1 存储引擎选择决策树

```text
存储引擎选择
│
├─► 读写比例如何？
│   ├─ 读 >> 写（如BI报表、OLAP）──► B+树（InnoDB / PostgreSQL）
│   │                                   └─ 范围查询友好，数据局部性优
│   │
│   ├─ 写 >> 读（如日志、时序、IoT）──► LSM-Tree（RocksDB / Cassandra）
│   │                                   └─ 顺序写优化，吞吐高
│   │
│   └─ 读写均衡（通用OLTP）──► 是否需要复杂范围查询？
│               ├─ 是 ──► B+树（InnoDB）
│               │           └─ 成熟稳定，范围查询性能优
│               └─ 否（ mostly点查 ）──► 可评估LSM-Tree
│                           └─ MyRocks / TiKV 等混合方案
```

### 9.2 Buffer Pool调优决策树

```text
Buffer Pool调优
│
├─► 工作集是否大于内存？
│   ├─ 否（全内存工作集）──► 增大Buffer Pool至覆盖工作集
│   │                           └─ 减少磁盘I/O，提升命中率
│   │
│   └─ 是（工作集 >> 内存）──► 替换策略选择
│               ├─► 访问模式是否有明显热点？
│               │   ├─ 是 ──► LRU / 2Q
│               │   │           └─ 热页驻留，冷页淘汰
│               │   └─ 否（均匀访问）──► CLOCK
│               │                       └─ 低开销近似LRU
│               │
│               └─► 脏页刷盘策略
│                   ├─ 写密集 ──► 频繁Checkpoint，减少崩溃恢复时间
│                   └─ 读密集 ──► 延迟刷盘，提升写入合并率
```

---

## 十、国际权威课程对齐

### 10.1 MIT 6.830: Database Systems

| 课程内容 | 对应 Lecture | 对应本文件内容 | 映射深度 |
|---------|-------------|---------------|---------|
| Storage & Indexing | Lec 1-3 | 页式管理、B+树、LSM-Tree | 核心映射 |
| Buffer Management | Lec 2 | Buffer Pool替换策略 | 核心映射 |
| Query Optimization | Lec 4-6 | 索引选择的代价模型 | 间接映射 |

### 10.2 Stanford CS 145 / CS 245: Database Systems

| 课程内容 | 对应模块 | 对应本文件内容 |
|---------|---------|---------------|
| Storage Architecture | Lecture 3-5 | 页式存储与堆文件组织 |
| Index Structures | Lecture 6-8 | B+树与哈希索引的设计 |
| Advanced Indexing | Lecture 9-10 | LSM-Tree与日志结构存储 |

### 10.3 CMU 15-445: Database Systems

| 课程内容 | 对应 Lecture | 对应本文件内容 |
|---------|-------------|---------------|
| Database Storage I/II | Lecture 3, 5 | 页式管理、Buffer Pool、磁盘布局 |
| Memory Management | Lecture 4 | Buffer Pool替换策略与并发控制 |
| Hash Tables | Lecture 7 | 哈希索引与扩展性哈希 |
| Indexes & Filters | Lecture 8-10 | B+树结构、Bloom Filter、并发索引 |

### 10.4 Berkeley CS 186: Database Systems

| 课程内容 | 对应模块 | 对应本文件内容 |
|---------|---------|---------------|
| Disks, Buffers, Files | Lecture 3-5 | 存储层与Buffer Pool |
| B+ Trees & Indexing | Lecture 4-7 | B+树结构与范围查询 |
| Cost Models | Lecture 4 | I/O代价模型与索引选择 |

### 10.5 核心参考文献

1. **Douglas Comer** (1979). "The Ubiquitous B-Tree." *ACM Computing Surveys*, 11(2), 121-137. —— B树家族的经典综述，定义了B+树作为数据库标准索引结构的理论基础。

2. **Patrick O'Neil et al.** (1996). "The Log-Structured Merge-Tree (LSM-Tree)." *Acta Informatica*, 33(4), 351-385. —— LSM-Tree的原始论文，提出了写优化索引的核心思想。

3. **Mark Callaghan et al.** (2014). "MySQL vs. RocksDB: A Performance Comparison." *Facebook Engineering*. —— 工业级B+树与LSM-Tree的实证对比研究。

4. **Goetz Graefe** (2011). "Modern B-Tree Techniques." *Foundations and Trends in Databases*, 3(4), 203-402. —— B树技术的现代综述，涵盖了B-link树、批量加载、并发控制等高级主题。

---

## 十一、批判性总结

B+树与LSM-Tree的对比本质上是"读优化"与"写优化"两种设计哲学的碰撞，这种碰撞的历史背景是存储介质特性的演变。B+树通过In-Place Update保持了数据的局部性和紧凑性，使其在混合负载（OLTP）中表现卓越，但随机写导致的磁盘寻道成本即使在SSD时代仍构成性能挑战——SSD的随机写入虽然比机械硬盘快数个数量级，但其内部垃圾回收和擦写放大机制仍使顺序写入具有显著优势。LSM-Tree将随机写转化为顺序写，配合SSD的顺序写入特性，在写密集型场景（日志、时序数据）中实现了数量级的性能提升。然而，LSM-Tree并非没有代价：写放大问题在层级数增加时呈超线性增长，对于写密集型工作负载，SSD的寿命被显著压缩；读放大则要求Bloom Filter等辅助结构的存在，增加了内存占用和实现复杂度。现代数据库（如MyRocks、TiKV）选择LSM-Tree作为底层存储，证明了写优化在云计算时代的优势，但这也要求DBA和开发者理解compaction策略、tuning参数——LSM-Tree的"开箱即用"体验远不如B+树。一个被忽视的趋势是混合架构的兴起：热数据用B+树或内存结构保证读性能，冷数据用LSM-Tree压缩归档，但这又引入了数据迁移和一致性的新挑战。最终，存储引擎的选择不应仅基于理论性能指标，而应基于对工作负载访问模式的精确分析——在大多数生产环境中，80%的读取集中在20%的数据上，这种偏斜分布使得缓存策略（Buffer Pool设计）比底层索引结构对性能的影响更大。
