# -*- coding: utf-8 -*-
r"""数学类单节结构自检。

用法:
    python tools/check.py                       # 检查 sections/ 全部
    python tools/check.py sections/1-1.html     # 检查指定文件
    python tools/check.py sections/1-1.html sections/2-1.html

检查的是「数学课件的写法」而不只是 HTML 合法性：
  · 严格陈述（定义 / 定理）必须带 .tag 标签，证明必须收尾 ∎；
  · 例题必须有题干区与 .sol 解答，习题必须「先思路后答案」；
  · 公式定界符成对、公式里的 < 必须写成 \lt、& 必须写成 &amp;；
  · 每节至少 2 幅带图注的图（figure.plot 自动绘图 / figure.fig 手绘 SVG）；
  · 正文汉字不少于 700，避免留下空壳。
"""
import glob
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
MIN_FIG, MIN_EX, MIN_EXS, MIN_THINK, MIN_CN = 2, 2, 3, 1, 700
PLOT_ATTRS = {"data-fn", "data-x", "data-y", "data-fill", "data-between", "data-tangent",
              "data-secant", "data-rect", "data-eps", "data-dots", "data-dotlabels",
              "data-legend", "data-type", "data-range", "data-points", "data-labels",
              "data-interval", "data-hollow", "data-hline", "data-vline", "data-svg"}
TAGGED = ("def", "thm", "prf", "insight", "warn", "why", "note")


def strip_tags(h):
    return re.sub(r"<[^>]+>", " ", h)


