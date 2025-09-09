# 知识图谱生成工具
# 该脚本用于从Markdown文件中提取概念和关系，生成知识图谱

# 定义理论体系
$theorySystems = @(
    @{
        Name = "哲学基础理论体系"
        Path = "Analysis/01-哲学基础理论体系"
        Color = "lightblue"
    },
    @{
        Name = "数学理论体系"
        Path = "Analysis/02-数学理论体系"
        Color = "lightgreen"
    },
    @{
        Name = "形式语言理论体系"
        Path = "Analysis/03-形式语言理论体系"
        Color = "lightyellow"
    },
    @{
        Name = "软件架构理论体系"
        Path = "Analysis/04-软件架构理论体系"
        Color = "lightpink"
    },
    @{
        Name = "编程语言理论体系"
        Path = "Analysis/05-编程语言理论体系"
        Color = "lightcoral"
    },
    @{
        Name = "形式模型理论体系"
        Path = "Analysis/06-形式模型理论体系"
        Color = "lightcyan"
    }
)

# 定义核心概念及其关键词
$coreConcepts = @(
    @{
        Name = "自动机"
        Keywords = @("自动机", "automata", "DFA", "NFA", "PDA", "图灵机")
    },
    @{
        Name = "语法"
        Keywords = @("语法", "grammar", "产生式", "推导", "终结符", "非终结符")
    },
    @{
        Name = "语义"
        Keywords = @("语义", "semantics", "操作语义", "指称语义", "公理语义")
    },
    @{
        Name = "类型"
        Keywords = @("类型", "type", "类型检查", "类型推导", "多态", "类型系统")
    },
    @{
        Name = "编译"
        Keywords = @("编译", "compilation", "词法分析", "语法分析", "语义分析", "代码生成")
    },
    @{
        Name = "架构"
        Keywords = @("架构", "architecture", "组件", "连接器", "接口", "层次", "服务")
    },
    @{
        Name = "状态机"
        Keywords = @("状态机", "state machine", "状态转换", "状态空间")
    },
    @{
        Name = "形式验证"
        Keywords = @("形式验证", "formal verification", "模型检查", "定理证明")
    }
)

# 提取文件中的概念
function Extract-Concepts {
    param (
        [string]$filePath,
        [array]$conceptList
    )
    
    $content = Get-Content -Path $filePath -Raw
    $foundConcepts = @()
    
    foreach ($concept in $conceptList) {
        foreach ($keyword in $concept.Keywords) {
            if ($content -match $keyword) {
                if ($foundConcepts -notcontains $concept.Name) {
                    $foundConcepts += $concept.Name
                }
                break
            }
        }
    }
    
    return $foundConcepts
}

# 提取文件之间的引用关系
function Extract-References {
    param (
        [string]$filePath,
        [array]$allFiles
    )
    
    $content = Get-Content -Path $filePath -Raw
    $references = @()
    
    foreach ($file in $allFiles) {
        $fileName = [System.IO.Path]::GetFileName($file)
        if ($content -match [regex]::Escape($fileName) -and $file -ne $filePath) {
            $references += $file
        }
    }
    
    return $references
}

# 生成Mermaid图表代码
function Generate-MermaidCode {
    param (
        [array]$nodes,
        [array]$edges
    )
    
    $sb = New-Object System.Text.StringBuilder
    [void]$sb.AppendLine('```mermaid')
    [void]$sb.AppendLine('graph TD')
    
    # 添加节点
    foreach ($node in $nodes) {
        $id = $node.Id
        $label = $node.Label
        $color = $node.Color
        
        [void]$sb.AppendLine(("    {0}[{1}]" -f $id, $label))
        if ($color) {
            [void]$sb.AppendLine(("    style {0} fill:{1}" -f $id, $color))
        }
    }
    
    # 添加边
    foreach ($edge in $edges) {
        $from = $edge.From
        $to = $edge.To
        $label = $edge.Label
        
        if ($label) {
            [void]$sb.AppendLine(("    {0} -->|{1}| {2}" -f $from, $label, $to))
        } else {
            [void]$sb.AppendLine(("    {0} --> {1}" -f $from, $to))
        }
    }
    
    [void]$sb.AppendLine('```')
    return $sb.ToString()
}

