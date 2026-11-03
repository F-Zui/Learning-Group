# -*- coding: utf-8 -*-
r"""数学类单节结构自检。

用法:
    python tools/check.py                       # 检查 sections/ 全部
    python tools/check.py sections/1-1.html     # 检查指定文件
    python tools/check.py sections/1-1.html sections/2-1.html

检查的是「数学课件的写法」而不只是 HTML 合法性：

  身份      data-sec / 文件名 / <title> 三者一致，四个引擎资源 + course.css 齐全
  节头      sec-head、lede、meta（难度、关键词）
  标题      h1 恰好 1 个；h2 为 s1…sN 连续
  推导卡    ≥1 张 .derive，且每个 .thm 之前必须已有推导卡（先推导、后定理）
  陈述      .def/.thm/.prf 等盒子必须以 .tag 开头；.prf 以 ∎ 收尾
  落地卡    有代码就必须有 .walk；每张 .walk 必须有需求 / 拆步 / 每步 snip / 为什么 / 竞赛用法
  代码      代码块内 < & 必须转义；有代码就必须有流程图（figure.fig + fnode）
  例题      2 个，每个有 .ex-h 与 .sol；习题 3 道，每题 .idea + .ans
  图        ≥2 幅且都有 figcaption；figure.plot 只能用受支持的 data-*
  公式      $ / $$ 成对；公式内 < > & 必须转义
  篇幅      正文汉字 <1000 报错，<1200 提醒
"""
import glob
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
MIN_FIG, MIN_EX, MIN_EXS, MIN_THINK = 2, 2, 3, 1
MIN_CN_HARD, MIN_CN = 1000, 1200
PLOT_ATTRS = {"data-fn", "data-x", "data-y", "data-fill", "data-between", "data-tangent",
              "data-secant", "data-rect", "data-eps", "data-dots", "data-dotlabels",
              "data-legend", "data-type", "data-range", "data-points", "data-labels",
              "data-interval", "data-hollow", "data-hline", "data-vline", "data-svg"}
TAGGED = ("def", "thm", "prf", "insight", "warn", "why", "note")


def strip_tags(h):
    return re.sub(r"<[^>]+>", " ", h)


