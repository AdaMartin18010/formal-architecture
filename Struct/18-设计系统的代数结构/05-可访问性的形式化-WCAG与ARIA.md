# 可访问性的形式化：WCAG 与 ARIA

> **来源映射**: View/05.md §6.5
> **国际权威参考**: WCAG 2.1 (W3C, 2018), WCAG 2.2 (W3C, 2023), WAI-ARIA 1.2 (W3C), "Accessibility for Everyone" (Laura Kalbag, 2017), "Inclusive Design Patterns" (Heydon Pickering, 2016), "A Web for Everyone" (Sarah Horton & Whitney Quesenbery), axe-core Docs (Deque)

---

## 一、知识体系思维导图

```text
可访问性的形式化：WCAG 与 ARIA
│
├─► WCAG (Web Content Accessibility Guidelines)
│   ├─► 四大原则 (POUR)
│   │   ├─ Perceivable (可感知): 信息必须以用户可感知的方式呈现
│   │   ├─ Operable (可操作): 界面组件必须可操作和可导航
│   │   ├─ Understandable (可理解): 信息和操作必须可理解
│   │   └─ Robust (健壮性): 内容必须可被辅助技术可靠解析
│   │
│   ├─► 合规等级
│   │   ├─ Level A: 最低可访问性 (必须满足)
│   │   ├─ Level AA: 推荐标准 (多数法规要求)
│   │   └─ Level AAA: 最高标准 (理想目标)
│   │
│   └─► 关键成功准则
│       ├─ 1.4.3 对比度: 文本与背景的最小对比度
│       ├─ 1.4.11 非文本对比度: UI 组件和图形的对比度
│       ├─ 2.1.1 键盘: 所有功能必须可通过键盘操作
│       ├─ 2.4.7 焦点可见: 键盘焦点指示器可见
│       ├─ 4.1.2 名称/角色/值: 组件状态必须可编程确定
│       └─ (WCAG 2.2 新增) 2.5.8 目标尺寸最小 24×24 CSS px
│
├─► ARIA (Accessible Rich Internet Applications)
│   ├─ 角色 (Roles): 定义组件的语义 (button, navigation, dialog)
│   ├─ 属性 (Properties): 定义组件特征 (aria-required, aria-orientation)
│   ├─ 状态 (States): 定义动态条件 (aria-expanded, aria-selected)
│   └─ 可访问性树: DOM + ARIA → 辅助技术可解析的树
│
├─► 形式化模型
│   ├─ 可访问性作为约束系统
│   ├─ 色彩对比度的数学公式
│   ├─ 焦点管理的图论模型
│   └─ 屏幕阅读器通知的形式化时序
│
└─► 自动化测试
    ├─ axe-core: 可访问性规则引擎
    ├─ Lighthouse: 集成可访问性审计
    ├─ Storybook a11y addon: 组件级测试
    └─ 手动测试: 屏幕阅读器 (NVDA/JAWS/VoiceOver)
```

---

## 二、核心概念的形式化定义

### 2.1 WCAG 合规的形式化

```text
定义 (WCAG 合规系统):
  设网页内容 C，用户能力集合 U = {visual, auditory, motor, cognitive}

  可访问性谓词:
    Accessible(C, u) ⟺ C 满足用户能力 u 下的所有相关成功准则

  WCAG 等级:
    Level A:   ∀u ∈ U, C 满足 Level A 的所有成功准则
    Level AA:  ∀u ∈ U, C 满足 Level A ∧ Level AA 的所有成功准则
    Level AAA: ∀u ∈ U, C 满足 Level A ∧ Level AA ∧ Level AAA 的所有成功准则

  形式化约束:
    设 SC 为所有成功准则的集合，每个准则 sc ∈ SC 有验证函数:
      Verify_sc: C → {PASS, FAIL, NA}

    Compliance(Level) = ⋀_{sc ∈ Level} Verify_sc(C) ∈ {PASS, NA}

    即: 对于该等级的所有准则，验证结果必须为通过或不适用
```

### 2.2 色彩对比度的数学模型

