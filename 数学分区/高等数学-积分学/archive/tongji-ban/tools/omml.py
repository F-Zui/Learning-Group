# -*- coding: utf-8 -*-
"""
omml.py —— 数学公式 -> OMML (Office Math Markup Language) 转换器

把课件源文件中的公式记法转换为 Word「插入-公式」所生成的 OMML，
从而得到上下叠置的分式、真正的上下角标、根式与求和号。

处理链：
    normalize()  源记法  ->  规范形式（结构记号 + Unicode 字符）
    tokenize()   规范形式 ->  记号流
    Parser       记号流   ->  语法树
    emit()       语法树   ->  OMML XML

规范形式中的结构记号：
    \\x01 ... \\x02      结构参数分组（分式的分子/分母、上下标的内容等）
    \\sqrt  \\root  \\lim   命令
    _ ^ /                上下标与除法
其余字符（α β ε → ∞ ≤ · 等）原样进入 OMML 的 m:t。
"""

import re

G_OPEN = "\x01"
G_CLOSE = "\x02"

M_NS = 'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"'

# ------------------------------------------------------------------ 上下标反向映射
_SUB_FWD = {
    "0": "\u2080", "1": "\u2081", "2": "\u2082", "3": "\u2083", "4": "\u2084",
    "5": "\u2085", "6": "\u2086", "7": "\u2087", "8": "\u2088", "9": "\u2089",
    "+": "\u208a", "-": "\u208b", "\u2212": "\u208b", "=": "\u208c",
    "(": "\u208d", ")": "\u208e",
    "a": "\u2090", "e": "\u2091", "h": "\u2095", "i": "\u1d62", "j": "\u2c7c",
    "k": "\u2096", "l": "\u2097", "m": "\u2098", "n": "\u2099", "o": "\u2092",
    "p": "\u209a", "r": "\u1d63", "s": "\u209b", "t": "\u209c", "u": "\u1d64",
    "v": "\u1d65", "x": "\u2093",
}
_SUP_FWD = {
    "0": "\u2070", "1": "\u00b9", "2": "\u00b2", "3": "\u00b3", "4": "\u2074",
    "5": "\u2075", "6": "\u2076", "7": "\u2077", "8": "\u2078", "9": "\u2079",
    "+": "\u207a", "-": "\u207b", "\u2212": "\u207b", "=": "\u207c",
    "(": "\u207d", ")": "\u207e", "n": "\u207f", "i": "\u2071", "k": "\u1d4f",
}
SUB_REV = {v: k for k, v in _SUB_FWD.items()}
SUP_REV = {v: k for k, v in _SUP_FWD.items()}

SUP_CLASS = "".join(re.escape(c) for c in SUP_REV)
SUB_CLASS = "".join(re.escape(c) for c in SUB_REV)

# 直立体函数名（长名在前，便于最长匹配）
FUNCS = sorted([
    "arcsin", "arccos", "arctan", "arccot", "sinh", "cosh", "tanh",
    "sin", "cos", "tan", "cot", "sec", "csc",
    "ln", "log", "exp", "lim", "max", "min",
    "arsh", "arch", "arth", "sh", "ch", "th",
], key=len, reverse=True)

NARY = {"\u03a3": "\u2211", "\u2211": "\u2211", "\u220f": "\u220f"}

REL_OPS = set("=<>≤≥≠≈∼~⟹⟺→∈⊆⊂∪∩±∓∝≡≪≫")

