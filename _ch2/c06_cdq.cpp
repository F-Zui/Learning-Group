#include <bits/stdc++.h>
using namespace std;

const int MAXN = 100005;
int n, m;
int a[MAXN], posv[MAXN];     // posv[值] = 下标
int tim[MAXN];               // tim[下标] = 该元素在第几步被删；未被删的记为 m+1
int delVal[MAXN];

struct Item { int t, p, v, id; } it[MAXN], tmp[MAXN];
int out[MAXN];               // out[下标] = 与它构成逆序对、且删它时还活着的元素个数
int bit[MAXN];

inline int lowbit(int x) { return x & -x; }
void add(int i, int d) { for (; i <= n; i += lowbit(i)) bit[i] += d; }
int sum(int i) { int s = 0; for (; i > 0; i -= lowbit(i)) s += bit[i]; return s; }

// 统计每个元素：在它之前(t 更大或相等)的元素里，p 比它小且 v 比它大的个数
void cdq(int l, int r) {
    if (l == r) return;
    int mid = (l + r) >> 1;
    cdq(l, mid);
    cdq(mid + 1, r);         // 递归后两半各自按 p 升序，t 的大小关系由初始排序保证
    int i = l;
    for (int j = mid + 1; j <= r; ++j) {
        while (i <= mid && it[i].p < it[j].p) { add(it[i].v, 1); ++i; }
        out[it[j].id] += (i - l) - sum(it[j].v);   // 已进的左半元素中 v > 它的个数
    }
    for (int k = l; k < i; ++k) add(it[k].v, -1);  // 撤销
    int x = l, y = mid + 1, z = l;
    while (x <= mid && y <= r) tmp[z++] = (it[x].p < it[y].p) ? it[x++] : it[y++];
    while (x <= mid) tmp[z++] = it[x++];
    while (y <= r) tmp[z++] = it[y++];
    for (int k = l; k <= r; ++k) it[k] = tmp[k];
}

void solveOnce(bool reflect) {
    for (int p = 1; p <= n; ++p) {
        it[p].t = tim[p];
        it[p].p = reflect ? n + 1 - p : p;
        it[p].v = reflect ? n + 1 - a[p] : a[p];
        it[p].id = p;
    }
    sort(it + 1, it + n + 1, [](const Item& x, const Item& y) { return x.t > y.t; });
    memset(bit, 0, sizeof(int) * (n + 1));
    cdq(1, n);
}

int main() {
    scanf("%d%d", &n, &m);
    for (int i = 1; i <= n; ++i) { scanf("%d", &a[i]); posv[a[i]] = i; tim[i] = m + 1; }
    for (int q = 1; q <= m; ++q) { scanf("%d", &delVal[q]); tim[posv[delVal[q]]] = q; }

    long long cur = 0;
    for (int i = 1; i <= n; ++i) { cur += (i - 1) - sum(a[i]); add(a[i], 1); }
    memset(bit, 0, sizeof(int) * (n + 1));

    solveOnce(false);        // 左边比它大
    solveOnce(true);         // 镜像后同一个问题：右边比它小

    for (int q = 1; q <= m; ++q) {
        int p = posv[delVal[q]];
        printf("%lld\n", cur);
        cur -= out[p];
    }
    return 0;
}
