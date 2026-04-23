# 构建工具链对比：Bundler 与 Transpiler 演化

> **来源映射**: View/05.md §8
> **权威参考**: esbuild 文档, SWC 文档, Turbopack 文档

---

## 一、工具链层次

| 层级 | 工具 | 功能 | 实现语言 |
|------|------|------|---------|
| **Bundler** | Webpack / Vite / Turbopack / Rspack | 模块打包 | JS / Rust |
| **Transpiler** | SWC / Babel / esbuild | 语法转换 | Rust / JS / Go |
| **包管理** | pnpm / npm / yarn | 依赖解析 | JS |
| **任务编排** | Turborepo / Nx | 增量构建 | JS |

---

## 二、待完善内容

- [ ] 各工具的性能基准对比
- [ ] Bundler 的模块图解析算法对比
