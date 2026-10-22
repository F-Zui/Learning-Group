# -*- coding: utf-8 -*-
"""
figures_ch1.py —— 第一章图解定义

用简洁的图元 DSL 描述每幅图，导出为指令文件，再由 render_figures.ps1
（C# + GDI+）渲染成 PNG。图片以 "fig1.2.3" 形式编号，正文用 ![[编号]] 引用。
"""
import io
import os

OUT_SPEC = r"D:\Project\math\.build\figures.txt"
OUT_DIR = r"D:\Project\math\figures"

BLACK = "#1A1A1A"
GRAY = "#8C8C8C"
RED = "#C00000"
BLUE = "#2E5C8A"
GREEN = "#3C7A3C"
FILLB = "#DCE6F2"
FILLR = "#F7DCDC"
FILLG = "#DDEBDD"
FILLY = "#FAF0D2"


class Fig(object):
    def __init__(self, name, w, h):
        self.name = name
        self.w, self.h = w, h
        self.c = []

    # ---------- 图元 ----------
    def line(self, x1, y1, x2, y2, color=BLACK, w=2):
        self.c.append("LINE %g %g %g %g %s %g" % (x1, y1, x2, y2, color, w))

    def dash(self, x1, y1, x2, y2, color=GRAY, w=1.5):
        self.c.append("DASH %g %g %g %g %s %g" % (x1, y1, x2, y2, color, w))

    def arrow(self, x1, y1, x2, y2, color=BLACK, w=2):
        self.c.append("ARROW %g %g %g %g %s %g" % (x1, y1, x2, y2, color, w))

    def axis(self, x1, y1, x2, y2, label=None, color=BLACK, w=2):
        self.arrow(x1, y1, x2, y2, color, w)
        if label:
            self.text(x2 + 16, y2, label, 18, color)

    def dot(self, x, y, r=5, color=RED):
        self.c.append("DOT %g %g %g %s" % (x, y, r, color))

    def circ(self, x, y, r=5, color=RED, w=2):
        self.c.append("CIRC %g %g %g %s %g" % (x, y, r, color, w))

    def rect(self, x1, y1, x2, y2, color=BLACK, w=1.5, fill="-"):
        self.c.append("RECT %g %g %g %g %s %g %s" % (x1, y1, x2, y2, color, w, fill))

    def ellipse(self, cx, cy, rx, ry, color=BLACK, w=1.5, fill="-"):
        self.c.append("ELLIPSE %g %g %g %g %s %g %s" % (cx, cy, rx, ry, color, w, fill))

    def poly(self, pts, color=BLACK, w=2, fill="-"):
        flat = " ".join("%g %g" % p for p in pts)
        self.c.append("POLY %g %s %d %s %s" % (w, fill, len(pts), flat, color))

    def curve(self, pts, color=BLUE, w=2.5):
        flat = " ".join("%g %g" % p for p in pts)
        self.c.append("CURVE %s %g %d %s" % (color, w, len(pts), flat))

    def arc(self, cx, cy, rx, ry, a0, a1, color=BLACK, w=2):
        self.c.append("ARC %g %g %g %g %g %g %s %g" % (cx, cy, rx, ry, a0, a1, color, w))

    def text(self, x, y, s, size=18, color=BLACK, align="c", bold=False):
        b = " B" if bold else ""
        self.c.append("TEXT %g %g %g %s %s%s %s" % (x, y, size, color, align, b, s))

    def dump(self):
        out = ["===FIG %s.png" % self.name, "SIZE %d %d" % (self.w, self.h)]
        return "\n".join(out + self.c)


F = {}


