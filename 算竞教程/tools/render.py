# -*- coding: utf-8 -*-
"""算竞教程 · 站点渲染器

数据驱动：每节课是一份 dict（见 SCHEMA 注释），由 lessons_*.py 提供。
渲染成独立的 HTML 文件 + 目录页 + 资源（CSS/JS）。

课程数据字段
-----------
id            : int    课号（1..）
star          : bool   是否属于 30days 已学范围（目录标 ⭐）
title         : str    节标题，如 "数组与桶计数"
group         : str    所属分组名（用于目录分组）
level         : str    难度标签，如 "入门 / 普及-"
tags          : [str]  知识点标签
summary       : str    一句话导语
minutes       : int    预计学习时长（分钟）
uses          : [str]  本节出现的"新函数/新语法"名字（自动生成开头拆解清单）
sections      : [dict] 正文小节，见下
math          : dict    可选："数学补给" {title, body[blocks]}
think         : [str]  思考点（举一反三）
check         : [str]  自测清单（是否真的学会了）
challenge     : dict    节末挑战题
refs          : [str]  参考书目条目

sections 每节的 kind：
  intro      : {kind, text}                       —— 引入
  example    : {kind, problem:{name, oj, id, diff, link}, statement:[blocks]}
  idea       : {kind, title, blocks}              —— 思路拆解
  code       : {kind, caption, code, lines:[(行号区间说明, 文本)]}  —— 分块代码
  explain    : {kind, title, rows:[[行或片段, 说明]]}   —— 逐行表
  after      : {kind, title, blocks}              —— 讲解后的小结/坑
  func       : {kind, name, signature, proto:[[片段, 说明]], example, notes:[str]}  —— 新函数拆解
  reproduce  : {kind, text}                       —— 让学生自己复现
  table      : {kind, head:[], rows:[[..]], widths:[..]}
  note       : {kind, level: "tip|warn|ok|info", title, lines:[str]}
  list       : {kind, ordered:bool, items:[str]}
  quote      : {kind, text}                       —— 强调句

challenge：
  {name, oj, id, diff, link, statement:[blocks], hint:[str], idea:[str],
   code:str, explain:[[片段, 说明]], pitfalls:[str]}
"""
import html
import json
import os

import diagrams
import searchindex

SITE = "算竞教程"

