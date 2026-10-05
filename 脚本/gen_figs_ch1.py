# -*- coding: utf-8 -*-
"""第 1 章配图生成：三张 SVG，画布 1000x650，配色按书稿规范"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '配图', 'svg')
os.makedirs(OUT, exist_ok=True)

BG, FG, SUB, ORG, TEAL, LINE, LIGHT, WARN = ('#FAFAF8', '#1C2026', '#6B7280',
                                             '#E0632D', '#2D6A6A', '#E5E1DA', '#F2EDE6', '#B03A2E')
FONT = 'Microsoft YaHei'


def text(x, y, s, size=16, fill=FG, weight='normal', anchor='start'):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{s}</text>')


def rect(x, y, w, h, fill='#fff', stroke=LINE, rx=10, sw=1.5):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}" rx="{rx}"/>')


def line(x1, y1, x2, y2, stroke=LINE, sw=1.5, dash=''):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def arrow(x1, y1, x2, y2, stroke=SUB, sw=2):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}" '
            f'marker-end="url(#arr)"/>')


def wrap(s, n):
    return [s[i:i + n] for i in range(0, len(s), n)]


DEFS = ('<defs><marker id="arr" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">'
        '<path d="M0,0 L8,4 L0,8 Z" fill="#6B7280"/></marker></defs>')


def svg(body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 650" '
            f'width="1000" height="650" style="background:{BG}">{DEFS}'
            f'<rect width="1000" height="650" fill="{BG}"/>' + body + '</svg>')


# ---------- 图 1-1 三种模式决策树 ----------
def fig_mode_tree():
    b = [text(500, 46, '三种模式怎么选', 26, FG, '800', 'middle'),
         text(500, 74, '先问任务明不明确，再看出错代价大不大', 15, SUB, anchor='middle')]
    b.append(rect(390, 100, 220, 52, ORG, ORG, 26))
    b.append(text(500, 133, '我有一件活', 19, '#fff', '800', 'middle'))
    # 分支1：说明白了吗
    b.append(line(500, 152, 500, 172, SUB, 2))
    b.append(rect(330, 178, 340, 52, LIGHT, LINE, 26))
    b.append(text(500, 211, '我能把活说清楚吗', 18, FG, '700', 'middle'))
    # 左右分支
    b.append(line(400, 230, 200, 280, SUB, 2))
    b.append(line(600, 230, 800, 280, SUB, 2))
    b.append(text(255, 258, '说不清', 14, SUB, anchor='middle'))
    b.append(text(745, 258, '说得清', 14, SUB, anchor='middle'))
    # 左：Plan
    b.append(rect(70, 286, 260, 84, '#fff', TEAL, 12, 2.5))
    b.append(text(200, 322, 'Plan · 先谋后动', 20, TEAL, '800', 'middle'))
    b.append(text(200, 350, '它出完整方案，你点头才动手', 14, SUB, anchor='middle'))
    b.append(rect(70, 386, 260, 170, '#fff', LINE))
    for i, s in enumerate(['方向还没想清楚的活', '第一次做、心里没底的活', '要花很多钱的活', '改方案比返工便宜的活']):
        b.append(text(90, 414 + i * 34, '· ' + s, 15, FG))
    # 右：Agent / Ask
    b.append(rect(670, 286, 260, 60, '#fff', ORG, 12, 2.5))
    b.append(text(800, 324, 'Agent · 直接干', 20, ORG, '800', 'middle'))
    b.append(line(800, 346, 800, 366, SUB, 2))
    b.append(text(800, 388, '活得足够清楚吗？', 15, FG, '700', 'middle'))
    b.append(line(730, 398, 680, 420, SUB, 1.5))
    b.append(line(870, 398, 920, 420, SUB, 1.5))
    b.append(rect(560, 424, 190, 60, '#fff', LINE))
    b.append(text(655, 450, 'Ask · 只问不干', 16, FG, '700', 'middle'))
    b.append(text(655, 472, '先聊聊，纯问答', 12.5, SUB, anchor='middle'))
    b.append(rect(770, 424, 190, 60, '#fff', ORG, 10, 2))
    b.append(text(865, 450, 'Agent · 交活', 16, ORG, '700', 'middle'))
    b.append(text(865, 472, '干完向你交差', 12.5, SUB, anchor='middle'))
    # 底部口诀
    b.append(rect(150, 556, 700, 56, LIGHT, LINE, 12))
    b.append(text(500, 591, '口诀：拿不准就用 Plan，活得清楚就上 Agent，纯聊天就用 Ask', 17, ORG, '800', 'middle'))
    return svg('\n'.join(b))


# ---------- 图 1-2 门槛对比 ----------
def fig_threshold():
    b = [text(500, 46, '同样的能力，不同的门槛', 26, FG, '800', 'middle'),
         text(500, 74, '命令行 Agent：每一步都要你跨过去；WorkBuddy：门是开着的', 15, SUB, anchor='middle')]
    cols = [
        (60, '命令行 Agent', SUB, [
            ('装运行环境', '英文报错自己查'), ('学指令格式', '路径、参数、语法'),
            ('记命令', '忘了就翻文档'), ('看日志排错', '报错以英文为主'),
            ('干完自己翻文件', '静悄悄，无交差汇报')]),
        (560, 'WorkBuddy', ORG, [
            ('安装包下一步', '装完即用'), ('说中文交活', '像给同事交代工作'),
            ('拖文件进去', '不用记任何路径'), ('它先自查', '解决不了用中文告诉你'),
            ('干完主动交差', '改了什么、哪里拿不准')]),
    ]
    for x, title, color, rows in cols:
        b.append(rect(x, 100, 380, 60, color if color == ORG else '#fff', color, 12, 2.5))
        b.append(text(x + 190, 138, title, 21, '#fff' if color == ORG else FG, '800', 'middle'))
        for i, (t1, t2) in enumerate(rows):
            y = 180 + i * 78
            b.append(rect(x, y, 380, 66, '#fff', LINE))
            b.append(text(x + 22, y + 28, f'{i + 1}. {t1}', 16, FG, '700'))
            b.append(text(x + 22, y + 52, t2, 13.5, SUB))
    # 中间箭头
    b.append(arrow(455, 320, 545, 320, ORG, 3))
    b.append(text(500, 300, '同级别的干活能力', 13, SUB, anchor='middle'))
    # 底部结论
    b.append(rect(150, 584, 700, 44, LIGHT, LINE, 10))
    b.append(text(500, 612, '能力相近时，门槛决定你用不用得起：工程现场的人，选门开着的那个', 15, FG, '700', 'middle'))
    return svg('\n'.join(b))


# ---------- 图 1-3 全书地图 ----------
def fig_book_map():
    b = [text(500, 46, '全书地图：六篇 23 章 72 个场景', 26, FG, '800', 'middle'),
         text(500, 74, '抄作业直达第 4 篇，系统学习按顺序读，当工具书查附录', 15, SUB, anchor='middle')]
    parts = [
        ('第一篇', '认识 WorkBuddy', '第 1 章', '是什么、差在哪', TEAL, '先读，建立认知'),
        ('第二篇', '环境搭建', '第 2-3 章', '下载安装到跑通第一件活', TEAL, '跟着做，半天见效'),
        ('第三篇', '核心机制', '第 4-6 章', '技能 / 记忆 / 子代理', TEAL, '懂原理，不背术语'),
        ('第四篇', '72 个场景实战', '第 7-18 章', '抄作业级 · 本书大本营', ORG, '72 场景 · 八件套 · 三级标注'),
        ('第五篇', '连接与扩展', '第 19-20 章', '连接器 / MCP', TEAL, '把 AI 接上你的软件'),
        ('第六篇', '团队落地', '第 21-23 章', '成本 / 排查 / 定责', TEAL, '写给带团队的人'),
    ]
    # 2 行 3 列
    for idx, (num, name, ch, desc, color, tail) in enumerate(parts):
        col, row = idx % 3, idx // 3
        x = 45 + col * 315
        y = 105 + row * 200
        hot = color == ORG
        b.append(rect(x, y, 285, 170, '#fff' if not hot else '#FDF3EC', ORG if hot else LINE,
                      14, 2.5 if hot else 1.5))
        b.append(rect(x, y, 285, 46, ORG if hot else TEAL, ORG if hot else TEAL, 14))
        b.append(rect(x, y + 32, 285, 14, ORG if hot else TEAL, ORG if hot else TEAL, 0))
        b.append(text(x + 16, y + 30, f'{num} · {ch}', 15.5, '#fff', '700'))
        b.append(text(x + 16, y + 88, name, 21, FG, '800'))
        b.append(text(x + 16, y + 122, desc, 14, SUB))
        b.append(text(x + 16, y + 152, tail, 13, ORG if hot else SUB, '700' if hot else 'normal'))
    # 底部三路线
    routes = [('路线一 · 直接抄', '翻到第 4 篇，按场景抄提示词'),
              ('路线二 · 顺序读', '三周成为团队里"什么都能搞定的人"'),
              ('路线三 · 工具书', '放在桌面，忘了就翻回去查')]
    b.append(text(500, 532, '三种读法', 16, FG, '800', 'middle'))
    for i, (t1, t2) in enumerate(routes):
        x = 45 + i * 315
        b.append(rect(x, 548, 285, 62, LIGHT, LINE, 10))
        b.append(text(x + 142, 574, t1, 15, ORG, '700', 'middle'))
        b.append(text(x + 142, 598, t2, 12.5, SUB, anchor='middle'))
    return svg('\n'.join(b))


if __name__ == '__main__':
    for name, fn in [('fig-1-1-mode-tree.svg', fig_mode_tree),
                     ('fig-1-2-threshold-compare.svg', fig_threshold),
                     ('fig-1-3-book-map.svg', fig_book_map)]:
        p = os.path.join(OUT, name)
        open(p, 'w', encoding='utf-8').write(fn())
        print('ok:', p, os.path.getsize(p), 'bytes')
