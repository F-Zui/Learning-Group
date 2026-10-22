# -*- coding: utf-8 -*-
"""
build_docx.py —— 零依赖 Markdown -> Word(.docx) 构建器
仅使用 Python 标准库 (zipfile + 手写 OOXML)。

支持的源文件语法
----------------
# / ## / ### / ####        一~四级标题 (映射到 Word 内置 Heading1~4，可生成目录)
**粗体**                   加粗
==高亮==                   加粗 + 黄色底纹（用于关键公式结论）
$行内公式$                 使用 Cambria Math 字体的数学文本
`代码`                     等宽字体
$$ 行间公式 $$             居中显示的公式段落
- 项目                     无序列表
1. 项目                    有序列表（十进制）
   I. 子项                 有序列表（大写罗马数字，二级）
| a | b |                  管道表格（第二行为 |---| 分隔）
> 引用                     浅灰引用块
:::难点 标题               醒目提示框（kind 可取：难点 / 易错 / 例题 / 练习 / 提示）
...
:::
---                        分隔线
[[TOC]]                    目录域
"""

import os
import re
import sys
import zipfile
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import omml  # noqa: E402  公式 -> OMML 转换器

# ---------------------------------------------------------------- 主题配色
BOX_THEME = {
    "难点": ("FFF1F1", "C00000", "8B1A1A"),
    "易错": ("FFF8E6", "BF8F00", "7F5F00"),
    "例题": ("F2F5FA", "2E5C8A", "1F3F63"),
    "练习": ("F2F7F2", "3C7A3C", "245224"),
    "提示": ("F0F4F8", "4472C4", "2C4C82"),
    "答案": ("F5F5F5", "808080", "404040"),
}
DEFAULT_BOX = ("F5F5F5", "A6A6A6", "595959")

CN_BODY = "宋体"
CN_HEAD = "黑体"
EN_BODY = "Times New Roman"
MATH_FONT = "Cambria Math"
MONO = "Consolas"

W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'


# ---------------------------------------------------------------- 工具函数
def esc(t: str) -> str:
    return escape(t)


