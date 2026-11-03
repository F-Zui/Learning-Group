# -*- coding: utf-8 -*-
"""算法类模板的构建器。

做四件事（全部由 curriculum.py 驱动）：

1. 扫描每一节 NN.html（与 extra 里的题解页）：
     · 给正文块补上稳定锚点 id="bN"（已有 id 则沿用，且新块从已有最大编号 +1 开始）；
     · 记录每块纯文本与它所属的标题，供全文检索；
     · 采集「本节目录」条目（例题 / 新函数拆解 / 逐行拆解 / 数学补给 / 挑战题 …）。
2. 用采集到的条目重建每页的 <aside class="rtoc">（作者只留占位注释）。
3. 生成目录页 index.html。
4. 生成 assets/toc.js 与 assets/search-index.js。

用法：
    python tools/build.py
    python tools/build.py --no-index     # 只回填各页锚点与本节目录 + 检索索引
"""
import html as _html
import json
import os
import re
import sys
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curriculum as C  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# 会拿到 id="bN" 的标签（正文块）
ANCHOR_TAGS = {"p", "li", "td", "th", "pre", "h2", "h3", "h4"}
# 另外按 class 取锚点的块：div.t（标题）/ .fh 新函数卡头 / .sh 教学区块标题 / span.pn 例题名 …
ANCHOR_CLASSES = {"t", "tt", "tq", "fh", "sh", "pn", "mt", "rt", "ct", "sig", "io", "cap",
                  "dnote", "dc", "dt", "ds", "dn", "dmc"}
# 本节目录的层级：class 或标签 -> 层级
TITLE_LEVEL = {"pn": 1, "ct": 1, "mt": 1, "tt": 1, "h2": 1,
               "t": 2, "fh": 2, "sh": 2, "rt": 2, "h3": 2}

VOID = {"br", "img", "hr", "input", "meta", "link", "col", "area", "base", "embed",
        "source", "track", "wbr", "param"}
MAX_TEXT = 4000
MAX_PROSE = 600
MIN_LEN = 2
PLACE = "<!--BUILD:RTOC-->"
RTOC_RE = re.compile(r'<aside class="rtoc".*?</aside>\s*', re.S)


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def norm(s):
    return " ".join(s.replace("\u00a0", " ").split())


def _inject_id(raw, aid):
    raw = raw.rstrip()
    if raw.endswith("/>"):
        return raw[:-2].rstrip() + ' id="%s"/>' % aid
    return raw[:-1].rstrip() + ' id="%s">' % aid


class Scan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.out = []
        self.stack = []
        self.cur = None
        self.depth = -1
        self.n = 0
        self.blocks = []      # [{"id","hidx","t"}]
        self.headings = []    # 标题文本序列
        self.titles = []      # [(id, level, text)]
        self.cur_head = -1

    def handle_starttag(self, tag, attrs):
        raw = self.get_starttag_text() or ("<%s>" % tag)
        a = {k: (v or "") for k, v in attrs}
        cls = a.get("class", "").split()
        is_anchor = (tag in ANCHOR_TAGS) or (tag in ("div", "span", "a", "summary")
                                            and any(c in ANCHOR_CLASSES for c in cls))
        if self.cur is None and is_anchor:
            aid = a.get("id")
            if aid:
                m = re.match(r"b(\d+)$", aid)
                if m:
                    self.n = max(self.n, int(m.group(1)) + 1)
            else:
                aid = "b%d" % self.n
                self.n += 1
                raw = _inject_id(raw, aid)
            ent = {"id": aid, "hidx": self.cur_head, "t": "", "tag": tag,
                   "cls": cls, "level": self._level(tag, cls)}
            self.blocks.append(ent)
            self.cur = ent
            self.depth = len(self.stack)
        self.out.append(raw)
        if tag not in VOID:
            self.stack.append(tag)

    @staticmethod
    def _level(tag, cls):
        for c in cls:
            if c in TITLE_LEVEL and TITLE_LEVEL[c] == 1:
                return 1
        if tag == "h2":
            return 1
        for c in cls:
            if c in TITLE_LEVEL:
                return TITLE_LEVEL[c]
        if tag == "h3":
            return 2
        return 0

    def handle_startendtag(self, tag, attrs):
        self.out.append(self.get_starttag_text() or ("<%s/>" % tag))

    def handle_endtag(self, tag):
        if tag in VOID:
            self.out.append("</%s>" % tag)
            return
        while self.stack:
            if self.stack.pop() == tag:
                break
        if self.cur is not None and len(self.stack) <= self.depth:
            self._finish()
        self.out.append("</%s>" % tag)

    def handle_data(self, data):
        self.out.append(data)
        if self.cur is not None and len(self.cur["t"]) < MAX_TEXT:
            self.cur["t"] += data

    def handle_entityref(self, name):
        self.out.append("&%s;" % name)
        if self.cur is not None and len(self.cur["t"]) < MAX_TEXT:
            self.cur["t"] += _html.unescape("&%s;" % name)

    def handle_charref(self, name):
        self.out.append("&#%s;" % name)
        if self.cur is not None and len(self.cur["t"]) < MAX_TEXT:
            self.cur["t"] += _html.unescape("&#%s;" % name)

    def handle_comment(self, data):
        self.out.append("<!--%s-->" % data)

    def handle_decl(self, decl):
        self.out.append("<!%s>" % decl)

    def handle_pi(self, data):
        self.out.append("<?%s>" % data)

    def _finish(self):
        ent, self.cur = self.cur, None
        txt = norm(ent["t"])
        if len(txt) > MAX_PROSE:
            txt = txt[:MAX_PROSE] + "…"
        ent["t"] = txt
        if ent["level"]:
            self.headings.append(txt)
            ent["hidx"] = len(self.headings) - 1
            if txt:
                self.titles.append((ent["id"], ent["level"], txt))


