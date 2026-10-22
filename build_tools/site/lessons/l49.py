# -*- coding: utf-8 -*-
"""第 49 节 · 堆与对顶堆、启发式合并"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dsl import *  # noqa

SEC = []

SEC.append(P("堆只有三条命令：push、pop、top，每次 O(log n)。第 17 节的贪心题里就用它挑最大 / 最小，"
             "这一节把它当积木：<b>两块拼成对顶堆求中位数</b>，<b>多块拼起来时讨论怎么合并最省</b>，"
             "最后看一眼支持 O(log n) 合并的左偏树。"))

SEC.append(Q("对顶堆的不变式只有一句：大根堆的元素个数 = 小根堆的元素个数，或比它多 1。"
             "于是中位数永远是大根堆的堆顶。"))

SEC.append(T(["任务", "做法", "单次代价", "总代价"], [
    ["动态中位数：插入 + 查询", "对顶堆（大根堆 + 小根堆）", "O(log n)", "n 次操作 O(n log n)"],
    ["合并两个 priority_queue", "没有 merge，只能 pop 出来再 push", "O(m log(n+m))", "—"],
    ["N 个集合反复两两合并", "启发式合并：小的并进大的", "搬一个元素 O(log n)", "O(n log² n)"],
    ["同上，改用可并堆", "左偏树 merge", "O(log n)", "O(n log n)"],
    ["子树信息合并", "DSU on tree：重儿子保留", "—", "O(n log n)"],
]))

# ---------------------------------------------------------------- 例题
SEC.append(EX("中位数", "P1168", "普及/提高-", "https://www.luogu.com.cn/problem/P1168",
              ["给出一个长度为 N 的非负整数序列 A<sub>1..N</sub>。对于所有 1 ≤ k ≤ (N+1)/2，"
               "输出 A<sub>1</sub>, A<sub>3</sub>, …, A<sub>2k−1</sub> 的中位数——也就是前 1、3、5、… 个数的中位数。",
               "输入：第一行一个整数 N（N ≤ 10<sup>5</sup>）；第二行 N 个整数 A<sub>i</sub>（0 ≤ A<sub>i</sub> ≤ 10<sup>9</sup>）。",
               "输出：共 (N+1)/2 行，每行一个整数，表示对应的中位数。"],
              sample="输入：\n7\n1 3 5 7 9 11 6\n输出：\n1\n3\n5\n6"))

SEC.append(P("例题里真正要维护的是“第 k 小”。先看两个这一节才会用到的成员函数，后面的合并与对顶堆都靠它们。"))

SEC.append(FN(
    "priority_queue::emplace",
    "pq.emplace(构造参数...);      // 等价于 pq.push(元素类型(构造参数...))",
    [("emplace(args...)", "把参数直接转给元素类型的构造函数，在容器内部原地构造，省掉“先造临时对象、再拷贝/移动进去”这两步。"),
     ("push 需要先有对象", "<code>push(make_pair(x, y))</code> 或 <code>push({x, y})</code>：先造一个临时 pair，再搬进去。"),
     ("和 pair 搭配最顺手", "<code>priority_queue&lt;pair&lt;int,int&gt;&gt;</code> 里写 <code>emplace(x, y)</code>，"
                            "直接构造出 <code>pair&lt;int,int&gt;(x, y)</code>，比较时先比 first 再比 second。"),
     ("参数必须能造出元素", "<code>priority_queue&lt;pair&lt;int,int&gt;&gt;</code> 里写 <code>emplace(1)</code> 编译失败——"
                            "pair 没有只接受一个 int 的构造函数。参数个数 / 类型不对时，报错信息埋在 construct 的模板里，"
                            "读不懂先数参数个数。"),
     ("没有返回值", "返回 void，别写 <code>x = pq.emplace(...)</code>。"),
     ("相等元素的顺序不确定", "堆只保证堆顶是极值；值相等的元素谁先出堆由内部结构决定，别依赖它。")],
    example=r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    priority_queue<pair<int, int>> pq;    // 先比 first，first 相同再比 second

    pq.emplace(3, 7);                     // 原地构造 pair(3, 7)
    pq.push(make_pair(4, 1));             // 老写法：先造对象再搬进去
    pq.push({5, 0});                      // 花括号也行

    cout << pq.top().first << " " << pq.top().second << "\n";   // 5 0
    cout << pq.size() << "\n";                                  // 3
    return 0;
}''',
    notes=["emplace 的参数个数、类型必须能匹配元素类型的某个构造函数，否则编译期报错——这是它比 push 唯一“难一点”的地方。",
           "速度差距在常数级（省一次拷贝），10<sup>6</sup> 次插入大约省几十毫秒；写起来更短才是主要收益。"],
    brief="原地构造，省一次临时对象，pair 元素尤其顺手"))

SEC.append(FN(
    "priority_queue::swap",
    "a.swap(b);          // 交换两个同类型堆的全部内容，O(1)\nswap(a, b);        // 同上，std::swap 走移动，也是 O(1) 级",
    [("O(1)", "只交换底层容器（vector/deque）的指针，一个元素都不搬。10<sup>6</sup> 个元素的堆互换也是常数时间。"),
     ("两个堆必须是同一类型", "<code>priority_queue&lt;int&gt;</code>（大根堆）和 "
                              "<code>priority_queue&lt;int, vector&lt;int&gt;, greater&lt;int&gt;&gt;</code>（小根堆）"
                              "是<b>不同类型</b>，swap 直接编译失败。"),
     ("用途 1：启发式合并", "<code>if (a.size() &lt; b.size()) a.swap(b);</code> 保证永远把小的往大的里搬。"),
     ("用途 2：O(1) 清空", "造一个空堆再 swap 进去，比 <code>while (!q.empty()) q.pop()</code> 的 O(n log n) 快得多。"),
     ("用 std::swap 也一样", "对容器来说 std::swap 内部就是三次移动构造，同样不搬元素。成员 swap 语义更直白。"),
     ("swap 之后比较器不变", "比较器是类型的一部分，跟着类型走，不会因为交换对象而改变。")],
    example=r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    priority_queue<int> a, b;
    a.push(1); a.push(2);          // a = {1, 2}，堆顶 2
    b.push(9);                     // b = {9}

    a.swap(b);                     // O(1)：现在 a = {9}，b = {1, 2}
    cout << a.top() << "\n";       // 9

    priority_queue<int> empty;
    a.swap(empty);                 // 也是 O(1) 清空

    // 大根堆和小根堆是两个类型，下面这行编译不过：
    // priority_queue<int> big;
    // priority_queue<int, vector<int>, greater<int>> small;
    // big.swap(small);            // error: no matching function for call to swap
    return 0;
}''',
    notes=["swap 只能交换“同一个模板实例”的对象。要对顶堆那样一大一小两个堆，只能老实 push/pop 搬元素。",
           "多测题里用一个空堆 swap 是最干净的重置方式，比重新声明局部变量更省事（尤其是全局堆）。"],
    brief="O(1) 交换两个同类型堆，启发式合并的关键一行"))

SEC.append(IDEA("例题怎么想：把有序数组从中间掰成两半", [
    "中位数的定义：i 个数从小到大排好后第 (i+1)/2 个（i 为奇数时唯一）。"
    "朴素做法是每来一个数就 sort 一遍，N = 10<sup>5</sup> 时约 10<sup>10</sup> 次比较，必然 TLE。",
    P("换个角度：不需要全序，只需要<b>中间那一个</b>。把已读入的数分成两半——"
      "小的那一半放<b>大根堆 big</b>（堆顶是这半边的最大值），大的那一半放<b>小根堆 small</b>"
      "（堆顶是这半边的最小值）。两个堆顶正好卡在有序数组的中间。"),
    P("只要维持一条不变式：<b>big 的大小 = small 的大小，或比它多 1</b>，那么 big 里恰好是最小的 (i+1)/2 个数，"
      "堆顶就是第 (i+1)/2 小——也就是中位数。"),
    P("每次插入做两件事：① 看新数和 big 堆顶的大小关系，决定进哪边；② 若不变式被破坏，"
      "把某一边的堆顶挪到另一边。一次插入最多挪一个元素，所以单次 O(log n)。"),
    C(r'''// ① 按大小关系归类
if (big.empty() || x <= big.top()) big.push(x); else small.push(x);

// ② 按数量关系拉平：big 的大小只能是 small 或 small + 1
if ((int)big.size() > (int)small.size() + 1) { small.push(big.top()); big.pop(); }
else if (big.size() < small.size())          { big.push(small.top()); small.pop(); }

// ③ 第奇数个数读完后，堆顶就是中位数
if (i & 1) printf("%d\n", big.top());''', "三步维护"),
    P("为什么不会连续挪多个：插入前不变式成立，插入后两边大小差最多变成 2，挪一次就恢复。"
      "这也是“对顶堆”能 O(log n) 的原因——它从不重排，只搬运一个堆顶。"),
]))

SEC.append(C(r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    scanf("%d", &n);

    priority_queue<int> big;                                 // 大根堆：存较小的一半
    priority_queue<int, vector<int>, greater<int>> small;     // 小根堆：存较大的一半

    for (int i = 1; i <= n; ++i) {
        int x; scanf("%d", &x);

        // ① 先按大小关系决定去左边还是右边
        if (big.empty() || x <= big.top()) big.push(x);
        else small.push(x);

        // ② 再按数量关系拉平：big 的大小只能是 small 或 small + 1
        if ((int)big.size() > (int)small.size() + 1) {
            small.push(big.top()); big.pop();
        } else if (big.size() < small.size()) {
            big.push(small.top()); small.pop();
        }

        // ③ 第奇数个数读完后总数为奇数，big 比 small 多一个，堆顶即中位数
        if (i & 1) printf("%d\n", big.top());
    }
    return 0;
}''', "完整代码"))

SEC.append(EXPLAIN("逐行拆解", [
    ("priority_queue<int> big;", "默认是大根堆：堆顶是最大值。它存“较小的一半”，所以堆顶是这半边的最大值，正是中位数。"),
    ("priority_queue<int, vector<int>, greater<int>> small;", "小根堆要写全三个模板参数：元素类型、底层容器、比较器。"
                                                              "greater&lt;int&gt; 表示“小的优先”，堆顶变成最小值。"),
    ("x <= big.top()", "比中位数小就归左半边。用 ≤ 还是 &lt; 都不影响正确性，关键是与后面平衡条件配套、前后一致。"),
    ("(int)big.size() > (int)small.size() + 1", "big 最多比 small 多 1 个。多到 2 个说明左边太重，把堆顶（左半边最大的）挪到右边。"
                                                "size() 是无符号数，要和 −1 之类的式子混算必须先转 int，否则空堆时会绕成巨大正数。"),
    ("big.size() < small.size()", "左边比右边少，把右边最小的挪过来。只可能差 1，所以一次就够。"),
    ("if (i & 1)", "题目只问前 1、3、5… 个数的中位数。总数为奇数时 big 恰好 (i+1)/2 个，堆顶就是第 (i+1)/2 小。"),
    ("printf(\"%d\\n\", big.top())", "每行一个。用 \\n 而不是 endl：N = 10<sup>5</sup> 时能省下十万次强制刷新。"),
]))

# ---------------------------------------------------------------- 堆的合并
SEC.append(P("priority_queue <b>没有 merge，也没有迭代器</b>，两个堆的内部数组不能直接拼（拼完不是堆）。"
             "想合并只有一条路：把一个堆的元素 pop 出来、push 进另一个。"))

SEC.append(P("单次合并的代价是 O(m log(n+m))，m 是较小堆的大小。只合一次的话这样足够。"
             "真正的麻烦是“N 个集合反复两两合并”——这时<b>合并顺序</b>决定复杂度。"))

SEC.append(C(r'''// 把 b 的全部元素搬进 a，并保证搬的是较小的那一堆
void mergeInto(priority_queue<int>& a, priority_queue<int>& b) {
    if (a.size() < b.size()) a.swap(b);      // ★ O(1)：只交换两个底层容器
    while (!b.empty()) {                     // 现在 b 一定是小的
        a.push(b.top());
        b.pop();
    }
}''', "启发式合并：小并大"))

SEC.append(EXPLAIN("三处关键", [
    ("a.swap(b)", "O(1) 交换整个容器，等价于“让 a 指向大的那堆”。没有它，就得手动判断方向、写两个分支。"),
    ("while (!b.empty()) { a.push(b.top()); b.pop(); }", "只能这样搬：priority_queue 不暴露内部数组，也没有 merge 接口。"),
    ("为什么总代价 O(n log² n)", "元素 x 每被搬一次，它所在集合的大小至少翻倍（因为它是从小的那边搬进大的）。"
                                 "所以 x 一生最多被搬 log₂ n 次；每次 push 是 O(log n)。合计 n log n 次 push，每次 log n。"),
    ("为什么不直接拼底层数组", "即使能拿到两段有序数据，拼起来也不是堆结构，还得花 O(n) 重建；"
                               "而 push 已经有 O(log n) 的增量维护。"),
    ("大根堆不能 swap 进小根堆", "两个类型不同，编译期就报错。想让对顶堆的两边互换，只能一个个 pop/push。"),
]))

# ---------------------------------------------------------------- DSU on tree
SEC.append(P("同一个“小并大”的思想搬到树上，就是 <b>DSU on tree</b>（树上启发式合并）。"
             "它解决的问题很固定：<b>对每个点 u，回答一个只与 u 的子树有关的问题</b>，"
             "而这个问题支持“加点、删点、随时取答案”这三种操作。"))

SEC.append(P("做法四步：① 求子树大小与重儿子；② 先递归所有<b>轻儿子</b>，算完把它们的贡献<b>清空</b>；"
             "③ 再递归<b>重儿子</b>，算完<b>保留</b>它的贡献；④ 把轻儿子的子树暴力加回来，加上自己，"
             "此时的答案就是 u 的答案；若 u 是轻儿子，用完再清空。"))

SEC.append(P("复杂度 O(n log n)：一个点被“暴力加入”的次数，等于它到根路径上轻边的条数；"
             "走一条轻边意味着父的子树大小至少是子的两倍，所以轻边不超过 log₂ n 条。"
             "每次加入是 O(1)（桶计数），合计 n log₂ n。"))

SEC.append(C(r'''#include <bits/stdc++.h>
using namespace std;
const int MAXN = 100005;

int n, c[MAXN];                     // c[u] = 点 u 的颜色
vector<int> g[MAXN];
int sz[MAXN], son[MAXN];            // 子树大小、重儿子
int cnt[MAXN], mx;                  // cnt[颜色] 出现次数；mx = 当前最大出现次数
long long sum, ans[MAXN];           // sum = 出现次数等于 mx 的颜色编号之和

void dfs1(int u, int p) {           // 第一遍：子树大小与重儿子
    sz[u] = 1;
    for (int v : g[u]) if (v != p) {
        dfs1(v, u);
        sz[u] += sz[v];
        if (sz[v] > sz[son[u]]) son[u] = v;   // sz[0] = 0，所以 son 初值 0 也能比
    }
}

void add(int u, int p, int d) {     // 把 u 子树的颜色整体加进 / 移出桶
    cnt[c[u]] += d;
    if (d > 0) {                    // 只加的时候维护答案，清空时不用管
        if (cnt[c[u]] > mx) { mx = cnt[c[u]]; sum = c[u]; }
        else if (cnt[c[u]] == mx) sum += c[u];
    }
    for (int v : g[u]) if (v != p) add(v, u, d);
}

void dfs2(int u, int p, bool keep) {
    for (int v : g[u]) if (v != p && v != son[u]) dfs2(v, u, false);   // 轻儿子：算完清空
    if (son[u]) dfs2(son[u], u, true);                                 // 重儿子：算完保留
    for (int v : g[u]) if (v != p && v != son[u]) add(v, u, 1);        // 轻儿子暴力补回来

    cnt[c[u]]++;                                                       // 加上自己
    if (cnt[c[u]] > mx) { mx = cnt[c[u]]; sum = c[u]; }
    else if (cnt[c[u]] == mx) sum += c[u];
    ans[u] = sum;

    if (!keep) { add(u, p, -1); mx = 0; sum = 0; }                     // 用完清空并复位
}

int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    cin >> n;
    for (int i = 1; i <= n; ++i) cin >> c[i];
    for (int i = 1; i < n; ++i) {
        int u, v; cin >> u >> v;
        g[u].push_back(v); g[v].push_back(u);
    }
    dfs1(1, 0);
    dfs2(1, 0, false);
    for (int i = 1; i <= n; ++i) cout << ans[i] << " ";
    cout << "\n";
    return 0;
}''', "DSU on tree：求每个子树中出现次数最多的颜色编号之和（n ≤ 10⁵，颜色编号 1..n）"))

SEC.append(EXPLAIN("四步与四个数组", [
    ("dfs1 求 sz 与 son", "重儿子 = 子树最大的儿子。所有“保留”都发生在重儿子上，所以它必须先算出来。"),
    ("dfs2(v, u, false) 轻儿子", "第三个参数 keep 表示“算完要不要保留贡献”。轻儿子一律 false，算完就清空。"),
    ("dfs2(son[u], u, true) 重儿子", "保留。重儿子那一大坨不用重新加，省下的正是 O(n log n) 里最贵的部分。"),
    ("add(v, u, 1) 把轻儿子加回来", "此时桶里已有重儿子的全部信息，只补轻儿子，代价 = 轻子树大小之和。"),
    ("cnt[c[u]]++ 与自己这一句", "别漏掉 u 自己。它不属于任何儿子，要单独加一次。"),
    ("if (!keep) { add(u, p, -1); mx = 0; sum = 0; }", "清空整棵 u 子树，并把 mx / sum 复位。"
                                                      "漏了复位，下一棵子树会沿用上一棵的最大值，答案全错。"),
]))

SEC.append(TIP("DSU on tree 的适用判定", [
    "问题只与「子树」有关，且不强制在线（可以先把所有答案算完再输出）。",
    "信息支持「加一个点 / 删一个点 / 取答案」三种操作，且加删都是 O(1) 级（桶计数、出现次数、颜色和这类）。",
    "如果信息不支持删除（比如最大值且要求精确回滚），就换线段树合并，或按 DFS 序整体离线处理。",
    "递归深度可能到 10<sup>5</sup>（树退化成链）。若 RE，先确认是不是爆栈，再考虑把递归改成手工栈。",
]))

# ---------------------------------------------------------------- 左偏树
SEC.append(P("启发式合并的 O(n log² n) 里，多出来的那个 log 是“每个元素都要 push 一次”。"
             "如果能<b>直接合并两个堆</b>、每次只走 O(log n) 步，总代价就降到 O(n log n)。"
             "这就是<b>可并堆</b>：左偏树是最常用的实现。"))

SEC.append(P("左偏树用 ls[]、rs[] 两个数组表示二叉树，另外记一个 dist。它只保证一件事："
             "<b>每个点的左子树 dist ≥ 右子树 dist</b>。于是从根一路往右走的“右路径”很短，"
             "merge 只沿右路径递归，自然 O(log n)——而右路径长度不超过 log₂(n+1)，这一点在数学补给里证。"))

SEC.append(FN(
    "左偏树 merge（可并堆）",
    "int merge(int x, int y);      // 合并两棵左偏树，返回新根；0 表示空树",
    [("x, y", "两棵左偏树的根。要求它们各自已经是合法的大根堆 + 左偏结构。"),
     ("if (!x || !y) return x + y;", "有一边为空就返回另一边。只有一个非零时 x + y 正好等于那个非零值。"),
     ("if (val[x] < val[y]) swap(x, y);", "让 x 当根。大根堆用 &lt;，小根堆把符号改成 &gt;。"),
     ("rs[x] = merge(rs[x], y);", "只往右子树递归——这是 O(log n) 的来源，也是它区别于普通堆的关键。"),
     ("if (dist[ls[x]] &lt; dist[rs[x]]) swap(ls[x], rs[x]);", "维持左偏：左子树的 dist 不能小于右子树。"),
     ("dist[x] = dist[rs[x]] + 1;", "dist 定义成“到最近空节点的边数”，空节点 dist = 0，所以叶子 dist = 1。"),
     ("dist[0] = 0，其余点 dist 初值必须是 1", "下标 0 是空节点，dist 恒为 0（全局数组默认值正好对）；但每个真实节点单独成堆时 "
                                             "<b>必须手动置 1</b>。忘了这一步，叶子会被算成 dist = 0，"
                                             "左偏性质失效，复杂度退化成 O(n)。")],
    example=r'''#include <bits/stdc++.h>
using namespace std;

const int MAXN = 100005;
int ls[MAXN], rs[MAXN], dist[MAXN], val[MAXN];

// 合并两棵左偏树（大根堆），返回新根
int merge(int x, int y) {
    if (!x || !y) return x + y;
    if (val[x] < val[y]) swap(x, y);                     // x 当根
    rs[x] = merge(rs[x], y);                             // 只递归右子树
    if (dist[ls[x]] < dist[rs[x]]) swap(ls[x], rs[x]);   // 维持左偏
    dist[x] = dist[rs[x]] + 1;
    return x;
}

// 删除堆顶：合并根的左右子树即可，O(log n)
int pop(int x) { return merge(ls[x], rs[x]); }

int main() {
    int n; cin >> n;
    for (int i = 1; i <= n; ++i) { cin >> val[i]; dist[i] = 1; }  // ★ 每个点单独成堆：dist = 1
    int root = 0;
    for (int i = 1; i <= n; ++i) root = merge(root, i);           // 全部并成一个大根堆
    while (root) { cout << val[root] << " "; root = pop(root); }  // 降序输出
    return 0;
}''',
    notes=["左偏树没有「按下标访问」「随机删除」这些能力，它存在的唯一理由是 merge 便宜。不要拿它当通用容器用。",
           "dist 只在 merge 里维护。如果手动改结构（比如直接修改 ls/rs），dist 会失效，复杂度立刻退化。",
           "想做模板去洛谷 P3377【模板】左偏树（可并堆），那里还要求判断两个元素是否已在同一堆里，需要并查集配合。"],
    brief="可并堆：O(log n) 合并两个堆，只沿右路径递归"))

SEC.append(P("三者的取舍：<b>只合一次</b>——直接 pop/push 搬，代码最短；"
             "<b>反复合并但不要求最优</b>——启发式合并，用 STL 就够；"
             "<b>合并次数多、常数敏感</b>——左偏树。选哪个看合并次数和常数，不看理论复杂度好不好看。"))

# ---------------------------------------------------------------- 坑
SEC.append(WARN("这一节的 8 种典型错法（含症状）", [
    "<b>WA，中位数整体偏小</b>。—— 平衡漏了一个方向：只写了“big 太多就往 small 挪”，没写“big 太少就从 small 补”。"
    "插入一个很大的数后 big 会比 small 少 1 个，之后每个奇数位置输出的都是第 (i−1)/2 小，比正确答案小一位。",
    "<b>TLE</b>。—— 每读一个数就 sort 一遍。N = 10<sup>5</sup> 时是 10<sup>10</sup> 量级次比较，"
    "对顶堆只有 10<sup>5</sup> 次 O(log n)。",
    "<b>RE / 答案随机</b>。—— 在空的 priority_queue 上调用 <code>top()</code>。std::priority_queue 对空堆取 top 是未定义行为，"
    "常见表现是读到垃圾值或 0。每次 top() 前都要保证非空。",
    "<b>CE</b>。—— 想让大根堆和小根堆互换内容而写 <code>big.swap(small)</code>：两者模板参数不同、类型不同，编译期就报错。",
    "<b>WA，DSU on tree 从第二棵子树开始全错</b>。—— 清空时忘了 <code>mx = 0; sum = 0;</code>，"
    "下一棵子树沿用上一棵的最大出现次数。",
    "<b>RE，DSU on tree 在链状数据上崩</b>。—— 递归深度 10<sup>5</sup> 爆栈。开大栈或改成手工栈。",
    "<b>TLE，启发式合并反而更慢</b>。—— 忘了 <code>if (a.size() &lt; b.size()) a.swap(b);</code>，"
    "每次都把大堆往小堆里塞，一个元素可能被搬 O(n) 次，总代价退化成 O(n² log n)。",
    "<b>TLE，左偏树和普通堆一样慢</b>。—— merge 里写成 <code>ls[x] = merge(ls[x], y)</code>，左偏性质被破坏，"
    "右路径可能长达 O(n)，单次合并退化成 O(n)。",
]))

SEC.append(REPRO("关掉页面，从空文件把 P1168 的代码敲一遍并提交到洛谷。",
                 "改一改 ①：把「左边比右边少就挪」的那段 <code>else if (big.size() &lt; small.size())</code> 整段删掉，"
                 "输入 <code>3\n1 5 3</code>。正确输出是 <code>1 / 3</code>，删掉后第二个数会输出 1——"
                 "亲手看到不变式被破坏的后果。",
                 "改一改 ②：把 <code>if (i &amp; 1)</code> 改成 <code>if (!(i &amp; 1))</code>，"
                 "输入 <code>4\n1 2 3 4</code>，看看偶数位置输出的是哪两个数的哪一个。"
                 "再想：要输出「下中位数」和「上中位数」，平衡条件该怎么改？",
                 "改一改 ③：造一个只有 1 个元素的小根堆和一个 10<sup>5</sup> 元素的大根堆，"
                 "先用 <code>a.swap(b)</code> 计时，再改成把 10<sup>5</sup> 个元素逐个 push 计时——"
                 "两者的差距就是“搬元素”和“换指针”的差距。",
                 "改一改 ④：在 DSU on tree 的代码里只删掉 <code>mx = 0; sum = 0;</code> 这两句（保留清空），"
                 "造一棵有多个轻儿子的树，观察 ans[] 从哪个点开始变错。"))

M = MATH("势能分析：合并的账怎么算", [
    P("<b>堆有多高。</b>n 个元素的完全二叉树高度是 ⌊log₂ n⌋ + 1。n = 10<sup>6</sup> 时 20 层，"
      "push / pop 只走一条“叶子到根”的路径，交换次数 ≤ 20。这就是 O(log n) 的具体数字——"
      "所以堆操作在 10<sup>6</sup> 规模上几乎免费，真正的代价在搬元素的次数。"),
    P("<b>中位数的位置。</b>i 个数从小到大排好，中间那个是第 ⌈i/2⌉ 个；i 为奇数时它等于 (i+1)/2。"
      "对顶堆让 big 恰好装最小的 (i+1)/2 个，于是 big 的堆顶就是第 (i+1)/2 小。"
      "这条“位置 = 大小”的对应关系，就是对顶堆全部正确性的来源。"),
    P("<b>启发式合并的势能账。</b>设元素 x 当前所在集合大小为 s。x 被搬动，只可能是因为它属于较小的那一半；"
      "搬完后新集合大小 ≥ 2s。于是 s 每被搬一次就翻倍，x 一生最多被搬 ⌊log₂ n⌋ 次。"
      "总搬动次数 ≤ n log₂ n，每次 push 是 O(log n)，合计 <b>O(n log² n)</b>。"),
    P("<b>为什么左偏树能省掉一个 log。</b>它不搬元素，只改指针：merge 沿两棵树的右路径走，"
      "每步 O(1)，总 O(log n) 次比较。合并 n 次就是 O(n log n)。这就是“可并堆”三个字的全部价值。"),
    P("<b>右路径为什么不超过 log₂(n+1)。</b>dist(x) 定义成“x 到最近空节点的边数”，空节点 dist = 0，"
      "叶子 dist = 1。左偏性质保证 dist(ls) ≥ dist(rs)，且 dist(x) = dist(rs) + 1。"
      "归纳可得：dist(x) = d 的子树至少有 2<sup>d</sup> − 1 个节点。所以 d ≤ log₂(n+1)。"
      "而右路径的边数恰好是 dist(root) − 1，于是 merge 的递归深度 ≤ log₂(n+1)。"),
    P("<b>DSU on tree 的账。</b>一个点被“暴力加入”的次数 = 它到根路径上的轻边条数。"
      "轻边的定义是“父的 sz ≥ 2 × 子的 sz”（否则它就是重儿子），所以每走一条轻边，所在子树大小至少减半，"
      "轻边不超过 log₂ n 条。每次加入 O(1)，合计 <b>O(n log n)</b>。"),
    T(["结构", "单次操作", "总代价", "什么时候用"], [
        ["priority_queue", "O(log n)", "—", "只要极值，不合并"],
        ["对顶堆", "O(log n)", "O(n log n)", "动态中位数、动态第 k 小"],
        ["启发式合并", "搬一个 O(log n)", "O(n log² n)", "合并次数多，能接受一个 log"],
        ["左偏树", "merge O(log n)", "O(n log n)", "合并次数多且常数敏感"],
        ["DSU on tree", "加一个点 O(1)", "O(n log n)", "子树统计、可离线"],
    ]),
])

THINK = [
    "对顶堆的平衡条件改成「big 的大小 = small 的大小，或比它少 1」，输出会变成什么？"
    "要同时支持「下中位数」和「上中位数」，条件该怎么写？",
    "要动态维护中位数，还要能<b>删除</b>任意一个已知元素，对顶堆还够用吗？需要补什么结构？",
    "把启发式合并里的 priority_queue 换成 set，同样的题还能做吗？代价从 O(n log² n) 变成了什么？",
    "DSU on tree 里如果不用重儿子、对所有儿子一视同仁地保留，复杂度会变成多少？举一棵树说明。",
    "左偏树怎么删除堆顶？怎么插入一个新元素？为什么它做不到 priority_queue 的「随机访问」？",
    "如果问题是「给一段区间，问它的中位数」，多组询问，对顶堆还能用吗？你会想到什么结构？",
    "为什么 priority_queue 的 swap 是 O(1)，而「把 b 的全部元素 push 进 a」是 O(m log(n+m))？差在哪一步？",
]

CHECK = [
    "能默写对顶堆的归类与平衡两段代码，并说清「奇数个时答案是大根堆堆顶」的理由。",
    "能说出 emplace 与 push 的区别，并用 emplace 往 priority_queue&lt;pair&lt;int,int&gt;&gt; 里塞元素。",
    "能写出 a.swap(b) 版的启发式合并，并解释它为什么必须是 O(1)。",
    "能独立推导启发式合并的 O(n log² n)：搬动次数 ≤ log₂ n，每次 push 又是 log。",
    "能复述 DSU on tree 的四步，并说清复杂度为什么是 O(n log n) 而不是 O(n log² n)。",
    "能写出左偏树 merge 的五行，并说清 dist 的定义与右路径 ≤ log₂(n+1) 的理由。",
    "知道 priority_queue 没有 merge，也知道大根堆和小根堆为什么不能 swap。",
]

CH2 = CH(
    "操作系统", "P2278", "提高-/提高", "https://www.luogu.com.cn/problem/P2278",
    [P("模拟一个单 CPU 的进程调度。每个进程的<b>进程号、到达时间、执行时间、运行优先级</b>都已知，"
       "优先级是自然数，数字越大优先级越高。调度规则是："),
     L(["进程到达时若 CPU 空闲，它就一直占用 CPU 直到运行结束；",
        "运行途中如果有<b>优先级更高</b>的进程到达，新进程抢占 CPU，被抢占的进程等以后继续；",
        "新进程到达时若 CPU 正在处理一个优先级<b>不低于</b>它的进程，则新进程排队等待；",
        "一旦 CPU 空闲，若有进程在等待，选优先级最高的运行；优先级相同则选到达时间最早的。"]),
     P("输入格式：若干行（读到文件结束），每行四个自然数：进程号、到达时间、执行时间、优先级，均不超过 10⁸。"
       "进程号互不相同，输入已按到达时间从小到大排序，且不会有两个相同优先级的进程同时到达；"
       "任意时刻等待队列中的进程不超过 15000 个。"),
     P("输出格式：按进程<b>结束时间</b>的先后，每行输出两个整数：进程号与结束时刻。"),
     P("<b>样例输入</b><br><code>1 1 10 1<br>2 2 3 5<br>3 3 1 4</code><br>"
       "<b>样例输出</b><br><code>2 5<br>3 6<br>1 15</code><br>"
       "样例解释：1 号在 t=1 开始跑；t=2 时 2 号（优先级 5）抢占；2 号跑到 t=5 结束；"
       "t=3 时 3 号（优先级 4）已在等待，t=5 时 CPU 空出来就让优先级更高的 3 号先跑，t=6 结束；"
       "最后 1 号只剩 9 个单位，跑到 t=15。")],
    hint=["时间值最大到 10⁸，进程一多，逐秒模拟就是 10¹² 次循环——必 TLE。"
          "把时间当成「事件」跳着走：只在<b>进程到达</b>和<b>进程结束</b>这两个时刻改变状态。",
          "任何时刻 CPU 上最多一个进程在跑，其余全在等待。等待集合要能 O(log n) 取出"
          "「优先级最高、同优先级里到达最早」的那个——想想哪个容器天生干这个。",
          "读入一个进程时，先把 CPU 从「现在」推进到它的到达时刻：途中可能跑完若干个排队的进程，"
          "每跑完一个就立刻输出它的结束时刻。"],
    idea=["<b>① 事件驱动。</b>用 now 表示当前时刻，cur 表示正在跑的进程（只记「还要跑多久」），"
          "等待集合用 priority_queue。时间只在事件处跳，不做逐秒循环。",
          "<b>② 读入一个进程 (id, arr, len, pri) 时先推进时间。</b>"
          "若 now + cur.len ≤ arr，说明 cur 会在 arr 之前（含等于）跑完：now 加上 cur.len、输出 cur，"
          "再从等待集合取下一位接着跑；重复直到「cur 跑不完」或「没人可跑」。",
          "<b>③ 被打断怎么办。</b>循环停下时若还有进程在跑，说明它只跑了 arr − now 这么久："
          "把它的剩余时间减掉、now 置成 arr。若本来就空闲，now 也置成 arr。",
          "<b>④ 新进程放哪。</b>CPU 空闲 → 它就地上机；正在跑 → 只有 pri 严格更大才抢占"
          "（题目说优先级相同则新来的等待），被打断的入队，新的上机；否则直接入队。",
          "<b>⑤ 堆的关键字。</b>第一关键字优先级<b>大</b>优先，第二关键字到达时间<b>小</b>优先。"
          "（题面保证同优先级不会同时到达，所以这样排序没有歧义。）",
          "<b>⑥ 读完之后。</b>把当前进程和等待队列里剩下的进程依次跑完，同样每完成一个就输出。",
          "<b>⑦ 数值。</b>进程数与执行时间都可能很大，结束时刻能到 10¹² 以上，now 必须 long long。"],
    code=r'''#include <bits/stdc++.h>
using namespace std;

struct Proc {
    long long id, arr, len, pri;   // len 在这里表示“还要跑多久”
};

struct Cmp {                        // 堆顶：优先级最高；同优先级取到达最早的
    bool operator()(const Proc &x, const Proc &y) const {
        if (x.pri != y.pri) return x.pri < y.pri;
        return x.arr > y.arr;
    }
};

int main() {
    priority_queue<Proc, vector<Proc>, Cmp> pq;   // 就绪队列
    long long now = 0;
    bool busy = false;
    Proc cur{};

    long long id, arr, len, pri;
    while (scanf("%lld%lld%lld%lld", &id, &arr, &len, &pri) == 4) {
        // 让 CPU 从 now 跑到 arr，途中结束的进程依次出结果
        while (busy && now + cur.len <= arr) {
            now += cur.len;
            printf("%lld %lld\n", cur.id, now);
            busy = false;
            if (!pq.empty()) { cur = pq.top(); pq.pop(); busy = true; }
        }
        if (busy) { cur.len -= (arr - now); now = arr; }   // 被打断，只跑了 arr-now 这么久
        else now = arr;                                    // 空闲到 arr

        Proc np{id, arr, len, pri};
        if (!busy) { cur = np; busy = true; }              // 空闲：直接开始
        else if (np.pri > cur.pri) { pq.push(cur); cur = np; }   // 严格更高才抢 CPU
        else pq.push(np);                                  // 否则排队
    }

    while (busy) {                       // 输入读完，把剩下的跑完
        now += cur.len;
        printf("%lld %lld\n", cur.id, now);
        busy = false;
        if (!pq.empty()) { cur = pq.top(); pq.pop(); busy = true; }
    }
    return 0;
}''',
    explain=[
        ("while (busy && now + cur.len <= arr)",
         "cur 会在 arr 之前（含恰好等于）跑完：先把它跑完、出结果，再从就绪队列取下一位。"
         "这一行等价于「时间跳跃」，把 O(时间) 的模拟压成 O(事件数)。"),
        ("cur.len -= (arr - now); now = arr;",
         "被打断：只跑了 arr − now 这么久。改的是「剩余时间」而不是原长——写成原长会让它多跑一遍。"),
        ("if (np.pri > cur.pri) { pq.push(cur); cur = np; }",
         "严格大于才抢占。题目说「优先级相同则新来的必须等待」，所以这里不能写 &gt;=。"),
        ("return x.arr > y.arr;",
         "同优先级时让到达早的排堆顶。比较器的方向与 sort 的 cmp 相反，这是 priority_queue 的老规矩。"),
        ("while (scanf(...) == 4)",
         "进程条数没给，读到文件结束为止。返回值等于 4 才说明这一行四个数都读到了。"),
        ("printf(\"%lld %lld\\n\", cur.id, now);",
         "按进程<b>结束</b>时间输出，所以每完成一个就立刻输出一次，不能攒到最后按进程号排。"),
    ],
    pitfalls=["逐秒模拟：时间值到 10⁸，进程一多就是 10¹² 次循环 → TLE。",
              "比较规则写反：抢占条件用 <code>&gt;=</code> 会让同优先级的新进程抢占 CPU；"
              "比较器第二关键字写成 <code>x.arr &lt; y.arr</code> 会让到达早的反而排在后面。",
              "用 int 存 now 和 len：结束时刻能到 10¹² 以上，溢出后输出负数。",
              "把被打断进程的剩余时间记成原长：它会多跑一遍，后面所有结束时刻全错。"],
    sample="输入：\n1 1 10 1\n2 2 3 5\n3 3 1 4\n输出：\n2 5\n3 6\n1 15",
)

CH = CH(
    "黑匣子", "P1801", "普及/提高-", "https://www.luogu.com.cn/problem/P1801",
    [P("Black Box 是一种原始的数据库。它能存一个整数数组，还有一个特殊的变量 i（初始为 0）。它支持两种操作："),
     P("<b>ADD(x)</b>：把 x 放进数组；<b>GET</b>：先把 i 加 1，然后输出数组中第 i 小的数。"),
     P("给定一个操作序列：先做 M 次 ADD，每次 ADD 之后可能紧跟若干次 GET。"
       "现在按顺序给出这 M 个被 ADD 的数，以及每次 GET 发生在第几次 ADD 之后，要求按顺序输出每次 GET 的结果。"),
     P("输入：第一行两个整数 M、N（1 ≤ N ≤ M ≤ 2×10<sup>5</sup>），分别是 ADD 的次数与 GET 的次数。"
       "第二行 M 个整数，依次是每次 ADD 的数（|x| ≤ 2×10<sup>9</sup>）。"
       "第三行 N 个整数 u<sub>1</sub> ≤ u<sub>2</sub> ≤ … ≤ u<sub>N</sub>（1 ≤ u<sub>j</sub> ≤ M），"
       "表示第 j 次 GET 紧跟在第 u<sub>j</sub> 次 ADD 之后。数据保证每次 GET 时数组里至少有 i 个数。"),
     P("输出：共 N 行，每行一个整数，依次是每次 GET 的答案。")],
    hint=["GET 要的是「第 i 小」，而 i 每次只加 1。这和例题里「前 i 个数的中位数」几乎是同一个问题。",
          "对顶堆的不变式可以推广：让大根堆里<b>恰好</b>放 i 个元素，它就是最小的 i 个，堆顶自然是第 i 小。",
          "ADD 时先随便塞进某一边并保持堆的性质；等到 GET 再按 i 调整两边的数量。x 可能为负，读入用 int，答案也用 int。"],
    idea=["把例题的不变式换掉：例题固定「big 的大小 = small 或 small + 1」，本题改成"
          "「<b>big 的大小恰好等于当前 GET 序号 i</b>」。这样 big 里就是最小的 i 个数，堆顶即第 i 小。",
          "ADD 阶段：x 比 big 堆顶小就进 big，否则进 small。此时 big 的大小可能大于或小于 i，先不管。",
          "GET 阶段：i 自增 1 之后调整——big 太小就从 small 的堆顶补，太大就把自己的堆顶送过去，"
          "直到 size(big) == i，输出 big.top()。",
          "为什么调整是 O(log n)：ADD 只做一次 push，GET 的调整次数等于 |size(big) − i|，"
          "而每次 GET 只让 i 加 1，累计的调整总量是 O(M)，摊到每次操作是 O(log n)。",
          "细节：u<sub>j</sub> 可以相等（同一次 ADD 后连续 GET），所以判断条件用 u[q] ≤ i 而不是 == i，"
          "并用 while 把这次 ADD 后面的所有 GET 都处理完。",
          "边界：只有 i 不超过已 ADD 个数时才会去 small 里取元素，所以 small 不会空——前提是 u 的含义没读错。"],
    code=r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    int m, n;
    scanf("%d%d", &m, &n);

    vector<int> a(m + 1), u(n + 1);
    for (int i = 1; i <= m; ++i) scanf("%d", &a[i]);
    for (int j = 1; j <= n; ++j) scanf("%d", &u[j]);

    priority_queue<int> big;                                  // 存最小的 i 个数
    priority_queue<int, vector<int>, greater<int>> small;      // 存剩下的
    int q = 1;                                                 // 下一次要处理的 GET 编号

    for (int i = 1; i <= m; ++i) {
        // ADD a[i]
        if (big.empty() || a[i] <= big.top()) big.push(a[i]);
        else small.push(a[i]);

        // 第 i 次 ADD 之后可能有若干次 GET（u 可能重复）
        while (q <= n && u[q] <= i) {
            while ((int)big.size() < q) { big.push(small.top()); small.pop(); }  // 补到 q 个
            while ((int)big.size() > q) { small.push(big.top()); big.pop(); }    // 多的送回右边
            printf("%d\n", big.top());     // 第 q 小
            ++q;
        }
    }
    return 0;
}''',
    explain=[
        ("if (big.empty() || a[i] <= big.top())", "归类：比当前「第 i 小」还小的进左边。"
                                                 "这里用 ≤ 是为了让相等的元素也进 big，保持 big 里存的东西“够小”。"),
        ("while ((int)big.size() < q)", "big 不够 q 个，就从右边最小的（small 堆顶）补进来。补一次 size 加 1，最多补到 q。"),
        ("while ((int)big.size() > q)", "big 超过 q 个，把左边最大的（big 堆顶）送到右边。"
                                        "这两个 while 合起来保证 size(big) 最终恰好等于 q。"),
        ("u[q] <= i", "u 可能重复（同一次 ADD 后连续 GET），所以用 while + ≤ 一次处理干净。"
                      "写成 == i 且用 if 会漏掉后面的 GET。"),
        ("printf(\"%d\\n\", big.top())", "size(big) = q 时，big 就是最小的 q 个数，堆顶是第 q 小。"),
        ("vector<int> a(m + 1), u(n + 1)", "1 基下标，和 u<sub>j</sub> 的定义直接对应，省掉减一的换算。"),
    ],
    pitfalls=["GET 的调整只写了「补」没写「送」：x 特别小时一堆元素挤进 big，size(big) 会超过 q，"
              "big.top() 变成比第 q 小更小的数。",
              "把 <code>u[q] &lt;= i</code> 写成 <code>u[q] == i</code> 并用 if 判断：u 有重复值时漏掉 GET，输出行数不够。",
              "在 small 为空时调用 <code>small.top()</code>：只有 i 超过已 ADD 个数时才可能发生，"
              "也就是把 u 的定义读错（比如当成「第几次 GET 之后」）。",
              "x 用 int 读、答案用 int 输出是对的（|x| ≤ 2×10<sup>9</sup>），但若题目把范围放宽到 10<sup>18</sup> 就必须换 long long。",
              "读入格式：u 在第三行，别和 a 混着读。"],
    sample="输入：\n7 4\n3 1 -4 2 8 -1000 2\n1 2 6 6\n输出：\n3\n3\n1\n2",
)

LESSONS = [LESSON(
    49, "堆与对顶堆、启发式合并",
    "堆的第二层用法：两块堆拼成对顶堆，把「动态第 k 小」压到 O(log n)；多块堆拼起来时，"
    "用启发式合并（小并大）把总代价从 O(n²) 压到 O(n log² n)；再把同一笔账搬到树上（DSU on tree，O(n log n)），"
    "最后用左偏树把合并本身做到 O(log n)。",
    65, ["对顶堆", "中位数", "DSU on tree"], "提高",
    SEC, math=M, think=THINK, check=CHECK, challenge=CH, challenge2=CH2,
    refs=["《算法竞赛进阶指南》0x14：堆与可并堆、0x16：树上启发式合并",
          "《算法竞赛入门笔记》：优先队列与对顶堆",
          "《算法竞赛试炼场：洛谷300题精析》P1168、P1801 两题的精析",
          "《算法竞赛黄金法则：提高算法和思考力的77项技巧》：把合并的代价摊到“集合大小翻倍”上"],
)]
