# RSC 与 Edge 计算：流式传输与网络边界

> **来源映射**: View/03.md §1.2, View/05.md §5.1
> **权威参考**: React Server Components RFC, Next.js App Router

---

## 一、核心概念

```text
RSC + Edge:
  拓扑: Client ←(RSC)→ Edge ←(API)→ Origin ←(SQL)→ DB
  延迟: L_total = L_edge + L_rsc_stream + L_cc
  特征: Edge 执行 RSC, 流式传输到客户端
  问题: 网络边界成为编程模型的一部分 (定理 T2)
```

---

## 二、待完善内容

- [ ] RSC Payload 的序列化协议
- [ ] Edge 函数与 Serverless 函数的边界
