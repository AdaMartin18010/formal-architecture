# monorepo 管理：Turborepo 与 Nx 的 DAG 编排

> **来源映射**: View/05.md §8.1
> **权威参考**: Turborepo 文档, Nx 文档

---

## 一、核心概念

```text
Turborepo Pipeline:
  定义任务依赖图: build → test → lint → deploy
  远程缓存: 复用已构建产物
  增量构建: 仅构建变更影响的包

Nx DAG:
  项目图: 包之间的依赖关系
   affected 命令: 仅执行受变更影响的任务
```

---

## 二、待完善内容

- [ ] monorepo 工具的任务调度算法对比
- [ ] 远程缓存的一致性与失效策略
