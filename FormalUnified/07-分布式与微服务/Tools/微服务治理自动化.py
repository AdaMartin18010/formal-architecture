#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微服务治理自动化
Microservice Governance Automation

本工具提供微服务架构的自动化治理功能，包括：
1. 服务发现与注册
2. 负载均衡
3. 熔断器模式
4. 配置管理
5. 监控与告警
6. 服务网格管理
"""

import json
import time
import logging
import threading
from typing import Dict, List, Set, Tuple, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import statistics

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    """服务状态枚举"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    OFFLINE = "offline"

class LoadBalancerType(Enum):
    """负载均衡器类型"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"
    IP_HASH = "ip_hash"

class CircuitBreakerState(Enum):
    """熔断器状态"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class ServiceInstance:
    """服务实例"""
    id: str
    service_name: str
    host: str
    port: int
    status: ServiceStatus
    health_check_url: str
    metadata: Dict[str, Any]
    last_heartbeat: float
    load: float = 0.0
    response_time: float = 0.0
    error_rate: float = 0.0

@dataclass
class ServiceConfig:
    """服务配置"""
    service_name: str
    version: str
    config_data: Dict[str, Any]
    environment: str
    last_updated: float

@dataclass
class CircuitBreaker:
    """熔断器"""
    service_name: str
    state: CircuitBreakerState
    failure_threshold: int
    success_threshold: int
    timeout: float
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: float = 0.0

class ServiceRegistry:
    """服务注册中心"""
    
    def __init__(self):
        self.services: Dict[str, List[ServiceInstance]] = {}
        self.health_check_interval = 30  # 秒
        self.health_check_thread = None
        self.running = False
    
    def register_service(self, instance: ServiceInstance):
        """注册服务"""
        if instance.service_name not in self.services:
            self.services[instance.service_name] = []
        
        # 检查是否已存在
        existing = next((s for s in self.services[instance.service_name] 
                        if s.id == instance.id), None)
        if existing:
            # 更新现有实例
            existing.status = instance.status
            existing.metadata = instance.metadata
            existing.last_heartbeat = time.time()
        else:
            # 添加新实例
            self.services[instance.service_name].append(instance)
        
        logger.info(f"服务注册: {instance.service_name} - {instance.id}")
    
    def deregister_service(self, service_name: str, instance_id: str):
        """注销服务"""
        if service_name in self.services:
            self.services[service_name] = [
                s for s in self.services[service_name] if s.id != instance_id
            ]
            logger.info(f"服务注销: {service_name} - {instance_id}")
    
    def get_service_instances(self, service_name: str) -> List[ServiceInstance]:
        """获取服务实例"""
        return self.services.get(service_name, [])
    
    def get_healthy_instances(self, service_name: str) -> List[ServiceInstance]:
        """获取健康实例"""
        instances = self.get_service_instances(service_name)
        return [i for i in instances if i.status == ServiceStatus.HEALTHY]
    
    def start_health_check(self):
        """启动健康检查"""
        self.running = True
        self.health_check_thread = threading.Thread(target=self._health_check_loop)
        self.health_check_thread.daemon = True
        self.health_check_thread.start()
    
    def stop_health_check(self):
        """停止健康检查"""
        self.running = False
        if self.health_check_thread:
            self.health_check_thread.join()
    
    def _health_check_loop(self):
        """健康检查循环"""
        while self.running:
            for service_name, instances in self.services.items():
                for instance in instances:
                    self._check_instance_health(instance)
            time.sleep(self.health_check_interval)
    
    def _check_instance_health(self, instance: ServiceInstance):
        """检查实例健康状态"""
        try:
            response = requests.get(instance.health_check_url, timeout=5)
            if response.status_code == 200:
                instance.status = ServiceStatus.HEALTHY
                instance.last_heartbeat = time.time()
            else:
                instance.status = ServiceStatus.UNHEALTHY
        except Exception as e:
            instance.status = ServiceStatus.UNHEALTHY
            logger.warning(f"健康检查失败: {instance.id} - {e}")

