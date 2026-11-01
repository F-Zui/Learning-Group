# 学习模块标准模板

这是一个**可直接运行**的学习模块骨架：章节划分、目录页、左侧章节栏、右侧「本节」栏、全站检索、深浅色主题、学习进度与导入导出都已接好。新建模块时复制整个目录，只改 `tools/curriculum.py` 与 `sections/`，其余样式与交互保持一致。

```
模板/学习模块标准模板/
├── index.html                 目录页（由 tools/build.py 生成）
├── sections/                  每一节一个 HTML
│   ├── 1-1.html
│   ├── 1-2.html
│   └── 2-1.html
├── assets/
│   ├── style.css              全部版式（目录、侧栏、右栏、检索、主题）
│   ├── app.js                 全部交互（进度、侧栏、右栏、检索、主题、绘图）
│   ├── theme.js               首屏前应用主题，避免闪白
│   ├── toc.js                 模块配置 + 章节数据（生成物）
│   ├── search-index.js        全文索引 + 正文锚点（生成物）
│   └── mathjax/tex-svg.js     本地 MathJax，离线渲染公式
└── tools/
    ├── curriculum.py          章节数据源（唯一需要手写的结构文件）
    ├── build.py               生成 index.html / toc.js / search-index.js
    ├── searchindex.py         给正文块注入锚点并抽取文本
    └── check.py               单节结构自检
```

---

## 一、新建一个模块（5 步）

1. **复制目录**：把 `模板/学习模块标准模板/` 复制为 `你的模块名/`。
2. **改身份**：编辑 `tools/build.py` 顶部的 `MODULE`（标题、副标题、图标字符、存储键、导出文件名）。存储键必须与其它模块不同，否则同一浏览器下进度会串。
3. **改章节**：编辑 `tools/curriculum.py` 的 `CHAPTERS`，每节一行 `(编号, 标题, 一句话核心, 难度)`。
4. **写内容**：按 `sections/1-1.html` 的骨架写 `sections/<编号>.html`，文件名把 `2.3` 写成 `2-3.html`，`body` 上写 `data-sec="2.3"`。
5. **构建 + 自检**：

```powershell
cd 你的模块名
python tools/build.py
python tools/check.py
```

打开 `index.html` 即可。全部资源本地化，MathJax 不联网。

---

## 二、章节划分方式

```
部分 Part（可选） → 章 Chapter → 节 Section
```

| 层级 | 数据位置 | 展示位置 | 约定 |
|---|---|---|---|
| 部分 | `PARTS` | 目录页的 `Part I` 分隔行 | 超过 7 章才需要拆分；否则一个 Part 即可 |
| 章 | `CHAPTERS[n]` | 目录页章块 + 左侧栏章组 | 章号连续；`title` 短；`sub` 一句话点题 |
| 节 | `CHAPTERS[n].sections` | 目录页节卡片 + 左侧栏条目 + 右栏 | 编号 `章.节`；同一章内连续 |

**编号即路由**：`3.7 → sections/3-7.html`，`body data-sec="3.7"`，`<title>3.7 标题 · 模块名</title>`。三者必须一致，`check.py` 会校验。

**排序即学习顺序**：目录、左侧栏、上一节/下一节、`←` `→` 全部按 `curriculum.py` 的数组顺序，不按编号排序。要调整顺序，移动数组项并重编号，不要只改编号。

**每节头部（`header.sec-head`）固定四件套**：

```html
<h1>节标题</h1>
<p class="lede">一句话说明本节要解决什么（会显示在右栏「本节」概述里）</p>
<div class="meta">
  <span>第 3 章 · 导数与微分</span>
  <span>难度 <b>●●○</b></span>
  <span>前置：<a href="3-6.html">§3.6 中值定理</a></span>
  <span>关键词：<b>洛必达</b> · <b>未定式</b></span>
</div>
```

**小节标题**用 `<h2 id="s1"><span class="num">一</span>标题</h2>`，`s1…sN` 连续。右栏大纲、页内跳转、检索上下文都依赖这些 `h2`。

---

## 三、目录页样式（index.html）

