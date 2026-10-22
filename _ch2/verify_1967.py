# -*- coding: utf-8 -*-
"""P1967 交叉验证：随机小图，最大生成森林 + 倍增 vs 暴力最大瓶颈路。"""
import random
import subprocess

EXE = r"D:\文档\学习中转\c++\_ch2\c03_mst_lca.exe"

def brute(n, edges, queries):
    INF = 10 ** 9
    # widest path by Floyd-like bottleneck: w[i][j] = 最大瓶颈
    w = [[-1] * n for _ in range(n)]
    for i in range(n):
        w[i][i] = INF
    for u, v, c in edges:
        if c > w[u][v]:
            w[u][v] = w[v][u] = c
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if w[i][k] >= 0 and w[k][j] >= 0:
                    t = min(w[i][k], w[k][j])
                    if t > w[i][j]:
                        w[i][j] = t
    return [-1 if w[u][v] < 0 else w[u][v] for u, v in queries]

random.seed(7)
for it in range(200):
    n = random.randint(2, 7)
    m = random.randint(1, 12)
    edges = []
    for _ in range(m):
        u = random.randrange(n)
        v = random.randrange(n)
        while v == u:
            v = random.randrange(n)
        edges.append((u, v, random.randint(0, 20)))
    qn = random.randint(1, 6)
    queries = []
    for _ in range(qn):
        u = random.randrange(n)
        v = random.randrange(n)
        while v == u:
            v = random.randrange(n)
        queries.append((u, v))
    lines = ["%d %d" % (n, m)]
    lines += ["%d %d %d" % (u + 1, v + 1, c) for u, v, c in edges]
    lines.append(str(qn))
    lines += ["%d %d" % (u + 1, v + 1) for u, v in queries]
    inp = "\n".join(lines) + "\n"
    r = subprocess.run([EXE], input=inp, capture_output=True, text=True)
    got = [int(x) for x in r.stdout.split()]
    exp = brute(n, edges, queries)
    if got != exp:
        print("MISMATCH")
        print(inp)
        print("got", got)
        print("exp", exp)
        break
else:
    print("P1967 200 random tests OK")
