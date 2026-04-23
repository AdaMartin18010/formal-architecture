# 前端安全构建：Supply Chain 与依赖审计

> **来源映射**: View/05.md §8.4
> **国际权威参考**: SLSA Framework (OpenSSF, v1.0), "Software Supply Chain Security" (NIST SP 800-204), npm audit Docs, sigstore.dev, "The State of Software Supply Chain Security" (Sonatype, 2023), "Dependency Confusion" (Alex Birsan, 2021)

---

## 一、知识体系思维导图

```text
前端安全构建：供应链与依赖审计
│
├─► 软件供应链攻击面
│   ├─ 恶意包注入: 仿冒知名包 (typosquatting)
│   ├─ 依赖混淆: 私有包名被公共仓库抢占
│   ├─ 妥协的开发者账户: 合法包被植入后门
│   ├─ 构建环境污染: CI/CD 中的恶意注入
│   ├─ 传递依赖传播: 深层依赖中的恶意代码
│   └─ Lockfile 篡改: 依赖图被恶意修改
│
├─► 依赖审计 (Dependency Audit)
│   ├─ npm audit: 基于 NPM Security Advisory DB
│   ├─ Snyk: 跨生态漏洞扫描与修复建议
│   ├─ OSV (Open Source Vulnerabilities): Google 开源漏洞库
│   ├─ Dependabot: GitHub 原生依赖安全监控
│   └─ 审计范围: 已知 CVE、许可证合规、废弃包检测
│
├─► SLSA 框架 (Supply-chain Levels for Software Artifacts)
│   ├─ Level 1: 构建过程有记录 (Provenance)
│   ├─ Level 2: 使用版本控制和托管构建服务
│   ├─ Level 3: 构建环境符合期望 (防篡改)
│   └─ Level 4: 可重现构建 + 双人审查
│
├─► 签名验证与出处
│   ├─ npm provenance: npm 包构建来源证明
│   ├─ sigstore/cosign: 基于 OIDC 的无密钥签名
│   ├─ Sigstore Rekor: 透明日志，防签名篡改
│   └─ GitHub Attestations: 工作流产物的密码学证明
│
└─► 防御策略
    ├─ 最小权限原则: 仅安装必需的依赖
    ├─ 依赖固定: lockfile + --frozen-lockfile
    ├─ 私有注册表: Nexus / Artifactory / Verdaccio
    ├─ 运行时隔离: SES / SafeDOM / ShadowRealm
    └─ SBOM: 软件物料清单 (CycloneDX / SPDX)
```

---

## 二、核心概念的形式化定义

### 2.1 软件供应链的形式化模型

```text
定义 (软件供应链):
  𝓢 = ⟨S, T, B, D, A⟩

  S = {s₁, s₂, ..., sₙ}: 源码集合
  T: 转换函数集合 (构建/编译/打包)
  B: 构建环境状态
  D: 依赖集合 (第三方包)
  A: 攻击者能力模型

  安全构建谓词:
    Secure(𝓢) ⟺ ∀t ∈ T, t(S, B, D) = t_expected(S, B_expected, D_expected)

    即: 实际构建结果等于预期构建结果

  供应链攻击:
    攻击者通过修改 S, B, D 中的任一元素，
    使得 Secure(𝓢) = false

    攻击向量:
      1. S' = S ∪ {恶意代码}          (源码污染)
      2. B' ≠ B                       (构建环境差异)
      3. D' = D ∪ {恶意包}            (依赖注入)
```

### 2.2 依赖审计的形式化

```text
定义 (依赖审计):
  设依赖图 G = (P, D, v)，漏洞数据库 VulnDB

  漏洞检测函数:
    Vulnerable: P × Version → {0, 1} × CVE_set

    Vulnerable(p, v) = (1, {cve₁, cve₂, ...})
      ⟺ ∃(p, v, cve) ∈ VulnDB

  审计结果:
    Audit(G) = {(p, v, cves) | p ∈ P, Vulnerable(p, v) = (1, cves)}

  风险评分:
    Risk(G) = Σ_{(p, v, cves) ∈ Audit(G)} Σ_{cve ∈ cves} CVSS(cve)

    CVSS: Common Vulnerability Scoring System (0-10)
```

### 2.3 SLSA 等级形式化

