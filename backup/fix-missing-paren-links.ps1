param(
    [string]$RootPath = ".",
    [string]$OutputFile = "reports\\links\\fix-missing-paren-report.txt"
)

# 确保输出目录存在
$reportDir = Split-Path $OutputFile -Parent
if (!(Test-Path -LiteralPath $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
}

Write-Host "开始修复缺失右括号的链接..." -ForegroundColor Green

$markdownFiles = Get-ChildItem -Path $RootPath -Filter "*.md" -Recurse
$changed = 0
$pattern = '(\[[^\]]*\]\([^\)\r\n]+)$'  # 匹配以 ]( 开始且未以 ) 结束的行尾

foreach ($file in $markdownFiles) {
    try {
        $raw = Get-Content -LiteralPath $file.FullName -Raw -Encoding UTF8
    } catch {
        continue
    }

    # 行级处理：仅在行尾补齐 )
    $lines = $raw -split "\r?\n"
    $updated = $false
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        if ($line -match $pattern) {
            $lines[$i] = $line + ")"
            $updated = $true
        }
    }

    if ($updated) {
        ($lines -join "`n") | Out-File -FilePath $file.FullName -Encoding UTF8 -NoNewline
        $changed++
        Write-Host ("已修复: {0}" -f $file.FullName) -ForegroundColor Yellow
    }
}

$report = @()
$report += "缺失右括号链接修复报告"
$report += "======================"
$report += "处理时间: $(Get-Date)"
$report += "处理目录: $RootPath"
$report += "修复文件数: $changed"
($report -join "`n") + "`n" | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Host "修复完成，报告已保存到: $OutputFile" -ForegroundColor Green
