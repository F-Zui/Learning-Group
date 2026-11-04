# -*- coding: utf-8 -*-
"""课程自检总入口（对齐模板的 `python tools/check.py`）。

    python tools/check.py           # 快速自检：结构 / 标准闭环 / 图解 / 思考点
    python tools/check.py --full    # 再加上「所有 C++ 程序能否编译」（较慢，约 10 分钟）

任何一个环节没通过就以非零码退出。
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable

# (脚本, 额外参数, 判定“通过”的依据)
STAGES = [
    ("audit.py", [], "问题 0 条"),
    ("check_std.py", [], "不合格 0 /"),
    ("check_diag.py", [str(i) for i in range(1, 61)], "不达标的节：0 /"),
    ("check_think.py", [], "有问题 0 节"),
]

FULL = [
    ("compile_check.py", [], "失败 0"),
    ("compile_check_sol.py", [], "失败 0"),
]


def run(script, args, marker):
    cmd = [PY, "-X", "utf8", os.path.join(HERE, script)] + args
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env)
    out = (r.stdout or "") + (r.stderr or "")
    ok = marker in out and r.returncode == 0
    tail = [ln for ln in out.strip().splitlines() if ln.strip()][-1:] or [""]
    print("%-6s %-22s %s" % ("✅" if ok else "❌", script, tail[0].strip()[:90]))
    if not ok:
        print("\n".join(out.strip().splitlines()[-25:]))
    return ok


def main():
    full = "--full" in sys.argv
    print("课程自检 · %s\n" % ("完整（含编译）" if full else "快速"))
    bad = 0
    for s, a, m in STAGES + (FULL if full else []):
        if not run(s, a, m):
            bad += 1
    print("\n%s" % ("全部通过" if not bad else "有 %d 项未通过" % bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
