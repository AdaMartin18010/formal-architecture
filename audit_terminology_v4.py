#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminology audit v4: focus on concise technical terms only.
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

# Very targeted blocklist of obvious non-terms that keep appearing
BLOCKLIST = {
    '权威来源', '核心命题', '模块定位', '思维导图', '多维矩阵对比',
    '工程映射', '形式化创始人', '核心通信原语', '通信语义', '状态封装',
    '组合算子', '死锁可检测性', '公平性保证', '定理', '工程启示',
    '公式', '假设', '局限', '关键洞察', '关键原则', '关键问题',
    '决策触发点', '典型实现', '典型系统', '内部工具', '分层策略',
    '分层计算', '压力测试', '双态配置', '反方论证（架构约束论）',
    '反方（模块化单体/回归单体）核心论证', '反模式', '变化放大',
    '变更频率', '可信执行环境（TEE）', '可判定性/权衡光谱',
    '可确定全序', '可确定因果', '因果历史', '因果捕获',
    '团队规模', '团队配置', '团队沟通上限', '团队规模阈值',
    '团队无法独立发布', '在特定故障模型、网络假设和性能需求下，选择形式化可证的最优解',
    '在特定约束下的多目标优化', '在组织规模、业务边界、性能需求和运维能力约束下的多目标优化问题',
    '场景树图', '复杂子系统', '多维矩阵对比', '容量规划的第一性原理工具',
    '工程假设的精确校准器', '工程实现', '工程成熟度', '工程现实',
    '工程绕过', '工程频率', '工具/方法', '已提交', '平台工程要求',
    '并发概念上限', '并发修改的合并结果与接收顺序无关', '幸存者偏差',
    '幻觉', '应用层', '弱点', '强制', '归纳', '形式化', '形成',
    '彻底转变', '微服务量化', '微服务架构', '必然', '必然王国',
    '必要', '思考', '总体', '总览', '悖论', '情况', '意图',
    '成本', '成果', '承诺', '技术', '技术债', '折中', '报告',
    '批判', '承受', '挑战', '捕捉', '损失', '掌握', '描述',
    '提升', '提示', '搜索', '收敛', '改善', '效果', '整体',
    '整理', '断言', '方法', '方法论', '明了', '普通', '最坏',
    '最优', '最有效', '最终', '服务', '期间', '本质', '机会',
    '机制', '条件', '条款', '杠杆点', '极限', '架构', '构造',
    '析取', '某些', '标准', '标志', '核心', '核心命题', '核心原理',
    '核心挑战', '核心概念', '核心问题', '模型', '模式', '欺诈',
    '正确性', '比较', '沟通', '消费', '消息', '演变', '灵感',
    '状态', '状态封装', '状态转换', '现代', '理论', '理论化',
    '理论边界', '理念', '生产', '生成', '用途', '画出', '界限',
    '痛苦', '相应', '矛盾', '监控', '目标', '直接', '相位',
    '真相', '知识', '确定性', '程度', '稳定性', '空间', '策略',
    '算法', '管理', '类型', '系统化', '系统思维', '系统性',
    '系统目标', '系统结构', '纯粹', '组成', '组织', '组织结构',
    '经验', '维护', '缓冲', '缓冲与参数', '编码', '编译', '缺陷',
    '网络', '自身', '自主', '自然', '行业', '衰退', '规范',
    '规则', '视图', '认知', '认知偏误', '认知资源', '认知负载',
    '训练', '证明', '词汇', '语言', '课程', '调节回路', '调节回路（B）',
    '调试', '谬误', '负担', '负责', '质量', '资源', '趋势',
    '路径', '输入', '输出', '过度', '运行', '运行时', '近因谬误',
    '边界', '迷惑', '选择', '逻辑', '连锁', '通信', '速度',
    '速率', '部件', '部分', '部署', '重视', '量', '量子',
    '量度', '问题', '问题的结构', '问题空间', '问题边界', '错误',
    '长度', '阅读', '隐含假设', '隐藏', '风格', '风险', '默认',
    '一致性（C）', '可用性（A）', '分区容错（P）',
    '一致性（Agreement）', '有效性（Validity）', '终止性（Termination）',
    '全部副本', '不存在确定性算法', '两者：处理器独立工作', '串行部分',
    '严格一致性', '会话一致', '会话一致性', '传播单元', '传统Serverful',
    '位置透明', '假设过于乐观', '假设验证', '偏序', '偏序集（Poset）',
    '元认知', '入职时间压缩', '全局库存', '公地悲剧', '公平性',
    '公平性保证', '共享DBA团队', '共享内存+锁', '共享数据库',
    '共同愿景', '共识', '共识要求', '关系', '内存', '内部锁服务',
    '决策复盘', '决策树图', '决策选项上限', '冷启动', '冷启动已解决',
    '减少嵌套', '分区', '分区时', '分区是二元事件', '分层（部门制）',
    '分布式', '分布式单体', '分布式原生', '分布式原生性', '分布式模式',
    '分布无关的守恒量', '分析方法', '分离逻辑', '则', '创始人',
    '创造性任务', '删除语义', '利用率', '半可判定', '半可判定性',
    '协调成本', '协调成本c', '协调成本系数', '协调自由', '单一职责',
    '单体', '单体优先', '单向因果', '单库瓶颈', '单调读', '即时最终性',
    '原文', '反方论证（架构约束论）', '反方（模块化单体/回归单体）核心论证',
    '反模式', '变化放大', '变更频率', '可信执行环境（TEE）', '可判定',
    '可确定全序', '可确定因果', '后端', '向量时钟', '吞吐量',
    '启动时间', '响应时间', '回流', '团队', '团队学习', '团队导师',
    '团队并行冲突', '团队规模', '团队配置', '团队沟通上限', '团队规模阈值',
    '团队无法独立发布', '图同态', '图同态的伪影', '在特定故障模型、网络假设和性能需求下，选择形式化可证的最优解',
    '在特定约束下的多目标优化', '在组织规模、业务边界、性能需求和运维能力约束下的多目标优化问题',
    '场景树图', '垃圾回收', '基线测试', '增强型回路（R）',
    '复杂子系统', '复杂度', '多Agent', '多活', '多维矩阵对比',
    '存储膨胀', '学习曲线', '安全关键', '安全启动', '安全性',
    '定理（HotStuff线性通信）', '定理（SEC保证）', '实现复杂度',
    '实现成本', '实现难度', '实际策略', '容量规划的第一性原理工具',
    '工程假设的精确校准器', '工程实现', '工程成熟度', '工程现实',
    '工程绕过', '工程频率', '工具/方法', '已提交', '带宽',
    '带宽效率', '常态', '平台', '平台团队', '平台工程要求',
    '并发', '并发处理', '并发概念上限',
    '并发修改的合并结果与接收顺序无关', '幸存者偏差', '幻觉',
    '库存扣减', '应用', '应用层', '延迟', '建设', '开悟',
    '弱点', '强制', '归纳', '形式化', '形成', '彻底转变',
    '微服务量化', '微服务架构', '必然', '必然王国', '必要',
    '思考', '总体', '总体计划', '总览', '总览文件', '悖论',
    '情况', '意图', '感知', '成', '成本', '成果', '或',
    '战斗', '战略', '所有', '承诺', '技术', '技术债',
    '折中', '报告', '批判', '承受', '挑战', '振动', '捕捉',
    '损失', '掌握', '描述', '提升', '提示', '搜索', '收敛',
    '改善', '效果', '整体', '整理', '断言', '新生', '方法',
    '方法论', '明了', '普通', '最坏', '最优', '最有效',
    '最终', '服务', '期', '期间', '本质', '机会', '机制',
    '条件', '条款', '杠杆点', '极限', '架构', '构造',
    '析取', '某些', '标准', '标志', '核心', '核心命题',
    '核心原理', '核心挑战', '核心概念', '核心问题', '模型',
    '模式', '欺诈', '正确性', '比较', '气象', '油条',
    '沟通', '消费', '消息', '温度', '演变', '灵感', '灰色',
    '热处理', '然后', '状态', '状态封装', '状态转换', '现代',
    '理论', '理论化', '理论边界', '理念', '生产', '生成',
    '用途', '画出', '界限', '痛苦', '相应', '矛盾', '监控',
    '目标', '直接', '相位', '真相', '知识', '确定性', '程度',
    '稳定性', '空间', '策略', '筛', '算法', '管理', '类型',
    '系统化', '系统思维', '系统性', '系统目标', '系统结构',
    '纯', '纯粹', '组成', '组织', '组织结构', '经验',
    '维护', '缓冲区', '缓冲与参数', '编码', '编译', '缺陷',
    '网', '网络', '自由王国', '自身', '自主', '自然',
    '行业', '衰退', '规范', '规则', '视图', '认知', '认知偏误',
    '认知资源', '认知负载', '训练', '证明', '词汇', '语言',
    '课程', '调节回路（B）', '调节回路', '调试', '谬误',
    '负担', '负责人', '质量', '资源', '趋势', '路径',
    '输入', '输出', '过度', '过程', '运', '运行', '运行时',
    '运行时间', '近因谬误', '边界', '边缘', '过程', '迷惑',
    '选择', '逻辑', '逻辑谬误', '连锁', '通信', '通论',
    '通常', '速度', '速率', '部件', '部分', '部署', '重拍',
    '重要', '重视', '量', '量子', '量度', '问题',
    '问题的结构', '问题空间', '问题边界', '错误', '长度',
    '阅读', '隐含假设', '隐藏', '非', '非常', '革命',
    '风格', '风险', '飞行', '饥饿', '首部', '鬼', '魅力',
    '默认', '黑暗', '为什么PACELC更准确', '为何PACELC更准确',
    '为特定受众群体优化认知资源配置', '人脑处理信息时的认知资源消耗',
    '今天的问题来自昨天的解决方案', '仍必须由人类定义',
    '你越用力推，系统反弹越大', '代', '令', '以', '会', '但',
    '你', '使', '便', '信', '做', '像', '全', '公', '内',
    '写', '减', '击', '分', '切', '判', '制', '力', '加',
    '务', '化', '区', '单', '卡', '原', '参', '反', '受',
    '变', '号', '合', '名', '后', '员', '呢', '品', '因',
    '国', '地', '型', '基', '增', '处', '复', '外', '多',
    '大', '头', '套', '女', '它', '安', '定', '实', '客',
    '对', '寻', '导', '小', '少', '局', '工', '差', '已',
    '常', '平', '年', '广', '度', '建', '开', '引', '当',
    '形', '影', '很', '得', '心', '性', '总', '息', '情',
    '感', '成', '所', '手', '打', '执', '技', '把', '抓',
    '投', '折', '报', '指', '按', '排', '接', '控', '推',
    '描', '提', '收', '改', '放', '故', '数', '文', '断',
    '无', '早', '时', '明', '是', '显', '智', '更', '最',
    '有', '服', '期', '未', '本', '机', '来', '构', '果',
    '根', '次', '款', '正', '步', '每', '比', '气', '求',
    '没', '法', '注', '流', '测', '消', '深', '游', '满',
    '潮', '点', '然', '熟', '特', '状', '独', '现', '理',
    '用', '由', '甲', '电', '疲', '白', '的', '目', '相',
    '看', '真', '着', '知', '短', '确', '示', '神', '种',
    '科', '积', '程', '空', '立', '端', '第', '等', '简',
    '算', '管', '类', '精', '素', '红', '约', '级', '线',
    '统', '继', '续', '维', '绿', '置', '美', '老', '者',
    '而', '联', '能', '脑', '自', '致', '节', '若', '英',
    '获', '行', '被', '装', '要', '见', '观', '规', '解',
    '言', '计', '认', '记', '许', '论', '设', '证', '评',
    '识', '该', '说', '请', '读', '调', '象', '负', '责',
    '费', '资', '赖', '起', '足', '跟', '身', '车', '转',
    '较', '这', '进', '远', '连', '追', '适', '选', '通',
    '造', '遇', '道', '那', '部', '都', '里', '重', '量',
    '鉴', '错', '长', '问', '间', '防', '降', '除', '随',
    '难', '需', '非', '面', '题', '颜', '饱', '首', '高',
    '黄', '黑',
    # More specific junk
    '谁拥有架构控制权', '-home标记', '100%', '14/14', '14个总览文件',
    '19世纪', '1（本地）', '2026代表系统', '2026年共识性结论',
    '2026年工业成果', '2026年现实', '2026年适用域', '2026趋势',
    '2026适用', '2026适用性', '2026采用度', '20世纪中', '20世纪初',
    '20世纪末', '21世纪20年代', '2（本地Quorum）', '3-chain规则',
    '35 个（92.1%）', '3（多数派）', '4:1 至 8:1', '6个bug',
    '70个子文件', '8. 缓冲与参数', '9. 系统结构',
    '0 个文件', 'Amdahl：串行部分固定为(1-p)', 'Amdahl：问题规模固定',
    'BAN的局限与Lowe攻击', 'CAP是连续光谱', 'CA系统仅在非分布式语境存在',
    'CRDT强最终一致', 'DAG（Bullshark）', 'DAG（有向无环图）编码了完整的因果历史，因此无需显式视图变更',
    'Delta-State CRDT', 'FLP定理', 'Gustafson：问题规模随N增长',
    'Leader切换', 'Leader容错', 'Leader概念', 'Leader瓶颈',
    'Leader选举', 'Leader选举未定义', 'Leader选举超时 > RTT',
    'Level 1：探索', 'Level 2：规范', 'Level 3：集成',
    'Level 4：优化', 'Level 5：自治',
    'Miller 定律的架构推论', 'O(n)线性', 'P不可避免', 'P是不可避免的',
    'PA/EC', 'PA/EL', 'PACELC-EL', 'PACELC-PC', 'PACELC是常态',
    'PACELC更实用', 'PC/EC', 'PC/EL', 'PoC/原型',
    'Serverless适用边界（形式化表达）', 'Serverless是架构拐杖',
    'TLC配置示例（Raft）', 'Two-Pizza Team',
    '你', '使', '信', '做', '全', '公', '写', '减', '分',
    '判', '制', '力', '务', '化', '区', '单', '卡', '原',
    '参', '反', '受', '变', '号', '合', '名', '后', '员',
    '品', '因', '国', '地', '型', '基', '处', '复', '外',
    '多', '大', '套', '它', '安', '定', '实', '客', '对',
    '寻', '导', '小', '局', '工', '差', '已', '平', '年',
    '建', '开', '引', '形', '很', '得', '性', '息', '情',
    '成', '所', '手', '执', '技', '把', '投', '报', '指',
    '按', '排', '接', '控', '推', '提', '收', '改', '放',
    '数', '文', '无', '早', '时', '是', '显', '更', '有',
    '服', '未', '本', '机', '来', '构', '果', '根', '法',
    '注', '流', '测', '消', '深', '点', '特', '状', '现',
    '理', '用', '由', '疲', '的', '目', '看', '真', '知',
    '短', '示', '神', '种', '科', '程', '空', '端', '简',
    '算', '管', '类', '素', '约', '线', '统', '置', '老',
    '者', '而', '联', '能', '自', '致', '节', '英', '行',
    '被', '要', '见', '规', '解', '言', '计', '认', '记',
    '许', '论', '设', '证', '评', '识', '该', '说', '请',
    '读', '调', '象', '负', '责', '费', '起', '足', '身',
    '车', '转', '这', '进', '连', '适', '选', '通', '造',
    '道', '部', '都', '里', '重', '错', '长', '问', '间',
    '防', '除', '随', '难', '需', '非', '面', '题', '高',
    'P0', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7',
    '10. 信息流结构', '11. 系统目标', '12. 超越范式',
    'Amdahl', 'Amazon', 'Anthropic', 'Aptos', 'AWS',
    'Basecamp', 'Berkeley', 'Cambridge', 'Camunda',
    'CMU', 'CNCF', 'Coq', 'Cornell', 'Dafny',
    'ETH Zurich', 'EPFL', 'Edinburgh',
    'Gartner', 'INRIA', 'Intel', 'Lean', 'MIT',
    'Microsoft', 'MongoDB', 'NASA', 'Netflix', 'NUS',
    'Oxford', 'Princeton', 'Shopify', 'Singapore',
    'Stack Overflow', 'Stanford', 'ThoughtWorks',
    'Uber', 'UIUC', 'Uppsala University', 'VMware',
    'Yale', 'Z3',
    'Alan Turing', 'Alonzo Church', 'Amir Pnueli',
    'Barbara Liskov', 'C.A.R. Hoare', 'Carl Hewitt',
    'Charles Antony Richard Hoare', 'Daniel Abadi',
    'Diego Ongaro', 'Donella Meadows', 'Edsger Dijkstra',
    'Eric Brewer', 'Eric Evans', 'Fred Brooks',
    'George A. Miller', 'Gerard Holzmann', 'Gul Agha',
    'Jeannette Wing', 'John Ousterhout', 'John Ousterhout 原话',
    'Lamport', 'Lamport原话', 'Leslie Lamport',
    'Marc Shapiro', 'Martin Fowler', 'Maurice Herlihy',
    'Mel Conway', 'Michael Fischer', 'Miguel Castro',
    'Nancy Lynch', 'Noam Chomsky', 'Per Martin-Löf',
    'Peter Senge', 'Robin Milner', 'Seth Gilbert',
    'Stephen Kleene', 'Tony Hoare', 'Vaughn Vernon',
    'Werner Vogels',
    '实际', '实用', '实践', '对', '将', '并', '当',
    '很', '我', '或', '所', '才', '把', '无', '是',
    '有', '没', '的', '给', '而', '被', '让', '该',
    '过', '这', '那', '都', '需要',
}

