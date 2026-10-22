# -*- coding: utf-8 -*-
"""第 48 节 · 单调栈与单调队列"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dsl import *  # noqa

SEC = []

SEC.append(P("单调栈和单调队列解决同一类问题：<b>在滑动窗口里随时拿到最值</b>。"
             "手法只有一句——把“永远不可能成为答案”的元素当场删掉。删得干净，"
             "每个元素只进一次、出一次，均摊 O(n)。"))

SEC.append(Q("单调栈维护“还没等到答案的下标”；单调队列维护“当前窗口里还可能成为最值的下标”。"
             "两者都只做两件事：入队前弹掉比自己差的，入队后弹掉过期的。"))

SEC.append(T(["任务", "结构", "弹出条件", "均摊代价"], [
    ["右边第一个更大元素", "单调栈，栈内值不增", "栈顶值 &lt; 当前值就弹", "O(n)"],
    ["柱状图中最大矩形", "单调栈，左右各跑一遍", "栈顶值 ≥ 当前值就弹", "O(n)"],
    ["长度 k 的窗口最值", "单调队列，队内值单调", "队尾更差就弹 + 队头过期就弹", "O(n)"],
    ["f[i] = a[i] + max f[j]", "单调队列，窗口 [i−R, i−L]", "队尾 f 更小就弹 + 队头出窗", "O(n)"],
]))

SEC.append(P("四段代码是同一份骨架：<code>while 弹队尾 → push 当前 → while 弹队头 → 用队头更新答案</code>。"
             "真正的差别只有两处：<b>弹队尾用 &lt; 还是 ≤</b>，以及<b>队头什么时候算过期</b>。"
             "这两处写错，样例照样过，随机数据一片 WA。"))

# ---------------------------------------------------------------- 例题
SEC.append(EX("【模板】单调栈", "P5788", "普及/提高-", "https://www.luogu.com.cn/problem/P5788",
              ["给出项数为 n 的整数数列 a<sub>1</sub>, a<sub>2</sub>, …, a<sub>n</sub>。"
               "定义 f(i) 为数列中第 i 个元素<b>之后</b>第一个<b>大于</b> a<sub>i</sub> 的元素的下标；"
               "若不存在这样的元素，则 f(i) = 0。",
               "输入：第一行一个整数 n（1 ≤ n ≤ 3×10<sup>6</sup>）；"
               "第二行 n 个整数 a<sub>1..n</sub>（1 ≤ a<sub>i</sub> ≤ 10<sup>9</sup>）。",
               "输出：一行 n 个整数 f(1), f(2), …, f(n)，相邻两数之间用一个空格隔开。"],
              sample="输入：\n5\n1 4 2 3 5\n输出：\n2 5 4 5 0"))

SEC.append(P("写代码前先把两个工具拆开。它们都很短，但每一条格式要求背后都对应着一类 WA。"))

SEC.append(FN(
    "deque（双端队列）",
    "deque<int> q;\nq.push_back(x);  q.pop_back();\nq.push_front(x); q.pop_front();\nq.front();  q.back();  q.empty();  q.size();",
    [("&lt;deque&gt;", "&lt;bits/stdc++.h&gt; 已包含。声明写成 <code>deque&lt;int&gt; q;</code> 或 <code>deque&lt;pair&lt;int,int&gt;&gt; q;</code>。"),
     ("push_back / pop_back", "队尾进、队尾出。单调队列用它们维护“值单调”这一侧。"),
     ("push_front / pop_front", "队头进出。这是它和 stack 的唯一区别：两端都能动，所以能弹掉过期元素。"),
     ("front() / back()", "O(1) 取两端。单调队列的队头永远是当前窗口的最值下标。"),
     ("必须存下标", "存值就无法回答“这个元素还在不在窗口里”。窗口滑动时只靠下标判断过期。"),
     ("q[i] 随机访问", "deque 支持 O(1) 下标访问，但单调队列只用两端，用 q[i] 遍历反而慢。"),
     ("底层结构", "分段连续存储，每段定长；两端增删都是 O(1)，比 vector 多一层指针，常数略大。"),
     ("什么时候用手写数组", "窗口长度和值域都固定时，用 <code>int q[N], head, tail</code> 更快（无函数调用、无内存分配）。")],
    example=r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    int a[] = {5, 3, 8, 1};        // 下标 0..3
    deque<int> q;                  // 只存下标，值从队头到队尾单调递增

    for (int i = 0; i < 4; ++i) {
        while (!q.empty() && a[q.back()] >= a[i]) q.pop_back();  // 队尾更差的永久退休
        q.push_back(i);
        cout << a[q.front()] << " ";   // 队头就是当前最小值：5 3 3 1
    }
    cout << "\n";
    return 0;
}''',
    notes=["在空的 deque 上调用 <code>front()</code> / <code>back()</code> 是未定义行为，通常读到垃圾值。"
           "每一处 front() 之前都要想清楚“它会不会是空的”。",
           "deque 虽然支持 q[i]，但它的迭代器比 vector 重；频繁按下标遍历时用 vector。",
           "本节所有题目都可以用 deque 实现，熟练后再换成手写数组压常数。"],
    brief="两端都能进出的队列，单调队列的容器"))

SEC.append(FN(
    "数组模拟栈：stk[++top]",
    "int stk[N], top = 0;\nstk[++top] = i;        // 入栈\nint t = stk[top];      // 取栈顶\n--top;                 // 出栈\nif (top == 0) { /* 空 */ }",
    [("top = 0 表示空栈", "元素存在 stk[1..top]，top 同时就是栈的大小。stk[0] 永远空着，可以当值为 0 的哨兵。"),
     ("stk[++top] = i", "先加后写：第一个元素落在 stk[1]。写成 stk[top++] 会让下标从 0 开始，后续判空要小心。"),
     ("a[stk[top]]", "栈里存下标，随时能取回原值、原位置。存值就丢了位置信息，答案要求下标时直接报废。"),
     ("--top", "出栈只减指针，O(1)，不动任何内存。"),
     ("比 std::stack 快 2~3 倍", "std::stack 的 top()、push()、pop() 是三次函数调用，且无法按下标回溯；"
                                 "3×10<sup>6</sup> 的题手写数组明显更快。"),
     ("栈必须是全局或 static", "n = 3×10<sup>6</sup> 时栈数组 12 MB，开在 main 里会让栈帧过大直接爆栈；"
                               "开成全局变量（在 BSS 段）最稳。")],
    example=r'''#include <bits/stdc++.h>
using namespace std;

const int MAXN = 3000005;
int stk[MAXN], top = 0;              // 全局：3e6 个 int 进静态区，不占调用栈

int main() {
    int a[] = {0, 5, 3, 8, 1};       // 1 基下标，a[0] 空着不用
    int n = 4;
    for (int i = 1; i <= n; ++i) {
        while (top > 0 && a[stk[top]] < a[i]) --top;   // 弹掉挡不住当前元素的
        stk[++top] = i;                                // 自己进栈
        cout << "i=" << i << "  栈内值：";
        for (int k = 1; k <= top; ++k) cout << a[stk[k]] << " ";
        cout << "\n";
    }
    return 0;
}

/* 输出（栈内值始终不增）：
i=1  栈内值：5
i=2  栈内值：5 3
i=3  栈内值：8
i=4  栈内值：8 1            */''',
    notes=["判空必须写 <code>top &gt; 0</code>。少了它，空栈时读 stk[0]（值恒为 0）可能侥幸不崩，"
           "但逻辑已经错了——这类“不崩的错”最难查。",
           "数组大小按题目上限 +5 开，n ≤ 3×10<sup>6</sup> 就开 3000005。开小一个数量级只会得到 RE，不会给你提示。"],
    brief="手写栈：top 指针 + 全局数组，单调栈的标准写法"))

SEC.append(IDEA("例题怎么想：被弹掉的元素再也用不上", [
    "朴素做法：对每个 i 向后扫，找到第一个更大的位置。n = 3×10<sup>6</sup> 时最坏 9×10<sup>12</sup> 次比较，"
    "按每秒 10<sup>8</sup> 次算要二十多个小时。瓶颈不是“找得慢”，而是<b>重复扫描</b>。",
    P("关键是一条支配关系：若 i &lt; j 且 a<sub>i</sub> ≤ a<sub>j</sub>，那么对任何 k &lt; i，j 都比 i 更近、"
      "且不小于 a<sub>i</sub>，所以 i 永远不可能是 k 的答案——<b>i 可以从候选集合里删掉</b>。"),
    P("按这条规则删下去，剩下的候选永远是一串“下标递增、值不增”的位置。新元素 a<sub>i</sub> 一到，"
      "值比它小的候选全部当场确定答案 i（i 确实是它们右边第一个更大的位置），然后 i 自己进候选集合。"),
    P("“只在一端增删、还要保持单调”——这就是栈。新元素从栈顶开始弹，弹干净再压入，栈里值自然不增。"),
    C(r'''for (int i = 1; i <= n; ++i) {
    while (top > 0 && a[stk[top]] < a[i]) { ans[stk[top]] = i; --top; }
    stk[++top] = i;
}''', "核心 4 行"),
    P("为什么总复杂度是 O(n)：每个下标进栈恰好 1 次、出栈至多 1 次，while 里的比较总次数 ≤ 2n。"
      "单次 while 最坏能弹 n 次，但那是把别人先前存下的“入栈次数”一次花掉；摊到全部 n 个元素上就是常数。"),
    P("两处细节决定对错：<b>弹的条件用 &lt; 还是 ≤</b>——题目要“严格大于”，值相等的候选必须留着，所以用 &lt;；"
      "<b>栈里存下标而不是值</b>——答案要位置，且重复值无法区分。"),
]))

SEC.append(C(r'''#include <bits/stdc++.h>
using namespace std;
const int MAXN = 3000005;

int n, a[MAXN], ans[MAXN];
int stk[MAXN], top = 0;          // 手写栈：stk[1..top] 存下标，top = 0 是空

inline int readInt() {           // 3×10^6 个数，逐字符读比 cin 快 3 倍以上
    int x = 0; char c = getchar();
    while (c < '0' || c > '9') c = getchar();
    while (c >= '0' && c <= '9') { x = x * 10 + (c - '0'); c = getchar(); }
    return x;
}

int main() {
    n = readInt();
    for (int i = 1; i <= n; ++i) a[i] = readInt();

    for (int i = 1; i <= n; ++i) {
        // 栈里每个下标都还没等到答案，它们的值从栈底到栈顶单调不增
        while (top > 0 && a[stk[top]] < a[i]) {
            ans[stk[top]] = i;   // i 是它右边第一个更大的位置，答案当场定下
            --top;               // 它再也不会被用到，出栈
        }
        stk[++top] = i;          // 自己进栈，继续等右边
    }
    // 结束时栈里剩下的下标右边没有更大的数，ans 保持 0

    for (int i = 1; i <= n; ++i) printf("%d ", ans[i]);
    printf("\n");
    return 0;
}''', "完整代码"))

SEC.append(EXPLAIN("逐行拆解", [
    ("const int MAXN = 3000005;", "题给 n ≤ 3×10<sup>6</sup>，多开 5 个位置防越界。开成 1e6 只会得到 RE。"),
    ("int stk[MAXN], top = 0;", "全局数组放在静态区，不占 8 MB 的调用栈；top = 0 表示空栈，元素从 stk[1] 开始存。"),
    ("while (c < '0' || c > '9') c = getchar();", "跳过空格与换行。本题 a<sub>i</sub> ≥ 1，可以不管负号。"),
    ("x = x * 10 + (c - '0');", "逐位累加。手写快读的本质就是自己解析数字，绕开 cin 的格式检查。"),
    ("while (top > 0 && a[stk[top]] < a[i])", "弹的边界是“严格小于”：等于 a[i] 的候选不能弹，因为等于不算“大于”。"
                                            "前半句 top &gt; 0 是判空，少了它会读 stk[0]。"),
    ("ans[stk[top]] = i;", "栈顶那个下标等的就是现在。注意先记答案再 --top，顺序反了就记错了人。"),
    ("stk[++top] = i;", "当前元素必定进栈：它自己也要等右边更大的数。先 ++ 后赋值，保证元素落在 stk[1..top]。"),
    ("printf(\"%d \", ans[i]);", "每个答案后面跟一个空格。题目不严格卡行末空格，但 3×10<sup>6</sup> 次 cout 会慢一截。"),
]))

# ---------------------------------------------------------------- 柱状图
SEC.append(P("第一件事是把“下一个更大”换成“左右第一个更矮”，问题就从模板题变成一道真正的模型题："
             "<b>柱状图中最大的矩形</b>。"))

SEC.append(P("n 根宽 1、高 h<sub>i</sub> 的柱子并排。结论是：最大矩形总可以“往上抬”到顶住某根柱子的顶端，"
             "所以它一定是以某个 h<sub>i</sub> 为高的矩形。于是枚举 i，求以 h<sub>i</sub> 为高时能伸多宽——"
             "答案是左右两边各自“第一个比 h<sub>i</sub> 矮”的位置之间。"))

SEC.append(P("设 L<sub>i</sub>、R<sub>i</sub> 为左右第一个比 h<sub>i</sub> 矮的下标（没有就是 0 与 n+1），"
             "则面积 = h<sub>i</sub> × (R<sub>i</sub> − L<sub>i</sub> − 1)。求 L、R 就是把上一题的不等号反过来，"
             "各跑一遍单调栈。"))

SEC.append(C(r'''#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

int main() {
    int n;
    cin >> n;
    vector<int> h(n + 2, 0);                 // h[0] 与 h[n+1] 是高度 0 的哨兵
    for (int i = 1; i <= n; ++i) cin >> h[i];

    vector<int> L(n + 2), R(n + 2), stk;
    stk.reserve(n + 2);

    // 左边界：i 左边第一个比 h[i] 矮的位置
    for (int i = 1; i <= n; ++i) {
        while (!stk.empty() && h[stk.back()] >= h[i]) stk.pop_back();
        L[i] = stk.empty() ? 0 : stk.back();
        stk.push_back(i);
    }
    stk.clear();
    // 右边界：i 右边第一个比 h[i] 矮的位置
    for (int i = n; i >= 1; --i) {
        while (!stk.empty() && h[stk.back()] >= h[i]) stk.pop_back();
        R[i] = stk.empty() ? n + 1 : stk.back();
        stk.push_back(i);
    }

    ll best = 0;
    for (int i = 1; i <= n; ++i)
        best = max(best, (ll)h[i] * (R[i] - L[i] - 1));
    cout << best << "\n";
    return 0;
}''', "柱状图最大矩形（两次单调栈）"))

SEC.append(EXPLAIN("为什么边界这么求", [
    ("vector<int> h(n + 2, 0);", "首尾各留一个高度 0 的哨兵。任何真实柱子都比它高，于是“左边没有更矮的”这种情况"
                                 "由 0 号位兜住，代码里少一个分支。"),
    ("h[stk.back()] >= h[i]", "弹掉所有“不比 h[i] 高”的柱子并保留等号：等高的柱子可以被同一个矩形一起覆盖，"
                              "让最靠左的那根算全宽度就够了，最大值不会漏。"),
    ("L[i] = stk.empty() ? 0 : stk.back();", "弹干净后栈顶就是左边第一个更矮的位置；栈空说明左边全是高个子，"
                                             "左边界顶到 0。"),
    ("for (int i = n; i >= 1; --i)", "右边界完全对称，只是方向反过来。两遍共用一个栈，中间必须 stk.clear()，"
                                     "否则上一遍的残留会污染结果。"),
    ("(ll)h[i] * (R[i] - L[i] - 1)", "高度到 10<sup>9</sup>、宽度到 10<sup>5</sup>，乘积到 10<sup>14</sup>，"
                                     "必须 long long。这是本题最隐蔽的 WA。"),
    ("R[i] - L[i] - 1", "减 1 是因为 L、R 都是“更矮”的位置，不参与矩形。写成 R−L 会把矩形撑到矮柱子上，"
                        "答案偏大。"),
]))

SEC.append(INFO("一遍扫完的写法（省掉一个数组）", [
    "把 h[0] = h[n+1] = 0 当哨兵，令 i 从 0 扫到 n+1：只要 h[栈顶] &gt; h[i] 就弹出栈顶 p，此时栈顶（弹完后的新栈顶）"
    "就是 p 的左边界，i 是右边界，直接算面积 h[p] × (i − 栈顶 − 1)。",
    "每个柱子只在被弹出时结算一次，所以只用一个栈、一个变量就能出答案，常数比两遍扫描小一半。",
    "二维版本是“每行当一次柱状图”：先对每一行求出“以这一行为底、向上连续 1 的个数”，再对每行跑一次上面的算法，"
    "总复杂度 O(nm)。洛谷上的玉蟾宫（P4147）就是这个模型。",
]))

# ---------------------------------------------------------------- 滑窗
SEC.append(P("<b>单调队列 = 单调栈 + 队头能出。</b>窗口 [i−k+1, i] 右移一格，左边出去一个、右边进来一个。"
             "队尾负责“进”时弹掉更差的，队头负责“出”时弹掉过期的。"))

SEC.append(C(r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    int n, k;
    cin >> n >> k;
    vector<int> a(n);
    for (int i = 0; i < n; ++i) cin >> a[i];

    deque<int> q;                    // 存下标；对应值从队头到队尾单调递增
    for (int i = 0; i < n; ++i) {
        while (!q.empty() && a[q.back()] >= a[i]) q.pop_back();  // ① 队尾更差的永久退休
        q.push_back(i);
        while (q.front() <= i - k) q.pop_front();                // ② 滑出窗口的从队头退休
        if (i >= k - 1) cout << a[q.front()] << " ";             // ③ 窗口满 k 个才有答案
    }
    cout << "\n";
    return 0;
}''', "长度 k 的窗口最小值"))

SEC.append(EXPLAIN("三步各管一件事", [
    ("a[q.back()] >= a[i]", "① 队尾的值不小于新元素，说明队尾既不更小、又比新元素先过期，永远轮不到它当最小值，直接弹。"
                            "等号也弹：留下最新的那个，窗口右移时它活得更久。"),
    ("q.push_back(i);", "弹干净后当前元素一定入队。它可能是后面若干个窗口的答案。"),
    ("q.front() <= i - k", "② 窗口左端是 i−k+1，下标 ≤ i−k 的都已出窗。写成 &lt; 就少弹一轮，"
                           "过期元素会霸占队头，答案偏小。"),
    ("if (i >= k - 1)", "③ 前 k−1 个位置窗口还没满，不能输出。0 基下标下这是唯一的正确边界，"
                        "写成 i &gt; k−1 会少一个数。"),
    ("cout << a[q.front()]", "队头是整个窗口的最小值，因为队内值单调递增且队头没有过期。"),
    ("求最大值", "把 ① 的 &gt;= 改成 &lt;=，其余一个字都不动。两类最值只差一个符号。"),
]))

SEC.append(P("复杂度：每个下标入队 1 次、出队至多 1 次，总操作 ≤ 2n，<b>与窗口长度 k 无关</b>。"
             "用 multiset 也能维护窗口最值，但每次 O(log k)，n = 10<sup>6</sup> 时慢 20 倍。"))

# ---------------------------------------------------------------- 优化 DP
SEC.append(P("单调队列真正的价值在优化 DP。看一个典型转移："
             "f<sub>i</sub> = a<sub>i</sub> + max{ f<sub>j</sub> : i−R ≤ j ≤ i−L }。"
             "题意：一条走廊有 n 个格子，从 0 出发，每次必须向前跳 L 到 R 格，落到格子 i 得 a<sub>i</sub> 分"
             "（可以是负数），求跳到 n 的最大得分。"))

SEC.append(P("暴力枚举 j 是 O(nR)。但 f<sub>j</sub> 的取值区间 [i−R, i−L] 随 i 单调右移、长度固定，"
             "正是“滑动窗口最值”。把它换成单调队列，转移降到 O(1)，总复杂度 O(n)。"))

SEC.append(C(r'''#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const ll NEG = LLONG_MIN / 4;            // "不可达"标记，加 a[i] 也不会溢出

int main() {
    int n, L, R;
    cin >> n >> L >> R;
    vector<ll> a(n + 1), f(n + 1, NEG);
    for (int i = 1; i <= n; ++i) cin >> a[i];

    f[0] = 0;                            // 起点，得分为 0
    deque<int> q;                        // 存下标 j，f 值从队头到队尾单调递减
    // 不要把 0 提前塞进队列：j = 0 只有在 i == L 那一轮才合法（一步正好跳 L 格）

    for (int i = 1; i <= n; ++i) {
        // ① j = i - L 从这一步起才允许用来跳到 i，进队
        if (i - L >= 0 && f[i - L] != NEG) {
            while (!q.empty() && f[q.back()] <= f[i - L]) q.pop_back();
            q.push_back(i - L);
        }
        // ② j < i - R 跳得太远，够不到 i，出队
        while (!q.empty() && q.front() < i - R) q.pop_front();
        // ③ 队头就是 [i-R, i-L] 里 f 最大的那个
        if (!q.empty()) f[i] = f[q.front()] + a[i];
    }
    cout << (f[n] == NEG ? -1 : f[n]) << "\n";
    return 0;
}''', "单调队列优化 DP"))

SEC.append(EXPLAIN("转移式与三段代码的对应", [
    ("f[i] = f[q.front()] + a[i]", "原来要对 j 扫一遍 max，现在队头 O(1) 给出最大值。转移从 O(R) 降到 O(1)。"),
    ("if (i - L >= 0 && f[i - L] != NEG)", "入队时机是本题的关键：j 只有在 j ≤ i−L 时才允许跳到 i，"
                                            "所以每轮新加入的候选恰好是 i−L 一个；起点 0 会在 i = L 那一轮自动进队。"),
    ("f[q.back()] <= f[i - L]", "队尾的 f 值不更大就弹：它既不更优、又比新来的先过期，永远用不上。"),
    ("q.front() < i - R", "过期条件用 &lt;：j = i−R 这一步跳 R 格，正好合法，不能弹。"),
    ("f[i - L] != NEG", "不可达状态不能入队。否则 NEG 加几次之后会变成一个大负数，"
                        "最后判 f[n] == NEG 失效，输出一个天文数字。"),
    ("const ll NEG = LLONG_MIN / 4", "用“足够小的数”当不可达标记。直接用 LLONG_MIN，加上 a[i] 会下溢成正数。"),
]))

SEC.append(WARN("这一节的 8 种典型错法（含症状）", [
    "<b>WA，答案整体错位一格</b>。—— 单调栈里存了值而不是下标。一旦出现重复值，或者题目要求输出位置，就彻底失效。",
    "<b>WA，只在有重复值的数据上错</b>。—— 求“第一个严格大于”却写成 <code>while (a[stk[top]] &lt;= a[i])</code>。"
    "相等的候选被提前弹掉，答案会记成一个“不大于它”的位置。样例通常没有重复值，看不出来。",
    "<b>WA，窗口答案偶尔偏小</b>。—— 滑动窗口忘了弹队头，或者过期条件写成 <code>q.front() &lt; i - k</code>。"
    "过期的元素还霸着队头，后面几个窗口全部被一个“幽灵”污染。用 n=2, k=1, a=3 5 一试就知道。",
    "<b>WA，第一行少输出一个数</b>。—— 输出条件写成 <code>i &gt; k - 1</code>，应该是 <code>i &gt;= k - 1</code>。",
    "<b>TLE，明明复杂度是 O(n)</b>。—— 3×10<sup>6</sup> 的输入用 cin 却没关同步；"
    "或者把“弹队尾”写成了每次扫一遍窗口找最小值（那就退回 O(nk)）。",
    "<b>RE（数组越界）</b>。—— MAXN 开成 10<sup>6</sup> 而 n 到 3×10<sup>6</sup>；"
    "或者空队列时调用 <code>q.front()</code>（<code>deque</code> 空时取值是未定义行为，多数时候读到垃圾值）。",
    "<b>WA，第二组数据开始全错</b>。—— 多测没有清空栈 / 队列 / top 指针。上组数据的残留让第一组之后的答案全歪。",
    "<b>WA，大测试点变成负数</b>。—— 柱状图面积写成 <code>h[i] * (R[i] - L[i] - 1)</code> 而没转 long long，"
    "10<sup>9</sup> 乘 10<sup>5</sup> 直接溢出成负数。",
]))

SEC.append(REPRO("关掉页面，从空文件把 P5788 的完整代码敲一遍并提交到洛谷。",
                 "改一改 ①：输入 <code>4\n1 4 4 5</code>，正确答案是 <code>2 4 4 0</code>。"
                 "把弹栈条件 <code>&lt;</code> 改成 <code>&lt;=</code>，答案变成 <code>2 3 4 0</code>——"
                 "亲手看清“严格大于”只差这一个等号。",
                 "改一改 ②：把栈里存的下标改成存值（<code>stk[++top] = a[i]</code>），"
                 "再用它当答案数组的下标——<code>ans[stk[top]]</code> 立刻越界（RE）。答案要的是位置，所以只能存下标。",
                 "改一改 ③：滑动窗口输入 <code>2 1</code> / <code>3 5</code>，正确输出 <code>3 5</code>；"
                 "把 <code>q.front() &lt;= i - k</code> 改成 <code>q.front() &lt; i - k</code>，输出变成 <code>3 3</code>。",
                 "改一改 ④：DP 的入队下标从 <code>i - L</code> 改成 <code>i - L - 1</code>，"
                 "允许的步长整体变成 L+1 … R+1——最小的那一步 L 被禁掉了。用 L=2, R=3 的数据跑一下，"
                 "答案可能变大、可能变小、也可能直接变成 -1。"))

M = MATH("均摊、笛卡尔树与贡献法", [
    P("<b>均摊 O(n) 怎么证。</b>用会计法：给元素 i 进栈时预存 2 次操作额度，一次用于将来出栈、一次用于本次比较。"
      "while 循环每弹一个元素就消耗掉它进栈时存下的额度，所以 n 次扫描中 while 体执行总次数 ≤ n。"
      "单次 while 最坏 O(n)，但 n 次合计 O(n)——这就是“均摊”与“最坏”的区别。"),
    P("<b>滑动窗口同理。</b>n 个下标各入队 1 次、出队至多 1 次，总代价 ≤ 2n，与 k 无关。"
      "对比 multiset 的 O(n log k)：k = 10<sup>6</sup> 时 log k ≈ 20，等于凭空多 20 倍常数。"),
    P("<b>笛卡尔树。</b>把 L<sub>i</sub>、R<sub>i</sub>（左右第一个更矮）当作父子关系，单调栈恰好建出一棵二叉树："
      "节点 i 的子树区间正好是 (L<sub>i</sub>, R<sub>i</sub>)，子树大小 = R<sub>i</sub> − L<sub>i</sub> − 1。"
      "于是“以 h<sub>i</sub> 为高的最大矩形” = h<sub>i</sub> × 子树大小——柱状图问题就是笛卡尔树上的“高度 × 子树大小”。"
      "等高柱子怎么挂都不影响面积。"),
    P("<b>贡献法（本节 tag 里的第三件事）。</b>要求“所有子数组的最小值之和”，必须让每个子数组只归属一个最小值，"
      "否则等高元素会被重复计数。规则：L<sub>i</sub> 取左边第一个<b>严格小于</b> h<sub>i</sub> 的位置，"
      "R<sub>i</sub> 取右边第一个<b>小于或等于</b> h<sub>i</sub> 的位置——于是每个子数组归给它最靠右的最小值。"),
    P("按这个规则，以 h<sub>i</sub> 为最小值的子数组个数 = (i − L<sub>i</sub>) × (R<sub>i</sub> − i)："
      "左端点可选 L<sub>i</sub>+1 … i 共 i − L<sub>i</sub> 种，右端点可选 i … R<sub>i</sub>−1 共 R<sub>i</sub> − i 种。"
      "答案 = Σ h<sub>i</sub> × (i − L<sub>i</sub>) × (R<sub>i</sub> − i)。注意这里是“左小于、右小于等于”的"
      "<b>不对称</b>写法；柱状图求面积时两边都用 ≥ 也对，因为面积与“归给谁”无关。"),
    P("<b>量级感受。</b>n = 3×10<sup>6</sup> 时，O(n²) 是 9×10<sup>12</sup> 次比较，1 GHz 也要两小时；"
      "O(n) 是 3×10<sup>6</sup> 次。同一道题，两个复杂度之间差的是“能不能交”。"),
    T(["式子", "含义", "典型用途"], [
        ["R<sub>i</sub> − L<sub>i</sub> − 1", "以 h<sub>i</sub> 为高的矩形宽度", "柱状图最大矩形"],
        ["(i − L<sub>i</sub>) × (R<sub>i</sub> − i)", "以 h<sub>i</sub> 为最小值的子数组个数", "所有子数组最小值之和"],
        ["Σ (i − L<sub>i</sub>)(R<sub>i</sub> − i)", "应等于子数组总数 n(n+1)/2", "贡献法写完后的自检"],
    ]),
])

THINK = [
    "把“第一个更大”改成“第一个不小于”（允许相等），弹栈条件该怎么变？举一组数据说明两种写法输出不同。",
    "“左边第一个更大”和“右边第一个更大”能不能一遍扫完同时求出来？需要几个栈、各自的方向是什么？",
    "柱状图结论里“最大矩形一定以某根柱子的高度为高”这句话为什么成立？如果矩形上方悬空，能不能往上抬？"
    "抬的过程中宽度会变吗？",
    "所有子数组最小值之和可以用 L、R 做贡献法。那“所有子数组最大值之和”呢？L、R 该怎么定义？",
    "滑动窗口求最值时，如果 k 接近 n，单调队列还是 O(n) 吗？它省下的到底是哪部分工作？",
    "把 dp<sub>i</sub> = min{ dp<sub>j</sub> + (sum<sub>i</sub> − sum<sub>j</sub>)² } 的转移也交给单调队列，"
    "为什么不行？这类式子需要什么额外条件（决策单调性 / 凸性）才能用队列维护？",
    "窗口里如果要同时维护“最大值”和“最大值出现的次数”，单调队列还够用吗？为什么？",
]

CHECK = [
    "能默写求“右边第一个更大元素”的 4 行核心代码，并说清被弹出的元素为什么再也用不上。",
    "能说清为什么总复杂度是均摊 O(n)，而不是“最坏 O(n²)”。",
    "能写出柱状图最大矩形的 L/R 数组，并说清弹栈写成 ≥ 和写成 &gt; 都得到正确答案的原因。",
    "能默写滑动窗口最小值的三步（弹尾、弹头、输出），并指出每一步对应哪类错误。",
    "知道 deque 里为什么必须存下标，以及什么时候该换手写数组。",
    "能把 f<sub>i</sub> = a<sub>i</sub> + max{f<sub>j</sub>} 的转移改成单调队列版本，并说清入队时机为什么是 i−L。",
    "拿到一道“区间最值 + 单调移动”的题，能判断该用单调队列还是 ST 表 / 线段树，理由是什么。",
]

CH2 = CH(
    "理想的正方形", "P2216", "提高-/提高", "https://www.luogu.com.cn/problem/P2216",
    [P("给定一个 a × b 的非负整数矩阵，请找出一个 n × n 的正方形区域，"
       "使这个区域内<b>最大值与最小值的差</b>尽可能小。输出这个最小差值。"),
     P("输入格式：第一行三个整数 a、b、n（2 ≤ a, b ≤ 1000，n ≤ a，n ≤ b，n ≤ 100）；"
       "接下来 a 行，每行 b 个非负整数，相邻两数之间一个空格。矩阵中所有数都不超过 10⁹。"),
     P("输出格式：一行一个整数，表示所有 n × n 正方形区域中「最大值 − 最小值」的最小值。"),
     P("<b>样例输入</b><br><code>5 4 2<br>1 2 5 6<br>0 17 16 0<br>16 17 2 1<br>2 10 2 1<br>1 2 2 2</code><br>"
       "<b>样例输出</b><br><code>1</code><br>"
       "样例解释：右下角的 2 × 2 方块是 {2,1;2,2}，最大 2 最小 1，差为 1，已经是最小可能值。")],
    hint=["先降到一维想：一条长度为 b 的数列，滑一个长度 n 的窗口，求每个窗口的最大值和最小值——"
          "这是本节刚学的单调队列，O(b)。",
          "二维怎么办？先<b>只在每一行内</b>滑一次，得到 rowmax[i][j] = 第 i 行第 j−n+1..j 列的最大值。"
          "接着把 rowmax 竖着看：每一列再滑一个长度 n 的窗口，拼起来正好是 n × n 方块的最大值。",
          "最大值和最小值要用两套单调队列，弹出方向相反，绝不能共用一个。"],
    idea=["<b>① 暴力为什么不行。</b>共 (a−n+1)(b−n+1) 个方块，每个求最值 O(n²)，"
          "最坏 10⁶ × 10⁴ = 10¹⁰。",
          "<b>② 二维最值可以拆成两次一维。</b>关键性质：n × n 方块的最大值 = 「每一行的窗口最大值」再对这 n 个值取最大；"
          "最小值同理。因为 max 和 min 都满足结合律，可以分方向做。",
          "<b>③ 第一次（横向）。</b>对每一行做长度 n 的单调队列，得到 rowmax[i][j]、rowmin[i][j]："
          "表示第 i 行以 j 结尾的长度 n 区间的最值。总代价 O(ab)。",
          "<b>④ 第二次（纵向）。</b>固定列 j，把 rowmax[1..a][j] 当成一个序列，再做一次长度 n 的单调队列，"
          "就得到以 (i, j) 为右下角的 n × n 方块的最大值；rowmin 同样处理后得到最小值。总代价还是 O(ab)。",
          "<b>⑤ 统计答案。</b>i ≥ n 且 j ≥ n 时（方块才凑得满）用 max − min 更新答案。",
          "<b>⑥ 复杂度。</b>两次 O(ab) 的滑动窗口，a、b ≤ 1000 时约 2×10⁶ 次队列操作，"
          "比暴力快 4 个数量级。三个 1005 × 1005 的 int 数组约 12 MB，放全局。"],
    code=r'''#include <bits/stdc++.h>
using namespace std;

const int MAXN = 1005;
int A, B, n;
static int v[MAXN][MAXN];
static int rmin[MAXN][MAXN], rmax[MAXN][MAXN];

int main() {
    scanf("%d%d%d", &A, &B, &n);
    for (int i = 1; i <= A; ++i)
        for (int j = 1; j <= B; ++j) scanf("%d", &v[i][j]);

    // 第一遍：每行内部滑动窗口，rmin/rmax[i][j] 表示第 i 行 [j-n+1, j] 的最值
    for (int i = 1; i <= A; ++i) {
        deque<int> qmin, qmax;
        for (int j = 1; j <= B; ++j) {
            while (!qmin.empty() && v[i][qmin.back()] >= v[i][j]) qmin.pop_back();
            qmin.push_back(j);
            if (qmin.front() <= j - n) qmin.pop_front();
            while (!qmax.empty() && v[i][qmax.back()] <= v[i][j]) qmax.pop_back();
            qmax.push_back(j);
            if (qmax.front() <= j - n) qmax.pop_front();
            rmin[i][j] = v[i][qmin.front()];
            rmax[i][j] = v[i][qmax.front()];
        }
    }

    // 第二遍：每一列上对 rmin/rmax 再做一次长度为 n 的滑动窗口
    int ans = INT_MAX;
    for (int j = n; j <= B; ++j) {
        deque<int> qmin, qmax;
        for (int i = 1; i <= A; ++i) {
            while (!qmin.empty() && rmin[qmin.back()][j] >= rmin[i][j]) qmin.pop_back();
            qmin.push_back(i);
            if (qmin.front() <= i - n) qmin.pop_front();
            while (!qmax.empty() && rmax[qmax.back()][j] <= rmax[i][j]) qmax.pop_back();
            qmax.push_back(i);
            if (qmax.front() <= i - n) qmax.pop_front();
            if (i >= n) ans = min(ans, rmax[qmax.front()][j] - rmin[qmin.front()][j]);
        }
    }

    printf("%d\n", ans);
    return 0;
}''',
    explain=[
        ("while (!qmin.empty() && v[i][qmin.back()] >= v[i][j]) qmin.pop_back();",
         "队尾比新元素大（或相等）的全部弹掉：它们既不会更小、又比新元素先过期，永远轮不到当答案。"),
        ("if (qmin.front() <= j - n) qmin.pop_front();",
         "窗口是 [j−n+1, j]。队头 ≤ j−n 就滑出去了。每步最多过期一个，所以用 if 就够。"),
        ("rmin[i][j] = v[i][qmin.front()];", "队头是这一段的最小值。第一遍把「行内 n 个数」压成一个值。"),
        ("for (int j = n; j <= B; ++j) { ... for (int i = 1; i <= A; ++i)",
         "第二遍拿 rmin/rmax 当输入，同样的骨架再跑一次，只是把「沿行滑」换成「沿列滑」。"),
        ("if (i >= n) ans = min(ans, ...);", "竖直方向凑满 n 行才是一个完整的 n × n 方块，前面几行还不能统计。"),
        ("deque<int> qmin, qmax;", "最大值和最小值的弹出方向相反，两个队列必须分开。共用一个立即失去单调性。"),
    ],
    pitfalls=["只做一次滑动窗口：行内窗口的最值不是方块的最值，必须横竖各做一次。",
              "最大和最小共用一个队列：弹出条件一正一反，队列立刻不再单调，答案随机错。",
              "窗口左端点写成 j−n 而不是 j−n+1：每个窗口多留一个过期元素，min 偏小、max 偏大。",
              "数组开成 1000：下标能取到 1000，越界 → RE 或异常答案，习惯开 1005。"],
    sample="输入：\n5 4 2\n1 2 5 6\n0 17 16 0\n16 17 2 1\n2 10 2 1\n1 2 2 2\n输出：\n1",
)

CH = CH(
    "发射站", "P1901", "普及/提高-", "https://www.luogu.com.cn/problem/P1901",
    [P("某地有 N 个能量发射站排成一行，第 i 个发射站的高度是 h<sub>i</sub>、能量值是 v<sub>i</sub>，"
       "所有 h<sub>i</sub> 互不相同。每个发射站同时向左右两边发射能量，"
       "能量只被<b>两边最近的、且比它高</b>的发射站接收；如果那边不存在更高的发射站，这份能量就损失掉。"),
     P("一个发射站收到的能量，是所有能到达它的发射站发出的能量之和。求收到的能量最多的那个发射站收到了多少。"),
     P("输入：第一行一个整数 N（1 ≤ N ≤ 10<sup>6</sup>）；接下来 N 行，每行两个整数 h<sub>i</sub>、v<sub>i</sub>"
       "（1 ≤ h<sub>i</sub>, v<sub>i</sub> ≤ 10<sup>9</sup>），数据保证所有 h<sub>i</sub> 互不相同。"),
     P("输出：一行一个整数，表示最大的接收能量。")],
    hint=["每个发射站只关心两件事：左边第一个比它高的、右边第一个比它高的。不用管能量会不会传到第三个人。",
          "“左边第一个比它高的”，和本节例题“右边第一个比它大的”，是同一个模板把方向反过来。",
          "从左往右跑一遍、从右往左跑一遍，两次都往一个累加数组里加。接收的能量总和可能到 10<sup>15</sup>。"],
    idea=["把任务拆成两半：对每个 i，找到 <b>左边</b>第一个 h 比自己大的位置 p，让 rec[p] += v<sub>i</sub>；"
          "再找<b>右边</b>第一个比自己大的位置 q，让 rec[q] += v<sub>i</sub>。两遍互不干扰。",
          "求“左边第一个更大”用单调栈：从左往右扫，维护一个高度<b>递减</b>的下标栈。"
          "遇到 i 时，把栈里所有高度小于 h<sub>i</sub> 的弹掉——它们挡不住 i，而且已经被 i 截住了，"
          "以后不可能再成为任何人的“最近的更高者”。",
          "弹干净之后，栈顶就是左边第一个比 h<sub>i</sub> 高的位置，把 v<sub>i</sub> 记在它头上。",
          "为什么栈顶一定对：设 j 是 i 左边第一个比 i 高的位置。若 j 被弹出，只能是被某个 k（j &lt; k &lt; i）"
          "以 h<sub>k</sub> &gt; h<sub>j</sub> &gt; h<sub>i</sub> 弹掉的，那 k 比 j 更靠右且也比 i 高，与 j 的“第一个”矛盾。"
          "所以 j 一定还在栈里，且栈里没有比它更靠右的合法候选，它就是栈顶。",
          "右边同理，从右往左再跑一遍同一个模板，栈清空后重新用。",
          "复杂度 O(N)：每个下标进栈一次、出栈至多一次，两遍合计 4N 次操作，N = 10<sup>6</sup> 轻松通过。"],
    code=r'''#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const int MAXN = 1000005;

int n, h[MAXN], v[MAXN];
int stk[MAXN], top = 0;             // 单调栈：存下标，高度从栈底到栈顶递减
ll rec[MAXN];                       // rec[i] = 第 i 个发射站收到的总能量

int main() {
    scanf("%d", &n);
    for (int i = 1; i <= n; ++i) scanf("%d%d", &h[i], &v[i]);

    // 第一遍：每个站把能量交给左边最近的更高者
    for (int i = 1; i <= n; ++i) {
        while (top > 0 && h[stk[top]] < h[i]) --top;   // 更矮的挡不住我，弹掉
        if (top > 0) rec[stk[top]] += v[i];            // 栈顶就是左边第一个更高的
        stk[++top] = i;                                // 自己进栈
    }

    // 第二遍：反方向再来一次，处理右边
    top = 0;
    for (int i = n; i >= 1; --i) {
        while (top > 0 && h[stk[top]] < h[i]) --top;
        if (top > 0) rec[stk[top]] += v[i];
        stk[++top] = i;
    }

    ll best = 0;
    for (int i = 1; i <= n; ++i) best = max(best, rec[i]);   // 注意用 ll 接
    printf("%lld\n", best);
    return 0;
}''',
    explain=[
        ("while (top > 0 && h[stk[top]] < h[i]) --top;",
         "高度严格小于就弹。本题保证高度互不相同，所以不会遇到“相等该不该弹”的问题；"
         "如果高度可能相等，题意“比它高”要求不弹等高的那个。"),
        ("if (top > 0) rec[stk[top]] += v[i];",
         "弹干净后栈顶是左边第一个更高的站。注意是 rec += v[i]：能量记在<b>接收方</b>头上。"),
        ("stk[++top] = i;", "自己入栈。能量已经交出去了，入栈是为了<b>将来接收</b>右边那些比它矮的站交来的能量。"),
        ("top = 0; 第二遍循环", "同一个模板反着跑。清空栈这一步最容易漏，漏了会把上一遍的残留混进来。"),
        ("ll rec[MAXN];", "一个站最多收 10<sup>6</sup> 份、每份 10<sup>9</sup>，总和 10<sup>15</sup>，int 直接爆。"),
        ("printf(\"%lld\\n\", best);", "long long 必须配 %lld。用 %d 打印只会输出低 32 位，等于随机数。"),
    ],
    pitfalls=["只从左往右跑一遍，忘了右边的能量：样例往往看不出来（最大值的站可能恰好在中间），大测试点掉一半。",
              "能量总和用 int 存：10<sup>6</sup> × 10<sup>9</sup> = 10<sup>15</sup>，比 int 上限高五个数量级。",
              "栈数组开 10<sup>5</sup>：N 到 10<sup>6</sup>，直接 RE；开 1000005 才安全。",
              "把“交给最近更高者”写成“交给最近的一个”：漏了 if (top &gt; 0) 判空，或者忘了弹栈，结果全错。",
              "两遍之间忘了 top = 0，第二遍直接在上一遍的栈上继续操作。"],
)

LESSONS = [LESSON(
    48, "单调栈与单调队列",
    "一句话概括这一节：把不可能成为答案的元素当场删掉。四个用法串起来——单调栈求下一个更大元素、"
    "左右边界定柱状图最大矩形、单调队列求滑动窗口最值、单调队列把 DP 的 O(nR) 转移压成 O(1)。",
    65, ["单调栈", "滑动窗口最值", "贡献法"], "提高-",
    SEC, math=M, think=THINK, check=CHECK, challenge=CH, challenge2=CH2,
    refs=["《算法竞赛进阶指南》0x11：单调栈与单调队列",
          "《算法竞赛入门笔记》：栈、队列与滑动窗口最值",
          "《算法竞赛试炼场：洛谷300题精析》P5788、P1886 两题的精析",
          "《算法竞赛黄金法则：提高算法和思考力的77项技巧》：先删无用元素，再谈优化"],
)]
