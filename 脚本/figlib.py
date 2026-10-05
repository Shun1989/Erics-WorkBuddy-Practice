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
        # 脚注自动折行：13pt 中文每字约 13px，可用宽度 W-112，最多两行
        avail = W - 112
        nl = wrap(str(note), avail, 13)
        if len(nl) > 2:
            tail = nl[1][:-1] + '…' if len(nl[1]) > 1 else '…'
            nl = [nl[0], tail]
        base = H - 34 - (len(nl) - 1) * 20
        for i, ln in enumerate(nl):
            s.append(txt(56, base + i * 20, ln, 13, GRAY))
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


# ================================================================
# 第二批：界面复刻类模板（2026-10-05 出版级升级新增）
# 用途：把书里真实的提示词、文件路径、终端输出、产物内容，
#       渲染成「界面长什么样」，内容真、形式是复刻。
# ================================================================

MONO = "Consolas, Menlo, Courier New, monospace"
DARK = '#1C2026'
DARK2 = '#2A2F37'


def mono(x, y, s, fs=13, fill='#E5E1DA', anchor='start', weight='normal'):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{MONO}" font-size="{fs}" '
            f'fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{esc(s)}</text>')


def wrapw(text, cols):
    """按视觉宽度（以半角为 1 单位）折行，用于等宽字体与路径"""
    out, cur, w = [], '', 0
    for ch in str(text):
        cw_ = 2 if ord(ch) > 0x2E80 else 1
        if w + cw_ > cols and cur:
            out.append(cur)
            cur, w = ch, cw_
        else:
            cur += ch
            w += cw_
    if cur:
        out.append(cur)
    return out


def chrome(s, x, y, w, h, title, dark=True, tabs=None):
    """窗口外框：标题栏 + 可选标签页，返回内容区起始 y"""
    bg = DARK if dark else '#FFFFFF'
    fg = '#E5E1DA' if dark else INK
    s.append(rect(x, y, w, h, bg, '#3A4049' if dark else LINE, 1.5, 10))
    s.append(f'<path d="M{x+10},{y+34} L{x+w-10},{y+34}" stroke="#3A4049" stroke-width="1"/>')
    for i, c in enumerate(['#E05C5C', '#E0A95C', '#5CB87C']):
        s.append(f'<circle cx="{x+20+i*16}" cy="{y+17}" r="5" fill="{c}"/>')
    s.append(txt(x + w / 2, y + 22, title, 14, fg, 'middle', 'bold'))
    cy = y + 34
    if tabs:
        cx = x + 12
        for i, t in enumerate(tabs):
            tw_ = tw(t, 13) + 24
            act = (i == 0)
            s.append(rect(cx, cy + 4, tw_, 28, '#2E343D' if act else bg,
                          '#3A4049' if act else bg, 1, 6))
            s.append(txt(cx + tw_ / 2, cy + 23, t, 13, fg if act else GRAY, 'middle',
                         'bold' if act else 'normal'))
            cx += tw_ + 6
        cy += 36
    return cy + 14


