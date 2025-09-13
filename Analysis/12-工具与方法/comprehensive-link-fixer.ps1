# 综合链接修复脚本
# 处理剩余的断链问题

param(
    [string]$RootPath = ".",
    [string]$OutputFile = "reports\links\comprehensive-fix-report.txt"
)

# 创建输出目录
$outputDir = Split-Path $OutputFile -Parent
if (!(Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force
}

Write-Host "开始综合链接修复..." -ForegroundColor Green

# 获取所有markdown文件
$markdownFiles = Get-ChildItem -Path $RootPath -Filter "*.md" -Recurse

$fixedCount = 0
$totalFiles = $markdownFiles.Count
$fixRules = @()

# 定义综合修复规则
$fixRules += @{
    Pattern = '\]\(\.\./00-主题树与内容索引\.md\)'
    Replacement = '](../00-主题树与内容索引.md)'
    Description = "修复主题树链接的相对路径"
}

$fixRules += @{
    Pattern = '\]\(\.\./00-形式化架构理论统一计划\.md\)'
    Replacement = '](../00-形式化架构理论统一计划.md)'
    Description = "修复统一计划链接的相对路径"
}

$fixRules += @{
    Pattern = '\]\(\.\./13-项目报告与总结/递归合并计划\.md\)'
    Replacement = '](../13-项目报告与总结/递归合并计划.md)'
    Description = "修复递归合并计划链接"
}

$fixRules += @{
    Pattern = '\]\(\.\./13-项目报告与总结/形式化架构理论项目路线图\.md\)'
    Replacement = '](../13-项目报告与总结/形式化架构理论项目路线图.md)'
    Description = "修复项目路线图链接"
}

$fixRules += @{
    Pattern = '\]\(\.\./07-理论统一与整合/03-跨领域证明\.md\)'
    Replacement = '](../07-理论统一与整合/03-跨领域证明.md)'
    Description = "修复跨领域证明链接"
}

$fixRules += @{
    Pattern = '\]\(\.\./README\.md\)'
    Replacement = '](../README.md)'
    Description = "修复README链接"
}

$fixRules += @{
    Pattern = '\]\(\.\./Matter/Theory/理论应用框架\.md\)'
    Replacement = '](../Matter/Theory/理论应用框架.md)'
    Description = "修复理论应用框架链接"
}

$fixRules += @{
    Pattern = '\]\(\.\./1\.1-Microservice/1\.1\.2-Integration/RPC与Web框架集成\.md#1\.1\.2\)'
    Replacement = '](../1.1-Microservice/1.1.2-Integration/RPC与Web框架集成.md#1.1.2)'
    Description = "修复微服务集成链接"
}

$fixRules += @{
    Pattern = '\]\(\.\./archive/README\.md\)'
    Replacement = '](../archive/README.md)'
    Description = "修复归档README链接"
}

$fixRules += @{
    Pattern = '\]\(\.\./相关文档1\.md\)'
    Replacement = '](../相关文档1.md)'
    Description = "修复相关文档1链接"
}

$fixRules += @{
    Pattern = '\]\(\.\./相关文档2\.md\)'
    Replacement = '](../相关文档2.md)'
    Description = "修复相关文档2链接"
}

$fixRules += @{
    Pattern = '\]\(\.\./相关文档3\.md\)'
    Replacement = '](../相关文档3.md)'
    Description = "修复相关文档3链接"
}

$fixRules += @{
    Pattern = '\]\(\.\./上级目录\.md\)'
    Replacement = '](../上级目录.md)'
    Description = "修复上级目录链接"
}

$fixRules += @{
    Pattern = '\]\(\.\./下级目录1/README\.md\)'
    Replacement = '](../下级目录1/README.md)'
    Description = "修复下级目录1链接"
}

$fixRules += @{
    Pattern = '\]\(\.\./下级目录2/README\.md\)'
    Replacement = '](../下级目录2/README.md)'
    Description = "修复下级目录2链接"
}

$fixRules += @{
    Pattern = '\]\(\./01-微服务与框架/01-Gin微服务设计与实现\.md\)'
    Replacement = '](../01-微服务与框架/01-Gin微服务设计与实现.md)'
    Description = "修复微服务框架链接"
}

$fixRules += @{
    Pattern = '\]\(\./02-可观测性/01-OpenTelemetry集成实践\.md\)'
    Replacement = '](../02-可观测性/01-OpenTelemetry集成实践.md)'
    Description = "修复可观测性链接"
}

$fixRules += @{
    Pattern = '\]\(\./03-网络与P2P/01-P2P网络与性能基准测试\.md\)'
    Replacement = '](../03-网络与P2P/01-P2P网络与性能基准测试.md)'
    Description = "修复网络P2P链接"
}

foreach ($file in $markdownFiles) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    $originalContent = $content
    $fileFixed = $false
    
    # 应用修复规则
    foreach ($rule in $fixRules) {
        if ($content -match $rule.Pattern) {
            $content = $content -replace $rule.Pattern, $rule.Replacement
            $fileFixed = $true
            Write-Host "  应用规则: $($rule.Description)" -ForegroundColor Yellow
        }
    }
    
    # 如果文件被修改，保存更改
    if ($fileFixed) {
        $content | Out-File -FilePath $file.FullName -Encoding UTF8 -NoNewline
        $fixedCount++
        Write-Host "修复文件: $($file.FullName)" -ForegroundColor Green
    }
}

# 生成修复报告
$report = @"
综合链接修复报告
================
修复时间: $(Get-Date)
检查目录: $RootPath
检查文件数: $totalFiles
修复文件数: $fixedCount

应用的修复规则:
===============
"@

foreach ($rule in $fixRules) {
    $report += "`n- $($rule.Description)"
    $report += "`n  模式: $($rule.Pattern)"
    $report += "`n  替换: $($rule.Replacement)"
    $report += "`n"
}

$report += "`n修复完成！建议重新运行链接检查验证修复效果。`n"

# 保存报告
$report | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Host "`n综合修复完成！" -ForegroundColor Green
Write-Host "检查文件数: $totalFiles" -ForegroundColor Cyan
Write-Host "修复文件数: $fixedCount" -ForegroundColor Cyan
Write-Host "报告已保存到: $OutputFile" -ForegroundColor Cyan
