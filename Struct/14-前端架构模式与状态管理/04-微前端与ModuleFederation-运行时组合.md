# 微前端与 Module Federation：运行时组合

> **来源映射**: View/05.md §10.2
> **国际权威参考**: Zack Jackson "Module Federation" (Webpack 5, 2020); Single-SPA Documentation; Michael Geers "Micro Frontends in Action" (Manning, 2020); Newman "Building Microservices" (O'Reilly, 2021), Ch. 1 (微服务分解原则)

---

## 一、知识体系思维导图

```text
微前端与运行时组合
│
├─► 分解策略
│   ├─ 按业务域分解: 每个微前端对应独立业务能力
│   ├─ 按团队自治分解: 康威定律的技术编码
│   └─ 按发布单元分解: 独立构建、独立部署、独立运行
│
├─► 运行时集成模式
│   ├─ Module Federation: 运行时共享依赖 + 动态远程加载
│   ├─ iframe 集成: 最强隔离，最差体验
│   ├─ Web Components: 原生封装，框架无关
│   ├─ Single-SPA: 路由级生命周期管理
│   └─ import-map / ES Modules: 浏览器原生模块映射
│
├─► 共享依赖管理
│   ├─ 共享版本协商: singleton / strictVersion / eager
│   ├─ 依赖去重: 运行时仅加载一份 React/Vue 实例
│   └─ 版本冲突: 多版本共存 vs 强制统一
│
└─► 形式化洞察
    ├─ 微前端 ≈ 前端的分片数据库 (Sharding)
    ├─ Module Federation = 分布式链接器 (Dynamic Linker)
    └─ 运行时组合 vs 构建时组合: 延迟绑定 vs 静态绑定
```

---

## 二、核心概念的形式化定义

### 2.1 微前端的代数结构

```text
定义 (微前端系统):
  设系统 𝓜 = {M₁, M₂, ..., Mₙ} 为微前端集合
  每个微前端 Mᵢ = ⟨UIᵢ, Stateᵢ, Routerᵢ, Buildᵢ, Deployᵢ⟩ 满足:
    1. 独立构建: Buildᵢ 不依赖 Buildⱼ (i ≠ j)
    2. 独立部署: Deployᵢ 可独立执行
    3. 运行时组合: ∃Shell : Shell ∘ M₁ ∘ M₂ ∘ ... ∘ Mₙ → IntegratedApp

定义 (Shell / 容器应用):
  Shell = ⟨Router, Layout, SharedDepsRegistry, LifecycleManager⟩
  Router:    将 URL 映射到对应微前端的激活/卸载
  Layout:    定义微前端的挂载点 (DOM 容器)
  Registry:  管理共享依赖的版本协商
  Lifecycle: bootstrap → mount → update → unmount
```

### 2.2 Module Federation 的分布式链接语义

```text
定义 (Module Federation):
  设 Host 为容器应用，Remote 为远程微前端
  MF 在运行时建立动态模块链接:
    Host 声明 remotes: { app1: "app1@https://cdn.example.com/remoteEntry.js" }
    Remote 暴露 exposes: { "./Component": "./src/Component" }
    运行时加载: import("app1/Component") → 动态获取 + 执行 + 渲染

共享依赖协议:
  SharedScope = { react: { [version]: ModuleFactory, singleton: bool } }
  版本协商算法 (简化):
    1. Host 注册 shared react@18.2.0 (singleton=true)
    2. Remote1 请求 react@^18.0.0 → 匹配 Host 版本 → 复用
    3. Remote2 请求 react@17.0.0 → 版本不匹配 → 报错或加载独立副本

形式化洞察:
  Module Federation 是浏览器中的「动态链接器」(Dynamic Linker)
  将传统的构建时静态链接 (webpack bundle) 延迟到运行时
  代价: 丧失构建时的类型检查与依赖分析完整性
```

### 2.3 集成模式的谱系分析

```text
模式 I: iframe (最强隔离)
  隔离维度: JS 运行时、DOM、CSS、Storage 完全隔离
  通信机制: postMessage (CSP 风格显式通道)
  代价: 性能开销 (独立渲染进程)、体验断裂 (弹窗遮罩无法跨边界)

模式 II: Web Components (原生封装)
  隔离维度: Shadow DOM (CSS 隔离)、CustomElement (生命周期)
  通信机制: 属性/事件 (标准 DOM 接口)
  代价: 框架互操作性复杂 (React/Vue 封装为 Web Component 需适配层)

模式 III: Module Federation (运行时共享)
  隔离维度: 构建独立，运行时在统一 JS 上下文
  通信机制: 共享模块、全局事件、URL 状态
  代价: 共享依赖版本冲突、全局样式污染、错误边界难以隔离

模式 IV: Single-SPA (路由级编排)
  隔离维度: 路由切换时的生命周期管理
  通信机制: 自定义事件、共享数据层
  代价: 框架版本必须一致或支持多实例，路由冲突风险
```

---

## 三、多维矩阵对比

| 维度 | iframe | Web Components | Module Federation | Single-SPA |
|------|--------|---------------|-------------------|------------|
| **JS 隔离** | **✅ 完全** | ⚠️ 同一运行时 | ❌ 共享运行时 | ❌ 共享运行时 |
| **CSS 隔离** | **✅ 完全** | **✅ Shadow DOM** | ❌ 需约定 | ❌ 需约定 |
| **性能** | 差 (独立进程) | 良 | **优** | 良 |
| **体验一致性** | 差 | **良** | **优** | 良 |
| **独立部署** | ✅ | ✅ | **✅** | ✅ |
| **共享依赖** | ❌ | ⚠️ 需适配 | **✅ 原生** | ⚠️ 需配置 |
| **框架无关** | **✅** | **✅** | ⚠️ 需共享 | ⚠️ 需适配 |
| **学习曲线** | 低 | 中 | 高 | 中 |
| **2026年首选** | 遗留系统 | 设计系统组件 | **大型应用分解** | 路由级迁移 |

---

## 四、权威引用

> **Zack Jackson** (Module Federation 作者, 2020):
> "Module Federation allows JavaScript applications to dynamically load code from other applications, sharing dependencies if possible."

> **Michael Geers** ("Micro Frontends in Action", Manning 2020):
> "The idea behind micro frontends is to think about a website or web app as a composition of features which are owned by independent teams."

> **Sam Newman** ("Building Microservices", O'Reilly 2021):
> "Microservices are independently releasable services modeled around a business domain." — 微前端是这一原则在前端层的自然延伸。

> **Single-SPA Core Team**:
> "single-spa is a framework for bringing together multiple JavaScript microfrontends in a frontend application."

---

## 五、工程实践与代码示例

### 5.1 Webpack Module Federation 配置

```js
// host/webpack.config.js —— 容器应用
const { ModuleFederationPlugin } = require("webpack").container;

module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: "host",
      remotes: {
        // 声明远程微前端入口
        checkout: "checkout@https://cdn.example.com/checkout/remoteEntry.js",
        product: "product@https://cdn.example.com/product/remoteEntry.js",
      },
      shared: {
        react: { singleton: true, requiredVersion: "^18.0.0" },
        "react-dom": { singleton: true, requiredVersion: "^18.0.0" },
      },
    }),
  ],
};

// checkout/webpack.config.js —— 远程微前端
module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: "checkout",
      filename: "remoteEntry.js",
      exposes: {
        "./CheckoutPage": "./src/CheckoutPage",
        "./CartWidget": "./src/CartWidget",
      },
      shared: {
        react: { singleton: true, requiredVersion: "^18.0.0" },
      },
    }),
  ],
};

// host/src/App.jsx —— 运行时动态加载
import React, { Suspense } from "react";
const CheckoutPage = React.lazy(() => import("checkout/CheckoutPage"));

function App() {
  return (
    <Suspense fallback={<div>Loading checkout...</div>}>
      <CheckoutPage />
    </Suspense>
  );
}
```

### 5.2 样式隔离策略 (CSS-in-JS + 命名约定)

```js
// 各微前端采用统一的 CSS 命名空间约定
// checkout/src/components/Button.jsx
function Button({ children }) {
  return <button className="mf-checkout-button">{children}</button>;
}

// 配合构建时前缀注入 (PostCSS / Babel)
// 输出: .mf-checkout__button { ... }

// 全局样式冲突防御检查 (CI 阶段)
const forbiddenGlobals = [".button", ".container", ".wrapper"];
// ❌ 违规: 微前端不得使用无命名空间的全局选择器
```

---

## 六、批判性总结

微前端与 Module Federation 代表了前端架构从「单体巨石」向「分布式系统」演进的历史性跨越，但这一跨越在理论层面充满了未解决的 tension。Module Federation 将 Webpack 的构建时 bundling 语义延迟到浏览器运行时，本质上是在客户端重新发明操作系统级别的「动态链接器」。这种设计的工程勇气令人赞叹，但其形式化代价同样不可忽视：构建时的静态分析——类型检查、tree-shaking、死代码消除、依赖循环检测——在运行时模块加载的场景中部分失效，错误从「编译期可捕获」退化为「生产环境偶现」。

更深层的批判指向微前端的「分解合理性」问题。微服务在后端的分解依据通常是「有界上下文」与「独立发布节奏」，但前端的特殊性在于用户体验的「视觉连续性」与「交互一致性」要求。当两个微前端共享同一个导航栏、同一个主题系统、同一套表单验证规则时，「独立部署」的理想便与「体验统一」的现实产生摩擦。共享依赖的版本协商机制（singleton / strictVersion）虽然在技术上优雅，却无法解决「语义版本兼容但视觉风格断裂」的产品级问题。

从数据库理论的视角审视，微前端与数据库分片（Sharding）存在深刻的同构性：两者都将全局状态空间划分为局部管理的子集，都面临跨分区查询（跨微前端通信）的性能与一致性挑战，都需要一个「编排层」（Shell / Query Router）来协调分布式单元。然而，前端比数据库多出一个维度——**用户体验的实时一致性**。用户不会在 300ms 内容忍「购物车微前端已更新但导航栏微前端仍显示旧数量」的最终一致窗口。这意味着微前端的 decomposition 边界必须比后端微服务更加谨慎地贴近「用户心智模型中的自然分区」，而非单纯的「团队组织结构映射」。Module Federation 是工具层面的卓越创新，但微前端架构的成功与否，最终取决于组织是否具备定义清晰、稳定、以用户为中心的业务边界的能力。
