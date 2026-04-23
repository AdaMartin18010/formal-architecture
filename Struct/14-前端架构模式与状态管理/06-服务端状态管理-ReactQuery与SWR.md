# 服务端状态管理：React Query 与 SWR

> **来源映射**: View/03.md §4.2, View/04.md §4.2, View/05.md §6-8
> **国际权威参考**: TanStack Query (React Query) Documentation; Vercel SWR Documentation; RFC 5861 "HTTP Cache-Control Extensions for Stale Content" (2010); Fielding et al. "Hypertext Transfer Protocol — HTTP/1.1" (RFC 2616, 1999), Section 13 (Caching)

---

## 一、知识体系思维导图

```text
服务端状态管理
│
├─► 核心问题域
│   ├─ 服务端状态 ≠ 客户端状态 (Server State ≠ Client State)
│   ├─ 服务端状态: 远端持久化、多用户共享、非开发者控制
│   ├─ 客户端状态: UI 临时态、本地缓存、用户私有
│   └─ 分离原则: 服务端状态应通过专用抽象管理，不与全局 Store 混同
│
├─► Stale-While-Revalidate (SWR)
│   ├─ 缓存优先: 立即返回缓存 (stale) → 后台重新验证 (revalidate)
│   ├─ 策略: cache-first → stale-while-revalidate → network-only
│   ├─ 去重: 相同 key 的并发请求自动合并 (deduping)
│   └─ 轮询: refreshInterval 实现周期性背景同步
│
├─► React Query / TanStack Query
│   ├─ QueryClient: 全局缓存管理器 (基于 Map 的规范化缓存)
│   ├─ useQuery: 查询状态机 (idle → loading → success/error)
│   ├─ useMutation: 变更操作 + 乐观更新 (Optimistic Update)
│   └─ 失效策略: queryClient.invalidateQueries(keyPattern)
│
└─► 缓存策略谱系
    ├─ cache-first: 快但可能陈旧 (适用不变数据)
    ├─ network-first: 实时但慢 (适用频繁变更数据)
    ├─ stale-while-revalidate: 平衡策略 (适用大多数场景)
    ├─ cache-only: 纯离线 (PWA 场景)
    └─ network-only: 禁用缓存 (敏感数据)
```

---

## 二、核心概念的形式化定义

### 2.1 服务端状态的形式化特征

```text
定义 (服务端状态):
  ServerState = ⟨data, timestamp, ttl, source_of_truth⟩
  其中:
    data:           远端数据的本地副本
    timestamp:      本地缓存的时间戳
    ttl:            生存时间 (Time To Live)
    source_of_truth: 服务端数据库 (非开发者控制)

  与客户端状态的本质差异:
    ┌─────────────────┬──────────────────┬──────────────────┐
    │     特性         │   服务端状态       │   客户端状态      │
    ├─────────────────┼──────────────────┼──────────────────┤
    │ 所有权           │ 服务端 (共享)      │ 客户端 (私有)     │
    │ 持久性           │ 持久化存储         │ 内存/Storage     │
    │ 并发修改          │ 多用户竞争         │ 单用户独占        │
    │ 一致性要求        │ 最终一致           │ 强一致           │
    │ 网络依赖          │ 必需               │ 可选             │
    │ 失效触发          │ 不可预测           │ 开发者控制        │
    └─────────────────┴──────────────────┴──────────────────┘

  核心公理 (服务端状态不确定性公理):
    ∀s ∈ ServerState, □(s_now = s_server) 不可判定
    (永远无法在本地严格证明缓存与服务端一致)
```

### 2.2 Stale-While-Revalidate 的形式化

```text
定义 (SWR 策略):
  设查询函数 query(key) → Promise<Data>
  设缓存 cache[key] = ⟨data, fetchedAt, isValidating⟩

  SWR 算法:
    1. 读取请求 R(key):
       若 cache[key] 存在:
         立即返回 cache[key].data  (stale 响应)
         若 now - fetchedAt > staleTime:
           触发 background revalidate: query(key).then(d => updateCache(key, d))
       若 cache[key] 不存在:
         返回 loading 状态，执行 query(key) (fetch)

    2. 去重机制 (Deduping):
       设 inflight[key] = 进行中的 Promise
       若 R₁(key) 与 R₂(key) 在 dedupingInterval 内并发发起:
         二者共享 inflight[key]，仅执行一次网络请求

    3. 窗口聚焦重验证 (Revalidate on Focus):
       window.addEventListener('focus', () => {
         对所有活跃 query key 执行 background revalidate
       })

  缓存失效边界:
    SWR 不主动知晓服务端数据何时变更
    依赖: 时间过期 (ttl)、手动触发 (mutate)、聚焦重验、轮询
```

