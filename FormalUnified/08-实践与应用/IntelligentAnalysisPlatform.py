#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能化分析平台
Intelligent Analysis Platform

这个平台用于综合分析FormalUnified理论体系的质量、
完整性和关联性，提供智能化的理论分析和优化建议。
"""

import json
import yaml
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import networkx as nx
from datetime import datetime
import re
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AnalysisMetric:
    """分析指标"""
    name: str
    value: float
    weight: float
    description: str
    status: str  # "excellent", "good", "warning", "critical"

@dataclass
class TheoryQualityProfile:
    """理论质量画像"""
    theory_name: str
    completeness_score: float
    consistency_score: float
    coherence_score: float
    accessibility_score: float
    innovation_score: float
    overall_score: float
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]

@dataclass
class CrossTheoryAnalysis:
    """跨理论分析结果"""
    source_theory: str
    target_theory: str
    relationship_type: str
    strength: float
    impact: float
    synergy_potential: float
    integration_opportunities: List[str]

@dataclass
class IntelligentInsight:
    """智能洞察"""
    insight_type: str
    title: str
    description: str
    confidence: float
    impact_level: str
    actionable_items: List[str]
    priority: int

class IntelligentAnalysisPlatform:
    """智能化分析平台"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.theory_systems = {}
        self.analysis_results = {}
        self.insights = []
        self.quality_profiles = {}
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"配置文件 {config_path} 未找到，使用默认配置")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "analysis_weights": {
                "completeness": 0.25,
                "consistency": 0.20,
                "coherence": 0.20,
                "accessibility": 0.15,
                "innovation": 0.20
            },
            "quality_thresholds": {
                "excellent": 0.9,
                "good": 0.7,
                "warning": 0.5,
                "critical": 0.3
            },
            "insight_confidence_threshold": 0.7
        }
    
    def load_theory_systems(self, base_path: str = "FormalUnified") -> bool:
        """加载理论体系"""
        try:
            base_path = Path(base_path)
            
            for theory_dir in base_path.iterdir():
                if theory_dir.is_dir() and theory_dir.name.startswith(('0', '1')):
                    theory_data = self._analyze_theory_system(theory_dir)
                    if theory_data:
                        self.theory_systems[theory_data['name']] = theory_data
            
            logger.info(f"成功加载 {len(self.theory_systems)} 个理论体系")
            return True
            
        except Exception as e:
            logger.error(f"加载理论体系失败: {e}")
            return False
    
    def _analyze_theory_system(self, theory_dir: Path) -> Optional[Dict[str, Any]]:
        """分析单个理论体系"""
        try:
            md_files = list(theory_dir.rglob("*.md"))
            if not md_files:
                return None
            
            # 基础统计
            total_files = len(md_files)
            total_size = sum(f.stat().st_size for f in md_files)
            
            # 内容分析
            concepts = self._extract_concepts(md_files)
            dependencies = self._extract_dependencies(md_files)
            
            # 结构分析
            structure_metrics = self._analyze_structure(md_files)
            
            # 质量分析
            quality_metrics = self._analyze_quality(md_files, concepts)
            
            return {
                'name': theory_dir.name,
                'path': str(theory_dir),
                'total_files': total_files,
                'total_size': total_size,
                'concepts': concepts,
                'dependencies': dependencies,
                'structure_metrics': structure_metrics,
                'quality_metrics': quality_metrics
            }
            
        except Exception as e:
            logger.error(f"分析理论体系 {theory_dir.name} 失败: {e}")
            return None
    
    def _extract_concepts(self, md_files: List[Path]) -> List[str]:
        """提取概念"""
        concepts = set()
        
        for file_path in md_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                
                # 提取标题
                headers = re.findall(r'^#{1,6}\s*([^\n]+)', content, re.MULTILINE)
                concepts.update(headers)
                
                # 提取代码块标识
                code_blocks = re.findall(r'```(\w+)\n', content)
                concepts.update(code_blocks)
                
                # 提取特殊标记
                special_concepts = re.findall(r'`([^`]+)`', content)
                concepts.update(special_concepts)
                
            except Exception:
                continue
        
        return list(concepts)
    
    def _extract_dependencies(self, md_files: List[Path]) -> List[str]:
        """提取依赖关系"""
        dependencies = set()
        
        for file_path in md_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                
                # 查找对其他理论体系的引用
                theory_patterns = [
                    r'01-哲学基础理论', r'02-数学理论体系', r'03-形式语言理论体系',
                    r'04-形式模型理论体系', r'05-编程语言理论体系', r'06-软件架构理论体系',
                    r'07-分布式与微服务', r'08-实践与应用', r'09-索引与导航'
                ]
                
                for pattern in theory_patterns:
                    if re.search(pattern, content):
                        dependencies.add(pattern)
                
            except Exception:
                continue
        
        return list(dependencies)
    
    def _analyze_structure(self, md_files: List[Path]) -> Dict[str, Any]:
        """分析文档结构"""
        structure_metrics = {
            'depth': 0,
            'breadth': 0,
            'organization': 0.0,
            'navigation': 0.0
        }
        
        # 计算目录深度
        max_depth = 0
        for file_path in md_files:
            depth = len(file_path.parts) - len(Path.cwd().parts)
            max_depth = max(max_depth, depth)
        
        structure_metrics['depth'] = max_depth
        structure_metrics['breadth'] = len(md_files)
        
        # 计算组织度（基于文件命名规范）
        organized_files = 0
        for file_path in md_files:
            if re.match(r'^\d{2}-.*\.md$', file_path.name):
                organized_files += 1
        
        structure_metrics['organization'] = organized_files / len(md_files) if md_files else 0.0
        
        # 计算导航度（基于索引文件）
        index_files = [f for f in md_files if 'index' in f.name.lower()]
        structure_metrics['navigation'] = len(index_files) / len(md_files) if md_files else 0.0
        
        return structure_metrics
    
    def _analyze_quality(self, md_files: List[Path], concepts: List[str]) -> Dict[str, Any]:
        """分析文档质量"""
        quality_metrics = {
            'content_richness': 0.0,
            'concept_density': 0.0,
            'code_examples': 0.0,
            'mathematical_formulas': 0.0,
            'cross_references': 0.0
        }
        
        total_content_length = 0
        total_code_blocks = 0
        total_math_formulas = 0
        total_cross_refs = 0
        
        for file_path in md_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                total_content_length += len(content)
                
                # 统计代码块
                code_blocks = len(re.findall(r'```\w*\n', content))
                total_code_blocks += code_blocks
                
                # 统计数学公式
                math_formulas = len(re.findall(r'\$[^$]+\$', content))
                total_math_formulas += math_formulas
                
                # 统计交叉引用
                cross_refs = len(re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content))
                total_cross_refs += cross_refs
                
            except Exception:
                continue
        
        if md_files:
            quality_metrics['content_richness'] = total_content_length / len(md_files) / 1000  # KB per file
            quality_metrics['concept_density'] = len(concepts) / len(md_files)
            quality_metrics['code_examples'] = total_code_blocks / len(md_files)
            quality_metrics['mathematical_formulas'] = total_math_formulas / len(md_files)
            quality_metrics['cross_references'] = total_cross_refs / len(md_files)
        
        return quality_metrics
    
    def generate_quality_profiles(self) -> Dict[str, TheoryQualityProfile]:
        """生成理论质量画像"""
        profiles = {}
        
        for theory_name, theory_data in self.theory_systems.items():
            # 计算各项指标
            completeness = self._calculate_completeness_score(theory_data)
            consistency = self._calculate_consistency_score(theory_data)
            coherence = self._calculate_coherence_score(theory_data)
            accessibility = self._calculate_accessibility_score(theory_data)
            innovation = self._calculate_innovation_score(theory_data)
            
            # 计算综合分数
            weights = self.config['analysis_weights']
            overall_score = (
                completeness * weights['completeness'] +
                consistency * weights['consistency'] +
                coherence * weights['coherence'] +
                accessibility * weights['accessibility'] +
                innovation * weights['innovation']
            )
            
            # 识别优势和劣势
            strengths = self._identify_strengths(theory_data)
            weaknesses = self._identify_weaknesses(theory_data)
            recommendations = self._generate_recommendations(theory_data, weaknesses)
            
            profiles[theory_name] = TheoryQualityProfile(
                theory_name=theory_name,
                completeness_score=completeness,
                consistency_score=consistency,
                coherence_score=coherence,
                accessibility_score=accessibility,
                innovation_score=innovation,
                overall_score=overall_score,
                strengths=strengths,
                weaknesses=weaknesses,
                recommendations=recommendations
            )
        
        self.quality_profiles = profiles
        return profiles
    
    def _calculate_completeness_score(self, theory_data: Dict[str, Any]) -> float:
        """计算完整性分数"""
        # 基于文档数量、概念数量和结构完整性
        file_score = min(1.0, theory_data['total_files'] / 20.0)  # 假设20个文件为完整
        concept_score = min(1.0, len(theory_data['concepts']) / 50.0)  # 假设50个概念为完整
        structure_score = theory_data['structure_metrics']['organization']
        
        return (file_score + concept_score + structure_score) / 3.0
    
    def _calculate_consistency_score(self, theory_data: Dict[str, Any]) -> float:
        """计算一致性分数"""
        # 基于命名规范、结构一致性和内容一致性
        naming_consistency = self._check_naming_consistency(theory_data['concepts'])
        structure_consistency = theory_data['structure_metrics']['organization']
        content_consistency = self._check_content_consistency(theory_data)
        
        return (naming_consistency + structure_consistency + content_consistency) / 3.0
    
    def _calculate_coherence_score(self, theory_data: Dict[str, Any]) -> float:
        """计算连贯性分数"""
        # 基于概念间的逻辑关系和依赖关系
        dependency_score = min(1.0, len(theory_data['dependencies']) / 5.0)  # 假设5个依赖为完整
        cross_ref_score = theory_data['quality_metrics']['cross_references'] / 2.0  # 标准化
        concept_relation_score = self._analyze_concept_relations(theory_data['concepts'])
        
        return (dependency_score + cross_ref_score + concept_relation_score) / 3.0
    
    def _calculate_accessibility_score(self, theory_data: Dict[str, Any]) -> float:
        """计算可访问性分数"""
        # 基于文档结构、导航和内容可读性
        navigation_score = theory_data['structure_metrics']['navigation']
        content_richness = min(1.0, theory_data['quality_metrics']['content_richness'] / 5.0)
        code_examples = min(1.0, theory_data['quality_metrics']['code_examples'] / 3.0)
        
        return (navigation_score + content_richness + code_examples) / 3.0
    
    def _calculate_innovation_score(self, theory_data: Dict[str, Any]) -> float:
        """计算创新性分数"""
        # 基于新概念、新方法和前沿内容
        new_concepts = self._identify_new_concepts(theory_data['concepts'])
        mathematical_content = min(1.0, theory_data['quality_metrics']['mathematical_formulas'] / 5.0)
        cross_theory_integration = len(theory_data['dependencies']) / len(self.theory_systems)
        
        return (new_concepts + mathematical_content + cross_theory_integration) / 3.0
    
    def _check_naming_consistency(self, concepts: List[str]) -> float:
        """检查命名一致性"""
        if not concepts:
            return 0.0
        
        # 检查命名风格一致性
        naming_patterns = {
            'snake_case': r'^[a-z][a-z0-9_]*$',
            'kebab_case': r'^[a-z][a-z0-9-]*$',
            'camel_case': r'^[a-z][a-zA-Z0-9]*$',
            'pascal_case': r'^[A-Z][a-zA-Z0-9]*$',
            'chinese': r'^[\u4e00-\u9fff\s\-_0-9]+$'
        }
        
        pattern_matches = {pattern: 0 for pattern in naming_patterns}
        
        for concept in concepts:
            for pattern_name, pattern_regex in naming_patterns.items():
                if re.match(pattern_regex, concept):
                    pattern_matches[pattern_name] += 1
                    break
        
        # 选择最常用的命名风格
        dominant_pattern = max(pattern_matches.items(), key=lambda x: x[1])
        return dominant_pattern[1] / len(concepts)
    
    def _check_content_consistency(self, theory_data: Dict[str, Any]) -> float:
        """检查内容一致性"""
        # 基于文档长度、代码示例和数学公式的一致性
        content_lengths = []
        
        for file_path in Path(theory_data['path']).rglob("*.md"):
            try:
                content = file_path.read_text(encoding='utf-8')
                content_lengths.append(len(content))
            except Exception:
                continue
        
        if not content_lengths:
            return 0.0
        
        # 计算内容长度的变异系数
        mean_length = sum(content_lengths) / len(content_lengths)
        variance = sum((length - mean_length) ** 2 for length in content_lengths) / len(content_lengths)
        std_dev = variance ** 0.5
        
        if mean_length == 0:
            return 0.0
        
        cv = std_dev / mean_length
        return max(0.0, 1.0 - cv)  # 变异系数越小，一致性越高
    
    def _analyze_concept_relations(self, concepts: List[str]) -> float:
        """分析概念关系"""
        if len(concepts) < 2:
            return 0.0
        
        # 基于概念名称的语义相似性
        related_concepts = 0
        total_pairs = 0
        
        for i, concept1 in enumerate(concepts):
            for j, concept2 in enumerate(concepts[i+1:], i+1):
                total_pairs += 1
                if self._are_concepts_related(concept1, concept2):
                    related_concepts += 1
        
        return related_concepts / total_pairs if total_pairs > 0 else 0.0
    
    def _are_concepts_related(self, concept1: str, concept2: str) -> bool:
        """判断两个概念是否相关"""
        # 基于关键词匹配
        keywords1 = set(re.findall(r'\w+', concept1.lower()))
        keywords2 = set(re.findall(r'\w+', concept2.lower()))
        
        intersection = keywords1.intersection(keywords2)
        union = keywords1.union(keywords2)
        
        if union:
            similarity = len(intersection) / len(union)
            return similarity > 0.3
        
        return False
    
    def _identify_new_concepts(self, concepts: List[str]) -> float:
        """识别新概念"""
        # 基于概念的新颖性（简化版）
        new_concepts = 0
        
        for concept in concepts:
            # 检查是否包含创新性关键词
            innovation_keywords = ['新', '创新', '前沿', '先进', '突破', '革命性', '颠覆性']
            if any(keyword in concept for keyword in innovation_keywords):
                new_concepts += 1
        
        return min(1.0, new_concepts / len(concepts)) if concepts else 0.0
    
    def _identify_strengths(self, theory_data: Dict[str, Any]) -> List[str]:
        """识别优势"""
        strengths = []
        
        if theory_data['total_files'] >= 15:
            strengths.append("文档数量充足")
        
        if len(theory_data['concepts']) >= 30:
            strengths.append("概念体系丰富")
        
        if theory_data['structure_metrics']['organization'] >= 0.8:
            strengths.append("文档组织良好")
        
        if theory_data['quality_metrics']['code_examples'] >= 2.0:
            strengths.append("代码示例丰富")
        
        if len(theory_data['dependencies']) >= 3:
            strengths.append("跨理论关联性强")
        
        return strengths
    
    def _identify_weaknesses(self, theory_data: Dict[str, Any]) -> List[str]:
        """识别劣势"""
        weaknesses = []
        
        if theory_data['total_files'] < 10:
            weaknesses.append("文档数量不足")
        
        if len(theory_data['concepts']) < 20:
            weaknesses.append("概念体系不够丰富")
        
        if theory_data['structure_metrics']['organization'] < 0.6:
            weaknesses.append("文档组织需要改进")
        
        if theory_data['quality_metrics']['code_examples'] < 1.0:
            weaknesses.append("缺少代码示例")
        
        if len(theory_data['dependencies']) < 2:
            weaknesses.append("跨理论关联性弱")
        
        return weaknesses
    
    def _generate_recommendations(self, theory_data: Dict[str, Any], weaknesses: List[str]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if "文档数量不足" in weaknesses:
            recommendations.append("增加理论文档，完善知识体系")
        
        if "概念体系不够丰富" in weaknesses:
            recommendations.append("扩展概念定义，建立概念词典")
        
        if "文档组织需要改进" in weaknesses:
            recommendations.append("统一文档命名规范，优化目录结构")
        
        if "缺少代码示例" in weaknesses:
            recommendations.append("增加代码示例和实现案例")
        
        if "跨理论关联性弱" in weaknesses:
            recommendations.append("加强与其他理论体系的关联")
        
        return recommendations
    
    def generate_intelligent_insights(self) -> List[IntelligentInsight]:
        """生成智能洞察"""
        insights = []
        
        # 分析理论体系间的协同效应
        synergy_insights = self._analyze_synergy_opportunities()
        insights.extend(synergy_insights)
        
        # 分析质量改进机会
        quality_insights = self._analyze_quality_improvements()
        insights.extend(quality_insights)
        
        # 分析创新潜力
        innovation_insights = self._analyze_innovation_potential()
        insights.extend(innovation_insights)
        
        # 分析风险点
        risk_insights = self._analyze_risk_points()
        insights.extend(risk_insights)
        
        self.insights = insights
        return insights
    
    def _analyze_synergy_opportunities(self) -> List[IntelligentInsight]:
        """分析协同机会"""
        insights = []
        
        # 找出关联度高的理论体系对
        theory_pairs = []
        for theory1 in self.theory_systems.keys():
            for theory2 in self.theory_systems.keys():
                if theory1 < theory2:
                    synergy_score = self._calculate_synergy_score(theory1, theory2)
                    if synergy_score > 0.7:
                        theory_pairs.append((theory1, theory2, synergy_score))
        
        # 生成协同洞察
        for theory1, theory2, score in sorted(theory_pairs, key=lambda x: x[2], reverse=True)[:3]:
            insight = IntelligentInsight(
                insight_type="synergy_opportunity",
                title=f"{theory1} 与 {theory2} 的协同机会",
                description=f"这两个理论体系具有很高的协同潜力（{score:.2f}），建议加强整合",
                confidence=score,
                impact_level="high",
                actionable_items=[
                    f"建立 {theory1} 和 {theory2} 的联合工作组",
                    f"开发跨理论验证工具",
                    f"创建统一的文档模板"
                ],
                priority=1
            )
            insights.append(insight)
        
        return insights
    
    def _calculate_synergy_score(self, theory1: str, theory2: str) -> float:
        """计算协同分数"""
        data1 = self.theory_systems[theory1]
        data2 = self.theory_systems[theory2]
        
        # 基于概念重叠度
        concepts1 = set(data1['concepts'])
        concepts2 = set(data2['concepts'])
        concept_overlap = len(concepts1.intersection(concepts2)) / len(concepts1.union(concepts2)) if concepts1.union(concepts2) else 0
        
        # 基于依赖关系
        dependency_score = 1.0 if theory2 in data1['dependencies'] or theory1 in data2['dependencies'] else 0.0
        
        # 基于质量互补性
        quality1 = data1['quality_metrics']['content_richness']
        quality2 = data2['quality_metrics']['content_richness']
        quality_complement = 1.0 - abs(quality1 - quality2) / max(quality1, quality2) if max(quality1, quality2) > 0 else 0.0
        
        return (concept_overlap * 0.4 + dependency_score * 0.4 + quality_complement * 0.2)
    
    def _analyze_quality_improvements(self) -> List[IntelligentInsight]:
        """分析质量改进机会"""
        insights = []
        
        # 找出质量最低的理论体系
        low_quality_theories = []
        for theory_name, theory_data in self.theory_systems.items():
            profile = self.quality_profiles.get(theory_name)
            if profile and profile.overall_score < 0.6:
                low_quality_theories.append((theory_name, profile.overall_score))
        
        for theory_name, score in sorted(low_quality_theories, key=lambda x: x[1])[:3]:
            profile = self.quality_profiles[theory_name]
            insight = IntelligentInsight(
                insight_type="quality_improvement",
                title=f"{theory_name} 质量改进机会",
                description=f"该理论体系质量评分较低（{score:.2f}），需要重点关注",
                confidence=1.0 - score,
                impact_level="medium",
                actionable_items=profile.recommendations[:3],
                priority=2
            )
            insights.append(insight)
        
        return insights
    
    def _analyze_innovation_potential(self) -> List[IntelligentInsight]:
        """分析创新潜力"""
        insights = []
        
        # 找出创新性最高的理论体系
        innovative_theories = []
        for theory_name, theory_data in self.theory_systems.items():
            profile = self.quality_profiles.get(theory_name)
            if profile and profile.innovation_score > 0.7:
                innovative_theories.append((theory_name, profile.innovation_score))
        
        for theory_name, score in sorted(innovative_theories, key=lambda x: x[1], reverse=True)[:2]:
            insight = IntelligentInsight(
                insight_type="innovation_potential",
                title=f"{theory_name} 创新潜力",
                description=f"该理论体系具有很高的创新性（{score:.2f}），建议优先发展",
                confidence=score,
                impact_level="high",
                actionable_items=[
                    "申请相关研究项目",
                    "发表学术论文",
                    "申请专利保护"
                ],
                priority=1
            )
            insights.append(insight)
        
        return insights
    
    def _analyze_risk_points(self) -> List[IntelligentInsight]:
        """分析风险点"""
        insights = []
        
        # 找出依赖关系过少的理论体系
        isolated_theories = []
        for theory_name, theory_data in self.theory_systems.items():
            if len(theory_data['dependencies']) < 1:
                isolated_theories.append(theory_name)
        
        if isolated_theories:
            insight = IntelligentInsight(
                insight_type="risk_identification",
                title="理论体系孤立风险",
                description=f"理论体系 {', '.join(isolated_theories)} 缺乏与其他体系的关联，存在孤立风险",
                confidence=0.8,
                impact_level="medium",
                actionable_items=[
                    "建立跨理论关联机制",
                    "增加交叉引用",
                    "组织跨理论研讨会"
                ],
                priority=2
            )
            insights.append(insight)
        
        return insights
    
    def export_analysis_report(self, output_dir: str = "analysis_output") -> bool:
        """导出分析报告"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # 导出质量画像
            quality_report = {
                "analysis_time": datetime.now().isoformat(),
                "total_theories": len(self.theory_systems),
                "quality_profiles": {name: asdict(profile) for name, profile in self.quality_profiles.items()},
                "insights": [asdict(insight) for insight in self.insights]
            }
            
            with open(output_path / "quality_analysis_report.json", 'w', encoding='utf-8') as f:
                json.dump(quality_report, f, ensure_ascii=False, indent=2)
            
            # 生成可视化报告
            self._generate_visualization_report(output_path)
            
            logger.info(f"分析报告已导出到 {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出分析报告失败: {e}")
            return False
    
    def _generate_visualization_report(self, output_path: Path):
        """生成可视化报告"""
        try:
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            
            # 创建质量评分雷达图
            self._create_radar_chart(output_path)
            
            # 创建理论体系对比图
            self._create_comparison_chart(output_path)
            
        except Exception as e:
            logger.warning(f"生成可视化报告失败: {e}")
    
    def _create_radar_chart(self, output_path: Path):
        """创建雷达图"""
        if not self.quality_profiles:
            return
        
        # 选择前5个理论体系
        top_theories = sorted(self.quality_profiles.items(), 
                            key=lambda x: x[1].overall_score, reverse=True)[:5]
        
        categories = ['完整性', '一致性', '连贯性', '可访问性', '创新性']
        
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(projection='polar'))
        
        for theory_name, profile in top_theories:
            values = [
                profile.completeness_score,
                profile.consistency_score,
                profile.coherence_score,
                profile.accessibility_score,
                profile.innovation_score
            ]
            
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            values += values[:1]  # 闭合图形
            angles += angles[:1]
            
            ax.plot(angles, values, 'o-', linewidth=2, label=theory_name)
            ax.fill(angles, values, alpha=0.25)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 1)
        ax.set_title('理论体系质量雷达图', size=16, pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        plt.tight_layout()
        plt.savefig(output_path / "quality_radar_chart.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_comparison_chart(self, output_path: Path):
        """创建对比图"""
        if not self.quality_profiles:
            return
        
        theories = list(self.quality_profiles.keys())
        scores = [profile.overall_score for profile in self.quality_profiles.values()]
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(theories, scores, color='skyblue', alpha=0.7)
        
        # 添加数值标签
        for bar, score in zip(bars, scores):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{score:.2f}', ha='center', va='bottom')
        
        plt.xlabel('理论体系')
        plt.ylabel('综合质量评分')
        plt.title('理论体系质量对比')
        plt.xticks(rotation=45, ha='right')
        plt.ylim(0, 1)
        plt.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path / "quality_comparison_chart.png", dpi=300, bbox_inches='tight')
        plt.close()

def main():
    """主函数"""
    platform = IntelligentAnalysisPlatform()
    
    # 加载理论体系
    if not platform.load_theory_systems():
        logger.error("加载理论体系失败")
        return
    
    # 生成质量画像
    logger.info("生成理论质量画像...")
    quality_profiles = platform.generate_quality_profiles()
    
    # 生成智能洞察
    logger.info("生成智能洞察...")
    insights = platform.generate_intelligent_insights()
    
    # 导出分析报告
    logger.info("导出分析报告...")
    platform.export_analysis_report()
    
    # 输出摘要
    print(f"\n=== 智能化分析结果摘要 ===")
    print(f"分析的理论体系数量: {len(platform.theory_systems)}")
    print(f"生成的质量画像数量: {len(quality_profiles)}")
    print(f"生成的智能洞察数量: {len(insights)}")
    
    # 显示前3个洞察
    print(f"\n=== 主要洞察 ===")
    for i, insight in enumerate(insights[:3], 1):
        print(f"{i}. {insight.title}")
        print(f"   描述: {insight.description}")
        print(f"   置信度: {insight.confidence:.2f}")
        print(f"   优先级: {insight.priority}")
        print()

if __name__ == "__main__":
    main() 