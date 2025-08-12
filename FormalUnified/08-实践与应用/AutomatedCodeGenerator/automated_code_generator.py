#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化代码生成器
Automated Code Generator

支持多种编程语言和架构模式的自动化代码生成工具
"""

import json
import yaml
import logging
import time
import argparse
import sys
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
import jinja2
import re

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CodeTemplate:
    """代码模板"""
    name: str
    language: str
    template_type: str
    content: str
    parameters: List[str]
    dependencies: List[str]

@dataclass
class GeneratedCode:
    """生成的代码"""
    file_name: str
    content: str
    language: str
    dependencies: List[str]
    metadata: Dict[str, Any]

class AutomatedCodeGenerator:
    """自动化代码生成器"""
    
    def __init__(self, config_path: str = "generator_config.yaml"):
        self.config = self._load_config(config_path)
        self.templates = {}
        self.language_support = {}
        
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
            "supported_languages": ["python", "java", "typescript", "rust", "go", "csharp"],
            "architecture_patterns": [
                "mvc", "mvvm", "repository", "factory", "observer", 
                "singleton", "strategy", "command", "adapter"
            ],
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
        self.templates["python"] = {
            "class": self._get_python_class_template(),
            "interface": self._get_python_interface_template(),
            "service": self._get_python_service_template(),
            "repository": self._get_python_repository_template(),
            "controller": self._get_python_controller_template(),
            "test": self._get_python_test_template(),
            "config": self._get_python_config_template()
        }
        
        # Java模板
        self.templates["java"] = {
            "class": self._get_java_class_template(),
            "interface": self._get_java_interface_template(),
            "service": self._get_java_service_template(),
            "repository": self._get_java_repository_template(),
            "controller": self._get_java_controller_template(),
            "test": self._get_java_test_template(),
            "config": self._get_java_config_template()
        }
        
        # TypeScript模板
        self.templates["typescript"] = {
            "class": self._get_typescript_class_template(),
            "interface": self._get_typescript_interface_template(),
            "service": self._get_typescript_service_template(),
            "repository": self._get_typescript_repository_template(),
            "controller": self._get_typescript_controller_template(),
            "test": self._get_typescript_test_template(),
            "config": self._get_typescript_config_template()
        }
        
        # Rust模板
        self.templates["rust"] = {
            "struct": self._get_rust_struct_template(),
            "trait": self._get_rust_trait_template(),
            "service": self._get_rust_service_template(),
            "repository": self._get_rust_repository_template(),
            "controller": self._get_rust_controller_template(),
            "test": self._get_rust_test_template(),
            "config": self._get_rust_config_template()
        }
    
    def _initialize_language_support(self):
        """初始化语言支持"""
        self.language_support = {
            "python": {
                "file_extension": ".py",
                "naming_convention": "snake_case",
                "comment_style": "#",
                "docstring_style": '"""',
                "type_hints": True
            },
            "java": {
                "file_extension": ".java",
                "naming_convention": "PascalCase",
                "comment_style": "//",
                "docstring_style": "/**",
                "type_hints": True
            },
            "typescript": {
                "file_extension": ".ts",
                "naming_convention": "camelCase",
                "comment_style": "//",
                "docstring_style": "/**",
                "type_hints": True
            },
            "rust": {
                "file_extension": ".rs",
                "naming_convention": "snake_case",
                "comment_style": "//",
                "docstring_style": "///",
                "type_hints": True
            }
        }
    
    def generate_code(self, specification: Dict[str, Any], 
                     language: str, output_dir: Optional[str] = None) -> List[GeneratedCode]:
        """生成代码"""
        try:
            if language not in self.templates:
                raise ValueError(f"不支持的语言: {language}")
            
            generated_files = []
            
            # 解析规范
            entities = specification.get("entities", [])
            services = specification.get("services", [])
            controllers = specification.get("controllers", [])
            repositories = specification.get("repositories", [])
            
            # 生成实体类
            for entity in entities:
                code = self._generate_entity(entity, language)
                generated_files.append(code)
            
            # 生成服务类
            for service in services:
                code = self._generate_service(service, language)
                generated_files.append(code)
            
            # 生成控制器
            for controller in controllers:
                code = self._generate_controller(controller, language)
                generated_files.append(code)
            
            # 生成仓储类
            for repository in repositories:
                code = self._generate_repository(repository, language)
                generated_files.append(code)
            
            # 生成配置文件
            config_code = self._generate_config(specification, language)
            generated_files.append(config_code)
            
            # 生成测试文件
            if self.config["code_generation"]["include_tests"]:
                test_code = self._generate_tests(specification, language)
                generated_files.append(test_code)
            
            # 保存文件
            if output_dir:
                self._save_files(generated_files, output_dir)
            
            return generated_files
            
        except Exception as e:
            logger.error(f"❌ 代码生成失败: {e}")
            return []
    
    def _generate_entity(self, entity: Dict[str, Any], language: str) -> GeneratedCode:
        """生成实体类"""
        # Rust使用struct，其他语言使用class
        template_key = "struct" if language == "rust" else "class"
        template = self.templates[language][template_key]
        
        # 准备模板变量
        template_vars = {
            "class_name": entity["name"],
            "properties": entity.get("properties", []),
            "methods": entity.get("methods", []),
            "language_config": self.language_support[language],
            "timestamp": datetime.now().isoformat()
        }
        
        # 渲染模板
        content = self.template_env.from_string(template).render(**template_vars)
        
        # 生成文件名
        file_name = f"{entity['name'].lower()}.{self.language_support[language]['file_extension']}"
        
        return GeneratedCode(
            file_name=file_name,
            content=content,
            language=language,
            dependencies=self._get_entity_dependencies(entity, language),
            metadata={"type": "entity", "entity_name": entity["name"]}
        )
    
    def _generate_service(self, service: Dict[str, Any], language: str) -> GeneratedCode:
        """生成服务类"""
        template = self.templates[language]["service"]
        
        template_vars = {
            "service_name": service["name"],
            "methods": service.get("methods", []),
            "dependencies": service.get("dependencies", []),
            "language_config": self.language_support[language],
            "timestamp": datetime.now().isoformat()
        }
        
        content = self.template_env.from_string(template).render(**template_vars)
        file_name = f"{service['name'].lower()}_service.{self.language_support[language]['file_extension']}"
        
        return GeneratedCode(
            file_name=file_name,
            content=content,
            language=language,
            dependencies=self._get_service_dependencies(service, language),
            metadata={"type": "service", "service_name": service["name"]}
        )
    
    def _generate_controller(self, controller: Dict[str, Any], language: str) -> GeneratedCode:
        """生成控制器"""
        template = self.templates[language]["controller"]
        
        template_vars = {
            "controller_name": controller["name"],
            "endpoints": controller.get("endpoints", []),
            "dependencies": controller.get("dependencies", []),
            "language_config": self.language_support[language],
            "timestamp": datetime.now().isoformat()
        }
        
        content = self.template_env.from_string(template).render(**template_vars)
        file_name = f"{controller['name'].lower()}_controller.{self.language_support[language]['file_extension']}"
        
        return GeneratedCode(
            file_name=file_name,
            content=content,
            language=language,
            dependencies=self._get_controller_dependencies(controller, language),
            metadata={"type": "controller", "controller_name": controller["name"]}
        )
    
    def _generate_repository(self, repository: Dict[str, Any], language: str) -> GeneratedCode:
        """生成仓储类"""
        template = self.templates[language]["repository"]
        
        template_vars = {
            "repository_name": repository["name"],
            "entity_name": repository.get("entity", "Entity"),
            "methods": repository.get("methods", []),
            "language_config": self.language_support[language],
            "timestamp": datetime.now().isoformat()
        }
        
        content = self.template_env.from_string(template).render(**template_vars)
        file_name = f"{repository['name'].lower()}_repository.{self.language_support[language]['file_extension']}"
        
        return GeneratedCode(
            file_name=file_name,
            content=content,
            language=language,
            dependencies=self._get_repository_dependencies(repository, language),
            metadata={"type": "repository", "repository_name": repository["name"]}
        )
    
    def _generate_config(self, specification: Dict[str, Any], language: str) -> GeneratedCode:
        """生成配置文件"""
        template = self.templates[language]["config"]
        
        template_vars = {
            "app_name": specification.get("name", "Application"),
            "version": specification.get("version", "1.0.0"),
            "database": specification.get("database", {}),
            "language_config": self.language_support[language],
            "timestamp": datetime.now().isoformat()
        }
        
        content = self.template_env.from_string(template).render(**template_vars)
        file_name = f"config.{self.language_support[language]['file_extension']}"
        
        return GeneratedCode(
            file_name=file_name,
            content=content,
            language=language,
            dependencies=[],
            metadata={"type": "config"}
        )
    
    def _generate_tests(self, specification: Dict[str, Any], language: str) -> GeneratedCode:
        """生成测试文件"""
        template = self.templates[language]["test"]
        
        template_vars = {
            "entities": specification.get("entities", []),
            "services": specification.get("services", []),
            "language_config": self.language_support[language],
            "timestamp": datetime.now().isoformat()
        }
        
        content = self.template_env.from_string(template).render(**template_vars)
        file_name = f"test_main.{self.language_support[language]['file_extension']}"
        
        return GeneratedCode(
            file_name=file_name,
            content=content,
            language=language,
            dependencies=[],
            metadata={"type": "test"}
        )
    
    def _save_files(self, generated_files: List[GeneratedCode], output_dir: str):
        """保存生成的文件"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for code_file in generated_files:
            file_path = output_path / code_file.file_name
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code_file.content)
            logger.info(f"✅ 保存文件: {file_path}")
    
    # 依赖分析方法
    def _get_entity_dependencies(self, entity: Dict[str, Any], language: str) -> List[str]:
        """获取实体依赖"""
        base_deps = {
            "python": ["dataclasses", "typing"],
            "java": ["java.util"],
            "typescript": [],
            "rust": ["serde"]
        }
        return base_deps.get(language, [])
    
    def _get_service_dependencies(self, service: Dict[str, Any], language: str) -> List[str]:
        """获取服务依赖"""
        base_deps = {
            "python": ["typing", "abc"],
            "java": ["java.util", "java.util.List"],
            "typescript": [],
            "rust": ["std"]
        }
        return base_deps.get(language, [])
    
    def _get_controller_dependencies(self, controller: Dict[str, Any], language: str) -> List[str]:
        """获取控制器依赖"""
        base_deps = {
            "python": ["flask", "json"],
            "java": ["org.springframework.web.bind.annotation"],
            "typescript": ["express"],
            "rust": ["actix_web"]
        }
        return base_deps.get(language, [])
    
    def _get_repository_dependencies(self, repository: Dict[str, Any], language: str) -> List[str]:
        """获取仓储依赖"""
        base_deps = {
            "python": ["sqlalchemy"],
            "java": ["org.springframework.data.repository"],
            "typescript": [],
            "rust": ["sqlx"]
        }
        return base_deps.get(language, [])
    
    # 模板定义方法
    def _get_python_class_template(self) -> str:
        return '''"""
{{ class_name }} 实体类
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
{% for dep in dependencies %}
import {{ dep }}
{% endfor %}

