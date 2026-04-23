# 前端存储层次：从 CPU 缓存到网络存储

> **来源映射**: View/05.md §4.1
> **权威参考**: WHATWG Storage Standard

---

## 一、存储层次的形式化

| 层级 | 延迟 | 容量 | 持久性 | 前端 API |
|------|------|------|--------|---------|
| **L1: CPU Cache** | ~1ns | ~64KB | 易失 | JS 变量/闭包 |
| **L2: Heap** | ~100ns | ~1GB | 易失 | V8 Heap |
| **L3: SessionStorage** | ~1μs | ~5MB | 会话级 | sessionStorage |
| **L4: localStorage** | ~10μs | ~10MB | 永久 | localStorage |
| **L5: IndexedDB** | ~1ms | ~1GB | 永久 | IndexedDB |
| **L6: OPFS** | ~5ms | ~磁盘容量 | 永久 | Origin Private FS |
| **L7: SQLite WASM** | ~10ms | ~2GB | 永久 | sql.js |
| **L8: Network** | ~100ms | ∞ | 服务端控制 | fetch, Cache API |

---

## 二、待完善内容

- [ ] 各层级的性能基准测试数据
- [ ] 存储层级的缓存替换策略
