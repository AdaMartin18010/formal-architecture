# 离线优先架构：Service Worker 与后台同步

> **来源映射**: View/05.md §4.2
> **权威参考**: Service Worker Spec, BackgroundSync Spec

---

## 一、核心概念

```text
Service Worker 作为前端分布式节点:
  - 代理网络请求
  - 缓存策略: Cache-First / Network-First / Stale-While-Revalidate
  - 后台同步: BackgroundSync, Periodic Background Sync

离线优先 = AP 系统选择:
  可用性优先 + 分区容错
  一致性通过后台同步最终达成
```

---

## 二、待完善内容

- [ ] Service Worker 的生命周期状态机
- [ ] 后台同步的可靠性边界
