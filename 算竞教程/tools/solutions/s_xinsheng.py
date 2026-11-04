# -*- coding: utf-8 -*-
"""2025 广工新生赛（初赛）10 题题解。B 为读入练习，跳过。"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from solutions.dsl_sol import *  # noqa: E402,F401,F403

PROBLEMS = []

# ---------------------------------------------------------------- A
PROBLEMS.append(PROB(
    letter="A",
    name="最大子串匹配删除操作",
    diff="提高-",
    tag="把操作序列化成「后缀链」，标准化后用 Z 函数 + 二分判定",
    statement=[
        "给定两个只含小写字母的字符串 S、T，1 ≤ |S|, |T| ≤ 2×10^5。反复执行下面两种操作之一，直到 T 变空：",
        L([
            "删除操作：删掉 T 的第一个字符，S 不变。",
            "匹配删除操作：若当前 T 恰好等于当前 S 的某个子串 S[i..j]，则删掉 S 的前缀 S[1..j]（S 只剩后缀 S[j+1..]），同时删掉 T 的第一个字符。",
        ]),
        "删除操作不算分，匹配删除算一次得分。求最多能做多少次匹配删除。",
        "输入两行，分别是 S 和 T；输出一个整数。样例：S = abcb、T = aab 时答案是 2。",
    ],
    hint=[
        "删除操作只动 T、不动 S，所以它随时都能补做：真正要决定的只有「哪些匹配做、按什么位置做」。",
        "一次匹配删除之后，S 的可用部分变成某个后缀，T 的可用部分也变成某个后缀。于是整个过程是一条链：第 t 次匹配吃掉 T 的某个后缀，位置必须在上一次结束之后。",
        "如果一条链做了 k 次匹配，第 t 次匹配用的后缀长度至少是多少？把这些长度加起来，k 最大能到多少？",
    ],
    idea=[
        "先换个说法。设第 t 次匹配用的是 T 的后缀 T[q_t..|T|]（长度 L_t = |T|-q_t+1），它出现在 S 的 i_t 处。那么必须 q_t 严格递增，且 i_{t+1} ≥ i_t + L_t（不重叠、从左到右）。删除操作只负责把 q 从 q_t 推到 q_{t+1}，随时可做，所以一条这样的链一定对应一个合法操作序列，反之亦然。问题就是求最长链。",
        "关键标准化：任何一条长 k 的链，都可以换成「长度恰为 k, k-1, ..., 1」的链。理由：T 的长 L 后缀以 T 的长 L' 后缀（L' 小于 L）为后缀，所以若长 L 后缀出现在 i，则长 L' 后缀出现在 i + (L - L')；令 j_t = i_t + (L_t - (k-t+1))，逐项验证 j_{t+1} ≥ j_t + (k-t+1)，不等号两边只差 (i_{t+1} - i_t - L_t) + L_{t+1} - (k-t) ≥ 0，成立。于是「能取 k 次」等价于「把长度 k, k-1, ..., 1 的后缀依次塞进 S」。",
        "长度序列固定后，贪心就是最优：每个后缀取它能取到的最左出现位置。长度固定时起点最左等价于终点最左，留给后面的 S 最多，这是标准交换论证。所以判定 k 只需要从左往右扫一遍，复杂度 O(|S|)。",
        "判定对 k 单调：长度为 k 的标准链去掉第一段就是 k-1 的标准链，所以二分答案。又因为 1+2+...+k ≤ |S|，k 上界是 632（|S| = 2×10^5），二分只要 10 次判定。",
        "「T 的长 L 后缀在 S 中最左出现在哪」用一次 Z 函数解决：把 S、T 都反转，T 的后缀变成 T' 的前缀，在 T'+'#'+S' 上跑 Z，z 值就是 S' 某位置与 T' 的 LCP，于是 O(1) 判定某个位置能否放长度 L 的后缀。总复杂度 O(|S| + |T| + |S| log min(|T|, 632))。",
    ],
    code=r"""#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string S, T;
    if (!(cin >> S >> T)) return 0;
    int n = S.size(), m = T.size();

    // 反转后 T 的后缀变成 T' 的前缀：一次 Z 函数就能 O(1) 判断任意位置能否放任意长度的后缀
    string Sr(S.rbegin(), S.rend()), Tr(T.rbegin(), T.rend());
    string U = Tr + "#" + Sr;
    int len = U.size();
    vector<int> z(len, 0);
    for (int i = 1, l = 0, r = 0; i < len; i++) {
        if (i <= r) z[i] = min(r - i + 1, z[i - l]);
        while (i + z[i] < len && U[z[i]] == U[i + z[i]]) z[i]++;
        if (i + z[i] - 1 > r) { l = i; r = i + z[i] - 1; }
    }
    int base = m + 1;                        // U 中 S' 部分的起点
    auto ok = [&](int i, int L) {            // S[i..i+L-1] 是否等于 T 的长 L 后缀
        return z[base + (n - i - L)] >= L;   // 对应到 S' 里的起点是 n-i-L
    };
    auto check = [&](int k) {                // 长度 k,k-1,...,1 的标准链能否塞进 S
        int p = 0;
        for (int L = k; L >= 1; L--) {
            int i = p;                       // 每个后缀都取能取到的最左位置
            while (i + L <= n && !ok(i, L)) i++;
            if (i + L > n) return false;
            p = i + L;                       // 下一段必须从这里之后开始
        }
        return true;
    };

    int hi = min(m, (int)((sqrt(8.0 * n + 1) - 1) / 2));  // 1+2+...+k 不能超过 |S|
    int lo = 0;
    while (lo < hi) {                        // 可行性对 k 单调，二分
        int mid = (lo + hi + 1) >> 1;
        if (check(mid)) lo = mid; else hi = mid - 1;
    }
    cout << lo << '\n';
    return 0;
}
""",
    explain=[
        ("string U = Tr + \"#\" + Sr;",
         "把两个串都反转。T 的长 L 后缀反转后是 T' 的长 L 前缀，于是「后缀出现」变成「前缀出现」，一次 Z 函数覆盖所有长度。"),
        ("return z[base + (n - i - L)] >= L;",
         "S[i..i+L-1] 等于 T 的长 L 后缀，等价于反转后 S' 从 n-i-L 起与 T' 的 LCP 至少为 L。下标 n-i-L 是被反转映射出来的，少减一个 L 就整体错位。"),
        ("while (i + L <= n && !ok(i, L)) i++;",
         "固定长度后最左出现就是最优：终点也最左，给后面的后缀留下最多的 S。贪心的正确性由交换论证保证。"),
        ("int hi = min(m, (int)((sqrt(8.0 * n + 1) - 1) / 2));",
         "长度 k,k-1,...,1 至少占 k(k+1)/2 个字符，所以 k 不超过 sqrt(2|S|) ≈ 632；同时不能超过 |T|。缺任何一个上界都可能判出非法的大 k。"),
        ("if (check(mid)) lo = mid; else hi = mid - 1;",
         "标准链去掉第一段就是 k-1 的标准链，可行性单调，所以能二分。"),
    ],
    pitfalls=[
        "「能匹配就立刻匹配」的贪心是错的：S = ddddddd、T = dddd 时一上来吃掉 dddd 只剩 2 次，正确答案是 3（先跳过 d，用长度 3、2、1）。症状是 WA 而不是 TLE。",
        "把 T 的后缀当成 T 的前缀：样例 acmer / medal 的正确输出是 0，若只看前缀会算出 1（a 匹配 a），属于读题错误。",
        "二分上界只取 |T| 不取 sqrt(2|S|)：check 会去试明显塞不下的 k，虽然结果一般还对，但如果 check 里没做长度越界检查就会读错下标甚至越界。",
        "Z 函数里 T 与 S 之间忘了加分隔符 '#'，LCP 会跨过 T 的末尾继续比，导致 ok 判定偏大。",
    ],
))

# ---------------------------------------------------------------- B 跳过

# ---------------------------------------------------------------- C
PROBLEMS.append(PROB(
    letter="C",
    name="逃出生天",
    diff="普及+",
    tag="把老虎位置写成时间的周期函数，在 (格子, 时刻 mod 周期) 上 BFS",
    statement=[
        "一个 n 行 m 列的网格，2 ≤ n, m ≤ 100。小猪从右上角 (1, m) 出发，要到左下角 (n, 1)。每一行都有一只老虎：第 i 行的老虎初始在第 c_i 列，初始方向 d_i 是 L 或 R，保证 c_1 ≠ m（起点安全）。",
        "每一时刻的时序是：小猪先动（可以走上、下、左、右或原地，不能出界），然后所有老虎同时动。老虎只会沿当前方向走一格；若该方向的前方出界，则先掉头再走一格。",
        "任何时刻（任一方移动前、移动后）小猪都不能与老虎同格，走到出口的那一刻也一样。问小猪能否到达出口，输出 YES 或 NO（大小写随意）。",
    ],
    hint=[
        "第 i 只老虎永远待在第 i 行，所以当小猪在 (x, y) 时，真正需要担心的只有第 x 行那一只。",
        "一行里左右来回走的老虎，位置随时间变化是周期性的。试试把列号换成「相位」，看 t 次移动之后它在哪。",
        "如果任意时刻老虎的位置都能 O(1) 算出来，那小猪的状态除了坐标还需要记录什么？",
    ],
    idea=[
        "老虎只在它所在的行里活动，所以小猪走到 (x, y) 时只可能撞上第 x 行的老虎。这一条把「与所有老虎判重」降成「与一只老虎判重」。",
        "单只老虎在一行内左右折返，位置是周期 2(m-1) 的三角波。取相位：初始方向 R 时相位 = c-1，初始方向 L 时相位 = 2(m-1)-(c-1)；那么做完 t 次移动后，位置列号是令 x = (相位+t) mod 2(m-1)，若 x ≤ m-1 则是 1+x，否则是 2m-1-x。这样任意时刻位置 O(1) 求出。注意 m = 2 时周期是 2，公式依然成立。",
        "所有老虎的周期都是 2(m-1)（与初始位置无关），所以整个局面以 2(m-1) 为周期重复。于是 BFS 的状态是 (行, 列, t mod 2(m-1))，状态数 n·m·2(m-1) ≤ 100·100·198 ≈ 2×10^6，每个状态枚举 5 种移动。",
        "转移要按题目时序检查两次：小猪先动，落点不能是时刻 t 的老虎格；然后老虎动，落点不能是时刻 t+1 的老虎格。两次都过了才把 (nr, nc, (t+1) mod 周期) 入队；若落点就是 (n,1) 且第二次检查通过，直接输出 YES。",
        "为什么状态里一定要带时间？同一个格子在时刻 t 和 t + 2(m-1) 是同一局面，但在时刻 t 与 t+1 的生死判断完全不同；只用 (行,列) 做 BFS 会漏掉「必须等老虎走开」的解，也会把不同时刻混成一点。",
    ],
    code=r"""#include <bits/stdc++.h>
