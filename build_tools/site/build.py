# -*- coding: utf-8 -*-
"""构建整站：渲染 60 节课 + 目录页 + 题解页 + 模拟赛。

用法：
    python build.py            # 构建全部
    python build.py --only 1 2 3
"""
import glob
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import curriculum
import render

OUT = os.path.normpath(os.path.join(HERE, "..", "..", "算竞教程"))


# ------------------------------------------------------------------ 载入内容
def load_lessons():
    data = {}
    for path in sorted(glob.glob(os.path.join(HERE, "lessons", "l*.py"))):
        modname = "lessons." + os.path.splitext(os.path.basename(path))[0]
        try:
            mod = importlib.import_module(modname)
        except Exception as e:                                  # noqa: BLE001
            print("  !! 载入失败 %s: %s" % (path, e))
            continue
        items = getattr(mod, "LESSONS", None)
        if items is None:
            items = []
            for k, v in vars(mod).items():
                if k.startswith("LESSON") and isinstance(v, dict):
                    items.append(v)
        for it in items:
            data[int(it["id"])] = it
    return data


def merge_meta(lesson, m):
    """课程总表提供标题/难度等元信息，内容文件可覆盖 summary 等。"""
    out = dict(m)
    out.update({k: v for k, v in lesson.items() if v not in (None, [], "")})
    out["id"] = m["id"]
    out["file"] = m["file"]
    out["group"] = m["group"]
    out["kind"] = m["kind"]
    out["star"] = bool(m.get("star"))      # ⭐ 由课程总表决定，内容文件不覆盖
    if not out.get("title"):
        out["title"] = m["title"]
    return out


# ------------------------------------------------------------------ 目录页
LEVEL_ORDER = ["入门", "入门+", "普及-", "普及/提高-", "普及+", "提高-/提高", "提高", "提高+", "省选"]


