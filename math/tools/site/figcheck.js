// 校验 HTML 里所有 data-fn 表达式能否求值。
// 用法: node tools/site/figcheck.js sections/*.html
const fs = require('fs');

function powify(src) {
  let s = String(src), guard = 0;
  while (s.indexOf('^') >= 0 && guard++ < 80) {
    const i = s.lastIndexOf('^');
    let j = i - 1;
    while (j >= 0 && s[j] === ' ') j--;
    let baseStart;
    if (s[j] === ')') {
      let depth = 0, k = j;
      for (; k >= 0; k--) {
        if (s[k] === ')') depth++;
        else if (s[k] === '(') { depth--; if (!depth) break; }
      }
      baseStart = k;
      if (baseStart > 0 && /[A-Za-z_]/.test(s[baseStart - 1])) {
        const mf = /[A-Za-z_][A-Za-z0-9_]*$/.exec(s.slice(0, baseStart));
        if (mf) baseStart -= mf[0].length;
      }
    } else {
      const mb = /[A-Za-z0-9_.]+$/.exec(s.slice(0, j + 1));
      baseStart = mb ? j + 1 - mb[0].length : j;
    }
    let e = i + 1;
    while (e < s.length && s[e] === ' ') e++;
    let sign = '';
    if (s[e] === '-' || s[e] === '+') { sign = s[e] === '-' ? '-' : ''; e++; }
    let expEnd;
    if (s[e] === '(') {
      let d2 = 0;
      for (expEnd = e; expEnd < s.length; expEnd++) {
        if (s[expEnd] === '(') d2++;
        else if (s[expEnd] === ')') { d2--; if (!d2) { expEnd++; break; } }
      }
    } else {
      const me = /^[A-Za-z0-9_.]+/.exec(s.slice(e));
      expEnd = e + (me ? me[0].length : 1);
    }
    const exp = sign + s.slice(e, expEnd);
    s = s.slice(0, baseStart) + 'pow(' + s.slice(baseStart, i) + ',' + exp + ')' + s.slice(expEnd);
  }
  return s;
}

function compile(expr) {
  const body = powify(expr).replace(/\bln\b/g, 'log').replace(/\bpi\b/g, 'PI');
  return new Function('x', 'y',
    'var sin=Math.sin,cos=Math.cos,tan=Math.tan,asin=Math.asin,acos=Math.acos,atan=Math.atan,' +
    'exp=Math.exp,log=Math.log,sqrt=Math.sqrt,abs=Math.abs,PI=Math.PI,E=Math.E,' +
    'sign=Math.sign,pow=Math.pow,min=Math.min,max=Math.max,floor=Math.floor,ceil=Math.ceil,' +
    'sinh=Math.sinh,cosh=Math.cosh,tanh=Math.tanh;return (' + body + ');');
}

let bad = 0, total = 0;
for (const file of process.argv.slice(2)) {
  const txt = fs.readFileSync(file, 'utf8');
  const exprs = [...txt.matchAll(/data-fn="([^"]+)"/g)].map(m => m[1]);
  for (const group of exprs) {
    for (const e of group.split(';')) {
      const expr = e.trim();
      if (!expr) continue;
      total++;
      let ok = 0, err = '';
      try {
        const f = compile(expr);
        for (let i = 0; i <= 40; i++) {
          const x = -2 + i * 0.1;
          const y = -2 + i * 0.1;
          try { if (Number.isFinite(f(x, y))) ok++; } catch (e2) { err = e2.message; }
        }
      } catch (e) { err = e.message; }
      if (ok === 0) {
        bad++;
        console.log(`FAIL ${file}  data-fn="${expr}" ${err ? '(' + err + ')' : '(全部为 NaN)'}`);
      }
    }
  }
}
console.log(`\n${total - bad}/${total} 表达式可求值`);
process.exit(bad ? 1 : 0);
