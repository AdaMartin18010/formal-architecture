Param(
  [string]$FilePath
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $FilePath)) { throw "File not found: $FilePath" }

$dateStr = Get-Date -Format 'yyyyMMdd'
$weekMd = "reports/week-$dateStr.md"
$lines = Get-Content -LiteralPath $FilePath

$insertLines = @(
  "- 统计：reports/stats/latest.json",
  "- 趋势：reports/week/trend.json，图：reports/week/trend.png",
  "- 条款趋势图：reports/week/trend-42010.png、trend-25010.png、trend-15288.png、trend-12207.png",
  "- 任务：reports/tasks/tasks-$dateStr.json、reports/tasks/tasks-$dateStr.md、reports/tasks/overview-$dateStr.md",
  "- 周报导出：$weekMd"
)

# 如果已有任意一行，视为已填充，跳过
foreach ($l in $insertLines) { if ($lines -contains $l) { Write-Host "Skipped: already filled -> $FilePath"; exit 0 } }

# 查找或创建“任务产物”段落
$headerMatch = ($lines | Select-String -Pattern '^###\s*任务产物\s*$').LineNumber
if (-not $headerMatch) {
  $lines += ""
  $lines += '### 任务产物'
  $lines += $insertLines
  Set-Content -LiteralPath $FilePath -Value $lines
  Write-Host "Created section and filled: $FilePath"
  exit 0
}

# 将行号转换为0基索引
$headerIdx = [int]$headerMatch - 1

# 找到下一段标题，限定插入位置
$i = $headerIdx + 1
while ($i -lt $lines.Count -and ($lines[$i] -notmatch '^### ')) { $i++ }

$pre = @()
if ($headerIdx -ge 0) { $pre = $lines[0..$headerIdx] }
$post = if ($i -lt $lines.Count) { $lines[$i..($lines.Count-1)] } else { @() }

$newLines = $pre + $insertLines + $post
Set-Content -LiteralPath $FilePath -Value $newLines
Write-Host "Filled: $FilePath"


