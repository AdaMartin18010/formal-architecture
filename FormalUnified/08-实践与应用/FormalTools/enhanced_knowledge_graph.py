#!/usr/bin/env python3
"""
增强版知识图谱可视化工具 (Enhanced Knowledge Graph Visualizer)
实现高级查询、导航和图谱分析功能

功能特性：
1. 高级查询语言支持
2. 智能导航系统
3. 图谱分析算法
4. 交互式可视化
5. 多格式导出
"""

import json
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle
import numpy as np
from typing import Dict, List, Any, Tuple, Optional, Set
import argparse
import sys
import os
import re
from collections import defaultdict, deque
import heapq

class EnhancedKnowledgeGraph:
    """增强版知识图谱可视化器"""
    
    def __init__(self, figsize=(16, 12)):
        self.figsize = figsize
        self.graph = nx.DiGraph()
        self.node_data = {}
        self.edge_data = {}
        self.colors = {
            'theory': '#E3F2FD',
            'concept': '#FFF3E0',
            'method': '#F3E5F5',
            'tool': '#E8F5E8',
            'application': '#FFEBEE',
            'relation': '#757575',
            'highlight': '#FF5722'
        }
        
        # 查询语言解析器
        self.query_parser = QueryParser()
        
        # 导航系统
        self.navigation = NavigationSystem()
        
        # 分析引擎
        self.analyzer = GraphAnalyzer()
        
    def load_from_markdown(self, markdown_files: List[str]) -> None:
        """从Markdown文件加载知识图谱"""
        print(f"正在从 {len(markdown_files)} 个Markdown文件加载知识图谱...")
        
        for file_path in markdown_files:
            if os.path.exists(file_path):
                self._parse_markdown_file(file_path)
            else:
                print(f"警告: 文件不存在: {file_path}")
        
        print(f"知识图谱加载完成，包含 {len(self.graph.nodes)} 个节点和 {len(self.graph.edges)} 条边")
    
    def _parse_markdown_file(self, file_path: str) -> None:
        """解析单个Markdown文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取文件名作为节点
            file_name = os.path.basename(file_path)
            file_dir = os.path.dirname(file_path)
            
            # 添加到图谱
            self.graph.add_node(file_name, 
                              type='document',
                              path=file_path,
                              directory=file_dir,
                              content_length=len(content))
            
            # 提取标题和概念
            self._extract_concepts_from_content(file_name, content)
            
            # 提取链接关系
            self._extract_links_from_content(file_name, content)
            
        except Exception as e:
            print(f"解析文件 {file_path} 时出错: {e}")
    
    def _extract_concepts_from_content(self, file_name: str, content: str) -> None:
        """从内容中提取概念"""
        # 提取标题
        title_pattern = r'^#+\s+(.+)$'
        titles = re.findall(title_pattern, content, re.MULTILINE)
        
        for i, title in enumerate(titles):
            concept_id = f"{file_name}:{i}"
            self.graph.add_node(concept_id,
                              type='concept',
                              name=title.strip(),
                              source_file=file_name,
                              level=len(title) - len(title.lstrip('#')))
            
            # 添加文档到概念的关系
            self.graph.add_edge(file_name, concept_id, 
                              type='contains', 
                              weight=1.0)
    
    def _extract_links_from_content(self, file_name: str, content: str) -> None:
        """从内容中提取链接关系"""
        # 提取Markdown链接
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, content)
        
        for link_text, link_url in links:
            # 处理相对路径
            if link_url.startswith('./') or link_url.startswith('../'):
                # 这里可以进一步处理相对路径
                pass
            
            # 添加链接关系
            self.graph.add_edge(file_name, link_url,
                              type='references',
                              text=link_text,
                              weight=0.5)
    
    def advanced_query(self, query_string: str) -> List[Dict[str, Any]]:
        """执行高级查询"""
        try:
            parsed_query = self.query_parser.parse(query_string)
            results = self._execute_query(parsed_query)
            return results
        except Exception as e:
            print(f"查询执行错误: {e}")
            return []
    
    def _execute_query(self, parsed_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """执行解析后的查询"""
        query_type = parsed_query.get('type')
        
        if query_type == 'search':
            return self._execute_search_query(parsed_query)
        elif query_type == 'path':
            return self._execute_path_query(parsed_query)
        elif query_type == 'analysis':
            return self._execute_analysis_query(parsed_query)
        else:
            return []
    
    def _execute_search_query(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """执行搜索查询"""
        keyword = query.get('keyword', '')
        node_type = query.get('node_type')
        max_results = query.get('max_results', 10)
        
        results = []
        for node, data in self.graph.nodes(data=True):
            if keyword.lower() in str(data).lower():
                if node_type is None or data.get('type') == node_type:
                    results.append({
                        'node': node,
                        'data': data,
                        'score': self._calculate_relevance_score(node, data, keyword)
                    })
        
        # 按相关性排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:max_results]
    
    def _execute_path_query(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """执行路径查询"""
        start_node = query.get('start')
        end_node = query.get('end')
        max_length = query.get('max_length', 5)
        
        if start_node not in self.graph or end_node not in self.graph:
            return []
        
        try:
            paths = list(nx.all_simple_paths(self.graph, start_node, end_node, cutoff=max_length))
            return [{'path': path, 'length': len(path)} for path in paths]
        except nx.NetworkXNoPath:
            return []
    
    def _execute_analysis_query(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """执行分析查询"""
        analysis_type = query.get('analysis_type')
        
        if analysis_type == 'centrality':
            return self._analyze_centrality()
        elif analysis_type == 'community':
            return self._analyze_communities()
        elif analysis_type == 'connectivity':
            return self._analyze_connectivity()
        else:
            return []
    
    def _calculate_relevance_score(self, node: str, data: Dict[str, Any], keyword: str) -> float:
        """计算节点与关键词的相关性分数"""
        score = 0.0
        
        # 标题匹配
        if 'name' in data and keyword.lower() in data['name'].lower():
            score += 10.0
        
        # 内容匹配
        if 'content' in str(data) and keyword.lower() in str(data).lower():
            score += 5.0
        
        # 类型匹配
        if 'type' in data and keyword.lower() in data['type'].lower():
            score += 3.0
        
        # 连接度
        score += self.graph.degree(node) * 0.1
        
        return score
    
    def _analyze_centrality(self) -> List[Dict[str, Any]]:
        """分析节点中心性"""
        centrality = nx.degree_centrality(self.graph)
        betweenness = nx.betweenness_centrality(self.graph)
        closeness = nx.closeness_centrality(self.graph)
        
        results = []
        for node in self.graph.nodes():
            results.append({
                'node': node,
                'degree_centrality': centrality[node],
                'betweenness_centrality': betweenness[node],
                'closeness_centrality': closeness[node],
                'type': self.graph.nodes[node].get('type', 'unknown')
            })
        
        return sorted(results, key=lambda x: x['degree_centrality'], reverse=True)
    
    def _analyze_communities(self) -> List[Dict[str, Any]]:
        """分析社区结构"""
        try:
            communities = nx.community.greedy_modularity_communities(self.graph.to_undirected())
            results = []
            
            for i, community in enumerate(communities):
                community_nodes = list(community)
                results.append({
                    'community_id': i,
                    'size': len(community_nodes),
                    'nodes': community_nodes,
                    'types': [self.graph.nodes[node].get('type', 'unknown') for node in community_nodes]
                })
            
            return results
        except Exception as e:
            print(f"社区分析错误: {e}")
            return []
    
    def _analyze_connectivity(self) -> List[Dict[str, Any]]:
        """分析连接性"""
        results = []
        
        # 连通分量
        if self.graph.is_directed():
            components = list(nx.strongly_connected_components(self.graph))
        else:
            components = list(nx.connected_components(self.graph))
        
        results.append({
            'metric': 'connected_components',
            'value': len(components),
            'details': [list(comp) for comp in components]
        })
        
        # 平均度
        avg_degree = sum(dict(self.graph.degree()).values()) / len(self.graph.nodes)
        results.append({
            'metric': 'average_degree',
            'value': avg_degree
        })
        
        # 密度
        density = nx.density(self.graph)
        results.append({
            'metric': 'density',
            'value': density
        })
        
        return results
    
    def navigate_to_node(self, target_node: str, start_node: str = None) -> List[str]:
        """导航到目标节点"""
        if start_node is None:
            # 如果没有指定起始节点，使用度最高的节点作为起始点
            start_node = max(self.graph.nodes(), key=lambda x: self.graph.degree(x))
        
        if target_node not in self.graph:
            return []
        
        try:
            path = nx.shortest_path(self.graph, start_node, target_node)
            return path
        except nx.NetworkXNoPath:
            return []
    
    def get_related_nodes(self, node: str, max_related: int = 5) -> List[Dict[str, Any]]:
        """获取相关节点"""
        if node not in self.graph:
            return []
        
        related = []
        for neighbor in self.graph.neighbors(node):
            edge_data = self.graph.edges[node, neighbor]
            related.append({
                'node': neighbor,
                'data': self.graph.nodes[neighbor],
                'relation': edge_data,
                'strength': edge_data.get('weight', 1.0)
            })
        
        # 按关系强度排序
        related.sort(key=lambda x: x['strength'], reverse=True)
        return related[:max_related]
    
    def visualize(self, highlight_nodes: List[str] = None, 
                 layout: str = 'spring', output_file: str = None, 
                 show: bool = True) -> None:
        """可视化知识图谱"""
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # 选择布局算法
        if layout == 'spring':
            pos = nx.spring_layout(self.graph, k=1, iterations=50)
        elif layout == 'circular':
            pos = nx.circular_layout(self.graph)
        elif layout == 'kamada_kawai':
            pos = nx.kamada_kawai_layout(self.graph)
        else:
            pos = nx.spring_layout(self.graph)
        
        # 绘制节点
        self._draw_nodes(ax, pos, highlight_nodes)
        
        # 绘制边
        self._draw_edges(ax, pos)
        
        # 添加图例
        self._add_legend(ax)
        
        # 设置标题
        ax.set_title('增强版知识图谱可视化', fontsize=16, fontweight='bold')
        ax.axis('off')
        
        # 保存或显示
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"图谱已保存到: {output_file}")
        
        if show:
            plt.show()
    
    def _draw_nodes(self, ax, pos: Dict[str, Tuple[float, float]], 
                    highlight_nodes: List[str] = None) -> None:
        """绘制节点"""
        highlight_set = set(highlight_nodes or [])
        
        for node, (x, y) in pos.items():
            node_data = self.graph.nodes[node]
            node_type = node_data.get('type', 'unknown')
            
            # 确定节点颜色
            if node in highlight_set:
                color = self.colors['highlight']
            else:
                color = self.colors.get(node_type, self.colors['concept'])
            
            # 确定节点大小
            degree = self.graph.degree(node)
            size = max(100, degree * 50)
            
            # 绘制节点
            circle = Circle((x, y), size/1000, facecolor=color, 
                           edgecolor='black', linewidth=1, alpha=0.8)
            ax.add_patch(circle)
            
            # 添加标签
            ax.text(x, y, str(node)[:20], ha='center', va='center', 
                   fontsize=8, fontweight='bold')
    
    def _draw_edges(self, ax, pos: Dict[str, Tuple[float, float]]) -> None:
        """绘制边"""
        for edge in self.graph.edges():
            start_pos = pos[edge[0]]
            end_pos = pos[edge[1]]
            
            # 绘制边
            ax.plot([start_pos[0], end_pos[0]], [start_pos[1], end_pos[1]], 
                   color=self.colors['relation'], alpha=0.6, linewidth=1)
    
    def _add_legend(self, ax) -> None:
        """添加图例"""
        legend_elements = []
        for node_type, color in self.colors.items():
            if node_type != 'highlight':
                legend_elements.append(patches.Patch(color=color, label=node_type.title()))
        
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1))
    
    def export_graph(self, format: str = 'json', output_file: str = None) -> str:
        """导出图谱数据"""
        if format == 'json':
            data = {
                'nodes': dict(self.graph.nodes(data=True)),
                'edges': dict(self.graph.edges(data=True)),
                'metadata': {
                    'node_count': len(self.graph.nodes),
                    'edge_count': len(self.graph.edges),
                    'directed': self.graph.is_directed()
                }
            }
            
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                return output_file
            else:
                return json.dumps(data, ensure_ascii=False, indent=2)
        
        elif format == 'gexf':
            if output_file:
                nx.write_gexf(self.graph, output_file)
                return output_file
            else:
                # 返回GEXF格式的字符串
                return nx.generate_gexf(self.graph)
        
        else:
            raise ValueError(f"不支持的导出格式: {format}")


class QueryParser:
    """查询语言解析器"""
    
    def parse(self, query_string: str) -> Dict[str, Any]:
        """解析查询字符串"""
        query_string = query_string.strip().lower()
        
        # 搜索查询: search keyword [type:node_type] [limit:max_results]
        if query_string.startswith('search '):
            return self._parse_search_query(query_string)
        
        # 路径查询: path from start_node to end_node [max:length]
        elif query_string.startswith('path '):
            return self._parse_path_query(query_string)
        
        # 分析查询: analyze centrality|community|connectivity
        elif query_string.startswith('analyze '):
            return self._parse_analysis_query(query_string)
        
        else:
            # 默认搜索查询
            return self._parse_search_query(f"search {query_string}")
    
    def _parse_search_query(self, query: str) -> Dict[str, Any]:
        """解析搜索查询"""
        # 格式: search keyword [type:node_type] [limit:max_results]
        parts = query.split()
        
        result = {
            'type': 'search',
            'keyword': parts[1] if len(parts) > 1 else '',
            'node_type': None,
            'max_results': 10
        }
        
        for part in parts[2:]:
            if ':' in part:
                key, value = part.split(':', 1)
                if key == 'type':
                    result['node_type'] = value
                elif key == 'limit':
                    try:
                        result['max_results'] = int(value)
                    except ValueError:
                        pass
        
        return result
    
    def _parse_path_query(self, query: str) -> Dict[str, Any]:
        """解析路径查询"""
        # 格式: path from start_node to end_node [max:length]
        parts = query.split()
        
        result = {
            'type': 'path',
            'start': None,
            'end': None,
            'max_length': 5
        }
        
        try:
            from_index = parts.index('from')
            to_index = parts.index('to')
            
            if from_index + 1 < len(parts) and to_index + 1 < len(parts):
                result['start'] = parts[from_index + 1]
                result['end'] = parts[to_index + 1]
            
            # 查找max参数
            for part in parts:
                if part.startswith('max:'):
                    try:
                        result['max_length'] = int(part.split(':', 1)[1])
                    except ValueError:
                        pass
                        break
        except ValueError:
            pass
        
        return result
    
    def _parse_analysis_query(self, query: str) -> Dict[str, Any]:
        """解析分析查询"""
        # 格式: analyze centrality|community|connectivity
        parts = query.split()
        
        result = {
            'type': 'analysis',
            'analysis_type': parts[1] if len(parts) > 1 else 'centrality'
        }
        
        return result


class NavigationSystem:
    """导航系统"""
    
    def __init__(self):
        self.navigation_history = []
        self.bookmarks = set()
        self.user_preferences = {}
    
    def add_to_history(self, node: str) -> None:
        """添加到导航历史"""
        if node not in self.navigation_history:
            self.navigation_history.append(node)
        
        # 保持历史记录在合理范围内
        if len(self.navigation_history) > 100:
            self.navigation_history.pop(0)
    
    def get_history(self, max_items: int = 10) -> List[str]:
        """获取导航历史"""
        return self.navigation_history[-max_items:]
    
    def add_bookmark(self, node: str) -> None:
        """添加书签"""
        self.bookmarks.add(node)
    
    def remove_bookmark(self, node: str) -> None:
        """移除书签"""
        self.bookmarks.discard(node)
    
    def get_bookmarks(self) -> List[str]:
        """获取书签列表"""
        return list(self.bookmarks)
    
    def set_preference(self, key: str, value: Any) -> None:
        """设置用户偏好"""
        self.user_preferences[key] = value
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """获取用户偏好"""
        return self.user_preferences.get(key, default)


class GraphAnalyzer:
    """图谱分析引擎"""
    
    def __init__(self):
        self.analysis_cache = {}
    
    def analyze_node_importance(self, graph: nx.DiGraph, node: str) -> Dict[str, float]:
        """分析节点重要性"""
        if node not in graph:
            return {}
        
        # 计算各种中心性指标
        degree_cent = nx.degree_centrality(graph)[node]
        betweenness_cent = nx.betweenness_centrality(graph)[node]
        closeness_cent = nx.closeness_centrality(graph)[node]
        
        # 计算PageRank
        try:
            pagerank = nx.pagerank(graph)[node]
        except:
            pagerank = 0.0
        
        return {
            'degree_centrality': degree_cent,
            'betweenness_centrality': betweenness_cent,
            'closeness_centrality': closeness_cent,
            'pagerank': pagerank,
            'overall_importance': (degree_cent + betweenness_cent + closeness_cent + pagerank) / 4
        }
    
    def find_bridges(self, graph: nx.DiGraph) -> List[Tuple[str, str]]:
        """查找桥接节点"""
        if not graph.is_directed():
            return list(nx.bridges(graph))
        else:
            # 对于有向图，转换为无向图查找桥
            undirected_graph = graph.to_undirected()
            return list(nx.bridges(undirected_graph))
    
    def find_clusters(self, graph: nx.DiGraph, min_cluster_size: int = 3) -> List[List[str]]:
        """查找聚类"""
        try:
            communities = nx.community.greedy_modularity_communities(graph.to_undirected())
            return [list(community) for community in communities if len(community) >= min_cluster_size]
        except:
            return []


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='增强版知识图谱可视化工具')
    parser.add_argument('--files', nargs='+', help='Markdown文件路径列表')
    parser.add_argument('--query', help='查询字符串')
    parser.add_argument('--visualize', action='store_true', help='可视化图谱')
    parser.add_argument('--export', help='导出文件路径')
    parser.add_argument('--export-format', choices=['json', 'gexf'], default='json', help='导出格式')
    parser.add_argument('--output', help='可视化输出文件')
    
    args = parser.parse_args()
    
    # 创建知识图谱
    kg = EnhancedKnowledgeGraph()
    
    # 加载文件
    if args.files:
        kg.load_from_markdown(args.files)
    else:
        # 默认加载当前目录下的Markdown文件
        markdown_files = [f for f in os.listdir('.') if f.endswith('.md')]
        if markdown_files:
            kg.load_from_markdown(markdown_files)
        else:
            print("未找到Markdown文件")
            return
    
    # 执行查询
    if args.query:
        results = kg.advanced_query(args.query)
        print(f"查询结果 ({len(results)} 项):")
        for i, result in enumerate(results[:10]):  # 只显示前10个结果
            print(f"{i+1}. {result}")
    
    # 可视化
    if args.visualize:
        kg.visualize(output_file=args.output, show=True)
    
    # 导出
    if args.export:
        output_path = kg.export_graph(args.export_format, args.export)
        print(f"图谱已导出到: {output_path}")


def demo():
    """演示函数"""
    print("增强版知识图谱可视化工具演示")
    print("=" * 50)
    
    # 创建示例图谱
    kg = EnhancedKnowledgeGraph()
    
    # 添加示例数据
    kg.graph.add_node("哲学基础", type="theory", name="哲学基础理论")
    kg.graph.add_node("数学理论", type="theory", name="数学理论体系")
    kg.graph.add_node("形式语言", type="theory", name="形式语言理论")
    kg.graph.add_node("软件架构", type="theory", name="软件架构理论")
    
    kg.graph.add_edge("哲学基础", "数学理论", type="foundation", weight=1.0)
    kg.graph.add_edge("数学理论", "形式语言", type="foundation", weight=1.0)
    kg.graph.add_edge("形式语言", "软件架构", type="application", weight=0.8)
    kg.graph.add_edge("哲学基础", "软件架构", type="influence", weight=0.6)
    
    # 演示查询功能
    print("\n1. 搜索查询演示:")
    results = kg.advanced_query("search 理论")
    print(f"找到 {len(results)} 个相关节点")
    
    print("\n2. 路径查询演示:")
    paths = kg.advanced_query("path from 哲学基础 to 软件架构")
    print(f"找到 {len(paths)} 条路径")
    
    print("\n3. 分析查询演示:")
    analysis = kg.advanced_query("analyze centrality")
    print(f"中心性分析完成，共 {len(analysis)} 个节点")
    
    # 演示导航功能
    print("\n4. 导航功能演示:")
    path = kg.navigate_to_node("软件架构", "哲学基础")
    print(f"从哲学基础到软件架构的导航路径: {' -> '.join(path)}")
    
    # 演示可视化
    print("\n5. 可视化演示:")
    kg.visualize(show=False)
    print("图谱可视化完成")
    
    print("\n演示完成！")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        demo()
    else:
        main() 