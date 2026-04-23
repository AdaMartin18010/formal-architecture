# TLS 与 mTLS：传输层安全

> **来源映射**: View/02.md §7, View/09.md
> **国际权威参考**: RFC 8446 (TLS 1.3), RFC 5280 (X.509), "Bulletproof SSL and TLS" (Ivan Ristić), NIST SP 800-52 (Guidelines for TLS)

---

## 一、知识体系思维导图

```text
TLS/mTLS 安全体系
│
├─► TLS 演进
│   ├─ SSL 2.0/3.0: 已废弃 (POODLE 攻击)
│   ├─ TLS 1.0/1.1: 已废弃 (BEAST, Lucky13)
│   ├─ TLS 1.2: 广泛部署，支持多种密码套件
│   └─ TLS 1.3 (2018, RFC 8446): 当前标准
│       ├─ 握手简化: 1-RTT (首次) / 0-RTT (恢复)
│       ├─ 移除不安全的密码套件和算法
│       ├─ 前向保密 (PFS): 强制 ECDHE
│       └─ 加密扩展: 握手更多步骤加密
│
├─► TLS 1.3 握手
│   ├─ 首次连接 (1-RTT):
│   │   ClientHello → ServerHello + {EncryptedExtensions} + {Finished}
│   │   → {ClientFinished} + 应用数据
│   ├─ 恢复连接 (0-RTT):
│   │   ClientHello + early_data → ServerHello + 应用数据
│   │   └─ 风险: 重放攻击 (仅限幂等操作)
│   └─ 关键改进: 服务端证书在加密扩展中发送，中间件不可窥探
│
├─► 密码套件 (TLS 1.3 精简)
│   ├─ 密钥交换: 仅 ECDHE (X25519, P-256, P-384)
│   ├─ 认证: RSA 或 ECDSA 签名
│   ├─ 对称加密: AES-128-GCM, AES-256-GCM, ChaCha20-Poly1305
│   └─ 哈希: SHA-256, SHA-384
│
├─► 证书体系 (X.509 PKI)
│   ├─ 证书链: 终端证书 → 中间 CA → 根 CA
│   ├─ 验证: 签名链验证 + 有效期 + 域名匹配 + 吊销检查
│   ├─ 吊销检查
│   │   ├─ CRL (Certificate Revocation List)
│   │   └─ OCSP (Online Certificate Status Protocol)
│   │       └─ OCSP Stapling: 服务端预取 OCSP 响应，保护隐私
│   ├─ 证书透明度 (CT): 所有证书必须记录到公共日志
│   └─ Let's Encrypt: 自动化 DV 证书颁发 (ACME 协议)
│
├─► mTLS (双向 TLS)
│   ├─ 服务端验证客户端证书
│   ├─ 证书即身份: 无需密码/令牌
│   ├─ 适用: 服务网格、IoT、API 网关内部通信
│   └─ 挑战: 证书生命周期管理、吊销、轮换
│
└─► 部署实践
    ├─ HSTS: 强制 HTTPS
    ├─ HPKP (已废弃): 证书固定过于危险
    ├─ Certificate Pinning (移动端): 内置公钥哈希
    └─ 自动化: cert-manager (K8s), ACME, 短期证书
```

---

## 二、核心概念的形式化定义

### 2.1 TLS 1.3 握手

```text
定义 (TLS 1.3 首次握手):
  客户端: 持有信任锚集合 TrustAnchors, 支持曲线集合 Curves
  服务端: 持有证书链 CertChain, 私钥 PrivateKey

  1. ClientHello:
     - Client Random (32 bytes)
     - Supported Groups (X25519, P-256)
     - Key Share: 客户端 ECDHE 公钥
     - Signature Algorithms
     - Supported Versions (0x0304 = TLS 1.3)

  2. ServerHello:
     - Server Random
     - Key Share: 服务端 ECDHE 公钥
     - Selected Cipher Suite
     - {EncryptedExtensions}: 加密传输的扩展
     - {Certificate}: 服务端证书链
     - {CertificateVerify}: 证书签名验证
     - {Finished}: HMAC 握手完整性

  3. 客户端响应:
     - {Finished}: HMAC 握手完整性
     - 应用数据 (1-RTT)

  密钥推导:
    shared_secret = ECDHE(client_private, server_public)
    handshake_secret = HKDF-Extract(0, shared_secret)
    client_handshake_traffic_secret = HKDF-Expand-Label(handshake_secret, "c hs traffic", ClientHello..ServerHello, Hash.length)
    server_handshake_traffic_secret = HKDF-Expand-Label(handshake_secret, "s hs traffic", ClientHello..ServerHello, Hash.length)
```

### 2.2 完美前向保密 (PFS)

```text
定义 (Perfect Forward Secrecy):
  传统 RSA 密钥交换:
    预主密钥 = RSA-Encrypt(server_public_key, pre_master_secret)
    风险: 若服务端长期私钥泄露, 所有历史会话可被解密

  ECDHE 密钥交换:
    每次会话生成临时 ECDH 密钥对
    会话密钥 = ECDH(client_ephemeral_private, server_ephemeral_public)
    风险: 仅泄露当前会话, 历史会话不受影响

  形式化保证:
    ∀ 历史会话 s, 即使长期私钥泄露,
    攻击者无法从 traffic 恢复 session_key(s)

  TLS 1.3 强制要求:
    所有握手必须使用 (EC)DHE
    RSA 密钥交换被完全移除
```

