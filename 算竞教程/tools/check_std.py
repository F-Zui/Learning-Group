# -*- coding: utf-8 -*-
"""按《算法类要求.md》/ 模板 tools/check.py 的规则检查已渲染的课程页面。"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.abspath(os.path.join(HERE, ".."))

MIN_THINK = 3
MIN_CN = 900


def strip_tags(h):
    return re.sub(r"<[^>]+>", " ", h)


def div_spans(h, cls):
    out = []
    tag_re = r'<(div|figure) class="%s"[^>]*>' % cls
    for m in re.finditer(tag_re, h):
        tag = m.group(1)
        i = m.end()
        depth = 1
        pat = r"<div\b|</div>|<figure\b|</figure>" if tag == "figure" else r"<div\b|</div>"
        for t in re.finditer(pat, h[i:]):
            if t.group(0).startswith("<" + tag):
                depth += 1
            elif t.group(0).startswith("</" + tag):
                depth -= 1
            if depth == 0:
                out.append((m.start(), i + t.end(), h[i:i + t.start()]))
                break
    return out


def check(path, num, title):
    errs = []
    h = open(path, encoding="utf-8").read()
    if not re.search(r'<div class="prob"[^>]*>', h):
        errs.append("缺例题卡 .prob")
    if not re.search(r'<div class="fn"[^>]*>', h):
        errs.append("缺新函数拆解 .fn")
    if not re.search(r'<div class="step"[^>]*>', h):
        errs.append("缺 .step")
    if not re.search(r'<div class="box warn"[^>]*>', h):
        errs.append("缺易错 .box.warn")
    if not re.search(r'<div class="mathcard"[^>]*>', h) and 'class="portal"' not in h:
        errs.append("缺数学补给 .mathcard / .portal")
    if not re.search(r'<div class="reproduce"[^>]*>', h):
        errs.append("缺复现 .reproduce")
    dias = re.findall(r'<figure class="dia[^"]*"[^>]*>(.*?)</figure>', h, re.S)
    if not dias:
        errs.append("缺代码逻辑图 figure.dia")
    for i, d in enumerate(dias, 1):
        if "<figcaption>" not in d:
            errs.append("图解 %d 缺 figcaption" % i)
        if not re.search(r'class="dflow"|class="dsteps"|class="darr"|class="dmatrix"|class="dcmp-wrap"|class="dtree"', d):
            errs.append("图解 %d 无主体" % i)
    think = div_spans(h, "think")
    if not think:
        errs.append("缺举一反三 .think")
    else:
        t = think[0][2]
        nq = len(re.findall(r'<div class="tq"', t))
        na = len(re.findall(r'<details class="ta"', t))
        if nq < MIN_THINK:
            errs.append("思考题 %d < %d" % (nq, MIN_THINK))
        if nq != na:
            errs.append("思考题 %d 道 / 解析 %d 个" % (nq, na))
    ch = div_spans(h, "challenge")
    if not ch:
        errs.append("缺挑战题 .challenge")
    for i, c in enumerate(ch, 1):
        if 'class="ct"' not in c[2]:
            errs.append("挑战题 %d 缺 .ct" % i)
        if 'class="hintbox"' not in c[2]:
            errs.append("挑战题 %d 缺 .hintbox" % i)
        if "<details" not in c[2]:
            errs.append("挑战题 %d 缺折叠" % i)
    for i, d in enumerate(re.findall(r"<details\b[^>]*>(.*?)</details>", h, re.S), 1):
        if "<summary>" not in d:
            errs.append("第 %d 个 details 缺 summary" % i)
    for i, b in enumerate(re.findall(r"<pre[^>]*>(.*?)</pre>", h, re.S), 1):
        if re.search(r"<(?![/a-zA-Z!])", b):
            errs.append("代码块 %d 有未转义 <" % i)
        if re.search(r"&(?!(amp|lt|gt|quot|#\d+|#x[0-9a-fA-F]+);)", b):
            errs.append("代码块 %d 有未转义 &" % i)
    ids = re.findall(r'\sid="(b\d+)"', h)
    if len(ids) < 8:
        errs.append("锚点只有 %d 个" % len(ids))
    if len(set(ids)) != len(ids):
        errs.append("锚点 id 重复")
    aside = re.search(r'<aside class="rtoc".*?</aside>', h, re.S)
    if not aside:
        errs.append("缺右册 rtoc")
    else:
        a = aside.group(0)
        items = re.findall(r'class="rt-i lv(\d)" href="#([^"]+)" data-t="([^"]+)"', a)
        if len(items) < 3:
            errs.append("rtoc 条目 %d < 3" % len(items))
        page_ids = set(re.findall(r'\sid="([^"]+)"', h))
        for _lv, href, dt in items:
            if dt not in page_ids:
                errs.append("rtoc 指向不存在的锚点 #%s" % href)
                break
        if not [x for x in items if x[0] == "1"]:
            errs.append("rtoc 没有一级条目")
    txt = strip_tags(re.sub(r"<pre.*?</pre>", " ", h, flags=re.S))
    cn = len(re.findall(r"[\u4e00-\u9fff]", txt))
    if cn < MIN_CN:
        errs.append("中文 %d < %d" % (cn, MIN_CN))
    return errs, cn


def main():
    ids = [int(x) for x in sys.argv[1:]] or list(range(1, 61))
    import curriculum
    metas = {m["id"]: m for m in curriculum.all_lessons()}
    bad = 0
    for lid in ids:
        path = os.path.join(OUT, "sections", "%02d.html" % lid)
        if not os.path.exists(path):
            print("[%02d] 页面缺失" % lid)
            bad += 1
            continue
        errs, cn = check(path, lid, metas.get(lid, {}).get("title", ""))
        if errs:
            bad += 1
            print("[%02d] 中文 %-5d %s" % (lid, cn, "；".join(errs)))
        else:
            print("[%02d] 中文 %-5d OK" % (lid, cn))
    print("\n不合格 %d / %d" % (bad, len(ids)))


if __name__ == "__main__":
    main()