def run(text, bold=False, italic=False, font=None, color=None,
        highlight=False, sz=None, mono=False):
    """构造一个 <w:r>。text 需已转义。"""
    rpr = []
    if mono:
        rpr.append(f'<w:rFonts w:ascii="{MONO}" w:hAnsi="{MONO}" w:eastAsia="{CN_BODY}"/>')
    elif font:
        rpr.append(f'<w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:eastAsia="{CN_BODY}"/>')
    if bold:
        rpr.append('<w:b/><w:bCs/>')
    if italic:
        rpr.append('<w:i/><w:iCs/>')
    if color:
        rpr.append(f'<w:color w:val="{color}"/>')
    if highlight:
        rpr.append('<w:shd w:val="clear" w:color="auto" w:fill="FFF2A8"/>')
    if sz:
        rpr.append(f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>')
    rpr_xml = f'<w:rPr>{"".join(rpr)}</w:rPr>' if rpr else ""
    return f'<w:r>{rpr_xml}<w:t xml:space="preserve">{text}</w:t></w:r>'


INLINE_RE = re.compile(r"\*\*.+?\*\*|==.+?==|\$[^$]+?\$|`[^`]+?`", re.S)


def _tokenize(text, attrs=None):
    """把行内文本递归拆成 [(纯文本, 属性字典)]，支持标记嵌套。"""
    attrs = attrs or {}
    out = []
    pos = 0
    for m in INLINE_RE.finditer(text):
        if m.start() > pos:
            out.append((text[pos:m.start()], attrs))
        tok = m.group(0)
        if tok.startswith("**"):
            out.extend(_tokenize(tok[2:-2], dict(attrs, bold=True)))
        elif tok.startswith("=="):
            out.extend(_tokenize(tok[2:-2], dict(attrs, bold=True, highlight=True)))
        elif tok.startswith("$"):
            out.append((tok[1:-1], dict(attrs, math=True)))
        elif tok.startswith("`"):
            out.append((tok[1:-1], dict(attrs, mono=True)))
        pos = m.end()
    if pos < len(text):
        out.append((text[pos:], attrs))
    return out


def inline(text, base=None):
    """把一行 Markdown 行内语法转为若干 <w:r>（公式转为 OMML 公式对象）。"""
    runs = []
    for t, a in _tokenize(text, base):
        if not t:
            continue
        if a.get("math"):
            runs.append(omml.omath(t, highlight=a.get("highlight", False)))
            continue
        runs.append(run(
            esc(t),
            bold=a.get("bold", False),
            italic=False,
            font=None,
            highlight=a.get("highlight", False),
            mono=a.get("mono", False),
            color=a.get("color"),
        ))
    if not runs:
        runs.append(run(""))
    return "".join(runs)


def para(runs_xml, style=None, align=None, ind=None, spacing=None,
         shade=None, border_left=None, keep_next=False, border_box=None,
         outline_lvl=None):
    ppr = []
    if style:
        ppr.append(f'<w:pStyle w:val="{style}"/>')
    if keep_next:
        ppr.append('<w:keepNext/>')
    if border_box:
        ppr.append(border_box)
    if border_left:
        ppr.append(border_left)
    if shade:
        ppr.append(f'<w:shd w:val="clear" w:color="auto" w:fill="{shade}"/>')
    if spacing:
        ppr.append(spacing)
    if ind:
        ppr.append(ind)
    if align:
        ppr.append(f'<w:jc w:val="{align}"/>')
    if outline_lvl is not None:
        ppr.append(f'<w:outlineLvl w:val="{outline_lvl}"/>')
    ppr_xml = f'<w:pPr>{"".join(ppr)}</w:pPr>' if ppr else ""
    return f"<w:p>{ppr_xml}{runs_xml}</w:p>"


def box_border_left(color, sz=24):
    return (f'<w:pBdr><w:left w:val="single" w:sz="{sz}" w:space="8" '
            f'w:color="{color}"/></w:pBdr>')


def box_border_all(color, sz=6):
    return (f'<w:pBdr>'
            f'<w:top w:val="single" w:sz="{sz}" w:space="4" w:color="{color}"/>'
            f'<w:left w:val="single" w:sz="{sz}" w:space="4" w:color="{color}"/>'
            f'<w:bottom w:val="single" w:sz="{sz}" w:space="4" w:color="{color}"/>'
            f'<w:right w:val="single" w:sz="{sz}" w:space="4" w:color="{color}"/>'
            f'</w:pBdr>')


# ---------------------------------------------------------------- 插图支持
FIG_META = {}        # figid -> (编号, 题注)
FIG_USED = []        # 按出现顺序记录用到的 figid
FIG_DIR = ""

EMU_PER_PX = 9525            # 96 dpi
MAX_IMG_EMU = 5620000        # 正文可用宽度（约 15.6 cm）


def load_figures(md_path):
    """读取 figures/index.txt 中的图号与题注。"""
    global FIG_DIR
    base = os.path.dirname(os.path.abspath(md_path))
    for cand in (os.path.join(base, "figures"),
                 os.path.join(base, os.pardir, "figures")):
        if os.path.isfile(os.path.join(cand, "index.txt")):
            FIG_DIR = os.path.abspath(cand)
            break
    else:
        return
    with open(os.path.join(FIG_DIR, "index.txt"), encoding="utf-8-sig") as f:
        for line in f:
            parts = line.strip().split("|")
            if len(parts) == 3:
                FIG_META[parts[0]] = (parts[1], parts[2])


def png_size(path):
    """从 PNG 的 IHDR 块读出像素宽高。"""
    with open(path, "rb") as f:
        head = f.read(26)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return 0, 0
    w = int.from_bytes(head[16:20], "big")
    h = int.from_bytes(head[20:24], "big")
    return w, h


def figure_rid(figid):
    """登记图片并返回其 rId。"""
    if figid not in FIG_USED:
        FIG_USED.append(figid)
    return "rId%d" % (500 + FIG_USED.index(figid))


def drawing_xml(figid, rid, docid):
    """生成内嵌图片的 w:drawing。"""
    src = os.path.join(FIG_DIR, figid + ".png")
    w, h = png_size(src)
    if w <= 0:
        return ""
    scale = min(1.0, float(MAX_IMG_EMU) / (w * EMU_PER_PX))
    cx, cy = int(w * EMU_PER_PX * scale), int(h * EMU_PER_PX * scale)
    A = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
    PIC = 'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"'
    return (
        '<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
        '<wp:extent cx="%d" cy="%d"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
        '<wp:docPr id="%d" name="Picture%d"/>'
        '<wp:cNvGraphicFramePr><a:graphicFrameLocks %s noChangeAspect="1"/></wp:cNvGraphicFramePr>'
        '<a:graphic %s><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:pic %s><pic:nvPicPr><pic:cNvPr id="%d" name="%s.png"/><pic:cNvPicPr/></pic:nvPicPr>'
        '<pic:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
        '</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>'
        % (cx, cy, docid, docid, A, A, PIC, docid, figid, rid, cx, cy))


def figure_block(figid, shade=None, border=None, ind=None):
    """返回 (图片段落, 题注段落) 的 XML 列表。"""
    num, cap = FIG_META.get(figid, ("?", figid))
    if figid not in FIG_USED:
        FIG_USED.append(figid)
    docid = 1000 + FIG_USED.index(figid)
    rid = figure_rid(figid)
    img = para(drawing_xml(figid, rid, docid), align="center",
               spacing='<w:spacing w:before="200" w:after="60"/>',
               shade=shade, border_left=border, ind=ind)
    cap_xml = para(run(esc("图 %s　%s" % (num, cap)), sz=19, color="595959"),
                   align="center",
                   spacing='<w:spacing w:before="0" w:after="240"/>',
                   shade=shade, border_left=border, ind=ind)
    return img, cap_xml


# ---------------------------------------------------------------- 解析器
def display_para(expr, shade=None, border=None, spacing=None, ind=None):
    """生成行间公式段落（居中，且保留段落边框）。"""
    return para(omml.omath(expr, display=True), align="center", shade=shade,
                border_left=border, spacing=spacing, ind=ind)


def parse(md_text):
    """Markdown -> 段落 XML 列表。"""
    lines = md_text.split("\n")
    body = []
    i = 0
    n = len(lines)

    while i < n:
        raw = lines[i]
        line = raw.rstrip()
        stripped = line.strip()

        # ---- 空行 / 构建期注释 / 游离的框结束标记
        if not stripped or stripped.startswith("<!--") or stripped == ":::":
            i += 1
            continue

        # ---- 分隔线
        if re.fullmatch(r"-{3,}", stripped):
            body.append(para("", spacing='<w:spacing w:before="120" w:after="120"/>',
                             border_box='<w:pBdr><w:bottom w:val="single" w:sz="6" '
                                        'w:space="1" w:color="BFBFBF"/></w:pBdr>'))
            i += 1
            continue

        # ---- 目录域
        if stripped == "[[TOC]]":
            body.append(
                '<w:p><w:pPr><w:spacing w:after="240"/></w:pPr>'
                '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
                '<w:r><w:instrText xml:space="preserve"> TOC \\o "1-3" \\h \\z \\u </w:instrText></w:r>'
                '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
                '<w:r><w:rPr><w:i/><w:color w:val="808080"/></w:rPr>'
                '<w:t>（目录域：在 Word 中按 Ctrl+A 后按 F9 即可生成／更新目录）</w:t></w:r>'
                '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>')
            i += 1
            continue

        # ---- 插图：![[fig1_1_1]]
        m = re.match(r"^!\[\[([A-Za-z0-9_]+)\]\]$", stripped)
        if m:
            img, cap = figure_block(m.group(1))
            body.append(img)
            body.append(cap)
            i += 1
            continue

        # ---- 提示框
        m = re.match(r"^:::\s*(\S+)\s*(.*)$", stripped)
        if m and m.group(1) not in ("::",):
            kind = m.group(1)
            title = m.group(2).strip()
            fill, bar, tcolor = BOX_THEME.get(kind, DEFAULT_BOX)
            buf = []
            i += 1
            while i < n and lines[i].strip() != ":::":
                buf.append(lines[i])
                i += 1
            i += 1  # 跳过 :::

            IND = '<w:ind w:left="200" w:right="120"/>'
            first = True
            if title:
                body.append(para(
                    run(f"【{kind}】", bold=True, color=tcolor)
                    + inline(title, {"bold": True, "color": tcolor}),
                    shade=fill, border_left=box_border_left(bar),
                    spacing='<w:spacing w:before="160" w:after="40"/>',
                    ind=IND, keep_next=True))
                first = False
            j = 0
            nb = len(buf)
            while j < nb:
                bs = buf[j].strip()
                if not bs:
                    j += 1
                    continue
                if first:
                    bs = f"**【{kind}】**{bs}"
                    sp = '<w:spacing w:before="160" w:after="40"/>'
                    first = False
                else:
                    sp = '<w:spacing w:before="40" w:after="40"/>'
                # 框内的插图与表格需单独处理
                m2 = re.match(r"^!\[\[([A-Za-z0-9_]+)\]\]$", bs)
                if m2:
                    img, capx = figure_block(m2.group(1), shade=fill,
                                             border=box_border_left(bar), ind=IND)
                    body.append(img)
                    body.append(capx)
                    j += 1
                    continue
                # 框内的表格需单独处理，否则管道符会原样漏出
                if (bs.startswith("|") and j + 1 < nb
                        and re.match(r"^\|[\s:|-]+\|$", buf[j + 1].strip())):
                    thead = split_row(bs)
                    j += 2
                    trows = []
                    while j < nb and buf[j].strip().startswith("|"):
                        trows.append(split_row(buf[j].strip()))
                        j += 1
                    body.append(make_table(thead, trows, fill=fill))
                    continue
                # 框内的行间公式需单独处理，否则会被行内规则拆坏
                if bs.startswith("$$") and bs.endswith("$$") and len(bs) > 4:
                    body.append(display_para(
                        bs[2:-2].strip(), shade=fill,
                        border=box_border_left(bar), spacing=sp, ind=IND))
                    j += 1
                    continue
                body.append(para(inline(bs), shade=fill,
                                 border_left=box_border_left(bar), spacing=sp, ind=IND))
                j += 1
            # 收尾：闭合色块底部
            body.append(para("", shade=fill,
                             spacing='<w:spacing w:before="0" w:after="160" w:line="40" w:lineRule="exact"/>',
                             ind=IND))
            continue

        # ---- 表格
        if stripped.startswith("|") and i + 1 < n and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            header = split_row(stripped)
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i].strip()))
                i += 1
            body.append(make_table(header, rows))
            continue

        # ---- 标题
        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            lvl = len(m.group(1))
            body.append(para(inline(m.group(2)), style=f"Heading{lvl}"))
            i += 1
            continue

        # ---- 行间公式（Word 公式对象，居中）
        if stripped.startswith("$$") and stripped.endswith("$$") and len(stripped) > 4:
            expr = stripped[2:-2].strip()
            body.append(display_para(expr,
                                     spacing='<w:spacing w:before="120" w:after="120"/>'))
            i += 1
            continue

        # ---- 引用
        if stripped.startswith(">"):
            body.append(para(inline(stripped.lstrip("> ").strip()),
                             shade="F7F7F7", border_left=box_border_left("BFBFBF", 18),
                             ind='<w:ind w:left="200" w:right="120"/>',
                             spacing='<w:spacing w:before="60" w:after="60"/>'))
            i += 1
            continue

        # ---- 无序列表
        m = re.match(r"^(\s*)[-*]\s+(.*)$", line)
        if m:
            lvl = 0 if len(m.group(1)) < 2 else 1
            body.append(para(inline(m.group(2)),
                             ind=f'<w:ind w:left="{420 + 340 * lvl}" w:hanging="240"/>',
                             spacing='<w:spacing w:before="20" w:after="20"/>',
                             ))
            body[-1] = body[-1].replace("<w:pPr>", '<w:pPr><w:numPr><w:ilvl w:val="%d"/><w:numId w:val="2"/></w:numPr>' % lvl, 1)
            i += 1
            continue

        # ---- 有序列表：1. / I.（字面编号 + 制表符对齐，编号稳定、不被 Word 重排）
        m = re.match(r"^(\s*)(\d+|[IVX]{1,5})[.)]\s+(.*)$", line)
        if m:
            indent, marker, content = m.group(1), m.group(2), m.group(3)
            lvl = 0 if len(indent) < 2 else 1
            left = 420 * (lvl + 1)
            runs = (run(esc(marker) + ".", bold=(lvl == 1))
                    + '<w:r><w:tab/></w:r>'
                    + inline(content))
            body.append(para(runs,
                             ind=f'<w:ind w:left="{left}" w:hanging="420"/>',
                             spacing='<w:spacing w:before="30" w:after="30"/>'))
            i += 1
            continue

        # ---- 普通段落
        body.append(para(inline(stripped),
                         spacing='<w:spacing w:before="40" w:after="40" w:line="300" w:lineRule="auto"/>',
                         ind='<w:ind w:firstLine="0"/>'))
        i += 1

    return body


