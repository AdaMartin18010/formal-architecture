# 从 Figma 到代码：设计系统的工作流

> **来源映射**: View/05.md §6.4
> **国际权威参考**: Figma Dev Mode Docs, "Design Tokens" (W3C Community Group), Style Dictionary (Amazon), Tokens Studio Docs, "DesignOps" (Dave Malouf, 2018), "The Design Systems Handbook" (DesignBetter.Co), Supernova, Specify

---

## 一、知识体系思维导图

```text
从 Figma 到代码：设计系统工作流
│
├─► 设计端 (Figma 生态)
│   ├─ Figma Variables: 原生设计令牌管理 (2023+)
│   ├─ Figma Styles: 颜色/文本/效果/网格样式
│   ├─ Figma Components: 可复用的设计组件 (变体/属性)
│   ├─ Figma Dev Mode: 开发者 inspect 模式
│   ├─ Tokens Studio (Figma Plugin): 令牌导入/导出/同步
│   └─ 设计规范: Auto Layout、约束、响应式规则
│
├─► 转换层 (Design → Code)
│   ├─► Style Dictionary
│   │   ├─ 输入: tokens.json / tokens.yaml (W3C DTCG 格式)
│   │   ├─ 转换 (Transforms): 值转换、命名转换、平台适配
│   │   ├─ 格式化 (Formats): CSS / SCSS / iOS / Android / JSON
│   │   └─ 动作 (Actions): 文件复制、自定义后处理
│   │
│   ├─► Tokens Studio Sync
│   │   ├─ Figma ↔ Git 双向同步
│   │   ├─ 令牌引用解析 (Aliases)
│   │   └─ 主题集合管理 (Theme Sets)
│   │
│   └─► 代码生成器
│       ├─ 组件代码生成: Figma → React/Vue/Svelte
│       ├─ 样式代码生成: CSS / CSS-in-JS / Tailwind
│       └─ 类型定义生成: TypeScript 接口
│
├─► 工程端 (Code 生态)
│   ├─ CSS Custom Properties: 运行时主题切换
│   ├─ CSS-in-JS: styled-components / Emotion
│   ├─ Tailwind CSS: Utility-first，令牌 → config
│   ├─ 组件库: React / Vue / Angular / Svelte
│   └─ 类型系统: TypeScript 类型驱动设计约束
│
└─► CI/CD 工作流
    ├─ 设计变更触发: Figma webhook → GitHub Actions
    ├─ 令牌构建: Style Dictionary → 多平台产物
    ├─ 视觉回归: Chromatic / Storybook 对比
    ├─ 自动化发布: Changesets / semantic-release
    └─ 文档同步: Storybook / Docusaurus 自动更新
```

---

## 二、核心概念的形式化定义

### 2.1 设计工作流的形式化模型

```text
定义 (设计系统工作流 𝓦):
  𝓦 = ⟨Design, Transform, Code, Validate, Deploy⟩

  Design: 设计空间 (Figma 中的视觉规范)
  Transform: 转换函数集合 (Design → Code 的映射)
  Code: 代码空间 (组件实现 + 样式定义)
  Validate: 验证谓词 (一致性检查)
  Deploy: 部署函数 (产物分发)

  转换函数:
    TokenTransform: FigmaVariables → DesignTokens
    StyleTransform: DesignTokens → CSS / SCSS / iOS / Android
    ComponentTransform: FigmaComponents → CodeComponents

  一致性谓词:
    Consistent(d, c) ⟺ Visual(d) ≈ Visual(Render(c))
    即: 设计稿的视觉输出 ≈ 代码渲染的视觉输出
```

### 2.2 Style Dictionary 的变换代数

