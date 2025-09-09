Param(
  [string]$Trend = "reports/week/trend.json",
  [string]$Weekly = "Analysis/00-总览与导航/内容整合进度报告.md",
  [string]$Latest = "reports/stats/latest.json"
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $Trend)) { throw "Trend file not found: $Trend" }

$series = Get-Content $Trend -Raw | ConvertFrom-Json
if ($series.Count -lt 2) { Write-Host "Not enough points for summary."; exit 0 }
$last = $series[-1]
$prev = $series[-2]

function Delta($a, $b) {
  $d = [int]$a - [int]$b
  $sign = if ($d -ge 0) { "+" } else { "" }
  return ("{0}{1}" -f $sign, $d)
}

$line1 = ("- 映射行：课程 {0} (Δ{1}) / 标准 {2} (Δ{3}) / 仓库 {4} (Δ{5})" -f $last.courses, (Delta $last.courses $prev.courses), $last.standards, (Delta $last.standards $prev.standards), $last.repo, (Delta $last.repo $prev.repo))
$line2 = ("- 条款命中：42010 {0} (Δ{1}) / 25010 {2} (Δ{3}) / 15288 {4} (Δ{5}) / 12207 {6} (Δ{7})" -f $last.clauses42010, (Delta $last.clauses42010 $prev.clauses42010), $last.clauses25010, (Delta $last.clauses25010 $prev.clauses25010), $last.clauses15288, (Delta $last.clauses15288 $prev.clauses15288), $last.clauses12207, (Delta $last.clauses12207 $prev.clauses12207))
$line3 = ("- 缺口：Open {0} (Δ{1}) / Doing {2} (Δ{3}) / Done {4} (Δ{5})" -f $last.gapsOpen, (Delta $last.gapsOpen $prev.gapsOpen), $last.gapsDoing, (Delta $last.gapsDoing $prev.gapsDoing), $last.gapsDone, (Delta $last.gapsDone $prev.gapsDone))

$extra = @()
$targetsMissing = $true
if (Test-Path $Latest) {
  try {
    $lt = Get-Content $Latest -Raw | ConvertFrom-Json
    if ($lt.coverage -and $lt.coverage.coursesPct -ne $null) {
      $targetsMissing = $false
      $extra += ("- 覆盖率：课程 {0}% / 标准 {1}% / 仓库 {2}%" -f $lt.coverage.coursesPct,$lt.coverage.standardsPct,$lt.coverage.repoPct)
      $extra += ("- 条款覆盖率：42010 {0}% / 25010 {1}% / 15288 {2}% / 12207 {3}%" -f $lt.coverage.c42010Pct,$lt.coverage.c25010Pct,$lt.coverage.c15288Pct,$lt.coverage.c12207Pct)
    }
    if ($lt.convergence -and $lt.convergence.gapsCloseRate -ne $null) {
      $targetsMissing = $false
      $extra += ("- 缺口收敛速率：{0}%" -f $lt.convergence.gapsCloseRate)
    }
  } catch {}
}
if ($targetsMissing) {
  $extra += "- 目标未设置：可编辑 reports/stats/targets.json 以启用覆盖率与收敛速率"
}

$lines = Get-Content $Weekly
$startIdx = ($lines | Select-String -Pattern '^### 趋势摘要（占位）' -SimpleMatch).LineNumber
$block = @('### 趋势摘要（占位）', $line1, $line2, $line3) + $extra

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

Write-Host "Trend summary writeback completed."
