# 前端并发模型：CSP / Actor / STM 映射

> **来源映射**: View/05.md §3.1
> **国际权威参考**: C.A.R. Hoare "Communicating Sequential Processes" (CACM, 1978; Prentice Hall, 1985); Carl Hewitt et al. "A Universal Modular Actor Formalism for Artificial Intelligence" (IJCAI, 1973); Shavit & Touitou "Software Transactional Memory" (PODC, 1995); Nir Shavit "The Art of Multiprocessor Programming" (Morgan Kaufmann, 2008)

---

## 一、知识体系思维导图

```text
前端并发模型映射
│
├─► CSP (Communicating Sequential Processes)
│   ├─ 形式化基础: Hoare 进程代数
│   ├─ 核心原语: 进程隔离 + 显式消息通道
│   ├─ 前端映射: Web Workers + postMessage
│   ├─ 消息语义: 结构化克隆算法 (Structured Clone)
│   └─ 适用场景: 计算密集型任务 (图像处理、AI 推理、大数据排序)
│
├─► Actor 模型
│   ├─ 形式化基础: Hewitt 演员模型
│   ├─ 核心原语: 异步消息邮箱 + 无共享状态
│   ├─ 前端映射: Service Worker + event.waitUntil
│   ├─ 生命周期: install → activate → fetch/message
│   └─ 适用场景: 后台同步、推送通知、离线缓存、拦截请求
│
├─► STM (Software Transactional Memory)
│   ├─ 形式化基础: Shavit/Touitou 事务内存
│   ├─ 核心原语: 原子性事务 + 冲突检测 + 自动回滚
│   ├─ 前端映射: React Concurrent (useTransition / startTransition)
│   ├─ 冲突解决: Lane 位掩码优先级调度 (非形式化 STM)
│   └─ 适用场景: UI 状态的原子更新、优先级调度、可中断渲染
│
└─► 数据并行
    ├─ SIMD / SPMD 映射: WebGPU Compute Shader
    ├─ SharedArrayBuffer + Atomics: 主线程与 Worker 共享内存
    └─ 适用场景: 矩阵运算、图像滤镜、AI 模型推理
```

---

## 二、核心概念的形式化定义

### 2.1 CSP 在前端的映射：Web Workers

```text
定义 (CSP 进程):
  进程 P = ⟨state, channel_in, channel_out, behavior⟩
  通信约束: 进程间不共享内存，仅通过显式通道交换消息
  确定性: 给定相同输入序列，进程产生相同输出序列

前端映射 (Web Workers):
  Worker = ⟨isolated_js_runtime, postMessage, onmessage⟩
  通道: MessageChannel / postMessage
  消息协议: Structured Clone Algorithm (支持大多数 JS 类型，不含函数)
  隔离性: Worker 无 DOM 访问权、无 window 对象、独立事件循环

形式化差异:
  经典 CSP: 通道是 first-class 实体，可传递、组合、选择 (alt)
  Web Workers: 仅支持点对点 postMessage，无原生 alt/select 原语
  补偿: 通过 Promise + AbortController 模拟选择操作
```

### 2.2 Actor 在前端的映射：Service Workers

```text
定义 (Actor):
  Actor = ⟨state, mailbox, behavior, address⟩
  行为: 接收消息 → 更新状态 → 发送消息 → 创建新 Actor
  无共享状态: Actor 之间仅通过异步消息通信

前端映射 (Service Worker):
  SW = ⟨cache_storage, fetch_event_mailbox, install/activate/fetch_handlers⟩
  邮箱: FetchEvent / PushEvent / MessageEvent 队列
  生命周期 Actor 行为:
    install:  预缓存静态资源 → self.skipWaiting()
    activate: 清理旧缓存 → clients.claim()
    fetch:    拦截网络请求 → 缓存优先/网络优先/仅缓存策略
  event.waitUntil(promise): 延长事件生命周期直至异步操作完成

形式化差异:
  经典 Actor: 可动态创建任意数量 Actor
  Service Worker: 单例 (每个 scope 仅一个激活实例)
  经典 Actor: 消息顺序不保证
  Service Worker: FetchEvent 顺序与请求顺序一致
```

