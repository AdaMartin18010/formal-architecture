# CI/CD 流水线：持续集成与持续交付

> **来源映射**: View/00.md §3.1, 模块27总览
> **国际权威参考**: "Continuous Delivery" (Jez Humble & David Farley, 2010), "Accelerate" (Forsgren et al., 2018), "DevOps Handbook" (Kim et al., 2016)

---

## 一、知识体系思维导图

```text
CI/CD 流水线
│
├─► 分支策略 (Branching Strategy)
│   ├─► GitFlow
│   │   ├─ master: 生产分支
│   │   ├─ develop: 集成分支
│   │   ├─ feature/*: 功能分支
│   │   ├─ release/*: 预发布分支
│   │   └─ hotfix/*: 紧急修复分支
│   ├─► GitHub Flow
│   │   ├─ 仅 master + feature 分支
│   │   └─ Pull Request 即代码审查门户
│   └─► Trunk-Based Development
│       ├─ 主干开发，短周期分支 (<1天)
│       └─ Feature Toggle 替代长周期分支
│
├─► 质量门禁 (Quality Gates)
│   ├─ 编译检查: 语法、依赖、构建产物
│   ├─ 静态分析: SonarQube、Checkstyle、ESLint
│   ├─ 单元测试: 覆盖率阈值 (通常 ≥80%)
│   ├─ 集成测试: API 契约、数据库迁移
│   ├─ 安全扫描: SAST (源码)、SCA (依赖)、DAST (运行时)
│   └─ 性能基线: 回归测试、负载阈值
│
├─► DORA 指标 (Four Key Metrics)
│   ├─ 部署频率 (Deployment Frequency)
│   ├─ 变更前置时间 (Lead Time for Changes)
│   ├─ 恢复服务时间 (Time to Restore Service)
│   └─ 变更失败率 (Change Failure Rate)
│
└─► 流水线即代码 (Pipeline as Code)
    ├─ Jenkins Pipeline (Groovy DSL)
    ├─ GitHub Actions (YAML)
    ├─ GitLab CI/CD (.gitlab-ci.yml)
    ├─ Tekton (Kubernetes-native)
    └─ 基础设施: Runner、Agent、Executor
```

---

## 二、核心概念的形式化定义

```text
定义 (持续交付流水线):
  设流水线 P 为一个有向无环图 P = (S, E)，其中:
    S = {s₁, s₂, ..., sₙ} 为阶段集合
    E ⊆ S × S 为阶段间依赖关系
    ∀sᵢ ∈ S, 存在状态函数 state(sᵢ) ∈ {Pending, Running, Success, Failed}

  质量门禁 (Quality Gate):
    Q(sᵢ) = ∧ⱼ metricⱼ(sᵢ) ≥ thresholdⱼ
    若 Q(sᵢ) = False，则 ∀(sᵢ, sₖ) ∈ E, state(sₖ) = Blocked

定义 (DORA 指标):
  设时间区间 T = [t₀, t₁]，部署集合 D = {d₁, d₂, ..., dₘ}:

  部署频率:     f_deploy = |D| / |T|
  变更前置时间: LT = median({t_deploy - t_commit | ∀d ∈ D})
  恢复时间:     MTTR = median({t_recover - t_failure | ∀failure})
  变更失败率:   CFR = |{d ∈ D | d 导致故障}| / |D|

  DORA 绩效分层:
    精英 (Elite):     f_deploy ≥ 1/天, LT < 1h, MTTR < 1h, CFR < 5%
    高绩效 (High):    f_deploy ≥ 1/周, LT < 1周, MTTR < 1天, CFR < 15%
    中等 (Medium):    f_deploy ≥ 1/月, LT < 1月, MTTR < 1周, CFR < 30%
    低绩效 (Low):     f_deploy < 1/月, LT > 1月, MTTR > 1周, CFR > 45%
```

---

## 三、多维矩阵对比

