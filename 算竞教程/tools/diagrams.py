# -*- coding: utf-8 -*-
"""代码逻辑图 / 概念图解。

纯 HTML + CSS 渲染，不依赖任何外部库，离线可用。

用法（写在各节 SEC 列表里）：

    DIAG("flow", cap="二分答案的骨架", items=[
        "读入 l = 1, r = n，ans = -1",
        {"c": "int mid = (l + r) >> 1;", "t": "取中点"},
        {"q": "check(mid) 为真？", "yes": "ans = mid; r = mid - 1", "no": "l = mid + 1"},
        "l > r 时结束，输出 ans",
    ])

    DIAG("steps", cap="整体三个阶段", items=["建图", "BFS 分层", "统计答案"])

    DIAG("array", cap="前缀和", cells=["3", "1", "4", "1", "5"],
         idx=True, hl=[1, 2], marks={0: "l", 3: "r"})

    DIAG("matrix", cap="数字三角形", head_row=["1", "2", "3"],
         head_col=["1", "2"], rows=[["7"], ["3", "8"]], hl=[(1, 2)])

    DIAG("tree", cap="线段树的区间划分", root={
        "t": "[1, 8]", "kids": [
            {"t": "[1, 4]", "kids": [{"t": "[1, 2]"}, {"t": "[3, 4]"}]},
            {"t": "[5, 8]"},
        ]})

    DIAG("compare", cap="两种写法的差别",
         left=("正序", ["dp[j] 已被本行覆盖", "读到的是新值 → 错"]),
         right=("倒序", ["dp[j] 还是上一行", "读到的是旧值 → 对"]))
"""
import html as _html

_ESC = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}


def _e(s):
    return "".join(_ESC.get(ch, ch) for ch in str(s))


def _code(s):
    """行内代码：只转义，保留内容原样（用于代码片段）。"""
    return '<code>%s</code>' % _e(s)


# ---------------------------------------------------------------- 各类图
def _node(d, i):
    """flow 的一个节点。d 可以是 str 或 dict。"""
    if isinstance(d, str):
        return '<div class="dn">%s</div>' % _e(d)
    if "q" in d:
        head = '<div class="dn dq"><span class="dq-m">?</span>%s</div>' % _e(d["q"])
        arms = []
        if d.get("yes"):
            arms.append('<span class="arm ok"><i>是</i>%s</span>' % _e(d["yes"]))
        if d.get("no"):
            arms.append('<span class="arm no"><i>否</i>%s</span>' % _e(d["no"]))
        return head + ('<div class="darms">%s</div>' % "".join(arms) if arms else "")
    parts = []
    if d.get("c"):
        parts.append('<div class="dc">%s</div>' % _code(d["c"]))
    if d.get("t"):
        parts.append('<div class="dt">%s</div>' % _e(d["t"]))
    return '<div class="dn%s">%s</div>' % (" dhas-code" if d.get("c") else "", "".join(parts))


def _flow(cap, items):
    body = []
    for k, it in enumerate(items):
        if k:
            body.append('<div class="dar" aria-hidden="true"></div>')
        body.append(_node(it, k))
    return _fig("flow", cap, '<div class="dflow">%s</div>' % "".join(body))


def _steps(cap, items):
    body = []
    for k, it in enumerate(items):
        if k:
            body.append('<div class="dsa" aria-hidden="true"></div>')
        body.append('<div class="ds"><b>%d</b><span>%s</span></div>' % (k + 1, _e(it)))
    return _fig("steps", cap, '<div class="dsteps">%s</div>' % "".join(body))


def _array(cap, cells, idx=False, hl=None, marks=None, note=""):
    hl = set(hl or [])
    marks = marks or {}
    out = []
    for i, v in enumerate(cells):
        cls = "dcell" + (" hl" if i in hl else "")
        mk = '<u>%s</u>' % _e(marks[i]) if i in marks else ""
        ix = '<i>%d</i>' % i if idx else ""
        out.append('<div class="%s">%s<b>%s</b>%s</div>' % (cls, ix, _e(v), mk))
    body = '<div class="darr">%s</div>' % "".join(out)
    if note:
        body += '<div class="dnote">%s</div>' % _e(note)
    return _fig("array", cap, body)