# ---- 模板 13：AI 对话框（用户气泡 + AI 气泡 + 模式标签 + 状态栏）----
def chat(title, subtitle, turns, note=None, mode='Plan', files=None, status=None):
    """turns: [('me','用户说的话'), ('ai','AI 回的话'), ...]，ai 可多段
    files / status 吸底对齐，形成「对话在上、状态在下」的三段式版式"""
    s = begin(title, subtitle, note)
    bw = W - 112
    MW, AW = bw * 0.56, bw * 0.72          # 我方气泡宽 / 对方气泡宽
    top, bot = 132, H - (58 if note else 16)
    fh = (30 + len(files) * 34) if files else 0
    sh = (40 if status else 0)
    # 第一遍：算每个气泡的高度与对话区总高
    hs = []
    for who, body in turns:
        if who == 'me':
            hs.append(34 + len(wrap(body, MW - 32, 15)) * 22 + 16)
        else:
            hs.append(40 + len(wrap(body, AW - 40, 15)) * 22 + 16)
    chat_h = sum(hs) - 16 if hs else 0
    free = bot - top - chat_h - (fh + sh + 24)
    y = top + max(0, min(free * 0.40, 56))     # 内容偏少时略微下移，视觉不顶头
    for (who, body), bh_full in zip(turns, hs):
        bh = bh_full - 16
        if who == 'me':
            lines = wrap(body, MW - 32, 15)
            x = 56 + bw - MW
            s.append(rect(x, y, MW, bh, '#EDF1F5', '#EDF1F5', 0, 12))
            s.append(txt(x + 16, y + 24, '我', 13, GRAY, weight='bold'))
            s.append(lines_block(x + 16, y + 48, lines, 15, INK, 22))
        else:
            lines = wrap(body, AW - 40, 15)
            s.append(rect(56, y, AW, bh, '#FFFFFF', LINE, 1.5, 12))
            s.append(rect(56, y, 5, bh, TEAL, TEAL, 0, 3))
            s.append(txt(76, y + 24, 'WorkBuddy', 13, TEAL, weight='bold'))
            s.append(rect(160, y + 12, 52, 20, PANEL, LINE, 1, 5))
            s.append(txt(186, y + 26, mode, 12, GRAY, 'middle', 'bold'))
            s.append(lines_block(76, y + 48, lines, 15, INK, 22))
        y += bh_full
    if files:
        by = y + 10
        s.append(txt(56, by, '附件', 13, GRAY, weight='bold'))
        by += 10
        for f in files:
            s.append(rect(56, by, min(320, tw(f, 13) + 34), 28, '#FFFFFF', LINE, 1.2, 6))
            s.append(txt(70, by + 19, f, 13, INK))
            by += 34
    if status:
        sy = bot - sh + 6
        s.append(rect(56, sy, W - 112, 34, PANEL, LINE, 1.2, 8))
        s.append(f'<circle cx="76" cy="{sy+17}" r="5" fill="{TEAL}"/>')
        s.append(txt(92, sy + 22, status, 13, GRAY))
    return end(s)


# ---- 模板 14：文件树（真实目录结构）----
def filetree(title, subtitle, root, items, note=None, width=560, explain=None):
    """items: [('目录/','子目录名'), ('文件.py','2.1 KB'), ...]，用缩进字符串表示层级
    explain: 右侧解说文案（不传则不画右栏）"""
    s = begin(title, subtitle, note)
    x, y = 56, 132
    nline = 0
    if explain:
        nline = len(wrap(explain, W - 112 - width - 40, 14))
    need = 52 + len(items) * 26 + 24
    avail = H - 132 - (46 if note else 0)
    ph = min(max(need, 150), avail)
    s.append(rect(x, y, width, ph, '#FFFFFF', LINE, 1.5, 10))
    s.append(rect(x, y, width, 36, PANEL, LINE, 1.5, 10))
    s.append(txt(x + 16, y + 24, root, 14, INK, weight='bold'))
    y += 52
    for it in items:
        depth = len(it) - len(it.lstrip(' ')) // 2
        name = it.strip()
        isdir = name.endswith('/') or name.endswith('：')
        col = TEAL if isdir else INK
        s.append(txt(x + 16 + depth * 18, y, ('▸ ' if isdir else '') + name.rstrip('：/'),
                     14, col, weight='bold' if isdir else 'normal'))
        y += 26
    if explain:
        rx = x + width + 40
        s.append(txt(rx, 160, '这张图在说什么', 15, INK, weight='bold'))
        s.append(f'<line x1="{rx}" y1="172" x2="{rx+18}" y2="172" stroke="{ORANGE}" stroke-width="2.5"/>')
        yy = 196
        for ln in wrap(explain, W - 112 - width - 40, 14):
            s.append(txt(rx, yy, ln, 14, GRAY))
            yy += 22
    return end(s)