def make_table(header, rows, fill=None):
    SP = '<w:spacing w:before="40" w:after="40"/>'
    hfill = fill or "EDEDED"

    def cell(text, bold=False, width=0, cell_fill=None):
        w = f'<w:tcW w:w="{width}" w:type="dxa"/>' if width else ""
        shd = f'<w:shd w:val="clear" w:color="auto" w:fill="{cell_fill}"/>' if cell_fill else ""
        runs = inline(text, {"bold": True}) if bold else inline(text)
        return ('<w:tc><w:tcPr>' + w + shd + '<w:vAlign w:val="center"/></w:tcPr>'
                + para(runs, spacing=SP) + '</w:tc>')

    # 等宽列
    total = 9360
    ncol = max(1, len(header))
    cw = total // ncol

    borders = ('<w:tblBorders>'
               '<w:top w:val="single" w:sz="6" w:color="808080"/>'
               '<w:left w:val="single" w:sz="6" w:color="808080"/>'
               '<w:bottom w:val="single" w:sz="6" w:color="808080"/>'
               '<w:right w:val="single" w:sz="6" w:color="808080"/>'
               '<w:insideH w:val="single" w:sz="4" w:color="BFBFBF"/>'
               '<w:insideV w:val="single" w:sz="4" w:color="BFBFBF"/>'
               '</w:tblBorders>')

    xml = ['<w:tbl><w:tblPr>',
           f'<w:tblW w:w="{total}" w:type="dxa"/>{borders}',
           '<w:tblLayout w:type="fixed"/>',
           '</w:tblPr><w:tblGrid>',
           "".join(f'<w:gridCol w:w="{cw}"/>' for _ in range(ncol)),
           '</w:tblGrid>']

    xml.append('<w:tr><w:trPr><w:tblHeader/></w:trPr>')
    for c in header:
        xml.append(cell(c, bold=True, width=cw, cell_fill=hfill))
    xml.append('</w:tr>')

    for r in rows:
        xml.append('<w:tr>')
        for k in range(ncol):
            v = r[k] if k < len(r) else ""
            xml.append(cell(v, width=cw, cell_fill=fill))
        xml.append('</w:tr>')
    xml.append('</w:tbl>')
    xml.append(para("", spacing='<w:spacing w:after="120"/>'))
    return "".join(xml)


