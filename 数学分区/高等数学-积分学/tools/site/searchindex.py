# -*- coding: utf-8 -*-
"""给每节的正文块注入稳定锚点，并抽取全文检索条目。

对已写好的 HTML 做一遍扫描：
  · 给 <p> <li> <td> <th> <figcaption> <blockquote> <h2..h4> 注入 id（已有 id 则沿用）；
  · 记录每块的纯文本与它所属的小标题（最近一个 h2/h3）；
  · 返回 (新 HTML, 条目列表)。

条目形如 {"id": "b7", "k": "p", "h": "三、麦克劳林展开", "t": "纯文本……"}
"""
import html as _html
import re
from html.parser import HTMLParser

VOID = {"br", "img", "hr", "input", "meta", "link", "col", "area", "base",
        "embed", "source", "track", "wbr", "param", "keygen"}

ANCHOR_TAGS = {"p", "li", "td", "th", "figcaption", "blockquote", "h2", "h3", "h4"}
HEADING_TAGS = {"h2", "h3"}

MAX_TEXT = 3000
MAX_PROSE = 600
MIN_LEN = 4
NUM_PREFIX = "一二三四五六七八九十"


def _attrs(attrs):
    return {k: (v or "") for k, v in attrs}


def _inject_id(raw, aid):
    raw = raw.rstrip()
    if raw.endswith("/>"):
        return raw[:-2].rstrip() + ' id="%s"/>' % aid
    return raw[:-1].rstrip() + ' id="%s">' % aid


def _norm(s):
    return " ".join(s.replace("\u00a0", " ").split())


def _clean_heading(s):
    s = _norm(s)
    i = 0
    while i < len(s) and s[i] in NUM_PREFIX:
        i += 1
    if 0 < i < len(s) and s[i] in "、．. ":
        i += 1
    return s[i:].strip() or s


class Scanner(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.out = []
        self.entries = []
        self.cur = None
        self.depth = -1
        self.stack = []
        self.heading = ""
        self.n = 0

    def handle_starttag(self, tag, attrs):
        raw = self.get_starttag_text() or ("<%s>" % tag)
        a = _attrs(attrs)
        if self.cur is None and tag in ANCHOR_TAGS:
            aid = a.get("id") or ("b%d" % self.n)
            if a.get("id"):
                m = re.match(r"b(\d+)$", aid)
                if m:
                    self.n = max(self.n, int(m.group(1)) + 1)
            else:
                self.n += 1
                raw = _inject_id(raw, aid)
            ent = {"id": aid, "k": tag, "h": self.heading, "t": ""}
            self.entries.append(ent)
            self.cur = ent
            self.depth = len(self.stack)
        self.out.append(raw)
        if tag not in VOID:
            self.stack.append(tag)

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
        txt = _norm(ent["t"])
        if not txt:
            self.entries.pop()
            return
        if len(txt) > MAX_PROSE:
            txt = txt[:MAX_PROSE] + "…"
        if len(txt) < MIN_LEN and ent["k"] not in HEADING_TAGS:
            self.entries.pop()
            return
        ent["t"] = txt
        if ent["k"] in HEADING_TAGS:
            self.heading = _clean_heading(txt)


def build(html_text):
    p = Scanner()
    p.feed(html_text)
    p.close()
    if p.cur is not None:
        p._finish()
    return "".join(p.out), [e for e in p.entries if e["t"]]
