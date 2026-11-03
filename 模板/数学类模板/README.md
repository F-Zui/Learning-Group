# 数学类模板

面向**数学课 / 算法竞赛数学基础课 / 专题课**的课件标准版式。

一句话区别：**先推导、后定理；定理之后还要落到算法**。每节都按「动机 → 推导卡 → 定义/定理 → 证明 → 图像 → 例题 → 算法落地卡 → 习题 → 一页纸」走，`tools/check.py` 会逐条核对这个顺序与组件是否齐备。

```
数学类模板/
├── index.html                 目录页（tools/build.py 生成，勿手改）
├── sections/
│   ├── 1-1.html               ★ 范本 A「纯理论节」：推导卡 → 定义 → 定理 → 证明 → 图 → 例题 → 习题
│   ├── 1-2.html               示例：连续与一致连续
│   ├── 2-1.html               ★ 范本 B「定理 + 算法节」：加代码块、算法流程图、算法落地卡
│   └── _骨架.html             空白骨架（不参与构建，复制它开新节）
├── assets/
│   ├── style.css              版式引擎（勿改）
│   ├── app.js                 交互引擎：侧栏 / 右栏 / 检索 / 主题 / 进度 / 自动绘图（勿改）
│   ├── theme.js               首屏前应用主题（勿改）
│   ├── course.css             课程补充样式：推导卡、算法落地卡、代码块、算法流程图
│   ├── toc.js                 模块配置 + 章节数据（生成物）
│   ├── search-index.js        全文索引 + 正文锚点（生成物）
│   └── mathjax/tex-svg.js     本地 MathJax，离线渲染公式
└── tools/
    ├── curriculum.py          课程结构 + MODULE（唯一需要手写的结构文件）
    ├── build.py               生成 index.html / toc.js / search-index.js
    ├── searchindex.py         给正文块注入 id="bN" 并抽取检索文本
    └── check.py               数学课件写法自检
```

> **引擎不动**：`style.css`、`app.js`、`theme.js` 三个文件由模板统一维护，任何课程都不要改。
> 需要新组件时，把样式追加到课程自己的 `assets/course.css` 里。

---

## 一、新建一门课（5 步）

1. **复制目录**：把 `模板/数学类模板/` 复制为你的课程目录。
2. **改身份**：编辑 `tools/curriculum.py` 顶部的 `MODULE`（标题、副标题、图标、`kicker`、`description`、`searchHint`、`lede`、**存储键**）。`progressKey` / `uiKey` 必须与其它课程不同，否则同一浏览器下进度会串。
3. **改章节**：编辑 `PARTS` 与 `CHAPTERS`，每节一行 `(编号, 标题, 一句话核心, 难度)`。
4. **写内容**：复制 `sections/_骨架.html` 为 `sections/<编号>.html`（`2.3` → `2-3.html`），按下面的七段式填。
5. **构建 + 自检**：

```powershell
cd 你的课程目录
python tools/build.py
python tools/check.py
```

打开 `index.html` 即可。全部资源本地化，MathJax 不联网。

---

## 二、每节的顺序（不能换）

```
一、动机        为什么需要它：一个算不出来的量、一个反例、一个旧工具的失效点
二、推导卡      问题 → 尝试 → 验证 → 落定理        ← 必须在定理之前
三、定理/证明   .thm + .prf（以 ∎ 收尾）
四、图像         figure.plot（函数图像）或 figure.fig（几何示意）
五、例题         2 个起步：标准情形 + 变式/反例
六、算法落地     codebox + 算法流程图 + .walk（只有“定理能变成算法”的节才需要）
七、习题         3~6 题，先思路后答案
八、一页纸       3~5 条，只放会反复用到的东西
```

两种节型：

