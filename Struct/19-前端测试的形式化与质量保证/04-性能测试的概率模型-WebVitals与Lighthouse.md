# 性能测试的概率模型：Web Vitals 与 Lighthouse

> **来源映射**: View/05.md §7.1
> **权威参考**: Google Web Vitals, Lighthouse CI

---

## 一、概率分布验证

```text
性能指标的概率模型:
  P(LCP < 2.5s) > 0.95  (Good)
  P(CLS < 0.1) > 0.95   (Good)
  P(INP < 200ms) > 0.95 (Good)

测试方法:
  多次采样 → 统计分布 → 与阈值比较
```

---

## 二、待完善内容

- [ ] 性能指标的概率分布拟合
- [ ] Lighthouse CI 的持续集成策略
