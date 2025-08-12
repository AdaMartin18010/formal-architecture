#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跨理论验证引擎
Cross-Theory Verification Engine

这个引擎用于验证FormalUnified九大理论体系间的一致性、
完整性和逻辑正确性，确保理论体系的整体质量。
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

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TheorySystem:
    """理论体系"""
    name: str
    path: str
    concepts: List[str]
    dependencies: List[str]
    completeness_score: float
    consistency_score: float
    integration_score: float

@dataclass
class VerificationResult:
    """验证结果"""
    theory_system: str
    verification_type: str
    status: str
    score: float
    issues: List[str]
    recommendations: List[str]
    timestamp: str

@dataclass
class CrossTheoryMapping:
    """跨理论映射"""
    source_theory: str
    target_theory: str
    mapping_type: str
    strength: float
    confidence: float
    examples: List[str]

class CrossTheoryVerificationEngine:
    """跨理论验证引擎"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.theory_systems = {}
        self.verification_graph = nx.DiGraph()
        self.mapping_relations = []
        self.verification_results = []
        
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
            "theory_systems": [
                "01-哲学基础理论",
                "02-数学理论体系", 
                "03-形式语言理论体系",
                "04-形式模型理论体系",
                "05-编程语言理论体系",
                "06-软件架构理论体系",
                "07-分布式与微服务",
                "08-实践与应用",
                "09-索引与导航"
            ],
            "verification_levels": ["syntax", "semantics", "logic", "consistency"],
            "mapping_types": ["inheritance", "composition", "dependency", "association"],
            "min_confidence_threshold": 0.7
        }
    
    def load_theory_systems(self, base_path: str = "FormalUnified") -> bool:
        """加载所有理论体系"""
        try:
            base_path = Path(base_path)
            
            for theory_dir in base_path.iterdir():
                if theory_dir.is_dir() and theory_dir.name.startswith(('0', '1')):
                    theory_system = self._analyze_theory_system(theory_dir)
                    if theory_system:
                        self.theory_systems[theory_system.name] = theory_system
                        self.verification_graph.add_node(theory_system.name)
            
            # 建立理论体系间的依赖关系
            self._build_dependency_graph()
            
            logger.info(f"成功加载 {len(self.theory_systems)} 个理论体系")
            return True
            
        except Exception as e:
            logger.error(f"加载理论体系失败: {e}")
            return False
    
    def _analyze_theory_system(self, theory_dir: Path) -> Optional[TheorySystem]:
        """分析单个理论体系"""
        try:
            # 统计文档数量
            md_files = list(theory_dir.rglob("*.md"))
            if not md_files:
                return None
            
            # 分析概念
            concepts = self._extract_concepts_from_files(md_files)
            
            # 分析依赖关系
            dependencies = self._extract_dependencies_from_files(md_files)
            
            # 计算完整性分数
            completeness_score = self._calculate_completeness_score(md_files, concepts)
            
            # 计算一致性分数
            consistency_score = self._calculate_consistency_score(concepts)
            
            # 计算集成分数
            integration_score = self._calculate_integration_score(dependencies)
            
            return TheorySystem(
                name=theory_dir.name,
                path=str(theory_dir),
                concepts=concepts,
                dependencies=dependencies,
                completeness_score=completeness_score,
                consistency_score=consistency_score,
                integration_score=integration_score
            )
            
        except Exception as e:
            logger.error(f"分析理论体系 {theory_dir.name} 失败: {e}")
            return None
    
    def _extract_concepts_from_files(self, md_files: List[Path]) -> List[str]:
        """从Markdown文件中提取概念"""
        concepts = set()
        
        for file_path in md_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                
                # 提取标题作为概念
                headers = re.findall(r'^#{1,6}\s*([^\n]+)', content, re.MULTILINE)
                concepts.update(headers)
                
                # 提取代码块中的概念
                code_blocks = re.findall(r'```(\w+)\n', content)
                concepts.update(code_blocks)
                
                # 提取特殊标记的概念
                special_concepts = re.findall(r'`([^`]+)`', content)
                concepts.update(special_concepts)
                
            except Exception as e:
                logger.warning(f"读取文件 {file_path} 失败: {e}")
                continue
        
        return list(concepts)
    
    def _extract_dependencies_from_files(self, md_files: List[Path]) -> List[str]:
        """从Markdown文件中提取依赖关系"""
        dependencies = set()
        
        for file_path in md_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                
                # 查找对其他理论体系的引用
                for theory_name in self.config["theory_systems"]:
                    if theory_name in content:
                        dependencies.add(theory_name)
                
                # 查找外部链接
                external_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
                for link_text, link_url in external_links:
                    if any(theory in link_url for theory in self.config["theory_systems"]):
                        dependencies.add(link_text)
                
            except Exception as e:
                logger.warning(f"分析依赖关系失败: {e}")
                continue
        
        return list(dependencies)
    
    def _calculate_completeness_score(self, md_files: List[Path], concepts: List[str]) -> float:
        """计算完整性分数"""
        # 基于文档数量和概念数量计算
        doc_score = min(1.0, len(md_files) / 20.0)  # 假设20个文档为完整
        concept_score = min(1.0, len(concepts) / 50.0)  # 假设50个概念为完整
        
        return (doc_score + concept_score) / 2.0
    
    def _calculate_consistency_score(self, concepts: List[str]) -> float:
        """计算一致性分数"""
        # 基于概念命名的一致性
        if not concepts:
            return 0.0
        
        # 检查命名风格一致性
        naming_patterns = {
            'snake_case': r'^[a-z][a-z0-9_]*$',
            'kebab_case': r'^[a-z][a-z0-9-]*$',
            'camel_case': r'^[a-z][a-zA-Z0-9]*$',
            'pascal_case': r'^[A-Z][a-zA-Z0-9]*$'
        }
        
        pattern_matches = {pattern: 0 for pattern in naming_patterns}
        
        for concept in concepts:
            for pattern_name, pattern_regex in naming_patterns.items():
                if re.match(pattern_regex, concept):
                    pattern_matches[pattern_name] += 1
                    break
        
        # 选择最常用的命名风格
        dominant_pattern = max(pattern_matches.items(), key=lambda x: x[1])
        consistency_score = dominant_pattern[1] / len(concepts)
        
        return consistency_score
    
    def _calculate_integration_score(self, dependencies: List[str]) -> float:
        """计算集成分数"""
        # 基于依赖关系的数量和质量
        if not dependencies:
            return 0.0
        
        # 计算与其他理论体系的连接度
        connection_score = min(1.0, len(dependencies) / len(self.config["theory_systems"]))
        
        return connection_score
    
    def _build_dependency_graph(self):
        """构建依赖关系图"""
        for theory_name, theory_system in self.theory_systems.items():
            for dependency in theory_system.dependencies:
                if dependency in self.theory_systems:
                    self.verification_graph.add_edge(dependency, theory_name)
    
    def verify_theory_consistency(self) -> List[VerificationResult]:
        """验证理论一致性"""
        results = []
        
        for theory_name, theory_system in self.theory_systems.items():
            # 验证内部一致性
            internal_result = self._verify_internal_consistency(theory_system)
            results.append(internal_result)
            
            # 验证与其他理论体系的一致性
            external_result = self._verify_external_consistency(theory_system)
            results.append(external_result)
        
        self.verification_results.extend(results)
        return results
    
    def _verify_internal_consistency(self, theory_system: TheorySystem) -> VerificationResult:
        """验证理论体系内部一致性"""
        issues = []
        score = 100.0
        
        try:
            # 1. 概念定义一致性检查
            concept_issues = self._check_concept_consistency(theory_system.concepts)
            if concept_issues:
                issues.extend(concept_issues)
                score -= len(concept_issues) * 5
            
            # 2. 文档结构一致性检查
            structure_issues = self._check_document_structure(theory_system.path)
            if structure_issues:
                issues.extend(structure_issues)
                score -= len(structure_issues) * 3
            
            # 3. 命名规范一致性检查
            naming_issues = self._check_naming_conventions(theory_system.concepts)
            if naming_issues:
                issues.extend(naming_issues)
                score -= len(naming_issues) * 2
            
            # 4. 逻辑关系一致性检查
            logic_issues = self._check_logical_consistency(theory_system.path)
            if logic_issues:
                issues.extend(logic_issues)
                score -= len(logic_issues) * 4
            
            score = max(0, score)
            
            return VerificationResult(
                theory_system=theory_system.name,
                verification_type="internal_consistency",
                status="PASS" if score >= 80 else "WARN" if score >= 60 else "FAIL",
                score=score,
                issues=issues,
                recommendations=self._generate_consistency_recommendations(issues),
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"验证理论体系 {theory_system.name} 内部一致性失败: {e}")
            return VerificationResult(
                theory_system=theory_system.name,
                verification_type="internal_consistency",
                status="ERROR",
                score=0.0,
                issues=[f"验证过程出错: {e}"],
                recommendations=["检查系统配置和文件权限"],
                timestamp=datetime.now().isoformat()
            )
    
    def _check_concept_consistency(self, concepts: List[str]) -> List[str]:
        """检查概念定义一致性"""
        issues = []
        
        # 检查重复概念
        concept_counts = {}
        for concept in concepts:
            clean_concept = concept.strip().lower()
            concept_counts[clean_concept] = concept_counts.get(clean_concept, 0) + 1
        
        for concept, count in concept_counts.items():
            if count > 1:
                issues.append(f"重复概念定义: '{concept}' 出现 {count} 次")
        
        # 检查概念命名规范
        for concept in concepts:
            if len(concept) < 2:
                issues.append(f"概念名称过短: '{concept}'")
            elif len(concept) > 100:
                issues.append(f"概念名称过长: '{concept}'")
            elif not re.match(r'^[a-zA-Z0-9\u4e00-\u9fff\s\-_]+$', concept):
                issues.append(f"概念名称包含非法字符: '{concept}'")
        
        return issues
    
    def _check_document_structure(self, theory_path: str) -> List[str]:
        """检查文档结构一致性"""
        issues = []
        theory_dir = Path(theory_path)
        
        # 检查必要的目录结构
        required_dirs = ['index.md', 'process.md']
        for required_file in required_dirs:
            if not (theory_dir / required_file).exists():
                issues.append(f"缺少必要文件: {required_file}")
        
        # 检查文档层次结构
        md_files = list(theory_dir.rglob("*.md"))
        if len(md_files) < 3:
            issues.append("文档数量过少，可能结构不完整")
        
        return issues
    
    def _check_naming_conventions(self, concepts: List[str]) -> List[str]:
        """检查命名规范一致性"""
        issues = []
        
        # 检查中文命名规范
        chinese_concepts = [c for c in concepts if re.search(r'[\u4e00-\u9fff]', c)]
        for concept in chinese_concepts:
            if not re.match(r'^[\u4e00-\u9fff\s\-_0-9]+$', concept):
                issues.append(f"中文概念命名不规范: '{concept}'")
        
        # 检查英文命名规范
        english_concepts = [c for c in concepts if re.match(r'^[a-zA-Z\s\-_0-9]+$', c) and not re.search(r'[\u4e00-\u9fff]', c)]
        for concept in english_concepts:
            if not re.match(r'^[A-Z][a-zA-Z\s\-_0-9]*$', concept):
                issues.append(f"英文概念命名不规范: '{concept}'")
        
        return issues
    
    def _check_logical_consistency(self, theory_path: str) -> List[str]:
        """检查逻辑关系一致性"""
        issues = []
        theory_dir = Path(theory_path)
        
        # 检查文档间的引用关系
        md_files = list(theory_dir.rglob("*.md"))
        for file_path in md_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                
                # 检查内部链接的有效性
                internal_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
                for link_text, link_url in internal_links:
                    if link_url.startswith('./') or link_url.startswith('../'):
                        target_path = file_path.parent / link_url
                        if not target_path.exists():
                            issues.append(f"无效的内部链接: {file_path.name} -> {link_url}")
                
            except Exception as e:
                issues.append(f"读取文件失败: {file_path.name} - {e}")
        
        return issues
    
    def _generate_consistency_recommendations(self, issues: List[str]) -> List[str]:
        """生成一致性改进建议"""
        recommendations = []
        
        if any("重复概念" in issue for issue in issues):
            recommendations.append("建立概念词典，避免重复定义")
        
        if any("命名规范" in issue for issue in issues):
            recommendations.append("制定统一的命名规范文档")
        
        if any("文档结构" in issue for issue in issues):
            recommendations.append("完善文档模板和结构规范")
        
        if any("逻辑关系" in issue for issue in issues):
            recommendations.append("建立文档间的引用关系检查机制")
        
        if not recommendations:
            recommendations.append("理论体系内部一致性良好，继续保持")
        
        return recommendations
    
    def _verify_external_consistency(self, theory_system: TheorySystem) -> VerificationResult:
        """验证外部一致性"""
        issues = []
        recommendations = []
        score = theory_system.integration_score * 100
        
        # 检查依赖关系的合理性
        for dependency in theory_system.dependencies:
            if dependency not in self.theory_systems:
                issues.append(f"引用了不存在的理论体系: {dependency}")
                recommendations.append(f"移除对 {dependency} 的无效引用")
        
        # 检查循环依赖
        if nx.is_directed_acyclic_graph(self.verification_graph):
            pass  # 无循环依赖
        else:
            cycles = list(nx.simple_cycles(self.verification_graph))
            for cycle in cycles:
                if theory_system.name in cycle:
                    issues.append(f"存在循环依赖: {' -> '.join(cycle)}")
                    recommendations.append("重构依赖关系，消除循环依赖")
        
        # 检查依赖强度
        if len(theory_system.dependencies) < 2:
            issues.append("与其他理论体系关联不足")
            recommendations.append("增加跨理论体系的关联")
        
        return VerificationResult(
            theory_system=theory_system.name,
            verification_type="external_consistency",
            status="pass" if score >= 80 else "warning" if score >= 60 else "fail",
            score=score,
            issues=issues,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
    
    def analyze_cross_theory_mappings(self) -> List[CrossTheoryMapping]:
        """分析跨理论映射关系"""
        mappings = []
        
        for source_name, source_system in self.theory_systems.items():
            for target_name, target_system in self.theory_systems.items():
                if source_name != target_name:
                    mapping = self._analyze_mapping_strength(source_system, target_system)
                    if mapping and mapping.confidence >= self.config["min_confidence_threshold"]:
                        mappings.append(mapping)
        
        self.mapping_relations = mappings
        return mappings
    
    def _analyze_mapping_strength(self, source: TheorySystem, target: TheorySystem) -> Optional[CrossTheoryMapping]:
        """分析两个理论体系间的映射强度"""
        try:
            # 1. 概念相似度分析
            concept_similarity = self._calculate_concept_similarity(source.concepts, target.concepts)
            
            # 2. 依赖关系强度分析
            dependency_strength = self._calculate_dependency_strength(source, target)
            
            # 3. 文档引用关联分析
            reference_strength = self._calculate_reference_strength(source.path, target.path)
            
            # 4. 语义关联分析
            semantic_strength = self._calculate_semantic_strength(source, target)
            
            # 综合计算映射强度
            overall_strength = (
                concept_similarity * 0.3 +
                dependency_strength * 0.25 +
                reference_strength * 0.25 +
                semantic_strength * 0.2
            )
            
            # 计算置信度
            confidence = self._calculate_mapping_confidence(
                concept_similarity, dependency_strength, reference_strength, semantic_strength
            )
            
            # 确定映射类型
            mapping_type = self._determine_mapping_type(overall_strength, concept_similarity)
            
            # 生成映射示例
            examples = self._generate_mapping_examples(source, target, mapping_type)
            
            if overall_strength >= self.config.get("min_confidence_threshold", 0.7):
                return CrossTheoryMapping(
                    source_theory=source.name,
                    target_theory=target.name,
                    mapping_type=mapping_type,
                    strength=overall_strength,
                    confidence=confidence,
                    examples=examples
                )
            
            return None
            
        except Exception as e:
            logger.error(f"分析映射强度失败: {source.name} -> {target.name}: {e}")
            return None
    
    def _calculate_concept_similarity(self, source_concepts: List[str], target_concepts: List[str]) -> float:
        """计算概念相似度"""
        if not source_concepts or not target_concepts:
            return 0.0
        
        # 标准化概念名称
        source_normalized = [self._normalize_concept(c) for c in source_concepts]
        target_normalized = [self._normalize_concept(c) for c in target_concepts]
        
        # 计算Jaccard相似度
        source_set = set(source_normalized)
        target_set = set(target_normalized)
        
        intersection = len(source_set.intersection(target_set))
        union = len(source_set.union(target_set))
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def _normalize_concept(self, concept: str) -> str:
        """标准化概念名称"""
        # 移除特殊字符，转换为小写
        normalized = re.sub(r'[^\w\s]', '', concept.lower())
        # 移除多余空格
        normalized = ' '.join(normalized.split())
        return normalized
    
    def _calculate_dependency_strength(self, source: TheorySystem, target: TheorySystem) -> float:
        """计算依赖关系强度"""
        # 检查直接依赖
        if target.name in source.dependencies:
            return 0.9
        
        # 检查间接依赖
        if any(target.name in dep for dep in source.dependencies):
            return 0.6
        
        # 检查反向依赖
        if source.name in target.dependencies:
            return 0.7
        
        return 0.1
    
    def _calculate_reference_strength(self, source_path: str, target_path: str) -> float:
        """计算文档引用关联强度"""
        try:
            source_dir = Path(source_path)
            target_name = Path(target_path).name
            
            # 统计引用次数
            reference_count = 0
            total_files = 0
            
            for md_file in source_dir.rglob("*.md"):
                try:
                    content = md_file.read_text(encoding='utf-8')
                    total_files += 1
                    
                    # 查找对目标理论体系的引用
                    if target_name in content:
                        reference_count += 1
                    
                    # 查找链接引用
                    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
                    for link_text, link_url in links:
                        if target_name in link_url or target_name in link_text:
                            reference_count += 1
                
                except Exception:
                    continue
            
            if total_files == 0:
                return 0.0
            
            # 计算引用强度
            reference_ratio = reference_count / total_files
            return min(1.0, reference_ratio * 2)  # 放大引用强度
            
        except Exception as e:
            logger.warning(f"计算引用强度失败: {e}")
            return 0.0
    
    def _calculate_semantic_strength(self, source: TheorySystem, target: TheorySystem) -> float:
        """计算语义关联强度"""
        try:
            # 基于理论体系名称的语义关联
            semantic_keywords = {
                '哲学': ['基础', '理论', '认识', '本体'],
                '数学': ['理论', '体系', '代数', '几何', '分析'],
                '形式语言': ['语言', '语法', '语义', '形式'],
                '形式模型': ['模型', '状态', '转换', '验证'],
                '编程语言': ['语言', '编程', '语法', '编译器'],
                '软件架构': ['架构', '设计', '模式', '系统'],
                '分布式': ['分布式', '微服务', '网络', '通信'],
                '实践': ['应用', '实现', '工具', '案例'],
                '索引': ['导航', '索引', '搜索', '组织']
            }
            
            source_keywords = []
            target_keywords = []
            
            for category, keywords in semantic_keywords.items():
                if category in source.name:
                    source_keywords.extend(keywords)
                if category in target.name:
                    target_keywords.extend(keywords)
            
            # 计算关键词重叠度
            if source_keywords and target_keywords:
                overlap = len(set(source_keywords).intersection(set(target_keywords)))
                total = len(set(source_keywords).union(set(target_keywords)))
                return overlap / total if total > 0 else 0.0
            
            return 0.3  # 默认语义关联强度
            
        except Exception as e:
            logger.warning(f"计算语义强度失败: {e}")
            return 0.3
    
    def _calculate_mapping_confidence(self, concept_sim: float, dep_strength: float, 
                                    ref_strength: float, semantic_strength: float) -> float:
        """计算映射置信度"""
        # 基于各项指标的方差计算置信度
        scores = [concept_sim, dep_strength, ref_strength, semantic_strength]
        mean_score = sum(scores) / len(scores)
        
        # 计算一致性（方差越小，置信度越高）
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        consistency = max(0, 1 - variance)
        
        # 综合置信度
        confidence = (mean_score * 0.7 + consistency * 0.3)
        return min(1.0, max(0.0, confidence))
    
    def _determine_mapping_type(self, strength: float, concept_similarity: float) -> str:
        """确定映射类型"""
        if strength >= 0.8 and concept_similarity >= 0.7:
            return "strong_inheritance"
        elif strength >= 0.6 and concept_similarity >= 0.5:
            return "composition"
        elif strength >= 0.4:
            return "dependency"
        else:
            return "association"
    
    def _generate_mapping_examples(self, source: TheorySystem, target: TheorySystem, 
                                 mapping_type: str) -> List[str]:
        """生成映射示例"""
        examples = []
        
        try:
            # 基于映射类型生成示例
            if mapping_type == "strong_inheritance":
                examples.append(f"{source.name} 继承 {target.name} 的核心概念")
                examples.append(f"{source.name} 扩展 {target.name} 的理论框架")
            elif mapping_type == "composition":
                examples.append(f"{source.name} 包含 {target.name} 的组件")
                examples.append(f"{source.name} 使用 {target.name} 的方法")
            elif mapping_type == "dependency":
                examples.append(f"{source.name} 依赖 {target.name} 的基础理论")
                examples.append(f"{source.name} 引用 {target.name} 的概念")
            else:
                examples.append(f"{source.name} 与 {target.name} 存在关联关系")
            
            # 添加具体的概念映射示例
            common_concepts = set(source.concepts).intersection(set(target.concepts))
            if common_concepts:
                examples.append(f"共同概念: {', '.join(list(common_concepts)[:3])}")
            
        except Exception as e:
            logger.warning(f"生成映射示例失败: {e}")
            examples.append("映射关系分析中...")
        
        return examples
    
    def generate_verification_report(self) -> Dict[str, Any]:
        """生成验证报告"""
        report = {
            "verification_summary": {
                "total_systems": len(self.theory_systems),
                "verification_time": datetime.now().isoformat(),
                "overall_score": 0.0,
                "status_distribution": {"pass": 0, "warning": 0, "fail": 0}
            },
            "system_details": {},
            "cross_theory_mappings": [],
            "recommendations": []
        }
        
        # 统计验证结果
        total_score = 0.0
        for result in self.verification_results:
            total_score += result.score
            status = result.status.lower()  # 转换为小写以匹配字典键
            if status in report["verification_summary"]["status_distribution"]:
                report["verification_summary"]["status_distribution"][status] += 1
            else:
                # 如果状态不在预定义中，添加到字典
                report["verification_summary"]["status_distribution"][status] = 1
        
        if self.verification_results:
            report["verification_summary"]["overall_score"] = total_score / len(self.verification_results)
        
        # 添加系统详情
        for theory_name, theory_system in self.theory_systems.items():
            report["system_details"][theory_name] = {
                "completeness": theory_system.completeness_score,
                "consistency": theory_system.consistency_score,
                "integration": theory_system.integration_score,
                "concepts_count": len(theory_system.concepts),
                "dependencies_count": len(theory_system.dependencies)
            }
        
        # 添加跨理论映射
        for mapping in self.mapping_relations:
            report["cross_theory_mappings"].append({
                "source": mapping.source_theory,
                "target": mapping.target_theory,
                "type": mapping.mapping_type,
                "strength": mapping.strength,
                "confidence": mapping.confidence,
                "examples": mapping.examples
            })
        
        # 生成总体建议
        report["recommendations"] = self._generate_overall_recommendations()
        
        return report
    
    def _generate_overall_recommendations(self) -> List[str]:
        """生成总体建议"""
        recommendations = []
        
        # 基于验证结果生成建议
        fail_count = sum(1 for r in self.verification_results if r.status == "FAIL")
        warning_count = sum(1 for r in self.verification_results if r.status == "WARN")
        
        if fail_count > 0:
            recommendations.append(f"有 {fail_count} 个验证失败，需要优先修复")
        
        if warning_count > 0:
            recommendations.append(f"有 {warning_count} 个验证警告，建议及时处理")
        
        # 基于理论体系状态生成建议
        low_completeness = [name for name, system in self.theory_systems.items() 
                           if system.completeness_score < 0.7]
        if low_completeness:
            recommendations.append(f"理论体系 {', '.join(low_completeness)} 完整性不足，需要补充内容")
        
        low_integration = [name for name, system in self.theory_systems.items() 
                          if system.integration_score < 0.5]
        if low_integration:
            recommendations.append(f"理论体系 {', '.join(low_integration)} 集成度低，需要加强跨体系关联")
        
        return recommendations
    
    def export_results(self, output_dir: str = "verification_output") -> bool:
        """导出验证结果"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # 导出验证报告
            report = self.generate_verification_report()
            with open(output_path / "verification_report.json", 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            # 导出详细结果
            with open(output_path / "detailed_results.json", 'w', encoding='utf-8') as f:
                json.dump([asdict(result) for result in self.verification_results], 
                         f, ensure_ascii=False, indent=2)
            
            # 导出映射关系
            with open(output_path / "cross_theory_mappings.json", 'w', encoding='utf-8') as f:
                json.dump([asdict(mapping) for mapping in self.mapping_relations], 
                         f, ensure_ascii=False, indent=2)
            
            logger.info(f"验证结果已导出到 {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出结果失败: {e}")
            return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="跨理论验证引擎")
    parser.add_argument("--config", default="config.yaml", help="配置文件路径")
    args = parser.parse_args()
    
    # 初始化验证引擎
    engine = CrossTheoryVerificationEngine(args.config)
    
    # 加载理论体系
    if not engine.load_theory_systems():
        logger.error("❌ 加载理论体系失败")
        return
    
    # 验证理论一致性
    logger.info("开始验证理论一致性...")
    verification_results = engine.verify_theory_consistency()
    
    # 分析跨理论映射关系
    logger.info("分析跨理论映射关系...")
    mapping_relations = engine.analyze_cross_theory_mappings()
    
    # 生成验证报告
    logger.info("生成验证报告...")
    report = engine.generate_verification_report()
    
    # 导出结果
    logger.info("导出验证结果...")
    if engine.export_results():
        print("\n=== 跨理论验证结果摘要 ===")
        print(f"理论体系数量: {report['verification_summary']['total_systems']}")
        print(f"验证结果数量: {len(verification_results)}")
        print(f"映射关系数量: {len(mapping_relations)}")
        print(f"总体评分: {report['verification_summary']['overall_score']:.2f}")
        
        status_dist = report['verification_summary']['status_distribution']
        status_str = ", ".join([f"{k}={v}" for k, v in status_dist.items()])
        print(f"状态分布: {status_str}")
    else:
        logger.error("❌ 导出验证结果失败")

if __name__ == "__main__":
    main() 