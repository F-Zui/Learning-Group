# -*- coding: utf-8 -*-
"""第 15 节 · 回顾三：函数、结构体与排序"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dsl import *  # noqa

SEC = []

SEC.append(P("第 11~14 节给的是四件工具：<b>函数</b>打包逻辑，<b>结构体</b>打包数据，"
             "<b>sort + cmp</b> 按你定的规则排队，<b>枚举</b>把搜索空间数清楚再暴力。"
             "比赛里它们几乎同时出现：先给数据建模（结构体），再定比较规则（cmp），"
             "交给 sort，最后按规则取出答案。这一节不讲新算法，只把这四件工具磨到不会写错。"))

SEC.append(Q("排序题 90% 的分数不在 <code>sort</code> 那一行，而在 <code>cmp</code> 的三行判断里。"))

SEC.append(T(["节", "内容", "一句话判据"], [
    ["11", "函数：参数传递与返回值", "想改调用者的变量，参数写成 <code>类型 &amp;</code>；只读不写，写 <code>const 类型 &amp;</code>"],
    ["12", "结构体与多关键字排序", "排序规则一句话说不完，就写 <code>cmp</code>"],
    ["13", "去重、离散化与第 k 大", "全部有序用 <code>sort</code>；只要一个位置用 <code>nth_element</code>；值域 10⁹ 而下标只有 10⁵，先离散化"],
    ["14", "枚举与暴力", "先估搜索空间有多大，再决定写几重循环"],
]))

# ---------------------------------------------------------------- 完整例题
SEC.append(EX("奖学金", "P1093", "普及-", "https://www.luogu.com.cn/problem/P1093",
              ["n 名学生，每人有语文、数学、英语三科成绩（0~100），总分 = 三科之和。",
               "排序规则：总分高的在前；总分相同，语文高的在前；总分和语文都相同，<b>学号小的在前</b>。",
               "输出：按上述规则排好的前 5 名，每行「学号 总分」。",
               "输入格式：第一行 n（n ≤ 300）；接下来 n 行，第 i 行是学号为 i 的学生的语文、数学、英语成绩。",
               "输出格式：共 5 行，每行两个整数，学号与总分。"],
              sample="输入：\n6\n90 67 80\n87 66 91\n78 89 91\n88 99 77\n67 89 64\n78 89 98\n\n"
                     "输出：\n6 265\n4 264\n3 258\n2 244\n1 237"))

SEC.append(P("这题只输出学号和总分，排序却要用到语文。所以结构体必须同时存 <code>id、ch、ma、en、sum</code>："
             "<b>排序要用什么，结构体就存什么</b>。下面先把四件工具的写法逐个拆开，再拼成完整代码。"))

# ---------------------------------------------------------------- 新函数拆解
SEC.append(FN(
    "sort（三参数版）",
    "sort(v.begin(), v.end(), cmp);",
    [("v.begin(), v.end()", "左闭右开区间 <code>[first, last)</code>，排的是 first 到 last-1。"),
     ("cmp", "比较函数：返回 <code>true</code> 表示「a 应该排在 b 前面」。"),
     ("返回值", "<code>void</code>。排的是原区间本身，不产生新数组。"),
     ("复杂度", "O(n log n) 次比较。n = 10⁶ 时约 2×10⁷ 次，1 秒内能过。"),
     ("两参数版", "<code>sort(v.begin(), v.end())</code> 按 <code>&lt;</code> 升序；<code>greater&lt;int&gt;()</code> 降序。")],
    example=r'''vector<int> v = {3, 1, 4, 1, 5};

sort(v.begin(), v.end());                  // 1 1 3 4 5   升序
sort(v.begin(), v.end(), greater<int>());  // 5 4 3 1 1   降序

int a[5] = {3, 1, 4, 1, 5};
sort(a, a + 5);        // 数组用「首指针, 尾后指针」
sort(a + 1, a + 4);    // 只排 a[1]..a[3]，a[0] 与 a[4] 不动''',
    notes=["数组写 <code>sort(a, a + n)</code>；写成 <code>sort(a, a + n - 1)</code> 就漏掉最后一个元素。",
           "下标从 1 开始时是 <code>sort(a + 1, a + n + 1)</code>，尾后指针要多加 1。"],
    brief="标准库排序，区间左闭右开，第三个参数就是你的比较规则"))

SEC.append(FN(
    "cmp 比较函数（结构体 + const 引用）",
    "bool cmp(const Stu &a, const Stu &b)",
    [("bool", "返回 a 是否该排在 b 前面：true 排前面，false 不排前面。"),
     ("const Stu &a", "引用传参不拷贝；结构体里有 string 时，按值传参每次比较都要复制一份。"),
     ("第一个 if", "第一关键字：不相等就定胜负，相等才往下走。"),
     ("最后一个 return", "兜底关键字，必须让任意两个不同元素分出胜负。"),
     ("严格弱序", "三条铁律：<code>cmp(a,a)</code> 必须为 false；<code>cmp(a,b)</code> 与 <code>cmp(b,a)</code> 不能同时为 true；大小关系可传递。")],
    example=r'''struct Stu { int id, sum, ch; };

bool cmp(const Stu &a, const Stu &b) {
    if (a.sum != b.sum) return a.sum > b.sum;  // 总分降序
    if (a.ch  != b.ch ) return a.ch  > b.ch;   // 语文降序
    return a.id < b.id;                        // 学号升序：兜底，必有胜负
}''',
    notes=["写成 <code>a.sum &gt;= b.sum</code> 破坏严格弱序：sort 可能越界读写，本地小数据正常、评测大点 RE 或乱序 WA。",
           "cmp 里只做比较，不要改元素、不要输出调试信息——sort 调用它多少次是不确定的。"],
    brief="把「谁排前面」写成三行 if，最后必须有一条一定分出胜负的兜底"))

SEC.append(FN(
    "unique（去重）",
    "v.erase(unique(v.begin(), v.end()), v.end());",
    [("前提", "区间已经有序（至少相同元素相邻），否则只去掉相邻的重复。"),
     ("作用", "把不重复元素依次搬到区间前部，返回去重后区间的尾后指针。"),
     ("长度不变", "<code>unique</code> 不删元素，容器 size 仍是原值，多余旧值留在后面。"),
     ("erase 收尾", "删掉 <code>[新尾, 原尾)</code> 这一段，size 才等于答案。"),
     ("只要个数", "<code>int k = unique(a, a + n) - a;</code> 不删元素，直接拿到去重后的长度。")],
    example=r'''vector<int> v = {1, 1, 2, 2, 2, 5};
sort(v.begin(), v.end());                      // 前提：先有序

v.erase(unique(v.begin(), v.end()), v.end());
// v = {1, 2, 5}, v.size() == 3

int a[6] = {1, 1, 2, 2, 2, 5};
int k = unique(a, a + 6) - a;                  // k == 3，前 3 个是答案''',
    notes=["只写 <code>unique</code> 不写 <code>erase</code>，再按原长度遍历就会输出重复值。",
           "没排序就 unique，只合并相邻重复：<code>1 2 1</code> 一个也去不掉。"],
    brief="必须先排序；返回的是新末尾，配 erase 才真正变短"))

SEC.append(FN(
    "nth_element（求第 k 小）",
    "nth_element(a, a + k, a + n);",
    [("a + k", "第 k 小（k 从 0 开始）该放的位置。执行完 <code>a[k]</code> 就是答案。"),
     ("两侧保证", "左边元素都不大于 <code>a[k]</code>，右边都不小于它。"),
     ("两侧无序", "不要假设 <code>a[0..k-1]</code> 有序，它只是「都比 a[k] 小」。"),
     ("复杂度", "平均 O(n)，比 sort 的 O(n log n) 快。n = 5×10⁶ 时差距是 0.2 秒和 1 秒的区别。"),
     ("第 k 大", "换下标：k 从 1 起时，第 k 大 = 第 <code>n-k</code> 小。")],
    example=r'''int a[8] = {7, 3, 9, 1, 5, 2, 8, 4};
nth_element(a, a + 2, a + 8);   // a[2] == 3，即第 2 小（0 起）
// 此时 a[0..1] 都 ≤ 3，a[3..7] 都 ≥ 3，但两侧都没排好序''',
    notes=["k ≥ n 是未定义行为，本地可能不报错，评测机给出乱答案。",
           "要的是「排序后的前 k 个」而不是「第 k 个」时，必须用 sort。"],
    brief="只要一个位置就够时用它，平均 O(n)"))

# ---------------------------------------------------------------- 思路
SEC.append(TIP("第 11 节回头看一眼：函数的三句话", [
    "<b>参数</b>：写 <code>int f(int x)</code> 是拷贝，改 x 不影响调用者；写 <code>void f(int &amp;x)</code> 才真正改到外面的变量。",
    "<b>返回</b>：<code>bool isPrime(int x)</code> 让调用处读起来就是一句话；需要返回多项时，返回一个结构体比用全局变量干净。",
    "<b>作用域</b>：函数里定义的变量出了函数就消失；算法题里的大数组一律放全局，主函数里开 10⁶ 个 int 会爆栈。",
]))

SEC.append(IDEA("例题怎么想：先定关键字，再写 cmp，最后才是 sort", [
    "关键字有三层，顺序不能换：总分降序 → 语文降序 → 学号升序。前一层分不出胜负才看后一层。",
    P("第三层「学号升序」不是为了好看：题目保证学号互不相同，这一层让任意两人一定分出先后，"
      "cmp 才是严格弱序，sort 的行为才可预测。这正是 P1093 里「必须严格按规则排序」的含义。"),
    "总分在<b>读入时</b>就算好存进结构体。放进 cmp 里现算的话，每次比较多做 3 次加法，"
    "n log n 次比较就是几百万次多余运算。",
    "排序只需要一次 <code>sort</code>，之后按下标取前 5 个就行——不要再写任何比较。",
]))

SEC.append(C(r'''#include <bits/stdc++.h>
using namespace std;

struct Stu {
    int id;            // 学号：第 i 行数据就是学号 i
    int ch, ma, en;    // 语文、数学、英语
    int sum;           // 总分，读入时一次算好
};

// 返回 true 表示 a 应该排在 b 前面
bool cmp(const Stu &a, const Stu &b) {
    if (a.sum != b.sum) return a.sum > b.sum;   // ① 总分高者在前
    if (a.ch  != b.ch ) return a.ch  > b.ch;    // ② 总分相同，语文高者在前
    return a.id < b.id;                         // ③ 再相同，学号小者在前（兜底）
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<Stu> v(n);
    for (int i = 0; i < n; ++i) {
        v[i].id = i + 1;                         // 输入顺序就是从 1 开始的学号
        cin >> v[i].ch >> v[i].ma >> v[i].en;
        v[i].sum = v[i].ch + v[i].ma + v[i].en;  // 只在读入时加一次
    }

    sort(v.begin(), v.end(), cmp);

    for (int i = 0; i < 5 && i < n; ++i)         // n 小于 5 时也不会越界
        cout << v[i].id << " " << v[i].sum << "\n";
    return 0;
}''', "完整代码 · 结构体 + 三关键字 cmp"))

SEC.append(EXPLAIN("逐行拆解", [
    ("#include <bits/stdc++.h>", "竞赛万能头，一次包含 <code>vector</code>、<code>algorithm</code>（sort、unique、nth_element）、<code>iostream</code>。"),
    ("struct Stu { ... };", "把一个人的 5 项信息打包成一个类型。sort 交换的是整个结构体，id 与 sum 跟着 ch/ma/en 一起移动，不会错位。"),
    ("bool cmp(const Stu &a, const Stu &b)", "const 引用：不拷贝、不改原对象。本题结构体只有 int，按值传也不慢，但换成带 string 的结构体就会明显变慢。"),
    ("if (a.sum != b.sum) return a.sum > b.sum;", "第一关键字降序。先判「不相等」再比大小，后两层只在真正相等时才执行。"),
    ("if (a.ch != b.ch) return a.ch > b.ch;", "第二关键字：只有总分相同时才走得到这一行，所以不需要再判总分。"),
    ("return a.id < b.id;", "兜底。学号互不相同，任意两元素在这里一定分出胜负，cmp 满足严格弱序。"),
    ("v[i].id = i + 1;", "第 i 行数据（i 从 0 起）对应学号 i+1。写错这一行，输出顺序对、号码全错，是本题最常见的 WA。"),
    ("v[i].sum = ...;", "读入即算。放在 cmp 里算也能过，但每次比较都重算三遍加法，属于白费。"),
    ("sort(v.begin(), v.end(), cmp);", "按 cmp 排整个 vector。n ≤ 300，排序耗时可以忽略，真正的成本在读入。"),
    ("i < 5 && i < n", "题目要求输出前 5 名；加 <code>i &lt; n</code> 保证 n 小于 5 时不越界。"),
]))

SEC.append(T(["排序要求", "cmp 写法", "注意"], [
    ["升序", "<code>return a &lt; b;</code>", "等价于不写 cmp"],
    ["降序", "<code>return a &gt; b;</code>", "不要写成 <code>a &gt;= b</code>"],
    ["多关键字", "<code>if (a.x != b.x) return a.x &gt; b.x;<br>return a.y &lt; b.y;</code>", "最后一层必须能分出胜负"],
    ["拼起来更大", "<code>return a.s + b.s &gt; b.s + a.s;</code>", "字符串拼接比较，不是比长度"],
    ["按比值排序", "<code>return (long long)a.p * b.w &gt; (long long)b.p * a.w;</code>", "交叉相乘代替除法，避免浮点"],
]))

SEC.append(WARN("这一章最容易踩的 7 个坑（都带症状）", [
    "cmp 里写 <code>&gt;=</code> 或 <code>&lt;=</code>：严格弱序被破坏，sort 内部可能走到区间外。"
    "症状是<b>本地小数据全对、交上去 RE 或随机 WA</b>，最难查。",
    "<b>cmp 忘了兜底 return</b>：函数走到末尾没有返回值，是未定义行为。症状是同一份代码两次运行结果不同。",
    "关键字的<b>顺序</b>写反：先比语文再比总分，样例可能刚好过，遇到总分高但语文低的就 WA。",
    "把 <code>sort(a, a + n)</code> 写成 <code>sort(a, a + n - 1)</code>：最后一个元素没参与排序。"
    "症状是<b>输出里总有一个数在原位不动</b>。",
    "<code>unique</code> 后忘记 <code>erase</code>：后续按原长度遍历，输出里出现旧值。症状是<b>答案行数比预期多</b>。",
    "用 <code>double</code> 算 <code>m * 1.5</code> 再截断：浮点存不准时可能少算 1 名。"
    "症状是<b>分数线差 1 分、人数差 1 人</b>，样例还看不出来。",
    "n = 10⁵ 还自己写冒泡或选择排序：约 5×10⁹ 次比较，必定 <b>TLE</b>；"
    "<code>sort</code> 只要 1.7×10⁶ 次，差距是 3000 倍。",
]))

SEC.append(P("第 13 节还有两件工具在这里补一句：<b>离散化</b> = 排序 + 去重 + 把每个值换成它的名次，"
             "把 10⁹ 的值域压成 10⁵ 以内的下标；<b>第 k 大</b> = 第 n−k 小，只是一次下标换算。"
             "两者都建立在「先排好序」之上，所以本章的动作顺序永远是：建模 → 排序 → 查表。"))

SEC.append(REPRO("关掉页面，把上面 P1093 的完整代码手打一遍并提交。",
                 "改一改①：把「输出前 5 名」改成「输出全部 n 名」，只动 for 循环的边界。",
                 "改一改②：把第三关键字从「学号升序」改成「英语降序 + 学号升序」，用同一组数据看结果变没变。",
                 "改一改③：把兜底那行改成 <code>return false;</code>，输入 5 个总分完全相同的学生，"
                 "观察输出顺序是否还是学号升序——这就是严格弱序被破坏的现场。"))

SEC.append(T(["题", "编号", "主要考什么", "最容易错在哪"], [
    ["A", "P1059", "sort + unique 的去重三行", "普及-"],
    ["B", "P1104", "结构体的多关键字排序", "普及-"],
    ["C", "P1068", "排序 + 分数线与并列人数", "普及-"],
    ["D", "P1923", "nth_element + 快读 + 全局数组", "普及/提高-"],
    ["E", "P1217", "枚举 + 两个判定函数", "偶数位回文数被 11 整除；i*i 溢出"],
]))

SEC.append(INFO("这次训练怎么用 90 分钟", [
    "0~10 分钟：只读题，不写代码。把 5 题按「能立刻写」→「有思路」→「没思路」排个序。",
    "10~30 分钟：P1059。最短的一道，用来找手感；写完只检查一件事：有没有 <code>erase</code>。",
    "30~60 分钟：P1104 与 P1068。两道都是结构体排序，重点在关键字的<b>顺序</b>和<b>兜底</b>。",
    "60~85 分钟：P1923 或 P1217 选一道做透。前者考 <code>nth_element</code> 与快读，后者考枚举 + 两个判定函数。",
    "85~90 分钟：不写新代码，只核对数组大小、<code>i*i</code> 溢出、0/1 起点、行末空格。",
]))

SEC.append(OK("提交前的 30 秒检查清单（排序题专用）", [
    "cmp 的三个分支都用 <code>!=</code> 判「不相等」了吗？最后一层是不是一定分出胜负？",
    "数组区间是 <code>[0, n)</code> 还是 <code>[1, n]</code>？尾后指针有没有差一位？",
    "结构体的字段数量够不够？排序要用到的信息是否都在结构体里？",
    "答案需要 long long 吗？总分、平方、乘积先按最坏情况估一遍。",
    "输出格式：行末有没有多余空格？换行够不够？",
]))

CHECK = [
    "不看资料能写出 P1093 的完整代码，并说清三行 cmp 各自在比什么。",
    "能手写 sort 的两参数版与三参数版，知道数组和 vector 的区间边界分别怎么写。",
    "能说出严格弱序的三条要求，并举一个「用 <code>&gt;=</code> 会 RE」的例子。",
    "能不查资料写出 sort + unique + erase 的去重三行，并解释为什么必须先排序。",
    "能说清 <code>nth_element</code> 之后 a[k] 两侧<b>是</b>什么性质、<b>不是</b>什么性质。",
    "P1068 里 ⌊1.5m⌋ 为什么用 <code>m * 3 / 2</code> 而不是 <code>m * 1.5</code>，能讲清浮点误差怎么变成 WA。",
    "P1217 里为什么能把 b 截断到 9999999，能自己举一个 4 位回文数验证它是 11 的倍数。",
]

# ---------------------------------------------------------------- 5 道训练题
CH1 = CH("明明的随机数", "P1059", "普及-", "https://www.luogu.com.cn/problem/P1059",
         [P("明明生成了 n 个 1 到 1000 之间的随机整数，其中重复的数只保留一个，剩下的数从小到大排好序。"),
          P("输入格式：第一行一个正整数 n（1 ≤ n ≤ 100）；第二行 n 个用空格隔开的整数，每个在 1 到 1000 之间。"),
          P("输出格式：第一行一个整数 M，表示不同的随机数个数；第二行 M 个用空格隔开的整数，为从小到大排好序的不相同的随机数。")],
         hint=["值域只有 1000，第 6 节的桶计数也能做；但这道题要求用「排序 + 去重」，把第 13 节的三行写熟。",
               "去重前必须先有序，否则只能去掉相邻的重复。",
               "unique 只搬元素、不改长度，想一想怎么把后面多余的部分真正删掉。"],
         idea=["<b>sort</b>：把相同数字挤到一起，为 unique 创造条件。",
               "<b>unique</b>：把每段连续重复的第一个留在原地，返回去重后区间的新末尾。",
               "<b>erase</b>：删掉 [新末尾, 原末尾) 这段垃圾，size() 才等于真实答案。",
               "先输出 size，再按下标输出。复杂度 O(n log n + n)，n ≤ 100 瞬间过。",
               "同理可推广：若值域是 10⁹ 而 n 只有 10⁵，排序去重后配合二分就是离散化。"],
         code=r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<int> a(n);
    for (int i = 0; i < n; ++i) cin >> a[i];

    sort(a.begin(), a.end());                      // 先让相同元素相邻
    a.erase(unique(a.begin(), a.end()), a.end());   // 再去重并真正缩短

    cout << a.size() << "\n";
    int m = (int)a.size();                          // size() 是无符号数，先转 int
    for (int i = 0; i < m; ++i)
        cout << a[i] << (i + 1 == m ? '\n' : ' ');  // 行末只换行，不加空格
    return 0;
}''',
         explain=[
             ("sort(a.begin(), a.end());", "unique 只合并相邻重复，所以必须先把相同值排到一起。"),
             ("unique(a.begin(), a.end())", "把不重复的元素依次搬到前面，返回去重后区间的新末尾；此时容器长度没变。"),
             ("a.erase(..., a.end());", "把 [新末尾, 原末尾) 这一段删掉，size() 才等于答案。"),
             ("int m = (int)a.size();", "size() 返回无符号数，直接与 int 比较会出现符号/无符号警告。"),
             ("(i + 1 == m ? '\\n' : ' ')", "最后一个数后面只换行，避免严格评测判行末空格错。"),
         ],
         pitfalls=["只写 unique 不写 erase，再按原长度遍历，输出里混进旧值 → WA。",
                   "忘了 sort 就 unique，只去掉相邻重复，输出 1 2 1 这种错答案。",
                   "第二行行末多打一个空格，个别评测机会判格式错。",
                   "把去重后的长度写成 n（原长度），第一行就错。"],
         sample="输入：\n10\n20 40 32 67 40 20 89 300 400 15\n\n输出：\n8\n15 20 32 40 67 89 300 400")

CH2 = CH("生日", "P1104", "普及-", "https://www.luogu.com.cn/problem/P1104",
         [P("给出 n 个同学的姓名与出生年、月、日，按年龄从大到小输出姓名，一行一个。"),
          P("年龄大的排在前面，也就是出生日期早的排在前面。"),
          P("如果两个同学生日完全相同，输入的靠后的同学先输出。"),
          P("输入格式：第一行一个整数 n；接下来 n 行，每行一个不含空格的姓名和三个整数，表示出生年、月、日。"),
          P("输出格式：共 n 行，每行一个姓名。")],
         hint=["比较两个生日，先比年、再比月、再比日，这个顺序就是 cmp 里 if 的顺序。",
               "「输入靠后先输出」说明结构体里除了生日，还得额外记一个输入下标。",
               "如果 cmp 只写两层，生日相同的两个人谁先谁后就不确定，答案会错。"],
         idea=["结构体存 <code>name、y、m、d、id</code>，id 是读入顺序（从 0 开始）。",
               "cmp 四层：年小在前 → 月小在前 → 日小在前 → id 大在前。",
               "前三层用「出生早 = 年龄大」；第四层用「id 大 = 输入靠后」。",
               "id 互不相同，所以第四层保证任意两人一定分出胜负，严格弱序成立。",
               "sort 后按顺序输出姓名。交换的是整个结构体，姓名跟着生日一起走，不会错配。"],
         code=r'''#include <bits/stdc++.h>
using namespace std;

struct Node {
    string name;
    int y, m, d, id;     // id：读入顺序，从 0 开始
};

bool cmp(const Node &a, const Node &b) {
    if (a.y != b.y) return a.y < b.y;   // 出生早的年龄大
    if (a.m != b.m) return a.m < b.m;
    if (a.d != b.d) return a.d < b.d;
    return a.id > b.id;                 // 生日相同：输入靠后的先输出
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<Node> v(n);
    for (int i = 0; i < n; ++i) {
        cin >> v[i].name >> v[i].y >> v[i].m >> v[i].d;
        v[i].id = i;
    }

    sort(v.begin(), v.end(), cmp);

    for (const auto &x : v) cout << x.name << "\n";
    return 0;
}''',
         explain=[
             ("struct Node { string name; ... };", "把一个人的姓名与生日打包。sort 交换的是整个结构体，姓名不会和生日错配。"),
             ("bool cmp(const Node &a, const Node &b)", "const 引用：结构体里有 string，按值传参会每次比较都复制字符串。"),
             ("if (a.y != b.y) return a.y < b.y;", "年份小 = 出生早 = 年龄大 = 排前面。"),
             ("return a.id > b.id;", "生日完全相同时，id 大的（输入靠后）排前面。"),
             ("sort(v.begin(), v.end(), cmp);", "整体排序，O(n log n)；n 不大，主要成本在读入。"),
             ("for (const auto &x : v)", "范围 for + 常引用，不拷贝结构体；只读时加 const 更安全。"),
         ],
         pitfalls=["cmp 只写到年份就 return，生日相同的两人顺序随机 → WA。",
                   "把 id 的兜底方向写反（写成 <code>a.id &lt; b.id</code>），同生日的人顺序颠倒。",
                   "把出生年份当「越大越老」，方向反了，整份输出倒序。",
                   "cmp 里用 <code>&gt;=</code>，严格弱序被破坏，可能 RE。"])

CH3 = CH("分数线划定", "P1068", "普及-", "https://www.luogu.com.cn/problem/P1068",
         [P("n 名选手报名，计划录取 m 名志愿者。面试分数线定为排名第 ⌊m × 1.5⌋ 名选手的分数"
            "（成绩高者排前，同分报名号小者排前）。"),
          P("所有成绩不低于面试分数线的选手都能进入面试。"),
          P("输入格式：第一行两个整数 n、m；接下来 n 行，每行两个整数，表示报名号与笔试成绩。"),
          P("输出格式：第一行输出面试分数线与实际进入面试的人数；接下来每行一个进入面试的选手的报名号和成绩，"
            "按成绩从高到低输出，成绩相同按报名号从小到大输出。")],
         hint=["先按「成绩降序、报名号升序」排好，讨论第几名才有意义。",
               "⌊1.5m⌋ 用整数算：<code>m * 3 / 2</code>，不要用 double。",
               "分数线之上可能有并列，实际人数要重新数一遍，不能直接输出 ⌊1.5m⌋。"],
         idea=["读入 + 排序：cmp 两个关键字，成绩降序、报名号升序。",
               "need = ⌊1.5m⌋，再用 min(n, need) 夹一下——m 接近 n 时 1.5m 会超过总人数。",
               "分数线 line = v[need-1].sc：下标从 0 开始，第 need 名就是 v[need-1]。",
               "实际人数 cnt = 从前往后数第一个「成绩 < line」的位置，这自动把并列的人全算进来。",
               "先输出 line 与 cnt，再输出前 cnt 个人的报名号与成绩。"],
         code=r'''#include <bits/stdc++.h>
using namespace std;

struct P {
    int id, sc;
};

bool cmp(const P &a, const P &b) {
    if (a.sc != b.sc) return a.sc > b.sc;   // 成绩高的在前
    return a.id < b.id;                     // 同分报名号小的在前
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;
    vector<P> v(n);
    for (int i = 0; i < n; ++i) cin >> v[i].id >> v[i].sc;

    sort(v.begin(), v.end(), cmp);

    int need = m * 3 / 2;            // ⌊1.5m⌋，整数运算没有精度问题
    if (need > n) need = n;          // 1.5m 可能超过总人数
    int line = v[need - 1].sc;       // 第 need 名的分数就是分数线

    int cnt = 0;
    while (cnt < n && v[cnt].sc >= line) ++cnt;   // 并列的全进，重新数

    cout << line << " " << cnt << "\n";
    for (int i = 0; i < cnt; ++i)
        cout << v[i].id << " " << v[i].sc << "\n";
    return 0;
}''',
         explain=[
             ("int need = m * 3 / 2;", "整数除法向下取整，正好等于 ⌊1.5m⌋；<code>(int)(1.5*m)</code> 可能因浮点误差少 1。"),
             ("if (need > n) need = n;", "m 接近 n 时 1.5m 超过总人数，不夹住就数组越界（RE）。"),
             ("int line = v[need - 1].sc;", "下标 0 起，第 need 名是 v[need-1]；写成 v[need] 分数线差一名。"),
             ("while (cnt < n && v[cnt].sc >= line)", "「不低于」用 >=；并列的人全部进入，人数不一定等于 need。"),
             ("cout << line << \" \" << cnt << \"\\n\";", "先分数线和人数，同行用空格分隔。"),
         ],
         pitfalls=["分数线取成 v[need] ，整份输出全错。",
                   "实际人数直接输出 need，忽略并列 → 人数与名单条数不一致，WA。",
                   "cmp 写成 <code>a.sc &gt;= b.sc</code>，严格弱序被破坏，可能 RE。",
                   "忘了把 need 夹到 n，n 较小时数组越界，表现为 RE 而不是 WA。"])

CH4 = CH("求第 k 小的数", "P1923", "普及/提高-", "https://www.luogu.com.cn/problem/P1923",
         [P("给出 n 个整数，求其中第 k 小的数，最小的数算第 0 小。"),
          P("输入格式：第一行两个整数 n、k（n &lt; 5×10⁶，0 ≤ k &lt; n）；接下来 n 个整数，可能跨多行。"),
          P("输出格式：一行一个整数，即第 k 小的数。")],
         hint=["只求一个位置，不需要把全部数据排好。想一想第 13 节为此准备的函数。",
               "题目的 k 从 0 开始：k = 0 就是最小值。",
               "n 到 5×10⁶，cin 读入偏慢，试试用 getchar 自己写一个读入函数。"],
         idea=["<code>nth_element(a, a+k, a+n)</code> 执行完后 a[k] 就是第 k 小（0 起），平均 O(n)。",
               "它的原理是快速选择：按基准把区间分成两半，只继续处理包含 k 的那一半，所以是 O(n) 而不是 O(n log n)。",
               "左侧元素都不大于 a[k]，右侧都不小于 a[k]，但两侧都没有排好序。",
               "5×10⁶ 个 int 约 20MB，必须放全局数组：栈空间只有几 MB，放 main 里直接栈溢出 RE。",
               "手写快读逐字符解析，比 cin 快 2~3 倍，也顺手解决「数据跨行」的问题。"],
         code=r'''#include <bits/stdc++.h>
using namespace std;

const int MAXN = 5000000;
int a[MAXN + 5];          // 全局数组：静态区，不受栈大小限制

int readInt() {           // 手写快读，返回一个 int
    int x = 0, f = 1;
    char c = getchar();
    while (c < '0' || c > '9') {      // 跳过空格、换行等
        if (c == '-') f = -1;
        c = getchar();
    }
    while (c >= '0' && c <= '9') {
        x = x * 10 + (c - '0');
        c = getchar();
    }
    return x * f;
}

int main() {
    int n = readInt(), k = readInt();
    for (int i = 0; i < n; ++i) a[i] = readInt();

    nth_element(a, a + k, a + n);     // 执行后 a[k] 就是第 k 小
    printf("%d\n", a[k]);
    return 0;
}''',
         explain=[
             ("int a[MAXN + 5];", "全局数组在静态区；5×10⁶ 个 int 约 20MB，放 main 里会栈溢出。"),
             ("int readInt()", "返回 int 的函数：把「读一个整数」这件事打包，主函数只剩三行调用。"),
             ("while (c < '0' || c > '9')", "跳过所有非数字字符，所以数据跨行、多空格都能正确读。"),
             ("x = x * 10 + (c - '0');", "逐位拼数：每读一位就把已有结果左移一位再加上新数字。"),
             ("nth_element(a, a + k, a + n);", "第 k 小放到 a[k]，左边不大于它、右边不小于它，两侧无序。"),
             ("printf(\"%d\\n\", a[k]);", "直接输出 a[k]；不必再 sort，排了也只会更慢。"),
         ],
         pitfalls=["把 k 当成 1 起，输出 a[k-1] → 全 WA。",
                   "把数组开在 main 里 → 栈溢出，本地小数据正常、大数据 RE。",
                   "用 sort 交：5×10⁶ 规模下 nlogn 约 1.1×10⁸ 次比较，容易 TLE。",
                   "数组少开一个 0（开成 5×10⁵）→ 越界，小数据看不出来。"])

CH5 = CH("回文质数", "P1217", "普及-", "https://www.luogu.com.cn/problem/P1217",
         [P("回文数是正着读与反着读都一样的数，151 既是回文数又是质数，称为回文质数。"),
          P("求区间 [a, b] 内所有回文质数，每行输出一个，从小到大。"),
          P("输入格式：一行两个整数 a、b（5 ≤ a &lt; b ≤ 10⁸）。"),
          P("输出格式：若干行，每行一个回文质数。")],
         hint=["先写两个小函数：判质数、判回文。主函数只负责枚举和调用，逻辑立刻变短。",
               "判质数只需试除到 √x，不必试到 x。",
               "10⁸ 全枚举太慢。注意偶数位数的回文数有一个固定因数，想想是几。"],
         idea=["偶数位回文数一定能被 11 整除：以 abba 为例，1001a + 110b = 11(91a + 10b)。",
               "所以除 11 本身以外，偶数位回文数全是合数。答案都落在 1~7 位数里。",
               "把 b 截断到 9999999，枚举量从 10⁸ 降到 10⁷。",
               "枚举 i ∈ [a, b]：先判回文（几次除法，极快），是回文再判质数（试除到 √i）。",
               "只有回文才做质数判定，实际质数判定约 1.1 万次，总耗时约 0.1 秒。"],
         code=r'''#include <bits/stdc++.h>
using namespace std;

bool isPrime(int x) {
    if (x < 2) return false;                        // 0、1 不是质数
    for (int i = 2; (long long)i * i <= x; ++i)     // 只试到 √x
        if (x % i == 0) return false;
    return true;
}

bool isPal(int x) {
    int t = x, r = 0;
    while (t > 0) { r = r * 10 + t % 10; t /= 10; } // 把 x 倒过来
    return r == x;                                  // 用临时变量，不改原数
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int a, b;
    cin >> a >> b;
    if (b > 9999999) b = 9999999;   // 8 位及以上回文数都是 11 的倍数

    for (int i = a; i <= b; ++i)
        if (isPal(i) && isPrime(i)) cout << i << "\n";
    return 0;
}''',
         explain=[
             ("if (b > 9999999) b = 9999999;", "偶数位回文数都能被 11 整除，截断后不会漏解，枚举量少一个数量级。"),
             ("bool isPrime(int x)", "判定函数：返回 bool，调用处 <code>if (isPrime(i))</code> 读起来就是一句话。"),
             ("(long long)i * i <= x", "i*i 在 i 接近 10⁵ 时会接近 10¹⁰，用 int 直接溢出成负数 → 死循环。"),
             ("int t = x, r = 0;", "用临时变量倒序，保持 x 不变；若直接改 x，后面的质数判定就拿到错的值。"),
             ("if (isPal(i) && isPrime(i))", "短路求值：先判回文（便宜），只有回文才做质数判定。"),
         ],
         pitfalls=["把 1 当质数（别的题 a 可能从 1 开始）。",
                   "循环条件写成 <code>i &lt; x</code> 而不是 <code>i*i &lt;= x</code>，10⁷ 级别直接 TLE。",
                   "不截断 b，枚举到 10⁸ → TLE。",
                   "isPal 里直接改 x，导致 isPrime 拿到的不是原数 → 全错。"])

CHS = [CH1, CH2, CH3, CH4, CH5]

LESSONS = [LESSON(
    15, "回顾三：函数、结构体与排序",
    "把第 11~14 节的四件工具装回同一把刀：函数打包逻辑，结构体打包数据，sort + cmp 按你的规则排队，"
    "枚举把搜索空间数清楚。5 道题，90 分钟，做完再进贪心。",
    90, ["回顾", "5 题"], "普及-",
    SEC, check=CHECK, challenge=CH1, refs=[
        "《算法竞赛入门笔记》：函数、结构体与排序相关章节",
        "《算法竞赛进阶指南》第 0x05 节：排序（cmp 与严格弱序）",
        "洛谷 P1093、P1104、P1068 题解区关于多关键字排序的讨论",
        "《算法竞赛黄金法则》：先把比较规则写清楚，再动手排序",
    ])]

# 回顾章由 render.render_review 渲染，读的是 challenges 列表（复数）
LESSONS[0]["challenges"] = CHS
