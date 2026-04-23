# SRE 实践：SLO、错误预算与告警

> **来源映射**: View/00.md §3.1
> **国际权威参考**: "Site Reliability Engineering" (Google, O'Reilly), "The Service Level Objective Handbook"

---

## 一、知识体系思维导图

```text
SRE 实践: SLO、错误预算与告警
│
├─► 可靠性层次
│   ├─ SLI (Service Level Indicator): 可量化指标
│   ├─ SLO (Service Level Objective): 可靠性目标
│   ├─ SLA (Service Level Agreement): 对外承诺 (含赔偿)
│   └─ 错误预算 (Error Budget): 100% - SLO
│
├─► SLO 设计原则
│   ├─ 以用户为中心: 衡量用户体验而非系统指标
│   ├─ 可度量: 基于客观数据
│   ├─ 可达成: 基于历史数据，非拍脑袋
│   ├─ 数量少: 每个服务 2-3 个 SLO
│   └─ 有期限: 明确评估窗口 (如 30天滚动)
│
├─► 错误预算政策
│   ├─ 预算充足 (>50% 剩余): 正常发布新功能
│   ├─ 预算紧张 (<50% 剩余): 谨慎发布，增加测试
│   ├─ 预算耗尽 (≤0%): 冻结发布，专注稳定性
│   └─ 预算超额: 启动紧急复盘 (Postmortem)
│
├─► 告警设计
│   ├─► 告警分级
│   │   ├─ P0 (Critical): 立即响应，任何时间
│   │   ├─ P1 (High): 4小时内响应
│   │   ├─ P2 (Medium): 24小时内响应
│   │   └─ P3 (Low): 工作日处理
│   │
│   ├─► 告警质量
│   │   ├─ Actionable: 收到告警必须能采取行动
│   │   ├─ 无噪音: 减少误报和抖动
│   │   └─ 根源导向: 告警应指向根因，非症状
│   │
│   └─► 告警疲劳缓解
│       ├─ 聚合: 同根因的多个告警合并
│       ├─ 抑制: 父告警抑制子告警
│       ├─ 静默: 计划内维护期间静默
│       └─ 自动恢复: 问题消失后自动关闭
│
└─► SRE 核心实践
    ├─ 运维负载上限: ≤50% 时间用于工单/on-call
    ├─ 自动化: 将手动操作转化为自动化
    ├─ 发布工程: 频繁、小批量、可回滚
    ├─ 容量规划: 基于负载测试和排队论
    └─ 事后复盘: 无责复盘 (Blameless Postmortem)
```

---

## 二、核心概念的形式化定义

### 2.1 SLO 与错误预算

```text
定义 (SLO):
  SLO = ⟨SLI, Target, Window⟩

  SLI: 服务级别指标，如 "HTTP 成功响应比例"
       SLI = good_events / total_events

  Target: 目标值，如 99.9%

  Window: 评估窗口，如 30天滚动窗口

  错误预算:
    ErrorBudget = 1 - Target = 0.1%

    30天窗口示例:
      总请求: 1,000,000
      允许错误: 1,000,000 × 0.1% = 1,000 次

  消耗速率:
    BurnRate = errors_in_window / ErrorBudget

    BurnRate = 1  → 刚好用完全部预算
    BurnRate = 2  → 2倍速消耗，15天内耗尽
    BurnRate = 0.5 → 0.5倍速，60天内耗尽
```

### 2.2 多窗口多 burn rate 告警

```text
定义 (多窗口告警):
  Google SRE 推荐的告警规则:

  快速消耗 (1小时窗口, burn_rate=14.4):
    若 1小时内消耗了 2% 的月度预算
    → 2% × 30天 ≈ 14.4小时
    → 1小时内烧完 14.4 小时的预算
    → 意味着服务在 1 小时内完全不可用

  慢速消耗 (3天窗口, burn_rate=2):
    若 3天内消耗了 10% 的月度预算
    → 服务持续降级但未完全崩溃

  告警条件:
    (快速窗口 ∧ 高burn_rate) ∨ (慢速窗口 ∧ 中burn_rate)

  这确保:
    - 快速故障: 立即告警 (分钟级响应)
    - 缓慢泄漏: 延迟告警 (天级响应，减少噪音)
```

---

## 三、SLO 设计对比矩阵

| SLI 类型 | 指标 | 适用服务 | 优点 | 缺点 |
|---------|------|---------|------|------|
| **可用性** | 成功请求比例 | API/Web | 直接反映用户体验 | 忽略延迟 |
| **延迟** | P50/P95/P99 响应时间 | API/搜索 | 捕获性能退化 | 阈值难以设定 |
| **吞吐量** | QPS/RPS | 网关/队列 | 反映容量 | 与可用性相关 |
| **错误率** | 5xx比例 | 所有服务 | 直接反映故障 | 4xx 是否计入? |
| **新鲜度** | 数据更新延迟 | 缓存/CDN | 捕获数据同步 | 难以统一度量 |
| **正确性** | 结果准确率 | 搜索/推荐 | 业务价值 | 主观判断 |

---

## 四、权威引用

> **Google SRE Book** (2016):
> "Hope is not a strategy." —— SRE 的核心是系统性消除对"希望"的依赖。

> **Ben Treynor Sloss** (Google VP, SRE 创始人):
> "SRE is what happens when you ask a software engineer to design an operations team."

> **Cindy Sridharan** ("Distributed Systems Observability"):
> "Monitoring tells you whether the system works. Observability lets you ask why it's not working."

> **Niall Murphy** (Google SRE):
> "If you can't measure it, you can't improve it. If you measure the wrong thing, you'll improve the wrong thing."

---

## 五、工程实践

### 5.1 SLO 与错误预算仪表板

```promql
# SLI: HTTP 可用性
(
  sum(rate(http_requests_total{status=~"2.."}[5m]))
  /
  sum(rate(http_requests_total[5m]))
) * 100

# 错误预算消耗速率 (30天窗口)
(
  sum(increase(http_requests_total{status=~"5.."}[30d]))
  /
  (sum(increase(http_requests_total[30d])) * (1 - 0.999))
)

# 告警: 快速 burn (1小时窗口)
- alert: ErrorBudgetFastBurn
  expr: |
    (
      sum(rate(http_requests_total{status=~"5.."}[1h]))
      /
      sum(rate(http_requests_total[1h]))
    ) > (14.4 * (1 - 0.999))
  for: 2m
  labels:
    severity: critical
```

### 5.2 无责复盘模板

```markdown
# 事后复盘 (Postmortem)

## 事件摘要
- 日期: 2026-04-20
- 持续时间: 23分钟
- 影响: 支付服务 99.5% 错误率，约 12,000 笔交易失败
- 触发: 数据库连接池耗尽

## 时间线 (精确到分钟)
- 14:32 部署新版本 v2.3.1
- 14:35 数据库连接数开始上升
- 14:38 连接池耗尽，大量请求超时
- 14:40 P0 告警触发
- 14:45 回滚到 v2.3.0
- 14:55 服务恢复正常

## 根因分析
新版本引入了 N+1 查询问题，每个请求额外查询 10 次数据库。

## 经验教训
1. 部署后应监控数据库连接数 (已添加到 checklist)
2. 连接池需要熔断保护 (已创建任务)
3. 集成测试需包含负载测试 (已排期)

## 行动项
| 任务 | 负责人 | 截止日期 |
|------|--------|---------|
| 添加连接池监控 | Alice | 2026-04-27 |
| 实现连接池熔断 | Bob | 2026-05-04 |
| 集成负载测试 | Carol | 2026-05-15 |

## 免责申明
本复盘聚焦于系统性改进，不追究个人责任。
```

---

## 六、批判性总结

SRE 的"错误预算"概念是**软件工程史上最优雅的管理工具之一**：它将抽象的"可靠性"转化为可量化的"预算"，使产品团队与工程团队有了共同语言。产品团队希望发布新功能，工程团队关注稳定性——错误预算成为两者之间的**自动仲裁者**：预算充足时，发布自由；预算耗尽时，强制冻结。

但 SLO 的设计是一个**政治过程**而非技术过程：过于宽松的 SLO（如 99%）意味着允许 7.2 小时/月的宕机，可能损害用户信任；过于严格的 SLO（如 99.999%）意味着仅允许 26 秒/月，成本呈指数增长。Google 的"四个九"（99.99%）不是技术最优解，而是**成本-收益曲线的拐点**——再往上每增加一个九，成本增加 10 倍，收益边际递减。

SRE 的"无责复盘"文化是**组织学习理论**的工程实践：它承认人类会犯错，系统的目标不是防止所有错误，而是从错误中学习。这与航空业的事后调查文化一脉相承——当所有人都知道"说真话不会受罚"时，真正的根因才能浮出水面。
