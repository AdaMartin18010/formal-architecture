#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标准化推进工具
Standardization Promoter

推进FormalUnified项目的标准化工作，包括标准制定、规范推广、最佳实践等
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import logging
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StandardizationPromoter:
    """标准化推进工具"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FormalUnified 标准化推进工具")
        self.root.geometry("1200x800")
        
        # 标准化数据
        self.standards_data = {
            "standards": [],
            "guidelines": [],
            "best_practices": [],
            "compliance_checks": []
        }
        
        self._setup_ui()
        self._load_sample_data()
        
    def _setup_ui(self):
        """设置用户界面"""
        # 创建主菜单
        self._create_menu()
        
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建选项卡
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 标准管理
        self._create_standards_tab(notebook)
        
        # 规范指南
        self._create_guidelines_tab(notebook)
        
        # 最佳实践
        self._create_best_practices_tab(notebook)
        
        # 合规检查
        self._create_compliance_tab(notebook)
        
        # 推广计划
        self._create_promotion_tab(notebook)
        
    def _create_menu(self):
        """创建主菜单"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 标准菜单
        standard_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="标准", menu=standard_menu)
        standard_menu.add_command(label="创建标准", command=self._create_standard)
        standard_menu.add_command(label="制定规范", command=self._create_guideline)
        standard_menu.add_command(label="添加最佳实践", command=self._add_best_practice)
        standard_menu.add_separator()
        standard_menu.add_command(label="导出标准文档", command=self._export_standards)
        
        # 推广菜单
        promotion_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="推广", menu=promotion_menu)
        promotion_menu.add_command(label="制定推广计划", command=self._create_promotion_plan)
        promotion_menu.add_command(label="合规检查", command=self._run_compliance_check)
        promotion_menu.add_command(label="培训计划", command=self._create_training_plan)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用指南", command=self._show_guide)
        help_menu.add_command(label="关于", command=self._show_about)
        
    def _create_standards_tab(self, notebook):
        """创建标准管理选项卡"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="标准管理")
        
        # 创建左右分栏
        left_frame = ttk.Frame(frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        right_frame = ttk.Frame(frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧：标准列表
        ttk.Label(left_frame, text="标准列表", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        # 标准树形视图
        self.standards_tree = ttk.Treeview(left_frame, columns=("版本", "状态", "制定者"), show="headings")
        self.standards_tree.heading("版本", text="版本")
        self.standards_tree.heading("状态", text="状态")
        self.standards_tree.heading("制定者", text="制定者")
        self.standards_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 右侧：标准详情
        ttk.Label(right_frame, text="标准详情", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        detail_frame = ttk.LabelFrame(right_frame, text="详细信息")
        detail_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.standard_detail = tk.Text(detail_frame, height=15, width=40)
        self.standard_detail.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def _create_guidelines_tab(self, notebook):
        """创建规范指南选项卡"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="规范指南")
        
        # 规范列表
        ttk.Label(frame, text="规范指南", font=("Arial", 12, "bold")).pack(anchor=tk.W, padx=10, pady=5)
        
        # 规范树形视图
        self.guidelines_tree = ttk.Treeview(frame, columns=("类别", "适用场景", "制定时间"), show="headings")
        self.guidelines_tree.heading("类别", text="类别")
        self.guidelines_tree.heading("适用场景", text="适用场景")
        self.guidelines_tree.heading("制定时间", text="制定时间")
        self.guidelines_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
    def _create_best_practices_tab(self, notebook):
        """创建最佳实践选项卡"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="最佳实践")
        
        # 最佳实践列表
        ttk.Label(frame, text="最佳实践", font=("Arial", 12, "bold")).pack(anchor=tk.W, padx=10, pady=5)
        
        # 最佳实践树形视图
        self.practices_tree = ttk.Treeview(frame, columns=("领域", "实践类型", "推荐度"), show="headings")
        self.practices_tree.heading("领域", text="领域")
        self.practices_tree.heading("实践类型", text="实践类型")
        self.practices_tree.heading("推荐度", text="推荐度")
        self.practices_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
    def _create_compliance_tab(self, notebook):
        """创建合规检查选项卡"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="合规检查")
        
        # 合规检查列表
        ttk.Label(frame, text="合规检查", font=("Arial", 12, "bold")).pack(anchor=tk.W, padx=10, pady=5)
        
        # 合规检查树形视图
        self.compliance_tree = ttk.Treeview(frame, columns=("检查项", "标准", "状态"), show="headings")
        self.compliance_tree.heading("检查项", text="检查项")
        self.compliance_tree.heading("标准", text="标准")
        self.compliance_tree.heading("状态", text="状态")
        self.compliance_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 检查按钮
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="运行合规检查", 
                  command=self._run_compliance_check).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="生成合规报告", 
                  command=self._generate_compliance_report).pack(side=tk.LEFT, padx=5)
        
    def _create_promotion_tab(self, notebook):
        """创建推广计划选项卡"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="推广计划")
        
        # 推广计划列表
        ttk.Label(frame, text="推广计划", font=("Arial", 12, "bold")).pack(anchor=tk.W, padx=10, pady=5)
        
        # 推广计划树形视图
        self.promotion_tree = ttk.Treeview(frame, columns=("计划名称", "目标", "进度"), show="headings")
        self.promotion_tree.heading("计划名称", text="计划名称")
        self.promotion_tree.heading("目标", text="目标")
        self.promotion_tree.heading("进度", text="进度")
        self.promotion_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 统计信息
        stats_frame = ttk.LabelFrame(frame, text="推广统计")
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(stats_grid, text="已制定标准:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.standards_count_label = ttk.Label(stats_grid, text="0")
        self.standards_count_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(stats_grid, text="规范指南:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.guidelines_count_label = ttk.Label(stats_grid, text="0")
        self.guidelines_count_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(stats_grid, text="最佳实践:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.practices_count_label = ttk.Label(stats_grid, text="0")
        self.practices_count_label.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(stats_grid, text="推广计划:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.promotion_count_label = ttk.Label(stats_grid, text="0")
        self.promotion_count_label.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        
    def _load_sample_data(self):
        """加载示例数据"""
        # 示例标准数据
        sample_standards = [
            ("FormalUnified核心标准", "v1.0", "已发布", "标准化委员会"),
            ("理论建模标准", "v1.2", "已发布", "理论组"),
            ("代码生成标准", "v1.1", "已发布", "工具组"),
            ("验证测试标准", "v1.0", "制定中", "测试组"),
            ("文档规范标准", "v1.0", "已发布", "文档组")
        ]
        
        for name, version, status, author in sample_standards:
            self.standards_tree.insert("", tk.END, values=(version, status, author))
        
        # 示例规范数据
        sample_guidelines = [
            ("理论建模规范", "理论体系构建", "2024-01-15"),
            ("代码生成规范", "多语言开发", "2024-02-20"),
            ("验证测试规范", "质量保证", "2024-03-10"),
            ("文档编写规范", "文档维护", "2024-04-05"),
            ("工具开发规范", "工具链开发", "2024-05-12")
        ]
        
        for name, category, create_date in sample_guidelines:
            self.guidelines_tree.insert("", tk.END, values=(category, name, create_date))
        
        # 示例最佳实践数据
        sample_practices = [
            ("理论建模", "分层建模", "强烈推荐"),
            ("代码生成", "模板驱动", "推荐"),
            ("验证测试", "自动化测试", "强烈推荐"),
            ("文档管理", "版本控制", "推荐"),
            ("工具集成", "插件化架构", "推荐")
        ]
        
        for domain, practice_type, recommendation in sample_practices:
            self.practices_tree.insert("", tk.END, values=(domain, practice_type, recommendation))
        
        # 示例合规检查数据
        sample_compliance = [
            ("理论一致性检查", "FormalUnified核心标准", "通过"),
            ("代码质量检查", "代码生成标准", "通过"),
            ("文档完整性检查", "文档规范标准", "通过"),
            ("工具集成检查", "工具开发规范", "进行中"),
            ("性能基准检查", "性能测试标准", "待检查")
        ]
        
        for check_item, standard, status in sample_compliance:
            self.compliance_tree.insert("", tk.END, values=(check_item, standard, status))
        
        # 示例推广计划数据
        sample_promotions = [
            ("标准推广计划", "提高标准采用率", "80%"),
            ("培训推广计划", "提升用户技能", "60%"),
            ("工具推广计划", "扩大工具使用", "70%"),
            ("社区推广计划", "扩大社区影响", "50%")
        ]
        
        for plan_name, target, progress in sample_promotions:
            self.promotion_tree.insert("", tk.END, values=(plan_name, target, progress))
        
        # 更新统计信息
        self._update_statistics()
        
    def _update_statistics(self):
        """更新统计信息"""
        standards_count = len(self.standards_tree.get_children())
        guidelines_count = len(self.guidelines_tree.get_children())
        practices_count = len(self.practices_tree.get_children())
        promotion_count = len(self.promotion_tree.get_children())
        
        self.standards_count_label.config(text=str(standards_count))
        self.guidelines_count_label.config(text=str(guidelines_count))
        self.practices_count_label.config(text=str(practices_count))
        self.promotion_count_label.config(text=str(promotion_count))
        
    def _create_standard(self):
        """创建标准"""
        # 创建标准对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("创建标准")
        dialog.geometry("500x400")
        
        # 表单内容
        ttk.Label(dialog, text="标准信息", font=("Arial", 12, "bold")).pack(pady=10)
        
        form_frame = ttk.Frame(dialog)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        ttk.Label(form_frame, text="标准名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(form_frame, width=40)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text="版本:").grid(row=1, column=0, sticky=tk.W, pady=5)
        version_entry = ttk.Entry(form_frame, width=40)
        version_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text="状态:").grid(row=2, column=0, sticky=tk.W, pady=5)
        status_combo = ttk.Combobox(form_frame, values=["制定中", "已发布", "已废弃"])
        status_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text="制定者:").grid(row=3, column=0, sticky=tk.W, pady=5)
        author_entry = ttk.Entry(form_frame, width=40)
        author_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text="描述:").grid(row=4, column=0, sticky=tk.W, pady=5)
        description_text = tk.Text(form_frame, height=6, width=40)
        description_text.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def save_standard():
            name = name_entry.get()
            version = version_entry.get()
            status = status_combo.get()
            author = author_entry.get()
            description = description_text.get(1.0, tk.END).strip()
            
            if name and version and status and author:
                self.standards_tree.insert("", tk.END, values=(version, status, author))
                self._update_statistics()
                dialog.destroy()
                messagebox.showinfo("成功", f"已创建标准: {name}")
            else:
                messagebox.showwarning("警告", "请填写所有必填字段")
        
        ttk.Button(button_frame, text="保存", command=save_standard).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    def _create_guideline(self):
        """制定规范"""
        # 创建规范对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("制定规范")
        dialog.geometry("500x400")
        
        # 表单内容
        ttk.Label(dialog, text="规范信息", font=("Arial", 12, "bold")).pack(pady=10)
        
        form_frame = ttk.Frame(dialog)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        ttk.Label(form_frame, text="规范名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(form_frame, width=40)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text="类别:").grid(row=1, column=0, sticky=tk.W, pady=5)
        category_combo = ttk.Combobox(form_frame, values=["理论建模", "代码生成", "验证测试", "文档管理", "工具开发"])
        category_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text="适用场景:").grid(row=2, column=0, sticky=tk.W, pady=5)
        scenario_entry = ttk.Entry(form_frame, width=40)
        scenario_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text="内容:").grid(row=3, column=0, sticky=tk.W, pady=5)
        content_text = tk.Text(form_frame, height=8, width=40)
        content_text.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def save_guideline():
            name = name_entry.get()
            category = category_combo.get()
            scenario = scenario_entry.get()
            content = content_text.get(1.0, tk.END).strip()
            
            if name and category and scenario:
                create_date = datetime.now().strftime("%Y-%m-%d")
                self.guidelines_tree.insert("", tk.END, values=(category, scenario, create_date))
                self._update_statistics()
                dialog.destroy()
                messagebox.showinfo("成功", f"已制定规范: {name}")
            else:
                messagebox.showwarning("警告", "请填写所有必填字段")
        
        ttk.Button(button_frame, text="保存", command=save_guideline).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    def _add_best_practice(self):
        """添加最佳实践"""
        # 创建最佳实践对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("添加最佳实践")
        dialog.geometry("500x400")
        
        # 表单内容
        ttk.Label(dialog, text="最佳实践信息", font=("Arial", 12, "bold")).pack(pady=10)
        
        form_frame = ttk.Frame(dialog)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        ttk.Label(form_frame, text="实践名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(form_frame, width=40)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text="领域:").grid(row=1, column=0, sticky=tk.W, pady=5)
        domain_combo = ttk.Combobox(form_frame, values=["理论建模", "代码生成", "验证测试", "文档管理", "工具开发"])
        domain_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text="实践类型:").grid(row=2, column=0, sticky=tk.W, pady=5)
        practice_type_entry = ttk.Entry(form_frame, width=40)
        practice_type_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text="推荐度:").grid(row=3, column=0, sticky=tk.W, pady=5)
        recommendation_combo = ttk.Combobox(form_frame, values=["强烈推荐", "推荐", "可选", "不推荐"])
        recommendation_combo.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text="描述:").grid(row=4, column=0, sticky=tk.W, pady=5)
        description_text = tk.Text(form_frame, height=6, width=40)
        description_text.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def save_practice():
            name = name_entry.get()
            domain = domain_combo.get()
            practice_type = practice_type_entry.get()
            recommendation = recommendation_combo.get()
            description = description_text.get(1.0, tk.END).strip()
            
            if name and domain and practice_type and recommendation:
                self.practices_tree.insert("", tk.END, values=(domain, practice_type, recommendation))
                self._update_statistics()
                dialog.destroy()
                messagebox.showinfo("成功", f"已添加最佳实践: {name}")
            else:
                messagebox.showwarning("警告", "请填写所有必填字段")
        
        ttk.Button(button_frame, text="保存", command=save_practice).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    def _run_compliance_check(self):
        """运行合规检查"""
        messagebox.showinfo("合规检查", "正在运行合规检查...")
        
        # 模拟合规检查过程
        import time
        time.sleep(2)
        
        # 更新检查状态
        for item in self.compliance_tree.get_children():
            values = self.compliance_tree.item(item)['values']
            if values[2] == "待检查":
                self.compliance_tree.set(item, "状态", "通过")
        
        messagebox.showinfo("合规检查", "合规检查完成！")
        
    def _generate_compliance_report(self):
        """生成合规报告"""
        report = self._generate_compliance_report_content()
        
        # 创建报告窗口
        report_window = tk.Toplevel(self.root)
        report_window.title("合规报告")
        report_window.geometry("800x600")
        
        # 报告内容
        report_text = tk.Text(report_window, wrap=tk.WORD)
        report_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        report_text.insert(1.0, report)
        report_text.config(state=tk.DISABLED)
        
    def _generate_compliance_report_content(self):
        """生成合规报告内容"""
        total_checks = len(self.compliance_tree.get_children())
        passed_checks = len([item for item in self.compliance_tree.get_children() 
                           if self.compliance_tree.item(item)['values'][2] == "通过"])
        failed_checks = len([item for item in self.compliance_tree.get_children() 
                           if self.compliance_tree.item(item)['values'][2] == "失败"])
        pending_checks = total_checks - passed_checks - failed_checks
        
        report = f"""FormalUnified 合规检查报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

