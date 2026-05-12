import os
import re

FORMAL_DEFS = {
    "Analysis/01-哲学基础理论/05-信息哲学基础.md": """
---

## 形式化定义

### 定义 2.2 (语义信息结构)

**语义信息**（Semantic Information）是一个结构化三元组，形式化定义为：

$$\\mathcal{I}_S = \\langle D, S, V \\rangle$$

其中：
- $D$ 是**数据域**（Data Domain），即符号序列的集合 $D \\subseteq \\Sigma^*$
- $S$ 是**语义解释函数**（Semantic Interpretation），$S: D \\rightarrow M$，将数据映射到意义空间 $M$
- $V$ 是**真值条件**（Veridicality Condition），$V: M \\rightarrow \\{0, 1\\}$，表征信息是否为真

### 定义 2.3 (语义熵)

基于 Floridi 的语义信息论，**语义熵**度量语义空间中的不确定性，形式化定义为：

$$H_S(\\mathcal{I}_S) = -\\sum_{m \\in M} p(S^{-1}(m)) \\log p(S^{-1}(m))$$

其中 $S^{-1}(m)$ 表示意义 $m$ 对应的所有数据实例的逆像集。

### 定义 2.4 (MSMFIT 信息本体)

MSMFIT 四要素构成最小语义信息本体结构：

$$\\mathcal{O}_{MSMFIT} = \\langle E, R, V, C \\rangle$$

其中：
- $E$ 为实体集合（Entity Set），$E = \\{e_1, e_2, \\dots, e_n\\}$
- $R \\subseteq E \\times E$ 为实体间关系集合
- $V: E \\times \\mathbb{T} \\rightarrow \\mathcal{S}$ 为事件函数，$\\mathbb{T}$ 为时间域，$\\mathcal{S}$ 为状态空间
- $C = \\langle C_{lang}, C_{dom} \\rangle$ 为上下文解释框架，包含语言上下文与领域上下文

> **来源**：Floridi, L. (2011). *The Philosophy of Information*. Oxford University Press; Shannon, C. E. (1948). A Mathematical Theory of Communication. *Bell System Technical Journal*, 27(3), 379–423.

""",
    
    "Analysis/01-哲学基础理论/06-计算哲学基础.md": """
---

## 形式化定义

### 定义 2.1 (计算的形式化)

遵循图灵论题（Church-Turing Thesis），**计算**是一个可有效执行的函数变换过程，形式化定义为：

$$\\mathcal{C} = \\langle Q, \\Sigma, \\Gamma, \\delta, q_0, F \\rangle$$

其中：
- $Q$ 是**状态有限集**（Finite Set of States）
- $\\Sigma$ 是**输入字母表**（Input Alphabet）
- $\\Gamma$ 是**带字母表**（Tape Alphabet），满足 $\\Sigma \\subseteq \\Gamma$
- $\\delta: Q \\times \\Gamma \\rightarrow Q \\times \\Gamma \\times \\{L, R\\}$ 是**转移函数**（Transition Function）
- $q_0 \\in Q$ 是**初始状态**
- $F \\subseteq Q$ 是**接受状态集**

### 定义 2.2 (程序作为可执行规范)

在计算哲学框架下，**程序**是形式规范与物理实现之间的中介结构：

$$\\mathcal{P} = \\langle \\mathcal{S}, \\mathcal{I}, \\mathcal{V} \\rangle$$

其中：
- $\\mathcal{S}$ 是**规范层**（Specification Layer），通常为逻辑公式 $\\phi \\in \\mathcal{L}$，$\\mathcal{L}$ 为某规范语言
- $\\mathcal{I}$ 是**实现层**（Implementation Layer），即具体代码 $C$ 在抽象机器 $M$ 上的运行实例
- $\\mathcal{V}: C \\times \\phi \\rightarrow \\{0, 1\\}$ 是**验证关系**（Verification Relation），判定实现是否满足规范

### 定义 2.3 (语义-实现同构)

**语义驱动计算**的核心是业务语义世界 $\\mathcal{W}_{biz}$ 与技术实现世界 $\\mathcal{W}_{tech}$ 之间的结构同构：

$$\\Phi: \\mathcal{W}_{biz} \\xrightarrow{\\cong} \\mathcal{W}_{tech}$$

其中 $\\Phi$ 为双射（bijection），保持操作结构与约束关系：

$$\\forall o_1, o_2 \\in \\mathcal{W}_{biz}, \\; R_{biz}(o_1, o_2) \\iff R_{tech}(\\Phi(o_1), \\Phi(o_2))$$

> **来源**：Turing, A. M. (1936). On Computable Numbers. *Proceedings of the London Mathematical Society*, 42(2), 230–265; Rapaport, W. J. (2023). *Philosophy of Computer Science*. Springer.

""",
    
    "Analysis/01-理论体系/13-理论映射与证明框架.md": """
---

## 形式化定义

### 定义 2.1 (理论映射函子)

理论映射可形式化为**范畴论中的函子**（Functor）：

$$\\mathcal{F}: \\mathbf{Cat}_{USTS} \\rightarrow \\mathbf{Cat}_{UMS}$$

其中：
- $\\mathbf{Cat}_{USTS}$ 是 USTS 理论范畴，其对象为状态转换系统 $\\mathcal{U} = \\langle S, E, R, M, I, F, L \\rangle$，态射为模拟关系（simulation relation）
- $\\mathbf{Cat}_{UMS}$ 是 UMS 理论范畴，其对象为模块化系统 $\\mathcal{M} = \\langle C, I_c, M_s, CT \\rangle$，态射为接口兼容关系
- $\\mathcal{F}$ 满足函子公理：
  1. **对象映射**：$\\mathcal{F}(\\mathcal{U}) = \\mathcal{M}$
  2. **态射映射**：$\\mathcal{F}(f: \\mathcal{U}_1 \\rightarrow \\mathcal{U}_2) = \\mathcal{F}(f): \\mathcal{F}(\\mathcal{U}_1) \\rightarrow \\mathcal{F}(\\mathcal{U}_2)$
  3. **复合保持**：$\\mathcal{F}(g \\circ f) = \\mathcal{F}(g) \\circ \\mathcal{F}(f)$

### 定义 7.1 (映射正确性)

映射 $\\mathcal{F}$ 的**语法正确性**定义为：

$$\\text{Syntax}(\\mathcal{F}) \\iff \\forall s \\in S, \\; \\exists! c \\in C, \\; comp(s) = c$$

**语义一致性**定义为行为等价：

$$\\text{Semantics}(\\mathcal{F}) \\iff \\forall s \\in S, \\; Behavior_{USTS}(s) \\equiv Behavior_{UMS}(comp(s))$$

**结构完整性**定义为满射覆盖：

$$\\text{Structure}(\\mathcal{F}) \\iff \\forall c \\in C, \\; \\exists s \\in S, \\; comp(s) = c \\lor c \\in C_{infra}$$

其中 $C_{infra}$ 为映射过程引入的基础设施组件集合。

### 定义 8.1 (行为双模拟)

映射前后系统的**行为等价性**通过双模拟（Bisimulation）严格定义：

$$\\mathcal{B} \\subseteq S \\times C \\quad \\text{s.t.} \\quad \\forall (s, c) \\in \\mathcal{B}:$$

- 若 $s \\xrightarrow{e} s'$，则 $\\exists c \\xrightarrow{m} c'$，满足 $(s', c') \\in \\mathcal{B}$ 且 $msg(e) = m$
- 若 $c \\xrightarrow{m} c'$，则 $\\exists s \\xrightarrow{e} s'$，满足 $(s', c') \\in \\mathcal{B}$ 且 $msg(e) = m$

> **来源**：Mac Lane, S. (1998). *Categories for the Working Mathematician* (2nd ed.). Springer; Milner, R. (1989). *Communication and Concurrency*. Prentice Hall.

""",
    
    "Analysis/06-形式模型理论体系/07-形式化方法理论.md": """
---

## 形式化定义

### 定义 2.1 (形式规约的逻辑结构)

**形式规约**（Formal Specification）是一个良构的逻辑公式，形式化定义为：

$$\\mathcal{SPEC} = \\langle \\mathcal{L}, \\mathcal{V}, \\Phi, \\mathcal{M} \\rangle$$

其中：
- $\\mathcal{L} = \\langle \\mathcal{F}, \\mathcal{P}, \\mathcal{C}, \\mathcal{V}_{ar} \\rangle$ 是**规范语言**的签名，包含函数符号集 $\\mathcal{F}$、谓词符号集 $\\mathcal{P}$、常量集 $\\mathcal{C}$ 与变量集 $\\mathcal{V}_{ar}$
- $\\mathcal{V}$ 是**值域**（Value Domain），通常为某数学结构如 $\\mathbb{N}$, $\\mathbb{B}$, 或自定义代数结构
- $\\Phi \\in Form(\\mathcal{L})$ 是**规约公式**，$Form(\\mathcal{L})$ 表示语言 $\\mathcal{L}$ 上的良构公式集
- $\\mathcal{M} = \\langle D, \\mathcal{I} \\rangle$ 是**语义模型**，$D$ 为论域，$\\mathcal{I}$ 为解释函数

### 定义 2.2 (形式验证的判定关系)

**形式验证**（Formal Verification）是模型与规约之间的逻辑蕴涵关系：

$$\\mathcal{M} \\models \\Phi$$

即语义模型 $\\mathcal{M}$ 满足规约公式 $\\Phi$。验证过程本质上是构造一个**证明** $\\Pi$：

$$\\Pi: \\vdash \\mathcal{M} \\models \\Phi$$

主要验证技术对应不同的证明策略：
- **模型检测**（Model Checking）：$\\mathcal{M} \\models \\Phi$ 通过状态空间穷尽搜索判定，要求 $\\mathcal{M}$ 为有限状态系统
- **定理证明**（Theorem Proving）：$\\Gamma \\vdash \\Phi$ 通过公理与推理规则构造演绎证明
- **抽象解释**（Abstract Interpretation）：$\\mathcal{M}^\\sharp \\models \\Phi^\\sharp$，在抽象域 $D^\\sharp$ 上进行近似验证

### 定义 2.3 (精化关系)

形式化开发中的**精化**（Refinement）是一个保持语义的预序关系：

$$\\mathcal{SPEC}_{high} \\sqsubseteq \\mathcal{SPEC}_{low} \\iff \\forall \\mathcal{M}, \\; \\mathcal{M} \\models \\mathcal{SPEC}_{low} \\Rightarrow \\mathcal{M} \\models \\mathcal{SPEC}_{high}$$

> **来源**：Hoare, C. A. R. (1969). An Axiomatic Basis for Computer Programming. *Communications of the ACM*, 12(10), 576–580; Clarke, E. M., Grumberg, O., & Peled, D. A. (1999). *Model Checking*. MIT Press.

""",
    
    "Analysis/06-形式模型理论体系/09-系统建模理论.md": """
---

## 形式化定义

### 定义 2.1 (系统模型的标记迁移系统)

**系统模型**（System Model）是一个标记迁移系统（Labelled Transition System, LTS），形式化定义为：

$$\\mathcal{M} = \\langle S, Act, \\rightarrow, s_0 \\rangle$$

其中：
- $S$ 是**状态集**（State Set），系统所有可能状态的集合
- $Act$ 是**动作集**（Action Set），系统可执行的原子操作标签集合
- $\\rightarrow \\subseteq S \\times Act \\times S$ 是**迁移关系**（Transition Relation），$(s, a, s') \\in \\rightarrow$ 表示系统在状态 $s$ 执行动作 $a$ 后进入状态 $s'$
- $s_0 \\in S$ 是**初始状态**

### 定义 2.2 (模型精化)

模型间的**精化关系**（Refinement） $R \\subseteq S_1 \\times S_2$ 满足：

$$\\forall (s_1, s_2) \\in R, \\; \\forall a \\in Act, \\; s_1 \\xrightarrow{a} s_1' \\Rightarrow \\exists s_2', \\; s_2 \\xrightarrow{a} s_2' \\land (s_1', s_2') \\in R$$

若 $R$ 为全关系，则称 $\\mathcal{M}_2$ 是 $\\mathcal{M}_1$ 的精化，记作 $\\mathcal{M}_1 \\sqsubseteq_R \\mathcal{M}_2$。

### 定义 2.3 (模型转换的保持性)

**模型转换**（Model Transformation）$T: \\mathcal{M}_{src} \\rightarrow \\mathcal{M}_{tgt}$ 需满足性质保持：

$$\\forall \\phi \\in \\mathcal{P}, \\; \\mathcal{M}_{src} \\models \\phi \\Rightarrow \\mathcal{M}_{tgt} \\models T(\\phi)$$

其中 $\\mathcal{P}$ 为待保持的性质集合，$T(\\phi)$ 为性质在目标模型上的对应表达。

### 定义 3.1 (抽象层次)

**抽象层次**（Abstraction Level）由观测等价类诱导：

$$\\mathcal{A}_i = \\langle S_i, Act_i, \\rightarrow_i, s_{0,i} \\rangle, \\quad S_i = S / \\sim_i$$

其中 $\\sim_i$ 为第 $i$ 层抽象等价关系，满足 $\\sim_{i+1} \\subseteq \\sim_i$（越高层抽象越粗粒度）。

> **来源**：Baier, C., & Katoen, J. P. (2008). *Principles of Model Checking*. MIT Press; Cousot, P., & Cousot, R. (1977). Abstract Interpretation: A Unified Lattice Model for Static Analysis of Programs. *POPL '77*, 238–252.

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

print(f"\nTotal enhanced in batch 1: {count}")