| 节型 | 适用 | 必须有的组件 |
|---|---|---|
| **纯理论节**（范本 `1-1.html`） | 极限、连续、中值定理、二次剩余这类“只有陈述与证明”的节 | 推导卡、定义/定理、证明、2 图、2 例题、3 习题、1 思考点、一页纸 |
| **定理 + 算法节**（范本 `2-1.html`） | 凡是有算法价值或建模价值的结论（gcd、CRT、快速幂、筛法、反演……） | 上面全部 **+** `.codebox`、算法流程图、`.walk` 落地卡 |

篇幅：正文汉字 **1200 起**（`check.py` 只卡下限 1000）。单条定理链的短节约 1.2k–2.5k，多条推导链的长节 3k–6k 也成立——模板自带的 `1-1` / `1-2` / `2-1` 分别是 2.4k / 5.6k / 2.3k，可以对照着估。

---

## 三、组件速查

### 3.1 严格陈述

| 组件 | 写法 | 硬规则 |
|---|---|---|
| 定义 | `<div class="def"><span class="tag">定义（…）</span>…</div>` | 必须以 `.tag` 开头 |
| 定理 | `<div class="thm"><span class="tag">定理（…）</span>…</div>` | 必须先有推导卡 |
| 证明 | `<div class="prf"><span class="tag">证明</span>…<span class="qed">∎</span></div>` | 必须以 `∎` 收尾 |
| 读法 / 为什么 / 提示 / 易错 | `.insight` / `.why` / `.note` / `.warn` | 都必须有 `.tag` |
| 出处 | `<span class="ref">Rudin §4.2</span>` | 行内用 |
| 表格 | `<table class="tbl">…</table>` | 必须带 `tbl` 类 |

### 3.2 推导卡 `.derive`（定理之前）

```html
<div class="derive">
  <div class="derive-h"><span class="dk">推导</span><b>在知道“某某定理”之前</b><span class="dsub">需求 → 尝试 → 验证 → 定理</span></div>
  <div class="derive-q"><b>问题</b>　一个具体需求，能立刻动手算。</div>
  <div class="dstep">
    <div class="dn">1</div>
    <div class="dh">这一步做什么</div>
    <p>枚举 / 试错 / 观察小例子，允许出现失败尝试。</p>
    <div class="dcheck"><b>观察</b>　把这一步得到的事实单独点出来。</div>
  </div>
  <!-- 2~5 步 -->
  <div class="derive-end"><b>于是我们得到：</b>……</div>
</div>
```

- 四段固定：**问题 → 尝试 → 验证 → 落定理**；`derive-end` 之后紧接着才是 `.thm` 与 `.prf`。
- 步数 3–5，每步只做一件小事，`dcheck` 里写「为什么可以这样 / 这一步在解决什么」。
- 一个定理一张卡；互相依赖的多个定理可以共用一张，但卡头要写清「覆盖：定理 A / 定理 B」。
- 推导卡里**不许提前使用定理结论**，也不许写「显然」「易证」。

### 3.3 算法落地卡 `.walk`（定理之后）

```html
<div class="walk">
  <div class="walk-h"><span class="wk">算法落地</span><b>用具体数字跑一遍</b><span class="cover">覆盖：定理 / 算法</span></div>
  <div class="walk-req"><b>需求</b>　一组能手算的输入 + 期望输出。</div>
  <div class="walk-step">
    <div class="ws-h"><span class="ws-n">1</span>这一步做什么（对应定理的哪一步）</div>
    <p>用具体数字说明。</p>
    <pre class="snip"><code>// 当前步骤的代码</code></pre>
    <div class="ws-why"><b>为什么</b>　动机、构造理由、边界（0 / 负数 / 溢出）。</div>
  </div>
  <!-- 2~5 步 -->
  <div class="walk-oi"><b>竞赛用法</b>　看到什么条件想到它；把什么复杂度降到什么；常见坑。
    <div class="tags"><span>模型：……</span><span>复杂度：O(log n)</span><span>常见坑：……</span></div>
  </div>
</div>
```

硬规则（`check.py` 会数）：

