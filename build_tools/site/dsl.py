# -*- coding: utf-8 -*-
"""课程内容的极简 DSL。

子代理写课时只需 import 本文件的短函数，返回 dict 列表即可，无需记忆 JSON 结构。

    from dsl import *
    sections = [
        P("读入两个整数，输出它们的和。"),
        EX("求两数之和", "P1001", "入门", "https://www.luogu.com.cn/problem/P1001",
           ["输入两个整数 a、b。"]),
        C("int a, b;\\ncin >> a >> b;\\ncout << a + b;"),
        NOTE("warn", "注意", ["不要输出提示语。"]),
    ]
"""


# ------------------------------------------------------------------ 正文块
def P(text):
    return {"kind": "p", "text": text}


def Q(text):
    return {"kind": "quote", "text": text}


def L(items, ordered=False):
    return {"kind": "list", "ordered": ordered, "items": items}


def T(head, rows):
    return {"kind": "table", "head": head, "rows": rows}


def NOTE(level, title, lines):
    return {"kind": "note", "level": level, "title": title, "lines": lines}


TIP = lambda title, lines: NOTE("tip", title, lines)
WARN = lambda title, lines: NOTE("warn", title, lines)
OK = lambda title, lines: NOTE("ok", title, lines)
INFO = lambda title, lines: NOTE("info", title, lines)


def C(code, caption=None):
    return {"kind": "code", "code": code, "caption": caption}


def EX(name, pid, diff, link, statement, oj="洛谷", sample=None):
    return {"kind": "example",
            "problem": {"name": name, "id": pid, "diff": diff, "link": link,
                        "oj": oj, "sample": sample},
            "statement": [P(it) if isinstance(it, str) else it for it in statement]}


def IDEA(title, blocks):
    return {"kind": "idea", "title": title,
            "blocks": [P(b) if isinstance(b, str) else b for b in blocks]}


def AFTER(title, blocks):
    return IDEA(title, blocks)


def EXPLAIN(title, rows):
    """rows: [(代码片段, 含义)]"""
    return {"kind": "explain", "title": title, "rows": rows}


def FN(name, signature, proto, example, notes=None, brief=""):
    """新函数拆解卡。
    proto: [(组成部分, 含义/格式要求)]
    """
    return {"kind": "func", "name": name, "signature": signature, "proto": proto,
            "example": example, "notes": notes or [], "brief": brief}


def REPRO(*lines):
    return {"kind": "reproduce", "lines": list(lines)}


# ------------------------------------------------------------------ 顶层
def CH(name, pid, diff, link, statement, hint, idea, code, explain=None, pitfalls=None,
       oj="洛谷", sample=None):
    return {"name": name, "oj": oj, "id": pid, "diff": diff, "link": link,
            "statement": [P(it) if isinstance(it, str) else it for it in statement],
            "hint": hint, "idea": idea, "code": code,
            "explain": explain or [], "pitfalls": pitfalls or [],
            "sample": sample}


def MATH(title, blocks):
    return {"title": title, "body": [P(b) if isinstance(b, str) else b for b in blocks]}


def LESSON(lid, title, summary, minutes, tags, level, sections,
           star=False, math=None, think=None, check=None, challenge=None, refs=None,
           challenge2=None):
    return dict(id=lid, title=title, summary=summary, minutes=minutes, tags=tags,
                level=level, sections=sections, star=star, math=math,
                think=think or [], check=check or [], challenge=challenge,
                challenge2=challenge2, refs=refs or [])
