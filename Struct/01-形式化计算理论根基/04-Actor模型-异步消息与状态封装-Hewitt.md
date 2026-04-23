# Actor模型：异步消息与状态封装

> **定位**：Actor模型是并发计算的"面向对象"——每个Actor是一个独立的计算实体，通过异步消息传递通信。它是Erlang、Akka、 Orleans等系统的理论基础。
>
> **核心命题**：共享状态是并发Bug的根源；Actor模型通过"不共享任何东西"（shared-nothing）从根本上消除了数据竞争。
>
> **来源映射**：Hewitt et al.(1973) → Agha(1986) → Erlang/OTP → 分布式系统设计

---

## 一、思维导图：Actor模型核心

```text
Actor模型（Actor Model）
│
├─【核心原语】
│   ├─ create：创建新Actor
│   ├─ send：向Actor发送异步消息
│   └─ receive：处理收到的消息
│
├─【Actor状态】
│   ├─ 私有状态（不共享）
│   ├─ 行为（消息处理函数）
│   └─ 邮箱（消息队列）
│
├─【关键性质】
│   ├─ 无共享状态 → 无数据竞争
│   ├─ 位置透明（Location Transparency）
│   ├─ 容错（监督树）
│   └─ 分布式天然支持
│
└─【代表系统】
    ├─ Erlang/Elixir
    ├─ Akka（Scala/Java）
    ├─ Orleans（.NET）
    └─ Ray（Python/ML）
```

---

## 二、Actor模型的形式化定义

> **权威来源**：Carl Hewitt, Peter Bishop, Richard Steiger, "A Universal Modular Actor Formalism for Artificial Intelligence", *IJCAI*, 1973

```
Actor定义为三元组：A = (State, Behavior, MailBox)

  State = 私有状态（不可被其他Actor直接访问）
  Behavior = 消息 → (新State, [新Actor], [消息发送])
  MailBox = 消息的FIFO队列

操作语义：
  1. 创建（Create）：
     Actor A执行create(Behavior')
     → 系统创建新Actor B，初始状态由Behavior'决定
     → A收到B的地址（ActorRef）

  2. 发送（Send）：
     Actor A执行send(B, msg)
     → msg被放入B的MailBox尾部
     → 异步、非阻塞、无保证送达时间

  3. 接收（Receive）：
     Actor A从其MailBox头部取出msg
     → 应用Behavior(msg, currentState)
     → 产生新State'、可能创建新Actor、可能发送新消息

关键保证：
  - 串行处理：每个Actor一次只处理一条消息
  - 无共享：状态只能通过消息传递
  - 无数据竞争：因为无共享状态
```

---

## 三、Actor vs 其他并发模型

| 维度 | **Actor** | **共享内存+锁** | **CSP** | **STM** |
|------|----------|----------------|--------|--------|
| **通信** | 异步消息 | 共享变量 | 同步通道 | 共享变量+事务 |
| **状态** | 私有 | 共享 | 私有 | 共享 |
| **数据竞争** | 不可能 | 可能 | 不可能 | 运行时检测 |
| **容错** | 监督树（内置） | 手动处理 | 手动处理 | 手动处理 |
| **分布式** | 天然支持 | 困难 | 可能（Go） | 困难 |
| **调试** | 消息追踪 | 困难（死锁、竞态） | 死锁可能 | 重试复杂 |
| **代表** | Erlang, Akka | Java, C++ | Go, Occam | Haskell, Clojure |

---

## 四、监督树与容错

```
Erlang/OTP的监督树：

  Supervisor
    ├── Worker A（one_for_one）
    │     └── 崩溃 → 仅重启A
    ├── Worker B（one_for_all）
    │     └── 崩溃 → 重启B及其兄弟
    └── Supervisor（rest_for_one）
          ├── Worker C
          └── Worker D
                └── 崩溃 → 重启D及在其后启动的

故障隔离原则：
  - "Let it crash"：不防御式编程，崩溃后快速重启
  - 进程（Actor）是廉价的：创建/销毁开销极低
  - 错误不传播：监督者控制故障范围

工业验证：
  - Ericsson AXD301：1M+行Erlang，99.9999999%可用性
  - WhatsApp：2M+连接/服务器，Erlang实现
```

