#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具链集成器 (Integrated Toolchain)
整合统一建模工具、跨理论验证引擎和智能化分析平台
提供统一的接口和工作流
"""

import os
import sys
import json
import logging
import time
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import traceback

# 导入核心工具
from UnifiedModelingTool import UnifiedModelingTool
from CrossTheoryVerificationEngine import CrossTheoryVerificationEngine
from IntelligentAnalysisPlatform import IntelligentAnalysisPlatform

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WorkflowType(Enum):
    """工作流类型"""
    MODEL_CREATION = "model_creation"
    MODEL_VERIFICATION = "model_verification"
    SYSTEM_ANALYSIS = "system_analysis"
    FULL_LIFECYCLE = "full_lifecycle"
    CUSTOM_WORKFLOW = "custom_workflow"

class ExecutionStatus(Enum):
    """执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class WorkflowStep:
    """工作流步骤"""
    step_id: str
    name: str
    tool: str
    parameters: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 300  # 秒
    retry_count: int = 3

@dataclass
class WorkflowExecution:
    """工作流执行"""
    execution_id: str
    workflow_type: WorkflowType
    steps: List[WorkflowStep]
    status: ExecutionStatus
    current_step: int = 0
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ToolchainConfig:
    """工具链配置"""
    max_concurrent_workflows: int = 5
    default_timeout: int = 300
    enable_parallel_execution: bool = True
    enable_caching: bool = True
    cache_ttl: int = 3600  # 秒
    log_level: str = "INFO"
    output_directory: str = "./output"
    temp_directory: str = "./temp"

