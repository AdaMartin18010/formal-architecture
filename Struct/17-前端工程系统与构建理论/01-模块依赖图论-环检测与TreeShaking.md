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


---

## 七、概念属性关系网络

```text
模块依赖图论概念属性关系网络
│
├─► 核心实体
│   ├─ [模块节点 v ∈ V] ──→ 属性: {文件路径, AST, 导出符号集, 副作用标记}
│   ├─ [依赖边 e=(u,v) ∈ E] ──→ 属性: {导入类型(static/dynamic), 导入符号, 条件依赖}
│   ├─ [入口节点 Entry ⊆ V] ──→ 属性: {chunk关联, 加载优先级, 运行时必需}
│   └─ [副作用节点 S ⊆ V] ──→ 属性: {全局状态修改, CSS注入, polyfill, 强制保留}
│
├─► 图论算法实体
│   ├─ [DFS三色标记] ──→ 属性: {WHITE(未访问), GRAY(访问中), BLACK(已完成)}
│   ├─ [Tarjan SCC] ──→ 属性: {index, lowlink, 栈状态}
│   └─ [可达性分析] ──→ 属性: {BFS/DFS frontier, 访问集合, 死代码补集}
│
├─► 属性关系
│   ├─ Entry × V → Reachable: 入口到模块的可达性关系
│   ├─ side: V → {0,1}: 副作用谓词决定模块是否可被消除
│   ├─ color: V → {WHITE,GRAY,BLACK}: DFS状态决定环检测
│   ├─ lowlink ≡ index: Tarjan条件决定SCC根节点
│   └─ V \ Reachable ⊆ S?: 死代码与副作用的交集约束
│
└─► 课程对齐
    ├─ MIT 6.170: 模块化与依赖管理
    ├─ Stanford CS 142: Webpack bundler 实践
    └─ CMU 17-313: 软件工程中的静态分析
```

---

## 八、形式化推理链

**推理命题 P**: ES Module 的静态结构使 Tree Shaking 成为编译期精确优化，而 CommonJS 的动态 require 导致 Tree Shaking 只能进行启发式近似。

**推理链**:

```text
前提 A1 (Rich Harris, 2016): "Tree-shaking is like dead code elimination, but powered by
                               ES modules' static structure. Import and export declarations
                               are static, analyzable at build time."
前提 A2 (Tobias Koppers, JSConf EU 2019): "The module graph is the central data structure
                                           that everything else revolves around."
前提 A3 (Addy Osmani, Google, 2018): "Parsing and compilation on the main thread can be
                                      2-5× the download cost on mobile."

步骤 1: 由 A1，ES Module 的 import/export 位于语法顶层
       ∀ import_stmt ∈ Module, import_stmt 不在条件分支或函数内部
       ∴ 依赖图 G=(V,E) 可在编译期完全确定
       形式化: ∃ Parser, ∀ source_file, Parse(source_file) → G 是确定性函数

步骤 2: 由 CommonJS 的 dynamic require 语义
       require(expr) 中 expr 可为运行时变量
       例: require(cond ? 'a' : 'b')
       ∴ 依赖边 e=(u,v) 的存在性在运行时才能确定
       形式化: G_runtime 是 G_static 的超集，G_runtime ⊇ G_static

步骤 3: Tree Shaking 的精确性依赖于 G 的完备性
       设 Reachable_static = {v | ∃e∈Entry, e →* v in G_static}
       设 Reachable_runtime = {v | ∃e∈Entry, e →* v in G_runtime}
       由于 G_runtime ⊇ G_static，有 Reachable_runtime ⊇ Reachable_static
       ∴ 基于 G_static 的 Tree Shaking 可能错误地消除运行时代码:
          DeadCode_static = V \ Reachable_static
          但 ∃v ∈ DeadCode_static, v ∈ Reachable_runtime

步骤 4: 副作用分析 side: V → {0,1} 的保守策略
       若 side(v) = 1 (全局副作用)，则 v 强制保留
       问题: 编译器无法静态确定所有副作用
       例: 模块修改 window 对象、注入 CSS、注册全局事件
       ∴ 实际实现采用保守策略: 未标记 /*#__PURE__*/ 的顶级调用视为有副作用

步骤 5: 综合 A1-A3
       ESM + sideEffects: false + /*#__PURE__*/ 标注 ⟹ 最优 Tree Shaking
       CJS + 动态 require + 无标注 ⟹ 保守保留，产物膨胀 15%-30%

结论: Tree Shaking 的精确性上界由模块系统的静态性决定。
      ESM 的静态导入使编译期精确分析成为可能；CJS 的动态特性使分析不完备，
      只能采用保守近似。这是编程语言设计（模块语义）直接影响编译器优化的典型案例。
```