using namespace std;

int main() {
    int n, m;
    if (scanf("%d %d", &n, &m) != 2) return 0;
    vector<int> c(n);
    vector<char> d(n);
    for (int i = 0; i < n; i++) scanf("%d %c", &c[i], &d[i]);

    int P = 2 * (m - 1);                     // 老虎位置的周期
    vector<int> ph(n);
    for (int i = 0; i < n; i++) {
        int x = c[i] - 1;
        ph[i] = (d[i] == 'R') ? x : (P - x) % P;   // 相位：位置只由 (ph + t) % P 决定
    }
    auto pos = [&](int row, int t) {          // 第 row 行老虎在时刻 t 的列号（1-indexed）
        int x = (ph[row] + t) % P;
        return x <= m - 1 ? 1 + x : 2 * m - 1 - x;   // 超过 m 的部分折返
    };

    vector<char> vis((size_t)n * m * P, 0);
    auto id = [&](int r, int col, int t) { return ((size_t)r * m + col) * P + t; };
    vector<int> q;
    int st = (int)id(0, m - 1, 0);            // 起点 (1, m)，0-indexed 是 (0, m-1)
    q.push_back(st);
    vis[st] = 1;
    const int dr[5] = {-1, 1, 0, 0, 0}, dc[5] = {0, 0, -1, 1, 0};
    for (size_t h = 0; h < q.size(); h++) {
        int cur = q[h];
        int t = cur % P, cell = cur / P, r = cell / m, col = cell % m;
        for (int k = 0; k < 5; k++) {
            int nr = r + dr[k], nc = col + dc[k];
            if (nr < 0 || nr >= n || nc < 0 || nc >= m) continue;
            if (nc + 1 == pos(nr, t)) continue;      // 小猪先动：落点上正站着老虎
            int t2 = (t + 1) % P;
            if (nc + 1 == pos(nr, t2)) continue;     // 老虎后动：不能被踩到
            if (nr == n - 1 && nc == 0) { puts("YES"); return 0; }
            int nid = (int)id(nr, nc, t2);
            if (!vis[nid]) { vis[nid] = 1; q.push_back(nid); }
        }
    }
    puts("NO");
    return 0;
}
""",
    explain=[
        ("int P = 2 * (m - 1);",
         "一格宽的行来回一趟需要 2(m-1) 步。所有老虎共用这个周期，所以整个棋盘以它为周期，状态里带 t % P 就够。"),
        ("ph[i] = (d[i] == 'R') ? x : (P - x) % P;",
         "把「位置 + 方向」压成一个相位。验证：m = 5、c = 3、方向 L 时相位 6，t = 1 得 x = 7，超过 4 折回成 2，正是「向左走一格」。"),
        ("return x <= m - 1 ? 1 + x : 2 * m - 1 - x;",
         "三角波映射：前 m 个相位向右走到 m，后 m-2 个相位折回。漏掉折返分支就会让老虎瞬移到列 0。"),
        ("if (nc + 1 == pos(nr, t)) continue;",
         "小猪先动，所以第一步只检查老虎当前（时刻 t）的位置。少了这一句，小猪会直接走进老虎格。"),
        ("if (nc + 1 == pos(nr, t2)) continue;",
         "老虎后动，时刻 t+1 的落点再查一次。只有两次都安全才入队；出口也必须在老虎动完后仍然安全才判 YES。"),
        ("int nid = (int)id(nr, nc, t2);",
         "状态三维编码：格子号 × P + 时刻余数。用 (行,列) 做状态会漏解。"),
    ],
    pitfalls=[
        "把周期写成 m 或者 2m：正确周期是 2(m-1)，m = 2 时写错成 2m 就会把 2 步周期当成 4 步，答案随机偏。",
        "漏掉「前方出界则先掉头再走一格」里的方向反向，只做了位置回弹：位置序列一样，但下一步又会往错的方向走，从第二次折返开始全错（WA，且小样例可能骗过去）。",
        "只查老虎移动后的位置、不查小猪移动前的位置：小猪会走进老虎当前所在格，样例 1 仍输出 NO 但很多数据会错判 YES。",
        "BFS 状态里不带时刻，或者 vis 数组只按 n×m 开：状态数少了 2(m-1) 倍，会漏解；反过来把 vis 开成 n×m×2(m-1) 但编码时忘了乘 P 会越界 RE。",
    ],
))

# ---------------------------------------------------------------- D
PROBLEMS.append(PROB(
    letter="D",
    name="师出同门",
    diff="提高",
    tag="把战斗序列翻译成运输问题，用霍尔条件得到一个 O(n) 判定，再挑第一场",
    statement=[
        "两国各由 n 个宗派组成。玄真国第 i 宗派有 a_i 人，幻月国第 i 宗派有 b_i 人（1 ≤ a_i, b_i ≤ 10^9，n ≤ 10^5，t ≤ 10^4 组测试，所有 n 之和 ≤ 10^5）。",
        "每场战斗：玄真国挑一个还有人的宗派 i，幻月国挑一个还有人的宗派 j。若 i = j，双方不动手，什么也不发生；若 i ≠ j，则 a_i 与 b_j 各减 1，称为一次有效战斗。",
        "问是否存在战斗序列，使得结束后至少一方的所有人阵亡（所有 a_i = 0 或所有 b_i = 0）。若存在，先输出 YES，再输出第一场有效战斗的 i、j（i ≠ j，多解任意）；否则输出 NO。",
    ],
    hint=[
        "非有效战斗什么也不改变，可以无限重复，所以只需考虑 i ≠ j 的战斗；它们才是真正在减人。",
        "把「第 i 宗派要死 a_i 个人」看成 a_i 份需求，「第 j 宗派最多死 b_j 个人」看成容量 b_j，而需求不能送给自己。",
        "什么样的配置会送不出去？先只盯住某一个 i 看：它所有的需求只能由别人的容量承担。",
    ],
    idea=[
        "要灭掉玄真国，就得让每个 i 挨 a_i 刀，共 SA = Σa_i 场有效战斗；每场战斗同时消耗一个 b_j，所以第 j 个宗派最多被消耗 b_j 次。也就是说：把 a_i 份「需求」分给各个 j（i ≠ j），每个 j 收不超过 b_j 份。这就是一个运输问题（源 i 供应 a_i，汇 j 容量 b_j，只缺 i = j 的边），存在解等价于存在这样的分配。",
        "有了分配表就能排出战斗顺序：任一时刻某宗派剩余人数 = 初始值减去已消耗，而总消耗不超过初值，所以随便什么顺序都不会出现「没人可派」。因此分配存在 ⟺ 战斗序列存在。",
        "按霍尔条件（最大流最小割）判可行性：对任意源集合 X，Σ_{i∈X} a_i 不能超过 X 能连到的汇容量和。若 |X| ≥ 2，任取 i∈X 与任一 j，只要 j ≠ i 就有边，所以 X 连到全部汇，条件是 SA ≤ SB。若 X = {i}，连到的汇是除 i 外的全部，条件是 a_i ≤ SB - b_i，即 a_i + b_i ≤ SB。",
        "于是：能灭甲方 ⟺ SA ≤ SB 且 max(a_i + b_i) ≤ SB；能灭乙方 ⟺ SB ≤ SA 且 max(a_i + b_i) ≤ SA。两个都不成立就输出 NO。注意 n = 1 时 a_1 + b_1 必然大于 SB 与 SA，自动判 NO，和样例一致。",
        "输出第一场：注意「SA ≤ SB」在双方各减 1 后仍然成立（同时减 1 不改变大小关系），所以计划不会因为这一刀而改变。设当前计划上限为 lim（灭甲取 SB、灭乙取 SA），开战后要求 max(a_k+b_k) ≤ lim 变成 ≤ lim-1；只有 i、j 两行会减 1，因此所有满足 a_k + b_k = lim 的下标 k 必须都落在 {i, j} 里。这样的下标至多 2 个：0 个则任取 i ≠ j，1 个则让它当 i，2 个则直接取 {i, j}。",
    ],
    code=r"""#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        int n; scanf("%d", &n);
        vector<ll> a(n), b(n);
        ll SA = 0, SB = 0, M = 0;
        for (int i = 0; i < n; i++) { scanf("%lld", &a[i]); SA += a[i]; }
        for (int i = 0; i < n; i++) { scanf("%lld", &b[i]); SB += b[i]; }
        for (int i = 0; i < n; i++) M = max(M, a[i] + b[i]);

        // 灭甲方：SA <= SB 且 max(a_i+b_i) <= SB；灭乙方对称
        bool okA = (SA <= SB) && (M <= SB);
        bool okB = (SB <= SA) && (M <= SA);

        // 在上限 lim 下挑第一场：所有 a_k+b_k == lim 的 k 都必须被 {i,j} 覆盖
        auto pick = [&](ll lim, int &ii, int &jj) -> bool {
            if (n < 2) return false;
            vector<int> z;
            for (int k = 0; k < n; k++) if (a[k] + b[k] == lim) z.push_back(k);
            if (z.size() > 2) return false;              // 一刀只能照顾两行
            if (z.size() == 2) { ii = z[0]; jj = z[1]; return true; }
            if (z.size() == 1) { ii = z[0]; jj = (z[0] == 0 ? 1 : 0); return true; }
            ii = 0; jj = 1; return true;                 // 没人卡在上限，随便打
        };

        int ii = -1, jj = -1;
        bool got = false;
        if (okA) got = pick(SB, ii, jj);
        if (!got && okB) got = pick(SA, ii, jj);         // SA == SB 时两种计划的覆盖条件相同
        if (!got) { puts("NO"); continue; }
        puts("YES");
        printf("%d %d\n", ii + 1, jj + 1);               // 输出 1-indexed
    }
    return 0;
}
""",
    explain=[
        ("bool okA = (SA <= SB) && (M <= SB);",
         "灭甲方的充要条件：总需求不超过总容量，且每个单独的 a_i 不能超过别人的容量和 SB - b_i。少写 M 这一项就是样例 1 的错解。"),
        ("for (int i = 0; i < n; i++) M = max(M, a[i] + b[i]);",
         "把 a_i ≤ SB - b_i 写成 a_i + b_i ≤ SB，只用一个 max 就能判全部 i。"),
        ("if (z.size() > 2) return false;",
         "开战后只有 i、j 两行的 a+b 会减 1，所以卡在上限的下标最多只能有两个，第三个就无法靠这一刀救回来。"),
        ("if (z.size() == 2) { ii = z[0]; jj = z[1]; return true; }",
         "两个下标都卡在上限时，必须让它们分别当 i 和 j，一刀同时降两行；顺带保证 i ≠ j。"),
        ("if (!got && okB) got = pick(SA, ii, jj);",
         "SA == SB 时两种计划的判定条件完全一样，先试甲方计划、不行再试乙方计划，能覆盖所有情况。"),
        ("printf(\"%d %d\\n\", ii + 1, jj + 1);",
         "输入是 1-indexed 的宗派编号，内部用 0-indexed 存，输出要加 1。"),
    ],
    pitfalls=[
        "只判 SA ≤ SB 就输出 YES：漏了 a_i + b_i ≤ SB。样例 1（a = 2, b = 4）会错答 YES，实际只有一个宗派，永远打不出有效战斗。",
        "用 int 存总和：a_i 到 10^9、n 到 10^5，Σa 能到 10^14，必须 long long，否则 WA（溢出后大小关系全乱）。",
        "第一场输出一个已经不剩人的宗派，或者输出 i = j。本解法第一场取的两个下标初始都 ≥ 1 人，但自己写贪心时容易违反这一点，会被判「构造不合法」。",
        "多组测试忘记重置，或者 YES/NO 的大小写、换行格式不对（有解要先单独一行 YES 再一行两个数）。",
    ],
))

# ---------------------------------------------------------------- E
PROBLEMS.append(PROB(
    letter="E",
    name="稳定区间",
    diff="普及-",
    tag="按 mod 3 的三类计数做前缀和，O(1) 回答询问",
    statement=[
        "给定长度 n 的序列 a（1 ≤ n, q ≤ 10^5，1 ≤ a_i ≤ 10^9）和 q 个询问，每个询问给出区间 [l, r]。",
        "问区间内是否存在一个非空子序列（下标递增即可，不要求连续）其元素之和是 3 的倍数。存在则称该区间稳定，输出 Yes，否则输出 No。",
        "输入第一行 n、q，第二行 n 个整数，接下来 q 行每行 l r；对每个询问输出一行。",
    ],
    hint=[
        "子序列不要求连续，所以答案只和区间里「模 3 余 0、余 1、余 2」各有多少个数有关。",
        "只用余数 1 和 2 的数，能凑出 3 的倍数的最小组合有哪几种？把它们列全。",
        "一个余数 0 的数自己就够；如果一个都没有，还能怎么凑？",
    ],
    idea=[
        "只看每个数 mod 3。设区间内余 0、1、2 的个数分别是 c0、c1、c2。",
        "c0 ≥ 1 时直接取那个数，和为 3 的倍数，成立。否则只能用余 1 和余 2 的数凑。1+1+1 = 3，2+2+2 = 6，1+2 = 3，这三种组合都成立；反过来，任何和 ≡ 0 (mod 3) 的非空组合，把 1 和 2 尽量配成对之后，剩下的全是同一种余数，必须凑够三个才能再次被 3 整除。所以判定就是三种组合之一可行。",
        "所以答案 = (c0 ≥ 1) 或 (c1 ≥ 1 且 c2 ≥ 1) 或 (c1 ≥ 3) 或 (c2 ≥ 3)。",
        "对三类余数各做一遍前缀和，每个询问 O(1)。预处理 O(n)、总复杂度 O(n + q)，与 a_i 的大小无关（也不需要真的求和，避免 10^9 × 10^5 溢出）。",
    ],
    code=r"""#include <bits/stdc++.h>