### 2.3 React Query 的状态机与乐观更新

```text
定义 (Query 状态机):
  QueryState = { idle, loading, error, success }
  转移函数:
    idle --fetch--> loading --success--> success
    idle --fetch--> loading --failure--> error
    success --refetch--> loading --success--> success
    success --invalidate--> loading ...

定义 (乐观更新 Optimistic Update):
  设变更操作 mutation: (oldData, variables) → newData
  乐观更新协议:
    1. 在 mutation 请求发出前，立即更新 UI 为预测状态
       cache[key] = applyMutation(cache[key], variables)  (乐观)
    2. 发送实际 mutation 请求到服务端
    3. 若成功: 用服务端返回数据替换乐观状态 (确认)
    4. 若失败: 回滚到乐观更新前的状态 (rollback)

  形式化约束:
    乐观更新必须满足「可逆性」: ∃rollback : State → State
    若 mutation 失败，rollback(optimisticState) = originalState
    在 UI 层面表现为「无闪烁的状态恢复」
```

---

## 三、多维矩阵对比

| 维度 | SWR (Vercel) | React Query v4 | React Query v5 | Apollo Client |
|------|-------------|----------------|----------------|---------------|
| **核心策略** | Stale-While-Revalidate | **规范化缓存 + 后台同步** | 同上 (类型强化) | GraphQL 缓存 |
| **缓存结构** | key → data | **key → 规范化实体** | 同上 | 实体 + 引用 |
| **乐观更新** | ⚠️ 手动实现 | **原生支持** | **原生支持** | 原生支持 |
| **离线能力** | 弱 | 中 (devtools) | 中 | **强** (Apollo 持久化) |
| **去重机制** | ✅ 自动 | ✅ 自动 | ✅ 自动 | ✅ 自动 |
| **DevTools** | 无 | **★★★★★** | **★★★★★** | ★★★★ |
| **包体积** | **小 (~4KB)** | 中 (~12KB) | 中 (~12KB) | 大 (~30KB+) |
| **框架绑定** | React | React/Vue/Svelte/Solid | React/Vue/Svelte/Solid | React 优先 |
| **2026年首选** | 轻量项目 | **中大型项目** | **新项目** | GraphQL 生态 |

---

## 四、权威引用

> **RFC 5861** ("HTTP Cache-Control Extensions for Stale Content", 2010):
> "The stale-while-revalidate response directive indicates that caches may serve a response after it becomes stale, up to the indicated number of seconds." — SWR 库直接以此 HTTP 缓存语义命名。

> **Tanner Linsley** (TanStack Query 作者):
> "Server state is a completely different beast from client state. It's asynchronous, shared, and persisted somewhere else. You need a tool built specifically for it."

> **Guillermo Rauch** (Vercel CEO, SWR 倡导者):
> "SWR is a strategy to first return the data from cache (stale), then send the fetch request (revalidate), and finally come with the up-to-date data."

> **Roy Fielding** (REST 论文, 2000):
> "The central feature that distinguishes the REST architectural style from other network-based styles is its emphasis on a uniform interface between components."

---

## 五、工程实践与代码示例

### 5.1 React Query 的查询与变更

