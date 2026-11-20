# -*- coding: utf-8 -*-
"""生成比赛用的纸质板子：从 60 节的落地卡里抽「场景 + 完整代码 + 易错自查」。

用法：
    python tools/cheatsheet.py                 # 生成 板子.html（目录不带页码）
    python tools/cheatsheet.py --pages map.json # 按页码表生成目录
    python tools/cheatsheet.py --only toc      # 只输出目录（量页数用）
    python tools/cheatsheet.py --only 46       # 只输出第 46 节
"""
import html
import importlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import curriculum                                    # noqa: E402

TAG = re.compile(r"<[^>]+>")
IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")


def txt(s):
    s = TAG.sub("", str(s))
    s = html.unescape(s).replace("\u3000", " ")
    return re.sub(r"\s+", " ", s).strip()


def blocks_of(card):
    out = []
    for key in ("req", "problem", "end", "oi"):
        out.extend(card.get(key) or [])
    for st in card.get("steps") or []:
        for part in st[1:3]:
            out.extend(part or [])
    return [b for b in out if isinstance(b, dict)]


def codes_of(card):
    return [b["code"] for b in blocks_of(card) if b.get("kind") == "code" and b.get("code")]


def pick_program(card):
    codes = codes_of(card)
    if not codes:
        return "", False
    full = [c for c in codes if "#include" in c and "int main" in c]
    if full:
        return max(full, key=len), True
    return max(codes, key=len), False


def scenario_of(card):
    for b in card.get("oi") or []:
        if isinstance(b, dict) and b.get("kind") in ("p", "quote"):
            t = txt(b.get("text") or b.get("t") or "")
            if t:
                return t
    return txt(card.get("cover") or "")


def problem_of(card):
    m = re.search(r"problem/(P\d+)", repr(card.get("req")))
    return m.group(1) if m else ""


def warn_lines(lesson):
    out = []
    for b in lesson.get("sections") or []:
        if isinstance(b, dict) and b.get("kind") == "note" and b.get("level") == "warn":
            out.extend(b.get("lines") or [])
    return out


def pick_warns(card, warns, used, limit=3):
    """按标识符重合度排序挑相关易错；同一节里已用过的往后排，避免几张卡完全一样。"""
    code = " ".join(codes_of(card)) + " " + str(card.get("title", ""))
    ids = set(IDENT.findall(code))
    scored = []
    for i, w in enumerate(warns):
        plain = txt(w)
        hit = sum(1 for t in ids if t in plain)
        scored.append([hit, 0 if i in used else 1, -i, plain])
    scored.sort(key=lambda x: (-x[0], -x[1], -x[2]))
    picked = [s for s in scored if s[0] > 0][:limit]
    if len(picked) < 2:
        for s in scored:
            if s not in picked:
                picked.append(s)
            if len(picked) >= min(3, len(scored)):
                break
    out = []
    for s in picked:
        used.add(-s[2])
        out.append(s[3])
    return out


def is_review(lid):
    try:
        return curriculum.meta(lid)["kind"] in ("review", "mock")
    except Exception:                                   # noqa: BLE001
        return False


CSS = """
@page { size: A4; margin: 12mm 11mm 12mm 11mm; }
* { box-sizing: border-box; }
body { margin: 0; font: 10pt/1.45 "Microsoft YaHei", "PingFang SC", sans-serif;
       color: #111; background: #fff; }
h1 { font-size: 17pt; margin: 0 0 2mm; }
.sub { font-size: 9.5pt; color: #555; margin-bottom: 4mm; }
.toc { columns: 2; column-gap: 8mm; font-size: 8.4pt; margin: 0 0 4mm; break-after: page; }
.toc .tg { break-inside: avoid; margin: 0 0 1.5mm; }
.toc .t1 { font-weight: 700; border-bottom: 0.3pt dotted #bbb; padding-bottom: 0.4mm; }
.toc .t1 i { font-style: normal; font-weight: 400; color: #777; }
.toc .t2 { color: #333; padding-left: 4mm; font-size: 7.9pt; line-height: 1.32; }
.pg { float: right; font-variant-numeric: tabular-nums; color: #333; font-weight: 700;
      padding-left: 2mm; }
.lesson { margin-top: 4mm; padding-top: 2.4mm; border-top: 0.8pt dashed #999; }
.lesson.first { border-top: 0; margin-top: 0; padding-top: 0; }
.lh { border-bottom: 1.6pt solid #111; padding-bottom: 1.2mm; margin: 0 0 3mm;
      font-size: 12.5pt; font-weight: 700; }
.lh span { font-weight: 400; color: #666; font-size: 9.5pt; margin-left: 2mm; }
.card { margin: 0 0 4.6mm; }
.hd { break-inside: avoid; break-after: avoid; }
pre, .err { break-inside: avoid; }
.ch { font-size: 10.4pt; font-weight: 700; margin: 0 0 1.4mm; }
.ch i { font-style: normal; font-weight: 400; color: #555; font-size: 9pt; }
.row { font-size: 8.8pt; margin: 0.9mm 0; }
pre { margin: 1.2mm 0 1.5mm; padding: 2mm 2.6mm; background: #f5f6f8;
      border: 0.4pt solid #d3d8e0; border-radius: 1.4mm;
      font: 7.5pt/1.34 Consolas, "Cascadia Mono", monospace; white-space: pre-wrap;
      word-break: break-all; }
.snip { font-size: 7.6pt; color: #8a5a3a; margin-left: 1.5mm; font-weight: 400; }
.err { margin: 1mm 0 0; padding: 1.3mm 2mm; background: #fdf7f4; border-left: 2pt solid #b4573f;
       font-size: 8.5pt; }
.err div { margin: 0.4mm 0; }
.err b { color: #a33d24; }
@media print { body { -webkit-print-color-adjust: exact; } }
"""