using namespace std;

int main() {
    int n, q;
    if (scanf("%d %d", &n, &q) != 2) return 0;
    vector<array<int, 3>> pre(n + 1);      // pre[i][r] = 前 i 个数里余 r 的个数
    pre[0] = {0, 0, 0};
    for (int i = 1; i <= n; i++) {
        int x; scanf("%d", &x);
        pre[i] = pre[i - 1];
        pre[i][x % 3]++;
    }
    while (q--) {
        int l, r; scanf("%d %d", &l, &r);
        int c0 = pre[r][0] - pre[l - 1][0];
        int c1 = pre[r][1] - pre[l - 1][1];
        int c2 = pre[r][2] - pre[l - 1][2];
        bool ok = c0 >= 1 || (c1 >= 1 && c2 >= 1) || c1 >= 3 || c2 >= 3;
        puts(ok ? "Yes" : "No");
    }
    return 0;
}
""",
    explain=[
        ("pre[i][x % 3]++;",
         "只保留余数信息：原值多大都不影响答案，这一步同时避免了区间求和溢出。"),
        ("vector<array<int, 3>> pre(n + 1);",
         "三类余数各一份前缀和，任取区间相减就是 O(1)；n ≤ 10^5 时总数也不超过 int 范围。"),
        ("bool ok = c0 >= 1 || (c1 >= 1 && c2 >= 1) || c1 >= 3 || c2 >= 3;",
         "四类可行组合：单个 3 的倍数、一个 1 加一个 2、三个 1、三个 2。四者缺一就会漏解。"),
        ("puts(ok ? \"Yes\" : \"No\");",
         "按题面要求的 Yes/No 输出；大小写不敏感但拼写不能错。"),
    ],
    pitfalls=[
        "只判「存在某个数是 3 的倍数」：漏掉 1+2 与三个同余数的组合，样例第二个询问就会错。",
        "只判 c1 ≥ 3 或 c2 ≥ 3：漏掉 1+2，整道题基本全错。",
        "真去算区间和再模 3：区间和能到 10^14，用 int 溢出后结论随机；本题只需要余数计数，根本不用原值。",
        "想把那组子序列真的找出来（背包、枚举）：n 到 10^5、a_i 到 10^9，做不了；这题只要判存在性，而存在性只由三类余数的个数决定。",
    ],
))

# ---------------------------------------------------------------- F
PROBLEMS.append(PROB(
    letter="F",
    name="【模板】Pollard-Rho",
    diff="提高",
    tag="交互协议 + Pollard-Rho；查询本质是拿 popcount 逐位定位",
    difficulty_note="难度定位：省选 / 提高+ 的拓展题。它把「交互题怎么写」和「大整数分解」捆在一起，新生赛阶段不会做完全正常；下面给出完整的 Pollard-Rho 模板，读完能直接当黑箱用。",
    statement=[
        "这是一道交互题。输入一个整数 n（2 ≤ n ≤ 2^60 - 1），你要输出它的最大质因子 p。",
        "你最多有 64 次尝试。每次尝试输出一行一个整数 m（0 ≤ m ≤ 2^63 - 1），交互器计算 d = p ⊕ m（按位异或），然后输出 popcount(d)，即 d 的二进制里 1 的个数。当交互器输出 0 时说明 m = p，你应立即结束程序。",
        "每次输出后必须刷新缓冲区：C++ 用 fflush(stdout) 或 std::endl。尝试次数达到 64 次也会被强制终止。",
    ],
    hint=[
        "交互器只回给你一个数：你的猜测和答案在二进制上差了多少位。想清楚「差多少位」怎么变成某个具体 bit 的取值。",
        "先输出 m = 0 能得到什么？再输出 m = 2^i，popcount 会怎么变？",
        "p 最多 60 个 bit，这个信息量够用；另外别忘了 n 本身不超过 2^60，直接把 n 分解掉也能一次命中。",
    ],
    idea=[
        "思路一（交互派）：逐位确定。先输出 m = 0，得到 c = popcount(p)。之后每次输出 m = 2^i，若 p 的第 i 位是 0，则 d 比 p 多一个 1，回复 c+1；若是 1，则回复 c-1。一次查询换来一个 bit，候选集合每次都缩小一半。p 有 60 个 bit：1 次求 c、59 次定下第 0..58 位，第 59 位由 c 减去已知的 1 的个数直接算出，最后输出 p 收 0，共 1+59+1 = 61 次，小于 64。",
        "思路二（分解派，也是代码走的路）：n ≤ 2^60，直接做质因数分解就能拿到最大质因子，第一次尝试输出 m = p 就立刻收到 0，只用 1 次机会。题目叫「模板」就是在提示这条路，提示说明里也写了「只需要写一个高效率的质因数分解算法」。",
        "分解的两个部件：Miller-Rabin 判素（用前 12 个质数当底，对 2^60 以内的数完全确定，不会误判），以及 Pollard-Rho 找因子（随机 c 与起点，用 Floyd 判圈在 O(n^{1/4}) 期望步数内找到非平凡因子）。n 不超过 2^60 时最坏是「两个 30 位质数相乘」，需要约 3×10^4 次迭代，而每次迭代是几次 128 位取模乘法，非常快。",
        "递归分解：n 是质数就更新答案；否则找到一个因子 d，递归处理 d 与 n/d。注意每层都要判素，因为 Pollard-Rho 只能保证返回一个非平凡因子（可能还是合数）。",
        "交互侧只需三步：读 n、分解、输出 p 并 fflush，然后读掉那行 0 再退出。千万不要在收到 0 之后继续输出，会被判协议错误。",
    ],
    code=r"""#include <bits/stdc++.h>
