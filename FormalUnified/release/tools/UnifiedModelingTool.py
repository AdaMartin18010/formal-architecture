#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一建模工具 (Unified Modeling Tool)
支持多种形式化理论的统一建模、模型转换和AI增强优化
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
import json
import logging
from dataclasses import dataclass, field
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TheoryType(Enum):
    """支持的理论类型"""
    PETRI_NET = "petri_net"
    STATE_MACHINE = "state_machine"
    TEMPORAL_LOGIC = "temporal_logic"
    TYPE_SYSTEM = "type_system"
    WORKFLOW = "workflow"
    MICROSERVICE = "microservice"

@dataclass
class ModelSpecification:
    """模型规范"""
    theory_type: TheoryType
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Model:
    """统一模型表示"""
    id: str
    theory_type: TheoryType
    specification: ModelSpecification
    content: Dict[str, Any]
    validation_status: str = "pending"
    optimization_status: str = "pending"
    created_at: str = ""
    updated_at: str = ""

class TheoryEngine(ABC):
    """理论引擎基类"""
    
    @abstractmethod
    def create_model(self, specification: ModelSpecification) -> Model:
        """创建模型"""
        pass
    
    @abstractmethod
    def validate_model(self, model: Model) -> Dict[str, Any]:
        """验证模型"""
        pass
    
    @abstractmethod
    def convert_from(self, source_model: Model) -> Model:
        """从其他模型转换"""
        pass

class PetriNetEngine(TheoryEngine):
    """Petri网引擎"""
    
    def create_model(self, specification: ModelSpecification) -> Model:
        """创建Petri网模型"""
        logger.info(f"创建Petri网模型: {specification.name}")
        
        # 解析参数
        places = specification.parameters.get('places', [])
        transitions = specification.parameters.get('transitions', [])
        arcs = specification.parameters.get('arcs', [])
        
        content = {
            'places': places,
            'transitions': transitions,
            'arcs': arcs,
            'initial_marking': specification.parameters.get('initial_marking', {}),
            'constraints': specification.constraints
        }
        
        model = Model(
            id=f"petri_{specification.name}_{hash(specification.name)}",
            theory_type=TheoryType.PETRI_NET,
            specification=specification,
            content=content
        )
        
        return model
    
    def validate_model(self, model: Model) -> Dict[str, Any]:
        """验证Petri网模型"""
        logger.info(f"验证Petri网模型: {model.id}")
        
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'details': {}
        }
        
        content = model.content
        
        # 检查基本结构
        if not content.get('places'):
            validation_result['valid'] = False
            validation_result['errors'].append("缺少库所定义")
        
        if not content.get('transitions'):
            validation_result['valid'] = False
            validation_result['errors'].append("缺少变迁定义")
        
        # 检查弧的连接性
        places = set(place['id'] for place in content.get('places', []))
        transitions = set(trans['id'] for trans in content.get('transitions', []))
        
        for arc in content.get('arcs', []):
            source = arc.get('source')
            target = arc.get('target')
            
            if source not in places and source not in transitions:
                validation_result['warnings'].append(f"弧的源节点未定义: {source}")
            
            if target not in places and target not in transitions:
                validation_result['warnings'].append(f"弧的目标节点未定义: {target}")
        
        model.validation_status = "valid" if validation_result['valid'] else "invalid"
        return validation_result
    
    def convert_from(self, source_model: Model) -> Model:
        """从其他模型转换为Petri网"""
        logger.info(f"转换模型到Petri网: {source_model.id}")
        
        if source_model.theory_type == TheoryType.STATE_MACHINE:
            return self._convert_from_state_machine(source_model)
        elif source_model.theory_type == TheoryType.WORKFLOW:
            return self._convert_from_workflow(source_model)
        else:
            raise ValueError(f"不支持从 {source_model.theory_type} 转换到Petri网")
    
    def _convert_from_state_machine(self, source_model: Model) -> Model:
        """从状态机转换到Petri网"""
        # 状态转换为库所
        places = []
        for state in source_model.content.get('states', []):
            places.append({
                'id': f"p_{state['id']}",
                'name': state['name'],
                'type': 'state'
            })
        
        # 转换转换为变迁
        transitions = []
        for transition in source_model.content.get('transitions', []):
            transitions.append({
                'id': f"t_{transition['id']}",
                'name': transition['name'],
                'guard': transition.get('guard', 'true')
            })
        
        # 构建弧
        arcs = []
        for transition in source_model.content.get('transitions', []):
            # 输入弧
            arcs.append({
                'id': f"arc_{transition['id']}_in",
                'source': f"p_{transition['from']}",
                'target': f"t_{transition['id']}",
                'weight': 1
            })
            # 输出弧
            arcs.append({
                'id': f"arc_{transition['id']}_out",
                'source': f"t_{transition['id']}",
                'target': f"p_{transition['to']}",
                'weight': 1
            })
        
        # 初始标记
        initial_marking = {}
        initial_state = source_model.content.get('initial_state')
        if initial_state:
            initial_marking[f"p_{initial_state}"] = 1
        
        specification = ModelSpecification(
            theory_type=TheoryType.PETRI_NET,
            name=f"{source_model.specification.name}_converted",
            description=f"从状态机转换的Petri网模型: {source_model.specification.description}",
            parameters={
                'places': places,
                'transitions': transitions,
                'arcs': arcs,
                'initial_marking': initial_marking
            }
        )
        
        content = {
            'places': places,
            'transitions': transitions,
            'arcs': arcs,
            'initial_marking': initial_marking,
            'source_model': source_model.id
        }
        
        return Model(
            id=f"petri_converted_{source_model.id}",
            theory_type=TheoryType.PETRI_NET,
            specification=specification,
            content=content
        )

