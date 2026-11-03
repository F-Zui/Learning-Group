# 算法类模板

面向**算法竞赛教程**的课件标准版式：一节 = 一个完整算法应用的闭环。

```
新函数拆解 → 例题（题面 / 思路 / 完整代码 / 逐行拆解）→ 易错清单
→ 数学补给 → 举一反三（每题折叠解析）→ 自测 → 挑战题（提示 → 思路 → 题解）→ 挑战 2
```

左侧章节栏、右侧本节目录、全站全文检索、⭐/🌟 完成标记都已接好；作者只写正文，锚点、本节目录、目录页与检索索引全部由 `tools/build.py` 生成。

```
算法类模板/
├── index.html                 目录页（生成物，勿手改）
├── 01.html 02.html 03.html    第 1~3 节（手写；锚点与本节目录由构建器回填）
├── assets/
│   ├── style.css              全部版式（引擎，勿改）
│   ├── app.js                 侧栏 / 勾选 / 检索 / 本节目录（引擎，勿改）
│   ├── toc.js                 window.MODULE + window.COURSE（生成物）
│   └── search-index.js        全文索引（生成物，按需加载）
└── tools/
    ├── curriculum.py          课程结构 + MODULE（唯一需要手写的结构文件）
    ├── build.py               扫描页面 → 注入锚点 → 重建本节目录 → 生成目录页与索引
    └── check.py               单节结构自检
```

---

## 一、新建一门课（5 步）

1. **复制目录**：把 `模板/算法类模板/` 复制为你的课程目录。
2. **改身份**：编辑 `tools/curriculum.py` 顶部的 `MODULE`（`title`、`heroTitle`、`heroSub`、`footer`、`storePrefix`、`rtocKey`）。`storePrefix` / `rtocKey` 必须与其它课程不同，否则同一浏览器下进度会串。
3. **改结构**：编辑 `GROUPS`（每组若干节）；`id` 决定文件名（`7` → `07.html`）与 `data-lesson="7"`；`CH2_FROM` 决定第几节起出现挑战 2。
4. **写页面**：复制 `01.html` 为 `NN.html`，改第二节列的七处「接口」，再写内容。
5. **构建 + 自检**：

```powershell
cd 你的课程目录
python tools/build.py
python tools/check.py
```

---

## 二、一节页面的七处「接口」

复制 `01.html` 后，只要改这七处，其余交给构建器：

| 位置 | 写什么 |
|---|---|
| `<title>` | `NN · 节标题 · 模块名` |
| `<body data-lesson="N">` | 节号，与文件名数字一致 |
| `<h1>` | `NN · 节标题` |
| `.topbar` 里的 `第 N / 总数 节` | 手写，`check.py` 会核对总数 |
| `div.sub` | 本节提要，一句话说清“学完能做什么”（右侧本节目录的概述取它） |
| `div.meta` | 难度徽章 + 预计时长 + 3~5 个关键词 |
| `div.nav` 的左右链接 | 上一节 / 下一节（第一节用 `<a class="disabled">`） |

**不要手写**：`id="bN"` 锚点、`<aside class="rtoc">` 本节目录、目录页、`toc.js`、`search-index.js`。

---

## 三、组件速查

### 3.1 正文与教学块

| 组件 | 写法 | 关键约束 |
|---|---|---|
| 新语法清单 | `<div class="box info"><div class="t">…</div><ul><li>…</li></ul></div>` | `.t` 会进右侧目录 |
| 例题卡 | `<div class="prob"><div class="ph">…</div><div class="st">…</div><div class="io">…</div></div>` | `.ph` 里放 `.pn` / `.oi` / `.badge.diff` / 外链 |
| 样例 | `<div class="io">输入：\n…\n输出：\n…</div>` | 直接换行，不要用 `<br>` |
| 新函数卡 | `<div class="fn"><div class="fh">新函数拆解 · 名字</div><div class="fb"><div class="sig">签名</div>…</div></div>` | `.fh` 会进右侧目录 |
| 逐项表 | `<table class="lines"><thead>…</thead><tbody>…</tbody></table>` | 第一列等宽字体 |
| 代码块小标题 | `<div class="cap">完整代码</div>` | 放在 `<pre>` 上一行 |
| 代码块 | `<pre><code>…</code></pre>` | **`<` 写 `&lt;`、`>` 写 `&gt;`、`&` 写 `&amp;`** |
| 代码高亮 | `<span class="k">` 关键字 / `.s` 字符串 / `.n` 数字 / `.c` 注释 / `.f` 函数名 | — |
| 思路块 | `<div class="step"><div class="sh">例题怎么想</div>…</div>` | 可嵌套一层做「逐行拆解」 |
| 提示 / 易错 / 通过 / 信息 | `.box.tip` / `.box.warn` / `.box.ok` / `.box.info` | 都用 `.t` 做标题 |
| 复现 | `<div class="reproduce"><div class="rt">自己动手复现</div>…</div>` | 给可执行的验证动作 |
| 数学补给 | `<div class="mathcard"><div class="mt">数学补给 · …</div>…</div>` | 讲数量级、位数、复杂度来源 |
| 一句话结论 | `<div class="quote">…</div>` | 绿色左边框 |

