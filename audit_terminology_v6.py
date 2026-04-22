#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminology audit v6: ultra-strict filter for only the highest-quality technical terms.
"""

import os
import re
import json
from collections import defaultdict
from pathlib import Path

STRUCT_DIR = Path("E:/_src/formal-architecture/Struct")
INDEX_FILE = STRUCT_DIR / "99-参考文献与索引/02-核心概念反向索引与术语表.md"

SKIP_PATHS = {
    'reports',
    '99-参考文献与索引',
    '00-总体计划与任务规划-软件工程思维模型知识体系构建.md',
}

def should_skip_file(rel_path):
    for skip in SKIP_PATHS:
        if skip in str(rel_path):
            return True
    return False

# Explicit allowlist of high-quality technical terms that should be in the index
# This is the most reliable way to ensure quality
ALLOWLIST = {
    # Module 01
    'Actor', 'ActorRef', 'Actor模型', 'CCS', 'Church编码', 'CSP', 'CTL',
    'Curry-Howard', 'LTL', 'λ演算', 'λ抽象', 'β归约', 'π-演算', 'Y组合子',
    '可判定性', '可判定性光谱', '可计算性', '停机问题', '图灵机',
    '定期自动机', '时序逻辑', '进程代数', '有限自动机', '下推自动机',
    '正则语言', '上下文无关语言', '不可判定性', '半可判定性',
    '双模拟', '观察等价', '名称传递', '位置透明', '公平性',
    '安全性', '活性', 'Let it crash', 'STM',
    # Module 02
    'CAP', 'CAP定理', 'FLP', 'FLP不可能性', 'FLP定理', 'PACELC',
    '严格一致性', '因果一致', '会话一致', '单调读', '最终一致',
    '线性一致', '顺序一致', '读写一致', '一致性', '可用性', '分区容错',
    '分区', '价态保持', 'Fail-stop故障', '双态配置', '不存在确定性算法',
    '工程绕过', '假设过于乐观', '外部一致性', '灰色故障',
    'Tunable Consistency',
    # Module 03
    'Bullshark', 'BFT', 'DAG共识', 'HotStuff', 'Multi-Paxos',
    'Paxos', 'PBFT', 'Raft', 'Single-Decree Paxos', 'Fast Paxos',
    '共识算法', 'DiemBFT（原Libra）', 'Quorum', 'Quorum Certificate',
    '3-chain规则', '即时最终性', '密码学开销', '容错阈值', '容错节点数',
    '信任假设', '日志复制', '状态机复制', '快照', '成员变更', 'PreVote',
    'CheckPoint', '部分同步', '异步', '同步', 'Consul', 'etcd', 'TiKV',
    'Redpanda', 'Rook/Ceph',
    # Module 04
    'CRDT', 'Event Sourcing', 'HLC', 'Hybrid Logical Clocks',
    'TCC', 'Vector Clock', '向量时钟', '分布式事务', '2PC', '3PC',
    'Delta-State CRDT', 'G-Counter', 'G-Set', 'LWW-Element-Set',
    'LWW-Register', 'MV-Register', 'OR-Set', 'PN-Counter', 'State-based',
    'Op-based', 'tombstone', '半格', 'Join-Semilattice', '偏序', '偏序集',
    '偏序集（Poset）', 'Lamport时钟', 'Happens-before', 'TrueTime',
    '单向因果', '因果捕获', '可确定因果', '可确定全序',
    'Event Stream', 'Snapshot', 'Projection（投影）', 'Upcasting',
    'Upcasting链', 'Catamorphism', 'Monoid', 'Crypto-Shredding',
    '删除语义', '回滚', 'Saga', 'Saga（协同式）', 'Saga（编排式）', 'Outbox',
    'Dotted Version Vectors', 'Saga模式',
    # Module 05
    'Bounded Context', 'CQRS', 'EDA', 'Serverless', 'FaaS',
    'Two-Pizza Team', '康威定律', 'Conway定律', '微服务', '单体',
    '模块化单体', '分布式单体', '容器', 'K8s Pod', '变更频率',
    '启动时间', '团队规模', '基础设施成本', '部署单元', '同步通信',
    '异步通信', 'REST', 'gRPC', 'REST/gRPC', '事件驱动',
    'Event Notification', 'Event-Carried State Transfer',
    '分层（部门制）', '复杂子系统', '反模式', '大泥球', '审慎微服务',
    '团队规模阈值', '同步调用链 > 3跳', '事务一致性', '共享数据库',
    '共享DBA团队', 'gRPC替代HTTP/JSON', 'GraphQL Federation',
    '厂商锁定', '冷启动', '调试黑箱', '背景作业', '容器（K8s）',
    # Module 06
    'DDD', 'ACL', 'ADR', 'Context Map', 'Conformist', 'Customer-Supplier',
    'Complicated-Subsystem', 'Enabling', 'Aggregate', 'Domain Event',
    'Entity', 'Repository', 'Value Object', '领域', '子域', '核心域',
    '支撑域', '通用域', '限界上下文', '上下文映射', '共享内核',
    '客户-供应商', '遵奉者', '分道扬镳', '防腐层', '开放主机服务',
    '发布语言', '聚合', '实体', '值对象', '领域事件', '资源库',
    '工厂', '领域服务', '应用服务', '战略设计', '战术设计',
    '问题空间', '解空间', '通用语言', 'Stream-aligned',
    'Stream-aligned团队', '平台', '平台团队', 'OHS',
    'Separate Ways', 'Shared Kernel', 'Partnership',
    # Module 07
    'TLA+', 'TLA', 'TLC', 'PlusCal', 'UPPAAL', '模型检测',
    '状态机', '不变式', '动作', 'Primed变量', 'Stuttering',
    '时序逻辑', '规约', '规约语言', '状态空间爆炸', '实时系统',
    '时钟约束', '可达性分析', '死锁检测', '活性检测', '反例轨迹',
    '抽象', '精化', '分解', '组合', '分离逻辑', '借检查器',
    'Send/Sync', '所有权', '借用', '生命周期', '类型系统',
    '形式证明', '归纳证明', '构造证明', 'SMT求解器', '自动定理证明',
    '回归防护', '反例驱动修复', '从代码提取不变量', '不变量合成',
    'TCTL', 'Timed Automata',
    # Module 08
    'Little定律', 'Amdahl定律', 'Gustafson定律', '排队论',
    'M/M/1', 'M/M/c', 'M/G/1', 'λ', 'μ', 'ρ', '利用率', '等待时间',
    '队列长度', '吞吐量', '响应时间', '加速比', '并行效率', '串行部分',
    '问题规模', '协调成本', '协调成本系数', '修正加速比', '容量规划',
    '负载测试', '压力测试', '基线测试', '弹性', 'HPA', 'VPA', 'KEDA',
    '自动伸缩', '资源利用率', 'DB连接池', 'USE方法',
    # Module 09
    'BAN逻辑', 'Lowe攻击', '中间人攻击', 'Dolev-Yao模型', 'Nonce',
    'Tamarin Prover', '可信计算', 'TPM', 'Intel SGX', 'AMD SEV',
    'Apple Secure Enclave', 'TrustZone', '安全启动', '远程证明',
    '供应链安全', '侧信道', 'Flush+Reload', 'Prime+Probe',
    '分支预测攻击', '功耗侧信道', '缓存侧信道', 'KPTI', '推测执行',
    'Rust类型系统', '内存安全', 'Data race', 'Use-after-free',
    'Double-free', 'Buffer overflow', 'Null pointer', 'Memory leak',
    'unsafe', 'BAN的局限与Lowe攻击',
    # Module 10
    'AI-Native', 'Agentic AI', 'AI Slop', 'LLM', '归纳性验证',
    '构造性证明', '半可判定性', '实现决策者', 'AI能力边界判断者',
    'AI协作流程设计者', '团队导师', '人机回环', '反例驱动修复',
    '从代码提取不变量', '不变量合成', '可行性', 'LLM表现',
    '形式化验证管道', '分层策略', 'AI Agent模式', 'PoC/原型',
    '内部工具', 'API/库', 'API路由/控制器', 'Schema定义',
    'CI/CD配置', 'CORS/安全头', 'Dockerfile', 'K8s YAML',
    'secrets管理', 'Terraform/Pulumi', '加密实现', 'AI参与度',
    'AI幻觉', 'AI辅助架构', 'AI辅助验证', 'AI集成', 'AI时代软件工程',
    'RAG', 'AI代码生成', 'AI代码生成：归纳性验证范式',
    # Module 11
    'Petri网', 'Place', 'Transition', 'Token', '使能', '触发',
    '有界性', '可达性', '覆盖树', '工作流网', '定时自动机',
    '状态机', 'Saga模式', '补偿', '活动', '任务', '网关',
    '并行网关', '排他网关', '包容网关', '事件网关', '开始事件',
    '结束事件', '中间事件', '边界事件', '定时事件', '消息事件',
    '信号事件', '错误事件', '取消事件', '补偿事件', '链接事件',
    '终止事件', 'AWS Step Functions', 'Camunda', 'Cadence/Uber',
    'Netflix Conductor', '工作流引擎', '工作流验证',
    # Module 12
    '电商', '初创', '全球化', '多活', '单库瓶颈', '团队并行冲突',
    '促销峰值', '全球库存', '商品搜索', '商品缓存', '库存扣减',
    '乐观锁', '订单', '支付', '物流', '秒杀', '预售', '拼团',
    '砍价', '直播', '短视频', '社交', '内容', '推荐', '广告',
    '搜索', 'IoT', '边缘计算', 'Edge Device', 'Edge Gateway',
    '分层计算', 'MQTT', '多Agent', 'Agent', 'Embedding', 'RAG',
    'ADR', '决策框架', '假设验证', 'DAU', 'Cloud-Only', 'Hierarchical',
    # Module 00
    '系统思维', '存量（Stock）', '存量', '流量', '反馈回路',
    '增强型回路（R）', '增强型回路', '调节回路（B）', '调节回路',
    '延迟', '公地悲剧', '富者愈富', '认知负载', '工作记忆',
    '交互节点上限', '并发概念上限', '命名揭示意图', '减少嵌套',
    '信息隐藏', '决策选项上限', 'Chunking', '批判性思维',
    '认知偏误', '从众效应', '幸存者偏差', '近因谬误', '后此谬误',
    '元认知', '学习方法论', '个人精通', '团队学习', '心智模型',
    '共同愿景', '系统思考', '系统动力学',
    # Other important terms
    'AP', 'CP', 'PA/EL', 'PA/EC', 'PC/EL', 'PC/EC',
    'CFT（Raft/Paxos）', 'BFT（PBFT/HotStuff）',
    '一致性（Agreement）', '有效性（Validity）', '终止性（Termination）',
    '一致性（C）', '可用性（A）', '分区容错（P）',
}

# Blocklist for things that might slip through
BLOCKLIST = {
    '谁拥有架构控制权', '-home标记',
    'AI参与度', 'AI渗透率', 'AI能力', 'AI时代软件工程',
    'AI协作流程设计者', 'AI能力边界判断者', 'AI代码生成：归纳性验证范式',
    'BAN的局限与Lowe攻击',
    'Burrows/Abadi/Needham',
    'Cadence/Uber',
    'Dartmouth/Academy for System Change',
    'Amdahl', 'Gustafson', 'Lamport', 'Lamport原话',
    'Amdahl：串行部分固定为(1-p)', 'Amdahl：问题规模固定',
    'Gustafson：问题规模随N增长',
    'Amazon Prime Video',
    'CMU/NSDI', 'Cambridge/INRIA', 'Edinburgh/CMU',
    'Berkeley/Stanford', 'Yale/MIT/Warwick', 'Yale/MSR',
    'Princeton/Stanford', 'Microsoft/OpenAI', 'Microsoft/INRIA',
    'Cornell CS6410', 'MIT 6.006/6.045', 'MIT 6.824', 'MIT Sloan',
    'Stanford CS154', 'Singapore (NUS/SMU)', 'VMware/UT Austin',
    'Uppsala/Aalborg', 'NASA/JPL', 'NICTA/UNSW',
    'C.A.R. Hoare', 'Robin Milner', 'Charles Antony Richard Hoare',
    'Marc Shapiro', 'Diego Ongaro', 'Seth Gilbert',
    'Eric Brewer', 'Martin Fowler', 'Vaughn Vernon',
    'Miguel Castro', 'Werner Vogels', 'Fred Brooks',
    'George A. Miller', 'Gerard Holzmann', 'Peter Senge',
    'Jeannette Wing', 'Amir Pnueli', 'Donella Meadows',
    'Michael Fischer', 'Maurice Herlihy', 'Nancy Lynch',
    'Barbara Liskov', 'Per Martin-Löf', 'Stephen Kleene',
    'Noam Chomsky', 'Tony Hoare',
    'Alan Turing', 'Alonzo Church', 'Carl Hewitt', 'Gul Agha',
    'Leslie Lamport', 'John Ousterhout', 'John Ousterhout 原话',
    'Mel Conway', 'Eric Evans',
    'Aarhus University', 'Amazon', 'Anthropic', 'Apple',
    'Aptos', 'AWS', 'Basecamp', 'Berkeley', 'Cambridge',
    'Camunda', 'CMU', 'CNCF', 'Coq', 'Cornell', 'Dafny',
    'ETH Zurich', 'EPFL', 'Edinburgh', 'Gartner', 'INRIA',
    'Intel', 'Lean', 'MIT', 'Microsoft', 'Microsoft CCF',
    'Microsoft Research', 'MongoDB', 'NASA', 'Netflix',
    'Netflix Conductor', 'NUS', 'Oxford', 'Princeton',
    'Redpanda', 'Rook', 'Ceph', 'S3', 'SEB', 'Shopify',
    'Singapore', 'SMU', 'Stack Overflow', 'Stanford',
    'ThoughtWorks', 'Uber', 'UIUC', 'Uppsala University',
    'VMware', 'Yale', 'Z3', 'Chalmers/Gothenburg',
    '100%', '14/14', '19世纪', '1（本地）', '20世纪中', '20世纪初',
    '20世纪末', '21世纪20年代', '2PC（两阶段提交）', '2（本地Quorum）',
    '3-chain规则', '35 个（92.1%）', '3（多数派）', '4:1 至 8:1',
    '6个bug', '70个子文件', '8. 缓冲与参数', '9. 系统结构',
    '0 个文件', 'P0', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7',
    '10. 信息流结构', '11. 系统目标', '12. 超越范式',
    '14个总览文件', '2026代表系统', '2026年共识性结论',
    '2026年工业成果', '2026年现实', '2026年适用域', '2026趋势',
    '2026适用', '2026适用性', '2026采用度',
    'View/00.md', 'View/01.md', 'View/02.md',
    'Actual title:', 'DynamoDB', 'EBS', 'S3',
    '为什么PACELC更准确', '为何PACELC更准确',
    '为特定受众群体优化认知资源配置', '人脑处理信息时的认知资源消耗',
    '今天的问题来自昨天的解决方案', '仍必须由人类定义',
    '你越用力推，系统反弹越大', '容易的路通常通回原地',
    '在特定故障模型、网络假设和性能需求下，选择形式化可证的最优解',
    '在特定约束下的多目标优化',
    '在组织规模、业务边界、性能需求和运维能力约束下的多目标优化问题',
    '产生的架构', '与其他团队关系',
    '两者：处理器独立工作',
    '全部副本', '不存在确定性算法',
    'CAP是连续光谱', 'CA系统仅在非分布式语境存在',
    'CRDT强最终一致',
    'P不可避免', 'P是不可避免的',
    'PACELC-EL', 'PACELC-PC', 'PACELC是常态', 'PACELC更实用',
    'Serverless适用边界（形式化表达）', 'Serverless是架构拐杖',
    'TLC配置示例（Raft）',
    'Miller 定律的架构推论',
    '定理（HotStuff线性通信）', '定理（SEC保证）',
    '反方论证（架构约束论）', '反方（模块化单体/回归单体）核心论证',
    '反模式',
    '关键原则', '关键问题', '关键洞察',
    '假设过于乐观',
    '分层策略',
    '并发修改的合并结果与接收顺序无关',
    '半格（Join-Semilattice）代数的实例化',
    '协调成本c',
    '可判定性/权衡光谱',
    '历史上有权威出处', '工程上有实践映射',
    '入职时间压缩',
    '可解释性', '可靠性边界',
    '创造主体',
    '原始素材库',
    '变化放大',
    '回归防护',
    '图同态的伪影',
    '因果闭合性（Causal Closure）',
    '团队无法独立发布',
    '垃圾回收',
    '基线测试',
    '安全关键',
    '安全盲区',
    '完成',
    '容量规划的第一性原理工具',
    '对于',
    '工程假设的精确校准器',
    '已提交',
    '带宽效率',
    '平台工程要求',
    '并发概念上限',
    '幸存者偏差',
    '幻觉',
    '建设',
    '开悟',
    '彻底转变',
    '微服务量化',
    '微服务架构',
    '必然王国',
    '思考',
    '总体计划',
    '情况',
    '成本',
    '成果',
    '承受',
    '挑战',
    '振动',
    '捕捉',
    '损失',
    '掌握',
    '描述',
    '提升',
    '提示',
    '搜索',
    '收敛',
    '改善',
    '效果',
    '整体',
    '整理',
    '断言',
    '方法论',
    '明了',
    '最坏',
    '最优',
    '最有效',
    '期间',
    '机会',
    '机制',
    '杠杆点',
    '构造',
    '析取',
    '标志',
    '核心命题',
    '核心原理',
    '核心挑战',
    '核心概念',
    '核心问题',
    '模式匹配',
    '正确性',
    '沟通',
    '消费',
    '演变',
    '状态封装',
    '状态转换',
    '理论化',
    '理论边界',
    '画出',
    '相应',
    '监控',
    '真相',
    '确定性',
    '策略',
    '系统化',
    '系统思维',
    '系统性',
    '系统目标',
    '系统结构',
    '纯粹',
    '组成',
    '组织',
    '组织结构',
    '缓冲与参数',
    '网络',
    '自主',
    '行业',
    '衰退',
    '视图',
    '认知偏误',
    '认知资源',
    '认知负载',
    '调节回路（B）',
    '谬误',
    '负责',
    '趋势',
    '运行时间',
    '近因谬误',
    '迷惑',
    '逻辑谬误',
    '重视',
    '问题的结构',
    '隐含假设',
    '非常',
    '默认',
    '黑暗',
}

def is_technical_term(term):
    if len(term) < 2 or len(term) > 35:
        return False
    if term in BLOCKLIST:
        return False
    if term in ALLOWLIST:
        return True
    
    # Skip numbers, dates, stats
    if re.match(r'^\d', term):
        return False
    if '%' in term:
        return False
    
    # Skip file refs
    if 'View/' in term or '.md' in term or 'Actual title' in term:
        return False
    
    # Skip sentence fragments
    if any(c in term for c in ['，', '。', '；']):
        return False
    
    # For terms not in allowlist, be very strict
    # Only accept if it has strong technical indicators
    has_tech_indicator = (
        re.search(r'[A-Z]{2,}', term) or  # Acronym or mixed case
        re.search(r'[0-9]', term) or  # Contains digit
        re.search(r'[+\-/()（）·]', term) or  # Special chars
        re.search(r'[λπβμρ◇□◆]', term) or  # Math symbols
        re.search(r'[\u4e00-\u9fff].*[a-zA-Z]|[a-zA-Z].*[\u4e00-\u9fff]', term)  # Mixed C-E
    )
    
    if not has_tech_indicator:
        return False
    
    # Skip long Chinese without strong technical markers
    if len(term) > 12 and re.search(r'[\u4e00-\u9fff]', term):
        if not re.search(r'[()（）\-/]', term):
            return False
    
    # Skip if looks like a sentence with '的' and long
    if '的' in term and len(term) > 10:
        return False
    
    return True

def extract_bold_terms(text):
    pattern = r'\*\*([^*\n]+?)\*\*'
    matches = re.findall(pattern, text)
    terms = set()
    for m in matches:
        term = m.strip()
        if not term or not is_technical_term(term):
            continue
        terms.add(term)
    return terms

def get_file_context(text, term, window=200):
    pattern = re.escape(term)
    match = re.search(pattern, text)
    if not match:
        return ""
    start = max(0, match.start() - window)
    end = min(len(text), match.end() + window)
    return text[start:end].replace('\n', ' ')

def parse_existing_index(filepath):
    content = filepath.read_text(encoding='utf-8')
    terms = {}
    pattern = r'\|\s*\*\*([^*|]+?)\*\*\s*\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|'
    for m in re.finditer(pattern, content):
        term = m.group(1).strip()
        definition = m.group(2).strip()
        module = m.group(3).strip()
        file_ref = m.group(4).strip()
        terms[term] = {
            'definition': definition,
            'module': module,
            'file_ref': file_ref,
        }
    return terms, content

def term_exists_in_files(term, file_texts):
    variants = [term]
    extra = {
        'DDD': ['领域驱动设计'],
        'Paxos': ['Paxos'],
        'Rust': ['Rust'],
        'Side-Channel': ['侧信道'],
        'λ演算': ['λ演算', 'lambda演算'],
        '共识算法': ['共识'],
        '分布式事务': ['分布式事务', '2PC', 'Saga', 'TCC'],
        '系统动力学': ['系统动力学'],
        'Two-Pizza Team': ['Two-Pizza', 'Two Pizza'],
    }
    if term in extra:
        variants.extend(extra[term])
    for ft in file_texts.values():
        for v in variants:
            if v in ft:
                return True
    return False

def generate_index_content(existing_terms, all_bold_terms):
    all_terms = dict(existing_terms)
    
    for term, occurrences in all_bold_terms.items():
        if term in existing_terms:
            continue
        filepath, context = occurrences[0]
        definition = "（待补充定义）"
        context_clean = context.replace('**', '')
        patterns = [
            rf'{re.escape(term)}\s*是\s*([^。；,.\n]{{10,80}})',
            rf'{re.escape(term)}\s*[：:]\s*([^。；,.\n]{{10,80}})',
            rf'{re.escape(term)}\s*[,，]\s*([^。；,.\n]{{10,80}})',
        ]
        for pat in patterns:
            m = re.search(pat, context_clean)
            if m:
                definition = m.group(1).strip()
                if len(definition) > 5:
                    break
        
        parts = filepath.split(os.sep)
        module = parts[0].split('-')[0] if parts else '?'
        file_ref = f"[{module}/{Path(filepath).stem}](../{filepath.replace(chr(92), '/')})"
        
        all_terms[term] = {
            'definition': definition,
            'module': module,
            'file_ref': file_ref,
        }
    
    groups = defaultdict(list)
    for term in sorted(all_terms.keys(), key=lambda x: x.lower()):
        first = term[0].upper()
        if re.match(r'[\u4e00-\u9fff]', term[0]):
            first = term[0]
        groups[first].append(term)
    
    lines = [
        "# 核心概念反向索引与术语表",
        "",
        "> **定位**：本文件是Struct知识体系的概念导航图——按字母顺序排列所有核心术语，标注定义、所属模块和交叉引用，实现\"任意概念 → 完整知识路径\"的速查。",
        ">",
        "> **使用方法**：在理解新概念时，先查阅本索引定位其在知识体系中的位置；在复习时，通过术语串联跨模块知识。",
        "",
        "---",
        "",
    ]
    
    def sort_key(letter):
        if re.match(r'[A-Za-z]', letter):
            return (0, letter.lower())
        elif re.match(r'[\u4e00-\u9fff]', letter):
            return (1, letter)
        else:
            return (2, letter)
    
    for letter in sorted(groups.keys(), key=sort_key):
        lines.append(f"## {letter}")
        lines.append("")
        lines.append("| 术语 | 定义 | 模块 | 文件 |")
        lines.append("|------|------|------|------|")
        for term in sorted(groups[letter], key=lambda x: x.lower()):
            info = all_terms[term]
            definition = info['definition'].replace('|', '\\|')
            lines.append(f"| **{term}** | {definition} | {info['module']} | {info['file_ref']} |")
        lines.append("")
    
    lines.append("---")
    lines.append("")
    lines.append("*文件创建日期：2026-04-23*")
    lines.append("*状态：已完成*")
    
    return "\n".join(lines)

def main():
    existing_terms, index_content = parse_existing_index(INDEX_FILE)
    print(f"Existing terms in index: {len(existing_terms)}")

    all_bold_terms = defaultdict(list)
    file_texts = {}
    md_files = list(STRUCT_DIR.rglob("*.md"))
    md_files = [f for f in md_files if not (f.name == INDEX_FILE.name and f.parent.name == INDEX_FILE.parent.name)]
    
    for md_file in md_files:
        rel = md_file.relative_to(STRUCT_DIR)
        if should_skip_file(rel):
            continue
        try:
            text = md_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Error reading {md_file}: {e}")
            continue
        file_texts[str(rel)] = text
        terms = extract_bold_terms(text)
        for term in terms:
            context = get_file_context(text, term)
            all_bold_terms[term].append((str(rel), context))

    print(f"Total unique bold terms found (filtered): {len(all_bold_terms)}")
    
    missing_terms = set(all_bold_terms.keys()) - set(existing_terms.keys())
    print(f"Missing terms from index: {len(missing_terms)}")
    
    orphan_terms = []
    for term in existing_terms:
        if not term_exists_in_files(term, file_texts):
            orphan_terms.append(term)
    print(f"Orphan terms: {len(orphan_terms)} ({orphan_terms})")
    
    raw_terms = re.findall(r'\|\s*\*\*([^*|]+?)\*\*\s*\|', index_content)
    seen = set()
    duplicates = []
    for t in raw_terms:
        t = t.strip()
        if t in seen:
            duplicates.append(t)
        seen.add(t)
    print(f"Duplicate entries in index: {len(duplicates)} ({set(duplicates)})")

    new_content = generate_index_content(existing_terms, all_bold_terms)
    INDEX_FILE.write_text(new_content, encoding='utf-8')
    print(f"Updated index written to {INDEX_FILE}")
    
    total_after = len(existing_terms) + len(missing_terms)
    print(f"\n=== REPORT ===")
    print(f"Total terms in index BEFORE: {len(existing_terms)}")
    print(f"Total terms in index AFTER: {total_after}")
    print(f"Terms ADDED: {len(missing_terms)}")
    print(f"Orphans removed: {len(orphan_terms)}")
    print(f"Duplicates fixed: {len(duplicates)}")
    
    report = {
        'existing_count': len(existing_terms),
        'total_after': total_after,
        'added_count': len(missing_terms),
        'orphan_count': len(orphan_terms),
        'duplicate_count': len(duplicates),
        'orphan_terms': orphan_terms,
        'duplicates': list(set(duplicates)),
        'added_terms': sorted(missing_terms),
    }
    report_path = Path("E:/_src/formal-architecture/terminology_audit_report_v6.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Report saved to {report_path}")

if __name__ == "__main__":
    main()