def strip_md(t):
    return re.sub(r"\*\*|==|`", "", t)


def split_row(line):
    """按 | 分列，支持用 \\| 转义数学中的绝对值符号。"""
    return [c.strip().replace("\x00", "|")
            for c in line.strip().strip("|").replace("\\|", "\x00").split("|")]


# ---------------------------------------------------------------- 静态部件
def styles_xml():
    def hstyle(sid, name, size, cn=CN_HEAD, color="1F3864", outline=0, before=280, after=120):
        return f'''<w:style w:type="paragraph" w:styleId="{sid}">
<w:name w:val="{name}"/><w:basedOn w:val="Normal"/><w:qFormat/>
<w:pPr><w:keepNext/><w:outlineLvl w:val="{outline}"/>
<w:spacing w:before="{before}" w:after="{after}" w:line="300" w:lineRule="auto"/></w:pPr>
<w:rPr><w:rFonts w:ascii="{EN_BODY}" w:hAnsi="{EN_BODY}" w:eastAsia="{cn}"/>
<w:b/><w:bCs/><w:color w:val="{color}"/><w:sz w:val="{size}"/><w:szCs w:val="{size}"/></w:rPr>
</w:style>'''

    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles {W}>
<w:docDefaults><w:rPrDefault><w:rPr>
<w:rFonts w:ascii="{EN_BODY}" w:hAnsi="{EN_BODY}" w:eastAsia="{CN_BODY}" w:cs="{EN_BODY}"/>
<w:sz w:val="21"/><w:szCs w:val="21"/>
<w:lang w:val="en-US" w:eastAsia="zh-CN" w:bidi="ar-SA"/>
</w:rPr></w:rPrDefault>
<w:pPrDefault><w:pPr>
<w:spacing w:before="40" w:after="40" w:line="300" w:lineRule="auto"/>
</w:pPr></w:pPrDefault></w:docDefaults>

