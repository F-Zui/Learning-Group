window.MODULE = {"title": "数学类模板", "subtitle": "Mathematics Course Template", "mark": "∫", "progressKey": "lg-math-template.progress.v1", "uiKey": "lg-math-template.ui.v1", "progressFile": "math-template-progress.json", "kicker": "Mathematics · Template", "description": "数学类课程的标准版式：推导卡 → 定义/定理 → 证明 → 图像与例题 → 算法落地卡 → 习题 → 一页纸；含函数图像、几何示意图、代码块与算法流程图，以及全站检索、深浅色主题与学习进度。", "searchHint": "检索全站：ε-δ / 推导卡 / 算法落地 / 例题 …", "lede": "复制这个目录即可新建一门数学课：推导卡、定理与证明、函数图像与流程图、代码块与算法落地卡、例题与习题、全站检索、深浅色主题、学习进度都已接好。把 <code>tools/curriculum.py</code> 换成你的章节，再按 <code>sections/_骨架.html</code> 写内容即可。"};
window.CURRICULUM = [
 {
  "n": 1,
  "part": "I",
  "title": "极限与连续",
  "sub": "把“靠近”写成不等式：分析学的全部语言都从这里出发。",
  "sections": [
   {
    "id": "1.1",
    "title": "极限的 ε-δ 定义",
    "core": "任意 ε 找 δ：极限的量化语言与估计套路",
    "diff": 2,
    "file": "sections/1-1.html"
   },
   {
    "id": "1.2",
    "title": "连续与一致连续",
    "core": "连续的三等价说法、间断分类与一致连续的差别",
    "diff": 3,
    "file": "sections/1-2.html"
   }
  ]
 },
 {
  "n": 2,
  "part": "I",
  "title": "数论与算法",
  "sub": "用定理撑起算法：从 Bézout 到扩展欧几里得。",
  "sections": [
   {
    "id": "2.1",
    "title": "最大公约数与 Bézout 恒等式",
    "core": "证明存在性，再把它变成 O(log n) 的 exgcd",
    "diff": 2,
    "file": "sections/2-1.html"
   }
  ]
 }
];
