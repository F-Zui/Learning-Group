# -*- coding: utf-8 -*-
"""第 47 节 · 线段树"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dsl import *  # noqa

SEC = []

SEC.append(P("第 46 节的树状数组很快，但它只吃“能相减”的信息：和、异或、计数。"
             "一旦题目要<b>区间加并且区间求和</b>，或者要<b>区间最值</b>，那套 12 行就不够了。"
             "这一节写一个通用得多的结构：<b>把区间二分到底，每个节点维护自己那一段的整体信息</b>。"
             "四十行代码，覆盖比赛里大半的区间问题。"))

SEC.append(Q("线段树的所有细节都能由一句话推出来：<b>每个节点负责一个区间，节点上的值由两个儿子合并而来</b>。"
             "哪个函数不会写，就回到这句话，问自己“我要的是哪一段、它的儿子是谁”。"))

SEC.append(T(["问题", "树状数组", "线段树"], [
    ["单点改 + 前缀和", "O(log n)，12 行", "O(log n)，40 行"],
    ["区间加 + 单点查", "O(log n)，差分", "O(log n)，懒标记"],
    ["区间加 + 区间和", "要两个树状数组推式子", "直接做，只改 pushup"],
    ["区间最值 / gcd", "不支持", "O(log n)"],
    ["区间最大子段和", "不支持", "O(log n)，多维护 3 个量"],
    ["常数", "极小，没有递归", "约 3~5 倍"],
    ["数组空间", "n", "4n"],
]))

# ---------------------------------------------------------------- 区间划分
SEC.append(P("先把<b>区间怎么分</b>钉死。这是线段树唯一不随题目变化的部分，也是 90% 的错位 bug 的来源。"
             "根节点管 [1, n]。对一个管 [l, r] 的节点，令 <code>mid = (l + r) / 2</code>（向下取整），"
             "把它劈成左儿子 [l, mid] 与右儿子 [mid+1, r]，两段长度差不超过 1。"
             "一直劈到 <code>l == r</code>，那就是叶子，管一个位置。"))

SEC.append(C(r'''                      [1,5]                    节点编号 p = 1
                    /       \
              [1,3]           [4,5]                 p = 2, 3
             /     \         /     \
         [1,2]   [3,3]   [4,4]   [5,5]              p = 4, 5, 6, 7
         /   \
      [1,1] [2,2]                                   p = 8, 9

  左儿子 2p，右儿子 2p+1：堆式编号，不用存指针，也不用存区间（l、r 现场推）''',
         "n = 5 时的区间划分与节点编号"))

SEC.append(P("编号带来一个副作用：<b>会跳号</b>。n = 5 时最大编号是 9，n = 6 时直接跳到 13。"
             "所以数组必须开 4n——按 2n 开会在 n = 6 这种小数据上就踩出去。这个 4 是怎么来的，数学补给里算清楚。"))
SEC.append(P("一个询问区间 [ql, qr] 与当前节点 [l, r] 的关系只有三种：<b>完全包含</b>（整段都要，直接返回，不再往下）、"
             "<b>完全不相交</b>（根本不会递归进来）、<b>部分相交</b>（两边各自递归）。"
             "query 里那几个 if，全部只是在区分这三件事。"))

# ---------------------------------------------------------------- 新函数
SEC.append(P("接下来四张卡对应线段树的四块骨头：<b>建树、合并、查询、懒标记</b>。"
             "前两张是“从下往上”，第三张是“从上往下”，第四张解决“整段修改怎么不往下走”。"))

SEC.append(FN(
    "build（递归建树）",
    "void build(int p, int l, int r);",
    [("p", "节点编号。根固定是 1，左儿子 2p，右儿子 2p+1。"),
     ("l, r", "这个节点负责的闭区间。它们跟着递归参数走，<b>不存进数组</b>，省掉 8n 的空间。"),
     ("if (l == r)", "叶子：这一段只有一个位置，把 a[l] 直接抄进 s[p]，然后 return。"),
     ("mid = (l + r) >> 1", "从中间劈开。(l+r)/2 向下取整，所以左段比右段多一个或一样长，两段都不可能为空。"),
     ("两次递归", "先建左子树再建右子树，顺序无所谓，反正都在 pushup 之前。"),
     ("pushup(p)", "两个儿子都有值了，用它们推出 s[p]。<b>必须写在两次递归之后</b>，写前面就用到 0。"),
     ("只调一次 build(1, 1, n)", "每个节点访问一次，总复杂度 O(n)，不是 O(n log n)。"),
     ("数组开 4n", "n 个位置的树有 2n−1 个真实节点，但堆式编号会跳号，4n 才一定够（数学补给给证明）。")],
    example=r'''#include <bits/stdc++.h>
using namespace std;

const int N = 100005;
long long a[N], s[N << 2];             // s[p]：节点 p 管辖区间内所有数的和

void pushup(int p) { s[p] = s[p << 1] + s[p << 1 | 1]; }

void build(int p, int l, int r) {
    if (l == r) { s[p] = a[l]; return; }         // 叶子：直接抄原数
    int mid = (l + r) >> 1;
    build(p << 1, l, mid);                       // 左子树 [l, mid]
    build(p << 1 | 1, mid + 1, r);               // 右子树 [mid+1, r]
    pushup(p);                                   // 儿子都好了，才能推自己
}

int main() {
    int n = 5;
    long long b[6] = {0, 1, 5, 4, 2, 3};
    for (int i = 1; i <= n; ++i) a[i] = b[i];
    build(1, 1, n);
    cout << s[1] << "\n";                        // 1+5+4+2+3 = 15
    cout << s[2] << " " << s[3] << "\n";         // a[1..3]=10, a[4..5]=5
    return 0;
}''',
    notes=["build 只在“初始有值”时需要。很多时候（比如从空数列开始追加）可以直接把 s 全清 0，跳过 build。",
           "递归深度是 ⌈log₂n⌉+1，n = 10⁵ 时 18 层，离爆栈差得远。"],
    brief="把 [1,n] 一路二分到单点，再自底向上合并"))

SEC.append(FN(
    "pushup（用两个儿子更新自己）",
    "void pushup(int p) { s[p] = s[p << 1] + s[p << 1 | 1]; }",
    [("p << 1", "左儿子 = 2p。位运算比乘法快，竞赛习惯写法。"),
     ("p << 1 | 1", "右儿子 = 2p+1。<code>|</code> 的优先级低于 <code>&lt;&lt;</code>，所以它等于 (p&lt;&lt;1)|1，正确；"
                    "写成 <code>p &lt;&lt; 1 + 1</code> 会被算成 p &lt;&lt; 2，直接跑去看错的节点。"),
     ("s[p] = ...", "只写“合并”这一步。求和用 +，求最值用 max，求 gcd 用 __gcd。"
                    "<b>这是整份代码里唯一随题目变化的一行</b>。"),
     ("调用时机", "build 的最后一行、update 的最后一行。query 只读不写，不调用。"),
     ("为什么不需要 l、r", "合并只用到两个儿子的值，用不上区间信息，所以只有一个参数。"),
     ("叶子不调用", "叶子在 build / modify 里直接赋值就 return 了，pushup 只作用于有儿子的节点。")],
    example=r'''#include <bits/stdc++.h>
using namespace std;

long long s[100];                        // 假设树已建好，2 是左儿子、3 是右儿子

void pushup(int p) { s[p] = s[p << 1] + s[p << 1 | 1]; }

int main() {
    s[2] = 10; s[3] = 5;                 // 左儿子 10，右儿子 5
    pushup(1);
    cout << s[1] << "\n";                // 15
    // 换成区间最大值，只改这一句：mx[p] = max(mx[p << 1], mx[p << 1 | 1]);
    return 0;
}''',
    notes=["pushup 是“儿子 → 自己”的方向，pushdown 是“自己 → 儿子”。两个搞反，答案要么偏小要么停在上一次的状态。",
           "维护和的时候不需要考虑 tag：apply 已经把 s[p] 改对了，pushup 照样成立。"],
    brief="s[p] = 左儿子 + 右儿子，唯一随题目变化的一行"))

SEC.append(FN(
    "query（区间查询）",
    "long long query(int p, int l, int r, int ql, int qr);",
    [("ql, qr", "询问区间，全程不变，递归时<b>不用减</b>，只在判断里用。"),
     ("ql <= l && r <= qr", "当前节点整段被包住 → 直接返回 s[p]，不再往下。这是 O(log n) 的唯一来源。"),
     ("if (ql <= mid)", "左儿子 [l, mid] 与询问区间有交集才进。判断是 <code>ql &lt;= mid</code>，"
                        "不是 <code>qr &lt;= mid</code>。"),
     ("if (qr > mid)", "右儿子同理。<b>这两个 if 互相独立</b>，因为询问区间可以同时伸进两边；"
                       "写成 else 就会漏掉跨中线的那一半。"),
     ("res 怎么合并", "求和用 res += ；求最值用 res = max(res, ...)，且 res 要初始化成 −∞。"),
     ("为什么不会死循环", "每次递归区间长度至少减半，走到 l == r 时一定被“完全包含”拦住并返回。"),
     ("复杂度", "每层最多 2 个节点是“部分相交”，一共 log n 层，所以访问 O(log n) 个节点。"),
     ("和 tag 的关系", "query 只读不写，所以不调 pushup；但如果树上有 tag，进入儿子前必须 pushdown。")],
    example=r'''#include <bits/stdc++.h>
using namespace std;

int n = 5;
long long a[6] = {0, 1, 5, 4, 2, 3}, s[24];

void build(int p, int l, int r) {
    if (l == r) { s[p] = a[l]; return; }
    int mid = (l + r) >> 1;
    build(p << 1, l, mid); build(p << 1 | 1, mid + 1, r);
    s[p] = s[p << 1] + s[p << 1 | 1];
}

long long query(int p, int l, int r, int ql, int qr) {
    if (ql <= l && r <= qr) return s[p];          // 整段被包住
    int mid = (l + r) >> 1;
    long long res = 0;
    if (ql <= mid) res += query(p << 1, l, mid, ql, qr);          // 左半边有交集
    if (qr > mid)  res += query(p << 1 | 1, mid + 1, r, ql, qr);  // 右半边有交集
    return res;
}

int main() {
    build(1, 1, n);
    cout << query(1, 1, n, 2, 4) << "\n";         // 5+4+2 = 11
    cout << query(1, 1, n, 1, 5) << "\n";         // 15
    return 0;
}''',
    notes=["线段树查询的区间<b>不会</b>像树状数组那样“相减”，因为每个节点只认自己那一段，不存在前缀和的概念。",
           "只有两个 if 都落空才是 bug：那种情况意味着进入了一个根本不相交的节点，说明上层的 if 写错了。"],
    brief="命中整段就返回，否则两边各自递归"))

SEC.append(FN(
    "懒标记 tag 与 pushdown（整段修改怎么不往下走）",
    "void apply(int p, int l, int r, long long v);\nvoid pushdown(int p, int l, int r);",
    [("tag[p]", "节点 p 那一段<b>每个数还欠着的加量</b>。有了它，区间加可以停在“整段被覆盖”的节点上，不改到叶子。"),
     ("apply(p, l, r, v)", "整段加 v：<code>s[p] += v * (r - l + 1)</code>（和增加 v 乘元素个数），"
                            "同时 <code>tag[p] += v</code>。这两句必须一起做。"),
     ("pushdown(p, l, r)", "把 tag[p] 分给两个儿子（对儿子各调一次 apply），然后把 <code>tag[p] = 0</code>。"),
     ("什么时候调", "<b>只要准备往儿子走，就必须先 pushdown</b>：update 的递归前、query 的递归前，一处都不能漏。"),
     ("if (!tag[p]) return;", "没有欠账立刻返回。这一行决定了常数大小，不能省。"),
     ("为什么只推一层就够", "懒标记是“按需结算”：只结算真正走过的那条路径，一条路径 O(log n) 层，总复杂度不变。"),
     ("为什么 s[p] 总是对的", "apply 同时改了 s[p] 和 tag[p]，所以节点自己的和永远准确；错的只是“儿子还没结账”。"),
     ("有乘法标记时", "像 P3373 那种“区间乘 + 区间加”，pushdown 必须<b>先乘后加</b>，顺序反了全错。")],
    example=r'''#include <bits/stdc++.h>
using namespace std;

long long s[100], tag[100];              // 设 1 号管 [1,5]，2、3 号是它的儿子

void apply(int p, int l, int r, long long v) {
    s[p] += v * (r - l + 1);             // 和增加 v 乘元素个数
    tag[p] += v;                         // 欠账记上
}

void pushdown(int p, int l, int r) {
    if (!tag[p]) return;                 // 没欠账，走人
    int mid = (l + r) >> 1;
    apply(p << 1, l, mid, tag[p]);       // 左儿子 [l, mid] 结账
    apply(p << 1 | 1, mid + 1, r, tag[p]);   // 右儿子 [mid+1, r] 结账
    tag[p] = 0;                          // 账分完了，自己清零
}

int main() {
    s[1] = 15; s[2] = 10; s[3] = 5;      // 和分别是 15、10、5
    apply(1, 1, 5, 2);                   // [1,5] 整段加 2
    cout << s[1] << " " << s[2] << "\n"; // 25 10：儿子还没结账
    pushdown(1, 1, 5);
    cout << s[2] << " " << s[3] << "\n"; // 16 9：左段 3 个数各加 2，右段 2 个数各加 2
    return 0;
}''',
    notes=["pushup 与 pushdown 是一对反向操作：前者“儿子 → 自己”，后者“自己 → 儿子”。写反了不报错，答案会停在旧值上。",
           "apply 里 <code>v * (r - l + 1)</code> 的乘号不能漏：漏了就是把“整段”当成“一个数”，"
           "n 越大错得越离谱，而样例常常只有很小的数，容易看不出来。"],
    brief="欠账记在自己头上，只在需要进儿子时才结算"))

# ---------------------------------------------------------------- 例题
SEC.append(P("模板题把上面四块骨头一次串起来：区间加、区间求和。这是线段树最常见的形态，"
             "其他变体基本只是换 pushup 那一行和 query 的合并方式。"))

SEC.append(EX("【模板】线段树 1", "P3372", "普及/提高-",
              "https://www.luogu.com.cn/problem/P3372",
              ["给定一个长度为 n 的数列，需要进行 m 次操作，操作有两种：",
               "<b>1 x y k</b>：把区间 [x, y] 内每个数加上 k；<b>2 x y</b>：输出区间 [x, y] 内每个数的和。",
               P("数据范围：1 ≤ n, m ≤ 10⁵，保证任意时刻数列中的数与答案在 64 位整数范围内。"),
               P("输入格式：第一行两个整数 n、m；第二行 n 个整数；接下来 m 行，每行为上述两种操作之一。<br>"
                 "输出格式：对每个操作 2，输出一行一个整数。")],
              sample="输入：\n5 5\n1 5 4 2 3\n2 2 4\n1 2 3 2\n2 3 4\n1 1 5 1\n2 1 4\n\n输出：\n11\n8\n20"))

SEC.append(IDEA("三件事：区间划分、懒标记、结算时机", [
    P("<b>① 朴素写法为什么死。</b>区间加如果老老实实改到每个叶子，一次操作 O(n)，m = 10⁵ 时 10¹⁰ 次加法。"
      "树状数组呢？区间加 + 区间和要用两个树状数组推公式 <code>Σdᵢ·(x−i+1)</code>，容易推错，而且换个询问（最值）就完全失效。"),
    P("<b>② 懒标记是“记账”。</b>当某个节点的区间<b>整段被修改范围包住</b>时，就没有必要往下走了："
      "把这笔加量记在 <code>tag[p]</code> 上，同时把 <code>s[p]</code> 改对。"
      "一次区间加只会停在 O(log n) 个这样的节点上，剩下的祖先用 pushup 重新算一遍。"),
    P("<b>③ 什么时候必须结算。</b>只有一件事会让“欠账”变成错误：<b>要往儿子走</b>。"
      "update 递归前、query 递归前，都必须 pushdown，把父亲的 tag 分给两个儿子。"
      "如果只在 update 里 pushdown 而 query 忘了——这题的样例就会从 20 变成 16（见下面的复现）。"),
    P("<b>④ 区间查询怎么动手。</b>询问 [2,4] 从根 [1,5] 开始：整段没被包住，切两半；"
      "左边 [1,3] 与 [2,4] 相交，进去继续切；右边 [4,5] 也相交，进去。"
      "最后整段被命中的节点是 [2,2]、[3,3]、[4,4]，三块拼起来正好是 [2,4]。"
      "<b>任何区间都能被切成 O(log n) 个这样的整段</b>，这就是它快的原因。"),
    P("<b>⑤ 规模估算。</b>n = 10⁵ 时树高 18 层。实测：单点查询访问 17 个节点，随机区间平均 43 个、最多 56 个。"
      "m = 10⁵ 次操作约 4×10⁶ 到 6×10⁶ 次节点访问，1 秒内轻松完成。"),
    P("<b>⑥ 数值。</b>用 long long：n = 10⁵、单个数到 10⁹ 时，一整个区间的和能到 10¹⁴，"
      "int 的上限 2.1×10⁹ 连零头都不够。s、tag、加法参数、返回值全部 long long，一个都别漏。"),
]))

SEC.append(C(r'''#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

const int N = 100005;
int n, m;
ll a[N], s[N << 2], tag[N << 2];       // s：区间和；tag：还没下推的加量

void pushup(int p) { s[p] = s[p << 1] + s[p << 1 | 1]; }

void build(int p, int l, int r) {
    if (l == r) { s[p] = a[l]; return; }        // 叶子
    int mid = (l + r) >> 1;
    build(p << 1, l, mid);
    build(p << 1 | 1, mid + 1, r);
    pushup(p);
}

void apply(int p, int l, int r, ll v) {         // 给整段 [l,r] 加 v
    s[p] += v * (r - l + 1);                    // 和增加 v 乘元素个数
    tag[p] += v;                                // 记账，等以后要用儿子时再结
}

void pushdown(int p, int l, int r) {            // 把欠账分给两个儿子
    if (!tag[p]) return;                        // 没欠账，省掉一切
    int mid = (l + r) >> 1;
    apply(p << 1, l, mid, tag[p]);
    apply(p << 1 | 1, mid + 1, r, tag[p]);
    tag[p] = 0;                                 // 账已分完，自己清零
}

void update(int p, int l, int r, int ql, int qr, ll v) {
    if (ql <= l && r <= qr) { apply(p, l, r, v); return; }   // 整段被包住就停手
    pushdown(p, l, r);                          // 要进儿子了，先结账
    int mid = (l + r) >> 1;
    if (ql <= mid) update(p << 1, l, mid, ql, qr, v);
    if (qr > mid)  update(p << 1 | 1, mid + 1, r, ql, qr, v);
    pushup(p);                                  // 儿子变了，自己重算
}

ll query(int p, int l, int r, int ql, int qr) {
    if (ql <= l && r <= qr) return s[p];        // 整段都要，直接返回
    pushdown(p, l, r);                          // 漏掉这一行，样例就会错
    int mid = (l + r) >> 1;
    ll res = 0;
    if (ql <= mid) res += query(p << 1, l, mid, ql, qr);
    if (qr > mid)  res += query(p << 1 | 1, mid + 1, r, ql, qr);
    return res;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cin >> n >> m;
    for (int i = 1; i <= n; ++i) cin >> a[i];
    build(1, 1, n);

    while (m--) {
        int op, x, y;
        ll k;
        cin >> op >> x >> y;
        if (op == 1) { cin >> k; update(1, 1, n, x, y, k); }
        else cout << query(1, 1, n, x, y) << "\n";
    }
    return 0;
}''', "完整可编译代码（C++17）"))

SEC.append(EXPLAIN("逐行拆解", [
    ("s[N << 2]", "N 左移 2 位 = N×4，就是 4n。按 2n 开在 n = 6 时就已越界（最大编号 13 > 12）。"),
    ("if (l == r) { s[p] = a[l]; return; }", "唯一的递归出口。p 与 l、r 一起才唯一确定一个节点，缺一个都不对。"),
    ("apply 里的 v * (r - l + 1)", "整段加 v，和增加 v 乘元素个数。漏掉乘号，n 越大错越多，小样例看不出来。"),
    ("tag[p] += v", "为什么是 += 而不是 =：同一个节点可能被多次整段加，欠账要累加。"),
    ("if (!tag[p]) return;", "pushdown 的第一行。绝大多数调用时 tag 是 0，这一行省掉大部分无谓操作。"),
    ("pushdown 在 update 里的位置", "必须在两次递归之前。写在之后，儿子已经算完了才结账，等于没结。"),
    ("if (ql <= mid) / if (qr > mid)", "两个独立判断。询问区间跨中线时两边都要进，写成 else if 直接漏一半。"),
    ("pushup(p) 在 update 末尾", "递归回来，儿子们的 s 都变了，必须重算 s[p]。漏掉它，祖先全部停在旧值。"),
    ("query 里的 pushdown", "最容易漏的一行：只在 update 写了 pushdown，查询时儿子少算了父亲那笔账 → WA。"),
]))

# ---------------------------------------------------------------- 换信息
SEC.append(P("模板题只用了“和”。真实的题目往往是别的信息，这时要改的其实只有三处："
             "<b>pushup 的合并方式</b>、<b>query 里 res 的合并方式与初值</b>、<b>tag 的含义与 apply 的写法</b>。"
             "下面换一个最常见的：区间最大值，配单点修改。"))

SEC.append(C(r'''#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

const int N = 100005;
const ll NEG = -(1LL << 60);           // 最值查询的中性元：比任何答案都小
ll mx[N << 2];

void pushup(int p) { mx[p] = max(mx[p << 1], mx[p << 1 | 1]); }   // 只换这一句

void modify(int p, int l, int r, int pos, ll v) {                 // 单点赋值
    if (l == r) { mx[p] = v; return; }
    int mid = (l + r) >> 1;
    if (pos <= mid) modify(p << 1, l, mid, pos, v);
    else            modify(p << 1 | 1, mid + 1, r, pos, v);
    pushup(p);                        // 儿子变了，自己跟着变
}

ll queryMax(int p, int l, int r, int ql, int qr) {
    if (ql <= l && r <= qr) return mx[p];
    int mid = (l + r) >> 1;
    ll res = NEG;
    if (ql <= mid) res = max(res, queryMax(p << 1, l, mid, ql, qr));
    if (qr > mid)  res = max(res, queryMax(p << 1 | 1, mid + 1, r, ql, qr));
    return res;
}

int main() {
    int n = 6;
    ll a[7] = {0, 3, 1, 4, 1, 5, 9};
    for (int i = 1; i <= n; ++i) modify(1, 1, n, i, a[i]);         // 逐个位置建树
    cout << queryMax(1, 1, n, 2, 4) << "\n";                       // max(1,4,1) = 4
    modify(1, 1, n, 3, 8);                                        // a[3] 改成 8
    cout << queryMax(1, 1, n, 2, 4) << "\n";                       // max(1,8,1) = 8
    return 0;
}''', "换成区间最大值：单点修改 + 区间查询（不需要 tag）"))

SEC.append(P("注意这份代码里<b>没有 tag、没有 pushdown</b>。因为修改是单点的，一路走到叶子，"
             "不存在“整段还没结算”的情况。单点修改的题，懒标记整套都可以删掉。"
             "反过来，只要支持区间修改，就必须有 tag；而 tag 的含义决定了 apply 怎么写："
             "<b>区间加</b>是 <code>s[p] += v*(len)</code>、<b>区间赋值</b>是 <code>s[p] = v*(len)</code>，"
             "<b>区间取反</b>是 <code>s[p] = len − s[p]</code>。"))

SEC.append(AFTER("什么时候该写线段树", [
    P("<b>三个信号同时出现就该写它：</b>① 有修改也有询问，且修改和询问都作用在<b>区间</b>上；"
      "② 信息可以“合并”（和、最值、gcd、最大子段和、出现次数）；③ n、m 到 10⁵，暴力撑不住。"),
    P("<b>常见变体只要换三处：</b>"),
    T(["题目要什么", "pushup 写法", "query 的合并", "tag 含义"], [
        ["区间加 + 区间和", "s = L + R", "res += ...", "加量 v"],
        ["区间加 + 区间最值", "mx = max(L, R)", "res = max(...)", "加量 v"],
        ["区间赋值 + 区间和", "s = L + R", "res += ...", "赋值成 v"],
        ["区间取反 + 区间和", "s = L + R", "res += ...", "翻转次数"],
        ["区间最大子段和", "sum / pre / suf / best 四量合并", "四量合并", "加量 v（best 也加 len·v）"],
    ]),
    P("<b>还有几个名字要认得。</b>把下标当成“值域”建的树叫<b>权值线段树</b>，能在 O(log n) 找第 k 小；"
      "只建用到的那几个节点叫<b>动态开点</b>；两棵树按节点合并叫<b>线段树合并</b>。"
      "这三样都是本节代码加一两句话就变形出来的，不必重新学。"),
    P("<b>常数提示。</b>递归线段树比树状数组慢 3~5 倍。n、m 都是 10⁵ 时完全够用；"
      "到了 10⁶ 或时限 0.5 秒，才需要考虑非递归（zkw）写法。"),
]))

SEC.append(WARN("这一节的 7 个坑，按症状记", [
    "数组按 n 或 2n 开：n = 6 时最大编号已是 13，n = 10⁵ 时是 262141 → <b>RE</b>（越界写坏别的变量）"
    " 或随机 <b>WA</b>。一律开 4n，别算。",
    "只在 update 里 pushdown，query 里忘了 → <b>WA</b>。症状：先加后查的数据全错，"
    "而这题样例最后一个答案会从 20 变成 16。",
    "update 里把 <code>if (qr &gt; mid)</code> 写成 <code>else</code>：询问区间跨中线时只进了一边 → <b>WA</b>，"
    "小数据可能蒙对。",
    "apply 里写成 <code>s[p] += v</code>，漏了乘 (r−l+1)：把“整段”当成“一个数” → <b>WA</b>，"
    "区间越长错得越多。",
    "把 <code>p &lt;&lt; 1 | 1</code> 写成 <code>p &lt;&lt; 1 + 1</code>：因为 + 优先级高于 &lt;&lt;，"
    "它等于 p&lt;&lt;2，跑到完全不相干的节点 → <b>WA</b> 或 <b>RE</b>。",
    "s 用 int：区间和到 10¹⁴ → 溢出成负数 → <b>WA</b>，样例全过（数太小）。",
    "多组数据不清 tag 和 s → 第二组开始全错 → <b>WA</b>。memset 两个数组，或者把 4n 个位置清 0。",
]))

SEC.append(REPRO("关掉页面，把 P3372 的六个函数（pushup / build / apply / pushdown / update / query）默写一遍，"
                "提交确认样例输出 11、8、20。",
                "改一改①：删掉 <code>query</code> 里那一行 <code>pushdown(p, l, r)</code>，再跑样例。"
                "前两个答案仍是 11 和 8，第三个会变成 <b>16</b>（正确是 20）——少掉的 4 正是节点 1 欠下的账。",
                "改一改②：把 <code>s</code> 改成 <code>int</code>，自己造一组“n = 10、每个数 10⁹、全区间求和”的数据，"
                "看输出为什么是负数。",
                "改一改③：把 <code>query</code> 里第二个 <code>if (qr &gt; mid)</code> 改成 <code>else</code>，"
                "查询 [2, 4] 会返回 <b>5</b>（正确是 11）：跨中线的右半边 [3,3]、[4,4] 全被跳过了。"))

# ---------------------------------------------------------------- 数学补给
M = MATH("4n 是怎么来的，O(log n) 又是怎么来的", [
    P("<b>先数节点。</b>n 个叶子，每个内部节点恰好有两个儿子，所以内部节点 n−1 个，整棵树 2n−1 个节点。"
      "如果按“节点个数”开数组，2n 就够。"),
    P("<b>但堆式编号会跳号。</b>编号是 2p、2p+1，当 n 不是 2 的幂时最后一层不满，"
      "空出来的位置仍然占着编号。实测最大编号："),
    T(["n", "最大编号", "2n", "4n"], [
        ["6", "13", "12（不够）", "24"],
        ["10", "25", "20（不够）", "40"],
        ["100", "253", "200（不够）", "400"],
        ["100000", "262141", "200000（不够）", "400000"],
    ]),
    P("<b>上界证明。</b>设 2^(k−1) &lt; n ≤ 2^k，则树高最多 k+1 层，编号最大不超过 2^(k+1)−1。"
      "又因为 n &gt; 2^(k−1)，所以 2^(k+1) = 4·2^(k−1) &lt; 4n。"
      "即<b>最大编号一定小于 4n</b>，这就是所有人写 <code>N &lt;&lt; 2</code> 的原因。"),
    P("<b>再算高度。</b>每递归一层，区间长度至少减半，所以层数 = ⌈log₂n⌉ + 1。"
      "n = 10⁵ 时 ⌈log₂10⁵⌉ = 17，共 18 层。递归深度 18，爆栈是不可能的事。"),
    P("<b>最后算查询为什么是 O(log n)。</b>关键观察：<b>同一层里，最多只有 2 个节点是“部分相交”的</b>。"
      "因为部分相交意味着节点区间里有询问区间的端点 ql 或 qr；而同一层的节点区间互不相交，"
      "所以含 ql 的最多一个，含 qr 的最多一个，合起来最多两个。"
      "每层 2 个、共 log n 层，于是访问节点数不超过 4⌈log₂n⌉。"),
    P("实测对得上：n = 10⁵ 时单点查询访问 17 个节点（正好等于高度），"
      "随机区间平均 43 个、最坏 56 个，而理论上界 4×17 = 68。"
      "m = 10⁵ 次操作因此只有几百万次节点访问，1 秒的时限绰绰有余。"),
])

THINK = [
    "把区间和换成区间<b>异或</b>和，tag 还能记成“加 v”吗？如果操作是“区间取反”，apply 该怎么写？",
    "如果同时有“区间加”和“区间赋值”两种标记，一个 tag 够不够？pushdown 里的顺序该怎么定？"
    "（提示：赋值会把之前的加量全部作废）",
    "求区间最大子段和时，一个节点要维护几个量？为什么只存 best 不够，还必须存 sum、前缀最大值、后缀最大值？",
    "n = 10⁶ 时 4n 个 long long 要多少内存？如果内存限制 256 MB，还能开几棵树？这时该怎么压空间？",
    "单点修改的题为什么可以把 tag 和 pushdown 整套删掉？如果保留它们，会多出多少无用的操作？",
    "树状数组和线段树都能做“单点改 + 区间和”。给你一道题，你用哪两条依据决定选谁？",
]

THINK_A = [
    "不能。tag 的语义必须换成“这一段每个数还要异或上 t”——加 v 对异或和没有闭式（加法不分配于异或），"
    "所以“区间加 + 区间异或和”不是写法问题，是根本没有简单的懒标记。"
    "异或标记的 apply 要写 <code>s[p] ^= ((r - l + 1) &amp; 1 ? t : 0)</code>，因为 t 在这 len 个数里出现 len 次，偶数次自相抵消；"
    "同时 <code>tag[p] ^= t</code>，不是 <code>+= t</code>（异或自逆，两次等于没做）。"
    "区间取反是 t = 1 的特例；若节点存的是“1 的个数”，apply 就直接写 <code>s[p] = (r - l + 1) - s[p]</code>、<code>tag[p] ^= 1</code>，正是挑战题 P2574 的写法。"
    "最常见的错路是照抄加法的 apply 写成 <code>s[p] ^= v</code>：段长是偶数时这一位本该抵消，却被留了下来，"
    "而小样例的段长常常是奇数，本地根本看不出来。",
    "一个不够，要两个：<b>赋值标记</b>（赋过没有、赋成几）和<b>加量标记</b>。规则只有一条——赋值会把之前所有的加量作废："
    "打赋值标记时把 add 清 0；打加法标记时，如果当前有赋值标记就把赋值值 += v，否则 add += v。"
    "pushdown 的顺序是<b>先赋值、后加法</b>，这正是两笔账真正发生的时间顺序；反过来推，等于把后来的加法加在了旧值上。"
    "常见错路是把 setv 和 add 当两个互不干扰的数组各推各的，于是被赋过值的节点还留着一笔旧加法，越查越偏；"
    "另一个错路是 pushdown 里只推了一个、忘记把父节点的另一个也清掉，同一笔账被结算两次。",
    "要 4 个量：<code>sum</code>、<code>pre</code>（最大前缀和）、<code>suf</code>（最大后缀和）、<code>best</code>（最大子段和）。"
    "合并是 <code>sum = L.sum + R.sum</code>、<code>pre = max(L.pre, L.sum + R.pre)</code>、"
    "<code>suf = max(R.suf, R.sum + L.suf)</code>、<code>best = max(L.best, R.best, L.suf + R.pre)</code>。"
    "只存 best 不够，因为最优段可能<b>跨中线</b>，它等于左后缀加右前缀；而 pre、suf 自己的合并又要用到 sum，缺一个就还原不出跨中线那项。"
    "常见错路是写成 <code>best = max(L.best, R.best)</code>，全正数时答案偏小；"
    "或者把 pre 的初值取成 0 而不是 −∞，题目要求非空子段时会选出空段，答案偏大。",
    "4n = 4×10⁶ 个 long long，每个 8 字节，<b>一棵树 32 MB</b>；带 tag 就是两倍，64 MB。"
    "256 MB 下：只放 s 能放 8 棵，s 和 tag 一起只能放 4 棵。"
    "压空间有三条路：① 别用堆式编号，改成 build 时按访问顺序发新编号，真实节点只有 2n−1 个，数组开 2n 直接省一半（迭代 zkw 写法也是 2n）；"
    "② 数值装得下就用 int，再省一半（4n×4B = 16 MB）；③ 只有单点修改的题把 tag 整个删掉。"
    "常见错路是听说“线段树必须开 4n”就照抄到底，然后 n = 10⁶ 时三棵树直接 MLE——4n 是堆式编号的上界，不是节点数的下界。",
    "因为 tag 存在的唯一理由是“整段被改、但儿子还没跟着改”。单点修改一路递归到叶子，路径上每个节点都被真正走过、儿子也都被递归改对了，"
    "从来不会留下欠账，所以 tag 恒为 0，pushdown 的第一行 <code>if (!tag[p]) return;</code> 每次都立刻返回。"
    "保留它们不会算错，只是白花：每次 update / query 在每个非叶节点多一次函数调用加一次判空，深度 18 层，10⁵ 次操作就是约 1.8×10⁶ 次空调用，"
    "还要多占一个 4n 的 tag 数组（10⁵ 时 3.2 MB）。"
    "常见错路是把结论反过来用——“单点修改不用 tag，那区间修改也能删”，那必错；"
    "另一头是把单点修改也写成每次先 pushdown 一遍，纯属浪费，因为根本没有账可结。",
    "两条依据：① <b>信息有没有逆运算</b>——和、异或、计数能靠两个前缀相减，树状数组 12 行就够；"
    "最值、gcd、最大子段和没法把前一段“减掉”，只能上线段树。"
    "② <b>常数与规模</b>——n = m = 5×10⁵ 时树状数组约 10⁷ 次加法、0.1 秒量级，线段树慢 3~5 倍；到了 10⁶ 或时限 0.5 秒，这个差距就决定过不过。"
    "另外两条附加项：要区间修改时，树状数组得推两个树状数组的式子，线段树直接做；要“第一个前缀和 ≥ k”的位置时，树状数组上二分比线段树好写。"
    "常见错路是“线段树更通用所以无脑上”，明明 12 行能过的题写成 40 行还慢三倍；"
    "反过来更危险：看到区间最值还硬套 sum 相减，代码能编译能跑，答案是错的。",
]

CHECK = [
    "能默写 build / pushup / update / query / pushdown 五个函数，并说出每个的递归出口。",
    "能画出 n = 5 的线段树，写出每个节点管辖的区间和编号。",
    "能解释为什么数组要开 4n，并说出 n = 6 时最大编号是 13。",
    "能说清 pushdown 必须在哪两个地方调用，以及漏掉 query 里的那次会错成什么样。",
    "能解释“每层最多 2 个部分相交节点”，从而说明区间查询是 O(log n)。",
    "能把区间和改成区间最大值，指出要改的三处。",
]

CH2 = CH(
    "XOR 的艺术", "P2574", "普及+/提高", "https://www.luogu.com.cn/problem/P2574",
    [P("有一个长度为 n 的伤害串，只含字符 <code>0</code> 和 <code>1</code>，下标从 1 开始。"
       "给定区间 [l, r]，这段区间的伤害定义为其中字符 <code>1</code> 的个数。"),
     P("有 m 次操作，每次给出 op、l、r：<b>op = 0</b> 表示把 [l, r] 里的 <code>0</code> 全变成 <code>1</code>、"
       "<code>1</code> 全变成 <code>0</code>；<b>op = 1</b> 表示询问 [l, r] 里 <code>1</code> 的个数。"),
     P("输入格式：第一行两个整数 n、m（2 ≤ n, m ≤ 2×10⁵）；第二行一个长度为 n 的 01 串；"
       "接下来 m 行，每行三个整数 op、l、r（0 ≤ op ≤ 1，1 ≤ l ≤ r ≤ n）。"),
     P("输出格式：对每个 op = 1 的操作，输出一行一个整数。"),
     P("<b>样例输入</b><br><code>10 6<br>1011101001<br>0 2 4<br>1 1 5<br>0 3 7<br>1 1 10<br>0 1 4<br>1 2 6</code><br>"
       "<b>样例输出</b><br><code>3<br>6<br>1</code><br>"
       "样例解释：第一次翻 [2,4] 后串变成 1100101001，查询 [1,5] 得 3；翻 [3,7] 后变成 1111010001，"
       "查询 [1,10] 得 6；再翻 [1,4] 后变成 0000010001，查询 [2,6] 得 1。")],
    hint=["n、m 都到 2×10⁵。老老实实把 [l, r] 一个字符一个字符翻是 O(nm) = 4×10¹⁰，先想清楚暴力死在哪。",
          "线段树每个节点存「这一段里 1 的个数」。整段取反之后，这个数会变成什么？"
          "只需要长度就能算出来——这就是 apply 的全部内容。",
          "取反标记不必记「翻了几次」，只记<b>奇偶</b>：翻两次等于没翻。所以 tag 用一个 bool，下推时异或。"],
    idea=["<b>① 暴力为什么不行。</b>一次区间取反是 O(n)，m = 2×10⁵ 时 4×10¹⁰ 次操作。"
          "要支持「区间改 + 区间问」，就是线段树 + 懒标记的场合。",
          "<b>② 节点存什么。</b>sum[p] = 这一段里 '1' 的个数。它可合并（左 + 右），所以 pushup 还是加法，一个字都不用改。",
          "<b>③ 整段取反怎么改。</b>取反后 1 的个数 = 总长度 − 原来的个数，即 "
          "<code>sum[p] = (r − l + 1) − sum[p]</code>；同时把标记翻一下：<code>tag[p] ^= 1</code>。"
          "两件事必须一起做——少了第一件，节点自己的值就不对；少了第二件，儿子永远不知道要翻。",
          "<b>④ 为什么标记能只记奇偶。</b>取反是自逆运算：翻两次等于没翻。"
          "所以「欠了几次」只需要一个 bit，下推时用异或，而不是加法。",
          "<b>⑤ pushdown 的时机没有变。</b>只要准备往儿子走，就先结算：update 递归前、query 递归前各一次，"
          "漏掉 query 里那次，查询就会读到没翻过的儿子。",
          "<b>⑥ 复杂度。</b>O((n + m) log n) ≈ 2×10⁵ × 18 ≈ 3.6×10⁶ 次节点访问，1 秒内几百万次，稳过。"],
    code=r'''#include <bits/stdc++.h>
using namespace std;

const int N = 200005;
int n, m;
int s[N << 2];                 // s[p]：这一段里 '1' 的个数
bool tag[N << 2];              // tag[p]：这一段整体还要翻转几次（奇偶）
int a[N];

void build(int p, int l, int r) {
    if (l == r) { s[p] = a[l]; return; }
    int mid = (l + r) >> 1;
    build(p << 1, l, mid);
    build(p << 1 | 1, mid + 1, r);
    s[p] = s[p << 1] + s[p << 1 | 1];
}

void apply(int p, int l, int r) {   // 整段翻转：1 的个数变成补集
    s[p] = (r - l + 1) - s[p];
    tag[p] ^= 1;                    // 翻转两次等于没翻，所以用异或
}

void pushdown(int p, int l, int r) {
    if (!tag[p]) return;
    int mid = (l + r) >> 1;
    apply(p << 1, l, mid);
    apply(p << 1 | 1, mid + 1, r);
    tag[p] = 0;
}

void update(int p, int l, int r, int ql, int qr) {
    if (ql <= l && r <= qr) { apply(p, l, r); return; }
    pushdown(p, l, r);
    int mid = (l + r) >> 1;
    if (ql <= mid) update(p << 1, l, mid, ql, qr);
    if (qr > mid)  update(p << 1 | 1, mid + 1, r, ql, qr);
    s[p] = s[p << 1] + s[p << 1 | 1];
}

int query(int p, int l, int r, int ql, int qr) {
    if (ql <= l && r <= qr) return s[p];
    pushdown(p, l, r);
    int mid = (l + r) >> 1, res = 0;
    if (ql <= mid) res += query(p << 1, l, mid, ql, qr);
    if (qr > mid)  res += query(p << 1 | 1, mid + 1, r, ql, qr);
    return res;
}

int main() {
    scanf("%d%d", &n, &m);
    char ch[N];
    scanf("%s", ch + 1);
    for (int i = 1; i <= n; ++i) a[i] = ch[i] - '0';
    build(1, 1, n);

    while (m--) {
        int op, l, r;
        scanf("%d%d%d", &op, &l, &r);
        if (op == 0) update(1, 1, n, l, r);
        else printf("%d\n", query(1, 1, n, l, r));
    }
    return 0;
}''',
    explain=[
        ("s[p] = (r - l + 1) - s[p];",
         "整段取反：1 变 0、0 变 1，所以新的 1 的个数 = 总长度 − 原来的个数。写成 <code>+=</code> 就完全不是取反了。"),
        ("tag[p] ^= 1;",
         "取反是自逆运算，翻两次等于没翻，所以标记按位异或维护奇偶；写成 <code>+= 1</code> 时翻两次会留下 2，"
         "下推时会白翻一轮。"),
        ("if (!tag[p]) return;", "没有欠账立刻返回。绝大多数调用 tag 是 0，这一行决定了常数。"),
        ("update 与 query 里各有一句 pushdown(p, l, r);",
         "只要准备往儿子走就先结算。只写 update 那一处，查询会读到还没翻的儿子——这是本节最容易漏的一行。"),
        ("s[p] = s[p << 1] + s[p << 1 | 1];",
         "取反不改变「可合并」这件事，所以 pushup 仍然是加法。换别的信息才需要改这一行。"),
        ("scanf(\"%s\", ch + 1);",
         "整个 01 串一次读进数组，下标从 1 开始，和题目一致；再拆成 a[i] = ch[i] − '0' 建树。"),
    ],
    pitfalls=["apply 里写成 <code>s[p] += (r - l + 1)</code>：取反不是加法，区间一长答案就飞。",
              "tag 用 <code>+= v</code> 而不是 <code>^= 1</code>：翻两次标记变成 2，逻辑上等于没翻，但代码里通常会误判成「还要翻」→ WA。",
              "只在 update 里 pushdown，query 里忘了：查询结果漏掉祖先欠下的翻转。",
              "数组开成 <code>N</code>：n = 2×10⁵ 时最大节点编号接近 5.2×10⁵，必须开 4n。"],
    sample="输入：\n10 6\n1011101001\n0 2 4\n1 1 5\n0 3 7\n1 1 10\n0 1 4\n1 2 6\n输出：\n3\n6\n1",
)

CH = CH(
    "最大数", "P1198", "普及/提高-", "https://www.luogu.com.cn/problem/P1198",
    [P("维护一个数列，初始为空，需要支持 m 次操作："),
     P("<b>A n</b>：把 n 加上 t 之后对固定常数 D 取模（t 是最近一次询问的答案，若还没问过则 t = 0），"
       "把结果追加到数列末尾。<b>Q L</b>：询问当前数列中<b>最后 L 个数</b>的最大值，输出它，并把它作为新的 t。"),
     P("输入格式：第一行两个整数 m、D；接下来 m 行，每行一个字符（A 或 Q）和一个整数。<br>"
       "输出格式：对每个 Q 操作，输出一行一个整数。"),
     P("数据范围：1 ≤ m ≤ 2×10⁵，1 ≤ D ≤ 2×10⁹，保证 L 不超过当前数列长度；每次给出的整数在 64 位整数范围内，可能为负。")],
    hint=["插入只会发生在末尾，位置一旦确定就再也不会变——所以“最后 L 个”永远是数组里连续的一段。",
          "既然最多插入 m 次，那位置最多只有 m 个。能不能先开一棵长度为 m 的空树，边插边改？",
          "这题只需要两个操作：单点赋值、区间最大值。想想为什么一个 tag 都不需要。"],
    idea=["<b>离线看出上界。</b>共 m 次操作，每次最多插入一个数，所以数列长度永远 ≤ m。"
          "于是可以直接建一棵管 [1, m] 的线段树，初始全是 0，等着被填。",
          "<b>在线维护。</b>用 <code>tail</code> 记当前长度。<b>A n</b>：<code>++tail</code>，"
          "把 <code>((n + t) % D + D) % D</code> 单点赋值到 <code>tail</code> 位置；"
          "<b>Q L</b>：查询 <code>[tail − L + 1, tail]</code> 的最大值，更新 <code>t</code> 并输出。",
          "<b>为什么正确。</b>插入位置的顺序就是数列顺序；已经插入的部分之后不再改动，"
          "而询问的区间一定落在 <code>[1, tail]</code> 内，全是已插入的有效值，树里的 0 初值永远不会被问到。",
          "<b>为什么不需要 tag。</b>修改是单点的，一路递归到叶子，中间没有任何“整段还没结算”的状态。"
          "把 pushdown 和 tag 全删掉，代码更短也更快。",
          "<b>易错的数值细节。</b><code>n + t</code> 可能超过 int（D 到 2×10⁹），全部用 long long；"
          "取模后可能为负，要 <code>((n + t) % D + D) % D</code> 才能落回 [0, D)。"],
    code=r'''#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

const int N = 200005;
int cap;                              // 树的长度 = 操作总数（最多插入这么多次）
ll D, mx[N << 2];                     // 插入值都落在 [0, D)，所以 0 是安全的初值

void modify(int p, int l, int r, int pos, ll v) {        // 单点赋值
    if (l == r) { mx[p] = v; return; }
    int mid = (l + r) >> 1;
    if (pos <= mid) modify(p << 1, l, mid, pos, v);
    else            modify(p << 1 | 1, mid + 1, r, pos, v);
    mx[p] = max(mx[p << 1], mx[p << 1 | 1]);             // 儿子变了，自己跟着变
}

ll queryMax(int p, int l, int r, int ql, int qr) {
    if (ql <= l && r <= qr) return mx[p];                // 整段被包住
    int mid = (l + r) >> 1;
    ll res = 0;                                          // 非负数，用 0 当"没有"
    if (ql <= mid) res = max(res, queryMax(p << 1, l, mid, ql, qr));
    if (qr > mid)  res = max(res, queryMax(p << 1 | 1, mid + 1, r, ql, qr));
    return res;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int m;
    cin >> m >> D;
    cap = m;                                         // 最多插 m 次，树不用更长
    int tail = 0;                                    // 当前数列长度
    ll t = 0;

    while (m--) {
        char op;
        ll n;
        cin >> op >> n;
        if (op == 'A') {
            ll v = ((n + t) % D + D) % D;             // 先加 t，再取模，负数也落进 [0,D)
            modify(1, 1, cap, ++tail, v);             // 追加到最后一个位置
        } else {
            int L = (int)n;
            t = queryMax(1, 1, cap, tail - L + 1, tail);   // 最后 L 个
            cout << t << "\n";
        }
    }
    return 0;
}''',
    explain=[
        ("cap = m", "把操作总数存下来当树的长度。后面 <code>while (m--)</code> 会把 m 用掉，所以必须提前保存。"),
        ("mx[N << 2]", "N = 2×10⁵，4N = 8×10⁵ 个 long long，约 6.4 MB，安全。"),
        ("((n + t) % D + D) % D", "C++ 的 % 对负数取模结果仍为负，加一个 D 再取模才能保证落在 [0, D)。"),
        ("modify(1, 1, cap, ++tail, v)", "先 ++tail 再传，参数求值顺序在这里无歧义（只有一个自增）。"),
        ("mx[p] = max(mx[p << 1], mx[p << 1 | 1])", "pushup 直接写在 modify 末尾，省一个函数调用。换信息只改这一句。"),
        ("queryMax(1, 1, cap, tail - L + 1, tail)", "末尾 L 个 = 区间 [tail−L+1, tail]。保证 L ≤ tail，所以不会越界。"),
        ("ll res = 0", "所有插入值都 ≥ 0，用 0 当“没有”是安全的；若允许负数，必须用 −∞ 起头。"),
    ],
    pitfalls=["漏掉 <code>cap = m</code>，直接拿被 <code>while (m--)</code> 消耗掉的 m 当右端点 → 树的范围变成 0，"
              "行为完全错乱。",
              "取模写成 <code>(n + t) % D</code>：n 可能为负，结果也为负，插进去的值破坏“非负”前提 → WA。",
              "Q 操作只 <code>cout</code> 忘了把答案写回 <code>t</code>：之后的每个 A 都少加了上一次的答案 → 从第二个 A 起全错。",
              "把查询区间写成 <code>[tail − L, tail]</code>：多算了前一个数，答案偏大。",
              "数组开成 <code>mx[N]</code> 而不是 <code>mx[N &lt;&lt; 2]</code>：堆式编号最大到 4m 附近 → 越界 → RE。"],
)

LESSONS = [LESSON(
    47, "线段树",
    "把区间二分到底，每个节点维护自己那一段的信息：build 自底向上，query 命中整段就返回，"
    "区间修改靠懒标记停在整段上、要进儿子时才 pushdown。一份代码，换掉 pushup 和合并方式就能做和、最值、最大子段和。",
    80, ["线段树", "懒标记", "区间合并"], "提高",
    SEC, math=M, think=THINK, think_a=THINK_A, check=CHECK, challenge=CH, challenge2=CH2,
    refs=["《算法竞赛进阶指南》0x43 线段树（懒标记、标记下传顺序）",
          "《算法竞赛试炼场：洛谷300题精析》线段树专题",
          "洛谷 P3372、P1198 题解区的高赞实现"],
)]
