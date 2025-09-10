param(
    [Parameter(Mandatory=$true)] [string]$ReportPath,
    [string]$Header = "# 占位文件"
)

if (!(Test-Path -LiteralPath $ReportPath)) {
    Write-Error "报告文件不存在: $ReportPath"
    exit 1
}

$lines = Get-Content -Path $ReportPath -Encoding UTF8
$lastFull = $null
for ($i = $lines.Count - 1; $i -ge 0; $i--) {
    $line = $lines[$i]
    if ($line -match '^FullPath\s*:\s*(.+)$') {
        $lastFull = $Matches[1].Trim()
        break
    }
}

if (-not $lastFull) {
    Write-Output 'NO_FULLPATH_FOUND'
    exit 0
}

Write-Output ("LAST_FULLPATH: " + $lastFull)

if (-not (Test-Path -LiteralPath $lastFull)) {
    $dir = Split-Path -Path $lastFull -Parent
    if (-not (Test-Path -LiteralPath $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    New-Item -ItemType File -Path $lastFull -Force | Out-Null
    Set-Content -Path $lastFull -Encoding UTF8 -Value ($Header + "`n`n> 自动创建以修复链接：" + (Split-Path -Leaf $lastFull))
    Write-Output 'CREATED_PLACEHOLDER'
} else {
    Write-Output 'ALREADY_EXISTS'
}

