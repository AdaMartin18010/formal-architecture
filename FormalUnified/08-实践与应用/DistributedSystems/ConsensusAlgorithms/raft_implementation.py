#!/usr/bin/env python3
"""
Raft共识算法实现
基于形式化架构理论的分布式系统实践案例

作者：形式化架构团队
日期：2024年12月
"""

import asyncio
import json
import logging
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
from uuid import uuid4

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NodeState(Enum):
    """节点状态枚举"""
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"

class LogEntry:
    """日志条目"""
    def __init__(self, term: int, index: int, command: str, data: dict):
        self.term = term
        self.index = index
        self.command = command
        self.data = data
    
    def to_dict(self):
        return {
            "term": self.term,
            "index": self.index,
            "command": self.command,
            "data": self.data
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["term"], data["index"], data["command"], data["data"])

@dataclass
class RaftNode:
    """Raft节点实现"""
    node_id: str
    peers: List[str]
    election_timeout: int = 150  # 毫秒
    heartbeat_interval: int = 50  # 毫秒
    
    # 持久化状态
    current_term: int = 0
    voted_for: Optional[str] = None
    log: List[LogEntry] = field(default_factory=list)
    
    # 易失性状态
    commit_index: int = 0
    last_applied: int = 0
    
    # 领导者状态
    next_index: Dict[str, int] = field(default_factory=dict)
    match_index: Dict[str, int] = field(default_factory=dict)
    
    # 运行时状态
    state: NodeState = NodeState.FOLLOWER
    leader_id: Optional[str] = None
    election_timer: Optional[asyncio.Task] = None
    heartbeat_timer: Optional[asyncio.Task] = None
    
    def __post_init__(self):
        # 初始化日志索引
        self.next_index = {peer: 1 for peer in self.peers}
        self.match_index = {peer: 0 for peer in self.peers}
    
    async def start(self):
        """启动节点"""
        logger.info(f"节点 {self.node_id} 启动，状态: {self.state.value}")
        await self.start_election_timer()
    
    async def start_election_timer(self):
        """启动选举定时器"""
        if self.election_timer:
            self.election_timer.cancel()
        
        timeout = random.randint(self.election_timeout, 2 * self.election_timeout)
        self.election_timer = asyncio.create_task(self.election_timeout_handler(timeout))
    
    async def election_timeout_handler(self, timeout: int):
        """选举超时处理器"""
        await asyncio.sleep(timeout / 1000.0)
        if self.state != NodeState.LEADER:
            await self.start_election()
    
    async def start_election(self):
        """开始领导者选举"""
        logger.info(f"节点 {self.node_id} 开始领导者选举")
        
        self.state = NodeState.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self.leader_id = None
        
        # 重置选举定时器
        await self.start_election_timer()
        
        # 发送投票请求
        votes_received = 1  # 自己投票给自己
        
        for peer in self.peers:
            if peer != self.node_id:
                try:
                    vote_granted = await self.request_vote(peer)
                    if vote_granted:
                        votes_received += 1
                except Exception as e:
                    logger.warning(f"向节点 {peer} 请求投票失败: {e}")
        
        # 检查是否获得多数票
        if votes_received > len(self.peers) // 2:
            await self.become_leader()
        else:
            # 选举失败，回到跟随者状态
            self.state = NodeState.FOLLOWER
            await self.start_election_timer()
    
    async def request_vote(self, peer: str) -> bool:
        """向其他节点请求投票"""
        # 模拟RPC调用
        request = {
            "type": "RequestVote",
            "term": self.current_term,
            "candidate_id": self.node_id,
            "last_log_index": len(self.log),
            "last_log_term": self.log[-1].term if self.log else 0
        }
        
        # 这里应该发送实际的RPC请求
        # 为了演示，我们模拟一个简单的响应
        await asyncio.sleep(0.01)  # 模拟网络延迟
        
        # 模拟投票结果（实际应该从peer获得）
        return random.choice([True, False])
    
    async def become_leader(self):
        """成为领导者"""
        logger.info(f"节点 {self.node_id} 成为领导者，任期: {self.current_term}")
        
        self.state = NodeState.LEADER
        self.leader_id = self.node_id
        
        # 初始化领导者状态
        for peer in self.peers:
            if peer != self.node_id:
                self.next_index[peer] = len(self.log) + 1
                self.match_index[peer] = 0
        
        # 取消选举定时器
        if self.election_timer:
            self.election_timer.cancel()
        
        # 开始发送心跳
        await self.start_heartbeat()
    
    async def start_heartbeat(self):
        """开始发送心跳"""
        while self.state == NodeState.LEADER:
            await self.send_heartbeat()
            await asyncio.sleep(self.heartbeat_interval / 1000.0)
    
    async def send_heartbeat(self):
        """发送心跳到所有跟随者"""
        for peer in self.peers:
            if peer != self.node_id:
                try:
                    await self.append_entries(peer, [], True)  # 空日志条目作为心跳
                except Exception as e:
                    logger.warning(f"向节点 {peer} 发送心跳失败: {e}")
    
    async def append_entries(self, peer: str, entries: List[LogEntry], is_heartbeat: bool = False) -> bool:
        """向跟随者追加日志条目"""
        # 模拟RPC调用
        request = {
            "type": "AppendEntries",
            "term": self.current_term,
            "leader_id": self.node_id,
            "prev_log_index": self.next_index[peer] - 1,
            "prev_log_term": self.log[self.next_index[peer] - 2].term if self.next_index[peer] > 1 else 0,
            "entries": [entry.to_dict() for entry in entries],
            "leader_commit": self.commit_index
        }
        
        # 模拟网络延迟
        await asyncio.sleep(0.01)
        
        # 模拟响应（实际应该从peer获得）
        success = random.choice([True, False])
        
        if success:
            if not is_heartbeat and entries:
                self.next_index[peer] += len(entries)
                self.match_index[peer] = self.next_index[peer] - 1
        else:
            # 日志不匹配，减少next_index
            if self.next_index[peer] > 1:
                self.next_index[peer] -= 1
        
        return success
    
    async def submit_command(self, command: str, data: dict) -> bool:
        """提交命令（仅领导者可用）"""
        if self.state != NodeState.LEADER:
            logger.warning(f"节点 {self.node_id} 不是领导者，无法提交命令")
            return False
        
        # 创建日志条目
        log_entry = LogEntry(
            term=self.current_term,
            index=len(self.log) + 1,
            command=command,
            data=data
        )
        
        # 添加到本地日志
        self.log.append(log_entry)
        
        # 复制到所有跟随者
        entries = [log_entry]
        for peer in self.peers:
            if peer != self.node_id:
                try:
                    await self.append_entries(peer, entries)
                except Exception as e:
                    logger.warning(f"向节点 {peer} 复制日志失败: {e}")
        
        # 尝试提交
        await self.try_commit()
        
        return True
    
    async def try_commit(self):
        """尝试提交日志条目"""
        for i in range(self.commit_index + 1, len(self.log) + 1):
            # 检查是否被多数节点复制
            replicated_count = 1  # 领导者自己
            for peer in self.peers:
                if peer != self.node_id and self.match_index[peer] >= i:
                    replicated_count += 1
            
            if replicated_count > len(self.peers) // 2:
                self.commit_index = i
                logger.info(f"日志条目 {i} 已提交")
    
    def get_log_summary(self) -> dict:
        """获取日志摘要"""
        return {
            "node_id": self.node_id,
            "state": self.state.value,
            "current_term": self.current_term,
            "commit_index": self.commit_index,
            "log_length": len(self.log),
            "leader_id": self.leader_id
        }

