Param(
  [string]$TargetDir = "Analysis",
  [string]$OutputReport = "reports/checks/alignment-check-$(Get-Date -Format 'yyyyMMdd-HHmmss').md"
)

$ErrorActionPreference = 'Stop'

# 确保报告目录存在
New-Item -ItemType Directory -Force -Path "reports/checks" | Out-Null

function Test-AlignmentSection {
  param(
    [string]$filePath,
    [string]$content
  )
  
  $alignmentSection = $content | Select-String -Pattern '### 2025 对齐' -Context 0, 10
  if (-not $alignmentSection) {
    return @{
      HasSection = $false
      Score = 0
      Issues = @("缺少'2025 对齐'段落")
    }
  }
  
  $sectionContent = $alignmentSection.Context.PostContext -join "`n"
  $score = 0
  $issues = @()
  
  # 检查必需元素
  $requiredElements = @(
    @{ Pattern = '国际\s*Wiki'; Name = '国际Wiki' },
    @{ Pattern = '名校课程'; Name = '名校课程' },
    @{ Pattern = '代表性论文'; Name = '代表性论文' },
    @{ Pattern = '前沿技术'; Name = '前沿技术' },
    @{ Pattern = '对齐状态.*?[:：]'; Name = '对齐状态' }
  )
  
  foreach ($element in $requiredElements) {
    if ($sectionContent -match $element.Pattern) {
      $score += 20
    } else {
      $issues += "缺少$($element.Name)条目"
    }
  }
  
  # 检查对齐状态
  if ($sectionContent -match '对齐状态.*?已完成') {
    $score += 20
  } elseif ($sectionContent -match '对齐状态.*?进行中') {
    $score += 10
  } else {
    $issues += "对齐状态未标记为已完成或进行中"
  }
  
  return @{
    HasSection = $true
    Score = $score
    Issues = $issues
  }
}

function Get-AlignmentReport {
  param([string]$targetDir)
  
  $report = @()
  $report += "# 对齐完整性检查报告"
  $report += ""
  $report += "**检查时间**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
  $report += "**检查目录**: $targetDir"
  $report += ""
  
  $totalFiles = 0
  $alignedFiles = 0
  $totalScore = 0
  $fileScores = @()
  
  # 获取所有Markdown文件
  $mdFiles = Get-ChildItem -Path $targetDir -Recurse -File -Filter "*.md" | Where-Object {
    $_.Name -notlike "*README*" -and 
    $_.Name -notlike "*总论*" -and
    $_.Name -notlike "*索引*" -and
    $_.Name -notlike "*计划*" -and
    $_.Name -notlike "*报告*"
  }
  
  foreach ($file in $mdFiles) {
    $content = Get-Content -Path $file.FullName -Raw
    $alignment = Test-AlignmentSection -filePath $file.FullName -content $content
    
    $totalFiles++
    if ($alignment.HasSection) {
      $alignedFiles++
      $totalScore += $alignment.Score
    }
    
    $fileScores += @{
      File = $file.FullName
      HasSection = $alignment.HasSection
      Score = $alignment.Score
      Issues = $alignment.Issues
    }
  }
  
  # 生成统计信息
  $avgScore = if ($alignedFiles -gt 0) { [math]::Round($totalScore / $alignedFiles, 2) } else { 0 }
  $alignmentRate = if ($totalFiles -gt 0) { [math]::Round(($alignedFiles / $totalFiles) * 100, 2) } else { 0 }
  
  $report += "## 统计摘要"
  $report += ""
  $report += "- **总文件数**: $totalFiles"
  $report += "- **已对齐文件数**: $alignedFiles"
  $report += "- **对齐率**: $alignmentRate%"
  $report += "- **平均对齐分数**: $avgScore/100"
  $report += ""
  
  # 按分数排序显示文件详情
  $report += "## 文件详情"
  $report += ""
  
  $sortedFiles = $fileScores | Sort-Object Score -Descending
  foreach ($file in $sortedFiles) {
    $status = if ($file.HasSection) { "✅" } else { "❌" }
    $report += "### $status $($file.File)"
    $report += ""
    $report += "- **对齐分数**: $($file.Score)/100"
    if ($file.Issues.Count -gt 0) {
      $report += "- **问题**:"
      foreach ($issue in $file.Issues) {
        $report += "  - $issue"
      }
    }
    $report += ""
  }
  
  # 生成建议
  $report += "## 改进建议"
  $report += ""
  $report += "1. **未对齐文件**: 为缺少'2025 对齐'段落的文件添加对齐信息"
  $report += "2. **不完整对齐**: 补充缺失的对齐条目（国际Wiki、名校课程、代表性论文、前沿技术）"
  $report += "3. **状态更新**: 将已完成的对齐标记为'已完成'状态"
  $report += "4. **定期检查**: 建议每周运行一次对齐完整性检查"
  $report += ""
  
  return $report -join "`n"
}

# 执行检查并生成报告
Write-Host "开始对齐完整性检查..."
$report = Get-AlignmentReport -targetDir $TargetDir
Set-Content -Path $OutputReport -Value $report -Encoding UTF8
Write-Host "对齐完整性检查完成，报告已保存至: $OutputReport"

# 显示简要统计
$lines = $report -split "`n"
$stats = $lines | Where-Object { $_ -match "总文件数|已对齐文件数|对齐率|平均对齐分数" }
Write-Host "`n检查结果摘要:"
$stats | ForEach-Object { Write-Host "  $_" }
