# 认证与授权：OAuth 2.0、OIDC 与 JWT

> **来源映射**: View/02.md §7, View/09.md
> **国际权威参考**: RFC 6749 (OAuth 2.0), RFC 7519 (JWT), OpenID Connect Core 1.0, NIST SP 800-63 (Digital Identity Guidelines)

---

## 一、知识体系思维导图

```text
认证与授权体系
│
├─► 认证 (Authentication) — 证明"你是谁"
│   ├─ 知识因素: 密码 (bcrypt/Argon2 慢哈希存储)
│   ├─ 持有因素: TOTP/HOTP (基于时间/计数器的一次性密码)
│   ├─ 生物因素: 指纹、面部识别、虹膜
│   ├─ 多因素认证 (MFA): 2FA / 3FA
│   │   └─ 风险: SIM 卡交换攻击 (SMS 2FA 被 NIST 不推荐)
│   └─ 无密码 (Passwordless): FIDO2 / WebAuthn / Passkeys
│
├─► 单点登录 (SSO)
│   ├─ SAML 2.0: 企业级, XML 断言, 较重
│   ├─ OAuth 2.0 + OIDC: 现代 Web/移动端标准
│   └─ Kerberos: 内网/Windows 域环境
│
├─► OAuth 2.0 授权框架
│   ├─ 角色: Resource Owner, Client, Authorization Server, Resource Server
│   ├─ 授权流程
│   │   ├─ Authorization Code: 服务端应用 (最安全, PKCE 扩展)
│   │   ├─ Implicit: 已废弃 (SPA 历史方案)
│   │   ├─ Password Credentials: 已废弃 (信任客户端场景)
│   │   └─ Client Credentials: 机器对机器 (M2M)
│   ├─ PKCE (RFC 7636): 授权码流程的防拦截保护
│   ├─ 令牌: Access Token (短期) + Refresh Token (长期)
│   └─ Scope: 权限范围的显式声明
│
├─► OpenID Connect (OIDC)
│   ├─ 基于 OAuth 2.0 的身份层
│   ├─ ID Token: JWT 格式的用户身份信息
│   ├─ UserInfo Endpoint: 获取额外用户属性
│   ├─ 标准 Scope: openid, profile, email, address
│   └─ 会话管理: 前端/后端渠道注销
│
├─► JWT (JSON Web Token)
│   ├─ 结构: Header.Payload.Signature (Base64Url)
│   ├─ 签名算法
│   │   ├─ HS256: HMAC-SHA256 (对称密钥)
│   │   ├─ RS256: RSA-SHA256 (非对称, 私钥签公钥验)
│   │   └─ ES256: ECDSA-SHA256 (非对称, 更短签名)
│   ├─ 风险: 泄露即授权、无法服务端撤销、Payload 膨胀
│   └─ 最佳实践: 短期过期、使用 RS256/ES256、不存敏感信息
│
└─► 授权模型 (Authorization)
    ├─ RBAC: 基于角色的访问控制 (Role-Based)
    ├─ ABAC: 基于属性的访问控制 (Attribute-Based)
    ├─ ReBAC: 基于关系的访问控制 (Google Zanzibar)
    └─ PBAC: 基于策略的访问控制 (OPA/Cedar)
```

---

## 二、核心概念的形式化定义

### 2.1 OAuth 2.0 授权码流程

