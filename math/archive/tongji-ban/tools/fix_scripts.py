# -*- coding: utf-8 -*-
"""把 LaTeX 风格的 _{...} / ^{...} 转为 Unicode 上下标。
不可映射的内容回退为 _(...) / ^(...) 形式，避免露出花括号。"""
import io
import re
import sys

SUB = {
    "0": "\u2080", "1": "\u2081", "2": "\u2082", "3": "\u2083", "4": "\u2084",
    "5": "\u2085", "6": "\u2086", "7": "\u2087", "8": "\u2088", "9": "\u2089",
    "+": "\u208a", "-": "\u208b", "\u2212": "\u208b", "=": "\u208c",
    "(": "\u208d", ")": "\u208e",
    "a": "\u2090", "e": "\u2091", "h": "\u2095", "i": "\u1d62", "j": "\u2c7c",
    "k": "\u2096", "l": "\u2097", "m": "\u2098", "n": "\u2099", "o": "\u2092",
    "p": "\u209a", "r": "\u1d63", "s": "\u209b", "t": "\u209c", "u": "\u1d64",
    "v": "\u1d65", "x": "\u2093",
}
SUP = {
    "0": "\u2070", "1": "\u00b9", "2": "\u00b2", "3": "\u00b3", "4": "\u2074",
    "5": "\u2075", "6": "\u2076", "7": "\u2077", "8": "\u2078", "9": "\u2079",
    "+": "\u207a", "-": "\u207b", "\u2212": "\u207b", "=": "\u207c",
    "(": "\u207d", ")": "\u207e", "n": "\u207f", "i": "\u2071", "k": "\u1d4f",
}


def conv(content, table):
    """全部字符可映射则返回 Unicode 形式，否则返回 None。"""
    out = []
    for ch in content:
        if ch in table:
            out.append(table[ch])
        else:
            return None
    return "".join(out)


def fix(md):
    # 先处理少数含嵌套/多字符的复杂名字，避免留下嵌套花括号
    md = md.replace("x_{n_k}", "x_(n_k)")
    md = md.replace("{x_{n_k}}", "{x_(n_k)}")

    def repl(m):
        mark, body = m.group(1), m.group(2)
        table = SUB if mark == "_" else SUP
        r = conv(body, table)
        if r is not None:
            return r
        return ("_(" + body + ")") if mark == "_" else ("^(" + body + ")")

    md = re.sub(r"([_^])\{([^{}]*)\}", repl, md)

    # 无花括号的单字符形式
    def repl1(m):
        mark, body = m.group(1), m.group(2)
        r = conv(body, SUB if mark == "_" else SUP)
        return r if r is not None else (mark + body)

    md = re.sub(r"([_^])([A-Za-z0-9])", repl1, md)
    return md


if __name__ == "__main__":
    p = sys.argv[1]
    s = io.open(p, encoding="utf-8").read()
    n0 = len(s)
    s = fix(s)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    left = sorted(set(re.findall(r"[_^]\{[^{}]*\}", s)))
    print("chars:", n0, "->", len(s))
    print("remaining braced sub/sup:", left if left else "NONE")
