# TCP 协议：握手、拥塞控制与队头阻塞

> **来源映射**: View/00.md §2.1
> **国际权威参考**: RFC 793 (TCP), RFC 5681 (Congestion Control), RFC 6298 (RTO Computation), "Computer Networking: A Top-Down Approach" (Kurose & Ross, 8th Ed.)

---

## 一、知识体系思维导图

```text
TCP 协议核心机制
│
├─► 连接管理
│   ├─ 三次握手 (Three-Way Handshake)
│   │   ├─ SYN → SYN-ACK → ACK
│   │   ├─ 目的: 同步序列号、交换窗口大小
│   │   └─ 状态机: CLOSED → SYN-SENT → ESTABLISHED
│   │
│   ├─ 四次挥手 (Four-Way Termination)
│   │   ├─ FIN → ACK → FIN → ACK
│   │   ├─ 全双工关闭: 每方向独立关闭
│   │   └─ TIME_WAIT (2MSL): 防止旧报文干扰新连接
│   │
│   └─ 状态机
│       ├─ LISTEN → SYN-RCVD → ESTABLISHED
│       ├─ ESTABLISHED → FIN-WAIT-1 → FIN-WAIT-2 → TIME_WAIT
│       └─ ESTABLISHED → CLOSE-WAIT → LAST-ACK → CLOSED
│
├─► 可靠传输
│   ├─ 序列号 (Sequence Number): 字节流排序
│   ├─ 确认应答 (ACK): 累积确认
│   ├─ 重传机制
│   │   ├─ 超时重传 (RTO): Jacobson/Karels 算法
│   │   └─ 快速重传 (Fast Retransmit): 3个重复ACK
│   └─ 滑动窗口 (Sliding Window)
│       ├─ 发送窗口: min(cwnd, rwnd)
│       ├─ 接收窗口 (rwnd): 流量控制
│       └─ 拥塞窗口 (cwnd): 拥塞控制
│
├─► 拥塞控制算法
│   ├─ 慢启动 (Slow Start)
│   │   └─ cwnd 每 RTT 翻倍: 指数增长
│   ├─ 拥塞避免 (Congestion Avoidance)
│   │   └─ cwnd 每 RTT 线性增长 (+1 MSS)
│   ├─ 快重传 (Fast Retransmit)
│   ├─ 快恢复 (Fast Recovery)
│   │   └─ ssthresh = cwnd/2, cwnd = ssthresh + 3 MSS
│   └─ 现代变体
│       ├─ CUBIC (Linux 默认): 三次函数增长
│       ├─ BBR (Google): 基于带宽和 RTT 模型
│       └─ Reno/NewReno: 经典实现
│
└─► 队头阻塞 (Head-of-Line Blocking)
    ├─ 原因: TCP 保证字节流顺序
    ├─ 表现: 一个包丢失，后续包无法交付应用层
    └─ 影响: HTTP/2 多路复用仍受 TCP 层队头阻塞限制
```

---

## 二、核心概念的形式化定义

### 2.1 三次握手形式化

```text
定义 (TCP 连接建立):
  设客户端 C, 服务端 S, ISN 为初始序列号

  步骤 1 (SYN):
    C → S: SYN, seq = ISN_C

  步骤 2 (SYN-ACK):
    S → C: SYN, ACK, seq = ISN_S, ack = ISN_C + 1

  步骤 3 (ACK):
    C → S: ACK, seq = ISN_C + 1, ack = ISN_S + 1

  连接建立条件:
    ∃ 交换序列号: C 知道 ISN_S, S 知道 ISN_C
    ∧ 双向通道可达: C 能收 S 的包, S 能收 C 的包

  为什么不是两次握手?
    两次握手时, 已失效的连接请求报文到达服务端,
    服务端会建立无效连接, 浪费资源。
```

### 2.2 拥塞控制形式化

```text
定义 (AIMD 拥塞控制):
  状态变量:
    cwnd: 拥塞窗口 (拥塞控制)
    rwnd: 接收窗口 (流量控制)
    ssthresh: 慢启动阈值

  发送窗口: W = min(cwnd, rwnd)

  慢启动阶段 (cwnd < ssthresh):
    每收到一个 ACK: cwnd ← cwnd + MSS
    每 RTT: cwnd ← cwnd × 2

  拥塞避免阶段 (cwnd ≥ ssthresh):
    每 RTT: cwnd ← cwnd + MSS

  丢包检测 (超时):
    ssthresh ← max(cwnd/2, 2×MSS)
    cwnd ← MSS
    进入慢启动

  丢包检测 (3个重复ACK):
    ssthresh ← cwnd/2
    cwnd ← ssthresh + 3×MSS
    进入快恢复
```