class WorkflowEngine:
    """工作流引擎"""
    
    def __init__(self, config: ToolchainConfig):
        self.config = config
        self.executions: Dict[str, WorkflowExecution] = {}
        self.executor = ThreadPoolExecutor(max_workers=config.max_concurrent_workflows)
        self.cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, float] = {}
        
        # 确保输出目录存在
        os.makedirs(config.output_directory, exist_ok=True)
        os.makedirs(config.temp_directory, exist_ok=True)
    
    def create_workflow(self, workflow_type: WorkflowType, **kwargs) -> WorkflowExecution:
        """创建工作流"""
        execution_id = f"workflow_{workflow_type.value}_{int(time.time())}"
        
        if workflow_type == WorkflowType.MODEL_CREATION:
            steps = self._create_model_creation_workflow(**kwargs)
        elif workflow_type == WorkflowType.MODEL_VERIFICATION:
            steps = self._create_model_verification_workflow(**kwargs)
        elif workflow_type == WorkflowType.SYSTEM_ANALYSIS:
            steps = self._create_system_analysis_workflow(**kwargs)
        elif workflow_type == WorkflowType.FULL_LIFECYCLE:
            steps = self._create_full_lifecycle_workflow(**kwargs)
        else:
            steps = kwargs.get('steps', [])
        
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_type=workflow_type,
            steps=steps,
            status=ExecutionStatus.PENDING,
            metadata=kwargs
        )
        
        self.executions[execution_id] = execution
        logger.info(f"创建工作流: {execution_id}")
        return execution
    
    def _create_model_creation_workflow(self, **kwargs) -> List[WorkflowStep]:
        """创建模型创建工作流"""
        theory_type = kwargs.get('theory_type', 'state_machine')
        specification = kwargs.get('specification', {})
        
        return [
            WorkflowStep(
                step_id="create_model",
                name="创建模型",
                tool="unified_modeling_tool",
                parameters={
                    'theory_type': theory_type,
                    'specification': specification
                }
            ),
            WorkflowStep(
                step_id="validate_model",
                name="验证模型",
                tool="cross_theory_verification",
                parameters={
                    'verification_type': 'basic_validation'
                },
                dependencies=["create_model"]
            )
        ]
    
    def _create_model_verification_workflow(self, **kwargs) -> List[WorkflowStep]:
        """创建模型验证工作流"""
        model_id = kwargs.get('model_id')
        verification_spec = kwargs.get('verification_spec', {})
        
        return [
            WorkflowStep(
                step_id="load_model",
                name="加载模型",
                tool="unified_modeling_tool",
                parameters={'action': 'load', 'model_id': model_id}
            ),
            WorkflowStep(
                step_id="verify_model",
                name="验证模型",
                tool="cross_theory_verification",
                parameters={
                    'verification_spec': verification_spec
                },
                dependencies=["load_model"]
            ),
            WorkflowStep(
                step_id="generate_report",
                name="生成报告",
                tool="cross_theory_verification",
                parameters={'action': 'generate_report'},
                dependencies=["verify_model"]
            )
        ]
    
    def _create_system_analysis_workflow(self, **kwargs) -> List[WorkflowStep]:
        """创建系统分析工作流"""
        model_id = kwargs.get('model_id')
        
        return [
            WorkflowStep(
                step_id="load_model",
                name="加载模型",
                tool="unified_modeling_tool",
                parameters={'action': 'load', 'model_id': model_id}
            ),
            WorkflowStep(
                step_id="analyze_system",
                name="系统分析",
                tool="intelligent_analysis",
                parameters={},
                dependencies=["load_model"]
            ),
            WorkflowStep(
                step_id="export_report",
                name="导出报告",
                tool="intelligent_analysis",
                parameters={'action': 'export_report'},
                dependencies=["analyze_system"]
            )
        ]
    
    def _create_full_lifecycle_workflow(self, **kwargs) -> List[WorkflowStep]:
        """创建完整生命周期工作流"""
        theory_type = kwargs.get('theory_type', 'state_machine')
        specification = kwargs.get('specification', {})
        verification_spec = kwargs.get('verification_spec', {})
        
        return [
            WorkflowStep(
                step_id="create_model",
                name="创建模型",
                tool="unified_modeling_tool",
                parameters={
                    'theory_type': theory_type,
                    'specification': specification
                }
            ),
            WorkflowStep(
                step_id="verify_model",
                name="验证模型",
                tool="cross_theory_verification",
                parameters={
                    'verification_spec': verification_spec
                },
                dependencies=["create_model"]
            ),
            WorkflowStep(
                step_id="analyze_system",
                name="系统分析",
                tool="intelligent_analysis",
                parameters={},
                dependencies=["verify_model"]
            ),
            WorkflowStep(
                step_id="optimize_model",
                name="模型优化",
                tool="unified_modeling_tool",
                parameters={'action': 'optimize'},
                dependencies=["analyze_system"]
            ),
            WorkflowStep(
                step_id="final_verification",
                name="最终验证",
                tool="cross_theory_verification",
                parameters={
                    'verification_spec': verification_spec
                },
                dependencies=["optimize_model"]
            ),
            WorkflowStep(
                step_id="export_results",
                name="导出结果",
                tool="unified_modeling_tool",
                parameters={'action': 'export'},
                dependencies=["final_verification"]
            )
        ]
    
    async def execute_workflow(self, execution_id: str) -> WorkflowExecution:
        """执行工作流"""
        if execution_id not in self.executions:
            raise ValueError(f"工作流不存在: {execution_id}")
        
        execution = self.executions[execution_id]
        execution.status = ExecutionStatus.RUNNING
        execution.start_time = time.time()
        
        logger.info(f"开始执行工作流: {execution_id}")
        
        try:
            # 按依赖关系排序步骤
            sorted_steps = self._topological_sort(execution.steps)
            
            for i, step in enumerate(sorted_steps):
                execution.current_step = i
                logger.info(f"执行步骤 {i+1}/{len(sorted_steps)}: {step.name}")
                
                # 检查依赖
                if not self._check_dependencies(step, execution.results):
                    raise RuntimeError(f"步骤依赖未满足: {step.step_id}")
                
                # 执行步骤
                step_result = await self._execute_step(step, execution.results)
                execution.results[step.step_id] = step_result
                
                logger.info(f"步骤完成: {step.name}")
            
            execution.status = ExecutionStatus.COMPLETED
            execution.end_time = time.time()
            logger.info(f"工作流执行完成: {execution_id}")
            
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.end_time = time.time()
            execution.errors.append(str(e))
            logger.error(f"工作流执行失败: {execution_id}, 错误: {e}")
            logger.error(traceback.format_exc())
        
        return execution
    
    def _topological_sort(self, steps: List[WorkflowStep]) -> List[WorkflowStep]:
        """拓扑排序步骤"""
        # 构建依赖图
        graph = {step.step_id: step for step in steps}
        in_degree = {step.step_id: 0 for step in steps}
        
        for step in steps:
            for dep in step.dependencies:
                if dep in in_degree:
                    in_degree[dep] += 1
        
        # 拓扑排序
        queue = [step_id for step_id, degree in in_degree.items() if degree == 0]
        sorted_steps = []
        
        while queue:
            step_id = queue.pop(0)
            sorted_steps.append(graph[step_id])
            
            for step in steps:
                if step_id in step.dependencies:
                    in_degree[step.step_id] -= 1
                    if in_degree[step.step_id] == 0:
                        queue.append(step.step_id)
        
        if len(sorted_steps) != len(steps):
            raise RuntimeError("工作流存在循环依赖")
        
        return sorted_steps
    
    def _check_dependencies(self, step: WorkflowStep, results: Dict[str, Any]) -> bool:
        """检查步骤依赖"""
        for dep in step.dependencies:
            if dep not in results:
                return False
        return True
    
    async def _execute_step(self, step: WorkflowStep, results: Dict[str, Any]) -> Any:
        """执行单个步骤"""
        # 检查缓存
        cache_key = self._generate_cache_key(step, results)
        if self.config.enable_caching and cache_key in self.cache:
            cache_age = time.time() - self.cache_timestamps[cache_key]
            if cache_age < self.config.cache_ttl:
                logger.info(f"使用缓存结果: {step.step_id}")
                return self.cache[cache_key]
        
        # 执行步骤
        if step.tool == "unified_modeling_tool":
            result = await self._execute_modeling_tool(step, results)
        elif step.tool == "cross_theory_verification":
            result = await self._execute_verification_tool(step, results)
        elif step.tool == "intelligent_analysis":
            result = await self._execute_analysis_tool(step, results)
        else:
            raise ValueError(f"未知工具: {step.tool}")
        
        # 缓存结果
        if self.config.enable_caching:
            self.cache[cache_key] = result
            self.cache_timestamps[cache_key] = time.time()
        
        return result
    
    def _generate_cache_key(self, step: WorkflowStep, results: Dict[str, Any]) -> str:
        """生成缓存键"""
        # 基于步骤参数和依赖结果生成缓存键
        key_data = {
            'tool': step.tool,
            'parameters': step.parameters,
            'dependencies': {dep: results.get(dep) for dep in step.dependencies}
        }
        return json.dumps(key_data, sort_keys=True)
    
    async def _execute_modeling_tool(self, step: WorkflowStep, results: Dict[str, Any]) -> Any:
        """执行建模工具"""
        # 这里应该调用实际的建模工具
        # 目前返回模拟结果
        action = step.parameters.get('action', 'create')
        
        if action == 'create':
            return {
                'model_id': f"model_{int(time.time())}",
                'theory_type': step.parameters.get('theory_type'),
                'status': 'created'
            }
        elif action == 'load':
            return {
                'model_id': step.parameters.get('model_id'),
                'content': {'states': [], 'transitions': []},
                'status': 'loaded'
            }
        elif action == 'optimize':
            return {
                'model_id': results.get('create_model', {}).get('model_id'),
                'optimizations': ['reduced_states', 'simplified_transitions'],
                'status': 'optimized'
            }
        elif action == 'export':
            return {
                'export_path': f"{self.config.output_directory}/model_export.json",
                'status': 'exported'
            }
        else:
            raise ValueError(f"未知建模工具操作: {action}")
    
    async def _execute_verification_tool(self, step: WorkflowStep, results: Dict[str, Any]) -> Any:
        """执行验证工具"""
        action = step.parameters.get('action', 'verify')
        
        if action == 'verify':
            return {
                'verification_id': f"verify_{int(time.time())}",
                'status': 'verified',
                'issues': [],
                'warnings': []
            }
        elif action == 'generate_report':
            return {
                'report_path': f"{self.config.output_directory}/verification_report.json",
                'status': 'generated'
            }
        else:
            raise ValueError(f"未知验证工具操作: {action}")
    
    async def _execute_analysis_tool(self, step: WorkflowStep, results: Dict[str, Any]) -> Any:
        """执行分析工具"""
        action = step.parameters.get('action', 'analyze')
        
        if action == 'analyze':
            return {
                'analysis_id': f"analysis_{int(time.time())}",
                'patterns': ['layered_architecture', 'microservices'],
                'insights': {'performance': 0.8, 'scalability': 0.7},
                'recommendations': ['optimize_performance', 'improve_scalability']
            }
        elif action == 'export_report':
            return {
                'report_path': f"{self.config.output_directory}/analysis_report.json",
                'status': 'exported'
            }
        else:
            raise ValueError(f"未知分析工具操作: {action}")
    
    def get_workflow_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """获取工作流状态"""
        return self.executions.get(execution_id)
    
    def cancel_workflow(self, execution_id: str) -> bool:
        """取消工作流"""
        if execution_id in self.executions:
            execution = self.executions[execution_id]
            if execution.status == ExecutionStatus.RUNNING:
                execution.status = ExecutionStatus.CANCELLED
                execution.end_time = time.time()
                logger.info(f"工作流已取消: {execution_id}")
                return True
        return False
    
    def cleanup(self):
        """清理资源"""
        self.executor.shutdown(wait=True)
        logger.info("工作流引擎已清理")