def render_index(all_lessons, done_ids, extra_pages):
    from render import esc, esc_attr
    body = []
    body.append("<h1>算竞教程 · 60 节重构版</h1>")
    body.append('<div class="sub">按难度重新编排的算法竞赛课程：每节一个完整算法应用，'
                '例题带完整代码拆解，节末一道挑战题；第 21 节起额外多一道<b>挑战 2</b>'
                '（跨算法、难度更高）；每 4~5 节插入一次回顾训练。</div>')

    body.append('<div class="progressbox"><b>我的进度</b>　<span id="idxProg">读表中…</span>'
                '<div class="bar"><i id="idxBar" style="width:0%"></i></div>'
                '<div style="font-size:13px;color:#5b6577;margin-top:6px">'
                '下面的列表可以自己勾：勾「已学」→ 该节打 ⭐；再勾「挑战2」→ ⭐ 变成 🌟。'
                '刷新、关掉浏览器都不会丢。</div></div>')

    body.append('<div class="legend">'
                '<b>图例</b>　⭐ 已学　·　🌟 已学且完成挑战 2　·　'
                '<span class="badge diff">难度</span> 参考洛谷难度标签　·　'
                '<b>回顾</b> 每 4~5 节一次的 5 题综合训练　·　<b>模拟赛</b> 限时整套题'
                '</div>')
    body.append('<form id="srForm" class="sr-bar" autocomplete="off">'
                '<input id="q" class="toc-search" type="search" '
                'placeholder="输入关键词后按回车检索，如：前缀和 / lower_bound / 并查集">'
                '<button type="submit" class="sr-go">检索</button>'
                '<button type="button" id="qClear" class="sr-clear" hidden title="退出检索">×</button>'
                '</form>')
    body.append('<div class="sr-tip">回车检索 · Esc 退出 · <b>标题命中排在前面</b>，'
                '正文命中会显示所在节与上下文，点击直接跳到关键字位置</div>')
    body.append('<div id="srWrap" class="sr-wrap" hidden></div>')
    body.append('<div id="tocWrap">')

    for a, b, gname in curriculum.GROUPS:
        items = [x for x in all_lessons if a <= x["id"] <= b]
        if not items:
            continue
        body.append('<div class="toc-group">%s</div>' % esc(gname))
        body.append('<div class="toc-list">')
        for it in items:
            star = '<span class="stars">⭐</span> ' if it.get("star") else '<span class="stars" style="display:none"></span> '
            kind_tag = ""
            if it.get("kind") == "review":
                kind_tag = ' <span class="badge">回顾</span>'
            elif it.get("kind") == "mock":
                kind_tag = ' <span class="badge">模拟赛</span>'
            kw = " ".join([it["title"]] + list(it.get("tags", []))).lower()
            ch2 = ('<label title="完成挑战2 后 ⭐ 变 🌟"><input type="checkbox" data-role="ch2" '
                   'data-id="%d">🌟</label>' % it["id"]) if it["id"] >= 21 else ""
            body.append('<div class="toc-item" data-id="%d" data-k="%s">'
                        '<a class="no" href="%s" style="min-width:34px">%02d</a>'
                        '<a class="nm" href="%s">%s%s%s</a>'
                        '<span class="badge diff">%s</span>'
                        '<span class="toc-ctl">'
                        '<label title="勾上表示已学（⭐）"><input type="checkbox" data-role="learned" '
                        'data-id="%d">⭐</label>%s</span></div>'
                        % (it["id"], esc_attr(kw), it["file"], it["id"], it["file"],
                           star, esc(it["title"]), kind_tag, esc(it.get("level", "")),
                           it["id"], ch2))
        body.append("</div>")

    if extra_pages:
        body.append('<div class="toc-group">题解</div>')
        body.append('<div class="toc-list">')
        for name, fname, desc, lvl in extra_pages:
            body.append('<div class="toc-item" style="cursor:default"><a class="no" href="%s" '
                        'style="min-width:34px">题解</a><a class="nm" href="%s">%s'
                        '<span style="color:#5b6577;font-size:13px">　%s</span></a>'
                        '<span class="badge diff">%s</span></div>'
                        % (fname, fname, esc(name), esc(desc), esc(lvl)))
        body.append("</div>")

    body.append('</div>')   # /tocWrap

    body.append('<div class="box tip" style="margin-top:18px"><div class="t">怎么打开 / 怎么用</div>'
                '<p>直接双击 <code>index.html</code> 用浏览器打开即可，全部是纯静态页面，不需要联网、不需要服务器。'
                '题目链接会跳到对应 OJ 的题面页（需联网）。</p>'
                '<p>顶部检索框支持全文搜索：输入关键词按回车，标题命中的节排在前面，正文命中会列出上下各一行，'
                '点击结果直接跳到该节并定位到关键字处（会自动展开折叠的题解）。</p>'
                '<p>左下角「☰ 章节」会拉出侧边栏：可以在任意一页直接跳到别的节，也能在侧边栏里'
                '勾选「已学 / 挑战2」，和这一页的勾选是同一份数据（存在浏览器 localStorage）。</p></div>')
    body.append('<div class="legend" style="margin-top:26px">'
                '<b>怎么用这套教程</b><br>'
                '① 每节先看「新函数拆解」，看懂每个参数是什么；'
                '② 跟着例题的思路读代码，读完后<strong>关掉页面自己敲一遍</strong>；'
                '③ 做节末挑战题，先只看提示，卡住 20 分钟再看思路；'
                '④ 第 21 节起的挑战 2 用来验证「真的会用」而不是「看懂了」；'
                '⑤ 做完回顾章再往下走，不要跳章。</div>')

    page = render.fmt_page(
        title="目录", site=render.SITE, desc=esc_attr("60 节算法竞赛教程目录"),
        root="", lid="index", crumb="全部 %d 节" % len(all_lessons), mark="",
        total=len(all_lessons), body="".join(body),
        nav='<a class="disabled">已经在这一页了</a>')
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)


