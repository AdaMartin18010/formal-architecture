# UPPAAL：实时系统模型检测

> **定位**：UPPAAL是实时系统形式化验证的工业级工具，基于Timed Automata理论。它将"系统是否在deadline内响应"这样的实时属性，从手工分析提升到自动验证。
>
> **核心命题**：实时系统的Bug（错过deadline）不是功能错误，而是时序错误——传统测试难以发现，但模型检测可以穷举所有时序可能。

---

## 一、思维导图：UPPAAL核心概念

```text
UPPAAL
│
├─【输入：Timed Automata Network】
│   ├─ 多个Timed Automata并行组合
│   ├─ 同步通道（Channels）
│   ├─ 共享变量
│   └─ 时钟约束（Clock Constraints）
│
├─【验证：TCTL子集】
│   ├─ A[] φ：所有路径所有状态满足φ
│   ├─ E<> φ：存在路径某状态满足φ
│   ├─ A<> φ：所有路径最终满足φ
│   └─ 带时钟约束：A[] x < 10（始终时钟x<10）
│
├─【核心能力】
│   ├─ 可达性分析
│   ├─ 死锁检测
│   ├─ Liveness验证
│   └─ 最短时间/成本分析
│
└─【应用领域】
    ├─ 实时操作系统调度
    ├─ 通信协议（CAN, FlexRay）
    ├─ 硬件电路（cache coherence）
    └─ 工作流验证
```

---

## 二、Timed Automata的形式化

```
Timed Automaton定义为：TA = (L, l₀, C, A, E, I)

  L = 有限位置集合
  l₀ ∈ L = 初始位置
  C = 有限时钟变量集合
  A = 动作集合（含同步通道）
  E ⊆ L × G(C) × A × 2^C × L = 边集合
    G(C) = 时钟约束（守卫条件）
    2^C = 时钟重置集合
  I: L → G(C) = 位置不变量

语义：
  - 延迟转换：时钟统一递增（时间流逝）
  - 离散转换：沿边移动，满足守卫条件，重置时钟
  - 同步：两个automaton通过匹配通道同步执行

示例：简单信号灯

  位置：Green, Yellow, Red
  时钟：x

  Green --x >= 30, x=0--> Yellow
  Yellow --x >= 5, x=0--> Red
  Red --x >= 25, x=0--> Green

  不变量：
    Green: x <= 30
    Yellow: x <= 5
    Red: x <= 25
```

---

## 三、UPPAAL查询语言

```
UPPAAL验证查询：

  安全性（Safety）：
    A[] not deadlock
      = "系统永远不会死锁"

    A[] (Train1.Critical + Train2.Critical <= 1)
      = "两个火车永远不会同时在临界区"

  可达性（Reachability）：
    E<> Process.Error
      = "存在一条路径到达错误状态"

    E<> (x >= 100 && y < 50)
      = "时钟x>=100且y<50的状态可达"

  Liveness：
    A<> Process.Done
      = "所有路径最终都会到达Done状态"

    Process.Request --> Process.Response
      = "若请求，则最终会有响应"

  带时间约束：
    A[] (Request --> Response within 10)
      = "所有请求的响应时间 ≤ 10个时间单位"
```

---

## 四、UPPAAL模型检测过程

```
1. 建模
   - 将系统分解为并行的Timed Automata
   - 定义时钟、变量、通道
   - 编写守卫条件和不变量

2. 验证
   - 编写TCTL查询
   - UPPAAL引擎执行符号状态空间搜索
   - 结果：SAT（满足）/ UNSAT（不满足）+ 反例轨迹

3. 分析
   - 若验证失败：分析反例轨迹，修复模型或设计
   - 若验证通过：增加查询覆盖度，考虑更复杂场景

状态空间优化：
  - 抽象：忽略无关变量
  - 对称性：利用进程对称性约减
  - 边界：限制时钟最大值（整数化）
```

---

## 五、概念定义与属性关系

| 概念 | 定义 | 属性 | 示例 | 反例 |
|------|------|------|------|------|
| **Timed Automata** | 带时钟变量的有限自动机 | 可建模实时约束、可判定 | UPPAAL输入模型 | 普通有限自动机 |
| **UPPAAL** | 实时系统模型检测工具 | 符号搜索、工业级、可反例 | 火车交叉验证 | 非实时系统验证 |
| **时钟约束** | 时钟变量上的线性不等式 | 可判定、支持区域图 | x < 10, x == y | 非线性约束 |
| **TCTL** | 实时计算树逻辑 | 可表达时间属性 | A[] x < 10 | CTL（无时钟） |
| **反例轨迹** | 违反属性的具体时序路径 | 可调试、有价值 | UPPAAL的XML轨迹 | 无反例（属性满足） |

---

## 六、交叉引用

- → [07-总览](../00-总览-从构造到归纳的范式转移.md)
- → [07/01-TLA+](01-TLA+-时序逻辑规范与系统验证.md)
- → [07/03-模型检测](03-模型检测-UPPAAL与状态空间爆炸问题.md)
- → [11/01-Petri网](../11-工作流与并发系统分析/01-Petri网-并发系统的形式化建模.md)

---

## 七、参考文献

| 作者 | 标题 | 出处 | 年份 |
|------|------|------|------|
| UPPAAL团队 | UPPAAL工具与文档 | uppaal.org | 持续更新 |
| Alur, Dill | "A Theory of Timed Automata" | *Theoretical Computer Science* | 1994 |
| Bengtsson, Yi | "Timed Automata: Semantics, Algorithms and Tools" | *Lectures on Concurrency and Petri Nets* | 2004 |
| Behrmann et al. | "UPPAAL 4.0" | *QEST* | 2006 |

---

*文件创建日期：2026-04-23*
*状态：已完成*
