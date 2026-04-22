# Actor模型：异步消息与状态封装

> **定位**：Actor模型是并发计算的"面向对象"——每个Actor是一个独立的计算实体，通过异步消息传递通信。它是Erlang、Akka、 Orleans等系统的理论基础。
>
> **核心命题**：共享状态是并发Bug的根源；Actor模型通过"不共享任何东西"（shared-nothing）从根本上消除了数据竞争。

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

---

*文件创建日期：2026-04-23*
*状态：已完成*
