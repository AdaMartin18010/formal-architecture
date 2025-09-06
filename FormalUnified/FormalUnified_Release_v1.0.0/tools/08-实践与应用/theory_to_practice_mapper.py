#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
理论到实践映射工具（核心入口）
Theory-to-Practice Mapping Tool (Core Entry)

- 读取 `config.yaml` 中的 `theory_to_practice_mapping.mapping_rules`
- 提供可编程API：查询支持的模式/语言、根据模式与语言选择模板
- 提供基础校验：配置完整性、语言支持、模板存在性（基于配置）
- 提供CLI：便捷查询与输出JSON结果

用法示例：
  python FormalUnified/08-实践与应用/theory_to_practice_mapper.py --pattern state_machine --language rust

注意：本工具只负责“映射选择”，不直接生成代码。代码生成由`AutomatedCodeGenerator`等组件完成。
"""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


DEFAULT_CONFIG_PATH = Path(__file__).parent / "config.yaml"


@dataclass
class MappingTemplate:
    pattern: str
    language: str
    template_name: str


class TheoryToPracticeMapper:
    """读取配置并提供模式到模板的映射查询能力。"""

    def __init__(self, config_path: Optional[Path] = None) -> None:
        self.config_path: Path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
        self.config: Dict = {}
        self.mapping_index: Dict[Tuple[str, str], MappingTemplate] = {}
        self.supported_languages: List[str] = []

        self._load_config()
        self._build_mapping_index()

    def _load_config(self) -> None:
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件未找到: {self.config_path}")
        with self.config_path.open('r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f) or {}
        mapping_cfg = self.config.get("theory_to_practice_mapping", {})
        self.supported_languages = mapping_cfg.get("supported_languages", [])
        if not self.supported_languages:
            LOGGER.warning("配置中未声明 supported_languages，默认视为空集")

    def _build_mapping_index(self) -> None:
        mapping_cfg = self.config.get("theory_to_practice_mapping", {})
        rules = mapping_cfg.get("mapping_rules", [])
        for rule in rules:
            pattern = rule.get("pattern")
            if not pattern:
                continue
            # 针对每种语言，收集其模板字段（命名为 <lang>_template）
            for language in self.supported_languages:
                field_name = f"{language}_template"
                template_name = rule.get(field_name)
                if template_name:
                    key = (pattern, language)
                    self.mapping_index[key] = MappingTemplate(
                        pattern=pattern,
                        language=language,
                        template_name=template_name,
                    )

    def get_supported_patterns(self) -> List[str]:
        patterns = {pattern for (pattern, _lang) in self.mapping_index.keys()}
        return sorted(patterns)

    def get_supported_languages(self) -> List[str]:
        return list(self.supported_languages)

    def resolve_template(self, pattern: str, language: str) -> Optional[MappingTemplate]:
        key = (pattern, language)
        return self.mapping_index.get(key)

    def validate(self) -> Dict[str, List[str]]:
        """对配置完整性做基础校验，返回问题列表。"""
        issues: Dict[str, List[str]] = {"errors": [], "warnings": []}

        # 校验语言集合
        if not self.supported_languages:
            issues["errors"].append("未配置 supported_languages")

        # 校验规则完整性
        patterns = self.get_supported_patterns()
        if not patterns:
            issues["warnings"].append("未发现任何可用的 mapping_rules")

        # 校验每个 (pattern, language) 是否有模板名
        for (pattern, language), mt in self.mapping_index.items():
            if not mt.template_name:
                issues["errors"].append(f"缺少模板名: pattern={pattern}, language={language}")

        return issues

    def describe(self) -> Dict:
        """提供简要的能力描述，用于集成或发布检查。"""
        patterns = self.get_supported_patterns()
        languages = self.get_supported_languages()
        coverage = {
            pattern: sorted({lang for (p, lang) in self.mapping_index.keys() if p == pattern})
            for pattern in patterns
        }
        return {
            "config_path": str(self.config_path),
            "supported_languages": languages,
            "supported_patterns": patterns,
            "coverage": coverage,
        }


def _parse_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Theory-to-Practice Mapper")
    parser.add_argument("--pattern", required=False, help="抽象模式名，例如: state_machine / petri_net / temporal_logic")
    parser.add_argument("--language", required=False, help="目标语言，例如: rust / go / python / typescript / java / csharp")
    parser.add_argument("--config", required=False, default=str(DEFAULT_CONFIG_PATH), help="配置文件路径，默认同目录 config.yaml")
    parser.add_argument("--describe", action="store_true", help="输出能力描述(JSON)")
    parser.add_argument("--validate", action="store_true", help="执行基础校验(JSON)")
    return parser.parse_args()


def _cli_main() -> int:
    args = _parse_cli_args()

    try:
        mapper = TheoryToPracticeMapper(Path(args.config))
    except Exception as exc:
        LOGGER.error("初始化失败: %s", exc)
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False))
        return 2

    if args.describe:
        print(json.dumps({"status": "ok", "data": mapper.describe()}, ensure_ascii=False, indent=2))
        return 0

    if args.validate:
        print(json.dumps({"status": "ok", "issues": mapper.validate()}, ensure_ascii=False, indent=2))
        return 0

    # 解析映射
    pattern = (args.pattern or "").strip()
    language = (args.language or "").strip()

    if not pattern or not language:
        example = {
            "usage": "--pattern state_machine --language rust",
            "supported_patterns": mapper.get_supported_patterns(),
            "supported_languages": mapper.get_supported_languages(),
        }
        print(json.dumps({"status": "missing_arguments", "example": example}, ensure_ascii=False, indent=2))
        return 1

    mapping = mapper.resolve_template(pattern=pattern, language=language)
    if not mapping:
        print(json.dumps({
            "status": "not_found",
            "message": f"未找到 pattern={pattern}, language={language} 的模板",
            "supported_patterns": mapper.get_supported_patterns(),
            "supported_languages": mapper.get_supported_languages(),
        }, ensure_ascii=False, indent=2))
        return 3

    output = {
        "status": "ok",
        "pattern": mapping.pattern,
        "language": mapping.language,
        "template_name": mapping.template_name,
        "config_path": str(mapper.config_path),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli_main()) 