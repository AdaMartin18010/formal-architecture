# 批量修复 01-理论体系 断链
$files = @(
    "05-线性仿射时序类型理论.md",
    "06-形式语言理论深化.md",
    "07-形式模型理论深化.md",
    "08-理论统一与整合.md",
    "09-实践应用开发.md",
    "10-概念定义与论证深化.md",
    "11-统一状态转换系统USTS.md",
    "12-统一模块化系统UMS.md",
    "13-理论映射与证明框架.md"
)
$basePath = "G:\_src\formal-architecture\Analysis\01-理论体系"
foreach ($f in $files) {
    $path = Join-Path $basePath $f
    if (Test-Path $path) {
        $content = Get-Content $path -Raw -Encoding UTF8
        $content = $content -replace '\[相关计划\]\(\.\./13-项目报告与总结/递归合并计划\.md\)', '[项目报告](../13-项目报告与总结/README.md)'
        $content = $content -replace '\(\.\./13-项目报告与总结/递归合并计划\.md\)', '(../13-项目报告与总结/README.md)'
        $content = $content -replace '\]\(\.\./01-理论体系总论\.md\)', '](../00-理论体系总论.md)'
        $content = $content -replace '\]\(01-理论体系总论\.md\)', '](../00-理论体系总论.md)'
        $content = $content -replace '\]\(进度追踪与上下文\.md\)', '](../13-项目报告与总结/进度追踪与上下文.md)'
        $content = $content -replace '\.\./Matter/Theory/[^)]+', '../07-理论统一与整合/00-理论统一与整合总论.md'
        Set-Content $path $content -Encoding UTF8 -NoNewline
        Write-Host "Fixed: $f"
    }
}