# ---- 模板 15：终端窗口（真实命令行 + 报错 + 补救）----
def term(title, subtitle, lines, note=None, fix=None):
    """lines: 字符串或 ('ok'|'err'|'dim'|'hl', 文本)"""
    h = 168 + len(lines) * 24
    s = begin(title, subtitle, note)
    cy = chrome(s, 56, 128, W - 112, min(h, 420), '终端  ·  bash')
    for ln in lines:
        if isinstance(ln, tuple):
            tag, t = ln[0], ln[1]
            col = {'ok': '#7FC48B', 'err': '#E05C5C', 'dim': '#8A9099',
                   'hl': '#E0A95C', 'cmd': '#FAFAF8'}.get(tag, '#E5E1DA')
        else:
            col, t = '#E5E1DA', ln
        if t.startswith('$'):
            s.append(mono(78, cy, '$', 14, '#E0A95C', weight='bold'))
            s.append(mono(96, cy, t[1:], 14, '#FAFAF8'))
        else:
            s.append(mono(78, cy, t, 14, col))
        cy += 24
    if fix:
        fy = 128 + min(h, 420) + 16
        s.append(rect(56, fy, W - 112, 62, '#FBF3EC', '#E8C9B4', 1.5, 10))
        s.append(txt(74, fy + 26, '补救动作', 14, ORANGE, weight='bold'))
        s.append(lines_block(160, fy + 26, wrap(fix, W - 260, 14)[:2], 14, INK, 21))
    return end(s)


# ---- 模板 16：Word 文档页（真实产物）----
def docpage(title, subtitle, heading, blocks, note=None, meta=None, kind='会议纪要', pages=1):
    """blocks: [('p','段落'), ('h','小标题'), ('t',[行,...]), ('b','• 要点')]"""
    s = begin(title, subtitle, note)
    px, py, pw = 150, 128, 700
    y = py + 76
    y += 16 + 32
    if meta:
        y += 26
    # 第一遍：只算高度，不出图
    for kb, val in blocks:
        if kb == 'h':
            y += 36
        elif kb == 'b':
            y += len(wrap(val, pw - 130, 14)) * 21 + 4
        elif kb == 't':
            y += 28 + (len(val) - 1) * 26 + 12
        else:
            y += len(wrap(val, pw - 112, 14)) * 22 + 8
    ph = min(max(y - py + 40, 220), H - py - (48 if note else 12))
    s.append(rect(px, py, pw, ph, '#FFFFFF', LINE, 1.5, 4))
    s.append(f'<line x1="{px+56}" y1="{py+40}" x2="{px+pw-56}" y2="{py+40}" stroke="{LINE}" stroke-width="1"/>')
    s.append(txt(px + 56, py + 30, kind, 12, GRAY))
    pgtxt = f'第 1 页 共 {pages} 页' if pages > 1 else '单页'
    s.append(txt(px + pw - 56, py + 30, pgtxt, 12, GRAY, 'end'))
    y = py + 76
    s.append(txt(px + 56, y, heading, 21, INK, weight='bold'))
    y += 16
    s.append(f'<line x1="{px+56}" y1="{y}" x2="{px+pw-56}" y2="{y}" stroke="{ORANGE}" stroke-width="2"/>')
    y += 32
    if meta:
        s.append(txt(px + 56, y, meta, 12, GRAY))
        y += 26
    for kb, val in blocks:
        if kb == 'h':
            y += 10
            s.append(txt(px + 56, y, val, 16, INK, weight='bold'))
            y += 26
        elif kb == 'b':
            for ln in wrap(val, pw - 130, 14):
                s.append(txt(px + 62, y, '· ' + ln, 14, INK))
                y += 21
            y += 4
        elif kb == 't':
            rows = val
            ncol = max(len(r) for r in rows)
            cw = (pw - 112) / ncol
            s.append(rect(px + 56, y, pw - 112, 28, PANEL, LINE, 1, 4))
            for i, c in enumerate(rows[0]):
                s.append(txt(px + 66 + i * cw, y + 19, c, 13, INK, weight='bold'))
            y += 28
            for r in rows[1:]:
                s.append(f'<line x1="{px+56}" y1="{y+26}" x2="{px+pw-56}" y2="{y+26}" stroke="{LINE}" stroke-width="1"/>')
                for i, c in enumerate(r):
                    s.append(txt(px + 66 + i * cw, y + 19, c, 13, GRAY))
                y += 26
            y += 12
        else:
            for ln in wrap(val, pw - 112, 14):
                s.append(txt(px + 56, y, ln, 14, '#3A3F47'))
                y += 22
            y += 8
    return end(s)


