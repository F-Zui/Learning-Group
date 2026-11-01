/* 主题：在首屏之前应用，避免闪白 / 闪黑。 */
(function () {
  try {
    var t = localStorage.getItem('lg.theme');
    if (t === 'light' || t === 'dark') {
      document.documentElement.setAttribute('data-theme', t);
      document.documentElement.style.colorScheme = t;
    }
  } catch (e) { /* file:// 可能禁用存储，跟随系统 */ }
})();
