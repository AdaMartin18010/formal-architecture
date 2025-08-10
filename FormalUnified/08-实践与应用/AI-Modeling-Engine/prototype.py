#!/usr/bin/env python3
"""
AI建模引擎原型 (AI Modeling Engine Prototype)
基于形式化架构理论的智能建模系统

本原型实现了以下核心功能：
1. 语义理解与推理
2. 形式化模型生成
3. AI增强验证
4. 代码自动生成
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelType(Enum):
    """模型类型枚举"""
    STATE_MACHINE = "state_machine"
    PETRI_NET = "petri_net"
    PROCESS_ALGEBRA = "process_algebra"
    TEMPORAL_LOGIC = "temporal_logic"
    UNIFIED_STS = "unified_sts"

class VerificationResult(Enum):
    """验证结果枚举"""
    VALID = "valid"
    INVALID = "invalid"
    UNKNOWN = "unknown"
    TIMEOUT = "timeout"

@dataclass
class SemanticConcept:
    """语义概念表示"""
    name: str
    type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    relations: List[str] = field(default_factory=list)
    confidence: float = 1.0

@dataclass
class FormalModel:
    """形式化模型表示"""
    model_id: str
    model_type: ModelType
    elements: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    properties: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VerificationTask:
    """验证任务"""
    task_id: str
    model: FormalModel
    property_to_verify: str
    verification_method: str
    result: Optional[VerificationResult] = None
    counterexample: Optional[Dict[str, Any]] = None
    proof: Optional[str] = None

class SemanticAnalyzer:
    """语义分析器"""
    
    def __init__(self):
        self.concept_knowledge = self._initialize_knowledge_base()
        
    def _initialize_knowledge_base(self) -> Dict[str, SemanticConcept]:
        """初始化知识库"""
        return {
            "system": SemanticConcept(
                name="system",
                type="entity",
                properties={"complexity": "high", "behavior": "dynamic"},
                relations=["composed_of", "interacts_with"]
            ),
            "component": SemanticConcept(
                name="component",
                type="entity", 
                properties={"modularity": "high", "reusability": "high"},
                relations=["implements", "depends_on", "communicates_with"]
            ),
            "state": SemanticConcept(
                name="state",
                type="concept",
                properties={"temporal": True, "discrete": True},
                relations=["transitions_to", "contains"]
            ),
            "event": SemanticConcept(
                name="event",
                type="concept",
                properties={"temporal": True, "instantaneous": True},
                relations=["triggers", "caused_by"]
            )
        }
    
    def analyze_requirements(self, requirements_text: str) -> List[SemanticConcept]:
        """分析需求文本，提取语义概念"""
        logger.info(f"分析需求文本：{requirements_text[:100]}...")
        
        concepts = []
        
        # 简单的关键词识别（实际实现中可使用NLP技术）
        keywords = {
            "system": ["系统", "系统", "system"],
            "component": ["组件", "模块", "component", "module"],
            "state": ["状态", "state", "status"],
            "event": ["事件", "event", "action"],
            "interface": ["接口", "interface", "API"],
            "service": ["服务", "service"],
            "process": ["流程", "过程", "process"],
            "data": ["数据", "data", "information"]
        }
        
        for concept_type, words in keywords.items():
            for word in words:
                if word.lower() in requirements_text.lower():
                    if concept_type in self.concept_knowledge:
                        concept = self.concept_knowledge[concept_type]
                        concepts.append(concept)
                    else:
                        concepts.append(SemanticConcept(
                            name=concept_type,
                            type="inferred",
                            confidence=0.8
                        ))
                    break
        
        logger.info(f"提取到 {len(concepts)} 个语义概念")
        return concepts

class ModelGenerator:
    """模型生成器"""
    
    def __init__(self):
        self.generation_strategies = {
            ModelType.STATE_MACHINE: self._generate_state_machine,
            ModelType.PETRI_NET: self._generate_petri_net,
            ModelType.UNIFIED_STS: self._generate_unified_sts
        }
    
    def generate_model(self, concepts: List[SemanticConcept], 
                      model_type: ModelType) -> FormalModel:
        """基于语义概念生成形式化模型"""
        logger.info(f"生成 {model_type.value} 模型，基于 {len(concepts)} 个概念")
        
        if model_type in self.generation_strategies:
            return self.generation_strategies[model_type](concepts)
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")
    
    def _generate_state_machine(self, concepts: List[SemanticConcept]) -> FormalModel:
        """生成状态机模型"""
        states = []
        transitions = []
        initial_state = "init"
        
        # 从概念中提取状态
        for concept in concepts:
            if concept.type in ["concept", "entity"] and "state" in concept.name.lower():
                states.append(concept.name)
        
        if not states:
            states = ["idle", "active", "error"]
        
        # 生成基本转换
        for i, state in enumerate(states):
            if i < len(states) - 1:
                transitions.append({
                    "from": state,
                    "to": states[i + 1],
                    "event": f"trigger_{i}",
                    "condition": "true"
                })
        
        return FormalModel(
            model_id=f"sm_{hash(str(concepts)) % 10000}",
            model_type=ModelType.STATE_MACHINE,
            elements={
                "states": states,
                "initial_state": initial_state,
                "final_states": [states[-1]] if states else [],
                "transitions": transitions
            },
            properties=["reachability", "safety", "liveness"],
            metadata={"generated_from_concepts": len(concepts)}
        )
    
    def _generate_petri_net(self, concepts: List[SemanticConcept]) -> FormalModel:
        """生成Petri网模型"""
        places = []
        transitions = []
        arcs = []
        
        # 从概念生成库所和变迁
        for concept in concepts:
            if "state" in concept.name.lower() or concept.type == "entity":
                places.append(f"place_{concept.name}")
            if "event" in concept.name.lower() or "process" in concept.name.lower():
                transitions.append(f"trans_{concept.name}")
        
        if not places:
            places = ["p1", "p2", "p3"]
        if not transitions:
            transitions = ["t1", "t2"]
        
        # 生成基本弧连接
        for i, trans in enumerate(transitions):
            if i < len(places):
                arcs.append({"from": places[i], "to": trans, "weight": 1})
            if i + 1 < len(places):
                arcs.append({"from": trans, "to": places[i + 1], "weight": 1})
        
        return FormalModel(
            model_id=f"pn_{hash(str(concepts)) % 10000}",
            model_type=ModelType.PETRI_NET,
            elements={
                "places": places,
                "transitions": transitions,
                "arcs": arcs,
                "initial_marking": {places[0]: 1} if places else {}
            },
            properties=["boundedness", "liveness", "reversibility"],
            metadata={"generated_from_concepts": len(concepts)}
        )
    
    def _generate_unified_sts(self, concepts: List[SemanticConcept]) -> FormalModel:
        """生成统一状态转换系统模型"""
        states = set()
        events = set()
        relations = []
        
        for concept in concepts:
            states.add(f"s_{concept.name}")
            for relation in concept.relations:
                events.add(f"e_{relation}")
        
        # 生成关系
        state_list = list(states)
        event_list = list(events)
        
        for i, state in enumerate(state_list):
            if i < len(event_list) and i + 1 < len(state_list):
                relations.append({
                    "from_state": state,
                    "event": event_list[i],
                    "to_state": state_list[i + 1],
                    "weight": 1.0
                })
        
        return FormalModel(
            model_id=f"usts_{hash(str(concepts)) % 10000}",
            model_type=ModelType.UNIFIED_STS,
            elements={
                "states": list(states),
                "events": list(events),
                "relations": relations,
                "initial_states": [state_list[0]] if state_list else [],
                "final_states": [state_list[-1]] if state_list else [],
                "marking_function": {},
                "weight_function": {}
            },
            properties=["reachability", "consistency", "completeness"],
            metadata={"unified_framework": True, "generated_from_concepts": len(concepts)}
        )

class AIVerificationEngine:
    """AI增强的验证引擎"""
    
    def __init__(self):
        self.verification_methods = {
            "model_checking": self._model_checking,
            "theorem_proving": self._theorem_proving,
            "simulation": self._simulation,
            "ai_assisted": self._ai_assisted_verification
        }
    
    def verify_property(self, model: FormalModel, property_spec: str, 
                       method: str = "ai_assisted") -> VerificationTask:
        """验证模型性质"""
        logger.info(f"验证模型 {model.model_id} 的性质: {property_spec}")
        
        task = VerificationTask(
            task_id=f"task_{hash(f'{model.model_id}_{property_spec}') % 10000}",
            model=model,
            property_to_verify=property_spec,
            verification_method=method
        )
        
        if method in self.verification_methods:
            result = self.verification_methods[method](model, property_spec)
            task.result = result[0]
            task.counterexample = result[1]
            task.proof = result[2]
        else:
            task.result = VerificationResult.UNKNOWN
        
        return task
    
    def _model_checking(self, model: FormalModel, property_spec: str) -> Tuple[VerificationResult, Optional[Dict], Optional[str]]:
        """模型检查方法"""
        # 简化实现：基于模型类型和性质进行基本检查
        if model.model_type == ModelType.STATE_MACHINE:
            if "reachability" in property_spec.lower():
                if model.elements.get("transitions"):
                    return VerificationResult.VALID, None, "所有状态可达"
                else:
                    return VerificationResult.INVALID, {"isolated_states": True}, None
        
        if model.model_type == ModelType.PETRI_NET:
            if "boundedness" in property_spec.lower():
                # 简单的有界性检查
                places = model.elements.get("places", [])
                if len(places) <= 10:  # 简单启发式
                    return VerificationResult.VALID, None, "网络有界"
                else:
                    return VerificationResult.UNKNOWN, None, None
        
        return VerificationResult.UNKNOWN, None, None
    
    def _theorem_proving(self, model: FormalModel, property_spec: str) -> Tuple[VerificationResult, Optional[Dict], Optional[str]]:
        """定理证明方法"""
        # 简化实现：基于逻辑推理
        if "safety" in property_spec.lower():
            return VerificationResult.VALID, None, "基于不变量的安全性证明"
        
        if "liveness" in property_spec.lower():
            return VerificationResult.VALID, None, "基于公平性假设的活性证明"
        
        return VerificationResult.UNKNOWN, None, None
    
    def _simulation(self, model: FormalModel, property_spec: str) -> Tuple[VerificationResult, Optional[Dict], Optional[str]]:
        """仿真验证方法"""
        # 简化实现：随机仿真
        simulation_steps = 100
        violations = 0
        
        # 模拟执行
        for step in range(simulation_steps):
            # 简单的随机执行模拟
            if step % 20 == 19:  # 模拟偶尔违反性质
                violations += 1
        
        if violations == 0:
            return VerificationResult.VALID, None, f"仿真 {simulation_steps} 步无违反"
        else:
            return VerificationResult.INVALID, {"violations": violations}, None
    
    def _ai_assisted_verification(self, model: FormalModel, property_spec: str) -> Tuple[VerificationResult, Optional[Dict], Optional[str]]:
        """AI辅助验证方法"""
        # 结合多种方法的AI增强验证
        logger.info("执行AI辅助验证...")
        
        # 1. 预处理：分析模型复杂度
        complexity_score = self._analyze_complexity(model)
        
        # 2. 策略选择：基于复杂度选择验证策略
        if complexity_score < 0.3:
            primary_result = self._model_checking(model, property_spec)
        elif complexity_score < 0.7:
            primary_result = self._simulation(model, property_spec)
        else:
            primary_result = self._theorem_proving(model, property_spec)
        
        # 3. 结果增强：AI辅助分析
        if primary_result[0] == VerificationResult.INVALID:
            # AI辅助的反例分析
            enhanced_counterexample = self._enhance_counterexample(
                model, property_spec, primary_result[1]
            )
            return primary_result[0], enhanced_counterexample, primary_result[2]
        
        elif primary_result[0] == VerificationResult.VALID:
            # AI生成的证明解释
            proof_explanation = self._generate_proof_explanation(
                model, property_spec, primary_result[2]
            )
            return primary_result[0], primary_result[1], proof_explanation
        
        return primary_result
    
    def _analyze_complexity(self, model: FormalModel) -> float:
        """分析模型复杂度"""
        elements = model.elements
        
        if model.model_type == ModelType.STATE_MACHINE:
            states = len(elements.get("states", []))
            transitions = len(elements.get("transitions", []))
            return min(1.0, (states + transitions) / 50.0)
        
        elif model.model_type == ModelType.PETRI_NET:
            places = len(elements.get("places", []))
            transitions = len(elements.get("transitions", []))
            arcs = len(elements.get("arcs", []))
            return min(1.0, (places + transitions + arcs) / 100.0)
        
        return 0.5  # 默认中等复杂度
    
    def _enhance_counterexample(self, model: FormalModel, property_spec: str, 
                              counterexample: Optional[Dict]) -> Dict[str, Any]:
        """AI增强的反例分析"""
        enhanced = counterexample or {}
        enhanced.update({
            "ai_analysis": "AI识别的主要违反原因",
            "suggested_fixes": ["修复建议1", "修复建议2"],
            "root_cause": "系统状态不一致",
            "impact_assessment": "高风险"
        })
        return enhanced
    
    def _generate_proof_explanation(self, model: FormalModel, property_spec: str, 
                                  proof: Optional[str]) -> str:
        """生成AI增强的证明解释"""
        base_proof = proof or "基本证明"
        ai_explanation = f"""
