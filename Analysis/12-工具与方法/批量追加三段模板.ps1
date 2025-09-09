Param(
  [string]$Root = "Analysis",
  [string]$Pattern = "*总论-整合版.md"
)

$ErrorActionPreference = "Stop"

$files = Get-ChildItem -Path $Root -Recurse -File -Filter $Pattern
$count = 0
foreach ($f in $files) {
  & (Join-Path $PSScriptRoot '追加三段模板.ps1') -FilePath $f.FullName
  $count++
}
Write-Host ("Processed: " + $count)


