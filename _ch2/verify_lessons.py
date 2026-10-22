# -*- coding: utf-8 -*-
"""端到端验证：把每节 challenge2 里嵌的代码抽出来编译、跑它自己的样例，再查 HTML 标签是否闭合。"""
import importlib
import os
import re
import subprocess
import sys

HERE = r"D:\文档\学习中转\c++\build_tools\site"
sys.path.insert(0, HERE)
os.chdir(HERE)

GPP = r"D:\software\CLion 2026.2.2\bin\mingw\bin\g++.exe"
os.environ["PATH"] = r"D:\software\CLion 2026.2.2\bin\mingw\bin;" + os.environ["PATH"]
WORK = os.path.join(HERE, "_one_check")
os.makedirs(WORK, exist_ok=True)

LESSONS = [51, 52, 53, 54, 55, 56, 57, 58, 59, 60]

def split_sample(s):
    s = s.replace("\r\n", "\n")
    m = re.match(r"输入：\n(.*?)\n输出：\n(.*)$", s, re.S)
    if not m:
        return None
    return m.group(1) + "\n", m.group(2).strip()

bad = 0
for lid in LESSONS:
    L = importlib.import_module("lessons.l%02d" % lid).LESSONS[0]
    c2 = L["challenge2"]
    src = os.path.join(WORK, "ch2_%02d.cpp" % lid)
    open(src, "w", encoding="utf-8").write(c2["code"])
    exe = src[:-4] + ".exe"
    r = subprocess.run([GPP, "-std=c++17", "-O2", "-w", "-static-libgcc", "-static-libstdc++",
                        "-o", exe, src], capture_output=True, text=True)
    if r.returncode != 0:
        print("[%d] 编译失败: %s" % (lid, r.stderr.strip().splitlines()[:2]))
        bad += 1
        continue
    sp = split_sample(c2["sample"] or "")
    if not sp:
        print("[%d] 样例格式异常" % lid)
        bad += 1
        continue
    inp, exp = sp
    rr = subprocess.run([exe], input=inp, capture_output=True, text=True, timeout=120)
    got = rr.stdout.strip()
    ok = got == exp.strip()
    print("[%d] %s %-8s 样例 %s" % (lid, "OK " if ok else "BAD", c2["id"], "通过" if ok else "不一致"))
    if not ok:
        bad += 1
        print("     got=%r" % got)
        print("     exp=%r" % exp.strip())

    # HTML 标签平衡检查
    texts = []
    for blk in c2["statement"]:
        texts.append(blk.get("text", "") if isinstance(blk, dict) else str(blk))
    texts += list(c2["hint"]) + list(c2["idea"]) + list(c2["pitfalls"])
    texts += ["%s %s" % (a, b) for a, b in c2["explain"]]
    for t in texts:
        # 找出形如 < 后面不是字母或 / 的裸小于号
        for m in re.finditer(r"<(?![/a-zA-Z])", t):
            print("     [%d] 可疑裸 '<'：%s" % (lid, t[max(0, m.start() - 25):m.start() + 25]))
            bad += 1
        for tag in ("b", "code", "sup"):
            if t.count("<%s>" % tag) != t.count("</%s>" % tag):
                print("     [%d] 标签 %s 不配对：%s" % (lid, tag, t[:60]))
                bad += 1

print("\n问题数：", bad)