| 维度 | GitFlow | GitHub Flow | Trunk-Based | GitLab Flow |
|------|---------|-------------|-------------|-------------|
| **分支数量** | 5+ 类型 | 2 (master + feature) | 1 (主干) | 3+ (含环境分支) |
| **发布周期** | 周/月 | 天 | 天/小时 | 周 |
| **团队规模** | 大型、多版本并行 | 中小型、SaaS | 大型、高频发布 | 中大型企业 |
| **复杂度** | 高 | 低 | 中 | 中 |
| **回滚能力** | 分支回退 | Revert PR | Toggle 关闭 | 环境分支回退 |
| **代表企业** | 传统软件厂商 | GitHub、SaaS 初创 | Google、Meta、Netflix | GitLab 用户 |

| 工具 | 语法 | 执行环境 | 云原生 | 社区生态 |
|------|------|---------|--------|---------|
| **Jenkins Pipeline** | Groovy | 自托管 Agent | 需插件 | 最成熟 |
| **GitHub Actions** | YAML | GitHub 托管/自托管 | 原生支持 | 市场丰富 |
| **GitLab CI** | YAML | GitLab Runner | 原生支持 | 集成度高 |
| **Tekton** | YAML | Kubernetes Pod | Kubernetes 原生 | CNCF 孵化 |
| **CircleCI** | YAML | 托管/自托管 | 原生支持 | 配置简洁 |

---

## 四、权威引用

> **Jez Humble** ("Continuous Delivery", 2010):
> "If it hurts, do it more frequently, and bring the pain forward. The magic of continuous delivery is that it forces you to address the pain points in your delivery process."

> **Nicole Forsgren et al.** ("Accelerate", 2018, Chapter 2):
> "We found that software delivery performance is not about tradeoffs between speed and stability. High performers achieve both."

> **Martin Fowler** ("Patterns for Managing Source Code Branches", 2020):
> "The essence of Trunk-Based Development is that all developers commit to a single shared branch (trunk) at least once per day."

> **Google SRE Book** (Beyer et al., 2016):
> "A service is not truly reliable until it can be deployed automatically, rolled back quickly, and monitored comprehensively."

---

## 五、工程实践与代码示例

```yaml
# GitHub Actions 示例: 多阶段质量门禁
name: CI Pipeline with Quality Gates
on: [push, pull_request]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Static Analysis
        run: |
          sonar-scanner \
            -Dsonar.projectKey=myapp \
            -Dsonar.qualitygate.wait=true

      - name: Unit Tests with Coverage Gate
        run: |
          pytest --cov=src --cov-report=xml
          # 质量门禁: 覆盖率 ≥ 80%
          coverage report --fail-under=80

      - name: Integration Tests
        run: pytest tests/integration/

      - name: Security Scan (SCA)
        run: snyk test --severity-threshold=high

      - name: Build Artifact
        run: docker build -t myapp:${{ github.sha }} .
```

---

## 六、批判性总结

CI/CD 的核心悖论在于：工具链的自动化程度与组织文化的成熟度往往不成正比。许多企业投入巨资构建 Jenkins/Tekton 流水线，却在"质量门禁"环节妥协——将覆盖率阈值从 80% 下调至 60%，甚至允许安全扫描告警继续部署。这种"自动化了错误的事情"比手动部署更具危害性，因为它以技术的确定性掩盖了质量的虚假安全感。

DORA 指标的深层价值不在于数字本身，而在于它揭示了**软件交付是一个可度量、可改进的系统**。精英团队并非天生如此，而是通过持续缩小"变更提交到生产部署"的反馈环（通常 < 1 小时），将大问题分解为可快速回滚的小变更。Trunk-Based Development 是这一理念的最优工程实践：它强制团队将功能拆分为小粒度变更，用 Feature Toggle 替代长周期分支，从根本上消除了"集成地狱"。然而，这一模式要求极高的自动化测试覆盖率和成熟的工程文化，对遗留系统团队而言转型成本极高。流水线的终极形态不是更复杂的 YAML，而是"提交即部署"的无感体验——开发者专注于业务逻辑，交付的摩擦降为零。
