# Rust类型系统：借检查器作为轻量级分离逻辑

> **定位**：Rust的借用检查器是形式化方法走向主流的里程碑——它将分离逻辑（Separation Logic）的核心思想嵌入到日常编程语言中，让数百万开发者在不知情的情况下使用形式化验证。
>
> **核心命题**：Rust不是"让系统编程变难"，而是"将内存安全的认知负担从运行时转移到编译时"——一次性学习，终身受益。

---

## 一、思维导图：Rust所有权与分离逻辑

```text
Rust类型系统 ≈ 轻量级分离逻辑
│
├─【所有权 ≈ 线性类型】
│   ├─ 每个值有唯一所有者
│   ├─ 所有者离开作用域 → 值被释放
│   └─ 线性逻辑：资源必须被使用（不能静默丢弃）
│
├─【借用 ≈ 分离逻辑中的*】
│   ├─ &T：共享只读访问（分离合取）
│   ├─ &mut T：独占写访问（分离蕴含）
│   └─ &T 和 &mut T 不能同时存在
│
├─【生命周期 ≈ 范围保证】
│   └─ 引用不会比其引用对象活得更长
│
├─【Send/Sync ≈ 并发安全】
│   ├─ Send：可安全跨线程传递
│   └─ Sync：可安全跨线程共享
│
└─【unsafe边界】
    ├─ 编译器放弃验证
    ├─ 程序员负责维持不变式
    └─ 安全封装：unsafe实现 → safe API
```

---

## 二、所有权作为线性类型

```
线性逻辑（Linear Logic）：
  A ⊗ B = A和B都必须被消耗（不能复制/丢弃）

Rust映射：
  let x = String::from("hello");  // 获得资源
  let y = x;                       // move：x的所有权转移到y
  // x 不再可用（线性消耗）

  // 编译错误：use of moved value
  // println!("{}", x);

仿射类型（Affine Type）：
  允许丢弃但不允许复制

Rust映射：
  let x = String::from("hello");
  // x 被丢弃（离开作用域）
  // OK，但不可隐式复制
```

---

## 三、借用检查器 ≈ 分离逻辑

```
分离逻辑（Separation Logic）：
  P * Q = P和Q描述不相交的内存区域
  {P} C {Q} = 前置条件P，执行C，后置条件Q

Rust借用检查：
  let mut data = vec![1, 2, 3];

  // 分离：&data 访问一个区域
  let r1 = &data;

  // 分离：&mut data 访问另一个（互斥）区域
  // let r2 = &mut data;  // 编译错误！

  // 等价于分离逻辑的：
  // {data ↦ [1,2,3]}
  // let r1 = &data;
  // {r1 ↦ [1,2,3] * data ↦ [1,2,3]}  // 共享只读
  // let r2 = &mut data;
  // ERROR: r1 和 r2 的区域不分离！

核心规则：
  - 任意数量 &T（共享只读）
  - 或 一个 &mut T（独占写）
  - 二者不可同时存在
  → 数据竞争在编译期被消除
```

---

## 四、生命周期：形式化的范围保证

```rust
// 生命周期标注确保引用不会悬垂
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}

// 编译器验证：返回的引用与输入引用同寿
fn main() {
    let string1 = String::from("long");
    let result;
    {
        let string2 = String::from("short");
        result = longest(&string1, &string2);
        println!("{}", result);  // OK，string2仍有效
    }
    // println!("{}", result);  // 编译错误！
    // result可能引用string2，而string2已离开作用域
}

形式化直觉：
  'a 是一个"存活区间"
  编译器构建存活区间图，确保：
    引用的存活区间 ⊆ 被引用数据的存活区间
```

---

## 五、Send/Sync：并发安全的形式化

```
Send trait：
  类型T实现Send ⟺ 可以安全地将T的所有权转移到另一个线程

  自动推导：大多数类型是Send
  例外：Rc<T>（引用计数非线程安全）

Sync trait：
  类型T实现Sync ⟺ &T是Send（可以安全地在多线程间共享引用）

  自动推导：大多数类型是Sync
  例外：Cell<T>, RefCell<T>（内部可变性非线程安全）

并发安全保证：
  - 编译器阻止非Send数据跨线程
  - 编译器阻止非Sync数据多线程共享
  → 数据竞争在编译期被消除（不依赖运行时锁）
```

---

## 六、概念定义与属性关系

| 概念 | 定义 | 属性 | 示例 | 反例 |
|------|------|------|------|------|
| **所有权** | 值有唯一所有者的资源管理模型 | 编译期检查、零成本抽象 | String的move | C++隐式拷贝 |
| **借用** | 临时获取引用而不转移所有权 | 读写互斥、生命周期验证 | &T, &mut T | C的任意指针 |
| **分离逻辑** | 描述程序内存状态的形式化逻辑 | 可组合、模块化验证 | Rust借用检查的理论基础 | Hoare逻辑（无分离） |
| **生命周期** | 引用的有效范围标注 | 编译期推断/显式标注 | 'a | C的裸指针（无生命周期） |
| **Send/Sync** | 标记类型可安全跨线程传递/共享 | 自动推导、unsafe手动实现 | Arc<T> | Rc<T>（非Send） |

---

## 七、交叉引用

- → [07-总览](../00-总览-从构造到归纳的范式转移.md)
- → [07/01-TLA+](01-TLA+-时序逻辑规范与系统验证.md)
- → [09/03-Rust安全](../../09-安全模型与可信计算/03-Rust类型系统-内存安全的形式化保证.md)
- ↓ [01/01-可计算性](../../01-形式化计算理论根基/01-可计算性边界-停机问题与Rice定理.md)

---

## 七、参考文献

| 作者 | 标题 | 出处 | 年份 |
|------|------|------|------|
| Ralf Jung et al. | "RustBelt: Securing the Foundations of Rust" | *POPL* | 2018 |
| Aaron Turon | "The Rust Programming Language" (The Book) | doc.rust-lang.org | 持续更新 |
| John Reynolds | "Separation Logic: A Logic for Shared Mutable Data Structures" | *LICS* | 2002 |
| Nichols, Klabnik | *The Rust Programming Language* (2nd ed.) | No Starch Press | 2023 |

---

*文件创建日期：2026-04-23*
*状态：已完成*
