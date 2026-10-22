# -*- coding: utf-8 -*-
"""渲染层：把 (kind, ...) 元组序列翻译成 docx 元素。"""
from docxkit import Builder

TYPE_TABLE = (
    ["类型", "大致范围", "占用", "必须开 long long 的典型信号"],
    [
        ["int", "±2.1 × 10⁹（约 21 亿）", "4 字节", "两数相乘 > 4 × 10⁹"],
        ["unsigned int", "0 ~ 4.29 × 10⁹", "4 字节", "减法出现负数时灾难性出错"],
        ["long long", "±9.2 × 10¹⁸", "8 字节", "答案绝对值可能超 21 亿"],
        ["unsigned long long", "0 ~ 1.8 × 10¹⁹", "8 字节", "几乎不用"],
        ["__int128", "±1.7 × 10³⁸", "16 字节", "long long 相乘仍溢出（GCC 特有）"],
        ["float", "约 7 位有效数字", "4 字节", "几乎不用，精度太差"],
        ["double", "约 15~16 位有效数字", "8 字节", "金额/比例题优先转整数"],
        ["char", "-128 ~ 127", "1 字节", "读字符时注意与数字区分"],
        ["bool", "0 / 1", "1 字节", "无"],
    ],
)

COMPLEXITY_TABLE = (
    ["数据规模 n", "可接受的复杂度", "被淘汰的复杂度", "常见对应算法"],
    [
        ["10⁶ ~ 10⁷", "O(n)", "O(n log n) 已偏紧", "线性筛、前缀和、单调队列"],
        ["10⁵ ~ 10⁶", "O(n log n)", "O(n²)", "排序、二分、堆、并查集"],
        ["10⁴", "O(n √n) / O(n log² n)", "O(n²)", "试除法、分块"],
        ["10³ ~ 3×10³", "O(n²)", "O(n³)", "简单 DP、Floyd、暴力枚举对"],
        ["100 ~ 500", "O(n³)", "O(2ⁿ)", "区间 DP、矩阵乘法"],
        ["≤ 25", "O(2ⁿ) / O(n · 2ⁿ)", "O(n!)", "状压 DP、子集枚举"],
        ["≤ 10", "O(n!)", "—", "全排列搜索、暴力回溯"],
    ],
)


def render(b: Builder, blocks):
    for blk in blocks:
        if isinstance(blk, str):          # 直接给字符串 = 普通段落
            b.p(blk)
            continue
        kind = blk[0]
        if kind == "h1":
            b.h1(blk[1])
        elif kind == "h2":
            b.h2(blk[1])
        elif kind == "h3":
            b.h3(blk[1], blk[2] if len(blk) > 2 else None)
        elif kind == "p":
            b.p(blk[1])
        elif kind == "usage":
            b.kv("用途　　：", blk[2] if len(blk) > 2 else blk[1])
        elif kind == "scene":
            b.kv("应用场景：", blk[2] if len(blk) > 2 else blk[1])
        elif kind == "complex":
            b.kv("复杂度　：", blk[2] if len(blk) > 2 else blk[1])
        elif kind == "cmp":
            b.kv("对比　　：", blk[2] if len(blk) > 2 else blk[1])
        elif kind == "bullets":
            b.bullets(blk[1])
        elif kind == "code":
            b.code(blk[1])
        elif kind == "box":
            b.box(blk[1], blk[2], blk[3] if len(blk) > 3 else "tip")
        elif kind == "tipbox":
            b.box(blk[1], blk[2], "tip")
        elif kind == "warnbox":
            b.box("⚠ " + blk[1], blk[2], "warn")
        elif kind == "okbox":
            b.box(blk[1], blk[2], "ok")
        elif kind == "table":
            b.table(blk[1], blk[2], blk[3] if len(blk) > 3 else None)
        elif kind == "typetable":
            b.table(TYPE_TABLE[0], TYPE_TABLE[1], [2.6, 4.2, 1.9, 6.3])
        elif kind == "bigotable":
            b.table(COMPLEXITY_TABLE[0], COMPLEXITY_TABLE[1], [2.4, 3.5, 3.4, 5.7])
        elif kind == "pagebreak":
            b.page_break()
        elif kind == "kv":
            b.kv(blk[1], blk[2])
        else:
            raise ValueError("unknown block kind: %r" % (kind,))
