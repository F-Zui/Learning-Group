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
        if k == "mtree":
            return _mtree(cap, d.get("root") or {}, d.get("gap", 30),
                          d.get("row_h", 92), d.get("note", ""))
        if k == "btree":
            return _btree(cap, d.get("root") or {}, d.get("gap", 36),
                          d.get("row_h", 92), d.get("note", ""))
        if k == "stack":
            return _stack(cap, d.get("items") or [], d.get("top"), d.get("hl"),
                          d.get("note", ""), d.get("label", "栈顶"))
        if k == "queue":
            return _queue(cap, d.get("items") or [], d.get("head", 0), d.get("tail"),
                          d.get("hl"), d.get("note", ""), d.get("label", ("队头", "队尾")))
        if k == "rangebars":
            return _rangebars(cap, d.get("n") or 8, d.get("items") or [],
                              d.get("note", ""), d.get("hi_label", "覆盖区间"))
        if k == "compare":
            return _compare(cap, d.get("left") or ("", []), d.get("right") or ("", []),
                            d.get("note", ""))
    except Exception as e:                                        # noqa: BLE001
        return '<!-- diagram error: %s -->' % _e(e)
    return "<!-- unknown diagram %s -->" % _e(k)


# ---------------------------------------------------------------- 真·二叉树（SVG）
def _node_size(n):
    """节点尺寸：标题 + 若干小格。"""
    cells = n.get("cells") or []
    w = max(66, len(cells) * 28 + 14)
    h = 30 if not cells else 46
    return w, h


def _measure(n, gap):
    w, h = _node_size(n)
    n["_w"], n["_h"] = w, h
    kids = n.get("kids") or []
    if not kids:
        n["_sub"] = w
        return
    for k in kids:
        _measure(k, gap)
    total = sum(k["_sub"] for k in kids) + gap * (len(kids) - 1)
    n["_sub"] = max(w, total)


def _place(n, left, gap):
    n["_x"] = left + n["_sub"] / 2.0
    kids = n.get("kids") or []
    if not kids:
        return
    total = sum(k["_sub"] for k in kids) + gap * (len(kids) - 1)
    x = left + (n["_sub"] - total) / 2.0
    for k in kids:
        _place(k, x, gap)
        x += k["_sub"] + gap


