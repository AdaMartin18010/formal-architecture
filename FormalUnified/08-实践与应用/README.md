# FormalUnified 工具链使用指南

## 项目概述

FormalUnified 工具链是一个完整的形式化架构理论统一平台，集成了AI建模引擎、跨理论验证引擎、智能化分析平台等多个核心组件，为形式化架构理论的研究和应用提供全面的工具支持。

## 核心组件

### 1. 增强版AI建模引擎 (Enhanced AI Modeling Engine)

**位置**: `AI-Modeling-Engine/enhanced_prototype.py`

**功能特性**:

- 智能理论解析和概念提取
- 多语言代码生成 (Python, Rust, Go, TypeScript)
- 增强的验证引擎 (语法、语义、架构、安全、性能)
- 智能文档生成
- 可视化理论图谱

**使用示例**:

```python
from AI_Modeling_Engine.enhanced_prototype import EnhancedAIModelingEngine

# 初始化引擎
engine = EnhancedAIModelingEngine("config.yaml")

# 加载理论体系
engine.load_theory_system("FormalUnified")

# 生成架构模式
requirements = {
    "pattern_type": "state_machine",
    "components": ["状态管理器", "状态转换器"],
    "constraints": ["状态一致性", "转换原子性"]
}
pattern = engine.generate_architecture_pattern(requirements)

# 生成实现代码
implementation = engine.generate_implementation(pattern, "rust")

# 验证实现
verification = engine.verify_implementation(pattern, implementation)
```

### 2. 理论到实践映射工具 (Theory to Practice Mapping Tool)

**位置**: `TheoryToPractice/mapping_tool.py`

**功能特性**:

- 智能理论概念解析
- 多语言模板系统
- 约束验证和代码生成
- 测试用例自动生成

**使用示例**:

```python
from TheoryToPractice.mapping_tool import MappingEngine

# 初始化映射引擎
mapping_engine = MappingEngine()

# 解析理论内容
theory_content = """
# 状态机理论
## 状态定义
状态机包含有限个状态和状态转换规则
## 转换规则
每个转换都有前置条件和后置条件
"""

# 映射到实践
implementations = mapping_engine.map_theory_to_practice(theory_content, "rust")
```

### 3. 跨理论验证引擎 (Cross-Theory Verification Engine)

**位置**: `CrossTheoryVerificationEngine.py`

**功能特性**:

- 理论体系内部一致性验证
- 跨理论映射关系分析
- 智能映射强度计算
- 详细验证报告生成

**使用示例**:

```python
from CrossTheoryVerificationEngine import CrossTheoryVerificationEngine

# 初始化验证引擎
verification_engine = CrossTheoryVerificationEngine("config.yaml")

# 加载理论体系
verification_engine.load_theory_systems("FormalUnified")

# 验证理论一致性
verification_results = verification_engine.verify_theory_consistency()

# 分析跨理论映射
cross_mappings = verification_engine.analyze_cross_theory_mappings()

# 生成验证报告
report = verification_engine.generate_verification_report()
```

### 4. 智能化分析平台 (Intelligent Analysis Platform)

**位置**: `IntelligentAnalysisPlatform.py`

**功能特性**:

- 理论质量画像生成
- 智能洞察分析
- 协同机会识别
- 可视化分析报告

**使用示例**:

```python
from IntelligentAnalysisPlatform import IntelligentAnalysisPlatform

# 初始化分析平台
analysis_platform = IntelligentAnalysisPlatform("config.yaml")

# 加载理论体系
analysis_platform.load_theory_systems("FormalUnified")

# 生成质量画像
quality_profiles = analysis_platform.generate_quality_profiles()

# 生成智能洞察
insights = analysis_platform.generate_intelligent_insights()

# 导出分析报告
analysis_platform.export_analysis_report("analysis_output")
```

### 5. 统一运行脚本 (Unified Runner)

**位置**: `run_formal_unified.py`

**功能特性**:

- 整合所有工具的统一入口
- 支持完整分析和特定分析
- 自动生成汇总报告
- 命令行界面支持

**使用示例**:

```bash
# 运行完整分析
python run_formal_unified.py --analysis-type full --output results

# 运行验证分析
python run_formal_unified.py --analysis-type verification --output verification_results

# 运行质量分析
python run_formal_unified.py --analysis-type quality --output quality_results

# 运行AI建模分析
python run_formal_unified.py --analysis-type ai_modeling --target-language rust --requirements '{"pattern_type": "state_machine"}'

# 运行映射分析
python run_formal_unified.py --analysis-type mapping --target-language go --theory-content "状态机理论..."
```

## 配置文件

### 主配置文件: `config.yaml`

配置文件包含以下主要部分：

