// 算竞教程 · 交互脚本
// ① 侧边栏：章节导航 + 完成情况（可滚动、可勾选）
// ② 勾选「已学」= ⭐，再勾「挑战2」= 🌟；状态存 localStorage，取不到时退化到内存

(function () {
  'use strict';

  var KEY_L = function (id) { return 'ac_learned_' + id; };
  var KEY_C = function (id) { return 'ac_ch2_' + id; };
  var DEF = {};      // id -> 课程表默认「已学」
  var MEM = {};      // localStorage 不可用时的内存兜底

  // ---------------------------------------------------------------- 存储层
  // 关键：显式存 '0' 表示「手动取消」，不要用 removeItem，
  // 否则会和「从未设置 → 用默认值」混为一谈，导致取消勾选后立刻被弹回。
  function raw(id, key) {
    try {
      var v = localStorage.getItem(key(id));
      if (v !== null) return v;
    } catch (e) { /* file:// 下可能被禁 */ }
    return Object.prototype.hasOwnProperty.call(MEM, key(id)) ? MEM[key(id)] : null;
  }
  function put(id, key, v) {
    var val = v ? '1' : '0';
    MEM[key(id)] = val;
    try { localStorage.setItem(key(id), val); } catch (e) { /* 忽略，用内存 */ }
  }
  function isLearned(id) {
    var v = raw(id, KEY_L);
    if (v === null) return DEF[id] === true;
    return v === '1';
  }
  function isCh2(id) { return raw(id, KEY_C) === '1'; }

  function markOf(id) {
    var l = isLearned(id), c = isCh2(id);
    if (l && c) return '🌟';
    if (l) return '⭐';
    return '';
  }

  // ---------------------------------------------------------------- 侧边栏
  function buildSidebar() {
    if (!window.COURSE) return null;

    var btn = document.createElement('button');
    btn.className = 'sb-btn';
    btn.type = 'button';
    btn.innerHTML = '<span class="sb-ico">☰</span><span class="sb-txt">章节</span>';
    btn.addEventListener('click', function () { toggleSidebar(); });

    var mask = document.createElement('div');
    mask.className = 'sb-mask';
    mask.addEventListener('click', function () { toggleSidebar(false); });

    var aside = document.createElement('aside');
    aside.className = 'sidebar';

    var head = [];
    head.push('<div class="sb-head">');
    head.push('<div class="sb-title">全部 ' + window.COURSE.total + ' 节</div>');
    head.push('<div class="sb-prog"><span id="sbLearn"></span></div>');
    head.push('<div class="sb-legend">⭐ 已学　🌟 已学 + 完成挑战2</div>');
    head.push('<button class="sb-close" type="button" aria-label="关闭">×</button>');
    head.push('</div>');

    var body = [];
    body.push('<div class="sb-body">');

    if (window.COURSE.extra && window.COURSE.extra.length) {
      body.push('<div class="sb-group">题解</div>');
      for (var e = 0; e < window.COURSE.extra.length; e++) {
        var ex = window.COURSE.extra[e];
        body.push('<div class="sb-item sb-extra"><a class="sb-link" href="' + ex.file + '">' +
          '<span class="sb-nm">' + ex.title + '</span></a></div>');
      }
    }

    for (var g = 0; g < window.COURSE.groups.length; g++) {
      var grp = window.COURSE.groups[g];
      body.push('<div class="sb-group">' + grp.name + '</div>');
      for (var i = 0; i < grp.items.length; i++) {
        var it = grp.items[i];
        var kindTag = it.kind === 'review' ? ' <em>回顾</em>'
          : (it.kind === 'mock' ? ' <em>模拟赛</em>' : '');
        body.push(
          '<div class="sb-item" data-id="' + it.id + '">' +
            '<a class="sb-link" href="' + it.file + '">' +
              '<span class="sb-no">' + (it.id < 10 ? '0' + it.id : it.id) + '</span>' +
              '<span class="sb-nm">' + it.title + kindTag + '</span>' +
            '</a>' +
            '<span class="sb-marks">' +
              '<label class="mk" title="已学（⭐）">' +
                '<input type="checkbox" data-role="learned" data-id="' + it.id + '">' +
                '<span class="mk-t">⭐</span>' +
              '</label>' +
              (it.id >= 21
                ? '<label class="mk" title="完成挑战2（🌟）">' +
                    '<input type="checkbox" data-role="ch2" data-id="' + it.id + '">' +
                    '<span class="mk-t">🌟</span>' +
                  '</label>'
                : '') +
            '</span>' +
          '</div>');
      }
    }
    body.push('</div>');

    aside.innerHTML = head.join('') + body.join('');
    document.body.appendChild(btn);
    document.body.appendChild(mask);
    document.body.appendChild(aside);

    // 事件委托：勾选
    aside.addEventListener('change', function (ev) {
      var t = ev.target;
      if (!t || t.tagName !== 'INPUT') return;
      var id = parseInt(t.getAttribute('data-id'), 10);
      var role = t.getAttribute('data-role');
      applyToggle(id, role, t.checked);
    });

    aside.querySelector('.sb-close').addEventListener('click', function () { toggleSidebar(false); });

    // 初始同步
    var boxes = aside.querySelectorAll('input[type="checkbox"]');
    Array.prototype.forEach.call(boxes, function (cb) {
      var id = parseInt(cb.getAttribute('data-id'), 10);
      cb.checked = cb.getAttribute('data-role') === 'learned' ? isLearned(id) : isCh2(id);
    });

    // 当前页高亮 + 滚到视野内
    var cur = document.body.getAttribute('data-lesson');
    if (cur) {
      var row = aside.querySelector('.sb-item[data-id="' + cur + '"]');
      if (row) {
        row.classList.add('cur');
        var box = aside.querySelector('.sb-body');
        if (box && row.offsetTop > box.clientHeight * 0.6) {
          box.scrollTop = row.offsetTop - box.clientHeight * 0.4;
        }
      }
    }
    return aside;
  }

  // 统一处理一次勾选（侧边栏与目录页共用）
  function applyToggle(id, role, checked) {
    if (role === 'learned') {
      put(id, KEY_L, checked);
      if (!checked) { put(id, KEY_C, false); syncBox(id, 'ch2'); }
    } else {
      put(id, KEY_C, checked);
      if (checked) { put(id, KEY_L, true); syncBox(id, 'learned'); }
    }
    syncBox(id, role);
    refreshProgress();
  }

  function syncBox(id, role) {
    var sel = 'input[data-id="' + id + '"][data-role="' + role + '"]';
    var list = document.querySelectorAll(sel);
    Array.prototype.forEach.call(list, function (cb) {
      cb.checked = role === 'learned' ? isLearned(id) : isCh2(id);
    });
  }

  function toggleSidebar(force) {
    var aside = document.querySelector('.sidebar');
    var mask = document.querySelector('.sb-mask');
    if (!aside) return;
    var open = force === undefined ? !aside.classList.contains('open') : force;
    aside.classList.toggle('open', open);
    if (mask) mask.classList.toggle('open', open);
    document.body.classList.toggle('sb-lock', open);
  }

  // ---------------------------------------------------------------- 进度
  function allItems() {
    var all = [];
    if (!window.COURSE) return all;
    for (var g = 0; g < window.COURSE.groups.length; g++)
      all = all.concat(window.COURSE.groups[g].items);
    return all;
  }

  function refreshProgress() {
    var all = allItems();
    if (!all.length) return;
    var learned = 0, ch2n = 0, ch2total = 0;
    for (var i = 0; i < all.length; i++) {
      if (isLearned(all[i].id)) learned++;
      if (all[i].id >= 21) { ch2total++; if (isCh2(all[i].id)) ch2n++; }
    }
    var el = document.getElementById('sbLearn');
    if (el) el.innerHTML = '已学 <b>' + learned + '</b> / ' + all.length +
      '　·　挑战2 <b>' + ch2n + '</b> / ' + ch2total;

    var ib = document.getElementById('idxProg');
    if (ib) {
      ib.innerHTML = '已学 <b>' + learned + '</b> / ' + all.length +
        '　·　完成挑战2 <b>' + ch2n + '</b> / ' + ch2total;
      var bar = document.getElementById('idxBar');
      if (bar) bar.style.width = (100 * learned / all.length).toFixed(1) + '%';
    }

    var lid = document.body.getAttribute('data-lesson');
    var pmark = document.getElementById('pageMark');
    if (pmark && lid && /^\d+$/.test(lid)) {
      var m = markOf(parseInt(lid, 10));
      pmark.textContent = m;
      pmark.style.display = m ? '' : 'none';
    }
  }

  // ---------------------------------------------------------------- 目录页
  function initIndex() {
    var rows = document.querySelectorAll('.toc-item[data-id]');
    if (!rows.length) return;
    Array.prototype.forEach.call(rows, function (row) {
      var id = parseInt(row.getAttribute('data-id'), 10);
      if (!id) return;
      var marks = row.querySelector('.stars');
      function paint() {
        var m = markOf(id);
        if (marks) { marks.textContent = m; marks.style.display = m ? '' : 'none'; }
      }
      var els = row.querySelectorAll('input[type="checkbox"]');
      Array.prototype.forEach.call(els, function (cb) {
        var role = cb.getAttribute('data-role');
        cb.checked = role === 'learned' ? isLearned(id) : isCh2(id);
        cb.addEventListener('change', function () {
          put(id, role === 'learned' ? KEY_L : KEY_C, cb.checked);
          if (role === 'learned' && !cb.checked) put(id, KEY_C, false);
          if (role === 'ch2' && cb.checked) put(id, KEY_L, true);
          syncBox(id, 'learned');
          syncBox(id, 'ch2');
          paint();
          refreshProgress();
        });
      });
      paint();
    });
  }

  // ---------------------------------------------------------------- 初始化
  function init() {
    if (window.COURSE) {
      var all = allItems();
      for (var i = 0; i < all.length; i++) DEF[all[i].id] = !!all[i].star;
    }
    buildSidebar();
    initIndex();
    refreshProgress();
    if (location.search.indexOf('selftest') >= 0) setTimeout(selfTest, 50);
  }

  // ---------------------------------------------------------------- 自测
  // 打开 26.html?selftest=1 会跑一遍「勾选 → 读回 → 取消 → 读回」，结果写进 <title>
  function selfTest() {
    var log = [];
    function box(id, role) {
      return document.querySelector('.sb-item[data-id="' + id + '"] input[data-role="' + role + '"]');
    }
    try {
      var b21 = box(21, 'learned');
      log.push('find21=' + (b21 ? 'y' : 'n'));
      if (b21) {
        log.push('init21=' + b21.checked);
        b21.click();
        log.push('click1=' + b21.checked + '/' + isLearned(21));
        b21.click();
        log.push('click2=' + b21.checked + '/' + isLearned(21));
      }
      var b1 = box(1, 'learned');
      if (b1) {
        log.push('init01=' + b1.checked);
        b1.click();
        log.push('un01=' + b1.checked + '/' + isLearned(1));
        b1.click();
        log.push('re01=' + b1.checked + '/' + isLearned(1));
      }
      var c21 = box(21, 'ch2');
      if (c21) {
        c21.click();
        log.push('ch2=' + c21.checked + '/' + isCh2(21) + '/L' + isLearned(21));
      }
      var sb = document.querySelector('.sb-body');
      log.push('body=' + (sb ? 'y' : 'n'));
      if (sb) log.push('scrollable=' + (sb.scrollHeight > sb.clientHeight + 4));
      log.push('items=' + document.querySelectorAll('.sb-item').length);
      log.push('store=' + (function () {
        try { localStorage.setItem('__t', '1'); localStorage.removeItem('__t'); return 'ok'; }
        catch (e) { return 'blocked'; }
      })());
    } catch (e) {
      log.push('ERR:' + (e && e.message ? e.message : e));
    }
    document.title = 'SELFTEST ' + log.join(' ; ');
  }

  window.__ac = { isLearned: isLearned, isCh2: isCh2, put: put, markOf: markOf };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
