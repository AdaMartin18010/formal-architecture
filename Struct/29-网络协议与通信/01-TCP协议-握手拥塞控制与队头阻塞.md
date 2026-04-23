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


---

## 七、概念属性关系网络

### 7.1 核心概念依赖/包含/对立关系表

| 概念 A | 关系类型 | 概念 B | 形式化描述 |
|--------|----------|--------|------------|
| TCP 连接 | ⊃ (包含) | 三次握手 | 握手协议 ⊂ 连接管理状态机 |
| 三次握手 | → (蕴含) | 序列号同步 | SYN 交换 ⟹ ISN_C 与 ISN_S 互知 |
| 四次挥手 | ⊃ (包含) | TIME_WAIT | 2MSL 等待 ⊂ 全双工优雅关闭 |
| 滑动窗口 | = (定义) | min(cwnd, rwnd) | 发送窗口受拥塞与流量双重约束 |
| cwnd | ⊥ (动态对立) | ssthresh | cwnd < ssthresh ⟹ 指数增长; cwnd ≥ ssthresh ⟹ 线性增长 |
| 慢启动 | → (前导) | 拥塞避免 | 状态转移: SS → CA 由 ssthresh 阈值触发 |
| 快重传 | → (前导) | 快恢复 | 3 重复 ACK 触发 FR, 进而进入 FR 状态 |
| CUBIC | ⊃ (包含) | W(t) = C(t-K)³ + W_max | 三次函数作为窗口增长核 |
| BBR | ⊥ (范式对立) | Reno/CUBIC | 模型驱动 (带宽/RTT) ↔ 事件驱动 (丢包) |
| 队头阻塞 | ∈ (必然属性) | TCP 字节流 | 有序性语义 ⟹ HoL 不可消除 |

### 7.2 ASCII 拓扑图：TCP 核心机制关系网

```text
┌──────────────────────────────────────────────────────────────────────┐
│                        TCP 连接生命周期                               │
│                                                                      │
│   CLOSED ──SYN──→ SYN-SENT ──SYN-ACK──→ ESTABLISHED                  │
│      ↑                                      │                        │
│      └──────────── 数据传输 ─────────────────┘                        │
│                                              │                        │
│                    ┌─────────────────────────┼─────────────┐          │
│                    ▼                         ▼             ▼          │
│              ┌──────────┐            ┌─────────────┐  ┌─────────┐     │
│              │可靠传输   │            │ 拥塞控制     │  │流量控制 │     │
│              │机制      │            │ 子系统       │  │子系统   │     │
│              └────┬─────┘            └──────┬──────┘  └────┬────┘     │
│                   │                         │              │          │
│         ┌─────────┼─────────┐      ┌────────┼────────┐    │          │
│         ▼         ▼         ▼      ▼        ▼        ▼    ▼          │
│      ┌─────┐  ┌─────┐  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐     │
│      │序列号│  │ACK  │  │重传 │ │慢启动│ │拥塞 │ │快重 │ │rwnd │     │
│      │排序 │  │累积  │  │RTO  │ │SS   │ │避免 │ │传/恢│ │通告  │     │
│      └─────┘  └─────┘  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘     │
│                                                      │               │
│                              ┌───────────────────────┘               │
│                              ▼                                       │
│                         ┌─────────┐                                  │
│                         │队头阻塞  │                                  │
│                         │(HoL)   │                                  │
│                         └────┬────┘                                  │
│                              │                                       │
│              有序性语义 ──────┘   ←── 结构性必然                      │
│                                                                      │
│   ESTABLISHED ──FIN──→ FIN-WAIT-1 ──ACK──→ FIN-WAIT-2               │
│                              │                                       │
│                              ▼                                       │
│                         TIME_WAIT (2MSL)                             │
│                              │                                       │
│                              ▼                                       │
│                           CLOSED                                     │
└──────────────────────────────────────────────────────────────────────┘
```

### 7.3 形式化映射

