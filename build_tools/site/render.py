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
PAGE = """<!doctype html>
<html lang="zh-CN"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · {site}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="{root}assets/style.css">
</head><body data-lesson="{lid}">
<div class="topbar"><div class="inner">
  <a href="{root}index.html">← 目录</a>
  <span class="spacer"></span>
  <span id="pageMark" class="page-mark">{mark}</span>
  <span>{crumb}</span>
  <span class="spacer"></span>
  <a href="{root}index.html">全部 {total} 节</a>
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
        nav.append('<a href="%s">← %02d %s</a>' % (prev_l["file"], prev_l["id"], esc(prev_l["title"])))
    else:
        nav.append('<a class="disabled">← 已经是第一节</a>')
    if next_l:
        nav.append('<a href="%s">%02d %s →</a>' % (next_l["file"], next_l["id"], esc(next_l["title"])))
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

    # 数学补给
    m = lesson.get("math")
    if m:
        body.append('<div class="mathcard"><div class="mt">数学补给 · %s</div>%s</div>'
                    % (esc(m.get("title", "")), render_blocks(m.get("body", []))))

    # 思考点
    if lesson.get("think"):
        body.append('<div class="think"><div class="tt">举一反三 · 想清楚这些再往下走</div><ol>%s</ol></div>'
                    % "".join("<li>%s</li>" % t for t in lesson["think"]))

    # 自测
    if lesson.get("check"):
        body.append('<div class="box tip"><div class="t">自测：能全部回答再进下一节</div><ul>%s</ul></div>'
                    % "".join("<li>%s</li>" % t for t in lesson["check"]))

    # 挑战题
    ch = lesson.get("challenge")
    if ch:
        body.append('<div class="challenge"><div class="ct">挑战题 · %s</div>' % esc(ch["name"]))
        body.append('<div class="ph" style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">'
                    '<span class="oi" style="font-size:13px;color:#5b6577;background:#eef3fb;'
                    'border-radius:6px;padding:2px 8px">%s %s</span>'
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
    page_body, entries = searchindex.build("".join(body))
    page = fmt_page(title=esc(lesson["title"]), site=SITE, desc=esc_attr(lesson.get("summary", "")),
                       root="", lid=lid, crumb=crumb, total=len(all_lessons), mark=('⭐' if lesson.get('star') else ''),
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
             '<span class="oi" style="font-size:13px;color:#5b6577;background:#eef3fb;'
             'border-radius:6px;padding:2px 8px">%s %s</span>'
             '<span class="badge diff">%s</span>'
             '<a href="%s" target="_blank" rel="noopener">去洛谷做这题 ↗</a></div>'
             % (esc(ch.get("oj", "洛谷")), esc(ch.get("id", "")), esc(ch.get("diff", "")),
                esc_attr(ch.get("link", "#"))))
    h.append('<div class="st">%s</div>' % render_blocks(ch.get("statement", [])))
    if ch.get("sample"):
        h.append('<div class="cap">样例</div><div style="white-space:pre-wrap;background:#f8fafc;'
                 'border:1px dashed #d7dfeb;border-radius:8px;padding:8px 12px;margin:8px 0;'
                 'font-family:Consolas,monospace;font-size:13px">%s</div>' % esc(ch["sample"]))
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
def render_review(lesson, all_lessons, outdir):
    lid = lesson["id"]
    prev_l = next((x for x in all_lessons if x["id"] == lid - 1), None)
    next_l = next((x for x in all_lessons if x["id"] == lid + 1), None)
    nav = ['<a href="%s">← %02d %s</a>' % (prev_l["file"], prev_l["id"], esc(prev_l["title"]))
           if prev_l else '<a class="disabled">← 第一节</a>',
           '<a href="%s">%02d %s →</a>' % (next_l["file"], next_l["id"], esc(next_l["title"]))
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

    page_body, entries = searchindex.build("".join(body))
    page = fmt_page(title=esc(lesson["title"]), site=SITE,
                       desc=esc_attr(lesson.get("summary", "")), root="", lid=lid,
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
    nav = ['<a href="%s">← %02d %s</a>' % (prev_l["file"], prev_l["id"], esc(prev_l["title"]))
           if prev_l else '<a class="disabled">← 第一节</a>',
           '<a href="%s">%02d %s →</a>' % (next_l["file"], next_l["id"], esc(next_l["title"]))
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

    page_body, entries = searchindex.build("".join(body))
    page = fmt_page(title=esc(lesson["title"]), site=SITE,
                       desc=esc_attr(lesson.get("summary", "")), root="", lid=lid,
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
                '<a href="index.html">← 返回目录</a></div>')
    page_body, entries = searchindex.build("".join(body))
    page = fmt_page(title=esc(doc["title"]), site=SITE,
                       desc=esc_attr(doc.get("desc", "")), root="", lid=doc["file"],
                       crumb="题解", total="", mark="", body=page_body, nav="")
    with open(os.path.join(outdir, doc["file"]), "w", encoding="utf-8") as f:
        f.write(page)
    return doc_entry(doc["file"], doc["title"], doc.get("level", ""), "题解",
                     [doc.get("source", "")], entries)

