# 交叉引用检查工具
# 该脚本用于检查所有Markdown文件中的交叉引用，特别是针对那些已经被合并或重定向的文件

# 定义旧引用和新引用的映射关系
$referenceMapping = @{
    # 自动机理论相关
    "Analysis/03-形式语言理论体系/01-自动机理论.md" = "Analysis/03-形式语言理论体系/01-自动机统一理论.md"
    "Analysis/06-形式模型理论体系/05-自动机理论.md" = "Analysis/03-形式语言理论体系/01-自动机统一理论.md"
    
    # 软件架构理论相关
    "Analysis/04-软件架构理论体系/04-分层架构理论.md" = "Analysis/04-软件架构理论体系/04-分层与云原生架构理论.md"
    "Analysis/04-软件架构理论体系/04-云原生架构理论.md" = "Analysis/04-软件架构理论体系/04-分层与云原生架构理论.md"
    "Analysis/04-软件架构理论体系/06-微服务架构理论.md" = "Analysis/04-软件架构理论体系/06-微服务与WebAssembly架构理论.md"
    "Analysis/04-软件架构理论体系/06-WebAssembly架构理论.md" = "Analysis/04-软件架构理论体系/06-微服务与WebAssembly架构理论.md"
    "Analysis/04-软件架构理论体系/07-架构评估理论.md" = "Analysis/04-软件架构理论体系/07-架构评估与工作流理论.md"
    "Analysis/04-软件架构理论体系/07-工作流架构理论.md" = "Analysis/04-软件架构理论体系/07-架构评估与工作流理论.md"
    
    # 编程语言理论相关
    "Analysis/05-编程语言理论体系/01-语法理论.md" = "Analysis/05-编程语言理论体系/01-语法与语言设计统一理论.md"
    "Analysis/05-编程语言理论体系/01-语言设计理论与原则.md" = "Analysis/05-编程语言理论体系/01-语法与语言设计统一理论.md"
    "Analysis/05-编程语言理论体系/02-语义理论.md" = "Analysis/05-编程语言理论体系/02-语义与语法统一理论.md"
    "Analysis/05-编程语言理论体系/02-语法和语义.md" = "Analysis/05-编程语言理论体系/02-语义与语法统一理论.md"
    "Analysis/05-编程语言理论体系/03-类型理论.md" = "Analysis/05-编程语言理论体系/03-类型统一理论.md"
    "Analysis/05-编程语言理论体系/04-类型系统.md" = "Analysis/05-编程语言理论体系/03-类型统一理论.md"
    "Analysis/05-编程语言理论体系/04-编译理论.md" = "Analysis/05-编程语言理论体系/04-编译统一理论.md"
    "Analysis/05-编程语言理论体系/03-编译器理论.md" = "Analysis/05-编程语言理论体系/04-编译统一理论.md"
    "Analysis/05-编程语言理论体系/07-语言设计理论.md" = "Analysis/05-编程语言理论体系/01-语法与语言设计统一理论.md"
}

# 获取所有Markdown文件
$mdFiles = Get-ChildItem -Path "Analysis" -Recurse -File -Filter "*.md"
$results = @()

# 遍历所有Markdown文件
foreach ($file in $mdFiles) {
    $content = Get-Content -Path $file.FullName -Raw
    
    # 检查每个旧引用
    foreach ($oldRef in $referenceMapping.Keys) {
        # 提取文件名部分，用于简单匹配
        $oldFileName = $oldRef.Split('/')[-1]
        
        # 检查文件内容是否包含旧引用
        if ($content -match [regex]::Escape($oldFileName)) {
            $result = [PSCustomObject]@{
                File = $file.FullName
                OldReference = $oldRef
                NewReference = $referenceMapping[$oldRef]
                NeedsUpdate = $true
            }
            $results += $result
        }
    }
}

# 输出结果
Write-Host "交叉引用检查结果:"
Write-Host "==================="
Write-Host ""

if ($results.Count -eq 0) {
    Write-Host "未发现需要更新的交叉引用。"
} else {
    Write-Host "发现 $($results.Count) 个需要更新的交叉引用:"
    Write-Host ""
    
    foreach ($result in $results) {
        Write-Host "文件: $($result.File)"
        Write-Host "旧引用: $($result.OldReference)"
        Write-Host "新引用: $($result.NewReference)"
        Write-Host "-------------------"
    }
    
    # 询问是否自动修复
    $fix = Read-Host "是否自动修复这些引用? (Y/N)"
    
    if ($fix -eq "Y" -or $fix -eq "y") {
        foreach ($result in $results) {
            $fileContent = Get-Content -Path $result.File -Raw
            $oldFileName = $result.OldReference.Split('/')[-1]
            $newFileName = $result.NewReference.Split('/')[-1]
            
            # 替换文件名
            $updatedContent = $fileContent -replace [regex]::Escape($oldFileName), $newFileName
            
            # 替换完整路径
            $updatedContent = $updatedContent -replace [regex]::Escape($result.OldReference), $result.NewReference
            
            # 保存更新后的内容
            Set-Content -Path $result.File -Value $updatedContent
            
            Write-Host "已更新: $($result.File)"
        }
        
        Write-Host "所有引用已更新。"
    } else {
        Write-Host "未进行任何修改。"
    }
}

Write-Host ""
Write-Host "交叉引用检查完成。" 