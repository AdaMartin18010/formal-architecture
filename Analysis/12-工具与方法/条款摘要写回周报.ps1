Param(
  [string]$Trend = "reports/week/trend.json",
  [string]$Weekly = "Analysis/00-总览与导航/内容整合进度报告.md"
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $Trend)) { throw "Trend file not found: $Trend" }

$series = Get-Content $Trend -Raw | ConvertFrom-Json
if ($series.Count -lt 2) { Write-Host "Not enough points for clause summary."; exit 0 }
$last = $series[-1]; $prev = $series[-2]

function Delta($a, $b) { $d = [int]$a - [int]$b; return ("{0}{1}" -f ($d -ge 0 ? "+" : ""), $d) }

$line1 = ("- 42010：累计 {0} (本期Δ{1})" -f $last.clauses42010, (Delta $last.clauses42010 $prev.clauses42010))
$line2 = ("- 25010：累计 {0} (本期Δ{1})" -f $last.clauses25010, (Delta $last.clauses25010 $prev.clauses25010))

$block = @('### 条款摘要（占位）', $line1, $line2)

$lines = Get-Content $Weekly
$startIdx = ($lines | Select-String -Pattern '^### 条款摘要（占位）' -SimpleMatch).LineNumber
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