- 每一步必须有 `<pre class="snip">` **和** `.ws-why`，缺一报错；
- 必须有 `.walk-req` 与 `.walk-oi`；`.walk-oi` 建议带 `.tags`；
- 代码是“证明步骤的可执行对应物”，不是贴一份完整 AC 代码；
- 变量名尽量与数学符号对应，例如 $d=\gcd(a,b)$ 对应 `long long d = gcd(a,b);`。

### 3.4 代码块与算法流程图

```html
<div class="codebox">
  <div class="code-h"><span>代码 1 · 标题：这段代码做什么</span><span class="lang">C++17</span></div>
  <pre class="code"><code>…</code></pre>
</div>
```

代码高亮类：`.kw` 关键字 / `.ty` 类型 / `.fn` 函数名 / `.st` 字符串 / `.nu` 数字 / `.cm` 注释 / `.op` 运算符。
代码里的 `<`、`&` 必须写成 `&lt;`、`&amp;`。

**有代码就必须有流程图**（`figure.fig` + `svg.dgm`，节点类来自 `course.css`）：

| 类 | 用途 |
|---|---|
| `fnode` / `fnode-b` / `fnode-g` / `fnode-r` / `fnode-a` | 普通 / 输入 / 成功 / 返回 / 判断节点 |
| `ftext` / `ftext-b` / `fsmall` | 节点文字 / 强调文字 / 小字 |
| `ar` / `ar-d` | 实线箭头 / 虚线箭头 |
| `flab` | 分支标注（是 / 否 / 循环） |
| `fdot` | 汇合点 |

流程图必须与代码分支一一对应；图注要写清「哪个节点对应哪一行」。

### 3.5 其余组件

| 组件 | 写法 | 用途 |
|---|---|---|
| 例题 | `<div class="ex"><div class="ex-h">例 1 <span>副标题</span></div><p>题面</p><p class="sol"><b>解</b>…</p></div>` | 每题必须有 `.ex-h` 与 `.sol` |
| 习题 | `<ol class="exs"><li><div class="q">…</div><div class="idea"><b>思路</b>…</div><div class="ans"><b>答案</b>…</div></li></ol>` | 先思路后答案，缺一报错 |
| 思考点 | `<div class="think"><div class="tq">问</div><div class="ta"><b>引导</b>…</div></div>` | `.tq` 与 `.ta` 缺一不可 |
| 一页纸 | `<div class="keybox"><div class="kb-h">一页纸</div><ul>…</ul></div>` | 必须有 `.kb-h` |
| 进阶折叠 | `<details class="deep"><summary>进阶 · …（参考书章节）</summary>…</details>` | 主线不能依赖它 |
| 小标签行 | `<div class="chip-row"><span>…</span></div>` | 关键词、难度、前置 |
| 补充说明 | `<div class="formula-note">…</div>` | 灰色虚线框的旁注 |

---

## 四、公式与符号排版

| 规则 | 写法 |
|---|---|
| 行内公式 | `$x^{2}$`（`$` 内侧不留空格） |
| 行间公式 | `$$…$$` 独占一行，前后各空一行，**不要**用 `<p>` 包住 |
| 小于 / 大于 | 公式里写 `\lt`、`\gt`，**不能**直接写 `<` `>` |
| 对齐 | `\begin{aligned} … &amp;= … \\ … &amp;= … \end{aligned}`（`&` 必须写 `&amp;`） |
| 分段函数 | `\begin{cases} x, &amp; x\ge0 \\ -x, &amp; x\lt0 \end{cases}` |
| 集合与数域 | `\mathbb{R}`、`\mathbb{N}`、`\mathbb{Z}`、`\mathbb{Q}` |
| 极限 | `\lim\limits_{x\to a}`（行内也要 `\limits`） |
| 分式 | 行内 `\tfrac{a}{b}`，行间 `\dfrac{a}{b}`，独立成行用 `\frac` |
| 文本夹在公式里 | `\text{或}`、`\text{当 }x\gt0` |

---

## 五、图：`figure.plot` 与 `figure.fig`

### 5.1 自动绘图 `figure.plot`

