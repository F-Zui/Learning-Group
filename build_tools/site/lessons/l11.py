# -*- coding: utf-8 -*-
"""第 11 节 · 函数：参数传递与返回值"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dsl import *  # noqa

SEC = []

SEC.append(P("到现在为止，你所有代码都挤在 <code>main</code> 里。同一段逻辑出现第二次，就得整段复制——"
             "改要改两处，错就两处一起错。<b>函数是把一段逻辑装进一个名字里</b>："
             "参数决定喂它什么，返回值决定它交回什么，函数名替你记住“这段在干什么”。"))

SEC.append(EX("距离函数", "P5735", "入门", "https://www.luogu.com.cn/problem/P5735",
              ["给出平面直角坐标系上不在同一条直线上的三个点 A、B、C 的坐标，求三角形 ABC 的周长。",
               "输入三行，每行两个实数，表示一个点的横、纵坐标（允许是小数）。",
               "输出一行一个实数，为三角形周长，保留两位小数。"],
              sample="输入：\n0 0\n0 3\n4 0\n输出：\n12.00"))

SEC.append(P("三条边公式一模一样，只有坐标不同。不用函数，<code>sqrt(dx*dx+dy*dy)</code> 要抄三遍。"
             "先看 5 张语法卡。"))

# ---------------------------------------------------------------- 新语法
SEC.append(FN(
    "函数定义与调用",
    "返回类型 函数名(形参表) {\n    ...\n    return 值;\n}\n\n函数名(实参表);      // 调用",
    [("返回类型", "结果是什么类型：算距离 <code>double</code>，判质数 <code>bool</code>，只做事不出结果 <code>void</code>。"),
     ("形参表", "占位符，每个参数各自声明，类型写全：<code>(double x1, double y1)</code>。"),
     ("return 值;", "把结果交回调用处，并立刻结束函数。"),
     ("调用", "实参按位置一一抄进形参，然后跳进函数体。")],
    example=r'''double area(double w, double h);   // 前置声明：定义在 main 之后就靠它

int main() {
    cout << area(3, 4) << "\n";    // 实参 3、4 抄给形参 w、h → 12
    return 0;
}

double area(double w, double h) {  // 定义：真正实现
    return w * h;
}''',
    notes=["示例省略 <code>#include &lt;bits/stdc++.h&gt;</code> 与 <code>using namespace std;</code>，所有卡片同理。",
           "定义在 <code>main</code> 之后必须先声明，否则报 <code>area was not declared in this scope</code>。"
           "函数最多 <code>return</code> 一个值，要带出两个结果只能靠引用参数。"],
    brief="参数进、返回值出，写一次调用任意次"))

SEC.append(FN(
    "值传递（形参是副本）",
    "void f(int x)      // x 是实参的一份拷贝",
    [("形参 int x", "调用时把实参的值拷一份进来，两个变量互不相干。"),
     ("改 x", "改的是副本。函数返回后副本销毁，实参一个字节都没变。"),
     ("代价", "传大对象要整体复制：10⁵ 个 int 的数组按值传进去，等于多拷 400 KB。")],
    example=r'''void addOne(int x) { x += 1; }

int main() {
    int a = 0;
    addOne(a);
    cout << a << "\n";             // 0，不是 1
}''',
    notes=["想改实参只有两条路：引用参数，或把新值 <code>return</code> 出来再赋回 <code>a = addOne(a);</code>。",
           "<code>int</code>、<code>double</code>、<code>char</code> 这类小类型，值传递最省事。"],
    brief="默认方式：改不了实参，适合小类型"))

SEC.append(FN(
    "引用参数 &（形参是别名）",
    "void f(int &x)     // x 是实参的另一个名字，不是副本",
    [("int &x", "&amp; 写在类型后、变量名前。x 与实参是同一块内存的两个名字。"),
     ("读 / 写 x", "读写 x 就是读写实参，函数返回后实参真的变了。"),
     ("实参要求", "必须是能取地址的变量。传 <code>f(3)</code>、<code>f(a + b)</code> 直接编译错误。")],
    example=r'''void addOne(int &x) { x += 1; }   // 只多了一个 &

int main() {
    int a = 0;
    addOne(a);
    cout << a << "\n";             // 1
}''',
    notes=["引用参数是“函数返回多个结果”的标准做法："
           "<code>void getMinMax(int a[], int n, int &amp;mn, int &amp;mx)</code>，调用后两个变量都被写好。",
           "所以 <code>mySwap(int a, int b)</code> 什么也没干，<code>mySwap(int &amp;a, int &amp;b)</code> 才对。"],
    brief="改实参就是改本体，用来带出多个结果"))

SEC.append(FN(
    "const 引用 const &（只读 + 不复制）",
    "int countChar(const string &s, char c);",
    [("const", "承诺函数内不修改参数。写 <code>s[0] = 'x'</code> 直接编译错误。"),
     ("&amp;", "不复制，直接引用原对象，省掉拷贝开销。"),
     ("用在哪", "参数是大对象（<code>string</code>、结构体、数组）且只读时，一律 <code>const T &amp;</code>。")],
    example=r'''int countChar(const string &s, char c) {
    int cnt = 0;
    for (int i = 0; i < (int)s.size(); ++i)
        if (s[i] == c) ++cnt;      // 只读，符合 const 的承诺
    return cnt;
}
// countChar("banana", 'a') == 3''',
    notes=["小类型不要加 <code>&amp;</code>：<code>const int &amp;x</code> 比 <code>int x</code> 还慢一点。"],
    brief="大对象只读传参的标准写法"))

SEC.append(FN(
    "递归函数雏形",
    "long long fact(int n) {\n    if (n <= 1) return 1;           // 出口\n    return 1LL * n * fact(n - 1);   // 递推\n}",
    [("出口", "最小规模直接给答案。没有出口就是无限递归，必然 RE。"),
     ("递推", "把规模 n 化成规模 n−1 的同类问题，规模必须严格变小。"),
     ("栈帧", "每层调用都留一份自己的局部变量，返回时才释放。深度 × 每帧大小 = 实际占用。"),
     ("1LL *", "强制按 <code>long long</code> 相乘。20! = 2432902008176640000，早就超 int。")],
    example=r'''long long fact(int n) {
    if (n <= 1) return 1;
    return 1LL * n * fact(n - 1);
}
// fact(5) = 120, fact(20) = 2432902008176640000''',
    notes=["本节的立场：<b>先会读递归，再决定用不用</b>。递归深度一般别超过 10⁵ 层。"],
    brief="自己调用自己：一个出口 + 规模变小"))

# ---------------------------------------------------------------- 例题
SEC.append(IDEA("例题怎么想：一条边的公式，调用三次", [
    "题目只有一件事：三条边相加。而“求一条边”要做三次。",
    P("所以把“求一条边”抽成只依赖 4 个形参的纯函数，再在 main 里调用三次。"
      "这种函数最好验算——随手喂两组坐标就能判断对不对，不用管程序的其他部分。"),
    C(r'''#include <bits/stdc++.h>
using namespace std;

// 只依赖 4 个形参，不碰任何全局状态，好测、可复用
double dist(double x1, double y1, double x2, double y2) {
    double dx = x1 - x2;
    double dy = y1 - y2;
    return sqrt(dx * dx + dy * dy);       // 勾股定理
}

int main() {
    double ax, ay, bx, by, cx, cy;
    cin >> ax >> ay >> bx >> by >> cx >> cy;

    // 三条边同一个公式，只有坐标不同 —— 这正是函数的用武之地
    double ans = dist(ax, ay, bx, by)
               + dist(bx, by, cx, cy)
               + dist(cx, cy, ax, ay);

    cout << fixed << setprecision(2) << ans << "\n";   // fixed 才表示"小数位数"
    return 0;
}''', "完整代码"),
    EXPLAIN("逐行拆解", [
        ("double dist(double x1, ..., double y2)", "返回 double：距离带小数，不能收成 int。4 个形参的顺序必须和调用时完全一致。"),
        ("double dx = x1 - x2;", "dx、dy 是 dist 的局部变量，出了函数就销毁，和 main 里的同名变量互不干扰。"),
        ("return sqrt(dx * dx + dy * dy);", "sqrt 的参数与返回值都是 double，与返回类型一致，不做隐式转换。"),
        ("cin >> ax >> ... >> cy;", "六个实数一次读完。cin 自动跳过换行，所以输入分三行也正确。"),
        ("dist(a...) + dist(b...) + dist(c...)", "三次独立调用：每次把新实参抄进形参，第一次的局部变量早已销毁，互不影响。"),
        ("cout << fixed << setprecision(2) << ans;", "fixed 表示“小数点后几位”。只写 setprecision(2) 是“总共两位有效数字”，会输出 12 而不是 12.00。"),
    ]),
]))

SEC.append(AFTER("数组传参：长度必须自己扛过去", [
    P("数组名传进函数时只传了首地址，长度在这条路上丢了。所以形参里必须再给一个 n，"
      "而且<b>不能</b>在函数里用 <code>sizeof</code> 反算长度——那时 <code>a</code> 已经是指针，<code>sizeof(a)</code> 恒为 8。"),
    C(r'''int sumOf(const int a[], int n) {      // const int a[] 等价于 const int *a
    int s = 0;
    for (int i = 0; i < n; ++i) s += a[i];
    return s;
}
// 调用 sumOf(x, 5)；在 main 里 sizeof(x)/sizeof(x[0]) 才等于 5''', "数组 + 长度，缺一不可"),
    P("二维数组同理，但第二维必须写出：<code>void f(int a[][105], int n, int m)</code>。"),
]))

SEC.append(AFTER("作用域与爆栈：变量放在哪，决定它能活多久", [
    T(["写在哪", "叫什么", "初值", "活到什么时候", "内存区"], [
        ["函数或 <code>{}</code> 内", "局部变量", "随机值（垃圾）", "出了这层花括号就销毁", "栈，约 1~8 MB"],
        ["所有函数之外", "全局变量", "自动为 0", "整个程序运行期间", "静态区，可用几百 MB"],
    ]),
    P("结论很硬：<code>int a[1000005]</code> 占 4 MB，写在 <code>main</code> 里会栈溢出（本地可能还能跑，评测机 RE）；"
      "写到所有函数外面就没事，还自动清零。<b>数组长度超过 10⁵ 就放全局</b>。"),
    P("但全局变量谁都能改，出了问题极难定位。所以只有“很大的数组”和“全程序共享的表”才放全局，能用参数传的一律用参数。"),
]))

SEC.append(WARN("这一节最容易犯的 5 个错", [
    "想让函数改实参却忘写 <code>&amp;</code>。程序能跑、输出还是原值，WA。"
    "典型是 <code>mySwap(int a, int b)</code>：函数里换得很认真，main 里一点没变。",
    "在函数里写 <code>sizeof(a) / sizeof(a[0])</code> 算长度。a 已退化为指针，结果恒为 2，循环只跑 2 次，WA。",
    "把大数组写在 <code>main</code> 里。<code>int a[1000005]</code> 超过栈容量，本地正常、评测机 RE。",
    "递归忘写出口，或出口永远不成立。症状是 RE（栈溢出）或 TLE，不是编译错误，第一次遇到很难想到。",
    "函数定义写在 <code>main</code> 后面又没声明。报 <code>xxx was not declared in this scope</code>，"
    "提示指向调用行，容易误以为自己名字打错了。",
]))

SEC.append(REPRO("不看本页，把 P5735 敲一遍并提交。",
                 "做三组对照：① 把 <code>dist</code> 的形参与 main 里的变量全改成 <code>int</code>，输入 <code>0 0 / 0 3 / 4 0</code>，"
                 "答案仍是 12.00（<code>sqrt</code> 会把 int 转成 double）；② 输入改成 <code>0.5 0 / 0 3 / 4 0</code>，"
                 "看 <code>cin &gt;&gt; int</code> 只吃下 <code>0</code>、把 <code>.5</code> 留在流里造成后续读入全部失效；"
                 "③ 各写一个 <code>addOne(int x)</code> 和 <code>addOneRef(int &amp;x)</code>，调用后打印 <code>a</code>，对比 0 与 1；"
                 "④ 在 <code>main</code> 里开 <code>int big[1000005]</code> 并赋值，看程序是否直接崩。",
                 "改一改：把三次 <code>dist</code> 收成 "
                 "<code>double perimeter(double ax, double ay, double bx, double by, double cx, double cy)</code>，"
                 "让 main 只剩两行。再想一步：要改成“返回最长的一条边”，需要几个引用参数？"))

# ---------------------------------------------------------------- 数学补给
M = MATH("递归式、等比数列与栈的真实上限", [
    P("把递归写成方程，就能在上机前判断够不够快。设 T(n) 是规模 n 的耗时："),
    P("<b>T(n) = T(n−1) + c</b>：每层只做常数工作，展开得 T(n) = cn = <b>O(n)</b>。阶乘递归、数组递归求和都属于这档。"),
    P("<b>T(n) = 2T(n−1) + c</b>：第 k 层有 2ᵏ 个调用，总数 2⁰+2¹+…+2ⁿ = 2ⁿ⁺¹ − 1 = <b>O(2ⁿ)</b>。"
      "朴素递归求斐波那契就是这样：f(40) 约 10⁸ 次调用，f(45) 约 2×10⁹ 次，必然 TLE。"),
    P("等比求和（q ≠ 1）：a₁ + a₁q + … + a₁q^(m−1) = a₁(qᵐ − 1)/(q − 1)。上面那个 2ⁿ⁺¹ − 1 就是 q = 2 的特例。"),
    P("处理 <b>f(n) = a·f(n−1) + b</b> 的通法是换元。以节末挑战题为例，逆向递推 f(d) = 2f(d+1) + 2，"
      "两边同加 2 得 f(d) + 2 = 2(f(d+1) + 2)。令 g(d) = f(d) + 2 就是纯等比，由 g(n) = 3 倒推 g(1) = 3·2ⁿ⁻¹，"
      "所以 <b>f(1) = 3·2ⁿ⁻¹ − 2</b>：n = 10 时 3×512 − 2 = 1534，与程序输出一致。"),
    P("栈的硬上限：Windows 默认 1 MB，Linux 默认 8 MB；一层栈帧通常 32~96 字节。"
      "于是递归深度上限约 <b>1 万层到 10 万层</b>——读到“n ≤ 10⁶ 还要递归”，就该改循环或手写栈了。"),
])

THINK = [
    "声明里可以只写类型不写形参名（<code>double dist(double, double);</code>），定义里必须写名字。为什么声明允许省略？省略了以后函数体里还能用这些参数吗？",
    "要让一个函数同时返回“最小值”和“它第一次出现的下标”，引用参数要几个？改成返回 <code>pair</code> 行不行？没找到时返回什么？",
    "为什么 <code>mySwap(int a, int b)</code> 什么都没干，而标准库的 <code>swap(a, b)</code> 有效？它的签名属于哪种传参？",
    "把 <code>sumOf(const int a[], int n)</code> 去掉 const，函数体里多了哪些可能？这会引入什么风险？",
    "一个只做一次加法的函数被调用 10⁵ 次，总开销大约是多少？和把这 10⁵ 次加法直接写在 main 里差多少？",
    "三个点共线时，“三角形周长”还有意义吗？题目为什么特意保证“不在同一条直线上”？",
]

CHECK = [
    "能用自己的话说清值传递与引用传递的区别，并各写一个 5 行以内的例子。",
    "知道为什么 <code>int sum(int a[])</code> 里 <code>sizeof(a)</code> 不等于数组字节数，以及正确做法。",
    "能把 main 里的三段重复逻辑抽成一个带返回值的函数，调用处只改三行。",
    "知道局部 <code>int a[1000000]</code> 为什么 RE，改成全局为什么就好了。",
    "能写出阶乘的递归版和循环版，并说出两个版本各自的代价。",
]

CHALLENGE = CH(
    "猴子吃桃", "P5743", "普及-", "https://www.luogu.com.cn/problem/P5743",
    [P("猴子第一天摘下若干桃子，当即吃了一半，还不过瘾，又多吃了一个。第二天早上又将剩下的吃掉一半，又多吃一个。"
       "以后每天早上都吃了前一天剩下的一半零一个。"),
     P("到第 n 天早上想再吃时，发现只剩下一个桃子了。求第一天共摘了多少个桃子。"),
     P("输入一个正整数 n（1 ≤ n ≤ 30）。输出一个整数，表示第一天摘的桃子数。")],
    hint=["别从第一天往后推——你不知道第一天有多少个。反过来，从第 n 天的 1 个往前倒推。",
          "设第 d 天早上有 f(d) 个。吃掉一半再多吃一个后剩下的是 f(d+1)，把它写成 f(d) 的表达式。",
          "写出反向公式后，既可以用一层循环从 n 倒着算到 1，也可以写成一个递归函数。"],
    idea=["第 d 天有 f(d) 个，吃掉一半再多吃一个，剩下 f(d) − f(d)/2 − 1 = f(d)/2 − 1，这个量就是 f(d+1)。",
          "所以 f(d+1) = f(d)/2 − 1，反解得 <b>f(d) = (f(d+1) + 1) × 2</b>。",
          "已知 f(n) = 1，用上式从 d = n−1 倒推到 d = 1，答案就是 f(1)。",
          "为什么对：每步都是等价代数变形，没丢解；f(d) 必为偶数，倒推结果一定是整数。",
          "写成函数 <code>int peach(int d)</code>：d == n 返回 1，否则返回 (peach(d+1)+1)*2 —— 这就是本节讲的递归雏形。"],
    code=r'''#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;

    // 从第 n 天早上的 1 个，倒推回第 1 天
    int cnt = 1;
    for (int d = n - 1; d >= 1; --d)
        cnt = (cnt + 1) * 2;      // f(d) = (f(d+1) + 1) * 2

    cout << cnt << "\n";
    return 0;
}''',
    explain=[
        ("int cnt = 1;", "初始值是第 n 天早上的桃子数，即已知的 1。cnt 表示“当前这一天的桃子数”。"),
        ("for (int d = n - 1; d >= 1; --d)", "从第 n−1 天倒推到第 1 天，共 n−1 步。n = 1 时一步不跑，直接输出 1，正合题意。"),
        ("cnt = (cnt + 1) * 2;", "把 f(d) = (f(d+1)+1)×2 翻成代码：先加 1 再乘 2，顺序不能反。"),
        ("cout << cnt << \"\\n\";", "此时 cnt 就是 f(1)，第一天摘的桃子数。"),
    ],
    pitfalls=["公式写反成 <code>cnt = cnt * 2 + 1</code>。这是另一条递推，不是“剩一半再多吃一个”的逆运算。",
              "循环写成 <code>for (int d = n; d &gt;= 1; --d)</code>，多推一步，答案变大。",
              "只看到 n ≤ 30 就用 int 存。n = 30 时答案是 3×2²⁹ − 2 ≈ 1.6×10⁹，已在 int 上限附近；"
              "题目一放宽就会溢出——看到“每天翻倍”就该想到 <code>long long</code>。",
              "把“第 n 天早上剩 1 个”读成“第 n 天吃完剩 1 个”，多算一天。读题要盯住“第几天早上”。"],
)

LESSONS = [LESSON(
    11, "函数：参数传递与返回值",
    "把重复逻辑收进函数：分清值传递与引用传递、知道数组传参为什么必须另传长度、"
    "搞清全局与局部变量的生存期与爆栈，并第一次见递归函数的出口与递推。",
    55, ["函数", "引用传递", "作用域"], "入门",
    SEC, math=M, think=THINK, check=CHECK, challenge=CHALLENGE,
    refs=["《算法竞赛入门笔记》第 4 章：函数、作用域与递归",
          "《算法竞赛黄金法则》：把重复的代码变成可调用的工具",
          "洛谷 P5735、P5743 题解区的高赞写法"],
)]
