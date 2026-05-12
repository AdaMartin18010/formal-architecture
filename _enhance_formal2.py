import os
import re

FORMAL_DEFS = {
    "Analysis/06-软件架构理论体系/00-软件架构理论体系总论.md": """
---

## 形式化定义

### 定义 4.3 (通用组件框架的代数结构)

**通用组件框架**（Universal Component Framework）是一个代数结构，形式化定义为：

$$\\mathcal{F} = \\langle C, R, I, \\oplus, \\otimes \\rangle$$

其中：
- $C$ 是**组件集合**（Component Set），每个组件 $c \\in C$ 满足通用属性：
  - $\\forall c \\in C, \\; \\text{Reusable}(c) = \\text{true}$
  - $\\forall c \\in C, \\; \\text{Configurable}(c) = \\text{true}$
  - $\\forall c \\in C, \\; \\text{Testable}(c) = \\text{true}$
- $R \\subseteq C \\times C$ 是**组件间关系集**
- $I = \\{i_c \\mid c \\in C\\}$ 是**接口集合**
- $\\oplus: \\mathcal{F} \\times \\mathcal{F} \\rightarrow \\mathcal{F}$ 是**框架组合运算符**：

$$\\mathcal{F}_1 \\oplus \\mathcal{F}_2 = \\langle C_1 \\cup C_2, R_1 \\cup R_2, I_1 \\cup I_2, \\oplus, \\otimes \\rangle$$

- $\\otimes: C \\times C \\rightarrow C$ 是**组件兼容积**

### 定义 4.4 (标准公共模型的不动点)

**标准公共模型** $\\mathcal{M}^*$ 是以下递归定义的不动点：

$$\\mathcal{M}_0 = \\emptyset$$
$$\\mathcal{M}_{n+1} = \\mathcal{M}_n \\cup \\{c \\mid c \\in C_{univ} \\land \\text{Compatible}(c, \\mathcal{M}_n)\\}$$

$$\\mathcal{M}^* = \\lim_{n \\rightarrow \\infty} \\mathcal{M}_n$$

其中 $C_{univ}$ 为通用组件全集。该递归过程满足：
- **单调性**：$\\mathcal{M}_n \\subseteq \\mathcal{M}_{n+1}$
- **收敛性**：因 $C_{univ}$ 有限，$\\exists N, \\; \\forall n \\geq N, \\; \\mathcal{M}_n = \\mathcal{M}^*$

### 定义 4.5 (框架组合定理)

**定理**（框架组合性）：通用组件框架的组合运算 $\\oplus$ 保持通用组件属性。

$$\\forall \\mathcal{F}_1, \\mathcal{F}_2, \\; \\text{Universal}(\\mathcal{F}_1) \\land \\text{Universal}(\\mathcal{F}_2) \\Rightarrow \\text{Universal}(\\mathcal{F}_1 \\oplus \\mathcal{F}_2)$$

**证明概要**：由 $C_1, C_2$ 均为通用组件集，$C_1 \\cup C_2$ 中每个元素仍满足可重用、可配置、可测试属性，故组合框架有效。

> **来源**：Shaw, M., & Garlan, D. (1996). *Software Architecture: Perspectives on an Emerging Discipline*. Prentice Hall; Buschmann, F., et al. (1996). *Pattern-Oriented Software Architecture: A System of Patterns*. Wiley.

""",
    
    "Analysis/06-软件架构理论体系/01-架构模式理论.md": """
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
    
    "Analysis/06-软件架构理论体系/03-设计模式理论.md": """
---

## 形式化定义

### 定义 3.2 (设计模式的重写系统)

**设计模式**（Design Pattern）可形式化为一个**项重写系统**（Term Rewriting System）：

$$\\mathcal{DP} = \\langle \\mathcal{T}, \\mathcal{R}, \\mathcal{G}, \\mathcal{N} \\rangle$$

其中：
- $\\mathcal{T}$ 是**项代数**（Term Algebra），由类型签名 $\\Sigma = \\langle S, F \\rangle$ 生成，$S$ 为排序集，$F$ 为函数符号集
- $\\mathcal{R} \\subseteq \\mathcal{T} \\times \\mathcal{T}$ 是**重写规则集**，每条规则 $l \\rightarrow r$ 表示从问题结构 $l$ 到解结构 $r$ 的转换
- $\\mathcal{G}: \\mathcal{T} \\rightarrow \\{0, 1\\}$ 是**守卫条件**（Guard Condition），判定模式是否适用
- $\\mathcal{N}: \\mathcal{R} \\rightarrow \\mathbb{N}$ 是**归约次数上界**，保证重写终止

### 定义 4.1.1 (单例模式的唯一性公理)

**单例模式**（Singleton Pattern）通过存在唯一性公理形式化：

$$\\exists! x \\in \\mathcal{O}, \\; \\text{InstanceOf}(x, C_{singleton})$$

其中 $\\mathcal{O}$ 为对象域，$C_{singleton}$ 为单例类。其访问函数 $getInstance: \\textbf{1} \\rightarrow \\mathcal{O}$ 满足：

$$\\forall t_1, t_2, \\; getInstance()_{t_1} = getInstance()_{t_2}$$

即所有时刻调用返回同一对象引用。

### 定义 4.1.2 (工厂模式的类型构造子)

**工厂模式**（Factory Pattern）定义了一个**类型构造子**（Type Constructor）：

$$Factory: \\prod_{t \\in T} (Args_t \\rightarrow Obj_t)$$

其中 $T$ 为产品类型索引集，$Args_t$ 为类型 $t$ 的构造参数集，$Obj_t$ 为类型 $t$ 的对象集。工厂方法满足：

$$\\forall t \\in T, \\; \\forall args \\in Args_t, \\; Factory(t)(args) \\in Obj_t$$

### 定义 5.1 (结构型模式的组合代数)

**结构型模式**（Structural Patterns）基于**组合代数**（Composition Algebra）：

$$\\mathcal{SA} = \\langle O, \\bullet, \\iota, \\pi \\rangle$$

其中：
- $O$ 为对象集合
- $\\bullet: O \\times O \\rightarrow O$ 为**组合运算**（如适配器封装、装饰器包装）
- $\\iota: O \\rightarrow O$ 为**恒等嵌入**
- $\\pi: O \\rightarrow 2^O$ 为**投影分解**（如桥接模式的维度分离）

> **来源**：Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley; Pierce, B. C. (2002). *Types and Programming Languages*. MIT Press.

""",
    
    "Analysis/06-软件架构理论体系/05-微服务架构理论.md": """
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
    
    "Analysis/06-软件架构理论体系/06-云原生架构理论.md": """
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

print(f"\nTotal enhanced in batch 2: {count}")
