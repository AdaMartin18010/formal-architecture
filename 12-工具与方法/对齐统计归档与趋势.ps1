Param(
  [string]$Latest = "reports/stats/latest.json",
  [string]$ArchiveDir = "reports/week"
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $Latest)) { throw "Stats not found: $Latest" }

$today = Get-Date -Format "yyyyMMdd"
if (-not (Test-Path $ArchiveDir)) { New-Item -ItemType Directory -Path $ArchiveDir | Out-Null }

$archiveFile = Join-Path $ArchiveDir ("week-" + $today + ".json")
Copy-Item -Path $Latest -Destination $archiveFile -Force

# 更新趋势文件
$trendFile = Join-Path $ArchiveDir "trend.json"
$point = Get-Content $Latest -Raw | ConvertFrom-Json
$point | Add-Member -NotePropertyName date -NotePropertyValue (Get-Date -Format "yyyy-MM-dd")

$trend = @()
if (Test-Path $trendFile) {
  $trend = Get-Content $trendFile -Raw | ConvertFrom-Json
}
$trend = @($trend) + @($point)
($trend | ConvertTo-Json -Depth 5) | Set-Content $trendFile

Write-Host "Archived to $archiveFile and updated $trendFile"
