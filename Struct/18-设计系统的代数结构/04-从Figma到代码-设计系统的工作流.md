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
