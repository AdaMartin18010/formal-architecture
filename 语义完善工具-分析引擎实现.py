#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语义完善工具 - 分析引擎实现
Semantic Enhancement Tool - Analysis Engine Implementation

本模块实现了语义完善工具的核心分析引擎，包括文档解析器和语义分析器。
"""

import re
import json
import yaml
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Concept:
    """概念数据结构"""
    name: str
    definition: str
    properties: List[str]
    relations: List[str]
    examples: List[str]
    counterexamples: List[str]
    formal_definition: Optional[str] = None
    source_section: Optional[str] = None

@dataclass
class Operation:
    """操作数据结构"""
    name: str
    description: str
    algorithm: Optional[str] = None
    complexity: Optional[str] = None
    correctness_proof: Optional[str] = None
    implementation: Optional[str] = None
    verification_method: Optional[str] = None
    source_section: Optional[str] = None

@dataclass
class Argument:
    """论证数据结构"""
    name: str
    statement: str
    proof_steps: List[str]
    reasoning_chain: List[str]
    verification_method: Optional[str] = None
    case_analysis: List[str] = None
    source_section: Optional[str] = None

@dataclass
class DocumentStructure:
    """文档结构数据"""
    title: str
    sections: List[Dict[str, Any]]
    concepts: List[Concept]
    operations: List[Operation]
    arguments: List[Argument]
    code_blocks: List[str]
    math_formulas: List[str]
    links: List[str]

class DocumentParser:
    """文档解析器，负责解析Markdown文档结构"""
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化文档解析器"""
        self.config = config or {}
        self.concept_patterns = [
            r'**([^:]+):**\s*(.+)',  # **概念名:** 定义
            r'([A-Z][a-zA-Z\s]+):\s*(.+)',  # 概念名: 定义
            r'###\s*([^#\n]+)',  # ### 概念名
        ]
        
    def parse_structure(self, content: str) -> DocumentStructure:
        """解析文档结构"""
        logger.info("开始解析文档结构")
        
        # 解析标题
        title = self._extract_title(content)
        
        # 解析章节
        sections = self._extract_sections(content)
        
        # 解析代码块
        code_blocks = self._extract_code_blocks(content)
        
        # 解析数学公式
        math_formulas = self._extract_math_formulas(content)
        
        # 解析链接
        links = self._extract_links(content)
        
        # 提取概念、操作、论证
        concepts = self.extract_concepts(content)
        operations = self.extract_operations(content)
        arguments = self.extract_arguments(content)
        
        return DocumentStructure(
            title=title,
            sections=sections,
            concepts=concepts,
            operations=operations,
            arguments=arguments,
            code_blocks=code_blocks,
            math_formulas=math_formulas,
            links=links
        )
    
    def _extract_title(self, content: str) -> str:
        """提取文档标题"""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        return "未命名文档"
    
    def _extract_sections(self, content: str) -> List[Dict[str, Any]]:
        """提取章节结构"""
        sections = []
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                
                if level == 1:
                    current_section = {
                        'title': title,
                        'level': level,
                        'subsections': []
                    }
                    sections.append(current_section)
                elif level == 2 and current_section:
                    subsection = {
                        'title': title,
                        'level': level,
                        'subsubsections': []
                    }
                    current_section['subsections'].append(subsection)
        
        return sections
    
    def _extract_code_blocks(self, content: str) -> List[str]:
        """提取代码块"""
        code_blocks = []
        pattern = r'```[\w]*\n(.*?)\n```'
        matches = re.findall(pattern, content, re.DOTALL)
        code_blocks.extend(matches)
        return code_blocks
    
    def _extract_math_formulas(self, content: str) -> List[str]:
        """提取数学公式"""
        math_formulas = []
        # 行内公式
        inline_pattern = r'\$(.*?)\$'
        inline_matches = re.findall(inline_pattern, content)
        math_formulas.extend(inline_matches)
        
        # 块级公式
        block_pattern = r'\$\$(.*?)\$\$'
        block_matches = re.findall(block_pattern, content, re.DOTALL)
        math_formulas.extend(block_matches)
        
        return math_formulas
    
    def _extract_links(self, content: str) -> List[str]:
        """提取链接"""
        links = []
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(pattern, content)
        links.extend([f"{text}: {url}" for text, url in matches])
        return links
    
    def extract_concepts(self, content: str) -> List[Concept]:
        """提取核心概念"""
        logger.info("开始提取核心概念")
        concepts = []
        
        # 按章节分割内容
        sections = content.split('\n## ')
        
        for section in sections:
            if not section.strip():
                continue
                
            section_lines = section.split('\n')
            section_title = section_lines[0].strip()
            
            # 查找概念定义
            for i, line in enumerate(section_lines):
                for pattern in self.concept_patterns:
                    match = re.search(pattern, line)
                    if match:
                        concept_name = match.group(1).strip()
                        
                        # 提取定义
                        definition = self._extract_definition(section_lines, i)
                        
                        # 提取属性
                        properties = self._extract_properties(section_lines, i)
                        
                        # 提取关系
                        relations = self._extract_relations(section_lines, i)
                        
                        # 提取示例
                        examples = self._extract_examples(section_lines, i)
                        
                        # 提取反例
                        counterexamples = self._extract_counterexamples(section_lines, i)
                        
                        # 提取形式化定义
                        formal_definition = self._extract_formal_definition(section_lines, i)
                        
                        concept = Concept(
                            name=concept_name,
                            definition=definition,
                            properties=properties,
                            relations=relations,
                            examples=examples,
                            counterexamples=counterexamples,
                            formal_definition=formal_definition,
                            source_section=section_title
                        )
                        concepts.append(concept)
                        break
        
        logger.info(f"提取到 {len(concepts)} 个概念")
        return concepts
    
    def _extract_definition(self, lines: List[str], start_index: int) -> str:
        """提取概念定义"""
        definition = ""
        definition_patterns = [
            r'定义[：:]\s*(.+)',
            r'Definition[：:]\s*(.+)',
            r'([^。]+是[^。]+。)',
        ]
        
        for i in range(start_index, min(start_index + 5, len(lines))):
            line = lines[i]
            for pattern in definition_patterns:
                match = re.search(pattern, line)
                if match:
                    definition = match.group(1).strip()
                    break
            if definition:
                break
        return definition
    
    def _extract_properties(self, lines: List[str], start_index: int) -> List[str]:
        """提取概念属性"""
        properties = []
        property_patterns = [
            r'性质[：:]\s*(.+)',
            r'Property[：:]\s*(.+)',
            r'([^。]+具有[^。]+。)',
        ]
        
        for i in range(start_index, min(start_index + 10, len(lines))):
            line = lines[i]
            for pattern in property_patterns:
                match = re.search(pattern, line)
                if match:
                    properties.append(match.group(1).strip())
                    break
        return properties
    
    def _extract_relations(self, lines: List[str], start_index: int) -> List[str]:
        """提取概念关系"""
        relations = []
        relation_patterns = [
            r'关系[：:]\s*(.+)',
            r'Relation[：:]\s*(.+)',
            r'([^。]+与[^。]+相关[^。]*。)',
        ]
        
        for i in range(start_index, min(start_index + 10, len(lines))):
            line = lines[i]
            for pattern in relation_patterns:
                match = re.search(pattern, line)
                if match:
                    relations.append(match.group(1).strip())
                    break
        return relations
    
    def _extract_examples(self, lines: List[str], start_index: int) -> List[str]:
        """提取概念示例"""
        examples = []
        example_patterns = [
            r'示例[：:]\s*(.+)',
            r'Example[：:]\s*(.+)',
            r'([^。]+例如[^。]*。)',
        ]
        
        for i in range(start_index, min(start_index + 10, len(lines))):
            line = lines[i]
            for pattern in example_patterns:
                match = re.search(pattern, line)
                if match:
                    examples.append(match.group(1).strip())
                    break
        return examples
    
    def _extract_counterexamples(self, lines: List[str], start_index: int) -> List[str]:
        """提取概念反例"""
        counterexamples = []
        counterexample_patterns = [
            r'反例[：:]\s*(.+)',
            r'Counterexample[：:]\s*(.+)',
            r'([^。]+不是[^。]*。)',
        ]
        
        for i in range(start_index, min(start_index + 10, len(lines))):
            line = lines[i]
            for pattern in counterexample_patterns:
                match = re.search(pattern, line)
                if match:
                    counterexamples.append(match.group(1).strip())
                    break
        return counterexamples
    
    def _extract_formal_definition(self, lines: List[str], start_index: int) -> Optional[str]:
        """提取形式化定义"""
        for i in range(start_index, min(start_index + 10, len(lines))):
            line = lines[i]
            # 查找数学公式
            if '$' in line or '```' in line:
                return line.strip()
        return None
    
    def extract_operations(self, content: str) -> List[Operation]:
        """提取操作"""
        logger.info("开始提取操作")
        operations = []
        
        # 查找操作相关章节
        operation_patterns = [
            r'算法[：:]\s*(.+)',
            r'Algorithm[：:]\s*(.+)',
            r'方法[：:]\s*(.+)',
            r'Method[：:]\s*(.+)',
        ]
        
        sections = content.split('\n## ')
        
        for section in sections:
            if not section.strip():
                continue
                
            section_lines = section.split('\n')
            section_title = section_lines[0].strip()
            
            for i, line in enumerate(section_lines):
                for pattern in operation_patterns:
                    match = re.search(pattern, line)
                    if match:
                        operation_name = match.group(1).strip()
                        
                        # 提取描述
                        description = self._extract_operation_description(section_lines, i)
                        
                        # 提取算法
                        algorithm = self._extract_algorithm(section_lines, i)
                        
                        # 提取复杂度
                        complexity = self._extract_complexity(section_lines, i)
                        
                        # 提取正确性证明
                        correctness_proof = self._extract_correctness_proof(section_lines, i)
                        
                        # 提取实现
                        implementation = self._extract_implementation(section_lines, i)
                        
                        # 提取验证方法
                        verification_method = self._extract_verification_method(section_lines, i)
                        
                        operation = Operation(
                            name=operation_name,
                            description=description,
                            algorithm=algorithm,
                            complexity=complexity,
                            correctness_proof=correctness_proof,
                            implementation=implementation,
                            verification_method=verification_method,
                            source_section=section_title
                        )
                        operations.append(operation)
                        break
        
        logger.info(f"提取到 {len(operations)} 个操作")
        return operations
    
    def _extract_operation_description(self, lines: List[str], start_index: int) -> str:
        """提取操作描述"""
        description = ""
        for i in range(start_index, min(start_index + 3, len(lines))):
            line = lines[i]
            if line.strip() and not line.startswith('#'):
                description = line.strip()
                break
        return description
    
    def _extract_algorithm(self, lines: List[str], start_index: int) -> Optional[str]:
        """提取算法"""
        for i in range(start_index, min(start_index + 20, len(lines))):
            line = lines[i]
            if '```' in line or '算法' in line or 'Algorithm' in line:
                # 提取代码块
                code_start = i
                for j in range(i, len(lines)):
                    if '```' in lines[j] and j > i:
                        return '\n'.join(lines[code_start:j+1])
        return None
    
    def _extract_complexity(self, lines: List[str], start_index: int) -> Optional[str]:
        """提取复杂度"""
        complexity_patterns = [
            r'复杂度[：:]\s*(.+)',
            r'Complexity[：:]\s*(.+)',
            r'时间复杂度[：:]\s*(.+)',
            r'空间复杂度[：:]\s*(.+)',
        ]
        
        for i in range(start_index, min(start_index + 10, len(lines))):
            line = lines[i]
            for pattern in complexity_patterns:
                match = re.search(pattern, line)
                if match:
                    return match.group(1).strip()
        return None
    
    def _extract_correctness_proof(self, lines: List[str], start_index: int) -> Optional[str]:
        """提取正确性证明"""
        proof_patterns = [
            r'证明[：:]\s*(.+)',
            r'Proof[：:]\s*(.+)',
            r'正确性[：:]\s*(.+)',
        ]
        
        for i in range(start_index, min(start_index + 15, len(lines))):
            line = lines[i]
            for pattern in proof_patterns:
                match = re.search(pattern, line)
                if match:
                    return match.group(1).strip()
        return None
    
    def _extract_implementation(self, lines: List[str], start_index: int) -> Optional[str]:
        """提取实现"""
        for i in range(start_index, min(start_index + 20, len(lines))):
            line = lines[i]
            if '实现' in line or 'Implementation' in line or '代码' in line:
                # 提取代码块
                for j in range(i, len(lines)):
                    if '```' in lines[j]:
                        code_start = j
                        for k in range(j+1, len(lines)):
                            if '```' in lines[k]:
                                return '\n'.join(lines[code_start:k+1])
        return None
    
    def _extract_verification_method(self, lines: List[str], start_index: int) -> Optional[str]:
        """提取验证方法"""
        verification_patterns = [
            r'验证[：:]\s*(.+)',
            r'Verification[：:]\s*(.+)',
            r'测试[：:]\s*(.+)',
        ]
        
        for i in range(start_index, min(start_index + 10, len(lines))):
            line = lines[i]
            for pattern in verification_patterns:
                match = re.search(pattern, line)
                if match:
                    return match.group(1).strip()
        return None
    
    def extract_arguments(self, content: str) -> List[Argument]:
        """提取论证过程"""
        logger.info("开始提取论证过程")
        arguments = []
        
        # 查找论证相关章节
        argument_patterns = [
            r'论证[：:]\s*(.+)',
            r'Argument[：:]\s*(.+)',
            r'证明[：:]\s*(.+)',
            r'Proof[：:]\s*(.+)',
        ]
        
        sections = content.split('\n## ')
        
        for section in sections:
            if not section.strip():
                continue
                
            section_lines = section.split('\n')
            section_title = section_lines[0].strip()
            
            for i, line in enumerate(section_lines):
                for pattern in argument_patterns:
                    match = re.search(pattern, line)
                    if match:
                        argument_name = match.group(1).strip()
                        
                        # 提取陈述
                        statement = self._extract_statement(section_lines, i)
                        
                        # 提取证明步骤
                        proof_steps = self._extract_proof_steps(section_lines, i)
                        
                        # 提取推理链
                        reasoning_chain = self._extract_reasoning_chain(section_lines, i)
                        
                        # 提取验证方法
                        verification_method = self._extract_argument_verification(section_lines, i)
                        
                        # 提取案例分析
                        case_analysis = self._extract_case_analysis(section_lines, i)
                        
                        argument = Argument(
                            name=argument_name,
                            statement=statement,
                            proof_steps=proof_steps,
                            reasoning_chain=reasoning_chain,
                            verification_method=verification_method,
                            case_analysis=case_analysis,
                            source_section=section_title
                        )
                        arguments.append(argument)
                        break
        
        logger.info(f"提取到 {len(arguments)} 个论证")
        return arguments
    
    def _extract_statement(self, lines: List[str], start_index: int) -> str:
        """提取论证陈述"""
        statement = ""
        for i in range(start_index, min(start_index + 3, len(lines))):
            line = lines[i]
            if line.strip() and not line.startswith('#'):
                statement = line.strip()
                break
        return statement
    
    def _extract_proof_steps(self, lines: List[str], start_index: int) -> List[str]:
        """提取证明步骤"""
        proof_steps = []
        step_patterns = [
            r'步骤[：:]\s*(.+)',
            r'Step[：:]\s*(.+)',
            r'(\d+)[.、]\s*(.+)',
        ]
        
        for i in range(start_index, min(start_index + 20, len(lines))):
            line = lines[i]
            for pattern in step_patterns:
                match = re.search(pattern, line)
                if match:
                    if len(match.groups()) == 1:
                        proof_steps.append(match.group(1).strip())
                    else:
                        proof_steps.append(match.group(2).strip())
                    break
        return proof_steps
    
    def _extract_reasoning_chain(self, lines: List[str], start_index: int) -> List[str]:
        """提取推理链"""
        reasoning_chain = []
        reasoning_patterns = [
            r'推理[：:]\s*(.+)',
            r'Reasoning[：:]\s*(.+)',
            r'因为[^。]*。',
            r'因此[^。]*。',
        ]
        
        for i in range(start_index, min(start_index + 15, len(lines))):
            line = lines[i]
            for pattern in reasoning_patterns:
                match = re.search(pattern, line)
                if match:
                    reasoning_chain.append(match.group(1).strip())
                    break
        return reasoning_chain
    
    def _extract_argument_verification(self, lines: List[str], start_index: int) -> Optional[str]:
        """提取论证验证方法"""
        verification_patterns = [
            r'验证[：:]\s*(.+)',
            r'Verification[：:]\s*(.+)',
            r'检验[：:]\s*(.+)',
        ]
        
        for i in range(start_index, min(start_index + 10, len(lines))):
            line = lines[i]
            for pattern in verification_patterns:
                match = re.search(pattern, line)
                if match:
                    return match.group(1).strip()
        return None
    
    def _extract_case_analysis(self, lines: List[str], start_index: int) -> List[str]:
        """提取案例分析"""
        case_analysis = []
        case_patterns = [
            r'案例[：:]\s*(.+)',
            r'Case[：:]\s*(.+)',
            r'情况[：:]\s*(.+)',
        ]
        
        for i in range(start_index, min(start_index + 15, len(lines))):
            line = lines[i]
            for pattern in case_patterns:
                match = re.search(pattern, line)
                if match:
                    case_analysis.append(match.group(1).strip())
                    break
        return case_analysis