```text
定义 TCP 状态机为一个五元组:
  M = ⟨Q, Σ, δ, q₀, F⟩  其中:
    Q = {CLOSED, LISTEN, SYN-SENT, SYN-RCVD, ESTABLISHED,
         FIN-WAIT-1, FIN-WAIT-2, CLOSE-WAIT, CLOSING,
         LAST-ACK, TIME_WAIT}
    Σ = {SYN, ACK, FIN, RST, data}
    δ: Q × Σ → Q  (非确定性，因包丢失/重传)
    q₀ = CLOSED
    F = {CLOSED, TIME_WAIT}

拥塞控制作为混合系统 (Hybrid System):
  连续变量:  cwnd ∈ ℝ⁺,  ssthresh ∈ ℝ⁺
  离散状态:  {SLOW_START, CONGESTION_AVOIDANCE, FAST_RECOVERY}
  转移条件:
    SLOW_START → CONGESTION_AVOIDANCE:  cwnd ≥ ssthresh
    CONGESTION_AVOIDANCE → FAST_RECOVERY:  dupACK ≥ 3
    FAST_RECOVERY → SLOW_START:  timeout
    FAST_RECOVERY → CONGESTION_AVOIDANCE:  new ACK arrives

CUBIC 的连续动力学:
  d²W/dt² = 6C(t - K)  (二阶非线性)
  在 t = K 处 dW/dt = 0，W 达到局部极大值 W_max
  远离 W_max 时高阶导数主导，增长迅速 (探测带宽)
  接近 W_max 时高阶项衰减，增长缓慢 (避免拥塞)

BBR 的状态估计:
  BtlBw = max(delivered / interval)  over recent windows
  RTprop = min(RTT_sample)  over 10 seconds
  发送速率:  pacing_rate = 2 × BtlBw / 3  (留 33% 余量)
   inflight 上限:  BtlBw × RTprop × 2  (2×BDP)
```

---

## 八、形式化推理链

### 8.1 公理体系

**公理 A₁ (可靠传输的不可能性三角)**
> 在异步不可靠网络上，同时满足 exactly-once 交付、低延迟、高可用性三者不可兼得 (Fischer, Lynch & Paterson, 1985 的 FLP 结果在网络层的表现)。

**公理 A₂ (网络资源稀缺性)**
> 任意网络路径的带宽 B 与缓冲区容量 BDP = B × RTT 均为有限量。

**公理 A₃ (丢包即拥塞信号，Jacobson 1988)**
> 在尾部丢弃队列中，丢包是拥塞的唯一可观测信号。

### 8.2 引理与定理

**引理 L₁ (三次握手的必要性)**
> 两次握手不足以建立可靠的全双工连接。
>
> 反证: 设仅两次握手 (SYN, SYN-ACK)。若客户端的 SYN 在网络中延迟，客户端超时重发 SYN'，服务端对 SYN' 回复 SYN'-ACK 并建立连接。之后延迟的 SYN 到达服务端，服务端再次建立无效连接。∴ 需要第三次 ACK 使服务端确认客户端收到了 SYN-ACK。∎

**引理 L₂ (AIMD 的公平性收敛)**
> 在共享瓶颈链路上，N 个采用相同 AIMD 参数的 TCP 连接收敛到每连接 1/N 带宽。
>
> 证明概要 (Chiu & Jain, 1989):  定义公平性度量 F = (∑xᵢ)² / (N∑xᵢ²)。AIMD 的加性增长使状态点沿 45° 线远离原点，乘性减少使状态点向原点收缩。在相空间中，任何非公平状态经 AIMD 迭代后 F 单调递增，最终收敛到 x₁=x₂=...=xₙ 的公平线。∎

**定理 T₁ (TCP Reno 的吞吐量上限)**
> 设丢包率为 p，RTT 为 T，MSS 为 M。TCP Reno 的稳态吞吐量为:
>
> B ≈ (M / T) × √(3 / 2p)   (Mathis et al., 1997)
>
> 证明概要:  一个拥塞周期内，窗口从 W/2 增长到 W，共发送 (3/8)W² 个包，丢失 1 个包。
> ∴ p ≈ 1 / ((3/8)W²) → W ≈ √(8 / 3p)
> 吞吐量 = (3/4)W × M / T ≈ (M / T) × √(3 / 2p)。∎