CSS = r"""
:root{
  --bg:#fbfcfe; --fg:#1d2330; --muted:#5b6577; --line:#e3e8f0;
  --brand:#1f5fd0; --brand2:#0f9d76; --amber:#b26b00; --red:#c0392b;
  --code-bg:#0f172a; --code-fg:#e6edf7; --code-line:#7d8ba1;
  --inline-bg:#eef3fb; --card:#ffffff;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0; background:var(--bg); color:var(--fg);
  font-family:"Source Han Sans SC","Noto Sans SC","Microsoft YaHei",system-ui,-apple-system,sans-serif;
  font-size:16px; line-height:1.75; -webkit-font-smoothing:antialiased;
}
.wrap{max-width:900px;margin:0 auto;padding:0 22px 90px}
a{color:var(--brand);text-decoration:none}
a:hover{text-decoration:underline}

/* 顶部 */
.topbar{position:sticky;top:0;z-index:30;background:rgba(251,252,254,.92);
  backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.topbar .inner{max-width:900px;margin:0 auto;padding:10px 22px;display:flex;
  align-items:center;gap:14px;font-size:14px;color:var(--muted)}
.topbar a{color:var(--muted)}
.topbar .spacer{flex:1}
.badge{display:inline-block;padding:1px 8px;border-radius:999px;font-size:12px;
  background:var(--inline-bg);color:var(--brand);border:1px solid #d6e2f7}
.badge.star{background:#fff7e6;color:#a86a00;border-color:#f3d9a4}
.badge.diff{background:#eefaf4;color:#0b7f5f;border-color:#bfe8d9}

h1{font-size:30px;line-height:1.3;margin:30px 0 8px;letter-spacing:-.3px}
.sub{color:var(--muted);font-size:15px;margin-bottom:22px}
h2{font-size:22px;margin:38px 0 10px;padding-bottom:6px;border-bottom:2px solid var(--line)}
h3{font-size:17.5px;margin:24px 0 8px}
h4{font-size:15.5px;margin:18px 0 6px;color:var(--muted)}
p{margin:10px 0}

/* 元信息卡 */
.meta{display:flex;flex-wrap:wrap;gap:8px;margin:6px 0 18px}
.meta span{font-size:13px;color:var(--muted);background:#fff;border:1px solid var(--line);
  border-radius:8px;padding:3px 9px}

/* 代码 */
pre{background:var(--code-bg);color:var(--code-fg);border-radius:10px;padding:14px 16px;
  overflow-x:auto;font-size:13.5px;line-height:1.62;margin:12px 0;
  font-family:"JetBrains Mono",Consolas,"Cascadia Mono",Menlo,monospace;tab-size:4}
pre .c{color:#7f8fa6;font-style:normal}         /* 注释 */
pre .k{color:#7aa2f7}                            /* 关键字 */
pre .s{color:#9ece6a}                            /* 字符串/字符 */
pre .n{color:#ff9e64}                            /* 数字 */
pre .f{color:#bb9af7}                            /* 函数名 */
code{font-family:"JetBrains Mono",Consolas,Menlo,monospace;font-size:.92em;
  background:var(--inline-bg);border-radius:4px;padding:1px 5px;color:#1b3a6b}
pre code{background:none;padding:0;color:inherit;font-size:inherit}

/* 提示框 */
.box{border-radius:10px;padding:12px 16px;margin:14px 0;border:1px solid;background:#fff}
.box .t{font-weight:700;margin-bottom:4px;font-size:14.5px}
.box ul{margin:6px 0 0 18px}
.box p{margin:4px 0}
.box.tip{background:#eef6ff;border-color:#c9defb}
.box.tip .t{color:#1b5ab5}
.box.warn{background:#fff6ec;border-color:#f6d7ae}
.box.warn .t{color:#a76500}
.box.ok{background:#eefaf3;border-color:#c3e9d6}
.box.ok .t{color:#0b7f5f}
.box.info{background:#f5f6f9;border-color:#e0e4ec}
.box.info .t{color:#4a5568}

/* 例题卡 */
.prob{border:1px solid var(--line);border-left:4px solid var(--brand);border-radius:10px;
  background:#fff;padding:14px 18px;margin:16px 0}
.prob .ph{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin-bottom:8px}
.prob .pn{font-weight:700;font-size:16.5px}
.prob .oi{font-size:13px;color:var(--muted);background:var(--inline-bg);
  border-radius:6px;padding:2px 8px}
.prob .st{font-size:15px}
.prob .io{background:#f8fafc;border:1px dashed #d7dfeb;border-radius:8px;padding:8px 12px;
  margin:8px 0;font-family:"JetBrains Mono",Consolas,monospace;font-size:13px;white-space:pre-wrap}

/* 表格 */
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:14.5px}
th,td{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}
th{background:#f2f6fd;color:#274b8a;font-weight:700}
tbody tr:nth-child(even){background:#fafbfd}

/* 列表 */
ul,ol{margin:10px 0 10px 22px;padding:0}
li{margin:5px 0}

/* 分块代码标题 */
.cap{font-size:13.5px;color:var(--muted);margin:14px 0 -6px;font-weight:600}

/* 逐行说明表 */
.lines td:first-child{font-family:"JetBrains Mono",Consolas,monospace;white-space:pre-wrap;
  color:#1b3a6b;width:44%}

/* 教学区块 */
.step{border-left:3px solid #cfdcf5;margin:20px 0;padding:2px 0 2px 16px}
.step>.sh{font-size:15px;font-weight:700;color:#274b8a;margin-bottom:4px}
.quote{border-left:4px solid var(--brand2);background:#f2fcf8;padding:10px 16px;
  border-radius:0 8px 8px 0;margin:16px 0;color:#0d6b52;font-weight:600}
.reproduce{background:#fffdf5;border:1px dashed #e8d9a8;border-radius:10px;padding:12px 16px;
  margin:16px 0}
.reproduce .rt{font-weight:700;color:#8a6d00;margin-bottom:4px}

/* 新函数卡 */
.fn{border:1px solid #d9e2f2;border-radius:10px;background:#fff;margin:14px 0;overflow:hidden}
.fn .fh{background:#f2f6fd;padding:10px 16px;font-weight:700;color:#274b8a;font-size:15px}
.fn .fb{padding:10px 16px}
.fn .sig{font-family:"JetBrains Mono",Consolas,monospace;font-size:13.5px;background:#0f172a;
  color:#e6edf7;border-radius:8px;padding:10px 12px;margin:4px 0 10px;white-space:pre-wrap}

/* 挑战题 */
.challenge{border:2px solid #f0d9a8;border-radius:12px;background:#fffdf7;padding:4px 20px 16px;
  margin:26px 0}
.challenge>.ct{font-size:19px;font-weight:800;color:#8a5a00;margin:14px 0 4px}
.hintbox{background:#fff8e8;border:1px solid #f0dcb0;border-radius:8px;padding:10px 14px;margin:12px 0}
.hintbox .ht{font-weight:700;color:#8a5a00;font-size:14px;margin-bottom:3px}
details{border:1px solid var(--line);border-radius:8px;background:#fff;margin:10px 0;padding:0 14px}
details>summary{cursor:pointer;padding:10px 0;font-weight:700;color:#274b8a;list-style:none}
details>summary::-webkit-details-marker{display:none}
details>summary::before{content:"▸ ";color:var(--brand)}
details[open]>summary::before{content:"▾ "}
details .dc{padding:0 0 12px}

/* 数学补给 */
.mathcard{background:linear-gradient(180deg,#f7f9ff,#fff);border:1px solid #dce5f6;
  border-radius:12px;padding:4px 20px 16px;margin:24px 0}
.mathcard>.mt{font-size:17px;font-weight:800;color:#274b8a;margin:14px 0 2px}

/* 思考点 */
.think{background:#f6f4ff;border:1px solid #ddd4fb;border-radius:12px;padding:4px 20px 14px;margin:24px 0}
.think>.tt{font-size:17px;font-weight:800;color:#4b3a9e;margin:14px 0 2px}

/* 页脚导航 */
.nav{display:flex;justify-content:space-between;gap:12px;margin:44px 0 0;
  border-top:1px solid var(--line);padding-top:18px;font-size:14.5px}
.nav a{background:#fff;border:1px solid var(--line);border-radius:9px;padding:9px 14px;
  flex:1;text-align:center}
.nav a.disabled{opacity:.4;pointer-events:none}

/* 目录页 */
.toc-group{margin:26px 0 8px;font-size:18px;font-weight:800;color:#274b8a;
  border-left:5px solid var(--brand);padding-left:10px}
.toc-list{display:grid;grid-template-columns:1fr;gap:6px}
@media(min-width:720px){.toc-list{grid-template-columns:1fr 1fr}}
.toc-item{display:flex;gap:10px;align-items:baseline;background:#fff;border:1px solid var(--line);
  border-radius:9px;padding:9px 12px;font-size:14.5px}
.toc-item:hover{border-color:#b9cdf0;text-decoration:none}
.toc-item .no{color:var(--muted);font-size:12.5px;min-width:34px;font-weight:700}
.toc-item .nm{flex:1;color:var(--fg)}
.toc-item.done .nm{color:#334;}
.stars{color:#e0a300;font-size:12px}
.legend{font-size:13.5px;color:var(--muted);background:#fff;border:1px solid var(--line);
  border-radius:9px;padding:10px 14px;margin:14px 0}
.progressbox{background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px 16px;margin:16px 0}
.bar{height:9px;background:#e9eef7;border-radius:99px;overflow:hidden;margin-top:8px}
.bar>i{display:block;height:100%;background:linear-gradient(90deg,#1f5fd0,#0f9d76)}
.toc-search{width:100%;padding:10px 14px;border:1px solid var(--line);border-radius:10px;
  font-size:15px;margin:12px 0;background:#fff;color:var(--fg)}
.kbd{font-family:Consolas,monospace;background:#eef1f6;border:1px solid #dde3ec;
  border-bottom-width:2px;border-radius:5px;padding:0 5px;font-size:13px}
footer{margin-top:50px;color:var(--muted);font-size:13.5px;text-align:center}
@media print{.topbar,.nav{display:none}body{background:#fff}pre{background:#f6f8fa;color:#111}
  .box,.prob,.challenge{break-inside:avoid}}

/* ---------------- 侧边栏 ---------------- */
.sb-btn{position:fixed;left:18px;bottom:22px;z-index:60;display:flex;align-items:center;gap:6px;
  background:var(--brand);color:#fff;border:none;border-radius:999px;padding:11px 17px;
  font-size:14.5px;font-weight:600;cursor:pointer;box-shadow:0 6px 20px rgba(31,95,208,.35)}
.sb-btn:hover{background:#1a52b8}
.sb-ico{font-size:16px;line-height:1}
.sb-mask{position:fixed;inset:0;background:rgba(15,23,42,.38);opacity:0;pointer-events:none;
  transition:.2s;z-index:70}
.sb-mask.open{opacity:1;pointer-events:auto}
.sidebar{position:fixed;top:0;left:0;height:100vh;width:352px;max-width:88vw;background:#fff;
  border-right:1px solid var(--line);z-index:80;transform:translateX(-102%);
  transition:transform .22s ease;display:flex;flex-direction:column;
  box-shadow:6px 0 26px rgba(15,23,42,.10)}
.sidebar.open{transform:none}
.sb-head{padding:16px 18px 12px;border-bottom:1px solid var(--line);position:relative;flex:0 0 auto}
.sb-title{font-size:15.5px;font-weight:800;color:#274b8a}
.sb-prog{font-size:13px;color:var(--muted);margin-top:5px}
.sb-legend{font-size:12px;color:#8a94a6;margin-top:4px}
.sb-close{position:absolute;right:12px;top:12px;border:none;background:#f1f4f9;color:#5b6577;
  width:28px;height:28px;border-radius:50%;font-size:17px;line-height:1;cursor:pointer}
.sb-group{font-size:12.5px;font-weight:800;color:#274b8a;background:#f5f8fe;
  padding:7px 18px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin-top:2px}
.sb-item{display:flex;align-items:center;gap:6px;padding:7px 12px 7px 18px;font-size:13.5px;
  border-bottom:1px solid #f2f5fa}
.sb-item:hover{background:#fafcff}
.sb-item.cur{background:#eef6ff;box-shadow:inset 3px 0 0 var(--brand)}
.sb-link{flex:1;display:flex;gap:8px;align-items:baseline;color:var(--fg);min-width:0}
.sb-link:hover{text-decoration:none;color:var(--brand)}
.sb-no{color:#9aa5b5;font-size:12px;font-weight:700;flex:0 0 auto}
.sb-nm{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sb-nm em{font-style:normal;color:#b26b00;font-size:11px;background:#fff6e5;
  border-radius:4px;padding:0 4px;margin-left:3px}
.sb-marks{display:flex;gap:2px;flex:0 0 auto}
.sb-marks label{display:flex;align-items:center;cursor:pointer;padding:2px}
.sb-marks b{font-weight:400;font-size:13px;opacity:.3;transition:.15s}
.sb-marks input{display:inline-block;width:15px;height:15px;margin:0;cursor:pointer;accent-color:#e0a300}
.sb-marks input:checked+b{opacity:1;transform:scale(1.15)}
.sb-marks label:hover b{opacity:.75}
.sb-extra{font-size:13.5px}
.sb-extra a{color:var(--brand)}
body.sb-lock{overflow:hidden}
@media(min-width:1180px){
  .sidebar{transform:none;box-shadow:none;width:332px}
  .sb-mask{display:none}
  .sb-btn{display:none}
  body.sb-lock{overflow:auto}
  .wrap{margin-left:362px}
  .topbar .inner{margin-left:362px;max-width:none}
  .sb-close{display:none}
}
@media print{.sidebar,.sb-btn,.sb-mask{display:none}}

/* ---------------- 目录勾选 ---------------- */
.toc-ctl{display:flex;gap:10px;flex:0 0 auto;align-items:center;margin-left:auto}
.toc-ctl label{display:flex;align-items:center;gap:3px;font-size:11.5px;color:#7a8598;
  cursor:pointer;user-select:none}
.toc-ctl input{cursor:pointer;width:14px;height:14px;accent-color:var(--brand)}
.toc-item{flex-wrap:wrap}
.toc-item .stars{font-size:15px;line-height:1}
.progressbox .bar>i{transition:width .25s}
.sb-nm{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

/* ---------------- 挑战2 / 页眉星标 ---------------- */
.page-mark{font-size:17px;line-height:1;margin-right:2px}
.challenge.ch2{border-color:#9ec9f5;background:#f7fbff}
.challenge.ch2>.ct{color:#134a8e}
.challenge.ch2 .hintbox{background:#eef6ff;border-color:#c9defb}
.challenge.ch2 .hintbox .ht{color:#134a8e}

/* ---------------- 侧边栏：滚动与勾选（修正版） ---------------- */
.sidebar{height:100vh;height:100dvh;display:flex;flex-direction:column;overflow:hidden}
.sb-body{flex:1 1 auto;min-height:0;overflow-y:auto;overflow-x:hidden;
  overscroll-behavior:contain;-webkit-overflow-scrolling:touch;padding-bottom:28px}
.sb-body::-webkit-scrollbar{width:9px}
.sb-body::-webkit-scrollbar-thumb{background:#c8d2e0;border-radius:5px}
.sb-body::-webkit-scrollbar-thumb:hover{background:#a9b6c9}
.sb-body::-webkit-scrollbar-track{background:#f4f7fb}
.sb-item{flex:0 0 auto}
.sb-group{position:sticky;top:0;z-index:2}
.sb-marks{display:flex;gap:1px;flex:0 0 auto;align-items:center}
.sb-marks .mk{display:inline-flex;align-items:center;gap:1px;padding:2px 3px;border-radius:6px;
  cursor:pointer;user-select:none;transition:background .15s}
.sb-marks .mk:hover{background:#eaf1fd}
.sb-marks .mk input{display:inline-block;width:14px;height:14px;margin:0;cursor:pointer;
  accent-color:#e0a300;flex:0 0 auto}
.sb-marks .mk-t{font-size:12px;line-height:1;opacity:.35;transition:.15s}
.sb-marks .mk input:checked+.mk-t{opacity:1}
.sb-marks .mk:hover .mk-t{opacity:.8}

/* ---------------- 目录页检索 ---------------- */
.sr-bar{display:flex;gap:8px;margin:14px 0 6px}
.sr-bar .toc-search{margin:0;flex:1}
.sr-go{flex:0 0 auto;border:1px solid var(--brand);background:var(--brand);color:#fff;
  border-radius:10px;padding:0 20px;font-size:15px;cursor:pointer;font-weight:600}
.sr-go:hover{background:#1a52b8}
.sr-clear{flex:0 0 auto;border:1px solid var(--line);background:#fff;color:#5b6577;
  border-radius:10px;width:40px;font-size:19px;line-height:1;cursor:pointer}
.sr-clear:hover{background:#f4f7fc;color:#c0392b}
.sr-tip{font-size:12.8px;color:#7a8598;margin:0 0 16px 2px}
.sr-wrap{margin:4px 0 24px}
.sr-sum{font-size:14px;color:#3c4757;background:#f5f8fe;border:1px solid #dbe5f6;
  border-radius:10px;padding:9px 14px;margin-bottom:14px}
.sr-sec{font-size:14.5px;font-weight:800;color:#274b8a;margin:18px 0 8px;
  border-left:4px solid var(--brand);padding-left:9px}
.sr-list{display:flex;flex-direction:column;gap:8px}
.sr-title{display:flex;align-items:center;gap:10px;background:#fff;border:1px solid var(--line);
  border-radius:9px;padding:9px 13px;font-size:15px}
.sr-title:hover{border-color:#b9cdf0;text-decoration:none;background:#fafcff}
.sr-title .sr-no{color:#9aa5b5;font-size:12.5px;font-weight:700;min-width:34px}
.sr-title .sr-tn{flex:1;color:var(--fg);font-weight:600}
.sr-hit{display:block;background:#fff;border:1px solid var(--line);border-left:3px solid #cfdcf5;
  border-radius:9px;padding:9px 13px;color:var(--fg)}
.sr-hit:hover{text-decoration:none;border-left-color:var(--brand);background:#fbfdff;
  box-shadow:0 2px 10px rgba(31,95,208,.07)}
.sr-hit .sr-head{display:flex;align-items:baseline;gap:7px;flex-wrap:wrap;font-size:12.8px;
  color:#7a8598;margin-bottom:3px}
.sr-hit .sr-no{font-weight:700;color:#9aa5b5}
.sr-hit .sr-tt{color:#274b8a;font-weight:700}
.sr-hit .sr-sub{color:#8a94a6}
.sr-line{font-size:13.6px;line-height:1.55;white-space:nowrap;overflow:hidden;
  text-overflow:ellipsis}
.sr-dim{color:#a3adbb;font-size:12.8px}
.sr-main{color:#2a3340}
.sr-tag{font-size:12px;color:#8a6d00;background:#fff7e0;border:1px solid #f0dfae;
  border-radius:6px;padding:1px 7px}
mark.sr-mk{background:#ffe28a;color:#5a3d00;border-radius:3px;padding:0 2px;font-weight:700}
mark.sr-mk.hit{background:#ffd54a;box-shadow:0 0 0 2px rgba(255,213,74,.45)}
.sr-empty{background:#fff;border:1px dashed #d7dfeb;border-radius:10px;padding:22px;
  text-align:center;color:#7a8598;font-size:14.5px;line-height:1.9}
/* 目标块闪烁提示 */
.sr-flash{animation:srflash 2.4s ease-out 1;border-radius:8px}
@keyframes srflash{
  0%{background:#fff3c4;box-shadow:0 0 0 6px rgba(255,226,138,.75)}
  40%{background:#fff9e0;box-shadow:0 0 0 3px rgba(255,226,138,.4)}
  100%{background:transparent;box-shadow:none}
}

.think .thint{display:block;font-size:12.6px;color:#8a86a8;font-weight:500;margin-top:5px}
.think ol>li{margin:10px 0;line-height:1.8}
.think .tq{line-height:1.78}
.think details.ta{border:0;background:transparent;margin:7px 0 0;padding:0 0 0 11px;
  border-left:3px solid #d9cdf9}
.think details.ta>summary{padding:2px 0;font-size:13px;font-weight:600;color:#6a5aa8}
.think details.ta>summary::before{content:"\25B8  ";color:#8b7bd0}
.think details.ta[open]>summary::before{content:"\25BE  "}
.think details.ta .dc{padding:3px 0 5px;font-size:14.2px;line-height:1.9;color:#3c4757}

/* ---------------- 右侧「本节目录」 ---------------- */
.rtoc{position:fixed;top:0;right:0;width:278px;height:100vh;height:100dvh;background:#fff;
  border-left:1px solid var(--line);display:flex;flex-direction:column;z-index:75;
  transform:translateX(101%);transition:transform .22s ease;
  box-shadow:-8px 0 26px rgba(16,32,64,.07)}
.rtoc.open{transform:none}
.rt-head{display:flex;align-items:center;justify-content:space-between;padding:14px 14px 10px;
  border-bottom:1px solid var(--line);flex:0 0 auto}
.rt-title{font-weight:800;font-size:15px;color:#274b8a}
.rt-close{border:1px solid var(--line);background:#fff;border-radius:8px;width:28px;height:28px;
  cursor:pointer;color:#5b6577;font-size:15px;line-height:1;flex:0 0 auto}
.rt-close:hover{background:#f1f5fc;color:var(--brand)}
.rt-sum{padding:10px 14px;font-size:12.8px;line-height:1.8;color:#5b6577;
  border-bottom:1px dashed var(--line);max-height:32vh;overflow-y:auto;flex:0 0 auto}
.rt-body{flex:1 1 auto;min-height:0;overflow-y:auto;padding:8px 0 70px;overscroll-behavior:contain}
.rt-body::-webkit-scrollbar{width:8px}
.rt-body::-webkit-scrollbar-thumb{background:#c8d2e0;border-radius:4px}
.rt-i{display:block;padding:5px 14px;font-size:13.4px;color:#3c4757;
  border-left:3px solid transparent;line-height:1.55}
.rt-i.lv1{font-weight:700;color:#274b8a;margin-top:7px}
.rt-i.lv2{padding-left:27px;font-size:13px;color:#5b6577}
.rt-i.lv3{padding-left:42px;font-size:12.8px;color:#7a8598}
.rt-i:hover{background:#f4f8ff;text-decoration:none;color:var(--brand)}
.rt-i.cur{background:#eef4ff;border-left-color:var(--brand);color:#1b3f7a}
.rt-tab{position:fixed;right:22px;bottom:26px;z-index:76;
  border:1px solid var(--line);border-radius:24px;background:#fff;
  padding:10px 18px;font-size:13.5px;color:#3c4757;cursor:pointer;
  box-shadow:0 6px 20px rgba(16,32,64,.14)}
.rt-tab:hover{color:var(--brand);background:#f7faff;border-color:#b9cdf0}
body.rtoc-open .rt-tab{display:none}
@media(min-width:1440px){
  body.rtoc-open .wrap{margin-right:300px}
  body.rtoc-open .topbar .inner{margin-right:300px;max-width:none}
}
@media print{.rtoc,.rt-tab{display:none}}

/* ---------------- 数学传送门 ---------------- */
.portal{background:linear-gradient(180deg,#f1f7ff 0%,#fbfdff 62%);border:1px solid #cfdcf5;
  border-left:4px solid var(--brand);border-radius:12px;padding:14px 18px 14px;margin:26px 0}
.portal .pt{display:flex;align-items:center;gap:9px;font-size:16.5px;font-weight:800;color:#1d3f7a}
.portal .ptt{font-size:16.5px;font-weight:800;color:#1d3f7a}
.portal .pmark{display:inline-flex;align-items:center;justify-content:center;width:27px;height:27px;
  border-radius:8px;background:#e1edff;color:#2d5fb8;font-size:14px;flex:0 0 auto}
.portal .phome{margin-left:auto;font-size:13px;font-weight:600;color:var(--brand)}
.portal .pintro{font-size:13.6px;color:#4a5a72;line-height:1.85;margin:9px 0 11px}
.portal .plist{display:flex;flex-direction:column;gap:8px}
.portal .pl{display:flex;align-items:flex-start;gap:10px;background:#fff;border:1px solid #dbe5f6;
  border-radius:9px;padding:9px 12px;color:var(--fg)}
.portal .pl:hover{text-decoration:none;border-color:#9dbcec;background:#fbfdff;
  box-shadow:0 2px 10px rgba(31,95,208,.09)}
.portal .pid{font-size:12.5px;font-weight:800;color:#2d5fb8;background:#edf3ff;border-radius:6px;
  padding:2px 7px;flex:0 0 auto;margin-top:1px}
.portal .pbody{display:flex;flex-direction:column;gap:2px;flex:1;min-width:0}
.portal .ptitle{font-size:14.5px;font-weight:700;color:#1d3f7a}
.portal .pwhy{font-size:12.8px;color:#6a7890;line-height:1.6}
.portal .parrow{color:#9db4d8;font-size:15px;flex:0 0 auto}

/* ---------------- 图解：代码逻辑图 / 概念图 ---------------- */
.dia{margin:22px 0;padding:14px 16px 16px;background:#f7faff;border:1px solid #d9e5f6;
  border-radius:12px}
.dia>figcaption{font-size:12.8px;font-weight:700;color:#3b6ba5;margin:0 0 12px;
  letter-spacing:.3px;display:flex;align-items:center;gap:6px}
.dia>figcaption::before{content:"";width:4px;height:13px;background:var(--brand);
  border-radius:2px;display:inline-block}
.dnote{font-size:12.4px;color:#7d8ba3;margin-top:9px;text-align:center}

/* 竖向流程 */
.dflow{display:flex;flex-direction:column;align-items:center}
.dn{width:100%;max-width:600px;background:#fff;border:1px solid #cfdcf0;border-radius:9px;
  padding:9px 13px;font-size:13.8px;color:#22303f;line-height:1.65;box-sizing:border-box}
.dn.dhas-code{border-left:3px solid var(--brand);background:#fff}
.dc{font-family:Consolas,"Cascadia Mono",monospace;font-size:12.6px;color:#0b4f9c;
  background:#eaf2ff;border-radius:6px;padding:3px 8px;display:inline-block;margin-bottom:5px;
  word-break:break-all}
.dt{color:#3c4757}
.dq{border-color:#e0c98c;background:#fffdf4;font-weight:700}
.dq-m{display:inline-flex;align-items:center;justify-content:center;width:17px;height:17px;
  border-radius:50%;background:#e8a93b;color:#fff;font-size:11px;font-weight:800;
  margin-right:7px;vertical-align:1px}
.darms{display:flex;gap:10px;width:100%;max-width:600px;margin-top:8px;flex-wrap:wrap}
.arm{flex:1 1 200px;background:#fff;border:1px dashed #cfdcf0;border-radius:8px;
  padding:7px 11px;font-size:12.9px;color:#4a5a72;line-height:1.6}
.arm i{font-style:normal;font-weight:800;color:#fff;border-radius:5px;padding:1px 6px;
  margin-right:7px;font-size:11.5px;background:#7ba7e0}
.arm.ok i{background:#3f9a63}
.arm.no i{background:#c2694f}
.dar{width:2px;height:16px;background:#b9cbe6;position:relative;flex:0 0 auto}
.dar::after{content:"";position:absolute;left:50%;bottom:-2px;transform:translateX(-50%);
  border:5px solid transparent;border-top:6px solid #b9cbe6;border-bottom:0}

/* 横向阶段 */
.dsteps{display:flex;align-items:center;gap:0;flex-wrap:wrap;justify-content:center}
.ds{flex:1 1 150px;min-width:130px;max-width:230px;background:#fff;border:1px solid #cfdcf0;
  border-radius:9px;padding:10px 12px;font-size:13.2px;display:flex;gap:8px;
  align-items:flex-start;line-height:1.55;color:#2a3644}
.ds b{flex:0 0 auto;width:20px;height:20px;border-radius:50%;background:var(--brand);
  color:#fff;font-size:11.5px;display:flex;align-items:center;justify-content:center;
  margin-top:1px}
.dsa{flex:0 0 auto;width:20px;height:2px;background:#b9cbe6;position:relative}
.dsa::after{content:"";position:absolute;right:-1px;top:-3px;border:5px solid transparent;
  border-left:7px solid #b9cbe6;border-right:0}

/* 数组快照 */
.darr{display:flex;gap:6px;justify-content:center;flex-wrap:wrap;padding:2px 0}
.dcell{min-width:46px;background:#fff;border:1px solid #cfdcf0;border-radius:8px;
  padding:4px 5px 3px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dcell i{font-style:normal;font-size:10.5px;color:#9aa8bd;line-height:1.2}
.dcell b{font-size:14.5px;color:#22303f;font-weight:700;line-height:1.3}
.dcell u{text-decoration:none;font-size:10.5px;color:#c2694f;font-weight:800;line-height:1.2}
.dcell.hl{border-color:var(--brand);background:#edf4ff;box-shadow:0 0 0 2px rgba(31,95,208,.12)}

/* 二维表 */
.dmatrix{display:grid;grid-template-columns:repeat(var(--cols),minmax(40px,auto));
  gap:4px;justify-content:center}
.dmh{font-size:11px;color:#8291a8;text-align:center;padding:2px 3px;line-height:1.3}
.dmh.dmhc{text-align:right;padding-right:6px}
.dmc{background:#fff;border:1px solid #cfdcf0;border-radius:6px;padding:6px 4px;
  text-align:center;font-size:13.2px;min-width:40px;color:#22303f}
.dmc.hl{border-color:var(--brand);background:#edf4ff;font-weight:700}
.dmc.empty{background:transparent;border-color:transparent}

/* 树 */
.dtree{display:flex;flex-direction:column;gap:5px;align-items:flex-start}
.dti{width:100%}
.dtn{display:inline-block;background:#fff;border:1px solid #cfdcf0;border-radius:7px;
  padding:4px 10px;font-size:13px;color:#2a3644}
.dtn.leaf{background:#f1f6ff;border-style:dashed}

/* 左右对比 */
.dcmp-wrap{display:flex;gap:12px;flex-wrap:wrap}
.dcmp{flex:1 1 240px;border-radius:9px;padding:10px 14px;border:1px solid}
.dcmp.l{background:#fdf6f4;border-color:#eed6cc}
.dcmp.r{background:#f3faf6;border-color:#cfe7d9}
.dcmp-h{font-weight:800;font-size:13.4px;margin-bottom:6px}
.dcmp.l .dcmp-h{color:#a4543a}
.dcmp.r .dcmp-h{color:#2f7a52}
.dcmp ul{margin:0;padding-left:17px}
.dcmp li{font-size:12.9px;line-height:1.75;color:#4a5a72}
@media print{.dia{break-inside:avoid}}

/* ---------------- 推导卡 / 算法落地卡 ---------------- */
:root{
  --paper:#fff; --ink:#1d2330; --ink-2:#3c4757; --ink-3:#7a8598;
  --line-2:#eef2f8;
  --purple:#6b4fbb; --purple-bg:#f4f1fd;
  --blue:#2f6fd0;   --blue-bg:#eef4ff;
  --green:#2f7a52;  --green-bg:#eef8f2;
  --amber-bg:#fff8e8;
  --mono:Consolas,"Cascadia Mono",monospace;
  --shadow:0 2px 10px rgba(16,32,64,.06);
}
.derive{margin:26px 0;border:1px dashed #c9bcec;border-radius:12px;background:var(--paper);
  overflow:hidden}
.derive-h{display:flex;align-items:center;gap:9px;flex-wrap:wrap;padding:12px 16px;
  background:var(--purple-bg);border-bottom:1px dashed var(--line)}
.derive-h .dk{font-size:10px;letter-spacing:.12em;font-weight:700;color:#fff;
  background:var(--purple);border-radius:4px;padding:2px 7px;white-space:nowrap}
.derive-h b{font-size:14.5px;color:var(--ink);font-weight:650}
.derive-h .dcover{font-size:11.5px;color:var(--purple);background:#fff;
  border:1px solid #d9cdf5;border-radius:6px;padding:1px 8px}
.derive-h .dsub{margin-left:auto;font-size:11px;color:var(--ink-3);
  border:1px solid var(--line);background:var(--paper);border-radius:99px;padding:1px 9px}
.derive-q{padding:11px 16px;background:var(--amber-bg);border-bottom:1px solid var(--line-2);
  font-size:14.5px;color:var(--ink-2)}
.derive-q>b{color:var(--amber);margin-right:8px}
.derive-q p{margin:0}
.dstep{padding:13px 17px;border-bottom:1px dashed var(--line-2)}
.dstep:last-of-type{border-bottom:0}
.dstep .dh{display:flex;align-items:flex-start;gap:9px;font-weight:650;color:var(--ink);
  font-size:14.5px;line-height:1.55}
.dstep .dnum{flex:0 0 auto;width:22px;height:22px;padding:0;border:0;max-width:none;
  border-radius:6px;background:var(--purple);color:#fff;font-size:12px;line-height:22px;
  text-align:center;font-family:var(--mono);font-weight:650;margin-top:1px}
.dstep p{margin:7px 0 0}
.dcheck{margin:8px 0 0;padding:7px 10px;border-left:2px solid var(--green);
  background:var(--green-bg);border-radius:0 6px 6px 0;font-size:13.5px;color:var(--ink-2);
  line-height:1.7}
.dcheck>b{color:var(--green);margin-right:8px}
.derive-end{padding:11px 16px;background:var(--purple-bg);border-top:1px dashed var(--line);
  font-size:13.8px;color:var(--ink-2);line-height:1.75}
.derive-end>b{color:var(--purple);margin-right:8px}
.walk{margin:26px 0;border:1px solid var(--line);border-radius:12px;background:var(--paper);
  box-shadow:var(--shadow);overflow:hidden}
.walk-h{display:flex;align-items:center;gap:9px;flex-wrap:wrap;padding:12px 16px;
  background:var(--blue-bg);border-bottom:1px solid var(--line)}
.walk-h .wk{font-size:10px;letter-spacing:.12em;font-weight:700;color:#fff;
  background:var(--blue);border-radius:4px;padding:2px 7px;white-space:nowrap}
.walk-h b{font-size:14.5px;color:var(--ink);font-weight:650}
.walk-h .cover{margin-left:auto;font-size:11px;color:var(--ink-3);border:1px solid var(--line);
  background:var(--paper);border-radius:99px;padding:1px 9px}
.walk-req{padding:11px 16px;background:var(--amber-bg);border-bottom:1px dashed var(--line);
  font-size:14.5px;color:var(--ink-2)}
.walk-req>b{color:var(--amber);margin-right:8px}
.walk-req p{margin:6px 0 0}
.walk-step{padding:14px 17px;border-bottom:1px solid var(--line-2)}
.walk-step:last-of-type{border-bottom:0}
.ws-h{display:flex;align-items:flex-start;gap:9px;font-weight:650;color:var(--ink);
  font-size:14.5px;line-height:1.55}
.ws-n{flex:0 0 auto;width:22px;height:22px;border-radius:6px;background:var(--blue);color:#fff;
  font-size:12px;line-height:22px;text-align:center;font-family:var(--mono);margin-top:1px}
.ws-why{margin:9px 0 0;padding:8px 11px;border-left:2px solid var(--purple);
  background:var(--purple-bg);border-radius:0 6px 6px 0;font-size:13.5px;color:var(--ink-2);
  line-height:1.75}
.ws-why>b{color:var(--purple);margin-right:8px}
.walk-oi{padding:12px 17px;background:#f7faf8;border-top:1px solid var(--line);
  font-size:13.5px;color:var(--ink-2);line-height:1.75}
.walk-oi>b{color:var(--green);margin-right:8px}
.walk-oi .tags{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
.walk-oi .tags span{font-size:11.5px;color:var(--ink-3);background:var(--paper);
  border:1px solid var(--line);border-radius:99px;padding:1px 9px}
.walk-step pre,.derive pre{margin:9px 0 0}
@media(max-width:760px){
  .derive-h .dsub{margin-left:0}
  .dstep{padding:12px 13px}
  .derive-q,.derive-end{padding-left:13px;padding-right:13px}
}

/* ---------------- 深色模式 ---------------- */
.theme-btn{margin-left:10px;border:1px solid var(--line);background:var(--card);color:var(--muted);
  border-radius:8px;width:28px;height:28px;font-size:14px;line-height:1;cursor:pointer;
  flex:0 0 auto}
.theme-btn:hover{color:var(--brand);border-color:#b9cdf0}
[data-theme="dark"]{
  color-scheme:dark;
  --bg:#14171c; --fg:#e6ebf2; --muted:#9aa6b8; --line:#2b323b;
  --brand:#6aa4f5; --brand2:#46c99b; --amber:#e0b060; --red:#f08a7a;
  --card:#1b2027; --inline-bg:#232b35;
  --code-bg:#0d1117; --code-fg:#e6edf7; --code-line:#8b98a8;
  --paper:#1b2027; --ink:#e6ebf2; --ink-2:#c2cbd8; --ink-3:#8f9bab;
  --line-2:#252c35;
  --purple:#b3a6dd; --purple-bg:#241f33;
  --blue:#7fb2e8;   --blue-bg:#182431;
  --green:#8fceac;  --green-bg:#16241d;
  --amber-bg:#2a2419;
  --shadow:0 2px 10px rgba(0,0,0,.5);
}
[data-theme="dark"] body{background:var(--bg);color:var(--fg)}
[data-theme="dark"] .topbar{background:rgba(20,23,28,.92)}
[data-theme="dark"] .sidebar,[data-theme="dark"] .rtoc{background:var(--card);border-color:var(--line)}
[data-theme="dark"] .sb-head,[data-theme="dark"] .rt-head{border-color:var(--line)}
[data-theme="dark"] .sb-body::-webkit-scrollbar-track,[data-theme="dark"] .rt-body::-webkit-scrollbar-track{background:#1a1f26}
[data-theme="dark"] .sb-body::-webkit-scrollbar-thumb,[data-theme="dark"] .rt-body::-webkit-scrollbar-thumb{background:#39424e}
/* 卡片与容器统一换底 */
[data-theme="dark"] .box,[data-theme="dark"] .toc-item,[data-theme="dark"] .dia,
[data-theme="dark"] .prob,[data-theme="dark"] .fn,[data-theme="dark"] .step,
[data-theme="dark"] .mathcard,[data-theme="dark"] .think,[data-theme="dark"] .challenge,
[data-theme="dark"] .reproduce,[data-theme="dark"] .portal,[data-theme="dark"] .walk,
[data-theme="dark"] .derive,[data-theme="dark"] .rt-i.cur,[data-theme="dark"] .sr-title,
[data-theme="dark"] .sr-hit,[data-theme="dark"] .sr-empty,[data-theme="dark"] .sr-sum,
[data-theme="dark"] .progressbox,[data-theme="dark"] table,[data-theme="dark"] details,
[data-theme="dark"] .dcell,[data-theme="dark"] .dmc,[data-theme="dark"] .dtn,
[data-theme="dark"] .dn,[data-theme="dark"] .ds,[data-theme="dark"] .arm,
[data-theme="dark"] .dcheck{background:var(--card);border-color:var(--line)}
[data-theme="dark"] .toc-search,[data-theme="dark"] .sr-bar input{background:#151a20;
  border-color:var(--line);color:var(--fg)}
/* 文字 */
[data-theme="dark"] h1,[data-theme="dark"] h2,[data-theme="dark"] h3,
[data-theme="dark"] .sh,[data-theme="dark"] .fh,[data-theme="dark"] .ct,
[data-theme="dark"] .mt,[data-theme="dark"] .tt,[data-theme="dark"] .sb-title,
[data-theme="dark"] .rt-title,[data-theme="dark"] .toc-group,[data-theme="dark"] .sr-sec,
[data-theme="dark"] .derive-h b,[data-theme="dark"] .walk-h b,[data-theme="dark"] .dh,
[data-theme="dark"] .ws-h,[data-theme="dark"] .ptitle,[data-theme="dark"] .sr-tt{color:#9dc0f5}
[data-theme="dark"] .sub,[data-theme="dark"] .meta,[data-theme="dark"] p,
[data-theme="dark"] li,[data-theme="dark"] .st,[data-theme="dark"] .dt,
[data-theme="dark"] .dstep p,[data-theme="dark"] .walk-step p{color:var(--fg)}
[data-theme="dark"] .quote{background:#1d2530;border-color:var(--brand);color:var(--fg)}
/* 表格 */
[data-theme="dark"] th{background:#222a34;color:#a9bad0;border-color:var(--line)}
[data-theme="dark"] td{border-color:var(--line)}
[data-theme="dark"] tr:nth-child(even) td{background:#181e25}
/* 代码 */
[data-theme="dark"] code{background:#232b35;color:#8fd0ff}
[data-theme="dark"] pre{background:var(--code-bg);color:var(--code-fg)}
/* 专项配色 */
[data-theme="dark"] .box.tip{background:#1a2632;border-color:#2c4257}
[data-theme="dark"] .box.warn{background:#2a201a;border-color:#4a3527}
[data-theme="dark"] .box.ok{background:#16241d;border-color:#24402f}
[data-theme="dark"] .box.info{background:#1b2330;border-color:#2b3a4d}
[data-theme="dark"] .derive-h,[data-theme="dark"] .derive-end{background:var(--purple-bg)}
[data-theme="dark"] .derive-q,[data-theme="dark"] .walk-req{background:var(--amber-bg)}
[data-theme="dark"] .walk-h{background:var(--blue-bg)}
[data-theme="dark"] .walk-oi{background:#18201d}
[data-theme="dark"] .dcheck{background:var(--green-bg)}
[data-theme="dark"] .ws-why{background:var(--purple-bg)}
[data-theme="dark"] .badge{background:#232b35;color:#a9bad0;border-color:var(--line)}
[data-theme="dark"] mark.sr-mk{background:#6b5a1f;color:#ffe9a8}
[data-theme="dark"] mark.sr-mk.hit{background:#7d6a24}
[data-theme="dark"] .sr-flash{background:#3a3320}
[data-theme="dark"] .sidebar,[data-theme="dark"] .sb-mask{box-shadow:none}
[data-theme="dark"] .nav a{color:var(--brand)}
[data-theme="dark"] footer{color:var(--ink-3)}

/* 深色下：图解与卡片里的文字颜色（这些规则原本写死了浅色主题的颜色） */
[data-theme="dark"] .ds{color:var(--fg);background:var(--card);border-color:var(--line)}
[data-theme="dark"] .dn{color:var(--fg);background:var(--card);border-color:var(--line)}
[data-theme="dark"] .dn.dq{background:#2a2419;border-color:#5a4a24;color:#f0d79a}
[data-theme="dark"] .dc{background:#1b2733;color:#9ad2ff}
[data-theme="dark"] .dt{color:var(--ink-2)}
[data-theme="dark"] .darr .dcell b,[data-theme="dark"] .dcell b{color:var(--fg)}
[data-theme="dark"] .dcell i{color:var(--ink-3)}
[data-theme="dark"] .dmc{color:var(--fg)}
[data-theme="dark"] .dmh{color:var(--ink-3)}
[data-theme="dark"] .dtn{color:var(--fg);background:var(--card);border-color:var(--line)}
[data-theme="dark"] .dtn.leaf{background:#1d2733}
[data-theme="dark"] .arm{color:var(--ink-2);background:var(--card);border-color:var(--line)}
[data-theme="dark"] .arm.ok{background:#16241d;border-color:#2c4a38}
[data-theme="dark"] .arm.no{background:#2a1e1a;border-color:#4a3128}
[data-theme="dark"] .dnote{color:var(--ink-3)}
[data-theme="dark"] .dtl,[data-theme="dark"] .wtl{color:#9dc0f5}
[data-theme="dark"] .dcover{background:#241f33;border-color:#3d3660;color:#c3b6ea}
[data-theme="dark"] .walk-oi .tags span{background:#1e262f;color:var(--ink-3);border-color:var(--line)}
[data-theme="dark"] .pid{background:#1c2a3a;color:#8fbcf0}
[data-theme="dark"] .sr-tag{background:#2a2419;border-color:#4a3f22;color:#e5c98a}
[data-theme="dark"] .opt,[data-theme="dark"] .pwhy,[data-theme="dark"] .pintro{color:var(--ink-2)}

/* 卡片内的「追问」（原 .think 模块并入） */
.dthink,.wthink{margin:13px 17px 15px;padding:11px 14px;border:1px dashed var(--line);
  border-radius:10px;background:#faf8ff}
.wthink{background:#f7fbff}
.dthink .dtk,.wthink .dtk{font-size:12.8px;font-weight:700;color:var(--purple);margin-bottom:7px;
  letter-spacing:.02em}
.wthink .dtk{color:var(--blue)}
.dthink ol,.wthink ol{margin:0;padding-left:20px}
.dthink li,.wthink li{margin:7px 0;font-size:14px;color:var(--ink-2);line-height:1.75}
.dthink .tq,.wthink .tq{line-height:1.75}
.dthink details.ta,.wthink details.ta{border:0;background:transparent;margin:6px 0 0;padding:0 0 0 11px;
  border-left:3px solid #d9cdf9}
.wthink details.ta{border-left-color:#c9dcf7}
.dthink details.ta>summary,.wthink details.ta>summary{padding:2px 0;font-size:13px;font-weight:600;
  color:#6a5aa8}
.wthink details.ta>summary{color:#3f6ba8}
.dthink details.ta .dc,.wthink details.ta .dc{padding:3px 0 5px;font-size:14px;line-height:1.9;
  color:var(--ink-2)}
[data-theme="dark"] .dthink,[data-theme="dark"] .wthink{background:#1d1f2a;border-color:#333a47}
[data-theme="dark"] .dthink .dtk{color:#b3a6dd}
[data-theme="dark"] .wthink .dtk{color:#8fbcf0}

/* 深色补丁 v2：逐个覆盖仍然写死浅色底的组件（追加在最后，保证同等优先级下生效） */
[data-theme="dark"] .meta span{background:#232b35;border:1px solid var(--line);color:var(--ink-2)}
[data-theme="dark"] .badge{background:#232b35;border:1px solid var(--line);color:var(--ink-2)}
[data-theme="dark"] .badge.star{background:#3a2f14;border-color:#5a4a24;color:#e8c778}
[data-theme="dark"] .badge.diff{background:#16301f;border-color:#2c4a38;color:#8fceac}
[data-theme="dark"] .prob .io{background:#151a20;color:var(--ink-2)}
[data-theme="dark"] .reproduce{background:#1e1c16;border-color:#4a4028}
[data-theme="dark"] .challenge{background:var(--card);border-color:var(--line)}
[data-theme="dark"] .challenge.ch2{background:#182430;border-color:#2b3a4d}
[data-theme="dark"] .hintbox{background:#241f14;border-color:#4a3f22;color:var(--ink-2)}
[data-theme="dark"] .challenge.ch2 .hintbox{background:#16222e;border-color:#2b3a4d}
[data-theme="dark"] .think{background:#1e1b2c;border-color:#3a3355}
[data-theme="dark"] .nav a{background:var(--card);border-color:var(--line);color:var(--ink-2)}
[data-theme="dark"] .nav a:hover{border-color:var(--brand);color:var(--brand)}
[data-theme="dark"] .legend{background:var(--card);border-color:var(--line)}
[data-theme="dark"] .bar{background:#232b35}
[data-theme="dark"] .kbd{background:#232b35;border-color:var(--line);color:var(--ink-2)}
[data-theme="dark"] .sb-close{background:#232b35;border-color:var(--line);color:var(--ink-2)}
[data-theme="dark"] .sb-group{background:#1f262e;border-color:var(--line);color:#9dc0f5}
[data-theme="dark"] .sb-item{border-color:var(--line-2)}
[data-theme="dark"] .sb-item:hover{background:#232b35}
[data-theme="dark"] .sb-item.cur{background:#1c2a3a;border-left-color:var(--brand)}
[data-theme="dark"] .sb-nm em{background:#3a2f14;color:#e8c778}
[data-theme="dark"] .rt-close{background:#232b35;border-color:var(--line);color:var(--ink-2)}
[data-theme="dark"] .rt-close:hover,[data-theme="dark"] .rt-tab:hover{background:#232b35}
[data-theme="dark"] .rt-i:hover{background:#232b35}
[data-theme="dark"] .rt-i.cur{background:#1c2a3a}
[data-theme="dark"] .rt-tab{background:var(--card);border-color:var(--line);color:var(--ink-2)}
[data-theme="dark"] .sr-clear{background:var(--card);border-color:var(--line);color:var(--ink-2)}
[data-theme="dark"] .sr-clear:hover{background:#232b35}
[data-theme="dark"] .sr-title:hover,[data-theme="dark"] .sr-hit:hover{background:#232b35}
[data-theme="dark"] .portal{background:linear-gradient(180deg,#18222e 0%,#171c24 62%);
  border-color:#2b3a4d}
[data-theme="dark"] .portal .pl{background:var(--card);border-color:var(--line)}
[data-theme="dark"] .portal .pl:hover{background:#232b35;border-color:var(--brand)}
[data-theme="dark"] .portal .pmark{background:#1c2a3a;color:#8fbcf0}
[data-theme="dark"] .portal .pid{background:#1c2a3a;color:#8fbcf0}
[data-theme="dark"] .portal .pintro,[data-theme="dark"] .portal .pwhy{color:var(--ink-2)}
[data-theme="dark"] .dia{background:#171d26;border-color:#2b3441}
[data-theme="dark"] .dia>figcaption{color:#8fbcf0}
[data-theme="dark"] .dcell.hl,[data-theme="dark"] .dmc.hl{background:#1b2b3f;border-color:var(--brand)}
[data-theme="dark"] .dcmp.l{background:#2a1e1a;border-color:#4a3128}
[data-theme="dark"] .dcmp.r{background:#16241d;border-color:#24402f}
[data-theme="dark"] .dcmp li{color:var(--ink-2)}
[data-theme="dark"] .derive-h .dcover{background:#241f33;border-color:#3d3660;color:#c3b6ea}
[data-theme="dark"] .walk-oi{background:#18201d;border-color:var(--line)}
[data-theme="dark"] .toc-group{border-left-color:var(--brand)}
[data-theme="dark"] .progressbox{background:var(--card)}
[data-theme="dark"] .topbar{border-bottom:1px solid var(--line)}
[data-theme="dark"] .theme-btn{background:var(--card);border-color:var(--line);color:var(--ink-2)}
[data-theme="dark"] footer{border-top:1px solid var(--line)}

/* 挑战卡的样例块与题号 chip（原来是行内样式，深色模式覆盖不到） */
.csample{white-space:pre-wrap;background:#f8fafc;border:1px dashed #d7dfeb;border-radius:8px;
  padding:8px 12px;margin:8px 0;font-family:Consolas,monospace;font-size:13px;color:#3c4757}
.ochip{font-size:13px;color:#5b6577;background:#eef3fb;border-radius:6px;padding:2px 8px}
[data-theme="dark"] .csample{background:#151a20;border-color:#2b3441;color:var(--ink-2)}
[data-theme="dark"] .ochip{background:#1c2a3a;color:#8fbcf0}
"""