# ---- 模板 17：Excel 表格页（清洗前后对照）----
def sheet(title, subtitle, cols, before, after, changed=None, note=None, names=None):
    """changed: 需要高亮的 (行,列) 集合；names 为左右两栏标题"""
    changed = changed or set()
    s = begin(title, subtitle, note)
    hw = (W - 112) / 2
    nrows = max(len(before), len(after))
    ph = min(66 + 30 + nrows * 28 + 16, H - 190 - (48 if note else 12))
    ty = max(148, 132 + ((H - (58 if note else 16) - 132 - (ph + 36)) * 0.45))
    for k, rows in enumerate([before, after]):
        x = 56 + k * (hw + 24)
        hd = (names or ['清洗前', '清洗后'])[k]
        col = ORANGE if k == 0 else TEAL
        s.append(txt(x, ty, hd, 14, col, weight='bold'))
        s.append(f'<line x1="{x}" y1="{ty+8}" x2="{x+22}" y2="{ty+8}" stroke="{col}" stroke-width="2.5"/>')
        cw = (hw - 96) / len(cols)
        cy = chrome(s, x, ty + 22, hw, ph, '数据.xlsx  ·  Sheet1', dark=False)
        s.append(rect(x, cy - 26, hw, 26, '#F7F8FA', '#E5E1DA', 1, 0))
        for i in range(len(cols) + 1):
            s.append(txt(x + 12 + i * cw, cy - 9, chr(65 + i), 11, GRAY, 'middle'))
        s.append(txt(x + 46, cy - 34, 'fx', 12, GRAY))
        for i, c in enumerate(cols):
            s.append(rect(x + 10 + i * cw, cy, cw - 3, 26, PANEL, LINE, 1, 3))
            s.append(txt(x + 18 + i * cw, cy + 18, c, 12, INK, weight='bold'))
        y = cy + 30
        for ri, row in enumerate(rows):
            for ci, c in enumerate(row):
                hot = (ri, ci) in changed
                s.append(rect(x + 10 + ci * cw, y, cw - 3, 26,
                              '#FDEDE4' if hot and k == 0 else ('#EAF3F1' if hot else '#FFFFFF'),
                              LINE, 1, 3))
                s.append(txt(x + 18 + ci * cw, y + 18, c, 12,
                             ORANGE if (hot and k == 0) else (TEAL if hot else GRAY)))
            y += 28
    return end(s)