### 3.2 举一反三（折叠解析）

```html
<div class="think">
  <div class="tt">举一反三 · 想清楚这些再往下走</div>
  <div class="thint">先自己写出答案，再点开核对——方向对不对，比答案本身更重要</div>
  <ol>
    <li>
      <div class="tq">问题……</div>
      <details class="ta"><summary>想好了？点开核对思路与解析</summary>
        <div class="dc">结论 / 理由 / 常见错路 三段式回答。</div>
      </details>
    </li>
  </ol>
</div>
```

硬规则：`.tq` 的个数必须等于 `details.ta` 的个数（`check.py` 会计数），每题 ≥3 道。

### 3.3 挑战题与挑战 2

```html
<div class="challenge">
  <div class="ct">挑战题 · 题目名</div>
  <div class="ph" style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">
    <span class="oi">洛谷 P1046</span><span class="badge diff">入门</span>
    <a href="https://www.luogu.com.cn/problem/P1046" target="_blank" rel="noopener">去洛谷做这题 ↗</a>
  </div>
  <div class="st">题面（输入 / 输出格式）</div>
  <div class="cap">样例</div>
  <div class="io">输入：…</div>
  <div class="hintbox"><div class="ht">引导性提示（先只看这里）</div><p>…</p></div>
  <details><summary>想看思路了？点开完整思路</summary><div class="dc">…</div></details>
  <details><summary>还是不会？点开题解代码与拆解</summary><div class="dc">…</div></details>
</div>

<div class="challenge ch2">…</div>   <!-- 挑战 2：结构同上，难度更高、允许组合已学算法 -->
```

- 必有 `.ct`、`.hintbox`、≥1 个 `<details>`；提示不剧透做法。
- 挑战 2 只在 `id >= CH2_FROM` 的节出现，目录页与侧栏会自动多画一个 🌟 勾选框。

### 3.4 图解 `figure.dia`（纯 HTML，可编辑、可搜索）

**每节至少一张代码逻辑图**，写法有两种：`figure.dia` 的 HTML 图解（推荐），或 `figure.fig` 里的 SVG 流程图（`fnode` 系列）。HTML 图解的好处是文字可选中、可被检索、深色主题自动适配。

```html
<figure class="dia dia-flow">
  <figcaption>这张图解释哪段代码（哪一层循环 / 哪个分支）</figcaption>
  <div class="dflow">
    <div class="dn">读入 n 与数组 a</div>
    <div class="dar" aria-hidden="true"></div>
    <div class="dn dhas-code"><div class="dc"><code>for (i = 1; i &lt;= n; ++i)</code></div><div class="dt">外层：逐行推进</div></div>
    <div class="dar" aria-hidden="true"></div>
    <div class="dn dq"><span class="dq-m">?</span>a[i] &lt; 0 ？</div>
    <div class="darms">
      <span class="arm ok"><i>是</i>把这一项计入答案</span>
      <span class="arm no"><i>否</i>跳过</span>
    </div>
  </div>
</figure>
<div class="dnote">图下补充说明（可选）</div>
```