@dataclass
class {{ class_name }}:
    """
    {{ class_name }} 实体类
    
    创建时间: {{ timestamp }}
    """
    
    {% for prop in properties %}
    {{ prop.name }}: {{ prop.type }} = {{ prop.default_value }}
    {% endfor %}
    
    def __post_init__(self):
        """初始化后验证"""
        pass
    
    {% for method in methods %}
    def {{ method.name }}(self{% for param in method.parameters %}, {{ param.name }}: {{ param.type }}{% endfor %}) -> {{ method.return_type }}:
        """
        {{ method.description }}
        """
        # TODO: 实现方法逻辑
        pass
    {% endfor %}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            {% for prop in properties %}
            "{{ prop.name }}": self.{{ prop.name }},
            {% endfor %}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> '{{ class_name }}':
        """从字典创建实例"""
        return cls(**data)
'''
    
    def _get_python_service_template(self) -> str:
        return '''"""
{{ service_name }} 服务类
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
{% for dep in dependencies %}
import {{ dep }}
{% endfor %}

class {{ service_name }}Service(ABC):
    """
    {{ service_name }} 服务接口
    """
    
    {% for method in methods %}
    @abstractmethod
    def {{ method.name }}(self{% for param in method.parameters %}, {{ param.name }}: {{ param.type }}{% endfor %}) -> {{ method.return_type }}:
        """
        {{ method.description }}
        """
        pass
    {% endfor %}

class {{ service_name }}ServiceImpl({{ service_name }}Service):
    """
    {{ service_name }} 服务实现
    """
    
    def __init__(self{% for dep in dependencies %}, {{ dep.lower() }}_repository{% endfor %}):
        {% for dep in dependencies %}
        self.{{ dep.lower() }}_repository = {{ dep.lower() }}_repository
        {% endfor %}
    
    {% for method in methods %}
    def {{ method.name }}(self{% for param in method.parameters %}, {{ param.name }}: {{ param.type }}{% endfor %}) -> {{ method.return_type }}:
        """
        {{ method.description }}
        """
        # TODO: 实现业务逻辑
        pass
    {% endfor %}
'''
    
    def _get_python_controller_template(self) -> str:
        return '''"""
{{ controller_name }} 控制器
"""

from flask import Flask, request, jsonify
from typing import Dict, Any
{% for dep in dependencies %}
import {{ dep }}
{% endfor %}

app = Flask(__name__)

class {{ controller_name }}Controller:
    """
    {{ controller_name }} 控制器
    """
    
    def __init__(self{% for dep in dependencies %}, {{ dep.lower() }}_service{% endfor %}):
        {% for dep in dependencies %}
        self.{{ dep.lower() }}_service = {{ dep.lower() }}_service
        {% endfor %}
    
    {% for endpoint in endpoints %}
    @app.route('{{ endpoint.path }}', methods=['{{ endpoint.method }}'])
    def {{ endpoint.name }}(self):
        """
        {{ endpoint.description }}
        """
        try:
            # TODO: 实现端点逻辑
            return jsonify({"message": "{{ endpoint.name }} endpoint"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    {% endfor %}
'''
    
    def _get_python_repository_template(self) -> str:
        return '''"""
{{ repository_name }} 仓储类
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from {{ entity_name.lower() }} import {{ entity_name }}