---

## 五、概念定义与属性关系

| 概念 | 定义 | 属性 | 示例 | 反例 |
|------|------|------|------|------|
| **Actor** | 封装状态和行为的并发计算实体 | 私有状态、异步消息、邮箱队列 | Erlang进程 | 共享内存线程 |
| **ActorRef** | Actor的不可变地址引用 | 位置透明、可序列化、可远程 | PID in Erlang | 直接对象引用 |
| **监督树** | 层级化的Actor故障恢复结构 | 自动重启、故障隔离、策略可配 | OTP Supervisor | 手动异常处理 |
| **Let it crash** | 不防御已知异常，崩溃后快速重启 | 简单、可靠、需监督 | Erlang哲学 | Java checked exceptions |
| **位置透明** | Actor地址不暴露本地/远程差异 | 分布式透明、可迁移 | Akka Remote | IP地址硬编码 |

---

## 六、交叉引用

- → [01-总览](./00-总览-可计算性与计算模型谱系.md)
- → [01/02-λ演算](02-λ演算-函数抽象与组合-Church.md)
- → [01/03-进程代数](03-进程代数家族-CSP-CCS-π演算.md)
- ↓ [05/03-EDA](../05-架构模式与部署单元光谱/03-事件驱动架构-解耦与一致性的设计哲学.md)

---

## 七、参考文献

| 作者 | 标题 | 出处 | 年份 |
|------|------|------|------|
| Hewitt, Bishop, Steiger | "A Universal Modular Actor Formalism..." | *IJCAI* | 1973 |
| Gul Agha | *Actors: A Model of Concurrent Computation* | MIT Press | 1986 |
| Joe Armstrong | *Programming Erlang* (2nd ed.) | Pragmatic Bookshelf | 2013 |
| Roland Kuhn et al. | *Reactive Design Patterns* | Manning | 2017 |

## 八、权威引用

> **Carl Hewitt** (1973): "An actor is a computational entity that, in response to a message it receives, can concurrently send messages to other actors, create new actors, and designate the behavior to be used for the next message it receives."

> **Gul Agha** (1986): "The actor model provides a flexible framework for understanding and implementing open distributed systems."

## 九、批判性总结

Actor模型通过共享状态禁令从根本上消除了数据竞争，这一优雅设计使其成为高可用分布式系统的首选范式（Erlang、Akka）。然而，其隐含假设——消息传递是可靠的且最终有序的——在真实网络中频繁失效：消息丢失、重复、乱序和延迟波动是常态而非异常。失效条件包括：邮箱无界增长导致内存溢出（缺乏反压机制）、消息丢失使状态机永久阻塞（等待永远不会到达的响应）、以及跨Actor事务的缺失迫使开发者自行实现Saga模式（引入新的复杂性）。与CSP的同步握手相比，Actor的异步模型更接近物理网络但更难推理；未来趋势是Akka Typed和类似系统将静态类型检查引入Actor接口，在保持位置透明的同时，于编译期捕获部分消息协议错误。

## 推理判定树

