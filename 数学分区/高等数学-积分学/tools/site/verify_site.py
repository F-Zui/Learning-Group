# -*- coding: utf-8 -*-
"""全站自检：文件齐全、单节规范、链接可达、目录数据一致。"""
import importlib.util
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from curriculum import CHAPTERS, all_sections  # noqa: E402

spec = importlib.util.spec_from_file_location("check", os.path.join(HERE, "check.py"))
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def main():
    missing, failed, warns, ok = [], [], [], 0
    for ch, sid, title, core, diff in all_sections():
        path = os.path.join(ROOT, "sections", sid.replace(".", "-") + ".html")
        if not os.path.exists(path):
            missing.append(sid)
            continue
        e, w = check.check(path)
        if e:
            failed.append((sid, e))
        else:
            ok += 1
        warns.extend((sid, x) for x in w)

    toc = open(os.path.join(ROOT, "assets", "toc.js"), encoding="utf-8").read()
    toc_ids = set(re.findall(r'"id": "([\d.]+)"', toc))
    cur_ids = {sid for _, sid, _, _, _ in all_sections()}
    toc_bad = toc_ids ^ cur_ids

    idx = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    idx_cards = set(re.findall(r'data-sec-card="([\d.]+)"', idx))
    card_bad = idx_cards ^ cur_ids

    print(f"节数: {len(cur_ids)}  文件通过: {ok}  缺失: {len(missing)}  不合规: {len(failed)}")
    if missing:
        print("缺失:", " ".join(sorted(missing)))
    for sid, e in failed:
        print(f"FAIL {sid}")
        for x in e:
            print("   x", x)
    if toc_bad:
        print("toc.js 与课程数据不一致:", sorted(toc_bad))
    if card_bad:
        print("index.html 卡片与课程数据不一致:", sorted(card_bad))
    real_warns = [w for w in warns if "链接目标尚不存在" not in w[1]]
    if real_warns:
        print("\n提示:")
        for sid, w in real_warns[:40]:
            print(f"  {sid}  {w}")

    bad = bool(missing or failed or toc_bad or card_bad)
    print("\n" + ("SITE OK" if not bad else "SITE HAS ISSUES"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