class {{ repository_name }}Repository:
    """
    {{ repository_name }} 仓储实现
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    {% for method in methods %}
    def {{ method.name }}(self{% for param in method.parameters %}, {{ param.name }}: {{ param.type }}{% endfor %}) -> {{ method.return_type }}:
        """
        {{ method.description }}
        """
        # TODO: 实现数据库操作
        pass
    {% endfor %}
'''
    
    def _get_python_test_template(self) -> str:
        return '''"""
测试文件
"""

import unittest
from unittest.mock import Mock, patch

{% for entity in entities %}
from {{ entity.name.lower() }} import {{ entity.name }}
{% endfor %}

{% for service in services %}
from {{ service.name.lower() }}_service import {{ service.name }}Service, {{ service.name }}ServiceImpl
{% endfor %}

class TestEntities(unittest.TestCase):
    """实体类测试"""
    
    {% for entity in entities %}
    def test_{{ entity.name.lower() }}_creation(self):
        """测试 {{ entity.name }} 创建"""
        # TODO: 实现测试
        pass
    {% endfor %}

class TestServices(unittest.TestCase):
    """服务类测试"""
    
    {% for service in services %}
    def test_{{ service.name.lower() }}_service(self):
        """测试 {{ service.name }} 服务"""
        # TODO: 实现测试
        pass
    {% endfor %}

if __name__ == '__main__':
    unittest.main()
'''
    
    def _get_python_config_template(self) -> str:
        return '''"""