支持 `+ - * / ^`、`abs()`、`sqrt()`、`exp()`、`log()`、`sin()`、`cos()`、`tan()`、`pi`、`e`，多个函数用 `;` 分隔。

| 属性 | 含义 |
|---|---|
| `data-fn` | 一个或多个函数，`;` 分隔 |
| `data-x` / `data-y` | 视窗范围 `min,max`；`data-y` 省略则自动取景 |
| `data-fill="a,b"` | 曲线与 $x$ 轴之间着色 |
| `data-between="a,b"` | 两条曲线之间着色 |
| `data-tangent="x0"` / `data-secant="x0,x1"` | 切线 / 割线 |
| `data-rect="n,a,b,side"` | 黎曼矩形，`side` 取 `left`/`mid`/`right` |
| `data-eps="x0,L,eps,delta"` | ε-δ 双带 |
| `data-dots="x1,y1;x2,y2"` / `data-dotlabels="P;Q"` | 标点与标签 |
| `data-hline="y"` / `data-vline="x"` | 水平 / 垂直虚线 |
| `data-legend="y₁;y₂"` | 图例 |
| `data-type="line"` | 数轴：配合 `data-range`、`data-points`、`data-labels`、`data-interval`、`data-hollow` |
| `data-type="field"` | 方向场：`data-fn` 里含 `x,y` |

### 5.2 手绘示意 `figure.fig`

`svg.dgm` 可用类：`lg`/`sm`（字号）、`ax`/`thin`/`dash`（线）、`blue`/`red`/`green`（曲线）、`fill-b`/`fill-r`/`fill-g`（半透明填充）、`dot`/`dot-r`/`hollow`（点）。
`viewBox` 建议 `0 0 520 300`；算法流程图用 `data-wide` 放宽到 620px。

图注不是“如图所示”，而是“看图该看出什么”：哪条线对应定义里的哪个条件、哪一段是反例、哪个量在变。

---

## 六、节头四件套

```html
<header class="sec-head">
  <h1>节标题</h1>
  <p class="lede">一句话说明本节解决什么、学完能做什么（右栏「本节」概述取它）</p>
  <div class="meta">
    <span>第 3 章 · 章名</span>
    <span>难度 <b>●●○</b></span>
    <span>前置：<a href="3-1.html">§3.1 某某</a></span>
    <span>关键词：<b>关键词一</b> · <b>关键词二</b></span>
  </div>
</header>
```

- `难度` 与 `curriculum.py` 里的难度数字一致（1/2/3）。
- `关键词` 是全站检索的标签命中来源，3 个左右，用 `·` 分隔。
- `前置` 指向真正的前置节；没有前置写「前置：无」。

---

## 七、目录页、侧栏、右栏、检索、主题

与 `../学习模块标准模板/` 一致，这里只列数学场景的用法要点：

| 功能 | 位置 | 说明 |
|---|---|---|
| 全站检索 | 目录页检索框，回车 | 搜 `ε-δ`、`exgcd`、`Möbius`；标题命中排在正文命中之前 |
| 跳到命中处 | 点正文命中 | 进入该节并滚动到关键词所在段落，闪一下；下次点击页面（或 Esc）清除高亮 |
| 右侧「本节」 | 正文右栏 | 自动列出 `h2`/`h3` 大纲；宽屏默认展开 |
| 左侧章节栏 | 正文左侧 | 按 `curriculum.py` 顺序列出全部节，可勾选完成 |
| 深浅色 | 目录工具条 / 节页顶栏 | 切换后图像与 SVG 自动换色 |
| 进度 | 目录进度环、侧栏 | 存本机浏览器，可导出 / 导入 JSON |

**排序即学习顺序**：目录、侧栏、上一节/下一节、`←` `→` 全部按数组顺序，不按编号排序。调整顺序要移动数组项并重编号。

---

## 八、构建与验收

```powershell
python tools/build.py     # 生成 index.html / toc.js / search-index.js，并注入 id="bN"
python tools/check.py     # 单节写法定检；也可 python tools/check.py sections/1-1.html
```