### 2.3 CUBIC 算法

```text
定义 (CUBIC 窗口增长):
  W(t) = C × (t - K)³ + W_max

  其中:
    W_max: 上次丢包时的窗口大小
    K = ∛(W_max × β / C): 无丢包增长至 W_max 的时间
    C = 0.4: 缩放因子
    β = 0.7: 乘性减少因子 (丢包后 cwnd = β × W_max)

  特性:
    - 在 W_max 附近增长缓慢 (拥塞避免)
    - 远离 W_max 时增长快速 (带宽探测)
    - RTT 公平性: 不同 RTT 的连接趋于收敛到相同带宽
```

---

## 三、多维矩阵对比

| 特性 | TCP Reno | TCP CUBIC | TCP BBR | QUIC (对比) |
|------|----------|-----------|---------|-------------|
| **拥塞信号** | 丢包 | 丢包 | 带宽/RTT 模型 | 丢包 + ACK 延迟 |
| **窗口增长** | 线性 (AIMD) | 三次函数 | 基于模型探测 | 可插拔 |
| **RTT 公平性** | 差 (短 RTT 占优) | 较好 | 好 | 好 |
| **Bufferbloat 抗性** | 差 | 差 | **优** | 优 |
| **实现位置** | 内核 | 内核 | 内核 | 用户空间 |
| **主要用户** | 历史系统 | Linux 默认 | Google/YouTube | HTTP/3 |

---

## 四、权威引用

> **Van Jacobson** (TCP/IP 性能优化先驱, 1988):
> "Congestion Avoidance and Control" —— 首次系统提出拥塞控制框架，奠定了现代互联网拥塞控制的基础。

> **RFC 5681** (TCP Congestion Control):
> "TCP MUST implement slow start and congestion avoidance."

> **Cardwell et al.** (Google, SIGCOMM 2016, "BBR: Congestion-Based Congestion Control"):
> "BBR models the network path as a pipe with a bottleneck rate and round-trip propagation time, rather than treating packet loss as the primary signal of congestion."

> **Kurose & Ross** ("Computer Networking: A Top-Down Approach", 8th Ed.):
> "TCP's sliding window is the marriage of reliable data transfer and flow control — elegant in theory, complex in practice."

---

## 五、工程实践与代码示例

### 5.1 查看 Linux TCP 拥塞控制算法

```bash
# 查看当前使用的拥塞控制算法
sysctl net.ipv4.tcp_congestion_control

# 查看可用算法
sysctl net.ipv4.tcp_available_congestion_control

# 切换为 BBR (需内核 4.9+)
echo "net.core.default_qdisc=fq" >> /etc/sysctl.conf
echo "net.ipv4.tcp_congestion_control=bbr" >> /etc/sysctl.conf
sysctl -p
```

### 5.2 TIME_WAIT 状态优化

```bash
# 查看 TIME_WAIT 连接数量
ss -tan state time-wait | wc -l

# 启用 TIME_WAIT 快速回收 (内核 < 4.12)
echo 1 > /proc/sys/net/ipv4/tcp_tw_recycle

# 启用 TIME_WAIT 重用
echo 1 > /proc/sys/net/ipv4/tcp_tw_reuse
```

---

## 六、批判性总结

TCP 的队头阻塞是其**可靠字节流语义**的直接后果：为了保证应用层接收到的数据严格有序，TCP 必须在收到乱序包时暂停交付。这种设计在单流场景下合理，但在 HTTP/2 的多路复用场景下变成了致命缺陷——一个流的丢包会阻塞所有其他流的交付，即使这些流的包已经正确到达。

BBR 的出现标志着拥塞控制范式的转变：从**丢包驱动**（Reno/CUBIC）到**模型驱动**（测量带宽和 RTT）。然而 BBR 与基于丢包的算法共存时会产生**公平性问题**——BBR 流会过度占用缓冲区，挤压 Reno/CUBIC 流的带宽。这再次印证了网络协议的**生态复杂性**：单个协议的优化可能破坏整个网络的纳什均衡。

CUBIC 作为 Linux 默认算法已经服役十余年，其基于三次函数的窗口增长在**高带宽长距离网络 (BDP)** 中表现优异，但在**低延迟交互式应用**中过于激进。TCP 的演进受限于内核实现——修改拥塞控制算法需要操作系统升级，这正是 QUIC 选择用户空间实现的根本动机。
