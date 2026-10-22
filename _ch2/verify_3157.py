# -*- coding: utf-8 -*-
"""P3157 交叉验证：随机排列 + 随机删除顺序，CDQ 结果 vs 暴力。"""
import random
import subprocess

EXE = r"D:\文档\学习中转\c++\_ch2\c06_cdq.exe"

def brute(a, dels):
    a = a[:]
    out = []
    for v in dels:
        cnt = 0
        for i in range(len(a)):
            for j in range(i + 1, len(a)):
                if a[i] > a[j]:
                    cnt += 1
        out.append(cnt)
        a.remove(v)
    return out

random.seed(12345)
for it in range(300):
    n = random.randint(2, 9)
    a = list(range(1, n + 1))
    random.shuffle(a)
    m = random.randint(1, n)
    dels = random.sample(range(1, n + 1), m)
    inp = "%d %d\n%s\n%s\n" % (n, m, " ".join(map(str, a)), " ".join(map(str, dels)))
    r = subprocess.run([EXE], input=inp, capture_output=True, text=True)
    got = [int(x) for x in r.stdout.split()]
    exp = brute(a, dels)
    if got != exp:
        print("MISMATCH", inp, got, exp)
        break
else:
    print("P3157 300 random tests OK")
