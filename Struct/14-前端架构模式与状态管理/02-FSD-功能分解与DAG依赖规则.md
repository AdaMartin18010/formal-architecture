# FSD：功能分解与 DAG 依赖规则

> **来源映射**: View/03.md §2.2, View/04.md §6.4
> **权威参考**: Feature-Sliced Design 官方文档

---

## 一、核心概念定义

### 1.1 FSD 的层次结构

```text
FSD (Feature-Sliced Design):
  分解维度: 业务功能 (Business Capability)

  Shared ──► Entities ──► Features ──► Widgets ──► Pages ──► App
    │           │            │           │          │
    ▼           ▼            ▼           ▼          ▼
  通用工具      业务实体       业务功能      页面区块      页面
  UI Kit       User         Auth        商品卡片      商品页
  API Client   Order        Checkout     评论列表      订单页

  本体论假设: UI 是业务能力的投影
  优势: 业务逻辑内聚, 团队按功能域自治
  约束: 导入规则 DAG, 禁止跨层循环依赖

  导入规则:
    - 上层模块只能导入下层模块
    - 同层切片禁止相互导入
    - 每层内部通过 Public API (index.ts) 暴露接口
```

### 1.2 FSD 的 AI 适配性原理

```text
定理 T8: AI 代码生成的正确性与上下文边界显式度正相关

证明概要:
  设 AI 模型为函数 G: Context → Code
  设正确性度量 corr: Code → [0,1]

  假设: corr(G(C)) ∝ 1/|C|_complexity

  FSD 通过分层 (Layers) 和切片 (Slices) 限制 |C|:
    |C_FSD| = |Shared| + |Entity| + |Feature| + ...
    每层有明确的导入规则, 限制跨层依赖

  对比无架构项目:
    |C_chaos| = |WholeProject| (全局上下文)

  ∵ |C_FSD| ≪ |C_chaos|
  ∴ corr(G(C_FSD)) > corr(G(C_chaos))    ∎
```

---

## 二、权威引用

> **FSD 社区**:
> "Feature-Sliced Design is an architectural methodology for frontend projects."

---

## 三、待完善内容

- [ ] FSD 的导入规则 ESLint 插件实现
- [ ] FSD 与 DDD 战略设计的映射关系
- [ ] FSD 在大型团队中的实际案例