```text
定义 (Style Dictionary 变换系统):
  设输入令牌集合 T_in，输出平台集合 P = {css, scss, ios, android, js}

  变换管道:
    Pipeline = Parse ∘ Transform ∘ Format ∘ Action

    Parse: JSON/YAML → 内部令牌图 G_token
    Transform: G_token → G_token'  (值转换、引用解析)
    Format: G_token' → String      (平台特定格式)
    Action: String → FileSystem    (文件写入)

  变换函数类型:
    1. 值变换: f(value) → value'
       例: hex → rgb, px → rem, px → pt
    2. 命名变换: f(name) → name'
       例: "color-primary-500" → "colorPrimary500" (camelCase)
    3. 属性变换: f(token) → token'
       例: 添加平台前缀、计算派生值

  变换的组合性质:
    设 𝓕 为所有变换的集合，∘ 为函数复合
    ⟨𝓕, ∘, id⟩ 构成幺半群

    封闭性: ∀f,g ∈ 𝓕, f ∘ g ∈ 𝓕
    结合律: (f ∘ g) ∘ h = f ∘ (g ∘ h)
    单位元: id(t) = t
```

### 2.3 双向同步的形式化

```text
定义 (双向同步问题):
  设设计端状态 D(t)，代码端状态 C(t)

  理想同步:
    ∀t, D(t) ≈ C(t)  (视觉语义等价)

  单向同步 (Design → Code):
    C(t+1) = Sync(D(t+1))
    问题: 代码端的自定义修改被覆盖

  双向同步:
    D(t+1) = Merge(D(t), CodeToDesign(C(t)))
    C(t+1) = Merge(C(t), DesignToCode(D(t)))

    Merge: 三路合并函数，需解决冲突

  冲突类型:
    1. 设计端修改令牌值，代码端也修改同一令牌
    2. 设计端新增令牌，代码端删除相关组件
    3. 设计端删除组件，代码端仍在引用

  当前无解: 双向同步的冲突消解需要人类设计师介入
```

---

## 三、多维矩阵对比

### 3.1 设计-代码转换工具对比

| 维度 | Style Dictionary | Tokens Studio | Specify | Supernova |Cobra |
|------|-----------------|---------------|---------|-----------|------|
| **数据源** | JSON/YAML | Figma Plugin | Figma/Adobe | Figma/Sketch/Adobe | Figma |
| **输出平台** | **15+** (全平台) | 需配合 SD | 多平台 | iOS/Android/Flutter | React |
| **双向同步** | ❌ (单向) | ✅ Figma↔Git | ✅ | ⚠️ 有限 | ❌ |
| **组件代码生成** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **W3C DTCG 兼容** | ✅ v3+ | ✅ | ⚠️ 部分 | ⚠️ 部分 | ❌ |
| **自定义转换** | ✅ 极丰富 | ⚠️ 有限 | ✅ | ✅ | ⚠️ 有限 |
| **成本** | 开源 | 开源/付费 | 付费 | 付费 | 开源 |
| **适用规模** | 企业级 | 中小团队 | 企业级 | 企业级 | 小型 |

### 3.2 样式技术方案对比

| 维度 | CSS Variables | CSS-in-JS | Tailwind | Sass/Less | CSS Modules |
|------|--------------|-----------|----------|-----------|-------------|
| **运行时主题** | ✅ 原生 | ✅ 动态注入 | ⚠️ 需插件 | ❌ 编译时 | ❌ 编译时 |
| **类型安全** | ❌ | ✅ TS 集成 | ⚠️ 配置驱动 | ❌ | ⚠️ 有限 |
| **构建开销** | 无 | ⚠️ 运行时/构建时 | 大 (purge) | 中 | 小 |
| **令牌集成** | ✅ 直接 | ✅ 对象映射 | ✅ config | ✅ 变量 | ⚠️ 手动 |
| **学习曲线** | 低 | 中 | 中 | 低 | 低 |
| **生态成熟度** | **原生** | 成熟 | 快速增长 | 成熟 | 成熟 |

---

## 四、权威引用

