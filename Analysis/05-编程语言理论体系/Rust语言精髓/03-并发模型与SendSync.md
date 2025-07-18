# 05-编程语言理论体系-Rust语言精髓-并发模型与SendSync

[返回主题树](../../00-主题树与内容索引.md) | [主计划文档](../../00-形式化架构理论统一计划.md) | [相关计划](../../递归合并计划.md)

> 本文档为编程语言理论体系分支 Rust 语言精髓-并发模型与SendSync，所有最新进展与结论以主计划文档为准，历史细节归档于archive/。

## 1. 核心概念：作为类型标记的Trait

在Rust的并发模型中，`Send` 和 `Sync` 是两个至关重要的**标记特征 (Marker Traits)**。它们不定义任何新的行为或方法，其唯一目的是在编译期向类型系统提供关于数据如何能被安全地用于多线程环境的元信息。

这种设计是Rust实现"无畏并发"(Fearless Concurrency)的基石，它将线程安全问题从运行时的动态检查或程序员的手动管理，转变为编译期的静态证明。

### 1.1 `Send` Trait: 所有权的跨线程转移

**形式化定义**: 如果一个类型 `T` 实现了 `Send` Trait，意味着 `T` 类型的值的所有权可以被安全地从一个线程**转移**到另一个线程。

```rust
// `Send` 是一个由编译器自动实现的 `unsafe auto trait`
pub unsafe auto trait Send {}
```

- **与所有权模型的关联**: `Send` 直接关联所有权的**移动(Move)**语义。一个值被发送到另一个线程，本质上是其所有权从当前线程的作用域转移到了新线程的作用域。
- **编译器保证**: 编译器会强制检查 `std::thread::spawn` 等API的闭包参数，确保其捕获的所有变量的类型都实现了 `Send`。

### 1.2 `Sync` Trait: 跨线程共享引用

**形式化定义**: 如果一个类型 `T` 实现了 `Sync` Trait，意味着 `&T` 类型（对`T`的不可变引用）可以被安全地在多个线程之间**共享**。

```rust
// `Sync` 同样是 `unsafe auto trait`
pub unsafe auto trait Sync {}
```

- **与所有权模型的关联**: `Sync` 直接关联所有权的**借用(Borrow)**语义。多个线程同时拥有对某个数据的不可变引用，这是安全的，因为不可变引用不允许修改数据。
- **`Send` 与 `Sync` 的关系**: 如果 `&T` 是 `Send` 的（即一个引用可以被发送到另一个线程），那么 `T` 就是 `Sync` 的。这是 `Sync` 定义的本质。

## 2. 编译器的推导逻辑：自动与负向实现

`Send` 和 `Sync` 作为 `auto trait`，其实现与否由编译器根据类型的内部结构自动推导。

### 2.1 自动实现规则 (Compositional Rule)

编译器的推导是递归的：

1. **对于 `Send`**: 如果一个复合类型（`struct` 或 `enum`）的所有成员都实现了 `Send`，那么该类型本身也自动实现 `Send`。
2. **对于 `Sync`**: 如果一个复合类型的所有成员都实现了 `Sync`，那么该类型本身也自动实现 `Sync`。

大多数基础类型，如 `i32`, `bool`, `&'static str` 以及 `Box<T>` (若 `T: Send`) 和 `Arc<T>` (若 `T: Send + Sync`) 都遵循这个规则。

### 2.2 负向实现 (Negative Implementation)

某些类型天生不具备跨线程安全性，因此它们**没有**实现 `Send` 或 `Sync`。当一个复合类型包含这些非线程安全的成员时，它也会自动地变为非 `Send` 或非 `Sync`。

最典型的例子是：

- **`std::rc::Rc<T>`**: `Rc<T>` 通过非原子性的引用计数来管理共享所有权，如果在多线程间共享会导致计数器出现数据竞争。因此，`Rc<T>` **没有实现 `Send` 和 `Sync`**。
- **`std::cell::RefCell<T>`**: `RefCell<T>` 在运行时检查借用规则，但这种检查本身不是线程安全的。因此，`RefCell<T>` **没有实现 `Sync`**。
- **裸指针 `*mut T` 和 `*const T`**: 编译器无法对裸指针的安全性做出任何保证，因此它们默认不是 `Send` 或 `Sync` 的。

**推论**: 任何包含 `Rc<T>` 或 `RefCell<T>` 的结构体，默认情况下都不会是线程安全的（即非`Send`/`Sync`）。

## 3. `Send` 和 `Sync` 的组合应用

`Send` 和 `Sync` 与Rust的智能指针结合，构成了管理并发状态的核心模式。

| 智能指针 | 所有权语义 | 线程安全 (`Send`/`Sync`) | 适用场景 |
|:---:|:---|:---|:---|
| `Box<T>` | 唯一所有权 | `T: Send` => `Box<T>: Send`  `T: Sync` => `Box<T>: Sync` | 将数据置于堆上，并在线程间转移所有权。 |
| `Arc<T>` | 原子性共享所有权 | `T: Send + Sync` => `Arc<T>: Send + Sync` | 在多个线程间安全地共享只读数据。 |
| `Mutex<T>`| 互斥访问 | `T: Send` => `Mutex<T>: Send + Sync` | 允许多个线程通过加锁来互斥地修改共享数据。 |
|`RwLock<T>`| 读写锁 | `T: Send + Sync` => `RwLock<T>: Send + Sync`| 允许多个读线程或一个写线程访问共享数据。|

### 形式化分析: `Arc<Mutex<T>>`

`Arc<Mutex<T>>` 是实现跨线程共享可变状态的最常用模式。其安全性可以形式化地分解：

1. **`T: Send`**: 保证了 `T` 类型的值可以被安全地移入 `Mutex` 的内部。
2. **`Mutex<T>: Send + Sync`**: `Mutex` 本身是 `Sync` 的，所以 `&Mutex<T>` 可以在线程间共享。`MutexGuard`（锁的持有凭证）不是 `Send` 的，防止锁在不同线程间转移。
3. **`Arc<Mutex<T>>: Send + Sync`**: 由于 `Mutex<T>` 是 `Send` 和 `Sync` 的，`Arc` 可以安全地封装它，从而允许 `Arc<Mutex<T>>` 的克隆体被**发送**到多个线程中。

最终，每个线程都持有一个指向同一个堆分配的 `Mutex` 的共享引用，并通过 `Mutex` 提供的同步机制安全地访问被保护的数据 `T`。

## 4. 总结：零成本的静态并发安全

`Send` 和 `Sync` trait 是Rust并发安全模型的基石。它们作为编译期标记，将线程安全检查左移到了编译阶段，具有以下核心优势：

- **无运行时开销**: 作为标记，它们不产生任何额外代码，符合Rust的零成本抽象原则。
- **组合性**: 编译器可根据类型的构成自动推导其线程安全性，使得构建复杂的线程安全类型变得简单和可靠。
- **可验证性**: 任何不满足 `Send` 或 `Sync` 约束的跨线程操作都会导致编译失败，从根本上消除了数据竞争。
