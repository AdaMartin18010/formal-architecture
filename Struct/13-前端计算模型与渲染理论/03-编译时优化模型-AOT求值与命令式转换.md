# 编译时优化模型：AOT 求值与命令式转换

> **来源映射**: View/03.md §1.1, View/04.md §6.3, View/05.md §1.1
> **权威参考**: Svelte 编译器文档, React Compiler (Forget) RFC

---

## 一、核心概念定义

### 1.1 编译时响应式的形式化

```text
定义 (编译时模型): 编译器静态分析依赖关系，将声明式代码转换为命令式 DOM 操作
  compile: AST → IR → DOMOps

  Svelte 5 (Runes):
    $state → 编译器生成响应式绑定代码
    $derived → 编译器生成依赖追踪代码
    $effect → 编译器生成副作用调度代码

  React Compiler (Forget):
    自动分析 Hooks 依赖 → 插入 memoization
    不改变编程模型，不改变语义
```

### 1.2 三种优化层级的本质对比

| 层级 | 设计时 | 编译时 | 运行时 | 优化层级 | 代表 |
|------|--------|--------|--------|---------|------|
| **原生 Signals** | 显式声明信号和依赖 | 最小转换 | 信号图自动传播 | 设计时 (心智模型) | Solid, Vue 3, Angular |
| **编译时转换** | 使用 Runes ($state, $derived) | 编译器分析依赖，生成更新代码 | 直接 DOM 操作 | 编译时 (静态分析) | Svelte 5 |
| **运行时优化编译器** | 标准 Hooks (无变化) | 自动插入 memoization | 仍使用 VDOM，跳过不必要 diff | 编译时 (自动 memo) | React Compiler |

---

## 二、批判性分析

```text
批判性结论:
  React Compiler 是 "在保留 Hooks 模型的前提下, 用编译器弥补其缺陷"
  这是工程上的务实选择, 但理论上是 "补丁叠补丁"
  Signals 是 "从根本上消除需要补丁的缺陷"

类比:
  Compiler = 自动变速器 (掩盖手动换挡的复杂性)
  Signals = 电动汽车 (没有变速箱, 从根本上不同)
```

---

## 三、权威引用

> **Rich Harris** (Svelte 作者):
> "Svelte is a compiler that generates surgical DOM updates."

> **React Team** (React Compiler 公告):
> "React Compiler automatically memoizes your code — no manual useMemo or useCallback required."

---

## 四、待完善内容

- [ ] Svelte 编译器的 AST 转换详细步骤
- [ ] React Compiler 的依赖分析算法
- [ ] 编译时优化与运行时优化的帕累托前沿
