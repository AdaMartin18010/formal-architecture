#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
形式化架构理论工具链命令行界面
提供用户友好的交互式操作和帮助信息
"""

import sys
import os
import json
import logging
import argparse
import cmd
import shlex
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
import asyncio
import threading
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入工具模块
try:
    from enhanced_toolchain import EnhancedToolchain
    from TestingFramework.comprehensive_test_suite import ComprehensiveTestRunner
except ImportError as e:
    logging.error(f"导入工具模块失败: {e}")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class FormalismCLI(cmd.Cmd):
    """形式化架构理论工具链命令行界面"""
    
    intro = """
🚀 欢迎使用形式化架构理论工具链！
=====================================

这是一个强大的工具链，集成了AI建模、形式验证、代码生成等功能。

输入 'help' 查看所有可用命令
输入 'help <command>' 查看特定命令的详细帮助
输入 'quit' 或 'exit' 退出程序

开始您的形式化架构之旅吧！ 🎯
"""
    
    prompt = 'formalism> '
    
    def __init__(self):
        super().__init__()
        self.toolchain = None
        self.test_runner = None
        self.current_project = None
        self.config = {}
        
        # 初始化工具链
        self._initialize_tools()
        
        # 加载配置
        self._load_config()
    
    def _initialize_tools(self):
        """初始化工具"""
        try:
            self.toolchain = EnhancedToolchain()
            self.test_runner = ComprehensiveTestRunner()
            logger.info("✅ 工具链初始化成功")
        except Exception as e:
            logger.error(f"❌ 工具链初始化失败: {e}")
    
    def _load_config(self):
        """加载配置文件"""
        config_file = Path(__file__).parent / "cli_config.yaml"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f)
                logger.info("✅ 配置文件加载成功")
            except Exception as e:
                logger.error(f"❌ 配置文件加载失败: {e}")
        else:
            logger.warning("⚠️ 配置文件不存在，使用默认配置")
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'default_language': 'rust',
            'output_directory': './generated_code',
            'test_enabled': True,
            'visualization_enabled': True,
            'verification_enabled': True
        }
    
    def do_help(self, arg):
        """显示帮助信息"""
        if arg:
            super().do_help(arg)
        else:
            print("""
📚 可用命令列表：
==================

🏗️  建模与设计：
  model <需求描述>     - 使用AI建模引擎创建架构模型
  visualize <模型ID>   - 生成模型可视化图表
  verify <模型ID>      - 执行形式化验证
  
💻  代码生成：
  generate <模型ID>    - 生成实现代码
  build <项目名>       - 构建项目
  deploy <项目名>      - 部署项目
  
🧪  测试与验证：
  test <类型>          - 运行测试套件
  benchmark <模型ID>   - 执行性能基准测试
  coverage <项目名>    - 生成代码覆盖率报告
  
📊  项目管理：
  new <项目名>         - 创建新项目
  open <项目路径>      - 打开现有项目
  list                 - 列出所有项目
  status               - 显示当前项目状态
  
🔧  工具管理：
  config               - 显示/修改配置
  update               - 更新工具链
  version              - 显示版本信息
  
❓  帮助与信息：
  help                 - 显示此帮助信息
  help <命令>          - 显示特定命令的详细帮助
  examples             - 显示使用示例
  about                - 关于此工具链
  
🚪  退出：
  quit, exit           - 退出程序
  clear                - 清屏

输入 'help <命令名>' 获取详细帮助信息。
""")
    
    def do_model(self, arg):
        """使用AI建模引擎创建架构模型
        
用法: model <需求描述>
        
示例:
  model "创建一个微服务架构的电商系统"
  model "设计一个分布式数据库系统，要求高可用性"
        """
        if not arg:
            print("❌ 请提供需求描述")
            print("用法: model <需求描述>")
            return
        
        if not self.toolchain:
            print("❌ 工具链未初始化")
            return
        
        print(f"🤖 AI建模引擎正在分析需求: {arg}")
        
        try:
            # 配置工作流程
            workflow_config = {
                'modeling': {
                    'requirements': arg,
                    'model_type': 'MICROSERVICE'  # 默认类型
                }
            }
            
            # 执行建模
            results = self.toolchain.execute_workflow(workflow_config)
            
            if results.get('modeling', {}).success:
                model_data = results['modeling'].data
                print(f"✅ 模型创建成功！")
                print(f"   模型ID: {model_data.get('model_id', 'N/A')}")
                print(f"   类型: {model_data.get('type', 'N/A')}")
                print(f"   元素数量: {model_data.get('elements_count', 'N/A')}")
                
                # 保存模型信息
                self.current_project = {
                    'model_id': model_data.get('model_id'),
                    'model_data': model_data,
                    'created_at': datetime.now().isoformat()
                }
                
                print(f"\n💡 提示: 使用 'visualize {model_data.get('model_id')}' 生成可视化图表")
                print(f"💡 提示: 使用 'verify {model_data.get('model_id')}' 执行形式验证")
                
            else:
                print(f"❌ 模型创建失败: {results['modeling'].error}")
                
        except Exception as e:
            print(f"❌ 建模过程出错: {e}")
            logger.error(f"建模失败: {e}")
    
    def do_visualize(self, arg):
        """生成模型可视化图表
        
