# 并发模型对比：OS 线程、Goroutine 与虚拟线程

> **来源映射**: View/01.md §1.1, View/05.md §3.1
> **国际权威参考**: "Communicating Sequential Processes" (Hoare, 1978), "The Problem with Threads" (Edward A. Lee, 2006), JEP 444 (Virtual Threads), "Actors: A Model of Concurrent Computation" (Agha, 1986)

---

## 一、知识体系思维导图

```text
并发模型谱系
│
├─► OS 线程 (1:1 模型)
│   ├─ 内核调度: 时间片轮转、优先级抢占
│   ├─ 资源开销: 栈 1-8MB，上下文切换 1-2μs
│   ├─ 同步原语: Mutex, Semaphore, Condition Variable
│   ├─ 编程模型: 共享内存 + 显式锁
│   └─ 代表: Java Thread, C++ std::thread, Python threading
│
├─► 用户态线程 / M:N 模型
│   ├─► Goroutine (Go)
│   │   ├─ Go运行时调度: GMP模型
│   │   ├─ 通信: Channel (CSP)
│   │   ├─ 栈: 2KB起，动态增长/收缩
│   │   └─ 阻塞: G挂起，M复用
│   │
│   ├─► 虚拟线程 (Java Project Loom, JDK 21+)
│   │   ├─ JVM运行时调度: M:N映射到OS线程
│   │   ├─ 阻塞: 虚拟线程挂起，载体线程复用
│   │   ├─ 兼容: 现有 Thread API 透明升级
│   │   └─ 同步: 传统锁 (synchronized) 自动优化
│   │
│   └─► 纤程 / Fiber (其他语言)
│       ├─ C++20 coroutines (无栈协程)
│       ├─ Rust async/await (状态机)
│       └─ Kotlin Coroutines (挂起函数)
│
├─► Actor 模型
│   ├─ 实体: Actor = 状态 + 行为 + 邮箱
│   ├─ 通信: 异步消息传递，无共享内存
│   ├─ 隔离: 每个Actor串行处理消息
│   └─ 代表: Erlang/OTP, Akka (Scala/Java), Orleans (.NET)
│
├─► 软件事务内存 (STM)
│   ├─ 思想: 数据库事务语义应用到内存
│   ├─ 操作: atomic { ... } 代码块
│   ├─ 冲突: 乐观并发，冲突时回滚重试
│   └─ 代表: Haskell STM, Clojure refs, Scala STM
│
└─► 异步/事件驱动
    ├─ 核心: 事件循环 + 非阻塞I/O
    ├─ 表达: callback / Promise / async-await
    └─ 代表: Node.js, Python asyncio, Rust Tokio
```

---

## 二、核心概念的形式化定义

### 2.1 并发模型的通信代数

```text
定义 (通信模型对比):

  共享内存模型 (Threads):
    State: 全局共享地址空间
    Operation: read(addr), write(addr, value)
    Synchronization: lock(m), unlock(m)
    风险: 数据竞争 (Data Race) = 未同步的并发读写

  CSP 模型 (Go Channel):
    Process: 独立顺序执行体
    Channel: 有向通信管道
    Operation: ch ! v (发送), ch ? v (接收)
    规则: 无共享内存，所有通信通过Channel
    性质: 确定性 (Deterministic) 对于给定输入，输出唯一

  Actor 模型:
    Actor: (State, Behavior, Mailbox)
    Operation: send(actor_ref, message)
    规则: Actor间仅通过异步消息通信
    性质: 位置透明 (Location Transparency)

  STM 模型:
    Transaction: atomic { read(x); write(y, f(x)); }
    语义: ACID 的简化版 (Atomicity, Consistency, Isolation)
    实现: 乐观并发控制 (OCC)，冲突时 abort + retry
```

### 2.2 虚拟线程调度形式化

```text
定义 (Java 虚拟线程):
  设虚拟线程集合 VT = {vt₁, vt₂, ..., vtₙ}
  设载体线程集合 CT = {ct₁, ct₂, ..., ctₘ}  (m ≈ CPU核心数)

  调度映射:
    schedule: VT → CT ∪ {READY_QUEUE}

  状态转移:
    RUNNING: vt 绑定到 ct，执行字节码

    RUNNING --(阻塞I/O/sleep/join)--> PARKED
      - 载体线程 ct 被释放
      - vt 状态保存到堆内存 (continuation)
      - scheduler 从 READY_QUEUE 选取下一个 vt 绑定到 ct

    PARKED --(I/O完成/超时/信号)--> READY
      - vt 加入 READY_QUEUE
      - 等待 scheduler 分配 ct

    RUNNING --(yield)--> READY
      - 自愿放弃载体线程

  关键不变式:
    - 虚拟线程从不直接绑定到OS线程 (仅在RUNNING时间接通过ct)
    - 阻塞操作不改变OS线程状态 (避免内核上下文切换)
    - synchronized 块内阻塞 → 载体线程不释放 (pinning风险)
```