class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self, lb_type: LoadBalancerType = LoadBalancerType.ROUND_ROBIN):
        self.lb_type = lb_type
        self.current_index = 0
        self.connection_counts = {}
    
    def select_instance(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        """选择实例"""
        if not instances:
            return None
        
        healthy_instances = [i for i in instances if i.status == ServiceStatus.HEALTHY]
        if not healthy_instances:
            return None
        
        if self.lb_type == LoadBalancerType.ROUND_ROBIN:
            return self._round_robin(healthy_instances)
        elif self.lb_type == LoadBalancerType.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin(healthy_instances)
        elif self.lb_type == LoadBalancerType.LEAST_CONNECTIONS:
            return self._least_connections(healthy_instances)
        elif self.lb_type == LoadBalancerType.RANDOM:
            return self._random(healthy_instances)
        elif self.lb_type == LoadBalancerType.IP_HASH:
            return self._ip_hash(healthy_instances)
        else:
            return healthy_instances[0]
    
    def _round_robin(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """轮询"""
        instance = instances[self.current_index % len(instances)]
        self.current_index += 1
        return instance
    
    def _weighted_round_robin(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """加权轮询"""
        # 简化实现，实际应该根据权重分配
        return self._round_robin(instances)
    
    def _least_connections(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """最少连接"""
        return min(instances, key=lambda x: self.connection_counts.get(x.id, 0))
    
    def _random(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """随机"""
        return random.choice(instances)
    
    def _ip_hash(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """IP哈希"""
        # 简化实现，实际应该根据客户端IP计算哈希
        return instances[hash(str(time.time())) % len(instances)]

class CircuitBreakerManager:
    """熔断器管理器"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
    
    def get_circuit_breaker(self, service_name: str, 
                           failure_threshold: int = 5,
                           success_threshold: int = 2,
                           timeout: float = 60.0) -> CircuitBreaker:
        """获取熔断器"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker(
                service_name=service_name,
                state=CircuitBreakerState.CLOSED,
                failure_threshold=failure_threshold,
                success_threshold=success_threshold,
                timeout=timeout
            )
        return self.circuit_breakers[service_name]
    
    def record_success(self, service_name: str):
        """记录成功"""
        cb = self.get_circuit_breaker(service_name)
        if cb.state == CircuitBreakerState.HALF_OPEN:
            cb.success_count += 1
            if cb.success_count >= cb.success_threshold:
                cb.state = CircuitBreakerState.CLOSED
                cb.failure_count = 0
                cb.success_count = 0
                logger.info(f"熔断器关闭: {service_name}")
    
    def record_failure(self, service_name: str):
        """记录失败"""
        cb = self.get_circuit_breaker(service_name)
        cb.failure_count += 1
        cb.last_failure_time = time.time()
        
        if cb.state == CircuitBreakerState.CLOSED and cb.failure_count >= cb.failure_threshold:
            cb.state = CircuitBreakerState.OPEN
            logger.warning(f"熔断器打开: {service_name}")
    
    def can_execute(self, service_name: str) -> bool:
        """检查是否可以执行"""
        cb = self.get_circuit_breaker(service_name)
        
        if cb.state == CircuitBreakerState.CLOSED:
            return True
        elif cb.state == CircuitBreakerState.OPEN:
            # 检查是否超时
            if time.time() - cb.last_failure_time >= cb.timeout:
                cb.state = CircuitBreakerState.HALF_OPEN
                logger.info(f"熔断器半开: {service_name}")
                return True
            return False
        else:  # HALF_OPEN
            return True

class ConfigurationManager:
    """配置管理器"""
    
    def __init__(self):
        self.configs: Dict[str, ServiceConfig] = {}
        self.config_watchers: Dict[str, List[Callable]] = {}
    
    def set_config(self, service_name: str, config_data: Dict[str, Any], 
                   version: str = "1.0", environment: str = "default"):
        """设置配置"""
        config = ServiceConfig(
            service_name=service_name,
            version=version,
            config_data=config_data,
            environment=environment,
            last_updated=time.time()
        )
        self.configs[service_name] = config
        
        # 通知观察者
        if service_name in self.config_watchers:
            for watcher in self.config_watchers[service_name]:
                try:
                    watcher(config)
                except Exception as e:
                    logger.error(f"配置观察者通知失败: {e}")
        
        logger.info(f"配置更新: {service_name} - {version}")
    
    def get_config(self, service_name: str) -> Optional[ServiceConfig]:
        """获取配置"""
        return self.configs.get(service_name)
    
    def watch_config(self, service_name: str, callback: Callable):
        """监听配置变化"""
        if service_name not in self.config_watchers:
            self.config_watchers[service_name] = []
        self.config_watchers[service_name].append(callback)

class MonitoringSystem:
    """监控系统"""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
    
    def record_metric(self, service_name: str, metric_name: str, value: float):
        """记录指标"""
        key = f"{service_name}.{metric_name}"
        if key not in self.metrics:
            self.metrics[key] = []
        
        self.metrics[key].append(value)
        
        # 保持最近1000个数据点
        if len(self.metrics[key]) > 1000:
            self.metrics[key] = self.metrics[key][-1000:]
        
        # 检查告警规则
        self._check_alerts(service_name, metric_name, value)
    
    def get_metric_stats(self, service_name: str, metric_name: str) -> Dict[str, float]:
        """获取指标统计"""
        key = f"{service_name}.{metric_name}"
        values = self.metrics.get(key, [])
        
        if not values:
            return {}
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "std": statistics.stdev(values) if len(values) > 1 else 0.0
        }
    
    def add_alert_rule(self, rule_name: str, service_name: str, metric_name: str, 
                       threshold: float, operator: str = ">"):
        """添加告警规则"""
        self.alert_rules[rule_name] = {
            "service_name": service_name,
            "metric_name": metric_name,
            "threshold": threshold,
            "operator": operator
        }
    
    def _check_alerts(self, service_name: str, metric_name: str, value: float):
        """检查告警"""
        for rule_name, rule in self.alert_rules.items():
            if (rule["service_name"] == service_name and 
                rule["metric_name"] == metric_name):
                
                triggered = False
                if rule["operator"] == ">":
                    triggered = value > rule["threshold"]
                elif rule["operator"] == "<":
                    triggered = value < rule["threshold"]
                elif rule["operator"] == ">=":
                    triggered = value >= rule["threshold"]
                elif rule["operator"] == "<=":
                    triggered = value <= rule["threshold"]
                
                if triggered:
                    alert = {
                        "rule_name": rule_name,
                        "service_name": service_name,
                        "metric_name": metric_name,
                        "value": value,
                        "threshold": rule["threshold"],
                        "operator": rule["operator"],
                        "timestamp": time.time()
                    }
                    self.alerts.append(alert)
                    logger.warning(f"告警触发: {rule_name} - {value} {rule['operator']} {rule['threshold']}")

class MicroserviceGovernance:
    """微服务治理主类"""
    
    def __init__(self):
        self.registry = ServiceRegistry()
        self.load_balancer = LoadBalancer()
        self.circuit_breaker_manager = CircuitBreakerManager()
        self.config_manager = ConfigurationManager()
        self.monitoring = MonitoringSystem()
        
        # 启动健康检查
        self.registry.start_health_check()
    
    def register_service_instance(self, instance: ServiceInstance):
        """注册服务实例"""
        self.registry.register_service(instance)
    
    def discover_service(self, service_name: str) -> Optional[ServiceInstance]:
        """服务发现"""
        instances = self.registry.get_healthy_instances(service_name)
        return self.load_balancer.select_instance(instances)
    
    def call_service(self, service_name: str, method: str = "GET", 
                    path: str = "/", data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """调用服务"""
        # 检查熔断器
        if not self.circuit_breaker_manager.can_execute(service_name):
            logger.warning(f"服务熔断: {service_name}")
            return None
        
        # 服务发现
        instance = self.discover_service(service_name)
        if not instance:
            logger.error(f"服务不可用: {service_name}")
            return None
        
        # 调用服务
        start_time = time.time()
        try:
            url = f"http://{instance.host}:{instance.port}{path}"
            response = requests.request(method, url, json=data, timeout=10)
            
            # 记录成功
            self.circuit_breaker_manager.record_success(service_name)
            
            # 记录指标
            response_time = time.time() - start_time
            self.monitoring.record_metric(service_name, "response_time", response_time)
            self.monitoring.record_metric(service_name, "request_count", 1)
            
            return response.json() if response.status_code == 200 else None
            
        except Exception as e:
            # 记录失败
            self.circuit_breaker_manager.record_failure(service_name)
            
            # 记录指标
            self.monitoring.record_metric(service_name, "error_count", 1)
            self.monitoring.record_metric(service_name, "response_time", time.time() - start_time)
            
            logger.error(f"服务调用失败: {service_name} - {e}")
            return None
    
    def set_service_config(self, service_name: str, config_data: Dict[str, Any]):
        """设置服务配置"""
        self.config_manager.set_config(service_name, config_data)
    
    def get_service_config(self, service_name: str) -> Optional[ServiceConfig]:
        """获取服务配置"""
        return self.config_manager.get_config(service_name)
    
    def add_monitoring_rule(self, rule_name: str, service_name: str, 
                           metric_name: str, threshold: float, operator: str = ">"):
        """添加监控规则"""
        self.monitoring.add_alert_rule(rule_name, service_name, metric_name, threshold, operator)
    
    def get_service_metrics(self, service_name: str) -> Dict[str, Dict[str, float]]:
        """获取服务指标"""
        metrics = {}
        for key in self.monitoring.metrics:
            if key.startswith(f"{service_name}."):
                metric_name = key.split(".", 1)[1]
                metrics[metric_name] = self.monitoring.get_metric_stats(service_name, metric_name)
        return metrics
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """获取告警"""
        return self.monitoring.alerts
    
    def generate_report(self) -> Dict[str, Any]:
        """生成治理报告"""
        return {
            "services": {
                service_name: {
                    "instance_count": len(instances),
                    "healthy_count": len([i for i in instances if i.status == ServiceStatus.HEALTHY]),
                    "unhealthy_count": len([i for i in instances if i.status == ServiceStatus.UNHEALTHY])
                }
                for service_name, instances in self.registry.services.items()
            },
            "circuit_breakers": {
                service_name: {
                    "state": cb.state.value,
                    "failure_count": cb.failure_count,
                    "success_count": cb.success_count
                }
                for service_name, cb in self.circuit_breaker_manager.circuit_breakers.items()
            },
            "configs": {
                service_name: {
                    "version": config.version,
                    "environment": config.environment,
                    "last_updated": config.last_updated
                }
                for service_name, config in self.config_manager.configs.items()
            },
            "alerts": len(self.monitoring.alerts),
            "metrics_count": len(self.monitoring.metrics)
        }
    
    def shutdown(self):
        """关闭治理系统"""
        self.registry.stop_health_check()

def main():
    """主函数"""
    print("🚀 微服务治理自动化系统启动")
    
    # 创建治理系统
    governance = MicroserviceGovernance()
    
    # 注册服务实例
    print("📡 注册服务实例...")
    
    services = [
        ServiceInstance(
            id="user-service-1",
            service_name="user-service",
            host="localhost",
            port=8081,
            status=ServiceStatus.HEALTHY,
            health_check_url="http://localhost:8081/health",
            metadata={"version": "1.0", "region": "us-east-1"},
            last_heartbeat=time.time()
        ),
        ServiceInstance(
            id="user-service-2",
            service_name="user-service",
            host="localhost",
            port=8082,
            status=ServiceStatus.HEALTHY,
            health_check_url="http://localhost:8082/health",
            metadata={"version": "1.0", "region": "us-east-1"},
            last_heartbeat=time.time()
        ),
        ServiceInstance(
            id="order-service-1",
            service_name="order-service",
            host="localhost",
            port=8083,
            status=ServiceStatus.HEALTHY,
            health_check_url="http://localhost:8083/health",
            metadata={"version": "1.0", "region": "us-east-1"},
            last_heartbeat=time.time()
        )
    ]
    
    for service in services:
        governance.register_service_instance(service)
    
    # 设置配置
    print("⚙️ 设置服务配置...")
    governance.set_service_config("user-service", {
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "user_db"
        },
        "cache": {
            "host": "localhost",
            "port": 6379
        }
    })
    
    governance.set_service_config("order-service", {
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "order_db"
        },
        "payment": {
            "gateway": "stripe",
            "timeout": 30
        }
    })
    
    # 添加监控规则
    print("📊 添加监控规则...")
    governance.add_monitoring_rule("high_response_time", "user-service", "response_time", 1.0, ">")
    governance.add_monitoring_rule("high_error_rate", "user-service", "error_count", 5, ">")
    
    # 模拟服务调用
    print("🔄 模拟服务调用...")
    for i in range(10):
        result = governance.call_service("user-service", "GET", "/users/1")
        if result:
            print(f"调用成功: {result}")
        else:
            print("调用失败")
        
        time.sleep(0.5)
    
    # 生成报告
    print("📋 生成治理报告...")
    report = governance.generate_report()
    
    # 输出结果
    print(f"\n📊 治理报告:")
    print(f"服务数量: {len(report['services'])}")
    print(f"熔断器数量: {len(report['circuit_breakers'])}")
    print(f"配置数量: {len(report['configs'])}")
    print(f"告警数量: {report['alerts']}")
    print(f"指标数量: {report['metrics_count']}")
    
    # 获取服务指标
    print(f"\n📈 服务指标:")
    for service_name in report['services']:
        metrics = governance.get_service_metrics(service_name)
        print(f"{service_name}: {metrics}")
    
    # 获取告警
    alerts = governance.get_alerts()
    if alerts:
        print(f"\n🚨 告警信息:")
        for alert in alerts[-5:]:  # 显示最近5个告警
            print(f"- {alert['rule_name']}: {alert['value']} {alert['operator']} {alert['threshold']}")
    
    # 保存报告
    with open("governance_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # 关闭系统
    governance.shutdown()
    
    print("✅ 微服务治理自动化完成！")
    print("📁 报告已保存到: governance_report.json")

if __name__ == "__main__":
    main()
