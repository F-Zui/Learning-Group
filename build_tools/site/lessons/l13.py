# -*- coding: utf-8 -*-
"""第 13 节 · 排序进阶：去重、离散化与第 k 大"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dsl import *  # noqa

SEC = []

SEC.append(P("第 12 节用 <code>sort</code> 把数据排成了一条线。真实题目很少停在“排好”这一步："
             "它们紧接着问三件事——<b>有哪些不同的值</b>、<b>这些值能不能当数组下标</b>、<b>第 k 个是谁</b>。"
             "这一节用 5 个函数把这三问一次解决，每问都只要两三行。"))

SEC.append(EX("明明的随机数", "P1059", "普及-", "https://www.luogu.com.cn/problem/P1059",
              ["输入 N 个 1 到 1000 之间的整数（N ≤ 100），重复的数字只保留一个，"
               "把剩下的数从小到大排序，再输出不同数的个数 M 和这 M 个数。"],
              sample="输入：\n10\n20 40 32 67 40 20 89 300 400 15\n输出：\n8\n15 20 32 40 67 89 300 400"))

SEC.append(P("同一道题有三条路。注意第三行代码量最少，而且它的代价<b>只跟 N 有关，和值域无关</b>——"
             "这是后面所有“大值域”题目的分水岭。"))

SEC.append(T(["做法", "核心代码", "复杂度", "什么时候不够用"], [
    ["桶计数（第 6 节）", "cnt[x] = 1，再扫 1~1000", "O(N + 值域)", "值域 10⁹ 时开不出数组"],
    ["手写去重", "排序后相邻比较，自己往前搬", "O(N log N)", "多写十几行，越界、漏搬都可能"],
    ["sort + unique + erase", "三行", "O(N log N)", "几乎没有"],
]))

# ---------------------------------------------------------------- 新函数
SEC.append(P("这 5 个函数的参数几乎都是“左闭右开区间”。<b>last 指向最后一个元素的下一个位置，永远不能取 *last。</b>"
             "先把这句话刻进脑子，后面的解释才读得顺。"))

SEC.append(FN(
    "unique（相邻去重）",
    "iterator unique(iterator first, iterator last);",
    [("first, last", "区间 [first, last)，左闭右开。last 是尾后位置。"),
     ("作用", "把<b>相邻</b>的重复元素合并：每组相等元素只保留第一个，其余依次往前挤。"),
     ("返回值", "指向“去重后区间”的下一个位置，也就是新的逻辑尾。原区间长度不变。"),
     ("前提", "只合并相邻元素。所以必须先 sort；未排序时 {1, 2, 1} 一个都去不掉。"),
     ("比较规则", "两参数版本用 == 判断相邻元素是否相同，与升序降序无关。三参数版本 "
                  "<code>unique(first, last, pred)</code> 把 pred(前一个, 后一个) 为真的相邻对当成重复——"
                  "传 greater&lt;int&gt;() 会把严格递减的序列压成一个元素。")],
    example=r'''int a[] = {1, 1, 2, 2, 2, 3, 3};
int* p = unique(a, a + 7);          // 前 3 个位置被写成 1 2 3
cout << (p - a) << "\n";            // 3：不重复元素的个数
// p 之后是残留值（标准不保证内容），长度（size）并没有变''',
    notes=["unique 不删元素、不改 size，只是把不重复的搬到前面，尾部留着旧值。",
           "真正删掉要接 erase：<code>v.erase(unique(v.begin(), v.end()), v.end())</code>。",
           "裸数组只能“逻辑删除”：记下 <code>m = unique(a, a + n) - a</code>，循环到 m 为止。"],
    brief="把相邻重复压到一起，返回新的逻辑尾"))

SEC.append(FN(
    "lower_bound（第一个 ≥ x 的位置）",
    "iterator lower_bound(iterator first, iterator last, const T& x);",
    [("first, last", "有序区间。必须按<b>与排序相同</b>的比较规则有序。"),
     ("x", "要找的值，类型和元素一致（int 就传 int）。"),
     ("返回值", "第一个 ≥ x 的元素位置；所有元素都 &lt; x 时返回 last。"),
     ("下标写法", "<code>lower_bound(a, a + n, x) - a</code> 得到 0-based 下标；不存在时正好等于 n。"),
     ("复杂度", "二分，O(log n) 次比较。n = 10⁵ 时最多 17 次。"),
     ("典型用途", "查排名、判存在性、离散化编号。")],
    example=r'''int a[] = {1, 3, 5, 7, 9};                       // 必须有序
cout << lower_bound(a, a + 5, 5) - a << "\n";    // 2：第一个 ≥ 5 的位置
cout << lower_bound(a, a + 5, 6) - a << "\n";    // 3：第一个 ≥ 6 的位置（a[3] = 7）
cout << lower_bound(a, a + 5, 100) - a << "\n";  // 5：没有 ≥ 100 的，返回尾后''',
    notes=["区间无序时不会报错，只会安静地给出错误答案。",
           "vector 要传 <code>v.begin(), v.end()</code>，写 <code>lower_bound(v, ...)</code> 编译不过。",
           "想找“最后一个 ≤ x 的位置”，写 <code>upper_bound(...) - 1</code>。"],
    brief="有序区间二分，返回第一个不小于 x 的位置"))

SEC.append(FN(
    "upper_bound（第一个 > x 的位置）",
    "iterator upper_bound(iterator first, iterator last, const T& x);",
    [("first, last", "同上，必须有序。"),
     ("返回值", "第一个 &gt; x 的元素位置；没有则返回 last。"),
     ("与 lower_bound 的差", "所有等于 x 的元素都落在 [lower, upper) 里，所以个数 = upper − lower。"),
     ("x 比所有元素都大", "返回 last。减掉首地址得到 n，含义是“x 会排在最后”。"),
     ("常见坑", "相等时 lower 在左、upper 在右：对 {3, 3, 3} 问 3，lower 给第一个 3，upper 给 3 后面那个位置。")],
    example=r'''int a[] = {1, 3, 3, 3, 5};
cout << upper_bound(a, a + 5, 3) - a << "\n";                        // 4：第一个 > 3
cout << upper_bound(a, a + 5, 3) - lower_bound(a, a + 5, 3) << "\n"; // 3：3 出现了 3 次
cout << *lower_bound(a, a + 5, 2) << "\n";                           // 3：第一个 ≥ 2 的值''',
    notes=["统计某个值出现几次，用 upper − lower，不要手写循环。",
           "判存在：<code>it != last &amp;&amp; *it == x</code>，两步都要判。"],
    brief="有序区间二分，返回第一个大于 x 的位置"))

SEC.append(FN(
    "nth_element（只让第 k 个就位）",
    "void nth_element(iterator first, iterator nth, iterator last);",
    [("first, last", "整个区间，左闭右开。"),
     ("nth", "希望“就位”的位置指针，<b>不是个数、也不是下标值</b>。第 k 小（0-based）写 first + k。"),
     ("执行后", "*nth 就是第 (nth − first + 1) 小的元素；它左边都 ≤ 它，右边都 ≥ 它。"),
     ("不保证", "左右两侧内部无序。要整体有序还得 sort。"),
     ("复杂度", "平均 O(n) 次比较，最坏 O(n²)（竞赛数据里极少触发）。")],
    example=r'''int a[] = {9, 1, 8, 2, 7, 3};
nth_element(a, a + 2, a + 6);      // 把“第 3 小”放到下标 2 上
cout << a[2] << "\n";              // 3
// 此时 a[0]、a[1] 都 ≤ 3，a[3..5] 都 ≥ 3，但它们内部顺序不定''',
    notes=["last 是尾后位置：6 个元素写 a + 6，写成 a + 5 会漏掉最后一个元素。",
           "求第 k 大（k 从 1 开始）：nth 写 <code>a + (n - k)</code>。",
           "nth_element 会打乱数组，需要原始顺序就先拷一份。"],
    brief="平均 O(n) 让第 k 小就位，其余不管"))

SEC.append(FN(
    "partial_sort（只排前 k 个）",
    "void partial_sort(iterator first, iterator middle, iterator last);",
    [("first, middle", "要真正排好的前半段 [first, middle)，长度 k = middle − first。"),
     ("last", "候选终点。[first, last) 里的元素都可能进前 k，后面的不管。"),
     ("执行后", "[first, middle) 就是全局最小的 k 个，且已升序；[middle, last) 顺序不定。"),
     ("复杂度", "O(n log k)，比全排序的 O(n log n) 省；k 接近 n 时没有优势。"),
     ("求前 k 大", "第 4 个参数传 greater&lt;int&gt;()。")],
    example=r'''int a[] = {9, 1, 8, 2, 7, 3};
partial_sort(a, a + 3, a + 6);                 // 只要前 3 小
for (int i = 0; i < 3; ++i) cout << a[i] << " ";   // 1 2 3''',
    notes=["k = n 时等价于 sort，但常数更大，没必要。",
           "只要答案不需要有序，nth_element 更快（O(n) vs O(n log k)）。"],
    brief="O(n log k) 把最小的 k 个排到前面"))

SEC.append(Q("三连的顺序不能换：sort 让重复相邻，unique 才能合并；unique 只挪不删，erase 才真正缩短长度。"
             "少任何一步，答案要么错，要么长度对不上。"))

# ---------------------------------------------------------------- 例题
SEC.append(IDEA("例题怎么想：把“去重 + 排序”翻译成三行", [
    P("题目要两样东西：不同数的个数 M、这 M 个数升序。第 12 节已经会排序了，剩下的问题只是“排序之后怎么去掉重复”。"),
    P("为什么不能直接开桶：本题值域只有 1000，<code>cnt[1001]</code> 确实能过。但题目里“随机数”三个字是干扰项——"
      "真正决定方法的是<b>值域</b>。值域一旦变成 10⁹，桶就死了，而 sort 路线照样跑，因为它只花 O(N log N)。"
      "这就是先估数据范围、再选方法。"),
    P("排序之后，相等的数一定挨在一起。于是“去重”退化成“把相邻的相同元素压成一个”，这正是 unique 干的事；"
      "再把尾部残留截掉，就得到答案。"),
    C(r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;
    vector<int> a(n);
    for (int i = 0; i < n; ++i) cin >> a[i];

    sort(a.begin(), a.end());                      // ① 排序：让相等的数挨在一起
    a.erase(unique(a.begin(), a.end()), a.end());   // ② 合并 + ③ 真正截断

    cout << a.size() << "\n";                      // 此时 size 就是不同数的个数
    for (int i = 0; i < (int)a.size(); ++i) {
        if (i) cout << " ";                        // 只在非首个元素前打空格
        cout << a[i];
    }
    cout << "\n";
    return 0;
}''', "完整代码：sort → unique → erase"),
    EXPLAIN("逐行拆解", [
        ("#include <bits/stdc++.h>", "一个头文件带上整套 STL：sort、unique、vector、lower_bound 全在里面。"
                                    "比赛不用逐个 include，省事也不影响速度。"),
        ("vector<int> a(n);", "长度 n 的动态数组，下标 0..n−1。选它而不是裸数组，是因为 erase 只有容器才有。"),
        ("sort(a.begin(), a.end());", "升序排列，把相等的数排到一起。这是 unique 生效的前提，不是可选项。"),
        ("unique(a.begin(), a.end())", "返回值指向“新逻辑尾”：它把不重复的元素依次写到前面，返回写到的下一个位置。"
                                       "注意容器长度没有变。"),
        ("a.erase(first, last)", "删掉 [first, last)。first 就是 unique 的返回值，last 是 a.end()，"
                                 "于是尾部残留被真正删掉，size 变小。两个实参来自两个不同的地方，别写反。"),
        ("cout << a.size()", "去重后 size 恰好等于不同数的个数 M，不用另外统计。"),
        ("if (i) cout << \" \"", "第一个数前面不加空格，最后一个数后面也不加。行末多一个空格在严格评测下会 WA。"),
        ("(int)a.size()", "size() 返回无符号的 size_t，和 int 的 i 比较会触发符号警告；强转一次干净利落。"),
    ]),
]))

# ---------------------------------------------------------------- 离散化
SEC.append(AFTER("离散化：10⁹ 的值域，10⁵ 个下标", [
    P("场景：n ≤ 10⁵ 个数，每个在 0..10⁹ 之间。你想“用值当下标”（桶计数、并查集、树状数组），"
      "但 10⁹ 个格子开不出来。可是你真正关心的只是<b>大小关系</b>，不是数值本身。"),
    P("做法：把所有出现过的值排序、去重，得到一张“值域字典”；再把每个数换成它在字典里的名次（1..m）。"
      "值域从 10⁹ 压到 m ≤ n，而所有比较结果不变。这就是离散化。"),
    C(r'''vector<int> xs(a.begin(), a.end());                 // ① 拷一份，原数组要留着被改写
sort(xs.begin(), xs.end());
xs.erase(unique(xs.begin(), xs.end()), xs.end());   // ② 排序 + 去重，xs 成为“值域字典”
int m = (int)xs.size();                             // 不同值的个数

for (int i = 0; i < n; ++i)
    a[i] = (int)(lower_bound(xs.begin(), xs.end(), a[i]) - xs.begin()) + 1;  // ③ 换成 1..m 的编号''',
      "标准三步"),
    EXPLAIN("三步各管什么", [
        ("vector<int> xs(a.begin(), a.end())", "拷贝原始值。a 马上要被覆盖成编号，没有副本就再也查不到原值。"),
        ("sort + unique + erase", "和例题完全一样的三连，把 xs 变成升序、无重复的字典。"),
        ("int m = (int)xs.size()", "不同值的个数，也是编号的最大值。之后开桶数组用 m + 1 个格子。"),
        ("lower_bound(...) - xs.begin() + 1", "二分查出 a[i] 在字典里的位置，加 1 变成 1..m 的编号。"),
        ("a[i] = ...", "原地改写。之后所有“谁比谁小”的判断都改用编号，结论不变。"),
    ]),
    T(["步骤", "内容"], [
        ["原数组 a（n = 5）", "5　1000000000　−7　42　1000000000"],
        ["xs 排序去重（m = 4）", "−7　5　42　1000000000"],
        ["a 被改写成编号", "2　4　1　3　4"],
    ]),
    P("三条铁律：① 必须用副本，原数组要留着被改写；② 编号从 1 开始，桶和树状数组都从 1 开始；"
      "③ 之后所有比较都改成比较编号——因为编号保序，答案一个字都不会变。"),
]))

# ---------------------------------------------------------------- 第 k 大
SEC.append(IDEA("第 k 大：不排全序也能知道答案", [
    P("只要一个数（第 k 大、中位数、前 90% 分位数），全排序就是浪费：你花了 O(n log n) 把所有数的顺序都定下来，"
      "却只用其中一条信息。"),
    P("nth_element 只做一件事：把第 k 个位置上的数放对，同时保证它左边都 ≤ 它、右边都 ≥ 它。"
      "平均 O(n)，比排序快一个 log。"),
    C(r'''// 求 n 个数里的第 k 大（k 从 1 开始）
int n = 7, k = 3;
int a[] = {5, 9, 1, 7, 3, 8, 2};

nth_element(a, a + (n - k), a + n);   // 第 k 大 = 第 (n-k+1) 小 → 0-based 下标 n-k
cout << a[n - k] << "\n";             // 7''', "求第 k 大"),
    T(["需求", "该调谁", "复杂度", "代价"], [
        ["整体有序", "sort(a, a + n)", "O(n log n)", "最贵，但信息最全"],
        ["最小的前 k 个且有序", "partial_sort(a, a + k, a + n)", "O(n log k)", "后面一段顺序不定"],
        ["第 k 小 / 中位数", "nth_element(a, a + k, a + n)", "平均 O(n)", "两侧无序"],
        ["某个值的个数 / 排名", "upper_bound − lower_bound", "O(log n)", "要求已排序"],
    ]),
    P("选型的顺序：先问“我到底要哪条信息”。只要一条，就别付全排序的钱。"),
]))

SEC.append(WARN("这一节最容易犯的 7 个错", [
    "unique 之后不 erase：<code>a.size()</code> 还是 n，输出会多出尾部残留值 → WA。"
    "vector 上必须写 <code>a.erase(unique(a.begin(), a.end()), a.end())</code>。",
    "没排序就 unique：<code>{1, 2, 1}</code> 一个都去不掉，因为 unique 只合并相邻元素 → WA。"
    "看到“去重结果里还有重复”，先检查 sort 那一行在不在。",
    "对降序数组用默认 lower_bound：<code>sort(a, a + n, greater&lt;int&gt;())</code> 之后，"
    "<code>lower_bound(a, a + n, x)</code> 不再有“第一个 ≥ x”的含义，返回的位置没有任何保证 → WA。"
    "比较器必须与排序一致，或者换成 upper_bound 配 greater。",
    "第 k 大的下标写成 a + k：k 从 1 开始时正确写法是 <code>a + (n - k)</code>。写反时 k 与 n−k 张冠李戴，"
    "小数据可能碰巧对，大数据必错 → WA。",
    "nth_element 的尾指针写成 <code>a + n - 1</code>：区间少一个元素，最大值永远进不了统计，"
    "样例能过、大数据偶发错 → WA。",
    "对每个查询都重新 sort 一遍：n = 10⁵、查询 10⁵ 次，每次 O(n log n) 就是 1.7×10⁶ 次比较，"
    "总共 ≈ 1.7×10¹¹ 次操作 → TLE。正确做法是排一次序、后面全部改用 lower_bound，或者先把答案预处理出来。",
    "离散化后混用 m 和 n：a 的长度是 n，字典的长度是 m。写 <code>for (int i = 0; i &lt; m; ++i)</code> 去遍历 a "
    "会漏掉后 n−m 个数 → WA；反过来拿 n 当字典长度去 lower_bound 则越界 → RE。",
]))

SEC.append(REPRO("关掉页面，把 P1059 的代码敲一遍再提交。",
                 "交之前先在 unique 前后各打印一次 <code>a.size()</code>，确认它从 10 变成 8。"
                 "这一步能让你彻底记住：<b>unique 不改长度，erase 才改</b>。",
                 "改一改：把 <code>sort(a.begin(), a.end())</code> 换成 <code>sort(a.begin(), a.end(), greater&lt;int&gt;())</code>，"
                 "其余不动。输出变成降序——unique 照样工作（它只判断是否相等），错的是题目要求升序。"
                 "这同时说明：<b>lower_bound 的比较器必须和 sort 一致，而 unique 只要求“相等”判断正确</b>。"))

# ---------------------------------------------------------------- 数学补给
M = MATH("离散化是保序单射，第 k 大是第 n−k+1 小", [
    P("把“值换成名次”的映射记作 f。设不同值升序为 v1, v2, …, vm，定义 f(vi) = i。它有两个性质："),
    L(["<b>单射</b>：不同的值名次不同。值域从 10⁹ 压到 m ≤ n ≤ 10⁵，一个格子一个下标，数组开得出来了。",
       "<b>保序</b>：x &lt; y 当且仅当 f(x) &lt; f(y)。"], ordered=True),
    P("只要题目里所有判断都只用到“谁比谁小”，把每个数换成 f(x) 之后答案完全不变：排序结果、去重结果、"
      "第 k 小是谁、逆序对个数都一样。这就是离散化合法的全部理由。"),
    P("反过来，如果题目要输出<b>具体的和、具体的差、具体的乘积</b>，就不能离散化——数值本身有意义，名次没有。"
      "先判断题目要的是“相对大小”还是“绝对数值”，再决定要不要离散化。"),
    P("第 k 大的下标：升序数组 a[0..n−1] 里，第 1 大是 a[n−1]，第 2 大是 a[n−2]，于是第 k 大是 a[n−k]。"
      "换一种说法：<b>第 k 大 = 第 (n−k+1) 小</b>。nth_element 要的是 0-based 下标，所以 nth 指针写 a + (n−k)。"),
    T(["n", "全排序比较次数 n·log₂n", "nth_element 平均比较次数"], [
        ["10⁴", "1.3×10⁵", "10⁴"],
        ["10⁵", "1.7×10⁶", "10⁵"],
        ["10⁶", "2.0×10⁷", "10⁶"],
        ["10⁷", "2.3×10⁸", "10⁷"],
    ]),
    P("评测机 1 秒大约做 10⁸ 次比较。最后一行的全排序已经踩在超时线上，nth_element 却只用不到 1/20 的比较次数。"
      "复杂度里的 log 不是装饰：它决定了你下一秒是 AC 还是 TLE。"),
])

THINK = [
    "题目改成“输出每个不同值以及它出现的次数”，sort + unique 还够用吗？不够的话，缺的那一步该用哪个函数补？",
    "n = 10⁶，只要中位数。sort 和 nth_element 各约需多少次比较？什么情况下你仍然会选 sort？",
    "值域 0..10⁹，但要问“第 k 小的数出现了几次”。离散化之后数组开多大？为什么不是 n + 1？",
    "把 {10, 9, 8, 7, 6} 用默认 lower_bound 查 8，返回的是哪个下标？亲手跑一遍，再说出两种修法。",
    "离散化能不能用来做“区间内不同数的个数”？先说清楚离散化会丢掉什么信息，再判断。",
]

CHECK = [
    "能默写 sort + unique + erase 三连，并说清 erase 的两个实参分别来自哪里。",
    "能说出 unique 之后不 erase 会发生什么（长度不变、尾部残留），以及它为什么会造成 WA。",
    "在 a = {1, 3, 3, 3, 5} 上能直接报出 lower_bound(a, a+5, 3) - a 与 upper_bound(a, a+5, 3) - a 的值。",
    "能用 nth_element 求第 k 大，并解释 nth 为什么是 a + (n − k) 而不是 a + k。",
    "能独立完成一次离散化，并说出“必须用副本”“编号从 1 开始”两条理由。",
    "能说出 partial_sort 与 sort 的复杂度差别，以及 k 多大时用 partial_sort 就不划算了。",
]

CH = CH(
    "第 k 小整数", "P1138", "普及-", "https://www.luogu.com.cn/problem/P1138",
    [P("给出 n 个正整数（n ≤ 10000），相同的数只算一个，求其中第 k 小的整数（k ≤ 4000）。所有正整数都小于 30000。"),
     P("输入格式：第一行两个整数 n 和 k；第二行起是 n 个正整数，用空格隔开。"),
     P("输出格式：一行一个整数，即第 k 小的数；如果不同的数不足 k 个，输出 <code>NO RESULT</code>。")],
    hint=["“相同的数只算一个”就是要先去重。去重的结果还必须有序，才谈得上第几小。",
          "排好序、去完重以后，第 k 小就是下标 k−1 的元素。注意 k 从 1 开始，数组下标从 0 开始。",
          "先数一数还剩几个数。剩下 m 个而 m &lt; k 时，题目要的不是 0、不是空行，而是一个固定的单词。"],
    idea=["读入 n、k 和 n 个数。",
          "sort 升序 → unique 合并 → erase 截断，得到 m 个互不相同的数（本节练的三连）。",
          "若 m &lt; k，输出 NO RESULT；否则输出 a[k − 1]。",
          "复杂度 O(n log n)：n = 10⁴ 时约 1.3×10⁵ 次比较，离 1 秒的预算差着三个数量级。",
          "为什么正确：去重后数组严格递增，第 i 个元素就是第 i 小的不同值，所以第 k 小落在下标 k−1。"],
    code=r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    int n, k;
    cin >> n >> k;
    vector<int> a(n);
    for (int i = 0; i < n; ++i) cin >> a[i];

    sort(a.begin(), a.end());                      // ① 先让相等的数挨在一起
    a.erase(unique(a.begin(), a.end()), a.end());   // ② 合并 + 真正截断

    int m = (int)a.size();                         // 不同数的个数
    if (m < k) {                                   // ③ 不够 k 个，题目要求固定单词
        cout << "NO RESULT\n";
        return 0;
    }
    cout << a[k - 1] << "\n";                      // ④ 第 k 小 = 下标 k-1
    return 0;
}''',
    explain=[
        ("sort(a.begin(), a.end())", "把重复的挤到一起。unique 只认相邻相等，这一步不能省。"),
        ("unique + erase", "unique 返回新逻辑尾，erase 从那里删到末尾。执行完 a 里恰好是全部不同的数，且升序。"),
        ("int m = (int)a.size()", "去重后的个数。别再用 n —— n 是原始个数，含重复。"),
        ("m < k", "不同数只有 m 个，第 k 小不存在。这时必须输出 NO RESULT，输出 0 或什么都不输出都是 WA。"),
        ("a[k - 1]", "k 从 1 开始数，下标从 0 开始，所以第 k 小在下标 k−1。"),
        ("\"NO RESULT\\n\"", "判题逐字比对，大小写、空格、下划线都必须和题面完全一致。"),
    ],
    pitfalls=["写成 a[k]：那是第 k+1 小，并且 k = m 时直接越界 → WA 或 RE。",
              "忘记判 m &lt; k 就访问 a[k−1]：越界读到一个随机值，表现为偶发 WA、或 RE。",
              "只 unique 不 erase：m 用 a.size() 得到的是 n，m &lt; k 的判断失效，还会把尾部残留的重复值当成“第 k 小”输出 → WA。",
              "输出单词拼错（No Result、NO_RESULT、No!!!）→ WA；这题最容易丢的分不在算法上。"],
)

LESSONS = [LESSON(
    13, "排序进阶：去重、离散化与第 k 大",
    "排序只是开始。这一节把排序之后最常用的三个动作练成肌肉记忆：sort + unique + erase 三连去重、"
    "离散化把 10⁹ 的值域压成 10⁵ 个下标、nth_element 与 partial_sort 只拿你需要的那部分信息。",
    60, ["unique", "离散化", "nth_element"], "普及-",
    SEC, math=M, think=THINK, check=CHECK, challenge=CH,
    refs=["《算法竞赛入门笔记》第 5 章：排序与离散化",
          "《算法竞赛进阶指南》0x05 排序",
          "洛谷 P1059、P1138 题解区的高赞写法"],
)]
