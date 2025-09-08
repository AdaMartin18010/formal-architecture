Param(
  [string]$MatrixDir = "Analysis/11-理论统一与整合/对齐矩阵",
  [string]$Report = "reports/stats/latest.json",
  [string]$Targets = "reports/stats/targets.json"
)

$newline = [Environment]::NewLine

$stats = [ordered]@{
  courses = 0; standards = 0; repo = 0;
  clauses42010 = 0; clauses25010 = 0; clauses15288 = 0; clauses12207 = 0;
  gapsOpen = 0; gapsDoing = 0; gapsDone = 0;
  coverage = @{ coursesPct = $null; standardsPct = $null; repoPct = $null; c42010Pct = $null; c25010Pct = $null; c15288Pct = $null; c12207Pct = $null };
  convergence = @{ gapsCloseRate = $null }
}

# 简易计数：按表行数估算
$cs = Get-Content "$MatrixDir/CS-课程-知识域对齐矩阵.md" -Raw
$std = Get-Content "$MatrixDir/架构标准-知识域对齐矩阵.md" -Raw
$repo = Get-Content "$MatrixDir/仓库文件-知识域映射矩阵.md" -Raw
$gap = Get-Content "$MatrixDir/缺口清单.md" -Raw

function Count-TableRows($md) {
  ($md -split "\r?\n") | Where-Object { $_ -match '^\|' } | Measure-Object | Select-Object -ExpandProperty Count
}

$stats.courses = (Count-TableRows $cs) - 2
$stats.standards = (Count-TableRows $std) - 2
$stats.repo = (Count-TableRows $repo) - 2

$stats.clauses42010 = ([regex]::Matches($std, '42010')).Count
$stats.clauses25010 = ([regex]::Matches($std, '25010')).Count
$stats.clauses15288 = ([regex]::Matches($std, '15288')).Count
$stats.clauses12207 = ([regex]::Matches($std, '12207')).Count

$stats.gapsOpen = ([regex]::Matches($gap, '\|\s*Open\s*\|')).Count
$stats.gapsDoing = ([regex]::Matches($gap, '\|\s*Doing\s*\|')).Count
$stats.gapsDone = ([regex]::Matches($gap, '\|\s*Done\s*\|')).Count

# 读取目标并计算覆盖率/收敛速率（可选）
if (Test-Path $Targets) {
  try {
    $t = Get-Content $Targets -Raw | ConvertFrom-Json
    function pct($num,$den) { if ($den -and $den -gt 0) { [math]::Round(($num*100.0)/$den,2) } else { $null } }
    $stats.coverage.coursesPct   = pct $stats.courses ($t.coursesTarget)
    $stats.coverage.standardsPct = pct $stats.standards ($t.standardsTarget)
    $stats.coverage.repoPct      = pct $stats.repo ($t.repoTarget)
    $stats.coverage.c42010Pct    = pct $stats.clauses42010 ($t.c42010Target)
    $stats.coverage.c25010Pct    = pct $stats.clauses25010 ($t.c25010Target)
    $stats.coverage.c15288Pct    = pct $stats.clauses15288 ($t.c15288Target)
    $stats.coverage.c12207Pct    = pct $stats.clauses12207 ($t.c12207Target)

    if ($t.gapsBaseline -ne $null -and $t.gapsBaseline -gt 0) {
      $closed = $t.gapsBaseline - $stats.gapsOpen
      $stats.convergence.gapsCloseRate = pct $closed ($t.gapsBaseline)
    }
  } catch { Write-Host "Targets parse failed, skipping coverage calculations." }
}

$dir = Split-Path $Report -Parent
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }

($stats | ConvertTo-Json -Depth 6) | Set-Content $Report
Write-Host "Saved stats => $Report"