### 2.3 mTLS 认证

```text
定义 (mTLS 双向认证):
  标准 TLS: Server 提供证书, Client 验证 Server 身份
  mTLS: Client 也提供证书, Server 验证 Client 身份

  服务端验证逻辑:
    verify_client(cert_chain) =
      validate_chain(cert_chain, trust_anchors) ∧
      check_not_revoked(cert) ∧
      check_validity_period(cert) ∧
      check_authorized_subjects(cert.subject, allowed_subjects)

  证书内容作为身份标识:
    Subject CN = 服务名 (如 "service-a.prod.cluster.local")
    或 Subject Alternative Name (SAN) = SPIFFE ID

  服务网格场景 (Istio):
    - 每个 Sidecar 持有由 Citadel/Istiod 签发的证书
    - 证书自动轮换 (默认 24 小时有效期)
    - 服务端通过 SAN 验证调用者身份
```

---

## 三、多维矩阵对比

| 维度 | TLS 1.2 | TLS 1.3 | mTLS | 纯 TCP |
|------|---------|---------|------|--------|
| **握手延迟** | 2-RTT | **1-RTT** | 2-RTT (双向) | 0-RTT |
| **恢复延迟** | 1-RTT | **0-RTT** | 1-RTT | N/A |
| **前向保密** | 可选 (ECDHE) | **强制** | 强制 | ❌ 无 |
| **密码套件数** | ~340 | **5** | 同 TLS 1.3 | N/A |
| **中间件窥探** | 证书明文 | **加密** | 加密 | 全部明文 |
| **实现复杂度** | 高 (兼容历史) | **较低** | 高 (证书管理) | 低 |
| **证书管理** | 服务端 | 服务端 | 双端 | 无 |
| **性能影响** | 中 | **低** | 中 | 无 |
| **2026 状态** | 逐步淘汰 | **标准** | 服务网格标配 | 仅内部可信网 |

---

## 四、权威引用

> **RFC 8446** (TLS 1.3):
> "TLS 1.3 provides significant latency improvements over TLS 1.2 and removes support for legacy algorithms known to have security vulnerabilities."

> **Ivan Ristić** ("Bulletproof SSL and TLS", Feisty Duck):
> "The only secure way to use SSL/TLS is to use the latest version and configure it properly. Everything else is a compromise."

> **Let's Encrypt**:
> "Our mission is to create a more secure and privacy-respecting Web by promoting the widespread adoption of HTTPS."

> **NIST SP 800-52 Rev. 2**:
> "Servers that support government-only applications shall be configured to use TLS 1.3 and shall not support TLS 1.2 or earlier versions."

---

## 五、工程实践与代码示例

### 5.1 检查服务端 TLS 配置

```bash
# 使用 OpenSSL 检查支持的协议和密码套件
openssl s_client -connect example.com:443 -tls1_3

# 使用 testssl.sh 全面审计
testssl.sh --openssl-timeout 30 https://example.com

# 使用 nmap 检测 SSL/TLS 版本
nmap --script ssl-enum-ciphers -p 443 example.com
```

### 5.2 Kubernetes cert-manager 自动证书

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: example-tls
  namespace: default
spec:
  secretName: example-tls-secret
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
    - example.com
    - www.example.com
  # 短期证书自动轮换
  duration: 2160h    # 90 天
  renewBefore: 360h  # 15 天前自动续期
```

### 5.3 Istio mTLS 策略

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT    # 强制 mTLS，拒绝明文通信
---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: service-a-policy
  namespace: default
spec:
  selector:
    matchLabels:
      app: service-a
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/service-b"]
```

---

## 六、批判性总结

TLS 1.3 是密码学工程与标准化政治的杰作：它在**安全性**（移除 RSA 密钥交换、RC4、MD5、SHA-1）、**性能**（1-RTT 握手、0-RTT 恢复）和**隐私性**（加密 ServerHello 之后的所有握手消息）之间取得了卓越平衡。加密握手扩展的设计尤其精妙——它阻止了中间盒 (Middlebox) 对证书和 ALPN 信息的窥探，这些窥探曾导致 TLS 1.2 的演进陷入停滞（中间盒假设证书在明文位置，新版本的微小变化导致连接失败）。

但 0-RTT 数据再次印证了安全领域的**永恒权衡**：用延迟换安全。0-RTT 允许客户端在握手完成前发送应用数据，但引入了**重放攻击**风险——攻击者可以截获并重复发送 0-RTT 数据。TLS 1.3 的缓解措施（要求 0-RTT 数据使用独立的早期密钥，服务端可拒绝 0-RTT）是务实的工程妥协，而非完美的数学保证。

mTLS 在服务网格中的普及揭示了**身份管理的深层挑战**：证书即身份的理念优雅简洁，但证书的生命周期管理（签发、分发、轮换、吊销）在大规模分布式系统中极为复杂。Istio 的短期证书（24 小时）自动轮换策略是有效的缓解，但它要求 Sidecar 代理的高可用性——如果 Istiod 不可用，新 Pod 无法获取证书，服务启动即失败。这再次验证了分布式系统的**脆弱性守恒定律**：安全性的提升往往以运营复杂度和新故障模式的引入为代价。