> **Figma Team** ("Dev Mode Announcement", Config 2023):
> "Dev Mode is a new space in Figma for developers with features that help you translate designs into code faster."

> **Danny Banks** (Style Dictionary 作者, Amazon):
> "Style Dictionary is a build system that allows you to define styles once, in a way for any platform or language to consume. A single source of truth for design tokens."

> **Jan Six** (Tokens Studio 作者, 2022):
> "Tokens Studio bridges the gap between design tools and code. It allows designers to manage design tokens in Figma and sync them with a Git repository."

> **Brad Frost** ("The Design Systems Handbook", 2019):
> "A design system is a product serving products. The workflow from design to code is not a handoff but a continuous collaboration."

---

## 五、工程实践与代码示例

### 5.1 Style Dictionary 完整配置

```json
{
  "source": ["tokens/**/*.json"],
  "platforms": {
    "css": {
      "transformGroup": "css",
      "buildPath": "build/css/",
      "files": [{
        "destination": "variables.css",
        "format": "css/variables",
        "options": { "outputReferences": true }
      }]
    },
    "scss": {
      "transformGroup": "scss",
      "buildPath": "build/scss/",
      "files": [{
        "destination": "_variables.scss",
        "format": "scss/variables"
      }, {
        "destination": "_map.scss",
        "format": "scss/map-deep"
      }]
    },
    "js": {
      "transformGroup": "js",
      "buildPath": "build/js/",
      "files": [{
        "destination": "tokens.js",
        "format": "javascript/es6"
      }, {
        "destination": "tokens.d.ts",
        "format": "typescript/es6-declarations"
      }]
    },
    "ios": {
      "transformGroup": "ios",
      "buildPath": "build/ios/",
      "files": [{
        "destination": "StyleDictionaryColor.swift",
        "format": "ios/swift/class.swift",
        "className": "StyleDictionaryColor",
        "filter": { "attributes": { "category": "color" } }
      }]
    }
  }
}
```

### 5.2 GitHub Actions 自动化工作流

```yaml
# .github/workflows/design-tokens.yml
name: Design Tokens CI

on:
  push:
    paths:
      - 'tokens/**'
  repository_dispatch:
    types: [figma-sync]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build tokens
        run: npx style-dictionary build

      - name: Run visual regression
        run: npx chromatic --project-token=${{ secrets.CHROMATIC_TOKEN }}

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v5
        with:
          title: 'chore(tokens): update design tokens from Figma'
          branch: 'auto/design-tokens-update'
```

### 5.3 Tailwind CSS 与 Design Tokens 集成

```javascript
// tailwind.config.js
const tokens = require('./build/js/tokens.js');

module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: tokens.ColorPrimary50,
          500: tokens.ColorPrimary500,
          900: tokens.ColorPrimary900,
        },
      },
      spacing: {
        '4': tokens.Space4,
        '8': tokens.Space8,
        '16': tokens.Space16,
      },
      fontFamily: {
        sans: [tokens.FontFamilySans, 'system-ui', 'sans-serif'],
      },
    },
  },
};
```

### 5.4 Figma → React 组件的代码生成

```typescript
// 使用 figma-api 提取组件规范
import { getFileComponents } from './figma-client';

interface FigmaComponent {
  name: string;
  type: 'COMPONENT' | 'COMPONENT_SET';
  variants?: FigmaVariant[];
  styles: {
    fill?: string;
    stroke?: string;
    effects?: FigmaEffect[];
    layout?: FigmaLayout;
  };
}

// 生成 React 组件骨架
function generateReactComponent(figma: FigmaComponent): string {
  const props = figma.variants?.map(v => `${v.name}: ${v.type}`) || [];

  return `
import React from 'react';

export interface ${figma.name}Props {
  ${props.join('\n  ')}
}

export function ${figma.name}({ ${props.map(p => p.split(':')[0]).join(', ')} }: ${figma.name}Props) {
  return (
    <div className="${figma.name.toLowerCase()}">
      {/* 根据Figma设计规范自动生成的组件实现 */}
    </div>
  );
}
`;
}
```

