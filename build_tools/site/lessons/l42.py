# -*- coding: utf-8 -*-
"""第 42 节 · 最短路：Dijkstra 与 Floyd"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dsl import *  # noqa

SEC = []

SEC.append(P("第 26 节已经会用 BFS 求最短路了，但它有一条隐形前提：<b>每条边的代价都相等</b>。"
             "有了这条前提，“先到”才等于“最近”。题目一旦给出边权 3、7、1 这样的数字，"
             "这个前提就碎了 —— 走两步的路径可能比走一步的代价还小。"))

SEC.append(P("于是要换判据：不比“第几层”，比“当前累计代价谁最小”。"
             "把 BFS 的队列换成按 dist 排序的容器，就得到 <b>Dijkstra</b>；"
             "把“一次算一个源点”改成“一次算所有点对”，就得到 <b>Floyd</b>。本节就这两个。"))

SEC.append(Q("Dijkstra 的全部正确性压在一句话上：每次取出当前 dist 最小的点，它的 dist 已经不会再变小了。"
             "边权非负是这句话成立的唯一理由。"))

SEC.append(T(["算法", "解决什么", "复杂度", "对边权的要求", "什么时候用"], [
    ["BFS（第 26 节）", "单源", "O(n + m)", "全部相等（通常为 1）", "无权图、最少步数"],
    ["Dijkstra（堆优化）", "单源", "O((n + m) log n)", "非负", "绝大多数单源题，m 到 10⁶"],
    ["Floyd", "全源（所有点对）", "O(n³)", "允许负边，不能有负环", "n ≤ 300~500，或要任意两点距离"],
    ["Bellman-Ford / SPFA", "单源 + 判负环", "O(nm)", "允许负边", "有负权边时（本节只提一句）"],
]))

SEC.append(P("先记三个数字，它决定了你该选谁。<b>①</b> n = 10⁵、m = 2×10⁵ 时，一次堆优化 Dijkstra 约 "
             "(n + m)·log m ≈ 3×10⁵ × 18 ≈ 5×10⁶ 次操作，稳过。<b>②</b> n = 500 时 Floyd 是 1.25×10⁸ 次内层操作，"
             "约 0.3 秒，能过。<b>③</b> n = 1000 时 Floyd 是 10⁹，必超时 —— 而同样规模下跑 1000 次 Dijkstra 是 10⁹ 级，"
             "也不行。所以“n 小用 Floyd”里的“小”是 500，不是 5000。"))

# ---------------------------------------------------------------- 新函数
SEC.append(P("本节的代码里只多了一个东西：一个能按“距离最小”自动排序的队列。"
             "它由 <code>priority_queue</code> 加 <code>pair</code> 加 <code>greater</code> 拼成，三样都要看准。"))

SEC.append(FN(
    "priority_queue 存 pair（堆里放 (距离, 点号)）",
    "priority_queue<pair<int,int>, vector<pair<int,int>>, greater<pair<int,int>>> pq;\npq.push({d, u});",
    [("pair&lt;int,int&gt;", "把“距离”和“点号”打成一个元素。Dijkstra 的堆里一个元素就是一条“到 u 的距离是 d”的<b>记录</b>，"
                           "不是点本身 —— 同一个 u 可以有多条记录。"),
     ("第一个参数（元素类型）", "必须是 pair，因为堆里要同时带走距离和点号。只放点号的话，取出来还得回表查 dist，"
                              "而 priority_queue 不支持按 dist 排序。"),
     ("第二个参数 vector&lt;pair&lt;int,int&gt;&gt;", "底层容器。想换比较器就必须把它写出来 —— "
                                                  "这是 priority_queue 模板最反直觉的地方：<b>三个参数得写全</b>。"),
     ("第三个参数 greater&lt;...&gt;", "比较器。<code>greater</code> 让“更小的”排在堆顶，于是 top() 是距离最小的记录，"
                                      "这正是“小根堆”。"),
     ("pq.push({d, u})", "花括号直接构造 pair，等价于 <code>push(make_pair(d, u))</code>。"),
     ("pq.top()", "取堆顶，返回 const 引用，<b>不能直接改</b>。要拆开用结构化绑定："
                  "<code>auto [d, u] = pq.top();</code>（C++17）。"),
     ("pq.pop()", "删掉堆顶，返回 void。所以 top 和 pop 必须成对写，顺序不能反。"),
     ("不能遍历、不能删任意元素", "只有 top / push / pop。Dijkstra 靠“重复入堆 + 取出时判旧值”绕开“修改已入堆元素”这个做不到的操作。")],
    example=r'''// 小根堆：(距离, 点号)，距离小的先出
priority_queue<pair<int,int>, vector<pair<int,int>>, greater<pair<int,int>>> pq;

pq.push({5, 3});                     // 到 3 号点距离 5
pq.push({2, 7});                     // 到 7 号点距离 2
pq.push({2, 4});                     // 距离同为 2，点号小的在前

while (!pq.empty()) {
    auto [d, u] = pq.top();          // C++17 结构化绑定，拆成两个变量
    pq.pop();
    cout << u << "(" << d << ") ";   // 输出 4(2) 7(2) 3(5)
}''',
    notes=["元素类型和比较器必须匹配。距离用 long long 时整个写法都要改成 "
           "<code>pair&lt;long long,int&gt;</code> 配 <code>greater&lt;pair&lt;long long,int&gt;&gt;</code>，"
           "漏改一个就是满屏模板报错。",
           "同一个点会在堆里出现多次（每次 dist 被改小就 push 一份）。这不是 bug，是“懒删除”的代价，"
           "取出时用 <code>if (d != dist[u]) continue;</code> 过滤即可。"],
    brief="把“到哪个点、距离多远”打成 pair 塞进小根堆"))

SEC.append(FN(
    "greater 对 pair 的比较（字典序，first 优先）",
    "greater<pair<A,B>>\n// 等价于 a > b，按字典序：先比 first，first 相等再比 second",
    [("字典序比较", "pair 的 <code>&gt;</code> 是<b>先比 first，first 相等才比 second</b>。"
                   "<code>greater</code> 把它倒过来用，于是“更小的”排在堆顶。"),
     ("所以 first 必须是距离", "堆顶 = 距离最小的记录。<b>写成 {u, d} 就变成“点号最小的先出堆”</b>，"
                              "距离完全没参与比较，“取最小即确定”的依据当场消失。"),
     ("first 相同时比 second", "距离相同的两条记录按点号升序出堆。这只影响同距离点之间的先后，不影响答案。"),
     ("为什么不能写 greater&lt;int&gt;", "元素是 pair，比较器必须能比较 pair。<code>greater&lt;int&gt;</code> "
                                        "和元素类型对不上，报错会指到模板深处。"),
     ("等价写法一：负数", "<code>priority_queue&lt;pair&lt;int,int&gt;&gt; pq;</code> 配 <code>push({-d, u})</code>，"
                          "用负号把大根堆当小根堆用。少写两个模板参数，但每个 d 前都要加负号，漏一次就是灾难。"),
     ("等价写法二：自定义结构体", "元素是自己写的 struct 时没有现成的 greater，要重载 <code>operator&lt;</code> "
                                 "或写函数对象（第 28 节），方向与 sort 的 cmp <b>相反</b>。")],
    example=r'''pair<int,int> a = {3, 9}, b = {3, 2}, c = {4, 1};
cout << (a > b) << " " << (a > c) << "\n";   // 1 0：first 相等时看 second；3 < 4 所以 a < c

// 所以小根堆里 {3,2} 先于 {3,9}，两者都先于 {4,1}
priority_queue<pair<int,int>, vector<pair<int,int>>, greater<pair<int,int>>> pq;
pq.push({9, 3});        // ✗ 把点号写在了 first：堆按 9 排序，距离 3 根本没参与
pq.push({3, 9});        // ✓ first = 距离 3，second = 点号 9
// 错写法里 {9,3} 和 {3,9} 比的是两个 first（9 与 3），也就是两个"点号"''',
    notes=["<code>greater</code> 在 <code>&lt;functional&gt;</code> 里，<code>bits/stdc++.h</code> 已包含。",
           "记住一句话：<b>堆里第一个字段永远是排序依据</b>。Dijkstra 里它必须是距离。"],
    brief="pair 按字典序比，greater 让小者居堆顶"))

# ---------------------------------------------------------------- 例题
SEC.append(EX("【模板】单源最短路径（标准版）", "P4779", "普及/提高-",
              "https://www.luogu.com.cn/problem/P4779",
              [P("给定一个 n 个点、m 条有向边的带非负权图，请计算从 s 出发到每个点的最短距离。"
                 "数据保证从 s 出发能到达任意点。"),
               P("输入格式：第一行三个正整数 n、m、s；第二行起 m 行，每行三个非负整数 u、v、w，"
                 "表示从 u 到 v 有一条权值为 w 的有向边。"),
               P("输出格式：一行 n 个空格分隔的非负整数，第 i 个数表示 s 到 i 的距离。"),
               P("数据范围：1 ≤ n ≤ 10⁵，1 ≤ m ≤ 2×10⁵，s = 1，1 ≤ u, v ≤ n，0 ≤ w ≤ 10⁹，0 ≤ Σw ≤ 10⁹。")],
              sample="输入：\n4 6 1\n1 2 2\n2 3 2\n2 4 1\n1 3 5\n3 4 3\n1 4 4\n输出：\n0 2 4 3"))

SEC.append(IDEA("例题怎么想：BFS 换成堆，只改一处", [
    P("<b>① dist 的定义和 BFS 一样。</b>dist[v] 表示“当前已知的 s 到 v 最短距离”。dist[s] = 0，"
      "其余设成一个极大的数 INF。<b>注意是极大，不是 0</b> —— 全 0 等于宣布“所有点都已经到达且距离为 0”，"
      "后面一条边都松弛不动。"),
    P("<b>② 重复做一件事：取出未确定的点里 dist 最小的那个 u，用它松弛所有出边。</b>"
      "“松弛”就是三角不等式：<code>if (dist[u] + w &lt; dist[v]) dist[v] = dist[u] + w;</code>。"
      "BFS 里这一步是 <code>dist[v] = dist[u] + 1</code>，因为不用比也知道更优。"),
    P("<b>③ 为什么取最小就能“确定”。</b>假设弹出的 u 的 dist 还不是真正的最短距离 d(u)。"
      "在 s→u 的真实最短路上，从 s 开始找第一个还没被确定的点 y。y 之前的点都已确定并松弛过，"
      "所以 dist[y] = d(y)。因为边权非负，最短路越往后越长，所以 d(y) ≤ d(u)；"
      "又因为 u 是当前未确定点里 dist 最小的，所以 dist[u] ≤ dist[y]。串起来："
      "d(y) ≤ d(u) &lt; dist[u] ≤ dist[y] = d(y)，矛盾。∎ "
      "<b>“边权非负”只用在这一步</b>，这是全节最值得记住的一句话。"),
    P("<b>④ 用堆代替线性扫描。</b>朴素写法每次在 n 个点里找最小是 O(n²)；"
      "把 (dist, u) 丢进小根堆，top() 就是最小，代价 O(log n)。"),
    P("<b>⑤ 懒删除。</b><code>priority_queue</code> 不能改已入堆的值，也不能删任意元素，"
      "所以 dist 变小时就再 push 一份新的，旧记录留在堆里。取出时判断 "
      "<code>if (d != dist[u]) continue;</code> —— 对不上说明这条是过期记录，扔掉。"),
    P("<b>⑥ 复杂度。</b>每条边最多触发一次 push，所以最多 push m + 1 次；堆大小 ≤ m + 1；"
      "每次 push/pop 是 O(log m)。总复杂度 O((n + m) log m)，写成 O((n + m) log n) 也一样。"),
    C(r'''// 骨架：初始化 → 源点入堆 → 弹堆顶 → 懒删除 → 松弛 → 新值入堆
vector<long long> dist(n + 1, INF);
dist[s] = 0;
pq.push({0, s});
while (!pq.empty()) {
    auto [d, u] = pq.top(); pq.pop();
    if (d != dist[u]) continue;                 // 过期记录，扔掉
    for (auto &e : g[u]) {                      // 只扫 u 的出边，每条边一生只被扫一次
        int v = e.first, w = e.second;
        if (dist[u] + w < dist[v]) {            // 三角不等式
            dist[v] = dist[u] + w;
            pq.push({dist[v], v});              // 新值入堆，旧值不管
        }
    }
}''', "骨架：六步"),
]))

SEC.append(P("把骨架补全就得到下面的程序。两个细节值得先看：邻接表存的是 <code>pair&lt;int,int&gt;</code>"
             "（终点 + 边权），所以不用 <code>struct Edge</code>；距离用 <code>long long</code>，"
             "虽然本题 Σw ≤ 10⁹ 用 int 也够，但换一道题（边权 × 点数）就会爆，统一 long long 省心。"))

SEC.append(C(r'''#include <bits/stdc++.h>
using namespace std;

typedef long long ll;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m, s;
    cin >> n >> m >> s;

    // 邻接表：g[u] 里每一项是 (终点, 边权)
    vector<vector<pair<int,int>>> g(n + 1);
    for (int i = 0; i < m; ++i) {
        int u, v, w;
        cin >> u >> v >> w;
        g[u].push_back({v, w});        // 有向边，只加一次
    }

    const ll INF = (ll)4e18;           // 4e18 + 4e18 仍在 long long 内
    vector<ll> dist(n + 1, INF);
    dist[s] = 0;                       // 源点到自己是 0

    // 小根堆：first 是距离，堆顶永远是"当前距离最小的记录"
    priority_queue<pair<ll,int>, vector<pair<ll,int>>, greater<pair<ll,int>>> pq;
    pq.push({0, s});

    while (!pq.empty()) {
        auto [d, u] = pq.top();        // C++17：把 pair 拆成 d 和 u
        pq.pop();
        if (d != dist[u]) continue;    // 懒删除：这是 u 的旧记录

        for (auto &e : g[u]) {         // 引用遍历，不复制 pair
            int v = e.first, w = e.second;
            if (dist[u] + w < dist[v]) {          // 绕 u 更快
                dist[v] = dist[u] + w;
                pq.push({dist[v], v});            // 旧记录留在堆里，靠上面那行过滤
            }
        }
    }

    for (int i = 1; i <= n; ++i)
        cout << dist[i] << (i == n ? '\n' : ' ');
    return 0;
}''', "完整代码（C++17）"))

SEC.append(EXPLAIN("逐行拆解", [
    ("vector&lt;vector&lt;pair&lt;int,int&gt;&gt;&gt; g(n + 1);",
     "邻接表，每项是 (终点, 边权)。这里用 pair 而不是 struct Edge，因为只有两个字段、没有别的语义。"
     "构造函数给了 n + 1，下标 1..n 直接用。"),
    ("const ll INF = (ll)4e18;",
     "INF 要满足两件事：比任何可能的最短路都大，且 INF + w 不溢出。4e18 加 1e9 远小于 long long 上限 9.22×10¹⁸，"
     "所以 <code>dist[u] + w</code> 不会变成负数。"),
    ("vector&lt;ll&gt; dist(n + 1, INF);",
     "全部先当不可达。这一行的关键在于<b>不是 0</b>：初值给 0，所有点都“已到达且距离 0”，"
     "任何 <code>dist[u] + w &lt; dist[v]</code> 都不成立，程序输出一行 0。"),
    ("dist[s] = 0;",
     "源点到自己是 0。别漏，漏了源点也是 INF，堆里第一条记录就是 (INF, s)，后面全乱。"),
    ("priority_queue&lt;pair&lt;ll,int&gt;, vector&lt;pair&lt;ll,int&gt;&gt;, greater&lt;pair&lt;ll,int&gt;&gt;&gt; pq;",
     "三段拼出来的小根堆。first 是距离，所以 top() 给的是“当前最小距离的记录”。"
     "把 greater 换成默认的 less，就变成每次取最大，答案全错。"),
    ("pq.push({0, s});",
     "只把源点入堆，不是把所有点都塞进去。堆里只该有“距离被更新过”的记录。"),
    ("auto [d, u] = pq.top(); pq.pop();",
     "先取出再删除。结构化绑定等价于 <code>ll d = pq.top().first; int u = pq.top().second;</code>，"
     "但只调一次 top()。"),
    ("if (d != dist[u]) continue;",
     "懒删除。u 的距离可能被改小过好几次，堆里躺着好几份 (d, u)，只有 d == dist[u] 的那份是最新的。"
     "删掉这行答案仍正确，但过期记录也会去扫一遍出边，度数大的点被改多次时可能 TLE。"),
    ("for (auto &amp;e : g[u])",
     "引用遍历，不复制 pair。e.first 是终点 v，e.second 是边权 w。写成 <code>auto e</code> 也能跑，只是多一次拷贝。"),
    ("if (dist[u] + w &lt; dist[v])",
     "松弛的三角不等式。dist[u] 此刻已是最优值，所以只需检查“绕过 u 这一条边”是否有改善 —— "
     "这正是“每个点只处理一次”的依据。"),
    ("pq.push({dist[v], v});",
     "新距离入堆。注意 push 的是 dist[v] 而不是 d + w（两者相等，但前者可读性更好，也不怕以后改写法）。"),
    ("(i == n ? '\\n' : ' ')",
     "n 个数一行，行末只换行。多一个空格在某些严格比对的题上会 WA。"),
]))

# ---------------------------------------------------------------- Floyd
SEC.append(AFTER("Floyd：三重循环，一次算出所有点对", [
    P("Dijkstra 解决“一个源点到所有点”。如果要<b>所有点对</b>的距离，跑 n 次 Dijkstra 是 "
      "O(n(m + n) log n)，n = 500 时约 8.5×10⁸，太慢；而 Floyd 是 O(n³) = 1.25×10⁸，反而更快。"
      "<b>稠密图上，Floyd 常常是更优的选择。</b>"),
    P("思路是动态规划。定义 f<sub>k</sub>(i, j) = 只允许把编号 1..k 的点当作中转点时，i 到 j 的最短距离。"
      "从 k−1 推到 k 只有两种选择：<b>不用 k</b>，还是 f<sub>k−1</sub>(i, j)；"
      "<b>用 k</b>，就是 f<sub>k−1</sub>(i, k) + f<sub>k−1</sub>(k, j)。于是"),
    P("f<sub>k</sub>(i, j) = min( f<sub>k−1</sub>(i, j), f<sub>k−1</sub>(i, k) + f<sub>k−1</sub>(k, j) )。"),
    P("k 这一维可以滚掉：算 f<sub>k</sub> 时 f<sub>k−1</sub>(i, k) 与 f<sub>k−1</sub>(k, j) 的值和 "
      "f<sub>k</sub> 的那两个值相同（最短路经过 k 本身不会变得更短，除非有负环），所以直接就地覆盖成二维数组即可。"
      "<b>这就是为什么 k 循环必须写最外层 —— 它是 DP 的阶段维。</b>"),
    C(r'''#include <bits/stdc++.h>
using namespace std;

const int N = 305;
const long long INF = (long long)4e18;
long long f[N][N];

int main() {
    int n, m;                      // n ≤ 300
    cin >> n >> m;
    for (int i = 1; i <= n; ++i)
        for (int j = 1; j <= n; ++j)
            f[i][j] = (i == j ? 0 : INF);          // ★ 自己到自己是 0
    for (int i = 0; i < m; ++i) {
        int u, v, w; cin >> u >> v >> w;
        f[u][v] = min(f[u][v], (long long)w);      // 重边取最小
    }
    for (int k = 1; k <= n; ++k)                   // ★ 阶段：必须最外层
        for (int i = 1; i <= n; ++i) {
            if (f[i][k] == INF) continue;          // 剪枝：i 到不了 k，这一层白算
            for (int j = 1; j <= n; ++j)
                if (f[i][k] + f[k][j] < f[i][j])
                    f[i][j] = f[i][k] + f[k][j];
        }
    // 到这里 f[i][j] 就是 i 到 j 的最短路
}''', "Floyd 骨架"),
    P("<b>k 放里层会错，给一个具体反例。</b>4 个点、3 条边 1→3、3→4、4→2，权都是 1，正确答案 d(1, 2) = 3。"
      "若写成 <code>for i for j for k</code>：算 (i = 1, j = 2) 时需要用 f[1][4]，"
      "而 f[1][4]（要等 j = 4 才算）此刻还是 INF，于是 f[1][2] 永远停在 INF。"
      "这类错误的表现是“一部分点对正确、一部分是 INF 或偏大”，极难靠小样例发现。"),
    P("Floyd 还白送三件东西：<b>①</b>允许负权边（只要没有负环）；"
      "<b>②</b>判负环 —— 跑完看 <code>f[i][i] &lt; 0</code>，说明有负环（正常应该等于 0）；"
      "<b>③</b>传递闭包 —— 把 <code>min</code> 换成 <code>or</code>、<code>+</code> 换成 <code>and</code>，"
      "得到的就是“i 能否走到 j”，三重循环一个字不用改。"),
]))

# ---------------------------------------------------------------- 负权
SEC.append(AFTER("负权边为什么不能 Dijkstra", [
    P("给一个三点反例，能一次看清问题：边 1→2 权 2，1→3 权 5，3→2 权 −4。真实答案是 d(2) = 1（绕 3 号点走）。"
      "Dijkstra 的执行顺序是：dist = [0, 2, 5]，先弹出 2 号点（dist = 2 最小），把它当最终值；"
      "再弹出 3 号点，松弛 3→2 得到 1 —— 但 2 号点已经处理完了，答案停在 2。"
      "<b>这一段描述的是带“弹出即确定”标记的经典实现</b>（弹出后 <code>vis[u] = true</code> 并不再更新 u），"
      "本节代码没有这个标记，结论见第三段。"),
    P("坏在哪一步？回到前面的证明：那句 <b>d(y) ≤ d(u)</b> 用的是“最短路越往后越长”，"
      "而这条性质只在边权非负时成立。有负边时，最短路可能越走越短，“先取出的最小点”就不再是确定的。"),
    P("还要说清楚一个细节，很多资料含糊过去：<b>本节这种“懒删除、不加 vis”的写法，在负权图上最终仍会给出正确答案</b>，"
      "因为每次距离变小都会重新入堆，等价于堆版的 Bellman-Ford —— 但复杂度从 O((n + m) log n) 退化成 O(nm) 量级，"
      "SPFA 的卡法能把它卡死。而只要你为了提速加上“弹出即确定”（<code>if (vis[u]) continue; vis[u] = true;</code>），"
      "负权图上就是彻底的 WA。"),
    P("所以结论不变，只是理由更精确：<b>Dijkstra 的复杂度保证依赖非负权，正确性在带“确定”标记的实现里也依赖它。"
      "有负权边时用 Bellman-Ford / SPFA，并且用它顺手判负环。</b>"),
    P("最后一个容易忽视的推论：<b>无向图里只要出现一条负权边，就一定有负环</b>"
      "（这条边来回走一趟，总权变成负数，可以无限刷小），此时最短路根本不存在。所以看到“无向图 + 负边”"
      "要么题目保证没有，要么答案是 −∞，不要指望任何最短路算法给出有限值。"),
]))

SEC.append(WARN("本节的 8 个坑，每个都有具体症状", [
    "dist 用默认值 0 初始化（全局数组、或 <code>vector&lt;ll&gt; dist(n + 1)</code>）：所有点都“已到达且距离 0”，"
    "一条边也松弛不动，输出一整行 0 → <b>WA</b>。这是本节第一大坑。",
    "INF 取得太小（如 1e9）：真实最短路超过 1e9 时会被当成“不可达”，输出 1000000000 → <b>WA</b>。"
    "INF 取 INT_MAX：<code>INF + w</code> 溢出成负数，负数被当成更短的路 → <b>WA</b>。",
    "删掉 <code>if (d != dist[u]) continue;</code>：答案仍对，但过期记录也会去扫一遍所有出边，"
    "高度数点被反复更新时工作量成倍上涨 → <b>TLE</b>。",
    "pair 写成 <code>{u, d}</code>（点号在前）：堆顶变成“点号最小的记录”，距离没参与比较，"
    "复杂度退化到 SPFA 级别，构造数据 → <b>TLE</b>；若你还加了“弹出即确定”的 vis，则直接 <b>WA</b>。",
    "忘记写 greater（用默认大根堆）：每次取当前<b>最大</b>距离的点，和“取最小即确定”完全相反。"
    "小数据可能因为反复入堆而碰巧收敛，一旦加 vis 就 <b>WA</b> —— 这种“样例能过”的隐患最危险。",
    "Floyd 的 k 循环写进 i、j 里层：部分点对停在 INF 或偏大 → <b>WA</b>，而且小样例常常是过的。",
    "Floyd 忘记 <code>f[i][i] = 0</code>：经过自己的转移全部失效（INF + x 还是 INF），答案偏大 → <b>WA</b>；"
    "反过来，用 0 初始化整个矩阵会得到“任意两点距离都是 0” → <b>WA</b>。",
    "用 int 存 dist：n = 10³、w = 10⁴ 时单程才 10⁷，看着够；但 n、w 各放大十倍就是 10⁹ 出头，"
    "再加一条边就溢出成负数 → <b>WA</b>。统一 long long，代价只是一点内存。",
]))

SEC.append(REPRO("关掉页面，从空文件把 P4779 敲一遍并提交。",
                 "自测数据就用样例：<code>4 6 1</code> 加 6 条边，答案应为 <code>0 2 4 3</code>。"
                 "手推一遍 Dijkstra 的出堆顺序（1 → 2 → 4 → 3），再和程序打印的对照。",
                 "改一改①：把 dist 的初值从 INF 改成 0，重跑样例。输出会变成一行 0 ——"
                 "亲眼确认“默认 0 等于宣布所有点都可达”。",
                 "改一改②：删掉 <code>if (d != dist[u]) continue;</code>，在 while 里加一个计数器统计出堆次数。"
                 "同一组数据对比加不加这一行时堆里到底弹了多少条过期记录。",
                 "改一改③：把 <code>greater&lt;...&gt;</code> 整段删掉（变成默认大根堆），重跑样例。"
                 "答案可能仍然正确 —— 想清楚为什么（提示：每次改进都会重新入堆），"
                 "以及为什么一旦加上“弹出即确定”的 vis 就会错。",
                 "改一改④：把 Floyd 代码里的 k 循环挪到 i、j 里面，用 4 个点、3 条边 "
                 "<code>1 3 / 3 4 / 4 2</code>（权都是 1）测 d(1, 2)。正确答案 3，错写法给 INF。"))

# ---------------------------------------------------------------- 数学补给
M = MATH("无穷大怎么选、复杂度怎么估、k 为什么必须在外层", [
    P("先解决最容易出错的小事：<b>INF 要同时满足三条</b>。"
      "① 比任何可能的最短路都大；② <code>INF + w</code> 不溢出；③ <code>INF + w</code> 仍要远大于任何真实路径，"
      "这样“不可达”的点不会因为加了一次边权就变成“可达”。"),
    P("若最短路长度的上界是 L = (n − 1)·w<sub>max</sub>，取 INF &gt; L 就够了。"
      "P4779 里 Σw ≤ 10⁹，所以 L ≤ 10⁹，INF = 10⁹ + 1 都行；但习惯上写 4e18。"),
    T(["选法", "数值", "两倍是否溢出", "适用"], [
        ["0x3f3f3f3f（int）", "1061109567", "2122219134 &lt; 2³¹−1，安全", "int 版最短路，最常用"],
        ["INT_MAX（int）", "2147483647", "溢出成负数，危险", "不要用"],
        ["4e18（long long）", "4×10¹⁸", "8×10¹⁸ &lt; 9.22×10¹⁸，安全", "long long 版"],
        ["1e18（long long）", "10¹⁸", "2×10¹⁸，安全", "也常用，但要确认 L &lt; 10¹⁸"],
    ]),
    P("再看复杂度怎么估，这是选算法的唯一依据。记 (n + m) log m 里的 log 按 18 算（m = 2×10⁵）："),
    T(["n", "m", "一次 Dijkstra", "n 次 Dijkstra（全源）", "Floyd n³"], [
        ["500", "10⁵", "1.7×10⁶", "8.5×10⁸", "1.25×10⁸"],
        ["10³", "10⁴", "1.4×10⁵", "1.4×10⁸", "10⁹"],
        ["10⁵", "2×10⁵", "5.4×10⁶", "5.4×10¹¹", "10¹⁵"],
    ]),
    P("表里最值得盯的是第一行：<b>n = 500 的稠密图上，Floyd 比“跑 500 次 Dijkstra”快 7 倍</b>。"
      "原因很朴素：Floyd 的内层只有一次加法、一次比较、一次赋值，而 Dijkstra 每次出堆都要做 log 级别的比较，"
      "常数大得多。所以“Dijkstra 一定比 Floyd 快”是错的 —— <b>看 n、m 的比例</b>。"),
    P("最后解释 k 循环的位置。Floyd 是一个 DP：阶段 k 表示“允许用编号 ≤ k 的点当中转”。"
      "转移只从 k−1 层来，所以必须<b>按层推进、层层算完</b>。k 放里层，等于在用“还没算好的中间结果”做转移，"
      "某些点对就会停留在旧值上。"),
    P("换个角度也说得通：最短路满足三角不等式 d(i, j) ≤ d(i, k) + d(k, j)。"
      "松弛就是把违反它的估计值改小。Floyd 的第 k 轮做完时，所有“只允许 1..k 当中间点”的三角不等式都成立；"
      "k 从 1 跑到 n，所有可能的中转点都被检查过一遍，留下的就是最短路。"),
    P("顺带两条能直接用的结论：<b>①</b> 跑完看 f[i][i] &lt; 0 就是在判负环；"
      "<b>②</b> 把 (min, +) 换成 (or, and) 就得到传递闭包 —— 同一个三重循环骨架，两种语义。"
      "这也是“矩阵乘法式”算法的开端：Floyd 本质上是 (min, +) 半环上的矩阵乘方。"),
])

THINK = [
    "如果图里有 0 权边，Dijkstra 还对吗？回到证明里看“d(y) ≤ d(u)”这一步 —— 它能扛住 0 权边，"
    "为什么扛不住负权边？只差一个等号还是不等号？",
    "要求“从 s 到每个点的最短路径<b>条数</b>”，该在 Dijkstra 的哪一步累加？"
    "为什么必须在“松弛成功”和“距离相等”两种情况分开处理，且相等时不能重新入堆？",
    "如果每条边的权只有 1 和 2 两种，能不能不用堆，把它做成 O(n + m)？"
    "提示：把每条权为 2 的边中间插一个虚拟点，拆成两条权为 1 的边（拆点），再用 BFS。",
    "Dijkstra 里什么时候可以提前退出？如果只关心“s 到 t 的距离”，弹出 t 的那一刻能不能停？"
    "换成“只关心 s 到某 k 个点的距离”呢？",
    "把 Floyd 的 (min, +) 换成 (max, min) 会得到什么？（提示：最大瓶颈路，答案是“路径上最小边权的最大值”。）"
    "为什么同一套循环换成 (max, +) 求最长路就不行了？",
    "如果边权是浮点数，Dijkstra 还成立吗？哪些地方要改（<code>d != dist[u]</code> 这一句首当其冲）？",
    "有 10⁵ 个点和 10⁵ 条边，但所有边的权都是非负整数且总和不超过 10⁶，能不能做得比 Dijkstra 更快？"
    "提示：桶排序式的 Dijkstra（Dial 算法），第 28 节的 0-1 BFS 是它在 W = 1 时的特例。",
]

CHECK = [
    "能不看资料默写堆优化 Dijkstra：dist 初始化、堆、弹出、懒删除、松弛、入堆。",
    "能说清为什么 first 必须是距离，并解释“取最小即确定”的证明中哪一步用到了非负权。",
    "能写出 0x3f3f3f3f 与 4e18 两种 INF，并说明为什么 INT_MAX 不行。",
    "能默写 Floyd 三重循环，并给出一个“k 放里层就错”的具体图。",
    "能举出三点反例说明负权边为什么让 Dijkstra 失效，并知道这种情况该换什么算法。",
    "拿到一道题，能根据 n、m 的大小在 Dijkstra、Floyd、n 次 Dijkstra 之间做出选择并说出理由。",
]

CH2 = CH(
    "牛的旅行 Cow Tours", "P1522", "提高-/提高", "https://www.luogu.com.cn/problem/P1522",
    [P("农场里有 n 个牧区，编号 1..n，每个牧区有自己的坐标，某些牧区之间有路直接相连。"
       "如果两个牧区能通过若干条路互相到达，就说它们属于同一片<b>牧场</b>（即连通块）。"
       "一片牧场的<b>直径</b>是这片牧场里最远的两个牧区之间的最短距离。"),
     P("目前至少有两片牧场互不连通。现在要<b>恰好修一条路</b>，连接两个不同牧场里的牧区，"
       "使连通后的新牧场直径尽可能小。求这个最小直径。"),
     P("输入格式：第一行一个整数 n（1 ≤ n ≤ 150）；接下来 n 行，每行两个整数 x、y（0 ≤ x, y ≤ 10⁵），表示牧区坐标；"
       "接下来 n 行，每行 n 个数字（0 或 1），给出对称邻接矩阵——第 i 行第 j 列为 1 表示 i、j 之间有直接道路。"),
     P("输出格式：一行一个实数，表示新牧场直径的最小值，保留六位小数。")],
    hint=["两个概念要分清：牧区是最小单位，牧场是连通的牧区集合；直径是<b>同一片牧场内</b>最远两点的最短路。"
          "n ≤ 150，能不能一次算出所有点对的距离？",
          "Floyd 之后，每个牧区到「自己这片牧场里最远那个点」的距离可以直接扫出来，记为 mx[i]；"
          "一片牧场的直径就是这片牧场里 mx 的最大值。",
          "新修 i–j 之后，新直径只可能是三种情况之一：左牧场原直径、右牧场原直径、"
          "或者「先走到 i，跨过新路到 j，再往右边最远处走」。三者取最大，再对所有 (i, j) 取最小。"],
    idea=["<b>① 全源最短路。</b>n ≤ 150，Floyd 三重循环 O(n³) = 3.4×10⁶，一次算出所有点对的距离。"
          "直接相连的两点边长取欧氏距离，不直接相连的设成 INF。",
          "<b>② 分牧场。</b>Floyd 跑完后 d[i][j] 仍然是 INF，说明 i、j 不同牧场；据此做一次 DFS 给每个点标上牧场编号。"
          "注意判据必须是「最短路还是 INF」，而不是「邻接矩阵上是 1」——后者只能看到直接相连。",
          "<b>③ 两个量。</b>mx[i] = max{ d[i][j] : j 与 i 同牧场 }；dia[c] = max{ mx[i] : i 属于牧场 c }。"
          "两者都是 O(n²) 扫出来。",
          "<b>④ 枚举新路。</b>对每一对不同牧场的点 i、j，新直径 = max( dia[ci], dia[cj], mx[i] + dist(i,j) + mx[j] )，"
          "取所有方案的最小值。dist(i,j) 是两点间的欧氏距离（新修的那条路）。",
          "<b>为什么新直径一定长这样。</b>连通后的最短路只有两种形态：完全在某片老牧场内，或者跨过新路。"
          "跨过的那条一定形如 a → i → j → b，其中 a 与 i 同牧场、b 与 j 同牧场，"
          "长度 = d(a,i) + dist(i,j) + d(j,b) ≤ mx[i] + dist(i,j) + mx[j]。两个上界都是可达的，所以新直径就是这三项的最大值。",
          "<b>复杂度。</b>Floyd 3.4×10⁶，标记与统计 O(n²)，枚举 O(n²)。n = 150 时总操作不到 10⁷，几十毫秒。",
          "<b>精度。</b>全程用 double，最后统一输出六位小数；不要在中间转成 int 或 float 存距离。"],
    code=r'''#include <bits/stdc++.h>
using namespace std;

const int N = 155;
const double INF = 1e18;
int n;
double x[N], y[N];
double d[N][N];          // d[i][j]：i 到 j 的最短距离
double far[N];           // far[i]：i 到本牧场内最远点的距离
double dia[N];           // dia[c]：第 c 个连通块的直径
int comp[N];

void dfs(int u, int c) {  // 只沿“有路且连通”的边扩散，给连通块编号
    comp[u] = c;
    for (int v = 1; v <= n; ++v)
        if (comp[v] == 0 && d[u][v] < INF / 2) dfs(v, c);
}

int main() {
    scanf("%d", &n);
    for (int i = 1; i <= n; ++i) scanf("%lf%lf", &x[i], &y[i]);

    char s[N];
    for (int i = 1; i <= n; ++i) {
        scanf("%s", s + 1);
        for (int j = 1; j <= n; ++j) {
            if (i == j) d[i][j] = 0;
            else if (s[j] == '1') d[i][j] = hypot(x[i] - x[j], y[i] - y[j]);
            else d[i][j] = INF;
        }
    }

    for (int k = 1; k <= n; ++k)                 // Floyd：n <= 150，O(n^3) = 3.4e6
        for (int i = 1; i <= n; ++i) {
            if (d[i][k] > INF / 2) continue;
            for (int j = 1; j <= n; ++j)
                if (d[i][k] + d[k][j] < d[i][j]) d[i][j] = d[i][k] + d[k][j];
        }

    int cc = 0;
    for (int i = 1; i <= n; ++i)
        if (comp[i] == 0) dfs(i, ++cc);

    for (int i = 1; i <= n; ++i) {
        far[i] = 0;
        for (int j = 1; j <= n; ++j)
            if (d[i][j] < INF / 2 && d[i][j] > far[i]) far[i] = d[i][j];
    }
    for (int i = 1; i <= n; ++i)
        if (far[i] > dia[comp[i]]) dia[comp[i]] = far[i];

    double ans = INF;
    for (int i = 1; i <= n; ++i)                 // 枚举新修的那条路的两端
        for (int j = 1; j <= n; ++j) {
            if (comp[i] == comp[j]) continue;    // 必须连两个不同牧场
            double cur = far[i] + hypot(x[i] - x[j], y[i] - y[j]) + far[j];
            if (dia[comp[i]] > cur) cur = dia[comp[i]];    // 新直径不会小于原来的两段
            if (dia[comp[j]] > cur) cur = dia[comp[j]];
            if (cur < ans) ans = cur;
        }

    printf("%.6f\n", ans);
    return 0;
}''',
    explain=[
        ("d[i][j] = hypot(x[i] - x[j], y[i] - y[j]);",
         "直接相连的两点，边长就是欧氏距离。用 hypot 免得自己写 sqrt 时漏掉开方或写错平方。"),
        ("else d[i][j] = INF;", "不直接相连先当不可达，交给 Floyd 去拼。INF 取 1e18，加法不会溢出。"),
        ("dfs(i, ++cc)", "分牧场靠一次 DFS，判据是 d[u][v] < INF/2（最短路存在），不是邻接矩阵上的 1。"),
        ("if (far[i] > dia[comp[i]]) dia[comp[i]] = far[i];", "牧场直径 = 场里所有 far 的最大值。far 是「到本场最远点」，两者差一层 max。"),
        ("if (comp[i] == comp[j]) continue;", "题目要求新路连接两个<b>不同</b>牧场。同一牧场内修路不改变直径，却会让答案变小。"),
        ("if (dia[comp[i]] > cur) cur = dia[comp[i]];",
         "新直径必须同时不小于两片老牧场的直径——新路只是多了一条选择，不会让老距离变短。漏掉这一项答案偏小。"),
        ("printf(\"%.6f\\n\", ans);", "六位小数。double 有 15~16 位有效数字，n = 150、坐标 10⁵ 时精度足够。"),
    ],
    pitfalls=["把「牧区」当成「牧场」：n 是牧区数，牧场数是连通块个数，两者不是一个量。",
              "用邻接矩阵判连通块：绕两个点才连上的牧区会被漏掉，牧场数偏大、直径偏小 → WA。",
              "枚举 i、j 时不做牧场判断，或让 i == j：同一片牧场里的点对也参与了取最小，答案偏小。",
              "新直径只算 far[i] + dist + far[j]，忘了跟两片老牧场的直径取最大：样例就会差一截。"],
    sample="输入：\n8\n10 10\n15 10\n20 10\n15 15\n20 15\n30 15\n25 10\n30 10\n"
           "01000000\n10111000\n01001000\n01001000\n01110000\n00000010\n00000101\n00000010\n"
           "输出：\n22.071068",
)

CH = CH(
    "邮递员送信", "P1629", "普及/提高-", "https://www.luogu.com.cn/problem/P1629",
    [P("邮局在 1 号点，要送 n − 1 件东西到 2..n 号点。城市里所有道路都是<b>单行道</b>，共 m 条。"
       "邮递员每次只能带一件东西，送完必须返回邮局。"),
     P("求送完这 n − 1 件东西并最终回到邮局所需的最少总时间。"),
     P("输入格式：第一行两个整数 n、m；接下来 m 行，每行三个整数 u、v、w，表示从 u 到 v 有一条耗时 w 的单行道。"),
     P("输出格式：一行一个整数，表示最少总时间。"),
     P("数据范围：1 ≤ n ≤ 10³，1 ≤ m ≤ 10⁵，1 ≤ w ≤ 10⁴，保证任意两点互相可达。")],
    hint=["每次出门的路线是 1 → i，回程是 i → 1，n − 1 次出差互不影响。"
          "所以总时间就是 Σ(d(1, i) + d(i, 1))，不要想成“一条大回路”。",
          "d(1, i) 跑一次 Dijkstra 就全有了。d(i, 1) 要对 n − 1 个 i 各跑一次吗？想想上一节的反向建图。",
          "把所有边方向掉个头，在反图上从 1 跑一次 Dijkstra —— 反图上 1 到 i 的最短路，就是原图上 i 到 1 的最短路。",
          "注意答案的最大量级：单程最坏约 10³ × 10⁴ = 10⁷，累加 10³ 次就是 10¹⁰，必须 long long。"],
    idea=["<b>拆开算。</b>送第 i 件东西的过程是“1 → i，再 i → 1”，与其他件无关，"
          "所以总时间 = Σ<sub>i=2..n</sub> ( d(1, i) + d(i, 1) )。两次 Dijkstra 就能得到全部 2(n − 1) 个值。",
          "<b>第一遍：正图。</b>以 1 为源点跑 Dijkstra，得到 distA[i] = d(1, i)。",
          "<b>第二遍：反图。</b>建一张把所有边反向的图，同样以 1 为源点跑 Dijkstra。"
          "反图上一条 1 → x<sub>1</sub> → … → i 的路径，在原图上正好是 i → … → x<sub>1</sub> → 1 的路径，长度相同。"
          "所以 distB[i] = d(i, 1)。",
          "<b>为什么不能只跑一遍。</b>正图给出的是“从 1 出发到各点”，"
          "而“从各点回到 1”在有向图里是完全不同的问题（单行道，去得回不得）。"
          "对每个点各跑一次是 O(n m log n) = 10³ × 10⁵ 量级，会超时；反图把它压回一次。",
          "<b>复杂度。</b>两遍堆优化 Dijkstra，O((n + m) log n)，n = 10³、m = 10⁵，约 2×10⁵ × 17 ≈ 3.4×10⁶ 次操作。",
          "<b>为什么不用 Floyd。</b>n = 10³ 时 10⁹ 次内层操作，超时；而且我们只需要 1 到各点、各点到 1 这两批值，"
          "Floyd 算的 10⁶ 个点对里绝大多数用不上。"],
    code=r'''#include <bits/stdc++.h>
using namespace std;

typedef long long ll;
const int N = 1005;
const ll INF = (ll)4e18;

int n, m;
vector<vector<pair<int,int>>> g, rg;   // g: 正图, rg: 反图
ll distA[N], distB[N];

// 从 s 出发的单源最短路，结果写进 d[1..n]
void dijkstra(vector<vector<pair<int,int>>> &gr, int s, ll *d) {
    for (int i = 1; i <= n; ++i) d[i] = INF;   // 全部先当不可达
    d[s] = 0;
    priority_queue<pair<ll,int>, vector<pair<ll,int>>, greater<pair<ll,int>>> pq;
    pq.push({0, s});
    while (!pq.empty()) {
        auto [du, u] = pq.top();
        pq.pop();
        if (du != d[u]) continue;              // 懒删除：过期记录
        for (auto &e : gr[u]) {
            int v = e.first, w = e.second;
            if (du + w < d[v]) {
                d[v] = du + w;
                pq.push({d[v], v});
            }
        }
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cin >> n >> m;
    g.resize(n + 1);
    rg.resize(n + 1);
    for (int i = 0; i < m; ++i) {
        int u, v, w;
        cin >> u >> v >> w;
        g[u].push_back({v, w});        // 正图：u → v
        rg[v].push_back({u, w});       // 反图：v → u，方向必须掉头
    }

    dijkstra(g, 1, distA);             // d(1, i)
    dijkstra(rg, 1, distB);            // 反图上从 1 出发 = 原图上 i 到 1

    ll ans = 0;
    for (int i = 2; i <= n; ++i)       // 1 号点是邮局自己，不算
        ans += distA[i] + distB[i];
    cout << ans << "\n";
    return 0;
}''',
    explain=[
        ("rg[v].push_back({u, w});",
         "全题的转折点。原边 u → v 在反图里存成 v → u，权值不变。这样“反图上 1 能到 i”就等价于"
         "“原图上 i 能到 1”，一次 Dijkstra 顶掉 n − 1 次。"),
        ("void dijkstra(vector<vector<pair<int,int>>> &gr, int s, ll *d)",
         "同一个函数跑两张图：传引用避免复制整张图，数组用指针传入 <code>ll *d</code>，"
         "传 <code>distA</code> 这种全局数组时会自动退化成指针。"),
        ("ans += distA[i] + distB[i];",
         "第 i 件东西的总耗时是“去 + 回”。i 从 2 开始，因为 1 号点是邮局，没有东西要送给自己。"),
        ("ll ans = 0;",
         "最大量级：单程最坏 (n − 1) × w = 999 × 10⁴ ≈ 10⁷，累加 999 次约 10¹⁰ —— "
         "超过 int 上限 2.1×10⁹，必须 long long。这是本题最容易漏的一处。"),
        ("for (int i = 1; i <= n; ++i) d[i] = INF;",
         "每次调用先重置。这里没写 0 而是 INF：写 0 就等于宣布“所有点距离 0”，一条边都松弛不动。"),
        ("if (du != d[u]) continue;",
         "懒删除。u 的距离每被改进一次就会 push 一份记录，堆里可能躺着好几份，"
         "只有 du == d[u] 的那份是最新的。"),
        ("if (du + w < d[v])",
         "松弛用本次弹出的 du 而不是 d[u]。通过懒删除后两者相等，但用 du 少一次数组访问，也更清楚。"),
        ("g.resize(n + 1); rg.resize(n + 1);",
         "开 n + 1 条空表，下标 1..n 直接用。两个 vector 分别在 main 里 resize，"
         "因为点数要到读入之后才知道。"),
        ("cout << ans << \"\\n\";",
         "只有一个整数，末尾换行。不要顺手输出“最少时间是：”这类提示语 —— 那会直接 WA。"),
    ],
    pitfalls=["把“回程”当成“去程”：只跑一遍正图，用 distA[i] 乘 2 当答案。有向图里两个方向的距离一般不同，必须建反图。",
              "反图加边时又写成 <code>rg[u].push_back({v, w})</code>：反图变成了正图的复制品，"
              "第二遍 Dijkstra 算的还是 d(1, i)，答案偏小。",
              "答案用 int：单程最坏 10⁷，累加 10³ 次约 10¹⁰，溢出成负数 → WA。累加与 dist 统一 long long。",
              "把单行道当无向边、每条边加两次：反向边凭空出现，去程和回程的距离都会变小 → WA。"],
    sample="自测小样例：\n输入：\n3 4\n1 2 1\n2 1 1\n1 3 5\n3 1 5\n输出：\n12",
)

LESSONS = [LESSON(
    42, "最短路：Dijkstra 与 Floyd",
    "把 BFS 的队列换成按 dist 排序的小根堆：Dijkstra 靠“每次取 dist 最小的点”做到 O((n + m) log n)，"
    "Floyd 用三重循环一次算出所有点对。重点是懒删除、INF 的选法，以及 k 循环为什么必须最外层。",
    75, ["Dijkstra", "Floyd", "堆优化"], "提高-",
    SEC, math=M, think=THINK, check=CHECK, challenge=CH, challenge2=CH2,
    refs=["《算法竞赛进阶指南》第 0x61 节：最短路",
          "《算法竞赛试炼场：洛谷 300 题精析》最短路章：堆优化与懒删除",
          "洛谷 P4779、P1629 题解区的高赞思路"],
)]
