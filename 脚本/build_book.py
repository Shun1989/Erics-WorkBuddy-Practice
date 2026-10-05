# -*- coding: utf-8 -*-
"""《WorkBuddy 实战指南》样书生成器：书稿 -> 封面/目录/章节 opener/引导页 -> HTML
   改造自《AI 工位》build_orange_book.py（已 6 次项目验证）"""
import re, os, base64, json, glob as globmod

ROOT = os.path.dirname(os.path.abspath(__file__))
BOOK = os.path.join(ROOT, '..', '书稿')
PICS = os.path.join(ROOT, '..', '配图')
OUT  = os.path.join(ROOT, '..', '成稿')
os.makedirs(OUT, exist_ok=True)

BOOK_TITLE = 'WorkBuddy 实战指南'
BOOK_SUB   = '把 AI 用进工程现场'

PARTS = {
    '第一篇': ('PART ONE', '认识 WorkBuddy'),
    '第二篇': ('PART TWO', '环境搭建与快速上手'),
    '第三篇': ('PART THREE', '核心机制深度理解'),
    '第四篇': ('PART FOUR', '72 个场景实战'),
    '第五篇': ('PART FIVE', '连接与工具扩展'),
    '第六篇': ('PART SIX', '团队落地 · 成本 · 排查'),
    '附　录': ('APPENDIX', '索引 · 术语 · 资源'),
}

def _sortkey(fname):
    """章号按数字排序，避免 '第10章' 排在 '第7章' 前面。"""
    m = re.match(r'^第\s*(\d+)\s*章', fname)
    if m:
        return (2, int(m.group(1)), fname)
    if fname.startswith('序章'):
        return (1, 0, fname)
    if fname.startswith('附录'):
        return (3, 0, fname)
    if fname.startswith('跋'):
        return (4, 0, fname)
    return (0, 0, fname)

def build_sections():
    """自动扫描书稿目录，按目录名排序生成章节清单，新增章节无需改脚本。"""
    skip_files = {'00_封面与版权.md'}
    secs = []
    for d in sorted(os.listdir(BOOK)):
        dpath = os.path.join(BOOK, d)
        if not os.path.isdir(dpath) or d.startswith('.'):
            continue
        mp = re.search(r'(第[一二三四五六]篇)', d)
        if mp:
            part = mp.group(1)
        elif '附录' in d:
            part = '附　录'
        else:
            part = None
        for f in sorted(os.listdir(dpath), key=_sortkey):
            if not f.endswith('.md') or f in skip_files or f.startswith('.'):
                continue
            rel = f'{d}/{f}'
            m = re.match(r'^第\s*(\d+)\s*章', f)
            if m:
                label = f'第 {m.group(1)} 章'
            elif f.startswith('序章'):
                label = '序章'
            elif f.startswith('跋'):
                label = '跋'
            elif f.startswith('附录'):
                label = re.sub(r'(附录\s*[A-H]).*', r'\1', f).strip().replace('录', '录 ')
            else:
                label = re.sub(r'\.md$', '', f)
                label = re.sub(r'^\d+_', '', label)
            secs.append((rel, label, part))
    return secs


SECTIONS = build_sections()

# ---------- markdown -> html（沿用已验证转换器） ----------
def slug(t):
    return re.sub(r'[^\w一-鿿]+', '-', t).strip('-') or 'sec'

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def inline(s):
    s = esc(s)
    s = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)',
               r'<figure><img src="\2" alt="\1"><figcaption>\1</figcaption></figure>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<em>\1</em>', s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    return s

def is_block_start(line):
    s = line.strip()
    if not s: return False
    if s.startswith('```'): return True
    if re.match(r'^#{1,6}\s', line): return True
    if s.startswith('>'): return True
    if re.match(r'^(\-{3,}|\*{3,}|_{3,})$', s): return True
    if '|' in line: return True
    if re.match(r'^\s*[-*]\s+', line) or re.match(r'^\s*\d+\.\s+', line): return True
    return False

def split_row(r):
    return [c.strip() for c in r.strip().strip('|').split('|')]

def render_table(rows):
    header = split_row(rows[0]); body = rows[2:]
    h = '<table><thead><tr>' + ''.join(f'<th>{inline(x)}</th>' for x in header) + '</tr></thead><tbody>'
    for r in body:
        h += '<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in split_row(r)) + '</tr>'
    return h + '</tbody></table>'