---

## 六、批判性总结

从 Figma 到代码的工作流是设计系统工程化中最具挑战性的一环，其核心矛盾是**视觉语义的连续性与代码表示的离散性**之间的映射难题。Figma 中的设计稿是像素级的连续空间——设计师可以任意调整一个矩形的圆角为 7.5px，而代码端的 Design Token 系统通常要求离散的规范值（如 4px、8px、16px 的间距阶梯）。这种**量化误差**不是技术缺陷，而是设计系统"一致性约束"的工程体现：通过将连续的设计空间离散化为有限的令牌集合，系统强制了视觉的一致性，但也限制了设计师的自由度。

Style Dictionary 的变换管道本质上是**设计代数的同态映射**：它将设计令牌从一个代数结构（W3C DTCG 的 JSON 表示）映射到另一个代数结构（CSS 变量、iOS Swift 常量、Android XML）。变换的组合性（Parse ∘ Transform ∘ Format）保证了复杂转换的可维护性——每个变换只负责单一的语义转换，通过组合实现多平台输出。但这种组合性也带来了**调试的困难**：当输出结果不符合预期时，开发者需要在变换链的多个阶段定位问题，而 Style Dictionary 的日志输出在这方面仍有改进空间。

双向同步（Bidirectional Sync）是当前工作流的"圣杯"，但本质上是一个**不可完全自动化**的问题。设计端和代码端的变更不仅涉及令牌的值，还涉及组件的结构、交互的行为、甚至业务逻辑的耦合。Tokens Studio 的 Figma↔Git 同步解决了令牌层面的双向问题，但组件层面的同步仍需要人类开发者的介入。未来的突破点可能在于**AI 辅助的代码生成**——通过训练在大量 Figma-to-Code 样本上的多模态模型，自动生成符合设计规范且可维护的组件代码。但这也带来了新的风险：自动生成的代码是否能通过形式化验证？是否满足可访问性和性能约束？这些问题将设计系统的工作流从工程问题扩展为**人机协同的形式化验证问题**。


---

## 七、概念属性关系网络

```text
Figma到代码设计系统工作流概念属性关系网络
│
├─► 核心实体层
│   ├─ [设计端 D(t)]
│   │   ├─ Figma Variables ──→ 属性: {令牌名, 值, 类型, 主题集合}
│   │   ├─ Figma Components ──→ 属性: {变体, 属性, AutoLayout, 约束}
│   │   ├─ Figma Styles ──→ 属性: {颜色样式, 文本样式, 效果样式, 网格样式}
│   │   └─ Tokens Studio ──→ 属性: {Git同步, 引用解析, 主题集管理}
│   │
│   ├─ [转换层 𝓕 = {Parse, Transform, Format, Action}]
│   │   ├─ Parse ──→ 属性: {JSON/YAML解析, 令牌图构建, 引用验证}
│   │   ├─ Transform ──→ 属性: {值转换, 命名转换, 平台适配, 引用解析}
│   │   ├─ Format ──→ 属性: {CSS/SCSS, iOS/Swift, Android/XML, JS/TS}
│   │   └─ Action ──→ 属性: {文件写入, 复制, 自定义后处理}
│   │
│   ├─ [代码端 C(t)]
│   │   ├─ CSS Variables ──→ 属性: {运行时主题, 原生切换, 无构建开销}
│   │   ├─ CSS-in-JS ──→ 属性: {类型安全, 动态注入, 构建时优化}
│   │   ├─ Tailwind ──→ 属性: {Utility-first, 配置驱动, Purge优化}
│   │   └─ 组件库 ──→ 属性: {React/Vue/Angular, Props接口, 类型导出}
│   │
│   └─ [一致性谓词 Consistent(d,c)]
│       ├─ 视觉 ──→ 属性: {像素级等价, 颜色空间匹配, 排版度量一致}
│       ├─ 语义 ──→ 属性: {ARIA角色, 焦点管理, 键盘导航}
│       └─ 行为 ──→ 属性: {交互动画, 状态转换, 响应式断点}
│
├─► 关系映射层
│   ├─ D(t) → TokenTransform: Figma变量映射到设计令牌
│   ├─ TokenTransform → StyleTransform: 令牌转换为平台特定样式
│   ├─ StyleTransform → ComponentTransform: 样式注入组件实现
│   ├─ C(t) → Validate: 代码端验证一致性谓词
│   ├─ Validate → Deploy: 验证通过触发产物分发
│   └─ D(t) ↔ C(t): 双向同步 (理想但存在冲突)
│
├─► 属性约束层
│   ├─ 完备性: ∀t∈T, ∃输出格式 f∈P, f(t) 有定义
│   ├─ 一致性: Consistent(d,c) ⟺ Visual(d) ≈ Visual(Render(c))
│   ├─ 可重现: 相同输入令牌 ⟹ 相同输出产物 (确定性构建)
│   ├─ 无环: G_alias (令牌引用图) 必须为 DAG
│   └─ 平台覆盖: P = {css, scss, ios, android, js} 至少覆盖目标平台
│
└─► 课程对齐层
    ├─ Stanford CS 247: 设计工具与原型实现
    └─ MIT 6.831: 原型构建与UI实现
```

