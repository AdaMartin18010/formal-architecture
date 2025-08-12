# FormalUnified

FormalUnified 是“形式化架构理论统一项目”的可运行实现与发布载体，包含九大理论体系的资料与工具链原型（AI建模引擎、验证引擎、统一建模工具、可视化建模界面、性能基准与综合演示等）。

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

- 本仓库以“理论优先、渐进实现”为原则，工具原型注重接口标准化与可扩展性。