```tsx
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

// 查询: 自动缓存、后台重验证、错误重试
function usePosts() {
  return useQuery({
    queryKey: ["posts"],
    queryFn: async () => {
      const res = await fetch("/api/posts");
      return res.json();
    },
    staleTime: 60 * 1000,      // 1 分钟内视为 fresh，不触发后台请求
    gcTime: 5 * 60 * 1000,     // 5 分钟无引用后垃圾回收
  });
}

// 变更: 乐观更新 + 缓存失效
function useCreatePost() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (newPost) =>
      fetch("/api/posts", {
        method: "POST",
        body: JSON.stringify(newPost),
      }).then((r) => r.json()),

    // 乐观更新: 请求发出前立即更新 UI
    onMutate: async (newPost) => {
      await queryClient.cancelQueries({ queryKey: ["posts"] });
      const previousPosts = queryClient.getQueryData(["posts"]);
      queryClient.setQueryData(["posts"], (old) => [newPost, ...old]);
      return { previousPosts }; // 上下文供回滚使用
    },

    // 失败回滚
    onError: (err, newPost, context) => {
      queryClient.setQueryData(["posts"], context.previousPosts);
    },

    // 成功后重新验证 (或直接使用服务端返回数据)
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["posts"] });
    },
  });
}
```

### 5.2 SWR 的极简数据获取

```tsx
import useSWR from "swr";

const fetcher = (url) => fetch(url).then((r) => r.json());

function Profile({ userId }) {
  // 自动缓存、去重、错误重试、聚焦重验证
  const { data, error, isLoading } = useSWR(
    `/api/user/${userId}`,
    fetcher,
    {
      refreshInterval: 30000,      // 30 秒轮询
      revalidateOnFocus: true,     // 窗口聚焦时重验证
      dedupingInterval: 2000,      // 2 秒内并发请求去重
    }
  );

  if (isLoading) return <div>加载中...</div>;
  if (error) return <div>加载失败</div>;
  return <div>用户名: {data.name}</div>;
}
```

---

## 六、批判性总结

服务端状态管理库的崛起标志着前端架构对「状态本体论」认知的成熟：开发者终于意识到，「来自服务端的数据」与「客户端的 UI 状态」在所有权、生命周期、一致性要求等维度上存在本质差异，强行将二者纳入同一套 Redux Store 管理是一种「范畴错误」。React Query 与 SWR 的核心贡献不在于其技术实现——缓存、去重、轮询、重试都是计算机科学中的经典问题——而在于它们以**专用抽象**的形式，将「服务端状态的不确定性」从应用代码中隔离出来，使开发者能够以声明式的方式表达「我希望获取这个数据，并在其生命周期内自动处理缓存与同步」，而非手动编写数十行的 useEffect + fetch + loading state + error state 的样板代码。

然而，Staleness（陈旧性）是这类库无法根本消除的原罪。SWR 的命名本身就揭示了其哲学立场：「首先返回缓存（可能是陈旧的），然后在后台重新验证」。这意味着用户在某些时刻看到的必然是「过时的真相」，而框架对此的唯一补偿是「尽快让它不那么过时」。这种「最终一致性」的语义与金融交易、实时协作等对强一致性有严格要求的场景存在结构性冲突。乐观更新（Optimistic Update）虽然在 UI 层面提供了即时反馈，但其回滚机制在复杂并发场景下（如用户快速连续操作、网络抖动导致的乱序响应）可能产生令人困惑的状态跳跃。

从更宏观的架构视角审视，React Query 和 SWR 实际上扮演了「客户端-服务端边界上的缓存协调器」角色，这与操作系统中的「分布式文件系统缓存」或「数据库连接池」具有同构的职责。2026 年的演进趋势表明，这一层正在与 RSC（React Server Components）和 Server Actions 发生融合：当数据获取逻辑迁移到服务端组件内部时，客户端「服务端状态管理」的适用范围将被重新定义——它不再是「如何缓存 REST API 响应」，而是「如何协调服务端渲染流与客户端交互状态的边界」。无论技术形态如何变迁，「服务端状态的不确定性公理」将永远成立：客户端永远无法在本地严格证明其缓存与服务端一致，这是分布式系统本质的不可约命题。


---

## 七、概念属性关系网络

