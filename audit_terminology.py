#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit terminology index: extract bold terms from all Struct markdown files,
compare with existing index, find missing/orphan/duplicate entries.
"""

import os
import re
import json
from collections import defaultdict
from pathlib import Path

STRUCT_DIR = Path("E:/_src/formal-architecture/Struct")
INDEX_FILE = STRUCT_DIR / "99-参考文献与索引/02-核心概念反向索引与术语表.md"

def extract_bold_terms(text):
    """Extract all **term** patterns from markdown text."""
    # Match **something** but not inside table headers or the title itself if it's about the term
    # Also exclude pure markdown bold formatting for emphasis that isn't a term
    pattern = r'\*\*([^*\n]+?)\*\*'
    matches = re.findall(pattern, text)
    terms = set()
    for m in matches:
        term = m.strip()
        # Skip empty, too long (likely sentences), or pure punctuation
        if not term or len(term) > 60:
            continue
        # Skip pure markdown formatting artifacts
        if term in ('术语', '定义', '模块', '文件', '定位', '使用方法', '核心概念反向索引与术语表'):
            continue
        # Skip pure numbers or common markdown text
        if re.match(r'^\d+$', term):
            continue
        # Skip common structural bold text in tables
        if term in ('术语', '定义', '模块', '文件'):
            continue
        terms.add(term)
    return terms

def get_file_context(text, term, window=200):
    """Get surrounding context for a term to help define it."""
    pattern = re.escape(term)
    match = re.search(pattern, text)
    if not match:
        return ""
    start = max(0, match.start() - window)
    end = min(len(text), match.end() + window)
    return text[start:end].replace('\n', ' ')

def parse_existing_index(filepath):
    """Parse the existing terminology index and return dict of term -> {definition, module, file}."""
    content = filepath.read_text(encoding='utf-8')
    terms = {}
    # Match table rows: | **term** | definition | module | file |
    pattern = r'\|\s*\*\*([^*|]+?)\*\*\s*\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|'
    for m in re.finditer(pattern, content):
        term = m.group(1).strip()
        definition = m.group(2).strip()
        module = m.group(3).strip()
        file_ref = m.group(4).strip()
        terms[term] = {
            'definition': definition,
            'module': module,
            'file_ref': file_ref,
        }
    return terms, content

def main():
    existing_terms, index_content = parse_existing_index(INDEX_FILE)
    print(f"Existing terms in index: {len(existing_terms)}")

    # Collect all bold terms from all markdown files
    all_bold_terms = defaultdict(list)  # term -> list of (filepath, context)
    md_files = list(STRUCT_DIR.rglob("*.md"))
    md_files = [f for f in md_files if f.name != INDEX_FILE.name or f.parent.name != INDEX_FILE.parent.name]
    
    for md_file in md_files:
        try:
            text = md_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Error reading {md_file}: {e}")
            continue
        terms = extract_bold_terms(text)
        for term in terms:
            # Skip pure markdown structural terms
            if term in ('术语', '定义', '模块', '文件', '定位', '使用方法'):
                continue
            context = get_file_context(text, term)
            all_bold_terms[term].append((str(md_file.relative_to(STRUCT_DIR)), context))

    print(f"Total unique bold terms found in files: {len(all_bold_terms)}")
    
    # Find missing terms
    missing_terms = set(all_bold_terms.keys()) - set(existing_terms.keys())
    print(f"Missing terms from index: {len(missing_terms)}")
    
    # Find orphans (terms in index but not found in any file)
    orphan_terms = set(existing_terms.keys()) - set(all_bold_terms.keys())
    print(f"Orphan terms (in index but not in files): {len(orphan_terms)}")
    
    # Find duplicates in index (shouldn't happen in dict, but check if file has duplicates)
    raw_terms = re.findall(r'\|\s*\*\*([^*|]+?)\*\*\s*\|', index_content)
    seen = set()
    duplicates = []
    for t in raw_terms:
        t = t.strip()
        if t in seen:
            duplicates.append(t)
        seen.add(t)
    print(f"Duplicate entries in index: {len(duplicates)} ({set(duplicates)})")

    # Save detailed report
    report = {
        'existing_count': len(existing_terms),
        'bold_terms_count': len(all_bold_terms),
        'missing_count': len(missing_terms),
        'orphan_count': len(orphan_terms),
        'duplicate_count': len(duplicates),
        'missing_terms': sorted(missing_terms),
        'orphan_terms': sorted(orphan_terms),
        'duplicates': list(set(duplicates)),
    }
    
    # For each missing term, gather info
    missing_details = []
    for term in sorted(missing_terms):
        occurrences = all_bold_terms[term]
        # Pick the first occurrence
        filepath, context = occurrences[0]
        # Try to extract a brief definition from context
        # Look for patterns like "term 是 ..." or "term：..." or "term, ..."
        definition = "（待补充定义）"
        # Try various patterns
        context_clean = context.replace('**', '')
        patterns = [
            rf'{re.escape(term)}\s*是\s*([^。；,.\n]{{10,80}})',
            rf'{re.escape(term)}\s*[：:]\s*([^。；,.\n]{{10,80}})',
            rf'{re.escape(term)}\s*[,，]\s*([^。；,.\n]{{10,80}})',
        ]
        for pat in patterns:
            m = re.search(pat, context_clean)
            if m:
                definition = m.group(1).strip()
                if len(definition) > 5:
                    break
        
        # Derive module from filepath
        parts = filepath.split(os.sep)
        module = parts[0].split('-')[0] if parts else '?'
        
        missing_details.append({
            'term': term,
            'definition': definition,
            'module': module,
            'file': filepath,
            'context': context_clean[:300],
        })
    
    report['missing_details'] = missing_details
    
    report_path = Path("E:/_src/formal-architecture/terminology_audit_report.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Report saved to {report_path}")
    
    # Print missing terms for review
    for item in missing_details:
        print(f"- {item['term']} | {item['definition'][:60]} | {item['module']} | {item['file']}")

if __name__ == "__main__":
    main()
