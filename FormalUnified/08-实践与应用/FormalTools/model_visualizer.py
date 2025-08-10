#!/usr/bin/env python3
"""
形式化模型可视化工具 (Formal Model Visualizer)
将形式化模型转换为图形化表示，支持多种建模范式的可视化

功能特性：
1. 状态机可视化
2. Petri网可视化  
3. 统一STS可视化
4. 交互式图形界面
5. 多种输出格式
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle
import numpy as np
from typing import Dict, List, Any, Tuple
import argparse
import sys
import os

class ModelVisualizer:
    """形式化模型可视化器"""
    
    def __init__(self, figsize=(12, 8)):
        self.figsize = figsize
        self.colors = {
            'state': '#E3F2FD',
            'initial_state': '#4CAF50',
            'final_state': '#F44336',
            'transition': '#2196F3',
            'place': '#FFF3E0',
            'transition_petri': '#FF9800',
            'token': '#E91E63',
            'arc': '#757575'
        }
        
    def visualize_model(self, model_data: Dict[str, Any], 
                       output_file: str = None, show: bool = True) -> None:
        """可视化模型主入口"""
        model_type = model_data.get('model_type', 'unknown')
        
        if model_type == 'state_machine':
            self._visualize_state_machine(model_data, output_file, show)
        elif model_type == 'petri_net':
            self._visualize_petri_net(model_data, output_file, show)
        elif model_type == 'unified_sts':
            self._visualize_unified_sts(model_data, output_file, show)
        else:
            print(f"不支持的模型类型: {model_type}")
            return
    
    def _visualize_state_machine(self, model_data: Dict[str, Any], 
                                output_file: str, show: bool) -> None:
        """可视化状态机"""
        elements = model_data.get('elements', {})
        states = elements.get('states', [])
        transitions = elements.get('transitions', [])
        initial_state = elements.get('initial_state', None)
        final_states = elements.get('final_states', [])
        
        fig, ax = plt.subplots(figsize=self.figsize)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # 计算状态位置
        state_positions = self._calculate_state_positions(states)
        
        # 绘制状态
        for state in states:
            x, y = state_positions[state]
            
            # 确定状态颜色
            if state == initial_state:
                color = self.colors['initial_state']
            elif state in final_states:
                color = self.colors['final_state']
            else:
                color = self.colors['state']
            
            # 绘制状态圆圈
            circle = Circle((x, y), 0.5, facecolor=color, 
                           edgecolor='black', linewidth=2)
            ax.add_patch(circle)
            
            # 添加状态标签
            ax.text(x, y, state, ha='center', va='center', 
                   fontsize=10, fontweight='bold')
        
        # 绘制转换
        for transition in transitions:
            from_state = transition.get('from')
            to_state = transition.get('to')
            event = transition.get('event', '')
            condition = transition.get('condition', '')
            
            if from_state in state_positions and to_state in state_positions:
                x1, y1 = state_positions[from_state]
                x2, y2 = state_positions[to_state]
                
                # 计算箭头位置（从圆圈边缘开始）
                dx, dy = x2 - x1, y2 - y1
                length = np.sqrt(dx**2 + dy**2)
                if length > 0:
                    unit_dx, unit_dy = dx/length, dy/length
                    start_x = x1 + 0.5 * unit_dx
                    start_y = y1 + 0.5 * unit_dy
                    end_x = x2 - 0.5 * unit_dx
                    end_y = y2 - 0.5 * unit_dy
                    
                    # 绘制箭头
                    ax.annotate('', xy=(end_x, end_y), xytext=(start_x, start_y),
                               arrowprops=dict(arrowstyle='->', 
                                             color=self.colors['transition'],
                                             lw=2))
                    
                    # 添加事件标签
                    mid_x = (start_x + end_x) / 2
                    mid_y = (start_y + end_y) / 2
                    label = event
                    if condition and condition != 'true':
                        label += f" [{condition}]"
                    
                    if label:
                        ax.text(mid_x, mid_y + 0.2, label, ha='center', va='bottom',
                               fontsize=8, bbox=dict(boxstyle="round,pad=0.3",
                                                    facecolor='white', alpha=0.8))
        
        # 添加标题
        model_id = model_data.get('model_id', 'Unknown')
        ax.set_title(f'状态机模型: {model_id}', fontsize=16, fontweight='bold', pad=20)
        
        # 添加图例
        self._add_state_machine_legend(ax)
        
        # 保存或显示
        self._save_or_show(fig, output_file, show)
    
    def _visualize_petri_net(self, model_data: Dict[str, Any], 
                            output_file: str, show: bool) -> None:
        """可视化Petri网"""
        elements = model_data.get('elements', {})
        places = elements.get('places', [])
        transitions = elements.get('transitions', [])
        arcs = elements.get('arcs', [])
        initial_marking = elements.get('initial_marking', {})
        
        fig, ax = plt.subplots(figsize=self.figsize)
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 8)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # 计算位置
        place_positions = self._calculate_place_positions(places)
        transition_positions = self._calculate_transition_positions(transitions)
        
        # 绘制库所
        for place in places:
            x, y = place_positions[place]
            
            # 绘制库所圆圈
            circle = Circle((x, y), 0.4, facecolor=self.colors['place'],
                           edgecolor='black', linewidth=2)
            ax.add_patch(circle)
            
            # 添加库所标签
            ax.text(x, y - 0.7, place, ha='center', va='center',
                   fontsize=9, fontweight='bold')
            
            # 绘制令牌
            tokens = initial_marking.get(place, 0)
            if tokens > 0:
                if tokens == 1:
                    token_circle = Circle((x, y), 0.1, facecolor=self.colors['token'])
                    ax.add_patch(token_circle)
                elif tokens <= 4:
                    # 绘制多个令牌
                    positions = [(x-0.1, y-0.1), (x+0.1, y-0.1), 
                                (x-0.1, y+0.1), (x+0.1, y+0.1)]
                    for i in range(min(tokens, 4)):
                        token_x, token_y = positions[i]
                        token_circle = Circle((token_x, token_y), 0.08, 
                                            facecolor=self.colors['token'])
                        ax.add_patch(token_circle)
                else:
                    # 用数字表示大量令牌
                    ax.text(x, y, str(tokens), ha='center', va='center',
                           fontsize=8, fontweight='bold', color='white')
        
        # 绘制变迁
        for transition in transitions:
            x, y = transition_positions[transition]
            
            # 绘制变迁矩形
            rect = Rectangle((x-0.3, y-0.15), 0.6, 0.3,
                           facecolor=self.colors['transition_petri'],
                           edgecolor='black', linewidth=2)
            ax.add_patch(rect)
            
            # 添加变迁标签
            ax.text(x, y - 0.5, transition, ha='center', va='center',
                   fontsize=9, fontweight='bold')
        
        # 绘制弧
        all_positions = {**place_positions, **transition_positions}
        for arc in arcs:
            from_node = arc.get('from')
            to_node = arc.get('to')
            weight = arc.get('weight', 1)
            
            if from_node in all_positions and to_node in all_positions:
                x1, y1 = all_positions[from_node]
                x2, y2 = all_positions[to_node]
                
                # 绘制弧
                ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                           arrowprops=dict(arrowstyle='->', 
                                         color=self.colors['arc'],
                                         lw=1.5))
                
                # 添加权重标签（如果不是1）
                if weight != 1:
                    mid_x = (x1 + x2) / 2
                    mid_y = (y1 + y2) / 2
                    ax.text(mid_x, mid_y, str(weight), ha='center', va='center',
                           fontsize=8, bbox=dict(boxstyle="circle,pad=0.2",
                                               facecolor='yellow', alpha=0.8))
        
        # 添加标题
        model_id = model_data.get('model_id', 'Unknown')
        ax.set_title(f'Petri网模型: {model_id}', fontsize=16, fontweight='bold', pad=20)
        
        # 添加图例
        self._add_petri_net_legend(ax)
        
        # 保存或显示
        self._save_or_show(fig, output_file, show)
    
    def _visualize_unified_sts(self, model_data: Dict[str, Any], 
                              output_file: str, show: bool) -> None:
        """可视化统一状态转换系统"""
        elements = model_data.get('elements', {})
        states = elements.get('states', [])
        events = elements.get('events', [])
        relations = elements.get('relations', [])
        initial_states = elements.get('initial_states', [])
        final_states = elements.get('final_states', [])
        
        fig, ax = plt.subplots(figsize=self.figsize)
        ax.set_xlim(0, 14)
        ax.set_ylim(0, 10)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # 使用networkx进行布局
        G = nx.DiGraph()
        
        # 添加节点
        for state in states:
            G.add_node(state, node_type='state')
        
        # 添加边
        for relation in relations:
            from_state = relation.get('from_state')
            to_state = relation.get('to_state')
            event = relation.get('event')
            weight = relation.get('weight', 1.0)
            
            if from_state and to_state:
                G.add_edge(from_state, to_state, 
                          event=event, weight=weight)
        
        # 计算布局
        if len(states) > 0:
            pos = nx.spring_layout(G, k=3, iterations=50)
            
            # 调整坐标到画布范围
            x_coords = [pos[node][0] for node in pos]
            y_coords = [pos[node][1] for node in pos]
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            
            # 缩放到画布
            for node in pos:
                x = (pos[node][0] - x_min) / (x_max - x_min) * 10 + 2
                y = (pos[node][1] - y_min) / (y_max - y_min) * 6 + 2
                pos[node] = (x, y)
        else:
            pos = {}
        
        # 绘制状态
        for state in states:
            if state in pos:
                x, y = pos[state]
                
                # 确定状态颜色
                if state in initial_states:
                    color = self.colors['initial_state']
                elif state in final_states:
                    color = self.colors['final_state']
                else:
                    color = self.colors['state']
                
                # 绘制状态（使用圆角矩形表示更复杂的状态）
                rect = FancyBboxPatch((x-0.6, y-0.3), 1.2, 0.6,
                                     boxstyle="round,pad=0.1",
                                     facecolor=color,
                                     edgecolor='black', linewidth=2)
                ax.add_patch(rect)
                
                # 添加状态标签
                state_name = state.replace('s_', '') if state.startswith('s_') else state
                ax.text(x, y, state_name, ha='center', va='center',
                       fontsize=9, fontweight='bold')
        
        # 绘制关系
        for relation in relations:
            from_state = relation.get('from_state')
            to_state = relation.get('to_state')
            event = relation.get('event')
            weight = relation.get('weight', 1.0)
            
            if from_state in pos and to_state in pos:
                x1, y1 = pos[from_state]
                x2, y2 = pos[to_state]
                
                # 计算箭头起点和终点
                dx, dy = x2 - x1, y2 - y1
                length = np.sqrt(dx**2 + dy**2)
                if length > 0:
                    unit_dx, unit_dy = dx/length, dy/length
                    start_x = x1 + 0.6 * unit_dx
                    start_y = y1 + 0.3 * unit_dy
                    end_x = x2 - 0.6 * unit_dx
                    end_y = y2 - 0.3 * unit_dy
                    
                    # 绘制箭头
                    arrow_color = self.colors['transition']
                    if weight > 1.0:
                        arrow_color = '#FF5722'  # 高权重用红色
                    
                    ax.annotate('', xy=(end_x, end_y), xytext=(start_x, start_y),
                               arrowprops=dict(arrowstyle='->', 
                                             color=arrow_color,
                                             lw=max(1, weight)))
                    
                    # 添加事件和权重标签
                    mid_x = (start_x + end_x) / 2
                    mid_y = (start_y + end_y) / 2
                    
                    event_name = event.replace('e_', '') if event and event.startswith('e_') else event
                    label = event_name or 'ε'
                    if weight != 1.0:
                        label += f" ({weight:.1f})"
                    
                    ax.text(mid_x, mid_y + 0.2, label, ha='center', va='bottom',
                           fontsize=8, bbox=dict(boxstyle="round,pad=0.2",
                                               facecolor='lightyellow', alpha=0.9))
        
        # 添加事件列表
        if events:
            event_text = "事件集合:\n" + "\n".join([
                f"• {event.replace('e_', '') if event.startswith('e_') else event}" 
                for event in events[:8]  # 限制显示数量
            ])
            if len(events) > 8:
                event_text += f"\n... 还有 {len(events) - 8} 个事件"
            
            ax.text(0.5, 9, event_text, ha='left', va='top',
                   fontsize=8, bbox=dict(boxstyle="round,pad=0.5",
                                       facecolor='lightblue', alpha=0.8))
        
        # 添加标题
        model_id = model_data.get('model_id', 'Unknown')
        ax.set_title(f'统一状态转换系统: {model_id}', fontsize=16, fontweight='bold', pad=20)
        
        # 添加图例
        self._add_unified_sts_legend(ax)
        
        # 保存或显示
        self._save_or_show(fig, output_file, show)
    
    def _calculate_state_positions(self, states: List[str]) -> Dict[str, Tuple[float, float]]:
        """计算状态机中状态的位置"""
        positions = {}
        n = len(states)
        
        if n == 0:
            return positions
        elif n == 1:
            positions[states[0]] = (5, 4)
        elif n == 2:
            positions[states[0]] = (3, 4)
            positions[states[1]] = (7, 4)
        else:
            # 圆形布局
            center_x, center_y = 5, 4
            radius = 2.5
            for i, state in enumerate(states):
                angle = 2 * np.pi * i / n
                x = center_x + radius * np.cos(angle)
                y = center_y + radius * np.sin(angle)
                positions[state] = (x, y)
        
        return positions
    
    def _calculate_place_positions(self, places: List[str]) -> Dict[str, Tuple[float, float]]:
        """计算Petri网中库所的位置"""
        positions = {}
        n = len(places)
        
        if n == 0:
            return positions
        
        # 网格布局
        cols = int(np.ceil(np.sqrt(n)))
        rows = int(np.ceil(n / cols))
        
        for i, place in enumerate(places):
            row = i // cols
            col = i % cols
            x = 2 + col * 3
            y = 6 - row * 2
            positions[place] = (x, y)
        
        return positions
    
    def _calculate_transition_positions(self, transitions: List[str]) -> Dict[str, Tuple[float, float]]:
        """计算Petri网中变迁的位置"""
        positions = {}
        n = len(transitions)
        
        if n == 0:
            return positions
        
        # 在库所之间放置变迁
        for i, transition in enumerate(transitions):
            x = 3.5 + (i % 3) * 3
            y = 4 - (i // 3) * 2
            positions[transition] = (x, y)
        
        return positions
    
    def _add_state_machine_legend(self, ax):
        """添加状态机图例"""
        legend_elements = [
            plt.Circle((0, 0), 0.1, facecolor=self.colors['initial_state'], label='初始状态'),
            plt.Circle((0, 0), 0.1, facecolor=self.colors['state'], label='普通状态'),
            plt.Circle((0, 0), 0.1, facecolor=self.colors['final_state'], label='终止状态'),
            plt.Line2D([0], [0], color=self.colors['transition'], lw=2, label='状态转换')
        ]
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1))
    
    def _add_petri_net_legend(self, ax):
        """添加Petri网图例"""
        legend_elements = [
            plt.Circle((0, 0), 0.1, facecolor=self.colors['place'], label='库所'),
            plt.Rectangle((0, 0), 0.1, 0.1, facecolor=self.colors['transition_petri'], label='变迁'),
            plt.Circle((0, 0), 0.05, facecolor=self.colors['token'], label='令牌'),
            plt.Line2D([0], [0], color=self.colors['arc'], lw=1.5, label='弧')
        ]
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1))
    
    def _add_unified_sts_legend(self, ax):
        """添加统一STS图例"""
        legend_elements = [
            plt.Rectangle((0, 0), 0.1, 0.1, facecolor=self.colors['initial_state'], label='初始状态'),
            plt.Rectangle((0, 0), 0.1, 0.1, facecolor=self.colors['state'], label='普通状态'),
            plt.Rectangle((0, 0), 0.1, 0.1, facecolor=self.colors['final_state'], label='终止状态'),
            plt.Line2D([0], [0], color=self.colors['transition'], lw=2, label='关系转换')
        ]
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1))
    
    def _save_or_show(self, fig, output_file: str, show: bool):
        """保存或显示图形"""
        plt.tight_layout()
        
        if output_file:
            fig.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"图形已保存到: {output_file}")
        
        if show:
            plt.show()
        
        plt.close(fig)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='形式化模型可视化工具')
    parser.add_argument('model_file', help='模型JSON文件路径')
    parser.add_argument('-o', '--output', help='输出图片文件路径')
    parser.add_argument('--no-show', action='store_true', help='不显示图形界面')
    parser.add_argument('--size', nargs=2, type=int, default=[12, 8], 
                       help='图形尺寸 (宽 高)')
    
    args = parser.parse_args()
    
    # 检查输入文件
    if not os.path.exists(args.model_file):
        print(f"错误: 文件不存在 {args.model_file}")
        sys.exit(1)
    
    # 读取模型数据
    try:
        with open(args.model_file, 'r', encoding='utf-8') as f:
            model_data = json.load(f)
    except Exception as e:
        print(f"错误: 无法读取模型文件 {e}")
        sys.exit(1)
    
    # 创建可视化器
    visualizer = ModelVisualizer(figsize=tuple(args.size))
    
    # 可视化模型
    visualizer.visualize_model(
        model_data, 
        output_file=args.output,
        show=not args.no_show
    )

def demo_visualizer():
    """可视化器演示"""
    print("🎨 形式化模型可视化器演示")
    print("=" * 50)
    
    visualizer = ModelVisualizer()
    
    # 演示1: 状态机可视化
    print("\n📊 演示1: 状态机可视化")
    state_machine_model = {
        "model_id": "login_system",
        "model_type": "state_machine",
        "elements": {
            "states": ["logged_out", "logged_in", "login_failed"],
            "initial_state": "logged_out",
            "final_states": ["logged_in"],
            "transitions": [
                {"from": "logged_out", "to": "logged_in", "event": "login_success", "condition": "valid_credentials"},
                {"from": "logged_out", "to": "login_failed", "event": "login_failure", "condition": "invalid_credentials"},
                {"from": "login_failed", "to": "logged_out", "event": "retry", "condition": "true"},
                {"from": "logged_in", "to": "logged_out", "event": "logout", "condition": "true"}
            ]
        }
    }
    
    visualizer.visualize_model(state_machine_model, "state_machine_demo.png", show=False)
    
    # 演示2: Petri网可视化
    print("📊 演示2: Petri网可视化")
    petri_net_model = {
        "model_id": "producer_consumer",
        "model_type": "petri_net",
        "elements": {
            "places": ["buffer", "producer_ready", "consumer_ready"],
            "transitions": ["produce", "consume"],
            "arcs": [
                {"from": "producer_ready", "to": "produce", "weight": 1},
                {"from": "produce", "to": "buffer", "weight": 1},
                {"from": "buffer", "to": "consume", "weight": 1},
                {"from": "consume", "to": "consumer_ready", "weight": 1}
            ],
            "initial_marking": {"producer_ready": 1, "buffer": 0, "consumer_ready": 1}
        }
    }
    
    visualizer.visualize_model(petri_net_model, "petri_net_demo.png", show=False)
    
    # 演示3: 统一STS可视化
    print("📊 演示3: 统一STS可视化")
    unified_sts_model = {
        "model_id": "microservice_system",
        "model_type": "unified_sts",
        "elements": {
            "states": ["s_idle", "s_processing", "s_completed", "s_error"],
            "events": ["e_start", "e_process", "e_complete", "e_error", "e_retry"],
            "relations": [
                {"from_state": "s_idle", "event": "e_start", "to_state": "s_processing", "weight": 1.0},
                {"from_state": "s_processing", "event": "e_complete", "to_state": "s_completed", "weight": 0.8},
                {"from_state": "s_processing", "event": "e_error", "to_state": "s_error", "weight": 0.2},
                {"from_state": "s_error", "event": "e_retry", "to_state": "s_processing", "weight": 0.9},
                {"from_state": "s_completed", "event": "e_start", "to_state": "s_processing", "weight": 1.0}
            ],
            "initial_states": ["s_idle"],
            "final_states": ["s_completed"]
        }
    }
    
    visualizer.visualize_model(unified_sts_model, "unified_sts_demo.png", show=False)
    
    print("\n✅ 演示完成！生成了以下可视化文件：")
    print("- state_machine_demo.png")
    print("- petri_net_demo.png") 
    print("- unified_sts_demo.png")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # 没有参数时运行演示
        demo_visualizer()
    else:
        # 有参数时运行主程序
        main() 