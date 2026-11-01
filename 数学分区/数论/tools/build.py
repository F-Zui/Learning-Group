# -*- coding: utf-8 -*-
"""数学类模板：从 curriculum.py 生成 index.html、assets/toc.js 与 assets/search-index.js。

用法：
    python tools/build.py

生成物（不要手改）：
    index.html                 目录页
    assets/toc.js              window.MODULE + window.CURRICULUM
    assets/search-index.js     全文检索索引（同时给正文块注入 id="bN" 锚点）
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from curriculum import CHAPTERS, MODULE, PARTS, all_sections  # noqa: E402
import searchindex  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
STAR = ('<svg viewBox="0 0 24 24" width="12" height="12" fill="currentColor" aria-hidden="true">'
        '<path d="M12 2.6l2.9 5.9 6.5.9-4.7 4.6 1.1 6.5L12 17.4 6.2 20.5l1.1-6.5L2.6 9.4l6.5-.9z"/></svg>')

def toc_js():
    data = []
    for ch in CHAPTERS:
        data.append({
            "n": ch["n"], "part": ch["part"], "title": ch["title"], "sub": ch["sub"],
            "sections": [
                {"id": s[0], "title": s[1], "core": s[2], "diff": s[3],
                 "file": "sections/" + s[0].replace(".", "-") + ".html"}
                for s in ch["sections"]
            ],
        })
    return ("window.MODULE = " + json.dumps(MODULE, ensure_ascii=False) + ";\n"
            "window.CURRICULUM = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n")


def diff_dots(d):
    return '<span class="diff">' + "".join('<i class="%s"></i>' % ("on" if i < d else "") for i in range(3)) + "</span>"


def card(sid, title, core, diff, ch):
    return (
        '<article class="card" data-sec-card="{sid}">'
        '<input type="checkbox" data-check="{sid}" aria-label="标记 {sid} 完成">'
        '<a href="sections/{fn}.html">'
        '<div class="c-top"><span class="c-id">{sid}</span><span class="c-title">{title}</span>'
        '<span class="c-star" data-star>{star}</span></div>'
        '<div class="c-core">{core}</div>'
        '<div class="c-foot">{dots}<span>第 {ch} 章</span></div>'
        '</a></article>'
    ).format(sid=sid, fn=sid.replace(".", "-"), title=title, core=core, star=STAR, dots=diff_dots(diff), ch=ch)


def chapter_block(ch):
    cards = "".join(card(s[0], s[1], s[2], s[3], ch["n"]) for s in ch["sections"])
    return (
        '<section class="ch-block" data-ch="{n}">'
        '<div class="ch-head">'
        '<div class="ch-no">{n:02d}</div>'
        '<div><h3>{title}</h3><div class="ch-sub">{sub}</div></div>'
        '<div class="ch-side"><span class="ch-count" data-chcount="{n}">0/{cnt}</span>'
        '<span class="ch-mini"><i data-chbar="{n}"></i></span></div>'
        '</div>'
        '<div class="cards">{cards}</div>'
        '</section>'
    ).format(n=ch["n"], title=ch["title"], sub=ch["sub"], cnt=len(ch["sections"]), cards=cards)


def index_html():
    total = sum(len(c["sections"]) for c in CHAPTERS)
    blocks = []
    for part in PARTS:
        chs = [c for c in CHAPTERS if c["part"] == part["name"]]
        if not chs:
            continue
        blocks.append(
            '<div class="part-head"><span class="pn">Part {name}</span>'
            '<h2>{title}</h2><span class="pr">{rng}</span></div>'.format(
                name=part["name"], title=part["title"], rng=part["range"]))
        blocks.extend(chapter_block(c) for c in chs)

    tpl = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · 目录</title>
<meta name="description" content="{desc}">
<script src="assets/theme.js"></script>
<link rel="stylesheet" href="assets/style.css">
</head>
<body data-index>
<div class="idx-wrap">
  <header class="hero">
    <div>
      <div class="kicker">{kicker}</div>
      <h1>{title}</h1>
      <p class="lede">{lede}</p>
      <div class="hero-actions">
        <a class="btn primary" href="#" data-continue>开始学习 →</a>
        <a class="btn" href="#toc">浏览全部 {total} 节</a>
      </div>
    </div>
    <div class="ring" aria-label="学习进度">
      <svg viewBox="0 0 118 118" width="118" height="118">
        <circle class="bgc" cx="59" cy="59" r="50"></circle>
        <circle class="fgc" cx="59" cy="59" r="50" data-ring="50" style="stroke-dasharray:314.16;stroke-dashoffset:314.16"></circle>
      </svg>
      <div><div class="pc" data-ringtext>0%</div><div class="pl">完成</div></div>
    </div>
  </header>

  <div class="storage-warn" data-storage-warn style="display:none">
    当前浏览器禁止本地存储，勾选状态只在本次页面有效。建议用 <code>python -m http.server</code> 在本地打开，或使用“导出 / 导入”保存进度。
  </div>

  <div class="toolbar" id="toolbar">
    <form class="search" id="srForm" role="search">
      <input id="q" type="search" placeholder="{hint}" aria-label="检索全站" autocomplete="off">
      <button class="q-clear" id="qClear" type="button" aria-label="清空检索" hidden>×</button>
    </form>
    <button class="chip on" type="button" data-filter="all">全部</button>
    <button class="chip" type="button" data-filter="todo">未完成</button>
    <button class="chip" type="button" data-filter="done">已完成</button>
    <button class="icon-btn theme-btn" type="button" data-theme-toggle aria-label="切换深浅色" title="切换深浅色"></button>
    <span class="ch-count" data-count style="margin-left:auto">0 / {total}</span>
  </div>

  <div id="srWrap" class="sr-wrap" hidden></div>

  <div id="tocWrap">
  <div id="toc">
{blocks}
  </div>
  </div>

  <footer class="idx-foot">
    <span>进度保存在本机浏览器，不上传。</span>
    <a href="#" data-export>导出进度</a>
    <a href="#" data-import>导入进度</a>
    <a href="#" data-reset>重置</a>
  </footer>
</div>
<script src="assets/toc.js"></script>
<script src="assets/app.js"></script>
</body>
</html>
"""
    return (tpl.replace("{title}", MODULE["title"])
               .replace("{desc}", MODULE.get("description", MODULE["title"]))
               .replace("{hint}", MODULE.get("searchHint", "检索全站"))
               .replace("{kicker}", MODULE["kicker"])
               .replace("{lede}", MODULE["lede"])
               .replace("{total}", str(total))
               .replace("{blocks}", "\n".join(blocks)))


