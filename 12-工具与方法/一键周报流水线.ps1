Param(
  [string]$MatrixDir = "Analysis/11-理论统一与整合/对齐矩阵",
  [string]$Weekly = "Analysis/00-总览与导航/内容整合进度报告.md"
)

$ErrorActionPreference = "Stop"

# 1) 生成知识图谱
./知识图谱生成工具.ps1 -Input $MatrixDir -Output "reports/kg" -Views "domain,standard,course,repo" | Out-Null

# 2) 一致性检查
./语义一致性检查工具.ps1 -Paths @(
  Join-Path $MatrixDir "CS-课程-知识域对齐矩阵.md" ,
  Join-Path $MatrixDir "架构标准-知识域对齐矩阵.md" ,
  Join-Path $MatrixDir "仓库文件-知识域映射矩阵.md" ,
  Join-Path $MatrixDir "缺口清单.md"
) -FailOnError:$false -Report "reports/checks/latest.json" | Out-Null

# 3) 统计
./对齐统计脚本模板.ps1 -MatrixDir $MatrixDir -Report "reports/stats/latest.json" | Out-Null

# 4) 写入周报占位
$date = Get-Date -Format "yyyy-MM-dd"
$append = @()
$append += "`n### 周报自动追加($date)" 
$append += "- 已生成知识图谱与一致性检查报告"
$append += "- 统计见 reports/stats/latest.json"
Add-Content -Path $Weekly -Value ($append -join [Environment]::NewLine)

# 5) 对齐统计写回周报
./对齐统计写回周报.ps1 -StatsFile "reports/stats/latest.json" -Weekly $Weekly | Out-Null

# 6) 归档统计并更新趋势
./对齐统计归档与趋势.ps1 -Latest "reports/stats/latest.json" -ArchiveDir "reports/week" | Out-Null

# 7) 趋势摘要写回
./趋势摘要写回周报.ps1 -Trend "reports/week/trend.json" -Weekly $Weekly | Out-Null

# 8) 导出趋势表格
./趋势表格导出.ps1 -Trend "reports/week/trend.json" -CsvOut "reports/week/trend.csv" -MdOut "reports/week/trend.md" -Weekly $Weekly | Out-Null

# 9) 生成整体趋势PNG图
./趋势图生成.ps1 -Trend "reports/week/trend.json" -OutPng "reports/week/trend.png" | Out-Null
Add-Content -Path $Weekly -Value "- 趋势图见 reports/week/trend.png"

# 10) 生成条款趋势图（42010/25010）
./条款趋势图生成.ps1 -Trend "reports/week/trend.json" -Out42010 "reports/week/trend-42010.png" -Out25010 "reports/week/trend-25010.png" | Out-Null
Add-Content -Path $Weekly -Value "- 条款趋势图见 reports/week/trend-42010.png 与 trend-25010.png"

# 11) 导出周报
./周报导出.ps1 -Weekly $Weekly -OutDir "reports" | Out-Null

Write-Host "Weekly pipeline completed."
Write-Host "See exported weekly: reports/week-$(Get-Date -Format 'yyyyMMdd').md"
