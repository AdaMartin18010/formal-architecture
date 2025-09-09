Param(
  [string]$Root = "Analysis"
)

$ErrorActionPreference = "Stop"

$files = @()
$files += Get-ChildItem -Path $Root -Recurse -File -Filter '*总论.md'
$files += Get-ChildItem -Path $Root -Recurse -File -Filter '*总论-整合版.md'

$count = 0
foreach ($f in $files) {
  & (Join-Path $PSScriptRoot '任务产物自动填充.ps1') -FilePath $f.FullName
  $count++
}
Write-Host ("Processed: " + $count)
