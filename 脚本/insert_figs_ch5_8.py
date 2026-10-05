# -*- coding: utf-8 -*-
"""把第 5 到第 8 章新增的 33 张配图插入书稿 md。

每张图插在它所描述的那段文字之后，格式按《配图补齐规范》：
  ![图 X-Y 图题](../../配图/svg/fig-X-Y-xxx.svg)
  空行
  *作者根据公开资料绘制*
"""
import os, sys

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
CAP = '*作者根据公开资料绘制*'


def block(fig_no, title, slug):
    return ('![图 %s %s](../../配图/svg/%s.svg)\n\n%s\n' % (fig_no, title, slug, CAP))


JOBS = []


def job(path, anchor, fig_no, title, slug, before=False):
    JOBS.append((path, anchor, block(fig_no, title, slug), before))


CH5 = '书稿/04_第三篇_核心机制/第5章_让它记住你和你的项目.md'
CH6 = '书稿/04_第三篇_核心机制/第6章_一个干不完就拆开分给几个.md'
CH7 = '书稿/05_第四篇_场景实战/第7章_通用办公自动化.md'
CH8 = '书稿/05_第四篇_场景实战/第8章_个人效率与知识管理.md'

# ---------------- 第 5 章 ----------------
job(CH5,
    '它的回复应当长这样：',
    '5-6', '写法一的提示词原文：说三条规矩，最后一句是复述指令',
    'fig-5-6-remember-three-things', before=True)

job(CH5,
    '复述这一句"现在把上面三条复述一遍"不能省。',
    '5-7', '写法一的复述回复：它回什么，你才判断写没写进去',
    'fig-5-7-recite-back', before=True)

job(CH5,
    '这份清单的价值在于你一眼能看出它归纳错了什么。',
    '5-8', '写法二的产出是一张带归属标记的清单，你只管划掉划留',
    'fig-5-8-memory-list', before=True)

job(CH5,
    '为什么要"回显"和"不要覆盖"这两句，',
    '5-9', '写法三追加进记忆文件的项目背景节原文',
    'fig-5-9-project-memory-section', before=True)

job(CH5,
    '这一页我写完用了大概十分钟。',
    '5-10', '第一步写好的项目背景卡：十分钟，九项',
    'fig-5-10-project-card', before=True)

job(CH5,
    '三个全对，这个项目的背景才算交代完了。',
    '5-11', '第四步的验收卡：新开对话问三题，答案要标注来自哪一层记忆',
    'fig-5-11-verify-three-questions', before=True)

job(CH5,
    '> 【待补：记忆的查看与编辑入口',
    '5-12', '同一条规矩写进工作区还是提到用户级，结果差得很远',
    'fig-5-12-rule-layer-fix', before=True)

# ---------------- 第 6 章 ----------------
job(CH6,
    '第一句给它岗位，限制它用什么眼光看。',
    '6-5', '按文件拆的委派提示词：七个部分，一个都不能少',
    'fig-6-5-delegate-by-file', before=True)

job(CH6,
    '按角色拆时，最有用的句子往往是"不在你的范围"。',
    '6-6', '按角色拆的委派提示词：最有用的一句是「不在你的范围」',
    'fig-6-6-delegate-by-role', before=True)

job(CH6,
    '我验这一站时不会从头重读 200 页，',
    '6-7', '两个子代理的输出表头必须一模一样，ID 前缀不同',
    'fig-6-7-extract-table-shape', before=True)

job(CH6,
    '### 第 1 步：两个子代理分段提取要求',
    '6-8', '一次多代理任务在窗口里长什么样',
    'fig-6-8-multi-agent-panel', before=True)

job(CH6,
    '接着我让主代理只做计划，不急着读正文：',
    '6-11', '第 0 步的验收单：先把总任务写成五条可判定的条件',
    'fig-6-11-acceptance-ticket', before=True)

job(CH6,
    '它交回来的汇报稿只有六部分，没有追求花哨。',
    '6-9', '汇报子代理的产出：固定六个部分，数量从表里统计',
    'fig-6-9-brief-six-sections', before=True)

job(CH6,
    '这个演示里，主代理始终做三件事：发任务、验中间件、组装成品。',
    '6-10', '主代理合并前要过的四道门',
    'fig-6-10-four-gates', before=True)

job(CH6,
    '通过后才把文件交给下一个子代理。',
    '6-12', '合并前的验收顺序：看回报、查文件、抽来源、验边界',
    'fig-6-12-verify-order', before=True)

# ---------------- 第 7 章 ----------------
job(CH7,
    '### 6. 过程与判断点\n\n它会先给你一份方案（Plan 模式）',
    '7-8', '场景 01 提示词：四部分输出，四条硬性约束',
    'fig-7-8-meeting-prompt', before=True)

