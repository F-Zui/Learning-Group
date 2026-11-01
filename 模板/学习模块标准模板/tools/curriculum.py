# -*- coding: utf-8 -*-
"""课程结构：唯一数据源。改这里，index.html / toc.js / search-index.js 一起重建。

每一节的元组：(编号, 标题, 一句话核心, 难度 1-3)
编号决定文件名：2.3 -> sections/2-3.html
"""

PARTS = [
    {"name": "I", "title": "示例部分", "range": "第 1–2 章"},
]

CHAPTERS = [
    {
        "n": 1, "part": "I", "title": "函数与极限",
        "sub": "把“靠近”写成不等式，把图像写成函数。",
        "sections": [
            ("1.1", "函数与图像", "定义域、复合与图像变换", 1),
            ("1.2", "极限的直觉与定义", "ε-δ、单侧极限与夹逼", 2),
        ],
    },
    {
        "n": 2, "part": "I", "title": "导数与积分",
        "sub": "局部线性化与累积：微积分的两半。",
        "sections": [
            ("2.1", "导数与切线", "差商、切线、可导与连续", 2),
        ],
    },
]


def all_sections():
    for ch in CHAPTERS:
        for sid, title, core, diff in ch["sections"]:
            yield ch, sid, title, core, diff
