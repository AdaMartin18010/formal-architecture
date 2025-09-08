# 知识图谱 Schema v1（说明与示例）

> 目的：统一三类对齐矩阵（课程/标准/仓库）与 L0-L4 知识域的节点与关系建模，支持自动校验与报表。

## 1. 节点类型（Nodes）

- DomainL1：顶层知识域
- DomainL2：子域
- DomainL3：知识单元
- CourseUnit：课程单元（学校/课程/模块/节次）
- StandardClause：标准条款（标准/章节/条目）
- RepoFile：仓库文件（相对路径）

## 2. 关系类型（Edges）

- COVERS(CourseUnit → DomainL[1/2/3])：课程覆盖
- SATISFIES(StandardClause → DomainL[1/2/3])：标准满足
- EVIDENCES(RepoFile → DomainL[1/2/3])：证据文件
- CITES(A → B)：引用（跨任意节点）
- REFINES(DomainL2 → DomainL1), REFINES(DomainL3 → DomainL2)：分层细化

## 3. 属性（Properties）

- 通用：id, name, description, updatedAt
- 覆盖/满足度量字段：
  - coverageLevel：None/Intro/Intermediate/Advanced
  - satisfaction：None/Partial/Full
  - completenessScore：0/25/50/75/100
  - evidenceLinks：[string]
  - notes：string

## 4. 示例（伪JSON）

```json
{
  "nodes": [
    {"type":"DomainL2","id":"dist.consistency","name":"一致性模型"},
    {"type":"CourseUnit","id":"mit.6.824","name":"MIT 6.824"},
    {"type":"StandardClause","id":"iso25010.reliability","name":"ISO 25010 可靠性"},
    {"type":"RepoFile","id":"A11.async-sync.part1","name":"异步同步组合-第一部分","path":"Analysis/11-理论统一与整合/异步同步组合形式化论证-第一部分.md"}
  ],
  "edges": [
    {"type":"COVERS","from":"mit.6.824","to":"dist.consistency","coverageLevel":"Advanced"},
    {"type":"SATISFIES","from":"iso25010.reliability","to":"dist.consistency","satisfaction":"Partial"},
    {"type":"EVIDENCES","from":"A11.async-sync.part1","to":"dist.consistency","completenessScore":60}
  ]
}
```

## 5. 与矩阵的字段映射

- 课程矩阵 → CourseUnit 与 COVERS
- 标准矩阵 → StandardClause 与 SATISFIES
- 仓库矩阵 → RepoFile 与 EVIDENCES

## 6. 校验规则（用于“语义一致性检查工具”）

- 缺失映射：任一 DomainL2 无入边（COVERS/SATISFIES/EVIDENCES）
- 悬空证据：RepoFile 无 EVIDENCES 出边
- 异常重复：同一（A,B）多条等价边、且属性完全一致
- 不一致：覆盖/满足与完整度评分矛盾（如 None 却有高分）

---

更新说明：Schema v1 为最小可用集，后续可扩展 DomainL4/能力点与过程度量模型。