---

## 八、形式化推理链

**推理命题 P**: Style Dictionary 的变换管道 ⟨𝓕, ∘, id⟩ 构成了设计令牌到多平台产物的同态映射，但其单向性导致了设计-代码双向同步的理论不可解性。

**推理链**:

```text
前提 A1 (Danny Banks, 2019): "Style Dictionary is a build system that allows you to
                               define styles once, in a way for any platform or language
                               to consume. A single source of truth for design tokens."
前提 A2 (Jan Six, 2022): "Tokens Studio bridges the gap between design tools and code.
                            It allows designers to manage design tokens in Figma and sync
                            them with a Git repository."
前提 A3 (Brad Frost, 2019): "A design system is a product serving products. The workflow
                               from design to code is not a handoff but a continuous
                               collaboration."

步骤 1: 由 A1，Style Dictionary 变换管道的代数结构
       设变换集合 𝓕，复合运算 ∘:
         Pipeline = Parse ∘ Transform ∘ Format ∘ Action
       验证幺半群性质:
         封闭性: Parse∘Transform 仍是合法变换
         结合律: (Parse∘Transform)∘Format = Parse∘(Transform∘Format)
         单位元: id(t) = t
       ∴ ⟨𝓕, ∘, id⟩ 构成幺半群
       该结构保证了复杂转换的可维护性——每个变换只负责单一语义

步骤 2: 设计-代码映射的形式化模型
       转换函数: Transform: Design → Code
       一致性谓词: Consistent(d,c) ⟺ Visual(d) ≈ Visual(Render(c))
       问题: Visual(·) 和 Render(·) 都是不可计算的近似函数
         - Visual(d): Figma 的渲染引擎 (封闭系统)
         - Render(c): 浏览器/原生平台的渲染引擎 (异构系统)
       ∴ 完美一致性 Consistent(d,c) = true 在实践中不可判定

步骤 3: 由 A2-A3，双向同步的不可能性
       理想同步: ∀t, D(t) ≈ C(t)
       单向同步: C(t+1) = Sync(D(t+1)) (Design → Code)
       双向同步:
         D(t+1) = Merge(D(t), CodeToDesign(C(t)))
         C(t+1) = Merge(C(t), DesignToCode(D(t)))
       冲突类型:
         1. 设计端修改令牌值，代码端也修改同一令牌
         2. 设计端新增令牌，代码端删除相关组件
         3. 设计端删除组件，代码端仍在引用
       形式化: 双向同步需要三路合并函数 Merge: D × C × Base → (D', C')
       但 Design 和 Code 的语义空间不同构，不存在通用的 Merge 算法
       ∴ 双向同步的冲突消解需要人类设计师介入 (不可完全自动化)

步骤 4: 量化误差的工程意义
       Figma 设计空间: 连续 (设计师可调 7.5px 圆角)
       Token 代码空间: 离散 (4px, 8px, 16px 阶梯)
       量化函数: Quantize: ℝ → Discrete
       误差: ε = |x - Quantize(x)|
       该误差不是缺陷，而是"一致性约束"的工程体现:
         离散化强制了视觉一致性，但限制了设计自由度
       最优策略: "结构化但不僵化"——80% 令牌化，20% 自由裁量

步骤 5: AI 辅助代码生成的形式化风险
       设 AI 生成函数: Generate: FigmaComponent → Code
       风险:
         1. 正确性: Generate(c) 是否满足 Consistent(c, Generate(c))?
         2. 可维护性: 生成代码是否符合团队的编码规范?
         3. 可访问性: 生成的 ARIA 属性是否满足 WCAG 约束?
       形式化验证需求: ∀c, Verify(Generate(c)) = PASS
       当前状态: 无此类通用验证器存在

结论: 设计系统工作流的核心矛盾是"视觉语义的连续性"与"代码表示的离散性"之间的
       映射难题。Style Dictionary 的幺半群结构保证了单向转换的可维护性，但双向
       同步在理论上不可完全自动化。未来的突破可能在于"AI辅助生成 + 形式化验证"
       的混合模式，但这要求建立从设计语义到代码语义的完备形式化规范——这正是
       本文件代数结构（群、幺半群、同态）所奠定的基础。
```