构建是**幂等**的：重复执行不会改动已生成的锚点，新块从「已有最大编号 + 1」开始，不会与历史 id 撞车。

`check.py` 检查项：

| 类别 | 具体 |
|---|---|
| 身份 | `data-sec`、文件名、`<title>` 前缀三者一致；五个资源引用齐全（含 `course.css`） |
| 标题 | `h1` 恰好 1 个；`h2` 为 `s1…sN` 连续 |
| 推导卡 | ≥1 张；**每个 `.thm` 之前必须已有推导卡**；卡内四段齐全，步数 ≥2 |
| 陈述 | 定义/定理/证明等盒子必须有 `.tag`；`.prf` 必须以 `∎` 收尾 |
| 落地卡 | 有代码就必须有 `.walk`；每步必须有 `.snip` 与 `.ws-why`；必须有需求和竞赛用法 |
| 代码 | `pre` 内 `<` `&` 必须转义；有代码就必须有流程图（`fnode`） |
| 例题/习题 | 例题 ≥2（`.ex-h`+`.sol`）；习题 ≥3（`.idea`+`.ans`） |
| 图 | ≥2 幅且都有 `figcaption`；`figure.plot` 只能用受支持的 `data-*` |
| 公式 | `$` / `$$` 成对；公式内 `<` `>` `&` 未转义即报错 |
| 篇幅 | 正文汉字 <1000 报错，<1200 提醒 |

验收清单：

- [ ] `python tools/build.py` 无报错，节数与 `curriculum.py` 一致
- [ ] `python tools/check.py` 全绿
- [ ] 每个定理前面都有推导卡，定理与证明排在推导之后
- [ ] 每张落地卡都是「需求 → 3–5 步 → 每步代码 → 为什么 → 竞赛用法」
- [ ] 流程图与代码分支一致，图注写清对应关系
- [ ] 公式全部渲染（不是原始 `$…$` 文本），深色主题下公式与图仍可读
- [ ] 390px 窄屏无横向溢出（行间公式可横向滚动）
- [ ] 检索 `exgcd` 之类能命中正文并定位；右栏大纲与 `h2` 一一对应

---

## 九、约定（各数学课程之间保持一致）

1. **引擎不动**：`style.css`、`app.js`、`theme.js` 由模板统一维护；新样式只追加到 `assets/course.css`。
2. **生成物不手改**：`index.html`、`assets/toc.js`、`assets/search-index.js` 由 `build.py` 重建。
3. **一文件一节**：文件名、`data-sec`、`<title>` 前缀三者一致；`sections/` 下以 `_` 开头的文件不参与构建与自检。
4. **先构建再提交**，否则检索索引与页面锚点会不同步。
5. **存储键隔离**：每门课用自己的 `progressKey` / `uiKey`。
6. **不写占位**：不留 `TODO`、`FIXME`、「这里写」。

---

## 十、与其它模板的差异

| 项 | 学习模块标准模板 | 数学类模板 | 算法类模板 |
|---|---|---|---|
| 定位 | 任意学科的通用骨架 | 数学课件：先推导后定理，定理落到算法 | 算法竞赛教程：一节一个算法闭环 |
| 定理 | 无 | **推导卡 → 定理 → 证明 → 落地卡** | 无（用例题与拆解代替） |
| 代码 | 可选 | 有算法价值的定理必须配 `.codebox` + `.walk` | 每节 2~5 段完整程序 + 逐行拆解 |
| 图 | `figure.plot` | `plot` + `figure.fig`（几何示意 / 算法流程图） | `figure.dia` 纯 HTML 图解 + `plot` |
| 自检 | 通用结构 | 结构 + 数学陈述规范 + 推导/落地卡 | 结构 + 教学闭环 + 代码逻辑图 |
| 范本 | `sections/1-1.html` | `sections/1-1.html`（理论）/ `sections/2-1.html`（算法） | `01.html` / `03.html`（挑战 2） |