<w:style w:type="paragraph" w:default="1" w:styleId="Normal">
<w:name w:val="Normal"/><w:qFormat/>
<w:pPr><w:spacing w:before="40" w:after="40" w:line="300" w:lineRule="auto"/></w:pPr>
<w:rPr><w:rFonts w:ascii="{EN_BODY}" w:hAnsi="{EN_BODY}" w:eastAsia="{CN_BODY}"/>
<w:sz w:val="21"/><w:szCs w:val="21"/></w:rPr>
</w:style>

{hstyle("Heading1", "heading 1", 36, color="1F3864", outline=0, before=360, after=200)}
{hstyle("Heading2", "heading 2", 28, color="2E5C8A", outline=1, before=320, after=140)}
{hstyle("Heading3", "heading 3", 24, color="2E5C8A", outline=2, before=240, after=120)}
{hstyle("Heading4", "heading 4", 21, color="404040", outline=3, before=200, after=100)}
</w:styles>'''


def numbering_xml():
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering {W}>
<w:abstractNum w:abstractNumId="0">
<w:multiLevelType w:val="multilevel"/>
<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/>
<w:lvlText w:val="%1."/><w:lvlJc w:val="left"/>
<w:pPr><w:ind w:left="420" w:hanging="420"/></w:pPr></w:lvl>
<w:lvl w:ilvl="1"><w:start w:val="1"/><w:numFmt w:val="upperRoman"/>
<w:lvlText w:val="%2."/><w:lvlJc w:val="left"/>
<w:pPr><w:ind w:left="900" w:hanging="420"/></w:pPr>
<w:rPr><w:b/></w:rPr></w:lvl>
</w:abstractNum>

<w:abstractNum w:abstractNumId="1">
<w:multiLevelType w:val="multilevel"/>
<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/>
<w:lvlText w:val="&#9679;"/><w:lvlJc w:val="left"/>
<w:pPr><w:ind w:left="420" w:hanging="240"/></w:pPr>
<w:rPr><w:rFonts w:ascii="Symbol" w:hAnsi="Symbol"/></w:rPr></w:lvl>
<w:lvl w:ilvl="1"><w:start w:val="1"/><w:numFmt w:val="bullet"/>
<w:lvlText w:val="&#9675;"/><w:lvlJc w:val="left"/>
<w:pPr><w:ind w:left="840" w:hanging="240"/></w:pPr></w:lvl>
</w:abstractNum>

<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>
<w:num w:numId="2"><w:abstractNumId w:val="1"/></w:num>
</w:numbering>'''


