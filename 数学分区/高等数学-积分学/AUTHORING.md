# 写作规范（供生成每一节 HTML 使用）

> 目标：**少文字、多数学语言、多图像**。读者是愿意自己动笔的大一学生。
> 参照物：《普林斯顿微积分读本》的图密度 + Rudin/Abbott 的符号密度。

---

## 0. 硬性清单（缺一不可）

| 项 | 要求 |
|---|---|
| 文件位置 | `sections/<编号>.html`，编号中的点换成短横：`3.2` → `sections/3-2.html` |
| 篇幅 | 正文汉字 **900–1600 字**（公式、表格、图注不计） |
| 图 | **≥ 4 幅**（其中 ≥ 2 幅用 `figure.plot` 自动绘制，其余可用手写 SVG） |
| 例题 | **≥ 4 个** `.ex` |
| 习题 | **≥ 6 道** `.exs > li`，每题**先思路、后答案** |
| 思考点 | **≥ 2 个** `.think` |
| 原理/证明 | 至少 1 个 `.prf` 或 `.why`；难度 ●●● 的节至少 1 个 `.deep` |
| 小结 | 结尾 1 个 `.keybox`，4–6 条 |
| 标题 | 恰好 1 个 `h1`；3–6 个 `h2`，每个带 `id="s1"`…`id="sN"` |

不要写“本节将介绍……”“综上所述”这类空话。不要重复目录里已有的元信息。
段落最多 3 句；能用公式说清楚的，不要用句子说。

---

## 1. 文件骨架（直接复制，只改标题与内容）

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>3.2 求导法则 · 微积分精讲</title>
<link rel="stylesheet" href="../assets/style.css">
<script defer src="../assets/app.js"></script>
</head>
<body data-sec="3.2">
<main class="content">
<header class="sec-head">
  <h1>求导法则</h1>
  <p class="lede">一句话点出本节的核心机制，可用公式。</p>
  <div class="meta">
    <span>第 3 章 · 导数与微分</span>
    <span>难度 <b>●●○</b></span>
    <span>前置：<a href="3-1.html">§3.1 导数</a></span>
    <span>关键词：<b>乘积法则</b> · <b>链式法则</b></span>
  </div>
</header>

<h2 id="s1"><span class="num">一</span>标题</h2>
…

<div class="keybox">
  <div class="kb-h">一页纸</div>
  <ul><li>…</li></ul>
</div>
</main>
</body>
</html>
```

`body data-sec` 必须与编号一致（app.js 靠它生成侧栏高亮、上下节导航、完成标记）。

---

## 2. 数学公式

- 行内 `$…$`，行间 `$$…$$`。MathJax 本地加载，无需联网。
- **数学里的 `<` `>` 写成 `\lt` `\gt`**（避免被 HTML 解析）。
- `aligned` 环境里的对齐符写成 `&amp;`：

```html
$$\begin{aligned}
(fg)' &amp;= \lim_{h\to 0}\frac{f(x+h)g(x+h)-f(x)g(x)}{h}\\
      &amp;= f'(x)g(x)+f(x)g'(x)
\end{aligned}$$
```

- 常用宏：`\dfrac \tfrac \lim \sum \int \mathbb{R} \varepsilon \delta \le \ge \to \mapsto \infty \partial \nabla \iint \oint`。
- 中文放进公式用 `\text{…}`。
- 不要用 `\label`、`\tag`、`\begin{equation}`（本模板不加载相应扩展）。
- 一个 `$$…$$` 只放一个公式或一组 `aligned`；不要在一个块里塞多行独立公式。

---

## 3. 组件（类名固定，不要自创）

### 定义 / 定理 / 推论
```html
<div class="thm">
  <span class="tag">定理 3.2（链式法则）</span>
  <p>设 $g$ 在 $x$ 可导，$f$ 在 $g(x)$ 可导，则</p>
  $$(f\circ g)'(x)=f'\bigl(g(x)\bigr)g'(x)$$
</div>
```
`class="def"` 用于定义（同款样式，蓝色）。

### 证明
```html
<div class="prf">
  <span class="tag">证明</span>
  <p>由 … 得 …<span class="qed">∎</span></p>
</div>
```

### 为什么（动机、思想来源）
```html
<div class="why">
  <span class="tag">为什么</span>
  <p>…<span class="ref">Courant Ch.3</span></p>
</div>
```

### 洞见 / 易错 / 普通提示
```html
<div class="insight"><span class="tag">洞见</span><p>…</p></div>
<div class="warn"><span class="tag">易错</span><p>…</p></div>
<div class="note"><span class="tag">注</span><p>…</p></div>
```

### 例题
```html
<div class="ex">
  <div class="ex-h">例 2 <span>用定义求导</span></div>
  <p>求 $f(x)=x^{3}$ 在 $x=1$ 处的导数。</p>
  <p class="sol"><b>解</b>　$\dfrac{(1+h)^{3}-1}{h}=3+3h+h^{2}\to 3$。</p>
</div>
```

### 思考点（一两句发问，紧跟引导）
```html
<div class="think">
  <div class="tq">如果 $f$ 在 $x_0$ 可导，$|f|$ 在 $x_0$ 一定可导吗？</div>
  <div class="ta"><b>引导</b>　考虑 $f(x)=x$ 与 $f(x)=x^{2}$ 在 $0$ 附近：绝对值把负值翻到上方，可能制造尖角。</div>