```text
定义 (OAuth 2.0 Authorization Code Flow with PKCE):
  参与者:
    U: Resource Owner (用户)
    C: Client (应用)
    AS: Authorization Server (认证服务器)
    RS: Resource Server (资源服务器)

  PKCE 参数生成 (客户端):
    code_verifier = random_string(43-128 chars)
    code_challenge = BASE64URL(SHA256(code_verifier))
    code_challenge_method = "S256"

  流程:
    1. C → U (浏览器): 引导至 AS 授权端点
       GET /authorize?response_type=code
         &client_id={client_id}
         &redirect_uri={uri}
         &scope={scopes}
         &state={random_state}
         &code_challenge={challenge}
         &code_challenge_method=S256

    2. U → AS: 认证并授权

    3. AS → C (重定向): 授权码 + state
       redirect_uri?code={auth_code}&state={state}

    4. C → AS: 用授权码换取令牌
       POST /token
       grant_type=authorization_code
       &code={auth_code}
       &redirect_uri={uri}
       &client_id={id}
       &client_secret={secret}  (或不用, 对于 Public Client)
       &code_verifier={verifier}

    5. AS → C: Access Token + Refresh Token + ID Token (OIDC)

    6. C → RS: 用 Access Token 访问受保护资源
       Authorization: Bearer {access_token}
```

### 2.2 JWT 结构形式化

```text
定义 (JWT):
  JWT = Base64Url(Header) || "." || Base64Url(Payload) || "." || Base64Url(Signature)

  Header = {"alg": "RS256", "typ": "JWT", "kid": "key-id"}

  Payload (Claims):
    iss (Issuer): 签发者
    sub (Subject): 主体标识 (用户ID)
    aud (Audience): 受众
    exp (Expiration Time): 过期时间 (Unix 时间戳)
    iat (Issued At): 签发时间
    nbf (Not Before): 生效时间
    jti (JWT ID): 唯一标识 (用于防止重放)

  Signature (RS256):
    Sign = RSA-SHA256( Base64Url(Header) || "." || Base64Url(Payload), PrivateKey )
    Verify = RSA-SHA256-Verify( Sign, Base64Url(Header) || "." || Base64Url(Payload), PublicKey )

  安全约束:
    - 必须验证签名 (防止篡改)
    - 必须验证 exp (防止过期令牌重用)
    - 必须验证 iss 和 aud (防止跨服务令牌滥用)
    - alg = "none" 攻击: 强制拒绝无签名 JWT
```

### 2.3 授权模型对比

```text
定义 (RBAC):
  Access(u, r) ↔ ∃ role ∈ Roles(u): Permission(role, r)

  结构: 用户 → 角色 → 权限 → 资源
  优点: 简单、直观、易于审计
  缺点: 粗粒度、角色爆炸 (Role Explosion)、上下文无关

definition (ABAC):
  Access(u, r) ↔ Policy( Attributes(u), Attributes(r), Attributes(env) ) = Permit

  结构: 策略规则评估主体/资源/环境属性
  优点: 细粒度、上下文感知、灵活
  缺点: 策略复杂度、性能开销、调试困难

definition (ReBAC / Zanzibar):
  Access(u, r) ↔ ∃ path: u →* r in Relation Graph

  结构: 用户与资源的关系有向图
  优点: 表达力强 (继承、组嵌套)、适合社交/协作场景
  缺点: 图查询性能、一致性模型复杂
```

---

## 三、多维矩阵对比

| 维度 | OAuth 2.0 | OIDC | SAML 2.0 | API Key | mTLS |
|------|-----------|------|----------|---------|------|
| **主要目的** | 授权 (Delegation) | 认证 (Identity) | 认证+授权 | 认证 | 认证 |
| **令牌格式** | 不透明/自包含 | JWT (ID Token) | XML 断言 | 随机字符串 | X.509 证书 |
| **浏览器流程** | ✅ 是 | ✅ 是 | ✅ 是 | ⚠️ 有限 | ❌ 否 |
| **移动端支持** | ✅ 原生 | ✅ 原生 | ⚠️ 复杂 | ✅ | ⚠️ 困难 |
| **M2M 支持** | ✅ Client Credentials | ⚠️ 有限 | ❌ 差 | ✅ | ✅ 最佳 |
| **用户属性** | ❌ 需额外调用 | ✅ UserInfo | ✅ 断言内 | ❌ 无 | ❌ 无 |
| **注销机制** | ⚠️ 令牌自然过期 | ✅ 前后端渠道 | ✅ SLO | ❌ 删除 Key | ❌ 吊销证书 |
| **实现复杂度** | 中 | 中 | 高 | 低 | 高 |
| **2026 趋势** | 标准标配 | 标准标配 | 企业遗留 | 内部 API | 服务网格 |