### 2.3 M:N 调度复杂度分析

```text
定义 (调度复杂度):

  OS 线程调度 (1:1):
    创建: O(1) 系统调用
    切换: O(1) 内核上下文 (寄存器+页表+TLB刷新)
    阻塞: O(1) 线程状态变更 (内核态)
    扩展性: 受限，线程数 ~ 数千 (内存限制)

  Goroutine 调度 (M:N):
    创建: O(1) 用户态，栈分配
    切换: O(1) 用户态 (寄存器保存，无内核切换)
    阻塞: O(1) G状态变更 + M可能释放P
    扩展性: ~ 百万级 (2KB栈起)

  虚拟线程调度 (M:N):
    创建: O(1) 用户态 (轻量对象分配)
    切换: O(1) 用户态 (Continuation保存/恢复)
    阻塞: O(1) 解除载体绑定
    扩展性: ~ 百万级 (与Goroutine同级)

  async/await 调度 (N:1 或 M:N):
    创建: O(1) 状态机对象分配
    切换: O(1) 事件循环调度
    阻塞: O(1) Future注册到Reactor
    扩展性: ~ 百万级

  核心差异:
    Goroutine/虚拟线程: 运行时自动抢占调度
    async/await: 协作式调度，依赖await显式让出
```

---

## 三、多维矩阵对比

| 维度 | OS 线程 | Goroutine | Java 虚拟线程 | Actor (Erlang) | async/await |
|------|---------|-----------|--------------|----------------|-------------|
| **调度器** | 内核 | Go运行时 | JVM运行时 | BEAM VM | 事件循环 |
| **映射比例** | 1:1 | **M:N** | M:N | M:N | N:1 或 M:N |
| **栈管理** | 固定1-8MB | **2KB动态增长** | 动态增长/收缩 | 1KB动态增长 | 无栈/状态机 |
| **阻塞处理** | 内核阻塞 | **G挂起+M复用** | VT挂起+CT复用 | 进程挂起+调度器复用 | 非阻塞I/O |
| **通信方式** | 共享内存+锁 | **Channel (CSP)** | 共享内存+锁/Channel | **异步消息** | Channel/Future |
| **容错模型** | 脆弱 (一崩全崩) | 脆弱 | 脆弱 | **监督树+隔离** | 脆弱 |
| **百万并发** | 不可行 | **可行** | 可行 | **可行** | 可行 |
| **调试难度** | 高 (数据竞争) | 中 (死锁) | 低 (兼容JVM工具) | 低 (顺序语义) | **高 (回调地狱)** |
| **生态成熟度** | **极高** | 高 | 中 (JDK21+) | 中 | 高 |

---

## 四、权威引用

> **Tony Hoare** (CSP 发明者, Turing奖 1980):
> "Communicating Sequential Processes offer a fundamental paradigm for concurrency that avoids the pitfalls of shared memory."

> **Edward A. Lee** ("The Problem with Threads", 2006):
> "Threads, as a model of computation, are wildly nondeterministic, and the job of the programmer becomes one of pruning that nondeterminism."

> **Joe Armstrong** (Erlang 发明者):
> "Processes (Actors) are the only true form of object-oriented programming." —— 隔离+消息传递 = OO的本质。

> **Ron Pressler** (Java Project Loom 负责人):
> "Virtual threads are not faster than platform threads; they're more scalable. The goal is not speed, but simplicity — write synchronous code, get asynchronous scalability."

> **Rob Pike** (Go 语言设计者):
> "Concurrency is not parallelism. Concurrency is about dealing with lots of things at once. Parallelism is about doing lots of things at once."

---

## 五、工程实践与代码示例

### 5.1 Java 虚拟线程 (JDK 21+)

```java
// 创建虚拟线程执行器
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    IntStream.range(0, 100_000).forEach(i -> {
        executor.submit(() -> {
            Thread.sleep(Duration.ofSeconds(1));  // 阻塞但 carrier 线程不阻塞！
            return i;
        });
    });
} // executor.close() 等待所有任务完成

// 对比: 平台线程执行 100,000 个任务 → OOM
//       虚拟线程执行 100,000 个任务 → 成功，几MB内存

// ⚠️  pinning 风险: synchronized + 阻塞I/O
synchronized(lock) {
    // 虚拟线程在此处阻塞 → 载体线程被"钉住"
    // 解决方案: 使用 ReentrantLock 替代 synchronized
    fileInputStream.read();
}
```

