# -*- coding: utf-8 -*-
"""第 30 节 · 回顾六：BFS、二分与容器"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dsl import *  # noqa

SEC = []

SEC.append(P("第 26~29 节给的东西可以压成三句话：<b>BFS 按层扩散，第一次访问就是最短路</b>；"
             "<b>答案有单调性时，把「求最优」换成「判可行」再二分</b>；"
             "<b>容器只决定一件事——下一次该取谁</b>（queue 取最早、stack 取最晚、priority_queue 取最小）。"
             "这一节不教新算法，只用一道完整例题把 BFS 模板从头抄到尾，"
             "再把二分、堆、队列的骨架各拆一遍，最后用 5 道洛谷黄题限时训练。"))

SEC.append(Q("BFS 的答案在第一次访问时定下；二分的答案在最后一次收缩时定下；容器的答案在弹出顺序里定下。"))

SEC.append(T(["节", "内容", "看到这些字就上它"], [
    ["26", "BFS：一层一层地扩散",
     "「最少几步」「最短时间」「同时从多个点出发」，且每一步代价相同"],
    ["27", "二分查找与二分答案",
     "「最大值最小」「最小值最大」「第 k 个满足…」，且答案随判定单调"],
    ["28", "双端队列与优先队列",
     "「每次取当前最小 / 最大」；边权只有 0 和 1 的最短路"],
    ["29", "栈与队列的应用",
     "「括号」「后缀表达式」「出栈顺序」；「最近一段时间内到达的人」"],
]))

# ---------------------------------------------------------------- 完整例题
SEC.append(EX("奶酪", "P3958", "普及/提高-", "https://www.luogu.com.cn/problem/P3958",
              ["一块长方体奶酪，高为 h，底面在平面 z = 0 上，顶面在 z = h。奶酪里有 n 个球形空洞，"
               "半径都是 r，第 i 个洞的球心是 (xᵢ, yᵢ, zᵢ)。",
               "一只老鼠在奶酪底面上，它只能通过空洞穿行：两个洞若<b>相交或相切</b>（球心距离 ≤ 2r）就互相连通；"
               "洞若与底面接触（zᵢ ≤ r）就能从底面钻进去，若与顶面接触（zᵢ + r ≥ h）就能钻出来。"
               "问老鼠能否从底面走到顶面。",
               "输入格式：第一行一个整数 T，表示数据组数。每组数据：第一行三个整数 n、h、r；"
               "接下来 n 行，每行三个整数 xᵢ、yᵢ、zᵢ。",
               "输出格式：每组数据输出一行，能走出去输出 <code>Yes</code>，否则输出 <code>No</code>。",
               P("数据范围：1 ≤ n ≤ 1000，1 ≤ h, r ≤ 10⁹，0 ≤ xᵢ, yᵢ, zᵢ ≤ 10⁹。")],
              sample="输入：\n1\n2 4 1\n1 1 1\n1 1 3\n输出：\nYes"))

# ---------------------------------------------------------------- 新函数拆解
SEC.append(P("先看清这 6 个东西的结构。它们的名字和参数写错一个字符，整道题就从 WA 开始。"))

SEC.append(FN(
    "queue（队列）",
    "queue<int> q;\nq.push(x);  q.front();  q.pop();  q.empty();",
    [("queue&lt;int&gt;", "先进先出（FIFO）容器。BFS 靠它保证「先被发现的点先扩展」，于是步数单调不减。"),
     ("q.push(x)", "放到队尾。BFS 里就是「发现一个新点，排队等处理」。"),
     ("q.front()", "读队头元素，<b>只读不删</b>。"),
     ("q.pop()", "删掉队头，<b>返回 void</b>，不能写 <code>int u = q.pop();</code>。"),
     ("q.empty()", "空返回 true。循环固定写 <code>while (!q.empty())</code>。"),
     ("q.size()", "元素个数，返回无符号数，和 int 比较时留意类型。")],
    example=r'''queue<int> q;
q.push(1); q.push(2); q.push(3);   // 队列内：1 2 3

int u = q.front();                 // u = 1，元素还在队里
q.pop();                           // 队列内：2 3

cout << q.front() << " " << q.size() << "\n";   // 2 2''',
    notes=["<code>front()</code> 取值和 <code>pop()</code> 删元素是两步。少写一步 = 同一个点被处理两次。",
           "对空队列调用 <code>front()/pop()</code> 是未定义行为：本地可能不崩，评测机上就是 RE。"],
    brief="BFS 的引擎：push 进队尾、front 看队头、pop 出队头"))

SEC.append(FN(
    "pair 与结构化绑定（C++17）",
    "queue<pair<int,int>> q;\nq.push({x, y});\nauto [x, y] = q.front();",
    [("pair&lt;int,int&gt;", "把两个 int 打包成一个类型。网格题用它存 (行, 列)，就不必开两个队列、两个数组。"),
     ("q.push({x, y})", "花括号直接构造一个 pair 压入队列。"),
     ("auto [x, y] = ...", "结构化绑定：一次把 first、second 拆成两个变量。C++17 起可用。"),
     ("老写法", "<code>int x = q.front().first, y = q.front().second;</code>，机子只支持 C++14 时改这样。"),
     ("嵌套尖括号", "<code>queue&lt;pair&lt;int,int&gt;&gt;</code> 结尾两个 <code>&gt;</code> 之间留空格，C++11 之前会当成右移。")],
    example=r'''queue<pair<int,int>> q;
q.push({2, 5});
q.push({3, 1});

auto [x, y] = q.front();      // x = 2, y = 5（拷贝，改它不影响队列）
q.pop();

int a = q.front().first;      // 不用结构化绑定的等价写法
int b = q.front().second;''',
    notes=["<code>auto [x, y]</code> 拿到的是副本；想改队列里的元素要用引用，而 <code>queue</code> 本来就不给改队头。",
           "坐标顺序全程统一：都用 (行, 列)。方向数组那里如果换成 (列, 行)，答案会整体转置。"],
    brief="把二维坐标压成一个元素，一队列搞定网格 BFS"))

SEC.append(FN(
    "lower_bound / upper_bound（有序区间二分）",
    "int p = lower_bound(a + 1, a + n + 1, x) - a;",
    [("区间", "左闭右开 <code>[first, last)</code>，<b>必须已按 &lt; 升序排好</b>。"),
     ("lower_bound", "返回<b>第一个大于等于</b> x 的位置。"),
     ("upper_bound", "返回<b>第一个严格大于</b> x 的位置。"),
     ("换成下标", "数组写 <code>- a</code>，vector 写 <code>- v.begin()</code>，否则得到的是迭代器。"),
     ("找不到", "返回 last。判断不存在要写 <code>it != last</code>，不能只看 <code>*it == x</code>。"),
     ("复杂度", "O(log n) 次比较。n = 10⁶ 时约 20 次，比扫一遍快 5 万倍。")],
    example=r'''int a[6] = {0, 1, 3, 3, 3, 7};              // a[1..5] 有序，下标从 1 起
int p = lower_bound(a + 1, a + 6, 3) - a;   // p = 2，第一个 3
int q = upper_bound(a + 1, a + 6, 3) - a;   // q = 5，第一个大于 3 的位置
int c = q - p;                              // c = 3，即 3 的个数''',
    notes=["没排序就 lower_bound，结果毫无意义：在 <code>1 2 1</code> 里查 1，返回的是中间那个。",
           "手写二分有 <code>while (l &lt;= r)</code> 与 <code>while (l &lt; r)</code> 两套模板，混着写必死循环；用库函数没有这个风险。"],
    brief="有序数组里 O(log n) 找位置，配 upper_bound 数出现次数"))

SEC.append(FN(
    "二分答案的固定骨架（check + 收缩）",
    "while (l < r) { int mid = ...; if (check(mid)) ...; else ...; }",
    [("check(x)", "返回「答案不超过 x（或 x 可行）」。必须<b>单调</b>：x 变大时结果只从 false 变 true，不能反复。"),
     ("l、r", "区间永远是「答案所在的范围」。l、r 的初值要真的把答案包住，宁可放宽一格。"),
     ("mid 防溢出", "<code>l + (r - l) / 2</code>，别写 <code>(l + r) / 2</code>：两者都接近 2×10⁹ 时会溢出成负数。"),
     ("求最小值", "下取整 mid；check 为真 <code>r = mid</code>，否则 <code>l = mid + 1</code>。"),
     ("求最大值", "上取整 <code>l + (r - l + 1) / 2</code>；check 为真 <code>l = mid</code>，否则 <code>r = mid - 1</code>。"),
     ("复杂度", "O(log 值域 × check)。值域 10⁹ 时约 30 次 check，10⁶ 个数也就 3×10⁷ 次运算。")],
    example=r'''// 求最小的可行值：check 形如 false false ... false true true ...
int l = 0, r = 1000000000;
while (l < r) {
    int mid = l + (r - l) / 2;
    if (check(mid)) r = mid;        // mid 可行，答案不超过 mid
    else            l = mid + 1;    // mid 不可行，答案更大
}
cout << l << "\n";                  // 收敛时 l == r，就是答案''',
    notes=["「r = mid 配下取整」「l = mid 配上取整」这两对必须成套。配错了就是死循环 TLE。",
           "check 写错方向（把 ≥ 写成 &gt;、把「不超过」写成「不少于」）时，二分照样跑完，只是答案是错的——这类 WA 最难查。"],
    brief="把「求最优」换成「判可行」，30 次判定定出答案"))

SEC.append(FN(
    "priority_queue（优先队列 / 堆）",
    "priority_queue<int, vector<int>, greater<int>> pq;",
    [("priority_queue&lt;int&gt;", "默认<b>大根堆</b>：<code>top()</code> 是当前最大值。"),
     ("三个参数", "元素类型、底层容器、比较方式。<code>greater&lt;int&gt;</code> 表示小的优先，即小根堆。"),
     ("pq.push(x)", "插入，O(log n)。"),
     ("pq.top()", "读堆顶（最值），O(1)，只读不删。"),
     ("pq.pop()", "删堆顶，O(log n)，同样不返回值。"),
     ("底层", "完全二叉树压在数组里；建堆 O(n)，单次操作 O(log n)。")],
    example=r'''priority_queue<int, vector<int>, greater<int>> pq;   // 小根堆

for (int x : {5, 1, 4, 2}) pq.push(x);
while (!pq.empty()) {
    cout << pq.top() << " ";   // 1 2 4 5
    pq.pop();
}''',
    notes=["写成 <code>priority_queue&lt;int&gt;</code> 就是大根堆，取出的顺序整个反过来——合并果子这类题会直接 WA。",
           "堆里存结构体要自己写比较规则；比较规则写反、或漏了兜底字段，是堆题的第一大 WA 来源。"],
    brief="每次 O(log n) 取当前最值，合并果子、Dijkstra 都靠它"))

SEC.append(FN(
    "stack（栈）",
    "stack<int> st;\nst.push(x);  st.top();  st.pop();  st.empty();",
    [("stack&lt;int&gt;", "后进先出（LIFO）容器。"),
     ("st.push(x)", "压栈，放到栈顶。"),
     ("st.top()", "读栈顶，O(1)，只读不删。"),
     ("st.pop()", "弹出栈顶，返回 void。"),
     ("用之前必须判空", "对空栈 <code>top()/pop()</code> 是未定义行为，代码里永远「先判空、再 top」。")],
    example=r'''stack<char> st;
string s = "(()";
for (char c : s) {
    if (c == '(') st.push(c);
    else if (!st.empty()) st.pop();   // 先判空
}
cout << (st.empty() ? "匹配" : "不匹配") << "\n";''',
    notes=["括号匹配的判据是「扫完栈为空」；中途遇到右括号而栈已空，同样直接判不匹配。",
           "把 stack 换成 queue 就是 BFS，换成 deque 就是 0-1 BFS——三个容器只差一两个函数名。"],
    brief="后进先出：括号匹配、后缀表达式、出栈序列验证"))

SEC.append(TIP("容器怎么选：只看「下一次该取谁」", [
    "取<b>最早进来的</b> → <code>queue</code>。BFS、按时间滑动的窗口（海港）。",
    "取<b>最后进来的</b> → <code>stack</code>。括号匹配、后缀表达式、非递归 DFS。",
    "取<b>当前最小 / 最大</b> → <code>priority_queue</code>。质量检测（滑窗最小值）、Dijkstra、贪心选最优。",
    "两头都要取 → <code>deque</code>。<b>0-1 BFS</b>（边权只有 0 和 1）：权 0 塞队头、权 1 塞队尾，一次 BFS 就得到最短路。",
]))

# ---------------------------------------------------------------- 思路
SEC.append(IDEA("例题怎么想：把“洞”当成点，把“连通”当成边", [
    P("<b>抽象。</b>每个洞是一个点。两个洞连通 ⇔ 球心距离 ≤ 2r。"
      "再加两个虚拟点：底面 S 与所有满足 <code>zᵢ ≤ r</code> 的洞相连，顶面 T 与所有满足 "
      "<code>zᵢ + r ≥ h</code> 的洞相连。问题变成“S 与 T 是否连通”——一次 BFS 就够。"),
    P("<b>判定条件为什么是这两个不等式。</b>洞是半径 r 的球：它最低点是 zᵢ − r，最高点是 zᵢ + r。"
      "与底面（z = 0）相碰 ⟺ <code>zᵢ − r ≤ 0</code>；与顶面（z = h）相碰 ⟺ <code>zᵢ + r ≥ h</code>。"
      "切点也算，所以用 ≤ / ≥ 而不是 &lt; / &gt;。"),
    P("<b>距离比较必须避开浮点。</b>球心距 ≤ 2r 等价于 "
      "<code>(Δx)² + (Δy)² + (Δz)² ≤ 4r²</code>。坐标到 10⁹，平方到 10¹⁸，"
      "三项相加到 3×10¹⁸，仍在 long long 范围内（上限约 9.2×10¹⁸）。"
      "如果先开根号再比较，浮点误差会让“相切”这种边界情况判错。"),
    P("<b>BFS 还是 DFS？</b>都可以。这里只要“连通与否”，不关心步数，"
      "用 BFS 只是为了不用递归、不担心栈深度（本题 n ≤ 1000，其实都安全）。"),
    P("<b>复杂度。</b>每轮 BFS 最多把每条边看一遍，边数是 n²/2 = 5×10⁵，"
      "乘上 T 组数据，1 秒能过。"),
    P("<b>为什么不能排序后只连相邻的。</b>“距离 ≤ 2r”不是一个偏序关系，"
      "排序之后相邻的两个洞不一定连通、隔得远的却可能连通，所以只能两两判。"),
]))

SEC.append(C(r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int T;
    cin >> T;
    while (T--) {
        int n;
        long long h, r;
        cin >> n >> h >> r;

        vector<array<long long, 3>> p(n);
        for (auto& a : p) cin >> a[0] >> a[1] >> a[2];

        vector<int> vis(n, 0);
        queue<int> q;

        for (int i = 0; i < n; ++i)
            if (p[i][2] <= r) { vis[i] = 1; q.push(i); }    // 从底面能直接钻进去

        bool ok = false;
        while (!q.empty() && !ok) {
            int u = q.front(); q.pop();
            if (p[u][2] + r >= h) { ok = true; break; }     // 这个洞碰到顶面
            for (int v = 0; v < n; ++v) {
                if (vis[v]) continue;
                long long dx = p[u][0] - p[v][0];
                long long dy = p[u][1] - p[v][1];
                long long dz = p[u][2] - p[v][2];
                if (dx * dx + dy * dy + dz * dz <= 4 * r * r) {   // 相交或相切
                    vis[v] = 1;
                    q.push(v);
                }
            }
        }
        cout << (ok ? "Yes" : "No") << "\n";
    }
    return 0;
}''', "完整代码"))

SEC.append(EXPLAIN("逐行拆解", [
    ("vector&lt;array&lt;long long, 3&gt;&gt; p(n);",
     "坐标存 long long：距离平方要到 10¹⁸ 量级，int 早就溢出。多组数据用 vector 现开现释放，"
     "比全局数组更省心。"),
    ("if (p[i][2] &lt;= r)", "与底面接触的条件。注意用它而不是 <code>z &lt; 0</code>——"
                            "球的最低点是 z − r，只要这个值 ≤ 0 就能从底下钻进去。"),
    ("if (p[u][2] + r &gt;= h)", "与顶面接触的条件。切点也算通，所以用 ≥。"),
    ("dx * dx + dy * dy + dz * dz &lt;= 4 * r * r",
     "用“平方比较”代替开根号：避免浮点误差，也省掉 sqrt 的时间。注意 <code>4 * r * r</code> "
     "必须先做乘法再比较，写成 <code>2 * r * 2 * r</code> 结果相同但可读性差。"),
    ("long long dx = ...;",
     "差值的平方一定非负，但差值本身可以是负数：用 long long 存，乘方之后才安全。"),
    ("if (vis[v]) continue;",
     "已经入队的洞不再重复入队。BFS 里“入队即标记”，这是从第 26 节就定下来的规矩。"),
    ("while (!q.empty() &amp;&amp; !ok)",
     "找到一条到顶面的路就可以停，不必跑完整张图。这份剪枝在多组数据时很值钱。"),
]))


SEC.append(T(["看到这些话", "第一反应", "复杂度"], [
    ["最少几步 / 最短时间，每步代价相同", "BFS，距离数组兼作 visited", "O(状态数)"],
    ["最大值最小 / 最小值最大", "二分答案 + check", "O(log 值域 × check)"],
    ["每次取当前最小 / 最大", "priority_queue（注意小根堆三参数）", "O(n log n)"],
    ["括号 / 后缀式 / 出栈顺序", "stack 模拟", "O(n)"],
    ["按时间滑动的区间", "queue 存元素 + cnt 计数，队头过期就弹出", "O(总元素数)"],
]))

# ---------------------------------------------------------------- 易错清单
SEC.append(WARN("这一章最容易踩的 7 个坑（都带症状）", [
    "BFS 把「标记已访问」写在出队时而不是入队时：同一个点被多个父亲反复推进队列。"
    "症状是<b>小数据全对、大数据 TLE 或 MLE</b>，队列长度能到状态数的几倍。",
    "距离数组初值用 0 而不是 −1：全局数组默认就是 0，「到不了」的格子被当成「0 步到达」。"
    "症状是<b>输出一片 0</b>，样例第一眼就能看出来。",
    "方向数组与棋盘下标起点不匹配（0 起 vs 1 起）：症状是<b>第一行或第一列全是 −1</b>，"
    "而且小样例往往只差一两个格子，极易被忽略。",
    "二分求最大值时 mid 用了下取整 <code>(l + r) / 2</code>：l 与 r 相邻且 check 为真时 l 不动。"
    "症状是<b>死循环 TLE</b>，最后几个点全挂。",
    "check 里累加用 <code>int</code>：砍树 n = 10⁶、树高 4×10⁵，总和到 4×10¹¹，溢出成负数后 check 永远为真。"
    "症状是<b>输出二分上界而不是答案</b>。",
    "二分的上界开小了：H 只开到 10⁵，比它高的答案全被截断。症状是<b>WA 但样例照过</b>，"
    "因为样例的树矮——上界一定要按题目给的最大值开。",
    "<code>priority_queue&lt;int&gt;</code> 当小根堆用：取出的永远是大值。"
    "症状是<b>质量检测的答案全变成窗口最大值</b>（1 3 2 5 4 6 会输出 3 3 5 6 而不是 1 2 2 4），因为大根堆把最大的顶在上面。",
]))

SEC.append(REPRO("关掉页面，把上面 P3958 的完整代码手打一遍并提交，样例必须输出 Yes。",
                 "改一改①：把距离判断换成浮点写法 <code>sqrt(dx*dx+dy*dy+dz*dz) &lt;= 2*r</code>，"
                 "造一组“两个球恰好相切”的数据，看会不会判错——这就是浮点误差的现场。",
                 "改一改②：把 <code>4 * r * r</code> 写成 <code>4 * r * r</code> 但把 dx 的类型改成 int，"
                 "输入坐标到 10⁹ 的数据，看结果为什么突然变成 Yes/No 乱跳（溢出）。",
                 "改一改③：把 <code>z &lt;= r</code> 改成 <code>z &lt; r</code>，"
                 "造一组“球正好与底面外切”的数据，验证边界必须取等号。",
                 "改一改④：把 BFS 换成 DFS 递归，n = 1000 的链状数据也能过；再想想如果 n 到 10⁵ 会怎样。"))

SEC.append(INFO("这次训练怎么用 95 分钟", [
    "0~10 分钟：只读题，不写代码。按「能立刻写」→「有思路」→「没思路」给 5 题排个序。",
    "10~30 分钟：A（01迷宫）。重点不是 BFS 模板，而是「每个连通块只算一次」那句优化。",
    "30~55 分钟：B（砍树）。二分答案的第一个方向：找最后一个可行值，mid 要上取整。",
    "55~75 分钟：C（数列分段）。第二个方向：找第一个可行值，下界必须取 max(aᵢ)。",
    "75~85 分钟：D（质量检测）。小根堆 + 懒删除：队首过期就 pop，写出 while 而不是 if。",
    "85~95 分钟：E（海港）。只写队列 + 计数数组，不写复杂结构；最后核对边界与计数顺序。",
]))

SEC.append(OK("提交前的 30 秒检查清单", [
    "BFS：距离数组初值 −1、起点 0、入队即标记，三件事都做了吗？",
    "二分：l、r 的初值真的把答案包住了吗？mid 的取整方向与收缩方向配套吗？",
    "check 里的累加变量是 <code>long long</code> 吗？最大值估一遍：个数 × 单值。",
    "小根堆是不是写全了 <code>&lt;int, vector&lt;int&gt;, greater&lt;int&gt;&gt;</code>？",
    "多组数据 / 多组询问：全局数组、栈、队列都清空了吗？",
    "输出：行末有没有多余空格？每组询问是否各自换行？",
]))

CHECK = [
    "不看资料能写出网格 BFS 的完整模板：方向数组、距离数组、入队即标记三件套。",
    "能说清「BFS 第一次访问即最短」的理由，并举一个 DFS 求最短路会错的例子。",
    "能手写二分答案的两套收缩方式，并说清哪一套必须配上取整的 mid。",
    "能解释 check 单调性是什么意思，以及为什么「段数 ≤ m」等价于「每段和 ≤ X 可行」。",
    "能说出 <code>priority_queue&lt;int, vector&lt;int&gt;, greater&lt;int&gt;&gt;</code> 三个参数各是什么。",
    "能说清 P2058 里为什么弹出条件是 <code>q.front().first &lt;= t - 86400</code> 而不是 <code>&lt;</code>，"
    "以及 P2251 里为什么用 while 清过期元素而不是 if。",
    "能说出 0-1 BFS 为什么必须用 deque：权 0 的边塞队头、权 1 的边塞队尾。",
]

# ---------------------------------------------------------------- 5 道训练题
CH1 = CH("01迷宫", "P1141", "普及/提高-", "https://www.luogu.com.cn/problem/P1141",
         [P("有一个 n × n 的迷宫，每格是 0 或 1。站在 0 上只能走到相邻 4 格中的 1，站在 1 上只能走到相邻 4 格中的 0。"),
          P("给出 m 个询问 (i, j)，每次求从这一格出发能走到的格子数（包含自身）。"),
          P("输入格式：第一行 n、m（1 ≤ n ≤ 1000，1 ≤ m ≤ 10⁵）；接下来 n 行每行 n 个 0/1 字符、字符间没有空格；"
            "再接下来 m 行，每行两个整数 i、j。"),
          P("输出格式：m 行，每行一个整数，表示对应询问的答案。")],
         hint=["照题面直译：每个询问从 (i,j) 做一次 BFS。先估一下最坏要做多少次、每次多大。",
               "如果两个格子互相可达，它们的答案必然相同。想一想「互相可达」把整张棋盘分成了什么。",
               "既然同块同答案，能不能每块只算一次，之后每个询问只查表？"],
         idea=["把格子看成点，相邻且数字不同就连一条边。「数字不同」是对称的，所以这是一张无向图。",
               "询问「从 (i,j) 能走到多少格」等价于求 (i,j) 所在<b>连通块的大小</b>。",
               "同一连通块里任意两点可达集合相同，块内一点也走不到块外，所以块内所有格子的答案都等于块大小。",
               "于是每个块只 BFS 一次：数出块大小，再把大小写回块内所有格子。之后每个询问 O(1) 查表。",
               "实现上让 ans 数组兼作访问标记：0 = 没处理，−1 = 已入队、大小待定，正数 = 块大小。",
               "复杂度 O(n² + m)：每格只入队一次，询问只查表。若每个询问单独 BFS，最坏 10⁵ × 10⁶ = 10¹¹，必 TLE。"],
         code=r'''#include <bits/stdc++.h>
using namespace std;

const int MAXN = 1005;
int n, m;
char g[MAXN][MAXN];            // g[i][j]：'0' 或 '1'，行列从 1 开始
int ans[MAXN][MAXN];           // 0 = 未处理，-1 = 已入队待定，正数 = 块大小
int cells[MAXN * MAXN];        // 当前块内的格子，压成 i * MAXN + j
int dx[4] = {1, -1, 0, 0};
int dy[4] = {0, 0, 1, -1};

// 把 (sx, sy) 所在的整个连通块算完，并把块大小写回块内每一格
void fill_block(int sx, int sy) {
    queue<pair<int,int>> q;
    q.push({sx, sy});
    ans[sx][sy] = -1;          // 入队就标记，不能等出队

    int cnt = 0;
    while (!q.empty()) {
        auto [x, y] = q.front(); q.pop();
        cells[cnt++] = x * MAXN + y;       // 记下块内格子，等会儿统一回填
        for (int d = 0; d < 4; ++d) {
            int nx = x + dx[d], ny = y + dy[d];
            if (nx < 1 || nx > n || ny < 1 || ny > n) continue;
            if (ans[nx][ny] != 0) continue;            // 已属于某个块
            if (g[nx][ny] == g[x][y]) continue;        // 只能走到数字不同的格
            ans[nx][ny] = -1;
            q.push({nx, ny});
        }
    }
    for (int k = 0; k < cnt; ++k)                  // 同块同答案
        ans[cells[k] / MAXN][cells[k] % MAXN] = cnt;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cin >> n >> m;
    for (int i = 1; i <= n; ++i)
        for (int j = 1; j <= n; ++j) cin >> g[i][j];   // 读 char 会自动跳过换行

    for (int i = 1; i <= n; ++i)
        for (int j = 1; j <= n; ++j)
            if (ans[i][j] == 0) fill_block(i, j);      // 每块只算一次

    while (m--) {
        int i, j;
        cin >> i >> j;
        cout << ans[i][j] << "\n";                     // 询问退化成查表
    }
    return 0;
}''',
         explain=[
             ("int ans[MAXN][MAXN];", "同时当答案表和访问标记。省掉一个 vis 数组，也省掉一次「两块表不同步」的 bug。"),
             ("ans[sx][sy] = -1;", "入队立刻标记。等出队再标记的话，同一块里的格子会被多个父亲重复压入，块大小就数大了。"),
             ("cells[cnt++] = x * MAXN + y;", "BFS 时还不知道块最终多大，只能先记下来；把坐标压成一个 int，一个数组就够。"),
             ("if (g[nx][ny] == g[x][y]) continue;", "这就是「边」的定义：只能走到数字不同的相邻格。写反成 != 时 continue，整题崩。"),
             ("ans[cells[k] / MAXN][cells[k] % MAXN] = cnt;", "回填：同一块所有格子的答案都等于块大小。"),
             ("while (m--)", "询问阶段只查表，O(1)。这正是把 10¹¹ 降到 10⁶ 的地方。"),
         ],
         pitfalls=["对每个询问单独 BFS：m = 10⁵、n = 1000 时约 10¹¹ 次操作 → TLE。",
                   "入队时不标记、只在出队时标记 → 同一格被重复压入，块大小数大 → WA。",
                   "cells 数组按 10⁵ 开：n = 1000 时一整块能有 10⁶ 个格子，越界 → RE。",
                   "询问下标 1 起、数组开成 0 起，混用后答案整体错位一行一列。"],
         sample="输入：\n2 2\n01\n10\n1 1\n2 2\n\n输出：\n4\n4")

CH2 = CH("砍树", "P1873", "普及/提高-", "https://www.luogu.com.cn/problem/P1873",
         [P("有 N 棵树，第 i 棵高 hᵢ。设定锯片高度 H 后，每棵高于 H 的树被锯掉 hᵢ − H 米，"
            "得到木材总量 Σ max(0, hᵢ − H)。"),
          P("求最大的整数 H，使木材总量至少为 M。"),
          P("输入格式：第一行两个整数 N、M（1 ≤ N ≤ 10⁶，1 ≤ M ≤ 2×10⁹）；"
            "第二行 N 个整数表示每棵树的高度（≤ 4×10⁵），保证所有树高之和 &gt; M。"),
          P("输出格式：一个整数，表示锯片能升到的最大高度 H。")],
         hint=["枚举 H 从 0 到最高的树，每次扫一遍 N 棵树：这样是多少次操作？N = 10⁶ 时能过吗？",
               "H 增大时木材总量怎么变？把这句话翻译成一个单调的判定函数。",
               "二分的上界不用猜——最高的那棵树就是自然上界。"],
         idea=["check(H)：Σ max(0, hᵢ − H) ≥ M。H 越大能锯到的越少，check 单调（真…真假…假）。",
               "要的是<b>最后一个</b> check 为真的 H，于是用「上取整 mid + 可行则 l = mid」那一套。",
               "上界取 mx = max(hᵢ)（再高就一棵也锯不到），下界 0（题目保证总和 &gt; M，H = 0 一定可行）。",
               "check 里的 sum 必须 long long：10⁶ 棵 4×10⁵ 的树，总量 4×10¹¹，int 直接溢出。",
               "复杂度 O(N log mx) ≈ 10⁶ × 19 ≈ 2×10⁷ 次运算，1 秒内稳过。",
               "边界提醒：答案可能是 0（树都很矮），也可能是 mx，所以 l、r 的初值必须覆盖这两端。"],
         code=r'''#include <bits/stdc++.h>
using namespace std;

const int MAXN = 1000005;
int n, h[MAXN];
long long need;              // M 到 2×10⁹，用 int 比较会溢出

// 锯片高度为 H 时，得到的木材是否够 M 米
bool check(int H) {
    long long sum = 0;
    for (int i = 1; i <= n; ++i) {
        if (h[i] > H) {
            sum += h[i] - H;
            if (sum >= need) return true;   // 够了就提前退出
        }
    }
    return false;
}

int main() {
    scanf("%d%lld", &n, &need);

    int mx = 0;
    for (int i = 1; i <= n; ++i) {
        scanf("%d", &h[i]);
        if (h[i] > mx) mx = h[i];
    }

    int l = 0, r = mx;                      // 答案一定在 [0, 最高的树] 内
    while (l < r) {
        int mid = l + (r - l + 1) / 2;      // 上取整：求最大值必须这么写
        if (check(mid)) l = mid;            // mid 可行，答案不小于 mid
        else            r = mid - 1;        // mid 不可行，答案更小
    }
    printf("%d\n", l);
    return 0;
}''',
         explain=[
             ("bool check(int H)", "把「H 行不行」封装成函数，主函数的二分只剩四行，也方便单独手测 check。"),
             ("long long sum = 0;", "木材总量最大 4×10¹¹。用 int 溢出后变负，check 永远为真，输出上界而不是答案。"),
             ("if (h[i] > H) sum += h[i] - H;", "严格高于 H 才锯。恰好等于 H 的树贡献 0，写 &gt;= 结果一样，但按题意写更好读。"),
             ("if (sum >= need) return true;", "提前退出。木材够了就没必要继续扫后半段，n = 10⁶ 时这一句能省掉不少循环。"),
             ("int mid = l + (r - l + 1) / 2;", "上取整。若用下取整，l 与 r 相邻且 check 为真时 l 永远不动 → 死循环。"),
             ("if (check(mid)) l = mid; else r = mid - 1;", "可行就往上走，不可行就退一格。循环结束时 l == r，就是最后一个可行值。"),
         ],
         pitfalls=["上界写成 10⁵ 或 n：树高可以到 4×10⁵，比上界高的答案被截断 → WA。",
                   "check 里 sum 用 int：总量 4×10¹¹ 溢出 → check 恒真 → WA（输出上界）。",
                   "mid 用下取整又配 l = mid：l = r − 1 时死循环 → TLE。",
                   "scanf 用 <code>%d</code> 读 M：M 到 2×10⁹ 时溢出 → 比较全错。"],
         sample="输入：\n4 7\n20 15 10 17\n\n输出：\n15")

CH3 = CH("数列分段 Section II", "P1182", "普及/提高-", "https://www.luogu.com.cn/problem/P1182",
         [P("给定一个长度为 N 的数列 A，把它分成 M 段连续的子段，要求每段和的最大值尽量小，输出这个最小值。"),
          P("输入格式：第一行两个正整数 N、M（1 ≤ N ≤ 10⁵，M ≤ N）；第二行 N 个空格隔开的非负整数 Aᵢ（Aᵢ &lt; 10⁸）。"),
          P("输出格式：一个整数，即每段和最大值的最小可能值（答案不超过 10⁹）。")],
         hint=["「最大值最小」是二分答案的固定信号。先回答一个问题：如果限定每段和 ≤ X，最少要几段？",
               "段数与 X 之间是单调的：X 越大，需要的段数越少。这就是能二分的理由。",
               "二分的下界不能随便取 1。想一想：一个数本身就超过 X 时，你的 check 会怎么数段？"],
         idea=["check(X)：从左往右贪心累加，能装就装，装不下就开新段，数出最少段数 cnt。",
               "cnt ≤ M 说明 X 可行——段数不够可以把某段再切开，段数只会更多，而上限仍是 X。",
               "段数随 X 单调不增，所以「最小可行 X」可以二分，用「下取整 mid + 可行则 r = mid」那一套。",
               "下界必须取 max(Aᵢ)：否则 X 比某个数还小时，check 会把「单个元素已超限」的段也当成一段，"
               "二分会输出一个装不下的假答案。例：A = 10 1 1、M = 3，正确答案 10，下界取 1 会输出 2。",
               "上界取总和 ΣAᵢ（只分一段），10⁵ × 10⁸ = 10¹³，必须 long long。",
               "复杂度 O(N log ΣA) ≈ 10⁵ × 44，稳过。"],
         code=r'''#include <bits/stdc++.h>
using namespace std;

const int MAXN = 100005;
int n, m, a[MAXN];

// 每段和不超过 X 时，最少要分成几段
bool check(long long X) {
    int cnt = 1;                 // 至少一段
    long long sum = 0;           // 当前段的和
    for (int i = 1; i <= n; ++i) {
        if (sum + a[i] <= X) {
            sum += a[i];         // 能装就装：段数越少越容易满足 cnt <= m
        } else {
            ++cnt;               // 装不下，开新段
            sum = a[i];
        }
    }
    return cnt <= m;
}

int main() {
    scanf("%d%d", &n, &m);

    long long l = 0, r = 0;
    for (int i = 1; i <= n; ++i) {
        scanf("%d", &a[i]);
        if (a[i] > l) l = a[i];  // 下界：最大的那个数
        r += a[i];               // 上界：全部装进一段
    }

    while (l < r) {
        long long mid = l + (r - l) / 2;
        if (check(mid)) r = mid;        // X 够大，试试更小
        else            l = mid + 1;    // X 太小，段数超了
    }
    printf("%lld\n", l);
    return 0;
}''',
         explain=[
             ("int cnt = 1; long long sum = 0;", "段数从 1 开始（哪怕只有一个数也是一段）。把 cnt 写成 0 会让答案差 1。"),
             ("if (sum + a[i] <= X)", "能塞就塞。贪心为什么对：段越少越容易满足 cnt ≤ m，而「尽量往右扩」不会让后面更难分。"),
             ("else { ++cnt; sum = a[i]; }", "装不下就开新段，并把当前数放进去。别写 sum = 0 再 += a[i]，多一步就多一次写错的机会。"),
             ("return cnt <= m;", "段数不超过 M 就算可行——多出来的段可以把某段切开，上限仍然是 X。"),
             ("if (a[i] > l) l = a[i];", "关键一行。下界取 1 会在 X &lt; max(aᵢ) 时把超限的段也数进去，二分会给出假答案。"),
             ("if (check(mid)) r = mid; else l = mid + 1;", "求最小值：可行就收缩右边界。配下取整的 mid，l = r 时收敛，不会死循环。"),
         ],
         pitfalls=["下界写成 0 或 1：X &lt; max(aᵢ) 时 check 仍会算出一个段数，于是输出比 max(aᵢ) 还小的假答案 → WA。",
                   "段数和 sum 用 int：总和可到 10¹³，直接溢出 → 二分区间错乱。",
                   "cnt 初值写 0：所有数装得下时正确答案是 1，你会输出 0。",
                   "上界只写 max(aᵢ)：那只够分一段，M ≥ 2 时真实答案超过上界，二分会卡在 max(aᵢ) → WA。"],
         sample="输入：\n5 3\n4 2 4 5 1\n\n输出：\n6")

CH4 = CH("质量检测", "P2251", "普及/提高-", "https://www.luogu.com.cn/problem/P2251",
    [P("生产流水线上有 N 件产品，第 i 件的质量分数是 Aᵢ。质检员要从第 1 件开始，每次框住<b>连续 M 件</b>"
       "（第 1~M 件、第 2~M+1 件、……、第 N−M+1~N 件），记下这一次框住的产品里最差（最小）的分数。"),
     P("请按顺序输出这一串最小值：共 N − M + 1 个数，第 i 个是第 i 个窗口里的最小值。"),
     P("输入格式：第一行两个整数 N、M（1 ≤ M ≤ N ≤ 10⁵）；第二行 N 个整数 Aᵢ（Aᵢ ≤ 10⁶）。"),
     P("输出格式：共 N − M + 1 行，每行一个整数。")],
    hint=["最直接的做法是对每个窗口扫一遍求最小，O(NM)；N = M = 10⁵ 时是 10¹⁰ 次比较，必超时。",
          "窗口每次只往右滑一格：进来一个新元素，出去一个旧元素。能不能用第 28 节的容器，"
          "让“求最小值”从 O(M) 降到 O(log M)？",
          "用优先队列存 <code>(数值, 下标)</code>。窗口滑动后，队首可能是早就滑出去的旧元素——"
          "只要它的下标 ≤ 当前窗口左端 − 1，就弹掉它。"],
    idea=["<b>暴力为什么慢。</b>相邻两个窗口重叠了 M−1 个元素，暴力把它们重新扫一遍，等于把同一批数据看了 M 次。"
          "要让每个元素“进出”容器的次数是常数，总复杂度才能降到 O(N log N)。",
          "<b>做法：小根堆 + 懒删除。</b>维护一个按值排序的优先队列，元素是 "
          "<code>(Aᵢ, i)</code>。从左到右依次把 Aᵢ 压入；此时队首是“已经出现过的所有元素里最小的”。"
          "但队首可能已经滑出窗口——它的下标不满足 <code>i − M + 1 ≤ 下标 ≤ i</code>。"
          "于是每到一个位置，先 <code>while</code> 把下标 ≤ i − M 的队首弹掉，剩下的队首就是当前窗口的最小值。",
          "<b>为什么懒删除是对的。</b>我们从不主动删除“过期但不在队首”的元素，"
          "它们被埋在堆里不会有危害：只要它还没冒到队首，就轮不到它当答案；"
          "而一旦它冒到队首，<code>while</code> 会立刻把它清掉。每个元素最多被压一次、弹一次，总 O(N log N)。",
          "<b>输出时机。</b>当 <code>i ≥ M</code>（窗口凑满 M 个）时，队首就是答案，输出一行。"
          "注意清过期的动作要放在输出<b>之前</b>。",
          "<b>另一种写法。</b>用单调队列（deque）可以做到 O(N)：队列里的下标递增、对应数值也递增，"
          "进队前把队尾比它大的都弹掉，出队时看队首下标是否过期。那是第 48 节的内容；"
          "本题用堆已经够快，而且“懒删除”是处理“过期元素”的通用技巧。",
          "<b>复杂度。</b>每个元素入堆一次、出堆至多一次，每次堆操作 O(log N)，总 O(N log N) ≈ 1.7×10⁶。"],
    code=r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;

    // 小根堆：按 (数值, 下标) 排序
    priority_queue<pair<int, int>, vector<pair<int, int>>, greater<pair<int, int>>> pq;

    for (int i = 1; i <= n; ++i) {
        int x;
        cin >> x;
        pq.push({x, i});
        while (pq.top().second <= i - m) pq.pop();   // 滑出窗口的旧元素，懒删除
        if (i >= m) cout << pq.top().first << "\n";  // 窗口凑满，队首即答案
    }
    return 0;
}''',
    explain=[
        ("priority_queue&lt;pair&lt;int,int&gt;, vector&lt;...&gt;, greater&lt;...&gt;&gt;",
         "小根堆。默认的 priority_queue 是大根堆，要加 <code>greater</code> 才反过来。"
         "pair 先比 first 再比 second，所以相等时按下标排，不影响结果。"),
        ("pq.push({x, i});",
         "边读边处理，不需要把整张表存下来。下标 i 必须一起入堆，否则无法判断是否过期。"),
        ("while (pq.top().second &lt;= i - m) pq.pop();",
         "当前窗口是 [i−m+1, i]，下标 ≤ i−m 的都已经滑出去了。用 while 是因为可能连续几个都过期。"),
        ("if (i &gt;= m) cout &lt;&lt; pq.top().first;",
         "前 m−1 个位置窗口还没凑满，不输出。清过期的动作一定要在输出之前。"),
        ("greater&lt;pair&lt;int,int&gt;&gt;",
         "需要 <code>&lt;functional&gt;</code>，<code>bits/stdc++.h</code> 已经包含。写成自定义 cmp 也行，"
         "但结构体写法比函数写法啰嗦。"),
    ],
    pitfalls=["用大根堆：输出的是窗口最大值。忘了写 <code>greater</code> 是最常见的错。",
              "只 pop 一次而不写 while：连续过期两个元素时，队首仍然是过期的，答案错。",
              "把过期判断写成 <code>&lt; i - m + 1</code>：差一位，会把窗口最左端的元素也弹掉。",
              "在 <code>i &lt; m</code> 时就输出：前 m−1 行是多余的，输出行数不对。"],
    sample="输入：\n6 3\n1 3 2 5 4 6\n输出：\n1\n2\n2\n4")

CH5 = CH("海港", "P2058", "普及/提高-", "https://www.luogu.com.cn/problem/P2058",
         [P("有 n 艘船依次到港，第 i 艘船在 tᵢ 秒到达，船上有 kᵢ 名乘客，国籍分别是 xᵢ,₁ … xᵢ,kᵢ。"
            "tᵢ 递增。"),
          P("对每艘船，统计「到它到达为止的 24 小时（86400 秒）内」到港的所有乘客来自多少个不同的国家，"
            "即统计满足 tᵢ − 86400 &lt; tⱼ ≤ tᵢ 的船上所有乘客的不同国籍数。"),
          P("输入格式：第一行 n（1 ≤ n ≤ 10⁵，Σkᵢ ≤ 3×10⁵）；接下来 n 行，每行先是 tᵢ、kᵢ，"
            "再是 kᵢ 个国籍编号（≤ 10⁵）。"),
          P("输出格式：n 行，每行一个整数，表示第 i 艘船到达后的统计结果。")],
         hint=["窗口随时间往后滑，过期的人要从统计里去掉。哪种容器适合「先进先出、按时间排队」？",
               "如果记录「每个国家在窗口里有几个人」，一个国家从 0 变 1 时答案加 1，从 1 变 0 时答案减 1。",
               "队头什么时候该弹？注意题面是 tᵢ − 86400 &lt; tⱼ，边界的等号要小心。"],
         idea=["把所有乘客按到达顺序排进一个队列，每个元素存 (到达时刻, 国籍)。船与人的层级被压平。",
               "维护 cnt[c] = 窗口内国籍 c 的人数，以及 ans = 窗口内不同国籍数。",
               "一艘船到达：先把它的 kᵢ 个乘客逐个入队并更新 cnt（从 0 到 1 时 ans++）。",
               "再把队头所有「到达时刻 ≤ tᵢ − 86400」的乘客弹出，弹出时 cnt−−，减到 0 时 ans−−。",
               "为什么用 queue：时间递增，过期的永远在队头，且不会有人「重新进来」。每个乘客进队一次、出队一次。",
               "复杂度 O(Σkᵢ) = 3×10⁵ 次操作。若每艘船都把窗口内的乘客重扫一遍，是 O(n·Σkᵢ)，必 TLE。"],
         code=r'''#include <bits/stdc++.h>
using namespace std;

const int MAXN = 100005;
int cnt[MAXN];                 // cnt[c]：窗口内国籍 c 的乘客数

int main() {
    int n;
    scanf("%d", &n);

    queue<pair<int,int>> q;    // (到达时刻, 国籍)，按时间排队
    int ans = 0;               // 窗口内不同国籍数

    for (int i = 0; i < n; ++i) {
        int t, k;
        scanf("%d%d", &t, &k);
        for (int j = 0; j < k; ++j) {
            int c;
            scanf("%d", &c);
            q.push({t, c});            // 同一艘船的人分享同一个到达时刻
            if (cnt[c] == 0) ++ans;    // 这个国家在窗口里从无到有
            ++cnt[c];
        }
        // 队伍左端：超过 24 小时的人出队
        while (!q.empty() && q.front().first <= t - 86400) {
            int c = q.front().second;
            q.pop();
            --cnt[c];
            if (cnt[c] == 0) --ans;    // 这个国家在窗口里彻底消失
        }
        printf("%d\n", ans);
    }
    return 0;
}''',
         explain=[
             ("queue<pair<int,int>> q;", "队列里放「每个乘客」，不是「每艘船」：出队时按人扣减，计数才对得上。"),
             ("if (cnt[c] == 0) ++ans; ++cnt[c];", "先判「从无到有」再加人数。顺序反了（先 ++cnt 再判 0）就永远不成立，ans 一直是 0。"),
             ("while (!q.empty() && q.front().first <= t - 86400)", "窗口左边界：t − 86400。用 ≤ 正好把「恰好 86400 秒前」的人排除，符合题面的严格小于。"),
             ("--cnt[c]; if (cnt[c] == 0) --ans;", "出队一个人：人数减一；减到 0 说明这个国家整个离开窗口，国家数减一。"),
             ("printf(\"%d\\n\", ans);", "每艘船处理完立刻输出当前窗口答案——题目要的是每艘船一个结果，不是最后一次性输出。"),
         ],
         pitfalls=["计数顺序写反（先 ++cnt 再判是否为 0）→ ans 永远不加 → 全输出 0。",
                   "弹出条件写成 <code>&lt; t - 86400</code>：恰好 86400 秒前到的人被留在窗口里 → 边界数据 WA。",
                   "用 bool 数组标记「这个国家在窗口里出现过」：同一国家有多人时，走掉一个就以为整个国家消失了 → 答案偏小。必须用计数。",
                   "cnt 只开到 1000：国籍编号最大 10⁵ → 越界，表现为乱答案或 RE。"],
         sample="输入：\n3\n1 4 4 1 2 2\n2 2 2 3\n10 1 3\n\n输出：\n3\n4\n4")

CH6 = CH(
    "刺杀大使", "P1902", "提高-/提高", "https://www.luogu.com.cn/problem/P1902",
    [P("一个 n×m 的房间矩阵，相邻房间之间有门可走（上下左右）。第 1 行的每个房间都有通向外界的大门，"
       "是入口；第 n 行的 m 个房间里有 m 个机关，必须<b>全部</b>到达。"),
     P("除第 1 行与第 n 行外，每个房间都装了激光装置，进入就会受到 pᵢⱼ 点伤害"
       "（第 1 行与第 n 行的伤害值都是 0）。"),
     P("可以派任意多的人从任意入口进入。一个士兵受到的伤害等于他路径上所有房间伤害值的<b>最大值</b>，"
       "整个部队的伤害等于所有士兵伤害的最大值。求让所有人完成任务的<b>最小</b>部队伤害。"),
     P("输入格式：第一行两个整数 n、m；接下来 n 行，每行 m 个整数 pᵢⱼ。"
       "数据范围：n, m ≤ 1000，0 ≤ pᵢⱼ ≤ 1000。"),
     P("输出格式：一行一个整数，表示最小伤害代价。")],
    hint=["答案一定在 [0, max p] 之间。先想一个更简单的问题：如果规定“只能走伤害值 ≤ X 的房间”，"
          "能不能从第 1 行走到第 n 行？这个判定只要一次 BFS。",
          "“X 越大越容易走通”——这个单调性就是二分答案的信号。",
          "判定时不用真的走到第 n 行的每一间：第 n 行的伤害值全是 0，只要有一只脚踏上第 n 行，"
          "就能沿着第 n 行横着走遍所有机关。"],
    idea=["<b>第一步：把“最小化最大值”翻译成判定问题。</b>设 <code>ok(X)</code> = “只用伤害值 ≤ X 的房间，"
          "能否从第 1 行走到第 n 行”。那么题目的答案就是最小的满足 ok(X) 的 X——"
          "因为部队伤害取的是所有路径最大值中的最大值，而只要存在一条“每格都 ≤ X”的路径，"
          "伤害就能控制在 X 以内。",
          "<b>第二步：单调性。</b>X 变大，能走的房间只增不减，所以 <code>ok</code> 形如“假假…假真真…真”。"
          "二分 X 的取值区间 <code>[0, max p]</code>，每次判定 O(nm)，共约 log₂(1000) ≈ 10 次。",
          "<b>第三步：判定怎么写。</b>把所有第 1 行的格子作为多源起点（它们的 p = 0，一定 ≤ X），"
          "BFS 只走 <code>p ≤ X</code> 且没访问过的格子。一旦扩到任意一个 <code>x == n</code> 的格子，就返回 true。",
          "<b>为什么“到达一个就等于到达全部”。</b>第 n 行所有格子的伤害值都是 0 ≤ X，"
          "而且它们左右相邻、可以互相走通，所以从任意一个第 n 行的格子出发都能走遍整行。"
          "这一条把“必须到达每个机关”化简成“到达第 n 行”。",
          "<b>为什么二分下界取 0。</b>第 1 行与第 n 行伤害为 0，若 n = 1 则不需要经过任何有伤害的房间，"
          "答案是 0。取 0 作下界可以覆盖这种退化情况。",
          "<b>复杂度。</b>每次判定 O(nm)；二分 10 次，总计约 10⁷ 次操作，"
          "n, m = 1000 时 1 秒内跑完。空间只需要 p 数组（4MB）和 vis（1MB）。",
          "<b>为什么不能直接求最短路。</b>“路径上最大值最小”是极小极大问题，"
          "它没有“距离可以相加”的结构，最短路算法用不上；二分 + 连通性判定才是标准解法。"],
    code=r'''#include <bits/stdc++.h>
using namespace std;

int n, m;
int p[1005][1005];
bool vis[1005][1005];
int dx[4] = {1, -1, 0, 0};
int dy[4] = {0, 0, 1, -1};

bool ok(int X) {                          // 只走伤害值 <= X 的房间，能否到第 n 行
    memset(vis, 0, sizeof vis);
    queue<pair<int, int>> q;
    for (int j = 1; j <= m; ++j) {        // 第 1 行全是入口
        vis[1][j] = true;
        q.push({1, j});
    }
    while (!q.empty()) {
        auto [x, y] = q.front(); q.pop();
        if (x == n) return true;          // 踩到第 n 行就算成功
        for (int k = 0; k < 4; ++k) {
            int nx = x + dx[k], ny = y + dy[k];
            if (nx < 1 || nx > n || ny < 1 || ny > m) continue;
            if (vis[nx][ny] || p[nx][ny] > X) continue;
            vis[nx][ny] = true;
            q.push({nx, ny});
        }
    }
    return false;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cin >> n >> m;
    int mx = 0;
    for (int i = 1; i <= n; ++i)
        for (int j = 1; j <= m; ++j) {
            cin >> p[i][j];
            mx = max(mx, p[i][j]);
        }

    int lo = 0, hi = mx, ans = mx;
    while (lo <= hi) {                    // 找第一个可行的 X
        int mid = (lo + hi) / 2;
        if (ok(mid)) { ans = mid; hi = mid - 1; }
        else         lo = mid + 1;
    }
    cout << ans << "\n";
    return 0;
}''',
    explain=[
        ("bool ok(int X)", "判定函数只回答“能不能”，不回答“代价是多少”。二分答案的判定函数语义必须单一。"),
        ("for (int j = 1; j &lt;= m; ++j) { vis[1][j] = true; q.push({1, j}); }",
         "第 1 行所有格子都是入口，一起入队——这就是第 26 节的多源 BFS，一次扫完。"),
        ("if (p[nx][ny] &gt; X) continue;", "整个判定只有这一处与 X 有关：伤害超标的房间当作墙。"),
        ("if (x == n) return true;",
         "踩到第 n 行立刻返回。不需要检查具体哪一间，因为第 n 行伤害全为 0、整行连通。"),
        ("memset(vis, 0, sizeof vis);", "每次判定都要重新清空。写成 <code>sizeof(vis)</code> 一次清 1MB，"
                                        "10 次共 10MB 的写入，可以忽略。"),
        ("if (ok(mid)) { ans = mid; hi = mid - 1; }",
         "可行就往小的方向继续找——“第一个可行的 X”的标准写法。若求“最后一个可行的”，就换成 lo = mid + 1。"),
        ("int lo = 0, hi = mx;", "上界取输入里出现过的最大伤害值。取一个更大的常数（如 1000）也能过，"
                                 "但用实测上界能让二分少几步。"),
    ],
    pitfalls=["把“到达第 n 行”写成“到达第 n 行的每一间”：判定退化成需要记住走了哪几列，复杂度和正确性都毁了。",
              "二分写成找“最后一个可行”：答案会偏大。题目要的是最小可行值。",
              "判定里忘了清空 vis：上一轮的访问痕迹把这一轮的路堵死，ok 恒为 false，答案变成上界。",
              "BFS 起点只放了 (1,1)：其他入口被漏掉，某些数据会错判为不可行。"],
    sample="输入：\n3 3\n0 0 0\n1 2 5\n0 0 0\n输出：\n1",
)
CHS = [CH1, CH2, CH3, CH4, CH5]

LESSONS = [LESSON(
    30, "回顾六：BFS、二分与容器",
    "把第 26~29 节压成一套动作：BFS 求无权最短路，二分答案处理单调性，"
    "queue / stack / priority_queue 决定「下一次取谁」。先抄一遍 P3958 的完整模板，"
    "再用 5 道洛谷黄题限时训练，每题都带完整思路与参考代码。",
    95, ["回顾", "5 题"], "普及/提高-",
    SEC, check=CHECK, challenge=CH1, challenge2=CH6, refs=[
        "《算法竞赛入门笔记》：BFS、二分查找与 STL 容器相关章节",
        "《算法竞赛进阶指南》第 0x25 节：广度优先搜索；第 0x04 节：二分",
        "《算法竞赛试炼场：洛谷300题精析》：P3958、P1141、P1873、P1182、P2251、P2058、P1902 的题解",
        "《算法竞赛黄金法则》：先证明单调性，再动手二分",
        "想再练一道纯栈模拟，加做 P4387 验证栈序列 / P1449 后缀表达式（不计入本次限时）",
    ])]

# 回顾章由 render.render_review 渲染，读的是 challenges 列表（复数）
LESSONS[0]["challenges"] = CHS