---

## 九、推理判定树/决策树

```text
设计-代码工作流工具选型决策树
│
├─► Q1: 团队规模与协作模式?
│   ├─ 小型 (<5人)，设计开发一人兼顾 ──→ Figma Variables + 手动导出 CSS
│   └─ 中大型 (≥5人)，设计与开发分离 ──→ 继续 Q2
│
├─► Q2: 令牌管理主导方?
│   ├─ 设计主导 ──→ Tokens Studio (Figma插件) + Git同步
│   ├─ 开发主导 ──→ Style Dictionary + 代码优先工作流
│   └─ 共同维护 ──→ Figma Variables ↔ Style Dictionary 双向管道
│
├─► Q3: 多平台输出需求?
│   ├─ Web only ──→ Style Dictionary CSS + Tailwind 配置集成
│   ├─ Web + Mobile ──→ Style Dictionary 全平台 (CSS / Swift / XML)
│   └─ 全平台 (含Flutter/Desktop) ──→ Style Dictionary v3+ 或 Specify/Supernova
│
├─► Q4: 运行时主题切换?
│   ├─ 是 ──→ CSS Custom Properties (原生) 或 CSS-in-JS (动态注入)
│   └─ 否 ──→ 编译时主题 (Sass/Less 变量 或 Style Dictionary 多主题构建)
│
├─► Q5: 组件代码生成需求?
│   ├─ 是 (Figma设计稿自动生成代码) ──→ Supernova / Specify / Cobra
│   └─ 否 (仅样式令牌) ──→ Style Dictionary + 手动组件实现
│
└─► Q6: CI/CD 自动化?
    ├─ GitHub Actions ──→ Figma webhook → 令牌构建 → 视觉回归 → PR 自动创建
    ├─ 其他 CI ──→ 类似管道，适配对应 CI 语法
    └─ 无 CI ──→ 手动触发 Style Dictionary 构建 + 人工验证

设计-代码一致性诊断决策树
│
├─► 症状: 代码实现与设计稿视觉不一致
│   ├─► Q1: 令牌值是否同步?
│   │   ├─ 否 ──→ 检查 Figma Variables / Tokens Studio 同步状态，重新导出
│   │   └─ 是 ──→ 继续 Q2
│   │
│   ├─► Q2: 平台渲染差异?
│   │   ├─ 是 (iOS/Android 与 Web 字体/颜色空间差异) ──→ 平台特定变换 (transform)
│   │   └─ 否 ──→ 继续 Q3
│   │
│   └─► Q3: 设计稿是否使用离散令牌?
│       ├─ 否 (设计师用了任意值) ──→ 量化误差，需设计师回归令牌系统
│       └─ 是 ──→ 检查 Style Dictionary 变换规则是否有误
│
├─► 症状: 双向同步冲突
│   ├─► Q1: 冲突层面?
│   │   ├─ 令牌值 ──→ 人工裁决，优先代码端 (运行时可靠性) 或设计端 (视觉权威)
│   │   ├─ 组件结构 ──→ 通常以代码端为准，设计端适配
│   │   └─ 删除/新增 ──→ 检查引用关系，避免破坏下游消费者
│   │
│   └─► Q2: 冲突频率?
│       ├─ 高频 ──→ 建立"设计评审→令牌锁定→开发实现"的串行工作流
│       └─ 低频 ──→ 个案处理，维持现有协作模式
│
└─► 症状: AI生成代码质量差
    ├─► Q1: 是否符合设计规范?
    │   ├─ 否 ──→ 调整 AI 提示词或训练数据，加入设计系统约束
    │   └─ 是 ──→ 继续 Q2
    │
    └─► Q2: 是否满足可访问性?
        ├─ 否 ──→ 人工审查 ARIA 属性，集成 axe-core 自动化检测
        └─ 是 ──→ 检查性能 (生成的代码可能存在冗余渲染)
```