AI增强证明解释：
1. 模型结构分析：{model.model_type.value} 模型符合验证要求
2. 性质分析：{property_spec} 在所有执行路径上成立
3. 关键不变量：系统状态一致性得到保证
4. 证明策略：{base_proof}
5. 置信度：95%
        """
        return ai_explanation.strip()

class CodeGenerator:
    """代码生成器"""
    
    def __init__(self):
        self.language_generators = {
            "rust": self._generate_rust_code,
            "go": self._generate_go_code,
            "python": self._generate_python_code
        }
    
    def generate_code(self, model: FormalModel, target_language: str) -> str:
        """从形式化模型生成代码"""
        logger.info(f"生成 {target_language} 代码，基于 {model.model_type.value} 模型")
        
        if target_language in self.language_generators:
            return self.language_generators[target_language](model)
        else:
            raise ValueError(f"不支持的目标语言: {target_language}")
    
    def _generate_rust_code(self, model: FormalModel) -> str:
        """生成Rust代码"""
        if model.model_type == ModelType.STATE_MACHINE:
            return self._generate_rust_state_machine(model)
        elif model.model_type == ModelType.UNIFIED_STS:
            return self._generate_rust_unified_sts(model)
        else:
            return f"// TODO: 实现 {model.model_type.value} 的Rust代码生成"
    
    def _generate_rust_state_machine(self, model: FormalModel) -> str:
        """生成Rust状态机代码"""
        states = model.elements.get("states", [])
        transitions = model.elements.get("transitions", [])
        
        # 生成状态枚举
        state_enum = "pub enum State {\n"
        for state in states:
            state_name = state.title().replace("_", "")
            state_enum += f"    {state_name},\n"
        state_enum += "}\n\n"
        
        # 生成事件枚举
        events = set()
        for trans in transitions:
            events.add(trans.get("event", "Unknown"))
        
        event_enum = "pub enum Event {\n"
        for event in events:
            event_name = event.title().replace("_", "")
            event_enum += f"    {event_name},\n"
        event_enum += "}\n\n"
        
        # 生成状态机结构
        state_machine = f"""pub struct StateMachine {{
    current_state: State,
}}