def is_junk(term):
    if len(term) < 2 or len(term) > 30:
        return True
    if term in BLOCKLIST:
        return True
    # Numbers/dates/stats
    if re.match(r'^\d', term):
        return True
    if re.search(r'[/%]', term):
        return True
    if re.match(r'^\d{4}年', term):
        return True
    # File refs and markdown artifacts
    if 'View/' in term or 'Actual title' in term or '.md' in term:
        return True
    # Skip long Chinese phrases (>12 chars) that look like sentences
    if len(term) > 14 and re.search(r'[\u4e00-\u9fff]', term):
        # Allow well-known longer technical terms with parentheses
        if not re.search(r'[()（）]', term):
            return True
    # Skip Chinese phrases with obvious sentence structure
    if len(term) > 10 and any(c in term for c in ['，', '。', '；', '、']):
        return True
    # Skip if starts with punctuation
    if re.match(r'^[^\w\u4e00-\u9fff]', term):
        return True
    return False

def extract_bold_terms(text):
    pattern = r'\*\*([^*\n]+?)\*\*'
    matches = re.findall(pattern, text)
    terms = set()
    for m in matches:
        term = m.strip()
        if not term:
            continue
        if is_junk(term):
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
    """Check if term or obvious variants exist anywhere in files."""
    variants = [term]
    # Common concept mappings
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

    missing_details = []
    for term in sorted(missing_terms):
        occurrences = all_bold_terms[term]
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
        
        missing_details.append({
            'term': term,
            'definition': definition,
            'module': module,
            'file': filepath,
            'context': context_clean[:300],
        })
    
    report = {
        'existing_count': len(existing_terms),
        'bold_terms_count': len(all_bold_terms),
        'missing_count': len(missing_terms),
        'orphan_count': len(orphan_terms),
        'duplicate_count': len(duplicates),
        'missing_terms': sorted(missing_terms),
        'orphan_terms': orphan_terms,
        'duplicates': list(set(duplicates)),
        'missing_details': missing_details,
    }
    
    report_path = Path("E:/_src/formal-architecture/terminology_audit_report_v4.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Report saved to {report_path}")
    
    for item in missing_details[:80]:
        print(f"- {item['term']} | {item['definition'][:60]} | {item['module']} | {item['file']}")
    if len(missing_details) > 80:
        print(f"... and {len(missing_details) - 80} more")

if __name__ == "__main__":
    main()