def scan(html_text):
    p = Scan()
    # 预扫描已有锚点：新块从「已有最大编号 + 1」开始，重复构建不会撞 id。
    existing = [int(x) for x in re.findall(r'id="b(\d+)"', html_text)]
    if existing:
        p.n = max(existing) + 1
    p.feed(html_text)
    p.close()
    if p.cur is not None:
        p._finish()
    blocks = [e for e in p.blocks if (e["t"] and len(e["t"]) >= MIN_LEN) or e.get("level")]
    return "".join(p.out), blocks, p.headings, p.titles


def page_summary(html_text):
    m = re.search(r'<div class="sub">(.*?)</div>', html_text, re.S)
    return m.group(1).strip() if m else ""


def rtoc_html(summary, titles):
    items = "".join(
        '<a class="rt-i lv%d" href="#%s" data-t="%s">%s</a>' % (lv, i, i, esc(t))
        for i, lv, t in titles)
    return (
        '<aside class="rtoc" id="rtoc" aria-label="本节目录">'
        '<div class="rt-head"><span class="rt-title">本节目录</span>'
        '<button class="rt-close" id="rtClose" type="button" title="收起">&#187;</button></div>'
        '<div class="rt-sum">' + (summary or "本节提要") + '</div>'
        '<nav class="rt-body">' + items + '</nav>'
        '</aside>'
    )


def build_page(path):
    """重建一页：注入锚点 + 重建本节目录。返回 (块, 标题序列, 目录条目)。"""
    raw = open(path, encoding="utf-8").read()
    summary = page_summary(raw)
    has_rtoc = bool(RTOC_RE.search(raw))
    work = RTOC_RE.sub(PLACE + "\n", raw, count=1) if has_rtoc else raw

    new, blocks, headings, titles = scan(work)
    rtoc = rtoc_html(summary, titles)
    if has_rtoc:
        new = new.replace(PLACE + "\n", rtoc + "\n", 1)
    else:
        new = new.replace('<div class="nav">', rtoc + '\n<div class="nav">', 1)

    if new != raw:
        open(path, "w", encoding="utf-8", newline="\n").write(new)
    return blocks, headings, titles


def toc_js():
    groups = []
    for g in C.GROUPS:
        items = []
        for it in g["items"]:
            items.append({
                "id": it["id"], "title": it["title"],
                "file": "%02d.html" % it["id"], "level": it["level"],
                "kind": it.get("kind", "lesson"), "star": bool(it.get("star")),
            })
        groups.append({"name": g["name"], "items": items})
    total = sum(len(g["items"]) for g in C.GROUPS)
    mod = dict(C.MODULE)
    mod.setdefault("sidebarTitle", "全部 %d 节" % total)
    mod["heroSub"] = (C.MODULE.get("heroSub") or "").replace("CH2_FROM", str(C.CH2_FROM))
    course = {
        "total": total,
        "ch2From": C.CH2_FROM,
        "indexFile": "assets/search-index.js",
        "groups": groups,
        "extra": [{"file": e["file"], "title": e["title"]} for e in C.EXTRA],
    }
    return ("window.MODULE = " + json.dumps(mod, ensure_ascii=False) + ";\n"
            "window.COURSE = " + json.dumps(course, ensure_ascii=False, separators=(",", ":")) + ";\n")


