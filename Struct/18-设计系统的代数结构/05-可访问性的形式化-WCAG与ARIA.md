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