```text
定义 (相对亮度与对比度):
  对于 sRGB 颜色 (R, G, B)，归一化到 [0, 1]:
    R_s = R_8bit / 255,  G_s = G_8bit / 255,  B_s = B_8bit / 255

  伽马校正:
    若 R_s ≤ 0.03928: R_lin = R_s / 12.92
    否则: R_lin = ((R_s + 0.055) / 1.055)^2.4

    (G_lin, B_lin 同理)

  相对亮度:
    L = 0.2126 × R_lin + 0.7152 × G_lin + 0.0722 × B_lin

  对比度比:
    CR(L₁, L₂) = (L₁ + 0.05) / (L₂ + 0.05)
    其中 L₁ ≥ L₂ (即 L₁ 为较亮颜色)

  WCAG 阈值:
    常规文本 (18pt 或 14pt bold 以下):
      Level AA: CR ≥ 4.5:1
      Level AAA: CR ≥ 7:1

    大文本 (18pt+ 或 14pt bold+):
      Level AA: CR ≥ 3:1
      Level AAA: CR ≥ 4.5:1

    非文本元素 (UI 组件、图形):
      Level AA: CR ≥ 3:1 (1.4.11)
```

### 2.3 焦点管理的图论模型

```text
定义 (焦点导航图):
  设可聚焦元素集合 F = {f₁, f₂, ..., fₙ}

  焦点导航图 G_focus = (F, E_focus)

  E_focus 的构成:
    1. Tab 顺序边: (fᵢ, fⱼ) 若按 Tab 键从 fᵢ 导航到 fⱼ
    2. 箭头键边: 对于复合组件 (如 grid, toolbar)，
       方向键导航构成额外的边
    3. 焦点陷阱边: 模态框内的循环焦点 (f_last → f_first)

  可访问性约束:
    1. 连通性: G_focus 必须是强连通的 (从任意焦点可达任意焦点)
       例外: 模态框内的焦点应限制在模态内 (焦点陷阱)

    2. 无死胡同: ∀f ∈ F, outdegree(f) ≥ 1 (Tab 顺序无断点)

    3. DOM 顺序一致性:
       Tab 顺序应与视觉顺序和 DOM 顺序一致
       (除非显式使用 tabindex 覆盖)

  焦点顺序函数:
    FocusOrder: F → {1, 2, ..., |F|}
    要求: FocusOrder 是 G_focus 拓扑排序的一个实例
```

### 2.4 ARIA 可访问性树

```text
定义 (可访问性树):
  设 DOM 树 T_DOM = (N_DOM, E_DOM)

  可访问性树 T_a11y = (N_a11y, E_a11y) 是 T_DOM 的语义投影:
    N_a11y = {n ∈ N_DOM | n 是语义节点 (有 role 或可访问名称)}
    E_a11y ⊆ E_DOM 的传递归约

  节点属性:
    Role(n): 元素语义角色 (button, heading, listitem)
    Name(n): 可访问名称 (aria-label, aria-labelledby, 文本内容)
    State(n): 动态状态 (aria-checked, aria-expanded, aria-selected)
    Value(n): 当前值 (input 的值, progress 的进度)

  辅助技术通过遍历 T_a11y (而非 T_DOM) 向用户呈现内容
```

---

## 三、多维矩阵对比

### 3.1 WCAG 等级要求矩阵

| 成功准则 | Level A | Level AA | Level AAA | 类型 | 自动检测 |
|---------|---------|----------|-----------|------|---------|
| **1.1.1 非文本内容替代** | ✅ | ✅ | ✅ | 文本 | ⚠️ 部分 |
| **1.4.3 文本对比度 (4.5:1)** | - | ✅ | ✅ | 视觉 | ✅ |
| **1.4.6 文本对比度 (7:1)** | - | - | ✅ | 视觉 | ✅ |
| **1.4.11 非文本对比度 (3:1)** | - | ✅ | ✅ | 视觉 | ⚠️ 部分 |
| **2.1.1 键盘可操作** | ✅ | ✅ | ✅ | 交互 | ❌ |
| **2.4.7 焦点可见** | - | ✅ | ✅ | 交互 | ⚠️ 部分 |
| **2.5.5 目标尺寸 (44×44)** | - | - | ✅ | 交互 | ✅ |
| **2.5.8 目标尺寸 (24×24)** | - | ✅ | - | 交互 | ✅ |
| **3.1.5 阅读级别** | - | - | ✅ | 认知 | ❌ |
| **4.1.2 名称/角色/值** | ✅ | ✅ | ✅ | 语义 | ⚠️ 部分 |