class SemanticAnalyzer:
    """语义分析器，负责分析文档语义内容"""
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化语义分析器"""
        self.config = config or {}
        
    def analyze_concept_definitions(self, concepts: List[Concept]) -> Dict[str, Any]:
        """分析概念定义的完整性"""
        logger.info("开始分析概念定义完整性")
        
        analysis_results = {
            'total_concepts': len(concepts),
            'complete_definitions': 0,
            'incomplete_definitions': 0,
            'missing_formal_definitions': 0,
            'missing_examples': 0,
            'missing_counterexamples': 0,
            'concept_details': []
        }
        
        for concept in concepts:
            concept_detail = {
                'name': concept.name,
                'definition_quality': self._assess_definition_quality(concept),
                'completeness_score': self._calculate_completeness_score(concept),
                'missing_elements': self._identify_missing_elements(concept),
                'improvement_suggestions': self._generate_improvement_suggestions(concept)
            }
            
            analysis_results['concept_details'].append(concept_detail)
            
            # 统计
            if concept_detail['completeness_score'] >= 0.8:
                analysis_results['complete_definitions'] += 1
            else:
                analysis_results['incomplete_definitions'] += 1
                
            if not concept.formal_definition:
                analysis_results['missing_formal_definitions'] += 1
                
            if not concept.examples:
                analysis_results['missing_examples'] += 1
                
            if not concept.counterexamples:
                analysis_results['missing_counterexamples'] += 1
        
        logger.info(f"概念定义分析完成，完整定义: {analysis_results['complete_definitions']}/{analysis_results['total_concepts']}")
        return analysis_results
    
    def _assess_definition_quality(self, concept: Concept) -> str:
        """评估定义质量"""
        if not concept.definition:
            return "缺失"
        
        # 检查定义长度
        if len(concept.definition) < 10:
            return "过短"
        elif len(concept.definition) > 200:
            return "过长"
        else:
            return "适中"
    
    def _calculate_completeness_score(self, concept: Concept) -> float:
        """计算完整性得分"""
        score = 0.0
        
        # 基础定义 (40%)
        if concept.definition:
            score += 0.4
        
        # 形式化定义 (20%)
        if concept.formal_definition:
            score += 0.2
        
        # 属性 (15%)
        if concept.properties:
            score += 0.15
        
        # 关系 (10%)
        if concept.relations:
            score += 0.1
        
        # 示例 (10%)
        if concept.examples:
            score += 0.1
        
        # 反例 (5%)
        if concept.counterexamples:
            score += 0.05
        
        return score
    
    def _identify_missing_elements(self, concept: Concept) -> List[str]:
        """识别缺失元素"""
        missing = []
        
        if not concept.definition:
            missing.append("基础定义")
        
        if not concept.formal_definition:
            missing.append("形式化定义")
        
        if not concept.properties:
            missing.append("属性描述")
        
        if not concept.relations:
            missing.append("关系描述")
        
        if not concept.examples:
            missing.append("示例")
        
        if not concept.counterexamples:
            missing.append("反例")
        
        return missing
    
    def _generate_improvement_suggestions(self, concept: Concept) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if not concept.definition:
            suggestions.append("添加清晰的概念定义")
        
        if not concept.formal_definition:
            suggestions.append("添加数学形式化定义")
        
        if not concept.properties:
            suggestions.append("列举概念的关键属性")
        
        if not concept.relations:
            suggestions.append("描述与其他概念的关系")
        
        if not concept.examples:
            suggestions.append("提供具体示例")
        
        if not concept.counterexamples:
            suggestions.append("提供反例以明确边界")
        
        return suggestions

def main():
    """主函数，演示工具使用"""
    # 初始化工具
    parser = DocumentParser()
    analyzer = SemanticAnalyzer()
    
    # 读取示例文档
    sample_content = """