def md2html(md):
    lines = md.split('\n'); out, i, code = [], 0, []; in_code = False
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith('```'):
            if not in_code: in_code = True; code = []; i += 1; continue
            in_code = False; out.append('<pre><code>' + esc('\n'.join(code)) + '</code></pre>'); i += 1; continue
        if in_code: code.append(line); i += 1; continue
        if ('|' in line and i+1 < len(lines) and '-' in lines[i+1]
                and re.match(r'^\s*\|?[\s:|-]+\|?\s*$', lines[i+1])):
            rows = [line]; j = i+1
            while j < len(lines) and '|' in lines[j]: rows.append(lines[j]); j += 1
            out.append(render_table(rows)); i = j; continue
        if re.match(r'^(\-{3,}|\*{3,}|_{3,})$', line.strip()):
            out.append('<hr>'); i += 1; continue
        m = re.match(r'^(#{1,6})\s+(.*)$', line)
        if m:
            lvl = len(m.group(1)); txt = m.group(2).strip()
            out.append(f'<h{lvl} id="{slug(txt)}">{inline(txt)}</h{lvl}>'); i += 1; continue
        if line.lstrip().startswith('>'):
            q = []
            while i < len(lines) and lines[i].lstrip().startswith('>'):
                q.append(lines[i].lstrip()[1:].lstrip()); i += 1
            out.append('<blockquote>' + inline(' '.join(q)) + '</blockquote>'); continue
        if re.match(r'^\s*[-*]\s+', line) or re.match(r'^\s*\d+\.\s+', line):
            items = []; ordered = bool(re.match(r'^\s*\d+\.\s+', line))
            while i < len(lines) and (re.match(r'^\s*[-*]\s+', lines[i]) or re.match(r'^\s*\d+\.\s+', lines[i])):
                content = re.sub(r'^\s*([-*]|\d+\.)\s+', '', lines[i])
                items.append('<li>' + inline(content) + '</li>'); i += 1
            out.append(('<ol>' if ordered else '<ul>') + ''.join(items) + ('</ol>' if ordered else '</ul>')); continue
        if line.strip() == '': i += 1; continue
        para = [line]; i += 1
        while i < len(lines) and lines[i].strip() != '' and not is_block_start(lines[i]):
            para.append(lines[i]); i += 1
        out.append('<p>' + inline(' '.join(para)) + '</p>')
    def attach(holder, em):
        for tag in ('</p>', '</blockquote>'):
            if holder.endswith(tag):
                return holder[:-len(tag)] + '<br><em>' + em + '</em>' + tag
        return holder + '\n<p><em>' + em + '</em></p>'
    merged = []
    for el in out:
        m = re.fullmatch(r'<p><em>(（[^<>]{0,200}?）)</em></p>', el)
        if m and merged:
            prev = merged.pop()
            if prev == '<hr>' and merged:
                prev = merged.pop()
            merged.append(attach(prev, m.group(1)))
        else:
            merged.append(el)
    return '\n'.join(merged)

# ---------- 图片 base64 内联 ----------
def data_uri(path):
    ext = os.path.splitext(path)[1].lower()
    mime = {'.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg'}[ext]
    with open(path, 'rb') as f:
        return f'data:{mime};base64,' + base64.b64encode(f.read()).decode()

PLACEHOLDER = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 650" '
               'width="1000" height="650">'
               '<rect width="1000" height="650" fill="#F2EDE6"/>'
               '<rect x="24" y="24" width="952" height="602" fill="none" stroke="#D8D2C8" '
               'stroke-width="3" stroke-dasharray="12 10"/>'
               '<text x="500" y="305" font-family="Microsoft YaHei" font-size="34" '
               'fill="#9A8F80" text-anchor="middle">配图待补</text>'
               '<text x="500" y="352" font-family="Microsoft YaHei" font-size="20" '
               'fill="#B5A99A" text-anchor="middle">PLACEHOLDER</text></svg>')


def inline_images(html, chapter_dir):
    def rep(m):
        src = m.group(1)
        base = os.path.abspath(chapter_dir)
        for _ in range(5):
            real = os.path.normpath(os.path.join(base, src))
            if os.path.exists(real):
                return f'<img src="{data_uri(real)}"'
            nxt = os.path.dirname(base)
            if nxt == base:
                break
            base = nxt
        ph = 'data:image/svg+xml;base64,' + base64.b64encode(
            PLACEHOLDER.encode('utf-8')).decode()
        return f'<img src="{ph}"'
    return re.sub(r'<img src="([^"]+)"', rep, html)

def img_b64(rel):
    return data_uri(os.path.join(PICS, rel))