### 3.2 可访问性测试工具对比

| 工具 | 规则引擎 | 浏览器集成 | CI/CD | 覆盖率 | 误报率 |
|------|---------|-----------|-------|--------|--------|
| **axe-core** | **最全面** | 插件+库 | ✅ | ~80% 可自动检测 | 低 |
| **Lighthouse** | 基于 axe | DevTools | ✅ | ~60% | 中 |
| **WAVE** | 独立规则 | 插件 | ❌ | ~50% | 中 |
| **Pa11y** | 基于 axe/HTML_CodeSniffer | CLI | ✅ | ~70% | 低 |
| **Storybook a11y** | axe-core | Storybook | ⚠️ 手动 | 组件级 | 低 |
| **NVDA/JAWS** | 真实屏幕阅读器 | 桌面 | ❌ | 100% (人工) | 无 |

---

## 四、权威引用

> **W3C WCAG 2.1** (Recommendation, 2018):
> "Web Content Accessibility Guidelines (WCAG) 2.1 covers a wide range of recommendations for making Web content more accessible. Following these guidelines will make content accessible to a wider range of people with disabilities."

> **W3C WAI-ARIA 1.2** (Recommendation, 2023):
> "Accessible Rich Internet Applications (WAI-ARIA) 1.2 provides an ontology of roles, states, and properties that define accessible user interface elements."

> **Deque Systems** (axe-core Documentation):
> "Accessibility rules are based on a combination of WCAG success criteria, best practices, and industry standards. axe-core can catch approximately 80% of accessibility issues automatically."

> **Laura Kalbag** ("Accessibility for Everyone", 2017):
> "Accessibility is not a feature. It's a fundamental quality of how we build the web. When we make our websites accessible, we don't just help people with disabilities—we make the web better for everyone."

---

## 五、工程实践与代码示例

### 5.1 色彩对比度计算与验证

```typescript
// WCAG 对比度计算
function getLuminance(r: number, g: number, b: number): number {
  const [rs, gs, bs] = [r, g, b].map(c => {
    c = c / 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}

function getContrastRatio(hex1: string, hex2: string): number {
  const rgb1 = hexToRgb(hex1);
  const rgb2 = hexToRgb(hex2);
  const lum1 = getLuminance(rgb1.r, rgb1.g, rgb1.b);
  const lum2 = getLuminance(rgb2.r, rgb2.g, rgb2.b);
  const lighter = Math.max(lum1, lum2);
  const darker = Math.min(lum1, lum2);
  return (lighter + 0.05) / (darker + 0.05);
}

// 验证设计令牌
const primaryColor = '#3B82F6';  // blue-500
const bgColor = '#FFFFFF';
const ratio = getContrastRatio(primaryColor, bgColor);  // 3.98
// Level AA 需要 4.5:1 → 不满足，需调整为 blue-600 (#2563EB, ratio ≈ 5.4)
```

### 5.2 ARIA 角色与属性的正确使用

```tsx
// ✅ 正确的 ARIA 实现
function Accordion({ items }: { items: { title: string; content: string }[] }) {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  return (
    <div className="accordion">
      {items.map((item, index) => (
        <div key={index} className="accordion-item">
          <button
            className="accordion-trigger"
            onClick={() => setOpenIndex(openIndex === index ? null : index)}
            aria-expanded={openIndex === index}
            aria-controls={`panel-${index}`}
            id={`trigger-${index}`}
          >
            {item.title}
            <span aria-hidden="true">{openIndex === index ? '−' : '+'}</span>
          </button>
          <div
            id={`panel-${index}`}
            role="region"
            aria-labelledby={`trigger-${index}`}
            hidden={openIndex !== index}
          >
            {item.content}
          </div>
        </div>
      ))}
    </div>
  );
}
```

### 5.3 焦点陷阱 (Focus Trap) 实现