```text
定义 (SLSA 等级):
  SLSA 等级 L ∈ {1, 2, 3, 4} 定义了供应链的安全保证强度

  Level 1 (可追溯):
    ∃ Provenance(A): 构建产物 A 的来源文档
    Provenance 包含: 源码地址、构建命令、构建环境标识

  Level 2 (托管构建):
    源码使用版本控制 (Git)
    构建在托管服务上执行 (GitHub Actions / Cloud Build)
    构建服务生成经过认证的 Provenance

  Level 3 (防篡改):
    构建环境符合期望 (hermetic build)
    构建脚本与源码分离审查
    构建参数不可被源码影响 (isolated)

  Level 4 (最高保证):
    所有源码变更经过双人审查 (two-person review)
    构建可重现: Rebuild(S, B) = A (bit-for-bit identical)
    使用封闭构建环境，无外部网络访问
```

---

## 三、多维矩阵对比

| 维度 | npm audit | Snyk | OSV | Dependabot | Trivy |
|------|-----------|------|-----|------------|-------|
| **漏洞数据库** | NPM Advisory | 多源聚合 | Google OSV | GitHub Advisory | NVD + 多源 |
| **生态覆盖** | npm 为主 | 全栈 (npm/Maven/Go) | 多语言 | npm/PIP/Maven | 全栈 |
| **修复建议** | ✅ 自动修复命令 | ✅ 详细修复指南 | ❌ 仅检测 | ✅ PR 自动创建 | ⚠️ 基础 |
| **许可证扫描** | ❌ | ✅ | ❌ | ✅ | ✅ |
| **SBOM 生成** | ❌ | ✅ | ❌ | ❌ | ✅ |
| **CI 集成** | ⚠️ 基础 | ✅ 丰富 | ✅ API | ✅ 原生 | ✅ 丰富 |
| **误报率** | 低 | 中 | 低 | 低 | 中 |
| **成本** | 免费 |  freemium | 免费 | 免费 (GitHub) | 开源 |

### 供应链安全框架对比

| 框架 | 发布机构 | 核心关注点 | 验证方式 | 成熟度 |
|------|---------|-----------|---------|--------|
| **SLSA** | OpenSSF / Google | 构建完整性 | Provenance + 签名 | 主流标准 |
| **SSDF** | NIST | 全生命周期 | 流程合规 | 政府合规 |
| **SCVS** | OWASP | 供应链脆弱性 | 扫描 + 评估 | 新兴 |
| **COSBOM** | CISA | 关键基础设施 | SBOM + 风险评估 | 政策驱动 |

---

## 四、权威引用

> **Alex Birsan** ("Dependency Confusion", 2021):
> "I discovered that if a package with the same name exists in both the public npm registry and a private registry, the package with the higher version number wins—regardless of source. This allowed me to execute code inside Apple, Microsoft, and Tesla."

> **OpenSSF SLSA** (v1.0 Spec, 2023):
> "SLSA is a security framework, a check-list of standards and controls to prevent tampering, improve integrity, and secure packages and infrastructure."

> **NIST** (SP 800-204, "Software Supply Chain Security"):
> "Organizations should implement software supply chain security practices that ensure the integrity, authenticity, and freshness of all software components."

> **sigstore** (Official Documentation, 2023):
> "Sigstore enables developers to sign software artifacts in a way that is transparent, automated, and eliminates the need for long-lived signing keys through OIDC-based identity federation."

---

## 五、工程实践与代码示例

### 5.1 npm audit 与修复

```bash
# 审计当前项目
npm audit

# 仅查看高危漏洞
npm audit --audit-level high

# 自动修复 (仅限 semver 兼容的升级)
npm audit fix

# 强制修复 (可能引入 breaking changes)
npm audit fix --force

# 输出 JSON 格式供 CI 解析
npm audit --json
```

### 5.2 依赖固定与可重现安装

```bash
# 生产环境强制使用 lockfile
npm ci --only=production

# pnpm 严格模式
pnpm install --frozen-lockfile

# Yarn Berry 不可变安装
yarn install --immutable --immutable-cache
```

### 5.3 npm Provenance 与签名验证

```bash
# 发布带 provenance 的包
npm publish --provenance

# 验证包的 provenance
npm audit signatures

# 查看包的 provenance 信息
npm view <package-name> --json | jq '.provenance'
```

### 5.4 SBOM 生成

```bash
# 使用 CycloneDX 生成 SBOM
npx @cyclonedx/cyclonedx-npm --output-file sbom.json

# 使用 Trivy 扫描并生成 SBOM
trivy fs --format cyclonedx --output sbom.xml .

# GitHub 依赖图 (自动在仓库 Insights > Dependency graph 中展示)
```

---

## 六、批判性总结

