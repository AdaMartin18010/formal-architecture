import os
import re

FORMAL_DEFS = {
    "Analysis/07-分布式与微服务/05-微服务架构理论.md": """
---

## 形式化定义

### 定义 1.2 (微服务架构的进程代数模型)

**微服务架构**（Microservices Architecture）可形式化为**进程代数**（Process Algebra）中的并行组合：

$$\\mathcal{MA} = \\langle \\mathcal{S}, \\mathcal{P}, \\mathcal{C}, \\parallel, \\backslash_L \\rangle$$

其中：
- $\\mathcal{S} = \\{s_1, s_2, \\dots, s_n\\}$ 是**服务进程集**，每个 $s_i$ 是一个 $\\pi$-演算进程
- $\\mathcal{P}$ 是**端口/通道集**（Channel Set），服务间通过通道 $c \\in \\mathcal{P}$ 通信
- $\\mathcal{C} \\subseteq 2^{\\mathcal{S}}$ 是**一致性协议配置**
- $\\parallel$ 是**并行组合运算符**：$\\mathcal{MA} = s_1 \\parallel s_2 \\parallel \\dots \\parallel s_n$
- $\\backslash_L$ 是**限制运算符**，隐藏内部通道 $L \\subseteq \\mathcal{P}$

### 定义 2.1 (服务边界的类型隔离)

**服务边界**（Service Boundary）通过**类型隔离**（Type Isolation）形式化：

$$\\forall s_i, s_j \\in \\mathcal{S}, \\; i \\neq j \\Rightarrow \\text{Type}(\\gamma(s_i)) \\cap \\text{Type}(\\gamma(s_j)) = \\emptyset$$

其中 $\\gamma: \\mathcal{S} \\rightarrow 2^{Data}$ 为数据所有权函数。服务接口类型签名 $\\Sigma_s$ 构成服务的**公共契约**：

$$\\Sigma_s = \\langle In_s, Out_s, Err_s, Pre_s, Post_s \\rangle$$

- $In_s$: 输入类型集合
- $Out_s$: 输出类型集合
- $Err_s$: 异常类型集合
- $Pre_s$: 前置条件谓词
- $Post_s$: 后置条件谓词

### 定义 3.1 (同步与异步通信的时序逻辑)

服务通信模式通过**时序逻辑公式**区分：

**同步通信**：

$$\\phi_{sync} = \\square (req \\rightarrow \\Diamond resp)$$

即每次请求 $req$ 最终必得到响应 $resp$（$\\square$ 为全局算子，$\\Diamond$ 为最终算子）。

**异步通信**：

$$\\phi_{async} = \\square (pub \\rightarrow \\neg \\text{block}) \\land \\Diamond deliv$$

即发布事件 $pub$ 不阻塞发送方，且消息最终投递 $deliv$ 无严格时限约束。

### 定义 4.1 (熔断降级的状态自动机)

**熔断器**（Circuit Breaker）是一个三状态有限自动机：

$$\\mathcal{CB} = \\langle \\{Closed, Open, HalfOpen\\}, \\{fail, success, timeout\\}, \\delta, Closed \\rangle$$

转移函数 $\\delta$ 定义为：

$$\\delta(Closed, fail) = Closed \\quad \\text{(故障计数)}$$
$$\\delta(Closed, timeout) = Open \\quad \\text{(超过阈值则熔断)}$$
$$\\delta(Open, timeout) = HalfOpen \\quad \\text{(超时后试探)}$$
$$\\delta(HalfOpen, success) = Closed \\quad \\text{(恢复)}$$
$$\\delta(HalfOpen, fail) = Open \\quad \\text{(再次熔断)}$$

> **来源**：Newman, S. (2021). *Building Microservices* (2nd ed.). O'Reilly; Milner, R. (1999). *Communicating and Mobile Systems: The $\\pi$-Calculus*. Cambridge University Press.

""",
    
    "Analysis/07-分布式与微服务/06-云原生架构理论.md": """
---

## 形式化定义

### 定义 1.2 (云原生架构的自适应控制系统)

**云原生架构**（Cloud-Native Architecture）可形式化为**自适应控制系统**（Adaptive Control System）：

$$\\mathcal{CN} = \\langle \\mathcal{C}, \\mathcal{O}, \\mathcal{M}, \\mathcal{A}, \\mathcal{F} \\rangle$$

其中：
- $\\mathcal{C} = \\{c_1, c_2, \\dots, c_n\\}$ 是**容器化组件集**
- $\\mathcal{O}$ 是**编排控制器**（Orchestrator），如 Kubernetes，其状态转移为：

$$O_{t+1} = \\mathcal{O}(O_t, \\Delta_t)$$

其中 $\\Delta_t$ 为 $t$ 时刻观测到的系统偏差
- $\\mathcal{M}: \\mathcal{C} \\rightarrow \\mathbb{R}^k$ 是**监控指标函数**，输出 $k$ 维可观测向量
- $\\mathcal{A}$ 是**自动扩缩容策略**，定义水平扩展规则：

$$\\text{Replicas}(c, t+1) = \\lfloor \\alpha \\cdot \\text{Replicas}(c, t) + \\beta \\cdot \\frac{Load(c, t)}{Target} \\rceil$$

- $\\mathcal{F}$ 是**故障恢复函数**，$\\mathcal{F}: \\mathcal{C} \\times Fault \\rightarrow \\mathcal{C}'$

### 定义 2.1 (容器映像的不可变性公理)

**不可变基础设施**（Immutable Infrastructure）通过映像不变性公理形式化：

$$\\forall img \\in Image, \\; \\forall t_1, t_2, \\; img(t_1) = img(t_2)$$

即容器映像 $img$ 一旦构建即不可变，状态变更只能通过创建新实例实现：

$$\\Delta state \\Rightarrow \\exists img', \\; Deploy(img') \\land Terminate(img)$$

### 定义 3.1 (声明式API的规范-实现一致性)

**声明式API**（Declarative API）定义期望状态 $S_{desired}$ 与实际状态 $S_{actual}$ 之间的**收敛关系**：

$$\\mathcal{K} \\models S_{desired} \\leadsto^* S_{actual}$$

其中 $\\mathcal{K}$ 为编排引擎的控制闭环，$\\leadsto^*$ 为零或多步状态迁移的反射传递闭包。一致性判定：

$$\\text{Consistent}(\\mathcal{K}) \\iff \\forall r \\in Resources, \\; Spec(r) = Observed(r)$$

### 定义 4.1 (服务网格的流量矩阵)

**服务网格**（Service Mesh）中的流量可形式化为**随机矩阵**（Stochastic Matrix）：

$$\\mathbf{T} = [t_{ij}]_{n \\times n}, \\quad t_{ij} = \\frac{Traffic(s_i \\rightarrow s_j)}{\\sum_k Traffic(s_i \\rightarrow s_k)}$$

其中 $\\sum_j t_{ij} = 1$。流量管理策略 $\\Pi$ 作用于矩阵变换：

$$\\mathbf{T}' = \\Pi(\\mathbf{T}, \\theta)$$

$\\theta$ 为策略参数（如权重、故障注入概率、重试次数）。

> **来源**：Burns, B., et al. (2016). *Designing Distributed Systems*. O'Reilly; Hightower, K., Burns, B., & Beda, J. (2017). *Kubernetes: Up and Running*. O'Reilly.

""",
    
    "Analysis/07-分布式与微服务/07-事件驱动架构理论.md": """
---

## 形式化定义

### 定义 1.2 (事件驱动架构的发布-订阅演算)

**事件驱动架构**（Event-Driven Architecture, EDA）可形式化为**发布-订阅演算**（Publish-Subscribe Calculus）：

$$\\mathcal{EDA} = \\langle \\mathcal{P}, \\mathcal{E}, \\mathcal{T}, \\mathcal{S}, pub, sub, notify \\rangle$$

其中：
- $\\mathcal{P} = \\{p_1, p_2, \\dots\\}$ 是**发布者集合**（Publisher Set）
- $\\mathcal{E} = \\{e_1, e_2, \\dots\\}$ 是**事件类型集**
- $\\mathcal{T} = \\{t_1, t_2, \\dots\\}$ 是**主题/通道集合**（Topic Set）
- $\\mathcal{S} = \\{s_1, s_2, \\dots\\}$ 是**订阅者集合**（Subscriber Set）
- $pub: \\mathcal{P} \\times \\mathcal{E} \\times \\mathcal{T} \\rightarrow \\mathcal{M}$ 是**发布函数**，将事件发布到主题通道
- $sub: \\mathcal{S} \\times \\mathcal{T} \\times Filter \\rightarrow \\{0, 1\\}$ 是**订阅关系**
- $notify: \\mathcal{T} \\times \\mathcal{E} \\rightarrow 2^{\\mathcal{S}}$ 是**通知函数**：

$$notify(t, e) = \\{s \\in \\mathcal{S} \\mid sub(s, t, f) = 1 \\land f(e) = \\text{true}\\}$$

### 定义 2.1 (事件结构的因果偏序)

**事件**（Event）的语义通过**因果偏序集**（Causal Poset）形式化：

$$\\mathcal{EV} = \\langle E, \\leq, \\#, \\lambda \\rangle$$

其中：
- $E$ 是事件实例集合
- $\\leq \\subseteq E \\times E$ 是**因果序**（Happens-Before Relation），满足自反、反对称、传递
- $\\# \\subseteq E \\times E$ 是**冲突关系**，满足对称、不可自反：$e \\# e' \\Rightarrow \\neg(\\exists s, \\; e \\leq s \\land e' \\leq s)$
- $\\lambda: E \\rightarrow \\mathcal{L}$ 是**标签函数**，映射到事件类型标签空间 $\\mathcal{L}$

事件一致性要求：

$$\\forall e_1, e_2 \\in E, \\; e_1 \\# e_2 \\Rightarrow \\neg(e_1 \\leq e_2) \\land \\neg(e_2 \\leq e_1)$$

### 定义 5.1 (事件溯源的状态函数)

**事件溯源**（Event Sourcing）将系统状态定义为事件序列的**折叠**（Fold）：

$$State(t) = fold(apply, State_0, [e_1, e_2, \\dots, e_n])$$

其中：
- $State_0$ 为初始状态
- $apply: State \\times E \\rightarrow State$ 为**状态应用函数**
- $[e_1, e_2, \\dots, e_n]$ 为到时刻 $t$ 为止按 $\\leq$ 全序排列的事件序列

事件重放（Replay）的形式化为：

$$\\forall t_1 < t_2, \\; Replay(State_0, [e_1, \\dots, e_{t_2}])_{[1..t_1]} = State(t_1)$$

即截取重放序列的前 $t_1$ 个事件必得到 $t_1$ 时刻状态。

### 定义 5.2 (Saga的事务补偿代数)

**Saga模式**（Saga Pattern）定义一个**可补偿事务序列**：

$$\\mathcal{SAGA} = \\langle [T_1, T_2, \\dots, T_n], [C_1, C_2, \\dots, C_n], \\prec \\rangle$$

其中：
- $T_i$ 为第 $i$ 个子事务
- $C_i$ 为 $T_i$ 对应的**补偿事务**（Compensating Transaction）
- $\\prec$ 为子事务执行全序

 Saga 执行语义：

$$\\text{Exec}(\\mathcal{SAGA}) = \\begin{cases} T_1 \\circ T_2 \\circ \\dots \\circ T_n & \\text{if } \\forall i, T_i \\text{ succeeds} \\ T_1 \\circ \\dots \\circ T_{k-1} \\circ C_{k-1} \\circ \\dots \\circ C_1 & \\text{if } T_k \\text{ fails} \\end{cases}$$

> **来源**：Lamport, L. (1978). Time, Clocks, and the Ordering of Events in a Distributed System. *Communications of the ACM*, 21(7), 558–565; Hohpe, G., & Woolf, B. (2003). *Enterprise Integration Patterns*. Addison-Wesley.

""",
    
    "Analysis/07-分布式与微服务/08-服务网格架构理论.md": """
---

## 形式化定义

### 定义 1.2 (服务网格的代理插入函子)

**服务网格**（Service Mesh）可形式化为**代理插入函子**（Proxy Insertion Functor）：

$$\\mathcal{SM}: \\mathbf{Svc} \\rightarrow \\mathbf{Svc}_{proxied}$$

其中：
- $\\mathbf{Svc}$ 是原始服务范畴，对象为服务 $s = \\langle addr, proto, handler \\rangle$
- $\\mathbf{Svc}_{proxied}$ 是代理增强服务范畴
- $\\mathcal{SM}(s) = s \\triangleleft p_{sidecar}$，$\\triangleleft$ 为 Sidecar 注入运算

代理 $p_{sidecar}$ 的语义为**请求截获器**（Request Interceptor）：

$$p_{sidecar}(req) = \\begin{cases} route(req) & \\text{if } policy(req) = allow \\ drop(req) & \\text{if } policy(req) = deny \\ retry(req) & \\text{if } policy(req) = retry \\end{cases}$$

### 定义 2.1 (数据平面的流处理单子)

**数据平面**（Data Plane）可形式化为**流处理单子**（Stream Processing Monad）：

$$\\mathcal{DP} = \\langle \\mathcal{F}, \\eta, \\mu, bind \\rangle$$

其中：
- $\\mathcal{F}(X) = Stream(X)$ 为流函子
- $\\eta: X \\rightarrow \\mathcal{F}(X)$ 将单个请求包装为单元素流
- $\\mu: \\mathcal{F}(\\mathcal{F}(X)) \\rightarrow \\mathcal{F}(X)$ 为流扁平化
- $bind: \\mathcal{F}(X) \\times (X \\rightarrow \\mathcal{F}(Y)) \\rightarrow \\mathcal{F}(Y)$ 支持流水线组合

流量规则 $R$ 作为 Kleisli 箭头组合：

$$proc = r_{auth} \\bind r_{route} \\bind r_{lb} \\bind r_{retry} \\bind r_{circuit}$$

### 定义 2.2 (负载均衡的加权随机选择)

**负载均衡**（Load Balancing）的加权选择可形式化为**离散概率分布**：

$$P(s_i) = \\frac{w_i}{\\sum_{j=1}^n w_j}$$

其中 $w_i$ 为实例 $s_i$ 的权重。期望负载分配满足：

$$\\mathbb{E}[Load(s_i)] = P(s_i) \\cdot TotalLoad$$

一致性哈希（Consistent Hashing）将请求 $req$ 映射到环空间 $[0, 2^{32})$：

$$hash: Req \\times Instances \\rightarrow [0, 2^{32})$$
$$select(req) = \\arg\\min_{s_i} \\|hash(req) - hash(s_i)\\|_{ring}$$

### 定义 3.1 (控制平面的配置收敛)

**控制平面**（Control Plane）维护**期望配置状态** $Config_{desired}$ 与**数据平面实际配置** $Config_{actual}$ 之间的收敛：

$$\\mathcal{CP} \\vdash Config_{desired} \\leadsto^* Config_{actual}$$

配置一致性判定：

$$\\text{Converged}(\\mathcal{CP}) \\iff \\forall proxy \\in DataPlane, \\; Config_{actual}(proxy) = Project(Config_{desired}, proxy)$$

其中 $Project$ 为按代理标签的投影函数。

> **来源**：Klein, I., et al. (2018). *Istio Up and Running*. O'Reilly; Fidge, C. J. (1991). Logical Time in Distributed Computing Systems. *Computer*, 24(8), 28–33.

""",
    
    "Analysis/07-分布式与微服务/04-软件架构理论体系/01-架构模式理论.md": """
---

## 形式化定义

### 定义 1.2 (架构模式的范畴论模型)

**架构模式**（Architectural Pattern）是一个设计问题的通用解结构，形式化定义为：

$$\\mathcal{AP} = \\langle P, S, C, \\sigma, \\kappa \\rangle$$

其中：
- $P$ 是**问题域**（Problem Domain），描述模式所解决的设计问题集合
- $S$ 是**解结构**（Solution Structure），$S = \\langle Comp, Conn, Cons \\rangle$
  - $Comp$ 为组件集合
  - $Conn \\subseteq Comp \\times Comp$ 为连接器集合
  - $Cons: Comp \\times Conn \\rightarrow \\{0, 1\\}$ 为约束函数
- $C$ 是**上下文条件**（Context Conditions），模式适用的前提谓词
- $\\sigma: P \\times C \\rightarrow S$ 是**求解映射**（Solution Mapping）
- $\\kappa: S \\rightarrow \\mathbb{R}^+$ 是**质量评估函数**（Quality Assessment）

### 定义 2.1 (分层架构的序结构)

**分层架构**（Layered Architecture）定义为一个严格偏序集：

$$\\mathcal{L} = \\langle L, \\prec, \\lambda, \\mu \\rangle$$

其中：
- $L = \\{l_1, l_2, \\dots, l_n\\}$ 是层集合
- $\\prec \\subseteq L \\times L$ 是**依赖序关系**，满足反自反、传递、非对称性
- $\\lambda: L \\rightarrow 2^{Comp}$ 将每层映射到其包含的组件集合
- $\\mu: L \\times L \\rightarrow \\{0, 1\\}$ 是**允许通信谓词**：

$$\\mu(l_i, l_j) = \\begin{cases} 1 & \\text{if } l_i \\prec l_j \\lor l_i = l_j \\lor \\exists l_k, \\; l_i \\prec l_k \\prec l_j \\text{ (间接通信)} \\ 0 & \\text{otherwise} \\end{cases}$$

### 定义 4.1 (微服务架构的服务图)

**微服务架构**（Microservices Architecture）可形式化为有向服务图：

$$\\mathcal{MS} = \\langle S, E, \\omega, \\delta, \\gamma \\rangle$$

其中：
- $S$ 是**服务节点集**（Service Node Set）
- $E \\subseteq S \\times S$ 是**服务间依赖边集**
- $\\omega: S \\rightarrow \\mathbb{R}^+$ 是**服务权重函数**（负载容量）
- $\\delta: E \\rightarrow \\{sync, async\\}$ 是**通信模式标记**
- $\\gamma: S \\rightarrow 2^{Data}$ 是**数据所有权函数**，满足 $s_i \\neq s_j \\Rightarrow \\gamma(s_i) \\cap \\gamma(s_j) = \\emptyset$（数据隔离原则）

> **来源**：Shaw, M., & Garlan, D. (1996). *Software Architecture: Perspectives on an Emerging Discipline*. Prentice Hall; Fowler, M. (2002). *Patterns of Enterprise Application Architecture*. Addison-Wesley.

""",
}

def insert_formal_defs(filepath, defs_text):
    if not os.path.exists(filepath):
        print(f"SKIP (not found): {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '## 形式化定义' in content:
        print(f"SKIP (already has formal defs): {filepath}")
        return False
    
    match = re.search(r'\n## 2025 对齐', content)
    if match:
        insert_pos = match.start()
        new_content = content[:insert_pos] + defs_text + content[insert_pos:]
    else:
        new_content = content.rstrip() + "\n" + defs_text
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"ENHANCED: {filepath}")
    return True

count = 0
for filepath, defs in FORMAL_DEFS.items():
    if insert_formal_defs(filepath, defs):
        count += 1

print(f"\nTotal enhanced in batch 4: {count}")
