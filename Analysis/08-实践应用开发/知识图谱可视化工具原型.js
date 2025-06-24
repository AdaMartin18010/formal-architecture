/**
 * 知识图谱可视化工具原型
 * 基于D3.js实现的知识图谱可视化工具原型
 * 版本: v62
 * 创建时间: 2024年7月
 */

// 核心数据模型定义
class KnowledgeGraph {
  constructor(id, name, description = '') {
    this.id = id;
    this.name = name;
    this.description = description;
    this.nodes = [];
    this.relations = [];
    this.metadata = {};
    this.views = [];
  }

  addNode(node) {
    this.nodes.push(node);
    return this;
  }

  addRelation(relation) {
    this.relations.push(relation);
    return this;
  }

  addView(view) {
    this.views.push(view);
    return this;
  }

  toJSON() {
    return {
      id: this.id,
      name: this.name,
      description: this.description,
      nodes: this.nodes,
      relations: this.relations,
      metadata: this.metadata,
      views: this.views
    };
  }

  static fromJSON(json) {
    const graph = new KnowledgeGraph(json.id, json.name, json.description);
    graph.nodes = json.nodes;
    graph.relations = json.relations;
    graph.metadata = json.metadata;
    graph.views = json.views;
    return graph;
  }
}

class Node {
  constructor(id, type, label, description = '') {
    this.id = id;
    this.type = type;
    this.label = label;
    this.description = description;
    this.properties = [];
    this.source = {};
    this.metadata = {};
  }

  addProperty(key, value, type = 'STRING') {
    this.properties.push({ key, value, type });
    return this;
  }

  setSource(file, line) {
    this.source = { file, line };
    return this;
  }

  setMetadata(metadata) {
    this.metadata = metadata;
    return this;
  }
}

class Relation {
  constructor(id, type, label, source, target) {
    this.id = id;
    this.type = type;
    this.label = label;
    this.source = source;
    this.target = target;
    this.properties = [];
    this.weight = 1.0;
    this.metadata = {};
  }

  addProperty(key, value, type = 'STRING') {
    this.properties.push({ key, value, type });
    return this;
  }

  setWeight(weight) {
    this.weight = weight;
    return this;
  }

  setMetadata(metadata) {
    this.metadata = metadata;
    return this;
  }
}

class View {
  constructor(id, name, description = '') {
    this.id = id;
    this.name = name;
    this.description = description;
    this.filter = {};
    this.layout = {};
    this.style = {};
  }

  setFilter(filter) {
    this.filter = filter;
    return this;
  }

  setLayout(layout) {
    this.layout = layout;
    return this;
  }

  setStyle(style) {
    this.style = style;
    return this;
  }
}

// 可视化引擎
class VisualizationEngine {
  constructor(containerId, options = {}) {
    this.containerId = containerId;
    this.options = {
      width: options.width || 800,
      height: options.height || 600,
      nodeRadius: options.nodeRadius || 10,
      linkDistance: options.linkDistance || 150,
      charge: options.charge || -300,
      ...options
    };
    
    this.svg = null;
    this.simulation = null;
    this.nodeElements = null;
    this.linkElements = null;
    this.textElements = null;
    
    this.graph = null;
    this.currentView = null;
  }

  initialize() {
    const container = document.getElementById(this.containerId);
    if (!container) {
      console.error(`Container element with id '${this.containerId}' not found`);
      return;
    }

    this.svg = d3.select(container)
      .append('svg')
      .attr('width', this.options.width)
      .attr('height', this.options.height)
      .attr('class', 'knowledge-graph-svg');

    // 添加箭头标记
    this.svg.append('defs').append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '-0 -5 10 10')
      .attr('refX', 20)
      .attr('refY', 0)
      .attr('orient', 'auto')
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('xoverflow', 'visible')
      .append('svg:path')
      .attr('d', 'M 0,-5 L 10 ,0 L 0,5')
      .attr('fill', '#999')
      .style('stroke', 'none');