def write_search_index(docs):
    """把全文索引写成 JS（含每块的锚点 id、纯文本、所在小标题）。"""
    import json
    compact = []
    for d in docs:
        heads, hidx, blocks = [], {}, []
        for e in d.get("b", []):
            h = e.get("h", "")
            if h not in hidx:
                hidx[h] = len(heads)
                heads.append(h)
            blocks.append([e["id"], hidx[h], e["t"]])
        compact.append({
            "f": d["file"], "n": d.get("n", 0), "t": d["t"], "lv": d.get("lv", ""),
            "g": d.get("g", ""), "tg": d.get("tags", []), "hs": heads, "b": blocks,
        })
    path = os.path.join(OUT, "assets", "search-index.js")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("/* 构建期生成，勿手改 */\nwindow.SEARCH_DOCS=")
        json.dump(compact, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    size = os.path.getsize(path) / 1024.0
    total = sum(len(d["b"]) for d in compact)
    print("  · 检索索引：%d 页 / %d 块 / %.0f KB" % (len(compact), total, size))


# ------------------------------------------------------------------ 主流程
def build_course_json(metas, extras=None):
    """生成侧边栏用的目录数据。"""
    groups = []
    for a, b, gname in curriculum.GROUPS:
        items = []
        for m in metas:
            if not (a <= m["id"] <= b):
                continue
            items.append({
                "id": m["id"], "title": m["title"], "file": m["file"],
                "level": m.get("level", ""), "kind": m.get("kind", "lesson"),
                "star": bool(m.get("star")),
            })
        if items:
            groups.append({"name": gname, "items": items})
    extra = []
    for name, fname, desc, lvl in (extras or []):
        extra.append({"title": name, "file": fname})
    return {"total": len(metas), "groups": groups, "extra": extra}


def main():
    only = None
    if "--only" in sys.argv:
        i = sys.argv.index("--only")
        only = set(int(x) for x in sys.argv[i + 1:])

    os.makedirs(OUT, exist_ok=True)
    metas = curriculum.all_lessons()
    render.write_assets(OUT, build_course_json(metas))

    contents = load_lessons()

    built = []
    search_docs = []
    for m in metas:
        lid = m["id"]
        if only and lid not in only:
            built.append(m)
            continue
        lesson = contents.get(lid)
        if lesson is None:
            built.append(m)
            continue
        merged = merge_meta(lesson, m)
        if merged.get("kind") == "review":
            doc = render.render_review(merged, metas, OUT)
        elif merged.get("kind") == "mock":
            doc = render.render_mock(merged, metas, OUT)
        else:
            doc = render.render_lesson(merged, metas, OUT)
        if doc:
            doc["n"] = lid
            search_docs.append(doc)
        built.append(merged)
        print("  ✓ %02d %s" % (lid, merged["title"]))

    # 题解页
    extras = []
    sol_dir = os.path.join(HERE, "solutions")
    if os.path.isdir(sol_dir):
        sys.path.insert(0, HERE)
        for path in sorted(glob.glob(os.path.join(sol_dir, "s_*.py"))):
            modname = "solutions." + os.path.splitext(os.path.basename(path))[0]
            try:
                mod = importlib.import_module(modname)
            except Exception as e:                              # noqa: BLE001
                print("  !! 题解载入失败 %s: %s" % (path, e))
                continue
            for doc in getattr(mod, "DOCS", []):
                sd = render.render_solution(doc, OUT)
                if sd:
                    sd["n"] = 0
                    search_docs.append(sd)
                extras.append((doc["title"], doc["file"], doc.get("desc", ""),
                               doc.get("level", "题解")))
                print("  ✓ 题解 %s" % doc["title"])

    write_search_index(search_docs)
    render_index(built, [m["id"] for m in built if m["id"] in contents], extras)
    # 题解页发现后再写一次 toc.js，让侧边栏也列出题解
    render.write_assets(OUT, build_course_json(metas, extras))
    print("站点输出：", OUT)


if __name__ == "__main__":
    main()
