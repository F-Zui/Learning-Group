# -*- coding: utf-8 -*-
"""对 omml.py 做结构测试：以树形记法核对分式 / 角标 / 根式 / 极限 / 求和。"""
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, r"D:\Project\math\tools")
import omml

NS = {
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}


def T(node):
    if node is None:
        return "-"
    tag = node.tag.split("}")[1]
    if tag in ("oMathPara", "oMath", "e", "num", "den", "sub", "sup", "lim", "deg"):
        parts = [T(c) for c in node]
        if tag in ("oMathPara", "oMath", "e"):
            return "".join(parts)
        return "[" + "".join(parts) + "]"
    if tag == "r":
        return "".join((t.text or "") for t in node.findall("m:t", NS)) or "·"
    if tag == "f":
        return "FRAC(%s / %s)" % (T(node.find("m:num", NS)), T(node.find("m:den", NS)))
    if tag == "sSup":
        return "SUP(%s ↑ %s)" % (T(node.find("m:e", NS)), T(node.find("m:sup", NS)))
    if tag == "sSub":
        return "SUB(%s ↓ %s)" % (T(node.find("m:e", NS)), T(node.find("m:sub", NS)))
    if tag == "sSubSup":
        return "SUBSUP(%s ↓%s ↑%s)" % (T(node.find("m:e", NS)),
                                       T(node.find("m:sub", NS)), T(node.find("m:sup", NS)))
    if tag == "rad":
        d = node.find("m:deg", NS)
        return "ROOT(%s%s)" % (T(d) if d is not None else "", T(node.find("m:e", NS)))
    if tag == "d":
        pr = node.find("m:dPr", NS)
        b = e = ""
        if pr is not None:
            x = pr.find("m:begChr", NS)
            y = pr.find("m:endChr", NS)
            b = x.get("{%s}val" % NS["m"]) if x is not None else "("
            e = y.get("{%s}val" % NS["m"]) if y is not None else ")"
        return "DLM%s%s%s" % (b, T(node.find("m:e", NS)), e)
    if tag == "nary":
        return "SUM%s↓%s↑%s" % (T(node.find("m:e", NS)),
                                T(node.find("m:sub", NS)), T(node.find("m:sup", NS)))
    if tag == "limLow":
        return "LIM(%s ↓ %s)" % (T(node.find("m:e", NS)), T(node.find("m:lim", NS)))
    if tag.endswith("Pr"):
        return ""
    return "".join(T(c) for c in node)


CASES = [
    "(x² − 4)/(x − 2)",
    "(sin x)/x",
    "lim(x→0) (sin x)/x = 1",
    "lim(n→∞) xₙ = a",
    "5n/(2n²)",
    "k · (sin kx)/(kx)",
    "1/(1 + h)^n",
    "f(f(x)) = 1/(1 − 1/(1 − x))",
    "√(1 + x) − 1",
    "ⁿ√(1 + x) − 1",
    "e^(1/x)",
    "(1 + 1/x)^(1/x) = e",
    "|xₙ − a| < ε",
    "1/2² + 1/2ⁿ⁻¹",
    "xₙ = Σₖ₌₀ⁿ C(n, k) (1/n)ᵏ",
    "sh x / ch x",
    "−(x + 2)/(1 + x + x²)",
    "x = (3y + 1)/(y − 2)　(y ≠ 2)",
    "f⁻¹[f(x)] = x",
    "lim(x→∞) (1 + 1/x)^x = e",
    "1/(1 − x) − 3/(1 − x³)",
    "2 sin²u/(4u²) = (1/2) · (sin u / u)²",
    "|xₙ − 3/2| = |(2(3n² + n) − 3(2n² − 1)) / (2(2n² − 1))|",
    "y = e^(√(1 − x²))",
    "max{N₀, N₁, N₂}",
    "th x = sh x / ch x",
]

W_NS = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'

for c in CASES:
    wrapped = omml.omath(c).replace(
        "<m:oMath>", "<m:oMath " + omml.M_NS + " " + W_NS + ">", 1)
    root = ET.fromstring(wrapped)
    print("源  :", c)
    print("结构:", T(root))
    print()

if omml.ERRORS:
    print("!!! 转换失败:", len(omml.ERRORS))
    for t, e in omml.ERRORS[:10]:
        print("   ", t[:60], "->", e)
