# FormalUnified

FormalUnified 是"形式化架构理论统一项目"的知识梳理与形式论证平台，专注于**形式论证和证明的知识梳理**，而非编程实现。项目包含九大理论体系的完整知识结构、形式化论证方法、理论验证框架，以及支持理论构建和验证的工具链。

## 项目核心定位

### 🎯 形式论证与证明的知识梳理项目

- **理论构建**：建立严格的形式化理论体系
- **逻辑论证**：提供完整的逻辑推理链条  
- **证明方法**：系统化各种证明技术和方法
- **知识结构**：优化知识组织和呈现方式

### 🔬 与编程项目的根本区别

| 编程项目特征 | 我们的项目特征 |
|-------------|---------------|
| 代码实现为主 | 理论论证为主 |
| 功能开发导向 | 知识梳理导向 |
| 技术栈选择 | 理论体系构建 |
| 性能优化 | 逻辑完整性 |
| 用户界面 | 知识结构 |

## 快速开始

- 运行综合演示（输出 `demo_report.json` 与 `demo_report.md`）

  ```bash
  python FormalUnified/08-实践与应用/comprehensive_demo.py
  ```

- 运行跨理论验证引擎（读取 `FormalUnified/08-实践与应用/config.yaml`）

  ```bash
  python FormalUnified/08-实践与应用/CrossTheoryVerificationEngine.py
  ```

- 查询理论到实践映射模板（只做映射选择，不直接生成代码）

  ```bash
  python FormalUnified/08-实践与应用/theory_to_practice_mapper.py --describe
  python FormalUnified/08-实践与应用/theory_to_practice_mapper.py --pattern state_machine --language rust
  ```

## 目录导航

- `01-哲学基础理论` ~ `09-索引与导航`：九大理论体系文档与导航
- `08-实践与应用/`：工具与运行脚本
  - `config.yaml`：统一配置
  - `comprehensive_demo.py`：综合演示
  - `CrossTheoryVerificationEngine.py`：跨理论验证
  - `UnifiedModelingTool.py`：统一建模工具（程序化API）
  - `visual_modeling_interface.py`：可视化建模界面（界面逻辑）
  - `automated_code_generator.py`：自动化代码生成器
  - `theory_to_practice_mapper.py`：理论到实践映射选择
  - `performance_benchmark_suite.py` / `advanced_performance_benchmark.py`：性能基准
  - `comprehensive_test_suite.py`：综合测试

## 一键演示与发布

- 发布准备报告位于 `FormalUnified/release/release_report.md`。
- 建议以 `Python 3.10+` 运行工具。首次运行请确保安装了依赖：

  ```bash
  pip install -r requirements.txt
  ```

## 备注

- 本仓库以"理论优先、渐进实现"为原则，工具原型注重接口标准化与可扩展性。
- **核心使命**：构建严格、完整、系统的形式化理论体系，为计算机科学和软件工程提供坚实的理论基础。
