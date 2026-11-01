window.MODULE = {"title": "数论入门", "subtitle": "Elementary Number Theory for Competitive Programming", "mark": "ℤ", "progressKey": "lg-number-theory.progress.v1", "uiKey": "lg-number-theory.ui.v1", "progressFile": "number-theory-progress.json", "kicker": "Mathematics · Number Theory", "description": "面向信息竞赛学生的数论入门教程：整除、Euclid 算法、素数、同余、快速幂、数论函数、Möbius 反演、二次剩余、二次互反律与 Pell 方程，配证明、图像、C++ 代码与算法流程图。", "searchHint": "检索全站：Möbius / 逆元 / 二次剩余 / Pell …", "lede": "从整数的内部结构出发：整除、同余、素数，一路走到数论函数、Möbius 反演与二次互反律。每个定理都配证明、图像与例题，每个算法都配 C++ 代码与逻辑流程图。"};
window.CURRICULUM = [
 {
  "n": 0,
  "part": "I",
  "title": "起点",
  "sub": "先看地图，再磨工具：数论研究整数的哪一种结构，证明又为什么必须比计算更严格。",
  "sections": [
   {
    "id": "0.1",
    "title": "数论的地图与证明工具箱",
    "core": "用良序、归纳、反证把整数的直觉变成可检验的证明",
    "diff": 1,
    "file": "sections/0-1.html"
   }
  ]
 },
 {
  "n": 1,
  "part": "I",
  "title": "整除与素数",
  "sub": "整数的第一层结构：谁被谁分成几份，以及那些再也分不动的积木。",
  "sections": [
   {
    "id": "1.1",
    "title": "整除与带余除法",
    "core": "把除法写成唯一的一对商与余数，用余数做分类讨论",
    "diff": 1,
    "file": "sections/1-1.html"
   },
   {
    "id": "1.2",
    "title": "Euclid 算法与 Bézout 恒等式",
    "core": "用取余求 gcd，用 exgcd 解 ax+by=gcd 与线性丢番图方程",
    "diff": 2,
    "file": "sections/1-2.html"
   },
   {
    "id": "1.3",
    "title": "素数与算术基本定理",
    "core": "证明素数无穷多、分解唯一，并用 Euclid 引理处理整除",
    "diff": 2,
    "file": "sections/1-3.html"
   },
   {
    "id": "1.4",
    "title": "筛法、素性判定与分解",
    "core": "从埃氏筛到线性筛、Miller–Rabin 与 Pollard–Rho 的算法全景",
    "diff": 3,
    "file": "sections/1-4.html"
   }
  ]
 },
 {
  "n": 2,
  "part": "II",
  "title": "同余",
  "sub": "只看余数的世界：等式变成同余式，逆元与周期成为新的运算规则。",
  "sections": [
   {
    "id": "2.1",
    "title": "同余、逆元与中国剩余定理",
    "core": "解线性同余、求模逆，并把多个模条件合并成一个",
    "diff": 2,
    "file": "sections/2-1.html"
   },
   {
    "id": "2.2",
    "title": "快速幂、Fermat–Euler 与 Wilson 定理",
    "core": "用 O(log n) 次乘法算大指数，理解 RSA 与阶乘同余",
    "diff": 2,
    "file": "sections/2-2.html"
   }
  ]
 },
 {
  "n": 3,
  "part": "III",
  "title": "数论函数",
  "sub": "不再盯着一个数，而是盯着“约数”“互素”“公因子”的函数关系。",
  "sections": [
   {
    "id": "3.1",
    "title": "数论函数与线性筛",
    "core": "用积性拆解 τ、σ、φ，并在 O(n) 内一次筛出所有值",
    "diff": 3,
    "file": "sections/3-1.html"
   },
   {
    "id": "3.2",
    "title": "Möbius 反演与求和实战",
    "core": "把 gcd 求和化成约数求和，再用整除分块压到 O(√n)",
    "diff": 3,
    "file": "sections/3-2.html"
   }
  ]
 },
 {
  "n": 4,
  "part": "IV",
  "title": "二次剩余",
  "sub": "开平方在模世界里什么时候可行？Legendre 符号与互反律给出回答。",
  "sections": [
   {
    "id": "4.1",
    "title": "二次剩余与 Legendre 符号",
    "core": "用平方表与 Euler 判别法判断 x²≡a (mod p) 是否有解",
    "diff": 2,
    "file": "sections/4-1.html"
   },
   {
    "id": "4.2",
    "title": "Gauss 引理与二次互反律",
    "core": "用数格子证明互反律，并把大 Legendre 符号翻转成小符号",
    "diff": 3,
    "file": "sections/4-2.html"
   },
   {
    "id": "4.3",
    "title": "Tonelli–Shanks 模平方根",
    "core": "知道有解之后，在 O(log²p) 内把平方根真正算出来",
    "diff": 3,
    "file": "sections/4-3.html"
   }
  ]
 },
 {
  "n": 5,
  "part": "V",
  "title": "走向远方",
  "sub": "从一题一解走向问题与方法：Pell 方程、连分数，以及计算与证明的边界。",
  "sections": [
   {
    "id": "5.1",
    "title": "Pell 方程与连分数",
    "core": "用 √D 的连分数展开求 x²−Dy²=1 的最小正整数解",
    "diff": 3,
    "file": "sections/5-1.html"
   },
   {
    "id": "5.2",
    "title": "猜想实验室：从数据到证明",
    "core": "用程序看见 Goldbach、孪生素数与 Collatz，并分清证据与证明",
    "diff": 2,
    "file": "sections/5-2.html"
   }
  ]
 }
];
