# -*- coding: utf-8 -*-
"""扫描 .docx 中所有公式对象，查找转换异常的残留记号。"""
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"

path = sys.argv[1]
z = zipfile.ZipFile(path)
x = z.read("word/document.xml").decode("utf-8")
root = ET.fromstring(x)

omaths = list(root.iter(M + "oMath"))
print("公式对象总数:", len(omaths))

suspicious = []
for idx, om in enumerate(omaths, 1):
    txt = "".join(t.text or "" for t in om.iter(M + "t"))
    # 不应出现的转换残留
    if re.search(r"[\\^_$]|\*\*|==", txt):
        suspicious.append((idx, txt[:90]))

print("可疑公式（残留 \\ ^ _ $ 等）:", len(suspicious))
for i, t in suspicious[:25]:
    print("    #%-5d %s" % (i, t))

# 统计结构元素
print()
for tag, name in [("f", "分式"), ("sSup", "上标"), ("sSub", "下标"),
                  ("sSubSup", "上下标"), ("rad", "根式"), ("nary", "求和/积分"),
                  ("limLow", "极限"), ("d", "括号定界符")]:
    print("  %-10s %5d" % (name, len(list(root.iter(M + tag)))))

# 抽查若干公式的文本，人工核对
print("\n--- 抽查 20 个公式文本 ---")
for i in list(range(1, 12)) + [400, 900, 1500, 2000, 2500, 2700]:
    if i <= len(omaths):
        om = omaths[i - 1]
        print("  #%-5d %s" % (i, "".join(t.text or "" for t in om.iter(M + "t"))[:80]))
