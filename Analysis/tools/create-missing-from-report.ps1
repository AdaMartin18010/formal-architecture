# 从综合链接检查报告中提取 FullPath 并创建缺失占位文件

param(
    [Parameter(Mandatory=$true)] [string]$ReportPath,
    [string]$Header = "# 占位文件",
    [switch]$WhatIf
)

if (!(Test-Path $ReportPath)) {
    Write-Error "报告文件不存在: $ReportPath"
    exit 1
}

# 逐行解析 FullPath，处理换行续行（报告中 FullPath 后一行常以缩进继续）
$lines = Get-Content -Path $ReportPath -Encoding UTF8
$fullPaths = New-Object System.Collections.Generic.List[string]

# 报告字段名集合，用于判定续行的停止
$fieldNames = @(
    'SourceFile','LinkPath','FullPath','LineNumber','Category','RelativePath'
)

for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    # 去除不可见控制字符
    $norm = $line -replace "[\u0000-\u0008\u000B\u000C\u000E-\u001F]",""
    if ($norm -match '^\s*FullPath\s*:\s*(.*)$') {
        $path = $Matches[1].Trim()
        $j = $i + 1
        while ($j -lt $lines.Count) {
            $next = $lines[$j]
            $nextNorm = $next -replace "[\u0000-\u0008\u000B\u000C\u000E-\u001F]",""
            # 若下一行以其他字段开头或为空，则停止续行
            if ($nextNorm -match '^\s*$') { break }
            if ($nextNorm -match '^\s*(' + ($fieldNames -join '|') + ')\s*:\s*') { break }
            if ($nextNorm -match '^\s+(.+)$') {
                $path += ($Matches[1]).Trim()
                $j++
                continue
            } else {
                break
            }
        }
        $i = $j - 1
        if (![string]::IsNullOrWhiteSpace($path)) {
            if (-not ($fullPaths.Contains($path))) { $fullPaths.Add($path) }
        }
    }
}

$created = @()
$exists  = @()

foreach ($p in $fullPaths) {
    try {
        if (Test-Path -LiteralPath $p) {
            $exists += $p
            continue
        }

        $dir = Split-Path -LiteralPath $p -Parent
        if (!(Test-Path -LiteralPath $dir)) {
            if (-not $WhatIf) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
        }

        if (-not $WhatIf) {
            New-Item -ItemType File -Path $p -Force | Out-Null
            Set-Content -Path $p -Encoding UTF8 -Value ("$Header`n`n> 自动创建以修复链接：" + (Split-Path -Leaf $p))
        }
        $created += $p
    }
    catch {
        Write-Warning "创建失败: $p - $($_.Exception.Message)"
    }
}

Write-Host "总计 FullPath 项: $($fullPaths.Count)" -ForegroundColor Cyan
Write-Host "已存在: $($exists.Count)" -ForegroundColor Yellow
Write-Host "新建占位: $($created.Count)" -ForegroundColor Green

if ($created.Count -gt 0) {
    Write-Host "CREATED:" -ForegroundColor Green
    $created | ForEach-Object { Write-Host $_ }
}

exit 0


