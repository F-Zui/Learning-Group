# render_figures.ps1 —— 把图形指令文件渲染为 PNG（C# + GDI+）
# 用法: powershell -File render_figures.ps1 -Spec <指令文件> -OutDir <输出目录>
param([string]$Spec, [string]$OutDir)

$csharp = @'
using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Globalization;
using System.IO;

public class FigRender
{
    static Color C(string s)
    {
        s = s.TrimStart('#');
        if (s.Length == 3) s = "" + s[0] + s[0] + s[1] + s[1] + s[2] + s[2];
        return Color.FromArgb(
            int.Parse(s.Substring(0, 2), NumberStyles.HexNumber),
            int.Parse(s.Substring(2, 2), NumberStyles.HexNumber),
            int.Parse(s.Substring(4, 2), NumberStyles.HexNumber));
    }
    static float F(string s) { return float.Parse(s, CultureInfo.InvariantCulture); }

    public static string Run(string specPath, string outDir)
    {
        string[] lines = File.ReadAllLines(specPath, System.Text.Encoding.UTF8);
        Bitmap bmp = null; Graphics g = null; string cur = null; int count = 0;
        foreach (string raw in lines)
        {
            string line = raw.Trim();
            if (line.Length == 0) continue;
            if (line.StartsWith("===FIG"))
            {
                if (bmp != null) { bmp.Save(Path.Combine(outDir, cur), System.Drawing.Imaging.ImageFormat.Png); g.Dispose(); bmp.Dispose(); count++; }
                cur = line.Substring(6).Trim(); bmp = null; g = null; continue;
            }
            string[] a = line.Split(' ');
            if (a[0] == "SIZE")
            {
                bmp = new Bitmap(int.Parse(a[1]), int.Parse(a[2]));
                g = Graphics.FromImage(bmp);
                g.SmoothingMode = SmoothingMode.AntiAlias;
                g.TextRenderingHint = System.Drawing.Text.TextRenderingHint.AntiAlias;
                g.Clear(Color.White);
                continue;
            }
            if (g == null) continue;
            try
            {
                switch (a[0])
                {
                    case "LINE":
                    case "DASH":
                    {
                        Pen p = new Pen(C(a[5]), F(a[6]));
                        if (a[0] == "DASH") p.DashPattern = new float[] { 5f, 4f };
                        p.StartCap = LineCap.Round; p.EndCap = LineCap.Round;
                        g.DrawLine(p, F(a[1]), F(a[2]), F(a[3]), F(a[4])); p.Dispose();
                        break;
                    }
                    case "ARROW":
                    {
                        Pen p = new Pen(C(a[5]), F(a[6]));
                        float x1 = F(a[1]), y1 = F(a[2]), x2 = F(a[3]), y2 = F(a[4]);
                        g.DrawLine(p, x1, y1, x2, y2);
                        float ang = (float)Math.Atan2(y2 - y1, x2 - x1);
                        float L = 10f + F(a[6]) * 2f, W = (float)(Math.PI / 7);
                        PointF[] tri = new PointF[] {
                            new PointF(x2, y2),
                            new PointF(x2 - L * (float)Math.Cos(ang - W), y2 - L * (float)Math.Sin(ang - W)),
                            new PointF(x2 - L * (float)Math.Cos(ang + W), y2 - L * (float)Math.Sin(ang + W))
                        };
                        g.FillPolygon(new SolidBrush(C(a[5])), tri); p.Dispose();
                        break;
                    }
                    case "DOT":
                        g.FillEllipse(new SolidBrush(C(a[4])), F(a[1]) - F(a[3]), F(a[2]) - F(a[3]), F(a[3]) * 2, F(a[3]) * 2);
                        break;
                    case "CIRC":
                    {
                        Pen p = new Pen(C(a[4]), F(a[5]));
                        g.DrawEllipse(p, F(a[1]) - F(a[3]), F(a[2]) - F(a[3]), F(a[3]) * 2, F(a[3]) * 2); p.Dispose();
                        break;
                    }
                    case "RECT":
                    {
                        float x1 = F(a[1]), y1 = F(a[2]), x2 = F(a[3]), y2 = F(a[4]);
                        RectangleF r = new RectangleF(Math.Min(x1, x2), Math.Min(y1, y2), Math.Abs(x2 - x1), Math.Abs(y2 - y1));
                        if (a[7] != "-") g.FillRectangle(new SolidBrush(C(a[7])), r);
                        if (F(a[6]) > 0) { Pen p = new Pen(C(a[5]), F(a[6])); g.DrawRectangle(p, r.X, r.Y, r.Width, r.Height); p.Dispose(); }
                        break;
                    }
                    case "ELLIPSE":
                    {
                        float cx = F(a[1]), cy = F(a[2]), rx = F(a[3]), ry = F(a[4]);
                        if (a[7] != "-") g.FillEllipse(new SolidBrush(C(a[7])), cx - rx, cy - ry, rx * 2, ry * 2);
                        if (F(a[6]) > 0) { Pen p = new Pen(C(a[5]), F(a[6])); g.DrawEllipse(p, cx - rx, cy - ry, rx * 2, ry * 2); p.Dispose(); }
                        break;
                    }
                    case "POLY":
                    {
                        // POLY width fill n x1 y1 ... color
                        int n = int.Parse(a[3]);
                        PointF[] pts = new PointF[n];
                        for (int i = 0; i < n; i++) pts[i] = new PointF(F(a[4 + i * 2]), F(a[5 + i * 2]));
                        string fillc = a[2];
                        if (fillc != "-") g.FillPolygon(new SolidBrush(C(fillc)), pts);
                        if (F(a[1]) > 0) { Pen p = new Pen(C(a[a.Length - 1]), F(a[1])); g.DrawLines(p, pts); p.Dispose(); }
                        break;
                    }
                    case "CURVE":
                    {
                        // CURVE color width n x1 y1 ...
                        int n = int.Parse(a[3]);
                        PointF[] pts = new PointF[n];
                        for (int i = 0; i < n; i++) pts[i] = new PointF(F(a[4 + i * 2]), F(a[5 + i * 2]));
                        Pen p = new Pen(C(a[1]), F(a[2]));
                        p.StartCap = LineCap.Round; p.EndCap = LineCap.Round;
                        p.LineJoin = LineJoin.Round;
                        if (n > 2) g.DrawCurve(p, pts); else if (n == 2) g.DrawLine(p, pts[0], pts[1]);
                        p.Dispose();
                        break;
                    }
                    case "ARC":
                    {
                        float cx = F(a[1]), cy = F(a[2]), rx = F(a[3]), ry = F(a[4]);
                        float a0 = F(a[5]), a1 = F(a[6]);
                        Pen p = new Pen(C(a[7]), F(a[8]));
                        g.DrawArc(p, cx - rx, cy - ry, rx * 2, ry * 2, a0, a1 - a0); p.Dispose();
                        break;
                    }
                    case "TEXT":
                    {
                        // TEXT x y size color alignBold font string...
                        float x = F(a[1]), y = F(a[2]), sz = F(a[3]);
                        string col = a[4], al = a[5];
                        int i = 6; bool bold = false;
                        if (a[6] == "B") { bold = true; i = 7; }
                        string txt = string.Join(" ", a, i, a.Length - i);
                        FontStyle fs = bold ? FontStyle.Bold : FontStyle.Regular;
                        Font f = new Font("Cambria Math", sz, fs, GraphicsUnit.Pixel);
                        SizeF m = g.MeasureString(txt, f);
                        float dx = 0;
                        if (al == "c") dx = -m.Width / 2; else if (al == "r") dx = -m.Width;
                        g.DrawString(txt, f, new SolidBrush(C(col)), x + dx, y - m.Height / 2);
                        f.Dispose();
                        break;
                    }
                }
            }
            catch (Exception e) { Console.WriteLine("ERR " + line + " :: " + e.Message); }
        }
        if (bmp != null) { bmp.Save(Path.Combine(outDir, cur), System.Drawing.Imaging.ImageFormat.Png); g.Dispose(); bmp.Dispose(); count++; }
        return "rendered " + count + " figures";
    }
}
'@

Add-Type -TypeDefinition $csharp -ReferencedAssemblies System.Drawing,System.Drawing.Primitives
if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Force -Path $OutDir | Out-Null }
[FigRender]::Run($Spec, $OutDir)
