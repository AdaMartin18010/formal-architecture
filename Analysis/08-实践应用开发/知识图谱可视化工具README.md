# 知识图谱可视化工具

## 概述

知识图谱可视化工具是形式化架构理论项目的一部分，旨在提供直观、交互式的知识图谱可视化功能，帮助用户理解理论体系、概念关系和项目结构。本工具基于D3.js实现，支持多种可视化布局、交互操作和查询功能。

## 功能特点

- **知识图谱可视化**：直观展示节点和关系，支持多种布局算法
- **交互功能**：点击节点/关系显示详情，拖拽节点调整位置，缩放和平移图谱
- **查询功能**：支持关键词搜索和高级查询
- **导航功能**：支持导航历史记录和书签管理
- **导出功能**：支持导出为SVG格式

## 快速开始

### 安装

1. 下载项目文件：
   - `知识图谱可视化工具原型.js`
   - `知识图谱可视化工具演示.html`

2. 确保已引入D3.js库（v7或更高版本）

### 使用

1. 在浏览器中打开`知识图谱可视化工具演示.html`
2. 使用控制面板选择视图和布局
3. 与图谱交互：
   - 点击节点查看详情
   - 点击关系查看详情
   - 拖拽节点调整位置
   - 滚轮缩放图谱
   - 拖拽空白区域平移图谱

## 核心组件

### 数据模型

- **KnowledgeGraph**：知识图谱类，包含节点、关系和视图
- **Node**：节点类，表示概念、理论等实体
- **Relation**：关系类，表示节点之间的关系
- **View**：视图类，定义图谱的显示方式

### 可视化引擎

- **VisualizationEngine**：核心可视化引擎，负责渲染图谱和处理交互

## 自定义图谱

可以通过以下方式创建自定义知识图谱：

```javascript
// 创建知识图谱
const graph = new KnowledgeGraph('my-graph', '我的知识图谱');

// 添加节点
const node1 = new Node('n1', 'CONCEPT', '概念1', '这是概念1的描述');
const node2 = new Node('n2', 'CONCEPT', '概念2', '这是概念2的描述');
graph.addNode(node1).addNode(node2);

// 添加关系
const relation = new Relation('r1', 'RELATES_TO', '相关', 'n1', 'n2');
graph.addRelation(relation);

// 创建视图
const view = new View('v1', '默认视图');
view.setFilter({
  nodeTypes: ['CONCEPT'],
  relationTypes: ['RELATES_TO']
});
graph.addView(view);

// 渲染图谱
const engine = new VisualizationEngine('container-id');
engine.initialize().renderGraph(graph);
```

## 配置选项

### 节点类型

- `CONCEPT`：概念
- `THEORY`：理论
- `FILE`：文件
- `DIRECTORY`：目录
- `EXAMPLE`：示例
- `TOOL`：工具
- `TASK`：任务

### 关系类型

- `IS_A`：是一种
- `PART_OF`：是部分
- `DEPENDS_ON`：依赖于
- `REFERENCES`：引用
- `IMPLEMENTS`：实现
- `EXTENDS`：扩展
- `RELATES_TO`：相关
- `TRANSFORMS_TO`：转换为
- `LOCATED_IN`：位于
- `MERGED_TO`：合并为

### 可视化引擎选项

```javascript
const engine = new VisualizationEngine('container-id', {
  width: 800,            // 宽度
  height: 600,           // 高度
  nodeRadius: 10,        // 节点半径
  linkDistance: 150,     // 连线距离
  charge: -300           // 电荷力（负值为排斥）
});
```

## 后续开发计划

1. **知识提取功能**：自动从Markdown文件提取知识
2. **高级分析功能**：中心性分析、社区发现、路径分析
3. **图谱编辑功能**：添加/编辑/删除节点和关系
4. **更多导出格式**：JSON、CSV、交互式HTML
5. **服务端集成**：与后端服务集成，支持大规模知识图谱

## 技术栈

- **D3.js**：核心可视化库
- **JavaScript/TypeScript**：编程语言
- **HTML/CSS**：界面展示

## 版本信息

- **版本**：v62
- **创建时间**：2024年7月
- **状态**：原型开发中

## 贡献指南

欢迎对本工具进行改进和扩展。贡献方式：

1. Fork本仓库
2. 创建特性分支
3. 提交变更
4. 创建Pull Request

## 许可证

本项目采用MIT许可证。

---

-**形式化架构理论项目 © 2024**