# 常见 LaTeX 记号 -> Unicode，便于源文件书写更宽容
LATEX_SYMBOLS = {
    "\\iff": "⟺", "\\Longleftrightarrow": "⟺", "\\Leftrightarrow": "⟺",
    "\\implies": "⟹", "\\Longrightarrow": "⟹", "\\Rightarrow": "⟹",
    "\\to": "→", "\\rightarrow": "→", "\\infty": "∞",
    "\\in": "∈", "\\notin": "∉", "\\subset": "⊂", "\\subseteq": "⊆",
    "\\cup": "∪", "\\cap": "∩",
    "\\le": "≤", "\\leq": "≤", "\\ge": "≥", "\\geq": "≥", "\\ne": "≠", "\\neq": "≠",
    "\\approx": "≈", "\\equiv": "≡", "\\sim": "∼",
    "\\pm": "±", "\\mp": "∓", "\\cdot": "·", "\\times": "×", "\\div": "÷",
    "\\alpha": "α", "\\beta": "β", "\\gamma": "γ", "\\delta": "δ",
    "\\varepsilon": "ε", "\\epsilon": "ε", "\\zeta": "ζ", "\\eta": "η",
    "\\theta": "θ", "\\mu": "μ", "\\nu": "ν", "\\xi": "ξ", "\\rho": "ρ",
    "\\sigma": "σ", "\\tau": "τ", "\\phi": "φ", "\\varphi": "φ",
    "\\chi": "χ", "\\psi": "ψ", "\\omega": "ω",
    "\\Gamma": "Γ", "\\Delta": "Δ", "\\Theta": "Θ", "\\Lambda": "Λ",
    "\\Sigma": "Σ", "\\Phi": "Φ", "\\Psi": "Ψ", "\\Omega": "Ω",
    "\\sum": "Σ", "\\prod": "∏", "\\int": "∫",
    "\\cdots": "…", "\\ldots": "…", "\\dots": "…",
    "\\quad": "　", "\\qquad": "　", "\\,": " ", "\\;": " ", "\\!": "",
    "\\{": "{", "\\}": "}", "\\ ": " ",
}


# ================================================================ 工具
def _is_letter(ch):
    """仅把拉丁字母与希腊字母视为标识符（排除中文）。"""
    if ch.isascii() and ch.isalpha():
        return True
    o = ord(ch)
    return 0x0370 <= o <= 0x03FF or 0x1F00 <= o <= 0x1FFF


def _match_brace(s, i, op, cl):
    """s[i] == op，返回匹配的 cl 的下标；失败返回 -1。"""
    depth = 0
    while i < len(s):
        if s[i] == op:
            depth += 1
        elif s[i] == cl:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def _match_paren(s, i, op="(", cl=")"):
    return _match_brace(s, i, op, cl)


