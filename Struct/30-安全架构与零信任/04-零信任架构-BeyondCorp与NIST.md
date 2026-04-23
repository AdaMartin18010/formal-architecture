# 零信任架构：BeyondCorp 与 NIST

> **来源映射**: View/02.md §7, View/09.md
> **国际权威参考**: NIST SP 800-207, Google BeyondCorp (USENIX 2014), Gartner Zero Trust

---

## 一、知识体系思维导图

```text
零信任架构 (Zero Trust Architecture, ZTA)
│
├─► 核心原则
│   ├─ 永不信任，始终验证 (Never Trust, Always Verify)
│   ├─ 假设 breach: 边界已失守、内部不可信
│   ├─ 最小权限: 按需授权、动态评估
│   ├─ 持续验证: 实时行为分析、风险评分
│   └─ 全面可见: 所有流量加密、所有访问记录
│
├─► Google BeyondCorp (工业起点)
│   ├─► 背景
│   │   ├─ 2010 年 Aurora 攻击 (Google 被入侵)
│   │   └─ 结论: 边界安全模型已死
│   │
│   ├─► 核心组件
│   │   ├─ 设备库存服务: 设备信任评估
│   │   ├─ 用户/群组数据库: 身份与权限
│   │   ├─ 访问控制引擎: 实时策略决策
│   │   ├─ 访问代理: 单点接入、TLS终止
│   │   └─ 网关: 应用级访问控制
│   │
│   └─► 关键洞察
│       ├─ 访问权限不基于网络位置
│       ├─ 设备信任度与用户身份同等重要
│       └─ 所有访问通过集中代理，统一审计
│
├─► NIST SP 800-207 (标准定义)
│   ├─► 逻辑组件
│   │   ├─ 策略引擎 (Policy Engine): 最终决策
│   │   ├─ 策略管理员 (Policy Administrator): 执行决策
│   │   ├─ 策略执行点 (PEP): 网关/代理
│   │   └─ 持续诊断与缓解 (CDM): 设备/用户状态
│   │
│   ├─► 部署模型
│   │   ├─ 增强身份治理: 以 IAM 为中心
│   │   ├─ 微分段: 网络层隔离
│   │   └─ 基础设施与软件定义边界: 软件层隔离
│   │
│   └─► 信任算法
│       ├─ 单源: 单一属性评分
│       ├─ 多源: 加权多属性评分
│       └─ 动态: 上下文实时调整
│
└─► 实施挑战 (2026)
    ├─ 遗留系统: 不支持现代认证协议
    ├─ 用户体验: 频繁验证造成摩擦
    ├─ 性能: 每次访问需策略评估
    ├─ 技能: 零信任架构师稀缺
    └─ 文化: "内部=安全"的思维惯性
```

---

## 二、核心概念的形式化定义

### 2.1 零信任访问决策

```text
定义 (零信任访问决策):
  AccessDecision = f(Identity, Device, Context, Resource, Policy, Time)

  输入:
    Identity: ⟨用户ID, 凭证强度, MFA状态⟩
    Device: ⟨设备ID, 合规状态, 补丁级别, 加密状态⟩
    Context: ⟨地理位置, 网络类型, 时间, 行为异常度⟩
    Resource: ⟨敏感度标签, 数据分类⟩
    Policy: ⟨组织策略, 合规要求⟩
    Time: ⟨当前时间, 会话持续时间⟩

  输出: {Allow, Deny, StepUpAuth, LimitAccess, Monitor}

  与传统边界模型的形式化差异:
    传统: Allow(network_location) → AccessAllResources
    零信任: ∀r ∈ Resources, Access(r) = Verify(Identity, Device, Context) ∧ Policy(r)
```

### 2.2 信任评分模型