using namespace std;
typedef unsigned long long ull;
typedef __int128 lll;

mt19937_64 rng(chrono::steady_clock::now().time_since_epoch().count());

ull mulmod(ull a, ull b, ull m) { return (ull)((lll)a * b % m); }   // 防溢出

ull powmod(ull a, ull e, ull m) {
    ull r = 1 % m;
    a %= m;
    while (e) {
        if (e & 1) r = mulmod(r, a, m);
        a = mulmod(a, a, m);
        e >>= 1;
    }
    return r;
}

// 前 12 个质数作底，对 n < 3.3e24 都是确定的，2^60 内绝不会误判
bool isPrime(ull n) {
    if (n < 2) return false;
    for (ull p : {2ULL, 3ULL, 5ULL, 7ULL, 11ULL, 13ULL, 17ULL, 19ULL, 23ULL, 29ULL, 31ULL, 37ULL})
        if (n % p == 0) return n == p;
    ull d = n - 1;
    int s = 0;
    while (!(d & 1)) { d >>= 1; s++; }
    for (ull a : {2ULL, 3ULL, 5ULL, 7ULL, 11ULL, 13ULL, 17ULL, 19ULL, 23ULL, 29ULL, 31ULL, 37ULL}) {
        ull x = powmod(a, d, n);
        if (x == 1 || x == n - 1) continue;
        bool comp = true;
        for (int r = 1; r < s; r++) {
            x = mulmod(x, x, n);
            if (x == n - 1) { comp = false; break; }
        }
        if (comp) return false;
    }
    return true;
}

