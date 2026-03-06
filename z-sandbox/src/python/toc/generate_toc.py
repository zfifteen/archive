#!/usr/bin/env python3
import os, re, sys
from pathlib import Path

DOCS_DIR = Path('docs')
OUT_FILE = DOCS_DIR / 'TOC.md'

def slugify(text: str) -> str:
    t = text.strip().lower()
    t = re.sub(r"[`~!@#$%^&*()=+[{]}\\|;:'\",.<>/?]", '', t)
    t = re.sub(r"\s+", '-', t)
    t = re.sub(r"-+", '-', t)
    return t

def humanize_name(p: Path) -> str:
    name = p.stem.replace('_',' ').replace('-', ' ')
    return name.title()

def parse_headings(path: Path):
    heads = []
    try:
        with path.open('r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if not line.startswith('#'): continue
                m = re.match(r"^(#{1,6})\s+(.*)$", line.strip())
                if not m: continue
                level = len(m.group(1))
                title = m.group(2).strip()
                heads.append((level, title))
    except Exception:
        pass
    return heads

def collect_files():
    files = []
    if not DOCS_DIR.exists():
        return files
    for root, dirs, filenames in os.walk(DOCS_DIR):
        # skip hidden dirs
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for fn in filenames:
            if not fn.lower().endswith('.md'): continue
            p = Path(root) / fn
            if p.name == 'TOC.md':
                continue
            files.append(p)
    files.sort()
    return files

def build_toc(files):
    lines = []
    lines.append('# Table of Contents')
    lines.append('')
    for p in files:
        rel = p.relative_to(DOCS_DIR)
        heads = parse_headings(p)
        # File title
        title = None
        for lvl, t in heads:
            if lvl == 1:
                title = t
                break
        if not title:
            title = humanize_name(rel)
        lines.append(f"- [{title}]({rel.as_posix()})")
        # Subheadings H2/H3
        for lvl, t in heads:
            if lvl not in (2,3):
                continue
            indent = '  ' * (lvl-1)
            anchor = slugify(t)
            lines.append(f"{indent}- [{t}]({rel.as_posix()}#{anchor})")
    lines.append('')
    return '\n'.join(lines)

def main():
    files = collect_files()
    toc = build_toc(files)
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    prev = ''
    if OUT_FILE.exists():
        prev = OUT_FILE.read_text(encoding='utf-8', errors='ignore')
    if toc != prev:
        OUT_FILE.write_text(toc, encoding='utf-8')
        print('TOC_UPDATED=1')
    else:
        print('TOC_UPDATED=0')

if __name__ == '__main__':
    sys.exit(main())