1. 检查概况
   - 总检查项: {total_checks}
   - 通过项: {passed_checks}
   - 失败项: {failed_checks}
   - 待检查项: {pending_checks}
   - 通过率: {passed_checks/total_checks*100:.1f}%

2. 检查详情
"""
        
        for item in self.compliance_tree.get_children():
            values = self.compliance_tree.item(item)['values']
            report += f"   - {values[0]}: {values[2]} (标准: {values[1]})\n"
        
        report += f"""
3. 建议
   - 继续推进标准化工作
   - 加强标准培训和推广
   - 定期进行合规检查
   - 及时更新和完善标准

4. 下一步计划
   - 制定更多标准规范
   - 扩大标准应用范围
   - 建立标准评估机制
   - 推进标准国际化
"""
        
        return report
        
    def _create_promotion_plan(self):
        """创建推广计划"""
        # 创建推广计划对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("创建推广计划")
        dialog.geometry("500x400")
        
        # 表单内容
        ttk.Label(dialog, text="推广计划信息", font=("Arial", 12, "bold")).pack(pady=10)
        
        form_frame = ttk.Frame(dialog)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        ttk.Label(form_frame, text="计划名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(form_frame, width=40)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text="目标:").grid(row=1, column=0, sticky=tk.W, pady=5)
        target_entry = ttk.Entry(form_frame, width=40)
        target_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text="进度:").grid(row=2, column=0, sticky=tk.W, pady=5)
        progress_entry = ttk.Entry(form_frame, width=40)
        progress_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text="计划内容:").grid(row=3, column=0, sticky=tk.W, pady=5)
        content_text = tk.Text(form_frame, height=8, width=40)
        content_text.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def save_plan():
            name = name_entry.get()
            target = target_entry.get()
            progress = progress_entry.get()
            content = content_text.get(1.0, tk.END).strip()
            
            if name and target and progress:
                self.promotion_tree.insert("", tk.END, values=(name, target, progress))
                self._update_statistics()
                dialog.destroy()
                messagebox.showinfo("成功", f"已创建推广计划: {name}")
            else:
                messagebox.showwarning("警告", "请填写所有必填字段")
        
        ttk.Button(button_frame, text="保存", command=save_plan).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    def _create_training_plan(self):
        """创建培训计划"""
        training_text = """FormalUnified 标准化培训计划

