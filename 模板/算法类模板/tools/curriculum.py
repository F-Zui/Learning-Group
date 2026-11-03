# -*- coding: utf-8 -*-
"""算法课程结构：唯一数据源。改这里，index.html / assets/toc.js / assets/search-index.js 一起重建。

结构是三层的：

    GROUPS（组） → ITEMS（节） → 节里的小节（写在 NN.html 里，构建立即生成右侧本节目录）

每一节：
    id     节号，同时决定文件名：id=7 → 07.html，body data-lesson="7"
    title  节标题（目录、侧栏、检索都用它）
    level  难度标签，照抄洛谷说法：入门 / 普及- / 普及 / 普及+ / 提高 …
    kind   lesson（普通节）/ review（回顾章）/ mock（模拟赛）
    star   True = 默认标为「已学」（新课程一般全写 False）
    tags   检索用的标签，3~5 个

EXTRA 是目录页“题解”分区，放比赛题解、专题补充这类不占节号的页面。
"""

# ---------------------------------------------------------------- 模块身份
MODULE = {
    "title": "算法类模板",
    "subtitle": "Algorithm Course Template",
    "storePrefix": "lg-algo-template",  # 进度存储键前缀，各课程必须不同
    "rtocKey": "lg-algo-template.rtoc", # 右侧本节目录展开状态
    "footer": "算法类模板 · 由 tools/build.py 生成 · 题目版权归各命题方所有",
    "sidebarTitle": "全部 3 节",
    "heroTitle": "算法类模板 · 做中学",
    "heroSub": ("一节 = 一个完整算法应用的闭环：先看懂新函数，再跟一遍带逐行拆解的例题，"
                "然后自己复现、做题、复盘。每节末尾一道挑战题，第 CH2_FROM 节起再加一道挑战 2。"),
}

# 第几节起出现「挑战 2」（侧栏与目录页会为这些节多画一个 🌟 勾选框）
CH2_FROM = 3

# ---------------------------------------------------------------- 课程结构
GROUPS = [
    {
        "name": "第一组 · 起步：让程序按你说的做",
        "items": [
            {"id": 1, "title": "输入输出与评测机制", "level": "入门", "kind": "lesson",
             "star": False, "tags": ["cin/cout", "getline", "整数范围", "评测机制"]},
            {"id": 2, "title": "循环、累加与整数溢出", "level": "入门", "kind": "lesson",
             "star": False, "tags": ["for/while", "long long", "溢出", "累加"]},
        ],
    },
    {
        "name": "第二组 · 前缀和：把区间求和变成一次减法",
        "items": [
            {"id": 3, "title": "前缀和与差分", "level": "普及-", "kind": "lesson",
             "star": False, "tags": ["前缀和", "差分", "区间修改", "二维前缀和"]},
        ],
    },
]

EXTRA = []          # 例：{"file": "sol-x.html", "title": "某某赛 题解", "note": "10 题全解", "level": "入门 ~ 提高"}


def all_items():
    for g in GROUPS:
        for it in g["items"]:
            yield g, it


def item_by_id(i):
    for _g, it in all_items():
        if it["id"] == i:
            return it
    return None
