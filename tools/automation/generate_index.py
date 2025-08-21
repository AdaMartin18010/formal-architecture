"""
Generate Markdown indices for the repository.

Features:
- Walks the repository and creates per-top-level directory index files
- Writes a consolidated index under verification_output/repo_index.md
- Ignores common build/cache directories

Usage:
  python tools/automation/generate_index.py
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List


EXCLUDE_DIR_NAMES = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
}


def should_exclude_dir(path: Path) -> bool:
    return path.name in EXCLUDE_DIR_NAMES


def list_all_files(root: Path) -> List[Path]:
    files: List[Path] = []
    for p in root.rglob("*"):
        try:
            if p.is_dir():
                if should_exclude_dir(p):
                    pass
                continue
            if any(parent.name in EXCLUDE_DIR_NAMES for parent in p.parents):
                continue
            files.append(p)
        except (OSError, PermissionError):
            continue
    return files


def group_by_top_level(root: Path, files: List[Path]) -> Dict[str, List[Path]]:
    groups: Dict[str, List[Path]] = {}
    for f in files:
        try:
            rel = f.relative_to(root)
        except ValueError:
            # Skip files outside root
            continue
        parts = rel.parts
        top = parts[0] if parts else "."
        groups.setdefault(top, []).append(f)
    return groups


def write_repo_index(root: Path, groups: Dict[str, List[Path]]) -> Path:
    out_dir = root / "verification_output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "repo_index.md"

    lines: List[str] = []
    lines.append("# 仓库索引 (自动生成)")
    lines.append("")
    for top in sorted(groups.keys()):
        lines.append(f"## {top}")
        subset = sorted(groups[top], key=lambda p: str(p).lower())
        for p in subset[:2000]:
            rel = p.relative_to(root)
            lines.append(f"- {rel.as_posix()}")
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    files = list_all_files(root)
    groups = group_by_top_level(root, files)
    out_path = write_repo_index(root, groups)
    print(f"Wrote index: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


