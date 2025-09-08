Param(
  [string]$Trend = "reports/week/trend.json",
  [string]$CsvOut = "reports/week/trend.csv",
  [string]$MdOut = "reports/week/trend.md",
  [string]$Weekly = ""
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $Trend)) { throw "Trend file not found: $Trend" }

$series = Get-Content $Trend -Raw | ConvertFrom-Json

# 导出CSV
$series | Export-Csv -NoTypeInformation -Path $CsvOut -Force

# 生成Markdown表格
$headers = @("date","courses","standards","repo","clauses42010","clauses25010","clauses15288","clauses12207","gapsOpen","gapsDoing","gapsDone")
$md = @()
$md += "| " + ($headers -join " | ") + " |"
$md += "|" + ($headers | ForEach-Object { " --- " }) -join "|" + "|"
foreach ($p in $series) {
  $row = @($p.date,$p.courses,$p.standards,$p.repo,$p.clauses42010,$p.clauses25010,$p.clauses15288,$p.clauses12207,$p.gapsOpen,$p.gapsDoing,$p.gapsDone)
  $md += "| " + ($row -join " | ") + " |"
}
$md -join [Environment]::NewLine | Set-Content $MdOut

if ($Weekly -and (Test-Path $Weekly)) {
  Add-Content -Path $Weekly -Value "`n### 趋势表格（占位）"
  Add-Content -Path $Weekly -Value "(见 reports/week/trend.md 与 trend.csv)"
}

Write-Host "Trend exported to $CsvOut and $MdOut"