def collect():
    lessons = []
    for lid in range(1, 61):
        L = importlib.import_module("lessons.l%02d" % lid).LESSONS[0]
        if is_review(lid):
            continue
        ws = [b for b in L["sections"] if isinstance(b, dict) and b.get("kind") == "walk"]
        if ws:
            lessons.append((lid, L, ws))
    return lessons


def lesson_html(lid, L, ws, first=False):
    out = ['<div class="lesson%s">' % (" first" if first else ""),
           '<div class="lh">%02d · %s<span>%d 张板子</span></div>'
           % (lid, html.escape(txt(L["title"])), len(ws))]
    warns = warn_lines(L)
    used = set()
    for c in ws:
        code, full = pick_program(c)
        sc = scenario_of(c)
        pid = problem_of(c)
        errs = pick_warns(c, warns, used)
        piece = ['<div class="card"><div class="hd">',
                 '<div class="ch">%s%s%s</div>' % (
                     html.escape(txt(c.get("title"))),
                     ('<i>（洛谷 %s）</i>' % pid) if pid else "",
                     "" if full or not code else '<span class="snip">代码片段</span>')]
        if sc:
            piece.append('<div class="row"><b>场景</b>　%s</div>' % html.escape(sc))
        cov = txt(c.get("cover") or "").replace("覆盖：", "")
        tags = "、".join(txt(t) for t in (c.get("tags") or []))
        if cov or tags:
            piece.append('<div class="row"><b>覆盖</b>　%s%s</div>'
                         % (html.escape(cov), ("　·　" + html.escape(tags)) if tags else ""))
        piece.append('</div>')
        if code:
            piece.append("<pre>%s</pre>" % html.escape(code))
        if errs:
            piece.append('<div class="err"><b>易错自查</b>%s</div>'
                         % "".join("<div>· %s</div>" % html.escape(e) for e in errs))
        piece.append("</div>")
        out.append("".join(piece))
    out.append("</div>")
    return "".join(out)


def toc_html(lessons, pages=None):
    items = []
    for lid, L, ws in lessons:
        kids = "".join('<div class="t2">· %s</div>' % html.escape(txt(c.get("title")))
                       for c in ws)
        if pages and str(lid) in pages:
            pg = '<span class="pg">%s</span>' % pages[str(lid)]
        else:
            pg = '<span class="pg">000</span>'   # 占位：宽度与真实页码一致，版式不跳
        items.append('<div class="tg"><div class="t1">%s%02d · %s　<i>%d</i></div>%s</div>'
                     % (pg, lid, html.escape(txt(L["title"])), len(ws), kids))
    return '<div class="toc">%s</div>' % "".join(items)


HEAD = ('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">'
        '<title>算法竞赛板子 · 速查</title><style>%s</style></head><body>')


def render(pages=None, only=None, upto=None):
    lessons = collect()
    if upto is not None:
        lessons = lessons[:int(upto)]
    head = HEAD % CSS
    if upto is not None:
        out = os.path.join(HERE, "_out_prefix.html")
    elif only == "toc":
        return head + toc_html(lessons, pages) + "</body></html>"
    if only is not None:
        for lid, L, ws in lessons:
            if str(lid) == str(only):
                return head + lesson_html(lid, L, ws, True) + "</body></html>"
        raise SystemExit("没有第 %s 节" % only)

    total_cards = sum(len(w) for _, _, w in lessons)
    doc = [head,
           "<h1>算法竞赛板子 · 速查</h1>",
           '<div class="sub">从 60 节课程的全部算法落地卡里抽出「场景 / 完整代码 / 易错自查」，'
           "顺序与课程一致。共 %d 节、%d 张板子；左侧是页码范围，比赛时按节号或标题直接翻。</div>"
           % (len(lessons), total_cards),
           toc_html(lessons, pages)]
    for n, (lid, L, ws) in enumerate(lessons):
        # 全书里每节都另起一页，页码才能按「目录页数 + 各节页数」精确累加
        doc.append(lesson_html(lid, L, ws, False))
    doc.append("</body></html>")
    return "".join(doc)


def main():
    pages = None
    only = None
    upto = None
    outpath = None
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--pages":
            pages = json.load(open(args[i + 1], encoding="utf-8"))
            i += 2
        elif args[i] == "--only":
            only = args[i + 1]
            i += 2
        elif args[i] == "--upto":
            upto = int(args[i + 1])
            i += 2
        elif args[i] == "--out":
            outpath = args[i + 1]
            i += 2
        else:
            i += 1
    doc = render(pages, only, upto)
    if outpath:
        out = outpath
    elif upto is not None:
        out = os.path.join(HERE, "_out_prefix.html")
    elif only == "toc":
        out = os.path.join(HERE, "_out_toc.html")
    elif only is not None:
        out = os.path.join(HERE, "_out_%s.html" % only)
    else:
        out = os.path.join(ROOT, "板子.html")
    open(out, "w", encoding="utf-8").write(doc)
    print(out)


if __name__ == "__main__":
    main()
