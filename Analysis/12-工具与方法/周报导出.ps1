Param(
  [string]$Weekly = "Analysis/00-总览与导航/内容整合进度报告.md",
  [string]$OutDir = "reports",
  [string]$Date = ""
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $Weekly)) { throw "Weekly file not found: $Weekly" }
if (-not $Date) { $Date = Get-Date -Format "yyyyMMdd" }

$lines = Get-Content $Weekly

function Extract-Section($title) {
  $start = ($lines | Select-String -Pattern ("^##\s+" + [regex]::Escape($title)) -SimpleMatch).LineNumber
  if (-not $start) { return @() }
  $i = $start
  while ($i -le $lines.Count -and $lines[$i] -notmatch '^## ') { $i++ }
  return $lines[($start-1)..($i-2)]
}

$sections = @()
$sections += Extract-Section "本周变化（对齐矩阵联动）"
$sections += ""
$sections += Extract-Section "对齐统计占位"
$sections += ""
$sections += Extract-Section "趋势摘要（占位）"
$sections += ""
$sections += Extract-Section "趋势归档（占位）"

$outName = Join-Path $OutDir ("week-" + $Date + ".md")
if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir | Out-Null }

$header = @("# 周报（$Date）","","> 本文件由脚本导出，来源：内容整合进度报告.md")
Set-Content -Path $outName -Value ($header + "" + $sections)

Write-Host "Weekly exported to $outName"