def settings_xml():
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings {W}>
<w:zoom w:percent="100"/>
<w:defaultTabStop w:val="420"/>
<w:updateFields w:val="true"/>
<w:compat><w:compatSetting w:name="compatibilityMode"
 xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
 w:uri="http://schemas.microsoft.com/office/word" w:val="15"/></w:compat>
</w:settings>'''


def footer_xml():
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr {W}>
<w:p><w:pPr><w:jc w:val="center"/></w:pPr>
<w:r><w:rPr><w:sz w:val="18"/><w:color w:val="808080"/></w:rPr>
<w:t xml:space="preserve">— </w:t></w:r>
<w:r><w:fldChar w:fldCharType="begin"/></w:r>
<w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>
<w:r><w:fldChar w:fldCharType="separate"/></w:r>
<w:r><w:rPr><w:sz w:val="18"/><w:color w:val="808080"/></w:rPr><w:t>1</w:t></w:r>
<w:r><w:fldChar w:fldCharType="end"/></w:r>
<w:r><w:rPr><w:sz w:val="18"/><w:color w:val="808080"/></w:rPr>
<w:t xml:space="preserve"> —</w:t></w:r>
</w:p></w:ftr>'''


CONTENT_TYPES = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>'''

ROOT_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''

DOC_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
<Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>
</Relationships>'''