前端安全构建的核心矛盾在于**便利性**与**安全性**的不可兼得。npm 生态的开放性和易用性是其成功的根基——任何人都可以发布包，任何项目都可以一键安装数千个依赖。但这种便利的代价是**攻击面的指数级扩张**：一个现代前端项目的传递依赖数量常超过 1000 个，每个依赖都是一个潜在的入侵点。Alex Birsan 在 2021 年展示的"依赖混淆"攻击证明，即使是最顶尖的科技公司，其构建系统也可能因包管理器的版本解析优先级逻辑而被攻破。这揭示了一个深刻的安全原理：**依赖解析算法的语义本身就是攻击面**。

SLSA 框架将供应链安全从模糊的最佳实践提升为**可度量的等级体系**，其 Level 4 要求的"可重现构建"（Reproducible Build）是密码学意义上的强保证——构建产物的比特级一致性消除了构建环境被篡改的可能性。但在前端领域，可重现构建几乎是不可能的：npm 包的安装过程依赖于网络请求、环境变量和操作系统语义，这些因素在两次构建之间几乎不可能完全一致。这要求前端工程系统重新思考安全模型：与其追求绝对的可重现性，不如通过**出处证明（Provenance）**和**透明日志（Transparency Log）**实现攻击的**可检测性**——sigstore 的 Rekor 正是这一思想的实现。

更深层的挑战在于**传递信任的衰减**。当项目 A 依赖 B，B 依赖 C，C 依赖 D 时，A 的开发者在不知不觉中信任了 D 的维护者。这种信任链的长度与前端项目的依赖深度成正比，而当前的工具链（npm audit, Snyk）只能检测**已知的**漏洞，对**零日漏洞**和**恶意维护者**（如 2022 年的 colors.js 和 node-ipc 事件）无能为力。根本性的解决方案可能需要**运行时隔离**——通过 SES (Secure ECMAScript) 或 WebAssembly 的 capabilities 模型，将第三方代码的执行限制在最小权限沙箱中，使供应链攻击的影响局部化。这是前端安全从"构建时审计"向"运行时隔离"的范式迁移。


---

## 七、概念属性关系网络

```text
前端安全构建概念属性关系网络
│
├─► 核心实体层
│   ├─ [软件供应链 𝓢 = ⟨S, T, B, D, A⟩]
│   │   ├─ S ──→ 属性: {源码完整性, 签名状态, 审查记录}
│   │   ├─ T ──→ 属性: {构建函数, 可重现性, 确定性}
│   │   ├─ B ──→ 属性: {环境标识, 隔离级别, 网络访问}
│   │   ├─ D ──→ 属性: {依赖来源, 版本锁定, 漏洞状态}
│   │   └─ A ──→ 属性: {攻击向量, 能力模型, 目标价值}
│   │
│   ├─ [依赖图 G = (P, D, v)]
│   │   ├─ P ──→ 属性: {包名, 维护者身份, 下载量, 更新时间}
│   │   ├─ D ──→ 属性: {直接依赖, 传递依赖, 开发依赖}
│   │   └─ v ──→ 属性: {SemVer, 发布来源, Provenance证明}
│   │
│   └─ [审计函数 Audit: G → RiskScore]
│       ├─ 输入 ──→ 属性: {漏洞数据库, 许可证策略, SBOM}
│       └─ 输出 ──→ 属性: {CVE列表, CVSS评分, 修复建议}
│
├─► 关系映射层
│   ├─ 𝓢 → Secure: 安全构建谓词评估整个供应链
│   ├─ G → Audit: 依赖图输入到审计函数
│   ├─ Audit → SLSA: 审计结果映射到 SLSA 等级
│   ├─ SLSA → Provenance: 等级要求决定出处证明强度
│   └─ D → sigstore: 依赖包通过 Rekor 透明日志验证
│
├─► 属性约束层
│   ├─ 安全构建: Secure(𝓢) ⟺ ∀t∈T, t(S,B,D) = t_expected(S,B_expected,D_expected)
│   ├─ 可重现性: Rebuild(S,B) = A (bit-for-bit identical, SLSA L4)
│   ├─ 审计覆盖: ∀p∈P, Vulnerable(p,v) 可判定
│   ├─ 信任传递: 若 p 依赖 q，则 Trust(p) ⟹ Trust(q) (传递信任衰减)
│   └─ 最小权限: 运行时隔离 ⟹ 第三方代码权限 ⊆ 最小必要集合
│
└─► 课程对齐层
    ├─ MIT 6.170 (Daniel Jackson): 安全与模块化设计
    ├─ Stanford CS 142 (Mendel Rosenblum): Web应用安全基础
    └─ CMU 17-313: 软件工程中的安全与隐私
```

---

