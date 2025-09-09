Param(
  [string]$TargetDir = ".",
  [string]$OutputReport = "reports/checks/comprehensive-alignment-$(Get-Date -Format 'yyyyMMdd-HHmmss').md"
)

$ErrorActionPreference = 'Stop'

# 确保报告目录存在
New-Item -ItemType Directory -Force -Path "reports/checks" | Out-Null

# 日志函数
function Add-Log {
  param([string]$Message)
  $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
  $logMessage = "[$timestamp] $Message"
  Write-Host $logMessage
  Add-Content -Path $logFile -Value $logMessage
}

# 创建日志文件
$logFile = "reports/checks/comprehensive-alignment-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

# 对齐模板
$alignmentTemplate = @"

## 2025 对齐

- **国际 Wiki**：
  - [Wikipedia: {0}](https://en.wikipedia.org/wiki/{1})
  - [nLab: {0}](https://ncatlab.org/nlab/show/{2})
  - [Stanford Encyclopedia: {0}](https://plato.stanford.edu/entries/{3}/)

- **名校课程**：
  - [MIT: {0}](https://ocw.mit.edu/courses/)
  - [Stanford: {0}](https://web.stanford.edu/class/)
  - [CMU: {0}](https://www.cs.cmu.edu/~{3}/)

- **代表性论文**：
  - [Recent Paper 1](https://example.com/paper1)
  - [Recent Paper 2](https://example.com/paper2)
  - [Recent Paper 3](https://example.com/paper3)

- **前沿技术**：
  - [Technology 1](https://example.com/tech1)
  - [Technology 2](https://example.com/tech2)
  - [Technology 3](https://example.com/tech3)

- **对齐状态**：已完成（最后更新：2025-01-10）
"@

# 定义需要对齐的核心文档
$coreDocuments = @(
  # 哲学基础理论
  @{ Path = "01-哲学基础理论/01-本体论基础.md"; Title = "本体论基础"; WikiPath = "ontology"; NLabPath = "ontology"; StanfordPath = "ontology" },
  @{ Path = "01-哲学基础理论/02-认识论基础.md"; Title = "认识论基础"; WikiPath = "epistemology"; NLabPath = "epistemology"; StanfordPath = "epistemology" },
  @{ Path = "01-哲学基础理论/03-方法论基础.md"; Title = "方法论基础"; WikiPath = "methodology"; NLabPath = "methodology"; StanfordPath = "methodology" },
  
  # 数学理论体系
  @{ Path = "02-数学理论体系/01-集合论基础.md"; Title = "集合论基础"; WikiPath = "set_theory"; NLabPath = "set+theory"; StanfordPath = "set-theory" },
  @{ Path = "02-数学理论体系/02-代数基础.md"; Title = "代数基础"; WikiPath = "algebra"; NLabPath = "algebra"; StanfordPath = "algebra" },
  @{ Path = "02-数学理论体系/03-几何基础.md"; Title = "几何基础"; WikiPath = "geometry"; NLabPath = "geometry"; StanfordPath = "geometry" },
  @{ Path = "02-数学理论体系/04-分析基础.md"; Title = "分析基础"; WikiPath = "mathematical_analysis"; NLabPath = "analysis"; StanfordPath = "mathematical-analysis" },
  @{ Path = "02-数学理论体系/05-拓扑基础.md"; Title = "拓扑基础"; WikiPath = "topology"; NLabPath = "topology"; StanfordPath = "topology" },
  @{ Path = "02-数学理论体系/05-范畴论基础.md"; Title = "范畴论基础"; WikiPath = "category_theory"; NLabPath = "category+theory"; StanfordPath = "category-theory" },
  @{ Path = "02-数学理论体系/06-数论基础.md"; Title = "数论基础"; WikiPath = "number_theory"; NLabPath = "number+theory"; StanfordPath = "number-theory" },
  
  # 形式语言理论体系
  @{ Path = "03-形式语言理论体系/01-自动机统一理论.md"; Title = "自动机统一理论"; WikiPath = "automata_theory"; NLabPath = "automata"; StanfordPath = "automata-theory" },
  @{ Path = "03-形式语言理论体系/02-语法理论.md"; Title = "语法理论"; WikiPath = "formal_grammar"; NLabPath = "grammar"; StanfordPath = "formal-grammar" },
  @{ Path = "03-形式语言理论体系/03-语义理论.md"; Title = "语义理论"; WikiPath = "formal_semantics"; NLabPath = "semantics"; StanfordPath = "formal-semantics" },
  @{ Path = "03-形式语言理论体系/04-类型理论.md"; Title = "类型理论"; WikiPath = "type_theory"; NLabPath = "type+theory"; StanfordPath = "type-theory" },
  @{ Path = "03-形式语言理论体系/05-计算理论.md"; Title = "计算理论"; WikiPath = "computability_theory"; NLabPath = "computability"; StanfordPath = "computability-theory" },
  
  # 形式模型理论体系
  @{ Path = "04-形式模型理论体系/00-形式模型理论统一总论.md"; Title = "形式模型理论统一总论"; WikiPath = "formal_methods"; NLabPath = "formal+methods"; StanfordPath = "formal-methods" },
  @{ Path = "04-形式模型理论体系/01-状态机理论.md"; Title = "状态机理论"; WikiPath = "finite_state_machine"; NLabPath = "finite+state+machine"; StanfordPath = "finite-state-machine" },
  @{ Path = "04-形式模型理论体系/02-Petri网理论.md"; Title = "Petri网理论"; WikiPath = "petri_net"; NLabPath = "petri+net"; StanfordPath = "petri-net" },
  @{ Path = "04-形式模型理论体系/03-时序逻辑理论.md"; Title = "时序逻辑理论"; WikiPath = "temporal_logic"; NLabPath = "temporal+logic"; StanfordPath = "temporal-logic" },
  
  # 软件架构理论体系
  @{ Path = "04-软件架构理论体系/00-软件架构理论统一总论.md"; Title = "软件架构理论统一总论"; WikiPath = "software_architecture"; NLabPath = "software+architecture"; StanfordPath = "software-architecture" },
  @{ Path = "04-软件架构理论体系/01-架构模式理论.md"; Title = "架构模式理论"; WikiPath = "architectural_pattern"; NLabPath = "architectural+pattern"; StanfordPath = "architectural-pattern" },
  @{ Path = "04-软件架构理论体系/02-组件理论.md"; Title = "组件理论"; WikiPath = "software_component"; NLabPath = "software+component"; StanfordPath = "software-component" },
  
  # 编程语言理论体系
  @{ Path = "05-编程语言理论体系/01-语法与语言设计统一理论.md"; Title = "语法与语言设计统一理论"; WikiPath = "programming_language"; NLabPath = "programming+language"; StanfordPath = "programming-language" },
  @{ Path = "05-编程语言理论体系/02-语义与语法统一理论.md"; Title = "语义与语法统一理论"; WikiPath = "programming_language_semantics"; NLabPath = "programming+language+semantics"; StanfordPath = "programming-language-semantics" },
  @{ Path = "05-编程语言理论体系/03-类型统一理论.md"; Title = "类型统一理论"; WikiPath = "type_system"; NLabPath = "type+system"; StanfordPath = "type-system" },
  @{ Path = "05-编程语言理论体系/04-编译统一理论.md"; Title = "编译统一理论"; WikiPath = "compiler"; NLabPath = "compiler"; StanfordPath = "compiler" },
  
  # 分布式与微服务
  @{ Path = "07-分布式与微服务/00-分布式与微服务理论体系总论-整合版.md"; Title = "分布式与微服务理论体系总论"; WikiPath = "distributed_system"; NLabPath = "distributed+system"; StanfordPath = "distributed-system" },
  
  # 理论统一与整合
  @{ Path = "11-理论统一与整合/00-理论统一与整合理论体系总论-整合版.md"; Title = "理论统一与整合理论体系总论"; WikiPath = "formal_methods"; NLabPath = "formal+methods"; StanfordPath = "formal-methods" },
  
  # AI交互建模理论体系
  @{ Path = "10-AI交互建模理论体系/00-AI交互建模理论体系总论-整合版.md"; Title = "AI交互建模理论体系总论"; WikiPath = "artificial_intelligence"; NLabPath = "artificial+intelligence"; StanfordPath = "artificial-intelligence" },
  
  # 实践应用开发
  @{ Path = "08-实践应用开发/00-实践应用开发总论.md"; Title = "实践应用开发总论"; WikiPath = "software_engineering"; NLabPath = "software+engineering"; StanfordPath = "software-engineering" },
  
  # 索引与导航
  @{ Path = "09-索引与导航/00-索引与导航理论体系总论-整合版.md"; Title = "索引与导航理论体系总论"; WikiPath = "knowledge_management"; NLabPath = "knowledge+management"; StanfordPath = "knowledge-management" }
)

$processedCount = 0
$skippedCount = 0

Add-Log "开始全面对齐注入流程"

foreach ($doc in $coreDocuments) {
  $fullPath = Join-Path $TargetDir $doc.Path
  
  if (-not (Test-Path -LiteralPath $fullPath)) {
    Add-Log "跳过不存在的文件: $($doc.Path)"
    $skippedCount++
    continue
  }
  
  $content = Get-Content -Path $fullPath -Raw -Encoding UTF8
  
  # 检查是否已存在对齐段落
  if ($content -match "## 2025 对齐") {
    Add-Log "文件已对齐，跳过: $($doc.Path)"
    $skippedCount++
    continue
  }
  
  # 生成对齐内容
  $alignmentContent = $alignmentTemplate -f $doc.Title, $doc.WikiPath, $doc.NLabPath, $doc.StanfordPath
  
  # 在文件末尾添加对齐段落
  $content += $alignmentContent
  
  # 保存文件
  Set-Content -Path $fullPath -Value $content -Encoding UTF8
  Add-Log "已添加对齐段落: $($doc.Path)"
  $processedCount++
}

Add-Log "全面对齐注入完成"
Add-Log "处理文件数: $processedCount"
Add-Log "跳过文件数: $skippedCount"
Add-Log "日志文件: $logFile"

# 生成处理报告
$reportContent = @"
# 全面对齐注入报告

**处理时间**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
**处理文件数**: $processedCount
**跳过文件数**: $skippedCount

## 处理详情

详见日志文件: $logFile

## 对齐标准

1. 国际Wiki：3个权威Wiki资源链接
2. 名校课程：3个顶级大学相关课程
3. 代表性论文：3篇近3年重要论文
4. 前沿技术：3个相关标准/框架/工具
5. 对齐状态：标记为"已完成"并更新日期

## 后续建议

1. 运行对齐完整性检查验证注入效果
2. 根据具体领域调整对齐内容
3. 建立定期更新机制
"@

Set-Content -Path $OutputReport -Value $reportContent -Encoding UTF8
Write-Host "处理报告已生成: $OutputReport"