// Floyd 判圈版 Pollard-Rho：找到 n 的一个非平凡因子（n 为合数时）
ull pollard(ull n) {
    if (n % 2 == 0) return 2;
    while (true) {
        ull c = rng() % (n - 1) + 1;
        ull x = rng() % (n - 2) + 2, y = x, d = 1;
        auto f = [&](ull v) { return (mulmod(v, v, n) + c) % n; };
        while (d == 1) {
            x = f(x);                       // 一步一步
            y = f(f(y));                    // 两步，相遇即出环
            d = __gcd(x > y ? x - y : y - x, n);
        }
        if (d != n) return d;               // d == n 说明这一轮退化，换 c 重来
    }
}

ull best = 1;                               // 最大质因子

void factor(ull n) {
    if (n < 2) return;
    if (isPrime(n)) { best = max(best, n); return; }
    ull d = pollard(n);
    factor(d);
    factor(n / d);
}

int main() {
    ull n;
    if (scanf("%llu", &n) != 1) return 0;
    factor(n);
    printf("%llu\n", best);                 // 第一次尝试就报出 p
    fflush(stdout);                         // 交互题必须刷新
    int c = 0;
    if (scanf("%d", &c) == 1) { /* 这里收到 0，代表猜对了 */ }
    return 0;
}
""",
    explain=[
        ("ull mulmod(ull a, ull b, ull m) { return (ull)((lll)a * b % m); }",
         "a×b 可能到 2^120，必须用 __int128 中转，否则溢出后分解必然出错。"),
        ("for (ull p : {2, 3, 5, ..., 37}) if (n % p == 0) return n == p;",
         "先用小质数筛掉，既加快速度，也避免 Miller-Rabin 里 a % n == 0 的退化情形。"),
        ("while (!(d & 1)) { d >>= 1; s++; }",
         "把 n-1 写成 d·2^s，这是 Miller-Rabin 的标准准备步骤。"),
        ("if (d != n) return d;",
         "Pollard-Rho 只保证给出非平凡因子；d == n 表示这一轮把 n 自己圈住了，必须换随机 c 重来。"),
        ("if (isPrime(n)) { best = max(best, n); return; }",
         "递归边界：只剩质数时更新答案。合数继续拆，所以最终 best 一定是最大质因子。"),
        ("fflush(stdout);",
         "交互题的生命线。不刷新的话交互器读不到你的输出，表现是 TLE 或 Idle。"),
    ],
    pitfalls=[
        "输出后不刷新缓冲区：交互器收不到数字，直接判超时（表现为 TLE / Idle 而不是 WA）。",
        "用 unsigned long long 直接乘：a×b 溢出，Miller-Rabin 与 Pollard-Rho 全部失效，答案是随机的（WA）。",
        "Miller-Rabin 只取 {2,3,5,7} 作底：2^60 范围内存在强伪素数，会把合数判成质数，于是 best 取到一个合数（WA）。",
        "协议与边界：输出 p 之后应读掉那行 0 就结束，别再输出；同时 factor 必须先判素再拆——n 是质数（或 n = 2）时直接 pollard 会死循环，表现是 TLE。",
    ],
))

# ---------------------------------------------------------------- G
PROBLEMS.append(PROB(
    letter="G",
    name="互异排列扩展",
    diff="普及+",
    tag="n+1 ≡ 0 决定了插入位置只能是开头，剩下只需判重",
    statement=[
        "给定一个 1 到 n 的排列 p（n ≤ 10^6，T ≤ 1000，所有 n 之和 ≤ 10^6）。把小 H 的数字 n+1 插入 p 的某个位置（含开头、结尾），得到长度 n+1 的排列 q。",
        "记 S_k = (q_1 + q_2 + ... + q_k) mod (n+1)，要求 S_1, S_2, ..., S_{n+1} 这 n+1 个值互不相同。",
        "有解则输出任意一个可行的 q（一行 n+1 个整数），无解输出 -1。",
    ],
    hint=[
        "n+1 对 n+1 取模等于 0，它对前缀和的贡献是什么？",
        "若把 n+1 插在第 k 个位置之后（k ≥ 1），那么 S_k 和 S_{k+1} 分别等于多少？比较一下。",
        "插入位置被唯一确定之后，剩下的检查只有一件事，想想要不要额外排除某个余数。",
    ],
    idea=[
        "n+1 ≡ 0 (mod n+1)，所以它的前缀和不会改变当前余数。若把它插在 p_1..p_k 之后（k ≥ 1），则 S_{k+1} = S_k，两个值相等，立即不合法。",
        "因此插入位置只能是开头：q = (n+1, p_1, p_2, ..., p_n)。此时 S_1 = n+1 ≡ 0，而 k ≥ 2 时 S_k 就是 p 的前 k-1 个前缀和 mod (n+1)。",
        "于是条件变成：p 的 n 个前缀和 mod (n+1) 两两不同，而且都不能等于 0（0 已经被 S_1 占了）。n+1 个余数正好 0..n，所以这 n 个值必须恰好是 1..n。",
        "扫一遍 p、用桶判重（同时把 0 预标记为已用）即可，O(n)。注意多组测试要按 n+1 的大小开桶，不要每组都 memset 一个 10^6 的数组。",
    ],
    code=r"""#include <bits/stdc++.h>
