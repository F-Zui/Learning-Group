# -*- coding: utf-8 -*-
"""暴力验证 P2575 的阶梯博弈公式：孔洞从右往左两两配对，间距异或。"""
import sys
from functools import lru_cache

def moves(mask, W):
    out = []
    for j in range(W):
        if not (mask >> j & 1):
            continue
        l = -1
        for q in range(j + 1, W):
            if not (mask >> q & 1):
                l = q
                break
        if l >= 0:
            out.append(mask ^ (1 << j) ^ (1 << l))
    return out

def all_sg(W):
    sg = {}
    for mask in sorted(range(1 << W), key=lambda s: -s):  # 这里顺序无关，用递归+memo
        pass
    sys.setrecursionlimit(10000)
    @lru_cache(maxsize=None)
    def g(mask):
        seen = set()
        for nm in moves(mask, W):
            seen.add(g(nm))
        v = 0
        while v in seen:
            v += 1
        return v
    return {mask: g(mask) for mask in range(1 << W)}

def pred(mask, W):
    c = [0]
    for p in range(W):
        if not (mask >> p & 1):
            c.append(p + 1)          # 空位用 1..W 编号
    t = len(c) - 1
    v = 0
    s = t
    while s >= 1:
        v ^= (c[s] - c[s - 1] - 1)
        s -= 2
    return v

bad = 0
for W in range(1, 9):
    sg = all_sg(W)
    for mask in range(1 << W):
        if sg[mask] != pred(mask, W):
            bad += 1
            if bad <= 10:
                print("W=%d mask=%s sg=%d pred=%d" % (W, bin(mask), sg[mask], pred(mask, W)))
    print("W=%d done, mismatches so far=%d" % (W, bad))
print("total mismatches:", bad)
