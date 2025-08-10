#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
理论到实践映射工具演示脚本
Theory to Practice Mapping Tool Demo Script

这个脚本展示了如何使用映射工具将理论概念转换为具体的编程实现。
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from mapping_tool import MappingEngine, TheoryConcept, PracticeImplementation

def create_sample_theory():
    """创建示例理论内容"""
    return """
### 状态机理论
状态机是一种计算模型，由状态集合、输入字母、转换函数和初始状态组成。

**核心概念:**
- 状态：系统的可能状态
- 转换：状态间的转换关系
- 事件：触发转换的事件

**应用场景:**
- 工作流引擎
- 游戏状态管理
- 协议实现

**理论性质:**
- 确定性：每个输入都有唯一的输出
- 有限性：状态数量有限
- 可计算性：可以模拟任何计算过程

### Petri网理论
Petri网是一种用于描述和分析并发系统的数学建模语言。

**核心概念:**
- 库所：系统的状态
- 变迁：状态转换
- 令牌：资源或请求

**应用场景:**
- 并发系统建模
- 工作流编排
- 资源分配

**理论性质:**
- 并发性：支持真正的并发执行
- 可达性：可以分析系统可达状态
- 活性：系统不会死锁

### 时态逻辑理论
时态逻辑是一种用于描述系统时序性质的逻辑系统。

**核心概念:**
- 线性时态逻辑(LTL)：描述线性时序性质
- 分支时态逻辑(CTL)：描述分支时序性质
- 模型检查：自动验证时序性质

**应用场景:**
- 系统性质验证
- 模型检查
- 时序分析

**理论性质:**
- 表达能力：可以表达复杂的时序性质
- 可判定性：某些性质可以自动验证
- 模型检查：支持自动验证算法
"""

def demo_basic_mapping():
    """演示基本映射功能"""
    print("🚀 开始演示基本映射功能")
    print("=" * 50)
    
    # 创建映射引擎
    engine = MappingEngine()
    
    # 创建示例理论内容
    theory_content = create_sample_theory()
    
    print("📚 理论内容:")
    print(theory_content[:200] + "...")
    print()
    
    # 执行映射到Rust
    print("🦀 映射到Rust语言...")
    rust_implementations = engine.map_theory_to_practice(theory_content, "rust")
    
    print(f"✅ 生成了 {len(rust_implementations)} 个Rust实现")
    for i, impl in enumerate(rust_implementations):
        print(f"  {i+1}. {impl.language} - {len(impl.code)} 字符")
    
    print()
    
    # 执行映射到Python
    print("🐍 映射到Python语言...")
    python_implementations = engine.map_theory_to_practice(theory_content, "python")
    
    print(f"✅ 生成了 {len(python_implementations)} 个Python实现")
    for i, impl in enumerate(python_implementations):
        print(f"  {i+1}. {impl.language} - {len(impl.code)} 字符")
    
    print()
    
    return rust_implementations, python_implementations

def demo_code_generation():
    """演示代码生成功能"""
    print("🔧 演示代码生成功能")
    print("=" * 50)
    
    # 创建理论概念
    concept = TheoryConcept(
        name="有限状态机",
        ty="state_machine",
        description="具有有限数量状态的自动机",
        properties={
            "状态数量": "有限",
            "输入类型": "离散",
            "确定性": "是"
        },
        relationships=["状态转换", "事件驱动"]
    )
    
    print(f"📖 理论概念: {concept.name}")
    print(f"   类型: {concept.ty}")
    print(f"   描述: {concept.description}")
    print(f"   属性: {concept.properties}")
    print()
    
    # 创建代码生成器
    from mapping_tool import CodeGenerator
    generator = CodeGenerator()
    
    # 生成Rust代码
    print("🦀 生成Rust代码...")
    rust_impl = generator.generate_code(concept, "rust")
    
    print("生成的Rust代码:")
    print("-" * 30)
    print(rust_impl.code[:300] + "...")
    print()
    
    # 生成Python代码
    print("🐍 生成Python代码...")
    python_impl = generator.generate_code(concept, "python")
    
    print("生成的Python代码:")
    print("-" * 30)
    print(python_impl.code[:300] + "...")
    print()
    
    return rust_impl, python_impl