## 八、形式化推理链

**推理命题 P**: 前端供应链安全的根本挑战在于传递信任的指数级衰减——当依赖深度 d 增加时，攻击面呈指数增长，而现有审计工具只能检测已知漏洞，无法防御零日攻击和恶意维护者。

**推理链**:

```text
前提 A1 (Alex Birsan, 2021): "I discovered that if a package with the same name exists
                                in both the public npm registry and a private registry,
                                the package with the higher version number wins—regardless
                                of source. This allowed me to execute code inside Apple,
                                Microsoft, and Tesla."
前提 A2 (OpenSSF SLSA, 2023): "SLSA is a security framework to prevent tampering,
                                improve integrity, and secure packages and infrastructure."
前提 A3 (sigstore, 2023): "Sigstore enables developers to sign software artifacts in a
                            way that is transparent, automated, and eliminates the need
                            for long-lived signing keys through OIDC-based identity
                            federation."

步骤 1: 由 A1，依赖解析算法的语义本身是攻击面
       设包管理器的版本选择策略为:
         Select(pkg) = argmax_{version} version  (满足约束的最高版本)
       若攻击者在公共仓库发布同名包的更高版本:
         v_malicious > v_private ⟹ Select(pkg) = v_malicious
       形式化: 版本选择函数的单调性假设 (更高版本 = 更新 = 更好) 被攻击者利用
       ∴ 依赖解析算法的设计缺陷导致了"依赖混淆"攻击

步骤 2: 由 A2，SLSA 框架将供应链安全等级化
       SLSA 等级 L ∈ {1,2,3,4} 定义了递进的安全保证:
         L1: ∃ Provenance(A) (可追溯)
         L2: 托管构建 + 版本控制 (可验证)
         L3: 构建环境防篡改 + 隔离 (可信任)
         L4: 双人审查 + 可重现构建 (最高保证)
       形式化: SLSA 等级构成了安全保证的格 (Lattice) 结构
         L4 ⟹ L3 ⟹ L2 ⟹ L1 (单调递增)

步骤 3: 传递信任的衰减模型
       设项目 A 的依赖深度为 d，每层依赖的平均包数为 b (分支因子)
       传递依赖总数: |Transitive| = Σᵢ₌₁ᵈ bⁱ ≈ b^{d+1}/(b-1)
       信任链长度 = d，信任衰减: Trust(d) = Trust₀ × αᵈ (α < 1)
       现代前端项目典型值: d ≈ 5-10, b ≈ 3-5
       ∴ |Transitive| 常达 1000-5000 个包
       攻击面 = 所有传递依赖的并集，与依赖深度指数相关

步骤 4: 由 A3，签名验证与透明日志的防御模型
       sigstore/cosign 提供基于 OIDC 的无密钥签名
       Rekor 透明日志保证签名的不可篡改性
       npm provenance 将构建来源与包绑定
       形式化: 这些机制将"信任某个人"转化为"信任某个可验证的过程"
       但局限: 只能验证"谁构建了包"，不能验证"构建的代码是否恶意"
       (2022 年 colors.js 和 node-ipc 事件: 合法维护者植入恶意代码)

步骤 5: 根本矛盾的数学表达
       设安全事件为随机变量 X，P(X) 为供应链被攻破的概率
       P(X) = 1 - Πᵢ (1 - P(xᵢ))  (各依赖独立假设)
       当 |Transitive| → ∞ 时，P(X) → 1 (必然性定理)
       ∴ 绝对安全不可达，只能降低 P(X) 并提高检测速度

结论: 前端供应链安全是一个"深度与概率"的博弈。依赖深度决定了攻击面的理论上限，
       SLSA/sigstore 等机制通过提高单点安全性降低每层风险，但无法打破指数增长。
       根本解决方案需要运行时隔离——通过 SES/ShadowRealm 将第三方代码限制在
       最小权限沙箱，使攻破的影响局部化。这是从"构建时审计"向"运行时隔离"
       的范式迁移。
```

---

## 九、推理判定树/决策树

