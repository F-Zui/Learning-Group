# -*- coding: utf-8 -*-
"""第 08 节 · 字符与字符串基础"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dsl import *  # noqa

SEC = []

SEC.append(P("<b>char 不是字母，是一个 0~127 的整数。</b>'0' 是 48，'A' 是 65，'a' 是 97。"
             "字符题最后只落到两件事：<b>用整数差值把字符映射成下标</b>，<b>用一次遍历扫完整个串</b>。"))

SEC.append(EX("手机按键", "P1765", "普及-", "https://www.luogu.com.cn/problem/P1765",
              ["手机键盘的字母分布：2:abc 3:def 4:ghi 5:jkl 6:mno 7:pqrs 8:tuv 9:wxyz。"
               "在同一个键上按第 n 下，得到这个键上的第 n 个字母（7 键连按 4 下得 s）；空格按 0 键一下。",
               "给定一行只含小写字母和空格的文本（长度不超过 200），求打出它最少要按多少下键。",
               "输入格式：一行文本。输出格式：一行一个整数。"],
              sample="输入：\nhello world\n输出：\n25"))

SEC.append(P("先记三组连续区间。区间<b>内部</b>编码连续，这是所有字符题的地基。"))
SEC.append(T(["区间", "ASCII 码", "长度", "取序号", "用途"], [
    ["'0' ~ '9'", "48 ~ 57", "10", "c - '0'", "数字字符 → 0~9"],
    ["'A' ~ 'Z'", "65 ~ 90", "26", "c - 'A'", "大写字母 → 0~25"],
    ["'a' ~ 'z'", "97 ~ 122", "26", "c - 'a'", "小写字母 → 0~25"],
    ["'a' - 'A'", "32", "—", "c ^ 32", "大小写互换"],
]))
SEC.append(Q("字符题只有两种操作：把字符变成下标，把下标变成字符。"))
SEC.append(P("两条推论：① 区间内第 k 个字符 = 首字符 + k，所以 <code>c - 'a'</code> 直接就是 0~25 的下标；"
             "② 区间之间不连续——'9'+1 是 ':'，'Z'+1 是 '['。判断一个字符属于哪一组，两头都要写。"))

# ---------------------------------------------------------------- 新函数
SEC.append(FN(
    "getline（读一整行）",
    "std::getline(std::cin, s);",
    [("std::cin", "从标准输入流读，换成 ifstream 就是读文件。"),
     ("s", "整行内容存进来，<b>不含结尾的 '\\n'</b>。"),
     ("停在哪", "遇 '\\n' 结束，并把它从缓冲区取走。"),
     ("返回值", "流本身，所以能写 <code>while (getline(cin, s))</code>。")],
    example=r'''string s;
getline(cin, s);        // 输入 hello world → 11 个字符全进来
cout << s.size();       // 11

cin >> s;               // 只读到第一个词，停在空格
getline(cin, s);        // 读到的是剩下的 " world"''',
    notes=["<code>cin &gt;&gt; s</code> 遇空格就停，含空格的整行只能用 getline。",
           "两者混用时缓冲区残留的换行必须先吃掉，见下一张卡。"],
    brief="整行读入，含空格文本的唯一选择"))

SEC.append(FN(
    "cin.ignore（清掉残留）",
    "cin.ignore();\ncin.ignore(n, '\\n');",
    [("无参", "吃掉 1 个字符。常用法就是吃掉 <code>cin &gt;&gt; n</code> 后面那个换行。"),
     ("两参", "最多吃掉 n 个字符，遇 '\\n' 提前停（'\\n' 一并吃掉）。"),
     ("为什么需要", "cin &gt;&gt; 读数字遇空白就停，<b>不把空白取走</b>。残留换行会让下一次 getline 读到空串。")],
    example=r'''int n;
cin >> n;               // 输入 3，缓冲区还剩一个 '\n'
cin.ignore();           // 吃掉它
string s;
getline(cin, s);        // 现在读到的才是真正的第 2 行''',
    notes=["漏了这句的症状固定：getline 读到空串，后面所有数据全部错位。",
           "全程只用 cin &gt;&gt; 的程序不需要它。"],
    brief="cin 与 getline 混用的必备补丁"))

SEC.append(FN(
    "string::size / length（长度）",
    "size_t s.size();",
    [("返回值", "字符个数。结尾的 '\\0' 由 string 内部维护，不计入。"),
     ("类型", "size_t，<b>无符号</b>整数，和 int 混用会出坑。"),
     ("等价写法", "<code>s.length()</code> 完全一样；判断空串用 <code>s.empty()</code>。")],
    example=r'''string s = "abc";
cout << s.size();       // 3

// ★ 经典坑：s 为空时 s.size() - 1 回绕成 1.8e19，当下标用直接 RE
int n = (int)s.size();                    // 先转成有符号
for (int i = n - 1; i >= 0; --i) cout << s[i];   // 倒序输出''',
    notes=["s 为空时 <code>s.size() - 1</code> 等于 18446744073709551615。",
           "把 size 存进 int 后，所有下标运算都是带符号的，倒序循环才不会变死循环。"],
    brief="字符个数，注意返回无符号数"))

SEC.append(FN(
    "范围 for（新语法）",
    "for (char c : s) { }\nfor (char &c : s) { }",
    [("char c", "<b>副本</b>。循环体里改 c 不影响 s，适合只读统计。"),
     ("char &amp;c", "<b>引用</b>，绑定在 s 的元素上。给 c 赋值就是改 s。"),
     ("const char &amp;c", "只读又不拷贝。char 拷贝代价极小，结构体才必须这么写。"),
     ("数组也能用", "<code>for (int &amp;x : a) cin &gt;&gt; x;</code> 一次读完数组。")],
    example=r'''string s = "Hello, World";
int letters = 0;
for (char c : s) if (isalpha(c)) ++letters;   // 只读：c 是副本

for (char &c : s) c = toupper(c);             // 要改：加 & ，c 是 s 里的字符
cout << s;                                    // HELLO, WORLD

for (char c : s) c = tolower(c);              // ✗ 改副本，s 一个字符都没变''',
    notes=["判断标准只有一条：<b>要不要改原串</b>，要改就加 &amp;。",
           "循环体里不要 push_back 或删除元素，长度一变遍历就失效。"],
    brief="遍历容器的简写法，改原串要加引用"))

SEC.append(FN(
    "isdigit（是不是数字字符）",
    "int isdigit(int ch);",
    [("参数", "字符的整数编码，直接把 char 传进去。"),
     ("返回", "是 '0'~'9' 返回非 0（真），否则 0。"),
     ("只认什么", "只认这 10 个字符，不认 '+', '-', '.', 空格。")],
    example=r'''cout << isdigit('7');    // 非 0
cout << isdigit(' ');    // 0
cout << '7' - '0';       // 7：字符转数值靠减法''',
    notes=["返回值是 int，当布尔用，别赋给 char；等价写法是两头都判断的区间比较。"],
    brief="判断 '0'~'9'，返回真假"))

SEC.append(FN(
    "isalpha（是不是字母）",
    "int isalpha(int ch);",
    [("返回", "是 'A'~'Z' 或 'a'~'z' 返回非 0，否则 0。"),
     ("同族", "isalnum、isspace、islower、isupper、ispunct 用法相同。"),
     ("为什么用它", "自己写区间判断容易漏边界，标准库不会错。")],
    example=r'''string s = "Luogu 2024";
int letters = 0, digits = 0, other = 0;
for (char c : s) {
    if (isalpha(c)) ++letters;
    else if (isdigit(c)) ++digits;
    else ++other;
}
// 5 4 1''',
    notes=["别写成 <code>c &gt;= 'A' &amp;&amp; c &lt;= 'z'</code>：'[' '\\' ']' '^' '_' '`' 这 6 个会被误判成字母。"],
    brief="判断英文字母，大小写都算"))

SEC.append(FN(
    "tolower（转小写）",
    "int tolower(int ch);",
    [("行为", "大写字母返回对应小写；其他字符原样返回。"),
     ("返回类型", "int。写 <code>c = (char)tolower(c);</code> 最稳。"),
     ("不改原值", "它只返回新字符，<code>tolower(c);</code> 单独一句等于什么都没做。")],
    example=r'''cout << (char)tolower('Q');       // q

string s = "Luogu";
for (char &r : s) r = tolower(r);  // 加 & 才改到原串
cout << s;                        // luogu

char d = 'Q';
tolower(d);                       // ✗ d 仍是 'Q'
''',
    notes=["最常见的错：<code>for (char c : s) c = tolower(c);</code> 改的是副本，原串一点没变。"],
    brief="大写转小写，返回新字符"))

SEC.append(FN(
    "toupper（转大写）",
    "int toupper(int ch);",
    [("行为", "小写字母返回对应大写；其他字符原样返回。"),
     ("与 tolower 对称", "都是“输入一个编码，输出一个编码”，不就地修改。"),
     ("典型场景", "把整行统一成一种大小写，之后只按一种形式比较——所有“不区分大小写”题的第一步。")],
    example=r'''string a = "Hello", b = "WORLD";
for (char &c : a) c = toupper(c);   // HELLO
for (char &c : b) c = tolower(c);   // world
cout << a << " " << b;              // HELLO world''',
    notes=["统一大小写只做一次就够，不要在每次比较里都调；对数字和空格调用无副作用。"],
    brief="小写转大写，返回新字符"))

# ---------------------------------------------------------------- 例题
SEC.append(IDEA("例题怎么想：把“按几下”做成一张 26 元表", [
    P("题目只问总按键数，与字符顺序无关——每个字符的贡献互不影响，一次累加即可。"
      "难点只剩“字符 → 次数”这个映射：键盘是死的，把 a~z 各自的次数按字母顺序写成数组，"
      "用 <code>c - 'a'</code> 当下标，一次数组访问就查完，比 8 个 if 又快又不容易写错。"),
    L(["① 用 getline 读整行（含空格，cin &gt;&gt; 只能读到第一个词）。",
       "② 准备 <code>int press[26]</code>，press[i] 是第 i 个字母的按键次数。",
       "③ 遍历：空格贡献 1，字母贡献 press[c - 'a']；④ 输出累加值。"]),
    C(r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string s;
    getline(cin, s);            // 一行含空格，只能整行读

    // press[i]：打出第 i 个字母（a 记 0）要按几下
    // a b c | d e f | g h i | j k l | m n o | p q r s | t u v | w x y z
    int press[26] = {1,2,3, 1,2,3, 1,2,3, 1,2,3, 1,2,3,
                     1,2,3,4, 1,2,3, 1,2,3,4};

    int ans = 0;
    for (char c : s) {              // 只读，不加 & ，c 是副本
        if (c == ' ') ans += 1;     // 空格按 0 键一下
        else ans += press[c - 'a']; // ASCII 连续 ⇒ 下标 = c - 'a'
    }

    cout << ans << "\n";
    return 0;
}''', "完整代码：26 元查表"),
    EXPLAIN("逐行拆解", [
        ("getline(cin, s);", "本题用 getline 的唯一理由：一行里含空格。用 cin &gt;&gt; s 只会拿到第一个词。"),
        ("int press[26]", "26 个数对应 a~z。手写表出错时错误集中在表里，一眼能查；比一堆 if 快。"),
        ("{1,2,3, 1,2,3, ...}", "每 3 个一组，pqrs 和 wxyz 是 4 个一组——这两组有 4 个字母，所以表里出现 4。"),
        ("for (char c : s)", "只读遍历，不加引用。c 是副本，改不动 s，而本题也不需要改。"),
        ("if (c == ' ')", "空格必须单独处理：它落在 'a' 左侧，直接算 c - 'a' 会得到 -65 这类负下标。"),
        ("press[c - 'a']", "三组连续性最直接的用法：'a'-'a'=0，'z'-'a'=25，字母序号就是下标。"),
        ("cout << ans << \"\\n\";", "只输出数字，不加任何提示语。"),
    ]),
]))

SEC.append(AFTER("另一种建表：8 个字符串", [
    P("也可以把键盘存成 <code>string key[10] = {\"\", \"\", \"abc\", \"def\", ...}</code>，"
      "每个字符去 8 组里找自己在第几位。它不用手抄 26 个数字，代价是每字符最多 32 次比较——"
      "n ≤ 10<sup>6</sup> 时也只有 3×10⁷ 次，照样过。所以选哪个只看你更不容易写错。"),
]))

SEC.append(WARN("这一节最常见的 5 个错（附症状）", [
    "<b>WA，答案总是偏小</b>：用 <code>cin &gt;&gt; s</code> 读含空格的整行，只拿到第一个词，<code>s.size()</code> 永远等于词长。",
    "<b>WA，读到空串</b>：<code>cin &gt;&gt; n</code> 后直接 getline，读到残留换行。补 <code>cin.ignore();</code>。",
    "<b>RE 或答案是个天文数字</b>：大写字母、空格代进 <code>press[c - 'a']</code>，下标为负，访问到数组外。",
    "<b>TLE / RE</b>：<code>for (int i = s.size() - 1; i &gt;= 0; --i)</code>。s 为空时 size()-1 回绕成 1.8×10¹⁹，"
    "i 转 int 后变负，条件恒真，越界读到崩。先把 size 存进 int。",
    "<b>WA，字符串没变</b>：<code>for (char c : s) c = tolower(c);</code> 改的是副本，加 <code>&amp;</code>。",
]))

SEC.append(REPRO(
    "关掉本页，把上面的完整代码从头敲一遍，提交 P1765，AC 了再往下。",
    "改一改 ①：输入换成含大写的 <code>Hello World</code>，先猜答案再运行；然后加一行 "
    "<code>for (char &amp;c : s) c = tolower(c);</code>，看结果变不变。",
    "改一改 ②：题目改成“输出 2~9 每个数字键各被按了多少次”，用 <code>int cnt[10]</code> 边算边统计。",
    "改一改 ③：先读整数 n，再读 n 行文本求和。故意删掉 <code>cin.ignore()</code> 跑一次，亲眼看它读空。",
))

# ---------------------------------------------------------------- 数学补给
M = MATH("为什么大小写只差 32", [
    P("把三组区间写成二进制，规律立刻出来："),
    T(["字符", "十进制", "二进制", "区间长度"], [
        ["'0'", "48", "011 0000", "—"],
        ["'9'", "57", "011 1001", "10 个"],
        ["'A'", "65", "100 0001", "—"],
        ["'Z'", "90", "101 1010", "26 个"],
        ["'a'", "97", "110 0001", "—"],
        ["'z'", "122", "111 1010", "26 个"],
    ]),
    P("'A' 与 'a' 只差第 5 位（权重 32）：100 0001 对 110 0001。'Z' 与 'z' 同样只差这一位，"
      "所以字母在编码表里的相对位置完全一致，这才有 <code>'a' - 'A' = 32</code>。"),
    L(["<code>tolower(c)</code>：标准库，最清楚，推荐。",
       "<code>c | 32</code>：把第 5 位置 1。大写变小写，小写不变，但它<b>不检查</b>字符是不是字母。",
       "<code>c &amp; 32</code>：看第 5 位。'a' 得 32，'A' 得 0——但 '0' = 011 0000 也得 32，会被误判成小写。",
       "<code>c + 32</code>：只对大写成立，小写字母会跑出区间。"]),
    P("数字字符同理：'0' = 48 是区间起点，<code>c - '0'</code> 直接得 0~9；反过来写 <code>d + '0'</code>，"
      "别写 <code>d + 48</code>——前者与编码表无关，后者只在 ASCII 上成立。"),
    P("循环移位是同一套想法：<code>(c - 'a' + k) % 26 + 'a'</code> 把整数轴折成长度 26 的环，'z' 后一位自动回到 'a'。"
      "k 可能为负时要写 <code>((c - 'a' + k) % 26 + 26) % 26 + 'a'</code>，因为 C++ 的 % 对负数取余仍是负的。"),
])

THINK = [
    "除了 26 元 int 表，还能用 8 个字符串查表。两种写法的比较次数、抄错风险、扩展到 100 个字符时的代价各是什么？",
    "为什么 getline 要把 '\\n' 取走却不把它放进 string？如果它放进去了，本节两道题分别会出什么错？",
    "把长度不超过 18 的数字字符串变成 long long，循环怎么写？若长度到 10⁵ 位还能用这个办法吗——这是第 9 节要解决的问题。",
    "<code>c &amp; 32</code> 对 'A'、'0'、'@' 分别返回什么？为什么这三个结果说明用位运算判断大小写之前必须先 isalpha？",
    "统计单词时把“左右是空格”改成“左右不是字母”，文章里出现逗号、句号、换行时哪种写法更稳？各举一个反例。",
    "同样是 O(n) 扫描，为什么字符题常常边读边算就够，而不必先存整个串？什么情况下必须先存下来？",
]

CHECK = [
    "能默写三组 ASCII 区间的端点与长度（10 / 26 / 26），并说出 'a' - 'A' 等于多少。",
    "能写出“先读整数 n，再读一整行文本”的正确代码，并解释 cin.ignore() 为什么不能省。",
    "能说出 <code>for (char c : s)</code> 与 <code>for (char &amp;c : s)</code> 的区别，各举一个该用的场景。",
    "能解释 s 为空时 <code>s.size() - 1</code> 为什么会出事，并给出两种安全写法。",
    "能用 isalpha / isdigit / isspace 写出“一行里字母、数字、其他各多少个”。",
    "能不看资料写出 P1765 的完整代码并一次 AC。",
]

CH = CH(
    "统计单词数", "P1308", "普及-", "https://www.luogu.com.cn/problem/P1308",
    [P("给定一个单词和一篇文章，统计它作为<b>独立单词</b>出现了多少次，以及第一次出现的位置。"
       "匹配不区分大小写；若它只是一个更长单词的一部分（to 出现在 today 里），不算。"),
     P("输入格式：第 1 行一个只含字母的字符串，表示单词（长度不超过 10）；"
       "第 2 行一个只含字母和空格的字符串，表示文章（长度不超过 10<sup>6</sup>）。"),
     P("输出格式：一行。出现过则输出两个整数——出现次数与第一次出现的位置（文章第一个字符的位置记为 0）；"
       "从未出现则输出 -1。")],
    hint=["大小写不影响匹配。先把两行统一成同一种大小写，再讨论比较；想想这一步要不要改到原串上。",
          "一次“算作出现”要同时满足两件事：从这个位置起的若干字符完全相同，并且前后都不是单词的字母。",
          "位置从 0 开始数：文章第一个字符是位置 0，不是 1。"],
    idea=["用 getline 读两行：第 2 行含空格，cin &gt;&gt; 只能拿到第一个词。",
          "两串都转小写，之后只比较一种形式。",
          "枚举起点 i（0 ≤ i ≤ n-m），逐字符比较 text[i..i+m-1] 与 word[0..m-1]。",
          "全同后再查边界：左边是 i == 0 或 text[i-1] == ' '，右边是 i+m == n 或 text[i+m] == ' '。",
          "两边都满足才计数，第一次满足时记下 i。复杂度 O(n·m) ≤ 10⁷。"],
    code=r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string word, text;
    getline(cin, word);          // 第 1 行：要查的单词
    getline(cin, text);          // 第 2 行：文章，含空格

    // 统一转小写。必须用引用，否则改的是副本，原串一点没动
    for (char &c : word) c = tolower(c);
    for (char &c : text) c = tolower(c);

    int n = (int)text.size(), m = (int)word.size();
    int cnt = 0, first = -1;     // first = -1 表示没出现，0 是合法位置

    for (int i = 0; i + m <= n; ++i) {       // i 是起点，保证 i+m-1 < n
        bool same = true;
        for (int j = 0; j < m; ++j)          // 手写比较，省一次子串拷贝
            if (text[i + j] != word[j]) { same = false; break; }
        if (!same) continue;

        // 完整单词：左边是开头或空格，右边是结尾或空格
        // || 的先后不能换：i == 0 时不能去访问 text[-1]
        bool leftOK  = (i == 0)     || (text[i - 1] == ' ');
        bool rightOK = (i + m == n) || (text[i + m] == ' ');

        if (leftOK && rightOK) {
            ++cnt;
            if (first == -1) first = i;      // 只记第一次
        }
    }

    if (cnt == 0) cout << -1 << "\n";
    else          cout << cnt << " " << first << "\n";
    return 0;
}''',
    explain=[
        ("getline(cin, word);", "第一行没有空格也用 getline，省掉“cin &gt;&gt; 之后要不要 ignore”的判断。"),
        ("for (char &c : word) c = tolower(c);", "引用绑定到原串元素才改得动；漏掉 &amp; 就全场 0 次。"),
        ("i + m <= n", "起点上限。写成 i &lt; n 会越界访问 text[i+m-1]。"),
        ("text[i + j] != word[j]", "逐字符比较，不同就立刻 break。"),
        ("(i == 0) || (text[i - 1] == ' ')", "短路求值：i 为 0 时右边不执行，不会访问 text[-1]。调换顺序就在第一个单词上越界。"),
        ("(i + m == n) || (text[i + m] == ' ')", "右边界。漏掉它，to 会把 today 开头的 to 也算一次。"),
        ("first == -1", "用 -1 表示“没出现”，因为位置 0 是合法的。"),
    ],
    pitfalls=[
        "用 <code>cin &gt;&gt; text</code> 读文章，只拿到第一个词，答案几乎是 0。",
        "转小写忘写 <code>&amp;</code>，word 仍是大写，任何输入都匹配不上，输出 -1。",
        "先写 text[i-1] 再判 i == 0，下标 -1 越界读，拿到随机值。",
        "只判左边界不判右边界：文章 “today to” 会把 today 开头的 to 也算一次。",
        "位置从 1 数起，答案整体差 1。",
    ],
    sample="输入：\nTo\nto be or not to be is a question\n输出：\n2 0",
)

LESSONS = [LESSON(
    8, "字符与字符串基础",
    "把 char 当整数、把 string 当数组：掌握 ASCII 三组连续区间、getline 与 cin.ignore 的配合、"
    "cctype 工具箱，以及范围 for 中引用与非引用的差别。",
    55, ["ASCII", "getline", "cctype"], "入门",
    SEC, math=M, think=THINK, check=CHECK, challenge=CH,
    refs=["《算法竞赛入门笔记》第 3 章：字符与字符串",
          "《算法竞赛黄金法则：提高算法和思考力的77项技巧》：把字符当整数看",
          "洛谷 P1765、P1308 题解区的高赞思路"],
)]
