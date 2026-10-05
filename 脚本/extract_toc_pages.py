# -*- coding: utf-8 -*-
"""从首轮渲染的 PDF 中提取目录链接的目标页码，输出 toc_pages.json 供第二遍构建注入。"""
import fitz, json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PDF = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '成稿', 'WorkBuddy实战指南.pdf')
OUT = os.path.join(ROOT, '..', '成稿', 'toc_pages.json')

doc = fitz.open(PDF)
# 目录页 = 前 6 页里含 "目 录" 标题的页；目录链接的 nameddest 形如 sec-N
pagemap = {}
for pno in range(min(8, len(doc))):
    page = doc[pno]
    for lk in page.get_links():
        dest = lk.get('nameddest') or ''
        if not dest.startswith('sec-'):
            # 某些链路只给 page，不给名字；跳过无名项
            continue
        target = lk.get('page')
        if target is not None and target >= 0:
            pagemap[dest] = target + 1  # 1-based
if not pagemap:
    print('ERROR: no named destinations found in TOC links'); sys.exit(1)
json.dump(pagemap, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('pagemap:', len(pagemap), 'entries ->', OUT)
total = len(doc)
missing = [f'sec-{i}' for i in range(1, total) if f'sec-{i}' not in pagemap]
print('missing:', missing if missing else 'none')
