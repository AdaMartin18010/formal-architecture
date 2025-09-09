Param(
  [string]$TasksJson = "reports/tasks/tasks-$(Get-Date -Format 'yyyyMMdd').json",
  [string]$OutMd = "reports/tasks/overview-$(Get-Date -Format 'yyyyMMdd').md"
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $TasksJson)) { throw "Tasks json not found: $TasksJson" }
$tasks = Get-Content $TasksJson -Raw | ConvertFrom-Json

# Group by priority
$byPrio = $tasks | Group-Object priority | Sort-Object Name
# Group by owner
$byOwner = $tasks | Group-Object owner | Sort-Object Name

$md = @("# 任务分组概览","","## 按优先级分组")
foreach ($g in $byPrio) {
  $md += ("### 优先级 {0} ({1})" -f $g.Name, $g.Count)
  $md += "| 域 | 描述 | 负责人 | 里程碑 | 状态 |"
  $md += "|---|---|---|---|---|"
  foreach ($t in $g.Group) { $md += "| $($t.domain) | $($t.description) | $($t.owner) | $($t.milestone) | $($t.status) |" }
  $md += ""
}

$md += "## 按负责人分组"
foreach ($g in $byOwner) {
  $md += ("### 负责人 {0} ({1})" -f ($g.Name -replace '^$','未指定'), $g.Count)
  $md += "| 域 | 描述 | 优先级 | 里程碑 | 状态 |"
  $md += "|---|---|---|---|---|"
  foreach ($t in $g.Group) { $md += "| $($t.domain) | $($t.description) | $($t.priority) | $($t.milestone) | $($t.status) |" }
  $md += ""
}

$dir = Split-Path $OutMd -Parent
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
$md -join [Environment]::NewLine | Set-Content $OutMd -Encoding UTF8

Write-Host "Task overview exported to $OutMd"
