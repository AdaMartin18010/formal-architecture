# 轻量级链接检查脚本
param(
    [string]$RootPath = ".",
    [string]$OutputFile = "reports\\links\\quick-link-check.txt"
)

# 确保输出目录
$dir = Split-Path $OutputFile -Parent
if (!(Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }

$files = Get-ChildItem -Path $RootPath -Filter "*.md" -Recurse
$broken = @()
$total = 0
$checked = 0

foreach ($f in $files) {
    $checked++
    $content = Get-Content -Raw -Encoding UTF8 -Path $f.FullName
    if ([string]::IsNullOrEmpty($content)) { continue }
    # 仅匹配内部markdown链接 [text](...md) 或 带锚点的md
    $linkMatches = [regex]::Matches($content, "\]\((?!https?://)([^)]+\.md(?:#[^)]+)?)\)")
    foreach ($m in $linkMatches) {
        $total++
        $rel = $m.Groups[1].Value
        # 去掉锚点部分
        $pathOnly = $rel.Split('#')[0]
        $full = Join-Path $f.DirectoryName $pathOnly
        if (!(Test-Path $full)) {
            $safeIndex = [Math]::Min($m.Index, $content.Length)
            $line = ($content.Substring(0, $safeIndex) -split "`n").Count
            $broken += [PSCustomObject]@{
                SourceFile = $f.FullName
                LinkPath = $rel
                FullPath = $full
                LineNumber = $line
            }
        }
    }
}

$report = @()
$report += "Quick Link Check"
$report += "Checked: $checked files"
$report += "Total links: $total"
$report += "Broken: $($broken.Count)"
$report += ""

# 输出前100条断链以便快速查看
$report += "Top broken (first 100):"
$report += "----------------------"
$report += ($broken | Select-Object -First 100 | ForEach-Object { "${($_.SourceFile)} | ${($_.LineNumber)} | ${($_.LinkPath)}" })

$reportText = ($report -join "`n")
$reportText | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Host "Checked: $checked, Broken: $($broken.Count) -> $OutputFile"