def check(path):
    errs, warns = [], []
    if not os.path.exists(path):
        return ["文件不存在: %s" % path], []
    h = open(path, encoding="utf-8").read()

    # ---- 身份：编号 / 文件名 / title 三者一致
    m = re.search(r'data-sec="([\d.]+)"', h)
    sid = None
    if not m:
        errs.append("缺少 body data-sec")
    else:
        sid = m.group(1)
        if os.path.basename(path) != sid.replace(".", "-") + ".html":
            errs.append("文件名应为 %s.html" % sid.replace(".", "-"))
        if "<title>%s " % sid not in h:
            errs.append("<title> 应以「%s 」开头" % sid)

    # ---- 引擎引用
    for ref, tip in (("../assets/style.css", "样式表"),
                     ("../assets/app.js", "app.js"),
                     ("../assets/theme.js", "theme.js（缺了主题会闪）"),
                     ("../assets/toc.js", "toc.js（缺了左侧栏与上一节/下一节会失效）")):
        if ref not in h:
            errs.append("缺少%s引用：%s" % (tip, ref))

    # ---- 节头四件套
    if 'class="sec-head"' not in h:
        errs.append('缺少 <header class="sec-head">')
    if 'class="lede"' not in h:
        errs.append("缺少 .lede 导语（右栏「本节」概述取它）")
    meta = re.search(r'<div class="meta">(.*?)</div>', h, re.S)
    if not meta:
        errs.append('缺少 <div class="meta"> 元信息')
    else:
        if "难度" not in meta.group(1):
            warns.append("meta 里没有「难度」")
        if "关键词" not in meta.group(1):
            warns.append("meta 里没有「关键词」（全站检索的标签命中取它）")

    # ---- 标题层级
    h1 = re.findall(r"<h1[^>]*>(.*?)</h1>", h, re.S)
    if len(h1) != 1:
        errs.append("h1 数量应为 1，实际 %d" % len(h1))
    h2 = re.findall(r'<h2[^>]*id="s(\d+)"[^>]*>', h)
    if len(h2) < 2:
        errs.append("h2 至少 2 个（右侧栏大纲用），实际 %d" % len(h2))
    nums = [int(x) for x in h2]
    if nums != list(range(1, len(nums) + 1)):
        errs.append("h2 的 id 必须 s1…sN 连续，实际 %s" % ("s" + ", s".join(map(str, nums)) if nums else "无"))
    if len(set(h2)) != len(h2):
        errs.append("h2 id 有重复")

    # ---- 图
    figs = re.findall(r"<figure\b.*?</figure>", h, re.S)
    if len(figs) < MIN_FIG:
        errs.append("图不足：需要 >=%d，实际 %d" % (MIN_FIG, len(figs)))
    for i, f in enumerate(figs, 1):
        cap = re.search(r"<figcaption[^>]*>(.*?)</figcaption>", f, re.S)
        if not cap or len(strip_tags(cap.group(1)).strip()) < 4:
            errs.append("第 %d 幅图缺图注（figcaption 里写清“看图该看出什么”）" % i)
        if "figure.plot" in f or 'class="plot"' in f:
            for attr in re.findall(r"(data-[a-z]+)=", f):
                if attr not in PLOT_ATTRS:
                    errs.append("第 %d 幅 plot 图用了不支持的属性 %s（可用：%s）"
                                % (i, attr, " ".join(sorted(PLOT_ATTRS))))
        elif 'class="fig"' not in f:
            warns.append("第 %d 幅图既不是 figure.plot 也不是 figure.fig，样式不会生效" % i)

    # ---- 严格陈述与证明
    boxes = {}
    for cls in TAGGED:
        boxes[cls] = re.findall(r'<div class="%s">' % cls, h)
        if boxes[cls] and len(re.findall(r'<div class="%s">\s*<span class="tag">' % cls, h)) < len(boxes[cls]):
            errs.append("有 .%s 缺少 <span class=\"tag\"> 标签" % cls)
    if not boxes["def"] and not boxes["thm"]:
        errs.append("数学节至少要有一个 .def（定义）或 .thm（定理）")
    prf = re.findall(r'<div class="prf">(.*?)</div>\s*(?=<h2|<div|<figure|<ol|<table|$)', h, re.S)
    for i, p in enumerate(prf, 1):
        if "qed" not in p:
            errs.append("第 %d 个证明 .prf 缺收尾符 <span class=\"qed\">∎</span>" % i)

    # ---- 例题
    exs = re.findall(r'<div class="ex">(.*?)(?=<div class="ex"|<div class="think"|<h2|<div class="keybox"|<ol class="exs"|$)', h, re.S)
    if len(exs) < MIN_EX:
        errs.append("例题不足：需要 >=%d，实际 %d" % (MIN_EX, len(exs)))
    for i, e in enumerate(exs, 1):
        if 'class="ex-h"' not in e:
            errs.append("例题 %d 缺 .ex-h 标题行" % i)
        if 'class="sol"' not in e:
            errs.append("例题 %d 缺 .sol 解答" % i)

    # ---- 习题
    exs_ol = re.findall(r'<ol class="exs">(.*?)</ol>', h, re.S)
    if not exs_ol:
        errs.append('缺少 <ol class="exs"> 习题列表')
    else:
        lis = re.findall(r"<li[^>]*>(.*?)</li>", exs_ol[0], re.S)
        if len(lis) < MIN_EXS:
            errs.append("习题不足：需要 >=%d，实际 %d" % (MIN_EXS, len(lis)))
        for i, li in enumerate(lis, 1):
            if 'class="idea"' not in li:
                errs.append("习题 %d 缺 .idea（思路）" % i)
            if 'class="ans"' not in li:
                errs.append("习题 %d 缺 .ans（答案）" % i)

    # ---- 思考点与小结
    think = re.findall(r'<div class="think">(.*?)</div>\s*</div>', h, re.S)
    if len(re.findall(r'<div class="think">', h)) < MIN_THINK:
        errs.append("至少需要 %d 个思考点 .think" % MIN_THINK)
    for i, t in enumerate(think, 1):
        if 'class="tq"' not in t or 'class="ta"' not in t:
            errs.append("思考点 %d 需要 .tq（问）与 .ta（引导），缺一不可" % i)
    kb = re.search(r'<div class="keybox">(.*?)</div>', h, re.S)
    if not kb:
        errs.append("缺少 .keybox 小结（一页纸）")
    elif 'class="kb-h"' not in kb.group(1):
        errs.append(".keybox 缺 .kb-h 标题")

    # ---- 折叠进阶
    for i, sm in enumerate(re.findall(r"<summary>(.*?)</summary>", h, re.S), 1):
        if len(strip_tags(sm).strip()) < 3:
            errs.append("第 %d 个 <summary> 标题为空" % i)
    if '<details class="deep">' in h and "<summary>" not in h:
        errs.append('<details class="deep"> 缺 <summary>')

    # ---- 表格
    for t in re.findall(r"<table[^>]*>", h):
        if "tbl" not in t:
            warns.append("表格建议写 <table class=\"tbl\">，否则不会套用版式")

    # ---- 公式
    if len(re.findall(r"\$\$", h)) % 2:
        errs.append("$$ 定界符不成对")
    single = re.sub(r"\$\$.*?\$\$", "", h, flags=re.S)
    if len(re.findall(r"(?<!\$)\$(?!\$)", single)) % 2:
        errs.append("$ 定界符不成对")
    for mm in re.finditer(r"\$\$(.+?)\$\$|\$([^$\n]+?)\$", h, re.S):
        body = mm.group(1) or mm.group(2) or ""
        if re.search(r"(?<![\\a-zA-Z])<(?![a-zA-Z/!])", body):
            errs.append("公式里有未转义的 < ：%s" % body[:40])
        if re.search(r"(?<![\\a-zA-Z])>(?![a-zA-Z/!])", body):
            errs.append("公式里有未转义的 > ：%s" % body[:40])
        bad_amp = re.search(r"&(?!amp;|lt;|gt;|quot;|#)", body)
        if bad_amp:
            errs.append("公式里的 & 要写成 &amp;（aligned 对齐用）：%s" % body[:40])

    # ---- 锚点唯一性（build.py 会注入 id="bN"）
    ids = re.findall(r'\sid="([^"]+)"', h)
    dup = sorted({x for x in ids if ids.count(x) > 1})
    if dup:
        errs.append("id 重复：%s" % ", ".join(dup))

    # ---- 链接
    for href in re.findall(r'href="([^"#]+\.html)"', h):
        p = os.path.normpath(os.path.join(os.path.dirname(path), href))
        if not os.path.exists(p):
            warns.append("链接目标不存在: %s" % href)

    # ---- 占位残留与篇幅
    for bad in ("TODO", "FIXME", "这里写", "xxxx"):
        if bad in h:
            warns.append("疑似占位内容：%s" % bad)
    txt = strip_tags(re.sub(r"\$\$.*?\$\$|\$[^$]*\$", "", h, flags=re.S))
    cn = len(re.findall(r"[\u4e00-\u9fff]", txt))
    if cn < MIN_CN:
        warns.append("正文汉字仅 %d（建议 >=%d），内容可能过薄" % (cn, MIN_CN))
    return errs, warns


def main():
    args = sys.argv[1:]
    files = []
    for a in args:
        files.extend(glob.glob(a))
    if not files:
        files = sorted(f for f in glob.glob(os.path.join(ROOT, "sections", "*.html"))
                       if not os.path.basename(f).startswith("_"))
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
    print("\n%d/%d 通过" % (len(files) - bad, len(files)))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
