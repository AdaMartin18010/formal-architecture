# 从指定 Markdown 文件提取相对 .md 链接并创建缺失占位文件

param(
    [Parameter(Mandatory=$true)] [string]$MarkdownFile,
    [string]$Header = "# 占位文件",
    [switch]$Recurse
)

if (!(Test-Path -LiteralPath $MarkdownFile)) {
    Write-Error "Markdown 文件不存在: $MarkdownFile"
    exit 1
}

$rootDir = Split-Path -LiteralPath $MarkdownFile -Parent
$pattern = '\]\((?!https?://)(?!#)([^)]+?\.md(?:#[^)]+)?)\)'
$mres = Select-String -Path $MarkdownFile -Pattern $pattern -AllMatches -Encoding UTF8

$relLinks = @{}
foreach ($res in $mres) {
    foreach ($m in $res.Matches) {
        $rel = $m.Groups[1].Value.Trim()
        $rel = ($rel -replace '#[^)]*$', '')
        if (-not [string]::IsNullOrWhiteSpace($rel)) { $relLinks[$rel] = $true }
    }
}

$created = @()
$exists  = @()

foreach ($rel in $relLinks.Keys) {
    $full = Join-Path -Path $rootDir -ChildPath $rel
    if (Test-Path -LiteralPath $full) { $exists += $full; continue }
    $dir = Split-Path -LiteralPath $full -Parent
    if (!(Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    New-Item -ItemType File -Path $full -Force | Out-Null
    Set-Content -Path $full -Encoding UTF8 -Value ("$Header`n`n> 自动创建以修复链接：" + (Split-Path -Leaf $full))
    $created += $full
}

Write-Host "链接总数: $($relLinks.Keys.Count)" -ForegroundColor Cyan
Write-Host "已存在: $($exists.Count)" -ForegroundColor Yellow
Write-Host "新建占位: $($created.Count)" -ForegroundColor Green

if ($Recurse) {
    # 可选：递归处理当前文件中创建的新文件的内部链接（简单深度，避免过度）
    foreach ($f in $created) {
        try {
            & $PSCommandPath -MarkdownFile $f | Out-Null
        } catch {}
    }
}

exit 0


