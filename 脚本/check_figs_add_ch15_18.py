# -*- coding: utf-8 -*-
"""新增 SVG 版式自检：估算文字边界、等宽行宽、底部越界。"""
import re, glob, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
NEW = ['15-13', '15-14', '15-15', '15-16', '15-17', '15-18', '15-19',
       '16-7', '16-8', '16-9', '16-10', '16-11', '16-12', '16-13', '16-14', '16-15',
       '17-11', '17-12', '17-13', '17-14', '17-15', '17-16', '17-17', '17-18',
       '17-19', '17-20', '17-21', '17-22',
       '18-6', '18-7', '18-8', '18-9', '18-10', '18-11', '18-12']

files = sorted(glob.glob(os.path.join(ROOT, '配图', 'svg', 'fig-1[5-8]-*.svg')))
new = [f for f in files if any(('fig-' + n + '-') in f for n in NEW)]
print('新增 %d 张，抽查 %d 张' % (len(NEW), len(new)))


def wid(s, fs):
    return sum(fs * (1.0 if ord(c) > 0x2E80 else 0.55) for c in s)


prob = 0
for f in new:
    name = os.path.basename(f)
    t = open(f, encoding='utf-8').read()
    for m in re.finditer(
            r'<text x="([\d.\-]+)" y="([\d.\-]+)"[^>]*font-size="(\d+)"'
            r'[^>]*text-anchor="(\w+)"[^>]*>([^<]*)</text>', t):
        x, y, fs = float(m.group(1)), float(m.group(2)), int(m.group(3))
        anch, s = m.group(4), m.group(5)
        d = wid(s, fs)
        x0 = x - d / 2 if anch == 'middle' else (x - d if anch == 'end' else x)
        if x0 < 20 or x0 + d > 982 or y > 640 or y < 10:
            print('溢出', name, 'x0=%.0f x1=%.0f y=%.0f' % (x0, x0 + d, y), repr(s[:40]))
            prob += 1
    for m in re.finditer(
            r'<text x="([\d.\-]+)" y="([\d.\-]+)" font-family="Consolas[^"]*"'
            r' font-size="(\d+)"[^>]*>([^<]*)</text>', t):
        x, y, fs, s = float(m.group(1)), float(m.group(2)), int(m.group(3)), m.group(4)
        d = sum(fs * 0.6 * (2 if ord(c) > 0x2E80 else 1) for c in s)
        if x + d > 990:
            print('等宽超宽', name, 'x1=%.0f y=%.0f' % (x + d, y), repr(s[:50]))
            prob += 1
    ys = [float(m.group(1)) for m in
          re.finditer(r'<text x="[\d.\-]+" y="([\d.\-]+)"', t)]
    if ys and max(ys) > 648:
        print('底部越界', name, max(ys))
        prob += 1
print('版式问题', prob)
sys.exit(1 if prob else 0)