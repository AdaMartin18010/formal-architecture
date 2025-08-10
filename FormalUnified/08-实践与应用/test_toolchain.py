#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具链基本功能测试脚本
"""

import sys
import os
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_imports():
    """测试模块导入"""
    logging.info("🧪 测试模块导入...")
    
    try:
        # 测试AI建模引擎
        from AI_Modeling_Engine.prototype import AIModelingEngine, ModelType, PropertyType
        logging.info("✅ AI建模引擎导入成功")
        
        # 测试模型可视化工具
        from FormalTools.model_visualizer import ModelVisualizer
        logging.info("✅ 模型可视化工具导入成功")
        
        # 测试形式验证工具
        from VerificationTools.formal_checker import FormalVerificationEngine, PropertySpec
        logging.info("✅ 形式验证工具导入成功")
        
        return True
        
    except ImportError as e:
        logging.error(f"❌ 模块导入失败: {e}")
        return False

def test_basic_functionality():
    """测试基本功能"""
    logging.info("🧪 测试基本功能...")
    
    try:
        from AI_Modeling_Engine.prototype import AIModelingEngine, ModelType
        
        # 创建引擎实例
        engine = AIModelingEngine()
        logging.info("✅ 引擎实例创建成功")
        
        # 测试简单需求处理
        simple_requirements = "创建一个简单的状态机"
        result = engine.process_requirements(simple_requirements, ModelType.STATE_MACHINE)
        
        if result and 'model_id' in result:
            logging.info("✅ 需求处理成功")
            logging.info(f"   模型ID: {result['model_id']}")
            logging.info(f"   模型类型: {result['model_type']}")
            return True
        else:
            logging.error("❌ 需求处理失败")
            return False
            
    except Exception as e:
        logging.error(f"❌ 基本功能测试失败: {e}")
        return False

def test_visualization():
    """测试可视化功能"""
    logging.info("🧪 测试可视化功能...")
    
    try:
        from FormalTools.model_visualizer import ModelVisualizer
        
        visualizer = ModelVisualizer()
        logging.info("✅ 可视化工具创建成功")
        
        # 创建测试模型数据
        test_model = {
            "id": "test_001",
            "type": "state_machine",
            "states": ["Start", "Running", "End"],
            "transitions": [
                {"from": "Start", "event": "begin", "to": "Running"},
                {"from": "Running", "event": "finish", "to": "End"}
            ]
        }
        
        # 测试可视化生成
        output_file = "test_visualization.png"
        visualizer.visualize_model(test_model, output_file)
        
        if os.path.exists(output_file):
            logging.info("✅ 可视化生成成功")
            os.remove(output_file)  # 清理测试文件
            return True
        else:
            logging.error("❌ 可视化文件未生成")
            return False
            
    except Exception as e:
        logging.error(f"❌ 可视化测试失败: {e}")
        return False

def test_verification():
    """测试验证功能"""
    logging.info("🧪 测试验证功能...")
    
    try:
        from VerificationTools.formal_checker import FormalVerificationEngine, PropertySpec, PropertyType
        
        verifier = FormalVerificationEngine()
        logging.info("✅ 验证引擎创建成功")
        
        # 创建测试模型
        test_model = {
            "id": "test_verification",
            "type": "state_machine",
            "states": ["A", "B"],
            "transitions": [{"from": "A", "event": "move", "to": "B"}]
        }
        
        # 测试性质验证
        property_spec = PropertySpec("可达性", PropertyType.REACHABILITY, "测试可达性")
        result = verifier.verify_property(test_model, property_spec)
        
        if result and 'result' in result:
            logging.info("✅ 性质验证成功")
            logging.info(f"   验证结果: {result['result']}")
            return True
        else:
            logging.error("❌ 性质验证失败")
            return False
            
    except Exception as e:
        logging.error(f"❌ 验证测试失败: {e}")
        return False

def test_code_generation():
    """测试代码生成功能"""
    logging.info("🧪 测试代码生成功能...")
    
    try:
        from AI_Modeling_Engine.prototype import AIModelingEngine, ModelType
        
        engine = AIModelingEngine()
        
        # 创建测试模型
        test_requirements = "创建一个简单的状态机，包含开始和结束状态"
        result = engine.process_requirements(test_requirements, ModelType.STATE_MACHINE)
        model_id = result['model_id']
        
        # 测试Rust代码生成
        rust_code = engine.generate_implementation(model_id, "rust")
        if rust_code and "pub enum State" in rust_code:
            logging.info("✅ Rust代码生成成功")
        else:
            logging.error("❌ Rust代码生成失败")
            return False
        
        # 测试Go代码生成
        go_code = engine.generate_implementation(model_id, "go")
        if go_code and "type State string" in go_code:
            logging.info("✅ Go代码生成成功")
        else:
            logging.error("❌ Go代码生成失败")
            return False
        
        return True
        
    except Exception as e:
        logging.error(f"❌ 代码生成测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    logging.info("🚀 开始运行工具链测试...")
    
    tests = [
        ("模块导入", test_imports),
        ("基本功能", test_basic_functionality),
        ("可视化功能", test_visualization),
        ("验证功能", test_verification),
        ("代码生成", test_code_generation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logging.info(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                logging.info(f"✅ {test_name} 测试通过")
            else:
                logging.error(f"❌ {test_name} 测试失败")
        except Exception as e:
            logging.error(f"❌ {test_name} 测试异常: {e}")
    
    # 输出测试结果
    logging.info(f"\n{'='*50}")
    logging.info("📊 测试结果总结")
    logging.info(f"{'='*50}")
    logging.info(f"总测试数: {total}")
    logging.info(f"通过测试: {passed}")
    logging.info(f"失败测试: {total - passed}")
    logging.info(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        logging.info("🎉 所有测试通过！工具链基本功能正常。")
        return True
    else:
        logging.warning("⚠️ 部分测试失败，请检查相关功能。")
        return False

def main():
    """主函数"""
    logging.info("🎯 工具链测试系统启动")
    
    # 检查工作目录
    current_dir = Path.cwd()
    logging.info(f"当前工作目录: {current_dir}")
    
    # 检查必要文件
    required_files = [
        "AI-Modeling-Engine/prototype.py",
        "FormalTools/model_visualizer.py",
        "VerificationTools/formal_checker.py"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            logging.error(f"❌ 缺少必要文件: {file_path}")
            logging.error("请确保在正确的目录下运行测试")
            return False
    
    # 运行测试
    success = run_all_tests()
    
    if success:
        logging.info("\n✨ 工具链测试完成，可以开始使用！")
        return 0
    else:
        logging.error("\n💥 工具链测试失败，请检查问题后重试")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 