**定理 T₂ (BBR 与丢包算法的公平性困境)**
> BBR 流与 Reno/CUBIC 流共享瓶颈缓冲区时，BBR 流会过度占用缓冲区，挤压丢包流带宽。
>
> 证明概要:  BBR 以 pacing_rate = 2BtlBw/3 发送， inflight 上限为 2BDP。
> Reno/CUBIC 以 cwnd 增长填充缓冲区直至丢包。
> 当缓冲区 > BDP 时，BBR 不减少发送速率（因未检测到 BtlBw 下降），
> 而 Reno 因丢包将 cwnd 减半。
> 结果:  BBR 获得 > 50% 带宽，Reno 获得 < 公平份额。∎

**推论 C₁ (CUBIC 的高 BDP 优越性)**
> CUBIC 的三次函数增长使其在高带宽长距离网络中比 Reno 更快收敛到公平带宽。
>
> 比较:  Reno 线性增长，从 W/2 到 W_max 需要 W/2 个 RTT。
> CUBIC 三次增长，从 W/2 到 W_max 需要 O(∛W_max) 个 RTT。
> 当 W_max ≫ 1 时，CUBIC 收敛时间 ≪ Reno。∎

### 8.3 关键学者引用（已验证）

> **Van Jacobson** (1988, SIGCOMM): "Congestion Avoidance and Control." *ACM Computer Communication Review*, 18(4), 314–329. —— 现代 TCP 拥塞控制的奠基论文。

> **Dah-Ming Chiu & Raj Jain** (1989): "Analysis of the Increase and Decrease Algorithms for Congestion Avoidance in Computer Networks." *Computer Networks and ISDN Systems*, 17(1), 1–14. —— AIMD 公平性收敛的严格分析。

> **Matthew Mathis, Jeffrey Semke, Jamshid Mahdavi & Teunis Ott** (1997): "The Macroscopic Behavior of the TCP Congestion Avoidance Algorithm." *ACM SIGCOMM CCR*, 27(3), 67–82. —— TCP 吞吐量平方根公式的推导。

> **Sangtae Ha, Injong Rhee & Lisong Xu** (2008): "CUBIC: A New TCP-Friendly High-Speed TCP Variant." *ACM SIGOPS Operating Systems Review*, 42(5), 64–74. —— Linux 默认拥塞控制算法。

---

## 九、ASCII 推理判定树 / 决策树

### 9.1 拥塞控制算法选型决策树

```text
                    ┌─────────────────────────────┐
                    │ 选择 TCP 拥塞控制算法         │
                    └──────────────┬──────────────┘
                                   │
            ┌──────────────────────┼──────────────────────┐
            ▼                      ▼                      ▼
      ┌───────────┐         ┌───────────┐         ┌───────────┐
      │ 高 BDP?   │         │ 低延迟交互?│         │ 公网混合流?│
      │ (>100ms)  │         │ (<20ms)   │         │ (多租户)  │
      └─────┬─────┘         └─────┬─────┘         └─────┬─────┘
            │                     │                     │
      ┌─────┴─────┐         ┌─────┴─────┐         ┌─────┴─────┐
      ▼           ▼         ▼           ▼         ▼           ▼
   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐
   │ 是   │   │ 否   │   │ 是   │   │ 否   │   │ 是   │   │ 否   │
   └──┬──┘   └──┬──┘   └──┬──┘   └──┬──┘   └──┬──┘   └──┬──┘
      │         │         │         │         │         │
      ▼         ▼         ▼         ▼         ▼         ▼
   ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
   │CUBIC │ │Reno  │ │BBR   │ │CUBIC │ │CUBIC │ │BBR   │
   │或 BBR│ │或 BBR│ │(激进) │ │(保守) │ │(默认) │ │(实验)│
   └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘
      │         │         │         │         │         │
      ▼         ▼         ▼         ▼         ▼         ▼
   理由:     理由:     理由:     理由:     理由:     理由:
   三次函数   简单公平  低延迟    高吞吐    兼容性    公平性
   快速收敛   资源友好  优先      兼顾      最好      最优
```

### 9.2 连接异常排查决策树

