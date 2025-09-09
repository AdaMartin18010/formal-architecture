# 综合链接检查脚本
# 更精确的断链识别和修复建议

param(
    [string]$RootPath = ".",
    [string]$OutputFile = "reports\links\comprehensive-link-check-report.txt"
)

# 创建输出目录
$outputDir = Split-Path $OutputFile -Parent
if (!(Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force
}

# 初始化结果
$results = @()
$brokenLinks = @()
$totalLinks = 0
$checkedFiles = 0
$linkCategories = @{
    "内部链接" = 0
    "外部链接" = 0
    "锚点链接" = 0
    "断链" = 0
}

Write-Host "开始综合链接检查..." -ForegroundColor Green

# 获取所有markdown文件
$markdownFiles = Get-ChildItem -Path $RootPath -Filter "*.md" -Recurse

foreach ($file in $markdownFiles) {
    $checkedFiles++
    Write-Host "检查文件 $checkedFiles/$($markdownFiles.Count): $($file.Name)" -ForegroundColor Yellow
    
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    
    # 匹配所有链接模式
    $linkPatterns = @(
        # 相对路径链接 [text](path/file.md)
        '\]\((\.{1,2}\/[^)]+\.md)\)',
        # 相对路径链接 [text](path/file.md#anchor)
        '\]\((\.{1,2}\/[^)]+\.md#[^)]+)\)',
        # 同级目录链接 [text](file.md)
        '\]\(([^/][^)]*\.md)\)',
        # 同级目录链接 [text](file.md#anchor)
        '\]\(([^/][^)]*\.md#[^)]+)\)',
        # 外部链接
        '\]\((https?://[^)]+)\)',
        # 锚点链接
        '\]\(#[^)]+\)'
    )
    
    foreach ($pattern in $linkPatterns) {
        $matches = [regex]::Matches($content, $pattern)
        foreach ($match in $matches) {
            $totalLinks++
            $linkPath = $match.Groups[1].Value
            
            # 跳过代码块中的链接
            $beforeMatch = $content.Substring(0, $match.Index)
            $codeBlockCount = ([regex]::Matches($beforeMatch, '```')).Count
            if ($codeBlockCount % 2 -eq 1) {
                continue
            }
            
            # 分类链接
            if ($linkPath.StartsWith('http')) {
                $linkCategories["外部链接"]++
            } elseif ($linkPath.StartsWith('#')) {
                $linkCategories["锚点链接"]++
            } else {
                $linkCategories["内部链接"]++
                
                # 构建完整路径
                $fullPath = if ($linkPath.StartsWith('./') -or $linkPath.StartsWith('../')) {
                    Join-Path $file.DirectoryName $linkPath
                } else {
                    Join-Path $file.DirectoryName $linkPath
                }
                
                # 检查文件是否存在
                if (!(Test-Path $fullPath)) {
                    $linkCategories["断链"]++
                    $brokenLinks += [PSCustomObject]@{
                        SourceFile = $file.FullName
                        LinkPath = $linkPath
                        FullPath = $fullPath
                        LineNumber = ($content.Substring(0, $match.Index) -split "`n").Count
                        Category = "内部断链"
                        RelativePath = $file.FullName.Replace((Get-Location).Path, "").TrimStart('\')
                    }
                }
            }
        }
    }
}

# 生成详细报告
$report = @"
综合链接完整性检查报告
========================
检查时间: $(Get-Date)
检查目录: $RootPath
检查文件数: $checkedFiles
总链接数: $totalLinks

链接分类统计:
=============
内部链接: $($linkCategories["内部链接"])
外部链接: $($linkCategories["外部链接"])
锚点链接: $($linkCategories["锚点链接"])
断链总数: $($linkCategories["断链"])

断链详情:
=========
"@

if ($brokenLinks.Count -gt 0) {
    # 按源文件分组
    $groupedBroken = $brokenLinks | Group-Object SourceFile
    
    foreach ($group in $groupedBroken) {
        $report += "`n源文件: $($group.Name)`n"
        $report += "断链数量: $($group.Count)`n"
        $report += "-" * 50 + "`n"
        
        foreach ($broken in $group.Group) {
            $report += "  链接: $($broken.LinkPath)`n"
            $report += "  行号: $($broken.LineNumber)`n"
            $report += "  类型: $($broken.Category)`n"
            $report += "  `n"
        }
    }
    
    # 生成修复建议
    $report += "`n修复建议:`n"
    $report += "=========`n"
    
    # 统计最常见的断链模式
    $linkPathPatterns = $brokenLinks | Group-Object LinkPath | Sort-Object Count -Descending | Select-Object -First 20
    
    foreach ($pattern in $linkPathPatterns) {
        $report += "`n模式: $($pattern.Name)`n"
        $report += "出现次数: $($pattern.Count)`n"
        $report += "建议: 检查路径是否正确，或创建缺失文件`n"
    }
} else {
    $report += "`n✅ 所有链接都有效！`n"
}

# 保存报告
$report | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Host "`n综合检查完成！" -ForegroundColor Green
Write-Host "检查文件数: $checkedFiles" -ForegroundColor Cyan
Write-Host "总链接数: $totalLinks" -ForegroundColor Cyan
Write-Host "断链数: $($brokenLinks.Count)" -ForegroundColor $(if ($brokenLinks.Count -eq 0) { "Green" } else { "Red" })
Write-Host "报告已保存到: $OutputFile" -ForegroundColor Cyan

# 返回断链信息
return $brokenLinks