# ============================================================ 图 1.1.1  邻域
def fig_neighbourhood():
    f = Fig("fig1_1_1", 1000, 330)
    a, d = 520, 150

    for row, y, label in ((0, 110, "U(a, δ)：中心 a 也在其中"),
                          (1, 250, "U°(a, δ)：挖掉中心 a")):
        f.line(70, y, 930, y, BLACK, 2)
        f.arrow(930, y, 950, y, BLACK, 2)
        if row == 0:
            f.rect(a - d, y - 26, a + d, y + 26, BLUE, 1.5, FILLB)
            f.circ(a - d, y, 5, BLUE); f.circ(a + d, y, 5, BLUE)
            f.dot(a, y, 6, RED)
        else:
            f.rect(a - d, y - 26, a - 8, y + 26, BLUE, 1.5, FILLB)
            f.rect(a + 8, y - 26, a + d, y + 26, BLUE, 1.5, FILLB)
            f.circ(a - d, y, 5, BLUE); f.circ(a + d, y, 5, BLUE)
            f.circ(a, y, 6, RED, 2)
        f.text(a, y + 52, "a", 19, RED)
        f.text(a - d, y + 52, "a − δ", 18, BLUE)
        f.text(a + d, y + 52, "a + δ", 18, BLUE)
        f.text(70, y - 48, label, 17, BLACK, "l")

    # 半径标注
    f.arrow(520, 190, 370, 190, GREEN, 1.5)
    f.arrow(520, 190, 670, 190, GREEN, 1.5)
    f.text(445, 210, "δ", 19, GREEN)
    f.text(595, 210, "δ", 19, GREEN)
    return f


# ==================================================== 图 1.2.1  ε-N 的几何意义
def fig_eps_n():
    f = Fig("fig1_4_1", 1000, 300)
    y, a, e = 180, 540, 105
    f.line(60, y, 930, y, BLACK, 2)
    f.arrow(930, y, 952, y, BLACK, 2)

    f.rect(a - e, y - 34, a + e, y + 34, RED, 1.5, FILLR)
    f.dash(a - e, y - 62, a - e, y + 62, RED, 1.5)
    f.dash(a + e, y - 62, a + e, y + 62, RED, 1.5)
    f.dot(a, y, 6, RED)

    # 带外的有限项
    for x in (120, 190, 250, 320, 400, 470):
        f.dot(x, y, 5, GRAY)
    # 带内的项
    for x in (500, 515, 545, 560, 580, 600, 620):
        f.dot(x, y, 5, GREEN)

    f.text(a, y - 88, "a − ε", 18, RED)
    f.text(a + e, y - 88, "a + ε", 18, RED)
    f.text(a, y + 58, "a", 19, RED)
    f.text(300, y - 58, "只有有限项落在带外", 17, GRAY)
    f.text(620, y - 58, "从第 N+1 项起全部落入带内", 17, GREEN)
    f.circ(500, y, 5, GREEN)
    f.text(480, y + 56, "N+1", 16, GREEN, "r")
    f.text(500, 40, "∀ε > 0，把数列的“尾巴”关进 (a − ε, a + ε)", 19, BLACK)
    return f


# ==================================================== 图 1.3.1  ε-δ 的几何意义
def fig_eps_delta():
    f = Fig("fig1_6_1", 1000, 440)
    ox, oy = 120, 370          # 原点
    x0, A = 560, 200
    d, e = 110, 68

    f.axis(ox, oy, 940, oy, "x")
    f.axis(ox, oy, ox, 40, "y")

    # ε 水平带（y 轴向上，故 A+ε 在上、A−ε 在下）
    f.rect(ox, A - e, 940, A + e, RED, 0, FILLR)
    f.dash(ox, A - e, 940, A - e, RED, 1.2)
    f.dash(ox, A + e, 940, A + e, RED, 1.2)
    f.text(ox - 14, A - e, "A + ε", 17, RED, "r")
    f.text(ox - 14, A + e, "A − ε", 17, RED, "r")

    # δ 竖直带
    f.rect(x0 - d, 152, x0 + d, oy, GREEN, 0, FILLG)
    f.dash(x0 - d, 152, x0 - d, oy, GREEN, 1.2)
    f.dash(x0 + d, 152, x0 + d, oy, GREEN, 1.2)
    f.text(x0 - d, oy + 26, "x₀ − δ", 17, GREEN)
    f.text(x0 + d, oy + 26, "x₀ + δ", 17, GREEN)
    f.text(x0, oy + 26, "x₀", 18, RED)

    # 函数曲线
    pts = [(170, 330), (230, 305), (300, 275), (370, 245), (430, 222),
           (490, 208), (560, 200), (640, 188), (720, 172), (800, 152), (880, 130)]
    f.curve(pts, BLUE, 3)

    f.dot(x0, A, 6, RED)
    f.dash(x0, A, x0, oy, GRAY, 1.2)
    f.dash(ox, A, x0, A, GRAY, 1.2)
    f.text(ox - 12, A, "A", 18, BLACK, "r")

    f.text(560, 52, "对任意水平带 (A − ε, A + ε)", 18, RED, "c")
    f.text(560, 80, "总能找到竖直带 (x₀ − δ, x₀ + δ)", 18, GREEN, "c")
    f.text(560, 108, "使其内的图像整段落在水平带里", 18, BLACK, "c")
    return f


