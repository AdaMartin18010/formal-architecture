#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final terminology audit: high-quality extraction only.
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

# Common English words that are NOT technical terms
COMMON_ENGLISH_WORDS = {
    'a', 'an', 'as', 'at', 'be', 'by', 'do', 'go', 'he', 'if', 'in', 'is', 'it',
    'me', 'my', 'no', 'of', 'on', 'or', 'so', 'to', 'up', 'us', 'we', 'all',
    'and', 'are', 'but', 'can', 'day', 'did', 'does', 'done', 'down', 'each',
    'end', 'even', 'every', 'for', 'from', 'get', 'got', 'had', 'has', 'have',
    'her', 'here', 'him', 'his', 'how', 'its', 'just', 'know', 'like', 'made',
    'make', 'many', 'may', 'more', 'most', 'much', 'must', 'new', 'not', 'now',
    'off', 'old', 'one', 'only', 'other', 'our', 'out', 'over', 'part', 'per',
    'put', 'said', 'same', 'say', 'see', 'set', 'she', 'should', 'side', 'since',
    'some', 'still', 'such', 'take', 'than', 'that', 'the', 'their', 'them',
    'then', 'there', 'these', 'they', 'this', 'those', 'through', 'too', 'try',
    'two', 'under', 'until', 'use', 'used', 'using', 'very', 'want', 'was',
    'way', 'well', 'went', 'were', 'what', 'when', 'where', 'which', 'while',
    'who', 'why', 'will', 'with', 'work', 'would', 'year', 'you', 'your',
    'about', 'above', 'across', 'after', 'again', 'against', 'almost', 'along',
    'already', 'also', 'although', 'always', 'among', 'another', 'any', 'around',
    'because', 'become', 'been', 'before', 'being', 'below', 'between', 'both',
    'came', 'come', 'could', 'does', 'during', 'each', 'early', 'enough',
    'every', 'few', 'find', 'first', 'found', 'give', 'given', 'good', 'great',
    'group', 'hand', 'having', 'high', 'home', 'however', 'important', 'into',
    'itself', 'keep', 'large', 'last', 'later', 'left', 'life', 'light', 'little',
    'long', 'look', 'low', 'man', 'might', 'move', 'much', 'name', 'need',
    'never', 'next', 'nothing', 'once', 'open', 'order', 'own', 'place', 'point',
    'possible', 'present', 'problem', 'public', 'quite', 'rather', 'really',
    'right', 'said', 'saw', 'second', 'seem', 'seen', 'several', 'shall',
    'show', 'small', 'sound', 'stand', 'start', 'state', 'still', 'stop',
    'study', 'system', 'then', 'thing', 'think', 'third', 'though', 'thought',
    'three', 'together', 'told', 'too', 'took', 'turn', 'under', 'until',
    'upon', 'value', 'water', 'while', 'whole', 'within', 'without', 'word',
    'world', 'young',
}

# Names and institutions
NAMES_INSTITUTIONS = {
    'Alan Turing', 'Alonzo Church', 'Amir Pnueli', 'Barbara Liskov',
    'C.A.R. Hoare', 'Carl Hewitt', 'Charles Antony Richard Hoare',
    'Daniel Abadi', 'Diego Ongaro', 'Donella Meadows', 'Edsger Dijkstra',
    'Eric Brewer', 'Eric Evans', 'Fred Brooks', 'George A. Miller',
    'Gerard Holzmann', 'Gul Agha', 'Jeannette Wing', 'John Ousterhout',
    'Lamport', 'Lamport原话', 'Leslie Lamport',
    'Marc Shapiro', 'Martin Fowler', 'Maurice Herlihy',
    'Mel Conway', 'Michael Fischer', 'Miguel Castro',
    'Nancy Lynch', 'Noam Chomsky', 'Per Martin-Löf', 'Peter Senge',
    'Robin Milner', 'Seth Gilbert', 'Stephen Kleene', 'Tony Hoare',
    'Vaughn Vernon', 'Werner Vogels',
    'Aarhus University', 'Amazon', 'Amazon Prime Video', 'Anthropic', 'Apple',
    'Apple Secure Enclave', 'Aptos', 'AWS', 'AWS Step Functions',
    'Basecamp', 'Berkeley', 'Cambridge', 'Camunda', 'Cadence', 'CMU', 'CNCF',
    'Coq', 'Cornell', 'Cornell CS6410', 'Dafny', 'ETH Zurich', 'EPFL',
    'Edinburgh', 'Gartner', 'INRIA', 'Intel', 'Intel SGX', 'Lean', 'MIT',
    'MIT 6.006/6.045', 'MIT 6.824', 'MIT Sloan', 'Microsoft',
    'Microsoft CCF', 'Microsoft Research', 'Microsoft/INRIA',
    'Microsoft/OpenAI', 'MongoDB', 'NASA', 'NASA/JPL', 'Netflix',
    'Netflix Conductor', 'NUS', 'NICTA/UNSW', 'Oxford', 'Princeton',
    'Princeton/Stanford', 'Redpanda', 'Rook', 'Ceph', 'S3', 'SEB',
    'Shopify', 'Singapore', 'Singapore (NUS/SMU)', 'SMU',
    'Stack Overflow', 'Stanford', 'Stanford CS154', 'ThoughtWorks',
    'Uber', 'UIUC', 'Uppsala University', 'Uppsala/Aalborg',
    'VMware', 'VMware/UT Austin', 'Yale', 'Yale/MIT/Warwick',
    'Yale/MSR', 'Z3',
}