```typescript
// 模态框焦点管理
function useFocusTrap(isActive: boolean, containerRef: RefObject<HTMLElement>) {
  useEffect(() => {
    if (!isActive || !containerRef.current) return;

    const container = containerRef.current;
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey && document.activeElement === firstElement) {
        lastElement.focus();
        e.preventDefault();
      } else if (!e.shiftKey && document.activeElement === lastElement) {
        firstElement.focus();
        e.preventDefault();
      }
    };

    container.addEventListener('keydown', handleTabKey);
    firstElement?.focus();  // 初始焦点

    return () => container.removeEventListener('keydown', handleTabKey);
  }, [isActive, containerRef]);
}
```

### 5.4 axe-core 自动化测试

```typescript
// jest + axe 测试示例
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { Button } from './Button';

expect.extend(toHaveNoViolations);

describe('Button Accessibility', () => {
  it('should have no accessibility violations', async () => {
    const { container } = render(<Button>Click me</Button>);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have proper contrast for primary variant', async () => {
    const { container } = render(<Button variant="primary">Submit</Button>);
    const results = await axe(container, {
      rules: {
        'color-contrast': { enabled: true }
      }
    });
    expect(results).toHaveNoViolations();
  });
});
```

---

## 六、批判性总结

可访问性的形式化揭示了一个常被忽视的真理：**可访问性不是用户体验的"附加功能"，而是交互系统的逻辑完备性要求**。WCAG 的四大原则（POUR）可以映射到形式化系统的四个基本属性：可感知性对应**输出的完全性**（所有信息都有可感知的表示），可操作性对应**状态的可迁移性**（从任意状态可达目标状态），可理解性对应**语言的良构性**（用户心智模型与系统语义一致），健壮性对应**规范的兼容性**（系统行为可被标准接口解析）。这种映射表明，可访问性缺陷本质上是**系统设计的形式化不完备**——正如类型系统捕获程序的逻辑错误，可访问性准则捕获人机交互的逻辑漏洞。

WCAG 对比度公式的数学严谨性是其最具形式化美感的部分。相对亮度公式基于 CIE 色彩空间的感知均匀性假设，通过伽马校正将 sRGB 的非线性编码转换为线性光度，再以 4.5:1 和 7:1 的阈值划分 AA/AAA 等级。这些阈值并非随意设定，而是基于**低视力用户的对比敏感度函数（CSF）**的统计研究结果——在典型显示条件下，4.5:1 的对比度保证了 80% 的低视力用户可辨识文本。然而，公式也有局限：它仅适用于 sRGB 色域，对 HDR 显示器的宽色域内容（Display P3、Rec. 2020）的适用性尚存争议。

ARIA 的可访问性树模型是 DOM 的**语义投影**，它将视觉丰富的网页抽象为辅助技术可遍历的结构化树。但这一投影的复杂性常被低估：当开发者滥用 `div` + `role="button"` 替代原生 `<button>` 时，他们不仅需要手动添加 role、tabindex、键盘事件处理器，还需要维护焦点状态、激活状态和无障碍名称——这些功能在原生元素中是**免费获得的语义完备性**。这揭示了一个工程原则：**优先使用原生语义元素，ARIA 仅作为补充而非替代**。形式化地看，原生 HTML 元素是交互语义空间中的"基本向量"，而 ARIA 是用于构造复合语义的"生成函数"——用基本向量直接表达总是比通过生成函数间接构造更可靠、更简洁。


---

## 七、概念属性关系网络