---

## 四、权威引用

> **Eran Hammer** (OAuth 2.0 原作者, 曾声明退出):
> "OAuth 2.0 is a framework, not a protocol. It provides too many options and places too much burden on implementers." —— 这解释了为何 PKCE 和 Security BCP 后续成为强制要求。

> **Dick Hardt** (Identity 2.0 运动推动者):
> "Identity is not a protocol problem; it's a user experience problem."

> **NIST SP 800-63B** (Digital Identity Guidelines):
> "Verifiers SHALL NOT accept passwords that have been compromised in a known data breach." —— 推动密码黑名单和 Have I Been Pwned 集成。

> **Google Zanzibar** (USENIX ATC 2019, "Zanzibar: Google's Consistent, Global Authorization System"):
> "ReBAC provides a uniform data model for authorization that captures RBAC and ABAC as special cases."

---

## 五、工程实践与代码示例

### 5.1 JWT 验证中间件 (Node.js)

```javascript
const jwt = require('jsonwebtoken');
const jwksClient = require('jwks-rsa');

const client = jwksClient({
  jwksUri: 'https://auth.example.com/.well-known/jwks.json'
});

function getKey(header, callback) {
  client.getSigningKey(header.kid, (err, key) => {
    callback(null, key.getPublicKey());
  });
}

function verifyToken(token) {
  return new Promise((resolve, reject) => {
    jwt.verify(token, getKey, {
      algorithms: ['RS256'],      // 强制算法，防止 alg=none 攻击
      issuer: 'https://auth.example.com',
      audience: 'my-api',
      clockTolerance: 30          // 30 秒时钟偏移容忍
    }, (err, decoded) => {
      if (err) reject(err);
      else resolve(decoded);
    });
  });
}
```

### 5.2 OAuth 2.0 + PKCE 授权 URL 生成

```javascript
function generatePKCE() {
  const verifier = base64URLEncode(crypto.randomBytes(32));
  const challenge = base64URLEncode(
    crypto.createHash('sha256').update(verifier).digest()
  );
  return { verifier, challenge };
}

// 构建授权 URL
const { verifier, challenge } = generatePKCE();
sessionStorage.setItem('pkce_verifier', verifier);
sessionStorage.setItem('oauth_state', randomState);

const authUrl = new URL('https://auth.example.com/oauth/authorize');
authUrl.searchParams.set('response_type', 'code');
authUrl.searchParams.set('client_id', CLIENT_ID);
authUrl.searchParams.set('redirect_uri', REDIRECT_URI);
authUrl.searchParams.set('scope', 'openid profile email');
authUrl.searchParams.set('state', randomState);
authUrl.searchParams.set('code_challenge', challenge);
authUrl.searchParams.set('code_challenge_method', 'S256');
```

---

## 六、批判性总结

JWT 的广泛滥用是 2020 年代应用安全领域最深刻的教训之一。开发者被"无状态认证"的便利性诱惑，将 JWT 用于长时间会话（设置数小时甚至数天的过期时间），却忽视了**JWT 无法服务端撤销**的本质。一旦令牌泄露（通过 XSS、日志泄露或网络嗅探），攻击者在令牌过期前拥有完全权限。Refresh Token 模式虽然缩短了 Access Token 的有效期，但 Refresh Token 本身仍是长期凭证——其安全存储在浏览器端几乎不可能（localStorage 易受 XSS，httpOnly Cookie 无法用于跨域 SPA）。

OAuth 2.0 的"框架而非协议"特性导致早期实现漏洞百出：缺少 PKCE 的授权码流程在公开客户端中可被拦截攻击，`response_mode=fragment` 在 SPA 中的回调处理不当导致令牌泄露，Scope 的动态降级被多数实现忽略。OAuth 2.1 正在努力收紧这些选项，但历史包袱沉重。