用法: visualize <模型ID>
        """
        if not arg:
            print("❌ 请提供模型ID")
            print("用法: visualize <模型ID>")
            return
        
        if not self.current_project or self.current_project['model_id'] != arg:
            print("❌ 模型ID不存在或未找到")
            return
        
        print(f"🎨 正在生成模型可视化图表...")
        
        try:
            # 配置可视化工作流程
            workflow_config = {
                'modeling': {
                    'requirements': 'visualization request',
                    'model_type': 'VISUALIZATION'
                },
                'visualization': {
                    'output_file': f"visualization_{arg}.png"
                }
            }
            
            # 执行可视化
            results = self.toolchain.execute_workflow(workflow_config)
            
            if results.get('visualization', {}).success:
                output_file = results['visualization'].data['output_file']
                print(f"✅ 可视化图表生成成功！")
                print(f"   输出文件: {output_file}")
            else:
                print(f"❌ 可视化生成失败: {results['visualization'].error}")
                
        except Exception as e:
            print(f"❌ 可视化过程出错: {e}")
            logger.error(f"可视化失败: {e}")
    
    def do_verify(self, arg):
        """执行形式化验证
        
用法: verify <模型ID>
        """
        if not arg:
            print("❌ 请提供模型ID")
            print("用法: verify <模型ID>")
            return
        
        if not self.current_project or self.current_project['model_id'] != arg:
            print("❌ 模型ID不存在或未找到")
            return
        
        print(f"🔍 正在执行形式化验证...")
        
        try:
            # 配置验证工作流程
            workflow_config = {
                'modeling': {
                    'requirements': 'verification request',
                    'model_type': 'VERIFICATION'
                },
                'verification': {
                    'properties': [
                        '服务间依赖无循环',
                        '数据一致性保证',
                        '故障隔离性',
                        '可扩展性验证'
                    ]
                }
            }
            
            # 执行验证
            results = self.toolchain.execute_workflow(workflow_config)
            
            if results.get('verification', {}).success:
                verification_data = results['verification'].data
                print(f"✅ 形式化验证完成！")
                
                # 显示验证结果
                if 'results' in verification_data:
                    for result in verification_data['results']:
                        status = "✅" if result['status'] == 'PASSED' else "❌"
                        print(f"   {status} {result['property']}: {result['status']}")
                        if result.get('details'):
                            print(f"      详情: {result['details']}")
                
                overall_status = verification_data.get('overall_status', 'UNKNOWN')
                print(f"\n📊 总体验证状态: {overall_status}")
                
            else:
                print(f"❌ 验证失败: {results['verification'].error}")
                
        except Exception as e:
            print(f"❌ 验证过程出错: {e}")
            logger.error(f"验证失败: {e}")
    
    def do_generate(self, arg):
        """生成实现代码
        
用法: generate <模型ID> [语言]
        
示例:
  generate model_001
  generate model_001 rust
  generate model_001 golang
        """
        if not arg:
            print("❌ 请提供模型ID")
            print("用法: generate <模型ID> [语言]")
            return
        
        if not self.current_project or self.current_project['model_id'] != arg:
            print("❌ 模型ID不存在或未找到")
            return
        
        # 解析语言参数
        parts = arg.split()
        model_id = parts[0]
        language = parts[1] if len(parts) > 1 else self.config.get('default_language', 'rust')
        
        print(f"💻 正在生成 {language} 实现代码...")
        
        try:
            # 配置代码生成工作流程
            workflow_config = {
                'modeling': {
                    'requirements': 'code generation request',
                    'model_type': 'CODE_GENERATION'
                },
                'code_generation': {
                    'target_language': language,
                    'output_dir': f"./generated_{language}_code"
                }
            }
            
            # 执行代码生成
            results = self.toolchain.execute_workflow(workflow_config)
            
            if results.get('code_generation', {}).success:
                code_data = results['code_generation'].data
                print(f"✅ 代码生成成功！")
                print(f"   目标语言: {code_data['target_language']}")
                print(f"   输出目录: {code_data['output_dir']}")
                print(f"   生成文件: {', '.join(code_data['generated_files'])}")
                
                print(f"\n💡 提示: 使用 'build {model_id}' 构建项目")
                print(f"💡 提示: 使用 'deploy {model_id}' 部署项目")
                
            else:
                print(f"❌ 代码生成失败: {results['code_generation'].error}")
                
        except Exception as e:
            print(f"❌ 代码生成过程出错: {e}")
            logger.error(f"代码生成失败: {e}")
    
    def do_test(self, arg):
        """运行测试套件
        
