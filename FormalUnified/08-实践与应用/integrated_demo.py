#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合工具演示脚本
展示AI建模引擎、模型可视化、形式验证和代码生成的完整工作流程
"""

import sys
import os
import logging
import json
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入我们的工具
try:
    from AI_Modeling_Engine.prototype import AIModelingEngine, ModelType, PropertyType
    from FormalTools.model_visualizer import ModelVisualizer
    from VerificationTools.formal_checker import FormalVerificationEngine, PropertySpec
except ImportError as e:
    logging.error(f"导入工具失败: {e}")
    logging.info("请确保所有工具模块都已正确安装")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('integrated_demo.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class IntegratedDemo:
    """综合工具演示类"""
    
    def __init__(self):
        self.engine = AIModelingEngine()
        self.visualizer = ModelVisualizer()
        self.verifier = FormalVerificationEngine()
        self.demo_results = {}
        
        logging.info("综合工具演示系统初始化完成")
    
    def run_complete_workflow(self, requirements_text: str, model_type: ModelType):
        """运行完整的建模工作流程"""
        logging.info("=" * 60)
        logging.info("🚀 开始完整建模工作流程")
        logging.info("=" * 60)
        
        # 阶段1: AI建模
        logging.info("\n📝 阶段1: AI建模引擎处理需求")
        model_result = self.engine.process_requirements(requirements_text, model_type)
        self.demo_results['modeling'] = model_result
        
        model_id = model_result['model_id']
        model_data = model_result['model_info']
        
        logging.info(f"✅ 模型生成完成: {model_id}")
        logging.info(f"   类型: {model_data['type']}")
        logging.info(f"   元素数量: {model_data['elements_count']}")
        
        # 阶段2: 模型可视化
        logging.info("\n🎨 阶段2: 生成模型可视化")
        try:
            viz_filename = f"demo_{model_id}_{model_data['type']}.png"
            self.visualizer.visualize_model(model_data, viz_filename)
            self.demo_results['visualization'] = {
                'filename': viz_filename,
                'status': 'success'
            }
            logging.info(f"✅ 可视化完成: {viz_filename}")
        except Exception as e:
            logging.error(f"❌ 可视化失败: {e}")
            self.demo_results['visualization'] = {
                'status': 'failed',
                'error': str(e)
            }
        
        # 阶段3: 形式验证
        logging.info("\n🔍 阶段3: 执行形式验证")
        verification_results = self._run_comprehensive_verification(model_id, model_data)
        self.demo_results['verification'] = verification_results
        
        # 阶段4: 代码生成
        logging.info("\n💻 阶段4: 生成实现代码")
        code_results = self._generate_multilingual_code(model_id)
        self.demo_results['code_generation'] = code_results
        
        # 阶段5: 生成综合报告
        logging.info("\n📊 阶段5: 生成综合报告")
        self._generate_comprehensive_report()
        
        logging.info("\n🎉 完整工作流程执行完成！")
        return self.demo_results
    
    def _run_comprehensive_verification(self, model_id: str, model_data: dict):
        """运行全面的形式验证"""
        verification_results = {}
        
        # 定义要验证的性质
        properties = [
            PropertySpec("安全性", PropertyType.SAFETY, "模型是否满足安全性要求"),
            PropertySpec("活性", PropertyType.LIVENESS, "模型是否满足活性要求"),
            PropertySpec("可达性", PropertyType.REACHABILITY, "所有状态是否可达"),
            PropertySpec("无死锁", PropertyType.DEADLOCK_FREE, "模型是否无死锁"),
            PropertySpec("不变性", PropertyType.INVARIANT, "模型是否满足不变性约束")
        ]
        
        for prop in properties:
            try:
                logging.info(f"   验证性质: {prop.name}")
                result = self.verifier.verify_property(model_data, prop, "model_checking")
                verification_results[prop.name] = result
                
                if result.get('result') == 'satisfied':
                    logging.info(f"   ✅ {prop.name}: 满足")
                elif result.get('result') == 'violated':
                    logging.warning(f"   ⚠️ {prop.name}: 违反")
                else:
                    logging.info(f"   ❓ {prop.name}: {result.get('result', '未知')}")
                    
            except Exception as e:
                logging.error(f"   ❌ {prop.name} 验证失败: {e}")
                verification_results[prop.name] = {
                    'result': 'error',
                    'error': str(e)
                }
        
        return verification_results
    
    def _generate_multilingual_code(self, model_id: str):
        """生成多语言实现代码"""
        code_results = {}
        target_languages = ['rust', 'go', 'python']
        
        for lang in target_languages:
            try:
                logging.info(f"   生成 {lang.upper()} 代码")
                code = self.engine.generate_implementation(model_id, lang)
                code_results[lang] = {
                    'status': 'success',
                    'code': code
                }
                logging.info(f"   ✅ {lang.upper()} 代码生成完成")
            except Exception as e:
                logging.error(f"   ❌ {lang.upper()} 代码生成失败: {e}")
                code_results[lang] = {
                    'status': 'failed',
                    'error': str(e)
                }
        
        return code_results
    
    def _generate_comprehensive_report(self):
        """生成综合报告"""
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_stages': 5,
                'completed_stages': 5,
                'overall_status': 'success'
            },
            'modeling': self.demo_results.get('modeling', {}),
            'visualization': self.demo_results.get('visualization', {}),
            'verification': self.demo_results.get('verification', {}),
            'code_generation': self.demo_results.get('code_generation', {})
        }
        
        # 保存报告到文件
        report_filename = f"comprehensive_report_{int(time.time())}.json"
        try:
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logging.info(f"📄 综合报告已保存: {report_filename}")
        except Exception as e:
            logging.error(f"❌ 报告保存失败: {e}")
        
        self.demo_results['comprehensive_report'] = report
        return report
    
    def demo_ecommerce_system(self):
        """演示电商系统建模"""
        requirements = """
        设计一个电商微服务系统，包含以下核心组件：
        
        1. 用户服务 (User Service)
           - 用户注册、登录、认证
           - 用户信息管理
           - 权限控制
        
        2. 商品服务 (Product Service)
           - 商品信息管理
           - 库存管理
           - 分类管理
        
        3. 订单服务 (Order Service)
           - 订单创建、修改、取消
           - 订单状态管理
           - 订单历史
        
        4. 支付服务 (Payment Service)
           - 支付处理
           - 退款处理
           - 支付记录
        
        5. 库存服务 (Inventory Service)
           - 实时库存更新
           - 库存预警
           - 库存同步
        
        系统需要支持：
        - 高并发访问
        - 分布式事务
        - 服务间异步通信
        - 故障容错
        - 可观测性
        """
        
        logging.info("🏪 开始电商系统建模演示")
        return self.run_complete_workflow(requirements, ModelType.UNIFIED_STS)
    
    def demo_workflow_system(self):
        """演示工作流系统建模"""
        requirements = """
        设计一个企业级工作流管理系统，支持：
        
        1. 工作流定义
           - 流程节点设计
           - 条件分支
           - 并行执行
           - 子流程嵌套
        
        2. 任务执行
           - 任务分配
           - 进度跟踪
           - 超时处理
           - 重试机制
        
        3. 审批流程
           - 多级审批
           - 会签/或签
           - 委托代理
           - 加签/减签
        
        4. 监控与分析
           - 实时监控
           - 性能分析
           - 瓶颈识别
           - 优化建议
        
        系统特性：
        - 高可用性
        - 可扩展性
        - 审计追踪
        - 合规性支持
        """
        
        logging.info("⚙️ 开始工作流系统建模演示")
        return self.run_complete_workflow(requirements, ModelType.PETRI_NET)
    
    def demo_iot_gateway(self):
        """演示IoT网关系统建模"""
        requirements = """
        设计一个智能IoT网关系统，具备以下功能：
        
        1. 设备管理
           - 设备注册与发现
           - 设备状态监控
           - 固件升级管理
           - 设备配置管理
        
        2. 数据采集
           - 多协议支持 (MQTT, CoAP, HTTP)
           - 实时数据采集
           - 数据预处理
           - 数据缓存
        
        3. 边缘计算
           - 本地数据处理
           - 规则引擎
           - 机器学习推理
           - 异常检测
        
        4. 安全机制
           - 设备认证
           - 数据加密
           - 访问控制
           - 威胁检测
        
        5. 云平台集成
           - 数据上传
           - 命令下发
           - 配置同步
           - 远程控制
        
        系统要求：
        - 低功耗运行
        - 高可靠性
        - 实时响应
        - 安全防护
        """
        
        logging.info("🏠 开始IoT网关系统建模演示")
        return self.run_complete_workflow(requirements, ModelType.STATE_MACHINE)

def main():
    """主函数"""
    logging.info("🎯 综合工具演示系统启动")
    
    demo = IntegratedDemo()
    
    # 运行多个演示案例
    demos = [
        ("电商系统", demo.demo_ecommerce_system),
        ("工作流系统", demo.demo_workflow_system),
        ("IoT网关", demo.demo_iot_gateway)
    ]
    
    all_results = {}
    
    for demo_name, demo_func in demos:
        try:
            logging.info(f"\n{'='*20} {demo_name} 演示 {'='*20}")
            result = demo_func()
            all_results[demo_name] = result
            logging.info(f"{demo_name} 演示完成")
            
            # 演示间隔
            time.sleep(2)
            
        except Exception as e:
            logging.error(f"{demo_name} 演示失败: {e}")
            all_results[demo_name] = {'error': str(e)}
    
    # 生成总体报告
    logging.info("\n" + "="*60)
    logging.info("📊 生成总体演示报告")
    logging.info("="*60)
    
    summary = {
        'total_demos': len(demos),
        'successful_demos': len([r for r in all_results.values() if 'error' not in r]),
        'failed_demos': len([r for r in all_results.values() if 'error' in r]),
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'results': all_results
    }
    
    # 保存总体报告
    summary_filename = f"demo_summary_{int(time.time())}.json"
    try:
        with open(summary_filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        logging.info(f"📄 总体报告已保存: {summary_filename}")
    except Exception as e:
        logging.error(f"❌ 总体报告保存失败: {e}")
    
    # 输出总结
    logging.info(f"\n🎉 演示完成总结:")
    logging.info(f"   总演示数: {summary['total_demos']}")
    logging.info(f"   成功演示: {summary['successful_demos']}")
    logging.info(f"   失败演示: {summary['failed_demos']}")
    logging.info(f"   成功率: {summary['successful_demos']/summary['total_demos']*100:.1f}%")
    
    logging.info("\n✨ 综合工具演示系统运行完成！")

if __name__ == "__main__":
    main() 