using namespace std;

int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        int n; scanf("%d", &n);
        vector<int> p(n + 1);
        for (int i = 1; i <= n; i++) scanf("%d", &p[i]);

        int m = n + 1;                       // n+1 ≡ 0，插在中间会让相邻两个前缀和相等
        vector<char> seen(m, 0);
        seen[0] = 1;                         // S_1 = 0 已经占用了余数 0
        long long s = 0;
        bool ok = true;
        for (int i = 1; i <= n; i++) {
            s = (s + p[i]) % m;
            if (seen[s]) { ok = false; break; }
            seen[s] = 1;
        }
        if (!ok) { puts("-1"); continue; }
        printf("%d", m);
        for (int i = 1; i <= n; i++) printf(" %d", p[i]);
        puts("");
    }
    return 0;
}
""",
    explain=[
        ("int m = n + 1;",
         "取模对象。后面所有余数都在 0..m-1 内。"),
        ("seen[0] = 1;",
         "S_1 = n+1 ≡ 0，所以前缀和不许再出现 0。这一句同时替代了「不能等于 0」的单独判断。"),
        ("s = (s + p[i]) % m;",
         "边读边累加前缀和，O(n) 完成，不需要存中间结果。"),
        ("if (seen[s]) { ok = false; break; }",
         "一旦余数重复（含重复的 0）就必然无解，可以立即跳出，但仍要把本组输入读完——这里已经读完了。"),
        ("vector<char> seen(m, 0);",
         "按 m 开桶，而不是每组都清空一个固定 10^6 的数组，避免 T = 1000 时 O(T·10^6) 的假 TLE。"),
    ],
    pitfalls=[
        "只判「前缀和两两不同」，忘了余数 0 已被 S_1 占用：例如 p 的某个前缀和正好是 n+1，判重检查通过但实际不合法（WA）。",
        "以为插在别的空位也可能成立：n+1 ≡ 0 必然造成相邻两个前缀和相等，这一步想错会导致答案全错。",
        "多组测试用 memset 清 10^6 的桶：T = 1000 时是 10^9 次写，TLE。",
        "输出 -1 之后还多输出东西，或 q 只输出了 p 忘了前面的 n+1。",
    ],
))

# ---------------------------------------------------------------- H
PROBLEMS.append(PROB(
    letter="H",
    name="互异排列生成",
    diff="提高-",
    tag="先由总和模 n+1 定出 n 必须是奇数，再用 Walecki 序列的差分构造",
    statement=[
        "接上一题：对给定的 n（n ≤ 10^6，T ≤ 1000，所有 n 之和 ≤ 10^6），判断是否存在 1..n 的排列 p，使得把 n+1 插入 p 之后能得到「前缀和模 n+1 互异」的排列 q。",
        "若存在，输出任意一个可行的 p（一行 n 个整数）；若不存在输出 -1。",
    ],
    hint=[
        "先回忆上一题的结论：n+1 只能插在开头，所以对 p 的要求是什么？",
        "p 的 n 个前缀和必须恰好占满 n+1 个余数里除 0 之外的全部，那么它们的总和 mod n+1 必须是多少？由此能得到 n 的奇偶限制。",
        "构造时可以让前缀和一半取 1,2,3,...，另一半取 m-1,m-2,...，然后反推出排列的每一项（差分）。",
    ],
    idea=[
        "由上一题：只有把 n+1 放在开头才可能合法，等价条件是 p 的 n 个前缀和 mod m（m = n+1）两两不同且都不为 0。n 个互不相同的非零余数正好占满 1..m-1，于是最后一个前缀和 = 1+2+...+n = n(n+1)/2 必须不等于 0 mod m。",
        "若 m 是奇数，(m-1)/2 是整数，n(n+1)/2 = m(m-1)/2 ≡ 0 (mod m)，矛盾。所以 m 必须偶数，即 n 必须奇数；n 为偶数时直接输出 -1。这也解释了样例里 n = 2 输出 -1。",
        "n 为奇数（m 偶数）时给出构造。取 p = (m-1, 2, m-3, 4, m-5, 6, ..., 1)，也就是奇数位依次放 m-1, m-3, ..., 1，偶数位依次放 2, 4, ..., m-2。",
        "验证：设 p 的第 2i 项是 2i，第 2i-1 项是 m-(2i-1)。则第 2i 个前缀和 = i·m + i ≡ i，第 2i-1 个前缀和 = i·m - i ≡ m-i。于是前缀和集合是 {1,...,m/2-1} ∪ {m/2,...,m-1} = 1..m-1，全部非零、全部互异，正好满足要求。",
        "复杂度 O(n)（每个数只输出一次），比「搜索构造」靠谱得多；而且这组 p 直接可以作为上一题的输入，两题互相对拍很合适。",
    ],
    code=r"""#include <bits/stdc++.h>
using namespace std;

