Param(
  [string]$StatsFile = "reports/stats/latest.json",
  [string]$Weekly = "Analysis/00-总览与导航/内容整合进度报告.md"
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $StatsFile)) { throw "Stats file not found: $StatsFile" }

$stats = Get-Content $StatsFile -Raw | ConvertFrom-Json

$lines = Get-Content $Weekly
$startIdx = ($lines | Select-String -Pattern '^### 对齐统计占位' -SimpleMatch).LineNumber

$block = @()
$block += '### 对齐统计占位'
$block += ("- 课程映射行：{0}；标准映射行：{1}；仓库映射行：{2}" -f $stats.courses, $stats.standards, $stats.repo)
$block += ("- 关键条款映射命中（42010/25010/15288/12207）：{0}/{1}/{2}/{3}" -f $stats.clauses42010, $stats.clauses25010, $stats.clauses15288, $stats.clauses12207)
$block += ("- 缺口状态：Open {0} / Doing {1} / Done {2}" -f $stats.gapsOpen, $stats.gapsDoing, $stats.gapsDone)

if ($startIdx) {
  # 找到段落，替换到下一空行或文档末尾
  $i = $startIdx
  while ($i -le $lines.Count -and $lines[$i] -notmatch '^### ') { $i++ }
  $pre = $lines[0..($startIdx-2)]
  $post = if ($i -le $lines.Count) { $lines[($i-1)..($lines.Count-1)] } else { @() }
  Set-Content -Path $Weekly -Value ($pre + $block + $post)
} else {
  Add-Content -Path $Weekly -Value ""  # 空行
  Add-Content -Path $Weekly -Value ($block -join [Environment]::NewLine)
}

Write-Host "Writeback completed."