class RaftCluster:
    """Raft集群管理"""
    def __init__(self, node_count: int = 3):
        self.node_count = node_count
        self.nodes: Dict[str, RaftNode] = {}
        self.tasks: List[asyncio.Task] = []
    
    async def create_cluster(self):
        """创建集群"""
        # 创建节点ID
        node_ids = [f"node-{i}" for i in range(self.node_count)]
        
        # 创建节点
        for node_id in node_ids:
            peers = [nid for nid in node_ids if nid != node_id]
            node = RaftNode(node_id=node_id, peers=node_ids)
            self.nodes[node_id] = node
        
        # 启动所有节点
        for node in self.nodes.values():
            task = asyncio.create_task(node.start())
            self.tasks.append(task)
        
        logger.info(f"Raft集群已创建，包含 {self.node_count} 个节点")
    
    async def run_simulation(self, duration: int = 30):
        """运行集群模拟"""
        logger.info(f"开始运行集群模拟，持续时间: {duration} 秒")
        
        start_time = time.time()
        
        while time.time() - start_time < duration:
            # 随机选择一个节点提交命令
            if random.random() < 0.3:  # 30% 概率提交命令
                node_id = random.choice(list(self.nodes.keys()))
                node = self.nodes[node_id]
                
                if node.state == NodeState.LEADER:
                    command = f"command-{int(time.time())}"
                    data = {"timestamp": time.time(), "value": random.randint(1, 100)}
                    
                    success = await node.submit_command(command, data)
                    if success:
                        logger.info(f"节点 {node_id} 成功提交命令: {command}")
            
            # 打印集群状态
            if int(time.time() - start_time) % 5 == 0:  # 每5秒打印一次
                await self.print_cluster_status()
            
            await asyncio.sleep(1)
        
        # 停止所有节点
        await self.stop_cluster()
    
    async def print_cluster_status(self):
        """打印集群状态"""
        logger.info("=" * 50)
        logger.info("集群状态:")
        for node_id, node in self.nodes.items():
            status = node.get_log_summary()
            logger.info(f"  {node_id}: {status['state']} (任期: {status['current_term']}, 日志: {status['log_length']})")
        logger.info("=" * 50)
    
    async def stop_cluster(self):
        """停止集群"""
        logger.info("正在停止集群...")
        
        # 取消所有任务
        for task in self.tasks:
            task.cancel()
        
        # 等待任务完成
        await asyncio.gather(*self.tasks, return_exceptions=True)
        
        logger.info("集群已停止")

async def main():
    """主函数"""
    logger.info("启动Raft共识算法演示")
    
    # 创建集群
    cluster = RaftCluster(node_count=5)
    await cluster.create_cluster()
    
    # 运行模拟
    await cluster.run_simulation(duration=30)
    
    logger.info("演示完成")

if __name__ == "__main__":
    asyncio.run(main()) 