用法: test [类型]
        
类型:
  unit        - 单元测试
  integration - 集成测试
  performance - 性能测试
  e2e         - 端到端测试
  all         - 所有测试 (默认)
        """
        if not self.test_runner:
            print("❌ 测试运行器未初始化")
            return
        
        test_type = arg.lower() if arg else 'all'
        
        print(f"🧪 正在运行 {test_type} 测试...")
        
        try:
            if test_type == 'all':
                # 运行所有测试
                report = self.test_runner.run_all_tests(parallel=True)
            elif test_type == 'unit':
                # 运行单元测试
                report = {'unit_tests': self.test_runner.unit_suite.run_tests().get_summary()}
            elif test_type == 'integration':
                # 运行集成测试
                report = {'integration_tests': self.test_runner.integration_suite.run_tests().get_summary()}
            elif test_type == 'performance':
                # 运行性能测试
                report = {'performance_tests': self.test_runner.performance_suite.run_tests().get_summary()}
            elif test_type == 'e2e':
                # 运行端到端测试
                report = {'e2e_tests': self.test_runner.e2e_suite.run_tests().get_summary()}
            else:
                print(f"❌ 未知的测试类型: {test_type}")
                print("可用类型: unit, integration, performance, e2e, all")
                return
            
            # 显示测试结果
            self._display_test_results(report)
            
        except Exception as e:
            print(f"❌ 测试执行出错: {e}")
            logger.error(f"测试失败: {e}")
    
    def _display_test_results(self, report: Dict[str, Any]):
        """显示测试结果"""
        print(f"\n📊 测试结果摘要:")
        print("=" * 40)
        
        for test_type, results in report.items():
            if isinstance(results, dict) and 'total_tests' in results:
                print(f"\n{test_type.replace('_', ' ').title()}:")
                print(f"  总测试数: {results['total_tests']}")
                print(f"  通过测试: {results['passed_tests']}")
                print(f"  失败测试: {results['failed_tests']}")
                print(f"  错误测试: {results['error_tests']}")
                print(f"  跳过测试: {results['skipped_tests']}")
                print(f"  成功率: {results['success_rate']}")
                print(f"  总耗时: {results['total_duration']}")
        
        print("=" * 40)
    
    def do_new(self, arg):
        """创建新项目
        
用法: new <项目名>
        """
        if not arg:
            print("❌ 请提供项目名")
            print("用法: new <项目名>")
            return
        
        project_name = arg
        project_path = Path(project_name)
        
        if project_path.exists():
            print(f"❌ 项目目录已存在: {project_path}")
            return
        
        try:
            # 创建项目目录
            project_path.mkdir(parents=True)
            
            # 创建项目结构
            (project_path / "src").mkdir()
            (project_path / "tests").mkdir()
            (project_path / "docs").mkdir()
            (project_path / "config").mkdir()
            
            # 创建配置文件
            config_file = project_path / "config" / "project.yaml"
            config_content = {
                'project': {
                    'name': project_name,
                    'version': '1.0.0',
                    'description': f'{project_name} 项目',
                    'created_at': datetime.now().isoformat()
                },
                'architecture': {
                    'type': 'microservice',
                    'language': 'rust',
                    'framework': 'actix-web'
                }
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_content, f, default_flow_style=False, allow_unicode=True)
            
            # 创建README
            readme_file = project_path / "README.md"
            readme_content = f"""# {project_name}

## 项目概述

这是一个使用形式化架构理论工具链创建的项目。

## 项目结构

```
{project_name}/
├── src/           # 源代码
├── tests/         # 测试文件
├── docs/          # 文档
├── config/        # 配置文件
└── README.md      # 项目说明
```

## 快速开始

