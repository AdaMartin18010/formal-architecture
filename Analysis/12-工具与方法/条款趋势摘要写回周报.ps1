Param(
  [string]$Trend = "reports/week/trend.json",
  [string]$Weekly = "Analysis/00-总览与导航/内容整合进度报告.md"
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $Trend)) { throw "Trend file not found: $Trend" }

$series = Get-Content $Trend -Raw | ConvertFrom-Json
if ($series.Count -lt 2) { Write-Host "Not enough points for clause summary."; exit 0 }
$last = $series[-1]; $prev = $series[-2]

function Delta($a, $b) {
  $d = [int]$a - [int]$b
  $sign = if ($d -ge 0) { "+" } else { "" }
  return ("{0}{1}" -f $sign, $d)
}

$line42010 = ("- 42010：本期 {0} (Δ{1})，累计 {2}" -f $last.clauses42010, (Delta $last.clauses42010 $prev.clauses42010), $last.clauses42010)
$line25010 = ("- 25010：本期 {0} (Δ{1})，累计 {2}" -f $last.clauses25010, (Delta $last.clauses25010 $prev.clauses25010), $last.clauses25010)
$line15288 = ("- 15288：本期 {0} (Δ{1})，累计 {2}" -f $last.clauses15288, (Delta $last.clauses15288 $prev.clauses15288), $last.clauses15288)
$line12207 = ("- 12207：本期 {0} (Δ{1})，累计 {2}" -f $last.clauses12207, (Delta $last.clauses12207 $prev.clauses12207), $last.clauses12207)

$lines = Get-Content $Weekly
$startIdx = ($lines | Select-String -Pattern '^### 条款趋势摘要（占位）' -SimpleMatch).LineNumber
$block = @('### 条款趋势摘要（占位）', $line42010, $line25010, $line15288, $line12207)

if ($startIdx) {
  $i = $startIdx
  while ($i -le $lines.Count -and $lines[$i] -notmatch '^### ') { $i++ }
  $pre = $lines[0..($startIdx-2)]
  $post = if ($i -le $lines.Count) { $lines[($i-1)..($lines.Count-1)] } else { @() }
  Set-Content -Path $Weekly -Value ($pre + $block + $post)
} else {
  Add-Content -Path $Weekly -Value ""
  Add-Content -Path $Weekly -Value ($block -join [Environment]::NewLine)
}

Write-Host "Clause summary writeback completed."
