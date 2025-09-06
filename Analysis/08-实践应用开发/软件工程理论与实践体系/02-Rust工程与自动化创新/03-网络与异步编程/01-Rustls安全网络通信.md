# 使用Rustls和Tokio实现安全网络通信

`Rustls`是一个现代、高性能且内存安全的纯Rust TLS库。与`Tokio`等异步运行时结合使用，可以轻松构建安全的异步网络应用。

## TLS服务器示例

以下是一个使用`Rustls`和`Tokio`构建的简单TLS服务器示例。

**前置条件:**

- 你需要生成一个自签名的证书（`cert.pem`）和私钥（`key.pem`）。

```rust
// 依赖:
// tokio = { version = "1", features = ["full"] }
// rustls = "0.20"
// rustls-pemfile = "1.0"

use rustls::{ServerConfig, ServerConnection};
use tokio::net::{TcpListener, TcpStream};
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use std::sync::Arc;
use std::io;

async fn rustls_server() -> io::Result<()> {
    // 加载证书和私钥
    let cert_file = &mut std::io::BufReader::new(std::fs::File::open("cert.pem")?);
    let key_file = &mut std::io::BufReader::new(std::fs::File::open("key.pem")?);
    
    let certs = rustls_pemfile::certs(cert_file).collect::<Result<Vec<_>, _>>().unwrap();
    let keys = rustls_pemfile::pkcs8_private_keys(key_file)
        .collect::<Result<Vec<_>, _>>().unwrap();
    
    // 配置服务器
    let config = ServerConfig::builder()
        .with_safe_defaults()
        .with_no_client_auth()
        .with_single_cert(certs, rustls::PrivateKey(keys[0].clone()))
        .expect("配置TLS失败");
    
    let tls_config = Arc::new(config);
    
    // 创建TLS服务器
    let listener = TcpListener::bind("127.0.0.1:8443").await?;
    println!("TLS服务器监听在 127.0.0.1:8443");
    
    loop {
        let (tcp_stream, addr) = listener.accept().await?;
        let tls_config = tls_config.clone();
        
        tokio::spawn(async move {
            println!("接受来自 {} 的连接", addr);
            
            // 创建TLS会话
            let server = match ServerConnection::new(tls_config) {
                Ok(s) => s,
                Err(e) => {
                    eprintln!("TLS初始化错误: {:?}", e);
                    return;
                }
            };
            
            // 此处可以进一步处理TLS会话，例如读写加密数据
            // let tls_stream = rustls::Stream::new(&mut server, &mut tcp_stream);
            // ...
        });
    }
}
```

## 相关安全通信框架生态

- **Rustls**: 纯Rust TLS实现
- **Ring**: 密码学原语
- **RustCrypto**: 各种加密算法
- **Snow**: Noise协议框架
- **OpenSSL**: OpenSSL绑定
- **Dalek**: 椭圆曲线密码学
- **Orion**: 易用的密码学库
- **Age**: 文件加密工具
- **Sodiumoxide**: libsodium绑定
- **HPKE-rs**: 混合公钥加密
