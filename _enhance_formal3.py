import os
import re

FORMAL_DEFS = {
    "Analysis/06-软件架构理论体系/07-事件驱动架构理论.md": """
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
    
    "Analysis/06-软件架构理论体系/08-服务网格架构理论.md": """
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
    
    "Analysis/07-分布式与微服务/00-分布式与微服务理论体系总论-整合版.md": """
---

## 形式化定义

### 定义 1.1 (分布式系统的异步消息传递模型)

**分布式系统**（Distributed System）形式化为**异步消息传递系统**（Asynchronous Message-Passing System）：

$$\\mathcal{DS} = \\langle N, C, P, S, \\xrightarrow{msg} \\rangle$$

其中：
- $N = \\{n_1, n_2, \\dots, n_k\\}$ 是**节点有限集**
- $C: N \\times N \\rightarrow Channel$ 是**通道函数**，节点间通过异步通道通信
- $P = \\{p_1, p_2, \\dots\\}$ 是**协议集合**
- $S = \\prod_{i=1}^k S_i$ 是**全局状态空间**，$S_i$ 为节点 $n_i$ 的局部状态
- $\\xrightarrow{msg} \\subseteq S \\times Msg \\times S$ 是**消息触发状态迁移关系**

### 定义 1.2 (USTS 的 Petri 网扩展)

**统一状态转换系统**（USTS）在分布式语境下扩展为**有色 Petri 网**（Colored Petri Net）：

$$\\mathcal{USTS}_{dist} = \\langle P_{dist}, T_{dist}, A, W, M_0, C_{color} \\rangle$$

其中：
- $P_{dist} = \\bigcup_{i=1}^k P_i$ 为分布式库所集，$P_i$ 归属节点 $n_i$
- $T_{dist} = T_{local} \\cup T_{sync}$，$T_{local}$ 为本地变迁，$T_{sync}$ 为跨节点同步变迁
- $A \\subseteq (P_{dist} \\times T_{dist}) \\cup (T_{dist} \\times P_{dist})$ 为弧集
- $W: A \\rightarrow Bag(C_{color})$ 为加权弧表达式
- $M_0: P_{dist} \\rightarrow Bag(C_{color})$ 为初始标记
- $C_{color}$ 为颜色类型集（数据类型）

### 定义 1.3 (CAP 定理的形式化表述)

**CAP 定理**（Brewer, 2000）的形式化表述：

设分布式系统 $\\mathcal{DS}$ 在分区事件 $\\pi$ 下运行，定义三个属性：

$$C(\\mathcal{DS}) \\iff \\forall r_1, r_2 \\in Reads, \\; r_1 = r_2 \\quad \\text{(一致性)}$$
$$A(\\mathcal{DS}) \\iff \\forall req, \\; \\Diamond resp(req) \\quad \\text{(可用性)}$$
$$P(\\mathcal{DS}) = \\text{NetworkPartition}(\\mathcal{DS}, t) \\quad \\text{(分区容错性)}$$

CAP 定理断言：

$$\\forall \\mathcal{DS}, \\; P(\\mathcal{DS}) \\Rightarrow \\neg(C(\\mathcal{DS}) \\land A(\\mathcal{DS}))$$

即分区容错系统无法同时保证强一致性与完全可用性。

### 定义 1.4 (FLP 不可能性)

**FLP 不可能定理**（Fischer, Lynch, Paterson, 1985）：

在**异步系统模型** $\\mathcal{A}$ 中，即使仅存在一个**崩溃故障**节点 $n_f \\in N$，也不存在确定性共识算法 $Alg$ 能在有限步内保证所有正确节点达成一致：

$$\\neg\\exists Alg, \\; \\forall \\mathcal{DS} \\in \\mathcal{A}, \\; \\forall n_f \\in N, \\; \\text{Crash}(n_f) \\Rightarrow \\text{Consensus}(Alg, \\mathcal{DS}) \\text{ in finite steps}$$

> **来源**：Lamport, L. (1978). Time, Clocks, and the Ordering of Events. *CACM*, 21(7), 558–565; Fischer, M. J., Lynch, N. A., & Paterson, M. S. (1985). Impossibility of Distributed Consensus with One Faulty Process. *JACM*, 32(2), 374–382; Brewer, E. (2000). Towards Robust Distributed Systems. *PODC '00*.

""",
    
    "Analysis/07-分布式与微服务/04-软件架构理论体系/07-工作流架构理论.md": """
---

## 形式化定义

### 定义 1.1 (工作流的形式化五元组)

**工作流**（Workflow）的形式化定义为五元组：

$$\\mathcal{W} = \\langle A, T, D, R, C \\rangle$$

其中：
- $A = \\{a_1, a_2, \\dots, a_n\\}$ 是**活动集合**（Activity Set）
- $T \\subseteq A \\times A$ 是**转移关系**（Transition Relation），定义流程的偏序执行结构
- $D = \\{d_1, d_2, \\dots\\}$ 是**数据对象集**
- $R = \\{r_1, r_2, \\dots\\}$ 是**资源集合**（角色、人员、服务）
- $C: A \\times R \\times D \\rightarrow \\{0, 1\\}$ 是**约束函数**，编码业务规则

### 定义 2.1 (工作流网的 Petri 网结构)

**工作流网**（WF-net）是一个特殊 Petri 网：

$$\\mathcal{WF} = \\langle P, T_{wf}, F, i, o \\rangle$$

满足：
- $\\exists! i \\in P, \\; \\bullet i = \\emptyset$（唯一源库所，无输入弧）
- $\\exists! o \\in P, \\; o \\bullet = \\emptyset$（唯一汇库所，无输出弧）
- 添加回归弧 $(o, t_{ret}, i)$ 后，网图强连通

其中 $\\bullet x = \\{y \\mid (y, x) \\in F\\}$ 为 $x$ 的前集，$x \\bullet = \\{y \\mid (x, y) \\in F\\}$ 为 $x$ 的后集。

### 定义 2.2 (健全性的形式化)

**健全性**（Soundness）是 WF-net 的核心正确性属性（van der Aalst, 1998）：

$$\\text{Sound}(\\mathcal{WF}) \\iff \\text{Option-to-Complete} \\land \\text{Proper-Completion} \\land \\text{No-Dead-Transitions}$$

其中：
1. **可完成性**：$\\forall M \\in Reach(\\mathcal{WF}, M_0), \\; \\exists M', \\; M \\xrightarrow{*} M' \\land M'(o) \\geq 1$
2. **正确完成**：$\\forall M \\in Reach(\\mathcal{WF}, M_0), \\; M(o) \\geq 1 \\Rightarrow M = \\{o\\}$
3. **无死变迁**：$\\forall t \\in T_{wf}, \\; \\exists M, M', \\; M_0 \\xrightarrow{*} M \\xrightarrow{t} M'$

### 定义 3.1 (工作流模式的组合语义)

**工作流模式**（Workflow Patterns）通过**进程代数组合子**定义：

$$\\text{Pattern} ::= seq(\\mathcal{W}_1, \\mathcal{W}_2) \\mid par(\\mathcal{W}_1, \\mathcal{W}_2) \\mid choice(\\mathcal{W}_1, \\mathcal{W}_2) \\mid loop(\\mathcal{W}, cond) \\mid merge_{sync}(\\mathcal{W}_1, \\mathcal{W}_2) \\mid merge_{xor}(\\mathcal{W}_1, \\mathcal{W}_2)$$

各组合子的语义：
- $seq(\\mathcal{W}_1, \\mathcal{W}_2)$：串行组合，$\\mathcal{W}_1$ 完成后启动 $\\mathcal{W}_2$
- $par(\\mathcal{W}_1, \\mathcal{W}_2)$：并行分支，AND-split / AND-join
- $choice(\\mathcal{W}_1, \\mathcal{W}_2)$：互斥选择，XOR-split / XOR-join
- $loop(\\mathcal{W}, cond)$：循环，$cond = \\text{true}$ 时重复执行 $\\mathcal{W}$

> **来源**：van der Aalst, W. M. P. (1998). The Application of Petri Nets to Workflow Management. *Journal of Circuits, Systems and Computers*, 8(1), 21–66; van der Aalst, W. M. P., et al. (2003). Workflow Patterns. *Distributed and Parallel Databases*, 14(1), 5–51.

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

print(f"\nTotal enhanced in batch 3: {count}")
