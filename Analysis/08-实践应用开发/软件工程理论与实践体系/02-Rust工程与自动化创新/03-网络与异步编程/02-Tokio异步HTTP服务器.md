# 使用Tokio构建异步HTTP服务器

本节展示如何使用`Tokio`从头开始构建一个简单的、基于`Future`的高性能异步HTTP服务器。这个例子将深入探讨`async/await`、特征在服务抽象中的应用，以及如何在异步任务间共享状态。

## 核心实现

这个服务器不依赖任何高级Web框架，而是直接在`Tokio`的TCP层上工作，手动处理HTTP请求的解析和响应。

```rust
// 依赖: tokio = { version = "1", features = ["full"] }

use tokio::net::{TcpListener, TcpStream};
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use std::collections::HashMap;
use std::sync::Arc;
use std::time::Duration;
use std::future::Future;

// 1. 请求处理器特征 (Handler Trait)
// 定义一个通用的服务处理器接口，使其可以接受异步闭包。
trait Handler: Send + Sync {
    fn call(&self) -> std::pin::Pin<Box<dyn Future<Output = String> + Send>>;
}

// 2. 处理器包装类型
// 一个具体的类型，用于将闭包包装成符合`Handler`特征的对象。
struct ClosureHandler<F, Fut> {
    f: F,
    _marker: std::marker::PhantomData<Fut>,
}

impl<F, Fut> Handler for ClosureHandler<F, Fut>
where
    F: Fn() -> Fut + Send + Sync + 'static,
    Fut: Future<Output = String> + Send + 'static,
{
    fn call(&self) -> std::pin::Pin<Box<dyn Future<Output = String> + Send>> {
        Box::pin((self.f)())
    }
}

// 3. 创建闭包处理器的辅助函数
// 这个辅助函数简化了从闭包创建`Box<dyn Handler>`的过程。
fn handler<F, Fut>(f: F) -> Box<dyn Handler>
where
    F: Fn() -> Fut + Send + Sync + 'static,
    Fut: Future<Output = String> + Send + 'static,
{
    Box::new(ClosureHandler {
        f,
        _marker: std::marker::PhantomData,
    })
}

// 4. 连接处理函数
// 每个TCP连接都会由这个函数处理。
async fn handle_connection(mut stream: TcpStream, routes: Arc<HashMap<String, Box<dyn Handler>>>) {
    let mut buffer = [0; 1024];
    
    match stream.read(&mut buffer).await {
        Ok(bytes_read) if bytes_read > 0 => {
            let request = String::from_utf8_lossy(&buffer[..bytes_read]);
            let request_line = request.lines().next().unwrap_or("");
            let mut parts = request_line.split_whitespace();
            
            let _method = parts.next().unwrap_or("GET");
            let path = parts.next().unwrap_or("/");
            
            println!("Request for: {}", path);
            
            // 根据路径查找并调用对应的处理器
            if let Some(handler) = routes.get(path) {
                let response = handler.call().await;
                let _ = stream.write_all(response.as_bytes()).await;
            } else {
                let response = "HTTP/1.1 404 NOT FOUND\r\nContent-Length: 0\r\n\r\n";
                let _ = stream.write_all(response.as_bytes()).await;
            }
        }
        _ => {
            // 读取错误或连接关闭
        }
    }
}

// 5. 服务器主函数
// 设置路由、绑定端口并循环接受连接。
pub async fn run_server() {
    let mut routes = HashMap::new();
    
    // 定义路由和对应的异步处理逻辑
    routes.insert("/".to_string(), handler(|| async {
        "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 13\r\n\r\nHello, World!".to_string()
    }));
    
    routes.insert("/api/users".to_string(), handler(|| async {
        // 模拟异步数据库查询
        tokio::time::sleep(Duration::from_millis(10)).await;
        
        let users = r#"[{"id":1,"name":"张三"},{"id":2,"name":"李四"}]"#;
        format!(
            "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\n\r\n{}",
            users.len(),
            users
        )
    }));
    
    // 使用Arc在多个任务间安全地共享路由表
    let routes = Arc::new(routes);
    
    let listener = TcpListener::bind("127.0.0.1:8080").await.unwrap();
    println!("服务器运行在 http://127.0.0.1:8080");
    
    loop {
        match listener.accept().await {
            Ok((stream, _)) => {
                let routes_clone = routes.clone();
                // 为每个连接创建一个新的Tokio任务
                tokio::spawn(async move {
                    handle_connection(stream, routes_clone).await;
                });
            }
            Err(e) => {
                eprintln!("接受连接失败: {}", e);
            }
        }
    }
}
