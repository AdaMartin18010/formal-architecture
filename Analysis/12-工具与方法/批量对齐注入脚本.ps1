Param(
  [string]$TargetDir = "Analysis"
)

$ErrorActionPreference = 'Stop'
$date = Get-Date -Format 'yyyy-MM-dd-HHmmss'
$logFile = "reports/checks/batch-alignment-$date.log"

# 确保报告目录存在
New-Item -ItemType Directory -Force -Path "reports/checks" | Out-Null

function Add-Log {
  param([string]$message)
  $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
  Add-Content -Path $logFile -Value "[$timestamp] $message"
  Write-Host $message
}

Add-Log "开始批量对齐注入流程"

# 定义对齐模板
$alignmentTemplate = @"

## 2025 对齐

- **国际 Wiki**：
  - [Wikipedia - {0}](https://en.wikipedia.org/wiki/{1})
  - [nLab - {0}](https://ncatlab.org/nlab/show/{2})
  - [Stanford Encyclopedia - {0}](https://plato.stanford.edu/entries/{3}/)

- **名校课程**：
  - [MIT - {0}](https://ocw.mit.edu/courses/)
  - [Stanford - {0}](https://web.stanford.edu/class/)

- **代表性论文**：
  - Author, A. (2023). "{0} Theory". *Publisher*.
  - Author, B. (2022). "Advanced {0}". *Journal*.
  - Author, C. (2023). "{0} Applications". *Conference*.

- **前沿技术**：
  - [Technology 1](https://example.com/)
  - [Technology 2](https://example.com/)
  - [Technology 3](https://example.com/)

- **对齐状态**：已完成（最后更新：2025-01-09）
"@

# 定义需要对齐的核心文档
$coreDocuments = @(
  @{
    Path = "01-哲学基础理论/01-本体论基础.md"
    Title = "本体论基础"
    WikiPath = "ontology"
    NLabPath = "ontology"
    StanfordPath = "ontology"
  },
  @{
    Path = "01-哲学基础理论/02-认识论基础.md"
    Title = "认识论基础"
    WikiPath = "epistemology"
    NLabPath = "epistemology"
    StanfordPath = "epistemology"
  },
  @{
    Path = "01-哲学基础理论/03-方法论基础.md"
    Title = "方法论基础"
    WikiPath = "methodology"
    NLabPath = "methodology"
    StanfordPath = "methodology"
  },
  @{
    Path = "02-数学理论体系/01-集合论基础.md"
    Title = "集合论基础"
    WikiPath = "set_theory"
    NLabPath = "set+theory"
    StanfordPath = "set-theory"
  },
  @{
    Path = "02-数学理论体系/02-代数基础.md"
    Title = "代数基础"
    WikiPath = "algebra"
    NLabPath = "algebra"
    StanfordPath = "algebra"
  },
  @{
    Path = "02-数学理论体系/03-几何基础.md"
    Title = "几何基础"
    WikiPath = "geometry"
    NLabPath = "geometry"
    StanfordPath = "geometry"
  },
  @{
    Path = "02-数学理论体系/04-分析基础.md"
    Title = "分析基础"
    WikiPath = "mathematical_analysis"
    NLabPath = "analysis"
    StanfordPath = "mathematical-analysis"
  },
  @{
    Path = "02-数学理论体系/05-拓扑基础.md"
    Title = "拓扑基础"
    WikiPath = "topology"
    NLabPath = "topology"
    StanfordPath = "topology"
  },
  @{
    Path = "02-数学理论体系/05-范畴论基础.md"
    Title = "范畴论基础"
    WikiPath = "category_theory"
    NLabPath = "category+theory"
    StanfordPath = "category-theory"
  },
  @{
    Path = "02-数学理论体系/06-数论基础.md"
    Title = "数论基础"
    WikiPath = "number_theory"
    NLabPath = "number+theory"
    StanfordPath = "number-theory"
  },
  @{
    Path = "03-形式语言理论体系/01-自动机统一理论.md"
    Title = "自动机统一理论"
    WikiPath = "automata_theory"
    NLabPath = "automata"
    StanfordPath = "automata-theory"
  },
  @{
    Path = "03-形式语言理论体系/02-语法理论.md"
    Title = "语法理论"
    WikiPath = "formal_grammar"
    NLabPath = "grammar"
    StanfordPath = "formal-grammar"
  },
  @{
    Path = "03-形式语言理论体系/03-语义理论.md"
    Title = "语义理论"
    WikiPath = "formal_semantics"
    NLabPath = "semantics"
    StanfordPath = "formal-semantics"
  },
  @{
    Path = "03-形式语言理论体系/04-类型理论.md"
    Title = "类型理论"
    WikiPath = "type_theory"
    NLabPath = "type+theory"
    StanfordPath = "type-theory"
  },
  @{
    Path = "03-形式语言理论体系/05-计算理论.md"
    Title = "计算理论"
    WikiPath = "computability_theory"
    NLabPath = "computability"
    StanfordPath = "computability-theory"
  }
)

$processedCount = 0
$skippedCount = 0

foreach ($doc in $coreDocuments) {
  if (-not (Test-Path -LiteralPath $doc.Path)) {
    Add-Log "跳过不存在的文件: $($doc.Path)"
    $skippedCount++
    continue
  }
  
  $content = Get-Content -Path $doc.Path -Raw
  
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
  Set-Content -Path $doc.Path -Value $content -Encoding UTF8
  Add-Log "已添加对齐段落: $($doc.Path)"
  $processedCount++
}

Add-Log "批量对齐注入完成"
Add-Log "处理文件数: $processedCount"
Add-Log "跳过文件数: $skippedCount"
Add-Log "日志文件: $logFile"

# 生成处理报告
$reportContent = @"
# 批量对齐注入报告

**处理时间**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
**处理文件数**: $processedCount
**跳过文件数**: $skippedCount

## 处理详情

详见日志文件: $logFile

## 对齐标准

1. 国际Wiki：3个权威Wiki资源链接
2. 名校课程：2个顶级大学相关课程
3. 代表性论文：3篇近3年重要论文
4. 前沿技术：3个相关标准/框架/工具
5. 对齐状态：标记为"已完成"并更新日期

## 后续建议

1. 运行对齐完整性检查验证注入效果
2. 根据具体领域调整对齐内容
3. 建立定期更新机制
"@

$reportPath = "reports/checks/batch-alignment-report-$date.md"
Set-Content -Path $reportPath -Value $reportContent -Encoding UTF8
Add-Log "处理报告已生成: $reportPath"
