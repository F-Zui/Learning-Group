# -*- coding: utf-8 -*-
"""检查 think / think_a 是否一一对应。

用法： python check_think.py [节号...]
"""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def main():
    ids = [int(x) for x in sys.argv[1:]] or list(range(1, 61))
    bad = 0
    total = 0
    for lid in ids:
        try:
            mod = importlib.import_module("lessons.l%02d" % lid)
        except Exception as e:                                   # noqa: BLE001
            print("[%02d] 导入失败: %s" % (lid, e))
            bad += 1
            continue
        L = mod.LESSONS[0]
        think = L.get("think") or []
        ans = L.get("think_a") or []
        total += len(think)
        msgs = []
        if len(ans) != len(think):
            msgs.append("条数不匹配：think=%d think_a=%d" % (len(think), len(ans)))
        for i, a in enumerate(ans):
            if not str(a).strip():
                msgs.append("第 %d 条解析为空" % (i + 1))
            elif len(str(a)) < 40:
                msgs.append("第 %d 条解析过短（%d 字）" % (i + 1, len(str(a))))
        if msgs:
            bad += 1
            print("[%02d] %s" % (lid, L.get("title", "")))
            for m in msgs:
                print("      -", m)
    print("\n共 %d 条思考点，有问题 %d 节" % (total, bad))


if __name__ == "__main__":
    main()