ReBAC（以 Google Zanzibar 为代表）代表了授权模型的未来方向：它将 RBAC 的角色继承和 ABAC 的上下文感知统一为关系图查询。但 Zanzibar 的实现复杂度（需要支持数十亿关系元组的全局一致性存储）使其仅适用于超大规模场景。对于大多数企业，**OPA (Open Policy Agent) + RBAC 基础 + ABAC 扩展**仍是务实的折中方案。安全架构的核心真理是：**没有完美的安全模型，只有与威胁模型和组织能力匹配的安全投入**。

---

## 七、概念属性关系网络

### 7.1 核心概念依赖/包含/对立关系表

| 概念A | 关系 | 概念B | 关系说明 |
|-------|------|-------|----------|
| 认证 (Authentication) | 前置依赖 | 授权 (Authorization) | 必须先确定"你是谁"，再决定"你能做什么" |
| OAuth 2.0 | 包含扩展 | OIDC | OIDC在OAuth 2.0之上增加身份层 (ID Token) |
| OAuth 2.0 | 依赖 | TLS 1.2+ | RFC 6749强制要求授权端点使用TLS |
| JWT | 实现载体 | OIDC / OAuth | JWT是ID Token和Access Token的格式之一 |
| HS256 | 对立风险 | RS256/ES256 | HS256共享密钥泄露风险高；RS256使用非对称密钥更安全 |
| RBAC | 被包含于 | ReBAC (Zanzibar) | Zanzibar证明RBAC可表示为关系图的子结构 |
| PKCE | 安全增强 | Authorization Code | PKCE将公开客户端的授权码流程从"不安全"提升为"推荐" |
| Refresh Token | 对立风险 | Access Token | Refresh Token长期有效但存储要求高；Access Token短期但无状态 |

### 7.2 ASCII拓扑图

```text
身份与访问管理 (IAM)
│
├─► 认证层 ─────────────────────────────┐
│   ├─ 知识因素: 密码 (bcrypt/Argon2)   │
│   ├─ 持有因素: TOTP/HOTP              │──► 多因素聚合
│   ├─ 生物因素: 指纹/面部              │    MFA → 信任提升
│   └─ 无密码: FIDO2/WebAuthn/Passkeys  │
│                                       │
├─► 联邦认证层 ◄────────────────────────┘
│   ├─ SAML 2.0 ──► 企业级XML断言
│   ├─ OAuth 2.0 ──► 授权委托框架
│   │      ├─ Authorization Code (+PKCE)
│   │      ├─ Client Credentials (M2M)
│   │      └─ Device Code (IoT/TV)
│   ├─ OIDC ───────► OAuth 2.0 + 身份层
│   │      ├─ ID Token (JWT)
│   │      ├─ UserInfo Endpoint
│   │      └─ 标准Claims (openid, profile, email)
│   └─ Kerberos ──► 内网/Windows域
│
├─► 令牌层
│   ├─ JWT ──► 自包含声明 (Header.Payload.Signature)
│   │     ├─ HS256 (HMAC-SHA256, 对称)
│   │     ├─ RS256 (RSA-SHA256, 非对称)
│   │     └─ ES256 (ECDSA-SHA256, 非对称)
│   └─ 不透明令牌 ──► 引用令牌 (需Introspection)
│
└─► 授权决策层
    ├─ RBAC ──► 角色 → 权限 (粗粒度)
    ├─ ABAC ──► 属性策略评估 (细粒度)
    ├─ ReBAC ──► 关系图查询 (Zanzibar)
    └─ PBAC ──► 策略即代码 (OPA/Cedar)
```

### 7.3 形式化映射

