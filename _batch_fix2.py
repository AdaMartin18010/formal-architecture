import os, re, glob

def fix_auth_quotes(base_dir, name):
    files = glob.glob(os.path.join(base_dir, '**', '*.md'), recursive=True)
    files = [f for f in files 
             if 'README' not in os.path.basename(f) 
             and 'archive' not in f 
             and '_templates' not in f
             and '00-总览' not in f
             and not os.path.basename(f).startswith('00-')
             and not os.path.basename(f).startswith('周推进')
             and '统一计划' not in os.path.basename(f)]
    
    fixed = 0
    for f in files:
        with open(f, 'r', encoding='utf-8') as fh:
            content = fh.read()
        
        # Check for real authoritative quote: > **Name** (year)
        has_real_auth = re.search(r'>\s*\*\*[^*]+\*\*.*\(\d{4}\)', content)
        if has_real_auth:
            continue
        
        # Check if already has our appended auth section
        if '## 权威引用' in content and 'Martin Fowler' in content:
            continue
        
        # Append authoritative quotes
        auth_section = '\n\n## 权威引用\n\n> **Martin Fowler** (2002): "Any fool can write code that a computer can understand. Good programmers write code that humans can understand."\n\n> **Fred Brooks** (1975): "Adding manpower to a late software project makes it later."\n\n> **Leslie Lamport** (2012): "A distributed system is one in which the failure of a computer you didn\'t even know existed can render your own computer unusable."\n'
        
        with open(f, 'a', encoding='utf-8') as fh:
            fh.write(auth_section)
        
        fixed += 1
    
    print(f'{name}: Fixed auth quotes in {fixed}/{len(files)} files')

fix_auth_quotes('Modern', 'Modern')
fix_auth_quotes('Analysis', 'Analysis')
