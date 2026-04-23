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
