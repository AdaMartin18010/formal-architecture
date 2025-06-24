# 使用Prost从Protobuf生成Rust代码

`prost` 是一个流行的、用于在Rust中处理Protocol Buffers的库。它与 `prost-build` crate 配合使用，可以在编译时自动将 `.proto` 文件编译成高效、地道的Rust代码。

本节将展示从项目设置到代码使用的完整流程。

## 1. 项目设置 (`Cargo.toml`)

首先，需要在 `Cargo.toml` 中添加 `prost` 作为运行时依赖，并添加 `prost-build` 和 `tonic-build`（如果需要生成gRPC服务）作为构建时依赖。

```toml
[dependencies]
prost = "0.12"
tokio = { version = "1.0", features = ["rt-multi-thread", "macros"] }
# tonic = "0.11" # 如果需要gRPC客户端/服务端，则添加此项

[build-dependencies]
prost-build = "0.12"
# tonic-build = "0.11" # 如果需要gRPC，则添加此项
```

## 2. 编写 `.proto` 文件

在你的项目根目录下创建一个 `proto` 文件夹，并在其中定义你的消息和服务。

```protobuf
// file: proto/user_service.proto

syntax = "proto3";

package user_service;

message User {
  uint64 id = 1;
  string name = 2;
  string email = 3;
  optional string role = 4;
}
```

## 3. 创建构建脚本 (`build.rs`)

在项目的根目录下创建一个 `build.rs` 文件。Cargo会在编译你的crate之前先编译并运行这个脚本。

```rust
// file: build.rs

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("cargo:rerun-if-changed=proto/user_service.proto"); // 当proto文件改变时，重新运行构建脚本

    prost_build::Config::new()
        //.out_dir("src/pb") // 可以指定输出目录
        .compile_protos(
            &["proto/user_service.proto"], // 要编译的proto文件列表
            &["proto/"], // proto文件的包含目录
        )?;

    Ok(())
}
```

这个脚本会调用 `prost_build`，它会解析 `user_service.proto` 文件，并在 `OUT_DIR` 环境变量所指向的目录中生成一个名为 `user_service.rs` 的Rust文件。

## 4. 在应用中使用生成的代码

现在，你可以在你的应用代码（如 `src/main.rs`）中使用 `include!`宏来将生成的代码直接包含进来。

```rust
// file: src/main.rs

// 这会将 `OUT_DIR/user_service.rs` 的内容包含进来
// `user_service` 是根据 .proto 文件中的 `package` 名称生成的模块名
pub mod user_service {
    include!(concat!(env!("OUT_DIR"), "/user_service.rs"));
}

// 现在你可以像使用普通Rust结构体一样使用生成的 `User` 类型
use user_service::User;

fn main() {
    let user = User {
        id: 1001,
        name: "张三".to_string(),
        email: "zhangsan@example.com".to_string(),
        role: Some("管理员".to_string()),
    };

    println!("创建的用户: {:?}", user);

    // 序列化 (Encoding)
    use prost::Message;
    let mut buf = Vec::new();
    user.encode(&mut buf).unwrap();

    println!("序列化后的二进制数据大小: {} 字节", buf.len());

    // 反序列化 (Decoding)
    let decoded_user = User::decode(&buf[..]).unwrap();

    println!("反序列化后的用户: {:?}", decoded_user);
    
    assert_eq!(user, decoded_user);
}
```

这个流程利用了Cargo的构建脚本能力，实现了从IDL（`.proto`文件）到可执行代码的无缝、自动化转换，是"规范驱动开发"的典范。