# 主函数
function Generate-KnowledgeGraph {
    # 获取所有Markdown文件
    $allFiles = Get-ChildItem -Path . -Recurse -File -Filter '*.md' | Select-Object -ExpandProperty FullName
    
    $nodes = @()
    $edges = @()
    $nodeId = 1
    $fileToNodeId = @{}
    
    # 为每个文件创建节点
    foreach ($file in $allFiles) {
        $fileName = [System.IO.Path]::GetFileName($file)
        $fileDir = [System.IO.Path]::GetDirectoryName($file)
        
        # 确定节点颜色
        $color = 'white'
        foreach ($system in $theorySystems) {
            $dirPattern = ('*{0}*' -f $system.Path)
            if ($fileDir -like $dirPattern) {
                $color = $system.Color
                break
            }
        }
        
        $id = ('node{0}' -f $nodeId)
        $fileToNodeId[$file] = $id
        
        $nodes += @{
            Id = $id
            Label = $fileName
            Color = $color
            File = $file
        }
        
        $nodeId++
    }
    
    # 提取文件之间的引用关系
    foreach ($file in $allFiles) {
        $references = Extract-References -filePath $file -allFiles $allFiles
        
        foreach ($ref in $references) {
            $edges += @{
                From = $fileToNodeId[$file]
                To = $fileToNodeId[$ref]
                Label = "引用"
            }
        }
    }
    
    # 提取概念关系
    $conceptToFiles = @{}
    foreach ($file in $allFiles) {
        $concepts = Extract-Concepts -filePath $file -conceptList $coreConcepts
        
        foreach ($concept in $concepts) {
            if (-not $conceptToFiles.ContainsKey($concept)) {
                $conceptToFiles[$concept] = @()
            }
            $conceptToFiles[$concept] += $file
        }
    }
    
    # 为每个概念创建节点
    foreach ($concept in $coreConcepts) {
        $conceptName = $concept.Name
        if ($conceptToFiles.ContainsKey($conceptName)) {
            $id = ('concept{0}' -f $nodeId)
            
            $nodes += @{
                Id = $id
                Label = $conceptName
                Color = "lightorange"
            }
            
            foreach ($file in $conceptToFiles[$conceptName]) {
                $edges += @{
                    From = $id
                    To = $fileToNodeId[$file]
                    Label = "包含"
                }
            }
            
            $nodeId++
        }
    }
    
    # 生成理论体系图
    $systemNodes = @()
    $systemEdges = @()
    $systemNodeId = 1
    
    foreach ($system in $theorySystems) {
        $id = ('system{0}' -f $systemNodeId)
        
        $systemNodes += @{
            Id = $id
            Label = $system.Name
            Color = $system.Color
        }
        
        $systemNodeId++
    }
    
    # 添加理论体系之间的关系
    $systemEdges += @{
        From = "system1"
        To = "system2"
        Label = "基础支撑"
    }
    
    $systemEdges += @{
        From = "system2"
        To = "system3"
        Label = "形式化基础"
    }
    
    $systemEdges += @{
        From = "system3"
        To = "system5"
        Label = "语言理论支持"
    }
    
    $systemEdges += @{
        From = "system3"
        To = "system6"
        Label = "形式化方法"
    }
    
    $systemEdges += @{
        From = "system5"
        To = "system4"
        Label = "实现基础"
    }
    
    $systemEdges += @{
        From = "system6"
        To = "system4"
        Label = "验证方法"
    }
    
    # 生成Mermaid代码
    $fileGraphCode = Generate-MermaidCode -nodes $nodes -edges $edges
    $systemGraphCode = Generate-MermaidCode -nodes $systemNodes -edges $systemEdges
    
    # 输出到文件
    $fileGraphCode | Out-File -FilePath "文件关系图.md" -Encoding utf8
    $systemGraphCode | Out-File -FilePath "理论体系关系图.md" -Encoding utf8
    
    Write-Host '知识图谱已生成:'
    Write-Host '1. 文件关系图: 文件关系图.md'
    Write-Host '2. 理论体系关系图: 理论体系关系图.md'
}

# 执行主函数
Generate-KnowledgeGraph 