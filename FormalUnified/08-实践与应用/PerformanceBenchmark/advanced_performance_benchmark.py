#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级性能基准测试工具
Advanced Performance Benchmark Tool

提供全面的性能测试功能，包括负载测试、压力测试、稳定性测试等
"""

import asyncio
import aiohttp
import time
import statistics
import psutil
import threading
import json
import yaml
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BenchmarkResult:
    """基准测试结果"""
    test_name: str
    start_time: datetime
    end_time: datetime
    total_requests: int
    successful_requests: int
    failed_requests: int
    response_times: List[float]
    throughput: float
    error_rate: float
    cpu_usage: List[float]
    memory_usage: List[float]
    network_io: Dict[str, float]
    custom_metrics: Dict[str, Any]

class AdvancedPerformanceBenchmark:
    """高级性能基准测试工具"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.results = []
        self.monitoring_active = False
        self.metrics_collector = MetricsCollector()
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            "test_scenarios": {
                "load_test": {
                    "duration": 300,
                    "ramp_up_time": 60,
                    "max_users": 1000,
                    "target_rps": 100
                },
                "stress_test": {
                    "duration": 600,
                    "ramp_up_time": 120,
                    "max_users": 2000,
                    "target_rps": 200
                },
                "spike_test": {
                    "duration": 180,
                    "spike_duration": 30,
                    "normal_rps": 50,
                    "spike_rps": 500
                },
                "endurance_test": {
                    "duration": 3600,
                    "steady_rps": 80,
                    "max_users": 500
                }
            },
            "targets": {
                "user_service": "http://localhost:8081",
                "product_service": "http://localhost:8082",
                "order_service": "http://localhost:8083",
                "payment_service": "http://localhost:8084"
            },
            "monitoring": {
                "collect_system_metrics": True,
                "collect_network_metrics": True,
                "metrics_interval": 1.0
            },
            "reporting": {
                "generate_charts": True,
                "save_results": True,
                "output_format": "json"
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.endswith('.json'):
                    user_config = json.load(f)
                else:
                    user_config = yaml.safe_load(f)
            
            # 合并配置
            self._merge_config(default_config, user_config)
        
        return default_config
    
    def _merge_config(self, default: Dict, user: Dict):
        """合并配置"""
        for key, value in user.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_config(default[key], value)
            else:
                default[key] = value
    
    async def run_load_test(self, target_url: str, scenario: str = "load_test") -> BenchmarkResult:
        """运行负载测试"""
        logger.info(f"开始负载测试: {target_url}")
        
        config = self.config["test_scenarios"][scenario]
        start_time = datetime.now()
        
        # 启动系统监控
        self.monitoring_active = True
        monitor_thread = threading.Thread(target=self._monitor_system_metrics)
        monitor_thread.start()
        
        # 执行测试
        result = await self._execute_load_test(target_url, config)
        
        # 停止监控
        self.monitoring_active = False
        monitor_thread.join()
        
        result.end_time = datetime.now()
        result.test_name = f"load_test_{scenario}"
        
        self.results.append(result)
        return result
    
    async def _execute_load_test(self, target_url: str, config: Dict[str, Any]) -> BenchmarkResult:
        """执行负载测试"""
        total_requests = 0
        successful_requests = 0
        failed_requests = 0
        response_times = []
        
        async with aiohttp.ClientSession() as session:
            # 爬坡阶段
            ramp_up_duration = config["ramp_up_time"]
            target_rps = config["target_rps"]
            max_users = config["max_users"]
            
            # 计算爬坡阶段的RPS增长
            ramp_up_rps = target_rps / ramp_up_duration
            
            current_rps = 0
            start_time = time.time()
            
            while time.time() - start_time < config["duration"]:
                elapsed = time.time() - start_time
                
                # 爬坡阶段
                if elapsed < ramp_up_duration:
                    current_rps = min(ramp_up_rps * elapsed, target_rps)
                else:
                    current_rps = target_rps
                
                # 计算当前并发用户数
                current_users = min(int(current_rps * 2), max_users)
                
                # 创建并发任务
                tasks = []
                for _ in range(current_users):
                    task = asyncio.create_task(self._make_request(session, target_url))
                    tasks.append(task)
                
                # 等待所有请求完成
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 统计结果
                for result in results:
                    total_requests += 1
                    if isinstance(result, dict):
                        successful_requests += 1
                        response_times.append(result["response_time"])
                    else:
                        failed_requests += 1
                
                # 控制请求频率
                await asyncio.sleep(1.0 / current_rps if current_rps > 0 else 1.0)
        
        # 计算指标
        throughput = successful_requests / config["duration"]
        error_rate = failed_requests / total_requests if total_requests > 0 else 0
        
        return BenchmarkResult(
            test_name="",
            start_time=datetime.now(),
            end_time=datetime.now(),
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            response_times=response_times,
            throughput=throughput,
            error_rate=error_rate,
            cpu_usage=self.metrics_collector.get_cpu_usage(),
            memory_usage=self.metrics_collector.get_memory_usage(),
            network_io=self.metrics_collector.get_network_io(),
            custom_metrics={}
        )
    
    async def _make_request(self, session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
        """发送单个请求"""
        start_time = time.time()
        try:
            async with session.get(url) as response:
                response_time = time.time() - start_time
                return {
                    "status": response.status,
                    "response_time": response_time,
                    "success": response.status < 400
                }
        except Exception as e:
            response_time = time.time() - start_time
            return {
                "status": 0,
                "response_time": response_time,
                "success": False,
                "error": str(e)
            }
    
    def _monitor_system_metrics(self):
        """监控系统指标"""
        while self.monitoring_active:
            self.metrics_collector.collect_metrics()
            time.sleep(self.config["monitoring"]["metrics_interval"])
    
    async def run_stress_test(self, target_url: str) -> BenchmarkResult:
        """运行压力测试"""
        logger.info(f"开始压力测试: {target_url}")
        return await self.run_load_test(target_url, "stress_test")
    
    async def run_spike_test(self, target_url: str) -> BenchmarkResult:
        """运行尖峰测试"""
        logger.info(f"开始尖峰测试: {target_url}")
        
        config = self.config["test_scenarios"]["spike_test"]
        start_time = datetime.now()
        
        # 启动系统监控
        self.monitoring_active = True
        monitor_thread = threading.Thread(target=self._monitor_system_metrics)
        monitor_thread.start()
        
        # 执行测试
        result = await self._execute_spike_test(target_url, config)
        
        # 停止监控
        self.monitoring_active = False
        monitor_thread.join()
        
        result.end_time = datetime.now()
        result.test_name = "spike_test"
        
        self.results.append(result)
        return result
    
    async def _execute_spike_test(self, target_url: str, config: Dict[str, Any]) -> BenchmarkResult:
        """执行尖峰测试"""
        total_requests = 0
        successful_requests = 0
        failed_requests = 0
        response_times = []
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            
            while time.time() - start_time < config["duration"]:
                elapsed = time.time() - start_time
                
                # 确定当前RPS
                if elapsed < config["spike_duration"]:
                    current_rps = config["spike_rps"]
                else:
                    current_rps = config["normal_rps"]
                
                # 创建并发任务
                tasks = []
                for _ in range(int(current_rps)):
                    task = asyncio.create_task(self._make_request(session, target_url))
                    tasks.append(task)
                
                # 等待所有请求完成
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 统计结果
                for result in results:
                    total_requests += 1
                    if isinstance(result, dict):
                        successful_requests += 1
                        response_times.append(result["response_time"])
                    else:
                        failed_requests += 1
                
                # 控制请求频率
                await asyncio.sleep(1.0)
        
        # 计算指标
        throughput = successful_requests / config["duration"]
        error_rate = failed_requests / total_requests if total_requests > 0 else 0
        
        return BenchmarkResult(
            test_name="",
            start_time=datetime.now(),
            end_time=datetime.now(),
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            response_times=response_times,
            throughput=throughput,
            error_rate=error_rate,
            cpu_usage=self.metrics_collector.get_cpu_usage(),
            memory_usage=self.metrics_collector.get_memory_usage(),
            network_io=self.metrics_collector.get_network_io(),
            custom_metrics={}
        )
    
    async def run_endurance_test(self, target_url: str) -> BenchmarkResult:
        """运行耐久性测试"""
        logger.info(f"开始耐久性测试: {target_url}")
        return await self.run_load_test(target_url, "endurance_test")
    
    async def run_comprehensive_test_suite(self) -> List[BenchmarkResult]:
        """运行综合测试套件"""
        logger.info("开始综合测试套件")
        
        results = []
        targets = self.config["targets"]
        
        for service_name, target_url in targets.items():
            logger.info(f"测试服务: {service_name}")
            
            # 负载测试
            load_result = await self.run_load_test(target_url, "load_test")
            results.append(load_result)
            
            # 压力测试
            stress_result = await self.run_stress_test(target_url)
            results.append(stress_result)
            
            # 尖峰测试
            spike_result = await self.run_spike_test(target_url)
            results.append(spike_result)
            
            # 耐久性测试
            endurance_result = await self.run_endurance_test(target_url)
            results.append(endurance_result)
        
        return results
    
    def generate_report(self, output_dir: str = "benchmark_reports"):
        """生成测试报告"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 生成JSON报告
        if self.config["reporting"]["output_format"] == "json":
            report_file = output_path / f"benchmark_report_{timestamp}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(result) for result in self.results], f, indent=2, default=str)
        
        # 生成图表
        if self.config["reporting"]["generate_charts"]:
            self._generate_charts(output_path, timestamp)
        
        # 生成汇总报告
        self._generate_summary_report(output_path, timestamp)
        
        logger.info(f"测试报告已生成: {output_path}")
    
    def _generate_charts(self, output_path: Path, timestamp: str):
        """生成图表"""
        for result in self.results:
            # 响应时间分布图
            plt.figure(figsize=(12, 8))
            
            plt.subplot(2, 2, 1)
            plt.hist(result.response_times, bins=50, alpha=0.7)
            plt.title(f"{result.test_name} - 响应时间分布")
            plt.xlabel("响应时间 (秒)")
            plt.ylabel("频次")
            
            # CPU使用率图
            plt.subplot(2, 2, 2)
            plt.plot(result.cpu_usage)
            plt.title(f"{result.test_name} - CPU使用率")
            plt.xlabel("时间")
            plt.ylabel("CPU使用率 (%)")
            
            # 内存使用率图
            plt.subplot(2, 2, 3)
            plt.plot(result.memory_usage)
            plt.title(f"{result.test_name} - 内存使用率")
            plt.xlabel("时间")
            plt.ylabel("内存使用率 (%)")
            
            # 吞吐量图
            plt.subplot(2, 2, 4)
            plt.bar(['成功', '失败'], [result.successful_requests, result.failed_requests])
            plt.title(f"{result.test_name} - 请求统计")
            plt.ylabel("请求数量")
            
            plt.tight_layout()
            plt.savefig(output_path / f"{result.test_name}_{timestamp}.png", dpi=300, bbox_inches='tight')
            plt.close()
    
    def _generate_summary_report(self, output_path: Path, timestamp: str):
        """生成汇总报告"""
        report_file = output_path / f"summary_report_{timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 性能基准测试汇总报告\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for result in self.results:
                f.write(f"## {result.test_name}\n\n")
                f.write(f"- 测试时间: {result.start_time} - {result.end_time}\n")
                f.write(f"- 总请求数: {result.total_requests}\n")
                f.write(f"- 成功请求: {result.successful_requests}\n")
                f.write(f"- 失败请求: {result.failed_requests}\n")
                f.write(f"- 吞吐量: {result.throughput:.2f} RPS\n")
                f.write(f"- 错误率: {result.error_rate:.2%}\n")
                
                if result.response_times:
                    f.write(f"- 平均响应时间: {statistics.mean(result.response_times):.3f}秒\n")
                    f.write(f"- 95%响应时间: {np.percentile(result.response_times, 95):.3f}秒\n")
                    f.write(f"- 99%响应时间: {np.percentile(result.response_times, 99):.3f}秒\n")
                
                f.write("\n")

class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.cpu_usage = []
        self.memory_usage = []
        self.network_io = {"bytes_sent": 0, "bytes_recv": 0}
        self.start_time = time.time()
    
    def collect_metrics(self):
        """收集系统指标"""
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        self.cpu_usage.append(cpu_percent)
        
        # 内存使用率
        memory = psutil.virtual_memory()
        self.memory_usage.append(memory.percent)
        
        # 网络IO
        network = psutil.net_io_counters()
        self.network_io["bytes_sent"] = network.bytes_sent
        self.network_io["bytes_recv"] = network.bytes_recv
    
    def get_cpu_usage(self) -> List[float]:
        """获取CPU使用率历史"""
        return self.cpu_usage.copy()
    
    def get_memory_usage(self) -> List[float]:
        """获取内存使用率历史"""
        return self.memory_usage.copy()
    
    def get_network_io(self) -> Dict[str, float]:
        """获取网络IO统计"""
        return self.network_io.copy()

async def main():
    """主函数"""
    # 创建基准测试工具
    benchmark = AdvancedPerformanceBenchmark()
    
    # 运行综合测试套件
    results = await benchmark.run_comprehensive_test_suite()
    
    # 生成报告
    benchmark.generate_report()
    
    # 打印汇总信息
    print("\n=== 性能基准测试完成 ===")
    for result in results:
        print(f"\n{result.test_name}:")
        print(f"  吞吐量: {result.throughput:.2f} RPS")
        print(f"  错误率: {result.error_rate:.2%}")
        if result.response_times:
            print(f"  平均响应时间: {statistics.mean(result.response_times):.3f}秒")

if __name__ == "__main__":
    asyncio.run(main()) 