```text
可访问性形式化概念属性关系网络
│
├─► 核心实体层
│   ├─ [WCAG 合规系统]
│   │   ├─ POUR原则 ──→ 属性: {Perceivable, Operable, Understandable, Robust}
│   │   ├─ 等级 L∈{A,AA,AAA} ──→ 属性: {覆盖准则数, 合规阈值, 法规要求}
│   │   └─ 成功准则 SC ──→ 属性: {验证函数, 自动检测率, 适用内容类型}
│   │
│   ├─ [色彩对比度 CR(L₁,L₂)]
│   │   ├─ 相对亮度 ──→ 属性: {sRGB归一化, 伽马校正, CIE线性光度}
│   │   ├─ 对比度比 ──→ 属性: {数学公式, WCAG阈值, 感知均匀性}
│   │   └─ 阈值矩阵 ──→ 属性: {常规文本4.5:1, 大文本3:1, 非文本3:1}
│   │
│   ├─ [焦点导航图 G_focus = (F, E_focus)]
│   │   ├─ F ──→ 属性: {可聚焦元素, Tab索引, 交互控件}
│   │   ├─ E_focus ──→ 属性: {Tab边, 箭头键边, 焦点陷阱边}
│   │   └─ 约束 ──→ 属性: {连通性, 无死胡同, DOM顺序一致性}
│   │
│   └─ [可访问性树 T_a11y = (N_a11y, E_a11y)]
│       ├─ N_a11y ──→ 属性: {语义节点, role, name, state, value}
│       ├─ E_a11y ──→ 属性: {父子关系, 层级结构, 可见性}
│       └─ 投影 ──→ 属性: {DOM→语义投影, 辅助技术遍历, 信息缩减}
│
├─► 关系映射层
│   ├─ DOM → T_a11y: DOM树通过ARIA语义投影为可访问性树
│   ├─ T_a11y → AT: 辅助技术遍历可访问性树呈现内容
│   ├─ Color → CR: 颜色值映射到对比度比
│   ├─ CR → WCAG: 对比度比判定合规等级
│   ├─ G_focus → FocusOrder: 焦点图拓扑排序决定Tab顺序
│   └─ axe-core → SC: 规则引擎映射到成功准则验证
│
├─► 属性约束层
│   ├─ 合规: Compliance(Level) = ⋀_{sc∈Level} Verify_sc(C) ∈ {PASS, NA}
│   ├─ 对比度: CR(L₁,L₂) ≥ 4.5:1 (AA级常规文本)
│   ├─ 焦点连通: G_focus 强连通 (模态框内焦点陷阱除外)
│   ├─ 语义完备: 交互元素必须具有 {role, name, state} 三要素
│   └─ 树投影: T_a11y 是 T_DOM 的语义归约 (保留交互语义，去除装饰)
│
└─► 课程对齐层
    ├─ Stanford CS 247: 包容性设计与伦理
    └─ MIT 6.831: 可访问性 (Lecture 18)
```

---

## 八、形式化推理链

**推理命题 P**: 可访问性不是用户体验的"附加功能"，而是交互系统的逻辑完备性要求——WCAG 的 POUR 原则对应形式化系统的输出完全性、状态可迁移性、语言良构性和规范兼容性。

**推理链**:

