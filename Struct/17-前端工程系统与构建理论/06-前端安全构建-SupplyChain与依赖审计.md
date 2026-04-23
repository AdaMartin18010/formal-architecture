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
