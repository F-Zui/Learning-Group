# -*- coding: utf-8 -*-
"""第一部分：常用非算法提速工具模板。"""

PART1 = [
    ("h1", "第一部分  通用工具与提速模板"),
    ("p", "本部分收录与具体算法无关、但每一道题都会用到的\"工具型\"代码。它们不改变算法的复杂度，"
          "却能显著减少代码量、避免低级错误、并在大数据下把程序从 TLE 边缘拉回来。"
          "建议把这一部分的代码整体放进你自己的 template.cpp，比赛时只写主逻辑。"),

    # ============================================================ 0 骨架
    ("h2", "1. 竞赛代码骨架（每道题的第一件事）"),
    ("usage", "用途", "固定开头的三行：万能头 + 命名空间 + 关闭同步流。它解决三件事："
                      "不用记需要哪个头文件；不用写 std:: 前缀；让 cin/cout 的速度接近 scanf/printf。"),
    ("scene", "应用场景", "所有需要用 cin/cout 的题目。当输入规模达到 10^5~10^6 个数时，"
                          "不加 ios::sync_with_stdio(false) 会直接 TLE。"),
    ("code", r'''
#include <bits/stdc++.h>          // GCC 万能头：一次包含所有标准库
using namespace std;

int main() {
    ios::sync_with_stdio(false);   // ① 关闭 C 流与 C++ 流的同步
    cin.tie(nullptr);              // ② 解除 cin 与 cout 的绑定（cin 前不再自动 flush cout）

    // ... 你的代码 ...

    return 0;
}
'''),
    ("bullets", [
        ("① ", ("ios::sync_with_stdio(false);", {"name": "Consolas"})),
        ("：默认情况下 cin/cout 每读一次都会和 scanf/printf 共享的缓冲区同步，代价很高。关掉之后 cin 速度提升 3~5 倍。"),
        ("副作用：关闭同步后，", ("cin", {"name": "Consolas"}), " 与 ",
         ("scanf", {"name": "Consolas"}), " 不能再混用。若题目要用 ",
         ("printf", {"name": "Consolas"}), " 格式化输出，请全程只用一套。"),
        ("② ", ("cin.tie(nullptr);", {"name": "Consolas"})),
        ("：默认 cin 会绑定 cout，每次读取前先刷新输出缓冲区（为了交互题的\"先问后答\"语义）。"
         "解除绑定后输出不再被频繁刷新，速度更快。"),
        ("注意：", ("#include <bits/stdc++.h>", {"name": "Consolas"}),
         " 是 GCC/MinGW 特有的，MSVC 不可用；绝大多数评测机（洛谷、Codeforces、AtCoder）都用 GCC，可放心使用。"),
    ]),
    ("warnbox", "常见报错与坑", [
        "编译错误 'bits/stdc++.h: No such file or directory' → 本地用了 MSVC/Clang 且未配置，换 MinGW-w64（g++）即可。",
        "关闭同步后混用 cin 与 scanf，读入顺序错乱导致 WA（两者缓冲区不共享）。",
        "只写了 sync_with_stdio 忘了 cin.tie(nullptr)，在输出量大的题目上仍然 TLE。",
        "把输出语句写在死循环里 → OLE（Output Limit Exceeded）。",
    ]),

    # ============================================================ 1 快读
    ("h2", "2. 快速读入（快读）"),
    ("usage", "用途", "用 getchar() 逐字符读出整数，比 cin 再快 3~5 倍，比 scanf 快 2 倍左右。"
                      "是卡常数题（n ≥ 10^6）最常用的救命工具。"),
    ("scene", "应用场景", "输入规模极大（n×m ≥ 10^6~10^7）、或需要反复读入的题目；"
                          "以及读入量不大但循环常数敏感、需要把 I/O 时间压到极限的场合。"),
    ("code", r'''
// ---------- 通用快读：支持负号，遇非数字字符停止 ----------
inline int readInt() {
    int x = 0, f = 1;
    char c = getchar();
    while (c < '0' || c > '9') {          // 跳过空白/换行
        if (c == '-') f = -1;             // 记录负号
        c = getchar();
    }
    while (c >= '0' && c <= '9') {        // 逐位累加
        x = x * 10 + (c - '0');
        c = getchar();
    }
    return x * f;
}

// ---------- long long 版本 ----------
inline long long readLL() {
    long long x = 0; int f = 1; char c = getchar();
    while (c < '0' || c > '9') { if (c == '-') f = -1; c = getchar(); }
    while (c >= '0' && c <= '9') { x = x * 10 + (c - '0'); c = getchar(); }
    return x * f;
}
'''),
    ("bullets", [
        ("核心思想：", ("getchar()", {"name": "Consolas"}),
         " 是最底层的字符读取，没有格式化解析的开销。"),
        ("关键行 ", ("x = x * 10 + (c - '0')", {"name": "Consolas"}),
         "：把字符 '3' 变成数字 3，靠的是 ASCII 码差值，这一技巧在字符串处理中反复出现。"),
        ("inline 的作用：建议编译器内联展开，避免函数调用开销；对 I/O 密集型代码有意义。"),
        ("【拓展】若输入只含非负整数且末尾一定有分隔符，可以去掉负号判断，再快一点点。"),
        ("【拓展】输出量同样巨大时配一个快写：", ("putchar", {"name": "Consolas"}),
         " 逐位输出（见下一节）。"),
    ]),
    ("warnbox", "常见报错与坑", [
        "读入到文件末尾时 getchar() 返回 EOF(-1)，没有终止条件会死循环 → TLE。竞赛数据保证格式正确，通常不必处理，但要心里有数。",
        "负数读入后 x 已经乘过符号，若再用 abs() 之类的处理会重复取正。",
        "忘记处理 '\\r'（Windows 换行）：由于判断是 c<'0'||c>'9'，'\\r' 会被自动跳过，一般无问题。",
        "返回值类型写成 int 却读 long long 数据 → 数据被截断，答案偏小（最隐蔽的 WA）。",
        "快读与 scanf/cin 混用时，编译器缓冲行为不同，可能读串行；使用快读后就统一用快读。",
    ]),

    # ============================================================ 2 快写
    ("h2", "3. 快速输出（快写）与固定格式输出"),
    ("usage", "用途", "递归或循环地用 putchar 逐位输出整数，避免 cout 的格式化开销；"
                      "同时给出控制小数位数、补前导零等常见格式要求的标准写法。"),
    ("scene", "应用场景", "输出规模超过 10^6 个数；或需要严格按格式输出（保留 k 位小数、"
                          "不足补 0、八进制/十六进制、科学计数法）。"),
    ("code", r'''
// ---------- 整数快写 ----------
inline void writeInt(int x) {
    if (x < 0) { putchar('-'); x = -x; }
    if (x > 9) writeInt(x / 10);   // 先输出高位
    putchar(x % 10 + '0');         // 再输出末位
}

// ---------- 固定格式输出（printf 家族） ----------
printf("%d\n", n);                     // 整数
printf("%lld\n", (long long)n);        // long long 必须用 %lld
printf("%.3f\n", x);                   // 保留 3 位小数（四舍五入）
printf("%05d\n", n);                   // 宽度 5，不足补前导 0
printf("%-5d|\n", n);                  // 左对齐
printf("%x %o\n", n, n);               // 十六进制 / 八进制

// ---------- 固定格式输出（cout 家族） ----------
cout << fixed << setprecision(3) << x << '\n';   // 固定 3 位小数，需 <iomanip>
cout << setw(5) << setfill('0') << n << '\n';    // 宽度 5，补 0
'''),
    ("bullets", [
        ("", ("fixed << setprecision(k)", {"name": "Consolas"}),
         " 表示\"小数点后固定 k 位\"；不加 fixed 时 setprecision(k) 表示\"有效数字 k 位\"，两者完全不同。"),
        ("浮点输出默认四舍五入，但受二进制误差影响：", ("0.5", {"name": "Consolas"}),
         " 这类边界值可能输出 0.4 或 0.5。题目要求四舍五入时，稳妥做法是先加一个极小量 "
         "（如 1e-9）再输出，或直接用整数运算。"),
        ("换行符优先用 ", ("'\\n'", {"name": "Consolas"}),
         "；仅在需要立刻刷新（交互题、调试）时才用 ", ("endl", {"name": "Consolas"}),
         "，因为 endl 会强制 flush，在循环中大量使用会严重拖慢速度。"),
        ("【拓展】如果答案可能超过 long long，输出要用高精度模板，不能靠 %lld。"),
    ]),
    ("warnbox", "常见报错与坑", [
        "printf 用 %d 输出 long long → 输出乱码或截断；必须 %lld。",
        "cout 输出 double 默认只有 6 位有效数字，1e-10 这类小数会变成 0 或 1e-10 形式 → WA。",
        "只写 setprecision 没写 fixed，精度含义变化，输出位数不符 → WA。",
        "setfill('0') 是持久的，后面所有 setw 都补 0；忘记 setfill(' ') 还原会污染后续输出。",
        "输出行末多出空格或缺少最后的换行，某些 OJ 会判 WA（洛谷通常忽略行末空格）。",
        "在 int 运算中直接 printf(\"%.2f\", a/b)（a、b 均为 int）→ 整数除法已经截断，输出必然错误。",
    ]),

    # ============================================================ 3 常量
    ("h2", "4. 常用常量与类型范围（写题前先看一眼）"),
    ("usage", "用途", "把常用极值、精度、模数写成常量，避免在代码里手抖写错；"
                      "同时明确每种类型的取值范围，从源头避免溢出。"),
    ("scene", "应用场景", "几乎所有题目。写 DP、二分、最短路、取最值时都要用到 INF 与 eps。"),
    ("code", r'''
const int    INF   = 0x3f3f3f3f;              // 约 1.06e9，两倍不溢出 int
const long long LINF = 0x3f3f3f3f3f3f3f3fLL;  // 约 4.5e18，两倍不溢出 long long
const double EPS   = 1e-8;                    // 浮点比较精度
const double PI    = acos(-1.0);              // 3.141592653589793
const int    MOD   = 1000000007;              // 1e9+7，常用模数
// const int MOD   = 998244353;               // NTT 友好模数
const int    dx[4] = {0, 0, 1, -1};           // 四方向：右、左、下、上
const int    dy[4] = {1, -1, 0, 0};
const int    dx8[8] = {1, 1, 1, 0, 0, -1, -1, -1};   // 八方向
const int    dy8[8] = {1, 0, -1, 1, -1, 1, 0, -1};
'''),
    ("typetable",),
    ("bullets", [
        ("为什么用 ", ("0x3f3f3f3f", {"name": "Consolas"}),
         " 当 INF：它约等于 10.6 亿，两个 INF 相加（做松弛时常见的 INF+INF）是 21.2 亿，"
         "仍然小于 int 上限 21.47 亿，不会溢出成负数。用 1e9 也可以，用 INT_MAX 则极易溢出。"),
        ("mem 初始化技巧：", ("memset(dis, 0x3f, sizeof(dis));", {"name": "Consolas"}),
         " 可以把每个字节填成 0x3f，于是 int 数组每个元素正好是 0x3f3f3f3f。"
         "注意 memset 只能按字节填充，填 0 或 -1 才是安全的。"),
    ]),

    # ============================================================ 4 质数
    ("h2", "5. 质数：判定、筛表与分解质因数"),
    ("usage", "用途", "\"质数\"类题目的一切基础：判断单个数是否质数（试除法）、"
                      "批量生成质数表（埃氏筛 / 线性筛）、把一个数分解成质因数乘积。"),
    ("scene", "应用场景", "求第 k 个质数、统计区间内质数个数、质因数分解、"
                          "欧拉函数 / 莫比乌斯函数（线性筛的典型用途）、因数枚举类构造题。"),
    ("code", r'''
// ---------- (1) 单个数判定：O(sqrt(n)) ----------
bool isPrime(long long n) {
    if (n < 2) return false;                  // 0、1 都不是质数
    for (long long i = 2; i * i <= n; ++i)    // 只试到 sqrt(n)
        if (n % i == 0) return false;
    return true;
}

// 6k±1 优化版：大于 3 的质数一定形如 6k±1，可省掉 2/3 的试除
bool isPrimeFast(long long n) {
    if (n < 2) return false;
    if (n % 2 == 0) return n == 2;
    if (n % 3 == 0) return n == 3;
    for (long long i = 5; i * i <= n; i += 6)
        if (n % i == 0 || n % (i + 2) == 0) return false;
    return true;
}

// ---------- (2) 埃氏筛：O(n log log n)，生成 [1, n] 质数表 ----------
const int MAXN = 1000005;
bool isp[MAXN];                // isp[i] = i 是否为质数（全局变量默认全 false）
vector<int> primes;

void sieve(int n) {
    fill(isp, isp + n + 1, true);          // 先假设全是质数
    isp[0] = isp[1] = false;               // 0、1 特殊处理
    for (int i = 2; (long long)i * i <= n; ++i) {
        if (!isp[i]) continue;
        for (long long j = 1LL * i * i; j <= n; j += i)  // 从 i*i 开始划掉
            isp[j] = false;
    }
    for (int i = 2; i <= n; ++i)
        if (isp[i]) primes.push_back(i);
}

// ---------- (3) 线性筛（欧拉筛）：O(n)，顺带记录最小质因子 ----------
int minp[MAXN];                // minp[i] = i 的最小质因子

void linearSieve(int n) {
    for (int i = 2; i <= n; ++i) {
        if (!minp[i]) { minp[i] = i; primes.push_back(i); }  // i 是质数
        for (int p : primes) {
            if (p > minp[i] || 1LL * i * p > n) break;       // 关键：p 不超过最小质因子
            minp[i * p] = p;                                  // 每个合数只被最小质因子筛一次
        }
    }
}

// ---------- (4) 分解质因数：配合 minp 可做到 O(log n) ----------
vector<pair<long long,int>> factorize(long long n) {   // 试除法 O(sqrt(n))
    vector<pair<long long,int>> res;
    for (long long i = 2; i * i <= n; ++i) {
        if (n % i) continue;
        int c = 0;
        while (n % i == 0) { n /= i; ++c; }
        res.push_back({i, c});
    }
    if (n > 1) res.push_back({n, 1});       // 剩下的一定是质数
    return res;
}

void factorByMinp(int n) {                  // 用 minp 快速分解
    while (n > 1) {
        int p = minp[n], c = 0;
        while (n % p == 0) { n /= p; ++c; }
        printf("%d^%d ", p, c);
    }
}
'''),
    ("bullets", [
        ("埃氏筛的两个关键优化：", ("i * i <= n", {"name": "Consolas"}),
         "（大于 sqrt(n) 的质数其倍数已被更小的质数筛过）与 ", ("j 从 i*i 开始", {"name": "Consolas"}),
         "（i 的 2i、3i… 已被更小的质数划掉）。欠这两条虽然答案仍然对，但会慢好几倍。"),
        ("线性筛的核心不变量：每个合数", (" 只被它的最小质因子筛掉一次", {"bold": True}),
         "，因此总复杂度严格 O(n)。判断条件 ", ("p > minp[i]", {"name": "Consolas"}),
         " 就是保证这一点，写错会退化成埃氏筛甚至重复筛。"),
        ("算 ", ("i*i", {"name": "Consolas"}),
         " 时务必先转 long long：", ("(long long)i * i", {"name": "Consolas"}),
         "。i 到 10^5 时 i*i 才 10^10，int 已经溢出 → 负数 → 循环行为完全错误。"),
        ("【拓展】有了 minp 后可以 O(n) 预处理欧拉函数 φ、莫比乌斯函数 μ、约数个数等积性函数，"
         "这是线性筛最实用的延伸。"),
        ("【拓展】区间筛：求 [L, R] 内质数（R 可达 10^12，R-L ≤ 10^6）时，"
         "先用埃氏筛出 sqrt(R) 以内的质数，再用它们去标记 [L, R]。"),
    ]),
    ("warnbox", "常见报错与坑", [
        "isp[0] = isp[1] = false 漏写 → 输出里凭空多出 0 和 1（最高频的错误）。",
        "筛表上界写小：循环到 i < n 而不是 i <= n，导致 n 本身没被判断 → WA。",
        "i*i 溢出成负数 → for 循环条件恒真，程序死循环 / 段错误 RE。",
        "数组开小 1：MAXN = 1000000 而题目 n = 10^6 需要下标到 10^6 → 越界，RE 或静默改数据。",
        "试除法里写了 i <= n / i 却忘了 n 变化；或写成 i*i <= n 但 i 是 int 且 n 很大 → 溢出。",
        "分解质因数后忘记处理 n > 1 的剩余部分 → 少了最后一个质因子（如 10 = 2 × 5 只输出 2）。",
        "线性筛内层 break 条件写错（如写成 p > i），导致某些合数被多次赋值 minp → 结果错、变慢。",
        "多组数据下 primes 与 minp 没有在每组开始前清空 / 重新筛 → 第二组结果异常。",
    ]),

    # ============================================================ 5 数论工具
    ("h2", "6. 数论小工具：gcd / lcm / 快速幂 / 取模"),
    ("usage", "用途", "竞赛里出现频率极高的四个小函数：最大公约数、最小公倍数、"
                      "快速幂（含取模）、以及安全取模与防溢出乘法。"),
    ("scene", "应用场景", "分数化简、同余问题、组合数取模、矩阵快速幂、"
                          "以及一切出现\"答案对 1e9+7 取模\"的题目。"),
    ("code", r'''
// ---------- (1) 最大公约数 ----------
long long gcd(long long a, long long b) {          // 辗转相除
    while (b) { long long t = a % b; a = b; b = t; }
    return a;
}
// C++17 起标准库自带：std::gcd(a, b) 与 std::lcm(a, b)（在 <numeric> 中，万能头已包含）

// ---------- (2) 最小公倍数：先除后乘，防止溢出 ----------
long long lcm(long long a, long long b) {
    return a / gcd(a, b) * b;      // 千万不能写成 a * b / gcd(a,b)
}

// ---------- (3) 快速幂：a^b mod m，O(log b) ----------
long long qpow(long long a, long long b, long long m = MOD) {
    long long r = 1 % m;
    a %= m;
    while (b) {
        if (b & 1) r = r * a % m;   // b 的当前二进制位为 1
        a = a * a % m;              // 底数平方
        b >>= 1;                    // 指数右移
    }
    return r;
}

// ---------- (4) 防溢出的取模乘法（用于 m > 1e9 或模数本身很大时） ----------
long long mulmod(long long a, long long b, long long m) {
    return (long long)((__int128)a * b % m);
}

// ---------- (5) 负数取模修正 ----------
long long norm(long long x, long long m) { return (x % m + m) % m; }
'''),
    ("bullets", [
        ("", ("a / gcd(a,b) * b", {"name": "Consolas"}),
         " 的写法把除法放在前面，中间结果最多是答案本身；写成 a*b/gcd 则中间乘积可能溢出 long long。"),
        ("快速幂的本质：把指数 b 按二进制拆开，例如 a^13 = a^8 · a^4 · a^1，"
         "每步只做一次平方，共 log b 次乘法。"),
        ("", ("1 % m", {"name": "Consolas"}), " 是为了兼容 m = 1 的边界情况（此时答案应为 0）。"),
        ("负数取模：C++ 中 -3 % 5 == -3，数学上应是 2。做减法后取模一定要加修正函数 norm，"
         "或写 ", ("(x % MOD + MOD) % MOD", {"name": "Consolas"}), "。"),
        ("【拓展】__int128 是 GCC 提供的 128 位整数，不支持 cin/cout，"
         "只能参与运算或手写输出，是绕过 10^18 × 10^18 溢出的最简手段。"),
        ("【拓展】需要求逆元时：模数为质数用费马小定理 ", ("qpow(a, m-2, m)", {"name": "Consolas"}),
         "；模数任意则用扩展欧几里得。"),
    ]),
    ("warnbox", "常见报错与坑", [
        "lcm 写成 a*b/gcd → 大数相乘溢出，答案变负数或错值。",
        "gcd 传入负数：辗转相除对负数结果不确定（C++ 取模符号跟随被除数），应先取绝对值。",
        "快速幂里忘记 a %= m，当 a 本身大于 m 时中间乘积溢出。",
        "qpow 的返回值用 int 接收 → 10^9 级别的结果被截断。",
        "把 gcd 与 lcm 的参数顺序、个数写错（lcm 只接受两个参数，多个数要循环求）。",
        "模板参数 m 默认 MOD，但题目换模数（如 998244353）时忘记传参 → 结果系统性错误。",
        "库函数 std::gcd 在 C++14 及以前不存在，提交时选错语言版本会 CE。",
    ]),

    # ============================================================ 6 字符串工具
    ("h2", "7. 字符串与字符处理工具"),
    ("usage", "用途", "把\"读入一行含空格的字符串\"、\"字符与数字互转\"、"
                      "\"大小写转换\"、\"分割字符串\"这几件高频小事封装好。"),
    ("scene", "应用场景", "标题统计、单词计数、字符串模拟、格式化解析、"
                          "读入含空格的句子（cin >> s 遇空格就停，必须用 getline）。"),
    ("code", r'''
string s;
getline(cin, s);                    // 读入整行（含空格），读到 '\n' 为止
cin >> s;                           // 读入一个\"词\"，遇空格/换行停止

cin.ignore();                       // 清掉缓冲区里残留的换行符（cin>>n 之后接 getline 时必须）
cin.ignore(1000, '\n');             // 最多丢弃 1000 个字符，或直到遇到换行

// ---------- 字符 <-> 数字 ----------
int d = c - '0';                    // 数字字符 -> 数值：'7' -> 7
char c = '0' + d;                   // 数值 -> 数字字符：7 -> '7'
int x = stoi(s);                    // string -> int（可能抛异常，数据保证合法时可直接用）
long long y = stoll(s);
string t = to_string(x);            // 数字 -> string

// ---------- 大小写转换 ----------
if (c >= 'a' && c <= 'z') c -= 32;  // 小写转大写（'a'-'A' == 32）
c = toupper(c); c = tolower(c);     // 库函数版本，返回 int，需转回 char
for (char &ch : s) ch = tolower(ch);

// ---------- 常用成员函数 ----------
s.size();  s.empty();               // 长度 / 是否为空（size() 返回无符号数，见易错点）
s.substr(pos, len);                 // 从 pos 开始取 len 个字符；len 省略则取到末尾
s.find(t);                          // 返回首次出现位置，找不到返回 string::npos
s.erase(pos, len);                  // 删除
s.insert(pos, t);                   // 插入
s.replace(pos, len, t);             // 替换
s.append(t);  s += t;               // 追加
reverse(s.begin(), s.end());        // 反转整个字符串（<algorithm>）
sort(s.begin(), s.end());           // 按 ASCII 排序

// ---------- 判断字符类别 ----------
isdigit(c);  isalpha(c);  isalnum(c);  isspace(c);   // 参数建议转成 unsigned char
'''),
    ("bullets", [
        ("", ("cin >> n", {"name": "Consolas"}), " 之后紧跟 ", ("getline", {"name": "Consolas"}),
         " 会读到一个空行——因为 >> 把数字读走后，换行符还留在缓冲区。"
         "这是新手最常见的\"莫名少读一行\"原因，解法是中间加一句 ", ("cin.ignore()", {"name": "Consolas"}), "。"),
        ("", ("s.size()", {"name": "Consolas"}), " 返回的是 ", ("size_t（无符号）", {"bold": True}),
         "。写 ", ("for (int i = 0; i + 1 < s.size(); ++i)", {"name": "Consolas"}),
         " 是安全的，但写 ", ("i - s.size()", {"name": "Consolas"}),
         " 这种减法一旦为负就会变成一个巨大的正数 → 越界 RE。"),
        ("", ("find", {"name": "Consolas"}), " 找不到时返回 ", ("string::npos", {"name": "Consolas"}),
         "（一个极大的无符号数），判断时应写 ", ("if (s.find(t) == string::npos)", {"name": "Consolas"}),
         "，不要和 -1 比较。"),
        ("【拓展】", ("isdigit", {"name": "Consolas"}), " 等函数的参数若传负数会 UB，"
         "稳妥写法是 ", ("isdigit((unsigned char)c)", {"name": "Consolas"}), "。"),
        ("【拓展】需要按分隔符切分字符串时，可用 ", ("stringstream", {"name": "Consolas"}),
         "：", ("while (ss >> word) { ... }", {"name": "Consolas"}),
         "，它能自动跳过任意多个空白符。"),
    ]),
    ("warnbox", "常见报错与坑", [
        "getline 读进来是空串 → 上一步 >> 留下的换行没清（加 cin.ignore()）。",
        "cin >> s 读不到含空格的标题 → 用错读入方式，应改 getline。",
        "getline 与 >> 混用后行号整体错位，答案莫名其妙差一行。",
        "s.size() - 1 在 s 为空时下溢成巨大正数 → 下标越界 RE。",
        "下标访问 s[i] 越界不会报错，会得到 '\\0' 或垃圾值 → 逻辑错误而非崩溃（更难查）。",
        "用 char 存中文字符：UTF-8 下一个汉字占 3 字节，逐字节处理必然错乱。",
        "toupper/tolower 忘记写回变量（它们不修改原值，只返回新值）。",
        "stoi 遇到非数字串会抛 std::invalid_argument → RE。",
    ]),

    # ============================================================ 7 浮点
    ("h2", "8. 浮点数比较与精度控制"),
    ("usage", "用途", "浮点数不能用 == 比较；本模板给出比较大小、取整、"
                      "以及把浮点误差控制在可接受范围内的标准写法。"),
    ("scene", "应用场景", "几何题判等、二分实数答案、概率期望题、"
                          "以及所有要求输出小数的题目。"),
    ("code", r'''
const double EPS = 1e-8;

bool eq(double a, double b)  { return fabs(a - b) < EPS; }        // 相等
bool lt(double a, double b)  { return a < b - EPS; }              // 严格小于
bool le(double a, double b)  { return a < b + EPS; }              // 小于等于
int  sgn(double x)           { return x < -EPS ? -1 : (x > EPS ? 1 : 0); }

// 实数二分的固定循环次数写法（比 while (r-l > EPS) 更稳）
double lo = 0, hi = 1e9;
for (int it = 0; it < 100; ++it) {          // 100 次迭代精度已达极限
    double mid = (lo + hi) / 2;
    if (check(mid)) lo = mid; else hi = mid;
}
printf("%.6f\n", lo);

// 取整
floor(x);  ceil(x);  round(x);              // 向下 / 向上 / 四舍五入
(int)(x + 0.5)                              // 非负数四舍五入的常用写法
'''),
    ("bullets", [
        ("EPS 取多大：一般 1e-8。若数据量级到 10^9，EPS 要相应放大到 1e-6 左右，"
         "否则\"本该相等\"的两个数因误差被判不等。"),
        ("实数二分推荐\"固定迭代 100 次\"而不是 while(r-l>EPS)："
         "后者在 EPS 过小、或区间因精度已经无法再缩小时会死循环 → TLE。"),
        ("【拓展】精度不够时考虑换成长 double（", ("long double", {"name": "Consolas"}),
         "，输入用 %Lf）：有效位数从 15 位提升到 18 位左右。"),
        ("【拓展】能不用浮点就不用：涉及金额、比例时优先把式子乘上倍数化整数运算，"
         "可以彻底消除误差。"),
    ]),
    ("warnbox", "常见报错与坑", [
        "if (a == b) 判断浮点相等 → 几乎永远不成立，逻辑失效。",
        "while (r - l > 1e-12) 二分 → 精度到达 double 极限后死循环 TLE。",
        "输入 double 用 %f 读（或 long double 用 %lf 读）→ 值完全错误；long double 必须 %Lf。",
        "忘记 EPS 就写 a < b 做下取整判断，边界值少算 1。",
        "printf 输出浮点没指定精度，OJ 按严格比对判 WA。",
        "整数除法写成 a / b 却期望小数结果（应写 1.0 * a / b 或 (double)a / b）。",
    ]),

    # ============================================================ 8 调试
    ("h2", "9. 调试工具箱：对拍、断言与中间输出"),
    ("usage", "用途", "\"我的代码样例过了但 WA\"时最有效的三种自查手段："
                      "打印中间状态、随机对拍、以及在提交前用宏一键关掉调试输出。"),
    ("scene", "应用场景", "任何提交失败之后。对拍是提高正确率性价比最高的技巧，"
                          "尤其适合贪心、模拟、DP 这类\"思路对但细节错\"的题。"),
    ("code", r'''
// ---------- (1) 一键关闭调试输出 ----------
#ifdef LOCAL
  #define debug(x) cerr << #x << " = " << (x) << '\n'
#else
  #define debug(x)               // 提交时自动变空
#endif
// 编译时加 -DLOCAL 即可开启：g++ -std=c++17 -O2 -Wall -DLOCAL a.cpp

// ---------- (2) 输出数组（调试常用） ----------
template <class T> void printArr(T a, int l, int r) {
    for (int i = l; i <= r; ++i) cerr << a[i] << " \n"[i == r];
}

// ---------- (3) 对拍脚本思路（Windows 批处理 / 命令行） ----------
// 1) 写一份暴力程序 brute.cpp（慢但一定对）与你的程序 a.cpp
// 2) 写随机数据生成器 gen.cpp，输出小规模数据
// 3) 循环执行：
//      gen.exe > in.txt
//      a.exe     < in.txt > out1.txt
//      brute.exe < in.txt > out2.txt
//      fc out1.txt out2.txt        (Windows 用 fc，Linux 用 diff)
//    一旦不一致，in.txt 就是能让你复现 bug 的反例

// ---------- (4) 断言：本地检查不变量 ----------
assert(0 <= idx && idx < n);       // 越界立即中止并报行号，比静默错值好查得多
// 提交前记得确认没有依赖 assert 的逻辑；NDEBUG 下 assert 会被移除
'''),
    ("bullets", [
        ("调试输出一律用 ", ("cerr", {"name": "Consolas"}),
         "：它不带缓冲、不受重定向影响，且不会混进标准答案输出里。"),
        ("对拍的三个文件缺一不可：暴力程序、随机生成器、比较脚本。"
         "生数据时注意覆盖边界：n=1、全相同、含 0、含负数、最大值。"),
        ("", ("assert", {"name": "Consolas"}), " 在 OJ 上若被触发会报 RE，"
         "所以它既是调试利器，也可能成为\"本地能过、提交 RE\"的原因——上线前确认逻辑不依赖它。"),
        ("【拓展】洛谷、Codeforces 的\"查看测试点\"功能可以直接拿到 WA 的那个点，"
         "配合本地对拍效率更高。"),
    ]),
    ("warnbox", "常见报错与坑", [
        "调试用的 cout 忘记删掉 → 输出里混入额外内容，直接 WA。",
        "cerr 输出在循环里刷屏，把真正的错误信息淹没。",
        "对拍时生成的数据太\"温和\"（全是随机大数、没有边界），永远拍不出 bug。",
        "对拍程序里两边用了不同的读入方式，导致差异其实来自读入而非算法。",
        "assert 里写了有副作用的表达式（如 assert(++i < n)），开启优化后行为改变。",
    ]),
]