### 2.3 STM 在前端的映射：React Concurrent

```text
定义 (软件事务内存):
  事务 T = ⟨read_set, write_set, validation, commit⟩
  原子性: 事务内所有操作要么全部提交，要么全部回滚
  隔离性: 并发事务的冲突通过乐观/悲观锁检测解决

前端映射 (React Concurrent Features):
  useTransition / startTransition:
    将状态更新标记为 "非紧急" (TransitionPriority)
    可被更高优先级的更新中断
    中断后自动「回滚」到一致状态 (WorkInProgress 树丢弃)

  与 STM 的形式化差距:
    ┌──────────────────┬──────────────────┬──────────────────┐
    │      特性         │     经典 STM      │   React Concurrent│
    ├──────────────────┼──────────────────┼──────────────────┤
    │ 冲突检测          │ 显式 read/write set│ Lane 位掩码启发式 │
    │ 回滚机制          │ 完全自动回滚       │ 丢弃 WIP 树       │
    │ 隔离级别          │ 可配置 (SI/RR/S)   │ 无明确级别        │
    │ 嵌套事务          │ 支持               │ 不支持           │
    │ 持久性            │ ACID-D             │ 无持久化保证      │
    └──────────────────┴──────────────────┴──────────────────┘

  结论: React Concurrent 是 STM 的**工程隐喻**而非**形式化实现**
```

### 2.4 SharedArrayBuffer + Atomics：底层内存共享

```text
定义 (共享内存并发):
  SharedArrayBuffer: 可被多个 Worker + 主线程共享的线性内存
  Atomics API: 提供原子操作 (load, store, add, and, or, xor, exchange, compareExchange)
  内存模型: ECMAScript Shared Memory and Atomics Model (ES2017)

  形式化约束:
    无数据竞争 (Data Race Freedom):
      对同一内存位置的访问，若至少一个为写，则必须使用 Atomics
      否则行为未定义 (Undefined Behavior in JS!)

  同步原语:
    Atomics.wait:   在指定地址上阻塞，直至被唤醒
    Atomics.notify: 唤醒在指定地址上等待的线程
    等价于: 基于内存地址的「条件变量」或「信号量」
```

---

## 三、多维矩阵对比

| 维度 | CSP (Web Workers) | Actor (Service Worker) | STM (React Concurrent) | SharedArrayBuffer |
|------|-------------------|------------------------|------------------------|-------------------|
| **共享状态** | ❌ 消息传递 | ❌ 事件邮箱 | ⚠️ 树结构副本 | **✅ 直接共享** |
| **通信开销** | 中 (序列化) | 低 (事件驱动) | 低 (同一线程) | **极低 (内存)** |
| **容错隔离** | **进程崩溃隔离** | **Scope 隔离** | 同线程无隔离 | 同线程无隔离 |
| **调试复杂度** | 高 (跨线程) | 高 (生命周期) | 中 (时间切片) | **极高 (数据竞争)** |
| **适用场景** | 计算密集型 | 网络代理/离线 | UI 响应性优化 | 高性能计算 |
| **标准状态** | ✅ 稳定标准 | ✅ 稳定标准 | ✅ React 18+ | ⚠️ 受 Spectre 限制 |
| **形式化纯度** | **高** (接近 CSP) | **中** (单例限制) | **低** (启发式) | **高** (内存模型) |

---

## 四、权威引用

> **C.A.R. Hoare** ("Communicating Sequential Processes", 1978):
> "Programs are regarded as networks of communicating processes, and their execution is modeled in terms of the exchanges of messages between them."

> **Carl Hewitt** ("A Universal Modular Actor Formalism", 1973):
> "An Actor is a computational entity that, in response to a message it receives, can concurrently send a finite number of messages to other Actors, create a finite number of new Actors, and designate the behavior to be used for the next message it receives."

