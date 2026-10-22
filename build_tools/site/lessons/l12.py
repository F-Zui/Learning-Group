# -*- coding: utf-8 -*-
"""第 12 节 · 结构体与多关键字排序"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dsl import *  # noqa

SEC = []

SEC.append(P("前 11 节里，一个数组只装一种东西：全是成绩，或全是坐标。可真实题目里，一个学生同时有学号、语文、数学、英语、总分，"
             "而且要求<b>按总分排、总分相同看语文、还相同看学号</b>。裸数组排不动这种题——学号一个数组、总分一个数组，一排序就对不上号。"
             "<b>结构体把多个字段打包成一个整体</b>，排序时整包一起搬，字段之间的对应关系才不会散。"))

SEC.append(EX("奖学金", "P1093", "普及-", "https://www.luogu.com.cn/problem/P1093",
              ["输入第一行一个整数 n，表示学生人数（n 不超过 300，且至少有 5 人）。",
               "接下来 n 行，每行三个整数（0~100），依次是语文、数学、英语成绩。学生按输入顺序编号为 1 到 n。",
               "按总分从高到低排序；总分相同按语文从高到低；语文也相同按学号从小到大。",
               "输出前 5 名，每行两个整数：学号、总分。"],
              sample="输入：\n6\n90 67 80\n87 66 91\n78 89 91\n88 99 77\n67 89 64\n78 89 98\n"
                     "输出：\n6 265\n4 264\n3 258\n2 244\n1 237"))

SEC.append(P("排序规则有三层。字段要一起搬、比较要按多个键——这是 struct 加 cmp 的典型场景。先看 6 张语法卡。"))

# ---------------------------------------------------------------- 新语法
SEC.append(FN(
    "struct：把多个字段打包成一个类型",
    "struct 名字 {\n    类型 字段1;\n    类型 字段2;\n};          // ← 这个分号不能漏",
    [("struct", "声明一个新类型。字段就是普通变量声明，可以是 <code>int</code>、<code>double</code>、<code>string</code>，甚至数组。"),
     ("名字", "习惯首字母大写：<code>Stu</code>、<code>Node</code>。用法和 <code>int</code> 一样：<code>Stu a;</code>、<code>Stu s[305];</code>。"),
     ("结尾 ;", "必须有。漏了会让后面几十行一起报 <code>expected ';'</code>，错误行号离真正的坑很远。")],
    example=r'''struct Stu {
    int id;
    int sum;
};                             // 分号不能漏

int main() {
    Stu a;                     // 像 int 一样定义变量
    a.id = 1;  a.sum = 265;
    Stu s[3];                  // s[0]、s[1]、s[2] 各是一个学生
    s[1].sum = 244;
    cout << a.id << " " << s[1].sum << "\n";
}''',
    notes=["示例省略 <code>#include &lt;bits/stdc++.h&gt;</code> 与 <code>using namespace std;</code>，每张卡片都照此补。",
           "局部结构体变量<b>不会自动初始化</b>：<code>Stu a;</code> 之后 <code>a.sum</code> 是随机值，读之前必须先写。"],
    brief="一个对象装多个字段，整包搬动不散架"))

SEC.append(FN(
    "sort：区间左闭右开",
    "sort(首指针, 尾后指针);              // 默认升序\nsort(首指针, 尾后指针, 比较器);      // 自定义顺序",
    [("首指针", "第一个元素的地址：<code>a</code>。"),
     ("尾后指针", "最后一个元素<b>下一个</b>位置的地址。排 a[0..n−1] 就写 <code>a + n</code>。"),
     ("比较器", "省略时按 <code>&lt;</code> 升序；结构体数组必须自己传。"),
     ("复杂度", "O(n log n)。n = 10⁶ 约 2×10⁷ 次比较，1 秒内跑完。")],
    example=r'''int main() {
    int a[6] = {5, 2, 8, 1, 9, 3};
    sort(a, a + 6);                  // 排 a[0..5] → 1 2 3 5 8 9
    sort(a, a + 3);                  // 只排前 3 个
    sort(a, a + 6, greater<int>());  // 降序 → 9 8 5 3 2 1

    int b[6] = {5, 2, 8, 1, 9, 3};
    sort(b + 1, b + 6);              // 1 下标：排 b[1..5]，b[0] 不动
}''',
    notes=["<code>sort(a, a + n - 1)</code> 只排了 n−1 个，最后一个不参与——最常见的差一位。",
           "1 下标数组写成 <code>sort(a + 1, a + n + 1)</code>，末尾是 <code>+ n + 1</code>，别抄成 <code>+ n</code>。"],
    brief="O(n log n) 排序，记住左闭右开"))

SEC.append(FN(
    "cmp：自定义比较器与严格弱序",
    "bool cmp(const T &a, const T &b) {\n    return a.键 < b.键;      // 返回 true ⇒ a 排在 b 前面\n}",
    [("返回值", "<code>bool</code>，只回答“a 该不该排在 b 前面”，不是返回差值，也不是返回“a 更小”。"),
     ("const T &amp;", "按引用传，避免每个元素被整包复制；<code>const</code> 保证比较时不改数据。"),
     ("运算符", "只写严格不等 <code>&lt;</code> 或 <code>&gt;</code>，<b>绝不能写 <code>&lt;=</code>、<code>&gt;=</code></b>。"),
     ("严格弱序", "<code>cmp(a,a)</code> 必须为 false；<code>cmp(a,b)</code> 与 <code>cmp(b,a)</code> 不能同时为 true；必须可传递。")],
    example=r'''bool cmpBig(int a, int b) { return a > b; }   // 降序：大的在前
bool bad(int a, int b) { return a >= b; }     // cmp(a,a) 竟返回 true

int main() {
    int a[5] = {3, 1, 4, 1, 5};
    sort(a, a + 5, cmpBig);                   // 5 4 3 1 1
    sort(a, a + 5, bad);                      // 可能直接 RE
}''',
    notes=["<code>std::sort</code> 的分区循环靠这三条假设决定指针往哪走。用 <code>&gt;=</code> 时" 
           "“等于 pivot 也算小”的指针停不下来，会一路越过数组末尾写内存，症状是 <b>RE</b> 而不是编译错误。"],
    brief="告诉 sort“谁排在前面”，必须严格弱序"))

SEC.append(FN(
    "greater：标准库自带的降序比较器",
    "sort(a, a + n, greater<类型>());",
    [("&lt;类型&gt;", "尖括号里写元素类型，必须和数组元素类型一致。"),
     ("末尾 ()", "这对圆括号是“构造一个对象”。漏了就语法错误：<code>greater&lt;int&gt;</code> 只是类型，类型不能当值传。"),
     ("等价", "<code>greater&lt;int&gt;()</code> 等价于 <code>[](int x, int y) { return x &gt; y; }</code>。")],
    example=r'''int main() {
    int a[5] = {3, 1, 4, 1, 5};
    sort(a, a + 5, greater<int>());       // 5 4 3 1 1
}''',
    notes=["同族的 <code>less&lt;int&gt;()</code> 就是 <code>&lt;</code>，也正是 sort 省略比较器时的默认行为。"],
    brief="降序一行搞定，注意末尾那对括号"))

SEC.append(FN(
    "stable_sort：稳定排序",
    "stable_sort(首, 尾后, 比较器);     // 认为“相等”的元素保持原有先后",
    [("稳定", "比较器认为等价的两个元素，排序后仍按原来的顺序排列；<code>sort</code> 不保证这一点。"),
     ("用法", "多关键字：<b>从最次要的键排到最重要的键</b>，每趟都用 <code>stable_sort</code>。"),
     ("代价", "多花 O(n) 内存，常数略大；n ≤ 10⁵ 完全够用。")],
    example=r'''// 假设已有例题里的 Stu s[] 与 n：目标 总分降序 → 语文降序 → 学号升序
sort(s, s + n, [](const Stu &a, const Stu &b) { return a.id < b.id; });
stable_sort(s, s + n, [](const Stu &a, const Stu &b) { return a.ch > b.ch; });
stable_sort(s, s + n, [](const Stu &a, const Stu &b) { return a.sum > b.sum; });''',
    notes=["顺序必须从次要到主要。反过来先排主键，后面几趟会把主键重新打乱。",
           "第一趟按唯一键（如学号）排，用 <code>sort</code> 也不会错，因为根本没有并列。"],
    brief="相等元素不打乱，多关键字分层排序的利器"))

SEC.append(FN(
    "lambda：就地写一个匿名比较器",
    "sort(a, a + n, [](const T &x, const T &y) { return 条件; });",
    [("[]", "捕获列表：空表示不用外部变量；<code>[&amp;]</code> 表示按引用用外部变量。"),
     ("(参数)", "和普通函数形参一样，写 <code>const T &amp;</code> 最省。"),
     ("位置", "就地写在 <code>sort</code> 第三个参数处，不必在全局另起一个函数；整个 lambda 后用 <code>)</code> 和 <code>;</code> 收尾。")],
    example=r'''struct Stu { int id, sum; };

int main() {
    Stu s[3] = {{1, 240}, {2, 265}, {3, 240}};
    sort(s, s + 3, [](const Stu &x, const Stu &y) {
        if (x.sum != y.sum) return x.sum > y.sum;   // 总分降序
        return x.id < y.id;                         // 学号升序兜底
    });
}''',
    notes=["lambda 里不能修改未被捕获的外部变量，编译会直接报错。",
           "只在排序里用一次的比较器，用 lambda 比在全局起名字更清楚。"],
    brief="就地写比较器，不用起名字"))

# ---------------------------------------------------------------- 例题
SEC.append(IDEA("例题怎么想：三个优先级，写成三层 if", [
    "排序规则有三层：总分 → 语文 → 学号。写成三层 if，<b>第一个不同的关键字就定胜负，后面的不看</b>。",
    P("最容易忽略的是最后一层 <code>return a.id &lt; b.id;</code>。它不是“顺便加一句”，而是把平局彻底消掉的兜底："
      "学号唯一，任意两人都有确定先后。少了它，总分语文都相同的人会互相“不小于”，严格弱序被破坏。"),
    C(r'''#include <bits/stdc++.h>
using namespace std;

struct Stu {
    int id;            // 原始下标：输入顺序就是学号，排序后靠它认人
    int ch, ma, en;    // 语文、数学、英语
    int sum;           // 总分：输入时就算好，别在 cmp 里反复加
};

// 返回 true 表示 a 应排在 b 前面
bool cmp(const Stu &a, const Stu &b) {
    if (a.sum != b.sum) return a.sum > b.sum;   // 第一关键字：总分降序
    if (a.ch  != b.ch ) return a.ch  > b.ch;    // 第二关键字：语文降序
    return a.id < b.id;                         // 第三关键字：学号升序
}

int main() {
    int n;
    cin >> n;
    Stu s[305];
    for (int i = 0; i < n; ++i) {
        s[i].id = i + 1;                        // 先记下原始下标，排完序就找不回来了
        cin >> s[i].ch >> s[i].ma >> s[i].en;
        s[i].sum = s[i].ch + s[i].ma + s[i].en;
    }

    sort(s, s + n, cmp);                        // 左闭右开：覆盖 s[0] ~ s[n-1]

    for (int i = 0; i < 5 && i < n; ++i)
        cout << s[i].id << " " << s[i].sum << "\n";
    return 0;
}''', "完整代码"),
    EXPLAIN("逐行拆解", [
        ("struct Stu { int id; int ch, ma, en; int sum; };", "5 个字段打成一个包。排序搬动的是整个 Stu，学号和总分的对应关系不会散。"),
        ("bool cmp(const Stu &a, const Stu &b)", "const 引用：n = 300 时省下数百次结构体拷贝，也防止比较过程改坏数据。"),
        ("if (a.sum != b.sum) return a.sum > b.sum;", "第一层：总分不同就按总分降序定胜负，后两行不执行。先判“不同”再比较，不能反。"),
        ("if (a.ch != b.ch) return a.ch > b.ch;", "走到这里说明总分相同，改用语文继续分。"),
        ("return a.id < b.id;", "最后一层必须给出“不平局”的判据。学号唯一，正好当兜底。"),
        ("s[i].id = i + 1;", "在排序<b>之前</b>把原始下标存进结构体。排完序 s[k] 是第 k 名，只有 id 能告诉你他是谁。"),
        ("s[i].sum = ...;", "总分在输入时算好。放进 cmp 里每次现算，一次排序要多做 O(n log n) 次加法。"),
        ("sort(s, s + n, cmp);", "左闭右开 [s+0, s+n)，正好覆盖 s[0]~s[n−1]。写成 s+n−1 会漏掉最后一个。"),
    ]),
]))

SEC.append(AFTER("同一个排序逻辑的两种载体", [
    P("A 与 C 结果完全一样。逻辑复杂、想单独验算就用独立 cmp；关键字多到写不清优先级就逐层 stable_sort，"
      "每层只关心一个键。lambda 只是 A 的就地缩写，见上一张卡片。"),
    C(r'''// A：独立 cmp 函数（本页用法）—— 定义见上面例题
sort(s, s + n, cmp);

// C：逐层 stable_sort —— 从最次要的键排到最重要的键
sort(s, s + n, [](const Stu &a, const Stu &b) { return a.id < b.id; });          // 最次要
stable_sort(s, s + n, [](const Stu &a, const Stu &b) { return a.ch > b.ch; });   // 次要
stable_sort(s, s + n, [](const Stu &a, const Stu &b) { return a.sum > b.sum; }); // 主要''', "两种写法"),
    P("C 的代价是排序 k 遍、常数乘 k；好处是每层表达式只有一两个字符，几乎不可能写错优先级。"),
]))

SEC.append(WARN("这一节最容易犯的 5 个错", [
    "cmp 里用 <code>&gt;=</code> 或 <code>&lt;=</code>。<code>cmp(a,a)</code> 返回 true，严格弱序被破坏，"
    "洛谷上的典型症状是 <b>RE</b>（Segmentation fault，常挂在中段测试点），而不是提示你写错了。改成 <code>&gt;</code> 立刻通过。",
    "漏写结构体定义结尾的 <code>};</code>，编译器在下一个函数处报 <code>expected ';' before ...</code>，报错行号和真正的坑差几十行。",
    "<code>sort(s, s + n - 1, cmp)</code> 漏排最后一个元素：最大（或最小）的那个人永远上不去，表现为“答案总是差一名”的 WA。",
    "<code>greater&lt;int&gt;</code> 少写末尾的圆括号。<code>sort(a, a+n, greater&lt;int&gt;)</code> 编译错误：类型不是表达式。",
    "只写了总分一个关键字。测试点里专门有“总分相同、语文不同”的构造，单关键字版能过大部分点，剩下的 WA 很不明显——因为前几名常常恰好没并列。",
]))

SEC.append(REPRO("不看本页，把 P1093 敲一遍并提交。",
                 "再做三组破坏性实验：① 把 cmp 里两个 <code>&gt;</code> 全改成 <code>&lt;</code>，看输出是否整体倒过来；"
                 "② 把最后一层改成 <code>return false;</code>，构造三个总分都是 240 的学生，看输出顺序是否还受规则约束"
                 "（它可能恰好没变——这正是未定义行为的可怕之处）；"
                 "③ 故意写成 <code>return a.sum &gt;= b.sum;</code>，多交几次观察是否偶发 RE。",
                 "改一改：把 cmp 换成等价的 lambda；再换成方案 C 的三趟 stable_sort，确认两种写法的输出逐字节相同。"))

# ---------------------------------------------------------------- 数学补给
M = MATH("全序、偏序与严格弱序", [
    P("排序器要的数学条件很明确：给定任意两个元素，它得能判断“谁先”。"),
    P("<b>全序</b>：任意两个元素都可比且无并列。按 总分＋语文＋学号 排完，任意两人次序唯一——这才是全序，"
      "结果确定、可复现。<b>偏序</b>只保证可比的那部分有次序，允许并列。"),
    P("<b>严格弱序</b>是 std::sort 的全部要求，翻成 cmp 就是三条公理："),
    L(["非自反：<code>cmp(a, a)</code> 恒为 false —— 自己不能排在自己前面。",
       "非对称：<code>cmp(a, b)</code> 为 true 时 <code>cmp(b, a)</code> 必须为 false。",
       "传递性：<code>cmp(a, b)</code> 与 <code>cmp(b, c)</code> 为 true，则 <code>cmp(a, c)</code> 必须为 true。"]),
    P("写 <code>&gt;=</code> 违反的是第一条。sort 分区里有一句“只要还小就继续前进”，"
      "而“等于 pivot 也算小”会让它永远停不下来，指针冲出数组末尾——所以症状是 RE 而不是 WA。"),
    P("<b>字典序</b>：把 k 个关键字看成 k 元组 (k₁, k₂, …, k_k)，从第一个分量开始比，遇到第一个不同分量就定胜负。"
      "本节的 cmp 就是字典序的手写展开；<code>sort</code> 排 <code>pair</code>、<code>string</code> 用的也是它。"
      "它一定是严格弱序，因为元组比较本身是全序；唯一例外是元组完全相等，此时 cmp 返回 false，正好满足非自反——"
      "这就是<b>最后一层要留一个唯一键</b>的原因。"),
    P("<b>稳定排序与基数排序</b>：对 k 个关键字，从最次要的键开始做 k 趟稳定排序，结果等价于一次多关键字排序。"
      "归纳证明：第 i 趟结束时序列按“前 i 个次要键”有序；第 i+1 趟稳定，相等元素保留上一趟次序，"
      "次要键信息被完整带过去。这就是 LSD 基数排序的正确性来源。"),
])

THINK = [
    "两个人总分、语文都相同时，cmp 最后写 <code>a.id &lt; b.id;</code> 与写 <code>return false;</code> 有什么区别？后者破坏了哪条公理？",
    "只按总分排序、不加学号兜底时，两个 250 分的同学谁在前？这个答案由什么决定？为什么不能指望它？",
    "字段有 6 个关键字时，你写 6 层 if 还是逐层 stable_sort？两种写法各要多少次比较、几趟排序？",
    "把 <code>struct</code> 换成 <code>pair&lt;int,int&gt;</code>，两关键字排序怎么写？三关键字呢？什么时候该退回 struct？",
    "“结构体里存原始下标”这件事还能用在哪？（输出原名次、离散化、排序后映射回原数组、按原顺序输出答案）",
    "若题目要求“总分相同的人按<b>输入顺序</b>输出”，用 sort＋下标 与 stable_sort 哪个更短？哪个更不容易写错？",
]

CHECK = [
    "能默写 struct 定义 + 结构体数组读入，且不漏结尾的分号。",
    "能解释为什么 <code>cmp(a, a)</code> 必须返回 false，以及违反后为什么是 RE 而不是编译错误。",
    "能写出三关键字的 cmp，并说清每层“先判不同再比较”的意义。",
    "知道 <code>sort(a, a + n)</code> 覆盖哪些元素，写成 <code>a + n - 1</code> 会怎样。",
    "知道 <code>greater&lt;int&gt;()</code> 末尾那对括号为什么不能省。",
]

CHALLENGE = CH(
    "生日", "P1104", "普及-", "https://www.luogu.com.cn/problem/P1104",
    [P("有 n 个人，每人给出姓名和出生年、月、日，请按年龄从大到小输出他们的姓名。"),
     P("如果两个人的生日完全相同，则后输入的那个人排在前面。"),
     P("输入第一行一个整数 n（n ≤ 100），接下来 n 行，每行一个字符串和三个整数：姓名、年、月、日。输出 n 行，每行一个姓名。")],
    hint=["年龄大就是出生早。先把“年龄从大到小”翻译成“日期从小到大”，比较方向就不会写反。",
          "年、月、日是分层比较：年份不同时，月和日根本不用看。",
          "“生日相同的后输入排前面”说明光有日期不够——把输入顺序也变成一个能比较的数字存起来。"],
    idea=["结构体存 name、y、m、d、idx，idx 按输入顺序编号。",
          "cmp：y 小的在前；y 相同比 m；m 相同比 d；三者全相同则 idx 大的在前。",
          "idx 唯一，所以任意两人都有确定次序，cmp 永远不会对两个不同元素同时返回 false，严格弱序成立，sort 安全。",
          "按排序后的顺序逐个输出 name。"],
    code=r'''#include <bits/stdc++.h>
using namespace std;

struct Per {
    string name;
    int y, m, d, idx;       // idx：输入顺序，用来打破生日相同的平局
};

bool cmp(const Per &a, const Per &b) {
    if (a.y != b.y) return a.y < b.y;    // 出生早 = 年龄大
    if (a.m != b.m) return a.m < b.m;
    if (a.d != b.d) return a.d < b.d;
    return a.idx > b.idx;                // 生日相同：后输入（idx 大）的排前面
}

int main() {
    int n;
    cin >> n;
    Per p[105];
    for (int i = 0; i < n; ++i) {
        cin >> p[i].name >> p[i].y >> p[i].m >> p[i].d;
        p[i].idx = i;                    // 先记下原始顺序，排完序就找不回来了
    }

    sort(p, p + n, cmp);                 // 左闭右开

    for (int i = 0; i < n; ++i) cout << p[i].name << "\n";
    return 0;
}''',
    explain=[
        ("struct Per { string name; int y, m, d, idx; };", "姓名和日期放在一起，排序时整包搬，姓名不会和日期错位。"),
        ("if (a.y != b.y) return a.y < b.y;", "年份小 = 出生早 = 年龄大，所以是 <code>&lt;</code>。顺着“年龄大”写成 <code>&gt;</code> 就整体反了。"),
        ("if (a.m != b.m) return a.m < b.m;", "同年才比月；月小 = 同一年里出生更早。"),
        ("return a.idx > b.idx;", "唯一键兜底：生日完全相同时，后输入的 idx 更大，要排前面，所以用 <code>&gt;</code>。"),
        ("sort(p, p + n, cmp);", "覆盖 p[0..n−1]。cmp 对任意两个不同元素都有确定结论，不会出现“互相都不小于”。"),
    ],
    pitfalls=["年份比较写成 <code>a.y &gt; b.y</code>（顺着“年龄大”的方向想），输出整个反了。",
              "忘了 idx 这一层，收尾写 <code>return false;</code>。生日相同的两人次序不受控，且严格弱序被破坏，可能 RE。",
              "用 <code>scanf(\"%s\", s.name)</code> 读 <code>string</code>——<code>string</code> 不是字符数组，会崩。"
              "要么 <code>cin &gt;&gt;</code>，要么把字段改成 <code>char name[25]</code>。",
              "结构体数组开成 <code>Per p[100]</code> 而 n 正好 100，越界写坏别的变量，症状时好时坏。"],
)

LESSONS = [LESSON(
    12, "结构体与多关键字排序",
    "用 struct 把多字段对象打包成可整体搬动的类型，用 cmp 把“总分 → 语文 → 学号”写成严格弱序，"
    "并搞清 sort 的左闭右开、greater、stable_sort 与 lambda 的分工。",
    60, ["struct", "sort", "cmp 严格弱序"], "普及-",
    SEC, math=M, think=THINK, check=CHECK, challenge=CHALLENGE,
    refs=["《算法竞赛进阶指南》0x05：排序与离散化",
          "《算法竞赛试炼场：洛谷300题精析》排序章",
          "洛谷 P1093、P1104 题解区的高赞写法"],
)]