# 形式语法归约

## 1. 理论基础深化

### 1.1 形式语法的层次结构深化

#### 1.1.1 正则语法（Regular Grammar）深化

**数学定义深化**：G = (V, Σ, P, S, F)，其中V是非终结符集合，Σ是终结符集合，P是产生式规则集合，S是起始符号，F是接受状态集合

**自动机对应深化**：有限状态自动机（DFA/NFA）与ε-NFA

**表达能力深化**：只能描述有限状态的语言模式，具有线性时间复杂性

**应用场景深化**：词法分析、模式匹配、简单文本处理、正则表达式引擎

**形式化性质深化**：在并集、连接、Kleene星号运算下封闭

**最小化算法深化**：Hopcroft算法的时间复杂度为O(n log n)

**等价性判定深化**：两个正则语言的等价性可以在多项式时间内判定

**泵引理深化**：用于证明语言不是正则的强有力工具
"""
    
    # 解析文档
    structure = parser.parse_structure(sample_content)
    
    # 提取概念、操作、论证
    concepts = parser.extract_concepts(sample_content)
    operations = parser.extract_operations(sample_content)
    arguments = parser.extract_arguments(sample_content)
    
    # 分析语义
    concept_analysis = analyzer.analyze_concept_definitions(concepts)
    
    # 输出结果
    print("=== 文档结构分析 ===")
    print(f"标题: {structure.title}")
    print(f"章节数: {len(structure.sections)}")
    print(f"代码块数: {len(structure.code_blocks)}")
    print(f"数学公式数: {len(structure.math_formulas)}")
    print(f"链接数: {len(structure.links)}")
    
    print("\n=== 概念分析 ===")
    print(f"概念总数: {concept_analysis['total_concepts']}")
    print(f"完整定义: {concept_analysis['complete_definitions']}")
    print(f"不完整定义: {concept_analysis['incomplete_definitions']}")
    
    print("\n=== 操作分析 ===")
    print(f"操作总数: {len(operations)}")
    
    print("\n=== 论证分析 ===")
    print(f"论证总数: {len(arguments)}")

if __name__ == "__main__":
    main()