def demo_validation():
    """演示验证功能"""
    print("✅ 演示验证功能")
    print("=" * 50)
    
    # 创建映射验证器
    from mapping_tool import MappingValidator
    validator = MappingValidator()
    
    # 创建示例理论概念和实践实现
    concept = TheoryConcept(
        name="测试概念",
        ty="test_type",
        description="用于测试的概念",
        properties={},
        relationships=[]
    )
    
    implementation = PracticeImplementation(
        language="rust",
        code="fn main() { println!(\"Hello, World!\"); }",
        tests="",
        documentation="",
        examples=[]
    )
    
    print("🔍 验证映射正确性...")
    
    # 添加验证规则
    class BasicVerificationRule:
        def verify(self, theory_concept, practice_implementation):
            # 简单的验证规则：检查代码是否包含必要的元素
            if "fn main" in practice_implementation.code:
                return {"valid": True, "message": "代码包含main函数"}
            else:
                return {"valid": False, "message": "代码缺少main函数"}
    
    validator.add_verification_rule(BasicVerificationRule())
    
    # 执行验证
    validation_result = validator.validate_mapping(concept, implementation)
    
    print("验证结果:")
    for result in validation_result.results:
        status = "✅" if result["valid"] else "❌"
        print(f"  {status} {result['message']}")
    
    print()
    
    # 生成测试用例
    print("🧪 生成测试用例...")
    test_cases = validator.generate_test_cases(concept, implementation)
    
    print(f"生成了 {len(test_cases)} 个测试用例")
    for i, test_case in enumerate(test_cases[:3]):  # 只显示前3个
        print(f"  {i+1}. {test_case}")
    
    print()

def demo_advanced_features():
    """演示高级功能"""
    print("🚀 演示高级功能")
    print("=" * 50)
    
    # 演示并行处理
    print("⚡ 并行映射处理...")
    
    # 创建多个理论概念
    concepts = [
        TheoryConcept("概念1", "type1", "描述1", {}, []),
        TheoryConcept("概念2", "type2", "描述2", {}, []),
        TheoryConcept("概念3", "type3", "描述3", {}, []),
        TheoryConcept("概念4", "type4", "描述4", {}, [])
    ]
    
    # 模拟并行处理
    import time
    start_time = time.time()
    
    # 这里可以集成真正的并行处理
    for concept in concepts:
        time.sleep(0.1)  # 模拟处理时间
    
    end_time = time.time()
    print(f"✅ 并行处理完成，耗时: {end_time - start_time:.2f}秒")
    print()
    
    # 演示缓存功能
    print("💾 缓存功能演示...")
    
    # 模拟缓存
    cache = {}
    cache_key = "test_concept"
    
    if cache_key not in cache:
        print("  📥 缓存未命中，生成新内容...")
        cache[cache_key] = "生成的内容"
    else:
        print("  📤 缓存命中，使用缓存内容...")
    
    print("✅ 缓存功能正常")
    print()
    
    # 演示插件系统
    print("🔌 插件系统演示...")
    
    class DemoPlugin:
        def __init__(self):
            self.name = "演示插件"
            self.version = "1.0.0"
        
        def get_hooks(self):
            return {
                'pre_mapping': self.pre_mapping_hook,
                'post_mapping': self.post_mapping_hook,
            }
        
        def pre_mapping_hook(self, concept):
            print(f"    🔄 预处理概念: {concept.name}")
            return concept
        
        def post_mapping_hook(self, implementation):
            print(f"    🔄 后处理实现: {implementation.language}")
            return implementation
    
    plugin = DemoPlugin()
    print(f"✅ 插件 '{plugin.name}' v{plugin.version} 加载成功")
    print()

def save_demo_results(implementations, output_dir="demo_output"):
    """保存演示结果"""
    print("💾 保存演示结果")
    print("=" * 50)
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # 保存实现
    for i, impl in enumerate(implementations):
        # 保存代码
        code_file = output_path / f"demo_implementation_{i+1}.{get_file_extension(impl.language)}"
        code_file.write_text(impl.code, encoding='utf-8')
        
        # 保存测试
        if impl.tests:
            test_file = output_path / f"demo_test_{i+1}.{get_file_extension(impl.language)}"
            test_file.write_text(impl.tests, encoding='utf-8')
        
        # 保存文档
        if impl.documentation:
            doc_file = output_path / f"demo_doc_{i+1}.md"
            doc_file.write_text(impl.documentation, encoding='utf-8')
    
    print(f"✅ 演示结果已保存到 {output_dir}/ 目录")
    print(f"📁 包含 {len(implementations)} 个实现文件")
    print()

def get_file_extension(language):
    """获取文件扩展名"""
    extensions = {
        'rust': 'rs',
        'python': 'py',
        'go': 'go',
        'java': 'java',
        'cpp': 'cpp'
    }
    return extensions.get(language, 'txt')

def main():
    """主函数"""
    print("🎯 理论到实践映射工具演示")
    print("=" * 60)
    print("这个演示展示了映射工具的核心功能和高级特性")
    print()
    
    try:
        # 基本映射演示
        rust_impls, python_impls = demo_basic_mapping()
        
        # 代码生成演示
        demo_code_generation()
        
        # 验证功能演示
        demo_validation()
        
        # 高级功能演示
        demo_advanced_features()
        
        # 保存结果
        all_implementations = rust_impls + python_impls
        save_demo_results(all_implementations)
        
        print("🎉 演示完成！")
        print("=" * 60)
        print("您可以使用以下命令来运行映射工具:")
        print("  python mapping_tool.py --help")
        print()
        print("或者查看生成的代码文件:")
        print("  ls demo_output/")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 