1. 进入项目目录: `cd {project_name}`
2. 查看配置: `cat config/project.yaml`
3. 开始开发！

## 技术栈

- 架构类型: 微服务
- 编程语言: Rust
- Web框架: Actix-web
- 数据库: PostgreSQL
- 缓存: Redis

---
*由形式化架构理论工具链生成*
"""
            
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            print(f"✅ 项目 '{project_name}' 创建成功！")
            print(f"   项目路径: {project_path.absolute()}")
            print(f"   配置文件: {config_file}")
            print(f"   说明文档: {readme_file}")
            
            # 设置为当前项目
            self.current_project = {
                'name': project_name,
                'path': str(project_path.absolute()),
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ 项目创建失败: {e}")
            logger.error(f"项目创建失败: {e}")
    
    def do_list(self, arg):
        """列出所有项目"""
        projects_dir = Path.cwd()
        
        print(f"📁 当前目录下的项目:")
        print("=" * 50)
        
        project_count = 0
        for item in projects_dir.iterdir():
            if item.is_dir():
                config_file = item / "config" / "project.yaml"
                if config_file.exists():
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config = yaml.safe_load(f)
                        
                        project_info = config.get('project', {})
                        name = project_info.get('name', item.name)
                        version = project_info.get('version', 'N/A')
                        description = project_info.get('description', '无描述')
                        
                        print(f"📦 {name} (v{version})")
                        print(f"   描述: {description}")
                        print(f"   路径: {item.absolute()}")
                        
                        if self.current_project and self.current_project.get('name') == name:
                            print(f"   🔵 当前项目")
                        
                        print()
                        project_count += 1
                        
                    except Exception as e:
                        print(f"📁 {item.name} (配置文件读取失败)")
                        print()
        
        if project_count == 0:
            print("   暂无项目")
        
        print("=" * 50)
        print(f"总计: {project_count} 个项目")
    
    def do_status(self, arg):
        """显示当前项目状态"""
        if not self.current_project:
            print("❌ 当前没有打开的项目")
            return
        
        print(f"📊 当前项目状态:")
        print("=" * 40)
        
        if 'name' in self.current_project:
            # 普通项目
            print(f"项目名称: {self.current_project['name']}")
            print(f"项目路径: {self.current_project['path']}")
            print(f"创建时间: {self.current_project['created_at']}")
        else:
            # 建模项目
            print(f"模型ID: {self.current_project['model_id']}")
            print(f"创建时间: {self.current_project['created_at']}")
            
            if 'model_data' in self.current_project:
                model_data = self.current_project['model_data']
                print(f"模型类型: {model_data.get('type', 'N/A')}")
                print(f"元素数量: {model_data.get('elements_count', 'N/A')}")
        
        print("=" * 40)
    
    def do_config(self, arg):
        """显示/修改配置
        
用法: config [配置项] [新值]
        
示例:
  config                    - 显示所有配置
  config default_language   - 显示特定配置项
  config default_language golang  - 修改配置项
        """
        if not arg:
            # 显示所有配置
            print("⚙️ 当前配置:")
            print("=" * 40)
            for key, value in self.config.items():
                print(f"{key}: {value}")
            print("=" * 40)
            return
        
        parts = arg.split()
        config_key = parts[0]
        
        if config_key not in self.config:
            print(f"❌ 未知的配置项: {config_key}")
            print(f"可用配置项: {', '.join(self.config.keys())}")
            return
        
        if len(parts) == 1:
            # 显示特定配置项
            print(f"⚙️ {config_key}: {self.config[config_key]}")
        elif len(parts) == 2:
            # 修改配置项
            new_value = parts[1]
            old_value = self.config[config_key]
            
            # 尝试类型转换
            try:
                if isinstance(old_value, bool):
                    if new_value.lower() in ['true', '1', 'yes', 'on']:
                        new_value = True
                    elif new_value.lower() in ['false', '0', 'no', 'off']:
                        new_value = False
                    else:
                        raise ValueError("布尔值无效")
                elif isinstance(old_value, int):
                    new_value = int(new_value)
                elif isinstance(old_value, float):
                    new_value = float(new_value)
                
                self.config[config_key] = new_value
                print(f"✅ 配置已更新: {config_key} = {new_value}")
                
                # 保存配置到文件
                self._save_config()
                
            except ValueError as e:
                print(f"❌ 配置值无效: {e}")
                print(f"期望类型: {type(old_value).__name__}")
        else:
            print("❌ 参数数量错误")
            print("用法: config [配置项] [新值]")
    
    def _save_config(self):
        """保存配置到文件"""
        config_file = Path(__file__).parent / "cli_config.yaml"
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            logger.info("配置已保存")
        except Exception as e:
            logger.error(f"配置保存失败: {e}")
    
    def do_examples(self, arg):
        """显示使用示例"""
        print("""
