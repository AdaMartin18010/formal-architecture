#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Refined terminology audit: better filtering for actual technical terms.
"""

import os
import re
import json
from collections import defaultdict
from pathlib import Path

STRUCT_DIR = Path("E:/_src/formal-architecture/Struct")
INDEX_FILE = STRUCT_DIR / "99-参考文献与索引/02-核心概念反向索引与术语表.md"

# Blocklist: common non-technical bold text patterns
BLOCKLIST = {
    '术语', '定义', '模块', '文件', '定位', '使用方法', '核心概念反向索引与术语表',
    '权威来源', '核心命题', '模块定位', '思维导图', '多维矩阵对比', '工程映射',
    '形式化创始人', '核心通信原语', '通信语义', '状态封装', '组合算子', '死锁可检测性',
    '公平性保证', '定理', '工程启示', '公式', '假设', '局限', '关键洞察',
    '否则', '则', '代表', '工具', '名称', '创始人', '产生的架构', '与其他团队关系',
    '关键原则', '关键问题', '决策触发点', '典型实现', '典型系统', '内部工具',
    '分层策略', '分层计算', '压力测试', '双态配置', '反例', '反例输出', '反例可读性',
    '反例轨迹', '反例解释', '反例驱动修复', '可扩展性', '可理解性', '可行性',
    '可观测性', '可读性', '可靠性', '可用性', '可见性', '后此谬误', '复杂度',
    '命名揭示意图', '响应', '因果一致', '因果一致性', '因果关系', '团队', '团队学习',
    '团队导师', '团队并行冲突', '团队规模', '团队配置', '团队沟通上限', '团队规模阈值',
    '团队无法独立发布', '基础设施成本', '处理位置', '处理方式', '外部一致性',
    '外部冲击打破结构', '失效条件', '存储需求', '存储膨胀', '存量', '存量（Stock）',
    '学习曲线', '守恒定律', '安全', '安全属性', '安全盲区', '安全边际',
    '定义', '定位', '定律', '定理猜测+自动验证', '实现决策者', '实现复杂度',
    '实现成本', '实现难度', '实际策略', '审视微服务', '审计能力', '容易的路通常通回原地',
    '容量规划的第一性原理工具', '工程假设的精确校准器', '工程上有实践映射',
    '工程实现', '工程成熟度', '工程现实', '工程绕过', '工程频率', '工程映射',
    '差异化', '带宽', '带宽效率', '常态', '平台', '平台团队', '平台工程要求',
    '并发', '并发处理', '并发概念上限', '并发修改的合并结果与接收顺序无关',
    '幸存者偏差', '幻觉', '库存扣减', '应用', '应用层', '应用场景',
    '延迟', '建设', '开悟', '弱点', '强制', '归纳', '形式化', '形成',
    '彻底转变', '微服务量化', '微服务架构', '必然', '必然王国', '必要', '思考',
    '总体', '总体计划', '总览', '总览文件', '悖论', '情况', '意图',
    '感', '感知', '成', '成本', '成果', '我', '或', '战', '战斗', '战略',
    '所有', '承诺', '技术', '技术债', '技術', '折中', '报告', '批判', '承受',
    '折磨', '挑战', '振动', '捕捉', '损失', '掌握', '描述', '提升', '提示',
    '搜索', '收敛', '改善', '效果', '整体', '整理', '断言', '新生',
    '方法', '方法论', '日程', '明了', '是', '普通', '最坏', '最优',
    '最有效', '最终', '服务', '期', '期间', '本质', '机会', '机制', '条件',
    '条款', '杠杆点', '极限', '架构', '构造', '构造方法', '构造证明',
    '析取', '某些', '标准', '标志', '核心', '核心命题', '核心原理',
    '核心挑战', '核心概念', '核心通信原语', '核心问题', '模型', '模式',
    '模式匹配', '欺诈', '正确性', '比较', '气象', '油条', '沟通', '消费',
    '消息', '温度', '演变', '灵感', '灰色', '热处理', '然后', '状态',
    '状态封装', '状态转换', '现代', '理论', '理论化', '理论边界', '理念',
    '生产', '生成', '用途', '画出', '界限', '痛苦', '的', '目的',
    '相应', '矛盾', '监控', '目标', '直接', '相位', '真相', '知识',
    '确定性', '程度', '稳定性', '空间', '策略', '筛', '算法', '管理',
    '类型', '系统化', '系统动力学', '系统思维', '系统性', '系统目标',
    '系统结构', '纯', '纯粹', '组成', '组织', '组织结构', '经验',
    '经验性', '维护', '缓冲区', '缓冲与参数', '编码', '编译', '缺陷',
    '网', '网络', '自由王国', '自身', '自主', '自然', '行业', '表明',
    '衰退', '规范', '规则', '视图', '认知', '认知偏误', '认知资源',
    '认知负载', '训练', '证明', '词汇', '语言', '课程', '调节回路（B）',
    '调节回路', '调试', '谬误', '负担', '负责人', '质量', '资源', '趋势',
    '路径', '输入', '输出', '过度', '过程', '运', '运行', '运行时',
    '运行时间', '近因谬误', '边界', '边缘', '过程', '迷惑', '选择',
    '逻辑', '逻辑谬误', '连锁', '通信', '通论', '通常', '速度', '速率',
    '部件', '部分', '部署', '重拍', '重要', '重视', '量', '量子',
    '量度', '问题', '问题的结构', '问题空间', '问题边界', '错误',
    '长度', '阅读', '隐含假设', '隐藏', '非', '非常', '革命',
    '风格', '风险', '飞行', '饥饿', '首部', '鬼', '魅力', '默认',
    '黑暗', '（B）', '（C）', '（P）', '（R）', '（Stock）', '（T）',
    '（A）', '（B', '（B）', '（C', '（E）', '（L）', '（N）',
    '一致性（C）', '可用性（A）', '分区容错（P）',
    '一致性（Agreement）', '有效性（Validity）', '终止性（Termination）',
    '全部副本', '不存在确定性算法', '两者：处理器独立工作', '串行部分',
    '严格一致性', '会话一致', '会话一致性', '传播单元', '传统Serverful',
    '位置透明', '你相信什么', '假设过于乐观', '假设验证', '偏序', '偏序集（Poset）',
    '元认知', '入职时间压缩', '全局库存', '公地悲剧', '公平性', '公平性保证',
    '共享DBA团队', '共享内存+锁', '共享数据库', '共同愿景', '共识', '共识要求',
    '关系', '典型系统', '内存', '内部锁服务', '决策复盘', '决策树图',
    '决策选项上限', '冷启动', '冷启动已解决', '减少嵌套', '分区', '分区时',
    '分区是二元事件', '分层（部门制）', '分布式', '分布式单体', '分布式原生',
    '分布式原生性', '分布式模式', '分布无关的守恒量', '分析方法',
    '分离逻辑', '则', '创始人', '创造性任务', '删除语义', '利用率',
    '半可判定', '半可判定性', '半格（Join-Semilattice）代数的实例化',
    '协调成本', '协调成本c', '协调成本系数', '协调自由', '单一职责',
    '单体', '单体优先', '单向因果', '单库瓶颈', '单调读', '即时最终性',
    '原文', '反方论证（架构约束论）', '反方（模块化单体/回归单体）核心论证',
    '反模式', '变化放大', '变更频率', '可信执行环境（TEE）', '可判定',
    '可判定性/权衡光谱', '可确定全序', '可确定因果', '后', '后端',
    '向量时钟', '吞吐量', '启动时间', '响应时间', '回流', '因果历史',
    '因果捕获', '团队规模', '图同态', '图同态的伪影', '在特定故障模型、网络假设和性能需求下，选择形式化可证的最优解',
    '在特定约束下的多目标优化', '在组织规模、业务边界、性能需求和运维能力约束下的多目标优化问题',
    '场景树图', '垃圾回收', '基线测试', '增强型回路（R）',
    '复杂子系统', '复杂度', '多Agent', '多活', '多维矩阵对比',
    '存储膨胀', '学习曲线', '安全关键', '安全启动', '安全性',
    '定理（HotStuff线性通信）', '定理（SEC保证）', '实现复杂度',
    '实现成本', '实现难度', '实际策略', '容易的路通常通回原地',
    '容量规划的第一性原理工具', '工程假设的精确校准器', '工程实现',
    '工程成熟度', '工程现实', '工程绕过', '工程频率', '工具/方法',
    '已提交', '带宽', '带宽效率', '常态', '平台', '平台团队',
    '平台工程要求', '并发', '并发处理', '并发概念上限',
    '并发修改的合并结果与接收顺序无关', '幸存者偏差', '幻觉',
    '幸存者偏差', '幻觉', '库存扣减', '应用', '应用层', '应用场景',
    '延迟', '建设', '开悟', '弱点', '强制', '归纳', '形式化', '形成',
    '彻底转变', '微服务量化', '微服务架构', '必然', '必然王国', '必要', '思考',
    '总体', '总体计划', '总览', '总览文件', '悖论', '情况', '意图',
    '感', '感知', '成', '成本', '成果', '我', '或', '战', '战斗', '战略',
    '所有', '承诺', '技术', '技术债', '技術', '折中', '报告', '批判', '承受',
    '折磨', '挑战', '振动', '捕捉', '损失', '掌握', '描述', '提升', '提示',
    '搜索', '收敛', '改善', '效果', '整体', '整理', '断言', '新生',
    '方法', '方法论', '日程', '明了', '是', '普通', '最坏', '最优',
    '最有效', '最终', '服务', '期', '期间', '本质', '机会', '机制', '条件',
    '条款', '杠杆点', '极限', '架构', '构造', '构造方法', '构造证明',
    '析取', '某些', '标准', '标志', '核心', '核心命题', '核心原理',
    '核心挑战', '核心概念', '核心通信原语', '核心问题', '模型', '模式',
    '模式匹配', '欺诈', '正确性', '比较', '气象', '油条', '沟通', '消费',
    '消息', '温度', '演变', '灵感', '灰色', '热处理', '然后', '状态',
    '状态封装', '状态转换', '现代', '理论', '理论化', '理论边界', '理念',
    '生产', '生成', '用途', '画出', '界限', '痛苦', '的', '目的',
    '相应', '矛盾', '监控', '目标', '直接', '相位', '真相', '知识',
    '确定性', '程度', '稳定性', '空间', '策略', '筛', '算法', '管理',
    '类型', '系统化', '系统动力学', '系统思维', '系统性', '系统目标',
    '系统结构', '纯', '纯粹', '组成', '组织', '组织结构', '经验',
    '经验性', '维护', '缓冲区', '缓冲与参数', '编码', '编译', '缺陷',
    '网', '网络', '自由王国', '自身', '自主', '自然', '行业', '表明',
    '衰退', '规范', '规则', '视图', '认知', '认知偏误', '认知资源',
    '认知负载', '训练', '证明', '词汇', '语言', '课程', '调节回路（B）',
    '调节回路', '调试', '谬误', '负担', '负责人', '质量', '资源', '趋势',
    '路径', '输入', '输出', '过度', '过程', '运', '运行', '运行时',
    '运行时间', '近因谬误', '边界', '边缘', '过程', '迷惑', '选择',
    '逻辑', '逻辑谬误', '连锁', '通信', '通论', '通常', '速度', '速率',
    '部件', '部分', '部署', '重拍', '重要', '重视', '量', '量子',
    '量度', '问题', '问题的结构', '问题空间', '问题边界', '错误',
    '长度', '阅读', '隐含假设', '隐藏', '非', '非常', '革命',
    '风格', '风险', '飞行', '饥饿', '首部', '鬼', '魅力', '默认',
    '黑暗', '（B）', '（C）', '（P）', '（R）', '（Stock）', '（T）',
    '（A）', '（B', '（B）', '（C', '（E）', '（L）', '（N）',
    '一致性（C）', '可用性（A）', '分区容错（P）',
    '一致性（Agreement）', '有效性（Validity）', '终止性（Termination）',
    '全部副本', '不存在确定性算法', '两者：处理器独立工作', '串行部分',
    '严格一致性', '会话一致', '会话一致性', '传播单元', '传统Serverful',
    '位置透明', '你相信什么', '假设过于乐观', '假设验证', '偏序', '偏序集（Poset）',
    '元认知', '入职时间压缩', '全局库存', '公地悲剧', '公平性', '公平性保证',
    '共享DBA团队', '共享内存+锁', '共享数据库', '共同愿景', '共识', '共识要求',
    '关系', '典型系统', '内存', '内部锁服务', '决策复盘', '决策树图',
    '决策选项上限', '冷启动', '冷启动已解决', '减少嵌套', '分区', '分区时',
    '分区是二元事件', '分层（部门制）', '分布式', '分布式单体', '分布式原生',
    '分布式原生性', '分布式模式', '分布无关的守恒量', '分析方法',
    '分离逻辑', '则', '创始人', '创造性任务', '删除语义', '利用率',
    '半可判定', '半可判定性', '半格（Join-Semilattice）代数的实例化',
    '协调成本', '协调成本c', '协调成本系数', '协调自由', '单一职责',
    '单体', '单体优先', '单向因果', '单库瓶颈', '单调读', '即时最终性',
    '原文', '反方论证（架构约束论）', '反方（模块化单体/回归单体）核心论证',
    '反模式', '变化放大', '变更频率', '可信执行环境（TEE）', '可判定',
    '可判定性/权衡光谱', '可确定全序', '可确定因果', '后', '后端',
    '向量时钟', '吞吐量', '启动时间', '响应时间', '回流', '因果历史',
    '因果捕获', '团队规模', '图同态', '图同态的伪影', '在特定故障模型、网络假设和性能需求下，选择形式化可证的最优解',
    '在特定约束下的多目标优化', '在组织规模、业务边界、性能需求和运维能力约束下的多目标优化问题',
    '场景树图', '垃圾回收', '基线测试', '增强型回路（R）',
    '复杂子系统', '复杂度', '多Agent', '多活', '多维矩阵对比',
    '存储膨胀', '学习曲线', '安全关键', '安全启动', '安全性',
    '定理（HotStuff线性通信）', '定理（SEC保证）', '实现复杂度',
    '实现成本', '实现难度', '实际策略', '容易的路通常通回原地',
    '容量规划的第一性原理工具', '工程假设的精确校准器', '工程实现',
    '工程成熟度', '工程现实', '工程绕过', '工程频率', '工具/方法',
    '已提交', '带宽', '带宽效率', '常态', '平台', '平台团队',
    '平台工程要求', '并发', '并发处理', '并发概念上限',
    '并发修改的合并结果与接收顺序无关', '幸存者偏差', '幻觉',
}

# Patterns to auto-skip
SKIP_PATTERNS = [
    r'^\d+$',  # pure numbers
    r'^\d+[/%].*',  # numbers with % or /
    r'^\d+\.\s+',  # numbered lists like "10. "
    r'^(19|20)\d{2}',  # years
    r'^\d{4}年',  # Chinese years
    r'View/\d+\.md$',  # file references
    r'^P\d+$',  # P0-P7 etc
    r'^[\d\s\-/]+$',  # pure numbers and separators
    r'^(\d+个|\d+条|\d+种).*$',  # "14个总览文件"
    r'^.{40,}$',  # anything longer than 40 chars
    r'^.{35,}$',  # anything longer than 35 chars
]

def is_junk(term):
    """Check if a term is junk that shouldn't be in the index."""
    if term in BLOCKLIST:
        return True
    for pat in SKIP_PATTERNS:
        if re.match(pat, term):
            return True
    # Skip if it contains obvious sentence markers for long Chinese phrases
    if len(term) > 20 and ('，' in term or '。' in term or '；' in term):
        return True
    # Skip if it's clearly a file path
    if '/' in term and '.' in term:
        return True
    # Skip pure punctuation or whitespace
    if not re.search(r'\w', term) and not re.search(r'[\u4e00-\u9fff]', term):
        return True
    return False

