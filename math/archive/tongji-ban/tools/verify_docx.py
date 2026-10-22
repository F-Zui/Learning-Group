# -*- coding: utf-8 -*-
"""校验生成的 .docx：标记残留、结构统计。"""
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# 任何未解析的 Markdown/LaTeX 标记
LEAK = re.compile(r":::|MORE|\*\*|==|\\[A-Za-z]+|\\[|{}]|\\,")


def main(path):
    z = zipfile.ZipFile(path)
    x = z.read("word/document.xml").decode("utf-8")
    root = ET.fromstring(x)

    paras = list(root.iter(W + "p"))
    texts = ["".join(t.text or "" for t in p.iter(W + "t")) for p in paras]
    full = "\n".join(texts)

    print("段落总数 :", len(texts))
    print("表格数   :", x.count("<w:tbl>"))
    print("标题统计 :", dict(Counter(re.findall(r'<w:pStyle w:val="(Heading\d)"/>', x))))
    print("目录域   :", "TOC" in x)
    print("总字符数 :", len(full))

    leaks = [(i, t) for i, t in enumerate(texts, 1) if LEAK.search(t)]
    print("标记残留 :", len(leaks))
    for i, t in leaks[:15]:
        print("    行%-5d %s" % (i, t[:100]))

    for name, fill in [("难点框", "FFF1F1"), ("易错框", "FFF8E6"),
                       ("例题框", "F2F5FA"), ("表头", "EDEDED"),
                       ("高亮", "FFF2A8")]:
        print("  %s: %d" % (name, x.count('w:fill="%s"' % fill)))

    # 精确不变量：源文件的表格分隔行数 == docx 中的表格数
    src_tables = 0
    if len(sys.argv) > 2:
        with open(sys.argv[2], encoding="utf-8-sig") as f:
            src = f.read()
        src_tables = len(re.findall(r"(?m)^\|[\s:|-]+\|$", src))
        ok = (src_tables == x.count("<w:tbl>"))
        print("源表格数 : %d  |  docx 表格数: %d  ->  %s"
              % (src_tables, x.count("<w:tbl>"), "一致 ✓" if ok else "不一致 ✗"))
        if not ok:
            bad += 1

    return len(leaks)


if __name__ == "__main__":
    bad = main(sys.argv[1])
    print("\n结论:", "通过 ✓" if bad == 0 else "存在问题 ✗")