# ---------------------------------------------------------------- 目录页
def toc_item(it):
    i = it["id"]
    kind = it.get("kind", "lesson")
    tag = ('<span class="badge">回顾</span>' if kind == "review"
           else '<span class="badge">模拟赛</span>' if kind == "mock" else "")
    keys = " ".join([it["title"]] + it.get("tags", []))
    ch2 = ('<label title="完成挑战2 后 ⭐ 变 🌟"><input type="checkbox" data-role="ch2" data-id="%d">🌟</label>' % i
           if i >= C.CH2_FROM else "")
    return (
        '<div class="toc-item" data-id="{i}" data-k="{keys}">'
        '<a class="no" href="{f}" style="min-width:34px">{no}</a>'
        '<a class="nm" href="{f}"><span class="stars"></span> {title} {tag}</a>'
        '<span class="badge diff">{lv}</span>'
        '<span class="toc-ctl"><label title="勾上表示已学（⭐）">'
        '<input type="checkbox" data-role="learned" data-id="{i}">⭐</label>{ch2}</span>'
        '</div>'
    ).format(i=i, keys=esc(keys), f="%02d.html" % i, no="%02d" % i,
             title=esc(it["title"]), tag=tag, lv=esc(it["level"]), ch2=ch2)


def index_html():
    total = sum(len(g["items"]) for g in C.GROUPS)
    parts = []
    for g in C.GROUPS:
        parts.append('<div class="toc-group">%s</div><div class="toc-list">' % esc(g["name"]))
        parts.extend(toc_item(it) for it in g["items"])
        parts.append("</div>")
    if C.EXTRA:
        parts.append('<div class="toc-group">题解 / 专题</div><div class="toc-list">')
        for e in C.EXTRA:
            parts.append(
                '<div class="toc-item" style="cursor:default">'
                '<a class="no" href="{f}" style="min-width:34px">题解</a>'
                '<a class="nm" href="{f}">{t}<span style="color:#5b6577;font-size:13px">　{note}</span></a>'
                '<span class="badge diff">{lv}</span></div>'.format(
                    f=e["file"], t=esc(e["title"]), note=esc(e.get("note", "")), lv=esc(e.get("level", ""))))
        parts.append("</div>")

    hero_sub = (C.MODULE.get("heroSub") or "").replace("CH2_FROM", str(C.CH2_FROM))
    ch2_note = "第 %d 节起额外多一个 🌟 勾选框（挑战 2）" % C.CH2_FROM
    return """<!doctype html>
<html lang="zh-CN"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>目录 · {title}</title>
<meta name="description" content="{sub}">
<link rel="stylesheet" href="assets/style.css">
</head><body data-lesson="index">
<div class="topbar"><div class="inner">
  <a href="index.html">← 目录</a>
  <span class="spacer"></span>
  <span id="pageMark" class="page-mark"></span>
  <span>全部 {total} 节</span>
  <span class="spacer"></span>
  <a href="index.html">{title}</a>
</div></div>
<div class="wrap">
<h1>{hero}</h1><div class="sub">{heroSub}</div><div class="progressbox"><b>我的进度</b>　<span id="idxProg">读表中…</span><div class="bar"><i id="idxBar" style="width:0%"></i></div><div style="font-size:13px;color:#5b6577;margin-top:6px">下面的列表可以自己勾：勾「已学」→ 该节打 ⭐；{ch2note}。刷新、关掉浏览器都不会丢。</div></div><div class="legend"><b>图例</b>　⭐ 已学　·　🌟 已学且完成挑战 2　·　<span class="badge diff">难度</span> 参考洛谷难度标签　·　<b>回顾</b> 阶段性综合训练　·　<b>模拟赛</b> 限时整套题</div><form id="srForm" class="sr-bar" autocomplete="off"><input id="q" class="toc-search" type="search" placeholder="输入关键词后按回车检索，如：前缀和 / 二分 / 二分答案"><button type="submit" class="sr-go">检索</button><button type="button" id="qClear" class="sr-clear" hidden title="退出检索">×</button></form><div class="sr-tip">回车检索 · Esc 退出 · <b>标题命中排在前面</b>，正文命中会显示所在节与上下文，点击直接跳到关键字位置</div><div id="srWrap" class="sr-wrap" hidden></div><div id="tocWrap">{parts}</div>
<div class="box tip" style="margin-top:18px"><div class="t">怎么打开 / 怎么用</div><p>直接双击 <code>index.html</code> 用浏览器打开即可，全部是纯静态页面，不需要联网、不需要服务器。题目链接会跳到对应 OJ 的题面页（需联网）。</p><p>顶部检索框支持全文搜索：输入关键词按回车，标题命中的节排在前面，正文命中会列出上下各一行，点击结果直接跳到该节并定位到关键字处（会自动展开折叠的题解）。</p><p>左下角「☰ 章节」会拉出侧边栏：可以在任意一页直接跳到别的节，也能在侧边栏里勾选「已学 / 挑战2」，和这一页的勾选是同一份数据（存在浏览器 localStorage）。</p></div>
<div class="legend" style="margin-top:26px"><b>怎么用这套教程</b><br>① 每节先看「新函数拆解」，看懂每个参数是什么；② 跟着例题的思路读代码，读完后<strong>关掉页面自己敲一遍</strong>；③ 做节末挑战题，先只看提示，卡住 20 分钟再看思路；④ 挑战 2 用来验证「真的会用」而不是「看懂了」；⑤ 做完回顾章再往下走，不要跳章。</div>
<div class="nav"><a class="disabled">已经在这一页了</a></div>
<footer>{footer}<br>
转载请注明出处；模板代码可直接用于比赛</footer>
</div>
<script src="assets/toc.js"></script>
<script src="assets/app.js"></script>
</body></html>
""".format(title=esc(C.MODULE["title"]), sub=esc(hero_sub),
           total=total, hero=esc(C.MODULE["heroTitle"]), heroSub=esc(hero_sub),
           ch2note=ch2_note, parts="".join(parts), footer=esc(C.MODULE["footer"]))