---

## 九、推理判定树/决策树

```text
Tree Shaking 优化策略选择决策树
│
├─► Q1: 项目使用 ESM 还是 CJS?
│   ├─ ESM ──→ 继续 Q2
│   └─ CJS ──→ 采用启发式分析 (webpack 的 usedExports: true)，预期优化有限
│
├─► Q2: 是否设置了 sideEffects: false?
│   ├─ 是 ──→ 继续 Q3
│   └─ 否 ──→ 在 package.json 中声明 sideEffects: false 或精确列表
│
├─► Q3: 是否存在大量纯函数调用?
│   ├─ 是 ──→ 添加 /*#__PURE__*/ 标注，启用编译器安全消除
│   └─ 否 ──→ 继续 Q4
│
├─► Q4: 使用的 Bundler?
│   ├─ Rollup ──→ 最优 Tree Shaking (原生 ESM，副作用分析最精确)
│   ├─ Webpack ──→ 良好 (需配置 optimization.usedExports + sideEffects)
│   ├─ Vite ──→ 优秀 (生产环境使用 Rollup)
│   └─ esbuild ──→ 基础 (速度快但副作用分析较保守)
│
└─► Q5: 验证 Tree Shaking 效果
    ├─ 使用 rollup-plugin-visualizer / webpack-bundle-analyzer
    ├─ 检查产物中是否仍包含未引用模块
    └─ 若存在 ──→ 检查模块是否有隐式副作用 (polyfill/CSS/global)

环检测与重构决策树
│
├─► Q1: 检测到循环依赖?
│   ├─ 否 ──→ 项目健康，维持当前架构
│   └─ 是 ──→ 继续 Q2
│
├─► Q2: 环涉及模块数?
│   ├─ 2个模块 ──→ 提取公共接口文件，双向依赖改为共同依赖
│   ├─ 3-5个模块 ──→ 使用 Tarjan 分解 SCC，识别核心耦合点
│   └─ >5个模块 ──→ 架构级重构：引入事件总线或依赖注入解耦
│
├─► Q3: 环是否为运行时必需?
│   ├─ 是 (如相互递归) ──→ 保留环，确保运行时加载器支持
│   └─ 否 ──→ 继续 Q4
│
└─► Q4: 重构策略
    ├─ 提取接口层: A→B→C→A 改为 A→I, B→I, C→I
    ├─ 合并模块: 将环内模块合并为单一模块
    └─ 依赖注入: 将直接导入改为构造函数/函数参数注入
```

---

## 十、国际课程对齐标注

> **📚 MIT 6.170 Software Studio** (Daniel Jackson)
>
> - **对齐章节**: §2.1 模块依赖图, §2.2 Tree Shaking 可达性分析, §2.3 强连通分量
> - **课程要点**: "Fundamentals of structuring a web application and writing modular code."
> - **深度映射**: MIT 6.170 的模块化编程主题直接对应本文件的模块依赖图论。
>   Daniel Jackson 强调"概念设计"(conceptual design)以达成清晰度与模块化——
>   本文件将这一设计原则形式化为有向图 G=(V,E) 的拓扑约束（无环性、SCC分解）。
>   课程中关于依赖管理的讨论（如如何避免循环依赖）对应本文件 DFS 三色法和
>   Tarjan 算法的工程应用。

> **📚 Stanford CS 142 Web Applications** (Mendel Rosenblum)
>
> - **对齐章节**: §一 知识体系思维导图, §5.1 副作用标注, §5.3 循环依赖检测
> - **课程要点**: "Project 4: ReactJS + Webpack bundling. Understanding module imports
>   and how bundlers resolve dependencies."
> - **深度映射**: CS142 的 Project 4 要求学生使用 Webpack 打包 React 组件，
>   学生必须理解 Webpack 如何从 entry 出发递归解析 import 语句——这正是本文件
>   "构建 ModuleGraph"过程的工程实践。课程中涉及的 ESLint 静态分析与本文件
>   副作用分析 (side: V→{0,1}) 具有相同的形式化目标：在编译期检测代码属性。

> **📚 CMU 17-313 Foundations of Software Engineering**
>
> - **对齐章节**: §2.2 Tree Shaking, §六 批判性总结
> - **课程要点**: "Static analysis, dependency management, and build system fundamentals."
> - **深度映射**: CMU 17-313 将静态分析视为软件工程的核心能力。本文件所述
>   Tree Shaking（基于可达性分析的代码消除）是静态分析在编译优化中的最直接应用。
>   课程中关于"如何评估代码质量"的讨论，与本文件批判性总结中"静态分析不完备性"
>   的论述形成呼应——两者都强调静态分析的保守性与近似性边界。