# ---------- 读取章节 ----------
def load_section(rel):
    chapter_dir = os.path.dirname(os.path.join(BOOK, rel))
    t = open(os.path.join(BOOK, rel), encoding='utf-8').read()
    m = re.search(r'^#\s+(.*)$', t, re.M)
    title = m.group(1).strip() if m else rel
    body = re.sub(r'^#\s+.*$', '', t, count=1, flags=re.M)
    html = inline_images(md2html(body), chapter_dir)
    return title, html

def clean_title(label, title):
    t = re.sub(r'^第\s*\d+\s*章[ _·:：\-]*', '', title).strip()
    t = re.sub(r'^(序章|跋|附录\s*[A-H]|别册)[ _·:：\-]*', '', t).strip()
    return t or title

# ---------- 组装 ----------
css = """
<style>
* { box-sizing: border-box; }
@page { size: A4; margin: 20mm 18mm 22mm 18mm;
  @top-center { content: "WorkBuddy 实战指南"; font-size:8.5pt; color:#9aa0a8;
    font-family:"Microsoft YaHei","PingFang SC",sans-serif; letter-spacing:.3em; }
  @bottom-center { content: "· " counter(page) " ·"; font-size:9pt; color:#8a8f98;
    font-family:"Microsoft YaHei",sans-serif; } }
@page cover { margin: 0; @top-center { content: none; } @bottom-center { content: none; } }
@page part { margin: 0; @top-center { content: none; } @bottom-center { content: none; } }
@page chapter { @top-center { content: none; } }
@page frontmatter { @top-center { content: none; } }
html { string-set: chap "WorkBuddy 实战指南"; }
html,body { margin:0; padding:0; }
body { font-family:"Source Han Serif SC","Noto Serif SC","Noto Serif CJK SC","SimSun",serif;
  color:#242a33; font-size:10.5pt; line-height:1.8; orphans:3; widows:3; }
/* 封面 */
.cover-page { page: cover; width:210mm; height:296.5mm;
  background: linear-gradient(150deg,#0f2e1d 0%,#14532d 48%,#0d47a1 130%);
  color:#fff; padding:26mm 22mm; position:relative; page-break-after:always;
  font-family:"Microsoft YaHei","PingFang SC","Noto Sans SC",sans-serif; }
.cover-badge { display:inline-block; background:#e67e22; color:#fff; font-weight:800;
  letter-spacing:.35em; padding:8px 20px 8px 24px; border-radius:4px; font-size:11pt; }
.cover-title { font-size:40pt; font-weight:900; margin:30mm 0 4mm; letter-spacing:.02em; }
.cover-title .en { display:block; font-size:26pt; letter-spacing:.04em; color:#cfe3d6; margin-bottom:5mm; font-weight:800; }
.cover-sub { font-size:18pt; color:#cfe3d6; font-weight:400; }
.cover-author { position:absolute; bottom:34mm; left:22mm; font-size:12pt; color:#e8f2ec; }
.cover-meta { position:absolute; bottom:20mm; left:22mm; font-size:9pt; color:#9fc4ad; letter-spacing:.2em; }
.cover-line { width:52mm; height:5px; background:#e67e22; margin-top:10mm; }
.cover-note { position:absolute; bottom:20mm; right:22mm; font-size:9pt; color:#9fc4ad; }
/* 目录 */
.toc-page { page: frontmatter; page-break-after:always; padding-top:8mm;
  font-family:"Microsoft YaHei","PingFang SC","Noto Sans SC",sans-serif; }
.toc-page h1 { font-size:22pt; color:#14532d; border-bottom:3px solid #e67e22; padding-bottom:6px; }
.toc ul { list-style:none; padding:0; margin:0; }
.toc li { margin:2.4mm 0; font-size:10.5pt; }
.toc li.part { font-weight:800; color:#e67e22; margin-top:6mm; font-size:12pt; }
.toc li.part ul { margin-top:1mm; }
.toc li a { color:#242a33; text-decoration:none; display:block; overflow:hidden;
  border-bottom:1px dotted #ddd6cb; padding-bottom:1mm; }
.toc li a .pg { float:right; color:#14532d; font-weight:700; }
/* 分部扉页 */
.part-page { page: part; width:210mm; height:296.5mm; page-break-after:always;
  background: linear-gradient(160deg,#14532d,#0f2e1d); color:#fff; padding:60mm 24mm; position:relative;
  font-family:"Microsoft YaHei","PingFang SC","Noto Sans SC",sans-serif; }
.part-num { font-size:15pt; letter-spacing:.5em; color:#e67e22; font-weight:800; }
.part-name { font-size:38pt; font-weight:900; margin-top:8mm; }
.part-sub { font-size:14pt; color:#cfe3d6; margin-top:6mm; }
.part-line { width:40mm; height:4px; background:#e67e22; margin-top:12mm; }
/* 章节 opener */
.chapter-opener { page-break-before:always; padding:12mm 0 7mm;
  border-bottom:2px solid #eef0f4; margin-bottom:7mm;
  font-family:"Microsoft YaHei","PingFang SC","Noto Sans SC",sans-serif; }
.ch-label { font-size:12pt; letter-spacing:.35em; color:#4a90d9; font-weight:800; }
.ch-title { font-size:24pt; font-weight:900; color:#e67e22; margin-top:3mm; line-height:1.3;
  string-set: chap content(); }
.chapter-opener + p { text-indent:0; }
h1,h2,h3,h4 { font-family:"Microsoft YaHei","PingFang SC","Noto Sans SC",sans-serif;
  page-break-after:avoid; orphans:3; widows:3; }
h1 { font-size:17pt; color:#14532d; margin:1.6em 0 .7em; }
h2 { font-size:14pt; color:#0d47a1; margin:1.5em 0 .6em;
  border-left:5px solid #e67e22; padding-left:10px; }
h3 { font-size:12pt; color:#14532d; margin:1.3em 0 .5em; }
h4 { font-size:11pt; color:#333; margin:1.2em 0 .4em; }
p { margin:0; text-indent:2em; text-align:justify; }
h1 + p, h2 + p, h3 + p, h4 + p,
figure + p, blockquote + p, pre + p, table + p,
ul + p, ol + p, hr + p { text-indent:0; }
a { color:#0d47a1; text-decoration:none; }
blockquote { margin:1em 0; padding:.55em 1.1em; background:#fdf6ee;
  border-left:4px solid #e67e22; color:#4a4038; page-break-inside:avoid; line-height:1.75; }
code { background:#f2ede6; padding:.1em .35em; border-radius:4px;
  font-family:Consolas,"JetBrains Mono",monospace; font-size:9pt; }
pre { background:#f6f4f0; color:#2d2a26; border:1px solid #e3ded6; border-radius:6px;
  padding:10px 13px; font-family:Consolas,"JetBrains Mono",monospace; font-size:8.5pt;
  line-height:1.65; overflow:hidden; page-break-inside:avoid;
  white-space:pre-wrap; word-break:break-all; }
pre code { background:none; color:inherit; padding:0; }
ul,ol { padding-left:1.8em; margin:.7em 0; }
li { margin:.22em 0; }
table { border-collapse:collapse; width:100%; margin:1em 0; font-size:9pt; }
thead { display:table-header-group; }
tr { page-break-inside:avoid; }
th,td { border:1px solid #d9d4cb; padding:5px 7px; text-align:left; vertical-align:top; line-height:1.65; }
th { background:#f2ede6; font-weight:700;
  font-family:"Microsoft YaHei","PingFang SC",sans-serif; }
figure { margin:1.3em auto; text-align:center; page-break-inside:avoid; }
figure img { max-width:100%; max-height:148mm; height:auto; border:1px solid #e5e1da; border-radius:6px; }
figcaption { font-size:8.5pt; color:#6b7280; margin-top:.5em;
  font-family:"Microsoft YaHei","PingFang SC",sans-serif; }
hr { border:none; width:38%; margin:1.8em auto; border-top:1px solid #d8d2c8; }
/* 引导页 */
.guide-page { page: chapter; page-break-before:always; padding-top:20mm; text-align:center;
  font-family:"Microsoft YaHei","PingFang SC","Noto Sans SC",sans-serif; }
.guide-page h1 { color:#14532d; font-size:20pt; }
.guide-cards { display:flex; justify-content:center; gap:10mm; margin-top:12mm; flex-wrap:wrap; }
.guide-card { width:58mm; border:1px solid #e5e1da; border-radius:10px; padding:6mm 4mm; }
.guide-card img { width:44mm; height:auto; }
.guide-card .t { font-weight:800; color:#e67e22; margin-top:3mm; font-size:10.5pt; }
.guide-card .d { font-size:8.5pt; color:#6b7280; margin-top:1.5mm; line-height:1.6; }
.guide-note { margin-top:14mm; font-size:9pt; color:#6b7280; line-height:2; }
.author-photo { width:52mm; border-radius:8px; }
</style>
"""

