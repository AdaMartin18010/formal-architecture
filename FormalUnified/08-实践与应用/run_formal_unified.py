#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FormalUnified 统一运行脚本
FormalUnified Unified Runner

这个脚本整合了FormalUnified项目的所有核心工具，
提供统一的入口点来运行各种分析和验证功能。
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
import json
import yaml

# 导入项目模块
try:
    from AI_Modeling_Engine.enhanced_prototype import EnhancedAIModelingEngine
    from TheoryToPractice.mapping_tool import MappingEngine
    from CrossTheoryVerificationEngine import CrossTheoryVerificationEngine
    from IntelligentAnalysisPlatform import IntelligentAnalysisPlatform
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保所有依赖模块都已正确安装")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('formal_unified.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class FormalUnifiedRunner:
    """FormalUnified统一运行器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.ai_engine = None
        self.mapping_engine = None
        self.verification_engine = None
        self.analysis_platform = None
        
    def _load_config(self) -> dict:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"配置文件 {self.config_path} 未找到，使用默认配置")
            return self._get_default_config()
    
    def _get_default_config(self) -> dict:
        """获取默认配置"""
        return {
            "project": {
                "name": "形式化架构理论统一项目",
                "version": "1.0.0"
            },
            "output": {
                "base_directory": "output",
                "formats": ["json", "yaml", "markdown"]
            },
            "logging": {
                "level": "INFO",
                "file": "formal_unified.log"
            }
        }
    
    def initialize_engines(self):
        """初始化所有引擎"""
        logger.info("初始化FormalUnified引擎...")
        
        try:
            # 初始化AI建模引擎
            self.ai_engine = EnhancedAIModelingEngine(self.config_path)
            logger.info("✓ AI建模引擎初始化成功")
            
            # 初始化理论到实践映射引擎
            self.mapping_engine = MappingEngine()
            logger.info("✓ 理论到实践映射引擎初始化成功")
            
            # 初始化跨理论验证引擎
            self.verification_engine = CrossTheoryVerificationEngine(self.config_path)
            logger.info("✓ 跨理论验证引擎初始化成功")
            
            # 初始化智能化分析平台
            self.analysis_platform = IntelligentAnalysisPlatform(self.config_path)
            logger.info("✓ 智能化分析平台初始化成功")
            
            return True
            
        except Exception as e:
            logger.error(f"初始化引擎失败: {e}")
            return False
    
    def run_full_analysis(self, output_dir: str = "output"):
        """运行完整分析"""
        logger.info("开始运行FormalUnified完整分析...")
        
        start_time = datetime.now()
        results = {
            "analysis_time": start_time.isoformat(),
            "status": "running",
            "results": {}
        }
        
        try:
            # 1. 加载理论体系
            logger.info("步骤1: 加载理论体系...")
            if not self.verification_engine.load_theory_systems():
                raise Exception("加载理论体系失败")
            
            if not self.analysis_platform.load_theory_systems():
                raise Exception("加载理论体系到分析平台失败")
            
            results["results"]["theory_loading"] = {
                "status": "success",
                "loaded_systems": len(self.verification_engine.theory_systems)
            }
            
            # 2. 运行跨理论验证
            logger.info("步骤2: 运行跨理论验证...")
            verification_results = self.verification_engine.verify_theory_consistency()
            cross_mappings = self.verification_engine.analyze_cross_theory_mappings()
            
            results["results"]["verification"] = {
                "status": "success",
                "verification_results": len(verification_results),
                "cross_mappings": len(cross_mappings)
            }
            
            # 3. 运行智能化分析
            logger.info("步骤3: 运行智能化分析...")
            quality_profiles = self.analysis_platform.generate_quality_profiles()
            insights = self.analysis_platform.generate_intelligent_insights()
            
            results["results"]["analysis"] = {
                "status": "success",
                "quality_profiles": len(quality_profiles),
                "insights": len(insights)
            }
            
            # 4. 生成AI建模示例
            logger.info("步骤4: 生成AI建模示例...")
            ai_examples = self._generate_ai_examples()
            
            results["results"]["ai_modeling"] = {
                "status": "success",
                "examples_generated": len(ai_examples)
            }
            
            # 5. 导出所有结果
            logger.info("步骤5: 导出分析结果...")
            self._export_all_results(output_dir, results, verification_results, 
                                   cross_mappings, quality_profiles, insights)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            results["status"] = "completed"
            results["duration_seconds"] = duration
            
            logger.info(f"FormalUnified完整分析完成，耗时 {duration:.2f} 秒")
            return results
            
        except Exception as e:
            logger.error(f"运行完整分析失败: {e}")
            results["status"] = "failed"
            results["error"] = str(e)
            return results
    
    def _generate_ai_examples(self) -> list:
        """生成AI建模示例"""
        examples = []
        
        try:
            # 示例1: 状态机模式
            state_machine_requirements = {
                "pattern_type": "state_machine",
                "components": ["状态管理器", "状态转换器", "事件处理器"],
                "constraints": ["状态一致性", "转换原子性"],
                "target_language": "rust"
            }
            
            pattern = self.ai_engine.generate_architecture_pattern(state_machine_requirements)
            implementation = self.ai_engine.generate_implementation(pattern, "rust")
            verification = self.ai_engine.verify_implementation(pattern, implementation)
            
            examples.append({
                "name": "状态机模式",
                "pattern": pattern.name,
                "implementation": implementation[:500] + "...",
                "verification_score": verification["score"]
            })
            
            # 示例2: 微服务架构
            microservice_requirements = {
                "pattern_type": "microservice",
                "components": ["服务注册中心", "API网关", "服务实例"],
                "constraints": ["服务发现", "负载均衡"],
                "target_language": "go"
            }
            
            pattern = self.ai_engine.generate_architecture_pattern(microservice_requirements)
            implementation = self.ai_engine.generate_implementation(pattern, "go")
            verification = self.ai_engine.verify_implementation(pattern, implementation)
            
            examples.append({
                "name": "微服务架构",
                "pattern": pattern.name,
                "implementation": implementation[:500] + "...",
                "verification_score": verification["score"]
            })
            
        except Exception as e:
            logger.warning(f"生成AI示例失败: {e}")
        
        return examples
    
    def _export_all_results(self, output_dir: str, results: dict, verification_results: list,
                           cross_mappings: list, quality_profiles: dict, insights: list):
        """导出所有结果"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 导出主结果
        with open(output_path / "full_analysis_results.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 导出验证结果
        self.verification_engine.export_results(str(output_path / "verification"))
        
        # 导出分析结果
        self.analysis_platform.export_analysis_report(str(output_path / "analysis"))
        
        # 生成汇总报告
        self._generate_summary_report(output_path, results, verification_results, 
                                    cross_mappings, quality_profiles, insights)
    
    def _generate_summary_report(self, output_path: Path, results: dict, verification_results: list,
                               cross_mappings: list, quality_profiles: dict, insights: list):
        """生成汇总报告"""
        report = f"""# FormalUnified 分析汇总报告

## 分析概览

- **分析时间**: {results['analysis_time']}
- **分析状态**: {results['status']}
- **耗时**: {results.get('duration_seconds', 0):.2f} 秒

## 理论体系状态

### 验证结果统计
- 验证结果总数: {len(verification_results)}
- 通过验证: {sum(1 for r in verification_results if r.status == 'PASS')}
- 警告: {sum(1 for r in verification_results if r.status == 'WARN')}
- 失败: {sum(1 for r in verification_results if r.status == 'FAIL')}

### 跨理论映射统计
- 映射关系总数: {len(cross_mappings)}
- 强继承关系: {sum(1 for m in cross_mappings if m.mapping_type == 'strong_inheritance')}
- 组合关系: {sum(1 for m in cross_mappings if m.mapping_type == 'composition')}
- 依赖关系: {sum(1 for m in cross_mappings if m.mapping_type == 'dependency')}

## 质量分析

### 理论体系质量排名
"""
        
        # 添加质量排名
        sorted_profiles = sorted(quality_profiles.items(), 
                               key=lambda x: x[1].overall_score, reverse=True)
        
        for i, (theory_name, profile) in enumerate(sorted_profiles, 1):
            report += f"{i}. **{theory_name}**: {profile.overall_score:.2f}\n"
        
        report += f"""
## 智能洞察

### 主要洞察 (前5个)
"""
        
        # 添加主要洞察
        sorted_insights = sorted(insights, key=lambda x: x.priority)[:5]
        for insight in sorted_insights:
            report += f"- **{insight.title}** (优先级: {insight.priority})\n"
            report += f"  - {insight.description}\n"
            report += f"  - 置信度: {insight.confidence:.2f}\n"
        
        report += f"""
## 建议和下一步行动

### 立即行动项
1. 关注验证失败的理论体系
2. 优先处理高优先级洞察
3. 加强跨理论体系关联

### 长期规划
1. 持续完善理论体系
2. 扩展工具功能
3. 建立实践验证框架

---
*报告生成时间: {datetime.now().isoformat()}*
"""
        
        with open(output_path / "summary_report.md", 'w', encoding='utf-8') as f:
            f.write(report)
    
    def run_specific_analysis(self, analysis_type: str, **kwargs):
        """运行特定分析"""
        logger.info(f"运行特定分析: {analysis_type}")
        
        if analysis_type == "verification":
            return self._run_verification_analysis(**kwargs)
        elif analysis_type == "quality":
            return self._run_quality_analysis(**kwargs)
        elif analysis_type == "ai_modeling":
            return self._run_ai_modeling_analysis(**kwargs)
        elif analysis_type == "mapping":
            return self._run_mapping_analysis(**kwargs)
        else:
            raise ValueError(f"不支持的分析类型: {analysis_type}")
    
    def _run_verification_analysis(self, **kwargs):
        """运行验证分析"""
        if not self.verification_engine.load_theory_systems():
            return {"status": "failed", "error": "加载理论体系失败"}
        
        verification_results = self.verification_engine.verify_theory_consistency()
        cross_mappings = self.verification_engine.analyze_cross_theory_mappings()
        
        return {
            "status": "success",
            "verification_results": len(verification_results),
            "cross_mappings": len(cross_mappings),
            "details": {
                "verification_results": [vars(r) for r in verification_results],
                "cross_mappings": [vars(m) for m in cross_mappings]
            }
        }
    
    def _run_quality_analysis(self, **kwargs):
        """运行质量分析"""
        if not self.analysis_platform.load_theory_systems():
            return {"status": "failed", "error": "加载理论体系失败"}
        
        quality_profiles = self.analysis_platform.generate_quality_profiles()
        insights = self.analysis_platform.generate_intelligent_insights()
        
        return {
            "status": "success",
            "quality_profiles": len(quality_profiles),
            "insights": len(insights),
            "details": {
                "quality_profiles": {name: vars(profile) for name, profile in quality_profiles.items()},
                "insights": [vars(insight) for insight in insights]
            }
        }
    
    def _run_ai_modeling_analysis(self, **kwargs):
        """运行AI建模分析"""
        requirements = kwargs.get('requirements', {})
        target_language = kwargs.get('target_language', 'rust')
        
        try:
            pattern = self.ai_engine.generate_architecture_pattern(requirements)
            implementation = self.ai_engine.generate_implementation(pattern, target_language)
            verification = self.ai_engine.verify_implementation(pattern, implementation)
            
            return {
                "status": "success",
                "pattern": pattern.name,
                "verification_score": verification["score"],
                "implementation": implementation[:1000] + "..." if len(implementation) > 1000 else implementation
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _run_mapping_analysis(self, **kwargs):
        """运行映射分析"""
        theory_content = kwargs.get('theory_content', '')
        target_language = kwargs.get('target_language', 'rust')
        
        try:
            implementations = self.mapping_engine.map_theory_to_practice(theory_content, target_language)
            
            return {
                "status": "success",
                "implementations": len(implementations),
                "details": [impl.to_dict() for impl in implementations]
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='FormalUnified 统一运行器')
    parser.add_argument('--config', default='config.yaml', help='配置文件路径')
    parser.add_argument('--output', default='output', help='输出目录')
    parser.add_argument('--analysis-type', choices=['full', 'verification', 'quality', 'ai_modeling', 'mapping'],
                       default='full', help='分析类型')
    parser.add_argument('--requirements', type=str, help='AI建模需求 (JSON格式)')
    parser.add_argument('--theory-content', type=str, help='理论内容 (用于映射分析)')
    parser.add_argument('--target-language', default='rust', 
                       choices=['rust', 'go', 'python', 'typescript'], help='目标编程语言')
    
    args = parser.parse_args()
    
    # 创建运行器
    runner = FormalUnifiedRunner(args.config)
    
    # 初始化引擎
    if not runner.initialize_engines():
        logger.error("初始化引擎失败")
        sys.exit(1)
    
    try:
        if args.analysis_type == 'full':
            # 运行完整分析
            results = runner.run_full_analysis(args.output)
        else:
            # 运行特定分析
            kwargs = {}
            if args.requirements:
                import json
                kwargs['requirements'] = json.loads(args.requirements)
            if args.theory_content:
                kwargs['theory_content'] = args.theory_content
            kwargs['target_language'] = args.target_language
            
            results = runner.run_specific_analysis(args.analysis_type, **kwargs)
        
        # 输出结果
        print(f"\n=== FormalUnified 分析结果 ===")
        print(f"状态: {results['status']}")
        
        if results['status'] == 'success':
            if 'duration_seconds' in results:
                print(f"耗时: {results['duration_seconds']:.2f} 秒")
            
            # 输出详细信息
            for key, value in results.get('results', {}).items():
                if isinstance(value, dict) and 'status' in value:
                    print(f"{key}: {value['status']}")
                    if 'loaded_systems' in value:
                        print(f"  加载理论体系: {value['loaded_systems']}")
                    if 'verification_results' in value:
                        print(f"  验证结果: {value['verification_results']}")
                    if 'cross_mappings' in value:
                        print(f"  跨理论映射: {value['cross_mappings']}")
                    if 'quality_profiles' in value:
                        print(f"  质量画像: {value['quality_profiles']}")
                    if 'insights' in value:
                        print(f"  智能洞察: {value['insights']}")
        else:
            print(f"错误: {results.get('error', '未知错误')}")
        
        print(f"\n结果已保存到: {args.output}")
        
    except Exception as e:
        logger.error(f"运行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 