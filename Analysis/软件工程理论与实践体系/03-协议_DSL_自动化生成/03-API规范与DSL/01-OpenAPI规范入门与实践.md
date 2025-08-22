# OpenAPI规范入门与实践

OpenAPI 规范（以前称为 Swagger 规范）是用于描述、生成、消费和可视化 RESTful Web 服务的语言无关的 API 定义格式。
它允许将 API 定义为"单一事实来源（Single Source of Truth）"，团队可以围绕这个来源构建工具、生成代码、生成文档，并自动化测试。

本节将通过一个简单的用户API示例，展示如何定义OpenAPI规范，以及如何利用该规范来驱动代码的自动生成。

## 1. 定义OpenAPI规范

API 规范通常写在 `YAML` 或 `JSON` 文件中。下面是一个定义简单"用户API"的 `openapi.yaml` 示例，它包含两个端点：获取用户列表和创建新用户。

```yaml
# file: openapi.yaml
openapi: 3.0.0
info:
  title: 用户API
  version: 1.0.0
paths:
  /users:
    get:
      summary: 获取用户列表
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
    post:
      summary: 创建用户
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/NewUser'
      responses:
        '201':
          description: 用户创建成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
components:
  schemas:
    # 'User' 代表API返回的用户对象
    User:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        email:
          type: string
      required:
        - id
        - name
        - email
    # 'NewUser' 代表创建用户时请求体中的对象
    NewUser:
      type: object
      properties:
        name:
          type: string
        email:
          type: string
      required:
        - name
        - email
```

## 2. 从规范到代码：自动化生成

一旦有了API规范，就可以用它来自动生成各种代码，确保客户端、服务器和文档的一致性。

下面是一个简化的Rust代码生成器示例，展示了如何从上面的规范中生成：

- **数据模型 (Models)**: 对应于`components/schemas`中的`User`和`NewUser`。
- **API客户端 (Client)**: 一个可以调用API的客户端。
- **服务器存根 (Server Stub)**: 一个包含API路由和处理器签名的服务器框架。

```rust
// 这是一个简化的代码生成器概念示例。
// 实际应用中会使用 utoipa, aide, openapi-generator-cli 等工具。

struct OpenApiGenerator;

impl OpenApiGenerator {
    // 从OpenAPI规范生成数据模型
    fn generate_models(spec: &str) -> String {
        // 在实际应用中，会解析规范并生成完整的Rust代码。
        // 此处为演示目的，返回手动编写的等效模型代码。
        r#"
        use serde::{Deserialize, Serialize};
        
        #[derive(Debug, Clone, Serialize, Deserialize)]
        pub struct User {
            pub id: i32,
            pub name: String,
            pub email: String,
        }
        
        #[derive(Debug, Clone, Serialize, Deserialize)]
        pub struct NewUser {
            pub name: String,
            pub email: String,
        }
        "#.to_string()
    }
    
    // 从OpenAPI规范生成基于reqwest的API客户端
    fn generate_client(spec: &str) -> String {
        // 同样，这是一个简化的演示
        r#"
        use reqwest::Client;
        // 假设User和NewUser模型已在别处定义
        
        pub struct UserApiClient {
            client: Client,
            base_url: String,
        }
        
        impl UserApiClient {
            // ... 实现 get_users() 和 create_user() 等方法 ...
        }
        "#.to_string()
    }
    
    // 从OpenAPI规范生成基于axum的服务器存根
    fn generate_server(spec: &str) -> String {
        // 同样，这是一个简化的演示
        r#"
        use async_trait::async_trait;
        use axum::{routing::{get, post}, Router};
        // 假设User和NewUser模型已在别处定义

        #[async_trait]
        pub trait UserService: Send + Sync + 'static {
            async fn get_users(&self) -> Result<Vec<User>, ()>;
            async fn create_user(&self, new_user: NewUser) -> Result<User, ()>;
        }
        
        pub fn create_router<S: UserService>(service: S) -> Router {
            // ... 创建路由并将其连接到处理器 ...
            unimplemented!()
        }
        "#.to_string()
    }
}
```

通过这种"规范驱动开发（Specification-Driven Development）"的方法，可以极大地提高开发效率，减少手动编码错误，并保证API的消费者和提供者之间始终同步。
