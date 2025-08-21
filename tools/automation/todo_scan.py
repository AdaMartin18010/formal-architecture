"""
Repository-wide TODO/FIXME scanner.

Features:
- Recursively scans text files (md, py, yml, yaml, js, ts, ps1, json, toml, txt)
- Detects multilingual markers: TODO, FIXME, TBD, [TODO], 待办, 待补充, 待完善, 占位, 占坑, 未完成, 后续补充, 继续完善
- Outputs a JSON summary and a Markdown report under verification_output/

Usage:
  python tools/automation/todo_scan.py
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


SUPPORTED_SUFFIXES = {
    ".md",
    ".py",
    ".yml",
    ".yaml",
    ".js",
    ".ts",
    ".ps1",
    ".json",
    ".toml",
    ".txt",
}

EXCLUDE_DIR_NAMES = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
}

MARKER_PATTERNS = [
    r"\bTODO\b",
    r"\bFIXME\b",
    r"\bTBD\b",
    r"\[\s*TODO\s*\]",
    r"待办",
    r"待补充",
    r"待完善",
    r"占位",
    r"占坑",
    r"未完成",
    r"后续补充",
    r"继续完善",
]

MARKER_REGEX = re.compile("|".join(MARKER_PATTERNS), re.IGNORECASE)


@dataclass
class TodoHit:
    file: str
    line: int
    text: str
    marker: str


def is_text_file(path: Path) -> bool:
    if not path.is_file():
        return False
    return path.suffix.lower() in SUPPORTED_SUFFIXES


def should_exclude_dir(path: Path) -> bool:
    return path.name in EXCLUDE_DIR_NAMES


def find_marker(text: str) -> Optional[str]:
    m = MARKER_REGEX.search(text)
    if m:
        return m.group(0)
    return None


def iter_candidate_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*"):
        try:
            if p.is_dir():
                if should_exclude_dir(p):
                    # Skip entire subtree
                    # rglob doesn't support pruning, so we just continue; file checks will skip
                    pass
                continue
            if any(parent.name in EXCLUDE_DIR_NAMES for parent in p.parents):
                continue
            if is_text_file(p):
                yield p
        except (OSError, PermissionError):
            continue


def scan_file(path: Path) -> List[TodoHit]:
    hits: List[TodoHit] = []
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return hits
    for idx, line in enumerate(content.splitlines(), start=1):
        marker = find_marker(line)
        if marker:
            snippet = line.strip()
            if len(snippet) > 300:
                snippet = snippet[:300] + " …"
            hits.append(TodoHit(file=str(path).replace("\\", "/"), line=idx, text=snippet, marker=marker))
    return hits


def aggregate_by_directory(hits: List[TodoHit]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for h in hits:
        directory = str(Path(h.file).parent)
        counts[directory] = counts.get(directory, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: kv[1], reverse=True))


def write_outputs(hits: List[TodoHit], repo_root: Path) -> Tuple[Path, Path]:
    out_dir = repo_root / "verification_output"
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "todo_report.json"
    md_path = out_dir / "todo_report.md"

    # JSON
    data = {
        "total": len(hits),
        "by_directory": aggregate_by_directory(hits),
        "items": [asdict(h) for h in hits],
    }
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # Markdown
    lines: List[str] = []
    lines.append("# TODO 扫描报告")
    lines.append("")
    lines.append(f"总计: {len(hits)} 条")
    lines.append("")
    lines.append("## 目录热点分布")
    for directory, count in list(aggregate_by_directory(hits).items())[:30]:
        lines.append(f"- {directory}: {count}")
    lines.append("")
    lines.append("## 详细项")
    for h in hits:
        lines.append(f"- {h.file}:{h.line} — [{h.marker}] {h.text}")
    md_path.write_text("\n".join(lines), encoding="utf-8")

    return json_path, md_path


def main(argv: List[str]) -> int:
    repo_root = Path(__file__).resolve().parents[2]
    hits: List[TodoHit] = []
    for path in iter_candidate_files(repo_root):
        hits.extend(scan_file(path))

    json_path, md_path = write_outputs(hits, repo_root)
    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