# ---- 模板 18：任务状态面板（Agent 在干什么）----
def taskpanel(title, subtitle, task, stages, done, elapsed, artifacts=None, note=None):
    s = begin(title, subtitle, note)
    # 深色面板：正文一律用浅色，标签用灰蓝
    TXT_C, SUB_C, DIM_C = '#E5E1DA', '#A8AFB8', '#7E8794'
    need = 34 + 44 + 22 + len(stages) * 30 + 10 + 24 + 34 + (60 + (len(artifacts) * 32) if artifacts else 0)
    ph = min(max(need, 200), H - 128 - (48 if note else 12))
    cy = chrome(s, 56, 128, W - 112, ph, 'WorkBuddy  ·  任务')
    s.append(txt(80, cy + 18, '任务', 13, SUB_C))
    s.append(txt(130, cy + 18, task, 15, TXT_C, weight='bold'))
    cy += 44
    s.append(txt(80, cy, '阶段', 13, SUB_C))
    cy += 22
    for i, (st, state) in enumerate(stages):
        col = {'done': '#5CB87C', 'now': ORANGE, 'wait': '#6B7280'}[state]
        sym = {'done': '✓', 'now': '▸', 'wait': '○'}[state]
        if state == 'now':
            s.append(rect(74, cy - 15, 640, 30, '#2A3038', '#2A3038', 0, 6))
        s.append(txt(84, cy + 4, sym, 14, col, weight='bold'))
        s.append(txt(108, cy + 4, st, 14, TXT_C if state != 'wait' else DIM_C,
                     weight='bold' if state == 'now' else 'normal'))
        cy += 30
    cy += 10
    s.append(f'<line x1="80" y1="{cy}" x2="{W-80}" y2="{cy}" stroke="#3A4049" stroke-width="1"/>')
    cy += 24
    s.append(txt(80, cy, f'已完成 {done} / {len(stages)} 个阶段', 14, TXT_C))
    s.append(txt(80, cy + 24, f'耗时 {elapsed}', 14, SUB_C))
    s.append(rect(300, cy + 10, 300, 12, '#2E343D', '#2E343D', 0, 6))
    s.append(rect(300, cy + 10, 300 * done / max(len(stages), 1), 12, TEAL, TEAL, 0, 6))
    if artifacts:
        ay = cy + 60
        s.append(txt(80, ay, '产物', 13, SUB_C, weight='bold'))
        ay += 22
        for a in artifacts:
            s.append(rect(78, ay - 14, min(560, tw(a, 13) + 30), 26, '#2A3038', '#3A4049', 1.2, 5))
            s.append(txt(90, ay + 4, a, 13, '#8FD4C4'))
            ay += 32
    return end(s)


# ---- 模板 19：提示词卡（等宽 + 变量高亮）----
def promptcard(title, subtitle, body, note=None, vars=None, width=None, chrome_title='提示词  ·  可直接复制'):
    """body 为提示词原文；vars 为需要高亮的变量名列表"""
    vars = vars or []
    s = begin(title, subtitle, note)
    w = width or (W - 112)
    x = 56 + (W - 112 - w) / 2
    all_lines = []
    for para in str(body).split('\n'):
        all_lines.extend(wrapw(para, int((w - 60) / 7.2)) or [''])
    h = min(H - 190 - (48 if note else 12), 62 + len(all_lines) * 19)
    ty = max(150, 128 + ((H - (58 if note else 16) - 128 - h) * 0.42))
    cy = chrome(s, x, ty, w, h, chrome_title)
    for ln in all_lines:
        hot = any(v in ln for v in vars)
        if hot:                                   # 关键约束行加底色，扫读时一眼抓到
            s.append(rect(70, cy - 15, w - 28, 21, '#3A2E1C', '#3A2E1C', 0, 4))
            s.append(rect(70, cy - 15, 3, 21, '#E0A95C', '#E0A95C', 0, 0))
        s.append(mono(80, cy, ln, 13, '#E0A95C' if hot else '#D8DCE2',
                      weight='bold' if hot else 'normal'))
        cy += 19
    return end(s)


