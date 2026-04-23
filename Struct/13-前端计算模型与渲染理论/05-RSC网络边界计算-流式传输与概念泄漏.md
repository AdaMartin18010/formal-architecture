# RSC 网络边界计算：流式传输与概念泄漏

> **来源映射**: View/03.md §1.2, View/04.md §6.2, View/05.md §1.2
> **权威参考**: React Server Components RFC, Next.js App Router 文档

---

## 一、核心概念定义

### 1.1 RSC 的形式化定义

```text
定义 (RSC - React Server Components):
  Server Component (SC): 在服务端执行, 无客户端生命周期
  Client Component (CC): 在客户端执行, 有完整生命周期

  通信: SC 通过 RSC Payload (流式序列化数据) 向 CC 传输渲染结果

  形式化争议:
    同一文件扩展名 (.tsx) 承载两种语义
    导入语句触发隐式网络边界切换
    类型系统无法表达 "Server-only" vs "Client-capable"
```

### 1.2 定理 T2：RSC 破坏组合封闭性

```text
前提: A7 要求 ∀c₁,c₂ ∈ Component, c₁ ∘ c₂ ∈ Component
      (组件组合必须封闭)

RSC 定义:
  Server Component (SC): 在服务端执行, 无客户端生命周期
  Client Component (CC): 在客户端执行, 有完整生命周期

考察组合 c_SC ∘ c_CC:
  情况 1: c_SC 导入 c_CC
    - 服务端渲染 c_SC 时, 遇到 c_CC 的引用
    - c_CC 不能在服务端完整执行 (需要浏览器 API)
    - 编译器需插入 "Client Boundary" 标记
    - 实际输出: RSC Payload + 客户端 JS 引用

  情况 2: c_CC 导入 c_SC
    - 客户端渲染 c_CC 时, 导入 c_SC
    - c_SC 已在服务端执行完毕, 结果为序列化数据
    - 客户端直接反序列化使用

问题:
  c_SC ∘ c_CC 的语义取决于执行环境 (Server vs Client)
  同一组合在不同环境产生不同计算结果
  即: c₁ ∘ c₂ ∉ Component (单一语义空间)

  更严格地, 设 Component 为代数结构 ⟨C, ∘⟩
  RSC 将其分裂为 ⟨C_server, ∘_s⟩ 和 ⟨C_client, ∘_c⟩
  且 ∘_s ≠ ∘_c

∴ RSC 破坏了 A7 的封闭性公理    ∎

推论: RSC 不是组件代数上的同态映射, 而是异构系统的粘合层
```

---

## 二、权威引用

> **React Team** (RSC 设计文档):
> "Server Components allow developers to build apps that span the server and client."

> **社区批判** (常见观点):
> "RSC 制造了'两个 React'，生态割裂，fetch 行为被魔改，调试困难。"

---

## 三、待完善内容

- [ ] RSC Payload 的序列化协议分析
- [ ] Server/Client 边界的类型系统设计挑战
- [ ] RSC 与 GraphQL 的对比分析
