# -*- coding: utf-8 -*-
"""单节结构自检（模板版）。

用法:
    python tools/check.py                 # 检查 sections/ 全部
    python tools/check.py sections/1-1.html
"""
import glob
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
MIN_FIG, MIN_EX, MIN_EXS, MIN_THINK = 2, 2, 3, 1


def strip_tags(h):
    return re.sub(r"<[^>]+>", " ", h)


def check(path):
    errs, warns = [], []
    if not os.path.exists(path):
        return ["文件不存在: %s" % path], []
    h = open(path, encoding="utf-8").read()

    m = re.search(r'data-sec="([\d.]+)"', h)
    if not m:
        errs.append("缺少 body data-sec")
    else:
        sid = m.group(1)
        if os.path.basename(path) != sid.replace(".", "-") + ".html":
            errs.append("文件名应为 %s.html" % sid.replace(".", "-"))
        if f"<title>{sid} " not in h:
            errs.append("<title> 应以「%s 」开头" % sid)

    if "../assets/style.css" not in h:
        errs.append("缺少样式表引用")
    if "../assets/app.js" not in h:
        errs.append("缺少 app.js 引用")
    if "../assets/theme.js" not in h:
        errs.append("缺少 theme.js 引用（主题会闪）")

    h1 = re.findall(r"<h1[^>]*>(.*?)</h1>", h, re.S)
    if len(h1) != 1:
        errs.append("h1 数量应为 1，实际 %d" % len(h1))
    h2 = re.findall(r'<h2[^>]*id="(s\d+)"[^>]*>', h)
    if len(h2) < 2:
        errs.append("h2 至少 2 个（右侧栏大纲用），实际 %d" % len(h2))
    if len(set(h2)) != len(h2):
        errs.append("h2 id 有重复")

    figs = re.findall(r"<figure\b.*?</figure>", h, re.S)
    if len(figs) < MIN_FIG:
        errs.append("图不足：需要 >=%d，实际 %d" % (MIN_FIG, len(figs)))
    for i, f in enumerate(figs, 1):
        cap = re.search(r"<figcaption[^>]*>(.*?)</figcaption>", f, re.S)
        if not cap or len(strip_tags(cap.group(1)).strip()) < 4:
            errs.append("第 %d 幅图缺图注" % i)

    if len(re.findall(r'<div class="ex">', h)) < MIN_EX:
        errs.append("例题不足：需要 >=%d" % MIN_EX)

    exs = re.findall(r'<ol class="exs">(.*?)</ol>', h, re.S)
    if not exs:
        errs.append('缺少 <ol class="exs"> 习题列表')
    else:
        lis = re.findall(r"<li[^>]*>(.*?)</li>", exs[0], re.S)
        if len(lis) < MIN_EXS:
            errs.append("习题不足：需要 >=%d，实际 %d" % (MIN_EXS, len(lis)))
        for i, li in enumerate(lis, 1):
            if 'class="idea"' not in li:
                errs.append("习题 %d 缺 .idea（思路）" % i)
            if 'class="ans"' not in li:
                errs.append("习题 %d 缺 .ans（答案）" % i)

    if len(re.findall(r'<div class="think">', h)) < MIN_THINK:
        errs.append("至少需要 1 个思考点 .think")
    if 'class="keybox"' not in h:
        errs.append("缺少 .keybox 小结")

    if len(re.findall(r"\$\$", h)) % 2:
        errs.append("$$ 定界符不成对")
    single = re.sub(r"\$\$.*?\$\$", "", h, flags=re.S)
    if len(re.findall(r"(?<!\$)\$(?!\$)", single)) % 2:
        errs.append("$ 定界符不成对")

    for mm in re.finditer(r"\$\$(.+?)\$\$|\$([^$\n]+?)\$", h, re.S):
        body = mm.group(1) or mm.group(2) or ""
        if re.search(r"(?<![\\a-zA-Z])<(?![a-zA-Z/!])", body):
            errs.append("公式里有未转义的 < ：%s" % body[:40])

    for href in re.findall(r'href="([^"#]+\.html)"', h):
        p = os.path.normpath(os.path.join(os.path.dirname(path), href))
        if not os.path.exists(p):
            warns.append("链接目标不存在: %s" % href)

    txt = strip_tags(re.sub(r"\$\$.*?\$\$|\$[^$]*\$", "", h, flags=re.S))
    cn = len(re.findall(r"[\u4e00-\u9fff]", txt))
    if cn < 300:
        warns.append("正文汉字仅 %d，内容可能过薄" % cn)
    return errs, warns


def main():
    args = sys.argv[1:]
    files = []
    for a in args:
        files.extend(glob.glob(a))
    if not files:
        files = sorted(glob.glob(os.path.join(ROOT, "sections", "*.html")))
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