```text
判定问题: 何时选择Actor模型作为并发/分布式系统的基础范式？
├─ 系统是否需要极高容错（如电信、金融核心、5个9以上可用性）？
│  ├─ 是 → Actor + 监督树（Erlang/OTP风格）→ "Let it crash"哲学
│  └─ 否 → 继续判定
├─ 状态是否可完全私有化，无共享内存需求？
│  ├─ 是 → Actor天然适合 → 无数据竞争
│  └─ 否 → 考虑共享内存+锁、STM或CSP
├─ 是否需要分布式透明（同一套代码本地/远程运行无需修改）？
│  ├─ 是 → Actor（Akka Remote/Cluster, Erlang分布式）→ 位置透明
│  └─ 否 → 继续判定
├─ 通信模式以异步消息为主，可容忍消息延迟/乱序？
│  ├─ 是 → Actor异步邮箱模型
│  └─ 否 → 若需同步保证 → 考虑CSP或请求-响应模式封装
├─ 是否需要跨Actor事务/强一致性？
│  ├─ 是 → Actor无内置事务 → 需自行实现Saga模式或考虑其他范式
│  └─ 否 → Actor适合
└─ 进程创建开销是否敏感（需百万级轻量进程）？
   ├─ 是 → Actor进程极轻量（Erlang < 1KB/进程）→ 理想选择
   └─ 否 → 其他范式也可接受
```

---

*文件创建日期：2026-04-23*
*状态：已完成*

---

## 概念属性关系网络

| 概念 | 依赖概念 | 包含概念 | 对立概念 | 映射概念 |
|------|---------|---------|---------|---------|
| Actor | 并发实体、封装、消息传递 | 私有状态、行为、邮箱（MailBox）、ActorRef | 共享内存线程、进程、对象 | Erlang进程、Akka Actor、Orleans Grain、Ray Task |
| 异步消息（Async Message） | 非阻塞发送、FIFO队列、最终交付 | send原语、邮箱缓冲、消息模式匹配 | 同步RPC、阻塞调用、rendezvous | Kafka消息、MQTT发布订阅、事件驱动架构（模块05-EDA） |
| 监督树（Supervision Tree） | 容错、故障隔离、let-it-crash | one_for_one、one_for_all、rest_for_one、simple_one_for_one | 防御式编程、try-catch泛滥、手动恢复 | Kubernetes Pod重启策略、 systemd服务重启、断路器模式 |
| 位置透明（Location Transparency） | 命名解析、序列化、网络透明 | 本地Actor/远程Actor无差异、动态迁移、分布式GC | 位置敏感、IP硬编码、本地调用优化 | 服务网格透明代理、DNS负载均衡、微服务服务发现 |
| Let-it-crash | 故障快速检测、快速重启、状态恢复 | 崩溃报告、监督者重启、状态初始化 | 防御式编程、异常吞咽、优雅降级 | 混沌工程（模块08）、熔断机制、健康检查 |
| 无界邮箱（Unbounded Mailbox） | 消息队列、内存消耗、背压缺失 | 图灵完备性、活性不可判定、消息累积 | 有界邮箱、背压机制、流控 | Reactive Streams背压、Akka Stream、缓冲区管理 |

## 形式化推理链

**公理/前提**: 设Actor为三元组 $A = (s, b, m)$，其中 $s \in S$ 为私有状态，$b: S \times M \to S \times \mathcal{P}(M) \times \mathcal{P}(A)$ 为行为函数（接收消息 $m \in M$ 后产生新状态、待发送消息集、新创建Actor集），$m \in M^*$ 为邮箱中的消息序列（Hewitt, 1973; Agha, 1986）。定义配置（configuration）为有限Actor集合 $C = \{A_1, A_2, \dots, A_n\}$。

**引理1**（Actor图灵完备性）: Actor模型是图灵完备的。对任意图灵机 $TM$，可构造等价的Actor系统 $A_{TM}$ 模拟其转移函数。
*证明*: （概要）用Actor的状态编码图灵机磁带内容，行为函数编码转移函数 $\delta$。无界邮箱允许模拟无限磁带（消息队列作为磁带的右侧扩展）。∎

**引理2**（活性不可判定性）: 对无界邮箱的Actor系统，判定"消息 $m$ 是否最终被处理"（活性）是半可判定而非可判定的。
*证明*: 由引理1，Actor模型图灵完备。将停机问题归约到Actor活性：构造Actor $A$ 在收到 $m$ 后模拟给定图灵机 $TM$，$TM$ 停机当且仅当 $A$ 最终处理下一条消息。故活性判定至少与停机问题同等困难。∎

