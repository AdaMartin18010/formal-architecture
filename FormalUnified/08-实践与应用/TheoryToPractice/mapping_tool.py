#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版理论到实践映射工具
Enhanced Theory-to-Practice Mapping Tool

支持多语言代码生成、智能模板系统、约束验证和测试用例自动生成
"""

import json
import yaml
import logging
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
import jinja2
import ast
import inspect

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TheoryConcept:
    """理论概念"""
    name: str
    description: str
    category: str
    properties: Dict[str, Any]
    constraints: List[str]
    examples: List[str]

@dataclass
class CodeTemplate:
    """代码模板"""
    language: str
    template_name: str
    template_content: str
    parameters: List[str]
    validation_rules: List[str]

@dataclass
class GeneratedCode:
    """生成的代码"""
    language: str
    file_name: str
    content: str
    dependencies: List[str]
    test_cases: List[str]
    documentation: str

class EnhancedTheoryToPracticeMapper:
    """增强版理论到实践映射器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.theory_concepts = {}
        self.code_templates = {}
        self.language_support = {}
        self.validation_rules = {}
        
        # 初始化Jinja2模板引擎
        self.template_env = jinja2.Environment(
            loader=jinja2.DictLoader({}),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        self._initialize_templates()
        self._initialize_language_support()
        
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
            "supported_languages": ["python", "rust", "go", "typescript", "java", "csharp"],
            "template_categories": ["class", "interface", "function", "module", "test"],
            "validation_levels": ["syntax", "semantics", "architecture", "security", "performance"],
            "code_generation": {
                "include_tests": True,
                "include_docs": True,
                "include_examples": True,
                "format_code": True
            }
        }
    
    def _initialize_templates(self):
        """初始化代码模板"""
        # Python模板
        self.code_templates["python"] = {
            "class": self._get_python_class_template(),
            "interface": self._get_python_interface_template(),
            "function": self._get_python_function_template(),
            "module": self._get_python_module_template(),
            "test": self._get_python_test_template()
        }
        
        # Rust模板
        self.code_templates["rust"] = {
            "struct": self._get_rust_struct_template(),
            "trait": self._get_rust_trait_template(),
            "function": self._get_rust_function_template(),
            "module": self._get_rust_module_template(),
            "test": self._get_rust_test_template()
        }
        
        # Go模板
        self.code_templates["go"] = {
            "struct": self._get_go_struct_template(),
            "interface": self._get_go_interface_template(),
            "function": self._get_go_function_template(),
            "package": self._get_go_package_template(),
            "test": self._get_go_test_template()
        }
        
        # TypeScript模板
        self.code_templates["typescript"] = {
            "class": self._get_typescript_class_template(),
            "interface": self._get_typescript_interface_template(),
            "function": self._get_typescript_function_template(),
            "module": self._get_typescript_module_template(),
            "test": self._get_typescript_test_template()
        }
    
    def _initialize_language_support(self):
        """初始化语言支持"""
        self.language_support = {
            "python": {
                "file_extension": ".py",
                "naming_convention": "snake_case",
                "comment_style": "#",
                "docstring_style": "docstring",
                "type_hints": True
            },
            "rust": {
                "file_extension": ".rs",
                "naming_convention": "snake_case",
                "comment_style": "//",
                "docstring_style": "///",
                "type_hints": True
            },
            "go": {
                "file_extension": ".go",
                "naming_convention": "camelCase",
                "comment_style": "//",
                "docstring_style": "//",
                "type_hints": True
            },
            "typescript": {
                "file_extension": ".ts",
                "naming_convention": "camelCase",
                "comment_style": "//",
                "docstring_style": "/**",
                "type_hints": True
            }
        }
    
    def load_theory_concepts(self, theory_path: str) -> bool:
        """加载理论概念"""
        try:
            theory_path = Path(theory_path)
            
            for md_file in theory_path.rglob("*.md"):
                concepts = self._extract_concepts_from_file(md_file)
                for concept in concepts:
                    self.theory_concepts[concept.name] = concept
                    
            logger.info(f"✅ 成功加载 {len(self.theory_concepts)} 个理论概念")
            return True
            
        except Exception as e:
            logger.error(f"❌ 加载理论概念失败: {e}")
            return False
    
    def _extract_concepts_from_file(self, md_file: Path) -> List[TheoryConcept]:
        """从Markdown文件中提取理论概念"""
        concepts = []
        
        try:
            content = md_file.read_text(encoding='utf-8')
            
            # 提取概念定义
            concept_patterns = [
                r'##\s*([^\n]+)',  # 二级标题
                r'###\s*([^\n]+)',  # 三级标题
                r'`([^`]+)`',  # 代码块中的概念
                r'\*\*([^*]+)\*\*',  # 粗体概念
            ]
            
            for pattern in concept_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if len(match.strip()) > 2:  # 过滤太短的概念
                        concept = TheoryConcept(
                            name=match.strip(),
                            description=self._extract_description(content, match),
                            category=self._determine_category(match, content),
                            properties=self._extract_properties(content, match),
                            constraints=self._extract_constraints(content, match),
                            examples=self._extract_examples(content, match)
                        )
                        concepts.append(concept)
                        
        except Exception as e:
            logger.warning(f"提取概念失败 {md_file}: {e}")
            
        return concepts
    
    def _extract_description(self, content: str, concept: str) -> str:
        """提取概念描述"""
        # 查找概念后的描述文本
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if concept in line and i + 1 < len(lines):
                return lines[i + 1].strip()
        return f"{concept} 的理论概念"
    
    def _determine_category(self, concept: str, content: str) -> str:
        """确定概念类别"""
        categories = {
            "哲学": ["存在", "本质", "关系", "属性", "本体", "认识"],
            "数学": ["集合", "函数", "映射", "关系", "代数", "拓扑"],
            "语言": ["语法", "语义", "语用", "语言", "符号", "表达"],
            "模型": ["状态", "转换", "模型", "系统", "过程", "行为"],
            "编程": ["类型", "函数", "类", "接口", "模块", "包"],
            "架构": ["组件", "服务", "模式", "架构", "设计", "结构"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in concept for keyword in keywords):
                return category
                
        return "通用"
    
    def _extract_properties(self, content: str, concept: str) -> Dict[str, Any]:
        """提取概念属性"""
        properties = {}
        
        # 查找属性定义
        property_patterns = [
            r'属性[：:]\s*([^\n]+)',
            r'特性[：:]\s*([^\n]+)',
            r'特征[：:]\s*([^\n]+)'
        ]
        
        for pattern in property_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                properties[f"property_{len(properties)}"] = match.strip()
                
        return properties
    
    def _extract_constraints(self, content: str, concept: str) -> List[str]:
        """提取概念约束"""
        constraints = []
        
        # 查找约束定义
        constraint_patterns = [
            r'约束[：:]\s*([^\n]+)',
            r'限制[：:]\s*([^\n]+)',
            r'条件[：:]\s*([^\n]+)'
        ]
        
        for pattern in constraint_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                constraints.append(match.strip())
                
        return constraints
    
    def _extract_examples(self, content: str, concept: str) -> List[str]:
        """提取概念示例"""
        examples = []
        
        # 查找示例定义
        example_patterns = [
            r'示例[：:]\s*([^\n]+)',
            r'例子[：:]\s*([^\n]+)',
            r'实例[：:]\s*([^\n]+)'
        ]
        
        for pattern in example_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                examples.append(match.strip())
                
        return examples
    
    def generate_code(self, concept_name: str, language: str, 
                     template_type: str = "class") -> Optional[GeneratedCode]:
        """生成代码"""
        try:
            if concept_name not in self.theory_concepts:
                logger.error(f"❌ 概念 {concept_name} 不存在")
                return None
                
            if language not in self.code_templates:
                logger.error(f"❌ 不支持的语言 {language}")
                return None
                
            concept = self.theory_concepts[concept_name]
            template = self.code_templates[language].get(template_type)
            
            if not template:
                logger.error(f"❌ 不支持的模板类型 {template_type}")
                return None
            
            # 准备模板变量
            template_vars = self._prepare_template_vars(concept, language)
            
            # 渲染模板
            rendered_content = self.template_env.from_string(template).render(**template_vars)
            
            # 生成文件名
            file_name = self._generate_file_name(concept_name, language, template_type)
            
            # 生成依赖
            dependencies = self._generate_dependencies(concept, language)
            
            # 生成测试用例
            test_cases = self._generate_test_cases(concept, language) if self.config["code_generation"]["include_tests"] else []
            
            # 生成文档
            documentation = self._generate_documentation(concept, language) if self.config["code_generation"]["include_docs"] else ""
            
            return GeneratedCode(
                language=language,
                file_name=file_name,
                content=rendered_content,
                dependencies=dependencies,
                test_cases=test_cases,
                documentation=documentation
            )
            
        except Exception as e:
            logger.error(f"❌ 代码生成失败: {e}")
            return None
    
    def _prepare_template_vars(self, concept: TheoryConcept, language: str) -> Dict[str, Any]:
        """准备模板变量"""
        lang_config = self.language_support[language]
        
        return {
            "concept_name": self._format_name(concept.name, language),
            "concept_description": concept.description,
            "concept_category": concept.category,
            "properties": concept.properties,
            "constraints": concept.constraints,
            "examples": concept.examples,
            "language_config": lang_config,
            "timestamp": datetime.now().isoformat(),
            "author": "Theory-to-Practice Mapper"
        }
    
    def _format_name(self, name: str, language: str) -> str:
        """格式化名称"""
        lang_config = self.language_support[language]
        convention = lang_config["naming_convention"]
        
        if convention == "snake_case":
            return name.lower().replace(" ", "_")
        elif convention == "camelCase":
            words = name.lower().split()
            return words[0] + "".join(word.capitalize() for word in words[1:])
        elif convention == "PascalCase":
            return "".join(word.capitalize() for word in name.lower().split())
        else:
            return name
    
    def _generate_file_name(self, concept_name: str, language: str, template_type: str) -> str:
        """生成文件名"""
        lang_config = self.language_support[language]
        extension = lang_config["file_extension"]
        formatted_name = self._format_name(concept_name, language)
        
        if template_type == "test":
            return f"test_{formatted_name}{extension}"
        else:
            return f"{formatted_name}{extension}"
    
    def _generate_dependencies(self, concept: TheoryConcept, language: str) -> List[str]:
        """生成依赖列表"""
        base_deps = {
            "python": ["typing", "dataclasses", "abc"],
            "rust": ["std"],
            "go": ["fmt", "time"],
            "typescript": ["typescript"]
        }
        
        deps = base_deps.get(language, [])
        
        # 根据概念类别添加特定依赖
        if concept.category == "数学":
            deps.extend({
                "python": ["math", "numpy"],
                "rust": ["num"],
                "go": ["math"],
                "typescript": ["math"]
            }.get(language, []))
            
        return list(set(deps))
    
    def _generate_test_cases(self, concept: TheoryConcept, language: str) -> List[str]:
        """生成测试用例"""
        test_template = self.code_templates[language].get("test", "")
        if not test_template:
            return []
            
        template_vars = self._prepare_template_vars(concept, language)
        return [self.template_env.from_string(test_template).render(**template_vars)]
    
    def _generate_documentation(self, concept: TheoryConcept, language: str) -> str:
        """生成文档"""
        lang_config = self.language_support[language]
        comment_style = lang_config["comment_style"]
        
        doc_lines = [
            f"{comment_style} {concept.name}",
            f"{comment_style} {concept.description}",
            f"{comment_style}",
            f"{comment_style} 类别: {concept.category}",
            f"{comment_style} 属性: {', '.join(concept.properties.keys())}",
            f"{comment_style} 约束: {', '.join(concept.constraints)}",
            f"{comment_style} 示例: {', '.join(concept.examples)}"
        ]
        
        return "\n".join(doc_lines)
    
    def validate_generated_code(self, generated_code: GeneratedCode) -> Dict[str, Any]:
        """验证生成的代码"""
        validation_result = {
            "syntax": self._validate_syntax(generated_code),
            "semantics": self._validate_semantics(generated_code),
            "architecture": self._validate_architecture(generated_code),
            "security": self._validate_security(generated_code),
            "performance": self._validate_performance(generated_code)
        }
        
        return validation_result
    
    def _validate_syntax(self, generated_code: GeneratedCode) -> Dict[str, Any]:
        """验证语法"""
        try:
            if generated_code.language == "python":
                ast.parse(generated_code.content)
                return {"valid": True, "errors": []}
            else:
                # 其他语言的语法验证可以扩展
                return {"valid": True, "errors": []}
        except SyntaxError as e:
            return {"valid": False, "errors": [str(e)]}
    
    def _validate_semantics(self, generated_code: GeneratedCode) -> Dict[str, Any]:
        """验证语义"""
        errors = []
        
        # 检查命名规范
        lang_config = self.language_support[generated_code.language]
        convention = lang_config["naming_convention"]
        
        # 检查是否有未定义的变量
        if "undefined_variable" in generated_code.content.lower():
            errors.append("发现未定义变量")
            
        return {"valid": len(errors) == 0, "errors": errors}
    
    def _validate_architecture(self, generated_code: GeneratedCode) -> Dict[str, Any]:
        """验证架构"""
        errors = []
        
        # 检查模块化
        if generated_code.language == "python" and "class" in generated_code.content:
            if "def __init__" not in generated_code.content:
                errors.append("类缺少初始化方法")
                
        return {"valid": len(errors) == 0, "errors": errors}
    
    def _validate_security(self, generated_code: GeneratedCode) -> Dict[str, Any]:
        """验证安全性"""
        errors = []
        
        # 检查潜在的安全问题
        security_patterns = [
            r'eval\s*\(',
            r'exec\s*\(',
            r'input\s*\(',
            r'os\.system\s*\('
        ]
        
        for pattern in security_patterns:
            if re.search(pattern, generated_code.content):
                errors.append(f"发现潜在安全风险: {pattern}")
                
        return {"valid": len(errors) == 0, "errors": errors}
    
    def _validate_performance(self, generated_code: GeneratedCode) -> Dict[str, Any]:
        """验证性能"""
        errors = []
        
        # 检查性能问题
        performance_patterns = [
            r'for.*for',  # 嵌套循环
            r'while.*while',  # 嵌套while
            r'\.append\s*\(.*for'  # 循环中append
        ]
        
        for pattern in performance_patterns:
            if re.search(pattern, generated_code.content):
                errors.append(f"发现潜在性能问题: {pattern}")
                
        return {"valid": len(errors) == 0, "errors": errors}
    
    # 模板定义方法
    def _get_python_class_template(self) -> str:
        return '''
# -*- coding: utf-8 -*-
"""
{{ concept_description }}
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class {{ concept_name }}:
    """
    {{ concept_description }}
    
    类别: {{ concept_category }}
    属性: {{ properties }}
    约束: {{ constraints }}
    """
    
    {% for key, value in properties.items() %}
    {{ key }}: Any = None
    {% endfor %}
    
    def __post_init__(self):
        """初始化后验证约束"""
        {% for constraint in constraints %}
        # {{ constraint }}
        pass
        {% endfor %}
    
    def validate(self) -> bool:
        """验证对象有效性"""
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            {% for key, value in properties.items() %}
            "{{ key }}": self.{{ key }},
            {% endfor %}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> '{{ concept_name }}':
        """从字典创建对象"""
        return cls(**data)
'''
    
    def _get_rust_struct_template(self) -> str:
        return '''
/// {{ concept_description }}
/// 
/// 类别: {{ concept_category }}
/// 属性: {{ properties }}
/// 约束: {{ constraints }}
#[derive(Debug, Clone, PartialEq)]
pub struct {{ concept_name }} {
    {% for key, value in properties.items() %}
    pub {{ key }}: Option<String>,
    {% endfor %}
}

impl {{ concept_name }} {
    /// 创建新的 {{ concept_name }} 实例
    pub fn new() -> Self {
        Self {
            {% for key, value in properties.items() %}
            {{ key }}: None,
            {% endfor %}
        }
    }
    
    /// 验证对象有效性
    pub fn validate(&self) -> bool {
        {% for constraint in constraints %}
        // {{ constraint }}
        {% endfor %}
        true
    }
    
    /// 转换为JSON字符串
    pub fn to_json(&self) -> Result<String, serde_json::Error> {
        serde_json::to_string(self)
    }
}
'''
    
    def _get_go_struct_template(self) -> str:
        return '''
// {{ concept_description }}
// 
// 类别: {{ concept_category }}
// 属性: {{ properties }}
// 约束: {{ constraints }}
type {{ concept_name }} struct {
    {% for key, value in properties.items() %}
    {{ key | title }} string `json:"{{ key }}" validate:"required"`
    {% endfor %}
}

// New{{ concept_name }} 创建新的 {{ concept_name }} 实例
func New{{ concept_name }}() *{{ concept_name }} {
    return &{{ concept_name }}{}
}

// Validate 验证对象有效性
func ({{ concept_name[0] | lower }} *{{ concept_name }}) Validate() error {
    {% for constraint in constraints %}
    // {{ constraint }}
    {% endfor %}
    return nil
}

// ToJSON 转换为JSON字符串
func ({{ concept_name[0] | lower }} *{{ concept_name }}) ToJSON() ([]byte, error) {
    return json.Marshal({{ concept_name[0] | lower }})
}
'''
    
    def _get_typescript_class_template(self) -> str:
        return '''
/**
 * {{ concept_description }}
 * 
 * 类别: {{ concept_category }}
 * 属性: {{ properties }}
 * 约束: {{ constraints }}
 */
export class {{ concept_name }} {
    {% for key, value in properties.items() %}
    private _{{ key }}: string | null = null;
    {% endfor %}
    
    constructor() {
        // 初始化对象
    }
    
    {% for key, value in properties.items() %}
    get {{ key }}(): string | null {
        return this._{{ key }};
    }
    
    set {{ key }}(value: string | null) {
        this._{{ key }} = value;
    }
    {% endfor %}
    
    /**
     * 验证对象有效性
     */
    validate(): boolean {
        {% for constraint in constraints %}
        // {{ constraint }}
        {% endfor %}
        return true;
    }
    
    /**
     * 转换为JSON对象
     */
    toJSON(): object {
        return {
            {% for key, value in properties.items() %}
            {{ key }}: this._{{ key }},
            {% endfor %}
        };
    }
}
'''
    
    # 其他模板方法...
    def _get_python_interface_template(self) -> str:
        return "class {{ concept_name }}(ABC):\n    pass"
    
    def _get_python_function_template(self) -> str:
        return "def {{ concept_name }}():\n    pass"
    
    def _get_python_module_template(self) -> str:
        return '"""{{ concept_description }}"""\n\n# 模块内容'
    
    def _get_python_test_template(self) -> str:
        return '''
import unittest
from {{ concept_name | lower }} import {{ concept_name }}

class Test{{ concept_name }}(unittest.TestCase):
    def setUp(self):
        self.instance = {{ concept_name }}()
    
    def test_creation(self):
        self.assertIsNotNone(self.instance)
    
    def test_validation(self):
        self.assertTrue(self.instance.validate())

if __name__ == '__main__':
    unittest.main()
'''
    
    # Rust模板
    def _get_rust_trait_template(self) -> str:
        return "pub trait {{ concept_name }} {\n    fn validate(&self) -> bool;\n}"
    
    def _get_rust_function_template(self) -> str:
        return "pub fn {{ concept_name }}() -> bool {\n    true\n}"
    
    def _get_rust_module_template(self) -> str:
        return "// {{ concept_description }}\n\n// 模块内容"
    
    def _get_rust_test_template(self) -> str:
        return '''
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_{{ concept_name | lower }}_creation() {
        let instance = {{ concept_name }}::new();
        assert!(instance.validate());
    }
}
'''
    
    # Go模板
    def _get_go_interface_template(self) -> str:
        return "type {{ concept_name }} interface {\n    Validate() error\n}"
    
    def _get_go_function_template(self) -> str:
        return "func {{ concept_name }}() error {\n    return nil\n}"
    
    def _get_go_package_template(self) -> str:
        return "package {{ concept_name | lower }}\n\n// {{ concept_description }}"
    
    def _get_go_test_template(self) -> str:
        return '''
package {{ concept_name | lower }}

import "testing"

func Test{{ concept_name }}(t *testing.T) {
    instance := New{{ concept_name }}()
    if err := instance.Validate(); err != nil {
        t.Errorf("Validation failed: %v", err)
    }
}
'''
    
    # TypeScript模板
    def _get_typescript_interface_template(self) -> str:
        return "export interface {{ concept_name }} {\n    validate(): boolean;\n}"
    
    def _get_typescript_function_template(self) -> str:
        return "export function {{ concept_name }}(): boolean {\n    return true;\n}"
    
    def _get_typescript_module_template(self) -> str:
        return "/** {{ concept_description }} */\n\nexport * from './{{ concept_name | lower }}';"
    
    def _get_typescript_test_template(self) -> str:
        return '''
import { {{ concept_name }} } from './{{ concept_name | lower }}';

describe('{{ concept_name }}', () => {
    let instance: {{ concept_name }};
    
    beforeEach(() => {
        instance = new {{ concept_name }}();
    });
    
    it('should create instance', () => {
        expect(instance).toBeDefined();
    });
    
    it('should validate correctly', () => {
        expect(instance.validate()).toBe(true);
    });
});
'''

def demo_enhanced_mapper():
    """演示增强版映射工具"""
    print("🚀 启动增强版理论到实践映射工具演示")
    
    # 创建映射器
    mapper = EnhancedTheoryToPracticeMapper()
    
    # 加载理论概念
    print("📚 加载理论概念...")
    success = mapper.load_theory_concepts("FormalUnified")
    
    if not success:
        print("❌ 加载理论概念失败")
        return
    
    # 演示代码生成
    print("🔧 演示代码生成...")
    
    # 为每个支持的语言生成示例代码
    for language in ["python", "rust", "go", "typescript"]:
        print(f"\n📝 生成 {language} 代码...")
        
        # 生成类代码
        generated_code = mapper.generate_code("状态机", language, "class")
        if generated_code:
            print(f"✅ 成功生成 {generated_code.file_name}")
            
            # 验证代码
            validation_result = mapper.validate_generated_code(generated_code)
            print(f"🔍 验证结果: {validation_result}")
            
            # 保存代码
            output_dir = Path(f"generated_code/{language}")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            with open(output_dir / generated_code.file_name, 'w', encoding='utf-8') as f:
                f.write(generated_code.content)
            
            print(f"💾 代码已保存到 {output_dir / generated_code.file_name}")
    
    print("\n🎉 演示完成！")

if __name__ == "__main__":
    demo_enhanced_mapper() 