```yaml
# 项目基本信息
project:
  name: "形式化架构理论统一项目"
  version: "1.0.0"

# 理论体系配置
theory_systems:
  - name: "01-哲学基础理论"
    path: "FormalUnified/01-哲学基础理论"
    weight: 1.0

# AI建模引擎配置
ai_modeling_engine:
  enabled: true
  output_formats: ["python", "rust", "go", "typescript"]
  verification_levels: ["syntax", "semantics", "architecture"]

# 跨理论验证配置
cross_theory_verification:
  enabled: true
  min_confidence_threshold: 0.7

# 输出配置
output:
  base_directory: "output"
  formats: ["json", "yaml", "markdown"]
```

## 安装和依赖

### 系统要求

- Python 3.8+
- 支持的操作系统: Windows, macOS, Linux

### 依赖包

```bash
pip install pyyaml networkx matplotlib seaborn numpy
```

### 可选依赖

```bash
# 用于更好的可视化
pip install plotly bokeh

# 用于性能优化
pip install numba cython
```

## 使用流程

### 1. 快速开始

```bash
# 1. 克隆项目
git clone <repository-url>
cd formal-architecture/FormalUnified/08-实践与应用

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行完整分析
python run_formal_unified.py --analysis-type full --output results

# 4. 查看结果
ls results/
```

### 2. 分步骤使用

```python
# 1. 理论验证
from CrossTheoryVerificationEngine import CrossTheoryVerificationEngine
verification_engine = CrossTheoryVerificationEngine()
verification_engine.load_theory_systems()
results = verification_engine.verify_theory_consistency()

# 2. 质量分析
from IntelligentAnalysisPlatform import IntelligentAnalysisPlatform
analysis_platform = IntelligentAnalysisPlatform()
analysis_platform.load_theory_systems()
profiles = analysis_platform.generate_quality_profiles()

# 3. AI建模
from AI_Modeling_Engine.enhanced_prototype import EnhancedAIModelingEngine
ai_engine = EnhancedAIModelingEngine()
pattern = ai_engine.generate_architecture_pattern(requirements)
implementation = ai_engine.generate_implementation(pattern, "rust")
```

## 输出文件说明

### 验证结果

- `verification_output/verification_report.json`: 验证报告
- `verification_output/detailed_results.json`: 详细验证结果
- `verification_output/cross_theory_mappings.json`: 跨理论映射关系

### 分析结果

- `analysis_output/quality_analysis_report.json`: 质量分析报告
- `analysis_output/quality_radar_chart.png`: 质量雷达图
- `analysis_output/quality_comparison_chart.png`: 质量对比图

### 汇总报告

- `output/summary_report.md`: 汇总报告
- `output/full_analysis_results.json`: 完整分析结果

## 高级功能

### 1. 自定义验证规则

```python
# 在配置文件中添加自定义验证规则
verification_rules:
  custom_rules:
    - name: "概念命名规范"
      pattern: r'^[A-Z][a-zA-Z0-9_]*$'
      message: "概念名称应以大写字母开头"
```

### 2. 扩展AI建模模板

```python
# 添加新的架构模式模板
custom_templates = {
    "event_sourcing": {
        "components": ["事件存储", "事件处理器", "投影器"],
        "constraints": ["事件不可变性", "时间顺序性"]
    }
}
```

### 3. 自定义分析指标

```python
# 在分析平台中添加自定义指标
custom_metrics = {
    "complexity_score": lambda theory_data: calculate_complexity(theory_data),
    "maintainability_score": lambda theory_data: calculate_maintainability(theory_data)
}
```

## 故障排除

### 常见问题

1. **模块导入错误**

   ```text
   解决方案: 确保所有依赖包已正确安装，检查Python路径设置
   ```

2. **配置文件未找到**

   ```text
   解决方案: 检查config.yaml文件路径，或使用默认配置
   ```

3. **理论体系加载失败**

   ```text
   解决方案: 检查FormalUnified目录结构，确保Markdown文件存在
   ```

4. **可视化生成失败**

   ```text
   解决方案: 安装matplotlib和seaborn，检查中文字体设置
   ```

### 调试模式

```bash
# 启用详细日志
python run_formal_unified.py --analysis-type full --output results --debug

# 查看日志文件
tail -f formal_unified.log
```

## 贡献指南

### 开发环境设置

1. Fork项目仓库
2. 创建功能分支
3. 编写代码和测试
4. 提交Pull Request

### 代码规范

- 使用Python类型注解
- 遵循PEP 8代码风格
- 添加详细的文档字符串
- 编写单元测试

### 测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_ai_engine.py
```

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

- 项目主页: [GitHub Repository]
- 问题反馈: [Issues]
- 讨论交流: [Discussions]

---

*最后更新: 2024年12月*-
