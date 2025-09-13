# 高级链接修复脚本
# 处理复杂的断链问题，包括相对路径和缺失文件

param(
    [string]$RootPath = ".",
    [string]$OutputFile = "reports\links\advanced-fix-report.txt"
)

# 创建输出目录
$outputDir = Split-Path $OutputFile -Parent
if (!(Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force
}

Write-Host "开始高级链接修复..." -ForegroundColor Green

# 获取所有markdown文件
$markdownFiles = Get-ChildItem -Path $RootPath -Filter "*.md" -Recurse

$fixedCount = 0
$totalFiles = $markdownFiles.Count
$fixRules = @()

# 定义高级修复规则
$fixRules += @{
    Pattern = '\]\(\.\./00-主题树与内容索引\.md\)'
    Replacement = '](../00-主题树与内容索引.md)'
    Description = "修复主题树链接的相对路径（从深层目录）"
}

$fixRules += @{
    Pattern = '\]\(\.\./00-形式化架构理论统一计划\.md\)'
    Replacement = '](../00-形式化架构理论统一计划.md)'
    Description = "修复统一计划链接的相对路径（从深层目录）"
}

$fixRules += @{
    Pattern = '\]\(\.\./13-项目报告与总结/递归合并计划\.md\)'
    Replacement = '](../13-项目报告与总结/递归合并计划.md)'
    Description = "修复递归合并计划链接的相对路径"
}

$fixRules += @{
    Pattern = '\]\(\.\./13-项目报告与总结/形式化架构理论项目路线图\.md\)'
    Replacement = '](../13-项目报告与总结/形式化架构理论项目路线图.md)'
    Description = "修复项目路线图链接的相对路径"
}

$fixRules += @{
    Pattern = '\]\(\.\./07-理论统一与整合/03-跨领域证明\.md\)'
    Replacement = '](../07-理论统一与整合/03-跨领域证明.md)'
    Description = "修复跨领域证明链接的相对路径"
}

$fixRules += @{
    Pattern = '\]\(\.\./README\.md\)'
    Replacement = '](../README.md)'
    Description = "修复README链接的相对路径"
}

$fixRules += @{
    Pattern = '\]\(\.\./Matter/Theory/理论应用框架\.md\)'
    Replacement = '](../Matter/Theory/理论应用框架.md)'
    Description = "修复理论应用框架链接的相对路径"
}

# 修复从项目报告与总结目录的链接
$fixRules += @{
    Pattern = '\]\(01-哲学基础理论/00-哲学基础理论总论\.md\)'
    Replacement = '](../01-哲学基础理论/00-哲学基础理论总论.md)'
    Description = "修复哲学基础理论总论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(01-哲学基础理论/01-本体论基础\.md\)'
    Replacement = '](../01-哲学基础理论/01-本体论基础.md)'
    Description = "修复本体论基础链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(01-哲学基础理论/02-认识论基础\.md\)'
    Replacement = '](../01-哲学基础理论/02-认识论基础.md)'
    Description = "修复认识论基础链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(01-哲学基础理论/03-逻辑学基础\.md\)'
    Replacement = '](../01-哲学基础理论/03-逻辑学基础.md)'
    Description = "修复逻辑学基础链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(01-哲学基础理论/04-伦理学基础\.md\)'
    Replacement = '](../01-哲学基础理论/04-伦理学基础.md)'
    Description = "修复伦理学基础链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(01-哲学基础理论/05-形而上学基础\.md\)'
    Replacement = '](../01-哲学基础理论/05-形而上学基础.md)'
    Description = "修复形而上学基础链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(01-哲学基础理论/06-现象学基础\.md\)'
    Replacement = '](../01-哲学基础理论/06-现象学基础.md)'
    Description = "修复现象学基础链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(01-哲学基础理论/07-缺陷与纠偏理论\.md\)'
    Replacement = '](../01-哲学基础理论/07-缺陷与纠偏理论.md)'
    Description = "修复缺陷与纠偏理论链接（从项目报告目录）"
}

# 修复数学理论体系链接
$fixRules += @{
    Pattern = '\]\(02-数学理论体系/00-数学理论体系总论\.md\)'
    Replacement = '](../02-数学理论体系/00-数学理论体系总论.md)'
    Description = "修复数学理论体系总论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(02-数学理论体系/01-集合论基础\.md\)'
    Replacement = '](../02-数学理论体系/01-集合论基础.md)'
    Description = "修复集合论基础链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(02-数学理论体系/02-代数基础\.md\)'
    Replacement = '](../02-数学理论体系/02-代数基础.md)'
    Description = "修复代数基础链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(02-数学理论体系/03-几何基础\.md\)'
    Replacement = '](../02-数学理论体系/03-几何基础.md)'
    Description = "修复几何基础链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(02-数学理论体系/04-分析基础\.md\)'
    Replacement = '](../02-数学理论体系/04-分析基础.md)'
    Description = "修复分析基础链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(02-数学理论体系/05-拓扑基础\.md\)'
    Replacement = '](../02-数学理论体系/05-拓扑基础.md)'
    Description = "修复拓扑基础链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(02-数学理论体系/05-概率统计基础\.md\)'
    Replacement = '](../02-数学理论体系/05-概率统计基础.md)'
    Description = "修复概率统计基础链接（从项目报告目录）"
}

# 修复形式语言理论体系链接
$fixRules += @{
    Pattern = '\]\(03-形式语言理论体系/00-形式语言理论统一总论\.md\)'
    Replacement = '](../03-形式语言理论体系/00-形式语言理论统一总论.md)'
    Description = "修复形式语言理论统一总论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(03-形式语言理论体系/00a-形式语言的多维批判性分析\.md\)'
    Replacement = '](../03-形式语言理论体系/00a-形式语言的多维批判性分析.md)'
    Description = "修复形式语言多维批判性分析链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(03-形式语言理论体系/01-自动机统一理论\.md\)'
    Replacement = '](../03-形式语言理论体系/01-自动机统一理论.md)'
    Description = "修复自动机统一理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(03-形式语言理论体系/02-形式语法\.md\)'
    Replacement = '](../03-形式语言理论体系/02-形式语法.md)'
    Description = "修复形式语法链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(03-形式语言理论体系/03-语义理论\.md\)'
    Replacement = '](../03-形式语言理论体系/03-语义理论.md)'
    Description = "修复语义理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(03-形式语言理论体系/04a-类型理论基础与演进\.md\)'
    Replacement = '](../03-形式语言理论体系/04a-类型理论基础与演进.md)'
    Description = "修复类型理论基础与演进链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(03-形式语言理论体系/05-计算理论\.md\)'
    Replacement = '](../03-形式语言理论体系/05-计算理论.md)'
    Description = "修复计算理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(03-形式语言理论体系/06-语言设计\.md\)'
    Replacement = '](../03-形式语言理论体系/06-语言设计.md)'
    Description = "修复语言设计链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(03-形式语言理论体系/07-时序逻辑与模型检测\.md\)'
    Replacement = '](../03-形式语言理论体系/07-时序逻辑与模型检测.md)'
    Description = "修复时序逻辑与模型检测链接（从项目报告目录）"
}

# 修复形式模型理论体系链接
$fixRules += @{
    Pattern = '\]\(04-形式模型理论体系/00-形式模型理论统一总论\.md\)'
    Replacement = '](../04-形式模型理论体系/00-形式模型理论统一总论.md)'
    Description = "修复形式模型理论统一总论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(04-形式模型理论体系/统一状态转换系统理论\.md\)'
    Replacement = '](../04-形式模型理论体系/统一状态转换系统理论.md)'
    Description = "修复统一状态转换系统理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(04-形式模型理论体系/01-状态机理论\.md\)'
    Replacement = '](../04-形式模型理论体系/01-状态机理论.md)'
    Description = "修复状态机理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(04-形式模型理论体系/02-Petri网理论\.md\)'
    Replacement = '](../04-形式模型理论体系/02-Petri网理论.md)'
    Description = "修复Petri网理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(04-形式模型理论体系/03-时序逻辑理论\.md\)'
    Replacement = '](../04-形式模型理论体系/03-时序逻辑理论.md)'
    Description = "修复时序逻辑理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(04-形式模型理论体系/04-进程代数理论\.md\)'
    Replacement = '](../04-形式模型理论体系/04-进程代数理论.md)'
    Description = "修复进程代数理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(04-形式模型理论体系/05-混合系统理论\.md\)'
    Replacement = '](../04-形式模型理论体系/05-混合系统理论.md)'
    Description = "修复混合系统理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(04-形式模型理论体系/06-模型检测\.md\)'
    Replacement = '](../04-形式模型理论体系/06-模型检测.md)'
    Description = "修复模型检测链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(04-形式模型理论体系/07-系统建模\.md\)'
    Replacement = '](../04-形式模型理论体系/07-系统建模.md)'
    Description = "修复系统建模链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(04-形式模型理论体系/08-协议验证\.md\)'
    Replacement = '](../04-形式模型理论体系/08-协议验证.md)'
    Description = "修复协议验证链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(04-形式模型理论体系/09-性能分析\.md\)'
    Replacement = '](../04-形式模型理论体系/09-性能分析.md)'
    Description = "修复性能分析链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(04-形式模型理论体系/10-安全分析\.md\)'
    Replacement = '](../04-形式模型理论体系/10-安全分析.md)'
    Description = "修复安全分析链接（从项目报告目录）"
}

# 修复编程语言理论体系链接
$fixRules += @{
    Pattern = '\]\(05-编程语言理论体系/00-编程语言理论统一总论\.md\)'
    Replacement = '](../05-编程语言理论体系/00-编程语言理论统一总论.md)'
    Description = "修复编程语言理论统一总论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(05-编程语言理论体系/01-语法与语言设计统一理论\.md\)'
    Replacement = '](../05-编程语言理论体系/01-语法与语言设计统一理论.md)'
    Description = "修复语法与语言设计统一理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(05-编程语言理论体系/02-语义与语法统一理论\.md\)'
    Replacement = '](../05-编程语言理论体系/02-语义与语法统一理论.md)'
    Description = "修复语义与语法统一理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(05-编程语言理论体系/03-类型统一理论\.md\)'
    Replacement = '](../05-编程语言理论体系/03-类型统一理论.md)'
    Description = "修复类型统一理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(05-编程语言理论体系/04-编译统一理论\.md\)'
    Replacement = '](../05-编程语言理论体系/04-编译统一理论.md)'
    Description = "修复编译统一理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(05-编程语言理论体系/05-运行时理论\.md\)'
    Replacement = '](../05-编程语言理论体系/05-运行时理论.md)'
    Description = "修复运行时理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(05-编程语言理论体系/06-并发理论\.md\)'
    Replacement = '](../05-编程语言理论体系/06-并发理论.md)'
    Description = "修复并发理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(05-编程语言理论体系/07-Rust语言理论\.md\)'
    Replacement = '](../05-编程语言理论体系/07-Rust语言理论.md)'
    Description = "修复Rust语言理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(05-编程语言理论体系/08-函数式编程理论\.md\)'
    Replacement = '](../05-编程语言理论体系/08-函数式编程理论.md)'
    Description = "修复函数式编程理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(05-编程语言理论体系/09-并发编程理论\.md\)'
    Replacement = '](../05-编程语言理论体系/09-并发编程理论.md)'
    Description = "修复并发编程理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(05-编程语言理论体系/10-系统编程理论\.md\)'
    Replacement = '](../05-编程语言理论体系/10-系统编程理论.md)'
    Description = "修复系统编程理论链接（从项目报告目录）"
}

# 修复软件架构理论体系链接
$fixRules += @{
    Pattern = '\]\(04-软件架构理论体系/00-软件架构理论统一总论\.md\)'
    Replacement = '](../04-软件架构理论体系/00-软件架构理论统一总论.md)'
    Description = "修复软件架构理论统一总论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(04-软件架构理论体系/01-架构模式理论\.md\)'
    Replacement = '](../04-软件架构理论体系/01-架构模式理论.md)'
    Description = "修复架构模式理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(04-软件架构理论体系/02-组件理论\.md\)'
    Replacement = '](../04-软件架构理论体系/02-组件理论.md)'
    Description = "修复组件理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(04-软件架构理论体系/03-接口理论\.md\)'
    Replacement = '](../04-软件架构理论体系/03-接口理论.md)'
    Description = "修复接口理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(04-软件架构理论体系/04-分层架构理论\.md\)'
    Replacement = '](../04-软件架构理论体系/04-分层架构理论.md)'
    Description = "修复分层架构理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(04-软件架构理论体系/05-微服务架构理论\.md\)'
    Replacement = '](../04-软件架构理论体系/05-微服务架构理论.md)'
    Description = "修复微服务架构理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(04-软件架构理论体系/06-事件驱动架构理论\.md\)'
    Replacement = '](../04-软件架构理论体系/06-事件驱动架构理论.md)'
    Description = "修复事件驱动架构理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(04-软件架构理论体系/07-云原生架构理论\.md\)'
    Replacement = '](../04-软件架构理论体系/07-云原生架构理论.md)'
    Description = "修复云原生架构理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(04-软件架构理论体系/08-分布式系统理论\.md\)'
    Replacement = '](../04-软件架构理论体系/08-分布式系统理论.md)'
    Description = "修复分布式系统理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(04-软件架构理论体系/09-安全架构理论\.md\)'
    Replacement = '](../04-软件架构理论体系/09-安全架构理论.md)'
    Description = "修复安全架构理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(04-软件架构理论体系/10-性能架构理论\.md\)'
    Replacement = '](../04-软件架构理论体系/10-性能架构理论.md)'
    Description = "修复性能架构理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(04-软件架构理论体系/11-可观测性架构理论\.md\)'
    Replacement = '](../04-软件架构理论体系/11-可观测性架构理论.md)'
    Description = "修复可观测性架构理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(04-软件架构理论体系/12-工作流架构理论\.md\)'
    Replacement = '](../04-软件架构理论体系/12-工作流架构理论.md)'
    Description = "修复工作流架构理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(04-软件架构理论体系/13-API设计理论\.md\)'
    Replacement = '](../04-软件架构理论体系/13-API设计理论.md)'
    Description = "修复API设计理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(04-软件架构理论体系/14-数据架构理论\.md\)'
    Replacement = '](../04-软件架构理论体系/14-数据架构理论.md)'
    Description = "修复数据架构理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(04-软件架构理论体系/15-集成架构理论\.md\)'
    Replacement = '](../04-软件架构理论体系/15-集成架构理论.md)'
    Description = "修复集成架构理论链接（从项目报告目录）"
}

# 修复软件工程理论与实践体系链接
$fixRules += @{
    Pattern = '\]\(软件工程理论与实践体系/00-软件工程理论与实践体系总论\.md\)'
    Replacement = '](../软件工程理论与实践体系/00-软件工程理论与实践体系总论.md)'
    Description = "修复软件工程理论与实践体系总论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(软件工程理论与实践体系/01-Golang_Rust后端工程理论与实践\.md\)'
    Replacement = '](../软件工程理论与实践体系/01-Golang_Rust后端工程理论与实践.md)'
    Description = "修复Golang_Rust后端工程理论与实践链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(软件工程理论与实践体系/02-领域定义语言与协议架构DSL\.md\)'
    Replacement = '](../软件工程理论与实践体系/02-领域定义语言与协议架构DSL.md)'
    Description = "修复领域定义语言与协议架构DSL链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(软件工程理论与实践体系/03-自动化生成与工程工具链\.md\)'
    Replacement = '](../软件工程理论与实践体系/03-自动化生成与工程工具链.md)'
    Description = "修复自动化生成与工程工具链链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(软件工程理论与实践体系/04-分布式系统与微服务架构理论与实践\.md\)'
    Replacement = '](../软件工程理论与实践体系/04-分布式系统与微服务架构理论与实践.md)'
    Description = "修复分布式系统与微服务架构理论与实践链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(软件工程理论与实践体系/05-行业应用与最佳实践\.md\)'
    Replacement = '](../软件工程理论与实践体系/05-行业应用与最佳实践.md)'
    Description = "修复行业应用与最佳实践链接（从项目报告目录）"
}

# 修复理论统一与整合链接
$fixRules += @{
    Pattern = '\]\(11-理论统一与整合/07-理论统一与整合/00-理论统一与整合总论\.md\)'
    Replacement = '](../11-理论统一与整合/07-理论统一与整合/00-理论统一与整合总论.md)'
    Description = "修复理论统一与整合总论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(11-理论统一与整合/07-理论统一与整合/01-理论映射关系\.md\)'
    Replacement = '](../11-理论统一与整合/07-理论统一与整合/01-理论映射关系.md)'
    Description = "修复理论映射关系链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(11-理论统一与整合/07-理论统一与整合/02-统一形式化理论\.md\)'
    Replacement = '](../11-理论统一与整合/07-理论统一与整合/02-统一形式化理论.md)'
    Description = "修复统一形式化理论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(11-理论统一与整合/07-理论统一与整合/03-跨领域理论整合\.md\)'
    Replacement = '](../11-理论统一与整合/07-理论统一与整合/03-跨领域理论整合.md)'
    Description = "修复跨领域理论整合链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(11-理论统一与整合/07-理论统一与整合/04-理论应用框架\.md\)'
    Replacement = '](../11-理论统一与整合/07-理论统一与整合/04-理论应用框架.md)'
    Description = "修复理论应用框架链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(11-理论统一与整合/07-理论统一与整合/21-统一边缘云系统理论\.md\)'
    Replacement = '](../11-理论统一与整合/07-理论统一与整合/21-统一边缘云系统理论.md)'
    Description = "修复统一边缘云系统理论链接（从项目报告目录）"
}

# 修复实践应用开发链接
$fixRules += @{
    Pattern = '\]\(08-实践应用开发/00-实践应用开发总论\.md\)'
    Replacement = '](../08-实践应用开发/00-实践应用开发总论.md)'
    Description = "修复实践应用开发总论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(08-实践应用开发/01-Rust形式化工具\.md\)'
    Replacement = '](../08-实践应用开发/01-Rust形式化工具.md)'
    Description = "修复Rust形式化工具链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(08-实践应用开发/02-Go形式化工具\.md\)'
    Replacement = '](../08-实践应用开发/02-Go形式化工具.md)'
    Description = "修复Go形式化工具链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(08-实践应用开发/03-形式化验证工具\.md\)'
    Replacement = '](../08-实践应用开发/03-形式化验证工具.md)'
    Description = "修复形式化验证工具链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(08-实践应用开发/04-模型检测工具\.md\)'
    Replacement = '](../08-实践应用开发/04-模型检测工具.md)'
    Description = "修复模型检测工具链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(08-实践应用开发/05-代码生成工具\.md\)'
    Replacement = '](../08-实践应用开发/05-代码生成工具.md)'
    Description = "修复代码生成工具链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(08-实践应用开发/06-架构分析工具\.md\)'
    Replacement = '](../08-实践应用开发/06-架构分析工具.md)'
    Description = "修复架构分析工具链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(08-实践应用开发/07-性能分析工具\.md\)'
    Replacement = '](../08-实践应用开发/07-性能分析工具.md)'
    Description = "修复性能分析工具链接（从项目报告目录）"
}

# 修复数学理论体系高级链接
$fixRules += @{
    Pattern = '\]\(02-数学理论体系/06-数论基础\.md\)'
    Replacement = '](../02-数学理论体系/06-数论基础.md)'
    Description = "修复数论基础链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(02-数学理论体系/07-范畴论\.md\)'
    Replacement = '](../02-数学理论体系/07-范畴论.md)'
    Description = "修复范畴论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(02-数学理论体系/08-拓扑学\.md\)'
    Replacement = '](../02-数学理论体系/08-拓扑学.md)'
    Description = "修复拓扑学链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(02-数学理论体系/09-泛函分析\.md\)'
    Replacement = '](../02-数学理论体系/09-泛函分析.md)'
    Description = "修复泛函分析链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(02-数学理论体系/10-数学哲学\.md\)'
    Replacement = '](../02-数学理论体系/10-数学哲学.md)'
    Description = "修复数学哲学链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(02-数学理论体系/11-数学方法论\.md\)'
    Replacement = '](../02-数学理论体系/11-数学方法论.md)'
    Description = "修复数学方法论链接（从项目报告目录）"
}

$fixRules += @{
    Pattern = '\]\(02-数学理论体系/12-数学应用\.md\)'
    Replacement = '](../02-数学理论体系/12-数学应用.md)'
    Description = "修复数学应用链接（从项目报告目录）"
}

# 修复外部链接问题
$fixRules += @{
    Pattern = '\]\(\.\./1\.1-Microservice/1\.1\.2-Integration/RPC与Web框架集成\.md#1\.1\.2\)'
    Replacement = '](../1.1-Microservice/1.1.2-Integration/RPC与Web框架集成.md#1.1.2)'
    Description = "修复外部微服务链接（从项目报告目录）"
}

# 修复archive链接
$fixRules += @{
    Pattern = '\]\(archive/README\.md\)'
    Replacement = '](../archive/README.md)'
    Description = "修复archive README链接（从项目报告目录）"
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
高级链接修复报告
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

Write-Host "`n高级修复完成！" -ForegroundColor Green
Write-Host "检查文件数: $totalFiles" -ForegroundColor Cyan
Write-Host "修复文件数: $fixedCount" -ForegroundColor Cyan
Write-Host "报告已保存到: $OutputFile" -ForegroundColor Cyan
