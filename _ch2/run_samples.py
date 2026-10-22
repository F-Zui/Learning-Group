# -*- coding: utf-8 -*-
"""跑 10 道挑战2 参考程序的样例，检查输出。"""
import subprocess
import os

D = os.path.dirname(os.path.abspath(__file__))

CASES = [
    ("c01_trie", "4\n1 2 3\n2 3 4\n2 4 6\n", "7"),
    ("c02_kmp", "whatthemomooofun\nmoo\n", "whatthefun"),
    ("c03_mst_lca", "4 3\n1 2 7\n2 3 5\n1 3 3\n3\n1 3\n3 1\n1 4\n", "5\n5\n-1"),
    ("c04_matching", "2\n2\n0 0\n0 1\n3\n1 1 1\n1 1 1\n1 1 1\n", "No\nYes"),
    ("c05_bit_offline", "6\n1 2 3 4 3 5\n3\n1 2\n3 5\n2 6\n", "2\n2\n4"),
    ("c06_cdq", "5 4\n1 5 3 4 2\n5 1 4 2\n", "5\n2\n2\n1"),
    ("c07_mo", "6 4\n1 2 3 3 3 2\n2 6\n1 3\n3 5\n1 6\n", "2/5\n0/1\n1/1\n4/15"),
    ("c08_stair", "2\n1\n1 20\n2\n1 1\n1 20\n", "NO\nYES"),
    ("c09_closest", "3\n1 1\n2 2\n2 0\n", "1.4142"),
    ("c10_dp", "2\n2 0\n1.00 3.00\n3.00 3.00\n5 0\n1.00 5.00\n2.00 8.00\n"
               "3.00 9.00\n4.00 8.00\n5.00 5.00\n", "1\n1"),
]

for name, inp, exp in CASES:
    exe = os.path.join(D, name + ".exe")
    r = subprocess.run([exe], input=inp, capture_output=True, text=True, timeout=60)
    got = r.stdout.strip()
    ok = "OK  " if got == exp.strip() else "BAD "
    print("%s %-16s got=%-28r exp=%r" % (ok, name, got, exp.strip()))
