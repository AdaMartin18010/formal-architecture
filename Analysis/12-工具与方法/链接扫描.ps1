# 链接完整性检查脚本
# 用途：扫描 Modern 和 Analysis 目录下的 Markdown 本地链接，检测断链
# 用法：在项目根目录执行 .\Analysis\12-工具与方法\链接扫描.ps1

param(
    [string]$RootPath = (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)),
    [string]$OutputFile = "reports\links\broken-links.txt",
    [switch]$IncludeModern = $true,
    [switch]$IncludeAnalysis = $true
)

$reportDir = Split-Path $OutputFile -Parent
if (!(Test-Path -LiteralPath $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
}

Write-Host "链接完整性检查开始..." -ForegroundColor Green
Write-Host "根目录: $RootPath"

# 确定扫描范围
$scanPaths = @()
if ($IncludeModern) { $scanPaths += Join-Path $RootPath "Modern" }
if ($IncludeAnalysis) { $scanPaths += Join-Path $RootPath "Analysis" }

$markdownFiles = @()
foreach ($p in $scanPaths) {
    if (Test-Path $p) {
        $markdownFiles += Get-ChildItem -Path $p -Filter "*.md" -Recurse
    }
}
$totalFiles = ($markdownFiles | Select-Object -Unique).Count

$brokenLinks = New-Object System.Collections.ArrayList
$linkRegex = '\[[^\]]*\]\(([^)]+)\)'
$codeFenceRegex = '```[\s\S]*?```'
$inlineCodeRegex = '`[^`\r\n]+`'

foreach ($file in $markdownFiles) {
    try {
        $raw = Get-Content -LiteralPath $file.FullName -Raw -Encoding UTF8
    } catch {
        Write-Host "读取失败: $($file.FullName)" -ForegroundColor Red
        continue
    }

    $content = [System.Text.RegularExpressions.Regex]::Replace($raw, $codeFenceRegex, '', 'Singleline')
    $content = [System.Text.RegularExpressions.Regex]::Replace($content, $inlineCodeRegex, '')

    $matches = [System.Text.RegularExpressions.Regex]::Matches($content, $linkRegex)
    foreach ($m in $matches) {
        $url = ($m.Groups[1].Value).Trim()
        if ([string]::IsNullOrWhiteSpace($url)) { continue }
        if ($url.StartsWith('#') -or $url.StartsWith('mailto:') -or $url -match '^(https?|ftp)://') { continue }
        if ($url -match '\s' -or $url -match '[:*?"<>|]') { continue }

        $pathOnly = $url.Split('#')[0]
        if ([string]::IsNullOrWhiteSpace($pathOnly)) { continue }

        $resolved = $null
        try {
            $resolved = [System.IO.Path]::GetFullPath((Join-Path $file.DirectoryName $pathOnly))
        } catch { continue }

        $exists = Test-Path -LiteralPath $resolved -ErrorAction SilentlyContinue
        if (-not $exists -and (Test-Path -LiteralPath (Join-Path $resolved 'README.md') -ErrorAction SilentlyContinue)) {
            $exists = $true
        }

        if (-not $exists) {
            try {
                $fileRel = $file.FullName.Replace($RootPath, '').TrimStart('\', '/')
            } catch { $fileRel = $file.FullName }
            [void]$brokenLinks.Add([pscustomobject]@{ File = $fileRel; Link = $url; Resolved = $resolved })
            Write-Host "断链: $fileRel -> $url" -ForegroundColor Yellow
        }
    }
}

$report = @"
链接完整性检查报告
==================
检查时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
根目录: $RootPath
Markdown 文件数: $totalFiles
断链数: $($brokenLinks.Count)

详情:
-----
"@
foreach ($b in $brokenLinks) {
    $report += "`n- 文件: $($b.File)`n  链接: $($b.Link)"
}
$report | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Host "`n检查完成，断链数: $($brokenLinks.Count)" -ForegroundColor $(if ($brokenLinks.Count -eq 0) { "Green" } else { "Yellow" })
Write-Host "报告已保存: $OutputFile"
