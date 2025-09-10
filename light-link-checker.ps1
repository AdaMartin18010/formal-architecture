param(
    [string]$RootPath = ".",
    [string]$OutputFile = "reports\\links\\full-check-report.txt"
)

# 确保输出目录存在
$reportDir = Split-Path $OutputFile -Parent
if (!(Test-Path -LiteralPath $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
}

Write-Host "开始轻量链接检查..." -ForegroundColor Green

# 收集所有Markdown文件
$markdownFiles = Get-ChildItem -Path $RootPath -Filter "*.md" -Recurse
$totalFiles = $markdownFiles.Count

# 结果容器
$brokenLinks = New-Object System.Collections.ArrayList

# 正则：链接、代码块、行内代码（使用单引号字符串避免转义混乱）
$linkRegex = '\[[^\]]*\]\(([^)]+)\)'
$codeFenceRegex = '```[\s\S]*?```'
$inlineCodeRegex = '`[^`\r\n]+`'

foreach ($file in $markdownFiles) {
    $raw = $null
    try {
        $raw = Get-Content -LiteralPath $file.FullName -Raw -Encoding UTF8
    } catch {
        Write-Host ("读取失败: {0} -> {1}" -f $file.FullName, $_.Exception.Message) -ForegroundColor Red
        continue
    }

    # 去除代码块与行内代码
    $content = [System.Text.RegularExpressions.Regex]::Replace($raw, $codeFenceRegex, '', 'Singleline')
    $content = [System.Text.RegularExpressions.Regex]::Replace($content, $inlineCodeRegex, '')

    $matches = [System.Text.RegularExpressions.Regex]::Matches($content, $linkRegex)
    foreach ($m in $matches) {
        $url = ($m.Groups[1].Value).Trim()
        if ([string]::IsNullOrWhiteSpace($url)) { continue }
        # 忽略协议链接、锚点、邮箱
        if ($url.StartsWith('#') -or $url.StartsWith('mailto:') -or $url -match '^(https?|ftp)://') { continue }
        # 忽略含空白或非法字符的伪链接
        if ($url -match '\s') { continue }
        if ($url -match '[:*?"<>|]') { continue }
        # 只检查相对或看起来像文件的链接（分两步判断，避免复杂交替）
        # 忽略包含未转义括号的URL，避免将文件名中的括号误判
        if ($url -match '[()]') { continue }
        $looksLikePath = $false
        if ($url -match '(^\./|^\.\./|/)') { $looksLikePath = $true }
        elseif ($url -match '\.(md|markdown|html|htm|txt|pdf|json)$') { $looksLikePath = $true }
        elseif ($url -match '^[^:]+\.[A-Za-z0-9]+$') { $looksLikePath = $true }
        if (-not $looksLikePath) { continue }

        # 去除锚点
        $pathOnly = $url.Split('#')[0]
        if ([string]::IsNullOrWhiteSpace($pathOnly)) { continue }

        # 解析绝对路径
        $resolved = Join-Path -Path $file.DirectoryName -ChildPath $pathOnly
        try { $resolved = [System.Uri]::UnescapeDataString($resolved) } catch {}

        $exists = $false
        try {
            if (Test-Path -LiteralPath $resolved) { $exists = $true }
            elseif (Test-Path -LiteralPath (Join-Path $resolved 'README.md')) { $exists = $true }
        } catch { $exists = $false }

        if (-not $exists) {
            $rootFull = (Resolve-Path -LiteralPath $RootPath).Path
            $fileRel = ($file.FullName).Substring($rootFull.Length)
            $fileRel = $fileRel -replace '^[\\/]+',''
            [void]$brokenLinks.Add([pscustomobject]@{
                File = $fileRel
                Link = $url
                Resolved = $resolved
            })
            Write-Host ("断链: {0} -> {1}" -f $fileRel, $url) -ForegroundColor Yellow
        }
    }
}

# 生成报告
$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("轻量链接检查报告")
$lines.Add("================")
$lines.Add("检查时间: $(Get-Date)")
$lines.Add("检查目录: $RootPath")
$lines.Add("Markdown文件数: $totalFiles")
$lines.Add("断链数: $($brokenLinks.Count)")
$lines.Add("")
$lines.Add("详情:")
$lines.Add("------")
foreach ($b in $brokenLinks) {
    $lines.Add("- 文件: {0}" -f $b.File)
    $lines.Add("  链接: {0}" -f $b.Link)
    $lines.Add("  解析路径: {0}" -f $b.Resolved)
}

$linesText = [string]::Join("`n", $lines)
$linesText | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Host "检查完成，报告已保存到: $OutputFile" -ForegroundColor Green