```text
前提 A1 (W3C WCAG 2.1, 2018): "Web Content Accessibility Guidelines cover a wide range
                                 of recommendations for making Web content more accessible.
                                 Following these guidelines will make content accessible to
                                 a wider range of people with disabilities."
前提 A2 (Deque Systems, axe-core): "Accessibility rules are based on a combination of
                                     WCAG success criteria, best practices, and industry
                                     standards. axe-core can catch approximately 80% of
                                     accessibility issues automatically."
前提 A3 (Laura Kalbag, 2017): "Accessibility is not a feature. It's a fundamental quality
                                of how we build the web. When we make our websites accessible,
                                we don't just help people with disabilities—we make the web
                                better for everyone."

步骤 1: WCAG 四大原则的形式化映射
       设交互系统为状态机 M = (S, I, O, δ)
       Perceivable (可感知) ⟺ 输出完全性:
         ∀o∈O, ∃表示函数 repr: o → 感知通道 (视觉/听觉/触觉)
         即: 所有信息都必须有至少一种可感知的表示
       Operable (可操作) ⟺ 状态可迁移性:
         ∀s₁,s₂∈S, 若 s₂ 可达，则 ∃输入序列 i₁...iₙ, δ*(s₁, i₁...iₙ) = s₂
         即: 从任意状态可达目标状态 (键盘导航、焦点管理)
       Understandable (可理解) ⟺ 语言良构性:
         用户心智模型 ≈ 系统语义模型
         即: 界面语言符合用户期望 (一致的导航、错误预防)
       Robust (健壮性) ⟺ 规范兼容性:
         系统行为可被标准接口 (ARIA, HTML语义) 完整解析
         即: 辅助技术能可靠地理解和操作界面

步骤 2: 对比度公式的感知基础
       相对亮度公式:
         L = 0.2126×R_lin + 0.7152×G_lin + 0.0722×B_lin
       系数来源: CIE 色彩匹配的视见函数 (luminous efficiency function)
       伽马校正: sRGB 的非线性编码 → 线性光度 (模拟人眼对暗部敏感)
       对比度阈值:
         4.5:1 (AA级): 基于低视力用户的对比敏感度函数 (CSF) 统计
         保证 80% 的低视力用户在典型显示条件下可辨识文本
       ∴ WCAG 阈值不是随意设定，而是基于感知心理学的统计结果

步骤 3: 可访问性树的语义投影
       T_DOM = (N_DOM, E_DOM): DOM 完整树
       T_a11y = (N_a11y, E_a11y): 语义投影，其中
         N_a11y = {n∈N_DOM | n有role或可访问名称}
       该投影是信息缩减: |N_a11y| ≤ |N_DOM|
       关键性质: 投影必须保持交互语义
         若 n∈N_DOM 是交互元素，则 proj(n)∈N_a11y 必须保留
         {role, name, state, value} 四元组
       反例: <div role="button"> 丢失了原生 <button> 的默认键盘语义
         需手动补充: tabindex, Enter/Space 处理器, 焦点状态

步骤 4: 自动化检测的理论边界
       设所有可访问性缺陷集合为 Defects
       axe-core 自动检测集合为 Auto ⊆ Defects
       经验值: |Auto| / |Defects| ≈ 80%
       不可自动检测的 20% 包括:
         - 交互逻辑正确性 (键盘导航是否 intuitive)
         - 内容可理解性 (文本是否 plain language)
         - 上下文语义 (aria-describedby 指向的内容是否有意义)
       形式化: 这些缺陷涉及"意义"(meaning) 而非"结构"(structure)，
               而意义的判定在计算上是不可判定的
       ∴ 完全自动化不可达，人工测试 (NVDA/JAWS/VoiceOver) 不可替代

步骤 5: ARIA 滥用与原生语义完备性
       原生 HTML 元素是交互语义空间中的"基本向量"
         <button>: {role=button, name=文本内容, keyboard=Enter/Space, focusable=true}
       ARIA 是构造复合语义的"生成函数"
         <div role="button">: 需手动定义所有上述属性
       形式化: 使用生成函数间接构造总是比使用基本向量直接表达更不可靠
       工程原则: 优先使用原生语义元素，ARIA 仅作为补充

结论: 可访问性的形式化揭示了深层规律：WCAG 准则不是"最佳实践清单"，
       而是交互系统逻辑完备性的必要条件。对比度公式基于感知心理学，
       焦点管理基于图论，可访问性树基于语义投影——三者共同构成了
       人机交互的"形式化验证框架"。未来的设计系统应将可访问性验证
       内建于构建流程（如 axe-core CI 集成），使合规性从"事后检查"
       变为"构造即正确"。
```

---

## 九、推理判定树/决策树