| 概念A | 关系 | 概念B | 关系说明 |
|-------|------|-------|----------|
| **服务端状态** | **对立** | 客户端状态 | 所有权(服务端/客户端)、持久性(持久/内存)、并发修改(多用户/单用户) |
| **SWR** | **包含** | stale-while-revalidate 策略 | 缓存优先 → 后台重新验证，RFC 5861 的 HTTP 缓存语义 |
| **React Query** | **包含** | QueryClient · useQuery · useMutation · invalidateQueries | 规范化缓存 + 查询状态机 + 乐观更新 |
| **Query 状态机** | **包含** | idle → loading → success/error | 自动管理查询生命周期的状态转移 |
| **乐观更新** | **依赖** | 可逆性公理 | ∃rollback : State → State，失败时恢复原始状态 |
| **去重机制** | **依赖** | dedupingInterval | 相同 key 的并发请求在间隔内自动合并 |
| **窗口聚焦重验** | **依赖** | visibilitychange/focus 事件 | 用户返回页面时自动后台重新验证 |
| **staleTime** | **对立** | gcTime | staleTime: 多久后视为 stale；gcTime: 多久无引用后垃圾回收 |
| **React Query** | **演化** | TanStack Query | 从 React 专用扩展到框架无关（Vue/Svelte/Solid） |
| **缓存策略** | **包含** | cache-first · network-first · stale-while-revalidate · cache-only · network-only | 五种策略对应不同数据新鲜度与性能需求 |

---

## 八、形式化推理链

```text
公理 A1 (状态闭包): ∀s ∈ State, ∃!ui ∈ DOM : ui = f(s)
        ↓
引理 L1 (服务端状态不确定性): ∀s ∈ ServerState, □(s_now = s_server) 不可判定
                             永远无法在本地严格证明缓存与服务端一致
        ↓
引理 L2 (SWR 最终一致性): SWR 首先返回缓存（可能是陈旧的），然后在后台重新验证，
                          用户在某些时刻看到的必然是「过时的真相」
        ↓
定理 T24 (陈旧性原罪): Staleness 是服务端状态管理库无法根本消除的原罪；
                       其唯一补偿是「尽快让它不那么过时」
        ↓
推论 C1 (强一致冲突): SWR 的「最终一致性」语义与金融交易、实时协作等
                      对强一致性有严格要求的场景存在结构性冲突
```

```text
公理 A3 (变更最小化): Δs → min(|ΔDOM|)
        ↓
引理 L3 (乐观更新可逆性): 乐观更新必须满足 ∃rollback : State → State，
                           若 mutation 失败，rollback(optimisticState) = originalState
        ↓
引理 L4 (并发乱序风险): 用户快速连续操作或网络抖动导致乱序响应时，
                        乐观更新的回滚机制可能产生令人困惑的状态跳跃
        ↓
定理 T25 (React Query 协调器角色): React Query / SWR 扮演「客户端-服务端边界上的缓存协调器」，
                                    与操作系统「分布式文件系统缓存」或「数据库连接池」同构
        ↓
推论 C2 (RSC 融合趋势): 当数据获取逻辑迁移到 RSC 内部时，客户端「服务端状态管理」的适用范围
                        将被重新定义为「服务端渲染流与客户端交互状态的边界协调」
```

---

## 九、推理判定树：SWR vs React Query vs Apollo Client？

```text
                    [开始: 服务端状态管理库选型]
                          │
                          ▼
                ┌─────────────────┐
                │ Q1: 数据协议?   │
                │ REST / GraphQL  │
                └────────┬────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
      [REST]          [GraphQL]         [混合]
        │                │                │
        ▼                ▼                ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ Q2: 项目规模? │ │ Q2: 离线需求? │ │ Q2: 类型安全? │
│ 小 / 中 / 大  │ │ 强 / 弱       │ │ 需要 / 不需要 │
└───────┬───────┘ └───────┬───────┘ └───────┬───────┘
        │                 │                 │
   ┌────┴────┐       ┌────┴────┐       ┌────┴────┐
   ▼    ▼    ▼       ▼         ▼       ▼         ▼
  [小]  [中]  [大]   [强]      [弱]    [需要]    [不需要]
   │     │     │      │         │       │         │
   ▼     ▼     ▼      ▼         ▼       ▼         ▼
  SWR  React React  Apollo    Apollo  Apollo   React
       Query Query  Client    Client  Client   Query
       v5    v5     (持久化)  (标准)  (强类型) (灵活)
```

---

## 十、国际课程对齐标注

