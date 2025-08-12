#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具链集成测试
Toolchain Integration Test

验证FormalUnified工具链中各组件的协同工作能力
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import sys

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ToolchainIntegrationTest:
    """工具链集成测试"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
        self.base_path = Path(__file__).parent
        
    async def run_integration_tests(self):
        """运行集成测试"""
        logger.info("🔧 开始工具链集成测试")
        
        # 1. 测试理论到实践映射工具
        await self._test_theory_mapper()
        
        # 2. 测试自动化代码生成器
        await self._test_code_generator()
        
        # 3. 测试跨理论验证引擎
        await self._test_verification_engine()
        
        # 4. 测试综合演示脚本
        await self._test_comprehensive_demo()
        
        # 5. 测试工具间集成
        await self._test_tool_integration()
        
        # 6. 生成测试报告
        self._generate_test_report()
        
        logger.info("✅ 工具链集成测试完成")
    
    async def _test_theory_mapper(self):
        """测试理论到实践映射工具"""
        logger.info("📋 测试理论到实践映射工具")
        
        try:
            # 测试describe功能
            result = subprocess.run([
                sys.executable, str(self.base_path / "theory_to_practice_mapper.py"),
                "--describe", "--config", str(self.base_path / "config.yaml")
            ], capture_output=True, text=True, check=True)
            
            describe_data = json.loads(result.stdout)
            if describe_data.get("status") == "ok":
                self.test_results["theory_mapper"] = {
                    "status": "PASS",
                    "supported_languages": describe_data["data"]["supported_languages"],
                    "supported_patterns": describe_data["data"]["supported_patterns"],
                    "coverage": describe_data["data"]["coverage"]
                }
                logger.info("✅ 理论映射工具测试通过")
            else:
                self.test_results["theory_mapper"] = {"status": "FAIL", "error": "describe返回异常"}
                
        except Exception as e:
            self.test_results["theory_mapper"] = {"status": "FAIL", "error": str(e)}
            logger.error(f"❌ 理论映射工具测试失败: {e}")
    
    async def _test_code_generator(self):
        """测试自动化代码生成器"""
        logger.info("⚙️ 测试自动化代码生成器")
        
        try:
            # 测试干跑模式
            result = subprocess.run([
                sys.executable, str(self.base_path / "AutomatedCodeGenerator" / "automated_code_generator.py"),
                "--language", "python", "--pattern", "state_machine", "--dry-run",
                "--config", str(self.base_path / "config.yaml")
            ], capture_output=True, text=True, check=True)
            
            if "生成" in result.stdout and "文件" in result.stdout:
                self.test_results["code_generator"] = {
                    "status": "PASS",
                    "output": result.stdout.strip()
                }
                logger.info("✅ 代码生成器测试通过")
            else:
                self.test_results["code_generator"] = {"status": "FAIL", "error": "输出格式异常"}
                
        except Exception as e:
            self.test_results["code_generator"] = {"status": "FAIL", "error": str(e)}
            logger.error(f"❌ 代码生成器测试失败: {e}")
    
    async def _test_verification_engine(self):
        """测试跨理论验证引擎"""
        logger.info("🔍 测试跨理论验证引擎")
        
        try:
            # 运行验证引擎
            result = subprocess.run([
                sys.executable, str(self.base_path / "CrossTheoryVerificationEngine.py")
            ], capture_output=True, text=True, check=True)
            
            if "验证结果已导出" in result.stdout:
                # 检查输出文件
                output_dir = Path("verification_output")
                if output_dir.exists() and (output_dir / "verification_report.json").exists():
                    self.test_results["verification_engine"] = {
                        "status": "PASS",
                        "output_files": [f.name for f in output_dir.iterdir() if f.is_file()]
                    }
                    logger.info("✅ 验证引擎测试通过")
                else:
                    self.test_results["verification_engine"] = {"status": "FAIL", "error": "输出文件缺失"}
            else:
                self.test_results["verification_engine"] = {"status": "FAIL", "error": "验证过程异常"}
                
        except Exception as e:
            self.test_results["verification_engine"] = {"status": "FAIL", "error": str(e)}
            logger.error(f"❌ 验证引擎测试失败: {e}")
    
    async def _test_comprehensive_demo(self):
        """测试综合演示脚本"""
        logger.info("🎭 测试综合演示脚本")
        
        try:
            # 运行综合演示
            result = subprocess.run([
                sys.executable, str(self.base_path / "comprehensive_demo.py")
            ], capture_output=True, text=True, check=True)
            
            if "综合演示完成" in result.stdout:
                # 检查输出文件
                demo_files = ["demo_report.json", "demo_report.md"]
                existing_files = [f for f in demo_files if Path(f).exists()]
                
                self.test_results["comprehensive_demo"] = {
                    "status": "PASS",
                    "output_files": existing_files
                }
                logger.info("✅ 综合演示测试通过")
            else:
                self.test_results["comprehensive_demo"] = {"status": "FAIL", "error": "演示过程异常"}
                
        except Exception as e:
            self.test_results["comprehensive_demo"] = {"status": "FAIL", "error": str(e)}
            logger.error(f"❌ 综合演示测试失败: {e}")
    
    async def _test_tool_integration(self):
        """测试工具间集成"""
        logger.info("🔗 测试工具间集成")
        
        try:
            # 测试映射工具与代码生成器的集成
            # 1. 获取映射信息
            mapper_result = subprocess.run([
                sys.executable, str(self.base_path / "theory_to_practice_mapper.py"),
                "--pattern", "state_machine", "--language", "rust",
                "--config", str(self.base_path / "config.yaml")
            ], capture_output=True, text=True, check=True)
            
            mapper_data = json.loads(mapper_result.stdout)
            
            if mapper_data.get("status") == "ok":
                # 2. 使用相同参数运行代码生成器
                generator_result = subprocess.run([
                    sys.executable, str(self.base_path / "AutomatedCodeGenerator" / "automated_code_generator.py"),
                    "--language", "rust", "--pattern", "state_machine", "--dry-run",
                    "--config", str(self.base_path / "config.yaml")
                ], capture_output=True, text=True, check=True)
                
                if "映射模板" in generator_result.stdout and "生成" in generator_result.stdout:
                    self.test_results["tool_integration"] = {
                        "status": "PASS",
                        "mapper_template": mapper_data.get("template_name"),
                        "integration_flow": "映射工具 → 代码生成器"
                    }
                    logger.info("✅ 工具集成测试通过")
                else:
                    self.test_results["tool_integration"] = {"status": "FAIL", "error": "集成流程异常"}
            else:
                self.test_results["tool_integration"] = {"status": "FAIL", "error": "映射工具返回异常"}
                
        except Exception as e:
            self.test_results["tool_integration"] = {"status": "FAIL", "error": str(e)}
            logger.error(f"❌ 工具集成测试失败: {e}")
    
    def _generate_test_report(self):
        """生成测试报告"""
        logger.info("📊 生成集成测试报告")
        
        # 计算测试时间
        test_duration = time.time() - self.start_time
        
        # 统计测试结果
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result.get("status") == "PASS")
        failed_tests = total_tests - passed_tests
        
        # 生成报告
        report = {
            "test_info": {
                "test_duration": f"{test_duration:.2f}秒",
                "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": f"{(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%"
            },
            "test_results": self.test_results,
            "summary": {
                "overall_status": "PASS" if failed_tests == 0 else "FAIL",
                "recommendations": self._generate_recommendations()
            }
        }
        
        # 保存报告
        report_file = Path("toolchain_integration_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # 生成Markdown报告
        markdown_report = self._generate_markdown_report(report)
        markdown_file = Path("toolchain_integration_report.md")
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        
        logger.info(f"✅ 集成测试报告已生成: {report_file}, {markdown_file}")
    
    def _generate_recommendations(self) -> List[str]:
        """生成建议"""
        recommendations = []
        
        failed_tests = [name for name, result in self.test_results.items() if result.get("status") == "FAIL"]
        
        if failed_tests:
            recommendations.append(f"需要修复失败的测试: {', '.join(failed_tests)}")
        
        if "theory_mapper" in self.test_results and self.test_results["theory_mapper"].get("status") == "PASS":
            coverage = self.test_results["theory_mapper"].get("coverage", {})
            if coverage:
                total_combinations = sum(len(langs) for langs in coverage.values())
                recommendations.append(f"映射工具支持 {total_combinations} 种模式-语言组合")
        
        if "tool_integration" in self.test_results and self.test_results["tool_integration"].get("status") == "PASS":
            recommendations.append("工具链集成良好，可以支持端到端的理论到代码生成流程")
        
        return recommendations
    
    def _generate_markdown_report(self, report: Dict[str, Any]) -> str:
        """生成Markdown格式的报告"""
        md = "# 工具链集成测试报告\n\n"
        
        # 测试信息
        md += "## 测试信息\n\n"
        md += f"- **测试时间**: {report['test_info']['test_time']}\n"
        md += f"- **测试时长**: {report['test_info']['test_duration']}\n"
        md += f"- **总测试数**: {report['test_info']['total_tests']}\n"
        md += f"- **通过测试**: {report['test_info']['passed_tests']}\n"
        md += f"- **失败测试**: {report['test_info']['failed_tests']}\n"
        md += f"- **成功率**: {report['test_info']['success_rate']}\n\n"
        
        # 测试结果
        md += "## 测试结果\n\n"
        for test_name, result in report['test_results'].items():
            status_icon = "✅" if result.get("status") == "PASS" else "❌"
            md += f"### {test_name}\n"
            md += f"- **状态**: {status_icon} {result.get('status')}\n"
            
            if result.get("status") == "PASS":
                for key, value in result.items():
                    if key != "status":
                        md += f"- **{key}**: {value}\n"
            else:
                md += f"- **错误**: {result.get('error', '未知错误')}\n"
            md += "\n"
        
        # 总结
        md += "## 总结\n\n"
        md += f"- **总体状态**: {report['summary']['overall_status']}\n\n"
        
        if report['summary']['recommendations']:
            md += "### 建议\n\n"
            for rec in report['summary']['recommendations']:
                md += f"- {rec}\n"
        
        return md

async def main():
    """主函数"""
    test = ToolchainIntegrationTest()
    await test.run_integration_tests()

if __name__ == "__main__":
    asyncio.run(main()) 