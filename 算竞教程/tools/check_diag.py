# -*- coding: utf-8 -*-
"""检查图解覆盖：每节 diagram 数量、是否有代码逻辑图、是否渲染报错。

用法： python check_diag.py [节号...]
"""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

MIN_TOTAL = 3          # 每节至少 3 张图
MIN_FLOW = 1           # 至少 1 张流程图（代码逻辑图）


def walk(blocks, out):
    """递归收集图解，包括卡在推导卡 / 落地卡各步里的图。"""
    for b in blocks or []:
        if not isinstance(b, dict):
            continue
        if b.get("kind") == "diagram":
            out.append(b)
        for key in ("blocks", "statement", "req", "problem", "end", "oi"):
            if b.get(key):
                walk(b[key], out)
        for st in b.get("steps") or []:
            for part in st[1:3]:
                if part:
                    walk(part, out)


def main():
    ids = [int(x) for x in sys.argv[1:]] or [i for i in range(31, 61)]
    bad = 0
    for lid in ids:
        try:
            mod = importlib.import_module("lessons.l%02d" % lid)
        except Exception as e:                                    # noqa: BLE001
            print("[%02d] 导入失败: %s" % (lid, e))
            bad += 1
            continue
        L = mod.LESSONS[0]
        got = []
        walk(L.get("sections"), got)
        for key in ("challenge", "challenge2"):
            c = L.get(key)
            if c:
                walk(c.get("idea_blocks"), got)
        kinds = [d.get("dtype") for d in got]
        msgs = []
        if len(got) < MIN_TOTAL:
            msgs.append("图太少：%d < %d" % (len(got), MIN_TOTAL))
        if kinds.count("flow") < MIN_FLOW:
            msgs.append("缺流程图（code logic）")
        for d in got:
            if not d.get("cap"):
                msgs.append("%s 图缺标题 cap" % d.get("dtype"))
                break
        no_cap = [d for d in got if not d.get("cap")]
        if no_cap:
            msgs.append("有 %d 张图没有标题" % len(no_cap))
        print("[%02d] %-30s 图 %d （%s）%s"
              % (lid, L["title"][:30], len(got),
                 " ".join(sorted(set(kinds))), "  <<< " + "；".join(msgs) if msgs else ""))
        if msgs:
            bad += 1
    print("\n不达标的节：%d / %d" % (bad, len(ids)))


if __name__ == "__main__":
    main()