SECT_PR = '''<w:sectPr>
<w:footerReference w:type="default" r:id="rId4"/>
<w:pgSz w:w="11906" w:h="16838"/>
<w:pgMar w:top="1440" w:right="1276" w:bottom="1440" w:left="1276" w:header="851" w:footer="992" w:gutter="0"/>
<w:cols w:space="425"/>
<w:docGrid w:type="lines" w:linePitch="312"/>
</w:sectPr>'''


def core_xml(title, author="高等数学课程组"):
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<dc:title>{esc(title)}</dc:title>
<dc:creator>{esc(author)}</dc:creator>
<cp:lastModifiedBy>{esc(author)}</cp:lastModifiedBy>
<dcterms:created xsi:type="dcterms:W3CDTF">2025-01-01T00:00:00Z</dcterms:created>
<dcterms:modified xsi:type="dcterms:W3CDTF">2025-01-01T00:00:00Z</dcterms:modified>
</cp:coreProperties>'''


def app_xml(title):
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
 xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
<Application>DSH Courseware Builder</Application>
<TitlesOfParts><vt:vector size="1" baseType="lpstr"><vt:lpstr>{esc(title)}</vt:lpstr></vt:vector></TitlesOfParts>
</Properties>'''


# ---------------------------------------------------------------- 主流程
def build(md_path, docx_path, title=None):
    with open(md_path, "r", encoding="utf-8-sig") as f:
        md = f.read()
    title = title or os.path.splitext(os.path.basename(md_path))[0]

    FIG_META.clear()
    del FIG_USED[:]
    load_figures(md_path)

    body = parse(md)
    document = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                f'<w:document {W} {omml.M_NS} '
                f'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
                f'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">'
                f'<w:body>{"".join(body)}{SECT_PR}</w:body></w:document>')

    # 图片关系与内容类型按实际用到的插图动态生成
    rels = DOC_RELS.replace("</Relationships>", "".join(
        '<Relationship Id="%s" Type="http://schemas.openxmlformats.org/'
        'officeDocument/2006/relationships/image" Target="media/%s.png"/>'
        % (figure_rid(fid), fid) for fid in FIG_USED) + "</Relationships>")
    ctypes = CONTENT_TYPES
    if FIG_USED:
        ctypes = ctypes.replace("<Default Extension=\"xml\"",
                                "<Default Extension=\"png\" ContentType=\"image/png\"/>\n"
                                "<Default Extension=\"xml\"")

    parts = {
        "[Content_Types].xml": ctypes,
        "_rels/.rels": ROOT_RELS,
        "word/document.xml": document,
        "word/_rels/document.xml.rels": rels,
        "word/styles.xml": styles_xml(),
        "word/numbering.xml": numbering_xml(),
        "word/settings.xml": settings_xml(),
        "word/footer1.xml": footer_xml(),
        "docProps/core.xml": core_xml(title),
        "docProps/app.xml": app_xml(title),
    }

    os.makedirs(os.path.dirname(os.path.abspath(docx_path)), exist_ok=True)
    with zipfile.ZipFile(docx_path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in parts.items():
            z.writestr(name, data.encode("utf-8"))
        for fid in FIG_USED:
            z.write(os.path.join(FIG_DIR, fid + ".png"), "word/media/%s.png" % fid)
    if FIG_USED:
        print("  已嵌入插图:", len(FIG_USED), "幅")
    if omml.ERRORS:
        print("  !! 公式降级为纯文本:", len(omml.ERRORS), "处")
        seen = set()
        for t, e in omml.ERRORS:
            if t in seen:
                continue
            seen.add(t)
            print("     ", t[:70], "->", e)
            if len(seen) >= 12:
                break
    return docx_path


if __name__ == "__main__":
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(src)[0] + ".docx"
    out = build(src, dst)
    print("OK ->", out, os.path.getsize(out), "bytes")