```
hero（标题 / 导语 / 开始学习 / 进度环）
storage-warn（localStorage 不可用时的提示）
toolbar（检索框 + 全部/未完成/已完成 + 主题按钮 + 总进度）
srWrap（检索结果，默认隐藏）
tocWrap
  Part 分隔行
  ch-block × N
    ch-head（章号 / 章名 / 一句话 / 本章进度 n/m / 迷你进度条）
    cards（节卡片 × m）
idx-foot（导出 / 导入 / 重置）
```

- **节卡片**：复选框、编号、标题、一句话核心、难度三点、⭐（完成后显示）。点卡片进节；点复选框只切换完成状态。
- **进度环**：完成节数 / 总节数，实时更新。
- **筛选**：全部 / 未完成 / 已完成，只影响目录卡片，不影响检索结果。
- **检索结果**出现时隐藏 `tocWrap`，清空检索或用 Esc 恢复。

目录页由 `tools/build.py` 生成，**不要手改 `index.html`**。

---

## 四、左侧章节栏

- 固定左侧，宽 `--sb-w`（302px），独立滚动（`overscroll-behavior: contain`），不随正文滚动。
- 顶部：模块名 + 图标 + 总进度条 + `已完成 / 总数`。
- 章组：章号 + 章名 + 本章 `n/m`；点章头折叠/展开，折叠状态写入 `localStorage`。
- 节条目：复选框 + 编号 + 标题 + ⭐；当前节高亮左侧竖线；打开页面时自动滚动到当前节。
- 底部：全目录 / 导出进度。
- 屏幕宽度 ≤ 900px 时变为抽屉：顶栏汉堡按钮打开，遮罩点击关闭，选中链接后自动关闭。

任何页面的复选框都与目录页共享同一份进度，`storage` 事件之外的页面通过 `localStorage` + 页面刷新同步。

---

## 五、右侧「本节」栏

- 位置：正文右侧，宽 `--rail-w`（232px），`position: fixed`，自身滚动。
- 内容：
  1. 「本节」标题 + 收起按钮；
  2. 本节概述（取 `header .lede`，公式会正常渲染）；
  3. 小节大纲：`h2`（一级）与 `h3`（二级，若有），点击平滑定位。
- **宽屏（≥1420px）默认展开**，收起后正文自动加宽；状态记在 `localStorage`（`uiKey` 里的 `railoff`）。
- **窄屏默认隐藏**，点顶栏「本节目录」按钮以抽屉浮出，带遮罩；点条目后自动收起。
- 当前阅读位置由 `IntersectionObserver` 高亮对应条目。

---

## 六、检索功能

### 交互

1. 在目录页检索框输入关键词，**回车**（或点表单提交）。
2. 结果按两级排序：
   - **节标题 / 标签命中**：节编号、标题、核心一句；命中的关键词高亮。
   - **正文命中**：每条上方标出「节编号 + 节标题 + 所属小节」，下方给出命中行，以及上下各一行上下文。
3. 点标题命中 → 进入该节顶部；点正文命中 → 进入该节并**滚动到关键词所在段落**，段落短暂闪一下，关键词高亮。
4. 跳转后**下一次点击页面任意位置（或按 Esc）**，高亮自动清除。
5. 检索框右侧 `×` 清空并恢复目录；URL 带 `?q=` 时刷新后仍保留检索。

### 索引如何生成

`tools/build.py` 对每一节做一次扫描（`tools/searchindex.py`）：

- 给 `<p> <li> <td> <th> <figcaption> <blockquote> <h2> <h3>` 注入稳定锚点 `id="bN"`（已有 `id` 则沿用）；
- 抽取每块纯文本，并记录它所属的最近 `h2`；
- 输出 `assets/search-index.js`：

```js
window.SEARCH_DOCS = [{
  f: "sections/3-7.html",   // 文件
  no: "3.7",                // 编号
  t: "3.7 洛必达法则与未定式", // 标题命中用
  title: "洛必达法则与未定式",
  core: "七种未定式、使用条件与失效",
  lv: "●●○",
  tg: ["0/0", "∞/∞", "未定式转化"], // 关键词标签
  b: [["b7", "二、三个前提与三种失效", "正文……"], ...] // 正文块
}];
```

