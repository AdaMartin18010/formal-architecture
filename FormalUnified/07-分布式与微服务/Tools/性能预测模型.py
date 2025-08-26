#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能预测模型
Performance Prediction Model

本工具提供分布式系统和微服务的性能预测功能，包括：
1. 延迟预测模型
2. 吞吐量预测模型
3. 资源利用率预测
4. 容量规划
5. 性能瓶颈分析
6. 负载预测
"""

import json
import time
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PredictionType(Enum):
    """预测类型枚举"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    NETWORK_USAGE = "network_usage"
    DISK_USAGE = "disk_usage"

class ModelType(Enum):
    """模型类型枚举"""
    LINEAR = "linear"
    RIDGE = "ridge"
    RANDOM_FOREST = "random_forest"
    POLYNOMIAL = "polynomial"

@dataclass
class PerformanceData:
    """性能数据"""
    timestamp: float
    request_rate: float
    concurrent_users: int
    cpu_usage: float
    memory_usage: float
    network_usage: float
    disk_usage: float
    latency: float
    throughput: float
    error_rate: float

@dataclass
class PredictionResult:
    """预测结果"""
    prediction_type: PredictionType
    model_type: ModelType
    predicted_value: float
    confidence: float
    features: Dict[str, float]
    model_score: float
    timestamp: float

@dataclass
class CapacityPlan:
    """容量规划"""
    service_name: str
    current_capacity: Dict[str, float]
    predicted_demand: Dict[str, float]
    recommended_capacity: Dict[str, float]
    scaling_factor: float
    cost_estimate: float