# ======================================================== 图 1.5.1  夹逼准则
def fig_squeeze():
    f = Fig("fig1_10_1", 1000, 380)
    ox, oy = 100, 320
    f.axis(ox, oy, 950, oy, "x")
    f.axis(ox, oy, ox, 40, "y")

    lim = 130
    f.dash(ox, lim, 950, lim, RED, 1.5)
    f.text(960, lim, "a", 19, RED)
    f.text(960, lim + 26, "极限值", 15, RED)

    # 上界 h(x) 递减趋近 a
    up = [(140, 96), (240, 106), (340, 114), (440, 120), (540, 124),
          (660, 127), (780, 129), (900, 130)]
    dn = [(140, 172), (240, 158), (340, 148), (440, 141), (540, 136),
          (660, 133), (780, 131), (900, 130)]
    mid = [(150, 150), (200, 118), (250, 152), (300, 112), (350, 150),
           (400, 120), (450, 145), (500, 122), (560, 137), (620, 126),
           (700, 131), (800, 129), (900, 130)]
    f.curve(up, GREEN, 2.5)
    f.curve(dn, GREEN, 2.5)
    f.curve(mid, BLUE, 2.5)

    f.text(200, 78, "h(x)（上界）", 18, GREEN, "l")
    f.text(200, 196, "g(x)（下界）", 18, GREEN, "l")
    f.text(760, 92, "f(x)", 19, BLUE, "c")
    f.text(520, 352, "上下两条边界合拢于 a ⟹ 夹在中间的 f(x) 也被迫趋于 a", 19, BLACK)
    return f


# ============================================== 图 1.5.2  第一个重要极限的面积比较
def fig_sinx_over_x():
    f = Fig("fig1_10_2", 1160, 560)
    import math
    O = (265, 345); R = 195
    th = math.radians(40)
    A = (O[0] + R, O[1])
    B = (O[0] + R * math.cos(th), O[1] - R * math.sin(th))
    t = (A[0] - O[0]) / math.cos(th)
    D = (A[0], O[1] - t * math.sin(th))

    f.axis(O[0], O[1], 580, O[1], "x")
    f.axis(O[0], O[1], O[0], 60, "y")
    f.ellipse(O[0], O[1], R, R, "#D0D0D0", 1.2, "-")

    # 扇形 OAB（黄色实填）
    arc = [(O[0] + R * math.cos(th * i / 40), O[1] - R * math.sin(th * i / 40)) for i in range(41)]
    f.poly([O, A] + arc, FILLY, 0, FILLY)
    # 三角形 OAB（蓝色轮廓）
    f.poly([O, A, B], BLUE, 2, "-")
    # 三角形 OAD（红色轮廓）
    f.poly([O, A, D], RED, 2, "-")
    f.line(O[0], O[1], D[0], D[1], BLACK, 1.6)
    f.line(O[0], O[1], A[0], A[1], BLACK, 1.6)

    for P, lb, dx, dy in ((O, "O", -24, 22), (A, "A", 8, 26),
                          (B, "B", -8, -24), (D, "D", 10, -10)):
        f.dot(P[0], P[1], 5, BLACK)
        f.text(P[0] + dx, P[1] + dy, lb, 20, BLACK)
    f.arc(O[0], O[1], 95, 95, -math.degrees(th), 0, BLACK, 1.5)
    f.text(O[0] + 118, O[1] - 40, "x", 19, BLACK)

    # 右侧说明区（不压图）
    f.text(640, 140, "三块图形的面积关系：", 19, BLACK, "l", True)
    f.text(640, 186, "三角形 OAB ⊂ 扇形 OAB ⊂ 三角形 OAD", 18, BLUE, "l")
    f.text(640, 226, "(1/2)·sin x  <  x/2  <  (1/2)·tan x", 18, BLUE, "l")
    f.text(640, 272, "同除以 (1/2)·sin x：", 18, BLACK, "l")
    f.text(640, 310, "cos x  <  (sin x)/x  <  1", 19, GREEN, "l", True)
    f.text(640, 358, "令 x → 0⁺，由夹逼准则得：", 18, BLACK, "l")
    f.text(640, 398, "lim (sin x)/x = 1", 20, RED, "l", True)
    return f