# ================================================================ 规范化
def normalize(s):
    """把课件源记法规范化为带结构记号的形式。"""
    # 0) LaTeX 记号的宽容处理：先换长命令，再换单字符转义
    for _k in sorted(LATEX_SYMBOLS, key=len, reverse=True):
        if _k in s:
            s = s.replace(_k, LATEX_SYMBOLS[_k])
    s = s.replace("\u2009", " ")

    # 1-2) 根式：ⁿ√(...) / ⁿ√x / √(...) / √原子（合并为一次扫描，避免重复内容）
    out = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\u221a":
            deg = None
            if out and out[-1] in SUP_REV:
                deg = SUP_REV[out.pop()]
            j = i + 1
            while j < len(s) and s[j] == " ":
                j += 1
            body = None
            nxt = i + 1
            if j < len(s) and s[j] == "(":
                k = _match_paren(s, j)
                if k > 0:
                    body = s[j + 1:k]
                    nxt = k + 1
            if body is None and j < len(s):
                k = j
                if s[j].isdigit():
                    while k < len(s) and (s[k].isdigit() or s[k] == "."):
                        k += 1
                else:
                    k = j + 1
                body = s[j:k]
                nxt = k
            if body is None:
                out.append("\u221a")
                i += 1
                continue
            if deg is None:
                out.append("\\sqrt%s%s%s" % (G_OPEN, body, G_CLOSE))
            else:
                out.append("\\root%s%s%s%s%s%s" % (G_OPEN, deg, G_CLOSE, G_OPEN, body, G_CLOSE))
            i = nxt
            continue
        out.append(c)
        i += 1
    s = "".join(out)

    # 3) lim(...) -> \lim⟨...⟩
    def limrepl(m):
        rest = s[m.end() - 1:]
        j = _match_paren(rest, 0)
        if j > 0:
            return "\\lim%s%s%s" % (G_OPEN, rest[1:j], G_CLOSE)
        return "lim"
    s = re.sub(r"\blim(?=\()", lambda m: "\x00LIM\x00", s)
    s = re.sub(r"\x00LIM\x00\(", lambda m: limrepl_at(s, m), s) if False else s
    # 上面的替换无法拿到全局下标，改为逐字符扫描
    s = s.replace("\x00LIM\x00", "lim")
    out = []
    i = 0
    while i < len(s):
        if s.startswith("lim(", i) and (i == 0 or not _is_letter(s[i - 1])):
            j = _match_paren(s, i + 3)
            if j > 0:
                out.append("\\lim%s%s%s" % (G_OPEN, s[i + 4:j], G_CLOSE))
                i = j + 1
                continue
        out.append(s[i])
        i += 1
    s = "".join(out)

    # 4) 括号形式的上下标：^(...) ^{...} _(...) _{...}
    s = _brace_script(s, "^")
    s = _brace_script(s, "_")

    # 5) Unicode 上下标连续段 -> ^{...} / _{...}
    s = re.sub("([%s]+)" % SUP_CLASS,
               lambda m: "^%s%s%s" % (G_OPEN, "".join(SUP_REV[c] for c in m.group(1)), G_CLOSE),
               s)
    s = re.sub("([%s]+)" % SUB_CLASS,
               lambda m: "_%s%s%s" % (G_OPEN, "".join(SUB_REV[c] for c in m.group(1)), G_CLOSE),
               s)

    # 6) 单字符上下标：x^m  x_n
    s = re.sub(r"([\^_])([A-Za-z0-9])",
               lambda m: "%s%s%s%s" % (m.group(1), G_OPEN, m.group(2), G_CLOSE), s)

    # 7) 除法符号两侧空格归一
    s = re.sub(r"\s*/\s*", "/", s)
    return s


def limrepl_at(s, m):  # 占位（未使用）
    return m.group(0)


def _brace_script(s, mark):
    """把 mark(...) / mark{...} 转为 mark⟨...⟩（支持嵌套括号）。"""
    out = []
    i = 0
    while i < len(s):
        if s[i] == mark and i + 1 < len(s) and s[i + 1] in "({":
            op = s[i + 1]
            cl = ")" if op == "(" else "}"
            j = _match_brace(s, i + 1, op, cl)
            if j > 0:
                out.append("%s%s%s%s" % (mark, G_OPEN, s[i + 2:j], G_CLOSE))
                i = j + 1
                continue
        out.append(s[i])
        i += 1
    return "".join(out)


# ================================================================ 词法
def tokenize(s):
    toks = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == G_OPEN or c == G_CLOSE:
            toks.append(("grp", c))
            i += 1
        elif c == "\\":
            m = re.match(r"\\([A-Za-z]+)", s[i:])
            if m:
                toks.append(("cmd", m.group(1)))
                i += m.end()
            else:
                toks.append(("chr", c))
                i += 1
        elif _is_letter(c):
            j = i
            while j < n and _is_letter(s[j]):
                j += 1
            word = s[i:j]
            k = 0
            while k < len(word):
                hit = None
                for f in FUNCS:
                    if word.startswith(f, k):
                        hit = f
                        break
                if hit:
                    toks.append(("func", hit))
                    k += len(hit)
                else:
                    toks.append(("id", word[k]))
                    k += 1
            i = j
        elif c.isdigit():
            j = i
            while j < n and (s[j].isdigit() or s[j] == "."):
                j += 1
            toks.append(("num", s[i:j]))
            i = j
        elif c == " ":
            i += 1
        else:
            toks.append(("chr", c))
            i += 1
    return toks


# ================================================================ 语法
def _tok_text(tok):
    """把记号还原为字面文本（用于无法推进时的兜底）。"""
    kind, val = tok
    if kind == "grp":
        return ""
    if kind == "cmd":
        return "\\" + val
    return val


