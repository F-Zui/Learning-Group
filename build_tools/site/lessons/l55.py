# -*- coding: utf-8 -*-
"""第 55 节 · 回顾九：数据结构与字符串"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dsl import *  # noqa

SEC = []

SEC.append(P("第 46~54 节一共给了 8 类工具，看着互不相干，其实都在做同一个替换："
             "<b>把「每次重扫一遍」换成「只碰 O(log n) 个位置或 O(1) 个位置」</b>。"
             "树状数组把前缀和切成 log n 段；线段树把区间摊成二叉树，用懒标记把整段操作压成一个数；"
             "单调队列把「永远不会再成为答案」的元素直接扔掉；Trie 把公共前缀合成一条链；"
             "KMP 把「已经匹配上的那一段」记成 nxt 不重算；ST 表用倍增把区间最值压成两次查表；"
             "匈牙利把「请你换一个」写成一次 dfs。"))

SEC.append(Q("判断标准只有一句：如果暴力里有一处「把这一段重新扫一遍」，就有一个 O(log n) 或 O(1) 的结构在等你。"))

SEC.append(T(["节", "工具", "看到这些字就上它", "一次操作"], [
    ["46", "树状数组", "「单点改 + 前缀和」「逆序对」「值域上数个数」", "O(log n)"],
    ["47", "线段树 + 懒标记", "「区间加 / 区间赋值」配「区间求和 / 区间最值」", "O(log n)"],
    ["48", "单调栈 / 单调队列", "「左边第一个更大的」「窗口最值，且窗口只往右滑」", "O(n)"],
    ["49", "堆 / 对顶堆", "「每次取最小」「动态中位数」「k 路归并取前 k 小」", "O(log n)"],
    ["51", "字符串哈希 / Trie", "「两个子串是否相等」「前缀查询」「单词出现过没有」", "O(1) / O(L)"],
    ["52", "KMP", "「模式串在主串里的出现位置」「最长 border」", "O(n + m)"],
    ["53", "倍增 / ST 表", "「静态区间最值」「第 2^k 级祖先」「LCA」", "O(1) / O(log n)"],
    ["54", "二分图 / 匈牙利", "「两两配对」「冲突分两组」「最大匹配」", "O(VE)"],
]))

SEC.append(P("第 50 节是模拟赛，P1886 滑动窗口与 P1908 逆序对已经在里面考过一次。"
             "这一节换 P1440 和 P1168 练单调队列与堆，另外三道覆盖 Trie、KMP、二分图。"
             "先把 P1908 完整写一遍——它同时用上离散化和树状数组，是 46 节所有套路的汇合点。"))

# ---------------------------------------------------------------- 完整例题
SEC.append(EX("逆序对", "P1908", "普及/提高-", "https://www.luogu.com.cn/problem/P1908",
              ["给定一段正整数序列 a，若 i &lt; j 且 a[i] &gt; a[j]，则称 (i, j) 是一个逆序对。求逆序对总数。",
               "输入格式：第一行一个整数 n（1 ≤ n ≤ 5×10⁵）；第二行 n 个整数 a[i]（1 ≤ a[i] ≤ 10⁹）。",
               "输出格式：一行一个整数，表示逆序对总数。"],
              sample="输入：\n6\n5 4 2 6 3 1\n\n输出：\n11"))

SEC.append(P("题意换个说法：每一对逆序对都唯一对应一个「右边比左边小」的关系。固定左边的数 a[i]，"
             "它贡献的个数就是「i 右边严格小于 a[i] 的数的个数」。于是题目变成 n 次提问："
             "<b>在值域上问「比 x 小的数已经出现了几个」</b>。值域开桶、单点加、前缀查询——三句话正好是树状数组。"))

SEC.append(P("先把三块骨头拆开：<b>lowbit</b> 决定管辖长度，<b>add / query</b> 决定怎么跳下标，"
             "<b>离散化</b> 把 10⁹ 的值域压到 1..m（m ≤ n）。"))

SEC.append(FN(
    "lowbit（取最低位的 1）",
    "int lowbit(int x) { return x & -x; }",
    [("x &amp; -x", "取 x 二进制里最低位的那个 1，连同它后面的 0，返回一个 2 的幂。"),
     ("为什么成立", "补码下 −x = ~x + 1。取反把最低位的 1 变 0、后面的 0 全变 1，再加 1 全部进位回去，高位互相抵消，只剩那一位。"),
     ("算几个", "lowbit(6) = 2（110 → 10）；lowbit(8) = 8（1000 → 1000）；lowbit(7) = 1。"),
     ("在树状数组里", "t[x] 管的区间长度恰好是 lowbit(x)，管辖范围是 (x − lowbit(x), x]。"),
     ("x = 0 时", "lowbit(0) = 0。下标一旦从 0 开始，add 里 p += 0 永不前进 → 死循环 TLE。")],
    example=r'''for (int x = 1; x <= 8; ++x)
    printf("%d ", x & -x);        // 1 2 1 4 1 2 1 8''',
    notes=["对 int 与 long long 都成立，因为补码规则一样。",
           "树状数组的下标恒从 1 开始；题目给 0-based 就整体 +1。"],
    brief="取最低位的 1，树状数组靠它算管辖长度"))

SEC.append(FN(
    "树状数组（单点加 + 前缀和）",
    "void add(int p, int v);\nint query(int p);",
    [("add(p, v)", "a[p] += v。沿 p → p + lowbit(p) 一路上跳，改掉每个管到 p 的 t，最多 log n 步。"),
     ("query(p)", "返回 a[1..p] 的和。沿 p → p − lowbit(p) 一路下跳，把覆盖到的 t 累加。"),
     ("区间和", "sum(l, r) = query(r) − query(l − 1)。树状数组只会求前缀，区间一律靠相减。"),
     ("循环上界", "add 写 p &lt;= n；值域压缩过时写 p &lt;= m（m 为不同值个数），写 n 也不会错，只是多跑空位。"),
     ("t 不是原数组", "t 是「若干段区间和」的堆叠，读 t[i] 得不到 a[i]。"),
     ("复杂度", "n = 5×10⁵ 时 log₂n ≈ 19，一次操作最多 19 次加法。")],
    example=r'''int t[N], n;
void add(int p, int v) { for (; p <= n; p += p & -p) t[p] += v; }
int query(int p) { int s = 0; for (; p > 0; p -= p & -p) s += t[p]; return s; }

add(3, 5); add(5, -2);
printf("%d\n", query(5) - query(2));    // a[3..5] 的和 = 3''',
    notes=["多组数据在每组开头 memset(t, 0, sizeof t)，否则第二组开始全错。",
           "树状数组不能求区间最值：query 靠相减，max 没有逆运算。要最值就换线段树或 ST 表。"],
    brief="单点改、前缀查，都是 O(log n)，12 行代码用三种下标含义"))

SEC.append(FN(
    "离散化：sort + unique + lower_bound",
    "sort(b + 1, b + n + 1);\nm = unique(b + 1, b + n + 1) - b - 1;\nrk[i] = lower_bound(b + 1, b + m + 1, a[i]) - b;",
    [("sort", "先排序。不排序就 unique，去重无效、名次整体错位 → WA。"),
     ("unique(first, last)", "把相邻重复元素搬到后面，返回到「新末尾」的迭代器。它不删元素、不改容量，只是搬移。"),
     ("− b − 1", "迭代器减首地址得到下标；因为从 b[1] 开始存，再减 1 才是不同值的个数 m。"),
     ("lower_bound(...) − b", "在去重后的有序数组里二分，得到 a[i] 的名次 1..m。"),
     ("保序性", "a[i] &lt; a[j] ⇔ rk[i] &lt; rk[j]，a[i] == a[j] ⇔ rk[i] == rk[j]，所以「比大小」可以整体换成名次比较。"),
     ("代价", "O(n log n)。n = 5×10⁵ 时约 10⁷ 次比较，和后面的树状数组同阶。")],
    example=r'''int a[6] = {0, 30, 10, 30, 20, 10};
int b[6]; memcpy(b, a, sizeof a);
sort(b + 1, b + 6);                      // 10 10 20 30 30
int m = unique(b + 1, b + 6) - b - 1;    // m = 3
for (int i = 1; i <= 5; ++i)
    printf("%d ", lower_bound(b + 1, b + m + 1, a[i]) - b);   // 3 1 3 2 1''',
    notes=["m 写成 n 也能过，只是树状数组多开一些用不到的位置。",
           "原数组 a 必须留着：扫的时候按原顺序，按 b 的顺序扫就把逆序对关系弄没了。"],
    brief="把 10⁹ 的值域压成 1..m，排名保留全部大小关系"))

# ---------------------------------------------------------------- 思路
SEC.append(IDEA("例题怎么想：把「数对」拆成「单点查询」", [
    "朴素做法枚举所有 i &lt; j 比较，n = 5×10⁵ 时是 1.25×10¹¹ 次比较。C++ 每秒约 10⁸ 次，要跑 20 分钟 → TLE。",
    P("换个数法：不枚举数对，只枚举<b>右边的数</b> a[i]，数它右边有几个比它小。所有位置的答案加起来，每对逆序对恰好被算一次。"),
    P("「右边有多少个比 x 小」是一个值域上的前缀计数：开桶 c[v]，出现一次就 c[v]++，查询 Σ<sub>v &lt; x</sub> c[v]。"
      "单点加 + 前缀和 = 树状数组，两种操作都是 O(log n)。"),
    P("值域到 10⁹，桶开不下。但题目只关心「谁比谁大」，不关心具体值：把每个数换成它在去重后的名次，"
      "严格小、相等这些关系全部保留，值域就压到 1..m ≤ n。"),
    P("从右往左扫 i = n..1：此刻桶里装的全是 a[i] 右边的数，<code>query(rk[i] − 1)</code> 数的是名次 ≤ rk[i]−1，"
      "也就是值严格小于 a[i] 的个数，直接累加。"),
    P("<b>先查后加</b>：query 必须在 add 之前，否则会把自己算进去，答案恰好大 n。"),
    P("对称写法是从左往右 <code>ans += (i − 1) − query(rk[i])</code>。两种写法答案一样，"
      "因为每一对 (i, j) 只在靠右的那个数处被统计一次；两者只差一个 i−1，记住一种即可。"),
]))

SEC.append(C(r'''#include <bits/stdc++.h>
using namespace std;

const int MAXN = 500005;
int a[MAXN], b[MAXN], rk[MAXN], t[MAXN];
int n, m;                       // m：不同值的个数，也是树状数组的值域上界
long long ans;                  // 最多 1.25×10^11，必须 long long

int lowbit(int x) { return x & -x; }

void add(int p) {               // 在名次 p 上记一次出现
    for (; p <= m; p += lowbit(p)) ++t[p];
}
int query(int p) {              // 名次 1..p 上一共出现过多少个数
    int s = 0;
    for (; p > 0; p -= lowbit(p)) s += t[p];
    return s;
}

int main() {
    scanf("%d", &n);
    for (int i = 1; i <= n; ++i) { scanf("%d", &a[i]); b[i] = a[i]; }

    sort(b + 1, b + n + 1);                                // 离散化第一步：排序
    m = unique(b + 1, b + n + 1) - b - 1;                  // 第二步：去重，得到值域 1..m
    for (int i = 1; i <= n; ++i)
        rk[i] = lower_bound(b + 1, b + m + 1, a[i]) - b;   // 第三步：查名次

    for (int i = n; i >= 1; --i) {
        ans += query(rk[i] - 1);   // 桶里全是 i 右边的数，这里数出严格小于 a[i] 的
        add(rk[i]);                // 再把 a[i] 放进桶，留给更左边的人用
    }
    printf("%lld\n", ans);
    return 0;
}''', "完整代码：离散化 + 树状数组"))

SEC.append(EXPLAIN("逐行拆解", [
    ("const int MAXN = 500005;", "n 的上限是 5×10⁵，多开 5 个防止 off-by-one。"),
    ("long long ans;", "5×10⁵ 个数全逆序时对数 = n(n−1)/2 ≈ 1.25×10¹¹，int 装不下，溢出后是负数。"),
    ("b[i] = a[i];", "复制一份用于排序，原数组一动手，逆序对关系就没了。"),
    ("m = unique(b + 1, b + n + 1) - b - 1;", "去重后的元素个数。unique 只搬移不删除，因此必须先 sort；返回值减首地址再减 1，因为下标从 1 起。"),
    ("lower_bound(b + 1, b + m + 1, a[i]) - b", "在去重数组里二分 a[i]，得到名次 1..m。相等的元素拿到同一个名次，这正是我们要的。"),
    ("for (int i = n; i >= 1; --i)", "倒着扫。扫描方向决定了桶里装的是「左边」还是「右边」，两种都对，混着写就错。"),
    ("ans += query(rk[i] - 1);", "rk[i] − 1 把「相等」排除在外，数出的是严格小于 a[i] 的个数，正好是逆序对的定义。"),
    ("add(rk[i]);", "先查后加。顺序反了会把自己算进去，答案固定多 n。"),
    ("printf(\"%lld\\n\", ans);", "long long 必须配 %lld，用 %d 会输出高 32 位的垃圾。"),
]))

SEC.append(P("逆序对还有第二种 O(n log n) 数法：<b>归并排序</b>。合并两段有序数组时，右段的 a[j] 每被取出一次，"
             "左段剩下的 mid − i + 1 个数都比它大，直接累加。常数比树状数组小一半，代价是会打乱原数组，"
             "也回答不了「每个位置右边有多少个更小的」这类附加问题。下一节讲分治时会再用到这段。"))

SEC.append(C(r'''int tmp[MAXN];
long long merge_sort(int l, int r) {      // 返回 [l, r] 内的逆序对数，顺手把 a[l..r] 排好
    if (l >= r) return 0;
    int mid = (l + r) >> 1;
    long long res = merge_sort(l, mid) + merge_sort(mid + 1, r);
    int i = l, j = mid + 1, k = l;
    while (i <= mid && j <= r) {
        if (a[i] <= a[j]) tmp[k++] = a[i++];              // 相等时先取左边，保证相等不算逆序
        else { res += mid - i + 1; tmp[k++] = a[j++]; }   // a[i..mid] 这 mid-i+1 个全都 > a[j]
    }
    while (i <= mid) tmp[k++] = a[i++];
    while (j <= r)   tmp[k++] = a[j++];
    for (int p = l; p <= r; ++p) a[p] = tmp[p];
    return res;
}''', "第二种数法：归并排序（片段，需自己补 MAXN、a、tmp）"))

# ---------------------------------------------------------------- 模板速查
SEC.append(P("46 节的题到这里收口。下面 6 张卡片分别对应 47、48、51、52、53、54，只留<b>最容易写错的那几行</b>；"
             "49 的堆与对顶堆不单独给卡片，第 2 题就是它的完整代码。"))

SEC.append(FN(
    "线段树：apply 与 pushdown",
    "void apply(int p, int l, int r, long long v);\nvoid pushdown(int p, int l, int r);",
    [("tr[p] 管 [l, r]", "每个节点管一段。sum 是这段之和，tag 是「整段要加、但还没分给孩子」的懒标记。"),
     ("数组开 4n", "递归划分出的节点编号最大接近 4n。开 2n 一定越界，症状是 RE 或「样例过、大测试点错」。"),
     ("apply(p, l, r, v)", "sum[p] += v × (r − l + 1); tag[p] += v; 加的是整段，长度必须乘进去。"),
     ("pushdown", "把 tag 分给两个孩子并清零。任何「要进孩子」的 update / query 都必须先调它。"),
     ("不清零的后果", "标记被反复下传，同一段被加多次 → WA，答案偏大，区间越大偏得越多。"),
     ("long long", "10⁵ 次区间加、每次 +10⁹，和可达 10¹⁴，sum 与 tag 都必须是 long long。")],
    example=r'''long long sum[N << 2], tag[N << 2];

void apply(int p, int l, int r, long long v) {
    sum[p] += v * (r - l + 1);     // 整段加 v，和要乘长度
    tag[p] += v;                   // 记账，孩子以后补
}
void pushdown(int p, int l, int r) {
    if (!tag[p]) return;           // 没账可还
    int mid = (l + r) >> 1;
    apply(p << 1, l, mid, tag[p]);
    apply(p << 1 | 1, mid + 1, r, tag[p]);
    tag[p] = 0;                    // 还完必须清零，否则下次又发一遍
}''',
    notes=["query 里也要 pushdown：孩子的 sum 可能是旧值，不推标记直接读会少算。",
           "区间赋值（不是加）时，tag 要记「赋值成几」，并用一个特殊值表示「没有标记」。"],
    brief="区间加 / 区间求和的核心：apply 记账，pushdown 还账并清零"))

SEC.append(FN(
    "单调队列（滑动窗口最值）",
    "deque<int> q;   // 存下标，不存值",
    [("存下标", "只有下标才能判断「有没有滑出窗口」。存值的话过期信息就丢了。"),
     ("保单调", "求最小值时队列里的值单调递增：新元素 a[i] 进队前，把队尾所有 ≥ a[i] 的弹掉。"),
     ("为什么能弹", "下标更大、值又不更大，在它过期之前永远优于被弹掉的元素；被弹掉的再也回不来。"),
     ("队头过期", "窗口左端是 i − k + 1，队头下标 &lt; 左端就 pop_front。"),
     ("取答案", "最小值 = a[q.front()]，O(1)。求最大值把两个比较方向反过来。"),
     ("复杂度", "每个下标进队一次、出队一次，总 O(n)；n = 2×10⁶ 也只有几十毫秒。")],
    example=r'''deque<int> q;
for (int i = 1; i <= n; ++i) {
    while (!q.empty() && a[q.back()] >= a[i]) q.pop_back();  // 队尾没有存在价值了
    q.push_back(i);
    while (q.front() <= i - k) q.pop_front();                // 滑出窗口
    if (i >= k) printf("%d ", a[q.front()]);
}''',
    notes=["用 multiset 是 O(n log n)，常数大 3~5 倍；每个窗口重扫一遍是 O(nk)，n = 10⁶ 必 TLE。",
           "队列里元素个数 ≤ k，手写数组队列比 deque 快一倍，2×10⁶ 的数据建议手写。"],
    brief="四步固定：弹队尾、入队、弹队头、取答案"))

SEC.append(FN(
    "Trie（字典树）",
    "int ch[MAXNODE][26], tot;\nint vis[MAXNODE];   // 0 非单词 / 1 未点过 / 2 已点过",
    [("根", "0 号节点是根，不代表任何字符。"),
     ("ch[p][c]", "节点 p 走字符 c 到达的儿子编号。0 表示没有这条边，所以节点编号从 1 开始，0 专门当「空」。"),
     ("tot", "已用节点数，新节点编号 = ++tot。"),
     ("节点数上界", "所有串长度之和 + 1。10⁴ 个名字、每个 ≤ 50 → 5×10⁵ 个节点。"),
     ("空间", "26 × 节点数 × 4 字节。5×10⁵ 个节点 = 52 MB，128 MB 限制下要算清楚。"),
     ("结尾标记", "走到底还不够：必须看这个节点有没有被标成「单词结尾」。")],
    example=r'''int ch[N][26], vis[N], tot;

void insert(const string &s) {
    int p = 0;
    for (char c : s) {
        int x = c - 'a';
        if (!ch[p][x]) ch[p][x] = ++tot;   // 没有就新建
        p = ch[p][x];
    }
    vis[p] = 1;                            // 只在结尾打标记
}
int query(const string &s) {
    int p = 0;
    for (char c : s) {
        int x = c - 'a';
        if (!ch[p][x]) return 0;           // 断链
        p = ch[p][x];
    }
    return vis[p];                         // 只看结尾标记
}''',
    notes=["字符集是 52 个字母就开 52，别硬套 26，越界写坏的是别的变量。",
           "把 ch 换成 map 能省空间，但每次多一个 log，10⁵ 次查询会慢 5 倍。"],
    brief="共用前缀的树，插入与查询都只走一遍串长"))

SEC.append(FN(
    "KMP 的 nxt 数组",
    "nxt[i] = p[0..i-1] 的最长 border 长度",
    [("border", "既是前缀又是后缀、且不等于自身的子串。"),
     ("nxt[i]", "前缀 p[0..i-1] 的最长 border 长度，同时就是「第 i 位失配后 j 该退到哪」。"),
     ("nxt[1] = 0", "单字符前缀没有非空真 border。"),
     ("递推", "j = nxt[i]；若 p[i] == p[j] 则 nxt[i+1] = j + 1；否则 j = nxt[j] 继续退，退到 0 为止。"),
     ("匹配", "主串指针 i 只增不减，失配时只动 j。总复杂度 O(n + m)。"),
     ("别用 find", "string::find 最坏 O(nm)；n = m = 10⁶ 时是 10¹² 次比较 → TLE。")],
    example=r'''nxt[1] = 0;                              // 下标是「前缀长度」
for (int i = 1, j = 0; i < m; ++i) {     // 循环开始时 j 恒等于 nxt[i]
    while (j && p[i] != p[j]) j = nxt[j];    // 失配就退到更短的 border
    if (p[i] == p[j]) ++j;                   // 接得上就延长一位
    nxt[i + 1] = j;                          // 记的是长度 i+1 的前缀
}''',
    notes=["nxt 的下标是「前缀长度」，不是字符位置；写成 nxt[i] = j 会整体错一位。",
           "n − nxt[n] 是最小循环节长度；当 n 能被 n − nxt[n] 整除时，循环次数就是 n / (n − nxt[n])。"],
    brief="失配不回头：把已匹配部分的最长 border 记下来反复利用"))

SEC.append(FN(
    "ST 表（静态区间最值）",
    "int st[LOG][N], lg[N];",
    [("lg[i]", "floor(log2 i)。预处理 lg[i] = lg[i/2] + 1，别用 log2 的浮点结果，误差一位就是错答案。"),
     ("st[k][i]", "从 i 开始、长度 2^k 的区间的最值。"),
     ("建表", "st[0][i] = a[i]；st[k][i] = max(st[k−1][i], st[k−1][i + 2^(k−1)])，k 由小到大。"),
     ("查询", "len = r − l + 1，k = lg[len]；答案 = max(st[k][l], st[k][r − 2^k + 1])，两段允许重叠。"),
     ("能用于哪些运算", "只限「可重复贡献」的运算：max、min、gcd、按位与/或。区间和不行，重叠部分会被算两次。"),
     ("空间", "LOG × N 个 int。N = 10⁶、LOG = 20 → 80 MB，注意内存限制。")],
    example=r'''for (int i = 2; i <= n; ++i) lg[i] = lg[i >> 1] + 1;    // lg[i] = floor(log2 i)
for (int i = 1; i <= n; ++i) st[0][i] = a[i];
for (int k = 1; (1 << k) <= n; ++k)
    for (int i = 1; i + (1 << k) - 1 <= n; ++i)
        st[k][i] = max(st[k - 1][i], st[k - 1][i + (1 << (k - 1))]);

int len = r - l + 1, k = lg[len];
int mx = max(st[k][l], st[k][r - (1 << k) + 1]);''',
    notes=["表建好后不能改：题目带修改就换线段树。",
           "倍增求 LCA 的内存版本也是 ST 表：把「欧拉序上的深度最小值」当区间最值，思路完全一样。"],
    brief="倍增建表，O(1) 查静态区间最值，两段可以重叠"))

SEC.append(FN(
    "匈牙利算法（二分图最大匹配）",
    "bool dfs(int u);\nint match[N], vis[N], stamp;",
    [("match[v]", "右部点 v 的搭档。0 表示空闲。"),
     ("vis[v]", "本轮 dfs 是否试过 v。少了它，dfs 会在两个点之间反复走 → 栈溢出 RE。"),
     ("让位", "v 被 match[v] 占着，就递归问 match[v] 能不能换一个；能换则 v 归 u。"),
     ("时间戳", "vis 存轮次号，每轮 ++stamp，等价于 memset(vis) 但只花 O(1)。"),
     ("答案", "每成功一次 dfs，匹配数 +1。最终 ans 就是最大匹配边数。"),
     ("复杂度", "O(V·E)。V = 500、E = 5×10⁴ 时 2.5×10⁷，1 秒内可过。")],
    example=r'''bool dfs(int u) {
    for (int v : g[u]) {
        if (vis[v] == stamp) continue;   // 本轮试过，跳过，否则绕圈
        vis[v] = stamp;
        if (!match[v] || dfs(match[v])) {// v 空闲，或 v 的搭档能换走
            match[v] = u;
            return true;
        }
    }
    return false;
}''',
    notes=["只从左部往右部连边，右部不需要存边，省一半空间。",
           "n、m 到 10⁵ 时匈牙利会 TLE，要换 Dinic 或 Hopcroft-Karp。"],
    brief="一次 dfs 找一条增广路，找不到增广路就说明已经是最大匹配"))

# ---------------------------------------------------------------- 易错
SEC.append(WARN("数据结构部分：6 个具体症状", [
    "树状数组下标从 0 开始：<code>add(0)</code> 里 <code>p += lowbit(0) = 0</code>，循环永不结束 → <b>TLE</b>，而且一个字符都不输出。",
    "逆序对答案用 int：n = 5×10⁵ 时最多 1.25×10¹¹，溢出成负数 → <b>WA</b>，小数据全对，只有大测试点挂。",
    "线段树数组只开 2n：递归编号能到 4n，越界写坏相邻变量 → <b>RE 或答案随机</b>。本地跑得通、交上去挂，最难查。",
    "pushdown 后忘记 <code>tag[p] = 0</code>：同一段被反复加 → <b>WA</b>，答案偏大，区间越大偏得越多。",
    "单调队列忘判队头过期：输出的是早就滑出窗口的最值 → <b>WA</b>，前 k 个对、后面全错。",
    "对顶堆只在插入后平衡、输出前不再检查：偶数位置的不变式被破坏，下一次 <code>top()</code> 取到错的 → <b>WA</b>。",
]))

SEC.append(WARN("字符串与二分图：6 个具体症状", [
    "Trie 的节点数组按 n 开（10⁴）而实际要 5×10⁵：写 <code>ch</code> 越界 → <b>RE</b> 或输出乱码。",
    "Trie 查询不判结尾标记：把某个名字的前缀当成名字，输出 OK → <b>WA</b>，只在「a 与 ab」这类数据上错。",
    "KMP 的 nxt 只开主串长度：模式串 10⁶ 时越界 → <b>RE</b>。nxt 的长度由模式串决定。",
    "KMP 里 <code>j = nxt[j]</code> 没判 <code>j &gt; 0</code>，退到 0 还继续取 <code>nxt[0]</code>（未定义）→ <b>死循环 / RE</b>。",
    "ST 表拿去求区间和：重叠部分被算两次 → <b>WA</b>，答案偏大，区间越长偏得越多。",
    "匈牙利忘写 <code>vis[v] = stamp</code>：同一轮反复走同一条边 → <b>RE</b>（栈溢出），数据小时表现为卡死。",
]))

SEC.append(REPRO("关掉页面，把 P1908 从空文件敲一遍并提交，样例必须输出 11。",
                 "把 <code>query(rk[i] - 1)</code> 改成 <code>query(rk[i])</code> 再交：答案会变成「右边 ≤ a[i] 的个数」之和，自己造一组含相等元素的数据，算一算差多少。",
                 "再改成从 1 扫到 n 的写法 <code>ans += (i - 1) - query(rk[i])</code>，确认两种写法输出相同，并说清为什么。",
                 "改一改：把 a[i] 限制到 [1, 1000]，删掉离散化直接开桶（<code>t[a[i]]++</code>），用 5×10⁵ 随机数据和原版比一次运行时间。"))

SEC.append(REPRO("把 P1440 的单调队列敲一遍，用 m = 1 和 m = n 各交一次，确认边界不越界。",
                 "把弹队尾的条件从 <code>&gt;=</code> 改成 <code>&gt;</code>，用 2×10⁶ 个全部相同的数测一次，比较队列最大长度和运行时间。",
                 "再改成「每个位置向前重扫 m 个」，同样的数据下看它跑多久——这就是 O(nm) 的手感。"))

SEC.append(TIP("赛前 10 分钟默写清单", [
    "树状数组：<code>lowbit</code>、<code>add</code>、<code>query</code> 三行，写完用 P3374 交一次。",
    "线段树：<code>apply</code>、<code>pushdown</code>、<code>update</code>、<code>query</code> 四个函数，pushdown 最后一行别忘了清零。",
    "单调队列：弹队尾 → 入队 → 弹队头 → 取答案，四步顺序固定。",
    "Trie：<code>insert</code> 与 <code>query</code>，节点数按「总长度 + 1」估。",
    "KMP：nxt 的六行递推，<code>nxt[1] = 0</code> 不能省。",
    "ST 表：lg 预处理 + 两层循环建表 + 两段重叠查询。",
    "匈牙利：一轮一个 stamp，dfs 里先判 vis 再让位。",
]))

SEC.append(P("下面 5 道按「数据结构 → 字符串 → 图」排列，覆盖 48、49、51、52、54 五节。"
             "每题先自己写 20 分钟；卡住先看提示，再给 10 分钟；还不行才展开思路。做完再往下走。"))

# ---------------------------------------------------------------- 挑战题
CH1 = CH("求 m 区间内的最小值", "P1440", "普及/提高-", "https://www.luogu.com.cn/problem/P1440",
         [P("给出一个含 n 项的数列，对每个元素求出它<b>前面 m 个元素</b>中的最小值。"),
          P("若前面的数不足 m 个，则从第 1 个数算起；若前面一个数都没有，输出 0。"),
          P("输入格式：第一行两个整数 n、m（1 ≤ m ≤ n ≤ 2×10⁶）；第二行 n 个整数 a[i]（0 ≤ a[i] ≤ 10⁹）。"),
          P("输出格式：n 行，第 i 行是 a[1..i−1] 中最后 min(m, i−1) 个数的最小值。")],
         hint=["处理第 i 个数时，它关心的是一段左端和右端都随 i 增大而增大的区间——这就是滑动窗口。",
               "如果 a[i] 比队尾那个元素还小，队尾在它过期之前都不可能再当最小值。",
               "插入 i 之后，队列里只该留下下标 ≥ i − m + 1 的元素；下标 ≤ i − m 的从队头弹掉。"],
         idea=["处理第 i 个数时，窗口是 [max(1, i−m), i−1]。",
               "队列里存下标，对应的值单调递增，队头就是当前窗口最小值。",
               "三步固定：① 输出队头（队列空则输出 0）；② 插入 i，插入前把队尾所有 ≥ a[i] 的弹掉；③ 把下标 ≤ i−m 的队头弹掉。",
               "为什么被弹掉的不会回来：它下标更小、值又不更小，在它过期之前全面劣于新元素，之后也不会重新进入窗口。",
               "复杂度 O(n)：每个下标最多进队一次、出队一次。n = 2×10⁶ 时约 4×10⁶ 次操作。",
               "对照：每个位置向前重扫 m 个是 O(nm)，m = n 时 4×10¹² → TLE；multiset 是 O(n log n)，常数大 3~5 倍。"],
         code=r'''#include <bits/stdc++.h>
using namespace std;

const int MAXN = 2000005;
int a[MAXN], q[MAXN];          // q 存下标：手写队列，比 deque 快一倍

int main() {
    int n, m;
    scanf("%d%d", &n, &m);
    for (int i = 1; i <= n; ++i) scanf("%d", &a[i]);

    int head = 1, tail = 0;     // 队列区间 [head, tail]，head > tail 表示空
    for (int i = 1; i <= n; ++i) {
        if (head > tail) printf("0\n");          // 只有 i = 1 会走到这里
        else printf("%d\n", a[q[head]]);         // 队头就是前 m 个数的最小值

        while (head <= tail && a[q[tail]] >= a[i]) --tail;  // 又大又早的队尾没用了
        q[++tail] = i;                           // 存下标，才能判过期

        while (head <= tail && q[head] <= i - m) ++head;    // 窗口左端是 i-m+1
    }
    return 0;
}''',
         explain=[
             ("int head = 1, tail = 0;", "用 [head, tail] 表示队列，空队列是 head = tail + 1。省掉 deque 的封装，2×10⁶ 次操作能快一倍。"),
             ("if (head > tail) printf(\"0\\n\");", "只有 i = 1 时队列为空：前面没有数，按题意输出 0。"),
             ("a[q[head]]", "队头下标对应的值就是答案，O(1) 取，不需要再维护别的东西。"),
             ("while (head <= tail && a[q[tail]] >= a[i]) --tail;", "写 ≥ 而不是 &gt;：值相等的旧元素下标更小、过期更早，留着没用。用 &gt; 会让队列里堆一堆相等的值。"),
             ("q[++tail] = i;", "存下标而不是值。存值就不知道这个元素是什么时候进来的，无法判断过期。"),
             ("while (head <= tail && q[head] <= i - m) ++head;", "窗口左端是 i−m+1，所以下标 ≤ i−m 的必须走。放在插入之后，保证下一轮队头有效。"),
         ],
         pitfalls=["队列里存值不存下标：无法判断队头是否过期，输出会变成整个前缀的最小值 → WA。",
                   "输出放在插入之后：第 i 行会把 a[i] 自己也算进去，而题意要的是「前面」m 个数 → WA。",
                   "数组只开 10⁶：n = 2×10⁶ 时越界，表现为前面几个数对、后面乱或直接 RE。",
                   "用 cin/cout 读 2×10⁶ 个数又没关同步 → TLE；请用 scanf 或加两行提速。",
                   "输出写成一行空格分隔：题目要 n 行，每行一个数 → WA。"])

CH2 = CH("中位数", "P1168", "普及/提高-", "https://www.luogu.com.cn/problem/P1168",
         [P("给出一个长度为 N 的非负整数序列 A。对每个 1 ≤ k ≤ (N+1)/2，输出 A<sub>1</sub>, A<sub>3</sub>, …, A<sub>2k−1</sub> 的中位数，"
            "也就是<b>前 2k−1 个数</b>的中位数。"),
          P("输入格式：第一行 N（1 ≤ N ≤ 10⁵，N 为奇数）；第二行 N 个整数（0 ≤ A[i] ≤ 10⁹）。"),
          P("输出格式：(N+1)/2 行，每行一个整数。")],
         hint=["中位数只关心「比它小的有多少个」，不需要把整个前缀排序。",
               "把数分成两堆：小的一半放一起，大的一半放一起。中位数就是小堆里最大的那个。",
               "两堆的大小差不能超过 1，每次插入后立刻调整。哪种容器能 O(log n) 取最值？"],
         idea=["用一个大根堆 small 存较小的一半，一个小根堆 large 存较大的一半。",
               "不变式：small.size() = large.size() 或 large.size() + 1，并且 small 里所有元素 ≤ large 里所有元素。",
               "插入 x：x ≤ small.top() 就进 small，否则进 large。",
               "调整：small 比 large 多出 2 个或更多，就把 small 的堆顶（小半部分的最大值）搬给 large；"
               "small 比 large 少，就把 large 的堆顶（大半部分的最小值）搬回 small。",
               "长度为 2k−1 时，small 恰好 k 个、large 恰好 k−1 个，中位数 = small.top()。",
               "复杂度 O(n log n)：每个数至多进堆一次、跨堆搬一次。"],
         code=r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    scanf("%d", &n);
    priority_queue<int> small;                                  // 大根堆：较小的一半
    priority_queue<int, vector<int>, greater<int> > large;      // 小根堆：较大的一半

    for (int i = 1; i <= n; ++i) {
        int x;
        scanf("%d", &x);
        if (small.empty() || x <= small.top()) small.push(x);
        else large.push(x);

        // 插入后立刻恢复不变式，别等到输出前才调
        if ((int)small.size() > (int)large.size() + 1) {
            large.push(small.top()); small.pop();
        } else if ((int)small.size() < (int)large.size()) {
            small.push(large.top()); large.pop();
        }

        if (i & 1) printf("%d\n", small.top());   // 长度 2k-1 时，中位数是 small 的堆顶
    }
    return 0;
}''',
         explain=[
             ("priority_queue<int> small;", "默认大根堆，堆顶是 small 里最大的，正好是「小半部分的最大值」。"),
             ("priority_queue<int, vector<int>, greater<int> > large;", "三个参数缺一不可。greater 让堆顶变成最小值，才能 O(1) 拿到大半部分的最小值。"),
             ("if (small.empty() || x <= small.top())", "第一个数必须进 small（空堆不能 top）。用 ≤ 而不是 &lt;，让相等的数优先留在 small，堆大小才稳定。"),
             ("if ((int)small.size() > (int)large.size() + 1)", "small 最多比 large 多 1 个。多出两个就把 small 的堆顶搬过去。"),
             ("else if ((int)small.size() < (int)large.size())", "small 比 large 少就搬回来。两个分支互斥，一轮只可能触发一个。"),
             ("if (i & 1) printf(\"%d\\n\", small.top());", "只在奇数长度输出。此时 small 有 k 个、large 有 k−1 个，第 k 小就是 small 的堆顶。"),
         ],
         pitfalls=["写成 <code>priority_queue&lt;int&gt;</code> 当小根堆：取到的是最大值，整个逻辑反了 → WA。",
                   "插入后不调整堆大小：small.top() 不是中位数，输出整体偏大或偏小。",
                   "只在输出前调整：偶数位置的不变式被破坏，下一次取 top 直接取错 → WA。",
                   "中位数位置搞错：长度 2k−1 时是第 k 小，不是第 k+1 小。",
                   "用 vector + 每次 sort：O(n² log n)，n = 10⁵ 必 TLE。"])

CH3 = CH("于是他错误的点名开始了", "P2580", "普及/提高-",
         "https://www.luogu.com.cn/problem/P2580",
         [P("老师手上有 n 个学生的名字，接下来要点名 m 次。"),
          P("被点的名字不在名单里输出 <code>WRONG</code>；在名单里且是第一次被点到输出 <code>OK</code>；"
            "在名单里但之前已经点到过输出 <code>REPEAT</code>。"),
          P("输入格式：第一行 n（n ≤ 10⁴）；接下来 n 行每行一个名字（只含小写字母，长度 ≤ 50）；"
            "然后一行 m（m ≤ 10⁵）；接下来 m 行每行一个被点的名字（格式同上）。"),
          P("输出格式：m 行，每行是 <code>OK</code>、<code>REPEAT</code> 或 <code>WRONG</code>。")],
         hint=["名字只含小写字母，字符集只有 26 个——这正是 Trie 的形状：每个节点 26 个儿子。",
               "「单词结尾」必须单独标记：名字 a 和名字 ab 会共用节点 0→a，不能只看走没走到。",
               "OK 与 REPEAT 的差别只是这个结尾节点被访问过几次，用一个 0/1/2 的状态数组就够。"],
         idea=["建 Trie：0 号是根，边表示字符，ch[p][c] 是节点 p 走字符 c 的儿子。",
               "插入：沿字符往下走，没有儿子就新建，最后在结尾节点上标 1。",
               "查询：沿字符往下走，中途没有儿子 → WRONG（断链）；走到底但结尾没标记 → WRONG（它只是别人的前缀）；"
               "标记为 1 → 改成 2 并输出 OK；标记为 2 → REPEAT。",
               "节点数上界 = 所有名字长度之和 + 1 ≤ 10⁴ × 50 + 1 ≈ 5×10⁵。",
               "空间 26 × 5×10⁵ × 4 字节 ≈ 52 MB，在 128 MB 限制内，但不能再多开一倍。",
               "复杂度 O(总字符数) ≈ 5×10⁵ + 5×10⁶（查询串总长），比 map 的每行一次 log 快得多。"],
         code=r'''#include <bits/stdc++.h>
using namespace std;

const int MAXNODE = 500005;      // 所有名字的总长度 + 1
int ch[MAXNODE][26];             // ch[p][c]：节点 p 走字符 c 的儿子，0 表示没有
int vis[MAXNODE];                // 0 不是单词；1 是单词且没点过；2 点过了
int tot;                         // 已用节点数，新节点编号 = ++tot

void insert(const string &s) {
    int p = 0;                                       // 0 号是根
    for (char c : s) {
        int x = c - 'a';
        if (!ch[p][x]) ch[p][x] = ++tot;             // 没有这条边就新建
        p = ch[p][x];
    }
    vis[p] = 1;                                      // 只在单词结尾打标记
}

int query(const string &s) {
    int p = 0;
    for (char c : s) {
        int x = c - 'a';
        if (!ch[p][x]) return 0;                     // 断链：名单里没有
        p = ch[p][x];
    }
    if (vis[p] == 0) return 0;                       // 走到底却没标记：只是别人的前缀
    if (vis[p] == 1) { vis[p] = 2; return 1; }       // 第一次点到
    return 2;                                        // 之前点过
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    for (int i = 0; i < n; ++i) { string s; cin >> s; insert(s); }

    int m;
    cin >> m;
    for (int i = 0; i < m; ++i) {
        string s;
        cin >> s;
        int r = query(s);
        if (r == 0) cout << "WRONG\n";
        else if (r == 1) cout << "OK\n";
        else cout << "REPEAT\n";
    }
    return 0;
}''',
         explain=[
             ("ch[MAXNODE][26]", "字符集 26 个字母，所以第二维是 26。全部初始化为 0，正好表示「没有这条边」。"),
             ("if (!ch[p][x]) ch[p][x] = ++tot;", "新节点编号从 1 开始，0 专门留给「空」。如果从 0 开始编号，就无法区分「根」和「不存在」。"),
             ("vis[p] = 1;", "只在单词的最后一个节点上标记：中间节点可能是别的单词的前缀，标了就会把前缀当成名字。"),
             ("if (!ch[p][x]) return 0;", "查询中途断开，这个串一定不在名单里，直接返回，不用再走。"),
             ("if (vis[p] == 0) return 0;", "走到位却没有标记，说明它只是某个名字的前缀（例如名单里只有 ab，来查 a）。"),
             ("vis[p] = 1 → 2", "第一次点到就把状态改成 2，下次再来走 REPEAT 分支。三个状态刚好够用。"),
         ],
         pitfalls=["节点数组按 n（10⁴）开：实际最长 5×10⁵，写 ch 越界 → RE 或输出乱码。",
                   "MAXNODE 开到 10⁶：26×10⁶×4 ≈ 104 MB，直接 MLE。按「总长度 + 1」估。",
                   "查询只判走到底、不判结尾标记：前缀被当成名字，输出 OK → WA。",
                   "用 map 每行 O(L log n)：m = 10⁵、L = 50，字符比较量约 10⁸，可能 TLE。",
                   "输出写成 Ok、ok、Wrong：大小写不符 → WA。"])

CH4 = CH("【模板】KMP字符串匹配", "P3375", "普及/提高-", "https://www.luogu.com.cn/problem/P3375",
         [P("给出两个字符串 s1 与 s2。若 s1 的区间 [l, r] 与 s2 完全相同，则称 s2 在 s1 中出现在位置 l。"),
          P("求出 s2 在 s1 中所有出现的位置（每行一个，按从小到大）。"),
          P("再对 s2 的每个前缀 s2[1..i] 求出它的<b>最长 border</b> 长度（border 指既是前缀又是后缀、且不等于自身的子串），"
            "最后输出一行 |s2| 个用空格分隔的整数。"),
          P("输入格式：第一行 s1，第二行 s2（1 ≤ |s1|, |s2| ≤ 10⁶，只含大写字母）。")],
         hint=["暴力匹配失配时把主串指针往回退，退掉的那些字符其实已经比较过了。",
               "记下「模式串前 i 个字符的最长 border」，失配时把 j 退到那里，主串指针一步都不回退。",
               "border 的 border 还是 border，所以可以一路 j = nxt[j] 退下去，不会漏掉更短的可能。"],
         idea=["nxt[i] = p[0..i−1] 的最长 border 长度，nxt[1] = 0。",
               "递推：已知 nxt[i]，令 j = nxt[i]；若 p[i] == p[j] 则 nxt[i+1] = j + 1，否则 j = nxt[j] 继续退到 0。",
               "匹配：i 扫主串，j 是已匹配长度；s[i] == p[j] 则 ++j，否则 j = nxt[j]；j == m 时记录起点。",
               "起点换成 1-based：i 是 0-based 的结尾，起点 = i − m + 1（0-based）= i − m + 2（1-based）。",
               "找到一次后令 j = nxt[m]，才能继续找<b>重叠</b>的出现（如 s1 = aaa、s2 = aa 有两个位置）。",
               "复杂度 O(n + m)：i 只增不减；j 每次失配至少减 1，总减少量不超过总增加量。"],
         code=r'''#include <bits/stdc++.h>
using namespace std;

const int MAXN = 1000005;
int nxt[MAXN];                  // nxt[i]：p[0..i-1] 的最长 border 长度

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string s, p;
    cin >> s >> p;
    int n = s.size(), m = p.size();

    nxt[1] = 0;                                       // 单字符前缀没有非空真 border
    for (int i = 1, j = 0; i < m; ++i) {              // 循环开始时 j 恒等于 nxt[i]
        while (j && p[i] != p[j]) j = nxt[j];         // 失配就退到更短的 border
        if (p[i] == p[j]) ++j;                        // 接得上就延长一位
        nxt[i + 1] = j;                               // 记的是「长度 i+1 的前缀」
    }

    for (int i = 0, j = 0; i < n; ++i) {
        while (j && s[i] != p[j]) j = nxt[j];         // 主串指针 i 从不后退
        if (s[i] == p[j]) ++j;
        if (j == m) {                                 // 找到一个完整匹配
            printf("%d\n", i - m + 2);                // 换成 1-based 起点
            j = nxt[j];                               // 退一步，继续找重叠的出现
        }
    }

    for (int i = 1; i <= m; ++i) printf("%d ", nxt[i]);
    printf("\n");
    return 0;
}''',
         explain=[
             ("nxt[1] = 0;", "长度为 1 的前缀没有非空真前缀，border 必为 0。nxt 是全局数组时漏写也恰好是 0，改成局部数组就成随机值。"),
             ("for (int i = 1, j = 0; i < m; ++i)", "i 是「正在算 nxt[i+1]」的位置，j 在循环开始时恒等于 nxt[i]。这个不变式是整个算法的骨架。"),
             ("while (j && p[i] != p[j]) j = nxt[j];", "失配就退到更短的 border 再比。j == 0 时停下，否则会去读 nxt[0]（未定义）。"),
             ("if (p[i] == p[j]) ++j;", "能接上就延长一位。j 是 0 时比较 p[0] 与 p[i] 也是合法的，不能用 if (j && ...) 包起来。"),
             ("nxt[i + 1] = j;", "nxt 的下标是前缀长度而不是字符位置，所以写 i+1。写成 nxt[i] 会整体错一位。"),
             ("j = nxt[j];", "匹配成功后必须退，否则下一轮 p[j] 越界；退到 nxt[m] 才能找到重叠的出现。"),
             ("printf(\"%d\\n\", i - m + 2);", "i 是 0-based 结尾，起点 = i−m+1（0-based）= i−m+2（1-based），少加 1 就整体偏小。"),
         ],
         pitfalls=["nxt 数组只开主串长度：模式串 10⁶ 时越界 → RE。nxt 的长度由模式串决定。",
                   "输出位置用 0-based：全部小 1 → WA。",
                   "忘了最后一行 nxt 的输出，或不用空格分隔 → WA / 格式错。",
                   "匹配成功后写 j = 0：漏掉重叠出现，s1 = aaa、s2 = aa 会少输出一个位置。",
                   "把 j = nxt[j] 写成 --j：最坏退化成 O(nm)，n = m = 10⁶ → TLE。"])

CH5 = CH("【模板】二分图最大匹配", "P3386", "普及/提高-",
         "https://www.luogu.com.cn/problem/P3386",
         [P("给定一个二分图：左部 n 个点、右部 m 个点、e 条边。求<b>最大匹配</b>——最多能选出多少条边，"
            "使任意两条选中的边没有公共端点。"),
          P("输入格式：第一行 n、m、e（1 ≤ n, m ≤ 500，1 ≤ e ≤ 5×10⁴）；接下来 e 行每行 u、v，"
            "表示左部点 u 与右部点 v 之间有一条边。"),
          P("输出格式：一行一个整数，表示最大匹配数。")],
         hint=["一条边被选中后，它两端的点都不能再用。题目问的是「最多能选几条」。",
               "从左部点一个一个处理：要么直接连一个空闲的右部点，要么请占着它的左部点「换一个」。",
               "「请别人换一个」就是递归。必须记录本轮试过哪些右部点，否则会在两个点之间绕圈。"],
         idea=["依次给每个左部点 u 找匹配，用 dfs 找一条增广路。",
               "dfs(u)：枚举 u 的每条边 (u, v)。若 v 本轮没试过，标记它；v 空闲则 match[v] = u 直接成功；"
               "否则递归 dfs(match[v])，若能给 match[v] 找到新位置，就让 v 归 u。",
               "成功一次，匹配数 +1。匈牙利算法的正确性来自「不存在增广路 ⇔ 当前匹配已是最大匹配」。",
               "vis 用时间戳：每轮 ++stamp，vis[v] == stamp 表示本轮试过，省掉每组 O(m) 的 memset。",
               "复杂度 O(V·E)：500 × 5×10⁴ = 2.5×10⁷，1 秒内可过。"],
         code=r'''#include <bits/stdc++.h>
using namespace std;

const int MAXN = 505;
vector<int> g[MAXN];             // 只存左部 → 右部的边
int match[MAXN];                 // match[v]：右部点 v 的搭档，0 表示空闲
int vis[MAXN], stamp;            // vis[v] == stamp 表示「本轮 dfs 试过 v」

bool dfs(int u) {
    for (int v : g[u]) {
        if (vis[v] == stamp) continue;      // 本轮试过就跳过，否则会绕圈
        vis[v] = stamp;
        if (!match[v] || dfs(match[v])) {   // v 空闲，或 v 的搭档能换走
            match[v] = u;                   // 让位成功，v 归 u
            return true;
        }
    }
    return false;
}

int main() {
    int n, m, e;
    scanf("%d%d%d", &n, &m, &e);
    for (int i = 0; i < e; ++i) {
        int u, v;
        scanf("%d%d", &u, &v);
        g[u].push_back(v);
    }

    int ans = 0;
    for (int u = 1; u <= n; ++u) {
        ++stamp;                            // 等价于 memset(vis)，但只花 O(1)
        if (dfs(u)) ++ans;
    }
    printf("%d\n", ans);
    return 0;
}''',
         explain=[
             ("vector<int> g[MAXN];", "只存左部到右部的边。右部的邻接表用不到，省一半空间。"),
             ("if (vis[v] == stamp) continue;", "同一轮里每个右部点只试一次。少了这一句，dfs 会在两个点之间来回走 → 栈溢出 RE。"),
             ("if (!match[v] || dfs(match[v]))", "v 空闲就直接占；否则问 v 现在的搭档能不能换地方。|| 的短路顺序不能反，先判空再递归。"),
             ("match[v] = u;", "让位成功之后才改 match。写在判断之前，失败时会把原来的匹配也弄丢。"),
             ("++stamp;", "每个左部点一轮，stamp 自增相当于 memset(vis)，但每次只花 O(1)。"),
             ("if (dfs(u)) ++ans;", "每找到一条增广路，匹配数加一。ans 就是最大匹配边数。"),
         ],
         pitfalls=["忘写 vis[v] = stamp：同一轮反复走同一条边 → 死循环或栈溢出 RE。",
                   "vis 清得比右部点少（循环写到 n 而不是 m）：n &lt; m 时右部点没清，第二轮起匹配出错 → WA。",
                   "把 match[v] = u 写在判断成功之前：dfs 失败时匹配已被破坏 → WA。",
                   "递归时传 v 而不是 match[v]：在右部点上递归，编号含义全乱 → WA 或 RE。",
                   "n、m 到 10⁵ 还用匈牙利：O(VE) 到 5×10⁹ → TLE，要换 Hopcroft-Karp 或 Dinic。"])

# ---------------------------------------------------------------- 附加挑战 2
# 回顾章的第 2 道加练：树状数组不只能数逆序对，配上「离线 + 按右端点扫」还能回答区间种类数。
CHT2 = CH(
    "HH 的项链", "P1972", "提高-/提高", "https://www.luogu.com.cn/problem/P1972",
    [P("HH 有一串由各种贝壳组成的项链，第 i 颗贝壳的种类编号是 a<sub>i</sub>。"
       "他有 m 个询问，每个询问给出一段区间 [l, r]，问这段区间里一共有多少<b>种不同</b>的贝壳。"),
     P("输入：第一行一个整数 n（1 ≤ n ≤ 10<sup>6</sup>）；第二行 n 个正整数 a<sub>i</sub>"
       "（1 ≤ a<sub>i</sub> ≤ 10<sup>6</sup>）；第三行一个整数 m（1 ≤ m ≤ 10<sup>6</sup>）；"
       "接下来 m 行，每行两个整数 l、r（1 ≤ l ≤ r ≤ n）。"),
     P("输出：m 行，每行一个整数，依次是每个询问的答案。"),
     P("样例：序列 1 2 3 4 3 5。询问 [1,2] 只有 1、2 两种；[3,5] 是 3、4、3，两种；"
       "[2,6] 是 2、3、4、3、5，四种。")],
    hint=["n 和 m 都是 10<sup>6</sup>，每个询问扫一遍区间是 10<sup>12</sup>。但这道题<b>没有修改</b>，"
          "所以可以把所有询问放在一起、换个顺序处理。",
          "假设右端点 r 从 1 慢慢推到 n，你只维护一个长度为 n 的 0/1 数组。"
          "怎么让它始终保持「[1, r] 里每个出现过的值恰好被记 1 次」？",
          "同一个值出现多次时，只保留它<b>最右</b>的那一次。那么每来一个新元素，它上一次出现的位置要做什么？"
          "区间和又要用什么结构 O(log n) 求？"],
    idea=["暴力：每个询问扫一遍，O(nm) = 10<sup>12</sup>，必 TLE。",
          "把「区间里有几种不同的值」换成「区间和」。维护 0/1 数组 c，规则：每个值只在它<b>当前最右一次</b>出现的位置上记 1。",
          "为什么这样就对：固定 r，对任意值 v，若 v 在 [l, r] 里出现过，那它在 [1, r] 里的最右出现位置 ≥ l，"
          "恰好落在 [l, r] 内，贡献 1；若 v 没在 [l, r] 里出现，它的最右出现位置就在 l 左边（或根本没有），贡献 0。"
          "所以 c 在 [l, r] 上的和就是不同种类数。",
          "右端点从 r−1 推到 r（新元素 a[r]）：先把 a[r] 上一次出现的位置上的 1 清成 0，再把 r 置 1。"
          "维护 last[值] 就能 O(1) 找到上一次的位置。",
          "区间和用树状数组：单点改 O(log n)，前缀和 O(log n)。",
          "离线：把询问按 r 升序排序，指针 p 从 1 扫到 n；每推进一步就把所有 r = p 的询问用 sum(r) − sum(l−1) 回答，"
          "答案按原编号存回去。r 只能往前推，所以必须按 r 排序。",
          "复杂度：O((n + m) log n) ≈ 2×10<sup>6</sup>×20 = 4×10<sup>7</sup> 次加法；"
          "输入约 20 MB，用 getchar 手写快读（cin 关同步在 10<sup>6</sup> 量级仍然吃力）。"],
    code=r'''#include <bits/stdc++.h>
using namespace std;

const int MAXN = 1000005;
int a[MAXN], last[MAXN], bit[MAXN], ans[MAXN];
struct Q { int l, r, id; } qs[MAXN];
int n, m;

inline int lowbit(int x) { return x & -x; }
void add(int i, int d) { for (; i <= n; i += lowbit(i)) bit[i] += d; }
int sum(int i) { int s = 0; for (; i > 0; i -= lowbit(i)) s += bit[i]; return s; }

inline int readInt() {
    int x = 0;
    char c = getchar();
    while (c < '0' || c > '9') c = getchar();
    while (c >= '0' && c <= '9') { x = x * 10 + (c - '0'); c = getchar(); }
    return x;
}

int main() {
    n = readInt();
    for (int i = 1; i <= n; ++i) a[i] = readInt();
    m = readInt();
    for (int i = 0; i < m; ++i) {
        qs[i].l = readInt(); qs[i].r = readInt(); qs[i].id = i;
    }
    sort(qs, qs + m, [](const Q& x, const Q& y) { return x.r < y.r; });

    int p = 0;
    for (int i = 0; i < m; ++i) {
        while (p < qs[i].r) {
            ++p;
            if (last[a[p]]) add(last[a[p]], -1);   // 同一个值只保留最右一次出现
            add(p, 1);
            last[a[p]] = p;
        }
        // 此时 c 里为 1 的位置，恰好是每种贝壳在 [1, r] 里的最右出现
        ans[qs[i].id] = sum(qs[i].r) - sum(qs[i].l - 1);
    }
    for (int i = 0; i < m; ++i) printf("%d\n", ans[i]);
    return 0;
}''',
    explain=[
        ("if (last[a[p]]) add(last[a[p]], -1);", "★ 同一个值只保留最右一次出现：把上一次的 1 撤掉，"
                                                "[1, r] 里每个值就恰好被记 1 次。"),
        ("add(p, 1); last[a[p]] = p;", "last 的大小是值域 10<sup>6</sup>，不是 n。两者数值接近但含义不同，写错就 RE。"),
        ("sort(qs, qs + m, ... x.r < y.r)", "离线核心：按右端点排序，树状数组只需要往后推进。"),
        ("while (p < qs[i].r) { ++p; ... }", "指针 p 只增不减，全部询问处理完总共走 n 步。"),
        ("ans[qs[i].id] = sum(r) - sum(l - 1);", "前缀和相减就是区间和；此时和为 1 的位置正好是每种贝壳的最右出现。"),
        ("inline int readInt()", "n = m = 10<sup>6</sup>、输入 20 MB，getchar 快读是本题的第二个知识点。"),
    ],
    pitfalls=["last 按 n 开：a<sub>i</sub> ≤ 10<sup>6</sup>，值域和长度不是一回事，越界后答案随机。",
              "对每个询问单独从 1 扫到 r：退化成 O(nm)，指针 p 必须单调。",
              "忘了清掉上一次出现的 1：每个值被重复计数，答案变成区间长度。",
              "按处理顺序输出：排序打乱了顺序，必须按 id 回填。"],
    sample="输入：\n6\n1 2 3 4 3 5\n3\n1 2\n3 5\n2 6\n输出：\n2\n2\n4",
)

CHS = [CH1, CH2, CH3, CH4, CH5]

CHECK = [
    "能不看模板写出 lowbit、add、query 三行，并说清 query 为什么是 O(log n)。",
    "能说清离散化三步各自的作用，以及漏掉 sort 会发生什么。",
    "看到「区间加 + 区间求和」能立刻指出 pushdown 要在 update 和 query 两处调用。",
    "能区分何时用单调队列、何时用堆：一个是「固定窗口 + 顺序滑动」，一个是「全局最值」。",
    "能写出 Trie 的 insert 与 query，并说出节点数上界怎么估、空间怎么算。",
    "能默写 KMP 的 nxt 递推，并解释 nxt[i] 的含义与 n − nxt[n] 的意义。",
    "能说出 ST 表为什么能求 max 却不能求区间和。",
    "能写出匈牙利的 dfs 框架，并解释 vis 数组与 stamp 时间戳各自防的是什么。",
]

LESSONS = [LESSON(
    55, "回顾九：数据结构与字符串",
    "把第 46~54 节压成一张对照表：树状数组、线段树、单调栈/队列、堆、Trie、KMP、ST 表、二分图各管哪类问题。"
    "先用 P1908 逆序对把「离散化 + 树状数组」完整写一遍并换方向再数一次，再配 6 张模板速查卡"
    "（线段树、单调队列、Trie、KMP、ST 表、匈牙利），最后用 P1440、P1168、P2580、P3375、P3386 五道黄题限时训练，"
    "每题带完整思路与参考代码。",
    100, ["回顾", "5 题"], "提高",
    SEC, check=CHECK, challenge=CH1, challenge2=CHT2,
    refs=[
        "《算法竞赛入门笔记》：树状数组、线段树、单调队列、字符串匹配相关章节",
        "《算法竞赛进阶指南》：树状数组、线段树、字符串哈希、KMP 与 Trie 相关章节",
        "《算法竞赛试炼场：洛谷300题精析》：P1908、P1440、P1168、P2580、P3375、P3386 的精析",
        "《算法竞赛黄金法则》：先把暴力里「重扫一遍」的那句标出来，再选结构",
        "想再练一道 Trie，加做 P3879 阅读理解（不计入本次限时）",
    ])]

# 回顾章由 render.render_review 渲染，读的是 challenges 列表（复数）
LESSONS[0]["challenges"] = CHS
