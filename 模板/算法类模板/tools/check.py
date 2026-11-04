# -*- coding: utf-8 -*-
"""算法类单节结构自检。

用法:
    python tools/check.py              # 检查 curriculum.py 里列出的全部节
    python tools/check.py 01.html      # 只查指定页

检查的是「算法教程的写法」：
  · 一节要有完整闭环：推导卡（问题 → 2~4 步尝试 → 落定理）→ 算法落地卡（题目身份 / 题面 / 样例
    → 3~5 个拆步，每步代码 + 为什么，最后一步保留完整程序 → 竞赛用法）→ 易错 → 数学补给
    → 举一反三（每题带折叠解析）→ 自己动手复现 → 挑战题（提示 → 思路 → 题解）；
  · 至少要有一张代码逻辑图（figure.dia 的竖排流程，或 figure.fig 里的 SVG 流程图）；
  · 代码块里的 < & 必须转义，否则浏览器会把它当标签；
  · 右侧本节目录的 data-t 必须都能在页面上找到对应 id（构建立刻能验出来的常见错）。

旧的 .prob（例题区）/ .fn（新函数拆解卡）/ .step（逐行拆解）已被 .walk / .derive 取代，
本脚本只按新写法检查（.step 那条放宽成 .step 或 .walk-step）。
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curriculum as C  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
MIN_CN = 900
MIN_THINK = 3
MIN_RTOC = 3


def strip_tags(h):
    return re.sub(r"<[^>]+>", " ", h)


def div_spans(h, cls):
    """返回 class 恰含 cls 的 <div>/<figure> 片段（按同层嵌套配平）。"""
    out = []
    tag_re = r'<(div|figure) class="%s"[^>]*>' % cls
    for m in re.finditer(tag_re, h):
        tag = m.group(1)
        i = m.end()
        depth = 1
        pat = r"<div\b|</div>|<figure\b|</figure>" if tag == "figure" else r"<div\b|</div>"
        for t in re.finditer(pat, h[i:]):
            opens = t.group(0).startswith("<")
            closes = t.group(0).startswith("</")
            opens_tag = t.group(0).startswith("<" + tag)
            closes_tag = t.group(0).startswith("</" + tag)
            if opens_tag:
                depth += 1
            elif closes_tag:
                depth -= 1
            if depth == 0:
                out.append((m.start(), i + t.end(), h[i:i + t.start()]))
                break
    return out


def check(path):
    errs, warns = [], []
    if not os.path.exists(path):
        return ["文件不存在: %s" % path], []
    h = open(path, encoding="utf-8").read()
    name = os.path.basename(path)

    m = re.match(r"(\d+)\.html$", name)
    num = None
    if not m:
        errs.append("文件名应为两位节号：01.html")
    else:
        num = int(m.group(1))
        it = C.item_by_id(num)
        if it is None:
            errs.append("curriculum.py 里没有第 %d 节" % num)
        elif it["title"] not in h:
            warns.append("页面里找不到 curriculum.py 里的标题「%s」" % it["title"])

    # ---- 文档骨架
    for need, tip in (('charset="utf-8"', "缺 charset"),
                      ('name="viewport"', "缺 viewport"),
                      ('href="assets/style.css"', "缺样式表"),
                      ('<div class="topbar">', "缺顶栏 .topbar"),
                      ('<div class="wrap">', "缺 .wrap 容器"),
                      ('<div class="nav">', "缺页脚翻页 .nav"),
                      ("<footer>", "缺 <footer>")):
        if need not in h:
            errs.append("缺%s" % tip)
    if num is not None:
        if 'data-lesson="%d"' % num not in h:
            errs.append('body 上应为 data-lesson="%d"' % num)
        if "<title>%02d · " % num not in h:
            errs.append("<title> 应以「%02d · 」开头" % num)
        h1 = re.search(r"<h1>(.*?)</h1>", h, re.S)
        if not h1:
            errs.append("缺 <h1>")
        elif not strip_tags(h1.group(1)).strip().startswith("%02d" % num):
            errs.append("<h1> 应以「%02d · 标题」开头" % num)
        total = sum(len(g["items"]) for g in C.GROUPS)
        if "第 %d / %d 节" % (num, total) not in h:
            warns.append("顶栏建议写「第 %d / %d 节」（本课程共 %d 节，改章节表后别忘了回来改）"
                         % (num, total, total))
        nav = re.search(r'<div class="nav">(.*?)</div>', h, re.S)
        if nav:
            body = nav.group(1)
            if num > 1 and ('href="%02d.html"' % (num - 1)) not in body:
                errs.append('翻页区缺「上一节」链接：<a href="%02d.html">' % (num - 1))
            if num < total and ('href="%02d.html"' % (num + 1)) not in body:
                errs.append('翻页区缺「下一节」链接：<a href="%02d.html">' % (num + 1))

    # ---- 节头
    sub = re.search(r'<div class="sub">(.*?)</div>', h, re.S)
    if not sub or len(strip_tags(sub.group(1)).strip()) < 15:
        errs.append('缺 <div class="sub"> 本节提要（右侧本节目录的概述取它）')
    meta = re.search(r'<div class="meta">(.*?)</div>', h, re.S)
    if not meta:
        errs.append('缺 <div class="meta"> 元信息')
    elif "badge diff" not in meta.group(1):
        warns.append(".meta 里建议放一个 <span class=\"badge diff\">难度</span>")

    # ---- 教学闭环：推导卡 + 算法落地卡
    if not re.search(r'<div class="derive"[^>]*>', h):
        errs.append("缺推导卡 .derive")
    for i, d in enumerate(div_spans(h, "derive"), 1):
        inner = d[2]
        if 'class="derive-h"' not in inner:
            errs.append("推导卡 %d 缺 .derive-h 标题" % i)
        elif 'class="dk"' not in inner:
            errs.append("推导卡 %d 标题缺 .dk 标签" % i)
        if 'class="derive-q"' not in inner:
            errs.append("推导卡 %d 缺 .derive-q（先写「遇到什么困难」）" % i)
        n = len(re.findall(r'<div class="dstep"', inner))
        if not 2 <= n <= 4:
            errs.append("推导卡 %d 的 .dstep 应为 2~4 步，实际 %d 步" % (i, n))
        if 'class="derive-end"' not in inner:
            errs.append("推导卡 %d 缺 .derive-end（落定理）" % i)

    if not re.search(r'<div class="walk"[^>]*>', h):
        errs.append("缺算法落地卡 .walk")
    for i, w in enumerate(div_spans(h, "walk"), 1):
        inner = w[2]
        if 'class="walk-h"' not in inner:
            errs.append("落地卡 %d 缺 .walk-h 标题" % i)
        if 'class="walk-req"' not in inner:
            errs.append("落地卡 %d 缺 .walk-req（题目身份 + 题面 + 样例）" % i)
        elif not re.search(r'<a href="https?://', inner):
            errs.append("落地卡 %d 的 .walk-req 缺原题外链" % i)
        n = len(re.findall(r'<div class="walk-step"', inner))
        if not 3 <= n <= 5:
            errs.append("落地卡 %d 的 .walk-step 应为 3~5 步，实际 %d 步" % (i, n))
        if 'class="walk-oi"' not in inner:
            errs.append("落地卡 %d 缺 .walk-oi（竞赛用法）" % i)
        else:
            m = re.search(r'<div class="tags">(.*?)</div>', inner, re.S)
            ntag = len(re.findall(r"<span>", m.group(1))) if m else 0
            if not 2 <= ntag <= 4:
                errs.append("落地卡 %d 的 .tags 应放 2~4 个标签，实际 %d 个" % (i, ntag))
        if not any("#include" in b and "return" in b
                   for b in re.findall(r"<pre[^>]*>.*?</pre>", inner, re.S)):
            errs.append("落地卡 %d 里没有保留完整程序（某个 <pre> 要从 #include 到 return）" % i)

    if not re.search(r'<div class="step"[^>]*>|<div class="walk-step"[^>]*>', h):
        errs.append("缺「逐行拆解」区块 .step / .walk-step")
    if not re.search(r'<div class="box warn"[^>]*>', h):
        errs.append("缺易错清单 .box.warn")
    if not re.search(r'<div class="mathcard"[^>]*>', h):
        errs.append("缺「数学补给」.mathcard")
    if not re.search(r'<div class="reproduce"[^>]*>', h):
        errs.append("缺「自己动手复现」.reproduce")
    if 'class="cap"' not in h:
        warns.append("代码块前建议加 <div class=\"cap\">完整代码</div> 之类的小标题")

    # ---- 代码逻辑图（figure.dia 竖排流程 或 figure.fig 里的 SVG 流程图）
    dias = div_spans(h, "dia")
    svg_flow = [f for f in re.findall(r"<figure\b.*?</figure>", h, re.S)
                if "fnode" in f or "flow" in f]
    if not dias and not svg_flow:
        errs.append("缺代码逻辑图：<figure class=\"dia\"> 的 dflow/dsteps，或 figure.fig 里的 SVG 流程图")
    for i, d in enumerate(dias, 1):
        inner = d[2]
        if "<figcaption>" not in inner:
            errs.append("图解 %d 缺 figcaption（写清“这张图在解释哪段代码”）" % i)
        if not re.search(r'class="dflow"|class="dsteps"|class="darr"|class="dmatrix"|class="dcmp-wrap"|class="dtree"', inner):
            errs.append("图解 %d 里没有可识别的主体（dflow / dsteps / darr / dmatrix / dcmp-wrap / dtree）" % i)

    # ---- 思考点：每个 .tq 后面必须紧跟 details.ta
    think = div_spans(h, "think")
    if not think:
        errs.append("缺「举一反三」.think 区块")
    else:
        t = think[0][2]
        if 'class="tt"' not in t:
            errs.append("思考点缺 .tt 标题")
        nq = len(re.findall(r'<div class="tq"', t))
        na = len(re.findall(r'<details class="ta"', t))
        if nq < MIN_THINK:
            errs.append("思考题不足：需要 >=%d，实际 %d" % (MIN_THINK, nq))
        if nq != na:
            errs.append("思考题 %d 道，但折叠解析 %d 个，必须一一对应" % (nq, na))

    # ---- 挑战题
    ch = div_spans(h, "challenge")
    if not ch:
        errs.append("缺节末挑战题 .challenge")
    for i, c in enumerate(ch, 1):
        inner = c[2]
        if 'class="ct"' not in inner:
            errs.append("挑战题 %d 缺 .ct 标题" % i)
        if 'class="hintbox"' not in inner:
            errs.append("挑战题 %d 缺 .hintbox（先只看提示）" % i)
        if len(re.findall(r"<details\b", inner)) < 1:
            errs.append("挑战题 %d 缺折叠的「思路 / 题解」<details>" % i)

    # ---- details 必须有 summary
    for i, d in enumerate(re.findall(r"<details\b[^>]*>(.*?)</details>", h, re.S), 1):
        if "<summary>" not in d:
            errs.append("第 %d 个 <details> 缺 <summary>（折叠标题）" % i)

    # ---- 代码块
    blocks = re.findall(r"<pre[^>]*>(.*?)</pre>", h, re.S)
    if not blocks:
        errs.append("缺代码块 <pre>")
    for i, b in enumerate(blocks, 1):
        if "<code>" not in b:
            warns.append("第 %d 个 <pre> 建议包一层 <code>" % i)
        if re.search(r"<(?![/a-zA-Z!])", b):
            errs.append("第 %d 个代码块里有未转义的 < ，浏览器会当成标签" % i)
        if re.search(r"&(?!(amp|lt|gt|quot|#\d+|#x[0-9a-fA-F]+);)", b):
            errs.append("第 %d 个代码块里有未转义的 &" % i)

    # ---- 锚点
    ids = re.findall(r'\sid="(b\d+)"', h)
    if len(ids) < 8:
        warns.append("正文锚点只有 %d 个，可能没跑 tools/build.py" % len(ids))
    dup = sorted({x for x in ids if ids.count(x) > 1})
    if dup:
        errs.append("id 重复：%s" % ", ".join(dup))

    # ---- 右侧本节目录
    aside = re.search(r'<aside class="rtoc".*?</aside>', h, re.S)
    if not aside:
        errs.append("缺右侧「本节目录」<aside class=\"rtoc\">")
    else:
        a = aside.group(0)
        items = re.findall(r'class="rt-i lv(\d)" href="#([^"]+)" data-t="([^"]+)"', a)
        if len(items) < MIN_RTOC:
            errs.append("本节目录只有 %d 条，可能没跑 tools/build.py" % len(items))
        if 'class="rt-sum"' not in a:
            errs.append("本节目录缺 .rt-sum（本节概述）")
        page_ids = set(re.findall(r'\sid="([^"]+)"', h))
        for _lv, href, dt in items:
            if dt not in page_ids or href != dt:
                errs.append("本节目录条目指向不存在的锚点 #%s" % href)
        if not [x for x in items if x[0] == "1"]:
            errs.append("本节目录里没有一级条目（例题 / 数学补给 / 挑战题的标题）")

    # ---- 链接
    for href in re.findall(r'href="([^"#:]+\.html)"', h):
        if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(path), href))):
            warns.append("链接目标不存在: %s" % href)

    # ---- 篇幅
    txt = strip_tags(re.sub(r"<pre.*?</pre>", " ", h, flags=re.S))
    cn = len(re.findall(r"[\u4e00-\u9fff]", txt))
    if cn < MIN_CN:
        warns.append("正文汉字仅 %d（建议 >=%d），内容可能过薄" % (cn, MIN_CN))
    for bad in ("TODO", "FIXME", "这里写"):
        if bad in h:
            errs.append("疑似占位内容：%s" % bad)
    return errs, warns


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    files = [os.path.join(ROOT, a) for a in args] if args else \
        [os.path.join(ROOT, "%02d.html" % it["id"]) for _g, it in C.all_items()]
    bad = 0
    for f in files:
        e, w = check(f)
        if e:
            bad += 1
            print("FAIL", os.path.basename(f))
            for x in e:
                print("   x", x)
        else:
            print("OK  ", os.path.basename(f))
        for x in w:
            print("   -", x)
    for need in ("assets/toc.js", "assets/search-index.js", "index.html"):
        if not os.path.exists(os.path.join(ROOT, need)):
            print("   - 缺生成物 %s（先跑 python tools/build.py）" % need)
    print("\n%d/%d 通过" % (len(files) - bad, len(files)))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