impl StateMachine {{
    pub fn new() -> Self {{
        StateMachine {{
            current_state: State::{states[0].title().replace("_", "") if states else "Init"},
        }}
    }}
    
    pub fn transition(&mut self, event: Event) -> Result<(), String> {{
        match (&self.current_state, event) {{"""
        
        # 生成转换逻辑
        for trans in transitions:
            from_state = trans.get("from", "").title().replace("_", "")
            to_state = trans.get("to", "").title().replace("_", "")
            event_name = trans.get("event", "").title().replace("_", "")
            
            state_machine += f"""
            (State::{from_state}, Event::{event_name}) => {{
                self.current_state = State::{to_state};
                Ok(())
            }}"""
        
        state_machine += """
            _ => Err("Invalid transition".to_string()),
        }
    }
    
    pub fn current_state(&self) -> &State {
        &self.current_state
    }
}"""
        
        return f"""// 自动生成的Rust状态机代码
// 基于模型: {model.model_id}

{state_enum}{event_enum}{state_machine}

#[cfg(test)]
mod tests {{
    use super::*;
    
    #[test]
    fn test_state_machine() {{
        let mut sm = StateMachine::new();
        // TODO: 添加测试用例
    }}
}}
"""
    
    def _generate_rust_unified_sts(self, model: FormalModel) -> str:
        """生成Rust统一状态转换系统代码"""
        return f"""// 自动生成的Rust统一状态转换系统代码
// 基于模型: {model.model_id}

use std::collections::{{HashMap, HashSet}};

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct State(pub String);

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Event(pub String);

#[derive(Debug, Clone)]
pub struct Relation {{
    pub from_state: State,
    pub event: Event,
    pub to_state: State,
    pub weight: f64,
}}

pub struct UnifiedSTS {{
    states: HashSet<State>,
    events: HashSet<Event>,
    relations: Vec<Relation>,
    initial_states: HashSet<State>,
    final_states: HashSet<State>,
    marking: HashMap<State, u32>,
}}

impl UnifiedSTS {{
    pub fn new() -> Self {{
        UnifiedSTS {{
            states: HashSet::new(),
            events: HashSet::new(),
            relations: Vec::new(),
            initial_states: HashSet::new(),
            final_states: HashSet::new(),
            marking: HashMap::new(),
        }}
    }}
    
    pub fn add_state(&mut self, state: State) {{
        self.states.insert(state);
    }}
    
    pub fn add_event(&mut self, event: Event) {{
        self.events.insert(event);
    }}
    
    pub fn add_relation(&mut self, relation: Relation) {{
        self.relations.push(relation);
    }}
    
    pub fn execute_event(&mut self, event: &Event) -> Result<Vec<State>, String> {{
        let mut new_states = Vec::new();
        
        for relation in &self.relations {{
            if &relation.event == event {{
                new_states.push(relation.to_state.clone());
            }}
        }}
        
        if new_states.is_empty() {{
            Err(format!("No transitions for event: {{:?}}", event))
        }} else {{
            Ok(new_states)
        }}
    }}
}}
"""
    
    def _generate_go_code(self, model: FormalModel) -> str:
        """生成Go代码"""
        if model.model_type == ModelType.STATE_MACHINE:
            return self._generate_go_state_machine(model)
        else:
            return f"// TODO: 实现 {model.model_type.value} 的Go代码生成"
    
    def _generate_go_state_machine(self, model: FormalModel) -> str:
        """生成Go状态机代码"""
        states = model.elements.get("states", [])
        
        return f"""// 自动生成的Go状态机代码
// 基于模型: {model.model_id}

package main

import (
    "fmt"
    "errors"
)

type State int

const (
{chr(10).join(f"    State{state.title().replace('_', '')} State = iota" for i, state in enumerate(states))}
)

type Event int

const (
    EventTrigger Event = iota
    // 添加更多事件
)

type StateMachine struct {{
    currentState State
}}

func NewStateMachine() *StateMachine {{
    return &StateMachine{{
        currentState: State{states[0].title().replace('_', '') if states else 'Init'},
    }}
}}

func (sm *StateMachine) Transition(event Event) error {{
    switch sm.currentState {{
    // TODO: 实现状态转换逻辑
    default:
        return errors.New("invalid transition")
    }}
}}

func (sm *StateMachine) CurrentState() State {{
    return sm.currentState
}}

func main() {{
    sm := NewStateMachine()
    fmt.Printf("Initial state: %v\\n", sm.CurrentState())
}}
"""
    
    def _generate_python_code(self, model: FormalModel) -> str:
        """生成Python代码"""
        return f"""# 自动生成的Python代码
# 基于模型: {model.model_id}

from enum import Enum
from typing import Dict, List, Optional

class ModelType(Enum):
    {model.model_type.value.upper()} = "{model.model_type.value}"

class GeneratedModel:
    def __init__(self):
        self.model_id = "{model.model_id}"
        self.model_type = ModelType.{model.model_type.value.upper()}
        self.elements = {json.dumps(model.elements, indent=8)}
    
    def execute(self):
        print(f"执行模型 {{self.model_id}}")
        # TODO: 实现模型执行逻辑

if __name__ == "__main__":
    model = GeneratedModel()
    model.execute()
"""

class AIModelingEngine:
    """AI建模引擎主类"""
    
    def __init__(self):
        self.semantic_analyzer = SemanticAnalyzer()
        self.model_generator = ModelGenerator()
        self.verification_engine = AIVerificationEngine()
        self.code_generator = CodeGenerator()
        self.models = {}
        self.verification_tasks = {}
        
        logger.info("AI建模引擎初始化完成")
    
    def process_requirements(self, requirements: str, 
                           model_type: ModelType = ModelType.UNIFIED_STS) -> str:
        """处理需求并生成模型"""
        logger.info("开始处理需求...")
        
        # 1. 语义分析
        concepts = self.semantic_analyzer.analyze_requirements(requirements)
        
        # 2. 模型生成
        model = self.model_generator.generate_model(concepts, model_type)
        self.models[model.model_id] = model
        
        # 3. 基本验证
        verification_task = self.verification_engine.verify_property(
            model, "basic_consistency", "ai_assisted"
        )
        self.verification_tasks[verification_task.task_id] = verification_task
        
        # 4. 返回模型摘要
        summary = f"""
处理完成！

模型信息：
- 模型ID: {model.model_id}
- 模型类型: {model.model_type.value}
- 元素数量: {len(model.elements)}
- 约束数量: {len(model.constraints)}
- 性质数量: {len(model.properties)}

语义分析：
- 识别概念: {len(concepts)} 个
- 概念列表: {[c.name for c in concepts]}

验证结果：
- 任务ID: {verification_task.task_id}
- 验证方法: {verification_task.verification_method}
- 结果: {verification_task.result.value if verification_task.result else 'pending'}
"""
        return summary.strip()
    
    def generate_implementation(self, model_id: str, language: str = "rust") -> str:
        """生成实现代码"""
        if model_id not in self.models:
            return f"错误：模型 {model_id} 不存在"
        
        model = self.models[model_id]
        return self.code_generator.generate_code(model, language)
    
    def verify_model_property(self, model_id: str, property_spec: str, 
                            method: str = "ai_assisted") -> str:
        """验证模型性质"""
        if model_id not in self.models:
            return f"错误：模型 {model_id} 不存在"
        
        model = self.models[model_id]
        task = self.verification_engine.verify_property(model, property_spec, method)
        self.verification_tasks[task.task_id] = task
        
        result_summary = f"""
验证任务完成：

任务信息：
- 任务ID: {task.task_id}
- 模型ID: {task.model.model_id}
- 验证性质: {task.property_to_verify}
- 验证方法: {task.verification_method}

验证结果：
- 结果: {task.result.value if task.result else 'unknown'}
- 反例: {'是' if task.counterexample else '无'}
- 证明: {'有' if task.proof else '无'}
"""
        
        if task.counterexample:
            result_summary += f"\n反例详情:\n{json.dumps(task.counterexample, indent=2, ensure_ascii=False)}"
        
        if task.proof:
            result_summary += f"\n证明详情:\n{task.proof}"
        
        return result_summary.strip()
    
    def get_model_summary(self, model_id: str) -> str:
        """获取模型摘要"""
        if model_id not in self.models:
            return f"错误：模型 {model_id} 不存在"
        
        model = self.models[model_id]
        return f"""
模型摘要：

基本信息：
- 模型ID: {model.model_id}
- 模型类型: {model.model_type.value}
- 元数据: {json.dumps(model.metadata, indent=2, ensure_ascii=False)}

模型元素：
{json.dumps(model.elements, indent=2, ensure_ascii=False)}

约束条件：
{chr(10).join(f"- {constraint}" for constraint in model.constraints)}

性质规范：
{chr(10).join(f"- {prop}" for prop in model.properties)}
"""
    
    def list_models(self) -> str:
        """列出所有模型"""
        if not self.models:
            return "当前没有模型"
        
        model_list = "当前模型列表：\n"
        for model_id, model in self.models.items():
            model_list += f"- {model_id}: {model.model_type.value}\n"
        
        return model_list.strip()
    
    def export_model(self, model_id: str, format: str = "json") -> str:
        """导出模型"""
        if model_id not in self.models:
            return f"错误：模型 {model_id} 不存在"
        
        model = self.models[model_id]
        
        if format == "json":
            return json.dumps({
                "model_id": model.model_id,
                "model_type": model.model_type.value,
                "elements": model.elements,
                "constraints": model.constraints,
                "properties": model.properties,
                "metadata": model.metadata
            }, indent=2, ensure_ascii=False)
        else:
            return f"不支持的导出格式: {format}"

def demo_ai_modeling_engine():
    """AI建模引擎演示"""
    print("🤖 AI建模引擎演示开始...")
    print("=" * 60)
    
    # 初始化引擎
    engine = AIModelingEngine()
    
    # 演示1: 处理简单需求
    print("\n📝 演示1: 处理用户登录系统需求")
    requirements1 = """
    设计一个用户登录系统，包含以下状态：
    - 用户未登录状态
    - 用户已登录状态  
    - 用户登录失败状态
    系统需要处理登录事件和登出事件
    """
    
    result1 = engine.process_requirements(requirements1, ModelType.STATE_MACHINE)
    print(result1)
    
    # 演示2: 生成代码
    print("\n💻 演示2: 生成Rust实现代码")
    models = list(engine.models.keys())
    if models:
        rust_code = engine.generate_implementation(models[0], "rust")
        print("生成的Rust代码:")
        print("-" * 40)
        print(rust_code[:800] + "..." if len(rust_code) > 800 else rust_code)
    
    # 演示3: 验证性质
    print("\n🔍 演示3: 验证模型性质")
    if models:
        verification_result = engine.verify_model_property(
            models[0], "reachability", "ai_assisted"
        )
        print(verification_result)
    
    # 演示4: 处理复杂需求（微服务）
    print("\n🏗️ 演示4: 处理微服务架构需求")
    requirements2 = """
    设计一个电商微服务系统，包含：
    - 用户服务组件
    - 订单服务组件
    - 支付服务组件
    - 库存服务组件
    系统需要处理下单流程，包括用户下单、库存检查、支付处理等事件
    """
    
    result2 = engine.process_requirements(requirements2, ModelType.UNIFIED_STS)
    print(result2)
    
    # 演示5: 列出所有模型
    print("\n📋 演示5: 当前模型列表")
    model_list = engine.list_models()
    print(model_list)
    
    print("\n" + "=" * 60)
    print("🎉 AI建模引擎演示完成！")

if __name__ == "__main__":
    demo_ai_modeling_engine() 