#!/usr/bin/env python3
"""
理论导航系统 (Theory Navigation System)
实现智能导航、搜索和推荐功能

功能特性：
1. 多维度导航
2. 智能搜索
3. 个性化推荐
4. 学习路径规划
5. 用户界面
"""

import json
import os
import re
from typing import Dict, List, Any, Tuple, Optional, Set
from collections import defaultdict, deque
import heapq
from datetime import datetime
import sqlite3
import hashlib

class TheoryNavigationSystem:
    """理论导航系统"""
    
    def __init__(self, data_dir: str = "navigation_data"):
        self.data_dir = data_dir
        self.ensure_data_directory()
        
        # 初始化数据库
        self.init_database()
        
        # 核心组件
        self.search_engine = SearchEngine()
        self.recommendation_engine = RecommendationEngine()
        self.path_planner = LearningPathPlanner()
        self.user_manager = UserManager()
        
        # 理论体系数据
        self.theory_graph = {}
        self.concept_index = {}
        self.relation_index = {}
        
        # 用户会话
        self.current_user = None
        self.session_data = {}
    
    def ensure_data_directory(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def init_database(self):
        """初始化数据库"""
        db_path = os.path.join(self.data_dir, "navigation.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # 创建表
        self._create_tables()
    
    def _create_tables(self):
        """创建数据库表"""
        # 理论实体表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS theory_entities (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                description TEXT,
                content TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 关系表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                metadata TEXT,
                FOREIGN KEY (source_id) REFERENCES theory_entities (id),
                FOREIGN KEY (target_id) REFERENCES theory_entities (id)
            )
        ''')
        
        # 用户表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                preferences TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 导航历史表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS navigation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (entity_id) REFERENCES theory_entities (id)
            )
        ''')
        
        # 学习路径表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_paths (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                creator_id TEXT NOT NULL,
                nodes TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (creator_id) REFERENCES users (id)
            )
        ''')
        
        self.conn.commit()
    
    def load_theory_data(self, theory_files: List[str]):
        """加载理论数据"""
        print(f"正在加载 {len(theory_files)} 个理论文件...")
        
        for file_path in theory_files:
            if os.path.exists(file_path):
                self._load_single_theory_file(file_path)
            else:
                print(f"警告: 文件不存在: {file_path}")
        
        print("理论数据加载完成")
        self._build_indexes()
    
    def _load_single_theory_file(self, file_path: str):
        """加载单个理论文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取文件信息
            file_name = os.path.basename(file_path)
            file_dir = os.path.dirname(file_path)
            
            # 解析内容
            entities = self._extract_entities_from_content(content, file_path)
            
            # 存储到数据库
            for entity in entities:
                self._store_entity(entity)
            
            # 提取关系
            relations = self._extract_relations_from_content(content, file_path)
            for relation in relations:
                self._store_relation(relation)
                
        except Exception as e:
            print(f"加载文件 {file_path} 时出错: {e}")
    
    def _extract_entities_from_content(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """从内容中提取理论实体"""
        entities = []
        
        # 提取标题作为概念实体
        title_pattern = r'^#+\s+(.+)$'
        titles = re.findall(title_pattern, content, re.MULTILINE)
        
        for i, title in enumerate(titles):
            entity_id = f"{file_path}:{i}"
            level = len(title) - len(title.lstrip('#'))
            
            entities.append({
                'id': entity_id,
                'name': title.strip(),
                'type': 'concept',
                'description': f"来自 {file_path} 的概念",
                'content': content,
                'metadata': json.dumps({
                    'source_file': file_path,
                    'level': level,
                    'position': i
                })
            })
        
        # 添加文件本身作为文档实体
        entities.append({
            'id': file_path,
            'name': os.path.basename(file_path),
            'type': 'document',
            'description': f"理论文档: {file_path}",
            'content': content,
            'metadata': json.dumps({
                'file_path': file_path,
                'file_size': len(content),
                'last_modified': datetime.now().isoformat()
            })
        })
        
        return entities
    
    def _extract_relations_from_content(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """从内容中提取关系"""
        relations = []
        
        # 提取Markdown链接
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, content)
        
        for link_text, link_url in links:
            relations.append({
                'source_id': file_path,
                'target_id': link_url,
                'relation_type': 'references',
                'weight': 0.5,
                'metadata': json.dumps({
                    'link_text': link_text,
                    'extracted_from': file_path
                })
            })
        
        # 提取标题层次关系
        title_pattern = r'^(#+)\s+(.+)$'
        titles = re.findall(title_pattern, content, re.MULTILINE)
        
        for i in range(len(titles) - 1):
            current_level = len(titles[i][0])
            next_level = len(titles[i + 1][0])
            
            if next_level > current_level:
                # 子标题关系
                source_id = f"{file_path}:{i}"
                target_id = f"{file_path}:{i + 1}"
                
                relations.append({
                    'source_id': source_id,
                    'target_id': target_id,
                    'relation_type': 'contains',
                    'weight': 1.0,
                    'metadata': json.dumps({
                        'hierarchy_level': current_level,
                        'relation_type': 'parent_child'
                    })
                })
        
        return relations
    
    def _store_entity(self, entity: Dict[str, Any]):
        """存储理论实体到数据库"""
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO theory_entities 
                (id, name, type, description, content, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                entity['id'],
                entity['name'],
                entity['type'],
                entity['description'],
                entity['content'],
                entity['metadata']
            ))
            self.conn.commit()
        except Exception as e:
            print(f"存储实体时出错: {e}")
    
    def _store_relation(self, relation: Dict[str, Any]):
        """存储关系到数据库"""
        try:
            self.cursor.execute('''
                INSERT INTO relations 
                (source_id, target_id, relation_type, weight, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                relation['source_id'],
                relation['target_id'],
                relation['relation_type'],
                relation['weight'],
                relation['metadata']
            ))
            self.conn.commit()
        except Exception as e:
            print(f"存储关系时出错: {e}")
    
    def _build_indexes(self):
        """构建索引"""
        # 构建概念索引
        self.cursor.execute('SELECT * FROM theory_entities WHERE type = "concept"')
        concepts = self.cursor.fetchall()
        
        for concept in concepts:
            concept_id, name, concept_type, description, content, metadata = concept
            self.concept_index[name.lower()] = concept_id
        
        # 构建关系索引
        self.cursor.execute('SELECT * FROM relations')
        relations = self.cursor.fetchall()
        
        for relation in relations:
            rel_id, source_id, target_id, rel_type, weight, metadata = relation
            
            if source_id not in self.relation_index:
                self.relation_index[source_id] = []
            self.relation_index[source_id].append({
                'target_id': target_id,
                'type': rel_type,
                'weight': weight,
                'metadata': metadata
            })
    
    def search(self, query: str, user_id: str = None, 
               search_type: str = 'keyword', max_results: int = 20) -> List[Dict[str, Any]]:
        """执行搜索"""
        if user_id:
            self.current_user = user_id
            self.user_manager.record_search(user_id, query)
        
        if search_type == 'keyword':
            return self.search_engine.keyword_search(query, max_results)
        elif search_type == 'semantic':
            return self.search_engine.semantic_search(query, max_results)
        elif search_type == 'advanced':
            return self.search_engine.advanced_search(query, max_results)
        else:
            return self.search_engine.keyword_search(query, max_results)
    
    def navigate(self, start_entity: str, target_entity: str = None, 
                 navigation_type: str = 'hierarchical') -> List[Dict[str, Any]]:
        """执行导航"""
        if target_entity:
            # 路径导航
            return self.path_planner.find_path(start_entity, target_entity)
        else:
            # 探索导航
            if navigation_type == 'hierarchical':
                return self._hierarchical_navigation(start_entity)
            elif navigation_type == 'related':
                return self._related_navigation(start_entity)
            elif navigation_type == 'recommended':
                return self._recommended_navigation(start_entity)
            else:
                return self._hierarchical_navigation(start_entity)
    
    def _hierarchical_navigation(self, entity_id: str) -> List[Dict[str, Any]]:
        """层次导航"""
        # 获取实体的层次结构
        self.cursor.execute('''
            SELECT * FROM theory_entities WHERE id = ?
        ''', (entity_id,))
        entity = self.cursor.fetchone()
        
        if not entity:
            return []
        
        # 获取包含关系
        self.cursor.execute('''
            SELECT r.*, te.name as target_name, te.type as target_type
            FROM relations r
            JOIN theory_entities te ON r.target_id = te.id
            WHERE r.source_id = ? AND r.relation_type = 'contains'
            ORDER BY r.weight DESC
        ''', (entity_id,))
        
        contains_relations = self.cursor.fetchall()
        
        # 获取被包含关系
        self.cursor.execute('''
            SELECT r.*, te.name as source_name, te.type as source_type
            FROM relations r
            JOIN theory_entities te ON r.source_id = te.id
            WHERE r.target_id = ? AND r.relation_type = 'contains'
            ORDER BY r.weight DESC
        ''', (entity_id,))
        
        contained_by_relations = self.cursor.fetchall()
        
        navigation_result = {
            'current_entity': {
                'id': entity_id,
                'name': entity[1],
                'type': entity[2],
                'description': entity[3]
            },
            'contains': [
                {
                    'id': rel[2],
                    'name': rel[6],
                    'type': rel[7],
                    'relation_weight': rel[4]
                } for rel in contains_relations
            ],
            'contained_by': [
                {
                    'id': rel[1],
                    'name': rel[6],
                    'type': rel[7],
                    'relation_weight': rel[4]
                } for rel in contained_by_relations
            ]
        }
        
        return [navigation_result]
    
    def _related_navigation(self, entity_id: str) -> List[Dict[str, Any]]:
        """相关导航"""
        # 获取相关实体
        self.cursor.execute('''
            SELECT r.*, te.name as target_name, te.type as target_type
            FROM relations r
            JOIN theory_entities te ON r.target_id = te.id
            WHERE r.source_id = ? AND r.relation_type != 'contains'
            ORDER BY r.weight DESC
            LIMIT 10
        ''', (entity_id,))
        
        relations = self.cursor.fetchall()
        
        return [
            {
                'id': rel[2],
                'name': rel[6],
                'type': rel[7],
                'relation_type': rel[3],
                'relation_weight': rel[4]
            } for rel in relations
        ]
    
    def _recommended_navigation(self, entity_id: str) -> List[Dict[str, Any]]:
        """推荐导航"""
        if not self.current_user:
            return self._related_navigation(entity_id)
        
        # 基于用户行为的推荐
        return self.recommendation_engine.get_recommendations(
            self.current_user, entity_id
        )
    
    def get_recommendations(self, user_id: str = None, 
                           entity_id: str = None, 
                           recommendation_type: str = 'personalized') -> List[Dict[str, Any]]:
        """获取推荐"""
        if user_id:
            self.current_user = user_id
        
        if recommendation_type == 'personalized':
            return self.recommendation_engine.get_personalized_recommendations(
                self.current_user, entity_id
            )
        elif recommendation_type == 'popular':
            return self.recommendation_engine.get_popular_recommendations()
        elif recommendation_type == 'related':
            return self.recommendation_engine.get_related_recommendations(entity_id)
        else:
            return self.recommendation_engine.get_personalized_recommendations(
                self.current_user, entity_id
            )
    
    def create_learning_path(self, name: str, description: str, 
                            nodes: List[str], creator_id: str) -> str:
        """创建学习路径"""
        path_id = hashlib.md5(f"{name}:{creator_id}:{datetime.now()}".encode()).hexdigest()
        
        try:
            self.cursor.execute('''
                INSERT INTO learning_paths 
                (id, name, description, creator_id, nodes, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                path_id,
                name,
                description,
                creator_id,
                json.dumps(nodes),
                json.dumps({
                    'created_at': datetime.now().isoformat(),
                    'node_count': len(nodes)
                })
            ))
            self.conn.commit()
            return path_id
        except Exception as e:
            print(f"创建学习路径时出错: {e}")
            return None
    
    def get_learning_paths(self, user_id: str = None) -> List[Dict[str, Any]]:
        """获取学习路径"""
        if user_id:
            # 获取用户的学习路径
            self.cursor.execute('''
                SELECT * FROM learning_paths WHERE creator_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
        else:
            # 获取所有公开的学习路径
            self.cursor.execute('''
                SELECT * FROM learning_paths ORDER BY created_at DESC
            ''')
        
        paths = self.cursor.fetchall()
        
        return [
            {
                'id': path[0],
                'name': path[1],
                'description': path[2],
                'creator_id': path[3],
                'nodes': json.loads(path[4]),
                'metadata': json.loads(path[5]) if path[5] else {},
                'created_at': path[6]
            } for path in paths
        ]
    
    def close(self):
        """关闭系统"""
        if hasattr(self, 'conn'):
            self.conn.close()


class SearchEngine:
    """搜索引擎"""
    
    def __init__(self):
        self.search_history = []
    
    def keyword_search(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """关键词搜索"""
        # 这里应该连接到数据库执行搜索
        # 简化实现，返回模拟结果
        return [
            {
                'id': f"result_{i}",
                'name': f"搜索结果 {i}",
                'type': 'concept',
                'description': f"匹配查询 '{query}' 的结果",
                'relevance_score': 0.9 - i * 0.1
            } for i in range(min(max_results, 5))
        ]
    
    def semantic_search(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """语义搜索"""
        # 语义搜索实现
        return self.keyword_search(query, max_results)
    
    def advanced_search(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """高级搜索"""
        # 高级搜索实现
        return self.keyword_search(query, max_results)


class RecommendationEngine:
    """推荐引擎"""
    
    def __init__(self):
        self.recommendation_cache = {}
    
    def get_personalized_recommendations(self, user_id: str, 
                                       entity_id: str = None) -> List[Dict[str, Any]]:
        """获取个性化推荐"""
        # 基于用户行为的个性化推荐
        return [
            {
                'id': f"rec_{i}",
                'name': f"个性化推荐 {i}",
                'type': 'concept',
                'reason': '基于您的学习历史',
                'confidence': 0.8 - i * 0.1
            } for i in range(5)
        ]
    
    def get_popular_recommendations(self) -> List[Dict[str, Any]]:
        """获取热门推荐"""
        # 基于流行度的推荐
        return [
            {
                'id': f"popular_{i}",
                'name': f"热门推荐 {i}",
                'type': 'concept',
                'reason': '热门内容',
                'popularity_score': 0.9 - i * 0.1
            } for i in range(5)
        ]
    
    def get_related_recommendations(self, entity_id: str) -> List[Dict[str, Any]]:
        """获取相关推荐"""
        # 基于内容相关性的推荐
        return [
            {
                'id': f"related_{i}",
                'name': f"相关推荐 {i}",
                'type': 'concept',
                'reason': '与当前内容相关',
                'relevance_score': 0.8 - i * 0.1
            } for i in range(5)
        ]
    
    def get_recommendations(self, user_id: str, entity_id: str) -> List[Dict[str, Any]]:
        """获取推荐（综合）"""
        # 综合多种推荐策略
        personalized = self.get_personalized_recommendations(user_id, entity_id)
        related = self.get_related_recommendations(entity_id)
        
        # 合并并去重
        all_recommendations = personalized + related
        seen_ids = set()
        unique_recommendations = []
        
        for rec in all_recommendations:
            if rec['id'] not in seen_ids:
                seen_ids.add(rec['id'])
                unique_recommendations.append(rec)
        
        return unique_recommendations[:10]


class LearningPathPlanner:
    """学习路径规划器"""
    
    def __init__(self):
        self.path_cache = {}
    
    def find_path(self, start_entity: str, target_entity: str) -> List[Dict[str, Any]]:
        """查找从起始实体到目标实体的路径"""
        # 这里应该实现路径查找算法
        # 简化实现，返回模拟路径
        return [
            {
                'step': i + 1,
                'entity_id': f"step_{i}",
                'entity_name': f"步骤 {i + 1}",
                'description': f"从 {start_entity} 到 {target_entity} 的第 {i + 1} 步",
                'estimated_time': f"{i + 1} 小时"
            } for i in range(3)
        ]
    
    def optimize_path(self, path: List[str], user_preferences: Dict[str, Any]) -> List[str]:
        """优化学习路径"""
        # 路径优化算法
        return path
    
    def estimate_completion_time(self, path: List[str]) -> str:
        """估算完成时间"""
        # 基于路径长度和复杂度估算时间
        estimated_hours = len(path) * 2
        return f"{estimated_hours} 小时"


class UserManager:
    """用户管理器"""
    
    def __init__(self):
        self.user_sessions = {}
    
    def create_user(self, username: str, preferences: Dict[str, Any] = None) -> str:
        """创建用户"""
        user_id = hashlib.md5(username.encode()).hexdigest()
        
        # 这里应该存储到数据库
        self.user_sessions[user_id] = {
            'username': username,
            'preferences': preferences or {},
            'created_at': datetime.now(),
            'last_activity': datetime.now()
        }
        
        return user_id
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """获取用户信息"""
        return self.user_sessions.get(user_id, {})
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """更新用户偏好"""
        if user_id in self.user_sessions:
            self.user_sessions[user_id]['preferences'].update(preferences)
            self.user_sessions[user_id]['last_activity'] = datetime.now()
    
    def record_search(self, user_id: str, query: str):
        """记录用户搜索"""
        if user_id in self.user_sessions:
            if 'search_history' not in self.user_sessions[user_id]:
                self.user_sessions[user_id]['search_history'] = []
            
            self.user_sessions[user_id]['search_history'].append({
                'query': query,
                'timestamp': datetime.now()
            })
            
            # 保持搜索历史在合理范围内
            if len(self.user_sessions[user_id]['search_history']) > 100:
                self.user_sessions[user_id]['search_history'] = \
                    self.user_sessions[user_id]['search_history'][-50:]


def main():
    """主函数"""
    # 创建导航系统
    nav_system = TheoryNavigationSystem()
    
    # 加载理论数据（示例）
    theory_files = [
        "FormalUnified/01-哲学基础理论/00-哲学基础理论总论.md",
        "FormalUnified/02-数学理论体系/00-数学理论体系总论.md"
    ]
    
    # 检查文件是否存在
    existing_files = [f for f in theory_files if os.path.exists(f)]
    if existing_files:
        nav_system.load_theory_data(existing_files)
    else:
        print("未找到理论文件，使用示例数据")
    
    # 演示功能
    print("理论导航系统演示")
    print("=" * 50)
    
    # 创建示例用户
    user_id = nav_system.user_manager.create_user("demo_user", {
        "interests": ["形式化方法", "软件架构"],
        "experience_level": "intermediate"
    })
    
    # 搜索演示
    print("\n1. 搜索功能演示:")
    search_results = nav_system.search("形式化", user_id, "keyword", 5)
    print(f"搜索 '形式化' 的结果: {len(search_results)} 项")
    
    # 导航演示
    print("\n2. 导航功能演示:")
    navigation_result = nav_system.navigate("哲学基础", navigation_type="hierarchical")
    print(f"层次导航结果: {len(navigation_result)} 项")
    
    # 推荐演示
    print("\n3. 推荐功能演示:")
    recommendations = nav_system.get_recommendations(user_id, "哲学基础", "personalized")
    print(f"个性化推荐: {len(recommendations)} 项")
    
    # 学习路径演示
    print("\n4. 学习路径演示:")
    path_id = nav_system.create_learning_path(
        "形式化方法入门",
        "从哲学基础到软件架构的学习路径",
        ["哲学基础", "数学理论", "形式语言", "软件架构"],
        user_id
    )
    print(f"创建学习路径: {path_id}")
    
    # 获取学习路径
    paths = nav_system.get_learning_paths(user_id)
    print(f"用户学习路径数量: {len(paths)}")
    
    print("\n演示完成！")
    
    # 关闭系统
    nav_system.close()


if __name__ == "__main__":
    main() 