    return this;
  }

  renderGraph(graph, viewId = null) {
    if (!this.svg) {
      this.initialize();
    }

    this.graph = graph;
    
    // 选择视图
    if (viewId && graph.views.length > 0) {
      this.currentView = graph.views.find(v => v.id === viewId) || graph.views[0];
    } else if (graph.views.length > 0) {
      this.currentView = graph.views[0];
    } else {
      this.currentView = new View('default', 'Default View');
    }

    // 应用过滤器
    let filteredNodes = graph.nodes;
    let filteredRelations = graph.relations;
    
    if (this.currentView.filter && this.currentView.filter.nodeTypes) {
      filteredNodes = filteredNodes.filter(node => 
        this.currentView.filter.nodeTypes.includes(node.type));
    }
    
    if (this.currentView.filter && this.currentView.filter.relationTypes) {
      filteredRelations = filteredRelations.filter(relation => 
        this.currentView.filter.relationTypes.includes(relation.type));
    }

    // 准备D3数据
    const nodes = filteredNodes.map(node => ({...node}));
    const links = filteredRelations.map(relation => ({
      ...relation,
      source: nodes.findIndex(n => n.id === relation.source),
      target: nodes.findIndex(n => n.id === relation.target)
    })).filter(link => link.source !== -1 && link.target !== -1);

    // 清除旧内容
    this.svg.selectAll('*').remove();

    // 重新添加箭头标记
    this.svg.append('defs').append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '-0 -5 10 10')
      .attr('refX', 20)
      .attr('refY', 0)
      .attr('orient', 'auto')
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('xoverflow', 'visible')
      .append('svg:path')
      .attr('d', 'M 0,-5 L 10 ,0 L 0,5')
      .attr('fill', '#999')
      .style('stroke', 'none');

    // 创建力导向模拟
    this.simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(d => d.id).distance(this.options.linkDistance))
      .force('charge', d3.forceManyBody().strength(this.options.charge))
      .force('center', d3.forceCenter(this.options.width / 2, this.options.height / 2));

    // 创建连线
    this.linkElements = this.svg.append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(links)
      .enter().append('line')
      .attr('stroke-width', d => Math.sqrt(d.weight))
      .attr('stroke', '#999')
      .attr('marker-end', 'url(#arrowhead)');

    // 创建节点
    this.nodeElements = this.svg.append('g')
      .attr('class', 'nodes')
      .selectAll('circle')
      .data(nodes)
      .enter().append('circle')
      .attr('r', d => this.getNodeRadius(d))
      .attr('fill', d => this.getNodeColor(d))
      .call(d3.drag()
        .on('start', this.dragStarted.bind(this))
        .on('drag', this.dragged.bind(this))
        .on('end', this.dragEnded.bind(this)));

    // 创建文本标签
    this.textElements = this.svg.append('g')
      .attr('class', 'texts')
      .selectAll('text')
      .data(nodes)
      .enter().append('text')
      .text(d => d.label)
      .attr('font-size', 12)
      .attr('dx', 15)
      .attr('dy', 4);

    // 添加节点点击事件
    this.nodeElements.on('click', this.handleNodeClick.bind(this));

    // 添加连线点击事件
    this.linkElements.on('click', this.handleLinkClick.bind(this));

    // 更新模拟
    this.simulation.on('tick', () => {
      this.linkElements
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      this.nodeElements
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);

      this.textElements
        .attr('x', d => d.x)
        .attr('y', d => d.y);
    });

    return this;
  }

  getNodeRadius(node) {
    if (this.currentView && this.currentView.style && this.currentView.style.node && this.currentView.style.node[node.type]) {
      return this.currentView.style.node[node.type].size || this.options.nodeRadius;
    }
    return this.options.nodeRadius;
  }

  getNodeColor(node) {
    if (this.currentView && this.currentView.style && this.currentView.style.node && this.currentView.style.node[node.type]) {
      return this.currentView.style.node[node.type].color || '#1f77b4';
    }
    
    // 默认颜色映射
    const colorMap = {
      'CONCEPT': '#1f77b4',
      'THEORY': '#2ca02c',
      'FILE': '#d62728',
      'DIRECTORY': '#9467bd',
      'EXAMPLE': '#8c564b',
      'TOOL': '#e377c2',
      'TASK': '#7f7f7f'
    };
    
    return colorMap[node.type] || '#1f77b4';
  }

  dragStarted(event, d) {
    if (!event.active) this.simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }

  dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }

  dragEnded(event, d) {
    if (!event.active) this.simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }

  handleNodeClick(event, d) {
    console.log('Node clicked:', d);
    // 在这里可以显示节点详情面板
    this.showNodeDetails(d);
  }

  handleLinkClick(event, d) {
    console.log('Link clicked:', d);
    // 在这里可以显示关系详情面板
    this.showRelationDetails(d);
  }

  showNodeDetails(node) {
    // 创建或更新节点详情面板
    let detailsPanel = document.getElementById('node-details-panel');
    if (!detailsPanel) {
      detailsPanel = document.createElement('div');
      detailsPanel.id = 'node-details-panel';
      detailsPanel.className = 'details-panel';
      document.body.appendChild(detailsPanel);
    }

    detailsPanel.innerHTML = `
      <div class="details-header">
        <h3>${node.label}</h3>
        <span class="details-type">${node.type}</span>
        <button class="details-close" onclick="document.getElementById('node-details-panel').style.display='none'">×</button>
      </div>
      <div class="details-content">
        <p>${node.description || 'No description available'}</p>
        <h4>Properties</h4>
        <ul>
          ${node.properties.map(p => `<li><strong>${p.key}:</strong> ${p.value}</li>`).join('')}
        </ul>
        ${node.source.file ? `<p><strong>Source:</strong> ${node.source.file}:${node.source.line || 'N/A'}</p>` : ''}
      </div>
    `;

    detailsPanel.style.display = 'block';
  }

  showRelationDetails(relation) {
    // 创建或更新关系详情面板
    let detailsPanel = document.getElementById('relation-details-panel');
    if (!detailsPanel) {
      detailsPanel = document.createElement('div');
      detailsPanel.id = 'relation-details-panel';
      detailsPanel.className = 'details-panel';
      document.body.appendChild(detailsPanel);
    }

    const sourceNode = this.graph.nodes.find(n => n.id === relation.source.id);
    const targetNode = this.graph.nodes.find(n => n.id === relation.target.id);

    detailsPanel.innerHTML = `
      <div class="details-header">
        <h3>${relation.label}</h3>
        <span class="details-type">${relation.type}</span>
        <button class="details-close" onclick="document.getElementById('relation-details-panel').style.display='none'">×</button>
      </div>
      <div class="details-content">
        <p><strong>From:</strong> ${sourceNode ? sourceNode.label : relation.source.id}</p>
        <p><strong>To:</strong> ${targetNode ? targetNode.label : relation.target.id}</p>
        <p><strong>Weight:</strong> ${relation.weight}</p>
        <h4>Properties</h4>
        <ul>
          ${relation.properties.map(p => `<li><strong>${p.key}:</strong> ${p.value}</li>`).join('')}
        </ul>
      </div>
    `;

    detailsPanel.style.display = 'block';
  }
}

