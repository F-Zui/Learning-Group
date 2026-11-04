# -*- coding: utf-8 -*-
"""第 11 节 · 函数：参数传递与返回值"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dsl import *  # noqa

SEC = []

SEC.append(P("到现在为止，你所有代码都挤在 <code>main</code> 里。同一段逻辑出现第二次，就得整段复制——"
             "改要改两处，错就两处一起错。<b>函数是把一段逻辑装进一个名字里</b>："
             "参数决定喂它什么，返回值决定它交回什么，函数名替你记住“这段在干什么”。"))

SEC.append(P("求三角形周长时，三条边公式一模一样，只有坐标不同。不用函数，<code>sqrt(dx*dx+dy*dy)</code> 要抄三遍。"
             "先看 4 张推导卡，最后用一张算法落地卡把这道题从头做到尾。"))

# ---------------------------------------------------------------- 新语法
SEC.append(DERIVE(
    "同一段逻辑要写第二遍：怎么只写一次？",
    [P("三条边是同一个公式，只是喂进去的坐标不同。现在只能整段复制：改一处要改三处，错一处三处一起错。"),
     P("想给这段逻辑起个名字反复用，先得回答三个问题：结果怎么交回调用处、参数写在哪里、"
       "为什么把定义放在 <code>main</code> 后面会报 <code>area was not declared in this scope</code>。")],
    [
        ("先定“交回什么”：返回类型与 return",
         [P("函数开头写返回类型：算距离交回小数就写 <code>double</code>，判质数交回真假就写 <code>bool</code>，"
            "只做事、不出结果就写 <code>void</code>。函数体的骨架因此固定成下面这样。"),
          C("返回类型 函数名(形参表) {\n    ...\n    return 值;\n}", "函数定义骨架"),
          P("<code>return 值;</code> 做两件事：把结果交回调用处，并<b>立刻结束</b>这个函数——写在 return 后面的语句不再执行。")],
         [P("<code>double area(double w, double h)</code> 里写 <code>return w * h;</code>，调用处就把这个乘积当成整个表达式的值。"
            "返回类型写错成 <code>int</code> 时 12.5 会被截成 12，编译器不一定报错。")]),
        ("再定“喂什么”：形参表与实参",
         [P("形参是占位符，每个都要各自声明类型，不能写成 <code>(double x1, y1)</code>。调用时实参按<b>位置</b>一一抄进去。"),
          T(["组成部分", "含义 / 格式要求"], [
              ["返回类型", "结果是什么类型：算距离 <code>double</code>，判质数 <code>bool</code>，只做事不出结果 <code>void</code>。"],
              ["形参表", "占位符，每个参数各自声明，类型写全：<code>(double x1, double y1)</code>。"],
              ["return 值;", "把结果交回调用处，并立刻结束函数。"],
              ["调用", "实参按位置一一抄进形参，然后跳进函数体。"],
          ])],
         [P("<code>area(3, 4)</code> 里 3 抄给 <code>w</code>、4 抄给 <code>h</code>，函数体算 <code>3 * 4</code> 交回 12，"
            "所以 <code>cout &lt;&lt; area(3, 4)</code> 输出 12。顺序颠倒成 <code>area(4, 3)</code> 结果一样；"
            "但换成 <code>dist(x1, y1, x2, y2)</code> 这种同类型的四参数，位置一错答案就错。")]),
        ("最后跑一遍：声明在前、定义在后",
         [P("编译器从上往下读。定义写在 <code>main</code> 后面时，调用处还没见过这个名字，必须先给一张“名片”——前置声明。"),
          C(r'''double area(double w, double h);   // 前置声明：定义在 main 之后就靠它

int main() {
    cout << area(3, 4) << "\n";    // 实参 3、4 抄给形参 w、h → 12
    return 0;
}

double area(double w, double h) {  // 定义：真正实现
    return w * h;
}''', "示例")],
         [P("只写 <code>int main() { cout &lt;&lt; area(3, 4); }</code> 再写定义，编译报 "
            "<code>area was not declared in this scope</code>——报错指向调用行，容易被误认为函数名打错。加回第一行声明即可。")]),
    ],
    [P("固定的写法就一句：<b>返回类型 函数名(形参表) { ... return 值; }</b>，调用处写 <b>函数名(实参表)</b>。"
       "实参按位置一一抄进形参，<code>return</code> 把结果交回并立刻结束函数。"),
     WARN("两个容易忽略的前提", [
         "示例省略 <code>#include &lt;bits/stdc++.h&gt;</code> 与 <code>using namespace std;</code>，所有卡片同理。",
         "定义在 <code>main</code> 之后必须先声明，否则报 <code>area was not declared in this scope</code>；"
         "函数最多 <code>return</code> 一个值，要带出两个结果只能靠引用参数。",
     ])],
    cover="覆盖：函数定义 / 调用 / 返回类型 / 前置声明",
))

SEC.append(DERIVE(
    "在函数里把 a 加了 1，回来怎么还是 0？",
    [P("写一个 <code>addOne(a)</code> 想把 a 加一，函数里明明写了 <code>x += 1</code>，主函数打印出来却是 0。"
       "改动到底落在哪块内存上了？"),
     P("更难的是反过来的需求：一次要带出最小值、最大值两个结果，可 <code>return</code> 只交得回一个值。"
       "两条路——值传递与引用传递——决定了函数能不能改到调用者的变量。")],
    [
        ("默认方式：形参是实参的副本",
         [P("不写任何修饰时，调用会把实参的<b>值</b>拷一份给形参。两个变量占两块内存，互不相干。"),
          C(r'''void addOne(int x) { x += 1; }

int main() {
    int a = 0;
    addOne(a);
    cout << a << "\n";             // 0，不是 1
}''', "值传递：void f(int x)   // x 是实参的一份拷贝"),
          T(["写法", "含义"], [
              ["形参 int x", "调用时把实参的值拷一份进来，两个变量互不相干。"],
              ["改 x", "改的是副本。函数返回后副本销毁，实参一个字节都没变。"],
              ["代价", "传大对象要整体复制：10⁵ 个 int 的数组按值传进去，等于多拷 400 KB。"],
          ])],
         [P("上面这段程序输出 <b>0</b>。函数里 <code>x</code> 确实变成了 1，但那是副本，"
            "随函数返回一起销毁，<code>a</code> 从头到尾没被碰过。")]),
        ("要改本体：加一个 & 让形参变成别名",
         [P("在类型和变量名之间加一个 <code>&amp;</code>，形参就不再是副本，而是实参的<b>另一个名字</b>：读写它就是读写实参。"),
          C(r'''void addOne(int &x) { x += 1; }   // 只多了一个 &

int main() {
    int a = 0;
    addOne(a);
    cout << a << "\n";             // 1
}''', "引用参数：void f(int &x)   // x 是实参的另一个名字，不是副本"),
          T(["写法", "含义 / 要求"], [
              ["int &amp;x", "<code>&amp;</code> 写在类型后、变量名前。x 与实参是同一块内存的两个名字。"],
              ["读 / 写 x", "读写 x 就是读写实参，函数返回后实参真的变了。"],
              ["实参要求", "必须是能取地址的变量。传 <code>f(3)</code>、<code>f(a + b)</code> 直接编译错误。"],
          ])],
         [P("同一段 <code>int a = 0; addOne(a);</code> 这次输出 <b>1</b>。"
            "而 <code>addOne(3)</code> 编译不过：字面量没有地址，没法当别名。")]),
        ("选哪个：三条判据",
         [P("两种传参各有地盘，按“要不要改、对象大不大、类型小不小”三问选。"),
          T(["需求", "写法", "理由"], [
              ["要改调用者的变量", "<code>int &amp;x</code>", "引用传递，改的就是本体。"],
              ["只读的大对象", "<code>const string &amp;s</code>", "不复制、也不许改，下一张卡细讲。"],
              ["<code>int</code>、<code>double</code>、<code>char</code> 这类小类型", "直接按值传", "复制成本几乎为零，最省事。"],
          ]),
          P("同一条思路还能一次带出多个结果：<code>void getMinMax(int a[], int n, int &amp;mn, int &amp;mx)</code>，"
            "调用之后 <code>mn</code>、<code>mx</code> 都被写好，一次调用交回两个答案。")],
         [P("<code>mySwap(int a, int b)</code> 什么也没干；把签名换成 <code>mySwap(int &amp;a, int &amp;b)</code> 才真的交换。"
            "这也解释了标准库 <code>swap(a, b)</code> 为什么有效——它的两个形参都是引用。")]),
    ],
    [P("两条规则：<b>默认的值传递改不了实参</b>，形参只是一份副本；"
       "<b>要改调用者的变量、或要带出多个结果，就写 <code>类型 &amp;</code></b>，让形参成为实参的别名。"
       "小类型按值传最省事，大对象只读传参用 <code>const &amp;</code>。"),
     WARN("想改实参，只有两条路", [
         "写成引用参数 <code>类型 &amp;</code>；或者把新值 <code>return</code> 出来再赋回：<code>a = addOne(a);</code>。",
         "<code>int</code>、<code>double</code>、<code>char</code> 这类小类型，值传递最省事；"
         "而 <code>mySwap(int a, int b)</code> 这种忘了写 <code>&amp;</code> 的写法，函数里换得再认真，外面也不会变。",
     ])],
    cover="覆盖：值传递 / 引用参数 & / 多结果返回 / mySwap",
))

SEC.append(DIAG("compare", cap="同一段“把 a 加一”的代码，两种传参两种命运",
    left=("void addOne(int x) 值传递", [
        "x 是 a 的一份拷贝，改 x 不碰 a",
        "addOne(a) 之后 a 仍然是 0 → WA",
        "大对象整体复制：10⁵ 个 int 要多拷 400 KB"]),
    right=("void addOne(int &x) 引用传递", [
        "x 与 a 是同一块内存的两个名字",
        "addOne(a) 之后 a 变成 1",
        "带出多个结果的标准写法：getMinMax(a, n, mn, mx)"]),
    note="判据三条：要改调用者的变量写 int &；只读的大对象写 const string &；int、double、char 这类小类型直接按值传。"))

SEC.append(DERIVE(
    "大对象按值传要整串复制，可又不想让函数改它",
    [P("统计一个长字符串里某个字符的个数。按值传 <code>string s</code>，每次调用都先把整串复制一遍，"
       "长度 10⁶ 时就是每个字符都要搬一次；改成 <code>string &amp;s</code> 省了复制，"
       "但函数里一句 <code>s[0] = 'x'</code> 就能悄悄改坏调用者的数据，调用处完全看不出来。"),
     P("既要“不复制”，又要“不许改”，一个参数需要同时表达这两件事。")],
    [
        ("const：把“不修改”写成编译期承诺",
         [P("在参数类型前加 <code>const</code>，就是向编译器和读代码的人承诺：这个函数不修改这个参数。"
            "函数体里真去写 <code>s[0] = 'x'</code>，编译直接失败，不用等到运行时出错。"),
          P("承诺换来的是“调用处可以放心”：看到 <code>const</code> 就知道数据不会被改，重构、复用时不用逐行读函数体。")],
         [P("把 <code>countChar</code> 里的循环体加一句 <code>s[0] = 'x';</code>，g++ 报 "
            "<code>assignment of read-only reference 's'</code>。删掉 <code>const</code> 就编译通过——风险也随之回来了。")]),
        ("&：不复制，直接引用原对象",
         [P("<code>const T &amp;</code> 的两个部分各管一件事：<code>&amp;</code> 让它成为原对象的别名、省掉拷贝；"
            "<code>const</code> 保证它只读。两者合起来就是“只读的大对象”标准写法。"),
          T(["写法", "含义"], [
              ["const", "承诺函数内不修改参数。写 <code>s[0] = 'x'</code> 直接编译错误。"],
              ["&amp;", "不复制，直接引用原对象，省掉拷贝开销。"],
              ["用在哪", "参数是大对象（<code>string</code>、结构体、数组）且只读时，一律 <code>const T &amp;</code>。"],
          ])],
         [P("<code>countChar(&quot;banana&quot;, 'a')</code> 里字面量是个临时对象，<code>const &amp;</code> 能绑定它、"
            "普通 <code>&amp;</code> 绑不了；换成 <code>string s</code> 则会把 banana 整串复制一次。")]),
        ("落成签名：一个函数同时读、不写、不复制",
         [P("把两件事写进签名，函数体就能放心按只读方式遍历。"),
          C(r'''int countChar(const string &s, char c) {
    int cnt = 0;
    for (int i = 0; i < (int)s.size(); ++i)
        if (s[i] == c) ++cnt;      // 只读，符合 const 的承诺
    return cnt;
}
// countChar("banana", 'a') == 3''', "int countChar(const string &s, char c);")],
         [P("对 <code>&quot;banana&quot;</code> 数 <code>'a'</code> 得 3；函数里 <code>s</code> 与实参是同一块内存，"
            "一次复制都没发生，而且编译期就挡住了任何写操作。")]),
    ],
    [P("默认写法：<b>参数是大对象、函数又只读它，就写 <code>const T &amp;</code></b>——"
       "不复制、也不许改，两个需求一次满足。"),
     NOTE("tip", "小类型不要加 &", [
         "小类型不要加 <code>&amp;</code>：<code>const int &amp;x</code> 比 <code>int x</code> 还慢一点"
         "——引用本身要占一个指针的位置，绕一层反而多一次访存。",
     ])],
    cover="覆盖：const / 引用参数 / 大对象只读传参",
))

SEC.append(DERIVE(
    "n! 要乘 n 次：能不能让函数去算规模更小的自己？",
    [P("求 <code>n!</code> 用循环两行就写完了。但有类问题没有这样一条从头扫到尾的循环："
       "它的答案是“规模 n 的答案由规模 n−1 的答案再加工一次”得到的，比如阶乘、猴子吃桃、二叉树求深度。"),
     P("要写成一个函数，它得在自己内部调用自己。问题是：这样不会永远调下去吗？运算结果又该按什么类型接住？")],
    [
        ("先写出口：最小的规模直接给答案",
         [P("递归函数的第一件事不是递推，是<b>出口</b>：规模小到不用再拆时，直接返回答案。"
            "出口不写或永远不成立，函数会一直调用自己，把栈撑爆——症状是 RE，不是编译错误。"),
          C("long long fact(int n) {\n    if (n <= 1) return 1;           // 出口\n    return 1LL * n * fact(n - 1);   // 递推\n}", "long long fact(int n) 的骨架"),
          P("这里的出口是 <code>n &lt;= 1</code>：0! = 1! = 1，最小的两种规模都直接给答案。")],
         [P("<code>fact(1)</code> 命中出口返回 1，一次都不递归；<code>fact(0)</code> 同样返回 1。"
            "把 <code>if</code> 那一行删掉，<code>fact(5)</code> 会一路调到 <code>fact(-1)</code>、<code>fact(-2)</code>……最终爆栈 RE。")]),
        ("再写递推：把规模 n 化成规模 n−1 的同类问题",
         [P("递推行只做一件事：<code>n! = n × (n−1)!</code>。右边那个 <code>(n−1)!</code> 交给下一次调用，"
            "规模必须<b>严格变小</b>，才保证有限步后落到出口。"),
          C(r'''long long fact(int n) {
    if (n <= 1) return 1;
    return 1LL * n * fact(n - 1);
}
// fact(5) = 120, fact(20) = 2432902008176640000''', "示例")],
         [P("手算 <code>fact(5)</code> = 5 × <code>fact(4)</code> = 5 × 4 × <code>fact(3)</code> = … = 120；"
            "程序输出的每一层都和这个展开对得上。若把 <code>fact(n - 1)</code> 写成 <code>fact(n)</code>，规模不变，无限递归。")]),
        ("最后看代价：栈帧与 1LL",
         [P("每层调用都要在栈上留一份自己的局部变量和返回地址，这就是<b>栈帧</b>；函数返回时才释放。"
            "深度 × 每帧大小就是实际占用：5 层不到 1 KB，10⁵ 层就得按 MB 算。"),
          T(["组成部分", "含义"], [
              ["出口", "最小规模直接给答案。没有出口就是无限递归，必然 RE。"],
              ["递推", "把规模 n 化成规模 n−1 的同类问题，规模必须严格变小。"],
              ["栈帧", "每层调用都留一份自己的局部变量，返回时才释放。深度 × 每帧大小 = 实际占用。"],
              ["1LL *", "强制按 <code>long long</code> 相乘。20! = 2432902008176640000，早就超 int。"],
          ])],
         [P("<code>fact(20)</code> 输出 2432902008176640000；把 <code>1LL *</code> 去掉、返回类型改成 <code>int</code>，"
            "13! 之后就开始输出负数——32 位装不下。")]),
    ],
    [P("递归的两个必需品：<b>一个出口 + 一条让规模严格变小的递推</b>。每层调用占一份栈帧，"
       "深度乘以帧大小就是实际内存；要乘出大数就先写 <code>1LL *</code> 把运算提到 64 位。"),
     NOTE("tip", "本节的立场", [
         "本节的立场：<b>先会读递归，再决定用不用</b>。递归深度一般别超过 10⁵ 层。",
         "栈的真实上限见本节数学补给：Windows 默认 1 MB，Linux 默认 8 MB，一层栈帧通常 32~96 字节。",
     ])],
    cover="覆盖：递归 / 出口 / 递推 / 栈帧 / 1LL 溢出",
))

SEC.append(DIAG("steps", cap="fact(5) 的 5 层压栈与 4 次回填", items=[
    "fact(5)：n = 5 > 1，要先等 fact(4) 的结果",
    "fact(4) 等 fact(3)，fact(3) 等 fact(2)，fact(2) 等 fact(1)",
    "fact(1)：n ≤ 1，直接 return 1 —— 这就是出口，不再往下压栈",
    "回填：fact(2) = 2×1 = 2，fact(3) = 3×2 = 6",
    "fact(4) = 4×6 = 24，fact(5) = 5×24 = 120",
    "每层栈帧约 32~96 字节，5 层不到 0.5 KB；深度到 10⁵ 层就得按 MB 算了",
]))

# ---------------------------------------------------------------- 例题
SEC.append(WALK(
    "一条边的公式，调用三次",
    [P('例题 · 距离函数 · <a href="https://www.luogu.com.cn/problem/P5735" target="_blank" rel="noopener">洛谷 P5735</a> <span class="badge diff">入门</span>'),
     P("给出平面直角坐标系上不在同一条直线上的三个点 A、B、C 的坐标，求三角形 ABC 的周长。"),
     P("输入三行，每行两个实数，表示一个点的横、纵坐标（允许是小数）。"),
     P("输出一行一个实数，为三角形周长，保留两位小数。"),
     C("输入：\n0 0\n0 3\n4 0\n输出：\n12.00", "样例")],
    [
        ("把“求一条边”抽成只依赖 4 个形参的纯函数",
         [C(r'''// 只依赖 4 个形参，不碰任何全局状态，好测、可复用
double dist(double x1, double y1, double x2, double y2) {
    double dx = x1 - x2;
    double dy = y1 - y2;
    return sqrt(dx * dx + dy * dy);       // 勾股定理
}''', "dist：一条边的长度")],
         [P("返回 <code>double</code>：距离带小数，不能收成 <code>int</code>。4 个形参的顺序必须和调用时完全一致。"
            "<code>dx</code>、<code>dy</code> 是 <code>dist</code> 的局部变量，出了函数就销毁，和 <code>main</code> 里的同名变量互不干扰。"
            "<code>sqrt</code> 的参数与返回值都是 <code>double</code>，与返回类型一致，不做隐式转换。")]),
        ("读入六个实数",
         [C("    double ax, ay, bx, by, cx, cy;\n    cin >> ax >> ay >> bx >> by >> cx >> cy;", "读入")],
         [P("六个实数一次读完。<code>cin</code> 自动跳过换行与空格，所以输入分三行也正确；"
            "但如果把变量写成 <code>int</code>，<code>cin</code> 吃下整数部分后会把 <code>.5</code> 留在流里，后续读入全部失效。")]),
        ("三次调用：同一个公式，只换坐标",
         [C("    double ans = dist(ax, ay, bx, by)\n               + dist(bx, by, cx, cy)\n               + dist(cx, cy, ax, ay);", "三条边相加")],
         [P("三次独立调用：每次把新实参抄进形参，第一次的局部变量早已销毁，互不影响。"
            "这也是把公式抽成函数最大的好处——只需验算一个函数，不用管整段程序。")]),
        ("按题目要求输出两位小数",
         [C('    cout << fixed << setprecision(2) << ans << "\\n";   // fixed 才表示"小数位数"', "输出")],
         [P("<code>fixed</code> 才表示“小数点后几位”。只写 <code>setprecision(2)</code> 是“总共两位有效数字”，"
            "会输出 12 而不是 12.00；两者合用才稳定得到 12.00。")]),
        ("完整程序",
         [C(r'''#include <bits/stdc++.h>
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
}''', "完整代码")],
         [P("这份程序可以直接提交：<code>#include</code> 与 <code>int main</code> 都在，构建脚本会拿它做编译自检。"
            "样例输入 0 0 / 0 3 / 4 0 时，三条边是 3、5、4，输出 12.00。")]),
    ],
    [P("题型特征：同一段计算出现两次以上、又只依赖参数——抽成函数。看到“保留 k 位小数”，先想 <code>fixed</code>。"),
     P("复杂度：三次 <code>sqrt</code>，与输入规模无关，O(1)；真正的耗时只花在输入输出上。"),
     L(["<b>坑</b>：<code>dist</code> 的形参顺序与调用不一致时，同类型参数不会报错，答案却整片错。",
        "<b>坑</b>：只写 <code>setprecision(2)</code> 忘了 <code>fixed</code>，样例就挂。",
        "<b>坑</b>：把坐标读成 <code>int</code>，小数输入会让后续读入全部失效。"])],
    cover="覆盖：洛谷 P5735 / 函数封装与值传递",
    tags=["模型：纯函数封装", "O(1)", "坑：fixed 与 setprecision"],
))

SEC.append(DIAG("flow", cap="P5735：dist 被调用三次，实参 → 形参 → 返回值", items=[
    "main 读入 ax=0 ay=0 bx=0 by=3 cx=4 cy=0",
    {"c": "double dist(ax, ay, bx, by);", "t": "实参按位置抄进形参：x1=0, y1=0, x2=0, y2=3"},
    {"c": "double dx = x1 - x2; double dy = y1 - y2;", "t": "dx = 0、dy = −3；都是 dist 的局部变量，出函数即销毁"},
    {"c": "return sqrt(dx * dx + dy * dy);", "t": "sqrt(0 + 9) = 3.0，交回调用处"},
    {"q": "三条边都算完了吗？", "yes": "ans = 3 + 5 + 4 = 12.00，转去输出", "no": "换下一对坐标，再调一次 dist"},
    {"c": "cout << fixed << setprecision(2) << ans;", "t": "fixed 表示“小数点后 2 位”，输出 12.00 而不是 12"},
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

SEC.append(DIAG("array", cap="把 x[5] = {3, 1, 4, 1, 5} 传进 sumOf：长度在传参路上就丢了", cells=[
    "3", "1", "4", "1", "5"], idx=True, hl=[0],
    note="函数里的 a 已退化成 int*：sizeof(a) = 8（指针），不是 20；sizeof(a)/sizeof(a[0]) = 2，循环只跑 2 次 → 答案是 4 而不是 14。长度必须另传 n = 5。"))

SEC.append(AFTER("作用域与爆栈：变量放在哪，决定它能活多久", [
    T(["写在哪", "叫什么", "初值", "活到什么时候", "内存区"], [
        ["函数或 <code>{}</code> 内", "局部变量", "随机值（垃圾）", "出了这层花括号就销毁", "栈，约 1~8 MB"],
        ["所有函数之外", "全局变量", "自动为 0", "整个程序运行期间", "静态区，可用几百 MB"],
    ]),
    P("结论很硬：<code>int a[1000005]</code> 占 4 MB，写在 <code>main</code> 里会栈溢出（本地可能还能跑，评测机 RE）；"
      "写到所有函数外面就没事，还自动清零。<b>数组长度超过 10⁵ 就放全局</b>。"),
    P("但全局变量谁都能改，出了问题极难定位。所以只有“很大的数组”和“全程序共享的表”才放全局，能用参数传的一律用参数。"),
]))

SEC.append(DIAG("tree", cap="int a[1000005]（约 4 MB）写在哪，决定它是 AC 还是 RE", root={
    "t": "int a[1000005] 的位置", "kids": [
        {"t": "写在 main 里 → 局部变量、栈区、Windows 默认 1 MB / Linux 8 MB → 栈溢出 RE（本机有时还能跑）"},
        {"t": "写在所有函数之外 → 全局变量、静态区 → 不占栈，还自动清零，连 memset 都省了"},
    ]},
    note="经验线：元素数超过 10⁵ 的数组一律放全局。全程序共享的常量表也放全局，其余能传参就传参。"))

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

THINK_A = [
    "因为声明只是给编译器一张名片：函数名、返回类型、参数类型；调用处靠它做类型检查和重载决议，形参名根本不参与函数签名，所以可以省。"
    "定义里有函数体，函数体要用形参，所以定义必须写名字；省了名字的函数体里就用不了这些参数，编译器会报 parameter name omitted。<br>"
    "常见错路是以为声明和定义的形参名必须一致——不必，但强烈建议一致，否则读代码的人要在两处之间来回对照。",

    "要两个引用参数：<code>void getMin(const int a[], int n, int &amp;mn, int &amp;mnPos)</code>，一个带回最小值，一个带回它的下标。"
    "返回 <code>pair&lt;int,int&gt;</code> 也行（C++11 起更常见），语义更清楚，但取值要写 first / second；返回一个结构体同样可以。<br>"
    "“没找到”必须提前约定：本题 n ≥ 1 必有最小值，所以不会没找到；真要表达没找到，就把位置初始化为 −1、值用 INT_MAX，调用方先看位置。"
    "常见错路是只加一个引用参数却想带回两个结果，或者忘了写 &amp;，函数里改得再认真，外面拿到的还是原值。",

    "因为 <code>mySwap(int a, int b)</code> 的形参是副本，它交换的是两个副本，函数一返回副本就销毁，实参一个字节都没动；"
    "<code>std::swap</code> 的签名是 <code>template&lt;class T&gt; void swap(T &amp;a, T &amp;b)</code>，两个<b>引用</b>参数，交换的就是实参本身，属于引用传递。<br>"
    "常见错路是以为“在函数里换了外面就换了”，或者只给一个参数加 &amp;——那样只换得动一个，另一个还是副本。",

    "去掉 const 之后，函数体里就能写 <code>a[i] = ...</code>、<code>a[0] = 0</code>，编译器不再替你拦下来。"
    "风险是调用者传进来的数组被静默改坏：调用处完全看不出这个函数会写数据，重构或复用时就会踩雷；如果传进来的是常量数组或字符串字面量，还可能直接编译不过。<br>"
    "常见错路是以为 const 只是“写给人的注释”——它其实是让编译器帮你抓写入的开关，也是“这个函数只读”的机器可验证承诺。",

    "每次调用有压栈、跳转、返回的开销，量级是几条到十几条指令；10⁵ 次大约是 10⁵~10⁶ 条指令，占 1 秒预算（10⁸ 次操作）最多也就百分之一。"
    "现代编译器在 -O2 下还会把这种小函数内联，开销接近 0。<br>"
    "真正要担心的是递归的<b>栈深度</b>（10⁶ 层会爆栈），不是“调用次数”。常见错路是听说“函数调用有开销”就把所有逻辑塞回 main，"
    "结果同一段代码抄三遍、改一处漏一处——省下的那点常数远不如多一个 bug 贵。",

    "共线时三点不构成三角形，“周长”退化成 A→B→C→A 的折返路程：若 B 在 A、C 之间，AB + BC + CA = 2AC，公式照样算得出一个数，"
    "但那个数不是任何三角形的周长。题目保证不共线，是为了让“三角形”这个说法成立、答案唯一，也避免退化情形下的判题歧义。<br>"
    "常见错路是以为共线会让程序崩——不会，sqrt 照算、输出照出，只是答案没有几何意义；真正会出问题的是输入里出现重合点（边长为 0）时某些公式里的除法。",
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
    SEC, math=M, think=THINK, think_a=THINK_A, check=CHECK, challenge=CHALLENGE,
    refs=["《算法竞赛入门笔记》第 4 章：函数、作用域与递归",
          "《算法竞赛黄金法则》：把重复的代码变成可调用的工具",
          "洛谷 P5735、P5743 题解区的高赞写法"],
)]
