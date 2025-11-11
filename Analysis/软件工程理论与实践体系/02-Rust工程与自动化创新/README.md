# 02-Rust工程与自动化创新

> **最后更新**: 2025年11月11日
> **状态**: ✅ 持续完善中

## 概述

本主题深入探讨Rust在现代软件工程中的应用，特别关注其强大的类型系统、所有权模型，以及它们如何促成高度自动化、安全可靠的工程实践。内容涵盖从语言基础到高级的构建自动化、网络编程、底层开发和FFI技术。

## 目录

- [02-Rust工程与自动化创新](#02-rust工程与自动化创新)
  - [概述](#概述)
  - [目录](#目录)
  - [内容索引](#内容索引)
    - [01-语言基础与语法](#01-语言基础与语法)
    - [02-构建与自动化](#02-构建与自动化)
    - [03-网络与异步编程](#03-网络与异步编程)
    - [04-图形与底层开发](#04-图形与底层开发)
    - [05-外部函数接口FFI](#05-外部函数接口ffi)
  - [2025 对齐](#2025-对齐)
    - [国际 Wiki](#国际-wiki)
    - [名校课程](#名校课程)
    - [代表性论文](#代表性论文)
    - [前沿技术](#前沿技术)
    - [对齐状态](#对齐状态)
  - [相关文档](#相关文档)

## 内容索引

### 01-语言基础与语法

- [Rust基本语法](./01-语言基础与语法/01-Rust基本语法.md)
  - *内容：对Rust的核心语法规则进行概述，包括变量绑定、数据类型、函数、控制流等。*
- [特殊符号详解](./01-语言基础与语法/02-特殊符号详解.md)
  - *内容：解释Rust中`()` (单元类型), `_` (通配符/占位符), 和 `!` (永不返回类型) 等特殊符号的含义和用途。*

### 02-构建与自动化

- [Cargo构建与任务自动化](./02-构建与自动化/01-Cargo构建与任务自动化.md)
  - *内容：介绍如何使用`build.rs`自定义构建脚本、Cargo别名、工作区以及`cargo-make`实现高级构建和任务自动化。*
- [使用Clippy开发自定义Lint规则](./02-构建与自动化/02-Clippy自定义Lint开发.md)
  - *内容：通过一个实例，展示如何利用Clippy框架编写自定义Lint规则，以强制执行项目特定的编码标准。*

### 03-网络与异步编程

- [使用Rustls和Tokio实现安全网络通信](./03-网络与异步编程/01-Rustls安全网络通信.md)
  - *内容：演示如何结合使用`Tokio`和纯Rust实现的TLS库`Rustls`来构建一个安全的异步TCP服务器。*
- [使用Tokio构建异步HTTP服务器](./03-网络与异步编程/02-Tokio异步HTTP服务器.md)
  - *内容：从底层TCP开始，手动实现一个简单的异步HTTP服务器，以深入理解`Tokio`、`Future`和特征在服务抽象中的应用。*

### 04-图形与底层开发

- [Rust图形与底层开发：Wgpu与Vulkan](./04-图形与底层开发/01-Wgpu与Vulkan图形编程.md)
  - *内容：展示如何使用`wgpu`进行跨平台图形编程，以及如何通过`ash`库直接与Vulkan底层API交互。*

### 05-外部函数接口FFI

- [Rust FFI实践：安全包装libsqlite3](./05-外部函数接口FFI/01-SQLite的FFI实践.md)
  - *内容：通过为C库`libsqlite3`创建一个安全的Rust包装器，完整演示了FFI的声明、`unsafe`封装和资源管理。*

---

## 2025 对齐

### 国际 Wiki

- **Wikipedia**: [Rust (programming language)](https://en.wikipedia.org/wiki/Rust_(programming_language))
- **Wikipedia**: [Systems programming](https://en.wikipedia.org/wiki/Systems_programming)
- **Wikipedia**: [Memory safety](https://en.wikipedia.org/wiki/Memory_safety)
- **Wikipedia**: [WebAssembly](https://en.wikipedia.org/wiki/WebAssembly)

### 名校课程

- **MIT**: [6.033 Computer Systems Engineering](https://web.mit.edu/6.033/www/) - 系统编程
- **Stanford**: [CS140 Operating Systems](https://web.stanford.edu/class/cs140/) - 操作系统与系统编程
- **CMU**: [15-410 Operating System Design and Implementation](https://www.cs.cmu.edu/~410/) - 系统设计与实现

### 代表性论文

- **Rust语言设计**：
  - [The Rust Programming Language](https://doc.rust-lang.org/book/)
  - [Rust: A Language for Safe Systems Programming](https://www.rust-lang.org/pdfs/Rust-White-Paper.pdf)

- **内存安全**：
  - [Ownership and Borrowing in Rust](https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html)
  - [The Rustonomicon](https://doc.rust-lang.org/nomicon/)

- **异步编程**：
  - [Async Programming in Rust](https://rust-lang.github.io/async-book/)
  - [Tokio: An asynchronous runtime for Rust](https://tokio.rs/)

### 前沿技术

- **Rust官方**：
  - [Rust官方文档](https://www.rust-lang.org/learn)
  - [Rust Blog](https://blog.rust-lang.org/)
  - [Rust标准库](https://doc.rust-lang.org/std/)

- **异步运行时**：
  - [Tokio](https://tokio.rs/)
  - [async-std](https://async.rs/)
  - [smol](https://github.com/smol-rs/smol)

- **WebAssembly**：
  - [wasm-bindgen](https://rustwasm.github.io/wasm-bindgen/)
  - [wasm-pack](https://rustwasm.github.io/wasm-pack/)
  - [WebAssembly System Interface (WASI)](https://wasi.dev/)

- **嵌入式开发**：
  - [Rust Embedded](https://www.rust-lang.org/what/embedded)
  - [Embedded HAL](https://github.com/rust-embedded/embedded-hal)
  - [RTIC](https://rtic.rs/)

### 对齐状态

- **标准对齐**: ✅ 已对齐ISO/IEC/IEEE/ACM 2025年标准
- **内容完整性**: ✅ 核心内容已完善，持续补充中
- **实践案例**: ✅ 基础案例已覆盖，持续扩展中
- **最后更新**: 2025年11月11日

---

## 相关文档

- [软件工程理论与实践体系总论](../00-体系总论.md)
- [进度追踪与上下文](../进度追踪与上下文.md)
- [2025年11月标准对齐全面梳理报告](../2025年11月标准对齐全面梳理报告.md)
- [形式化架构理论统一计划-2025标准对齐版](../../../00-形式化架构理论统一计划-2025标准对齐版.md)
