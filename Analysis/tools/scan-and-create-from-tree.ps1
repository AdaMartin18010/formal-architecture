# 递归扫描指定根目录下所有 Markdown 的相对 .md 链接，批量创建缺失占位文件

param(
    [Parameter(Mandatory=$true)] [string]$Root,
    [string]$Header = "# 占位文件"
)

if (!(Test-Path -LiteralPath $Root)) {
    Write-Error "根目录不存在: $Root"
    exit 1
}

$mdFiles = Get-ChildItem -Path $Root -Filter *.md -Recurse -File -ErrorAction SilentlyContinue
$pattern = '\]\((?!https?://)(?!#)([^)]+?\.md)(?:#[^)]+)?\)'

$targets = @{}
foreach ($f in $mdFiles) {
    try {
        $content = Get-Content -LiteralPath $f.FullName -Raw -Encoding UTF8 -ErrorAction Stop
        $allMatches = [regex]::Matches($content, $pattern)
        foreach ($m in $allMatches) {
            $rel = $m.Groups[1].Value.Trim()
            if (-not [string]::IsNullOrWhiteSpace($rel)) {
                $full = Join-Path -Path $f.DirectoryName -ChildPath $rel
                $full = [System.IO.Path]::GetFullPath($full)
                $targets[$full] = $true
            }
        }
    } catch { }
}

$created = @()
foreach ($t in $targets.Keys) {
    if (-not (Test-Path -LiteralPath $t)) {
        $dir = Split-Path -Path $t -Parent
        if (-not (Test-Path -LiteralPath $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
        New-Item -ItemType File -Path $t -Force | Out-Null
        Set-Content -Path $t -Encoding UTF8 -Value ($Header + "`n`n> 自动创建以修复链接：" + (Split-Path -Leaf $t))
        $created += $t
    }
}

Write-Output ("FILES_SCANNED:" + $mdFiles.Count)
Write-Output ("LINK_TARGETS:" + $targets.Keys.Count)
Write-Output ("CREATED:" + $created.Count)

