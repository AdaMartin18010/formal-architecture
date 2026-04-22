#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminology audit v3: strict filtering for genuine technical terms.
"""

import os
import re
import json
from collections import defaultdict
from pathlib import Path

STRUCT_DIR = Path("E:/_src/formal-architecture/Struct")
INDEX_FILE = STRUCT_DIR / "99-参考文献与索引/02-核心概念反向索引与术语表.md"

# Files/directories to skip entirely
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

# Common Western names (partial list for heuristic)
COMMON_FIRST_NAMES = {
    'Alan', 'Alonzo', 'Amir', 'Barbara', 'Carl', 'Charles', 'Daniel', 'Diego',
    'Donella', 'Edsger', 'Eric', 'Fred', 'George', 'Gerard', 'Gul', 'Jeannette',
    'John', 'Leslie', 'Marc', 'Martin', 'Maurice', 'Mel', 'Michael', 'Miguel',
    'Nancy', 'Noam', 'Per', 'Peter', 'Robin', 'Seth', 'Stephen', 'Tony', 'Vaughn',
    'Werner',
}

COMMON_LAST_NAMES = {
    'Turing', 'Church', 'Hoare', 'Milner', 'Hewitt', 'Agha', 'Lamport',
    'Liskov', 'Brooks', 'Meadows', 'Dijkstra', 'Brewer', 'Evans', 'Fowler',
    'Ousterhout', 'Conway', 'Vogels', 'Vernon', 'Shapiro', 'Herlihy', 'Fischer',
    'Lynch', 'Gilbert', 'Abadi', 'Needham', 'Kleene', 'Pnueli', 'Wing', 'Castro',
    'Chomsky', 'Miller', 'Holzmann',
}

# Company/institution names to skip
INSTITUTIONS = {
    'Amazon', 'Anthropic', 'Apple', 'Aptos', 'Aarhus University',
    'AWS', 'Basecamp', 'Berkeley', 'Cambridge', 'CMU', 'CNCF',
    'Cornell', 'Delft', 'ETH Zurich', 'EPFL', 'Edinburgh',
    'Gartner', 'Google', 'INRIA', 'Intel', 'MIT', 'Microsoft',
    'MongoDB', 'NASA', 'Netflix', 'NUS', 'NSDI', 'Oxford',
    'Princeton', 'Shopify', 'Singapore', 'SMU', 'Stack Overflow',
    'Stanford', 'ThoughtWorks', 'Uber', 'UIUC', 'Uppsala University',
    'VMware', 'Yale', 'Z3',
}

# Generic/common words that shouldn't be in a technical index
GENERIC_WORDS = {
    '业务', '业务健康', '业务系统', '世界观', '代价', '代码', '代表', '代表应用',
    '代表框架', '代表系统', '假设', '假设验证', '元认知', '全局', '全球化',
    '全部副本', '公地悲剧', '共享', '关系', '内存', '决策', '决策树', '决策选项',
    '冷启动', '减少', '分区', '分层', '分布式', '分布式单体', '分布', '分析',
    '分离', '则', '创始人', '删除', '利用', '利用率', '协调', '单一', '单体',
    '单库', '单调', '即时', '原文', '反方', '反模式', '变化', '变更', '可信',
    '可判定', '可扩展', '可理解', '可行性', '可观测', '可读', '可达', '可靠',
    '可用', '可确定', '后端', '吞吐', '启动', '响应', '因果', '团队', '团队学习',
    '团队导师', '团队并行', '团队规模', '团队配置', '图同态', '在特定', '场景',
    '垃圾', '基线', '增强', '复杂', '复杂度', '多维', '存储', '学习', '安全',
    '安全关键', '安全启动', '安全性', '实现', '审慎', '审计', '容量', '工程',
    '已提交', '带宽', '常态', '平台', '平台团队', '平台工程', '并发', '并发处理',
    '并发概念', '并发修改', '幸存', '幻觉', '库存', '应用', '应用层', '建设',
    '开悟', '弱点', '强制', '归纳', '形式化', '形成', '彻底', '微服务量化',
    '微服务架构', '必然', '必要', '思考', '总体', '总览', '悖论', '情况', '意图',
    '感知', '成本', '成果', '承诺', '技术', '技术债', '折中', '报告', '批判',
    '承受', '挑战', '捕捉', '损失', '掌握', '描述', '提升', '提示', '搜索',
    '收敛', '改善', '效果', '整体', '整理', '断言', '方法', '方法论', '明了',
    '普通', '最坏', '最优', '最有效', '最终', '服务', '期间', '本质', '机会',
    '机制', '条件', '条款', '杠杆', '极限', '架构', '构造', '析取', '某些',
    '标准', '标志', '核心', '核心命题', '核心原理', '核心挑战', '核心概念',
    '核心问题', '模型', '模式', '欺诈', '正确性', '比较', '沟通', '消费',
    '消息', '演变', '灵感', '状态', '状态封装', '状态转换', '现代', '理论',
    '理论化', '理论边界', '理念', '生产', '生成', '用途', '画出', '界限',
    '痛苦', '相应', '矛盾', '监控', '目标', '直接', '相位', '真相', '知识',
    '确定性', '程度', '稳定性', '空间', '策略', '算法', '管理', '类型',
    '系统化', '系统思维', '系统性', '系统目标', '系统结构', '纯粹', '组成',
    '组织', '组织结构', '经验', '维护', '缓冲', '编码', '编译', '缺陷',
    '网络', '自身', '自主', '自然', '行业', '衰退', '规范', '规则', '视图',
    '认知', '认知偏误', '认知资源', '认知负载', '训练', '证明', '词汇', '语言',
    '课程', '调节回路', '调试', '谬误', '负担', '负责', '质量', '资源', '趋势',
    '路径', '输入', '输出', '过度', '运行', '运行时', '近因', '边界', '迷惑',
    '选择', '逻辑', '连锁', '通信', '速度', '速率', '部件', '部分', '部署',
    '重视', '量', '量子', '问题', '问题的结构', '问题空间', '问题边界', '错误',
    '长度', '阅读', '隐含', '隐藏', '风格', '风险', '默认',
    # English generics
    'Actual title', 'Analysis', 'Application', 'Approach', 'Architecture',
    'Area', 'Array', 'Aspect', 'Assessment', 'Asset', 'Assumption',
    'Attempt', 'Attribute', 'Author', 'Authority', 'Auto', 'Automation',
    'Availability', 'Awareness', 'Base', 'Basic', 'Basis', 'Behavior',
    'Benchmark', 'Benefit', 'Best', 'Better', 'Between', 'Block',
    'Blocking', 'Body', 'Book', 'Border', 'Both', 'Bottom', 'Boundary',
    'Branch', 'Break', 'Bridge', 'Brief', 'Bucket', 'Buffer', 'Build',
    'Builder', 'Building', 'Built', 'Bundle', 'Business', 'Busy',
    'Button', 'Buy', 'By', 'Byte', 'Cache', 'Calculate', 'Calculation',
    'Call', 'Callback', 'Caller', 'Can', 'Candidate', 'Capability',
    'Capacity', 'Capture', 'Card', 'Care', 'Career', 'Carrier', 'Case',
    'Cast', 'Catalog', 'Catch', 'Category', 'Cause', 'Caution', 'Cell',
    'Center', 'Central', 'Centric', 'Certain', 'Chain', 'Challenge',
    'Chance', 'Change', 'Channel', 'Chapter', 'Character', 'Charge',
    'Chart', 'Check', 'Child', 'Choice', 'Choose', 'Chunk', 'Circuit',
    'Circumstance', 'Claim', 'Class', 'Classic', 'Classification',
    'Clause', 'Clean', 'Clear', 'Click', 'Client', 'Climate', 'Clock',
    'Clone', 'Close', 'Cloud', 'Cluster', 'Code', 'Coding', 'Collapse',
    'Collection', 'Collector', 'Column', 'Combination', 'Combine',
    'Come', 'Comfort', 'Command', 'Comment', 'Commit', 'Common',
    'Communication', 'Community', 'Company', 'Compare', 'Comparison',
    'Compass', 'Compensation', 'Competence', 'Competition', 'Complex',
    'Complexity', 'Component', 'Compose', 'Composition', 'Compound',
    'Comprehension', 'Computation', 'Computer', 'Computing', 'Concept',
    'Concern', 'Conclusion', 'Condition', 'Conference', 'Confidence',
    'Config', 'Configuration', 'Confirm', 'Conflict', 'Conform',
    'Confront', 'Confusion', 'Connect', 'Connection', 'Consequence',
    'Conservation', 'Consider', 'Consistency', 'Consistent', 'Console',
    'Const', 'Constant', 'Constraint', 'Construct', 'Construction',
    'Consult', 'Consumer', 'Consumption', 'Contact', 'Container',
    'Contain', 'Content', 'Context', 'Continue', 'Continuous', 'Contract',
    'Contradiction', 'Contrast', 'Contribute', 'Contribution', 'Control',
    'Convenience', 'Convenient', 'Converge', 'Conversation', 'Convert',
    'Cook', 'Coordination', 'Copy', 'Core', 'Corner', 'Corpus',
    'Correct', 'Correspond', 'Cost', 'Count', 'Counter', 'Couple',
    'Course', 'Cover', 'Coverage', 'Craft', 'Create', 'Creation',
    'Creative', 'Creator', 'Credential', 'Credit', 'Crew', 'Crisis',
    'Criterion', 'Critical', 'Criticism', 'Cross', 'Crowd', 'Crucial',
    'Crude', 'Cruel', 'Crypt', 'Culture', 'Cup', 'Cure', 'Curiosity',
    'Current', 'Curriculum', 'Curve', 'Custom', 'Customer', 'Cut',
    'Cycle', 'Daily', 'Damage', 'Danger', 'Dark', 'Dashboard', 'Data',
    'Database', 'Date', 'Day', 'Dead', 'Deadline', 'Deal', 'Death',
    'Debate', 'Debt', 'Debug', 'Decade', 'Decay', 'Decide', 'Decision',
    'Deck', 'Declare', 'Decline', 'Decorate', 'Decrease', 'Dedicate',
    'Deep', 'Default', 'Defeat', 'Defect', 'Defense', 'Deficiency',
    'Deficit', 'Define', 'Definition', 'Degree', 'Delay', 'Delegate',
    'Delete', 'Deliberate', 'Delight', 'Deliver', 'Delivery', 'Demand',
    'Demo', 'Democracy', 'Demonstrate', 'Denial', 'Denote', 'Dense',
    'Density', 'Depart', 'Department', 'Depend', 'Dependency', 'Dependent',
    'Deploy', 'Deployment', 'Deposit', 'Deprecate', 'Depth', 'Deputy',
    'Derive', 'Descend', 'Describe', 'Description', 'Desert', 'Deserve',
    'Design', 'Designer', 'Desire', 'Desk', 'Desktop', 'Detail',
    'Detect', 'Detection', 'Determine', 'Develop', 'Developer',
    'Development', 'Device', 'Devise', 'Diagram', 'Dialog', 'Dictionary',
    'Die', 'Diet', 'Difference', 'Different', 'Difficult', 'Difficulty',
    'Dig', 'Digital', 'Dignity', 'Dimension', 'Dinner', 'Direct',
    'Direction', 'Director', 'Directory', 'Dirty', 'Disability',
    'Disadvantage', 'Disagree', 'Disappear', 'Disappoint', 'Disaster',
    'Discard', 'Discharge', 'Discipline', 'Disclose', 'Discount',
    'Discover', 'Discovery', 'Discrete', 'Discuss', 'Discussion',
    'Disease', 'Disk', 'Dismiss', 'Disorder', 'Display', 'Dispose',
    'Dispute', 'Disrupt', 'Distance', 'Distant', 'Distinct',
    'Distinction', 'Distinguish', 'Distort', 'Distribute', 'Distribution',
    'District', 'Disturb', 'Dive', 'Diverse', 'Divide', 'Division',
    'Do', 'Doctor', 'Document', 'Documentation', 'Dog', 'Domain',
    'Domestic', 'Dominant', 'Donate', 'Door', 'Dose', 'Dot', 'Double',
    'Doubt', 'Down', 'Draft', 'Drag', 'Drain', 'Drama', 'Draw',
    'Drawer', 'Drawing', 'Dream', 'Dress', 'Drift', 'Drill', 'Drink',
    'Drive', 'Driver', 'Drop', 'Drug', 'Dry', 'Due', 'Dump', 'During',
    'Dust', 'Duty', 'Dynamic', 'Each', 'Eager', 'Ear', 'Early',
    'Earn', 'Earth', 'Ease', 'Easily', 'East', 'Easy', 'Eat', 'Echo',
    'Economic', 'Economy', 'Edge', 'Edit', 'Edition', 'Editor',
    'Educate', 'Education', 'Educator', 'Effect', 'Effective',
    'Effectiveness', 'Efficiency', 'Efficient', 'Effort', 'Egg',
    'Eight', 'Either', 'Elaborate', 'Elect', 'Election', 'Electric',
    'Electricity', 'Electronic', 'Element', 'Elementary', 'Eliminate',
    'Elite', 'Else', 'Elsewhere', 'Email', 'Embark', 'Embed', 'Embrace',
    'Emerge', 'Emergency', 'Emit', 'Emotion', 'Emotional', 'Emphasis',
    'Emphasize', 'Empire', 'Employ', 'Employee', 'Employer',
    'Employment', 'Empty', 'Enable', 'Encounter', 'Encourage', 'End',
    'Endeavor', 'Ending', 'Enemy', 'Energy', 'Enforce', 'Engage',
    'Engine', 'Engineer', 'Engineering', 'Enhance', 'Enjoy', 'Enormous',
    'Enough', 'Enrich', 'Ensure', 'Enter', 'Enterprise', 'Entertain',
    'Entertainment', 'Enthusiasm', 'Entire', 'Entitle', 'Entity',
    'Entrance', 'Entry', 'Envelope', 'Environment', 'Environmental',
    'Episode', 'Equal', 'Equality', 'Equation', 'Equip', 'Equipment',
    'Era', 'Erase', 'Erect', 'Error', 'Escape', 'Especially', 'Essay',
    'Essence', 'Essential', 'Establish', 'Establishment', 'Estate',
    'Estimate', 'Ethical', 'Ethics', 'Ethnic', 'Evaluate', 'Evaluation',
    'Even', 'Evening', 'Event', 'Eventually', 'Ever', 'Every',
    'Everybody', 'Everyday', 'Everyone', 'Everything', 'Everywhere',
    'Evidence', 'Evil', 'Evoke', 'Evolution', 'Evolve', 'Exact',
    'Exactly', 'Exam', 'Examination', 'Examine', 'Example', 'Exceed',
    'Excellent', 'Except', 'Exception', 'Excerpt', 'Excess', 'Exchange',
    'Excite', 'Excitement', 'Exciting', 'Exclude', 'Exclusion',
    'Exclusive', 'Excuse', 'Execute', 'Execution', 'Executive', 'Exercise',
    'Exhaust', 'Exhibit', 'Exhibition', 'Exist', 'Existence', 'Existing',
    'Exit', 'Expand', 'Expansion', 'Expect', 'Expectation', 'Expense',
    'Expensive', 'Experience', 'Experiment', 'Expert', 'Expertise',
    'Explain', 'Explanation', 'Explicit', 'Explode', 'Exploit',
    'Exploration', 'Explore', 'Explorer', 'Explosion', 'Export',
    'Expose', 'Exposure', 'Express', 'Expression', 'Extend', 'Extension',
    'Extensive', 'Extent', 'External', 'Extra', 'Extract', 'Extraordinary',
    'Extreme', 'Eye', 'Fabric', 'Face', 'Facility', 'Fact', 'Factor',
    'Factory', 'Faculty', 'Fade', 'Fail', 'Failure', 'Fair', 'Faith',
    'Fall', 'False', 'Familiar', 'Family', 'Famous', 'Fan', 'Fancy',
    'Far', 'Farm', 'Farmer', 'Fashion', 'Fast', 'Fatal', 'Fate',
    'Father', 'Fault', 'Favor', 'Favorite', 'Fear', 'Feature', 'Federal',
    'Fee', 'Feed', 'Feedback', 'Feel', 'Feeling', 'Fellow', 'Female',
    'Fence', 'Festival', 'Fetch', 'Fever', 'Few', 'Fiber', 'Fiction',
    'Field', 'Fierce', 'Fifteen', 'Fifth', 'Fifty', 'Fig', 'Fight',
    'Figure', 'File', 'Fill', 'Film', 'Filter', 'Final', 'Finally',
    'Finance', 'Financial', 'Find', 'Finding', 'Fine', 'Finger',
    'Finish', 'Fire', 'Firm', 'First', 'Fish', 'Fishing', 'Fit',
    'Fitness', 'Five', 'Fix', 'Flag', 'Flame', 'Flash', 'Flat',
    'Flavor', 'Flee', 'Fleet', 'Flesh', 'Flexibility', 'Flexible',
    'Flight', 'Flip', 'Float', 'Flood', 'Floor', 'Flour', 'Flow',
    'Flower', 'Fluctuate', 'Fluency', 'Fluid', 'Fly', 'Focus', 'Fold',
    'Folk', 'Follow', 'Following', 'Food', 'Foot', 'Football', 'For',
    'Force', 'Forecast', 'Foreign', 'Forest', 'Forever', 'Forget',
    'Forgive', 'Form', 'Formal', 'Format', 'Formation', 'Former',
    'Formula', 'Fort', 'Fortune', 'Forty', 'Forum', 'Forward', 'Fossil',
    'Foster', 'Found', 'Foundation', 'Founder', 'Four', 'Fourteen',
    'Fourth', 'Fox', 'Frame', 'Framework', 'Free', 'Freedom', 'Freeze',
    'Frequency', 'Frequent', 'Fresh', 'Friend', 'Friendly', 'Friendship',
    'Frighten', 'From', 'Front', 'Fruit', 'Fuel', 'Full', 'Fully',
    'Fun', 'Function', 'Functional', 'Fund', 'Fundamental', 'Funding',
    'Funeral', 'Funny', 'Furniture', 'Further', 'Future', 'Gain', 'Gallery',
    'Game', 'Gap', 'Garage', 'Garden', 'Gas', 'Gate', 'Gather', 'Gauge',
    'Gaze', 'Gear', 'Gender', 'Gene', 'General', 'Generally', 'Generate',
    'Generation', 'Generic', 'Generous', 'Genetic', 'Genius', 'Genre',
    'Gentle', 'Gentleman', 'Genuine', 'Gesture', 'Get', 'Ghost', 'Giant',
    'Gift', 'Girl', 'Give', 'Glad', 'Glance', 'Glass', 'Global', 'Glove',
    'Go', 'Goal', 'God', 'Gold', 'Golden', 'Golf', 'Good', 'Govern',
    'Government', 'Governor', 'Grab', 'Grade', 'Gradually', 'Graduate',
    'Grain', 'Grand', 'Grant', 'Graph', 'Graphic', 'Grasp', 'Grass',
    'Grateful', 'Grave', 'Great', 'Green', 'Grocery', 'Ground', 'Group',
    'Grow', 'Growth', 'Guarantee', 'Guard', 'Guess', 'Guest', 'Guide',
    'Guideline', 'Guilty', 'Gulf', 'Gun', 'Guy', 'Habit', 'Habitat',
    'Hair', 'Half', 'Hall', 'Hand', 'Handle', 'Hang', 'Happen',
    'Happy', 'Hard', 'Harm', 'Hat', 'Hate', 'Have', 'Hazard', 'Head',
    'Headache', 'Headline', 'Heal', 'Health', 'Healthy', 'Hear',
    'Heart', 'Heat', 'Heaven', 'Heavy', 'Height', 'Hell', 'Hello',
    'Help', 'Helpful', 'Hence', 'Her', 'Here', 'Heritage', 'Hero',
    'Herself', 'Hide', 'High', 'Highlight', 'Highly', 'Highway', 'Hill',
    'Him', 'Himself', 'Hint', 'Hip', 'Hire', 'His', 'Historian',
    'Historic', 'Historical', 'History', 'Hit', 'Hold', 'Hole',
    'Holiday', 'Holy', 'Home', 'Homework', 'Honest', 'Honey', 'Honor',
    'Hook', 'Hope', 'Horizon', 'Horror', 'Horse', 'Hospital', 'Host',
    'Hot', 'Hotel', 'Hour', 'House', 'Household', 'Housing', 'How',
    'However', 'Huge', 'Human', 'Humor', 'Hundred', 'Hunger', 'Hunt',
    'Hunter', 'Hurry', 'Hurt', 'Husband', 'Hypothesis', 'Ice', 'Idea',
    'Ideal', 'Identify', 'Identity', 'If', 'Ignore', 'Ill', 'Illegal',
    'Illness', 'Illustrate', 'Image', 'Imagination', 'Imagine',
    'Immediate', 'Immediately', 'Immigrant', 'Immigration', 'Impact',
    'Implement', 'Implementation', 'Implication', 'Implicit', 'Imply',
    'Import', 'Importance', 'Important', 'Impose', 'Impossible',
    'Impress', 'Impression', 'Impressive', 'Improve', 'Improvement',
    'In', 'Incentive', 'Incident', 'Include', 'Including', 'Income',
    'Incorporate', 'Increase', 'Increasingly', 'Incredible', 'Indeed',
    'Independence', 'Independent', 'Index', 'Indicate', 'Indication',
    'Individual', 'Industry', 'Inevitable', 'Infant', 'Infection',
    'Infer', 'Inflation', 'Influence', 'Inform', 'Informal',
    'Information', 'Ingredient', 'Initial', 'Initially', 'Initiate',
    'Initiative', 'Injure', 'Injury', 'Inner', 'Innocent', 'Innovation',
    'Innovative', 'Input', 'Inquiry', 'Insect', 'Insert', 'Inside',
    'Insight', 'Insist', 'Inspect', 'Inspection', 'Inspire', 'Install',
    'Instance', 'Instead', 'Instinct', 'Institution', 'Instruction',
    'Instructor', 'Instrument', 'Insurance', 'Intact', 'Intake',
    'Integral', 'Integrate', 'Integration', 'Integrity', 'Intellectual',
    'Intelligence', 'Intelligent', 'Intend', 'Intense', 'Intensity',
    'Intent', 'Intention', 'Interact', 'Interaction', 'Interest',
    'Interested', 'Interesting', 'Interface', 'Interfere', 'Interior',
    'Internal', 'International', 'Internet', 'Interpret',
    'Interpretation', 'Interrupt', 'Interval', 'Intervention',
    'Interview', 'Into', 'Introduce', 'Introduction', 'Invade',
    'Invasion', 'Invent', 'Invention', 'Invest', 'Investigate',
    'Investigation', 'Investigator', 'Investment', 'Investor', 'Invite',
    'Involve', 'Involvement', 'Iron', 'Island', 'Isolate', 'Isolation',
    'Issue', 'Item', 'Its', 'Itself', 'Jacket', 'Jail', 'Jam', 'Job',
    'Join', 'Joint', 'Joke', 'Journal', 'Journey', 'Joy', 'Judge',
    'Judgment', 'Juice', 'Jump', 'Jungle', 'Junior', 'Jury', 'Just',
    'Justice', 'Justify', 'Keen', 'Keep', 'Key', 'Kick', 'Kid',
    'Kill', 'Kind', 'King', 'Kiss', 'Kitchen', 'Knee', 'Knife',
    'Knock', 'Know', 'Knowledge', 'Lab', 'Label', 'Labor', 'Laboratory',
    'Lack', 'Ladder', 'Lady', 'Lake', 'Lamp', 'Land', 'Landscape',
    'Lane', 'Language', 'Large', 'Largely', 'Last', 'Late', 'Later',
    'Latest', 'Latter', 'Laugh', 'Launch', 'Law', 'Lawn', 'Lawsuit',
    'Lawyer', 'Lay', 'Layer', 'Lazy', 'Lead', 'Leader', 'Leadership',
    'Leading', 'Leaf', 'League', 'Lean', 'Learn', 'Learning', 'Least',
    'Leave', 'Lecture', 'Left', 'Leg', 'Legal', 'Legend', 'Legislation',
    'Legitimate', 'Leisure', 'Lemon', 'Lend', 'Length', 'Lens', 'Less',
    'Lesson', 'Let', 'Letter', 'Level', 'Liberal', 'Liberty', 'Library',
    'License', 'Lie', 'Life', 'Lifestyle', 'Lifetime', 'Lift', 'Light',
    'Like', 'Likely', 'Likewise', 'Limit', 'Limitation', 'Limited',
    'Line', 'Link', 'Lion', 'Lip', 'Liquid', 'List', 'Listen',
    'Literally', 'Literary', 'Literature', 'Little', 'Live', 'Living',
    'Load', 'Loan', 'Local', 'Locate', 'Location', 'Lock', 'Log',
    'Logic', 'Logical', 'Lonely', 'Long', 'Long-term', 'Look', 'Loose',
    'Lose', 'Loss', 'Lot', 'Loud', 'Love', 'Lovely', 'Low', 'Lower',
    'Loyal', 'Luck', 'Lucky', 'Lunch', 'Lung', 'Machine', 'Mad',
    'Magazine', 'Magic', 'Magnetic', 'Magnificent', 'Main', 'Mainly',
    'Maintain', 'Maintenance', 'Major', 'Majority', 'Make', 'Maker',
    'Makeup', 'Male', 'Mall', 'Man', 'Manage', 'Management', 'Manager',
    'Manner', 'Manufacturer', 'Manufacturing', 'Many', 'Map', 'March',
    'Margin', 'Mark', 'Market', 'Marketing', 'Marriage', 'Married',
    'Marry', 'Mass', 'Massive', 'Master', 'Match', 'Mate', 'Material',
    'Math', 'Mathematics', 'Matter', 'Maximum', 'May', 'Maybe', 'Meal',
    'Mean', 'Meaning', 'Meanwhile', 'Measure', 'Measurement', 'Meat',
    'Mechanism', 'Media', 'Medical', 'Medicine', 'Medium', 'Meet',
    'Meeting', 'Member', 'Membership', 'Memory', 'Mental', 'Mention',
    'Menu', 'Merchant', 'Mercy', 'Merely', 'Merge', 'Merit', 'Mess',
    'Message', 'Metal', 'Meter', 'Method', 'Methodology', 'Middle',
    'Midnight', 'Might', 'Mild', 'Mile', 'Military', 'Milk', 'Mill',
    'Million', 'Mind', 'Mine', 'Mineral', 'Minimal', 'Minimize',
    'Minimum', 'Minister', 'Minor', 'Minority', 'Minute', 'Miracle',
    'Mirror', 'Miss', 'Mission', 'Mistake', 'Mix', 'Mixed', 'Mixture',
    'Mobile', 'Mode', 'Model', 'Moderate', 'Modern', 'Modest', 'Modify',
    'Moment', 'Money', 'Monitor', 'Monitoring', 'Month', 'Mood', 'Moon',
    'Moral', 'Moreover', 'Morning', 'Mortgage', 'Most', 'Mostly',
    'Mother', 'Motion', 'Motivate', 'Motivation', 'Motive', 'Motor',
    'Mount', 'Mountain', 'Mouse', 'Mouth', 'Move', 'Movement', 'Movie',
    'Much', 'Multiple', 'Murder', 'Muscle', 'Museum', 'Music',
    'Musical', 'Musician', 'Must', 'Mutual', 'My', 'Myself', 'Mystery',
    'Myth', 'Nail', 'Name', 'Narrative', 'Narrow', 'Nation', 'National',
    'Native', 'Natural', 'Naturally', 'Nature', 'Naval', 'Near',
    'Nearby', 'Nearly', 'Necessary', 'Neck', 'Need', 'Negative',
    'Neglect', 'Negotiate', 'Negotiation', 'Neighbor', 'Neighborhood',
    'Neither', 'Nerve', 'Nervous', 'Net', 'Network', 'Neutral', 'Never',
    'Nevertheless', 'New', 'Newly', 'News', 'Newspaper', 'Next', 'Nice',
    'Night', 'Nine', 'No', 'Nobody', 'Nod', 'Noise', 'Nomination',
    'None', 'Nonetheless', 'Nor', 'Normal', 'Normally', 'North',
    'Northeast', 'Northern', 'Northwest', 'Norwegian', 'Nose', 'Not',
    'Note', 'Nothing', 'Notice', 'Notion', 'Novel', 'Now', 'Nowadays',
    'Nowhere', 'Nuclear', 'Number', 'Numerous', 'Nurse', 'Nut',
    'Nutrition', 'Object', 'Objective', 'Obligation', 'Observation',
    'Observe', 'Observer', 'Obstacle', 'Obtain', 'Obvious', 'Obviously',
    'Occasion', 'Occasionally', 'Occupy', 'Occur', 'Ocean', 'Odd',
    'Odds', 'Of', 'Off', 'Offense', 'Offensive', 'Offer', 'Office',
    'Officer', 'Official', 'Often', 'Oil', 'Okay', 'Old', 'Olympic',
    'On', 'Once', 'One', 'Ongoing', 'Onion', 'Online', 'Only', 'Onto',
    'Open', 'Opening', 'Operate', 'Operating', 'Operation', 'Operational',
    'Operator', 'Opinion', 'Opponent', 'Opportunity', 'Oppose',
    'Opposite', 'Opposition', 'Opt', 'Optical', 'Optimism', 'Optimistic',
    'Option', 'Or', 'Orange', 'Order', 'Ordinary', 'Organ', 'Organic',
    'Organization', 'Organizational', 'Organize', 'Orientation',
    'Origin', 'Original', 'Originally', 'Other', 'Otherwise', 'Ought',
    'Our', 'Ourselves', 'Out', 'Outcome', 'Outdoor', 'Outer', 'Outlet',
    'Outline', 'Output', 'Outside', 'Outsider', 'Outstanding', 'Over',
    'Overall', 'Overcome', 'Overlook', 'Overnight', 'Overseas', 'Owe',
    'Own', 'Owner', 'Ownership', 'Oxford', 'Pace', 'Pack', 'Package',
    'Pad', 'Page', 'Pain', 'Painful', 'Paint', 'Painter', 'Painting',
    'Pair', 'Palace', 'Pale', 'Palm', 'Pan', 'Panel', 'Panic', 'Pants',
    'Paper', 'Parent', 'Park', 'Parking', 'Part', 'Participant',
    'Participate', 'Participation', 'Particle', 'Particular',
    'Particularly', 'Partner', 'Partnership', 'Party', 'Pass', 'Passage',
    'Passenger', 'Passion', 'Past', 'Patch', 'Patent', 'Path', 'Patience',
    'Patient', 'Pattern', 'Pause', 'Pay', 'Payment', 'Peace', 'Peaceful',
    'Peak', 'Peer', 'Penalty', 'People', 'Pepper', 'Per', 'Perceive',
    'Percent', 'Percentage', 'Perception', 'Perfect', 'Perfectly',
    'Perform', 'Performance', 'Perhaps', 'Period', 'Permanent',
    'Permission', 'Permit', 'Person', 'Personal', 'Personally',
    'Personality', 'Personnel', 'Perspective', 'Persuade', 'Pet',
    'Phase', 'Phenomenon', 'Philosophy', 'Phone', 'Photo', 'Photograph',
    'Photographer', 'Phrase', 'Physical', 'Physically', 'Physics',
    'Piano', 'Pick', 'Picture', 'Pie', 'Piece', 'Pig', 'Pile', 'Pilot',
    'Pin', 'Pine', 'Pink', 'Pipe', 'Pitch', 'Pity', 'Place', 'Plain',
    'Plan', 'Plane', 'Planet', 'Planning', 'Plant', 'Plastic', 'Plate',
    'Platform', 'Play', 'Player', 'Plea', 'Please', 'Pleasure', 'Plenty',
    'Plot', 'Plus', 'Pocket', 'Poem', 'Poet', 'Poetry', 'Point',
    'Poison', 'Polar', 'Pole', 'Police', 'Policy', 'Political',
    'Politically', 'Politician', 'Politics', 'Poll', 'Pollution',
    'Pool', 'Poor', 'Pop', 'Popular', 'Population', 'Port', 'Portfolio',
    'Portion', 'Portrait', 'Pose', 'Position', 'Positive', 'Positively',
    'Possess', 'Possession', 'Possibility', 'Possible', 'Possibly',
    'Post', 'Pot', 'Potato', 'Potential', 'Potentially', 'Pound',
    'Pour', 'Poverty', 'Powder', 'Power', 'Powerful', 'Practical',
    'Practically', 'Practice', 'Pray', 'Prayer', 'Precise', 'Precisely',
    'Predict', 'Prediction', 'Prefer', 'Preference', 'Pregnancy',
    'Pregnant', 'Premise', 'Preparation', 'Prepare', 'Prescription',
    'Presence', 'Present', 'Presentation', 'Preserve', 'President',
    'Presidential', 'Press', 'Pressure', 'Pretend', 'Pretty', 'Prevent',
    'Previous', 'Previously', 'Price', 'Pride', 'Priest', 'Primarily',
    'Primary', 'Prime', 'Principal', 'Principle', 'Print', 'Prior',
    'Priority', 'Prison', 'Prisoner', 'Privacy', 'Private', 'Privately',
    'Probably', 'Problem', 'Procedure', 'Proceed', 'Process', 'Produce',
    'Producer', 'Product', 'Production', 'Profession', 'Professional',
    'Professor', 'Profile', 'Profit', 'Profound', 'Program', 'Progress',
    'Progressive', 'Prohibit', 'Project', 'Prominent', 'Promise',
    'Promote', 'Promotion', 'Prompt', 'Proof', 'Proper', 'Properly',
    'Property', 'Proportion', 'Proposal', 'Propose', 'Proposed',
    'Prosecution', 'Prospect', 'Protect', 'Protection', 'Protective',
    'Protein', 'Protest', 'Proud', 'Prove', 'Provide', 'Provider',
    'Province', 'Provision', 'Psychological', 'Psychologist', 'Psychology',
    'Public', 'Publicly', 'Publish', 'Publisher', 'Pull', 'Pump',
    'Punch', 'Punishment', 'Pupil', 'Purchase', 'Pure', 'Purely',
    'Purpose', 'Pursue', 'Push', 'Put', 'Qualify', 'Quality',
    'Quantity', 'Quarter', 'Queen', 'Question', 'Quick', 'Quickly',
    'Quiet', 'Quietly', 'Quit', 'Quite', 'Quote', 'Race', 'Racial',
    'Radical', 'Radio', 'Rail', 'Raise', 'Range', 'Rank', 'Rapid',
    'Rapidly', 'Rare', 'Rarely', 'Rate', 'Rather', 'Rating', 'Ratio',
    'Raw', 'Reach', 'React', 'Reaction', 'Read', 'Reader', 'Reading',
    'Ready', 'Real', 'Reality', 'Realize', 'Really', 'Reason',
    'Reasonable', 'Recall', 'Receive', 'Recent', 'Recently',
    'Reception', 'Recipe', 'Recognition', 'Recognize', 'Recommend',
    'Recommendation', 'Record', 'Recording', 'Recover', 'Recovery',
    'Recruit', 'Recruitment', 'Recycle', 'Red', 'Reduce', 'Reduction',
    'Refer', 'Reference', 'Reflect', 'Reflection', 'Reform', 'Refugee',
    'Refuse', 'Regard', 'Regarding', 'Regardless', 'Regime', 'Region',
    'Regional', 'Register', 'Registration', 'Regret', 'Regular',
    'Regularly', 'Regulate', 'Regulation', 'Reinforce', 'Reject',
    'Relate', 'Relation', 'Relationship', 'Relative', 'Relatively',
    'Relax', 'Release', 'Relevant', 'Reliability', 'Reliable', 'Relief',
    'Relieve', 'Religion', 'Religious', 'Rely', 'Remain', 'Remaining',
    'Remark', 'Remarkable', 'Remind', 'Remote', 'Removal', 'Remove',
    'Repeat', 'Repeatedly', 'Replace', 'Replacement', 'Reply', 'Report',
    'Reporter', 'Represent', 'Representation', 'Representative',
    'Republic', 'Reputation', 'Request', 'Require', 'Requirement',
    'Rescue', 'Research', 'Researcher', 'Resemble', 'Reservation',
    'Reserve', 'Resident', 'Residential', 'Resist', 'Resistance',
    'Resolution', 'Resolve', 'Resort', 'Resource', 'Respect',
    'Respective', 'Respond', 'Response', 'Responsibility', 'Responsible',
    'Rest', 'Restaurant', 'Restore', 'Restrict', 'Restriction',
    'Result', 'Retain', 'Retire', 'Retirement', 'Retreat', 'Return',
    'Reveal', 'Revenue', 'Reverse', 'Review', 'Revolution', 'Reward',
    'Rhythm', 'Rice', 'Rich', 'Rid', 'Ride', 'Ridiculous', 'Right',
    'Ring', 'Rise', 'Risk', 'Rival', 'River', 'Road', 'Robot', 'Rock',
    'Role', 'Roll', 'Romantic', 'Roof', 'Room', 'Root', 'Rope', 'Rough',
    'Round', 'Route', 'Routine', 'Row', 'Royal', 'Rub', 'Rule', 'Run',
    'Running', 'Rural', 'Rush', 'Sad', 'Safe', 'Safety', 'Sake', 'Salad',
    'Salary', 'Sale', 'Salt', 'Same', 'Sample', 'Sanction', 'Sand',
    'Satellite', 'Satisfaction', 'Satisfy', 'Sauce', 'Save', 'Saving',
    'Say', 'Scale', 'Scandal', 'Scare', 'Scenario', 'Scene', 'Schedule',
    'Scheme', 'Scholar', 'Scholarship', 'School', 'Science', 'Scientific',
    'Scientist', 'Scope', 'Score', 'Scream', 'Screen', 'Script',
    'Sea', 'Search', 'Season', 'Seat', 'Second', 'Secondary', 'Secret',
    'Secretary', 'Section', 'Sector', 'Secure', 'Security', 'See',
    'Seed', 'Seek', 'Seem', 'Segment', 'Seize', 'Select', 'Selection',
    'Self', 'Sell', 'Senate', 'Senator', 'Send', 'Senior', 'Sensation',
    'Sense', 'Sensitive', 'Sentence', 'Separate', 'Sequence', 'Series',
    'Serious', 'Seriously', 'Serve', 'Service', 'Session', 'Set',
    'Setting', 'Settle', 'Settlement', 'Seven', 'Several', 'Severe',
    'Sew', 'Sex', 'Sexual', 'Shade', 'Shadow', 'Shake', 'Shall',
    'Shape', 'Share', 'Sharp', 'She', 'Shelf', 'Shell', 'Shelter',
    'Shift', 'Shine', 'Ship', 'Shirt', 'Shock', 'Shoe', 'Shoot',
    'Shop', 'Shopping', 'Short', 'Shortly', 'Shot', 'Should', 'Shoulder',
    'Shout', 'Show', 'Shower', 'Shrug', 'Shut', 'Sick', 'Side',
    'Sigh', 'Sight', 'Sign', 'Signal', 'Signature', 'Significance',
    'Significant', 'Significantly', 'Silence', 'Silent', 'Silver',
    'Similar', 'Similarly', 'Simple', 'Simply', 'Sin', 'Since',
    'Sing', 'Singer', 'Single', 'Sink', 'Sir', 'Sister', 'Sit',
    'Site', 'Situation', 'Six', 'Size', 'Ski', 'Skill', 'Skin',
    'Skip', 'Skirt', 'Sky', 'Slave', 'Sleep', 'Slice', 'Slide',
    'Slight', 'Slightly', 'Slip', 'Slow', 'Slowly', 'Small', 'Smart',
    'Smell', 'Smile', 'Smoke', 'Smooth', 'Snap', 'Snow', 'So',
    'So-called', 'Soccer', 'Social', 'Socially', 'Society', 'Soft',
    'Software', 'Soil', 'Solar', 'Soldier', 'Solid', 'Solution',
    'Solve', 'Some', 'Somebody', 'Somehow', 'Someone', 'Something',
    'Sometimes', 'Somewhat', 'Somewhere', 'Son', 'Song', 'Soon',
    'Sorry', 'Sort', 'Soul', 'Sound', 'Soup', 'Source', 'South',
    'Southeast', 'Southern', 'Southwest', 'Space', 'Spare', 'Speak',
    'Speaker', 'Special', 'Specialist', 'Specialize', 'Specific',
    'Specifically', 'Specification', 'Spectacular', 'Spectrum',
    'Speech', 'Speed', 'Spell', 'Spend', 'Spending', 'Sphere', 'Spider',
    'Spin', 'Spirit', 'Spiritual', 'Split', 'Spokesman', 'Sport',
    'Spot', 'Spread', 'Spring', 'Square', 'Squeeze', 'Stability',
    'Stable', 'Staff', 'Stage', 'Stair', 'Stake', 'Stand', 'Standard',
    'Standing', 'Star', 'Stare', 'Start', 'Starve', 'State', 'Statement',
    'Station', 'Statistics', 'Status', 'Stay', 'Steady', 'Steal',
    'Steam', 'Steel', 'Step', 'Stick', 'Still', 'Stir', 'Stock',
    'Stomach', 'Stone', 'Stop', 'Storage', 'Store', 'Storm', 'Story',
    'Straight', 'Strange', 'Stranger', 'Strategic', 'Strategy', 'Stream',
    'Street', 'Strength', 'Strengthen', 'Stress', 'Stretch', 'Strike',
    'String', 'Strip', 'Stroke', 'Strong', 'Strongly', 'Structure',
    'Struggle', 'Student', 'Studio', 'Study', 'Stuff', 'Stupid',
    'Style', 'Subject', 'Submit', 'Subsequent', 'Substance',
    'Substantial', 'Substantially', 'Substitute', 'Subtle', 'Suburb',
    'Succeed', 'Success', 'Successful', 'Successfully', 'Such',
    'Sudden', 'Suddenly', 'Sue', 'Suffer', 'Sufficient', 'Sugar',
    'Suggest', 'Suggestion', 'Suicide', 'Suit', 'Suitable', 'Sum',
    'Summary', 'Summer', 'Summit', 'Sun', 'Super', 'Superior',
    'Supermarket', 'Supply', 'Support', 'Supporter', 'Suppose',
    'Supposed', 'Sure', 'Surely', 'Surface', 'Surgery', 'Surprise',
    'Surprised', 'Surprising', 'Surprisingly', 'Surround', 'Survey',
    'Survival', 'Survive', 'Survivor', 'Suspect', 'Suspend', 'Suspicion',
    'Sustain', 'Sustainable', 'Swallow', 'Swear', 'Sweat', 'Sweep',
    'Sweet', 'Swim', 'Swing', 'Switch', 'Symbol', 'Sympathy',
    'Symptom', 'System', 'Table', 'Tablespoon', 'Tactic', 'Tail',
    'Take', 'Tale', 'Talent', 'Talk', 'Tall', 'Tank', 'Tap', 'Tape',
    'Target', 'Task', 'Taste', 'Tax', 'Taxpayer', 'Tea', 'Teach',
    'Teacher', 'Teaching', 'Team', 'Tear', 'Teaspoon', 'Technical',
    'Technique', 'Technology', 'Teen', 'Teenager', 'Telephone',
    'Telescope', 'Television', 'Tell', 'Temperature', 'Temporary',
    'Ten', 'Tend', 'Tendency', 'Tennis', 'Tension', 'Tent', 'Term',
    'Terms', 'Terrain', 'Terrible', 'Territory', 'Terror', 'Terrorism',
    'Terrorist', 'Test', 'Testify', 'Testimony', 'Testing', 'Text',
    'Than', 'Thank', 'Thanks', 'That', 'The', 'Theater', 'Their',
    'Them', 'Theme', 'Themselves', 'Then', 'Theology', 'Theory',
    'Therapy', 'There', 'Therefore', 'These', 'They', 'Thick',
    'Thin', 'Thing', 'Think', 'Thinking', 'Third', 'Thirty', 'This',
    'Those', 'Though', 'Thought', 'Thousand', 'Threat', 'Threaten',
    'Three', 'Throat', 'Through', 'Throughout', 'Throw', 'Thus',
    'Ticket', 'Tie', 'Tight', 'Time', 'Tiny', 'Tip', 'Tire', 'Tired',
    'Tissue', 'Title', 'To', 'Tobacco', 'Today', 'Toe', 'Together',
    'Toilet', 'Tolerance', 'Tolerate', 'Tomato', 'Tomorrow', 'Tone',
    'Tongue', 'Tonight', 'Too', 'Tool', 'Top', 'Topic', 'Toss',
    'Total', 'Totally', 'Touch', 'Tough', 'Tour', 'Tourist',
    'Tournament', 'Toward', 'Towards', 'Tower', 'Town', 'Toy',
    'Trace', 'Track', 'Trade', 'Trading', 'Tradition', 'Traditional',
    'Traffic', 'Tragedy', 'Trail', 'Train', 'Training', 'Trait',
    'Transaction', 'Transfer', 'Transform', 'Transformation',
    'Transition', 'Translate', 'Translation', 'Transmission', 'Transport',
    'Transportation', 'Trap', 'Travel', 'Traveler', 'Treat', 'Treatment',
    'Treaty', 'Tree', 'Tremendous', 'Trend', 'Trial', 'Tribe',
    'Trick', 'Trip', 'Triumph', 'Troop', 'Tropical', 'Trouble', 'Truck',
    'True', 'Truly', 'Trust', 'Truth', 'Try', 'Tube', 'Tunnel',
    'Turn', 'TV', 'Twelve', 'Twenty', 'Twice', 'Twin', 'Two', 'Type',
    'Typical', 'Typically', 'Ugly', 'Uh', 'Ultimate', 'Ultimately',
    'Unable', 'Uncle', 'Under', 'Undergo', 'Understand',
    'Understanding', 'Unfortunately', 'Unhappy', 'Uniform', 'Union',
    'Unique', 'Unit', 'United', 'Universal', 'Universe', 'University',
    'Unknown', 'Unless', 'Unlike', 'Unlikely', 'Until', 'Unusual',
    'Up', 'Upon', 'Upper', 'Upset', 'Urban', 'Urge', 'Us', 'Use',
    'Used', 'Useful', 'User', 'Usual', 'Usually', 'Utility', 'Vacation',
    'Vaccine', 'Vacuum', 'Valid', 'Validity', 'Valley', 'Valuable',
    'Value', 'Van', 'Variable', 'Variation', 'Variety', 'Various',
    'Vary', 'Vast', 'Vegetable', 'Vehicle', 'Venture', 'Version',
    'Versus', 'Very', 'Vessel', 'Veteran', 'Via', 'Victim', 'Victory',
    'Video', 'View', 'Viewer', 'Village', 'Violate', 'Violation',
    'Violence', 'Violent', 'Virtual', 'Virtually', 'Virtue', 'Virus',
    'Visible', 'Vision', 'Visit', 'Visitor', 'Visual', 'Vital',
    'Voice', 'Volume', 'Volunteer', 'Vote', 'Voter', 'Vs', 'Vulnerable',
    'Wage', 'Wait', 'Wake', 'Walk', 'Wall', 'Wander', 'Want', 'War',
    'Warm', 'Warn', 'Warning', 'Wash', 'Waste', 'Watch', 'Water',
    'Wave', 'Way', 'We', 'Weak', 'Weaken', 'Wealth', 'Wealthy',
    'Weapon', 'Wear', 'Weather', 'Web', 'Wedding', 'Week', 'Weekend',
    'Weekly', 'Weigh', 'Weight', 'Weird', 'Welcome', 'Welfare',
    'Well', 'West', 'Western', 'Wet', 'What', 'Whatever', 'Wheel',
    'When', 'Whenever', 'Where', 'Whereas', 'Whether', 'Which',
    'While', 'Whisper', 'White', 'Who', 'Whole', 'Whom', 'Whose',
    'Why', 'Wide', 'Widely', 'Widespread', 'Wife', 'Wild', 'Will',
    'Willing', 'Win', 'Wind', 'Window', 'Wine', 'Wing', 'Winner',
    'Winter', 'Wipe', 'Wire', 'Wisdom', 'Wise', 'Wish', 'With',
    'Withdraw', 'Within', 'Without', 'Witness', 'Woman', 'Wonder',
    'Wonderful', 'Wood', 'Wooden', 'Word', 'Work', 'Worker', 'Working',
    'Works', 'Workshop', 'World', 'Worry', 'Worth', 'Would', 'Wound',
    'Wow', 'Wrap', 'Write', 'Writer', 'Writing', 'Written', 'Wrong',
    'Yard', 'Yeah', 'Year', 'Yell', 'Yellow', 'Yes', 'Yesterday',
    'Yet', 'Yield', 'You', 'Young', 'Your', 'Yourself', 'Youth',
    'Zone',
}

def is_junk(term):
    if len(term) < 2 or len(term) > 30:
        return True
    if term in GENERIC_WORDS:
        return True
    # Skip numbers/stats/dates
    if re.match(r'^\d', term):
        return True
    if re.search(r'[/%]', term):
        return True
    if re.match(r'^\d{4}年', term):
        return True
    # Skip file refs
    if 'View/' in term or 'Actual title' in term:
        return True
    # Skip Western names
    parts = term.split()
    if len(parts) == 2 and parts[0] in COMMON_FIRST_NAMES and parts[1] in COMMON_LAST_NAMES:
        return True
    if term in COMMON_FIRST_NAMES or term in COMMON_LAST_NAMES:
        return True
    # Skip institutions
    if term in INSTITUTIONS:
        return True
    # Skip long Chinese phrases that are likely sentences
    if len(term) > 18 and re.search(r'[\u4e00-\u9fff]', term):
        return True
    # Skip Chinese phrases with obvious sentence structure
    if len(term) > 12 and any(c in term for c in ['的', '了', '是', '在', '与', '和']):
        # But keep well-known technical compounds
        pass  # let through for now, we'll filter more below
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
    """Check if term or obvious variants exist anywhere in files (for orphan detection)."""
    variants = [term]
    # Add some common variants
    if term == 'DDD':
        variants.extend(['领域驱动设计'])
    elif term == 'Paxos':
        variants.extend(['Paxos'])
    elif term == 'Rust':
        variants.extend(['Rust'])
    elif term == 'Side-Channel':
        variants.extend(['侧信道'])
    elif term == 'λ演算':
        variants.extend(['λ演算', 'lambda演算'])
    elif term == '共识算法':
        variants.extend(['共识'])
    elif term == '分布式事务':
        variants.extend(['分布式事务', '2PC', 'Saga', 'TCC'])
    elif term == '系统动力学':
        variants.extend(['系统动力学'])
    
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
    
    # Orphan check: term in index but not found anywhere in files (even as plain text)
    orphan_terms = []
    for term in existing_terms:
        if not term_exists_in_files(term, file_texts):
            orphan_terms.append(term)
    print(f"Orphan terms (in index but not in files): {len(orphan_terms)} ({orphan_terms})")
    
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
    
    report_path = Path("E:/_src/formal-architecture/terminology_audit_report_v3.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Report saved to {report_path}")
    
    for item in missing_details[:50]:
        print(f"- {item['term']} | {item['definition'][:60]} | {item['module']} | {item['file']}")
    if len(missing_details) > 50:
        print(f"... and {len(missing_details) - 50} more")

if __name__ == "__main__":
    main()
