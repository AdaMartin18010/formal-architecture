# 工具链集成测试报告

## 测试信息

- **测试时间**: 2025-08-11 21:23:37
- **测试时长**: 45.11秒
- **总测试数**: 5
- **通过测试**: 3
- **失败测试**: 2
- **成功率**: 60.0%

## 测试结果

### theory_mapper

- **状态**: ✅ PASS
- **supported_languages**: ['rust', 'go', 'python', 'typescript', 'java', 'csharp']
- **supported_patterns**: ['petri_net', 'state_machine', 'temporal_logic']
- **coverage**: {'petri_net': ['go', 'python', 'rust'], 'state_machine': ['go', 'python', 'rust'], 'temporal_logic': ['go', 'python', 'rust']}

### code_generator

- **状态**: ✅ PASS
- **output**: 映射模板: state_machine_python.template
✅ 生成4个文件 (language=python, dry_run=True)

### verification_engine

- **状态**: ❌ FAIL
- **错误**: 验证过程异常

### comprehensive_demo

- **状态**: ❌ FAIL
- **错误**: 演示过程异常

### tool_integration

- **状态**: ✅ PASS
- **mapper_template**: state_machine_rust.template
- **integration_flow**: 映射工具 → 代码生成器

## 总结

- **总体状态**: FAIL

### 建议

- 需要修复失败的测试: verification_engine, comprehensive_demo
- 映射工具支持 9 种模式-语言组合
- 工具链集成良好，可以支持端到端的理论到代码生成流程
