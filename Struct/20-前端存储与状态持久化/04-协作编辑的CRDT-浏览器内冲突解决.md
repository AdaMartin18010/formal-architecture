# 协作编辑的 CRDT：浏览器内冲突解决

> **来源映射**: View/05.md §4.2
> **权威参考**: Yjs 文档, CRDT 论文 (Shapiro et al.)

---

## 一、核心概念

```text
CRDT 在前端的应用:
  Yjs: 浏览器内的 CRDT 实现
  适用场景: 协作编辑、共享白板、实时表单

  一致性: 最终一致 + 冲突自动解决
  分区容错: P2P 同步 (WebRTC / WebSocket)
```

---

## 二、待完善内容

- [ ] Yjs 的文档更新传播机制
- [ ] CRDT 与 Operational Transformation 的对比
