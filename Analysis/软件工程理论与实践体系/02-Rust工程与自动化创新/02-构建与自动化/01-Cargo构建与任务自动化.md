# Cargo构建与任务自动化

Rust 提供了强大的构建和包管理工具，其核心是`Cargo`。通过`build.rs`自定义构建脚本、Cargo别名、工作区以及`cargo-make`等社区工具，可以实现高度的构建与任务自动化。

## 自定义构建脚本 (build.rs)

`build.rs` 是一个在构建包之前由 Cargo 编译和执行的脚本。它可以用于代码生成、链接原生库、设置条件编译等。

```rust
// file: build.rs
use std::env;
use std::fs;
use std::path::Path;

fn main() {
    // 获取输出目录
    let out_dir = env::var("OUT_DIR").unwrap();
    let dest_path = Path::new(&out_dir).join("generated.rs");
    
    // 生成代码
    let generated_code = r#"
        // 自动生成的代码
        pub fn generated_function() {
            println!("这是一个自动生成的函数!");
        }
        
        pub const GENERATED_VERSION: &str = "1.0.0";
    "#;
    
    fs::write(&dest_path, generated_code).unwrap();
    
    // 条件编译设置
    if cfg!(target_os = "windows") {
        println!("cargo:rustc-link-lib=dylib=user32");
    } else if cfg!(target_os = "linux") {
        println!("cargo:rustc-link-lib=dylib=X11");
    }
    
    // 通知Cargo在源文件更改时重新运行
    println!("cargo:rerun-if-changed=build.rs");
}
```

## 自定义Cargo命令 (`.cargo/config.toml`)

可以在项目根目录的`.cargo/config.toml`文件中为常用的Cargo命令设置别名，以简化工作流程。

```toml
# file: .cargo/config.toml
[alias]
check-all = "check --all-targets --all-features"
b = "build --release"
t = "test --all-features"
docs = "doc --open"
audit = "clippy && cargo outdated && cargo audit"
```

## Cargo工作区 (Workspaces)

对于包含多个关联包的大型项目，Cargo工作区（Workspaces）功能允许你统一管理它们。

```toml
# file: Cargo.toml
[workspace]
members = [
    "core",
    "client",
    "server",
    "common",
]

# 在工作区级别定义共享依赖
[workspace.dependencies]
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1.0", features = ["full"] }
log = "0.4"
```

## 使用`cargo-make`进行任务自动化

`cargo-make`是一个社区开发的强大任务运行器，它允许你在`Makefile.toml`中定义复杂的、跨平台的任务流，功能类似于`make`但与`Cargo`深度集成。

```toml
# file: Makefile.toml
[tasks.format]
command = "cargo"
args = ["fmt", "--all"]

[tasks.check]
command = "cargo"
args = ["check", "--all-targets", "--all-features"]

[tasks.clippy]
command = "cargo"
args = ["clippy", "--all-targets", "--all-features", "--", "-D", "warnings"]

[tasks.test]
command = "cargo"
args = ["test", "--all-features"]

[tasks.docs]
command = "cargo"
args = ["doc", "--no-deps", "--open"]

[tasks.audit]
dependencies = ["outdated", "security"]

[tasks.outdated]
command = "cargo"
args = ["outdated"]

[tasks.security]
command = "cargo"
args = ["audit"]

[tasks.ci]
dependencies = [
    "format",
    "check",
    "clippy",
    "test",
    "audit",
]
```

## 相关工具生态

- **cargo**: 包管理器
- **cargo-edit**: 依赖管理
- **cargo-watch**: 文件监视
- **cargo-expand**: 宏展开
- **cargo-outdated**: 依赖更新检查
- **cargo-audit**: 安全审计
- **cargo-tarpaulin**: 代码覆盖率
- **cargo-bloat**: 二进制大小分析
- **cargo-udeps**: 未使用依赖检测
- **cargo-nextest**: 测试运行器
- **cargo-deny**: 依赖审核
- **sccache**: 编译缓存
- **cross**: 跨平台编译 