int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        int n; scanf("%d", &n);
        if (n % 2 == 0) { puts("-1"); continue; }   // m 为奇数时总和必为 0 mod m，无解
        int m = n + 1;                              // 偶数
        // p = (m-1, 2, m-3, 4, ..., 1)：差分出的前缀和覆盖 1..m-1
        vector<int> p(n);
        int odd = m - 1, even = 2;
        for (int i = 0; i < n; i++) {
            if (i % 2 == 0) { p[i] = odd; odd -= 2; }
            else { p[i] = even; even += 2; }
        }
        for (int i = 0; i < n; i++) printf("%d%c", p[i], i + 1 == n ? '\n' : ' ');
    }
    return 0;
}
""",
    explain=[
        ("if (n % 2 == 0) { puts(\"-1\"); continue; }",
         "m = n+1 为奇数时，所有元素之和 ≡ 0 (mod m)，最后一个前缀和必然是 0，与「非零」矛盾，所以偶数 n 无解。"),
        ("int odd = m - 1, even = 2;",
         "构造的两个指针：奇数位置从 m-1 开始往下减 2，偶数位置从 2 开始往上加 2。"),
        ("if (i % 2 == 0) { p[i] = odd; odd -= 2; }",
         "生成 m-1, m-3, ..., 1。它与下一项配对后差分出的前缀和正好是 m-i 与 i 交替。"),
        ("else { p[i] = even; even += 2; }",
         "生成 2, 4, ..., m-2。这样 1..n 每个数恰好出现一次，p 是合法排列。"),
        ("printf(\"%d%c\", p[i], i + 1 == n ? '\\n' : ' ');",
         "按题面要求输出一行 n 个整数，行末不能多空格。"),
    ],
    pitfalls=[
        "以为 n 偶数也可能有解：n = 2 时三个前缀和只能落在 {0,1,2}，永远撞；本质是总和必为 0。",
        "把奇数位与偶数位的取值搞反（奇数位放 2,4,...，偶数位放 m-1,m-3,...）：会输出到 m 这个非法值，同时前缀和也会重复。",
        "直接输出升序 1..n：n = 5 时前三个前缀和是 1, 3, 6 ≡ 0，立刻不合法。",
        "用搜索/回溯造排列：总和到 10^6，最坏情况根本搜不出来，TLE。",
    ],
))

# ---------------------------------------------------------------- I
PROBLEMS.append(PROB(
    letter="I",
    name="2-冲突数对",
    diff="入门",
    tag="总数对减去同值数对，注意答案要用 long long",
    statement=[
        "给定长度 n 的数组 a（1 ≤ n ≤ 10^5，1 ≤ a_i ≤ 10^5）。",
        "统计满足 1 ≤ i ≤ j ≤ n 且 a_i ≠ a_j 的下标对 (i, j) 的个数（i = j 会被 a_i ≠ a_j 排除，所以等价于 i 小于 j）；两个数对不同当且仅当 i 或 j 不同。",
        "输出一个整数。样例：n = 3、a = 1 1 2 时答案是 2；n = 5、a = 1 2 3 2 1 时答案是 8。",
    ],
    hint=[
        "所有下标对一共多少个？把不满足 a_i ≠ a_j 的那些减掉就行。",
        "同值对只和每个值出现了多少次有关。",
        "n = 10^5 时答案大约多大？int 够吗？",
    ],
    idea=[
        "全部下标对是 C(n,2) = n(n-1)/2 个，需要去掉 a_i = a_j 的。",
        "对每个值 v，若出现 cnt[v] 次，则它内部贡献 C(cnt_v,2) = cnt_v(cnt_v-1)/2 个同值对。答案是 C(n,2) 减去所有值的 C(cnt_v,2)。",
        "用桶统计 cnt，O(n + V) 一遍扫完，V 是值域 10^5。n = 10^5 时 C(n,2) ≈ 5×10^9，超出 int，必须用 long long。",
    ],
    code=r"""#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    const int V = 100000;
    vector<long long> cnt(V + 1, 0);
    for (int i = 0; i < n; i++) {
        int x; scanf("%d", &x);
        cnt[x]++;
    }
    long long ans = (long long)n * (n - 1) / 2;      // 全部有序对
    for (int v = 1; v <= V; v++) ans -= cnt[v] * (cnt[v] - 1) / 2;   // 减掉同值对
    printf("%lld\n", ans);
    return 0;
}
""",
    explain=[
        ("long long ans = (long long)n * (n - 1) / 2;",
         "n = 10^5 时约 5×10^9，int 会溢出，先转 long long 再乘。"),
        ("vector<long long> cnt(V + 1, 0);",
         "值域只有 10^5，桶数组直接开满，省掉排序或 map 的 log。"),
        ("ans -= cnt[v] * (cnt[v] - 1) / 2;",
         "同值对的个数只看出现次数：cnt 个下标任取两个，都在同一个值里，都要减掉。"),
        ("printf(\"%lld\\n\", ans);",
         "long long 用 %lld 输出，用 %d 会打印垃圾值。"),
    ],
    pitfalls=[
        "用 int 存答案：n = 10^5 时约 5×10^9 溢出，输出负数（WA）。",
        "写成 O(n^2) 枚举所有对：n = 10^5 时 10^10 次，必定 TLE。",
        "把同值对按 (i,j)、(j,i) 数成两倍：C(cnt,2) 已经是无序对，对应到有序只是 i ≤ j 的那一半，不要重复减。",
        "cnt 用 int 但 cnt*(cnt-1) 先溢出：cnt 到 1e5 时乘积到 1e10，建议 cnt 直接开 long long。",
    ],
))

# ---------------------------------------------------------------- J
PROBLEMS.append(PROB(
    letter="J",
    name="收藏宝石",
    diff="普及+",
    tag="合法性等价于剩余集合始终连通，倒过来按价值从小到大加点的 BFS",
    statement=[
        "n 个宝石编号 1..n，房梁编号 0。m 条绳索把节点两两相连（无重边、无自环），保证每个宝石都能连到房梁。每个宝石有价值 a_i（1 ≤ a_i ≤ k ≤ 10^5，n, m ≤ 10^5）。",
        "使用一个宝石的操作是：选定它，切断所有与它相连的绳索。若这次操作恰好只让一个宝石失去与房梁的连接（也就是它自己掉下来），则操作合法，该宝石被取下；它上面的绳索一并消失。",
        "问是否存在一种取下顺序，使得每一步取下的都是「当前剩余宝石中价值最大的之一」。输出 YES 或 NO（大小写随意）。",
    ],
    hint=[
        "先想清楚「合法」到底等价于什么：切掉 v 的所有绳索之后，除了 v 之外的宝石还能不能全部连到房梁？",
        "把顺序倒过来看：从只剩房梁开始，每次加入一个宝石。加入时对连通性提什么要求？价值又变成什么顺序？",
        "同价值的宝石之间可以任意排序，所以它们可能互相解锁——一组同价值的点要怎么一起处理？",
    ],
    idea=[
        "合法性其实是连通性条件。切掉 v 的全部绳索后，v 必然与房梁断开（其它宝石不能再断），所以操作合法 ⟺ 取走 v 之后，剩下的宝石仍然全部连到房梁。于是整个问题要求：每一步之后，剩余集合（加上房梁 0）都是连通的。",
        "把顺序反过来：从集合 {0} 开始，按逆序把宝石一个个加回去。逆序里每次加入 v 时，剩下的是已经加进去的那些，所以要求恰好是「v 在已加入集合里有邻居」——加一个和当前集合相邻的点，连通性自动保持。这样做也把「割点」这类棘手判断完全绕开了。",
        "正序要求每一步取的都是当前最大值，反过来就是要求加入顺序的价值不降。于是：所有宝石按价值升序处理，同价值的为一组；组内可以任意排序，因此只要组内某些点已经和已加入集合相邻，就可以先加它，再由它解锁同组别的点——也就是在组内做一次 BFS 扩散。",
        "具体做法：排序后按价值分组；处理一组时，先把所有「已经与已加入集合相邻」的组内点入队，然后 BFS：出队即标记已加入，并把它在组内的邻居入队。整组扩散结束后若还有人没被加入，说明这个价值没法整体接上，答案 NO。",
        "注意「只能取叶子」只是树上的特例。有环时，环上的点取走后其余部分仍连通，同样合法——样例 1 是个三角形，两个点都不是叶子却都能取，套「只取叶子」会直接错。",
        "复杂度：排序 O(n log n)，BFS 每个点、每条边各走一次，总 O((n + m) log n)。",
    ],
    code=r"""#include <bits/stdc++.h>
