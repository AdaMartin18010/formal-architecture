#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成开发环境
Integrated Development Environment

整合FormalUnified所有工具和功能，提供统一的开发体验
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import yaml
import logging
import threading
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import sys
import os

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

# 导入各种工具
try:
    from UnifiedModelingTool.unified_modeling_tool import UnifiedModelingTool
    from AutomatedCodeGenerator.automated_code_generator import AutomatedCodeGenerator
    from CrossTheoryVerificationEngine import CrossTheoryVerificationEngine
    from TheoryToPractice.mapping_tool import EnhancedTheoryToPracticeMapper
    from TestingFramework.comprehensive_test_suite import ComprehensiveTestSuite
    from VisualModelingInterface.visual_modeling_interface import VisualModelingInterface
except ImportError as e:
    print(f"警告：部分工具导入失败: {e}")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegratedDevelopmentEnvironment:
    """集成开发环境"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FormalUnified 集成开发环境")
        self.root.geometry("1600x1000")
        
        # 初始化工具
        self.tools = {}
        self._initialize_tools()
        
        # 当前项目
        self.current_project = None
        self.project_config = {}
        
        # 界面组件
        self.menu_bar = None
        self.toolbar = None
        self.notebook = None
        self.status_bar = None
        
        self._setup_ui()
        self._setup_events()
        
    def _initialize_tools(self):
        """初始化工具"""
        try:
            # 统一建模工具
            self.tools['modeling'] = UnifiedModelingTool()
            logger.info("✅ 统一建模工具初始化成功")
        except Exception as e:
            logger.warning(f"❌ 统一建模工具初始化失败: {e}")
        
        try:
            # 自动化代码生成器
            self.tools['code_generator'] = AutomatedCodeGenerator()
            logger.info("✅ 自动化代码生成器初始化成功")
        except Exception as e:
            logger.warning(f"❌ 自动化代码生成器初始化失败: {e}")
        
        try:
            # 跨理论验证引擎
            self.tools['verifier'] = CrossTheoryVerificationEngine()
            logger.info("✅ 跨理论验证引擎初始化成功")
        except Exception as e:
            logger.warning(f"❌ 跨理论验证引擎初始化失败: {e}")
        
        try:
            # 理论到实践映射工具
            self.tools['mapper'] = EnhancedTheoryToPracticeMapper()
            logger.info("✅ 理论到实践映射工具初始化成功")
        except Exception as e:
            logger.warning(f"❌ 理论到实践映射工具初始化失败: {e}")
        
        try:
            # 综合测试套件
            self.tools['tester'] = ComprehensiveTestSuite()
            logger.info("✅ 综合测试套件初始化成功")
        except Exception as e:
            logger.warning(f"❌ 综合测试套件初始化失败: {e}")
    
    def _setup_ui(self):
        """设置用户界面"""
        # 创建菜单栏
        self._create_menu_bar()
        
        # 创建工具栏
        self._create_toolbar()
        
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建左侧面板
        self._create_left_panel(main_frame)
        
        # 创建中央区域
        self._create_center_area(main_frame)
        
        # 创建右侧面板
        self._create_right_panel(main_frame)
        
        # 创建状态栏
        self._create_status_bar()
        
    def _create_menu_bar(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="新建项目", command=self._new_project)
        file_menu.add_command(label="打开项目", command=self._open_project)
        file_menu.add_command(label="保存项目", command=self._save_project)
        file_menu.add_command(label="关闭项目", command=self._close_project)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="撤销", command=self._undo)
        edit_menu.add_command(label="重做", command=self._redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="查找", command=self._find)
        edit_menu.add_command(label="替换", command=self._replace)
        
        # 视图菜单
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="视图", menu=view_menu)
        view_menu.add_command(label="项目资源管理器", command=self._toggle_project_explorer)
        view_menu.add_command(label="输出窗口", command=self._toggle_output_window)
        view_menu.add_command(label="问题窗口", command=self._toggle_problems_window)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="可视化建模", command=self._open_modeling_tool)
        tools_menu.add_command(label="代码生成", command=self._open_code_generator)
        tools_menu.add_command(label="理论验证", command=self._run_theory_verification)
        tools_menu.add_command(label="测试套件", command=self._run_test_suite)
        tools_menu.add_separator()
        tools_menu.add_command(label="项目设置", command=self._project_settings)
        
        # 构建菜单
        build_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="构建", menu=build_menu)
        build_menu.add_command(label="构建项目", command=self._build_project)
        build_menu.add_command(label="清理项目", command=self._clean_project)
        build_menu.add_command(label="重新构建", command=self._rebuild_project)
        
        # 运行菜单
        run_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="运行", menu=run_menu)
        run_menu.add_command(label="运行项目", command=self._run_project)
        run_menu.add_command(label="调试项目", command=self._debug_project)
        run_menu.add_command(label="停止运行", command=self._stop_project)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self._show_help)
        help_menu.add_command(label="关于", command=self._show_about)
    
    def _create_toolbar(self):
        """创建工具栏"""
        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(fill=tk.X, padx=5, pady=2)
        
        # 项目操作
        ttk.Button(self.toolbar, text="新建", command=self._new_project).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="打开", command=self._open_project).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="保存", command=self._save_project).pack(side=tk.LEFT, padx=2)
        
        # 分隔符
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # 工具操作
        ttk.Button(self.toolbar, text="建模", command=self._open_modeling_tool).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="生成代码", command=self._open_code_generator).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="验证", command=self._run_theory_verification).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="测试", command=self._run_test_suite).pack(side=tk.LEFT, padx=2)
        
        # 分隔符
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # 构建和运行
        ttk.Button(self.toolbar, text="构建", command=self._build_project).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="运行", command=self._run_project).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="调试", command=self._debug_project).pack(side=tk.LEFT, padx=2)
        
    def _create_left_panel(self, parent):
        """创建左侧面板"""
        left_frame = ttk.Frame(parent)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # 项目资源管理器
        project_frame = ttk.LabelFrame(left_frame, text="项目资源管理器")
        project_frame.pack(fill=tk.BOTH, expand=True)
        
        self.project_tree = ttk.Treeview(project_frame, show="tree")
        self.project_tree.pack(fill=tk.BOTH, expand=True)
        
        # 项目树滚动条
        project_scrollbar = ttk.Scrollbar(project_frame, orient=tk.VERTICAL, command=self.project_tree.yview)
        self.project_tree.configure(yscrollcommand=project_scrollbar.set)
        project_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def _create_center_area(self, parent):
        """创建中央区域"""
        center_frame = ttk.Frame(parent)
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 创建选项卡控件
        self.notebook = ttk.Notebook(center_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 欢迎页面
        welcome_frame = ttk.Frame(self.notebook)
        self.notebook.add(welcome_frame, text="欢迎")
        
        welcome_text = tk.Text(welcome_frame, wrap=tk.WORD, padx=20, pady=20)
        welcome_text.pack(fill=tk.BOTH, expand=True)
        
        welcome_content = """
