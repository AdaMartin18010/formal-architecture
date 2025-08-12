#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化建模界面 - 增强版
Enhanced Visual Modeling Interface

提供图形化的建模体验，支持拖拽式建模、实时预览、模型验证、协作编辑等功能
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import json
import yaml
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import sys
import os
import threading
import queue
import hashlib
import uuid
import time # Added for CollaborationListener

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

# 导入统一建模工具
try:
    from UnifiedModelingTool.unified_modeling_tool import (
        UnifiedModelingTool, ModelType, ElementType, 
        ModelElement, ModelRelationship, UnifiedModel
    )
except ImportError:
    print("警告：无法导入统一建模工具，将使用模拟模式")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedVisualModelingInterface:
    """增强版可视化建模界面"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FormalUnified 增强版可视化建模界面 v2.0")
        self.root.geometry("1600x1000")
        
        # 初始化建模工具
        try:
            self.modeling_tool = UnifiedModelingTool()
        except:
            self.modeling_tool = None
            logger.warning("使用模拟模式")
        
        # 当前模型和状态
        self.current_model = None
        self.selected_element = None
        self.model_history = []  # 模型历史记录
        self.undo_stack = []
        self.redo_stack = []
        self.model_versions = {}  # 版本管理
        
        # 协作功能
        self.collaboration_mode = False
        self.collaborators = []
        self.changes_queue = queue.Queue()
        
        # 性能优化
        self.render_cache = {}
        self.update_timer = None
        self.batch_updates = []
        
        # 智能提示
        self.suggestion_engine = SuggestionEngine()
        self.auto_complete = True
        
        # 界面组件
        self.toolbar = None
        self.sidebar = None
        self.canvas = None
        self.properties_panel = None
        self.status_bar = None
        self.console_panel = None
        self.minimap = None
        
        self._setup_ui()
        self._setup_events()
        self._start_background_tasks()
        
    def _setup_ui(self):
        """设置用户界面"""
        # 创建主菜单
        self._create_menu()
        
        # 创建工具栏
        self._create_toolbar()
        
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建侧边栏
        self._create_sidebar(main_frame)
        
        # 创建画布区域
        self._create_canvas_area(main_frame)
        
        # 创建属性面板
        self._create_properties_panel(main_frame)
        
        # 创建控制台面板
        self._create_console_panel(main_frame)
        
        # 创建小地图
        self._create_minimap(main_frame)
        
        # 创建状态栏
        self._create_status_bar()
        
    def _create_menu(self):
        """创建主菜单"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="新建模型", command=self._new_model, accelerator="Ctrl+N")
        file_menu.add_command(label="打开模型", command=self._open_model, accelerator="Ctrl+O")
        file_menu.add_command(label="保存模型", command=self._save_model, accelerator="Ctrl+S")
        file_menu.add_command(label="另存为", command=self._save_as_model, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="导入", command=self._import_model)
        file_menu.add_command(label="导出", command=self._export_model)
        file_menu.add_separator()
        file_menu.add_command(label="版本管理", command=self._version_management)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self._quit_app, accelerator="Ctrl+Q")
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="撤销", command=self._undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="重做", command=self._redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="剪切", command=self._cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="复制", command=self._copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="粘贴", command=self._paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="全选", command=self._select_all, accelerator="Ctrl+A")
        edit_menu.add_command(label="删除", command=self._delete_element, accelerator="Del")
        
        # 视图菜单
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="视图", menu=view_menu)
        view_menu.add_command(label="放大", command=self._zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="缩小", command=self._zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="适应窗口", command=self._fit_to_window, accelerator="Ctrl+F")
        view_menu.add_command(label="实际大小", command=self._actual_size, accelerator="Ctrl+0")
        view_menu.add_separator()
        view_menu.add_checkbutton(label="显示网格", command=self._toggle_grid)
        view_menu.add_checkbutton(label="显示标尺", command=self._toggle_rulers)
        view_menu.add_checkbutton(label="显示小地图", command=self._toggle_minimap)
        view_menu.add_checkbutton(label="显示控制台", command=self._toggle_console)
        
        # 建模菜单
        model_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="建模", menu=model_menu)
        model_menu.add_command(label="验证模型", command=self._validate_model, accelerator="F5")
        model_menu.add_command(label="生成代码", command=self._generate_code, accelerator="F6")
        model_menu.add_command(label="预览模型", command=self._preview_model, accelerator="F7")
        model_menu.add_separator()
        model_menu.add_command(label="应用模板", command=self._apply_template)
        model_menu.add_command(label="保存为模板", command=self._save_as_template)
        model_menu.add_separator()
        model_menu.add_command(label="模型统计", command=self._show_model_stats)
        model_menu.add_command(label="依赖分析", command=self._analyze_dependencies)
        
        # 协作菜单
        collaboration_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="协作", menu=collaboration_menu)
        collaboration_menu.add_checkbutton(label="协作模式", command=self._toggle_collaboration)
        collaboration_menu.add_command(label="邀请协作者", command=self._invite_collaborator)
        collaboration_menu.add_command(label="查看协作者", command=self._view_collaborators)
        collaboration_menu.add_separator()
        collaboration_menu.add_command(label="同步更改", command=self._sync_changes)
        collaboration_menu.add_command(label="解决冲突", command=self._resolve_conflicts)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="性能分析", command=self._performance_analysis)
        tools_menu.add_command(label="代码质量检查", command=self._code_quality_check)
        tools_menu.add_command(label="安全扫描", command=self._security_scan)
        tools_menu.add_separator()
        tools_menu.add_command(label="批量操作", command=self._batch_operations)
        tools_menu.add_command(label="自动化脚本", command=self._automation_scripts)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="用户手册", command=self._show_manual)
        help_menu.add_command(label="快捷键", command=self._show_shortcuts)
        help_menu.add_command(label="示例模型", command=self._show_examples)
        help_menu.add_separator()
        help_menu.add_command(label="检查更新", command=self._check_updates)
        help_menu.add_command(label="关于", command=self._show_about)
        
    def _create_toolbar(self):
        """创建工具栏"""
        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(fill=tk.X, padx=5, pady=2)
        
        # 新建按钮
        ttk.Button(self.toolbar, text="新建", command=self._new_model).pack(side=tk.LEFT, padx=2)
        
        # 打开按钮
        ttk.Button(self.toolbar, text="打开", command=self._open_model).pack(side=tk.LEFT, padx=2)
        
        # 保存按钮
        ttk.Button(self.toolbar, text="保存", command=self._save_model).pack(side=tk.LEFT, padx=2)
        
        # 分隔符
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # 验证按钮
        ttk.Button(self.toolbar, text="验证", command=self._validate_model).pack(side=tk.LEFT, padx=2)
        
        # 生成代码按钮
        ttk.Button(self.toolbar, text="生成代码", command=self._generate_code).pack(side=tk.LEFT, padx=2)
        
        # 预览按钮
        ttk.Button(self.toolbar, text="预览", command=self._preview_model).pack(side=tk.LEFT, padx=2)
        
    def _create_sidebar(self, parent):
        """创建侧边栏"""
        # 左侧边栏框架
        left_frame = ttk.Frame(parent)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # 模型类型选择
        model_frame = ttk.LabelFrame(left_frame, text="模型类型")
        model_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.model_type_var = tk.StringVar(value="uml_class")
        model_types = [
            ("UML类图", "uml_class"),
            ("UML时序图", "uml_sequence"),
            ("UML活动图", "uml_activity"),
            ("BPMN", "bpmn"),
            ("Petri网", "petri_net"),
            ("状态机", "state_machine"),
            ("数据流图", "data_flow"),
            ("架构图", "architecture")
        ]
        
        for text, value in model_types:
            ttk.Radiobutton(model_frame, text=text, variable=self.model_type_var, 
                          value=value, command=self._on_model_type_change).pack(anchor=tk.W)
        
        # 元素工具箱
        elements_frame = ttk.LabelFrame(left_frame, text="元素工具箱")
        elements_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建元素按钮
        element_buttons = [
            ("类", "class"),
            ("接口", "interface"),
            ("方法", "method"),
            ("属性", "attribute"),
            ("关系", "relationship"),
            ("任务", "task"),
            ("网关", "gateway"),
            ("事件", "event"),
            ("库所", "place"),
            ("变迁", "transition"),
            ("状态", "state"),
            ("初始状态", "initial"),
            ("最终状态", "final")
        ]
        
        for text, element_type in element_buttons:
            btn = ttk.Button(elements_frame, text=text, 
                           command=lambda t=element_type: self._add_element(t))
            btn.pack(fill=tk.X, pady=1)
        
        # 模板选择
        template_frame = ttk.LabelFrame(left_frame, text="模板")
        template_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.template_var = tk.StringVar()
        template_combo = ttk.Combobox(template_frame, textvariable=self.template_var)
        template_combo.pack(fill=tk.X, pady=2)
        template_combo.bind("<<ComboboxSelected>>", self._on_template_change)
        
        ttk.Button(template_frame, text="应用模板", 
                  command=self._apply_template).pack(fill=tk.X, pady=2)
        
    def _create_canvas_area(self, parent):
        """创建画布区域"""
        # 画布框架
        canvas_frame = ttk.Frame(parent)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 画布工具栏
        canvas_toolbar = ttk.Frame(canvas_frame)
        canvas_toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(canvas_toolbar, text="选择", command=self._select_mode).pack(side=tk.LEFT, padx=2)
        ttk.Button(canvas_toolbar, text="连接", command=self._connect_mode).pack(side=tk.LEFT, padx=2)
        ttk.Button(canvas_toolbar, text="移动", command=self._move_mode).pack(side=tk.LEFT, padx=2)
        
        # 缩放控制
        ttk.Button(canvas_toolbar, text="+", command=self._zoom_in).pack(side=tk.RIGHT, padx=2)
        ttk.Button(canvas_toolbar, text="-", command=self._zoom_out).pack(side=tk.RIGHT, padx=2)
        ttk.Button(canvas_toolbar, text="适应", command=self._fit_to_window).pack(side=tk.RIGHT, padx=2)
        
        # 画布
        self.canvas = tk.Canvas(canvas_frame, bg="white", relief=tk.SUNKEN, bd=2)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 滚动条
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def _create_properties_panel(self, parent):
        """创建属性面板"""
        # 右侧边栏框架
        right_frame = ttk.Frame(parent)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        # 属性面板
        properties_frame = ttk.LabelFrame(right_frame, text="属性")
        properties_frame.pack(fill=tk.BOTH, expand=True)
        
        # 属性列表
        self.properties_tree = ttk.Treeview(properties_frame, columns=("value",), show="tree headings")
        self.properties_tree.heading("#0", text="属性")
        self.properties_tree.heading("value", text="值")
        self.properties_tree.pack(fill=tk.BOTH, expand=True)
        
        # 属性编辑区域
        edit_frame = ttk.Frame(properties_frame)
        edit_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(edit_frame, text="名称:").pack(anchor=tk.W)
        self.name_entry = ttk.Entry(edit_frame)
        self.name_entry.pack(fill=tk.X, pady=2)
        
        ttk.Label(edit_frame, text="类型:").pack(anchor=tk.W)
        self.type_entry = ttk.Entry(edit_frame)
        self.type_entry.pack(fill=tk.X, pady=2)
        
        ttk.Button(edit_frame, text="应用", command=self._apply_properties).pack(fill=tk.X, pady=2)
        
        # 模型信息
        info_frame = ttk.LabelFrame(right_frame, text="模型信息")
        info_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.info_text = tk.Text(info_frame, height=8, width=30)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
    def _create_console_panel(self, parent):
        """创建控制台面板"""
        self.console_panel = ttk.Frame(parent)
        self.console_panel.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
        
        self.console_text = tk.Text(self.console_panel, height=10, width=80)
        self.console_text.pack(fill=tk.BOTH, expand=False)
        
        self.console_text.config(state=tk.DISABLED)
    
    def _create_minimap(self, parent):
        """创建小地图"""
        self.minimap = ttk.Frame(parent)
        self.minimap.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0), expand=False)
        
        self.minimap_canvas = tk.Canvas(self.minimap, bg="lightgray", relief=tk.SUNKEN, bd=1)
        self.minimap_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.minimap_scrollbar = ttk.Scrollbar(self.minimap, orient=tk.VERTICAL, command=self.minimap_canvas.yview)
        self.minimap_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.minimap_canvas.configure(yscrollcommand=self.minimap_scrollbar.set)
    
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
        # 画布事件
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_canvas_release)
        self.canvas.bind("<Double-Button-1>", self._on_canvas_double_click)
        
        # 属性面板事件
        self.properties_tree.bind("<<TreeviewSelect>>", self._on_property_select)
        
    def _start_background_tasks(self):
        """启动后台任务"""
        # 启动协作模式监听
        if self.collaboration_mode:
            self._start_collaboration_listener()
        
        # 启动性能分析器
        self._start_performance_analyzer()
        
        # 启动智能提示引擎
        self._start_suggestion_engine()
        
    def _new_model(self):
        """新建模型"""
        try:
            model_type = ModelType(self.model_type_var.get())
            model_name = f"新模型_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            if self.modeling_tool:
                self.current_model = self.modeling_tool.create_model(model_name, model_type)
            else:
                # 模拟模式
                self.current_model = {
                    "id": f"model_{int(datetime.now().timestamp())}",
                    "name": model_name,
                    "type": model_type.value,
                    "elements": [],
                    "relationships": []
                }
            
            self._clear_canvas()
            self._update_info_panel()
            self._update_status("新建模型成功")
            
        except Exception as e:
            messagebox.showerror("错误", f"新建模型失败: {e}")
    
    def _open_model(self):
        """打开模型"""
        file_path = filedialog.askopenfilename(
            title="打开模型",
            filetypes=[("JSON文件", "*.json"), ("YAML文件", "*.yaml"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    if file_path.endswith('.json'):
                        data = json.load(f)
                    else:
                        data = yaml.safe_load(f)
                
                self.current_model = data
                self._load_model_to_canvas()
                self._update_info_panel()
                self._update_status(f"打开模型: {file_path}")
                
            except Exception as e:
                messagebox.showerror("错误", f"打开模型失败: {e}")
    
    def _save_model(self):
        """保存模型"""
        if not self.current_model:
            messagebox.showwarning("警告", "没有可保存的模型")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存模型",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("YAML文件", "*.yaml")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    if file_path.endswith('.json'):
                        json.dump(self.current_model, f, indent=2, ensure_ascii=False)
                    else:
                        yaml.dump(self.current_model, f, default_flow_style=False, allow_unicode=True)
                
                self._update_status(f"保存模型: {file_path}")
                
            except Exception as e:
                messagebox.showerror("错误", f"保存模型失败: {e}")
    
    def _save_as_model(self):
        """另存为模型"""
        if not self.current_model:
            messagebox.showwarning("警告", "没有可保存的模型")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="另存为模型",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("YAML文件", "*.yaml")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    if file_path.endswith('.json'):
                        json.dump(self.current_model, f, indent=2, ensure_ascii=False)
                    else:
                        yaml.dump(self.current_model, f, default_flow_style=False, allow_unicode=True)
                
                self._update_status(f"另存为模型: {file_path}")
                
            except Exception as e:
                messagebox.showerror("错误", f"另存为模型失败: {e}")
    
    def _import_model(self):
        """导入模型"""
        file_path = filedialog.askopenfilename(
            title="导入模型",
            filetypes=[("JSON文件", "*.json"), ("YAML文件", "*.yaml"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    if file_path.endswith('.json'):
                        data = json.load(f)
                    else:
                        data = yaml.safe_load(f)
                
                self.current_model = data
                self._load_model_to_canvas()
                self._update_info_panel()
                self._update_status(f"导入模型: {file_path}")
                
            except Exception as e:
                messagebox.showerror("错误", f"导入模型失败: {e}")
    
    def _export_model(self):
        """导出模型"""
        if not self.current_model:
            messagebox.showwarning("警告", "没有可导出的模型")
            return
        
        export_format = messagebox.askyesnocancel("导出格式", "选择导出格式:\n是 - JSON\n否 - YAML\n取消")
        
        if export_format is not None:
            try:
                if self.modeling_tool:
                    success = self.modeling_tool.export_model(
                        self.current_model["id"], 
                        "json" if export_format else "yaml"
                    )
                    if success:
                        self._update_status("导出模型成功")
                    else:
                        messagebox.showerror("错误", "导出模型失败")
                else:
                    # 模拟导出
                    self._update_status("模拟导出模型")
                    
            except Exception as e:
                messagebox.showerror("错误", f"导出模型失败: {e}")
    
    def _validate_model(self):
        """验证模型"""
        if not self.current_model:
            messagebox.showwarning("警告", "没有可验证的模型")
            return
        
        try:
            if self.modeling_tool:
                result = self.modeling_tool.validate_model(self.current_model["id"])
            else:
                # 模拟验证
                result = {"valid": True, "warnings": ["模拟验证模式"]}
            
            if result["valid"]:
                messagebox.showinfo("验证结果", "模型验证通过！")
            else:
                messagebox.showerror("验证结果", f"模型验证失败:\n{result.get('errors', [])}")
            
            self._update_status("模型验证完成")
            
        except Exception as e:
            messagebox.showerror("错误", f"验证模型失败: {e}")
    
    def _generate_code(self):
        """生成代码"""
        if not self.current_model:
            messagebox.showwarning("警告", "没有可生成代码的模型")
            return
        
        # 选择编程语言
        language = tk.simpledialog.askstring("选择语言", "请输入编程语言 (python/java/typescript/rust):")
        if not language:
            return
        
        try:
            if self.modeling_tool:
                result = self.modeling_tool.generate_code(self.current_model["id"], language)
            else:
                # 模拟代码生成
                result = {"success": True, "files": ["模拟生成的文件"], "language": language}
            
            if result["success"]:
                messagebox.showinfo("代码生成", f"代码生成成功！\n语言: {result['language']}\n文件: {result['files']}")
            else:
                messagebox.showerror("代码生成", f"代码生成失败: {result.get('error', '未知错误')}")
            
            self._update_status("代码生成完成")
            
        except Exception as e:
            messagebox.showerror("错误", f"生成代码失败: {e}")
    
    def _preview_model(self):
        """预览模型"""
        if not self.current_model:
            messagebox.showwarning("警告", "没有可预览的模型")
            return
        
        # 创建预览窗口
        preview_window = tk.Toplevel(self.root)
        preview_window.title("模型预览")
        preview_window.geometry("800x600")
        
        # 预览文本
        preview_text = tk.Text(preview_window, wrap=tk.WORD)
        preview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 显示模型信息
        preview_text.insert(tk.END, f"模型名称: {self.current_model.get('name', 'N/A')}\n")
        preview_text.insert(tk.END, f"模型类型: {self.current_model.get('type', 'N/A')}\n")
        preview_text.insert(tk.END, f"元素数量: {len(self.current_model.get('elements', []))}\n")
        preview_text.insert(tk.END, f"关系数量: {len(self.current_model.get('relationships', []))}\n\n")
        
        # 显示元素
        preview_text.insert(tk.END, "元素列表:\n")
        for element in self.current_model.get('elements', []):
            preview_text.insert(tk.END, f"- {element.get('name', 'N/A')} ({element.get('type', 'N/A')})\n")
        
        # 显示关系
        preview_text.insert(tk.END, "\n关系列表:\n")
        for rel in self.current_model.get('relationships', []):
            preview_text.insert(tk.END, f"- {rel.get('type', 'N/A')}: {rel.get('source_id', 'N/A')} -> {rel.get('target_id', 'N/A')}\n")
        
        preview_text.config(state=tk.DISABLED)
    
    def _add_element(self, element_type):
        """添加元素"""
        if not self.current_model:
            messagebox.showwarning("警告", "请先创建模型")
            return
        
        # 创建元素
        element_id = f"{element_type}_{int(datetime.now().timestamp())}"
        element_name = f"新{element_type}"
        
        element = {
            "id": element_id,
            "name": element_name,
            "type": element_type,
            "properties": {},
            "position": [100, 100],
            "size": [120, 80]
        }
        
        # 添加到模型
        if "elements" not in self.current_model:
            self.current_model["elements"] = []
        self.current_model["elements"].append(element)
        
        # 添加到画布
        self._draw_element(element)
        self._update_info_panel()
        
    def _draw_element(self, element):
        """在画布上绘制元素"""
        x, y = element["position"]
        width, height = element["size"]
        
        # 根据元素类型绘制不同的图形
        if element["type"] in ["class", "interface"]:
            # 绘制矩形
            rect_id = self.canvas.create_rectangle(x, y, x + width, y + height, 
                                                 fill="lightblue", outline="black")
            text_id = self.canvas.create_text(x + width/2, y + height/2, 
                                            text=element["name"], anchor=tk.CENTER)
            
        elif element["type"] in ["state", "initial", "final"]:
            # 绘制圆形
            if element["type"] == "initial":
                circle_id = self.canvas.create_oval(x, y, x + width, y + height, 
                                                  fill="green", outline="black")
            elif element["type"] == "final":
                circle_id = self.canvas.create_oval(x, y, x + width, y + height, 
                                                  fill="red", outline="black")
            else:
                circle_id = self.canvas.create_oval(x, y, x + width, y + height, 
                                                  fill="yellow", outline="black")
            text_id = self.canvas.create_text(x + width/2, y + height/2, 
                                            text=element["name"], anchor=tk.CENTER)
            
        else:
            # 默认矩形
            rect_id = self.canvas.create_rectangle(x, y, x + width, y + height, 
                                                 fill="lightgray", outline="black")
            text_id = self.canvas.create_text(x + width/2, y + height/2, 
                                            text=element["name"], anchor=tk.CENTER)
        
        # 存储画布对象ID
        element["canvas_ids"] = [rect_id, text_id]
        
    def _clear_canvas(self):
        """清空画布"""
        self.canvas.delete("all")
    
    def _load_model_to_canvas(self):
        """将模型加载到画布"""
        self._clear_canvas()
        
        if not self.current_model:
            return
        
        # 绘制元素
        for element in self.current_model.get("elements", []):
            self._draw_element(element)
        
        # 绘制关系
        for relationship in self.current_model.get("relationships", []):
            self._draw_relationship(relationship)
    
    def _draw_relationship(self, relationship):
        """绘制关系"""
        # 查找源和目标元素
        source_element = None
        target_element = None
        
        for element in self.current_model.get("elements", []):
            if element["id"] == relationship["source_id"]:
                source_element = element
            elif element["id"] == relationship["target_id"]:
                target_element = element
        
        if source_element and target_element:
            # 计算连接点
            sx, sy = source_element["position"]
            sw, sh = source_element["size"]
            tx, ty = target_element["position"]
            tw, th = target_element["size"]
            
            # 绘制箭头线
            line_id = self.canvas.create_line(sx + sw/2, sy + sh/2, 
                                            tx + tw/2, ty + th/2, 
                                            arrow=tk.LAST, fill="black")
            
            # 存储画布对象ID
            relationship["canvas_id"] = line_id
    
    def _update_info_panel(self):
        """更新信息面板"""
        if not self.current_model:
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, "没有加载的模型")
            self.info_text.config(state=tk.DISABLED)
            return
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        info = f"""模型信息:
名称: {self.current_model.get('name', 'N/A')}
类型: {self.current_model.get('type', 'N/A')}
元素数量: {len(self.current_model.get('elements', []))}
关系数量: {len(self.current_model.get('relationships', []))}
创建时间: {self.current_model.get('created_at', 'N/A')}
更新时间: {self.current_model.get('updated_at', 'N/A')}
"""
        self.info_text.insert(tk.END, info)
        self.info_text.config(state=tk.DISABLED)
    
    def _update_status(self, message):
        """更新状态栏"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    # 事件处理方法
    def _on_model_type_change(self):
        """模型类型改变事件"""
        pass
    
    def _on_template_change(self, event):
        """模板改变事件"""
        pass
    
    def _apply_template(self):
        """应用模板"""
        template_name = self.template_var.get()
        if template_name and self.modeling_tool:
            try:
                model_type = ModelType(self.model_type_var.get())
                model_name = f"模板模型_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.current_model = self.modeling_tool.create_model(model_name, model_type, template_name)
                self._load_model_to_canvas()
                self._update_info_panel()
                self._update_status(f"应用模板: {template_name}")
            except Exception as e:
                messagebox.showerror("错误", f"应用模板失败: {e}")
    
    def _on_canvas_click(self, event):
        """画布点击事件"""
        # 查找点击的元素
        clicked_items = self.canvas.find_closest(event.x, event.y)
        if clicked_items:
            # 查找对应的元素
            for element in self.current_model.get("elements", []):
                if "canvas_ids" in element:
                    if clicked_items[0] in element["canvas_ids"]:
                        self.selected_element = element
                        self._update_properties_panel()
                        break
    
    def _on_canvas_drag(self, event):
        """画布拖拽事件"""
        pass
    
    def _on_canvas_release(self, event):
        """画布释放事件"""
        pass
    
    def _on_canvas_double_click(self, event):
        """画布双击事件"""
        pass
    
    def _on_property_select(self, event):
        """属性选择事件"""
        pass
    
    def _apply_properties(self):
        """应用属性"""
        if self.selected_element:
            name = self.name_entry.get()
            element_type = self.type_entry.get()
            
            if name:
                self.selected_element["name"] = name
            if element_type:
                self.selected_element["type"] = element_type
            
            # 更新画布显示
            self._load_model_to_canvas()
            self._update_status("属性已更新")
    
    # 工具栏方法
    def _select_mode(self):
        """选择模式"""
        self._update_status("选择模式")
    
    def _connect_mode(self):
        """连接模式"""
        self._update_status("连接模式")
    
    def _move_mode(self):
        """移动模式"""
        self._update_status("移动模式")
    
    def _zoom_in(self):
        """放大"""
        self.canvas.scale("all", 0, 0, 1.2, 1.2)
        self._update_status("放大")
    
    def _zoom_out(self):
        """缩小"""
        self.canvas.scale("all", 0, 0, 0.8, 0.8)
        self._update_status("缩小")
    
    def _fit_to_window(self):
        """适应窗口"""
        self._update_status("适应窗口")
    
    def _actual_size(self):
        """实际大小"""
        self.canvas.scale("all", 0, 0, 1.0, 1.0)
        self._update_status("实际大小")
    
    def _toggle_grid(self):
        """切换网格显示"""
        self._update_status("切换网格显示")
    
    def _toggle_rulers(self):
        """切换标尺显示"""
        self._update_status("切换标尺显示")
    
    def _toggle_minimap(self):
        """切换小地图显示"""
        self._update_status("切换小地图显示")
    
    def _toggle_console(self):
        """切换控制台显示"""
        self._update_status("切换控制台显示")
    
    # 编辑方法
    def _undo(self):
        """撤销"""
        self._update_status("撤销")
    
    def _redo(self):
        """重做"""
        self._update_status("重做")
    
    def _cut(self):
        """剪切"""
        self._update_status("剪切")
    
    def _copy(self):
        """复制"""
        self._update_status("复制")
    
    def _paste(self):
        """粘贴"""
        self._update_status("粘贴")
    
    def _select_all(self):
        """全选"""
        self._update_status("全选")
    
    def _delete_element(self):
        """删除元素"""
        if self.selected_element:
            # 从模型中删除
            self.current_model["elements"] = [e for e in self.current_model["elements"] 
                                            if e["id"] != self.selected_element["id"]]
            
            # 从画布删除
            if "canvas_ids" in self.selected_element:
                for canvas_id in self.selected_element["canvas_ids"]:
                    self.canvas.delete(canvas_id)
            
            self.selected_element = None
            self._update_info_panel()
            self._update_status("元素已删除")
    
    # 版本管理方法
    def _version_management(self):
        """版本管理"""
        self._update_status("版本管理")
    
    def _save_as_template(self):
        """保存为模板"""
        self._update_status("保存为模板")
    
    def _show_model_stats(self):
        """显示模型统计"""
        self._update_status("模型统计")
    
    def _analyze_dependencies(self):
        """分析依赖"""
        self._update_status("依赖分析")
    
    # 协作方法
    def _toggle_collaboration(self):
        """切换协作模式"""
        self.collaboration_mode = not self.collaboration_mode
        self._update_status(f"协作模式 {'开启' if self.collaboration_mode else '关闭'}")
    
    def _invite_collaborator(self):
        """邀请协作者"""
        collaborator_name = tk.simpledialog.askstring("邀请协作者", "请输入协作者名称:")
        if collaborator_name:
            self.collaborators.append(collaborator_name)
            self._update_status(f"邀请协作者: {collaborator_name}")
    
    def _view_collaborators(self):
        """查看协作者"""
        if not self.collaborators:
            messagebox.showinfo("协作者", "当前没有协作者")
            return
        
        collaborator_list = "\n".join(self.collaborators)
        messagebox.showinfo("协作者列表", f"当前协作者:\n{collaborator_list}")
    
    def _sync_changes(self):
        """同步更改"""
        self._update_status("同步更改")
    
    def _resolve_conflicts(self):
        """解决冲突"""
        self._update_status("解决冲突")
    
    # 性能分析方法
    def _performance_analysis(self):
        """性能分析"""
        self._update_status("性能分析")
    
    def _code_quality_check(self):
        """代码质量检查"""
        self._update_status("代码质量检查")
    
    def _security_scan(self):
        """安全扫描"""
        self._update_status("安全扫描")
    
    # 批量操作方法
    def _batch_operations(self):
        """批量操作"""
        self._update_status("批量操作")
    
    def _automation_scripts(self):
        """自动化脚本"""
        self._update_status("自动化脚本")
    
    # 智能提示方法
    def _start_suggestion_engine(self):
        """启动智能提示引擎"""
        self._update_status("智能提示引擎启动")
    
    # 帮助方法
    def _show_manual(self):
        """显示用户手册"""
        help_text = """
FormalUnified 增强版可视化建模界面用户手册:

1. 创建模型:
   - 选择模型类型
   - 点击"新建"按钮

2. 添加元素:
   - 从左侧工具箱拖拽元素到画布
   - 或点击工具箱中的元素按钮

3. 编辑元素:
   - 点击元素选中
   - 在右侧属性面板中编辑属性

4. 创建关系:
   - 使用连接工具连接元素

5. 验证模型:
   - 点击"验证"按钮检查模型

6. 生成代码:
   - 点击"生成代码"按钮

7. 保存模型:
   - 点击"保存"按钮保存为JSON或YAML格式
"""
        messagebox.showinfo("用户手册", help_text)
    
    def _show_shortcuts(self):
        """显示快捷键"""
        shortcuts_text = """
FormalUnified 增强版可视化建模界面快捷键:

Ctrl+N: 新建模型
Ctrl+O: 打开模型
Ctrl+S: 保存模型
Ctrl+Shift+S: 另存为模型
Ctrl+Z: 撤销
Ctrl+Y: 重做
Ctrl+X: 剪切
Ctrl+C: 复制
Ctrl+V: 粘贴
Ctrl+A: 全选
Del: 删除元素
F5: 验证模型
F6: 生成代码
F7: 预览模型
"""
        messagebox.showinfo("快捷键", shortcuts_text)
    
    def _show_examples(self):
        """显示示例模型"""
        self._update_status("显示示例模型")
    
    def _check_updates(self):
        """检查更新"""
        self._update_status("检查更新")
    
    def _show_about(self):
        """显示关于"""
        about_text = """
FormalUnified 增强版可视化建模界面
版本: 2.0.0

基于FormalUnified理论体系的图形化建模工具
支持多种建模语言和代码生成

作者: FormalUnified团队
日期: 2024年12月
"""
        messagebox.showinfo("关于", about_text)
    
    def run(self):
        """运行界面"""
        self.root.mainloop()

class SuggestionEngine:
    """智能提示引擎"""
    
    def __init__(self):
        self.suggestions = {
            'element_types': ['类', '接口', '组件', '服务', '数据库', '队列'],
            'relationships': ['继承', '实现', '依赖', '关联', '组合', '聚合'],
            'patterns': ['MVC', 'MVVM', 'Repository', 'Factory', 'Observer', 'Strategy'],
            'languages': ['Python', 'Java', 'TypeScript', 'Rust', 'Go', 'C#']
        }
        self.context_history = []
    
    def get_suggestions(self, context, partial_input):
        """根据上下文获取建议"""
        suggestions = []
        
        if 'element' in context:
            suggestions.extend(self.suggestions['element_types'])
        elif 'relationship' in context:
            suggestions.extend(self.suggestions['relationships'])
        elif 'pattern' in context:
            suggestions.extend(self.suggestions['patterns'])
        elif 'language' in context:
            suggestions.extend(self.suggestions['languages'])
        
        # 过滤匹配的部分输入
        if partial_input:
            suggestions = [s for s in suggestions if partial_input.lower() in s.lower()]
        
        return suggestions[:5]  # 返回前5个建议

class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self):
        self.metrics = {
            'render_time': [],
            'memory_usage': [],
            'cpu_usage': [],
            'response_time': []
        }
        self.start_time = None
    
    def start_measurement(self):
        """开始测量"""
        self.start_time = datetime.now()
    
    def end_measurement(self, metric_type):
        """结束测量"""
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            self.metrics[metric_type].append(duration)
            self.start_time = None
    
    def get_average_metrics(self):
        """获取平均指标"""
        return {
            metric: sum(values) / len(values) if values else 0
            for metric, values in self.metrics.items()
        }
    
    def generate_report(self):
        """生成性能报告"""
        avg_metrics = self.get_average_metrics()
        report = "性能分析报告:\n"
        for metric, value in avg_metrics.items():
            report += f"{metric}: {value:.3f}s\n"
        return report

class CollaborationListener:
    """协作监听器"""
    
    def __init__(self, interface):
        self.interface = interface
        self.running = False
        self.changes_buffer = []
    
    def start(self):
        """启动监听"""
        self.running = True
        self._listen_thread = threading.Thread(target=self._listen_loop)
        self._listen_thread.daemon = True
        self._listen_thread.start()
    
    def stop(self):
        """停止监听"""
        self.running = False
    
    def _listen_loop(self):
        """监听循环"""
        while self.running:
            try:
                # 模拟接收协作更改
                if self.interface.changes_queue.qsize() > 0:
                    change = self.interface.changes_queue.get_nowait()
                    self._process_change(change)
                
                time.sleep(0.1)  # 100ms间隔
            except Exception as e:
                logger.error(f"协作监听错误: {e}")
    
    def _process_change(self, change):
        """处理更改"""
        self.changes_buffer.append(change)
        self.interface._update_status(f"收到协作更改: {change.get('type', 'unknown')}")

def main():
    """主函数"""
    print("🚀 启动可视化建模界面")
    
    try:
        app = EnhancedVisualModelingInterface()
        app.run()
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        logger.error(f"界面启动失败: {e}")

if __name__ == "__main__":
    main() 