JS = r"""
// 搜索过滤（目录页）
document.addEventListener('DOMContentLoaded',function(){
  var inp=document.getElementById('q');
  if(!inp)return;
  inp.addEventListener('input',function(){
    var v=this.value.trim().toLowerCase();
    document.querySelectorAll('.toc-item').forEach(function(el){
      var t=el.dataset.k||'';
      el.style.display=(!v||t.indexOf(v)>=0)?'':'none';
    });
    document.querySelectorAll('.toc-group').forEach(function(g){
      var any=false,n=g.nextElementSibling;
      while(n&&n.classList&&n.classList.contains('toc-list')){
        if([...n.children].some(c=>c.style.display!=='none'))any=true;
        break;
      }
      g.style.display=(!v||any)?'':'none';
    });
  });
  // 本地记录进度
  var id=document.body.dataset.lesson;
  if(id){try{localStorage.setItem('ac_'+id,'1')}catch(e){}}
});
"""


# ----------------------------------------------------------------- 工具函数
def esc(s):
    return html.escape(str(s), quote=False)


def esc_code(s):
    """用于 <code> 内：先反转义一次，再统一转义，避免出现 &amp;gt; 双转义。"""
    t = html.unescape(str(s))
    return html.escape(t, quote=False)


def esc_attr(s):
    return html.escape(str(s), quote=True)