// 示例用法
function createExampleGraph() {
  // 创建知识图谱
  const graph = new KnowledgeGraph(
    'theory-graph-v62',
    '形式化架构理论知识图谱',
    '展示形式化架构理论项目的理论体系和概念关系'
  );

  // 添加节点
  const n1 = new Node('n1', 'THEORY', '形式化架构理论体系', '形式化架构理论的总体框架');
  const n2 = new Node('n2', 'THEORY', '软件架构理论体系', '软件架构相关的理论体系');
  const n3 = new Node('n3', 'THEORY', '形式模型理论体系', '形式模型相关的理论体系');
  const n4 = new Node('n4', 'THEORY', '编程语言理论体系', '编程语言相关的理论体系');
  const n5 = new Node('n5', 'THEORY', '形式语言理论体系', '形式语言相关的理论体系');
  
  const n6 = new Node('n6', 'THEORY', '组件与接口统一理论', '组件理论和接口理论的统一');
  const n7 = new Node('n7', 'THEORY', '统一状态转换系统理论', '状态机理论和Petri网理论的统一');
  
  const n8 = new Node('n8', 'THEORY', '组件理论', '研究软件组件的理论');
  const n9 = new Node('n9', 'THEORY', '接口理论', '研究软件接口的理论');
  
  const n10 = new Node('n10', 'THEORY', '状态机理论', '研究状态机的理论');
  const n11 = new Node('n11', 'THEORY', 'Petri网理论', '研究Petri网的理论');

  // 设置节点属性和元数据
  n1.addProperty('field', '计算机科学').setMetadata({ created: '2023-06-01' });
  n2.addProperty('field', '软件工程').setMetadata({ created: '2023-06-02' });
  n3.addProperty('field', '形式化方法').setMetadata({ created: '2023-06-03' });
  n4.addProperty('field', '编程语言').setMetadata({ created: '2023-06-04' });
  n5.addProperty('field', '理论计算机科学').setMetadata({ created: '2023-06-05' });
  
  n6.addProperty('field', '软件工程').setMetadata({ created: '2023-07-01' });
  n7.addProperty('field', '形式化方法').setMetadata({ created: '2023-07-02' });
  
  n8.addProperty('field', '软件工程').setMetadata({ created: '2023-06-10' });
  n9.addProperty('field', '软件工程').setMetadata({ created: '2023-06-11' });
  
  n10.addProperty('field', '形式化方法').setMetadata({ created: '2023-06-12' });
  n11.addProperty('field', '形式化方法').setMetadata({ created: '2023-06-13' });

  // 添加节点到图谱
  graph.addNode(n1).addNode(n2).addNode(n3).addNode(n4).addNode(n5)
       .addNode(n6).addNode(n7).addNode(n8).addNode(n9).addNode(n10).addNode(n11);

  // 添加关系
  graph.addRelation(new Relation('r1', 'PART_OF', '是部分', 'n2', 'n1'));
  graph.addRelation(new Relation('r2', 'PART_OF', '是部分', 'n3', 'n1'));
  graph.addRelation(new Relation('r3', 'PART_OF', '是部分', 'n4', 'n1'));
  graph.addRelation(new Relation('r4', 'PART_OF', '是部分', 'n5', 'n1'));
  
  graph.addRelation(new Relation('r5', 'PART_OF', '是部分', 'n6', 'n2'));
  graph.addRelation(new Relation('r6', 'PART_OF', '是部分', 'n7', 'n3'));
  
  graph.addRelation(new Relation('r7', 'MERGED_TO', '合并为', 'n8', 'n6'));
  graph.addRelation(new Relation('r8', 'MERGED_TO', '合并为', 'n9', 'n6'));
  
  graph.addRelation(new Relation('r9', 'MERGED_TO', '合并为', 'n10', 'n7'));
  graph.addRelation(new Relation('r10', 'MERGED_TO', '合并为', 'n11', 'n7'));
  
  graph.addRelation(new Relation('r11', 'RELATES_TO', '相关', 'n6', 'n7'));

  // 创建视图
  const theoriesView = new View('theories', '理论体系视图', '展示理论体系的层次结构');
  theoriesView.setFilter({
    nodeTypes: ['THEORY'],
    relationTypes: ['PART_OF', 'MERGED_TO', 'RELATES_TO']
  });
  theoriesView.setLayout({
    type: 'hierarchical',
    direction: 'TB'
  });
  theoriesView.setStyle({
    node: {
      'THEORY': {
        shape: 'circle',
        color: '#4CAF50',
        size: 10
      }
    },
    relation: {
      'PART_OF': {
        style: 'solid',
        color: '#000000'
      },
      'MERGED_TO': {
        style: 'dashed',
        color: '#666666'
      },
      'RELATES_TO': {
        style: 'dotted',
        color: '#999999'
      }
    }
  });

  // 添加视图到图谱
  graph.addView(theoriesView);

  return graph;
}