### 5.2 Actor 模型 (Akka 风格伪代码)

```scala
// Actor 定义
class OrderActor extends Actor {
  def receive = {
    case CreateOrder(items) =>
      // 串行处理，无需锁
      val order = process(items)
      sender() ! OrderCreated(order.id)

    case CancelOrder(id) =>
      // 同一Actor内无并发，天然线程安全
      cancel(id)
      sender() ! OrderCancelled(id)
  }
}

// Actor 创建与通信
val orderActor = system.actorOf(Props[OrderActor], "orders")
orderActor ! CreateOrder(List("item1", "item2"))
// 异步发送，立即返回，无阻塞
```

### 5.3 并发模型选型决策

```text
场景: 构建一个高并发 Web 网关，需要处理 100K+ 并发连接

方案对比:
  1. OS线程 (Java传统):
     - 限制: ~10K线程即内存/上下文切换瓶颈
     - 需要: 线程池 + 复杂背压管理

  2. Goroutine (Go):
     - 100K Goroutine 轻松支撑
     - Channel 组织请求流
     - 风险: 单个Goroutine死循环饿死其他G (协作式缺陷)

  3. 虚拟线程 (Java Loom):
     - 100K 虚拟线程，兼容现有代码
     - 传统阻塞代码 (JDBC, FileIO) 自动获得扩展性
     - 风险: synchronized 导致 pinning，需逐步替换为 ReentrantLock

  4. async/await (Rust/Node.js):
     - 极高扩展性
     - 风险: 传染性问题 (所有调用链必须 async)
     - Node.js: 单事件循环，CPU密集型任务阻塞所有I/O

  5. Actor (Erlang/Elixir):
     - 每个连接一个 Actor
     - 监督树自动重启失败组件
     - 限制: 函数式编程范式，生态较小

推荐:
  - 已有Java生态 → 虚拟线程 (渐进升级)
  - 新系统/I/O密集型 → Goroutine 或虚拟线程
  - 极高可靠性要求 (电信/金融) → Actor (Erlang/Elixir)
  - 性能极致 + 安全 → Rust async/await
```

---

## 六、批判性总结

并发模型的历史是一部**抽象层级不断提升**的进化史：从裸机中断到OS线程，从共享内存锁到消息传递，从回调地狱到协程语法糖。每一种模型都是对前一种的**回应与超越**，但也带来了新的认知负担和陷阱。

OS线程（1:1模型）的**根本缺陷**在于资源开销：每个线程消耗数MB内存和数千个时钟周期的上下文切换，使得"为每个连接创建一个线程"的朴素架构在C10K问题面前崩溃。Java虚拟线程和Go Goroutine用M:N调度解决了资源问题，但保留了线程模型的**心智模型**——开发者仍按顺序思维编写代码，运行时负责高效调度。这是"通过抽象隐藏复杂度"的胜利，但这种隐藏的代价是**调试地狱**：当百万个Goroutine或虚拟线程中出现死锁或资源泄漏时，现有的调试工具（pprof、JFR）往往力不从心。

CSP（Go Channel）与Actor模型的根本差异在于**通信语义**：CSP的Channel是同步的（无缓冲时握手），强调"发送方与接收方同时就绪"；Actor的邮箱是异步的，强调"发送即忘记"。CSP更适合**流水线**和**协调**场景，Actor更适合**分布式**和**容错**场景。然而，2026年的工程现实是：**没有任何主流语言实现纯粹的CSP或Actor**——Go开发者大量使用sync.Mutex和atomic，Erlang开发者常常绕过消息传递直接使用ETS表（共享内存）。这揭示了并发模型的一个基本真理：理论纯洁性在性能压力面前总是妥协。

虚拟线程（Project Loom）代表了Java社区对**向后兼容性**的极致追求：它不要求开发者学习新的API或重写代码，而是让现有的`Thread`和`synchronized`在底层自动获得M:N扩展性。但这种兼容性是有毒的——`synchronized`块内的阻塞会"钉住"载体线程（pinning），抵消虚拟线程的全部优势。这意味着Java生态需要一场**缓慢的锁替换运动**（从synchronized到ReentrantLock），而这种大规模代码迁移在经济上几乎不可能在短期内完成。

最终，并发模型的选择不是技术问题，而是**组织问题**：一个熟悉Java Spring的团队使用虚拟线程，其生产力远超被迫学习Rust async的团队；一个拥有Erlang OTP经验的团队构建的电信系统，其可靠性是任何Go微服务难以企及的。并发模型的最佳实践不是追求最先进的抽象，而是选择团队能够**真正掌握和驾驭**的那一种——因为最危险的并发bug不是数据竞争，而是开发者对所用模型的**误解**。
