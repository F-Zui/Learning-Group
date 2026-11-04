# -*- coding: utf-8 -*-
"""第 12 节 · 结构体与多关键字排序"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dsl import *  # noqa

SEC = []

SEC.append(P("前 11 节里，一个数组只装一种东西：全是成绩，或全是坐标。可真实题目里，一个学生同时有学号、语文、数学、英语、总分，"
             "而且要求<b>按总分排、总分相同看语文、还相同看学号</b>。裸数组排不动这种题——学号一个数组、总分一个数组，一排序就对不上号。"
             "<b>结构体把多个字段打包成一个整体</b>，排序时整包一起搬，字段之间的对应关系才不会散。"))

# ---------------------------------------------------------------- 新语法
SEC.append(DERIVE(
    "一个学生五个字段：排序时怎么不散架？",
    [P("一个学生同时有学号、语文、数学、英语、总分。若把它们分别存进五个数组，<code>sort</code> 只搬得动其中一个，"
       "排完总分，学号还在原地——整张表就对不上人了。"),
     P("手写交换五个数组？漏搬一个就前功尽弃。需要的是一个新类型：把五个字段打成一个整体，排序时整包搬走。")],
    [
        ("先声明一个新类型",
         [P("<code>struct</code> 后面跟名字、一对花括号、里面是普通变量声明，最后是一个<b>不能漏的分号</b>。"),
          C("struct 名字 {\n    类型 字段1;\n    类型 字段2;\n};          // ← 这个分号不能漏", "struct 的标准形状")],
         [P("漏掉那个分号，编译器会在<b>下一个函数</b>处报 <code>expected ';' before ...</code>，"
            "报错行号离真正的坑差几十行——这是最常见的“看一眼就知道”的错误。")]),
        ("字段就是普通变量声明",
         [P("字段可以是 <code>int</code>、<code>double</code>、<code>string</code>，甚至数组；声明方式与你在函数里写局部变量完全一样。"
            "名字习惯首字母大写：<code>Stu</code>、<code>Node</code>。"),
          T(["组成部分", "含义 / 格式要求"], [
              ["struct", "声明一个新类型。字段就是普通变量声明，可以是 <code>int</code>、<code>double</code>、<code>string</code>，甚至数组。"],
              ["名字", "习惯首字母大写：<code>Stu</code>、<code>Node</code>。用法和 <code>int</code> 一样：<code>Stu a;</code>、<code>Stu s[305];</code>。"],
              ["结尾 ;", "必须有。漏了会让后面几十行一起报 <code>expected ';'</code>，错误行号离真正的坑很远。"],
          ])],
         [P("<code>Stu s[305]</code> 一次开出 305 个学生，<code>s[i].id</code> 取第 i 个的学号；"
            "每个元素都和 <code>int</code> 数组的元素一样按顺序排布。")]),
        ("像 int 一样定义、赋值、访问",
         [C(r'''struct Stu {
    int id;
    int sum;
};                             // 分号不能漏

int main() {
    Stu a;                     // 像 int 一样定义变量
    a.id = 1;  a.sum = 265;
    Stu s[3];                  // s[0]、s[1]、s[2] 各是一个学生
    s[1].sum = 244;
    cout << a.id << " " << s[1].sum << "\n";
}''', "示例")],
         [P("这段输出 <code>1 244</code>。字段用点号访问，和结构体变量本身一样是普通左值——"
            "可以读、可以写，也可以整个结构体赋值。但要注意：局部结构体变量<b>不会自动初始化</b>，"
            "<code>Stu a;</code> 之后 <code>a.sum</code> 是随机值，读之前必须先写。")]),
    ],
    [P("<b>struct 名字 { 类型 字段; ... };</b> 就是一个新类型，用法和 <code>int</code> 完全平行——"
       "定义变量、开数组、整体赋值、用点号访问字段。排序时它整包搬动，字段之间的对应关系不会散。"),
     WARN("两条硬规矩", [
         "结构体定义结尾的 <code>};</code> 分号不能漏，漏了会让后面几十行一起报 <code>expected ';'</code>。",
         "局部结构体变量<b>不会自动初始化</b>：<code>Stu a;</code> 之后 <code>a.sum</code> 是随机值，读之前必须先写。",
     ])],
    cover="覆盖：struct 定义 / 字段 / 结构体数组 / 初始化",
    think=[
        ("把 <code>struct</code> 换成 <code>pair&lt;int,int&gt;</code>，两关键字排序怎么写？三关键字呢？什么时候该退回 struct？",
         "<code>pair&lt;int,int&gt;</code> 两关键字直接 <code>sort(v.begin(), v.end())</code> 就是按 first、再按 second 升序；要混合方向就传 lambda："
         "<code>[](const pair&lt;int,int&gt; &amp;a, const pair&lt;int,int&gt; &amp;b) { return a.first != b.first ? a.first &gt; b.first : a.second &lt; b.second; }</code>。"
         "三关键字 pair 就不够了，得用 <code>tuple</code>（配 tie 比较）或者退回 struct。<br>"
         "什么时候退回 struct：字段超过两个、字段有名字（id / sum / ch 比 first / second 好读）、要带 string 或数组字段、比较规则要在多处复用。"
         "常见错路是硬用 pair 套 pair（<code>pair&lt;int, pair&lt;int,int&gt;&gt;</code>），可读性立刻崩掉。"),
    ],
))

SEC.append(DIAG("matrix", cap="Stu 数组就是一张 6 行 × 4 列的表：sort 搬的是整行",
    head_row=["语文", "数学", "英语", "总分"], head_col=["1", "2", "3", "4", "5", "6"],
    rows=[["90", "67", "80", "237"],
          ["87", "66", "91", "244"],
          ["78", "89", "91", "258"],
          ["88", "99", "77", "264"],
          ["67", "89", "64", "220"],
          ["78", "89", "98", "265"]],
    hl=[(5, 3)],
    note="行号就是学号（输入顺序）。学号 6 的 78 + 89 + 98 = 265，正是样例第一名；排序时这 4 个字段一起移动，id 不会和 sum 错位。"))

SEC.append(DERIVE(
    "排 a[0..n−1]：第二个参数到底写 a+n 还是 a+n−1？",
    [P("要排一个数组，<code>sort</code> 却不要“长度”，要两个指针。多写一个 <code>-1</code>，最后一个元素就不参与排序，"
       "症状是“答案总是差一名”的 WA，样例还可能刚好过。"),
     P("另一个方向的困难：题目要降序。难道还得手写一个比较函数？")],
    [
        ("先看区间：左闭右开",
         [P("<code>sort</code> 的第一个参数是首指针，第二个是<b>尾后指针</b>——最后一个元素的下一个位置。"
            "所以排 <code>a[0..n−1]</code>，第二个参数写 <code>a + n</code>，正好不包含 <code>a[n]</code>。"),
          C("sort(首指针, 尾后指针);              // 默认升序\nsort(首指针, 尾后指针, 比较器);      // 自定义顺序", "两种签名"),
          T(["参数", "含义"], [
              ["首指针", "第一个元素的地址：<code>a</code>。"],
              ["尾后指针", "最后一个元素<b>下一个</b>位置的地址。排 a[0..n−1] 就写 <code>a + n</code>。"],
              ["比较器", "省略时按 <code>&lt;</code> 升序；结构体数组必须自己传。"],
              ["复杂度", "O(n log n)。n = 10⁶ 约 2×10⁷ 次比较，1 秒内跑完。"],
          ])],
         [P("<code>sort(a, a + 6)</code> 排 6 个；<code>sort(a, a + 6 - 1)</code> 只排 5 个，<code>a[5]</code> 原地不动。"
            "1 下标数组写成 <code>sort(a + 1, a + n + 1)</code>，末尾是 <code>+ n + 1</code>，不是 <code>+ n</code>。")]),
        ("看清三种常用形态",
         [C(r'''int main() {
    int a[6] = {5, 2, 8, 1, 9, 3};
    sort(a, a + 6);                  // 排 a[0..5] → 1 2 3 5 8 9
    sort(a, a + 3);                  // 只排前 3 个
    sort(a, a + 6, greater<int>());  // 降序 → 9 8 5 3 2 1

    int b[6] = {5, 2, 8, 1, 9, 3};
    sort(b + 1, b + 6);              // 1 下标：排 b[1..5]，b[0] 不动
}''', "同一份数据，四种区间")],
         [P("<code>sort(a, a + 3)</code> 之后前三个变成 2 5 8，后三个仍是 1 9 3 的原顺序——"
            "区间右端不包含在排序范围里，这件事每个用例都能看出来。")]),
        ("要降序就用 greater<类型>()",
         [P("<code>greater&lt;int&gt;</code> 是标准库自带的比较器，含义是“大的排在前面”。它是个<b>类型</b>，"
            "而 <code>sort</code> 的第三个参数要一个<b>值</b>，所以末尾那对圆括号是在构造对象，不能漏。"),
          C("sort(a, a + n, greater<类型>());", "签名"),
          C(r'''int main() {
    int a[5] = {3, 1, 4, 1, 5};
    sort(a, a + 5, greater<int>());       // 5 4 3 1 1
}''', "降序一行"),
          T(["写法", "含义"], [
              ["&lt;类型&gt;", "尖括号里写元素类型，必须和数组元素类型一致。"],
              ["末尾 ()", "这对圆括号是“构造一个对象”。漏了就语法错误：<code>greater&lt;int&gt;</code> 只是类型，类型不能当值传。"],
              ["等价", "<code>greater&lt;int&gt;()</code> 等价于 <code>[](int x, int y) { return x &gt; y; }</code>。"],
          ])],
         [P("<code>sort(a, a + 5, greater&lt;int&gt;)</code> 编译报错，提示 <code>expected primary-expression</code>；"
            "补上 <code>()</code> 输出 5 4 3 1 1。同族的 <code>less&lt;int&gt;()</code> 就是 <code>&lt;</code>，"
            "也正是 sort 省略比较器时的默认行为。")]),
    ],
    [P("<b>sort(首指针, 尾后指针)</b> 排左闭右开区间，默认升序；<b>sort(首, 尾后, greater&lt;类型&gt;())</b> 降序。"
       "右端点写 <code>a + n</code>，写成 <code>a + n - 1</code> 就漏掉最后一个元素。"),
     WARN("两个最常见的差一位", [
         "<code>sort(a, a + n - 1)</code> 只排了 n−1 个，最后一个不参与——最常见的差一位。",
         "1 下标数组写成 <code>sort(a + 1, a + n + 1)</code>，末尾是 <code>+ n + 1</code>，别抄成 <code>+ n</code>。",
     ])],
    cover="覆盖：sort 区间 / greater 降序 / 复杂度",
))

SEC.append(DERIVE(
    "规则有三层：怎么告诉 sort 谁排前面？",
    [P("奖学金按“总分降序 → 语文降序 → 学号升序”排。三个条件一起说才完整，可 <code>sort</code> 只会比较两个元素，"
       "它需要你回答一个更小的问题：<b>a 和 b 两个人，谁该排在前面？</b>"),
     P("回答这个问题的函数，返回值该是什么？哪些写法会让 <code>sort</code> 直接崩？只在一个地方用的规则，"
       "还要专门起个全局函数名吗？")],
    [
        ("先定返回值：只回答“a 该不该在前”",
         [P("比较器返回 <code>bool</code>：<code>true</code> 表示 a 排在 b 前面。它不是返回差值，也不是返回“谁更小”，"
            "而是<b>优先级</b>。参数用 <code>const T &amp;</code>：按引用传、避免每个元素整包复制，"
            "<code>const</code> 保证比较时不改数据。"),
          C("bool cmp(const T &a, const T &b) {\n    return a.键 < b.键;      // 返回 true ⇒ a 排在 b 前面\n}", "比较器签名"),
          T(["组成部分", "含义"], [
              ["返回值", "<code>bool</code>，只回答“a 该不该排在 b 前面”，不是返回差值，也不是返回“a 更小”。"],
              ["const T &amp;", "按引用传，避免每个元素被整包复制；<code>const</code> 保证比较时不改数据。"],
              ["运算符", "只写严格不等 <code>&lt;</code> 或 <code>&gt;</code>，<b>绝不能写 <code>&lt;=</code>、<code>&gt;=</code></b>。"],
              ["严格弱序", "<code>cmp(a,a)</code> 必须为 false；<code>cmp(a,b)</code> 与 <code>cmp(b,a)</code> 不能同时为 true；必须可传递。"],
          ])],
         [P("<code>cmpBig(a,b) { return a &gt; b; }</code> 让大的在前，是降序；换成 <code>a &lt; b</code> 就是升序。"
            "同一个不等式，方向换一下就是另一个算法。")]),
        ("再看严格弱序：为什么绝不能用 >=",
         [P("<code>std::sort</code> 的分区循环只依赖三条假设：<code>cmp(a,a)</code> 为 false；<code>cmp(a,b)</code> 与 "
            "<code>cmp(b,a)</code> 不同时为 true；可传递。写成 <code>&gt;=</code> 就破坏了第一条。"),
          C(r'''bool cmpBig(int a, int b) { return a > b; }   // 降序：大的在前
bool bad(int a, int b) { return a >= b; }     // cmp(a,a) 竟返回 true

int main() {
    int a[5] = {3, 1, 4, 1, 5};
    sort(a, a + 5, cmpBig);                   // 5 4 3 1 1
    sort(a, a + 5, bad);                      // 可能直接 RE
}''', "同一份数据，两种比较器两种命运")],
         [P("<code>bad(3, 3)</code> 返回 <code>true</code>——“等于 pivot 也算小”，分区指针停不下来，"
            "会一路越过数组末尾写内存。症状是 <b>RE</b> 而不是编译错误；换成 <code>&gt;</code> 之后立刻恢复正常。")]),
        ("不想另起名字：lambda 就地写",
         [P("只在一个 <code>sort</code> 里用一次的规则，不必在全局占一个名字。lambda 直接写在第三个参数的位置："
            "<code>[]</code> 是捕获列表（空表示不用外部变量，<code>[&amp;]</code> 表示按引用用外部变量），"
            "后面跟参数列表与函数体，整个 lambda 写完再用 <code>);</code> 收尾。"),
          C("sort(a, a + n, [](const T &x, const T &y) { return 条件; });", "lambda 的位置"),
          T(["组成部分", "含义"], [
              ["[]", "捕获列表：空表示不用外部变量；<code>[&amp;]</code> 表示按引用用外部变量。"],
              ["(参数)", "和普通函数形参一样，写 <code>const T &amp;</code> 最省。"],
              ["位置", "就地写在 <code>sort</code> 第三个参数处，不必在全局另起一个函数；整个 lambda 后用 <code>)</code> 和 <code>;</code> 收尾。"],
          ]),
          C(r'''struct Stu { int id, sum; };

int main() {
    Stu s[3] = {{1, 240}, {2, 265}, {3, 240}};
    sort(s, s + 3, [](const Stu &x, const Stu &y) {
        if (x.sum != y.sum) return x.sum > y.sum;   // 总分降序
        return x.id < y.id;                         // 学号升序兜底
    });
}''', "带兜底的多关键字 lambda")],
         [P("这段把 {1,240}、{2,265}、{3,240} 排成 265、240（学号 1）、240（学号 3）——"
            "总分相同时靠第二行 <code>x.id &lt; y.id</code> 分出先后，这正是“严格弱序”在代码里的样子。")]),
    ],
    [P("<b>比较器是一个返回 bool 的函数</b>，回答“a 是否该排在 b 前面”；参数写 <code>const T &amp;</code>，"
       "运算符只能用严格不等号。只在一个地方用的规则，用 lambda 就地写，不必另起名字。"),
     WARN("两条不能碰的线", [
         "只用 <code>&lt;</code> 或 <code>&gt;</code>；写 <code>&gt;=</code> 时 <code>cmp(a,a)</code> 返回 true，"
         "<code>std::sort</code> 可能越界写内存，症状是 RE 或随机 WA。",
         "lambda 里不能修改未被捕获的外部变量，编译会直接报错；只在一个排序里用的比较器，lambda 比全局函数更清楚。",
     ])],
    cover="覆盖：cmp 比较器 / 严格弱序 / lambda",
    think=[
        ("两个人总分、语文都相同时，cmp 最后写 <code>a.id &lt; b.id;</code> 与写 <code>return false;</code> 有什么区别？后者破坏了哪条公理？",
         "写 <code>a.id &lt; b.id</code>：这两人有了确定次序（学号小的在前），cmp(a,b) 与 cmp(b,a) 恰有一个为 true，任意两人都可比，结果可复现。"
         "写 <code>return false</code>：两个方向都返回 false，等于宣布“这两人等价”——严格说它并不违反那三条公理（非自反、非对称、传递都还成立，等价类本身是合法的），"
         "丢掉的是<b>全序</b>：他们不再有确定先后，而 sort 不稳定，最终顺序由实现和分区过程决定，同一份代码换个数据规模就可能变；"
         "正文说“严格弱序被破坏”，指的后果就是这个不可复现。真正会破坏非自反的是写 <code>&gt;=</code>，那个会让 sort 越界，症状是 RE。<br>"
         "常见错路是拿样例“恰好没变”来证明自己没问题。"),
        ("只按总分排序、不加学号兜底时，两个 250 分的同学谁在前？这个答案由什么决定？为什么不能指望它？",
         "不确定，谁在前由 sort 的实现决定：它不稳定，两个“等价”元素在分区、交换过程中谁先谁后没有保证，跟你输入的先后也没有必然关系。"
         "所以这次跑 A 在前、下次数据量一变可能就 B 在前——不能指望，也不能拿样例“恰好对”当证据。<br>"
         "常见错路是只写总分一个关键字就提交，本地样例又刚好没有并列，于是以为对了；正解是加一个唯一键兜底（学号或输入下标）。"),
    ],
))

SEC.append(DERIVE(
    "三个关键字不想写三层 if：有没有更笨但更稳的办法？",
    [P("cmp 里写三层 <code>if</code> 能过，但关键字再多几层、优先级再调一次，这函数就没人看得懂了；"
       "写反一个不等号，整题全错。"),
     P("能不能让每一趟只比较一个键，把“优先级”交给排序的<b>顺序</b>去表达？这要求排序能保住上一趟的结果——"
       "而 <code>sort</code> 恰好不保证这件事。")],
    [
        ("先要一个“稳定”的排序",
         [P("<b>稳定</b>的意思是：比较器认为等价的两个元素，排序后仍按原来的先后排列。<code>sort</code> 不保证这一点，"
            "<code>stable_sort</code> 保证。"),
          C("stable_sort(首, 尾后, 比较器);     // 认为“相等”的元素保持原有先后", "签名"),
          T(["性质", "含义"], [
              ["稳定", "比较器认为等价的两个元素，排序后仍按原来的顺序排列；<code>sort</code> 不保证这一点。"],
              ["用法", "多关键字：<b>从最次要的键排到最重要的键</b>，每趟都用 <code>stable_sort</code>。"],
              ["代价", "多花 O(n) 内存，常数略大；n ≤ 10⁵ 完全够用。"],
          ])],
         [P("三个学生总分都是 240、输入顺序是 1、2、3。先用 <code>sort</code> 按学号排、再用 <code>stable_sort</code> "
            "按总分排，输出仍是 1、2、3——上一趟的次序被完整保留了下来。")]),
        ("从最次要的键排到最重要的键",
         [P("先按学号（最次要、且唯一）排一趟，再按语文排，最后按总分排。每一趟都把上一趟的结果当作“相等的默认顺序”，"
            "于是主要键相同的人，自动保持次要键的次序。"),
          C(r'''// 假设已有例题里的 Stu s[] 与 n：目标 总分降序 → 语文降序 → 学号升序
sort(s, s + n, [](const Stu &a, const Stu &b) { return a.id < b.id; });
stable_sort(s, s + n, [](const Stu &a, const Stu &b) { return a.ch > b.ch; });
stable_sort(s, s + n, [](const Stu &a, const Stu &b) { return a.sum > b.sum; });''', "三趟 stable_sort")],
         [P("样例 6 个学生跑完三趟，输出与一次 cmp 的三层 if 逐字节相同——"
            "两种写法的差别只在“哪种更不容易写反优先级”。")]),
        ("反过来排就前功尽弃",
         [P("如果先排主键（总分）、再排次键（语文），最后一趟会把总分相同的次序重新打乱，等于前面的工作全白做。"),
          P("所以顺序只有一个方向：<b>最次要 → 最重要</b>。第一趟按唯一键（如学号）排时，用 <code>sort</code> 也不会错，"
            "因为根本没有并列。")],
         [P("把上面三行倒过来（先 sum、再 ch、最后 id），语文不同但总分相同的学生就会被学号顺序覆盖，"
            "输出与题目要求不符。")]),
    ],
    [P("<b>stable_sort 保证等价元素保持原有先后</b>；多关键字排序就“从最次要的键排到最重要的键”，"
       "每趟只写一个不等式。代价是多花 O(n) 内存序，n ≤ 10⁵ 完全够用。"),
     WARN("顺序只有一个方向", [
         "顺序必须从次要到主要。反过来先排主键，后面几趟会把主键重新打乱。",
         "第一趟按唯一键（如学号）排，用 <code>sort</code> 也不会错，因为根本没有并列。",
     ])],
    cover="覆盖：stable_sort / 稳定排序 / 多关键字分层",
    think=[
        ("字段有 6 个关键字时，你写 6 层 if 还是逐层 stable_sort？两种写法各要多少次比较、几趟排序？",
         "关键字少（2~3 个）时写多层 if 更划算：一次 sort 是 O(n log n) 次比较，每次最多 6 次字段比较，总计约 6·n log n 次字段访问。"
         "关键字多、优先级容易写错时改用逐层 stable_sort：从最次要的键排到最重要的键，6 个键就是 6 趟，每趟 O(n log n) 次比较、每次只比一个字段，比较总次数同量级，"
         "但要多花 O(n) 内存、常数乘 6。<br>所以选的依据不是“快”，而是“哪种更不容易把优先级写反”。"
         "常见错路是先排主键再排次键——stable_sort 必须从次要到主要，反过来后面几趟会把主键重新打乱。"),
        ("若题目要求“总分相同的人按<b>输入顺序</b>输出”，用 sort＋下标 与 stable_sort 哪个更短？哪个更不容易写错？",
         "<code>stable_sort</code> 更短：<code>stable_sort(v.begin(), v.end(), [](const Stu &amp;a, const Stu &amp;b) { return a.sum &gt; b.sum; })</code> 一行，"
         "等价元素自动保持输入顺序，结构体里不用加字段。sort 加下标也能做：存 idx，cmp 里写 <code>a.sum != b.sum ? a.sum &gt; b.sum : a.idx &lt; b.idx</code>，多一个字段、多一层判断。<br>"
         "更不容易写错的是 stable_sort：不用想兜底、不用管方向，代价是多 O(n) 内存。"
         "常见错路是用 <code>sort</code> 却以为它稳定——sort 不保证，等价元素的次序完全可能被打乱。"),
    ],
))


# ---------------------------------------------------------------- 例题
SEC.append(WALK(
    "三个优先级，写成三层 if",
    [P('例题 · 奖学金 · <a href="https://www.luogu.com.cn/problem/P1093" target="_blank" rel="noopener">洛谷 P1093</a> <span class="badge diff">普及-</span>'),
     P("输入第一行一个整数 n，表示学生人数（n 不超过 300，且至少有 5 人）。"),
     P("接下来 n 行，每行三个整数（0~100），依次是语文、数学、英语成绩。学生按输入顺序编号为 1 到 n。"),
     P("按总分从高到低排序；总分相同按语文从高到低；语文也相同按学号从小到大。输出前 5 名，每行两个整数：学号、总分。"),
     C("输入：\n6\n90 67 80\n87 66 91\n78 89 91\n88 99 77\n67 89 64\n78 89 98\n"
       "输出：\n6 265\n4 264\n3 258\n2 244\n1 237", "样例")],
    [
        ("struct：五个字段打成一个包",
         [C(r'''struct Stu {
    int id;            // 原始下标：输入顺序就是学号，排序后靠它认人
    int ch, ma, en;    // 语文、数学、英语
    int sum;           // 总分：输入时就算好，别在 cmp 里反复加
};''', "Stu")],
         [P("5 个字段打成一个包。排序搬动的是整个 <code>Stu</code>，学号和总分的对应关系不会散。"
            "<code>sum</code> 在输入时就算好：放进 <code>cmp</code> 里每次现算，一次排序要多做 O(n log n) 次加法。")]),
        ("读入时记下原始下标、算好总分",
         [C(r'''    int n;
    cin >> n;
    Stu s[305];
    for (int i = 0; i < n; ++i) {
        s[i].id = i + 1;                        // 先记下原始下标，排完序就找不回来了
        cin >> s[i].ch >> s[i].ma >> s[i].en;
        s[i].sum = s[i].ch + s[i].ma + s[i].en;
    }''', "读入")],
         [P("<code>s[i].id = i + 1;</code> 必须在排序<b>之前</b>把原始下标存进结构体。排完序 <code>s[k]</code> 是第 k 名，"
            "只有 <code>id</code> 能告诉你他是谁。")]),
        ("cmp：三层 if，第一个不同的键就定胜负",
         [C(r'''// 返回 true 表示 a 应排在 b 前面
bool cmp(const Stu &a, const Stu &b) {
    if (a.sum != b.sum) return a.sum > b.sum;   // 第一关键字：总分降序
    if (a.ch  != b.ch ) return a.ch  > b.ch;    // 第二关键字：语文降序
    return a.id < b.id;                         // 第三关键字：学号升序
}''', "三层比较")],
         [P("<code>const Stu &amp;</code> 省下数百次结构体拷贝，也防止比较过程改坏数据。每一层都是“先判不同再比较”，"
            "不能写成 <code>a.sum &gt;= b.sum</code>。最后一层不是顺便加的：学号唯一，它把平局彻底消掉，"
            "少了它，总分语文都相同的人会互相“不小于”，严格弱序被破坏。")]),
        ("排序 + 输出前 5 名",
         [C(r'''    sort(s, s + n, cmp);                        // 左闭右开：覆盖 s[0] ~ s[n-1]

    for (int i = 0; i < 5 && i < n; ++i)
        cout << s[i].id << " " << s[i].sum << "\n";''', "排序与输出")],
         [P("左闭右开 <code>[s+0, s+n)</code> 正好覆盖 <code>s[0]~s[n−1]</code>，写成 <code>s+n−1</code> 会漏掉最后一个。"
            "输出用 <code>i &lt; 5 &amp;&amp; i &lt; n</code> 双保险：题目保证 n ≥ 5，但这样写不依赖题面。")]),
        ("完整程序",
         [C(r'''#include <bits/stdc++.h>
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
}''', "完整代码")],
         [P("这份程序可以直接提交，构建脚本会拿它做编译自检。样例输出 6 265 / 4 264 / 3 258 / 2 244 / 1 237。")]),
    ],
    [P("题型特征：一个对象有多个字段、排序规则一句话说不完——<code>struct</code> + <code>cmp</code>。"
       "看到“总分相同看语文，语文相同看学号”就该条件反射式地写三层 <code>if</code>。"),
     P("复杂度：一次 <code>sort</code>，O(n log n)；n = 300 时约 2.5×10³ 次比较，随便过。"),
     L(["<b>坑</b>：cmp 里用 <code>&gt;=</code> 或 <code>&lt;=</code>，<code>cmp(a,a)</code> 返回 true，典型症状是 RE。",
        "<b>坑</b>：只写总分一个关键字——测试点专挑“总分相同、语文不同”的构造。",
        "<b>坑</b>：忘了在排序前记下 <code>id</code>，排完就找不回学号了。"])],
    cover="覆盖：洛谷 P1093 / 结构体多关键字排序",
    tags=["模型：struct + cmp", "O(n log n)", "坑：严格弱序 / 平局兜底"],
    think=[
        ("“结构体里存原始下标”这件事还能用在哪？（输出原名次、离散化、排序后映射回原数组、按原顺序输出答案）",
         "至少四类：输出原名次（P1093 要输出学号，排序把顺序打乱后只有 id 能认人）；离散化时保留原值（原数组要被改写成编号，得先留一份）；"
         "排序后映射回原数组（按原顺序输出排序结果，或把排名写回原位）；以及需要“稳定”语义又不想换函数时，用下标当第二关键字。<br>"
         "凡是“排完序还要找回原来那个人或那个位置”的题，都要在下标被覆盖之前把它存进结构体。"
         "常见错路是排完序才想“第 3 名是谁”，这时原始下标已经找不回来了。"),
    ],
))

SEC.append(DIAG("flow", cap="cmp(a, b) 的三层判定：哪一层先返回 true，谁就排前面", items=[
    "sort 从 6 个学生里任取两个，调 cmp(a, b)",
    {"q": "a.sum != b.sum？", "yes": "return a.sum > b.sum（总分高的在前，后两层不执行）", "no": "总分相同，下沉一层"},
    {"q": "a.ch != b.ch？", "yes": "return a.ch > b.ch（语文高的在前）", "no": "语文也相同，只剩最后一层"},
    {"c": "return a.id < b.id;", "t": "学号升序：学号唯一，任意两人必分胜负"},
    {"q": "a、b 是同一个人（sum、ch、id 全相同）？", "yes": "三层“不相等”都不成立，返回 false → cmp(a,a) = false", "no": "前两层早已 return，走不到这里"},
    "三条公理（非自反、非对称、传递）都成立 → 严格弱序，sort 行为可预测",
]))

SEC.append(DIAG("array", cap="P1093 样例：下标 0..5 是输入顺序，值是总分", cells=[
    "237", "244", "258", "264", "220", "265"], idx=True, hl=[5],
    marks={0: "1号", 1: "2号", 2: "3号", 3: "4号", 4: "5号", 5: "6号"},
    note="sort 之后是 265(6号)、264(4号)、258(3号)、244(2号)、237(1号)；取前 5 名 → 6 265 / 4 264 / 3 258 / 2 244 / 1 237。"))

SEC.append(DIAG("compare", cap="同一个排序规则的两种载体：一次 cmp 还是多趟 stable_sort",
    left=("A：独立 cmp，排一次", [
        "一次 O(n log n)：300 人约 2.5×10³ 次比较",
        "逻辑集中在一处，能单独喂两组数据验算",
        "三层 if 的优先级写错，整题就错"]),
    right=("C：逐层 stable_sort，排 k 趟", [
        "从最次要的键排到最重要的键：id → ch → sum",
        "每趟只比一个字段，优先级几乎不可能写错",
        "代价：排序 3 遍，常数乘 3，多花 O(n) 内存"]),
    note="P1093 在 n ≤ 300 时两种写法都瞬间过，差别只在“哪种更不容易写反”。先算出这个量级，才敢选。"))

SEC.append(DIAG("flow", cap="为什么写 >= 会 RE 而不是编译错误：sort 分区里指针停不下来", items=[
    "sort 取一个 pivot，左右两个指针向中间走，靠 cmp 决定停不停",
    {"q": "cmp(*p, pivot) 为真（还小，可以继续）？", "yes": "指针继续前进", "no": "停下，等另一侧交换"},
    {"c": "bool bad(int a, int b) { return a >= b; }", "t": "写 >= 时 cmp(x, x) 也是 true —— 等于 pivot 的元素永远“还小”"},
    "于是等于 pivot 的那一段没人停下，两个指针一路冲出数组两端",
    {"q": "越过 a + n 了吗？", "yes": "越界写内存 → 段错误 RE，或随机 WA；编译器不会拦", "no": "正常分区，交换后继续"},
    "改成严格 > ：cmp(x, x) 返回 false，指针一定停得住，分区必然收敛",
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
    SEC, math=M, check=CHECK, challenge=CHALLENGE,
    refs=["《算法竞赛进阶指南》0x05：排序与离散化",
          "《算法竞赛试炼场：洛谷300题精析》排序章",
          "洛谷 P1093、P1104 题解区的高赞写法"],
)]