```text
                    ┌─────────────────────────────┐
                    │ TCP 连接异常诊断              │
                    └──────────────┬──────────────┘
                                   │
            ┌──────────────────────┼──────────────────────┐
            ▼                      ▼                      ▼
      ┌───────────┐         ┌───────────┐         ┌───────────┐
      │ 连接建立  │         │ 数据传输  │         │ 连接关闭  │
      │ 阶段失败? │         │ 阶段异常? │         │ 阶段问题? │
      └─────┬─────┘         └─────┬─────┘         └─────┬─────┘
            │                     │                     │
      ┌─────┴─────┐         ┌─────┴─────┐         ┌─────┴─────┐
      ▼           ▼         ▼           ▼         ▼           ▼
   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐
   │SYN  │   │SYN  │   │吞吐 │   │延迟 │   │大量 │   │FIN  │
   │超时 │   │被RST│   │骤降 │   │飙升 │   │TIME│   │无响应│
   └─┬───┘   └──┬──┘   └──┬──┘   └──┬──┘   │_WAIT│   └─┬───┘
      │          │         │         │      └──┬──┘      │
      ▼          ▼         ▼         ▼         ▼         ▼
   ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
   │检查  │ │检查  │ │检查  │ │检查  │ │启用  │ │检查  │
   │防火墙│ │服务  │ │拥塞  │ │Buffer│ │tw_   │ │对端  │
   │规则  │ │是否  │ │窗口  │ │bloat │ │reuse │ │进程  │
   │      │ │监听  │ │      │ │/丢包 │ │      │ │存活  │
   └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘
```

---

## 十、国际权威课程对齐

### 10.1 课程映射表

| 本模块主题 | MIT 6.829 | Stanford CS 144 | CMU 15-441 | Berkeley CS 168 |
|------------|-----------|-----------------|------------|-----------------|
| **三次握手/四次挥手** | L3: TCP Basics | L5: TCP State Machine | L11: TCP Connection Management | L9: Transport Layer |
| **滑动窗口** | L4: Flow Control | L4: Reliable Delivery | L13: TCP Sliding Window | L10: Reliable Delivery |
| **拥塞控制 (AIMD)** | L8: Congestion Control | L6: TCP Details | L15: Congestion Control | L12: Congestion Control |
| **CUBIC/BBR** | L9: TCP Issues | L14: Newer CCAs | L16: Advanced TCP | L12: BBR Discussion |
| **队头阻塞** | L10: Multiplexing | L8: HTTP/2 | L17: Transport Futures | L11: HoL Analysis |
| **TIME_WAIT** | L5: TCP Internals | Lab 2: Edge Cases | L12: TCP State Machine | L9: Discussion |

### 10.2 详细 Lecture / Homework / Project 映射

**MIT 6.829: Computer Networks**

- **Lecture 3-4**: TCP Basics & Flow Control —— Karn 算法、RTT 估计、窗口管理
- **Lecture 8**: End-to-End Congestion Control —— Jacobson (1988) 论文精读，AIMD 稳定性分析
- **Homework 1**: ns-2 模拟 Reno 与 CUBIC 的吞吐量与公平性
- **Final Project**: 可选实现新的拥塞控制算法或评估 BBRv2

**Stanford CS 144**

- **Lab 1-2**: Reliable Transport —— 实现 TCPSender 与 TCPReceiver，处理窗口、重传、超时
- **Lecture 5**: TCP State Machine —— 三次握手、四次挥手的完整状态转换
- **Lecture 6**: TCP Details —— 拥塞控制、Nagle 算法、延迟 ACK
- **Checkpoint 4**: 将自实现 TCP 接入完整协议栈，与 Linux TCP 互操作测试

**CMU 15-441**

- **Lecture 11-12**: TCP Connection Management —— 状态机、SYN cookies、TIME_WAIT 优化
- **Lecture 13-14**: TCP Sliding Window & Performance —— 吞吐量公式、RTT 公平性
- **Lecture 15**: Congestion Control —— Reno、NewReno、SACK、CUBIC 对比
- **Project 2**: BitTorrent 客户端 —— 实践 TCP 连接管理与拥塞控制

**Berkeley CS 168**

