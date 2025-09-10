param(
    [string]$RootPath = ".",
    [string]$OutputFile = "reports\\links\\normalize-dir-links-report.txt"
)

# 确保输出目录存在
$reportDir = Split-Path $OutputFile -Parent
if (!(Test-Path -LiteralPath $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
}

Write-Host "开始目录链接规范化(补全 README.md)..." -ForegroundColor Green

$markdownFiles = Get-ChildItem -Path $RootPath -Filter "*.md" -Recurse
$totalFiles = $markdownFiles.Count
$changedFiles = 0

# 仅匹配相对目录链接，避免 http/https/mailto 与纯锚点
# 模式说明：`](相对路径/)`，相对路径不含 :// 与空白
$pattern = '\]\((?!https?://|mailto:|#)([^)\s]+?)/\)'

foreach ($file in $markdownFiles) {
    $raw = $null
    try {
        $raw = Get-Content -LiteralPath $file.FullName -Raw -Encoding UTF8
    } catch {
        Write-Host ("读取失败: {0} -> {1}" -f $file.FullName, $_.Exception.Message) -ForegroundColor Red
        continue
    }

    $new = [System.Text.RegularExpressions.Regex]::Replace($raw, $pattern, ']($1/README.md)')
    if ($new -ne $raw) {
        $new | Out-File -FilePath $file.FullName -Encoding UTF8 -NoNewline
        $changedFiles++
        Write-Host ("规范化: {0}" -f $file.FullName) -ForegroundColor Yellow
    }
}

$report = @()
$report += "目录链接规范化报告"
$report += "=================="
$report += "处理时间: $(Get-Date)"
$report += "处理目录: $RootPath"
$report += "Markdown文件数: $totalFiles"
$report += "修改文件数: $changedFiles"
$reportText = ($report -join "`n") + "`n"
$reportText | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Host "规范化完成，报告已保存到: $OutputFile" -ForegroundColor Green