def cover():
    return f"""
<div class="cover-page">
  <div class="cover-badge">全稿 · 征求意见稿</div>
  <div class="cover-title"><span class="en">WorkBuddy</span>实战指南</div>
  <div class="cover-sub">{BOOK_SUB}</div>
  <div class="cover-line"></div>
  <div class="cover-author">Eric &nbsp;著</div>
  <div class="cover-meta">汽车微电机与智能执行器研发工程师 · 11 年一线实战 · 2026</div>
  <div class="cover-note">6 篇 23 章 · 72 个场景 · 附索引术语表与随书资源</div>
</div>"""

def toc(entries, pagemap=None):
    pagemap = pagemap or {}
    out = ['<div class="toc-page"><h1>目 录</h1><ul class="toc">']
    for kind, text_, anchor in entries:
        if kind == 'part':
            out.append(f'<li class="part">{text_}<ul>')
        elif kind == 'partend':
            out.append('</ul></li>')
        else:
            pg = pagemap.get(anchor)
            num = f'<span class="pg">{pg}</span>' if pg else ''
            out.append(f'<li><a href="#{anchor}">{text_}{num}</a></li>')
    out.append('</ul></div>')
    return '\n'.join(out)

def part_page(part):
    en, sub = PARTS[part]
    return f"""
<div class="part-page">
  <div class="part-num">{en} · {part}</div>
  <div class="part-name">{sub}</div>
  <div class="part-line"></div>
</div>"""

