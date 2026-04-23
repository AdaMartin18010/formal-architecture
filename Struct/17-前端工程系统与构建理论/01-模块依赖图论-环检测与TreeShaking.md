# 模块依赖图论：环检测与 Tree Shaking

> **来源映射**: View/03.md §2.2, View/05.md §8
> **国际权威参考**: Rollup Documentation (Rich Harris), Webpack Module Federation (Zack Jackson), "JavaScript Module Bundling" (Google V8 Blog, 2018), "Static Module Resolution in ES6" (ECMA-262 Spec)

---

## 一、知识体系思维导图

```text
前端模块依赖图论
│
├─► 依赖图模型
│   ├─ 有向图 G = (V, E)
│   │   V: 模块集合 (文件/ES Module/Namespace)
│   │   E: 依赖关系 (import/export/require)
│   ├─ 无环依赖图 (DAG): 可拓扑排序，构建顺序确定
│   └─ 有环依赖图: 需打破循环或允许运行时解析
│
├─► 环检测算法
│   ├─ DFS 三色标记: 白(未访问) → 灰(访问中) → 黑(已完成)
│   ├─ 遇到灰节点 → 发现环
│   ├─ Tarjan 算法: 强连通分量 (SCC) 分解
│   └─ 时间复杂度: O(V + E)
│
├─► Tree Shaking (摇树优化)
│   ├─► 可达性分析 (Reachability Analysis)
│   │   ├─ 入口模块为根节点
│   │   ├─ DFS/BFS 遍历所有可达模块
│   │   └─ 不可达模块被"摇掉"
│   │
│   ├─► ES Module 静态结构优势
│   │   ├─ import/export 在语法顶层
│   │   ├─ 编译时确定依赖关系
│   │   └─ 副作用标注: "sideEffects": false
│   │
│   ├─► CommonJS 动态挑战
│   │   ├─ 动态 require: require(cond ? 'a' : 'b')
│   │   ├─ 运行时确定依赖
│   │   └─ Tree Shaking 困难 → 启发式分析
│   │
│   └─► 副作用分析 (Side Effect Analysis)
│       ├─ 纯函数: 无副作用，可安全删除未使用导出
│       ├─ 副作用: 修改全局状态、polyfill、CSS注入
│       ├─ PURE 标注: /*#__PURE__*/ 提示编译器
│       └─ 闭包副作用: 模块级变量逃逸
│
├─► 代码分割 (Code Splitting)
│   ├─ 入口点分割: 多页面应用 (MPA)
│   ├─ 动态导入: import() → 单独 chunk
│   ├─ 公共 chunk: SplitChunksPlugin 提取 vendor
│   └─ 预加载: prefetch / preload 指令
│
└─► Monorepo 依赖图扩展
    ├─ 工作区: pnpm workspace / Yarn workspace / Nx
    ├─ 内部依赖: workspace:* 协议
    ├─ 任务图: 构建顺序由依赖图拓扑排序决定
    └─ 缓存: 未变更的模块跳过重新构建
```

---

## 二、核心概念的形式化定义

### 2.1 模块依赖图

```text
定义 (模块依赖图):
  G = (V, E) 是有向图

  V = {m₁, m₂, ..., mₙ}: 模块集合
  E = {(mᵢ, mⱼ) | mᵢ imports from mⱼ}: 依赖边

  关键性质:
    1. G 是无环图 (DAG) ⟺ 存在拓扑排序
    2. G 有环 ⟺ 存在反向边 (back edge) in DFS

  环检测 (DFS三色法):
    color: V → {WHITE, GRAY, BLACK}

    DFS(v):
      color[v] = GRAY
      for each u in neighbors(v):
        if color[u] == GRAY:  // 发现环！
          report_cycle(v, u)
        if color[u] == WHITE:
          DFS(u)
      color[v] = BLACK

    时间复杂度: O(|V| + |E|)
    空间复杂度: O(|V|)
```

### 2.2 Tree Shaking 的可达性分析

```text
定义 (Tree Shaking):
  设入口模块集合 Entry = {e₁, e₂, ..., eₖ}

  可达模块集:
    Reachable = ⋃_{e ∈ Entry} DFS_reachable(e)

  其中 DFS_reachable(e) = {v ∈ V | 存在路径 e →* v}

  Tree Shaking 结果:
    DeadCode = V \ Reachable
    输出: G' = (Reachable, E[Reachable])

  副作用约束:
    设副作用函数 side: V → {0, 1}
    若 side(v) = 1 (有副作用):
      v 必须保留，即使 v ∉ Reachable

  ES Module vs CommonJS:
    ES Module: 依赖在编译时确定 → Tree Shaking 精确 (AOT)
    CommonJS: 依赖在运行时确定 → 需启发式分析 (近似)
```

### 2.3 强连通分量与循环依赖

```text
定义 (强连通分量 SCC):
  对于子图 G' ⊆ G，若 G' 中任意两节点 u, v 互相可达，
  则 G' 是一个强连通分量。

  Tarjan 算法:
    为每个节点维护 index 和 lowlink
    当 lowlink[v] == index[v] 时，弹出栈中节点形成一个 SCC

  工程映射:
    每个 SCC 对应一组循环依赖的模块
    建议重构: 提取接口层打破循环，或合并为单一模块
```

