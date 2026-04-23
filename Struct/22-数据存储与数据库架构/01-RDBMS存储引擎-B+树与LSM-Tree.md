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
