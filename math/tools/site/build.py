# -*- coding: utf-8 -*-
"""从 curriculum.py 生成 index.html 与 assets/toc.js。"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from curriculum import CHAPTERS, PARTS, all_sections  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
STAR = ('<svg viewBox="0 0 24 24" width="12" height="12" fill="currentColor" aria-hidden="true">'
        '<path d="M12 2.6l2.9 5.9 6.5.9-4.7 4.6 1.1 6.5L12 17.4 6.2 20.5l1.1-6.5L2.6 9.4l6.5-.9z"/></svg>')


def toc_js():
    data = []
    for ch in CHAPTERS:
        data.append({
            "n": ch["n"], "part": ch["part"], "title": ch["title"], "sub": ch["sub"],
            "sections": [
                {"id": s[0], "title": s[1], "core": s[2], "diff": s[3], "file": "sections/" + s[0].replace(".", "-") + ".html"}
                for s in ch["sections"]
            ],
        })
    return "window.CURRICULUM = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n"


def diff_dots(d):
    return '<span class="diff">' + "".join('<i class="%s"></i>' % ("on" if i < d else "") for i in range(3)) + "</span>"


def card(sid, title, core, diff, ch):
    return (
        '<article class="card" data-sec-card="{sid}">'
        '<input type="checkbox" data-check="{sid}" aria-label="标记 {sid} 完成">'
        '<a href="sections/{fn}.html">'
        '<div class="c-top"><span class="c-id">{sid}</span><span class="c-title">{title}</span>'
        '<span class="c-star" data-star>{star}</span></div>'
        '<div class="c-core">{core}</div>'
        '<div class="c-foot">{dots}<span>第 {ch} 章</span></div>'
        '</a></article>'
    ).format(sid=sid, fn=sid.replace(".", "-"), title=title, core=core, star=STAR, dots=diff_dots(diff), ch=ch)


def chapter_block(ch):
    cards = "".join(card(s[0], s[1], s[2], s[3], ch["n"]) for s in ch["sections"])
    return (
        '<section class="ch-block" data-ch="{n}">'
        '<div class="ch-head">'
        '<div class="ch-no">{n:02d}</div>'
        '<div><h3>{title}</h3><div class="ch-sub">{sub}</div></div>'
        '<div class="ch-side"><span class="ch-count" data-chcount="{n}">0/{cnt}</span>'
        '<span class="ch-mini"><i data-chbar="{n}"></i></span></div>'
        '</div>'
        '<div class="cards">{cards}</div>'
        '</section>'
    ).format(n=ch["n"], title=ch["title"], sub=ch["sub"], cnt=len(ch["sections"]), cards=cards)


def index_html():
    total = sum(len(c["sections"]) for c in CHAPTERS)
    blocks = []
    for part in PARTS:
        chs = [c for c in CHAPTERS if c["part"] == part["name"]]
        if not chs:
            continue
        blocks.append(
            '<div class="part-head"><span class="pn">Part {name}</span>'
            '<h2>{title}</h2><span class="pr">{rng}</span></div>'.format(
                name=part["name"], title=part["title"], rng=part["range"])
        )
        blocks.extend(chapter_block(c) for c in chs)

    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>微积分精讲 · 目录</title>
<meta name="description" content="从图像直觉到严格分析的微积分课程：63 节，含例题、图像、思考点与题解。">
<link rel="stylesheet" href="assets/style.css">
</head>
<body data-index>
<div class="idx-wrap">
  <header class="hero">
    <div>
      <div class="kicker">Calculus, rebuilt</div>
      <h1>微积分：从图像到严格分析</h1>
      <p class="lede">以 Stewart 建立直觉，以 Thomas 磨题，以 Courant 追问“为什么”，以 Abbott / Rudin / Apostol 收束严格性，以 Zorich 铺开结构。全部 63 节，每节自带图像、例题、思考点与题解。</p>
      <div class="hero-actions">
        <a class="btn primary" href="#" data-continue>继续学习 →</a>
        <a class="btn" href="#toc">浏览全部 {total} 节</a>
      </div>
    </div>
    <div class="ring" aria-label="学习进度">
      <svg viewBox="0 0 118 118" width="118" height="118">
        <circle class="bgc" cx="59" cy="59" r="50"></circle>
        <circle class="fgc" cx="59" cy="59" r="50" data-ring="50" style="stroke-dasharray:314.16;stroke-dashoffset:314.16"></circle>
      </svg>
      <div><div class="pc" data-ringtext>0%</div><div class="pl">完成</div></div>
    </div>
  </header>

  <div class="storage-warn" data-storage-warn style="display:none">
    当前浏览器禁止本地存储，勾选状态只在本次页面有效。建议用 <code>python -m http.server</code> 在本地打开，或使用“导出 / 导入”保存进度。
  </div>

  <div class="toolbar">
    <div class="search"><input id="q" type="search" placeholder="搜索：极限、泰勒、格林公式、一致收敛…" aria-label="搜索章节"></div>
    <button class="chip on" type="button" data-filter="all">全部</button>
    <button class="chip" type="button" data-filter="todo">未完成</button>
    <button class="chip" type="button" data-filter="done">已完成</button>
    <span class="ch-count" data-count style="margin-left:auto">0 / {total}</span>
  </div>

  <div id="toc">
{blocks}
  </div>

  <footer class="idx-foot">
    <span>进度保存在本机浏览器，不上传。</span>
    <a href="#" data-export>导出进度</a>
    <a href="#" data-import>导入进度</a>
    <a href="#" data-reset>重置</a>
    <span style="margin-left:auto">Stewart · Thomas · Courant–John · Abbott · Rudin · Apostol · Zorich</span>
  </footer>
</div>
<script src="assets/toc.js"></script>
<script src="assets/app.js"></script>
</body>
</html>
""".replace("{total}", str(total)).replace("{blocks}", "\n".join(blocks))