# ==================================================== 图 1.6.1  间断点的四种类型
def fig_discontinuity():
    f = Fig("fig1_13_1", 1020, 500)
    W, H = 460, 200
    panels = [
        (30, 40, "可去间断点（第一类）", "hole"),
        (530, 40, "跳跃间断点（第一类）", "jump"),
        (30, 270, "无穷间断点（第二类）", "inf"),
        (530, 270, "振荡间断点（第二类）", "osc"),
    ]
    import math
    for px, py, cap, kind in panels:
        cx, cy = px + W / 2, py + H / 2 + 18
        f.rect(px, py, px + W, py + H, "#BFBFBF", 1, "-")
        f.line(px + 30, cy, px + W - 20, cy, BLACK, 1.5)
        f.line(px + W / 2, py + 76, px + W / 2, py + H - 16, BLACK, 1.5)
        f.text(px + W / 2, py + 14, cap, 17, BLUE, "c", True)
        ox, oy = px + W / 2, cy

        if kind == "hole":
            pts = [(ox - 130, oy + 34), (ox - 70, oy + 18), (ox - 20, oy + 6)]
            f.curve(pts, BLUE, 2.5)
            pts2 = [(ox + 20, oy - 6), (ox + 70, oy - 18), (ox + 130, oy - 34)]
            f.curve(pts2, BLUE, 2.5)
            f.circ(ox, oy, 5, RED, 2)
        elif kind == "jump":
            pts = [(ox - 130, oy + 22), (ox - 60, oy + 6), (ox - 2, oy - 4)]
            f.curve(pts, BLUE, 2.5)
            pts2 = [(ox + 2, oy - 30), (ox + 60, oy - 40), (ox + 130, oy - 52)]
            f.curve(pts2, BLUE, 2.5)
            f.dot(ox - 2, oy - 4, 4.5, BLUE)
            f.circ(ox + 2, oy - 30, 4.5, BLUE, 2)
            f.dash(ox, oy - 30, ox, oy - 4, RED, 1.5)
        elif kind == "inf":
            pts = [(ox - 130, oy - 60), (ox - 70, oy - 34), (ox - 30, oy - 6),
                   (ox - 12, oy + 34), (ox - 6, oy + 66)]
            f.curve(pts, BLUE, 2.5)
            pts2 = [(ox + 6, oy + 66), (ox + 12, oy + 34), (ox + 30, oy - 6),
                    (ox + 70, oy - 34), (ox + 130, oy - 60)]
            f.curve(pts2, BLUE, 2.5)
            f.dash(ox, oy - 62, ox, oy + 70, RED, 1.5)
        else:
            pts = []
            for i in range(0, 261):
                x = ox - 130 + i
                if abs(x - ox) < 4:
                    continue
                pts.append((x, oy - 34 * math.sin(60.0 / (x - ox))))
            f.curve(pts, BLUE, 1.6)
            f.dash(ox, oy - 62, ox, oy + 70, RED, 1.5)
    return f