job(CH7,
    '**听不清标记数**：录音质量一般的话',
    '7-10', '场景 01 的三个数对得上才算过',
    'fig-7-10-meeting-three-numbers', before=True)

job(CH7,
    '### 7. 翻车清单\n\n**翻车点一：人名被听成同音字。**',
    '7-9', '场景 01 产物：一个 Markdown 文件，四部分齐全',
    'fig-7-9-meeting-output', before=True)

job(CH7,
    '![图 7-3 一份模板出四个版本',
    '7-11', '变量的粒度：日期和钟点拆成两个变量，四个版本就一致了',
    'fig-7-11-variable-granularity', before=True)

job(CH7,
    '### 6. 过程与判断点\n\n体检报告是这一步最值钱的东西。',
    '7-12', '场景 03 第一步的体检清单：七类问题逐项报处数',
    'fig-7-12-excel-checkup', before=True)

job(CH7,
    '### 7. 翻车清单\n\n**翻车点一：它改了你的原始数值。**',
    '7-13', '场景 03 清洗前后：同一个零件号原来有四种写法',
    'fig-7-13-excel-before-after', before=True)

job(CH7,
    '### 6. 过程与判断点\n\nPlan 阶段的价值在于：',
    '7-14', '场景 04 提示词：先读模板出清单，再按清单套内容',
    'fig-7-14-word-prompt', before=True)

job(CH7,
    '### 6. 过程与判断点\n\nPlan 阶段的页面规划表是这套流程的核心',
    '7-15', '场景 05 第一步的页面规划表：这一步你一定要改',
    'fig-7-15-ppt-page-plan', before=True)

job(CH7,
    '我统计过自己的收件：一周 200 封上下',
    '7-16', '场景 06 产物：按类别分节的草稿文件，只写草稿不发送',
    'fig-7-16-email-drafts', before=True)

# ---------------- 第 8 章 ----------------
job(CH8,
    '### 操作步骤\n\n**步骤 1：先只搬一个来源。**',
    '8-8', '个人知识库的目录结构：三个来源分开，卡片与总目录各归其位',
    'fig-8-8-library-tree', before=True)

job(CH8,
    '步骤 5 用的提问提示词：',
    '8-9', '每个文件一张身份证卡片，四栏固定，缺哪栏写未知',
    'fig-8-9-index-card', before=True)

job(CH8,
    '### 过程与判断点\n\n跑完步骤 2，',
    '8-10', '场景 07 步骤 5 的提问提示词：没出处的结论一律不算数',
    'fig-8-10-ask-with-source', before=True)

job(CH8,
    '步骤 3 的卡片，判断点是**卡片数必须等于处理数**。',
    '8-11', '步骤 2 的盘点结果：3182 个文件里，231 个它读不了',
    'fig-8-11-inventory-table', before=True)

job(CH8,
    '改写阶段，判断点是**判定标准能不能判**。',
    '8-12', '场景 08 的条数对账：原文 63 条，清单第一次只报上来 58 条',
    'fig-8-12-clause-count', before=True)

job(CH8,
    '**步骤 4：标强制与推荐。**',
    '8-13', '场景 08 步骤 3：把「要做到 A」改写成「怎么确认做到了 A」',
    'fig-8-13-clause-to-action', before=True)

job(CH8,
    '### 过程与判断点\n\n我第一次跑这套，输入 23 条',
    '8-14', '场景 09 步骤 5：按会议空档填，一次只排到容量的七成',
    'fig-8-14-day-schedule', before=True)

job(CH8,
    '从那以后我给自己定了条规矩：清单里出现"跟进""推进""优化""配合"',
    '8-15', '场景 09：出现这四个词，说明这条你还没想清楚',
    'fig-8-15-verb-rewrite', before=True)

job(CH8,
    '### 过程与判断点\n\n我连续用了 14 周',
    '8-16', '场景 10 的周报模板加一张数字自查对照表',
    'fig-8-16-weekly-report', before=True)


def run():
    byfile = {}
    for p, a, b, before in JOBS:
        byfile.setdefault(p, []).append((a, b, before))
    ok = 0
    for path, items in byfile.items():
        full = os.path.join(BASE, path)
        s = open(full, encoding='utf-8').read()
        for anchor, blk, before in items:
            i = s.find(anchor)
            if i < 0:
                print('ANCHOR MISS  %s  <<%s>>' % (path, anchor[:30]))
                continue
            if before:
                s = s[:i] + blk + '\n' + s[i:]
            else:
                j = i + len(anchor)
                s = s[:j] + '\n\n' + blk + s[j:]
            ok += 1
        open(full, 'w', encoding='utf-8').write(s)
        print('updated %s  (%d figures)' % (path, len(items)))
    print('inserted %d / %d' % (ok, len(JOBS)))


if __name__ == '__main__':
    run()
