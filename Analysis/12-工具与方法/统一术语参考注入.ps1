Param(
  [string[]]$Files
)

$ErrorActionPreference = 'Stop'
if (-not $Files -or $Files.Count -eq 0) { throw 'No input files provided. Use -Files <list>' }

$date = Get-Date -Format 'yyyy-MM-dd'
$block = @()
$block += '### 统一术语参考'
$block += "- 统一规范：Analysis/00-统一术语与定义规范.md（最后更新：$date）"
$block += '- 关键锚点：#语法-grammar、#语义-semantics、#类型-type、#编译-compilation、#软件架构-software-architecture'

foreach ($f in $Files) {
  if (-not (Test-Path -LiteralPath $f)) { Write-Host "Skip (missing): $f"; continue }
  $lines = Get-Content -LiteralPath $f

  # 已存在则跳过
  if ($lines | Select-String -SimpleMatch '### 统一术语参考') { Write-Host "Skip (exists): $f"; continue }

  # 插入位置：若存在“参考/参考文献/附录/术语/2025 对齐”等段落，则在其前插入，否则末尾追加
  $idx = ($lines | Select-String -Pattern '^(###\s*(参考|参考文献|附录|术语|2025\s*对齐)\s*)$' -CaseSensitive:$false).LineNumber | Select-Object -First 1
  if ($idx) {
    $pre  = if ($idx -gt 1) { $lines[0..($idx-2)] } else { @() }
    $post = $lines[($idx-1)..($lines.Count-1)]
    $new  = $pre + '' + $block + '' + $post
    Set-Content -LiteralPath $f -Value $new
    Write-Host "Injected before matched section: $f"
  } else {
    Add-Content -LiteralPath $f -Value ''
    Add-Content -LiteralPath $f -Value $block
    Write-Host "Appended to end: $f"
  }
}


