/* 微积分精讲 · 站点脚本
   负责：侧边栏、进度（localStorage）、上下节导航、图像绘制、目录页交互。 */
(function () {
  'use strict';

  var SCRIPT = document.currentScript;
  var BASE = SCRIPT ? SCRIPT.src.replace(/assets\/app\.js.*$/, '') : '';
  var MOD = window.MODULE || {};
  function mod(k, d) { return (MOD && MOD[k]) ? MOD[k] : d; }
  var STORE = mod('progressKey', 'lg.progress.v1');
  var UI = mod('uiKey', 'lg.ui.v1');
  var memStore = null;

  (function () {
    var m = document.createElement('meta');
    m.name = 'color-scheme';
    m.content = 'light dark';
    document.head.appendChild(m);
  })();

  /* ---------- 数据 ---------- */
  var CURRICULUM = window.CURRICULUM || null;
  var FLAT = [];

  function flatten() {
    FLAT = [];
    CURRICULUM.forEach(function (ch) {
      ch.sections.forEach(function (s) {
        FLAT.push({ id: s.id, title: s.title, core: s.core, diff: s.diff, ch: ch.n, chTitle: ch.title });
      });
    });
  }

  /* ---------- 进度存取 ---------- */
  function readStore(k) {
    try { return JSON.parse(localStorage.getItem(k)) || {}; }
    catch (e) { return memStore ? memStore[k] || {} : {}; }
  }
  function writeStore(k, v) {
    try { localStorage.setItem(k, JSON.stringify(v)); }
    catch (e) { memStore = memStore || {}; memStore[k] = v; }
  }
  var progress = readStore(STORE);
  var storageOK = (function () {
    try { localStorage.setItem('__t', '1'); localStorage.removeItem('__t'); return true; }
    catch (e) { return false; }
  })();

  function isDone(id) { return !!progress[id]; }
  function doneCount() { return FLAT.filter(function (s) { return isDone(s.id); }).length; }

  function setDone(id, on) {
    if (on) progress[id] = Date.now(); else delete progress[id];
    writeStore(STORE, progress);
    sync();
    document.dispatchEvent(new CustomEvent('progresschange', { detail: { id: id, done: on } }));
  }

  /* ---------- 全站状态同步 ---------- */
  function sync() {
    var n = doneCount(), total = FLAT.length || 1;
    document.querySelectorAll('[data-check]').forEach(function (el) {
      var id = el.getAttribute('data-check');
      var on = isDone(id);
      if (el.tagName === 'INPUT') el.checked = on;
      var row = el.closest('.sb-item, .card, .sec-row');
      if (row) row.classList.toggle('is-done', on);
      var star = row ? row.querySelector('[data-star]') : null;
      if (star) star.style.display = on ? '' : 'none';
    });
    document.querySelectorAll('[data-count]').forEach(function (el) {
      el.textContent = n + ' / ' + total;
    });
    document.querySelectorAll('[data-chcount]').forEach(function (el) {
      var ch = +el.getAttribute('data-chcount');
      var c = CURRICULUM.filter(function (x) { return x.n === ch; })[0];
      if (!c) return;
      var d = c.sections.filter(function (s) { return isDone(s.id); }).length;
      el.textContent = d + '/' + c.sections.length;
      el.classList.toggle('full', d === c.sections.length);
    });
    document.querySelectorAll('[data-chbar]').forEach(function (el) {
      var ch = +el.getAttribute('data-chbar');
      var c = CURRICULUM.filter(function (x) { return x.n === ch; })[0];
      if (!c) return;
      var d = c.sections.filter(function (s) { return isDone(s.id); }).length;
      el.style.width = (100 * d / c.sections.length).toFixed(1) + '%';
    });
    document.querySelectorAll('[data-bar]').forEach(function (el) {
      el.style.width = (100 * n / total).toFixed(2) + '%';
    });
    document.querySelectorAll('[data-ring]').forEach(function (el) {
      var r = +el.getAttribute('r') || 34;
      var C = 2 * Math.PI * r;
      el.style.strokeDasharray = C;
      el.style.strokeDashoffset = C * (1 - n / total);
    });
    var ringTxt = document.querySelector('[data-ringtext]');
    if (ringTxt) ringTxt.textContent = Math.round(100 * n / total) + '%';

    var body = document.body;
    if (body.hasAttribute('data-sec')) {
      var id = body.getAttribute('data-sec');
      var on = isDone(id);
      body.classList.toggle('is-done', on);
      var btn = document.querySelector('[data-toggle-done]');
      if (btn) {
        btn.setAttribute('aria-pressed', on ? 'true' : 'false');
        btn.querySelector('.lbl').textContent = on ? '已完成' : '标记完成';
      }
      var clean = document.title.replace(/^⭐\s*/, '');
      document.title = on ? '⭐ ' + clean : clean;
    }
    var warn = document.querySelector('[data-storage-warn]');
    if (warn) warn.style.display = storageOK ? 'none' : '';
  }

  /* ---------- 主题 ---------- */
  var THEME_KEY = mod('themeKey', 'lg.theme');

  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function sysDark() {
    try { return window.matchMedia('(prefers-color-scheme: dark)').matches; } catch (e) { return false; }
  }
  function themeNow() {
    var t = document.documentElement.getAttribute('data-theme');
    return (t === 'light' || t === 'dark') ? t : (sysDark() ? 'dark' : 'light');
  }
  function paintThemeBtns() {
    var dark = themeNow() === 'dark';
    document.querySelectorAll('[data-theme-toggle]').forEach(function (b) {
      b.innerHTML = dark ? ICON.sun : ICON.moon;
      b.setAttribute('aria-label', dark ? '切换到浅色' : '切换到深色');
      b.setAttribute('title', dark ? '切换到浅色' : '切换到深色');
      b.setAttribute('aria-pressed', dark ? 'true' : 'false');
    });
  }
  function repaintPlots() {
    document.querySelectorAll('figure.plot').forEach(function (f) {
      var svg = f.querySelector('svg');
      if (svg) svg.parentNode.removeChild(svg);
    });
    themePalette();
    initFigures();
  }
  function initTheme() {
    document.querySelectorAll('[data-theme-toggle]').forEach(function (b) {
      if (b.getAttribute('data-wired')) return;
      b.setAttribute('data-wired', '1');
      b.addEventListener('click', function () {
        var next = themeNow() === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        document.documentElement.style.colorScheme = next;
        try { localStorage.setItem(THEME_KEY, next); } catch (e) { /* 忽略 */ }
        paintThemeBtns();
        repaintPlots();
      });
    });
    paintThemeBtns();
    try {
      if (!localStorage.getItem(THEME_KEY) && window.matchMedia) {
        matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function () {
          paintThemeBtns();
          repaintPlots();
        });
      }
    } catch (e) { /* 忽略 */ }
  }

  /* ---------- 图标 ---------- */
  var ICON = {
    menu: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 6h18M3 12h18M3 18h18"/></svg>',
    left: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M15 5l-7 7 7 7"/></svg>',
    right: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 5l7 7-7 7"/></svg>',
    star: '<svg viewBox="0 0 24 24" width="13" height="13" fill="currentColor"><path d="M12 2.6l2.9 5.9 6.5.9-4.7 4.6 1.1 6.5L12 17.4 6.2 20.5l1.1-6.5L2.6 9.4l6.5-.9z"/></svg>',
    sun: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.2 5.2l1.6 1.6M17.2 17.2l1.6 1.6M18.8 5.2l-1.6 1.6M6.8 17.2l-1.6 1.6"/></svg>',
    moon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M20 14.6A8.2 8.2 0 0 1 9.4 4a8.4 8.4 0 1 0 10.6 10.6z"/></svg>',
    rail: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M4 6h16M4 12h10M4 18h13"/><path d="M20 9.5v5" stroke-width="2.2"/></svg>'
  };

  /* ---------- 页面骨架 ---------- */
  function buildChrome() {
    var content = document.querySelector('main.content');
    if (!content) return null;

    var aside = document.createElement('aside');
    aside.className = 'sidebar';
    aside.id = 'sidebar';
    aside.innerHTML =
      '<div class="sb-head">' +
        '<a class="brand" href="' + BASE + 'index.html"><span class="brand-mark">' + esc(mod('mark', '▦')) + '</span><span class="brand-txt">' + esc(mod('title', '学习模块')) + '<em>' + esc(mod('subtitle', 'Learning Module')) + '</em></span></a>' +
        '<div class="sb-meter"><div class="meter"><i data-bar></i></div><span class="meter-txt" data-count></span></div>' +
      '</div>' +
      '<nav class="sb-nav" aria-label="目录"></nav>' +
      '<div class="sb-foot"><a href="' + BASE + 'index.html">全目录</a><span>·</span><a href="#" data-export>导出进度</a></div>';

    var nav = aside.querySelector('.sb-nav');
    nav.innerHTML = CURRICULUM.map(function (ch) {
      var items = ch.sections.map(function (s) {
        return '<li class="sb-item" data-id="' + s.id + '">' +
          '<input type="checkbox" data-check="' + s.id + '" aria-label="标记 ' + s.id + ' 完成">' +
          '<a href="' + BASE + 'sections/' + s.id.replace('.', '-') + '.html">' +
            '<span class="sb-id">' + s.id + '</span>' +
            '<span class="sb-title">' + s.title + '</span>' +
            '<span class="sb-star" data-star style="display:none">' + ICON.star + '</span>' +
          '</a></li>';
      }).join('');
      return '<section class="sb-ch" data-ch="' + ch.n + '">' +
        '<button class="sb-chh" type="button" aria-expanded="true">' +
          '<span class="sb-chn">' + ch.n + '</span>' +
          '<span class="sb-chtt">' + ch.title + '</span>' +
          '<span class="sb-chc" data-chcount="' + ch.n + '">0/0</span>' +
          '<span class="chev"></span>' +
        '</button>' +
        '<ul class="sb-list">' + items + '</ul>' +
      '</section>';
    }).join('');

    var wrap = document.createElement('div');
    wrap.className = 'main';
    var top = document.createElement('header');
    top.className = 'topbar';
    top.innerHTML =
      '<button class="icon-btn only-mobile" data-menu type="button" aria-label="目录">' + ICON.menu + '</button>' +
      '<div class="crumbs"></div>' +
      '<div class="top-actions">' +
        '<button class="icon-btn rail-btn" data-rail-toggle type="button" aria-label="本节目录" title="本节目录">' + ICON.rail + '</button>' +
        '<button class="icon-btn theme-btn" data-theme-toggle type="button" aria-label="切换深浅色" title="切换深浅色">' + ICON.moon + '</button>' +
        '<button class="done-toggle" data-toggle-done type="button" aria-pressed="false">' +
          '<span class="box"></span><span class="lbl">标记完成</span><span class="star-inline">' + ICON.star + '</span></button>' +
      '</div>';

    content.parentNode.insertBefore(aside, content);
    content.parentNode.insertBefore(wrap, content);
    wrap.appendChild(top);
    wrap.appendChild(content);

    var veil = document.createElement('div');
    veil.className = 'veil';
    veil.setAttribute('data-veil', '');
    document.body.appendChild(veil);
    return { aside: aside, top: top, content: content };
  }

  function sidebarBehavior(aside) {
    var cur = document.body.getAttribute('data-sec');
    var ui = readStore(UI);

    aside.querySelectorAll('.sb-chh').forEach(function (btn) {
      var ch = btn.parentNode.getAttribute('data-ch');
      var collapsed = !!ui['c' + ch];
      btn.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
      btn.parentNode.classList.toggle('collapsed', collapsed);
      btn.addEventListener('click', function () {
        var now = !btn.parentNode.classList.contains('collapsed');
        btn.parentNode.classList.toggle('collapsed', now);
        btn.setAttribute('aria-expanded', now ? 'false' : 'true');
        var u = readStore(UI); if (now) u['c' + ch] = 1; else delete u['c' + ch]; writeStore(UI, u);
      });
    });

    var curItem = aside.querySelector('.sb-item[data-id="' + cur + '"]');
    if (curItem) {
      curItem.classList.add('current');
      var chBox = curItem.closest('.sb-ch');
      if (chBox) chBox.classList.remove('collapsed');
      setTimeout(function () {
        var r = curItem.getBoundingClientRect();
        if (r.top < 80 || r.bottom > window.innerHeight - 40) curItem.scrollIntoView({ block: 'center' });
      }, 30);
    }

    var menuBtn = document.querySelector('[data-menu]');
    var veil = document.querySelector('[data-veil]');
    function close() { document.body.classList.remove('nav-open'); }
    if (menuBtn) menuBtn.addEventListener('click', function () { document.body.classList.toggle('nav-open'); });
    if (veil) veil.addEventListener('click', close);
    var link = veil;
    aside.addEventListener('click', function (e) { if (e.target.closest('a')) close(); });
  }

  function crumbsAndPager(content) {
    var id = document.body.getAttribute('data-sec');
    var idx = FLAT.findIndex(function (s) { return s.id === id; });
    if (idx < 0) return;
    var s = FLAT[idx];
    var crumbs = document.querySelector('.crumbs');
    if (crumbs) {
      crumbs.innerHTML = '<span class="cb-ch">第 ' + s.ch + ' 章 · ' + s.chTitle + '</span>' +
        '<span class="cb-sep">/</span><span class="cb-sec">§' + s.id + '</span>';
    }
    var prev = FLAT[idx - 1], next = FLAT[idx + 1];
    var nav = document.createElement('nav');
    nav.className = 'pager';
    nav.innerHTML =
      (prev ? '<a class="pg prev" href="' + prev.id.replace('.', '-') + '.html"><span class="dir">' + ICON.left + ' 上一节</span><b>§' + prev.id + '　' + prev.title + '</b></a>' : '<span class="pg empty"></span>') +
      (next ? '<a class="pg next" href="' + next.id.replace('.', '-') + '.html"><span class="dir">下一节 ' + ICON.right + '</span><b>§' + next.id + '　' + next.title + '</b></a>' : '<a class="pg next" href="' + BASE + 'index.html"><span class="dir">回到目录 ' + ICON.right + '</span><b>课程目录</b></a>');
    content.appendChild(nav);

    document.addEventListener('keydown', function (e) {
      if (e.target.matches('input, textarea, select')) return;
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      if (e.key === 'ArrowLeft' && prev) location.href = prev.id.replace('.', '-') + '.html';
      if (e.key === 'ArrowRight' && next) location.href = next.id.replace('.', '-') + '.html';
    });
  }

  function pageRail(content) {
    var heads = Array.prototype.slice.call(content.querySelectorAll('h2[id], h3'));
    if (heads.length < 2) return;
    heads.forEach(function (h, i) { if (!h.id) h.id = 'h-' + i; });

    var lede = content.querySelector('.lede');
    var items = heads.map(function (h) {
      var lv = h.tagName === 'H2' ? 2 : 3;
      var clone = h.cloneNode(true);
      var num = clone.querySelector('.num');
      if (num) num.parentNode.removeChild(num);
      var label = clone.textContent.replace(/\s+/g, ' ').trim();
      return '<li class="lv' + lv + '"><a href="#' + h.id + '">' + esc(label) + '</a></li>';
    }).join('');

    var rail = document.createElement('aside');
    rail.className = 'rail';
    rail.id = 'rail';
    rail.setAttribute('aria-label', '本节目录');
    rail.innerHTML =
      '<div class="rail-h"><b>本节</b><button class="rail-x" type="button" data-rail-close aria-label="收起">×</button></div>' +
      '<div class="rail-body">' +
        (lede ? '<div class="rail-ov">' + lede.innerHTML + '</div>' : '') +
        '<ul>' + items + '</ul>' +
      '</div>';
    document.body.appendChild(rail);

    var veil = document.createElement('div');
    veil.className = 'rail-veil';
    veil.setAttribute('data-rail-veil', '');
    document.body.appendChild(veil);

    var ui = readStore(UI);
    if (ui.railoff === 1) document.body.classList.add('rail-off');

    var wide = window.matchMedia('(min-width:1420px)');
    function setOff(off) {
      document.body.classList.toggle('rail-off', off);
      var u = readStore(UI);
      if (off) u.railoff = 1; else delete u.railoff;
      writeStore(UI, u);
      paintRailBtn();
    }
    function closeDrawer() { document.body.classList.remove('rail-open'); paintRailBtn(); }
    function paintRailBtn() {
      var b = document.querySelector('[data-rail-toggle]');
      if (!b) return;
      var open = wide.matches ? !document.body.classList.contains('rail-off')
                              : document.body.classList.contains('rail-open');
      b.setAttribute('aria-pressed', open ? 'true' : 'false');
    }
    var btn = document.querySelector('[data-rail-toggle]');
    if (btn) {
      btn.addEventListener('click', function () {
        if (wide.matches) setOff(!document.body.classList.contains('rail-off'));
        else { document.body.classList.toggle('rail-open'); paintRailBtn(); }
      });
    }
    var x = rail.querySelector('[data-rail-close]');
    if (x) x.addEventListener('click', function () {
      if (wide.matches) setOff(true); else closeDrawer();
    });
    veil.addEventListener('click', closeDrawer);

    rail.addEventListener('click', function (e) {
      var a = e.target.closest('a');
      if (!a) return;
      var el = document.getElementById(a.getAttribute('href').slice(1));
      if (el) {
        var p = el.parentNode;
        while (p && p.nodeType === 1) {
          if (p.tagName === 'DETAILS' && !p.open) p.open = true;
          p = p.parentNode;
        }
      }
      if (!wide.matches) closeDrawer();
    });

    var links = rail.querySelectorAll('a');
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          links.forEach(function (a) { a.classList.toggle('on', a.getAttribute('href') === '#' + en.target.id); });
        }
      });
    }, { rootMargin: '-12% 0px -72% 0px' });
    heads.forEach(function (h) { obs.observe(h); });
    paintRailBtn();
  }

  function doneToggle() {
    var btn = document.querySelector('[data-toggle-done]');
    var id = document.body.getAttribute('data-sec');
    if (!btn || !id) return;
    btn.addEventListener('click', function () { setDone(id, !isDone(id)); });
  }

  /* ---------- 图像 ---------- */
  var PALETTE = ['#1f4e79', '#a5432d', '#2f6b4f', '#6b4e9e', '#8a6d1f'];
  function themePalette() {
    try {
      var cs = getComputedStyle(document.documentElement);
      var out = [1, 2, 3, 4, 5].map(function (i) { return cs.getPropertyValue('--p' + i).trim(); });
      if (out.every(Boolean)) PALETTE = out;
    } catch (e) { /* 保留默认色 */ }
  }
  var NS = 'http://www.w3.org/2000/svg';

  function el(tag, attrs, parent) {
    var n = document.createElementNS(NS, tag);
    for (var k in attrs) if (attrs[k] !== undefined && attrs[k] !== null) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }
  function powify(src) {
    var s = String(src), guard = 0;
    while (s.indexOf('^') >= 0 && guard++ < 80) {
      var i = s.lastIndexOf('^');
      var j = i - 1;
      while (j >= 0 && s[j] === ' ') j--;
      var baseStart;
      if (s[j] === ')') {
        var depth = 0, k = j;
        for (; k >= 0; k--) {
          if (s[k] === ')') depth++;
          else if (s[k] === '(') { depth--; if (!depth) break; }
        }
        baseStart = k;
        if (baseStart > 0 && /[A-Za-z_]/.test(s[baseStart - 1])) {
          var mf = /[A-Za-z_][A-Za-z0-9_]*$/.exec(s.slice(0, baseStart));
          if (mf) baseStart -= mf[0].length;
        }
      } else {
        var mb = /[A-Za-z0-9_.]+$/.exec(s.slice(0, j + 1));
        baseStart = mb ? j + 1 - mb[0].length : j;
      }
      var e = i + 1;
      while (e < s.length && s[e] === ' ') e++;
      var sign = '';
      if (s[e] === '-' || s[e] === '+') { sign = s[e] === '-' ? '-' : ''; e++; }
      var expEnd;
      if (s[e] === '(') {
        var d2 = 0;
        for (expEnd = e; expEnd < s.length; expEnd++) {
          if (s[expEnd] === '(') d2++;
          else if (s[expEnd] === ')') { d2--; if (!d2) { expEnd++; break; } }
        }
      } else {
        var me = /^[A-Za-z0-9_.]+/.exec(s.slice(e));
        expEnd = e + (me ? me[0].length : 1);
      }
      var exp = sign + s.slice(e, expEnd);
      s = s.slice(0, baseStart) + 'pow(' + s.slice(baseStart, i) + ',' + exp + ')' + s.slice(expEnd);
    }
    return s;
  }

  function compile(expr) {
    var body = powify(String(expr))
      .replace(/\bln\b/g, 'log').replace(/\bpi\b/g, 'PI');
    var f;
    try {
      f = new Function('x', 'y',
        'var sin=Math.sin,cos=Math.cos,tan=Math.tan,asin=Math.asin,acos=Math.acos,atan=Math.atan,' +
        'atan2=Math.atan2,exp=Math.exp,log=Math.log,sqrt=Math.sqrt,abs=Math.abs,PI=Math.PI,E=Math.E,' +
        'sign=Math.sign,pow=Math.pow,min=Math.min,max=Math.max,floor=Math.floor,ceil=Math.ceil,' +
        'sinh=Math.sinh,cosh=Math.cosh,tanh=Math.tanh;return (' + body + ');');
    } catch (e) { f = function () { return NaN; }; }
    return function (x, y) { try { var v = f(x, y); return (typeof v === 'number' && isFinite(v)) ? v : NaN; } catch (e) { return NaN; } };
  }
  function niceStep(span, target) {
    var raw = span / target, p = Math.pow(10, Math.floor(Math.log10(raw))), n = raw / p;
    var m = n <= 1 ? 1 : n <= 2 ? 2 : n <= 2.5 ? 2.5 : n <= 5 ? 5 : 10;
    return m * p;
  }
  function ticks(min, max, target) {
    var step = niceStep(max - min, target), out = [], v = Math.ceil(min / step) * step;
    for (; v <= max + step * 1e-6; v += step) out.push(Math.abs(v) < step * 1e-6 ? 0 : v);
    return { list: out, step: step };
  }
  function fmt(v) {
    if (Math.abs(v) < 1e-9) return '0';
    var a = Math.abs(v);
    if (a >= 1e4 || a < 1e-3) return v.toExponential(1).replace('e+', 'e');
    return String(Math.round(v * 1e6) / 1e6);
  }
  function numList(s, dflt) {
    if (!s) return dflt;
    return s.split(/[,;]/).map(function (t) { return parseFloat(t); });
  }

  function drawPlot(fig) {
    var W = 560, H = 340, P = { l: 48, r: 22, t: 16, b: 36 };
    var exprs = (fig.getAttribute('data-fn') || '').split(';').map(function (s) { return s.trim(); }).filter(Boolean);
    if (!exprs.length) return;
    var fns = exprs.map(compile);
    var iw = W - P.l - P.r, ih = H - P.t - P.b;

    var xr = numList(fig.getAttribute('data-x'), null);
    if (!xr || xr.length < 2) {
      var guess = 3;
      var pass = fig.getAttribute('data-pass');
      if (pass) guess = parseFloat(pass) / 2;
      xr = [-guess, guess];
    }
    var yr = numList(fig.getAttribute('data-y'), null);
    if (!yr || yr.length < 2) {
      var lo = Infinity, hi = -Infinity, vals = [];
      for (var i = 0; i <= 400; i++) {
        var x = xr[0] + (xr[1] - xr[0]) * i / 400;
        fns.forEach(function (f) { var v = f(x); if (isFinite(v)) vals.push(v); });
      }
      vals.sort(function (a, b) { return a - b; });
      if (vals.length) {
        var q1 = vals[Math.floor(vals.length * 0.02)], q9 = vals[Math.floor(vals.length * 0.98)];
        lo = Math.min(0, q1); hi = Math.max(0, q9);
        var pad = (hi - lo) * 0.12 || 1; lo -= pad; hi += pad;
      } else { lo = -1; hi = 1; }
      yr = [lo, hi];
    }
    var X = function (x) { return P.l + (x - xr[0]) / (xr[1] - xr[0]) * iw; };
    var Y = function (y) { return P.t + ih - (y - yr[0]) / (yr[1] - yr[0]) * ih; };

    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, class: 'plot-svg', role: 'img' });
    var defs = el('defs', {}, svg);
    var cp = el('clipPath', { id: 'cp' + Math.random().toString(36).slice(2, 8) }, defs);
    el('rect', { x: P.l, y: P.t, width: iw, height: ih }, cp);
    var clipUrl = 'url(#' + cp.getAttribute('id') + ')';
    var g = el('g', { 'clip-path': clipUrl }, svg);

    var tx = ticks(xr[0], xr[1], 8), ty = ticks(yr[0], yr[1], 5);
    tx.list.forEach(function (v) {
      el('line', { x1: X(v), y1: P.t, x2: X(v), y2: P.t + ih, class: 'grid' }, g);
      var t = el('text', { x: X(v), y: P.t + ih + 16, class: 'tick', 'text-anchor': 'middle' }, svg);
      t.textContent = fmt(v);
    });
    ty.list.forEach(function (v) {
      el('line', { x1: P.l, y1: Y(v), x2: P.l + iw, y2: Y(v), class: 'grid' }, g);
      var t = el('text', { x: P.l - 8, y: Y(v) + 3.5, class: 'tick', 'text-anchor': 'end' }, svg);
      t.textContent = fmt(v);
    });

    /* 区域着色 */
    function area(pathFn, fill, opacity) {
      if (!pathFn) return;
      el('path', { d: pathFn, fill: fill, 'fill-opacity': opacity || 0.13, stroke: 'none' }, g);
    }
    var fillSpec = fig.getAttribute('data-fill');
    if (fillSpec) {
      var ab = numList(fillSpec, [0, 1]);
      area(curveArea(fns[0], ab[0], ab[1]), PALETTE[0], 0.14);
    }
    var betw = fig.getAttribute('data-between');
    if (betw && fns.length > 1) {
      var ab2 = numList(betw, [0, 1]);
      area(betweenArea(fns[0], fns[1], ab2[0], ab2[1]), PALETTE[2], 0.14);
    }
    var rectSpec = fig.getAttribute('data-rect');
    if (rectSpec) {
      var p = rectSpec.split(',');
      var n = parseInt(p[0], 10) || 8, a = parseFloat(p[1]), b = parseFloat(p[2]);
      var side = p[3] || 'left';
      var w = (b - a) / n;
      for (var k = 0; k < n; k++) {
        var xl = a + k * w, xm = xl + w / 2;
        var xs = side === 'mid' ? xm : (side === 'right' ? xl + w : xl);
        var h = fns[0](side === 'mid' ? xm : xs);
        if (!isFinite(h)) continue;
        var y0 = Y(0), y1 = Y(h);
        var r = el('rect', {
          x: X(xl), y: Math.min(y0, y1), width: Math.max(0.5, X(xl + w) - X(xl)),
          height: Math.abs(y1 - y0), class: 'riem'
        }, g);
        r.setAttribute('fill-opacity', '0.16');
      }
    }

    /* 曲线 */
    fns.forEach(function (f, i) {
      var d = '';
      var N = 700, started = false, prevBad = true;
      for (var j = 0; j <= N; j++) {
        var x = xr[0] + (xr[1] - xr[0]) * j / N, y = f(x);
        var ok = isFinite(y) && y > yr[0] - (yr[1] - yr[0]) * 2 && y < yr[1] + (yr[1] - yr[0]) * 2;
        if (!ok) { started = false; prevBad = true; continue; }
        var px = X(x).toFixed(2), py = Y(y).toFixed(2);
        if (!started) { d += 'M' + px + ',' + py; started = true; }
        else {
          var jump = Math.abs(y - f(x - (xr[1] - xr[0]) / N)) > (yr[1] - yr[0]) * 1.5;
          d += (jump ? 'M' : 'L') + px + ',' + py;
        }
        prevBad = false;
      }
      el('path', { d: d, fill: 'none', stroke: PALETTE[i % PALETTE.length], 'stroke-width': 2, 'stroke-linecap': 'round', class: 'curve' }, g);
    });

    function curveArea(f, a, b) {
      var pts = [], N = 200;
      for (var j = 0; j <= N; j++) {
        var x = a + (b - a) * j / N, y = f(x);
        if (!isFinite(y)) continue;
        pts.push([X(x), Y(y)]);
      }
      if (pts.length < 2) return null;
      var y0 = Y(0);
      var d = 'M' + pts[0][0] + ',' + y0 + 'L' + pts.map(function (q) { return q[0] + ',' + q[1]; }).join('L') +
        'L' + pts[pts.length - 1][0] + ',' + y0 + 'Z';
      return d;
    }
    function betweenArea(f, gg, a, b) {
      var up = [], dn = [], N = 200;
      for (var j = 0; j <= N; j++) {
        var x = a + (b - a) * j / N, y1 = f(x), y2 = gg(x);
        if (!isFinite(y1) || !isFinite(y2)) continue;
        up.push([X(x), Math.min(Y(y1), Y(y2))]);
        dn.push([X(x), Math.max(Y(y1), Y(y2))]);
      }
      if (up.length < 2) return null;
      return 'M' + up[0][0] + ',' + up[0][1] + 'L' + up.slice(1).map(function (q) { return q[0] + ',' + q[1]; }).join('L') +
        'L' + dn.reverse().map(function (q) { return q[0] + ',' + q[1]; }).join('L') + 'Z';
    }

    /* 坐标轴 */
    if (yr[0] <= 0 && yr[1] >= 0) el('line', { x1: P.l, y1: Y(0), x2: P.l + iw, y2: Y(0), class: 'axis' }, g);
    if (xr[0] <= 0 && xr[1] >= 0) el('line', { x1: X(0), y1: P.t, x2: X(0), y2: P.t + ih, class: 'axis' }, g);
    el('rect', { x: P.l, y: P.t, width: iw, height: ih, fill: 'none', class: 'frame' }, svg);
    var xlx = P.l + iw - 2, xly = (yr[0] <= 0 && yr[1] >= 0) ? Y(0) - 7 : P.t + ih - 8;
    var xl = el('text', { x: xlx, y: xly, class: 'axlab', 'text-anchor': 'end' }, svg); xl.textContent = 'x';
    var ylx = (xr[0] <= 0 && xr[1] >= 0) ? X(0) + 8 : P.l + 10;
    var yl = el('text', { x: ylx, y: P.t + 12, class: 'axlab' }, svg); yl.textContent = 'y';

    /* 切线 / 割线 */
    function lineThrough(x0, slope, color) {
      var y0 = fns[0](x0);
      if (!isFinite(y0) || !isFinite(slope)) return;
      var dx = (xr[1] - xr[0]) * 0.32;
      el('line', {
        x1: X(x0 - dx), y1: Y(y0 - slope * dx), x2: X(x0 + dx), y2: Y(y0 + slope * dx),
        stroke: color, 'stroke-width': 1.6, 'stroke-dasharray': '6 4'
      }, g);
      el('circle', { cx: X(x0), cy: Y(y0), r: 3.6, fill: color }, g);
      el('line', { x1: X(x0), y1: Y(y0), x2: X(x0), y2: Y(0), class: 'drop' }, g);
    }
    var tan = fig.getAttribute('data-tangent');
    if (tan) {
      var x0 = parseFloat(tan), h = 1e-5;
      lineThrough(x0, (fns[0](x0 + h) - fns[0](x0 - h)) / (2 * h), PALETTE[1]);
    }
    var sec = fig.getAttribute('data-secant');
    if (sec) {
      var ab3 = numList(sec, [0, 1]);
      var m = (fns[0](ab3[1]) - fns[0](ab3[0])) / (ab3[1] - ab3[0]);
      var y0s = fns[0](ab3[0]);
      el('line', { x1: X(ab3[0]), y1: Y(y0s), x2: X(ab3[1]), y2: Y(fns[0](ab3[1])), stroke: PALETTE[1], 'stroke-width': 1.6 }, g);
      [ab3[0], ab3[1]].forEach(function (xx) {
        el('circle', { cx: X(xx), cy: Y(fns[0](xx)), r: 3.2, fill: PALETTE[1] }, g);
      });
    }

    /* 竖线、水平线 */
    (fig.getAttribute('data-vline') || '').split(';').filter(Boolean).forEach(function (s) {
      var v = parseFloat(s);
      el('line', { x1: X(v), y1: P.t, x2: X(v), y2: P.t + ih, class: 'dash-line' }, g);
    });
    (fig.getAttribute('data-hline') || '').split(';').filter(Boolean).forEach(function (s) {
      var v = parseFloat(s);
      el('line', { x1: P.l, y1: Y(v), x2: P.l + iw, y2: Y(v), class: 'dash-line' }, g);
    });

    /* ε-δ 图 */
    var eps = fig.getAttribute('data-eps');
    if (eps) {
      var e4 = numList(eps, null);
      if (e4 && e4.length >= 4) {
        var ex0 = e4[0], L = e4[1], ee = e4[2], dd = e4[3];
        el('rect', { x: X(ex0 - dd), y: Y(L + ee), width: X(ex0 + dd) - X(ex0 - dd), height: Y(L - ee) - Y(L + ee), class: 'eps-band' }, g);
        el('rect', { x: X(ex0 - dd), y: P.t, width: X(ex0 + dd) - X(ex0 - dd), height: ih, class: 'delta-band' }, g);
        el('line', { x1: P.l, y1: Y(L), x2: P.l + iw, y2: Y(L), class: 'dash-line' }, g);
        el('line', { x1: X(ex0), y1: P.t, x2: X(ex0), y2: P.t + ih, class: 'dash-line' }, g);
        el('circle', { cx: X(ex0), cy: Y(L), r: 3.4, fill: PALETTE[1] }, g);
      }
    }

    /* 点 */
    var dots = fig.getAttribute('data-dots');
    if (dots) {
      var labs = (fig.getAttribute('data-dotlabels') || '').split(';');
      dots.split(';').filter(Boolean).forEach(function (s, i) {
        var q = s.split(',').map(parseFloat);
        if (!isFinite(q[0]) || !isFinite(q[1])) return;
        el('circle', { cx: X(q[0]), cy: Y(q[1]), r: 3.6, fill: PALETTE[1] }, g);
        if (labs[i]) {
          var t = el('text', { x: X(q[0]) + 7, y: Y(q[1]) - 8, class: 'dotlab' }, svg);
          t.textContent = labs[i];
        }
      });
    }

    /* 图例 */
    var legend = (fig.getAttribute('data-legend') || '').split(';');
    if (legend.length) {
      var lg = el('g', { class: 'legend' }, svg);
      legend.forEach(function (txt, i) {
        if (!txt) return;
        var y = P.t + 10 + i * 16;
        el('line', { x1: P.l + iw - 118, y1: y - 3, x2: P.l + iw - 100, y2: y - 3, stroke: PALETTE[i % PALETTE.length], 'stroke-width': 2 }, lg);
        var t = el('text', { x: P.l + iw - 94, y: y, class: 'legend-t' }, lg);
        t.textContent = txt;
      });
    }

    fig.insertBefore(svg, fig.firstChild);
  }

  function drawField(fig) {
    var W = 560, H = 340, P = { l: 40, r: 20, t: 16, b: 34 };
    var f = compile(fig.getAttribute('data-fn') || 'x');
    var xr = numList(fig.getAttribute('data-x'), [-3, 3]);
    var yr = numList(fig.getAttribute('data-y'), [-2, 2]);
    var iw = W - P.l - P.r, ih = H - P.t - P.b;
    var X = function (x) { return P.l + (x - xr[0]) / (xr[1] - xr[0]) * iw; };
    var Y = function (y) { return P.t + ih - (y - yr[0]) / (yr[1] - yr[0]) * ih; };
    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, class: 'plot-svg', role: 'img' });
    var g = el('g', {}, svg);
    el('rect', { x: P.l, y: P.t, width: iw, height: ih, class: 'frame', fill: 'none' }, svg);
    if (yr[0] <= 0 && yr[1] >= 0) el('line', { x1: P.l, y1: Y(0), x2: P.l + iw, y2: Y(0), class: 'axis' }, g);
    if (xr[0] <= 0 && xr[1] >= 0) el('line', { x1: X(0), y1: P.t, x2: X(0), y2: P.t + ih, class: 'axis' }, g);
    var nx = Math.max(6, Math.round(iw / 26)), ny = Math.max(5, Math.round(ih / 26));
    var stepX = (xr[1] - xr[0]) / nx, stepY = (yr[1] - yr[0]) / ny;
    var len = Math.min(iw / nx, ih / ny) * 0.38;
    var scale = (ih / (yr[1] - yr[0])) / (iw / (xr[1] - xr[0]));
    for (var gi = 0; gi < nx; gi++) {
      for (var gj = 0; gj < ny; gj++) {
        var xv = xr[0] + (gi + 0.5) * stepX, yv = yr[0] + (gj + 0.5) * stepY;
        var m = f(xv, yv);
        if (!isFinite(m)) continue;
        var sp = -m * scale;
        var nrm = Math.sqrt(1 + sp * sp);
        var ax = len / nrm, ay = sp * len / nrm;
        el('line', { x1: X(xv) - ax, y1: Y(yv) - ay, x2: X(xv) + ax, y2: Y(yv) + ay, class: 'field-seg' }, g);
      }
    }
    fig.insertBefore(svg, fig.firstChild);
  }

  function drawLine(fig) {
    var W = 560, H = 120, P = { l: 34, r: 34, t: 44, b: 44 };
    var rng = numList(fig.getAttribute('data-range'), [-3, 4]);
    var X = function (x) { return P.l + (x - rng[0]) / (rng[1] - rng[0]) * (W - P.l - P.r); };
    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, class: 'plot-svg line-svg', role: 'img' });
    var g = el('g', {}, svg);
    el('line', { x1: P.l, y1: 60, x2: W - P.r, y2: 60, class: 'axis' }, g);
    el('path', { d: 'M' + (W - P.r) + ',56 l8,4 -8,4 z', class: 'axis-fill' }, g);
    var tk = ticks(rng[0], rng[1], Math.max(4, Math.round((W - 80) / 70)));
    tk.list.forEach(function (v) {
      el('line', { x1: X(v), y1: 55, x2: X(v), y2: 65, class: 'axis' }, g);
      var t = el('text', { x: X(v), y: 82, class: 'tick', 'text-anchor': 'middle' }, g);
      t.textContent = fmt(v);
    });
    var iv = fig.getAttribute('data-interval');
    if (iv) {
      iv.split(';').filter(Boolean).forEach(function (sp) {
        var p = sp.split(','), a = parseFloat(p[0]), b = parseFloat(p[1]);
        el('rect', { x: X(a), y: 56, width: X(b) - X(a), height: 8, class: 'iv-bar' }, g);
      });
    }
    var pts = fig.getAttribute('data-points');
    if (pts) {
      var labs = (fig.getAttribute('data-labels') || '').split(';');
      var hollow = (fig.getAttribute('data-hollow') || '').split(';').map(parseFloat);
      pts.split(';').filter(Boolean).forEach(function (sp, i) {
        var v = parseFloat(sp);
        el('circle', { cx: X(v), cy: 60, r: 4.6, class: 'pt', 'fill-opacity': hollow.indexOf(v) >= 0 ? 0 : 1 }, g);
        if (labs[i]) {
          var t = el('text', { x: X(v), y: 38, class: 'dotlab', 'text-anchor': 'middle' }, g);
          t.textContent = labs[i];
        }
      });
    }
    fig.insertBefore(svg, fig.firstChild);
  }

  function initFigures() {
    document.querySelectorAll('figure.plot').forEach(function (fig) {
      if (fig.getAttribute('data-svg') === '1' || fig.querySelector('svg')) return;
      var type = fig.getAttribute('data-type') || 'plot';
      try {
        if (type === 'line') drawLine(fig);
        else if (type === 'field') drawField(fig);
        else drawPlot(fig);
      } catch (e) { /* 静默：坏图不拖垮整页 */ }
    });
  }

  /* ---------- 全站检索（目录页） ---------- */
  var SR = {}, IDX_READY = false, IDX_LOADING = false, IDX_CB = [], MAX_HITS = 200;

  function escRe(s) { return String(s).replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }
  function markHtml(text, q) {
    if (!q) return esc(text);
    var re = new RegExp('(' + escRe(q) + ')', 'ig');
    return esc(text).replace(re, '<mark class="sr-mk">$1</mark>');
  }
  function ensureIndex(cb) {
    if (IDX_READY || window.SEARCH_DOCS) { IDX_READY = true; cb(); return; }
    IDX_CB.push(cb);
    if (IDX_LOADING) return;
    IDX_LOADING = true;
    var s = document.createElement('script');
    s.src = BASE + 'assets/search-index.js';
    s.onload = function () {
      IDX_READY = true; IDX_LOADING = false;
      IDX_CB.splice(0).forEach(function (f) { try { f(); } catch (e) { } });
    };
    s.onerror = function () {
      IDX_LOADING = false;
      if (SR.wrap) {
        SR.wrap.innerHTML = '<div class="sr-empty">检索索引加载失败：缺少 assets/search-index.js。请在 math 目录运行 <code>python tools/site/build.py</code> 重新生成。</div>';
        SR.wrap.hidden = false;
      }
    };
    document.body.appendChild(s);
  }
  function windowAround(text, q, before, after) {
    var low = text.toLowerCase(), qq = q.toLowerCase(), p = low.indexOf(qq);
    if (p < 0) return { p: 0, pre: '', mid: text.slice(0, before), post: text.slice(before, before + after) };
    var s = Math.max(0, p - before), e = Math.min(text.length, p + qq.length + after);
    return {
      p: p,
      pre: (s > 0 ? '…' : '') + text.slice(s, p),
      mid: text.slice(p, p + qq.length),
      post: text.slice(p + qq.length, e) + (e < text.length ? '…' : '')
    };
  }
  function inMath(t, p) {
    var re = /\$\$[\s\S]*?\$\$|\$[^$]*\$/g, m;
    while ((m = re.exec(t)) !== null) {
      if (p >= m.index && p < m.index + m[0].length) return true;
      if (m.index > p) break;
    }
    return false;
  }
  function cleanSeg(s) {
    return String(s)
      .replace(/\$\$[\s\S]*?\$\$/g, '…')
      .replace(/\$[^$]{1,200}\$/g, '…')
      .replace(/\s+/g, ' ').trim();
  }
  function dimText(s, n, mode) {
    var t = cleanSeg(s);
    var x = mode === 'head' ? head(t, n) : tail(t, n);
    return x.replace(/…/g, '').trim().length < 2 ? '' : x;
  }
  function tail(t, n) { return t.length <= n ? t : '…' + t.slice(-n); }
  function head(t, n) { return t.length <= n ? t : t.slice(0, n) + '…'; }

  function runSearch(q) {
    var docs = window.SEARCH_DOCS || [], qq = q.toLowerCase();
    var titleHits = [], bodyHits = [], total = 0;
    docs.forEach(function (d) {
      var inTitle = d.t.toLowerCase().indexOf(qq) >= 0;
      var tagHit = (d.tg || []).filter(function (t) { return t.toLowerCase().indexOf(qq) >= 0; });
      if (inTitle || tagHit.length) titleHits.push({ d: d, inTitle: inTitle, tags: tagHit });
      for (var j = 0; j < d.b.length; j++) {
        if (d.b[j][2].toLowerCase().indexOf(qq) >= 0) {
          total++;
          if (bodyHits.length < MAX_HITS) bodyHits.push({ d: d, i: j });
        }
      }
    });
    titleHits.sort(function (a, b) { return (a.d.n - b.d.n) || (a.d.no < b.d.no ? -1 : 1); });
    renderResults(q, titleHits, bodyHits, total);
  }

  function renderResults(q, titleHits, bodyHits, total) {
    var out = [];
    out.push('<div class="sr-sum">检索 <b>' + esc(q) + '</b>：标题/标签命中 <b>' + titleHits.length +
      '</b> 节，正文命中 <b>' + total + '</b> 处' +
      (total > MAX_HITS ? '（只显示前 ' + MAX_HITS + ' 处，请把关键词写得更具体）' : '') + '</div>');

    if (titleHits.length) {
      out.push('<div class="sr-sec">节标题与标签命中</div><div class="sr-list">');
      titleHits.forEach(function (h) {
        var d = h.d;
        out.push('<a class="sr-title" href="' + d.f + '">' +
          '<span class="sr-no">' + esc(d.no) + '</span>' +
          '<span class="sr-tn">' + (h.inTitle ? markHtml(d.title, q) : esc(d.title)) + '</span>' +
          '<span class="sr-tag">' + esc(d.core) + '</span>' +
          (h.tags.length ? '<span class="sr-tag">标签：' + h.tags.map(function (t) { return markHtml(t, q); }).join('、') + '</span>' : '') +
          '</a>');
      });
      out.push('</div>');
    }

    if (bodyHits.length) {
      out.push('<div class="sr-sec">正文命中 · 点击跳到关键字位置</div><div class="sr-list">');
      bodyHits.forEach(function (h) {
        var d = h.d, idx = h.i, blk = d.b[idx];
        var anchor = blk[0], sub = blk[1], txt = blk[2];
        var href = d.f + '?q=' + encodeURIComponent(q) + '#' + anchor;
        out.push('<a class="sr-hit" href="' + href + '">' +
          '<div class="sr-head"><span class="sr-no">' + esc(d.no) + '</span>' +
          '<span class="sr-tt">' + esc(d.title) + '</span>' +
          (sub ? '<span class="sr-sub">› ' + esc(sub) + '</span>' : '') + '</div>');
        if (idx > 0) {
          var pv = dimText(d.b[idx - 1][2], 60, 'tail');
          if (pv) out.push('<div class="sr-line sr-dim">' + esc(pv) + '</div>');
        }
        var p0 = txt.toLowerCase().indexOf(q.toLowerCase());
        var inside = p0 >= 0 && inMath(txt, p0);
        var w = windowAround(inside ? txt : cleanSeg(txt), q, 46, 72);
        var pre = w.pre, post = w.post;
        out.push('<div class="sr-line sr-main">' + esc(pre) + '<mark class="sr-mk">' +
          esc(w.mid) + '</mark>' + esc(post) + '</div>');
        if (idx + 1 < d.b.length) {
          var nx = dimText(d.b[idx + 1][2], 60, 'head');
          if (nx) out.push('<div class="sr-line sr-dim">' + esc(nx) + '</div>');
        }
        out.push('</a>');
      });
      out.push('</div>');
    }

    if (!titleHits.length && !bodyHits.length) {
      out.push('<div class="sr-empty">没有找到「' + esc(q) + '」。<br>试试更短的关键词（如「泰勒」而不是「泰勒公式怎么用」），或换一个说法。</div>');
    }
    SR.wrap.innerHTML = out.join('');
    SR.wrap.hidden = false;
    if (SR.toc) SR.toc.hidden = true;
    if (SR.clear) SR.clear.hidden = false;
  }

  function clearSearch() {
    if (SR.wrap) { SR.wrap.hidden = true; SR.wrap.innerHTML = ''; }
    if (SR.toc) SR.toc.hidden = false;
    if (SR.clear) SR.clear.hidden = true;
    if (SR.input) { SR.input.value = ''; SR.input.focus(); }
    if (/[?&]q=/.test(location.search) && history.replaceState) {
      history.replaceState(null, '', location.pathname);
    }
  }

  function initSearch() {
    SR.input = document.getElementById('q');
    if (!SR.input) return;
    SR.form = document.getElementById('srForm');
    SR.wrap = document.getElementById('srWrap');
    SR.toc = document.getElementById('tocWrap');
    SR.clear = document.getElementById('qClear');

    function go() {
      var q = (SR.input.value || '').trim();
      if (!q) { clearSearch(); return; }
      ensureIndex(function () { runSearch(q); });
    }
    if (SR.form) SR.form.addEventListener('submit', function (e) { e.preventDefault(); go(); });
    SR.input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') { e.preventDefault(); go(); }
      else if (e.key === 'Escape') { clearSearch(); }
    });
    if (SR.clear) SR.clear.addEventListener('click', clearSearch);

    var m = /[?&]q=([^&]*)/.exec(location.search);
    if (m) {
      var q = decodeURIComponent(m[1].replace(/\+/g, ' '));
      SR.input.value = q;
      ensureIndex(function () { runSearch(q); });
    }
  }

  /* ---------- 目录页 ---------- */
  function initIndex() {
    if (!document.body.hasAttribute('data-index')) return;
    var q = document.querySelector('#q');
    var cards = Array.prototype.slice.call(document.querySelectorAll('[data-sec-card]'));
    var filter = 'all';
    function apply() {
      cards.forEach(function (c) {
        var id = c.getAttribute('data-sec-card');
        var okF = filter === 'all' || (filter === 'done' ? isDone(id) : !isDone(id));
        c.classList.toggle('is-hidden', !okF);
      });
      document.querySelectorAll('.ch-block').forEach(function (b) {
        var vis = b.querySelectorAll('[data-sec-card]:not(.is-hidden)').length;
        b.classList.toggle('is-hidden', vis === 0);
      });
    }
    document.querySelectorAll('[data-filter]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        filter = btn.getAttribute('data-filter');
        document.querySelectorAll('[data-filter]').forEach(function (b) { b.classList.toggle('on', b === btn); });
        apply();
      });
    });
    document.addEventListener('progresschange', apply);

    var cont = document.querySelector('[data-continue]');
    if (cont) cont.addEventListener('click', function (e) {
      e.preventDefault();
      var nx = FLAT.filter(function (s) { return !isDone(s.id); })[0] || FLAT[0];
      location.href = BASE + 'sections/' + nx.id.replace('.', '-') + '.html';
    });

    var exp = document.querySelector('[data-export]');
    if (exp) exp.addEventListener('click', function (e) {
      e.preventDefault();
      var blob = new Blob([JSON.stringify(progress, null, 2)], { type: 'application/json' });
      var a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = mod('progressFile', 'learning-progress.json');
      a.click();
    });
    var imp = document.querySelector('[data-import]');
    if (imp) imp.addEventListener('click', function (e) {
      e.preventDefault();
      var i = document.createElement('input');
      i.type = 'file'; i.accept = '.json';
      i.onchange = function () {
        var fr = new FileReader();
        fr.onload = function () {
          try {
            var obj = JSON.parse(fr.result);
            Object.keys(obj).forEach(function (k) { progress[k] = obj[k]; });
            writeStore(STORE, progress); sync();
          } catch (err) { alert('文件格式不对'); }
        };
        fr.readAsText(i.files[0]);
      };
      i.click();
    });
    var rst = document.querySelector('[data-reset]');
    if (rst) rst.addEventListener('click', function (e) {
      e.preventDefault();
      if (confirm('清空全部学习进度？此操作不可撤销。')) {
        progress = {}; writeStore(STORE, progress); sync();
      }
    });
  }

  /* ---------- 全局勾选 ---------- */
  function bindChecks() {
    document.addEventListener('change', function (e) {
      var t = e.target;
      if (!t.hasAttribute || !t.hasAttribute('data-check')) return;
      setDone(t.getAttribute('data-check'), t.checked);
    });
    document.addEventListener('click', function (e) {
      var exp = e.target.closest && e.target.closest('[data-export]');
      if (exp && !document.body.hasAttribute('data-index')) {
        e.preventDefault();
        var blob = new Blob([JSON.stringify(progress, null, 2)], { type: 'application/json' });
        var a = document.createElement('a');
        a.href = URL.createObjectURL(blob); a.download = mod('progressFile', 'learning-progress.json'); a.click();
      }
    });
  }

  /* ---------- 从检索跳到命中处 ---------- */
  var HIT_DONE = false;

  function clearHitMarks() {
    document.querySelectorAll('mark.sr-mk.hit').forEach(function (m) {
      var p = m.parentNode;
      if (!p) return;
      p.replaceChild(document.createTextNode(m.textContent), m);
      p.normalize();
    });
    document.querySelectorAll('.sr-flash').forEach(function (x) { x.classList.remove('sr-flash'); });
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
    if (!q) return 0;
    var probe = new RegExp(escRe(q), 'i');
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        if (!n.nodeValue || !n.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        var p = n.parentNode;
        while (p && p !== root.parentNode) {
          if (p.tagName === 'SCRIPT' || p.tagName === 'STYLE' || p.tagName === 'MARK' ||
              p.tagName === 'TEXTAREA' || p.tagName === 'svg') return NodeFilter.FILTER_REJECT;
          p = p.parentNode;
        }
        return probe.test(n.nodeValue) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
      }
    }, false);
    var nodes = [], n;
    while ((n = walker.nextNode())) nodes.push(n);
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
    return nodes.length;
  }

  function jumpToHit() {
    if (HIT_DONE) return;
    var m = /^#([\w-]+)$/.exec(location.hash || '');
    if (!m) return;
    var el = document.getElementById(m[1]);
    if (!el) return;
    HIT_DONE = true;

    var p = el.parentNode;
    while (p && p.nodeType === 1) {
      if (p.tagName === 'DETAILS' && !p.open) p.open = true;
      p = p.parentNode;
    }

    var qm = /[?&]q=([^&]*)/.exec(location.search);
    var q = qm ? decodeURIComponent(qm[1].replace(/\+/g, ' ')) : '';
    if (q) highlightIn(el, q);

    el.classList.add('sr-flash');
    setTimeout(function () { el.classList.remove('sr-flash'); }, 2800);

    function place() {
      var html = document.documentElement;
      var prev = html.style.scrollBehavior;
      html.style.scrollBehavior = 'auto';
      var top = el.getBoundingClientRect().top + window.pageYOffset;
      var h = window.innerHeight || 800;
      window.scrollTo(0, Math.max(0, top - h * 0.32));
      html.style.scrollBehavior = prev;
    }
    setTimeout(place, 60);
    setTimeout(function () {
      var r = el.getBoundingClientRect();
      if (r.top < 0 || r.bottom > (window.innerHeight || 800)) place();
    }, 500);
    armClearHighlight();
  }

  /* ---------- MathJax ---------- */
  function typeset() {
    window.MathJax = {
      tex: { inlineMath: [['$', '$']], displayMath: [['$$', '$$']], processEscapes: true, tags: 'none' },
      svg: { fontCache: 'global', scale: 0.98 },
      options: { skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code', 'svg'] },
      startup: { typeset: true }
    };
    var s = document.createElement('script');
    s.src = BASE + 'assets/mathjax/tex-svg.js';
    s.async = true;
    s.onload = function () {
      try {
        if (window.MathJax && MathJax.startup && MathJax.startup.promise) {
          MathJax.startup.promise.then(function () { setTimeout(jumpToHit, 40); });
        } else { setTimeout(jumpToHit, 120); }
      } catch (e) { setTimeout(jumpToHit, 120); }
    };
    document.head.appendChild(s);
    setTimeout(jumpToHit, 3000);
  }

  /* ---------- 打印时展开折叠 ---------- */
  function printBehavior() {
    window.addEventListener('beforeprint', function () {
      document.querySelectorAll('details.deep').forEach(function (d) {
        d.dataset.wasOpen = d.open ? '1' : '';
        d.open = true;
      });
    });
    window.addEventListener('afterprint', function () {
      document.querySelectorAll('details.deep').forEach(function (d) {
        if (!d.dataset.wasOpen) d.open = false;
      });
    });
  }

  /* ---------- 启动 ---------- */
  function boot() {
    if (!window.CURRICULUM) {
      if (document.querySelector('script[data-toc]')) return;
      var s = document.createElement('script');
      s.src = BASE + 'assets/toc.js';
      s.setAttribute('data-toc', '1');
      s.onload = boot;
      document.head.appendChild(s);
      return;
    }
    CURRICULUM = window.CURRICULUM;
    flatten();
    themePalette();

    if (document.body.hasAttribute('data-index')) {
      bindChecks();
      initIndex();
      initTheme();
      initSearch();
      sync();
      initFigures();
      return;
    }

    var parts = buildChrome();
    if (!parts) return;
    initTheme();
    sidebarBehavior(parts.aside);
    crumbsAndPager(parts.content);
    pageRail(parts.content);
    doneToggle();
    bindChecks();
    sync();
    initFigures();
    printBehavior();
    typeset();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
