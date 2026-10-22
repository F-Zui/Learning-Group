# -*- coding: utf-8 -*-
"""检查一节 HTML 是否符合 AUTHORING.md 的硬性要求。
用法: python tools/site/check.py sections/3-2.html [...]
"""
import glob
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
MIN_FIG, MIN_EX, MIN_EXS, MIN_THINK = 3, 4, 6, 2


def strip_tags(h):
    return re.sub(r"<[^>]+>", " ", h)


def check(path):
    errs, warns = [], []
    if not os.path.exists(path):
        return [f"文件不存在: {path}"], []
    h = open(path, encoding="utf-8").read()

    m = re.search(r'data-sec="([\d.]+)"', h)
    if not m:
        errs.append("缺少 body data-sec")
    else:
        sid = m.group(1)
        want = sid.replace(".", "-") + ".html"
        if os.path.basename(path) != want:
            errs.append(f"文件名应为 {want}（data-sec={sid}）")
        if f"<title>{sid} " not in h:
            errs.append(f"<title> 应以「{sid} 」开头")

    if not h.lstrip().startswith("<!DOCTYPE html>"):
        errs.append("缺少 <!DOCTYPE html>")
    if "../assets/style.css" not in h:
        errs.append("缺少样式表引用")
    if "../assets/app.js" not in h:
        errs.append("缺少 app.js 引用")

    h1 = re.findall(r"<h1[^>]*>(.*?)</h1>", h, re.S)
    if len(h1) != 1:
        errs.append(f"h1 数量应为 1，实际 {len(h1)}")
    h2 = re.findall(r'<h2[^>]*id="(s\d+)"[^>]*>', h)
    if not (3 <= len(h2) <= 8):
        errs.append(f"h2 数量应在 3–8 之间，实际 {len(h2)}")
    if len(set(h2)) != len(h2):
        errs.append("h2 id 有重复")

    allfigs = re.findall(r"<figure\b.*?</figure>", h, re.S)
    if len(allfigs) < MIN_FIG:
        errs.append(f"图不足：需要 >={MIN_FIG}，实际 {len(allfigs)}")
    for i, f in enumerate(allfigs, 1):
        cap = re.search(r"<figcaption>(.*?)</figcaption>", f, re.S)
        if not cap or len(strip_tags(cap.group(1)).strip()) < 4:
            errs.append(f"第 {i} 幅图缺图注或图注过短")
        if "data-fn=" in f:
            fn = re.search(r'data-fn="([^"]+)"', f)
            if fn:
                for expr in fn.group(1).split(";"):
                    expr = expr.strip()
                    if re.search(r"\d\s*[a-zA-Z]", expr) and not re.search(r"\d\s*[eE]\b", expr):
                        errs.append(f'data-fn="{expr}" 缺少乘号（写 2*x 而不是 2x）')
                    if re.search(r"[^\w\s\.\+\-\*/\^\(\),;]", expr):
                        errs.append(f'data-fn="{expr}" 含可疑字符')

    exs = len(re.findall(r'<div class="ex">', h))
    if exs < MIN_EX:
        errs.append(f"例题不足：需要 >={MIN_EX}，实际 {exs}")

    exs_items = re.findall(r'<ol class="exs">(.*?)</ol>', h, re.S)
    if not exs_items:
        errs.append('缺少 <ol class="exs"> 习题列表')
    else:
        lis = re.findall(r"<li>(.*?)</li>", exs_items[0], re.S)
        if len(lis) < MIN_EXS:
            errs.append(f"习题不足：需要 >={MIN_EXS}，实际 {len(lis)}")
        for i, li in enumerate(lis, 1):
            if 'class="idea"' not in li:
                errs.append(f"习题 {i} 缺 .idea（思路）")
            if 'class="ans"' not in li:
                errs.append(f"习题 {i} 缺 .ans（答案）")

    if len(re.findall(r'<div class="think">', h)) < MIN_THINK:
        errs.append(f"思考点不足：需要 >={MIN_THINK}")

    if 'class="keybox"' not in h:
        errs.append("缺少 .keybox 小结")
    if not re.search(r'class="prf"|class="why"', h):
        errs.append("至少要有一个证明 .prf 或动机 .why")

    if len(re.findall(r"\$\$", h)) % 2:
        errs.append("$$ 定界符不成对")
    single = re.sub(r"\$\$.*?\$\$", "", h, flags=re.S)
    if len(re.findall(r"(?<!\$)\$(?!\$)", single)) % 2:
        errs.append("$ 定界符不成对")

    for mm in re.finditer(r"\$\$(.+?)\$\$|\$([^$\n]+?)\$", h, re.S):
        body = mm.group(1) or mm.group(2) or ""
        if re.search(r"(?<![\\a-zA-Z])<(?![a-zA-Z/!])", body):
            errs.append(f"公式里有未转义的 < ：{body[:40]}")

    for href in re.findall(r'href="([^"#]+\.html)"', h):
        p = os.path.normpath(os.path.join(os.path.dirname(path), href))
        if not os.path.exists(p):
            warns.append(f"链接目标尚不存在: {href}")

    txt = strip_tags(re.sub(r"\$\$.*?\$\$|\$[^$]*\$", "", h, flags=re.S))
    cn = len(re.findall(r"[\u4e00-\u9fff]", txt))
    if cn < 600:
        warns.append(f"正文汉字仅 {cn}，可能过于单薄")
    if cn > 3200:
        warns.append(f"正文汉字 {cn}，偏长")

    for bad in ("TODO", "lorem", "待补", "XXX"):
        if bad in h:
            errs.append(f"残留占位符 {bad}")

    return errs, warns


def main():
    args = sys.argv[1:]
    files = []
    for a in args:
        files.extend(glob.glob(a))
    if not files:
        files = sorted(glob.glob(os.path.join(ROOT, "sections", "*.html")))
        files = [f for f in files if not os.path.basename(f).startswith("_")]
    bad = 0
    for f in files:
        e, w = check(f)
        name = os.path.basename(f)
        if e:
            bad += 1
            print(f"FAIL {name}")
            for x in e:
                print("   x", x)
        else:
            print(f"OK   {name}")
        for x in w:
            print("   - ", x)
    print(f"\n{len(files) - bad}/{len(files)} 通过")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
