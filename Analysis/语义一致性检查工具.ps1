# 语义一致性检查工具
# 该脚本用于检查合并后文件的语义一致性，包括概念定义、术语使用、形式化表示等

# 定义需要检查的核心概念
$coreConcepts = @(
    @{
        Name = "自动机"
        Keywords = @("自动机", "automata", "DFA", "NFA", "PDA", "图灵机", "Turing machine")
        Files = @("Analysis/03-形式语言理论体系/01-自动机统一理论.md")
    },
    @{
        Name = "语法"
        Keywords = @("语法", "grammar", "产生式", "推导", "终结符", "非终结符", "CFG", "上下文无关文法")
        Files = @("Analysis/05-编程语言理论体系/01-语法与语言设计统一理论.md")
    },
    @{
        Name = "语义"
        Keywords = @("语义", "semantics", "操作语义", "指称语义", "公理语义", "语义分析")
        Files = @("Analysis/05-编程语言理论体系/02-语义与语法统一理论.md")
    },
    @{
        Name = "类型"
        Keywords = @("类型", "type", "类型检查", "类型推导", "多态", "类型系统", "类型安全")
        Files = @("Analysis/05-编程语言理论体系/03-类型统一理论.md")
    },
    @{
        Name = "编译"
        Keywords = @("编译", "compilation", "词法分析", "语法分析", "语义分析", "代码生成", "优化")
        Files = @("Analysis/05-编程语言理论体系/04-编译统一理论.md")
    },
    @{
        Name = "架构"
        Keywords = @("架构", "architecture", "组件", "连接器", "接口", "层次", "服务", "微服务")
        Files = @("Analysis/04-软件架构理论体系/00-软件架构理论统一总论.md")
    }
)

# 定义形式化表示模式
$formalPatterns = @(
    @{
        Name = "数学符号"
        Pattern = '\$\$.*?\$\$|\$.*?\$'
        Description = "数学公式"
    },
    @{
        Name = "形式化定义"
        Pattern = '定义.*?[:：]|Definition.*?:|形式化定义'
        Description = "形式化定义"
    },
    @{
        Name = "算法"
        Pattern = '算法.*?[:：]|Algorithm.*?:|```.*?```'
        Description = "算法或代码块"
    },
    @{
        Name = "图表"
        Pattern = '```mermaid.*?```'
        Description = "Mermaid图表"
    }
)

# 获取所有Markdown文件
$mdFiles = Get-ChildItem -Path "Analysis" -Recurse -File -Filter "*.md"
$results = @()

# 检查核心概念
Write-Host "检查核心概念定义一致性..."
foreach ($concept in $coreConcepts) {
    Write-Host "检查概念: $($concept.Name)"
    $conceptDefinitions = @()
    
    # 在指定文件中查找概念定义
    foreach ($file in $concept.Files) {
        if (Test-Path $file) {
            $content = Get-Content -Path $file -Raw
            
            # 查找概念定义
            foreach ($keyword in $concept.Keywords) {
                if ($content -match "(?<definition>$keyword.*?[:：][^.。]*[.。])") {
                    $definition = $matches['definition']
                    $conceptDefinitions += @{
                        File = $file
                        Definition = $definition.Trim()
                    }
                }
            }
        } else {
            Write-Host "  警告: 文件不存在 - $file"
        }
    }
    
    # 检查定义一致性
    if ($conceptDefinitions.Count -gt 1) {
        for ($i = 0; $i -lt $conceptDefinitions.Count - 1; $i++) {
            for ($j = $i + 1; $j -lt $conceptDefinitions.Count; $j++) {
                $def1 = $conceptDefinitions[$i].Definition
                $def2 = $conceptDefinitions[$j].Definition
                
                # 简单相似度检查 (可以用更复杂的算法替换)
                $similarity = 0
                $words1 = $def1 -split '\s+'
                $words2 = $def2 -split '\s+'
                
                $commonWords = $words1 | Where-Object { $words2 -contains $_ }
                if ($words1.Count -gt 0 -and $words2.Count -gt 0) {
                    $similarity = $commonWords.Count / [Math]::Max($words1.Count, $words2.Count)
                }
                
                # 如果相似度低于阈值，可能存在不一致
                if ($similarity -lt 0.5) {
                    $results += [PSCustomObject]@{
                        Type = "概念定义不一致"
                        Concept = $concept.Name
                        File1 = $conceptDefinitions[$i].File
                        Definition1 = $def1
                        File2 = $conceptDefinitions[$j].File
                        Definition2 = $def2
                        Similarity = $similarity
                    }
                }
            }
        }
    } elseif ($conceptDefinitions.Count -eq 0) {
        Write-Host "  警告: 未找到概念 '$($concept.Name)' 的定义"
    }
}

# 检查形式化表示一致性
Write-Host "检查形式化表示一致性..."
foreach ($pattern in $formalPatterns) {
    Write-Host "检查形式化表示: $($pattern.Name)"
    $formalExpressions = @()
    
    # 在所有文件中查找形式化表示
    foreach ($file in $mdFiles) {
        $content = Get-Content -Path $file.FullName -Raw
        
        # 查找形式化表示
        if ($content -match $pattern.Pattern) {
            $formalExpressions += @{
                File = $file.FullName
                Pattern = $pattern.Name
                Count = ([regex]::Matches($content, $pattern.Pattern)).Count
            }
        }
    }
    
    # 输出形式化表示统计
    if ($formalExpressions.Count -gt 0) {
        Write-Host "  形式化表示 '$($pattern.Name)' 在 $($formalExpressions.Count) 个文件中找到:"
        foreach ($expr in $formalExpressions) {
            Write-Host "    $($expr.File): $($expr.Count) 处"
        }
    } else {
        Write-Host "  警告: 未找到形式化表示 '$($pattern.Name)'"
    }
}

# 输出结果
Write-Host ""
Write-Host "语义一致性检查结果:"
Write-Host "==================="
Write-Host ""

if ($results.Count -eq 0) {
    Write-Host "未发现明显的语义一致性问题。"
} else {
    Write-Host "发现 $($results.Count) 个潜在的语义一致性问题:"
    Write-Host ""
    
    foreach ($result in $results) {
        Write-Host "类型: $($result.Type)"
        Write-Host "概念: $($result.Concept)"
        Write-Host "文件1: $($result.File1)"
        Write-Host "定义1: $($result.Definition1)"
        Write-Host "文件2: $($result.File2)"
        Write-Host "定义2: $($result.Definition2)"
        Write-Host "相似度: $($result.Similarity)"
        Write-Host "-------------------"
    }
    
    Write-Host "建议:"
    Write-Host "1. 检查这些概念定义，确保它们在语义上一致"
    Write-Host "2. 如果定义确实不同，考虑添加注释说明不同视角下的概念理解"
    Write-Host "3. 如果定义应该相同，统一这些定义"
}

Write-Host ""
Write-Host "语义一致性检查完成。" 