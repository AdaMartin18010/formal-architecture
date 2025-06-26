import argparse
import os
import re

SECRET_PATTERNS = [
    re.compile(r'(?i)api[_-]?key\s*[:=]\s*[\'\"]?([A-Za-z0-9\-_=]{16,})[\'\"]?'),
    re.compile(r'(?i)secret[_-]?key\s*[:=]\s*[\'\"]?([A-Za-z0-9\-_=]{16,})[\'\"]?'),
    re.compile(r'(?i)password\s*[:=]\s*[\'\"]?([A-Za-z0-9\-_=]{8,})[\'\"]?'),
    re.compile(r'(?i)private[_-]?key'),
]

WEAK_PASSWORDS = {'123456', 'password', 'admin', 'letmein', 'qwerty'}


def scan_file(filepath):
    risks = []
    with open(filepath, encoding='utf-8', errors='ignore') as f:
        for i, line in enumerate(f, 1):
            for pat in SECRET_PATTERNS:
                if pat.search(line):
                    risks.append((filepath, i, line.strip()))
            for weak in WEAK_PASSWORDS:
                if weak in line:
                    risks.append((filepath, i, f'Weak password: {weak}'))
    return risks

def scan_dir(path):
    all_risks = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.sol', '.rs', '.go', '.env', '.json', '.yaml', '.yml', '.toml')):
                all_risks.extend(scan_file(os.path.join(root, file)))
    return all_risks

def main():
    parser = argparse.ArgumentParser(description='密钥与配置安全检查')
    parser.add_argument('--path', required=True, help='待扫描目录')
    args = parser.parse_args()
    risks = scan_dir(args.path)
    if risks:
        print('发现风险项:')
        for filepath, lineno, content in risks:
            print(f'{filepath}:{lineno}: {content}')
    else:
        print('未发现明文密钥或弱口令')

if __name__ == '__main__':
    main() 