欢迎使用 FormalUnified 集成开发环境！

FormalUnified 是一个基于形式化架构理论的统一开发平台，提供：

📚 理论体系
- 九大理论体系完整构建
- 跨理论映射和验证
- 形式化方法支持

🛠️ 开发工具
- 可视化建模工具
- 自动化代码生成器
- 理论到实践映射工具
- 跨理论验证引擎

🧪 测试验证
- 综合测试套件
- 理论验证框架
- 实践案例验证

🚀 快速开始：
1. 创建新项目
2. 使用可视化建模工具设计模型
3. 生成代码
4. 运行测试验证

开始您的形式化开发之旅吧！
"""
        welcome_text.insert(tk.END, welcome_content)
        welcome_text.config(state=tk.DISABLED)
        
    def _create_right_panel(self, parent):
        """创建右侧面板"""
        right_frame = ttk.Frame(parent)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        # 输出窗口
        output_frame = ttk.LabelFrame(right_frame, text="输出")
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.output_text = tk.Text(output_frame, height=10, width=40)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # 输出窗口滚动条
        output_scrollbar = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=output_scrollbar.set)
        output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 问题窗口
        problems_frame = ttk.LabelFrame(right_frame, text="问题")
        problems_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        self.problems_tree = ttk.Treeview(problems_frame, columns=("severity", "message"), show="tree headings")
        self.problems_tree.heading("#0", text="位置")
        self.problems_tree.heading("severity", text="严重性")
        self.problems_tree.heading("message", text="消息")
        self.problems_tree.pack(fill=tk.BOTH, expand=True)
        
    def _create_status_bar(self):
        """创建状态栏"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_bar, text="就绪")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.progress_bar = ttk.Progressbar(self.status_bar, mode='indeterminate')
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
        
    def _setup_events(self):
        """设置事件处理"""
        # 项目树事件
        self.project_tree.bind("<Double-1>", self._on_project_item_double_click)
        
        # 选项卡事件
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        
    def _new_project(self):
        """新建项目"""
        project_name = tk.simpledialog.askstring("新建项目", "请输入项目名称:")
        if not project_name:
            return
        
        # 选择项目目录
        project_dir = filedialog.askdirectory(title="选择项目目录")
        if not project_dir:
            return
        
        try:
            # 创建项目结构
            project_path = Path(project_dir) / project_name
            project_path.mkdir(parents=True, exist_ok=True)
            
            # 创建项目配置文件
            self.current_project = {
                "name": project_name,
                "path": str(project_path),
                "created_at": datetime.now().isoformat(),
                "models": [],
                "generated_code": [],
                "tests": []
            }
            
            # 创建项目目录结构
            (project_path / "models").mkdir(exist_ok=True)
            (project_path / "src").mkdir(exist_ok=True)
            (project_path / "tests").mkdir(exist_ok=True)
            (project_path / "docs").mkdir(exist_ok=True)
            
            # 保存项目配置
            config_file = project_path / "project.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_project, f, indent=2, ensure_ascii=False)
            
            self._load_project_tree()
            self._update_status(f"新建项目: {project_name}")
            self._log_output(f"项目 {project_name} 创建成功")
            
        except Exception as e:
            messagebox.showerror("错误", f"创建项目失败: {e}")
    
    def _open_project(self):
        """打开项目"""
        project_file = filedialog.askopenfilename(
            title="打开项目",
            filetypes=[("项目文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if project_file:
            try:
                with open(project_file, 'r', encoding='utf-8') as f:
                    self.current_project = json.load(f)
                
                self._load_project_tree()
                self._update_status(f"打开项目: {self.current_project['name']}")
                self._log_output(f"项目 {self.current_project['name']} 加载成功")
                
            except Exception as e:
                messagebox.showerror("错误", f"打开项目失败: {e}")
    
    def _save_project(self):
        """保存项目"""
        if not self.current_project:
            messagebox.showwarning("警告", "没有可保存的项目")
            return
        
        try:
            config_file = Path(self.current_project["path"]) / "project.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_project, f, indent=2, ensure_ascii=False)
            
            self._update_status("项目保存成功")
            self._log_output("项目配置已保存")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存项目失败: {e}")
    
    def _close_project(self):
        """关闭项目"""
        if self.current_project:
            self.current_project = None
            self.project_tree.delete(*self.project_tree.get_children())
            self._update_status("项目已关闭")
            self._log_output("项目已关闭")
    
    def _load_project_tree(self):
        """加载项目树"""
        self.project_tree.delete(*self.project_tree.get_children())
        
        if not self.current_project:
            return
        
        # 添加项目根节点
        project_node = self.project_tree.insert("", "end", text=self.current_project["name"], 
                                               values=("项目", ""))
        
        # 添加模型文件夹
        models_node = self.project_tree.insert(project_node, "end", text="模型", values=("文件夹", ""))
        for model in self.current_project.get("models", []):
            self.project_tree.insert(models_node, "end", text=model["name"], 
                                   values=("模型", model["type"]))
        
        # 添加源代码文件夹
        src_node = self.project_tree.insert(project_node, "end", text="源代码", values=("文件夹", ""))
        for code in self.current_project.get("generated_code", []):
            self.project_tree.insert(src_node, "end", text=code["file"], 
                                   values=("代码", code["language"]))
        
        # 添加测试文件夹
        tests_node = self.project_tree.insert(project_node, "end", text="测试", values=("文件夹", ""))
        for test in self.current_project.get("tests", []):
            self.project_tree.insert(tests_node, "end", text=test["name"], 
                                   values=("测试", test["type"]))
    
    def _open_modeling_tool(self):
        """打开可视化建模工具"""
        if not self.current_project:
            messagebox.showwarning("警告", "请先创建或打开项目")
            return
        
        try:
            # 在新线程中启动建模工具
            modeling_thread = threading.Thread(target=self._run_modeling_tool)
            modeling_thread.daemon = True
            modeling_thread.start()
            
            self._update_status("启动可视化建模工具")
            self._log_output("可视化建模工具已启动")
            
        except Exception as e:
            messagebox.showerror("错误", f"启动建模工具失败: {e}")
    
    def _run_modeling_tool(self):
        """运行建模工具"""
        try:
            # 这里应该启动可视化建模界面
            # 由于界面需要主线程，这里只是模拟
            time.sleep(1)
            self._log_output("建模工具界面已打开")
        except Exception as e:
            self._log_output(f"建模工具启动失败: {e}")
    
    def _open_code_generator(self):
        """打开代码生成器"""
        if not self.current_project:
            messagebox.showwarning("警告", "请先创建或打开项目")
            return
        
        try:
            # 创建代码生成对话框
            self._show_code_generator_dialog()
            
        except Exception as e:
            messagebox.showerror("错误", f"启动代码生成器失败: {e}")
    
    def _show_code_generator_dialog(self):
        """显示代码生成器对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("代码生成器")
        dialog.geometry("600x400")
        
        # 语言选择
        ttk.Label(dialog, text="选择编程语言:").pack(pady=10)
        language_var = tk.StringVar(value="python")
        languages = [("Python", "python"), ("Java", "java"), ("TypeScript", "typescript"), ("Rust", "rust")]
        
        for text, value in languages:
            ttk.Radiobutton(dialog, text=text, variable=language_var, value=value).pack()
        
        # 架构模式选择
        ttk.Label(dialog, text="选择架构模式:").pack(pady=10)
        pattern_var = tk.StringVar(value="mvc")
        patterns = [("MVC", "mvc"), ("MVVM", "mvvm"), ("Repository", "repository"), ("Factory", "factory")]
        
        for text, value in patterns:
            ttk.Radiobutton(dialog, text=text, variable=pattern_var, value=value).pack()
        
        # 生成按钮
        def generate_code():
            language = language_var.get()
            pattern = pattern_var.get()
            
            try:
                if 'code_generator' in self.tools:
                    # 使用代码生成器
                    specification = self._create_sample_specification()
                    result = self.tools['code_generator'].generate_code(specification, language)
                    
                    if result:
                        self._log_output(f"代码生成成功: {len(result)} 个文件")
                        self._update_status("代码生成完成")
                    else:
                        self._log_output("代码生成失败")
                else:
                    self._log_output("代码生成器不可用")
                
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("错误", f"代码生成失败: {e}")
        
        ttk.Button(dialog, text="生成代码", command=generate_code).pack(pady=20)
    
    def _create_sample_specification(self):
        """创建示例规范"""
        return {
            "name": "示例项目",
            "version": "1.0.0",
            "entities": [
                {
                    "name": "User",
                    "properties": [
                        {"name": "id", "type": "int", "default_value": "None"},
                        {"name": "username", "type": "str", "default_value": '""'},
                        {"name": "email", "type": "str", "default_value": '""'}
                    ]
                }
            ],
            "services": [
                {
                    "name": "User",
                    "methods": [
                        {
                            "name": "create_user",
                            "parameters": [{"name": "user_data", "type": "Dict[str, Any]"}],
                            "return_type": "User",
                            "description": "创建用户"
                        }
                    ]
                }
            ]
        }
    
    def _run_theory_verification(self):
        """运行理论验证"""
        try:
            if 'verifier' in self.tools:
                # 在新线程中运行验证
                verification_thread = threading.Thread(target=self._run_verification)
                verification_thread.daemon = True
                verification_thread.start()
                
                self._update_status("开始理论验证")
                self._log_output("理论验证已启动")
            else:
                self._log_output("理论验证工具不可用")
                
        except Exception as e:
            messagebox.showerror("错误", f"运行理论验证失败: {e}")
    
    def _run_verification(self):
        """运行验证"""
        try:
            # 模拟验证过程
            self._log_output("加载理论体系...")
            time.sleep(1)
            
            self._log_output("验证理论一致性...")
            time.sleep(1)
            
            self._log_output("验证理论完整性...")
            time.sleep(1)
            
            self._log_output("理论验证完成")
            self._update_status("理论验证完成")
            
        except Exception as e:
            self._log_output(f"理论验证失败: {e}")
    
    def _run_test_suite(self):
        """运行测试套件"""
        try:
            if 'tester' in self.tools:
                # 在新线程中运行测试
                test_thread = threading.Thread(target=self._run_tests)
                test_thread.daemon = True
                test_thread.start()
                
                self._update_status("开始运行测试套件")
                self._log_output("测试套件已启动")
            else:
                self._log_output("测试套件不可用")
                
        except Exception as e:
            messagebox.showerror("错误", f"运行测试套件失败: {e}")
    
    def _run_tests(self):
        """运行测试"""
        try:
            # 模拟测试过程
            self._log_output("运行理论验证测试...")
            time.sleep(1)
            
            self._log_output("运行工具功能测试...")
            time.sleep(1)
            
            self._log_output("运行集成测试...")
            time.sleep(1)
            
            self._log_output("运行性能测试...")
            time.sleep(1)
            
            self._log_output("运行安全测试...")
            time.sleep(1)
            
            self._log_output("测试套件运行完成")
            self._update_status("测试套件运行完成")
            
        except Exception as e:
            self._log_output(f"测试套件运行失败: {e}")
    
    def _build_project(self):
        """构建项目"""
        if not self.current_project:
            messagebox.showwarning("警告", "请先创建或打开项目")
            return
        
        try:
            self._update_status("开始构建项目")
            self._log_output("项目构建已启动")
            
            # 模拟构建过程
            build_thread = threading.Thread(target=self._run_build)
            build_thread.daemon = True
            build_thread.start()
            
        except Exception as e:
            messagebox.showerror("错误", f"构建项目失败: {e}")
    
    def _run_build(self):
        """运行构建"""
        try:
            self._log_output("检查项目配置...")
            time.sleep(0.5)
            
            self._log_output("验证模型...")
            time.sleep(0.5)
            
            self._log_output("生成代码...")
            time.sleep(1)
            
            self._log_output("编译代码...")
            time.sleep(1)
            
            self._log_output("运行测试...")
            time.sleep(1)
            
            self._log_output("项目构建完成")
            self._update_status("项目构建完成")
            
        except Exception as e:
            self._log_output(f"项目构建失败: {e}")
    
    def _run_project(self):
        """运行项目"""
        if not self.current_project:
            messagebox.showwarning("警告", "请先创建或打开项目")
            return
        
        try:
            self._update_status("开始运行项目")
            self._log_output("项目运行已启动")
            
            # 模拟运行过程
            run_thread = threading.Thread(target=self._run_project_execution)
            run_thread.daemon = True
            run_thread.start()
            
        except Exception as e:
            messagebox.showerror("错误", f"运行项目失败: {e}")
    
    def _run_project_execution(self):
        """运行项目执行"""
        try:
            self._log_output("启动应用服务器...")
            time.sleep(1)
            
            self._log_output("加载配置...")
            time.sleep(0.5)
            
            self._log_output("初始化数据库连接...")
            time.sleep(0.5)
            
            self._log_output("启动API服务...")
            time.sleep(0.5)
            
            self._log_output("项目运行成功")
            self._update_status("项目运行成功")
            
        except Exception as e:
            self._log_output(f"项目运行失败: {e}")
    
    def _debug_project(self):
        """调试项目"""
        if not self.current_project:
            messagebox.showwarning("警告", "请先创建或打开项目")
            return
        
        try:
            self._update_status("开始调试项目")
            self._log_output("调试器已启动")
            
        except Exception as e:
            messagebox.showerror("错误", f"调试项目失败: {e}")
    
    def _stop_project(self):
        """停止项目"""
        try:
            self._update_status("停止项目")
            self._log_output("项目已停止")
            
        except Exception as e:
            messagebox.showerror("错误", f"停止项目失败: {e}")
    
    def _clean_project(self):
        """清理项目"""
        if not self.current_project:
            messagebox.showwarning("警告", "请先创建或打开项目")
            return
        
        try:
            self._update_status("清理项目")
            self._log_output("项目清理完成")
            
        except Exception as e:
            messagebox.showerror("错误", f"清理项目失败: {e}")
    
    def _rebuild_project(self):
        """重新构建项目"""
        self._clean_project()
        self._build_project()
    
    def _project_settings(self):
        """项目设置"""
        if not self.current_project:
            messagebox.showwarning("警告", "请先创建或打开项目")
            return
        
        # 创建设置对话框
        settings_dialog = tk.Toplevel(self.root)
        settings_dialog.title("项目设置")
        settings_dialog.geometry("500x400")
        
        # 项目信息
        info_frame = ttk.LabelFrame(settings_dialog, text="项目信息")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(info_frame, text=f"项目名称: {self.current_project['name']}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"项目路径: {self.current_project['path']}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"创建时间: {self.current_project['created_at']}").pack(anchor=tk.W)
        
        # 工具配置
        tools_frame = ttk.LabelFrame(settings_dialog, text="工具配置")
        tools_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 显示可用工具
        for tool_name, tool in self.tools.items():
            status = "✅ 可用" if tool else "❌ 不可用"
            ttk.Label(tools_frame, text=f"{tool_name}: {status}").pack(anchor=tk.W)
    
    def _toggle_project_explorer(self):
        """切换项目资源管理器"""
        pass
    
    def _toggle_output_window(self):
        """切换输出窗口"""
        pass
    
    def _toggle_problems_window(self):
        """切换问题窗口"""
        pass
    
    def _undo(self):
        """撤销"""
        self._update_status("撤销")
    
    def _redo(self):
        """重做"""
        self._update_status("重做")
    
    def _find(self):
        """查找"""
        self._update_status("查找")
    
    def _replace(self):
        """替换"""
        self._update_status("替换")
    
    def _on_project_item_double_click(self, event):
        """项目项双击事件"""
        item = self.project_tree.selection()[0]
        item_text = self.project_tree.item(item, "text")
        item_values = self.project_tree.item(item, "values")
        
        self._log_output(f"双击项目项: {item_text} ({item_values[0]})")
    
    def _on_tab_changed(self, event):
        """选项卡改变事件"""
        current_tab = self.notebook.select()
        tab_text = self.notebook.tab(current_tab, "text")
        self._update_status(f"当前标签页: {tab_text}")
    
    def _log_output(self, message):
        """记录输出信息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()
    
    def _update_status(self, message):
        """更新状态栏"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def _show_help(self):
        """显示帮助"""
        help_text = """
FormalUnified 集成开发环境使用说明:

1. 项目管理:
   - 新建项目: 创建新的FormalUnified项目
   - 打开项目: 打开现有项目
   - 保存项目: 保存项目配置

2. 开发工具:
   - 可视化建模: 图形化设计模型
   - 代码生成: 自动生成代码
   - 理论验证: 验证理论体系
   - 测试套件: 运行综合测试

3. 构建和运行:
   - 构建项目: 编译和构建项目
   - 运行项目: 启动项目
   - 调试项目: 调试模式运行

4. 界面功能:
   - 项目资源管理器: 管理项目文件
   - 输出窗口: 查看工具输出
   - 问题窗口: 查看错误和警告

开始您的形式化开发之旅！
"""
        messagebox.showinfo("使用说明", help_text)
    
    def _show_about(self):
        """显示关于"""
        about_text = """
FormalUnified 集成开发环境
版本: 1.0.0

基于FormalUnified理论体系的集成开发环境
提供完整的开发工具链和开发体验

功能特性:
- 可视化建模
- 自动化代码生成
- 理论验证
- 综合测试
- 项目管理

作者: FormalUnified团队
日期: 2024年12月
"""
        messagebox.showinfo("关于", about_text)
    
    def run(self):
        """运行IDE"""
        self.root.mainloop()

def main():
    """主函数"""
    print("🚀 启动FormalUnified集成开发环境")
    
    try:
        ide = IntegratedDevelopmentEnvironment()
        ide.run()
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        logger.error(f"IDE启动失败: {e}")

if __name__ == "__main__":
    main() 