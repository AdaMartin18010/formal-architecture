# 实用拜占庭容错 (Practical Byzantine Fault Tolerance, PBFT)

## 目录

- [实用拜占庭容错 (Practical Byzantine Fault Tolerance, PBFT)](#实用拜占庭容错-practical-byzantine-fault-tolerance-pbft)
  - [目录](#目录)
  - [1. 核心概念](#1-核心概念)
    - [1.1 核心思想](#11-核心思想)
    - [1.2 共识协议流程](#12-共识协议流程)
    - [1.3 视图更换 (View Change)](#13-视图更换-view-change)
    - [1.4 优缺点](#14-优缺点)
      - [优点](#优点)
      - [缺点](#缺点)
  - [2. Rust 实现示例](#2-rust-实现示例)

## 1. 核心概念

PBFT (Practical Byzantine Fault Tolerance) 是由 Castro 和 Liskov 于1999年提出的一种经典的拜占庭容错（BFT）共识算法。它主要设计用于**许可制系统 (permissioned systems)**，如联盟链或其他需要高确定性和低延迟的分布式环境中。

### 1.1 核心思想

该算法旨在解决"拜占庭将军问题"，即在一个可能存在恶意或故障节点（拜占庭节点）的分布式网络中，如何让所有诚实的节点对信息达成一致。

PBFT 的核心假设是：**网络中恶意或故障的节点总数 `f` 不超过总节点数 `n` 的三分之一，即 `n >= 3f + 1`**。

它通过一个三阶段的协议来确保所有诚实节点对请求的顺序和执行结果达成一致，从而保证系统的安全性和活性。

### 1.2 共识协议流程

PBFT 的共识达成涉及一个主节点（Primary）和多个备份节点（Backups）。客户端的请求首先发送给主节点，然后由主节点发起三阶段的共识流程。

1. **预准备 (Pre-Prepare)**
    - 主节点接收客户端请求，验证其有效性，为其分配一个序列号 `n`，然后构建一个"预准备"消息。
    - 该消息包含 `<PRE-PREPARE, v, n, d>`，其中 `v` 是视图编号，`n` 是序列号，`d` 是请求内容的摘要。
    - 主节点将此消息广播给所有备份节点。

2. **准备 (Prepare)**
    - 备份节点收到"预准备"消息后，会进行一系列验证：消息签名、视图编号 `v` 是否正确、序列号 `n` 是否在合法范围内、是否已处理过相同 `v` 和 `n` 的其他请求。
    - 验证通过后，该备份节点会向网络中的所有其他节点（包括主节点）广播一个"准备"消息，格式为 `<PREPARE, v, n, d, i>`，其中 `i` 是该备份节点的ID。
    - 同时，该节点将预准备消息和准备消息都记录到本地日志中。

3. **确认 (Commit)**
    - 当任何一个节点（无论是主节点还是备份节点）收到 `2f` 个来自不同节点的、与其本地日志中预准备消息相匹配的"准备"消息后，该节点就进入"已准备就绪"（prepared）状态。这证明了网络中的多数诚实节点就请求的顺序（`v` 和 `n`）达成了一致。
    - 进入"已准备就绪"状态后，该节点会向所有其他节点广播一个"确认"消息，格式为 `<COMMIT, v, n, d, i>`。
    - "确认"消息是节点对请求顺序和内容的最终承诺。

4. **执行与回复 (Execute & Reply)**
    - 当任何一个节点收到 `2f + 1` 个（包括自己）来自不同节点的、内容一致的"确认"消息后，它就认为该请求已在整个网络中达成了明确共识。
    - 该节点会在本地执行客户端的请求（例如，更新状态机），并将执行结果直接回复给客户端。
    - 由于客户端可能会收到来自多个节点的相同回复，它只需要等待 `f + 1` 个相同的回复即可确认操作已成功完成。

### 1.3 视图更换 (View Change)

如果主节点作恶（例如，不发送预准备消息、发送无效消息）或崩溃，备份节点会通过超时机制检测到。当一个备份节点在预设时间内没有收到主节点的有效消息，它会触发"视图更换"协议，选举出新的主节点，确保系统的活性。

### 1.4 优缺点

#### 优点

- **高确定性 (Finality)**：一旦请求被确认，就不会被推翻或分叉（除非拜占庭节点超过阈值）。
- **低延迟**：相比于工作量证明（PoW）等概率性共识，PBFT 的共识周期非常快。
- **节能**：不涉及大规模的哈希计算，资源消耗低。

#### 缺点

- **通信开销大**：每一轮共识都需要节点间进行多对多的广播，消息复杂度为 O(n²)，其中 n 是节点总数。
- **可扩展性有限**：由于通信开销大，PBFT 通常只适用于节点数量较少（几十到几百个）的场景。
- **许可环境**：需要预先知道所有参与共识节点的身份，并建立点对点的通信信道，不适用于节点可自由加入和退出的匿名公有链环境。

---

## 2. Rust 实现示例

下面展示一个简化的PBFT共识算法的Rust实现骨架，用于说明其核心数据结构和状态转换逻辑。

```rust
use std::collections::{HashMap, HashSet};
use std::time::{Duration, Instant};

// 节点ID类型
type NodeId = String;
// 消息哈希类型
type MessageHash = Vec<u8>;
// 区块哈希类型
type BlockHash = Vec<u8>;
// 签名类型
type Signature = Vec<u8>;

// PBFT状态机状态
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
enum PbftPhase {
    Idle,       // 等待 Pre-Prepare
    PrePrepared, // 已收到 Pre-Prepare，广播了 Prepare
    Prepared,   // 已收到 2f+1 个 Prepare，广播了 Commit
    Committed,  // 已收到 2f+1 个 Commit，可以执行
}

// PBFT消息类型
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
enum MessageType {
    PrePrepare,
    Prepare,
    Commit,
    ViewChange,
    NewView,
}

// PBFT消息
#[derive(Debug, Clone)]
struct PbftMessage {
    msg_type: MessageType,
    view: u64,
    sequence: u64,
    digest: BlockHash,
    sender: NodeId,
    signature: Signature,
}

// 视图变更消息
#[derive(Debug, Clone)]
struct ViewChangeMessage {
    new_view: u64,
    sequence: u64,
    prepared_messages: Vec<PbftMessage>,
    sender: NodeId,
    signature: Signature,
}

// 新视图消息
#[derive(Debug, Clone)]
struct NewViewMessage {
    new_view: u64,
    view_change_messages: Vec<ViewChangeMessage>,
    new_pre_prepares: Vec<PbftMessage>,
    sender: NodeId,
    signature: Signature,
}

// 区块数据
#[derive(Debug, Clone)]
struct Block {
    sequence: u64,
    data: Vec<u8>,
    previous_hash: BlockHash,
    hash: BlockHash,
}

// 用于存储每个共识实例的日志
struct ConsensusInstanceLog {
    phase: PbftPhase,
    pre_prepare: Option<PbftMessage>,
    prepares: HashMap<NodeId, PbftMessage>,
    commits: HashMap<NodeId, PbftMessage>,
}

impl ConsensusInstanceLog {
    fn new() -> Self {
        Self {
            phase: PbftPhase::Idle,
            pre_prepare: None,
            prepares: HashMap::new(),
            commits: HashMap::new(),
        }
    }
}

// PBFT共识实现
struct PbftConsensus {
    node_id: NodeId,
    view: u64,
    sequence: u64,
    nodes: Vec<NodeId>,
    // 日志，键为序列号
    message_log: HashMap<u64, ConsensusInstanceLog>,
    committed_blocks: Vec<Block>,
    view_change_timer: Option<Instant>,
    view_change_timeout: Duration,
    view_change_messages: HashMap<u64, Vec<ViewChangeMessage>>,
    // 容错能力 f
    f: usize,
}

impl PbftConsensus {
    fn new(node_id: NodeId, nodes: Vec<NodeId>) -> Self {
        let n = nodes.len();
        // f = (n - 1) / 3
        let f = (n - 1) / 3;
        
        PbftConsensus {
            node_id,
            view: 0,
            sequence: 0,
            nodes,
            message_log: HashMap::new(),
            committed_blocks: Vec::new(),
            view_change_timer: None,
            view_change_timeout: Duration::from_secs(5),
            view_change_messages: HashMap::new(),
            f,
        }
    }

    fn primary_node_id(&self) -> &NodeId {
        &self.nodes[(self.view as usize) % self.nodes.len()]
    }

    fn is_primary(&self) -> bool {
        self.node_id == *self.primary_node_id()
    }

    // 处理客户端请求 (仅主节点)
    fn handle_client_request(&mut self, block_data: Vec<u8>) {
        if !self.is_primary() {
            return;
        }
        
        self.sequence += 1;
        let digest = self.hash_data(&block_data); // 假设的哈希函数

        let pre_prepare_msg = PbftMessage {
            msg_type: MessageType::PrePrepare,
            view: self.view,
            sequence: self.sequence,
            digest,
            sender: self.node_id.clone(),
            signature: self.sign_message(&block_data), // 假设的签名函数
        };

        // 将 Pre-Prepare 存入日志
        let log = self.message_log.entry(self.sequence).or_insert_with(ConsensusInstanceLog::new);
        log.pre_prepare = Some(pre_prepare_msg.clone());
        log.phase = PbftPhase::PrePrepared;

        // 广播 Pre-Prepare
        self.broadcast(pre_prepare_msg);
        self.reset_view_change_timer();
    }
    
    // 处理收到的消息
    fn handle_message(&mut self, message: PbftMessage) {
        if !self.verify_signature(&message) || message.view < self.view {
            println!("消息验证失败或视图陈旧: {:?}", message.msg_type);
            return;
        }
        
        match message.msg_type {
            MessageType::PrePrepare => self.handle_pre_prepare(message),
            MessageType::Prepare => self.handle_prepare(message),
            MessageType::Commit => self.handle_commit(message),
            _ => println!("未处理的消息类型: {:?}", message.msg_type),
        }
    }
    
    fn handle_pre_prepare(&mut self, message: PbftMessage) {
        if self.is_primary() { return; } // 主节点不处理 Pre-Prepare
        
        // 验证... (来自主节点, 序列号等)
        
        let log = self.message_log.entry(message.sequence).or_insert_with(ConsensusInstanceLog::new);
        if log.phase != PbftPhase::Idle { return; }

        log.pre_prepare = Some(message.clone());
        
        let prepare_msg = PbftMessage {
            msg_type: MessageType::Prepare,
            view: message.view,
            sequence: message.sequence,
            digest: message.digest,
            sender: self.node_id.clone(),
            signature: self.sign_message(&[]), // 签名
        };

        log.phase = PbftPhase::PrePrepared;
        log.prepares.insert(self.node_id.clone(), prepare_msg.clone());

        self.broadcast(prepare_msg);
        self.reset_view_change_timer();
    }
    
    fn handle_prepare(&mut self, message: PbftMessage) {
        let log = self.message_log.entry(message.sequence).or_insert_with(ConsensusInstanceLog::new);
        if log.phase >= PbftPhase::Prepared { return; }

        // 验证... (摘要是否与 pre-prepare 匹配)
        if let Some(pre_prepare) = &log.pre_prepare {
            if pre_prepare.digest != message.digest { return; }
        } else {
             // 可能需要等待 Pre-Prepare
            return;
        }

        log.prepares.insert(message.sender.clone(), message.clone());

        // 检查是否达到 prepared 状态 (2f + 1 个 prepares, 包括自己的)
        if log.prepares.len() >= 2 * self.f + 1 {
            log.phase = PbftPhase::Prepared;
            
            let commit_msg = PbftMessage {
                msg_type: MessageType::Commit,
                view: message.view,
                sequence: message.sequence,
                digest: message.digest,
                sender: self.node_id.clone(),
                signature: self.sign_message(&[]),
            };

            log.commits.insert(self.node_id.clone(), commit_msg.clone());
            self.broadcast(commit_msg);
        }
    }
    
    fn handle_commit(&mut self, message: PbftMessage) {
        let log = self.message_log.entry(message.sequence).or_insert_with(ConsensusInstanceLog::new);
        if log.phase >= PbftPhase::Committed { return; }
        
        // 验证...

        log.commits.insert(message.sender.clone(), message);
        
        // 检查是否达到 committed 状态 (2f + 1 个 commits)
        if log.phase == PbftPhase::Prepared && log.commits.len() >= 2 * self.f + 1 {
            log.phase = PbftPhase::Committed;
            self.execute_request(log);
        }
    }

    fn execute_request(&mut self, instance_log: &ConsensusInstanceLog) {
        if let Some(pre_prepare) = &instance_log.pre_prepare {
             println!("节点 {} 在序列号 {} 上提交了请求: {:?}", self.node_id, pre_prepare.sequence, pre_prepare.digest);
             // 实际应用中这里会更新状态机
             // self.committed_blocks.push(...)
        }
    }
    
    // --- 辅助函数 ---
    fn broadcast(&self, message: PbftMessage) { /* 通过网络发送消息 */ }
    fn verify_signature(&self, message: &PbftMessage) -> bool { true }
    fn sign_message(&self, data: &[u8]) -> Signature { vec![] }
    fn hash_data(&self, data: &[u8]) -> BlockHash {vec![]}
    fn reset_view_change_timer(&mut self) {
        self.view_change_timer = Some(Instant::now());
    }
}
```
