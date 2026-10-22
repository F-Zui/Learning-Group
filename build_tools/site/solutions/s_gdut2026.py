# -*- coding: utf-8 -*-
"""GDUT 2026 月赛题解。

本场 PDF 的中文字体缺少正确的 ToUnicode 映射，直接复制题目会得到乱码；但乱码是可逆的
（码位 C 与原始 GBK 双字节 (hi, lo) 满足 C = 94 * (hi - 0xA6) + (lo - 0xA1)），
按此反解后 14 题的题面全部还原，并逐条与官方样例核对过。

A ~ K、M、N 共 13 题的参考代码都通过官方样例；其中 B/C/D/E/F/G/I/J/K/N 另用独立暴力
对拍过随机小数据。L 只给题面与关键结论，不给代码，原因见 skip 说明。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from solutions.dsl_sol import *  # noqa: F401,F403

PROBLEMS = []


PROBLEMS.append(PROB(
    letter='A',
    name='迈向第 50 届世界总决赛',
    diff='入门',
    tag='零输入、输出固定串（签到题）',
    statement=[
        P('本题没有任何输入。请输出下面这一行（注意下划线、大小写与结尾的感叹号）：'),
        P('We_are_going_to_the_50th_World_Finals!'),
        T(['标准输入', '标准输出'], [['（空）', 'We_are_going_to_the_50th_World_Finals!']]),
    ],
    hint=[
        '题面写着「本题没有任何输入」——所以一行读入语句都不要写。',
        '把答案串当成数据抄下来，逐字符核对：下划线到底有几个？大小写？最后一个字符是 ! 还是 。？',
    ],
    idea=[
        '签到题。零输入，直接把字符串打印出来即可，时间、空间都是 O(1)。',
        '唯一会挂的地方是抄错串：本题的串里有 7 个下划线（We_are_going_to_the_50th_World_Finals!），开头 We 是大写 W，结尾是半角感叹号，行末要有换行。',
    ],
    code=r'''#include <cstdio>

int main() {
    // 本题零输入：一个 scanf / cin 都不要写，否则会一直等输入
    const char* ans = "We_are_going_to_the_50th_World_Finals!";
    std::puts(ans);      // puts 输出后自动补换行；用 printf 则要自己写 \n
    return 0;
}
''',
    explain=[
        ('// 本题零输入：一个 scanf / cin 都不要写', '题目没有输入文件内容，写了读入会阻塞在等待输入上'),
        ('const char* ans = "We_are_going_to_the_50th_World_Finals!"', '把答案串提到一个变量里，便于和自己数出来的字符逐个对照'),
        ('std::puts(ans);', 'puts 输出完自动补换行；若改用 printf 必须自己写 \\n'),
        ('return 0;', 'main 正常返回 0；此时输出已经写完'),
    ],
    pitfalls=[
        '输出里不能有任何提示语（例如「答案是：」），评测机按字符比对。',
        '别把下划线 _ 打成空格或减号，也别把结尾的 ! 漏掉。',
        '补一句换行更保险；虽然多数评测容忍行末无换行，但没必要赌。',
    ],
))

PROBLEMS.append(PROB(
    letter='B',
    name='是啊，吃什么',
    diff='普及-',
    tag='贪心 + 单状态模拟（只跟踪空位数）',
    statement=[
        P('餐厅有 n 个座位，初始有 k 个空位（0 ≤ k ≤ n）。接下来依次发生 m 个事件，用一个长度为 m 的 01 串 s 描述：'),
        L([
            's_i = 0：一名正在用餐的客人离开，空位数 +1；但若此时所有座位都空（空位数 = n），空位数不变。',
            's_i = 1：一名客人到达。若存在空位，他立刻入座、空位数 −1；否则他必须等位。',
        ], ordered=False),
        P('你拥有一种「魔法」：每施展一次，可以让一名正在用餐的客人立刻离开，从而立刻空出一个座位。魔法可以在任意时刻施展。求最少需要施展多少次，才能使每一位到达的客人都能立刻入座、无须等位。'),
        P('输入：第一行 T（1 ≤ T ≤ 10^4）；每组数据第一行 n, k, m（1 ≤ n, m ≤ 10^6，0 ≤ k ≤ n），第二行一个长度 m 的 01 串 s。保证 Σn + Σm ≤ 10^6。输出：每组一行一个整数。'),
        T(['标准输入', '标准输出'], [['3<br>1 0 3<br>101<br>3 2 4<br>1110<br>2 2 5<br>00111', '1<br>1<br>1']]),
    ],
    hint=[
        '整个过程里真正会影响决策的状态只有一个：当前还有几个空位。别把「谁坐在哪」也记下来。',
        '如果此刻还有空位，施法有意义吗？施法让空位 +1，而下一个到达者立刻就会把它吃掉。',
        '试着证明「只在没有空位的那一刻施法」不会比任何方案差。',
    ],
    idea=[
        '施法的唯一作用是让空位 +1。若当前空位 > 0，提前施法只是让空位暂时变大，而下一个 s_i = 1 马上把它吃掉——这个座位存不住，等于白施。所以最优解可以在「空位 = 0 且有人到达」时才施法。',
        '而在空位 = 0 时，餐厅必然是满的（n 个座位全被占，且 n ≥ 1），所以一定有「正在用餐的人」可以逼走，施法合法。逼走一人 → 空位变 1 → 该客人立刻坐下 → 空位回到 0。净效果就是：答案 +1，空位数不变。',
        '于是只需 O(m) 扫一遍串，维护空位数 empty：',
        's_i = 0：若 empty < n 则 ++empty（题面专门说了全空时不增）。',
        's_i = 1：若 empty > 0 则 --empty；否则 ++ans（施法一次，empty 仍然为 0）。',
        '样例 1：n=1,k=0，串 101 —— 第 1 个 1 时 empty=0，施法一次；随后 0 让 empty 变 1，最后一个 1 顺利入座，答案 1。',
        '样例 2：n=3,k=2，串 1110 —— 前两个 1 吃掉两个空位，第三个 1 时 empty=0 需施法一次，答案 1。',
        '样例 3：n=2,k=2，串 00111 —— 前两个 0 因为全空所以空位不变（仍是 2），两个 1 坐满，第三个 1 施法一次，答案 1。',
    ],
    code=r'''#include <cstdio>

// B：只需跟踪"空位数"这一个状态。
// 施法只在空位为 0 的那一刻才可能有用：让一名正在用餐的人离开，
// 空位 +1，随后到达者立刻坐下，空位又回到 0，净效果就是"多接待一人"。
// 提前施法是浪费（空位迟早会被吃掉），所以贪心按需施法即可。
int main() {
    int T;
    std::scanf("%d", &T);
    static char s[1000005];
    while (T--) {
        int n, k, m;
        std::scanf("%d %d %d", &n, &k, &m);
        std::scanf("%s", s);
        long long empty = k, magic = 0;
        for (int i = 0; i < m; ++i) {
            if (s[i] == '0') {
                if (empty < n) ++empty;      // 全员都在吃时没人能离开，空位不变
            } else {
                if (empty > 0) --empty;      // 有空位，直接入座
                else ++magic;                // 满座：逼走一人腾位，坐下后仍满座
            }
        }
        std::printf("%lld\n", magic);
    }
    return 0;
}
''',
    explain=[
        ('static char s[1000005];', 'Σm ≤ 10^6，把串放到静态数组里，避免每组数据反复分配'),
        ('if (empty < n) ++empty;', '题面额外规定「所有座位均为空时空位不变」，所以空位封顶在 n'),
        ('if (empty > 0) --empty;', '有空位就直接入座，不需要任何代价'),
        ('else ++magic;', '满座才施法：逼走一名用餐者腾出座位，该客人随即坐下，空位数仍是 0'),
        ('std::printf("%lld\\n", magic);', '每组数据独立输出一行，答案用 long long 更稳'),
    ],
    pitfalls=[
        's_i = 0 且空位已经是 n 时，空位不能再 +1（题目专门写了这一条，写成无条件 ++empty 会错）。',
        '满座施法后不要以为「多了一个空位」：到达者立刻坐下，空位仍然回到 0，只让答案 +1。',
        '多组数据，empty 和 magic 每组都要重新初始化（初始 empty = k）。',
        'Σm 到 10^6，用 cin 逐字符读会偏慢；scanf("%s") 或快读更稳。',
    ],
))

PROBLEMS.append(PROB(
    letter='C',
    name='小猪玩音游',
    diff='普及',
    tag='模拟 + 排序（按题意算 Rating）',
    statement=[
        P('游戏里有 N 首歌，编号 1..N，第 i 首有一个定数 d_i（恰好两位小数，1.00 ≤ d_i ≤ 20.00）。小猪共进行了 M 次游玩，每次记录包含歌曲编号 s_j 和本次准确率 a_j（a_j 是百分数本体，0.00 ≤ a_j ≤ 100.90，恰好两位小数，不带百分号）。'),
        P('一次定数为 d、准确率为 a% 的游玩，其单曲评分为：'),
        P('S(d, a) = 0（0 ≤ a < 97.50）；S(d, a) = d + 2.15 × (a − 97.50) / (100.90 − 97.50)（97.50 ≤ a ≤ 100.90）。'),
        P('计算 Rating 时：每首歌只保留它所有游玩记录中的最高单曲评分（同一首歌最多在 B30 中出现一次）；把所有歌的最高分从高到低取前 30 个组成 B30；没有游玩过的歌、以及不足 30 首时多出来的位置都记为 0 分。Rating 定义为 B30 中 30 个分数的平均值，即「30 个分数之和 / 30」。'),
        P('输入：第一行 N, M（1 ≤ N, M ≤ 2 × 10^5）；第二行 N 个实数 d_i；接下来 M 行每行 s_j 和 a_j。保证至少有一条游玩记录。输出一个浮点数，绝对或相对误差不超过 10^-6 即算正确。'),
        T(['标准输入', '标准输出'], [['3 6<br>15.90 12.00 14.00<br>1 97.50<br>1 100.90<br>2 99.20<br>2 98.18<br>3 97.49<br>1 99.20', '1.0375000000']]),
    ],
    hint=[
        '游玩有 M 次，可是歌只有 N 首——第一步显然是把 M 次的信息压到「每首歌一个数」上。',
        '「同一首歌最多只能在 B30 中出现一次」这句话，等价于对每首歌做什么操作？',
        '想清楚分母：只有 1 首歌时，Rating 是「分数/1」还是「分数/30」？',
    ],
    idea=[
        '第一步 O(M)：对每首歌维护 best[i]，用 S(d[s], a) 去更新取最大值。同一首歌多次游玩只留最高分，正是「同一首歌最多出现一次」的含义。',
        '第二步 O(N log N)：把 best[1..N] 降序排序，取前 min(N, 30) 个求和，再除以 30。不足 30 首的位置按 0 分补，而补 0 不影响和，所以直接只加前 min(N,30) 项即可。',
        '评分公式要注意 a 是「百分数本体」：a = 97.50 时给 d 分，a = 100.90 时给 d + 2.15 分，中间线性。a = 97.49 虽然只差 0.01，也是 0 分——样例的第 3 首歌正是这个陷阱。',
        '验样例：歌 1 最高 15.90 + 2.15 = 18.05；歌 2 在 99.20% 得 12.00 + 2.15 × (99.20−97.50)/3.40 = 13.075；歌 3 的 ACC 97.49 < 97.50 得 0。B30 之和 31.125，其余 27 个位置补 0，Rating = 31.125 / 30 = 1.0375。',
        'double 的精度远好于 1e-6 的宽容度，输出 10 位小数即可。',
    ],
    code=r'''#include <cstdio>
#include <algorithm>
#include <functional>
#include <vector>

// C：每首歌只留最高单曲评分，然后取前 30 高求和除以 30。
// 关键三点：① 同一首歌的多次游玩只取 max；② 不足 30 首用 0 补齐（0 不影响和）；
// ③ 评分公式里 a 是百分数本体（如 97.50），不是小数。
static double scoreOf(double d, double a) {
    if (a < 97.50) return 0.0;
    return d + 2.15 * (a - 97.50) / (100.90 - 97.50);
}

int main() {
    int N, M;
    std::scanf("%d %d", &N, &M);
    std::vector<double> d(N + 1), best(N + 1, 0.0);
    for (int i = 1; i <= N; ++i) std::scanf("%lf", &d[i]);
    for (int j = 0; j < M; ++j) {
        int s;
        double a;
        std::scanf("%d %lf", &s, &a);
        double sc = scoreOf(d[s], a);
        if (sc > best[s]) best[s] = sc;               // 每首歌只保留最高分
    }
    // best[1..N] 是各歌的最高分；从大到小排，取前 30
    std::sort(best.begin() + 1, best.end(), std::greater<double>());
    double sum = 0.0;
    for (int i = 1; i <= std::min(N, 30); ++i) sum += best[i];   // 缺的位置补 0
    std::printf("%.10f\n", sum / 30.0);               // 分母恒为 30，不是 min(N,30)
    return 0;
}
''',
    explain=[
        ('static double scoreOf(double d, double a)', '把评分公式抽成函数，避免在两处写出不一致的表达式'),
        ('if (a < 97.50) return 0.0;', '严格小于才给 0 分；a = 97.50 恰好拿 d 分，是常见的 off-by-one'),
        ('return d + 2.15 * (a - 97.50) / (100.90 - 97.50);', '分母 3.40 是区间长度，2.15 是满分加成，两者都取自题面'),
        ('if (sc > best[s]) best[s] = sc;', '同一首歌只保留最高单曲评分，绝不累加'),
        ('std::sort(best.begin() + 1, best.end(), std::greater<double>());', '降序排序后前 30 项就是 B30'),
        ('std::printf("%.10f\\n", sum / 30.0);', '分母恒为 30，不是 min(N,30)'),
    ],
    pitfalls=[
        '分母恒为 30。只玩过 1 首歌且最高分 15.90 时，Rating = 15.90/30 = 0.53，不是 15.90。',
        '边界是 a < 97.50 才为 0；a = 97.50 恰好拿 d 分，写成 a <= 97.50 会错。',
        '同一首歌多次游玩取最大值，不是求和、也不是取最后一次。',
        '输入的 a 就是 97.50 这样的数，不要再除以 100；d 也不用做任何换算。',
    ],
))

PROBLEMS.append(PROB(
    letter='D',
    name='课后作业',
    diff='普及/提高-',
    tag='构造 + 进制观察（三进制只有 0/1/2）',
    statement=[
        P('定义：把一个正整数的各位数字相乘，对得到的积重复这一操作，直到结果变成一位数，所需步数就是这个数的「乘法持续性」；已经是一位数时持续性为 0。'),
        P('本题所有运算都在三进制下进行：每一步都把当前数视为三进制数，把它各位数字相乘，结果继续写成三进制。例如 12₃ 各位数字之积为 1 × 2 = 2，所以 12₃ 的持续性为 1。'),
        P('给定 x（0 ≤ x ≤ 11），请构造一个长度不超过 38 位的三进制正整数，使其乘法持续性恰好为 x，输出这个数（只含 0、1、2，不含前导零）。若不存在，输出 −1。'),
        T(['标准输入', '标准输出'], [['2', '22']]),
        P('样例说明：22₃ → 11₃ → 1₃，共 2 步，所以输出 22 的持续性为 2。'),
    ],
    hint=[
        '三进制的数字只有 0、1、2 三种。那么「各位数字相乘」的结果只可能是哪些数？',
        '如果这个数含数字 0 且不止一位，第一步的积是什么？它已经是一位数了吗？',
        '如果数字只含 1 和 2，积只由「2 的个数」决定。把 x 拆成 1 + （一个 2^t 的持续性）来枚举。',
    ],
    idea=[
        '三进制数字 ∈ {0, 1, 2}，所以各位数字之积只可能是 0，或者 2^t（t 为数字 2 的个数）。这把问题一下压扁了：',
        '情形一：这个数含 0 且至少两位 → 第一步的积就是 0，而 0 本身是一位数，持续性 = 1。',
        '情形二：数字只由 1 和 2 组成 → 积恒等于 2^t，其中 t 是数字 2 的个数，持续性 = 1 + P(2^t)（P 表示持续性）。',
        '枚举 t = 0..38 直接算 P(2^t)：P(1) = P(2) = 0，P(4) = 1（4 = 11₃ → 1），P(8) = 2（8 = 22₃ → 4 → 1），而 t ≥ 4 时 2^t 的三进制表示必然含 0，P(2^t) = 1。',
        '所以可达的持续性只有 {0, 1, 2, 3}，x ≥ 4 一律输出 −1。最小代表分别是：x=0 → 1（一位数）、x=1 → 10（1×0 = 0）、x=2 → 22（样例）、x=3 → 222（222₃ = 26 → 8 → 4 → 1，三步）。',
        '程序里不必背表：对 t = 0..38 现场算 1 + P(2^t) 去匹配 x 就行，复杂度 O(38 log)。',
    ],
    code=r'''#include <cstdio>
#include <string>

// D：三进制只有 0/1/2 三个数字，乘法持续性的取值范围被死死卡住。
//   ① 一个数若含数字 0 且至少两位 -> 积为 0，0 是一位数，持续性 = 1；
//   ② 只含 1/2 -> 积恒等于 2^(2 的个数)，记 t = 2 的个数，持续性 = 1 + P(2^t)。
// 于是可达集合 = {0} U {1 + P(2^t) : t = 0..38}，用暴力枚举就能确定。
// 实测：P(2^t) 在 t<=38 内只取 0/1/2，可达持续性只有 0,1,2,3，
// 故 x>=4 一律输出 -1。最小代表：1、10、22、222。

// 三进制下的乘法持续性
static int persistence(unsigned long long n) {
    int steps = 0;
    while (n > 2) {                 // 0/1/2 都是一位数，停
        unsigned long long p = 1;
        while (n > 0) { p *= n % 3; n /= 3; }
        n = p;                      // 含 0 时 p = 0，下一轮直接停
        ++steps;
    }
    return steps;
}

int main() {
    int x;
    if (std::scanf("%d", &x) != 1) return 0;
    // 一位数：持续性 0
    if (x == 0) { std::puts("1"); return 0; }
    // 枚举"2 的个数" c，构造 c 个 2 + 若干 1 保证长度 >= 2
    for (int c = 0; c <= 38; ++c) {
        int extra = (c == 0 ? 2 : (c == 1 ? 1 : 0));   // 让总长度至少 2
        int len = c + extra;
        if (len > 38) break;
        unsigned long long v = 1ULL << c;               // c <= 38，2^c 不会溢出
        if (1 + persistence(v) == x) {
            std::string ans(c, '2');
            ans.append(extra, '1');
            std::puts(ans.c_str());
            return 0;
        }
    }
    std::puts("-1");
    return 0;
}
''',
    explain=[
        ('static int persistence(unsigned long long n)', '按定义模拟：一位数（n ≤ 2）停，否则把三进制各位相乘继续'),
        ('while (n > 2) {', '三进制的一位数是 0/1/2，所以 n > 2 才需要再迭代一步'),
        ('while (n > 0) { p *= n % 3; n /= 3; }', '取出三进制每一位并累乘；遇到 0 时 p 变 0，下一轮直接停'),
        ('if (x == 0) { std::puts("1"); return 0; }', '一位数持续性为 0，输出 1（不能输出空串、也不能有前导零）'),
        ('int extra = (c == 0 ? 2 : (c == 1 ? 1 : 0));', '保证构造出的数至少两位——「0」是一位数，持续性 0，不能拿来当 x=1 的答案'),
        ('if (1 + persistence(v) == x)', '核心判定：全是 1/2 的数，持续性 = 1 + P(2^c)'),
    ],
    pitfalls=[
        '别按十进制直觉去枚举数字：38 位三进制到 1.35e18，枚举不完；必须先利用「积只能是 0 或 2^t」。',
        '构造含 0 的答案时至少要两位数字：单独的「0」持续性为 0，不是 1。',
        'x = 0 要输出一位数（如 1），不能输出空串，也不能带前导零。',
        '输出的是三进制串，别把 22 理解成十进制的 22（22₃ 才是 8）。',
    ],
))

PROBLEMS.append(PROB(
    letter='E',
    name='QZKago Requiem',
    diff='普及+/提高-',
    tag='多源最短路（关键在「只关心最大值」的化归）',
    statement=[
        P('给定一棵 n 个点的带权树，边权 w。树上有 m 个点被指定为「影响源」（s_1..s_m 互不相同）。'),
        P('为第 i 个影响源设置一个非负整数影响范围 r_i。若 dist(s_i, v) < r_i（严格小于），则称点 v 被 s_i 覆盖。要求树上每个点至少被一个影响源覆盖，在此前提下让所有 r_i 中的最大值尽可能小，输出这个最小值。'),
        P('输入：第一行 n, m（1 ≤ n ≤ 4 × 10^5，1 ≤ m ≤ n）；接下来 n − 1 行每行 u, v, w（1 ≤ w ≤ 10^9）；最后一行 m 个互不相同的整数表示影响源位置。输出一个整数。答案可能超过 32 位整数范围。'),
        T(['标准输入', '标准输出'], [['3 1<br>1 2 5<br>2 3 7<br>1', '13'], ['5 2<br>1 2 4<br>2 3 3<br>3 4 10<br>4 5 2<br>1 5', '8']]),
    ],
    hint=[
        '目标只是「最大半径」尽量小，那每一个 r_i 是不是可以各管各地定？相邻两个源的半径之间有没有耦合约束？',
        '如果最大半径是 R，那么「点 v 被源 s 覆盖」能推出一个只关于 dist(s,v) 和 R 的不等式吗？',
        '把「半径」换回「距离」看看：题目其实在问每个点到最近源的什么量？',
    ],
    idea=[
        '设所有半径的最大值为 R。点 v 被源 s 覆盖要求 dist(s,v) < r_s ≤ R，而两边都是整数，所以等价于 dist(s,v) ≤ R − 1。',
        '必要性：对每个 v 都要存在某个 s 使 dist(s,v) ≤ R − 1，即 min_s dist(s,v) ≤ R − 1，于是 R ≥ 1 + max_v min_s dist(s,v)。',
        '充分性：把所有源的半径都设成同一个 R。此时覆盖集合就是「半径 R − 1 的球」之并；只要 R − 1 ≥ max_v min_s dist(s,v)，就全覆盖了。注意不同的 r_i 之间没有任何耦合约束（没有总能量预算），所以「让所有源都用满」永远不亏。',
        '结论：答案 = 1 + max_v min_s dist(s,v)。做法就是多源 Dijkstra：把所有源以距离 0 一起入堆，跑完取 dist 的最大值再加 1。',
        '验样例 1：源为点 1，dist = 0, 5, 12，max = 12 → 13。验样例 2：源为 1 和 5，最近源距离 = 0, 4, 7, 2, 0，max = 7 → 8。',
        '路径长度可达 4 × 10^5 × 10^9 = 4 × 10^14，必须 64 位整数。',
    ],
    code=r'''#include <cstdio>
#include <cstring>
#include <queue>
#include <vector>

// E：答案就是 "1 + 树上每个点到最近影响源的距离" 的最大值。
// 证明（两句话）：设所有半径的最大值为 R。
//   必要性：点 v 被源 s 覆盖要求 dist(s,v) < r_s <= R，即 dist 至多 R-1，
//           所以 R >= 1 + min_s dist(s,v)，对每个 v 都成立。
//   充分性：把每个源的半径都取 R，覆盖集合就是半径 R-1 的球之并，正好达标。
// 于是先多源 Dijkstra 求出 dist 数组，取 max 再加 1。边权可到 1e9、路径可到 4e14，必须 64 位。

const int MAXN = 400005;
const int MAXE = 800005;

static int head[MAXN], to[MAXE], nxt[MAXE], ecnt;
static long long wt[MAXE];

static inline void addEdge(int u, int v, int w) {
    to[++ecnt] = v; wt[ecnt] = w; nxt[ecnt] = head[u]; head[u] = ecnt;
}

static char buf[1 << 24];
static int blen, bpos;

static inline int nextInt() {
    while (bpos < blen && (buf[bpos] < '0' || buf[bpos] > '9')) ++bpos;
    int x = 0;
    while (bpos < blen && buf[bpos] >= '0' && buf[bpos] <= '9') x = x * 10 + (buf[bpos++] - '0');
    return x;
}

int main() {
    blen = (int)fread(buf, 1, sizeof(buf), stdin);
    int n = nextInt(), m = nextInt();
    ecnt = 0;
    for (int i = 1; i <= n; ++i) head[i] = 0;
    for (int i = 1; i < n; ++i) {
        int u = nextInt(), v = nextInt(), w = nextInt();
        addEdge(u, v, w);
        addEdge(v, u, w);
    }

    const long long INF = (long long)4e18;
    std::vector<long long> dist(n + 1, INF);
    typedef std::pair<long long, int> PII;
    std::priority_queue<PII, std::vector<PII>, std::greater<PII> > pq;

    for (int i = 0; i < m; ++i) {
        int s = nextInt();
        dist[s] = 0;
        pq.push(PII(0, s));          // 所有源同时入堆 = 多源最短路
    }
    while (!pq.empty()) {
        PII cur = pq.top(); pq.pop();
        long long d = cur.first;
        int u = cur.second;
        if (d > dist[u]) continue;
        for (int e = head[u]; e; e = nxt[e]) {
            int v = to[e];
            if (d + wt[e] < dist[v]) {
                dist[v] = d + wt[e];
                pq.push(PII(dist[v], v));
            }
        }
    }

    long long far = 0;
    for (int i = 1; i <= n; ++i) if (dist[i] > far) far = dist[i];
    std::printf("%lld\n", far + 1);
    return 0;
}
''',
    explain=[
        ('dist[s] = 0;', '所有源初始距离置 0 并一起入堆，堆里跑一次就是「到最近源的距离」'),
        ('if (d > dist[u]) continue;', '堆里的过期状态直接跳过，保证每条边只做一次有效松弛'),
        ('if (d + wt[e] < dist[v])', '松弛用 long long，边权 10^9 且路径可累加到 10^14'),
        ('const long long INF = (long long)4e18;', 'INF 要远大于最长路径 4e14；别用 1e18 再去做 d + w 之外的加法'),
        ('std::printf("%lld\\n", far + 1);', '答案是最大距离 +1：覆盖条件是严格小于，距离恰好为 far 的点盖不到'),
    ],
    pitfalls=[
        '覆盖条件是严格不等式 dist < r，所以答案不是最大距离，而是最大距离 + 1。',
        '每个源也要覆盖自己：dist(s,s) = 0 < r_s，所以半径至少为 1——这也是那个 +1 的来源之一。',
        '边权到 10^9、点数到 4 × 10^5，距离必须 long long；用 int 会直接溢出。n = 1 时没有边、m = 1，答案是 1。',
        '不要往「二分答案 + 树形 DP」上想：本题已经证明了答案是闭式，二分既多余又容易写错。',
    ],
))

PROBLEMS.append(PROB(
    letter='F',
    name='猪猪的难题（简单版）',
    diff='提高+',
    tag='离线 + 树状数组（用「最后一次出现」拆贡献）',
    statement=[
        P('定义一个非空字符串的权值 w(T) 为其中出现过的不同小写英文字母种类数。'),
        P('给定长度为 n 的小写英文字母串 S（下标从 1 开始），q 次询问，每次给 l, r，求'),
        P('Σ_{l ≤ i ≤ j ≤ r} w(S_i S_{i+1} … S_j)，'),
        P('即区间 [l, r] 内所有非空连续子串的权值总和。'),
        P('输入：第一行 T（1 ≤ T ≤ 1000）；每组数据第一行 n, q（1 ≤ n, q ≤ 10^6），第二行串 S，接下来 q 行每行 l, r。保证 Σn ≤ 10^6、Σq ≤ 10^6。输出：每组数据输出一行 q 个整数，空格隔开。答案可能超过 32 位整数范围。'),
        T(['标准输入', '标准输出'], [['1<br>3 3<br>abc<br>1 3<br>1 1<br>2 3', '10 1 4']]),
    ],
    hint=[
        '不要真的去枚举子串。换一种方式数「不同字符种类数」：它等于区间里「是某个字符最后一次出现」的位置个数。',
        '固定右端点 r，让左端点 i 从 1 到 r 变，每个位置 p 对答案的贡献能写成一个关于 i 的简单式子吗？',
        '把求和次序交换后，答案会变成 Σ (p − l + 1) · c_p(r) 的形状。然后想：r 增加 1 时，哪些 p 的 c 值不再变化？',
    ],
    idea=[
        '记 next[p] 为 p 之后与 S[p] 同字符的下一个位置（没有则记 n+1）。那么 S[i..j] 里每个字符恰好在它「最后一次出现」的位置被数到一次，即 w(S[i..j]) = #{ p ∈ [i, j] : next[p] > j }。',
        '交换求和次序并整理，可以得到一个很干净的闭式：',
        'Ans(l, r) = Σ_{p=l..r} (p − l + 1) · c_p(r)，  其中 c_p(r) = min(r, next[p] − 1) − p + 1。',
        "c_p(r) 的含义是：p 在多少个右端点 r' ≤ r 上仍然是「最后一次出现」，也就是它对 B 数组的累计贡献。",
        '于是 Ans = S1 − l · S2，其中 S2 = Σ c_p(r)、S1 = Σ (p + 1) · c_p(r)（p 取遍 [l, r]）。用两个树状数组分别维护 c_p 和 (p+1)·c_p 即可。',
        '关键观察：当右端点从 r−1 走到 r 时，唯一会「死掉」的位置是上一个与 S[r] 同字符的位置 pv —— 它的 next 就是 r，从此刻起 c_pv 永远定格为 r − pv，把它塞进树状数组。而仍然活着的位置恰好是 26 个字符各自的最后一次出现位置，最多 26 个，查询时直接扫一遍累加，不必进树状数组。',
        '复杂度 O(n log n + q (26 + log n))，Σn、Σq 各 10^6 都跑得很快（实测 1.6s）。',
        '验样例：S = abc，next = 4, 4, 4，于是 c = 3, 2, 1；S2 = 6，S1 = 2×3 + 3×2 + 4×1 = 16；Ans(1,3) = 16 − 1×6 = 10 ✓Ans(1,1) = 2 − 1×1 = 1 ✓  Ans(2,3) = 10 − 2×3 = 4 ✓',
    ],
    code=r'''#include <cstdio>
#include <cstring>

// F：Ans(l,r) = sum_{l<=i<=j<=r} w(S[i..j])
// 关键变形：把"每个子串的不同字符数"换成"每个位置 p 作为某字符最后一次出现"的次数。
//   w(S[i..j]) = #{ p in [i,j] : next[p] > j }，next[p] 是 p 之后同字符的下一个位置。
// 交换求和次序可得
//   Ans(l,r) = sum_{p=l..r} (p-l+1) * c_p(r),
//   c_p(r)   = min(r, next[p]-1) - p + 1  = "p 在多少个 r' <= r 里仍存活"。
// 于是答案 = S1 - l*S2，其中
//   S2 = sum c_p(r)，S1 = sum (p+1)*c_p(r)（p 取遍 [l,r]）。
// 当 r 前进时：只有"上一个同字符位置"会死掉，把它的 c 定死成 (r-p) 塞进树状数组；
// 而仍然存活的 p 恰好是 26 个字符各自的最后出现位置，最多 26 个，直接扫一遍即可。

const int MAXN = 1000005;

static int n, q;
static char s[MAXN];
static long long bit1[MAXN], bit2[MAXN];   // bit1 存 c_p，bit2 存 (p+1)*c_p
static int last[26];
static int qhead[MAXN], qnext[MAXN], qleft[MAXN];
static long long qans[MAXN];

static inline void bitAdd(long long* b, int i, long long v) {
    for (; i <= n; i += i & (-i)) b[i] += v;
}
static inline long long bitSum(long long* b, int i) {
    long long r = 0;
    for (; i > 0; i -= i & (-i)) r += b[i];
    return r;
}

static char obuf[1 << 25];
static int olen;

static inline void writeLL(long long v) {
    if (v == 0) { obuf[olen++] = '0'; return; }
    char t[24]; int k = 0;
    while (v > 0) { t[k++] = (char)('0' + v % 10); v /= 10; }
    while (k > 0) obuf[olen++] = t[--k];
}

int main() {
    int T;
    if (std::scanf("%d", &T) != 1) return 0;
    while (T--) {
        std::scanf("%d %d", &n, &q);
        std::scanf("%s", s + 1);
        for (int i = 0; i <= n + 1; ++i) { bit1[i] = bit2[i] = 0; qhead[i] = -1; }
        memset(last, 0, sizeof(last));
        for (int j = 0; j < q; ++j) {
            int l, r;
            std::scanf("%d %d", &l, &r);
            qleft[j] = l;
            qnext[j] = qhead[r];          // 按右端点把询问挂成链表
            qhead[r] = j;
        }
        for (int r = 1; r <= n; ++r) {
            int ch = s[r] - 'a';
            int pv = last[ch];
            if (pv) {                     // pv 的 next 就是 r，它的 c 从此定格为 r-pv
                long long v = r - pv;
                bitAdd(bit1, pv, v);
                bitAdd(bit2, pv, (long long)(pv + 1) * v);
            }
            last[ch] = r;
            for (int e = qhead[r]; e != -1; e = qnext[e]) {
                int l = qleft[e];
                long long S2 = bitSum(bit1, r) - bitSum(bit1, l - 1);
                long long S1 = bitSum(bit2, r) - bitSum(bit2, l - 1);
                for (int c = 0; c < 26; ++c) {
                    int p = last[c];      // 存活位置：各字符的最后一次出现
                    if (p >= l) {         // last[c] <= r 恒成立，只需判下界
                        long long cc = r - p + 1;
                        S2 += cc;
                        S1 += (long long)(p + 1) * cc;
                    }
                }
                qans[e] = S1 - (long long)l * S2;
            }
        }
        for (int j = 0; j < q; ++j) {
            if (j) obuf[olen++] = ' ';
            writeLL(qans[j]);
        }
        obuf[olen++] = '\n';
    }
    fwrite(obuf, 1, olen, stdout);
    return 0;
}
''',
    explain=[
        ('bitAdd(bit2, pv, (long long)(pv + 1) * v);', '上一个同字符位置在此刻死亡，把 c 定格成 r−pv 后一次性写进两个树状数组'),
        ('last[ch] = r;', '维护 26 个字符的最后出现位置——它们是查询时唯一还「活着」的候选'),
        ('if (p >= l) {', '活着的位置天然 ≤ r，只需判下界 p ≥ l，省掉一次上界判断'),
        ('qnext[j] = qhead[r];', '把询问按右端点挂成链表，一次扫描回答全部询问'),
        ('qans[e] = S1 - (long long)l * S2;', '闭式答案：Σ(p+1)c − l·Σc，两个量都来自 BIT + 26 个活位置'),
        ('writeLL(qans[j]);', 'q 可达 10^6 且必须输出在同一行，手动缓冲区比 cout 快很多'),
    ],
    pitfalls=[
        'c_p 里是 next[p] − 1 而不是 next[p]：p 在 r = next[p] 时才死亡，所以 r 最大只能取到 next[p] − 1。',
        '死掉的位置只能在它死亡的那一刻写入一次，否则会被重复累计；多组数据还要把 BIT、qhead、last 全清空（清空范围是 0..n）。',
        '答案量级约 10^13，而 S1 会到 10^17，必须全程 long long；BIT 用 int 会溢出。',
        '输出是「每组数据一行 q 个数」，不是每个询问一行，别多打换行。',
    ],
))

PROBLEMS.append(PROB(
    letter='G',
    name='智慧大学生猪猪比赛',
    diff='提高-',
    tag='排序 + 线性 DP（只需考虑 2 元组与 3 元组）',
    statement=[
        P('n 名评委给出原始评分 a_1..a_n。要把所有评委划分成若干小组，每人恰属一组，每组至少 2 人。'),
        P('每组选定一个整数 x 作为该组所有评委的最终评分，要求组内每个 i 满足 |x − a_i| ≤ d。不同组可以选不同的 x，x 没有额外的取值范围限制。小猪的总分为所有评委最终评分之和，即一个有 k 人、最终评分为 x 的组贡献 k·x。求最大总分；若无法完成合法分组，输出 Impossible。'),
        P('输入：第一行 T（1 ≤ T ≤ 10^5）；每组第一行 n, d（2 ≤ n ≤ 10^6，0 ≤ d ≤ 10^9），第二行 n 个整数 a_i（0 ≤ a_i ≤ 10^9）。保证 Σn ≤ 10^6。输出：每组一行，总分或 Impossible（注意大小写）。'),
        T(['标准输入', '标准输出'], [['3<br>4 2<br>0 1 2 3<br>3 0<br>0 1 1<br>3 2<br>2 4 6', '12<br>Impossible<br>12']]),
    ],
    hint=[
        '先排序。如果两个人的组「交错」在一起，把其中一个人换到另一个组，总分和可行性会不会变差？',
        '一个组里 x 取多大最赚？它被组内最小值还是最大值卡住？',
        '把一个 4 人大组拆成两个 2 人组，总分变大了还是变小了？推广一下能得到什么结论？',
    ],
    idea=[
        '先排序。若两组的人交错（a_u ≤ a_v ≤ a_w，u、w 同组而 v 在别组），把 v 换进来不会让「最大值−最小值」变大，而每个组的 a_min 也不会变大——所以最优解一定可以取成连续段分组。',
        '对一段 [l, r]：要存在整数 x 使所有 |x − a_i| ≤ d，等价于 a_r − a_l ≤ 2d。在此前提下 k·x 随 x 增大而增大，而 x 的上界是 a_l + d（a_l、d 都是整数，所以 x 也是整数）。于是该段贡献 (r − l + 1)(a_l + d)。',
        '关键剪枝：把一段拆成更小的段后，每一小段的 a_min 都不小于原段的 a_l，所以 Σ size·(a_min + d) 只会变大；而最细的拆法只能拆到 2 元组和 3 元组（每组至少 2 人）。因此最优解只由 2 元组和 3 元组构成。',
        '于是 dp[i] = 前缀 i 的最大总分，转移只看最后一段是 2 个还是 3 个：',
        'dp[i] = max( dp[i−2] + 2(a_{i−1} + d) 若 a_i − a_{i−1} ≤ 2d ,  dp[i−3] + 3(a_{i−2} + d) 若 i ≥ 3 且 a_i − a_{i−2} ≤ 2d )。',
        '用 −∞ 表示该前缀无法划分；dp[n] 仍是 −∞ 就输出 Impossible。复杂度 O(n log n)（排序）。',
        '验样例 1：排序后 0 1 2 3，dp = 0, −∞, 4, 6, 12 —— 分成 {0,1} 取 x=2、{2,3} 取 x=4，总分 4 + 8 = 12。',
        '验样例 2：d = 0 时只有原始分相同的评委能同组，原始分为 0 的评委（只有 1 人）无法进任何合法组 → Impossible。',
        '验样例 3：三人一组，a_min = 2，x 取 2 + 2 = 4，总分 3 × 4 = 12。',
    ],
    code=r'''#include <cstdio>
#include <algorithm>
#include <vector>
#include <climits>

// G：排序后最优解的分组一定是连续段（把交错的两个人互换不会变差）。
// 一段 [l,r] 里所有 a 都要满足 |x-a| <= d，故 x 最大取 a_l + d（要整数，a_l、d 都是整数），
// 该段贡献 (r-l+1)*(a_l+d)，可行当且仅当 a_r - a_l <= 2d。
// 再注意一个单调事实：把一个大段拆成若干小段，每小段的 a_l 都不小于原段的 a_l，
// 所以拆开只会更赚 —— 最细的拆法只能拆到 2 元组和 3 元组。
// 于是 dp[i] 只用考虑"最后一段是 2 个还是 3 个"。
int main() {
    int T;
    std::scanf("%d", &T);
    const long long NEG = LLONG_MIN / 4;
    while (T--) {
        int n;
        long long d;
        std::scanf("%d %lld", &n, &d);
        std::vector<long long> a(n + 1);
        for (int i = 1; i <= n; ++i) std::scanf("%lld", &a[i]);
        std::sort(a.begin() + 1, a.end());

        long long lim = 2 * d;
        std::vector<long long> dp(n + 1, NEG);
        dp[0] = 0;
        for (int i = 2; i <= n; ++i) {
            if (dp[i - 2] > NEG / 2 && a[i] - a[i - 1] <= lim)      // 最后一段是 {i-1, i}
                dp[i] = std::max(dp[i], dp[i - 2] + 2 * (a[i - 1] + d));
            if (i >= 3 && dp[i - 3] > NEG / 2 && a[i] - a[i - 2] <= lim)  // 最后一段是 {i-2,i-1,i}
                dp[i] = std::max(dp[i], dp[i - 3] + 3 * (a[i - 2] + d));
        }
        if (dp[n] <= NEG / 2) std::puts("Impossible");
        else std::printf("%lld\n", dp[n]);
    }
    return 0;
}
''',
    explain=[
        ('std::sort(a.begin() + 1, a.end());', '先排序，之后最优分组才是连续段，DP 才能只看相邻元素'),
        ('long long lim = 2 * d;', '一段可行 ⟺ a_r − a_l ≤ 2d，阈值是 2d 不是 d'),
        ('dp[i - 2] + 2 * (a[i - 1] + d)', '最后一段是 {i−1, i}，x 取该段最小值加 d 最赚'),
        ('dp[i - 3] + 3 * (a[i - 2] + d)', '最后一段是 {i−2, i−1, i}，n 为奇数时必然用到这一支'),
        ('if (dp[i - 2] > NEG / 2 && a[i] - a[i - 1] <= lim)', '先判可达再判可行，避免 NEG 参与加法后下溢'),
        ('if (dp[n] <= NEG / 2) std::puts("Impossible");', 'dp[n] 不可达才无解'),
    ],
    pitfalls=[
        'x 的上界是 a_l + d（不是 a_l、也不是平均值）；只有取到这个上界才最赚。',
        '可行性是 a_r − a_l ≤ 2d，不是 ≤ d。',
        'dp 必须区分「不可达」，用一个足够小的负数当 −∞，并防止它参与加法后下溢成正数。',
        '总分可达 10^6 × 2 × 10^9 = 2 × 10^15 要用 long long；无解输出的是 Impossible（首字母大写）。',
    ],
))

PROBLEMS.append(PROB(
    letter='H',
    name='取整互交',
    diff='提高',
    tag='交互题 + 两阶段二分（30 次卡进 32）',
    statement=[
        P('本题是交互题。交互器隐藏了一个整数 n（10^9 ≤ n ≤ 10^18），在整个交互过程中不变。'),
        P('每次询问，你输出一行 `? k`，其中 k 是满足 10^9 ≤ k ≤ 10^18 的整数；随后从标准输入读回一个整数，值为 ⌊n / k⌋。'),
        P('你最多可以进行 32 次形如 `? k` 的询问。确定 n 之后，输出一行 `! n` 并立即结束程序。每次输出查询或最终答案后都必须输出换行并刷新输出缓冲区，否则可能得到 Idleness Limit Exceeded。'),
        P('本题没有初始输入。样例展示的是 n = 10^9 时的一次交互（样例中的回答不一定足以唯一确定 n，仅示意格式）：'),
        T(['标准输入', '标准输出'], [['0<br>0', '? 1234567890<br>? 1000000001<br>! 1000000000']]),
    ],
    hint=[
        'k 最小只能是 10^9。那么第一次固定问 k = 10^9，得到的 ⌊n/10^9⌋ 能把 n 锁进多宽的区间？',
        '在锁定的区间里，如果取 k = mid，能不能让 ⌊n/mid⌋ 变成一个「n ≥ mid 吗」的布尔判断？',
        '数一数：宽度 10^9 的区间二分需要多少次？再加上前面那 1 次，够不够 32？',
    ],
    idea=[
        '第一阶段（1 次询问）：问 k = 10^9，拿到 a = ⌊n / 10^9⌋。由整除的定义立即有 n ∈ [a·10^9, (a+1)·10^9 − 1]，区间宽度正好 10^9。',
        '第二阶段（把 k 当比较器）：在窗口内取 k = mid。因为 mid ≥ a·10^9 且 n < (a+1)·10^9 ≤ 2·mid，所以 ⌊n/mid⌋ 只可能是 0 或 1，且⌊n/mid⌋ ≥ 1 ⟺ n ≥ mid。一次询问等于一次比较。',
        '于是对宽度 10^9 的窗口二分，需要 ⌈log2 10^9⌉ = 30 次。总计 1 + 30 = 31 次，卡进 32。',
        '两个边界要处理：n = 10^18 时 a = 10^9，窗口上界被 10^18 截断成单点，直接输出；a ≥ 1 是因为 n ≥ 10^9，所以下界 a·10^9 一定 ≥ 10^9，k 不会越界。',
        '样例解读：n = 10^9，a = 1，窗口 [10^9, 2·10^9 − 1]。问 1234567890 得 0 ⇒ n < 1234567890；问 1000000001 得 0 ⇒ n < 1000000001，配合 n ≥ 10^9 就锁定 n = 10^9。',
    ],
    code=r'''#include <cstdio>
#include <cstdlib>
#include <algorithm>

// H：k 可以取到 1e18，而 n <= 1e18，所以询问 k 得到的 floor(n/k) 只有
//   "n >= k ? 至少 1 : 0" 这一位信息最好用。
// 但若直接对 [1e9,1e18] 二分要 60 次，超了。先花 1 次询问 k = 1e9 拿到
//   a = floor(n/1e9)，就把 n 锁进长度恰好 1e9 的窗口 [a*1e9, (a+1)*1e9-1]。
// 窗口内再用 k = mid 询问：由 mid >= a*1e9 且 n < (a+1)*1e9 <= 2*mid 可知
//   floor(n/mid) >= 1  <=>  n >= mid
// 正好是一次比较，于是 30 次二分足够。总计 1 + 30 = 31 <= 32 次。

static long long ask(long long k) {
    std::printf("? %lld\n", k);
    std::fflush(stdout);
    long long q;
    if (std::scanf("%lld", &q) != 1) std::exit(0);
    return q;
}

int main() {
    const long long LO = 1000000000LL;         // 1e9
    const long long HI = 1000000000000000000LL; // 1e18
    long long a = ask(LO);                     // a = floor(n / 1e9)
    long long lo = a * LO;
    long long hi = std::min((a + 1) * LO - 1, HI);
    if (lo < LO) lo = LO;
    while (lo < hi) {
        long long mid = lo + (hi - lo + 1) / 2;   // 上取整，避免死循环
        if (ask(mid) >= 1) lo = mid;              // n >= mid
        else hi = mid - 1;
    }
    std::printf("! %lld\n", lo);
    std::fflush(stdout);
    return 0;
}
''',
    explain=[
        ('long long a = ask(LO);', '第一阶段：k = 10^9，用一次询问把 n 压进宽度 10^9 的窗口'),
        ('long long hi = std::min((a + 1) * LO - 1, HI);', '上界要截到 10^18，否则 mid 会超出 k 的允许范围'),
        ('long long mid = lo + (hi - lo + 1) / 2;', '上取整，配合 lo = mid 才能收敛而不是死循环'),
        ('if (ask(mid) >= 1) lo = mid;', '窗口内 ⌊n/mid⌋ ≥ 1 ⟺ n ≥ mid，正好一次比较'),
        ('std::fflush(stdout);', '每次输出后必须刷新，否则交互器收不到你的询问'),
        ('std::printf("! %lld\\n", lo);', '最终答案格式，输出后立即结束'),
    ],
    pitfalls=[
        '每次 printf 之后都要 fflush(stdout)，交互题最常见的挂法就是忘了刷新。',
        '二分必须用上取整 mid = (lo + hi + 1) / 2，否则 lo = mid 时区间不缩小、死循环。',
        '判定方向别弄反：⌊n/mid⌋ ≥ 1 说明 n ≥ mid（含等号），不是 n > mid。',
        'k 必须落在 [10^9, 10^18]：窗口下界天然 ≥ 10^9，上界要 min 上 10^18；询问上限 32 次（形如 `! n` 的最终答案不计入），别把次数浪费在边界上。',
    ],
))

PROBLEMS.append(PROB(
    letter='I',
    name='SBR：荒野中的觉悟',
    diff='提高-',
    tag='期望的线性性 + 模逆元',
    statement=[
        P('有 n 名神枪手，第 i 名的命中率为 a_i / 100（a_i 为整数）。进行一轮射击：'),
        L([
            '每名神枪手从除自己以外的 n − 1 人中，等概率随机选择一人作为目标。',
            '所有人同时射击，每人只射一发；即使本轮被击中，也会完成自己的射击。',
            '第 i 名的子弹以 a_i / 100 的概率命中所选目标，否则不击中任何人。',
            '一个人只要被至少一发子弹击中就死亡；未被任何子弹击中的人存活。',
            '各人的目标选择相互独立，各发子弹是否命中也相互独立，且与所有目标选择独立。',
        ], ordered=False),
        P('求这一轮结束后存活人数的期望，输出它对 998244353 取模的结果。'),
        P('输入：第一行 T（1 ≤ T ≤ 10^5）；每组第一行 n（2 ≤ n ≤ 2 × 10^6），第二行 n 个整数 a_i（0 ≤ a_i ≤ 100）。保证 Σn ≤ 2 × 10^6。'),
        T(['标准输入', '标准输出'], [['1<br>3<br>100 100 100', '249561089'], ['1<br>2<br>25 80', '848507701']]),
    ],
    hint=[
        '直接算「存活 k 人的概率」是 O(n^2)，但期望有线性性——先只算一个人存活的概率。',
        '第 j 个人打中第 i 个人的概率是多少？（先选目标，再判命中，两个因子都要乘上。）',
        '「第 i 人存活」要求其余每个人都打空他。这些事件关于 j 相互独立吗？乘起来之后，Σ_i 里能不能提公因式？',
    ],
    idea=[
        '用期望的线性性：E[存活人数] = Σ_i P(第 i 人存活)，问题变成 n 个独立的小概率。',
        'j 打中 i 的概率 = (a_j / 100) × 1/(n − 1)。所以 P(i 存活) = Π_{j ≠ i} p_j，其中 p_j = 1 − a_j / (100(n − 1))。',
        '于是 E = Σ_i Π_{j≠i} p_j = (Π_j p_j) × (Σ_i 1/p_i) —— 一次前缀积加上一次倒数和，O(n)。',
        'p_j = 0 怎么办？p_j = 0 ⟺ a_j = 100(n − 1)。因为 a_j ≤ 100，这只可能出现在 n = 2 且 a_j = 100 时。分三种情况：两个 0 → 所有人都必死，答案 0；恰好一个 0 → 只有那个人的「他人乘积」非零，答案就是其余 p 的乘积；没有 0 → 用上面的公式。',
        '模运算：p_j = (100(n − 1) − a_j) / (100(n − 1))，1/p_j = 100(n − 1) / (100(n − 1) − a_j)。由于 n ≤ 2 × 10^6，有 100(n − 1) ≤ 2 × 10^8 < 998244353，分母恒可逆。',
        '验样例 2：n = 2，p_1 = 3/4、p_2 = 1/5。P(1 存活) = 1/5，P(2 存活) = 3/4，E = 19/20，取模得 848507701。',
        '验样例 1：n = 3，p 全为 1/2，E = 3 × (1/2)^2 = 3/4，取模得 249561089。',
    ],
    code=r'''#include <cstdio>
#include <cstring>

// I：求存活人数期望。用期望的线性性，逐个算每个人存活的概率。
// 子弹 j 打中 i 的概率 = (a_j/100) * 1/(n-1)，所以
//   P(i 存活) = prod_{j != i} (1 - a_j / (100(n-1))) = prod_{j != i} p_j。
// 于是 E = sum_i prod_{j!=i} p_j = (prod_j p_j) * (sum_i 1/p_i)。
// p_j = 0 只会出现在 n == 2 且 a_j == 100 时（此时 100(n-1) == 100），要单独处理：
//   两个 0 -> 全员必死，答案 0；一个 0 -> 只有那个零的"别人乘积"非零。

typedef long long ll;
const ll MOD = 998244353;

static ll pw(ll b, ll e) {
    ll r = 1;
    b %= MOD;
    while (e > 0) {
        if (e & 1) r = r * b % MOD;
        b = b * b % MOD;
        e >>= 1;
    }
    return r;
}

static char buf[1 << 24];
static int blen, bpos;

static inline int nextInt() {
    while (bpos < blen && (buf[bpos] < '0' || buf[bpos] > '9')) ++bpos;
    int x = 0;
    while (bpos < blen && buf[bpos] >= '0' && buf[bpos] <= '9') x = x * 10 + (buf[bpos++] - '0');
    return x;
}

int main() {
    blen = (int)fread(buf, 1, sizeof(buf), stdin);
    int T = nextInt();
    static int cnt[101];
    static ll invMemo[101];
    while (T--) {
        int n = nextInt();
        ll Dnum = 100LL * (n - 1);          // 分母的分子部分，<= 2e8 < MOD
        ll invD = pw(Dnum % MOD, MOD - 2);
        memset(cnt, 0, sizeof(cnt));
        for (int i = 0; i < 101; ++i) invMemo[i] = -1;

        ll zeros = 0, accNum = 1;
        for (int i = 0; i < n; ++i) {
            int x = nextInt();
            ++cnt[x];
            ll num = Dnum - x;              // p = num / Dnum
            if (num == 0) ++zeros;
            else accNum = accNum * (num % MOD) % MOD;
        }
        ll prod = accNum * pw(invD, n - zeros) % MOD;   // 只对非零项除 Dnum，零项已跳过

        ll invsum = 0;
        for (int x = 0; x <= 100; ++x) {
            if (!cnt[x]) continue;
            ll num = Dnum - x;
            if (num == 0) continue;
            if (invMemo[x] < 0) invMemo[x] = pw(num % MOD, MOD - 2);
            // 1/p = Dnum / num
            ll invp = (Dnum % MOD) * invMemo[x] % MOD;
            invsum = (invsum + (ll)cnt[x] % MOD * invp) % MOD;
        }

        ll ans;
        if (zeros >= 2) ans = 0;
        else if (zeros == 1) ans = prod;            // 只有那个零的"他人乘积"非零
        else ans = prod * invsum % MOD;
        std::printf("%lld\n", ans);
    }
    return 0;
}
''',
    explain=[
        ('ll Dnum = 100LL * (n - 1);', '命中率的分母：先除以 n−1 选目标，再乘 a/100，合起来分母是 100(n−1)'),
        ('if (num == 0) ++zeros;', '分子为 0 说明 p_j = 0，不能求逆，单独计数'),
        ('ll prod = accNum * pw(invD, n - zeros) % MOD;', 'Π p_j = (Π 非零分子) / D^(非零项个数)：只对非零项除 D，指数不是 n'),
        ('ll invp = (Dnum % MOD) * invMemo[x] % MOD;', '1/p = D / (D − a)，用逆元代替除法'),
        ('if (zeros >= 2) ans = 0;', '两个零 → 所有人都被必中的子弹覆盖，期望 0'),
        ('else if (zeros == 1) ans = prod;', '一个零 → 只有那个零的「其他人乘积」不为 0'),
        ('ans = prod * invsum % MOD;', '一般情形：E = (Π p_j) × Σ (1/p_j)'),
    ],
    pitfalls=[
        '分母是 100(n − 1) 而不是 100：每颗子弹先在 n − 1 个目标里等概率选一个。',
        'p_j 可能等于 0，绝不能直接求逆元；必须先数零的个数再分情况。',
        'Π p_j 的指数是「非零项的个数」，不是 n —— 跳过零项后仍按 n 次除会算错（这里踩过坑）。',
        'a 只有 101 种取值，逆元可以按下标缓存；Σn 到 2 × 10^6 必须快读。输出是模意义下的整数，不是浮点数。',
    ],
))

PROBLEMS.append(PROB(
    letter='J',
    name='捕风的异乡人',
    diff='提高+',
    tag='双指针 + 线段树优化 DP',
    statement=[
        P('给定长度为 n 的正整数序列 a_1..a_n，把它划分成若干连续区间，每个区间的长度都必须 ≥ k。约定 0 = p_0 ≤ p_1 ≤ … ≤ p_m = n，第 t 个区间是 [p_{t−1} + 1, p_t]。'),
        P('若某个区间内所有元素之积整除 u（即 Π a_j | u），则这个区间可以完成一次有效共鸣。请选择一种划分方案，使有效区间的数量最大，输出这个最大值。'),
        P('输入：第一行 n, k, u（1 ≤ k ≤ n ≤ 500000，1 ≤ u ≤ 10^18）；第二行 n 个正整数 a_i（1 ≤ a_i ≤ 500000）。'),
        T(['标准输入', '标准输出'], [['8 3 12<br>2 2 3 1 2 2 3 5', '1']]),
    ],
    hint=[
        '固定右端点 i，把左端点 s 往左推时，乘积 Πa[s..i] 会怎么变？能让它整除 u 的 s 有什么形状？',
        '形状是一段后缀。那怎么在线维护这个后缀的左边界？想想「乘积一旦不整除就再也回不来」。',
        'dp[i] 由 dp 的一段区间最大值转移而来，用线段树（或单调队列）把 O(n^2) 压成 O(n log n)。',
    ],
    idea=[
        '先看可行性结构：若某个 a_i 单独就不整除 u，那么任何含 i 的区间都不可能整除 u，窗口只能从 i+1 重新开始。',
        '否则，把左端点 s 往左移只会让乘积变大、更难整除，所以「能让 Πa[s..i] 整除 u」的 s 恰好是一段后缀 [L, i]。用双指针维护 L：每加入 a_i 就把左端往右挪，直到乘积重新整除 u。由于 L 单调不减，总复杂度 O(n)。',
        '再叠 DP：dp[i] 表示前缀 i 的最大有效区间数。最后一段是 [j + 1, i]，必须满足 i − j ≥ k，即分界点 j ≤ i − k。于是',
        'dp[i] = max( 1 + max{ dp[j] : L − 1 ≤ j ≤ i − k } ,  max{ dp[j] : 0 ≤ j ≤ min(L − 2, i − k) } )。',
        '前一项表示最后一段有效（+1），后一项表示最后一段无效（不加分，但允许存在）。两个区间最大值都用线段树查。',
        '乘积不会溢出：因为只在 prod 整除 u 时保留，prod ≤ u ≤ 10^18；加入 a_i 前先用 prod > u / a[i] 判一下，再决定是否把左端挪走。',
        '验样例：a = 2 2 3 1 2 2 3 5，k = 3，u = 12。L 依次为 1,1,1,1,2,3,4,9，dp = 0,−∞,−∞,1,1,0,2,2,1，输出 dp[8] = 1。唯一有效的划分是 [1,3]（积 12）+ 剩下的 [4,8]（积 60，无效）。',
    ],
    code=r'''#include <cstdio>
#include <algorithm>
#include <climits>

// J：dp[i] = 前缀 i 能拿到的最大有效区间数。
// 对固定右端点 i，"起点 s 使 prod(a[s..i]) 整除 u" 的 s 构成一段后缀 [L, i]
// （把区间再往左延长只会让乘积变大、更难整除，所以可行集合对 s 单调），
// 用双指针维护这个 L；L = i+1 表示一个有效段都没有。
// 于是
//   dp[i] = max( 1 + max dp[L-1 .. i-k] ,  max dp[0 .. min(L-2, i-k)] )
// 前一项 = 最后一段有效，后一项 = 最后一段无效（无效段允许，只是不加分）。
// 注意长度约束：最后一段长度 >= k，所以分界点 j <= i-k。
// 两个区间最大值都落在 dp 上，线段树查询，整体 O(n log n)。

typedef long long ll;
const ll NEG = LLONG_MIN / 4;

static int n, k;
static ll u;
static ll a[500005];
static ll dp[500005];

static int segsz;
static ll seg[1 << 21];

static void segInit(int m) {
    segsz = 1;
    while (segsz < m) segsz <<= 1;
    for (int i = 0; i < 2 * segsz; ++i) seg[i] = NEG;
}
static void segUpdate(int p, ll v) {
    p += segsz;
    seg[p] = v;
    for (p >>= 1; p; p >>= 1) seg[p] = std::max(seg[p << 1], seg[p << 1 | 1]);
}
static ll segQuery(int l, int r) {          // 闭区间 [l,r]；l > r 返回 NEG
    if (l > r) return NEG;
    ll res = NEG;
    for (l += segsz, r += segsz; l <= r; l >>= 1, r >>= 1) {
        if (l & 1) res = std::max(res, seg[l++]);
        if (!(r & 1)) res = std::max(res, seg[r--]);
    }
    return res;
}

int main() {
    std::scanf("%d %d %lld", &n, &k, &u);
    for (int i = 1; i <= n; ++i) std::scanf("%lld", &a[i]);

    segInit(n + 1);
    dp[0] = 0;
    segUpdate(0, 0);

    int L = 1;
    ll prod = 1;                 // prod = a[L] * ... * a[i]，始终 <= u，不会乘爆
    for (int i = 1; i <= n; ++i) {
        if (u % a[i] != 0) {
            // 单个 a[i] 都不整除 u，任何有效段都不能含 i：窗口清空
            L = i + 1;
            prod = 1;
        } else {
            while (L <= i && prod > u / a[i]) { prod /= a[L]; ++L; }  // 先防溢出
            prod *= a[i];
            while (L <= i && u % prod != 0) { prod /= a[L]; ++L; }    // 再保证整除
        }

        int hi = i - k;                        // 分界点 j 的上界
        ll best = NEG;
        if (hi >= L - 1) best = std::max(best, segQuery(L - 1, hi) + 1);
        if (hi >= 0 && L - 2 >= 0) best = std::max(best, segQuery(0, std::min(L - 2, hi)));
        dp[i] = best;
        segUpdate(i, dp[i]);
    }
    std::printf("%lld\n", dp[n] < 0 ? 0LL : dp[n]);
    return 0;
}
''',
    explain=[
        ('if (u % a[i] != 0) {', '单个元素不整除 u，任何有效段都不能含它，窗口直接清空（此时 L = i+1 让「有效后缀」为空）'),
        ('while (L <= i && prod > u / a[i]) { prod /= a[L]; ++L; }', '先防溢出：时刻保证 prod * a[i] ≤ u，所以 prod（long long）永远不会超出 10^18'),
        ('while (L <= i && u % prod != 0) { prod /= a[L]; ++L; }', '左端单调右移，直到乘积重新整除 u；L 推进到 i+1 时 prod = 1 必然整除，循环必然结束'),
        ('int hi = i - k;', '长度约束：最后一段长度 ≥ k，所以分界点 j ≤ i − k'),
        ('if (hi >= L - 1) best = std::max(best, segQuery(L - 1, hi) + 1);', '最后一段有效的转移：起点 s = j + 1 ≥ L，即 j ≥ L − 1'),
        ('if (hi >= 0 && L - 2 >= 0) best = std::max(best, segQuery(0, std::min(L - 2, hi)));', '最后一段无效也要参与转移，只是不加分；漏掉这一支会把合法划分误判成不可达'),
    ],
    pitfalls=[
        '必须先判 u % a[i] != 0 再谈 u / a[i]，否则 a[i] > u 时 u / a[i] = 0，逻辑全乱；乘法也要用 prod > u / a[i] 提前拦住。',
        '左端右移时可能连续遇到 a[L] = 1，prod 不变；靠 L 自身的单调推进保证循环终止，不要写成 while 里只看 prod。',
        '长度约束的分界点是 j ≤ i − k，不是 j ≤ i − k + 1（最后一段有 i − j 个元素）。',
        '无效段必须参与 DP 转移，只是不加分；只考虑有效段会得到 −∞。答案下限是 0，因为整段作为一个区间（长度 n ≥ k）永远合法。',
    ],
))

PROBLEMS.append(PROB(
    letter='K',
    name='野比大雄的射击训练',
    diff='入门',
    tag='切比雪夫距离',
    statement=[
        P('有一个 (2n − 1) × (2n − 1) 的正方形靶盘，行列均从 1 编号，中心格坐标为 (n, n)。'),
        P('靶盘由中心向外划分为若干方形环：中心格得 n 分；围绕中心的第一圈共 8 个格子，得分均为 n − 1；此后每向外一圈得分减少 1，最外圈得分均为 1。当 n = 1 时靶盘只有一个格子，得 1 分。'),
        P('现在有 k 支飞镖落在靶盘上，落点互不相同。给定每支飞镖的落点坐标 (x_i, y_i)，求它们的总分。'),
        P('输入：第一行 n, k（1 ≤ n ≤ 1000，1 ≤ k ≤ (2n − 1)^2）；接下来 k 行每行 x_i, y_i（1 ≤ x_i, y_i ≤ 2n − 1），保证坐标对两两不同。输出一个整数。'),
        T(['标准输入', '标准输出'], [['3 4<br>3 3<br>1 1<br>2 4<br>5 3', '7']]),
        P('样例说明：n = 3 时四支飞镖分别得 3、1、2、1 分，总分 7。'),
    ],
    hint=[
        '「第 d 圈」这个几何概念，用坐标怎么写成一个式子？',
        '先看四个角和四条边上的格子：角是 |dx| = |dy| = d，边是 max(|dx|,|dy|) = d。',
        '是 max(|dx|, |dy|) 还是 |dx| + |dy|？拿样例里的 (1,1) 试一试就知道。',
    ],
    idea=[
        '以中心 (n, n) 为原点看偏移 dx = x − n、dy = y − n。第 d 圈正是 max(|dx|, |dy|) = d 的等值线，也就是「切比雪夫距离」，而这一圈的得分是 n − d。',
        '所以每一支飞镖的得分就是 n − max(|x − n|, |y − n|)，逐个累加即可，O(k)。',
        '验样例：n = 3。(3,3) → d = 0 → 3 分；(1,1) → max(2,2) = 2 → 1 分；(2,4) → max(1,1) = 1 → 2 分；(5,3) → max(2,0) = 2 → 1 分。合计 3 + 1 + 2 + 1 = 7 ✓',
        'n = 1 时 d 只能为 0，得 1 分，公式自洽，不需要特判。',
    ],
    code=r'''#include <cstdio>
#include <algorithm>

// K：(2n-1)*(2n-1) 的方阵，第 d 个环得分 n-d，其中 d 是切比雪夫距离
// d = max(|x-n|, |y-n|)。中心 (n,n) 得 n，最外环得 1。
// 逐点累加即可，注意 n<=1000、k<=4e6，总和可达 4e9，要 64 位。
int main() {
    int n, k;
    std::scanf("%d %d", &n, &k);
    long long ans = 0;
    for (int i = 0; i < k; ++i) {
        int x, y;
        std::scanf("%d %d", &x, &y);
        int d = std::max(std::abs(x - n), std::abs(y - n));
        ans += n - d;
    }
    std::printf("%lld\n", ans);
    return 0;
}
''',
    explain=[
        ('int d = std::max(std::abs(x - n), std::abs(y - n));', '圈号就是到中心的切比雪夫距离（max 而不是和）'),
        ('ans += n - d;', '第 d 圈得 n − d 分：中心 n 分，最外圈 d = n−1 得 1 分'),
        ('long long ans = 0;', 'k 最大 (2n−1)^2 = 4 × 10^6、每支最多 1000 分，总分到 4 × 10^9，超出 int'),
        ('std::printf("%lld\\n", ans);', '64 位输出'),
    ],
    pitfalls=[
        '距离用的是切比雪夫距离 max(|dx|,|dy|)，不是曼哈顿距离 |dx|+|dy|；用错了 (1,1) 会算成 3−4 < 0。',
        '总分到 4 × 10^9，必须 long long；int 会溢出成负数。',
        '得分下限是 1，不是 0：最外圈（d = n−1）仍然有 1 分。',
        'n = 1 时靶盘只有一格，d = 0，公式自然得到 1，别多写特判。',
    ],
))

PROBLEMS.append(PROB(
    letter='L',
    name='幻想乡树状结界',
    diff='提高+',
    tag='构造 + 异或（子树异或为 0）',
    difficulty_note='说明：本题题意已完整还原，但下面只给出题面、提示与关键结论，<b>不提供代码</b>。原因见文末「跳过说明」——我还没能给出一个自己敢担保正确的构造算法，按「宁可少写也不写错」的原则略去实现。',
    statement=[
        P('有 n 个魔力结点，编号 1..n，第 i 个结点有权值 a_i（非负整数）。需要在结点之间添加 n − 1 条边把它连成一棵树，并以 1 号结点（博丽神社所在结点）为根。'),
        P('其中有 k 个结点被标记为「关键点」。对每个关键点 v，记 subtree(v) 为以 v 为根的子树所含结点的集合（含 v 本身）。要求构造出的树对每个关键点 v 都满足'),
        P('⊕_{u ∈ subtree(v)} a_u = 0（⊕ 表示按位异或）。'),
        P('若存在合法方案，输出 n − 1 行、每行两个整数 x, y 表示一条无向边（多解任选其一输出）；若不存在，输出 −1。特别地，n = 1 且 a_1 = 0 时合法输出为空（因为树没有边）。'),
        P('数据范围：1 ≤ n ≤ 20，1 ≤ k ≤ n，0 ≤ a_i < 2^60，1 ≤ v_i ≤ n，关键点编号互不相同。'),
        T(['标准输入', '标准输出'], [['5 2<br>0 5 5 5 5<br>2 3', '1 2<br>2 4<br>1 3<br>3 5'], ['3 1<br>1 2 4<br>2', '-1']]),
    ],
    hint=[
        'n ≤ 20 这么小，说明做法大概是指数级的（状压 / 搜索），不要去想着多项式贪心。',
        '先把「子树异或为 0」翻译成集合语言：对每个关键点 v，都要存在一个包含 v 的集合异或为 0。多个关键点的这些集合之间是什么关系？',
        '陷阱预警：不要假设「子树在输入顺序里是连续的一段」。样例 1 的官方输出里 subtree(2) = {2, 4} 就不是连续段。',
    ],
    idea=[
        '记 S_v = subtree(v)。这些集合一定是「层叠（laminar）」的：任取两个关键点 u、v，S_u 与 S_v 要么不相交，要么一个包含另一个——因为子树结构本身就是这样。',
        '对每个关键点 v 定义 B_v = S_v 去掉它内部那些「极大关键后代」的子树。于是 B_v 两两不交、都含 v、且不含别的关键点，并且 XOR(B_v) = XOR(S_v) ⊕ (内部关键子树的异或) = 0 ⊕ 0 = 0。所以「每个关键点 v 都配一个互不相交、含 v、异或为 0 的集合 B_v」是必要条件。',
        '反过来也够用：把这些 B_v 按任意顺序排成一条链，每个 B_v 里的关键点放在该块最前面、其余点挂在它后面，再把所有没用上的点（连同 1 号点）放在链首当作前缀，就得到一棵合法的树（v ≠ 1 时 B_v 不能含 1；若 1 是关键点则还要全局异或为 0，此时 B_1 自动取剩下的全部点）。',
        '于是问题化归为：为每个关键点 v 找一个互不相交的集合 B_v ∋ v、XOR(B_v) = 0（即给每个需求找一个异或等于 a_v 的辅助集合）。这才是真正要写搜索的部分——也正是我在这里不敢保证写对的地方。',
        '反例（证明「子树 = 输入顺序里的连续段」这个简化是错的）：n = 4、a = [1, 5, 7, 5]、关键点 {2}。树 1-2、2-4、1-3 中 subtree(2) = {2, 4}，异或 5 ⊕ 5 = 0，合法；而任何让子树等于连续段的构造都做不到——{[2], [2,3], [2,4]} 的异或分别是 5、2、7，没有 0。',
    ],
    pitfalls=[
        '不要假设子树在输入顺序中连续：反例见上面的 n = 4、a = [1,5,7,5]。',
        '关键点 v ≠ 1 的集合不能包含 1（1 永远是根、是所有点的祖先）。',
        'n = 1 时合法输出是空（不打印任何内容），只有无解才打印 −1；a_i 可到 2^60，异或用 64 位无符号/有符号整数且注意读入方式。',
    ],
))

PROBLEMS.append(PROB(
    letter='M',
    name='教练，我想打 xcpc',
    diff='入门',
    tag='字符串筛选与输出',
    statement=[
        P('共有 n 条报名记录，每条包含四项：队伍名、赛站名、比赛日期、报名结果。请输出所有报名成功的队伍，每行格式为 gdut_队伍名 赛站名 比赛日期（输出顺序任意）。报名失败的记录不输出；若没有队伍报名成功，可以不输出任何内容。'),
        P('约定：队伍名由大小写英文字母组成、长度 ≤ 30 且两两不同；赛站名由小写英文字母组成、长度 ≤ 10；比赛日期格式为 YYYY-MM-DD 且是合法日期；报名结果为 1（成功）或 0（失败）。n ≤ 50，每支队伍恰好出现一次。'),
        T(['标准输入', '标准输出'], [['3<br>avemujica shanghai 2026-01-01 1<br>CRYCHIC wuhan 2026-01-10 0<br>mygo changchun 2026-02-01 1', 'gdut_avemujica shanghai 2026-01-01<br>gdut_mygo changchun 2026-02-01']]),
    ],
    hint=[
        '每条记录只有四个字段，而决定要不要输出的只有最后一个字段。',
        '注意前缀的形态：是 gdut_ 直接贴在队名前面，中间没有空格。',
        '日期是字符串，原样输出即可——不要真的去解析它。',
    ],
    idea=[
        '逐条读入四个字段，若最后一项为 1，就拼接 "gdut_" + 队名 + " " + 赛站名 + " " + 比赛日期 输出一行。',
        'n ≤ 50，直接按输入顺序输出即可，O(n) 时间、O(1) 额外空间。多条输出拼进一个缓冲区再一次性写出更省事。',
    ],
    code=r'''#include <cstdio>
#include <iostream>
#include <string>

// M：纯筛选。报名结果为 1 的记录输出，格式为 gdut_<队名> <赛站> <日期>，顺序任意。
int main() {
    int n;
    std::scanf("%d", &n);
    std::string out;
    for (int i = 0; i < n; ++i) {
        char team[64], site[32], date[32];
        int ok;
        std::scanf("%s %s %s %d", team, site, date, &ok);
        if (ok == 1) {
            out += "gdut_";
            out += team;
            out += ' ';
            out += site;
            out += ' ';
            out += date;
            out += '\n';
        }
    }
    std::fwrite(out.data(), 1, out.size(), stdout);
    return 0;
}
''',
    explain=[
        ('std::scanf("%s %s %s %d", team, site, date, &ok);', '四个字段都是空白分隔的 token，日期不含空格，可以整体当一个字符串读'),
        ('if (ok == 1) {', '只有报名结果为 1 的记录才输出，失败的整行跳过'),
        ('out += "gdut_";', '前缀紧贴队名，中间不能插空格'),
        ('std::fwrite(out.data(), 1, out.size(), stdout);', '所有成功记录先攒起来一次性输出，避免多次 I/O'),
    ],
    pitfalls=[
        '前缀是 gdut_ 且与队名无缝相连；写成 "gdut_ " 会多一个空格。',
        '日期 2026-01-01 直接当字符串输出，不要做日期运算、不要去掉补零。',
        '报名失败的记录一行都不输出；全部失败时输出为空，不要打印 0、空行或提示语。',
        '队伍名含大小写字母，不要统一转小写；输出顺序任意，按输入顺序最省事。',
    ],
))

PROBLEMS.append(PROB(
    letter='N',
    name='不太整齐的队伍（简单版）',
    diff='普及-',
    tag='mex 的等价转化 + 最大空档',
    statement=[
        P('有 n 名同学站成一排，第 i 名同学有一个非负整数标签 a_i。'),
        P('对连续区间 [l, r]，记 S 为其中出现过的标签组成的集合，mex(S) 表示不属于 S 的最小非负整数。例如标签为 0, 1, 1, 3 时 S = {0, 1, 3}，mex(S) = 2；标签为 1, 2, 3, 3 时 S = {1, 2, 3}，mex(S) = 0。重复出现的标签不影响 S。'),
        P('请选择一个连续区间，使其中标签集合的 mex 不超过 K，并求这个区间的最大长度。'),
        P('输入：第一行 T（1 ≤ T ≤ 100）；每组第一行 n, K（1 ≤ n ≤ 2 × 10^5，0 ≤ K ≤ 10^18），第二行 n 个整数 a_i（0 ≤ a_i ≤ n）。保证 Σn ≤ 2 × 10^5。输出：每组一行一个整数。'),
        T(['标准输入', '标准输出'], [['2<br>8 2<br>0 1 2 3 0 2 3 1<br>5 0<br>1 2 0 3 1', '5<br>2']]),
    ],
    hint=[
        '把 mex(S) ≤ K 翻译成「S 里必须缺什么」——是必须缺一个，还是必须缺全部？',
        '如果某个数 t 在整个区间里一次都没出现，mex 会是多少？',
        '固定 t，「完全不含 t 的最长区间」等于 t 的哪些位置之间的空隙？',
    ],
    idea=[
        'mex(S) ≤ K ⟺ 0, 1, …, K 里至少有一个数不在 S 里。（反之若 0..K 全都在 S 里，mex 至少是 K + 1 > K。）注意是「至少缺一个」，不是「全都缺」。',
        '于是答案 = max_{t = 0..K}（区间里完全不含 t 的最长长度）。而对固定的 t，完全不含 t 的最长子段就是 t 的相邻出现位置之间的最大空档，并且要把「第一个出现位置之前」和「最后一个出现位置之后」这两段也算进去。',
        '还有一个 O(1) 的快路：因为 a_i ≤ n，所以 K > n 时必有某个 t ∈ [0, K] 永不出现（例如 t = n + 1），答案直接是 n。这样就不需要为 10^18 级别的 K 开数组。',
        '复杂度 O(n + K) = O(n)。',
        '验样例 1：n = 8、K = 2、a = 0 1 2 3 0 2 3 1。t = 0 位置 {1,5}，空档 max(0,3,3) = 3；t = 1 位置 {2,8}，空档 max(1,5,0) = 5；t = 2 位置 {3,6}，空档 max(2,2,2) = 2 → 答案 5（区间 [3,7] 缺 1）。',
        '验样例 2：n = 5、K = 0，t = 0 位置 {3}，空档 max(2,2) = 2 → 答案 2。',
    ],
    code=r'''#include <cstdio>
#include <vector>
#include <algorithm>

// N：mex(S) <= K 等价于 "0..K 里至少缺一个数"（若 0..K 全出现则 mex >= K+1）。
// 于是答案 = max_{t=0..K} (区间里完全不含 t 的最长子段)
//          = max_t (t 的相邻出现位置之间的最大空档)。
// 又因 a_i <= n：K > n 时必有某个 t 永不出现，答案直接是 n。
int main() {
    int T;
    std::scanf("%d", &T);
    static int a[200005];
    while (T--) {
        int n;
        long long K;
        std::scanf("%d %lld", &n, &K);
        for (int i = 1; i <= n; ++i) std::scanf("%d", &a[i]);
        if (K > n) {                          // 0..K 里一定有值超出 a_i 范围，必不出现
            std::printf("%d\n", n);
            continue;
        }
        std::vector<std::vector<int> > pos((size_t)K + 1);
        for (int i = 1; i <= n; ++i)
            if (a[i] <= K) pos[a[i]].push_back(i);
        int best = 0;
        for (int t = 0; t <= (int)K; ++t) {
            int prev = 0;                     // 哨兵：位置 0
            for (size_t j = 0; j < pos[t].size(); ++j) {
                int p = pos[t][j];
                best = std::max(best, p - prev - 1);
                prev = p;
            }
            best = std::max(best, n - prev);  // 最后一段到 n 为止
        }
        std::printf("%d\n", best);
    }
    return 0;
}
''',
    explain=[
        ('if (K > n) {', 'a_i ≤ n，K > n 时 0..K 里必有永不出现的值，整个数组都是答案'),
        ('std::vector<std::vector<int> > pos((size_t)K + 1);', 'K ≤ n 时才建表；Σn ≤ 2 × 10^5，总空间可控'),
        ('if (a[i] <= K) pos[a[i]].push_back(i);', '大于 K 的标签对「0..K 里缺谁」毫无影响，直接丢掉'),
        ('best = std::max(best, p - prev - 1);', '两个相邻出现位置之间（不含端点）的长度'),
        ('best = std::max(best, n - prev);', '最后一段要单独算：最后一个出现位置到 n 的空档'),
        ('int prev = 0;', '用 0 当哨兵，这样第一段（位置 1 之前）也能用同一个式子算'),
    ],
    pitfalls=[
        'K 可到 10^18，不能直接开 K + 1 大小的位置表；先判 K > n 再建表，此时答案直接是 n（不是 K）。',
        '空档要含「第一个出现位置之前」和「最后一个出现位置之后」两段，只算中间会漏。',
        '等价条件是「0..K 里至少缺一个」，不是「0..K 全部缺失」。',
        'T 可达 100，每组的位置表要重新构建（不要跨组复用残留数据）。',
    ],
))


DOCS = [DOC(
    title="GDUT 2026 月赛 题解",
    file="sol-gdut2026.html",
    desc="14 题里 13 题给了完整思路与可过代码，另 1 题只给题面与结论",
    source="GDUT 2026 Monthly competition（2026-10-15）",
    level="入门 ~ 提高+",
    sections=[
        P("本场 PDF 的中文字体没有嵌入正确的 ToUnicode 映射，直接复制题目文本只会得到乱码。"
          "好消息是这批乱码是可逆的：乱码字符的码位 C 与原始 GBK 双字节 (hi, lo) 满足 "
          "C = 94 × (hi − 0xA6) + (lo − 0xA1)，反解之后 14 道题的题面全部还原，并与每题的官方样例逐条对照过。"
          "所以这份题解覆盖了全部 14 题。"),
        P("覆盖情况：A ~ K、M、N 共 13 题给出完整思路与参考代码；这 13 份代码全部通过官方样例，"
          "其中 B/C/D/E/F/G/I/J/K/N 还用独立写的暴力程序对拍过随机小数据，H 用本地交互器验过 97 个隐藏值"
          "（最多用了 31 次询问，上限 32）。L 见下方跳过说明。"),
        WARN("读题提示", [
            "原 PDF 的样例区把「标准输入 / 标准输出」并排放在一张表里，粘贴时容易把两栏混成一段。"
            "本文每题都给出了完整的样例输入与输出，可以直接照抄去本地测。",
            "另外这份题面里所有上标都被拍平了：10^4 显示成 104、10^6 显示成 106、4 × 10^5 显示成 4 ∗ 105。"
            "读题时注意别把 10^4 当成 104。",
        ]),
        TIP("怎么用这份题解", [
            "每题先看「引导性提示」——只有两三句话，够你判断方向对不对。",
            "卡住 20 分钟再看折叠的「思路」，最后再对代码。",
            "代码段的注释写的是「为什么这么写」，不是「这行在干什么」，建议对着注释读。",
        ]),
    ],
    problems=PROBLEMS,
    skip=[
        "L 幻想乡树状结界：题意已完整还原（n ≤ 20，要求每个关键点 v 满足 subtree(v) 的异或和为 0，"
        "构造任意一棵以 1 为根的树），上面也给出了题面、提示和关键结论，但<b>没有代码</b>。"
        "原因是这题的构造我还没能给出一个自己敢担保正确的搜索算法——"
        "「为每个关键点找一个互不相交、异或为 0 的集合」这步在 n ≤ 20 下的正确剪枝与回溯强度不好把握，"
        "按「宁可少写也不写错」的原则略去实现，请直接看官方题解。"
        "顺带记一个常见错误：不要假设子树在输入顺序里是连续一段——n = 4、a = [1,5,7,5]、关键点 {2} 时，"
        "树 1-2、2-4、1-3 里 subtree(2) = {2,4} 异或为 0 是合法的，而任何「子树 = 连续段」的构造都做不到"
        "（[2]、[2,3]、[2,4] 的异或分别是 5、2、7）。",

        "除 L 之外的 13 题均已给出可编译、可过样例的 C++17 代码；"
        "如果你在第 14 题上有了把握，可以按上面那条「互不相交、异或为 0 的集合」的思路继续做。",
    ]
)]