def div_spans(h, cls):
    """返回所有 class 恰含 cls 的 <div> 片段（按 div 嵌套深度配平），元素为 (start, end, inner)。"""
    out = []
    for m in re.finditer(r'<div class="%s"[^>]*>' % cls, h):
        i = m.end()
        depth = 1
        for t in re.finditer(r"<div\b|</div>", h[i:]):
            depth += 1 if t.group(0).startswith("<div") else -1
            if depth == 0:
                out.append((m.start(), i + t.end(), h[i:i + t.start()]))
                break
    return out


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

    # ---- 引擎与课程样式
    for ref, tip in (("../assets/style.css", "样式表"),
                     ("../assets/course.css", "课程样式表（推导卡、落地卡、代码块、流程图都靠它）"),
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

    # ---- 推导卡（先推导，后定理）
    derives = div_spans(h, "derive")
    thms = [m.start() for m in re.finditer(r'<div class="thm"[^>]*>', h)]
    if not derives:
        errs.append("缺少推导卡 .derive（每个定理前必须有「问题 → 尝试 → 验证 → 落定理」）")
    if thms:
        first_derive = derives[0][0] if derives else None
        if first_derive is None or thms[0] < first_derive:
            errs.append("第 1 个定理出现在推导卡之前：定理必须排在推导之后")
        for i, pos in enumerate(thms, 1):
            if derives and not any(d[0] < pos for d in derives):
                errs.append("第 %d 个定理之前没有推导卡" % i)
    for i, (s, e, inner) in enumerate(derives, 1):
        if 'class="derive-h"' not in inner:
            errs.append("推导卡 %d 缺 .derive-h 卡头" % i)
        elif 'class="dk"' not in inner:
            errs.append("推导卡 %d 的卡头缺 <span class=\"dk\">推导</span>" % i)
        if 'class="derive-q"' not in inner:
            errs.append("推导卡 %d 缺 .derive-q（问题）" % i)
        if len(re.findall(r'class="dstep"', inner)) < 2:
            errs.append("推导卡 %d 的步骤少于 2 步（建议 3–5 步）" % i)
        if 'class="dh"' not in inner:
            errs.append("推导卡 %d 缺 .dh 步骤标题" % i)
        if 'class="dcheck"' not in inner:
            warns.append("推导卡 %d 没有 .dcheck（验证/关键一步最好单独点出）" % i)
        if 'class="derive-end"' not in inner:
            errs.append("推导卡 %d 缺 .derive-end（「于是我们得到……」）" % i)

    # ---- 算法落地卡（定理之后的可执行版本）
    walks = div_spans(h, "walk")
    has_code = bool(re.search(r'<pre class="code"', h)) or bool(re.search(r'<pre class="snip"', h))
    if has_code and not walks:
        errs.append("出现代码块但没有算法落地卡 .walk（代码必须对应定理的某一步）")
    for i, (s, e, inner) in enumerate(walks, 1):
        if 'class="walk-h"' not in inner:
            errs.append("落地卡 %d 缺 .walk-h 卡头" % i)
        elif 'class="wk"' not in inner:
            errs.append("落地卡 %d 的卡头缺 <span class=\"wk\">算法落地</span>" % i)
        if 'class="cover"' not in inner:
            warns.append("落地卡 %d 的卡头建议写 <span class=\"cover\">覆盖：定理/算法</span>" % i)
        if 'class="walk-req"' not in inner:
            errs.append("落地卡 %d 缺 .walk-req（需求：一个能手算的具体例子）" % i)
        steps = re.findall(r'class="walk-step"', inner)
        if len(steps) < 2:
            errs.append("落地卡 %d 的拆步少于 2 步（建议 3–5 步）" % i)
        snips = len(re.findall(r'<pre class="snip"', inner))
        if snips < len(steps):
            errs.append("落地卡 %d：%d 步只有 %d 段代码，每步都要有 .snip" % (i, len(steps), snips))
        whys = len(re.findall(r'class="ws-why"', inner))
        if whys < len(steps):
            errs.append("落地卡 %d：%d 步只有 %d 个 .ws-why（每步都要说明为什么）" % (i, len(steps), whys))
        if 'class="ws-n"' not in inner:
            errs.append("落地卡 %d 缺 .ws-n 步骤序号" % i)
        if 'class="walk-oi"' not in inner:
            errs.append("落地卡 %d 缺 .walk-oi（竞赛用法）" % i)
        elif 'class="tags"' not in inner:
            warns.append("落地卡 %d 的竞赛用法建议加 .tags（模型 / 复杂度 / 常见坑）" % i)

    # ---- 代码块
    codeboxes = div_spans(h, "codebox")
    for i, (s, e, inner) in enumerate(codeboxes, 1):
        if 'class="code-h"' not in inner:
            errs.append("代码块 %d 缺 .code-h 标题条（写清这段代码对应哪一步）" % i)
        if '<pre class="code"' not in inner:
            errs.append("代码块 %d 缺 <pre class=\"code\">" % i)
    for i, b in enumerate(re.findall(r"<pre[^>]*>(.*?)</pre>", h, re.S), 1):
        if re.search(r"<(?![/a-zA-Z!])", b):
            errs.append("第 %d 个代码块里有未转义的 < ，浏览器会当成标签" % i)
        if re.search(r"&(?!(amp|lt|gt|quot|#\d+|#x[0-9a-fA-F]+);)", b):
            errs.append("第 %d 个代码块里有未转义的 &" % i)

    # ---- 图
    figs = re.findall(r"<figure\b.*?</figure>", h, re.S)
    if len(figs) < MIN_FIG:
        errs.append("图不足：需要 >=%d，实际 %d" % (MIN_FIG, len(figs)))
    flow = [f for f in figs if "fnode" in f]
    if has_code and not flow:
        errs.append("有代码但没有代码逻辑流程图（figure.fig + svg.dgm 里用 fnode/ar 画分支）")
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
        boxes[cls] = re.findall(r'<div class="%s"' % cls, h)
        if boxes[cls] and len(re.findall(r'<div class="%s"[^>]*>\s*<span class="tag">' % cls, h)) < len(boxes[cls]):
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
        if re.search(r"&(?!amp;|lt;|gt;|quot;|#)", body):
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
            errs.append("疑似占位内容：%s" % bad)
    txt = strip_tags(re.sub(r"\$\$.*?\$\$|\$[^$]*\$", "", h, flags=re.S))
    cn = len(re.findall(r"[\u4e00-\u9fff]", txt))
    if cn < MIN_CN_HARD:
        errs.append("正文汉字仅 %d，低于下限 %d" % (cn, MIN_CN_HARD))
    elif cn < MIN_CN:
        warns.append("正文汉字 %d，建议 >=%d" % (cn, MIN_CN))
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
