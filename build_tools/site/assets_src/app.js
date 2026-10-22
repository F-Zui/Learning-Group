// 算竞教程 · 交互脚本
// ① 侧边栏：章节导航 + 完成情况（可滚动、可勾选）
// ② 勾选「已学」= ⭐，再勾「挑战2」= 🌟；状态存 localStorage，取不到时退化到内存
// ③ 目录页全文检索：回车检索、标题命中优先、命中处上下各一行、点击跳到关键字位置

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

  // ---------------------------------------------------------------- 目录页勾选
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

  // ================================================================ 检索
  var S = {};
  var IDX_READY = false, IDX_LOADING = false, IDX_CB = [];

  function ensureIndex(cb) {
    if (IDX_READY || window.SEARCH_DOCS) { IDX_READY = true; cb(); return; }
    IDX_CB.push(cb);
    if (IDX_LOADING) return;
    IDX_LOADING = true;
    var s = document.createElement('script');
    s.src = 'assets/search-index.js';
    s.onload = function () {
      IDX_READY = true; IDX_LOADING = false;
      IDX_CB.splice(0).forEach(function (f) { try { f(); } catch (e) { } });
    };
    s.onerror = function () {
      IDX_LOADING = false;
      if (S.srWrap) {
        S.srWrap.innerHTML = '<div class="sr-empty">检索索引加载失败：assets/search-index.js 缺失。</div>';
        S.srWrap.hidden = false;
      }
    };
    document.body.appendChild(s);
  }

  function escHtml(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function escRe(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

  function markHtml(text, q) {
    if (!q) return escHtml(text);
    var re = new RegExp('(' + escRe(q) + ')', 'ig');
    return escHtml(text).replace(re, '<mark class="sr-mk">$1</mark>');
  }

  // 命中处上下文窗口
  function windowAround(text, q, before, after) {
    var low = text.toLowerCase(), qq = q.toLowerCase();
    var p = low.indexOf(qq);
    if (p < 0) return { pre: '', mid: text.slice(0, before), post: text.slice(before, before + after) };
    var s = Math.max(0, p - before);
    var e = Math.min(text.length, p + qq.length + after);
    return {
      pre: (s > 0 ? '…' : '') + text.slice(s, p),
      mid: text.slice(p, p + qq.length),
      post: text.slice(p + qq.length, e) + (e < text.length ? '…' : '')
    };
  }
  function tail(t, n) { return t.length <= n ? t : '…' + t.slice(-n); }
  function head(t, n) { return t.length <= n ? t : t.slice(0, n) + '…'; }

  var MAX_HITS = 240;

  function runSearch(q) {
    var docs = window.SEARCH_DOCS || [];
    var qq = q.toLowerCase();
    var titleHits = [], bodyHits = [], total = 0;
    for (var i = 0; i < docs.length; i++) {
      var d = docs[i];
      var inTitle = d.t.toLowerCase().indexOf(qq) >= 0;
      var tagHit = (d.tg || []).filter(function (t) { return t.toLowerCase().indexOf(qq) >= 0; });
      if (inTitle || tagHit.length) titleHits.push([d, inTitle, tagHit]);
      for (var j = 0; j < d.b.length; j++) {
        if (d.b[j][2].toLowerCase().indexOf(qq) >= 0) {
          total++;
          if (bodyHits.length < MAX_HITS) bodyHits.push([d, j]);
        }
      }
    }
    titleHits.sort(function (a, b) { return (a[0].n || 0) - (b[0].n || 0); });
    renderResults(q, titleHits, bodyHits, total);
  }

  function renderResults(q, titleHits, bodyHits, total) {
    var out = [];
    out.push('<div class="sr-sum">检索 <b>' + escHtml(q) + '</b>：标题命中 <b>' +
      titleHits.length + '</b> 节，正文命中 <b>' + total + '</b> 处' +
      (total > MAX_HITS ? '（只显示前 ' + MAX_HITS + ' 处，请把关键词写具体些）' : '') + '</div>');

    if (titleHits.length) {
      out.push('<div class="sr-sec">章节标题命中</div><div class="sr-list">');
      titleHits.forEach(function (hit) {
        var d = hit[0], inTitle = hit[1], tagHit = hit[2];
        var no = d.n ? (d.n < 10 ? '0' + d.n : '' + d.n) : '题解';
        var tagHtml = '';
        if (tagHit.length) {
          tagHtml = '<span class="sr-tag">标签命中：' + tagHit.map(function (t) {
            return markHtml(t, q);
          }).join('、') + '</span>';
        }
        out.push('<a class="sr-title" href="' + d.f + '">' +
          '<span class="sr-no">' + no + '</span>' +
          '<span class="sr-tn">' + (inTitle ? markHtml(d.t, q) : escHtml(d.t)) + '</span>' +
          tagHtml +
          '<span class="badge diff">' + escHtml(d.lv || '') + '</span></a>');
      });
      out.push('</div>');
    }

    if (bodyHits.length) {
      out.push('<div class="sr-sec">正文命中 · 点击跳到关键字位置</div><div class="sr-list">');
      bodyHits.forEach(function (pair) {
        var d = pair[0], idx = pair[1];
        var blk = d.b[idx];
        var anchor = blk[0], hidx = blk[1], txt = blk[2];
        var sub = (d.hs && d.hs[hidx]) ? d.hs[hidx] : '';
        var no = d.n ? (d.n < 10 ? '0' + d.n : '' + d.n) : '题解';
        var href = d.f + '?q=' + encodeURIComponent(q) + '#' + anchor;

        out.push('<a class="sr-hit" href="' + href + '">');
        out.push('<div class="sr-head"><span class="sr-no">' + no + '</span>' +
          '<span class="sr-tt">' + escHtml(d.t) + '</span>' +
          (sub ? '<span class="sr-sub">› ' + escHtml(sub) + '</span>' : '') + '</div>');
        if (idx > 0) {
          out.push('<div class="sr-line sr-dim">' + escHtml(tail(d.b[idx - 1][2], 44)) + '</div>');
        }
        var w = windowAround(txt, q, 50, 76);
        out.push('<div class="sr-line sr-main">' + escHtml(w.pre) +
          '<mark class="sr-mk">' + escHtml(w.mid) + '</mark>' + escHtml(w.post) + '</div>');
        if (idx + 1 < d.b.length) {
          out.push('<div class="sr-line sr-dim">' + escHtml(head(d.b[idx + 1][2], 44)) + '</div>');
        }
        out.push('</a>');
      });
      out.push('</div>');
    }

    if (!titleHits.length && !bodyHits.length) {
      out.push('<div class="sr-empty">没有找到「' + escHtml(q) + '」。<br>' +
        '试试更短的关键词（如「前缀」而不是「前缀和怎么用」），或换个说法。</div>');
    }

    S.srWrap.innerHTML = out.join('');
    S.srWrap.hidden = false;
    if (S.tocWrap) S.tocWrap.hidden = true;
    if (S.clearBtn) S.clearBtn.hidden = false;
  }

  function clearSearch() {
    if (S.srWrap) { S.srWrap.hidden = true; S.srWrap.innerHTML = ''; }
    if (S.tocWrap) S.tocWrap.hidden = false;
    if (S.clearBtn) S.clearBtn.hidden = true;
    if (S.input) { S.input.value = ''; S.input.focus(); }
    if (/[?&]q=/.test(location.search) && history.replaceState) {
      history.replaceState(null, '', location.pathname);
    }
  }

  function initSearch() {
    S.input = document.getElementById('q');
    if (!S.input) return;
    S.srWrap = document.getElementById('srWrap');
    S.tocWrap = document.getElementById('tocWrap');
    S.clearBtn = document.getElementById('qClear');
    S.form = document.getElementById('srForm');

    function go() {
      var q = (S.input.value || '').trim();
      if (!q) { clearSearch(); return; }
      ensureIndex(function () { runSearch(q); });
    }

    if (S.form) S.form.addEventListener('submit', function (e) { e.preventDefault(); go(); });
    S.input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') { e.preventDefault(); go(); }
      else if (e.key === 'Escape') { clearSearch(); }
    });
    if (S.clearBtn) S.clearBtn.addEventListener('click', clearSearch);

    var m = /[?&]q=([^&]*)/.exec(location.search);
    if (m) {
      var q = decodeURIComponent(m[1].replace(/\+/g, ' '));
      S.input.value = q;
      ensureIndex(function () { runSearch(q); });
    }
  }

  // ================================================================ 跳到命中处
  function jumpToHit() {
    var m = /^#(b\d+)$/.exec(location.hash || '');
    if (!m) return;
    var el = document.getElementById(m[1]);
    if (!el) return;

    var p = el.parentNode;
    while (p && p.nodeType === 1) {
      if (p.tagName === 'DETAILS' && !p.open) p.open = true;
      p = p.parentNode;
    }

    var qm = /[?&]q=([^&]*)/.exec(location.search);
    var q = qm ? decodeURIComponent(qm[1].replace(/\+/g, ' ')) : '';
    if (q) highlightIn(el, q);

    el.classList.add('sr-flash');
    setTimeout(function () { el.classList.remove('sr-flash'); }, 2600);
    // 即时定位：页面上有 html{scroll-behavior:smooth}，会让 scrollTo 变成动画，
    // 长页面下容易被中断，所以临时改成 auto 再滚。
    function place() {
      var html = document.documentElement;
      var prev = html.style.scrollBehavior;
      html.style.scrollBehavior = 'auto';
      var top = el.getBoundingClientRect().top + window.pageYOffset;
      var h = window.innerHeight || 800;
      var target = Math.max(0, top - h / 2 + el.offsetHeight / 2);
      window.scrollTo(0, target);
      html.style.scrollBehavior = prev;
    }
    setTimeout(place, 30);
    setTimeout(function () {
      var r = el.getBoundingClientRect();
      if (r.top < 0 || r.bottom > (window.innerHeight || 800)) place();
    }, 400);
    armClearHighlight();
  }

  // 跳转后的关键词高亮，在下一次点击屏幕时清除
  function clearHitMarks() {
    var marks = document.querySelectorAll('mark.sr-mk.hit');
    Array.prototype.forEach.call(marks, function (m) {
      var p = m.parentNode;
      if (!p) return;
      p.replaceChild(document.createTextNode(m.textContent), m);
      p.normalize();
    });
    var fl = document.querySelectorAll('.sr-flash');
    Array.prototype.forEach.call(fl, function (x) { x.classList.remove('sr-flash'); });
  }

  function armClearHighlight() {
    if (!document.querySelector('mark.sr-mk.hit')) return;
    function once() {
      document.removeEventListener('click', once, true);
      document.removeEventListener('keydown', onKey, true);
      clearHitMarks();
    }
    function onKey(e) {
      if (e.key !== 'Escape') return;
      document.removeEventListener('click', once, true);
      document.removeEventListener('keydown', onKey, true);
      clearHitMarks();
    }
    document.addEventListener('click', once, true);
    document.addEventListener('keydown', onKey, true);
  }

  function highlightIn(root, q) {
    var probe = new RegExp(escRe(q), 'i');
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null, false);
    var nodes = [], n;
    while ((n = walker.nextNode())) if (probe.test(n.nodeValue)) nodes.push(n);
    nodes.forEach(function (node) {
      var txt = node.nodeValue;
      var frag = document.createDocumentFragment();
      var last = 0, r = new RegExp(escRe(q), 'ig'), mm;
      while ((mm = r.exec(txt)) !== null) {
        if (mm[0].length === 0) { r.lastIndex++; continue; }
        if (mm.index > last) frag.appendChild(document.createTextNode(txt.slice(last, mm.index)));
        var mk = document.createElement('mark');
        mk.className = 'sr-mk hit';
        mk.textContent = mm[0];
        frag.appendChild(mk);
        last = mm.index + mm[0].length;
      }
      if (last < txt.length) frag.appendChild(document.createTextNode(txt.slice(last)));
      node.parentNode.replaceChild(frag, node);
    });
  }

  // ================================================================ 右侧本节目录
  function initRtoc() {
    var panel = document.getElementById('rtoc');
    if (!panel) return;
    var tab = document.getElementById('rtTab');
    var closeBtn = document.getElementById('rtClose');
    var KEY = 'ac_rtoc';

    var saved = null;
    try { saved = localStorage.getItem(KEY); } catch (e) { }
    var wide = window.matchMedia('(min-width:1440px)').matches;
    var open = saved === null ? wide : saved === '1';

    function apply(v, persist) {
      panel.classList.toggle('open', v);
      document.body.classList.toggle('rtoc-open', v);
      if (persist !== false) { try { localStorage.setItem(KEY, v ? '1' : '0'); } catch (e) { } }
    }
    apply(open, false);
    if (tab) tab.addEventListener('click', function () { apply(true); });
    if (closeBtn) closeBtn.addEventListener('click', function () { apply(false); });

    var links = Array.prototype.slice.call(panel.querySelectorAll('.rt-i'));
    var targets = links.map(function (a) {
      return document.getElementById(a.getAttribute('data-t'));
    });

    function setCur(i) {
      links.forEach(function (a, k) { a.classList.toggle('cur', k === i); });
      if (i >= 0 && links[i]) {
        var body = panel.querySelector('.rt-body');
        var a = links[i];
        if (body && (a.offsetTop < body.scrollTop ||
                     a.offsetTop > body.scrollTop + body.clientHeight - 40)) {
          body.scrollTop = a.offsetTop - body.clientHeight * 0.4;
        }
      }
    }

    function scrollToEl(el) {
      var html = document.documentElement;
      var prev = html.style.scrollBehavior;
      html.style.scrollBehavior = 'auto';
      var top = el.getBoundingClientRect().top + window.pageYOffset - 64;
      window.scrollTo(0, Math.max(0, top));
      html.style.scrollBehavior = prev;
    }

    panel.addEventListener('click', function (ev) {
      var a = ev.target;
      while (a && a !== panel && !(a.className && String(a.className).indexOf('rt-i') >= 0)) {
        a = a.parentNode;
      }
      if (!a || a === panel) return;
      ev.preventDefault();
      var id = a.getAttribute('data-t');
      var el = document.getElementById(id);
      if (!el) return;
      scrollToEl(el);
      setCur(links.indexOf(a));
      if (!window.matchMedia('(min-width:1440px)').matches) apply(false);
    });

    // 滚动联动高亮
    var ticking = false;
    function spy() {
      ticking = false;
      var best = -1;
      for (var i = 0; i < targets.length; i++) {
        var t = targets[i];
        if (!t) continue;
        if (t.getBoundingClientRect().top - 80 <= 0) best = i;
      }
      setCur(best);
    }
    window.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(spy);
    }, { passive: true });
    spy();
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
    initSearch();
    initRtoc();
    jumpToHit();
    if (location.search.indexOf('selftest') >= 0) setTimeout(selfTest, 80);
  }

  function selfTest() {
    var log = [];
    function done() { document.title = 'SELFTEST ' + log.join(' ; '); }
    try {
      // ---- 跳到命中处 → 点一下屏幕 → 高亮应消失 ----
      if (location.hash) {
        var el = document.getElementById(location.hash.slice(1));
        log.push('anchor=' + (el ? 'y' : 'n'));
        log.push('flash=' + !!(el && el.classList.contains('sr-flash')));
        var m0 = document.querySelectorAll('mark.sr-mk.hit').length;
        log.push('marks0=' + m0);
        setTimeout(function () {
          document.body.click();
          setTimeout(function () {
            log.push('marks1=' + document.querySelectorAll('mark.sr-mk.hit').length);
            done();
          }, 60);
        }, 500);
        return;
      }

      var b1 = document.querySelector('.sb-item[data-id="1"] input[data-role="learned"]');
      if (b1) {
        var was = b1.checked;
        b1.click();
        log.push('toggle01=' + (b1.checked !== was));
        b1.click();
        log.push('back01=' + (b1.checked === was));
      }
      var sb = document.querySelector('.sb-body');
      log.push('scroll=' + (sb ? (sb.scrollHeight > sb.clientHeight + 4) : 'no'));

      // ---- 右侧本节目录 ----
      var panel = document.getElementById('rtoc');
      if (panel) {
        var links = panel.querySelectorAll('.rt-i');
        log.push('rtoc=' + (panel.classList.contains('open') ? 'open' : 'closed') +
          '/items=' + links.length +
          '/sum=' + (panel.querySelector('.rt-sum').textContent.length > 20 ? 'y' : 'n'));
        var body = panel.querySelector('.rt-body');
        log.push('rtScroll=' + (body ? (body.scrollHeight > body.clientHeight) : 'no'));
        if (links.length > 2 && !location.hash) {
          var before = window.pageYOffset;
          links[2].click();
          log.push('rtJump=' + (Math.abs(window.pageYOffset - before) > 20 ? 'y' : 'n') +
            '/y=' + Math.round(window.pageYOffset) +
            '/cur=' + panel.querySelectorAll('.rt-i.cur').length);
        }
      }

      if (document.getElementById('q')) {
        ensureIndex(function () {
          try {
            runSearch('前缀和');
            var wrap = document.getElementById('srWrap');
            var first = wrap.querySelector('.sr-hit');
            log.push('title=' + wrap.querySelectorAll('.sr-title').length);
            log.push('hit=' + wrap.querySelectorAll('.sr-hit').length);
            log.push('tocHidden=' + document.getElementById('tocWrap').hidden);
            log.push('href=' + (first ? first.getAttribute('href') : 'none'));
            log.push('marks=' + wrap.querySelectorAll('mark.sr-mk').length);
            log.push('docs=' + (window.SEARCH_DOCS || []).length);
          } catch (e) { log.push('SRERR:' + e.message); }
          done();
        });
        return;
      }

      var pnl = document.getElementById('rtoc');
      if (pnl && !pnl.classList.contains('open')) {
        var tb = document.getElementById('rtTab');
        if (tb) { tb.click(); log.push('rtOpen=' + pnl.classList.contains('open')); }
      }
    } catch (e) { log.push('ERR:' + e.message); }
    done();
  }

  window.__ac = { isLearned: isLearned, isCh2: isCh2, put: put, markOf: markOf };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