KEYWORDS = set("""alignas alignof and and_eq asm auto bitand bitor bool break case catch char
char8_t char16_t char32_t class compl concept const consteval constexpr constinit const_cast
continue co_await co_return co_yield decltype default delete do double dynamic_cast else enum
explicit export extern false float for friend goto if inline int long mutable namespace new
noexcept not not_eq nullptr operator or or_eq private protected public register reinterpret_cast
requires return short signed sizeof static static_assert static_cast struct switch template this
thread_local throw true try typedef typeid typename union unsigned using virtual void volatile
wchar_t while xor xor_eq size_t string vector map set queue stack pair priority_queue greater
less sort unique lower_bound upper_bound reverse max min abs sqrt printf scanf memset memcpy
fill swap push_back pop_back begin end size empty first second cin cout endl getline ios
sync_with_stdio tie nullptr_t INT_MAX LLONG_MAX""".split())


def hl(code):
    """极简 C++ 高亮：注释、字符串、字符、数字、关键字、Common 函数名。"""
    out = []
    i, n = 0, len(code)
    while i < n:
        c = code[i]
        # 行注释
        if code.startswith("//", i):
            j = code.find("\n", i)
            j = n if j < 0 else j
            out.append('<span class="c">%s</span>' % esc(code[i:j]))
            i = j
            continue
        # 块注释
        if code.startswith("/*", i):
            j = code.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append('<span class="c">%s</span>' % esc(code[i:j]))
            i = j
            continue
        # 字符串 / 字符
        if c in "\"'":
            q = c
            j = i + 1
            while j < n:
                if code[j] == "\\":
                    j += 2
                    continue
                if code[j] == q:
                    j += 1
                    break
                if code[j] == "\n":
                    break
                j += 1
            out.append('<span class="s">%s</span>' % esc(code[i:j]))
            i = j
            continue
        # 预处理指令整行
        if c == "#" and (i == 0 or code[i - 1] == "\n"):
            j = code.find("\n", i)
            j = n if j < 0 else j
            out.append('<span class="k">%s</span>' % esc(code[i:j]))
            i = j
            continue
        # 数字
        if c.isdigit():
            j = i
            while j < n and (code[j].isalnum() or code[j] in "._'"):
                j += 1
            out.append('<span class="n">%s</span>' % esc(code[i:j]))
            i = j
            continue
        # 标识符
        if c.isalpha() or c == "_":
            j = i
            while j < n and (code[j].isalnum() or code[j] == "_"):
                j += 1
            w = code[i:j]
            if w in KEYWORDS:
                out.append('<span class="k">%s</span>' % esc(w))
            elif j < n and code[j] == "(":
                out.append('<span class="f">%s</span>' % esc(w))
            else:
                out.append(esc(w))
            i = j
            continue
        out.append(esc(c))
        i += 1
    return "".join(out)