class IntegratedToolchain:
    """工具链集成器"""
    
    def __init__(self, config: ToolchainConfig = None):
        self.config = config or ToolchainConfig()
        self.workflow_engine = WorkflowEngine(self.config)
        
        # 初始化核心工具
        self.modeling_tool = UnifiedModelingTool()
        self.verification_engine = CrossTheoryVerificationEngine()
        self.analysis_platform = IntelligentAnalysisPlatform()
        
        logger.info("工具链集成器初始化完成")
    
    async def create_andVerify_model(self, theory_type: str, specification: Dict[str, Any], 
                                   verification_spec: Dict[str, Any] = None) -> Dict[str, Any]:
        """创建并验证模型"""
        logger.info(f"开始创建并验证模型: {theory_type}")
        
        # 创建工作流
        workflow = self.workflow_engine.create_workflow(
            WorkflowType.MODEL_CREATION,
            theory_type=theory_type,
            specification=specification,
            verification_spec=verification_spec or {}
        )
        
        # 执行工作流
        result = await self.workflow_engine.execute_workflow(workflow.execution_id)
        
        if result.status == ExecutionStatus.COMPLETED:
            return {
                'success': True,
                'model_id': result.results.get('create_model', {}).get('model_id'),
                'verification_result': result.results.get('validate_model', {}),
                'execution_time': result.end_time - result.start_time
            }
        else:
            return {
                'success': False,
                'errors': result.errors,
                'execution_time': result.end_time - result.start_time if result.end_time else 0
            }
    
    async def analyze_system(self, model_id: str) -> Dict[str, Any]:
        """分析系统"""
        logger.info(f"开始系统分析: {model_id}")
        
        # 创建工作流
        workflow = self.workflow_engine.create_workflow(
            WorkflowType.SYSTEM_ANALYSIS,
            model_id=model_id
        )
        
        # 执行工作流
        result = await self.workflow_engine.execute_workflow(workflow.execution_id)
        
        if result.status == ExecutionStatus.COMPLETED:
            return {
                'success': True,
                'analysis_result': result.results.get('analyze_system', {}),
                'report_path': result.results.get('export_report', {}).get('report_path'),
                'execution_time': result.end_time - result.start_time
            }
        else:
            return {
                'success': False,
                'errors': result.errors,
                'execution_time': result.end_time - result.start_time if result.end_time else 0
            }
    
    async def full_lifecycle_workflow(self, theory_type: str, specification: Dict[str, Any],
                                    verification_spec: Dict[str, Any] = None) -> Dict[str, Any]:
        """完整生命周期工作流"""
        logger.info(f"开始完整生命周期工作流: {theory_type}")
        
        # 创建工作流
        workflow = self.workflow_engine.create_workflow(
            WorkflowType.FULL_LIFECYCLE,
            theory_type=theory_type,
            specification=specification,
            verification_spec=verification_spec or {}
        )
        
        # 执行工作流
        result = await self.workflow_engine.execute_workflow(workflow.execution_id)
        
        if result.status == ExecutionStatus.COMPLETED:
            return {
                'success': True,
                'model_id': result.results.get('create_model', {}).get('model_id'),
                'verification_result': result.results.get('verify_model', {}),
                'analysis_result': result.results.get('analyze_system', {}),
                'optimization_result': result.results.get('optimize_model', {}),
                'final_verification': result.results.get('final_verification', {}),
                'export_path': result.results.get('export_results', {}).get('export_path'),
                'execution_time': result.end_time - result.start_time
            }
        else:
            return {
                'success': False,
                'errors': result.errors,
                'execution_time': result.end_time - result.start_time if result.end_time else 0
            }
    
    def get_workflow_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """获取工作流状态"""
        return self.workflow_engine.get_workflow_status(execution_id)
    
    def cancel_workflow(self, execution_id: str) -> bool:
        """取消工作流"""
        return self.workflow_engine.cancel_workflow(execution_id)
    
    def cleanup(self):
        """清理资源"""
        self.workflow_engine.cleanup()
        logger.info("工具链集成器已清理")

