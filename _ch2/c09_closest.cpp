#include <bits/stdc++.h>
using namespace std;

const int MAXN = 200005;
struct P { long long x, y; } p[MAXN], t[MAXN];

inline double dist(const P& a, const P& b) {
    double dx = (double)a.x - b.x, dy = (double)a.y - b.y;
    return sqrt(dx * dx + dy * dy);
}
bool cmpx(const P& a, const P& b) { return a.x < b.x || (a.x == b.x && a.y < b.y); }

double solve(int l, int r) {
    if (l == r) return 1e30;
    if (r - l == 1) return dist(p[l], p[r]);
    int mid = (l + r) >> 1;
    long long mx = p[mid].x;
    double d = min(solve(l, mid), solve(mid + 1, r));

    // 归并：让 [l, r] 按 y 升序，供上层和带状扫描用
    int i = l, j = mid + 1, k = l;
    while (i <= mid && j <= r) t[k++] = (p[i].y <= p[j].y) ? p[i++] : p[j++];
    while (i <= mid) t[k++] = p[i++];
    while (j <= r) t[k++] = p[j++];
    for (k = l; k <= r; ++k) p[k] = t[k];

    // 只留离中线 x 距离 < d 的点，按 y 已有序
    int c = 0;
    for (k = l; k <= r; ++k)
        if (fabs((double)p[k].x - (double)mx) < d) t[c++] = p[k];
    for (i = 0; i < c; ++i)
        for (j = i + 1; j < c && (t[j].y - t[i].y) < d; ++j) {
            double nd = dist(t[i], t[j]);
            if (nd < d) d = nd;
        }
    return d;
}

int main() {
    int n;
    scanf("%d", &n);
    for (int i = 1; i <= n; ++i) scanf("%lld%lld", &p[i].x, &p[i].y);
    sort(p + 1, p + n + 1, cmpx);
    printf("%.4f\n", solve(1, n));
    return 0;
}
