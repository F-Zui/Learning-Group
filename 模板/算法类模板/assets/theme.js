/* 主题：在首屏之前应用，避免闪白 / 闪黑；点 [data-theme-toggle] 切换。 */
(function () {
  var K = 'lg.theme';
  function apply(t) {
    document.documentElement.setAttribute('data-theme', t);
    document.documentElement.style.colorScheme = t;
  }
  try {
    var s = localStorage.getItem(K);
    if (s === 'light' || s === 'dark') apply(s);
  } catch (e) { /* file:// 可能禁用存储，跟随系统 */ }
  document.addEventListener('click', function (ev) {
    var b = ev.target.closest ? ev.target.closest('[data-theme-toggle]') : null;
    if (!b) return;
    var cur = document.documentElement.getAttribute('data-theme');
    if (!cur) {
      cur = (window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches)
        ? 'dark' : 'light';
    }
    var next = cur === 'dark' ? 'light' : 'dark';
    apply(next);
    try { localStorage.setItem(K, next); } catch (e) { }
  });
})();