| 课程代码 | 课程名称 | 对齐章节 | 映射内容 |
|----------|----------|----------|----------|
| **Stanford CS 142** | Web Applications (Rosenblum, 2023) | Lecture: Browser/Server Communication (Week 5); Lecture: Sessions and Caching (Week 7) | SWR 的 HTTP 缓存语义与浏览器缓存机制；React Query 的查询状态机与 REST API 错误处理；乐观更新的用户体验设计 |
| **CMU 15-213** | Computer Systems (Bryant & O'Hallaron, 2016) | Chapter 6: Memory Hierarchy; Chapter 12: Concurrent Programming | 服务端状态的本地缓存对应 CPU 缓存层次结构（L1/L2/L3）；缓存失效策略对应缓存一致性协议（MESI）；去重机制对应连接池与请求合并 |
| **MIT 6.170** | Software Studio (Daniel Jackson, 2013) | Lecture: RESTful APIs; Lecture: Web Servers and Web Apps | SWR 的 stale-while-revalidate 策略与 HTTP Cache-Control 语义；React Query 的规范化缓存与关系数据库范式对比；服务端状态与客户端状态的「范畴错误」分离 |

> **学术溯源**: SWR 的命名直接引用 **RFC 5861** (2010) «HTTP Cache-Control Extensions for Stale Content» 中 "stale-while-revalidate" 响应指令；React Query 的规范化缓存设计受 **Roy Fielding** (2000) REST 论文中「统一接口」与「无状态通信」原则的间接启发；服务端状态管理的不确定性公理受 **Leslie Lamport** (1978) «Time, Clocks, and the Ordering of Events in a Distributed System» 中「分布式系统不存在全局时钟」的深刻影响——客户端与服务端的缓存状态不存在全局一致性时钟；乐观更新的可逆性约束受 **Jim Gray** (1981) 事务处理理论中 ACID 原子性与补偿事务 (Compensating Transaction) 思想的工程映射。

---

## 十一、深度批判性形式化总结（增强版）

服务端状态管理库的崛起标志着前端架构对「状态本体论」认知的成熟：开发者终于意识到，「来自服务端的数据」与「客户端的 UI 状态」在所有权、生命周期、一致性要求等维度上存在本质差异，强行将二者纳入同一套 Redux Store 管理是一种「范畴错误」。**Tanner Linsley** (TanStack Query 作者) 将服务端状态定义为「完全不同的野兽——它是异步的、共享的、持久化在别处的」——这一洞见的形式化内涵在于：服务端状态空间与客户端状态空间具有不同的拓扑结构，需要专用抽象来管理其不确定性。**Guillermo Rauch** (Vercel CEO) 将 SWR 策略概括为「首先返回缓存（stale），然后发送请求（revalidate），最后带回最新数据」——这一描述在数学上对应于一个近似一致性的收敛过程，而非严格的一致性保证。

然而，Staleness（陈旧性）是这类库无法根本消除的原罪。SWR 的命名本身就揭示了其哲学立场：「首先返回缓存（可能是陈旧的），然后在后台重新验证」。这意味着用户在某些时刻看到的必然是「过时的真相」，而框架对此的唯一补偿是「尽快让它不那么过时」。这种「最终一致性」的语义与金融交易、实时协作等对强一致性有严格要求的场景存在结构性冲突。乐观更新（Optimistic Update）虽然在 UI 层面提供了即时反馈，但其回滚机制在复杂并发场景下——用户快速连续操作、网络抖动导致的乱序响应——可能产生令人困惑的状态跳跃。**Jim Gray** (1981) 的事务处理理论要求原子操作满足「全有或全无」的语义，但前端乐观更新仅是「尽最大努力」的近似，其回滚函数 rollback: State → State 在工程实践中往往无法保证严格的可逆性。

从更宏观的架构视角审视，React Query 和 SWR 实际上扮演了「客户端-服务端边界上的缓存协调器」角色，这与操作系统中的「分布式文件系统缓存」或「数据库连接池」具有同构的职责。2026 年的演进趋势表明，这一层正在与 RSC（React Server Components）和 Server Actions 发生融合：当数据获取逻辑迁移到服务端组件内部时，客户端「服务端状态管理」的适用范围将被重新定义——它不再是「如何缓存 REST API 响应」，而是「如何协调服务端渲染流与客户端交互状态的边界」。无论技术形态如何变迁，**Leslie Lamport** (1978) 的洞察将永远成立：分布式系统不存在全局时钟，客户端永远无法在本地严格证明其缓存与服务端一致——这是分布式系统本质的不可约命题，也是服务端状态管理理论永远无法跨越的形式化边界。