> **Nir Shavit & Dan Touitou** ("Software Transactional Memory", PODC 1995):
> "STM provides the performance of fine-grained locking while maintaining the simplicity of coarse-grained locking."

> **React Team** (React 18 Concurrent Mode Documentation):
> "Concurrent React is a set of new features that help React apps stay responsive and gracefully adjust to the user's device capabilities and network speed."

---

## 五、工程实践与代码示例

### 5.1 Web Worker 的 CSP 风格消息通道

```js
// main.js —— 主线程 (进程 A)
const worker = new Worker("worker.js");

// 显式消息通道 (符合 CSP 显式通信原则)
const { port1, port2 } = new MessageChannel();
worker.postMessage({ type: "INIT_CHANNEL", port: port2 }, [port2]);

port1.onmessage = (e) => {
  console.log("Worker 结果:", e.data);
};

port1.postMessage({ task: "HEAVY_COMPUTE", data: largeArray });

// worker.js —— Worker 线程 (进程 B)
self.onmessage = (e) => {
  if (e.data.type === "INIT_CHANNEL") {
    const port = e.data.port;
    port.onmessage = (msg) => {
      const result = heavyComputation(msg.data.data);
      port.postMessage({ result }); // 通过显式通道回复
    };
  }
};
```

### 5.2 Service Worker 的 Actor 生命周期

```js
// sw.js —— Service Worker (单例 Actor)
const CACHE_NAME = "v1";
const PRECACHE_ASSETS = ["/", "/styles.css", "/app.js"];

// install: 预缓存 (Actor 初始化行为)
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_ASSETS))
  );
  self.skipWaiting(); // 立即激活新版本
});

// activate: 清理旧状态 (Actor 状态迁移)
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim(); // 接管所有客户端
});

// fetch: 拦截请求 (Actor 消息处理行为)
self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request); // 缓存优先策略
    })
  );
});
```

---

## 六、批判性总结

前端并发模型的理论映射是一项充满诱惑却也布满陷阱的智力工程。Web Workers 向 CSP 的映射在概念上最为纯粹——进程隔离、显式消息通道、无共享状态——但 JavaScript 的 Structured Clone Algorithm 限制了消息类型的丰富性（函数、Symbol、DOM 节点均不可传递），这使得「通道即 first-class 实体」的理想被迫妥协为「序列化管道」的现实。Service Worker 的 Actor 映射则受困于浏览器安全模型的根本约束：每个 scope 仅允许一个激活实例，这与经典 Actor 模型中「动态创建无限 Actor」的自由度形成尖锐对比，使其更像一个「受监禁的代理进程」而非「自主的计算实体」。

React Concurrent 与 STM 的类比是最为牵强却也最具工程价值的映射。useTransition 的「可中断更新 + 状态回滚」确实在隐喻层面呼应了事务的原子性与隔离性，但 React 的实现完全抛弃了 STM 的形式化基础：没有 read/write set 的显式追踪，没有冲突检测的严格语义，没有可配置的隔离级别，甚至不存在真正的「回滚」——它只是丢弃了尚未提交的 WorkInProgress 树。Lane 位掩码优先级调度是一种实用的启发式工程方案，但若以数据库事务的理论标准审视，它连最宽松的「读取已提交」隔离级别都无法保证。

SharedArrayBuffer 与 Atomics API 代表了前端并发向系统编程靠拢的最激进尝试，但 Spectre 安全漏洞引发的「站点隔离」政策使其在跨域场景中几乎被废黜。这一技术史插曲揭示了一个深层真理：**前端运行时的安全模型与并发模型的演进是同一枚硬币的两面**。2026 年的共识是：前端并发不应追求「通用计算框架」的野心，而应在「CSP 风格的任务卸载」「Actor 风格的生命周期管理」与「同线程协作式调度」之间根据场景做出理性选择。WebGPU Compute Shader 的兴起标志着数据并行路径的独立成熟——它不与任何经典并发模型直接映射，却在前端高性能计算领域开辟了新大陆。