```text
认证与授权的形式化层级:

L0 (集合论): 用户集 U, 角色集 R, 权限集 P, 关系 ⊆ U × R × P
L1 (谓词逻辑): RBAC — ∀u∈U, ∀r∈Resource: Access(u,r) ↔ ∃role∈Roles(u): Permission(role,r)
L2 (属性逻辑): ABAC — Access(u,r) ↔ Policy(Attributes(u), Attributes(r), Attributes(env)) = Permit
L3 (图论): ReBAC — Access(u,r) ↔ ∃path: u →* r in Relation Graph G
L4 (协议逻辑): OAuth 2.0 — ◇(Client ⊢ AS: authorize_request) → ◇(AS ⊢ Client: access_token)
L5 (时序逻辑): Refresh Token — □(refresh_token_valid(t) → ◇(access_token_issued(t+Δ)))
```

---

## 八、形式化推理链

### 8.1 公理 → 引理 → 定理 → 推论

**公理A1** (Kerckhoffs, 1883 — 柯克霍夫原则):
> 密码系统的安全性应仅依赖于密钥的保密性，而非算法的保密性。

**公理A2** (OAuth 2.0威胁模型, RFC 6819, Jones & Hardt, 2015):
> 授权码在传输过程中可能被拦截；公开客户端无法安全存储client_secret。

**引理L1** (PKCE安全增强, Sakimura et al., 2015 — RFC 7636):
> 若客户端生成随机code_verifier并通过公开信道发送code_challenge = SHA256(verifier)，
> 则攻击者即使拦截授权码，也无法换取令牌（因缺乏verifier）。

形式化: ∀ adversary A, 若 A 拦截 auth_code 但不知道 code_verifier:
       Pr[A 换取 access_token] ≤ negl(|code_verifier|)

**引理L2** (JWT签名验证必要性, Jones et al., 2015 — RFC 7519):
> 未验证签名的JWT等同于明文授权凭证；alg="none"攻击可完全绕过认证。

**定理T1** (Fett et al., 2016 — IEEE S&P):
> 在Dolev-Yao攻击者模型下，OAuth 2.0 Authorization Code Flow with PKCE
> 满足会话密钥的保密性和身份认证性，前提是:
> (1) TLS通道完整; (2) AS的私钥保密; (3) code_verifier熵足够。

**定理T2** (Zanzibar表达能力, Google, 2019 — USENIX ATC):
> ReBAC关系代数可表达任意RBAC和ABAC策略。
> 证明要点: Role ⊆ RelationType; Attribute ⊆ Tuple(subject, predicate, object, context)。

**推论C1**:
> 在浏览器环境中，Authorization Code + PKCE 是唯一安全的OAuth 2.0流程；
> Implicit流程和Password Credentials流程在RFC中已被废弃。

**推论C2**:
> JWT作为会话令牌时，若过期时间 > 15分钟且缺乏令牌绑定(Token Binding)，
> 则泄露风险呈指数级增长（因无法撤销）。

---

## 九、ASCII推理判定树 / 决策树

### 9.1 OAuth 2.0流程选型决策树

```text
                    ┌─────────────────┐
                    │ 选择OAuth 2.0流程 │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
    ┌─────────────────┐           ┌─────────────────┐
    │ 客户端类型?     │           │ 是否需要用户交互?│
    │ (公开/机密)     │           │                 │
    └────────┬────────┘           └────────┬────────┘
             │                             │
    ┌────────┴────────┐                    │
    ▼                 ▼                    │
┌─────────┐     ┌─────────┐               │
│ 公开客户端 │     │ 机密客户端 │               │
│ (SPA/移动)│     │ (服务端)  │               │
└────┬────┘     └────┬────┘               │
     │               │                    │
     ▼               ▼                    │
┌─────────────────┐ ┌─────────────────┐   │
│ Authorization   │ │ Authorization   │   │
│ Code + PKCE     │ │ Code (可选PKCE) │   │
│ (强制!)         │ │                 │   │
└─────────────────┘ └─────────────────┘   │
                                          │
                                     否 ◄─┤
                                          ▼
                                 ┌─────────────────┐
                                 │ 是否M2M通信?     │
                                 └────────┬────────┘
                                          │
                                     是 ◄─┤
                                          ▼
                                 ┌─────────────────┐
                                 │ Client          │
                                 │ Credentials     │
                                 │ Grant           │
                                 └─────────────────┘
                                          │
                                     否 ◄─┤
                                          ▼
                                 ┌─────────────────┐
                                 │ Device          │
                                 │ Authorization   │
                                 │ Grant (IoT/TV)  │
                                 └─────────────────┘
```

