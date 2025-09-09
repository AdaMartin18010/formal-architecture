Param(
  [string]$MatrixDir = "Analysis/11-理论统一与整合/对齐矩阵",
  [string]$Weekly = "Analysis/00-总览与导航/内容整合进度报告.md"
)

$ErrorActionPreference = "Stop"

# 允许本进程执行脚本
try { Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force } catch {}

# 计算仓库根目录（当前脚本位于 12-工具与方法/ 下）
$RepoRoot = (Get-Item $PSScriptRoot).Parent.FullName

# 确保输出目录存在
Push-Location $RepoRoot
New-Item -ItemType Directory -Force -Path "reports" | Out-Null
New-Item -ItemType Directory -Force -Path "reports/kg" | Out-Null
New-Item -ItemType Directory -Force -Path "reports/checks" | Out-Null
New-Item -ItemType Directory -Force -Path "reports/stats" | Out-Null
New-Item -ItemType Directory -Force -Path "reports/week" | Out-Null
New-Item -ItemType Directory -Force -Path "reports/tasks" | Out-Null

# 1) 生成知识图谱（根目录脚本）
$KgScript = Join-Path $RepoRoot '知识图谱生成工具.ps1'
if (Test-Path $KgScript) {
& $KgScript -Input $MatrixDir -Output "reports/kg" -Views "domain,standard,course,repo" | Out-Null
} else { Write-Warning "跳过：未找到脚本 $KgScript" }

# 2) 一致性检查（根目录脚本）
$CheckScript = Join-Path $RepoRoot '语义一致性检查工具.ps1'
if (Test-Path $CheckScript) {
& $CheckScript -Paths @(
  Join-Path $MatrixDir "CS-课程-知识域对齐矩阵.md" ,
  Join-Path $MatrixDir "架构标准-知识域对齐矩阵.md" ,
  Join-Path $MatrixDir "仓库文件-知识域映射矩阵.md" ,
  Join-Path $MatrixDir "缺口清单.md"
) -FailOnError:$false -Report "reports/checks/latest.json" | Out-Null
} else { Write-Warning "跳过：未找到脚本 $CheckScript" }

# 3) 统计
& (Join-Path $PSScriptRoot '对齐统计脚本模板.ps1') -MatrixDir $MatrixDir -Report "reports/stats/latest.json" | Out-Null

# 4) 写入周报占位
$date = Get-Date -Format "yyyy-MM-dd"
$append = @()
$append += "`n### 周报自动追加($date)" 
$append += "- 已生成知识图谱与一致性检查报告"
$append += "- 统计见 reports/stats/latest.json"
Add-Content -Path $Weekly -Value ($append -join [Environment]::NewLine)

# 5) 对齐统计写回周报
& (Join-Path $PSScriptRoot '对齐统计写回周报.ps1') -StatsFile "reports/stats/latest.json" -Weekly $Weekly | Out-Null

# 6) 归档统计并更新趋势
& (Join-Path $PSScriptRoot '对齐统计归档与趋势.ps1') -Latest "reports/stats/latest.json" -ArchiveDir "reports/week" | Out-Null

# 7) 趋势摘要写回
& (Join-Path $PSScriptRoot '趋势摘要写回周报.ps1') -Trend "reports/week/trend.json" -Weekly $Weekly -Latest "reports/stats/latest.json" | Out-Null

# 8) 导出趋势表格
& (Join-Path $PSScriptRoot '趋势表格导出.ps1') -Trend "reports/week/trend.json" -CsvOut "reports/week/trend.csv" -MdOut "reports/week/trend.md" -Weekly $Weekly | Out-Null

# 9) 生成整体趋势PNG图
& (Join-Path $PSScriptRoot '趋势图生成.ps1') -Trend "reports/week/trend.json" -OutPng "reports/week/trend.png" | Out-Null
Add-Content -Path $Weekly -Value "- 趋势图见 reports/week/trend.png"

# 10) 生成条款趋势图（42010/25010/15288/12207）
& (Join-Path $PSScriptRoot '条款趋势图生成.ps1') -Trend "reports/week/trend.json" -Out42010 "reports/week/trend-42010.png" -Out25010 "reports/week/trend-25010.png" -Out15288 "reports/week/trend-15288.png" -Out12207 "reports/week/trend-12207.png" | Out-Null
Add-Content -Path $Weekly -Value "- 条款趋势图见 reports/week/trend-42010.png、trend-25010.png、trend-15288.png、trend-12207.png"

# 11) 条款趋势摘要写回
& (Join-Path $PSScriptRoot '条款趋势摘要写回周报.ps1') -Trend "reports/week/trend.json" -Weekly $Weekly | Out-Null

# 12) 缺口转任务清单
& (Join-Path $PSScriptRoot '缺口转任务.ps1') -GapsFile (Join-Path $MatrixDir "缺口清单.md") -OutDir "reports/tasks" | Out-Null
Add-Content -Path $Weekly -Value "- 缺口任务清单见 reports/tasks/tasks-$(Get-Date -Format 'yyyyMMdd').md"

# 13) 任务分组导出
& (Join-Path $PSScriptRoot '任务分组导出.ps1') -TasksJson "reports/tasks/tasks-$(Get-Date -Format 'yyyyMMdd').json" -OutMd "reports/tasks/overview-$(Get-Date -Format 'yyyyMMdd').md" | Out-Null
Add-Content -Path $Weekly -Value "- 任务分组概览见 reports/tasks/overview-$(Get-Date -Format 'yyyyMMdd').md"

# 14) 导出周报
& (Join-Path $PSScriptRoot '周报导出.ps1') -Weekly $Weekly -OutDir "reports" | Out-Null

Write-Host "Weekly pipeline completed."
Write-Host "See exported weekly: reports/week-$(Get-Date -Format 'yyyyMMdd').md"
Pop-Location