1. 培训目标
   - 提高团队标准化意识
   - 掌握标准制定方法
   - 学会标准应用实践
   - 培养标准化人才

2. 培训内容
   - 标准化基础知识
   - FormalUnified标准体系
   - 标准制定流程
   - 标准应用方法
   - 最佳实践分享

3. 培训方式
   - 线上培训课程
   - 线下研讨会
   - 实践项目指导
   - 案例分析讨论

4. 培训计划
   - 第一阶段: 基础知识培训 (2周)
   - 第二阶段: 标准制定培训 (3周)
   - 第三阶段: 实践应用培训 (4周)
   - 第四阶段: 考核认证 (1周)

5. 预期效果
   - 建立标准化团队
   - 制定完善标准体系
   - 提高项目质量
   - 扩大标准影响
"""
        messagebox.showinfo("培训计划", training_text)
        
    def _export_standards(self):
        """导出标准文档"""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            title="导出标准文档",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                standards_doc = self._generate_standards_document()
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(standards_doc)
                messagebox.showinfo("成功", f"标准文档已导出: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")
        
    def _generate_standards_document(self):
        """生成标准文档"""
        doc = f"""FormalUnified 标准文档

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

1. 标准列表
"""
        
        for item in self.standards_tree.get_children():
            values = self.standards_tree.item(item)['values']
            doc += f"   - {values[0]} (版本: {values[1]}, 状态: {values[2]}, 制定者: {values[3]})\n"
        
        doc += f"""