def code_block(code, caption=None):
    h = []
    if caption:
        h.append('<div class="cap">%s</div>' % esc(caption))
    h.append("<pre><code>%s</code></pre>" % hl(code.rstrip("\n")))
    return "".join(h)


# ----------------------------------------------------------------- 渲染块
def render_blocks(blocks):
    out = []
    for b in blocks or []:
        if isinstance(b, str):
            out.append("<p>%s</p>" % esc(b))
            continue
        k = b.get("kind")
        if k == "p" or k == "intro" or k == "text":
            out.append("<p>%s</p>" % b["text"])
        elif k == "quote":
            out.append('<div class="quote">%s</div>' % b["text"])
        elif k == "list":
            tag = "ol" if b.get("ordered") else "ul"
            items = "".join("<li>%s</li>" % it for it in b["items"])
            out.append("<%s>%s</%s>" % (tag, items, tag))
        elif k == "table":
            ws = b.get("widths")
            head = b.get("head") or []
            th = "".join("<th>%s</th>" % esc(x) for x in head)
            body = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % x for x in row)
                           for row in b["rows"])
            tbl = "<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>" % (th, body)
            out.append(tbl)
        elif k == "note":
            lv = b.get("level", "info")
            lines = "".join("<p>%s</p>" % x for x in b.get("lines", []))
            out.append('<div class="box %s"><div class="t">%s</div>%s</div>'
                       % (lv, esc(b.get("title", "")), lines))
        elif k == "code":
            out.append(code_block(b["code"], b.get("caption")))
        elif k == "diagram":
            out.append(diagrams.build(b))
        elif k == "derive":
            out.append(render_derive(b))
        elif k == "walk":
            out.append(render_walk(b))
        elif k == "example":
            pr = b["problem"]
            st = render_blocks(b.get("statement", []))
            io = ""
            if pr.get("sample"):
                io = '<div class="io">%s</div>' % esc(pr["sample"])
            out.append(
                '<div class="prob"><div class="ph"><span class="pn">例题 · %s</span>'
                '<span class="oi">%s %s</span><span class="badge diff">%s</span>'
                '<a href="%s" target="_blank" rel="noopener">去洛谷做这题 ↗</a></div>'
                '<div class="st">%s</div>%s</div>'
                % (esc(pr["name"]), esc(pr.get("oj", "洛谷")), esc(pr.get("id", "")),
                   esc(pr.get("diff", "")), esc_attr(pr.get("link", "#")), st, io))
        elif k == "idea" or k == "after":
            inner = render_blocks(b.get("blocks", []))
            out.append('<div class="step"><div class="sh">%s</div>%s</div>'
                       % (esc(b.get("title", "思路")), inner))
        elif k == "explain":
            rows = "".join("<tr><td><code>%s</code></td><td>%s</td></tr>"
                           % (esc_code(a), t) for a, t in b["rows"])
            out.append('<div class="step"><div class="sh">%s</div>'
                       '<table class="lines"><thead><tr><th>代码片段</th><th>含义与理由</th>'
                       '</tr></thead><tbody>%s</tbody></table></div>'
                       % (esc(b.get("title", "逐行拆解")), rows))
        elif k == "func":
            rows = "".join("<tr><td><code>%s</code></td><td>%s</td></tr>" % (esc_code(a), t)
                           for a, t in b.get("proto", []))
            notes = "".join("<p>%s</p>" % x for x in b.get("notes", []))
            ex = code_block(b["example"], "示例") if b.get("example") else ""
            out.append(
                '<div class="fn"><div class="fh">新函数拆解 · %s</div><div class="fb">'
                '<div class="sig">%s</div>'
                '<table class="lines"><thead><tr><th>组成</th><th>含义 / 格式要求</th>'
                '</tr></thead><tbody>%s</tbody></table>'
                '<div class="cap">最小可运行示例</div>%s%s</div></div>'
                % (esc(b["name"]), esc(b.get("signature", "")), rows, ex,
                   ('<div class="box tip"><div class="t">注意</div>%s</div>' % notes) if notes else ""))
        elif k == "reproduce":
            out.append('<div class="reproduce"><div class="rt">自己动手复现</div>%s</div>'
                       % "".join("<p>%s</p>" % x for x in b.get("lines", [])))
        else:
            out.append("<!-- unknown block %s -->" % esc(k))
    return "".join(out)