def _matrix(cap, rows, head_row=None, head_col=None, hl=None, note="", offset=None):
    hl = set(map(tuple, hl or []))
    offset = offset or []
    ncol = max([len(r) + (offset[i] if i < len(offset) else 0) for i, r in enumerate(rows)]
               + [len(head_row or [])])
    grid = []
    if head_row:
        if head_col:
            grid.append('<div class="dmh"></div>')
        for j in range(ncol):
            grid.append('<div class="dmh">%s</div>' % (_e(head_row[j]) if j < len(head_row) else ""))
    for i, row in enumerate(rows):
        if head_col:
            grid.append('<div class="dmh dmhc">%s</div>' % (_e(head_col[i]) if i < len(head_col) else ""))
        for _ in range(offset[i] if i < len(offset) else 0):
            grid.append('<div class="dmc empty"></div>')
        for j in range(ncol - (offset[i] if i < len(offset) else 0)):
            v = row[j] if j < len(row) else ""
            cls = "dmc" + (" hl" if (i, j) in hl else "") + (" empty" if v == "" else "")
            grid.append('<div class="%s">%s</div>' % (cls, _e(v)))
    body = '<div class="dmatrix" style="--cols:%d">%s</div>' % (ncol, "".join(grid))
    if note:
        body += '<div class="dnote">%s</div>' % _e(note)
    return _fig("matrix", cap, body)


def _tree_node(d, out, depth, last, prefix):
    cls = "dtn" + (" leaf" if not d.get("kids") else "")
    out.append('<div class="dti" style="padding-left:%dpx">%s<span class="%s">%s</span></div>'
               % (depth * 20, prefix, cls, _e(d.get("t", ""))))
    kids = d.get("kids") or []
    for k, kid in enumerate(kids):
        _tree_node(kid, out, depth + 1, k == len(kids) - 1, "")


def _tree(cap, root, note=""):
    out = []
    _tree_node(root, out, 0, True, "")
    body = '<div class="dtree">%s</div>' % "".join(out)
    if note:
        body += '<div class="dnote">%s</div>' % _e(note)
    return _fig("tree", cap, body)


def _compare(cap, left, right, note=""):
    def col(tup, side):
        title, lines = tup
        items = "".join('<li>%s</li>' % _e(x) for x in lines)
        return ('<div class="dcmp %s"><div class="dcmp-h">%s</div><ul>%s</ul></div>'
                % (side, _e(title), items))
    body = '<div class="dcmp-wrap">%s%s</div>' % (col(left, "l"), col(right, "r"))
    if note:
        body += '<div class="dnote">%s</div>' % _e(note)
    return _fig("compare", cap, body)


def _fig(kind, cap, body):
    c = '<figcaption>%s</figcaption>' % _e(cap) if cap else ""
    return '<figure class="dia dia-%s">%s%s</figure>' % (kind, c, body)


# ---------------------------------------------------------------- 入口
def build(d):
    """把 {"dtype": ..., ...} 渲染成 HTML。"""
    k = d.get("dtype")
    cap = d.get("cap", "")
    try:
        if k == "flow":
            return _flow(cap, d.get("items") or [])
        if k == "steps":
            return _steps(cap, d.get("items") or [])
        if k == "array":
            return _array(cap, d.get("cells") or [], d.get("idx", False),
                          d.get("hl"), d.get("marks"), d.get("note", ""))
        if k == "matrix":
            return _matrix(cap, d.get("rows") or [], d.get("head_row"), d.get("head_col"),
                           d.get("hl"), d.get("note", ""), d.get("offset"))
        if k == "tree":
            return _tree(cap, d.get("root") or {}, d.get("note", ""))
        if k == "compare":
            return _compare(cap, d.get("left") or ("", []), d.get("right") or ("", []),
                            d.get("note", ""))
    except Exception as e:                                        # noqa: BLE001
        return '<!-- diagram error: %s -->' % _e(e)
    return "<!-- unknown diagram %s -->" % _e(k)
