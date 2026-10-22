# -*- coding: utf-8 -*-
"""第 09 节 · 字符串进阶：数字、进制与格式"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dsl import *  # noqa

SEC = []

SEC.append(P("上一节把字符串当<b>字符数组</b>用：下标、遍历、字符分类。这一节换个看法——"
             "把字符串当成<b>数字的另一种写法</b>。同一个值 255，10 进制写作 <code>255</code>，"
             "2 进制写作 <code>11111111</code>，16 进制写作 <code>FF</code>。三串字符，一个数。"))

SEC.append(L([
    "<b>数字 → 字符串</b>：<code>to_string</code>、<code>sprintf</code>。拼输出、算位数、补前导零。",
    "<b>字符串 → 数字</b>：<code>stoi</code>、<code>stoll</code>，或者自己写秦九韶循环。",
    "<b>定位与切段</b>：<code>find</code> 找分隔符，<code>substr</code> 切开，<code>reverse</code> 就地翻转。",
]))

SEC.append(Q("判断标准只有一条：这个数能保证不超过 19 位吗？能，就用 long long 中转；"
             "不能，就全程 string，一个字符都别进数字类型。"))

# ---------------------------------------------------------------- 新函数
SEC.append(FN(
    "to_string",
    "string to_string(int x);\nstring to_string(long long x);\nstring to_string(double x);",
    [("参数", "任意算术类型，编译器按实参自动挑重载。"),
     ("返回值", "string。位数就是 <code>.size()</code>，第 i 位字符就是 <code>s[i]</code>。"),
     ("double 版本", "固定 6 位小数，宽度和位数都管不了——要格式就别用它。"),
     ("效率", "比 sprintf 慢 2~3 倍，循环 10⁶ 次以上要掂量。")],
    example=r'''int a = 42;
string s1 = to_string(a);                     // "42"，长度 2
string s2 = to_string(123456789012345678LL);  // 18 位
cout << s1 + "!";                             // 42!：+ 是拼接
cout << s2.size();                            // 18：位数 = 长度''',
    notes=["<code>to_string(1.0)</code> 得到 <code>\"1.000000\"</code>，不是 <code>\"1\"</code>。",
           "两个结果只能 <code>+</code> 拼接，<code>s1 - s2</code> 编译不过。"],
    brief="数字转字符串，位数直接看 size()"))

SEC.append(FN(
    "stoi",
    "int stoi(const string& s, size_t* pos = nullptr, int base = 10);",
    [("s", "要解析的串，允许前导空格与正负号。"),
     ("pos", "可选。传 <code>&amp;p</code> 就把“停在哪个下标”写进 p。"),
     ("base", "可选，2~36。写 16 就能直接读 <code>\"7f\"</code> 得 127。"),
     ("停在哪", "遇到不属于该进制的字符就停，不报错：<code>\"123abc\"</code> 得 123。"),
     ("抛异常", "超出 int 范围时抛 <code>std::out_of_range</code>，进程终止，评测显示 <b>RE</b>。")],
    example=r'''string s = "  -12345abc";
size_t pos;
int x = stoi(s, &pos);                 // -12345，pos = 8（停在 'a'）
int y = stoi("7f", nullptr, 16);       // 127
int z = stoi("11111111", nullptr, 2);  // 255''',
    notes=["只认 int 范围。11 位的 <code>\"99999999999\"</code> 就抛异常。",
           "怕异常就自己写 <code>x = x * 10 + (c - '0')</code>，绝不会炸。"],
    brief="字符串转 int，可指定进制与停止位置"))

SEC.append(FN(
    "stoll",
    "long long stoll(const string& s, size_t* pos = nullptr, int base = 10);",
    [("三个参数", "含义与 stoi 一字不差，只是返回值换成 long long。"),
     ("上限", "9223372036854775807（19 位）。值一旦超过它就抛 <code>out_of_range</code>，所以 19 位也不能乱填。"),
     ("怎么选", "≤ 9 位用 stoi，10~18 位用 stoll，19 位对照上限看，≥ 20 位不转数字。")],
    example=r'''long long a = stoll("9223372036854775807");   // 19 位，正好 LLONG_MAX
// stoll("9223372036854775808")  → 抛 out_of_range
string big = "12345678901234567890";          // 20 位，只能留在 string 里''',
    notes=["20 位的 18446744073709551615 连 unsigned long long 都装不下。",
           "题目给出 20 位以上的数字，等于明示这道题考字符串。"],
    brief="字符串转 long long，19 位是硬上限"))

SEC.append(FN(
    "reverse",
    "reverse(s.begin(), s.end());      // 需要 <algorithm>",
    [("区间", "左闭右开 <code>[first, last)</code>。<code>s.end()</code> 是末字符的下一个位置。"),
     ("返回值", "<b>void</b>。原地修改，不产生新串。"),
     ("数组也能用", "<code>reverse(a, a + n)</code> 反转 int 数组。"),
     ("复杂度", "O(n)，每个元素交换一次。")],
    example=r'''string s = "hello";
reverse(s.begin(), s.end());   // s 变成 "olleh"
cout << s;                     // 先反转，再输出

int a[5] = {1, 2, 3, 4, 5};
reverse(a, a + 5);             // 5 4 3 2 1''',
    notes=["<code>cout &lt;&lt; reverse(...)</code> 是编译错误（no match for operator&lt;&lt;），不是 WA。",
           "只给一个迭代器参数也编译不过——它要首尾两个。"],
    brief="原地反转，返回 void，别往 cout 里塞"))

SEC.append(FN(
    "find",
    "s.find(要找的东西, 起点 = 0);     // 返回 size_t",
    [("参数", "子串或单个 char：<code>s.find('.')</code>、<code>s.find(\"to\")</code>。"),
     ("起点", "从哪个下标开始找；想接着找就传 <code>上次位置 + 1</code>。"),
     ("返回值", "首次出现的下标；找不到返回 <code>string::npos</code>，不是 -1。"),
     ("npos", "size_t 的最大值 2⁶⁴−1。判断写 <code>!= string::npos</code>，别写 <code>&lt; 0</code>。")],
    example=r'''string t = " to be or not to be ", w = " to ";
int cnt = 0;
size_t p = t.find(w);
while (p != string::npos) {
    ++cnt;
    p = t.find(w, p + 1);      // 从下一位继续，否则原地死循环
}
cout << cnt;                   // 2''',
    notes=["漏掉 <code>+1</code>：find 每次返回同一个下标，死循环，评测 <b>TLE</b>。",
           "把结果存进 int 再和 npos 比，npos 截断成 -1，看似能过；换成 <code>&lt; 0</code> 的判断就永远为假。"],
    brief="找子串/字符，返回下标或 npos"))

SEC.append(FN(
    "substr",
    "string substr(size_t pos = 0, size_t len = npos) const;",
    [("pos", "起点下标。<code>pos == size()</code> 合法，得空串。"),
     ("len", "取几个字符；省略就取到结尾，写大了自动截断，不报错。"),
     ("pos 越界", "<code>pos &gt; size()</code> 抛 out_of_range → <b>RE</b>。"),
     ("最常用", "取 <code>[l, r)</code> 这一段写 <code>s.substr(l, r - l)</code>。")],
    example=r'''string s = "123.456";
size_t p = s.find('.');        // 3
string a = s.substr(0, p);     // "123"
string b = s.substr(p + 1);    // "456"，取到结尾
string c = s.substr(2, 5 - 2); // "3.4"''',
    notes=["<code>s.substr(p + 1)</code> 在 p 是末字符时返回空串，合法。",
           "第一个参数是起点，不是长度——这是最常见的错法。"],
    brief="切段：起点 + 长度，或只给起点取到结尾"))

SEC.append(FN(
    "sprintf",
    "int sprintf(char buf[], const char* fmt, ...);    // <cstdio>",
    [("buf", "字符数组，大小自己保证；写越界就是踩内存，表现为 RE 或莫名 WA。"),
     ("fmt", "%d 整数、%lld 长整型、%x 小写十六进制、%X 大写、%02d 补两位零、%s 字符串。"),
     ("转 string", "char 数组可以直接赋给 string：<code>string s = buf;</code>")],
    example=r'''char buf[64];
sprintf(buf, "%03d", 7);              // "007"，前导零
sprintf(buf, "%X", 255);              // "FF"
sprintf(buf, "%lld", 10000000000LL);  // long long 必须 %lld
string s = buf;''',
    notes=["用 %d 打印 long long 是未定义行为：出乱码，且往往只在部分数据上错。",
           "放 20 位数字，<code>char buf[32]</code> 够；做拼接按 <code>len + 16</code> 估。"],
    brief="格式化到字符数组，唯一能做前导零的函数"))

# ---------------------------------------------------------------- 例题
SEC.append(EX("进制转换", "P1143", "普及-", "https://www.luogu.com.cn/problem/P1143",
              [P("输入三行：第一行整数 n（2 ≤ n ≤ 16），表示原数的进制；第二行一个 n 进制数，"
                 "n &gt; 10 时用大写 A~F 表示 10~15，且它的十进制值不超过 10⁹；"
                 "第三行整数 m（2 ≤ m ≤ 16），表示目标进制。"),
               P("输出这个数在 m 进制下的写法，m &gt; 10 时同样使用大写 A~F。")],
              sample="输入：\n16\nFF\n2\n输出：\n11111111"))

SEC.append(IDEA("思路：先落到十进制，再从十进制长出来", [
    P("n 进制与 m 进制之间没有逐位对应关系（2↔4/8/16 是例外），十进制是唯一的中转站。"
      "中转只需要两个操作："),
    L([
        "<b>读成十进制</b>：秦九韶 <code>dec = dec * n + 当前位的值</code>，从左到右扫一遍，k 位只做 k 次乘加。",
        "<b>写成 m 进制</b>：除基取余，<code>dec % m</code> 是当前最低位，<code>dec /= m</code> 砍掉它，最后整体倒序。",
        "<b>字符 ↔ 数值</b>：不做 if-else，造一张数码表 <code>\"0123456789ABCDEF\"</code>，下标即数值，"
        "<code>digit.find(c)</code> 就是反向查表。",
    ]),
    P("先手算再写码。<code>FF</code>（16 进制）：0×16+15 = 15，15×16+15 = 255。"
      "255 转 2 进制：连除 2 得 8 个余数全是 1，商归零停下，倒着读就是 8 个 1。"),
    P("再用小数字看清“为什么必须倒序”：6 转 2 进制，6 % 2 = 0（这是最低位），3 % 2 = 1，1 % 2 = 1，商为 0 停。"
      "余数按 0、1、1 的顺序出来，可答案是 <code>110</code>——余数天生从低位到高位，所以最后那一次 reverse 不是装饰。"),
]))

SEC.append(C(r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    int n, m;
    string s;
    cin >> n >> s >> m;                  // 三行输入；cin 按“词”读，换行自动跳过

    string digit = "0123456789ABCDEF";   // 数码表：下标即数值，够用到 16 进制

    // ① n 进制 -> 十进制，秦九韶
    long long dec = 0;
    for (int i = 0; i < (int)s.size(); ++i) {
        int d = (int)digit.find(s[i]);   // 'F' 在表里的下标是 15
        dec = dec * n + d;               // 旧值升一档，再加新的一位
    }

    // ② 十进制 -> m 进制，除基取余
    string res;
    if (dec == 0) res = "0";             // 特判：否则 while 一次不进，输出空行
    while (dec > 0) {
        res += digit[(int)(dec % m)];    // 余数就是当前最低位
        dec /= m;                        // 砍掉最低位，下一位升上来
    }
    reverse(res.begin(), res.end());     // 低位先产生，倒过来才是正常写法

    cout << res << "\n";
    return 0;
}''', "完整代码：n 进制 → m 进制"))

SEC.append(EXPLAIN("逐行拆解", [
    ("cin >> n >> s >> m;", "三行被当成三个“词”。s 是 string，遇空白就停，正好读完整个 n 进制数。"),
    ("string digit = \"0123456789ABCDEF\";", "把“数值→字符”做成一张表：digit[15] 就是 'F'。比 if-else 短、比 switch 快；代价是表只有 16 个字符，扩到 36 进制得换表。"),
    ("int d = (int)digit.find(s[i]);", "反向查表：'F' 在表里的下标是 15，即它的数值。find 返回 size_t，赋给 int 要显式转换。"),
    ("dec = dec * n + d;", "秦九韶。乘 n 是把已读部分整体左移一位，加 d 是补上新的最低位。第 i 位最终被乘了 n^(k−1−i) 次，正好等于位权。"),
    ("if (dec == 0) res = \"0\";", "输入 0 时循环一次不进，res 保持空串，会输出一个空行。这是本题唯一的数据边界。"),
    ("res += digit[(int)(dec % m)];", "余数 r = dec mod m 一定是当前最低位，digit[r] 把数值翻回字符，追加到尾部。"),
    ("dec /= m;", "整除砍掉刚取走的最低位，剩下的是「原数除以 m 向下取整」，规模严格变小，循环必停。"),
    ("reverse(res.begin(), res.end());", "余数从低位到高位产生，答案要从高位写起，所以整体倒序。忘掉这句，6 转 2 进制会输出 011。"),
]))

# ---------------------------------------------------------------- 切段
SEC.append(AFTER("切段：find + substr + reverse 三件套", [
    P("小数、分数、日期、坐标的本质都一样：<b>一个串被一个分隔符切成两段</b>。"
      "find 负责定位，substr 负责切开，reverse 各管自己翻转。"),
    C(r'''string s = "123.456";
size_t p = s.find('.');       // 3；找不到时是 string::npos
string a = s.substr(0, p);    // "123"，从 0 取 p 个
string b = s.substr(p + 1);   // "456"，从 p+1 取到结尾
reverse(a.begin(), a.end());  // "321"
reverse(b.begin(), b.end());  // "654"
cout << a << "." << b;        // 321.654''', "切段 + 反转"),
    P("顺带记住两条容易被忽略的规则：string 比较用的是<b>字典序</b>（<code>\"9\" &lt; \"10\"</code> 为假，"
      "而数值上 9 &lt; 10），要按数值比就先比长度、再比字典序；"
      "<code>to_string</code> 造不出前导零，固定宽度只能靠 sprintf。"),
    P("还有一个顺序问题：一个串上通常只有一种分隔符，所以按 <code>%</code> → <code>.</code> → <code>/</code> 依次试，"
      "命中一个就停。写成几个独立的 if（而不是 else if），同一串会被输出两遍——这是下一题最隐蔽的错法。"),
]))

SEC.append(AFTER("这一套能解的五类题", [
    L([
        "<b>回文</b>：复制一份再 <code>reverse</code>，与原串比较；或双指针首尾对扫。",
        "<b>位数 / 数位统计</b>：<code>to_string(x).size()</code> 得位数，遍历字符串得每个数位。",
        "<b>按数值排序</b>：先比长度、再比字典序；数字位数超过 19 时这是唯一可行的比法。",
        "<b>带分隔符的数据</b>：日期 2024-03-15、分数 700/27、坐标 3.5 —— find 定位，substr 切段。",
        "<b>任意进制输入输出</b>：秦九韶进来，除基取余出去；密码题、颜色题、编号题都是它的变体。",
    ]),
]))

SEC.append(AFTER("19 位红线：什么时候不许用数字类型", [
    P("<code>long long</code> 最大 9223372036854775807，19 位。超过它一步，"
      "“string → 数字 → string”这条链就整条断掉——20 位的输入必然如此，19 位的也得先和上限比一比。"
      "P1143 只保证十进制值 ≤ 10⁹（10 位），所以 long long 很富余；"
      "而本节挑战题把长度给到 20 位，同一个算法必须换成纯 string 版本。"),
    P("但<b>不进数字类型 ≠ 不能算</b>：只要最终要的是余数、位数、某一位这类只依赖低位的信息，"
      "秦九韶就能只保留这部分状态往下跑，中间值永远不超范围。所以看到“输入是一个很长的数字串”，"
      "第一个问题永远是：我到底需要它的哪一部分信息？"),
    C(r'''string s = "12345678901234567890";       // 20 位
// long long x = stoll(s);                   // 抛 out_of_range → RE

int r = 0;                                   // 求这个数 mod 7
for (int i = 0; i < (int)s.size(); ++i)
    r = (r * 10 + (s[i] - '0')) % 7;         // 中间值最大 6*10+9 = 69
cout << r;                                   // 1''', "位数超 19：只保留需要的那部分"),
]))

SEC.append(AFTER("怎么验证你的进制转换是对的", [
    P("进制题的答案没法靠“看起来像”判断，交之前用三个办法自检，每个都不到一分钟："),
    L([
        "<b>回环验证</b>：把输出的 m 进制结果再当输入转回 n 进制，应当逐字符还原原串。转两次还一样，基本就对了。",
        "<b>对拍小数据</b>：取 n = 10、m = 2，把 0~100 逐个跑一遍，与计算器或 Excel 的 DEC2BIN 对照。",
        "<b>边界四连</b>：0、1、最大数码（n−1）、n 本身（应写成 <code>10</code>）。这四组能打掉九成的 WA。",
    ]),
    P("这三招不只对进制题有用：凡是“有明确逆运算”的题（进制互转、加解密、编解码）都能用回环验证。"),
]))

SEC.append(T(["进制", "数码", "一位能表示", "典型场合"], [
    ["2", "0 1", "2", "位运算、状压 DP、集合的子集"],
    ["10", "0~9", "10", "所有读入输出、日常计算"],
    ["16", "0~9 A~F", "16", "内存地址 0x7ffd、颜色 #FF8800、哈希"],
    ["36", "0~9 A~Z", "36", "短链接、编号压缩：位数能省一半"],
]))

SEC.append(TIP("看到“数字 / 进制”的题，先回答三问", [
    "最大可能多少位？≤ 9 位 int，≤ 18 位 long long，19 位踮脚，≥ 20 位一律 string。",
    "需要整体数值吗？要就转数字；只要某位、某段、某个余数就全程字符串。",
    "输出有固定宽度、前导零、大小写要求吗？有就用 sprintf 或数码表。",
]))

SEC.append(INFO("输出格式最常见的三种要求", [
    "十六进制大小写：数码表写成 <code>\"0123456789ABCDEF\"</code> 或全小写，一行切换。",
    "固定宽度补零：<code>sprintf(buf, \"%05d\", x)</code>；<code>to_string</code> 做不到这件事。",
    "去掉多余前导零：从下标 0 起跳过 '0'，但至少保留一位，否则 0 会变成空串。",
]))

SEC.append(WARN("这一节最容易踩的 7 个坑", [
    "把 20 位数喂给 <code>stoll</code>：抛 <code>std::out_of_range</code>，进程直接结束，评测显示 <b>RE</b>，连输出都看不到。",
    "字符忘了减 <code>'0'</code>：写成 <code>dec = dec * n + s[i]</code>，<code>'7'</code> 的 ASCII 是 55，答案偏到天边。",
    "除基取余忘了 <code>reverse</code>：6 转 2 进制应输出 <code>110</code>，你会输出 <code>011</code>，带前导零，<b>WA</b>。",
    "用 <code>s.find(c) &lt; 0</code> 判断没找到：<code>size_t</code> 无符号，条件永远为假。一律写 <code>!= string::npos</code>。",
    "拿 <code>find</code> 的返回值直接当 <code>substr</code> 起点：找不到时 npos + 1 是个天文数字，<code>pos &gt; size()</code> 抛异常 → <b>RE</b>。",
    "在循环里写 <code>res = to_string(i) + res</code>：每轮都要整体搬移整串，10⁵ 轮就是 O(n²)，本地跑得动、交上去 <b>TLE</b>。正确做法是往后追加、最后 reverse 一次。",
    "<code>dec == 0</code> 不特判：输入 <code>0</code> 时 <code>res</code> 是空串，输出一个空行 → <b>WA</b>。",
]))

SEC.append(REPRO(
    "关掉页面，把 P1143 的代码从零敲一遍提交。第一组数据用 <code>16 / FF / 2</code>，输出应为 11111111。",
    "再打两个边界：<code>2 / 1011 / 10</code> 应得 11；<code>10 / 0 / 16</code> 应得 0（专打特判）。",
    "改一改：把数码表换成全小写 <code>\"0123456789abcdef\"</code>，输出立刻变小写十六进制；但输入也得跟着变小写——"
    "同一张表既要用 <code>find</code> 查字符、又要用下标取字符，大小写必须一致。用 <code>16 / ff / 2</code> 验证。",
    "再改一改：把表扩成 36 个字符 <code>\"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ\"</code>，代码一行都不用动，"
    "输入 <code>36 / Z / 10</code> 就得到 35——这就是表比 if-else 划算的地方。",
    "最后一改：把秦九韶换成“倒着扫、第 i 位重算 n^i”的直白写法，用 18 位输入数一数两种写法各做多少次乘法。"))

# ---------------------------------------------------------------- 数学补给
M = MATH("位权、秦九韶与位数公式", [
    P("设 n 进制数从高到低是 d<sub>k−1</sub>, …, d<sub>0</sub>，它的值就是各位乘自己位权的和："
      "<b>V = d<sub>k−1</sub>·n<sup>k−1</sup> + … + d<sub>1</sub>·n + d<sub>0</sub></b>。"),
    P("秦九韶把它改写成嵌套乘法：<b>V = ((…(d<sub>k−1</sub>·n + d<sub>k−2</sub>)·n + d<sub>k−3</sub>)…·n + d<sub>0</sub></b>。"
      "把括号一层层拆开，每一项的系数与 n 的次数都和上式相同，两者等价。"),
    P("差别只在代价：直白写法每位都要重算一次 n<sup>i</sup>，乘法 0+1+…+(k−1) = k(k−1)/2 次，k = 18 时是 153 次；"
      "秦九韶一次乘加一位，18 次。"),
    P("除基取余的正确性来自带余除法：V = q·m + r，0 ≤ r &lt; m，所以 r 一定是 m 进制写法里的<b>最低位</b>，"
      "q 是“砍掉最低位”后的数。对 q 重复同样的推理，位就从低到高被逐位剥出，因此最后必须倒序。"),
    P("位数估算：k = ⌊log<sub>n</sub> V⌋ + 1。十进制 19 位对应 2⁶³−1 = 9223372036854775807；"
      "同一个值写成二进制要 63 位，写成十六进制只要 16 位——基数越大，位数越少，36 进制因此能把编号压到一半。"),
    P("顺手把“19”推导一遍：2¹⁰ = 1024 ≈ 10³，于是 2⁶³ = (2¹⁰)⁶·2³ ≈ 10¹⁸×8 = 8×10¹⁸，"
      "精确值是 9.223×10¹⁸，刚好落在 10¹⁹ 以下——所以 long long 装得下 19 位、装不下 20 位；"
      "unsigned long long 是 2⁶⁴ ≈ 1.84×10¹⁹，正好 20 位，再多一位也装不下。"),
    P("最后解释那个例外：2、4、8、16 之间可以<b>直接换</b>，不必经过十进制，因为 16 = 2⁴、8 = 2³——"
      "一个十六进制位恰好对应 4 个二进制位。所以 <code>FF</code> 逐位查表就得到 <code>1111 1111</code>。"
      "十六进制在底层代码里流行，正因为它对人可读（8 位一组）对机器整齐（4 位一组）。"),
])

THINK = [
    "P1143 保证“十进制值不超过 10⁹”，所以 long long 中转很安全。若把这条保证删掉、改成“位数不超过 10⁵”，"
    "你的秦九韶还成立吗？除基取余会卡在哪一步？",
    "判断一个 20 位正整数能否被 3 整除，可以全程用字符串。提示：秦九韶不必保留整个数，只保留那部分有用信息就够——推广到 7、13 呢？",
    "给定 10⁵ 个长度不超过 20 的数字串，要求按数值排序。直接用 sort 比字符串为什么错？"
    "先比长度、再比字典序为什么对？有前导零时这个方案会怎样？",
    "洛谷 P1601（高精度加法）为什么不能写成 <code>cout &lt;&lt; a + b</code>？把理由压成一句话。",
    "十六进制在真实世界里至少出现三处：内存地址、颜色 #RRGGBB、哈希。把 <code>\"#FF8800\"</code> 拆成三个 0~255 的整数，"
    "用本节的哪几个函数组合最省事？",
    "判断回文串可以写 <code>s == string(s.rbegin(), s.rend())</code>，也可以双指针首尾对比。两者时间、空间差多少？长度 10⁷ 时哪个会 MLE？",
]

CHECK = [
    "能默写 to_string / stoi / stoll 的签名，并说出各自的位数上限。",
    "能手算 0x3F：秦九韶每一步的值写在纸上（3、63），并说出它是二进制的几位。",
    "知道 reverse 为什么不能直接接在 cout 后面，也说得清它改的是谁。",
    "能解释 find 返回 npos 时为什么不能写成 <code>&lt; 0</code>。",
    "看到“20 位数字”四个字，第一反应是 string 而不是 long long。",
    "能说清除基取余为什么必须倒序输出，并举一个不倒序就错的例子（6 → 110）。",
]

CH = CH(
    "数字反转（升级版）", "P1553", "普及-", "https://www.luogu.com.cn/problem/P1553",
    [P("给定一个不含负号的实数 s，把它的各个数位反转。s 可能是整数、小数、分数或百分数。"),
     P("整数：所有数位对调。小数：整数部分、小数部分各自反转，小数点不动。"
       "分数：分子、分母各自反转，分数线不动，不约分。百分数：只反转数字部分，% 保留。"),
     P("反转后的最高位不能是 0（0 本身除外）；小数部分末尾的 0 要去掉，若只剩 0 则保留一个 0。"),
     P("输入格式：一行，一个实数 s，各段长度最多 20 位。输出格式：一行，s 的反转数。"
       "样例：<code>600.084</code> 得 <code>6.48</code>，<code>700/27</code> 得 <code>7/72</code>。")],
    hint=["四种情况互斥，判别靠串里有没有 %、.、/ 这三个字符，不需要猜数据类型。",
          "整段串里已经有全部信息。先想清楚：能不能把某一段转成数字再反转？数据范围允许吗？",
          "真正要动脑的不是 reverse，而是删零：哪一端是“无意义的 0”，四种情况各不相同。"],
    idea=["① 依次 <code>find('%')</code>、<code>find('.')</code>、<code>find('/')</code>，命中哪个就是哪一类，都没命中就是整数。",
          "② 用 <code>substr</code> 在分隔符两侧切开，左右两段各自 <code>reverse</code>。",
          "③ 左段（整数部分、分子、百分数的数字）去掉反转后开头连续的 0，至少留一位；"
          "右段若是小数部分，去掉反转后末尾连续的 0，也至少留一位；若是分母，按整数规则去掉开头的 0。",
          "④ 拼回去：<code>a + \"%\"</code>、<code>a + \".\" + b</code>、<code>a + \"/\" + b</code>，整数直接输出 a。"
          "全程在 string 里流动，一个字符都不进 long long。",
          "为什么小数部分要删末尾的 0：<code>600.084</code> 的小数段 \"084\" 反转得 \"480\"，"
          "末尾那个 0 由原数的前导 0 变来，是无意义的 0，答案要求 6.48 而不是 6.480。"],
    code=r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    string s;
    cin >> s;                       // 整行只有一个串，不含空格

    size_t p = s.find('%');
    if (p != string::npos) {                    // 百分数：只动数字部分
        string a = s.substr(0, p);
        reverse(a.begin(), a.end());
        int i = 0;
        while (i + 1 < (int)a.size() && a[i] == '0') ++i;  // 去前导零，至少留一位
        cout << a.substr(i) << "%\n";
    } else if ((p = s.find('.')) != string::npos) {        // 小数：两段各管自己
        string a = s.substr(0, p), b = s.substr(p + 1);
        reverse(a.begin(), a.end());
        reverse(b.begin(), b.end());
        int i = 0;
        while (i + 1 < (int)a.size() && a[i] == '0') ++i;  // 整数段去前导零
        int e = (int)b.size() - 1;
        while (e > 0 && b[e] == '0') --e;                  // 小数段去末尾零
        cout << a.substr(i) << "." << b.substr(0, e + 1) << "\n";
    } else if ((p = s.find('/')) != string::npos) {        // 分数：分子分母都按整数
        string a = s.substr(0, p), b = s.substr(p + 1);
        reverse(a.begin(), a.end());
        reverse(b.begin(), b.end());
        int i = 0, j = 0;
        while (i + 1 < (int)a.size() && a[i] == '0') ++i;
        while (j + 1 < (int)b.size() && b[j] == '0') ++j;
        cout << a.substr(i) << "/" << b.substr(j) << "\n";
    } else {                                               // 整数
        reverse(s.begin(), s.end());
        int i = 0;
        while (i + 1 < (int)s.size() && s[i] == '0') ++i;
        cout << s.substr(i) << "\n";
    }
    return 0;
}''',
    explain=[
        ("size_t p = s.find('%');", "先单独算一次，后面三个分支复用 p。用 size_t 接，别用 int。"),
        ("(p = s.find('.')) != string::npos", "赋值表达式的值就是 p，少写一行，也保证 p 只在这个分支里有意义。"),
        ("s.substr(0, p) / s.substr(p + 1)", "分隔符左边取 [0, p)，右边从 p+1 取到结尾，两段长度互不影响。"),
        ("while (i + 1 < (int)a.size() && a[i] == '0') ++i;", "去前导零，但下标最多走到最后一位：保证 \"0\" 这类串不会被删成空串。"),
        ("int e = (int)b.size() - 1; while (e > 0 && b[e] == '0') --e;", "小数段规则相反：删末尾的 0，同样留最后一位。e 是最后一个保留字符的下标。"),
        ("b.substr(0, e + 1)", "取 [0, e]，长度是 e+1 而不是 e。差一错就在这里。"),
        ("a.substr(i)", "只给起点，取到结尾——删完前导零剩下的正是答案。"),
        ("i + 1 < (int)a.size()", "size() 是 size_t（无符号），与 int 比较会有警告，显式转 int 更保险。"),
    ],
    pitfalls=[
        "用 stoll 读整数部分：输入能到 20 位；即使是 19 位的 <code>9223372036854775808</code>，也已超过 LLONG_MAX，"
        "直接抛 out_of_range，评测 <b>RE</b>。",
        "删零删成空串：<code>\"0\"</code> 反转后还是 <code>\"0\"</code>，无条件删前导零会输出空行 → <b>WA</b>。循环条件里必须有 <code>i + 1 &lt; size()</code>。",
        "小数段照抄整数规则去前导零：<code>600.084</code> 会输出 6.480 而不是 6.48。小数段要删的是<b>末尾</b>的 0。",
        "拼回分隔符时手抖：<code>cout &lt;&lt; a &lt;&lt; b</code> 少了小数点，输出 648，只差一个字符，判 <b>WA</b>。",
        "四个分支用四个独立 if 而不是 else if：同一串可能被输出两次，答案多出一行。",
    ],
    sample="输入：\n600.084\n输出：\n6.48\n\n输入：\n700/27\n输出：\n7/72",
)

LESSONS = [LESSON(
    9, "字符串进阶：数字、进制与格式",
    "把字符串当“数字的另一种写法”：用 to_string / stoi / stoll 在两个方向搬运，"
    "用秦九韶与除基取余做任意进制互转，用 find / substr / reverse 切段，并且记住 19 位这条硬红线。",
    60, ["to_string", "进制转换", "find/substr"], "普及-",
    SEC, math=M, think=THINK, check=CHECK, challenge=CH,
    refs=["《算法竞赛入门笔记》字符串与进制转换一章",
          "《算法竞赛试炼场：洛谷300题精析》P1143、P1553 的多解对比",
          "《算法竞赛进阶指南》0x10 基本算法：位运算与进位制",
          "cppreference：std::stoi / std::stoll / std::to_string"],
)]