**定理**（Actor数据竞争自由定理）: 在纯Actor模型中（无共享状态、消息不可变），不存在数据竞争（data race）。形式化地，对任意两个Actor $A_i, A_j$（$i \neq j$），其状态转换序列 $\{s_i^{(t)}\}$ 和 $\{s_j^{(t)}\}$ 满足：$s_i^{(t+1)}$ 仅依赖于 $s_i^{(t)}$ 和 $A_i$ 邮箱中的消息，与 $s_j^{(t)}$ 无关。
*证明*: 由Actor语义，状态 $s$ 是私有的，仅行为函数 $b$ 可访问。行为函数每次处理一条消息，且消息传递是Actor之间唯一的交互方式。不存在两个Actor同时读写同一内存位置的语义构造。∎

**推论**: Erlang/Elixir的"无数据竞争"保证是语言语义层面的定理，而非运行时碰巧未触发竞态；但这一保证的前提是消息深度不可变（deep immutable），若违反（如传递可变ETS表引用），则定理失效。

## 思维表征

### 推理判定树：Actor模型适用性与设计决策

```
开始：需要为并发/分布式系统选择并发模型
│
├─ 核心需求是否是容错与高可用？
│   ├─ 是（电信、金融核心、实时交易）
│   │   ├─ 故障隔离粒度要求？
│   │   │   ├─ 进程级隔离 → Actor模型：监督树自动重启崩溃Actor
│   │   │   └─ 机器级隔离 → Actor + 分布式监督：Erlang节点间监控
│   │   └─ 状态恢复策略？
│   │       ├─ 状态可重建 → Let-it-crash + 从持久化日志恢复
│   │       └─ 状态不可丢失 → 状态快照 + Event Sourcing（模块04）
│   └─ 否（一般Web后端、批处理）
│       └─ 共享内存+锁或CSP可能更简单高效
│
├─ 通信模式是否以异步事件流为主？
│   ├─ 是（IoT遥测、日志聚合、实时推送）
│   │   ├─ 消息量是否巨大且突发？
│   │   │   ├─ 是 → 需背压机制（Reactive Streams）防止邮箱溢出
│   │   │   └─ 否 → 纯Actor邮箱足够
│   │   └─ 消息顺序是否必须严格保证？
│   │       ├─ 是 → 单Actor串行处理天然保证每Actor内FIFO
│   │       └─ 否 → 可引入并行消费者（但牺牲顺序）
│   └─ 否（以请求-响应为主）
│       └─ Actor仍可用，但需异步RPC封装（Ask模式）
│
├─ 是否需要跨语言/跨平台互操作？
│   ├─ 是 → Actor模型的位置透明可映射到gRPC/HTTP2
│   │         └─ 注意：序列化成本与Schema演化需额外设计
│   └─ 否 → 同构技术栈（Erlang/Elixir、Akka）可获得最优语义保证
│
├─ 可分析性 vs 表达力权衡
│   ├─ 需静态验证死锁/活性？ → 限制为有限状态子集或使用会话类型
│   ├─ 需动态弹性？ → 接受无界状态，依赖运行时监控与混沌工程
│   └─ 混合策略：关键路径用CSP验证，边缘节点用Actor弹性
│
└─ 邮箱管理策略
    ├─ 无界邮箱风险：内存溢出、GC压力、级联延迟
    ├─ 有界邮箱 + 背压：流控但可能降低吞吐
    └─ 优先级邮箱：关键消息优先，但引入 starvation 风险
```

### 多维关联树：Actor模型与全模块的分布式映射

