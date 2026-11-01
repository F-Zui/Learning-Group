# 图论入门

**Graph Theory for Competitive Programming** —— 给信息竞赛学生的图论第一门课。

从“谁和谁有关系”出发，把七桥、排课、社交网络抽象成顶点与边，再沿连通、树、匹配、网络流、着色、平面图一层层追问。
每个定理都配图、配证明、配例题；每个算法都配 C++17 代码与逻辑流程图。

- **读者**：会写 C++、学过基础离散数学的竞赛学生；不需要任何图论基础。
- **先修**：数组、`vector`、递归、队列；会读简单的求和符号。
- **产出**：读完后能独立完成“最短路 / 生成树 / 最大匹配 / 最大流 / 割点 / 拓扑排序 / 欧拉路”这一档的建模与实现，并说清每个结论的来源。

---

## 一、课程地图

十三节，五部分。编号即学习顺序，也决定文件名（`2.1` → `sections/2-1.html`）。

| 部分 | 章 | 节 | 一句话 | 主要参考 |
|---|---|---|---|---|
| I 结构 | 0 起点 | 0.1 图论的地图：把关系画成图 | 建模、术语、邻接表与 DFS | Wilson Ch.1 |
| I | 1 图的语言 | 1.1 顶点、边与度：握手定理 | 度序列、可图化、同构 | West Ch.1 |
| I | 1 | 1.2 路、圈与连通性 | BFS、连通块、二分图判定 | West Ch.1 |
| I | 1 | 1.3 树与生成树 | 树的等价刻画、Kruskal、Cayley | West Ch.2 |
| II 匹配与网络 | 2 匹配与网络流 | 2.1 匹配与 Hall 定理 | 增广路、Hall、König | West Ch.3 |
| II | 2 | 2.2 二分图最大匹配：Kuhn 算法 | 让位递归、$O(VE)$、应用 | West Ch.3 |
| II | 2 | 2.3 网络流：Dinic 与最大流最小割 | 残量网络、分层图、建模式 | Bondy & Murty Ch.7 |
| III 着色与平面 | 3 着色与平面图 | 3.1 顶点着色与贪心 | 色数、团数、Welsh–Powell | West Ch.5 / Wilson Ch.9 |
| III | 3 | 3.2 平面图与 Euler 公式 | $V-E+F=2$、$K_5$、$K_{3,3}$、对偶图 | West Ch.6 / Wilson Ch.8 |
| IV 深度优先 | 4 深度优先的艺术 | 4.1 割点、桥与双连通分量 | dfn/low、Tarjan | West Ch.4 |
| IV | 4 | 4.2 欧拉回路与一笔画 | Euler 判据、Hierholzer | Wilson Ch.6 |
| IV | 4 | 4.3 拓扑排序与强连通分量 | Kahn、Tarjan SCC、缩点 DP | Bondy & Murty Ch.9 |
| V 远方 | 5 远方 | 5.1 Turán 定理与 Ramsey 数 | Mantel、Turán 图、$R(3,3)=6$ | West Ch.8 / Wilson Ch.11 |

**参考书定位**：Wilson《Introduction to Graph Theory》负责直觉与历史（七桥、一笔画、四色），West 负责严谨陈述与证明，Bondy & Murty 负责算法与网络流。每节的 `<span class="ref">` 行内标注具体出处。

---

## 二、每一节怎么写

沿用数学类模板的七段式，另外加两类图论专用元素：

```
一、动机      一个具体问题：七桥、排课、网络瓶颈
二、严格陈述  定义 → 定理 → 证明 → 读法 → 易错
三、图像      图的画法（figure.fig 里的 .gv/.ge）或算法流程图
四、例题      2 个：标准情形 + 变体/反例
五、代码      竞赛算法：C++17 + 复杂度 + 逻辑流程图
六、习题      3~6 题，先思路后答案
七、一页纸    3~5 条，只放会反复用到的东西
```

篇幅参考：正文汉字 1.5k–2.5k，图 2–4 幅，例题 2 个，习题 5 道。

---

## 三、目录结构

```
图论/
├── index.html                 目录页（build.py 生成，勿手改）
├── sections/                  一节一个 HTML
│   ├── 0-1.html               …
│   └── _骨架.html             空白骨架（不参与构建与自检）
├── assets/
│   ├── style.css              引擎：全站版式（勿改）
│   ├── app.js                 引擎：侧栏、检索、主题、进度（勿改）
│   ├── theme.js               引擎：首屏前应用主题（勿改）
│   ├── course.css             本课补充：代码块、流程图、图的画法
│   ├── toc.js                 生成物：章节数据
│   ├── search-index.js        生成物：全文检索索引 + 正文锚点
│   └── mathjax/tex-svg.js     本地 MathJax，离线渲染
└── tools/
    ├── curriculum.py          章节数据源（唯一需要手写的结构文件）
    ├── build.py               生成 index.html / toc.js / search-index.js
    ├── searchindex.py         给正文注入 id="bN" 并抽取检索文本
    └── check.py               写法自检
```