| 组件 | 类名 | 用途 |
|---|---|---|
| 竖排流程 | `.dflow` + `.dn`（`.dq` 判断、`.dhas-code` 带代码、`.dc` 代码格、`.dt` 说明）+ `.dar` 箭头 | 代码执行顺序 |
| 分支 | `.darms` + `.arm.ok` / `.arm.no`（`<i>是</i>` 标签） | 条件的两条路 |
| 横向阶段 | `.dsteps` + `.ds`（内含 `<b>` 序号）+ `.dsa` 箭杆 | 算法的几个阶段 |
| 数组快照 | `.darr` + `.dcell`（`<i>` 下标 / `<b>` 值 / `<u>` 标记，`.hl` 高亮） | 下标变化 |
| 二维表 | `.dmatrix`（`--cols` 变量）+ `.dmh` / `.dmh.dmhc` 表头 + `.dmc`（`.hl`、`.empty`） | DP 表、矩阵 |
| 树 | `.dtree` + `.dti` + `.dtn`（`.leaf` 叶子） | 递归树、字典树 |
| 左右对比 | `.dcmp-wrap` + `.dcmp.l` / `.dcmp.r`（`.dcmp-h` 标题 + `<ul>`） | 两种做法的对错 |
| 数学传送门 | `.portal`（`.pt`/`.pmark`/`.pintro`/`.plist`/`.pl`/`.pid`/`.ptitle`/`.pwhy`） | 指向配套数学课的相关节 |

图注写「这张图解释哪段代码、哪条边对应哪个分支」，不要写“如图所示”。

---

## 四、代码与高亮

| 类 | 用途 | 颜色 |
|---|---|---|
| `.k` | 关键字、`#include` | 蓝 |
| `.s` | 字符串、字符、头文件名 | 绿 |
| `.n` | 数字 | 橙 |
| `.c` | 注释 | 灰 |
| `.f` | 函数名 | 紫 |

三条硬规则：

1. `<` `>` `&` 必须转义，否则浏览器会把 `vector<int>` 当成标签吞掉。
2. 每个完整程序都要能编译：从 `#include` 到 `return 0;`，不要留 `…` 占位。
3. 循环里用 `"\n"` 而不是 `endl`；样例块里不要出现行末多余空格（严格比对会 WA）。

---

## 五、右侧「本节目录」怎么来的

`build.py` 扫描页面，按下面的规则收集条目，层级用 `lv1` / `lv2`：

| 元素 | 层级 | 出现在 |
|---|---|---|
| `<h2>` | 1 | 手工分节 |
| `.prob .pn` | 1 | 例题 |
| `.challenge .ct` | 1 | 挑战题 / 挑战 2 |
| `.mathcard .mt` | 1 | 数学补给 |
| `.think .tt` | 1 | 举一反三 |
| `.box .t` | 2 | 提示 / 易错 / 自测 / 延伸阅读的标题 |
| `.fn .fh` | 2 | 新函数拆解 |
| `.step .sh` | 2 | 思路与逐行拆解 |
| `.reproduce .rt` | 2 | 自己动手复现 |
| `<h3>` | 2 | 手工分小节 |

因此：**标题文字要短**（超过 20 字右侧栏会折成两行）；不要给普通段落加 `class="t"`，否则会多出一条目录。

---

## 六、锚点与全文检索

`build.py` 给下列块注入稳定锚点 `id="bN"`（已有 id 则沿用；新块从「已有最大编号 + 1」开始，重复构建不会撞车）：

`p` `li` `td` `th` `pre` `h2` `h3` `h4`，以及带这些 class 的元素：`t` `tt` `tq` `fh` `sh` `pn` `mt` `rt` `ct` `sig` `io` `cap` `dnote` `dc` `dt` `ds` `dn` `dmc`。

检索行为：

- 目录页输入关键词回车 → 标题（含 `tags`）命中排在前面，正文命中在后；
- 正文命中显示「节号 + 节标题 + 所属小节」与上下各一行，点击跳到 `NN.html?q=关键词#b12`；
- 命中会**自动展开**外层 `<details>`（题解默认折叠也能跳进去）；
- 跳转后的高亮在**下一次点击页面（或 Esc）**时清除。

正文块纯文本上限 600 字，超长段落会被截断；所以一段只讲一件事，检索结果才准。

---

## 七、目录页与进度

| 元素 | 来源 |
|---|---|
| 分组标题 | `GROUPS[i].name` |
| 每行 | `id` / `title` / `level` / `kind`（`review` → 「回顾」，`mock` → 「模拟赛」） |
| ⭐ 勾选框 | `data-role="learned"` |
| 🌟 勾选框 | `id >= CH2_FROM` 时出现，`data-role="ch2"` |
| 题解分区 | `EXTRA`（不占节号的页面，如比赛题解） |

进度存在 `localStorage`，键为 `MODULE.storePrefix + '.learned.' + 节号` / `'.ch2.' + 节号`。显式存 `'0'` 表示“手动取消”，取消后不会被默认值弹回。