- **正文命中链接**形如 `sections/3-7.html?q=未定式#b7`。页面加载后由 `app.js` 读取 `#b7`，在块内高亮 `q`，再滚动定位。
- 正文块的纯文本上限 600 字；检索结果最多显示 200 条正文命中。
- 结果中的公式以 `…` 省略，避免把 LaTeX 源码直接展示（若命中恰在公式内部则保留原样）。

### 样式要点

- 高亮：`mark.sr-mk`（结果内）、`mark.sr-mk.hit`（跳转后）。
- 命中块闪烁：`.sr-flash`，约 2.8 秒。
- 上下文三行：`.sr-line.sr-dim`（上下各一行）、`.sr-line.sr-main`（命中行）。

---

## 七、深浅色主题

- **首屏前**：`assets/theme.js` 在 `<head>` 中同步执行，读取 `localStorage['lg.theme']` 并设置 `<html data-theme="light|dark">`，避免闪白。
- **CSS**：`:root` 是浅色变量；`:root[data-theme="dark"]` 与 `prefers-color-scheme: dark`（未显式选浅色时）覆盖同一组变量。
- **切换按钮**：`[data-theme-toggle]`，目录页在检索栏右侧，节页面在顶栏；图标随状态切换（月亮 ↔ 太阳）。
- **图表重绘**：主题切换后，`repaintPlots()` 重新读取 CSS 变量并重绘所有 `figure.plot`，保证曲线颜色与深色背景协调。
- 主题键固定为 `lg.theme`，各模块共享选择。

---

## 八、可操作功能清单

| 功能 | 位置 | 操作 | 备注 |
|---|---|---|---|
| 标记完成 / 取消 | 目录卡片、左侧栏、顶栏 | 点复选框或「标记完成」 | 完成后显示 ⭐ |
| 总进度 | 目录进度环、左侧栏进度条 | 自动 | `n / 总节数` |
| 导出 / 导入 / 重置进度 | 目录页脚、左侧栏底部 | 点击 | JSON 文件，键为节编号 |
| 上一节 / 下一节 | 节页底部 | 点击 | 也可用 `←` `→` |
| 折叠章组 | 左侧栏章头 | 点击 | 状态持久化 |
| 收起右侧栏 | 右栏「×」或顶栏按钮 | 点击 | 宽屏持久化 |
| 全站检索 | 目录检索框 | 输入 + 回车 | Esc 清空 |
| 跳到关键词 | 检索结果 | 点击 | 滚动 + 高亮，下次点击消失 |
| 筛选 | 目录工具条 | 全部 / 未完成 / 已完成 | 仅影响卡片 |
| 深浅色 | 目录工具条 / 节页顶栏 | 点击 | 记在 `lg.theme` |
| 页内定位 | 右侧栏大纲 | 点击 | 平滑滚动 |

**存储键**（可在 `tools/build.py` 的 `MODULE` 中改）：

| 键 | 内容 |
|---|---|
| `MODULE.progressKey` | 节编号 → 完成时间戳 |
| `MODULE.uiKey` | 章折叠、右栏收起等界面状态 |
| `lg.theme` | `light` / `dark` |

---

## 九、内容组件（与样式配套）

| 组件 | 写法 | 用途 |
|---|---|---|
| 定义 / 定理 | `<div class="def"><span class="tag">定义（…）</span>…</div>` | 严格陈述 |
| 证明 | `<div class="prf"><span class="tag">证明</span>…<span class="qed">∎</span></div>` | 补跳步 |
| 为什么 | `<div class="why">…</div>` | 动机、直觉 |
| 洞见 / 提示 / 易错 | `insight` / `note` / `warn` | 阅读提示 |
| 例题 | `<div class="ex"><div class="ex-h">例 1 <span>副标题</span></div>…</div>` | 示范 |
| 思考点 | `<div class="think"><div class="tq">问</div><div class="ta"><b>引导</b>…</div></div>` | 发散 |
| 习题 | `<ol class="exs"><li><div class="q">…</div><div class="idea"><b>思路</b>…</div><div class="ans"><b>答案</b>…</div></li></ol>` | 先思路后答案 |
| 小结 | `<div class="keybox"><div class="kb-h">一页纸</div><ul>…</ul></div>` | 收束 |
| 进阶折叠 | `<details class="deep"><summary>…</summary>…</details>` | 选读 |
| 出处 | `<span class="ref">Rudin Ch.3</span>` | 参考书定位 |
| 表格 | `<table class="tbl">…</table>` | 对照 |
| 图 | `<figure class="plot" data-fn="x^2" …><figcaption>…</figcaption></figure>` | 自动绘图 |
| 手绘图 | `<figure class="fig"><svg class="dgm" viewBox="0 0 520 300">…</svg><figcaption>…</figcaption></figure>` | 几何示意 |