</div>
```

### 进阶（默认折叠）
```html
<details class="deep">
  <summary>进阶 · 用 Carathéodory 定义重证链式法则（Abbott / Rudin）</summary>
  <p>…</p>
</details>
```

### 习题（先思路，后答案；答案必须给结果）
```html
<ol class="exs">
<li>
  <div class="q">求 $\displaystyle\lim_{x\to 0}\frac{\sin 3x}{x}$。</div>
  <div class="idea"><b>思路</b>　凑成 $\dfrac{\sin u}{u}$ 的标准形。</div>
  <div class="ans"><b>答案</b>　$3$。</div>
</li>
</ol>
```

### 表格 / 小结 / 教材出处
```html
<table class="tbl">
  <thead><tr><th>函数</th><th>导数</th></tr></thead>
  <tbody><tr><td>$\sin x$</td><td>$\cos x$</td></tr></tbody>
</table>

<div class="keybox"><div class="kb-h">一页纸</div><ul><li>…</li></ul></div>

<span class="ref">Stewart Ch.3</span>
```

出处只在有把握时写，**只写到章**（`Stewart Ch.3`、`Thomas Ch.11`、`Abbott 1.3`、`Rudin 3`、`Apostol 4`、`Courant Ch.2`、`Zorich 1.2`）。不要编造小节号。

---

## 4. 图像

### 4.1 自动绘图 `<figure class="plot" …>`

```html
<figure class="plot" data-fn="x^2" data-x="-1.5,2.5" data-tangent="1"
        data-dots="1,1" data-dotlabels="P">
  <figcaption>切线斜率 $f'(1)=2$：割线的极限位置。</figcaption>
</figure>
```

| 属性 | 含义 |
|---|---|
| `data-fn` | 一个或多个函数，用 `;` 分隔（第二、三条用不同颜色）。只能含 `x`；`data-type="field"` 时含 `x,y` |
| `data-x` / `data-y` | 视窗范围 `min,max`；`data-y` 省略则自动取景 |
| `data-fill="a,b"` | 第一条曲线与 $x$ 轴之间在 $[a,b]$ 上着色 |
| `data-between="a,b"` | 前两条曲线之间着色 |
| `data-tangent="x0"` | 在 $x_0$ 画切线、切点与竖直虚线 |
| `data-secant="x0,x1"` | 画割线 |
| `data-rect="n,a,b,mid"` | 用 $n$ 个矩形逼近第一条曲线下的面积（第四项可省，或 `left`/`right`/`mid`） |
| `data-eps="x0,L,eps,delta"` | 画 ε-δ 图：$y=L\pm\varepsilon$ 蓝带、$x=x_0\pm\delta$ 红带 |
| `data-dots="x,y;x,y"` + `data-dotlabels="P;Q"` | 标点 |
| `data-vline` / `data-hline` | 竖直/水平虚线（多个用 `;`） |
| `data-legend="f(x);g(x)"` | 右上角图例 |
| `data-type="line"` | 数轴：`data-range="min,max"`、`data-points="1;2.5"`、`data-labels="a;b"`、`data-interval="1,2"`、`data-hollow="2"` |
| `data-type="field"` | 方向场：`data-fn="x+y"`（$y'=f(x,y)$） |

表达式是 JS 语法，**乘法必须写 `*`**（`2*x` 不能写 `2x`），幂用 `^`：

```
x^2     1/x     exp(-x^2)     sin(x)/x     log(x)     sqrt(1-x^2)     abs(x)     3*x-1
```

已知函数：`sin cos tan exp log(=ln) sqrt abs PI E sinh cosh tanh`。

### 4.2 手写示意图 `<svg class="dgm" viewBox="0 0 520 300">`

几何体、向量、面积分割、映射示意等用内联 SVG。统一约定：

```html
<figure class="fig">
  <svg class="dgm" viewBox="0 0 520 300" role="img">
    <line x1="40" y1="240" x2="480" y2="240" class="ax"/>
    <path d="M40,240 Q260,20 480,240" class="blue"/>
    <rect x="150" y="120" width="40" height="120" class="fill-b"/>
    <text x="252" y="270" class="lg" text-anchor="middle">x</text>
  </svg>
  <figcaption>…</figcaption>
</figure>
```

可用类：`ax`（坐标轴）、`thin`、`dash`、`blue`、`red`、`green`（线）、`fill-b`/`fill-r`/`fill-g`（浅色填充）、`dot`/`dot-r`（实心点）、`hollow`（空心点）、`lg`（斜体数学标签）、`sm`（小字）。不要写死颜色，交给主题。

图注 1 行、≤ 40 字，**必须含数学信息**，不要写“如图所示”。

---

## 5. 语气与深度

- 先给机制，再给定义；先给图，再给式子；先给反例，再给定理。
- 每节至少回答一次“为什么可以这样”，用 `.why` 或 `.prf`。
- 证明要短：把跳步补上，但不要写成散文。长证明拆成 2–4 个 `$$` 片段。
- 例题要有变式：一个标准、一个稍难、一个应用、一个易错。
- 习题 6–10 道，按“基础 3 / 进阶 2 / 挑战 1”排列，难度递增。
- 专业术语首次出现时给英文：`导数（derivative）`。
- 连续两段不得都以“设”开头；避免“我们”“大家”。

---

## 6. 自检

写完后运行：

```
python tools/site/check.py sections/3-2.html
```

必须输出 `OK`。检查项包括：文件存在、`data-sec` 匹配、组件数量、图注齐全、公式定界符成对、`<` 未转义、链接目标存在、`data-fn` 表达式可解析。
