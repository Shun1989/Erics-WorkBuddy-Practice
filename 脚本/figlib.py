# -*- coding: utf-8 -*-
"""全书配图 SVG 工厂库（纯标准库）

统一版式：1000 x 650，米白底 #FAFAF8，墨色字 #1C2026
所有执笔脚本只调用本库的函数，不自己拼 SVG，保证 162 张图风格一致。
"""
import os

W, H = 1000, 650
BG    = '#FAFAF8'
INK   = '#1C2026'
GRAY  = '#6B7280'
ORANGE= '#E0632D'
TEAL  = '#2D6A6A'
LINE  = '#E5E1DA'
PANEL = '#F2EDE6'
FONT  = "Microsoft YaHei, PingFang SC, Noto Sans CJK SC, sans-serif"
OUT   = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '配图', 'svg')


# ---------------- 基础工具 ----------------
def esc(t):
    return (str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def cw(ch, fs):
    """单个字符的估算宽度"""
    return fs * (1.0 if ord(ch) > 0x2E80 else 0.55)


def tw(t, fs):
    return sum(cw(c, fs) for c in str(t))


def wrap(t, maxw, fs):
    """中英混排折行：优先在标点/空格处断，其次硬断"""
    t = str(t)
    lines, cur = [], ''
    for ch in t:
        if tw(cur + ch, fs) > maxw and cur:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


def txt(x, y, s, fs=16, fill=INK, anchor='start', weight='normal', opacity=None):
    op = f' opacity="{opacity}"' if opacity else ''
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{fs}" '
            f'fill="{fill}" text-anchor="{anchor}" font-weight="{weight}"{op}>{esc(s)}</text>')


def lines_block(x, y, ls, fs=15, fill=INK, lh=None, anchor='start', weight='normal'):
    lh = lh or int(fs * 1.5)
    return '\n'.join(txt(x, y + i * lh, s, fs, fill, anchor, weight) for i, s in enumerate(ls))


