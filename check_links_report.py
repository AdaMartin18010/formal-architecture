import os, re, json
from urllib.parse import unquote

dirs = ['Analysis', 'Modern', 'Struct']
links = []
link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

for root_dir in dirs:
    for root, dirs_list, files in os.walk(root_dir):
        for f in files:
            if f.endswith('.md'):
                path = os.path.join(root, f)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                        content = file.read()
                    for m in link_pattern.finditer(content):
                        link = m.group(2).strip()
                        if '.md' in link and not link.startswith('http') and not link.startswith('#') and not link.startswith('mailto'):
                            link = link.split('#')[0]
                            links.append((path, m.group(1), link))
                except Exception as e:
                    pass

broken = []
for source, text, target in links:
    target = unquote(target)
    source_dir = os.path.dirname(source)
    if target.startswith('/'):
        resolved = target[1:]
    else:
        resolved = os.path.normpath(os.path.join(source_dir, target))
    resolved = resolved.replace(os.sep, '/')
    if not os.path.exists(resolved):
        broken.append((source, text, target, resolved))

# Categorize broken links
pseudo = []  # template/example links
struct_missing = []  # Struct dir missing files
analysis_missing = []  # Analysis dir missing files
modern_missing = []  # Modern dir missing files
other = []

for b in broken:
    source, text, target, resolved = b
    if '相对路径' in target or '链接文本' in target or '链接文字' in target or '文档标题' in target or '.*' in target:
        pseudo.append(b)
    elif source.startswith('Struct'):
        struct_missing.append(b)
    elif source.startswith('Analysis'):
        analysis_missing.append(b)
    elif source.startswith('Modern'):
        modern_missing.append(b)
    else:
        other.append(b)

report = f"""# 链接完整性检查报告

生成时间: 2026-05-13

## 统计汇总

| 项目 | 数量 |
|---|---|
| 检查的本地 .md 链接总数 | {len(links)} |
| 断链总数 | {len(broken)} |
| 断链率 | {len(broken)/len(links)*100:.2f}% |
| 伪链接/模板链接 | {len(pseudo)} |
| Struct 目录断链 | {len(struct_missing)} |
| Analysis 目录断链 | {len(analysis_missing)} |
| Modern 目录断链 | {len(modern_missing)} |
| 其他 | {len(other)} |

## 伪链接/模板链接清单（建议清理或修正）

"""
for s, t, target, resolved in pseudo[:20]:
    report += f"- `{s}` -> `[{t}]({target})`\n"

report += "\n## Analysis 目录断链清单\n\n"
for s, t, target, resolved in analysis_missing[:30]:
    report += f"- `{s}` -> `[{t}]({target})` -> `{resolved}`\n"

report += "\n## Struct 目录断链清单\n\n"
for s, t, target, resolved in struct_missing[:30]:
    report += f"- `{s}` -> `[{t}]({target})` -> `{resolved}`\n"

report += "\n## Modern 目录断链清单\n\n"
for s, t, target, resolved in modern_missing[:30]:
    report += f"- `{s}` -> `[{t}]({target})` -> `{resolved}`\n"

with open('链接完整性检查报告-2026-05-13.md', 'w', encoding='utf-8') as f:
    f.write(report)

# Save raw data
with open('broken_links_raw.json', 'w', encoding='utf-8') as f:
    json.dump(broken, f, ensure_ascii=False, indent=2)

print("Report saved to 链接完整性检查报告-2026-05-13.md")
print(f"Total: {len(links)}, Broken: {len(broken)}, Pseudo: {len(pseudo)}")
