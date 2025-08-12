# FormalUnified使用指南

## 快速开始

### 1. 环境要求
- Python 3.8+
- 依赖包: yaml, jinja2, networkx

### 2. 安装依赖
```bash
pip install pyyaml jinja2 networkx
```

### 3. 运行演示
```bash
# 综合演示
python tools/08-实践与应用/comprehensive_demo.py

# 理论到实践映射
python tools/08-实践与应用/theory_to_practice_mapper.py --describe

# 代码生成器
python tools/08-实践与应用/AutomatedCodeGenerator/automated_code_generator.py --language python --pattern state_machine --dry-run

# 跨理论验证
python tools/08-实践与应用/CrossTheoryVerificationEngine.py

# 工具链集成测试
python tools/08-实践与应用/toolchain_integration_test.py
```

### 4. 查看报告
- 综合演示报告: `reports/demo_report.md`
- 集成测试报告: `reports/toolchain_integration_report.md`
- 发布报告: `reports/release_report.md`

## 项目结构

```
FormalUnified_Release_v1.0.0/
├── docs/                    # 项目文档
├── tools/                   # 核心工具
├── examples/                # 示例代码
└── reports/                 # 测试报告
```

## 核心工具说明

### 理论到实践映射工具
- 功能: 将抽象理论模式映射到具体编程语言模板
- 支持: 6种语言 × 3种模式 = 18种组合

### 自动化代码生成器
- 功能: 根据规范自动生成多语言代码
- 支持: Python, Java, TypeScript, Rust等

### 跨理论验证引擎
- 功能: 验证理论体系的一致性和完整性
- 输出: 详细的验证报告和建议

### 综合演示脚本
- 功能: 展示整个理论体系的核心功能
- 输出: 完整的演示报告

## 技术支持

如有问题，请查看项目文档或联系开发团队。

---
*FormalUnified v1.0.0 - 形式化架构理论统一项目*