公式：行内 `$…$`，行间 `$$…$$`；数学里的 `<` `>` 写成 `\lt` `\gt`；`aligned` 用 `&amp;` 对齐。

### `figure.plot` 常用属性

| 属性 | 含义 |
|---|---|
| `data-fn` | 一个或多个函数，`;` 分隔；乘法写 `*`，幂写 `^` |
| `data-x` / `data-y` | 视窗范围；`data-y` 省略则自动取景 |
| `data-fill="a,b"` | 曲线与 $x$ 轴之间着色 |
| `data-between="a,b"` | 两条曲线之间着色 |
| `data-tangent="x0"` / `data-secant="x0,x1"` | 切线 / 割线 |
| `data-rect="n,a,b,mid"` | 黎曼矩形 |
| `data-eps="x0,L,eps,delta"` | ε-δ 双带 |
| `data-dots` / `data-dotlabels` | 标点与标签 |
| `data-legend` | 图例 |
| `data-type="line"` | 数轴（`data-points`、`data-interval`、`data-hollow`） |
| `data-type="field"` | 方向场（`data-fn` 含 `x,y`） |

---

## 十、模块配置（`window.MODULE`）

由 `tools/build.py` 写入 `assets/toc.js`，`app.js` 读取：

| 字段 | 示例 | 说明 |
|---|---|---|
| `title` | `学习模块模板` | 侧栏品牌与页面标题 |
| `subtitle` | `Learning Module Template` | 品牌副行 |
| `mark` | `▦` | 品牌图标字符 |
| `progressKey` | `lg-template.progress.v1` | 进度存储键，**各模块必须不同** |
| `uiKey` | `lg-template.ui.v1` | 界面状态键 |
| `progressFile` | `learning-progress.json` | 导出文件名 |

---

## 十一、构建与验收

```powershell
python tools/build.py     # 生成 index.html / toc.js / search-index.js（会重建锚点）
python tools/check.py     # 单节结构自检：编号、标题、图注、习题思路与答案、公式配对、链接
```

验收清单：

- [ ] `python tools/build.py` 无报错，`sections` 数量与 `curriculum.py` 一致
- [ ] 目录页卡片数量与章节数一致，章节计数、进度环正常
- [ ] 每节 `check.py` 通过
- [ ] 检索标题命中排在正文命中之前；点击命中能定位且高亮；下一次点击高亮消失
- [ ] 右栏可收起、可滚动、当前项高亮
- [ ] 深浅色切换后图表重绘、刷新后保持
- [ ] 窄屏（≤900px）左侧栏为抽屉，右栏可浮出
- [ ] 导出 JSON 后重置，再导入能恢复 ⭐

---

## 十二、约定（保持模块间一致）

1. **引擎不动**：`assets/style.css`、`assets/app.js`、`assets/theme.js` 由模板统一维护；模块只写 `curriculum.py` 与 `sections/`。
2. **生成物不手改**：`index.html`、`assets/toc.js`、`assets/search-index.js` 由 `build.py` 重建。
3. **一文件一节**：文件名、`data-sec`、`<title>` 前缀三者一致。
4. **先构建再提交**：提交前必须跑 `build.py`，否则检索索引与页面锚点会不同步。
5. **存储键隔离**：每个模块用自己的 `progressKey` / `uiKey`，避免同一浏览器下互相覆盖。
