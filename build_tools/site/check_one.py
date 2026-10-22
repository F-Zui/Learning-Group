# -*- coding: utf-8 -*-
"""单节课检查：导入、结构、编译该节全部完整程序、检查是否用到已做过的题。

用法： python check_one.py 21 22 23
"""
import importlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

GPP = r"D:\software\CLion 2026.2.2\bin\mingw\bin\g++.exe"
WORK = os.path.join(HERE, "_one_check")
from done_check import DONE  # noqa: E402


def codes_of(L):
    out = []
    for s in L.get("sections", []):
        if not isinstance(s, dict):
            continue
        if s.get("kind") == "code":
            out.append(("section", s["code"]))
        elif s.get("kind") in ("idea", "after"):
            for b in s.get("blocks", []):
                if isinstance(b, dict) and b.get("kind") == "code":
                    out.append(("idea", b["code"]))
        elif s.get("kind") == "func" and s.get("example"):
            out.append(("func", s["example"]))
    for key in ("challenge", "challenge2"):
        c = L.get(key)
        if c and c.get("code"):
            out.append((key, c["code"]))
    for c in L.get("challenges") or []:
        if c.get("code"):
            out.append(("challenges", c["code"]))
    return out


def main():
    ids = [int(x) for x in sys.argv[1:]] or list(range(1, 61))
    os.makedirs(WORK, exist_ok=True)
    bad = 0
    for lid in ids:
        path = os.path.join(HERE, "lessons", "l%02d.py" % lid)
        if not os.path.exists(path):
            print("[%02d] 文件不存在" % lid)
            bad += 1
            continue
        try:
            mod = importlib.import_module("lessons.l%02d" % lid)
        except Exception as e:                           # noqa: BLE001
            print("[%02d] 导入失败: %s" % (lid, e))
            bad += 1
            continue
        L = getattr(mod, "LESSONS", [None])[0]
        if not L:
            print("[%02d] LESSONS 为空" % lid)
            bad += 1
            continue
        msgs = []
        # 结构
        kinds = []
        def flat(bs):
            for b in bs:
                if isinstance(b, dict):
                    kinds.append(b.get("kind"))
                    if b.get("blocks"):
                        flat(b["blocks"])
        flat(L.get("sections", []))
        if lid >= 21:
            if not L.get("challenge2"):
                msgs.append("缺 challenge2")
            else:
                c2 = L["challenge2"]
                for k in ("name", "code", "hint", "idea", "pitfalls", "link"):
                    if not c2.get(k):
                        msgs.append("challenge2 缺字段 %s" % k)
        # 已做过的题
        used = []
        for s in L.get("sections", []):
            if isinstance(s, dict) and s.get("kind") == "example":
                used.append(("example", s["problem"].get("id")))
        for key in ("challenge", "challenge2"):
            c = L.get(key)
            if c:
                used.append((key, c.get("id")))
        for c in L.get("challenges") or []:
            used.append(("challenges", c.get("id")))
        for where, pid in used:
            if pid in DONE:
                msgs.append("用了已做过的题 %s (%s)" % (pid, where))
        # 编译
        fails = 0
        for i, (where, code) in enumerate(codes_of(L)):
            if "#include" not in code or "int main" not in code:
                continue
            src = os.path.join(WORK, "l%02d_%d_%s.cpp" % (lid, i, where))
            with open(src, "w", encoding="utf-8") as f:
                f.write(code)
            r = subprocess.run([GPP, "-std=c++17", "-O2", "-w", "-o", src[:-4] + ".exe", src],
                               capture_output=True, text=True, timeout=180)
            if r.returncode != 0:
                fails += 1
                msgs.append("编译失败 %s: %s" % (where, (r.stderr or "").strip().splitlines()[:2]))
        if fails:
            bad += 1
        print("[%02d] %s  %s" % (lid, "OK " if not msgs else "!! ", L.get("title", "")))
        for msg in msgs:
            print("      -", msg)
    print("\n有问题的节数：", bad)


if __name__ == "__main__":
    main()