def search_js():
    docs = []
    for ch, sid, title, core, diff in all_sections():
        path = os.path.join(ROOT, "sections", sid.replace(".", "-") + ".html")
        raw = open(path, encoding="utf-8").read()
        new, entries = searchindex.build(raw)
        if new != raw:
            open(path, "w", encoding="utf-8", newline="").write(new)
        # 关键词行：<span>关键词：<b>洛必达</b> · <b>未定式</b></span>
        m = re.search(r"关键词：(.+?)</span>", raw)
        tags = []
        if m:
            tags = [re.sub(r"<[^>]+>", "", x).strip(" ·") for x in re.split(r"[·、]", m.group(1))]
            tags = [t for t in tags if t]
        docs.append({
            "f": "sections/" + sid.replace(".", "-") + ".html",
            "no": sid, "n": ch["n"], "t": sid + " " + title,
            "title": title, "core": core,
            "lv": "●" * diff + "○" * (3 - diff),
            "tg": tags,
            "b": [[e["id"], e["h"], e["t"]] for e in entries],
        })
    return "window.SEARCH_DOCS = " + json.dumps(docs, ensure_ascii=False, separators=(",", ":")) + ";\n"


def main():
    missing = [sid for _ch, sid, _t, _c, _d in all_sections()
               if not os.path.exists(os.path.join(ROOT, "sections", sid.replace(".", "-") + ".html"))]
    if missing:
        sys.exit("缺少正文文件：sections/" + ", sections/".join(x.replace(".", "-") + ".html" for x in missing))
    with open(os.path.join(ROOT, "assets", "toc.js"), "w", encoding="utf-8", newline="\n") as f:
        f.write(toc_js())
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(index_html())
    with open(os.path.join(ROOT, "assets", "search-index.js"), "w", encoding="utf-8", newline="\n") as f:
        f.write(search_js())
    n = sum(1 for _ in all_sections())
    print("sections:", n, "| index.html + toc.js + search-index.js written")


if __name__ == "__main__":
    main()
