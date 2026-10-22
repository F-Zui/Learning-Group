#include <bits/stdc++.h>
using namespace std;

const int MAXN = 50005;
int col[MAXN], cnt[MAXN], blk;
long long cur = 0;            // 当前区间里 Σ C(cnt[颜色], 2)
long long num[MAXN], den[MAXN];
int n, m;

struct Q { int l, r, id; } q[MAXN];

inline void addPos(int i) { cur += cnt[col[i]]; ++cnt[col[i]]; }   // 增量 = 旧次数
inline void delPos(int i) { --cnt[col[i]]; cur -= cnt[col[i]]; }   // 减量 = 新次数

int main() {
    scanf("%d%d", &n, &m);
    for (int i = 1; i <= n; ++i) scanf("%d", &col[i]);
    for (int i = 0; i < m; ++i) { scanf("%d%d", &q[i].l, &q[i].r); q[i].id = i; }

    blk = max(1, (int)(n / sqrt((double)max(1, m))));       // 块大小 = n / √m
    sort(q, q + m, [](const Q& x, const Q& y) {
        int bx = x.l / blk, by = y.l / blk;
        if (bx != by) return bx < by;
        return (bx & 1) ? x.r > y.r : x.r < y.r;            // 奇数块 r 倒序，少走一整趟
    });

    int L = 1, R = 0;
    for (int i = 0; i < m; ++i) {
        while (L > q[i].l) addPos(--L);
        while (R < q[i].r) addPos(++R);
        while (L < q[i].l) delPos(L++);
        while (R > q[i].r) delPos(R--);
        long long len = q[i].r - q[i].l + 1;
        num[q[i].id] = cur;
        den[q[i].id] = len * (len - 1) / 2;                 // 总方案数 C(len, 2)
    }
    for (int i = 0; i < m; ++i) {
        if (num[i] == 0) { puts("0/1"); continue; }
        long long g = __gcd(num[i], den[i]);
        printf("%lld/%lld\n", num[i] / g, den[i] / g);
    }
    return 0;
}