配置文件
"""

import os
from typing import Dict, Any

class Config:
    """
    应用配置
    """
    
    # 应用信息
    APP_NAME = "{{ app_name }}"
    APP_VERSION = "{{ version }}"
    
    # 数据库配置
    DATABASE_URL = "{{ database.url }}"
    DATABASE_USERNAME = "{{ database.username }}"
    DATABASE_PASSWORD = "{{ database.password }}"
    
    # 其他配置
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    
    @classmethod
    def get_database_config(cls) -> Dict[str, Any]:
        """获取数据库配置"""
        return {
            "url": cls.DATABASE_URL,
            "username": cls.DATABASE_USERNAME,
            "password": cls.DATABASE_PASSWORD
        }
'''
    
    # Java模板
    def _get_java_class_template(self) -> str:
        return '''package com.example.entity;

import java.util.Objects;
{% for dep in dependencies %}
import {{ dep }};
{% endfor %}

/**
 * {{ class_name }} 实体类
 * 
 * 创建时间: {{ timestamp }}
 */
public class {{ class_name }} {
    
    {% for prop in properties %}
    private {{ prop.type }} {{ prop.name }};
    {% endfor %}
    
    // 构造函数
    public {{ class_name }}() {
    }
    
    public {{ class_name }}({% for prop in properties %}{{ prop.type }} {{ prop.name }}{% if not loop.last %}, {% endif %}{% endfor %}) {
        {% for prop in properties %}
        this.{{ prop.name }} = {{ prop.name }};
        {% endfor %}
    }
    
    // Getter和Setter方法
    {% for prop in properties %}
    public {{ prop.type }} get{{ prop.name | title }}() {
        return {{ prop.name }};
    }
    
    public void set{{ prop.name | title }}({{ prop.type }} {{ prop.name }}) {
        this.{{ prop.name }} = {{ prop.name }};
    }
    {% endfor %}
    
    // 业务方法
    {% for method in methods %}
    public {{ method.return_type }} {{ method.name }}({% for param in method.parameters %}{{ param.type }} {{ param.name }}{% if not loop.last %}, {% endif %}{% endfor %}) {
        // TODO: 实现方法逻辑
        return null;
    }
    {% endfor %}
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        {{ class_name }} that = ({{ class_name }}) o;
        return Objects.equals(id, that.id);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(id);
    }
    
    @Override
    public String toString() {
        return "{{ class_name }}{" +
                {% for prop in properties %}
                "{{ prop.name }}=" + {{ prop.name }} +{% if not loop.last %}, {% endif %}
                {% endfor %}
                '}';
    }
}
'''
    
    # TypeScript模板
    def _get_typescript_class_template(self) -> str:
        return '''/**
 * {{ class_name }} 实体类
 * 
 * 创建时间: {{ timestamp }}
 */

{% for dep in dependencies %}
import { {{ dep }} } from '{{ dep.lower() }}';
{% endfor %}

export class {{ class_name }} {
    {% for prop in properties %}
    private _{{ prop.name }}: {{ prop.type }} = {{ prop.default_value }};
    {% endfor %}
    
    constructor({% for prop in properties %}{{ prop.name }}?: {{ prop.type }}{% if not loop.last %}, {% endif %}{% endfor %}) {
        {% for prop in properties %}
        if ({{ prop.name }} !== undefined) {
            this._{{ prop.name }} = {{ prop.name }};
        }
        {% endfor %}
    }
    
    // Getter方法
    {% for prop in properties %}
    get {{ prop.name }}(): {{ prop.type }} {
        return this._{{ prop.name }};
    }
    {% endfor %}
    
    // Setter方法
    {% for prop in properties %}
    set {{ prop.name }}(value: {{ prop.type }}) {
        this._{{ prop.name }} = value;
    }
    {% endfor %}
    
    // 业务方法
    {% for method in methods %}
    {{ method.name }}({% for param in method.parameters %}{{ param.name }}: {{ param.type }}{% if not loop.last %}, {% endif %}{% endfor %}): {{ method.return_type }} {
        // TODO: 实现方法逻辑
        return null;
    }
    {% endfor %}
    
    // 工具方法
    toJSON(): object {
        return {
            {% for prop in properties %}
            {{ prop.name }}: this._{{ prop.name }},
            {% endfor %}
        };
    }
    
    static fromJSON(data: any): {{ class_name }} {
        return new {{ class_name }}(data);
    }
}
'''
    
    # Rust模板
    def _get_rust_struct_template(self) -> str:
        return '''use serde::{Deserialize, Serialize};
{% for dep in dependencies %}
use {{ dep }};
{% endfor %}

/// {{ class_name }} 实体结构体
/// 
/// 创建时间: {{ timestamp }}
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct {{ class_name }} {
    {% for prop in properties %}
    pub {{ prop.name }}: {{ prop.type }},
    {% endfor %}
}

impl {{ class_name }} {
    /// 创建新的 {{ class_name }} 实例
    pub fn new({% for prop in properties %}{{ prop.name }}: {{ prop.type }}{% if not loop.last %}, {% endif %}{% endfor %}) -> Self {
        Self {
            {% for prop in properties %}
            {{ prop.name }},
            {% endfor %}
        }
    }
    
    {% for method in methods %}
    /// {{ method.description }}
    pub fn {{ method.name }}(&self{% for param in method.parameters %}, {{ param.name }}: {{ param.type }}{% endfor %}) -> {{ method.return_type }} {
        // TODO: 实现方法逻辑
        todo!()
    }
    {% endfor %}
}

impl Default for {{ class_name }} {
    fn default() -> Self {
        Self {
            {% for prop in properties %}
            {{ prop.name }}: {{ prop.default_value }},
            {% endfor %}
        }
    }
}
'''
    
    # 其他模板方法（简化版）
    def _get_python_interface_template(self) -> str:
        return "from abc import ABC, abstractmethod\n\nclass {{ interface_name }}(ABC):\n    pass"
    
    def _get_java_interface_template(self) -> str:
        return "public interface {{ interface_name }} {\n    // TODO: 定义接口方法\n}"
    
    def _get_typescript_interface_template(self) -> str:
        return "export interface {{ interface_name }} {\n    // TODO: 定义接口属性\n}"
    
    def _get_rust_trait_template(self) -> str:
        return "pub trait {{ trait_name }} {\n    // TODO: 定义特征方法\n}"
    
    # 其他模板（简化版）
    def _get_java_service_template(self) -> str:
        return "public class {{ service_name }}Service {\n    // TODO: 实现服务逻辑\n}"
    
    def _get_java_controller_template(self) -> str:
        return "@RestController\npublic class {{ controller_name }}Controller {\n    // TODO: 实现控制器逻辑\n}"
    
    def _get_java_repository_template(self) -> str:
        return "public interface {{ repository_name }}Repository extends JpaRepository<{{ entity_name }}, Long> {\n    // TODO: 定义仓储方法\n}"
    
    def _get_java_test_template(self) -> str:
        return "@Test\npublic class {{ test_name }}Test {\n    // TODO: 实现测试逻辑\n}"
    
    def _get_java_config_template(self) -> str:
        return "@Configuration\npublic class {{ config_name }}Config {\n    // TODO: 实现配置逻辑\n}"
    
    def _get_typescript_service_template(self) -> str:
        return "export class {{ service_name }}Service {\n    // TODO: 实现服务逻辑\n}"
    
    def _get_typescript_controller_template(self) -> str:
        return "export class {{ controller_name }}Controller {\n    // TODO: 实现控制器逻辑\n}"
    
    def _get_typescript_repository_template(self) -> str:
        return "export class {{ repository_name }}Repository {\n    // TODO: 实现仓储逻辑\n}"
    
    def _get_typescript_test_template(self) -> str:
        return "describe('{{ test_name }}', () => {\n    // TODO: 实现测试逻辑\n});"
    
    def _get_typescript_config_template(self) -> str:
        return "export const config = {\n    // TODO: 实现配置逻辑\n};"
    
    def _get_rust_service_template(self) -> str:
        return "pub struct {{ service_name }}Service {\n    // TODO: 实现服务逻辑\n}"
    
    def _get_rust_controller_template(self) -> str:
        return "pub struct {{ controller_name }}Controller {\n    // TODO: 实现控制器逻辑\n}"
    
    def _get_rust_repository_template(self) -> str:
        return "pub struct {{ repository_name }}Repository {\n    // TODO: 实现仓储逻辑\n}"
    
    def _get_rust_test_template(self) -> str:
        return "#[cfg(test)]\nmod tests {\n    // TODO: 实现测试逻辑\n}"
    
    def _get_rust_config_template(self) -> str:
        return "pub struct Config {\n    // TODO: 实现配置逻辑\n}"

def demo_automated_code_generator():
    """演示自动化代码生成器"""
    print("🚀 启动自动化代码生成器演示")
    
    # 创建代码生成器
    generator = AutomatedCodeGenerator()
    
    # 定义应用规范
    specification = {
        "name": "用户管理系统",
        "version": "1.0.0",
        "entities": [
            {
                "name": "User",
                "properties": [
                    {"name": "id", "type": "int", "default_value": "None"},
                    {"name": "username", "type": "str", "default_value": '""'},
                    {"name": "email", "type": "str", "default_value": '""'},
                    {"name": "created_at", "type": "datetime", "default_value": "None"}
                ],
                "methods": [
                    {
                        "name": "validate",
                        "parameters": [],
                        "return_type": "bool",
                        "description": "验证用户数据"
                    }
                ]
            }
        ],
        "services": [
            {
                "name": "User",
                "methods": [
                    {
                        "name": "create_user",
                        "parameters": [
                            {"name": "user_data", "type": "Dict[str, Any]"}
                        ],
                        "return_type": "User",
                        "description": "创建用户"
                    },
                    {
                        "name": "get_user",
                        "parameters": [
                            {"name": "user_id", "type": "int"}
                        ],
                        "return_type": "Optional[User]",
                        "description": "获取用户"
                    }
                ],
                "dependencies": ["UserRepository"]
            }
        ],
        "controllers": [
            {
                "name": "User",
                "endpoints": [
                    {
                        "name": "create_user",
                        "path": "/users",
                        "method": "POST",
                        "description": "创建用户端点"
                    },
                    {
                        "name": "get_user",
                        "path": "/users/<int:user_id>",
                        "method": "GET",
                        "description": "获取用户端点"
                    }
                ],
                "dependencies": ["UserService"]
            }
        ],
        "repositories": [
            {
                "name": "User",
                "entity": "User",
                "methods": [
                    {
                        "name": "save",
                        "parameters": [
                            {"name": "user", "type": "User"}
                        ],
                        "return_type": "User",
                        "description": "保存用户"
                    },
                    {
                        "name": "find_by_id",
                        "parameters": [
                            {"name": "user_id", "type": "int"}
                        ],
                        "return_type": "Optional[User]",
                        "description": "根据ID查找用户"
                    }
                ]
            }
        ],
        "database": {
            "url": "postgresql://localhost:5432/userdb",
            "username": "admin",
            "password": "password"
        }
    }
    
    # 生成Python代码
    print("\n🐍 生成Python代码...")
    python_files = generator.generate_code(specification, "python", "generated_code/python")
    
    # 生成Java代码
    print("\n☕ 生成Java代码...")
    java_files = generator.generate_code(specification, "java", "generated_code/java")
    
    # 生成TypeScript代码
    print("\n📘 生成TypeScript代码...")
    typescript_files = generator.generate_code(specification, "typescript", "generated_code/typescript")
    
    # 生成Rust代码
    print("\n🦀 生成Rust代码...")
    rust_files = generator.generate_code(specification, "rust", "generated_code/rust")
    
    print(f"\n✅ 代码生成完成！")
    print(f"Python文件: {len(python_files)} 个")
    print(f"Java文件: {len(java_files)} 个")
    print(f"TypeScript文件: {len(typescript_files)} 个")
    print(f"Rust文件: {len(rust_files)} 个")

if __name__ == "__main__":
    def _parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser(description="Automated Code Generator CLI")
        parser.add_argument("--language", help="目标语言，如 python/java/typescript/rust/go/csharp")
        parser.add_argument("--pattern", help="抽象模式，如 state_machine/petri_net/temporal_logic")
        parser.add_argument("--config", default=str(Path(__file__).resolve().parent.parent / "config.yaml"), help="统一配置config.yaml路径")
        parser.add_argument("--out", default="generated_code/cli", help="输出目录")
        parser.add_argument("--dry-run", action="store_true", help="仅解析与校验，不写文件")
        parser.add_argument("--spec", help="规范JSON文件路径（不提供则使用内置示例）")
        return parser.parse_args()

    def _load_spec(spec_path: Optional[str]) -> Dict[str, Any]:
        if not spec_path:
            # 提供一个最小可运行的默认规范
            return {
                "entities": [
                    {"name": "User", "properties": [{"name": "id", "type": "int"}, {"name": "name", "type": "str"}], "methods": []}
                ],
                "services": [
                    {"name": "UserService", "methods": [{"name": "get_user", "parameters": [{"name": "user_id", "type": "int"}], "return_type": "User"}], "dependencies": []}
                ],
                "controllers": [],
                "repositories": [],
                "database": {"url": "", "username": "", "password": ""}
            }
        p = Path(spec_path)
        data = json.loads(p.read_text(encoding="utf-8"))
        return data

    def _resolve_template_via_mapper(pattern: Optional[str], language: Optional[str], config_path: str) -> Optional[str]:
        if not pattern or not language:
            return None
        # 直接复用映射工具模块（相对导入路径）
        mapper_path = Path(__file__).resolve().parent.parent / "08-实践与应用" / "theory_to_practice_mapper.py"
        if not mapper_path.exists():
            # 兼容运行路径：工具与本文件均在08-实践与应用子目录树
            mapper_path = Path(__file__).resolve().parent.parent / "theory_to_practice_mapper.py"
        try:
            # 以子进程方式最稳妥，避免包路径冲突
            import subprocess
            cmd = [sys.executable, str(mapper_path), "--pattern", pattern, "--language", language, "--config", config_path]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode != 0:
                logging.warning("映射工具返回码非零: %s", result.returncode)
                return None
            obj = json.loads(result.stdout)
            if obj.get("status") == "ok":
                return obj.get("template_name")
        except Exception as exc:
            logging.warning("调用映射工具失败: %s", exc)
        return None

    args = _parse_args()
    gen = AutomatedCodeGenerator()
    # 若提供pattern/language，则解析模板名（信息用途，现阶段生成器内置模板，不强依赖该名称）
    template_name = _resolve_template_via_mapper(args.pattern, args.language, args.config) if (args.pattern and args.language) else None
    if template_name:
        print(f"映射模板: {template_name}")

    spec = _load_spec(args.spec)
    target_lang = args.language or "python"
    out_dir = None if args.dry_run else args.out
    files = gen.generate_code(spec, target_lang, out_dir)
    print(f"✅ 生成{len(files)}个文件 (language={target_lang}, dry_run={args.dry_run})") 