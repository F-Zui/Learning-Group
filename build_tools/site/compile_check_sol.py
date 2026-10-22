# -*- coding: utf-8 -*-
"""编译并跑通三份题解文档里的所有代码（只编译，不判题）。"""
import importlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

GPP = r"D:\software\CLion 2026.2.2\bin\mingw\bin\g++.exe"
WORK = os.path.join(HERE, "_build_check", "sol")


def main():
    os.makedirs(WORK, exist_ok=True)
    ok = fail = 0
    failures = []
    for modname in ("solutions.s_xinsheng", "solutions.s_yuesai2025", "solutions.s_gdut2026"):
        mod = importlib.import_module(modname)
        for doc in mod.DOCS:
            for p in doc["problems"]:
                code = p.get("code") or ""
                if "#include" not in code or "int main" not in code:
                    continue
                tag = "%s_%s" % (modname.split(".")[-1], p["letter"])
                src = os.path.join(WORK, tag + ".cpp")
                exe = src[:-4] + ".exe"
                with open(src, "w", encoding="utf-8") as f:
                    f.write(code)
                r = subprocess.run([GPP, "-std=c++17", "-O2", "-w", "-o", exe, src],
                                   capture_output=True, text=True, timeout=180)
                if r.returncode == 0:
                    ok += 1
                else:
                    fail += 1
                    failures.append((tag, (r.stderr or "").strip().splitlines()[:4]))
    print("题解代码：通过 %d，失败 %d" % (ok, fail))
    for tag, err in failures:
        print("\n[%s] 编译失败" % tag)
        for line in err:
            print("   ", line)


if __name__ == "__main__":
    main()
