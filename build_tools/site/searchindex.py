# -*- coding: utf-8 -*-
"""构建期全文索引：给正文块注入稳定锚点 id，并抽取可检索文本。

对渲染好的 HTML 片段做一次单遍扫描：
  · 给 <p> <li> <td> <th> <pre> <h2..h4> 以及若干 <div class="..."> 注入 id="b0"、"b1"……
  · 收集每块纯文本（去标签、反转义）与它所属的小标题
  · 其余标记原样输出，页面结构不变

返回 (新 HTML, 索引条目列表)。条目形如：
    {"id": "b7", "k": "p", "h": "例题怎么想", "t": "纯文本……"}
"""
import html as _html
from html.parser import HTMLParser

VOID = {"br", "img", "hr", "input", "meta", "link", "col", "area", "base",
        "embed", "source", "track", "wbr", "param", "keygen"}

ANCHOR_TAGS = {"p", "li", "td", "th", "pre", "h2", "h3", "h4", "blockquote"}
ANCHOR_DIV_CLASS = {"quote", "sh", "fh", "ct", "cap", "rt", "t", "io", "sig"}
HEADING_TAGS = {"h2", "h3", "h4"}
HEADING_DIV_CLASS = {"sh", "fh", "ct", "t"}

MAX_TEXT = 4000          # 收集时的硬上限
MAX_PROSE = 700          # 正文块入库上限（够显示上下文即可）
MAX_CODE = 900          # 代码块入库上限
MIN_LEN = 3              # 太短的块不入库（表格里 入门O(n) 之类）


def _classes(attrs):
    for k, v in attrs:
        if k == "class" and v:
            return set(v.split())
    return set()


def _inject_id(raw, aid):
    """在原始开始标签末尾插入 id="..."，保留其余属性与写法。"""
    raw = raw.rstrip()
    if raw.endswith("/>"):
        return raw[:-2].rstrip() + ' id="%s"/>' % aid
    return raw[:-1].rstrip() + ' id="%s">' % aid


def _norm(s):
    return " ".join(s.replace("\u00a0", " ").split())


class _Scanner(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.out = []
        self.entries = []
        self.cur = None            # 正在收集的条目
        self.anchor_depth = -1      # 该条目开始时的栈深
        self.stack = []
        self.heading = ""           # 最近的小标题
        self.next_id = 0            # 锚点编号（空块也占号，避免 id 冲突）

    # ------------------------------------------------------------ 标签
    def handle_starttag(self, tag, attrs):
        raw = self.get_starttag_text() or ("<%s>" % tag)
        if self.cur is None and self._want(tag, attrs):
            aid = "b%d" % self.next_id
            self.next_id += 1
            ent = {"id": aid, "k": tag,
                   "cls": sorted(_classes(attrs) & ANCHOR_DIV_CLASS),
                   "h": self.heading, "t": ""}
            self.entries.append(ent)
            self.cur = ent
            self.anchor_depth = len(self.stack)
            self.out.append(_inject_id(raw, aid))
        else:
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
        if self.cur is not None and len(self.stack) <= self.anchor_depth:
            self._finish()
        self.out.append("</%s>" % tag)

    # ------------------------------------------------------------ 文本
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

    # ------------------------------------------------------------ 内部
    @staticmethod
    def _want(tag, attrs):
        if tag in ANCHOR_TAGS:
            return True
        if tag == "div":
            return bool(_classes(attrs) & ANCHOR_DIV_CLASS)
        return False

    def _finish(self):
        ent, self.cur = self.cur, None
        txt = _norm(ent["t"])
        if not txt:
            self.entries.pop()
            return
        cap = MAX_CODE if ent["k"] == "pre" else MAX_PROSE
        if len(txt) > cap:
            txt = txt[:cap] + "…"
        if len(txt) < MIN_LEN and ent["k"] not in HEADING_TAGS:
            self.entries.pop()
            return
        ent["t"] = txt
        if ent["k"] in HEADING_TAGS:
            self.heading = txt
        elif ent["k"] == "div" and set(ent.get("cls") or []) & HEADING_DIV_CLASS:
            self.heading = txt


def build(html_text):
    """返回 (注入锚点后的 HTML, 索引条目列表)。"""
    p = _Scanner()
    p.feed(html_text)
    p.close()
    if p.cur is not None:
        p._finish()
    return "".join(p.out), [e for e in p.entries if e["t"]]