def rect(x, y, w, h, fill='#FFFFFF', stroke=LINE, sw=1.5, rx=10, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def arrow_def(color):
    return (f'<marker id="ar-{color.strip("#")}" viewBox="0 0 10 10" refX="9" refY="5" '
            f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker>')


def arrow(x1, y1, x2, y2, color=GRAY, sw=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{sw}" marker-end="url(#ar-{color.strip("#")})"{d}/>')


def path_arrow(d, color=GRAY, sw=2, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" '
            f'marker-end="url(#ar-{color.strip("#")})"{da}/>')


# ---------------- 画布骨架 ----------------
def begin(title, subtitle=None, note=None):
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="{BG}"/>',
         arrow_def(GRAY), arrow_def(ORANGE), arrow_def(TEAL), arrow_def(INK),
         txt(56, 58, title, 27, INK, weight='bold')]
    y = 58
    if subtitle:
        s.append(txt(56, 88, subtitle, 15, GRAY))
        y = 88
    s.append(f'<line x1="56" y1="{y+18}" x2="{W-56}" y2="{y+18}" stroke="{LINE}" stroke-width="1.5"/>')
    if note:
        s.append(txt(56, H - 34, note, 13, GRAY))
    return s


def end(parts):
    parts.append('</svg>')
    return '\n'.join(parts)


def save(name, svg):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, name if name.endswith('.svg') else name + '.svg')
    open(p, 'w', encoding='utf-8').write(svg)
    return p


def head_body(item):
    """把 ('标题','正文') 或 '单行' 统一成 (head, body_lines)"""
    if isinstance(item, (tuple, list)):
        head = item[0]
        body = item[1] if len(item) > 1 else ''
        if isinstance(body, (list, tuple)):
            body = list(body)
        else:
            body = [body] if body else []
        return head, body
    return str(item), []


# ---------------- 模板 1：流程图 ----------------
def flow(title, subtitle, steps, cols=None, note=None, color=TEAL, top=140):
    """steps: ['步骤一','步骤二'] 或 [('标题','正文'), ...]"""
    n = len(steps)
    cols = cols or (4 if n <= 4 else (3 if n <= 9 else 4))
    rows = (n + cols - 1) // cols
    bw, gap = (W - 112 - (cols - 1) * 28) / cols, 28
    if rows == 1:
        top, bh = 200, 170
    else:
        bh = min(126, (600 - top) / rows - 34)
    items = [head_body(s) for s in steps]
    s = begin(title, subtitle, note)
    pos = []
    for i, (hd, bd) in enumerate(items):
        r, c = divmod(i, cols)
        x = 56 + c * (bw + gap)
        y = top + r * (bh + 34)
        s.append(rect(x, y, bw, bh, '#FFFFFF', LINE, 1.5, 10))
        s.append(rect(x, y, 6, bh, color, color, 0, 3))
        s.append(txt(x + 20, y + 30, hd, 17, INK, weight='bold'))
        s.append(lines_block(x + 20, y + 56, wrap(''.join(bd), bw - 40, 14), 14, GRAY, 21))
        pos.append((x, y))
        if c < cols - 1 and i + 1 < n:
            s.append(arrow(x + bw + 4, y + bh / 2, x + bw + gap - 4, y + bh / 2, color, 2))
        if c == cols - 1 and r < rows - 1 and i + 1 < n:
            # 行末折返：永远回到下一行行首（阅读顺序固定从左到右）
            d = (f'M{x+bw/2:.0f},{y+bh:.0f} L{x+bw/2:.0f},{y+bh+16:.0f} '
                 f'L{56+bw/2:.0f},{y+bh+16:.0f} L{56+bw/2:.0f},{y+bh+30:.0f}')
            s.append(path_arrow(d, color, 2))
    return end(s)


# ---------------- 模板 2：左右对比 ----------------
def compare(title, subtitle, ltitle, litems, rtitle, ritems, note=None,
            lcolor=GRAY, rcolor=ORANGE):
    pw = (W - 112 - 40) / 2
    s = begin(title, subtitle, note)
    for k, (tt, items, col) in enumerate([(ltitle, litems, lcolor), (rtitle, ritems, rcolor)]):
        x = 56 + k * (pw + 40)
        s.append(rect(x, 138, pw, 430, '#FFFFFF', LINE, 1.5, 12))
        s.append(rect(x, 138, pw, 46, col, col, 0, 12))
        s.append(txt(x + pw / 2, 167, tt, 17, '#FFFFFF', 'middle', 'bold'))
        y = 205
        for it in items:
            if isinstance(it, (tuple, list)):
                hd, bd = it[0], (it[1] if len(it) > 1 else '')
                s.append(txt(x + 22, y, '▍', 15, col))
                s.append(txt(x + 38, y, hd, 16, INK, weight='bold'))
                y += 24
                for ln in wrap(bd, pw - 60, 14):
                    s.append(txt(x + 38, y, ln, 14, GRAY))
                    y += 21
                y += 12
            else:
                for j, ln in enumerate(wrap(it, pw - 60, 15)):
                    s.append(txt(x + 22, y, ('· ' if j == 0 else '  ') + ln, 15, INK))
                    y += 22
                y += 10
    return end(s)


# ---------------- 模板 3：树 / 结构 ----------------
def tree(title, subtitle, root, branches, note=None, color=TEAL):
    """branches: [('分支名','说明'), ...] 或 [('分支名',['子项1','子项2']), ...]"""
    n = len(branches)
    bw = min(230, (W - 112 - (n - 1) * 20) / n)
    gap = (W - 112 - n * bw) / max(n - 1, 1)
    s = begin(title, subtitle, note)
    rw = min(320, max(200, tw(root, 19) + 60))
    s.append(rect((W - rw) / 2, 136, rw, 52, color, color, 0, 10))
    s.append(txt(W / 2, 168, root, 19, '#FFFFFF', 'middle', 'bold'))
    y2 = 240
    xs = []
    for i, b in enumerate(branches):
        x = 56 + i * (bw + gap) + (0 if n > 1 else (W - 112 - bw) / 2)
        xs.append(x)
    for i, b in enumerate(branches):
        hd, sub = b[0], (b[1] if len(b) > 1 else '')
        x = xs[i]
        cy = y2 + 26
        s.append(path_arrow(f'M{W/2:.0f},188 L{W/2:.0f},{y2-14:.0f} L{x+bw/2:.0f},{y2-14:.0f} '
                            f'L{x+bw/2:.0f},{y2:.0f}', GRAY, 1.6))
        s.append(rect(x, y2, bw, 46, '#FFFFFF', LINE, 1.5, 8))
        s.append(txt(x + bw / 2, cy, hd, 15, INK, 'middle', 'bold'))
        yy = y2 + 66
        if isinstance(sub, (list, tuple)):
            for it in sub:
                s.append(rect(x + 8, yy, bw - 16, 40, PANEL, LINE, 1, 6))
                for j, ln in enumerate(wrap(it, bw - 40, 13)[:2]):
                    s.append(txt(x + 20, yy + 17 + j * 17, ln, 13, GRAY))
                yy += 48
        elif sub:
            for ln in wrap(sub, bw - 24, 13)[:3]:
                s.append(txt(x + bw / 2, yy, ln, 13, GRAY, 'middle'))
                yy += 19
    return end(s)


# ---------------- 模板 4：表格矩阵 ----------------
def matrix(title, subtitle, headers, rows, note=None, colw=None, color=TEAL):
    n = len(headers)
    x0, x1 = 56, W - 56
    colw = colw or [(x1 - x0) / n] * n
    s = begin(title, subtitle, note)
    y = 138
    hh = 44
    s.append(rect(x0, y, x1 - x0, hh, color, color, 0, 8))
    cx = x0
    for i, hd in enumerate(headers):
        s.append(txt(cx + 14, y + 28, hd, 16, '#FFFFFF', weight='bold'))
        cx += colw[i]
    y += hh
    for ri, row in enumerate(rows):
        rh = 40 + 22 * (max(len(wrap(c, colw[k] - 24, 14)) for k, c in enumerate(row)) - 1)
        if ri % 2 == 1:
            s.append(rect(x0, y, x1 - x0, rh, PANEL, PANEL, 0, 0))
        cx = x0
        for k, c in enumerate(row):
            for j, ln in enumerate(wrap(c, colw[k] - 24, 14)):
                s.append(txt(cx + 14, y + 26 + j * 21, ln, 14, INK if k == 0 else GRAY,
                             weight='bold' if k == 0 else 'normal'))
            cx += colw[k]
        s.append(f'<line x1="{x0}" y1="{y+rh}" x2="{x1}" y2="{y+rh}" stroke="{LINE}" stroke-width="1"/>')
        y += rh
    return end(s)


# ---------------- 模板 5：循环 ----------------
def cycle(title, subtitle, items, center='', note=None, color=TEAL):
    n = len(items)
    cx, cy, rx, ry = W / 2, 370, 300, 165
    s = begin(title, subtitle, note)
    s.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{LINE}" '
             f'stroke-width="1.5" stroke-dasharray="6 5"/>')
    if center:
        s.append(f'<circle cx="{cx}" cy="{cy}" r="70" fill="{PANEL}" stroke="{LINE}"/>')
        for j, ln in enumerate(wrap(center, 110, 15)):
            s.append(txt(cx, cy - 6 + j * 22, ln, 15, INK, 'middle', 'bold'))
    pts = []
    import math
    for i in range(n):
        a = -math.pi / 2 + 2 * math.pi * i / n
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        sx, sy = cx + (mx - cx) * 1.02, cy + (my - cy) * 1.02
        s.append(path_arrow(f'M{x1:.0f},{y1:.0f} Q{sx:.0f},{sy:.0f} {x2:.0f},{y2:.0f}', color, 1.8))
    for i, (x, y) in enumerate(pts):
        hd, bd = head_body(items[i])
        bw = min(240, max(160, tw(hd, 15) + 44))
        bh = 58 if not bd else 76
        s.append(rect(x - bw / 2, y - bh / 2, bw, bh, '#FFFFFF', LINE, 1.5, 9))
        s.append(txt(x, y - 6 + (0 if bd else 7), hd, 15, INK, 'middle', 'bold'))
        if bd:
            for j, ln in enumerate(wrap(''.join(bd), bw - 26, 12)[:2]):
                s.append(txt(x, y + 16 + j * 16, ln, 12, GRAY, 'middle'))
    return end(s)


# ---------------- 模板 6：清单（对勾 / 叉 / 警示） ----------------
def checklist(title, subtitle, items, note=None, color=TEAL):
    """items: [('ok','该做的'), ('no','不该做的'), ('warn','注意')]"""
    marks = {'ok': ('✓', TEAL), 'no': ('✕', ORANGE), 'warn': ('!', '#C2410C'), 'dot': ('·', GRAY)}
    s = begin(title, subtitle, note)
    y = 148
    for it in items:
        mk, tx = it[0], it[1]
        sub = it[2] if len(it) > 2 else None
        sym, col = marks.get(mk, marks['dot'])
        s.append(f'<circle cx="72" cy="{y-5}" r="14" fill="#FFFFFF" stroke="{col}" stroke-width="1.5"/>')
        s.append(txt(72, y, sym, 15, col, 'middle', 'bold'))
        s.append(txt(100, y, tx, 17, INK, weight='bold'))
        y += 26
        if sub:
            for ln in wrap(sub, W - 200, 14):
                s.append(txt(100, y, ln, 14, GRAY))
                y += 20
        y += 20
    return end(s)


# ---------------- 模板 7：分层架构 ----------------
def stack(title, subtitle, layers, note=None, color=TEAL, bottom_up=False):
    """layers: [('层名','说明'), ...] 自上而下"""
    n = len(layers)
    lh = min(78, (590 - 140) / n - 12)
    s = begin(title, subtitle, note)
    seq = layers[::-1] if bottom_up else layers
    for i, lay in enumerate(seq):
        hd, bd = lay[0], (lay[1] if len(lay) > 1 else '')
        y = 140 + i * (lh + 12)
        shade = TEAL if i == (n - 1 if bottom_up else 0) else GRAY
        s.append(rect(90, y, W - 180, lh, '#FFFFFF', LINE, 1.5, 10))
        s.append(rect(90, y, 8, lh, shade, shade, 0, 4))
        s.append(txt(120, y + 30, hd, 17, INK, weight='bold'))
        if bd:
            for j, ln in enumerate(wrap(bd, W - 320, 14)[:2]):
                s.append(txt(120, y + 52 + j * 19, ln, 14, GRAY))
    return end(s)


# ---------------- 模板 8：横向条对比 ----------------
def bars(title, subtitle, bars, note=None, unit='', color=TEAL, color2=ORANGE):
    """bars: [('标签', 数值, '显示文本'), ...]"""
    mx = max(b[1] for b in bars) or 1
    s = begin(title, subtitle, note)
    y = 158
    lw = 210
    bw_max = W - 56 - 56 - lw - 130
    for i, b in enumerate(bars):
        lb, v, disp = b[0], b[1], (b[2] if len(b) > 2 else f'{v}{unit}')
        col = color if i % 2 == 0 else color2
        s.append(txt(56, y + 22, lb, 16, INK, weight='bold'))
        s.append(rect(56 + lw, y + 6, bw_max, 24, PANEL, PANEL, 0, 6))
        s.append(rect(56 + lw, y + 6, max(6, bw_max * v / mx), 24, col, col, 0, 6))
        s.append(txt(56 + lw + bw_max + 16, y + 23, disp, 15, GRAY, weight='bold'))
        y += 46
    return end(s)


# ---------------- 模板 9：卡片组 ----------------
def cards(title, subtitle, items, cols=2, note=None, color=TEAL):
    n = len(items)
    cw_ = (W - 112 - (cols - 1) * 26) / cols
    rows = (n + cols - 1) // cols
    ch = min(160, (600 - 140) / rows - 20)
    s = begin(title, subtitle, note)
    for i, it in enumerate(items):
        hd, bd = head_body(it)
        r, c = divmod(i, cols)
        x = 56 + c * (cw_ + 26)
        y = 140 + r * (ch + 20)
        s.append(rect(x, y, cw_, ch, '#FFFFFF', LINE, 1.5, 12))
        s.append(rect(x, y, cw_, 42, PANEL, PANEL, 0, 12))
        s.append(txt(x + 20, y + 28, hd, 16, INK, weight='bold'))
        yy = y + 66
        for ln in wrap(''.join(bd) if isinstance(bd, (list, tuple)) else bd, cw_ - 40, 14)[:5]:
            s.append(txt(x + 20, yy, ln, 14, GRAY))
            yy += 20
    return end(s)


# ---------------- 模板 10：编号步骤 + 提示词框 ----------------
def steps(title, subtitle, items, note=None, color=ORANGE):
    """items: [('做什么','为什么/注意'), ...] 竖排带序号"""
    s = begin(title, subtitle, note)
    y = 146
    for i, it in enumerate(items):
        hd, bd = head_body(it)
        s.append(f'<circle cx="78" cy="{y+4}" r="17" fill="{color}"/>')
        s.append(txt(78, y + 10, str(i + 1), 16, '#FFFFFF', 'middle', 'bold'))
        s.append(txt(112, y + 10, hd, 17, INK, weight='bold'))
        y += 28
        if bd:
            for ln in wrap(''.join(bd) if isinstance(bd, (list, tuple)) else bd, W - 220, 14)[:3]:
                s.append(txt(112, y, ln, 14, GRAY))
                y += 20
        y += 24
    return end(s)


# ---------------- 模板 11：代码/终端示意 ----------------
def terminal(title, subtitle, lines, note=None):
    s = begin(title, subtitle, note)
    s.append(rect(56, 140, W - 112, 420, '#1C2026', '#1C2026', 0, 12))
    y = 172
    for ln in lines:
        if isinstance(ln, tuple):
            col, t = ln[0], ln[1]
        else:
            col, t = '#E5E1DA', ln
        if t.startswith('$'):
            s.append(txt(80, y, '$', 15, ORANGE, weight='bold'))
            s.append(txt(100, y, t[1:], 15, '#FAFAF8'))
        else:
            s.append(txt(100, y, t, 15, col))
        y += 26
    return end(s)


# ---------------- 模板 12：时间轴 ----------------
def timeline(title, subtitle, items, note=None, color=TEAL):
    """items: [('时间点','事'), ...]"""
    n = len(items)
    y0 = 300
    s = begin(title, subtitle, note)
    s.append(f'<line x1="80" y1="{y0}" x2="{W-80}" y2="{y0}" stroke="{LINE}" stroke-width="2"/>')
    step = (W - 160) / max(n - 1, 1)
    for i, it in enumerate(items):
        hd, bd = head_body(it)
        x = 80 + i * step
        up = i % 2 == 0
        s.append(f'<circle cx="{x}" cy="{y0}" r="9" fill="{color}"/>')
        ly = y0 - 40 if up else y0 + 50
        s.append(f'<line x1="{x}" y1="{y0-12 if up else y0+12}" x2="{x}" y2="{ly+(0 if up else -14)}" '
                 f'stroke="{color}" stroke-width="1.5"/>')
        ty = ly - (18 * 0) + (0 if up else 14)
        s.append(txt(x, ty, hd, 16, INK, 'middle', 'bold'))
        yy = ty + (22 if up else 22)
        for ln in wrap(''.join(bd) if isinstance(bd, (list, tuple)) else bd, step - 30, 13)[:3]:
            s.append(txt(x, yy, ln, 13, GRAY, 'middle'))
            yy += 18
    return end(s)


def placeholder(name, title='配图待补'):
    s = begin(title, name)
    s.append(rect(200, 220, 600, 200, PANEL, LINE, 2, 12))
    s.append(txt(W / 2, 340, '配图待补', 24, GRAY, 'middle', 'bold'))
    return end(s)