```
【04-Actor模型-异步消息与状态封装-Hewitt】
│
├─→ 01-形式化总览
│   └─ Actor ↔ 可计算性：图灵完备导致活性不可判定，与CSP有限状态形成对比
│
├─→ 02-分布式系统不可能性
│   ├─ Actor异步 ↔ CAP：异步消息假设与Partition的物理现实一致，
│   │   但消息丢失使Actor需在可用性与一致性间权衡
│   └─ Actor容错 ↔ FLP：Let-it-crash通过接受崩溃（Fail-stop）绕过FLP
│
├─→ 03-分布式共识算法完整谱系
│   ├─ Actor ↔ Raft：Raft节点可建模为Actor，但Raft的同步假设（超时）
│   │   与Actor的纯异步有张力
│   └─ Actor ↔ PBFT：拜占庭Actor（恶意消息）需BFT协议防御
│
├─→ 04-数据一致性代数结构
│   └─ Actor邮箱 ↔ CRDT：Actor的状态更新若满足交换律/结合律，
│       可无冲突复制；邮箱本身是有序的，与集合语义CRDT不同
│
├─→ 05-架构模式与部署单元光谱
│   ├─ Actor ↔ 微服务：Actor的"不共享任何东西"映射到微服务的独立部署
│   ├─ Actor ↔ EDA：事件驱动架构是Actor模型的大规模工程变体
│   └─ Actor ↔ Serverless：Actor的位置透明与函数计算的弹性扩缩容理念一致
│
├─→ 06-领域驱动设计与组织动力学
│   └─ Actor ↔ 聚合根：DDD聚合根的不变性维护与Actor的串行消息处理
│       在语义上高度同构
│
├─→ 07-形式化方法与验证体系
│   └─ Actor活性 ↔ 半可判定：无界邮箱使形式化验证需依赖有界抽象或
│       运行时监控（Runtime Verification）
│
└─→ 09-安全模型与可信计算
    └─ Actor隔离 ↔ 安全边界：Actor的状态封装可映射到安全域的隔离策略，
        消息传递对应受控的跨域通信（如Bell-LaPadula的读写规则）
```

## 深度批判性分析（增强版）

Actor模型通过共享状态禁令从根本上消除了数据竞争，这一优雅设计使其成为高可用分布式系统的首选范式，但其工程实践中的隐含假设在真实网络环境中频繁失效，且这些失效往往具有灾难性的级联特征。首先，**消息传递的可靠性假设**是Actor模型最危险的隐性前提：Hewitt (1973) 的原始语义假设消息最终交付且保持FIFO顺序，但在真实网络中，消息丢失、重复、乱序和延迟波动是常态而非异常。当Actor基于"请求-响应"模式构建状态机时，单条消息的丢失可能使Actor永久阻塞在等待状态，形成分布式系统中的"孤儿等待"（orphan waiting）。形式化地，设消息交付概率为 $p < 1$，则 $n$ 轮交互后成功完成的概率为 $p^n \to 0$（当 $n \to \infty$），这意味着长事务在无可靠传输保证下必然失败。其次，**邮箱无界增长**是生产环境中最常见的Actor失效模式：当生产者速率 $r_{\text{in}}$ 持续大于消费者处理速率 $r_{\text{out}}$ 时，邮箱长度 $L(t) = L_0 + (r_{\text{in}} - r_{\text{out}}) \cdot t$ 线性增长直至内存耗尽。虽然Akka等框架引入了背压（backpressure）机制，但这本质上是在Actor语义外部添加的流控层，破坏了模型的纯粹性。第三，**跨Actor事务的缺失**迫使开发者自行实现Saga模式或两阶段提交，这引入了新的复杂性层——事务协调者本身成为单点故障源，且补偿事务的语义正确性难以形式化验证。与CSP的同步握手相比，Actor的异步模型更接近物理网络但更难推理；未来趋势是Akka Typed和类似系统将静态类型检查引入Actor接口，在编译期捕获部分消息协议错误（如向Actor发送未处理类型的消息），同时探索将Actor语义与线性逻辑结合，使消息消费的可追踪性成为类型系统的不变式，从而在保持位置透明的同时恢复部分静态可检查性。

> **国际课程对齐**: MIT 6.042J Mathematics for Computer Science / Stanford CS 103 Mathematical Foundations of Computing / CMU 15-312 Foundations of Programming Languages
