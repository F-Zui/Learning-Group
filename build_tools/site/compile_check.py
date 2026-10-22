# -*- coding: utf-8 -*-
"""抽取所有课程里的完整 C++ 程序，逐个编译，报告失败项。

只编译「有 #include 的完整程序」，跳过片段。
"""
import importlib
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

GPP = r"D:\software\CLion 2026.2.2\bin\mingw\bin\g++.exe"
WORK = os.path.join(HERE, "_build_check")


def iter_code(lesson):
    for s in lesson.get("sections", []):
        if not isinstance(s, dict):
            continue
        if s.get("kind") == "code":
            yield "section", s["code"]
        elif s.get("kind") in ("idea", "after"):
            for b in s.get("blocks", []):
                if isinstance(b, dict) and b.get("kind") == "code":
                    yield "idea", b["code"]
        elif s.get("kind") == "func" and s.get("example"):
            yield "func", s["example"]
    ch = lesson.get("challenge")
    if ch and ch.get("code"):
        yield "challenge", ch["code"]
    for ch in lesson.get("challenges") or []:
        if ch.get("code"):
            yield "challenge", ch["code"]


def is_full_program(code):
    return ("#include" in code) and ("int main" in code)


def main():
    os.makedirs(WORK, exist_ok=True)
    total = ok = skipped = 0
    failures = []
    for lid in range(1, 61):
        path = os.path.join(HERE, "lessons", "l%02d.py" % lid)
        if not os.path.exists(path):
            continue
        mod = importlib.import_module("lessons.l%02d" % lid)
        items = getattr(mod, "LESSONS", [])
        if not items:
            continue
        for idx, (where, code) in enumerate(iter_code(items[0])):
            total += 1
            if not is_full_program(code):
                skipped += 1
                continue
            src = os.path.join(WORK, "l%02d_%d_%s.cpp" % (lid, idx, where))
            exe = src[:-4] + ".exe"
            with open(src, "w", encoding="utf-8") as f:
                f.write(code)
            r = subprocess.run([GPP, "-std=c++17", "-O2", "-w", "-o", exe, src],
                               capture_output=True, text=True, timeout=120)
            if r.returncode == 0:
                ok += 1
            else:
                err = (r.stderr or "").strip().splitlines()
                failures.append((lid, where, idx, err[:4]))
    print("代码块总数 %d：完整程序 %d（通过 %d），片段 %d"
          % (total, ok + len(failures), ok, skipped))
    for lid, where, idx, err in failures:
        print("\n[第 %02d 节 · %s · #%d] 编译失败" % (lid, where, idx))
        for line in err:
            print("   ", line)


if __name__ == "__main__":
    main()