def _btree(cap, root, gap=36, row_h=92, note="", kind="btree"):
    import copy
    n = copy.deepcopy(root)
    _measure(n, gap)
    _place(n, 0, gap)

    # 计算高度
    depth = {"v": 0}

    def walk(nn, d):
        depth["v"] = max(depth["v"], d)
        for k in nn.get("kids") or []:
            walk(k, d + 1)
    walk(n, 0)

    pad = 18
    W = int(n["_sub"] + pad * 2)
    H = int((depth["v"] + 1) * row_h + pad * 2 + 14)

    parts = ['<svg class="btree" viewBox="0 0 %d %d" width="%d" height="%d" role="img">'
             % (W, H, W, H)]

    # 先画连线（在节点下面）
    def edges(nn, d):
        cy = pad + d * row_h
        for k in nn.get("kids") or []:
            kx = k["_x"] + pad
            ky = pad + (d + 1) * row_h
            px = nn["_x"] + pad
            py = cy + nn["_h"]
            parts.append('<path class="bt-edge" d="M%.1f %.1f L%.1f %.1f" '
                         'marker-end="url(#bt-arrow)"/>' % (px, py, kx, ky - 18))
            if k.get("e"):
                mx, my = (px + kx) / 2.0, (py + ky - 18) / 2.0
                parts.append('<text class="bt-elab" x="%.1f" y="%.1f" text-anchor="middle">%s</text>'
                             % (mx + 9, my + 3, _e(k["e"])))
            edges(k, d + 1)
    parts.insert(1, '<defs><marker id="bt-arrow" viewBox="0 0 8 8" refX="6" refY="4" '
                    'markerWidth="6" markerHeight="6" orient="auto">'
                    '<path class="bt-arrow" d="M0 0 L8 4 L0 8 z"/></marker></defs>')
    edges(n, 0)

    # 再画节点
    def draw(nn, d):
        cx = nn["_x"] + pad
        y = pad + d * row_h
        w, h = nn["_w"], nn["_h"]
        x = cx - w / 2.0
        cells = nn.get("cells") or []
        label = nn.get("t", "")
        if cells:
            parts.append('<text class="bt-lab" x="%.1f" y="%.1f" text-anchor="middle">%s</text>'
                         % (cx, y - 10, _e(label)))
            cw = 26
            sx = cx - (len(cells) * cw) / 2.0
            parts.append('<rect class="bt-box" x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                         'rx="4"/>' % (sx - 4, y + 2, len(cells) * cw + 8, 30))
            for i, c in enumerate(cells):
                parts.append('<rect class="bt-cell" x="%.1f" y="%.1f" width="%d" height="24" '
                             'rx="3"/>' % (sx + i * cw + 1, y + 5, cw - 2))
                parts.append('<text class="bt-cv" x="%.1f" y="%.1f" text-anchor="middle">%s</text>'
                             % (sx + i * cw + cw / 2.0, y + 22, _e(c)))
        else:
            parts.append('<rect class="bt-box" x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                         'rx="5"/>' % (x, y + 2, w, 26))
            parts.append('<text class="bt-nv" x="%.1f" y="%.1f" text-anchor="middle">%s</text>'
                         % (cx, y + 20, _e(label)))
        for k in nn.get("kids") or []:
            draw(k, d + 1)
    draw(n, 0)
    parts.append("</svg>")
    body = "".join(parts)
    if note:
        body += '<div class="dnote">%s</div>' % _e(note)
    return _fig(kind, cap, body)


# ---------------------------------------------------------------- 区间覆盖条
def _mtree(cap, root, gap=30, row_h=92, note=""):
    """多叉树：kids 可以有任意多个，每个子节点可用 e 标边上的字符。"""
    return _btree(cap, root, gap, row_h, note, kind="mtree")


def _rangebars(cap, n, items, note="", hi_label="覆盖区间"):
    """items: [(标签, lo, hi, 值)]，1-based 闭区间。"""
    head = ['<div class="rb-head"><span class="rb-name">%s</span>' % _e(hi_label)]
    for i in range(1, n + 1):
        head.append('<span class="rb-idx">%d</span>' % i)
    head.append("</div>")
    rows = []
    for lab, lo, hi, val in items:
        cells = ['<div class="rb-row"><span class="rb-name">%s</span>' % _e(lab)]
        cells.append('<span class="rb-bar" style="grid-column:%d/%d">%s</span>'
                     % (int(lo) + 1, int(hi) + 2, _e(val)))
        cells.append("</div>")
        rows.append("".join(cells))
    body = ('<div class="rangebars" style="--n:%d">%s%s</div>'
            % (n, "".join(head), "".join(rows)))
    if note:
        body += '<div class="dnote">%s</div>' % _e(note)
    return _fig("rangebars", cap, body)


# ---------------------------------------------------------------- 线性结构状态
def _stack(cap, items, top=None, hl=None, note="", label="栈顶"):
    """竖排的栈：最后入栈的在最上面。"""
    hl = set(hl or [])
    if top is None:
        top = len(items) - 1
    rows = []
    for i in range(len(items) - 1, -1, -1):
        cls = "sk-box" + (" hl" if i in hl else "") + (" top" if i == top else "")
        tag = '<span class="sk-tag">%s</span>' % _e(label) if i == top else ""
        rows.append('<div class="sk-row"><span class="sk-i">%d</span>'
                    '<div class="%s">%s</div>%s</div>'
                    % (i, cls, _e(items[i]), tag))
    body = '<div class="stack">%s</div>' % "".join(rows)
    if note:
        body += '<div class="dnote">%s</div>' % _e(note)
    return _fig("stack", cap, body)


def _queue(cap, items, head=0, tail=None, hl=None, note="", label=("队头", "队尾")):
    """横排的队列：标出队头与队尾。"""
    hl = set(hl or [])
    if tail is None:
        tail = len(items) - 1
    cells = []
    for i, v in enumerate(items):
        cls = "dcell" + (" hl" if i in hl else "")
        mk = ""
        if i == head:
            mk += '<u class="q-head">%s</u>' % _e(label[0])
        if i == tail:
            mk += '<u class="q-tail">%s</u>' % _e(label[1])
        cells.append('<div class="%s"><i>%d</i><b>%s</b>%s</div>' % (cls, i, _e(v), mk))
    body = '<div class="darr">%s</div>' % "".join(cells)
    if note:
        body += '<div class="dnote">%s</div>' % _e(note)
    return _fig("queue", cap, body)
