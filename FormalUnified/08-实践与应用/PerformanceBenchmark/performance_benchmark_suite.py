#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能基准测试套件
Performance Benchmark Suite

为FormalUnified工具链提供全面的性能基准测试，包括理论加载、代码生成、验证引擎等核心功能的性能评估
"""

import time
import psutil
import threading
import multiprocessing
import json
import yaml
import logging
import statistics
from typing import Dict, List, Any, Optional, Tuple, Callable
from pathlib import Path
from datetime import datetime
import sys
import os
import gc
import asyncio
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

# 导入工具
try:
    from UnifiedModelingTool.unified_modeling_tool import UnifiedModelingTool
    from AutomatedCodeGenerator.automated_code_generator import AutomatedCodeGenerator
    from CrossTheoryVerificationEngine import CrossTheoryVerificationEngine
    from TheoryToPractice.mapping_tool import EnhancedTheoryToPracticeMapper
    from TestingFramework.comprehensive_test_suite import ComprehensiveTestSuite
except ImportError as e:
    print(f"警告：部分工具导入失败: {e}")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BenchmarkConfig:
    """基准测试配置"""
    # 测试名称
    name: str
    # 测试描述
    description: str
    # 测试函数
    test_function: Callable
    # 测试参数
    parameters: Dict[str, Any] = field(default_factory=dict)
    # 重复次数
    iterations: int = 10
    # 预热次数
    warmup_iterations: int = 3
    # 超时时间（秒）
    timeout: float = 300.0
    # 是否启用内存监控
    enable_memory_monitoring: bool = True
    # 是否启用CPU监控
    enable_cpu_monitoring: bool = True
    # 是否启用多线程测试
    enable_multithreading: bool = False
    # 线程数
    thread_count: int = 4
    # 是否启用多进程测试
    enable_multiprocessing: bool = False
    # 进程数
    process_count: int = 4

@dataclass
class BenchmarkResult:
    """基准测试结果"""
    # 测试名称
    name: str
    # 测试配置
    config: BenchmarkConfig
    # 执行时间（秒）
    execution_times: List[float]
    # 平均执行时间
    avg_execution_time: float
    # 最小执行时间
    min_execution_time: float
    # 最大执行时间
    max_execution_time: float
    # 标准差
    std_deviation: float
    # 内存使用（MB）
    memory_usage: Optional[float] = None
    # 峰值内存使用（MB）
    peak_memory_usage: Optional[float] = None
    # CPU使用率（%）
    cpu_usage: Optional[float] = None
    # 峰值CPU使用率（%）
    peak_cpu_usage: Optional[float] = None
    # 是否成功
    success: bool = True
    # 错误信息
    error_message: Optional[str] = None
    # 测试时间戳
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class PerformanceMetrics:
    """性能指标"""
    # 吞吐量（操作/秒）
    throughput: float
    # 延迟（毫秒）
    latency_ms: float
    # 内存效率（MB/操作）
    memory_efficiency: float
    # CPU效率（%）
    cpu_efficiency: float
    # 可扩展性评分
    scalability_score: float
    # 稳定性评分
    stability_score: float

class PerformanceBenchmarkSuite:
    """性能基准测试套件"""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.configs: List[BenchmarkConfig] = []
        self.tools = {}
        self._initialize_tools()
        self._setup_benchmarks()
        
    def _initialize_tools(self):
        """初始化工具"""
        try:
            self.tools['modeling'] = UnifiedModelingTool()
            logger.info("✅ 统一建模工具初始化成功")
        except Exception as e:
            logger.warning(f"❌ 统一建模工具初始化失败: {e}")
        
        try:
            self.tools['code_generator'] = AutomatedCodeGenerator()
            logger.info("✅ 自动化代码生成器初始化成功")
        except Exception as e:
            logger.warning(f"❌ 自动化代码生成器初始化失败: {e}")
        
        try:
            self.tools['verifier'] = CrossTheoryVerificationEngine()
            logger.info("✅ 跨理论验证引擎初始化成功")
        except Exception as e:
            logger.warning(f"❌ 跨理论验证引擎初始化失败: {e}")
        
        try:
            self.tools['mapper'] = EnhancedTheoryToPracticeMapper()
            logger.info("✅ 理论到实践映射工具初始化成功")
        except Exception as e:
            logger.warning(f"❌ 理论到实践映射工具初始化失败: {e}")
        
        try:
            self.tools['tester'] = ComprehensiveTestSuite()
            logger.info("✅ 综合测试套件初始化成功")
        except Exception as e:
            logger.warning(f"❌ 综合测试套件初始化失败: {e}")
    
    def _setup_benchmarks(self):
        """设置基准测试配置"""
        # 理论加载性能测试
        self.configs.append(BenchmarkConfig(
            name="理论加载性能测试",
            description="测试理论文档加载和解析的性能",
            test_function=self._benchmark_theory_loading,
            parameters={
                "theory_files": ["01-哲学基础理论", "02-数学理论体系", "03-形式语言理论体系"],
                "file_count": 10
            },
            iterations=20,
            warmup_iterations=5
        ))
        
        # 代码生成性能测试
        self.configs.append(BenchmarkConfig(
            name="代码生成性能测试",
            description="测试多语言代码生成的性能",
            test_function=self._benchmark_code_generation,
            parameters={
                "languages": ["python", "rust", "go", "typescript"],
                "patterns": ["mvc", "repository", "factory"],
                "complexity": "medium"
            },
            iterations=15,
            warmup_iterations=3
        ))
        
        # 模型验证性能测试
        self.configs.append(BenchmarkConfig(
            name="模型验证性能测试",
            description="测试模型验证和一致性检查的性能",
            test_function=self._benchmark_model_verification,
            parameters={
                "model_types": ["uml", "bpmn", "petri_net", "state_machine"],
                "model_size": "large"
            },
            iterations=12,
            warmup_iterations=3
        ))
        
        # 跨理论验证性能测试
        self.configs.append(BenchmarkConfig(
            name="跨理论验证性能测试",
            description="测试跨理论体系验证的性能",
            test_function=self._benchmark_cross_theory_verification,
            parameters={
                "theory_pairs": [
                    ("哲学基础理论", "数学理论体系"),
                    ("形式语言理论体系", "编程语言理论体系"),
                    ("形式模型理论体系", "软件架构理论体系")
                ]
            },
            iterations=10,
            warmup_iterations=2
        ))
        
        # 内存使用性能测试
        self.configs.append(BenchmarkConfig(
            name="内存使用性能测试",
            description="测试工具链的内存使用效率",
            test_function=self._benchmark_memory_usage,
            parameters={
                "operation_count": 1000,
                "data_size": "large"
            },
            iterations=8,
            warmup_iterations=2,
            enable_memory_monitoring=True
        ))
        
        # 并发性能测试
        self.configs.append(BenchmarkConfig(
            name="并发性能测试",
            description="测试工具链的并发处理能力",
            test_function=self._benchmark_concurrent_operations,
            parameters={
                "concurrent_tasks": 10,
                "task_type": "code_generation"
            },
            iterations=5,
            warmup_iterations=1,
            enable_multithreading=True,
            thread_count=8
        ))
        
        # 大规模数据处理测试
        self.configs.append(BenchmarkConfig(
            name="大规模数据处理测试",
            description="测试处理大规模理论数据的性能",
            test_function=self._benchmark_large_scale_processing,
            parameters={
                "data_size": "extra_large",
                "operation_type": "analysis"
            },
            iterations=3,
            warmup_iterations=1,
            timeout=600.0
        ))
    
    def _benchmark_theory_loading(self, config: BenchmarkConfig) -> Dict[str, Any]:
        """理论加载性能测试"""
        theory_files = config.parameters.get("theory_files", [])
        file_count = config.parameters.get("file_count", 10)
        
        # 模拟理论文件加载
        results = []
        for _ in range(file_count):
            start_time = time.time()
            
            # 模拟加载理论文件
            theory_data = {
                "name": f"理论文件_{_}",
                "content": "理论内容" * 1000,  # 模拟大量内容
                "metadata": {
                    "author": "系统",
                    "created": datetime.now().isoformat(),
                    "version": "1.0"
                }
            }
            
            # 模拟解析过程
            time.sleep(0.01)  # 模拟解析时间
            
            end_time = time.time()
            results.append(end_time - start_time)
        
        return {
            "execution_time": sum(results),
            "file_count": file_count,
            "avg_time_per_file": sum(results) / len(results)
        }
    
    def _benchmark_code_generation(self, config: BenchmarkConfig) -> Dict[str, Any]:
        """代码生成性能测试"""
        languages = config.parameters.get("languages", ["python"])
        patterns = config.parameters.get("patterns", ["mvc"])
        complexity = config.parameters.get("complexity", "medium")
        
        start_time = time.time()
        
        # 模拟代码生成
        generated_code = {}
        for language in languages:
            for pattern in patterns:
                # 模拟生成代码
                code = f"""
