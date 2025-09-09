Param(
  [string]$GapsFile = "Analysis/11-理论统一与整合/对齐矩阵/缺口清单.md",
  [string]$OutDir = "reports/tasks",
  [string]$Date = ""
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $GapsFile)) { throw "Gaps file not found: $GapsFile" }
if (-not $Date) { $Date = Get-Date -Format "yyyyMMdd" }

$content = Get-Content $GapsFile -Raw -Encoding UTF8
$lines = $content -split "\r?\n"

# Find table start (header row begins with '|')
$table = @()
foreach ($ln in $lines) { if ($ln -match '^\|') { $table += $ln } }
if ($table.Count -lt 3) { Write-Host "No table found."; exit 0 }

# Columns: 知识域 | 缺口类型 | 缺口描述 | 优先级 | 负责人 | 计划里程碑 | 证据链接 | 状态
$rows = $table[2..($table.Count-1)]
$tasks = @()
foreach ($r in $rows) {
  $cols = ($r -split '\|').Trim() | Where-Object { $_ -ne '' }
  if ($cols.Count -ge 8) {
    $task = [ordered]@{
      domain = $cols[0]
      gapType = $cols[1]
      description = $cols[2]
      priority = $cols[3]
      owner = $cols[4]
      milestone = $cols[5]
      evidence = $cols[6]
      status = $cols[7]
    }
    $tasks += [pscustomobject]$task
  }
}

if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir | Out-Null }

$jsonOut = Join-Path $OutDir ("tasks-" + $Date + ".json")
($tasks | ConvertTo-Json -Depth 4) | Set-Content $jsonOut -Encoding UTF8

$mdOut = Join-Path $OutDir ("tasks-" + $Date + ".md")
$md = @("# 缺口任务清单（$Date）","","| 域 | 类型 | 描述 | 优先级 | 负责人 | 里程碑 | 证据 | 状态 |","|---|---|---|---|---|---|---|---|")
foreach ($t in $tasks) {
  $md += "| $($t.domain) | $($t.gapType) | $($t.description) | $($t.priority) | $($t.owner) | $($t.milestone) | $($t.evidence) | $($t.status) |"
}
$md -join [Environment]::NewLine | Set-Content $mdOut -Encoding UTF8

Write-Host "Tasks exported to $jsonOut and $mdOut"
