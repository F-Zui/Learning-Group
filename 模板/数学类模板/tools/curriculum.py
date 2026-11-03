# -*- coding: utf-8 -*-
"""数学类课程结构：唯一数据源。改这里，index.html / toc.js / search-index.js 一起重建。

每节元组：(编号, 标题, 一句话核心, 难度 1-3)
编号决定文件名：2.3 -> sections/2-3.html

数学类课程的编写约定（详见 README）：
  · 章 = 一个数学对象或一个方法族（极限、导数、数论、二次剩余……），不宜超过 8 节；
  · 节 = 一个「推导 → 定理 → 证明 → 落地」的闭环：先需求，后定义；先推导，后定理；
  · 结论必须配算法落地卡：定理不是用来背的，要能变成可执行的步骤。
"""

# 模块身份：换课程时只改这里（存储键必须与其它模块不同，否则同一浏览器下进度会串）
MODULE = {
    "title": "数学类模板",
    "subtitle": "Mathematics Course Template",
    "mark": "∫",
    "progressKey": "lg-math-template.progress.v1",
    "uiKey": "lg-math-template.ui.v1",
    "progressFile": "math-template-progress.json",
    "kicker": "Mathematics · Template",
    "description": (
        "数学类课程的标准版式：推导卡 → 定义/定理 → 证明 → 图像与例题 → 算法落地卡 → 习题 → 一页纸；"
        "含函数图像、几何示意图、代码块与算法流程图，以及全站检索、深浅色主题与学习进度。"
    ),
    "searchHint": "检索全站：ε-δ / 推导卡 / 算法落地 / 例题 …",
    "lede": (
        "复制这个目录即可新建一门数学课：推导卡、定理与证明、函数图像与流程图、代码块与算法落地卡、"
        "例题与习题、全站检索、深浅色主题、学习进度都已接好。把 <code>tools/curriculum.py</code> 换成你的章节，"
        "再按 <code>sections/_骨架.html</code> 写内容即可。"
    ),
}

PARTS = [
    {"name": "I", "title": "示例部分", "range": "第 1–2 章"},
]

CHAPTERS = [
    {
        "n": 1, "part": "I", "title": "极限与连续",
        "sub": "把“靠近”写成不等式：分析学的全部语言都从这里出发。",
        "sections": [
            ("1.1", "极限的 ε-δ 定义", "任意 ε 找 δ：极限的量化语言与估计套路", 2),
            ("1.2", "连续与一致连续", "连续的三等价说法、间断分类与一致连续的差别", 3),
        ],
    },
    {
        "n": 2, "part": "I", "title": "数论与算法",
        "sub": "用定理撑起算法：从 Bézout 到扩展欧几里得。",
        "sections": [
            ("2.1", "最大公约数与 Bézout 恒等式", "证明存在性，再把它变成 O(log n) 的 exgcd", 2),
        ],
    },
]


def all_sections():
    for ch in CHAPTERS:
        for sid, title, core, diff in ch["sections"]:
            yield ch, sid, title, core, diff