# ----------------------------------------------------------------- 页面模板
PAGE_ROOT = "../"     # 章节页在 sections/ 下，回课程根要用 ../

PAGE = """<!doctype html>
<html lang="zh-CN"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · {site}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="{root}assets/style.css">
<script>(function () {{ try {{ var t = localStorage.getItem('ac.theme');
if (t === 'light' || t === 'dark') {{ document.documentElement.setAttribute('data-theme', t);
document.documentElement.style.colorScheme = t; }} }} catch (e) {{}} }})();</script>
</head><body data-lesson="{lid}" data-root="{root}">
<div class="topbar"><div class="inner">
  <a href="{root}index.html">← 目录</a>
  <span class="spacer"></span>
  <span id="pageMark" class="page-mark">{mark}</span>
  <span>{crumb}</span>
  <span class="spacer"></span>
  <a href="{root}index.html">全部 {total} 节</a>
  <button class="theme-btn" data-theme-toggle type="button" aria-label="切换深浅色" title="切换深浅色">◐</button>
</div></div>
<div class="wrap">
{body}
<div class="nav">{nav}</div>
<footer>算竞教程 · {site} · 生成于自建课程体系，题目版权归洛谷及各命题方所有<br>
转载请注明出处；模板代码可直接用于比赛</footer>
</div>
{extra_scripts}<script src="{root}assets/toc.js"></script>
<script src="{root}assets/app.js"></script>
</body></html>
"""


def render_rtoc(outline, summary=""):
    """右侧「本节目录」：本节概述 + 全部小标题。"""
    if not outline:
        return ""
    items = []
    for o in outline:
        items.append('<a class="rt-i lv%d" href="#%s" data-t="%s">%s</a>'
                     % (o["lv"], o["id"], o["id"], esc(o["t"])))
    return (
        '<button class="rt-tab" id="rtTab" type="button" aria-label="打开本节目录">≡ 本节目录</button>'
        '<aside class="rtoc" id="rtoc" aria-label="本节目录">'
        '<div class="rt-head"><span class="rt-title">本节目录</span>'
        '<button class="rt-close" id="rtClose" type="button" title="收起">&#187;</button></div>'
        '<div class="rt-sum">%s</div>'
        '<nav class="rt-body">%s</nav>'
        '</aside>' % (esc(summary), "".join(items)))


def _rel(h):
    """课程根的相对链接 → 从 sections/ 出发的链接。"""
    if not h or h.startswith(("http", "#")):
        return h
    return PAGE_ROOT + h


def _think_html(items, kind="derive"):
    """卡片内的「追问」块：问题 + 折叠解析。"""
    if not items:
        return ""
    box = []
    for it in items:
        q, a = it[0], (it[1] if len(it) > 1 else "")
        if a:
            box.append('<li><div class="tq">%s</div>'
                       '<details class="ta"><summary>想好了？点开核对思路与解析</summary>'
                       '<div class="dc">%s</div></details></li>' % (q, a))
        else:
            box.append('<li><div class="tq">%s</div></li>' % q)
    cls = "wthink" if kind == "walk" else "dthink"
    label = "追问 · 落到代码上再想一遍" if kind == "walk" else "追问 · 把这一步想透"
    return ('<div class="%s"><div class="dtk">%s</div><ol>%s</ol></div>'
            % (cls, label, "".join(box)))


def render_derive(b):
    """推导卡：问题 → 尝试 → 验证 → 落定理。"""
    head = ('<div class="derive"><div class="derive-h">'
            '<span class="dk">推导</span><b class="dtl">%s</b>%s<span class="dsub">%s</span></div>'
            % (esc(b.get("title", "")),
               ('<span class="dcover">%s</span>' % esc(b["cover"])) if b.get("cover") else "",
               esc(b.get("sub", ""))))
    q = '<div class="derive-q"><b>问题</b>%s</div>' % render_blocks(b.get("problem"))
    steps = []
    for i, item in enumerate(b.get("steps") or [], 1):
        h, body = item[0], item[1]
        chk = item[2] if len(item) > 2 else None
        s = ('<div class="dstep"><div class="dh"><span class="dnum">%d</span>'
             '<span class="dt">%s</span></div>%s' % (i, esc(h), render_blocks(body)))
        if chk:
            s += '<div class="dcheck"><b>验证 / 关键</b>%s</div>' % render_blocks(chk)
        steps.append(s + "</div>")
    end = '<div class="derive-end"><b>于是我们得到：</b>%s</div>' % render_blocks(b.get("end"))
    return head + q + "".join(steps) + end + _think_html(b.get("think"), "derive") + "</div>"


def render_walk(b):
    """算法落地卡：需求 → 拆步（每步代码 + 为什么）→ 竞赛用法。"""
    head = ('<div class="walk"><div class="walk-h">'
            '<span class="wk">算法落地</span><b class="wtl">%s</b>%s</div>'
            % (esc(b.get("title", "")),
               ('<span class="cover">%s</span>' % esc(b["cover"])) if b.get("cover") else ""))
    req = '<div class="walk-req"><b>需求</b>%s</div>' % render_blocks(b.get("req"))
    steps = []
    for i, item in enumerate(b.get("steps") or [], 1):
        h, body = item[0], item[1]
        why = item[2] if len(item) > 2 else None
        s = ('<div class="walk-step"><div class="ws-h"><span class="ws-n">%d</span>%s</div>%s'
             % (i, esc(h), render_blocks(body)))
        if why:
            s += '<div class="ws-why"><b>为什么</b>%s</div>' % render_blocks(why)
        steps.append(s + "</div>")
    tags = "".join('<span>%s</span>' % esc(t) for t in (b.get("tags") or []))
    oi = ('<div class="walk-oi"><b>竞赛用法</b>%s%s</div>'
          % (render_blocks(b.get("oi")), ('<div class="tags">%s</div>' % tags) if tags else ""))
    return (head + req + "".join(steps) + oi + _think_html(b.get("think"), "walk")
            + "</div>")


def render_portal(p):
    """数学传送门：指向数学分区对应章节，替代「数学补给」卡片。"""
    if not p:
        return ""
    links = []
    for item in p.get("links", []):
        lid, title, href, why = item
        links.append(
            '<a class="pl" href="%s">'
            '<span class="pid">%s</span>'
            '<span class="pbody"><span class="ptitle">%s</span>'
            '<span class="pwhy">%s</span></span>'
            '<span class="parrow">\u2197</span></a>'
            % (esc_attr(_rel(href)), esc(lid), esc(title), esc(why)))
    home = p.get("home", "")
    home_link = ('<a class="phome" href="%s">整门课 &#8599;</a>' % esc_attr(_rel(home))) if home else ""
    return (
        '<div class="portal"><div class="pt">'
        '<span class="pmark">%s</span>'
        '<span class="ptt">数学传送门 \u00b7 %s</span>%s</div>'
        '<div class="pintro">%s</div>'
        '<div class="plist">%s</div></div>'
        % (esc(p.get("mark", "\u25c8")), esc(p.get("course", "")), home_link,
           esc(p.get("intro", "")), "".join(links)))


def fmt_page(**kw):
    """PAGE.format 的包装：extra_scripts 默认为空，避免漏传。"""
    kw.setdefault("extra_scripts", "")
    return PAGE.format(**kw)