def opener(idx, label, title):
    return f"""
<div class="chapter-opener" id="sec-{idx}">
  <div class="ch-label">{label}</div>
  <div class="ch-title">{title}</div>
</div>"""

def guide():
    gzh = img_b64('png/公众号二维码.jpg')
    gh  = img_b64('png/GitHub开源仓库二维码.png')
    return f"""
<div class="guide-page">
  <h1>找到作者，拿到随书资产</h1>
  <p style="color:#6b7280">这本书没写完的部分，都在下面这几个地方持续更新。</p>
  <div class="guide-cards">
    <div class="guide-card"><img src="{gzh}"><div class="t">公众号「Eric的数字花园」</div>
      <div class="d">回复「实战」，领 72 个场景提示词合集与脱敏练习素材包</div></div>
    <div class="guide-card"><img src="{gh}"><div class="t">GitHub 开源仓库</div>
      <div class="d">github.com/Shun1989/Erics-WorkBuddy-Practice<br>全部模板/技能/SVG 源文件，MIT 协议</div></div>
    <div class="guide-card" style="padding-top:16mm"><div class="t">汽研 Agent 中文社区</div>
      <div class="d" style="padding-top:6mm">qiyanagent.org.cn<br>汽车与制造行业的 AI 应用者社区<br>每天整理行业动态与真实用法</div></div>
  </div>
  <div class="guide-note">
    © 2026 Eric · 本书为作者一线实战记录 · 欢迎转发，转载请注明出处
  </div>
</div>"""

def main():
    toc_entries = []
    body_parts = []
    cur_part = None
    idx = 0
    for rel, label, part in SECTIONS:
        title, html = load_section(rel)
        disp = clean_title(label, title)
        if part and part != cur_part:
            if cur_part is not None:
                toc_entries.append(('partend', '', ''))
            cur_part = part
            en, sub = PARTS[part]
            body_parts.append(part_page(part))
            toc_entries.append(('part', f'{part} · {sub}', ''))
        idx += 1
        disp_txt = label if disp == label else f'{label}　{disp}'
        toc_entries.append(('ch', disp_txt, f'sec-{idx}'))
        body_parts.append(opener(idx, label, disp))
        body_parts.append(html)
    toc_entries.append(('partend', '', ''))

    pm_path = os.path.join(OUT, 'toc_pages.json')
    pagemap = {}
    if os.path.exists(pm_path):
        pagemap = json.load(open(pm_path, encoding='utf-8'))
        print('toc pagemap loaded:', len(pagemap), 'entries')

    full = ['<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">',
            f'<title>{BOOK_TITLE} · {BOOK_SUB}</title>', css, '</head><body>',
            cover(), toc(toc_entries, pagemap)] + body_parts + [guide(), '</body></html>']
    html_path = os.path.join(OUT, 'WorkBuddy实战指南.html')
    open(html_path, 'w', encoding='utf-8').write('\n'.join(full))
    print('html:', html_path, round(os.path.getsize(html_path)/1024/1024, 2), 'MB')

if __name__ == '__main__':
    main()
