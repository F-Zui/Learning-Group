# -*- coding: utf-8 -*-
"""极简 PDF 文本提取：解压 FlateDecode 流，抽取文本显示操作符。

只依赖标准库。适合提取由 LaTeX / Word 导出的文字型 PDF。
"""
import re
import sys
import zlib


def iter_streams(data):
    """遍历 PDF 中所有流对象，返回已解码的字节串。"""
    for m in re.finditer(rb"stream\r?\n", data):
        start = m.end()
        end = data.find(b"endstream", start)
        if end < 0:
            continue
        raw = data[start:end]
        raw = raw.rstrip(b"\r\n")
        try:
            yield zlib.decompress(raw)
        except zlib.error:
            # 未压缩或其它编码，直接返回原文（可能含二进制，交给调用方过滤）
            yield raw


def unescape_pdf_string(s):
    out = bytearray()
    i = 0
    n = len(s)
    while i < n:
        c = s[i:i + 1]
        if c == b"\\" and i + 1 < n:
            nxt = s[i + 1:i + 2]
            mapping = {b"n": b"\n", b"r": b"\r", b"t": b"\t", b"b": b"\b",
                       b"f": b"\f", b"(": b"(", b")": b")", b"\\": b"\\"}
            if nxt in mapping:
                out += mapping[nxt]
                i += 2
                continue
            if nxt.isdigit():                     # 八进制 \ddd
                j = i + 1
                oct_digits = b""
                while j < n and len(oct_digits) < 3 and s[j:j + 1].isdigit():
                    oct_digits += s[j:j + 1]
                    j += 1
                out.append(int(oct_digits, 8) & 0xFF)
                i = j
                continue
            i += 2
            continue
        out += c
        i += 1
    return bytes(out)


def decode_bytes(b):
    """PDF 里常见：UTF-16BE 带 BOM、或单字节。"""
    if b.startswith(b"\xfe\xff"):
        try:
            return b[2:].decode("utf-16-be", "ignore")
        except Exception:
            return ""
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("latin-1", "ignore")


TEXT_RE = re.compile(rb"\((?:\\.|[^\\()])*\)|<[0-9A-Fa-f\s]+>", re.S)


def extract_from_content(stream):
    pieces = []
    for tm in re.finditer(rb"\[(.*?)\]\s*TJ|(\((?:\\.|[^\\()])*\)|<[0-9A-Fa-f\s]+>)\s*Tj|"
                          rb"(T\*|Td|TD|ET|BT)", stream, re.S):
        arr, single, op = tm.group(1), tm.group(2), tm.group(3)
        if op is not None:
            if op in (b"T*", b"Td", b"TD", b"ET"):
                pieces.append("\n")
            continue
        if arr is not None:
            for part in TEXT_RE.finditer(arr):
                tok = part.group(0)
                if tok.startswith(b"("):
                    pieces.append(decode_bytes(unescape_pdf_string(tok[1:-1])))
                else:
                    hexs = re.sub(rb"\s", b"", tok[1:-1])
                    if len(hexs) % 2:
                        hexs += b"0"
                    try:
                        pieces.append(decode_bytes(bytes.fromhex(hexs.decode())))
                    except ValueError:
                        pass
        elif single is not None:
            tok = single
            if tok.startswith(b"("):
                pieces.append(decode_bytes(unescape_pdf_string(tok[1:-1])))
            else:
                hexs = re.sub(rb"\s", b"", tok[1:-1])
                if len(hexs) % 2:
                    hexs += b"0"
                try:
                    pieces.append(decode_bytes(bytes.fromhex(hexs.decode())))
                except ValueError:
                    pass
    return "".join(pieces)


def extract(path):
    data = open(path, "rb").read()
    chunks = []
    for st in iter_streams(data):
        if b"BT" not in st and b"Tj" not in st and b"TJ" not in st:
            continue
        txt = extract_from_content(st)
        if txt.strip():
            chunks.append(txt)
    return "\n".join(chunks)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        out = extract(p)
        dst = p.rsplit(".", 1)[0] + ".txt"
        with open(dst, "w", encoding="utf-8") as f:
            f.write(out)
        print(dst, len(out), "chars")