# ==================================================== 图 1.7.1  零点定理
def fig_zero_point():
    f = Fig("fig1_14_1", 940, 430)
    ox, oy = 120, 300
    f.axis(ox, oy, 890, oy, "x")
    f.axis(ox, oy, ox, 40, "y")

    a, b = 250, 700
    xi = 430
    pts = [(a, 410), (300, 372), (350, 344), (xi - 10, 306), (xi, 300),
           (xi + 10, 294), (500, 262), (560, 224), (620, 186), (680, 150), (b, 120)]
    f.curve(pts, BLUE, 3)

    for x, lb, col in ((a, "a", BLACK), (b, "b", BLACK)):
        f.dash(x, oy, x, dict(zip((a, b), (410, 120)))[x], GRAY, 1.2)
        f.dot(x, dict(zip((a, b), (410, 120)))[x], 5, col)
        f.text(x, oy + 26, lb, 19, BLACK)
    f.dot(xi, oy, 6, RED)
    f.text(xi + 22, oy - 20, "ξ", 20, RED)

    fa = 410; fb = 120
    f.text(a - 14, fa, "f(a)", 17, BLUE, "r")
    f.text(b + 14, fb, "f(b)", 17, BLUE, "l")
    f.dash(ox, fa, a, fa, GRAY, 1.0)
    f.dash(ox, fb, b, fb, GRAY, 1.0)

    f.text(510, 388, "f(a) < 0 < f(b)，曲线要跨过 x 轴就必然与它相交", 18, BLACK)
    f.text(510, 416, "故存在 ξ ∈ (a, b) 使 f(ξ) = 0", 19, RED, "c", True)
    return f


# ==================================================== 图 1.2.2  收敛与有界
def fig_bounded():
    f = Fig("fig1_5_1", 1000, 330)
    import math
    # 左图：收敛 ⟹ 有界
    f.text(250, 26, "收敛：尾部被圈住，整体有界", 18, BLUE, "c", True)
    ox, oy = 70, 200
    f.line(ox, oy, 460, oy, BLACK, 1.5)
    f.dash(ox, oy - 46, 460, oy - 46, RED, 1.2)
    f.dash(ox, oy + 46, 460, oy + 46, RED, 1.2)
    for i in range(1, 15):
        x = ox + i * 26
        y = oy + 46 * (0.55 ** i) * (-1 if i % 2 else 1)
        f.dot(x, y, 4, GREEN)
    f.text(250, oy - 74, "极限值附近的带", 16, RED)
    f.text(250, oy + 86, "只有前有限项可能在外", 16, GRAY)

    # 右图：有界但发散
    f.text(760, 26, "有界但发散：两个子列跑向不同值", 18, RED, "c", True)
    ox2, oy2 = 570, 200
    f.line(ox2, oy2, 970, oy2, BLACK, 1.5)
    f.dash(ox2, oy2 - 70, 970, oy2 - 70, BLUE, 1.2)
    f.dash(ox2, oy2 + 70, 970, oy2 + 70, BLUE, 1.2)
    for i in range(1, 15):
        x = ox2 + i * 27
        f.dot(x, oy2 - 70, 5, RED)
        f.dot(x, oy2 + 70, 5, RED)
    f.text(770, oy2 - 92, "奇数项子列 → 1", 16, RED)
    f.text(770, oy2 + 96, "偶数项子列 → −1", 16, RED)
    return f


def main():
    figs = [fig_neighbourhood(), fig_bounded(), fig_eps_n(), fig_eps_delta(),
            fig_squeeze(), fig_sinx_over_x(), fig_discontinuity(), fig_zero_point()]
    with io.open(OUT_SPEC, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(x.dump() for x in figs) + "\n")
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    # 图号与题注
    meta = [
        ("fig1_1_1", "1.1.1", "邻域 U(a, δ) 与去心邻域 U°(a, δ)"),
        ("fig1_4_1", "1.4.1", "数列极限 ε-N 定义的几何意义"),
        ("fig1_5_1", "1.5.1", "收敛必有界；有界未必收敛"),
        ("fig1_6_1", "1.6.1", "函数极限 ε-δ 定义的几何意义"),
        ("fig1_10_1", "1.10.1", "夹逼准则"),
        ("fig1_10_2", "1.10.2", "第一个重要极限的证明：面积比较"),
        ("fig1_13_1", "1.13.1", "间断点的四种类型"),
        ("fig1_14_1", "1.14.1", "零点定理的几何意义"),
    ]
    with io.open(os.path.join(OUT_DIR, "index.txt"), "w",
                 encoding="utf-8", newline="\n") as fh:
        for fid, num, cap in meta:
            fh.write("%s|%s|%s\n" % (fid, num, cap))
    print("指令文件已写出:", OUT_SPEC, "共", len(figs), "幅")


if __name__ == "__main__":
    main()