---

## 十、国际课程对齐标注

> **📚 Stanford CS 247 Human-Computer Interaction Design Studio**
>
> - **对齐章节**: §2.1 设计工作流的形式化模型, §2.2 Style Dictionary 变换代数, §5.1 Style Dictionary 完整配置
> - **课程要点**: "Project-based course on interaction design: needs analysis, sketching,
>   prototyping, and evaluation. Tools: Figma, design systems, and rapid iteration."
> - **深度映射**: CS247 的设计工作室大量使用 Figma 进行原型设计和设计系统构建。
>   本文件将 Figma-to-Code 工作流形式化为 𝓦 = ⟨Design, Transform, Code, Validate, Deploy⟩，
>   为 CS247 学生从"设计原型"到"工程实现"的过渡提供了系统化框架。课程中关于
>   "设计工具选择"的讨论与本文件 Style Dictionary / Tokens Studio / Supernova 的
>   对比矩阵直接对应。CS247 强调"快速迭代"，本文件的 CI/CD 自动化管道（Figma webhook
>   → GitHub Actions → 视觉回归）正是迭代流程的工程化实现。

> **📚 MIT 6.831 User Interface Design and Implementation**
>
> - **对齐章节**: §2.3 双向同步的形式化, §六 批判性总结, §5.4 Figma→React 代码生成
> - **课程要点**: "Implementation techniques: low-fidelity prototypes, toolkits, and
>   programming projects. Evaluation: heuristic evaluation, user testing."
> - **深度映射**: MIT 6.831 的实现模块涵盖从低保真原型到可运行界面的完整流程。
>   本文件将这一流程扩展到设计系统级别：Figma 中的 Variables/Components 对应
>   6.831 中的"低保真原型"，Style Dictionary 的变换管道对应"工具包"(Toolkit)，
>   组件库的实现对应"编程项目"。课程中关于"原型保真度"的讨论与本文件
>   "视觉语义连续性与代码离散性"的批判性总结形成深层呼应——两者都指出
>   设计工具与实现平台之间的"表示鸿沟"是 UI 工程的核心挑战。
