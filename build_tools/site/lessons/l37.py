# -*- coding: utf-8 -*-
"""第 37 节 · 最大公约数、同余与快速幂"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dsl import *  # noqa

SEC = []

SEC.append(P("上一节把数拆成质数，这一节处理“两个数的公共结构”和“大指数”。"
             "三件事：<b>两个数的最大公约数与最小公倍数</b>、<b>同余方程与逆元</b>、<b>a<sup>b</sup> mod m</b>。"
             "第三件是第二件的工具，第二件是第一件的推广——三者用同一套代码互相支撑。"))

SEC.append(Q("gcd(a, b) = gcd(b, a mod b)，递归到 b = 0 就得到答案；"
             "a<sup>b</sup> mod m 只要把 b 拆成二进制，31 轮乘法就能算完。"))

SEC.append(T(["要做的事", "数据规模", "用什么", "复杂度"], [
    ["两个数的 gcd", "a, b ≤ 10^18", "辗转相除", "O(log min(a,b))，≤ 95 步"],
    ["两个数的 lcm", "结果 ≤ 9.2×10^18", "a / gcd * b，先除后乘", "同上"],
    ["a·x ≡ 1 (mod m) 的逆元", "m ≤ 10^9", "扩展欧几里得 / 费马小定理", "O(log m)"],
    ["a^b mod m", "b ≤ 10^18", "快速幂", "O(log b)"],
    ["两个 10^18 的数相乘再取模", "mod ≤ 10^18", "__int128", "O(1)"],
]))

# ---------------------------------------------------------------- 新工具
SEC.append(P("先把这几个工具拆开看清。它们都很短，但每一个都有一处“不这么写就错”的细节，"
             "这些细节正是这一节真正的考点。"))

SEC.append(FN(
    "std::gcd（C++17）",
    "int g = std::gcd(a, b);\nlong long g = std::gcd(x, y);",
    [("头文件", "&lt;numeric&gt;。&lt;bits/stdc++.h&gt; 已经包含，不用额外写。"),
     ("两个参数类型必须相同", "gcd(3, 4LL) 编译不过（模板推导冲突）。竞赛里统一用 long long 最省事。"),
     ("返回值", "非负。gcd(−12, 18) = 6，它内部按绝对值算。"),
     ("gcd(x, 0) = |x|", "辗转相除的终止条件正好是 b = 0，所以 0 是合法参数，不用特判。"),
     ("C++17 之前", "只能手写辗转相除，或用 GNU 扩展 <code>__gcd(a, b)</code>（非标准，MSVC 没有）。"),
     ("手写版", "四行：while (b) { t = a % b; a = b; b = t; } return a; 逻辑与递归版完全一样。")],
    example=r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    cout << gcd(12, 18) << "\n";        // 6
    cout << gcd(0, 7)   << "\n";        // 7：gcd(0, x) = |x|
    cout << gcd(-12, 18)<< "\n";        // 6：取绝对值

    long long a = 1000000000000LL, b = 8;
    cout << gcd(a, b) << "\n";          // 4：两个都是 long long

    // 手写辗转相除（不依赖 C++17）
    long long x = a, y = b;
    while (y) { long long t = x % y; x = y; y = t; }
    cout << x << "\n";                  // 4
    return 0;
}''',
    notes=["<code>gcd(3, 4LL)</code> 这类“一个 int 一个 long long”的写法直接编译失败（no matching function）。出错时先看参数的声明类型。",
           "手写版若 a、b 可能为负数，先各自取绝对值：C++ 的 % 对负数返回负余数，不处理会死循环。"],
    brief="C++17 一行求最大公约数，参数类型必须一致"))

SEC.append(FN(
    "lcm：先除后乘",
    "long long lcm(long long a, long long b) { return a / gcd(a, b) * b; }",
    [("a * b / gcd", "<b>错</b>。a = b = 4×10^9 时 a·b = 1.6×10^19，超出 long long 上限 9.22×10^18，先溢出再除，结果毫无意义。"),
     ("a / gcd * b", "<b>对</b>。gcd 一定整除 a，先除不丢精度；中间值最大就是最终答案，不会比 lcm 更大。"),
     ("为什么顺序有效", "公因子被提前消掉了。两个数相乘只做一次，谁先谁后不影响结果，只影响中间值的大小。"),
     ("std::lcm 也存在", "C++17 提供，同样先除后乘；但竞赛里更常手写——模意义下的 lcm 要乘逆元，标准库帮不上。"),
     ("返回值", "lcm(a, b) = a / gcd(a, b) * b 对正整数恒成立；带负数时先取绝对值。"),
     ("装不下的情况", "lcm 本身超过 9.2×10^18 时，任何 long long 写法都没救，要么题目保证范围，要么上 __int128。")],
    example=r'''long long lcm(long long a, long long b) {
    return a / gcd(a, b) * b;      // 先除后乘
}

// 反例：a = b = 4e9
//   a * b / gcd = 1.6e19 / 4e9   → 1.6e19 已超出 long long，溢出成负数
//   a / gcd * b = 1e9 * 4e9      → 4e18，正确''',
    notes=["写乘法前先估一次中间值。这是数论题里最常见、也最难查的一类 WA：答案小的时候全对，大测试点突然变成负数。",
           "a ≥ b 时先算 a / gcd 得到的商更小，习惯上把大的放前面。"],
    brief="lcm = a / gcd * b，顺序决定会不会溢出"))

SEC.append(FN(
    "__int128（128 位整数）",
    "__int128 x = (__int128)a * b % m;",
    [("范围", "约 ±1.7×10^38。两个 10^18 的数相乘得 10^36，装进去还剩两位数量级的余量。"),
     ("不是标准类型", "GCC / Clang 支持（洛谷、Codeforces、NOI 系列评测机都是 GCC），MSVC 不支持。别名 __int128_t。"),
     ("不能直接读入输出", "cin、cout、scanf、printf 全不认识它。读入先读进 long long 再赋值；输出要手写按位打印。"),
     ("转换要写在乘法之前", "<code>(__int128)a * b</code> 正确：a 先被提升，b 自动跟着提升。"
                            "<code>(__int128)(a * b)</code> 错误：乘法已经在 long long 里溢出，再转也救不回来。"),
     ("速度", "加减与 long long 接近，乘除取模慢 3~10 倍。10^8 次循环里慎用。"),
     ("典型用法", "把一次可能溢出的乘法“抬”到 128 位算完，取模后降回 long long。")],
    example=r'''// ① 防溢出的乘法取模：a、b < m ≤ 10^18
long long mulMod(long long a, long long b, long long m) {
    return (long long)((__int128)a * b % m);   // 中间 10^36，long long 装不下
}

// ② 打印 __int128：cout 不认识它，只能自己按位输出
void print128(__int128 x) {
    if (x < 0) { putchar('-'); x = -x; }
    if (x > 9) print128(x / 10);
    putchar('0' + (int)(x % 10));
}''',
    notes=["<code>(long long)(...)</code> 这一步不能省：表达式类型是 __int128，赋给 long long 变量时虽会自动截断，但显式写出来更清楚，也避免 cout 直接输出它。",
           "本节题目 k ≤ 2^31，(2^31)² = 4.6×10^18 还在 long long 内，其实不用 128 位；但模板写成 __int128 版本可以无脑复用，不必每次重新估范围。"],
    brief="128 位整数，专治乘法溢出"))

SEC.append(FN(
    "快速幂（二进制拆分指数）",
    "long long qpow(long long a, long long b, long long mod);",
    [("a", "底数。进门先 a %= mod，否则第一次乘法就可能用到大数。"),
     ("b", "指数。必须用 long long：2^31 = 2147483648 已经超过 int 上限 2147483647。"),
     ("mod", "模数。mod = 1 时任何数都同余于 0，结果必须是 0。"),
     ("r = 1 % mod", "累乘器初值。直接写 1 在 mod = 1 且 b = 0 时会返回 1，答案应为 0；写 1 % mod 一劳永逸。"),
     ("b &amp; 1", "取 b 的最低位。为 1 表示当前这份 <code>a^(2^k)</code> 要乘进答案。"),
     ("a = a * a % mod", "a 依次变成 a<sup>2</sup>、a<sup>4</sup>、a<sup>8</sup>……每轮平方一次。"),
     ("b &gt;&gt;= 1", "右移一位，处理下一个二进制位。循环次数 = b 的二进制位数 ≤ 63。")],
    example=r'''long long qpow(long long a, long long b, long long mod) {
    long long r = 1 % mod;              // 处理 mod = 1 的退化情况
    a %= mod;
    while (b) {
        if (b & 1) r = r * a % mod;     // 这一位是 1：把 a^(2^k) 乘进来
        a = a * a % mod;                // a 平方，准备下一位
        b >>= 1;
    }
    return r;
}

// qpow(2, 10, 9)   = 1024 % 9 = 7
// qpow(2, 0, 1000) = 1
// qpow(7, 5, 1)    = 0''',
    notes=["每一步都要取模。写成 <code>r = r * a</code> 最后统一取模，b ≥ 40 就溢出，症状是中等数据突然错、大数据变成负数。",
           "mod ≤ 2^31 时 r·a 不超过 4.7×10<sup>18</sup>，long long 够用；mod 到 10^18 就必须把两次乘法换成 __int128。"],
    brief="O(log b) 求 a^b mod m，三步循环"))

# ---------------------------------------------------------------- 例题
SEC.append(EX("【模板】快速幂", "P1226", "普及/提高-", "https://www.luogu.com.cn/problem/P1226",
              ["输入三个整数 b、p、k（1 ≤ b, p, k ≤ 2<sup>31</sup>），求 b<sup>p</sup> mod k 的值。",
               "输出格式严格为 <code>b^p mod k=s</code>，其中 s 是结果，等号两边没有空格。",
               "注意：p 最大 2<sup>31</sup>，用 int 读入会失败。"],
              sample="输入：\n2 10 9\n输出：\n2^10 mod 9=7"))

SEC.append(IDEA("例题怎么想：把指数拆成二进制", [
    "先算朴素做法要多久：循环 p 次做一次乘法，p ≤ 2<sup>31</sup> = 21 亿，就算每纳秒一次乘法也要 2 秒以上，必然 TLE。"
    "所以必须减少乘法次数，而不是优化每一步。",
    "关键观察：p 的二进制最多 31 位，p 就是若干个 2 的幂之和。于是 <code>b^p</code> 等于对应的那些 "
    "<code>b^(2^k)</code> 相乘——只要手里有 <code>b^1、b^2、b^4、…、b^(2^30)</code> 这 31 个数，"
    "按 p 的二进制位挑出来相乘即可。",
    "这 31 个数不用分别算：后一个是前一个的平方。<code>(b^2)^2 = b^4</code>，<code>(b^4)^2 = b^8</code>，"
    "一路平方下去，正好 31 次。",
    "取模可以随时插入：因为 (x·y) mod m = ((x mod m)·(y mod m)) mod m。"
    "每一次乘法后立刻取模，中间值就永远不超过 m² ≤ 4.6×10<sup>18</sup>，long long 装得下。",
    C(r'''r = 1, a = b % k
当 p > 0：
    若 p 的最低位是 1：r = r * a % k     ← 这一位对应的幂要乘进来
    a = a * a % k                        ← 幂次翻倍：a, a², a⁴, ...
    p >>= 1                              ← 右移，看下一位
输出 r''', "三步循环"),
    P("两处细节必须写在代码里，否则有测试点过不了：<b>p 用 long long 读</b>（2<sup>31</sup> 超 int）；"
      "<b>输出用原始的 b、p、k</b>（不是在函数里取过模的副本）。"),
]))

SEC.append(C(r'''#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

// 计算 a^b mod m
ll qpow(ll a, ll b, ll m) {
    ll r = 1 % m;                          // m = 1 时答案恒为 0，1 % 1 = 0
    a %= m;                                // 底数先进模，后面的乘法才安全
    while (b) {
        if (b & 1) r = (__int128)r * a % m; // 这一位是 1，把当前的 a^(2^k) 乘进答案
        a = (__int128)a * a % m;            // 平方，得到下一份的幂
        b >>= 1;                            // 处理下一个二进制位
    }
    return r;
}

int main() {
    ll b, p, k;
    cin >> b >> p >> k;                     // p 可达 2^31，必须 long long
    cout << b << "^" << p << " mod " << k << "=" << qpow(b, p, k) << "\n";
    return 0;
}''', "完整代码"))

SEC.append(EXPLAIN("逐行拆解", [
    ("ll r = 1 % m;", "累乘器初值。写 1 的话，m = 1 且 b = 0 时返回 1，而正确答案是 0。"),
    ("a %= m;", "底数先取模。否则 b 的最低位就是 1 时，第一轮 r * a 直接用到大数，乘完再取模已经溢出。"),
    ("while (b)", "b 每轮右移一位，循环次数等于 b 的二进制位数，p ≤ 2^31 时最多 31 轮。"),
    ("if (b &amp; 1)", "取最低位。这一位是 1 表示 <code>a^(2^k)</code> 属于乘积，要乘进 r；是 0 就跳过。"),
    ("(__int128)r * a % m", "抬起一轮再取模。m 到 10^18 时 r·a 会溢出 long long，这样写一劳永逸。"),
    ("a = (__int128)a * a % m;", "平方。注意这里用的是取模后的 a，与 r 无关，两行互不干扰。"),
    ("b &gt;&gt;= 1;", "右移一位。写成 b /= 2 结果一样，移位更贴合“二进制位”的语义。"),
    ("cin &gt;&gt; b &gt;&gt; p &gt;&gt; k;", "三个变量都是 long long：p 最大 2^31 = 2147483648，int 上限只有 2147483647，用它读会失败。"),
    ("cout &lt;&lt; b &lt;&lt; \"^\" ...", "输出的是原始 b、p、k，不是函数里取过模的副本。格式里 ^ 和 = 两边都没有空格。"),
]))

# ---------------------------------------------------------------- 同余
SEC.append(P("快速幂解决“指数很大怎么算”。数论的另一半问题是“<b>除法怎么取模</b>”。"
             "加减乘都可以边算边取模，只有除法不行：(a / b) mod m 既不等于 (a mod m) / (b mod m)，"
             "很多时候压根不是整数。要让“除以 b”变成“乘以 b 的逆元”，就得解同余方程 b·x ≡ 1 (mod m)。"))

SEC.append(T(["运算", "能否直接取模", "正确写法"], [
    ["(a + b) mod m", "能", "(a mod m + b mod m) mod m"],
    ["(a − b) mod m", "能", "((a mod m − b mod m) + m) mod m，先加 m 防负"],
    ["(a × b) mod m", "能", "快速幂每步取模的依据；中间乘积超范围就上 __int128"],
    ["(a ÷ b) mod m", "<b>不能</b>", "乘以 b 的逆元 b<sup>−1</sup>，前提是 gcd(b, m) = 1"],
]))

SEC.append(P("求逆元要先会解 <b>a·x + b·y = gcd(a, b)</b>。裴蜀定理保证这个方程一定有整数解，"
             "而把辗转相除的每一步“回代”就能把解构造出来——这就是扩展欧几里得。"))

SEC.append(C(r'''// 求 a*x + b*y = gcd(a,b) 的一组整数解，返回 gcd(a,b)
// x、y 用引用传递，返回值通过参数带出（第 11 节学过）
long long exgcd(long long a, long long b, long long &x, long long &y) {
    if (b == 0) {                    // 出口：a*1 + 0*0 = a
        x = 1; y = 0;
        return a;
    }
    long long x1, y1;
    long long g = exgcd(b, a % b, x1, y1);   // 先让规模变小，再回代
    x = y1;                          // a 的系数
    y = x1 - (a / b) * y1;           // b 的系数
    return g;
}''', "扩展欧几里得（递归回代版）"))

SEC.append(EXPLAIN("回代是怎么来的", [
    ("if (b == 0) { x = 1; y = 0; return a; }", "出口。此时 a 就是 gcd(a, b)，取 x = 1、y = 0 满足 a·1 + 0·0 = a。"),
    ("exgcd(b, a % b, x1, y1)", "规模从 (a, b) 变成 (b, a mod b)，和辗转相除走的是同一条路，所以递归深度也同阶。"),
    ("b·x1 + (a mod b)·y1 = g", "递归返回时我们手里有这一条等式。"),
    ("a mod b = a − (a / b)·b", "把上式里的 a mod b 展开：b·x1 + (a − (a/b)·b)·y1 = a·y1 + b·(x1 − (a/b)·y1)。"),
    ("x = y1;", "对照展开后的式子，a 的系数是 y1，所以新的 x 就是 y1。"),
    ("y = x1 - (a / b) * y1;", "b 的系数是 x1 − (a/b)·y1，这就是新的 y。"),
    ("返回 g", "顺手拿到 gcd，省得再调一次，也是判断“方程有没有解”的依据。"),
]))

SEC.append(P("拿到 exgcd 之后，逆元就是一行的事：a·x + m·y = 1 里的 x 就是 a 模 m 的逆元。"
             "另一种求法是把上一节的快速幂接上来——当 m 是质数时，费马小定理直接给答案。"))

SEC.append(C(r'''// ① 扩展欧几里得：任意模数，只要 gcd(a, m) == 1 就有逆元
long long invExgcd(long long a, long long m) {
    long long x, y;
    long long g = exgcd(a, m, x, y);     // a*x + m*y = gcd(a, m)
    if (g != 1) return -1;               // 不互质，逆元不存在
    return (x % m + m) % m;              // 归一化到 [0, m)
}

// ② 费马小定理：只在 m 是质数时可用（1e9+7、998244353 这类）
long long invFermat(long long a, long long m) {
    return qpow(a, m - 2, m);            // a^(m-2) ≡ a^(-1) (mod m)
}''', "两种求逆元"))

SEC.append(EXPLAIN("逆元的三处关键", [
    ("a·x + m·y = gcd(a, m)", "裴蜀定理：a·x + m·y 能取到的最小正数恰是 gcd(a, m)。所以方程的右边必须能被 gcd 整除。"),
    ("if (g != 1) return -1;", "要让右边等于 1，只有 gcd = 1。这就是“逆元存在 ⟺ 互质”的来源。"),
    ("(x % m + m) % m", "C++ 的 % 结果符号跟着被除数走，负数取模仍是负数。先 %m 把它拉进 (−m, m)，加 m 变正，再 %m 收进 [0, m)。"),
    ("qpow(a, m - 2, m)", "费马小定理：m 为质数且 m ∤ a 时 a^(m−1) ≡ 1，两边同除 a 得 a^(m−2) ≡ a^(−1)。"),
    ("两种做法的取舍", "费马版是 log m 次乘法，常数小、代码短；exgcd 版任意模数都能用。m 是 1e9+7 时竞赛里普遍用费马版。"),
]))

SEC.append(WARN("这一节的 8 种典型错法（含症状）", [
    "<b>WA，答案恒为 0</b>。—— 快速幂的累乘器写成 <code>long long r = 0;</code>。任何数乘 0 都是 0，样例就能看出来。",
    "<b>WA，小数据全对、大数据错误或为负</b>。—— 每步忘了取模，中间值 40 次乘法后溢出。凡是“取模题答案忽正忽负”，先查这一步。",
    "<b>TLE 或输出随机值</b>。—— 指数 p 用 int 读 2^31。<code>cin</code> 解析失败后 p 保持未初始化值，"
    "循环次数完全随机，表现为 TLE 或答案离谱。指数、模数一律 long long。",
    "<b>WA，输出负数</b>。—— 逆元直接写 <code>x % m</code>。样例 3 10 恰好得到正数 7 看不出来，"
    "换 a = 2、b = 3 会输出 −1（正确答案 2）。必须 <code>(x % m + m) % m</code>。",
    "<b>WA，答案比正确值小且是负数</b>。—— lcm 写成 <code>a * b / gcd(a, b)</code>，a、b 到 4×10^9 时乘积溢出。",
    "<b>RE（除零）或无限递归</b>。—— 手写 gcd 的出口写成 <code>if (b == 1) return 1;</code>。"
    "该停的时候 b 已经变成 0，下一轮还要算 <code>a % b</code>，除零 RE。必须是 <code>if (b == 0)</code>。",
    "<b>CE（编译失败）</b>。—— <code>gcd(3, 4LL)</code> 类型不一致；或者用 <code>cin &gt;&gt; x</code> 读 __int128。"
    "前者加一个 <code>LL</code> 后缀统一类型，后者只能先读 long long 再赋值。",
    "<b>WA，本应输出“无解”却输出了一个数</b>。—— 同余方程 a·x ≡ b (mod m) 在 gcd(a, m) ∤ b 时无解，"
    "但 exgcd 照样会返回 a·x + m·y = g 的一组解，直接拿来用就是错的。先判 <code>b % g != 0</code> 再谈求解。",
]))

SEC.append(REPRO("关掉页面，从空文件把 P1226 敲一遍并提交到洛谷。",
                 "改一改 ①：把 while 循环换成 <code>for (ll i = 0; i &lt; p; ++i) r = r * b % k;</code>，"
                 "输入 <code>2 1000000000 998244353</code>，用 time 计时——亲眼看一次 10 亿次乘法要多久。",
                 "改一改 ②：把 <code>if (b &amp; 1)</code> 改成 <code>if (b &amp; 2)</code>，输入 <code>2 10 1000</code>，"
                 "看答案从 24 变成多少。想清楚为什么只“少乘了某些位”。",
                 "改一改 ③：把 lcm 写成 <code>a * b / gcd(a, b)</code>，输入 a = b = 4000000000，"
                 "打印中间值 a*b——观察它变成负数，再换回 <code>a / gcd * b</code> 对比。",
                 "改一改 ④：用 exgcd 版求逆元，把 <code>(x % m + m) % m</code> 改成 <code>x % m</code>，"
                 "输入 a = 2、m = 3，输出会变成 −1。这就是“最小正整数解”必须归一化的原因。"))

M = MATH("同余、裴蜀与逆元", [
    P("同余的定义只有一句：a ≡ b (mod m) 表示 m 整除 a − b。它把整数按“除以 m 的余数”分成 m 类，"
      "而所有运算都在这 m 个类上进行——这就是“模 m 剩余系”。"),
    P("<b>为什么加减乘可以随便取模</b>：若 a ≡ a′、b ≡ b′ (mod m)，则 a ± b ≡ a′ ± b′、a·b ≡ a′·b′。"
      "所以每一步乘完立刻取模，结果不变。这也解释了快速幂为什么能边乘边模。"),
    P("<b>除法为什么不行</b>：2 ≡ 8 (mod 6)，两边同除 2 得 1 与 4，而 1 ≢ 4 (mod 6)。"
      "取模把“差 m 的倍数”这个信息扔掉了，而除法恰好要用到它。补救办法是乘逆元。"),
    P("<b>裴蜀定理</b>：对任意整数 a、b（不全为 0），存在整数 x、y 使 a·x + b·y = gcd(a, b)，"
      "而且 gcd(a, b) 是所有形如 a·x + b·y 的正数中最小的那个。"),
    L(["推论 1：a·x ≡ 1 (mod m) 有解 ⟺ gcd(a, m) = 1。（右边 1 必须能被 gcd 整除）",
       "推论 2：a·x ≡ b (mod m) 有解 ⟺ gcd(a, m) | b。有解时在 [0, m) 内恰好有 gcd(a, m) 个解。"]),
    P("<b>通解结构</b>：若 (x<sub>0</sub>, y<sub>0</sub>) 是 a·x + b·y = g 的一组解，则全部解为 "
      "x = x<sub>0</sub> + k·(b/g)、y = y<sub>0</sub> − k·(a/g)，k 取遍整数。"
      "所以对 b 取模后逆元唯一——这就是 <code>(x % m + m) % m</code> 一定对的理由。"),
    P("<b>费马小定理</b>：p 为质数且 p ∤ a，则 a<sup>p−1</sup> ≡ 1 (mod p)，于是 a<sup>−1</sup> ≡ a<sup>p−2</sup>。"
      "模 10<sup>9</sup>+7 求逆元时 p − 2 = 1000000005，一次快速幂 30 轮乘法搞定。"
      "（更一般的是欧拉定理 a<sup>φ(m)</sup> ≡ 1，条件只有 gcd(a, m) = 1。）"),
    P("<b>量级感受</b>：gcd 的递归次数不超过 5·log<sub>10</sub>(min(a, b))（拉梅定理），"
      "a、b ≤ 2×10<sup>9</sup> 时不超过 50 层，绝无爆栈风险；快速幂的轮数等于指数的二进制位数，"
      "b ≤ 10<sup>18</sup> 时 60 轮。两个算法在 10<sup>18</sup> 的量级上都只要几十步——这就是“对数级”的含义。"),
])

THINK = [
    "如果要算 a<sup>b</sup> mod m，但 b 是一个 1000 位的十进制字符串（远超 long long），该怎么办？"
    "（提示：指数能不能也“取模”？取模的对象是什么？）",
    "gcd(a, b) = gcd(b, a mod b) 为什么成立？请用“a、b 的公因子集合 = b、a mod b 的公因子集合”这个角度写出证明。",
    "gcd(a, b) · lcm(a, b) = a · b 对两个数成立。三个数的时候还成立吗？lcm(a, b, c) 该怎么算才不会溢出？",
    "扩展欧几里得求出的一组解不唯一。如果要求 x 为最小正数，怎么在 O(1) 内调整（不能暴力试 k）？",
    "若 gcd(a, m) = d &gt; 1，方程 a·x ≡ b (mod m) 有解的条件是什么？有解时不同的解有几个？"
    "怎么把它化归成互质的情形？",
    "快速幂的模板能不能直接用来算矩阵的幂？需要满足什么条件（结合律？单位元？）才能照抄？",
    "为什么 r 和 a 每一步都要取模，而 b 不需要？如果 b 也取模会发生什么？",
]

THINK_A = [
    "别把 1000 位读成整数。按十进制位从左往右推：ans = ans<sup>10</sup> · a<sup>d<sub>i</sub></sup> mod m，"
    "每一步用快速幂算 ans<sup>10</sup>，总共 1000×log10 次乘法。"
    "想走“指数取模”这条路，要模的是 <b>φ(m)</b> 而不是 m：a 与 m 互质时 a<sup>b</sup> ≡ a<sup>b mod φ(m)</sup>；"
    "不互质时要用扩展欧拉定理 a<sup>b</sup> ≡ a<sup>b mod φ(m) + φ(m)</sup>（b ≥ φ(m) 时），而 b 的大小比较又得回到按位处理。"
    "常见错路：把指数对 m 取模——a<sup>b mod m</sup> 和 a<sup>b</sup> 毫无关系；或者用 long long 去读这串数字，直接读失败。",

    "两边公因子集合相等，所以最大元相等。① 若 d | a 且 d | b，由 a mod b = a − (a/b)·b 得 d | (a mod b)，"
    "故 d 也是 b 与 a mod b 的公因子；② 反过来若 d | b 且 d | (a mod b)，则 d | ((a/b)·b + (a mod b)) = a，"
    "故 d 也是 a、b 的公因子。两个方向合起来，两个集合相同，最大元自然相同。"
    "常见错路：只写方向 ①，那只能得到 gcd(a,b) ≤ gcd(b, a mod b)，推不出相等；"
    "还有忘了 b ≠ 0 这个前提（a mod b 要有定义）。",

    "不成立。反例 a = 2、b = 4、c = 8：gcd = 2、lcm = 8，乘积 16，而 abc = 64。"
    "三数的正确关系是 lcm(a,b,c) = abc·gcd(a,b,c) / (gcd(a,b)·gcd(a,c)·gcd(b,c))，代进去得 "
    "64×2/(2×2×4) = 8 ✓——不是“gcd·lcm = 乘积”那种干净形式。"
    "算法上老老实实两步：lcm(lcm(a,b), c)，每一步都 a/gcd*b，乘之前先估一次中间值，必要时上 __int128。"
    "常见错路：以为 gcd·lcm = abc 可以推广，于是拿 a·b·c/gcd 去算，既错又早溢出。",

    "通解是 x = x<sub>0</sub> + k·(m/g)，g = gcd(a, m)，所以周期是 m/g 而不是 m。最小正数解一步算完："
    "<code>t = (x0 % (m/g) + (m/g)) % (m/g); if (t == 0) t += m/g;</code>。"
    "为什么周期是 m/g：a·(x+T) ≡ a·x (mod m) ⟺ m | a·T ⟺ (m/g) | (a/g)·T，而 a/g 与 m/g 互质，故必须 (m/g) | T。"
    "常见错路：对 m 取模，得到的可能是 x<sub>0</sub> + 若干倍 m/g，不是最小；"
    "或者用 while (x &lt; 0) x += m 硬挪——能过小数据，等价于 O(m/g) 的暴力；还有忘了“最小正数”不能是 0。",

    "有解 ⟺ d | b，其中 d = gcd(a, m)；有解时在 [0, m) 内恰好有 <b>d 个</b>解。化归办法是两边同除以 d："
    "a′·x ≡ b′ (mod m′)，a′=a/d、b′=b/d、m′=m/d，此时 gcd(a′, m′)=1，逆元存在，"
    "解出模 m′ 的唯一解 x<sub>0</sub>，原方程的 d 个解就是 x<sub>0</sub> + k·m′（k = 0..d−1）。"
    "常见错路：不知道有 d 个解，只输出一个；或者直接拿 exgcd 的解当答案——它满足的是 a·x + m·y = d，右边不是 b。",

    "能，逐字照抄。快速幂只依赖三件事：乘法有<b>结合律</b>、存在<b>单位元</b>、能反复平方，"
    "矩阵乘法三条全占。改法只有三处：把 1 换成单位矩阵 I（对角线 1、其余 0），把乘法换成矩阵乘法，"
    "每个元素在乘加时都取模。常见错路：把累乘器初始化成全 0 矩阵——那不是单位元，乘完永远是零矩阵；"
    "或者只在最后取模，矩阵乘是 n³ 次累加，中间值撑爆 long long；还有指数为 0 时要返回 I 而不是 0。",

    "r、a 都参与乘法，而同余对乘法封闭：每步乘完立刻降回 [0, m)，结果不变，中间值也不会溢出。"
    "b 是指数，它只决定“乘几次”，对 b 取模等于改变了乘的次数。"
    "反例：a = 2、m = 9、b = 10，2<sup>10</sup> mod 9 = 7；而 b mod 9 = 1，2<sup>1</sup> = 2，完全不是一回事。"
    "指数上唯一合法的“降”是欧拉定理那一类（对 φ(m) 取模），不是随便取模。"
    "常见错路：在循环前顺手写一句 b %= m；或者以为“取模不影响结果”对所有变量都成立。",
]

CHECK = [
    "能默写辗转相除（递归与迭代两种），并说清出口为什么是 b == 0 而不是 b == 1。",
    "知道 std::gcd 的两个参数类型必须一致，能说出 gcd(0, x)、gcd(−12, 18) 各等于什么。",
    "能写出 lcm 的正确写法，并解释先除后乘省下的是哪一次溢出。",
    "能默写快速幂，说清 r 的初值为什么是 1 % mod、b 为什么要用 long long。",
    "能写出 exgcd 并解释回代公式 y = x1 − (a/b)·y1 是怎么从 a mod b 展开得到的。",
    "知道逆元存在的充要条件，能用 exgcd 和费马小定理各写一遍求逆元，并处理负数归一化。",
    "拿到一道乘法可能溢出的题，能判断该用 long long 还是 __int128，并说清 (__int128)a * b 与 (__int128)(a * b) 的区别。",
]

CH2 = CH(
    "青蛙的约会", "P1516", "提高+/省选-", "https://www.luogu.com.cn/problem/P1516",
    [
        P("把一条长度 L 的纬度线看成一个环，坐标 0..L−1，首尾相接。青蛙 A 从坐标 x 出发，每次向前跳 m 米；青蛙 B 从坐标 y 出发，每次向前跳 n 米。两只青蛙每跳一次花的时间相同，并且同时开始跳。"),
        P("求至少跳多少次它们会落在同一个点上；如果永远不可能，输出 Impossible。"),
        P("输入格式：一行五个整数 x、y、m、n、L。"),
        P("输出格式：一行，一个整数表示次数，或者字符串 Impossible。"),
        P("数据范围：1 ≤ x, y, m, n ≤ 2×10⁹，x ≠ y，1 ≤ L ≤ 2.1×10⁹。"),
    ],
    hint=[
        "跳 t 次后 A 在 (x + m·t) mod L，B 在 (y + n·t) mod L。相遇就是这两个数同余。",
        "把式子移项整理成 (m−n)·t ≡ y−x (mod L)，这正是第 37 节那种 a·t + L·k = b 的方程。",
        "扩展欧几里得只解出右边等于 gcd 的那一版；右边不是 gcd 的倍数就无解，是的话还要放大并把解归一到最小非负。",
    ],
    idea=[
        "列方程：(m−n)·t ≡ (y−x) (mod L)。记 a = (m−n) mod L、b = (y−x) mod L，先都归一到 [0, L)。",
        "它等价于求整数解 a·t + L·k = b。裴蜀定理：有解 ⟺ gcd(a, L) | b。",
        "先 exgcd(a, L, u, v) 得到 a·u + L·v = g。若 b % g ≠ 0 → 输出 Impossible。",
        "放大：a·(u·b/g) + L·(v·b/g) = b，所以一个特解是 t₀ = u·(b/g)。",
        "通解 t = t₀ + k·(L/g)：t 每加 L/g 就回到同一个同余类。所以最小非负解就是把 t₀ 对 L/g 取模再归正。",
        "为什么周期是 L/g 而不是 L：a·(t+T) ≡ a·t (mod L) ⟺ L | a·T ⟺ (L/g) | (a/g)·T，而 a/g 与 L/g 互质，故必须 (L/g) | T。",
        "溢出检查：u &lt; L/g ≤ 2.1×10⁹，b/g &lt; L/g，乘积 &lt; 4.5×10¹⁸ &lt; 9.2×10¹⁸，long long 够用。",
        "复杂度：一次 exgcd，O(log L) ≈ 31 层递归。",
    ],
    code=r'''#include <bits/stdc++.h>
using namespace std;

typedef long long ll;

ll exgcd(ll a, ll b, ll &x, ll &y) {       // a·x + b·y = gcd(a, b)
    if (b == 0) { x = 1; y = 0; return a; }
    ll x1, y1;
    ll g = exgcd(b, a % b, x1, y1);
    x = y1;
    y = x1 - (a / b) * y1;
    return g;
}

int main() {
    ll x, y, m, n, L;
    scanf("%lld %lld %lld %lld %lld", &x, &y, &m, &n, &L);

    // 相遇条件 (x + m·t) ≡ (y + n·t) (mod L)  →  (m-n)·t ≡ y-x (mod L)
    ll a = ((m - n) % L + L) % L;          // 方程左边系数，先归一到 [0, L)
    ll b = ((y - x) % L + L) % L;          // 方程右边常数，同样归一

    ll u, v;
    ll g = exgcd(a, L, u, v);              // a·u + L·v = g
    if (b % g != 0) { puts("Impossible"); return 0; }   // 裴蜀定理：右边不是 g 的倍数就无解

    ll mod = L / g;                        // 解在模 mod 意义下唯一
    u = (u % mod + mod) % mod;             // 归一成最小非负解
    u = u * (b / g) % mod;                 // 把 a·u = g 放大成 a·u = b
    printf("%lld\n", u);
    return 0;
}
''',
    explain=[
        ("ll a = ((m - n) % L + L) % L;", "系数先归一到 [0, L)：m &lt; n 时 (m−n) 为负，不归一解会带负号。"),
        ("ll g = exgcd(a, L, u, v);", "解 a·u + L·v = g，u、v 靠引用带出，返回值是 gcd。"),
        ("if (b % g != 0) { puts(\"Impossible\"); return 0; }", "裴蜀定理的判定：右边不是 gcd 的倍数就没有整数解。"),
        ("ll mod = L / g;", "解的周期。a = 2、L = 6 时 g = 2，周期是 3，用 L = 6 会把同一个解数成两个。"),
        ("u = (u % mod + mod) % mod;", "把特解归一到 [0, mod)，负解也能变成最小非负解。"),
        ("u = u * (b / g) % mod;", "放大到右边等于 b。先除后乘，中间值不会超过 4.5×10¹⁸。"),
    ],
    pitfalls=[
        "归一化只写 u % mod 不加 mod：exgcd 常给出负解，直接输出负数。",
        "模数用 L 而不是 L/g：解集是 t₀ + k·(L/g)，用 L 归一化会得到偏大的 t，样例就过不了。",
        "(m−n) 不归一到非负：系数为负时 b 也必须同步归一，否则正负混用，解错符号。",
        "用 int 存 u·(b/g)：约 4×10¹⁸，long long 才装得下，int 直接溢出。",
    ],
    sample="输入：\n1 2 3 4 5\n输出：\n4",
)

CH = CH(
    "同余方程", "P1082", "普及/提高-", "https://www.luogu.com.cn/problem/P1082",
    [P("求关于 x 的同余方程 a·x ≡ 1 (mod b) 的最小正整数解。"),
     P("输入：一行两个正整数 a、b（2 ≤ a, b ≤ 2×10<sup>9</sup>），用一个空格隔开。"),
     P("输出：一行一个正整数 x<sub>0</sub>，即最小正整数解。输入数据保证一定有解。")],
    hint=["把“a·x 除以 b 余 1”翻译成等式：a·x − 1 是 b 的倍数，也就是存在整数 y 使 a·x + b·y = 1。",
          "求 a·x + b·y = gcd(a, b) 的一组解是扩展欧几里得的标准任务。先想清楚：本题里 gcd(a, b) 必须等于几，方程才有解？",
          "解出来的 x 可能为负、也可能大于 b。怎么把它挪进 1 到 b−1 之间？注意 C++ 里负数取模的结果。"],
    idea=["a·x ≡ 1 (mod b) 等价于 b | (a·x − 1)，即存在整数 y 使 a·x − 1 = b·y，也就是 a·x + b·(−y) = 1。"
          "令 y′ = −y，问题变成解 a·x + b·y′ = 1。",
          "由裴蜀定理，a·x + b·y 能取到的最小正数恰是 gcd(a, b)。题目保证有解，所以 gcd(a, b) 只能是 1。",
          "调用 exgcd(a, b, x, y)，返回时 x 满足 a·x + b·y = gcd(a, b) = 1，它就是一组解。",
          "通解是 x + k·b：因为 a·(x + k·b) = a·x + k·a·b ≡ a·x (mod b)。所以把所有解对 b 取模，"
          "落进 [0, b) 的那个就是唯一答案。",
          "C++ 的 % 对负数返回负余数，必须写成 (x % b + b) % b。又因为 b ≥ 2 且 a·x ≡ 1 ≠ 0，"
          "所以结果不会等于 0，落在 1..b−1，正是最小正整数解。",
          "复杂度：与辗转相除同阶，b ≤ 2×10<sup>9</sup> 时递归不超过 50 层，O(log b)。"],
    code=r'''#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

// 求 a*x + b*y = gcd(a,b) 的一组整数解，返回 gcd(a,b)
ll exgcd(ll a, ll b, ll &x, ll &y) {
    if (b == 0) {                       // 出口：a*1 + 0*0 = a
        x = 1; y = 0;
        return a;
    }
    ll x1, y1;
    ll g = exgcd(b, a % b, x1, y1);     // 规模先变小
    x = y1;                             // 回代：a 的系数
    y = x1 - (a / b) * y1;              // 回代：b 的系数
    return g;
}

int main() {
    ll a, b, x, y;
    cin >> a >> b;

    exgcd(a, b, x, y);                  // 得到 a*x + b*y = gcd(a,b) = 1
    x = (x % b + b) % b;                // 归一化到 [0, b)：先 % 再 +b 再 %
    cout << x << "\n";
    return 0;
}''',
    explain=[
        ("ll exgcd(ll a, ll b, ll &x, ll &y)", "x、y 用引用传递，答案靠它们带出；返回值是 gcd。"
                                              "a、b 都是 long long，因为上限 2×10^9 已经贴着 int 的边缘。"),
        ("if (b == 0) { x = 1; y = 0; return a; }",
         "递归出口，也就是辗转相除的最后一步：此时 gcd = a，取 x = 1、y = 0 使 a·1 + 0·0 = a 成立。"),
        ("exgcd(b, a % b, x1, y1)", "把 (a, b) 换成 (b, a mod b)。这是整个算法唯一“变小”的地方，"
                                    "也是它必然终止的原因。"),
        ("x = y1; y = x1 - (a / b) * y1;", "回代。由 b·x1 + (a − (a/b)·b)·y1 = g 直接对照系数得到，不能写反。"),
        ("x = (x % b + b) % b;", "★ 归一化。exgcd 给的解可能为负（例如 a = 2、b = 3 时 x = −1），"
                                 "负余数仍是负数，必须加 b 再取模才能落进 [0, b)。"),
        ("cout &lt;&lt; x", "b ≥ 2 且 a·x ≡ 1 (mod b)，所以 x 不会是 0；归一化后的值就是最小正整数解。"),
    ],
    pitfalls=["输出 x 而不归一化：样例 3 10 恰好是正数 7，看不出问题；换 a = 2、b = 3 会输出 −1（正确答案 2），WA。",
              "把 <code>x % b</code> 当成“取最小正数”：C++ 的余数跟随被除数符号，负数取模还是负数。",
              "回代公式写错：把 <code>x = y1; y = x1 - (a/b)*y1;</code> 里的 x1、y1 对调，"
              "样例 3 10 立刻输出 1 而不是 7。这两行必须从 a mod b 的展开式自己推一遍。",
              "把递归参数换成 <code>exgcd(b, a % b, y, x)</code>（另一种紧凑写法）却照抄上面两行回代公式——"
              "两种写法必须成套使用，混用会得到错误的符号。",
              "参数用 int：a、b 到 2×10<sup>9</sup>，中间 <code>a / b</code>、乘法都贴着 int 上限，统一 long long 更安全。"],
    sample="输入：\n3 10\n输出：\n7",
)

LESSONS = [LESSON(
    37, "最大公约数、同余与快速幂",
    "数论应用的三件套：辗转相除求 gcd 与 lcm、扩展欧几里得解同余方程与逆元、"
    "二进制拆分求 a^b mod m。每一件都附一条防溢出规矩：lcm 先除后乘、快速幂每步取模、乘积超范围上 __int128。",
    65, ["gcd", "扩展欧几里得", "快速幂"], "普及/提高-",
    SEC, math=M, think=THINK, think_a=THINK_A, check=CHECK, challenge=CH, challenge2=CH2,
    refs=["《算法竞赛入门笔记》数论章节：gcd、同余与快速幂",
          "《算法竞赛进阶指南》0x33 同余：扩展欧几里得与逆元",
          "《算法竞赛试炼场：洛谷300题精析》P1226、P1082 两题的精析",
          "《算法竞赛黄金法则：提高算法和思考力的77项技巧》第 31 条：把乘法搬到大类型里算"],
)]