### 9.2 授权模型选型决策树

```text
                    ┌─────────────────┐
                    │ 选择授权模型     │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
    ┌─────────────────┐           ┌─────────────────┐
    │ 权限需求简单?    │           │ 需要上下文感知?  │
    │ < 20个角色?     │           │ (时间/地点/设备) │
    └────────┬────────┘           └────────┬────────┘
             │                             │
        是 ◄─┤                             ├──► 是
             │                             ▼
             ▼                    ┌─────────────────┐
    ┌─────────────────┐           │ ABAC / PBAC     │
    │ RBAC            │           │ (OPA/Cedar)     │
    │ 简单、可审计     │           │ 细粒度策略引擎   │
    └─────────────────┘           └─────────────────┘
             │
        否 ◄─┤
             ▼
    ┌─────────────────┐
    │ 需要关系继承?    │
    │ (组织架构/社交)  │
    └────────┬────────┘
             │
        是 ◄─┤                    ┌─────────────────┐
             │                    │ ReBAC (Zanzibar)│
             ▼                    │ 关系图 + 全局   │
    ┌─────────────────┐   ┌──────►│ 一致性存储      │
    │ 用户规模 > 1亿?  │   │       └─────────────────┘
    │ 需要全球一致性?  │   │
    └────────┬────────┘   │
             │             │
        是 ◄─┤             │
             │             │
             └─────────────┘
                          │
                     否 ◄─┤
                          ▼
                 ┌─────────────────┐
                 │ RBAC + ABAC混合  │
                 │ (分层策略模型)   │
                 └─────────────────┘
```

---

## 十、国际权威课程对齐

### 10.1 Stanford CS 155: Computer and Network Security

| 本文件主题 | 对应Stanford Lecture | 对应Homework/Project |
|-----------|---------------------|----------------------|
| Web认证与会话 | Lecture 9: User Authentication & Session Management | HW: 会话管理安全分析 |
| OAuth/OIDC协议 | Lecture 11: HTTPS, SSO | Project: 实现OAuth 2.0客户端 |
| Web应用安全 | Lecture 10: Web Application Security | HW: XSS/CSRF防御设计 |
| 权限模型 | Lecture 4: Access Control | Project: 访问控制策略实现 |

### 10.2 MIT 6.858: Computer Systems Security

| 本文件主题 | 对应MIT Lecture | 对应Lab/Project |
|-----------|----------------|----------------|
| 认证协议形式化 | Lecture 17: User Authentication | Lab: Kerberos/OAuth分析 |
| Web安全模型 | Lecture 8-9: Web Security Model | Lab 3: 安全Web服务器 |
| 令牌安全 | Lecture 14: SSL/HTTPS | Final Project: 身份系统设计 |
| 权限系统 | Lecture 6: Capabilities | Lab: 能力系统实现 |

### 10.3 CMU 18-330: Introduction to Computer Security

| 本文件主题 | 对应CMU Lecture | 对应Assignment |
|-----------|----------------|---------------|
| 认证机制 | Lecture 5-6: Authentication | HW: 多因素认证设计 |
| 访问控制模型 | Lecture 3-4: Access Control | HW: BLP/RBAC形式化证明 |
| Web协议安全 | Lecture 8-9: Web Security | Lab: OAuth安全审计 |
| 密码学应用 | Lecture 7: Applied Crypto | Project: JWT实现与分析 |

