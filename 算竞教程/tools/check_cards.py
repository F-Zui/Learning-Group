# -*- coding: utf-8 -*-
"""两种卡自检：推导卡（DERIVE）与算法落地卡（WALK）。

用法：
    python check_cards.py 1 2 3 ...    # 检查指定节
    python check_cards.py              # 检查全部节

检查项（每一节）：
  1. 至少一张推导卡（kind == "derive"），且四段齐全：问题 / 2~4 步 / 落定理；
  2. 至少一张算法落地卡（kind == "walk"），且 req 第一段带题目身份（外链 + 难度徽标）、
     3~5 步、每步配代码、有竞赛用法；
  3. 落地卡里保留了一份完整可编译程序（含 #include 与 int main）；
  4. 不再残留旧组件：FN（kind == "func"）与例题（kind == "example"）。

回顾章 / 模拟赛（curriculum 里 kind 为 review / mock）不需要两种卡，直接跳过。
任何一项不通过就以非零码退出。
"""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import curriculum            # noqa: E402


def load_lesson(lid):
    modname = "lessons.l%02d" % lid
    mod = importlib.import_module(modname)
    items = getattr(mod, "LESSONS", None) or []
    for it in items:
        if int(it.get("id", -1)) == lid:
            return it
    return items[0] if items else None


def walk_blocks(blocks):
    """把一个 blocks 列表里所有 dict 块摊平（含 steps 里的嵌套 blocks）。"""
    out = []
    for b in blocks or []:
        if isinstance(b, dict):
            out.append(b)
    return out


def codes_in(blocks):
    return [b for b in walk_blocks(blocks) if b.get("kind") == "code"]


def codes_of_card(card):
    """推导卡 / 落地卡里全部代码块：req、steps 的正文与「为什么」、oi。"""
    out = []
    for key in ("req", "problem", "end", "oi"):
        out.extend(codes_in(card.get(key)))
    for st in card.get("steps") or []:
        if not isinstance(st, (tuple, list)):
            continue
        for part in st[1:3]:
            out.extend(codes_in(part))
    return out


def has_full_program(card):
    for c in codes_of_card(card):
        code = str(c.get("code") or "")
        if "#include" in code and "int main" in code:
            return True
    return False


def check_derive(card):
    bad = []
    if not card.get("problem"):
        bad.append("缺「问题」段")
    steps = card.get("steps") or []
    if not (2 <= len(steps) <= 4):
        bad.append("步数为 %d，要求 2~4 步" % len(steps))
    for i, st in enumerate(steps, 1):
        if not isinstance(st, (tuple, list)) or len(st) < 2 or not st[0]:
            bad.append("第 %d 步格式不对（应为 (小标题, [blocks], [验证]?)）" % i)
    if not card.get("end"):
        bad.append("缺「落定理」段")
    if not card.get("cover"):
        bad.append("缺 cover（覆盖范围）")
    return bad


def check_walk(card):
    bad = []
    req = card.get("req") or []
    head = req[0] if req else None
    txt = ""
    if isinstance(head, dict):
        txt = str(head.get("text") or "")
    elif isinstance(head, str):
        txt = head
    if not txt:
        bad.append("req 缺第一段题目身份")
    else:
        if "http" not in txt:
            bad.append("req 第一段没有题号外链")
        if "badge diff" not in txt:
            bad.append("req 第一段没有难度徽标")
    steps = card.get("steps") or []
    if not (3 <= len(steps) <= 5):
        bad.append("步数为 %d，要求 3~5 步" % len(steps))
    for i, st in enumerate(steps, 1):
        if not isinstance(st, (tuple, list)) or len(st) < 2 or not st[0]:
            bad.append("第 %d 步格式不对（应为 (小标题, [blocks], [为什么])）" % i)
            continue
        if not codes_in(st[1] if len(st) > 1 else []):
            bad.append("第 %d 步没有配代码" % i)
        if len(st) < 3 or not st[2]:
            bad.append("第 %d 步缺「为什么」" % i)
    if not card.get("oi"):
        bad.append("缺「竞赛用法」段")
    tags = card.get("tags") or []
    if not (2 <= len(tags) <= 4):
        bad.append("tags 有 %d 个，要求 2~4 个" % len(tags))
    if not card.get("cover"):
        bad.append("缺 cover（覆盖范围）")
    if not has_full_program(card):
        bad.append("没有保留完整可编译程序（#include + int main）")
    return bad


def collect(blocks):
    out = []
    for b in blocks or []:
        if isinstance(b, dict):
            out.append(b)
    return out


def check_lesson(lid):
    try:
        lesson = load_lesson(lid)
    except Exception as e:                                  # noqa: BLE001
        return ["载入失败：%s" % e]
    if lesson is None:
        return ["载入失败：LESSONS 里没有 id=%d" % lid]

    sections = lesson.get("sections") or []
    derives = [b for b in collect(sections) if b.get("kind") == "derive"]
    walks = [b for b in collect(sections) if b.get("kind") == "walk"]
    funcs = [b for b in collect(sections) if b.get("kind") == "func"]
    examples = [b for b in collect(sections) if b.get("kind") == "example"]

    bad = []
    if not derives:
        bad.append("没有推导卡（DERIVE）")
    else:
        for i, d in enumerate(derives, 1):
            for msg in check_derive(d):
                bad.append("推导卡 %d「%s」：%s" % (i, d.get("title", ""), msg))
    if not walks:
        bad.append("没有算法落地卡（WALK）")
    else:
        for i, w in enumerate(walks, 1):
            for msg in check_walk(w):
                bad.append("落地卡 %d「%s」：%s" % (i, w.get("title", ""), msg))
    if funcs:
        bad.append("残留 %d 张 FN（新函数拆解）" % len(funcs))
    if examples:
        bad.append("残留 %d 张 EX（例题）" % len(examples))
    return bad


def main():
    ids = [int(x) for x in sys.argv[1:]]
    if not ids:
        ids = list(range(1, 61))

    skipped, failed, passed = [], 0, 0
    for lid in ids:
        try:
            kind = curriculum.meta(lid)["kind"]
        except Exception:                                   # noqa: BLE001
            kind = "lesson"
        if kind in ("review", "mock"):
            skipped.append(lid)
            continue
        bad = check_lesson(lid)
        if bad:
            failed += 1
            print("[%02d] ✗" % lid)
            for msg in bad:
                print("      - %s" % msg)
        else:
            passed += 1
            lesson = load_lesson(lid)
            ds = [b for b in lesson["sections"] if b.get("kind") == "derive"]
            ws = [b for b in lesson["sections"] if b.get("kind") == "walk"]
            print("[%02d] ✓ %s ｜ 推导卡 %d ｜ 落地卡 %d "
                  % (lid, lesson.get("title", ""), len(ds), len(ws)))

    if skipped:
        print("跳过回顾章 / 模拟赛：%s" % " ".join("%02d" % i for i in skipped))
    print("\n通过 %d / 失败 %d%s"
          % (passed, failed, ("，跳过 %d" % len(skipped)) if skipped else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
