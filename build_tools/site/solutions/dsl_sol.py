# -*- coding: utf-8 -*-
"""题解用 DSL：在课程 DSL 之上，加一个 DOC 描述整份题解文档。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dsl import *  # noqa: F401,F403


def DOC(title, file, desc, source, level, sections=None, problems=None, skip=None):
    """一份题解文档。

    title   文档标题（如「2025 新生赛初赛 题解」）
    file    输出文件名（如 "sol-xinsheng.html"）
    desc    一句话说明
    source  题目来源
    level   整体难度标签
    sections 文档开头的说明块（用 P/T/L/NOTE 等）
    problems [PROB(...)] 列表
    skip    跳过的题号与理由（字符串列表）
    """
    return dict(title=title, file=file, desc=desc, source=source, level=level,
                sections=sections or [], problems=problems or [], skip=skip or [])


def PROB(letter, name, diff, tag, statement=None, difficulty_note=None,
         hint=None, idea=None, code=None, explain=None, pitfalls=None):
    """一道题的题解。

    letter   题号（A/B/C…）
    name     题名
    diff     难度标签（入门/普及-/普及/提高- 等）
    tag      核心考点，一句话
    statement 题意复述（list of blocks）
    hint     [str] 引导性提示
    idea     [str] 思路（可剧透）
    code     参考代码（C++17）
    explain  [(片段, 作用)]
    pitfalls [str] 易错点
    """
    return dict(letter=letter, name=name, diff=diff, tag=tag,
                statement=[P(x) if isinstance(x, str) else x for x in (statement or [])],
                difficulty_note=difficulty_note, hint=hint or [], idea=idea or [],
                code=code, explain=explain or [], pitfalls=pitfalls or [])
