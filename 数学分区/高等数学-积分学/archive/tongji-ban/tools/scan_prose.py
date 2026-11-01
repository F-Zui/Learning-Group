# -*- coding: utf-8 -*-
"""检查正文（公式对象之外）是否仍残留计算机记法，如 x^2、a_n、(a)/(b)。"""
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"

z = zipfile.ZipFile(sys.argv[1])
root = ET.fromstring(z.read("word/document.xml").decode("utf-8"))

# 收集所有不在 m:oMath 内的 w:t 文本
math_texts = set()
for om in root.iter(M + "oMath"):
    for t in om.iter(M + "t"):
        math_texts.add(id(t))

outside = []
for p in root.iter(W + "p"):
    buf = []
    for t in p.iter(W + "t"):
        buf.append(t.text or "")
    outside.append("".join(buf))

PATTERNS = [
    (r"[\u2070\u00b9\u00b2\u00b3\u2074-\u2079]", "Unicode 上标"),
    (r"[\u2080-\u208e]", "Unicode 下标"),
    (r"\^\(|\^\{|\^[0-9A-Za-z]", "脱字符幂"),
    (r"_[({]|_[0-9A-Za-z]", "下划线角标"),
    (r"\\[A-Za-z]", "LaTeX 命令"),
    (r"\$\$|\$", "美元符"),
]
hits = {}
for i, t in enumerate(outside, 1):
    for pat, name in PATTERNS:
        m = re.search(pat, t)
        if m:
            hits.setdefault(name, []).append((i, t.strip()[:95]))

print("正文段落总数:", len(outside))
for name, _ in PATTERNS:
    got = hits.get(name, [])
    print("\n[%s] %d 处" % (name, len(got)))
    for i, t in got[:8]:
        print("    行%-5d %s" % (i, t))
