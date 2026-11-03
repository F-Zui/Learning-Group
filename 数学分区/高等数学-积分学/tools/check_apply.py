# -*- coding: utf-8 -*-
"""检查每个定理：前有推导卡、后有例题应用卡；并检查两类卡的四段结构。"""
import glob, os, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

def spans(h, cls):
    out = []
    for m in re.finditer(r'<div class="%s"[^>]*>' % cls, h):
        i = m.end(); depth = 1
        for t in re.finditer(r"<div\b|</div>", h[i:]):
            depth += 1 if t.group(0).startswith("<div") else -1
            if depth == 0:
                out.append((m.start(), i + t.end(), h[m.start():i + t.end()]))
                break
    return out

def tag_of(block):
    m = re.search(r'<span class="tag">(.*?)</span>', block, re.S)
    return re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else "?"

def check(path):
    h = open(path, encoding="utf-8").read()
    blocks = []
    for cls in ("derive", "thm", "prf", "apply"):
        for s, e, inner in spans(h, cls):
            blocks.append((s, e, cls, inner))
    blocks.sort()
    errs = []
    for idx, (s, e, cls, inner) in enumerate(blocks):
        if cls != "thm":
            continue
        prev = [b for b in blocks if b[1] <= s]
        name = tag_of(inner)
        if not prev or prev[-1][2] != "derive":
            errs.append("定理「%s」前缺少紧邻的推导卡" % name)
        nxt = [b for b in blocks if b[0] >= e]
        j = 0
        if j < len(nxt) and nxt[j][2] == "prf":
            j += 1
        if j >= len(nxt) or nxt[j][2] != "apply":
            errs.append("定理「%s」后缺少紧邻的例题应用卡（应在证明之后）" % name)
    for s, e, inner in spans(h, "derive"):
        for key, label in (("derive-h", "卡头"), ("derive-q", "问题"), ("derive-end", "落定理")):
            if key not in inner:
                errs.append("推导卡缺少 .%s（%s）" % (key, label))
        if inner.count('class="dstep"') < 2:
            errs.append("推导卡少于 2 个 .dstep")
        if inner.count('class="dcheck"') < inner.count('class="dstep"'):
            errs.append("推导卡有步骤缺少 .dcheck")
    for s, e, inner in spans(h, "apply"):
        for key, label in (("apply-h", "卡头"), ("apply-q", "问题"), ("apply-use", "用法")):
            if key not in inner:
                errs.append("例题应用卡缺少 .%s（%s）" % (key, label))
        steps = inner.count('class="apply-step"')
        if steps < 3:
            errs.append("例题应用卡少于 3 个 .apply-step")
        if inner.count('class="as-why"') < steps:
            errs.append("例题应用卡有步骤缺少 .as-why")
        if 'class="ak"' not in inner or 'class="cover"' not in inner:
            errs.append("例题应用卡缺少 .ak 或 .cover")
    return errs

def main():
    files = sys.argv[1:] or sorted(f for f in glob.glob(os.path.join(ROOT, "sections", "*.html"))
                                    if not os.path.basename(f).startswith("_"))
    bad = 0
    for f in files:
        e = check(f)
        if e:
            bad += 1
            print("FAIL", os.path.basename(f))
            for x in e: print("   x", x)
        else:
            print("OK  ", os.path.basename(f))
    print("\n%d/%d 通过" % (len(files) - bad, len(files)))
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