---

## 四、新增一节

1. 在 `tools/curriculum.py` 的 `CHAPTERS` 里加一行 `("2.4", 标题, 一句话核心, 难度)`。
2. 复制 `sections/_骨架.html` 为 `sections/2-4.html`，把三处编号改成 `2.4`。
3. 按七段式写内容；先跑 `python tools/check.py sections/2-4.html` 自检。
4. `python tools/build.py` 重建目录与检索索引。

编号必须同时出现在 **文件名、`body data-sec`、`<title>` 前缀** 三处，否则 `check.py` 报错。

---

## 五、图论专用组件

### 5.1 图的画法

```html
<circle cx="120" cy="80" r="15" class="gv-b"/>          <!-- 顶点（蓝） -->
<path d="M120,95 L240,150" class="ge-b"/>               <!-- 边（蓝，匹配/树边） -->
<text x="120" y="80" text-anchor="middle"
      dominant-baseline="central" class="vl">A</text>    <!-- 顶点标签 -->
```

| 类 | 用途 |
|---|---|
| `gv` / `gv-b` / `gv-r` / `gv-g` / `gv-a` | 普通 / 高亮 / 割点等顶点 |
| `ge` / `ge-b` / `ge-r` / `ge-g` / `ge-a` / `ge-d` | 普通 / 匹配 / 圈 / 树 / 强调 / 虚线边 |
| `vl` `wgt` `glab` `gdim` | 顶点标签 / 边权 / 图例 / 小注 |
| `halo` `halo-2` | 文字描边，压在边线上也读得清 |
| `fnode` `fnode-b/g/r/a`、`ftext` `fsmall`、`ar`、`flab` | 流程图节点、文字、箭头、分支标签 |
| `fill-b` `fill-a`、`ring` | 面/区域的半透明填充、虚线圆环 |

先画边、后画顶点圆，圆会自然盖住线段末端；箭头统一 `markerUnits="userSpaceOnUse"`、10×10。

### 5.2 代码块

```html
<div class="codebox">
  <div class="code-h"><span>代码 1 · 算法名（复杂度）</span><span class="lang">C++17</span></div>
  <pre class="code"><code><span class="kw">for</span> (...) ...</code></pre>
</div>
```

`<` `>` `&` 必须转义；关键字 `.kw`、类型 `.ty`、注释 `.cm`、函数名 `.fn`、数字 `.nu`、字符串 `.st`。
**代码后面紧跟一幅流程图**，把分支画出来——这是本课与普通讲义的区别。

---

## 六、构建与验收

```powershell
python tools/build.py     # 重建 index.html / toc.js / search-index.js，并注入 id="bN"
python tools/check.py     # 写法自检
```

验收清单：

- [x] `build.py` 无报错，`sections/` 数量与 `curriculum.py` 一致（13）
- [x] `check.py` 全绿
- [ ] 目录页卡片数 = 章节数，进度环随勾选变化
- [ ] 公式渲染为排版结果（不是原始 `$…$`）
- [ ] 每幅图可读，深色主题下仍可读
- [ ] 检索“割点”有标题命中并能定位高亮

---

## 七、约定

1. **引擎不动**：`style.css`、`app.js`、`theme.js` 由模板统一维护；本课只加 `course.css`。
2. **生成物不手改**：`index.html`、`toc.js`、`search-index.js` 由 `build.py` 重建。
3. **先构建再提交**：否则检索索引与页面锚点不同步。
4. **存储键隔离**：`lg-graph-theory.progress.v1` / `lg-graph-theory.ui.v1`，不要与其它课程重复。
5. **`sections/` 下以 `_` 开头的文件不参与构建与自检**，用来放骨架或草稿。

---

## 八、参考书目

- Robin J. Wilson, *Introduction to Graph Theory*, 5th ed. —— 直觉、历史与七桥。
- Douglas B. West, *Introduction to Graph Theory*, 2nd ed. —— 定义、定理与证明的标准。
- J. A. Bondy & U. S. R. Murty, *Graph Theory* (GTM 244) —— 网络流、连通度与算法视角。