```text
WCAG 合规等级选择决策树
│
├─► Q1: 目标市场法规要求?
│   ├─ 美国 (ADA/Section 508) ──→ Level AA (最低合规)
│   ├─ 欧盟 (EAA/EN 301 549) ──→ Level AA (2025年起强制)
│   ├─ 政府/教育 ──→ Level AA 或 AAA (取决于机构政策)
│   └─ 无特定法规 ──→ 继续 Q2
│
├─► Q2: 用户群体特征?
│   ├─ 高比例残障用户 (如康复医疗、辅助技术) ──→ Level AAA
│   ├─ 一般公众 ──→ Level AA (推荐标准)
│   └─ 内部工具 (可控用户群) ──→ Level A + 关键 AA 准则
│
├─► Q3: 资源投入?
│   ├─ 充足 (专职 a11y 团队) ──→ 目标 AAA，逐步推进
│   └─ 有限 ──→ 优先 AA，聚焦关键用户流程
│
└─► Q4: 验证策略?
    ├─ 自动化为主 ──→ axe-core + Lighthouse CI (覆盖 ~80% 可自动检测)
    ├─ 自动化 + 人工审计 ──→ 每季度专业 a11y 审计 (Deque/WCAG-EM)
    └─ 全面覆盖 ──→ 自动化 + 专家审计 + 真实用户测试 (残障用户参与)

组件可访问性实现决策树
│
├─► Q1: 是否使用原生 HTML 元素?
│   ├─ 是 (button, a, input, select) ──→ 免费获得语义完备性，补充 aria-label 若文本不足
│   └─ 否 (div/span 自定义组件) ──→ 继续 Q2
│
├─► Q2: 自定义组件的交互类型?
│   ├─ 按钮 ──→ role="button", tabindex="0", Enter/Space 事件, focus 样式
│   ├─ 链接 ──→ role="link", tabindex="0", Enter 事件, href 或键盘导航
│   ├─ 输入框 ──→ 使用原生 <input> 或 role="textbox", aria-label, aria-describedby
│   ├─ 选择器 ──→ role="listbox" / "combobox", aria-expanded, aria-selected, 方向键导航
│   ├─ 对话框 ──→ role="dialog", aria-modal, 焦点陷阱, Escape 关闭
│   ├─ 标签页 ──→ role="tablist"/"tab"/"tabpanel", 方向键切换, aria-selected
│   └─ 手风琴 ──→ role="button" + aria-expanded + aria-controls + 面板 region
│
├─► Q3: 色彩对比度是否满足?
│   ├─ 是 (CR ≥ 4.5:1 常规文本) ──→ 通过
│   └─ 否 ──→ 调整颜色值，或使用对比度增强模式 (高对比度主题)
│
├─► Q4: 焦点管理?
│   ├─ 可见焦点环 (:focus-visible) ──→ 确保所有交互元素有清晰的焦点指示
│   ├─ Tab 顺序 ──→ 与 DOM 顺序/视觉顺序一致
│   └─ 焦点陷阱 ──→ 模态框内循环 (Shift+Tab 在首元素循环到末元素)
│
└─► Q5: 自动化测试覆盖?
    ├─ jest-axe (组件级单元测试)
    ├─ Cypress + axe-core (E2E 流程测试)
    └─ Storybook a11y addon (设计系统组件库级测试)
```

---

## 十、国际课程对齐标注

> **📚 Stanford CS 247 Human-Computer Interaction Design Studio**
>
> - **对齐章节**: §2.1 WCAG 合规的形式化, §2.2 色彩对比度的数学模型, §5.1 色彩对比度计算与验证
> - **课程要点**: "Examining the ethical consequences of design decisions and exploring
>   current issues arising from unintended consequences. Inclusive design for diverse users."
> - **深度映射**: CS247 的设计工作室强调"包容性设计"(Inclusive Design)和"伦理后果"，
>   与本文件将可访问性视为"交互系统逻辑完备性"的观点深度一致。课程中关于
>   "为多样化用户设计"的讨论对应本文件 WCAG 的 POUR 原则形式化映射——Perceivable
>   对应视觉/听觉通道设计，Operable 对应交互流程的键盘可达性。CS247 中"快速原型"
>   阶段的本文件 axe-core 自动化测试建议，确保原型从早期就满足可访问性约束。

> **📚 MIT 6.831 User Interface Design and Implementation**
>
> - **对齐章节**: §2.3 焦点管理的图论模型, §2.4 ARIA 可访问性树, §5.3 焦点陷阱实现, §六 批判性总结
> - **课程要点**: "Lecture 18: Accessibility. Human capabilities: perception, motor skills,
>   color vision, attention, and human error."
> - **深度映射**: MIT 6.831 的第18讲专门讲授可访问性，内容涵盖人类能力（感知、运动技能、
>   色觉）与界面设计的关联。本文件将这些生理基础转化为数学模型：对比度公式基于
>   CIE 视见函数和对比敏感度函数；焦点管理建模为有向图 G_focus = (F, E_focus)；
>   可访问性树是 DOM 的语义投影。课程中关于"人类信息处理器模型"(Human Information
>   Processor) 的讨论与本文件"输出完全性"(Perceivable) 的形式化定义同构——两者都
>   从人类认知和感知能力的限制出发，推导界面设计的约束条件。