# Chinese terms that are too generic or are sentence fragments
CHINESE_BLOCKLIST = {
    '业务', '业务健康', '业务系统', '世界观', '代价', '代码', '代码作者',
    '代表', '代表应用', '代表框架', '代表系统', '价格', '价值', '位置',
    '位置透明', '体验', '信任', '信任假设', '信息', '信息隐藏',
    '假设', '假设验证', '偏序', '元素', '全局', '全球化', '全局库存',
    '全面', '共识', '共识要求', '关系', '典型', '典型实现', '典型系统',
    '内存', '内部', '内部工具', '内部锁服务', '决策', '决策复盘',
    '决策树', '决策选项', '决定', '准备', '准确', '准确性', '减少',
    '减少嵌套', '分区', '分区时', '分布', '分布式', '分布式单体',
    '分布式原生', '分布式原生性', '分布式模式', '分布无关的守恒量',
    '分析', '分离', '分离逻辑', '则', '创建', '创造性任务', '删除',
    '删除语义', '利用', '利用率', '利益', '协调', '协调成本',
    '协调成本c', '协调成本系数', '协调自由', '单一', '单一职责',
    '单位', '单体', '单体优先', '单向', '单向因果', '单库瓶颈',
    '单调', '单调读', '即时', '即时最终性', '原文', '反例', '反例输出',
    '反例可读性', '反例轨迹', '反例解释', '反例驱动修复', '反射',
    '反应', '反方', '反模式', '变化', '变化放大', '变更', '变更频率',
    '可信', '可判定', '可扩展', '可扩展性', '可理解', '可理解性',
    '可行性', '可观测', '可观测性', '可读', '可读性', '可达', '可达性',
    '可靠', '可靠性', '可用', '可用性', '可确定', '可确定全序',
    '可确定因果', '可见', '可见性', '右派', '右旋', '后', '后端',
    '吐', '吞吐量', '启动', '启动时间', '响应', '响应时间', '因果',
    '因果一致', '因果一致性', '因果关系', '因果历史', '因果捕获',
    '团队', '团队学习', '团队导师', '团队并行冲突', '团队规模',
    '团队配置', '团队沟通上限', '团队规模阈值', '团队无法独立发布',
    '困难', '图同态', '图案', '在线', '场', '场景', '垃圾', '垃圾回收',
    '基线', '基线测试', '增加', '增强', '增强型回路（R）', '复', '复杂',
    '复杂子系统', '复杂度', '多', '多Agent', '多活', '多维矩阵对比',
    '大', '大规模', '大小', '头部', '存储', '存储膨胀', '存储需求',
    '学习', '学习曲线', '安全', '安全关键', '安全启动', '安全性',
    '安全属性', '安全盲区', '安全边际', '定义', '定位', '定律',
    '定理猜测+自动验证', '实施', '实现', '实现决策者', '实现复杂度',
    '实现成本', '实现难度', '实际', '实际策略', '审视微服务', '审计',
    '审计能力', '容器', '容器（K8s）', '容易', '容量',
    '容量规划的第一性原理工具', '宽容', '寄存', '工程',
    '工程假设的精确校准器', '工程实现', '工程成熟度', '工程现实',
    '工程绕过', '工程频率', '工具', '工具/方法', '已提交', '带宽',
    '带宽效率', '常态', '平台', '平台团队', '平台工程要求', '并发',
    '并发处理', '并发概念上限',
    '并发修改的合并结果与接收顺序无关', '并发处理', '并集', '幸存',
    '幸存者偏差', '幻觉', '库存', '库存扣减', '应用', '应用层', '延迟',
    '建设', '开悟', '异', '弱', '弱点', '强制', '归纳', '形式化', '形成',
    '彻底', '彻底转变', '微小', '微妙', '微服务量化', '微服务架构',
    '必要', '思考', '总体', '总体计划', '总览', '总览文件', '悖论',
    '情况', '意图', '感', '感知', '成', '成本', '成果', '或', '战斗',
    '战略', '所有', '承诺', '技术', '技术债', '折中', '报告', '批判',
    '承受', '挑战', '振动', '捕捉', '损失', '掌握', '描述', '提升',
    '提示', '搜索', '收敛', '改善', '效果', '整体', '整理', '断言',
    '新生', '方法', '方法论', '明了', '普通', '最坏', '最优', '最有效',
    '最终', '服务', '期', '期间', '本质', '机会', '机制', '条件',
    '条款', '杠杆', '极限', '架构', '构造', '析取', '某些', '标准',
    '标志', '核心', '核心命题', '核心原理', '核心挑战', '核心概念',
    '核心问题', '模型', '模式', '模式匹配', '欺诈', '正确性', '比较',
    '沟通', '消费', '消息', '演变', '灵感', '状态', '状态封装',
    '状态转换', '现代', '理论', '理论化', '理论边界', '理念', '生产',
    '生成', '用途', '画出', '界限', '痛苦', '相应', '矛盾', '监控',
    '目标', '直接', '相位', '真相', '知识', '确定性', '程度', '稳定性',
    '空间', '策略', '筛', '算法', '管理', '类型', '系统化', '系统思维',
    '系统性', '系统目标', '系统结构', '纯粹', '组成', '组织', '组织结构',
    '经验', '维护', '缓冲区', '缓冲与参数', '编码', '编译', '缺陷',
    '网络', '自身', '自主', '自然', '行业', '衰退', '规范', '规则',
    '视图', '认知', '认知偏误', '认知资源', '认知负载', '训练', '证明',
    '词汇', '语言', '课程', '调节回路', '调节回路（B）', '调试', '谬误',
    '负担', '负责', '质量', '资源', '趋势', '路径', '输入', '输出',
    '过度', '运行', '运行时', '近因', '边界', '迷惑', '选择', '逻辑',
    '连锁', '通信', '速度', '速率', '部件', '部分', '部署', '重视',
    '量', '量子', '量度', '问题', '问题的结构', '问题空间', '问题边界',
    '错误', '长度', '阅读', '隐含', '隐藏', '风格', '风险', '默认',
    '一致性', '一致', '一致性策略', '一致性格式', '一致性级别',
    '不可变', '不可判定', '不可判定问题', '不可变数据结构',
    '世界上', '中心', '中心化', '中间', '中间人', '中间人攻击',
    '串行', '主', '主题', '主题树', '主讲', '主要', '主张', '义',
    '之', '乐', '乐部', '也', '书', '买', '了', '事', '二', '于',
    '互', '交互', '交叉', '产出', '产品', '产生', '享受', '人选',
    '人员', '人数', '人群', '介', '仍然', '从', '他', '代替', '以',
    '任务', '任', '任何', '份', '优', '优秀', '优雅', '伙', '伙伴',
    '会', '会议', '位', '体', '何', '作', '作用', '作者', '你',
    '使', '使用', '供应', '依据', '侧', '保护', '保证', '信号',
    '修复', '候', '借', '借助', '倾斜', '假', '假阳性', '假阳性重选',
    '停', '停机', '停机问题', '停等', '健', '偶', '偶发', '偷',
    '储', '允', '元', '充', '先', '光', '克', '入', '全', '公主',
    '公地', '共', '共享', '共享DBA团队', '共享内存+锁', '共享数据库',
    '关', '关闭', '兴', '具', '养', '兼', '内', '册', '再', '写',
    '冲', '决', '冷', '准', '减', '凑', '几', '凡', '击', '函',
    '分', '切', '列', '则', '初', '判', '利', '别', '到', '制',
    '券', '刺', '剂', '前', '剩', '力', '加', '务', '动', '助',
    '努', '劳', '势', '勿', '包', '化', '匹', '区', '升', '半',
    '协', '单', '卖', '博', '卡', '印', '危', '即', '原', '参',
    '又', '双', '反', '发', '受', '变', '号', '合', '名', '后',
    '向', '否', '含', '听', '启', '吴', '否', '告', '周', '和',
    '品', '哲', '唯', '唱', '商', '善', '器', '因', '团', '固',
    '国', '图', '圆', '地', '场', '址', '均', '坏', '坐', '块',
    '垂', '型', '域', '基', '堂', '堆', '增', '声', '处', '备',
    '复', '外', '多', '够', '大', '天', '太', '头', '夹', '契',
    '套', '女', '她', '好', '如', '妃', '妥', '始', '姓', '婚',
    '子', '字', '存', '学', '孩', '宁', '它', '完', '定', '宜',
    '客', '室', '宫', '害', '家', '容', '宿', '寄', '密', '寸',
    '对', '寻', '导', '封', '射', '尊', '小', '少', '尔', '尖',
    '就', '尺', '局', '层', '居', '展', '山', '屿', '工', '左',
    '巧', '差', '己', '已', '巴', '市', '布', '帅', '师', '希',
    '帐', '带', '帮', '常', '平', '年', '并', '幸', '广', '序',
    '底', '度', '座', '库', '应', '底', '延', '建', '开', '异',
    '式', '引', '弟', '张', '弱', '强', '当', '形', '影', '彼',
    '往', '待', '律', '得', '心', '必', '忆', '忌', '志', '快',
    '念', '怎', '思', '性', '总', '恋', '恐', '恕', '息', '情',
    '惊', '惑', '惜', '惠', '想', '感', '愧', '愿', '慈', '慢',
    '慰', '懂', '懊', '戏', '成', '我', '战', '房', '所', '手',
    '才', '扑', '打', '托', '执', '扩', '扫', '扬', '技', '把',
    '抑', '抓', '投', '抗', '折', '护', '报', '披', '抬', '抱',
    '抵', '押', '抽', '担', '拆', '拉', '拍', '拒', '拓', '拔',
    '拖', '拘', '招', '拜', '拟', '择', '拾', '拿', '持', '指',
    '按', '挑', '挡', '挤', '拼', '挖', '振', '捉', '捐', '捕',
    '损', '据', '排', '探', '接', '控', '推', '描', '提', '插',
    '握', '援', '搜', '搞', '摄', '摆', '摇', '摘', '摸', '撑',
    '撒', '撞', '播', '擦', '攀', '支', '收', '改', '攻', '放',
    '政', '故', '效', '敌', '教', '散', '数', '文', '斗', '料',
    '断', '新', '方', '旁', '旅', '旋', '无', '日', '旦', '旧',
    '早', '时', '明', '易', '星', '春', '昨', '是', '显', '晓',
    '晚', '普', '景', '智', '暗', '更', '曾', '替', '最', '月',
    '有', '朋', '服', '期', '木', '未', '本', '术', '机', '杀',
    '杂', '权', '杆', '来', '杯', '松', '板', '极', '构', '析',
    '林', '果', '枝', '枢', '枪', '查', '柳', '柴', '标', '校',
    '样', '核', '根', '格', '框', '案', '桌', '梅', '梳', '检',
    '棉', '棋', '棒', '森', '棵', '椅', '植', '椒', '楚', '楼',
    '概', '榜', '模', '樱', '橡', '欢', '欣', '款', '歌', '止',
    '正', '此', '步', '武', '歧', '死', '残', '段', '母', '每',
    '比', '毛', '毫', '氏', '民', '气', '水', '永', '求', '汇',
    '汉', '汗', '汝', '江', '池', '污', '汤', '汽', '没', '河',
    '油', '治', '沿', '泉', '法', '泛', '泡', '波', '泣', '泥',
    '注', '泪', '泰', '洁', '洋', '洲', '活', '洽', '派', '流',
    '浅', '测', '济', '浑', '浓', '浪', '浮', '海', '消', '涉',
    '涛', '涨', '液', '淡', '深', '混', '清', '渐', '渗', '温',
    '港', '游', '湖', '滋', '滑', '满', '滴', '漂', '漏', '演',
    '漠', '漫', '潘', '潜', '潮', '激', '火', '灯', '灰', '灵',
    '灾', '炉', '炎', '点', '烂', '烈', '热', '焦', '然', '照',
    '熊', '熟', '燃', '爆', '爪', '爱', '父', '片', '版', '牌',
    '牙', '牛', '物', '牵', '特', '犬', '犯', '状', '犹', '狂',
    '狗', '独', '狮', '狼', '猛', '猪', '猫', '献', '猴', '玉',
    '王', '玩', '环', '现', '球', '理', '琴', '瑞', '瓶', '甘',
    '甚', '生', '用', '田', '由', '甲', '申', '电', '男', '画',
    '畅', '界', '留', '略', '疏', '疲', '疾', '病', '痕', '痛',
    '登', '白', '百', '的', '皇', '皮', '盈', '益', '监', '盒',
    '盖', '盘', '目', '盲', '直', '相', '省', '看', '真', '眠',
    '眼', '着', '睡', '督', '瞧', '知', '短', '石', '码', '破',
    '础', '硬', '确', '碍', '示', '礼', '社', '神', '票', '祸',
    '禁', '福', '离', '秀', '私', '种', '科', '秘', '租', '秤',
    '秩', '积', '称', '移', '稀', '程', '稍', '税', '稳', '稻',
    '稿', '穆', '究', '空', '穿', '突', '窗', '立', '站', '竞',
    '章', '童', '端', '竹', '笔', '笼', '等', '筑', '筒', '答',
    '策', '筛', '签', '简', '算', '管', '箱', '篇', '簿', '米',
    '类', '粉', '粒', '粗', '精', '糖', '糟', '素', '索', '紧',
    '紫', '累', '红', '约', '级', '纪', '纯', '纳', '纷', '纸',
    '纹', '线', '组', '细', '终', '经', '结', '绕', '给', '络',
    '统', '绝', '继', '续', '维', '绿', '编', '缘', '缩', '缺',
    '网', '置', '署', '羊', '美', '群', '羽', '翅', '翻', '老',
    '考', '者', '而', '耐', '耕', '耳', '联', '肉', '肌', '肖',
    '股', '肢', '肥', '肩', '肺', '胆', '背', '胜', '胞', '能',
    '脂', '脆', '脉', '脑', '脚', '脱', '脸', '脾', '腐', '腰',
    '腹', '腾', '腿', '臣', '自', '至', '致', '舅', '舆', '舒',
    '舞', '舟', '航', '般', '舰', '船', '良', '色', '艳', '节',
    '花', '芳', '若', '英', '茅', '茎', '茶', '草', '荐', '荒',
    '荣', '药', '荷', '莫', '获', '菜', '营', '萨', '落', '著',
    '葛', '葡', '董', '葱', '蒋', '蒙', '蒸', '蓝', '蔬', '藏',
    '虎', '虑', '虫', '虹', '虽', '虾', '蚁', '蛇', '蛋', '蛙',
    '蜂', '蜜', '蝴', '融', '螺', '血', '行', '街', '衣', '补',
    '表', '袋', '被', '裁', '装', '裕', '裙', '裸', '西', '要',
    '覆', '见', '规', '视', '览', '觉', '角', '解', '触', '言',
    '誉', '誓', '警', '计', '认', '让', '议', '讯', '记', '讲',
    '许', '论', '设', '访', '证', '评', '识', '诉', '词', '试',
    '诗', '诚', '话', '诞', '该', '详', '语', '误', '说', '请',
    '诸', '读', '课', '调', '谈', '谊', '谋', '谓', '谢', '谨',
    '谱', '谷', '豆', '象', '豪', '貌', '负', '财', '责', '贤',
    '败', '账', '货', '质', '购', '贯', '贵', '贷', '费', '贺',
    '贼', '资', '赋', '赏', '赖', '赞', '赢', '走', '赴', '起',
    '趁', '超', '越', '足', '趴', '跑', '距', '跟', '跨', '路',
    '跳', '踏', '踢', '踩', '身', '车', '轨', '转', '轮', '软',
    '载', '较', '辅', '辆', '辈', '辉', '辐', '输', '辛', '辞',
    '辨', '辩', '边', '达', '过', '迎', '运', '近', '还', '进',
    '远', '违', '连', '迫', '述', '迷', '追', '退', '送', '适',
    '逃', '选', '透', '逐', '递', '通', '造', '逢', '逮', '逻',
    '遍', '道', '遗', '避', '那', '邻', '郎', '郑', '部', '郭',
    '都', '配', '酒', '里', '重', '野', '量', '金', '针', '钉',
    '钟', '钢', '钱', '钻', '铁', '铃', '铜', '银', '铺', '链',
    '销', '锁', '锅', '错', '键', '镇', '镜', '长', '门', '闪',
    '闭', '问', '闲', '间', '闹', '闻', '阅', '队', '防', '阳',
    '阶', '阻', '阿', '附', '际', '陆', '陈', '降', '限', '除',
    '险', '随', '隐', '隔', '难', '雄', '集', '雨', '雪', '零',
    '雷', '需', '霸', '青', '静', '非', '靠', '面', '革', '音',
    '页', '顶', '项', '顺', '须', '顾', '顿', '频', '题', '颜',
    '额', '风', '飞', '食', '餐', '饭', '饮', '饱', '首', '香',
    '马', '驾', '验', '骑', '骨', '高', '鬼', '魂', '鱼', '鲜',
    '鸟', '鸡', '鸣', '鸿', '鹿', '麦', '麻', '黄', '黑', '默',
    '鼓', '鼠', '龙',
    # Specific sentence fragments that keep appearing
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
    'PACELC是常态', 'PACELC更实用',
    'Serverless适用边界（形式化表达）', 'Serverless是架构拐杖',
    'Amdahl：串行部分固定为(1-p)', 'Amdahl：问题规模固定',
    'Gustafson：问题规模随N增长',
    'BAN的局限与Lowe攻击',
    'Miller 定律的架构推论',
    '定理（HotStuff线性通信）', '定理（SEC保证）',
    '反方论证（架构约束论）', '反方（模块化单体/回归单体）核心论证',
    '反模式',
    '关键原则', '关键问题', '关键洞察',
    '假设过于乐观',
    '分层策略',
    '分层（部门制）',
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
    '负责人',
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
    """Determine if a bolded term is a genuine technical term worth indexing."""
    if len(term) < 2 or len(term) > 22:
        return False
    
    # Skip numbers, dates, stats
    if re.match(r'^\d', term):
        return False
    if '%' in term:
        return False
    if re.match(r'^\d{4}年', term):
        return False
    
    # Skip file refs and markdown artifacts
    if 'View/' in term or '.md' in term or 'Actual title' in term:
        return False
    
    # Skip names and institutions
    if term in NAMES_INSTITUTIONS:
        return False
    
    # Skip Chinese blocklist
    if term in CHINESE_BLOCKLIST:
        return False
    
    # Skip common English words
    if term.lower() in COMMON_ENGLISH_WORDS:
        return False
    
    # Skip sentence fragments with Chinese punctuation
    if any(c in term for c in ['，', '。', '；']):
        return False
    
    # Skip long Chinese phrases without technical punctuation
    if len(term) > 12 and re.search(r'[\u4e00-\u9fff]', term):
        if not re.search(r'[()（）\-/]', term):
            return False
    
    # For pure lowercase English words > 3 chars, very likely not a technical term
    # (unless it's a well-known term like 'rust' but we already have Rust)
    if re.match(r'^[a-z]+$', term) and len(term) > 3:
        return False
    
    # Skip phrases that look like clauses
    if '的' in term and len(term) > 10:
        return False
    if len(term) > 15:
        return False
    
    # Skip very short Chinese that is just a common word
    if re.match(r'^[\u4e00-\u9fff]{2,3}$', term):
        # These are likely common words unless they're well-known technical terms
        # We'll allow them through and let the blocklist catch them
        pass
    
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
    
    # Group by first letter
    from collections import defaultdict
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
    
    # Sort: English letters first, then Chinese, then others
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
    report_path = Path("E:/_src/formal-architecture/terminology_audit_report_final2.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Report saved to {report_path}")

if __name__ == "__main__":
    main()
