# 前端并发模型：CSP / Actor / STM 映射

> **来源映射**: View/05.md §3.1
> **权威参考**: Hoare CSP (1978), Hewitt Actor (1973), Shavit/Touitou STM

---

## 一、核心概念定义

### 1.1 前端并发模型的形式化分类

| 并发模型 | 形式化基础 | 前端实现 | 适用场景 |
|---------|-----------|---------|---------|
| **CSP** (通信顺序) | Hoare 进程代数 | Web Workers + postMessage | 计算密集型任务 |
| **Actor** | Hewitt 演员模型 | Service Worker + event.waitUntil | 后台同步, 推送通知 |
| **STM** (软件事务) | Shavit/Touitou | useTransition / startTransition | UI 状态的原子更新 |
| **数据并行** | SIMD / SPMD | WebGPU Compute Shader | 矩阵运算, AI 推理 |
| **结构化并发** | async/await | AbortController | 请求取消, 竞态处理 |

### 1.2 React Concurrent 的半可判定性分析

```text
定理 T5: React Concurrent 的优先级调度是优先级翻转的启发式解

证明概要:
  设任务集合 T = {t₁, t₂, ..., tₙ}, 优先级 p: T → ℕ
  React 使用 Lane 模型: Lane = 2^k, k ∈ [0, 31]

  优先级翻转场景:
    t_high: 用户输入 (TransitionPriority = 1)
    t_low: 数据获取 (DefaultPriority = 16)
    t_lock: 渲染锁 (由 t_low 持有, 因为 Suspense 边界)

  React 的解决: Time Slicing + Interruptible Reconciliation
    1. t_low 在执行过程中可被 t_high 中断
    2. t_low 的渲染状态保存为 "WorkInProgress" 树
    3. t_high 完成后, t_low 从断点恢复

  但此方案非形式化正确:
    1. 状态一致性: 中断时 Rₖ(s) 可能处于不一致状态
    2. 副作用原子性: useEffect 可能在中断边界处部分执行
    3. 内存开销: 需维护多棵 WIP 树

  ∴ React Concurrent 是优先级翻转的实用解, 非形式化解    ∎
```

---

## 二、权威引用

> **C.A.R. Hoare** (CSP 作者, 1978):
> "Communicating Sequential Processes."

> **Carl Hewitt** (Actor 模型创始人, 1973):
> "A universal, modular ACTOR formalism for artificial intelligence."

---

## 三、待完善内容

- [ ] Web Workers 与主线程的 CSP 语义映射
- [ ] Service Worker 的 Actor 模型分析
- [ ] React Lane 模型的位运算优先级调度
