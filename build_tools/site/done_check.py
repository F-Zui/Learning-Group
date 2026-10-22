# -*- coding: utf-8 -*-
"""已做过的题目清单（来自用户洛谷做题记录截图）。

凡是出现在这里的题号，第 21 节及之后的例题 / 挑战题 / 挑战2 都不能再用。
"""
import glob
import importlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

DONE = set("""
B2001 B2002 B2003 B2004 B2005 B2006 B2007 B2008 B2009 B2010 B2011 B2012
B2013 B2014 B2015 B2016 B2017 B2018 B2019 B2020 B2021 B2022 B2023 B2024
B2025 B2026 B2027 B2028 B2029 B2030 B2032 B2033 B2034 B2035 B2036 B2071
B2079 B2085 B2158
P1000 P1001 P1035 P1200 P1307 P1554 P1720 P1765 P1914 P1980 P2084 P2550
P2911 P5015 P5703 P5704 P5707 P5711 P5729 P5731 P5732 P5733 P5739 P5743
B2031 B2084 B2161 B2162
P1003 P1008 P1024 P1028 P1036 P1044 P1059 P1093 P1094 P1101 P1102 P1104
P1116 P1157 P1162 P1208 P1223 P1443 P1464 P1478 P1553 P1596 P1605 P1618
P1678 P1706 P1746 P1781 P1803 P2004 P2240 P2249 P2367 P2404 P3397 P3817
P4995 P5143 P5717 P5730 P5740
P1090 P1106 P1135 P1219 P1332 P1719 P2895 P5461
P1012 P4053
""".split())


def lesson_problems(lesson):
    """返回 [(位置描述, 题号)]。"""
    out = []
    for i, b in enumerate(lesson.get("sections", [])):
        if isinstance(b, dict) and b.get("kind") == "example":
            out.append(("example@%d %s" % (i, b["problem"].get("name")), b["problem"].get("id")))
    if lesson.get("challenge"):
        out.append(("challenge %s" % lesson["challenge"].get("name"), lesson["challenge"].get("id")))
    for c in lesson.get("challenges") or []:
        out.append(("challenges %s" % c.get("name"), c.get("id")))
    if lesson.get("challenge2"):
        out.append(("challenge2 %s" % lesson["challenge2"].get("name"), lesson["challenge2"].get("id")))
    return out


def main():
    print("已做过的题号共 %d 个\n" % len(DONE))
    for lid in range(21, 61):
        path = os.path.join(HERE, "lessons", "l%02d.py" % lid)
        if not os.path.exists(path):
            continue
        mod = importlib.import_module("lessons.l%02d" % lid)
        L = getattr(mod, "LESSONS", [None])[0]
        if not L:
            continue
        hits = [(where, pid) for where, pid in lesson_problems(L) if pid in DONE]
        if hits:
            print("[%02d] %s" % (lid, L["title"]))
            for where, pid in hits:
                print("     %-40s %s" % (where, pid))
    print("\n--- 全课程重复出现的题号（同一题在多节用到）---")
    seen = {}
    for lid in range(1, 61):
        path = os.path.join(HERE, "lessons", "l%02d.py" % lid)
        if not os.path.exists(path):
            continue
        mod = importlib.import_module("lessons.l%02d" % lid)
        L = getattr(mod, "LESSONS", [None])[0]
        if not L:
            continue
        for _, pid in lesson_problems(L):
            seen.setdefault(pid, []).append(lid)
    for pid, ls in sorted(seen.items()):
        if len(ls) > 1:
            print("  %-8s %s" % (pid, ls))


if __name__ == "__main__":
    main()