async def main():
    """主函数 - 演示工具链集成器使用"""
    print("=== 工具链集成器演示 ===\n")
    
    # 创建工具链
    config = ToolchainConfig(
        max_concurrent_workflows=3,
        enable_parallel_execution=True,
        enable_caching=True
    )
    
    toolchain = IntegratedToolchain(config)
    
    try:
        # 1. 创建并验证状态机模型
        print("1. 创建并验证状态机模型")
        state_machine_spec = {
            'states': ['idle', 'processing', 'completed', 'error'],
            'transitions': [
                {'from': 'idle', 'to': 'processing', 'trigger': 'start'},
                {'from': 'processing', 'to': 'completed', 'trigger': 'finish'},
                {'from': 'processing', 'to': 'error', 'trigger': 'fail'},
                {'from': 'error', 'to': 'idle', 'trigger': 'reset'}
            ]
        }
        
        result = await toolchain.createAndVerify_model('state_machine', state_machine_spec)
        print(f"   结果: {'成功' if result['success'] else '失败'}")
        if result['success']:
            print(f"   模型ID: {result['model_id']}")
            print(f"   执行时间: {result['execution_time']:.2f}秒")
        
        # 2. 系统分析
        if result['success']:
            print("\n2. 系统分析")
            analysis_result = await toolchain.analyze_system(result['model_id'])
            print(f"   结果: {'成功' if analysis_result['success'] else '失败'}")
            if analysis_result['success']:
                print(f"   报告路径: {analysis_result['report_path']}")
                print(f"   执行时间: {analysis_result['execution_time']:.2f}秒")
        
        # 3. 完整生命周期工作流
        print("\n3. 完整生命周期工作流")
        lifecycle_result = await toolchain.full_lifecycle_workflow('petri_net', {
            'places': ['p1', 'p2', 'p3'],
            'transitions': ['t1', 't2'],
            'arcs': [{'from': 'p1', 'to': 't1'}, {'from': 't1', 'to': 'p2'}]
        })
        
        print(f"   结果: {'成功' if lifecycle_result['success'] else '失败'}")
        if lifecycle_result['success']:
            print(f"   模型ID: {lifecycle_result['model_id']}")
            print(f"   导出路径: {lifecycle_result['export_path']}")
            print(f"   执行时间: {lifecycle_result['execution_time']:.2f}秒")
        
        # 4. 显示工作流状态
        print("\n4. 工作流状态")
        for execution_id in toolchain.workflow_engine.executions:
            status = toolchain.get_workflow_status(execution_id)
            print(f"   工作流 {execution_id}: {status.status.value}")
    
    except Exception as e:
        print(f"演示过程中发生错误: {e}")
        logger.error(f"演示错误: {e}")
        logger.error(traceback.format_exc())
    
    finally:
        # 清理资源
        toolchain.cleanup()
        print("\n=== 演示完成 ===")

if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main()) 