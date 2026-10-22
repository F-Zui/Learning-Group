#include <bits/stdc++.h>
using namespace std;

const int MAXN = 10005, MAXM = 50005, LOG = 15, INF = 1e9;
struct Edge { int u, v, w; } e[MAXM];

int head[MAXN], nxt[MAXN << 1], to[MAXN << 1], wt[MAXN << 1], ecnt = 0;
void addEdge(int u, int v, int w) {
    to[++ecnt] = v; wt[ecnt] = w; nxt[ecnt] = head[u]; head[u] = ecnt;
}

int fa[MAXN];
int find(int x) { return fa[x] == x ? x : fa[x] = find(fa[x]); }

int up[LOG][MAXN], mn[LOG][MAXN], dep[MAXN];
bool vis[MAXN];

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    for (int i = 1; i <= m; ++i) cin >> e[i].u >> e[i].v >> e[i].w;

    // 1) Kruskal 建最大生成森林：限重最大的那棵树才可能给出答案
    for (int i = 1; i <= n; ++i) fa[i] = i;
    sort(e + 1, e + m + 1, [](const Edge& a, const Edge& b) { return a.w > b.w; });
    for (int i = 1; i <= m; ++i) {
        int ru = find(e[i].u), rv = find(e[i].v);
        if (ru == rv) continue;
        fa[ru] = rv;
        addEdge(e[i].u, e[i].v, e[i].w);
        addEdge(e[i].v, e[i].u, e[i].w);
    }

    // 2) 每棵树 BFS 一遍，填 up[0] 与 mn[0]
    queue<int> q;
    for (int r = 1; r <= n; ++r) {
        if (vis[r]) continue;
        vis[r] = true; dep[r] = 0; up[0][r] = r; mn[0][r] = INF;
        q.push(r);
        while (!q.empty()) {
            int u = q.front(); q.pop();
            for (int i = head[u]; i; i = nxt[i]) {
                int v = to[i];
                if (vis[v]) continue;
                vis[v] = true; dep[v] = dep[u] + 1;
                up[0][v] = u; mn[0][v] = wt[i];
                q.push(v);
            }
        }
    }

    // 3) 倍增表：2^k 级祖先 + 这一段路径上的最小边权
    for (int k = 1; k < LOG; ++k)
        for (int v = 1; v <= n; ++v) {
            up[k][v] = up[k - 1][up[k - 1][v]];
            mn[k][v] = min(mn[k - 1][v], mn[k - 1][up[k - 1][v]]);
        }

    int Q;
    cin >> Q;
    while (Q--) {
        int u, v;
        cin >> u >> v;
        if (find(u) != find(v)) { cout << -1 << '\n'; continue; }
        int ans = INF;
        if (dep[u] < dep[v]) swap(u, v);
        int diff = dep[u] - dep[v];
        for (int k = 0; k < LOG; ++k)
            if (diff >> k & 1) { ans = min(ans, mn[k][u]); u = up[k][u]; }
        if (u == v) { cout << ans << '\n'; continue; }
        for (int k = LOG - 1; k >= 0; --k)
            if (up[k][u] != up[k][v]) {
                ans = min(ans, min(mn[k][u], mn[k][v]));
                u = up[k][u]; v = up[k][v];
            }
        ans = min(ans, min(mn[0][u], mn[0][v]));   // 最后一步跳到 LCA
        cout << ans << '\n';
    }
    return 0;
}