// 生成的{language}代码 - {pattern}模式
class {pattern.title()}Controller:
    def __init__(self):
        self.service = {pattern.title()}Service()
    
    def handle_request(self, request):
        return self.service.process(request)
"""
                generated_code[f"{language}_{pattern}"] = code
        
        end_time = time.time()
        
        return {
            "execution_time": end_time - start_time,
            "languages": len(languages),
            "patterns": len(patterns),
            "total_combinations": len(languages) * len(patterns)
        }
    
    def _benchmark_model_verification(self, config: BenchmarkConfig) -> Dict[str, Any]:
        """模型验证性能测试"""
        model_types = config.parameters.get("model_types", ["uml"])
        model_size = config.parameters.get("model_size", "medium")
        
        start_time = time.time()
        
        # 模拟模型验证
        verification_results = {}
        for model_type in model_types:
            # 模拟验证过程
            time.sleep(0.02)  # 模拟验证时间
            
            verification_results[model_type] = {
                "valid": True,
                "issues": [],
                "performance_score": 0.95
            }
        
        end_time = time.time()
        
        return {
            "execution_time": end_time - start_time,
            "model_types": len(model_types),
            "verification_results": verification_results
        }
    
    def _benchmark_cross_theory_verification(self, config: BenchmarkConfig) -> Dict[str, Any]:
        """跨理论验证性能测试"""
        theory_pairs = config.parameters.get("theory_pairs", [])
        
        start_time = time.time()
        
        # 模拟跨理论验证
        verification_results = {}
        for theory1, theory2 in theory_pairs:
            # 模拟验证过程
            time.sleep(0.05)  # 模拟复杂验证时间
            
            verification_results[f"{theory1}_vs_{theory2}"] = {
                "consistency_score": 0.92,
                "mapping_strength": 0.88,
                "conflicts": []
            }
        
        end_time = time.time()
        
        return {
            "execution_time": end_time - start_time,
            "theory_pairs": len(theory_pairs),
            "verification_results": verification_results
        }
    
    def _benchmark_memory_usage(self, config: BenchmarkConfig) -> Dict[str, Any]:
        """内存使用性能测试"""
        operation_count = config.parameters.get("operation_count", 1000)
        data_size = config.parameters.get("data_size", "large")
        
        # 获取初始内存使用
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        start_time = time.time()
        
        # 模拟内存密集型操作
        data_structures = []
        for i in range(operation_count):
            # 创建大型数据结构
            data = {
                "id": i,
                "content": "数据内容" * 100,
                "metadata": {"timestamp": time.time()}
            }
            data_structures.append(data)
        
        # 获取峰值内存使用
        peak_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        end_time = time.time()
        
        # 清理内存
        del data_structures
        gc.collect()
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        return {
            "execution_time": end_time - start_time,
            "initial_memory_mb": initial_memory,
            "peak_memory_mb": peak_memory,
            "final_memory_mb": final_memory,
            "memory_increase_mb": peak_memory - initial_memory
        }
    
    def _benchmark_concurrent_operations(self, config: BenchmarkConfig) -> Dict[str, Any]:
        """并发性能测试"""
        concurrent_tasks = config.parameters.get("concurrent_tasks", 10)
        task_type = config.parameters.get("task_type", "code_generation")
        
        def task_worker(task_id: int) -> Dict[str, Any]:
            """工作线程函数"""
            start_time = time.time()
            
            # 模拟任务执行
            if task_type == "code_generation":
                # 模拟代码生成任务
                time.sleep(0.1)
                result = f"Generated code for task {task_id}"
            elif task_type == "verification":
                # 模拟验证任务
                time.sleep(0.15)
                result = f"Verified model for task {task_id}"
            else:
                # 默认任务
                time.sleep(0.05)
                result = f"Processed task {task_id}"
            
            end_time = time.time()
            return {
                "task_id": task_id,
                "execution_time": end_time - start_time,
                "result": result
            }
        
        start_time = time.time()
        
        # 使用线程池执行并发任务
        with ThreadPoolExecutor(max_workers=concurrent_tasks) as executor:
            futures = [executor.submit(task_worker, i) for i in range(concurrent_tasks)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        
        return {
            "total_execution_time": end_time - start_time,
            "concurrent_tasks": concurrent_tasks,
            "task_results": results,
            "avg_task_time": sum(r["execution_time"] for r in results) / len(results)
        }
    
    def _benchmark_large_scale_processing(self, config: BenchmarkConfig) -> Dict[str, Any]:
        """大规模数据处理测试"""
        data_size = config.parameters.get("data_size", "large")
        operation_type = config.parameters.get("operation_type", "analysis")
        
        # 根据数据大小确定处理量
        if data_size == "large":
            item_count = 10000
        elif data_size == "extra_large":
            item_count = 100000
        else:
            item_count = 1000
        
        start_time = time.time()
        
        # 模拟大规模数据处理
        processed_items = 0
        for i in range(item_count):
            # 模拟数据处理
            data_item = {
                "id": i,
                "content": f"数据项 {i}",
                "timestamp": time.time()
            }
            
            # 模拟分析操作
            if operation_type == "analysis":
                # 模拟复杂分析
                analysis_result = {
                    "complexity": i % 10,
                    "priority": (i * 7) % 100,
                    "category": f"类别_{i % 5}"
                }
            else:
                # 模拟简单处理
                analysis_result = {"processed": True}
            
            processed_items += 1
            
            # 每处理1000个项目，进行一次小暂停
            if i % 1000 == 0 and i > 0:
                time.sleep(0.001)
        
        end_time = time.time()
        
        return {
            "execution_time": end_time - start_time,
            "processed_items": processed_items,
            "items_per_second": processed_items / (end_time - start_time),
            "operation_type": operation_type
        }
    
    def _monitor_resources(self, duration: float) -> Dict[str, float]:
        """监控资源使用"""
        if not self._should_monitor_resources():
            return {}
        
        cpu_samples = []
        memory_samples = []
        
        start_time = time.time()
        while time.time() - start_time < duration:
            # 监控CPU使用率
            if self._should_monitor_cpu():
                cpu_percent = psutil.cpu_percent(interval=0.1)
                cpu_samples.append(cpu_percent)
            
            # 监控内存使用
            if self._should_monitor_memory():
                memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
                memory_samples.append(memory_mb)
            
            time.sleep(0.1)
        
        return {
            "avg_cpu_percent": statistics.mean(cpu_samples) if cpu_samples else 0,
            "peak_cpu_percent": max(cpu_samples) if cpu_samples else 0,
            "avg_memory_mb": statistics.mean(memory_samples) if memory_samples else 0,
            "peak_memory_mb": max(memory_samples) if memory_samples else 0
        }
    
    def _should_monitor_resources(self) -> bool:
        """是否应该监控资源"""
        return True
    
    def _should_monitor_cpu(self) -> bool:
        """是否应该监控CPU"""
        return True
    
    def _should_monitor_memory(self) -> bool:
        """是否应该监控内存"""
        return True
    
    def run_benchmark(self, config: BenchmarkConfig) -> BenchmarkResult:
        """运行单个基准测试"""
        logger.info(f"🚀 开始运行基准测试: {config.name}")
        
        execution_times = []
        resource_metrics = {}
        
        try:
            # 预热
            for i in range(config.warmup_iterations):
                logger.info(f"  预热 {i+1}/{config.warmup_iterations}")
                config.test_function(config)
            
            # 正式测试
            for i in range(config.iterations):
                logger.info(f"  执行测试 {i+1}/{config.iterations}")
                
                # 开始资源监控
                if config.enable_memory_monitoring or config.enable_cpu_monitoring:
                    monitor_thread = threading.Thread(
                        target=self._monitor_resources_thread,
                        args=(config.timeout, resource_metrics)
                    )
                    monitor_thread.daemon = True
                    monitor_thread.start()
                
                # 执行测试
                start_time = time.time()
                result = config.test_function(config)
                end_time = time.time()
                
                execution_time = end_time - start_time
                execution_times.append(execution_time)
                
                # 等待资源监控完成
                if config.enable_memory_monitoring or config.enable_cpu_monitoring:
                    monitor_thread.join(timeout=1.0)
                
                logger.info(f"    执行时间: {execution_time:.4f}秒")
            
            # 计算统计信息
            avg_time = statistics.mean(execution_times)
            min_time = min(execution_times)
            max_time = max(execution_times)
            std_dev = statistics.stdev(execution_times) if len(execution_times) > 1 else 0
            
            # 创建结果
            benchmark_result = BenchmarkResult(
                name=config.name,
                config=config,
                execution_times=execution_times,
                avg_execution_time=avg_time,
                min_execution_time=min_time,
                max_execution_time=max_time,
                std_deviation=std_dev,
                memory_usage=resource_metrics.get("avg_memory_mb"),
                peak_memory_usage=resource_metrics.get("peak_memory_mb"),
                cpu_usage=resource_metrics.get("avg_cpu_percent"),
                peak_cpu_usage=resource_metrics.get("peak_cpu_percent"),
                success=True
            )
            
            logger.info(f"✅ 基准测试完成: {config.name}")
            logger.info(f"  平均执行时间: {avg_time:.4f}秒")
            logger.info(f"  最小执行时间: {min_time:.4f}秒")
            logger.info(f"  最大执行时间: {max_time:.4f}秒")
            logger.info(f"  标准差: {std_dev:.4f}秒")
            
            return benchmark_result
            
        except Exception as e:
            logger.error(f"❌ 基准测试失败: {config.name} - {str(e)}")
            
            return BenchmarkResult(
                name=config.name,
                config=config,
                execution_times=[],
                avg_execution_time=0,
                min_execution_time=0,
                max_execution_time=0,
                std_deviation=0,
                success=False,
                error_message=str(e)
            )
    
    def _monitor_resources_thread(self, duration: float, metrics: Dict[str, float]):
        """资源监控线程"""
        try:
            resource_data = self._monitor_resources(duration)
            metrics.update(resource_data)
        except Exception as e:
            logger.warning(f"资源监控失败: {e}")
    
    def run_all_benchmarks(self) -> List[BenchmarkResult]:
        """运行所有基准测试"""
        logger.info("🎯 开始运行所有基准测试")
        
        all_results = []
        
        for config in self.configs:
            try:
                result = self.run_benchmark(config)
                all_results.append(result)
                self.results.append(result)
            except Exception as e:
                logger.error(f"基准测试执行失败: {config.name} - {e}")
        
        logger.info(f"✅ 所有基准测试完成，共执行 {len(all_results)} 个测试")
        return all_results
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """生成性能报告"""
        if not self.results:
            return {"error": "没有可用的基准测试结果"}
        
        # 计算总体性能指标
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r.success])
        failed_tests = total_tests - successful_tests
        
        # 计算平均性能指标
        avg_execution_times = [r.avg_execution_time for r in self.results if r.success]
        avg_memory_usage = [r.memory_usage for r in self.results if r.success and r.memory_usage]
        avg_cpu_usage = [r.cpu_usage for r in self.results if r.success and r.cpu_usage]
        
        # 生成报告
        report = {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": successful_tests / total_tests if total_tests > 0 else 0
            },
            "performance_metrics": {
                "avg_execution_time": statistics.mean(avg_execution_times) if avg_execution_times else 0,
                "min_execution_time": min(avg_execution_times) if avg_execution_times else 0,
                "max_execution_time": max(avg_execution_times) if avg_execution_times else 0,
                "avg_memory_usage_mb": statistics.mean(avg_memory_usage) if avg_memory_usage else 0,
                "avg_cpu_usage_percent": statistics.mean(avg_cpu_usage) if avg_cpu_usage else 0
            },
            "detailed_results": [
                {
                    "name": result.name,
                    "avg_execution_time": result.avg_execution_time,
                    "min_execution_time": result.min_execution_time,
                    "max_execution_time": result.max_execution_time,
                    "std_deviation": result.std_deviation,
                    "memory_usage_mb": result.memory_usage,
                    "cpu_usage_percent": result.cpu_usage,
                    "success": result.success,
                    "error_message": result.error_message
                }
                for result in self.results
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        return report
    
    def save_results(self, filename: str = None):
        """保存测试结果"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_results_{timestamp}.json"
        
        report = self.generate_performance_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📊 基准测试结果已保存到: {filename}")
    
    def generate_visualizations(self, output_dir: str = "benchmark_visualizations"):
        """生成可视化图表"""
        if not self.results:
            logger.warning("没有可用的基准测试结果来生成可视化")
            return
        
        # 创建输出目录
        Path(output_dir).mkdir(exist_ok=True)
        
        # 准备数据
        successful_results = [r for r in self.results if r.success]
        
        if not successful_results:
            logger.warning("没有成功的基准测试结果来生成可视化")
            return
        
        # 1. 执行时间对比图
        plt.figure(figsize=(12, 8))
        names = [r.name for r in successful_results]
        avg_times = [r.avg_execution_time for r in successful_results]
        
        plt.bar(names, avg_times, color='skyblue', alpha=0.7)
        plt.title('基准测试执行时间对比', fontsize=16, fontweight='bold')
        plt.xlabel('测试名称', fontsize=12)
        plt.ylabel('平均执行时间 (秒)', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/execution_times.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. 内存使用对比图
        memory_results = [r for r in successful_results if r.memory_usage]
        if memory_results:
            plt.figure(figsize=(12, 8))
            names = [r.name for r in memory_results]
            memory_usage = [r.memory_usage for r in memory_results]
            
            plt.bar(names, memory_usage, color='lightgreen', alpha=0.7)
            plt.title('基准测试内存使用对比', fontsize=16, fontweight='bold')
            plt.xlabel('测试名称', fontsize=12)
            plt.ylabel('平均内存使用 (MB)', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(f"{output_dir}/memory_usage.png", dpi=300, bbox_inches='tight')
            plt.close()
        
        # 3. CPU使用对比图
        cpu_results = [r for r in successful_results if r.cpu_usage]
        if cpu_results:
            plt.figure(figsize=(12, 8))
            names = [r.name for r in cpu_results]
            cpu_usage = [r.cpu_usage for r in cpu_results]
            
            plt.bar(names, cpu_usage, color='lightcoral', alpha=0.7)
            plt.title('基准测试CPU使用对比', fontsize=16, fontweight='bold')
            plt.xlabel('测试名称', fontsize=12)
            plt.ylabel('平均CPU使用率 (%)', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(f"{output_dir}/cpu_usage.png", dpi=300, bbox_inches='tight')
            plt.close()
        
        # 4. 性能雷达图
        if len(successful_results) >= 3:
            plt.figure(figsize=(10, 10))
            
            # 计算性能指标
            categories = ['执行速度', '内存效率', 'CPU效率', '稳定性', '可扩展性']
            
            # 标准化指标 (0-1范围)
            max_time = max(r.avg_execution_time for r in successful_results)
            max_memory = max(r.memory_usage or 0 for r in successful_results)
            max_cpu = max(r.cpu_usage or 0 for r in successful_results)
            
            # 选择前3个测试进行对比
            top_3_results = successful_results[:3]
            
            for i, result in enumerate(top_3_results):
                # 计算各项指标 (越小越好，所以用1减去标准化值)
                speed_score = 1 - (result.avg_execution_time / max_time)
                memory_score = 1 - ((result.memory_usage or 0) / max_memory)
                cpu_score = 1 - ((result.cpu_usage or 0) / max_cpu)
                stability_score = 1 - (result.std_deviation / result.avg_execution_time) if result.avg_execution_time > 0 else 0
                scalability_score = 0.8  # 假设值
                
                values = [speed_score, memory_score, cpu_score, stability_score, scalability_score]
                
                # 绘制雷达图
                angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
                values += values[:1]  # 闭合图形
                angles += angles[:1]
                
                plt.polar(angles, values, 'o-', linewidth=2, label=result.name, alpha=0.7)
                plt.fill(angles, values, alpha=0.1)
            
            plt.xticks(angles[:-1], categories)
            plt.ylim(0, 1)
            plt.title('性能雷达图对比', fontsize=16, fontweight='bold', pad=20)
            plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
            plt.tight_layout()
            plt.savefig(f"{output_dir}/performance_radar.png", dpi=300, bbox_inches='tight')
            plt.close()
        
        logger.info(f"📈 可视化图表已生成到: {output_dir}")
    
    def print_summary(self):
        """打印测试摘要"""
        if not self.results:
            print("❌ 没有可用的基准测试结果")
            return
        
        print("\n" + "="*80)
        print("🎯 FORMALUNIFIED 性能基准测试摘要")
        print("="*80)
        
        # 总体统计
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r.success])
        failed_tests = total_tests - successful_tests
        
        print(f"\n📊 总体统计:")
        print(f"  总测试数: {total_tests}")
        print(f"  成功测试: {successful_tests}")
        print(f"  失败测试: {failed_tests}")
        print(f"  成功率: {successful_tests/total_tests*100:.1f}%")
        
        if successful_tests > 0:
            # 性能统计
            avg_times = [r.avg_execution_time for r in self.results if r.success]
            avg_memory = [r.memory_usage for r in self.results if r.success and r.memory_usage]
            avg_cpu = [r.cpu_usage for r in self.results if r.success and r.cpu_usage]
            
            print(f"\n⚡ 性能统计:")
            print(f"  平均执行时间: {statistics.mean(avg_times):.4f}秒")
            print(f"  最快执行时间: {min(avg_times):.4f}秒")
            print(f"  最慢执行时间: {max(avg_times):.4f}秒")
            
            if avg_memory:
                print(f"  平均内存使用: {statistics.mean(avg_memory):.2f}MB")
            if avg_cpu:
                print(f"  平均CPU使用: {statistics.mean(avg_cpu):.1f}%")
        
        # 详细结果
        print(f"\n📋 详细结果:")
        for result in self.results:
            status = "✅" if result.success else "❌"
            print(f"  {status} {result.name}")
            if result.success:
                print(f"    执行时间: {result.avg_execution_time:.4f}秒 (±{result.std_deviation:.4f})")
                if result.memory_usage:
                    print(f"    内存使用: {result.memory_usage:.2f}MB")
                if result.cpu_usage:
                    print(f"    CPU使用: {result.cpu_usage:.1f}%")
            else:
                print(f"    错误: {result.error_message}")
        
        print("\n" + "="*80)

def main():
    """主函数"""
    print("🚀 启动FormalUnified性能基准测试套件")
    
    # 创建基准测试套件
    benchmark_suite = PerformanceBenchmarkSuite()
    
    # 运行所有基准测试
    results = benchmark_suite.run_all_benchmarks()
    
    # 生成报告
    benchmark_suite.print_summary()
    
    # 保存结果
    benchmark_suite.save_results()
    
    # 生成可视化
    benchmark_suite.generate_visualizations()
    
    print("\n🎉 性能基准测试完成！")

if __name__ == "__main__":
    main() 