def _unwrap(node):
    """分式的分子/分母若为圆括号组，去掉多余的括号（叠置分式本身已起分组作用）。"""
    if (isinstance(node, tuple) and node[0] == "dlm"
            and node[1] == "(" and node[2] == ")"):
        body = node[3]
        if isinstance(body, tuple) and body[0] == "seq" and len(body[1]) == 1:
            body = body[1][0]
        return body
    return node


class Parser(object):
    def __init__(self, toks):
        self.t = toks
        self.i = 0
        self.limit = len(toks)   # 竖线配对不得越过当前绝对值组的终止位置

    def peek(self, k=0):
        j = self.i + k
        return self.t[j] if j < len(self.t) else None

    def eat(self, kind=None, val=None):
        tok = self.peek()
        if tok is None:
            return None
        if kind and tok[0] != kind:
            return None
        if val is not None and tok[1] != val:
            return None
        self.i += 1
        return tok

    # ---- 顶层：关系式
    def parse(self):
        seq = self.p_rel()
        if self.i < len(self.t):
            # 兜底：剩余记号顺序拼接，避免丢内容（带进度保证）
            rest = self.parse_rest()
            return ("seq", [seq, rest] if rest else [seq])
        return seq

    def parse_rest(self):
        items = []
        while self.i < len(self.t):
            before = self.i
            items.append(self.p_atom_with_scripts())
            if self.i == before:
                items.append(("txt", _tok_text(self.t[self.i])))
                self.i += 1
        return ("seq", items) if items else None

    def p_rel(self):
        items = [self.p_prefix()]
        while True:
            tok = self.peek()
            if tok and tok[0] == "chr" and tok[1] in REL_OPS:
                self.i += 1
                items.append(("txt", tok[1]))
                items.append(self.p_prefix())
            elif tok and tok[0] == "chr" and tok[1] == "\u3000":
                # 表意空格：分隔两个并列的结论
                self.i += 1
                items.append(("txt", "\u3000"))
                items.append(self.p_prefix())
            else:
                break
        return ("seq", items)

    def p_prefix(self):
        """lim⟨...⟩ 是低优先级前缀：它作用于随后的整个表达式，不属于分式的分子。"""
        tok = self.peek()
        if tok and tok[0] == "cmd" and tok[1] == "lim":
            nxt = self.peek(1)
            if nxt and nxt[0] == "grp" and nxt[1] == G_OPEN:
                self.i += 2
                inner = self.p_rel()
                self.eat("grp", G_CLOSE)
                return ("seq", [("limlow", inner), self.p_prefix()])
        return self.p_add()

    def p_add(self):
        items = [self.p_mul()]
        while True:
            tok = self.peek()
            if tok and tok[0] == "chr" and tok[1] in "+-\u2212\u00b1":
                # 一元正负号归入下一项
                self.i += 1
                items.append(("txt", tok[1]))
                items.append(self.p_mul())
            else:
                break
        return ("seq", items)

    def p_mul(self):
        items = [self.p_div()]
        while True:
            tok = self.peek()
            if tok and tok[0] == "chr" and tok[1] in "\u00b7\u00d7":
                self.i += 1
                items.append(("txt", tok[1]))
                items.append(self.p_div())
            else:
                break
        return ("seq", items)

    def p_div(self):
        num = self.p_chain()
        while self.peek() and self.peek()[0] == "chr" and self.peek()[1] == "/":
            self.i += 1
            den = self.p_chain()
            num = ("frac", _unwrap(num), _unwrap(den))
        return num

    def p_chain(self):
        items = []
        while True:
            tok = self.peek()
            if tok is None:
                break
            if tok[0] == "grp" and tok[1] == G_CLOSE:
                break
            if tok[0] == "chr" and (tok[1] in "/=<>+\u2212-\u00b7\u00d7"
                                    or tok[1] in REL_OPS or tok[1] in ")]}"
                                    or tok[1] == "\u3000"
                                    or (tok[1] == "|" and self.i >= self.limit)):
                break
            items.append(self.p_atom_with_scripts())
        if not items:
            return ("seq", [])
        if len(items) == 1:
            return items[0]
        return ("seq", items)

    def p_atom_with_scripts(self):
        base = self.p_primary()
        sub = sup = None
        while True:
            tok = self.peek()
            if tok and tok[0] == "chr" and tok[1] in "^_":
                self.i += 1
                arg = self.p_script_arg()
                if tok[1] == "^":
                    sup = arg
                else:
                    sub = arg
            else:
                break
        if sub is not None or sup is not None:
            return self.make_script(base, sub, sup)
        return base

    def make_script(self, base, sub, sup):
        # 求和号 / 连乘号 -> n 元运算符
        if base and base[0] == "txt" and base[1] in NARY:
            ch = NARY[base[1]]
            body = self.p_nary_body()
            return ("nary", ch, sub, sup, body)
        if sub is not None and sup is not None:
            return ("subsup", base, sub, sup)
        if sup is not None:
            return ("sup", base, sup)
        return ("sub", base, sub)

    def p_nary_body(self):
        """求和号的被求和项：紧随其后的乘除链。"""
        tok = self.peek()
        if tok is None or (tok[0] == "grp" and tok[1] == G_CLOSE):
            return ("seq", [])
        if tok[0] == "chr" and tok[1] in "=<>+\u2212-\u00b7\u00d7" + "".join(REL_OPS):
            return ("seq", [])
        return self.p_div()

    def p_script_arg(self):
        tok = self.peek()
        if tok and tok[0] == "grp" and tok[1] == G_OPEN:
            self.i += 1
            inner = self.p_rel()
            self.eat("grp", G_CLOSE)
            return inner
        return self.p_atom_with_scripts()

    def p_primary(self):
        tok = self.peek()
        if tok is None:
            return ("seq", [])
        kind, val = tok

        if kind == "grp":
            if val == G_OPEN:
                self.i += 1
                inner = self.p_rel()
                self.eat("grp", G_CLOSE)
                return inner
            self.i += 1
            return ("txt", "")

        if kind == "cmd":
            self.i += 1
            if val == "lim":
                nxt = self.peek()
                if nxt and nxt[0] == "grp" and nxt[1] == G_OPEN:
                    self.i += 1
                    inner = self.p_rel()
                    self.eat("grp", G_CLOSE)
                    return ("limlow", inner)
                return ("up", "lim")
            if val == "sqrt":
                nxt = self.peek()
                if nxt and nxt[0] == "grp" and nxt[1] == G_OPEN:
                    self.i += 1
                    inner = self.p_rel()
                    self.eat("grp", G_CLOSE)
                    return ("rad", None, inner)
                return ("txt", "\u221a")
            if val == "root":
                d = self.p_script_arg()
                b = self.p_script_arg()
                return ("rad", d, b)
            return ("up", val)

        if kind == "func":
            self.i += 1
            return ("up", val)

        if kind == "num":
            self.i += 1
            return ("txt", val)

        if kind == "id":
            self.i += 1
            return ("txt", val)

        # chr
        if val == "|":
            # 绝对值：与同一层内最近的另一条竖线配对，形成可自动拉伸的定界符
            depth = 0
            j = self.i + 1
            end = -1
            stop = min(len(self.t), self.limit)
            while j < stop:
                k2, v2 = self.t[j]
                if k2 == "grp":
                    depth += 1 if v2 == G_OPEN else -1
                    if depth < 0:
                        break
                elif k2 == "chr" and v2 in "([{":
                    depth += 1
                elif k2 == "chr" and v2 in ")]}":
                    if depth == 0:
                        break
                    depth -= 1
                elif k2 == "chr" and v2 == "|" and depth == 0:
                    end = j
                    break
                j += 1
            if end > 0:
                self.i += 1
                saved = self.limit
                self.limit = end
                items = []
                while self.i < end:
                    before = self.i
                    items.append(self.p_rel())
                    if self.i == before:
                        items.append(("txt", _tok_text(self.t[self.i])))
                        self.i += 1
                self.limit = saved
                self.i = end + 1
                body = ("seq", items) if len(items) != 1 else items[0]
                return ("dlm", "|", "|", body)
            self.i += 1
            return ("txt", "|")

        if val in "([{":
            close = {"(": ")", "[": "]", "{": "}"}[val]
            self.i += 1
            items = []
            while True:
                nxt = self.peek()
                if nxt is None or (nxt[0] == "grp" and nxt[1] == G_CLOSE):
                    break
                if nxt[0] == "chr" and nxt[1] in ")]}":
                    break
                before = self.i
                items.append(self.p_rel())
                if self.i == before:
                    # 无法推进：按字面量收下，避免死循环
                    items.append(("txt", _tok_text(nxt)))
                    self.i += 1
            self.eat("chr", close)
            body = ("seq", items) if len(items) != 1 else items[0]
            return ("dlm", val, close, body)
        if val == "}":
            self.i += 1
            return ("txt", "}")
        self.i += 1
        return ("txt", val)


