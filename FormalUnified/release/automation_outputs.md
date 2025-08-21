# 自动化产物说明

本页汇总仓库级自动化脚本的输出位置与使用方法。

## 产物位置

- TODO 扫描报告（JSON）：`verification_output/todo_report.json`
- TODO 扫描报告（Markdown）：`verification_output/todo_report.md`
- 仓库索引（Markdown）：`verification_output/repo_index.md`

## 使用方法

在仓库根目录执行：

```bash
python tools/automation/todo_scan.py
python tools/automation/generate_index.py
```

Windows PowerShell：

```powershell
python tools/automation/todo_scan.py
python tools/automation/generate_index.py
```

## 说明

- TODO 扫描支持多语言标记：`TODO`、`FIXME`、`TBD`、`[TODO]`、`待办`、`待补充`、`待完善`、`占位`、`占坑`、`未完成`、`后续补充`、`继续完善`。
- 索引会按仓库顶层目录分组列出文件路径，便于检索与交叉引用。
- 所有输出均写入 `verification_output/` 目录，可纳入发布流程或校验流程。