using namespace std;

int main() {
    int n, m, k;
    if (scanf("%d %d %d", &n, &m, &k) != 3) return 0;
    vector<int> a(n + 1);
    for (int i = 1; i <= n; i++) scanf("%d", &a[i]);
    vector<vector<int>> g(n + 1);
    for (int i = 0; i < m; i++) {
        int x, y; scanf("%d %d", &x, &y);
        g[x].push_back(y);
        g[y].push_back(x);
    }

    vector<int> ord(n);
    for (int i = 0; i < n; i++) ord[i] = i + 1;
    sort(ord.begin(), ord.end(), [&](int x, int y) { return a[x] < a[y]; });   // 逆序 = 价值升序

    vector<char> added(n + 1, 0), inq(n + 1, 0), ing(n + 1, 0);
    added[0] = 1;                       // 房梁一开始就在集合里
    bool ok = true;
    int i = 0;
    while (i < n && ok) {
        int j = i;
        while (j < n && a[ord[j]] == a[ord[i]]) j++;         // 同价值一组
        for (int t = i; t < j; t++) ing[ord[t]] = 1;
        vector<int> q;
        for (int t = i; t < j; t++) {
            int v = ord[t];
            for (int w : g[v]) if (added[w]) { q.push_back(v); inq[v] = 1; break; }
        }
        for (size_t h = 0; h < q.size(); h++) {              // 组内扩散
            int v = q[h];
            added[v] = 1;
            for (int w : g[v]) if (ing[w] && !added[w] && !inq[w]) { inq[w] = 1; q.push_back(w); }
        }
        for (int t = i; t < j; t++) if (!added[ord[t]]) ok = false;   // 有人接不上
        for (int t = i; t < j; t++) ing[ord[t]] = 0;
        i = j;
    }
    puts(ok ? "YES" : "NO");
    return 0;
}
""",
    explain=[
        ("vector<char> added(n + 1, 0), inq(n + 1, 0), ing(n + 1, 0);",
         "added：已加回集合（含房梁 0）；inq：本组内已入队；ing：本组成员标记，避免每组都清空 n 大小的数组。"),
        ("added[0] = 1;",
         "房梁视为一开始就在集合里，于是「与房梁直接相连」的宝石在第一步就能加入。漏了这一句会让所有宝石都加不进来，全部输出 NO。"),
        ("sort(ord.begin(), ord.end(), [&](int x, int y) { return a[x] < a[y]; });",
         "倒着看以后价值必须不降，所以按价值升序排序；同价值的点相对顺序任意。"),
        ("for (int t = i; t < j; t++) ing[ord[t]] = 1;",
         "只标记当前这一组，BFS 扩散时限定组内，避免同价值以外的点被提前加入。"),
        ("for (int w : g[v]) if (added[w]) { q.push_back(v); inq[v] = 1; break; }",
         "组内种子：已经和已加入集合相邻的点。一个点只要有一个已加入邻居就够了。"),
        ("for (int w : g[v]) if (ing[w] && !added[w] && !inq[w]) { inq[w] = 1; q.push_back(w); }",
         "组内 BFS：加入 v 之后，同组邻居也被解锁。没有 inq 标记会重复入队，队列规模退化。"),
        ("for (int t = i; t < j; t++) if (!added[ord[t]]) ok = false;",
         "整组扩散完还有人没加入，说明这一档价值出现了「接不上」的断点，答案就是 NO。"),
    ],
    pitfalls=[
        "套用「只有叶子能取」：样例 1 是三角形，两个宝石都不是叶子却都合法，按叶子判会输出 NO（正确答案 YES）。",
        "只做一次全局 BFS 而不按价值分组：同价值的点本来可以互相解锁，不分组的做法会把它们误判成接不上（WA）。",
        "把「恰好一个宝石失去连接」理解成「切掉 v 就行，别的宝石断不断无所谓」：那会允许砍掉整棵子树，样例 2 会错答 YES。",
        "组内扩散没有 inq 标记，同一个点被反复入队，入队次数从 O(n + m) 退化成 O(deg^2)，大数据 TLE。",
    ],
))

DOCS = [DOC(
    title="2025 广工新生赛（初赛）题解",
    file="sol-xinsheng.html",
    desc="10 题全解：从字符串贪心到树上的取值顺序",
    source="2025 年广东工业大学 ACM 新生程序设计竞赛（初赛）",
    level="入门 ~ 提高",
    sections=[
        P("这份题解的用法：先自己看题意，再看「引导性提示」，卡住 20 分钟再点开思路与代码。"),
        P("难度：I 入门；E 普及-；C、G、J 普及+；A、H 提高-；D、F 提高（F 实际是省选向的模板拓展）。"
          "考场上 I、E 十分钟内该出；C、J 想清「状态里带什么」就没了；A、G、H 的关键是先把不变量写出来；"
          "D 想到运输问题就结束；F 会 Pollard-Rho 就是送分，不会就先跳过。"),
        NOTE("tip", "复盘建议", [
            "A：把「匹配删除」写成 (q, i) 的链，再想想为什么可以把长度压成 k, k-1, ..., 1。",
            "C：老虎位置是时间的三角波，周期 2(m-1)。会写这个函数，BFS 就是模板。",
            "D：先把战斗序列翻译成「需求 − 容量」的分配，再用霍尔条件判一眼。",
            "J：正着看是「割点」，倒着看只是「新点必须有已加入的邻居」。换个方向，整题难度就掉下来了。",
        ]),
    ],
    problems=PROBLEMS,
    skip=["B 我不是AI：只要求判断一行输入是否严格等于 Are you AI，属于读入练习（入门），略去。"],
)]
