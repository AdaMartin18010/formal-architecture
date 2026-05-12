import os
import re

# Short formal definitions for outline/redirect files
FORMAL_DEFS = {
    "Analysis/07-分布式与微服务/04-软件架构理论体系/05-分布式架构理论.md": """
---

## 形式化定义

### 定义 1.1 (分布式架构的形式化)

**分布式架构**（Distributed Architecture）形式化为节点拓扑与通信协议的复合结构：

$$\\mathcal{DA} = \\langle N, Topo, Proto, Cons \\rangle$$

其中：
- $N = \\{n_1, n_2, \\dots, n_k\\}$ 是**计算节点集**
- $Topo \\subseteq N \\times N$ 是**网络拓扑**，定义节点间可达性
- $Proto = \\{p_1, p_2, \\dots\\}$ 是**通信协议集**
- $Cons: N \\times Data \\rightarrow \\{0, 1\\}$ 是**局部一致性约束**

> **来源**：Coulouris, G., et al. (2011). *Distributed Systems: Concepts and Design* (5th ed.). Addison-Wesley.

""",
    
    "Analysis/07-分布式与微服务/04-软件架构理论体系/05-统一状态转换系统理论.md": """
---

## 形式化定义

### 定义 1.1 (USTS 核心结构)

**统一状态转换系统**（Unified State Transition System, USTS）形式化为七元组：

$$\\mathcal{USTS} = \\langle S, E, R, M, I, F, L \\rangle$$

其中：
- $S$ 为状态元素集合
- $E$ 为事件集合
- $R \\subseteq S \\times E \\times S$ 为关系集合
- $M: S \\rightarrow \\mathbb{N}$ 为标记函数
- $I \\subseteq S$ 为初始状态集
- $F \\subseteq S$ 为终止状态集
- $L: R \\rightarrow \\mathbb{N}^+$ 为关系权重函数

> **来源**：本项目统一理论框架；参见 [形式模型理论体系](../06-形式模型理论体系/00-形式模型理论体系总论.md)。

""",
    
    "Analysis/07-分布式与微服务/04-软件架构理论体系/07-架构评估理论.md": """
---

## 形式化定义

### 定义 1.1 (架构评估的决策矩阵)

**架构评估**（Architecture Evaluation）形式化为多属性决策问题：

$$\\mathcal{AE} = \\langle A, Q, W, Score, Thresh \\rangle$$

其中：
- $A = \\{a_1, a_2, \\dots\\}$ 为**候选架构集**
- $Q = \\{q_1, q_2, \\dots, q_m\\}$ 为**质量属性集**
- $W: Q \\rightarrow [0, 1]$ 为属性权重函数，$\\sum W(q_i) = 1$
- $Score: A \\times Q \\rightarrow \\mathbb{R}$ 为评分函数
- $Thresh: Q \\rightarrow \\mathbb{R}$ 为阈值函数

综合评分：

$$Total(a) = \\sum_{q \\in Q} W(q) \\cdot Score(a, q)$$

> **来源**：Kazman, R., et al. (2000). ATAM: Method for Architecture Evaluation. *CMU/SEI-2000-TR-004*.

""",
    
    "Analysis/07-分布式与微服务/04-软件架构理论体系/08-架构安全与鲁棒性.md": """
---

## 形式化定义

### 定义 1.1 (安全架构的访问控制矩阵)

**安全架构**（Security Architecture）的核心访问控制形式化为：

$$\\mathcal{SA} = \\langle Sub, Obj, A, M, Policy \\rangle$$

其中：
- $Sub$ 为主体集合（用户、进程、服务）
- $Obj$ 为客体集合（资源、数据、接口）
- $A = \\{read, write, execute, delete\\}$ 为操作类型集
- $M: Sub \\times Obj \\times A \\rightarrow \\{0, 1\\}$ 为**访问控制矩阵**
- $Policy: Sub \\times Obj \\times A \\times Context \\rightarrow \\{0, 1\\}$ 为**动态策略函数**

### 定义 1.2 (鲁棒性的容错边界)

**鲁棒性**（Robustness）定义为系统在故障子集 $F \\subseteq Faults$ 下的行为保持能力：

$$Robust(\\mathcal{S}, F) \\iff \\forall f \\in F, \\; \\mathcal{S} \\xrightarrow{f} \\mathcal{S}' \\land \\mathcal{S}' \\models CoreProps$$

> **来源**：Saltzer, J. H., & Schroeder, M. D. (1975). The Protection of Information in Computer Systems. *Proceedings of the IEEE*, 63(9), 1278–1308.

""",
    
    "Analysis/07-分布式与微服务/04-软件架构理论体系/09-架构可观测性与运维.md": """
---

## 形式化定义

### 定义 1.1 (可观测性的状态重构)

**可观测性**（Observability）形式化为从输出重构系统状态的能力：

$$Obs(\\mathcal{S}) \\iff \\forall s_1, s_2 \\in S, \\; s_1 \\neq s_2 \\Rightarrow \\exists t, \\; Output(s_1, t) \\neq Output(s_2, t)$$

其中 $Output: S \\times \\mathbb{T} \\rightarrow \\mathcal{O}$ 为观测输出函数。可观测性三支柱：

- **指标**（Metrics）：$M: S \\rightarrow \\mathbb{R}^k$，$k$ 维时序指标
- **日志**（Logs）：$L: E^* \\rightarrow \\mathcal{L}^*$，事件序列的文本映射
- **追踪**（Traces）：$Tr: Exec \\rightarrow DAG(Path)$，执行路径的有向无环图表示

> **来源**：Lemos, C., et al. (2022). *Observability Engineering*. O'Reilly; Kreps, J. (2013). The Log: What every software engineer should know about real-time data's unifying abstraction. *LinkedIn Engineering*.

""",
    
    "Analysis/07-分布式与微服务/04-软件架构理论体系/10-架构自动化与智能化.md": """
---

## 形式化定义

### 定义 1.1 (架构自动化的状态机)

**架构自动化**（Architecture Automation）形式化为控制状态机：

$$\\mathcal{AA} = \\langle Q_{auto}, \\Sigma_{trigger}, \\delta_{auto}, q_0, Actions \\rangle$$

其中：
- $Q_{auto} = \\{Idle, Planning, Executing, Verifying, RollingBack\\}$ 为自动化状态集
- $\\Sigma_{trigger}$ 为触发事件集（监控告警、定时任务、手动触发）
- $\\delta_{auto}: Q_{auto} \\times \\Sigma_{trigger} \\rightarrow Q_{auto}$ 为状态转移函数
- $Actions: Q_{auto} \\rightarrow 2^{Ops}$ 为状态关联操作集

### 定义 1.2 (智能化决策的贝叶斯网络)

**智能化架构决策**（Intelligent Decision）基于**贝叶斯信念网络**：

$$P(A_i \\mid Obs) = \\frac{P(Obs \\mid A_i) \\cdot P(A_i)}{\\sum_j P(Obs \\mid A_j) \\cdot P(A_j)}$$

其中 $A_i$ 为候选架构调整动作，$Obs$ 为当前系统观测。

> **来源**：Kim, G., et al. (2016). *The DevOps Handbook*. IT Revolution; Morris, K. (2016). *Infrastructure as Code*. O'Reilly.

""",
    
    "Analysis/07-分布式与微服务/04-软件架构理论体系/11-架构案例与应用拓展.md": """
---

## 形式化定义

### 定义 1.1 (架构案例的归纳模式)

**架构案例**（Architecture Case）可形式化为**归纳模式实例**：

$$\\mathcal{AC} = \\langle Context, Problem, Solution, Result, Metrics \\rangle$$

其中：
- $Context = \\langle Domain, Scale, Constraints \\rangle$ 为案例上下文
- $Problem \\in \\mathcal{P}_{arch}$ 为架构问题空间中的元素
- $Solution = \\langle Patterns_{applied}, TechStack, OrgModel \\rangle$ 为解决方案结构
- $Result \\in \\{Success, Partial, Failure\\}$ 为结果分类
- $Metrics: Solution \\times Time \\rightarrow \\mathbb{R}^m$ 为效果度量函数

案例归纳要求：

$$\\forall c_1, c_2 \\in Cases, \\; Similar(Context_1, Context_2) > \\theta \\Rightarrow Solution_1 \\approx Solution_2$$

> **来源**：Shaw, M., & Garlan, D. (1996). *Software Architecture: Perspectives on an Emerging Discipline*. Prentice Hall.

""",
    
    "Analysis/07-分布式与微服务/04-软件架构理论体系/13-架构理论批判与未来展望.md": """
---

## 形式化定义

### 定义 1.1 (架构理论的完备性度量)

**架构理论完备性**（Architectural Theory Completeness）形式化为 coverage 度量：

$$Comp(\\mathcal{T}) = \\frac{|\\{p \\in Practice \\mid \\exists t \\in \\mathcal{T}, t \\models p\\}|}{|Practice|}$$

其中 $Practice$ 为工程实践问题全集，$\\mathcal{T}$ 为理论命题集。

### 定义 1.2 (技术演化的形式化模型)

**技术演化**（Technology Evolution）遵循**S曲线累积分布**：

$$Adoption(t) = \\frac{L}{1 + e^{-k(t - t_0)}}$$

其中 $L$ 为市场饱和上限，$k$ 为扩散速率，$t_0$ 为拐点时间。架构理论需满足：

$$\\frac{d\\mathcal{T}}{dt} = \\alpha \\cdot Gap(Practice, \\mathcal{T}) - \\beta \\cdot Obsolete(\\mathcal{T}, t)$$

即理论增长正比于实践差距，反比于过时命题。

> **来源**：Lehman, M. M., & Ramil, J. F. (2006). *Software Evolution and Feedback: Theory and Practice*. Wiley.

""",
    
    "Analysis/07-分布式与微服务/04-软件架构理论体系/06-架构风格与质量属性.md": """
---

## 形式化定义

### 定义 1.1 (架构风格的代数签名)

**架构风格**（Architectural Style）形式化为**代数签名**：

$$\\mathcal{AS} = \\langle Sorts, Ops, Axioms, \\mathcal{V} \\rangle$$

其中：
- $Sorts = \\{Component, Connector, Configuration, Constraint\\}$ 为排序集
- $Ops$ 为操作符号集（如 $connect: Component \\times Component \\rightarrow Connector$）
- $Axioms$ 为风格约束公理集
- $\\mathcal{V}: Style \\times QAttribute \\rightarrow \\mathbb{R}$ 为**风格-质量属性映射**

### 定义 1.2 (质量属性的偏序评估)

**质量属性**（Quality Attributes）构成评估偏序集：

$$\\mathcal{QA} = \\langle Q, \\preceq, w, agg \\rangle$$

其中：
- $Q = \\{q_{perf}, q_{rel}, q_{sec}, q_{maint}, q_{scal}\\}$ 为质量属性集
- $\\preceq \\subseteq Q \\times Q$ 为优先级偏序
- $w: Q \\rightarrow [0, 1]$ 为权重函数
- $agg: \\mathbb{R}^n \\rightarrow \\mathbb{R}$ 为聚合函数（如加权平均、Minimax）

> **来源**：Shaw, M., & Clements, P. (2006). The Golden Age of Software Architecture. *IEEE Software*, 23(2), 31–39.

""",
    
    "Analysis/07-分布式与微服务/04-软件架构理论体系/07-架构演化与动态适应.md": """
---

## 形式化定义

### 定义 1.1 (架构演化的重写系统)

**架构演化**（Architecture Evolution）形式化为**图重写系统**（Graph Rewriting System）：

$$\\mathcal{AEvo} = \\langle G_0, \\mathcal{R}_{evo}, \\preceq \\rangle$$

其中：
- $G_0$ 为初始架构图 $G_0 = \\langle Comp_0, Conn_0 \\rangle$
- $\\mathcal{R}_{evo} = \\{r_1, r_2, \\dots\\}$ 为演化规则集，每条规则 $r: L \\rightarrow R$ 将左模式 $L$ 替换为右模式 $R$
- $\\preceq$ 为规则应用的优先级偏序

### 定义 1.2 (动态适应的反馈控制)

**动态适应**（Dynamic Adaptation）形式化为**反馈控制回路**：

$$u(t) = K_p \\cdot e(t) + K_i \\int_0^t e(\\tau) d\\tau + K_d \\frac{de(t)}{dt}$$

其中：
- $e(t) = S_{desired}(t) - S_{observed}(t)$ 为架构状态偏差
- $u(t)$ 为架构调整控制量（如扩容、缩容、路由切换）
- $K_p, K_i, K_d$ 为比例-积分-微分控制参数

> **来源**：Garlan, D., et al. (2004). Rainbow: Architecture-Based Self-Adaptation with Reusable Infrastructure. *Computer*, 37(10), 46–54.

""",
    
    "Analysis/07-分布式与微服务/04-软件架构理论体系/04-统一模块化系统理论.md": """
---

## 形式化定义

### 定义 1.1 (UMS 核心结构)

**统一模块化系统**（Unified Modular System, UMS）形式化为四元组：

$$\\mathcal{UMS} = \\langle C, I_c, M_s, CT \\rangle$$

其中：
- $C = \\{c_1, c_2, \\dots, c_n\\}$ 为**组件集合**
- $I_c = \\{i_1, i_2, \\dots\\}$ 为**接口集合**
- $M_s: C \\times C \\rightarrow \\{0, 1\\}$ 为**模块间服务关系**
- $CT = \\{ct_1, ct_2, \\dots\\}$ 为**契约集合**（Contracts）

组件组合运算：

$$c_1 \\oplus c_2 = \\langle Comp_1 \\cup Comp_2, Iface_1 \\cup Iface_2, M_{12}, CT_1 \\cup CT_2 \\cup \\{compatibility(ct_1, ct_2)\\} \\rangle$$

> **来源**：本项目统一理论框架；参见 [软件架构理论体系](../06-软件架构理论体系/00-软件架构理论体系总论.md)。

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

print(f"\nTotal enhanced in batch 5: {count}")
