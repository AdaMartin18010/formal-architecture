#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版工具链集成脚本
提供统一的工具接口、错误处理、性能监控和协作机制
"""

import sys
import os
import logging
import json
import time
import traceback
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_toolchain.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@dataclass
class ToolResult:
    """工具执行结果"""
    success: bool
    data: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Optional[Dict[str, Any]] = None

class EnhancedToolchain:
    """增强版工具链集成器"""
    
    def __init__(self):
        self.tools = {}
        self.workflow_history = []
        self.performance_metrics = {}
        self.error_log = []
        
        # 初始化工具
        self._initialize_tools()
        
    def _initialize_tools(self):
        """初始化所有工具"""
        try:
            # AI建模引擎
            from AI_Modeling_Engine.prototype import AIModelingEngine, ModelType, PropertyType
            self.tools['ai_engine'] = AIModelingEngine()
            logger.info("✅ AI建模引擎初始化成功")
            
            # 模型可视化工具
            from FormalTools.model_visualizer import ModelVisualizer
            self.tools['visualizer'] = ModelVisualizer()
            logger.info("✅ 模型可视化工具初始化成功")
            
            # 形式验证工具
            from VerificationTools.formal_checker import FormalVerificationEngine, PropertySpec
            self.tools['verifier'] = FormalVerificationEngine()
            logger.info("✅ 形式验证工具初始化成功")
            
        except ImportError as e:
            logger.error(f"❌ 工具初始化失败: {e}")
            raise
    
    def execute_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, ToolResult]:
        """执行完整的工作流程"""
        start_time = time.time()
        workflow_id = f"workflow_{int(start_time)}"
        
        logger.info(f"🚀 开始执行工作流程: {workflow_id}")
        logger.info(f"配置: {json.dumps(workflow_config, indent=2, ensure_ascii=False)}")
        
        results = {}
        
        try:
            # 阶段1: AI建模
            if 'modeling' in workflow_config:
                results['modeling'] = self._execute_modeling(workflow_config['modeling'])
            
            # 阶段2: 模型可视化
            if 'visualization' in workflow_config and results.get('modeling', {}).success:
                results['visualization'] = self._execute_visualization(
                    results['modeling'].data, 
                    workflow_config['visualization']
                )
            
            # 阶段3: 形式验证
            if 'verification' in workflow_config and results.get('modeling', {}).success:
                results['verification'] = self._execute_verification(
                    results['modeling'].data,
                    workflow_config['verification']
                )
            
            # 阶段4: 代码生成
            if 'code_generation' in workflow_config and results.get('modeling', {}).success:
                results['code_generation'] = self._execute_code_generation(
                    results['modeling'].data,
                    workflow_config['code_generation']
                )
            
            # 记录工作流程历史
            workflow_duration = time.time() - start_time
            self.workflow_history.append({
                'id': workflow_id,
                'config': workflow_config,
                'results': results,
                'duration': workflow_duration,
                'timestamp': start_time
            })
            
            logger.info(f"✅ 工作流程执行完成: {workflow_id} (耗时: {workflow_duration:.2f}s)")
            
        except Exception as e:
            logger.error(f"❌ 工作流程执行失败: {e}")
            self.error_log.append({
                'workflow_id': workflow_id,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': time.time()
            })
        
        return results
    
    def _execute_modeling(self, config: Dict[str, Any]) -> ToolResult:
        """执行AI建模"""
        start_time = time.time()
        
        try:
            requirements = config.get('requirements', '')
            model_type = getattr(ModelType, config.get('model_type', 'STATE_MACHINE'))
            
            result = self.tools['ai_engine'].process_requirements(requirements, model_type)
            
            execution_time = time.time() - start_time
            return ToolResult(
                success=True,
                data=result,
                execution_time=execution_time,
                metadata={'tool': 'ai_engine', 'config': config}
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ToolResult(
                success=False,
                data=None,
                error=str(e),
                execution_time=execution_time,
                metadata={'tool': 'ai_engine', 'config': config}
            )
    
    def _execute_visualization(self, model_data: Dict[str, Any], config: Dict[str, Any]) -> ToolResult:
        """执行模型可视化"""
        start_time = time.time()
        
        try:
            output_file = config.get('output_file', f"visualization_{model_data.get('model_id', 'unknown')}.png")
            
            self.tools['visualizer'].visualize_model(model_data, output_file)
            
            execution_time = time.time() - start_time
            return ToolResult(
                success=True,
                data={'output_file': output_file},
                execution_time=execution_time,
                metadata={'tool': 'visualizer', 'config': config}
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ToolResult(
                success=False,
                data=None,
                error=str(e),
                execution_time=execution_time,
                metadata={'tool': 'visualizer', 'config': config}
            )
    
    def _execute_verification(self, model_data: Dict[str, Any], config: Dict[str, Any]) -> ToolResult:
        """执行形式验证"""
        start_time = time.time()
        
        try:
            properties = config.get('properties', [])
            verification_result = self.tools['verifier'].verify_model(model_data, properties)
            
            execution_time = time.time() - start_time
            return ToolResult(
                success=True,
                data=verification_result,
                execution_time=execution_time,
                metadata={'tool': 'verifier', 'config': config}
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ToolResult(
                success=False,
                data=None,
                error=str(e),
                execution_time=execution_time,
                metadata={'tool': 'verifier', 'config': config}
            )
    
    def _execute_code_generation(self, model_data: Dict[str, Any], config: Dict[str, Any]) -> ToolResult:
        """执行代码生成"""
        start_time = time.time()
        
        try:
            target_language = config.get('target_language', 'rust')
            output_dir = config.get('output_dir', './generated_code')
            
            # 这里需要实现代码生成逻辑
            # 暂时返回模拟结果
            generated_files = [f"{output_dir}/main.{target_language}"]
            
            execution_time = time.time() - start_time
            return ToolResult(
                success=True,
                data={'generated_files': generated_files, 'target_language': target_language},
                execution_time=execution_time,
                metadata={'tool': 'code_generator', 'config': config}
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ToolResult(
                success=False,
                data=None,
                error=str(e),
                execution_time=execution_time,
                metadata={'tool': 'code_generator', 'config': config}
            )
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        if not self.workflow_history:
            return {"message": "暂无工作流程历史"}
        
        total_workflows = len(self.workflow_history)
        successful_workflows = len([w for w in self.workflow_history if all(r.success for r in w['results'].values())])
        
        avg_duration = sum(w['duration'] for w in self.workflow_history) / total_workflows
        
        tool_performance = {}
        for workflow in self.workflow_history:
            for tool_name, result in workflow['results'].items():
                if tool_name not in tool_performance:
                    tool_performance[tool_name] = {'total_time': 0, 'count': 0, 'errors': 0}
                
                tool_performance[tool_name]['total_time'] += result.execution_time
                tool_performance[tool_name]['count'] += 1
                if not result.success:
                    tool_performance[tool_name]['errors'] += 1
        
        # 计算平均时间
        for tool_name, stats in tool_performance.items():
            if stats['count'] > 0:
                stats['avg_time'] = stats['total_time'] / stats['count']
                stats['success_rate'] = (stats['count'] - stats['errors']) / stats['count']
        
        return {
            'total_workflows': total_workflows,
            'successful_workflows': successful_workflows,
            'success_rate': successful_workflows / total_workflows,
            'average_duration': avg_duration,
            'tool_performance': tool_performance,
            'error_summary': self.error_log
        }
    
    def export_workflow_report(self, output_file: str = "workflow_report.json"):
        """导出工作流程报告"""
        report = {
            'timestamp': time.time(),
            'performance': self.get_performance_report(),
            'workflow_history': self.workflow_history,
            'error_log': self.error_log
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 工作流程报告已导出到: {output_file}")

def demo_enhanced_toolchain():
    """演示增强版工具链"""
    logger.info("🎯 开始演示增强版工具链")
    
    toolchain = EnhancedToolchain()
    
    # 配置示例工作流程
    workflow_config = {
        'modeling': {
            'requirements': '创建一个微服务架构的电商系统，包含用户管理、商品管理、订单管理三个服务',
            'model_type': 'MICROSERVICE'
        },
        'visualization': {
            'output_file': 'ecommerce_microservice.png'
        },
        'verification': {
            'properties': ['服务间通信正确性', '数据一致性', '故障隔离']
        },
        'code_generation': {
            'target_language': 'rust',
            'output_dir': './generated_ecommerce'
        }
    }
    
    # 执行工作流程
    results = toolchain.execute_workflow(workflow_config)
    
    # 显示结果
    logger.info("\n📋 工作流程执行结果:")
    for stage, result in results.items():
        status = "✅" if result.success else "❌"
        logger.info(f"{status} {stage}: {result.success}")
        if result.error:
            logger.error(f"   错误: {result.error}")
        if result.data:
            logger.info(f"   数据: {result.data}")
    
    # 生成性能报告
    performance_report = toolchain.get_performance_report()
    logger.info(f"\n📊 性能报告:")
    logger.info(f"总工作流程数: {performance_report['total_workflows']}")
    logger.info(f"成功率: {performance_report['success_rate']:.2%}")
    logger.info(f"平均耗时: {performance_report['average_duration']:.2f}s")
    
    # 导出报告
    toolchain.export_workflow_report()
    
    return toolchain

if __name__ == "__main__":
    try:
        demo_enhanced_toolchain()
    except Exception as e:
        logger.error(f"演示失败: {e}")
        traceback.print_exc() 