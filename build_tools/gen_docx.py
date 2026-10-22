# -*- coding: utf-8 -*-
"""生成《算法竞赛模板手册》docx。

用法： python gen_docx.py
输出： 算法竞赛模板手册.docx（脚本同级的上级目录，即工作区根目录）
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from docx.enum.text import WD_ALIGN_PARAGRAPH  # noqa: E402
from docx.shared import Pt  # noqa: E402
from docxkit import Builder  # noqa: E402
from render import render  # noqa: E402

import content_tools  # noqa: E402
import content_algo  # noqa: E402
import content_check  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "算法竞赛模板手册.docx")

FRONT = [
    ("h1", "使用说明"),
    ("p", "这是一本\"边写边查\"的模板手册。它不替代系统学习，"
          "而是把竞赛中最常用、最容易写错的代码固化成可以直接抄用的模板，"
          "并把每个模板配套的坑点写清楚。全册按下表分工使用。"),
    ("table", ["部分", "内容", "怎么用"], [
        ["第一部分", "通用工具与提速模板（快读快写、质数筛、取模、字符串、浮点、调试）",
         "当作抄写本：每道题开头照抄骨架，需要质数表/快速幂时直接取用"],
        ["第二部分", "算法模板（排序 → 贪心 → 前缀和 → 递归搜索 → 二分 → DP → 栈队列 → 高精度）",
         "当作工具书：按\"用途 + 应用场景 + 模板 + 常见报错\"四段式查阅"],
        ["第三部分", "易错自检（类型、数组、边界、格式、浮点、复杂度、逻辑、调试、清单、流程）",
         "当作检查单：提交前 60 秒逐条核对；WA/TLE/RE 后按分类定位"],
    ], [2.2, 7.4, 5.4]),
    ("h2", "编排约定"),
    ("bullets", [
        ("每个模板统一按五段呈现：", ("用途 → 应用场景 → 复杂度 → 模板代码 → 常见报错。", {"bold": True}),
         "复杂算法额外给出\"对比/延伸\"，说明它与相邻算法的取舍。"),
        ("模板代码中的所有变量名都可以自由替换；注释标明了\"关键行\"的作用，"
         "优先读注释再读代码。"),
        ("标注【拓展】的内容超出 30 天课件范围，是为你后续进阶预留的接口，"
         "第一遍阅读可以跳过。"),
        ("标注 ⚠ 的方框是易错点清单，建议在写对应算法前扫一眼，"
         "写完后当检查表用。"),
        ("代码统一使用 C++17 标准、GCC（g++）编译，"
         "编译建议：", ("g++ -std=c++17 -O2 -Wall -Wextra -o a a.cpp", {"name": "Consolas", "size": 9.5}), "。"),
    ]),
    ("h2", "算法索引（按难度递进）"),
    ("p", "第二部分不按课件的天数顺序组织，而是按\"知识点相关度\"分成了 9 个板块，"
          "板块之间由易到难，板块内部也大体按从简单到复杂排列。"),
    ("table", ["板块", "包含模板", "难度"], [
        ["① 数组与模拟", "桶计数 / 计数排序、二维数组与方阵、方向数组与网格、模拟题套路", "★"],
        ["② 排序与查找基础", "sort 与自定义 cmp、结构体排序、去重与离散化、nth_element、"
                              "lower_bound/upper_bound", "★"],
        ["③ 字符串处理", "字符与数字互转、进制转换、格式化与解析、字符串模拟技巧", "★"],
        ["④ 贪心", "排序贪心、区间调度、区间选点、哈夫曼（堆）、分数背包、按位贪心", "★★"],
        ["⑤ 前缀和与差分", "一维/二维前缀和、一维/二维差分、离散化、"
                            "（拓展）树上差分", "★★"],
        ["⑥ 递归、递推与搜索", "递归三要素、递推与记忆化、DFS 枚举、DFS 回溯与剪枝、"
                                "网格 DFS/BFS、多源 BFS", "★★★"],
        ["⑦ 二分", "手写 lower/upper bound、二分答案、实数二分、（拓展）三分", "★★★"],
        ["⑧ 动态规划", "线性 DP、LIS、LCS、最大子段和、0/1 背包、完全背包、"
                        "多重/分组背包、区间 DP", "★★★★"],
        ["⑨ 栈、队列与高精度", "stack/queue/deque/priority_queue、括号匹配、后缀表达式、"
                                "单调栈与单调队列、高精度四则运算", "★★★★"],
    ], [3.4, 9.4, 1.9]),
    ("tipbox", "先记住三张表", [
        "① 数据类型范围表（第一部分第 4 节）——决定你会不会 WA。",
        "② 复杂度对照表（第三部分 F）——决定你会不会 TLE。",
        "③ 提交前检查清单（第三部分 I）——决定你会不会因为低级失误丢分。",
    ]),
]


def add_toc_field(b):
    """插入一个 TOC 域占位段落。

    真正的目录内容与页码由 finalize.ps1 调用 Word 生成（否则域是空的）。
    """
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.enum.text import WD_ALIGN_PARAGRAPH as AL

    b.page_break()
    p = b.doc.add_paragraph()
    p.alignment = AL.LEFT
    r = p.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = r'TOC \o "1-2" \h \z \u'
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    placeholder = OxmlElement("w:t")
    placeholder.text = "（目录将在最终保存时由 Word 生成）"
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    for el in (fld_begin, instr, fld_sep, placeholder, fld_end):
        r._element.append(el)


def add_footer_page_numbers(b):
    """直接用 OOXML 写入页脚：第 {PAGE} 页 / 共 {NUMPAGES} 页。"""
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.enum.text import WD_ALIGN_PARAGRAPH as AL

    footer = b.doc.sections[0].footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0]
    p.alignment = AL.CENTER

    def add_run(text=None, size=9):
        run = p.add_run(text or "")
        run.font.size = Pt(size)
        run.font.name = "Times New Roman"
        rpr = run._element.get_or_add_rPr()
        rf = rpr.find(qn("w:rFonts"))
        if rf is None:
            rf = OxmlElement("w:rFonts")
            rpr.append(rf)
        rf.set(qn("w:ascii"), "Times New Roman")
        rf.set(qn("w:hAnsi"), "Times New Roman")
        rf.set(qn("w:eastAsia"), "微软雅黑")
        return run

    def add_field(run, code):
        begin = OxmlElement("w:fldChar")
        begin.set(qn("w:fldCharType"), "begin")
        instr = OxmlElement("w:instrText")
        instr.set(qn("xml:space"), "preserve")
        instr.text = " %s " % code
        sep = OxmlElement("w:fldChar")
        sep.set(qn("w:fldCharType"), "separate")
        val = OxmlElement("w:t")
        val.text = "1"
        end = OxmlElement("w:fldChar")
        end.set(qn("w:fldCharType"), "end")
        for el in (begin, instr, sep, val, end):
            run._element.append(el)

    add_run("第 ")
    add_field(add_run(), "PAGE")
    add_run(" 页 / 共 ")
    add_field(add_run(), "NUMPAGES")
    add_run(" 页")


def main():
    t0 = time.time()
    b = Builder()
    b.title("算法竞赛模板手册",
            "通用工具 · 算法模板 · 易错自检　|　基于 ACM 30 天学习课件整理　|　C++17")
    add_toc_field(b)
    add_footer_page_numbers(b)
    render(b, FRONT)
    render(b, content_tools.PART1)
    render(b, content_algo.PART2)
    render(b, content_check.PART3)
    b.save(OUT)
    print("saved:", OUT, "%.1fs" % (time.time() - t0),
          os.path.getsize(OUT) // 1024, "KB")


if __name__ == "__main__":
    main()
