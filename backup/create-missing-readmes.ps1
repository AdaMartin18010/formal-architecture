param(
    [string]$ReportFile = "reports\\links\\full-check-report.txt",
    [string]$RootPath = ".",
    [string]$OutputFile = "reports\\links\\create-readmes-report.txt"
)

# 确保输出目录存在
$reportDir = Split-Path $OutputFile -Parent
if (!(Test-Path -LiteralPath $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
}

if (!(Test-Path -LiteralPath $ReportFile)) {
    Write-Host "未找到断链报告: $ReportFile" -ForegroundColor Red
    exit 1
}

Write-Host "开始创建缺失的 README 占位文件..." -ForegroundColor Green

$lines = Get-Content -LiteralPath $ReportFile -Encoding UTF8
$targets = @()
$currentFileRel = $null
$currentFileAbs = $null

$rootFull = (Resolve-Path -LiteralPath $RootPath).Path

foreach ($line in $lines) {
    if ($line -match '^\s*-\s*文件:\s*(.*)$') {
        $currentFileRel = $Matches[1].Trim()
        if ($currentFileRel) {
            $currentFileAbs = Join-Path -Path $rootFull -ChildPath $currentFileRel
        } else {
            $currentFileAbs = $null
        }
        continue
    }
    if ($line -match '^\s*链接:\s+(.+)$') {
        $link = $Matches[1].Trim()
        if (-not $currentFileAbs) { continue }
        if ($link -notmatch 'README\.md$') { continue }
        # 去除锚点
        $pathOnly = $link.Split('#')[0]
        # 基于文件目录解析绝对路径
        $baseDir = Split-Path -Path $currentFileAbs -Parent
        $abs = Join-Path -Path $baseDir -ChildPath $pathOnly
        # 规范路径
        try { $abs = [System.IO.Path]::GetFullPath($abs) } catch {}
        $dir = Split-Path -Path $abs -Parent
        $targets += [pscustomobject]@{ Rel=$pathOnly; Abs=$abs; Dir=$dir }
    }
}

# 去重
$targets = $targets | Sort-Object -Property Abs -Unique

$created = 0
$skipped = 0
$failed = 0

foreach ($t in $targets) {
    try {
        $shouldCreateDir = $false
        if (!(Test-Path -LiteralPath $t.Dir)) {
            # 允许在 Analysis 与 FormalUnified 下创建
            if ($t.Abs -like (Join-Path $rootFull 'FormalUnified*') -or $t.Abs -like (Join-Path $rootFull 'Analysis*')) {
                $shouldCreateDir = $true
            } else {
                Write-Host ("目录不存在，跳过: {0}" -f $t.Dir) -ForegroundColor DarkYellow
                $skipped++
                continue
            }
        }
        if ($shouldCreateDir) {
            New-Item -ItemType Directory -Path $t.Dir -Force | Out-Null
        }
        if (Test-Path -LiteralPath $t.Abs) {
            $skipped++
            continue
        }
        "# README

该文件为自动生成的占位 README，用于修复目录链接。

- 目录: {0}
- 生成时间: {1}
" -f ($t.Rel), (Get-Date) | Out-File -FilePath $t.Abs -Encoding UTF8
        Write-Host ("已创建: {0}" -f $t.Abs) -ForegroundColor Yellow
        $created++
    } catch {
        Write-Host ("创建失败: {0} -> {1}" -f $t.Abs, $_.Exception.Message) -ForegroundColor Red
        $failed++
    }
}

# 报告
$report = @()
$report += "创建缺失README报告"
$report += "=================="
$report += "来源报告: $ReportFile"
$report += "根目录: $RootPath"
$report += "候选总数: $($targets.Count)"
$report += "已创建: $created"
$report += "已跳过: $skipped"
$report += "失败数: $failed"
($report -join "`n") + "`n" | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Host "创建完成，报告已保存到: $OutputFile" -ForegroundColor Green