```text
定义 (动态信任评分):
  TrustScore(t) = α·IdentityScore + β·DeviceScore + γ·BehaviorScore + δ·ContextScore

  其中 α + β + γ + δ = 1, 权重由组织策略确定

  阈值决策:
    TrustScore ≥ T_high  → Allow
    T_low ≤ TrustScore < T_high → StepUpAuth
    TrustScore < T_low  → Deny

  衰减函数:
    TrustScore(t) = TrustScore(t₀) · e^(-λ·Δt)
    长时间无验证 → 信任衰减 → 需重新认证
```

---

## 三、多维矩阵对比

| 维度 | 传统边界模型 | 零信任模型 |
|------|-----------|-----------|
| **信任假设** | 内网可信，外网不可信 | 所有位置均不可信 |
| **访问控制** | 网络层 (防火墙/VPN) | 应用层 (身份+上下文) |
| **认证频率** | 一次认证，长期有效 | 持续验证，动态评估 |
| **设备信任** | 忽略或不重要 | 核心评估维度 |
| **数据保护** | 边界防护 | 端到端加密、微分段 |
| **可见性** | 边界日志 | 全流量分析、UEBA |
| **用户体验** | VPN 连接后无感知 | 频繁 MFA 验证 |
| **实施复杂度** | 低 | 高 |
| **适用组织** | 小型、静态网络 | 大型、云原生、分布式 |

---

## 四、权威引用

> **NIST SP 800-207** (2020):
> "Zero trust assumes there is no implicit trust granted to assets or user accounts based solely on their physical or network location or based on asset ownership."

> **Google BeyondCorp** (USENIX ;login: 2014):
> "The perimeter security model no longer works." —— 零信任的工业起点。

> **John Kindervag** (Forrester, 零信任概念创造者):
> "Zero Trust is not a product or a technology; it is a strategy."

> **Gartner** (2025):
> "By 2026, 60% of organizations will have implemented Zero Trust principles, up from 10% in 2021."

---

## 五、工程实践

### 5.1 BeyondCorp 访问流程

```text
用户请求访问内部应用:
  1. 请求 → 访问代理 (Access Proxy)
  2. 代理 → 策略引擎: "允许访问吗?"
  3. 策略引擎查询:
     - 用户身份与组归属
     - 设备库存: 是否企业设备? 补丁是否最新?
     - 用户行为: 是否异常登录地点?
  4. 策略引擎决策 → 策略管理员执行
  5. 若允许: 代理建立 TLS 隧道到后端应用
  6. 若拒绝: 返回 403 或要求 MFA
  7. 所有事件记录到审计日志
```

### 5.2 微分段实现

```text
传统网络:
  [Web层] → [App层] → [DB层]
  层间开放所有端口

零信任微分段:
  [Web-A] --80/tcp--> [App-B]
  [Web-A] -- denies --> [App-C]  (无业务关系)
  [App-B] --3306/tcp--> [DB-D]
  [App-B] -- denies --> [DB-E]  (无授权)

  每个连接需显式策略授权
  默认拒绝 (Default Deny)
```

---

## 六、批判性总结

零信任的核心洞察是**边界安全模型的数学失效**：当攻击者一旦突破边界（通过钓鱼邮件、供应链攻击、内部威胁），传统模型 granting 的"内网信任"就变成了**自由通行证**。零信任将访问控制从**网络拓扑**转移到**身份与上下文**——这是一次从" WHERE you are"到" WHO you are and WHAT you do"的范式转换。

但零信任的"持续验证"带来了**可用性税**：频繁的 MFA 提示、设备合规检查、网络质量评估，这些都在消耗用户的时间和耐心。2026 年的趋势是**风险自适应认证**——低风险场景减少验证频率，高风险场景强化验证，在安全性与用户体验之间寻找动态平衡。

零信任的最大误区是将其视为**产品购买清单**（买XDR、买CASB、买ZTNA）。真正的零信任是**组织变革**：打破网络团队与安全团队的墙，建立跨职能的零信任治理委员会，重新定义"内部"与"外部"的概念边界。这是康威定律在安全领域的又一次验证。
