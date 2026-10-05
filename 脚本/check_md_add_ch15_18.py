# -*- coding: utf-8 -*-
"""新增配图交稿自检：图引用完整性、图注、图题、违禁词、文件名冲突。"""
import io, os, re, glob, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
CH = os.path.join(ROOT, '书稿', '05_第四篇_场景实战')
SVG = os.path.join(ROOT, '配图', 'svg')

NEW = ['15-13', '15-14', '15-15', '15-16', '15-17', '15-18', '15-19',
       '16-7', '16-8', '16-9', '16-10', '16-11', '16-12', '16-13', '16-14', '16-15',
       '17-11', '17-12', '17-13', '17-14', '17-15', '17-16', '17-17', '17-18',
       '17-19', '17-20', '17-21', '17-22',
       '18-6', '18-7', '18-8', '18-9', '18-10', '18-11', '18-12']

BAN = ['座椅', '滑轨', '调角器', '头枕', '腰托', '靠背', '坐垫', 'Brose', '博泽',
       'ChatGPT', 'Claude', 'Gemini', 'DeepSeek', '通义', '文心', '混元', 'Kimi',
       '豆包', '智谱', '——', '赋能', '抓手', '闭环', '沉淀', '对齐', '拉通',
       '打通', '范式', '至关重要', '值得注意的是', '综上所述', '简而言之', '颗粒度']

bad = 0
cnt = 0
pat = re.compile(r'!\[图 (\d+-\d+) (.+?)\]\(\.\./\.\./配图/svg/([^)]+)\)')

for f in sorted(glob.glob(os.path.join(CH, '第1[5-8]章*.md'))):
    lines = io.open(f, encoding='utf-8').read().split('\n')
    nums = []
    for i, l in enumerate(lines):
        m = pat.match(l.strip())
        if not m:
            continue
        num, ttl, fn = m.groups()
        nums.append(int(num.split('-')[1]))
        if num not in NEW:
            continue
        cnt += 1
        if not os.path.exists(os.path.join(SVG, fn)):
            print('文件缺失', fn)
            bad += 1
        if len(ttl) < 10 or ttl.endswith('示意图') or ttl.endswith('流程图'):
            print('图题不合格', num, ttl)
            bad += 1
        if i + 2 >= len(lines) or \
                lines[i + 2].strip() != '*图 %s 作者根据公开资料绘制。*' % num:
            print('图注缺失或错位', num, repr(lines[i + 1:i + 4]))
            bad += 1
        if lines[i + 1].strip() != '':
            print('图后缺空行', num)
            bad += 1
        if '→' in l:
            print('箭头字符', num)
            bad += 1
        for b in BAN:
            if b in ttl:
                print('图题违禁', num, b)
                bad += 1
    exp = list(range(1, max(nums) + 1))
    tag = '连续' if sorted(nums) == exp else '不连续 缺%s' % sorted(set(exp) - set(nums))
    print('%-34s %2d 张  %s' % (os.path.basename(f), len(nums), tag))

# 新增 SVG 违禁词与文件名冲突
names = [os.path.basename(p) for p in glob.glob(os.path.join(SVG, '*.svg'))]
if len(names) != len(set(names)):
    print('文件名冲突')
    bad += 1
print('配图目录总数 %d，唯一 %d' % (len(names), len(set(names))))

for n in NEW:
    hits = glob.glob(os.path.join(SVG, 'fig-%s-*.svg' % n))
    if len(hits) != 1:
        print('新增图数量异常', n, len(hits))
        bad += 1
        continue
    t = io.open(hits[0], encoding='utf-8').read()
    for b in BAN:
        if b in t:
            print('SVG 违禁', os.path.basename(hits[0]), b)
            bad += 1

print('新增图引用 %d 张，问题 %d 处' % (cnt, bad))
sys.exit(1 if bad else 0)