class StateMachineEngine(TheoryEngine):
    """状态机引擎"""
    
    def create_model(self, specification: ModelSpecification) -> Model:
        """创建状态机模型"""
        logger.info(f"创建状态机模型: {specification.name}")
        
        states = specification.parameters.get('states', [])
        transitions = specification.parameters.get('transitions', [])
        initial_state = specification.parameters.get('initial_state', '')
        
        content = {
            'states': states,
            'transitions': transitions,
            'initial_state': initial_state,
            'final_states': specification.parameters.get('final_states', []),
            'constraints': specification.constraints
        }
        
        model = Model(
            id=f"sm_{specification.name}_{hash(specification.name)}",
            theory_type=TheoryType.STATE_MACHINE,
            specification=specification,
            content=content
        )
        
        return model
    
    def validate_model(self, model: Model) -> Dict[str, Any]:
        """验证状态机模型"""
        logger.info(f"验证状态机模型: {model.id}")
        
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'details': {}
        }
        
        content = model.content
        
        # 检查基本结构
        if not content.get('states'):
            validation_result['valid'] = False
            validation_result['errors'].append("缺少状态定义")
        
        if not content.get('transitions'):
            validation_result['warnings'].append("缺少转换定义")
        
        # 检查初始状态
        states = set(state['id'] for state in content.get('states', []))
        if content.get('initial_state') and content['initial_state'] not in states:
            validation_result['errors'].append("初始状态未定义")
        
        # 检查转换的有效性
        for transition in content.get('transitions', []):
            from_state = transition.get('from')
            to_state = transition.get('to')
            
            if from_state not in states:
                validation_result['warnings'].append(f"转换的源状态未定义: {from_state}")
            
            if to_state not in states:
                validation_result['warnings'].append(f"转换的目标状态未定义: {to_state}")
        
        model.validation_status = "valid" if validation_result['valid'] else "invalid"
        return validation_result
    
    def convert_from(self, source_model: Model) -> Model:
        """从其他模型转换为状态机"""
        logger.info(f"转换模型到状态机: {source_model.id}")
        
        if source_model.theory_type == TheoryType.PETRI_NET:
            return self._convert_from_petri_net(source_model)
        else:
            raise ValueError(f"不支持从 {source_model.theory_type} 转换到状态机")
    
    def _convert_from_petri_net(self, source_model: Model) -> Model:
        """从Petri网转换到状态机"""
        # 库所转换为状态
        states = []
        for place in source_model.content.get('places', []):
            states.append({
                'id': f"s_{place['id']}",
                'name': place['name'],
                'type': place.get('type', 'state')
            })
        
        # 变迁转换为转换
        transitions = []
        for transition in source_model.content.get('transitions', []):
            # 找到输入和输出库所
            input_places = []
            output_places = []
            
            for arc in source_model.content.get('arcs', []):
                if arc['target'] == transition['id']:
                    input_places.append(arc['source'])
                elif arc['source'] == transition['id']:
                    output_places.append(arc['target'])
            
            # 为每个输入-输出对创建转换
            for input_place in input_places:
                for output_place in output_places:
                    transitions.append({
                        'id': f"t_{transition['id']}_{input_place}_{output_place}",
                        'from': f"s_{input_place}",
                        'to': f"s_{output_place}",
                        'trigger': transition['name'],
                        'guard': transition.get('guard', 'true')
                    })
        
        # 初始状态
        initial_marking = source_model.content.get('initial_marking', {})
        initial_state = ""
        for place, tokens in initial_marking.items():
            if tokens > 0:
                initial_state = f"s_{place}"
                break
        
        if not initial_state and states:
            initial_state = f"s_{states[0]['id']}"
        
        specification = ModelSpecification(
            theory_type=TheoryType.STATE_MACHINE,
            name=f"{source_model.specification.name}_converted",
            description=f"从Petri网转换的状态机模型: {source_model.specification.description}",
            parameters={
                'states': states,
                'transitions': transitions,
                'initial_state': initial_state
            }
        )
        
        content = {
            'states': states,
            'transitions': transitions,
            'initial_state': initial_state,
            'source_model': source_model.id
        }
        
        return Model(
            id=f"sm_converted_{source_model.id}",
            theory_type=TheoryType.STATE_MACHINE,
            specification=specification,
            content=content
        )