**题解页**（`EXTRA`）：与普通节一样是完整页面，但 `body data-lesson` 不带数字，`h1` 写「某某赛 题解」；`build.py` 一样注入锚点与本节目录，并收进检索索引。

```python
EXTRA = [{"file": "sol-x.html", "title": "某某赛 题解", "note": "14 题里 13 题给出完整思路", "level": "入门 ~ 提高"}]
```

---

## 八、构建与验收

```powershell
python tools/build.py              # 注入锚点 + 重建本节目录 + 生成 index.html / toc.js / search-index.js
python tools/build.py --no-index   # 只回填各页与索引，不动目录页
python tools/check.py              # 全节自检
python tools/check.py 03.html      # 单节自检
```

`check.py` 检查项：

| 类别 | 具体 |
|---|---|
| 身份 | 文件名两位数字、`data-lesson`、`<title>` / `<h1>` 前缀三者一致 |
| 骨架 | charset / viewport / 样式表 / `.topbar` / `.wrap` / `.nav` / `<footer>` |
| 闭环 | `.prob`（`.pn` + `.st`）、`.fn`、`.step`、`.box.warn`、`.mathcard`、`.reproduce`、`.think`、`.challenge`（`.ct` + `.hintbox` + `<details>`）逐项检查 |
| 图解 | 必须有 `figure.dia`（含可识别主体）或 SVG 流程图 |
| 思考点 | `.tq` 数量必须等于 `details.ta` 数量，且 ≥3 |
| 代码 | 每个 `<pre>` 内不能有未转义的 `<` 与 `&` |
| 折叠 | 每个 `<details>` 必须有 `<summary>` |
| 本节目录 | 条目数 ≥3、`data-t` 指向的 id 必须真实存在、必须有一级条目 |
| 篇幅 | 正文汉字 <900 提醒；有占位内容直接报错 |

验收清单：

- [ ] `python tools/build.py` 无报错，打印的每页 `blocks` 数都在 60 以上
- [ ] `python tools/check.py` 全绿
- [ ] 目录页分组、难度徽章、勾选框数量正确（`id >= CH2_FROM` 的节才有 🌟）
- [ ] 任选一节：右侧本节目录条目与标题对得上，点击能定位、滚动能高亮
- [ ] 检索一个只在代码里出现的词（如 `sync_with_stdio`）也能命中
- [ ] 点正文命中 → 跳转、自动展开 `<details>`、关键字闪烁；再点一下页面高亮消失
- [ ] 宽屏（≥1180px）左侧栏常驻；窄屏为抽屉；右侧目录 ≥1440px 默认展开
- [ ] 勾选 ⭐ / 🌟 后刷新仍在，且目录页与侧栏数值同步

---

## 九、约定

1. **引擎不动**：`assets/style.css`、`assets/app.js` 由模板统一维护，本模板只在 `style.css` 末尾追加了两条通用规则（`.io` 可用于 `.prob` 之外、`.challenge.ch2 .oi` 配色），不影响原有任何样式。
2. **生成物不手改**：`index.html`、`assets/toc.js`、`assets/search-index.js`。
3. **一文件一节**：`NN.html` 平铺在根目录（翻页与检索路径都按它写死）。
4. **先构建再提交**：锚点与右侧目录都在构建期回填。
5. **存储键隔离**：每门课用自己的 `storePrefix` / `rtocKey`。

---

## 十、与其它模板的差异

| 项 | 学习模块标准模板 | 数学类模板 | 算法类模板 |
|---|---|---|---|
| 定位 | 任意学科的通用骨架 | 数学课件：先推导后定理 | 算法竞赛教程：一节一个算法闭环 |
| 目录模型 | Part → 章 → 节 | 同左 | 组 → 节（无章） |
| 侧栏 | 常驻左栏 + 右栏 | 同左 | 抽屉式章节栏 + 右侧本节目录 |
| 定理组件 | 通用盒 | **推导卡 → 定理 → 证明 → 落地卡** | 无（用例题与拆解代替） |
| 图 | `figure.plot` | `plot` + `figure.fig` | **`figure.dia` 纯 HTML 图解** + `plot` |
| 代码 | 可选 | 有算法价值的定理必须配 `.codebox` + `.walk` | 每节 2~5 段完整程序 + 逐行拆解 |
| 自检 | 通用结构 | 结构 + 数学陈述规范 | 教学闭环 + 代码逻辑图 + 目录锚点 |
| 范本 | `sections/1-1.html` | `sections/1-1.html` / `2-1.html` | `01.html` / `03.html`（挑战 2） |