# ---- 模板 20：报错面板（症状 + 原因 + 补救）----
def errpanel(title, subtitle, err, reasons, fixes, note=None):
    s = begin(title, subtitle, note)
    # 首行可能很长，等宽排版下要折行
    err_lines = []
    for i, ln in enumerate(err):
        err_lines.extend(wrapw(ln, 104))
    eh = 34 + 36 + len(err_lines) * 21 + 16
    ch = min(max(eh, 130), 230)
    nh_max = 0
    hw0 = (W - 112 - 28) / 2
    for items in (reasons, fixes):
        t = 40
        for it in items:
            t += len(wrap(it, hw0 - 50, 14)) * 20 + 12
        nh_max = max(nh_max, t)
    bh0 = min(max(nh_max + 20, 160), 260)
    ty0 = max(140, 128 + ((H - (58 if note else 16) - 128 - (ch + 24 + bh0)) * 0.42))
    cy = chrome(s, 56, ty0, W - 112, ch, 'WorkBuddy  ·  任务中断', tabs=['问题', '日志'])
    s.append(mono(80, cy, err_lines[0], 14, '#E05C5C', weight='bold'))
    cy += 22
    for ln in err_lines[1:]:
        s.append(mono(80, cy, ln, 13, '#AEB4BC'))
        cy += 21
    cy = ty0 + ch + 24
    hw = (W - 112 - 28) / 2
    bh = bh0
    for k, (hd, items, col) in enumerate([('可能原因', reasons, ORANGE),
                                          ('补救动作', fixes, TEAL)]):
        x = 56 + k * (hw + 28)
        s.append(rect(x, cy, hw, bh, '#FFFFFF', LINE, 1.5, 10))
        s.append(rect(x, cy, hw, 40, col, col, 0, 10))
        s.append(txt(x + 18, cy + 26, hd, 15, '#FFFFFF', weight='bold'))
        yy = cy + 66
        for it in items:
            lines = wrap(it, hw - 50, 14)
            s.append(txt(x + 18, yy, '·', 14, col, weight='bold'))
            s.append(lines_block(x + 34, yy, lines, 14, INK, 20))
            yy += len(lines) * 20 + 12
    return end(s)


# ---- 模板 21：前后对比（双栏 + 中间箭头）----
def beforeafter(title, subtitle, left, right, note=None, labels=('之前', '之后')):
    """left/right: (标题, [要点...])"""
    s = begin(title, subtitle, note)
    hw = (W - 112 - 60) / 2
    nh = 0
    for _hd, items in (left, right):
        t = 0
        for it in items:
            t += len(wrap(it, hw - 60, 14)) * 20 + 14
        nh = max(nh, t)
    bh = min(max(nh + 40, 180), H - 216 - (48 if note else 12))
    ty = 148
    by = ty + 16
    for k, ((hd, items), lab) in enumerate([(left, labels[0]), (right, labels[1])]):
        x = 56 + k * (hw + 60)
        col = GRAY if k == 0 else TEAL
        s.append(txt(x, ty, lab, 14, col, weight='bold'))
        s.append(f'<line x1="{x}" y1="{ty+8}" x2="{x+22}" y2="{ty+8}" stroke="{col}" stroke-width="2.5"/>')
        s.append(rect(x, by, hw, bh, '#FFFFFF', LINE, 1.5, 12))
        s.append(txt(x + 20, by + 32, hd, 16, INK, weight='bold'))
        s.append(f'<line x1="{x+20}" y1="{by+44}" x2="{x+hw-20}" y2="{by+44}" stroke="{col}" stroke-width="2"/>')
        yy = by + 72
        for it in items:
            lines = wrap(it, hw - 60, 14)
            s.append(txt(x + 20, yy, ('✕' if k == 0 else '✓'), 14, col, weight='bold'))
            s.append(lines_block(x + 42, yy, lines, 14, INK, 20))
            yy += len(lines) * 20 + 14
    ax = 56 + hw + 8
    s.append(f'<circle cx="{ax+22}" cy="{by + bh/2}" r="19" fill="{ORANGE}"/>')
    s.append(txt(ax + 22, by + bh / 2 + 7, '→', 19, '#FFFFFF', 'middle', 'bold'))
    return end(s)


