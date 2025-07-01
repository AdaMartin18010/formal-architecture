# verification_engine.py
# 自动化验证工具核心引擎

import yaml
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any
from collections import deque
import z3
import json

class VerificationStatus(Enum):
    """验证任务的状态"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

@dataclass
class VerificationTask:
    """定义一个验证任务"""
    task_id: str
    target_model_id: str
    rule_ids: List[str]
    status: VerificationStatus = VerificationStatus.PENDING
    result: Any = None

@dataclass
class VerificationRule:
    """定义一个验证规则"""
    rule_id: str
    name: str
    description: str
    algorithm: str # e.g., "StaticAnalysis", "DeductiveVerification"
    parameters: Dict[str, Any]

class RuleManager:
    """
    规则管理器
    - 负责从外部文件加载和管理验证规则
    """
    def __init__(self, rule_file_path: str):
        self.rule_file_path = rule_file_path
        self._rules = self._load_rules()
        print(f"规则管理器: 成功加载 {len(self._rules)} 条规则 from {self.rule_file_path}")

    def _load_rules(self) -> Dict[str, VerificationRule]:
        """从YAML文件加载规则"""
        try:
            with open(self.rule_file_path, 'r', encoding='utf-8') as f:
                rules_data = yaml.safe_load(f)
            
            rules = {}
            for rule_data in rules_data.get('rules', []):
                rule = VerificationRule(**rule_data)
                rules[rule.rule_id] = rule
            return rules
        except FileNotFoundError:
            print(f"错误: 规则文件未找到 at {self.rule_file_path}")
            return {}
        except Exception as e:
            print(f"错误: 加载规则文件失败: {e}")
            return {}

    def get_rule(self, rule_id: str) -> VerificationRule:
        """根据ID获取规则"""
        return self._rules.get(rule_id)

    def get_all_rules(self) -> List[VerificationRule]:
        """获取所有规则"""
        return list(self._rules.values())

class TaskScheduler:
    """
    任务调度器
    - 负责接收、排队和调度验证任务
    """
    def __init__(self):
        self._task_queue = deque()
        self._task_history = {} # 保存已完成或失败的任务
        print("任务调度器: 初始化成功")

    def submit_task(self, task: VerificationTask):
        """提交一个新任务到队列"""
        self._task_queue.append(task)
        print(f"任务调度器: 新任务 {task.task_id} 已提交")

    def get_next_task(self) -> VerificationTask:
        """从队列中获取下一个待处理任务"""
        if not self._task_queue:
            return None
        
        task = self._task_queue.popleft()
        task.status = VerificationStatus.RUNNING
        print(f"任务调度器: 任务 {task.task_id} 开始执行")
        return task

    def complete_task(self, task: VerificationTask, result: Any):
        """标记一个任务为完成状态"""
        task.status = VerificationStatus.COMPLETED
        task.result = result
        self._task_history[task.task_id] = task
        print(f"任务调度器: 任务 {task.task_id} 已完成")

class KnowledgeGraphService:
    """
    模拟知识图谱服务
    - 提供查询模型信息和更新验证状态的接口
    """
    def __init__(self):
        # 模拟的图数据库
        self._db = {
            "UMS-Module-B": {
                "contracts": {
                    "increase_post_condition": {
                        "pre": "y > 0",
                        "post": "return > x",
                        "body_z3": "z3.ForAll([x, y], z3.Implies(y > 0, x + y > x))",
                        "negation_z3": "z3.And(y > 0, x + y <= x)" # 用于寻找反例
                    }
                },
                "verification_status": {}
            },
            "CounterModel": {
                "contracts": {},
                "verification_status": {}
            }
        }
        print("知识图谱服务: 初始化成功，加载了模拟数据。")

    def get_model_contracts(self, model_id: str) -> Dict[str, Any]:
        """根据模型ID获取其契约"""
        return self._db.get(model_id, {}).get("contracts")

    def update_verification_status(self, model_id: str, rule_id: str, result: Dict[str, Any]):
        """更新模型节点的验证状态"""
        if model_id in self._db:
            status_entry = {
                "status": "COMPLETED",
                "result": result
            }
            self._db[model_id]["verification_status"][rule_id] = status_entry
            print(f"知识图谱服务: 已更新模型 '{model_id}' 的验证状态 for rule '{rule_id}'")
        else:
            print(f"知识图谱服务: 警告 - 无法找到模型 '{model_id}' 来更新状态")

    def print_db(self):
        print("\n--- 知识图谱最终状态 ---")
        print(json.dumps(self._db, default=str, indent=2))
        print("--------------------------\n")

class VerificationEngine:
    """
    验证引擎主类
    - 协调任务调度器、规则管理器和验证插件
    """
    def __init__(self, scheduler: "TaskScheduler", rule_manager: "RuleManager", kg_service: "KnowledgeGraphService"):
        self._scheduler = scheduler
        self._rule_manager = rule_manager
        self._kg_service = kg_service
        self._plugins = {}
        self.register_default_plugins()
        print("验证引擎: 初始化成功并注册默认插件")

    def register_plugin(self, algorithm_name: str, plugin: Any):
        """注册一个验证插件"""
        self._plugins[algorithm_name] = plugin
        print(f"验证引擎: 成功注册插件 for algorithm '{algorithm_name}'")

    def register_default_plugins(self):
        """注册所有默认的验证插件"""
        self.register_plugin("StaticAnalysis", StaticAnalysisPlugin())
        self.register_plugin("RuntimeVerification", RuntimeVerificationPlugin())
        # 传入kg_service
        self.register_plugin("DeductiveVerification", DeductiveVerificationPlugin(self._kg_service))
        self.register_plugin("ModelChecking", ModelCheckingPlugin())

    def run_single_task(self):
        """处理单个任务"""
        task = self._scheduler.get_next_task()
        if not task:
            print("验证引擎: 任务队列为空，无事可做。")
            return

        print(f"--- 开始处理任务: {task.task_id} ---")
        task_results = {}
        for rule_id in task.rule_ids:
            rule = self._rule_manager.get_rule(rule_id)
            if not rule:
                print(f"警告: 任务 {task.task_id} 中的规则 {rule_id} 未找到，已跳过。")
                continue

            plugin = self._plugins.get(rule.algorithm)
            if not plugin:
                print(f"警告: 规则 {rule.rule_id} 所需的算法插件 '{rule.algorithm}' 未注册，已跳过。")
                task_results[rule_id] = {"status": "SKIPPED", "reason": f"Plugin for {rule.algorithm} not found."}
                continue

            try:
                print(f"  -> 应用规则 '{rule.name}' (使用插件: {type(plugin).__name__})")
                result = plugin.execute(task.target_model_id, rule.parameters)
                task_results[rule_id] = result
                # 验证成功后，更新知识图谱
                self._kg_service.update_verification_status(task.target_model_id, rule_id, result)
            except Exception as e:
                print(f"错误: 执行规则 {rule.rule_id} 失败: {e}")
                task_results[rule_id] = {"status": "FAILED", "error": str(e)}

        self._scheduler.complete_task(task, task_results)
        print(f"--- 任务处理完成: {task.task_id} ---")

    def run_all_tasks(self):
        """循环处理所有任务直到队列为空"""
        print("\n===================================")
        print("验证引擎: 开始批量处理所有任务...")
        print("===================================")
        while self._scheduler._task_queue:
            self.run_single_task()
        print("\n验证引擎: 所有任务处理完毕。")


# --- 验证插件实现 ---

class StaticAnalysisPlugin:
    """
    静态分析插件
    - 包含各种静态分析算法的实现
    """
    def execute(self, model_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行静态分析"""
        # 这是一个模拟实现
        # 实际应用中，这里会解析模型文件，构建依赖图等
        print(f"    [静态分析插件]: 正在对模型 '{model_id}' 进行循环依赖检查...")
        
        # 模拟结果：假设模型A没有循环依赖，模型B有
        if model_id == "UMS-Module-A":
            return {"has_cycle": False, "details": "No circular dependency found."}
        elif model_id == "UMS-Module-B":
            return {"has_cycle": True, "details": "Found cycle: B -> D -> E -> B", "path": ["B", "D", "E", "B"]}
        else:
            return {"has_cycle": False, "details": "Model not recognized, assuming no cycle."}