```text
供应链安全策略决策树
│
├─► Q1: 项目性质?
│   ├─ 开源库 (被他人依赖) ──→ 继续 Q2
│   └─ 内部/商业应用 ──→ 继续 Q3
│
├─► Q2: 开源库安全等级?
│   ├─ 基础: npm publish --provenance + 启用 2FA
│   ├─ 中级: SLSA Level 2 (GitHub Actions 托管构建 + 签名)
│   └─ 高级: SLSA Level 3+ (封闭构建环境 + sigstore 签名)
│
├─► Q3: 应用部署环境?
│   ├─ 面向公众 (高价值目标) ──→ 继续 Q4
│   └─ 内部工具 (低风险) ──→ 基础审计 + lockfile 固定
│
├─► Q4: 现有安全基线?
│   ├─ 无 ──→ 立即启用: npm audit + lockfile + --frozen-lockfile
│   └─ 有基础审计 ──→ 继续 Q5
│
├─► Q5: 高级防御需求?
│   ├─ 依赖混淆防护 ──→ 私有注册表 (Verdaccio/Nexus) + 命名空间隔离
│   ├─ 零日漏洞缓解 ──→ SBOM (CycloneDX/SPDX) + 运行时监控
│   └─ 恶意包隔离 ──→ SES / ShadowRealm / WebAssembly capabilities
│
└─► Q6: CI/CD 集成?
    ├─ GitHub Actions ──→ npm audit signatures + SLSA GitHub Generator
    ├─ 其他 CI ──→ Snyk/Trivy 扫描 + sigstore cosign 签名
    └─ 自研流水线 ──→ 私有 Rekor 实例 + 自定义 provenance 验证

依赖漏洞响应决策树
│
├─► Q1: npm audit 发现漏洞?
│   ├─ 否 ──→ 定期审计 (建议每次 CI 运行)
│   └─ 是 ──→ 继续 Q2
│
├─► Q2: 漏洞严重程度?
│   ├─ Critical/High ──→ 立即评估影响，准备热修复
│   ├─ Moderate ──→ 计划在下个迭代修复
│   └─ Low ──→ 监控，低优先级
│
├─► Q3: 是否存在可用修复?
│   ├─ 是 (semver 兼容升级) ──→ npm audit fix 或手动升级
│   └─ 否 (major 升级或无人维护) ──→ 继续 Q4
│
├─► Q4: 漏洞是否在传递依赖中?
│   ├─ 是 ──→ 尝试 overrides/resolutions 强制升级，或寻找替代包
│   └─ 否 ──→ 评估自行修复可行性，或联系维护者
│
└─► Q5: 临时缓解措施?
    ├─ 运行时隔离受影响代码路径
    ├─ WAF/防火墙规则阻断攻击向量
    └─ 监控日志检测异常行为
```

---

## 十、国际课程对齐标注

> **📚 MIT 6.170 Software Studio** (Daniel Jackson)
>
> - **对齐章节**: §2.1 软件供应链的形式化模型, §2.3 SLSA 等级形式化
> - **课程要点**: "Software engineering with an emphasis on design.
>   Topics include security in web applications."
> - **深度映射**: MIT 6.170 的安全模块涵盖 Web 应用的基础安全实践。本文件将安全
>   从应用层扩展到供应链层，将软件供应链建模为五元组 𝓢 = ⟨S, T, B, D, A⟩，
>   这是 Daniel Jackson "概念设计"方法在安全领域的应用——将复杂的供应链攻击面
>   分解为源码、构建、环境、依赖、攻击者五个可独立分析的概念。课程中关于
>   "模块化降低风险"的论述与本文件"运行时隔离"的防御策略同构。

> **📚 Stanford CS 142 Web Applications** (Mendel Rosenblum)
>
> - **对齐章节**: §一 知识体系思维导图 (安全构建层), §5.1 npm audit 与修复
> - **课程要点**: "Web application security: sessions, validation, and safe coding practices."
> - **深度映射**: CS142 在 Session State and Validation 模块中讨论 Web 安全基础。
>   本文件将安全视角从"应用代码"下推到"依赖代码"——现代前端应用 90%+ 的代码
>   来自第三方，供应链安全已成为比 XSS/CSRF 更紧迫的风险。课程中 npm 的使用
>   经验直接关联本文件的 npm audit、lockfile 完整性等实践工具。

> **📚 CMU 17-313 Foundations of Software Engineering**
>
> - **对齐章节**: §2.2 依赖审计的形式化, §六 批判性总结, §5.4 SBOM 生成
> - **课程要点**: "Security, privacy, and open source dependencies as core software
>   engineering concerns."
> - **深度映射**: CMU 17-313 在 Security 和 Open Source II - Dependencies 模块中明确
>   将供应链安全纳入软件工程核心议题。本文件的风险评分模型
>   Risk(G) = Σ CVSS(cve) 为 17-313 中"量化安全风险"的需求提供了形式化工具。
>   课程中关于"依赖管理"的讨论（Recitation 9/10）与本文件 SLSA 框架的等级化
>   安全保证直接对应——两者都强调"安全不是二元属性，而是可度量的连续谱"。
