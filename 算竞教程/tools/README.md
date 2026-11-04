# tools · 课程构建与自检

《算竞教程》的引擎与内容源码。**只改这里，页面由构建生成，不要手改 `../NN.html`。**

```
tools/
├─ curriculum.py      60 节总表：标题、难度、⭐ 默认值、标签、分组
├─ dsl.py             内容 DSL：P / C / EX / IDEA / EXPLAIN / FN / DIAG / CH / LESSON …
├─ diagrams.py        图解渲染：flow / steps / array / matrix / tree / compare
├─ render.py          HTML 渲染器：代码高亮、组件、右侧本节目录、页面模板
├─ searchindex.py     构建期索引：正文块锚点 id + 全文文本 + 本节目录条目
├─ build.py           构建入口 → 生成 ../index.html、../assets/{toc,search-index}.js
├─ assets_src/app.js  侧栏 / 勾选 / 检索 / 本节目录的前端逻辑（构建时写入 ../assets/app.js）
├─ lessons/l01.py…l60.py   每节内容
├─ solutions/         三份比赛题解
│
├─ check.py           ★ 自检总入口（等价于模板的 tools/check.py）
├─ audit.py           结构审计：每节是否缺例题/挑战题/数学补给
├─ check_std.py       按《算法类要求.md》的九段闭环验收
├─ check_diag.py      图解数量与类型（每节 ≥3 张、至少 1 张 flow、cap 齐全）
├─ check_think.py     思考点与解析是否一一对应
├─ check_one.py       单节：结构 + 是否用了已做过的题 + 编译该节全部完整程序
├─ compile_check.py   全量编译（较慢）
├─ compile_check_sol.py  题解代码编译
├─ done_check.py      已做过的 118 道题清单
└─ gap_report.py      按九段闭环盘点缺项
```

## 常用命令

在本目录（或课程根目录）执行：

```powershell
python tools/build.py                 # 重新生成全站
python tools/check.py                 # 快速自检（结构 + 标准 + 图解 + 思考点）
python tools/check.py --full          # 再加上全部 C++ 程序编译验证
```

单节调试：

```powershell
python tools/build.py --only 31 32    # 只重建某几节
python tools/check_one.py 31          # 单节结构 + 已做题 + 编译
python tools/check_diag.py 31 32      # 只看图解
python tools/gap_report.py 31 32      # 只看缺项
```

## 约定

- **生成物不手改**：`../index.html`、`../NN.html`、`../assets/*.js` 全部由 `build.py` 重建；
- **引擎与内容分离**：`render.py` / `diagrams.py` / `dsl.py` 是引擎，`lessons/` 是内容；
- **先构建再提交**：锚点、检索索引、右侧本节目录都在构建期回填，跳过构建会让检索和定位失效；
- `__pycache__/` 不入库。

## 与模板的关系

`模板/算法类模板` 的引擎取自本课程，参数化后单独维护。本目录比模板多的是内容 DSL
（模板用裸 HTML 写正文，这里用 Python 生成）与更细的验收脚本；两者的组件类名、
`figure.dia` 图解规范、九段闭环顺序一致。
