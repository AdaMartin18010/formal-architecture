Param(
  [string]$Weekly = "Analysis/00-总览与导航/内容整合进度报告.md"
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $Weekly)) { throw "Weekly not found: $Weekly" }

$lines = Get-Content -LiteralPath $Weekly
for ($i = 0; $i -lt $lines.Count; $i++) {
  $line = $lines[$i]
  if ($line -match '^### \s*对齐统计占位\d+\s*$') {
    $lines[$i] = '### 对齐统计占位'
  }
  if ($line -match '^### \s*趋势摘要\d+（占位）\s*$') {
    $lines[$i] = '### 趋势摘要（占位）'
  }
}
Set-Content -LiteralPath $Weekly -Value $lines
Write-Host "Weekly headings normalized."
