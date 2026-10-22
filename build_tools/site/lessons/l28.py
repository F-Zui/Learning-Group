# -*- coding: utf-8 -*-
"""第 28 节 · 双端队列与优先队列"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dsl import *  # noqa

SEC = []

SEC.append(P("第 26 节的 BFS 只有一条规矩：所有点<b>从队尾进、从队头出</b>。这条规矩之所以对，"
             "是因为每条边的长度都等于 1 —— 先被发现的点一定不比后发现的远。"
             "可一旦边权出现 0，这个前提就断了：一个点是绕了三步才发现的，距离却可能和第一步就发现的点一样。"
             "<b>“第几层”不再等于“多远”</b>，所以要换容器。"))
SEC.append(P("本节的另一半内容方向刚好相反：有些问题根本不关心先后顺序，只关心"
             "<b>“当前最小的是谁”</b>。这时用 <code>priority_queue</code>（二叉堆），"
             "每次取最值 O(log n)，付出的代价是彻底放弃顺序。"))
SEC.append(Q("三种容器，三种规矩：queue 守顺序，deque 守“距离只差 0 或 1”，priority_queue 守“堆顶最值”。选错了不是慢一点，是答案错。"))

SEC.append(T(["容器", "元素怎么进出", "能拿到什么", "单次代价", "用在哪种题上"], [
    ["queue&lt;int&gt;", "队尾进、队头出", "最旧的元素", "O(1)", "边权全为 1 的 BFS、按层扩散"],
    ["deque&lt;int&gt;", "两端都能进、两端都能出", "最旧的和最新的", "O(1)", "0-1 BFS、滑动窗口最值（第 19 节）"],
    ["priority_queue&lt;int&gt;", "随便进、只能从堆顶出", "当前最大/最小", "O(log n)", "每步取当前最优、多路归并、Top-K"],
]))

SEC.append(P("表里只有 deque 那一行是新的容器，另外两个前面都见过。"
             "但“见过”和“能说清它为什么能两端 O(1) 插入”是两件事 —— deque 的内存是<b>分段</b>的："
             "一段一段申请，用一张表记录各段的首地址，头插就往前一段挂，尾插就往后一段挂，"
             "所以不像 vector 那样要把整块数据搬家。代价是元素不保证连续，"
             "<code>&amp;dq[0] + n</code> 这种指针算术在 deque 上是危险的。"))

# ---------------------------------------------------------------- 新函数
SEC.append(FN(
    "deque：双端队列的两端操作",
    "deque<int> dq;\ndq.push_back(x);   dq.push_front(x);\ndq.pop_back();     dq.pop_front();\ndq.front();        dq.back();",
    [("deque&lt;int&gt;", "头文件 &lt;deque&gt;（bits 已包含）。带下标的双端队列，<b>两端插入删除都是 O(1)</b>。"),
     ("push_back(x) / push_front(x)", "在队尾 / 队头插入一个元素。这是 deque 与 vector 的实质区别："
                                     "vector 的 push_front 是不存在的，insert(begin(), x) 是 O(n)。"),
     ("pop_back() / pop_front()", "删除队尾 / 队头元素，O(1)。<b>返回 void，不返回值</b>；要取值必须先 back() / front()。"),
     ("front() / back()", "读队头 / 队尾，O(1)，不删除。容器为空时调用是未定义行为，通常表现为 RE。"),
     ("empty() / size()", "判空 / 元素个数。pop 之前先判空，是本节所有代码的固定动作。"),
     ("dq[i]", "支持下标访问，O(1)。但一旦用下标，说明你只需要随机访问，那就该用 vector 了。")],
    example=r'''deque<int> dq;
dq.push_back(1);     // [1]
dq.push_back(2);     // [1, 2]
dq.push_front(0);    // [0, 1, 2]      只有 deque 能这么干
cout << dq.front() << dq.back();        // 02
dq.pop_front();      // [1, 2]
dq.pop_back();       // [1]

deque<int> d2;
// d2.front();       // 空容器上取 front：未定义行为，现场 RE
if (!d2.empty()) d2.pop_front();        // 正确写法：先判空''',
    notes=["deque 没有 reserve()，也不能用 memcpy / 指针遍历 —— 内存是分段的。",
           "0-1 BFS 里<b>只有边权为 0 才允许 push_front</b>。把边权为 1 的也插到队头，队列的距离序列不再递增，"
           "同一个点会被反复松弛，答案虽然还对，但最坏退化成 SPFA 量级 → TLE。"],
    brief="两端 O(1) 进出的队列；0-1 BFS 的核心工具"))

SEC.append(FN(
    "priority_queue 的三参数模板",
    "priority_queue<T, Container, Compare> q;",
    [("T（第 1 个参数）", "元素类型。可以是 int、long long、pair&lt;int,int&gt;，或自己写的 struct。"),
     ("Container（第 2 个）", "底层容器，默认 vector&lt;T&gt;。要求随机访问 + push_back + pop_back，"
                             "所以只能是 vector 或 deque，<b>写 list 会编译失败</b>。平时照抄 vector&lt;T&gt;。"),
     ("Compare（第 3 个）", "比较器，回答“谁排在后面”。默认 less&lt;T&gt;，于是 top() 是最大值；"
                           "写 greater&lt;T&gt; 则 top() 是最小值（第 17 节用过）。"),
     ("三个参数必须写全", "想换比较器，前两个也得一起写出来。只写 priority_queue&lt;int, greater&lt;int&gt;&gt; "
                         "会得到一屏指向 &lt;bits/stl_queue.h&gt; 的模板报错 —— 因为第二个位置固定是容器。"),
     ("自定义比较器", "写函数对象：struct Cmp { bool operator()(const Node &amp;x, const Node &amp;y) const "
                     "{ return x.w &gt; y.w; } }，然后 priority_queue&lt;Node, vector&lt;Node&gt;, Cmp&gt; q; "
                     "<b>不能直接传函数名</b>，除非用 decltype 取它的类型。"),
     ("Compare 的语义", "Cmp(a, b) == true 表示 a 的优先级<b>更低</b>、排在 b 后面。"
                        "所以想要小根堆，就要让“大的”优先级低 —— 传 greater，或写 x.w &gt; y.w。")],
    example=r'''// 写法一：小根堆
priority_queue<int, vector<int>, greater<int>> small;

// 写法二：pair 默认按 first 比，first 相同再比 second
priority_queue<pair<int, int>> p;              // 默认大根堆
p.push({2, 5}); p.push({2, 3}); p.push({1, 9});
cout << p.top().first << ' ' << p.top().second; // 2 5（first 同，second 大的在前）

// 写法三：自定义比较器，按 w 小的优先
struct Node { int w, id; };
struct Cmp { bool operator()(const Node &x, const Node &y) const { return x.w > y.w; } };
priority_queue<Node, vector<Node>, Cmp> q;''',
    notes=["priority_queue 不能遍历、不能删除任意元素、<b>不能修改已入堆元素的值</b>（改了也不会重排）。"
           "要“改值”就再 push 一份新的，取出时和记录里的最新值比一下，旧的那份就跳过。",
           "pair 的默认比较是字典序：{dist, id} 放进小根堆，距离小的先出，距离相同时 id 小的先出。"
           "如果题目对同距离的顺序敏感，就别依赖这个次序。"],
    brief="元素类型 + 底层容器 + 比较器；缺一个参数就编译不过"))

# ---------------------------------------------------------------- 例题
SEC.append(EX("最小函数值", "P2085", "普及/提高-", "https://www.luogu.com.cn/problem/P2085",
              ["有 n 个函数 F_i(x) = a_i·x² + b_i·x + c_i，定义域是正整数 x = 1, 2, 3, …。"
               "把所有函数在所有正整数上取到的值合在一起，求其中最小的 m 个，按升序输出（重复的值各算一个）。",
               "输入格式：第一行两个整数 n、m；接下来 n 行，每行三个正整数 a_i、b_i、c_i。",
               "输出格式：m 行，每行一个整数，依次为第 1 小、第 2 小……第 m 小的函数值。",
               P("数据范围：1 ≤ n, m ≤ 10⁴，a_i 恒为正（保证每个函数在正整数上单调递增）。")]))

SEC.append(IDEA("把无穷多个值砍成 n 个有序序列", [
    P("<b>第一步：每个函数自己是有序的。</b>a_i ＞ 0，抛物线开口向上，对称轴在 x = −b_i/(2a_i) ＜ 0，"
      "所以整数部分 x ≥ 1 整段都落在增区间上：F_i(1) ≤ F_i(2) ≤ F_i(3) ≤ …。"
      "这一步把“无穷多个值”变成了“一条递增序列”。"),
    P("<b>第二步：问题变成 n 路归并。</b>每个函数贡献一条递增序列，全局前 m 小就是这 n 条序列归并后的前 m 项。"
      "这和第 17 节合并果子是同一个结构：<b>每一步在 n 个候选里取最小</b>。"),
    P("<b>第三步：候选只需要 n 个。</b>对第 i 个函数，只把“它当前还没输出的最小项”放进堆。"
      "堆顶就是全体候选的最小值，输出它，然后让这个函数往前走一格（x 加 1）再放回去。"
      "其他函数的候选没变，不用动。"),
    P("<b>为什么不会漏。</b>堆里始终装着每条序列“尚未输出部分”的首元素。"
      "全局最小必然等于某条序列尚无输出的首元素，所以它一定在堆里 —— 取堆顶就是取全局最小。"),
    P("<b>为什么只推进 m 次。</b>输出 m 个数就结束；每个函数最多被推进 m 次，"
      "堆的大小恒为 n，总复杂度 O((n + m) log n)。n = m = 10⁴ 时是 2×10⁴ 次堆操作、每次约 14 次比较，"
      "总共几十万次比较，可以忽略不计。"),
    C(r'''// 核心只有三步：取堆顶 -> 输出 -> 同一函数推进一格
Node cur = pq.top();
pq.pop();
cout << cur.val << '\n';
int nx = cur.x + 1;                   // 只推进这一个函数，别的候选不动
long long nv = f[cur.id].a * nx * nx + f[cur.id].b * nx + f[cur.id].c;
pq.push({nv, cur.id, nx});''', "每次输出的六个动作"),
]))

SEC.append(P("函数值最大能到 a_i·x² 量级，x 可以到 10⁴，所以乘积必须用 long long 存，"
             "这一点在代码里靠 <code>long long a</code> 让整条表达式自动提升。"))

SEC.append(C(r'''#include <bits/stdc++.h>
using namespace std;

struct Func { long long a, b, c; };   // 系数只存一份，堆结点里不重复存

struct Node {
    long long val;                    // 这个函数当前能给出的最小值
    int id, x;                        // 来自第 id 个函数，自变量取 x
    // 小根堆：val 大的"排在后面"。方向和 sort 的 cmp 相反（第 17 节）
    bool operator<(const Node &o) const { return val > o.val; }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;
    vector<Func> f(n);
    priority_queue<Node> pq;          // 大小恒为 n：每个函数只放一个候选

    for (int i = 0; i < n; ++i) {
        cin >> f[i].a >> f[i].b >> f[i].c;
        long long v = f[i].a + f[i].b + f[i].c;   // F_i(1) = a+b+c，a 是 long long 自动提升
        pq.push({v, i, 1});
    }

    for (int t = 0; t < m; ++t) {
        Node cur = pq.top();
        pq.pop();                     // pop 不返回值，所以先把堆顶存下来
        cout << cur.val << '\n';

        // 只让同一个函数往前走一格：其他函数的候选本来就在堆里，不需要重放
        const Func &g = f[cur.id];
        int nx = cur.x + 1;
        long long nv = g.a * nx * nx + g.b * nx + g.c;
        pq.push({nv, cur.id, nx});
    }
    return 0;
}''', "完整可编译代码（C++17）"))

SEC.append(EXPLAIN("逐行拆解", [
    ("struct Func { long long a, b, c; };",
     "系数单独存在 vector 里。堆里每个结点只带 id，重算时回表取系数，结点小、拷贝便宜。"),
    ("bool operator<(const Node &o) const { return val > o.val; }",
     "整个算法的方向由这一行决定。写成 val &lt; o.val 就是大根堆，每次弹出当前最大值，答案整片错。"
     "末尾的 const 不能漏，漏了报错指向模板深处。"),
    ("long long v = f[i].a + f[i].b + f[i].c;",
     "初始候选是 x = 1 的值。因为 a 是 long long，加法的每一步都按 64 位算，不会溢出。"),
    ("priority_queue<Node> pq;",
     "三个模板参数这里只写了第一个，因为另外两个用默认值（vector&lt;Node&gt; 和 less&lt;Node&gt;），"
     "而 less&lt;Node&gt; 会去调我们刚重载的 operator&lt;。"),
    ("Node cur = pq.top(); pq.pop();",
     "先复制再删。pq.pop() 返回 void，直接写 cur = pq.pop() 编译不过。"),
    ("cout << cur.val << '\\n';",
     "输出的是值，不是下标、也不是 x。这里最容易在改代码时手滑写成 cur.id。"),
    ("const Func &g = f[cur.id];",
     "引用而不是拷贝，避免每次迭代复制三个 long long；const 只是表明不修改。"),
    ("pq.push({nv, cur.id, nx});",
     "把<b>同一个函数</b>的下一个值放回去。写成别的 id，那条序列就会断层，答案偏大。"),
    ("pq 的大小恒为 n",
     "初始 n 个候选，每轮一出一进，所以堆永远是 n 个元素。O(m log n) 的前提就靠这一点。"),
]))

# ---------------------------------------------------------------- Top-K
SEC.append(AFTER("同一个堆，换个方向：Top-K 只留 k 个", [
    P("问题：n 个数里找出最大的 k 个（k 远小于 n），n 可以到 10⁶。"
      "排序是 O(n log n)，而<b>只留 k 个候选</b>可以做到 O(n log k)。"),
    P("做法：维护一个<b>大小为 k 的小根堆</b>。堆顶是“当前第 k 大”，也就是候选里最差的那个。"
      "新来的数只有比堆顶大，才可能挤进前 k，于是弹掉堆顶、把新数放进去；否则直接扔掉。"),
    P("为什么这样对：扫描到任意位置时，堆里恰好是“已扫描部分最大的 min(k, 已扫描个数) 个”。"
      "归纳一步：新数 x 若 ≤ 堆顶，则堆里已有 k 个数 ≥ 堆顶 ≥ x，x 挤不进前 k（最多与第 k 名并列）；"
      "若 x ＞ 堆顶，堆顶是 k 个里最差的，用 x 换掉它，剩下的仍然是最大的 k 个。"),
    C(r'''// n 个数里最大的 k 个，按降序输出
priority_queue<int, vector<int>, greater<int>> q;   // 小根堆，堆顶 = 第 k 大
for (int i = 0; i < n; ++i) {
    int x;
    cin >> x;
    if ((int)q.size() < k) q.push(x);               // 前 k 个直接进
    else if (x > q.top()) {                         // 只有更大才值得换
        q.pop();
        q.push(x);
    }
}
vector<int> ans;
while (!q.empty()) { ans.push_back(q.top()); q.pop(); }   // 弹出是升序
reverse(ans.begin(), ans.end());                   // 翻成降序''', "Top-K 的核心代码"),
    P("两个必须记住的细节：<b>①</b>堆的大小没到 k 时不能读 q.top()（空堆 RE），所以先判 size；"
      "<b>②</b>求“最小的 k 个”时方向完全反过来 —— 用大根堆，堆顶是第 k 小，条件是 x ＜ 堆顶。"
      "<b>堆顶永远是“当前候选里最差的那个”，被替换的永远是它。</b>"),
    P("代价对比：n = 10⁶、k = 10 时，log k ≈ 3.3，总比较约 3.3×10⁶ 次；排序要 2×10⁷ 次，差一个量级。"
      "k 接近 n 时两者差不多，直接 sort 更省事。"),
]))

# ---------------------------------------------------------------- 0-1 BFS
SEC.append(AFTER("0-1 BFS：只有两种边权时，deque 比堆便宜", [
    P("模型：n × m 的网格，每格有权 0 或 1。从左上角走到右下角，每步上下左右，"
      "进入一格的代价等于该格的权值，求最小总代价。"),
    P("<b>普通 BFS 不行。</b>BFS 的正确性依赖“先发现的更近”，而这里边权有 0："
      "同一个点可能被一条长路先发现（层数多），却被一条短路后到达（总代价小）。层数和距离脱钩了。"),
    P("<b>Dijkstra 行，但贵。</b>nm 个点各有一个 dist，每次取最小要堆，复杂度 O(nm log(nm))。"
      "可是这里边权只有 0 和 1，<b>dist 的最小值只有两种可能</b>：当前值 d，或 d + 1。"
      "两种值只需要两个“桶”，而 deque 恰好能当两个桶用 —— 这就是 0-1 BFS。"),
    P("规矩只有两条：从<b>队头</b>取点 u 扩展；若走到 v 的边权是 0，把 v <b>push_front</b>，"
      "若是 1，把 v <b>push_back</b>。"),
    P("<b>为什么队头一定是最小的。</b>设当前 dq 里的距离序列非递减，且只含 d 与 d + 1 两种值。"
      "从队头取出 dist = d 的点 u：边权 0 的新点距离也是 d，插到队头不破坏非递减；"
      "边权 1 的新点距离是 d + 1，插到队尾也不破坏非递减。<b>两条规矩都是为了保住这个不变式。</b>"
      "于是每次取出的都是当前最小，和 Dijkstra 一样，只是“堆”退化成了两个桶。"),
    C(r'''#include <bits/stdc++.h>
using namespace std;

const int N = 1005;
const int INF = 0x3f3f3f3f;
int n, m;
int w[N][N], d[N][N];
int dx[4] = {-1, 1, 0, 0}, dy[4] = {0, 0, -1, 1};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cin >> n >> m;
    for (int i = 0; i < n; ++i)
        for (int j = 0; j < m; ++j) {
            cin >> w[i][j];
            d[i][j] = INF;
        }

    deque<int> dq;                       // 存编号 x*m+y，省一个 pair 的拷贝
    d[0][0] = 0;
    dq.push_front(0);                    // 源点距离最小，从队头进
    while (!dq.empty()) {
        int id = dq.front();
        dq.pop_front();
        int x = id / m, y = id % m;      // 注意除的是列数 m，不是行数 n
        for (int k = 0; k < 4; ++k) {
            int nx = x + dx[k], ny = y + dy[k];
            if (nx < 0 || nx >= n || ny < 0 || ny >= m) continue;
            int nd = d[x][y] + w[nx][ny];
            if (nd >= d[nx][ny]) continue;   // 不比已知更优，就不必再进队
            d[nx][ny] = nd;
            if (w[nx][ny] == 0) dq.push_front(nx * m + ny);   // 0 边：插队头
            else                dq.push_back(nx * m + ny);    // 1 边：排队尾
        }
    }
    cout << d[n - 1][m - 1] << '\n';
    return 0;
}''', "0-1 BFS 的完整骨架"),
    EXPLAIN("0-1 BFS 的四个要点", [
        ("deque<int> dq; dq.push_front(0);",
         "源点必须从队头进：它的距离 0 是全图最小的。用 push_back 也碰巧对，但会破坏“队头最小”的阅读直觉。"),
        ("int x = id / m, y = id % m;",
         "编号是按行铺开的，所以模和除都用列数 m。用成 n 时只有方阵能过，非方阵立刻 WA —— 这类错极难自查。"),
        ("if (nd >= d[nx][ny]) continue;",
         "这里没有 visited，而且<b>不能有</b>：同一个点可能入队两次 —— 先被一条 1 边松弛到 d + 1，"
         "再被一条 0 边改小到 d（新的一份插到队头，会先出队）。所以判断条件必须是 nd &lt; d[nx][ny]。"
         "这一行也是复杂度的保证：每个点的 dist 最多被改小一次，即最多入队两次，总代价 O(V + E)。"),
        ("w[nx][ny] == 0 ? push_front : push_back",
         "整个算法只有这一行在区分两种边。判断的对象是<b>进入 v 的这条边的权值</b>，不是 u 的权值，"
         "也不是 dist 的奇偶。写错就退化成 SPFA。"),
        ("cout << d[n-1][m-1]",
         "终点代价含终点自己的权值（因为代价计在“进入”上）。若题面把代价定义在出发格，"
         "就要改成 d[n-1][m-1] + w[0][0] —— 读题时确认一次。"),
    ]),
]))

SEC.append(WARN("这一节的 7 个坑，每个都有具体症状", [
    "空 deque 上调用 front() / back() / pop_front()：未定义行为，几乎必然 <b>RE</b>。"
    "0-1 BFS 里忘记 push 源点，或者把 while 写成 do-while，第一轮就访问空容器。",
    "0-1 BFS 把 0 边的 push_front 写成 push_back：距离序列不再非递减，同一个点被反复松弛，"
    "<b>答案仍然正确但会超时（TLE）</b>。这种错在随机小数据上完全看不出来，必须用长链数据压。",
    "0-1 BFS 用 <code>int x = id / n</code>：只有 n == m 时才对，矩形网格一测就 <b>WA</b>。"
    "牢记“行优先编号，除和模都用列数”。",
    "priority_queue 自定义比较器方向写反（想要小根堆却写 <code>return val &lt; o.val;</code>）："
    "只有一个函数时看不出问题，n 个函数立刻 <b>WA</b>。方向口诀：cmp 写“谁在前”，operator&lt; 写“谁在后”。",
    "Top-K 用默认大根堆还写 <code>if (x &gt; q.top())</code>：堆顶是候选里最大的，新数几乎永远比不过它，"
    "结果输出的是前 k 个输入数 → <b>WA</b>（数据 <code>5 1 9 3 7 2</code>、k = 3 时会输出 1 5 9，正确答案 9 7 5）。",
    "用 int 存函数值或前缀乘积：P2085 里 a·x² 可到 10¹¹，溢出成负数后堆顶跑到最小端，"
    "输出一整片负数 → <b>WA</b>。凡是“平方”“乘积”“累加”，先估一遍量级。",
    "想修改已经 push 进堆的元素（比如把某个点的 dist 改小后直接改结构体字段）：堆内部顺序不会重排，"
    "之后 top() 拿到的是错的值 → <b>WA</b>。正确做法是 push 一份新值，取出时判旧值并跳过。",
]))

SEC.append(REPRO("关掉页面，把 P2085 的代码从零敲一遍并提交。",
                "自测数据：<code>2 4 / 1 1 1 / 1 1 2</code>，两个函数的值是 3,7,13,21 和 4,8,14,22，"
                "答案应为 3 4 7 8。手算一遍再对拍。",
                "改一改①：把 <code>operator&lt;</code> 里的 <code>val &gt; o.val</code> 改成 <code>val &lt; o.val</code>"
                "（变成大根堆），同一组数据，输出从 3 4 7 8 变成 4 8 14 22 —— 四个数全取自第二个函数，"
                "第一个函数一次都没出队。只改一个字符，却是本节最高频的错。",
                "改一改②：Top-K 代码把 <code>greater&lt;int&gt;</code> 删掉变成大根堆，跑 n = 6、k = 3、"
                "数据 <code>5 1 9 3 7 2</code>。正确答案是 9 7 5，改完得到 1 5 9 —— 亲手确认一次“堆顶是谁决定了一切”。"))

# ---------------------------------------------------------------- 数学补给
M = MATH("log 到底省了多少：堆的高度、Top-K 与两个桶", [
    P("堆是一棵完全二叉树：n 个结点时高度 h = ⌊log₂ n⌋ + 1。一次 push 或 pop 沿着一条从根到叶的路径上下移动，"
      "最多比较 h 次，所以是 O(log n)。<b>堆的所有复杂度都来自这一条路径。</b>"),
    T(["n", "⌊log₂ n⌋", "堆高 h", "n·log₂n 次比较", "n·log₂k（k = 10）次比较"], [
        ["10³", "9", "10", "10⁴", "3.3×10³"],
        ["10⁵", "16", "17", "1.7×10⁶", "3.3×10⁵"],
        ["10⁶", "19", "20", "2.0×10⁷", "3.3×10⁶"],
        ["10⁸", "26", "27", "2.7×10⁹", "3.3×10⁸"],
    ]),
    P("速记：<b>2¹⁰ = 1024 ≈ 10³</b>，所以每 10 次二分大约跨越 3 个十进制位。"
      "log₂(10⁶) = 19.9，log₂(10⁹) = 29.9 —— 十亿也就 30 层。竞赛里 n ≤ 10⁶ 时，"
      "log n 的常数按 20 估，堆操作 10⁶ 次约 2×10⁷ 次比较，在 1 秒内很宽裕。"),
    P("Top-K 的收益就来自把 log n 换成 log k：n = 10⁶、k = 10 时是 3.3×10⁶ 对 2.0×10⁷，差 6 倍；"
      "k = 10³ 时是 10⁷ 对 2×10⁷，只差 2 倍 —— <b>k 越大越不值得用堆</b>，这是选择排序还是堆的量化依据。"),
    P("0-1 BFS 省掉的则是整个 log。Dijkstra 每次要取 dist 最小的点，所以需要堆；"
      "而边权只有 0 和 1 时，队列中的 dist 只可能是 d 与 d + 1 两个值，"
      "<b>“取最小”退化成“看队头属于哪个桶”</b>，O(log V) 变成 O(1)，总复杂度从 O(E log V) 降到 O(V + E)。"),
    P("这类“值域很小的最短路”有统一名字：桶排序式的最短路（Dial 算法）。边权是 0…W 时开 W + 1 个桶循环使用，"
      "复杂度 O(E + W·V)；W = 1 就是本节的双端队列版本。"),
])

THINK = [
    "如果边权只有 0、1、2 三种，deque 还够用吗？想想需要几个“桶”，"
    "以及为什么不能简单地用两个 deque 循环装（提示：取最小的时候要同时看两个桶的头）。",
    "P2085 如果 m 到 10⁹ 而 n 只有 10，堆还合适吗？提示：二分答案 mid，"
    "数一数每个函数有几个 x 满足 F_i(x) ≤ mid —— 解一元二次不等式，O(n log C) 就能定位第 m 小。",
    "Top-K 要改成“只求第 k 大、不要排序”时，还能更快吗？回忆第 13 节的 nth_element 与快速选择，"
    "为什么它的期望复杂度是 O(n) 而不是 O(n log k)？",
    "把 0-1 BFS 的 deque 直接换成 priority_queue，答案还对吗？复杂度变成多少？"
    "在什么形状的数据上这两种写法几乎没差别？",
    "P2085 如果 a_i 允许为负，单调性就没了。这时该怎么办？"
    "提示：抛物线顶点在 x₀ = −b/(2a)，从顶点往两边各是一条单调序列，相当于每个函数贡献两条序列。",
    "为什么 0-1 BFS 的队列里元素距离“最多只差 1”？如果图里有 −1 权边，这个性质会怎么坏掉？"
    "再想想为什么负权图需要 Bellman-Ford 而不是 Dijkstra。",
    "用 deque 求滑动窗口最大值（第 19 节单调队列）时，为什么被淘汰的元素从队尾弹，而不是队头？"
    "把“队头”和“队尾”的角色说清楚，你就真的懂 deque 了。",
]

CHECK = [
    "能不看资料写出 deque 的四个两端操作，并说出它与 vector 的实质差别（以及它不能做什么）。",
    "能写出 priority_queue 的三参数模板，并解释三个参数各自为什么不能省。",
    "能说清 0-1 BFS 中 push_front 与 push_back 分别对应哪种权值，并给出“队头最小”的证明。",
    "能证明 P2085 中每个函数只推进 m 次，并算出总复杂度 O((n + m) log n)。",
    "能用一句话说明 Top-K 为什么用小根堆、堆顶代表什么、被替换的为什么是堆顶。",
    "知道 priority_queue 不能修改已入堆的值，要用“重新 push 一份 + 取出时跳过旧值”的办法。",
]

CH2 = CH(
    "电路维修", "P4667", "普及/提高-", "https://www.luogu.com.cn/problem/P4667",
    [P("一块 N 行 M 列的电路板上，每个格子是一个正方形元件：它的两条对角线中，只有一条接着导线，"
       "另一条不接。元件上画 <code>/</code> 或 <code>\\</code> 表示接着的是哪一条对角线。"),
     P("电源接在电路板的左上角（格点），灯接在右下角（格点）。导线只在格点上相连，"
       "所以电流要沿着元件里的对角线一段一段走。"),
     P("任意元件都可以旋转 90°（每旋转一个元件算 1 次操作）。求让灯亮起来所需的最少旋转次数；"
       "如果无论怎么转都接不通，输出 <code>NO SOLUTION</code>。"),
     P("输入格式：第一行 N、M（1 ≤ N, M ≤ 500）；接下来 N 行，每行 M 个字符，只含 <code>/</code> 或 <code>\\</code>。"),
     P("输出格式：一行，最少旋转次数，或 <code>NO SOLUTION</code>。"),
     P("样例：1×1 的元件画成 <code>/</code> 时，它接的是左下到右上，而电源在左上、灯在右下，通不了；"
       "旋转一次变成 <code>\\</code> 就接通了，所以答案是 1。")],
    hint=["把“格点”当节点、把“元件里的导线”当边，这就是一张图。元件不需要转时这条边权是 0，需要转时权是 1。",
          "边权只有 0 和 1，用普通 BFS 会错（它按边数分层，不按权值分层）。想想第 28 节的 deque 能怎么用："
          "权 0 的边放到队头，权 1 的边放到队尾。",
          "还有一个必须提前判掉的情况：从左上角走到右下角，横竖坐标之和的奇偶性是固定的——"
          "只有奇偶性匹配的格点才可能被走到，否则直接判无解。"],
    idea=["<b>建模。</b>把 (N+1)×(M+1) 个格点当作图的节点，编号 (i,j)（0 ≤ i ≤ N，0 ≤ j ≤ M）。"
          "每个元件 (i,j) 连接它的两条对角线中的一条：",
          L(["画 <code>\\</code>：连接左上 (i,j) 与右下 (i+1,j+1)；",
             "画 <code>/</code>：连接右上 (i,j+1) 与左下 (i+1,j)。"]),
          "<b>边权。</b>从当前格点沿元件里真实存在的对角线走到对面格点，花费 0；"
          "如果元件方向不对、必须旋转才能沿这条对角线走，花费 1。"
          "于是“最少旋转次数”= 从 (0,0) 到 (N,M) 的 0-1 最短路。",
          "<b>为什么普通 BFS 不行。</b>BFS 按“边数”分层，而这里一条 0 权边不花代价。"
          "若把 0/1 混在一起入队，某个点可能先被 1 权路径标记，之后又发现 0 权路径——没法更新。",
          "<b>0-1 BFS 的做法。</b>队列换成 <code>deque</code>：边权 0 时把新点 <code>push_front</code>，"
          "边权 1 时 <code>push_back</code>。这样队列里的距离始终只有两种取值、且非降，"
          "和普通 BFS 的“两层”性质一模一样，只是每层内又把 0 权边先处理完。"
          "复杂度 O(V + E) = O(NM)，每个格点最多被“稳定”两次。",
          "<b>松弛条件。</b>写成 <code>if (d + w &lt; dist[nx][ny]) { dist[nx][ny] = d + w; push... }</code>，"
          "而不是简单的“没访问过就入队”——因为同一个点可能先以较大的距离被访问，之后才找到更短的 0 权路。"
          "这是 0-1 BFS 与普通 BFS 最大的代码区别。",
          "<b>无解的奇偶性判断。</b>每走一个元件，格点的 (i+j) 奇偶性都改变一次（因为两个端点的 i+j 相差 1）。"
          "从 (0,0)（偶）走到 (N,M) 需要 N+M 步，所以 N+M 必须是偶数；否则一步都走不到，直接输出 "
          "<code>NO SOLUTION</code>。这一句能在最前面挡掉一半的无解数据。",
          "<b>量级。</b>节点数 (N+1)(M+1) ≤ 251001，每个节点 4 条出边，deque 操作均为 O(1)，"
          "总共约 10⁶ 次操作，1 秒内轻松跑完。"],
    code=r'''#include <bits/stdc++.h>
using namespace std;

const int MAXV = 505 * 505;
int n, m;
string g[505];                     // g[i][j]：第 i 行第 j 列的元件（0-based）
int dist[505][505];                // 到格点 (i,j) 的最少旋转次数，-1 表示没到过

struct Node { int x, y; };

int main() {
    cin >> n >> m;
    for (int i = 0; i < n; ++i) cin >> g[i];

    if ((n + m) % 2) {             // 奇偶性不匹配，永远走不到
        cout << "NO SOLUTION\n";
        return 0;
    }

    memset(dist, -1, sizeof dist);
    deque<Node> dq;
    dist[0][0] = 0;
    dq.push_front({0, 0});

    // 四个方向：目标格点 (nx,ny)、涉及的元件坐标、走这条对角线元件"应该"画成什么
    int dx[4] = {1, 1, -1, -1}, dy[4] = {1, -1, 1, -1};
    char want[4] = {'\\', '/', '/', '\\'};

    while (!dq.empty()) {
        Node u = dq.front(); dq.pop_front();
        int d = dist[u.x][u.y];
        if (u.x == n && u.y == m) break;            // 出了队首就说明它已是最短

        for (int k = 0; k < 4; ++k) {
            int nx = u.x + dx[k], ny = u.y + dy[k];
            if (nx < 0 || nx > n || ny < 0 || ny > m) continue;
            int cx = min(u.x, nx), cy = min(u.y, ny);   // 这一步跨过的元件坐标
            int w = (g[cx][cy] == want[k]) ? 0 : 1;     // 方向对 = 0，要转 = 1
            if (dist[nx][ny] == -1 || d + w < dist[nx][ny]) {
                dist[nx][ny] = d + w;
                if (w == 0) dq.push_front({nx, ny});    // 0 权走队头
                else        dq.push_back({nx, ny});     // 1 权走队尾
            }
        }
    }

    if (dist[n][m] == -1) cout << "NO SOLUTION\n";
    else                  cout << dist[n][m] << "\n";
    return 0;
}''',
    explain=[
        ("int dist[505][505];", "存的是“最少旋转次数”，不是“步数”。它是 0/1 权最短路，取值范围 0..NM。"),
        ("if ((n + m) % 2) { cout &lt;&lt; \"NO SOLUTION\"; }",
         "每走一个元件，(i+j) 的奇偶性必变。从 (0,0) 出发能到的格点必须满足 i+j 为偶数，"
         "所以 N+M 为奇数时终点根本不可达。这一句直接挡掉一半无解数据。"),
        ("deque&lt;Node&gt; dq;", "普通 queue 只能从队尾进；0-1 BFS 需要把 0 权的新点插到队头，所以必须用双端队列。"),
        ("int cx = min(u.x, nx), cy = min(u.y, ny);",
         "这一步跨过的元件的左上角坐标。因为 (nx,ny) 与 (u.x,u.y) 只差 1，取最小值正好是元件的位置。"),
        ("char want[4] = {'\\\\', '/', '/', '\\\\'};",
         "四条对角线与“元件应有的字符”的对应表。注意反斜杠在 C++ 字符串里要写成 <code>'\\\\'</code>。"
         "四个方向与四个字符必须一一对应，写错一个答案就整体偏大。"),
        ("int w = (g[cx][cy] == want[k]) ? 0 : 1;",
         "方向对就不用转（0），方向错就转一次（1）。这就是边权的全部来源。"),
        ("if (dist[nx][ny] == -1 || d + w &lt; dist[nx][ny])",
         "必须用“松弛”而不是“没访问过才进”。同一个格点可能先被一条 1 权路径访问，"
         "之后才被 0 权路径找到更优值。"),
        ("if (w == 0) dq.push_front(...); else dq.push_back(...);",
         "0-1 BFS 的核心一行：0 权插队头，1 权插队尾。这样队列里的距离始终只有两种取值。"),
        ("if (u.x == n &amp;&amp; u.y == m) break;",
         "终点一出队就可以停。因为 deque 保证出队顺序的距离非降，第一次出队即最短。"),
    ],
    pitfalls=["用普通 BFS 的“没访问过就入队”：0 权边和 1 权边混在一起，答案偏大。",
              "用了 deque 但仍然“访问过就不再更新”：漏掉了“后来发现更短的 0 权路”的情况。",
              "方向字符表写错（<code>/</code> 与 <code>\\</code> 对应反了）：所有边权整体反转，答案完全不对。",
              "忘了奇偶性判断：N+M 为奇数时答案应为 NO SOLUTION，但程序可能输出一个错误的小数字。"],
    sample="输入：\n1 1\n/\n输出：\n1",
)
CH = CH(
    "序列合并", "P1631", "普及/提高-", "https://www.luogu.com.cn/problem/P1631",
    [P("有两个长度都是 N 的序列 A、B。在 A 中取一个数、在 B 中取一个数相加，一共能得到 N² 个和。"
       "求这些和里最小的 N 个，按升序输出。"),
     P("输入格式：第一行一个整数 N；第二行 N 个整数 A_i；第三行 N 个整数 B_i。"),
     P("输出格式：一行 N 个整数，为最小的 N 个和，从小到大排列，用空格隔开。"),
     P("数据范围：1 ≤ N ≤ 10⁵，1 ≤ A_i, B_i ≤ 10⁹。")],
    hint=["N² 个和存都存不下（N = 10⁵ 时是 10¹⁰ 个），必须利用“有序”。先把 A、B 都升序排序，再观察结构。",
          "固定 A_i，序列 A_i + B_1, A_i + B_2, …, A_i + B_N 是递增的（因为 B 已排序）。"
          "于是 N² 个和 = N 个递增序列的并，问题变成多路归并。",
          "要求全局第 1 小，只需在这 N 个序列的首元素里取最小 —— 用一个堆维护这 N 个候选，"
          "取出之后只把被取走的那条序列往前推一格。"],
    idea=["<b>排序。</b>把 A、B 都升序排。设排好后 A_1 ≤ … ≤ A_N，B_1 ≤ … ≤ B_N。",
          "<b>转化。</b>对每个 i，S_i = (A_i + B_1, A_i + B_2, …, A_i + B_N) 是一条非递减序列。"
          "N² 个和正是这 N 条序列的全部元素。求最小的 N 个 = N 路归并取前 N 项。",
          "<b>候选。</b>每个序列只把首元素 A_i + B_1 放进堆：堆结点存 (和, i, j)，i 是行号，j 是 B 的下标。"
          "堆里初始有 N 个元素。",
          "<b>循环 N 次。</b>取堆顶输出；若 j &lt; N，把同一行的下一个 (A_i + B_{j+1}, i, j+1) 放回堆。"
          "一出一进，堆大小恒为 N。",
          "<b>正确性。</b>堆里始终是每条序列“尚未输出部分”的首元素，而序列内部非递减，"
          "所以全局最小必定是某个序列的首元素 —— 它一定在堆里。取出后只推进该序列，"
          "其余序列的首元素不变，不变式保持。",
          "<b>为什么只推进一格不会漏。</b>S_i 的第 j+1 项只有在第 j 项被取走之后，才可能成为全局最小"
          "（它 ≥ 第 j 项，而第 j 项当时就在堆里且更小）。",
          "<b>复杂度。</b>排序 O(N log N)，归并 N 次、每次 O(log N)，总共 O(N log N)，N = 10⁵ 轻松过。"],
    code=r'''#include <bits/stdc++.h>
using namespace std;

const int N = 100005;
int n;
long long a[N], b[N];

struct Node {
    long long val;          // 和：A_i + B_j
    int i, j;               // 来自 A 的第 i 个、B 的第 j 个（1-indexed）
    // 小根堆：val 大的排在后面（与 sort 的 cmp 反着写）
    bool operator<(const Node &o) const { return val > o.val; }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cin >> n;
    for (int i = 1; i <= n; ++i) cin >> a[i];
    for (int i = 1; i <= n; ++i) cin >> b[i];
    sort(a + 1, a + n + 1);
    sort(b + 1, b + n + 1);      // 两个都要排，只排一个序列就不单调了

    priority_queue<Node> pq;
    for (int i = 1; i <= n; ++i)
        pq.push({a[i] + b[1], i, 1});    // 每条序列只放首元素，共 N 个候选

    for (int t = 1; t <= n; ++t) {
        Node cur = pq.top();
        pq.pop();                        // pop 不返回值，先存堆顶
        cout << cur.val << (t == n ? '\n' : ' ');

        if (cur.j < n) {                 // 该行还有下一个，放回去
            int nj = cur.j + 1;
            pq.push({a[cur.i] + b[nj], cur.i, nj});
        }
    }
    return 0;
}''',
    explain=[
        ("sort(a + 1, a + n + 1); sort(b + 1, b + n + 1);",
         "两个序列都必须升序。只排 A 的话，固定 A_i 得到的 A_i + B_j 就不再单调，"
         "“堆里放首元素”的前提直接崩了。"),
        ("pq.push({a[i] + b[1], i, 1});",
         "初始候选是每条序列的最小项，共 N 个。不要把所有 N² 个和都塞进去 —— 内存和时间都不允许。"),
        ("bool operator<(const Node &o) const { return val > o.val; }",
         "取最小 → 小根堆 → operator&lt; 里写 val &gt; o.val。方向反了就是每次输出当前最大，答案整片错。"),
        ("cout << cur.val << (t == n ? '\\n' : ' ');",
         "行末不能多空格，用一个条件表达式控制分隔符。写成先输出再判空也等价，但别两边都加空格。"),
        ("if (cur.j < n)",
         "边界：j = N 时该行已经取完，不能再 push。不加这个判断会访问 b[N+1]，读到 0 或脏数据 → WA。"),
        ("pq.push({a[cur.i] + b[nj], cur.i, nj});",
         "只推进 cur 所在的这一行，i 必须沿用 cur.i。写成别的行号会让某条序列断层、另一条重复，答案错。"),
        ("long long val", "A_i、B_i 到 10⁹，两个相加到 2×10⁹，已经贴着 int 上限；必须 long long。"),
    ],
    pitfalls=["只排序一个序列：固定 A_i 后 A_i + B_j 不单调，堆里放的“首元素”不是最小，WA。",
              "把 N² 个和全部算出来再排序：N = 10⁵ 时是 10¹⁰ 个 long long，内存直接爆（MLE / RE）。",
              "弹出后忘记 push 下一项：堆会提前变空，循环还没走完就对空堆 top() → RE；"
              "只忘了 j 加 1（一直 push 同一个 j）：输出一堆重复值 → WA。",
              "用 int 存和：2×10⁹ 溢出成负数后堆序全乱 → WA。",
              "行末多输出一个空格：本机看不出，严格比对时会 WA。"],
)

LESSONS = [LESSON(
    28, "双端队列与优先队列",
    "把 BFS 的 queue 拆成两种新工具：deque 用两端插入把 0-1 BFS 做到 O(V+E)，"
    "priority_queue 用堆顶取最值解决多路归并与 Top-K。重点在“队头最小”的不变式与比较器方向。",
    60, ["deque", "priority_queue", "0-1 BFS"], "普及/提高-",
    SEC, math=M, think=THINK, check=CHECK, challenge=CH, challenge2=CH2,
    refs=["《算法竞赛进阶指南》第 0x26 节：广搜的变形（双端队列 BFS）",
          "《算法竞赛试炼场：洛谷 300 题精析》搜索章：0-1 BFS 与多路归并",
          "洛谷 P2085、P1631 题解区的高赞思路"],
)]
