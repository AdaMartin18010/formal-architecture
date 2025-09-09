# 07目录定向链接修复脚本
param(
    [string]$TargetDir = "F:\_src\formal-architecture\Analysis\11-理论统一与整合\07-理论统一与整合"
)

Write-Host "开始修复: $TargetDir" -ForegroundColor Green

$markdownFiles = Get-ChildItem -Path $TargetDir -Filter "*.md" -Recurse

foreach ($file in $markdownFiles) {
    $content = Get-Content -Raw -Encoding UTF8 -Path $file.FullName
    $original = $content

    # 从07目录指向根Analysis的链接需要上跳两级
    $content = $content -replace "\]\(\.\./00-主题树与内容索引\.md\)", "](../../00-主题树与内容索引.md)"
    $content = $content -replace "\]\(\.\./00-形式化架构理论统一计划\.md\)", "](../../00-形式化架构理论统一计划.md)"
    $content = $content -replace "\]\(\.\./13-项目报告与总结/递归合并计划\.md\)", "](../../13-项目报告与总结/递归合并计划.md)"
    $content = $content -replace "\]\(\.\./13-项目报告与总结/形式化架构理论项目路线图\.md\)", "](../../13-项目报告与总结/形式化架构理论项目路线图.md)"

    if ($content -ne $original) {
        $content | Out-File -FilePath $file.FullName -Encoding UTF8 -NoNewline
        Write-Host "fixed: $($file.FullName)" -ForegroundColor Yellow
    }
}

Write-Host "修复完成" -ForegroundColor Cyan
