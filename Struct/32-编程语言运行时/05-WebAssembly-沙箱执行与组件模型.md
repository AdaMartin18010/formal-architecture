# WebAssembly：沙箱执行与组件模型

> **来源映射**: View/01.md §1.5, View/05.md §3.1
> **国际权威参考**: W3C WASM Spec, "WebAssembly: The Definitive Guide" (Titzer et al.), WASI Preview 2 Docs, Bytecode Alliance

---

## 一、知识体系思维导图

```text
WebAssembly (WASM)
│
├─► 核心虚拟机模型
│   ├─ 栈式虚拟机: 指令操作隐式操作数栈
│   ├─ 线性内存 (Linear Memory): 单一连续字节数组
│   │   └─ 页大小: 64KB，初始页数+最大页数
│   ├─ 表 (Table): 函数引用数组 (用于间接调用)
│   ├─ 全局 (Global): 可变/不可变全局变量
│   └─ 沙箱边界: 内存访问通过 bounds check，无法越界
│
├─► 执行模型
│   ├─ 加载: WASM 字节码 → 验证 → 实例化
│   ├─ 调用: 导出函数被宿主调用
│   ├─ 宿主函数: WASM 调用宿主提供的 API
│   └─ 无内置I/O: 纯计算，无文件/网络/时钟访问
│
├─► WASI (WebAssembly System Interface)
│   ├─ 目标: 可移植的系统接口标准
│   ├─ 能力安全 (Capability-based Security)
│   │   └─ 通过文件描述符访问资源，非路径字符串
│   ├─ Preview 1: 基于 POSIX 子集
│   └─ Preview 2: 基于组件模型 (WIT 接口定义)
│
├─► 组件模型 (Component Model)
│   ├─ WIT (WASM Interface Types): 接口定义语言
│   ├─ 组件: 组合多个 WASM 模块，跨语言互操作
│   ├─ 接口类型: 记录、变体、枚举、资源
│   └─ 包管理: WARGO / 组件注册表
│
├─► WASM GC 提案 (2023-2025)
│   ├─ 托管语言支持: Java/Kotlin/Dart/OCaml
│   ├─ 结构类型: 对象布局描述
│   ├─ 引用类型: externref, funcref
│   └─ 挑战: GC 语义与宿主 GC 协调
│
└─► 运行时实现
    ├─ 浏览器: V8, SpiderMonkey, JavaScriptCore
    ├─ 服务端: Wasmtime (Bytecode Alliance), Wasmer, WAMR
    ├─ 嵌入式: Wasm3, WAMR (轻量级)
    └─ 边缘: Cloudflare Workers, Fastly Compute@Edge
```

---

## 二、核心概念的形式化定义

### 2.1 线性内存安全模型

```text
定义 (WASM 线性内存):
  设实例 I 拥有线性内存 M:
    M = (base, size_current, size_max)
    base: 内存基地址 (由运行时分配)
    size_current: 当前大小 (64KB 页的整数倍)
    size_max: 最大可扩展大小 (可选)

  内存访问指令 (i32.load offset, align):
    effective_address = pop(i32) + offset
    if effective_address + sizeof(type) > size_current:
      trap! (立即终止，不可恢复)
    else:
      读取/写入内存

  安全性质:
    1. 空间安全: 所有访问通过 bounds check，无法越界
    2. 无指针算术: 内存索引为 i32，非物理地址
    3. 无执行数据: 线性内存不可执行 (NX bit)
    4. 无共享内存 (除非显式使用 SharedArrayBuffer)

  注意: bounds check 开销约为 3-5% (可通过虚拟内存技巧优化为 0%)
```

### 2.2 能力安全 (Capability-based Security)