---

## 三、多维矩阵对比

| 维度 | Webpack | Rollup | Vite | esbuild | SWC |
|------|---------|--------|------|---------|-----|
| **架构** | JS编写+插件系统 | JS编写+插件系统 | 开发服务器+Rollup生产 | Go编写 | Rust编写 |
| **Tree Shaking** | 好 (ESM) | **优秀** (原生ESM) | 同Rollup | 好 | 好 |
| **启动速度** | 慢 (秒级) | 中 | **快** (毫秒级) | **极快** | **极快** |
| **构建速度** | 中 | 中 | 快 | **极快** | **极快** |
| **HMR** | ✅ 成熟 | ❌ 弱 | ✅ 极速 | ❌ 无 | ❌ 无 |
| **代码分割** | ✅ 强大 | ✅ 支持 | ✅ 支持 | ⚠️ 有限 | ⚠️ 有限 |
| **生态** | **最大** | 大 | 快速增长 | 小 | 小 |
| **适用场景** | 大型应用 | 库打包 | 现代前端开发 | 工具链 | 工具链 |

---

## 四、权威引用

> **Rich Harris** (Rollup 作者, 2016):
> "Tree-shaking is like dead code elimination, but powered by ES modules' static structure. It relies on the fact that import and export declarations are static, which means they can be analyzed at build time."

> **Tobias Koppers** (Webpack 作者, JSConf EU 2019):
> "Webpack's job is to bundle your JavaScript, but its real value is in the ecosystem of loaders and plugins. The module graph is the central data structure that everything else revolves around."

> **Evan You** (Vue/Vite 作者, 2021):
> "Vite is not just a faster bundler; it's a rethinking of the development server architecture. Native ESM in development removes the bundling step entirely, making the module graph explicit in the browser."

> **Addy Osmani** (Google Chrome, "JavaScript Start-up Performance", 2018):
> "The cost of JavaScript is not just the download time. Parsing and compilation on the main thread can be 2-5× the download cost on mobile devices. Tree Shaking directly reduces this tax."

---

## 五、工程实践与代码示例

### 5.1 副作用标注

```json
// package.json
{
  "name": "my-library",
  "sideEffects": [
    "*.css",
    "*.scss",
    "./src/polyfill.js"
  ]
}
```

```javascript
// 纯函数标注
const add = /* #__PURE__ */ (a, b) => a + b;

// 副作用标注
const globalSetup = /* @__PURE__ */ (() => {
  window.myLib = {};
})();
```

### 5.2 动态导入与代码分割

```javascript
// 路由级代码分割
const LazyComponent = React.lazy(() => import('./HeavyComponent'));

// prefetch 预加载
const prefetchAbout = () => {
  const link = document.createElement('link');
  link.rel = 'prefetch';
  link.href = '/about.chunk.js';
  document.head.appendChild(link);
};

// 条件加载
if (user.needsAdvancedFeature) {
  const { advanced } = await import('./advanced-features');
  advanced.init();
}
```

### 5.3 循环依赖检测

```javascript
// 使用 Madge 检测循环依赖
// npx madge --circular --extensions js,ts src/

// 重构策略: 提取公共接口
// 前: A → B → C → A (循环)
// 后: A → Interface, B → Interface, C → Interface (DAG)
```

---

## 六、批判性总结

Tree Shaking 是**静态分析在工程实践中的胜利**：ES Module 的顶层 import/export 结构使编译器能够在不执行代码的情况下确定依赖关系，从而精确剪除未使用的代码。但 Tree Shaking 的精确性受限于**副作用边界**——当模块修改全局状态、注入 CSS 或执行 polyfill 时，编译器无法确定这些副作用是否被其他模块隐式依赖，只能保守地保留整个模块。这种"保守保留"策略在实践中常导致产物膨胀 15%-30%，这是静态分析不完备性的必然代价。

Vite 的架构洞察是**开发时与生产时的分离**：开发时使用原生 ESM（浏览器直接解析模块，无需打包），生产时使用 Rollup 进行优化打包。这颠覆了 Webpack 的"开发生产同构"假设——开发时的首要目标是**启动速度**而非**打包优化**，因为开发者每秒都在经历启动过程。这一分离的代价是**环境差异风险**：某些 bug 只在生产构建中出现，因为 Rollup 的优化改变了模块图的语义。

Monorepo 工具链（Nx, Turborepo）将图论从模块级提升到**任务级**：构建、测试、Lint 等任务构成另一个有向图，工具通过拓扑排序和缓存优化 CI/CD 流水线。这是图论在前端工程中的**二次胜利**——第一次用于模块依赖解析，第二次用于任务调度优化。然而，任务图的构建和维护本身也引入了新的复杂度：当任务依赖声明不准确时，缓存可能返回过期产物，导致**不可重现的构建错误**。这提示我们：任何层级的图优化都必须以**图的正确性**为前提，否则优化将退化为缺陷的放大器。