def extract_bold_terms(text):
    """Extract all **term** patterns from markdown text."""
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
    """Get surrounding context for a term to help define it."""
    pattern = re.escape(term)
    match = re.search(pattern, text)
    if not match:
        return ""
    start = max(0, match.start() - window)
    end = min(len(text), match.end() + window)
    return text[start:end].replace('\n', ' ')

def parse_existing_index(filepath):
    """Parse the existing terminology index."""
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

def main():
    existing_terms, index_content = parse_existing_index(INDEX_FILE)
    print(f"Existing terms in index: {len(existing_terms)}")

    all_bold_terms = defaultdict(list)
    md_files = list(STRUCT_DIR.rglob("*.md"))
    md_files = [f for f in md_files if not (f.name == INDEX_FILE.name and f.parent.name == INDEX_FILE.parent.name)]
    
    for md_file in md_files:
        try:
            text = md_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Error reading {md_file}: {e}")
            continue
        terms = extract_bold_terms(text)
        for term in terms:
            context = get_file_context(text, term)
            all_bold_terms[term].append((str(md_file.relative_to(STRUCT_DIR)), context))

    print(f"Total unique bold terms found (filtered): {len(all_bold_terms)}")
    
    missing_terms = set(all_bold_terms.keys()) - set(existing_terms.keys())
    print(f"Missing terms from index: {len(missing_terms)}")
    
    orphan_terms = set(existing_terms.keys()) - set(all_bold_terms.keys())
    print(f"Orphan terms (in index but not in files): {len(orphan_terms)}")
    
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
        'orphan_terms': sorted(orphan_terms),
        'duplicates': list(set(duplicates)),
        'missing_details': missing_details,
    }
    
    report_path = Path("E:/_src/formal-architecture/terminology_audit_report_v2.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Report saved to {report_path}")
    
    for item in missing_details[:50]:
        print(f"- {item['term']} | {item['definition'][:60]} | {item['module']} | {item['file']}")
    if len(missing_details) > 50:
        print(f"... and {len(missing_details) - 50} more")

if __name__ == "__main__":
    main()