```text
定义 (WASI 能力模型):
  传统 POSIX 安全模型:
    open("/etc/passwd", O_RDONLY)  // 通过路径字符串访问
    // 安全问题: 路径遍历、TOCTOU 竞争

  WASI 能力模型:
    设能力集合 C = {fd₁, fd₂, ..., fdₙ}
    每个 fd 是对特定资源的不可伪造引用

    fd_openat(dir_fd, "relative_path") → new_fd
    前提: dir_fd ∈ C, 且进程对 dir_fd 有目录遍历能力

    安全性质:
      - 无全局文件系统命名空间
      - 能力只能通过已有能力派生 (能力单调性)
      - 最小权限: 默认无能力，显式授予

  组件模型中的能力传递:
    组件 A 导出接口 I，组件 B 导入接口 I
    运行时验证: I 的 WIT 定义匹配 (类型安全)
    资源生命周期: 由导出方管理，导入方通过 handle 引用
```

### 2.3 组件模型组合

```text
定义 (WASM Component):
  组件 C = (Imports, Exports, Instances, Links)

  Imports: 所需外部接口集合
    import wasi:filesystem/types@0.2.0;
    import wasi:io/streams@0.2.0;

  Exports: 提供给外部的接口
    export app:handler/request@1.0.0;

  Instances: 内部 WASM 核心模块实例
    instance core_module = instantiate("module.wasm", ...)

  Links: 将 imports 连接到 exports 或内部实例

  组合性质:
    - 类型擦除: 组件边界使用 WIT 类型，内部使用核心 WASM 类型
    - 语言无关: Rust组件 + Python组件 + Go组件 → 同一应用
    - 沙箱保持: 组件间内存隔离，通过 lift/lower 传递数据
```

---

## 三、多维矩阵对比

| 维度 | WASM Core | WASI Preview 1 | WASI Preview 2 | Docker容器 | VM |
|------|-----------|----------------|----------------|-----------|-----|
| **启动时间** | **<1ms** | <10ms | <10ms | ~100ms-1s | ~秒级 |
| **隔离粒度** | 函数级 | 进程级 | 组件级 | 进程级 | OS级 |
| **内存开销** | **~MB级** | ~MB级 | ~MB级 | ~100MB | ~GB级 |
| **可移植性** | **二进制级** | 需WASI运行时 | 需组件运行时 | 需Linux内核 | 需Hypervisor |
| **沙箱强度** | **硬件级** | 硬件+能力 | 硬件+能力 | 内核命名空间 | 硬件虚拟化 |
| **I/O能力** | 无 | POSIX子集 | 组件接口 | 完整 | 完整 |
| **多语言组合** | 否 | 否 | **是** | 是(IPC) | 是(网络) |
| **GC语言支持** | 受限 | 受限 | **原生(WASM GC)** | 完整 | 完整 |

---

## 四、权威引用

> **Andreas Rossberg** (WebAssembly 联合设计负责人):
> "WebAssembly is not just a compile target for the web; it's a universal, safe, and efficient binary format for any platform."

> **Luke Wagner** (WebAssembly 核心设计者, Fastly):
> "The Component Model is to WebAssembly what the module system is to JavaScript — it enables composition at scale."

> **Bytecode Alliance**:
> "WebAssembly's sandbox is not an afterthought; it's the foundational property that makes everything else possible."

> **Lin Clark** (Mozilla/Bytecode Alliance):
> "With the Component Model, we're not just running code in the browser or the server — we're building a new kind of software Lego."

---

## 五、工程实践与代码示例

### 5.1 Rust → WASM 组件开发

```rust
// WIT 接口定义 (world.wit)
// package example:calculator;
// interface ops { add: func(a: u32, b: u32) -> u32; }
// world calculator { export ops; }

// Rust 实现 (src/lib.rs)
wit_bindgen::generate!({
    world: "calculator",
    path: "./wit"
});

struct Calculator;

impl exports::example::calculator::ops::Guest for Calculator {
    fn add(a: u32, b: u32) -> u32 {
        a + b
    }
}

export!(Calculator);

// 编译为组件:
// cargo component build --release
// 输出: target/wasm32-wasi/release/calculator.wasm
```

### 5.2 Wasmtime 运行时嵌入

