Param(
  [string]$ReportPath = "reports/checks/semantic-*.txt"
)

$ErrorActionPreference = 'Stop'
$date = Get-Date -Format 'yyyy-MM-dd-HHmmss'
$fixLog = "reports/checks/semantic-fixes-$date.log"

# 确保报告目录存在
New-Item -ItemType Directory -Force -Path "reports/checks" | Out-Null

function Add-FixLog {
  param([string]$message)
  $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
  Add-Content -Path $fixLog -Value "[$timestamp] $message"
  Write-Host $message
}

Add-FixLog "开始语义差异修复流程"

# 定义修复规则
$fixRules = @{
  '语法' = @{
    'pattern' = '语法.*?[:：]'
    'replacement' = '语法（Grammar）：'
    'note' = '统一术语：语法'
  }
  '语义' = @{
    'pattern' = '语义.*?[:：]'
    'replacement' = '语义（Semantics）：'
    'note' = '统一术语：语义'
  }
  '类型' = @{
    'pattern' = '类型.*?[:：]'
    'replacement' = '类型（Type）：'
    'note' = '统一术语：类型'
  }
  '编译' = @{
    'pattern' = '编译.*?[:：]'
    'replacement' = '编译（Compilation）：'
    'note' = '统一术语：编译'
  }
  '架构' = @{
    'pattern' = '架构.*?[:：]'
    'replacement' = '架构（Architecture）：'
    'note' = '统一术语：架构'
  }
}

# 获取需要修复的文件
$targetFiles = @(
  'Analysis/05-编程语言理论体系/01-语法与语言设计统一理论.md',
  'Analysis/05-编程语言理论体系/02-语义与语法统一理论.md',
  'Analysis/05-编程语言理论体系/03-类型统一理论.md',
  'Analysis/05-编程语言理论体系/04-编译统一理论.md',
  'Analysis/04-软件架构理论体系/00-软件架构理论统一总论.md'
)

$totalFixes = 0

foreach ($file in $targetFiles) {
  if (-not (Test-Path -LiteralPath $file)) {
    Add-FixLog "跳过不存在的文件: $file"
    continue
  }
  
  $content = Get-Content -Path $file -Raw
  $originalContent = $content
  $fileFixes = 0
  
  foreach ($term in $fixRules.Keys) {
    $rule = $fixRules[$term]
    $matches = [regex]::Matches($content, $rule.pattern)
    
    if ($matches.Count -gt 0) {
      $content = $content -replace $rule.pattern, $rule.replacement
      $fileFixes += $matches.Count
      Add-FixLog "文件 $file - 术语 '$term': 修复 $($matches.Count) 处"
    }
  }
  
  if ($content -ne $originalContent) {
    Set-Content -Path $file -Value $content -Encoding UTF8
    $totalFixes += $fileFixes
    Add-FixLog "已更新文件: $file (共 $fileFixes 处修复)"
  } else {
    Add-FixLog "文件无需修复: $file"
  }
}

Add-FixLog "语义差异修复完成，总计修复 $totalFixes 处"
Add-FixLog "修复日志已保存至: $fixLog"

# 生成修复报告
$reportContent = @"
# 语义差异修复报告

**修复时间**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
**修复文件数**: $($targetFiles.Count)
**总修复数**: $totalFixes

## 修复详情

详见日志文件: $fixLog

## 修复规则

1. 统一术语格式：中文术语（英文术语）：
2. 确保与统一术语规范一致
3. 保持文档结构完整性

## 后续建议

1. 运行语义一致性检查验证修复效果
2. 如有必要，进一步细化修复规则
3. 建立定期检查机制
"@

$reportPath = "reports/checks/semantic-fix-report-$date.md"
Set-Content -Path $reportPath -Value $reportContent -Encoding UTF8
Add-FixLog "修复报告已生成: $reportPath"
