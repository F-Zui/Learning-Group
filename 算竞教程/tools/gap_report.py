# -*- coding: utf-8 -*-
"""按《算法类要求.md》的九段闭环盘点 60 节，输出缺项表。"""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

NEED = ["fn", "example", "idea", "code", "explain", "note", "reproduce",
        "math", "think", "check", "challenge"]


def collect(blocks, acc):
    for b in blocks or []:
        if isinstance(b, str):
            acc["p"] += 1
            continue
        if not isinstance(b, dict):
            continue
        k = b.get("kind")
        acc["all"] += 1
        acc[k] = acc.get(k, 0) + 1
        if k in ("idea", "after"):
            collect(b.get("blocks"), acc)
        if k == "example":
            collect(b.get("statement"), acc)
    return acc


def main():
    rows = []
    ids = [int(x) for x in sys.argv[1:]] or list(range(1, 61))
    for lid in ids:
        try:
            L = importlib.import_module("lessons.l%02d" % lid).LESSONS[0]
        except Exception as e:                                    # noqa: BLE001
            rows.append((lid, "导入失败 %s" % e))
            continue
        acc = collect(L.get("sections"), {"all": 0, "p": 0})
        miss = []
        if acc.get("func", 0) < 1:
            miss.append("新函数拆解")
        if acc.get("example", 0) < 1:
            miss.append("例题")
        if acc.get("code", 0) < 1:
            miss.append("代码")
        if acc.get("explain", 0) < 1:
            miss.append("逐行拆解")
        if acc.get("note", 0) < 1:
            miss.append("易错")
        if acc.get("reproduce", 0) < 1:
            miss.append("复现")
        if not L.get("math") and not L.get("portal"):
            miss.append("数学")
        if len(L.get("think") or []) < 3:
            miss.append("思考点<3")
        if len(L.get("think_a") or []) != len(L.get("think") or []):
            miss.append("思考点解析不配对")
        if not L.get("check"):
            miss.append("自测")
        if not L.get("challenge") and not L.get("challenges"):
            miss.append("挑战题")
        if lid >= 21 and not L.get("challenge2"):
            miss.append("挑战2")
        dia = acc.get("diagram", 0)
        if dia < 1:
            miss.append("代码逻辑图×%d" % dia)
        blocks = acc["all"]
        flag = "" if not miss else "缺: " + "、".join(miss)
        rows.append((lid, blocks, dia, flag))
    print("%-4s %-7s %-4s %s" % ("节", "块数", "图", "缺项"))
    bad = 0
    for r in rows:
        if len(r) == 2:
            print(r[0], r[1])
            bad += 1
            continue
        lid, blocks, dia, flag = r
        if flag:
            bad += 1
        print("%-4d %-7d %-4d %s" % (lid, blocks, dia, flag))
    print("\n有缺项的节：%d / %d" % (bad, len(rows)))


if __name__ == "__main__":
    main()