```rust
use wasmtime::{Engine, Module, Store, Instance};

fn main() -> wasmtime::Result<()> {
    let engine = Engine::default();
    let module = Module::from_file(&engine, "app.wasm")?;

    // 创建带 WASI 的存储
    let wasi = wasmtime_wasi::WasiCtxBuilder::new()
        .inherit_stdio()
        .preopened_dir("/tmp", "/tmp", wasmtime_wasi::DirPerms::all(), wasmtime_wasi::FilePerms::all())?
        .build();

    let mut store = Store::new(&engine, wasi);
    let mut linker = wasmtime::Linker::new(&engine);
    wasmtime_wasi::add_to_linker(&mut linker, |s| s)?;

    let instance = linker.instantiate(&mut store, &module)?;
    let main = instance.get_typed_func::<(), ()>(&mut store, "main")?;
    main.call(&mut store, ())?;

    Ok(())
}
```

### 5.3 WASM 边界安全模型

```text
WASM 沙箱 vs 容器沙箱 vs VM 沙箱:

┌─────────────────────────────────────────────────────────────┐
│  攻击向量: 恶意 WASM 模块                                    │
├─────────────────────────────────────────────────────────────┤
│  WASM 边界保证:                                               │
│  1. 内存越界 → runtime trap (立即终止)                        │
│  2. 无限循环 → fuel metering / 指令计数限制                    │
│  3. 栈溢出 → 显式栈限制检查                                    │
│  4. 系统调用 → 只能通过宿主提供的受限接口                       │
│  5. 代码注入 → WASM 无 JIT，代码段只读                         │
├─────────────────────────────────────────────────────────────┤
│  逃逸风险 (需宿主防范):                                       │
│  - 宿主提供的函数存在漏洞 (如路径遍历)                          │
│  - side-channel (Spectre): WASM 同样受 CPU 漏洞影响            │
│  - 资源耗尽: 宿主需限制内存/CPU时间                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 六、批判性总结

WebAssembly是2026年最具**范式转移潜力**的技术之一，它将被 JavaScript 验证过的沙箱执行模型从浏览器带到了服务端、边缘和嵌入式设备。WASM的核心价值不在于性能（虽然它接近原生速度的90-95%），而在于**可移植性和安全性的统一**：同一份WASM二进制可以在浏览器、Kubernetes、IoT设备和边缘节点上运行，且无需信任代码提供者——运行时保证代码无法越界内存、无法执行任意系统调用、无法访问未授权资源。

然而，WASM的"通用编译目标"愿景仍面临**结构性障碍**。核心WASM（Core Spec）仅支持四种数值类型（i32, i64, f32, f64），这意味着任何复杂类型（字符串、数组、对象）都必须通过线性内存手动编解码。WASM Component Model和WIT接口类型正在解决这一"外部化类型系统"问题，但生态成熟度远不及gRPC或REST。WASM GC提案虽然已逐步落地，但托管语言（Java/Kotlin）的WASM支持仍落后于原生语言（Rust/C/C++）——这限制了WASM在现有企业代码库中的直接应用。

更深层的问题是**WASI的分裂**：Preview 1基于POSIX子集，Preview 2转向组件模型，两者之间存在不兼容性。云厂商（如Fermyon、Fastly）纷纷推出自己的WASM平台扩展，形成了新的碎片化风险。WASM的未来取决于Bytecode Alliance能否在标准化和商业竞争之间找到平衡——如果每个平台都要求开发者使用专有的SDK和工具链，WASM将重蹈"Write Once, Debug Everywhere"的覆辙。

尽管如此，WASM在**插件系统**和**多语言微服务**场景中的价值已得到验证：Envoy Proxy使用WASM作为扩展机制，允许用户以任何语言编写过滤器；Fermyon的Spin框架展示了WASM在Serverless中的极低启动优势。WASM不是现有运行时的替代品，而是一种新的**计算粒度**——比容器更轻、比进程更安全、比函数更通用。随着WASM GC和线程支持的成熟，它将成为云原生栈中不可或缺的中间层。