💡 使用示例：
=============

1. 🏗️ 创建电商系统架构：
   formalism> model "创建一个微服务架构的电商系统，包含用户管理、商品管理、订单管理、支付服务"
   
2. 🎨 生成可视化图表：
   formalism> visualize model_001
   
3. 🔍 执行形式验证：
   formalism> verify model_001
   
4. 💻 生成Rust代码：
   formalism> generate model_001 rust
   
5. 🧪 运行所有测试：
   formalism> test all
   
6. 📁 创建新项目：
   formalism> new my_ecommerce_system
   
7. 📊 查看项目状态：
   formalism> status
   
8. ⚙️ 修改配置：
   formalism> config default_language golang

🎯 完整工作流程示例：
======================

# 1. 创建新项目
formalism> new ecommerce_system

# 2. 使用AI建模
formalism> model "设计一个高可用的电商微服务系统"

# 3. 生成可视化
formalism> visualize model_001

# 4. 执行验证
formalism> verify model_001

# 5. 生成代码
formalism> generate model_001 rust

# 6. 运行测试
formalism> test all

# 7. 查看状态
formalism> status

这样您就完成了一个完整的从需求到代码的流程！ 🎉
""")
    
    def do_about(self, arg):
        """关于此工具链"""
        print("""
🌟 形式化架构理论工具链
==========================

这是一个革命性的软件架构设计工具，将形式化理论与AI智能相结合，
为软件工程提供科学化的理论基础和智能化的实践工具。

🔬 核心特性：
• AI增强的架构建模
• 形式化验证与证明
• 自动化代码生成
• 智能测试与验证
• 可视化架构设计

🏗️ 技术架构：
• 哲学基础理论
• 数学理论体系
• 形式语言理论
• 编程语言理论
• 软件架构理论
• 分布式系统理论

🤖 AI建模引擎：
• 91个深度理论文档
• 双向递归推理
• 智能需求分析
• 自动架构生成

📚 理论基础：
• 集合论与范畴论
• 自动机理论
• 类型理论
• 进程代数
• 时态逻辑

🎯 应用场景：
• 微服务架构设计
• 分布式系统建模
• 实时系统验证
• 安全协议设计
• 并发系统分析

🌐 支持语言：
• Rust
• Go
• Python
• Java
• C++

📖 更多信息：
• 项目主页: https://github.com/your-repo
• 文档: ./docs/
• 理论体系: ./FormalUnified/
• AI引擎: ./AI-Modeling-Engine/

---
*让软件架构设计更加科学、智能、可靠* 🚀
""")
    
    def do_version(self, arg):
        """显示版本信息"""
        print("""
📦 形式化架构理论工具链
版本: v1.0.0
构建日期: 2024年12月
Python版本: 3.8+

🔄 更新日志：
• v1.0.0 - 初始版本发布
  - AI建模引擎
  - 形式验证工具
  - 代码生成器
  - 综合测试框架
  - 命令行界面

📋 系统要求：
• Python 3.8+
• 8GB RAM (推荐)
• 2GB 磁盘空间
• 支持的操作系统: Linux, macOS, Windows

🔧 依赖组件：
• AI建模引擎: v1.0.0
• 形式验证工具: v1.0.0
• 测试框架: v1.0.0
• 可视化工具: v1.0.0
""")
    
    def do_clear(self, arg):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def do_quit(self, arg):
        """退出程序"""
        print("👋 感谢使用形式化架构理论工具链！")
        print("期待下次相见！ 🚀")
        return True
    
    def do_exit(self, arg):
        """退出程序"""
        return self.do_quit(arg)
    
    def default(self, line):
        """处理未知命令"""
        print(f"❓ 未知命令: {line}")
        print("输入 'help' 查看可用命令")
    
    def emptyline(self):
        """处理空行"""
        pass

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='形式化架构理论工具链命令行界面',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                    # 启动交互式界面
  %(prog)s --version          # 显示版本信息
  %(prog)s --help             # 显示帮助信息
        """
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='形式化架构理论工具链 v1.0.0'
    )
    
    args = parser.parse_args()
    
    try:
        # 启动CLI
        cli = FormalismCLI()
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\n\n👋 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")
        logger.error(f"程序运行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 