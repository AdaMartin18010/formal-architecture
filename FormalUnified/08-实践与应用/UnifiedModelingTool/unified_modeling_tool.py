#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一建模工具
Unified Modeling Tool

支持多种建模语言（UML、BPMN、Petri网、状态机等）的统一建模平台
提供可视化建模、模型验证、代码生成等功能
"""

import json
import yaml
import logging
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
import networkx as nx
from enum import Enum
import re

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelType(Enum):
    """模型类型"""
    UML_CLASS = "uml_class"
    UML_SEQUENCE = "uml_sequence"
    UML_ACTIVITY = "uml_activity"
    BPMN = "bpmn"
    PETRI_NET = "petri_net"
    STATE_MACHINE = "state_machine"
    DATA_FLOW = "data_flow"
    ARCHITECTURE = "architecture"

class ElementType(Enum):
    """元素类型"""
    # UML元素
    CLASS = "class"
    INTERFACE = "interface"
    METHOD = "method"
    ATTRIBUTE = "attribute"
    RELATIONSHIP = "relationship"
    
    # BPMN元素
    TASK = "task"
    GATEWAY = "gateway"
    EVENT = "event"
    POOL = "pool"
    LANE = "lane"
    
    # Petri网元素
    PLACE = "place"
    TRANSITION = "transition"
    ARC = "arc"
    TOKEN = "token"
    
    # 状态机元素
    STATE = "state"
    TRANSITION_SM = "transition_sm"
    INITIAL = "initial"
    FINAL = "final"

@dataclass
class ModelElement:
    """模型元素"""
    id: str
    name: str
    type: ElementType
    properties: Dict[str, Any]
    position: Optional[Tuple[float, float]] = None
    size: Optional[Tuple[float, float]] = None
    style: Optional[Dict[str, Any]] = None

@dataclass
class ModelRelationship:
    """模型关系"""
    id: str
    source_id: str
    target_id: str
    type: str
    properties: Dict[str, Any]
    style: Optional[Dict[str, Any]] = None

@dataclass
class UnifiedModel:
    """统一模型"""
    id: str
    name: str
    type: ModelType
    elements: List[ModelElement]
    relationships: List[ModelRelationship]
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str

class UnifiedModelingTool:
    """统一建模工具"""
    
    def __init__(self, config_path: str = "modeling_config.yaml"):
        self.config = self._load_config(config_path)
        self.models = {}
        self.templates = {}
        self.validators = {}
        
        self._initialize_templates()
        self._initialize_validators()
        
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
            "supported_model_types": [
                "uml_class", "uml_sequence", "uml_activity",
                "bpmn", "petri_net", "state_machine", "data_flow", "architecture"
            ],
            "export_formats": ["json", "yaml", "xml", "png", "svg"],
            "validation_rules": {
                "syntax": True,
                "semantics": True,
                "consistency": True
            },
            "code_generation": {
                "enabled": True,
                "languages": ["python", "java", "typescript", "rust"]
            }
        }
    
    def _initialize_templates(self):
        """初始化模型模板"""
        self.templates = {
            ModelType.UML_CLASS: self._get_uml_class_template(),
            ModelType.UML_SEQUENCE: self._get_uml_sequence_template(),
            ModelType.BPMN: self._get_bpmn_template(),
            ModelType.PETRI_NET: self._get_petri_net_template(),
            ModelType.STATE_MACHINE: self._get_state_machine_template(),
            ModelType.ARCHITECTURE: self._get_architecture_template()
        }
    
    def _initialize_validators(self):
        """初始化验证器"""
        self.validators = {
            ModelType.UML_CLASS: self._validate_uml_class,
            ModelType.UML_SEQUENCE: self._validate_uml_sequence,
            ModelType.BPMN: self._validate_bpmn,
            ModelType.PETRI_NET: self._validate_petri_net,
            ModelType.STATE_MACHINE: self._validate_state_machine,
            ModelType.ARCHITECTURE: self._validate_architecture
        }
    
    def create_model(self, name: str, model_type: ModelType, 
                    template_name: Optional[str] = None) -> UnifiedModel:
        """创建新模型"""
        model_id = f"{model_type.value}_{int(time.time())}"
        
        # 使用模板或创建空模型
        if template_name and template_name in self.templates[model_type]:
            template = self.templates[model_type][template_name]
            elements = template.get("elements", [])
            relationships = template.get("relationships", [])
        else:
            elements = []
            relationships = []
        
        model = UnifiedModel(
            id=model_id,
            name=name,
            type=model_type,
            elements=elements,
            relationships=relationships,
            metadata={
                "template": template_name,
                "version": "1.0.0",
                "author": "Unified Modeling Tool"
            },
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self.models[model_id] = model
        logger.info(f"✅ 创建模型: {name} ({model_type.value})")
        
        return model
    
    def add_element(self, model_id: str, element: ModelElement) -> bool:
        """添加模型元素"""
        if model_id not in self.models:
            logger.error(f"❌ 模型不存在: {model_id}")
            return False
        
        model = self.models[model_id]
        model.elements.append(element)
        model.updated_at = datetime.now().isoformat()
        
        logger.info(f"✅ 添加元素: {element.name} ({element.type.value})")
        return True
    
    def add_relationship(self, model_id: str, relationship: ModelRelationship) -> bool:
        """添加模型关系"""
        if model_id not in self.models:
            logger.error(f"❌ 模型不存在: {model_id}")
            return False
        
        model = self.models[model_id]
        model.relationships.append(relationship)
        model.updated_at = datetime.now().isoformat()
        
        logger.info(f"✅ 添加关系: {relationship.type}")
        return True
    
    def update_element(self, model_id: str, element_id: str, 
                      updates: Dict[str, Any]) -> bool:
        """更新模型元素"""
        if model_id not in self.models:
            logger.error(f"❌ 模型不存在: {model_id}")
            return False
        
        model = self.models[model_id]
        for element in model.elements:
            if element.id == element_id:
                for key, value in updates.items():
                    if hasattr(element, key):
                        setattr(element, key, value)
                model.updated_at = datetime.now().isoformat()
                logger.info(f"✅ 更新元素: {element.name}")
                return True
        
        logger.error(f"❌ 元素不存在: {element_id}")
        return False
    
    def delete_element(self, model_id: str, element_id: str) -> bool:
        """删除模型元素"""
        if model_id not in self.models:
            logger.error(f"❌ 模型不存在: {model_id}")
            return False
        
        model = self.models[model_id]
        
        # 删除元素
        model.elements = [e for e in model.elements if e.id != element_id]
        
        # 删除相关关系
        model.relationships = [r for r in model.relationships 
                             if r.source_id != element_id and r.target_id != element_id]
        
        model.updated_at = datetime.now().isoformat()
        logger.info(f"✅ 删除元素: {element_id}")
        return True
    
    def validate_model(self, model_id: str) -> Dict[str, Any]:
        """验证模型"""
        if model_id not in self.models:
            return {"valid": False, "errors": ["模型不存在"]}
        
        model = self.models[model_id]
        validator = self.validators.get(model.type)
        
        if validator:
            return validator(model)
        else:
            return {"valid": True, "warnings": ["无验证器可用"]}
    
    def export_model(self, model_id: str, format: str, 
                    output_path: Optional[str] = None) -> bool:
        """导出模型"""
        if model_id not in self.models:
            logger.error(f"❌ 模型不存在: {model_id}")
            return False
        
        model = self.models[model_id]
        
        if format == "json":
            return self._export_json(model, output_path)
        elif format == "yaml":
            return self._export_yaml(model, output_path)
        elif format == "xml":
            return self._export_xml(model, output_path)
        elif format in ["png", "svg"]:
            return self._export_image(model, format, output_path)
        else:
            logger.error(f"❌ 不支持的导出格式: {format}")
            return False
    
    def generate_code(self, model_id: str, language: str, 
                     output_dir: Optional[str] = None) -> Dict[str, Any]:
        """生成代码"""
        if model_id not in self.models:
            return {"success": False, "error": "模型不存在"}
        
        model = self.models[model_id]
        
        if not self.config["code_generation"]["enabled"]:
            return {"success": False, "error": "代码生成功能未启用"}
        
        if language not in self.config["code_generation"]["languages"]:
            return {"success": False, "error": f"不支持的语言: {language}"}
        
        try:
            if model.type == ModelType.UML_CLASS:
                return self._generate_class_code(model, language, output_dir)
            elif model.type == ModelType.STATE_MACHINE:
                return self._generate_state_machine_code(model, language, output_dir)
            elif model.type == ModelType.BPMN:
                return self._generate_bpmn_code(model, language, output_dir)
            else:
                return {"success": False, "error": f"不支持的模型类型: {model.type.value}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_model_summary(self, model_id: str) -> Dict[str, Any]:
        """获取模型摘要"""
        if model_id not in self.models:
            return {}
        
        model = self.models[model_id]
        
        element_counts = {}
        for element in model.elements:
            element_type = element.type.value
            element_counts[element_type] = element_counts.get(element_type, 0) + 1
        
        return {
            "id": model.id,
            "name": model.name,
            "type": model.type.value,
            "element_count": len(model.elements),
            "relationship_count": len(model.relationships),
            "element_counts": element_counts,
            "created_at": model.created_at,
            "updated_at": model.updated_at
        }
    
    # 模板定义方法
    def _get_uml_class_template(self) -> Dict[str, Any]:
        return {
            "basic_class": {
                "elements": [
                    ModelElement(
                        id="class_1",
                        name="User",
                        type=ElementType.CLASS,
                        properties={
                            "visibility": "public",
                            "abstract": False,
                            "final": False
                        },
                        position=(100, 100),
                        size=(200, 150)
                    ),
                    ModelElement(
                        id="attr_1",
                        name="id: Long",
                        type=ElementType.ATTRIBUTE,
                        properties={
                            "visibility": "private",
                            "type": "Long",
                            "static": False
                        },
                        position=(110, 130)
                    ),
                    ModelElement(
                        id="method_1",
                        name="getName(): String",
                        type=ElementType.METHOD,
                        properties={
                            "visibility": "public",
                            "return_type": "String",
                            "abstract": False
                        },
                        position=(110, 160)
                    )
                ],
                "relationships": []
            }
        }
    
    def _get_uml_sequence_template(self) -> Dict[str, Any]:
        return {
            "basic_sequence": {
                "elements": [
                    ModelElement(
                        id="actor_1",
                        name="User",
                        type=ElementType.CLASS,
                        properties={"type": "actor"},
                        position=(50, 50)
                    ),
                    ModelElement(
                        id="system_1",
                        name="System",
                        type=ElementType.CLASS,
                        properties={"type": "system"},
                        position=(200, 50)
                    )
                ],
                "relationships": [
                    ModelRelationship(
                        id="msg_1",
                        source_id="actor_1",
                        target_id="system_1",
                        type="message",
                        properties={"message": "request()"}
                    )
                ]
            }
        }
    
    def _get_bpmn_template(self) -> Dict[str, Any]:
        return {
            "simple_process": {
                "elements": [
                    ModelElement(
                        id="start_1",
                        name="Start",
                        type=ElementType.EVENT,
                        properties={"event_type": "start"},
                        position=(100, 100)
                    ),
                    ModelElement(
                        id="task_1",
                        name="Process Task",
                        type=ElementType.TASK,
                        properties={"task_type": "user"},
                        position=(200, 100)
                    ),
                    ModelElement(
                        id="end_1",
                        name="End",
                        type=ElementType.EVENT,
                        properties={"event_type": "end"},
                        position=(300, 100)
                    )
                ],
                "relationships": [
                    ModelRelationship(
                        id="flow_1",
                        source_id="start_1",
                        target_id="task_1",
                        type="sequence_flow",
                        properties={}
                    ),
                    ModelRelationship(
                        id="flow_2",
                        source_id="task_1",
                        target_id="end_1",
                        type="sequence_flow",
                        properties={}
                    )
                ]
            }
        }
    
    def _get_petri_net_template(self) -> Dict[str, Any]:
        return {
            "simple_net": {
                "elements": [
                    ModelElement(
                        id="place_1",
                        name="P1",
                        type=ElementType.PLACE,
                        properties={"tokens": 1},
                        position=(100, 100)
                    ),
                    ModelElement(
                        id="transition_1",
                        name="T1",
                        type=ElementType.TRANSITION,
                        properties={"enabled": True},
                        position=(200, 100)
                    ),
                    ModelElement(
                        id="place_2",
                        name="P2",
                        type=ElementType.PLACE,
                        properties={"tokens": 0},
                        position=(300, 100)
                    )
                ],
                "relationships": [
                    ModelRelationship(
                        id="arc_1",
                        source_id="place_1",
                        target_id="transition_1",
                        type="arc",
                        properties={"weight": 1}
                    ),
                    ModelRelationship(
                        id="arc_2",
                        source_id="transition_1",
                        target_id="place_2",
                        type="arc",
                        properties={"weight": 1}
                    )
                ]
            }
        }
    
    def _get_state_machine_template(self) -> Dict[str, Any]:
        return {
            "simple_state_machine": {
                "elements": [
                    ModelElement(
                        id="initial_1",
                        name="",
                        type=ElementType.INITIAL,
                        properties={},
                        position=(50, 100)
                    ),
                    ModelElement(
                        id="state_1",
                        name="Idle",
                        type=ElementType.STATE,
                        properties={},
                        position=(150, 100)
                    ),
                    ModelElement(
                        id="state_2",
                        name="Active",
                        type=ElementType.STATE,
                        properties={},
                        position=(250, 100)
                    ),
                    ModelElement(
                        id="final_1",
                        name="",
                        type=ElementType.FINAL,
                        properties={},
                        position=(350, 100)
                    )
                ],
                "relationships": [
                    ModelRelationship(
                        id="trans_1",
                        source_id="initial_1",
                        target_id="state_1",
                        type="transition",
                        properties={"event": "init"}
                    ),
                    ModelRelationship(
                        id="trans_2",
                        source_id="state_1",
                        target_id="state_2",
                        type="transition",
                        properties={"event": "activate"}
                    ),
                    ModelRelationship(
                        id="trans_3",
                        source_id="state_2",
                        target_id="final_1",
                        type="transition",
                        properties={"event": "complete"}
                    )
                ]
            }
        }
    
    def _get_architecture_template(self) -> Dict[str, Any]:
        return {
            "microservice_architecture": {
                "elements": [
                    ModelElement(
                        id="api_gateway",
                        name="API Gateway",
                        type=ElementType.CLASS,
                        properties={"component_type": "gateway"},
                        position=(200, 50)
                    ),
                    ModelElement(
                        id="user_service",
                        name="User Service",
                        type=ElementType.CLASS,
                        properties={"component_type": "service"},
                        position=(100, 150)
                    ),
                    ModelElement(
                        id="order_service",
                        name="Order Service",
                        type=ElementType.CLASS,
                        properties={"component_type": "service"},
                        position=(300, 150)
                    ),
                    ModelElement(
                        id="database",
                        name="Database",
                        type=ElementType.CLASS,
                        properties={"component_type": "database"},
                        position=(200, 250)
                    )
                ],
                "relationships": [
                    ModelRelationship(
                        id="conn_1",
                        source_id="api_gateway",
                        target_id="user_service",
                        type="dependency",
                        properties={"protocol": "HTTP"}
                    ),
                    ModelRelationship(
                        id="conn_2",
                        source_id="api_gateway",
                        target_id="order_service",
                        type="dependency",
                        properties={"protocol": "HTTP"}
                    ),
                    ModelRelationship(
                        id="conn_3",
                        source_id="user_service",
                        target_id="database",
                        type="dependency",
                        properties={"protocol": "JDBC"}
                    ),
                    ModelRelationship(
                        id="conn_4",
                        source_id="order_service",
                        target_id="database",
                        type="dependency",
                        properties={"protocol": "JDBC"}
                    )
                ]
            }
        }
    
    # 验证方法
    def _validate_uml_class(self, model: UnifiedModel) -> Dict[str, Any]:
        """验证UML类图"""
        errors = []
        warnings = []
        
        # 检查类名唯一性
        class_names = [e.name for e in model.elements if e.type == ElementType.CLASS]
        if len(class_names) != len(set(class_names)):
            errors.append("类名必须唯一")
        
        # 检查关系有效性
        for rel in model.relationships:
            source_exists = any(e.id == rel.source_id for e in model.elements)
            target_exists = any(e.id == rel.target_id for e in model.elements)
            if not source_exists or not target_exists:
                errors.append(f"关系 {rel.id} 引用了不存在的元素")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _validate_uml_sequence(self, model: UnifiedModel) -> Dict[str, Any]:
        """验证UML时序图"""
        errors = []
        warnings = []
        
        # 检查是否有参与者
        actors = [e for e in model.elements if e.properties.get("type") == "actor"]
        if not actors:
            warnings.append("时序图应该包含至少一个参与者")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _validate_bpmn(self, model: UnifiedModel) -> Dict[str, Any]:
        """验证BPMN图"""
        errors = []
        warnings = []
        
        # 检查开始和结束事件
        start_events = [e for e in model.elements 
                       if e.type == ElementType.EVENT and e.properties.get("event_type") == "start"]
        end_events = [e for e in model.elements 
                     if e.type == ElementType.EVENT and e.properties.get("event_type") == "end"]
        
        if not start_events:
            errors.append("BPMN图必须包含开始事件")
        if not end_events:
            errors.append("BPMN图必须包含结束事件")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _validate_petri_net(self, model: UnifiedModel) -> Dict[str, Any]:
        """验证Petri网"""
        errors = []
        warnings = []
        
        # 检查库所和变迁
        places = [e for e in model.elements if e.type == ElementType.PLACE]
        transitions = [e for e in model.elements if e.type == ElementType.TRANSITION]
        
        if not places:
            errors.append("Petri网必须包含至少一个库所")
        if not transitions:
            errors.append("Petri网必须包含至少一个变迁")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _validate_state_machine(self, model: UnifiedModel) -> Dict[str, Any]:
        """验证状态机"""
        errors = []
        warnings = []
        
        # 检查初始状态和最终状态
        initial_states = [e for e in model.elements if e.type == ElementType.INITIAL]
        final_states = [e for e in model.elements if e.type == ElementType.FINAL]
        states = [e for e in model.elements if e.type == ElementType.STATE]
        
        if not initial_states:
            errors.append("状态机必须包含初始状态")
        if not states:
            errors.append("状态机必须包含至少一个状态")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _validate_architecture(self, model: UnifiedModel) -> Dict[str, Any]:
        """验证架构图"""
        errors = []
        warnings = []
        
        # 检查组件类型
        components = [e for e in model.elements if e.type == ElementType.CLASS]
        if not components:
            warnings.append("架构图应该包含组件")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    # 导出方法
    def _export_json(self, model: UnifiedModel, output_path: Optional[str] = None) -> bool:
        """导出为JSON格式"""
        try:
            data = asdict(model)
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            return True
        except Exception as e:
            logger.error(f"❌ JSON导出失败: {e}")
            return False
    
    def _export_yaml(self, model: UnifiedModel, output_path: Optional[str] = None) -> bool:
        """导出为YAML格式"""
        try:
            data = asdict(model)
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            else:
                print(yaml.dump(data, default_flow_style=False, allow_unicode=True))
            return True
        except Exception as e:
            logger.error(f"❌ YAML导出失败: {e}")
            return False
    
    def _export_xml(self, model: UnifiedModel, output_path: Optional[str] = None) -> bool:
        """导出为XML格式"""
        try:
            # 简化的XML导出
            xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<model id="{model.id}" name="{model.name}" type="{model.type.value}">
    <elements>
"""
            for element in model.elements:
                xml_content += f'        <element id="{element.id}" name="{element.name}" type="{element.type.value}"/>\n'
            xml_content += """    </elements>
    <relationships>
"""
            for rel in model.relationships:
                xml_content += f'        <relationship id="{rel.id}" source="{rel.source_id}" target="{rel.target_id}" type="{rel.type}"/>\n'
            xml_content += """    </relationships>
</model>"""
            
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(xml_content)
            else:
                print(xml_content)
            return True
        except Exception as e:
            logger.error(f"❌ XML导出失败: {e}")
            return False
    
    def _export_image(self, model: UnifiedModel, format: str, 
                     output_path: Optional[str] = None) -> bool:
        """导出为图像格式"""
        try:
            # 这里应该使用图形库生成图像
            # 简化实现，只记录导出信息
            logger.info(f"导出图像格式: {format}")
            if output_path:
                logger.info(f"输出路径: {output_path}")
            return True
        except Exception as e:
            logger.error(f"❌ 图像导出失败: {e}")
            return False
    
    # 代码生成方法
    def _generate_class_code(self, model: UnifiedModel, language: str, 
                           output_dir: Optional[str] = None) -> Dict[str, Any]:
        """生成类图代码"""
        try:
            classes = [e for e in model.elements if e.type == ElementType.CLASS]
            relationships = model.relationships
            
            generated_files = []
            
            for cls in classes:
                code = self._generate_class_definition(cls, language)
                filename = f"{cls.name.lower()}.{self._get_file_extension(language)}"
                
                if output_dir:
                    output_path = Path(output_dir) / filename
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(code)
                    generated_files.append(str(output_path))
                else:
                    generated_files.append(filename)
            
            return {
                "success": True,
                "files": generated_files,
                "language": language
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_state_machine_code(self, model: UnifiedModel, language: str, 
                                   output_dir: Optional[str] = None) -> Dict[str, Any]:
        """生成状态机代码"""
        try:
            states = [e for e in model.elements if e.type == ElementType.STATE]
            transitions = [r for r in model.relationships if r.type == "transition"]
            
            code = self._generate_state_machine_definition(states, transitions, language)
            filename = f"state_machine.{self._get_file_extension(language)}"
            
            if output_dir:
                output_path = Path(output_dir) / filename
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                return {"success": True, "files": [str(output_path)], "language": language}
            else:
                return {"success": True, "files": [filename], "language": language}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_bpmn_code(self, model: UnifiedModel, language: str, 
                          output_dir: Optional[str] = None) -> Dict[str, Any]:
        """生成BPMN代码"""
        try:
            tasks = [e for e in model.elements if e.type == ElementType.TASK]
            flows = [r for r in model.relationships if r.type == "sequence_flow"]
            
            code = self._generate_bpmn_definition(tasks, flows, language)
            filename = f"workflow.{self._get_file_extension(language)}"
            
            if output_dir:
                output_path = Path(output_dir) / filename
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                return {"success": True, "files": [str(output_path)], "language": language}
            else:
                return {"success": True, "files": [filename], "language": language}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_class_definition(self, cls: ModelElement, language: str) -> str:
        """生成类定义代码"""
        if language == "python":
            return f"""class {cls.name}:
    def __init__(self):
        pass
"""
        elif language == "java":
            return f"""public class {cls.name} {{
    public {cls.name}() {{
    }}
}}
"""
        elif language == "typescript":
            return f"""export class {cls.name} {{
    constructor() {{
    }}
}}
"""
        else:
            return f"// {cls.name} class definition for {language}"
    
    def _generate_state_machine_definition(self, states: List[ModelElement], 
                                         transitions: List[ModelRelationship], 
                                         language: str) -> str:
        """生成状态机定义代码"""
        if language == "python":
            code = """class StateMachine:
    def __init__(self):
        self.current_state = None
        self.states = {
"""
            for state in states:
                code += f'            "{state.name}": "{state.name}",\n'
            code += """        }
        self.transitions = {
"""
            for trans in transitions:
                code += f'            "{trans.properties.get("event", "event")}": "{trans.target_id}",\n'
            code += """        }
"""
            return code
        else:
            return f"// State machine definition for {language}"
    
    def _generate_bpmn_definition(self, tasks: List[ModelElement], 
                                flows: List[ModelRelationship], 
                                language: str) -> str:
        """生成BPMN定义代码"""
        if language == "python":
            code = """class Workflow:
    def __init__(self):
        self.tasks = {
"""
            for task in tasks:
                code += f'            "{task.name}": self.{task.name.lower().replace(" ", "_")},\n'
            code += """        }
"""
            for task in tasks:
                code += f"""
    def {task.name.lower().replace(" ", "_")}(self):
        print("Executing {task.name}")
"""
            return code
        else:
            return f"// Workflow definition for {language}"
    
    def _get_file_extension(self, language: str) -> str:
        """获取文件扩展名"""
        extensions = {
            "python": "py",
            "java": "java",
            "typescript": "ts",
            "rust": "rs",
            "go": "go"
        }
        return extensions.get(language, "txt")

def demo_unified_modeling_tool():
    """演示统一建模工具"""
    print("🚀 启动统一建模工具演示")
    
    # 创建建模工具
    tool = UnifiedModelingTool()
    
    # 创建UML类图
    print("\n📝 创建UML类图...")
    class_model = tool.create_model("用户管理系统", ModelType.UML_CLASS, "basic_class")
    
    # 添加新元素
    new_class = ModelElement(
        id="class_2",
        name="Order",
        type=ElementType.CLASS,
        properties={"visibility": "public", "abstract": False, "final": False},
        position=(300, 100),
        size=(200, 150)
    )
    tool.add_element(class_model.id, new_class)
    
    # 添加关系
    relationship = ModelRelationship(
        id="rel_1",
        source_id="class_1",
        target_id="class_2",
        type="association",
        properties={"multiplicity": "1..*"}
    )
    tool.add_relationship(class_model.id, relationship)
    
    # 验证模型
    print("\n🔍 验证模型...")
    validation_result = tool.validate_model(class_model.id)
    print(f"验证结果: {validation_result}")
    
    # 获取模型摘要
    print("\n📊 模型摘要...")
    summary = tool.get_model_summary(class_model.id)
    print(f"摘要: {summary}")
    
    # 导出模型
    print("\n💾 导出模型...")
    tool.export_model(class_model.id, "json")
    
    # 生成代码
    print("\n🔧 生成代码...")
    code_result = tool.generate_code(class_model.id, "python")
    print(f"代码生成结果: {code_result}")
    
    # 创建状态机
    print("\n🔄 创建状态机...")
    state_model = tool.create_model("订单状态机", ModelType.STATE_MACHINE, "simple_state_machine")
    
    # 验证状态机
    state_validation = tool.validate_model(state_model.id)
    print(f"状态机验证结果: {state_validation}")
    
    # 生成状态机代码
    state_code_result = tool.generate_code(state_model.id, "python")
    print(f"状态机代码生成结果: {state_code_result}")
    
    print("\n🎉 演示完成！")

if __name__ == "__main__":
    demo_unified_modeling_tool() 