# ================================================================ OMML 生成
def _x(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _rpr(upright=False):
    r = '<w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/>'
    if upright:
        return '<w:rPr>%s</w:rPr>' % r
    return '<w:rPr>%s</w:rPr>' % r


_CUR = {"highlight": False}


def _run(text, upright=False):
    if text == "":
        return ""
    sty = '<m:rPr><m:sty m:val="p"/></m:rPr>' if upright else ""
    # 与正文使用同一种底纹实现，避免深浅不一、边界错位
    hl = '<w:shd w:val="clear" w:color="auto" w:fill="FFF2A8"/>' if _CUR["highlight"] else ""
    sp = ' xml:space="preserve"' if text != text.strip() else ""
    return ('<m:r>%s<w:rPr><w:rFonts w:ascii="Cambria Math" '
            'w:hAnsi="Cambria Math"/>%s</w:rPr><m:t%s>%s</m:t></m:r>'
            % (sty, hl, sp, _x(text)))


# 用于分隔函数名与自变量、以及相邻变量之间的间隔
THIN = "\u2009"


def _arg(node):
    return emit(node)


def _kind(node):
    """判定节点在"是否与前后的符号粘连"意义上的类别。"""
    if node is None:
        return "other"
    k = node[0]
    if k == "up":
        return "func"
    if k == "txt":
        s = (node[1] or "").strip()
        if not s:
            return "other"
        if s[-1].isdigit():
            return "num"
        if len(s) == 1 and _is_letter(s):
            return "var"
        return "other"
    if k in ("sup", "sub", "subsup"):
        return _kind(node[1])
    return "other"


def _base_of(node):
    """穿透上下标包装，取得其基底节点。"""
    while node is not None and node[0] in ("sup", "sub", "subsup"):
        node = node[1]
    return node


def _join_sep(prev, nxt):
    """判断相邻两个节点之间应插入的间隔（空串表示紧贴）。"""
    kp, kc = _kind(prev), _kind(nxt)
    if kp == "func":
        if kc in ("func", "var", "num"):
            return THIN                       # lim f(x)、sin x、ln x
        # lim[ ... ]、lim[ ... ]^n、max{ ... }：函数名后接非圆括号的定界符也要留白
        b = _base_of(nxt)
        if b is not None and b[0] == "dlm" and b[1] != "(":
            return THIN
        return ""
    if kp == "var" and kc == "var":
        return "\u00b7"                        # 两个变量相乘：a·b
    if kp == "var" and kc == "func":
        return THIN                           # x sin x
    return ""


def _emit_seq(children):
    """顺序拼接子节点，并在函数名与自变量、相邻变量之间补足间隔。"""
    out = []
    for idx, ch in enumerate(children):
        if idx:
            sep = _join_sep(children[idx - 1], ch)
            if sep:
                out.append(_run(sep))
        out.append(emit(ch))
    return "".join(out)


def emit(node):
    if node is None:
        return ""
    k = node[0]
    if k == "seq":
        return _emit_seq(node[1])
    if k == "txt":
        return _run(node[1], upright=not _is_letter(node[1][:1] or "x")
                    and not node[1][:1].isalpha())
    if k == "up":
        return _run(node[1], upright=True)
    if k == "frac":
        return "<m:f><m:num>%s</m:num><m:den>%s</m:den></m:f>" % (_arg(node[1]), _arg(node[2]))
    if k == "sup":
        return "<m:sSup><m:e>%s</m:e><m:sup>%s</m:sup></m:sSup>" % (_arg(node[1]), _arg(node[2]))
    if k == "sub":
        return "<m:sSub><m:e>%s</m:e><m:sub>%s</m:sub></m:sSub>" % (_arg(node[1]), _arg(node[2]))
    if k == "subsup":
        return ("<m:sSubSup><m:e>%s</m:e><m:sub>%s</m:sub><m:sup>%s</m:sup></m:sSubSup>"
                % (_arg(node[1]), _arg(node[2]), _arg(node[3])))
    if k == "rad":
        deg, body = node[1], node[2]
        if deg is None:
            return ('<m:rad><m:radPr><m:degHide m:val="1"/></m:radPr>'
                    '<m:deg/><m:e>%s</m:e></m:rad>' % _arg(body))
        return ('<m:rad><m:radPr/><m:deg>%s</m:deg><m:e>%s</m:e></m:rad>'
                % (_arg(deg), _arg(body)))
    if k == "nary":
        ch, sub, sup, body = node[1], node[2], node[3], node[4]
        pr = '<m:naryPr><m:chr m:val="%s"/><m:limLoc m:val="undOvr"/>' % _x(ch)
        pr += '<m:subHide m:val="%d"/><m:supHide m:val="%d"/></m:naryPr>' % (
            1 if sub is None else 0, 1 if sup is None else 0)
        return ("<m:nary>%s<m:sub>%s</m:sub><m:sup>%s</m:sup><m:e>%s</m:e></m:nary>"
                % (pr, _arg(sub) if sub else "", _arg(sup) if sup else "", _arg(body)))
    if k == "limlow":
        return ('<m:limLow><m:e>%s</m:e><m:lim>%s</m:lim></m:limLow>'
                % (_run("lim", upright=True), _arg(node[1])))
    if k == "dlm":
        op, cl, body = node[1], node[2], node[3]
        return ('<m:d><m:dPr><m:begChr m:val="%s"/><m:endChr m:val="%s"/></m:dPr>'
                '<m:e>%s</m:e></m:d>' % (_x(op), _x(cl), _arg(body)))
    return ""


ERRORS = []

# 行间公式的呈现方式：
#   "center"     居中段落内使用 m:oMath。Word 会把"独占整段的公式"自动按行间
#                规格渲染（分式全尺寸），且段落边框正常，是默认方案。
#   "mathpara"   使用 m:oMathPara。Word 原生行间公式，但段落会丢失边框
#                （提示框左边条会断成一段段），仅供对比。
DISPLAY_MODE = "center"


def omath(tex, display=False, highlight=False):
    """把一段公式源码转成 OMML 片段。转换失败时降级为纯文本并记录。"""
    _CUR["highlight"] = bool(highlight)
    try:
        src = normalize(tex)
        toks = tokenize(src)
        tree = Parser(toks).parse()
        inner = emit(tree)
        if not inner:
            raise ValueError("empty")
    except Exception as e:                                  # noqa: BLE001
        ERRORS.append((tex, "%s: %s" % (type(e).__name__, e)))
        inner = _run(tex.strip() or " ", upright=False)
    finally:
        _CUR["highlight"] = False
    if not display or DISPLAY_MODE != "mathpara":
        return "<m:oMath>%s</m:oMath>" % inner
    return ('<m:oMathPara><m:oMathParaPr><m:jc m:val="center"/></m:oMathParaPr>'
            '<m:oMath>%s</m:oMath></m:oMathPara>' % inner)


if __name__ == "__main__":
    import sys
    for t in sys.argv[1:]:
        print(t, "=>")
        print(omath(t))
        print()