class RuntimeVerificationPlugin:
    """
    运行时验证插件
    - 模拟在模型执行期间监控其行为
    """
    def execute(self, model_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行运行时验证"""
        contract_name = params.get("contract_name", "UnknownContract")
        print(f"    [运行时验证插件]: 正在对模型 '{model_id}' 进行运行时监控，检查契约: '{contract_name}'...")

        # 模拟运行时行为和检查
        # 假设模型 'UMS-Module-C' 在其操作中会触发一个除零错误
        if model_id == "UMS-Module-C" and contract_name == "NoZeroDivisor":
            # 模拟执行一系列操作
            operations = [
                {"op": "add", "args": [5, 10]},
                {"op": "divide", "args": [20, 0]}, # 违反契约的操作
                {"op": "subtract", "args": [10, 5]},
            ]
            
            for op in operations:
                if op["op"] == "divide" and op["args"][1] == 0:
                    print(f"      -> 发现违反契约 '{contract_name}' 的行为! 操作: {op}")
                    return {
                        "contract_violated": True,
                        "contract_name": contract_name,
                        "details": "Division by zero occurred during execution.",
                        "violating_operation": op,
                    }
        
        print(f"      -> 模型 '{model_id}' 的执行未违反契约 '{contract_name}'。")
        return {"contract_violated": False, "contract_name": contract_name}

class DeductiveVerificationPlugin:
    """
    演绎验证插件
    - 使用Z3 SMT求解器来验证模型的契约
    """
    def __init__(self, kg_service: KnowledgeGraphService):
        self._kg_service = kg_service

    def execute(self, model_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行演绎验证"""
        print(f"    [演绎验证插件]: 正在对模型 '{model_id}' 的契约进行逻辑证明...")

        # 1. 从知识图谱获取契约
        contracts = self._kg_service.get_model_contracts(model_id)
        if not contracts:
            return {"contract_satisfied": "Unknown", "details": f"No contracts found for model {model_id} in KG."}

        # 假设我们只验证第一个找到的契约
        contract_name, contract_data = next(iter(contracts.items()))
        print(f"      -> 从知识图谱加载契约: '{contract_name}'")
        
        x = z3.Int('x')
        y = z3.Int('y')
        solver = z3.Solver()
        
        # 2. 使用从KG获取的公式
        try:
            # eval() 有安全风险，此处仅为模拟，实际应用需使用安全的AST解析
            formula = eval(contract_data["negation_z3"]) 
            solver.add(formula)
        except Exception as e:
            return {"contract_satisfied": "Failed", "details": f"Failed to parse Z3 formula from KG: {e}"}

        print(f"      -> 正在求解公式: {contract_data['body_z3']}")
        check_result = solver.check()

        if check_result == z3.sat:
            # 找到了反例
            model = solver.model()
            print(f"      -> 发现反例! 契约被违反。模型: {model}")
            return {
                "contract_satisfied": False,
                "details": "The contract is violated.",
                "counterexample": str(model)
            }
        elif check_result == z3.unsat:
            # 未找到反例，证明成立
            print(f"      -> 证明成功! 契约得到满足。")
            return {"contract_satisfied": True, "details": "The contract holds."}
        else:
            # 求解器无法确定
            print(f"      -> 求解器无法确定满足性。")
            return {"contract_satisfied": "Unknown", "details": "Solver returned unknown."}

class ModelCheckingPlugin:
    """
    模型检测插件
    - 使用有界模型检测（BMC）方法来寻找违反安全属性的反例
    """
    def execute(self, model_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行有界模型检测"""
        k_bound = params.get("k_bound", 10) # 展开步数
        print(f"    [模型检测插件]: 正在对模型 '{model_id}' 进行有界模型检测 (k={k_bound})...")

        # 这是一个高度简化的模拟，实际应用中会复杂得多
        # 1. 假设我们有一个简单的USTS模型：一个计数器
        #    - 状态: (counter: Int)
        #    - 初始状态: counter == 0
        #    - 转换: counter' = counter + 1
        # 2. 假设我们要验证的安全属性 P: counter < 5
        # 3. BMC要检查是否存在一条路径，在k步内使得 ¬P (即 counter >= 5) 成立

        s = z3.Solver()
        
        # 创建k+1个状态变量，代表 k 步执行
        states = [z3.Int(f"s_{i}") for i in range(k_bound + 1)]

        # 添加初始状态约束
        s.add(states[0] == 0)

        # 添加转换关系约束
        for i in range(k_bound):
            s.add(states[i+1] == states[i] + 1)
        
        # 添加 "坏" 状态的断言 (属性 ¬P 的可满足性)
        # 检查在0到k步之间，是否有任何一个状态的 counter >= 5
        bad_state_assertion = z3.Or([st >= 5 for st in states])
        s.add(bad_state_assertion)
        
        print(f"      -> 正在求解:是否存在路径在 {k_bound} 步内达到 state >= 5")
        check_result = s.check()

        if check_result == z3.sat:
            model = s.model()
            path = [model.eval(st).as_long() for st in states]
            print(f"      -> 发现反例! 路径: {path}")

            # 生成Mermaid图
            mermaid_graph = "graph TD;\n"
            for i in range(len(path) - 1):
                style = ""
                if path[i+1] >= 5: # 假设5是违规状态
                    style = "style " + str(i+1) + " fill:#f96,stroke:#333,stroke-width:2px"
                mermaid_graph += f"    S{i}[\"State {i}<br/>counter = {path[i]}\"] --> S{i+1}[\"State {i+1}<br/>counter = {path[i+1]}\"];\n"
                if style:
                    mermaid_graph += style + "\n"

            return {
                "property_violated": True,
                "details": f"Safety property violated within {k_bound} steps.",
                "counterexample_path": str(path),
                "mermaid_graph": mermaid_graph
            }
        else: # unsat
            print(f"      -> 未发现反例。属性在 {k_bound} 步内得到满足。")
            return {"property_violated": False, "details": f"Property holds for {k_bound} steps."}

# --- 示例用法 ---

def create_dummy_rule_file(filepath: str):
    """创建一个示例规则文件用于测试"""
    rules_content = {
        "rules": [
            {
                "rule_id": "RULE-001",
                "name": "循环依赖检查",
                "description": "检查UMS模块之间是否存在循环依赖",
                "algorithm": "StaticAnalysis",
                "parameters": {"depth": 3}
            },
            {
                "rule_id": "RULE-002",
                "name": "契约满足性检查",
                "description": "使用Z3验证模块实现是否满足前置/后置条件",
                "algorithm": "DeductiveVerification",
                "parameters": {"solver_timeout": 5000}
            },
            {
                "rule_id": "RULE-004",
                "name": "安全性模型检测",
                "description": "使用有界模型检测（BMC）验证系统是否会在k步内违反安全属性",
                "algorithm": "ModelChecking",
                "parameters": {"k_bound": 10}
            }
        ]
    }
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(rules_content, f)

if __name__ == '__main__':
    # 1. 创建/更新示例规则文件
    rule_file = "verification_rules.yaml"
    create_dummy_rule_file(rule_file)

    # 2. 初始化规则管理器、知识图谱服务
    rule_manager = RuleManager(rule_file_path=rule_file)
    kg_service = KnowledgeGraphService()
    
    # 3. 初始化任务调度器
    scheduler = TaskScheduler()

    # 4. 初始化验证引擎
    engine = VerificationEngine(scheduler, rule_manager, kg_service)

    # 5. 创建并提交验证任务
    print("\n提交任务...")
    task1 = VerificationTask(
        task_id="TASK-001",
        target_model_id="UMS-Module-A",
        rule_ids=["RULE-001"]
    )
    scheduler.submit_task(task1)

    task2 = VerificationTask(
        task_id="TASK-002",
        target_model_id="UMS-Module-B",
        rule_ids=["RULE-001", "RULE-002"]
    )
    scheduler.submit_task(task2)

    task3 = VerificationTask(
        task_id="TASK-003",
        target_model_id="UMS-Module-C",
        rule_ids=["RULE-003"]
    )
    scheduler.submit_task(task3)

    # 创建并提交模型检测任务
    task4 = VerificationTask(
        task_id="TASK-004",
        target_model_id="CounterModel",
        rule_ids=["RULE-004"]
    )
    scheduler.submit_task(task4)

    # 6. 验证引擎执行所有任务
    engine.run_all_tasks()
    
    # 7. 打印知识图谱最终状态
    kg_service.print_db()

    print("\n最终任务历史 (包含可视化报告):")
    final_history = scheduler._task_history
    for task_id, task_data in final_history.items():
        print(f"--- Task: {task_id} ---")
        print(json.dumps(task_data, default=str, indent=2))
        # 检查是否有Mermaid图需要打印
        if task_data.result:
            for rule_id, result_data in task_data.result.items():
                if isinstance(result_data, dict) and "mermaid_graph" in result_data:
                    print(f"\n>>>> Mermaid 可视化报告 for rule {rule_id}:")
                    print("```mermaid")
                    print(result_data["mermaid_graph"])
                    print("```")
        print("---------------------\n") 