Param(
  [Parameter(Mandatory=$true)] [string]$File,
  [Parameter(Mandatory=$true)] [ValidateSet('语法','语义','类型','编译','软件架构')] [string]$Term
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $File)) { throw "File not found: $File" }

$date = Get-Date -Format 'yyyy-MM-dd'

function Get-Anchor {
  param([string]$term)
  switch ($term) {
    '语法' { return '#语法-grammar' }
    '语义' { return '#语义-semantics' }
    '类型' { return '#类型-type' }
    '编译' { return '#编译-compilation' }
    '软件架构' { return '#软件架构-software-architecture' }
  }
}

$anchor = Get-Anchor -term $Term
$lines = Get-Content -LiteralPath $File

if ($lines | Select-String -SimpleMatch '### 统一定义') { Write-Host "Skip (exists): $File"; exit 0 }

$block = @()
$block += '### 统一定义'
$block += "- 依据：Analysis/00-统一术语与定义规范.md ($date)"
$block += ("- 首选术语：{0}" -f $Term)
$block += ("- 统一锚点：{0}" -f $anchor)
$block += "- 说明：如与本文局部用法存在差异，请以统一规范为准并在本文保留差异说明。"

# 插入位置：正文最前面任一二级标题后，如果不存在则追加到文末
$h2 = ($lines | Select-String -Pattern '^##\s+').LineNumber | Select-Object -First 1
if ($h2) {
  $pre  = $lines[0..($h2-1)]
  $post = $lines[$h2..($lines.Count-1)]
  $new  = $pre + '' + $block + '' + $post
  Set-Content -LiteralPath $File -Value $new
  Write-Host "Injected after first H2: $File"
} else {
  Add-Content -LiteralPath $File -Value ''
  Add-Content -LiteralPath $File -Value $block
  Write-Host "Appended to end: $File"
}


