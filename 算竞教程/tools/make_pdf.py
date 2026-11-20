# -*- coding: utf-8 -*-
"""把 板子.html 打成 PDF，并给目录补上真实页码。

版式是连续排版（不按节强制换页），所以页码用「前缀测量」得到：
渲染「目录 + 前 k 节」并数页数 P(k)，那么第 k+1 节就起在页 P(k) 上。
目录里始终留 3 位占位数字，测量与正式版版式一致，页码不会漂。

用法：python tools/make_pdf.py
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PY = sys.executable


def pdf_pages(path):
    b = open(path, "rb").read()
    return len(re.findall(rb"/Type\s*/Page[^s]", b))


def to_pdf(html_path, pdf_path):
    tmp = tempfile.mkdtemp()
    cmd = [EDGE, "--headless=new", "--disable-gpu", "--no-first-run",
           "--user-data-dir=" + tmp, "--no-pdf-header-footer",
           "--virtual-time-budget=1500",
           "--print-to-pdf=" + pdf_path,
           "file:///" + html_path.replace("\\", "/")]
    subprocess.run(cmd, capture_output=True, timeout=120)
    return pdf_pages(pdf_path)


def gen(args):
    r = subprocess.run([PY, "-X", "utf8", os.path.join(HERE, "cheatsheet.py")] + args,
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise SystemExit("生成失败：%s\n%s" % (r.stdout, r.stderr))
    return r.stdout.strip()


def stamp_pages(path):
    """在每页底部居中压上页码（不影响分页，目录里的页码仍然对得上）。"""
    import pymupdf
    doc = pymupdf.open(path)
    total = doc.page_count
    for i, page in enumerate(doc, 1):
        w, h = page.rect.width, page.rect.height
        label = "%d / %d" % (i, total)
        fs = 8.5
        tw = pymupdf.get_text_length(label, fontname="helv", fontsize=fs)
        page.insert_text((w / 2 - tw / 2, h - 18), label,
                         fontname="helv", fontsize=fs, color=(0.45, 0.45, 0.45))
    doc.saveIncr() if False else doc.save(path + ".tmp", deflate=True, garbage=3)
    doc.close()
    os.replace(path + ".tmp", path)
    return total


def main():
    sys.path.insert(0, HERE)
    import cheatsheet

    lessons = cheatsheet.collect()
    n = len(lessons)
    tmp = tempfile.mkdtemp()
    print("共 %d 节" % n)

    # 前缀测量：P(k) = 目录 + 前 k 节的页数
    def measure(k):
        html = os.path.join(tmp, "pref%02d.html" % k)
        gen(["--upto", str(k), "--out", html])
        return to_pdf(html, os.path.join(tmp, "pref%02d.pdf" % k))

    with ThreadPoolExecutor(max_workers=4) as ex:
        pref = list(ex.map(measure, range(0, n + 1)))
    print("前缀页数：", pref[:8], "… 总 %d" % pref[-1])

    # 第 i 节（1-based）起始页 = 前缀 i-1 的页数 + 1（若该页已写过内容则同页，取前缀页数）
    pages = {}
    for idx, (lid, _, _) in enumerate(lessons):
        prev = pref[idx]                    # 前 idx 节的页数
        pages[str(lid)] = prev
    json.dump(pages, open(os.path.join(tmp, "pages.json"), "w", encoding="utf-8"), ensure_ascii=False)

    out_html = os.path.join(tmp, "final.html")
    gen(["--pages", os.path.join(tmp, "pages.json"), "--out", out_html])
    final = os.path.join(ROOT, "板子.pdf")
    got = to_pdf(out_html, final)
    print("实际 PDF 页数：", got, "| 预测：", pref[-1])
    if got != pref[-1]:
        print("⚠ 页数不一致，页码可能偏移")
    n = stamp_pages(final)
    print("已压页码：%d 页" % n)
    print("PDF：", final, "%.1f MB" % (os.path.getsize(final) / 1048576.0))


if __name__ == "__main__":
    main()