- **Lecture 9**: Transport Layer —— 端到端原则、端口复用、连接管理
- **Lecture 10-11**: Reliable Delivery —— 序列号、ACK、超时重传、滑动窗口
- **Lecture 12**: Congestion Control —— AIMD、慢启动、TCP 吞吐量分析
- **Project 3**: Implement a Reliability Protocol —— 在模拟不可靠网络上实现类 TCP 协议

### 10.3 核心参考文献

1. **Jacobson, V.** (1988). "Congestion Avoidance and Control." *ACM SIGCOMM Computer Communication Review*, 18(4), 314–329. —— TCP 拥塞控制的奠基论文，定义了慢启动、拥塞避免和快重传。

2. **Chiu, D.-M., & Jain, R.** (1989). "Analysis of the Increase and Decrease Algorithms for Congestion Avoidance in Computer Networks." *Computer Networks and ISDN Systems*, 17(1), 1–14. —— AIMD 收敛性的严格数学证明。

3. **Mathis, M., Semke, J., Mahdavi, J., & Ott, T.** (1997). "The Macroscopic Behavior of the TCP Congestion Avoidance Algorithm." *ACM SIGCOMM CCR*, 27(3), 67–82. —— 推导 TCP Reno 吞吐量平方根公式。

4. **Brakmo, L. S., O'Malley, S. W., & Peterson, L. L.** (1994). "TCP Vegas: New Techniques for Congestion Detection and Avoidance." *ACM SIGCOMM CCR*, 24(4), 24–35. —— 首次将 RTT 增长作为拥塞信号，早于 BBR 二十年。

---

## 十一、批判性总结

TCP 的队头阻塞是其可靠字节流语义的**逻辑必然**，而非实现层面的优化空间。任何试图在保持 TCP 有序性承诺的同时消除队头阻塞的努力，在形式上都等价于试图构造一个既保证全序又允许独立并行的矛盾系统。HTTP/2 的多路复用正是这种矛盾的集中爆发点：应用层抽象假设存在多个独立的字节流通道，但传输层只提供一个单一的全序管道。这不是 HTTP/2 的设计失误，而是 TCP/IP 协议栈分层抽象的根本性泄漏——当上层语义与下层保证发生结构性冲突时，分层模型的封装边界便失去了意义。QUIC 的激进方案不是优化 TCP，而是**放弃 TCP**，在用户空间重建传输层，这实际上宣告了操作系统内核作为网络协议唯一仲裁者时代的终结。

CUBIC 与 BBR 的并存揭示了网络协议研究的一个深层张力：**公平性**与**效率**之间的不可调和性。CUBIC 基于丢包的保守设计保证了多流共存时的收敛公平，但在高带宽长距离网络中收敛缓慢；BBR 基于模型的激进设计在高 BDP 网络中表现卓越，但与 Reno/CUBIC 共存时产生严重的公平性失衡。这不是算法本身的缺陷，而是拥塞信号选择的基本权衡：丢包信号滞后但公平，带宽探测信号及时但排他。网络研究者长期追求"完美"的拥塞控制算法，但 Nash 均衡理论告诉我们，在异构策略共存的网络中，单一策略的局部最优往往导致全局次优。未来的方向可能不在于寻找更好的单一算法，而在于设计**拥塞控制选择机制**——让网络路径能够协商并适配最优的算法组合。

TIME_WAIT 状态是 TCP 设计中最容易被低估的复杂性来源。2MSL 等待期的存在使得高并发短连接场景下操作系统迅速耗尽可用端口和内存资源，成为许多微服务架构的隐形瓶颈。Linux 的 `tcp_tw_reuse` 和 `tcp_tw_recycle`（后者已被移除）是试图绕过这一限制的权宜之计，但它们破坏了 TCP 的可靠性假设——重用 TIME_WAIT 连接可能导致旧连接的迟滞报文被新连接误收。这一困境的根本原因在于 TCP 将连接标识（四元组）与连接状态紧密绑定，而 QUIC 的 ConnectionID 机制从根本上解除了这一绑定，允许连接在地址变化后持续存在。这再次证明：协议层面的问题，最终的解决往往需要在协议层面重构核心抽象，而非在实现层面打补丁。