### 10.4 Berkeley CS 161: Computer Security

| 本文件主题 | 对应Berkeley Topic | 对应Homework/Project |
|-----------|-------------------|----------------------|
| 密码学基础 | Ch. 5-10: Cryptography | HW2-HW3 |
| Web安全 | Ch. 17-24: Web Security | Project 2 |
| 网络安全 | Ch. 25-29: Network Security | HW4 |
| 访问控制 | Ch. 11-16: OS Security | Project 1 |

### 10.5 核心参考文献

1. **Hardt, D. (2012)**. "The OAuth 2.0 Authorization Framework." RFC 6749, IETF. — OAuth 2.0核心规范，定义了四种授权流程和角色体系。

2. **Fett, D., Küsters, R. & Schmitz, G. (2016)**. "A Comprehensive Formal Security Analysis of OAuth 2.0." *IEEE Symposium on Security and Privacy (S&P)*, 1204-1219. — 使用Dolev-Yao模型对OAuth 2.0进行形式化安全分析的开创性工作。

3. **Sakimura, N., Bradley, J. & Agarwal, N. (2015)**. "Proof Key for Code Exchange by OAuth Public Clients." RFC 7636, IETF. — PKCE规范，将公开客户端的OAuth安全性提升到生产可用级别。

4. **Pang et al. / Google (2019)**. "Zanzibar: Google's Consistent, Global Authorization System." *USENIX ATC*. — 定义了ReBAC的工业标准实现，证明关系代数可统一RBAC和ABAC。

---

## 十一、深度批判性总结

OAuth 2.0的安全困境深刻诠释了**标准制定与工程实践之间的结构性张力**。Hardt在RFC 6749中刻意将OAuth定义为"框架而非协议"——这一设计哲学赋予了实现者极大的灵活性，但也埋下了灾难性的安全隐患。2016年之前，绝大多数公开客户端（单页应用、移动应用）错误地使用了Authorization Code Flow without PKCE，使得授权码在HTTP重定向中被拦截后即可换取访问令牌。Fett等人 (IEEE S&P 2016) 的形式化分析证明，在Dolev-Yao攻击者模型下，缺少PKCE的授权码流程对中间人攻击是脆弱的。PKCE (RFC 7636) 的出现不是锦上添花，而是**亡羊补牢**——它将一个本质上不安全的流程修补到了可接受的风险水平。

JWT的广泛滥用是另一个安全工程中"便利性压倒安全性"的经典案例。JWT被设计为自包含的声明载体，其无状态特性完美契合了微服务架构的横向扩展需求。但开发者常常忽视两个致命约束：第一，JWT一旦签发即无法服务端撤销（除非引入额外的令牌黑名单服务，这破坏了无状态优势）；第二，alg="none"攻击和密钥混淆攻击（将RS256公钥替换为HS256对称密钥）在2015-2019年间攻破了无数生产系统。JWT的15分钟过期时间建议（OWASP）在多数实现中被延长至数小时甚至数天——这是性能优化对安全保证的侵蚀。

从RBAC到ABAC再到ReBAC的演进，反映了访问控制从"预定义角色"到"动态属性"再到"关系网络"的认知深化。Google Zanzibar (USENIX ATC 2019) 的工程成就令人瞩目——它在全球数十亿关系元组上保持强一致性，但这也暴露了一个残酷现实：**表达力越强的授权模型，其工程实现越依赖于底层存储的能力边界**。对于大多数企业，OPA (Open Policy Agent) 提供的PBAC是更务实的中间道路：它允许在Rego语言中编写任意策略，同时避免了全局分布式图数据库的运营负担。认证与授权领域的前沿挑战正在从"如何验证身份"转向"如何在持续验证的同时保持可用性"——风险自适应认证（Risk-Adaptive Authentication）和隐私增强凭证（Privacy-Preserving Credentials）将是2026-2030年的核心研究方向。