// 初始化函数
function initializeKnowledgeGraph(containerId) {
  // 创建示例图谱
  const graph = createExampleGraph();
  
  // 创建可视化引擎
  const engine = new VisualizationEngine(containerId, {
    width: 800,
    height: 600,
    nodeRadius: 12,
    linkDistance: 150,
    charge: -400
  });
  
  // 渲染图谱
  engine.initialize().renderGraph(graph, 'theories');
  
  return engine;
}

// 添加CSS样式
function addStyles() {
  const style = document.createElement('style');
  style.textContent = `
    .knowledge-graph-svg {
      border: 1px solid #ddd;
      background-color: #f9f9f9;
    }
    
    .nodes circle {
      stroke: #fff;
      stroke-width: 1.5px;
      cursor: pointer;
    }
    
    .nodes circle:hover {
      stroke: #333;
      stroke-width: 2px;
    }
    
    .links line {
      stroke-opacity: 0.6;
      cursor: pointer;
    }
    
    .links line:hover {
      stroke-opacity: 1;
      stroke-width: 2px;
    }
    
    .texts {
      pointer-events: none;
      font-family: Arial, sans-serif;
    }
    
    .details-panel {
      position: fixed;
      top: 20px;
      right: 20px;
      width: 300px;
      background-color: white;
      border: 1px solid #ddd;
      border-radius: 5px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      z-index: 1000;
      display: none;
    }
    
    .details-header {
      background-color: #f5f5f5;
      padding: 10px;
      border-bottom: 1px solid #ddd;
      position: relative;
    }
    
    .details-header h3 {
      margin: 0;
      padding: 0;
      font-size: 16px;
    }
    
    .details-type {
      display: inline-block;
      background-color: #eee;
      padding: 2px 5px;
      border-radius: 3px;
      font-size: 12px;
      margin-left: 5px;
    }
    
    .details-close {
      position: absolute;
      top: 10px;
      right: 10px;
      background: none;
      border: none;
      font-size: 18px;
      cursor: pointer;
      color: #666;
    }
    
    .details-content {
      padding: 10px;
    }
    
    .details-content h4 {
      margin: 10px 0 5px 0;
      font-size: 14px;
    }
    
    .details-content ul {
      margin: 0;
      padding: 0 0 0 20px;
    }
  `;
  document.head.appendChild(style);
}

// 导出函数和类
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    KnowledgeGraph,
    Node,
    Relation,
    View,
    VisualizationEngine,
    createExampleGraph,
    initializeKnowledgeGraph,
    addStyles
  };
} 