def doc_entry(file, title, level, group, tags, entries):
    """一页的检索元数据。"""
    return {"file": file, "t": title, "lv": level, "g": group,
            "tags": list(tags or []), "b": entries}


def write_assets(outdir, course=None):
    """写出 CSS / JS / 目录数据。app.js 从 assets_src 读取（便于单独维护）。"""
    import json
    adir = os.path.join(outdir, "assets")
    os.makedirs(adir, exist_ok=True)
    with open(os.path.join(adir, "style.css"), "w", encoding="utf-8") as f:
        f.write(CSS)
    src_js = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets_src", "app.js")
    if os.path.exists(src_js):
        with open(src_js, encoding="utf-8") as f:
            js = f.read()
    else:
        js = JS
    with open(os.path.join(adir, "app.js"), "w", encoding="utf-8") as f:
        f.write(js)
    if course is not None:
        with open(os.path.join(adir, "toc.js"), "w", encoding="utf-8") as f:
            f.write("window.COURSE = ")
            json.dump(course, f, ensure_ascii=False)
            f.write(";\n")


def render_lesson(lesson, all_lessons, outdir):
    lid = lesson["id"]
    prev_l = next((x for x in all_lessons if x["id"] == lid - 1), None)
    next_l = next((x for x in all_lessons if x["id"] == lid + 1), None)
    nav = []
    if prev_l:
        nav.append('<a href="%s">← %02d %s</a>' % (os.path.basename(prev_l["file"]), prev_l["id"], esc(prev_l["title"])))
    else:
        nav.append('<a class="disabled">← 已经是第一节</a>')
    if next_l:
        nav.append('<a href="%s">%02d %s →</a>' % (os.path.basename(next_l["file"]), next_l["id"], esc(next_l["title"])))
    else:
        nav.append('<a class="disabled">已经是最后一节 →</a>')

    body = []
    star = '<span class="badge star">⭐ 已学范围</span>' if lesson.get("star") else ""
    body.append('<h1>%02d · %s</h1>' % (lid, esc(lesson["title"])))
    body.append('<div class="sub">%s</div>' % esc(lesson.get("summary", "")))
    body.append('<div class="meta">%s<span class="badge diff">%s</span>'
                '<span>预计 %s 分钟</span>%s</div>'
                % (star, esc(lesson.get("level", "")), lesson.get("minutes", 40),
                   "".join('<span>%s</span>' % esc(t) for t in lesson.get("tags", []))))

    # 本节新函数列表
    fns = [s for s in lesson.get("sections", []) if s.get("kind") == "func"]
    if fns:
        body.append('<div class="box info"><div class="t">本节出现的新函数 / 新语法（先看懂再用）</div>')
        body.append('<ul>%s</ul></div>' % "".join(
            '<li><a href="#fn-%d">%s</a> —— %s</li>' % (i, esc(f["name"]), esc(f.get("brief", "")))
            for i, f in enumerate(fns)))

    body.append(render_blocks(lesson.get("sections", [])))

    # 数学传送门（优先）／数学补给
    if lesson.get("portal"):
        body.append(render_portal(lesson["portal"]))
    elif lesson.get("math"):
        m = lesson["math"]
        body.append('<div class="mathcard"><div class="mt">数学补给 · %s</div>%s</div>'
                    % (esc(m.get("title", "")), render_blocks(m.get("body", []))))

    # 思考点
    if lesson.get("think"):
        ans = lesson.get("think_a") or []
        items = []
        for i, t in enumerate(lesson["think"]):
            a = ans[i] if i < len(ans) else ""
            if a:
                items.append('<li><div class="tq">%s</div>'
                             '<details class="ta"><summary>想好了？点开核对思路与解析</summary>'
                             '<div class="dc">%s</div></details></li>' % (t, a))
            else:
                items.append('<li><div class="tq">%s</div></li>' % t)
        body.append('<div class="think"><div class="tt">举一反三 · 想清楚这些再往下走</div>'
                    '<div class="thint">先自己写出答案，再点开核对——方向对不对，比答案本身更重要</div>'
                    '<ol>%s</ol></div>' % "".join(items))

    # 自测
    if lesson.get("check"):
        body.append('<div class="box tip"><div class="t">自测：能全部回答再进下一节</div><ul>%s</ul></div>'
                    % "".join("<li>%s</li>" % t for t in lesson["check"]))

    # 挑战题
    ch = lesson.get("challenge")
    if ch:
        body.append('<div class="challenge"><div class="ct">挑战题 · %s</div>' % esc(ch["name"]))
        body.append('<div class="ph" style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">'
                    '<span class="oi ochip">%s %s</span>'
                    '<span class="badge diff">%s</span>'
                    '<a href="%s" target="_blank" rel="noopener">去洛谷做这题 ↗</a></div>'
                    % (esc(ch.get("oj", "洛谷")), esc(ch.get("id", "")), esc(ch.get("diff", "")),
                       esc_attr(ch.get("link", "#"))))
        body.append('<div class="st">%s</div>' % render_blocks(ch.get("statement", [])))
        if ch.get("hint"):
            body.append('<div class="hintbox"><div class="ht">引导性提示（先只看这里）</div>%s</div>'
                        % "".join("<p>%s</p>" % h for h in ch["hint"]))
        if ch.get("idea"):
            body.append('<details><summary>想看思路了？点开完整思路</summary><div class="dc">%s</div></details>'
                        % render_blocks([{"kind": "p", "text": x} for x in ch["idea"]]))
        if ch.get("code"):
            inner = [code_block(ch["code"], "参考代码")]
            if ch.get("explain"):
                rows = "".join("<tr><td><code>%s</code></td><td>%s</td></tr>" % (esc_code(a), t)
                               for a, t in ch["explain"])
                inner.append('<div class="cap">关键片段拆解</div><table class="lines">'
                             '<thead><tr><th>片段</th><th>作用</th></tr></thead><tbody>%s</tbody>'
                             '</table>' % rows)
            if ch.get("pitfalls"):
                inner.append('<div class="box warn"><div class="t">这题最容易错的地方</div><ul>%s</ul></div>'
                             % "".join("<li>%s</li>" % p for p in ch["pitfalls"]))
            body.append('<details><summary>还是不会？点开题解代码与拆解</summary><div class="dc">%s</div>'
                        '</details>' % "".join(inner))
        body.append("</div>")

    if lesson.get("challenge2"):
        body.append('<div class="box tip" style="margin:22px 0 -6px"><div class="t">'
                    '挑战 2 · 难度高一级，允许组合多个已学算法</div>'
                    '<p>这题比上面的挑战题更难：它不只用本节一个算法，可能需要把前面几节的工具拼起来。'
                    '独立做出来说明这一块真的过关了；做完记得在侧边栏勾上 🌟。</p></div>')
        body.append(render_challenge_card(lesson["challenge2"], label="挑战 2", cls="ch2"))

    if lesson.get("refs"):
        body.append('<div class="box info"><div class="t">延伸阅读 / 参考</div><ul>%s</ul></div>'
                    % "".join("<li>%s</li>" % r for r in lesson["refs"]))

    crumb = "第 %d / %d 节" % (lid, len(all_lessons))
    page_body, entries, outline = searchindex.build("".join(body))
    page_body += render_rtoc(outline, lesson.get("summary", ""))
    page = fmt_page(title=esc(lesson["title"]), site=SITE, desc=esc_attr(lesson.get("summary", "")),
                       root=PAGE_ROOT, lid=lid, crumb=crumb, total=len(all_lessons), mark=('⭐' if lesson.get('star') else ''),
                       body=page_body, nav="".join(nav))
    path = os.path.join(outdir, lesson["file"])
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
    return doc_entry(lesson["file"], lesson["title"], lesson.get("level", ""),
                     lesson.get("group", ""), lesson.get("tags"), entries)


# ----------------------------------------------------------------- 挑战题渲染
def render_challenge_card(ch, idx=None, big=False, label="挑战题", cls=""):
    h = []
    h.append('<div class="challenge%s">' % (" " + cls if cls else ""))
    head = '<div class="ct">%s%s%s · %s</div>' % (
        "大题 " if big else "", label, (" %d" % idx) if idx else "", esc(ch["name"]))
    h.append(head)
    h.append('<div class="ph" style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">'
             '<span class="oi ochip">%s %s</span>'
             '<span class="badge diff">%s</span>'
             '<a href="%s" target="_blank" rel="noopener">去洛谷做这题 ↗</a></div>'
             % (esc(ch.get("oj", "洛谷")), esc(ch.get("id", "")), esc(ch.get("diff", "")),
                esc_attr(ch.get("link", "#"))))
    h.append('<div class="st">%s</div>' % render_blocks(ch.get("statement", [])))
    if ch.get("sample"):
        h.append('<div class="cap">样例</div><div class="csample">%s</div>' % esc(ch["sample"]))
    if ch.get("hint"):
        h.append('<div class="hintbox"><div class="ht">引导性提示（先只看这里）</div>%s</div>'
                 % "".join("<p>%s</p>" % x for x in ch["hint"]))
    if ch.get("idea"):
        h.append('<details><summary>想看思路了？点开完整思路</summary><div class="dc">%s</div></details>'
                 % render_blocks([{"kind": "p", "text": x} for x in ch["idea"]]))
    if ch.get("code"):
        inner = [code_block(ch["code"], "参考代码")]
        if ch.get("explain"):
            rows = "".join("<tr><td><code>%s</code></td><td>%s</td></tr>" % (esc_code(a), t)
                           for a, t in ch["explain"])
            inner.append('<div class="cap">关键片段拆解</div><table class="lines">'
                         '<thead><tr><th>片段</th><th>作用</th></tr></thead><tbody>%s</tbody>'
                         '</table>' % rows)
        if ch.get("pitfalls"):
            inner.append('<div class="box warn"><div class="t">这题最容易错的地方</div><ul>%s</ul></div>'
                         % "".join("<li>%s</li>" % p for p in ch["pitfalls"]))
        h.append('<details><summary>还是不会？点开题解代码与拆解</summary><div class="dc">%s</div>'
                 '</details>' % "".join(inner))
    h.append("</div>")
    return "".join(h)


# ----------------------------------------------------------------- 回顾章
def _render_math_think(lesson):
    """数学补给（或数学传送门）+ 举一反三。三处渲染共用。"""
    out = []
    if lesson.get("portal"):
        out.append(render_portal(lesson["portal"]))
    elif lesson.get("math"):
        m = lesson["math"]
        out.append('<div class="mathcard"><div class="mt">数学补给 · %s</div>%s</div>'
                   % (esc(m.get("title", "")), render_blocks(m.get("body", []))))
    if lesson.get("think"):
        ans = lesson.get("think_a") or []
        items = []
        for i, t in enumerate(lesson["think"]):
            a = ans[i] if i < len(ans) else ""
            if a:
                items.append('<li><div class="tq">%s</div>'
                             '<details class="ta"><summary>想好了？点开核对思路与解析</summary>'
                             '<div class="dc">%s</div></details></li>' % (t, a))
            else:
                items.append('<li><div class="tq">%s</div></li>' % t)
        out.append('<div class="think"><div class="tt">举一反三 · 想清楚这些再往下走</div>'
                   '<div class="thint">先自己写出答案，再点开核对——方向对不对，比答案本身更重要</div>'
                   '<ol>%s</ol></div>' % "".join(items))
    return "".join(out)


