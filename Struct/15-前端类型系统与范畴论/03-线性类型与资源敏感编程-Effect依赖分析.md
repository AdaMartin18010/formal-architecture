# 线性类型与资源敏感编程：Effect 依赖分析

> **来源映射**: View/05.md §2.2
> **权威参考**: Wadler "Linear Types can Change the World", React Compiler 文档

---

## 一、核心概念定义

### 1.1 线性类型在前端的映射

```text
传统类型: A → A → A  (幂等, 可多次使用)
线性类型: A ⊸ A ⊸ A  (资源必须恰好使用一次)

前端映射:
  useEffect 的依赖数组 ≈ 线性类型的 "使用上下文"

  违反线性性:
    const [count, setCount] = useState(0)
    useEffect(() => { console.log(count) }, [])
    // 线性错误: 使用了未在依赖数组中声明的资源

  React Compiler 的自动 memo ≈ 线性类型推断器
    自动推断 "资源使用图", 插入正确的依赖声明
```

---

## 二、权威引用

> **Philip Wadler** (1990):
> "Linear types can change the world."

---

## 三、待完善内容

- [ ] 线性类型的所有权语义与 Rust Borrow Checker 的对比
- [ ] React Compiler 的依赖图推断算法
- [ ] 线性类型在前端资源管理中的扩展应用
