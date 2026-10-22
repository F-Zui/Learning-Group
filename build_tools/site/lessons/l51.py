# -*- coding: utf-8 -*-
"""第 51 节 · 字符串哈希与 Trie"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dsl import *  # noqa

SEC = []

SEC.append(P("字符串题只有两个基本动作：<b>比较</b>和<b>查找</b>。直接比较两个长 L 的串要 L 次字符比较；"
             "一万个长 1000 的串两两比较是 5×10<sup>10</sup> 次，必然超时。"
             "这一节给两种把动作变便宜的工具：<b>哈希</b>把整个串压成一个整数，比较退化成一次整数比较；"
             "<b>Trie</b> 把公共前缀折叠成一条路径，插入和查询都只走 L 步。"
             "Trie 的一个变体把整数按二进制位建树，就能回答“和 x 异或最大的数是谁”。"))

SEC.append(Q("哈希回答“这两个串一样吗”，Trie 回答“这个前缀出现过几次”，"
             "01-Trie 回答“和 x 异或最大的数是谁”。三个问题，一条共同的思路：把串或数变成可以随手比较、随手走几步的东西。"))

SEC.append(T(["任务", "规模", "工具", "单次操作", "主要风险"], [
    ["判断两个串是否相等", "长 10<sup>6</sup>，比较 10<sup>5</sup> 次", "多项式哈希", "O(1)", "哈希冲突 → 判成相等"],
    ["求子串 [l, r] 的指纹", "长 10<sup>6</sup>，询问 10<sup>5</sup> 次", "前缀哈希 + 幂表", "O(1)", "同上"],
    ["插入 / 查询一个串", "总长 10<sup>6</sup>", "Trie", "O(len)", "数组开小 → RE"],
    ["和 x 异或最大的数", "n ≤ 10<sup>5</sup>，值 &lt; 2<sup>31</sup>", "01-Trie", "O(31)", "位宽取错 → WA"],
]))

SEC.append(P("先把这一节会出现的 4 样东西拆开。它们都很短，但每一件都有一个“不这么写就错”的细节，"
             "这四处细节才是真正的考点。"))

# ---------------------------------------------------------------- 新东西
SEC.append(FN(
    "unsigned long long（无符号 64 位整数）",
    "typedef unsigned long long ull;\n\null h = 0;\nfor (char c : s) h = h * B + (ull)c;   // 溢出即取模",
    [("取值范围", "0 ~ 2<sup>64</sup>−1 = 18446744073709551615，20 位十进制。"),
     ("自然溢出", "无符号整数的运算按 2<sup>64</sup> 取模：溢出的高位被硬件直接丢弃，不用写 %。"),
     ("为什么快", "取模 % 是一条除法指令，10~40 个时钟周期；乘法和丢弃高位只要 1 个。10<sup>6</sup> 次哈希能差 3 倍时间。"),
     ("换成 long long 会怎样", "有符号整数溢出是未定义行为（UB）。编译器可以假设它不会发生，"
                                 "在 -O2 下把比较优化掉，同一份代码本地对、交上去错。"),
     ("写法", "h = h * B + (ull)c；先把 char 转成无符号再加，字符值 ≥ 128 时才不会被符号扩展成负数。"),
     ("怎么观察它", "cout 直接输出十进制；<code>ull x = 0; --x;</code> 得到 18446744073709551615。")],
    example=r'''#include <bits/stdc++.h>
using namespace std;
typedef unsigned long long ull;

int main() {
    ull x = 0;
    --x;                              // 0 - 1 回绕到 2^64 - 1
    cout << x << "\n";                // 18446744073709551615

    string s = "abc";
    ull h = 0;
    for (char c : s) h = h * 131 + (ull)c;   // 等价于 (h * 131 + c) % 2^64
    cout << h << "\n";

    // 同一个函数对 "abc" 永远给出同一个数，这就是“指纹”
    return 0;
}''',
    notes=["减法也回绕：<code>ull a = 1, b = 2; a - b</code> 得到 1.8×10<sup>19</sup>，不是 −1。"
           "哈希里大量用到“减法回绕”，这正是子串哈希公式能成立的原因。",
           "把 ull 换成 long long，h * 131 一旦超过 9.2×10<sup>18</sup> 就是 UB，"
           "g++ 可能直接按“不溢出”优化，结果无法预测。"],
    brief="64 位无符号整数，模 2^64 的取模由硬件免费完成"))

SEC.append(FN(
    "双哈希（两套模数各算一遍）",
    "pair<long long, long long> H(const string& s);",
    [("为什么一个不够", "模 2<sup>64</sup> 且基数固定时，存在确定的构造性攻击（Thue–Morse 串）。"
                        "洛谷 P3370 的“拓展阅读”里整排 Hash Killer 就是干这个的。"),
     ("做法", "对同一个串，用两组 (模数, 基数) 各算一个值，组成 pair 一起比较。"),
     ("模数怎么选", "两个互不相同的大质数：10<sup>9</sup>+7 与 10<sup>9</sup>+9，或 998244353 与 10<sup>9</sup>+7。"),
     ("基数怎么选", "大于字符集（62），常用质数 131、13331。两套的基数也要不同，否则等于一个哈希算两遍。"),
     ("比较方式", "pair 自带 operator&lt; 和 operator==（先比 first，再比 second），可以直接 sort、unique、放 set。"),
     ("代价", "常数 ×2，代码多三行。字符串题里这是最便宜的保险。")],
    example=r'''#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

const ll M1 = 1000000007, M2 = 1000000009;    // 两个不同的大质数
const ll B1 = 131,        B2 = 13331;        // 两套基数也要不同

pair<ll, ll> H(const string& s) {
    ll h1 = 0, h2 = 0;
    for (unsigned char c : s) {              // 转无符号，防止负字符
        h1 = (h1 * B1 + c) % M1;
        h2 = (h2 * B2 + c) % M2;
    }
    return {h1, h2};
}

int main() {
    vector<pair<ll, ll>> v = {H("abc"), H("abc"), H("abd")};
    sort(v.begin(), v.end());
    cout << unique(v.begin(), v.end()) - v.begin() << "\n";   // 2
    return 0;
}''',
    notes=["两个模数都取 10<sup>9</sup> 量级，乘积约 10<sup>18</sup>；随机数据下 n = 10<sup>5</sup> 个串的期望冲突数约 5×10<sup>−9</sup>。",
           "别用 998244353 与 10<sup>9</sup>+7 配同一个基数——基数相同会让两个哈希产生关联，安全性下降。",
           "更狠的一招是运行时随机基数：<code>B = chrono::steady_clock::now().time_since_epoch().count() | 1</code>，"
           "出题人无法预先构造。"],
    brief="两套模数 + 两套基数，把冲突概率压到可以忽略"))

SEC.append(FN(
    "Trie（字典树）的数组实现",
    "int ch[MAXN][26];\nint pass[MAXN], ended[MAXN], tot = 0;",
    [("ch[u][c]", "节点 u 沿字符 c 这条边走到的节点编号。0 表示这条边不存在；根固定是 0，所以节点编号从 1 开始分配。"),
     ("tot", "已分配的节点数，也是最新节点的编号。新建节点就是 <code>ch[u][x] = ++tot</code>。"),
     ("pass[u]", "有多少个串经过节点 u，也就是“以该节点对应的字符串为前缀的串数”。"),
     ("ended[u]", "有多少个串恰好结束在 u。用来区分“是某个串的前缀”和“自己就是一个串”。"),
     ("空间怎么估", "节点数 = 所有串的总长度 + 1。ch 占 MAXN×26×4 字节：总长 10<sup>5</sup> 约 10 MB，总长 10<sup>6</sup> 约 104 MB。"),
     ("为什么不用指针", "new 一次约 100 字节开销还慢。数组连续分配，缓存友好，清空只要 memset(ch, 0, sizeof ch)，多测方便。")],
    example=r'''#include <bits/stdc++.h>
using namespace std;

const int MAXN = 100005;                 // 节点上限 = 总字符数 + 1
int ch[MAXN][26], pass[MAXN], ended[MAXN], tot = 0;

void insert(const string& s) {
    int u = 0;                           // 从根出发
    for (char c : s) {
        int x = c - 'a';
        if (!ch[u][x]) ch[u][x] = ++tot; // 边不存在才新建，这是“共享前缀”的全部秘密
        u = ch[u][x];
        ++pass[u];
    }
    ++ended[u];                          // 有一个串在这里结束
}

int node(const string& s) {              // 返回路径终点；-1 表示走不通
    int u = 0;
    for (char c : s) {
        int x = c - 'a';
        if (!ch[u][x]) return -1;
        u = ch[u][x];
    }
    return u;
}
// node(s) != -1 → 以 s 为前缀的串有 pass[node(s)] 个
// ended[node(s)] > 0 → s 本身是一个插入过的串''',
    notes=["0 号既当根又当“不存在的边”，所以判定必须是 <code>if (!ch[u][x])</code>，而不是 <code>== -1</code>"
           "（全局数组默认 0，拿 -1 判永远不成立，会把 0 当合法子节点原地打转）。",
           "节点总数只与总字符数有关，与字符集大小无关——这正是 Trie 比“把所有前缀塞进 set”省的地方。"],
    brief="插入与查询各走 len 步，公共前缀只存一份"))

SEC.append(FN(
    "01-Trie（二进制 Trie）",
    "void insert(int x);\nint query(int x);      // 返回与 x 异或能取到的最大值",
    [("节点含义", "从根往下第 b 层存的是 x 的第 b 位（b 从 30 降到 0）。一条根到叶的路径就是一个 31 位二进制数。"),
     ("ch[u][2]", "只有 0、1 两条边。节点数上限 = 数值个数 × 31。"),
     ("query 的贪心", "从高位到低位，尽量走与当前位<b>相反</b>的边；走不通才走相同的边。"),
     ("为什么贪心对", "第 b 位是 1 贡献 2<sup>b</sup>，而低 b 位全取 1 也只有 2<sup>b</sup>−1。高位赢一次就赢过所有低位，所以从高到低逐位定。"),
     ("位宽", "值 &lt; 2<sup>31</sup> 时从第 30 位开始；值 &lt; 10<sup>9</sup> &lt; 2<sup>30</sup> 时从第 29 位开始也够。多枚举一位不会错，只多一层。")],
    example=r'''const int MAXN = 100005;
int ch[MAXN * 31][2], tot = 0;

void insert(int x) {
    int u = 0;
    for (int b = 30; b >= 0; --b) {
        int c = (x >> b) & 1;
        if (!ch[u][c]) ch[u][c] = ++tot;
        u = ch[u][c];
    }
}

int query(int x) {                       // 与 x 异或的最大值
    int u = 0, r = 0;
    for (int b = 30; b >= 0; --b) {
        int c = (x >> b) & 1;
        if (ch[u][c ^ 1]) {              // 反边存在：这一位异或出 1
            r |= 1 << b;
            u = ch[u][c ^ 1];
        } else {                         // 只能将就，这一位异或出 0
            u = ch[u][c];
        }
    }
    return r;
}''',
    notes=["插入和查询都是 31 步固定开销，与数值大小无关。",
           "ch 占 3.1×10<sup>6</sup>×2×4 ≈ 25 MB，n = 10<sup>5</sup> 时刚好；n 再大就要算清楚内存。"],
    brief="把整数按二进制位存成树，31 步求出最大异或"))

# ---------------------------------------------------------------- 例题
SEC.append(EX("【模板】字符串哈希", "P3370", "普及-", "https://www.luogu.com.cn/problem/P3370",
              ["给定 N 个字符串（第 i 个长度为 M<sub>i</sub>），字符串内只含数字与大小写字母，<b>大小写敏感</b>。"
               "请求出这 N 个字符串中共有多少个<b>不同</b>的字符串。",
               "输入：第一行一个整数 N；接下来 N 行，每行一个字符串。",
               "输出：一行一个整数，表示不同字符串的个数。",
               "数据范围：N ≤ 10000，M<sub>max</sub> ≤ 1500（总字符数可达 1.5×10<sup>7</sup>）。"],
              sample="输入：\n5\nabc\naaaa\nabc\nabcc\n12345\n输出：\n4"))

SEC.append(IDEA("例题怎么想：先把串变成整数，再去重", [
    "朴素做法：读进 N 个串，两两比较是否相同。N = 10<sup>4</sup> 时约 5×10<sup>7</sup> 对，"
    "每对最多比 1500 个字符，最坏 7×10<sup>10</sup> 次字符比较，TLE。",
    "换目标：题目只问“有几个不同的串”，不问“谁和谁相同”。于是可以给每个串算一个整数指纹，"
    "把“字符串去重”降级成“整数去重”。",
    P("指纹怎么算：把串看成一个 B 进制数。<code>h = 0; for (c : s) h = h * B + c;</code>。"
      "长度 3 的 <code>abc</code> 展开是 a·B<sup>2</sup> + b·B + c，与按位权展开一致。"
      "只要 B 大于字符集（62），不同串在<b>不取模</b>时必然得到不同的整数——这就是“指纹”能表示串的原因。"),
    "取模是为了把整数压进 64 位。取模会丢信息，于是不同串可能落到同一个余数上，这叫哈希冲突。"
    "模 2<sup>64</sup>、随机数据、N = 10<sup>4</sup> 时，期望冲突对数约 N<sup>2</sup>/(2·2<sup>64</sup>) ≈ 3×10<sup>−12</sup>，可以忽略。",
    "去重：N 个整数排序，再 unique 一遍。unique 把不重复的元素挪到前面并返回新的逻辑结尾，"
    "减去 begin 就是不同元素个数。总复杂度 O(N log N)，与串长无关。",
    C(r'''读入 n
for 每个串 s:
    h = 0
    for c in s: h = h * 131 + c      # 溢出即 mod 2^64
    把 h 存进数组
排序、unique
输出 unique 之后的元素个数''', "四步"),
    P("两处细节：<b>h 必须无符号</b>（有符号溢出是 UB）；<b>unique 之前必须排序</b>（它只消除相邻重复）。"),
]))

SEC.append(C(r'''#include <bits/stdc++.h>
using namespace std;
typedef unsigned long long ull;

const ull B = 131;          // 基数：大于字符集(62)，且是质数

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<ull> h;
    h.reserve(n);

    string s;
    for (int i = 0; i < n; ++i) {
        cin >> s;
        ull x = 0;
        // 每个串独立从 0 开始累；乘 131 后的溢出位被丢弃，正是 mod 2^64
        for (char c : s) x = x * B + (ull)c;
        h.push_back(x);
    }

    sort(h.begin(), h.end());              // 整数排序，比字符串比较便宜得多
    // unique 把不重复的元素挪到前面，返回新结尾；减去 begin 即个数
    cout << (int)(unique(h.begin(), h.end()) - h.begin()) << "\n";
    return 0;
}''', "完整代码"))

SEC.append(EXPLAIN("逐行拆解", [
    ("typedef unsigned long long ull;", "64 位无符号。哈希的取模靠它自然溢出，一次 % 都不写。"),
    ("const ull B = 131;", "基数必须大于字符集大小。取 B = 1 时 <code>ab</code> 与 <code>ba</code> 哈希都是 a+b，"
                           "取 B = 2 时重排也会撞。质数让各次幂分布更散。"),
    ("ios::sync_with_stdio(false);", "总输入 1.5×10<sup>7</sup> 个字符，读入本身是瓶颈之一，关同步省一半时间。"),
    ("ull x = 0;", "写在读串的循环内，保证每个串的累加器是干净的。写在循环外会让所有串首尾相连。"),
    ("for (char c : s) x = x * B + (ull)c;", "核心一行：先乘再加，等价于把串看成 B 进制数。"
                                             "(ull) 转换保证字符值 ≥ 128 时不做符号扩展。"),
    ("x * B 溢出为什么不算错", "无符号溢出是“按 2<sup>64</sup> 取模”，C++ 标准明确规定；"
                              "换 long long 就是 UB。同一个式子，类型决定它是算法还是未定义行为。"),
    ("h.push_back(x);", "N 个指纹存进 vector，长度只有 N，与串长无关。"),
    ("sort(h.begin(), h.end());", "O(N log N)，比较的是 8 字节整数。若直接 sort 字符串，比较代价是 O(串长)。"),
    ("unique(h.begin(), h.end()) - h.begin()", "unique 返回去重后区间的新结尾。前提是已经有序，"
                                               "否则只消除相邻重复，答案偏大。"),
    ("(int)(...)", "迭代器相减得到 ptrdiff_t，转 int 后输出，避免某些环境下按长整型打印。"),
]))

# ---------------------------------------------------------------- 子串哈希
SEC.append(P("哈希真正的威力不在“整串比较”，而在<b>任意子串比较</b>。要做到这一点，先算前缀哈希，"
             "再用一次减法把任意一段“抠”出来。"))

SEC.append(P("设 h[i] 是前 i 个字符的哈希，则 h[r] = h[l−1]·B<sup>r−l+1</sup> + H(l..r)："
             "前 r 个字符 = 前 l−1 个字符整体左移 r−l+1 位，再接上第 l..r 个字符。"
             "移项得到子串哈希公式。"))

SEC.append(Q("H(l..r) = h[r] − h[l−1] · B<sup>r−l+1</sup>。两段子串相同，这个值一定相同；"
             "值相同，则以极大概率两段相同——剩余的小概率就是“哈希冲突”。"))

SEC.append(C(r'''#include <bits/stdc++.h>
using namespace std;
typedef unsigned long long ull;

const ull B = 131;
const int MAXN = 1000005;
char s[MAXN];
ull h[MAXN], pw[MAXN];          // h：前缀哈希；pw：B 的幂

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cin >> (s + 1);             // 1 基下标，s[1] 是第一个字符
    int n = strlen(s + 1);

    pw[0] = 1;
    for (int i = 1; i <= n; ++i) {
        h[i]  = h[i - 1] * B + (ull)s[i];   // 前 i 个字符的指纹
        pw[i] = pw[i - 1] * B;              // B^i
    }

    // 子串 [l, r]（1 ≤ l ≤ r ≤ n）的指纹
    auto sub = [&](int l, int r) -> ull {
        return h[r] - h[l - 1] * pw[r - l + 1];
    };

    int q;
    cin >> q;
    while (q--) {
        int l1, r1, l2, r2;
        cin >> l1 >> r1 >> l2 >> r2;
        cout << (sub(l1, r1) == sub(l2, r2) ? "Yes\n" : "No\n");
    }
    return 0;
}''', "子串哈希：O(1) 判断两段是否相同"))

SEC.append(EXPLAIN("公式里的每一项在做什么", [
    ("cin >> (s + 1);", "把字符串读到 s[1] 起始的位置，这样下标 1 就是第一个字符。"
                        "括号不能省：<code>cin &gt;&gt; s + 1</code> 会被解析成 <code>(cin &gt;&gt; s) + 1</code>。"),
    ("h[i] = h[i - 1] * B + (ull)s[i];", "递推：把前 i−1 个字符整体“左移一位”，再在末位接上 s[i]。"),
    ("pw[i] = pw[i - 1] * B;", "幂表。子串公式里要乘 B<sup>r−l+1</sup>，现算会多一次 O(log n)，查表是 O(1)。"),
    ("h[r]", "前 r 个字符的指纹，等于 H(1..l−1) 左移 r−l+1 位后加上 H(l..r)。"),
    ("h[l - 1] * pw[r - l + 1]", "把前缀 1..l−1 移到与 h[r] 相同的位权上，才能相减。"
                                 "少了这一项，减出来的是“两个不同长度的前缀”之差，毫无意义。"),
    ("h[r] - h[l - 1] * pw[...]", "减法在 ull 里回绕，正好等价于模 2<sup>64</sup> 的减法，不需要 +M 再取模。"),
    ("auto sub = [&](int l, int r) -> ull", "lambda 捕获外部数组的引用，调用处像函数一样短。C++17 支持显式返回类型写法。"),
]))

SEC.append(P("这个公式是后面所有子串题的地基：找模式串出现位置（逐个起点比指纹）、"
             "最长公共前缀（二分长度 + 判等，O(log n)）、回文判断（正串和反串各一套哈希）。"
             "代价都是“预处理 O(n) + 每次询问 O(1) 或 O(log n)”。"))

# ---------------------------------------------------------------- Trie 实战
SEC.append(P("哈希能判相等，却回答不了“有多少个串以某个前缀开头”——那是集合问题，不是相等问题。"
             "Trie 把公共前缀压成一条公共路径，走到某个节点，<b>子树里有多少个词</b>就是这个前缀的出现次数。"))

SEC.append(C(r'''#include <bits/stdc++.h>
using namespace std;

const int MAXN = 100005;               // 节点上限 = 所有串总长 + 1
int ch[MAXN][26], pass[MAXN], ended[MAXN], tot = 0;

void insert(const string& s) {
    int u = 0;                         // 根
    for (char c : s) {
        int x = c - 'a';
        if (!ch[u][x]) ch[u][x] = ++tot;   // 没有这条边才新建：前缀只存一份
        u = ch[u][x];
        ++pass[u];                     // 经过 u 的串多了一个
    }
    ++ended[u];                        // 有一个串在这里结束
}

int node(const string& s) {            // 返回路径终点；-1 表示路断了
    int u = 0;
    for (char c : s) {
        int x = c - 'a';
        if (!ch[u][x]) return -1;
        u = ch[u][x];
    }
    return u;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, q;
    cin >> n >> q;
    string s;
    for (int i = 0; i < n; ++i) { cin >> s; insert(s); }

    while (q--) {
        cin >> s;
        int u = node(s);
        if (u == -1) { cout << "0 0\n"; continue; }
        cout << pass[u] << " " << (ended[u] > 0 ? 1 : 0) << "\n";
        // 第一个数：以 s 为前缀的串数；第二个数：s 自己是不是一个插入过的串
    }
    return 0;
}''', "Trie：插入、前缀计数、是否存在"))

SEC.append(EXPLAIN("Trie 的三处关键", [
    ("if (!ch[u][x]) ch[u][x] = ++tot;", "共享前缀的全部秘密。边已存在就直接复用，不新建节点——"
                                         "所以 <code>abc</code> 和 <code>abd</code> 只多花 1 个节点，不是 3 个。"),
    ("u = ch[u][x];", "沿着边走一步。循环结束时 u 就是整个串对应的节点。"),
    ("++pass[u];", "放在“走完这一步”之后，统计的是“经过该节点的串数”。"
                   "若放在走之前，统计的就变成了父节点的信息。"),
    ("++ended[u];", "区分“是前缀”和“是单词”。<code>ab</code> 是 <code>abc</code> 的前缀，"
                    "但 <code>ab</code> 自己可能没被插入——这时 ended[ab] = 0。"),
    ("if (u == -1)", "走不通说明这条路径从没被插入过，前缀数一定是 0。提前返回省掉后面的遍历。"),
    ("复杂度", "单次插入/查询 O(len)，与集合里有多少串无关。这是 Trie 相对“线性扫描所有串”的本质优势。"),
]))

# ---------------------------------------------------------------- 01-Trie
SEC.append(P("把 Trie 的边从 26 条换成 2 条、从字符换成二进制位，就得到 01-Trie。"
             "它解决一类问题：给定一堆数，问“与 x 异或最大的数是谁”。"))

SEC.append(C(r'''#include <bits/stdc++.h>
using namespace std;

const int MAXN = 100005;
int ch[MAXN * 31][2], tot = 0;         // 每个数最多占 31 个节点

void insert(int x) {
    int u = 0;
    for (int b = 30; b >= 0; --b) {    // 从最高位开始，高位决定大小
        int c = (x >> b) & 1;
        if (!ch[u][c]) ch[u][c] = ++tot;
        u = ch[u][c];
    }
}

int query(int x) {                     // 返回与 x 异或能得到的最大值
    int u = 0, r = 0;
    for (int b = 30; b >= 0; --b) {
        int c = (x >> b) & 1;
        if (ch[u][c ^ 1]) {            // 反边存在 → 这一位异或出 1，必选
            r |= 1 << b;
            u = ch[u][c ^ 1];
        } else {
            u = ch[u][c];              // 没得选，这一位异或出 0
        }
    }
    return r;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    int ans = 0;
    for (int i = 1; i <= n; ++i) {
        int x;
        cin >> x;
        if (i > 1) ans = max(ans, query(x));   // 先问已有的数，答案一定来自两个不同的数
        insert(x);
    }
    cout << ans << "\n";
    return 0;
}''', "01-Trie：求最大异或对（n ≤ 10⁵，值 < 2³¹）"))

SEC.append(EXPLAIN("为什么可以一位一位贪", [
    ("for (int b = 30; b >= 0; --b)", "从最高位往下。值 &lt; 2<sup>31</sup>，第 30 位是最高可能出现的位。"),
    ("if (ch[u][c ^ 1])", "c 是 x 当前位，c^1 是相反的位。走反边意味着这一位异或结果是 1。"),
    ("r |= 1 << b;", "这一位确定为 1，把 2<sup>b</sup> 记进答案。b ≤ 30，1 &lt;&lt; b 不会溢出 int。"),
    ("为什么高位优先", "第 b 位贡献 2<sup>b</sup>，低 b 位全取 1 也只有 2<sup>b</sup>−1 &lt; 2<sup>b</sup>。"
                      "高位多赢一位就大于所有低位之和，所以逐位贪心与全局最优一致。"),
    ("先 query 再 insert", "若先插后问，可能问到自己（x xor x = 0）；虽然不影响最大值，"
                           "但“重复元素”的题会算错计数。顺序写对一次，以后不用想。"),
    ("ans 用 int 就够", "两个 &lt; 2<sup>31</sup> 的数异或仍 &lt; 2<sup>31</sup>，不会超 int。"
                        "若把值域改到 10<sup>18</sup>，位宽要改成 62，r 必须换 long long。"),
]))

# ---------------------------------------------------------------- 易错
SEC.append(WARN("这一节的 7 种错法（都带症状）", [
    "<b>RE / 段错误</b>。—— Trie 的 MAXN 按“串的个数”开成 10<sup>4</sup>。节点数等于<b>总字符数</b>，"
    "1 万个长 1500 的串要 1.5×10<sup>7</sup> 个节点，insert 时写 ch[u][x] 越界。",
    "<b>WA，形如 ab 和 ba 被判成同一个串</b>。—— 基数取了 B = 1 或 2，哈希退化成字符求和，任何重排都同值。"
    "B 必须大于字符集大小。",
    "<b>WA，本地全对、-O2 下答案诡异</b>。—— 用 <code>long long</code> 做自然溢出。有符号溢出是 UB，"
    "编译器可以按“不会溢出”优化。必须 <code>unsigned long long</code>。",
    "<b>TLE</b>。—— 用 <code>set&lt;string&gt;</code> 或 <code>map&lt;string,int&gt;</code> 存 10<sup>5</sup> 个长 10<sup>3</sup> 的串："
    "每次比较 O(L)，总代价 O(N·L·log N)。哈希后排序整数是 O(N log N)。",
    "<b>WA，只有个别测试点错</b>。—— 单哈希被卡。长串 + 固定基数 + 模 2<sup>64</sup> 有确定的 Thue–Morse 反例，"
    "换双哈希或随机基数。",
    "<b>RE / 死循环</b>。—— 用 -1 表示“边不存在”，但全局数组默认 0。判定写成 <code>if (ch[u][x] == -1)</code> "
    "永远不成立，于是把 0 当成合法子节点原地打转。约定：0 表示不存在，编号从 1 开始。",
    "<b>WA，01-Trie 答案偏小</b>。—— 位宽只写到第 20 位而数据里有 10<sup>6</sup> 以上的数；"
    "或者值域到 2<sup>31</sup> 还写 <code>1 &lt;&lt; 31</code>（有符号移位溢出），应写 <code>1LL &lt;&lt; b</code>。",
]))

SEC.append(REPRO("关掉页面，把 P3370 从空文件敲一遍并 AC。",
                 "改一改 ①：把 B 改成 1，输入 <code>5 / ab / ba / abc / cba / aabb</code>，"
                 "不同字符串数会从 5 变成 3。想清楚哪几对撞了。",
                 "改一改 ②：把 <code>ull</code> 全换成 <code>long long</code>，加 <code>-O2</code> 编译，"
                 "输入 10<sup>5</sup> 个随机串，对比两种写法的答案是否一致。",
                 "改一改 ③：把 sort + unique 换成 <code>set&lt;ull&gt;</code>，用 time 命令比较 10<sup>5</sup> 个串的耗时差。",
                 "改一改 ④：在 01-Trie 里把位宽从 30 改成 20，输入 10<sup>6</sup> 以内的数，看答案错在哪一位。",
                 "改一改 ⑤：给子串哈希那题加一组询问，让 l1、r1、l2、r2 长度不同，验证“长度不同必然不等”是否由公式自动保证。"))

M = MATH("哈希为什么会有冲突：生日问题与 2^64", [
    P("多项式哈希把长 L 的串映射到 <b>H(s) = Σ s<sub>i</sub>·B<sup>L−i</sup> mod M</b>。"
      "不取模时这是 B 进制表示，B 大于字符集时不同串必得不同整数；取模把 M 以外的信息丢掉了，"
      "不同的串就可能落到同一个余数上，这就是冲突。"),
    P("<b>生日问题</b>：把 n 个串丢进 M 个桶，期望冲突对数 ≈ n(n−1)/(2M)。"
      "要让冲突概率低于 10<sup>−6</sup>，需要 M ≳ 5×10<sup>11</sup>·n<sup>2</sup>。"),
    T(["模数", "大小", "n = 10⁵ 时的期望冲突数", "能否被构造攻击"], [
        ["2<sup>32</sup>", "4.3×10<sup>9</sup>", "≈ 1.2", "能"],
        ["2<sup>64</sup>", "1.8×10<sup>19</sup>", "≈ 2.7×10<sup>−10</sup>", "能（Thue–Morse）"],
        ["10<sup>9</sup>+7 单哈希", "10<sup>9</sup>", "≈ 5", "能"],
        ["双哈希 10<sup>9</sup>+7 × 10<sup>9</sup>+9", "10<sup>18</sup>", "≈ 5×10<sup>−9</sup>", "极难"],
    ]),
    P("<b>为什么模 2<sup>64</sup> 特别脆</b>：2<sup>64</sup> 不是质数，奇数基数 B 的高次幂在模 2<sup>64</sup> 下很快退化，"
      "于是可以用“差分”构造出等长且哈希相同的两个串。已知的构造按 Thue–Morse 串取位"
      "（第 i 位由 popcount(i) 的奇偶决定），在模 2<sup>64</sup>、基数为奇数时两个串哈希完全相同。"
      "这就是 anti-hash 数据的来源——它不是运气，是构造。"),
    P("<b>双哈希为什么够</b>：两套哈希同时撞上的概率近似为两个概率之积。两个 10<sup>9</sup> 量级的模数给到 10<sup>18</sup> 的组合空间，"
      "且出题人要同时对两个不同模数构造反例，难度远超对 2<sup>64</sup>。代价只是常数 ×2。"),
    P("<b>子串哈希的恒等式</b>：h[r] = h[l−1]·B<sup>r−l+1</sup> + H(l..r)，移项即 "
      "<b>H(l..r) = h[r] − h[l−1]·B<sup>r−l+1</sup></b>。这一步把任意子串的指纹变成两次查表加一次乘法，"
      "是所有“子串比较”类题目的地基。"),
    P("<b>基数怎么选</b>：B 要大于字符集（否则不同字符会进位混叠），且最好与模数互质（取质数最省事）。"
      "131、13331 是习惯用法；更稳的是运行时随机取一个 10<sup>8</sup> 附近的质数，让反例无法预先构造。"),
])

THINK = [
    "判断“一个串是否在另一个串中出现”，哈希和下一节的 KMP 都能做，都是 O(n+m)。什么情况下哈希会退化成 O(nm)，什么情况下必须用 KMP？",
    "如果题目要求“把 s 的某个位置改成另一个字符，然后判断两个子串是否相等”，前缀哈希要怎么改？提示：h[i] 是一个和，能不能用树状数组维护？",
    "Trie 的空间是 O(总字符数)。那它比“把所有串塞进 set”省在哪？如果字符集是 10<sup>5</sup> 个汉字，<code>ch[u][c]</code> 还能这么开吗？替代方案是什么？",
    "01-Trie 求“最大异或对”是 O(31n)。如果改问“异或值 ≥ k 的数对有多少个”，怎么在树上做？提示：走边时同时统计子树里的数值个数。",
    "双哈希一定安全吗？要构造同时卡住两个模数的数据，串至少要多长？提示：两个模数乘积约 10<sup>18</sup>，而长度 L 的串有 62<sup>L</sup> 种。",
    "把 ull 换成 uint32_t（模 2<sup>32</sup> 自然溢出），n = 10<sup>5</sup> 时期望冲突数约 1.2。这个数字说明什么？",
    "为什么哈希替代不了 Trie 的“前缀计数”？前缀哈希能算出“某个前缀的指纹”，但它答不了哪个问题？",
]

CHECK = [
    "能默写多项式哈希的那一行，并说清为什么必须用 unsigned long long 而不是 long long。",
    "能写出子串哈希公式，并解释 h[l−1]·B<sup>r−l+1</sup> 这一项在做什么、去掉会错成什么样。",
    "能说出单哈希、双哈希在 n = 10<sup>5</sup> 时的冲突期望值数量级，并知道 Hash Killer 的存在。",
    "能默写 Trie 的 insert 与 node 查询，说清 0 号为什么既是根又是“不存在的边”。",
    "能默写 01-Trie 的插入与查询，并用“高位大于所有低位之和”解释贪心的正确性。",
    "拿到一道字符串题，能判断该用哈希、Trie，还是该等下一节的 KMP。",
]

# ---------------------------------------------------------------- 挑战 2
# 比挑战题难一档：本节只有哈希 / Trie / 01-Trie，这题要先把「树上的路径异或」折成「一堆整数的异或」，
# 再把 01-Trie 用上，两节工具各出一半力。
CH2 = CH(
    "最长异或路径", "P4551", "提高-/提高", "https://www.luogu.com.cn/problem/P4551",
    [P("给定一棵 n 个点的带权树，点编号 1..n。一条“异或路径”指树上 u、v 两点之间唯一路径上"
       "所有边权的异或值。求所有点对之间异或路径的最大值。"),
     P("输入：第一行一个整数 n（1 ≤ n ≤ 10<sup>5</sup>）；接下来 n−1 行，每行三个整数 u、v、w，"
       "表示 u 与 v 之间有一条权值为 w 的边（0 ≤ w &lt; 2<sup>31</sup>）。"),
     P("输出：一行一个整数，最大的异或路径值。"),
     P("样例：4 个点，边是 (1,2,3)、(2,3,4)、(2,4,6)。1 到 3 要经过权值 3 和 4 两条边，3 ⊕ 4 = 7，"
       "这一对是所有点对里最大的。")],
    hint=["先把问题从树上搬下来：记 d[u] 为“根走到 u”这一路的边权异或值。一条 u→v 的路径，"
          "和 d[u]、d[v] 之间差了什么？注意异或的逆运算是它自己，两个相同的数异或起来是多少？",
          "树上 n 个 d 值两两异或要 5×10<sup>9</sup> 次。本节正课里有个结构能把“和 x 异或最大”压到 31 步，"
          "它要求的输入是“一堆整数”还是“一棵树”？",
          "别按点数开数组：一个数要 31 个二进制位，10<sup>5</sup> 个数最多需要 3.1×10<sup>6</sup> 个 Trie 节点。"],
    idea=["记 d[u] 为根到 u 路径上的边权异或值。u→v 的路径 = u→lca→v，而 d[u] ⊕ d[v] 里"
          "“根→lca”那一段出现了两次，异或后归零，剩下的正好是 u→v 这一段的异或值。"
          "所以答案 = max{d[u] ⊕ d[v]}，与树的形状无关，只跟这 n 个数有关。",
          "题目于是变成：给 n 个不超过 2<sup>31</sup> 的整数，求两两异或的最大值。暴力 C(n,2) = 5×10<sup>9</sup> 次，超时。",
          "把这 n 个数从第 30 位到第 0 位插进 01-Trie，查询 x 时从高位往下走：只要 x 这一位的反向儿子存在，"
          "就一定走它。因为第 k 位贡献 2<sup>k</sup>，而 2<sup>k</sup> 大于所有更低位之和 2<sup>k</sup>−1，"
          "所以“先保高位”的贪心不会错。",
          "对每个 d[i] 查一次，答案取最大。单次 31 步，总计 O(31n)；Trie 节点数上限 31n+1。",
          "边界：n = 1 时没有边，只有 d[1] = 0，答案为 0（自己和自己异或）；w 可以取 0；"
          "d 用 int 就够，因为异或不会超过 2<sup>31</sup>−1。",
          "复杂度：时间 O(31n)，空间 O(31n)，n = 10<sup>5</sup> 时约 3.1×10<sup>6</sup> 个节点、25 MB。"],
    code=r'''#include <bits/stdc++.h>
using namespace std;

const int MAXN = 100005;
int head[MAXN], nxt[MAXN << 1], to[MAXN << 1], wt[MAXN << 1], ecnt = 0;
int d[MAXN];                 // d[u] = 根到 u 的边权异或值
bool vis[MAXN];

void addEdge(int u, int v, int w) {
    to[++ecnt] = v; wt[ecnt] = w; nxt[ecnt] = head[u]; head[u] = ecnt;
}

// 01-Trie：每个数从第 30 位插到第 0 位，节点数 <= 31n + 1
const int MAXT = 3200005;
int ch[MAXT][2], tot = 0;

void insert(int x) {
    int u = 0;
    for (int i = 30; i >= 0; --i) {
        int b = (x >> i) & 1;
        if (!ch[u][b]) ch[u][b] = ++tot;      // 走不通才建新点，前缀靠共享
        u = ch[u][b];
    }
}

int query(int x) {
    int u = 0, res = 0;
    for (int i = 30; i >= 0; --i) {
        int b = (x >> i) & 1;
        if (ch[u][b ^ 1]) {                    // 反向位存在就先走，这一位能拿到 1
            res |= 1 << i;
            u = ch[u][b ^ 1];
        } else {
            u = ch[u][b];
        }
    }
    return res;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    for (int i = 1; i < n; ++i) {
        int u, v, w;
        cin >> u >> v >> w;
        addEdge(u, v, w);
        addEdge(v, u, w);
    }
    // 迭代 BFS 求前缀异或：链状树深度 10^5，递归 DFS 有爆栈风险
    queue<int> q;
    q.push(1);
    vis[1] = true;
    while (!q.empty()) {
        int u = q.front(); q.pop();
        insert(d[u]);
        for (int e = head[u]; e; e = nxt[e]) {
            int v = to[e];
            if (vis[v]) continue;
            vis[v] = true;
            d[v] = d[u] ^ wt[e];               // 异或是自己的逆运算，可沿路径累积
            q.push(v);
        }
    }
    int ans = 0;
    for (int i = 1; i <= n; ++i) ans = max(ans, query(d[i]));
    cout << ans << '\n';
    return 0;
}''',
    explain=[
        ("d[v] = d[u] ^ wt[e];", "地基：异或是自己的逆运算，所以 d[u] ⊕ d[v] 里“根→lca”那一段自动消掉，"
                                 "剩下正是 u→v 的路径异或值。"),
        ("for (int i = 30; i >= 0; --i)", "位宽。w &lt; 2<sup>31</sup>，最高位是第 30 位；"
                                          "写成从 29 起循环会把 2<sup>30</sup> 那一档算漏。"),
        ("if (ch[u][b ^ 1]) { res |= 1 << i; ... }", "★ 贪心核心：反向位存在就选它。"
                                                    "第 k 位的一个 1 抵得过后面所有位之和。"),
        ("const int MAXT = 3200005;", "节点上限 31n+1 ≈ 3.1×10<sup>6</sup>。按点数 n 开数组必 RE。"),
        ("queue&lt;int&gt; q; ... vis[v] = true;", "链状树深 10<sup>5</sup>，递归 DFS 会爆栈；"
                                                  "BFS 里顺手算 d 并插入，一个循环干完两件事。"),
        ("for (int i = 1; i <= n; ++i) ans = max(ans, query(d[i]));", "每个 d 查一次。"
                                                                     "n = 1 时循环仍执行，答案是 0，正确。"),
    ],
    pitfalls=["Trie 数组按点数 n 开：节点数是 31n+1（每个节点 2 个儿子），10<sup>5</sup> 时直接越界 RE。",
              "位宽取错：w &lt; 2<sup>31</sup> 意味着第 30 位也要建，从 29 或从 20 起循环都会答案偏小。",
              "忘了每条无向边要建两条：只 addEdge(u, v, w) 时树是断的，一半的点 d 值永远是 0。",
              "n = 1 时特判成“无解”或直接输出 −1：此时答案是 0（自己到自己），不该特殊处理掉。"],
    sample="输入：\n4\n1 2 3\n2 3 4\n2 4 6\n输出：\n7",
)

CH = CH(
    "于是他错误的点名开始了", "P2580", "普及/提高-", "https://www.luogu.com.cn/problem/P2580",
    [P("化学竞赛组有 n 名学生，教练手里有名单。教练会依次报出 m 个名字，你要对每个名字给出判断："),
     P("若这个名字在名单里且是<b>第一次</b>被点到，输出 <code>OK</code>；"
       "若在名单里但<b>之前已经被点过</b>，输出 <code>REPEAT</code>；若<b>不在</b>名单里，输出 <code>WRONG</code>。"),
     P("输入：第一行一个整数 n；接下来 n 行每行一个名字（互不相同，只含小写字母，长度 ≤ 50）；"
       "第 n+2 行一个整数 m；接下来 m 行每行一个教练报的名字（只含小写字母，长度 ≤ 50）。"
       "数据范围 n ≤ 10<sup>4</sup>，m ≤ 10<sup>5</sup>。"),
     P("输出：对教练报的每个名字输出一行，为 <code>OK</code>、<code>REPEAT</code> 或 <code>WRONG</code>。")],
    hint=["名字总数 10<sup>4</sup>、长度 ≤ 50，总字符数不超过 5×10<sup>5</sup>。这个数字提示你：可以按字符建结构，不必按名字建。",
          "查询要区分三件事：这条路径存在吗？路径的终点真的有名字结束吗？这个名字之前被点过吗？三件事需要三种不同的信息。",
          "“前缀”和“单词”要分开：名单里只有 ab，教练报 abc，这条路径走不通；名单里只有 abc，教练报 ab，路径走得通但 ab 不结束。"],
    idea=["把名单建成 Trie：每个名字从根出发逐字符走，没有边就新建节点。走完整个名字时，把该节点的“结束计数”加一。",
          "查询一个名字也是逐字符走：中途某条边不存在，说明名单里没有以它为前缀的名字，直接 WRONG。",
          "走完整条路径后，还要看终点节点的结束计数是否为 0。为 0 说明它只是某个更长名字的前缀，自己不是名单里的名字——也是 WRONG。",
          "为了区分 OK 和 REPEAT，再给每个节点一个 vis 标记：第一次走到这里输出 OK 并置 true，之后再走到就输出 REPEAT。",
          "为什么用 Trie 而不是 set：set 查一次是 O(len·log n) 次字符串比较，Trie 是 O(len) 次下标访问，而且 m 到 10<sup>5</sup>，差距会放大。",
          "复杂度：插入 O(总字符数) ≤ 5×10<sup>5</sup>，查询 O(m×50) ≤ 5×10<sup>6</sup>，空间 O(总字符数)。"],
    code=r'''#include <bits/stdc++.h>
using namespace std;

const int MAXN = 500005;               // 节点上限 = n × 50
int ch[MAXN][26], ended[MAXN], tot = 0;
bool vis[MAXN];                        // 这个节点被点过名没有

void insert(const string& s) {
    int u = 0;
    for (char c : s) {
        int x = c - 'a';
        if (!ch[u][x]) ch[u][x] = ++tot;   // 前缀只有一份
        u = ch[u][x];
    }
    ++ended[u];                        // 这个名字真的在名单里
}

int node(const string& s) {            // 返回终点编号；-1 表示路径不存在
    int u = 0;
    for (char c : s) {
        int x = c - 'a';
        if (!ch[u][x]) return -1;
        u = ch[u][x];
    }
    return u;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    string s;
    for (int i = 0; i < n; ++i) { cin >> s; insert(s); }

    int m;
    cin >> m;
    for (int i = 0; i < m; ++i) {
        cin >> s;
        int u = node(s);
        // 路走不通，或者走通了但这里没有名字结束：都不是名单里的名字
        if (u == -1 || ended[u] == 0) { cout << "WRONG\n"; continue; }
        if (vis[u]) { cout << "REPEAT\n"; continue; }
        vis[u] = true;
        cout << "OK\n";
    }
    return 0;
}''',
    explain=[
        ("const int MAXN = 500005;", "n ≤ 10<sup>4</sup>、每个名字长 ≤ 50，总字符数 ≤ 5×10<sup>5</sup>，"
                                     "节点数不会超过总长 + 1。按“名字个数”开数组是这题最常见的 RE。"),
        ("if (!ch[u][x]) ch[u][x] = ++tot;", "共享前缀。名字 abc 与 abd 只多花一个节点，不是三个。"),
        ("++ended[u];", "★ 结束标记。没有它，“abc 在名单里，报 ab”会被判 OK，而正确答案是 WRONG。"),
        ("if (!ch[u][x]) return -1;", "边走边判。路径断了就没有必要走下去，也顺便区分了“不存在”和“存在但不是名字”。"),
        ("if (u == -1 || ended[u] == 0)", "两个条件缺一不可。u == -1 是路径断了；ended[u] == 0 是路径存在但只是别人的前缀。"),
        ("if (vis[u])", "★ 用节点编号当访问标记，而不是再存一份字符串。同一个名字必然落在同一个节点上，"
                        "所以节点编号就是名字的唯一 ID。"),
        ("vis[u] = true;", "只在这一步置真：确保“第一次报”输出 OK，“第二次及以后”输出 REPEAT。"),
    ],
    pitfalls=["把 MAXN 按名字个数开成 10<sup>4</sup>：节点数是总字符数，直接 RE。",
              "忘了判 <code>ended[u] == 0</code>：名单里只有 abc 时报 ab，会错判成 OK。",
              "用 <code>map&lt;string,int&gt;</code> 记是否点过名：能过，但多了一次哈希，且意图不如“节点编号当 ID”清晰；"
              "n、m 更大时会被卡。",
              "用 <code>ended[u]--</code> 表示“点过”：同一个名字第二次来时 ended[u] 已变成 0，"
              "会被判成 WRONG 而不是 REPEAT。",
              "多测不清空：本题只有一组，但换到多测题时必须把 tot、ch、ended、vis 一起清。"],
    sample="输入：\n5\na\nb\nc\nad\nacd\n3\na\na\ne\n输出：\nOK\nREPEAT\nWRONG",
)

LESSONS = [LESSON(
    51, "字符串哈希与 Trie",
    "把字符串压成整数、把前缀压成路径：多项式哈希与 ull 自然溢出解决整串比较，前缀哈希 + 幂表解决子串比较，"
    "Trie 解决前缀计数，01-Trie 解决最大异或。附带一套防冲突的规矩：基数大于字符集、模数用双哈希、溢出必须无符号。",
    65, ["哈希", "Trie", "冲突"], "提高-",
    SEC, math=M, think=THINK, check=CHECK, challenge=CH, challenge2=CH2,
    refs=["《算法竞赛进阶指南》0x14 哈希与 0x31 字典树",
          "《算法竞赛入门笔记》字符串章节：哈希与 Trie",
          "《算法竞赛试炼场：洛谷300题精析》P3370、P2580 两题的精析",
          "《算法竞赛黄金法则：提高算法和思考力的77项技巧》中“把比较换成指纹”的思路",
          "洛谷 P3370 题目的“拓展阅读”：Hash Killer I~Extra 系列"],
)]