# ---- 模板 22：属性表（参数面板，软件界面复刻）----
def proppanel(title, subtitle, groups, note=None):
    """groups: [(组名, [(参数, 值, 单位), ...]), ...]"""
    s = begin(title, subtitle, note)
    x, pw = 56, W - 112
    need = 22 + sum(40 + len(rows) * 28 + 10 for _g, rows in groups)
    ph = min(max(need, 180), H - 150 - (48 if note else 12))
    ty = max(140, 132 + ((H - (58 if note else 16) - 132 - ph) * 0.42))
    s.append(rect(x, ty, pw, ph, '#FFFFFF', LINE, 1.5, 10))
    y = ty + 22
    for gname, rows in groups:
        if y + 40 > ty + ph:
            break
        s.append(rect(x + 1, y, pw - 2, 32, PANEL, PANEL, 0, 6))
        s.append(txt(x + 18, y + 22, gname, 14, INK, weight='bold'))
        y += 40
        c1 = 300
        for i, row in enumerate(rows):
            if i % 2 == 1:
                s.append(rect(x + 1, y - 20, pw - 2, 28, '#FBFBFA', '#FBFBFA', 0, 0))
            name, val = row[0], row[1]
            unit = row[2] if len(row) > 2 else ''
            s.append(txt(x + 18, y, name, 14, GRAY))
            s.append(txt(x + c1, y, val, 14, INK, weight='bold'))
            if unit:
                s.append(txt(x + c1 + tw(val, 14) + 8, y, unit, 13, GRAY))
            y += 28
        y += 10
    return end(s)


# ---- 模板 23：甘特 / 排期条 ----
def gantt(title, subtitle, rows, note=None, today='今天', today_at=42, ticks=None):
    """rows: [(任务, 起, 止, 标注 or None)]，起止为 0-100 的百分比位置
    ticks: 6 个等距刻度标签，如 ['W1','W2',...]，不传则不画"""
    s = begin(title, subtitle, note)
    x0, pw = 250, W - 56 - 250
    rh = 34
    ch = len(rows) * rh + 16 + (22 if ticks else 0)
    y0 = max(180, 132 + ((H - (58 if note else 16) - 132 - ch) * 0.40))
    bot = y0 + ch - (22 if ticks else 0)
    for i in range(6):
        gx = x0 + pw * i / 5
        s.append(f'<line x1="{gx}" y1="{y0-20}" x2="{gx}" y2="{bot}" stroke="{LINE}" stroke-width="1"/>')
        if ticks and i < len(ticks):
            s.append(txt(gx, bot + 20, ticks[i], 12, GRAY, 'middle'))
    y = y0
    for name, a, b, tag in rows:
        s.append(txt(x0 - 14, y + 17, name, 14, INK, 'end'))
        s.append(rect(x0, y, pw, 24, '#F2F0EB', '#F2F0EB', 0, 5))
        bx = x0 + pw * a / 100
        bw = pw * (b - a) / 100
        col = ORANGE if tag else TEAL
        s.append(rect(bx, y, bw, 24, col, col, 0, 5))
        if tag:
            s.append(txt(bx + bw / 2, y + 17, tag, 12, '#FFFFFF', 'middle', 'bold'))
        y += rh
    tx = x0 + pw * today_at / 100
    s.append(f'<line x1="{tx}" y1="{y0-26}" x2="{tx}" y2="{bot}" stroke="{ORANGE}" stroke-width="1.5" stroke-dasharray="4 3"/>')
    s.append(txt(tx, y0 - 34, today, 12, ORANGE, 'middle', 'bold'))
    return end(s)