class AIEnhancementEngine:
    """AI增强引擎"""
    
    def __init__(self):
        self.optimization_strategies = {
            'petri_net': self._optimize_petri_net,
            'state_machine': self._optimize_state_machine
        }
    
    def optimize_model(self, model: Model) -> Model:
        """优化模型"""
        logger.info(f"AI优化模型: {model.id}")
        
        if model.theory_type.value in self.optimization_strategies:
            optimizer = self.optimization_strategies[model.theory_type.value]
            optimized_content = optimizer(model.content)
            
            # 创建优化后的模型
            optimized_model = Model(
                id=f"{model.id}_optimized",
                theory_type=model.theory_type,
                specification=model.specification,
                content=optimized_content
            )
            
            optimized_model.optimization_status = "completed"
            return optimized_model
        
        return model
    
    def _optimize_petri_net(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """优化Petri网模型"""
        optimized_content = content.copy()
        
        # 简化冗余的库所和变迁
        places = content.get('places', [])
        transitions = content.get('transitions', [])
        arcs = content.get('arcs', [])
        
        # 移除孤立的库所
        connected_places = set()
        for arc in arcs:
            connected_places.add(arc['source'])
            connected_places.add(arc['target'])
        
        optimized_places = [p for p in places if p['id'] in connected_places]
        
        # 移除孤立的变迁
        connected_transitions = set()
        for arc in arcs:
            if arc['source'] in [t['id'] for t in transitions]:
                connected_transitions.add(arc['source'])
            if arc['target'] in [t['id'] for t in transitions]:
                connected_transitions.add(arc['target'])
        
        optimized_transitions = [t for t in transitions if t['id'] in connected_transitions]
        
        # 合并相似的库所
        # 这里可以实现更复杂的合并逻辑
        
        optimized_content['places'] = optimized_places
        optimized_content['transitions'] = optimized_transitions
        
        return optimized_content
    
    def _optimize_state_machine(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """优化状态机模型"""
        optimized_content = content.copy()
        
        states = content.get('states', [])
        transitions = content.get('transitions', [])
        
        # 移除不可达状态
        reachable_states = set()
        reachable_states.add(content.get('initial_state', ''))
        
        # 简单的可达性分析
        changed = True
        while changed:
            changed = False
            for transition in transitions:
                if transition['from'] in reachable_states:
                    if transition['to'] not in reachable_states:
                        reachable_states.add(transition['to'])
                        changed = True
        
        optimized_states = [s for s in states if s['id'] in reachable_states]
        optimized_transitions = [t for t in transitions 
                               if t['from'] in reachable_states and t['to'] in reachable_states]
        
        optimized_content['states'] = optimized_states
        optimized_content['transitions'] = optimized_transitions
        
        return optimized_content

class UnifiedModelingTool:
    """统一建模工具"""
    
    def __init__(self):
        self.theory_engines = {
            TheoryType.PETRI_NET: PetriNetEngine(),
            TheoryType.STATE_MACHINE: StateMachineEngine(),
        }
        self.ai_enhancer = AIEnhancementEngine()
        self.models: Dict[str, Model] = {}
    
    def create_model(self, theory_type: TheoryType, specification: ModelSpecification) -> Model:
        """创建指定理论的模型"""
        logger.info(f"创建模型: {specification.name} ({theory_type.value})")
        
        if theory_type not in self.theory_engines:
            raise ValueError(f"不支持的理论类型: {theory_type}")
        
        engine = self.theory_engines[theory_type]
        model = engine.create_model(specification)
        
        # AI优化
        optimized_model = self.ai_enhancer.optimize_model(model)
        
        # 存储模型
        self.models[optimized_model.id] = optimized_model
        
        return optimized_model
    
    def convert_model(self, source_model: Model, target_theory: TheoryType) -> Model:
        """模型转换"""
        logger.info(f"转换模型: {source_model.id} -> {target_theory.value}")
        
        if target_theory not in self.theory_engines:
            raise ValueError(f"不支持的目标理论类型: {target_theory}")
        
        engine = self.theory_engines[target_theory]
        converted_model = engine.convert_from(source_model)
        
        # AI优化转换后的模型
        optimized_model = self.ai_enhancer.optimize_model(converted_model)
        
        # 存储转换后的模型
        self.models[optimized_model.id] = optimized_model
        
        return optimized_model
    
    def validate_model(self, model_id: str) -> Dict[str, Any]:
        """验证模型"""
        if model_id not in self.models:
            raise ValueError(f"模型不存在: {model_id}")
        
        model = self.models[model_id]
        engine = self.theory_engines[model.theory_type]
        return engine.validate_model(model)
    
    def get_model(self, model_id: str) -> Optional[Model]:
        """获取模型"""
        return self.models.get(model_id)
    
    def list_models(self) -> List[Model]:
        """列出所有模型"""
        return list(self.models.values())
    
    def export_model(self, model_id: str, format: str = "json") -> str:
        """导出模型"""
        if model_id not in self.models:
            raise ValueError(f"模型不存在: {model_id}")
        
        model = self.models[model_id]
        
        if format == "json":
            return json.dumps({
                'id': model.id,
                'theory_type': model.theory_type.value,
                'specification': {
                    'name': model.specification.name,
                    'description': model.specification.description,
                    'parameters': model.specification.parameters,
                    'constraints': model.specification.constraints
                },
                'content': model.content,
                'validation_status': model.validation_status,
                'optimization_status': model.optimization_status
            }, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"不支持的导出格式: {format}")
    
    def import_model(self, model_data: str, format: str = "json") -> Model:
        """导入模型"""
        if format == "json":
            data = json.loads(model_data)
            
            # 重建模型规范
            specification = ModelSpecification(
                theory_type=TheoryType(data['theory_type']),
                name=data['specification']['name'],
                description=data['specification']['description'],
                parameters=data['specification']['parameters'],
                constraints=data['specification']['constraints']
            )
            
            # 重建模型
            model = Model(
                id=data['id'],
                theory_type=TheoryType(data['theory_type']),
                specification=specification,
                content=data['content'],
                validation_status=data['validation_status'],
                optimization_status=data['optimization_status']
            )
            
            # 存储模型
            self.models[model.id] = model
            
            return model
        else:
            raise ValueError(f"不支持的导入格式: {format}")

def main():
    """主函数 - 演示工具使用"""
    print("=== 统一建模工具演示 ===\n")
    
    # 创建工具实例
    tool = UnifiedModelingTool()
    
    # 创建Petri网模型
    print("1. 创建Petri网模型")
    petri_spec = ModelSpecification(
        theory_type=TheoryType.PETRI_NET,
        name="简单工作流",
        description="一个简单的工作流Petri网模型",
        parameters={
            'places': [
                {'id': 'start', 'name': '开始', 'type': 'start'},
                {'id': 'process', 'name': '处理中', 'type': 'state'},
                {'id': 'end', 'name': '结束', 'type': 'end'}
            ],
            'transitions': [
                {'id': 'begin', 'name': '开始处理'},
                {'id': 'complete', 'name': '完成处理'}
            ],
            'arcs': [
                {'id': 'arc1', 'source': 'start', 'target': 'begin', 'weight': 1},
                {'id': 'arc2', 'source': 'begin', 'target': 'process', 'weight': 1},
                {'id': 'arc3', 'source': 'process', 'target': 'complete', 'weight': 1},
                {'id': 'arc4', 'source': 'complete', 'target': 'end', 'weight': 1}
            ],
            'initial_marking': {'start': 1}
        }
    )
    
    petri_model = tool.create_model(TheoryType.PETRI_NET, petri_spec)
    print(f"   创建成功: {petri_model.id}")
    
    # 验证模型
    print("\n2. 验证Petri网模型")
    validation_result = tool.validate_model(petri_model.id)
    print(f"   验证结果: {'通过' if validation_result['valid'] else '失败'}")
    if validation_result['errors']:
        print(f"   错误: {validation_result['errors']}")
    if validation_result['warnings']:
        print(f"   警告: {validation_result['warnings']}")
    
    # 转换为状态机
    print("\n3. 转换为状态机模型")
    sm_model = tool.convert_model(petri_model, TheoryType.STATE_MACHINE)
    print(f"   转换成功: {sm_model.id}")
    
    # 验证转换后的模型
    print("\n4. 验证转换后的状态机模型")
    sm_validation = tool.validate_model(sm_model.id)
    print(f"   验证结果: {'通过' if sm_validation['valid'] else '失败'}")
    
    # 列出所有模型
    print("\n5. 所有模型列表")
    models = tool.list_models()
    for model in models:
        print(f"   - {model.id}: {model.theory_type.value} ({model.validation_status})")
    
    # 导出模型
    print("\n6. 导出Petri网模型")
    exported = tool.export_model(petri_model.id, "json")
    print(f"   导出成功，长度: {len(exported)} 字符")
    
    print("\n=== 演示完成 ===")

if __name__ == "__main__":
    main() 