2. 规范指南
"""
        
        for item in self.guidelines_tree.get_children():
            values = self.guidelines_tree.item(item)['values']
            doc += f"   - {values[0]} (类别: {values[1]}, 制定时间: {values[2]})\n"
        
        doc += f"""
3. 最佳实践
"""
        
        for item in self.practices_tree.get_children():
            values = self.practices_tree.item(item)['values']
            doc += f"   - {values[0]} (领域: {values[1]}, 推荐度: {values[2]})\n"
        
        doc += f"""
4. 推广计划
"""
        
        for item in self.promotion_tree.get_children():
            values = self.promotion_tree.item(item)['values']
            doc += f"   - {values[0]} (目标: {values[1]}, 进度: {values[2]})\n"
        
        return doc
        
    def _show_guide(self):
        """显示使用指南"""
        guide_text = """FormalUnified 标准化推进工具使用指南

1. 标准管理
   - 查看标准列表和详细信息
   - 创建新的标准
   - 跟踪标准状态和版本

2. 规范指南
   - 查看规范指南列表
   - 制定新的规范
   - 按类别组织规范

3. 最佳实践
   - 查看最佳实践列表
   - 添加新的最佳实践
   - 按推荐度分类

4. 合规检查
   - 运行合规检查
   - 查看检查结果
   - 生成合规报告

5. 推广计划
   - 制定推广计划
   - 跟踪推广进度
   - 统计推广效果

6. 最佳实践
   - 定期更新标准
   - 及时进行合规检查
   - 持续推广标准应用
   - 收集用户反馈
"""
        messagebox.showinfo("使用指南", guide_text)
        
    def _show_about(self):
        """显示关于信息"""
        about_text = """FormalUnified 标准化推进工具

版本: 1.0.0
开发团队: FormalUnified Team

本工具旨在推进FormalUnified项目的标准化工作，
建立完善的标准体系，促进项目规范化发展。

主要功能:
- 标准管理
- 规范指南
- 最佳实践
- 合规检查
- 推广计划

通过本工具，可以更好地推进标准化工作，
提高项目质量和规范性。
"""
        messagebox.showinfo("关于", about_text)
        
    def run(self):
        """运行标准化推进工具"""
        self.root.mainloop()

def main():
    """主函数"""
    print("🚀 启动FormalUnified标准化推进工具")
    
    # 创建标准化推进工具
    promoter = StandardizationPromoter()
    
    # 运行工具
    promoter.run()

if __name__ == "__main__":
    main() 