def search_js(docs):
    return "window.SEARCH_DOCS = " + json.dumps(docs, ensure_ascii=False, separators=(",", ":")) + ";\n"


def lesson_doc(it, blocks, headings):
    return {
        "f": "%02d.html" % it["id"], "n": it["id"], "no": "%02d" % it["id"],
        "t": it["title"], "title": it["title"], "core": "",
        "lv": it["level"], "tg": it.get("tags", []),
        "hs": headings, "b": [[b["id"], b["hidx"], b["t"]] for b in blocks],
    }


def extra_doc(e, path, blocks, headings):
    m = re.search(r"<h1[^>]*>(.*?)</h1>", open(path, encoding="utf-8").read(), re.S)
    title = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else e["title"]
    return {
        "f": e["file"], "n": None, "no": "题解", "t": title, "title": title,
        "core": "", "lv": e.get("level", ""), "tg": [],
        "hs": headings, "b": [[b["id"], b["hidx"], b["t"]] for b in blocks],
    }


def main():
    only_pages = "--no-index" in sys.argv
    docs, missing = [], []
    for _g, it in C.all_items():
        p = os.path.join(ROOT, "%02d.html" % it["id"])
        if not os.path.exists(p):
            missing.append(os.path.basename(p))
            continue
        blocks, headings, titles = build_page(p)
        docs.append(lesson_doc(it, blocks, headings))
        print("  %-10s blocks=%-4d 本节目录=%d" % (os.path.basename(p), len(blocks), len(titles)))
    for e in C.EXTRA:
        p = os.path.join(ROOT, e["file"])
        if not os.path.exists(p):
            missing.append(e["file"])
            continue
        blocks, headings, _titles = build_page(p)
        docs.append(extra_doc(e, p, blocks, headings))
        print("  %-10s blocks=%-4d（题解）" % (e["file"], len(blocks)))
    if missing:
        sys.exit("缺少页面：" + ", ".join(missing))

    with open(os.path.join(ROOT, "assets", "toc.js"), "w", encoding="utf-8", newline="\n") as f:
        f.write(toc_js())
    with open(os.path.join(ROOT, "assets", "search-index.js"), "w", encoding="utf-8", newline="\n") as f:
        f.write(search_js(docs))
    if not only_pages:
        with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8", newline="\n") as f:
            f.write(index_html())
    print("\n%d 页 · toc.js + search-index.js%s 已生成"
          % (len(docs), "" if only_pages else " + index.html"))


if __name__ == "__main__":
    main()
