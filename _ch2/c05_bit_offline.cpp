#include <bits/stdc++.h>
using namespace std;

const int MAXN = 1000005;
int a[MAXN], last[MAXN], bit[MAXN], ans[MAXN];
struct Q { int l, r, id; } qs[MAXN];
int n, m;

inline int lowbit(int x) { return x & -x; }
void add(int i, int d) { for (; i <= n; i += lowbit(i)) bit[i] += d; }
int sum(int i) { int s = 0; for (; i > 0; i -= lowbit(i)) s += bit[i]; return s; }

inline int readInt() {
    int x = 0;
    char c = getchar();
    while (c < '0' || c > '9') c = getchar();
    while (c >= '0' && c <= '9') { x = x * 10 + (c - '0'); c = getchar(); }
    return x;
}

int main() {
    n = readInt();
    for (int i = 1; i <= n; ++i) a[i] = readInt();
    m = readInt();
    for (int i = 0; i < m; ++i) {
        qs[i].l = readInt(); qs[i].r = readInt(); qs[i].id = i;
    }
    sort(qs, qs + m, [](const Q& x, const Q& y) { return x.r < y.r; });

    int p = 0;
    for (int i = 0; i < m; ++i) {
        while (p < qs[i].r) {
            ++p;
            if (last[a[p]]) add(last[a[p]], -1);   // 同一种贝壳只在最右一次出现处记 1
            add(p, 1);
            last[a[p]] = p;
        }
        // 此时 [1, r] 里每个种类恰好被记在"最右一次出现"上
        ans[qs[i].id] = sum(qs[i].r) - sum(qs[i].l - 1);
    }
    for (int i = 0; i < m; ++i) printf("%d\n", ans[i]);
    return 0;
}