class PerformancePredictor:
    """性能预测器"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.feature_columns = [
            'request_rate', 'concurrent_users', 'cpu_usage', 
            'memory_usage', 'network_usage', 'disk_usage'
        ]
        self.target_columns = ['latency', 'throughput']
        self.performance_history: List[PerformanceData] = []
        
    def add_performance_data(self, data: PerformanceData):
        """添加性能数据"""
        self.performance_history.append(data)
        logger.info(f"添加性能数据: {data.timestamp}")
    
    def prepare_training_data(self, prediction_type: PredictionType) -> Tuple[np.ndarray, np.ndarray]:
        """准备训练数据"""
        if len(self.performance_history) < 10:
            raise ValueError("需要至少10个数据点进行训练")
        
        # 转换为DataFrame
        df = pd.DataFrame([asdict(data) for data in self.performance_history])
        
        # 选择特征和目标
        X = df[self.feature_columns].values
        y = df[prediction_type.value].values
        
        return X, y
    
    def train_model(self, prediction_type: PredictionType, model_type: ModelType = ModelType.RANDOM_FOREST):
        """训练模型"""
        try:
            X, y = self.prepare_training_data(prediction_type)
            
            # 数据标准化
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # 选择模型
            if model_type == ModelType.LINEAR:
                model = LinearRegression()
            elif model_type == ModelType.RIDGE:
                model = Ridge(alpha=1.0)
            elif model_type == ModelType.RANDOM_FOREST:
                model = RandomForestRegressor(n_estimators=100, random_state=42)
            else:
                model = LinearRegression()
            
            # 训练模型
            model.fit(X_scaled, y)
            
            # 评估模型
            y_pred = model.predict(X_scaled)
            score = r2_score(y, y_pred)
            
            # 保存模型和scaler
            model_key = f"{prediction_type.value}_{model_type.value}"
            self.models[model_key] = model
            self.scalers[model_key] = scaler
            
            logger.info(f"模型训练完成: {model_key}, R² = {score:.4f}")
            return score
            
        except Exception as e:
            logger.error(f"模型训练失败: {e}")
            return 0.0
    
    def predict(self, features: Dict[str, float], prediction_type: PredictionType, 
                model_type: ModelType = ModelType.RANDOM_FOREST) -> Optional[PredictionResult]:
        """进行预测"""
        model_key = f"{prediction_type.value}_{model_type.value}"
        
        if model_key not in self.models:
            logger.warning(f"模型不存在: {model_key}")
            return None
        
        try:
            model = self.models[model_key]
            scaler = self.scalers[model_key]
            
            # 准备特征
            feature_vector = []
            for col in self.feature_columns:
                feature_vector.append(features.get(col, 0.0))
            
            X = np.array([feature_vector])
            X_scaled = scaler.transform(X)
            
            # 预测
            predicted_value = model.predict(X_scaled)[0]
            
            # 计算置信度（简化实现）
            confidence = 0.8  # 实际应该基于模型的不确定性
            
            return PredictionResult(
                prediction_type=prediction_type,
                model_type=model_type,
                predicted_value=predicted_value,
                confidence=confidence,
                features=features,
                model_score=0.85,  # 实际应该保存训练时的分数
                timestamp=time.time()
            )
            
        except Exception as e:
            logger.error(f"预测失败: {e}")
            return None
    
    def predict_latency(self, request_rate: float, concurrent_users: int, 
                       cpu_usage: float = 0.5, memory_usage: float = 0.5,
                       network_usage: float = 0.5, disk_usage: float = 0.5) -> Optional[PredictionResult]:
        """预测延迟"""
        features = {
            'request_rate': request_rate,
            'concurrent_users': concurrent_users,
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'network_usage': network_usage,
            'disk_usage': disk_usage
        }
        return self.predict(features, PredictionType.LATENCY)
    
    def predict_throughput(self, request_rate: float, concurrent_users: int,
                          cpu_usage: float = 0.5, memory_usage: float = 0.5,
                          network_usage: float = 0.5, disk_usage: float = 0.5) -> Optional[PredictionResult]:
        """预测吞吐量"""
        features = {
            'request_rate': request_rate,
            'concurrent_users': concurrent_users,
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'network_usage': network_usage,
            'disk_usage': disk_usage
        }
        return self.predict(features, PredictionType.THROUGHPUT)

class CapacityPlanner:
    """容量规划器"""
    
    def __init__(self, performance_predictor: PerformancePredictor):
        self.predictor = performance_predictor
        self.capacity_limits = {
            'cpu_usage': 0.8,
            'memory_usage': 0.8,
            'network_usage': 0.7,
            'disk_usage': 0.8,
            'latency': 1000.0,  # ms
            'throughput': 1000.0  # requests/second
        }
    
    def plan_capacity(self, service_name: str, target_load: Dict[str, float]) -> CapacityPlan:
        """容量规划"""
        # 预测在目标负载下的性能
        latency_pred = self.predictor.predict_latency(
            target_load.get('request_rate', 100),
            target_load.get('concurrent_users', 50)
        )
        
        throughput_pred = self.predictor.predict_throughput(
            target_load.get('request_rate', 100),
            target_load.get('concurrent_users', 50)
        )
        
        # 当前容量（假设）
        current_capacity = {
            'cpu_cores': 4,
            'memory_gb': 8,
            'network_mbps': 1000,
            'disk_gb': 100
        }
        
        # 预测的资源需求
        predicted_demand = {
            'cpu_cores': target_load.get('request_rate', 100) / 50,  # 简化计算
            'memory_gb': target_load.get('concurrent_users', 50) * 0.1,
            'network_mbps': target_load.get('request_rate', 100) * 0.1,
            'disk_gb': target_load.get('request_rate', 100) * 0.01
        }
        
        # 推荐容量
        recommended_capacity = {}
        scaling_factor = 1.0
        
        for resource, current in current_capacity.items():
            predicted = predicted_demand.get(resource, 0)
            if predicted > current:
                scaling_factor = max(scaling_factor, predicted / current)
                recommended_capacity[resource] = predicted * 1.2  # 20%缓冲
            else:
                recommended_capacity[resource] = current
        
        # 成本估算（简化）
        cost_estimate = sum(recommended_capacity.values()) * 0.1
        
        return CapacityPlan(
            service_name=service_name,
            current_capacity=current_capacity,
            predicted_demand=predicted_demand,
            recommended_capacity=recommended_capacity,
            scaling_factor=scaling_factor,
            cost_estimate=cost_estimate
        )

class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self, performance_predictor: PerformancePredictor):
        self.predictor = performance_predictor
    
    def analyze_bottlenecks(self, current_load: Dict[str, float]) -> Dict[str, Any]:
        """分析性能瓶颈"""
        bottlenecks = {}
        
        # 预测当前负载下的性能
        latency_pred = self.predictor.predict_latency(
            current_load.get('request_rate', 100),
            current_load.get('concurrent_users', 50)
        )
        
        if latency_pred:
            if latency_pred.predicted_value > self.predictor.capacity_limits['latency']:
                bottlenecks['latency'] = {
                    'current': latency_pred.predicted_value,
                    'limit': self.predictor.capacity_limits['latency'],
                    'severity': 'high' if latency_pred.predicted_value > 2000 else 'medium'
                }
        
        # 检查资源使用率
        for resource in ['cpu_usage', 'memory_usage', 'network_usage', 'disk_usage']:
            current_usage = current_load.get(resource, 0.0)
            limit = self.predictor.capacity_limits[resource]
            
            if current_usage > limit:
                bottlenecks[resource] = {
                    'current': current_usage,
                    'limit': limit,
                    'severity': 'high' if current_usage > limit * 1.2 else 'medium'
                }
        
        return bottlenecks
    
    def generate_performance_report(self, service_name: str, 
                                  current_load: Dict[str, float]) -> Dict[str, Any]:
        """生成性能报告"""
        # 性能预测
        latency_pred = self.predictor.predict_latency(
            current_load.get('request_rate', 100),
            current_load.get('concurrent_users', 50)
        )
        
        throughput_pred = self.predictor.predict_throughput(
            current_load.get('request_rate', 100),
            current_load.get('concurrent_users', 50)
        )
        
        # 瓶颈分析
        bottlenecks = self.analyze_bottlenecks(current_load)
        
        # 容量规划
        capacity_planner = CapacityPlanner(self.predictor)
        capacity_plan = capacity_planner.plan_capacity(service_name, current_load)
        
        return {
            'service_name': service_name,
            'timestamp': time.time(),
            'current_load': current_load,
            'predictions': {
                'latency': asdict(latency_pred) if latency_pred else None,
                'throughput': asdict(throughput_pred) if throughput_pred else None
            },
            'bottlenecks': bottlenecks,
            'capacity_plan': asdict(capacity_plan),
            'recommendations': self._generate_recommendations(bottlenecks, capacity_plan)
        }
    
    def _generate_recommendations(self, bottlenecks: Dict[str, Any], 
                                capacity_plan: CapacityPlan) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if 'latency' in bottlenecks:
            recommendations.append("考虑增加CPU核心数或优化代码性能")
        
        if 'cpu_usage' in bottlenecks:
            recommendations.append("增加CPU资源或优化CPU密集型操作")
        
        if 'memory_usage' in bottlenecks:
            recommendations.append("增加内存容量或优化内存使用")
        
        if 'network_usage' in bottlenecks:
            recommendations.append("升级网络带宽或优化网络通信")
        
        if capacity_plan.scaling_factor > 1.5:
            recommendations.append("建议进行容量扩展")
        
        return recommendations

class LoadForecaster:
    """负载预测器"""
    
    def __init__(self):
        self.historical_loads: List[Dict[str, float]] = []
        self.forecast_model = None
    
    def add_historical_load(self, load_data: Dict[str, float]):
        """添加历史负载数据"""
        self.historical_loads.append(load_data)
    
    def forecast_load(self, time_horizon: int = 24) -> List[Dict[str, float]]:
        """预测未来负载"""
        if len(self.historical_loads) < 10:
            return []
        
        # 简化的负载预测（实际应该使用时间序列模型）
        forecasts = []
        last_load = self.historical_loads[-1]
        
        for i in range(time_horizon):
            # 添加一些随机变化和趋势
            forecast = {}
            for key, value in last_load.items():
                if key in ['request_rate', 'concurrent_users']:
                    # 添加增长趋势和随机波动
                    trend = 1.0 + (i * 0.01)  # 1%每小时增长
                    noise = 1.0 + np.random.normal(0, 0.05)  # 5%随机波动
                    forecast[key] = value * trend * noise
                else:
                    forecast[key] = value
            
            forecasts.append(forecast)
        
        return forecasts

def main():
    """主函数"""
    print("🚀 性能预测模型系统启动")
    
    # 创建性能预测器
    predictor = PerformancePredictor()
    
    # 生成模拟性能数据
    print("📊 生成模拟性能数据...")
    
    for i in range(50):
        # 模拟不同负载下的性能数据
        request_rate = 50 + i * 10
        concurrent_users = 10 + i * 2
        cpu_usage = 0.3 + (i / 50) * 0.4
        memory_usage = 0.4 + (i / 50) * 0.3
        network_usage = 0.2 + (i / 50) * 0.4
        disk_usage = 0.1 + (i / 50) * 0.2
        
        # 模拟延迟和吞吐量（基于负载）
        latency = 100 + (request_rate / 10) + (concurrent_users * 2) + np.random.normal(0, 10)
        throughput = request_rate * (1 - cpu_usage * 0.5) + np.random.normal(0, 5)
        
        data = PerformanceData(
            timestamp=time.time() + i * 3600,  # 每小时一个数据点
            request_rate=request_rate,
            concurrent_users=concurrent_users,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            network_usage=network_usage,
            disk_usage=disk_usage,
            latency=latency,
            throughput=throughput,
            error_rate=0.01 + (cpu_usage * 0.02)
        )
        
        predictor.add_performance_data(data)
    
    # 训练模型
    print("🤖 训练性能预测模型...")
    
    latency_score = predictor.train_model(PredictionType.LATENCY, ModelType.RANDOM_FOREST)
    throughput_score = predictor.train_model(PredictionType.THROUGHPUT, ModelType.RANDOM_FOREST)
    
    print(f"延迟预测模型 R² = {latency_score:.4f}")
    print(f"吞吐量预测模型 R² = {throughput_score:.4f}")
    
    # 进行预测
    print("🔮 进行性能预测...")
    
    test_features = {
        'request_rate': 200,
        'concurrent_users': 100,
        'cpu_usage': 0.7,
        'memory_usage': 0.6,
        'network_usage': 0.5,
        'disk_usage': 0.3
    }
    
    latency_pred = predictor.predict_latency(
        test_features['request_rate'],
        test_features['concurrent_users'],
        test_features['cpu_usage'],
        test_features['memory_usage'],
        test_features['network_usage'],
        test_features['disk_usage']
    )
    
    throughput_pred = predictor.predict_throughput(
        test_features['request_rate'],
        test_features['concurrent_users'],
        test_features['cpu_usage'],
        test_features['memory_usage'],
        test_features['network_usage'],
        test_features['disk_usage']
    )
    
    print(f"预测延迟: {latency_pred.predicted_value:.2f}ms (置信度: {latency_pred.confidence:.2f})")
    print(f"预测吞吐量: {throughput_pred.predicted_value:.2f} req/s (置信度: {throughput_pred.confidence:.2f})")
    
    # 性能分析
    print("📈 进行性能分析...")
    
    analyzer = PerformanceAnalyzer(predictor)
    current_load = {
        'request_rate': 150,
        'concurrent_users': 75,
        'cpu_usage': 0.8,
        'memory_usage': 0.7,
        'network_usage': 0.6,
        'disk_usage': 0.4
    }
    
    report = analyzer.generate_performance_report("user-service", current_load)
    
    # 输出分析结果
    print(f"\n📋 性能分析报告:")
    print(f"服务名称: {report['service_name']}")
    print(f"瓶颈数量: {len(report['bottlenecks'])}")
    print(f"扩展因子: {report['capacity_plan']['scaling_factor']:.2f}")
    print(f"成本估算: ${report['capacity_plan']['cost_estimate']:.2f}")
    
    if report['bottlenecks']:
        print(f"\n🚨 发现瓶颈:")
        for resource, info in report['bottlenecks'].items():
            print(f"- {resource}: {info['current']:.2f} > {info['limit']:.2f} ({info['severity']})")
    
    if report['recommendations']:
        print(f"\n💡 建议:")
        for rec in report['recommendations']:
            print(f"- {rec}")
    
    # 负载预测
    print("\n🔮 负载预测...")
    
    forecaster = LoadForecaster()
    for data in predictor.performance_history[:10]:
        forecaster.add_historical_load({
            'request_rate': data.request_rate,
            'concurrent_users': data.concurrent_users,
            'cpu_usage': data.cpu_usage
        })
    
    forecasts = forecaster.forecast_load(24)  # 预测24小时
    
    print(f"负载预测完成，预测未来24小时的负载变化")
    print(f"当前负载: {forecasts[0]['request_rate']:.0f} req/s")
    print(f"24小时后预测负载: {forecasts[-1]['request_rate']:.0f} req/s")
    
    # 保存报告
    with open("performance_prediction_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # 生成可视化
    print("🎨 生成性能可视化...")
    
    # 绘制性能数据
    plt.figure(figsize=(15, 10))
    
    # 延迟vs请求率
    plt.subplot(2, 3, 1)
    request_rates = [data.request_rate for data in predictor.performance_history]
    latencies = [data.latency for data in predictor.performance_history]
    plt.scatter(request_rates, latencies, alpha=0.6)
    plt.xlabel('Request Rate (req/s)')
    plt.ylabel('Latency (ms)')
    plt.title('Latency vs Request Rate')
    
    # 吞吐量vs并发用户
    plt.subplot(2, 3, 2)
    concurrent_users = [data.concurrent_users for data in predictor.performance_history]
    throughputs = [data.throughput for data in predictor.performance_history]
    plt.scatter(concurrent_users, throughputs, alpha=0.6)
    plt.xlabel('Concurrent Users')
    plt.ylabel('Throughput (req/s)')
    plt.title('Throughput vs Concurrent Users')
    
    # CPU使用率趋势
    plt.subplot(2, 3, 3)
    timestamps = [data.timestamp for data in predictor.performance_history]
    cpu_usages = [data.cpu_usage for data in predictor.performance_history]
    plt.plot(timestamps, cpu_usages)
    plt.xlabel('Time')
    plt.ylabel('CPU Usage')
    plt.title('CPU Usage Trend')
    
    # 内存使用率趋势
    plt.subplot(2, 3, 4)
    memory_usages = [data.memory_usage for data in predictor.performance_history]
    plt.plot(timestamps, memory_usages)
    plt.xlabel('Time')
    plt.ylabel('Memory Usage')
    plt.title('Memory Usage Trend')
    
    # 负载预测
    plt.subplot(2, 3, 5)
    forecast_hours = list(range(len(forecasts)))
    forecast_rates = [f['request_rate'] for f in forecasts]
    plt.plot(forecast_hours, forecast_rates)
    plt.xlabel('Hours')
    plt.ylabel('Predicted Request Rate')
    plt.title('Load Forecast')
    
    # 性能指标分布
    plt.subplot(2, 3, 6)
    plt.hist(latencies, bins=20, alpha=0.7)
    plt.xlabel('Latency (ms)')
    plt.ylabel('Frequency')
    plt.title('Latency Distribution')
    
    plt.tight_layout()
    plt.savefig("performance_analysis.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ 性能预测模型完成！")
    print("📁 报告已保存到: performance_prediction_report.json")
    print("🖼️ 可视化已保存到: performance_analysis.png")

if __name__ == "__main__":
    main()