# ---- 模板 24：数据条（单指标横向对比，带口径说明）----
def databar(title, subtitle, items, unit='', note=None, caliber=None, scale=True):
    """items: [(标签, 数值, 显示文本, 是否高亮)]
    scale=False 时只画标签与结论，不画条（不同量纲不可比时用）"""
    mx = max(abs(i[1]) for i in items) or 1
    s = begin(title, subtitle, note)
    top = 152
    nh = (30 if caliber else 0) + len(items) * (48 if scale else 56) + 20
    y = top + max(0, ((H - (58 if note else 16) - top - nh) * 0.38))
    if caliber:
        s.append(rect(56, y - 30, W - 112, 30, PANEL, PANEL, 0, 6))
        s.append(txt(70, y - 10, '口径  ' + caliber, 13, GRAY))
    y += 14
    lw = 250
    bw_max = W - 56 - 56 - lw - 170
    for lb, v, disp, hot in items:
        col = ORANGE if hot else TEAL
        if scale:
            s.append(txt(56, y + 22, lb, 15, INK, weight='bold' if hot else 'normal'))
            s.append(rect(56 + lw, y + 6, bw_max, 24, '#F4F2ED', '#F4F2ED', 0, 6))
            s.append(rect(56 + lw, y + 6, max(6, bw_max * v / mx), 24, col, col, 0, 6))
            s.append(txt(56 + lw + bw_max + 16, y + 23, disp, 15, col, weight='bold'))
            y += 48
        else:
            s.append(rect(56, y, W - 112, 46, '#FFFFFF', LINE, 1.5, 10))
            s.append(rect(56, y, 4, 46, col, col, 0, 0))
            s.append(txt(78, y + 29, lb, 15, INK, weight='bold'))
            s.append(txt(56 + lw, y + 29, disp, 15, col, weight='bold'))
            y += 56
    return end(s)


# ---- 模板 25：验收三问卡（谁签字谁验收）----
def signcard(title, subtitle, deliverable, questions, evidence, note=None):
    s = begin(title, subtitle, note)
    hw = (W - 112 - 24) / 2
    nh = 0
    for items in (questions, evidence):
        t = 0
        for it in items:
            t += 24 + len(wrap(it, hw - 130, 14)) * 20 if items is questions \
                 else len(wrap(it, hw - 76, 14)) * 20 + 12
        nh = max(nh, t)
    bh = min(max(nh + 66, 200), 280)
    ty = max(140, 128 + ((H - (58 if note else 16) - 128 - (86 + 26 + bh)) * 0.42))
    cy = chrome(s, 56, ty, W - 112, 86, '交付物  ·  待验收')
    s.append(txt(80, cy + 20, '产物', 13, '#A8AFB8'))
    s.append(txt(130, cy + 20, deliverable, 15, '#E5E1DA', weight='bold'))
    y = ty + 86 + 26
    s.append(rect(56, y, hw, bh, '#FFFFFF', LINE, 1.5, 10))
    s.append(rect(56, y, hw, 42, ORANGE, ORANGE, 0, 10))
    s.append(txt(56 + 18, y + 28, '签字前问自己三句', 15, '#FFFFFF', weight='bold'))
    yy = y + 74
    for i, q in enumerate(questions):
        lines = wrap(q, hw - 130, 14)
        s.append(f'<circle cx="76" cy="{yy-5}" r="12" fill="{PANEL}"/>')
        s.append(txt(76, yy, str(i + 1), 13, ORANGE, 'middle', 'bold'))
        s.append(lines_block(98, yy, lines, 14, INK, 20))
        yy += 24 + len(lines) * 20
    x2 = 56 + hw + 24
    s.append(rect(x2, y, hw, bh, '#FFFFFF', LINE, 1.5, 10))
    s.append(rect(x2, y, hw, 42, TEAL, TEAL, 0, 10))
    s.append(txt(x2 + 18, y + 28, '要留的证据', 15, '#FFFFFF', weight='bold'))
    yy = y + 74
    for e in evidence:
        lines = wrap(e, hw - 76, 14)
        for j, ln in enumerate(lines):        # 勾选框用描边矩形，避免字体缺字
            if j == 0:
                s.append(f'<rect x="{x2+20}" y="{yy-11}" width="13" height="13" fill="#FFFFFF" stroke="{TEAL}" stroke-width="1.6" rx="2"/>')
        s.append(lines_block(x2 + 44, yy, lines, 14, INK, 20))
        yy += len(lines) * 20 + 12
    return end(s)