def outline_md():
    total = sum(len(c["sections"]) for c in CHAPTERS)
    L = []
    L.append("# 微积分精讲 · 课程纲要")
    L.append("")
    L.append("> %d 节 ｜ 3 部分 ｜ 12 章 ｜ 每节独立 HTML，目录与侧栏可勾选进度。" % total)
    L.append("> 交付形态：`index.html`（目录）+ `sections/X-Y.html`（每一节）。")
    L.append("")
    L.append("## 一、设计原则")
    L.append("")
    L.append("1. **图像先行**：每个新概念先给图，再给式，再给定义。图不是装饰，是论证的一部分。")
    L.append("2. **符号优先**：能用公式、表格、不等式说清的，不写句子。正文段落不超过 3 句。")
    L.append("3. **证明分层**：基础证明放正文（Abbott 级），进阶证明折叠在 `.deep` 里（Rudin / Apostol 级），不打断主线。")
    L.append("4. **题解内嵌**：每道习题下面紧跟「思路 → 答案」，不把答案堆到章末。")
    L.append("5. **进度可视**：目录与侧栏同一份进度，勾选即完成，完成节标 ⭐。")
    L.append("")
    L.append("## 二、课程结构")
    L.append("")
    for part in PARTS:
        chs = [c for c in CHAPTERS if c["part"] == part["name"]]
        if not chs:
            continue
        L.append("### 第 %s 部分　%s（%s）" % (part["name"], part["title"], part["range"]))
        L.append("")
        for ch in chs:
            L.append("#### 第 %d 章　%s" % (ch["n"], ch["title"]))
            L.append("")
            L.append("> %s" % ch["sub"])
            L.append("")
            L.append("| 节 | 标题 | 核心内容 | 难度 |")
            L.append("|---|---|---|---|")
            for sid, title, core, diff in ch["sections"]:
                L.append("| %s | %s | %s | %s |" % (sid, title, core, "●" * diff + "○" * (3 - diff)))
            L.append("")
    L.append("## 三、三条主线")
    L.append("")
    L.append("- **极限线**：§2.1–2.6 建立 ε-N / ε-δ，§5.1–5.2 升级为黎曼和与 FTC，§7.2、§11.1–11.5、§12.1–12.3 反复回到「用有限逼近无限」。")
    L.append("- **局部线性化线**：§3.1–3.5 用直线代替曲线，§3.7 升级为多项式，§9.2–9.4 升维为切平面与梯度。")
    L.append("- **统一公式线**：FTC、Green、Gauss、Stokes 是同一个定理的四张面孔，在 §11.5 收束。")
    L.append("")
    L.append("## 四、参考书分工")
    L.append("")
    L.append("| 用途 | 教材 |")
    L.append("|---|---|")
    L.append("| 新知识、直觉、图像 | Stewart, *Calculus: Early Transcendentals* |")
    L.append("| 习题与题解风格 | Thomas, *Thomas' Calculus* |")
    L.append("| 「为什么」、动机、历史 | Courant & John, *Introduction to Calculus and Analysis* |")
    L.append("| 定理证明（基础） | Abbott, *Understanding Analysis* |")
    L.append("| 定理证明（进阶） | Rudin, *Principles of Mathematical Analysis* |")
    L.append("| 证明的补充与推广 | Apostol, *Mathematical Analysis* |")
    L.append("| 结构、例子、多变量 | Zorich, *Mathematical Analysis I / II* |")
    L.append("")
    L.append("## 五、每节的标准结构")
    L.append("")
    L.append("| 区块 | 作用 | 硬性要求 |")
    L.append("|---|---|---|")
    L.append("| 标题 + lede | 一句话点出机制 | 1–2 句 |")
    L.append("| 定义 / 定理 | 严格陈述，条件写全 | 每个新概念至少 1 个 |")
    L.append("| 证明 / 为什么 | 补跳步，或讲动机 | 至少 1 个 |")
    L.append("| 图 | 解释几何与机制 | ≥4 幅 |")
    L.append("| 例题 | 标准、变式、应用、易错 | ≥4 个 |")
    L.append("| 思考点 | 一两句发问 + 引导 | ≥2 个 |")
    L.append("| 习题 | 先思路后答案 | ≥6 道 |")
    L.append("| 一页纸 | 4–6 条结论 | 1 个 |")
    L.append("")
    L.append("## 六、与旧版（同济框架）的差异")
    L.append("")
    L.append("| 维度 | 旧版 | 本版 |")
    L.append("|---|---|---|")
    L.append("| 组织 | 按教材 140 课时，逐节对应 | 按概念依赖重划 12 章 63 节 |")
    L.append("| 语言 | 讲义式长段落 | 符号优先，段落 ≤3 句 |")
    L.append("| 图 | 少量示意图 | 每节 ≥4 幅，函数图自动绘制 |")
    L.append("| 证明 | 跳过或口头带过 | 分层：正文 Abbott 级，折叠 Rudin 级 |")
    L.append("| 题解 | 答案集中放章末 | 每题下紧跟思路与答案 |")
    L.append("| 交付 | 单个 docx | 静态站点，目录与侧栏可勾选、可导出进度 |")
    L.append("")
    return "\n".join(L)


def main():
    with open(os.path.join(ROOT, "assets", "toc.js"), "w", encoding="utf-8") as f:
        f.write(toc_js())
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html())
    with open(os.path.join(ROOT, "课程纲要.md"), "w", encoding="utf-8") as f:
        f.write(outline_md())
    n = sum(1 for _ in all_sections())
    print("sections:", n, "| index.html + assets/toc.js + 课程纲要.md written")


if __name__ == "__main__":
    main()