def render_review(lesson, all_lessons, outdir):
    lid = lesson["id"]
    prev_l = next((x for x in all_lessons if x["id"] == lid - 1), None)
    next_l = next((x for x in all_lessons if x["id"] == lid + 1), None)
    nav = ['<a href="%s">← %02d %s</a>' % (os.path.basename(prev_l["file"]), prev_l["id"], esc(prev_l["title"]))
           if prev_l else '<a class="disabled">← 第一节</a>',
           '<a href="%s">%02d %s →</a>' % (os.path.basename(next_l["file"]), next_l["id"], esc(next_l["title"]))
           if next_l else '<a class="disabled">最后一节 →</a>']

    body = []
    body.append('<h1>%02d · %s</h1>' % (lid, esc(lesson["title"])))
    body.append('<div class="sub">%s</div>' % esc(lesson.get("summary", "")))
    star_badge = '<span class="badge star">⭐ 已学范围</span>' if lesson.get("star") else ""
    body.append('<div class="meta">' + star_badge + '<span class="badge">回顾训练</span>'
                '<span class="badge diff">%s</span><span>建议 %s 分钟</span>%s</div>'
                % (esc(lesson.get("level", "")), lesson.get("minutes", 90),
                   "".join("<span>%s</span>" % esc(t) for t in lesson.get("tags", []))))

    if lesson.get("sections"):
        body.append(render_blocks(lesson["sections"]))
    body.append(_render_math_think(lesson))

    chs = lesson.get("challenges") or []
    if chs:
        body.append('<h2>本次训练 · 共 %d 题</h2>' % len(chs))
        body.append('<div class="box tip"><div class="t">做题方式</div>'
                    '<p>限时 <b>%d 分钟</b>。每题先自己写 20~25 分钟；写不出来先看提示，'
                    '再给自己 10 分钟；还不行才点开思路。每题都独立限时，不要一题耗死。</p></div>'
                    % max(60, 20 * len(chs)))
        for i, ch in enumerate(chs, 1):
            body.append(render_challenge_card(ch, idx=i, big=True))

    if lesson.get("challenge2"):
        body.append('<div class="box tip" style="margin:24px 0 -6px"><div class="t">'
                    '附加挑战 2（不计入限时）</div>'
                    '<p>做完上面的整套题还有余力，再啃这一道。它比本套题的平均难度高一级。</p></div>')
        body.append(render_challenge_card(lesson["challenge2"], label="挑战 2", cls="ch2"))

    if lesson.get("check"):
        body.append('<div class="box ok"><div class="t">做完之后自问</div><ul>%s</ul></div>'
                    % "".join("<li>%s</li>" % t for t in lesson["check"]))
    if lesson.get("refs"):
        body.append('<div class="box info"><div class="t">延伸阅读</div><ul>%s</ul></div>'
                    % "".join("<li>%s</li>" % r for r in lesson["refs"]))

    page_body, entries, outline = searchindex.build("".join(body))
    page_body += render_rtoc(outline, lesson.get("summary", ""))
    page = fmt_page(title=esc(lesson["title"]), site=SITE,
                       desc=esc_attr(lesson.get("summary", "")), root=PAGE_ROOT, lid=lid,
                       crumb="第 %d / %d 节" % (lid, len(all_lessons)),
                       total=len(all_lessons), mark=('⭐' if lesson.get("star") else ""), body=page_body, nav="".join(nav))
    with open(os.path.join(outdir, lesson["file"]), "w", encoding="utf-8") as f:
        f.write(page)
    return doc_entry(lesson["file"], lesson["title"], lesson.get("level", ""),
                     lesson.get("group", ""), lesson.get("tags"), entries)


# ----------------------------------------------------------------- 模拟赛
def render_mock(lesson, all_lessons, outdir):
    lid = lesson["id"]
    prev_l = next((x for x in all_lessons if x["id"] == lid - 1), None)
    next_l = next((x for x in all_lessons if x["id"] == lid + 1), None)
    nav = ['<a href="%s">← %02d %s</a>' % (os.path.basename(prev_l["file"]), prev_l["id"], esc(prev_l["title"]))
           if prev_l else '<a class="disabled">← 第一节</a>',
           '<a href="%s">%02d %s →</a>' % (os.path.basename(next_l["file"]), next_l["id"], esc(next_l["title"]))
           if next_l else '<a class="disabled">最后一节 →</a>']

    body = []
    body.append('<h1>%02d · %s</h1>' % (lid, esc(lesson["title"])))
    body.append('<div class="sub">%s</div>' % esc(lesson.get("summary", "")))
    star_badge = '<span class="badge star">⭐ 已学范围</span>' if lesson.get("star") else ""
    body.append('<div class="meta">' + star_badge + '<span class="badge">模拟赛</span>'
                '<span class="badge diff">%s</span><span>限时 %s 分钟</span>%s</div>'
                % (esc(lesson.get("level", "")), lesson.get("minutes", 120),
                   "".join("<span>%s</span>" % esc(t) for t in lesson.get("tags", []))))

    if lesson.get("sections"):
        body.append(render_blocks(lesson["sections"]))
    body.append(_render_math_think(lesson))

    probs = lesson.get("challenges") or []
    if probs:
        body.append('<h2>题目 · 共 %d 题</h2>' % len(probs))
        body.append('<table><thead><tr><th>题号</th><th>题目</th><th>难度</th><th>建议用时</th>'
                    '</tr></thead><tbody>%s</tbody></table>'
                    % "".join('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s 分钟</td></tr>'
                              % (chr(65 + i), esc(p["name"]), esc(p.get("diff", "")),
                                 p.get("t", 30)) for i, p in enumerate(probs)))
        body.append('<div class="box warn"><div class="t">比赛规则（自己执行）</div>'
                    '<ul><li>先花 8 分钟通读全部题目，按“会做 → 有思路 → 完全不会”排序。</li>'
                    '<li>单题最多投入 %d 分钟，超过就换题。</li>'
                    '<li>每题先写暴力拿部分分，再想正解。</li>'
                    '<li>最后 15 分钟不再改算法，只按清单检查数组大小、long long、多测清空、输出格式。</li>'
                    '</ul></div>' % max(35, lesson.get("minutes", 120) // len(probs)))
        for i, p in enumerate(probs):
            body.append(render_challenge_card(p, idx=None, big=True))
            body.append('<div style="margin:-14px 0 26px;color:#5b6577;font-size:13.5px">'
                        '↑ 第 %s 题 · %s</div>' % (chr(65 + i), esc(p["name"])))

    if lesson.get("challenge2"):
        body.append('<div class="box tip" style="margin:28px 0 -6px"><div class="t">'
                    '附加挑战 2（不计入限时，难度高一级）</div>'
                    '<p>整套题做完还有余力再啃这一道。它不在本场的考点范围内，'
                    '但只用已经学过的算法，需要把前面的工具自己拼起来。</p></div>')
        body.append(render_challenge_card(lesson["challenge2"], label="挑战 2", cls="ch2"))

    if lesson.get("check"):
        body.append('<div class="box ok"><div class="t">赛后必做</div><ul>%s</ul></div>'
                    % "".join("<li>%s</li>" % t for t in lesson["check"]))

    page_body, entries, outline = searchindex.build("".join(body))
    page_body += render_rtoc(outline, lesson.get("summary", ""))
    page = fmt_page(title=esc(lesson["title"]), site=SITE,
                       desc=esc_attr(lesson.get("summary", "")), root=PAGE_ROOT, lid=lid,
                       crumb="第 %d / %d 节" % (lid, len(all_lessons)),
                       total=len(all_lessons), mark=('⭐' if lesson.get("star") else ""), body=page_body, nav="".join(nav))
    with open(os.path.join(outdir, lesson["file"]), "w", encoding="utf-8") as f:
        f.write(page)
    return doc_entry(lesson["file"], lesson["title"], lesson.get("level", ""),
                     lesson.get("group", ""), lesson.get("tags"), entries)


# ----------------------------------------------------------------- 题解页
def render_solution(doc, outdir):
    """doc: {title, file, desc, level, source, sections:[blocks], problems:[challenge]}"""
    body = []
    body.append('<h1>%s</h1>' % esc(doc["title"]))
    body.append('<div class="sub">%s</div>' % esc(doc.get("desc", "")))
    body.append('<div class="meta"><span class="badge">题解</span>'
                '<span class="badge diff">%s</span><span>%s</span></div>'
                % (esc(doc.get("level", "")), esc(doc.get("source", ""))))

    if doc.get("skip"):
        body.append('<div class="box info"><div class="t">跳过说明</div><ul>%s</ul></div>'
                    % "".join("<li>%s</li>" % s for s in doc["skip"]))

    if doc.get("sections"):
        body.append(render_blocks(doc["sections"]))

    probs = doc.get("problems") or []
    if probs:
        body.append('<h2>题目索引</h2><table><thead><tr><th>题号</th><th>题目</th>'
                    '<th>核心考点</th><th>难度</th></tr></thead><tbody>%s</tbody></table>'
                    % "".join('<tr><td>%s</td><td><a href="#p%s">%s</a></td><td>%s</td><td>%s</td></tr>'
                              % (esc(p.get("letter", "%02d" % (i + 1))), esc(p.get("letter", str(i + 1))),
                                 esc(p["name"]), esc(p.get("tag", "")), esc(p.get("diff", "")))
                              for i, p in enumerate(probs)))
        for i, p in enumerate(probs):
            body.append('<h2 id="p%s">%s · %s</h2>'
                        % (esc(p.get("letter", str(i + 1))),
                           esc(p.get("letter", "%02d" % (i + 1))), esc(p["name"])))
            if p.get("difficulty_note"):
                body.append('<p>%s</p>' % p["difficulty_note"])
            if p.get("statement"):
                body.append('<div class="prob"><div class="ph"><span class="pn">题意</span>'
                            '<span class="badge diff">%s</span></div>%s</div>'
                            % (esc(p.get("diff", "")), render_blocks(p["statement"])))
            if p.get("hint"):
                body.append('<div class="hintbox"><div class="ht">引导性提示</div>%s</div>'
                            % "".join("<p>%s</p>" % x for x in p["hint"]))
            if p.get("idea"):
                body.append('<details><summary>思路（先自己推，再看这里）</summary><div class="dc">%s</div></details>'
                            % render_blocks([{"kind": "p", "text": x} for x in p["idea"]]))
            if p.get("code"):
                inner = [code_block(p["code"], "参考代码")]
                if p.get("explain"):
                    rows = "".join("<tr><td><code>%s</code></td><td>%s</td></tr>" % (esc_code(a), t)
                                   for a, t in p["explain"])
                    inner.append('<div class="cap">代码拆解</div><table class="lines">'
                                 '<thead><tr><th>片段</th><th>作用</th></tr></thead>'
                                 '<tbody>%s</tbody></table>' % rows)
                if p.get("pitfalls"):
                    inner.append('<div class="box warn"><div class="t">易错点</div><ul>%s</ul></div>'
                                 % "".join("<li>%s</li>" % x for x in p["pitfalls"]))
                body.append('<details><summary>题解代码与拆解</summary><div class="dc">%s</div>'
                            '</details>' % "".join(inner))

    body.append('<div class="nav" style="margin-top:36px">'
                '<a href="" + PAGE_ROOT + "index.html">← 返回目录</a></div>')
    page_body, entries, outline = searchindex.build("".join(body))
    page_body += render_rtoc(outline, doc.get("desc", ""))
    page = fmt_page(title=esc(doc["title"]), site=SITE,
                       desc=esc_attr(doc.get("desc", "")), root=PAGE_ROOT, lid=doc["file"],
                       crumb="题解", total="", mark="", body=page_body, nav="")
    with open(os.path.join(outdir, doc["file"]), "w", encoding="utf-8") as f:
        f.write(page)
    return doc_entry(doc["file"], doc["title"], doc.get("level", ""), "题解",
                     [doc.get("source", "")], entries)

